#!/usr/bin/env python3
"""Baseline (c) for Phase 3: zero-shot LLMs over OpenRouter, scored by the scorer.

One runner for every row of the table. `--model` picks the row; the frontier
reference row is this same script with the Haiku slug and `--reference-only`,
which marks the record so that no gate can read it. There is no second script.

Each run scores three frozen inputs — the 400-row comment test set, the 250-row
post test set and the 108-row sarcasm holdout — one request per row, at the
precision the pre-registered rule fixed and the endpoint the ADR pinned
(`knowledge/decisions/3b-infra-and-precision.md`). A row that comes back
unreadable is counted as a parse failure; a row that does not come back at all is
counted as an API failure. Both are reported with their n and excluded from
scoring. Neither is ever coerced to a label.

Every number leaves through `market_pulse.scorer` into `results/baselines.json`,
append-only.

    pip install -e '.[dev]'          # nothing else: the client is urllib
    python3.11 scripts/eval_zero_shot.py --model qwen/qwen3.5-9b --smoke
    python3.11 scripts/eval_zero_shot.py --model qwen/qwen3.5-9b --dry-run
    python3.11 scripts/eval_zero_shot.py --model qwen/qwen3.5-9b --probe 3
    python3.11 scripts/eval_zero_shot.py --model qwen/qwen3.5-9b
"""

import argparse
import itertools
import json
import os
import re
import subprocess
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse import local_llm, parents, prompts, records, scorer, zero_shot  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402
from market_pulse.scorer import UNCLEAR  # noqa: E402

FROZEN = REPO_ROOT / "data" / "frozen"
RESULTS = REPO_ROOT / "results" / "baselines.json"
LEDGER = REPO_ROOT / "results" / "spend_3b.json"
PREDICTIONS = REPO_ROOT / "results" / "predictions"
G1B_SLICE = REPO_ROOT / "results" / "g1b_slice.json"
SLICE_OF = {"v2": G1B_SLICE, "v4": REPO_ROOT / "results" / "g1b_slice_v4.json"}
"""One G1b slice per frozen-test-set version, and never one file for two.

The slice is the gate's denominator (amendment 3.5 (3)) and is written by the version's own
anchor from that version's own holdout. Sharing a path would let a v4 anchor overwrite the 44
pre-registered ids Phase 4's verdict was decided against."""

SEED = 42
TEMPERATURE = 0.0
MAX_TOKENS = 256
PHASE_CAP_USD = 8.00
DEFAULT_RUN_CAP_USD = 1.50
UNUSABLE_LIMIT = 0.02
# Fallbacks are off, so a pinned endpoint's rate limit is ours to wait out. Six
# attempts is ~46 s of backoff per row; four workers is what stopped `venice/fp8`
# from returning 429 at all (the first qwen3.5-9b run lost 11 rows to it).
RETRY_ATTEMPTS = 6
DEFAULT_CONCURRENCY = 4

# Pinned by `knowledge/decisions/3b-infra-and-precision.md` §(b): fp8 for all three
# candidates (qwen3.6-27b offers no bf16 anywhere), cheapest healthy fp8 endpoint
# each. The Anthropic rows report no quantization to pin and anchor no gate.
ROWS = {
    "google/gemma-4-31b-it": {"tag": "parasail/fp8", "quantization": "fp8"},
    "qwen/qwen3.6-27b": {"tag": "io-net/fp8", "quantization": "fp8"},
    "qwen/qwen3.5-9b": {"tag": "venice/fp8", "quantization": "fp8"},
    # OpenRouter serves the :batch variant only through /api/beta/batches — a
    # 404 on /chat/completions, verified 2026-07-31. Kept here so the slug the
    # 3b prompt names gets an explanation rather than an argparse error.
    "anthropic/claude-haiku-4.5:batch": {
        "tag": "anthropic",
        "quantization": None,
        "ref": True,
        "batch_only": True,
    },
    "anthropic/claude-haiku-4.5": {"tag": "anthropic", "quantization": None, "ref": True},
}

INPUTS = (("comments_test", "T1"), ("posts_test", "T2"), ("sarcasm_holdout", "T1"))
"""The three frozen inputs and the task each one is, before a version resolves either."""

RAW_POSTS = REPO_ROOT / "data" / "raw" / "posts"
CAPTIONS = REPO_ROOT / "data" / "annotation" / "post_captions.jsonl"


def inputs_for(version: str) -> tuple[tuple[str, str, str], ...]:
    """``(name, the task to render, the file to score)`` for one test-set version.

    v2 is the unsuffixed files and the frozen v1 prompts — what every Phase 4 record was
    measured on. A later version resolves both at once, because those are not two choices: a
    v4 file's gold carries six intents and `parse_reply("T1", …)` refuses the sixth."""
    suffix = "" if version == records.DEFAULT_TESTSET_VERSION else f"_{version}"
    return tuple(
        (name, prompts.REVISIONS[version][base], f"{name}{suffix}.jsonl") for name, base in INPUTS
    )


def post_context(task: str, rows: list[dict]) -> list[dict] | None:
    """One :func:`parents.post_kwargs` per row, or ``None`` for a task that takes no post.

    The parent index is loaded once per input rather than per row, and a missing parent
    raises out of `parents.text_for` — a row asked without the post its neighbours got would
    be labelled by a different instrument and nothing downstream could see it.
    """
    if task not in prompts.WITH_POST:
        return None
    posts = parents.load(RAW_POSTS)
    captions = parents.load_captions(CAPTIONS)
    return [parents.post_kwargs(parents.context(posts, captions, row)) for row in rows]


def load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path}: not found")
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def gold(rows: list[dict], field: str, unclear=UNCLEAR):
    return [unclear if row["unclear"] else row[field] for row in rows]


def git_state() -> dict:
    """HEAD plus every path that differs from it — provenance, not a boolean.

    Same rule as scripts/run_baseline.py: a results file cannot name the commit
    that contains it, so the honest record is the commit the numbers were made
    against and the files that were not in it.
    """

    def run(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        ).stdout

    dirty = [line.split(maxsplit=1)[1] for line in run("status", "--porcelain").splitlines()]
    ignore = {str(p.relative_to(REPO_ROOT)) for p in (RESULTS, LEDGER)}
    return {
        "commit": run("rev-parse", "HEAD").strip(),
        "dirty": sorted(path for path in dirty if path not in ignore),
    }


def append(record: dict) -> None:
    """Append-only: a model's runs accumulate, none is ever overwritten."""
    RESULTS.parent.mkdir(exist_ok=True)
    history = json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.exists() else {}
    history.setdefault(record["model"], []).append(record)
    RESULTS.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def api_key() -> str:
    """OPENROUTER_API_KEY from the environment, else from .env. No other vendor."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        env = REPO_ROOT / ".env"
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                name, _, value = line.partition("=")
                if name.strip() == "OPENROUTER_API_KEY":
                    key = value.strip()
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is not set (environment or .env)")
    return key


class Client:
    """One pinned endpoint, one budget, retries — and nothing else.

    Thread-safe because the budget is: the guard has to see every row's cost as
    it lands, not a per-worker sum reconciled at the end, or the cap is only a
    cap on average.
    """

    def __init__(self, key, model, tag, quantization, budget, lock):
        self.key, self.model, self.tag, self.quantization = key, model, tag, quantization
        self.budget, self.lock = budget, lock
        self.usage = Counter()

    def __call__(self, task: str, text: str) -> dict:
        body = zero_shot.request_body(
            model=self.model,
            messages=prompts.build_messages(task, text),
            tag=self.tag,
            quantization=self.quantization,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            seed=SEED,
        )
        payload, headers = zero_shot.call_with_retry(
            lambda: zero_shot.post("/chat/completions", body, self.key), attempts=RETRY_ATTEMPTS
        )
        usage = payload.get("usage") or {}
        cost = float(usage.get("cost") or 0.0)
        with self.lock:
            self.budget.add(cost)
            self.usage["prompt_tokens"] += int(usage.get("prompt_tokens") or 0)
            self.usage["completion_tokens"] += int(usage.get("completion_tokens") or 0)
            self.usage["reasoning_tokens"] += int(
                (usage.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0
            )
        choices = payload.get("choices") or []
        if not choices:
            raise zero_shot.ApiError(-1, "no choices in reply")
        return {
            "content": choices[0].get("message", {}).get("content") or "",
            "finish_reason": choices[0].get("finish_reason"),
            "cost": cost,
            "usage": usage,
            "generation_id": headers.get("X-Generation-Id") or payload.get("id"),
        }


class FakeClient:
    """`--smoke`: the whole pipeline, no network, no money, every counter exercised.

    The canned replies deliberately include a fenced answer (legal), a garbage
    answer (parse failure) and a dead endpoint (API failure), so a smoke run that
    prints zeros in the failure table is itself the bug.
    """

    REPLIES = {
        "T1": [
            '{"sentiment": "negative", "sarcasm": true, "intents": ["price"]}',
            '```json\n{"sentiment": "neutral", "sarcasm": false, "intents": []}\n```',
            "I cannot label this.",
            '{"sentiment": "positive", "sarcasm": false, "intents": ["taste"]}',
        ],
        "T2": [
            '{"relevant": true, "post_type": "promo", "brands": [{"mention": "Rud"}]}',
            '```json\n{"relevant": false, "post_type": "other", "brands": []}\n```',
            '{"relevant": false, "post_type": "sale", "brands": []}',
            '{"relevant": true, "post_type": "launch", "brands": ["Halychyna"]}',
        ],
    }

    def __init__(self):
        self.cycles = {task: itertools.cycle(range(5)) for task in self.REPLIES}
        self.usage = Counter()
        self.lock = threading.Lock()

    def __call__(self, task: str, text: str, post: dict | None = None) -> dict:
        # the same refusals a real request goes through, so --smoke exercises the with-post
        # contract instead of only the code that follows a successful render
        prompts.build_messages(task, text, **(post or {}))
        family = "T2" if prompts.DELIMITERS[task] == "post" else "T1"
        with self.lock:
            step = next(self.cycles[family])
        if step == 4:
            raise zero_shot.ApiError(503, "fake endpoint down")
        return {
            "content": self.REPLIES[family][step],
            "finish_reason": "stop",
            "cost": 0.0,
            "usage": {},
            "generation_id": f"fake-{family}-{step}",
        }

    def batch(self, task: str, texts: list[str], posts: list[dict] | None = None) -> list[dict]:
        """`--backend local --smoke`: the batched path, same canned replies.

        A row that fails comes back *as* its exception rather than raising, the
        way a single bad generation does — a whole batch only fails when the
        generate call itself does.
        """
        replies = []
        for text, post in zip(texts, posts or [None] * len(texts)):
            try:
                replies.append(self(task, text, post))
            except zero_shot.ApiError as err:
                replies.append(err)
        return replies


def outcome(task: str, row_id: str, reply, unusable: str) -> dict:
    """One reply — or the exception instead of one — as the row's outcome.

    Shared by both backends so that the failure taxonomy cannot drift between
    them: only the name of the non-parse bucket differs (``api`` for a
    third-party endpoint, ``generation`` for our own weights), because 3b §(e)
    counts "no usable response" separately from "a response we cannot read".
    """
    if isinstance(reply, BaseException):
        return {"id": row_id, "failure": unusable, "reason": f"{type(reply).__name__}: {reply}"}
    entry = {"id": row_id, "finish_reason": reply["finish_reason"]}
    try:
        return entry | {"labels": prompts.parse_reply(task, reply["content"])}
    except prompts.ParseError as err:
        return entry | {"failure": "parse", "reason": err.reason}


def classify(client, task: str, rows: list[dict], concurrency: int) -> list[dict]:
    """One request per row, bounded concurrency, ordered results.

    A failure is recorded against the row, never dropped: the caller has to be
    able to name which ids it did not score.
    """

    def one(row: dict) -> dict:
        try:
            reply = client(task, row["text"])
        except zero_shot.BudgetExceeded:
            raise  # the cap stops the run; it is not one more failed row
        except Exception as err:  # noqa: BLE001 — every other failure mode is a counted row
            reply = err
        return outcome(task, row["id"], reply, "api")

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        return list(pool.map(one, rows))


def classify_local(
    client, task: str, rows: list[dict], batch_size: int, on_row=None, posts=None
) -> list[dict]:
    """The same contract, one padded batch at a time instead of one request per row.

    Batches are a throughput choice and nothing else — decoding is greedy, so
    the runbook's batch-invariance check on the pod is what makes that claim a
    measurement rather than an assumption.

    A batch that raises is retried one row at a time before anything is charged.
    The OpenRouter client retries every row six times; without the fallback a
    single transient would cost eight rows here against nought or one there, and
    the 2% limit is two rows on the 108-row holdout — one bad batch would end the
    run. Only a row that fails alone is a generation failure.

    An out-of-memory is never charged to a row: it is a fact about the machine,
    and turning it into 758 counted failures would bury the one line that says
    what actually happened.

    ``on_row`` is called with each outcome the moment it exists. That is what
    makes an eval resumable: PROMPT-4c's crash protocol says a crashed eval
    resumes on the rows it has left and never re-scores a completed one, and a
    result that lives only in this list until the last input finishes cannot
    honour it.
    """
    outcomes = []
    for start in range(0, len(rows), batch_size):
        chunk = rows[start : start + batch_size]
        window = posts[start : start + batch_size] if posts is not None else None
        texts = [row["text"] for row in chunk]
        try:
            replies = client.batch(task, texts, window) if window else client.batch(task, texts)
        except MemoryError:
            raise
        except Exception as err:  # noqa: BLE001 — retried per row, then counted
            # Older torch raises a plain RuntimeError for OOM, newer one a named
            # class; both mean the batch size was wrong, not that a row was.
            if type(err).__name__ == "OutOfMemoryError" or "out of memory" in str(err).lower():
                raise
            print(f"    batch at row {start} failed ({err}) — retrying its rows one by one")
            replies = [
                _one_row(client, task, row["text"], window[index] if window else None)
                for index, row in enumerate(chunk)
            ]
        for row, reply in zip(chunk, replies):
            scored = outcome(task, row["id"], reply, "generation")
            if on_row is not None:
                on_row(scored)  # persisted before the next batch: a crash resumes here
            outcomes.append(scored)
    return outcomes


def _one_row(client, task: str, text: str, post: dict | None = None):
    """One row on its own; the exception itself when even that fails."""
    try:
        # positional-optional: a client that predates the parent post takes two arguments
        return client.batch(task, [text], [post])[0] if post else client.batch(task, [text])[0]
    except Exception as err:  # noqa: BLE001 — now it really is this row's failure
        if type(err).__name__ == "OutOfMemoryError" or "out of memory" in str(err).lower():
            raise
        return err


def split(rows: list[dict], outcomes: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """(scored rows, their labels, the failures) — paired by position."""
    scored, labels, failures = [], [], []
    for row, outcome in zip(rows, outcomes):
        if "labels" in outcome:
            scored.append(row)
            labels.append(outcome["labels"])
        else:
            failures.append(outcome)
    return scored, labels, failures


def failure_block(name: str, outcomes: list[dict], failures: list[dict]) -> dict:
    kinds = Counter(f["failure"] for f in failures)
    return {
        "input": name,
        "rows": len(outcomes),
        "scored": len(outcomes) - len(failures),
        "parse_failures": kinds["parse"],
        # Both buckets are always present, whichever backend ran: a schema that
        # changed with the runtime would make the two rows harder to compare
        # than the numbers they carry. The local path leaves `api_failures` 0,
        # the OpenRouter path leaves `generation_failures` 0.
        "api_failures": kinds["api"],
        "generation_failures": kinds["generation"],
        # A truncated reply is a parse failure with a cause worth separating: it
        # says max_tokens was too small, not that the model cannot follow a format.
        "truncated": sum(1 for o in outcomes if o.get("finish_reason") == "length"),
        "reasons": dict(Counter(f["reason"][:60] for f in failures).most_common(8)),
        "failed_ids": sorted(f["id"] for f in failures)[:20],
    }


def scored_ids_sha256(rows: list[dict]) -> str:
    """The exact paired subset a gate was anchored on, in one field."""
    return sha256("\n".join(row["id"] for row in rows).encode("utf-8")).hexdigest()


def prediction_lines(scored_inputs: dict) -> list[str]:
    """One JSON line per scored row: the input, the id, and what the model answered.

    Ids and predicted labels only — no gold label and no source text, so the dump
    is a record of the model and never a second copy of a frozen file.

    Sorted by ``(input, id)``: rows come back from a thread pool, and a hash that
    depends on which worker finished first is not a hash of the data.
    """
    rows = sorted(
        (
            (name, row["id"], pred)
            for name, (scored, labels) in scored_inputs.items()
            for row, pred in zip(scored, labels)
        ),
        key=lambda entry: entry[:2],
    )
    return [
        json.dumps({"input": name, "id": row_id, "pred": pred}, ensure_ascii=False, sort_keys=True)
        for name, row_id, pred in rows
    ]


def write_predictions(path: Path, scored_inputs: dict) -> str:
    """Persist the dump, return its SHA256. The gap 3b left: a hash of ids cannot
    re-score them, so a later paired comparison needs the answers themselves."""
    text = "".join(line + "\n" for line in prediction_lines(scored_inputs))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return sha256(text.encode("utf-8")).hexdigest()


def open_checkpoint(path: Path, header: dict) -> dict:
    """Rows this eval already scored, or an empty ledger with its header written.

    One JSON line per row, opened and closed per write — the same discipline
    `loss.jsonl` follows, and for the same reason: a buffered file is empty
    exactly when the process died. The header is the refusal that makes resuming
    safe. A checkpoint carries the model, the arm and the adapter it was scored
    with, so an arm-A file left in place cannot quietly donate 400 of arm B's
    rows; the prompt hashes are in it because a prompt that moved is a different
    measurement (SPEC §7) and half a record from each would be neither.
    """
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"header": header}, sort_keys=True) + "\n", encoding="utf-8")
        return {}
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    stored = json.loads(lines[0]).get("header") if lines else None
    if stored != header:
        differ = sorted(
            key for key in set(header) | set(stored or {}) if (stored or {}).get(key) != header[key]
        )
        raise SystemExit(
            f"{path.name} was written by a different run — it differs on {differ}."
            " Scoring on top of it would mix two models' rows into one gate record."
            " Delete it to start this eval from zero, or point --eval-checkpoint at its own file."
        )
    done = {}
    for line in lines[1:]:
        entry = json.loads(line)
        done[(entry["input"], entry["outcome"]["id"])] = entry["outcome"]
    return done


def append_checkpoint(path: Path, name: str, scored: dict) -> None:
    """One scored row, on disk before the next one is asked for."""
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"input": name, "outcome": scored}, ensure_ascii=False) + "\n")


def predictions_path(model: str, timestamp: str) -> Path:
    """``results/predictions/<sanitized-slug>--<UTC-ts>.jsonl``."""
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", model)
    stamp = re.sub(r"[^0-9TZ]", "", timestamp.replace("+00:00", "Z"))
    return PREDICTIONS / f"{slug}--{stamp}.jsonl"


def history() -> dict:
    return json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.exists() else {}


def recorded_prompt_sha256(model: str) -> list[dict]:
    """Every ``prompt_sha256`` map the results file already holds for a model."""
    return records.prompt_sha_history(history(), model)


def assert_prompt_sha_matches_3b(model: str) -> dict:
    """Refuse to run unless this checkout's fixed prompts hash to 3b's hashes.

    A cross-check whose prompt moved is not a cross-check of a serving stack; it
    is two different measurements with one name (SPEC amendment 3.4 (2)). The
    comparison itself is `records.assert_prompt_sha`, which the trainer runs
    against the same records at dataset build — one prompt identity, one
    implementation.
    """
    try:
        return records.assert_prompt_sha(recorded_prompt_sha256(model), model)
    except ValueError as err:
        raise SystemExit(str(err)) from None


def local_config(
    shared: dict,
    batch_size: int,
    runtime: dict,
    training: dict | None,
    anchor_valid: bool,
    slice_ids: dict | None,
    scored_inputs: dict,
    version: str = records.DEFAULT_TESTSET_VERSION,
) -> dict:
    """What a run on our own weights records about itself.

    Two rows come out of here and they must not be confusable. The zero-shot one
    anchors every Phase 4 bar and *writes* the G1b slice; the fine-tuned one is
    an ablation arm and only *reads* it. So:

    - ``train_sources`` stops saying "no training data" the moment an adapter is
      loaded. ``records.anchor`` narrows on exactly that field precisely because
      Phase 4's arms are also ``backend: local`` — a row that lied here would
      hand a model itself as its own baseline, and every derived bar would be
      quietly wrong.
    - the slice file is never rewritten by an arm. It is pre-registered
      (amendment 3.5 (3)); replacing it with a fine-tuned model's error set would
      move the gate's denominator without moving one number in this record.
      ``slice_ids`` is ``None`` on that branch, so ``write_slice`` has nothing to
      be called with even by accident.
    """
    config = shared | {
        "backend": "local",
        "max_tokens": local_llm.MAX_NEW_TOKENS,
        "quantization": local_llm.QUANTIZATION,
        "generation": {
            "greedy": True,
            "do_sample": False,
            "batch_size": batch_size,
            "chat_template": local_llm.CHAT_TEMPLATE,
        },
        "runtime": runtime,
        "spend_ledger": "results/spend_phase4.json",
        "determinism_note": (
            "our own pod: weights, kernels and tokenizer are all in this record's `runtime`,"
            " decoding is greedy and the prompts are byte-identical to the OpenRouter run of"
            " the same model (asserted before the weights load)."
        )
        + (
            " This is a Phase 4 ablation arm — the 4-bit base plus its UNMERGED adapter, the"
            " exact configuration the artefact serves in (amendment 3.4 (1)). It is scored"
            " once; nothing is retrained or re-scored after a gate number is seen."
            if training
            else " This row is the G1d/G1e anchor (SPEC amendment 3.4 (2)); where it disagrees"
            " with the OpenRouter fp8 row, this one anchors and the disagreement is recorded,"
            " never averaged (ADR 3b-infra-and-precision §(d))."
        ),
    }
    gate_slice = SLICE_OF[version]
    if training:
        return config | {
            "train_sources": training["rows_per_source"],
            "fine_tune": training,
            "g1b_slice_path": str(gate_slice.relative_to(REPO_ROOT)),
            "g1b_slice_sha256": sha256(
                gate_slice.read_text(encoding="utf-8").encode("utf-8")
            ).hexdigest(),
        }
    if anchor_valid:
        return config | {
            "g1b_slice_path": str(gate_slice.relative_to(REPO_ROOT)),
            "g1b_slice_sha256": write_slice(
                gate_slice, scored_inputs["sarcasm_holdout"][0], slice_ids
            ),
        }
    return config


def arm_preflight(
    adapter: Path, arm: str, version: str = records.DEFAULT_TESTSET_VERSION
) -> tuple[dict, dict]:
    """Everything an ablation arm's gate eval must be sure of, before the weights.

    Ordered by what it costs to learn late: the anchor and its slice decide the
    gate and are free to read; the adapter hash is a directory walk. All of it
    happens before 62 GB of base model and an hour of A6000 time — and before
    the one attempt this phase gets is spent scoring the wrong artefact.

    Returns the G1b inputs and the training provenance the record carries, so
    that a gate number can name the dataset and the adapter it came from.
    """
    try:
        record = records.anchor(history(), version)
        ids = records.slice_ids(SLICE_OF[version].read_text(encoding="utf-8"), record)
        overall = records.anchor_values(record)["G1a"]["overall"]
    except (ValueError, OSError) as err:
        raise SystemExit(f"the anchor this arm is measured against is unusable: {err}") from None

    source = adapter.parent / "provenance.json"
    if not adapter.is_dir() or not source.exists():
        raise SystemExit(
            f"{adapter} must be a trainer output directory holding the adapter, beside the"
            f" run's provenance.json ({source} is missing). A gate record whose adapter"
            " cannot name the dataset it was trained on is not provenance."
        )
    training = json.loads(source.read_text(encoding="utf-8"))
    if training["arm"] != arm:
        raise SystemExit(
            f"{source} says this adapter is the {training['arm']!r} arm, not {arm!r}."
            " Scoring one arm under the other's name would decide the ablation by mislabelling."
        )
    current = {task: prompts.prompt_sha256(task) for task in prompts.TASKS}
    if training["prompt_sha256"] != current:
        raise SystemExit(
            f"the adapter was trained on different prompts: {training['prompt_sha256']} against"
            f" {current}. The prompt is part of the measurement (SPEC §7) — stop and report."
        )
    # The check above cannot see a rendering change: it covers the frozen v1 prompts, which
    # stay frozen through one. This is the one that can, and it is what makes "the arm was
    # trained in the space the gate scores in" a check instead of a claim.
    rendering = prompts.revision_sha256(version)
    if training.get("prompt_revision_sha256", prompts.revision_sha256("v2")) != rendering:
        raise SystemExit(
            f"the adapter renders {training.get('prompt_revision_sha256')} and this eval renders"
            f" {rendering}. An arm scored through a prompt it was not trained on measures the"
            " rendering, not the data — stop and report."
        )
    return (
        {"ids": ids, "anchor_overall": overall},
        {
            "arm": arm,
            "adapter_path": str(adapter),
            "adapter_sha256": records.artifact_sha256(adapter),
            "train_sha256": training["train_sha256"],
            "carve_sha256": training["carve_sha256"],
            "n_train": training["n_train"],
            "rows_per_source": training["rows_per_source"],
            "synthetic_ids_added": training["synthetic_ids_added"],
            "training_run": training.get("run"),
            "prompt_revision_sha256": training.get("prompt_revision_sha256"),
            "anchor": {"model": record["model"], "timestamp": record["timestamp"]},
        },
    )


def write_slice(path: Path, holdout: list[dict], slice_ids: dict) -> str:
    """Persist the G1b slice as an explicit id list, and return its SHA256.

    Amendment 3.2 draws G1b from "the holdout rows the base model
    misclassifies"; the gate review of 2026-07-31 read that as the **union** of
    the sentiment and sarcasm error sets, and amendment 3.4 (2) puts the
    measurement on our own pod. Counts were enough to choose a base model; a
    gate needs the ids, because Phase 4's fix-rate is computed row by row
    against exactly this list.
    """
    payload = {
        "definition": "union(sentiment errors, sarcasm errors) of the base model on the frozen"
        " sarcasm holdout — SPEC amendment 3.2 as read by the 2026-07-31 gate review,"
        " measured on our own pod per amendment 3.4 (2)",
        "input": "sarcasm_holdout",
        "n_holdout_scored": len(holdout),
        "n": len(slice_ids["union"]),
        "n_sentiment_errors": len(slice_ids["sentiment"]),
        "n_sarcasm_errors": len(slice_ids["sarcasm"]),
        "ids": slice_ids["union"],
        "sentiment_error_ids": slice_ids["sentiment"],
        "sarcasm_error_ids": slice_ids["sarcasm"],
        "note": (
            "Fewer than 100 rows is the pre-registered fallback, not a defect: amendment 3.2"
            " says the slice is then whatever the base model errs on and the smaller n is"
            " reported next to the gate verdict. Nothing is topped up to reach a count."
        ),
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")
    return sha256(text.encode("utf-8")).hexdigest()


def append_record_file(path: Path) -> int:
    """Append a record produced by ``--record-out`` on another machine.

    The pod holds a throwaway checkout, so its `results/baselines.json` is not
    the project's file and must never travel back over it — wholesale
    replacement of an append-only anchor is the mistake `spend_3b.json` has a
    footgun note about. What travels is the record the scorer built there.
    """
    record = json.loads(path.read_text(encoding="utf-8"))
    history = json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.exists() else {}
    for existing in history.get(record["model"], []):
        if existing["timestamp"] == record["timestamp"]:
            raise SystemExit(
                f"{record['model']} @ {record['timestamp']} is already in"
                f" {RESULTS.name} — appending it twice would double a row, not add one"
            )
    append(record)
    print(f"appended {record['model']} @ {record['timestamp']} to {RESULTS.name}")
    if record.get("diagnostics", {}).get("gate_anchor_valid") is False:
        # Appending it is right — the 27B rows live in the file the same way, and
        # evidence of a bad run beats a gap. Saying so out loud is what stops it
        # from being read as this phase's anchor.
        print("  NOTE: gate_anchor_valid is false — this row anchors no gate without an operator")
        print("        decision, and no G1b slice was written for it.")
    return 0


def verify_pin(key: str, model: str, tag: str, quantization: str | None) -> dict:
    """Refuse to spend if the pinned endpoint is not the one the ADR pinned."""
    endpoints = zero_shot.get(f"/models/{model}/endpoints", key)["data"]["endpoints"]
    match = [e for e in endpoints if e.get("tag") == tag]
    if not match:
        raise SystemExit(f"{model}: pinned endpoint {tag!r} is gone — stop and report")
    found = match[0].get("quantization")
    if quantization and found != quantization:
        raise SystemExit(
            f"{model}: {tag} now serves {found!r}, not the pinned {quantization!r} — stop and report"
        )
    return match[0]


def precision_probe(key: str) -> int:
    """Task 2 of the 3b brief, as a command rather than a one-off.

    Prints candidate x provider x quantization, applies the pre-registered rule
    verbatim, and names the branch that fires. Read-only: GET requests, no spend.
    """
    candidates = [slug for slug, row in ROWS.items() if not row.get("ref")]
    offered, listings = {}, {}
    for slug in candidates:
        listings[slug] = zero_shot.get(f"/models/{slug}/endpoints", key)["data"]["endpoints"]
        offered[slug] = {e.get("quantization") for e in listings[slug]}

    print(
        f"{'candidate':<24} {'endpoint tag':<22} {'quant':<8} {'$in':>7} {'$out':>8} {'st':>4} up1d"
    )
    for slug in candidates:
        for endpoint in listings[slug]:
            pricing = endpoint["pricing"]
            print(
                f"{slug.split('/')[-1]:<24} {str(endpoint.get('tag')):<22}"
                f" {str(endpoint.get('quantization')):<8}"
                f" {float(pricing['prompt']) * 1e6:>7.3f} {float(pricing['completion']) * 1e6:>8.3f}"
                f" {str(endpoint.get('status')):>4} {(endpoint.get('uptime_last_1d') or 0):.1f}%"
            )
        print()

    # The rule, verbatim: bf16 for ALL THREE, otherwise fp8 for ALL THREE.
    missing_bf16 = [slug for slug in candidates if "bf16" not in offered[slug]]
    chosen = "fp8" if missing_bf16 else "bf16"
    if missing_bf16:
        print(f"bf16 branch does NOT fire: no bf16 endpoint for {', '.join(missing_bf16)}")
    print(f"RULE FIRES: {chosen} for all {len(candidates)} candidates")

    without = [slug for slug in candidates if chosen not in offered[slug]]
    if without:
        raise SystemExit(
            f"STOP: {chosen} is not offered for {', '.join(without)} and bf16 is not offered for"
            f" {', '.join(missing_bf16)} — neither precision covers all three. Report; do not"
            " improvise a third option."
        )

    print("\npinned endpoints (ADR 3b-infra-and-precision §(b)):")
    for slug in candidates:
        pinned = ROWS[slug]
        match = [e for e in listings[slug] if e.get("tag") == pinned["tag"]]
        state = "GONE" if not match else match[0].get("quantization")
        agrees = "ok" if state == chosen == pinned["quantization"] else "MISMATCH — stop and report"
        print(
            f"  {slug:<24} {pinned['tag']:<22} pinned {pinned['quantization']} · now {state} · {agrees}"
        )
    return 0


def read_ledger(usage_now: float) -> dict:
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {"openrouter_total_usage_at_3b_start": usage_now, "runs": []}


def write_ledger(ledger: dict) -> None:
    LEDGER.parent.mkdir(exist_ok=True)
    LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def g1b_zero_shot(holdout: list[dict], holdout_labels: list[dict]) -> tuple[dict, dict, dict]:
    """The G1b entry of a run with no fine-tune: the slice, not the fix-rate.

    Amendment 3.2 says the slice is what the base model "misclassifies"; the
    holdout carries two labels and the amendment names neither, so both error
    sets and their union are reported and the operator picks the reading at the
    Phase 4 gate — the executor does not decide a gate definition.
    """
    errs = {
        field: {
            row["id"]
            for row, pred in zip(holdout, holdout_labels)
            if not row["unclear"] and row[field] != pred[field]
        }
        for field in ("sentiment", "sarcasm")
    }
    counts = {
        "base_errs_sentiment": len(errs["sentiment"]),
        "base_errs_sarcasm": len(errs["sarcasm"]),
        "base_errs_union": len(errs["sentiment"] | errs["sarcasm"]),
    }
    entry = {
        "gate": "G1b",
        "metric": "sarcasm slice fix-rate (sarcasm_holdout)",
        "value": None,
        "n": {"holdout_scored": len(holdout), **counts},
        "note": (
            "the fix-rate needs a fine-tune (Phase 4); what this run contributes is the"
            " slice. Amendment 3.2 defines it as the rows this base model misclassifies"
            " and the holdout carries two labels, so all three counts are reported and"
            " the reading is the operator's call at the Phase 4 gate."
        ),
    }
    ids = {
        "sentiment": sorted(errs["sentiment"]),
        "sarcasm": sorted(errs["sarcasm"]),
        "union": sorted(errs["sentiment"] | errs["sarcasm"]),
    }
    return entry, counts, ids


def g1b_fix_rate(
    holdout: list[dict], holdout_labels: list[dict], gate_slice: dict, overall: float
) -> dict:
    # ``overall`` is this run's G1a number; ``gate_slice["anchor_overall"]`` is
    # the anchor's, and the gate is the drop between them.
    """The G1b entry of a fine-tuned run: the pre-registered slice, scored.

    The slice is the anchor's persisted 44 ids (amendment 3.5 (3)) — never this
    model's error set, which is why nothing here recomputes one. A row of the
    slice that this run did not score raises inside the scorer rather than
    counting as unfixed: an incomplete run must not read as a failed gate.

    ``base_errs_*`` deliberately do not appear. On a fine-tuned run those
    numbers would be *this* model's errors under a field name that says "base" —
    a plausible number in a gate record that nothing downstream could question.

    The ≤2 pp guard travels with the fix-rate because it is half of the gate:
    G1b is "fixes ≥60% **while** overall macro-F1 degrades ≤2 pp", and the
    overall in question is :func:`scorer.sentiment_macro_f1`'s, measured on the
    comment test set against the same anchor every other bar is measured from.
    """
    gold_labels = {
        row["id"]: {
            "sentiment": UNCLEAR if row["unclear"] else row["sentiment"],
            "sarcasm": None if row["unclear"] else row["sarcasm"],
        }
        for row in holdout
    }
    predicted = {
        row["id"]: {"sentiment": pred["sentiment"], "sarcasm": pred["sarcasm"]}
        for row, pred in zip(holdout, holdout_labels)
    }
    # `holdout` is the SCORED rows, so a slice row that failed to parse is absent
    # from both maps and the scorer would name whichever it checks first. Say what
    # actually happened instead: the denominator is pre-registered, so an unscored
    # slice row is an incomplete eval and never a failed gate.
    missing = [row_id for row_id in gate_slice["ids"] if row_id not in predicted]
    if missing:
        raise SystemExit(
            f"{len(missing)} of {len(gate_slice['ids'])} slice rows were not scored by this"
            f" run: {missing[:5]}. Resume the eval on what is left (--eval-checkpoint) rather"
            " than reading a short slice as a failed G1b; nothing already scored is re-scored."
        )
    fix = scorer.sarcasm_slice_fix_rate(gate_slice["ids"], gold_labels, predicted)
    return {
        "gate": "G1b",
        "metric": "sarcasm slice fix-rate (sarcasm_holdout)",
        "value": fix["rate"],
        "fixed": fix["fixed"],
        "n": {"slice": fix["n"], "holdout_scored": len(holdout)},
        "guard": {
            "metric": "sentiment macro-F1 overall (comments_test)",
            "anchor": gate_slice["anchor_overall"],
            "value": overall,
            "delta": overall - gate_slice["anchor_overall"],
            "max_drop": scorer.G1B_MACRO_F1_DROP,
        },
        "note": (
            "FIXED means the row leaves the union of sentiment and sarcasm errors — correct"
            " on BOTH labels (amendment 3.5 (3)). n is the pre-registered denominator and"
            " travels with the verdict (amendment 3.2's fallback)."
        ),
    }


def build_gates(
    inputs: dict, aliases: dict, gate_slice: dict | None = None
) -> tuple[list, dict, dict | None]:
    """Gate entries, diagnostics and the G1b error sets — every number from the scorer.

    ``gate_slice`` is the fine-tuned branch: ``{"ids": [...], "anchor_overall":
    float}``, the anchor's persisted G1b slice and the macro-F1 its ≤2 pp guard
    is measured against. Without it this is a zero-shot run, which *produces* a
    slice instead of scoring one — and the third return value is that slice, or
    ``None`` when the run scored a pre-registered one and has no business
    writing the file.
    """
    comments, comment_labels = inputs["comments_test"]
    posts, post_labels = inputs["posts_test"]
    holdout, holdout_labels = inputs["sarcasm_holdout"]

    languages = [row["language"] for row in comments]
    sentiment = scorer.sentiment_macro_f1(
        gold(comments, "sentiment"), [x["sentiment"] for x in comment_labels], languages
    )
    holdout_sentiment = scorer.sentiment_macro_f1(
        gold(holdout, "sentiment"),
        [x["sentiment"] for x in holdout_labels],
        [row["language"] for row in holdout],
    )
    if gate_slice is None:
        g1b, g1b_diagnostics, slice_ids = g1b_zero_shot(holdout, holdout_labels)
    else:
        g1b = g1b_fix_rate(holdout, holdout_labels, gate_slice, sentiment["overall"])
        g1b_diagnostics, slice_ids = {}, None
    gates = [
        {
            "gate": "G1a",
            "metric": "sentiment macro-F1 (comments_test)",
            "values": sentiment,
            "n": {"overall": len(comments), **Counter(languages)},
            "gated_languages": list(scorer.GATED_LANGUAGES),
        },
        g1b,
        {
            "gate": "G1c",
            "metric": "intents micro-F1 (comments_test)",
            "value": scorer.intents_micro_f1(
                gold(comments, "intents", unclear=None), [x["intents"] for x in comment_labels]
            ),
            "n": {"overall": len(comments)},
        },
        {
            "gate": "G1d",
            "metric": "post_type macro-F1 (posts_test)",
            "value": scorer.launch_detection_macro_f1(
                gold(posts, "post_type"), [x["post_type"] for x in post_labels]
            ),
            "n": {"overall": len(posts), **Counter(row["post_type"] for row in posts)},
        },
        {
            "gate": "G1d",
            "metric": "relevance macro-F1 (posts_test)",
            "value": scorer.relevance_macro_f1(
                gold(posts, "relevant"), [x["relevant"] for x in post_labels]
            ),
            "n": {
                "overall": len(posts),
                "relevant": sum(1 for row in posts if row["relevant"]),
            },
            "note": "second head of G1d; reported beside it and not gated (amendment 3.3)",
        },
        {
            "gate": "G1e",
            "metric": "brand extraction F1 (posts_test)",
            "value": scorer.brand_extraction_f1(
                gold(posts, "brands", unclear=None), [x["brands"] for x in post_labels], aliases
            ),
            "n": {
                "overall": len(posts),
                "posts_with_brands": sum(1 for row in posts if row["brands"]),
                "gold_entities": sum(
                    len({scorer.normalise_brand(b, aliases) for b in row["brands"]})
                    for row in posts
                ),
                "predicted_entities": sum(
                    len({scorer.normalise_brand(b, aliases) for b in labels["brands"]})
                    for labels in post_labels
                ),
            },
        },
    ]
    diagnostics = {
        "sarcasm_binary_macro_f1_comments_test": scorer.macro_f1(
            gold(comments, "sarcasm"), [x["sarcasm"] for x in comment_labels]
        ),
        "holdout_sentiment_macro_f1": holdout_sentiment,
        "holdout_sarcasm_macro_f1": scorer.macro_f1(
            gold(holdout, "sarcasm"), [x["sarcasm"] for x in holdout_labels]
        ),
        "holdout_sarcasm_detected": sum(1 for x in holdout_labels if x["sarcasm"]),
    } | g1b_diagnostics
    return gates, diagnostics, slice_ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=sorted(ROWS))
    parser.add_argument(
        "--precision-probe",
        action="store_true",
        help="print candidate x provider x quantization and the branch the rule fires (free)",
    )
    parser.add_argument(
        "--reference-only",
        action="store_true",
        help="mark the record so no gate can read it (the frontier row)",
    )
    parser.add_argument(
        "--testset-version",
        choices=sorted(prompts.REVISIONS),
        default=records.DEFAULT_TESTSET_VERSION,
        help="which frozen test set to score, and therefore which prompt revision to render",
    )
    parser.add_argument("--smoke", action="store_true", help="mocked client, no network, no write")
    parser.add_argument("--dry-run", action="store_true", help="estimate and routing, then stop")
    parser.add_argument("--probe", type=int, default=0, metavar="N", help="N live rows per input")
    parser.add_argument("--max-run-usd", type=float, default=DEFAULT_RUN_CAP_USD)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument(
        "--backend",
        choices=("openrouter", "local"),
        default="openrouter",
        help="where the weights are: OpenRouter (3b's rows) or this GPU (Phase 4)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=local_llm.DEFAULT_BATCH_SIZE,
        help="--backend local: rows per padded generate call",
    )
    parser.add_argument(
        "--model-path",
        help="--backend local: weights directory, if not the Hugging Face repo id",
    )
    parser.add_argument(
        "--revision",
        help="--backend local: pin the weights to one Hugging Face revision",
    )
    parser.add_argument(
        "--adapter",
        type=Path,
        metavar="DIR",
        help="--backend local: a Phase 4 LoRA adapter, loaded UNMERGED onto the NF4 base"
        " (amendment 3.4 (1)). Turns this into an ablation arm's gate eval: G1b becomes the"
        " fix-rate over the anchor's pre-registered slice instead of a slice to write.",
    )
    parser.add_argument(
        "--arm",
        choices=("real-only", "with-synthetic"),
        help="--adapter: which ablation arm this adapter is (amendment 3.4 (3))",
    )
    parser.add_argument(
        "--eval-checkpoint",
        type=Path,
        metavar="PATH",
        help="append every scored row here and skip the rows it already holds, so a crashed"
        " eval resumes on what is left instead of re-scoring (PROMPT-4c crash protocol)",
    )
    parser.add_argument(
        "--record-out",
        type=Path,
        metavar="PATH",
        help="write the record here instead of appending — for a run on a machine whose"
        " results/ is not the project's (the pod). Append it later with --append-record.",
    )
    parser.add_argument(
        "--append-record",
        type=Path,
        metavar="PATH",
        help="append a record written by --record-out to results/baselines.json",
    )
    args = parser.parse_args(argv)

    if args.append_record:
        return append_record_file(args.append_record)
    if args.precision_probe:
        return precision_probe(api_key())
    if not args.model:
        parser.error("--model is required unless --precision-probe is given")

    row = ROWS[args.model]
    local = args.backend == "local"
    if bool(args.adapter) != bool(args.arm):
        parser.error("--adapter and --arm go together: a gate record must name its arm")
    if args.adapter:
        if not local:
            parser.error("--adapter is a local-weights run: pass --backend local")
        if args.reference_only:
            raise SystemExit("--reference-only would hide the arm this phase exists to score")
        if args.batch_size != 1:
            # ADR phase4-own-pod-anchor §(c): greedy is NOT batch-invariant on this
            # stack — measured, one row of 24 flipped its intents between batch 8
            # and batch 1. Defaulting it silently would hide the decision.
            raise SystemExit(
                f"--adapter runs at --batch-size 1, not {args.batch_size}: greedy decoding is"
                " not batch-invariant on bitsandbytes NF4 + A6000 (measured 2026-08-01,"
                " ADR phase4-own-pod-anchor §(c)). Re-measure and record it, or pass 1."
            )
    if local and row.get("ref"):
        raise SystemExit(f"{args.model} is a reference row — the local backend runs the base model")
    if row.get("batch_only"):
        raise SystemExit(
            f"{args.model}: OpenRouter serves this variant only through /api/beta/batches,"
            " which is asynchronous and can take hours. Use --model anthropic/claude-haiku-4.5"
            " (same model, synchronous, ~$0.48 for the reference row instead of ~$0.24)."
            " Logged as deviation D5 in implementation-notes.md."
        )
    if row.get("ref") and not args.reference_only:
        raise SystemExit(f"{args.model} is the frontier reference row — pass --reference-only")
    if args.reference_only and not row.get("ref"):
        raise SystemExit(f"{args.model} is a gated candidate — --reference-only would hide it")

    version = args.testset_version
    resolved = inputs_for(version)
    if version != records.DEFAULT_TESTSET_VERSION and not local:
        raise SystemExit(
            f"test set {version} renders {prompts.REVISIONS[version]}, and the OpenRouter path"
            " sends one text per row with no parent post. Every run of this version is an"
            " own-pod run — pass --backend local."
        )
    data = {name: load(FROZEN / filename) for name, _, filename in resolved}
    if args.probe:
        data = {name: rows[: args.probe] for name, rows in data.items()}
    contexts = {name: post_context(task, data[name]) for name, task, _ in resolved}
    aliases = watchlist_aliases(load_registry(REPO_ROOT / "config" / "registry.yaml").watchlist)
    gate_slice, training = None, None
    if local:
        # Before the weights, before the pod bill: the prompts must be the ones
        # the recorded run sent, or this is not a cross-check.
        assert_prompt_sha_matches_3b(args.model)
        print(f"model {args.model} · backend local · quantization {local_llm.QUANTIZATION}")
        print(f"greedy · max_new_tokens {local_llm.MAX_NEW_TOKENS} · seed {SEED}")
        print(f"prompt SHA256 equal to the recorded {args.model} run: yes")
        if args.adapter:
            gate_slice, training = arm_preflight(args.adapter, args.arm, version)
            print(f"arm {training['arm']} · adapter sha256 {training['adapter_sha256']}")
            print(f"  dataset sha256 {training['train_sha256']} ({training['n_train']} rows)")
            print(f"  G1b slice {len(gate_slice['ids'])} ids, sha256 verified against the anchor")
            print(f"  guard anchor (G1a overall) {gate_slice['anchor_overall']:.4f}")
    else:
        print(f"model {args.model} · endpoint {row['tag']} · quantization {row['quantization']}")
        print(f"temperature {TEMPERATURE} · max_tokens {MAX_TOKENS} · seed {SEED}")
    for task in prompts.TASKS:
        print(f"prompt {task} sha256 {prompts.prompt_sha256(task)}")
    print(f"test set {version} · rendering {prompts.REVISIONS[version]}")
    for name, task, filename in resolved:
        state = "" if contexts[name] is None else f" · {len(contexts[name])} parent posts"
        print(f"  {name:<16} {filename:<26} {task}{state}")

    runtime = None
    if args.smoke:
        client, budget = FakeClient(), None
        if local:
            runtime = {"smoke": "no weights were loaded"}
    elif local:
        budget = None
        weights = args.model_path or local_llm.MODEL_ID
        tokenizer, model = local_llm.load(weights, args.revision)
        if args.adapter:
            # Unmerged, onto the 4-bit base: the deliverable artefact is exactly
            # this pair, and every gate is scored in the configuration that
            # serves (amendment 3.4 (1); merging stays forbidden until Phase 5).
            from peft import PeftModel

            model = PeftModel.from_pretrained(model, str(args.adapter))
            model.eval()
        client = local_llm.LocalClient(tokenizer, model)
        runtime = local_llm.environment(model, weights=weights, revision=args.revision)
        for field, value in runtime.items():
            print(f"  {field:<20} {value}")
        if args.dry_run:
            print("\n--dry-run: weights loaded, nothing scored")
            return 0
    else:
        key = api_key()
        endpoint = verify_pin(key, args.model, row["tag"], row["quantization"])
        usage_now = zero_shot.total_usage(key)
        ledger = read_ledger(usage_now)
        spent_before = usage_now - ledger["openrouter_total_usage_at_3b_start"]
        estimates = {
            name: zero_shot.estimate_cost(
                rows=[r["text"] for r in data[name]],
                prompt_chars=len(prompts.PROMPTS[task]),
                pricing=endpoint["pricing"],
                completion_tokens=60,
            )
            for name, task, _ in resolved
        }
        estimate = sum(e["usd"] for e in estimates.values())
        print(
            f"\npricing $/Mtok  in {float(endpoint['pricing']['prompt']) * 1e6:.3f}"
            f" · out {float(endpoint['pricing']['completion']) * 1e6:.3f}"
        )
        for name, value in estimates.items():
            print(f"  estimate {name:<16} {value['requests']:>4} req  ${value['usd']:.4f}")
        print(f"  ESTIMATE TOTAL                     ${estimate:.4f}")
        print(
            f"caps: this run ${args.max_run_usd:.2f} · all of 3b ${PHASE_CAP_USD:.2f}"
            f" (spent so far in 3b ${spent_before:.4f})"
        )
        if estimate > args.max_run_usd:
            raise SystemExit(
                f"estimate ${estimate:.4f} exceeds the per-run cap ${args.max_run_usd:.2f}"
                " — stop and report rather than raising the cap silently"
            )
        if args.dry_run:
            print("\n--dry-run: nothing spent")
            return 0
        budget = zero_shot.Budget(PHASE_CAP_USD, args.max_run_usd, spent_before)
        client = Client(key, args.model, row["tag"], row["quantization"], budget, threading.Lock())

    checkpoint, resumed = args.eval_checkpoint, {}
    if checkpoint:
        resumed = open_checkpoint(
            checkpoint,
            {
                "model": args.model,
                "arm": args.arm,
                "adapter_sha256": training["adapter_sha256"] if training else None,
                "batch_size": args.batch_size if local else None,
                "probe": args.probe,
                "prompt_sha256": {task: prompts.prompt_sha256(task) for task in prompts.TASKS},
                "testset_version": version,
                "prompt_revision_sha256": prompts.revision_sha256(version),
            },
        )
        print(f"\ncheckpoint {checkpoint} — {len(resumed)} rows already scored")

    scored_inputs, failure_blocks = {}, []
    try:
        for name, task, _ in resolved:
            if local:
                done = {
                    row_id: entry for (input_, row_id), entry in resumed.items() if input_ == name
                }
                pending = [row for row in data[name] if row["id"] not in done]
                if done:
                    print(f"\n{name}: {len(done)} rows resumed, {len(pending)} left to score")
                on_row = None
                if checkpoint:

                    def on_row(scored, name=name):  # noqa: E731 — the input it belongs to
                        append_checkpoint(checkpoint, name, scored)

                by_row = (
                    None
                    if contexts[name] is None
                    else {row["id"]: post for row, post in zip(data[name], contexts[name])}
                )
                fresh = classify_local(
                    client,
                    task,
                    pending,
                    args.batch_size,
                    on_row,
                    None if by_row is None else [by_row[row["id"]] for row in pending],
                )
                by_id = done | {entry["id"]: entry for entry in fresh}
                outcomes = [by_id[row["id"]] for row in data[name]]
            else:
                outcomes = classify(client, task, data[name], args.concurrency)
            rows, labels, failures = split(data[name], outcomes)
            scored_inputs[name] = (rows, labels)
            block = failure_block(name, outcomes, failures)
            failure_blocks.append(block)
            print(
                f"\n{name}: scored {block['scored']}/{block['rows']}"
                f" · parse {block['parse_failures']} · api {block['api_failures']}"
                f" · generation {block['generation_failures']}"
                f" · truncated {block['truncated']}"
            )
            for reason, count in block["reasons"].items():
                print(f"    {count:>4}  {reason}")
            if budget is not None:
                print(f"    spend so far this run ${budget.run_spend:.4f}")
                zero_shot.call_with_retry(
                    lambda: budget.reconcile(
                        zero_shot.total_usage(key) - ledger["openrouter_total_usage_at_3b_start"]
                    )
                )
    except zero_shot.BudgetExceeded as err:
        print(f"\nBUDGET CAP TRIPPED: {err}")
        print("No record was written — a partial run must not become a gate anchor.")
        return 2

    if args.probe:
        print("\n--probe: no record written")
        # The per-row answers, not just the counts. Two probes at different batch
        # sizes are only a batch-invariance check if what they print is the
        # labels; an aggregate "scored 3/3" is identical whenever both parse.
        for line in prediction_lines(scored_inputs):
            print(f"  {line}")
        if budget is not None:
            print(f"actual spend this probe ${budget.run_spend:.4f}")
        if not args.smoke:
            print(f"tokens {dict(client.usage)}")
        return 0

    if any(block["scored"] == 0 for block in failure_blocks):
        raise SystemExit("an input scored zero rows — stop and report, do not write a record")

    gates, diagnostics, slice_ids = build_gates(scored_inputs, aliases, gate_slice)
    unusable = {b["input"]: (b["rows"] - b["scored"]) / b["rows"] for b in failure_blocks}
    anchor_valid = all(share <= UNUSABLE_LIMIT for share in unusable.values())
    diagnostics |= {
        "failures": failure_blocks,
        "gate_anchor_valid": anchor_valid,
        "note": (
            "diagnostics, not gates."
            + (
                " G1b is the fix-rate over the anchor's pre-registered slice; no base_errs_*"
                " appear, because on a fine-tuned run they would be this model's errors under"
                " a name that says base."
                if gate_slice
                else " base_errs_* are this base model's error sets on the frozen sarcasm"
                " holdout — the raw material of the G1b slice (amendment 3.2), reported for"
                " both labels because the amendment names neither."
            )
            + (
                ""
                if anchor_valid
                else f" GATE ANCHOR INVALID: unusable rows exceed {UNUSABLE_LIMIT:.0%} in"
                f" {[k for k, v in unusable.items() if v > UNUSABLE_LIMIT]} — this run must not"
                " anchor G1d/G1e without an operator decision."
            )
        ),
    }

    if args.smoke:
        print("\n--smoke: record built, nothing written")
        print(
            json.dumps(
                {"gates": gates, "diagnostics": diagnostics},
                ensure_ascii=False,
                indent=2,
                default=str,
            )[:2400]
        )
        return 0

    timestamp = datetime.now(UTC).isoformat(timespec="seconds")
    dump = predictions_path(args.model, timestamp)
    dump_sha = write_predictions(dump, scored_inputs)
    head_prefix = f"{training['arm']} fine-tune · " if training else "zero-shot "
    shared = {
        "seed": SEED,
        "temperature": TEMPERATURE,
        "prompt_sha256": {task: prompts.prompt_sha256(task) for task in prompts.TASKS},
        "testset_version": version,
        "prompt_revision": prompts.REVISIONS[version],
        "prompt_revision_sha256": prompts.revision_sha256(version),
        "inputs": {
            name: {"file": filename, "sha256": sha256((FROZEN / filename).read_bytes()).hexdigest()}
            for name, _, filename in resolved
        },
        "heads": {
            "T1": f"{head_prefix}sentiment 3-class · sarcasm binary · intents multi-label",
            "T2": f"{head_prefix}relevance binary · post_type 3-class · brands free-text",
        },
        # Overridden by `local_config` when an adapter was loaded — see there for
        # why the difference is what keeps `records.anchor` honest.
        "train_sources": records.ANCHOR_TRAIN_SOURCES,
        "scored_ids_sha256": {
            name: scored_ids_sha256(rows) for name, (rows, _) in scored_inputs.items()
        },
        "predictions_path": str(dump.relative_to(REPO_ROOT)),
        "predictions_sha256": dump_sha,
        "tokens": dict(client.usage),
    }

    if local:
        config = local_config(
            shared,
            args.batch_size,
            runtime,
            training,
            anchor_valid,
            slice_ids,
            scored_inputs,
            version,
        )
    else:
        usage_after = zero_shot.total_usage(key)
        budget.reconcile(usage_after - ledger["openrouter_total_usage_at_3b_start"])
        actual = usage_after - usage_now
        config = shared | {
            "backend": "openrouter",
            "max_tokens": MAX_TOKENS,
            "provider": {
                "endpoint": row["tag"],
                "provider_name": endpoint.get("provider_name"),
                "quantization": endpoint.get("quantization"),
                "pinned_quantization": row["quantization"],
                "allow_fallbacks": False,
            },
            "spend_usd": round(actual, 6),
            "determinism_note": (
                "third-party serving endpoint: provider-side determinism is NOT guaranteed,"
                " temperature 0 and a fixed seed notwithstanding. The model chosen at the"
                " Phase 4 gate is re-run zero-shot on our own GPU during the Phase 4 smoke"
                " as the cross-check (ADR 3b-infra-and-precision §(d))."
            ),
        }

    record = zero_shot.build_record(
        model=args.model,
        timestamp=timestamp,
        git=git_state(),
        config=config,
        gates=gates,
        diagnostics=diagnostics,
        reference_only=args.reference_only,
    )
    if args.record_out:
        args.record_out.parent.mkdir(parents=True, exist_ok=True)
        args.record_out.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"\nwrote {args.record_out} — append it with --append-record, nothing appended here")
    else:
        append(record)
        print(f"\nwrote {RESULTS.relative_to(REPO_ROOT)} — read it with scripts/show_results.py")

    if not local:
        ledger["runs"].append(
            {
                "model": args.model,
                "timestamp": record["timestamp"],
                "usd": round(actual, 6),
                "requests": sum(b["rows"] for b in failure_blocks),
            }
        )
        write_ledger(ledger)
        print(
            f"actual spend this run ${actual:.4f}"
            f" · 3b total ${usage_after - ledger['openrouter_total_usage_at_3b_start']:.4f}"
            f" of ${PHASE_CAP_USD:.2f}"
        )
    print(f"tokens {dict(client.usage)}")
    print(f"wrote {dump.relative_to(REPO_ROOT)} — {len(prediction_lines(scored_inputs))} rows")
    # `slice_ids` is None when an arm scored the pre-registered slice instead of
    # writing one — the same condition `local_config` branches on, and the reason
    # this line is not guarded by `anchor_valid` alone.
    if local and anchor_valid and slice_ids is not None:
        print(
            f"wrote {SLICE_OF[version].relative_to(REPO_ROOT)} — G1b slice n"
            f" {len(slice_ids['union'])}"
            f" of {len(scored_inputs['sarcasm_holdout'][0])} holdout rows"
            f" (sentiment {len(slice_ids['sentiment'])} ∪ sarcasm {len(slice_ids['sarcasm'])})"
        )
        if len(slice_ids["union"]) < 100:
            print(
                "  n < 100: amendment 3.2's pre-registered fallback — the slice is whatever the"
                " base model errs on and the smaller n is reported beside the gate verdict."
                " Nothing is topped up."
            )
    code = [p for p in record["git"]["dirty"] if p.startswith(("src/", "scripts/", "config/"))]
    if code:
        print(
            f"WARNING: uncommitted code — {record['git']['commit'][:9]} does not reproduce: {code}"
        )
    if not anchor_valid:
        print(
            f"\nSTOP AND REPORT: unusable rows exceed {UNUSABLE_LIMIT:.0%} in"
            f" {[k for k, v in unusable.items() if v > UNUSABLE_LIMIT]}. The record is written"
            " so the evidence survives, marked gate_anchor_valid false; no G1b slice was"
            " written and this run anchors nothing. Do not re-run in a loop — report."
        )
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
