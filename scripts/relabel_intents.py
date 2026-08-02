#!/usr/bin/env python3
"""Re-label the `intents` column under taxonomy v2 — one field, one budget.

SPEC amendment 3.8 adds a sixth intent (`service`) and pre-registers an intents
re-label of the labelled data. This is the runner for it. 4.5d spent it on a probe —
~50 already-labelled TRAIN rows, to measure how far v2 moves the column and what the
full pass would cost — and 4.5e runs the full pass over every labelled non-frozen
row, into a staged `_tax2` copy beside each source.

What the design refuses rather than promises:

- **one column moves.** The request asks for `intents` and nothing else
  (`prompts.RELABEL_INTENTS_PROMPT`), and every produced row is proved by putting
  the old intents back: unless the line then matches its source byte for byte, the
  run stops. `sentiment`, `sarcasm` and `unclear` cannot move through a path that
  never carries them.
- **no test row is re-labelled here.** docs/PROMPT-4.5d.md: no test-row labelling
  at all. The four frozen test files are read for their ids and every drawn row is
  checked against them — a missing file is a defect, not a smaller forbidden set.
- **the ledger is anchored before the first request.** The phase's ledger is written
  before anything is spent, so a crash cannot leave the next run counting from a
  balance that already includes this one. Which ledger and which cap is `--phase`,
  and it has no default: a run that does not say whose money it is does not start.
- **a row that comes back unreadable is counted, named and excluded** — never
  coerced to `[]`, which is the majority answer and would flatter the drift rate.
  Every source row is accounted for as labelled, skipped or unusable, and the three
  are required to add up to the file.

    python3.11 scripts/relabel_intents.py --phase 45d --smoke
    python3.11 scripts/relabel_intents.py --phase 45e --source comments_train --limit 0 --dry-run
    python3.11 scripts/relabel_intents.py --phase 45e --source comments_train --limit 0
    python3.11 scripts/relabel_intents.py --phase 45e --source all --from-rows data/*/*_tax2.jsonl

Writes the phase's record (append-only) and the re-labelled rows; the source files,
`data/frozen/` gold and `results/baselines.json` are never touched.
"""

import argparse
import json
import random
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))  # the pinned endpoints live with the eval

import eval_zero_shot as evaluator  # noqa: E402
from market_pulse import prompts, zero_shot  # noqa: E402

FROZEN = REPO_ROOT / "data" / "frozen"
ANNOTATION = REPO_ROOT / "data" / "annotation"
RESULTS = REPO_ROOT / "results"

PHASES = {
    "45d": {
        "cap_usd": 2.00,
        "ledger": RESULTS / "spend_45d.json",
        "record": RESULTS / "relabel_probe_45d.json",
        "rows_out": RESULTS / "relabel_45d_probe_rows.jsonl",
    },
    "45e": {
        "cap_usd": 1.50,
        "ledger": RESULTS / "spend_45e.json",
        "record": RESULTS / "relabel_45e.json",
        "rows_out": None,  # staged beside each source — see `staged`
    },
}
"""Each phase's own anchor, cap and record. `--phase` is required and has no default.

A phase's ledger is what its cap is enforced against; charging 4.5e's rows to the
4.5d anchor would silently widen both caps by the other phase's spend, and the
mistake is one forgotten flag away. So the flag is not forgettable."""

SOURCES = {
    "comments_train": FROZEN / "comments_train.jsonl",
    "sarcasm_candidates": ANNOTATION / "sarcasm_candidates.jsonl",
    "holdout_pool": ANNOTATION / "sarcasm_holdout_pool.jsonl",
}
NEVER = (
    FROZEN / "comments_test.jsonl",
    FROZEN / "comments_test_v3.jsonl",
    FROZEN / "sarcasm_holdout.jsonl",
    FROZEN / "sarcasm_holdout_v3.jsonl",
)
"""Every file whose ids this step may not label. Read, not assumed."""

TASK = "relabel_intents_v2"
MODEL = "qwen/qwen3.6-27b"
"""Chosen on the one measurement that exists for it: intents micro-F1 against human
gold on the comment test set (`results/baselines.json`, 3b). 0.768 for this model,
0.774 for `anthropic/claude-haiku-4.5`, 0.798 for `google/gemma-4-31b-it` — and the
last one is the model under test, so gold produced by it would make G1c partly a
measure of agreement with itself. Both alternatives are priced in the record."""

SEED = 42
MAX_TOKENS = 128
RETRY_ATTEMPTS = 6
DEFAULT_CONCURRENCY = 4
"""Four workers, the number `eval_zero_shot` settled on for the same endpoint: enough
to keep a 3,263-row pass under half an hour, few enough that the pinned fp8 endpoint
does not start answering 429. Each row is its own generation either way — concurrency
buys wall-clock and changes no label."""
# The prompt names comments_train + sarcasm_candidates + comments_test; the labelled
# comment rows that carry an intents column are more than that (see the report).
FULL_RELABEL_ROWS = {"prompt 4.5d (train + candidates + test)": 2746, "every labelled row": 3771}


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def staged(source: Path) -> Path:
    """The v2 copy that sits beside a source file — never the source itself.

    The convention the frozen sets already use for a taxonomy that moved (`_v3`
    beside v2): a labelled file is a read-only input, and the re-labelled rows are a
    new file that can be diffed against it line for line."""
    return source.with_name(f"{source.stem}_tax2{source.suffix}")


def load(path: Path) -> tuple[list[dict], list[str]]:
    """Rows and their source lines — the lines are what byte-identity is proved against."""
    if not path.exists():
        raise SystemExit(f"{rel(path)}: not found")
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [json.loads(line) for line in lines], lines


def forbidden_ids() -> set[str]:
    missing = [rel(path) for path in NEVER if not path.exists()]
    if missing:
        raise SystemExit(
            f"the frozen test files are the forbidden set and {missing} are missing — a guard"
            " that cannot read them would let test rows through instead of stopping"
        )
    return {row["id"] for path in NEVER for row in load(path)[0]}


def draw(rows: list[dict], lines: list[str], limit: int, seed: int):
    """A seeded sample in id order — or, with no limit, the file exactly as it is.

    Two different jobs. A *sample* must not depend on the order its file happens to
    be in, so it is drawn from an id-sorted pairing. A *full pass* produces a staged
    copy whose whole point is that it diffs against its source line for line, and
    re-ordering it would throw that away for nothing."""
    if not limit or limit >= len(rows):
        return rows, lines
    paired = sorted(zip(rows, lines), key=lambda pair: pair[0]["id"])
    paired = sorted(random.Random(seed).sample(paired, limit), key=lambda pair: pair[0]["id"])
    return [row for row, _ in paired], [line for _, line in paired]


def relabelled(row: dict, line: str, intents: list[str]) -> str:
    """The row with its intents replaced — proved by putting the old ones back.

    A field-by-field comparison would miss key order, spacing and escaping; the only
    statement worth making is that this line differs from its source in one value.
    """
    produced = json.dumps({**row, "intents": intents}, ensure_ascii=False)
    if json.dumps({**json.loads(produced), "intents": row["intents"]}, ensure_ascii=False) != line:
        raise SystemExit(
            f"{row['id']}: restoring the old intents does not reproduce the source line byte for"
            " byte, so this run changed more than one column. Stop and report."
        )
    return produced


class Asker:
    """One pinned endpoint, one budget, retries — and nothing else it could spend on.

    Thread-safe because the budget is: with workers in flight the guard has to see
    every row's cost as it lands, not a per-worker sum added up at the end, or the
    cap is only a cap on average."""

    def __init__(self, key: str, model: str, tag: str, quantization: str | None, budget):
        self.key, self.model, self.tag, self.quantization = key, model, tag, quantization
        self.budget = budget
        self.lock = threading.Lock()

    def __call__(self, text: str) -> tuple[dict, dict]:
        body = zero_shot.request_body(
            model=self.model,
            messages=prompts.build_messages(TASK, text),
            tag=self.tag,
            quantization=self.quantization,
            max_tokens=MAX_TOKENS,
            seed=SEED,
        )
        payload = zero_shot.call_with_retry(
            lambda: zero_shot.post("/chat/completions", body, self.key)[0], attempts=RETRY_ATTEMPTS
        )
        usage = payload.get("usage") or {}
        with self.lock:
            self.budget.add(float(usage.get("cost") or 0.0))
        return payload, usage


class FakeAsker:
    """The smoke client: every branch of the write path, no network, no spend.

    It still pays into the budget, because the per-row cost and the projection built
    on it are part of what a probe produces and an untested arithmetic path is where
    a $2 cap turns into a $200 one.
    """

    def __init__(self, budget):
        self.budget = budget
        self.calls = 0
        self.lock = threading.Lock()

    def __call__(self, text: str) -> tuple[dict, dict]:
        usage = {"cost": 0.0001, "prompt_tokens": 500, "completion_tokens": 12}
        with self.lock:
            self.calls += 1
            # a reply that is not an answer, so the unusable counter is exercised
            bad = self.calls % 17 == 0
            self.budget.add(float(usage["cost"]))
        reply = '{"intents": ["service"]}' if "розіграш" in text else '{"intents": []}'
        if bad:
            reply = "I cannot label this."
        return {"choices": [{"message": {"content": reply}}], "usage": usage}, usage


def ask_one(row: dict, ask) -> dict:
    """One outcome for one row: the new labels, or the reason there are none."""
    usage: dict = {}
    try:
        payload, usage = ask(row["text"])
        reply = payload["choices"][0]["message"]["content"] or ""
        outcome = {"id": row["id"], "intents": prompts.parse_reply(TASK, reply)["intents"]}
    except prompts.ParseError as err:
        outcome = {"id": row["id"], "intents": None, "unusable": f"parse: {err.reason}"}
    except (zero_shot.ApiError, OSError) as err:
        outcome = {"id": row["id"], "intents": None, "unusable": f"api: {err}"}
    return {**outcome, "usage": usage}


def ask_all(rows: list[dict], ask, concurrency: int = 1, on_row=None) -> list[dict]:
    """One outcome per row, in row order, with ``on_row`` called as each one lands.

    ``BudgetExceeded`` is not caught anywhere below: the cap ends the run, it is not
    one more failed row. Results are consumed in order so the caller can persist each
    one as it arrives — a 3,263-row pass that dies at row 3,000 has still been paid
    for, and an unwritten row is money spent twice."""
    outcomes = []
    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        for index, outcome in enumerate(pool.map(lambda row: ask_one(row, ask), rows), start=1):
            outcomes.append(outcome)
            if on_row:
                on_row(index, outcome)
    return outcomes


EMPTY = "[]"
LABELS = (*prompts.INTENTS_V2, EMPTY)


def churn(old_of: dict[str, set], scored: list[dict]) -> dict:
    """Per old label: how many rows kept it, lost it, and what they carry instead.

    `labels_added` / `labels_removed` are margins and cannot answer the question the
    calibration will be read against — *which* old class the movement came out of.
    A row with two labels is counted under both: this is a co-occurrence matrix, and
    the margins beside it (`before`/`after`) are the row and column totals."""
    matrix = {label: dict.fromkeys(LABELS, 0) for label in LABELS}
    before = dict.fromkeys(LABELS, 0)
    after = dict.fromkeys(LABELS, 0)
    kept = dict.fromkeys(LABELS, 0)
    for out in scored:
        old = sorted(old_of[out["id"]]) or [EMPTY]
        new = sorted(out["intents"]) or [EMPTY]
        for label in old:
            before[label] += 1
            kept[label] += label in new
            for other in new:
                matrix[label][other] += 1
        for label in new:
            after[label] += 1
    return {
        "labels": list(LABELS),
        "old_to_new": {label: row for label, row in matrix.items() if before[label]},
        "margins": {
            label: {
                "before": before[label],
                "after": after[label],
                "kept": kept[label],
                "lost": before[label] - kept[label],
                "gained": after[label] - kept[label],
            }
            for label in LABELS
            if before[label] or after[label]
        },
    }


def drift(rows: list[dict], outcomes: list[dict], split: bool = True) -> dict:
    """What moved, split into the part v2 explains and the part it does not.

    Split again by ``unclear``, because half of a train sample is `unclear` and those
    rows are excluded from every gate: a prevalence over all of them answers "how
    much does v2 move this file" and not "how much does v2 move what G1c scores".
    """
    old_of = {row["id"]: set(row["intents"]) for row in rows}
    scored = [out for out in outcomes if out["intents"] is not None]
    added: dict[str, int] = {}
    removed: dict[str, int] = {}
    changed = service = unexplained = 0
    service_from: dict[str, int] = {}
    for out in scored:
        old, new = old_of[out["id"]], set(out["intents"])
        for label in new - old:
            added[label] = added.get(label, 0) + 1
        for label in old - new:
            removed[label] = removed.get(label, 0) + 1
        changed += old != new
        if "service" in new:
            service += 1
            key = ", ".join(sorted(old)) or "[]"
            service_from[key] = service_from.get(key, 0) + 1
        # A row that gained `service` moved for a reason v2 states — including one
        # whose old label the new rule replaces (a promo mechanic was `price`). A row
        # that changed *without* gaining it moved for a reason the taxonomy does not
        # explain, and that is the part of the drift that is model-versus-annotator.
        unexplained += "service" not in new and old != new
    found = {
        "rows": len(outcomes),
        "scored": len(scored),
        "unusable": [out for out in outcomes if out["intents"] is None],
        "changed": changed,
        "changed_rate": changed / len(scored) if scored else 0.0,
        "changed_without_service": unexplained,
        "changed_without_service_rate": unexplained / len(scored) if scored else 0.0,
        "service_rows": service,
        "service_prevalence": service / len(scored) if scored else 0.0,
        "service_came_from": dict(sorted(service_from.items(), key=lambda kv: -kv[1])),
        "labels_added": dict(sorted(added.items(), key=lambda kv: -kv[1])),
        "labels_removed": dict(sorted(removed.items(), key=lambda kv: -kv[1])),
        "churn": churn(old_of, scored),
    }
    if split:
        unclear_of = {row["id"]: row["unclear"] for row in rows}
        found["by_unclear"] = {
            name: drift(
                [row for row in rows if unclear_of[row["id"]] is flag],
                [out for out in outcomes if unclear_of[out["id"]] is flag],
                split=False,
            )
            for name, flag in (("scoreable", False), ("unclear", True))
        }
    return found


def anchor_key(phase: str) -> str:
    return f"openrouter_total_usage_at_{phase}_start"


def read_ledger(path: Path, phase: str, cap: float, usage_now: float) -> dict:
    if path.exists():
        ledger = json.loads(path.read_text(encoding="utf-8"))
        if anchor_key(phase) not in ledger:
            raise SystemExit(
                f"{rel(path)} carries no {anchor_key(phase)} — it is another phase's anchor."
                " Spending against it would enforce this cap on the wrong balance."
            )
        return ledger
    return {
        anchor_key(phase): usage_now,
        "note": (
            f"lifetime OpenRouter usage read at the start of {phase}, before the first request of"
            f" this phase. Phase spend = total_usage now minus this, and the ${cap:.2f} cap of"
            f" docs/PROMPT-{phase[0]}.{phase[1:]}.md is enforced against that difference. Delete"
            " or regenerate this file and the counter silently restarts at today's usage — the"
            " same footgun results/spend_3b.json carries. Every other phase's anchor is a"
            " different file and is never written here."
        ),
        "cap_usd": cap,
        "runs": [],
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_record(path: Path, record: dict) -> None:
    history = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"runs": []}
    history["runs"].append(record)
    write_json(path, history)


def redrift(sources: list[Path], produced: list[Path]) -> tuple[list[dict], list[dict]]:
    """The drift of a finished run, recomputed from its own output. No requests.

    The split by ``unclear`` was added after the probe had already been paid for,
    and re-running would produce a *different* run (greedy is not deterministic
    across a provider's batches). Re-reading the rows it wrote is the same run.
    """
    by_id = {}
    order = {}
    for source in sources:
        source_rows, source_lines = load(source)
        for index, (row, line) in enumerate(zip(source_rows, source_lines)):
            by_id[row["id"]] = (row, line)
            order[row["id"]] = index
    where = ", ".join(rel(source) for source in sources)
    rows, outcomes = [], []
    for path in produced:
        seen = -1
        for row, line in zip(*load(path)):
            if row["id"] not in by_id:
                raise SystemExit(f"{row['id']}: not in {where} — these rows came from elsewhere")
            source_row, source_line = by_id[row["id"]]
            # the same inverse the run itself is held to, re-checked on what is on disk
            if relabelled(source_row, source_line, row["intents"]) != line:
                raise SystemExit(
                    f"{row['id']}: {rel(path)} differs from its source in more than `intents`"
                )
            if order[row["id"]] <= seen:
                raise SystemExit(
                    f"{row['id']}: {rel(path)} is not in its source's order, so the two files"
                    " cannot be read side by side"
                )
            seen = order[row["id"]]
            rows.append(source_row)
            outcomes.append({"id": row["id"], "intents": row["intents"], "usage": {}})
    return rows, outcomes


def report(record: dict) -> None:
    found = record["drift"]
    print(f"\nsource: {record['source']} · {found['rows']} rows drawn, seed {record['seed']}")
    print(f"model:  {record['model']} @ {record['endpoint']['tag']} · prompt {record['task']}")
    print(f"scored: {found['scored']} · unusable {len(found['unusable'])}")
    print("\ndrift, old intents vs re-labelled")
    print(f"  rows whose set changed          {found['changed']:>4}  {found['changed_rate']:.1%}")
    print(
        f"  ... and did not gain `service`  {found['changed_without_service']:>4} "
        f" {found['changed_without_service_rate']:.1%}  (drift the taxonomy does not explain)"
    )
    print(
        f"  rows carrying `service`         {found['service_rows']:>4} "
        f" {found['service_prevalence']:.1%}"
    )
    print(f"  labels added   {json.dumps(found['labels_added'], ensure_ascii=False)}")
    print(f"  labels removed {json.dumps(found['labels_removed'], ensure_ascii=False)}")
    print(f"  `service` replaced {json.dumps(found['service_came_from'], ensure_ascii=False)}")

    print("\nthe same rows split by `unclear`, which no gate scores")
    print(f"  {'':<12}{'n':>4} {'changed':>9} {'no service':>12} {'`service`':>11}")
    for name, part in found.get("by_unclear", {}).items():
        print(
            f"  {name:<12}{part['scored']:>4} {part['changed_rate']:>8.0%}"
            f" {part['changed_without_service_rate']:>12.0%} {part['service_prevalence']:>11.0%}"
        )

    print("\nchurn: rows carrying an old label (down) that now carry a new one (across)")
    corner = "old \\ new"
    print(f"  {corner:<14}" + "".join(f"{label:>13}" for label in LABELS))
    for label, row in found["churn"]["old_to_new"].items():
        print(f"  {label:<14}" + "".join(f"{row[other]:>13}" for other in LABELS))
    print(f"  {'':<14}" + "".join(f"{'—':>13}" for _ in LABELS))
    for name in ("before", "after", "kept", "lost", "gained"):
        margins = found["churn"]["margins"]
        print(
            f"  {name:<14}"
            + "".join(f"{margins.get(label, {}).get(name, 0):>13}" for label in LABELS)
        )

    if accounting := record.get("accounting"):
        print("\nevery source row accounted for")
        for name, entry in accounting.items():
            print(
                f"  {name:<34}{entry['source_rows']:>6} = {entry['labelled']:>6} labelled"
                f" + {entry['skipped_frozen']:>3} frozen + {entry['unusable']:>3} unusable"
            )

    cost = record["cost"]
    if not cost["requests"]:
        print("\nre-derived from the rows a paid run wrote — no requests, no spend")
        return
    print(f"\ncost: ${cost['usd']:.4f} over {cost['requests']} requests")
    print(
        f"  per row ${cost['usd_per_row']:.6f} · phase spend ${cost['phase_spend_usd']:.4f}"
        f" of ${cost['cap_usd']:.2f}"
    )
    if not record["alternatives"]:
        return
    print(f"{'projection':<44} {'rows':>6} {'this model':>12}   alternatives")
    for name, rows in FULL_RELABEL_ROWS.items():
        alt = "  ".join(
            f"{slug.split('/')[-1]} ${rows * usd:.2f}"
            for slug, usd in record["alternatives"].items()
        )
        print(f"  {name:<42} {rows:>6} {rows * cost['usd_per_row']:>11.2f}   {alt}")


def already_done(rows_out: Path, pairs: dict[str, tuple[dict, str]]) -> dict[str, str]:
    """The rows a previous invocation wrote — re-checked, not adopted.

    A resume that trusts the file on disk trusts whatever wrote it. Each line is put
    back through the same inverse the run itself uses: replace its intents with the
    source's and it has to reproduce the source line byte for byte."""
    if not rows_out.exists():
        return {}
    done = {}
    for row in load(rows_out)[0]:
        if row["id"] not in pairs:
            raise SystemExit(
                f"{rel(rows_out)} holds {row['id']}, which is not in this source — resuming on top"
                " of another run's file would mix two sets of rows into one staged copy"
            )
        source_row, source_line = pairs[row["id"]]
        done[row["id"]] = relabelled(source_row, source_line, row["intents"])
    return done


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=sorted(PHASES), required=True)
    parser.add_argument("--source", choices=[*sorted(SOURCES), "all"], default="comments_train")
    parser.add_argument("--limit", type=int, default=50, help="0 = the whole file, in file order")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--model", default=MODEL, choices=sorted(evaluator.ROWS))
    parser.add_argument("--max-run-usd", type=float, default=None)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument("--smoke", action="store_true", help="fake client, no network, no spend")
    parser.add_argument("--dry-run", action="store_true", help="draw the sample, then stop")
    parser.add_argument(
        "--skip-frozen",
        action="store_true",
        help="drop frozen test/holdout rows from the source instead of refusing the whole run",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="keep the rows already in --rows-out and ask only for the rest",
    )
    parser.add_argument("--rows-out", type=Path, default=None)
    parser.add_argument("--record", type=Path, default=None)
    parser.add_argument(
        "--from-rows",
        type=Path,
        nargs="+",
        help="re-derive the drift of a finished run from the rows it wrote, no requests",
    )
    args = parser.parse_args(argv)
    phase = PHASES[args.phase]
    cap = phase["cap_usd"]
    args.max_run_usd = cap if args.max_run_usd is None else args.max_run_usd
    # A smoke run produces a record shaped exactly like a real one; the one thing it
    # must not do is land where the real one is read from.
    smoke_dir = RESULTS / "smoke"
    args.record = args.record or (
        smoke_dir / phase["record"].name if args.smoke else phase["record"]
    )

    if args.source == "all" and not args.from_rows:
        raise SystemExit("--source all only re-derives drift; a run labels one source at a time")
    sources = list(SOURCES.values()) if args.source == "all" else [SOURCES[args.source]]
    source = sources[0]
    if args.from_rows:
        rows, outcomes = redrift(sources, args.from_rows)
        produced_paths = [rel(path) for path in args.from_rows]
        record = {
            "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
            "task": TASK,
            "model": args.model,
            "endpoint": {"tag": "—", "quantization": None},
            "smoke": False,
            "source": ", ".join(rel(path) for path in sources),
            "source_sha256": {rel(p): sha256(p.read_bytes()).hexdigest() for p in sources},
            "seed": args.seed,
            "prompt_sha256": {},
            "git": evaluator.git_state(),
            "drift": drift(rows, outcomes),
            "per_file": {
                rel(path): drift(*redrift(sources, [path]), split=False) for path in args.from_rows
            },
            "cost": {
                "requests": 0,
                "usd": 0.0,
                "usd_per_row": 0.0,
                "phase_spend_usd": 0.0,
                "cap_usd": cap,
            },
            "alternatives": {},
            "rows_out": produced_paths,
            "note": (
                f"RE-DERIVED from {produced_paths}, the rows a paid run wrote — no model was"
                " called. Re-running would have been a different run, not the same one measured"
                " twice: greedy decoding is not deterministic across a provider's batches."
            ),
        }
        append_record(args.record, record)
        report(record)
        return 0

    args.rows_out = args.rows_out or (
        smoke_dir / f"{source.stem}_tax2.jsonl"
        if args.smoke
        else (phase["rows_out"] or staged(source))
    )
    if args.rows_out.resolve() in {path.resolve() for path in SOURCES.values()}:
        raise SystemExit(f"{rel(args.rows_out)} is a source file — it is a read-only input")

    source_rows, source_lines = load(source)
    banned = forbidden_ids()
    skipped = 0
    if args.skip_frozen:
        keep = [pair for pair in zip(source_rows, source_lines) if pair[0]["id"] not in banned]
        skipped = len(source_rows) - len(keep)
        source_rows, source_lines = [row for row, _ in keep], [line for _, line in keep]
        print(f"{rel(source)}: {skipped} frozen test/holdout rows dropped before the draw")

    in_file = len(source_rows) + skipped
    rows, lines = draw(source_rows, source_lines, args.limit, args.seed)
    if left := banned & {row["id"] for row in rows}:
        raise SystemExit(
            f"{len(left)} drawn rows are in the frozen test files ({sorted(left)[:3]}) —"
            " a test row is never labelled here (--skip-frozen drops them instead)"
        )
    print(f"{rel(source)}: {len(rows)} rows drawn (seed {args.seed}), none in the test files")
    if args.dry_run:
        print("\n".join(f"  {row['id']:<24} {row['intents']}" for row in rows[:10]))
        return 0

    pairs = {row["id"]: (row, line) for row, line in zip(rows, lines)}
    produced = already_done(args.rows_out, pairs) if args.resume else {}
    pending = [row for row in rows if row["id"] not in produced]
    if produced:
        print(f"resume: {len(produced)} rows already written and re-checked, {len(pending)} to go")

    pinned = evaluator.ROWS[args.model]
    endpoint = {"tag": pinned["tag"], "quantization": pinned["quantization"]}
    if args.smoke:
        budget = zero_shot.Budget(cap, args.max_run_usd)
        ask = FakeAsker(budget)
        ledger = None
    else:
        key = evaluator.api_key()
        live = evaluator.verify_pin(key, args.model, pinned["tag"], pinned["quantization"])
        endpoint |= {"served_quantization": live.get("quantization"), "status": live.get("status")}
        usage_now = zero_shot.total_usage(key)
        ledger = read_ledger(phase["ledger"], args.phase, cap, usage_now)
        write_json(phase["ledger"], ledger)  # anchored before the first request, never after
        spent_before = usage_now - ledger[anchor_key(args.phase)]
        budget = zero_shot.Budget(cap, args.max_run_usd, spent_before=spent_before)
        print(
            f"ledger: {args.phase} spend so far ${spent_before:.4f},"
            f" headroom ${budget.headroom():.4f}"
        )
        ask = Asker(key, args.model, pinned["tag"], pinned["quantization"], budget)

    args.rows_out.parent.mkdir(parents=True, exist_ok=True)
    handle = args.rows_out.open("a" if produced else "w", encoding="utf-8")

    def persist(index: int, outcome: dict) -> None:
        """On disk before the next row is asked for — a lost row is money spent twice."""
        row, line = pairs[outcome["id"]]
        if outcome["intents"] is not None:
            produced[outcome["id"]] = relabelled(row, line, outcome["intents"])
            handle.write(produced[outcome["id"]] + "\n")
            handle.flush()
        print(
            f"  {index:>5}/{len(pending)} {outcome['id']:<24}"
            f" {outcome.get('unusable') or outcome['intents']}"
        )

    started = datetime.now(UTC).isoformat(timespec="seconds")
    try:
        outcomes = ask_all(pending, ask, args.concurrency, persist)
    finally:
        handle.close()
    # Written in arrival order for crash safety, re-emitted in the source's own order:
    # a staged copy exists to be diffed against its source line for line.
    ordered = [produced[row["id"]] for row in rows if row["id"] in produced]
    args.rows_out.write_text("\n".join(ordered) + "\n", encoding="utf-8")

    if ledger is not None:
        budget.reconcile(zero_shot.total_usage(key) - ledger[anchor_key(args.phase)])
    unusable = [out for out in outcomes if out["intents"] is None]
    scored = len(pending) - len(unusable)
    if len(rows) != len(produced) + len(unusable):
        raise SystemExit(
            f"{len(rows)} rows drawn but {len(produced)} written and {len(unusable)} unusable —"
            " a row that is neither is a row silently left on the old taxonomy"
        )
    settled = [
        {"id": row["id"], "intents": json.loads(produced[row["id"]])["intents"], "usage": {}}
        for row in rows
        if row["id"] in produced
    ]
    record = {
        "timestamp": started,
        "task": TASK,
        "model": args.model,
        "endpoint": endpoint,
        "smoke": args.smoke,
        "source": rel(source),
        "source_sha256": sha256(source.read_bytes()).hexdigest(),
        "seed": args.seed,
        "prompt_sha256": {TASK: prompts.prompt_sha256(TASK), "T1v2": prompts.prompt_sha256("T1v2")},
        "git": evaluator.git_state(),
        "drift": drift(rows, settled + unusable),
        "accounting": {
            rel(source): {
                "source_rows": in_file,
                "drawn": len(rows),
                "skipped_frozen": skipped,
                "labelled": len(produced),
                "unusable": len(unusable),
                "full_pass": len(rows) + skipped == in_file,
            }
        },
        "cost": {
            "requests": len(pending),
            "usd": budget.run_spend,
            "usd_per_row": budget.run_spend / scored if scored else 0.0,
            "phase_spend_usd": budget.phase_spend,
            "cap_usd": cap,
        },
        # measured elsewhere, at 758 rows each: results/spend_3b.json, same prompt shape
        "alternatives": {"anthropic/claude-haiku-4.5": 0.000678, "google/gemma-4-31b-it": 0.000045},
        "rows_out": rel(args.rows_out),
        "note": (
            "Intents only; every other column is byte-identical to the source line. A staged v2"
            " copy beside its source, not a gold file: nothing reads it as gold until the"
            " calibration decides it."
        ),
    }
    if not args.smoke:
        ledger["runs"].append(
            {
                "model": args.model,
                "timestamp": started,
                "usd": budget.run_spend,
                "requests": len(pending),
                "note": (
                    f"{args.phase}: {len(pending)} {args.source} rows re-labelled under taxonomy v2"
                ),
            }
        )
        write_json(phase["ledger"], ledger)
    append_record(args.record, record)
    report(record)
    print(f"\nwrote {rel(args.rows_out)} ({len(ordered)} rows) and {rel(args.record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
