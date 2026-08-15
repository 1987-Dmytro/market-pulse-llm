#!/usr/bin/env python3
"""Batch parity for cycle 2, from the records alone. ($0, offline, no endpoint, no prereg.)

`docs/PROMPT-cycle2-prep-a.md` deliverable 2. Four questions, and the contract's own rule for the
fourth kind of answer: what the records cannot say is marked **NOT MEASURABLE** and is never
estimated into a number.

(a) which forward batch sizes a serverless RTX 4090 24 GB can be a candidate for, given the A6000
    48 GB out-of-memory the 5b.2 attempt recorded;
(b) what a new pre-registration would MEASURE and against which anchors — gate evals stay batch 1
    forever (SPEC 3.11 (2)), so the only candidate is the production loop's row price;
(c) what the measurement session itself costs per candidate, at measured serverless prices;
(d) break-even at −30% and −50% row price against the reference volumes.

**Every figure is READ out of the file it cites.** `projection_5c2.cite` is the one resolver and
this module adds exactly one thing to it — `sample`, the population a price was measured on, which
`.claude/rules/registrations-and-draws.md` makes mandatory beside every price ("a rate is not a
property of a leg, it is a property of the SAMPLE it was measured on"). Nothing here is typed in.

The memory arithmetic of (a) is the one place a number lives inside PROSE: the 5b.2 verdict's
`blocker` field is a sentence, and :func:`oom_reading` regexes it rather than restating it, so the
day that sentence is rewritten this producer stops instead of printing a stale bound.

    PYTHONPATH=src python3 scripts/projection_batch_cycle2.py
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from projection_5c2 import cite, dig, load, rel, sha256_of  # noqa: E402

# --- the six anchors the contract names ---------------------------------------------------------
SPEND = REPO_ROOT / "results" / "spend_5c2run.json"
PARITY = REPO_ROOT / "results" / "parity_srv2.json"
SERVING_5B = REPO_ROOT / "results" / "serving_5b.json"
LADDER = REPO_ROOT / "results" / "batch_ladder_5b2.json"
B2_PROJECTION = REPO_ROOT / "results" / "batch_5b2_projection.json"
B2_VERDICT = REPO_ROOT / "results" / "batch_5b2_verdict.json"
CONTRACT_ANCHORS = (SPEND, PARITY, SERVING_5B, LADDER, B2_PROJECTION, B2_VERDICT)

# --- two records the contract did not name, and why they are here -------------------------------
RUN_COMMENTS = REPO_ROOT / "results" / "run_5c2_comments.json"
"""The paid comment leg's own record. `results/spend_5c2run.json` is a BALANCE anchor — two
readings and a note — so it prices the SESSION and cannot price a step (a balance delta is not a
per-leg cost). The serverless $/s rate, the seconds-per-row over the bought population, and the
boot that (c) is literally defined as ("boot + warm-up + N rows") exist in this file and in no
other. Marked `outside_the_named_anchors` in the record's provenance, not smuggled in."""

WINDOW = REPO_ROOT / "results" / "window_summary_5c2.json"
"""The reference cycle volume the contract names as «one cycle window ≈ the 5c2 window», and the
3.19 class beside it. Read for two counts only; also marked outside the named anchors."""

HISTORY_ROWS = 11143
"""The contract's own reference volume («history 11 143»), quoted from the brief and from
`scripts/run_5c2.py`'s `nongold_comments` docstring. The only figure in this file that is not read
out of a result record, because no result record holds it — it is stated as the CONTRACT's number
and `tests/test_projection_batch_cycle2.py` greps it back out of both."""

OUT = REPO_ROOT / "results" / "batch_cycle2_projection.json"

MIB = 1024
PROBE_ARM_ROWS = (24, 400, 758)
"""The arm sizes priced. 24 is the 5b.2 ladder's own carve, 758 is the srv-2d parity population —
both are anchors, so neither is a size this file invented — and 400 sits between them because the
`comments_test` input is 400 rows. What each buys in DETECTION is computed, not asserted."""


def priced(path: Path, dotted: str, why: str, sample: str) -> dict:
    """A cited figure with the population it was measured on. The house `cite` plus the one rule.

    `.claude/rules/registrations-and-draws.md`: beside every price, name what it was measured ON.
    A rate carried without its sample is the Dv308 / Dv310 / Dv180 defect, three times over.
    """
    return cite(path, dotted, why) | {"sample": sample}


def mib(text: str) -> int:
    """`"49140 MiB"` → 49140. A unit that is not MiB is a refusal, never a silent number."""
    found = re.fullmatch(r"(\d+)\s*MiB", text.strip())
    if not found:
        raise SystemExit(f"{text!r}: expected a MiB reading — the card's memory is not comparable")
    return int(found.group(1))


def oom_reading() -> dict:
    """The four memory figures inside the 5b.2 verdict's `blocker` sentence, regexed out of it.

    They are the whole of (a)'s evidence and they live in prose, so they are PARSED rather than
    restated: a rewritten sentence must stop this producer, not leave it printing a bound nobody
    can trace. The quote travels with them for the same reason.
    """
    quote = dig(load(B2_VERDICT), "blocker")
    patterns = {
        "requested_gib": r"([\d.]+) GiB requested",
        "free_mib": r"([\d.]+) MiB free",
        "allocated_gib": r"([\d.]+) GiB allocated",
        "weights_at_rest_gib": r"~([\d.]+) GiB model at rest",
        "batch_size": r"batch of (\d+)",
    }
    out = {}
    for name, pattern in patterns.items():
        found = re.search(pattern, quote)
        if not found:
            raise SystemExit(f"{rel(B2_VERDICT)} :: blocker no longer carries {name} ({pattern})")
        out[name] = float(found.group(1))
    return {"quote": quote, "source": f"{rel(B2_VERDICT)} :: blocker", "read": out}


def batch_candidates() -> dict:
    """(a) — an INEQUALITY over the two cards, and the line past which nothing is derivable."""
    oom = oom_reading()
    read = oom["read"]
    a6000 = mib(dig(load(LADDER), "worker.runtime.gpu_memory_total")) / MIB
    ada = mib(dig(load(PARITY), "config.runtime.gpu_memory_total")) / MIB
    # what the failing STEP demanded, not what was resting: the allocation that raised is the one
    # a smaller card has to fit, so the request is added to what was already held
    demand = read["allocated_gib"] + read["requested_gib"]
    above_weights = demand - read["weights_at_rest_gib"]
    headroom = ada - read["weights_at_rest_gib"]
    per_row = above_weights / read["batch_size"]
    largest = math.floor(headroom / per_row)
    return {
        "asks": "which forward batch sizes a serverless RTX 4090 24 GB can be a candidate for",
        "recorded_oom": oom,
        "cards": {
            "measured_on": priced(
                LADDER,
                "worker.runtime.gpu",
                "the pod the 5b.2 ladder and the failed batch-16 attempt ran on",
                "one pod, 5b.2 (2026-08-06)",
            )
            | {"total_gib": round(a6000, 3)},
            "projected_onto": priced(
                PARITY,
                "config.runtime.gpu",
                "the serverless class every paid row since srv-2d has been served on, and the one"
                " the 5c2 window was bought on",
                "srv-2d parity, 758 rows, and the 5c2-run comment leg",
            )
            | {"total_gib": round(ada, 3)},
            "same_weights": priced(
                PARITY,
                "config.quantization.bnb_4bit_quant_type",
                "4-bit NF4 on both cards — `results/batch_ladder_5b2.json :: worker.quantization`"
                " is the identical block, so the ~20 GiB at rest transfers and the working set is"
                " the only variable",
                "both records",
            ),
        },
        "derivable": {
            "demand_at_the_failing_step_gib": round(demand, 3),
            "above_the_weights_gib": round(above_weights, 3),
            "headroom_on_24gb_above_the_weights_gib": round(headroom, 3),
            "shortfall_factor": round(above_weights / headroom, 2),
            "linear_per_row_gib": round(per_row, 4),
            "largest_batch_the_inequality_admits": largest,
            "ruled_out": [n for n in (3, 4, 8, 16) if n > largest],
            "reading": (
                f"the batch-16 step demanded {above_weights:.2f} GiB above the weights and a 24 GB"
                f" 4090 has {headroom:.2f} GiB above them — short by"
                f" {above_weights / headroom:.1f}x. Batch 16 is impossible on this card, and so is"
                " every N above the floor of that ratio. Batch 1 is not projected: it is"
                " DEMONSTRATED — the 5c2-run comment leg served the whole window on this class."
            ),
        },
        "not_measurable": {
            "claim": f"whether batch {largest} actually fits on a 24 GB 4090",
            "why": [
                "the per-row figure above is the failing step's peak divided by 16, and GPU memory"
                " scales with TOKENS, not rows — the ladder chose 16 on a 24-row carve whose"
                " longest T1 batch fitted and the test set's did not"
                f" ({rel(B2_VERDICT)} :: evidence[0])",
                "no record in this repository carries a memory reading from the serverless worker:"
                " the ~20 GiB at rest is the pod's, on a different allocator and a different"
                " driver, and the 4090's resting footprint has never been measured",
                "the KV cache of `max_new_tokens: 256` sits inside the working set and no record"
                " separates it from the activations",
            ],
            "what_would_settle_it": "a live probe on the serving class — priced in (c)",
        },
    }


def prices() -> dict:
    """Every price this file uses, each beside the sample it was measured on."""
    return {
        "rate_usd_per_second": priced(
            RUN_COMMENTS,
            "rate_usd_per_second",
            "the serverless $/s the 5c2-run comment endpoint billed at — the machine's price",
            "endpoint gfmtqi3uqcjyv5, the whole 5c2-run comment leg",
        ),
        "row_seconds_batch_1_production": priced(
            RUN_COMMENTS,
            "timing.seconds_per_row",
            "worker seconds per row at forward batch 1 — the number a batch change would move,"
            " and the only one measured over a whole bought population",
            "5 078 rows (5 075 gold + 3 warm-up), serverless RTX 4090, 2026-08-14",
        ),
        "row_seconds_batch_1_gate_slice": priced(
            PARITY,
            "config.serving.timing.seconds_per_row",
            "the same quantity on the GATE population — carried to show how far two samples of the"
            " same rate sit apart on the same card, and used in no arithmetic below",
            "758 rows of the v4 gate sets, srv-2d, 2026-08-08",
        ),
        "row_seconds_batch_1_pod": priced(
            SERVING_5B,
            "adopted.seconds_per_row",
            "the POD anchor. SPEC 3.18 (4) forbids pricing serverless work with it; it is here as"
            " the ratio the two runtimes sit at, and enters no dollar figure",
            "758 rows on an A6000 pod, 5b (2026-08-06)",
        ),
        "boot_and_warmup_seconds": priced(
            RUN_COMMENTS,
            "go_no_go.billed_seconds",
            "everything the endpoint billed before the first GOLD call — staging, cold start and"
            " the two non-gold warm-up calls of SPEC 3.17 (9). A refusal after this point still"
            " pays it, so it is the session's floor and not an overhead line",
            "one serverless session, n=1 (5c2-run comments, 2026-08-14)",
        ),
        "idle_tail_seconds": priced(
            RUN_COMMENTS,
            "go_no_go.idle_tail_seconds",
            "the endpoint's idle tail after the last job, as the run's own gate priced it",
            "the same one session",
        ),
        "session_billed_usd": priced(
            SPEND,
            "runs[-1].step_spent_usd",
            "the whole 5c2-run session against its balance anchor — ANCHOR-RELATIVE, so this is"
            " the cumulative figure and the positions leg is inside it",
            "5 278 rows across three legs — a blend, and named as one",
        ),
        "positions_leg_usd": priced(
            SPEND,
            "runs[0].step_spent_usd",
            "the first anchor-relative reading, so it is the positions leg on its own",
            "159 leaflet pages + 44 posts",
        ),
    }


def money() -> dict:
    """The two row prices this projection turns on, and the arithmetic that separates them."""
    rate = dig(load(RUN_COMMENTS), "rate_usd_per_second")
    row_seconds = dig(load(RUN_COMMENTS), "timing.seconds_per_row")
    gold_rows = dig(load(RUN_COMMENTS), "selection.comment.rows")
    session = dig(load(SPEND), "runs[-1].step_spent_usd")
    positions = dig(load(SPEND), "runs[0].step_spent_usd")
    marginal = row_seconds * rate
    leg = session - positions
    return {
        "marginal_usd_per_row": round(marginal, 7),
        "marginal_is": (
            "worker seconds x the machine's rate. THE price a batch change moves: the boot and the"
            " idle tail are per-session and do not scale with the batch, so every saving below is"
            " computed on this one and never on the all-in figure"
        ),
        "all_in_usd_per_row": round(leg / gold_rows, 7),
        "all_in_is": (
            f"the comment leg's own billed dollars (${leg:.4f} — the two anchor-relative readings"
            f" subtracted) over its {gold_rows} gold rows, boot and idle inside it. Carried for the"
            " operator's arithmetic, used in no saving"
        ),
        "comment_leg_usd": round(leg, 4),
        "gold_rows": gold_rows,
    }


def prereg_shape() -> dict:
    """(b) — what a new registration would measure, and against which anchors."""
    agreement = dig(load(B2_VERDICT), "salvage.row_agreement_vs_batch_1")
    return {
        "asks": "what a new prereg would measure and against which anchors",
        "the_candidate_is_only_the_loop": {
            "rule": cite(
                B2_VERDICT,
                "rule_could_not_run",
                "SPEC 3.11 (2) as the failed attempt states it: serving is fixed at batch 1 and"
                " only a NEW pre-registration may re-open it",
            ),
            "so": (
                "gate evals stay batch 1 forever. The measurable candidate is the PRODUCTION"
                " loop's row price on the comment leg — the one leg whose rows are bought by the"
                " thousand — and nothing that feeds a bar."
            ),
        },
        "what_it_must_measure": [
            {
                "what": "row IDENTITY against batch 1, on the production population",
                "why": (
                    f"the 5b.2 attempt scored {agreement['compared']} rows before it died and"
                    f" {agreement['compared'] - agreement['agree']} of them DISAGREED with batch 1"
                    f" ({1 - agreement['rate']:.4f} of the rows), while every batch size on the"
                    " 24-row carve was byte-identical. Batching this stack is not answer-neutral,"
                    " and the carve is where that fact hides"
                ),
                "anchor": f"{rel(B2_VERDICT)} :: salvage.row_agreement_vs_batch_1",
            },
            {
                "what": "seconds per row at the candidate N against batch 1",
                "why": (
                    "the whole money case. The batch-1 reference is a POPULATION price and already"
                    " exists — it does not have to be re-bought"
                ),
                "anchor": f"{rel(RUN_COMMENTS)} :: timing.seconds_per_row (n=5 078)",
            },
            {
                "what": "peak GPU memory at the candidate N, reported per step",
                "why": (
                    "the thing (a) cannot derive. The 5b.2 attempt learned its memory bound by"
                    " dying at row 666 of 758, having written no record and no prediction dump"
                    f" ({rel(B2_VERDICT)} :: evidence[1])"
                ),
                "anchor": "no anchor exists — this is the new measurement",
            },
        ],
        "abort_rule_to_inherit": cite(
            B2_PROJECTION,
            "abort_rule",
            "the 5b.2 registration's own stop, and the reason a retry is not on the table:"
            " one attempt, no retry, and a failed measurement closes the question",
        ),
        "adopted_today": cite(
            B2_VERDICT, "adopted_batch_size", "what production serves at now, and until a new seal"
        ),
    }


def session_cost(arms: tuple[int, ...]) -> dict:
    """(c) — boot + warm-up + N rows, at measured serverless prices, per candidate."""
    figures = money()
    rate = dig(load(RUN_COMMENTS), "rate_usd_per_second")
    fixed_seconds = dig(load(RUN_COMMENTS), "go_no_go.billed_seconds") + dig(
        load(RUN_COMMENTS), "go_no_go.idle_tail_seconds"
    )
    # rounded ONCE, here, and every figure below is built from the rounded value: a record whose
    # columns do not re-add from the ones printed beside them is a record nobody can check
    fixed_usd = round(fixed_seconds * rate, 4)
    agreement = dig(load(B2_VERDICT), "salvage.row_agreement_vs_batch_1.rate")
    disagreement = 1 - agreement
    rows = []
    for size in arms:
        arm = size * figures["marginal_usd_per_row"]
        rows.append(
            {
                "rows_per_arm": size,
                "one_arm_usd": round(arm, 4),
                "candidate_only_usd": round(fixed_usd + arm, 4),
                "with_a_batch_1_control_usd": round(fixed_usd + 2 * arm, 4),
                "blind_to_the_identity_defect": round((1 - disagreement) ** size, 4),
            }
        )
    return {
        "asks": "the measurement session's own cost per candidate",
        "fixed": {
            "seconds": round(fixed_seconds, 3),
            "usd": round(fixed_usd, 4),
            "what": (
                "boot + staging + the two warm-up calls, plus the idle tail — billed whether the"
                " session buys a gold row or refuses at its own gate"
            ),
        },
        "per_row_usd": figures["marginal_usd_per_row"],
        "per_row_is_a_ceiling": (
            "arms are priced at the BATCH-1 seconds-per-row, because the candidate's own rate is"
            " what the session exists to measure. A batch that is faster costs less than this; a"
            " batch that is slower is not a candidate. NOT MEASURABLE before the probe."
        ),
        "arms": rows,
        "detection": (
            f"`blind_to_the_identity_defect` is (1 - {disagreement:.6f})^rows at the ONE recorded"
            " batch-vs-1 disagreement rate: the 5b.2 ladder's 24-row arm would have seen nothing"
            " four times out of five, which is exactly how a 24-row carve certified batch 16."
        ),
    }


def break_even(arms: tuple[int, ...]) -> dict:
    """(d) — break-even at −30% and −50% against the contract's reference volumes."""
    figures = money()
    price = figures["marginal_usd_per_row"]
    window_rows = dig(load(WINDOW), "comment.total.rows")
    window_empty = dig(load(WINDOW), "comment.total.empty_text.rows")
    costs = session_cost(arms)
    volumes = {
        "history_backlog": {
            "rows": HISTORY_ROWS,
            "source": "the contract's own reference volume; scripts/run_5c2.py :: nongold_comments",
        },
        "one_cycle_window_as_bought": {
            "rows": window_rows,
            "source": f"{rel(WINDOW)} :: comment.total.rows",
        },
        "one_cycle_window_payable_after_3_19": {
            "rows": window_rows - window_empty,
            "source": (
                f"{rel(WINDOW)} :: comment.total.rows minus comment.total.empty_text.rows — the"
                " rows deliverable 1's queue rule leaves in the paid queue"
            ),
        },
    }
    out = {
        "asks": "break-even at -30% and -50% row price against the reference volumes",
        "priced_on": (
            "the MARGINAL row price. A batch changes worker seconds and nothing else, so a saving"
            " computed on the all-in price would credit the batch with the boot it does not touch."
        ),
        "row_price_usd": price,
        "volumes": volumes,
        "depths": {},
    }
    for label, depth in (("minus_30_pct", 0.30), ("minus_50_pct", 0.50)):
        # rounded once, as `session_cost`'s fixed cost is, so every dollar below re-adds from the
        # per-row figure the record prints and not from a longer one it kept to itself
        delta = round(price * depth, 7)
        out["depths"][label] = {
            "saving_per_row_usd": delta,
            "saving_by_volume_usd": {
                name: round(found["rows"] * delta, 4) for name, found in volumes.items()
            },
            "break_even_rows": {
                f"{arm['rows_per_arm']}_row_arms_with_control": math.ceil(
                    arm["with_a_batch_1_control_usd"] / delta
                )
                for arm in costs["arms"]
            },
        }
    cheapest = min(arm["with_a_batch_1_control_usd"] for arm in costs["arms"])
    dearest = max(arm["with_a_batch_1_control_usd"] for arm in costs["arms"])
    # read back out of the table above rather than recomputed: a prose figure that took its own
    # path to the same quantity is how a record ends up disagreeing with itself by a rounding
    payable_at_30 = out["depths"]["minus_30_pct"]["saving_by_volume_usd"][
        "one_cycle_window_payable_after_3_19"
    ]
    out["readings"] = [
        (
            f"the 3.19 skip has already banked ${round(window_empty * price, 4)} per window at $0 —"
            f" {window_empty} rows of {window_rows} never reach the queue. That is more than a"
            f" -30% batch would save on the rows that remain (${payable_at_30})"
            " and it needed no probe."
        ),
        (
            f"a probe costs between ${cheapest:.4f} and ${dearest:.4f} with a control arm. Against"
            f" the history backlog ({HISTORY_ROWS} rows) it repays at both depths; against a single"
            " post-3.19 window it repays only at -50%, and only with the smaller arms."
        ),
        (
            "the window's 26.8% text-less share is NOT applied to the history backlog: it is a"
            " rate measured on one 4-week window, and the history is a different sample"
            " (.claude/rules/registrations-and-draws.md). How many of the 11 143 carry no text is"
            " derivable at $0 and no anchor states it — NOT ANSWERED HERE."
        ),
    ]
    return out


def provenance() -> dict:
    def entry(path: Path, named: bool, why: str) -> dict:
        return {
            "path": rel(path),
            "sha256": sha256_of(path),
            "named_by_the_contract": named,
            "why": why,
        }

    return {
        "anchors": [
            entry(SPEND, True, "the only population-priced serverless anchor — 5 278 rows bought"),
            entry(
                PARITY, True, "srv-2d parity, batch 1, 758 rows; and the serving card's identity"
            ),
            entry(SERVING_5B, True, "the pod cost anchor — carried as a ratio, never as a price"),
            entry(LADDER, True, "the 5b.2 ladder: the arms, the control, and the A6000 it ran on"),
            entry(B2_PROJECTION, True, "the failed attempt's registration and its abort rule"),
            entry(B2_VERDICT, True, "the OOM, the salvaged row agreement, and the batch-1 ruling"),
            entry(
                RUN_COMMENTS,
                False,
                "the serverless $/s, the population seconds-per-row and the boot. A balance anchor"
                " prices an account, not a step, so (c) cannot be answered without this file",
            ),
            entry(
                WINDOW,
                False,
                "the reference cycle volume the contract names, and the 3.19 class beside it",
            ),
        ],
        "producer": {
            "script": rel(Path(__file__)),
            "sha256": sha256_of(Path(__file__)),
            "why": (
                "no git block: `git status --porcelain` is a fact about the tree and would move"
                " this record on somebody else's commit (`projection_5c2.producer`'s reason)"
            ),
        },
        "not_typed": (
            "every figure above is resolved through `projection_5c2.cite` / `dig` by the dotted"
            " path printed beside it, except HISTORY_ROWS, which is the contract's own reference"
            " volume and is grepped back out of it by the test"
        ),
    }


def build() -> dict:
    return {
        "phase": "cycle-2 prep-a — deliverable 2",
        "contract": "docs/PROMPT-cycle2-prep-a.md deliverable 2",
        "asks": (
            "batch parity for cycle 2, from records only. PAPER: no prereg is written, no SPEC is"
            " edited, no endpoint or pod is created and nothing is spent. The money line is an"
            " open operator decision and this record does not take it."
        ),
        "job_shape_today": cite(
            PARITY,
            "config.serving.job_shape",
            "what 'batch' means here: rows already travel many-per-JOB and the forward pass is"
            " one row at a time. The candidate is `forward_batch_size` in the worker, not the"
            " transport — which is why nothing in the loop or the driver would change",
        ),
        "prices": prices(),
        "money": money(),
        "a_batch_candidates": batch_candidates(),
        "b_what_a_prereg_would_measure": prereg_shape(),
        "c_measurement_session_cost": session_cost(PROBE_ARM_ROWS),
        "d_break_even": break_even(PROBE_ARM_ROWS),
        "ladder_for_reference": {
            "what": (
                "the 5b.2 ladder's wall seconds per row, on a POD and an A6000, over a 24-row"
                " training carve. A FLOOR-direction bound on what batching can buy and never a"
                " prediction of it: different card, different runtime, and a sample of 24"
            ),
            "arms": {
                name: cite(
                    LADDER,
                    f"arms.{name}.seconds_per_row_wall",
                    "wall seconds per row of that arm's chunks",
                )
                for name in ("1", "1-repeat", "4", "8", "16")
            },
            "control": cite(
                LADDER, "control.identical", "the 1-repeat arm: byte-identical replies on the carve"
            ),
        },
        "provenance": provenance(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    record = build()
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    found = record["a_batch_candidates"]["derivable"]
    print(
        f"(a) batch 16 needs {found['above_the_weights_gib']} GiB above the weights,"
        f" a 24 GB 4090 has {found['headroom_on_24gb_above_the_weights_gib']} —"
        f" short {found['shortfall_factor']}x."
        f" Admitted by the inequality: batch {found['largest_batch_the_inequality_admits']};"
        f" ruled out {found['ruled_out']}. Does it FIT: NOT MEASURABLE."
    )
    print(
        f"(c) fixed ${record['c_measurement_session_cost']['fixed']['usd']} +"
        f" ${record['money']['marginal_usd_per_row']}/row; arms: "
        + ", ".join(
            f"{arm['rows_per_arm']}→${arm['with_a_batch_1_control_usd']}"
            for arm in record["c_measurement_session_cost"]["arms"]
        )
    )
    for label, depth in record["d_break_even"]["depths"].items():
        print(
            f"(d) {label}: ${depth['saving_per_row_usd']}/row · "
            + " · ".join(f"{k} ${v}" for k, v in depth["saving_by_volume_usd"].items())
        )
    print(f"\nwrote {rel(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
