#!/usr/bin/env python3
"""The v2ctx probe: the same hundred rows, asked with two facts beside the post (4.5g6, Task 5).

One attempt. `results/v2ctx_probe_plan.json` names the sample, the reference labels, which row
renders which context line and the two thresholds, and it has to be **committed** before this
script will start — the check is `git`, not a comment.

What it refuses:

- **a plan that is untracked or modified**, before the ledger is read, so nothing is anchored.
- **a batch that is not the one the plan measured**, by sha256, and a planned id missing from it.
- **rendering a line the plan did not pre-register.** The flags travel from the plan to
  `prompts.build_messages`; nothing here re-derives a feature from the raw store mid-run.
- **spending past the shared cap.** $1.50 spans 4.5g3 through this phase. What the closed
  phases spent is read from their own ledgers and cross-checked against their run records, and
  the total is held to the figure `docs/PROMPT-4.5g6.md` states to the cent.
- **its own scoring.** Every counter comes from `plan_v2ctx_probe`, the module the committed
  plan applied to its own baselines, so the probe and its four reference columns are read by one
  implementation.

    PYTHONPATH=src python3 scripts/run_v2ctx_probe.py --smoke     # fake client, no network
    PYTHONPATH=src python3 scripts/run_v2ctx_probe.py --dry-run   # scope, estimate, headroom
    PYTHONPATH=src python3 scripts/run_v2ctx_probe.py

Writes `results/v2ctx_probe_results.json`, `results/v2ctx_probe_rows.jsonl` and updates
`results/spend_45g6.json`.
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import eval_zero_shot as evaluator  # noqa: E402
import plan_v2ctx_probe as planner  # noqa: E402
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
from run_v22_probe import committed, moves, prior_spend  # noqa: E402

from market_pulse import parents, prompts, zero_shot  # noqa: E402

PLAN = REPO_ROOT / "results" / "v2ctx_probe_plan.json"
POSTS = REPO_ROOT / "data" / "raw" / "posts"
CAPTIONS = REPO_ROOT / "data" / "annotation" / "post_captions.jsonl"
V21_BATCH = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g3.jsonl"
V22_ROWS = REPO_ROOT / "results" / "v22_probe_rows.jsonl"
OUTCOMES = REPO_ROOT / "results" / "v2ctx_probe_rows.jsonl"
RECORD = REPO_ROOT / "results" / "v2ctx_probe_results.json"

PHASE = "45g6"
CAP_USD = 1.50
LEDGER = REPO_ROOT / "results" / "spend_45g6.json"

PRIOR_LEDGERS = (
    (REPO_ROOT / "results" / "spend_45g3.json", REPO_ROOT / "results" / "rerun_45g3.json"),
    (REPO_ROOT / "results" / "spend_45g4.json", REPO_ROOT / "results" / "v22_probe_results.json"),
)
ZERO_LEDGER = REPO_ROOT / "results" / "spend_45g5.json"
PRIOR_EXPECTED = 0.7794
"""What `docs/PROMPT-4.5g6.md` says the closed phases spent under the shared cap.

Three readings have to agree before a request goes out: each phase's ledger against its own run
record, and their sum against this figure. A number the briefing states in passing is a check
owed, not a comment — and here it is the one thing that says how much headroom is real."""

TASK = "precheck_v2ctx_with_post"
MODEL = "qwen/qwen3.6-27b"
ANNOTATOR = "llm-precheck-v2ctx"
CONCURRENCY = 4
COMPLETION_TOKENS = 45


def rel(path: Path) -> str:
    return relabel.rel(path)


def prior_total(pairs=PRIOR_LEDGERS, zero: Path = ZERO_LEDGER) -> float:
    """What the closed phases spent under the shared cap, from their ledgers, cross-checked.

    The $0.00 phase is read too rather than assumed: a ledger with a run in it would mean 4.5g5
    spent money it pre-registered itself never to spend, and the headroom here would be wrong by
    exactly that amount.
    """
    spent = sum(prior_spend(ledger, record) for ledger, record in pairs)
    zero_runs = json.loads(zero.read_text(encoding="utf-8"))["runs"]
    if zero_runs:
        raise SystemExit(
            f"{rel(zero)} holds {len(zero_runs)} runs, and 4.5g5 was pre-registered at $0.00."
            " Two phases disagree about what has been spent — stop and report."
        )
    if abs(spent - PRIOR_EXPECTED) > 0.01:
        raise SystemExit(
            f"the closed phases sum to ${spent:.4f} and docs/PROMPT-4.5g6.md states"
            f" ${PRIOR_EXPECTED:.4f}. The headroom under the ${CAP_USD:.2f} shared cap is"
            " unknown — stop and report."
        )
    return spent


def as_labels(row: dict) -> dict:
    return {field: row[field] for field in FIELDS}


def rendered_context(rows: list[dict]) -> dict:
    """How many of the asked rows carried each line — counted off what is about to be sent."""
    return {
        "reply": sum(1 for row in rows if row["reply"]),
        "sender": sum(1 for row in rows if row["sender"]),
        "both": sum(1 for row in rows if row["reply"] and row["sender"]),
        "neither": sum(1 for row in rows if not row["reply"] and not row["sender"]),
        "lines": sum(len(prompts.context_lines(row["reply"], row["sender"])) for row in rows),
    }


def main(argv: list[str] | None = None, asker=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=PLAN)
    parser.add_argument("--posts", type=Path, default=POSTS)
    parser.add_argument("--captions", type=Path, default=CAPTIONS)
    parser.add_argument("--v21-batch", type=Path, default=V21_BATCH)
    parser.add_argument("--v22-rows", type=Path, default=V22_ROWS)
    parser.add_argument("--outcomes", type=Path, default=OUTCOMES)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
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
    if plan["rendering"]["templates"] != list(prompts.CONTEXT_TEMPLATES):
        raise SystemExit(
            f"{rel(args.plan)} pre-registered context lines this checkout does not render."
            " The revision is the rendering, so a template edit is an instrument change."
        )
    by_id = {row["id"]: row for row in relabel.load(batch)[0]}
    if missing := [row["id"] for row in plan["rows"] if row["id"] not in by_id]:
        raise SystemExit(f"{len(missing)} planned ids are not in {rel(batch)}: {missing[:3]}")
    posts = parents.load(args.posts)
    captions = parents.load_captions(args.captions)
    # the flags come from the committed plan and are never re-derived here: what renders was
    # pre-registered, and a mid-run derivation could disagree with it silently
    sample = with_context(
        [
            {**by_id[row["id"]], "reply": row["reply"], "sender": row["sender"]}
            for row in plan["rows"]
        ],
        posts,
        captions,
    )
    context = rendered_context(sample)

    already = answered(args.outcomes, {TASK: {row["id"] for row in sample}})
    pending = [row for row in sample if row["id"] not in already[TASK]]
    print(
        f"{rel(args.plan)}: {len(sample)} rows under {TASK}"
        f"\n  {plan['gate']['rule']}"
        f"\n  what their post says: {states(sample)}"
        f"\n  context rendered: {context}"
    )
    if already[TASK]:
        print(f"resume: {len(already[TASK])} rows already paid for, {len(pending)} to go")

    pinned = evaluator.ROWS[MODEL]
    endpoint = {"tag": pinned["tag"], "quantization": pinned["quantization"]}
    ledger, key, estimate = None, None, None
    prior = prior_total()
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
            rows=[
                "\n".join(
                    [
                        row["parent"],
                        row["caption"] or "",
                        *prompts.context_lines(row["reply"], row["sender"]),
                        row["text"],
                    ]
                )
                for row in pending
            ],
            prompt_chars=len(prompts.PROMPTS[TASK]),
            pricing=live["pricing"],
            completion_tokens=COMPLETION_TOKENS,
        )
        print(
            f"ledger: the closed phases spent ${prior:.4f} and {PHASE} ${spent_here:.4f} of the"
            f" ${CAP_USD:.2f} shared cap, headroom ${budget.headroom():.4f}"
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
    counts = planner.counters(plan["rows"], produced)
    gate = planner.verdict(counts, plan["gate"])
    was = {row["id"]: row for row in relabel.load(args.v21_batch)[0]}
    reference = {row["id"]: row["reference"] for row in plan["rows"]}
    v21 = {row_id: as_labels(was[row_id]) for row_id in reference if row_id in was}
    v22 = {
        json.loads(line)["id"]: json.loads(line)["labels"]
        for line in args.v22_rows.read_text(encoding="utf-8").splitlines()
    }
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
            for task in (TASK, "precheck_v2_with_post", "precheck_v2.2_with_post")
        },
        "rendering": {
            **{k: v for k, v in plan["rendering"].items() if k != "templates"},
            "asked_with": context,
            "note": (
                "The prompt hash of this run equals precheck_v2_with_post's, by construction."
                " What identifies it is templates_sha256 above and the per-row flags in the"
                " committed plan; `asked_with` is those flags counted off the rows actually sent."
            ),
        },
        "gate": {
            "verdict": gate,
            "rule": plan["gate"]["rule"],
            "attempts": plan["gate"]["attempts"],
            "preserved": f"{counts['preserved']['kept']}/{counts['preserved']['n']}",
            "feature_fixed": f"{counts['feature_named']['landed']}/{counts['feature_named']['n']}",
            "thresholds": {
                "preserved": plan["gate"]["preserved"],
                "feature_fixed": plan["gate"]["feature_fixed"],
            },
        },
        "counts": counts,
        "per_family": planner.per_family(plan["rows"], produced),
        "in_sample": plan["in_sample"],
        "in_sample_caveat": plan["in_sample_caveat"],
        "compared_with": {
            **plan["reference_runs"],
            "v2.1 recomputed here": planner.counters(plan["rows"], v21),
            "v2.2 recomputed here": planner.counters(plan["rows"], v22),
        },
        "reference_points": plan["reference_points"],
        "per_family_of_the_priors": {
            "v2.2": planner.per_family(plan["rows"], v22),
            "v2.1": planner.per_family(plan["rows"], v21),
        },
        "per_field_moved_from_the_reference": {
            "v2ctx": moves(plan["rows"], produced),
            "v2.2": moves(plan["rows"], v22),
            "v2.1": moves(plan["rows"], v21),
            "of": len(produced),
        },
        "rows": {
            "asked": len(sample),
            "answered": len(produced),
            "unusable": unusable,
            "context_states": states(sample),
            "outcomes": rel(args.outcomes),
        },
        "estimate_usd": estimate and estimate["usd"],
        "cost": {
            "requests": len(pending),
            "rows_from_an_earlier_run": len(already[TASK]),
            "usd": budget.run_spend,
            "prior_phases_usd": prior,
            "phase_spend_usd": budget.run_spend + (budget.spent_before - prior),
            "against_shared_cap_usd": budget.phase_spend,
            "cap_usd": CAP_USD,
        },
        "note": (
            "In-sample by construction and pre-registered because of it. No prompt text moved:"
            " this run and the v2 run send byte-identical requests for every row that carries"
            " neither feature. Nothing is written to a batch file — the probe measures a"
            " rendering, it does not re-label a corpus."
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
        f"\n  {'preserved':<14} {counts['preserved']['kept']:>3}/{counts['preserved']['n']}"
        f"   PASS at {plan['gate']['preserved']['pass_at']}, KILL below"
        f" {plan['gate']['preserved']['kill_below']}"
        f"\n  {'feature-fixed':<14} {counts['feature_named']['landed']:>3}/"
        f"{counts['feature_named']['n']}   PASS at {plan['gate']['feature_fixed']['pass_at']},"
        f" KILL below {plan['gate']['feature_fixed']['kill_below']}"
        f"\n  ==> {gate}"
    )
    for name, block in record["compared_with"].items():
        print(
            f"    {name:<52} preserved {block['preserved']['kept']:>2}/{block['preserved']['n']}"
            f" · feature-fixed {block['feature_named']['landed']:>2}/{block['feature_named']['n']}"
            f" · other named {block['not_feature_named']['landed']:>2}/"
            f"{block['not_feature_named']['n']}"
        )
    print("\n  gated rows by the feature that explains them:")
    for name, block in record["per_family"].items():
        was_v22 = record["per_family_of_the_priors"]["v2.2"].get(name, {}).get("landed", 0)
        print(f"    {name:<8} {block['landed']:>2}/{block['n']}   (v2.2 landed {was_v22})")
    print(
        f"\n  moved from the reference, per field: {record['per_field_moved_from_the_reference']['v2ctx']}"
        f"\n  (v2.2 on the same rows:              {record['per_field_moved_from_the_reference']['v2.2']})"
        f"\n  preserved lost: {len(counts['preserved_lost'])}"
        f" · named-field-only: {len(counts['named_field_only'])}"
        f"\n  ungated 2: {len(counts['ungated_moved'])} moved,"
        f" {len(counts['ungated_unmoved'])} unmoved"
        f"\ncost ${budget.run_spend:.4f}, total against the ${CAP_USD:.2f} shared cap:"
        f" ${budget.phase_spend:.4f}"
        f"\nwrote {rel(args.record)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
