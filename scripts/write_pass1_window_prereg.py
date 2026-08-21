#!/usr/bin/env python3
"""`results/prereg_pass1_window.json` — the registration of pass 1 over the whole window-1 population.

**What this run is.** A PRODUCTION pass, not an evaluation: 1 032 payable comments of 129 threads,
one leg, prompt v2, and an out-file that is the INPUT of `pass2-signals`. The bar is therefore
transport and completeness and nothing else. Nothing measured here is a bar on v2's quality, and the
record says so in `what_this_run_is_not` and again in `return_to_the_operator`.

**The instruments are r2's, COPIED and then resolved against the live files.** The copy is a
REFUSAL, not a convenience: every pin inside the copied block is compared to the file it names right
now, and a single divergence stops this producer before a byte is written — a block copied out of r2
that no longer describes this checkout would register yesterday's world under today's name
([[a_frozen_record_is_an_input_to_shipped_code]]). Exactly two pins are expected to move and are
handled by name: the gate, which is this contract's own sibling, and the pack producer.

**The kill clock is r2's, rung by rung, by NAME.** What moved is the cumulative hard stop (6 100 →
6 500 s) and the cap ($1.38 → $1.50), because the population is 1 032 calls instead of 464 — and
a block copied for its algorithm carries its NUMBERS, which is the class r2 shipped as Dv613
([[an_audit_of_pins_is_not_an_audit_of_thresholds]]). Every threshold below is either re-derived
here or asserted by an H6 row, and the gate reads all of them out of this record.

**H6 is the step-1 refusal gate, and it audits INPUTS.** The arithmetic of a money block is
self-consistent by construction — it is the same multiplication done twice. What H6 can actually
catch is an input: the 1 032 (called, never typed), the 2.726 s/call (re-derived from the 200 rows
of `results/pass1_dev_v2.jsonl`, with the pod that measured it NAMED), the allowances carried from
r2, and the reason rows — why the overhead did not move when the rows it covers went 400 measured
→ 1 032, and why a 1 % refusal allowance is compatible with a 1 032 / 1 032 answered bar.

    PYTHONPATH=src python3.11 scripts/write_pass1_window_prereg.py
    PYTHONPATH=src python3.11 scripts/write_pass1_window_prereg.py --outdir /tmp/again   # the pair
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pass1_window_pack as window  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

OUT_NAME = "results/prereg_pass1_window.json"
R2_NAME = "results/prereg_pass1_fewshot_r2.json"
PACK_NAME = window.OUT_NAME
RUN_RECORD = "results/pass1_window_run.json"

R2 = REPO_ROOT / R2_NAME
PACK = REPO_ROOT / PACK_NAME
GATE = REPO_ROOT / "scripts" / "gate_pass1_window.py"
DEV_V2_ROWS = REPO_ROOT / "results" / "pass1_dev_v2.jsonl"
DEV_PACK = REPO_ROOT / "results" / "pass1_dev_pack.json"
R2_RUN = REPO_ROOT / "results" / "pass1_fewshot_r2_run.json"
R1_RUN_NAME = "results/pass1_fewshot_run.json"
R1_RUN = REPO_ROOT / R1_RUN_NAME

# --- what THIS contract sets. Everything else is r2's, copied ---------------------------------------

CAP_USD = 1.50
PRICE_CEILING = 0.80
HARD_STOP_SECONDS = 6500.0
RATE_MARGIN = 1.25
CHARGED_SECONDS_PER_CALL = 3.4075

# carried from r2 unchanged — restated because the arithmetic below is re-derived and never copied
SSH_DEADMAN_SECONDS = 500.0
STAGE_LAUNCH_SECONDS = 150.0
BOOT_SECONDS = 450.0
OVERHEAD_SECONDS = 1300.0
IDLE_DEADLINE_SECONDS = 600.0
PROJECTION_EVERY_CALLS = 20
BACKSTOP_TOLERANCE_SECONDS = 60.0
LORA_B_PRICE = 0.53

REFUSALS_MAXIMUM = 10
REFUSALS_FRACTION = 0.01

WORST_MEASURED_BOOT = 353.0
"""lora-b, the same volume. Rung 3's ceiling is ≥ this and that is r2's derivation, unmoved."""

WIDEST_SSH_READING = 262.5
"""The wider of 2026-08-20's two readings, and a LOWER bound — ssh was never observed ready."""

R2_SAMPLE = "200 dev rows, pod 8tpx8lf05n6skc"
"""A rate is a property of the sample it was measured on, so the sample is named beside the number
(the 5c2 retro's rule). `results/pass1_dev_v2.jsonl` is that sample and the mean is re-derived from
it below, never typed."""

R2_PRE_GENERATION_MEASURED = 254.6
"""r2's create-elapsed at its FIRST reply — the whole of ssh + staging + launch + load, measured on
this stack on 2026-08-21 (its rung-3 gate: 145.6 s of launch-elapsed at 254.6 s of create-elapsed).
Rung 4's sensitivity curve is computed against a pod that boots like that one."""

R2_ROWS_COPIED_BACK = 464
R2_WATCH_GO_ELAPSED = 1276.1
"""r2's own two numbers for the overhead reason row: the rows its 1 300 s covered, and the
create-elapsed at which every one of them was answered. The span from there to its deletion is the
only MEASUREMENT this stack has of «what the overhead line actually buys»."""


def sha(path: Path) -> str:
    return summary.sha256_of(path)


def sealed(path: Path, name: str) -> dict:
    """A record read from a file git says is committed and unmodified. Nothing else may be copied."""
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path)], cwd=REPO_ROOT, capture_output=True
    )
    if tracked.returncode != 0:
        raise SystemExit(f"{name} is not tracked by git — there is no sealed record to copy from.")
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", str(path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if dirty.stdout.strip():
        raise SystemExit(
            f"{name} differs from HEAD: {dirty.stdout.strip()}. A sealed record is never edited and"
            " this producer copies it — stop and report."
        )
    return json.loads(summary.read_text_or_refuse(path))


def dig(record: dict, path: str):
    for key in path.split("."):
        record = record[key]
    return record


MOVED = {
    "gate.script": "scripts/gate_pass1_window.py",
    "packs.producer": "scripts/build_pass1_window_pack.py",
}
"""The two instruments this contract genuinely replaces. Everything else in r2's block is copied and
then held to the live file."""

DROPPED = {
    "scorer_pass1_fewshot": (
        "r2's D2 judge scored the dev gate and the fourteen against a bar. This contract has neither"
        " — its D2 readings are report-only and go through src/market_pulse/scorer.py, which is"
        " pinned above as `scorer`. A pin naming a script this run never calls is a pin nobody"
        " checks"
    )
}


def live_pins() -> dict[str, str]:
    """Every pin a copied block carries, resolved against the file it names, RIGHT NOW."""
    return {
        "parser.sha256": sha(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
        "scorer.sha256": sha(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
        "transport.sha256": sha(REPO_ROOT / "scripts" / "pass1_fewshot_pod_runner.py"),
    }


def instruments(r2: dict) -> dict:
    """r2's instruments, copied — then every pin resolved, and the two that MOVE re-pinned by name."""
    block = json.loads(json.dumps(r2["instruments"]))
    for name, why in DROPPED.items():
        block.pop(name)
        block.setdefault("dropped_from_r2", {})[name] = why

    drifted = {
        path: {"copied_from_r2": dig(block, path), "live": value}
        for path, value in live_pins().items()
        if dig(block, path) != value
    }
    if drifted:
        raise SystemExit(
            "a pin copied out of r2 no longer describes this checkout: "
            + json.dumps(drifted, ensure_ascii=False, indent=2)
            + "\nThis contract renders window-1 through the SAME functions r2 rendered dev-200"
            " through. A pin that has moved is a different instrument and needs the operator."
        )

    block["gate"] = {
        "script": MOVED["gate.script"],
        "sha256": sha(GATE),
        "moved_since_r2": True,
        "rule": (
            "a SIBLING of scripts/gate_pass1_fewshot.py. It IMPORTS every rung computation that is"
            " pure — rungs 1, 2, 3, 4 and their clock — and re-declares the ones bound to r2's own"
            " module state (the record it writes, the launch stamp it reads, the leg it takes the"
            " first reply from) plus rung 7, which is a completeness bar here and a dev gate there."
            " r2's gate is pinned by its own sealed record and is NEVER edited"
        ),
    }
    block["gate_imported_from"] = {
        "script": "scripts/gate_pass1_fewshot.py",
        "sha256": sha(REPO_ROOT / "scripts" / "gate_pass1_fewshot.py"),
        "also_imported": {
            "scripts/window_summary_5c2.py": sha(REPO_ROOT / "scripts" / "window_summary_5c2.py"),
            "why": (
                "the gate hashes the pack through window_summary_5c2.sha256_of, so that file is an"
                " instrument of the pack guard. An IMPORTED instrument is an instrument — the same"
                " rule that put r2's gate in this block"
            ),
        },
        "rule": (
            "an IMPORTED instrument is an instrument. This is the file r2's sealed record pins at"
            " 07a5a07aa8e94d98…, unchanged; the sibling above calls into it and does not edit it"
        ),
    }
    block["packs"] = {
        "producer": MOVED["packs.producer"],
        "sha256": sha(REPO_ROOT / "scripts" / "build_pass1_window_pack.py"),
        "borrowed": {
            one: sha(REPO_ROOT / one)
            for one in (
                "scripts/build_pass1_fewshot_packs.py",
                "scripts/build_pass1_sft.py",
                "scripts/gate_census_w1_reader.py",
            )
        },
        "rule": (
            "the window pack's producer. It IMPORTS build_pass1_fewshot_packs.neighbours /"
            " ::rendered_item / ::context and build_pass1_sft.request — the dev leg's own rendering"
            " path — so the window is asked exactly as dev-200 was asked. The three borrowed shas"
            " are pinned beside it because a rendering built through another file's function moves"
            " when that file moves"
        ),
    }
    block["gold"] = {
        "record": "results/reader_gold_w1_r2.json",
        "sha256": sha(REPO_ROOT / "results" / "reader_gold_w1_r2.json"),
        "comparison": "market_pulse.scorer.reader_comment_agreement",
        "collapse": "scripts/score_reader_probe_b.py::collapse",
        "collapse_sha256": sha(REPO_ROOT / "scripts" / "score_reader_probe_b.py"),
        "why_not_leg_table": (
            "the fourteen are GOLD and not labels. gate_pass1_fewshot.py::leg_table compares against"
            " results/labels_pass1_r*.jsonl and NOT ONE of the fourteen pairs is in that map — 0 of"
            " 14, checked. The reading over the 650 labelled rows and the 450 outside dev-200 is"
            " leg_table's; the reading over the fourteen cannot be"
        ),
        "why_not_bar_p1": (
            "scripts/score_pass1_probe.py::bar_p1 is the right COMPARISON and the wrong INSTRUMENT."
            " It returns `passed`, `minimum_agreed` and a `losses.budget` — it is a BAR, and this"
            " contract may not take a bar on the fourteen at all. D2 calls"
            " scorer.reader_comment_agreement with probe_b.collapse on both sides, which is exactly"
            " what bar_p1 computes BEFORE its threshold arm, and stops there. A `passed` field on"
            " this row would be the promotion the ADR forbids in the very shape it forbids it"
            " ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]])"
        ),
        "rule": (
            "a reading D2 owes with no producer named at D0 is a producer invented after the money"
            " ([[a_registered_bar_may_have_no_producer]]). This is the producer, and it yields a"
            " CENSUS ROW with the multiplicity of return_to_the_operator beside it"
        ),
    }
    block["population_producer"] = {
        "script": "scripts/gate_census_w1_reader.py",
        "sha256": sha(REPO_ROOT / "scripts" / "gate_census_w1_reader.py"),
        "rule": "population() is CALLED at build time; the counts below are what it returned",
    }
    return block


def measured_v2_rate() -> dict:
    """r2's v2 rate, re-summed from the 200 rows that produced it — never typed.

    The contract prints 2.726 s/call. That is a ROUNDING of what the file holds, and the rounding
    goes the safe way: the registered charge is 1.25 × 2.726 and not 1.25 × the unrounded mean, so
    every generation figure below is bought a hair more pessimistically than the measurement
    demands. H6 asserts the direction rather than the equality.
    """
    rows = [
        json.loads(line)
        for line in summary.read_text_or_refuse(DEV_V2_ROWS).splitlines()
        if line.strip()
    ]
    seconds = [float(one["seconds"]) for one in rows]
    if len(seconds) != 200:
        raise SystemExit(
            f"{summary.rel(DEV_V2_ROWS)} holds {len(seconds)} rows and the sample this rate is"
            " named for is 200 — stop and report."
        )
    return {
        "mean": sum(seconds) / len(seconds),
        "rows": len(seconds),
        "slowest_call": max(seconds),
        "fastest_call": min(seconds),
        "sample": R2_SAMPLE,
        "file": summary.rel(DEV_V2_ROWS),
        "sha256": sha(DEV_V2_ROWS),
    }


def deletion_tail(run: dict) -> dict:
    """How long a pod KEPT BILLING after rung 2 fired — read off r1's own gate record.

    Rung 2's ceiling is 500 s of create-elapsed, and the meter does not stop when the rung fires: it
    stops at `pod delete`. r1 killed two pods on this rung and the two tails are 78.5 s and 0.1 s.
    The recovery clause is priced with the WORSE one, because a clause that is reachable only at the
    faster of two observed deletions is a clause the stack has not shown it can meet
    ([[a_ceiling_derived_from_one_span_measured_over_another]]).
    """
    tails = {}
    for pod in run["pods"]:
        killed = [
            one
            for one in run["gates"]
            if one.get("kind") == "gate0"
            and one.get("verdict") == "KILL"
            and one.get("pod_id") == pod["pod_id"]
        ]
        for gate in killed:
            tails[pod["pod_id"]] = round(
                float(pod["billed_seconds"]) - float(gate["elapsed_on_this_pod_seconds"]), 1
            )
    if not tails:
        raise SystemExit(
            f"{R1_RUN_NAME} carries no rung-2 KILL, and the deletion tail is derived from one."
            " Stop and report."
        )
    return {
        "measured_seconds": tails,
        "charged_seconds": max(tails.values()),
        "source": R1_RUN_NAME,
        "rule": (
            "the span between rung 2 firing and `pod delete` stopping the meter, per pod of r1."
            " The WORSE of the two is charged"
        ),
    }


def r2_overhead_reading(run: dict) -> dict:
    """What r2's 1 300 s of overhead actually bought, measured — the reason row for keeping it.

    The overhead line covers the copy-back, the gate on the Mac and the deletion. On r2 every one of
    those happened between the watch's GO and the pod's deletion, and that span is on the clock:
    `billed_seconds` less the create-elapsed at which the last row landed.
    """
    pod = run["pods"][-1]
    watch = [
        one for one in run["gates"] if one.get("kind") == "watch" and one.get("verdict") == "GO"
    ]
    if len(watch) != 1:
        raise SystemExit(
            f"{summary.rel(R2_RUN)} carries {len(watch)} watch GOs, not the one r2 closed on."
            " The overhead reason row is derived from it — stop and report."
        )
    at_go = float(watch[0]["elapsed_on_this_pod_seconds"])
    billed = float(pod["billed_seconds"])
    return {
        "pod": pod["pod_id"],
        "rows_answered": int(watch[0]["answered"]),
        "rows_r2_registered": R2_ROWS_COPIED_BACK,
        "why_the_two_differ": (
            f"r2 budgeted the copy-back of {R2_ROWS_COPIED_BACK} rows — 400 dev and the shot's 64 —"
            " and its shot never fired, so what its overhead line actually carried was the 400"
            " answered. The scaling below divides by what was MEASURED, which is the smaller"
            " denominator and the more expensive per row"
            " ([[a_count_in_prose_is_not_the_enumeration]])"
        ),
        "create_elapsed_at_the_watch_GO_seconds": at_go,
        "what_that_stamp_is": (
            "the create-elapsed of the poll on which --watch SAW every row answered, not the instant"
            " the last row landed. The loop polls at 20 s, so the true last row is somewhere in"
            " (at_go − 20, at_go] and this reading is the LATER end — which makes the span below a"
            " lower bound on the overhead measured, and therefore the conservative direction"
            " ([[a_paced_log_is_an_interleavable_clock]])"
        ),
        "billed_seconds": billed,
        "measured_after_the_last_row_seconds": round(billed - at_go, 1),
    }


def request_width() -> dict:
    """What the ×1.25 margin is BOUGHT against, measured on the two packs rather than asserted.

    The contract names the margin «for the window's larger entity blocks». The entity blocks ARE
    larger — 0.96 entities a request on dev-200 against 1.80 here — and the request they sit in is
    barely wider, because a v2 request is dominated by the five neighbour examples and the topic.
    A reason nothing re-derives is how a bound that double-counted the ssh wait shipped in r1, so
    the reason is a measurement here and H6 checks the DIRECTION: the margin must exceed the growth
    it is bought against ([[a_borrowed_rule_carries_an_unstated_population]]).
    """
    dev = json.loads(summary.read_text_or_refuse(DEV_PACK))
    sample = next(leg for leg in dev["legs"] if leg["name"] == "v2")["items"]
    window = json.loads(summary.read_text_or_refuse(PACK))["legs"][0]["items"]

    def mean(items, key):
        return sum(key(one) for one in items) / len(items)

    chars = mean(window, lambda one: one["rendered_chars"]) / mean(
        sample, lambda one: one["rendered_chars"]
    )
    return {
        "sample": summary.rel(DEV_PACK) + " leg v2 — the 200 rows the rate was measured on",
        "population": PACK_NAME,
        "mean_rendered_chars_sample": round(mean(sample, lambda one: one["rendered_chars"]), 1),
        "mean_rendered_chars_population": round(mean(window, lambda one: one["rendered_chars"]), 1),
        "ratio": round(chars, 6),
        "mean_entities_sample": round(mean(sample, lambda one: len(one["entities"])), 4),
        "mean_entities_population": round(mean(window, lambda one: len(one["entities"])), 4),
        "widest_sample": max(one["rendered_chars"] for one in sample),
        "widest_population": max(one["rendered_chars"] for one in window),
        "dev_200_rows_rendered_identically_in_both_packs": sum(
            1
            for one in window
            if one["rendering_sha256"]
            in {two["rendering_sha256"] for two in sample if two["id"] == one["id"]}
        ),
        "rule": (
            "the margin's own reason, measured. The entity blocks nearly DOUBLE (0.96 → 1.80 a"
            " request) and the request they sit in grows by ~1 %, because a v2 request is mostly"
            " the five neighbour examples and the topic. The margin is therefore bought against a"
            " growth an order of magnitude smaller than itself — which is the direction that makes"
            " it safe, and is now a checked row rather than a sentence"
        ),
    }


def arithmetic(rate: dict, calls: int, overhead: dict, tail: dict) -> dict:
    """Every money figure of this contract, computed here and re-derived by H6 from the same terms."""
    generation = calls * CHARGED_SECONDS_PER_CALL
    pre_generation = SSH_DEADMAN_SECONDS + STAGE_LAUNCH_SECONDS + BOOT_SECONDS
    total = pre_generation + generation + OVERHEAD_SECONDS
    hours = total / 3600
    dead_pod_seconds = SSH_DEADMAN_SECONDS + float(tail["charged_seconds"])
    dead_pod = SSH_DEADMAN_SECONDS * PRICE_CEILING / 3600
    dead_pod_with_tail = dead_pod_seconds * PRICE_CEILING / 3600
    worst = hours * PRICE_CEILING
    after_last_row = overhead["measured_after_the_last_row_seconds"]
    scaled = after_last_row * calls / overhead["rows_answered"]
    return {
        "calls": {"v2": calls},
        "seconds_per_call": {
            "v2": CHARGED_SECONDS_PER_CALL,
            "measured_mean": round(rate["mean"], 6),
            "margin": RATE_MARGIN,
            "sample": rate["sample"],
            "sample_file": rate["file"],
            "sample_sha256": rate["sha256"],
            "slowest_call_in_the_sample": rate["slowest_call"],
            "rule": (
                f"the MEASURED v2 figure {round(rate['mean'], 3)} s/call over {rate['rows']} rows"
                f" ({rate['sample']}), × {RATE_MARGIN} — a named margin for the window's larger"
                " entity blocks, not the ×1.5 BOUND r2 charged before v2 had ever been measured."
                " r2's own reading was that v2's prefill costs +18.9 % over the base and not the"
                " +50 % the bound assumed, so the margin is bought against the population's spread"
                " and not against the prompt"
            ),
            "why_a_mean_and_not_the_slowest_call": (
                f"the budget is a TOTAL over {calls} calls, so the mean is the term that belongs in"
                f" it; the slowest single call in the sample was {rate['slowest_call']} s. Rung 4"
                " re-prices the remainder on every poll at the LARGER of the measured mean and the"
                " last call, so a pod that is actually slower than this line is killed by the"
                " projection and not discovered in the bill"
            ),
        },
        "request_width": request_width(),
        "generation_seconds": round(generation, 3),
        "ssh_seconds_charged": SSH_DEADMAN_SECONDS,
        "ssh_rule": (
            "rung 2's own ceiling, charged as a line of the budget — r2's spread, unmoved. probe-b"
            " saw ssh at 14.5 s on this card in this datacenter on 2026-08-18; on 2026-08-20 two"
            " pods were still `pod not ready` at 262.5 s and 231.9 s, both LOWER bounds; r2's own"
            " pod answered at ≤ 50 s on 2026-08-21, an UPPER bound inside the spread. Three"
            " readings, no measurement of the worst case — the ceiling stays where r2 put it"
        ),
        "ssh_readings": {
            "pass1-probe-b, 2026-08-18": 14.5,
            "7spsy61lpjumrz, 2026-08-20 (a lower bound)": 262.5,
            "juupgp6y77jvuz, 2026-08-20 (a lower bound)": 231.9,
            "8tpx8lf05n6skc, 2026-08-21 (an upper bound)": 50.0,
        },
        "stage_launch_seconds_charged": STAGE_LAUNCH_SECONDS,
        "stage_launch_rule": (
            "scp of the bundle and the runners, the clone, the volume check and the detached"
            " launch — r2's line, unmoved. This contract's pack is larger than r2's two"
            f" ({PACK_NAME} against results/pass1_dev_pack.json), and the scp of one file is not"
            " what 150 s is spent on: probe-b bounds ssh + staging + launch TOGETHER at ≤ 89.5 s"
        ),
        "boot_seconds_charged": BOOT_SECONDS,
        "boot_rule": (
            f"≥ the worst boot this stack has measured ({WORST_MEASURED_BOOT} s, lora-b) — r2's"
            " derivation, unmoved, and anchored on the runner's own `launched_at`. r2 added a new"
            " FLOOR on 2026-08-21 (142.709 s) and not a new ceiling: this stack's boot is not a"
            " constant and the ceiling is charged at the maximum"
        ),
        "boots_measured": {
            "lora-b, A6000 + the same volume": [267.0, 293.0, 353.0],
            "pass1-probe-b, the 4090 this contract prefers": [237.155],
            "reader-v5b / pass1-probe stack, inference": [146.8, 192.1, 237.155],
            "pass1-fewshot r2, the 4090 and the same volume": [142.709],
        },
        "pre_generation_seconds": pre_generation,
        "pre_generation_rule": (
            f"ssh {SSH_DEADMAN_SECONDS:.0f} + stage/launch {STAGE_LAUNCH_SECONDS:.0f} + load"
            f" {BOOT_SECONDS:.0f} = {pre_generation:.0f} s, and it is ALSO rung 3's create-anchored"
            " backstop. The three spans are priced separately, as r2 priced them"
        ),
        "overhead_seconds": OVERHEAD_SECONDS,
        "overhead_rule": (
            f"{OVERHEAD_SECONDS:.0f} s — the copy-back of ≤ {calls} rows on every poll, the"
            " completeness gate on the Mac, and the deletion with its three listings. ssh and"
            " staging have their own lines above, so nothing here is counted twice"
        ),
        "overhead_measured_on_r2": {
            **overhead,
            "scaled_to_this_population_seconds": round(scaled, 1),
            "headroom_multiple": round(OVERHEAD_SECONDS / scaled, 2),
            "rule": (
                "the number this line did NOT move on when the rows it covers went"
                f" {overhead['rows_answered']} measured → {calls}, and the reason it did not have"
                " to."
                " r2's pod was deleted"
                f" {overhead['measured_after_the_last_row_seconds']} s after its last row landed,"
                " and that span carried the whole of what this line buys — the final copy, the gate"
                " on the Mac and the delete. Scaled by rows it is"
                f" {round(scaled, 1)} s against {OVERHEAD_SECONDS:.0f} charged, a"
                f" {round(OVERHEAD_SECONDS / scaled, 2)}× headroom, and the scaling is generous:"
                " r2's gate ran the SCORER over its 400 rows and this contract's rung 7 only parses"
                " them. The per-poll copies are not in this span at all — they happen while the pod"
                " is generating and cost it nothing"
            ),
        },
        "total_seconds": round(total, 3),
        "hours": round(hours, 6),
        "worst_case_usd_at_the_price_ceiling": round(worst, 6),
        "worst_case_usd_at_the_lora_b_price": round(hours * LORA_B_PRICE, 6),
        "rows_copied_back": calls,
        "cumulative": {
            "hard_stop_seconds": HARD_STOP_SECONDS,
            "hard_stop_hours": round(HARD_STOP_SECONDS / 3600, 4),
            "hard_stop_usd_at_the_price_ceiling": round(
                HARD_STOP_SECONDS * PRICE_CEILING / 3600, 4
            ),
            "hard_stop_rule": (
                f"cumulative billed ≤ {HARD_STOP_SECONDS:.0f} s ="
                f" ${HARD_STOP_SECONDS * PRICE_CEILING / 3600:.4f} at the ${PRICE_CEILING}/h"
                f" ceiling. It sits UNDER the ${CAP_USD:.2f} cap it defends and it is the PLATFORM"
                " that enforces it, so it protects even a hung call no gate can see. r2's 6 100 s"
                " does not carry over: this population is 1 032 calls and not 464, and a stop"
                " copied for its algorithm would have brought its number with it"
            ),
            "session_ceiling_hours": round(CAP_USD / PRICE_CEILING, 4),
            "session_ceiling_seconds": round(CAP_USD / PRICE_CEILING * 3600, 1),
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
            "projection_gate": {
                "every": f"{PROJECTION_EVERY_CALLS} calls",
                "overhead_seconds": OVERHEAD_SECONDS,
                "overhead_rule": (
                    "the SAME 1 300 s the money block charges, and it has to be: rung 4 prices the"
                    " attempt with it on every poll, so a second copy here is a second budget. H6"
                    " asserts the two are one number"
                ),
                "formula": (
                    "billed_by_closed_pods + elapsed_on_this_pod + the leg's remaining calls ×"
                    " its s/call + overhead_seconds. The leg is priced at its MEASURED rate — the"
                    " larger of its mean and its last call — as soon as it has a reply, and at the"
                    " registered rate before that"
                ),
                "why_one_leg": (
                    "r2 priced every leg still owed because its shot's 64 calls were what made the"
                    " dev legs affordable. This contract has ONE leg, so «every leg still owed» and"
                    " «the running leg» are the same set — the formula did not need weakening and"
                    " was not weakened"
                ),
                "verdict": (
                    f"KILL if the projection exceeds ${CAP_USD:.2f} at the LIVE price, or exceeds"
                    f" the {HARD_STOP_SECONDS:.0f} s hard stop in seconds. The stricter binds"
                ),
            },
        },
        "recovery_arithmetic": {
            "re_creations_allowed": 1,
            "one_dead_pod_at_rung_2_seconds": SSH_DEADMAN_SECONDS,
            "one_dead_pod_at_rung_2_usd": round(dead_pod, 6),
            "deletion_tail": tail,
            "one_dead_pod_at_rung_2_with_the_measured_tail_seconds": dead_pod_seconds,
            "one_dead_pod_at_rung_2_with_the_measured_tail_usd": round(dead_pod_with_tail, 6),
            "with_the_tail_then_the_full_worst_case_seconds": round(dead_pod_seconds + total, 3),
            "with_the_tail_then_the_full_worst_case_usd": round(dead_pod_with_tail + worst, 6),
            "margin_after_the_tail_seconds": round(HARD_STOP_SECONDS - dead_pod_seconds - total, 3),
            "the_tail_rule": (
                "rung 2's ceiling is a CREATE-ELAPSED, and the meter stops at `pod delete` and not"
                " when the rung fires. r1 measured the span between them twice —"
                f" {tail['measured_seconds']} — and the worse of the two is charged here. So the"
                f" clause is reachable at {round(dead_pod_seconds + total, 2)} s ≤"
                f" {HARD_STOP_SECONDS:.0f}, a margin of"
                f" {round(HARD_STOP_SECONDS - dead_pod_seconds - total, 2)} s and NOT the"
                f" {round(HARD_STOP_SECONDS - SSH_DEADMAN_SECONDS - total, 2)} s the ceiling alone"
                " implies. The runbook says «delete immediately» because of this number"
            ),
            "then_the_full_worst_case_seconds": round(SSH_DEADMAN_SECONDS + total, 3),
            "then_the_full_worst_case_usd": round(dead_pod + worst, 6),
            "widest_dead_pod_that_still_fits_seconds": round(HARD_STOP_SECONDS - total, 3),
            "rule": (
                "the recovery clause must stay REACHABLE after one dead pod. One dead pod at rung 2"
                f" plus the full worst case is {round(SSH_DEADMAN_SECONDS + total, 2)} s ≤"
                f" {HARD_STOP_SECONDS:.0f} and ${round(dead_pod + worst, 4)} ≤ ${CAP_USD:.2f}, so"
                " ONE re-creation fits by the registered arithmetic. `--pre-create-check` computes"
                " both bounds before every create and the stricter binds"
            ),
            "the_knife_edge": (
                f"the widest dead pod that still leaves the whole worst case inside the stop is"
                f" {round(HARD_STOP_SECONDS - total, 2)} s, which is WIDER than rung 2's"
                f" {SSH_DEADMAN_SECONDS:.0f} s ceiling — so a pod killed by rung 2 can never be the"
                " one that closes the recovery clause"
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


def rung_4_sensitivity(sums: dict, calls: int, rate: dict) -> dict:
    """What a SINGLE slow call costs at rung 4 — computed at BOTH pre-generations, worst first.

    `leg_state` prices the remainder at the LARGER of the leg's mean and its LAST call, so one slow
    reply is priced as if every remaining call were that slow. That is the pessimistic direction and
    it is correct — but the knife edge it creates depends on a span this record carries TWO values
    for, and the two disagree about whether there is any margin at all:

    * `pre_generation_measured` = 254.6 s, r2's create-elapsed at its first reply. At this span the
      edge is ~4.8 s/call and the worst call this stack has measured (4.066 s) is comfortably under
      it.
    * `pre_generation_seconds` = 1 100 s, what the MONEY BLOCK CHARGES and what rung 3's backstop
      allows. At this span the sustained rate the hard stop can pay for is only
      (6 500 − 1 300 − 1 100) / 1 032 = **3.9729 s/call — BELOW the 4.066 s already measured**, and
      one such call landing as the most recent row at an early poll KILLs the pod.

    A curve computed over one span and quoted about a budget that pays for the other is the class
    this program keeps buying ([[a_ceiling_derived_from_one_span_measured_over_another]]). Both are
    computed here and the WORSE one is the headline. Nothing is loosened: `leg_state` and
    `projection` are r2's, pinned, and pricing the remainder at the mean would be the permissive
    direction. What this block buys is that a KILL is a FORESEEN outcome with an instruction, and
    that the executor knows before the create which of the two worlds the pod is in.
    """
    stop = float(sums["cumulative"]["hard_stop_seconds"])
    overhead = float(sums["overhead_seconds"])
    charged_pre = float(sums["pre_generation_seconds"])
    mean = float(rate["mean"])
    slowest = float(rate["slowest_call"])

    def curve(pre: float) -> list[dict]:
        return [
            {
                "at_call": at,
                "create_elapsed_seconds": round(pre + at * mean, 1),
                "kill_above_seconds_per_call": round(
                    (stop - overhead - pre - at * mean) / (calls - at), 3
                ),
            }
            for at in (10, 20, 100, 200, 400, 700, 1000)
        ]

    measured, charged = curve(R2_PRE_GENERATION_MEASURED), curve(charged_pre)
    tight_measured = min(one["kill_above_seconds_per_call"] for one in measured)
    tight_charged = min(one["kill_above_seconds_per_call"] for one in charged)
    sustained = (stop - overhead - charged_pre) / calls
    return {
        "formula": (
            "(hard_stop − overhead − pre_generation − n × measured_mean) / (calls − n), and the"
            " pre_generation is the span this record carries two values for"
        ),
        "measured_mean_seconds_per_call": round(mean, 6),
        "slowest_call_in_the_sample": slowest,
        "at_the_MEASURED_pre_generation": {
            "pre_generation_seconds": R2_PRE_GENERATION_MEASURED,
            "source": "r2's create-elapsed at its first reply, 2026-08-21",
            "curve": measured,
            "tightest_kill_above_seconds_per_call": tight_measured,
            "headroom_over_the_slowest_call_measured": round(tight_measured / slowest, 3),
        },
        "at_the_CHARGED_pre_generation": {
            "pre_generation_seconds": charged_pre,
            "source": "money.arithmetic.pre_generation_seconds — and rung 3's own backstop",
            "curve": charged,
            "tightest_kill_above_seconds_per_call": tight_charged,
            "headroom_over_the_slowest_call_measured": round(tight_charged / slowest, 3),
        },
        "sustained_rate_the_charged_pre_generation_can_pay_for": round(sustained, 4),
        "the_headline": (
            f"at the pre-generation the budget CHARGES, the sustained rate the hard stop can pay for"
            f" is {round(sustained, 4)} s/call and the slowest call this stack has measured is"
            f" {slowest} — the measured worst is ABOVE it. One such call landing as the most recent"
            f" row at an early poll makes rung 4 project past {stop:.0f} s and KILL. At the"
            f" pre-generation r2 actually MEASURED ({R2_PRE_GENERATION_MEASURED} s) the edge is"
            f" {tight_measured} s/call and the same call is safe by"
            f" {round(tight_measured / slowest, 2)}×. The pod is in one world or the other by the"
            " time the first reply lands, and rung 3's GO is where the executor reads which"
        ),
        "what_it_costs_if_it_fires": (
            "the pod is deleted mid-run and the seconds already billed are gone. Every reply is"
            " flushed as it lands and the shipped resume skips every unit already answered — but"
            " `--pre-create-check` prices a re-creation at the FULL worst case ahead, so a KILL"
            " past 583.46 s of billed seconds refuses the re-creation too and the session closes"
            " with no verdict on a run that was working. That is the whole cost and it is named"
            " here rather than discovered"
        ),
        "what_the_executor_can_do_about_it": (
            "nothing after the create, and one thing before it: the charged 1 100 s is ssh 500 +"
            " stage/launch 150 + load 450, and the staging half is HAND-DRIVEN. probe-b bounds ssh"
            " + staging + launch together at ≤ 89.5 s and r2's whole pre-generation was 254.6 s, so"
            " a brisk staging keeps the pod in the safe world. Every second spent between the ssh"
            " GO and the launch is a second rung 4 will not lend to the rate"
        ),
        "why_it_is_not_loosened": (
            "`leg_state` and `projection` are scripts/gate_pass1_fewshot.py's, pinned by r2's sealed"
            " record and imported here unedited. Pricing the remainder at the mean alone would be a"
            " weaker gate in the PERMISSIVE direction, which is the one these rungs exist to close."
            " Raising the hard stop is the operator's word: 6 500 s is the number"
            " docs/PROMPT-pass1-window.md prints, and 6 700 s would be $1.4889 — still inside the"
            " $1.50 cap and enough to put the charged-span edge at 4.167 s/call, above the measured"
            " worst. That trade is REPORTED to the operator and taken by nobody here"
        ),
    }


def bars(calls: int) -> dict:
    """The completeness bar — three numbers, and what each of them counts."""
    return {
        "completeness": {
            "rule": (
                f"answered {calls} / {calls} · every row's `rendering_sha256` equals its pack item's"
                f" · parse refusals ≤ {REFUSALS_MAXIMUM} ({REFUSALS_FRACTION:.0%}). All three, or"
                " RED"
            ),
            "owed": calls,
            "answered_minimum": calls,
            "sha_mismatches_maximum": 0,
            "parse_refusals_maximum": REFUSALS_MAXIMUM,
            "parse_refusals_fraction": REFUSALS_FRACTION,
            "answered_means": (
                "a reply came back and was written into the out-file, counted by DISTINCT id. A"
                " parse refusal is an ANSWERED row whose reply the parser refused — the two counts"
                " are NOT disjoint, and up to ten answered rows may be refusals without the bar"
                " moving. A gate that treated a refusal as unanswered would report RED at"
                f" {calls - REFUSALS_MAXIMUM} / {calls} on a run this bar accepts"
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
            "why_this_and_not_quality": (
                "the out-file is the INPUT of pass 2. What pass 2 needs from this run is that every"
                " comment has an answer and that each answer belongs to the request it was asked"
                " under. Whether the answers are GOOD is measured against"
                " docs/REFERENCE-signals-w1.md by `pass2-signals`, and by nothing here"
            ),
        },
        "report_only": {
            "our_readings": ["категория_личное", "молочный_бренд"],
            "our_readings_rule": (
                "the two labels the «our rows» readings count, carried here because"
                " gate_pass1_fewshot.py::leg_table — the function D2's clause names — reads them"
                " from `bars.dev_gate.our_readings`, a key this record does not have and must not"
                " invent: this contract has NO dev gate. D2 hands leg_table a view carrying these"
                " readings under the name it reads, and the proof that it is the same instrument is"
                " that the dev-200 subset reproduces r2's 136/200 and 38/49 — checked at $0 in"
                " tests/test_gate_pass1_window.py, on r2's own 200 replies"
            ),
            "rule": (
                "READINGS, each captioned «not a bar». None of them can pass, fail or close"
                " anything, and none of them may be quoted as a verdict on v2"
            ),
            "the_fourteen": (
                "the gold rows' agreement, with the multiplicity named — see"
                " `return_to_the_operator`"
            ),
            "the_650_labelled_rows": (
                "agreement over every labelled row inside this population, against"
                " results/labels_pass1_r1.jsonl + _r2.jsonl through"
                " scorer.reader_comment_agreement, exactly as gate_pass1_fewshot.py::leg_table"
                " computes it"
            ),
            "the_450_not_in_dev_200": (
                "the same reading on the rows no prompt was ever tuned against — a larger reading"
                " of v2 than the dev gate's, and still not a bar"
            ),
            "the_dev_200": (
                "should reproduce r2's 136/200 and 38/49 up to decoding noise. A difference is"
                " STATED and not explained away"
            ),
            "the_label_distribution": "what v2 said over the 1 032, and per thread",
            "the_pass_2_filter_table": (
                "per thread: the rows pass 1 labelled категория_личное / молочный_бренд /"
                " сеть_ритейлер, their characters and the entity block size. This is what prices"
                " `pass2-signals` and it is a census, not a bar"
            ),
        },
    }


def kill_clock(sums: dict, bar: dict) -> list[dict]:
    """r2's rungs, inherited BY NAME — and every number in them read out of this record."""
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
            "read": "money.arithmetic.ssh_rule — the spread this ceiling is, and its four readings",
            "rule": (
                f"ssh dead-man ≤ {SSH_DEADMAN_SECONDS:.0f} s of this pod's create-elapsed or KILL."
                " r2's ceiling, unmoved: its own pod answered at ≤ 50 s, which is an upper bound"
                " INSIDE the registered spread and not a reason to lower a ceiling that two pods of"
                " 2026-08-20 never reached. One dead pod under it costs"
                f" ${sums['recovery_arithmetic']['one_dead_pod_at_rung_2_usd']:.4f}"
            ),
        },
        {
            "rung": 3,
            "anchor": "launched_at",
            "before": "the first reply",
            "read": (
                "the `launched_at` stamp the runbook writes into the pod's run directory the moment"
                " the runner starts, copied back by --watch and recorded in"
                f" {RUN_RECORD}. It is never typed"
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
                f" {BOOT_SECONDS:.0f}. It is what bounds the launch anchor: a stamp taken late"
                " cannot buy a window the registration never priced, and the backstop fires with no"
                " human in the path"
            ),
            "one_leg_note": (
                "r2 read this rung off the FIRST registered leg because the shipped `run()` is"
                " called once per leg and re-zeros its own clock, so a minimum across legs would"
                " have returned the second leg's ~8 s and reported GO on any load whatever (Dv620)."
                " This contract has one leg, so there is no minimum to take — and the gate still"
                " reads the leg the record NAMES rather than scanning the run directory, because"
                " the defect was the scan and not the count"
            ),
        },
        {
            "rung": 4,
            "before": "the run is allowed to continue past a call",
            "read": "money.arithmetic.cumulative.projection_gate — the formula and its terms",
            "rule": (
                f"projection gate every {PROJECTION_EVERY_CALLS} calls: the projected attempt total"
                " at MEASURED rates, with the leg's remaining calls priced and the registered"
                " overhead added, must fit the cap at the LIVE price AND the cumulative hard stop,"
                " else KILL. The registered interval is a FLOOR — the computation is local and free"
                " and --watch runs it on every poll (Dv613: an overhead a gate carries from a"
                " previous registration prices this run with a repealed number)"
            ),
        },
        {
            "rung": 5,
            "before": "the executor may look away",
            "read": "held by scripts/gate_pass1_window.py --watch, a BLOCKING loop",
            "rule": (
                f"liveness: {IDLE_DEADLINE_SECONDS:.0f} s with no new answered row and no new"
                " pod-log line → KILL. The deadline is measured from the LAST EVENT and never from"
                " create, and an event is a RISE — a failed copy that shortens a local file is not"
                " work and does not refresh it. lora-b lost 9 720 s and an arm because every rung"
                " there watched the training log and none watched a pod that had stopped working"
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
            "on_red": (
                "RED does not delete anything already bought and does not re-run the pod: the"
                " out-file, its refusals by cause and its sha mismatches go back to the team lead"
                " with the census. A partial out-file is still the evidence, and the resume can"
                " re-ask only what has no reply — but a second pod is the recovery clause's, and"
                " the recovery clause allows one"
            ),
        },
    ]


def h6(sums: dict, rate: dict, calls: int, threads: int) -> dict:
    """Every number `docs/PROMPT-pass1-window.md` prints, re-derived from the formula it names.

    `equals` allows 1 % — a rounding is not a finding; `below` and `at_least` check the DIRECTION.
    Three rows check REASONS rather than numbers, because a reason nothing re-derives is how a bound
    that double-counted the ssh wait shipped in r1 (Dv605).
    """
    cumulative = sums["cumulative"]
    recovery = sums["recovery_arithmetic"]
    overhead = sums["overhead_measured_on_r2"]
    sensitivity = cumulative["projection_gate"]["single_call_sensitivity"]
    rows = [
        # --- the inputs. This is the half a re-multiplication cannot catch ---
        {
            "name": "population_payable_comments",
            "formula": "gate_census_w1_reader.population(), CALLED and counted",
            "registered": 1032,
            "re_derived": calls,
            "mode": "equals",
        },
        {
            "name": "population_threads",
            "formula": "gate_census_w1_reader.population(), CALLED and counted",
            "registered": 129,
            "re_derived": threads,
            "mode": "equals",
        },
        {
            "name": "v2_seconds_per_call_measured",
            "formula": f"mean of `seconds` over {rate['rows']} rows of {rate['file']}",
            "registered": 2.726,
            "re_derived": round(rate["mean"], 6),
            "mode": "equals",
        },
        {
            "name": "the_charged_rate_is_not_below_the_measurement_times_the_margin",
            "formula": f"{CHARGED_SECONDS_PER_CALL} ≥ measured mean × {RATE_MARGIN}",
            "registered": round(rate["mean"] * RATE_MARGIN, 6),
            "re_derived": CHARGED_SECONDS_PER_CALL,
            "mode": "at_least",
        },
        {
            "name": "rate_margin",
            "formula": f"{CHARGED_SECONDS_PER_CALL} / 2.726",
            "registered": RATE_MARGIN,
            "re_derived": CHARGED_SECONDS_PER_CALL / 2.726,
            "mode": "equals",
        },
        # --- generation and the seconds ---
        {
            "name": "generation_seconds",
            "formula": f"{calls} calls × {CHARGED_SECONDS_PER_CALL} s/call",
            "registered": 3516.54,
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
            "registered": 5916.54,
            "re_derived": sums["total_seconds"],
            "mode": "equals",
        },
        {
            "name": "hours",
            "formula": f"{sums['total_seconds']} / 3600",
            "registered": 1.6435,
            "re_derived": sums["hours"],
            "mode": "equals",
        },
        {
            "name": "worst_case_usd_at_the_price_ceiling",
            "formula": f"{sums['hours']} h × ${PRICE_CEILING}/h",
            "registered": 1.3148,
            "re_derived": sums["worst_case_usd_at_the_price_ceiling"],
            "mode": "equals",
        },
        {
            "name": "worst_case_usd_at_the_lora_b_price",
            "formula": f"{sums['hours']} h × ${LORA_B_PRICE}/h",
            "registered": 0.8710,
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
        # --- the cumulative stop and the session ceiling ---
        {
            "name": "hard_stop_usd_at_the_price_ceiling",
            "formula": f"{HARD_STOP_SECONDS:.0f} s × ${PRICE_CEILING}/h / 3600",
            "registered": 1.4444,
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
            "registered": 6750.0,
            "re_derived": cumulative["session_ceiling_seconds"],
            "mode": "equals",
        },
        {
            "name": "the_session_ceiling_is_not_below_the_hard_stop",
            "formula": "cap / price ceiling ≥ the hard stop, so the PLATFORM holds the binding one",
            "registered": HARD_STOP_SECONDS,
            "re_derived": cumulative["session_ceiling_seconds"],
            "mode": "at_least",
        },
        # --- the recovery clause ---
        {
            "name": "one_dead_pod_at_rung_2_usd",
            "formula": f"{SSH_DEADMAN_SECONDS:.0f} s × ${PRICE_CEILING}/h / 3600",
            "registered": 0.1111,
            "re_derived": recovery["one_dead_pod_at_rung_2_usd"],
            "mode": "equals",
        },
        {
            "name": "one_dead_pod_then_the_full_worst_case_seconds",
            "formula": f"{SSH_DEADMAN_SECONDS:.0f} + {sums['total_seconds']}",
            "registered": 6416.54,
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
            "formula": f"${recovery['one_dead_pod_at_rung_2_usd']} + the worst case in dollars",
            "registered": 1.4259,
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
            "registered": 583.46,
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
        # --- the allowances carried from r2 ---
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
                f" ({WIDEST_SSH_READING} s), and both readings are LOWER bounds"
            ),
            "registered": WIDEST_SSH_READING,
            "re_derived": SSH_DEADMAN_SECONDS,
            "mode": "at_least",
        },
        {
            "name": "the_projection_gate_and_the_money_block_charge_ONE_overhead",
            "formula": "money.arithmetic.overhead_seconds == cumulative.projection_gate.overhead_seconds",
            "registered": sums["overhead_seconds"],
            "re_derived": cumulative["projection_gate"]["overhead_seconds"],
            "mode": "equals",
        },
        # --- the step, and the bar ---
        {
            "name": "step_cap_is_the_contract_cap",
            "formula": (
                "the step `pass1-window` opens with no pod of its own — there is nothing to add to"
                f" the cap, so the step cap IS ${CAP_USD:.2f}"
            ),
            "registered": CAP_USD,
            "re_derived": CAP_USD,
            "mode": "equals",
        },
        {
            "name": "parse_refusals_maximum",
            "formula": f"{REFUSALS_FRACTION:.0%} of {calls}, floored",
            "registered": REFUSALS_MAXIMUM,
            "re_derived": int(calls * REFUSALS_FRACTION),
            "mode": "equals",
        },
        # --- three rows that check a REASON ---
        {
            "name": (
                "REASON — the overhead did not move when the rows it covers went"
                f" {overhead['rows_answered']} → {calls}"
            ),
            "formula": (
                "r2's pod was deleted"
                f" {overhead['measured_after_the_last_row_seconds']} s after its last row landed,"
                f" and that span carried the whole of what this line buys. r2 REGISTERED"
                f" {R2_ROWS_COPIED_BACK} rows to copy back and MEASURED"
                f" {overhead['rows_answered']}, because its shot never fired — the scaling below"
                " divides by the MEASURED count, which is the smaller denominator and therefore the"
                " more expensive per row. Scaled to"
                f" {calls} it is {overhead['scaled_to_this_population_seconds']} s, and"
                f" {OVERHEAD_SECONDS:.0f} s is charged. The check is that the charge is ≥ the"
                " scaled measurement, not that it is equal to it"
            ),
            "registered": overhead["scaled_to_this_population_seconds"],
            "re_derived": OVERHEAD_SECONDS,
            "mode": "at_least",
        },
        {
            "name": ("REASON — the ×1.25 margin exceeds the growth it is named for"),
            "formula": (
                "the contract buys the margin «for the window's larger entity blocks». Measured on"
                " the two packs: mean entities per request"
                f" {sums['request_width']['mean_entities_sample']} →"
                f" {sums['request_width']['mean_entities_population']}, and the rendered request"
                f" they sit in {sums['request_width']['mean_rendered_chars_sample']} →"
                f" {sums['request_width']['mean_rendered_chars_population']} chars, a ratio of"
                f" {sums['request_width']['ratio']}. The margin must be ≥ that ratio, and it is"
                f" {round(RATE_MARGIN / sums['request_width']['ratio'], 2)}× it. A rate is a"
                " property of the sample it was measured on, so the growth from that sample to this"
                " population is measured and not assumed"
            ),
            "registered": sums["request_width"]["ratio"],
            "re_derived": RATE_MARGIN,
            "mode": "at_least",
        },
        {
            "name": "REASON — the recovery clause is reachable WITH the measured deletion tail",
            "formula": (
                "rung 2's ceiling is a create-elapsed and the meter stops at `pod delete`. r1"
                f" measured the span between them at {recovery['deletion_tail']['measured_seconds']}"
                f" and the worse is charged, so a real rung-2 death bills"
                f" {recovery['one_dead_pod_at_rung_2_with_the_measured_tail_seconds']} s and not"
                f" {SSH_DEADMAN_SECONDS:.0f}. That plus the full worst case must still fit the hard"
                f" stop — it does, by"
                f" {recovery['margin_after_the_tail_seconds']} s, which is the honest margin"
            ),
            "registered": HARD_STOP_SECONDS,
            "re_derived": recovery["with_the_tail_then_the_full_worst_case_seconds"],
            "mode": "below",
        },
        {
            "name": "REASON — the budget's own sustained rate covers the rate it charges",
            "formula": (
                "the hard stop must pay for the run the money block PRICES: at the charged"
                f" pre-generation the sustained rate it can afford is"
                f" ({HARD_STOP_SECONDS:.0f} − {OVERHEAD_SECONDS:.0f} −"
                f" {sums['pre_generation_seconds']:.0f}) / {calls} ="
                f" {sensitivity['sustained_rate_the_charged_pre_generation_can_pay_for']} s/call,"
                f" and the rate charged is {CHARGED_SECONDS_PER_CALL}. This is the inequality that"
                " makes the budget self-consistent — and it is NOT the same question as whether one"
                " outlier call survives rung 4, which"
                " money.arithmetic.cumulative.projection_gate.single_call_sensitivity.the_headline"
                " answers and answers NO at this span"
            ),
            "registered": CHARGED_SECONDS_PER_CALL,
            "re_derived": sensitivity["sustained_rate_the_charged_pre_generation_can_pay_for"],
            "mode": "at_least",
        },
        {
            "name": (
                "REASON — rung 4's knife edge is reported at BOTH pre-generations and the worse is"
                " the headline"
            ),
            "formula": (
                "the record carries two values for one span: pre_generation_measured"
                f" {R2_PRE_GENERATION_MEASURED} s (r2's own reading) and pre_generation_seconds"
                f" {sums['pre_generation_seconds']:.0f} s (what the money block charges). The edge"
                " is"
                f" {sensitivity['at_the_MEASURED_pre_generation']['tightest_kill_above_seconds_per_call']}"
                " s/call at the first and"
                f" {sensitivity['at_the_CHARGED_pre_generation']['tightest_kill_above_seconds_per_call']}"
                f" at the second, against a measured worst call of"
                f" {sensitivity['slowest_call_in_the_sample']} s. The check is that BOTH are"
                " computed and that the CHARGED one is the smaller, so the headline cannot quote"
                " the flattering span"
            ),
            "registered": sensitivity["at_the_CHARGED_pre_generation"][
                "tightest_kill_above_seconds_per_call"
            ],
            "re_derived": sensitivity["at_the_MEASURED_pre_generation"][
                "tightest_kill_above_seconds_per_call"
            ],
            "mode": "at_least",
        },
        {
            "name": "REASON — nothing is counted twice in the seconds line",
            "formula": (
                "the pre-generation lines and the overhead line are disjoint by construction: ssh"
                " ends when the endpoint answers, staging and launch end when the runner starts,"
                " the load ends at the first reply, and the overhead begins at the LAST reply. The"
                " sum of the named spans equals total_seconds with generation between them"
            ),
            "registered": sums["total_seconds"],
            "re_derived": (
                sums["pre_generation_seconds"]
                + sums["generation_seconds"]
                + sums["overhead_seconds"]
            ),
            "mode": "equals",
        },
        {
            "name": "REASON — the bar's two numbers are jointly reachable",
            "formula": (
                f"the bar demands answered == {calls} AND refusals ≤ {REFUSALS_MAXIMUM}. They are"
                " satisfiable together only because a refusal is an ANSWERED row whose reply the"
                " parser refused. Counting a refusal as unanswered would make the highest reachable"
                f" answered count {calls - REFUSALS_MAXIMUM}, below the bar's own minimum, and the"
                " bar would be unmeetable by construction"
                " ([[an_expectation_no_reading_reaches]])"
            ),
            "registered": calls,
            "re_derived": calls,
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
            "every number docs/PROMPT-pass1-window.md prints, re-derived from the formula the"
            " contract names for it. `equals` allows 1 % — a rounding is not a finding; `below` and"
            " `at_least` check the DIRECTION. The rows that matter are the INPUT rows: the"
            " arithmetic of a money block is the same multiplication done twice and cannot"
            " disagree with itself, so what H6 catches is a population that moved, a rate whose"
            " sample is not what it claims, or an allowance carried across a re-registration"
            " without its reason"
        ),
        "rows": rows,
        "mismatches": mismatches,
        "reading": (
            "every registered number re-derives"
            if not mismatches
            else f"{len(mismatches)} registered numbers do NOT re-derive — this is a STOP"
        ),
    }


LEG_OUT_HINT = "pass1_window_v2.jsonl"


def build() -> dict:
    r2 = sealed(R2, R2_NAME)
    pack = json.loads(summary.read_text_or_refuse(PACK))
    calls = len(pack["legs"][0]["items"])
    threads = pack["population"]["threads"]
    rate = measured_v2_rate()
    r2_run = sealed(R2_RUN, summary.rel(R2_RUN))
    overhead = r2_overhead_reading(r2_run)
    tail = deletion_tail(sealed(R1_RUN, R1_RUN_NAME))
    sums = arithmetic(rate, calls, overhead, tail)
    sums["cumulative"]["projection_gate"]["single_call_sensitivity"] = rung_4_sensitivity(
        sums, calls, rate
    )
    total_seconds = sums["total_seconds"]
    bar = bars(calls)

    return {
        "phase": "pass1-window",
        "contract": "docs/PROMPT-pass1-window.md",
        "authority": (
            "the operator's rulings of 2026-08-21 in the team-lead session, registered in"
            " docs/STATUS.md «Открытые решения», п. 1 (а)–(д): v2 is the BASE prompt of pass 1;"
            " the next step is the end-to-end window run; two contracts, one paid run each, and"
            " THIS one is pass 1 only at a cap of $1.50"
        ),
        "what_this_run_is": (
            "a PRODUCTION pass over the whole window-1 reader population on prompt v2. Its out-file"
            " is the INPUT of `pass2-signals`, which is priced from THIS run's census"
        ),
        "what_this_run_is_not": (
            "**NOT an evaluation.** There is no dev gate, no paired arm, no bar on v2's quality and"
            " no attempt to spend. v2 was measured in `pass1-fewshot r2` and its dev gate answered"
            " RED at +7 of +10; the operator's ruling ships it as the PROVISIONAL filter for an"
            " end-to-end measurement, not as an accepted deliverable. Nothing in this record, this"
            " run or its report may be read as v2 passing anything"
        ),
        "return_to_the_operator": (
            "**The fourteen gold rows and probe-b's sixty-four are INSIDE this population and are"
            " answered like every other comment.** Their agreement with the gold is a REPORT-ONLY"
            " census row and it carries its multiplicity: this is the FOURTH look at the same"
            " fourteen — the base (pass1-probe-b, 9/14), arm A of the LoRA line (lora-b, 9/14), v2"
            " which was registered for a shot it never fired because its dev gate went RED, and now"
            " v2 inside a production pass that was registered for transport. A reading taken on"
            " rows this program has already looked at three times is a reading and never a bar. It"
            " cannot be promoted to «v2 takes N of 14» by anyone — not by this report, not by the"
            " acceptance, not by the next registration — and a bar on the fourteen needs a NEW"
            " registration with its own attempt, its own pre-declared threshold and the operator's"
            " word ([[a_reproducible_probe_can_be_unrepresentative]]). The same holds for the 650"
            " labelled rows and the 450 outside dev-200: larger readings, still readings"
        ),
        "attempt": (
            "there is no ONE-ATTEMPT clause here and that is deliberate. `pass1-fewshot`'s attempt"
            " was the right to fire a registered prompt at a sealed exam once; this run answers a"
            " production population, and the exam rows inside it are answered BECAUSE they are in"
            " the population and not because anyone is taking a shot. The attempt r2 left intact"
            " stays intact: it belongs to a bar on the fourteen, and no bar on the fourteen is"
            " being taken here"
        ),
        "instruments": instruments(r2),
        "population": {
            "pack": PACK_NAME,
            "sha256": sha(PACK),
            "cell": pack["population"]["cell"],
            "threads": threads,
            "payable_comments": calls,
            "leg": pack["legs"][0]["name"],
            "out_file": pack["legs"][0]["out"],
            "membership": {
                name: pack["membership"][name]["n"]
                for name in ("gold_14", "probe_64", "labelled_650", "dev_200")
            },
            "gold": {
                "rows": [
                    {"thread": one.rsplit("#", 1)[0], "msg_id": int(one.rsplit("#", 1)[1])}
                    for one in pack["membership"]["gold_14"]["ids"]
                ],
                "rule": (
                    "the fourteen by (thread, msg_id), taken from the pack's own membership block."
                    " D2 reads this list rather than re-joining the gold to the population after"
                    " the money — and it is the pair key everywhere, because a msg_id is unique per"
                    " CHANNEL and 13 of this population's are carried by two threads"
                ),
            },
            "widest_request_chars": pack["length"]["widest_request_chars"],
            "ceiling_chars": pack["length"]["ceiling_chars"],
            "self_exclusion": {
                "items_shown_a_neighbour_from_their_own_thread": len(
                    pack["self_exclusion"]["items_shown_a_neighbour_from_their_own_thread"]
                ),
                "items_whose_own_thread_carries_labels": pack["self_exclusion"][
                    "items_whose_own_thread_carries_labels"
                ],
                "labels_withheld_from_those_items": pack["self_exclusion"][
                    "labels_withheld_from_those_items"
                ],
            },
            "rule": (
                "derived by CALLING gate_census_w1_reader.population(); the contract's «1 032"
                " payable comments of 129 threads» is the expectation the producer refuses on"
            ),
        },
        "bars": bar,
        "kill_clock": kill_clock(sums, bar),
        "money": {
            "cap_usd_all_in": CAP_USD,
            "cap_rule": (
                f"${CAP_USD:.2f} all-in, frozen at the FIRST `pod create`. The step `pass1-window`"
                " opens with no pods of its own, so the step cap and the contract cap are the same"
                " number and there is nothing prior to add. Raising it is the operator's word"
                " BEFORE any endpoint exists, never after a reading"
            ),
            "arithmetic": sums,
            "recovery": {
                "arithmetic": sums["recovery_arithmetic"],
                "rule": (
                    "ONE pod re-creation, and only after a deletion PROVEN by listing. Never two"
                    " billing endpoints. `--pre-create-check` computes both bounds and refuses the"
                    " create itself"
                ),
                "two_meters_and_the_stricter_binds": (
                    "`--pre-create-check` computes from the GATE's own ledger — the closed pods'"
                    " billed seconds at their own price, which is timely and exact to the pod"
                    " clock. `scripts/runpod_guard.py` reads the BALANCE delta and the billing walk,"
                    " which is what the cap is defined against and which LAGS by up to ~32 min"
                    " (Dv504). They are two meters and neither is the other: the gate's refuses a"
                    " create the seconds cannot pay for, the guard's refuses one the money cannot."
                    " The runbook takes BOTH readings before a re-creation and the stricter binds —"
                    " a clause that named one and computed the other would be true of neither"
                    " ([[a_balance_delta_is_not_a_per_leg_cost]])"
                ),
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
                    f"`--pre-create-check` prices the FULL worst case ahead ({total_seconds} s) and"
                    " not the calls that actually remain, so a re-creation is refused once the dead"
                    f" pod has billed more than {round(HARD_STOP_SECONDS - total_seconds, 2)} s —"
                    " whatever the resume would have saved. A KILL at rung 2 or rung 3 is inside"
                    " that window; a KILL deep inside the generation is NOT, and the clause is then"
                    " a STOP and not a recovery. This is the registered arithmetic and not a"
                    " defect: the seconds are what the platform holds, and pricing a re-creation at"
                    " «only what remains» would open a run the cap closes. It is written down"
                    " because a clause that reads as unconditional is a clause somebody will lean"
                    " on at the one moment it does not hold"
                    " ([[the_contracts_scope_is_narrower_than_the_rulings]])"
                ),
                "what_the_pod_keeps_and_what_it_clears": (
                    "on a re-creation the volume still holds /workspace/run/"
                    + LEG_OUT_HINT
                    + " and it MUST be kept — it is the whole of «costs the boot, not the leg»."
                    " What must go is every clock the dead pod owns: `launched_at`, which the gate"
                    " refuses as older than the new pod, and `pod.log`, whose line count would be a"
                    " high-water mark the new pod never rises above. The runbook's staging step"
                    " wipes the directory on the FIRST pod and only on the first"
                ),
            },
            "meter": {
                "resource": (
                    "ONE rented pod, billed for every second it EXISTS — from `pod create` to `pod"
                    " delete`. `pod stop` does not stop the bill, so the run deletes and never stops"
                ),
                "price_ceiling_usd_per_hour": PRICE_CEILING,
                "usd_per_second_at_the_ceiling": round(PRICE_CEILING / 3600, 9),
                "price_rule": (
                    "**READ ON THE DAY.** `costPerHr` in the create response is the meter of record"
                    " and every figure here is recomputed from it by rung 4 before the run is"
                    " allowed to continue"
                ),
                "datacenter": "EU-RO-1, pinned by network volume qw4nwleanc — the volume decides",
                "card_preferred": (
                    "RTX 4090 at ≤ $0.80/h — the card probe-b's and r2's rates were measured on."
                    " Under the ceiling in EU-RO-1 on 2026-08-21: 4090 24 GB $0.74, RTX PRO 4500"
                    " 32 GB $0.72, L4 24 GB $0.49. A6000 48 GB was `none`"
                ),
                "memory": (
                    "this line does NOT train, so lora-b's 48 GB constraint does not apply: probe-b"
                    " and r2 both served this base on a 24 GB 4090"
                ),
            },
            "reading": {
                "step": "pass1-window",
                "anchor_file": "results/spend_pass1_window.json",
                "rule": "money is read from the GUARD, never from a ledger and never from prose (Dv33)",
            },
            "guard": (
                f"PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-window --step-cap"
                f" {CAP_USD:.2f} — the anchor is committed BEFORE the pod exists, and the reading is"
                " what the rungs that name one act on"
            ),
            "step_sum": {
                "step_budget_usd": CAP_USD,
                "prior_pods_usd": 0.0,
                "sum_usd": CAP_USD,
                "rule": (
                    "the step opens with no pods. `pass1-fewshot`'s $0.397133 belongs to ITS step"
                    " ledger, which is closed, and is not added here — the operator's ruling (д)"
                    " gives `pass1-window` and `pass2-signals` a cap of $1.50 each"
                ),
            },
        },
        "h6": h6(sums, rate, calls, threads),
        "frozen_when_the_pod_exists": [
            "docs/PROMPT-pass1-window.md and every other docs/PROMPT-*.md — team-lead files",
            "src/market_pulse/prompts.py — v2, v1, the renderer and the parser",
            f"{PACK_NAME} — the pack, its items and their per-item shas",
            OUT_NAME + " — this record",
            "results/labels_pass1_r1.jsonl and _r2.jsonl — the team lead's labels",
            "results/reader_gold_w1_r2.json — the gold",
            "results/pass1_probe_b_pack.json and its verdict — sealed",
            "results/prereg_pass1_fewshot.json and _r2.json — sealed, superseded, never re-opened",
            "results/pass1_dev_pack.json, pass1_dev_base.jsonl, pass1_dev_v2.jsonl — r2's evidence",
            "scripts/gate_pass1_fewshot.py — r2's instrument, IMPORTED here and never edited",
            "scripts/pass1_fewshot_pod_runner.py, scripts/pass1_pod_runner.py,"
            " scripts/reader_v5_pod_runner.py — the transport that runs ON the pod. The pack pins"
            " the parser sha the handshake checks, so an edit here is refused by the pod and not by"
            " a human",
            "results/spend_pass1_window.json — the step anchor. Regenerating it re-zeroes the step"
            " at that day's balance, which is the one way this cap stops being a cap",
            "scripts/gate_pass1_window.py and scripts/build_pass1_window_pack.py — pinned by this"
            " record; an edit after the create moves a pin the gate itself is read through",
        ],
        "do_not": [
            "no change to prompt v2, the neighbour rule, the labels, the gold or any sealed record",
            "no second leg — the base was measured in r2 and is not re-run",
            "no dev gate; this contract has none",
            "no re-purchase of reader context — the v5b / v4 / topup verdicts are read, never bought",
            "no generation before H6 re-derives and the D0 commits are in",
            "never leave --watch while a pod is live",
            "never two billing endpoints CONCURRENTLY; one re-creation after a PROVEN deletion",
            "no third pod",
        ],
        "run_record": RUN_RECORD,
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": sha(Path(__file__)),
            "supersedes_nothing": (
                "this is a NEW line, not a re-registration. `results/prereg_pass1_fewshot_r2.json`"
                " is the record its instruments and its kill clock are COPIED from, and it is"
                " sealed, closed and never re-opened"
            ),
            "copied_from": {"record": R2_NAME, "sha256": sha(R2)},
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    record = build()
    path = args.outdir / OUT_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUT_NAME}  sha256 {summary.sha256_of(path)[:16]}…")

    sums = record["money"]["arithmetic"]
    print(
        f"  population: {record['population']['threads']} threads ·"
        f" {record['population']['payable_comments']} payable comments · one leg"
        f" {record['population']['leg']} → {record['population']['out_file']}"
    )
    print(
        f"  generation: {sums['calls']['v2']} × {sums['seconds_per_call']['v2']} s ="
        f" {sums['generation_seconds']} s   (measured mean"
        f" {sums['seconds_per_call']['measured_mean']} over {R2_SAMPLE})"
    )
    print(
        f"  worst case: {sums['total_seconds']} s = {sums['hours']} h ="
        f" ${sums['worst_case_usd_at_the_price_ceiling']} at ${PRICE_CEILING}/h"
        f"  (${sums['worst_case_usd_at_the_lora_b_price']} at ${LORA_B_PRICE}/h)"
    )
    print(
        f"  cap ${record['money']['cap_usd_all_in']:.2f} · hard stop"
        f" {sums['cumulative']['hard_stop_seconds']:.0f} s ="
        f" ${sums['cumulative']['hard_stop_usd_at_the_price_ceiling']} · session ceiling"
        f" {sums['cumulative']['session_ceiling_seconds']:.0f} s"
    )
    recovery = sums["recovery_arithmetic"]
    print(
        f"  recovery: one dead pod {recovery['one_dead_pod_at_rung_2_seconds']:.0f} s"
        f" (${recovery['one_dead_pod_at_rung_2_usd']}) + the worst case ="
        f" {recovery['then_the_full_worst_case_seconds']} s ≤"
        f" {sums['cumulative']['hard_stop_seconds']:.0f} and"
        f" ${recovery['then_the_full_worst_case_usd']} ≤"
        f" ${record['money']['cap_usd_all_in']:.2f} · widest dead pod that fits"
        f" {recovery['widest_dead_pod_that_still_fits_seconds']} s"
    )
    bar = record["bars"]["completeness"]
    print(
        f"  bar: answered {bar['answered_minimum']}/{bar['owed']} · sha mismatches"
        f" {bar['sha_mismatches_maximum']} · parse refusals ≤ {bar['parse_refusals_maximum']}"
    )
    h6_block = record["h6"]
    print(
        f"  H6: {len(h6_block['rows'])} rows · {len(h6_block['mismatches'])} mismatches —"
        f" {h6_block['reading']}"
    )
    for row in h6_block["mismatches"]:
        print(f"    MISMATCH {row['name']}: {row['formula']}")
    return 2 if h6_block["mismatches"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
