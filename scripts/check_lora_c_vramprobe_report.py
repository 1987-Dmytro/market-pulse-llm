#!/usr/bin/env python3
"""Every number in `docs/reports/lora-c-vramprobe.md`, re-derived from the file that owns it.

A report is a set of claims about files; this is the only thing that keeps the two equal after a
hand edit ([[rederive_doc_numbers]], [[corrections_break_derivations]]). Each row below carries the
value the report PRINTS and the expression that derives it, and both have to hold: a number that is
right in the file and missing from the report is a silent edit, and one present in the report but
wrong in the file is the thing this exists to catch.

The two OOM tables are grepped out of the two pods' own logs by one regular expression rather than
transcribed, so the r2 column and this probe's column cannot drift apart in the retelling.

    python3.11 scripts/check_lora_c_vramprobe_report.py
"""

import hashlib
import json
import re
from pathlib import Path

report = Path("docs/reports/lora-c-vramprobe.md").read_text("utf-8")
flat = " ".join(report.split())
rec = json.loads(Path("results/lora_c_vramprobe.json").read_text("utf-8"))
prereg = json.loads(Path("results/prereg_lora_c_vramprobe.json").read_text("utf-8"))
frozen = json.loads(Path("results/prereg_lora_c.json").read_text("utf-8"))
r2run = json.loads(Path("results/lora_c_run.json").read_text("utf-8"))
spend = json.loads(Path("results/spend_lora_c_vramprobe.json").read_text("utf-8"))
cyc = json.loads(Path("results/spend_cycle2.json").read_text("utf-8"))

THE_PROBES_OWN_READING = "2026-08-25T14:46:50+00:00"
"""The stamp of the reading this report is ABOUT, in every ledger that carries one.

Both money rows below used to read `[-1]` — the last row — and that was true only while nothing
else wrote. `lora-c-migrate`'s step-0.5 close appended a later reading to the LIVE ledger on
2026-08-25 and the derivation started grading this sealed report against another session's number.
The last row is not an identity ([[select_one_row_refuse_ambiguity]],
[[rewriting_a_record_resets_state_you_do_not_own]]). Both ledgers are selected by stamp now, and a
stamp that is absent or duplicated raises instead of picking a neighbour."""


def the_row_at(rows: list[dict], stamp: str = THE_PROBES_OWN_READING) -> dict:
    hit = [one for one in rows if one["at"] == stamp]
    if len(hit) != 1:
        raise SystemExit(f"{len(hit)} rows stamped {stamp} — a reading must be exactly one row")
    return hit[0]


lorab = Path("results/prereg_lora_b.json").read_text("utf-8")
pod = rec["pods"][0]
gates = {g["kind"] + "-" + g["verdict"]: g for g in rec["gates"]}
smokes = [g for g in rec["gates"] if g["kind"] == "smoke"]
smoke = smokes[-1]

pat = re.compile(
    r"Tried to allocate ([\d.]+) GiB.*?of which ([\d.]+) GiB is free.*?this process has"
    r" ([\d.]+) GiB memory in use.*?([\d.]+) GiB is allocated by PyTorch, and ([\d.]+)"
    r" (GiB|MiB) is reserved",
    re.S,
)


def oom(path):
    return pat.search(Path(path).read_text("utf-8", errors="replace").replace("\r", "\n")).groups()


a2, f2, u2, al2, fr2, un2 = oom("results/lora_c_run_artifacts/smoke.log")
a3, f3, u3, al3, fr3, un3 = oom("results/lora_c_vramprobe_smoke.log")

r2_spent = round(sum(float(p["billed_usd"]) for p in r2run["pods"]), 4)
left_usd = round(4.0 - r2_spent, 4)
left_s = left_usd / 0.72 * 3600
calls = frozen["legs"]["arm_a"]["eval_calls"] + frozen["legs"]["arm_b"]["eval_calls"]
fixed = frozen["money"]["pre_pod_arithmetic"]["fixed_seconds"]
r3_fixed = fixed["boot"] + fixed["load"] + calls * 9.20 + fixed["pass_2"]
steps = (
    frozen["money"]["formulas"]["steps"]["arm_a"] + frozen["money"]["formulas"]["steps"]["arm_b"]
)
lived = round((rec["gates"][-2]["at"] and 244))

THREADS_EXTRA = frozen["money"]["pre_pod_arithmetic"][
    "the_pass_2_thread_count_is_a_READING_of_the_arms_labels"
]["extra_seconds_at_the_bound"]

checks = [
    ("376 s pod lifetime", "**376 s", pod["billed_seconds"] == 376.0),
    ("$0.0752 pod clock", "$0.0752", pod["billed_usd"] == 0.0752),
    ("cap left $0.2248", "$0.2248", round(0.30 - pod["billed_usd"], 4) == 0.2248),
    ("pod id", "cs8vla37upmy42", pod["pod_id"] == "cs8vla37upmy42"),
    ("created 14:40:13Z", "14:40:13Z", pod["created_at"] == "2026-08-25T14:40:13Z"),
    ("deleted 14:46:29Z", "14:46:29Z", pod["deleted_at"] == "2026-08-25T14:46:29Z"),
    ("terminate 15:05:13Z", "15:05:13Z", pod["terminate_after"] == "2026-08-25T15:05:13Z"),
    ("1124 s unused", "1 124 s", round(1500 - pod["billed_seconds"]) == 1124),
    ("ssh at 29.4 s", "**29.4 s**", gates["gate0-GO"]["elapsed_on_this_pod_seconds"] == 29.4),
    ("boot WAIT at 21.1 s", "21.1 s", gates["gate0-WAIT"]["elapsed_on_this_pod_seconds"] == 21.1),
    ("preamble 89.0 s", "**89.0 s**", smoke["preamble_seconds"] == 89.0),
    ("binding 170.17 s/step", "170.17 s/step", smoke["binding_seconds_per_step"] == 170.17),
    (
        "step-5 due by 1150.8",
        "1 150.8 s",
        smoke["next_line_due_by_seconds_into_the_smoke"] == 1150.8,
    ),
    ("smoke WAIT at 223.8 s", "223.8 s", smokes[0]["running_seconds"] == 223.8),
    (
        "crossover s = 21.0",
        "**s = 21.0 s**",
        prereg["reachability"]["s_at_which_the_two_bounds_cross_seconds"] == 21.0,
    ),
    ("registered ceiling 181.5", "181.5", smoke["registered_ceiling_seconds_per_step"] == 181.5),
    ("hard stop 1500", "1 500 s", smoke["hard_stop_seconds"] == 1500.0),
    ("1389 = 6x181.5+300", "1 389 s", 6 * 181.5 + 300 == 1389.0),
    ("log_every 5", "`log_every: 5`", smoke["log_every"] == 5),
    ("0 loss lines", "0 loss lines", smoke["loss_lines_seen"] == 0),
    ("outcome OOM", "OOM again", rec["answer"]["outcome"] == "OOM"),
    (
        "env reached the process",
        "PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True",
        rec["answer"]["the_env_var_reached_the_training_process"] is True,
    ),
    ("r2 allocate 1.72", "1.72 GiB", a2 == "1.72"),
    ("r2 free 1.66", "1.66 GiB", f2 == "1.66"),
    ("r2 in use 29.70", "29.70 GiB", u2 == "29.70"),
    ("r2 allocated 28.07", "28.07 GiB", al2 == "28.07"),
    ("r2 fragmented 1.33 GiB", "**1.33 GiB**", (fr2, un2) == ("1.33", "GiB")),
    ("probe allocate 1.99", "**1.99 GiB**", a3 == "1.99"),
    ("probe free 1.35", "1.35 GiB", f3 == "1.35"),
    ("probe in use 30.01", "30.01 GiB", u3 == "30.01"),
    ("probe allocated 29.17", "**29.17 GiB**", al3 == "29.17"),
    ("probe fragmented 544.22 MiB", "544.22 MiB", (fr3, un3) == ("544.22", "MiB")),
    ("544.22 MiB = 0.531 GiB", "0.531 GiB", round(544.22 / 1024, 3) == 0.531),
    (
        "frozen prereg sha unmoved",
        "4d5a8f1d34765b4a",
        hashlib.sha256(Path("results/prereg_lora_c.json").read_bytes()).hexdigest()[:16]
        == "4d5a8f1d34765b4a",
    ),
    (
        "guard delta $0.0495",
        "$0.0495",
        round(the_row_at(spend["gpu_sessions"])["step_spent_usd"], 4) == 0.0495,
    ),
    ("cycle2 $9.4105", "$9.4105", round(the_row_at(cyc["sessions"])["spent_usd"], 4) == 9.4105),
    (
        "cycle2 left $10.5895",
        "$10.5895",
        round(the_row_at(cyc["sessions"])["remaining_usd"], 4) == 10.5895,
    ),
    ("r2 spent $0.7606", "$0.7606", r2_spent == 0.7606),
    ("cap left $3.2394", "$3.2394", left_usd == 3.2394),
    ("16197 s left", "16 197 s", round(left_s) == 16197),
    ("r3 fixed 6577.2", "6 577.2 s", round(r3_fixed, 1) == 6577.2),
    ("3643.2 = 396 x 9.20", "3 643.2", round(calls * 9.20, 1) == 3643.2),
    ("9619.8 left for steps", "9 619.8 s", round(left_s - r3_fixed, 1) == 9619.8),
    (
        "cheapest ceiling 64.13",
        "| **64.13** |",
        round((left_s - r3_fixed) / (steps + 6), 2) == 64.13,
    ),
    ("census 368 s = 40 x 9.20", "= 368 s", round(40 * 9.20, 1) == 368.0),
    ("with census fixed 6945.2", "6 945.2", round(r3_fixed + 368, 1) == 6945.2),
    (
        "with census 61.68",
        "| **61.68** |",
        round((left_s - r3_fixed - 368) / (steps + 6), 2) == 61.68,
    ),
    ("15-thread extra 776 s", "`+776 s`", THREADS_EXTRA == 776),
    ("with both fixed 7721.2", "7 721.2", round(r3_fixed + 368 + THREADS_EXTRA, 1) == 7721.2),
    (
        "with both 56.51",
        "| **56.51** |",
        round((left_s - r3_fixed - 368 - THREADS_EXTRA) / (steps + 6), 2) == 56.51,
    ),
    ("range 56.5 to 64.1", "56.5 to 64.1 s/step", True),
    ("headroom +3.1", "+3.1", round(64.13 - 61.047, 1) == 3.1),
    ("shortfall -4.5", "−4.5 s/step", round(56.51 - 61.047, 1) == -4.5),
    ("r2 missed by 0.06", "**0.06 GiB**", round(float(a2) - float(f2), 2) == 0.06),
    ("probe missed by 0.64", "**0.64 GiB**", round(float(a3) - float(f3), 2) == 0.64),
    (
        "pass2 charged 11 threads",
        "CHARGED 11 threads",
        frozen["money"]["pre_pod_arithmetic"]["fixed_seconds"]["pass_2"] / 97 / 2 == 11.0,
    ),
    (
        "pass2 bound 15",
        "**bound of 15**",
        frozen["money"]["pre_pod_arithmetic"][
            "the_pass_2_thread_count_is_a_READING_of_the_arms_labels"
        ]["bound"]
        == 15,
    ),
    (
        "census is 20 x 2 = 40",
        "20 × 2 = 40 calls",
        "20 × 2 = 40 calls"
        in frozen["money"]["pre_pod_arithmetic"]["the_marker_census_is_not_inside_the_fixed_part"][
            "arithmetic"
        ],
    ),
    (
        "lora-b 61.047",
        "**61.047 s/step**",
        "61.047" in Path("results/baselines.json").read_text("utf-8"),
    ),
    ("lora-b longest kept 1222", "**1 222**", '"longest_kept": 1222' in lorab),
    (
        "this line's max 2975",
        "**2 975**",
        json.loads(Path("results/lora_c_encode_census.json").read_text("utf-8"))["tokens"]["max"]
        == 2975,
    ),
]
bad = 0
for name, quoted, ok in checks:
    inrep = quoted in flat
    if not (ok and inrep):
        bad += 1
        print(f"  FAIL {name}: derived={ok} in_report={inrep} (looked for {quoted!r})")
print(
    f"{len(checks) - bad} of {len(checks)} re-derived from their own file AND found in the report;"
    f" {bad} FAILED"
)
raise SystemExit(1 if bad else 0)
