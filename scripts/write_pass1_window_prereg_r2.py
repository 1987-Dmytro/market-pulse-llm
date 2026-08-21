#!/usr/bin/env python3
"""`results/prereg_pass1_window_r2.json` — the 901 still owed, priced on the POD CLASS.

**What this record is.** The pre-registration of `docs/PROMPT-pass1-window-r2.md`: the same
population, the same prompt v2, the same rendering and the same rungs as `pass1-window`, over the
901 comments the killed r1 pod never reached. What MOVED is the price and the population owed, and
every number that moved is derived here from a file rather than typed from the contract's prose.

**The rate is the whole reason this contract exists.** r1 charged 3.4075 s/call — a measurement on
one pod times a margin — and the pod that ran went at 4.498 (Dv647). A rate is a property of the
POD, so this record charges it on the pod CLASS, at the top of the spread this stack has actually
measured, and derives it from three files:

    probe-b   results/pass1_probe_b_rows.jsonl   64 rows   the slowest BASE pod measured
    dev base  results/pass1_dev_base.jsonl      200 rows   the fastest BASE pod measured
    dev v2    results/pass1_dev_v2.jsonl        200 rows   v2 over base, on ONE pod

    charged = mean(probe-b) × mean(dev v2) / mean(dev base)

The two base legs ran the SAME prompt (`pass1_comment_gm4_v1`, sha 5a4a3cb6…) at nearly the same
request width, so the 2.25× between them is a property of the silicon and not of the question. That
check is an H6 row and a refusal, not a sentence.

**The rounding is deliberate and it is UP.** The derivation gives 6.135572 and this record charges
**6.14**, the number `docs/PROMPT-pass1-window-r2.md` prints and the number every figure it prints is
computed at. Rounding up is the conservative direction — it charges more per call, so the worst case
grows and the widest dead pod the recovery clause allows shrinks. Both values are recorded, an H6 row
asserts `charged ≥ derived`, and nothing downstream may read one when it means the other
([[two_values_for_one_input_get_quoted_kindly]]).

**Nothing of r1's is edited.** `results/prereg_pass1_window.json` is a sealed record of a closed paid
session and is READ here — for its instruments, for what `supersedes` names, and for the closing
state. Its repealed numbers (6 500 · 3.4075 · 5 916.54 · 583.46 · 1.50) may not survive as NUMBERS
anywhere in this record's money block except inside `supersedes`, where they are quoted by name.
`tests/test_pass1_window_r2_prereg.py` sweeps for them.

    PYTHONPATH=src python3.11 scripts/write_pass1_window_prereg_r2.py
    PYTHONPATH=src python3.11 scripts/write_pass1_window_prereg_r2.py --out /tmp/again.json
"""

import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pass1_window_r2_pack as r2pack  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_pass1_window_prereg as r1prod  # noqa: E402

OUT = REPO_ROOT / "results" / "prereg_pass1_window_r2.json"
OUT_NAME = "results/prereg_pass1_window_r2.json"
PACK_NAME = r2pack.OUT_NAME
PACK = REPO_ROOT / PACK_NAME
GATE = REPO_ROOT / "scripts" / "gate_pass1_window_r2.py"
RUN_RECORD = "results/pass1_window_r2_run.json"

R1_PREREG = REPO_ROOT / "results" / "prereg_pass1_window.json"
R1_PREREG_NAME = "results/prereg_pass1_window.json"
R1_RUN = REPO_ROOT / "results" / "pass1_window_run.json"
R1_OUT = REPO_ROOT / "results" / "pass1_window_v2.jsonl"
R1_FEWSHOT_RUN = REPO_ROOT / "results" / "pass1_fewshot_run.json"
R2_RUN = REPO_ROOT / "results" / "pass1_fewshot_r2_run.json"
DEV_PACK = REPO_ROOT / "results" / "pass1_dev_pack.json"

PROBE_B_ROWS = REPO_ROOT / "results" / "pass1_probe_b_rows.jsonl"
DEV_BASE_ROWS = REPO_ROOT / "results" / "pass1_dev_base.jsonl"
DEV_V2_ROWS = REPO_ROOT / "results" / "pass1_dev_v2.jsonl"

CAP_USD = 2.00
PRICE_CEILING = 0.80
HARD_STOP_SECONDS = 8600.0
CHARGED_SECONDS_PER_CALL = 6.14
"""What every call is charged at. Derived below as 6.135572 and rounded UP to the figure the
contract prints; the H6 block refuses a charge below the derivation."""

SSH_DEADMAN_SECONDS = 500.0
STAGE_LAUNCH_SECONDS = 150.0
BOOT_SECONDS = 450.0
OVERHEAD_SECONDS = 1300.0
IDLE_DEADLINE_SECONDS = 600.0
PROJECTION_EVERY_CALLS = 20
BACKSTOP_TOLERANCE_SECONDS = 60.0
LORA_B_PRICE = 0.53

REFUSALS_FRACTION = 0.01
"""1 % of the leg — 9 of 901. r1 registered 10 of 1 032 by the same rule; the fraction is what
carried over and the count is derived from it, because a count copied across populations is a
threshold that stopped meaning what it said ([[a_moved_constant_fails_green]])."""

WORST_MEASURED_BOOT = 353.0
WIDEST_SSH_READING = 262.5
SLOWEST_CALL_EVER_MEASURED = 6.214
"""probe-b's slowest single reply — the worst this stack has ever seen from one call, on the card
this contract rents. Rung 4 prices the remainder at the LARGER of the mean and the last call, so the
knife edge is reported against this number and not against a mean."""

R1_POD = "xpz3zb7yxus5cw"
R1_MEASURED_SECONDS_PER_CALL = 4.498473
R1_PRE_GENERATION_MEASURED = 252.5
"""The r1 window pod's own two readings: the rate it ran at, and the create-elapsed at its first
reply. The second is the span this record carries TWO values for — the measured one and the 1 100 s
it CHARGES — and rung 4's knife edge is published at both (Dv630/655)."""

R2_ROWS_COPIED_BACK = 464
R2_WATCH_GO_ELAPSED = 1276.1


def sha(path: Path) -> str:
    return summary.sha256_of(path)


def seconds_of(path: Path) -> list[float]:
    return [
        float(json.loads(line)["seconds"])
        for line in summary.read_text_or_refuse(path).splitlines()
        if line.strip()
    ]


def rate() -> dict:
    """The charged s/call, DERIVED from three files — the pod class, and v2's uplift over the base.

    Two base readings on two pods, one prompt: probe-b's 64 rows and r2's 200 dev-base rows both ran
    `pass1_comment_gm4_v1` under the same prompt sha, at request widths within 6 % of each other, and
    they are 2.25× apart. That spread is the pod and nothing else — r1's registration priced the
    window off ONE of those pods and its live rate came in 1.65× the sample (Dv647,
    [[a_rate_is_a_property_of_the_pod]]).

    v2's uplift over the base is measured on ONE pod, where both legs ran, and is charged as a
    property of the PROMPT. That is this record's one modelling assumption and it is named as one.
    """
    probe = seconds_of(PROBE_B_ROWS)
    base = seconds_of(DEV_BASE_ROWS)
    v2 = seconds_of(DEV_V2_ROWS)
    slowest_base = statistics.fmean(probe)
    fastest_base = statistics.fmean(base)
    uplift = statistics.fmean(v2) / fastest_base
    derived = slowest_base * uplift

    probe_rows = [
        json.loads(line)
        for line in summary.read_text_or_refuse(PROBE_B_ROWS).splitlines()
        if line.strip()
    ]
    prompts_seen = {row["prompt_sha256"] for row in probe_rows}
    dev = json.loads(summary.read_text_or_refuse(DEV_PACK))
    base_prompt = dev["instruments"]["prompt_sha256"]["pass1_comment_gm4_v1"]
    if prompts_seen != {base_prompt}:
        raise SystemExit(
            f"the probe-b rows ran prompt(s) {sorted(prompts_seen)} and the dev base leg ran"
            f" {base_prompt}. The 2.25× spread between them is charged here as a property of the"
            " POD, and that reading only holds if the two legs asked the same question — stop."
        )
    if CHARGED_SECONDS_PER_CALL < derived:
        raise SystemExit(
            f"the charged rate {CHARGED_SECONDS_PER_CALL} is BELOW the derivation {derived:.6f}."
            " The rounding of this line is deliberate and it is UP — a charge under the derived"
            " rate buys seconds the arithmetic does not have. Stop and report."
        )
    return {
        "v2": CHARGED_SECONDS_PER_CALL,
        "derived": round(derived, 6),
        "charged": CHARGED_SECONDS_PER_CALL,
        "rounding_rule": (
            f"the derivation is {derived:.6f} and this record charges"
            f" {CHARGED_SECONDS_PER_CALL} — rounded UP, which is the conservative direction: a"
            " higher charge grows the worst case and SHRINKS the widest dead pod the recovery"
            " clause allows. It is also the figure docs/PROMPT-pass1-window-r2.md prints and every"
            " figure that contract prints is computed at it. Both values are here so no reader has"
            " to choose ([[two_values_for_one_input_get_quoted_kindly]])"
        ),
        "formula": "mean(probe-b) × mean(dev v2) / mean(dev base)",
        "the_pod_class": {
            "slowest_base_pod_seconds_per_call": round(slowest_base, 6),
            "slowest_base_pod_sample": "64 rows, results/pass1_probe_b_rows.jsonl, 2026-08-18",
            "slowest_base_pod_sha256": sha(PROBE_B_ROWS),
            "fastest_base_pod_seconds_per_call": round(fastest_base, 6),
            "fastest_base_pod_sample": "200 dev rows, results/pass1_dev_base.jsonl, pod 8tpx8lf05n6skc",
            "fastest_base_pod_sha256": sha(DEV_BASE_ROWS),
            "spread": round(slowest_base / fastest_base, 6),
            "one_prompt_two_pods": (
                f"both legs ran pass1_comment_gm4_v1 at prompt sha {base_prompt[:16]}…, checked"
                " above and a refusal if it ever stops being true. The requests differ in width by"
                " 5.6 % and the replies by 1.7 % — so the 2.25× between the two means is the"
                " silicon"
            ),
            "rule": (
                "the TOP of the measured spread is charged. r1 charged the bottom of it times a"
                " margin and the live pod came in 1.65× the sample; the sample was reproducible and"
                " it was not representative ([[a_reproducible_probe_can_be_unrepresentative]])"
            ),
        },
        "the_uplift": {
            "v2_over_base": round(uplift, 6),
            "measured_on": "pod 8tpx8lf05n6skc — the ONE pod that ran both legs",
            "v2_sample": "200 dev rows, results/pass1_dev_v2.jsonl",
            "v2_sample_sha256": sha(DEV_V2_ROWS),
            "v2_seconds_per_call": round(statistics.fmean(v2), 6),
            "the_assumption": (
                "the uplift is charged as a property of the PROMPT and therefore transferable"
                " across pods, while the base rate is charged as a property of the pod. This is the"
                " one modelling assumption in this record and no run has tested it: no pod has ever"
                " run both legs at both ends of the spread. It is stated rather than hidden, and it"
                " is checkable against the r1 window pod — 4.498473 s/call on v2 implies a base of"
                f" {R1_MEASURED_SECONDS_PER_CALL / uplift:.3f}, which sits INSIDE the measured"
                " spread"
            ),
        },
        "against_what_this_line_has_measured": {
            "r1_window_pod_measured_v2_seconds_per_call": R1_MEASURED_SECONDS_PER_CALL,
            "charged_over_the_r1_window_pod": round(
                CHARGED_SECONDS_PER_CALL / R1_MEASURED_SECONDS_PER_CALL, 4
            ),
            "slowest_single_call_ever_measured": SLOWEST_CALL_EVER_MEASURED,
            "slowest_single_call_source": "results/pass1_probe_b_rows.jsonl",
            "rule": (
                "the charge is 1.37× the rate the r1 window pod actually ran at and just UNDER the"
                " slowest single reply this stack has ever measured. A pod slower than this line is"
                " killed by rung 4's projection and not discovered in a bill"
            ),
        },
        "why_no_margin": (
            "r1's margin — the multiplier quoted by name in"
            " supersedes.its_numbers_this_record_REPEALS is the rate it produced — was bought for"
            " the window's larger entity blocks, and the H6 row that"
            " measured its own reason found the growth an order of magnitude smaller than the"
            " margin. It was never what was missing. This line charges the SPREAD instead: a"
            " measured 2.25× between two pods, not a chosen multiplier"
        ),
    }


def request_width() -> dict:
    """The margin's old reason, re-measured over the 901 — kept as a CHECK, not as a price."""
    dev = json.loads(summary.read_text_or_refuse(DEV_PACK))
    sample = next(leg for leg in dev["legs"] if leg["name"] == "v2")["items"]
    owed = json.loads(summary.read_text_or_refuse(PACK))["legs"][0]["items"]

    def mean(items, key):
        return sum(key(one) for one in items) / len(items)

    return {
        "sample": summary.rel(DEV_PACK) + " leg v2 — the 200 rows the uplift was measured on",
        "population": PACK_NAME,
        "mean_rendered_chars_sample": round(mean(sample, lambda one: one["rendered_chars"]), 1),
        "mean_rendered_chars_population": round(mean(owed, lambda one: one["rendered_chars"]), 1),
        "ratio": round(
            mean(owed, lambda one: one["rendered_chars"])
            / mean(sample, lambda one: one["rendered_chars"]),
            6,
        ),
        "mean_entities_sample": round(mean(sample, lambda one: len(one["entities"])), 4),
        "mean_entities_population": round(mean(owed, lambda one: len(one["entities"])), 4),
        "widest_sample": max(one["rendered_chars"] for one in sample),
        "widest_population": max(one["rendered_chars"] for one in owed),
        "rule": (
            "this contract charges no margin for width, so this block is no longer a price — it is"
            " the CHECK that width is not what moved. The 901 are ~2 % wider than the rows the"
            " uplift was measured on, which is inside any reading of the rate and is why the rate"
            " is charged on the pod class instead"
        ),
    }


def probe_b_width() -> dict:
    """The other half of the same check: is the pod-class spread a WIDTH difference in disguise?"""
    rows = [
        json.loads(line)
        for line in summary.read_text_or_refuse(PROBE_B_ROWS).splitlines()
        if line.strip()
    ]
    dev = json.loads(summary.read_text_or_refuse(DEV_PACK))
    base = next(leg for leg in dev["legs"] if leg["name"] == "base")["items"]
    probe_chars = statistics.fmean(one["request_chars"] for one in rows)
    base_chars = statistics.fmean(one["rendered_chars"] for one in base)
    probe_out = statistics.fmean(one["emitted_chars"] for one in rows)
    base_out = statistics.fmean(
        json.loads(line)["emitted_chars"]
        for line in summary.read_text_or_refuse(DEV_BASE_ROWS).splitlines()
        if line.strip()
    )
    return {
        "probe_b_mean_request_chars": round(probe_chars, 1),
        "dev_base_mean_request_chars": round(base_chars, 1),
        "request_ratio": round(probe_chars / base_chars, 6),
        "probe_b_mean_emitted_chars": round(probe_out, 1),
        "dev_base_mean_emitted_chars": round(base_out, 1),
        "emitted_ratio": round(probe_out / base_out, 6),
        "rule": (
            "the two base pods are 2.25× apart in seconds. Their requests are 5.6 % apart and their"
            " replies 1.7 % apart, so neither the prefill nor the decode length explains it. This is"
            " the row that makes «the spread is the pod» a measurement rather than an inference —"
            " the r1 report eliminated five causes AFTER the money and this one is eliminated before"
            " it"
        ),
    }


def arithmetic(charged: dict, calls: int, overhead: dict, tail: dict) -> dict:
    """Every money figure of this contract, computed once here and re-derived by H6 from its terms."""
    per_call = float(charged["v2"])
    generation = round(calls * per_call, 2)
    pre_generation = SSH_DEADMAN_SECONDS + STAGE_LAUNCH_SECONDS + BOOT_SECONDS
    total = round(generation + pre_generation + OVERHEAD_SECONDS, 2)
    hours = total / 3600.0
    worst_usd = hours * PRICE_CEILING

    hard_stop_hours = HARD_STOP_SECONDS / 3600.0
    session_ceiling_seconds = round(CAP_USD / PRICE_CEILING * 3600.0, 1)

    dead_pod = SSH_DEADMAN_SECONDS
    dead_pod_usd = dead_pod / 3600.0 * PRICE_CEILING
    then_seconds = round(dead_pod + total, 2)
    then_usd = then_seconds / 3600.0 * PRICE_CEILING
    widest_dead_pod = round(HARD_STOP_SECONDS - total, 2)
    with_tail = round(dead_pod + tail["charged_seconds"] + total, 2)

    return {
        "calls": {"v2": calls},
        "seconds_per_call": charged,
        "generation_seconds": generation,
        "ssh_seconds_charged": SSH_DEADMAN_SECONDS,
        "ssh_readings": {
            "pass1-probe-b, 2026-08-18": 14.5,
            "juupgp6y77jvuz, 2026-08-20 (a lower bound)": 231.9,
            "7spsy61lpjumrz, 2026-08-20 (a lower bound)": 262.5,
            "8tpx8lf05n6skc, 2026-08-21 (an upper bound)": 50.0,
            f"{R1_POD}, 2026-08-21 (measured)": 29.0,
        },
        "ssh_rule": (
            f"rung 2's own ceiling, charged as a line of the budget. FIVE readings now and still no"
            " measurement of the worst case: 14.5 s on this card in this datacenter on 2026-08-18,"
            " two pods still `pod not ready` at 262.5 s and 231.9 s on 2026-08-20 (both LOWER"
            f" bounds), ≤ 50 s on 2026-08-21 and {R1_POD} answering at 29 s the same day. The"
            " ceiling stays where r2 put it — a spread with two unbounded readings in it is not"
            " narrowed by two fast ones"
        ),
        "stage_launch_seconds_charged": STAGE_LAUNCH_SECONDS,
        "stage_launch_rule": (
            "scp of the bundle and the runners, the clone, the volume check and the detached launch"
            " — r2's line, unmoved. This contract ALSO copies the volume's surviving out-file back"
            " before the run directory is cleared, and that scp is inside this line: r1 measured"
            " stage + launch at 54 s against the 150 charged, and the file is 70 KB"
        ),
        "boot_seconds_charged": BOOT_SECONDS,
        "boot_rule": (
            "≥ the worst boot this stack has measured (353.0 s, lora-b) — r2's derivation, unmoved,"
            f" and anchored on the runner's own `launched_at`. {R1_POD} loaded in 164.9 s, a sixth"
            " reading and another FLOOR: this stack's boot is not a constant and the ceiling is"
            " charged at the maximum"
        ),
        "boots_measured": {
            "lora-b, A6000 + the same volume": [267.0, 293.0, 353.0],
            "reader-v5b / pass1-probe stack, inference": [146.8, 192.1, 237.155],
            "pass1-probe-b, the 4090 this contract prefers": [237.155],
            "pass1-fewshot r2, the 4090 and the same volume": [142.709],
            f"pass1-window r1, {R1_POD}": [164.915],
        },
        "pre_generation_seconds": pre_generation,
        "pre_generation_rule": (
            f"ssh {SSH_DEADMAN_SECONDS:.0f} + stage/launch {STAGE_LAUNCH_SECONDS:.0f} + load"
            f" {BOOT_SECONDS:.0f} = {pre_generation:.0f} s, and it is ALSO rung 3's create-anchored"
            f" backstop. r1's pod MEASURED {R1_PRE_GENERATION_MEASURED} s for the whole span — a"
            " third of what is charged — and this record publishes rung 4's knife edge at BOTH,"
            " because a continuation's pre-generation is unknown and the CHARGED span is the one"
            " that governs the budget (Dv655)"
        ),
        "overhead_seconds": OVERHEAD_SECONDS,
        "overhead_rule": (
            f"{OVERHEAD_SECONDS:.0f} s — the copy-back of ≤ {calls} rows on every poll, the"
            " completeness gate on the Mac, and the deletion with its three listings. ssh and"
            " staging have their own lines above, so nothing here is counted twice"
        ),
        "overhead_measured_on_r2": overhead,
        "rows_copied_back": calls,
        "request_width": request_width(),
        "the_pod_class_is_not_a_width": probe_b_width(),
        "total_seconds": total,
        "hours": round(hours, 6),
        "worst_case_usd_at_the_price_ceiling": round(worst_usd, 6),
        "worst_case_usd_at_the_lora_b_price": round(hours * LORA_B_PRICE, 6),
        "cumulative": {
            "hard_stop_seconds": HARD_STOP_SECONDS,
            "hard_stop_hours": round(hard_stop_hours, 4),
            "hard_stop_usd_at_the_price_ceiling": round(hard_stop_hours * PRICE_CEILING, 4),
            "hard_stop_rule": (
                f"cumulative billed ≤ {HARD_STOP_SECONDS:.0f} s ="
                f" ${hard_stop_hours * PRICE_CEILING:.4f} at the ${PRICE_CEILING}/h ceiling. It sits"
                f" UNDER the ${CAP_USD:.2f} cap it defends and it is the PLATFORM that enforces it,"
                " so it protects even a hung call no gate can see. r1's stop does not carry over:"
                " that number was computed for 1 032 calls at a rate this contract repeals, and a"
                " stop copied for its algorithm would have brought its number with it (Dv613)"
            ),
            "session_ceiling_seconds": session_ceiling_seconds,
            "session_ceiling_hours": round(CAP_USD / PRICE_CEILING, 4),
            "session_ceiling_rule": (
                "cap / price ceiling — the longest session the cap can pay for. It is ≥ the hard"
                " stop, so the platform-held stop is the binding one and the cap is never what"
                " discovers an overrun"
            ),
            "backstop_tolerance_seconds": BACKSTOP_TOLERANCE_SECONDS,
            "backstop_tolerance_rule": (
                "how far the `--terminate-after` stamp actually handed to `pod create` may sit"
                " BEYOND the one the hard stop computes. Only overshoot is bounded — a window"
                " rounded DOWN shortens itself and is always safe. The gate READS it from here and"
                " a record without this field is a refusal, not a default"
            ),
            "rule": (
                "the hard stop and EVERY budget check count across ALL pods of this attempt, never"
                " per pod. `--terminate-after` on each pod is stamped at that pod's create plus the"
                " hard stop LESS what every closed pod already billed, so two pods cannot each be"
                " given a fresh window"
            ),
            "projection_gate": projection_gate(total, calls, per_call),
        },
        "recovery_arithmetic": {
            "re_creations_allowed": 1,
            "one_dead_pod_at_rung_2_seconds": dead_pod,
            "one_dead_pod_at_rung_2_usd": round(dead_pod_usd, 6),
            "deletion_tail": tail,
            "one_dead_pod_at_rung_2_with_the_measured_tail_seconds": round(
                dead_pod + tail["charged_seconds"], 2
            ),
            "one_dead_pod_at_rung_2_with_the_measured_tail_usd": round(
                (dead_pod + tail["charged_seconds"]) / 3600.0 * PRICE_CEILING, 6
            ),
            "then_the_full_worst_case_seconds": then_seconds,
            "then_the_full_worst_case_usd": round(then_usd, 6),
            "with_the_tail_then_the_full_worst_case_seconds": with_tail,
            "with_the_tail_then_the_full_worst_case_usd": round(
                with_tail / 3600.0 * PRICE_CEILING, 6
            ),
            "widest_dead_pod_that_still_fits_seconds": widest_dead_pod,
            "margin_after_the_tail_seconds": round(HARD_STOP_SECONDS - with_tail, 2),
            "rule": (
                "the recovery clause must stay REACHABLE after one dead pod. One dead pod at rung 2"
                f" plus the full worst case is {then_seconds:.2f} s ≤ {HARD_STOP_SECONDS:.0f} and"
                f" ${then_usd:.4f} ≤ ${CAP_USD:.2f}, so ONE re-creation fits by the registered"
                " arithmetic. `--pre-create-check` computes both bounds before every create, the"
                " stricter binds, and its verdict is RECORDED whichever way it goes — r1's printed"
                " the refusal that ended its session and wrote nothing down"
            ),
            "the_knife_edge": (
                f"the widest dead pod that still leaves the whole worst case inside the stop is"
                f" {widest_dead_pod:.2f} s of BILLED seconds, which is WIDER than rung 2's"
                f" {SSH_DEADMAN_SECONDS:.0f} s ceiling plus its measured deletion tail"
                f" ({dead_pod + tail['charged_seconds']:.1f} s) — so a pod killed by rung 2 can"
                " never be the one that closes the recovery clause"
            ),
            "which_KILLS_stay_recoverable": {
                "the_number_that_decides_it": round(widest_dead_pod - tail["charged_seconds"], 2),
                "what_it_is": (
                    "the widest CREATE-ELAPSED at which a pod may be killed and still leave the"
                    " re-creation reachable. The clause is checked on BILLED seconds and the meter"
                    f" runs until `pod delete`, so the charged tail of {tail['charged_seconds']} s"
                    f" comes off the {widest_dead_pod:.2f} s before the rung sees it"
                ),
                "rung_2": (
                    f"ALWAYS inside: its ceiling is {SSH_DEADMAN_SECONDS:.0f} s and with the tail it"
                    f" bills {dead_pod + tail['charged_seconds']:.1f} s ≤ {widest_dead_pod:.2f}"
                ),
                "rung_3": (
                    "SOMETIMES. Its launch-anchored ceiling can fire early and be inside, but its"
                    f" CREATE-anchored backstop is {pre_generation:.0f} s and a KILL there bills"
                    f" {pre_generation + tail['charged_seconds']:.1f} s — well outside"
                    f" {widest_dead_pod:.2f}. r1's record said «a KILL at rung 2 or rung 3 is inside"
                    " that window» and that half of the sentence was never true at these spans"
                ),
                "rung_4": (
                    "ONLY IN THE MEASURED WORLD, and this is the correction the five-lens review"
                    " made to this record. A rate KILL is recoverable only while the create-elapsed"
                    f" at the kill is ≤ {widest_dead_pod - tail['charged_seconds']:.2f} s. At the"
                    f" pre-generation this budget CHARGES ({pre_generation:.0f} s) that is already"
                    " past before the first call lands, so NO rung-4 kill is recoverable at any"
                    " rate and any call count. At the pre-generation r1's pod MEASURED"
                    f" ({R1_PRE_GENERATION_MEASURED} s) an 8 s/call pod dies about 20 calls in"
                    " having billed ≈ 412 s and the clause is reachable. Both arms, because a"
                    " continuation's pre-generation is unknown"
                    " ([[a_ceiling_derived_from_one_span_measured_over_another]])"
                ),
                "rung_5_and_rung_6": (
                    "never recoverable in practice: rung 5 fires after 600 s of idle on top of"
                    " whatever the pod had already billed, and rung 6 is the stop itself"
                ),
            },
            "the_tail_rule": (
                "rung 2's ceiling is a CREATE-ELAPSED and the meter stops at `pod delete`, not when"
                f" the rung fires. r1 measured that span twice — {tail['measured_seconds']} — and"
                f" the worse is charged, so the clause is reachable at {with_tail:.2f} s ≤"
                f" {HARD_STOP_SECONDS:.0f}, a margin of"
                f" {HARD_STOP_SECONDS - with_tail:.2f} s. The runbook says «delete immediately»"
                " because of this number"
            ),
            "a_second_dead_pod": (
                "STOP. After a second dead pod nothing fits and the session closes with no verdict"
                " — a THIRD pod under this registration is refused by the arithmetic and by this"
                " record. `--pre-create-check` READS `re_creations_allowed` and refuses the create"
                " itself, because at two CHEAP deaths the seconds would still fit and only the"
                " count says no"
            ),
        },
    }


def projection_gate(total: float, calls: int, per_call: float) -> dict:
    """Rung 4, and its knife edge published at BOTH values of the span this record carries two of."""

    def arm(pre_generation: float, source: str) -> dict:
        budget = HARD_STOP_SECONDS - OVERHEAD_SECONDS - pre_generation
        curve = []
        for at in (10, 20, 100, 200, 400, 700, 900):
            if at >= calls:
                continue
            curve.append(
                {
                    "at_call": at,
                    "create_elapsed_seconds": round(pre_generation + at * per_call, 1),
                    "kill_above_seconds_per_call": round(
                        (budget - at * per_call) / (calls - at), 3
                    ),
                }
            )
        sustained = budget / calls
        return {
            "pre_generation_seconds": pre_generation,
            "source": source,
            "sustained_rate_the_hard_stop_can_pay_for": round(sustained, 4),
            "headroom_over_the_slowest_call_measured": round(
                sustained / SLOWEST_CALL_EVER_MEASURED, 3
            ),
            "curve": curve,
        }

    charged_arm = arm(
        SSH_DEADMAN_SECONDS + STAGE_LAUNCH_SECONDS + BOOT_SECONDS,
        "money.arithmetic.pre_generation_seconds — and rung 3's own create-anchored backstop",
    )
    measured_arm = arm(
        R1_PRE_GENERATION_MEASURED,
        f"pod {R1_POD}'s create-elapsed at its first reply, 2026-08-21",
    )
    return {
        "every": f"{PROJECTION_EVERY_CALLS} calls",
        "formula": (
            "billed_by_closed_pods + elapsed_on_this_pod + the leg's remaining calls × its s/call +"
            " overhead_seconds. The leg is priced at its MEASURED rate — the larger of its mean and"
            " its last call — as soon as it has a reply, and at the registered rate before that"
        ),
        "overhead_seconds": OVERHEAD_SECONDS,
        "overhead_rule": (
            "the SAME 1 300 s the money block charges, and it has to be: rung 4 prices the attempt"
            " with it on every poll, so a second copy here is a second budget. H6 asserts the two"
            " are one number"
        ),
        "verdict": (
            f"KILL if the projection exceeds ${CAP_USD:.2f} at the LIVE price, or exceeds the"
            f" {HARD_STOP_SECONDS:.0f} s hard stop in seconds. The stricter binds"
        ),
        "why_one_leg": (
            "one leg, so «every leg still owed» and «the running leg» are the same set. The formula"
            " is r2's, imported unedited and not weakened"
        ),
        "why_there_is_no_separate_rate_rung": (
            "this rung IS the rate rung. It re-prices the remainder on every poll at max(mean, last"
            " call) and kills any pod that cannot finish inside the hard stop at the FIRST poll"
            " that shows it. A separate rung reading the same number against the same stop would be"
            " the same check twice, and two gates on one number is how a threshold gets repealed in"
            " one of them"
        ),
        "what_an_early_rate_KILL_costs_AT_BOTH_SPANS": (
            "the contract's own worked example is «a pod at 8 s/call dies ≈ 20 calls in, ≈ $0.10,"
            " re-creation still reachable». That is TRUE at the pre-generation r1's pod measured"
            f" ({R1_PRE_GENERATION_MEASURED} s: the kill lands at 412.5 s of create-elapsed,"
            " $0.0917 at the price ceiling, and the clause is reachable) and FALSE at the"
            f" pre-generation this budget CHARGES ({SSH_DEADMAN_SECONDS + STAGE_LAUNCH_SECONDS + BOOT_SECONDS:.0f} s:"
            " the same kill lands at 1 260 s, $0.28, and the re-creation is REFUSED). See"
            " recovery_arithmetic.which_KILLS_stay_recoverable for the number that decides it. Both"
            " arms are published because a continuation's pre-generation is unknown and the CHARGED"
            " span is the one that governs the budget — the review found this record quoting the"
            " flattering arm, which is the very defect it indicts r1 for two keys above"
        ),
        "single_call_sensitivity": {
            "formula": (
                "(hard_stop − overhead − pre_generation − n × charged_rate) / (calls − n), and the"
                " pre_generation is the span this record carries two values for"
            ),
            "charged_rate_seconds_per_call": per_call,
            "slowest_call_in_the_stack": SLOWEST_CALL_EVER_MEASURED,
            "at_the_CHARGED_pre_generation": charged_arm,
            "at_the_MEASURED_pre_generation": measured_arm,
            "the_headline": (
                "at the pre-generation the budget CHARGES, the sustained rate the hard stop can pay"
                f" for is {charged_arm['sustained_rate_the_hard_stop_can_pay_for']} s/call; the"
                f" slowest single call this stack has ever measured is"
                f" {SLOWEST_CALL_EVER_MEASURED}, so the edge sits"
                f" {charged_arm['headroom_over_the_slowest_call_measured']}× above it. At the"
                f" pre-generation r1's pod actually MEASURED ({R1_PRE_GENERATION_MEASURED} s) the"
                f" edge is {measured_arm['sustained_rate_the_hard_stop_can_pay_for']} s/call. BOTH"
                " arms are published and the WORSE is the headline — r1 computed this curve at the"
                " measured span while its budget charged the other one, and then wrote its headline"
                " off the flattering arm a section later (Dv630/655)"
            ),
            "what_it_costs_if_it_fires": (
                "the pod is deleted mid-run and the seconds already billed are gone. Every reply is"
                " flushed as it lands and the shipped resume skips every unit already answered —"
                " but `--pre-create-check` prices a re-creation at the FULL worst case ahead, so a"
                " KILL past the widest-dead-pod figure refuses the re-creation too. That is the"
                " whole cost, and it is what closed r1: its pod was paying its own 845 s out of the"
                " slack the stop had left"
            ),
            "what_the_executor_can_do_about_it": (
                "nothing after the create, and one thing before it: the charged pre-generation is"
                " ssh + stage/launch + load, and the staging half is HAND-DRIVEN. r1 measured ssh at"
                " 29 s, stage + launch at 54 s and the load at 164.9 s — 252.5 s against 1 100"
                " charged. Every second between the ssh GO and the launch is a second rung 4 will"
                " not lend to the rate, and rung 3's GO is where the executor reads which world the"
                " pod is in"
            ),
        },
    }


def bars(calls: int, window_calls: int) -> dict:
    """The completeness bar of THIS registration — and the window's own completeness beside it."""
    maximum = int(calls * REFUSALS_FRACTION)
    return {
        "completeness": {
            "rule": (
                f"answered {calls} / {calls} · every row's `rendering_sha256` equals its pack item's"
                f" · parse refusals ≤ {maximum} ({REFUSALS_FRACTION:.0%}). All three, or RED"
            ),
            "owed": calls,
            "answered_minimum": calls,
            "sha_mismatches_maximum": 0,
            "parse_refusals_maximum": maximum,
            "parse_refusals_fraction": REFUSALS_FRACTION,
            "answered_means": (
                "a reply came back and was written into the out-file, counted by DISTINCT id. A"
                " parse refusal is an ANSWERED row whose reply the parser refused — the two counts"
                f" are NOT disjoint, and up to {maximum} answered rows may be refusals without the"
                " bar moving. A gate that treated a refusal as unanswered would report RED at"
                f" {calls - maximum} / {calls} on a run this bar accepts"
                " ([[measure_on_the_rows_the_gate_scores]])"
            ),
            "refusals_are_counted_by_cause": (
                "never dropped and never summed into a single «other». An unreadable reply is a"
                " disagreement with a name, and unreadable replies pile up wherever the answer is"
                " the quiet one ([[the_empty_class_eats_the_parse_failures]])"
            ),
            "sha_rule": (
                "the pod re-renders every item from its own fields and REFUSES the whole leg if one"
                " sha does not match, so a mismatch on the Mac means the out-file and the pack have"
                " parted after the run — a copy-back error or a rebuilt pack. Either is RED"
            ),
            "why_the_count_moved_from_r1": (
                f"the FRACTION is r1's and the count is derived from it: 1 % of {calls} is"
                f" {maximum}. Carrying r1's own count across a population that shrank by 131 rows"
                " would have been a threshold that quietly stopped meaning what it said"
                " ([[a_moved_constant_fails_green]])"
            ),
        },
        "the_windows_completeness": {
            "not_a_bar_of_this_registration": True,
            "owed": window_calls,
            "rule": (
                f"D2 reports the WINDOW's completeness — answered / {window_calls} over the UNION of"
                " r1's out-file and this one — BESIDE the bar above. It is the number pass 2 needs"
                " and it is not what this registration can pass or fail: this contract bought 901"
                " comments and can only be graded on them. A GO here with the union short of"
                f" {window_calls} is a GO on this contract and an open window, and the report says"
                " both"
            ),
            "keyed_on": (
                "the PAIR (thread, msg_id). Seven msg_ids of the 650 labelled rows live in two"
                " threads each and the union is taken across two files — a union keyed on the"
                " msg_id would silently merge them (the ADDENDUM of docs/reports/pass1-window.md)"
            ),
        },
        "report_only": {
            "our_readings": ["категория_личное", "молочный_бренд"],
            "our_readings_rule": (
                "the two labels the «our rows» readings count, carried here because"
                " gate_pass1_fewshot.py::leg_table — the function D2's clause names — reads them"
                " from `bars.dev_gate.our_readings`, a key this record does not have and must not"
                " invent: this contract has NO dev gate. D2 hands leg_table a view carrying these"
                " readings under the name it reads, ONE THREAD AT A TIME, because within a thread a"
                " msg_id is unique and the scorer's answer map is keyed on the msg_id alone"
            ),
            "rule": (
                "READINGS, each captioned «not a bar». None of them can pass, fail or close"
                " anything, and none of them may be quoted as a verdict on v2"
            ),
            "the_fourteen": (
                "the gold rows' agreement over the WHOLE window, with the multiplicity named — the"
                " FIFTH look at these fourteen rows. See `return_to_the_operator`"
            ),
            "the_650_labelled_rows": (
                "agreement over every labelled row of the window, against"
                " results/labels_pass1_r1.jsonl + _r2.jsonl through scorer.reader_comment_agreement"
                " as gate_pass1_fewshot.py::leg_table computes it, scored per THREAD"
            ),
            "the_450_not_in_dev_200": (
                "the same reading on the rows no prompt was ever tuned against. Its «our»"
                " denominator is ZERO BY CONSTRUCTION and always will be (Dv652)"
            ),
            "the_dev_200": (
                "should reproduce r2's 136/200 and 38/49 up to decoding noise, now over all 200"
                " rows for the first time on this population. A difference is STATED and not"
                " explained away"
            ),
            "the_label_distribution": "what v2 said over the union 1 032, and per thread",
            "the_pass_2_filter_table": (
                "per thread, over the WHOLE window: the rows pass 1 labelled категория_личное /"
                " молочный_бренд / сеть_ритейлер, their characters and the entity block size. THIS"
                " is what prices `pass2-signals` — r1's census covered 24 of 127 callable threads"
                " and could not"
            ),
            "the_rows_bought_twice": (
                "the volume's surviving out-file is copied back as EVIDENCE and its rows beyond the"
                " Mac's 131 are counted and PRICED («N rows bought twice, N × the measured"
                " s/call»). It is never merged: two answers for one id is an ambiguity this"
                " registration does not buy"
            ),
        },
    }


def kill_clock(sums: dict, bar: dict) -> list[dict]:
    """r1's rungs, inherited BY NAME — and every number in them read out of THIS record."""
    recovery = sums["recovery_arithmetic"]
    return [
        {
            "rung": 1,
            "before": "the endpoint exists",
            "read": "costPerHr in the create response is the meter of record (Dv448)",
            "rule": (
                f"live price > ${PRICE_CEILING}/h at create → STOP, no endpoint. The backstop stamp"
                " is checked against the cumulative hard stop in the same command, and `--price`"
                " runs the recovery clause on the state BEFORE this pod joins it (Dv615)"
            ),
        },
        {
            "rung": 2,
            "before": "the model is loaded",
            "read": "money.arithmetic.ssh_rule — the spread this ceiling is, and its five readings",
            "rule": (
                f"ssh dead-man ≤ {SSH_DEADMAN_SECONDS:.0f} s of this pod's create-elapsed or KILL."
                " r2's ceiling, unmoved: two pods of 2026-08-20 were still unreachable past 230 s"
                " and both readings are LOWER bounds, so two fast days do not narrow it. One dead"
                f" pod under it costs ${recovery['one_dead_pod_at_rung_2_usd']:.4f}"
            ),
        },
        {
            "rung": 3,
            "anchor": "launched_at",
            "before": "the first reply",
            "read": (
                "the `launched_at` stamp the runbook writes into the pod's run directory the moment"
                f" the runner starts, copied back by --watch and recorded in {RUN_RECORD}. It is"
                " never typed"
            ),
            "rule": (
                f"launch → first reply ≤ {BOOT_SECONDS:.0f} s of the runner's OWN `launched_at` or"
                " KILL. A run record without `launched_at` cannot report GO on this rung — a"
                " deadline that cannot be demonstrated has not been passed (Dv605)"
            ),
            "backstop_seconds": sums["pre_generation_seconds"],
            "backstop_rule": (
                "and a create-anchored BACKSTOP beside it: first reply ≤"
                f" {sums['pre_generation_seconds']:.0f} s of create-elapsed or KILL — ssh"
                f" {SSH_DEADMAN_SECONDS:.0f} + stage/launch {STAGE_LAUNCH_SECONDS:.0f} + load"
                f" {BOOT_SECONDS:.0f}. It bounds the launch anchor: a stamp taken late cannot buy a"
                " window the registration never priced"
            ),
            "and_it_is_where_the_executor_reads_the_MONEY_world": (
                "this rung's GO carries `first_reply_at_create_elapsed_seconds`, and that number"
                " says which arm of money.arithmetic.cumulative.projection_gate."
                "single_call_sensitivity the pod is in. r1 recorded it at 252.5 s of a 1 100 s"
                " backstop and never had to act on it; the runbook makes it a reading the executor"
                " takes deliberately"
            ),
            "cannot_always_be_a_standalone_gate": (
                "`--boot` needs a LIVE pod, and a watch KILL deletes the pod inside its own loop."
                " On a killed run this rung is reported from the artifacts — the launch stamp, the"
                " first row's `boot_seconds` and `elapsed_since_start` — and never back-filled"
                " (Dv649, [[a_registered_bar_may_have_no_producer]])"
            ),
        },
        {
            "rung": 4,
            "before": "the run is allowed to continue past a call",
            "read": "money.arithmetic.cumulative.projection_gate — the formula and its terms",
            "rule": (
                f"projection gate every {PROJECTION_EVERY_CALLS} calls: the projected attempt total"
                " at MEASURED rates, with the leg's remaining calls priced at max(mean, last call)"
                " and the registered overhead added, must fit the cap at the LIVE price AND the"
                " cumulative hard stop, else KILL. The registered interval is a FLOOR — the"
                " computation is local and free and --watch runs it on every poll"
            ),
            "this_is_the_rate_rung": (
                "and there is no other. It killed r1's pod correctly at 131 of 1 032 and it is the"
                " gate that makes charging a rate at all survivable: a pod slower than the charge"
                " is deleted at the first poll that shows it. See"
                " projection_gate.why_there_is_no_separate_rate_rung"
            ),
        },
        {
            "rung": 5,
            "before": "the executor may look away",
            "read": f"held by {summary.rel(GATE)} --watch, a BLOCKING loop",
            "rule": (
                f"liveness: {IDLE_DEADLINE_SECONDS:.0f} s with no new answered row and no new"
                " pod-log line → KILL. The deadline is measured from the LAST EVENT and never from"
                " create, and an event is a RISE — a failed copy that shortens a local file is not"
                " work and does not refresh it"
            ),
        },
        {
            "rung": 6,
            "before": "anything",
            "read": "the `--terminate-after` stamp, read back and refused on overshoot",
            "rule": (
                f"cumulative hard stop {HARD_STOP_SECONDS:.0f} s, PLATFORM-held. Each pod's"
                " --terminate-after is its own create plus what the stop has left, and the"
                f" overshoot it forgives is the registered {BACKSTOP_TOLERANCE_SECONDS:.0f} s"
            ),
        },
        {
            "rung": 7,
            "before": "the out-file is handed to pass 2",
            "read": "bars.completeness — all three numbers, on the Mac after scp",
            "rule": bar["completeness"]["rule"],
            "and_the_window_beside_it": bar["the_windows_completeness"]["rule"],
            "on_red": (
                "RED does not delete anything already bought and does not re-run the pod: the"
                " out-file, its refusals by cause and its sha mismatches go back to the team lead"
                " with the census. A partial out-file is still the evidence, and the resume can"
                " re-ask only what has no reply — but a second pod is the recovery clause's, and"
                " the recovery clause allows one"
            ),
        },
    ]


def h6(sums: dict, charged: dict, calls: int, window_calls: int, bar: dict) -> dict:
    """Every number the contract prints, re-derived from the formula the contract names for it."""
    cumulative = sums["cumulative"]
    recovery = sums["recovery_arithmetic"]
    gate = cumulative["projection_gate"]["single_call_sensitivity"]
    charged_arm = gate["at_the_CHARGED_pre_generation"]
    measured_arm = gate["at_the_MEASURED_pre_generation"]
    klass = charged["the_pod_class"]
    width = sums["the_pod_class_is_not_a_width"]
    overhead = sums["overhead_measured_on_r2"]
    scaled = round(
        overhead["measured_after_the_last_row_seconds"] / overhead["rows_answered"] * calls, 1
    )

    rows = [
        # --- the population ---
        {
            "name": "population_owed",
            "formula": f"{PACK_NAME}: the r1 pack's leg MINUS the ids of the r1 out-file",
            "registered": 901,
            "re_derived": calls,
            "mode": "equals",
        },
        {
            "name": "the_owed_plus_what_r1_bought_is_the_window",
            "formula": "901 owed + 131 answered by r1 = the window's 1 032 payable comments",
            "registered": 1032,
            "re_derived": window_calls,
            "mode": "equals",
        },
        # --- the rate, from three files ---
        {
            "name": "slowest_base_pod_seconds_per_call",
            "formula": "mean of `seconds` over 64 rows of results/pass1_probe_b_rows.jsonl",
            "registered": 5.162,
            "re_derived": klass["slowest_base_pod_seconds_per_call"],
            "mode": "equals",
        },
        {
            "name": "fastest_base_pod_seconds_per_call",
            "formula": "mean of `seconds` over 200 rows of results/pass1_dev_base.jsonl",
            "registered": 2.293,
            "re_derived": klass["fastest_base_pod_seconds_per_call"],
            "mode": "equals",
        },
        {
            "name": "the_pod_class_spread",
            "formula": "the slowest base pod over the fastest, ONE prompt, two pods",
            "registered": 2.25,
            "re_derived": klass["spread"],
            "mode": "equals",
        },
        {
            "name": "v2_over_base_uplift",
            "formula": "mean(results/pass1_dev_v2.jsonl) / mean(results/pass1_dev_base.jsonl)",
            "registered": 1.189,
            "re_derived": charged["the_uplift"]["v2_over_base"],
            "mode": "equals",
        },
        {
            "name": "seconds_per_call_derived",
            "formula": "mean(probe-b) × the uplift",
            "registered": 6.14,
            "re_derived": charged["derived"],
            "mode": "equals",
        },
        {
            "name": "the_charged_rate_is_not_below_the_derivation",
            "formula": (
                "the rounding of this line is UP, which is the conservative direction: a charge"
                " under the derived rate buys seconds the arithmetic does not have"
            ),
            "registered": charged["derived"],
            "re_derived": charged["charged"],
            "mode": "at_least",
        },
        {
            "name": "the_charge_is_above_what_the_r1_window_pod_ran_at",
            "formula": (
                f"the charge over pod {R1_POD}'s measured {R1_MEASURED_SECONDS_PER_CALL} s/call —"
                " the only v2 rate this line has measured on a window pod"
            ),
            "registered": R1_MEASURED_SECONDS_PER_CALL,
            "re_derived": charged["charged"],
            "mode": "at_least",
        },
        # --- the seconds and the dollars ---
        {
            "name": "generation_seconds",
            "formula": f"{calls} calls × {charged['charged']} s/call",
            "registered": 5532.14,
            "re_derived": sums["generation_seconds"],
            "mode": "equals",
        },
        {
            "name": "total_seconds",
            "formula": (
                f"ssh {SSH_DEADMAN_SECONDS:.0f} + stage/launch {STAGE_LAUNCH_SECONDS:.0f} + load"
                f" {BOOT_SECONDS:.0f} + generation {sums['generation_seconds']} + overhead"
                f" {OVERHEAD_SECONDS:.0f}"
            ),
            "registered": 7932.14,
            "re_derived": sums["total_seconds"],
            "mode": "equals",
        },
        {
            "name": "hours",
            "formula": f"{sums['total_seconds']} / 3600",
            "registered": 2.2034,
            "re_derived": sums["hours"],
            "mode": "equals",
        },
        {
            "name": "worst_case_usd_at_the_price_ceiling",
            "formula": f"{sums['hours']} h × ${PRICE_CEILING}/h",
            "registered": 1.7627,
            "re_derived": sums["worst_case_usd_at_the_price_ceiling"],
            "mode": "equals",
        },
        {
            "name": "worst_case_usd_at_the_lora_b_price",
            "formula": f"{sums['hours']} h × ${LORA_B_PRICE}/h",
            "registered": 1.1678,
            "re_derived": sums["worst_case_usd_at_the_lora_b_price"],
            "mode": "equals",
        },
        {
            "name": "the_worst_case_is_inside_the_cap",
            "formula": f"worst case ≤ ${CAP_USD:.2f}",
            "registered": CAP_USD,
            "re_derived": sums["worst_case_usd_at_the_price_ceiling"],
            "mode": "below",
        },
        # --- the cumulative stop ---
        {
            "name": "hard_stop_usd_at_the_price_ceiling",
            "formula": f"{HARD_STOP_SECONDS:.0f} s / 3600 × ${PRICE_CEILING}/h",
            "registered": 1.9111,
            "re_derived": cumulative["hard_stop_usd_at_the_price_ceiling"],
            "mode": "equals",
        },
        {
            "name": "the_hard_stop_sits_under_the_cap",
            "formula": f"hard stop in dollars ≤ ${CAP_USD:.2f}",
            "registered": CAP_USD,
            "re_derived": cumulative["hard_stop_usd_at_the_price_ceiling"],
            "mode": "below",
        },
        {
            "name": "the_hard_stop_is_above_the_worst_case",
            "formula": f"{HARD_STOP_SECONDS:.0f} s ≥ the whole worst case in seconds",
            "registered": sums["total_seconds"],
            "re_derived": HARD_STOP_SECONDS,
            "mode": "at_least",
        },
        {
            "name": "session_ceiling_seconds",
            "formula": f"${CAP_USD:.2f} / ${PRICE_CEILING}/h × 3600",
            "registered": 9000.0,
            "re_derived": cumulative["session_ceiling_seconds"],
            "mode": "equals",
        },
        {
            "name": "the_session_ceiling_is_not_below_the_hard_stop",
            "formula": (
                "cap / price ceiling ≥ the hard stop, so the PLATFORM holds the binding one"
            ),
            "registered": HARD_STOP_SECONDS,
            "re_derived": cumulative["session_ceiling_seconds"],
            "mode": "at_least",
        },
        # --- the recovery clause ---
        {
            "name": "one_dead_pod_at_rung_2_usd",
            "formula": f"{SSH_DEADMAN_SECONDS:.0f} s / 3600 × ${PRICE_CEILING}/h",
            "registered": 0.1111,
            "re_derived": recovery["one_dead_pod_at_rung_2_usd"],
            "mode": "equals",
        },
        {
            "name": "one_dead_pod_then_the_full_worst_case_seconds",
            "formula": f"{SSH_DEADMAN_SECONDS:.0f} + {sums['total_seconds']}",
            "registered": 8432.14,
            "re_derived": recovery["then_the_full_worst_case_seconds"],
            "mode": "equals",
        },
        {
            "name": "the_recovery_clause_fits_the_hard_stop",
            "formula": f"one dead pod + the full worst case ≤ {HARD_STOP_SECONDS:.0f} s",
            "registered": HARD_STOP_SECONDS,
            "re_derived": recovery["then_the_full_worst_case_seconds"],
            "mode": "below",
        },
        {
            "name": "one_dead_pod_then_the_full_worst_case_usd",
            "formula": f"{recovery['then_the_full_worst_case_seconds']} s / 3600 × ${PRICE_CEILING}/h",
            "registered": 1.8738,
            "re_derived": recovery["then_the_full_worst_case_usd"],
            "mode": "equals",
        },
        {
            "name": "the_recovery_clause_fits_the_cap",
            "formula": f"one dead pod + the full worst case ≤ ${CAP_USD:.2f}",
            "registered": CAP_USD,
            "re_derived": recovery["then_the_full_worst_case_usd"],
            "mode": "below",
        },
        {
            "name": "widest_dead_pod_that_still_fits_seconds",
            "formula": f"{HARD_STOP_SECONDS:.0f} − {sums['total_seconds']}",
            "registered": 667.86,
            "re_derived": recovery["widest_dead_pod_that_still_fits_seconds"],
            "mode": "equals",
        },
        {
            "name": "the_knife_edge_is_wider_than_rung_2",
            "formula": (
                "the widest dead pod that still fits ≥ rung 2's ceiling, so a pod killed by rung 2"
                " can never be the one that closes the recovery clause"
            ),
            "registered": SSH_DEADMAN_SECONDS,
            "re_derived": recovery["widest_dead_pod_that_still_fits_seconds"],
            "mode": "at_least",
        },
        {
            "name": "REASON — the recovery clause is reachable WITH the measured deletion tail",
            "formula": (
                "rung 2's ceiling is a create-elapsed and the meter stops at `pod delete`. r1"
                f" measured that span at {recovery['deletion_tail']['measured_seconds']} and the"
                f" worse is charged, so a real rung-2 death bills"
                f" {recovery['one_dead_pod_at_rung_2_with_the_measured_tail_seconds']} s and not"
                f" {SSH_DEADMAN_SECONDS:.0f}. That plus the full worst case must still fit the hard"
                f" stop — it does, by {recovery['margin_after_the_tail_seconds']} s, which is the"
                " honest margin and is 18× wider than r1's 4.96 s"
            ),
            "registered": HARD_STOP_SECONDS,
            "re_derived": recovery["with_the_tail_then_the_full_worst_case_seconds"],
            "mode": "below",
        },
        # --- the rungs' own numbers ---
        {
            "name": "the_widest_rate_KILL_that_stays_recoverable_seconds",
            "formula": (
                "widest_dead_pod_that_still_fits (BILLED) minus the charged deletion tail — the"
                " widest CREATE-ELAPSED at which a pod may be killed with the re-creation still"
                " reachable"
            ),
            "registered": 589.36,
            "re_derived": recovery["which_KILLS_stay_recoverable"]["the_number_that_decides_it"],
            "mode": "equals",
        },
        {
            "name": "REASON — a rung-2 death is ALWAYS inside the recovery window",
            "formula": (
                f"rung 2's ceiling {SSH_DEADMAN_SECONDS:.0f} s plus the charged deletion tail"
                f" {recovery['deletion_tail']['charged_seconds']} s, against the widest dead pod in"
                " BILLED seconds"
            ),
            "registered": recovery["widest_dead_pod_that_still_fits_seconds"],
            "re_derived": recovery["one_dead_pod_at_rung_2_with_the_measured_tail_seconds"],
            "mode": "below",
        },
        {
            "name": "REASON — a rung-3 BACKSTOP death is NEVER inside it, and r1's record said it was",
            "formula": (
                "rung 3's create-anchored backstop is the charged pre-generation, so a KILL there"
                " bills the backstop plus the tail. r1's recovery block carried «a KILL at rung 2 or"
                " rung 3 is inside that window» and the second half was never true at these spans."
                " The check asserts the INEQUALITY that makes it false, so the sentence cannot come"
                " back ([[a_borrowed_rule_carries_an_unstated_population]])"
            ),
            "registered": recovery["widest_dead_pod_that_still_fits_seconds"],
            "re_derived": round(
                sums["pre_generation_seconds"] + recovery["deletion_tail"]["charged_seconds"], 2
            ),
            "mode": "at_least",
        },
        {
            "name": "REASON — at the CHARGED pre-generation NO rate KILL is recoverable, at any rate",
            "formula": (
                "the charged pre-generation is already past the widest recoverable create-elapsed"
                " BEFORE the first call lands, so every rung-4 KILL in that world is a STOP. The"
                " contract's worked example («8 s/call, ≈ 20 calls in, ≈ $0.10, re-creation still"
                f" reachable») holds at the {R1_PRE_GENERATION_MEASURED} s r1 MEASURED and at no"
                " pre-generation above"
                f" {recovery['which_KILLS_stay_recoverable']['the_number_that_decides_it'] - 20 * 8.0:.2f} s."
                " Both arms are published; this row is the inequality that makes the flattering one"
                " unquotable"
            ),
            "registered": recovery["which_KILLS_stay_recoverable"]["the_number_that_decides_it"],
            "re_derived": sums["pre_generation_seconds"],
            "mode": "at_least",
        },
        {
            "name": "boot_ceiling_over_the_worst_measured_boot",
            "formula": f"{BOOT_SECONDS:.0f} s ≥ max(every boot this stack has measured)",
            "registered": WORST_MEASURED_BOOT,
            "re_derived": BOOT_SECONDS,
            "mode": "at_least",
        },
        {
            "name": "ssh_deadman_over_the_widest_2026_08_20_reading",
            "formula": (
                f"{SSH_DEADMAN_SECONDS:.0f} s ≥ the widest 2026-08-20 reading"
                f" ({WIDEST_SSH_READING} s), and both readings that day are LOWER bounds"
            ),
            "registered": WIDEST_SSH_READING,
            "re_derived": SSH_DEADMAN_SECONDS,
            "mode": "at_least",
        },
        {
            "name": "the_projection_gate_and_the_money_block_charge_ONE_overhead",
            "formula": (
                "rung 4 prices the attempt with the overhead on every poll, so a second copy would"
                " be a second budget"
            ),
            "registered": sums["overhead_seconds"],
            "re_derived": cumulative["projection_gate"]["overhead_seconds"],
            "mode": "equals",
        },
        {
            "name": "parse_refusals_maximum",
            "formula": f"{REFUSALS_FRACTION:.0%} of {calls} calls, floored",
            "registered": 9,
            "re_derived": bar["completeness"]["parse_refusals_maximum"],
            "mode": "equals",
        },
        # --- rung 4's knife edge, at BOTH spans ---
        {
            "name": "rung_4_knife_edge_at_the_CHARGED_pre_generation",
            "formula": (
                f"({HARD_STOP_SECONDS:.0f} − {OVERHEAD_SECONDS:.0f} −"
                f" {sums['pre_generation_seconds']:.0f}) / {calls}"
            ),
            "registered": 6.88,
            "re_derived": charged_arm["sustained_rate_the_hard_stop_can_pay_for"],
            "mode": "equals",
        },
        {
            "name": "rung_4_knife_edge_at_the_MEASURED_pre_generation",
            "formula": (
                f"({HARD_STOP_SECONDS:.0f} − {OVERHEAD_SECONDS:.0f} −"
                f" {R1_PRE_GENERATION_MEASURED}) / {calls}"
            ),
            "registered": 7.82,
            "re_derived": measured_arm["sustained_rate_the_hard_stop_can_pay_for"],
            "mode": "equals",
        },
        {
            "name": "REASON — the CHARGED span is the tighter arm and it is the headline",
            "formula": (
                "the record carries two values for one span and the headline must quote the worse."
                " r1 computed this curve at the measured span while its budget charged the other"
                " one, then wrote its headline off the flattering arm a section later (Dv655). The"
                " check is that the charged arm's edge is the SMALLER of the two"
            ),
            "registered": measured_arm["sustained_rate_the_hard_stop_can_pay_for"],
            "re_derived": charged_arm["sustained_rate_the_hard_stop_can_pay_for"],
            "mode": "below",
        },
        {
            "name": "REASON — the budget's own sustained rate covers the rate it CHARGES",
            "formula": (
                "at the charged pre-generation the sustained rate the hard stop can pay for is"
                f" {charged_arm['sustained_rate_the_hard_stop_can_pay_for']} s/call and the rate"
                f" charged is {charged['charged']}. This is the inequality that makes the budget"
                " self-consistent"
            ),
            "registered": charged["charged"],
            "re_derived": charged_arm["sustained_rate_the_hard_stop_can_pay_for"],
            "mode": "at_least",
        },
        {
            "name": "REASON — the charged edge is above the SLOWEST CALL this stack has measured",
            "formula": (
                f"the slowest single reply ever measured here is {SLOWEST_CALL_EVER_MEASURED} s"
                " (probe-b). Rung 4 prices the remainder at max(mean, last call), so one such call"
                " landing as the most recent row must NOT project past the stop. r1's charged-span"
                " edge was 3.9729 against a measured worst of 4.066 — BELOW it, headroom 0.98, and"
                " that was reported to the operator as the risk it was"
            ),
            "registered": SLOWEST_CALL_EVER_MEASURED,
            "re_derived": charged_arm["sustained_rate_the_hard_stop_can_pay_for"],
            "mode": "at_least",
        },
        # --- the reasons ---
        {
            "name": "REASON — the pod-class spread is not a WIDTH difference in disguise",
            "formula": (
                f"the two base pods are {klass['spread']}× apart in seconds. Their requests are"
                f" {width['request_ratio']}× apart and their replies {width['emitted_ratio']}×"
                " apart, so neither the prefill nor the decode explains it. The check is that the"
                " seconds ratio EXCEEDS the request ratio — if width explained the spread it would"
                " not"
            ),
            "registered": width["request_ratio"],
            "re_derived": klass["spread"],
            "mode": "at_least",
        },
        {
            "name": "REASON — the overhead did not move when the rows it covers went 400 → 901",
            "formula": (
                f"r2's pod was deleted {overhead['measured_after_the_last_row_seconds']} s after its"
                f" last row landed, and that span carried the whole of what this line buys. Scaled"
                f" by the {overhead['rows_answered']} rows it MEASURED it is {scaled} s for"
                f" {calls}, and {OVERHEAD_SECONDS:.0f} s is charged. The scaling is generous: r2's"
                " gate ran the SCORER over its rows and rung 7 only parses them"
            ),
            "registered": scaled,
            "re_derived": OVERHEAD_SECONDS,
            "mode": "at_least",
        },
        {
            "name": "REASON — nothing is counted twice in the seconds line",
            "formula": (
                "ssh, stage/launch, load, generation and overhead are five disjoint spans and their"
                " sum is total_seconds. The copy-back of the volume's surviving out-file is inside"
                " stage/launch and is not a sixth line"
            ),
            "registered": sums["total_seconds"],
            "re_derived": round(
                SSH_DEADMAN_SECONDS
                + STAGE_LAUNCH_SECONDS
                + BOOT_SECONDS
                + sums["generation_seconds"]
                + OVERHEAD_SECONDS,
                2,
            ),
            "mode": "equals",
        },
        {
            "name": "REASON — the bar is reachable: the leg asks exactly what the bar owes",
            "formula": (
                "answered_minimum = owed = the pack's item count. A bar registered over a number"
                " the leg does not ask is a bar no run can take"
                " ([[an_absolute_bar_needs_a_reachability_state]])"
            ),
            "registered": calls,
            "re_derived": bar["completeness"]["answered_minimum"],
            "mode": "equals",
        },
        {
            "name": "step_sum_usd",
            "formula": (
                "r1's pod on the clock ($0.173694) + this contract's cap. r1's step ledger stays"
                " OPEN for `money-anchors`; this contract opens a FRESH step with its own cap"
            ),
            "registered": 2.1737,
            "re_derived": round(0.173694 + CAP_USD, 6),
            "mode": "equals",
        },
    ]

    mismatches = []
    for row in rows:
        registered, derived = float(row["registered"]), float(row["re_derived"])
        if row["mode"] == "equals":
            agrees = abs(derived - registered) <= abs(registered) * 0.01
        elif row["mode"] == "at_least":
            agrees = derived >= registered
        elif row["mode"] == "below":
            agrees = derived <= registered
        else:
            raise SystemExit(f"{row['name']}: {row['mode']} is not an H6 mode — stop.")
        row["agrees"] = agrees
        if not agrees:
            mismatches.append(row)
    return {
        "rule": (
            "every number docs/PROMPT-pass1-window-r2.md prints, re-derived from the formula the"
            " contract names for it. `equals` allows 1 % — a rounding is not a finding; `below` and"
            " `at_least` check the DIRECTION. The rows that matter are the INPUT rows: the"
            " arithmetic of a money block is the same multiplication done twice and cannot disagree"
            " with itself, so what H6 catches is a population that moved, a rate whose file no"
            " longer says what it said, and an inequality that stopped holding"
        ),
        "reading": "every registered number re-derives",
        "rows": rows,
        "mismatches": mismatches,
    }


MOVED = {
    "gate.script": "scripts/gate_pass1_window_r2.py",
    "packs.producer": "scripts/build_pass1_window_r2_pack.py",
}
"""The two instruments this registration genuinely replaces. Everything else in r1's block is copied
and then held to the live file."""


def instruments(r1: dict) -> dict:
    """r1's instruments, copied — then every pin resolved live, and the two that MOVE re-pinned."""
    block = json.loads(json.dumps(r1["instruments"]))
    drifted = {
        path: {"copied_from_r1": r1prod.dig(block, path), "live": value}
        for path, value in r1prod.live_pins().items()
        if r1prod.dig(block, path) != value
    }
    if drifted:
        raise SystemExit(
            "a pin copied out of r1 no longer describes this checkout: "
            + json.dumps(drifted, ensure_ascii=False, indent=2)
            + "\nThis contract renders the 901 through the SAME functions r1 rendered the 1 032"
            " through — the items are literally r1's items. A pin that has moved is a different"
            " instrument and needs the operator."
        )

    block["gate"] = {
        "script": MOVED["gate.script"],
        "sha256": sha(GATE),
        "moved_since_r1": True,
        "rule": (
            "a SIBLING of scripts/gate_pass1_window.py, and a sibling of an unusual kind: it LOADS"
            " that file a second time under its own module object (importlib) and re-binds the six"
            " path globals — PHASE, PREREG, RECORD, PACK, POD_LOG, LAUNCH_STAMP. The rung logic is"
            " not copied and not re-implemented: it is r1's, executing, byte for byte, against this"
            " registration. r1's gate is pinned by ITS sealed record and is never edited, and this"
            " file refuses to run if its sha ever moves"
        ),
        "what_changed_at_all": (
            "one behaviour: `--pre-create-check` is intercepted and its verdict is APPENDED to the"
            " run record every time it runs, GO and KILL alike. r1's printed the refusal that ended"
            " its session and recorded nothing — step 0.5's second finding"
        ),
        "why_not_a_flag_on_r1s_gate": (
            "docs/PROMPT-pass1-window-r2.md allows `--revision r2` only if r1's pinned bytes stay"
            " untouched. scripts/gate_pass1_window.py is pinned by"
            " results/prereg_pass1_window.json::instruments.gate.sha256, a sealed record of a closed"
            " PAID session, so any flag added to it moves those bytes. Dv624's split stands"
        ),
    }
    block["gate_runs_the_bytes_of"] = {
        "script": "scripts/gate_pass1_window.py",
        "sha256": sha(REPO_ROOT / "scripts" / "gate_pass1_window.py"),
        "pinned_by": f"{R1_PREREG_NAME}::instruments.gate.sha256",
        "rule": (
            "the sibling above holds this file to exactly this sha BEFORE it executes it. An"
            " imported instrument is an instrument, and an EXECUTED one is more so"
            " ([[the_guard_hashes_the_half_that_cannot_move]])"
        ),
    }
    block["gate_imported_from"] = {
        "script": "scripts/gate_pass1_fewshot.py",
        "sha256": sha(REPO_ROOT / "scripts" / "gate_pass1_fewshot.py"),
        "also_imported": {
            "scripts/window_summary_5c2.py": sha(REPO_ROOT / "scripts" / "window_summary_5c2.py"),
            "why": (
                "the gate hashes the pack through window_summary_5c2.sha256_of, so that file is an"
                " instrument of the pack guard"
            ),
        },
        "rule": (
            "every pure rung computation — rung, clock, pre_create, gate_zero, gate_boot, leg_state,"
            " projection, scp, pod_delete — comes from here, through r1's gate, unedited. This is"
            " the file r2's sealed record pins at 07a5a07aa8e94d98…"
        ),
    }
    block["packs"] = {
        "producer": MOVED["packs.producer"],
        "sha256": sha(REPO_ROOT / "scripts" / "build_pass1_window_r2_pack.py"),
        "reads": {
            "results/pass1_window_pack.json": sha(REPO_ROOT / "results" / "pass1_window_pack.json"),
            "results/pass1_window_v2.jsonl": sha(R1_OUT),
        },
        "borrowed": {
            "scripts/build_pass1_fewshot_packs.py": sha(
                REPO_ROOT / "scripts" / "build_pass1_fewshot_packs.py"
            ),
        },
        "rule": (
            "a THIN sibling of scripts/build_pass1_window_pack.py that subtracts and never renders."
            " The items of this pack ARE r1's items — same fields, same neighbours, same"
            " rendering_sha256 — because a re-render would move the shas the pod's handshake, rung 7"
            " and D2's union census all compare against. `ceiling_check` is the only borrowed"
            " function and it reads `rendered_chars`; the r1 pack's own length block is re-measured"
            " with it as a positive control before the 901's is published"
        ),
        "the_r1_producer_is_not_re_run": (
            "scripts/build_pass1_window_pack.py stays exactly where r1's sealed record pins it. It"
            " is not called, not imported and not edited: calling it would re-enumerate the"
            " population and re-render 1 032 requests, and the only thing that could produce is a"
            " disagreement with the record that already registered them"
        ),
    }
    return block


def supersedes() -> dict:
    """What r1 was, what it bought, and every number of its money block this record repeals."""
    r1 = json.loads(summary.read_text_or_refuse(R1_PREREG))
    run = json.loads(summary.read_text_or_refuse(R1_RUN))
    pod = run["pods"][0]
    return {
        "record": R1_PREREG_NAME,
        "sha256": sha(R1_PREREG),
        "report": "docs/reports/pass1-window.md",
        "run_record": "results/pass1_window_run.json",
        "closing_state": (
            "closed RED at rung 7, 131 of 1 032, killed by rung 4 on the rate; recovery refused on"
            " seconds"
        ),
        "what_it_bought": {
            "pod": pod["pod_id"],
            "billed_seconds": pod["billed_seconds"],
            "billed_usd": pod["billed_usd"],
            "answered": 131,
            "out_file": "results/pass1_window_v2.jsonl",
            "out_file_sha256": sha(R1_OUT),
            "transport_defects": 0,
            "rule": (
                "131 replies, 131 parsed, 0 sha mismatches, 0 refusals, 0 duplicates. The"
                " instrument was sound and the bar failed on the one number the money model could"
                " not deliver"
            ),
        },
        "its_numbers_this_record_REPEALS": {
            "hard_stop_seconds": r1["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"],
            "seconds_per_call": r1["money"]["arithmetic"]["seconds_per_call"]["v2"],
            "total_seconds": r1["money"]["arithmetic"]["total_seconds"],
            "widest_dead_pod_that_still_fits_seconds": r1["money"]["arithmetic"][
                "recovery_arithmetic"
            ]["widest_dead_pod_that_still_fits_seconds"],
            "cap_usd_all_in": r1["money"]["cap_usd_all_in"],
            "rule": (
                "these five are quoted HERE, by name, and appear as numbers nowhere else in this"
                " record's money block. A threshold copied for its algorithm brings its number with"
                " it, and that is how a repealed figure goes on gating a run nobody priced it for"
                " (Dv613). tests/test_pass1_window_r2_prereg.py sweeps the money block for them"
            ),
        },
        "what_is_UNCHANGED_from_it": [
            "prompt v2, its sha and the renderer",
            "the five neighbours and the self-exclusion rule",
            "the topic / entity context and its bought verdicts",
            "the shape of the completeness bar — answered, sha, refusals by cause",
            "the kill-clock's seven rungs, by name and by algorithm",
            "the fourteen-as-census-row rule and the multiplicity sentence",
            "the population: these 901 items ARE r1's items",
        ],
    }


def population(pack: dict) -> dict:
    """What this leg asks, and what the window it completes is — both, keyed on the pair."""
    r1 = json.loads(summary.read_text_or_refuse(R1_PREREG))
    block = pack["population"]
    return {
        "pack": PACK_NAME,
        "sha256": sha(PACK),
        "leg": pack["legs"][0]["name"],
        "out_file": pack["legs"][0]["out"],
        "payable_comments": block["payable_comments"],
        "threads": block["threads"],
        "cell": block["cell"],
        "ceiling_chars": pack["length"]["ceiling_chars"],
        "widest_request_chars": pack["length"]["widest_request_chars"],
        "membership": {
            name: pack["membership"][name]["n"]
            for name in ("gold_14", "probe_64", "labelled_650", "dev_200")
        },
        "self_exclusion": {
            "items_shown_a_neighbour_from_their_own_thread": len(
                pack["self_exclusion"]["items_shown_a_neighbour_from_their_own_thread"]
            ),
            "distinct_neighbours_used": pack["self_exclusion"]["distinct_neighbours_used"],
        },
        "rule": (
            "the r1 pack's leg MINUS the 131 ids of results/pass1_window_v2.jsonl, each verified"
            " against its pack item's rendering_sha256 before it was subtracted. Nothing was"
            " re-enumerated and nothing was re-rendered"
        ),
        "the_window_this_completes": {
            "payable_comments": block["payable_comments_in_the_window"],
            "answered_by_r1": block["answered_by_r1"],
            "threads_in_the_cell": block["threads_in_the_cell"],
            "threads_r1_finished": len(block["threads_r1_finished"]),
            "membership_of_the_whole_window": block["membership_of_the_whole_window"],
            "union_key": (
                "the PAIR (thread, msg_id). D2 censuses r1's out-file and this one together; seven"
                " msg_ids of the 650 labelled rows live in two threads each, so a union keyed on"
                " the msg_id would merge two channels' comments into one row (the ADDENDUM of"
                " docs/reports/pass1-window.md)"
            ),
        },
        "gold": {
            **r1["population"]["gold"],
            "owed_here": pack["membership"]["gold_14"]["n"],
            "answered_by_r1": 14 - pack["membership"]["gold_14"]["n"],
            "multiplicity_note": (
                "D2 reads these fourteen over the UNION and it is their FIFTH look: the base"
                " (pass1-probe-b, 9/14), arm A of the LoRA line (lora-b, 9/14), v2 registered for a"
                " shot it never fired, v2 inside r1's production pass (five reached, four agreeing)"
                " and now the rest of them. A census row, never a bar"
            ),
        },
        "the_volume_tail": {
            "path": "/workspace/run/pass1_window_v2.jsonl",
            "volume": "qw4nwleanc",
            "rows_the_mac_holds": 131,
            "rows_the_r1_pod_log_names": 132,
            "the_named_row": "@klopotenkofood:6035#21205",
            "rule": (
                "EVIDENCE, not input. It is scp'd to results/pass1_window_volume_tail.jsonl BEFORE"
                " the run directory is cleared, sha'd on both sides, and its rows beyond the Mac's"
                " 131 are COUNTED and PRICED («N rows bought twice, N × the measured s/call»). It"
                " is never merged: every one of its ids is inside the 901 and is bought again here,"
                " and two answers for one id is an ambiguity this registration does not buy"
                " ([[a_retry_inherits_the_last_attempts_output]])"
            ),
            "and_then_the_clocks_are_cleared": (
                "the dead pod's `launched_at` and `pod.log` are wiped by the staging step on THIS"
                " attempt's first pod — a stamp older than the pod is a refusal and a log's line"
                " count is a high-water mark the new pod never rises above (Dv621/632). The"
                " out-file itself is copied first, and only then"
            ),
        },
    }


def build() -> dict:
    r1 = r1prod.sealed(R1_PREREG, R1_PREREG_NAME)
    pack = json.loads(summary.read_text_or_refuse(PACK))
    calls = int(pack["population"]["payable_comments"])
    window_calls = int(pack["population"]["payable_comments_in_the_window"])

    charged = rate()
    tail = r1prod.deletion_tail(json.loads(summary.read_text_or_refuse(R1_FEWSHOT_RUN)))
    overhead = r1prod.r2_overhead_reading(json.loads(summary.read_text_or_refuse(R2_RUN)))
    sums = arithmetic(charged, calls, overhead, tail)
    bar = bars(calls, window_calls)
    checks = h6(sums, charged, calls, window_calls, bar)
    if checks["mismatches"]:
        raise SystemExit(
            "H6 does not re-derive: "
            + json.dumps(checks["mismatches"], ensure_ascii=False, indent=2)
            + "\nNo pod is created against a record whose own arithmetic disagrees with the"
            " contract. Stop and report."
        )

    return {
        "phase": "pass1-window-r2",
        "contract": "docs/PROMPT-pass1-window-r2.md",
        "authority": (
            "the operator's ruling of 2026-08-21 (evening) in the team-lead session, registered in"
            " docs/STATUS.md «Открытые решения» п. 1 (е): re-register the remainder as"
            " `pass1-window r2` with a cap of $2.00 (step ≤ $2.17); the alternatives — a pass-2"
            " smoke on the 24 covered threads first, and stopping the line — were rejected. The"
            " pass-2 smoke on the covered threads enters `pass2-signals` as a rung BEFORE its full"
            " run"
        ),
        "attempt": (
            "there is no ONE-ATTEMPT clause here and that is deliberate, exactly as in r1. This is"
            " a production population, and the exam rows inside it are answered BECAUSE they are in"
            " the population and not because anyone is taking a shot. The attempt `pass1-fewshot`"
            " left intact stays intact: it belongs to a bar on the fourteen, and no bar on the"
            " fourteen is being taken here"
        ),
        "supersedes": supersedes(),
        "what_this_run_is": pack["what_this_run_is"],
        "what_this_run_is_not": (
            "an evaluation. Nothing in it is a bar on v2's quality, and no reading it produces may"
            " be promoted to one — not the fourteen, not the 650, not the 450 and not the dev-200."
            " It is also NOT a re-run of r1: the 131 comments r1 bought are not re-asked and its"
            " out-file is not touched. And it is not a repair of the r1 pod's rate — the rate is"
            " re-CHARGED, not fixed; nobody has made a rented GPU faster"
        ),
        "population": population(pack),
        "instruments": instruments(r1),
        "money": {
            "cap_usd_all_in": CAP_USD,
            "cap_rule": (
                f"${CAP_USD:.2f} all-in, frozen at the FIRST `pod create`. The guard step"
                " `pass1-window-r2` is FRESH and opens with no pods of its own, so the step cap and"
                " the contract cap are the same number. r1's step ledger is a different step and"
                " stays OPEN for `money-anchors`; its pod's $0.173694 is added in `step_sum` as the"
                " window's total cost and is NOT charged against this cap. Raising the cap is the"
                " operator's word BEFORE any endpoint exists, never after a reading"
            ),
            "guard": (
                f"PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-window-r2"
                f" --step-cap {CAP_USD:.2f} — the anchor is committed BEFORE the pod exists, and"
                " the reading is what the rungs that name one act on"
            ),
            "reading": {
                "step": "pass1-window-r2",
                "anchor_file": "results/spend_pass1_window_r2.json",
                "rule": "money is read from the GUARD, never from a ledger and never from prose (Dv33)",
            },
            "meter": {
                "resource": (
                    "ONE rented pod, billed for every second it EXISTS — from `pod create` to"
                    " `pod delete`. `pod stop` does not stop the bill, so the run deletes and never"
                    " stops"
                ),
                "card_preferred": (
                    f"RTX 4090 at ≤ ${PRICE_CEILING}/h — the card probe-b, r2 and the r1 window pod"
                    " all ran on. A6000 48 GB in EU-RO-1 has been `none` on every look"
                ),
                "memory": (
                    "this line does NOT train, so lora-b's 48 GB constraint does not apply: three"
                    " pods have served this base on a 24 GB 4090"
                ),
                "datacenter": "EU-RO-1, pinned by network volume qw4nwleanc — the volume decides",
                "price_ceiling_usd_per_hour": PRICE_CEILING,
                "usd_per_second_at_the_ceiling": round(PRICE_CEILING / 3600.0, 9),
                "price_rule": (
                    "**READ ON THE DAY.** `costPerHr` in the create response is the meter of record"
                    " and every figure here is recomputed from it by rung 4 before the run is"
                    " allowed to continue"
                ),
                "and_the_rate_is_NOT_a_property_of_the_price": (
                    "the r1 pod cost $0.74/h and ran at 4.498 s/call; probe-b's pod cost the same"
                    " and ran its base leg at 5.162. The price ceiling bounds the dollars per"
                    " second and says nothing about the seconds per call — that is what this"
                    " record's rate block is for"
                ),
            },
            "arithmetic": sums,
            "recovery": {
                "rule": (
                    "ONE pod re-creation, and only after a deletion PROVEN by listing. Never two"
                    " billing endpoints. `--pre-create-check` computes both bounds, refuses the"
                    " create itself, and RECORDS its verdict"
                ),
                "arithmetic": sums["recovery_arithmetic"],
                "clear_the_mac_first": (
                    "the Mac's copies of a dead pod's run directory are cleared before the second"
                    " pod is created (Dv621): a resume reads whatever out-file is on disk, and a"
                    " previous attempt's rows would be counted as this one's"
                ),
                "there_is_no_generation_checkpoint_to_lose": (
                    "every reply is flushed to its out-file as it lands and the shipped resume"
                    " skips every unit already answered, so a re-creation re-asks only what has no"
                    " reply. A KILL mid-leg costs the boot, not the leg — WHERE THE CLAUSE IS"
                    " REACHABLE AT ALL, and the next field is where that is"
                ),
                "the_window_the_clause_is_reachable_in": (
                    "`--pre-create-check` prices the FULL worst case ahead"
                    f" ({sums['total_seconds']} s) and not the calls that actually remain, so a"
                    " re-creation is refused once the dead pod has billed more than"
                    f" {sums['recovery_arithmetic']['widest_dead_pod_that_still_fits_seconds']} s —"
                    " whatever the resume would have saved. A KILL at rung 2 or rung 3 is inside"
                    " that window ONLY while the create-elapsed at the kill is inside"
                    " recovery_arithmetic.which_KILLS_stay_recoverable.the_number_that_decides_it —"
                    " rung 2's ceiling always is and rung 3's create-anchored backstop never is. A"
                    " KILL deep inside the generation is NOT, and the clause is then"
                    " a STOP and not a recovery. THIS IS EXACTLY WHAT CLOSED r1: its pod had billed"
                    " 845 s against an allowance this record repeals and quotes by name in"
                    " supersedes.its_numbers_this_record_REPEALS, so the refusal came on seconds"
                    " while the money still fitted. The window is"
                    f" {sums['recovery_arithmetic']['widest_dead_pod_that_still_fits_seconds']} s"
                    " here and the shape is the same"
                    " ([[the_contracts_scope_is_narrower_than_the_rulings]])"
                ),
                "two_meters_and_the_stricter_binds": (
                    "`--pre-create-check` computes from the GATE's own ledger — the closed pods'"
                    " billed seconds at their own price, timely and exact to the pod clock."
                    " `scripts/runpod_guard.py` reads the BALANCE delta and the billing walk, which"
                    " is what the cap is defined against and which LAGS (Dv504; on r1 the walk"
                    " reported `pods $0.0000` for a pod that had demonstrably run 845 s). They are"
                    " two meters and neither is the other. The runbook takes BOTH readings before a"
                    " re-creation and the stricter binds"
                ),
                "what_the_pod_keeps_and_what_it_clears": (
                    "on a re-creation the volume still holds /workspace/run/pass1_window_r2_v2.jsonl"
                    " and it MUST be kept — it is the whole of «costs the boot, not the leg». What"
                    " must go is every clock the dead pod owns: `launched_at`, which the gate"
                    " refuses as older than the new pod, and `pod.log`, whose line count would be a"
                    " high-water mark the new pod never rises above. The r1 file"
                    " /workspace/run/pass1_window_v2.jsonl is copied back and then removed from the"
                    " run directory by the FIRST pod's staging step, so it can never be mistaken"
                    " for this leg's output"
                ),
            },
            "step_sum": {
                "step": "pass1-window-r2",
                "step_budget_usd": CAP_USD,
                "prior_pods_usd": 0.0,
                "the_windows_total_cost_usd": round(0.173694 + CAP_USD, 6),
                "rule": (
                    "this step is FRESH and opens with no pods, so `prior_pods_usd` is 0 and the"
                    " step cap is the contract cap. What the WINDOW has cost is a different"
                    " question and its answer is $0.173694 (r1's pod, on the gate's clock) + this"
                    " cap = $2.1737, which is the ≤ $2.17 the operator's ruling names. r1's step"
                    " ledger stays OPEN for `money-anchors` and this record does not close it"
                ),
            },
        },
        "bars": bar,
        "kill_clock": kill_clock(sums, bar),
        "h6": checks,
        "do_not": [
            "no change to prompt v2, the neighbour rule, the labels, the gold or any sealed record",
            "no change to results/pass1_window_pack.json, results/pass1_window_v2.jsonl or"
            " results/prereg_pass1_window.json — r1's pack, out-file and record are sealed inputs",
            "no merge of the volume's surviving out-file — it is copied, counted and priced",
            "no second leg, no dev gate, no bar on the fourteen",
            "no re-purchase of reader context — the v5b / v4 / topup verdicts are read, never bought",
            "no generation before H6 re-derives and the D0′ commits are in",
            "never leave --watch while a pod is live",
            "never two billing endpoints CONCURRENTLY; one re-creation after a PROVEN deletion",
            "no third pod",
        ],
        "frozen_when_the_pod_exists": [
            "docs/PROMPT-pass1-window-r2.md and every other docs/PROMPT-*.md — team-lead files",
            "src/market_pulse/prompts.py — v2, v1, the renderer and the parser",
            "src/market_pulse/scorer.py — the single judge, pinned by sealed records",
            "results/pass1_window_pack.json and results/pass1_window_v2.jsonl — r1's pack and its"
            " replies, the two inputs this pack was subtracted from",
            "results/prereg_pass1_window.json — r1's record, sealed and superseded",
            f"{PACK_NAME} — this pack, its items and their per-item shas",
            f"{OUT_NAME} — this record",
            "results/labels_pass1_r1.jsonl and _r2.jsonl — the team lead's labels",
            "results/reader_gold_w1_r2.json — the gold",
            "results/pass1_probe_b_rows.jsonl, results/pass1_dev_base.jsonl,"
            " results/pass1_dev_v2.jsonl — the three files the RATE is derived from",
            "results/prereg_pass1_fewshot.json and _r2.json — sealed, superseded, never re-opened",
            "scripts/gate_pass1_fewshot.py and scripts/gate_pass1_window.py — instruments this"
            " gate IMPORTS and EXECUTES, never edits",
            "scripts/pass1_fewshot_pod_runner.py — the transport that runs ON the pod",
            "results/spend_pass1_window_r2.json — the step anchor. Regenerating it re-zeroes the"
            " step at that day's balance, which is the one way this cap stops being a cap",
            "scripts/gate_pass1_window_r2.py and scripts/build_pass1_window_r2_pack.py — pinned by"
            " this record; an edit after the create moves a pin the gate itself is read through",
        ],
        "return_to_the_operator": (
            "THE FOURTEEN ARE A CENSUS ROW AND THIS IS THEIR FIFTH LOOK. The base took 9/14"
            " (pass1-probe-b), arm A of the LoRA line took 9/14 (lora-b), v2 was registered for a"
            " shot it never fired, r1's production pass reached five of them and agreed on four,"
            " and this run answers the remaining nine. Their agreement over the union is REPORTED"
            " with that multiplicity beside it and it may not be promoted to «v2 takes N of 14» by"
            " this report, by the acceptance or by the next registration. A bar on the fourteen"
            " needs a NEW registration with its own attempt, its own threshold and the operator's"
            " word. The same holds for the 650, the 450 and the dev-200: bigger samples, still"
            " readings. AND THE RATE IS STILL NOT KNOWN — this record charges the TOP of a measured"
            " spread and the spread has two readings in it. If this pod comes in under the charge,"
            " that is one more reading of the class and not a rate the programme owns"
        ),
        "run_record": RUN_RECORD,
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": sha(Path(__file__)),
            "copied_from": {
                R1_PREREG_NAME: sha(R1_PREREG),
                "scripts/write_pass1_window_prereg.py": sha(
                    REPO_ROOT / "scripts" / "write_pass1_window_prereg.py"
                ),
            },
            "copied_rule": (
                "r1's producer is IMPORTED for the four helpers that are pure in their arguments —"
                " `sealed`, `dig`, `live_pins`, `deletion_tail`, `r2_overhead_reading` — and"
                " nothing else. Every number of the money block is computed here, because that is"
                " the half that moved"
            ),
        },
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    record = build()
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    sums = record["money"]["arithmetic"]
    charged = sums["seconds_per_call"]
    cumulative = sums["cumulative"]
    recovery = sums["recovery_arithmetic"]
    gate = cumulative["projection_gate"]["single_call_sensitivity"]
    print(f"wrote {summary.rel(args.out)}  sha256 {sha(args.out)[:16]}…")
    print(
        f"  rate: probe-b {charged['the_pod_class']['slowest_base_pod_seconds_per_call']:.6f}"
        f" × uplift {charged['the_uplift']['v2_over_base']:.6f} = {charged['derived']} →"
        f" charged {charged['charged']} s/call"
        f"  (the pod class spans {charged['the_pod_class']['spread']:.4f}×)"
    )
    print(
        f"  generation: {sums['calls']['v2']} × {charged['charged']} ="
        f" {sums['generation_seconds']} s"
    )
    print(
        f"  worst case: {sums['total_seconds']} s = {sums['hours']:.6f} h ="
        f" ${sums['worst_case_usd_at_the_price_ceiling']:.6f} at ${PRICE_CEILING}/h"
        f"  (${sums['worst_case_usd_at_the_lora_b_price']:.6f} at ${LORA_B_PRICE})"
    )
    print(
        f"  cap ${CAP_USD:.2f} · hard stop {cumulative['hard_stop_seconds']:.0f} s ="
        f" ${cumulative['hard_stop_usd_at_the_price_ceiling']:.4f} · session ceiling"
        f" {cumulative['session_ceiling_seconds']:.0f} s"
    )
    print(
        f"  recovery: one dead pod at rung 2 + worst ="
        f" {recovery['then_the_full_worst_case_seconds']} s ="
        f" ${recovery['then_the_full_worst_case_usd']:.4f} · widest dead pod"
        f" {recovery['widest_dead_pod_that_still_fits_seconds']} s"
    )
    print(
        "  rung 4 knife edge:"
        f" {gate['at_the_CHARGED_pre_generation']['sustained_rate_the_hard_stop_can_pay_for']}"
        " s/call at the CHARGED pre-generation ·"
        f" {gate['at_the_MEASURED_pre_generation']['sustained_rate_the_hard_stop_can_pay_for']}"
        f" at the measured — slowest call ever measured {SLOWEST_CALL_EVER_MEASURED}"
    )
    print(
        f"  bar: answered {record['bars']['completeness']['answered_minimum']} /"
        f" {record['bars']['completeness']['owed']} · sha 0 · refusals ≤"
        f" {record['bars']['completeness']['parse_refusals_maximum']}"
        f"   (the window's own completeness: {record['bars']['the_windows_completeness']['owed']})"
    )
    print(f"  H6: {len(record['h6']['rows'])} rows, {len(record['h6']['mismatches'])} mismatches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
