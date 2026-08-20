#!/usr/bin/env python3
"""`results/prereg_pass1_fewshot.json` — the law of the ONE paid session, with H6 as its step-1 gate.

**Every threshold this contract has lives HERE and nowhere else.** `scripts/gate_pass1_fewshot.py`
reads each of them out of this file; nothing is typed twice, because a gate whose number lives in
two files goes green after one of them moves ([[preregistration_is_a_file_not_a_constant]]).

**H6 is a refusal gate, not a table.** Every figure `docs/PROMPT-pass1-fewshot.md` prints is
re-derived here from the formula the contract names for it, and a mismatch is a `SystemExit` at step
1 — before any pod exists. Two of the contract's numbers are re-derived DIFFERENTLY from the way its
parenthetical spells them and both are recorded as such:

- the boot ceiling. The contract writes «450 (worst 293 × 1.5)», and 293 s was the worst boot
  measured when that sentence was drafted. lora-b then measured **353 s** on the same card and the
  same volume. 450 is kept — it is the registered ceiling, and it still sits above the true worst —
  but its derivation is now «≥ the worst boot measured, ×1.2748», and H6 checks the direction of
  that margin rather than the arithmetic of a stale multiplier
  ([[a_named_revision_is_not_a_passing_one]]).
- the printed seconds. 64 × 7.743 = 495.552 and the contract prints 495.6; the total is 5 326.552
  against a printed 5 326.6. H6 re-derives the exact values and asserts the printed ones are their
  roundings, so the money block carries the arithmetic and the contract carries the reading.

**The dev gate's reachability is registered BEFORE the pod.** `our_v2 − our_base ≥ 10` over 49 rows
is impossible whenever the base already answers more than 39 of them correctly, and the base's dev
number is measured on the pod, with money running. So the branch is written down here: an
unreachable delta is a STOP with the attempt NOT spent, and it returns to the operator
([[an_absolute_bar_needs_a_reachability_state]]).

    PYTHONPATH=src python3.11 scripts/write_pass1_fewshot_prereg.py
    PYTHONPATH=src python3.11 scripts/write_pass1_fewshot_prereg.py --outdir /tmp/again   # the pair
"""

import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pass1_fewshot_packs as packs  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import prompts  # noqa: E402

OUT_NAME = "results/prereg_pass1_fewshot.json"

DEV_PACK = REPO_ROOT / packs.DEV_NAME
SHOT_PACK = REPO_ROOT / packs.SHOT_NAME
SEALED_PACK = REPO_ROOT / "results" / "pass1_probe_b_pack.json"
BASE_VERDICT = REPO_ROOT / "results" / "pass1_probe_b_verdict.json"
GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
HOLDOUT = REPO_ROOT / "results" / "pass1_holdout_100.json"
LORA_B = REPO_ROOT / "results" / "prereg_lora_b.json"

CAP_USD = 1.50
PRICE_CEILING = 0.80
BOOT_SECONDS = 450.0
BASE_SECONDS_PER_CALL = 5.162
V2_MULTIPLIER = 1.5
OVERHEAD_SECONDS = 1800.0
HARD_STOP_SECONDS = 6300.0
SSH_DEADMAN_SECONDS = 180.0
IDLE_DEADLINE_SECONDS = 600.0
PROJECTION_EVERY_CALLS = 20
OUR_DELTA_MINIMUM = 10
AGREEMENT_DELTA_MINIMUM = -5
GOLD_MINIMUM_AGREED = 12

MEASURED_BOOTS = {
    "reader-v5b / pass1-probe stack, inference": [146.8, 192.1, 237.155],
    "pass1-probe-b, the 4090 this contract prefers": [237.155],
    "lora-b, A6000 + the same volume": [267.0, 293.0, 353.0],
}
"""Every boot this stack has MEASURED, by the run that measured it. The ceiling is checked against
the maximum of all of them — charging by the max is the standing rule of this stack, whose boot has
never been a constant ([[the_fix_that_was_not_a_fix]])."""

CONTRACT_PRINTS = {
    "boot_seconds": 450,
    "dev_base_seconds": 1032.4,
    "dev_v2_seconds": 1548.6,
    "shot_seconds": 495.6,
    "overhead_seconds": 1800,
    "total_seconds": 5326.6,
    "total_hours": 1.4796,
    "worst_case_usd_at_the_ceiling": 1.1837,
    "hard_stop_seconds": 6300,
    "hard_stop_usd_at_the_ceiling": 1.40,
    "session_ceiling_hours": 1.875,
    "v2_seconds_per_call": 7.743,
}
"""Every figure `docs/PROMPT-pass1-fewshot.md` prints, quoted so H6 has something to check AGAINST.
A re-derivation with nothing to disagree with is arithmetic, not a gate."""


def counts() -> dict:
    dev = json.loads(summary.read_text_or_refuse(DEV_PACK))
    shot = json.loads(summary.read_text_or_refuse(SHOT_PACK))
    return {
        "dev_base": len(next(one for one in dev["legs"] if one["name"] == "base")["items"]),
        "dev_v2": len(next(one for one in dev["legs"] if one["name"] == "v2")["items"]),
        "shot": len(shot["legs"][0]["items"]),
        "our": dev["population"]["our_rows"],
    }


def arithmetic() -> dict:
    """Every money figure, computed from the calls the packs actually carry."""
    n = counts()
    v2_rate = round(BASE_SECONDS_PER_CALL * V2_MULTIPLIER, 6)
    legs = {
        "base": n["dev_base"] * BASE_SECONDS_PER_CALL,
        "v2": n["dev_v2"] * v2_rate,
        "shot": n["shot"] * v2_rate,
    }
    total = BOOT_SECONDS + sum(legs.values()) + OVERHEAD_SECONDS
    hours = total / 3600
    return {
        "boot_seconds_charged": BOOT_SECONDS,
        "boot_rule": (
            f"the registered ceiling, and rung 3's own threshold. It is ≥ the worst boot this stack"
            f" has measured ({max(max(one) for one in MEASURED_BOOTS.values())} s, lora-b) by"
            f" ×{round(BOOT_SECONDS / max(max(one) for one in MEASURED_BOOTS.values()), 4)}. The"
            " contract's parenthetical «worst 293 × 1.5» quotes the worst as it stood before lora-b"
            " measured 353 s; the CEILING has not moved and is still above the true worst"
        ),
        "boots_measured": MEASURED_BOOTS,
        "calls": n,
        "seconds_per_call": {
            "base": BASE_SECONDS_PER_CALL,
            "v2": v2_rate,
            "shot": v2_rate,
            "rule": (
                f"base is MEASURED — probe-b's 64 paid calls on an RTX 4090, mean {BASE_SECONDS_PER_CALL}"
                f" s. v2 is UNMEASURED and is registered as a BOUND: {V2_MULTIPLIER} × the measured"
                " base, for the longer prefill five labelled examples add. Rung 4 measures it at"
                f" call {PROJECTION_EVERY_CALLS} and every {PROJECTION_EVERY_CALLS} after that, and"
                " the projection then prices the rest at what the pod is actually doing"
            ),
            "sample": (
                "results/pass1_probe_b_rows.jsonl — 64 calls, one card, one boot. Named beside the"
                " number because a rate is a property of the sample it was measured on"
            ),
        },
        "leg_seconds": {name: round(value, 3) for name, value in legs.items()},
        "overhead_seconds": OVERHEAD_SECONDS,
        "overhead_rule": "0.5 h — staging, the scp's, the dev gate on the Mac, and the deletion",
        "total_seconds": round(total, 3),
        "hours": round(hours, 6),
        "worst_case_usd_at_the_price_ceiling": round(hours * PRICE_CEILING, 6),
        "worst_case_usd_at_the_lora_b_price": round(hours * 0.53, 6),
        "cumulative": {
            "rule": (
                "the hard stop and EVERY budget check count across ALL pods of this attempt, never"
                " per pod. `--terminate-after` on each pod is stamped at that pod's create plus the"
                " hard stop LESS what every closed pod already billed, so two pods cannot each be"
                " given a fresh window"
            ),
            "hard_stop_seconds": HARD_STOP_SECONDS,
            "hard_stop_hours": round(HARD_STOP_SECONDS / 3600, 4),
            "hard_stop_usd_at_the_price_ceiling": round(
                HARD_STOP_SECONDS / 3600 * PRICE_CEILING, 4
            ),
            "hard_stop_rule": (
                f"cumulative billed ≤ {HARD_STOP_SECONDS / 3600} h ="
                f" ${round(HARD_STOP_SECONDS / 3600 * PRICE_CEILING, 2)} at the ${PRICE_CEILING}/h"
                f" ceiling. It sits UNDER the ${CAP_USD:.2f} cap it defends, and it is the PLATFORM"
                " that enforces it — so it protects even a hung call no gate can see"
            ),
            "session_ceiling_hours": round(CAP_USD / PRICE_CEILING, 6),
            "session_ceiling_rule": "cap / price ceiling — the longest session the cap can pay for",
            "projection_gate": {
                "every": f"{PROJECTION_EVERY_CALLS} calls",
                "formula": (
                    "billed_by_closed_pods + elapsed_on_this_pod + Σ over every leg still owed of"
                    " (its remaining calls × its s/call) + overhead_seconds. A leg with a reply is"
                    " priced at its MEASURED rate — the larger of its mean and its last call; a leg"
                    " with none is priced at the LARGER of its registered rate and the worst rate"
                    " measured on this pod so far"
                ),
                "overhead_seconds": OVERHEAD_SECONDS,
                "verdict": (
                    f"KILL if the projection exceeds ${CAP_USD:.2f} at the LIVE price, or exceeds"
                    f" the {HARD_STOP_SECONDS:.0f} s hard stop in seconds. The stricter binds"
                ),
                "why_every_leg": (
                    "the shot's 64 calls are what makes the dev legs affordable at all. A projection"
                    " that priced only the running leg would open a run the cap closes"
                ),
            },
        },
    }


def h6(sums: dict) -> dict:
    """Every printed figure of the contract, re-derived. A mismatch STOPS before any pod."""
    n = sums["calls"]
    worst_boot = max(max(one) for one in MEASURED_BOOTS.values())
    rows = [
        {
            "name": "dev_base_seconds",
            "formula": f"{n['dev_base']} calls × {BASE_SECONDS_PER_CALL} s",
            "re_derived": sums["leg_seconds"]["base"],
            "registered": CONTRACT_PRINTS["dev_base_seconds"],
            "mode": "equals",
        },
        {
            "name": "v2_seconds_per_call",
            "formula": f"{V2_MULTIPLIER} × {BASE_SECONDS_PER_CALL} s (a BOUND, not a measurement)",
            "re_derived": sums["seconds_per_call"]["v2"],
            "registered": CONTRACT_PRINTS["v2_seconds_per_call"],
            "mode": "equals",
        },
        {
            "name": "dev_v2_seconds",
            "formula": f"{n['dev_v2']} calls × {sums['seconds_per_call']['v2']} s",
            "re_derived": sums["leg_seconds"]["v2"],
            "registered": CONTRACT_PRINTS["dev_v2_seconds"],
            "mode": "equals",
        },
        {
            "name": "shot_seconds",
            "formula": f"{n['shot']} calls × {sums['seconds_per_call']['v2']} s",
            "re_derived": sums["leg_seconds"]["shot"],
            "registered": CONTRACT_PRINTS["shot_seconds"],
            "mode": "rounds_to",
        },
        {
            "name": "total_seconds",
            "formula": "boot + dev base + dev v2 + shot + overhead",
            "re_derived": sums["total_seconds"],
            "registered": CONTRACT_PRINTS["total_seconds"],
            "mode": "rounds_to",
        },
        {
            "name": "total_hours",
            "formula": "total_seconds / 3600",
            "re_derived": round(sums["hours"], 4),
            "registered": CONTRACT_PRINTS["total_hours"],
            "mode": "equals",
        },
        {
            "name": "worst_case_usd_at_the_ceiling",
            "formula": f"total_hours × ${PRICE_CEILING}/h",
            "re_derived": round(sums["worst_case_usd_at_the_price_ceiling"], 4),
            "registered": CONTRACT_PRINTS["worst_case_usd_at_the_ceiling"],
            "mode": "equals",
        },
        {
            "name": "hard_stop_usd_at_the_ceiling",
            "formula": f"{HARD_STOP_SECONDS} s / 3600 × ${PRICE_CEILING}/h",
            "re_derived": sums["cumulative"]["hard_stop_usd_at_the_price_ceiling"],
            "registered": CONTRACT_PRINTS["hard_stop_usd_at_the_ceiling"],
            "mode": "equals",
        },
        {
            "name": "session_ceiling_hours",
            "formula": f"${CAP_USD:.2f} / ${PRICE_CEILING}/h",
            "re_derived": sums["cumulative"]["session_ceiling_hours"],
            "registered": CONTRACT_PRINTS["session_ceiling_hours"],
            "mode": "equals",
        },
        {
            "name": "the_hard_stop_is_under_the_cap",
            "formula": "hard stop at the ceiling < cap",
            "re_derived": sums["cumulative"]["hard_stop_usd_at_the_price_ceiling"],
            "registered": CAP_USD,
            "mode": "below",
        },
        {
            "name": "the_worst_case_is_under_the_cap",
            "formula": "worst case at the ceiling < cap",
            "re_derived": round(sums["worst_case_usd_at_the_price_ceiling"], 4),
            "registered": CAP_USD,
            "mode": "below",
        },
        {
            "name": "boot_ceiling_over_the_worst_measured_boot",
            "formula": f"{BOOT_SECONDS} s ≥ max(every boot this stack has measured) = {worst_boot} s",
            "re_derived": BOOT_SECONDS,
            "registered": worst_boot,
            "mode": "at_least",
        },
        {
            "name": "dev_rows",
            "formula": "all 49 «our» labels + 151 stratified from the other 601",
            "re_derived": n["dev_base"],
            "registered": 200,
            "mode": "equals",
        },
        {
            "name": "the_two_dev_legs_are_the_same_size",
            "formula": "paired on the same rows",
            "re_derived": n["dev_v2"],
            "registered": n["dev_base"],
            "mode": "equals",
        },
        {
            "name": "shot_units",
            "formula": "probe-b's eval pack, unchanged in identity and order",
            "re_derived": n["shot"],
            "registered": len(json.loads(summary.read_text_or_refuse(SEALED_PACK))["items"]),
            "mode": "equals",
        },
        {
            "name": "our_delta_is_reachable_at_the_bases_own_worst",
            "formula": f"49 «our» rows − {OUR_DELTA_MINIMUM} = the highest base that leaves it open",
            "re_derived": n["our"] - OUR_DELTA_MINIMUM,
            "registered": 39,
            "mode": "equals",
        },
    ]
    for row in rows:
        left, right = float(row["re_derived"]), float(row["registered"])
        if row["mode"] == "equals":
            row["agrees"] = math.isclose(left, right, rel_tol=0.01, abs_tol=1e-9)
        elif row["mode"] == "rounds_to":
            row["agrees"] = round(left, 1) == round(right, 1)
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
            "every number docs/PROMPT-pass1-fewshot.md prints, re-derived from the formula the"
            " contract names for it. `equals` allows 1% — a rounding is not a finding; `rounds_to`"
            " is for the two figures the contract prints rounded; `below` and `at_least` check the"
            " DIRECTION of a margin, which is what a ceiling has instead of a value"
        ),
        "reading": "every registered number re-derives",
        "mismatches": [],
        "rows": rows,
    }


def kill_clock() -> list[dict]:
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
            "rule": f"ssh dead-man ≤ {SSH_DEADMAN_SECONDS:.0f} s or KILL — pass1-probe's proven gate-0",
        },
        {
            "rung": 3,
            "before": "the first reply",
            "rule": (
                f"boot → first reply ≤ {BOOT_SECONDS:.0f} s or KILL. The ceiling is above every boot"
                " this stack has measured, the worst of them 353 s"
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
                " --terminate-after is its own create plus what the stop has left"
            ),
        },
        {
            "rung": 7,
            "before": "the shot",
            "read": "bars.dev_gate — both inequalities, paired on the same 200 rows",
            "rule": (
                f"dev gate: our_v2 − our_base ≥ {OUR_DELTA_MINIMUM} AND agree_v2 − agree_base ≥"
                f" {AGREEMENT_DELTA_MINIMUM}. Both or NO shot. RED → delete, prove it by listing,"
                " the attempt is NOT spent, and the table returns to the team lead"
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
    sums = arithmetic()
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    dev = json.loads(summary.read_text_or_refuse(DEV_PACK))
    shot = json.loads(summary.read_text_or_refuse(SHOT_PACK))
    base_verdict = json.loads(summary.read_text_or_refuse(BASE_VERDICT))
    lora_b = json.loads(summary.read_text_or_refuse(LORA_B))

    return {
        "phase": "pass1-fewshot",
        "contract": "docs/PROMPT-pass1-fewshot.md",
        "authority": (
            "the operator's rulings of 2026-08-20 registered in docs/STATUS.md «Открытые решения»"
            " п. 0 — the base stays Gemma-4-31B, the operator's word replaces sitting C, the goal is"
            " the analysis of docs/REFERENCE-signals-w1.md, and the team lead labels — plus the"
            " three answers of the joint step review: dev-200, the shot in the same session on a"
            " pre-registered gate, and the dev gate as written below"
        ),
        "what_this_line_is": (
            "line B (labels + LoRA) closed RED: the adapter learned the label marginal and not the"
            " decision. All four «категория» misses of the base are ONE error class — the comment"
            " MENTIONS a retailer or a brand inside a category habit, and the base classifies by the"
            " mention. This line fixes the DEFINITION in the prompt and shows the contrast with"
            " labelled neighbours. Nothing is trained"
        ),
        "attempt": (
            "ONE. No retry, no second prompt variant, and no tuning after any eval output is seen."
            " **The attempt is SPENT at the first GOLD-row reply generated** — not at pod create,"
            " not at a dev reply, and not at the dev gate, whose 200 rows are labelled comments"
            " outside both the sealed fourteen and the eval pack's sixty-four. A session that closes"
            " before any gold row is answered has NOT spent it and returns to the team lead, and"
            " every rung before rung 8 closes the session in exactly that state"
        ),
        "multiplicity": (
            "this is the THIRD shot at the same fourteen — the base (pass1-probe-b), arm A (lora-b)"
            " and now v2 — so the false-pass odds are about 3p and not p. Named here, in the"
            " registration, so the verdict is never read as a single shot. Accepted by the"
            " operator's «приступаем» of 2026-08-20"
        ),
        "return_to_the_operator": (
            "**A FAILED BAR GOES BACK TO THE OPERATOR, never to a prompt iteration.** A RED dev gate"
            " or a RED shot closes this line in-session: nothing is re-worded, nothing is re-run,"
            " and the dev table and the per-row fourteen go back for the next option of the menu"
            " (synthetic + LoRA, or rationale-supervised LoRA). A GREEN shot ships v2 as the pass-1"
            " prompt of the window run, which is the NEXT contract and is priced there"
        ),
        "bars": {
            "judge": {
                "entry_point": "market_pulse.scorer.reader_comment_agreement",
                "through": "scripts/score_pass1_probe.py::bar_p1",
                "collapse": {
                    "map": packs.json.loads(json.dumps({"категория_личное": "категория"})),
                    "symmetric": True,
                },
                "absent_or_refusal": "a DISAGREEMENT — silence about a row that was asked is a miss",
                "rule": (
                    "the same bytes probe-b and lora-b were scored with. A new equality loop would be"
                    " a second definition of the bar and is refused"
                ),
                "module_sha256": summary.sha256_of(
                    REPO_ROOT / "src" / "market_pulse" / "scorer.py"
                ),
            },
            "dev_gate": {
                "when": "rung 7, before the shot, on the Mac",
                "population": len(
                    next(one for one in dev["legs"] if one["name"] == "base")["items"]
                ),
                "our_rows": dev["population"]["our_rows"],
                "our_readings": list(packs.OUR),
                "our_delta_minimum": OUR_DELTA_MINIMUM,
                "agreement_delta_minimum": AGREEMENT_DELTA_MINIMUM,
                "rule": (
                    f"paired on the same {dev['population']['rows']} rows:"
                    f" our_v2 − our_base ≥ {OUR_DELTA_MINIMUM} (correct rows among the"
                    f" {dev['population']['our_rows']} категория_личное/молочный_бренд labels) AND"
                    f" agree_v2 − agree_base ≥ {AGREEMENT_DELTA_MINIMUM} (over all"
                    f" {dev['population']['rows']}). BOTH or no shot"
                ),
                "the_base_is_measured_here": (
                    "the base's dev numbers are MEASURED in this session on the same pod, never"
                    " assumed and never taken from another run. That is what «paired» means"
                ),
                "reachability": (
                    f"our_v2 ≤ {dev['population']['our_rows']}, so the delta is unreachable whenever"
                    f" our_base > {dev['population']['our_rows'] - OUR_DELTA_MINIMUM}. That is a"
                    " STOP, not a RED: the gate could not have been met by any v2 whatever, the"
                    " attempt is NOT spent, and the table goes to the operator with the reading"
                ),
            },
            "P1_per_comment_agreement": {
                "gating": True,
                "threshold": f"≥ {GOLD_MINIMUM_AGREED} of {len(gold['per_comment'])}",
                "minimum_agreed": GOLD_MINIMUM_AGREED,
                "n": len(gold["per_comment"]),
                "population": len(gold["per_comment"]),
                "loss_budget": {
                    "rows_that_may_be_lost": len(gold["per_comment"]) - GOLD_MINIMUM_AGREED,
                    "rule": (
                        "a refusal and an ABSENT row cost exactly what a disagreement costs. The"
                        " budget is registered before the run so the result cannot be re-read"
                        " against one nobody wrote"
                    ),
                },
                "comparison": "market_pulse.scorer.reader_comment_agreement",
                "collapse": {"map": {"категория_личное": "категория"}, "symmetric": True},
                "base_scored": base_verdict["bars"]["P1_per_comment_agreement"]["agreed"],
                "arm_a_scored": json.loads(
                    summary.read_text_or_refuse(REPO_ROOT / "results" / "lora_b_verdict.json")
                )["arms"]["a"]["bar"]["agreed"],
                "rule": (
                    "the sealed r2 gold, answered under probe-b's own 64-unit pack identity. ONE"
                    " attempt, SPENT at the first gold-row reply"
                ),
            },
            "census_50": {
                "rule": "OBSERVATION ONLY — no number here moves any gate",
                "reading": (
                    "the subject_type distribution v2 answers the eval pack's census rows with,"
                    " beside the base's and arm A's. Line B's whole finding was a census that moved"
                    " while the bar did not (None 25 → 9, не_наш_рынок 8 → 23)"
                ),
            },
        },
        "population": {
            "dev": {
                "pack": summary.rel(DEV_PACK),
                "sha256": summary.sha256_of(DEV_PACK),
                "rows": dev["population"]["rows"],
                "distribution": dev["population"]["distribution"],
                "legs": [
                    {
                        "name": one["name"],
                        "task": one["task"],
                        "out": one["out"],
                        "units": len(one["items"]),
                    }
                    for one in dev["legs"]
                ],
                "labels": dev["neighbours"]["pool"]["files"],
            },
            "shot": {
                "pack": summary.rel(SHOT_PACK),
                "sha256": summary.sha256_of(SHOT_PACK),
                "units": len(shot["legs"][0]["items"]),
                "out": shot["legs"][0]["out"],
                "sealed_source": shot["sealed_source"],
            },
            "gold": {
                "n": len(gold["per_comment"]),
                "record": summary.rel(GOLD),
                "revision": "r2",
                "sha256": summary.sha256_of(GOLD),
                "rows": lora_b["population"]["gold"]["rows"],
            },
            "holdout": {
                "record": summary.rel(HOLDOUT),
                "sha256": summary.sha256_of(HOLDOUT),
                "rule": (
                    "registered EVALUATION ONLY before this session. This line trains nothing, so"
                    " dev rows MAY overlap it and the overlap is published in both records"
                ),
            },
        },
        "instruments": {
            "prompt_sha256": {task: prompts.prompt_sha256(task) for task in sorted(prompts.PASS1)},
            "prompt_v1_did_not_move": (
                json.loads(summary.read_text_or_refuse(SEALED_PACK))["instruments"][
                    "prompt_sha256"
                ][prompts.PASS1_TASK]
                == prompts.prompt_sha256(prompts.PASS1_TASK)
            ),
            "v2_is_v1_plus_two_paragraphs": {
                "codebook_clause_sha256": packs.sha_text(prompts.PASS1_CODEBOOK_CLAUSE_V2),
                "examples_slot_sha256": packs.sha_text(prompts.PASS1_EXAMPLES_SLOT_V2),
                "rule": (
                    "PASS1_COMMENT_PROMPT_V2 == PASS1_COMMENT_PROMPT + the clause + the slot, and"
                    " nothing else. tests/test_pass1_prompt.py asserts it in both directions"
                ),
            },
            "parser": {
                "entry_point": "market_pulse.prompts.parse_pass1",
                "module": "src/market_pulse/prompts.py",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
            },
            "scorer": {
                "module": "src/market_pulse/scorer.py",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
            },
            "renderer": "market_pulse.prompts.pass1_messages_gm4",
            "transport": {
                "script": "scripts/pass1_fewshot_pod_runner.py",
                "sha256": summary.sha256_of(REPO_ROOT / "scripts" / "pass1_fewshot_pod_runner.py"),
                "rule": (
                    "it CALLS scripts/pass1_pod_runner.py, which calls the shipped v5 runner. One"
                    " model load serves every leg of a pack, and each leg is answered into its own"
                    " out-file"
                ),
            },
            "gate": {
                "script": "scripts/gate_pass1_fewshot.py",
                "sha256": summary.sha256_of(REPO_ROOT / "scripts" / "gate_pass1_fewshot.py"),
            },
            "packs": {
                "producer": "scripts/build_pass1_fewshot_packs.py",
                "sha256": summary.sha256_of(REPO_ROOT / "scripts" / "build_pass1_fewshot_packs.py"),
            },
        },
        "money": {
            "cap_usd_all_in": CAP_USD,
            "cap_rule": (
                f"${CAP_USD:.2f} all-in, frozen at the FIRST `pod create`. Raising it is the"
                " operator's word BEFORE any endpoint exists, never after a reading"
            ),
            "guard": (
                "PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-fewshot --step-cap"
                f" {CAP_USD:.2f} — the anchor is committed BEFORE the pod exists, and the reading is"
                " what the rungs that name one act on"
            ),
            "meter": {
                "price_ceiling_usd_per_hour": PRICE_CEILING,
                "card_preferred": (
                    "probe-b's class — RTX 4090 at $0.74/h, the card the 5.162 s/call sample was"
                    " measured on. An A6000 under the ceiling is allowed"
                ),
                "memory": (
                    "this line does NOT train, so lora-b's 48 GB constraint does not apply: probe-b"
                    " served this same base on a 24 GB 4090. That makes rung 1 a price gate against"
                    " a much wider market than lora-b faced"
                ),
                "datacenter": "EU-RO-1, pinned by network volume qw4nwleanc — the volume decides",
                "resource": (
                    "ONE rented pod, billed for every second it EXISTS — from `pod create` to `pod"
                    " delete`. `pod stop` does not stop the bill, so the run deletes and never stops"
                ),
                "price_rule": (
                    "**READ ON THE DAY.** `costPerHr` in the create response is the meter of record"
                    " and every figure here is recomputed from it by rung 4 before the run is"
                    " allowed to continue"
                ),
                "usd_per_second_at_the_ceiling": round(PRICE_CEILING / 3600, 9),
            },
            "arithmetic": sums,
            "recovery": {
                "rule": (
                    "ONE pod re-creation, and only after a deletion PROVEN by listing. It happens"
                    f" only if the guard READING plus the worst case remaining at MEASURED rates is"
                    f" ≤ ${CAP_USD:.2f} and inside the cumulative stop. Never two billing endpoints"
                ),
                "there_is_no_generation_checkpoint_to_lose": (
                    "every reply is flushed to its out-file as it lands and the shipped resume skips"
                    " every unit already answered, so a re-creation re-asks only what has no reply."
                    " That is the one thing this line has that lora-b did not: a KILL mid-leg costs"
                    " the boot, not the leg"
                ),
            },
            "reading": {
                "rule": "money is read from the GUARD, never from a ledger and never from prose (Dv33)",
                "step": "pass1-fewshot",
                "anchor_file": "results/spend_pass1_fewshot.json",
            },
        },
        "kill_clock": kill_clock(),
        "h6": h6(sums),
        "frozen_when_the_pod_exists": [
            "src/market_pulse/prompts.py",
            "src/market_pulse/scorer.py",
            "results/pass1_dev_pack.json",
            "results/pass1_probe_b_pack_v2.json",
            "results/pass1_probe_b_pack.json",
            "results/pass1_probe_b_verdict.json",
            "results/reader_gold_w1_r2.json",
            "results/pass1_holdout_100.json",
            "results/prereg_pass1_fewshot.json",
        ],
        "do_not": [
            "no training, no adapter, no second prompt variant, no tuning after any eval output",
            "never edit results/prereg_pass1_probe_b.json, results/pass1_probe_b_pack.json, the"
            " gold, the labels or the base verdict",
            "never touch the sealed fourteen before the dev gate says GO",
            "never leave --watch while a pod is billing",
            "never two billing endpoints",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    record = build()
    record["producer"] = {
        "script": summary.rel(Path(__file__)),
        "sha256": summary.sha256_of(Path(__file__)),
        "borrowed": {
            one: summary.sha256_of(REPO_ROOT / one)
            for one in ("scripts/build_pass1_fewshot_packs.py", "scripts/window_summary_5c2.py")
        },
    }
    out = args.outdir / OUT_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    out.write_text(payload, encoding="utf-8")

    sums = record["money"]["arithmetic"]
    print(f"wrote {OUT_NAME}  sha256 {packs.sha_text(payload)[:16]}…")
    print(f"  H6: {len(record['h6']['rows'])} rows, {record['h6']['reading']}")
    print(
        f"  seconds: boot {sums['boot_seconds_charged']} + base {sums['leg_seconds']['base']}"
        f" + v2 {sums['leg_seconds']['v2']} + shot {sums['leg_seconds']['shot']}"
        f" + overhead {sums['overhead_seconds']} = {sums['total_seconds']}"
        f" = {sums['hours']:.4f} h"
    )
    print(
        f"  worst case ${sums['worst_case_usd_at_the_price_ceiling']:.4f} at ${PRICE_CEILING}/h"
        f" (${sums['worst_case_usd_at_the_lora_b_price']:.4f} at $0.53/h) against a cap of"
        f" ${CAP_USD:.2f}"
    )
    stop = sums["cumulative"]
    print(
        f"  hard stop {stop['hard_stop_seconds']:.0f} s = {stop['hard_stop_hours']} h ="
        f" ${stop['hard_stop_usd_at_the_price_ceiling']:.2f} < cap · session ceiling"
        f" {stop['session_ceiling_hours']:.3f} h"
    )
    bar = record["bars"]["dev_gate"]
    print(
        f"  dev gate: our delta ≥ {bar['our_delta_minimum']} of {bar['our_rows']} AND agreement"
        f" delta ≥ {bar['agreement_delta_minimum']} over {bar['population']}"
    )
    print(
        f"  kill clock: {len(record['kill_clock'])} rungs, liveness is rung 5 and the script holds it"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
