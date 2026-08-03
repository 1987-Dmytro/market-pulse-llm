#!/usr/bin/env python3
"""The v2.2 probe: 100 rows the sitting already ruled on, scored against the committed plan.

One attempt. `results/v22_probe_plan.json` names the sample, the reference labels and the two
thresholds, and it has to be **committed** before this script will start — a plan still sitting
in the working tree can be edited after the numbers come back, which is the whole failure
pre-registration exists to prevent. The check is `git`, not a comment.

What it refuses:

- **a plan that is untracked or modified.** Named above, and it stops before the ledger is even
  read, so nothing is anchored and nothing is spent.
- **a batch that is not the one the plan measured.** The plan pins the sha256 of the file it
  read the rows from, and the ids it lists have to all be in it.
- **spending past the cap.** $1.50 spans this phase and 4.5g3; the prior spend is read from
  that phase's own ledger and cross-checked against its run record, so the headroom enforced
  here is what 4.5g3 actually left rather than a number typed into this file.
- **its own scoring.** Every counter comes from `plan_v22_probe.score`, the function the
  committed plan applied to its baselines, so the probe and its reference row are read by one
  implementation.

    PYTHONPATH=src python3 scripts/run_v22_probe.py --smoke     # fake client, no network
    PYTHONPATH=src python3 scripts/run_v22_probe.py --dry-run   # scope, estimate, headroom
    PYTHONPATH=src python3 scripts/run_v22_probe.py

Writes `results/v22_probe_results.json` and updates `results/spend_45g4.json`.
"""

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import eval_zero_shot as evaluator  # noqa: E402
import plan_v22_probe as planner  # noqa: E402
import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from recheck_with_captions import (  # noqa: E402
    FIELDS,
    Asker,
    FakeAsker,
    answered,
    ask_all,
    states,
    with_context,
)
from market_pulse import parents, prompts, zero_shot  # noqa: E402

PLAN = REPO_ROOT / "results" / "v22_probe_plan.json"
POSTS = REPO_ROOT / "data" / "raw" / "posts"
CAPTIONS = REPO_ROOT / "data" / "annotation" / "post_captions.jsonl"
GUIDELINE = REPO_ROOT / "docs" / "annotation" / "comments.md"
V21_BATCH = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g3.jsonl"
"""What the v2.1 re-run wrote. The plan's own source is the 4.5g2 batch — the labels the
sitting judged — so reading the comparison row off it would compare v2 with itself; the smoke
run did exactly that and reported a flawless 58/58 for a prompt that scores 20."""
OUTCOMES = REPO_ROOT / "results" / "v22_probe_rows.jsonl"
RECORD = REPO_ROOT / "results" / "v22_probe_results.json"

PHASE = "45g4"
CAP_USD = 1.50
LEDGER = REPO_ROOT / "results" / "spend_45g4.json"
"""This phase's own anchor, and the cap it shares with 4.5g3.

The anchor is new and this phase's alone — charging 4.5g4 to `results/spend_45g3.json` would
widen that closed phase's record by a run it never made. The **cap** is the one thing the two
share: $1.50 covers the 4.5g work, so what this phase may spend is the cap minus what 4.5g3
spent, read from that ledger below rather than written down here."""

PRIOR_LEDGER = REPO_ROOT / "results" / "spend_45g3.json"
PRIOR_RECORD = REPO_ROOT / "results" / "rerun_45g3.json"

TASK = "precheck_v2.2_with_post"
MODEL = "qwen/qwen3.6-27b"
ANNOTATOR = "llm-precheck-v2.2"
CONCURRENCY = 4
COMPLETION_TOKENS = 45

FAMILY = re.compile(r"\(([^()]*?)— pattern (P\d)[.,)]")
"""The guideline's own bracket naming a ruling's rows: `(@a:1, @b:2 — pattern P5.)`. Read from
`docs/annotation/comments.md` rather than listed here, because a family is whatever the law
says it is and a second copy of the ids would drift from it."""


def rel(path: Path) -> str:
    return relabel.rel(path)


def committed(path: Path, cwd: Path = REPO_ROOT) -> None:
    """Stop unless git has this file tracked and unmodified — the plan is a pre-registration."""
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path)],
        cwd=cwd,
        capture_output=True,
    )
    if tracked.returncode != 0:
        raise SystemExit(
            f"{rel(path)} is not tracked by git. The plan is the pre-registration: until it is"
            " committed, nothing stops it from being rewritten once the numbers are in."
        )
    dirty = subprocess.run(
        ["git", "diff", "HEAD", "--quiet", "--", str(path)], cwd=cwd, capture_output=True
    )
    if dirty.returncode != 0:
        raise SystemExit(
            f"{rel(path)} differs from HEAD. The committed plan is the one this run is read"
            " against — commit the change, or restore the file, before spending on it."
        )


def prior_spend(ledger: Path, record: Path) -> float:
    """What 4.5g3 spent under the shared cap — from its ledger, checked against its record.

    Two independent copies of one number, so a hand-edit to either shows up as a disagreement
    rather than as headroom this phase never had. Deliberately not `total_usage - anchor_45g3`:
    that difference grows with every request 4.5g4 makes.
    """
    runs = json.loads(ledger.read_text(encoding="utf-8"))["runs"]
    total = sum(run["usd"] for run in runs)
    recorded = json.loads(record.read_text(encoding="utf-8"))["runs"][-1]["cost"]["phase_spend_usd"]
    if abs(total - recorded) > 0.01:
        raise SystemExit(
            f"{rel(ledger)} sums to ${total:.4f} and {rel(record)} recorded ${recorded:.4f}."
            " Two readings of the prior phase's spend disagree, so the headroom under the shared"
            " cap is unknown. Stop and report."
        )
    return total


def families(guideline: Path) -> dict[str, list[str]]:
    """The P-numbered ruling families and their row ids, as the guideline itself names them."""
    text = guideline.read_text(encoding="utf-8")
    return {name: re.findall(r"@[A-Za-z_0-9]+:\d+", ids) for ids, name in FAMILY.findall(text)}


def moves(rows: list[dict], produced: dict[str, dict]) -> dict:
    """How many of the answered rows moved each field away from the pack."""
    per_field = Counter()
    for row in rows:
        got = produced.get(row["id"])
        if got is None:
            continue
        for field in FIELDS:
            if not planner.same(got, {field: row["reference"][field]}, fields=(field,)):
                per_field[field] += 1
    return dict(sorted(per_field.items()))


def as_labels(row: dict) -> dict:
    return {field: row[field] for field in FIELDS}


def main(argv: list[str] | None = None, asker=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=PLAN)
    parser.add_argument("--posts", type=Path, default=POSTS)
    parser.add_argument("--captions", type=Path, default=CAPTIONS)
    parser.add_argument("--guideline", type=Path, default=GUIDELINE)
    parser.add_argument("--v21-batch", type=Path, default=V21_BATCH)
    parser.add_argument("--outcomes", type=Path, default=OUTCOMES)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--prior-ledger", type=Path, default=PRIOR_LEDGER)
    parser.add_argument("--prior-record", type=Path, default=PRIOR_RECORD)
    parser.add_argument("--concurrency", type=int, default=CONCURRENCY)
    parser.add_argument("--smoke", action="store_true", help="fake client, no network, no spend")
    parser.add_argument("--dry-run", action="store_true", help="the scope and the estimate")
    parser.add_argument("--skip-git-check", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.smoke:
        smoke = REPO_ROOT / "results" / "smoke"
        args.record, args.outcomes = smoke / args.record.name, smoke / args.outcomes.name

    if not args.skip_git_check:
        committed(args.plan)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    if plan["task"] != TASK:
        raise SystemExit(f"{rel(args.plan)} plans {plan['task']} and this run asks {TASK}")

    batch = REPO_ROOT / plan["source"]["batch"]
    found = sha256(batch.read_bytes()).hexdigest()
    if found != plan["source"]["batch_sha256"]:
        raise SystemExit(
            f"{rel(batch)}: sha256 {found[:16]}…, the plan pins"
            f" {plan['source']['batch_sha256'][:16]}…. These are not the rows it sampled."
        )
    by_id = {row["id"]: row for row in relabel.load(batch)[0]}
    if missing := [row["id"] for row in plan["rows"] if row["id"] not in by_id]:
        raise SystemExit(f"{len(missing)} planned ids are not in {rel(batch)}: {missing[:3]}")
    posts = parents.load(args.posts)
    captions = parents.load_captions(args.captions)
    sample = with_context([by_id[row["id"]] for row in plan["rows"]], posts, captions)

    # what a previous invocation already bought, read BEFORE the estimate: an estimate over rows
    # already on disk prices a run nobody is about to make (4.5g3, deviation 9).
    already = answered(args.outcomes, {TASK: {row["id"] for row in sample}})
    pending = [row for row in sample if row["id"] not in already[TASK]]
    print(
        f"{rel(args.plan)}: {len(sample)} rows under {TASK}"
        f"\n  {plan['gate']['rule']}"
        f"\n  what their post says: {states(sample)}"
    )
    if already[TASK]:
        print(f"resume: {len(already[TASK])} rows already paid for, {len(pending)} to go")

    pinned = evaluator.ROWS[MODEL]
    endpoint = {"tag": pinned["tag"], "quantization": pinned["quantization"]}
    ledger, key, estimate = None, None, None
    prior = prior_spend(args.prior_ledger, args.prior_record)
    if asker is not None:
        ask, budget = asker, asker.budget
    elif args.smoke:
        budget = zero_shot.Budget(CAP_USD, CAP_USD, spent_before=prior)
        ask = FakeAsker(budget)
    else:
        key = evaluator.api_key()
        live = evaluator.verify_pin(key, MODEL, pinned["tag"], pinned["quantization"])
        endpoint |= {"served_quantization": live.get("quantization"), "status": live.get("status")}
        usage_now = zero_shot.total_usage(key)
        ledger = relabel.read_ledger(args.ledger, PHASE, CAP_USD, usage_now)
        relabel.write_json(args.ledger, ledger)  # anchored before the first request, never after
        spent_here = usage_now - ledger[relabel.anchor_key(PHASE)]
        budget = zero_shot.Budget(CAP_USD, CAP_USD, spent_before=prior + spent_here)
        estimate = zero_shot.estimate_cost(
            rows=[f"{row['parent']}\n{row['caption'] or ''}\n{row['text']}" for row in pending],
            prompt_chars=len(prompts.PROMPTS[TASK]),
            pricing=live["pricing"],
            completion_tokens=COMPLETION_TOKENS,
        )
        print(
            f"ledger: 4.5g3 spent ${prior:.4f} and {PHASE} ${spent_here:.4f} of the ${CAP_USD:.2f}"
            f" shared cap, headroom ${budget.headroom():.4f}"
            f"\nestimate: ${estimate['usd']:.4f} over {estimate['requests']} requests"
        )
        if estimate["usd"] > budget.headroom():
            raise SystemExit(
                f"the estimate ${estimate['usd']:.4f} is over the ${budget.headroom():.4f} left"
                f" under the ${CAP_USD:.2f} cap. Stop and report — the sample is pre-registered"
                " and trimming it to fit would score a hundred nobody registered."
            )
        ask = Asker(key, MODEL, pinned["tag"], pinned["quantization"], budget)
    if args.dry_run:
        print("--dry-run: nothing spent")
        return 0

    started = datetime.now(UTC).isoformat(timespec="seconds")
    args.outcomes.parent.mkdir(parents=True, exist_ok=True)
    handle = args.outcomes.open("a" if already[TASK] else "w", encoding="utf-8")
    done = 0

    def persist(outcome: dict) -> None:
        nonlocal done
        done += 1
        if outcome["labels"] is not None:
            handle.write(json.dumps({"task": TASK, **outcome}, ensure_ascii=False) + "\n")
            handle.flush()  # on disk before the next row is asked for
        if outcome["labels"] is None or done % 25 == 0:
            print(f"  {done:>4} {outcome['id']:<24} {outcome.get('unusable') or ''}")

    try:
        outcomes = ask_all(TASK, pending, ask, args.concurrency, dict, persist)
    finally:
        handle.close()
    outcomes += [{"id": row_id, "labels": labels} for row_id, labels in already[TASK].items()]
    if ledger is not None:
        budget.reconcile(zero_shot.total_usage(key) - ledger[relabel.anchor_key(PHASE)] + prior)

    produced = {out["id"]: out["labels"] for out in outcomes if out["labels"] is not None}
    unusable = [out for out in outcomes if out["labels"] is None]
    counts = planner.score(plan["rows"], produced)
    gate = planner.verdict(counts)
    reference = {row["id"]: row["reference"] for row in plan["rows"]}
    was = {row["id"]: row for row in relabel.load(args.v21_batch)[0]}
    v21 = {row_id: as_labels(was[row_id]) for row_id in reference if row_id in was}
    family = families(args.guideline)
    record = {
        "timestamp": started,
        "phase": PHASE,
        "task": TASK,
        "model": MODEL,
        "endpoint": endpoint,
        "smoke": bool(args.smoke),
        "annotator": ANNOTATOR,
        "plan": rel(args.plan),
        "plan_sha256": sha256(args.plan.read_bytes()).hexdigest(),
        "prompt_sha256": {
            task: prompts.prompt_sha256(task)
            for task in (TASK, "T1v2.2", "precheck_v2.1_with_post", "precheck_v2_with_post")
        },
        "gate": {
            "verdict": gate,
            "rule": plan["gate"]["rule"],
            "attempts": plan["gate"]["attempts"],
            "preserved": f"{counts['preserved']['kept']}/{counts['preserved']['n']}",
            "fixed": f"{counts['fixed']['landed']}/{counts['fixed']['n']}",
            "thresholds": {"preserved": plan["gate"]["preserved"], "fixed": plan["gate"]["fixed"]},
        },
        "counts": counts,
        "in_sample": plan["in_sample"],
        "in_sample_caveat": plan["in_sample_caveat"],
        "compared_with": {
            **plan["reference_runs"],
            "v2.1 recomputed here": planner.score(plan["rows"], v21),
        },
        "per_field_moved_from_the_pack": {
            "v2.2": moves(plan["rows"], produced),
            "v2.1": moves(plan["rows"], v21),
            "of": len(produced),
        },
        "families": {
            name: [
                {
                    "id": row_id,
                    "verdict": next(
                        (r["verdict"] for r in plan["rows"] if r["id"] == row_id), "not sampled"
                    ),
                    "pack": reference.get(row_id),
                    "v2.1": v21.get(row_id),
                    "v2.2": produced.get(row_id),
                }
                for row_id in ids
            ]
            for name, ids in family.items()
            if name in ("P5", "P6")
        },
        "rows": {
            "asked": len(sample),
            "answered": len(produced),
            "unusable": unusable,
            "context_states": states(sample),
        },
        "estimate_usd": estimate and estimate["usd"],
        "cost": {
            "requests": len(pending),
            "rows_from_an_earlier_run": len(already[TASK]),
            "usd": budget.run_spend,
            "prior_phase_usd": prior,
            "phase_spend_usd": budget.run_spend + (budget.spent_before - prior),
            "against_shared_cap_usd": budget.phase_spend,
            "cap_usd": CAP_USD,
        },
        "note": (
            "In-sample by construction and pre-registered because of it: the plan was committed"
            " before the first request and this run is scored by the function that plan applied"
            " to its own baselines. Nothing is written to a batch file — the probe measures a"
            " prompt, it does not re-label a corpus."
        ),
        "git": git_state(args.record),
    }
    if ledger is not None:
        ledger["runs"].append(
            {
                "model": MODEL,
                "timestamp": started,
                "usd": budget.run_spend,
                "requests": len(pending),
                "note": f"{PHASE}: {len(pending)} pre-registered probe rows under {TASK}",
            }
        )
        relabel.write_json(args.ledger, ledger)
    relabel.append_record(args.record, record)

    print(
        f"\n  {'preserved':<12} {counts['preserved']['kept']:>3}/{counts['preserved']['n']}"
        f"   PASS at {plan['gate']['preserved']['pass_at']}, KILL below"
        f" {plan['gate']['preserved']['kill_below']}"
        f"\n  {'fixed':<12} {counts['fixed']['landed']:>3}/{counts['fixed']['n']}"
        f"   PASS at {plan['gate']['fixed']['pass_at']}, KILL below"
        f" {plan['gate']['fixed']['kill_below']}"
        f"\n  ==> {gate}"
    )
    for name, block in record["compared_with"].items():
        print(
            f"    {name:<52} preserved {block['preserved']['kept']:>2}/{block['preserved']['n']}"
            f" · fixed {block['fixed']['landed']:>2}/{block['fixed']['n']}"
        )
    print(
        f"\n  moved from the pack, per field: {record['per_field_moved_from_the_pack']['v2.2']}"
        f"\n  (v2.1 on the same rows:        {record['per_field_moved_from_the_pack']['v2.1']})"
        f"\n  ungated 13: {len(counts['ungated_moved'])} moved, {len(counts['ungated_unmoved'])}"
        " unmoved"
        f"\n  named-field-only: {len(counts['named_field_only'])}"
        f"\ncost ${budget.run_spend:.4f}, phase total against the ${CAP_USD:.2f} shared cap:"
        f" ${budget.phase_spend:.4f}"
        f"\nwrote {rel(args.record)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
