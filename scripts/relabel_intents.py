#!/usr/bin/env python3
"""Re-label the `intents` column under taxonomy v2 — one field, one budget (4.5d).

SPEC amendment 3.8 adds a sixth intent (`service`) and pre-registers an intents
re-label of the labelled data. This is the runner for it, and 4.5d spends it on a
probe: ~50 already-labelled TRAIN rows, to measure how far v2 moves the column and
what the full pass would cost.

What the design refuses rather than promises:

- **one column moves.** The request asks for `intents` and nothing else
  (`prompts.RELABEL_INTENTS_PROMPT`), and every produced row is proved by putting
  the old intents back: unless the line then matches its source byte for byte, the
  run stops. `sentiment`, `sarcasm` and `unclear` cannot move through a path that
  never carries them.
- **no test row is re-labelled here.** docs/PROMPT-4.5d.md: no test-row labelling
  at all. The four frozen test files are read for their ids and every drawn row is
  checked against them — a missing file is a defect, not a smaller forbidden set.
- **the ledger is anchored before the first request.** results/spend_45d.json is
  written before anything is spent, so a crash cannot leave the next run counting
  from a balance that already includes this one.
- **a row that comes back unreadable is counted, named and excluded** — never
  coerced to `[]`, which is the majority answer and would flatter the drift rate.

    python3.11 scripts/relabel_intents.py --smoke
    python3.11 scripts/relabel_intents.py --limit 50 --dry-run
    python3.11 scripts/relabel_intents.py --limit 50

Writes `results/relabel_probe_45d.json` (append-only) and the re-labelled rows
beside it; `data/frozen/` and `results/baselines.json` are never touched.
"""

import argparse
import json
import random
import sys
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
LEDGER = REPO_ROOT / "results" / "spend_45d.json"
RECORD = REPO_ROOT / "results" / "relabel_probe_45d.json"
ROWS_OUT = REPO_ROOT / "results" / "relabel_45d_probe_rows.jsonl"

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
CAP_USD = 2.00
DEFAULT_RUN_CAP_USD = 2.00
RETRY_ATTEMPTS = 6
# The prompt names comments_train + sarcasm_candidates + comments_test; the labelled
# comment rows that carry an intents column are more than that (see the report).
FULL_RELABEL_ROWS = {"prompt 4.5d (train + candidates + test)": 2746, "every labelled row": 3771}


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


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
    """A seeded sample, in a row order that does not depend on the file's."""
    paired = sorted(zip(rows, lines), key=lambda pair: pair[0]["id"])
    if limit and limit < len(paired):
        paired = sorted(random.Random(seed).sample(paired, limit), key=lambda p: p[0]["id"])
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
    """One pinned endpoint, one budget, retries — and nothing else it could spend on."""

    def __init__(self, key: str, model: str, tag: str, quantization: str | None, budget):
        self.key, self.model, self.tag, self.quantization = key, model, tag, quantization
        self.budget = budget

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

    def __call__(self, text: str) -> tuple[dict, dict]:
        self.calls += 1
        reply = '{"intents": ["service"]}' if "розіграш" in text else '{"intents": []}'
        if self.calls % 17 == 0:  # a reply that is not an answer, so the counter is exercised
            reply = "I cannot label this."
        usage = {"cost": 0.0001, "prompt_tokens": 500, "completion_tokens": 12}
        self.budget.add(float(usage["cost"]))
        return {"choices": [{"message": {"content": reply}}], "usage": usage}, usage


def ask_all(rows: list[dict], ask) -> list[dict]:
    """One outcome per row: the new labels, or the reason there are none."""
    outcomes = []
    for index, row in enumerate(rows, start=1):
        try:
            payload, usage = ask(row["text"])
            reply = payload["choices"][0]["message"]["content"] or ""
            outcome = {"id": row["id"], "intents": prompts.parse_reply(TASK, reply)["intents"]}
        except prompts.ParseError as err:
            outcome = {"id": row["id"], "intents": None, "unusable": f"parse: {err.reason}"}
        except (zero_shot.ApiError, OSError) as err:
            outcome = {"id": row["id"], "intents": None, "unusable": f"api: {err}"}
            usage = {}
        outcomes.append({**outcome, "usage": usage})
        print(
            f"  {index:>4}/{len(rows)} {row['id']:<24} {outcome.get('unusable') or outcome['intents']}"
        )
    return outcomes


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


def read_ledger(usage_now: float) -> dict:
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {
        "openrouter_total_usage_at_45d_start": usage_now,
        "note": (
            "lifetime OpenRouter usage read at the start of 4.5d, before the first request of"
            " this phase. Phase spend = total_usage now minus this, and the $2.00 cap of"
            " docs/PROMPT-4.5d.md is enforced against that difference. Delete or regenerate this"
            " file and the counter silently restarts at today's usage — the same footgun"
            " results/spend_3b.json carries. results/spend_3b.json is a different phase's anchor"
            " and is never written here."
        ),
        "cap_usd": CAP_USD,
        "runs": [],
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_record(path: Path, record: dict) -> None:
    history = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"runs": []}
    history["runs"].append(record)
    write_json(path, history)


def redrift(source: Path, produced: Path) -> tuple[list[dict], list[dict]]:
    """The drift of a finished run, recomputed from its own output. No requests.

    The split by ``unclear`` was added after the probe had already been paid for,
    and re-running would produce a *different* run (greedy is not deterministic
    across a provider's batches). Re-reading the rows it wrote is the same run.
    """
    by_id = {row["id"]: row for row in load(source)[0]}
    rows, outcomes = [], []
    for row in load(produced)[0]:
        if row["id"] not in by_id:
            raise SystemExit(f"{row['id']}: not in {rel(source)} — these rows came from elsewhere")
        rows.append(by_id[row["id"]])
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

    cost = record["cost"]
    if not cost["requests"]:
        print("\nre-derived from the rows a paid run wrote — no requests, no spend")
        return
    print(f"\ncost: ${cost['usd']:.4f} over {cost['requests']} requests")
    print(
        f"  per row ${cost['usd_per_row']:.6f} · phase spend ${cost['phase_spend_usd']:.4f}"
        f" of ${CAP_USD:.2f}"
    )
    print(f"{'projection':<44} {'rows':>6} {'this model':>12}   alternatives")
    for name, rows in FULL_RELABEL_ROWS.items():
        alt = "  ".join(
            f"{slug.split('/')[-1]} ${rows * usd:.2f}"
            for slug, usd in record["alternatives"].items()
        )
        print(f"  {name:<42} {rows:>6} {rows * cost['usd_per_row']:>11.2f}   {alt}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=sorted(SOURCES), default="comments_train")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--model", default=MODEL, choices=sorted(evaluator.ROWS))
    parser.add_argument("--max-run-usd", type=float, default=DEFAULT_RUN_CAP_USD)
    parser.add_argument("--smoke", action="store_true", help="fake client, no network, no spend")
    parser.add_argument("--dry-run", action="store_true", help="draw the sample, then stop")
    parser.add_argument("--rows-out", type=Path, default=None)
    parser.add_argument("--record", type=Path, default=None)
    parser.add_argument(
        "--from-rows",
        type=Path,
        help="re-derive the drift of a finished run from the rows it wrote, no requests",
    )
    args = parser.parse_args(argv)
    # A smoke run produces a record shaped exactly like a real one; the one thing it
    # must not do is land where the real one is read from.
    smoke_dir = REPO_ROOT / "results" / "smoke"
    args.rows_out = args.rows_out or (smoke_dir / ROWS_OUT.name if args.smoke else ROWS_OUT)
    args.record = args.record or (smoke_dir / RECORD.name if args.smoke else RECORD)

    source = SOURCES[args.source]
    if args.from_rows:
        rows, outcomes = redrift(source, args.from_rows)
        record = {
            "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
            "task": TASK,
            "model": args.model,
            "endpoint": {"tag": "—", "quantization": None},
            "smoke": False,
            "source": rel(source),
            "source_sha256": sha256(source.read_bytes()).hexdigest(),
            "seed": args.seed,
            "prompt_sha256": {},
            "git": evaluator.git_state(),
            "drift": drift(rows, outcomes),
            "cost": {"requests": 0, "usd": 0.0, "usd_per_row": 0.0, "phase_spend_usd": 0.0},
            "alternatives": {},
            "rows_out": rel(args.from_rows),
            "note": (
                f"RE-DERIVED from {rel(args.from_rows)}, the rows a paid run wrote — no model was"
                " called. The split by `unclear` was added after that run; re-running would have"
                " been a different run, not the same one measured twice."
            ),
        }
        append_record(args.record, record)
        report(record)
        return 0

    rows, lines = draw(*load(source), args.limit, args.seed)
    banned = forbidden_ids() & {row["id"] for row in rows}
    if banned:
        raise SystemExit(
            f"{len(banned)} drawn rows are in the frozen test files ({sorted(banned)[:3]}) —"
            " docs/PROMPT-4.5d.md forbids labelling a test row at all"
        )
    print(f"{rel(source)}: {len(rows)} rows drawn (seed {args.seed}), none in the test files")
    if args.dry_run:
        print("\n".join(f"  {row['id']:<24} {row['intents']}" for row in rows[:10]))
        return 0

    pinned = evaluator.ROWS[args.model]
    endpoint = {"tag": pinned["tag"], "quantization": pinned["quantization"]}
    if args.smoke:
        budget = zero_shot.Budget(CAP_USD, args.max_run_usd)
        ask = FakeAsker(budget)
        ledger = None
    else:
        key = evaluator.api_key()
        live = evaluator.verify_pin(key, args.model, pinned["tag"], pinned["quantization"])
        endpoint |= {"served_quantization": live.get("quantization"), "status": live.get("status")}
        usage_now = zero_shot.total_usage(key)
        ledger = read_ledger(usage_now)
        write_json(LEDGER, ledger)  # anchored before the first request, never after
        spent_before = usage_now - ledger["openrouter_total_usage_at_45d_start"]
        budget = zero_shot.Budget(CAP_USD, args.max_run_usd, spent_before=spent_before)
        print(f"ledger: 4.5d spend so far ${spent_before:.4f}, headroom ${budget.headroom():.4f}")
        ask = Asker(key, args.model, pinned["tag"], pinned["quantization"], budget)

    started = datetime.now(UTC).isoformat(timespec="seconds")
    outcomes = ask_all(rows, ask)
    produced = [
        relabelled(row, line, out["intents"])
        for row, line, out in zip(rows, lines, outcomes)
        if out["intents"] is not None
    ]
    args.rows_out.parent.mkdir(parents=True, exist_ok=True)
    args.rows_out.write_text("\n".join(produced) + "\n", encoding="utf-8")

    if ledger is not None:
        budget.reconcile(zero_shot.total_usage(key) - ledger["openrouter_total_usage_at_45d_start"])
    scored = sum(1 for out in outcomes if out["intents"] is not None)
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
        "drift": drift(rows, outcomes),
        "cost": {
            "requests": len(outcomes),
            "usd": budget.run_spend,
            "usd_per_row": budget.run_spend / scored if scored else 0.0,
            "phase_spend_usd": budget.phase_spend,
            "cap_usd": CAP_USD,
        },
        # measured elsewhere, at 758 rows each: results/spend_3b.json, same prompt shape
        "alternatives": {"anthropic/claude-haiku-4.5": 0.000678, "google/gemma-4-31b-it": 0.000045},
        "rows_out": rel(args.rows_out),
        "note": (
            "PROBE. Intents only; every other column is byte-identical to the source line."
            " The re-labelled rows are evidence for the 4.5d gate, not a gold file."
        ),
    }
    if not args.smoke:
        ledger["runs"].append(
            {
                "model": args.model,
                "timestamp": started,
                "usd": budget.run_spend,
                "requests": len(outcomes),
                "note": f"4.5d probe: {args.limit} {args.source} rows re-labelled under taxonomy v2",
            }
        )
        write_json(LEDGER, ledger)
    append_record(args.record, record)
    report(record)
    print(f"\nwrote {rel(args.rows_out)} ({scored} rows) and {rel(args.record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
