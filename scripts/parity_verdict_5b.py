#!/usr/bin/env python3
"""Phase 5b's serving-parity verdict, and the abort rule that can precede it — as code.

`docs/PROMPT-5b.md` §Deliverable 3 asks for the SPEC selection rule applied *mechanically*,
"code, not prose", and this is that code. It is committed before either config is scored, so
the rule cannot be reworded once the numbers are inconvenient — the discipline
`scripts/gate_verdict_45h.py` established for the 4.5h2 ablation, one phase on.

Two modes, and the second one exists because the phase's most likely outcome is that it
never spends:

``--project``
    the abort rule of SPEC amendment 3.11 (2). The smoke's own measurements — seconds per
    row, dollars per billed second, cold-start seconds — projected onto the pair. Always
    writes `results/parity_5b_projection.json`; if the projection is over the cap it *also*
    writes the verdict record, because "an aborted pair closes the merge question in favour
    of A" is a decision and a decision needs an artifact. A measured abort and a run that
    never happened look identical otherwise.

default
    both parity records against the 4.5h2 anchor. Every head is reported three ways — A, B,
    and the 4.5h2 pod number — with explicit deltas, then the rule decides. Bars are
    re-derived from the v4 anchor rather than read out of the 4.5h2 verdict, and the two are
    asserted equal: a bar that moved between the phases would silently rewrite the gate.

    PYTHONPATH=src python3 scripts/parity_verdict_5b.py --project \\
        --seconds-per-row 2.9 --usd-per-second 0.00047 --cold-start-seconds 240 --merge-usd 1.0
    PYTHONPATH=src python3 scripts/parity_verdict_5b.py --record results/parity_verdict_5b.json
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from market_pulse import records, scorer, serving  # noqa: E402

RESULTS = REPO_ROOT / "results"
BASELINES = RESULTS / "baselines.json"
ANCHOR_45H2 = RESULTS / "verdict_45h2.json"
PARITY = {"A": RESULTS / "parity_5b_a.json", "B": RESULTS / "parity_5b_b.json"}
PROJECTION = RESULTS / "parity_5b_projection.json"
VERDICT = RESULTS / "parity_verdict_5b.json"

VERSION = "v4"
CAP_USD = 4.00
"""SPEC amendment 3.11 (2): "hard budget stop $4 of the $8 cap"."""

TEST_V4_ROWS = 758
"""What 4.5h2 scored: 400 comments_test + 250 posts_test + 108 sarcasm_holdout."""

HEADS = ("G1a", "G1b", "G1c", "G1d", "G1e")

ABORT_RULE = (
    "if the smoke projects the pair over $4, stop before the paid run and report projections"
    " instead; a failed or aborted pair closes the merge question in favour of A, no retry"
    " (SPEC amendment 3.11 (2))"
)


def flat(values: dict) -> dict:
    """One number per head, in the shape the rule reads — G1b as its fix-rate."""
    return {gate: value for gate, value in values.items() if gate != "G1b"} | {
        "G1b": values["G1b"]["rate"]
    }


def bars_from_anchor() -> tuple[dict, dict]:
    """The v4 bars, re-derived, and the 4.5h2 verdict they must equal."""
    history = json.loads(BASELINES.read_text(encoding="utf-8"))
    anchor = records.anchor(history, VERSION)
    slice_text = (REPO_ROOT / anchor["config"]["g1b_slice_path"]).read_text(encoding="utf-8")
    ids = records.slice_ids(slice_text, anchor)
    bars = scorer.gate_thresholds(records.anchor_values(anchor), len(ids))
    recorded = json.loads(ANCHOR_45H2.read_text(encoding="utf-8"))
    if bars != recorded["bars"]:
        raise SystemExit(
            f"the bars re-derived from the {VERSION} anchor are not the ones"
            f" {ANCHOR_45H2.name} recorded: {bars} vs {recorded['bars']}. A bar that moved"
            " between the phases would rewrite the gate — stop and report."
        )
    return bars, recorded


def passed_at_45h2(recorded: dict) -> list[str]:
    """Which gates the shipped 4.5h2 arm passed. Derived, never typed.

    These are the gates the rule requires B to keep. Reading them off the record is
    what stops the requirement from quietly shrinking to whatever B happens to pass.
    """
    return sorted(gate for gate, verdict in recorded["verdicts"].items() if verdict["pass"])


def anchor_values(recorded: dict) -> dict:
    """The 4.5h2 pod numbers of the arm that shipped — every head's third column."""
    return flat(recorded["arms"][recorded["decision"]["selected"]]["values"])


def read_parity(path: Path, config: str) -> dict:
    """One config's eval record, refusing anything that is not the half it claims."""
    if not path.exists():
        raise SystemExit(f"{path} is missing — config {config} was not scored")
    record = json.loads(path.read_text(encoding="utf-8"))
    block = record.get("config", {}).get("serving")
    if not block:
        raise SystemExit(f"{path} carries no serving block — it is not a 5b endpoint run")
    if block.get("config") != config:
        raise SystemExit(f"{path} says it served config {block.get('config')!r}, not {config!r}")
    return record


def head_value(value):
    """A head's single number: G1a reports its per-language floors beside an overall."""
    return value["overall"] if isinstance(value, dict) else value


def column(label: str, a, b, anchor, precision: str = ".4f") -> str:
    return (
        f"{label:26}{a:>12{precision}}{b:>12{precision}}{anchor:>14{precision}}"
        f"{b - a:>+11{precision}}{a - anchor:>+13{precision}}"
    )


def task_mix(version: str = VERSION) -> dict:
    """How many rows of test ``version`` each rendering carries. Counted, not typed.

    Test v4 is 508 rows of `T1v2_with_post` and 250 of `T2`, and the two are not
    interchangeable: the with-post rendering carries the parent and runs to 1 388
    tokens, so it is the slower one. A smoke drawn evenly across the two tasks
    therefore *under*-predicts a run that is two-thirds the slow kind, and a flat
    mean of the smoke's per-row seconds is a projection biased toward spending.
    """
    import eval_zero_shot as runner  # noqa: PLC0415 — a script, imported for its inputs

    mix = {}
    for _name, rendering, filename in runner.inputs_for(version):
        # `inputs_for` already resolves the version's rendering, so this counts the
        # renderings the paid run will actually send — not the task ids they came from.
        mix[rendering] = mix.get(rendering, 0) + len(runner.load(runner.FROZEN / filename))
    return mix


def weighted_seconds_per_row(rows: list[dict], mix: dict) -> float:
    """The smoke's per-row seconds, re-weighted to the paid run's task mix."""
    total = sum(mix.values())
    weighted, covered = 0.0, 0
    for rendering, count in mix.items():
        seen = [row["wall_seconds"] for row in rows if row["task"] == rendering]
        if not seen:
            continue
        weighted += (count / total) * (sum(seen) / len(seen))
        covered += count
    if covered != total:
        raise SystemExit(
            f"the smoke covered {covered} of {total} rows' worth of renderings"
            f" ({sorted({row['task'] for row in rows})} vs {sorted(mix)}) — a projection that"
            " weights a rendering it never timed is a guess. Re-run the smoke over both."
        )
    return round(weighted, 3)


def from_smoke(path: Path) -> dict:
    """seconds-per-row, cold start and $/s, all read off the smoke's own artifact."""
    record = json.loads(path.read_text(encoding="utf-8"))
    cost = record.get("cost")
    if not cost:
        raise SystemExit(
            f"{path} carries no cost block — stamp the guard's measured spend into it first"
            " (scripts/smoke_5b.py --stamp-cost <USD>). A projection needs dollars."
        )
    if not cost.get("above_pod_floor"):
        raise SystemExit(
            f"{path}'s derived rate {cost['usd_per_second']} is below the A6000 pod floor"
            f" {cost['floor_usd_per_second']}. Serverless does not bill under the pod class it"
            " runs on — the balance had not settled. Re-read the guard and stamp again."
        )
    return {
        "seconds_per_row": weighted_seconds_per_row(record["rows"], task_mix()),
        "usd_per_second": cost["usd_per_second"],
        "cold_start_seconds": record["cold_start"]["wall_seconds"],
    }


def project(args) -> dict:
    """The abort rule's arithmetic, from what the smoke measured."""
    return serving.project_pair_usd(
        seconds_per_row=args.seconds_per_row,
        rows=args.rows,
        runs=2,
        usd_per_second=args.usd_per_second,
        cold_start_seconds=args.cold_start_seconds,
        merge_usd=args.merge_usd,
        spent_usd=args.spent_usd,
    )


def stamp(payload: dict) -> dict:
    return payload | {
        "step": "5b serving parity",
        "testset_version": VERSION,
        "cap_usd": CAP_USD,
        "written_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }


def shown(path: Path) -> Path:
    return path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path


def write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"record: {shown(path)}")


def run_projection(args) -> int:
    projection = project(args)
    over = projection["total_usd"] > CAP_USD
    print(f"seconds per run    {projection['seconds_per_run']}")
    print(f"scored             ${projection['scored_usd']:.4f}  (2 runs of {args.rows} rows)")
    print(f"merge job          ${projection['merge_usd']:.4f}")
    print(f"PROJECTED PAIR     ${projection['projected_usd']:.4f}")
    print(f"already spent      ${projection['spent_usd']:.4f}  (staging, cold-start proof, smoke)")
    print(f"5b TOTAL           ${projection['total_usd']:.4f} of ${CAP_USD:.2f}")
    print(f"VERDICT            {'OVER THE CAP — do not run the pair' if over else 'clears'}")
    write(
        PROJECTION,
        stamp({"projection": projection, "abort_rule": ABORT_RULE, "over_cap": over}),
    )
    if over:
        # The decision, not just its input. SPEC: an aborted pair closes the merge
        # question in favour of A, so the shipped config is named here and 5c reads it.
        write(
            VERDICT,
            stamp(
                {
                    "outcome": "aborted-over-cap",
                    "abort_rule": ABORT_RULE,
                    "projection": projection,
                    "rule": scorer.SERVING_SELECTION_RULE,
                    "selected": "A",
                    "shipped": "A",
                    "why": (
                        f"the smoke projects the pair at ${projection['projected_usd']:.4f} on"
                        f" top of ${projection['spent_usd']:.4f} already spent —"
                        f" ${projection['total_usd']:.4f} against the ${CAP_USD:.2f} hard stop,"
                        f" which is on the phase, not on the pair. No paid pair ran; SPEC amendment"
                        " 3.11 (2) closes the merge question in favour of A. Merging stays"
                        " forbidden — it is adopted only if this measurement selects it, and"
                        " this measurement did not happen."
                    ),
                }
            ),
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", action="store_true", help="the abort rule, before the pair")
    parser.add_argument("--seconds-per-row", type=float, help="--project: measured by the smoke")
    parser.add_argument("--usd-per-second", type=float, help="--project: spend / billed seconds")
    parser.add_argument("--cold-start-seconds", type=float, default=0.0)
    parser.add_argument("--merge-usd", type=float, default=0.0, help="--project: config B's job")
    parser.add_argument(
        "--spent-usd",
        type=float,
        default=0.0,
        help="--project: what 5b has already cost, read from runpod_guard. The $4 stop is on"
        " the phase, so a projection that ignores it authorises a run the phase cannot afford.",
    )
    parser.add_argument("--rows", type=int, default=TEST_V4_ROWS)
    parser.add_argument(
        "--smoke-record",
        type=Path,
        help="--project: derive seconds-per-row, cold start and $/s from results/serving_5b.json"
        " instead of typing them. Explicit flags override.",
    )
    parser.add_argument("--record", type=Path, help="persist the verdict as well as printing it")
    args = parser.parse_args(argv)

    if args.project:
        if args.smoke_record:
            for field, value in from_smoke(args.smoke_record).items():
                if getattr(args, field) in (None, 0):
                    setattr(args, field, value)
        missing = [
            name
            for name in ("seconds_per_row", "usd_per_second")
            if getattr(args, name) in (None, 0)
        ]
        if missing:
            parser.error(f"--project needs {missing} from the smoke — a projection is measured")
        return run_projection(args)

    bars, recorded = bars_from_anchor()
    required = passed_at_45h2(recorded)
    anchor = anchor_values(recorded)
    parity = {config: read_parity(path, config) for config, path in PARITY.items()}
    values = {config: records.arm_values(record) for config, record in parity.items()}
    verdicts = {
        config: scorer.gate_verdicts(
            {
                "G1a": value["G1a"],
                "G1b": {"fixed": value["G1b"]["fixed"], "guard_delta": value["G1b"]["guard_delta"]},
                **{gate: value[gate] for gate in ("G1c", "G1d", "G1e")},
            },
            bars,
        )
        for config, value in values.items()
    }

    print(f"anchor: {recorded['anchor']['model']} @ {recorded['anchor']['timestamp']} — {VERSION}")
    print(f"4.5h2 shipped arm: {recorded['decision']['selected']}, gates passed {required}")
    for config, record in parity.items():
        block = record["config"]["serving"]
        print(
            f"config {config}: endpoint {block['endpoint_id']} · {block['merge_state']}"
            f" · {block['timing']['worker_seconds']}s billed · {record['timestamp']}"
        )

    print("\n--- every head: A, B, and the 4.5h2 pod number ---")
    print(f"{'':26}{'A':>12}{'B':>12}{'4.5h2':>14}{'B-A':>11}{'A-4.5h2':>13}")
    flat_values = {config: flat(value) for config, value in values.items()}
    for head in HEADS:
        print(
            column(
                head,
                head_value(flat_values["A"][head]),
                head_value(flat_values["B"][head]),
                head_value(anchor[head]),
            )
        )
    for language in scorer.GATED_LANGUAGES:
        print(
            column(
                f"  G1a {language}",
                values["A"]["G1a"][language],
                values["B"]["G1a"][language],
                recorded["arms"][recorded["decision"]["selected"]]["values"]["G1a"][language],
            )
        )

    decision = scorer.select_serving_config(
        flat_values["A"],
        flat_values["B"],
        must_stay_passing={gate: verdicts["B"][gate]["pass"] for gate in required},
    )
    print(f"\n--- the rule ---\n{decision['rule']}")
    print(f"  required gates still passing on B   {decision['must_stay_passing']}")
    print(f"  head deltas (B - A)                 {decision['head_deltas']}")
    print(f"  drops beyond {decision['tolerance']}                  {decision['drops'] or 'none'}")
    print(f"  SHIPPED CONFIG                      {decision['selected']}  ({decision['why']})")

    payload = stamp(
        {
            "outcome": "pair-scored",
            "anchor": recorded["anchor"],
            "bars": bars,
            "required_gates": required,
            "anchor_values_45h2": anchor,
            "configs": {
                config: {
                    "record": str(shown(PARITY[config])),
                    "timestamp": parity[config]["timestamp"],
                    "serving": parity[config]["config"]["serving"],
                    "values": values[config],
                    "verdicts": verdicts[config],
                    "passed": sum(1 for v in verdicts[config].values() if v["pass"]),
                }
                for config in PARITY
            },
            "decision": decision,
            "shipped": decision["selected"],
        }
    )
    if PROJECTION.exists():
        payload["projection"] = json.loads(PROJECTION.read_text(encoding="utf-8"))["projection"]
    if args.record:
        write(args.record, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
