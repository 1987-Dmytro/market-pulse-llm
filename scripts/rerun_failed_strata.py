#!/usr/bin/env python3
"""The strata that failed the sitting, re-labelled under the v2.1 rulings (4.5g3).

A stratum below the bar sends back its **whole** population, not the hundred that were judged
— that is what `results/sitting_45g2_manifest.json` registered before the pack went out. All
three failed, so this asks the model about all 1,912 rows again, with one thing changed: the
prompt now carries the boundary rulings the sitting produced (`precheck_v2.1_with_post`,
registered beside the revision that labelled them the first time).

Same model, same pinned endpoint, same parent posts and the same surrogates for the posts with
no text of their own. A difference in the returned labels is the rulings and nothing else.

What it refuses:

- **choosing its own scope.** Which strata failed comes from `results/sitting_45g_gates.json`
  and from nowhere else; a stratum that passed is copied line for line, bytes included.
- **overwriting what a manifest pins.** The 4.5g2 batch is read-only here — the sealed sitting
  still verifies against it — and this run writes a new file beside it.
- **spending past the cap.** `results/spend_45g3.json` is anchored before the first request and
  an estimate over the remaining headroom stops the run instead of trimming the pool.
- **a reply that could not be read.** Counted, named, excluded; never coerced to a label.

    python3.11 scripts/rerun_failed_strata.py --smoke     # fake client, no network, no spend
    python3.11 scripts/rerun_failed_strata.py --dry-run   # the scope and the cost estimate
    python3.11 scripts/rerun_failed_strata.py

Writes `data/annotation/uplabel_precheck_45g3.jsonl` and `results/rerun_45g3.json`.
"""

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_sitting_pack as builder  # noqa: E402
import eval_zero_shot as evaluator  # noqa: E402
import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from recheck_with_captions import (  # noqa: E402
    FIELDS,
    Asker,
    FakeAsker,
    answered,
    ask_all,
    field_diff,
    states,
    with_context,
)
from market_pulse import annotation, parents, prompts, zero_shot  # noqa: E402

POSTS = REPO_ROOT / "data" / "raw" / "posts"
CAPTIONS = REPO_ROOT / "data" / "annotation" / "post_captions.jsonl"
BATCH_IN = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g2.jsonl"
BATCH_OUT = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g3.jsonl"
GATES = REPO_ROOT / "results" / "sitting_45g_gates.json"
MANIFEST = REPO_ROOT / "results" / "sitting_45g2_manifest.json"
OUTCOMES = REPO_ROOT / "results" / "rerun_45g3_rows.jsonl"
RECORD = REPO_ROOT / "results" / "rerun_45g3.json"

PHASE = "45g3"
CAP_USD = 1.50
LEDGER = REPO_ROOT / "results" / "spend_45g3.json"
"""This phase's own anchor, cap and ledger — declared here and never imported from an earlier
phase's script. `results/spend_45g.json` and the rest are closed anchors: charging this run to
one of them would silently widen that phase's cap by this phase's spend and leave both records
describing a run that never happened."""

TASK = "precheck_v2.1_with_post"
MODEL = "qwen/qwen3.6-27b"
ANNOTATOR = "llm-precheck-v2.1"
CONCURRENCY = 4
COMPLETION_TOKENS = 45


def rel(path: Path) -> str:
    return relabel.rel(path)


def scope(gates: Path, manifest: Path, rows: list[dict]) -> tuple[list[dict], dict]:
    """The rows of every failed stratum, and the strata table this run is working from."""
    record = json.loads(gates.read_text(encoding="utf-8"))
    if record["manifest"] != rel(manifest):
        raise SystemExit(
            f"{rel(gates)} reads {record['manifest']} and this run was given {rel(manifest)}"
            " — two sittings, and a stratum's verdict does not transfer between them."
        )
    if not record["failed"]:
        raise SystemExit(
            "every stratum passed the bar, so nothing goes back for a second round. This script"
            " re-labels what a gate refused; with nothing refused there is nothing to re-label."
        )
    pools = builder.strata(rows)
    if unknown := sorted(set(record["failed"]) - set(pools)):
        raise SystemExit(f"{unknown}: the gate record names strata this batch does not derive")
    sealed = json.loads(manifest.read_text(encoding="utf-8"))["precheck"]["strata"]
    for name in record["failed"]:
        if len(pools[name]) != sealed[name]["population"]:
            raise SystemExit(
                f"{name} derives as {len(pools[name])} rows and the sealed manifest recorded"
                f" {sealed[name]['population']}. The batch this gate judged has moved, so"
                " 'the whole population' means a different set of rows than the one refused."
            )
    return [row for name in record["failed"] for row in pools[name]], record


def rewritten(row: dict, line: str, labels: dict) -> str:
    """The four labels and the annotator that names the revision — proved by putting them back.

    `recheck_with_captions.rewritten` restores exactly the four label fields, and this run moves
    a fifth: every row it touches was labelled under a different prompt from the one its file
    still claimed, and a batch that cannot say which of its rows came from which revision is a
    file whose provenance lives only in a record beside it.
    """
    changes = {**labels, "annotator": ANNOTATOR}
    produced = json.dumps({**row, **changes}, ensure_ascii=False)
    back = {**json.loads(produced), **{field: row[field] for field in changes}}
    if json.dumps(back, ensure_ascii=False) != line:
        raise SystemExit(
            f"{row['id']}: restoring the 4.5g2 labels does not reproduce the batch line byte for"
            " byte, so this run changed more than the five fields it names. Stop and report."
        )
    return produced


def in_sample(gates: dict, before: dict, after: dict) -> dict:
    """How the re-run moved the 300 rows the sitting judged — a signal, never the gate.

    In-sample by construction: those verdicts are what the v2.1 rulings were written from, so a
    row moving here is the prompt doing what it was told and not evidence that it generalises.
    The fresh hundred in the wave-2 pack is what decides.
    """
    verdicts = {row["id"]: row["verdict"] for row in gates["rows"]}
    moved = Counter()
    seen = Counter()
    for row_id, verdict in verdicts.items():
        if row_id not in after:
            continue
        seen[verdict] += 1
        old, new = before[row_id], after[row_id]
        changed = any(
            sorted(old[field]) != sorted(new[field])
            if field == "intents"
            else old[field] != new[field]
            for field in FIELDS
        )
        moved[verdict] += changed
    return {
        "judged_rows_re_asked": dict(seen),
        "moved_a_field": dict(moved),
        "note": (
            "In-sample: the v2.1 rulings were distilled from these verdicts. Movement on the"
            " `incorrect` rows is the prompt following its instructions; movement on the"
            " `correct` rows is the cost of that, and both are read against the fresh hundred."
        ),
    }


def main(argv: list[str] | None = None, asker=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-in", type=Path, default=BATCH_IN)
    parser.add_argument("--batch-out", type=Path, default=BATCH_OUT)
    parser.add_argument("--gates", type=Path, default=GATES)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--captions", type=Path, default=CAPTIONS)
    parser.add_argument("--posts", type=Path, default=POSTS)
    parser.add_argument("--outcomes", type=Path, default=OUTCOMES)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--concurrency", type=int, default=CONCURRENCY)
    parser.add_argument("--limit", type=int, default=0, help="first N rows of the scope, a probe")
    parser.add_argument("--smoke", action="store_true", help="fake client, no network, no spend")
    parser.add_argument("--dry-run", action="store_true", help="the scope and the estimate")
    args = parser.parse_args(argv)
    if args.smoke:
        smoke = REPO_ROOT / "results" / "smoke"
        args.record, args.batch_out = smoke / args.record.name, smoke / args.batch_out.name
        args.outcomes = smoke / args.outcomes.name

    batch_rows, batch_lines = relabel.load(args.batch_in)
    failed_rows, gates = scope(args.gates, args.manifest, batch_rows)
    posts = parents.load(args.posts)
    captions = parents.load_captions(args.captions)
    reask = with_context(failed_rows, posts, captions)
    if args.limit:
        reask = reask[: args.limit]
    print(
        f"{rel(args.gates)}: failed {gates['failed']}"
        f"\n{len(reask)} rows go back of {len(batch_rows)} in the batch, under {TASK}"
        f"\n  what their post says: {states(reask)}"
    )

    pinned = evaluator.ROWS[MODEL]
    endpoint = {"tag": pinned["tag"], "quantization": pinned["quantization"]}
    ledger, key, estimate = None, None, None
    if asker is not None:
        ask, budget = asker, asker.budget
    elif args.smoke:
        budget = zero_shot.Budget(CAP_USD, CAP_USD)
        ask = FakeAsker(budget)
    else:
        key = evaluator.api_key()
        live = evaluator.verify_pin(key, MODEL, pinned["tag"], pinned["quantization"])
        endpoint |= {"served_quantization": live.get("quantization"), "status": live.get("status")}
        usage_now = zero_shot.total_usage(key)
        ledger = relabel.read_ledger(args.ledger, PHASE, CAP_USD, usage_now)
        relabel.write_json(args.ledger, ledger)  # anchored before the first request, never after
        spent_before = usage_now - ledger[relabel.anchor_key(PHASE)]
        budget = zero_shot.Budget(CAP_USD, CAP_USD, spent_before=spent_before)
        estimate = zero_shot.estimate_cost(
            rows=[f"{row['parent']}\n{row['caption'] or ''}\n{row['text']}" for row in reask],
            prompt_chars=len(prompts.PROMPTS[TASK]),
            pricing=live["pricing"],
            completion_tokens=COMPLETION_TOKENS,
        )
        print(
            f"ledger: {PHASE} spent ${spent_before:.4f}, headroom ${budget.headroom():.4f}"
            f"\nestimate: ${estimate['usd']:.4f} over {estimate['requests']} requests"
        )
        if estimate["usd"] > budget.headroom():
            raise SystemExit(
                f"the estimate ${estimate['usd']:.4f} is over the ${budget.headroom():.4f} left"
                f" under the ${CAP_USD:.2f} {PHASE} cap. Stop and report — do not trim the scope"
                " to fit, because a second round of part of a stratum re-labels a different set."
            )
        ask = Asker(key, MODEL, pinned["tag"], pinned["quantization"], budget)
    if args.dry_run:
        print("--dry-run: nothing spent")
        return 0

    started = datetime.now(UTC).isoformat(timespec="seconds")
    already = answered(args.outcomes, {TASK: {row["id"] for row in reask}})
    if already[TASK]:
        print(f"resume: {len(already[TASK])} rows already paid for")
    args.outcomes.parent.mkdir(parents=True, exist_ok=True)
    handle = args.outcomes.open("a" if already[TASK] else "w", encoding="utf-8")
    done = 0

    def persist(outcome: dict) -> None:
        nonlocal done
        done += 1
        if outcome["labels"] is not None:
            handle.write(json.dumps({"task": TASK, **outcome}, ensure_ascii=False) + "\n")
            handle.flush()  # on disk before the next row is asked for
        if outcome["labels"] is None or done % 100 == 0:
            print(f"  {done:>5} {outcome['id']:<24} {outcome.get('unusable') or ''}")

    pending = [row for row in reask if row["id"] not in already[TASK]]
    try:
        outcomes = ask_all(TASK, pending, ask, args.concurrency, dict, persist)
    finally:
        handle.close()
    outcomes += [{"id": row_id, "labels": labels} for row_id, labels in already[TASK].items()]
    if ledger is not None:
        budget.reconcile(zero_shot.total_usage(key) - ledger[relabel.anchor_key(PHASE)])

    at = {row["id"]: position for position, row in enumerate(batch_rows)}
    produced = {out["id"]: out["labels"] for out in outcomes if out["labels"] is not None}
    replacement = {}
    for row_id, labels in produced.items():
        row, line = batch_rows[at[row_id]], batch_lines[at[row_id]]
        if bad := annotation.check_labels({**row, **labels, "annotator": ANNOTATOR}, "comments"):
            raise SystemExit(f"{row_id}: the re-run produced a row the checker refuses ({bad})")
        replacement[row_id] = rewritten(row, line, labels)
    lines = [
        replacement.get(row["id"], line) for row, line in zip(batch_rows, batch_lines, strict=True)
    ]
    args.batch_out.parent.mkdir(parents=True, exist_ok=True)
    args.batch_out.write_text("".join(line + "\n" for line in lines), encoding="utf-8")

    before = {row["id"]: {field: row[field] for field in FIELDS} for row in batch_rows}
    diff = field_diff(before, produced)
    unusable = [out for out in outcomes if out["labels"] is None]
    record = {
        "timestamp": started,
        "task": TASK,
        "model": MODEL,
        "endpoint": endpoint,
        "smoke": bool(args.smoke),
        "annotator": ANNOTATOR,
        "prompt_sha256": {
            task: prompts.prompt_sha256(task) for task in (TASK, "T1v2.1", "precheck_v2_with_post")
        },
        "gates": {
            "record": rel(args.gates),
            "bar": gates["bar"],
            "failed": gates["failed"],
            "passed": gates["passed"],
            "strata": {name: block["agreement"] for name, block in gates["strata"].items()},
        },
        "scope": {
            "source": rel(args.batch_in),
            "source_sha256": sha256(args.batch_in.read_bytes()).hexdigest(),
            "batch": rel(args.batch_out),
            "batch_sha256": sha256(args.batch_out.read_bytes()).hexdigest(),
            "rows_in_batch": len(batch_rows),
            "re_asked": len(reask),
            "relabelled": len(produced),
            "copied_unchanged": len(batch_rows) - len(replacement),
            "context_states": states(reask),
            "unusable": unusable,
        },
        "diff": diff,
        "in_sample": in_sample(gates, before, produced),
        "estimate_usd": estimate and estimate["usd"],
        "cost": {
            "requests": len(pending),
            "rows_from_an_earlier_run": len(already[TASK]),
            "usd": budget.run_spend,
            "phase_spend_usd": budget.phase_spend,
            "cap_usd": CAP_USD,
        },
        "git": git_state(args.record),
        "note": (
            "The second round the sitting's three FAIL verdicts require. Still a PRECHECK:"
            " every row carries an `llm-precheck-v2.1` annotator and nothing merges until a"
            " fresh sealed hundred is judged. The 4.5g2 batch is read-only here so that"
            " results/sitting_45g2_manifest.json still pins the bytes it sealed."
        ),
    }
    if ledger is not None:
        ledger["runs"].append(
            {
                "model": MODEL,
                "timestamp": started,
                "usd": budget.run_spend,
                "requests": len(pending),
                "note": f"{PHASE}: {len(pending)} rows of the failed strata re-labelled under v2.1",
            }
        )
        relabel.write_json(args.ledger, ledger)
    relabel.append_record(args.record, record)

    print(
        f"\n{len(produced)} of {len(reask)} rows re-labelled · {len(unusable)} unusable"
        f"\n  {diff['changed_any_field']} changed a field ({diff['changed_rate']:.0%})"
        f" · per field {diff['per_field']}"
        f"\n  intents gained {diff['intents_gained']} · lost {diff['intents_lost']}"
        f"\n  in-sample on the 300 judged: {record['in_sample']['moved_a_field']}"
        f" of {record['in_sample']['judged_rows_re_asked']}"
        f"\ncost ${budget.run_spend:.4f} of the ${CAP_USD:.2f} {PHASE} cap"
        f"\nwrote {rel(args.batch_out)} and {rel(args.record)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
