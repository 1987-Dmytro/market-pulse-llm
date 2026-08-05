#!/usr/bin/env python3
"""The пласт ablation's decision and the five Tier-1 verdicts, as a script output (4.5h2).

`docs/PROMPT-4.5h2.md` §6 asks for the pre-registered rule's *application*, committed as
code BEFORE any arm is scored — not a paragraph afterwards claiming it was applied. So
this reads the two arm records out of `results/baselines.json`, prints both columns side
by side, applies the rule arithmetically, and decides the gates of the arm it selects
against bars derived from the v4 anchor. Nothing here is typed: the anchors, the slice
size, the margins and the tolerance all come from the record, the slice file and
`market_pulse.scorer`.

The rule is amendment 3.4 (3) **transposed** — Phase 4's synthetic ablation turned on
G1b, this one turns on G1c — and the transposition is a parameter of one judge rather
than a second copy of it (`scorer.select_arm_by`). What the pivot changes is the *second*
half of the rule: G1b stops being what the arm is chosen for and becomes one of the heads
it may not regress, which is what stops an arm buying intents with a collapsed sarcasm
slice.

Read-only by default, so a reviewer who trusts neither the report nor this script can
re-run it. `--record` persists the same numbers, because "the gate passed" in prose is
not the gate.

    PYTHONPATH=src python3 scripts/gate_verdict_45h.py
    PYTHONPATH=src python3 scripts/gate_verdict_45h.py --record results/verdict_45h2.json
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse import records, scorer  # noqa: E402

RESULTS = REPO_ROOT / "results" / "baselines.json"
VERSION = "v4"
ARMS = ("without-plast", "with-plast")
PIVOT = "G1c"

SELECTION_RULE = (
    "the пласт stays iff arm B's G1c is strictly higher than arm A's AND no other gated"
    " head of B is lower than A's by more than 0.5 pp (SPEC amendment 3.4 (3) transposed;"
    " operator decision of 2026-08-04, fixed and committed before any arm was scored)"
)
"""The rule, in the words `docs/PROMPT-4.5h2.md` §6 fixes it. A test holds this string to
that document: a rule that can be reworded after the numbers are in is not pre-registered.
"""

LABELS = {
    "G1a": "G1a sentiment macro-F1",
    "G1b": "G1b slice fix-rate",
    "G1c": "G1c intents micro-F1",
    "G1d": "G1d post_type macro-F1",
    "G1e": "G1e brand extraction F1",
}


def relevance(record: dict) -> float | None:
    """The head amendment 3.3 reports beside G1d and never inside it."""
    for entry in record["gates"]:
        if entry["gate"] == "G1d" and entry["metric"].startswith("relevance"):
            return entry["value"]
    return None


def line(label: str, low: float, high: float, delta: bool = True) -> None:
    tail = f"{high - low:>+11.4f}" if delta else ""
    print(f"{label:32}{low:>14.4f}{high:>16.4f}{tail}")


def columns(values: dict, arms: dict) -> None:
    """Both arms, every gated head, with the difference between them."""
    left, right = values[ARMS[0]], values[ARMS[1]]
    print(f"{'':32}{ARMS[0]:>14}{ARMS[1]:>16}{'delta':>11}")
    line(LABELS["G1a"], left["G1a"]["overall"], right["G1a"]["overall"])
    for language in scorer.GATED_LANGUAGES:
        line(f"  {language}", left["G1a"][language], right["G1a"][language])
    print(
        f"{LABELS['G1b']:32}{left['G1b']['fixed']:>8}/{left['G1b']['n']:<5}"
        f"{right['G1b']['fixed']:>10}/{right['G1b']['n']:<5}"
    )
    line("  rate", left["G1b"]["rate"], right["G1b"]["rate"])
    line("  guard delta (>= -0.02)", left["G1b"]["guard_delta"], right["G1b"]["guard_delta"], False)
    for gate in ("G1c", "G1d", "G1e"):
        line(LABELS[gate], left[gate], right[gate])
    both = [relevance(arms[arm]) for arm in ARMS]
    if all(value is not None for value in both):
        print(
            f"{'relevance (reported, not gated)':32}{both[0]:>14.4f}{both[1]:>16.4f}"
            f"{both[1] - both[0]:>+11.4f}"
        )


def flat(values: dict) -> dict:
    """One number per gated head, in the shape the rule reads."""
    return {gate: value for gate, value in values.items() if gate != "G1b"} | {
        "G1b": values["G1b"]["rate"]
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=RESULTS)
    parser.add_argument("--record", type=Path, help="persist the verdict as well as printing it")
    args = parser.parse_args(argv)

    try:
        history = json.loads(args.results.read_text(encoding="utf-8"))
        anchor = records.anchor(history, VERSION)
        slice_text = (REPO_ROOT / anchor["config"]["g1b_slice_path"]).read_text(encoding="utf-8")
        ids = records.slice_ids(slice_text, anchor)
        bars = scorer.gate_thresholds(records.anchor_values(anchor), len(ids))
        arms = {arm: records.arm_record(history, arm) for arm in ARMS}
        values = {arm: records.arm_values(record) for arm, record in arms.items()}
    except (ValueError, KeyError, OSError) as err:
        raise SystemExit(f"refused: {err}") from None

    print(f"anchor: {anchor['model']} @ {anchor['timestamp']} — test set {VERSION}, bars derived")
    print(f"        rendering {anchor['config']['prompt_revision']}")
    for arm, record in arms.items():
        fine = record["config"]["fine_tune"]
        print(
            f"{arm:15} {record['timestamp']}  dataset {fine['train_sha256'][:12]}"
            f"  adapter {fine['adapter_sha256'][:12]}  {fine['n_train']} rows"
        )

    print("\n--- both arms ---")
    columns(values, arms)

    decision = scorer.select_arm_by(
        flat(values[ARMS[0]]),
        flat(values[ARMS[1]]),
        pivot=PIVOT,
        rule=SELECTION_RULE,
        names=ARMS,
    )
    print(f"\n--- the rule ---\n{decision['rule']}")
    pivot = decision[PIVOT.lower()]
    print(
        f"  {PIVOT} strictly higher   {pivot[ARMS[1]]:.4f} > {pivot[ARMS[0]]:.4f}"
        f"   {'YES' if pivot['strictly_higher'] else 'NO'}"
    )
    print(
        "  head deltas           "
        + " · ".join(f"{gate} {delta:+.4f}" for gate, delta in decision["head_deltas"].items())
    )
    print(
        f"  lower by > {decision['tolerance'] * 100:.1f} pp     "
        + (
            " · ".join(f"{gate} {delta:+.4f}" for gate, delta in decision["regressions"].items())
            or "none"
        )
    )
    selected = decision["selected"]
    print(
        f"  SELECTED ARM          {selected}"
        f"  (the пласт {'stays' if decision['keep'] else 'is dropped'})"
    )

    chosen = values[selected]
    verdicts = scorer.gate_verdicts(
        {
            "G1a": chosen["G1a"],
            "G1b": {"fixed": chosen["G1b"]["fixed"], "guard_delta": chosen["G1b"]["guard_delta"]},
            **{gate: chosen[gate] for gate in ("G1c", "G1d", "G1e")},
        },
        bars,
    )
    print(f"\n--- Tier-1 verdicts — {selected} (n={bars['G1b']['n']} for G1b) ---")
    print(f"{'gate':6}{'what':16}{'value':>10}{'bar':>10}   verdict")
    for gate, verdict in verdicts.items():
        for check in verdict["checks"]:
            shape = ">10" if isinstance(check["value"], int) else ">10.4f"
            print(
                f"{gate:6}{check['what']:16}{check['value']:{shape}}"
                f"{check['bar']:{shape}}   {'PASS' if check['pass'] else 'FAIL'}"
            )
        print(f"{gate:6}{'':16}{'':>10}{'':>10}   ==> {'PASS' if verdict['pass'] else 'FAIL'}")
    passed = sum(1 for verdict in verdicts.values() if verdict["pass"])
    print(f"\n{passed} of {len(verdicts)} Tier-1 gates pass on the {selected} arm.")

    if args.record:
        args.record.write_text(
            json.dumps(
                {
                    "step": "4.5h2 пласт ablation",
                    "testset_version": VERSION,
                    "anchor": {
                        "model": anchor["model"],
                        "timestamp": anchor["timestamp"],
                        "g1b_slice_path": anchor["config"]["g1b_slice_path"],
                        "g1b_slice_sha256": anchor["config"]["g1b_slice_sha256"],
                        "prompt_revision_sha256": anchor["config"]["prompt_revision_sha256"],
                    },
                    "bars": bars,
                    "arms": {
                        arm: {
                            "timestamp": record["timestamp"],
                            "fine_tune": record["config"]["fine_tune"],
                            "values": values[arm],
                            "relevance_reported_not_gated": relevance(record),
                        }
                        for arm, record in arms.items()
                    },
                    "decision": decision,
                    "verdicts": verdicts,
                    "passed": passed,
                    "of": len(verdicts),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        shown = (
            args.record.relative_to(REPO_ROOT)
            if args.record.is_absolute() and args.record.is_relative_to(REPO_ROOT)
            else args.record
        )
        print(f"\nrecord: {shown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
