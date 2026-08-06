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

``--single``
    what the pair became. SPEC amendment 3.11 (2) was amended again on 2026-08-06, after the
    pair aborted on an unreachable serverless runtime: config A alone, once, on the pod
    runtime. There is no rule to apply — the merge question is closed and B is dead — so this
    mode reports instead of selecting, and it moves no bar.

    PYTHONPATH=src python3 scripts/parity_verdict_5b.py --project \\
        --seconds-per-row 2.9 --usd-per-second 0.00047 --cold-start-seconds 240 --merge-usd 1.0
    PYTHONPATH=src python3 scripts/parity_verdict_5b.py --record results/parity_verdict_5b.json
    PYTHONPATH=src python3 scripts/parity_verdict_5b.py --single
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


def from_ladder(path: Path, arm: str) -> dict:
    """One ladder arm's seconds-per-row, re-weighted to the paid run's task mix.

    The ladder measures the candidate N on 24 carve rows; the paid run sends 758 test
    rows in a mix the carve does not share (19:5 there, 508:250 here). Weighting is the
    same arithmetic `from_smoke` does — and the same refusal if an arm never timed one of
    the two renderings. No cost is read: a ladder arm is billed inside the same pod-hour
    as everything else, and the rate comes from the machine, not from an arm.
    """
    record = json.loads(path.read_text(encoding="utf-8"))
    arms = record.get("arms") or {}
    if arm not in arms:
        raise SystemExit(f"{path} holds arms {sorted(arms)}, not {arm!r}")
    if arms[arm].get("failed"):
        raise SystemExit(f"{path} arm {arm} failed ({arms[arm]['failed']}) — it timed nothing")
    return {"seconds_per_row": weighted_seconds_per_row(arms[arm]["rows"], task_mix())}


def project(args) -> dict:
    """The abort rule's arithmetic, from what the smoke measured.

    ``--runs`` is 2 for the pre-registered pair and 1 for the single-config measurement
    SPEC amendment 3.11 (2) put in its place. It is a flag rather than a constant because
    the cap it is compared against never moved: the $4 stop is on the phase, ``spent_usd``
    carries what the phase has already cost, and "the $3.47 remaining" is the same
    inequality read from the other end.
    """
    return serving.project_pair_usd(
        seconds_per_row=args.seconds_per_row,
        rows=args.rows,
        runs=args.runs,
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


def run_abort(args) -> int:
    """The pair could not be scored at all. SPEC's outcome, with the evidence.

    Distinct from the cost abort on purpose. `--project` records "we measured what
    the pair would cost and it is over the cap"; this records "the pre-registered
    runtime could not be reached", and the two must not be confusable by a reader
    six weeks from now. Both end in the same shipped config, because SPEC amendment
    3.11 (2) says a failed or aborted pair closes the merge question in favour of A
    — and both leave an artifact, because a measured abort and a phase nobody ran
    look identical otherwise.
    """
    write(
        args.verdict_out,
        stamp(
            {
                "outcome": "aborted-runtime-unreachable",
                "abort_rule": ABORT_RULE,
                "rule": scorer.SERVING_SELECTION_RULE,
                "selected": "A",
                "shipped": "A",
                "blocker": args.blocker,
                "evidence": args.evidence,
                "spent_usd": args.spent_usd,
                "cap_usd": CAP_USD,
                "why": (
                    "the pair was never scored: the production serverless runtime SPEC"
                    " amendment 3.11 (2) pre-registers could not be reached. An aborted pair"
                    " closes the merge question in favour of A, and merging stays forbidden —"
                    " it is adopted only if this measurement selects it, and this measurement"
                    " did not happen. No gate number in results/verdict_45h2.json is touched."
                ),
            }
        ),
    )
    print("OUTCOME            aborted-runtime-unreachable, shipped A")
    print(f"blocker            {args.blocker}")
    for line in args.evidence:
        print(f"  - {line}")
    print(f"spent              ${args.spent_usd:.4f} of ${CAP_USD:.2f}")
    return 0


def run_projection(args) -> int:
    projection = project(args)
    over = projection["total_usd"] > CAP_USD
    scored = "the pair" if args.runs == 2 else f"{args.runs} run"
    print(f"seconds per run    {projection['seconds_per_run']}")
    print(f"scored             ${projection['scored_usd']:.4f}  ({args.runs} x {args.rows} rows)")
    print(f"merge job          ${projection['merge_usd']:.4f}")
    print(f"PROJECTED {scored:<8} ${projection['projected_usd']:.4f}")
    print(f"already spent      ${projection['spent_usd']:.4f}  (staging, cold-start proof, smoke)")
    print(f"5b TOTAL           ${projection['total_usd']:.4f} of ${CAP_USD:.2f}")
    print(f"headroom left      ${CAP_USD - projection['spent_usd']:.4f}")
    print(f"VERDICT            {'OVER THE CAP — do not run' if over else 'clears'}")
    write(
        args.projection_out,
        stamp(
            {
                "projection": projection,
                "runs": args.runs,
                "abort_rule": ABORT_RULE,
                "over_cap": over,
            }
        ),
    )
    if over:
        # The decision, not just its input. SPEC: an aborted pair closes the merge
        # question in favour of A, so the shipped config is named here and 5c reads it.
        write(
            args.verdict_out,
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


def run_single(args) -> int:
    """SPEC amendment 3.11 (2)'s single-config measurement: A on the pod, beside the anchors.

    Deliberately **not** `main`'s rule. The pair is closed and B is dead, so there is nothing
    to select and no config to ship that is not already shipped. What this does is report:
    every head three ways — the pod-runtime number, the 4.5h2 anchor, the delta — against the
    bar it is measured by, re-derived from the v4 anchor and asserted equal to the one 4.5h2
    recorded. Whatever it finds, **no bar moves**: a head that passed at 4.5h2 and lands under
    its bar here is a loud finding for an operator briefing, not this phase's verdict, and
    saying so in the artifact is what stops a later reader from taking it for one.

    The comparison is stamped into the parity record itself, because that is where the brief
    puts it — "per-gate-head numbers BESIDE the 4.5h2 anchors with explicit deltas" — and a
    number that lives in one file and its baseline in another gets compared by hand exactly
    once. `results/parity_verdict_5b.json` is never touched: it is the committed verdict of
    the aborted pair, and this measurement does not re-open it.
    """
    bars, recorded = bars_from_anchor()
    required = passed_at_45h2(recorded)
    anchor = anchor_values(recorded)
    record = read_parity(args.parity_record, "A")
    values = records.arm_values(record)
    flat_values = flat(values)
    verdicts = scorer.gate_verdicts(
        {
            "G1a": values["G1a"],
            "G1b": {"fixed": values["G1b"]["fixed"], "guard_delta": values["G1b"]["guard_delta"]},
            **{gate: values[gate] for gate in ("G1c", "G1d", "G1e")},
        },
        bars,
    )
    deltas = {
        head: round(head_value(flat_values[head]) - head_value(anchor[head]), 6) for head in HEADS
    }
    under_bar = sorted(gate for gate in required if not verdicts[gate]["pass"])

    block = record["config"]["serving"]
    print(f"anchor: {recorded['anchor']['model']} @ {recorded['anchor']['timestamp']} — {VERSION}")
    print(f"4.5h2 shipped arm: {recorded['decision']['selected']}, gates passed {required}")
    print(
        f"config A: {block.get('transport', 'serverless-api')} {block.get('endpoint_id')}"
        f" · {block['merge_state']} · {record['timestamp']}"
    )
    print("\n--- every head: the pod runtime, the 4.5h2 pod number, and the delta ---")
    print(f"{'':26}{'A on pod':>12}{'4.5h2':>14}{'delta':>12}{'bar':>12}{'pass':>7}")
    for head in HEADS:
        bar = bars[head].get("min", bars[head].get("min_fixed"))
        print(
            f"{head:26}{head_value(flat_values[head]):>12.4f}{head_value(anchor[head]):>14.4f}"
            f"{deltas[head]:>+12.4f}{bar:>12.4f}{str(verdicts[head]['pass']):>7}"
        )
    for language in scorer.GATED_LANGUAGES:
        pod_value = values["G1a"][language]
        was = recorded["arms"][recorded["decision"]["selected"]]["values"]["G1a"][language]
        print(f"{'  G1a ' + language:26}{pod_value:>12.4f}{was:>14.4f}{pod_value - was:>+12.4f}")

    print(f"\npassed {sum(1 for v in verdicts.values() if v['pass'])} of {len(HEADS)}")
    if under_bar:
        print(
            f"\nLOUD FINDING: {under_bar} passed at 4.5h2 and land UNDER the bar on the"
            " production runtime. No bar moves and this phase rules on nothing — SPEC"
            " amendment 3.11 (2) sends it to an operator briefing."
        )
    payload = stamp(
        {
            "outcome": "single-config-scored",
            "config": "A",
            "runtime": block.get("transport", "serverless-api"),
            "not_a_gate": (
                "SPEC amendment 3.11 (2): the deltas are reported, never averaged away, and no"
                " bar moves. A 4.5h2-passed head under its bar here is a finding for an operator"
                " briefing, not a verdict of this phase."
            ),
            "pair_status": (
                "closed — results/parity_verdict_5b.json, aborted-runtime-unreachable, A ships"
                " and merging stays forbidden. Config B was never built."
            ),
            "anchor": recorded["anchor"],
            "bars": bars,
            "required_gates": required,
            "anchor_values_45h2": anchor,
            "values": values,
            "deltas_vs_45h2": deltas,
            "verdicts": verdicts,
            "passed": sum(1 for v in verdicts.values() if v["pass"]),
            "under_bar": under_bar,
        }
    )
    write(args.parity_record, record | {"parity": payload})
    return 0


def predictions(path: Path) -> dict:
    """A prediction dump as ``(input, id) -> pred``, refusing a duplicated row.

    Keyed rather than zipped, because the two runs' dumps are both sorted by
    ``(input, id)`` and a comparison that trusted the order would silently pair the
    wrong rows if either lost one. A dict built from duplicates is last-wins, which is
    a decision no reader would see — so a repeated key stops instead.
    """
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        key = (row["input"], row["id"])
        if key in out:
            raise SystemExit(f"{path} holds {key} twice — a dump with duplicate rows is not one")
        out[key] = row["pred"]
    return out


def row_agreement(batch_dump: Path, anchor_dump: Path) -> dict:
    """How often the batched run labelled a row exactly as the batch-1 run did.

    **Description, never a gate** — SPEC amendment 3.11 (2) is explicit: the adoption rule
    is the gate heads, and row-level agreement is reported beside them. It is here because
    5b.1 could not report it at all (arm A's 4.5h2 dump was lost on 04.08,
    `results/predictions/LOST.md`) and this is the first comparison in this project that
    has both dumps.
    """
    batched, base = predictions(batch_dump), predictions(anchor_dump)
    shared = sorted(set(batched) & set(base))
    agree = [key for key in shared if batched[key] == base[key]]
    disagree = [key for key in shared if batched[key] != base[key]]
    per_input = {}
    for name, row_id in shared:
        seen = per_input.setdefault(name, {"rows": 0, "agree": 0})
        seen["rows"] += 1
        seen["agree"] += batched[(name, row_id)] == base[(name, row_id)]
    return {
        "compared": len(shared),
        "in_batch_only": sorted(f"{n}:{i}" for n, i in set(batched) - set(base)),
        "in_batch_1_only": sorted(f"{n}:{i}" for n, i in set(base) - set(batched)),
        "agree": len(agree),
        "rate": round(len(agree) / len(shared), 6) if shared else None,
        "per_input": {
            name: seen | {"rate": round(seen["agree"] / seen["rows"], 6)}
            for name, seen in sorted(per_input.items())
        },
        "disagreeing_ids": [f"{n}:{i}" for n, i in disagree][:40],
        "not_a_gate": (
            "reported as description. The adoption rule reads the gate heads and the bars,"
            " never this number (SPEC amendment 3.11 (2))."
        ),
    }


def scored_every_row(record: dict, path: Path) -> dict:
    """Refuse a partial run before it is compared to anything.

    `read_parity` checks the record claims config A and nothing else. A run that lost rows
    to an `ApiError` is a **failed attempt** under SPEC amendment 3.11 (2) — "one attempt,
    no retry" — not a lower number to compare, and `solo_retried` names the rows the
    per-row fallback re-generated at batch 1 while the record still says N.
    """
    blocks = record["diagnostics"]["failures"]
    lost = [b for b in blocks if b["scored"] != b["rows"]]
    if lost:
        raise SystemExit(
            f"{path}: {[(b['input'], b['scored'], b['rows']) for b in lost]} — rows were not"
            " scored. Under SPEC amendment 3.11 (2) that is a failed attempt, not a result."
        )
    solo = sorted(row_id for block in blocks for row_id in block.get("solo_retried", []))
    return {"rows": sum(b["rows"] for b in blocks), "solo_retried": solo}


def batch_size_of(record: dict) -> int:
    return record["config"]["generation"]["batch_size"]


def run_batch(args) -> int:
    """SPEC amendment 3.11 (2)'s batch measurement: N against batch 1, and the rule applied.

    Three columns, not two. The rule reads the batch-1 record — that is what production
    already does and what the change is charged against — but the 4.5h2 anchors stay in the
    table because they are what the gates were written on, and a reader six weeks out must
    be able to see both distances at once.

    The verdict is `scorer.select_serving_config`, unforked: the shape is identical (does
    every required gate still pass, did any head drop more than the tolerance) and forking
    it to say "batch" instead of "config" would be a second copy of the one rule this
    project has for questions of this form.
    """
    bars, recorded = bars_from_anchor()
    required = passed_at_45h2(recorded)
    anchor = anchor_values(recorded)
    base_record = read_parity(args.baseline_record, "A")
    batch_record = read_parity(args.parity_record, "A")
    base_n, batch_n = batch_size_of(base_record), batch_size_of(batch_record)
    if base_n != 1 or batch_n <= 1:
        raise SystemExit(
            f"the baseline was scored at batch {base_n} and the candidate at batch {batch_n}."
            " This comparison is only a batch measurement if the first is 1 and the second is"
            " above it — stop and report rather than labelling whatever is in the files."
        )
    integrity = scored_every_row(batch_record, args.parity_record)

    base_values, batch_values = records.arm_values(base_record), records.arm_values(batch_record)
    base_flat, batch_flat = flat(base_values), flat(batch_values)
    verdicts = scorer.gate_verdicts(
        {
            "G1a": batch_values["G1a"],
            "G1b": {
                "fixed": batch_values["G1b"]["fixed"],
                "guard_delta": batch_values["G1b"]["guard_delta"],
            },
            **{gate: batch_values[gate] for gate in ("G1c", "G1d", "G1e")},
        },
        bars,
    )
    decision = scorer.select_serving_config(
        base_flat,
        batch_flat,
        must_stay_passing={gate: verdicts[gate]["pass"] for gate in required},
        rule=scorer.BATCH_SELECTION_RULE,
        tolerance=scorer.SYNTHETIC_HEAD_TOLERANCE,
        names=("batch-1", f"batch-{batch_n}"),
    )
    deltas_vs_anchor = {
        head: round(head_value(batch_flat[head]) - head_value(anchor[head]), 6) for head in HEADS
    }
    agreement = (
        row_agreement(args.batch_dump, args.baseline_dump)
        if args.batch_dump and args.baseline_dump
        else None
    )

    print(f"anchor: {recorded['anchor']['model']} @ {recorded['anchor']['timestamp']} — {VERSION}")
    print(f"4.5h2 shipped arm: {recorded['decision']['selected']}, gates passed {required}")
    print(f"batch {batch_n} vs batch 1 · {integrity['rows']} rows scored, none lost")
    print(f"\n{'':22}{'batch ' + str(batch_n):>12}{'batch 1':>12}{'4.5h2':>12}", end="")
    print(f"{'Δ vs 1':>11}{'bar':>12}{'pass':>7}")
    for head in HEADS:
        bar = bars[head].get("min", bars[head].get("min_fixed"))
        print(
            f"{head:22}{head_value(batch_flat[head]):>12.4f}{head_value(base_flat[head]):>12.4f}"
            f"{head_value(anchor[head]):>12.4f}{decision['head_deltas'][head]:>+11.4f}"
            f"{bar:>12.4f}{str(verdicts[head]['pass']):>7}"
        )
    for language in scorer.GATED_LANGUAGES:
        now, was = batch_values["G1a"][language], base_values["G1a"][language]
        print(f"{'  G1a ' + language:22}{now:>12.4f}{was:>12.4f}{'':>12}{now - was:>+11.4f}")
    if agreement:
        print(f"\nrow agreement vs the batch-1 dump: {agreement['agree']}/{agreement['compared']}")
        for name, seen in agreement["per_input"].items():
            print(f"  {name:<18} {seen['agree']:>4}/{seen['rows']:<5} {seen['rate']:.4f}")
        print("  (description — the rule reads the heads and the bars, never this)")
    if integrity["solo_retried"]:
        print(
            f"\nMIXED BATCH: {len(integrity['solo_retried'])} rows were re-generated at batch 1"
            f" by the fallback — {integrity['solo_retried'][:8]}. The number above is not a"
            f" measurement of batch {batch_n} alone; report it as mixed, never averaged away."
        )
    print(f"\nrule: {decision['why']}")
    print(
        f"ADOPTED: {decision['selected']}" if decision["adopt_b"] else "NOT ADOPTED: batch 1 stays"
    )

    payload = stamp(
        {
            "outcome": "batch-measured",
            "candidate_batch_size": batch_n,
            "baseline": {
                "record": str(shown(args.baseline_record)),
                "batch_size": base_n,
                "values": base_flat,
            },
            "adopted": decision["adopt_b"],
            "adopted_batch_size": batch_n if decision["adopt_b"] else 1,
            "decision": decision,
            "required_gates": required,
            "bars": bars,
            "anchor": recorded["anchor"],
            "anchor_values_45h2": anchor,
            "values": batch_values,
            "deltas_vs_batch_1": decision["head_deltas"],
            "deltas_vs_45h2": deltas_vs_anchor,
            "verdicts": verdicts,
            "passed": sum(1 for v in verdicts.values() if v["pass"]),
            "under_bar": sorted(gate for gate in required if not verdicts[gate]["pass"]),
            "rows_scored": integrity["rows"],
            "solo_retried": integrity["solo_retried"],
            "row_agreement": agreement,
            "on_failure": (
                "SPEC amendment 3.11 (2): a failed measurement fixes serving at batch 1"
                " permanently and returns the money question to the operator. One attempt,"
                " no retry at another N."
            ),
        }
    )
    write(args.parity_record, batch_record | {"parity": payload})
    if args.serving_record:
        stamp_adopted(args.serving_record, payload, batch_record, args.usd_per_hour)
    return 0


def stamp_adopted(path: Path, payload: dict, record: dict, usd_per_hour: float) -> None:
    """What 5c reads: the adopted batch, and what a row costs at it.

    Added to `results/serving_5b.json` rather than written over it — that file is the 5b.1
    smoke plus the cost block stamped into it after the fact, which `--project` still reads
    and the 5b.1 projection was derived from. A new key answers the new question without
    destroying the old answer.
    """
    timing = record["config"]["serving"]["timing"]
    rows = payload["rows_scored"]
    seconds_per_row = round(timing["wall_seconds"] / rows, 3)
    served = json.loads(path.read_text(encoding="utf-8"))
    served["adopted"] = {
        "decided_at": payload["written_at"],
        "batch_size": payload["adopted_batch_size"],
        "measured_at_batch_size": payload["candidate_batch_size"],
        "adopted": payload["adopted"],
        "why": payload["decision"]["why"],
        "rows": rows,
        "wall_seconds": timing["wall_seconds"],
        "seconds_per_row": seconds_per_row,
        "usd_per_hour": usd_per_hour,
        "usd_per_1000_rows": round(seconds_per_row * usd_per_hour / 3600 * 1000, 4),
        "source": str(shown(REPO_ROOT / "results" / "parity_5b2.json")),
        "note": (
            "seconds_per_row is the paid run's whole wall over its rows, so it carries the"
            " handshake call on an already-warm worker and no cold start — a per-pass model"
            " adds the cold start separately (53.0 s measured 2026-08-06 on local NVMe)."
            " If `adopted` is false the batch_size here is 1: SPEC amendment 3.11 (2) fixes"
            " serving at batch 1 permanently on a failed measurement."
        ),
    }
    path.write_text(json.dumps(served, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"record: {shown(path)} — adopted batch {served['adopted']['batch_size']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", action="store_true", help="the abort rule, before the pair")
    parser.add_argument(
        "--single",
        action="store_true",
        help="SPEC amendment 3.11 (2)'s single-config measurement: config A against the 4.5h2"
        " anchors, deltas reported and no bar moved. Stamps the comparison into the parity"
        " record; the aborted pair's verdict is not touched.",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="SPEC amendment 3.11 (2)'s batch measurement: the candidate N against the batch-1"
        " record and the 4.5h2 anchors, the adoption rule applied as code",
    )
    parser.add_argument("--parity-record", type=Path, default=PARITY["A"])
    parser.add_argument(
        "--baseline-record",
        type=Path,
        default=PARITY["A"],
        help="--batch: the batch-1 record the rule charges the change against",
    )
    parser.add_argument("--batch-dump", type=Path, help="--batch: the candidate's per-row dump")
    parser.add_argument(
        "--baseline-dump", type=Path, help="--batch: the batch-1 per-row dump to agree with"
    )
    parser.add_argument(
        "--serving-record",
        type=Path,
        help="--batch: stamp the adopted batch and its $/1000 rows into results/serving_5b.json,"
        " which is what 5c reads",
    )
    parser.add_argument(
        "--usd-per-hour",
        type=float,
        default=0.0,
        help="--batch: the pod's posted rate, for the adopted config's $/1000 rows",
    )
    parser.add_argument(
        "--ladder-record",
        type=Path,
        help="--project: derive seconds-per-row from a batch_ladder_5b2.json arm instead of"
        " typing it. Use with --ladder-arm.",
    )
    parser.add_argument("--ladder-arm", default="", help="--project: which arm, e.g. 8")
    parser.add_argument(
        "--runs",
        type=int,
        default=2,
        help="--project: 2 for the pre-registered pair, 1 for the single-config measurement",
    )
    parser.add_argument("--projection-out", type=Path, default=PROJECTION)
    parser.add_argument(
        "--verdict-out",
        type=Path,
        default=VERDICT,
        help="where an abort lands. Defaults to the pair's verdict — point it elsewhere for a"
        " later phase, because that file is a committed decision and not a scratch pad.",
    )
    parser.add_argument(
        "--abort",
        action="store_true",
        help="the pair could not be scored at all — record SPEC's outcome and the evidence",
    )
    parser.add_argument("--blocker", default="", help="--abort: one line, what stopped it")
    parser.add_argument(
        "--evidence", action="append", default=[], help="--abort: repeatable, one fact per flag"
    )
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

    if args.single:
        return run_single(args)
    if args.batch:
        if args.serving_record and not args.usd_per_hour:
            parser.error(
                "--serving-record needs --usd-per-hour: what 5c reads is a price per thousand"
                " rows, and a price with no rate behind it is a guess in a record"
            )
        return run_batch(args)
    if args.abort:
        if not (args.blocker and args.evidence):
            parser.error(
                "--abort needs --blocker and at least one --evidence:"
                " an abort with no evidence is indistinguishable from a phase nobody ran"
            )
        return run_abort(args)
    if args.project:
        if args.smoke_record:
            for field, value in from_smoke(args.smoke_record).items():
                if getattr(args, field) in (None, 0):
                    setattr(args, field, value)
        if args.ladder_record:
            if not args.ladder_arm:
                parser.error("--ladder-record needs --ladder-arm: a ladder holds several")
            for field, value in from_ladder(args.ladder_record, args.ladder_arm).items():
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
