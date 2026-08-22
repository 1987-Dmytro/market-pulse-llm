#!/usr/bin/env python3
"""`results/prereg_pass2_signals_r2.json` — the law of the ONE paid session of `pass2-signals-r2`.

Every threshold this contract acts on is written HERE and nowhere else, and the H6 block at the
bottom re-derives every number `docs/PROMPT-pass2-signals-r2.md` prints, from the file it comes out
of. A mismatch is a REFUSAL: `main` exits non-zero and nothing is written, which is the step-1 gate
the executor's instruction asks for ([[preregistration_is_a_file_not_a_constant]]).

**r2 has a rate and r1 did not, so there is no go/no-go.** r1 bought the measurement: five pass-2
calls at 15.801 … 58.07 s on one pod. The operator's ruling (з) charges the remainder at the
smoke's MAXIMUM times the measured pod-class spread — `58.07 × 1.67 = 96.98 → 97 s/thread` — and
rungs 4 and 5 cover the run the way they cover any single-leg run. What that buys is one leg, one
out-file and one decision, taken before the create instead of in the middle of it.

**Four replies are carried and not re-bought.** `results/pass2_signals_r2_v1.jsonl` is seeded with
r1's four parsed replies before the pod exists, so the leg owes 75 of 79. Every rate this record
measures excludes them by construction — they belong to another pod
([[a_rate_is_a_property_of_the_pod]]).

    PYTHONPATH=src python3.11 scripts/write_pass2_prereg_r2.py
    PYTHONPATH=src python3.11 scripts/write_pass2_prereg_r2.py --out /tmp/again.json   # the pair
"""

import json
import math
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import window_summary_5c2 as summary  # noqa: E402
import write_pass2_prereg as r1producer  # noqa: E402

from market_pulse import pass2, pass2_r2, prompts  # noqa: E402

RESULTS = REPO_ROOT / "results"
OUT = RESULTS / "prereg_pass2_signals_r2.json"
PACK = RESULTS / "pass2_r2_pack.json"
R1_PREREG = RESULTS / "prereg_pass2_signals.json"
R1_OUT = RESULTS / "pass2_signals_v1.jsonl"
GOLD = RESULTS / "reader_gold_w1_r2.json"
V5B_VERDICT = RESULTS / "reader_v5b_verdict.json"
V5B_ROWS = RESULTS / "reader_v5b_w1.jsonl"
V5B_PACK = RESULTS / "reader_v5b_pack.json"

PHASE = "pass2-signals-r2"
LEG = "r2"
OUT_FILE = "pass2_signals_r2_v1.jsonl"

RATE_FILES = {
    "pass1-probe-b, base v1, 64 rows": "pass1_probe_b_pod.jsonl",
    "pass1-fewshot r2, base v1, 200 dev rows": "pass1_dev_base.jsonl",
    "pass1-fewshot r2, v2, 200 dev rows": "pass1_dev_v2.jsonl",
    "pass1-window r1, v2, 131 window rows": "pass1_window_v2.jsonl",
    "pass1-window r2, v2, 901 window rows": "pass1_window_r2_v2.jsonl",
}
V2_RATE_FILES = (
    "pass1_dev_v2.jsonl",
    "pass1_window_v2.jsonl",
    "pass1_window_r2_v2.jsonl",
)
"""The three v2 readings the pod-class spread is measured over — three pods, one prompt. Named as
FILES and not as numbers, because a spread quoted from a report is a spread nobody can re-derive
([[trace_the_producer_not_the_result]])."""

# ---------------------------------------------------------------------------------------------
# the constants of this registration. Each is typed ONCE, here, with the derivation that produced
# it; everything below is computed. H6 re-derives every one that has a file behind it.
# ---------------------------------------------------------------------------------------------

CAP_USD = 2.50
"""The operator's ruling (з) of 2026-08-22 (day): buy the remaining 75 threads under a new
registration at a cap of $2.50, the rate charged on the smoke's MAX × the pod-class spread. The
alternatives — a $2.00 cap with the row-weighted arm, and a stop into LoRA — were rejected."""

HARD_STOP_SECONDS = 11_000.0
"""Cumulative billed seconds, platform-held. $2.4444 at the price ceiling, under the $2.50 cap it
defends, and above the 9 675 s worst case by 1 325 s — which is exactly the widest dead pod the
recovery clause can afford."""

PRICE_CEILING_USD_PER_HOUR = 0.80
MEASURED_PRICE_USD_PER_HOUR = 0.53
"""The two prices the worst case is quoted at: the ceiling rung 1 refuses above, and the cheapest
card this line has actually rented (RTX A6000, `docs/reports/lora-b-run.md`). The 4090 24 GB every
pod of this contract's lineage has landed on is $0.74 and sits between them."""

SMOKE_MAX_SECONDS = 58.07
"""r1's slowest pass-2 call — `@VARUS_channel:10613`, the F1 thread, 3 252 emitted characters.
Re-derived from `results/pass2_signals_v1.jsonl` by H6 and never typed anywhere else."""

POD_CLASS_SPREAD = 1.67
"""v2's measured pod-class spread on pass 1: 2.694083 s/call on `fnlktbelhkmte5` against 4.498473 on
`xpz3zb7yxus5cw`, three pods and one prompt. Rounded to two places from 1.669656, and the rounding
direction does not reach the charge — 58.07 × 1.669656 = 96.96 and 58.07 × 1.67 = 96.98 both ceil to
97 ([[two_values_for_one_input_get_quoted_kindly]]).

The BASE prompt's own two-point spread is 2.2509 (5.161578 / 2.293075) and it is the wider reading
this registration does NOT charge — named here so a reader can see which of the two was taken."""

SECONDS_PER_CALL = float(math.ceil(SMOKE_MAX_SECONDS * POD_CLASS_SPREAD))
"""97 s/thread — `ceil(58.07 × 1.67) = ceil(96.9769)`.

**The MAX and not a row-weighted mean.** The population's widest unit carries 26 filtered rows
(`@klopotenkofood:6040`) against the smoke's widest 10 (`@VARUS_channel:10613`), so a fit over the
five smoke points would extrapolate 2.6× beyond its own range on the very units most likely to be
slow. The maximum is the only reading that covers that tail without a model of it, and r1's own
row-weighted arm — which said GO where the flat arm said STOP — is exactly the arm this registration
declines to bet on ([[a_smoke_drawn_from_the_exam_is_not_a_rate_sample]] read the other way: a
sample chosen for richness is safe as a BOUND and wrong as a ratio)."""

SSH_SECONDS = 500.0
STAGE_LAUNCH_SECONDS = 150.0
LOAD_SECONDS = 450.0
"""Pre-generation, charged once, unmoved from r1: the ssh spread over six readings runs 14.5 → 262.5
and the boot over eight runs 139.5 → 353. r1's own pod MEASURED 135 s of pre-generation against the
1 100 charged; the charge is the maximum of the readings and not the last one."""

OVERHEAD_SECONDS = 1300.0
BACKSTOP_TOLERANCE_SECONDS = 60.0
SSH_DEADMAN_SECONDS = 500.0
LAUNCH_TO_FIRST_REPLY_SECONDS = 450.0
BOOT_BACKSTOP_SECONDS = 1100.0
LIVENESS_SECONDS = 600.0
PROJECTION_EVERY_CALLS = 20

DELETION_TAIL_SECONDS = 78.5
"""The worse of the two deletion tails r1's window lineage measured (78.5 s and 0.1 s). The meter
stops at `pod delete` and not when a rung fires, so a rung-2 death bills 578.5 s and not 500
([[a_ceiling_derived_from_one_span_measured_over_another]], Dv631)."""

MEASURED_PRE_GENERATION_SECONDS = 135.0
"""What r1's pod actually took — ssh 38 + stage/clone 97 — published beside every span the budget
CHARGES, because r1's own knife edge was quoted at a span the pod never spent (Dv703, Dv668)."""

REFUSALS_FRACTION = 0.174
"""v5b's measured refusal rate through the same parser after the same repairs: 4 of 23 leg-A
threads. Carried from r1 — and r2's tolerant reader should push the realised rate well below it,
which is a MEASUREMENT this run takes and not a bar it lowers."""

R1_CLOCK_USD = 0.108122
SIGNAL_LAYER_PASS_1_USD = 0.742055
ONE_SHOT_READER_USD = 0.312592

# ---------------------------------------------------------------------------------------------


def pack() -> dict:
    return json.loads(summary.read_text_or_refuse(PACK))


def gold() -> dict:
    return json.loads(summary.read_text_or_refuse(GOLD))


def rows(path: Path) -> list[dict]:
    return [
        json.loads(one) for one in summary.read_text_or_refuse(path).splitlines() if one.strip()
    ]


def rate_of(name: str) -> float:
    """One out-file's mean s/call, re-derived from its own rows."""
    return statistics.mean(float(one["seconds"]) for one in rows(RESULTS / name))


def pod_class_spread() -> dict:
    """The v2 spread, three files, three pods — and the base's two-point spread beside it."""
    measured = {name: round(rate_of(name), 6) for name in RATE_FILES.values()}
    v2 = [measured[name] for name in V2_RATE_FILES]
    base = [measured["pass1_probe_b_pod.jsonl"], measured["pass1_dev_base.jsonl"]]
    return {
        "per_file": {label: measured[name] for label, name in RATE_FILES.items()},
        "v2_readings": v2,
        "v2_min": min(v2),
        "v2_max": max(v2),
        "v2_spread": round(max(v2) / min(v2), 6),
        "v2_spread_registered": POD_CLASS_SPREAD,
        "base_spread": round(max(base) / min(base), 6),
        "base_spread_rule": (
            "the wider reading — 2.2509 on ONE prompt over two pods — and the one the ruling did"
            " NOT charge. Named so a reader can see which of the two was taken and how much room"
            " the other one would have wanted"
        ),
        "rule": (
            "each rate is the mean of its out-file's own `seconds`, re-derived here and never read"
            " out of a report. The spread is max/min over the THREE v2 readings — one prompt, three"
            " pods — and it is what turns one pod's measured maximum into a charge for another's"
        ),
    }


def smoke_seconds() -> dict:
    """r1's five paid calls, off r1's own out-file. The only measured pass-2 decode that exists."""
    r1 = rows(R1_OUT)
    seconds = [float(one["seconds"]) for one in r1]
    return {
        "record": summary.rel(R1_OUT),
        "sha256": summary.sha256_of(R1_OUT),
        "per_thread": {one["id"]: float(one["seconds"]) for one in r1},
        "seconds": seconds,
        "mean": round(statistics.mean(seconds), 4),
        "max": max(seconds),
        "min": min(seconds),
        "pod_id": "9rquj8p0lelct3",
        "card": "RTX 4090 24 GB, EU-RO-1, $0.74/h",
        "rule": (
            "ONE pod, five threads, greedy decoding. The MAX is what this registration charges; the"
            " mean is published beside it and gates nothing"
        ),
    }


def population(held: dict) -> dict:
    items = held["legs"][0]["items"]
    widest_rows = max(items, key=lambda one: len(one["comments"]))
    widest_chars = max(items, key=lambda one: sum(len(row["text"]) for row in one["comments"]))
    carried = held["carried"]["ids"]
    owed = held["owed"]["ids"]
    smoke_ids = set(carried) | {held["owed"]["re_asked_after_a_refusal"]}
    return {
        "units": len(items),
        "unit": "one THREAD",
        "out_file": OUT_FILE,
        "out_file_rule": (
            "the ONE out-file. `gate_pass1_window.first_reply_after_launch` reads rung 3's"
            " reading out of the leg this record NAMES — a scan of the run directory is what let"
            " Dv620 take a minimum across two legs"
        ),
        "sha256": summary.sha256_of(PACK),
        "sha256_rule": (
            "the PACK's own sha. `gate_pass1_window.main` subscripts `record.population.sha256`"
            " before every rung that reads a pack and a record without it raises `KeyError` inside"
            " `--watch`, on a pod that is already billing. Found by driving the COMMAND"
            " ([[the_entry_points_preamble_is_untested_code]])"
        ),
        "payable_comments": len(items),
        "payable_comments_is_the_UNIT_count": held["population"][
            "payable_comments_is_the_UNIT_count"
        ],
        "carried_units": len(carried),
        "carried_ids": carried,
        "owed_units": len(owed),
        "owed_ids": owed,
        "re_asked_after_a_refusal": held["owed"]["re_asked_after_a_refusal"],
        "filtered_rows": held["population"]["filtered_rows"],
        "filtered_chars": held["population"]["filtered_chars"],
        "widest_unit_rows": len(widest_rows["comments"]),
        "widest_unit": widest_rows["id"],
        "widest_unit_chars": sum(len(one["text"]) for one in widest_chars["comments"]),
        "widest_unit_by_chars": widest_chars["id"],
        "widest_smoke_unit_rows": max(
            len(one["comments"]) for one in items if one["id"] in smoke_ids
        ),
        "widest_smoke_units_at_the_maximum": sum(
            1
            for one in items
            if one["id"] in smoke_ids
            and len(one["comments"])
            == max(len(x["comments"]) for x in items if x["id"] in smoke_ids)
        ),
        "widest_smoke_units": sorted(
            one["id"]
            for one in items
            if one["id"] in smoke_ids
            and len(one["comments"])
            == max(len(x["comments"]) for x in items if x["id"] in smoke_ids)
        ),
        "rows_per_thread_population": round(held["population"]["filtered_rows"] / len(items), 3),
        "rows_per_thread_smoke": round(
            sum(len(one["comments"]) for one in items if one["id"] in smoke_ids) / len(smoke_ids), 3
        ),
        "derived_from": held["population"]["derived_from"],
        "rule": (
            "r1's 79 units, r1's order, r1's renderings — checked at build time by re-rendering"
            " every one of them. r2 does not re-derive the population and does not re-buy the four"
            " threads whose replies parsed"
        ),
    }


def bars(held: dict, reach: dict) -> dict:
    """r1's bars, one arm. Everything that is not about the arm is r1's own text, unmoved."""
    units = len(held["legs"][0]["items"])
    inherited = r1producer.bars(
        json.loads(summary.read_text_or_refuse(RESULTS / "pass2_pack.json")), reach
    )
    noise_called = reach["noise_threads_pass_2_calls"]
    scored_noise = [one for one in noise_called if one != "N1"]
    one_arm = (
        "ONE arm. r1's bars carried a GO arm and a STOP arm because rung S′ could stop the run at"
        " five units; r2 has no go/no-go, so every bar is scored over the whole population or the"
        " run did not finish and rung 7 is RED. The four carried rows are part of that population"
        " and their replies are the ones r1 bought"
    )
    no_stop_arm = (
        "REPEALED WITH THE RUNG. r1's clause here described what this bar reports under a rung-S′"
        " STOP; r2 abolished that rung — `gate_pass2_signals_r2.main` raises on `--go-no-go` — and"
        " `arm_rule` says nothing can select a second arm. What replaces it: if the pod dies before"
        " the leg is answered, rung 7 is RED and every bar is UNSCORED with the threads it never"
        " read named beside it. Carrying r1's sentence forward would put a clause about a rung that"
        " does not exist into this run's own verdict"
        " ([[an_audit_of_pins_is_not_an_audit_of_thresholds]])"
    )
    return {
        "1_flagships": {
            **inherited["1_flagships"],
            "one_arm": one_arm,
            "scored_over_all_79": True,
            "F2_is_read_this_time": (
                "r1 answered F2 and its parser refused the reply on `per_comment.note`, so bar 1"
                " was UNSCORED. r2 re-asks the thread and its parser cannot be refused by that"
                " field — so F2 will be READ, and it is still expected RED by construction:"
                " strict authority forbids the `молочный_бренд` signal the gold reads from a row"
                " pass 1 labelled `сеть_ритейлер`. Say that beside the verdict"
            ),
        },
        "2_entity_cases": {
            **inherited["2_entity_cases"],
            "one_arm": one_arm,
            "under_a_STOP": no_stop_arm,
            "computed": r1producer.bar_two_at_zero(held),
        },
        "3_noise": {
            **inherited["3_noise"],
            "one_arm": one_arm,
            "under_a_STOP": no_stop_arm,
            "scored_over": scored_noise,
            "N2_is_bought_this_time": (
                "@VARUS_channel:10366 is one of the 75 owed, so bar 3 has a case in the evidence"
                " for the first time. Its four `сеть_ритейлер` rows in a plus-spam thread are the"
                " mention-vs-about confusion arriving as pass 2's own question"
            ),
        },
        "completeness": {
            "rule": (
                "answered N / N · every row's `rendering_sha256` equals its pack item's ·"
                f" UNREADABLE replies ≤ {REFUSALS_FRACTION:.1%} of N (ceil), relabellings excluded ·"
                " no unknown id and no duplicate · **and the rows carrying `carried_from` are"
                " exactly the four the pack names as carried**. All FIVE, or RED"
            ),
            "the_fifth_condition": (
                "registered here because a bar may not go RED for a reason the record does not"
                " carry. A row without `carried_from` for a thread the pack calls carried means the"
                " SEED never reached the pod and those threads were RE-BOUGHT — the one thing the"
                " DO NOT names in as many words — and the count would otherwise be attributed to r1"
                " ([[a_registered_bar_may_have_no_producer]] read forwards: the producer exists, so"
                " the bar is registered)"
            ),
            "arms": {
                "GO": {
                    "owed": units,
                    "answered_minimum": units,
                    "parse_refusals_maximum": math.ceil(units * REFUSALS_FRACTION),
                    "sha_mismatches_maximum": 0,
                }
            },
            "arm_rule": (
                "one arm. There is no rung whose verdict could choose another, and a record with a"
                " second arm nothing selects would be a bar that reads its own arm off a field no"
                " instrument writes"
            ),
            "carried_rows_count_as_answered": (
                f"the {len(held['carried']['ids'])} carried rows are ANSWERED — they are in the"
                " out-file with their shas before the pod starts, and rung 7 re-parses them with"
                " r2's parser like any other row. What they are not is BOUGHT by this pod, and no"
                " rate this record measures includes their seconds"
            ),
            "answered_means": (
                "a reply is in the out-file, counted by DISTINCT id. A parse refusal is an ANSWERED"
                " row whose reply the parser refused — the two counts are NOT disjoint"
                " ([[measure_on_the_rows_the_gate_scores]])"
            ),
            "parse_refusals_fraction": REFUSALS_FRACTION,
            "parse_refusals_fraction_rule": (
                "v5b's 4 of 23 through the same parser after the same repairs, carried from r1."
                " r2's tolerant reader removes the whole class of refusal that fired in r1, so the"
                " realised rate should come in far under this. The bar is NOT lowered for that: a"
                " budget is a transport allowance and tightening it because the parser improved"
                " would price a hope"
            ),
            "relabellings_are_outside_the_budget": inherited["completeness"][
                "relabellings_are_outside_the_budget"
            ],
            "refusal_set_is_closed": list(pass2_r2.REFUSALS),
            "report_only_fields_cannot_refuse": sorted(pass2_r2.REPORT_ONLY_FIELDS),
            "scored_fields": pass2_r2.SCORED_FIELDS,
            "what_this_bar_is": inherited["completeness"]["what_this_bar_is"],
            "refusals_are_counted_by_cause": inherited["completeness"][
                "refusals_are_counted_by_cause"
            ],
            "sha_rule": inherited["completeness"]["sha_rule"],
        },
        "report_only": {
            **inherited["report_only"],
            "the_unreadable_field_table": (
                "NEW in r2, and it is the measurement Dv702 bought: every report-only field the"
                " tolerant reader could not read, by field and by thread. In r1 that table did not"
                " exist because the first such field killed the whole reply"
            ),
            "the_cost_of_the_signal_layer": (
                f"pass 1 ${SIGNAL_LAYER_PASS_1_USD} + pass 2 r1 ${R1_CLOCK_USD} + this step, beside"
                f" v5b's ${ONE_SHOT_READER_USD}. r1's sentence said «pass 1 + this step» and meant"
                " ITS step; inherited unchanged it would drop the $0.108122 r1 spent, which is the"
                " leg D2 is required to report"
            ),
            "the_comparison_row": (
                "v5b (bar-1 2/5, $0.312592, 23 threads) vs pass 2 over 79 threads at pass 1"
                f" ${SIGNAL_LAYER_PASS_1_USD} + r1 ${R1_CLOCK_USD} + r2's spend"
            ),
        },
    }


def kill_clock(people: dict) -> list[dict]:
    owed = people["owed_units"]
    pre_generation = SSH_SECONDS + STAGE_LAUNCH_SECONDS + LOAD_SECONDS
    knife = (HARD_STOP_SECONDS - OVERHEAD_SECONDS - pre_generation) / owed
    knife_measured = (HARD_STOP_SECONDS - OVERHEAD_SECONDS - MEASURED_PRE_GENERATION_SECONDS) / owed
    return [
        {
            "rung": 1,
            "name": "price",
            "deadline_seconds": None,
            "rule": (
                f"live price > ${PRICE_CEILING_USD_PER_HOUR}/h at create → STOP, no endpoint. The"
                " backstop stamp is checked against the cumulative hard stop in the same command"
            ),
            "read": "`--price` refuses to record a pod above the ceiling",
            "before": "the first billed second",
        },
        {
            "rung": 2,
            "name": "ssh dead-man",
            "deadline_seconds": SSH_DEADMAN_SECONDS,
            "rule": (
                "the ssh endpoint has to answer inside this pod's create-elapsed deadline or KILL."
                " Unmoved: six readings run 14.5 → 262.5 and two pods of 2026-08-20 were still"
                " unreachable past 230 s"
            ),
            "read": "`--gate0 [--ssh-ok]`",
            "before": "staging",
        },
        {
            "rung": 3,
            "name": "launch → first reply",
            "deadline_seconds": LAUNCH_TO_FIRST_REPLY_SECONDS,
            "anchor": "the runner's own `pass2_signals_r2_launched_at`, copied back by --watch",
            "backstop_seconds": BOOT_BACKSTOP_SECONDS,
            "backstop_rule": (
                "create-anchored, and it equals the charged pre-generation. Without an anchor there"
                " is no GO: a rung whose deadline cannot be demonstrated has not been passed"
            ),
            "rule": (
                "the first NEW reply has to land inside this many seconds of the runner's OWN"
                " launch stamp, or KILL. The four carried rows are in the out-file before the pod"
                " starts and are not a first reply — the gate counts rows that are not carried"
            ),
            "read": "`--boot`, and every poll of `--watch` while no NEW row has landed",
            "before": "the first bought reply",
        },
        {
            "rung": 4,
            "name": "projection",
            "deadline_seconds": None,
            "rule": (
                f"projection gate every {PROJECTION_EVERY_CALLS} calls — a FLOOR; the gate runs it"
                " on every poll because it is a local computation and costs nothing. The projected"
                " attempt total at MEASURED rates, with the leg's remaining calls priced at"
                " max(mean, last call), against BOTH the cap and the cumulative hard stop"
            ),
            "this_is_the_rate_rung": (
                "no separate rate rung is added and there is no go/no-go. Rung 4 re-prices the"
                " remainder on every poll and kills a pod that cannot finish inside the stop at the"
                " first poll that shows it"
            ),
            "the_measured_rate_excludes_the_carried_rows": (
                "their seconds were spent on pod `9rquj8p0lelct3` in r1's session. A projection"
                " that averaged them into this pod's rate would report a number no pod ever ran at"
                " ([[a_rate_is_a_property_of_the_pod]])"
            ),
            "knife_edge_seconds_per_call": round(knife, 4),
            "knife_edge_formula": (
                f"({HARD_STOP_SECONDS:.0f} − {OVERHEAD_SECONDS:.0f} − pre_generation) / {owed}"
            ),
            "knife_edge_at_the_charged_spans": round(knife, 4),
            "knife_edge_at_the_measured_pre_generation": round(knife_measured, 4),
            "the_band_and_why_both_ends_are_published": (
                f"at the CHARGED pre-generation ({pre_generation:.0f} s) the edge is"
                f" {knife:.1f} s/thread and at the one r1's pod MEASURED"
                f" ({MEASURED_PRE_GENERATION_SECONDS:.0f} s) it is {knife_measured:.1f}. Both are"
                f" far above the {SECONDS_PER_CALL:.0f} charged and above"
                f" {SMOKE_MAX_SECONDS}, the slowest pass-2 call ever measured. The gate uses"
                " NEITHER: it projects from the clock at the moment it polls, so whatever the"
                " pre-generation actually cost is already inside the number that decides. These two"
                " are the band a reader should have in front of them and neither is a threshold"
                " ([[a_registered_threshold_that_is_really_a_function]])"
            ),
            "read": "every poll of `--watch`, and `--projection` on demand",
            "before": "every call after the first reply",
        },
        {
            "rung": 5,
            "name": "liveness",
            "deadline_seconds": LIVENESS_SECONDS,
            "rule": (
                "no new answered row AND no new pod-log line for this many seconds → KILL. The"
                " deadline is measured from the LAST EVENT and never from create, and an event is a"
                " RISE: a failed scp can shorten a local file and a drop is never work"
            ),
            "the_event_is_a_log_line_too": (
                "a pass-2 call takes up to a minute, so the liveness event is the pod LOG line the"
                " runner prints per call beside a new out-file row. `reader_v5_pod_runner.run`"
                " prints one per reply — asserted by test"
            ),
            "read": "`--watch`",
            "before": "a pod that has stopped working outliving its usefulness",
        },
        {
            "rung": 6,
            "name": "cumulative hard stop",
            "deadline_seconds": HARD_STOP_SECONDS,
            "rule": (
                "cumulative billed seconds, PLATFORM-held. Each pod's `--terminate-after` is its"
                " own create plus what the stop has left, and the overshoot it forgives is"
                f" {BACKSTOP_TOLERANCE_SECONDS:.0f} s"
            ),
            "read": "`--price` checks the stamp; the platform enforces it",
            "before": "a hung call no gate can see",
        },
        {
            "rung": 7,
            "name": "completeness",
            "deadline_seconds": None,
            "rule": (
                "answered 79 / 79 · every row's `rendering_sha256` equals its pack item's ·"
                f" UNREADABLE replies ≤ {REFUSALS_FRACTION:.1%} of 79 (ceil) —"
                f" {math.ceil(people['units'] * REFUSALS_FRACTION)} — relabellings excluded and"
                " counted by cause. All three, or RED"
            ),
            "read": "`--completeness` on the Mac, after the pod is deleted",
            "on_red": (
                "the out-file goes back to the team lead WITH its refusals by cause. Nothing"
                " already bought is deleted and nothing is re-asked without a new registration"
            ),
            "before": "the report",
        },
    ]


def arithmetic(people: dict) -> dict:
    owed = people["owed_units"]
    pre_generation = SSH_SECONDS + STAGE_LAUNCH_SECONDS + LOAD_SECONDS
    generation = owed * SECONDS_PER_CALL
    total = generation + pre_generation + OVERHEAD_SECONDS
    dead_pod = SSH_DEADMAN_SECONDS
    dead_pod_billed = SSH_DEADMAN_SECONDS + DELETION_TAIL_SECONDS
    return {
        "calls": {LEG: owed},
        "carried": people["carried_units"],
        "seconds_per_call": {
            LEG: SECONDS_PER_CALL,
            "rule": (
                "the registered charge AND the floor the projection uses before this pod has a"
                " reply of its own. It is a MEASURED rate scaled by a MEASURED spread, which is the"
                " first time this contract's lineage has had one for pass 2"
            ),
            "formula": (
                f"ceil(smoke_max × pod_class_spread) = ceil({SMOKE_MAX_SECONDS} ×"
                f" {POD_CLASS_SPREAD}) = ceil({SMOKE_MAX_SECONDS * POD_CLASS_SPREAD:.4f}) ="
                f" {SECONDS_PER_CALL:.0f}"
            ),
            "smoke": smoke_seconds(),
            "pod_class_spread": pod_class_spread(),
            "why_the_max": (
                "the population's widest unit is 26 filtered rows against the smoke's widest EIGHT"
                " — the contract prints 10 and the pack does not carry it — so a row-weighted fit"
                " over the five smoke points extrapolates 3.25× beyond its own range on exactly the"
                " units most likely to be slow. The maximum covers the heavy tail without a model"
                " of it. r1's row-weighted arm predicted 27.485 s/call and would have said GO; this"
                " registration declines to bet on it and says so"
            ),
        },
        "generation_seconds": generation,
        "pre_generation_seconds": pre_generation,
        "pre_generation_rule": (
            f"ssh {SSH_SECONDS:.0f} + stage/launch {STAGE_LAUNCH_SECONDS:.0f} + load"
            f" {LOAD_SECONDS:.0f}. Charged ONCE. r1's pod measured"
            f" {MEASURED_PRE_GENERATION_SECONDS:.0f} against it"
        ),
        "overhead_seconds": OVERHEAD_SECONDS,
        "overhead_rule": (
            "the watch tail, the copy-backs and the deletion tail. Rung 4 prices the attempt with"
            " it on every poll, so a second copy would be a second budget; H6 asserts the"
            " projection gate carries this same number"
        ),
        "total_seconds": total,
        "total_seconds_rule": (
            f"**the WHOLE run, all in** — {owed} × {SECONDS_PER_CALL:.0f} + {pre_generation:.0f} +"
            f" {OVERHEAD_SECONDS:.0f} = {total:.0f} s. Unlike r1's, this number authorises the"
            " whole population: the rate is registered, so rung 0 authorises a create against what"
            " the run actually costs and no rung in the middle has to re-decide it"
        ),
        "hours": round(total / 3600, 4),
        "worst_case_usd_at_the_price_ceiling": round(total / 3600 * PRICE_CEILING_USD_PER_HOUR, 6),
        "worst_case_usd_at_the_cheapest_measured_price": round(
            total / 3600 * MEASURED_PRICE_USD_PER_HOUR, 6
        ),
        "worst_case_usd_at_the_card_this_line_lands_on": round(total / 3600 * 0.74, 6),
        "cumulative": {
            "hard_stop_seconds": HARD_STOP_SECONDS,
            "hard_stop_hours": round(HARD_STOP_SECONDS / 3600, 4),
            "hard_stop_usd_at_the_price_ceiling": round(
                HARD_STOP_SECONDS / 3600 * PRICE_CEILING_USD_PER_HOUR, 4
            ),
            "hard_stop_rule": (
                f"cumulative billed ≤ {HARD_STOP_SECONDS:.0f} s ="
                f" ${HARD_STOP_SECONDS / 3600 * PRICE_CEILING_USD_PER_HOUR:.4f} at the"
                f" ${PRICE_CEILING_USD_PER_HOUR}/h ceiling. It sits UNDER the ${CAP_USD:.2f} cap it"
                " defends and it is the PLATFORM that enforces it, so it protects even a hung call"
                " no gate can see"
            ),
            "session_ceiling_seconds": round(CAP_USD / PRICE_CEILING_USD_PER_HOUR * 3600, 1),
            "session_ceiling_rule": (
                f"${CAP_USD:.2f} / ${PRICE_CEILING_USD_PER_HOUR}/h ="
                f" {CAP_USD / PRICE_CEILING_USD_PER_HOUR:.3f} h ="
                f" {CAP_USD / PRICE_CEILING_USD_PER_HOUR * 3600:.0f} s ≥ the hard stop, so the"
                " SECONDS bind first and the cap can never be the thing that stops a run"
            ),
            "backstop_tolerance_seconds": BACKSTOP_TOLERANCE_SECONDS,
            "backstop_tolerance_rule": (
                "how far the `--terminate-after` stamp actually handed to `pod create` may sit"
                " BEYOND the one the hard stop computes. Only overshoot is bounded — a window"
                " rounded DOWN shortens itself and is always safe. The gate READS it from here and"
                " a record without this field is a refusal, not a default"
            ),
            "projection_gate": {
                "every": f"{PROJECTION_EVERY_CALLS} calls",
                "every_calls": PROJECTION_EVERY_CALLS,
                "formula": (
                    "billed_by_closed_pods + elapsed_on_this_pod + the leg's remaining calls × its"
                    " s/call + overhead_seconds. The leg is priced at its MEASURED rate — the"
                    " larger of its mean and its last call, over the rows THIS pod bought — as soon"
                    " as it has a reply, and at the registered rate before that"
                ),
                "overhead_seconds": OVERHEAD_SECONDS,
                "overhead_rule": (
                    "the SAME bucket the money block charges, and it has to be: rung 4 prices the"
                    " attempt with it on every poll. H6 asserts the two are one number"
                ),
                "authorised_rule": (
                    "the whole leg, from the first poll. There is no go/no-go and no prefix: the"
                    " rate is registered, so what rung 4 prices is what rung 0 authorised"
                ),
            },
        },
        "recovery_arithmetic": {
            "re_creations_allowed": 1,
            "rule": (
                "ONE re-creation after a proven deletion, and ONLY for a death BEFORE the first NEW"
                " reply — rungs 1, 2 and 3. The four carried rows are not a reply of this session"
                " and do not close the clause. After the first bought reply a KILL closes the"
                " session: the rows on the Mac are the evidence and the remainder is a new"
                " registration"
            ),
            "dead_pod_at_rung_2_seconds": dead_pod,
            "dead_pod_at_rung_2_billed_seconds": dead_pod_billed,
            "dead_pod_at_rung_2_usd": round(dead_pod / 3600 * PRICE_CEILING_USD_PER_HOUR, 6),
            "dead_pod_plus_worst_case_seconds": dead_pod + total,
            "dead_pod_plus_worst_case_usd": round(
                (dead_pod + total) / 3600 * PRICE_CEILING_USD_PER_HOUR, 6
            ),
            "dead_pod_plus_worst_case_with_the_deletion_tail_seconds": dead_pod_billed + total,
            "recovery_fits_the_stop": dead_pod + total <= HARD_STOP_SECONDS,
            "recovery_fits_the_stop_with_the_tail": dead_pod_billed + total <= HARD_STOP_SECONDS,
            "recovery_fits_the_cap": (dead_pod + total) / 3600 * PRICE_CEILING_USD_PER_HOUR
            <= CAP_USD,
            "widest_dead_pod_that_still_fits_seconds": HARD_STOP_SECONDS - total,
            "widest_dead_pod_rule": (
                f"{HARD_STOP_SECONDS:.0f} − {total:.0f} = {HARD_STOP_SECONDS - total:.0f} s — the"
                " widest dead pod that still leaves the WHOLE run inside the stop. Computed by"
                " `pre_create` on every create and never typed into a command"
            ),
            "widest_create_elapsed_at_which_a_KILL_is_still_recoverable_seconds": round(
                HARD_STOP_SECONDS - DELETION_TAIL_SECONDS - total, 1
            ),
            "widest_create_elapsed_at_the_measured_pre_generation_seconds": round(
                HARD_STOP_SECONDS
                - DELETION_TAIL_SECONDS
                - (generation + MEASURED_PRE_GENERATION_SECONDS + OVERHEAD_SECONDS),
                1,
            ),
            "widest_create_elapsed_rule": (
                "**the deciding number of the recovery clause, derived and published rather than"
                f" implied** (Dv668): a KILL at create-elapsed E bills E plus the"
                f" {DELETION_TAIL_SECONDS} s deletion tail, and the replacement pod then needs the"
                " whole worst case. So the clause is reachable only while E ≤ hard_stop −"
                " deletion_tail − total. At the CHARGED pre-generation that is"
                f" {HARD_STOP_SECONDS - DELETION_TAIL_SECONDS - total:.1f} s and at the MEASURED"
                " one it is"
                f" {HARD_STOP_SECONDS - DELETION_TAIL_SECONDS - (generation + MEASURED_PRE_GENERATION_SECONDS + OVERHEAD_SECONDS):.1f}"
                " s. Rung 2's own deadline is"
                f" {SSH_DEADMAN_SECONDS:.0f} s and rung 3's create-anchored backstop is"
                f" {BOOT_BACKSTOP_SECONDS:.0f}, so BOTH rungs fire inside the recoverable window at"
                " both spans — which is the check r1's lineage got wrong once and had to derive"
                " ([[a_ceiling_derived_from_one_span_measured_over_another]])"
            ),
            "rung_2_is_inside_the_window": SSH_DEADMAN_SECONDS
            <= HARD_STOP_SECONDS - DELETION_TAIL_SECONDS - total,
            "rung_3_is_inside_the_window": BOOT_BACKSTOP_SECONDS
            <= HARD_STOP_SECONDS - DELETION_TAIL_SECONDS - total,
        },
    }


def money(people: dict) -> dict:
    sums = arithmetic(people)
    return {
        "cap_usd_all_in": CAP_USD,
        "cap_rule": (
            f"${CAP_USD:.2f}, the operator's ruling (з) of 2026-08-22 (day). A FRESH guard step:"
            f" `results/spend_{PHASE.replace('-', '_')}.json`, so r1's $0.108122 and r2's spend are"
            " never one ledger"
        ),
        "arithmetic": sums,
        "guard": {
            "step": PHASE,
            "step_cap_usd": CAP_USD,
            "rule": (
                f"`scripts/runpod_guard.py --step {PHASE} --step-cap {CAP_USD:.2f}`, anchored"
                " BEFORE the first create. Every rung that names a guard reading acts on the"
                " guard's number and never on the gate's projection"
            ),
        },
        "meter": {
            "price_ceiling_usd_per_hour": PRICE_CEILING_USD_PER_HOUR,
            "price_rule": (
                f"rung 1 refuses a create above ${PRICE_CEILING_USD_PER_HOUR}/h. The 4090 24 GB"
                " this line has rented five times costs $0.74 and is taken on the first attempt"
            ),
            "rule": (
                "the gate's CLOCK is what the rungs act on: create-elapsed × the pod's own price."
                " The billing walk and the balance delta are read afterwards and reconciled in the"
                " report, and where they disagree the clock is the number quoted"
            ),
            "why": (
                "three steps of this lineage are OPEN because the walk lags past the session, and"
                " r1's balance delta came in ABOVE its clock 25 minutes after the deletion. A rung"
                " that waited for the endpoint would be a rung that never fires"
            ),
        },
        "recovery": {
            "rule": (
                "ONE re-creation after a proven deletion, and only for a death before the first NEW"
                " reply. `pre_create` computes both bounds on every create — reading + the worst"
                " case ≤ cap, and billed + the worst case ≤ the hard stop — and the stricter binds"
            ),
            "a_second_dead_pod_is_a_STOP": True,
            "the_carried_rows_are_not_a_reply": (
                "the out-file carries four rows before the pod exists. A recovery clause that"
                " counted rows in the file would refuse the FIRST create of this session"
            ),
            "after_the_first_reply": (
                "a KILL closes the session. The rows already bought stand in the out-file as"
                " evidence, nothing is deleted and nothing is re-asked, and the remainder is a new"
                " registration — never a third pod"
            ),
        },
        "step_sum": {
            "this_step_cap_usd": CAP_USD,
            "r1_on_the_clock_usd": R1_CLOCK_USD,
            "the_step_sum_usd": round(R1_CLOCK_USD + CAP_USD, 6),
            "the_step_sum_rule": (
                f"r1 ${R1_CLOCK_USD} (clock) + r2's cap ${CAP_USD:.2f} ="
                f" ${R1_CLOCK_USD + CAP_USD:.6f} for the pass-2 layer, on TWO guard steps"
            ),
            "the_signal_layer_so_far_usd": round(SIGNAL_LAYER_PASS_1_USD + R1_CLOCK_USD, 6),
            "the_one_shot_reader_for_comparison_usd": ONE_SHOT_READER_USD,
        },
    }


def instruments(held: dict) -> dict:
    def pin(name: str) -> dict:
        return {"path": name, "sha256": summary.sha256_of(REPO_ROOT / name)}

    return {
        "task": pass2.PASS2_TASK_V1,
        "prompt_sha256": {pass2.PASS2_TASK_V1: pass2.prompt_sha256(pass2.PASS2_TASK_V1)},
        "prompt_rule": (
            "BYTE-IDENTICAL to r1's. Four replies r1 paid for are carried into this run's out-file,"
            " and a copied reply is an answer to this request only if this request is that request"
        ),
        "module": {
            **pin("src/market_pulse/pass2.py"),
            "rule": "r1's, unmoved — the TEXT and the RENDERER",
        },
        "module_r2": {
            **pin("src/market_pulse/pass2_r2.py"),
            "rule": (
                "the derived ceiling and the tolerant parser. A SIBLING and not an edit:"
                " `results/pass2_pack.json` pins `pass2.py` and that pack is pinned by"
                " `results/prereg_pass2_signals.json`, a sealed record of a closed paid session"
            ),
        },
        "parser": {
            **pin("src/market_pulse/prompts.py"),
            "entry_point": "market_pulse.pass2_r2.parse_pass2",
            "refusal_set": list(pass2_r2.REFUSALS),
            "report_only_fields": sorted(pass2_r2.REPORT_ONLY_FIELDS),
            "rule": (
                "`prompts._reader_object`, then the thread's bought entity block, then every"
                " REPORT-ONLY field checked with the pinned validator that owns it and repaired"
                " where it refuses, then `prompts._reader`. The domains are never re-implemented"
            ),
        },
        "ceiling": {
            "chars": pass2_r2.PASS2_MAX_INPUT_CHARS,
            **pass2_r2.CEILING,
            "widest_unit_chars": held["length"]["widest_request_chars"],
            "widest_unit": held["length"]["widest_request"],
            "headroom_chars": held["length"]["headroom_chars"],
            "the_contracts_STOP_does_not_fire": pass2_r2.PASS2_MAX_INPUT_CHARS
            >= held["length"]["widest_request_chars"],
        },
        "scorer": {
            **pin("src/market_pulse/scorer.py"),
            "functions": [
                "reader_signal_found",
                "reader_entity_found",
                "reader_noise_count",
                "reader_comment_agreement",
            ],
            "rule": "the reader's own scorer, IMPORTED over pass 2's out-file and never forked",
        },
        "bar_scorer": pin("scripts/score_reader_probe_b.py"),
        "verdict_producer": pin("scripts/score_pass2_signals_r2.py"),
        "pack_builder": pin("scripts/build_pass2_r2_pack.py"),
        "gate": pin("scripts/gate_pass2_signals_r2.py"),
        "gate_r1": {
            **pin("scripts/gate_pass2_signals.py"),
            "rule": (
                "r2's gate RUNS this file's rung logic through the Dv663 construction and refuses"
                " to load if it has moved. It is pinned by r1's sealed record and is never edited"
            ),
        },
        "runner": pin("scripts/pass2_r2_pod_runner.py"),
        "shipped_runner": pin("scripts/reader_v5_pod_runner.py"),
        "producer": pin("scripts/write_pass2_prereg_r2.py"),
        "gold": {**pin("results/reader_gold_w1_r2.json"), "rule": "the reader's r2 gold, unedited"},
        "population": {"record": summary.rel(PACK), "sha256": summary.sha256_of(PACK)},
        "carried_rows": {
            "record": summary.rel(R1_OUT),
            "sha256": summary.sha256_of(R1_OUT),
            "ids": held["carried"]["ids"],
            "seeded_into": f"results/{OUT_FILE}",
            "rule": (
                "bought by r1's pod `9rquj8p0lelct3` and re-verified by `rendering_sha256` against"
                " r2's own pack at seed time. Never re-asked, never re-rendered"
            ),
        },
        "serving": held["serving"],
        "reference": {
            **pin("docs/REFERENCE-signals-w1.md"),
            "rule": "the bar's text, the team lead's, never re-read against the machine's answer",
        },
    }


def h6(held: dict, people: dict, sums: dict, clock: list[dict]) -> dict:
    """Every number `docs/PROMPT-pass2-signals-r2.md` prints, RE-DERIVED — the step-1 refusal gate."""
    items = held["legs"][0]["items"]
    owed = people["owed_units"]
    pre_generation = SSH_SECONDS + STAGE_LAUNCH_SECONDS + LOAD_SECONDS
    generation = owed * SECONDS_PER_CALL
    total = generation + pre_generation + OVERHEAD_SECONDS
    smoke = sums["seconds_per_call"]["smoke"]
    spread = sums["seconds_per_call"]["pod_class_spread"]
    recovery = sums["recovery_arithmetic"]
    r1_record = json.loads(summary.read_text_or_refuse(R1_PREREG))
    r1_gate = next(
        one
        for one in reversed(
            json.loads(summary.read_text_or_refuse(RESULTS / "pass2_signals_run.json"))["gates"]
        )
        if one.get("kind") == "go-no-go"
    )
    reader = {one["id"]: one for one in json.loads(summary.read_text_or_refuse(V5B_PACK))["items"]}
    reader_rows = {one["id"]: one for one in rows(V5B_ROWS) if one["id"] in reader}
    widest_reader = max(reader_rows, key=lambda one: reader[one]["rendered_chars"])
    pass2_density = [
        (held_item["rendered_chars"] / int(json.loads(line)["usage"]["prompt_tokens"]))
        for line in summary.read_text_or_refuse(R1_OUT).splitlines()
        if line.strip()
        for held_item in [next(x for x in items if x["id"] == json.loads(line)["id"])]
    ]
    rung = {int(one["rung"]): one for one in clock}

    def row(name, formula, registered, derived, mode="equals"):
        agrees = (
            abs(float(derived) - float(registered)) <= 5e-4
            if mode == "equals"
            else (derived >= registered if mode == "at_least" else derived <= registered)
        )
        return {
            "name": name,
            "formula": formula,
            "mode": mode,
            "registered": registered,
            "re_derived": derived,
            "agrees": bool(agrees),
        }

    table = [
        # ---- step 0.5, the three corrections this contract opens with
        row(
            "step_0_5_pack_headroom_under_pass_1s_constant",
            "12 000 − the widest rendered request",
            144,
            12_000 - held["length"]["widest_request_chars"],
        ),
        row(
            "step_0_5_widest_request_chars",
            "max rendered_chars over the 79 units — @mandziak:3679",
            11_856,
            held["length"]["widest_request_chars"],
        ),
        row(
            "step_0_5_widest_request_rows",
            "the filtered rows of that unit",
            18,
            len(next(one for one in items if one["id"] == "@mandziak:3679")["comments"]),
        ),
        row(
            "step_0_5_cumulative_at_r1s_decision",
            "results/pass2_signals_run.json, the go-no-go gate's cumulative_billed_seconds",
            517.3,
            float(r1_gate["cumulative_billed_seconds"]),
        ),
        row(
            "step_0_5_a_43_09_mean_projects_over_the_stop",
            "517.3 + 74 × 1.5 × 43.09 + 1 300",
            6600.29,
            round(517.3 + 74 * 1.5 * 43.09 + 1300, 2),
        ),
        row(
            "step_0_5_break_even_mean",
            "(6 600 − 517.3 − 1 300) / (74 × 1.5), floored to 3 places",
            43.087,
            math.floor((6600 - 517.3 - 1300) / (74 * 1.5) * 1000) / 1000,
        ),
        row(
            "step_0_5_the_break_even_times_the_multiplier_is_the_live_knife_edge",
            "1.5 × 43.087 vs (6 600 − 1 300 − 517.3) / 74",
            round((6600 - 1300 - 517.3) / 74, 2),
            round(1.5 * (math.floor((6600 - 517.3 - 1300) / (74 * 1.5) * 1000) / 1000), 2),
        ),
        # ---- the population
        row("population_units", "the r2 pack's leg", 79, len(items)),
        row("owed_units", "79 − the four carried", 75, owed),
        row("carried_units", "r1's replies that PARSED", 4, people["carried_units"]),
        row(
            "the_refused_thread_is_owed",
            "@matusi_ukr:22303 is in the owed list",
            1,
            int(held["owed"]["re_asked_after_a_refusal"] in held["owed"]["ids"]),
        ),
        row("filtered_rows", "the r1 pack's own count, carried", 281, people["filtered_rows"]),
        row(
            "widest_unit_rows",
            "max rows in a unit — @klopotenkofood:6040",
            26,
            people["widest_unit_rows"],
        ),
        row(
            "widest_smoke_unit_rows",
            "max rows over the five threads r1 asked. **The contract prints 10 and the pack says"
            " 8** — @mandziak:3703 and @matusi_ukr:22272 TIE at 8, and no reading of the five"
            " gives 10. Registered at the derived value; the extrapolation the MAX avoids is"
            " therefore 26/8 = 3.25x and not the 2.6x the contract's own number implies",
            8,
            people["widest_smoke_unit_rows"],
        ),
        row(
            "widest_smoke_unit_is_a_TIE",
            "how many of the five threads carry the widest row count",
            2,
            people["widest_smoke_units_at_the_maximum"],
        ),
        row(
            "the_extrapolation_the_max_avoids",
            "population widest rows / smoke widest rows",
            3.25,
            round(people["widest_unit_rows"] / people["widest_smoke_unit_rows"], 2),
        ),
        # ---- the ceiling
        row(
            "reader_proven_prompt_tokens",
            "results/reader_v5b_w1.jsonl :: the widest reader request's usage.prompt_tokens",
            pass2_r2.CEILING["proven_prompt_tokens"],
            int(reader_rows[widest_reader]["usage"]["prompt_tokens"]),
        ),
        row(
            "reader_proven_request_chars",
            "results/reader_v5b_pack.json :: that item's rendered_chars",
            15_673,
            reader[widest_reader]["rendered_chars"],
        ),
        row(
            "reader_proven_request_finished_on_its_own",
            "finish_reason == stop on that reply",
            1,
            int(reader_rows[widest_reader]["finish_reason"] == "stop"),
        ),
        row(
            "serving_output_tokens",
            "results/reader_v5b_pack.json :: serving.output_tokens",
            4000,
            int(held["serving"]["output_tokens"]),
        ),
        row(
            "pass2_chars_per_prompt_token_min",
            "min over the five PAID pass-2 requests of rendered_chars / usage.prompt_tokens",
            pass2_r2.CEILING["chars_per_prompt_token"],
            math.floor(min(pass2_density) * 10_000) / 10_000,
        ),
        row(
            "derived_input_ceiling_chars",
            "floor(proven_prompt_tokens × chars_per_prompt_token)",
            15_569,
            pass2_r2.PASS2_MAX_INPUT_CHARS,
        ),
        row(
            "the_derived_ceiling_clears_the_widest_unit",
            "ceiling ≥ 11 856 — the contract's STOP-before-any-pod does not fire",
            held["length"]["widest_request_chars"],
            pass2_r2.PASS2_MAX_INPUT_CHARS,
            "at_least",
        ),
        row(
            "derived_ceiling_headroom_chars",
            "ceiling − the widest unit",
            3713,
            held["length"]["headroom_chars"],
        ),
        # ---- the rate
        row(
            "smoke_max_seconds",
            "max seconds over results/pass2_signals_v1.jsonl",
            SMOKE_MAX_SECONDS,
            smoke["max"],
        ),
        row(
            "smoke_mean_seconds",
            "mean seconds over the same file",
            45.582,
            smoke["mean"],
        ),
        row(
            "smoke_seconds_are_five_and_element_wise_the_files_own",
            "every one of the five seconds, in the file's own order — D2 QUOTES this list now",
            5,
            sum(
                1
                for one, two in zip(
                    smoke["seconds"],
                    [float(x["seconds"]) for x in rows(R1_OUT)],
                    strict=True,
                )
                if one == two
            ),
        ),
        row(
            "the_smokes_own_file_hashes_to_what_the_record_pins",
            "results/pass2_signals_v1.jsonl against money.arithmetic.seconds_per_call.smoke.sha256",
            1,
            int(smoke["sha256"] == summary.sha256_of(R1_OUT)),
        ),
        row(
            "pod_class_spread_v2",
            "max/min over the three v2 out-files' means, rounded to 2 places",
            POD_CLASS_SPREAD,
            round(spread["v2_spread"], 2),
        ),
        row(
            "pod_class_spread_v2_low",
            "results/pass1_window_r2_v2.jsonl mean",
            2.694083,
            spread["v2_min"],
        ),
        row(
            "pod_class_spread_v2_high",
            "results/pass1_window_v2.jsonl mean",
            4.498473,
            spread["v2_max"],
        ),
        row(
            "base_two_point_spread",
            "probe-b base / dev base — the wider reading the ruling did NOT charge",
            2.2509,
            round(spread["base_spread"], 4),
        ),
        row(
            "charged_before_the_ceil",
            "58.07 × 1.67",
            96.98,
            round(SMOKE_MAX_SECONDS * POD_CLASS_SPREAD, 2),
        ),
        row(
            "seconds_per_call",
            "ceil(58.07 × 1.67)",
            97.0,
            SECONDS_PER_CALL,
        ),
        row(
            "the_exact_spread_ceils_to_the_same_charge",
            "ceil(58.07 × 1.669656) — the rounding does not reach the charge",
            97.0,
            float(math.ceil(SMOKE_MAX_SECONDS * spread["v2_spread"])),
        ),
        row(
            "the_charge_is_above_the_slowest_call_measured",
            "97 ≥ 58.07",
            SMOKE_MAX_SECONDS,
            SECONDS_PER_CALL,
            "at_least",
        ),
        # ---- the money
        row("generation_seconds", "75 × 97", 7275.0, generation),
        row(
            "pre_generation_seconds",
            f"ssh {SSH_SECONDS:.0f} + stage/launch {STAGE_LAUNCH_SECONDS:.0f} + load {LOAD_SECONDS:.0f}",
            1100.0,
            pre_generation,
        ),
        row("overhead_seconds", "the r2 bucket, carried", 1300.0, OVERHEAD_SECONDS),
        row(
            "overhead_is_one_number",
            "money.arithmetic.overhead_seconds == projection_gate.overhead_seconds",
            OVERHEAD_SECONDS,
            float(sums["cumulative"]["projection_gate"]["overhead_seconds"]),
        ),
        row("total_seconds", "7 275 + 1 100 + 1 300", 9675.0, total),
        row("total_hours", "9 675 / 3 600", 2.6875, round(total / 3600, 4)),
        row(
            "worst_case_usd_at_the_ceiling",
            "2.6875 h × $0.80/h",
            2.15,
            round(total / 3600 * PRICE_CEILING_USD_PER_HOUR, 6),
        ),
        row(
            "worst_case_usd_at_0_53",
            "2.6875 h × $0.53/h — the contract prints $1.424, and the exact value is 1.424375",
            1.424375,
            round(total / 3600 * MEASURED_PRICE_USD_PER_HOUR, 6),
        ),
        row("cap_usd", "the ruling (з)", 2.50, CAP_USD),
        row("hard_stop_seconds", "the registered cumulative stop", 11000.0, HARD_STOP_SECONDS),
        row(
            "hard_stop_usd",
            "11 000 s × $0.80/h",
            2.4444,
            round(HARD_STOP_SECONDS / 3600 * PRICE_CEILING_USD_PER_HOUR, 4),
        ),
        row(
            "the_hard_stop_is_under_the_cap",
            "$2.4444 ≤ $2.50",
            round(HARD_STOP_SECONDS / 3600 * PRICE_CEILING_USD_PER_HOUR, 4),
            CAP_USD,
            "at_least",
        ),
        row(
            "session_ceiling_seconds",
            "$2.50 / $0.80/h × 3 600",
            11250.0,
            float(sums["cumulative"]["session_ceiling_seconds"]),
        ),
        row(
            "the_session_ceiling_is_above_the_hard_stop",
            "11 250 ≥ 11 000 — the seconds bind first",
            HARD_STOP_SECONDS,
            float(sums["cumulative"]["session_ceiling_seconds"]),
            "at_least",
        ),
        # ---- the recovery
        row(
            "dead_pod_at_rung_2_seconds",
            "rung 2's own deadline",
            500.0,
            float(recovery["dead_pod_at_rung_2_seconds"]),
        ),
        row(
            "dead_pod_at_rung_2_usd",
            "500 s × $0.80/h",
            0.111111,
            float(recovery["dead_pod_at_rung_2_usd"]),
        ),
        row(
            "dead_pod_billed_with_the_deletion_tail",
            "500 + 78.5 — the meter stops at `pod delete`",
            578.5,
            float(recovery["dead_pod_at_rung_2_billed_seconds"]),
        ),
        row(
            "recovery_seconds",
            "500 + 9 675",
            10175.0,
            float(recovery["dead_pod_plus_worst_case_seconds"]),
        ),
        row(
            "recovery_fits_the_stop",
            "10 175 ≤ 11 000",
            float(recovery["dead_pod_plus_worst_case_seconds"]),
            HARD_STOP_SECONDS,
            "at_least",
        ),
        row(
            "recovery_usd",
            "10 175 s × $0.80/h — the contract prints $2.2607 and the arithmetic is 2.261111",
            2.261111,
            float(recovery["dead_pod_plus_worst_case_usd"]),
        ),
        row(
            "recovery_fits_the_cap",
            "$2.2611 ≤ $2.50",
            float(recovery["dead_pod_plus_worst_case_usd"]),
            CAP_USD,
            "at_least",
        ),
        row(
            "widest_dead_pod_seconds",
            "11 000 − 9 675",
            1325.0,
            float(recovery["widest_dead_pod_that_still_fits_seconds"]),
        ),
        row(
            "widest_create_elapsed_still_recoverable_charged",
            "11 000 − 78.5 − 9 675 (Dv668's construction)",
            1246.5,
            float(recovery["widest_create_elapsed_at_which_a_KILL_is_still_recoverable_seconds"]),
        ),
        row(
            "widest_create_elapsed_still_recoverable_measured",
            "11 000 − 78.5 − (7 275 + 135 + 1 300)",
            2211.5,
            float(recovery["widest_create_elapsed_at_the_measured_pre_generation_seconds"]),
        ),
        row(
            "rung_2_fires_inside_the_recoverable_window",
            "rung 2's deadline ≤ the widest recoverable create-elapsed at the CHARGED spans",
            1,
            int(recovery["rung_2_is_inside_the_window"]),
        ),
        row(
            "rung_3_fires_inside_the_recoverable_window",
            "rung 3's create-anchored backstop ≤ the same window",
            1,
            int(recovery["rung_3_is_inside_the_window"]),
        ),
        # ---- rung 4's band
        row(
            "rung_4_knife_edge_at_the_charged_spans",
            "(11 000 − 1 300 − 1 100) / 75",
            114.6667,
            float(rung[4]["knife_edge_at_the_charged_spans"]),
        ),
        row(
            "rung_4_knife_edge_at_the_measured_pre_generation",
            "(11 000 − 1 300 − 135) / 75",
            127.5333,
            float(rung[4]["knife_edge_at_the_measured_pre_generation"]),
        ),
        row(
            "both_knife_edges_are_above_the_charge",
            "the tighter of the two ≥ 97 s/thread",
            SECONDS_PER_CALL,
            min(
                float(rung[4]["knife_edge_at_the_charged_spans"]),
                float(rung[4]["knife_edge_at_the_measured_pre_generation"]),
            ),
            "at_least",
        ),
        # ---- the step
        row("r1_on_the_clock_usd", "r1's gate clock", 0.108122, R1_CLOCK_USD),
        row("step_sum_usd", "$0.108122 + $2.50", 2.608122, round(R1_CLOCK_USD + CAP_USD, 6)),
        # ---- the bars and the parser
        row(
            "completeness_refusal_budget",
            "ceil(0.174 × 79)",
            14,
            math.ceil(people["units"] * REFUSALS_FRACTION),
        ),
        row(
            "the_completeness_bar_has_ONE_arm",
            "no rung's verdict selects an arm in r2",
            1,
            len(json.loads(json.dumps(bars_arms(held)))),
        ),
        row(
            "the_refusal_set_is_closed_at_six",
            "market_pulse.pass2_r2.REFUSALS",
            6,
            len(pass2_r2.REFUSALS),
        ),
        row(
            "the_prompt_has_not_moved_a_byte",
            "pass2.prompt_sha256 against the sha r1's sealed record pins",
            1,
            int(
                pass2.prompt_sha256(pass2.PASS2_TASK_V1)
                == r1_record["instruments"]["prompt_sha256"][pass2.PASS2_TASK_V1]
            ),
        ),
        row(
            "the_prompt_still_carries_the_two_clauses_the_reader_line_paid_for",
            "prompts.READER_ASPECT_V5 and prompts.READER_NOT_A_SIGNAL_V3, spliced not retyped",
            2,
            sum(
                1
                for clause in (prompts.READER_ASPECT_V5, prompts.READER_NOT_A_SIGNAL_V3)
                if clause in pass2.PASS2_THREAD_PROMPT
            ),
        ),
        row(
            "r1s_F2_reply_is_COUNTED_by_r2s_parser",
            "the exact reply that killed r1's F2 thread, parsed here",
            1,
            int(f2_is_counted(held)),
        ),
        row(
            "r1s_F2_reply_is_still_REFUSED_by_r1s_parser",
            "r1's record stays true: pass2.parse_pass2 refuses it exactly as it did",
            1,
            int(f2_is_refused_by_r1(held)),
        ),
        row(
            "every_carried_row_re_renders_to_r2s_own_sha",
            "the four carried replies against the r2 pack",
            4,
            carried_shas_match(held),
        ),
    ]
    mismatches = [one["name"] for one in table if not one["agrees"]]
    return {
        "rule": (
            "every number the contract prints, re-derived from the file it comes out of. A mismatch"
            " REFUSES: this producer writes nothing and exits non-zero"
        ),
        "rows": table,
        "mismatches": mismatches,
        "reading": (
            "every registered number re-derives"
            if not mismatches
            else f"{len(mismatches)} numbers do not re-derive"
        ),
    }


def bars_arms(held: dict) -> dict:
    units = len(held["legs"][0]["items"])
    return {
        "GO": {
            "owed": units,
            "answered_minimum": units,
            "parse_refusals_maximum": math.ceil(units * REFUSALS_FRACTION),
            "sha_mismatches_maximum": 0,
        }
    }


def _carried_pairs(held: dict) -> list[tuple[dict, dict]]:
    by_id = {one["id"]: one for one in held["legs"][0]["items"]}
    return [(one, by_id[one["id"]]) for one in rows(R1_OUT) if one["id"] in by_id]


def carried_shas_match(held: dict) -> int:
    carried = set(held["carried"]["ids"])
    return sum(
        1
        for row, item in _carried_pairs(held)
        if row["id"] in carried and row["rendering_sha256"] == item["rendering_sha256"]
    )


def f2_is_counted(held: dict) -> bool:
    name = held["owed"]["re_asked_after_a_refusal"]
    row, item = next(pair for pair in _carried_pairs(held) if pair[0]["id"] == name)
    verdict = pass2_r2.parse_pass2(row["reply"], unit=item)
    return bool(verdict["unreadable_field_names"]) and not verdict["signals"]


def f2_is_refused_by_r1(held: dict) -> bool:
    name = held["owed"]["re_asked_after_a_refusal"]
    row, item = next(pair for pair in _carried_pairs(held) if pair[0]["id"] == name)
    try:
        pass2.parse_pass2(row["reply"], unit=item)
    except prompts.ParseError:
        return True
    return False


def build() -> dict:
    held = pack()
    people = population(held)
    reach = r1producer.reachability(held)
    clock = kill_clock(people)
    purse = money(people)
    return {
        "phase": PHASE,
        "contract": "docs/PROMPT-pass2-signals-r2.md",
        "authority": {
            "ruling": (
                "docs/STATUS.md «Открытые решения» п. 1 (з), 2026-08-22 (day): pass2-signals r2 —"
                " buy the remaining 75 threads, cap $2.50, the rate charged on the smoke's MAX ×"
                " the pod-class spread. The alternatives — a $2.00 cap with the row-weighted arm,"
                " and a stop into LoRA — were rejected"
            ),
            "inherits": "docs/PROMPT-pass2-signals.md — every clause not amended by r2 stands",
            "adr": "knowledge/decisions/pass-2-in-the-readers-schema-and-strict-authority.md",
            "reference": "docs/REFERENCE-signals-w1.md — the bar's text, the team lead's",
        },
        "attempt": (
            "ONE attempt, ONE paid session. A KILL after the first NEW reply closes it: the rows"
            " bought stand in the out-file as evidence and the remainder is a new registration"
        ),
        "what_this_run_is": (
            "the 75 threads pass 2 still owes, at a rate this stack has now MEASURED. One leg, one"
            " out-file, no go/no-go — the decision rung S′ took in the middle of r1's session is"
            " taken here before the create, by the operator, with the measured rate in front of it"
        ),
        "what_this_run_is_not": (
            "not a re-buy of the four threads r1 paid for. Not a re-derivation of the population."
            " Not a change to the prompt, the bars, the scorer or the gold. Not a re-attribution —"
            " strict authority is unmoved and a relabel is still a refusal"
        ),
        "population": people,
        "reachability": reach,
        "bars": bars(held, reach),
        "kill_clock": clock,
        "kill_clock_order": [f"{one['rung']} — {one['name']}" for one in clock],
        "money": purse,
        "instruments": instruments(held),
        "run_record": {
            "record": f"results/{PHASE.replace('-', '_')}_run.json",
            "pod_log": f"results/{PHASE.replace('-', '_')}_pod.log",
            "launch_stamp": "pass2_signals_r2_launched_at",
            "out_file": f"results/{OUT_FILE}",
            "rule": (
                "this attempt's OWN names for every file a rung reads or writes. `results/` holds"
                " four closed sessions' stamps and logs, and a rung that read one of them would be"
                " reading a dead pod's clock (Dv621/632). There is NO go token in r2"
            ),
        },
        "frozen_when_the_pod_exists": [
            "results/prereg_pass2_signals_r2.json",
            "results/pass2_r2_pack.json",
            f"results/{OUT_FILE}",
            "src/market_pulse/pass2.py",
            "src/market_pulse/pass2_r2.py",
            "scripts/gate_pass2_signals_r2.py",
            "scripts/pass2_r2_pod_runner.py",
        ],
        "supersedes": {
            "record": summary.rel(R1_PREREG),
            "sha256": summary.sha256_of(R1_PREREG),
            "r1s_closing_state": (
                "rung S′ STOP at 5 of 79 — four replies parsed, F2 REFUSED on a report-only field."
                " $0.108122 on the clock, 526.0 s, pod 9rquj8p0lelct3. A registered outcome: the"
                " contract bought a measurement and got one"
            ),
            "repealed_numbers": {
                "6600 s": "r1's cumulative hard stop, priced for a five-thread smoke. r2's is 11 000",
                "1.50 usd": "r1's cap. r2's is 2.50, by the ruling (з)",
                "120 s/call": (
                    "r1's ASSUMED smoke rate — the only assumption in that record. It is repealed"
                    " by measurement: 15.801 … 58.07 s on five paid calls"
                ),
                "48.6486 s/call": (
                    "r1's registered rung-S′ knife edge. Repealed with the rung: r2 has no"
                    " go/no-go. It was also never the number that bound — the live edge at the"
                    " decision was 64.63 (Dv703)"
                ),
                "32.4324 s/call": "the mean arm of the same repealed edge",
                "12000 chars as the input ceiling": (
                    "pass 1's constant, aliased by r1. Repealed by a DERIVED ceiling of 15 569"
                    " chars — and the 12 000 is still reported beside it, because the pack's"
                    " headroom under pass 1's number (144) is the reading that made the derivation"
                    " necessary"
                ),
                "rung S and rung S′": (
                    "the smoke leg and the go/no-go. Both are repealed: r2 has a registered rate,"
                    " so there is nothing for a mid-session rung to decide"
                ),
            },
            "the_Dv613_sweep": (
                "every number above is quoted ONLY inside this block. Grep the rest of this record"
                " for 6600, 1.50, 120, 48.6486, 32.4324 or 12000-as-a-ceiling and the sweep is"
                " clean — a repealed threshold that survives somewhere else in the file is the"
                " defect this sweep exists to catch. ONE exception, named rather than silent: the"
                " `step_0_5_*` H6 rows re-derive r1's own arithmetic to correct it, so 6 600 and"
                " 517.3 appear there BY SUBJECT. They are corrections of a closed record and not"
                " thresholds of this one"
                " ([[an_audit_of_pins_is_not_an_audit_of_thresholds]])"
            ),
            "what_it_carries_and_why": {
                "ssh 500 s": "the same six-reading spread; nothing has narrowed it",
                "load 450 s": "the boot is not a constant and is charged at the maximum of eight",
                "overhead 1 300 s": "the same tail this line has now measured three times",
                "backstop tolerance 60 s": "unmoved",
                "liveness 600 s": "unmoved",
                "refusal fraction 0.174": (
                    "v5b's 4 of 23. r2's tolerant reader should beat it and the bar is not lowered"
                    " for a hope"
                ),
                "bars 1/2/3, the gold, the scorer, the prompt": "r1's, byte for byte",
            },
        },
        "return_to_the_operator": {
            "whatever_happens": [
                "bars 1/2/3 over all 79 threads — the first time any of them is SCORED",
                "the per-flagship scorecard, citing the pass-1 label of every row it names",
                "the DROP table — the filtered rows pass 2 sent to noise, by thread and by label",
                "the subject_doubt rate by pass-1 label",
                "the unreadable-field table, which is what Dv702 bought",
                "the v5b comparison row on the same gold and scorer",
                "this pod's measured s/thread beside r1's 45.6 mean / 58.1 max",
            ],
            "on_a_KILL": (
                "the rows bought stand, the bars say UNSCORED with the reason, and the remainder"
                " returns as a new registration with this pod's own rate in it"
            ),
            "the_fourteen": (
                "no reading over them is a bar, in this report or in its acceptance. The ADR's"
                " «What binds» point 2 binds the team lead as well as the executor"
            ),
        },
        "do_not": [
            "edit prompts.py, scorer.py, the reader gold, or any r1 artifact",
            "move the prompt text of pass2_thread_gm4_v1 by a byte",
            "re-buy any of the four carried threads",
            "render a raw unfiltered comment in any request",
            "accept a relabelling, however named",
            "register a bar on the fourteen",
            "leave --watch",
            "open two billing endpoints at once, or a third pod",
        ],
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "rule": (
                "the constants are typed once at the top of this file with their derivations; every"
                " other number here is computed. H6 re-derives the ones that have a file behind them"
            ),
        },
        "h6": h6(held, people, purse["arithmetic"], clock),
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    record = build()
    check = record["h6"]
    if check["mismatches"]:
        for one in check["rows"]:
            if not one["agrees"]:
                print(
                    f"  H6 MISMATCH {one['name']}: registered {one['registered']} · re-derived"
                    f" {one['re_derived']} · {one['formula']}"
                )
        raise SystemExit(
            f"{len(check['mismatches'])} of {len(check['rows'])} H6 rows do not re-derive."
            " Nothing was written — this is the step-1 refusal gate."
        )
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    sums = record["money"]["arithmetic"]
    rec = sums["recovery_arithmetic"]
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    print(f"  H6: {len(check['rows'])} rows, {check['reading']}")
    print(
        f"  owed {record['population']['owed_units']} × {SECONDS_PER_CALL:.0f} s ="
        f" {sums['generation_seconds']:.0f} s · all-in {sums['total_seconds']:.0f} s ="
        f" ${sums['worst_case_usd_at_the_price_ceiling']:.4f} at ${PRICE_CEILING_USD_PER_HOUR}/h"
    )
    print(
        f"  hard stop {HARD_STOP_SECONDS:.0f} s ="
        f" ${sums['cumulative']['hard_stop_usd_at_the_price_ceiling']:.4f} of ${CAP_USD:.2f}"
        f" · widest dead pod {rec['widest_dead_pod_that_still_fits_seconds']:.0f} s"
        f" · recoverable up to {rec['widest_create_elapsed_at_which_a_KILL_is_still_recoverable_seconds']:.1f} s of create-elapsed"
    )
    print(
        f"  ceiling {pass2_r2.PASS2_MAX_INPUT_CHARS} chars (derived) ·"
        f" widest unit {record['instruments']['ceiling']['widest_unit_chars']} ·"
        f" headroom {record['instruments']['ceiling']['headroom_chars']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
