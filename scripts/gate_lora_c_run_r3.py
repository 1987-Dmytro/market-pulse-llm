#!/usr/bin/env python3
"""`lora-c-run r3`'s rungs — a SIBLING of `scripts/gate_lora_c.py`, which is a sibling of lora-b's.

`docs/PROMPT-lora-c-run-r3.md` D1 registers eight rungs plus a named load proof, against the
POST-FREEZE money record `results/prereg_lora_c_run_r3.json`. The frozen `results/prereg_lora_c.json`
holds the bars, the legs and the step counts and is READ; the cap, the rates and the hard stop of
THIS session live beside it, because a registration written into after its freeze is not one.

**What is CALLED.** `gate_lora_c` owns rung 0's price-and-card refusal, rung 1's ssh dead-man, rung
2's silence clock, rung 3's realised-rate arithmetic, rung 5's projection, the plan table, the
cumulative clock, the `--terminate-after` backstop, the run state and the gate append. All of it is
reached through the module object with `PHASE`/`PREREG`/`RECORD` re-bound for the length of one call
by :func:`the_gate_reads_r3` — a module-level constant cannot be told anything by a parameter
([[a_self_pinning_producer_cannot_grow_a_parameter]]). lora-c's and the migration's own gates keep
reading their own files: the swap is undone in a `finally`.

**Five things are written here, and every one of them is a defect the sibling would have carried
onto a billing pod.** None of them is fixed in `scripts/gate_lora_c_migrate_r2.py` or
`scripts/load_proof_pod_runner.py`: those two shas are pinned by the SEALED
`docs/reports/lora-c-migrate-r2.md` through a checker the suite drives as a command, so an edit
there would make a closed report stop re-deriving ([[the_gates_evidence_outlived_its_artifact]]).

- **the load proof, on BLOBS.** The migration's rung 5 graded `du -sb /workspace/hf` either side of
  the load and KILLed on 40 bytes of HuggingFace bookkeeping — a `refs/main` write and four
  zero-byte absence markers — with 0 of 12 blobs touched. The blobs are the weights; the invariant
  worth registering is that no blob grows ([[an_invariant_on_the_container_not_the_payload]]).
- **the smoke, graded on the PROVENANCE rate.** `log_every: 5` and `--max-steps 6` write TWO loss
  lines, not six, so the sibling's smoke gate WAITs for ever on a surviving smoke (Dv813); and each
  line's `seconds_per_step` divides by `log_every` rather than by the window it covers, so the
  step-6 line reads about a fifth of the truth (Dv814). `provenance.json::run.seconds_per_step` is
  the whole loop's wall over its steps and it is the only quotable one. Both are printed, neither is
  averaged into the other.
- **the OOM, READ rather than asserted.** `train_qlora.train` catches `OutOfMemoryError` and, while
  `micro_batch > 1`, halves it, doubles `grad_accum` and carries on — so an OOM at the registered
  `micro_batch_size: 2` need not crash, it silently makes the arm a different instrument from the
  one the registration prices. `run.micro_batch_final` is the reading; a caller's flag is not
  ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]]).
- **the rate rung on an EVAL leg, charging the MEASURED step.** The sibling's `--leg` admits only
  the two base legs, which this session does not buy, and its remaining steps are charged at the
  registered 61.047 floor even after the smoke has measured a real one
  ([[projected_rate_versus_measured_rate]]).
- **the projection's teardown TAIL.** `gate_lora_c.projection` prices the remainder in calls, steps
  and threads. Pulling nine artifacts and proving a deletion is billed work in none of those units,
  and a session projected to exactly the cap has no room left to end.

    PYTHONPATH=src python3.11 scripts/gate_lora_c_run_r3.py --read-back
    PYTHONPATH=src python3.11 scripts/gate_lora_c_run_r3.py --pre-create-check
    PYTHONPATH=src python3.11 scripts/gate_lora_c_run_r3.py --open --pod-id <id> \\
        --created-at <ISO> --usd-per-hour <costPerHr> --card '<displayName>' \\
        --terminate-after '<the stamp given to pod create>'
    PYTHONPATH=src python3.11 scripts/gate_lora_c_run_r3.py --gate0 [--ssh-ok]
    PYTHONPATH=src python3.11 scripts/gate_lora_c_run_r3.py --liveness --last-event <ISO>
    PYTHONPATH=src python3.11 scripts/gate_lora_c_run_r3.py --load-proof --started-at <ISO> \\
        --proof results/lora_c_run_r3_load_proof.json
    PYTHONPATH=src python3.11 scripts/gate_lora_c_run_r3.py --smoke \\
        --provenance results/lora_c_run_r3_smoke_provenance.json --loss <loss.jsonl>
    PYTHONPATH=src python3.11 scripts/gate_lora_c_run_r3.py --rate --leg eval_a \\
        --replies <out.jsonl> --started-at <ISO>
    PYTHONPATH=src python3.11 scripts/gate_lora_c_run_r3.py --projection --after smoke \\
        --reading <USD> [--pass-2-threads-realised N]
    PYTHONPATH=src python3.11 scripts/gate_lora_c_run_r3.py --close-pod --deleted-at <ISO> \\
        --outcome '<why>'
"""

import argparse
import contextlib
import copy
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_lora_c as sibling  # noqa: E402
import gate_lora_c_migrate_r2 as migration  # noqa: E402

PHASE = "lora-c-run-r3"
PREREG = REPO_ROOT / "results" / "prereg_lora_c_run_r3.json"
RECORD = REPO_ROOT / "results" / "lora_c_run_r3.json"
FROZEN = REPO_ROOT / "results" / "prereg_lora_c.json"
CONFIG = REPO_ROOT / "config" / "qlora.yaml"

GO, KILL, WAIT = sibling.GO, sibling.KILL, sibling.WAIT

rel = sibling.rel
stamp = sibling.stamp
elapsed_since = sibling.elapsed_since
first_number = sibling.first_number
rung = sibling.rung
log_lines = sibling.log_lines
show = sibling.show
rate_of = sibling.rate_of
live_pod = sibling.sibling.live_pod

the_cap_affords_the_hard_stop = migration.the_cap_affords_the_hard_stop
"""The migration's INEQUALITY helper, CALLED. It reads `money.pre_pod_arithmetic.hard_stop_seconds`,
its formula string and `money.cap_usd_all_in` — all three of which this record holds — so nothing
about it is specific to that step ([[a_published_ratio_is_not_the_gates]])."""


@contextlib.contextmanager
def the_gate_reads_r3():
    """`gate_lora_c`'s file constants point at this session, for the length of one call."""
    was = (sibling.PHASE, sibling.PREREG, sibling.RECORD)
    sibling.PHASE, sibling.PREREG, sibling.RECORD = PHASE, PREREG, RECORD
    try:
        yield
    finally:
        sibling.PHASE, sibling.PREREG, sibling.RECORD = was


def registration() -> dict:
    with the_gate_reads_r3():
        return sibling.registration()


def frozen() -> dict:
    return json.loads(FROZEN.read_text(encoding="utf-8"))


def the_frozen_registration_is_unmoved(record: dict) -> dict:
    """The FROZEN registration, hashed and compared to the sha this record was built against.

    Here it is not «the attempt this step does not spend» — this session SPENDS it. What the check
    holds is that the bars, the legs and the step counts every gate reads are the ones a create
    froze on 2026-08-24, and that no hand touched them between the freeze and the money
    ([[a_claim_no_number_can_check]]).
    """
    want = record["the_frozen_registration"]["sha256"]
    got = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
    if got != want:
        raise SystemExit(
            f"{rel(FROZEN)} hashes to {got}, and this registration was built against {want}."
            " The frozen registration is this session's first DO-NOT. STOP."
        )
    return {"the_frozen_registration": rel(FROZEN), "sha256": got, "unmoved": True}


# --- the read-back, the contract's refusal gate ---------------------------------------------------


def rows_of(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def read_back(record: dict) -> dict:
    """Every number the contract asks to be re-derived before step 1, each from the file that owns it.

    A read-back typed out of the contract is the contract quoting itself. Each row below carries the
    value AND the file it came out of, and a mismatch with the registered number is a FINDING that
    stops the session ([[rederive_doc_numbers]], [[a_count_in_prose_is_not_the_enumeration]]).
    """
    import yaml

    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    training = config["training"]
    micro, accum, epochs = (
        int(training["micro_batch_size"]),
        int(training["grad_accum"]),
        int(training["epochs"]),
    )
    seal = frozen()
    census = {
        "arm_a": json.loads(
            (REPO_ROOT / "results" / "lora_c_encode_census.json").read_text(encoding="utf-8")
        ),
        "arm_b": json.loads(
            (REPO_ROOT / "results" / "lora_c_encode_census_arm_b.json").read_text(encoding="utf-8")
        ),
    }
    pack = json.loads((REPO_ROOT / "results" / "lora_c_eval_pack.json").read_text(encoding="utf-8"))
    arithmetic = record["money"]["pre_pod_arithmetic"]

    def steps(rows: int) -> int:
        return (-(-rows // micro) // accum) * epochs

    def planned(rows: int) -> int:
        return -(-rows // (micro * accum)) * epochs

    rows = {arm: int(census[arm]["rows"]) for arm in ("arm_a", "arm_b")}
    bases = {
        name: rows_of(REPO_ROOT / record["legs"][name]["out_file"])
        for name in ("base_v2", "base_v3")
    }
    lines = [
        (
            "optimizer steps",
            f"arm A {steps(rows['arm_a'])} / arm B {steps(rows['arm_b'])}"
            f" (planned {planned(rows['arm_a'])}/{planned(rows['arm_b'])})",
            steps(rows["arm_a"]) == record["money"]["formulas"]["steps"]["arm_a"] == 62
            and steps(rows["arm_b"]) == record["money"]["formulas"]["steps"]["arm_b"] == 82
            and planned(rows["arm_a"]) == 64
            and planned(rows["arm_b"]) == 84,
            f"{rel(CONFIG)} micro {micro} × accum {accum} × epochs {epochs}, over the census rows",
        ),
        (
            "training rows",
            f"{rows['arm_a']} / {rows['arm_b']}",
            rows == {"arm_a": 506, "arm_b": 666}
            and rows_of(REPO_ROOT / record["legs"]["arm_a"]["train_file"]) == 506
            and rows_of(REPO_ROOT / record["legs"]["arm_b"]["train_file"]) == 666,
            "results/lora_c_encode_census*.json, and the SFT files counted line by line",
        ),
        (
            "eval set E per leg",
            f"{[leg['n'] for leg in pack['legs']]}",
            all(int(leg["n"]) == 198 for leg in pack["legs"])
            and seal["legs"]["arm_a"]["eval_calls"] == 198
            and seal["legs"]["arm_b"]["eval_calls"] == 198,
            "results/lora_c_eval_pack.json::legs[].n, against the frozen registration",
        ),
        (
            "the base legs are BOUGHT and are not re-bought",
            f"v2 {bases['base_v2']} rows on disk · v3 {bases['base_v3']} rows · charged calls"
            f" {record['legs']['base_v2']['eval_calls']}/{record['legs']['base_v3']['eval_calls']}",
            bases["base_v2"] > 0
            and bases["base_v3"] > 0
            and record["legs"]["base_v2"]["eval_calls"] == 0
            and record["legs"]["base_v3"]["eval_calls"] == 0,
            "results/lora_c_base_v2.jsonl and _v3.jsonl, bought by r2",
        ),
        (
            "pass-2 threads charged, per leg",
            f"{sibling.plan(record)['eval_a']['pass_2_threads']} (the BOUND, not a count)",
            sibling.plan(record)["eval_a"]["pass_2_threads"] == 15
            and sibling.plan(record)["eval_b"]["pass_2_threads"] == 15,
            "derived from fixed_seconds.pass_2 ÷ 97 s/thread ÷ 2 legs",
        ),
        (
            "the encode ceiling and the widest row",
            f"{census['arm_b']['max_seq_len']} / {census['arm_b']['tokens']['max']}"
            f" (headroom {census['arm_b']['headroom']})",
            int(census["arm_b"]["max_seq_len"]) == int(training["max_seq_len"]) == 3072
            and int(census["arm_b"]["tokens"]["max"]) == 2975
            and not census["arm_a"]["refused"]
            and not census["arm_b"]["refused"],
            f"{rel(CONFIG)}::training.max_seq_len, against both encode censuses",
        ),
        (
            "v3's charged s/call",
            f"{arithmetic['rates_used']['pass_1_seconds_per_call']}",
            float(arithmetic["rates_used"]["pass_1_seconds_per_call"]) == 9.20,
            "ruling (п) — never 6.14",
        ),
        (
            "the cap",
            f"${record['money']['cap_usd_all_in']:.2f} all-in, hard stop"
            f" {arithmetic['hard_stop_seconds']:.0f} s",
            float(record["money"]["cap_usd_all_in"]) == 7.00
            and float(arithmetic["hard_stop_seconds"]) == 18000.0
            and first_number(rung(record, 5)["rule"]) == 7.00,
            "ruling (т), and rung 5's own rule string",
        ),
        (
            "the bars, per ruling (к) — all three or RED, one attempt per arm",
            "holdout ≥ 64 of 100 (reachable 98) AND bar 1 = 5/5 AND bar 3 = 0;"
            " base v3 takes no bar",
            seal["bars"]["P1_holdout_agreement"]["minimum_agreed"] == 64
            and seal["bars"]["P1_holdout_agreement"]["gating"]
            and seal["bars"]["P2_bar_1_flagships"]["threshold"] == "5 of 5 cases"
            and seal["bars"]["P2_bar_3_noise"]["gating"]
            and seal["legs"]["base_v3"]["bar"] is None,
            "results/prereg_lora_c.json::bars — FROZEN, read and never restated",
        ),
    ]
    findings = [one[0] for one in lines if not one[2]]
    return {
        "read_back": [
            {"what": what, "reading": reading, "holds": holds, "from": source}
            for what, reading, holds, source in lines
        ],
        "findings": findings,
        "verdict": "GO" if not findings else "KILL",
        "next_step": (
            "every registered number re-derives — run --pre-create-check"
            if not findings
            else "a re-derivation disagrees with a registered number. That is a FINDING: STOP and"
            " report it to the team lead before any create"
        ),
    }


# --- the load proof, on BLOBS ---------------------------------------------------------------------


def grown_blobs(before: dict, after: dict) -> list[dict]:
    """Every blob that is new or larger after the load. Shrinks are reported by the caller, not here.

    A re-download writes a blob. Nothing else in a HuggingFace cache read does — the ref file and the
    `.no_exist` markers are bookkeeping and they are exactly what made the migration's rung 5 refuse
    a healthy load ([[an_invariant_on_the_container_not_the_payload]]).
    """
    return [
        {
            "blob": name,
            "bytes_before": before.get(name),
            "bytes_after": size,
            "grew_by": size - before.get(name, 0),
        }
        for name, size in sorted(after.items())
        if size > before.get(name, 0)
    ]


def load_proof_gate(
    record: dict,
    state: dict,
    started_at: str,
    proof: Path,
    now: datetime | None = None,
) -> dict:
    """The load, its seconds, and the proof that it read the weights off the volume.

    Three conditions and the gate says which one fired: the deadline, the pinned revision, and the
    blob invariant. The whole-cache byte delta is REPORTED beside them and grades nothing.
    """
    entry = record["the_load_proof"]
    threshold = first_number(entry["rule"])
    running = elapsed_since(started_at, now)
    seen = json.loads(proof.read_text(encoding="utf-8")) if proof.exists() else None

    if seen is None:
        return {
            "the_load_proof": True,
            "started_at": started_at,
            "running_seconds": round(running, 1),
            "threshold_seconds": threshold,
            "seconds_left": round(threshold - running, 1),
            "proof": rel(proof),
            "proof_exists": False,
            "verdict": "KILL" if running >= threshold else "WAIT",
            "rule": entry["rule"],
            "next_step": (
                "keep copying the proof file back; the load is still running"
                if running < threshold
                else "KILL: delete, prove it by listing, --close-pod, and report"
            ),
            **sibling.clock(record, state, now),
        }

    before, after = seen["blob_bytes_before"], seen["blob_bytes_after"]
    grew = grown_blobs(before, after)
    vanished = sorted(set(before) - set(after))
    took = float(seen["load_seconds"])
    revision_ok = seen["revision"] == record["target"]["revision"]
    loaded = bool(seen.get("loaded"))
    good = took <= threshold and not grew and revision_ok and loaded
    why = None
    if not good:
        why = (
            "the load exceeded its deadline"
            if took > threshold
            else f"{len(grew)} blob(s) GREW across the load — weights were fetched, not read"
            if grew
            else "the loaded revision is not the pinned one"
            if not revision_ok
            else "the loader did not report a loaded model"
        )
    gb = 1024**3
    return {
        "the_load_proof": True,
        "started_at": started_at,
        "running_seconds": round(running, 1),
        "threshold_seconds": threshold,
        "proof": rel(proof),
        "proof_exists": True,
        "load_seconds": took,
        "gpu": seen.get("gpu"),
        "vram_gb_allocated": (
            None
            if seen.get("vram_bytes_allocated") is None
            else round(int(seen["vram_bytes_allocated"]) / gb, 3)
        ),
        "vram_gb_total": (
            None
            if seen.get("vram_bytes_total") is None
            else round(int(seen["vram_bytes_total"]) / gb, 3)
        ),
        "blobs_counted": len(after),
        "blob_bytes_total": sum(after.values()),
        "blobs_that_grew": grew,
        "blobs_that_vanished": vanished,
        "no_blob_grew": not grew,
        "the_pinned_revision_loaded": revision_ok,
        "hf_bytes_before": seen.get("hf_bytes_before"),
        "hf_bytes_after": seen.get("hf_bytes_after"),
        "whole_cache_moved_by_bytes": (
            None
            if seen.get("hf_bytes_after") is None or seen.get("hf_bytes_before") is None
            else int(seen["hf_bytes_after"]) - int(seen["hf_bytes_before"])
        ),
        "the_whole_cache_delta_grades_nothing": entry["the_invariant_is_BLOBS_and_why_it_moved"],
        "what_failed": why,
        "verdict": "GO" if good else "KILL",
        "rule": entry["rule"],
        "next_step": (
            "the weights are on the GPU and none was fetched — run the smoke"
            if good
            else "KILL: delete, prove it by listing, --close-pod, and report"
        ),
        **sibling.clock(record, state, now),
    }


# --- rung 4, the smoke -----------------------------------------------------------------------------


def the_registered_micro_batch() -> tuple[int, int]:
    import yaml

    training = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["training"]
    return int(training["micro_batch_size"]), int(training["grad_accum"])


def the_registered_log_every() -> int:
    import yaml

    return int(yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["training"]["log_every"])


def the_last_windows_isolated_wall(
    rows: list[dict], log_every: int, steps_run: int
) -> float | None:
    """The final loss line's ONE step, un-divided — REPORT-ONLY, and it moves no verdict.

    Dv814 says the line's `seconds_per_step` is its window's wall over `log_every` no matter how many
    steps the window held. On a 6-step smoke at `log_every: 5` the last window holds exactly ONE
    step, so multiplying that field BACK by `log_every` recovers that single step's wall — the
    closest thing to a steady-state reading this instrument produces.

    It matters because the quotable rate is the whole loop's wall over its steps, and the loop's
    first step pays CUDA autotuning, the allocator's first growth and gradient-checkpointing setup.
    Over 6 steps that overhead is amortised over 6; over arm A's 62 it is amortised over 62. So the
    number the projection rung fires on is biased HIGH against the arms it is predicting, and at a
    break-even of 62.15 s/step that bias is inside the decision. A KILL caused by first-step
    overhead and a KILL caused by the card are the same output unless this is written down
    ([[a_ceiling_derived_from_one_span_measured_over_another]]).

    Registered BEFORE the smoke lands. Deriving it after seeing a KILL would be post-hoc.
    """
    if len(rows) < 2 or not steps_run:
        return None
    last, prior = rows[-1], rows[-2]
    if last.get("seconds_per_step") is None or last.get("step") is None:
        return None
    if int(last["step"]) != steps_run or int(last["step"]) - int(prior.get("step", 0)) != 1:
        return None
    return round(float(last["seconds_per_step"]) * log_every, 3)


def smoke_gate(
    record: dict,
    state: dict,
    provenance: Path,
    loss: Path,
    now: datetime | None = None,
) -> dict:
    """The six optimizer steps that buy this line's first s/step at 3 072 — and the VRAM test.

    The rate is the PROVENANCE's, the loss lines are reported beside it and never averaged into it,
    and the OOM is read out of `micro_batch_final` rather than asserted by whoever ran the command.
    """
    entry = rung(record, 4)
    ceiling = first_number(entry["rule"])
    want_steps = int(entry["steps"])
    micro, accum = the_registered_micro_batch()
    rows = log_lines(loss)
    per_line = [
        {
            "step": one.get("step"),
            "loss": one.get("loss"),
            "seconds_per_step_as_logged": one.get("seconds_per_step"),
            "micro_batch": one.get("micro_batch"),
            "gpu_gb": one.get("gpu_gb"),
        }
        for one in rows
    ]
    seen = json.loads(provenance.read_text(encoding="utf-8")) if provenance.exists() else None
    run = None if seen is None else seen.get("run")

    if run is None:
        return {
            "rung": 4,
            "provenance": rel(provenance),
            "provenance_exists": seen is not None,
            "loss": rel(loss),
            "loss_lines_so_far": per_line,
            "verdict": "WAIT",
            "why": "the smoke has not written its provenance yet — the loop is still running",
            "rule": entry["rule"],
            "next_step": "keep copying loss.jsonl and provenance.json back",
            **sibling.clock(record, state, now),
        }

    measured = float(run["seconds_per_step"])
    steps_run = int(run["steps"])
    log_every = the_registered_log_every()
    isolated = the_last_windows_isolated_wall(rows, log_every, steps_run)
    micro_final = int(run["micro_batch_final"])
    accum_final = int(run["grad_accum_final"])
    instrument_moved = micro_final != micro or accum_final != accum

    if instrument_moved:
        verdict, why = (
            "KILL",
            f"the trainer halved its way out of an OOM: micro_batch {micro} → {micro_final},"
            f" grad_accum {accum} → {accum_final}. `micro_batch_size` is frozen law and an arm"
            " trained at a different one is not the arm this registration prices — STOP",
        )
    elif steps_run < want_steps:
        verdict, why = "KILL", f"the smoke ran {steps_run} of {want_steps} optimizer steps"
    elif measured > ceiling:
        verdict, why = (
            "KILL",
            f"{measured:.2f} s/step is over the registered {ceiling} s/step ceiling",
        )
    else:
        verdict, why = "GO", None

    gate = {
        "rung": 4,
        "provenance": rel(provenance),
        "loss": rel(loss),
        "smoke_steps_registered": want_steps,
        "smoke_steps_run": steps_run,
        "measured_seconds_per_step": round(measured, 3),
        "the_rate_is_the_whole_loops_wall_over_its_steps": {
            "loop_seconds": run.get("seconds"),
            "steps": steps_run,
            "source": "provenance.json::run.seconds_per_step",
        },
        "loss_lines": per_line,
        "the_loss_lines_are_NOT_a_rate": entry["the_quotable_rate_is_the_PROVENANCE_one"],
        "the_decomposition_REPORT_ONLY": {
            "log_every": log_every,
            "the_final_steps_isolated_wall_seconds": isolated,
            "the_graded_rate_seconds_per_step": round(measured, 3),
            "the_loop_wall_seconds": run.get("seconds"),
            "the_amortised_start_up_seconds": (
                None
                if isolated is None or run.get("seconds") is None
                else round(float(run["seconds"]) - steps_run * isolated, 1)
            ),
            "the_arms_are_10x_and_14x_this_smokes_length": (
                "62 and 82 optimizer steps against 6, so whatever the loop's start-up costs is"
                " amortised over ten to fourteen times as many steps there as it is here"
            ),
            "it_moves_no_verdict": entry["the_decomposition_is_REPORT_ONLY"],
        },
        "ceiling_seconds_per_step": ceiling,
        "micro_batch_registered": micro,
        "micro_batch_final": micro_final,
        "grad_accum_registered": accum,
        "grad_accum_final": accum_final,
        "the_instrument_is_the_registered_one": not instrument_moved,
        "gpu_gb_peak": run.get("gpu_gb_peak"),
        "why": why,
        "verdict": verdict,
        "rule": entry["rule"],
        "next_step": (
            "this is the ONLY s/step this line may use — run --projection --after smoke"
            if verdict == "GO"
            else "KILL and STOP: delete, prove it by listing, --close-pod, report to the team lead"
        ),
        **sibling.clock(record, state, now),
    }
    if verdict == "GO":
        state["measured_seconds_per_step"] = gate["measured_seconds_per_step"]
    return gate


# --- rung 3, on an EVAL leg, charging the measured step --------------------------------------------

RATEABLE = ("eval_a", "eval_b")
"""The legs this session pays generation for. The base legs are r2's and are not re-bought, so the
sibling's `--leg` choices could never fire here."""


def the_rate_rung_charges_the_measured_step(record: dict, state: dict) -> tuple[dict, dict]:
    """A VIEW of the record whose rung-3 step charge is the s/step the SMOKE measured.

    The registered 61.047 is a FLOOR — the cheapest this stack has ever been registered at — and it
    is the right charge only while no reading exists. By the time this rung can fire, one does. The
    view moves the reference and never the number, which is the same shape
    `gate_lora_c.as_the_sibling_reads_it` uses ([[projected_rate_versus_measured_rate]]).
    """
    floor = float(rung(record, 3)["steps_charged_at_seconds_per_step"])
    measured = state.get("measured_seconds_per_step")
    if measured is None:
        return record, {"steps_charged_at": floor, "the_charge_is_measured": False}
    view = copy.deepcopy(record)
    rung(view, 3)["steps_charged_at_seconds_per_step"] = float(measured)
    return view, {
        "steps_charged_at": float(measured),
        "the_charge_is_measured": True,
        "the_registered_floor_it_replaces": floor,
    }


# --- rung 5, the projection, with the teardown tail -------------------------------------------------


def projection(
    record: dict,
    state: dict,
    after: str,
    reading: float,
    threads_realised: int | None = None,
    now: datetime | None = None,
) -> dict:
    """`gate_lora_c.projection`, plus the tail it cannot see and the thread bound it charged.

    The sibling's verdict is recomputed here rather than trusted, because adding seconds to a
    projection can only make it later and a gate that reports GO while its own arithmetic says KILL
    is worse than no gate at all.
    """
    inner = sibling.projection(record, state, after, reading, now)
    tail = float(record["money"]["pre_pod_arithmetic"]["fixed_seconds"]["teardown_and_pull"])
    pod = live_pod(state)
    if pod is None:
        raise SystemExit("no pod is live — there is nothing to project")
    rate = rate_of(pod)
    cap = first_number(rung(record, 5)["rule"])

    ahead = float(inner["seconds_ahead"]) + tail
    projected_usd = reading + ahead * rate
    projected_seconds = float(inner["cumulative_billed_seconds"]) + ahead
    over_cap = projected_usd > cap
    over_stop = projected_seconds > float(inner["hard_stop_seconds"])

    charged = sibling.plan(record)["eval_a"]["pass_2_threads"]
    bound = {
        "pass_2_threads_charged_per_leg": charged,
        "pass_2_threads_realised_per_leg": threads_realised,
        "the_charge_is_a_BOUND_not_a_count": (
            "a thread enters an arm's rebuilt pack only if that arm marked one of its rows OURS;"
            " r2's v2 leg produced 11 of the 15 charged. A KILL that would not have happened at the"
            " realised count is a bound-attributable KILL and has to be visible as one"
        ),
        "seconds_the_bound_charges_over_the_realised_count": (
            None
            if threads_realised is None
            else round(
                (charged - threads_realised)
                * float(
                    record["money"]["pre_pod_arithmetic"]["rates_used"]["pass_2_seconds_per_thread"]
                )
                * 2,  # both eval legs are charged at the bound
                1,
            )
        ),
    }
    return {
        **inner,
        "teardown_and_pull_tail_seconds": tail,
        "the_tail_is_billed_work_in_no_priced_unit": rung(record, 5)[
            "the_TAIL_is_added_because_the_sibling_does_not_carry_it"
        ],
        "seconds_ahead_with_the_tail": round(ahead, 1),
        "projected_seconds": round(projected_seconds, 1),
        "projected_usd": round(projected_usd, 4),
        "over_the_cap": over_cap,
        "over_the_hard_stop": over_stop,
        "the_pass_2_bound": bound,
        "verdict": "KILL" if over_cap or over_stop else "GO",
        "next_step": (
            "KILL: pull every artifact, prove the teardown by listing, STOP to the team lead with"
            " the ledger. A KILL here is compliance"
            if over_cap or over_stop
            else f"GO — the next milestone after {after}"
        ),
    }


MINE = ("--read-back", "--load-proof", "--smoke", "--rate", "--projection")


def main(argv: list[str] | None = None, now: datetime | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    with the_gate_reads_r3():
        record = sibling.registration()
        seal = the_frozen_registration_is_unmoved(record)

        if "--read-back" in argv:
            gate = {**read_back(record), "frozen": seal}
            print(json.dumps(gate, ensure_ascii=False, indent=2, sort_keys=True))
            print(f"\n{gate['verdict']}  ·  {gate['next_step']}")
            return GO if gate["verdict"] == "GO" else KILL

        if "--pre-create-check" in argv:
            code = sibling.main(argv, now)
            print(json.dumps({"frozen": seal}, ensure_ascii=False, indent=2, sort_keys=True))
            return code

        if "--open" in argv:
            code = sibling.main(argv, now)
            if code != GO:
                return code
            peek = argparse.ArgumentParser(add_help=False)
            peek.add_argument("--usd-per-hour", type=float)
            known, _ = peek.parse_known_args(argv)
            print(
                json.dumps(
                    the_cap_affords_the_hard_stop(record, known.usd_per_hour),
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
            )
            return code

        if not any(one in argv for one in MINE):
            return sibling.main(argv, now)

        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--load-proof", action="store_true", help="the load, on blobs")
        parser.add_argument("--smoke", action="store_true", help="rung 4")
        parser.add_argument("--rate", action="store_true", help="rung 3, on an eval leg")
        parser.add_argument("--projection", action="store_true", help="rung 5")
        parser.add_argument("--started-at", help="when this stage began")
        parser.add_argument("--proof", type=Path, help="the pod's own load record")
        parser.add_argument("--provenance", type=Path, help="the smoke's provenance.json")
        parser.add_argument("--loss", type=Path, help="the smoke's loss.jsonl")
        parser.add_argument("--leg", choices=RATEABLE)
        parser.add_argument("--replies", type=Path, help="the leg's growing out-file")
        parser.add_argument("--after", choices=sibling.ORDER)
        parser.add_argument("--reading", type=float, help="the guard's reading in USD")
        parser.add_argument(
            "--pass-2-threads-realised",
            type=int,
            help="how many threads the rebuilt pack actually holds, per leg — reported, never charged",
        )
        args = parser.parse_args(argv)
        state = sibling.state_now()

        if args.load_proof:
            if not args.proof or not args.started_at:
                parser.error("--load-proof needs --proof and --started-at")
            gate = load_proof_gate(record, state, args.started_at, args.proof, now)
            kind = "load-proof"
        elif args.smoke:
            if not args.provenance or not args.loss:
                parser.error("--smoke needs --provenance and --loss")
            gate = smoke_gate(record, state, args.provenance, args.loss, now)
            kind = "smoke"
        elif args.rate:
            if not args.leg or not args.replies or not args.started_at:
                parser.error("--rate needs --leg, --replies and --started-at")
            view, charge = the_rate_rung_charges_the_measured_step(record, state)
            gate = {
                **sibling.rate_gate(view, state, args.leg, args.replies, args.started_at, now),
                "the_step_charge": charge,
            }
            if gate["verdict"] != "WAIT":
                state["measured_seconds_per_call"] = gate["realised_seconds_per_call"]
            kind = f"rate-{args.leg}"
        else:
            if not args.after or args.reading is None:
                parser.error("--projection needs --after and --reading (the guard's USD)")
            gate = projection(
                record, state, args.after, args.reading, args.pass_2_threads_realised, now
            )
            kind = f"projection-{args.after}"

        gate["frozen"] = seal
        sibling.append_gate(state, gate, kind)
        sibling.save(state)
        return show(gate)


if __name__ == "__main__":
    raise SystemExit(main())
