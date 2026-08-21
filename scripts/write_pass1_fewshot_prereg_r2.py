#!/usr/bin/env python3
"""`results/prereg_pass1_fewshot_r2.json` — the SAME line, re-registered on the 20.08 environment.

**A SIBLING producer, not a `--revision` flag on `scripts/write_pass1_fewshot_prereg.py`.** The
operator offered the choice and this is the answer: the r1 producer hashes ITSELF into the record it
writes (`producer.sha256`), so a flag added to it moves that pin and r1 stops rebuilding byte for
byte — the one property `docs/PROMPT-pass1-fewshot-r2.md` asks acceptance to diff against `c7cbfd1`.
A sibling leaves r1's producer untouched, and r1 keeps rebuilding at every path except the one this
contract genuinely moves ([[provenance_cannot_name_itself]]).

**What r2 changes, and only this.** The question, the bars, the packs, the prompt, the holdout, the
dev gate, the attempt and its multiplicity are r1's — COPIED out of the committed r1 record rather
than recomputed, so «byte-identical» is true by construction and not by a claim acceptance has to
re-derive. What moved is the environment reading: on 2026-08-20 ssh on two 4090s in EU-RO-1 was
still `pod not ready` at 262.5 s and 231.9 s of create-elapsed (probe-b on 18.08: 14.5 s). Four
amendments, each from a named finding — rung 2's ceiling (Dv602), rung 3's ANCHOR (Dv605), the two
pins the r1 registration could no longer absorb (Dv603, Dv606), and the money re-derived for the new
allowances.

**The copy is a REFUSAL, not a convenience.** Every pin inside a copied block is checked against the
live file it names, and a single divergence is a `SystemExit` before the record is written: a block
copied out of r1 that no longer describes this checkout would re-register yesterday's world under
today's name ([[a_frozen_record_is_an_input_to_shipped_code]]).

**H6 is still the step-1 refusal gate.** Every figure `docs/PROMPT-pass1-fewshot-r2.md` prints is
re-derived here from the formula the contract names for it, including the three the contract states
as REASONS: why 500 and not 600, why the overhead fell from 1 800 to 1 300 with no double count, and
what the 464 rows of the scp are. A reason nothing re-derives is how Dv605 shipped a bound that
double-counted the ssh wait.

    PYTHONPATH=src python3.11 scripts/write_pass1_fewshot_prereg_r2.py
    PYTHONPATH=src python3.11 scripts/write_pass1_fewshot_prereg_r2.py --outdir /tmp/again  # the pair
"""

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pass1_fewshot_packs as packs  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_pass1_fewshot_prereg as r1_producer  # noqa: E402

OUT_NAME = "results/prereg_pass1_fewshot_r2.json"
R1_NAME = "results/prereg_pass1_fewshot.json"
R1_RUN_NAME = "results/pass1_fewshot_run.json"

R1 = REPO_ROOT / R1_NAME
R1_RUN = REPO_ROOT / R1_RUN_NAME
GATE = REPO_ROOT / "scripts" / "gate_pass1_fewshot.py"
SCORER = REPO_ROOT / "scripts" / "score_pass1_fewshot.py"

# --- what r2 moves. Every other number in this file is r1's, copied ---------------------------------

CAP_USD = 1.38
STEP_BUDGET_USD = 1.50
SSH_DEADMAN_SECONDS = 500.0
STAGE_LAUNCH_SECONDS = 150.0
OVERHEAD_SECONDS = 1300.0
HARD_STOP_SECONDS = 6100.0
BACKSTOP_TOLERANCE_SECONDS = 60.0

# unchanged from r1, restated here because the arithmetic below is re-derived and not copied
PRICE_CEILING = 0.80
BOOT_SECONDS = 450.0
BASE_SECONDS_PER_CALL = 5.162
V2_MULTIPLIER = 1.5
IDLE_DEADLINE_SECONDS = 600.0
PROJECTION_EVERY_CALLS = 20
R1_OVERHEAD_SECONDS = 1800.0
COUNTERFACTUAL_SSH_SECONDS = 600.0

PROBE_B_SSH_SECONDS = 14.5
"""probe-b's ssh wait on 2026-08-18, on this same card in this same datacenter. The other end of the
spread rung 2 is now registered as — 500 s is a SPREAD (14.5 s … >262.5 s), never a measurement."""

PROBE_B_EVERYTHING_ELSE_SECONDS = 89.5
"""657 s billed − 237.155 s of model load − 330.3 s of generation, from `results/pass1_probe_b_run.json`'s
own arithmetic: the only bound this stack has on ssh + staging + launch TOGETHER, and it already
CONTAINS probe-b's own 14.5 s of ssh (the correction Dv605 carries)."""

WORST_MEASURED_BOOT = 353.0
"""lora-b, the same volume. Rung 3's ceiling is ≥ this by ×1.2748 and that has not moved in r2 —
what moved is the span the ceiling is measured OVER."""


def sha(path: Path) -> str:
    return summary.sha256_of(path)


def sealed_r1() -> dict:
    """r1, read from a file git says is committed and unmodified. Nothing else may be copied.

    The whole value of «byte-identical to r1» is that r1 predates this session's money. A copy taken
    from a working tree nobody committed proves the opposite ([[preregistration_is_a_file_not_a_constant]]).
    """
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(R1)], cwd=REPO_ROOT, capture_output=True
    )
    if tracked.returncode != 0:
        raise SystemExit(f"{R1_NAME} is not tracked by git — there is no sealed r1 to copy from.")
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", str(R1)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if dirty.stdout.strip():
        raise SystemExit(
            f"{R1_NAME} differs from HEAD: {dirty.stdout.strip()}. r1 is NEVER edited and r2 copies"
            " it — stop and report."
        )
    return json.loads(summary.read_text_or_refuse(R1))


COPIED = (
    "what_this_line_is",
    "attempt",
    "multiplicity",
    "return_to_the_operator",
    "bars",
    "population",
    "instruments",
)
"""The blocks `docs/PROMPT-pass1-fewshot-r2.md` requires to be r1's byte for byte — the question,
the bars, the packs, the prompt, the holdout, the dev gate, the attempt and its multiplicity. Two
pins INSIDE `instruments` are the declared exceptions and are handled below by name."""


def dig(record: dict, path: str):
    for key in path.split("."):
        record = record[key]
    return record


def live_pins() -> dict[str, str]:
    """Every pin a copied block carries, resolved against the file it names, RIGHT NOW."""
    return {
        "bars.judge.module_sha256": sha(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
        "population.dev.sha256": sha(REPO_ROOT / packs.DEV_NAME),
        "population.shot.sha256": sha(REPO_ROOT / packs.SHOT_NAME),
        "population.gold.sha256": sha(REPO_ROOT / "results" / "reader_gold_w1_r2.json"),
        "population.holdout.sha256": sha(REPO_ROOT / "results" / "pass1_holdout_100.json"),
        "population.shot.sealed_source.sha256": sha(
            REPO_ROOT / "results" / "pass1_probe_b_pack.json"
        ),
        "instruments.parser.sha256": sha(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
        "instruments.scorer.sha256": sha(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
        "instruments.transport.sha256": sha(REPO_ROOT / "scripts" / "pass1_fewshot_pod_runner.py"),
        "instruments.packs.sha256": sha(REPO_ROOT / "scripts" / "build_pass1_fewshot_packs.py"),
    }


def copied(r1: dict) -> dict:
    """r1's eight blocks, and the refusal that keeps them describing THIS checkout.

    `instruments.gate` is the one pin that MUST move — the gate is the instrument this contract
    amends — so it is excluded here and re-pinned by `build`. Everything else is compared, and a
    divergence stops the producer before a single byte is written.
    """
    out = {name: json.loads(json.dumps(r1[name])) for name in COPIED}
    drifted = {
        path: {"copied_from_r1": dig(out, path), "live": value}
        for path, value in live_pins().items()
        if dig(out, path) != value
    }
    if drifted:
        raise SystemExit(
            "a block copied out of r1 no longer describes this checkout: "
            + json.dumps(drifted, ensure_ascii=False, indent=2)
            + "\nr2 re-registers the SAME line. A pin that has moved is a different line and needs"
            " the operator, not a re-run."
        )
    return out


# --- the readings the four amendments are derived from ---------------------------------------------


def ssh_readings(run: dict) -> dict[str, float]:
    """The two 2026-08-20 readings, taken out of r1's own gate record and never typed.

    They are LOWER bounds: on neither pod was ssh ever observed ready, so what the rung recorded is
    «still not up at N s», not «up at N s» ([[unreadable_now_versus_never]]).
    """
    out = {}
    for gate in run["gates"]:
        if gate.get("kind") == "gate0" and gate.get("verdict") == "KILL":
            out[f"{gate['pod_id']} (pod {gate['pod']}, {gate['at']})"] = float(
                gate["elapsed_on_this_pod_seconds"]
            )
    if len(out) != 2:
        raise SystemExit(
            f"{R1_RUN_NAME} carries {len(out)} rung-2 KILLs, not the two r1's report registers."
            " The ceiling below is derived from them — stop and report."
        )
    return out


def r1_pods(run: dict) -> dict:
    closed = [one for one in run["pods"] if one.get("deleted_at")]
    if len(closed) != len(run["pods"]):
        raise SystemExit(f"{R1_RUN_NAME} still has an OPEN pod. r1 is closed — stop and report.")
    return {
        "pods": len(closed),
        "billed_seconds": round(sum(float(one["billed_seconds"]) for one in closed), 1),
        "billed_usd": round(sum(float(one["billed_usd"]) for one in closed), 6),
    }


def arithmetic(r1: dict, run: dict) -> dict:
    """Every money figure of r2, computed from the calls the packs carry and the seconds r2 buys.

    The call counts are re-derived from the LIVE packs through r1's own `counts()` and then compared
    with what r1 registered. Copying them would have made the generation legs a quotation; two
    independent derivations that agree are what says the packs did not move
    ([[trace_the_producer_not_the_result]]).
    """
    n = r1_producer.counts()
    if n != r1["money"]["arithmetic"]["calls"]:
        raise SystemExit(
            "the live packs carry "
            + json.dumps(n, ensure_ascii=False)
            + " calls and r1 registered "
            + json.dumps(r1["money"]["arithmetic"]["calls"], ensure_ascii=False)
            + ". r2 re-registers the SAME question — a pack that moved is a different one, and it"
            " needs the operator."
        )
    v2_rate = round(BASE_SECONDS_PER_CALL * V2_MULTIPLIER, 6)
    legs = {
        "base": n["dev_base"] * BASE_SECONDS_PER_CALL,
        "v2": n["dev_v2"] * v2_rate,
        "shot": n["shot"] * v2_rate,
    }
    generation = sum(legs.values())
    pre_generation = SSH_DEADMAN_SECONDS + STAGE_LAUNCH_SECONDS + BOOT_SECONDS
    total = pre_generation + generation + OVERHEAD_SECONDS
    hours = total / 3600
    dead_pod_usd = SSH_DEADMAN_SECONDS * PRICE_CEILING / 3600
    worst_usd = hours * PRICE_CEILING
    readings = ssh_readings(run)
    counterfactual_total = (
        COUNTERFACTUAL_SSH_SECONDS
        + STAGE_LAUNCH_SECONDS
        + BOOT_SECONDS
        + generation
        + OVERHEAD_SECONDS
    )
    return {
        "calls": n,
        "rows_copied_back": n["dev_base"] + n["dev_v2"] + n["shot"],
        "seconds_per_call": json.loads(json.dumps(r1["money"]["arithmetic"]["seconds_per_call"])),
        "leg_seconds": {name: round(value, 3) for name, value in legs.items()},
        "generation_seconds": round(generation, 3),
        "ssh_seconds_charged": SSH_DEADMAN_SECONDS,
        "ssh_rule": (
            f"rung 2's own ceiling, charged as a line of the budget. It is a SPREAD and not a"
            f" measurement: probe-b saw ssh at {PROBE_B_SSH_SECONDS} s on this card in this"
            f" datacenter on 2026-08-18, and on 2026-08-20 two pods were still `pod not ready` at"
            f" {' and '.join(f'{one} s' for one in sorted(readings.values(), reverse=True))} — both"
            " of them LOWER bounds, because ssh was never observed up. The ceiling is"
            f" ×{round(SSH_DEADMAN_SECONDS / min(readings.values()), 4)} the smaller of the two"
        ),
        "ssh_readings_2026_08_20": readings,
        "ssh_observed_ready": {"pass1-probe-b, 2026-08-18, the same card": PROBE_B_SSH_SECONDS},
        "stage_launch_seconds_charged": STAGE_LAUNCH_SECONDS,
        "stage_launch_rule": (
            f"scp of the bundle and the runners, the clone, the volume check and the detached"
            f" launch. probe-b bounds all of it at ≤ {PROBE_B_EVERYTHING_ELSE_SECONDS} s"
            " (657 s billed − 237.155 s of load − 330.3 s of generation) INCLUDING its own ssh"
            f" wait, so ×{round(STAGE_LAUNCH_SECONDS / PROBE_B_EVERYTHING_ELSE_SECONDS, 4)} of a"
            " bound that is already generous is what this line buys"
        ),
        "boot_seconds_charged": BOOT_SECONDS,
        "boot_rule": (
            f"UNCHANGED from r1 — ≥ the worst boot this stack has measured ({WORST_MEASURED_BOOT} s,"
            f" lora-b) by ×{round(BOOT_SECONDS / WORST_MEASURED_BOOT, 4)}. What r2 moves is not the"
            " ceiling but the SPAN it is measured over: r1 derived it from the model-load window and"
            " applied it to create-elapsed, which also carries the ssh wait, the staging and the"
            " launch (Dv605). In r2 it is anchored on the runner's own `launched_at`"
        ),
        "boots_measured": json.loads(json.dumps(r1["money"]["arithmetic"]["boots_measured"])),
        "pre_generation_seconds": pre_generation,
        "pre_generation_rule": (
            f"ssh {SSH_DEADMAN_SECONDS:.0f} + stage/launch {STAGE_LAUNCH_SECONDS:.0f} + load"
            f" {BOOT_SECONDS:.0f} = {pre_generation:.0f} s, and it is ALSO rung 3's create-anchored"
            " backstop. The three spans are priced separately because r1 priced them as one and the"
            " one was named for the shortest of them"
        ),
        "overhead_seconds": OVERHEAD_SECONDS,
        "overhead_rule": (
            f"{OVERHEAD_SECONDS:.0f} s (r1: {R1_OVERHEAD_SECONDS:.0f}) — the scp of"
            f" {n['dev_base'] + n['dev_v2'] + n['shot']} answered rows and the pod log, the dev gate"
            " on the Mac, and the deletion with its three listings. It is SMALLER than r1's because"
            f" the ssh wait and the staging now have their own lines: the reduction of"
            f" {R1_OVERHEAD_SECONDS - OVERHEAD_SECONDS:.0f} s is covered by the"
            f" {SSH_DEADMAN_SECONDS + STAGE_LAUNCH_SECONDS:.0f} s those lines add, so nothing is"
            " counted twice and nothing is dropped"
        ),
        "total_seconds": round(total, 3),
        "hours": round(hours, 6),
        "worst_case_usd_at_the_price_ceiling": round(worst_usd, 6),
        "worst_case_usd_at_the_lora_b_price": round(hours * 0.53, 6),
        "cumulative": {
            "rule": r1["money"]["arithmetic"]["cumulative"]["rule"],
            "hard_stop_seconds": HARD_STOP_SECONDS,
            "hard_stop_hours": round(HARD_STOP_SECONDS / 3600, 4),
            "hard_stop_usd_at_the_price_ceiling": round(
                HARD_STOP_SECONDS / 3600 * PRICE_CEILING, 4
            ),
            "hard_stop_rule": (
                f"cumulative billed ≤ {HARD_STOP_SECONDS:.0f} s ="
                f" ${round(HARD_STOP_SECONDS / 3600 * PRICE_CEILING, 4)} at the ${PRICE_CEILING}/h"
                f" ceiling. It sits UNDER the ${CAP_USD:.2f} cap it defends, and it is the PLATFORM"
                " that enforces it — so it protects even a hung call no gate can see"
            ),
            "backstop_tolerance_seconds": BACKSTOP_TOLERANCE_SECONDS,
            "backstop_tolerance_rule": (
                "how far the `--terminate-after` stamp actually handed to `pod create` may sit"
                " BEYOND the one the hard stop computes. Only overshoot is bounded — a window"
                " rounded DOWN shortens itself and is always safe. It lived in the gate's source in"
                " r1 (Dv603) and the gate now READS it from here; a record without this field is a"
                " refusal, not a default"
            ),
            "session_ceiling_hours": round(CAP_USD / PRICE_CEILING, 6),
            "session_ceiling_seconds": round(CAP_USD / PRICE_CEILING * 3600, 1),
            "session_ceiling_rule": (
                "cap / price ceiling — the longest session the cap can pay for. It is ≥ the hard"
                " stop, so the platform-held stop is the binding one and the cap is never what"
                " discovers an overrun"
            ),
            "projection_gate": {
                **json.loads(
                    json.dumps(r1["money"]["arithmetic"]["cumulative"]["projection_gate"])
                ),
                # rung 4's own overhead line, and it is r2's. Copied whole from r1 it would have
                # charged the REPEALED 1 800 s against a hard stop r2 also lowered — the projection
                # runs on every poll of the watch, so the stale copy deletes a healthy pod at the
                # shot. The formula, the interval and «why every leg» did not move; these two did
                "overhead_seconds": OVERHEAD_SECONDS,
                "verdict": (
                    f"KILL if the projection exceeds ${CAP_USD:.2f} at the LIVE price, or exceeds"
                    f" the {HARD_STOP_SECONDS:.0f} s hard stop in seconds. The stricter binds"
                ),
                "overhead_rule": (
                    f"the SAME {OVERHEAD_SECONDS:.0f} s the money block charges, and it has to be:"
                    " rung 4 prices the attempt with it on every poll, so a second copy here is a"
                    " second budget. H6 asserts the two are one number"
                ),
            },
        },
        "recovery_arithmetic": {
            "one_dead_pod_at_rung_2_seconds": SSH_DEADMAN_SECONDS,
            "one_dead_pod_at_rung_2_usd": round(dead_pod_usd, 6),
            "then_the_full_worst_case_seconds": round(SSH_DEADMAN_SECONDS + total, 3),
            "then_the_full_worst_case_usd": round(dead_pod_usd + worst_usd, 6),
            "widest_dead_pod_that_still_fits_seconds": round(HARD_STOP_SECONDS - total, 3),
            "rule": (
                "the recovery clause must stay REACHABLE after one dead pod, and that is what fixes"
                f" rung 2 at {SSH_DEADMAN_SECONDS:.0f} s. One dead pod plus the full worst case is"
                f" {round(SSH_DEADMAN_SECONDS + total, 3)} s ≤ {HARD_STOP_SECONDS:.0f} and"
                f" ${round(dead_pod_usd + worst_usd, 4)} ≤ ${CAP_USD:.2f}, so ONE re-creation fits"
                " by the registered arithmetic. `--pre-create-check` computes both bounds before"
                " every create and the stricter binds"
            ),
            "why_not_600": (
                f"a {COUNTERFACTUAL_SSH_SECONDS:.0f} s rung 2 grows the worst case itself to"
                f" {round(counterfactual_total, 3)} s, so one dead pod plus that worst case is"
                f" {round(COUNTERFACTUAL_SSH_SECONDS + counterfactual_total, 3)} s —"
                f" PAST the {HARD_STOP_SECONDS:.0f} s hard stop. The dollars would still fit; the"
                " seconds do not, and the seconds are what the platform holds"
            ),
            "counterfactual_600_total_seconds": round(counterfactual_total, 3),
            "counterfactual_600_with_one_dead_pod_seconds": round(
                COUNTERFACTUAL_SSH_SECONDS + counterfactual_total, 3
            ),
            "re_creations_allowed": 1,
            "a_second_dead_pod": (
                "STOP. After a second dead pod nothing fits and the session closes with the attempt"
                " NOT spent — a THIRD pod under this registration is refused by the arithmetic and"
                " by this record. `--pre-create-check` READS `re_creations_allowed` and refuses the"
                " create itself, because at two CHEAP deaths the seconds would still fit and only"
                " the count says no"
            ),
        },
    }


CONTRACT_PRINTS = {
    "ssh_deadman_seconds": 500,
    "ssh_deadman_multiplier": 2.16,
    "ssh_worst_reading": 262.5,
    "one_dead_pod_usd": 0.1111,
    "stage_launch_seconds": 150,
    "stage_launch_multiplier": 1.68,
    "boot_seconds": 450,
    "boot_multiplier": 1.2748,
    "backstop_seconds": 1100,
    "dev_base_seconds": 1032.4,
    "dev_v2_seconds": 1548.6,
    "shot_seconds": 495.552,
    "generation_seconds": 3076.552,
    "overhead_seconds": 1300,
    "rows_copied_back": 464,
    "total_seconds": 5476.552,
    "total_hours": 1.5213,
    "worst_case_usd_at_the_ceiling": 1.2170,
    "worst_case_usd_at_the_lora_b_price": 0.8063,
    "cap_usd": 1.38,
    "hard_stop_seconds": 6100,
    "hard_stop_usd_at_the_ceiling": 1.3556,
    "session_ceiling_hours": 1.725,
    "session_ceiling_seconds": 6210,
    "recovery_seconds": 5976.552,
    "recovery_usd": 1.3281,
    "r1_pods_usd": 0.1178,
    "step_sum_usd": 1.4978,
}
"""Every figure `docs/PROMPT-pass1-fewshot-r2.md` prints, quoted so H6 has something to check
AGAINST. A re-derivation with nothing to disagree with is arithmetic, not a gate."""


def h6(sums: dict, pods: dict, r1_calls: dict) -> dict:
    """Every printed figure of the r2 contract, re-derived. A mismatch STOPS before any pod."""
    readings = sums["ssh_readings_2026_08_20"]
    worst_reading = max(readings.values())
    smaller_reading = min(readings.values())
    stop = sums["cumulative"]
    recovery = sums["recovery_arithmetic"]
    step_sum = pods["billed_usd"] + CAP_USD
    rows = [
        {
            "name": "ssh_deadman_over_the_worst_reading",
            "formula": (
                f"{SSH_DEADMAN_SECONDS:.0f} s ≥ the widest 2026-08-20 reading ({worst_reading} s),"
                " and both readings are LOWER bounds"
            ),
            "re_derived": SSH_DEADMAN_SECONDS,
            "registered": CONTRACT_PRINTS["ssh_worst_reading"],
            "mode": "at_least",
        },
        {
            "name": "ssh_deadman_multiplier",
            "formula": f"{SSH_DEADMAN_SECONDS:.0f} s / {smaller_reading} s",
            "re_derived": SSH_DEADMAN_SECONDS / smaller_reading,
            "registered": CONTRACT_PRINTS["ssh_deadman_multiplier"],
            "mode": "equals",
        },
        {
            "name": "one_dead_pod_at_rung_2_usd",
            "formula": f"{SSH_DEADMAN_SECONDS:.0f} s × ${PRICE_CEILING}/h / 3600",
            "re_derived": recovery["one_dead_pod_at_rung_2_usd"],
            "registered": CONTRACT_PRINTS["one_dead_pod_usd"],
            "mode": "equals",
        },
        {
            "name": "stage_launch_over_probe_bs_bound",
            "formula": (
                f"{STAGE_LAUNCH_SECONDS:.0f} s ≥ probe-b's whole «everything else»"
                f" ({PROBE_B_EVERYTHING_ELSE_SECONDS} s, ssh included)"
            ),
            "re_derived": STAGE_LAUNCH_SECONDS,
            "registered": PROBE_B_EVERYTHING_ELSE_SECONDS,
            "mode": "at_least",
        },
        {
            "name": "stage_launch_multiplier",
            "formula": f"{STAGE_LAUNCH_SECONDS:.0f} s / {PROBE_B_EVERYTHING_ELSE_SECONDS} s",
            "re_derived": STAGE_LAUNCH_SECONDS / PROBE_B_EVERYTHING_ELSE_SECONDS,
            "registered": CONTRACT_PRINTS["stage_launch_multiplier"],
            "mode": "equals",
        },
        {
            "name": "boot_ceiling_over_the_worst_measured_boot",
            "formula": f"{BOOT_SECONDS:.0f} s ≥ max(every boot this stack has measured)",
            "re_derived": BOOT_SECONDS,
            "registered": max(max(one) for one in sums["boots_measured"].values()),
            "mode": "at_least",
        },
        {
            "name": "boot_ceiling_multiplier",
            "formula": f"{BOOT_SECONDS:.0f} s / {WORST_MEASURED_BOOT} s",
            "re_derived": BOOT_SECONDS / WORST_MEASURED_BOOT,
            "registered": CONTRACT_PRINTS["boot_multiplier"],
            "mode": "equals",
        },
        {
            "name": "the_create_anchored_backstop",
            "formula": (
                f"ssh {SSH_DEADMAN_SECONDS:.0f} + stage/launch {STAGE_LAUNCH_SECONDS:.0f} + load"
                f" {BOOT_SECONDS:.0f}"
            ),
            "re_derived": sums["pre_generation_seconds"],
            "registered": CONTRACT_PRINTS["backstop_seconds"],
            "mode": "equals",
        },
        {
            "name": "the_live_packs_still_carry_r1s_call_counts",
            "formula": (
                "the dev pack's two legs and the shot pack's units, counted through r1's own"
                " producer, against the counts r1 registered"
            ),
            "re_derived": sums["calls"]["dev_base"]
            + sums["calls"]["dev_v2"]
            + sums["calls"]["shot"],
            "registered": sum(r1_calls[one] for one in ("dev_base", "dev_v2", "shot")),
            "mode": "equals",
        },
        {
            "name": "dev_base_seconds",
            "formula": f"{sums['calls']['dev_base']} calls × {BASE_SECONDS_PER_CALL} s",
            "re_derived": sums["leg_seconds"]["base"],
            "registered": CONTRACT_PRINTS["dev_base_seconds"],
            "mode": "equals",
        },
        {
            "name": "dev_v2_seconds",
            "formula": f"{sums['calls']['dev_v2']} calls × {sums['seconds_per_call']['v2']} s",
            "re_derived": sums["leg_seconds"]["v2"],
            "registered": CONTRACT_PRINTS["dev_v2_seconds"],
            "mode": "equals",
        },
        {
            "name": "shot_seconds",
            "formula": f"{sums['calls']['shot']} calls × {sums['seconds_per_call']['shot']} s",
            "re_derived": sums["leg_seconds"]["shot"],
            "registered": CONTRACT_PRINTS["shot_seconds"],
            "mode": "equals",
        },
        {
            "name": "generation_seconds",
            "formula": "dev base + dev v2 + shot — r1's three legs, unmoved",
            "re_derived": sums["generation_seconds"],
            "registered": CONTRACT_PRINTS["generation_seconds"],
            "mode": "equals",
        },
        {
            "name": "rows_copied_back",
            "formula": "dev base + dev v2 + shot units — what the 1 300 s overhead scp's",
            "re_derived": sums["rows_copied_back"],
            "registered": CONTRACT_PRINTS["rows_copied_back"],
            "mode": "equals",
        },
        {
            "name": "the_projection_gate_charges_the_registered_overhead",
            "formula": (
                "money.arithmetic.cumulative.projection_gate.overhead_seconds ="
                " money.arithmetic.overhead_seconds — rung 4 acts on the first and the budget is"
                " the second, so they are one number or they are two budgets"
            ),
            "re_derived": stop["projection_gate"]["overhead_seconds"],
            "registered": sums["overhead_seconds"],
            "mode": "equals",
        },
        {
            "name": "the_overhead_reduction_is_covered_by_the_new_lines",
            "formula": (
                f"ssh {SSH_DEADMAN_SECONDS:.0f} + stage/launch {STAGE_LAUNCH_SECONDS:.0f} ≥ r1's"
                f" overhead {R1_OVERHEAD_SECONDS:.0f} − r2's {OVERHEAD_SECONDS:.0f} — the two new"
                " lines pay for everything the overhead stopped covering, so nothing is double-counted"
            ),
            "re_derived": SSH_DEADMAN_SECONDS + STAGE_LAUNCH_SECONDS,
            "registered": R1_OVERHEAD_SECONDS - OVERHEAD_SECONDS,
            "mode": "at_least",
        },
        {
            "name": "total_seconds",
            "formula": "ssh + stage/launch + load + generation + overhead",
            "re_derived": sums["total_seconds"],
            "registered": CONTRACT_PRINTS["total_seconds"],
            "mode": "equals",
        },
        {
            "name": "total_hours",
            "formula": "total_seconds / 3600",
            "re_derived": sums["hours"],
            "registered": CONTRACT_PRINTS["total_hours"],
            "mode": "equals",
        },
        {
            "name": "worst_case_usd_at_the_ceiling",
            "formula": f"total_hours × ${PRICE_CEILING}/h",
            "re_derived": sums["worst_case_usd_at_the_price_ceiling"],
            "registered": CONTRACT_PRINTS["worst_case_usd_at_the_ceiling"],
            "mode": "equals",
        },
        {
            "name": "worst_case_usd_at_the_lora_b_price",
            "formula": "total_hours × $0.53/h",
            "re_derived": sums["worst_case_usd_at_the_lora_b_price"],
            "registered": CONTRACT_PRINTS["worst_case_usd_at_the_lora_b_price"],
            "mode": "equals",
        },
        {
            "name": "hard_stop_usd_at_the_ceiling",
            "formula": f"{HARD_STOP_SECONDS:.0f} s / 3600 × ${PRICE_CEILING}/h",
            "re_derived": stop["hard_stop_usd_at_the_price_ceiling"],
            "registered": CONTRACT_PRINTS["hard_stop_usd_at_the_ceiling"],
            "mode": "equals",
        },
        {
            "name": "the_hard_stop_is_under_the_cap",
            "formula": "hard stop at the ceiling < cap",
            "re_derived": stop["hard_stop_usd_at_the_price_ceiling"],
            "registered": CAP_USD,
            "mode": "below",
        },
        {
            "name": "the_worst_case_is_under_the_cap",
            "formula": "worst case at the ceiling < cap",
            "re_derived": sums["worst_case_usd_at_the_price_ceiling"],
            "registered": CAP_USD,
            "mode": "below",
        },
        {
            "name": "session_ceiling_hours",
            "formula": f"${CAP_USD:.2f} / ${PRICE_CEILING}/h",
            "re_derived": stop["session_ceiling_hours"],
            "registered": CONTRACT_PRINTS["session_ceiling_hours"],
            "mode": "equals",
        },
        {
            "name": "the_session_ceiling_is_not_the_binding_bound",
            "formula": "session ceiling in seconds ≥ the hard stop",
            "re_derived": stop["session_ceiling_seconds"],
            "registered": HARD_STOP_SECONDS,
            "mode": "at_least",
        },
        {
            "name": "recovery_seconds_fit_the_hard_stop",
            "formula": "one dead pod at rung 2 + the full worst case ≤ the hard stop",
            "re_derived": recovery["then_the_full_worst_case_seconds"],
            "registered": HARD_STOP_SECONDS,
            "mode": "below",
        },
        {
            "name": "recovery_usd_fits_the_cap",
            "formula": "one dead pod at the ceiling + the worst case at the ceiling ≤ cap",
            "re_derived": recovery["then_the_full_worst_case_usd"],
            "registered": CAP_USD,
            "mode": "below",
        },
        {
            "name": "a_600_s_rung_2_would_put_the_recovery_past_the_hard_stop",
            "formula": (
                f"at {COUNTERFACTUAL_SSH_SECONDS:.0f} s the worst case itself grows to"
                f" {recovery['counterfactual_600_total_seconds']} s, so one dead pod plus it is"
                " ≥ the hard stop — which is why rung 2 is 500 and not 600"
            ),
            "re_derived": recovery["counterfactual_600_with_one_dead_pod_seconds"],
            "registered": HARD_STOP_SECONDS,
            "mode": "at_least",
        },
        {
            "name": "r1_pods_usd",
            "formula": f"the closed pods of {R1_RUN_NAME}, on the gate's own clock",
            "re_derived": pods["billed_usd"],
            "registered": CONTRACT_PRINTS["r1_pods_usd"],
            "mode": "equals",
        },
        {
            "name": "the_step_sum_is_inside_the_step_budget",
            "formula": f"r1's pods + r2's cap ≤ ${STEP_BUDGET_USD:.2f}, the STEP budget the ruling kept",
            "re_derived": step_sum,
            "registered": STEP_BUDGET_USD,
            "mode": "below",
        },
        {
            "name": "step_sum_usd",
            "formula": "r1's pods + r2's cap",
            "re_derived": step_sum,
            "registered": CONTRACT_PRINTS["step_sum_usd"],
            "mode": "equals",
        },
    ]
    for row in rows:
        left, right = float(row["re_derived"]), float(row["registered"])
        if row["mode"] == "equals":
            row["agrees"] = math.isclose(left, right, rel_tol=0.01, abs_tol=1e-9)
        elif row["mode"] == "below":
            row["agrees"] = left < right
        elif row["mode"] == "at_least":
            row["agrees"] = left >= right
        else:
            raise SystemExit(f"{row['name']}: unknown H6 mode {row['mode']}")
    bad = [row for row in rows if not row["agrees"]]
    if bad:
        raise SystemExit(
            "H6 is the step-1 refusal gate and it does NOT agree: "
            + json.dumps(bad, ensure_ascii=False)
            + "\nRe-register the number, do not re-run this producer."
        )
    return {
        "rule": (
            "every number docs/PROMPT-pass1-fewshot-r2.md prints, re-derived from the formula the"
            " contract names for it. `equals` allows 1% — a rounding is not a finding; `below` and"
            " `at_least` check the DIRECTION of a margin, which is what a ceiling has instead of a"
            " value. Three of the rows check REASONS the contract gives rather than numbers it"
            " prints: why 500 and not 600, that the overhead cut is covered by the lines that"
            " replaced it, and what the 464 copied-back rows are"
        ),
        "reading": "every registered number re-derives",
        "mismatches": [],
        "rows": rows,
    }


def kill_clock(sums: dict, bar: dict) -> list[dict]:
    """r1's eight rungs. Two of them move, and only two."""
    return [
        {
            "rung": 1,
            "before": "the endpoint exists",
            "read": "costPerHr in the create response is the meter of record (Dv448)",
            "rule": (
                f"live price > ${PRICE_CEILING}/h at create → STOP, no endpoint. The backstop stamp"
                " is checked against the cumulative hard stop in the same command"
            ),
        },
        {
            "rung": 2,
            "before": "the model is loaded",
            "read": "money.arithmetic.ssh_rule — the spread this ceiling is, and the two readings",
            "rule": (
                f"ssh dead-man ≤ {SSH_DEADMAN_SECONDS:.0f} s of this pod's create-elapsed or KILL."
                " r1's 180 s was pass1-probe's reading of one night: it passed on 2026-08-18 and"
                " failed on BOTH pods of 2026-08-20, on the same card in the same datacenter"
                " (Dv602). The new ceiling is a spread, and one dead pod under it costs"
                f" ${sums['recovery_arithmetic']['one_dead_pod_at_rung_2_usd']:.4f}"
            ),
        },
        {
            "rung": 3,
            "before": "the first reply",
            "anchor": "launched_at",
            "read": (
                "the `launched_at` stamp the runbook writes into the pod's run directory the moment"
                " the runner starts, copied back by --watch and recorded in"
                " results/pass1_fewshot_r2_run.json"
            ),
            "rule": (
                f"launch → first reply ≤ {BOOT_SECONDS:.0f} s of the runner's OWN `launched_at` or"
                " KILL. r1 derived this ceiling from the model-LOAD window and measured it from"
                " create, and the two spans are not the same one: create-elapsed also carries the"
                " ssh wait, the staging and the launch, and the two spans this stack has MEASURED"
                " already exceed it together (Dv605). A run record without `launched_at` cannot"
                " report GO on this rung — a deadline that cannot be demonstrated has not been"
                " passed"
            ),
            "backstop_seconds": sums["pre_generation_seconds"],
            "backstop_rule": (
                f"and a create-anchored BACKSTOP beside it: first reply ≤"
                f" {sums['pre_generation_seconds']:.0f} s of create-elapsed or KILL — ssh"
                f" {SSH_DEADMAN_SECONDS:.0f} + stage/launch {STAGE_LAUNCH_SECONDS:.0f} + load"
                f" {BOOT_SECONDS:.0f}. It is what bounds the launch anchor: a stamp taken late"
                " cannot buy a window the registration never priced, and the backstop fires with no"
                " human in the path"
            ),
        },
        {
            "rung": 4,
            "before": "the run is allowed to continue past a call",
            "read": "money.arithmetic.cumulative.projection_gate — the formula and its terms",
            "rule": (
                f"projection gate every {PROJECTION_EVERY_CALLS} calls: the projected attempt total"
                " at MEASURED rates, with every leg still owed priced, must fit the cap at the LIVE"
                " price AND the cumulative hard stop, else KILL"
            ),
        },
        {
            "rung": 5,
            "before": "the executor may look away",
            "read": "held by scripts/gate_pass1_fewshot.py --watch, a BLOCKING loop",
            "rule": (
                f"liveness: {IDLE_DEADLINE_SECONDS:.0f} s with no new answered row and no new pod-log"
                " line → KILL. The deadline is measured from the LAST EVENT and never from create."
                " The executor does not poll by hand and does not leave the loop — lora-b lost 9 720"
                " s and an arm because every rung there watched the training log and none watched a"
                " pod that had stopped working"
            ),
        },
        {
            "rung": 6,
            "before": "anything",
            "read": "the `--terminate-after` stamp, read back and refused on overshoot",
            "rule": (
                f"cumulative hard stop {HARD_STOP_SECONDS:.0f} s, PLATFORM-held. Each pod's"
                " --terminate-after is its own create plus what the stop has left, and the overshoot"
                f" it forgives is the registered {BACKSTOP_TOLERANCE_SECONDS:.0f} s"
            ),
        },
        {
            "rung": 7,
            "before": "the shot",
            "read": "bars.dev_gate — both inequalities, paired on the same 200 rows",
            "rule": (
                f"dev gate: our_v2 − our_base ≥ {bar['our_delta_minimum']} AND agree_v2 −"
                f" agree_base ≥ {bar['agreement_delta_minimum']}. Both or NO shot. RED → delete,"
                " prove it by listing, the attempt is NOT spent, and the table returns to the"
                " team lead"
            ),
        },
        {
            "rung": 8,
            "before": "the verdict",
            "rule": (
                "the shot is 64 units into its OWN out-file, never a dev leg's — the shipped resume"
                " skips every id it already sees (Dv560). The attempt is SPENT at the first"
                " gold-row reply"
            ),
        },
    ]


def build() -> dict:
    r1 = sealed_r1()
    run = json.loads(summary.read_text_or_refuse(R1_RUN))
    blocks = copied(r1)
    sums = arithmetic(r1, run)
    pods = r1_pods(run)

    blocks["instruments"]["gate"] = {
        "script": "scripts/gate_pass1_fewshot.py",
        "sha256": sha(GATE),
        "moved_since_r1": True,
        "rule": (
            "the ONE instrument this re-registration amends, and the one pin that must move. r1's"
            f" record still carries its own sha ({r1['instruments']['gate']['sha256'][:16]}…) and is"
            " never edited; this checkout's gate reads THIS record and holds r2's rungs"
        ),
    }
    blocks["instruments"]["scorer_pass1_fewshot"] = {
        "script": "scripts/score_pass1_fewshot.py",
        "sha256": sha(SCORER),
        "rule": (
            "D2's judge, pinned. r1 named the bar and left the file that computes it unpinned"
            " (Dv606) — the same class as lora-b's Dv584, one contract later. It is the same script"
            " r1 committed at c7cbfd1 with its two record paths moved to r2's"
        ),
    }

    return {
        "phase": "pass1-fewshot-r2",
        "revision": "r2",
        "contract": "docs/PROMPT-pass1-fewshot-r2.md",
        "supersedes": {
            "record": R1_NAME,
            "sha256": sha(R1),
            "r1_closing_state": "closed at rung 2 twice, attempt NOT spent, recovery used",
            "r1_pods": pods,
            "rule": (
                "r1 is NEVER edited and never re-opened. It is committed, its recovery clause is"
                " spent, and no third pod may be created under it. r2 is a new registration of the"
                " SAME question, and the blocks the contract requires to be r1's are COPIED out of"
                " the file above rather than recomputed"
            ),
        },
        "authority": (
            "the operator's ruling of 2026-08-21 in the team-lead session, registered in"
            " docs/STATUS.md «Открытые решения» п. 3: re-register, and the STEP budget stays $1.50"
            " all-in — r1's pods already bought $0.117783 of it, so r2's cap is $1.38. The four"
            " amendments below are each derived from a finding of docs/reports/pass1-fewshot.md"
        ),
        "what_r2_changes": [
            "rung 2: the ssh dead-man 180 → 500 s of create-elapsed (Dv602)",
            "rung 3: the 450 s ceiling ANCHORED on the runner's launched_at, plus a create-anchored"
            " 1 100 s backstop (Dv605)",
            "instruments: scripts/score_pass1_fewshot.py pinned (Dv606) and"
            " BACKSTOP_TOLERANCE_SECONDS moved out of the gate's source into this record (Dv603)",
            "money: re-derived for the new allowances — cap $1.38, hard stop 6 100 s, overhead"
            " 1 300 s because ssh and staging now have their own lines",
        ],
        "what_r2_does_not_change": (
            "the question, the bars, the packs, the prompt, the holdout, the dev gate, the attempt"
            " and its multiplicity are r1's, copied out of the sealed record byte for byte. The"
            " producer REFUSES if any pin inside them no longer describes this checkout"
        ),
        **blocks,
        "money": {
            "cap_usd_all_in": CAP_USD,
            "cap_rule": (
                f"${CAP_USD:.2f} all-in for r2, frozen at the FIRST `pod create`. It is not a new"
                f" budget: the STEP's budget is ${STEP_BUDGET_USD:.2f} and r1's pods already bought"
                f" ${pods['billed_usd']:.6f} of it. Raising it is the operator's word BEFORE any"
                " endpoint exists, never after a reading"
            ),
            "step_sum": {
                "r1_pods_usd": pods["billed_usd"],
                "r1_pods_source": (
                    f"{R1_RUN_NAME} — {pods['pods']} closed pods,"
                    f" {pods['billed_seconds']} s on the gate's own clock"
                ),
                "r2_cap_usd": CAP_USD,
                "sum_usd": round(pods["billed_usd"] + CAP_USD, 6),
                "step_budget_usd": STEP_BUDGET_USD,
                "rule": (
                    "the report carries this line. The guard reads r2 against its OWN anchor and its"
                    f" own ${CAP_USD:.2f}; the step sum is what the ruling bounds and it is checked"
                    " by H6"
                ),
            },
            "guard": (
                "PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-fewshot-r2"
                f" --step-cap {CAP_USD:.2f} — the anchor is committed BEFORE the pod exists, and the"
                " reading is what the rungs that name one act on. r1's step ledger is closed and is"
                " never re-anchored"
            ),
            "meter": json.loads(json.dumps(r1["money"]["meter"])),
            "arithmetic": sums,
            "recovery": {
                "rule": (
                    "ONE pod re-creation, and only after a deletion PROVEN by listing. It happens"
                    " only if the guard READING plus the worst case remaining at MEASURED rates is"
                    f" ≤ ${CAP_USD:.2f} and inside the cumulative stop. Never two billing endpoints."
                    " `--pre-create-check` computes both bounds and refuses the create itself"
                ),
                "there_is_no_generation_checkpoint_to_lose": r1["money"]["recovery"][
                    "there_is_no_generation_checkpoint_to_lose"
                ],
                "arithmetic": sums["recovery_arithmetic"],
            },
            "reading": {
                "rule": r1["money"]["reading"]["rule"],
                "step": "pass1-fewshot-r2",
                "anchor_file": "results/spend_pass1_fewshot_r2.json",
            },
        },
        "kill_clock": kill_clock(sums, blocks["bars"]["dev_gate"]),
        "h6": h6(sums, pods, r1["money"]["arithmetic"]["calls"]),
        "run_record": "results/pass1_fewshot_r2_run.json",
        "frozen_when_the_pod_exists": [*r1["frozen_when_the_pod_exists"], OUT_NAME],
        "do_not": [
            *r1["do_not"],
            "no THIRD pod: the recovery arithmetic pays for ONE re-creation and refuses a second,"
            " and a second dead pod closes the session with the attempt NOT spent",
            "no edit to results/prereg_pass1_fewshot.json — r1 is sealed and superseded, never"
            " re-opened",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    record = build()
    record["producer"] = {
        "script": summary.rel(Path(__file__)),
        "sha256": sha(Path(__file__)),
        "borrowed": {
            one: sha(REPO_ROOT / one)
            for one in (
                "scripts/build_pass1_fewshot_packs.py",
                "scripts/window_summary_5c2.py",
                "scripts/write_pass1_fewshot_prereg.py",
            )
        },
    }
    out = args.outdir / OUT_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    out.write_text(payload, encoding="utf-8")

    sums = record["money"]["arithmetic"]
    stop = sums["cumulative"]
    recovery = sums["recovery_arithmetic"]
    print(f"wrote {OUT_NAME}  sha256 {packs.sha_text(payload)[:16]}…")
    print(
        f"  supersedes {R1_NAME} {record['supersedes']['sha256'][:16]}… — {record['supersedes']['r1_closing_state']}"
    )
    print(f"  H6: {len(record['h6']['rows'])} rows, {record['h6']['reading']}")
    print(
        f"  seconds: ssh {sums['ssh_seconds_charged']:.0f} + stage/launch"
        f" {sums['stage_launch_seconds_charged']:.0f} + load {sums['boot_seconds_charged']:.0f}"
        f" + generation {sums['generation_seconds']} + overhead {sums['overhead_seconds']:.0f}"
        f" = {sums['total_seconds']} = {sums['hours']:.4f} h"
    )
    print(
        f"  worst case ${sums['worst_case_usd_at_the_price_ceiling']:.4f} at ${PRICE_CEILING}/h"
        f" (${sums['worst_case_usd_at_the_lora_b_price']:.4f} at $0.53/h) against a cap of"
        f" ${CAP_USD:.2f}"
    )
    print(
        f"  hard stop {stop['hard_stop_seconds']:.0f} s ="
        f" ${stop['hard_stop_usd_at_the_price_ceiling']:.4f} < cap · session ceiling"
        f" {stop['session_ceiling_hours']:.3f} h = {stop['session_ceiling_seconds']:.0f} s"
    )
    print(
        f"  recovery: one dead pod {recovery['one_dead_pod_at_rung_2_seconds']:.0f} s"
        f" + the worst case = {recovery['then_the_full_worst_case_seconds']} s ≤"
        f" {stop['hard_stop_seconds']:.0f} and"
        f" ${recovery['then_the_full_worst_case_usd']:.4f} ≤ ${CAP_USD:.2f} — the widest dead pod"
        f" that still fits is {recovery['widest_dead_pod_that_still_fits_seconds']} s"
    )
    step = record["money"]["step_sum"]
    print(
        f"  STEP SUM: r1 pods ${step['r1_pods_usd']:.6f} + r2 cap ${step['r2_cap_usd']:.2f}"
        f" = ${step['sum_usd']:.6f} ≤ ${step['step_budget_usd']:.2f}"
    )
    rung3 = next(one for one in record["kill_clock"] if one["rung"] == 3)
    print(
        f"  rungs: 2 → {SSH_DEADMAN_SECONDS:.0f} s from create · 3 → {BOOT_SECONDS:.0f} s from"
        f" `{rung3['anchor']}` with a {rung3['backstop_seconds']:.0f} s create-anchored backstop"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
