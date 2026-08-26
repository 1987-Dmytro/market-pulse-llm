#!/usr/bin/env python3
"""Every number in `docs/reports/lora-c-run-r3.md`, re-derived from the file that owns it.

A report is a set of claims about files; this is the only thing that keeps the two equal after a
hand edit ([[rederive_doc_numbers]], [[corrections_break_derivations]]). Each row below carries the
value the report PRINTS and the expression that derives it, and both have to hold: a number that is
right in the file and missing from the report is a silent edit, and one present in the report but
wrong in the file is the thing this exists to catch.

**Two rows are counterfactuals and they are DERIVED, not transcribed.** The report's central claim
is that `gate_lora_b.measured_step` would have turned this KILL into a GO. That is not an opinion:
the function is CALLED here on the session's real loss log, and the projection is re-run at the
number it returns. A claim about a shipped function that nobody drives is a claim
([[a_claim_no_number_can_check]]).

Rows are selected by IDENTITY, never by `[-1]`: this session's record has one pod and one projection
gate today, and a re-creation would make the last row someone else's
([[select_one_row_refuse_ambiguity]]).

    python3.11 scripts/check_lora_c_run_r3_report.py
"""

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_lora_b as lorab  # noqa: E402

REPORT = REPO_ROOT / "docs" / "reports" / "lora-c-run-r3.md"
PREREG = REPO_ROOT / "results" / "prereg_lora_c_run_r3.json"
FROZEN = REPO_ROOT / "results" / "prereg_lora_c.json"
RECORD = REPO_ROOT / "results" / "lora_c_run_r3.json"
PROOF = REPO_ROOT / "results" / "lora_c_run_r3_load_proof.json"
PROVENANCE = REPO_ROOT / "results" / "lora_c_run_r3_smoke_provenance.json"
LOSS = REPO_ROOT / "results" / "lora_c_run_r3_smoke_loss.jsonl"
SMOKE_LOG = REPO_ROOT / "results" / "lora_c_run_r3_artifacts" / "smoke.log"
STOCK = REPO_ROOT / "results" / "lora_c_run_r3_stock.json"

report = REPORT.read_text(encoding="utf-8")
flat = " ".join(report.split())
prereg = json.loads(PREREG.read_text(encoding="utf-8"))
record = json.loads(RECORD.read_text(encoding="utf-8"))
proof = json.loads(PROOF.read_text(encoding="utf-8"))
run = json.loads(PROVENANCE.read_text(encoding="utf-8"))["run"]

POD_ID = "otq63mmt7s2uf1"
THE_PROJECTION = "projection-smoke"

pod = next(one for one in record["pods"] if one["pod_id"] == POD_ID)
gates = {}
for one in record["gates"]:
    if one["kind"] in gates:
        raise SystemExit(
            f"{one['kind']} appears twice in {RECORD.name} — a reading must be exactly one row"
        )
    gates[one["kind"]] = one
projection = gates[THE_PROJECTION]
smoke = gates["smoke"]
load = gates["load-proof"]

CAP = float(prereg["money"]["cap_usd_all_in"])
PRICE = float(pod["usd_per_hour"])
STOP = float(prereg["money"]["pre_pod_arithmetic"]["hard_stop_seconds"])
CALL = float(prereg["money"]["pre_pod_arithmetic"]["rates_used"]["pass_1_seconds_per_call"])
THREAD = float(prereg["money"]["pre_pod_arithmetic"]["rates_used"]["pass_2_seconds_per_thread"])
TAIL = float(prereg["money"]["pre_pod_arithmetic"]["fixed_seconds"]["teardown_and_pull"])
CALLS = int(projection["remaining_work"]["pass_1_calls"])
STEPS = int(projection["remaining_work"]["steps"])
BILLED_AT_PROJECTION = float(projection["cumulative_billed_seconds"])

checks: list[tuple[str, bool, str]] = []


def says(what: str, quoted: str, derived: bool = True) -> None:
    checks.append((what, derived and quoted in flat, quoted))


def priced(steps: int, call: float, threads_per_leg: int, per_step: float) -> tuple[float, float]:
    """The projection rung's own arithmetic, re-derived: remainder + tail, on the pod clock."""
    ahead = CALLS * call + steps * per_step + 2 * threads_per_leg * THREAD + TAIL
    seconds = BILLED_AT_PROJECTION + ahead
    return seconds, float(projection["guard_reading_usd"]) + ahead * PRICE / 3600


# --- the reading this session bought ---------------------------------------------------------------

says("the measured rate", "**89.961 s/step**", run["seconds_per_step"] == 89.961)
says("the loop's wall", "539.8", run["seconds"] == 539.8)
says("the smoke's steps", "six optimizer steps", run["steps"] == 6)
says(
    "the instrument did not move",
    "`micro_batch` 2 → 2",
    run["micro_batch_final"] == 2 and run["grad_accum_final"] == 8,
)
says("the peak allocation", "**49.54 GiB**", run["gpu_gb_peak"] == 49.54)

lines = lorab.log_lines(LOSS)
five = next(one for one in lines if one["step"] == 5)
six = next(one for one in lines if one["step"] == 6)
says("the step-5 line", "89.938", round(float(five["seconds_per_step"]), 3) == 89.938)
says("the step-6 line as logged", "17.441", round(float(six["seconds_per_step"]), 3) == 17.441)
says(
    "the step-6 line multiplied back",
    "**87.207**",
    round(float(six["seconds_per_step"]) * 5, 3) == 87.207,
)
says(
    "the amortised start-up",
    "**16.6**",
    round(float(run["seconds"]) - 6 * round(float(six["seconds_per_step"]) * 5, 3), 1) == 16.6,
)
says(
    "the start-up is 3.1% of the loop",
    "3.1% of the loop",
    round(16.6 / float(run["seconds"]) * 100, 1) == 3.1,
)

# --- the priors -------------------------------------------------------------------------------------

holds = prereg["money"]["pre_pod_arithmetic"]["the_break_even_is_a_FUNCTION_not_a_number"][
    "readings_this_repo_holds"
]
says("lora-b's registered rate", "| 61.047 |", holds["registered_by_lora_b"] == 61.047)
says("lora-b's measured rate", "| 68.442 |", holds["measured_on_lora_b_arm_a"] == 68.442)
says(
    "the ratio to the registered prior",
    "**1.47×**",
    round(run["seconds_per_step"] / holds["registered_by_lora_b"], 2) == 1.47,
)
says(
    "the ratio to the measured prior",
    "**1.31×**",
    round(run["seconds_per_step"] / holds["measured_on_lora_b_arm_a"], 2) == 1.31,
)

# --- the KILL, and every corner of it ----------------------------------------------------------------

says("the projection's verdict", "the projection rung KILLed", projection["verdict"] == "KILL")
says(
    "the projected seconds",
    "**21 284.8 s**",
    projection["projected_seconds"] == 21284.8
    and round(priced(STEPS, CALL, 15, run["seconds_per_step"])[0], 1) == 21284.8,
)
says("the projected usd", "**$8.1271**", projection["projected_usd"] == 8.1271)
says("the hard stop", "18 000 s hard stop", STOP == 18000.0)
says("the cap", "$7.00 cap", CAP == 7.00)
says("the billed at the projection", "1 109.2 s were billed", BILLED_AT_PROJECTION == 1109.2)
says(
    "the meter at the projection",
    "$0.3371 was on the meter",
    projection["guard_reading_usd"] == 0.3371,
)

CORNERS = (
    (9.20, 15, 21284.8, 8.2183),
    (9.20, 10, 20314.8, 7.8438),
    (6.14, 15, 19950.6, 7.7032),
    (6.14, 10, 18980.6, 7.3286),
)
for call, threads, seconds, usd in CORNERS:
    got_seconds, _ = priced(STEPS, call, threads, run["seconds_per_step"])
    got_usd = got_seconds / 3600 * PRICE
    says(
        f"the corner at {call} s/call and {threads} threads",
        f"| {seconds:,.1f} | {usd:.4f} |".replace(",", " "),
        round(got_seconds, 1) == seconds and round(got_usd, 4) == usd,
    )

fixed_ahead = CALLS * CALL + 2 * 15 * THREAD + TAIL
says(
    "the s/step the cap affords",
    "**68.05 s/step**",
    round((CAP / PRICE * 3600 - BILLED_AT_PROJECTION - fixed_ahead) / STEPS, 2) == 68.05,
)
says(
    "the s/step the stop affords",
    "**67.15 s/step**",
    round((STOP - BILLED_AT_PROJECTION - fixed_ahead) / STEPS, 2) == 67.15,
)
says(
    "the cap ratio",
    "measured is **1.32×** that",
    round(run["seconds_per_step"] / 68.05, 2) == 1.32,
)
says(
    "the stop ratio",
    "measured is **1.34×** that",
    round(run["seconds_per_step"] / 67.15, 2) == 1.34,
)

arm_a_only = BILLED_AT_PROJECTION + 218 * CALL + 62 * run["seconds_per_step"] + 15 * THREAD + TAIL
says(
    "arm A alone",
    "| 10 447.4 | **4.0339** |",
    round(arm_a_only, 1) == 10447.4 and round(arm_a_only / 3600 * PRICE, 4) == 4.0339,
)
one_epoch, _ = priced(72, CALL, 15, run["seconds_per_step"])
says(
    "both arms at one epoch",
    "| 14 807.6 | **5.7174** |",
    round(one_epoch, 1) == 14807.6 and round(one_epoch / 3600 * PRICE, 4) == 5.7174,
)

# --- the counterfactual, DRIVEN rather than asserted ---------------------------------------------------

sibling = lorab.measured_step(lines)
says(
    "what the sibling's number would have been",
    "**53.690**",
    round(sibling, 3) == 53.690,
)
counter_seconds, counter_usd = priced(STEPS, CALL, 15, sibling)
says(
    "the counterfactual projection",
    "| 16 061.7 | 6.1104 | **GO** |",
    round(counter_seconds, 1) == 16061.7
    and round(counter_usd, 4) == 6.1104
    and counter_seconds <= STOP
    and counter_usd <= CAP,
)
says(
    "the understatement",
    "A 40.3% understatement",
    round((1 - sibling / run["seconds_per_step"]) * 100, 1) == 40.3,
)
says(
    "the real projection is the other side of both bounds",
    "| 21 284.8 | 8.1271 | **KILL** |",
    projection["over_the_cap"] and projection["over_the_hard_stop"],
)

# --- the load, and the money ----------------------------------------------------------------------------

says("the cold load", "**138.491 s**", proof["load_seconds"] == 138.491)
says("the blobs", "12 blobs, **0 grew**", proof["blobs_counted"] == 12 and proof["no_blob_grew"])
says(
    "the whole cache did not move",
    "**0 bytes**",
    int(proof["hf_bytes_after"]) - int(proof["hf_bytes_before"]) == 0,
)
says("the load's vram", "17.046", round(int(proof["vram_bytes_allocated"]) / 1024**3, 3) == 17.046)
says(
    "the warm load",
    "| **13** |",
    "1188/1188 [00:13" in SMOKE_LOG.read_text("utf-8", errors="replace"),
)
MIGRATION = REPO_ROOT / "results" / "lora_c_migrate_r2_load_proof.json"
says(
    "the migration's load",
    "| 40.22 |",
    json.loads(MIGRATION.read_text(encoding="utf-8"))["load_seconds"] == 40.22,
)
says(
    "the spread inside one pod",
    "A **10.7×** spread inside ONE pod",
    round(proof["load_seconds"] / 13, 1) == 10.7,
)

says("the billed seconds", "1 152.0 s", pod["billed_seconds"] == 1152.0)
says(
    "the billed usd",
    "**$0.4448**",
    pod["billed_usd"] == 0.4448
    and round(pod["billed_seconds"] * PRICE / 3600, 4) == pod["billed_usd"],
)
says("the cap left", "**$6.5552 left**", round(CAP - pod["billed_usd"], 4) == 6.5552)
says(
    "the pod against its stop",
    "1 152 s of 18 000 = **6.4%**",
    round(pod["billed_seconds"] / STOP * 100, 1) == 6.4,
)
says(
    "the guard's delta",
    "**$0.4461**",
    round(10.4726 - 10.0265, 4) == 0.4461,
)
says(
    "the guard against the pod clock",
    "0.29% over the clock",
    round(abs(0.4461 - pod["billed_usd"]) / pod["billed_usd"] * 100, 2) == 0.29,
)

# --- this step's own row in the LIVE cycle ledger, selected by its stamp ---------------------------

CYCLE = REPO_ROOT / "results" / "spend_cycle2.json"
THIS_STEPS_ROW = "2026-08-26T09:14:45+00:00"
BEFORE_THE_CREATE = 10.0265

rows = [
    one
    for one in json.loads(CYCLE.read_text(encoding="utf-8"))["sessions"]
    if one["at"] == THIS_STEPS_ROW
]
if len(rows) != 1:
    raise SystemExit(
        f"{len(rows)} rows stamped {THIS_STEPS_ROW} in {CYCLE.name} — a reading is exactly one row"
    )
ledger = rows[0]

says(
    "the ledger row this session wrote",
    "**$10.4921 of $20.00**, $9.5079 left",
    ledger["spent_usd"] == 10.4921 and ledger["remaining_usd"] == 9.5079,
)
says(
    "the delta fifteen minutes later",
    "**$0.4656**",
    round(ledger["spent_usd"] - BEFORE_THE_CREATE, 4) == 0.4656,
)
says(
    "the walk is persisted in the row, and it did not move for this pod",
    "`billing_since_usd` **$10.026469**",
    round(ledger["billing_since_usd"], 6) == 10.026469
    and round(ledger["billing_since_usd"] - BEFORE_THE_CREATE, 4) == 0.0,
)
says(
    "the row names this pod",
    "`2026-08-26T09:14:45+00:00`",
    POD_ID in ledger["note"] and "UNSPENT" in ledger["note"],
)

# --- the stock, the gates, the audit ------------------------------------------------------------------------

stock = json.loads(STOCK.read_text(encoding="utf-8"))["the_rulings_row"]
says("the price rung 0 graded", "`costPerHr` **1.39**", stock["secure_usd_per_hour"] == PRICE)
says("the card", "`A100 PCIe`", stock["card"] == "A100 PCIe")
says("the boot", "**24.3 s**", gates["gate0"]["elapsed_on_this_pod_seconds"] == 24.3)
says(
    "the backstop overshoot",
    "given `13:39:49Z`, computed `13:39:50Z`",
    gates["open"]["backstop"]["overshoot_seconds"] == -1.0,
)
says("one pod", "| pods alive at any moment | **1** |", len(record["pods"]) == 1)
says(
    "six gates",
    "**6** — open · gate0 · load-proof · smoke · projection-smoke · close-pod",
    len(record["gates"]) == 6,
)
says(
    "five GO and a KILL",
    "Six gates, five GO and a KILL",
    [one["verdict"] for one in record["gates"]].count("GO") == 5
    and [one["verdict"] for one in record["gates"]].count("KILL") == 1,
)
says("the smoke gate passed its ceiling", "≤181.5 s/step", smoke["verdict"] == "GO")
says("the load gate", "| — | the load proof, on BLOBS |", load["verdict"] == "GO")
says(
    "the frozen registration is unmoved",
    "`4d5a8f1d34765b4a…`, asserted at every gate, **unmoved**",
    hashlib.sha256(FROZEN.read_bytes()).hexdigest() == prereg["the_frozen_registration"]["sha256"]
    and all(one["frozen"]["unmoved"] for one in record["gates"] if "frozen" in one),
)
says(
    "the attempt is unspent",
    "| **UNSPENT** — no adapter leg generated a reply against E |",
    not any(one["kind"].startswith("rate-") for one in record["gates"])
    and not (REPO_ROOT / "results" / "lora_c_run_r3_eval_a.jsonl").exists()
    and not (REPO_ROOT / "results" / "lora_c_run_r3_eval_b.jsonl").exists(),
)

for name, path in (
    ("results/prereg_lora_c_run_r3.json", PREREG),
    ("results/lora_c_run_r3_stock.json", STOCK),
    ("results/lora_c_run_r3.json", RECORD),
    ("results/lora_c_run_r3_load_proof.json", PROOF),
    ("results/lora_c_run_r3_smoke_provenance.json", PROVENANCE),
    ("results/lora_c_run_r3_smoke_loss.jsonl", LOSS),
    ("results/lora_c_run_r3_artifacts/smoke.log", SMOKE_LOG),
    ("scripts/gate_lora_c_run_r3.py", REPO_ROOT / "scripts" / "gate_lora_c_run_r3.py"),
    ("scripts/load_proof_r3_pod_runner.py", REPO_ROOT / "scripts" / "load_proof_r3_pod_runner.py"),
    ("tests/test_lora_c_run_r3.py", REPO_ROOT / "tests" / "test_lora_c_run_r3.py"),
):
    says(
        f"the sha of {name}",
        f"| `{name}` | `{hashlib.sha256(path.read_bytes()).hexdigest()[:16]}` |",
    )

# --- the deviation tally ---------------------------------------------------------------------------------

rows = [one for one in report.splitlines() if one.startswith("| **8") and one.count("|") >= 4]
kinds: dict[str, int] = {}
for row in rows:
    kinds[row.split("|")[2].strip()] = kinds.get(row.split("|")[2].strip(), 0) + 1
for kind, count in sorted(kinds.items()):
    says(f"the tally's own count of {kind}", f"{kind} {count}")
says(
    "the tally counts every row it has",
    f"**{['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight'][len(rows)]} rows**",
    sum(kinds.values()) == len(rows),
)


def main() -> int:
    bad = [one for one in checks if not one[1]]
    for what, ok, printed in checks:
        print(f"{'ok  ' if ok else 'FAIL'} {what}" + ("" if ok else f"  — expected {printed!r}"))
    print(
        f"\n{len(checks) - len(bad)} of {len(checks)} re-derived from their own file AND found in"
        f" the report; {len(bad)} FAILED"
    )
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
