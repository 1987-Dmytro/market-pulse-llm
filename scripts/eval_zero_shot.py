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

from market_pulse import prompts, scorer, zero_shot  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402
from market_pulse.scorer import UNCLEAR  # noqa: E402

FROZEN = REPO_ROOT / "data" / "frozen"
RESULTS = REPO_ROOT / "results" / "baselines.json"
LEDGER = REPO_ROOT / "results" / "spend_3b.json"
PREDICTIONS = REPO_ROOT / "results" / "predictions"

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

INPUTS = (
    ("comments_test", "T1", "comments_test.jsonl"),
    ("posts_test", "T2", "posts_test.jsonl"),
    ("sarcasm_holdout", "T1", "sarcasm_holdout.jsonl"),
)


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

    def __call__(self, task: str, text: str) -> dict:
        with self.lock:
            step = next(self.cycles[task])
        if step == 4:
            raise zero_shot.ApiError(503, "fake endpoint down")
        return {
            "content": self.REPLIES[task][step],
            "finish_reason": "stop",
            "cost": 0.0,
            "usage": {},
            "generation_id": f"fake-{task}-{step}",
        }


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
            return {"id": row["id"], "failure": "api", "reason": f"{type(err).__name__}: {err}"}
        outcome = {"id": row["id"], "finish_reason": reply["finish_reason"]}
        try:
            return outcome | {"labels": prompts.parse_reply(task, reply["content"])}
        except prompts.ParseError as err:
            return outcome | {"failure": "parse", "reason": err.reason}

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        return list(pool.map(one, rows))


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
        "api_failures": kinds["api"],
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


def predictions_path(model: str, timestamp: str) -> Path:
    """``results/predictions/<sanitized-slug>--<UTC-ts>.jsonl``."""
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", model)
    stamp = re.sub(r"[^0-9TZ]", "", timestamp.replace("+00:00", "Z"))
    return PREDICTIONS / f"{slug}--{stamp}.jsonl"


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


def build_gates(inputs: dict, aliases: dict) -> tuple[list[dict], dict]:
    """Gate entries and diagnostics, every number computed by the scorer."""
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
    # Amendment 3.2 says the slice is what the base model "misclassifies"; the
    # holdout carries two labels and the amendment names neither. Both error sets
    # and their union are reported, and the operator picks the reading at the
    # Phase 4 gate — the executor does not decide a gate definition.
    sentiment_errs = {
        row["id"]
        for row, pred in zip(holdout, holdout_labels)
        if not row["unclear"] and row["sentiment"] != pred["sentiment"]
    }
    sarcasm_errs = {
        row["id"]
        for row, pred in zip(holdout, holdout_labels)
        if not row["unclear"] and row["sarcasm"] != pred["sarcasm"]
    }
    gates = [
        {
            "gate": "G1a",
            "metric": "sentiment macro-F1 (comments_test)",
            "values": sentiment,
            "n": {"overall": len(comments), **Counter(languages)},
            "gated_languages": list(scorer.GATED_LANGUAGES),
        },
        {
            "gate": "G1b",
            "metric": "sarcasm slice fix-rate (sarcasm_holdout)",
            "value": None,
            "n": {
                "holdout_scored": len(holdout),
                "base_errs_sentiment": len(sentiment_errs),
                "base_errs_sarcasm": len(sarcasm_errs),
                "base_errs_union": len(sentiment_errs | sarcasm_errs),
            },
            "note": (
                "the fix-rate needs a fine-tune (Phase 4); what this run contributes is the"
                " slice. Amendment 3.2 defines it as the rows this base model misclassifies"
                " and the holdout carries two labels, so all three counts are reported and"
                " the reading is the operator's call at the Phase 4 gate."
            ),
        },
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
        "base_errs_sentiment": len(sentiment_errs),
        "base_errs_sarcasm": len(sarcasm_errs),
        "base_errs_union": len(sentiment_errs | sarcasm_errs),
    }
    return gates, diagnostics


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
    parser.add_argument("--smoke", action="store_true", help="mocked client, no network, no write")
    parser.add_argument("--dry-run", action="store_true", help="estimate and routing, then stop")
    parser.add_argument("--probe", type=int, default=0, metavar="N", help="N live rows per input")
    parser.add_argument("--max-run-usd", type=float, default=DEFAULT_RUN_CAP_USD)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    args = parser.parse_args(argv)

    if args.precision_probe:
        return precision_probe(api_key())
    if not args.model:
        parser.error("--model is required unless --precision-probe is given")

    row = ROWS[args.model]
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

    data = {name: load(FROZEN / filename) for name, _, filename in INPUTS}
    if args.probe:
        data = {name: rows[: args.probe] for name, rows in data.items()}
    aliases = watchlist_aliases(load_registry(REPO_ROOT / "config" / "registry.yaml").watchlist)
    print(f"model {args.model} · endpoint {row['tag']} · quantization {row['quantization']}")
    print(f"temperature {TEMPERATURE} · max_tokens {MAX_TOKENS} · seed {SEED}")
    for task in prompts.TASKS:
        print(f"prompt {task} sha256 {prompts.prompt_sha256(task)}")

    if args.smoke:
        client, budget = FakeClient(), None
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
            for name, task, _ in INPUTS
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

    scored_inputs, failure_blocks = {}, []
    try:
        for name, task, _ in INPUTS:
            outcomes = classify(client, task, data[name], args.concurrency)
            rows, labels, failures = split(data[name], outcomes)
            scored_inputs[name] = (rows, labels)
            block = failure_block(name, outcomes, failures)
            failure_blocks.append(block)
            print(
                f"\n{name}: scored {block['scored']}/{block['rows']}"
                f" · parse {block['parse_failures']} · api {block['api_failures']}"
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
        if not args.smoke:
            print(f"actual spend this probe ${budget.run_spend:.4f}")
            print(f"tokens {dict(client.usage)}")
        return 0

    if any(block["scored"] == 0 for block in failure_blocks):
        raise SystemExit("an input scored zero rows — stop and report, do not write a record")

    gates, diagnostics = build_gates(scored_inputs, aliases)
    unusable = {b["input"]: (b["rows"] - b["scored"]) / b["rows"] for b in failure_blocks}
    anchor_valid = all(share <= UNUSABLE_LIMIT for share in unusable.values())
    diagnostics |= {
        "failures": failure_blocks,
        "gate_anchor_valid": anchor_valid,
        "note": (
            "diagnostics, not gates. base_errs_* are this base model's error sets on the"
            " frozen sarcasm holdout — the raw material of the G1b slice (amendment 3.2),"
            " reported for both labels because the amendment names neither."
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

    usage_after = zero_shot.total_usage(key)
    budget.reconcile(usage_after - ledger["openrouter_total_usage_at_3b_start"])
    actual = usage_after - usage_now
    timestamp = datetime.now(UTC).isoformat(timespec="seconds")
    dump = predictions_path(args.model, timestamp)
    dump_sha = write_predictions(dump, scored_inputs)
    record = zero_shot.build_record(
        model=args.model,
        timestamp=timestamp,
        git=git_state(),
        config={
            "seed": SEED,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "provider": {
                "endpoint": row["tag"],
                "provider_name": endpoint.get("provider_name"),
                "quantization": endpoint.get("quantization"),
                "pinned_quantization": row["quantization"],
                "allow_fallbacks": False,
            },
            "prompt_sha256": {task: prompts.prompt_sha256(task) for task in prompts.TASKS},
            "heads": {
                "T1": "zero-shot sentiment 3-class · sarcasm binary · intents multi-label",
                "T2": "zero-shot relevance binary · post_type 3-class · brands free-text",
            },
            "train_sources": {"zero-shot": "no training data"},
            "scored_ids_sha256": {
                name: scored_ids_sha256(rows) for name, (rows, _) in scored_inputs.items()
            },
            "predictions_path": str(dump.relative_to(REPO_ROOT)),
            "predictions_sha256": dump_sha,
            "spend_usd": round(actual, 6),
            "tokens": dict(client.usage),
            "determinism_note": (
                "third-party serving endpoint: provider-side determinism is NOT guaranteed,"
                " temperature 0 and a fixed seed notwithstanding. The model chosen at the"
                " Phase 4 gate is re-run zero-shot on our own GPU during the Phase 4 smoke"
                " as the cross-check (ADR 3b-infra-and-precision §(d))."
            ),
        },
        gates=gates,
        diagnostics=diagnostics,
        reference_only=args.reference_only,
    )
    append(record)
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
        f"\nactual spend this run ${actual:.4f}"
        f" · 3b total ${usage_after - ledger['openrouter_total_usage_at_3b_start']:.4f}"
        f" of ${PHASE_CAP_USD:.2f}"
    )
    print(f"tokens {dict(client.usage)}")
    print(f"wrote {RESULTS.relative_to(REPO_ROOT)} — read it with scripts/show_results.py")
    print(f"wrote {dump.relative_to(REPO_ROOT)} — {len(prediction_lines(scored_inputs))} rows")
    code = [p for p in record["git"]["dirty"] if p.startswith(("src/", "scripts/", "config/"))]
    if code:
        print(
            f"WARNING: uncommitted code — {record['git']['commit'][:9]} does not reproduce: {code}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
