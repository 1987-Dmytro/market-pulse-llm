#!/usr/bin/env python3
"""The r2 migration's rungs — a SIBLING of `scripts/gate_lora_c.py`, which is a sibling of lora-b's.

`docs/PROMPT-lora-c-migrate-r2.md` registers eight rungs. Four of them already have an instrument
one line up, reading a record through module-level constants: rung 0's price-and-card refusal,
rung 1's ssh dead-man, rung 2's silence clock and the `--terminate-after` backstop, plus the
cumulative clock, the run state and the gate append. Those are re-bound and CALLED, in zero new
copies ([[a_self_pinning_producer_cannot_grow_a_parameter]]).

Four things are written here because the sibling cannot answer them:

- **the cap affords the hard stop, as an INEQUALITY.** The vramprobe registered the same relation
  as an equality and it survived only because $0.30 / $0.72 x 3600 was 1500.0 exactly. At this cap
  the affordable window is 3 884.9 s against a registered stop of 3 600, and an equality would
  refuse a price the cap comfortably covers ([[a_published_ratio_is_not_the_gates]]).
- **the stage bounds SUM inside the hard stop.** The previous contract's boot + download + load
  already came to 3 500 s of a 3 600 s stop with four stages unnamed (Dv822). This adds the check
  the arithmetic needed, at `--pre-create-check`, before any money.
- **rung 4, the download, graded on BYTES.** `hf download` prints carriage-return progress while a
  transfer is stalled, so a line-based liveness rung reads a dead transfer as alive
  ([[no_rung_watches_an_idle_pod]]). This one reads `du -sb /workspace/hf` over stamped polls: a
  poll that did not grow starts rung 2's silence clock, one that grew resets it, and completion is
  a byte FLOOR rather than a caller's assertion ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]]).
- **rungs 3 and 5, the venv and the load proof.** Both are new stages, and both are graded on a
  file the pod produced: the venv on its own interpreter naming the installed stack and the card,
  the load proof on the seconds, the VRAM and the volume's byte count either side of the load.

    PYTHONPATH=src python3.11 scripts/gate_lora_c_migrate_r2.py --pre-create-check
    PYTHONPATH=src python3.11 scripts/gate_lora_c_migrate_r2.py --open --pod-id <id> \\
        --created-at <ISO> --usd-per-hour <costPerHr> --card '<displayName>' \\
        --terminate-after '<the stamp given to pod create>'
    PYTHONPATH=src python3.11 scripts/gate_lora_c_migrate_r2.py --gate0 [--ssh-ok]
    PYTHONPATH=src python3.11 scripts/gate_lora_c_migrate_r2.py --liveness --last-event <ISO>
    PYTHONPATH=src python3.11 scripts/gate_lora_c_migrate_r2.py --venv --started-at <ISO> \\
        [--done-at <ISO>] [--proof results/lora_c_migrate_r2_venv.txt]
    PYTHONPATH=src python3.11 scripts/gate_lora_c_migrate_r2.py --download --started-at <ISO> \\
        --polls results/lora_c_migrate_r2_bytes.jsonl
    PYTHONPATH=src python3.11 scripts/gate_lora_c_migrate_r2.py --load-proof --started-at <ISO> \\
        --proof results/lora_c_migrate_r2_load_proof.json
    PYTHONPATH=src python3.11 scripts/gate_lora_c_migrate_r2.py --close-pod --deleted-at <ISO> \\
        --outcome '<why>'
"""

import argparse
import contextlib
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_lora_c as sibling  # noqa: E402

PHASE = "lora-c-migrate-r2"
PREREG = REPO_ROOT / "results" / "prereg_lora_c_migrate_r2.json"
RECORD = REPO_ROOT / "results" / "lora_c_migrate_r2.json"

GO, KILL, WAIT = sibling.GO, sibling.KILL, sibling.WAIT

rel = sibling.rel
stamp = sibling.stamp
elapsed_since = sibling.elapsed_since
first_number = sibling.first_number
rung = sibling.rung
show = sibling.show
live_pod = sibling.sibling.live_pod

FROZEN = REPO_ROOT / "results" / "prereg_lora_c.json"


@contextlib.contextmanager
def the_gate_reads_the_migration():
    """`gate_lora_c`'s file constants point at this step, for the length of one call.

    That module re-binds lora-b's constants from its OWN module globals at call time, so moving
    these three moves the whole chain onto this step's two files. The `finally` is what keeps
    lora-c's and the probe's own gates true in the same process.
    """
    was = (sibling.PHASE, sibling.PREREG, sibling.RECORD)
    sibling.PHASE, sibling.PREREG, sibling.RECORD = PHASE, PREREG, RECORD
    try:
        yield
    finally:
        sibling.PHASE, sibling.PREREG, sibling.RECORD = was


def the_frozen_registration_is_unmoved(record: dict) -> dict:
    """The FROZEN `results/prereg_lora_c.json`, hashed and compared to the sha registered here.

    It is an INPUT to this step and the contract's first DO-NOT. A record that merely SAYS it did
    not touch something is prose; this is the sentence made checkable ([[a_claim_no_number_can_check]]).
    """
    import hashlib

    want = record["this_is_not_the_registered_attempt"]["sha256"]
    got = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
    if got != want:
        raise SystemExit(
            f"{rel(FROZEN)} hashes to {got}, and this registration was built against {want}."
            " The frozen registration is this step's first DO-NOT. STOP."
        )
    return {"the_frozen_registration": rel(FROZEN), "sha256": got, "unmoved": True}


def the_cap_affords_the_hard_stop(record: dict, usd_per_hour: float) -> dict:
    """`cap / price x 3600 >= hard_stop`, re-solved on the create response. An INEQUALITY.

    Rung 0 runs FIRST and owns the price refusal. What this adds is that the window the plan was
    solved TO is one the cap can still pay for at the price the create actually returned.

    At this cap and this stop the inequality reduces to `price <= $1.50`, which IS rung 0's ceiling,
    so no price rung 0 admits can fail it today. It is registered in the general form because that
    is the form that is true, and it is driven to its refusing branch on a synthetic pair in the
    tests — a check whose failing branch has never run is a check nobody has seen work
    ([[guard_selftest_negative_control]]).
    """
    block = record["money"]["pre_pod_arithmetic"]
    stop = float(block["hard_stop_seconds"])
    cap = float(record["money"]["cap_usd_all_in"])
    buys = cap / usd_per_hour * 3600.0
    if buys < stop:
        raise SystemExit(
            f"the cap ${cap:.2f} at ${usd_per_hour}/h buys {buys:.1f} s, and {rel(PREREG)}"
            f" registers a hard stop of {stop:.1f} s — {stop - buys:.1f} s more than the cap can"
            f" pay for. The formula is {block['hard_stop_formula']!r}. DELETE the pod and STOP:"
            " the backstop this session would be given outlives the money behind it."
        )
    return {
        "cap_usd_all_in": cap,
        "usd_per_hour": usd_per_hour,
        "hard_stop_formula": block["hard_stop_formula"],
        "hard_stop_registered_seconds": stop,
        "what_the_cap_buys_seconds": round(buys, 1),
        "slack_seconds": round(buys - stop, 1),
        "the_full_stop_would_cost_usd": round(stop / 3600.0 * usd_per_hour, 6),
        "cap_left_if_the_stop_is_reached_usd": round(cap - stop / 3600.0 * usd_per_hour, 6),
    }


STAGE_RUNGS = (1, 3, 4, 5)
"""Boot, venv, download, load proof — the four stages with a registered deadline. The teardown
margin is not a rung: nothing grades it, it is the room the deletion needs."""


def the_stage_bounds_sum_inside_the_hard_stop(record: dict) -> dict:
    """The four stage deadlines plus the teardown margin, against the hard stop.

    Read from the rungs themselves, never from the registration's own summary of them: a sum that
    is asserted beside its addends is a number with two homes, and the previous contract's own
    arithmetic crossed its stop by 3 500 of 3 600 s with four stages unnamed (Dv822).
    """
    block = record["money"]["pre_pod_arithmetic"]["the_stage_bounds_SUM_inside_the_stop"]
    stop = float(record["money"]["pre_pod_arithmetic"]["hard_stop_seconds"])
    margin = float(block["teardown_margin_seconds"])
    stages = {int(one): float(rung(record, one)["threshold"]) for one in STAGE_RUNGS}
    summed = sum(stages.values()) + margin
    return {
        "stage_thresholds_by_rung": stages,
        "teardown_margin_seconds": margin,
        "summed_seconds": round(summed, 1),
        "hard_stop_seconds": stop,
        "headroom_seconds": round(stop - summed, 1),
        "the_registrations_own_summary_agrees": (
            abs(float(block["summed_seconds"]) - summed) < 1e-9
            and abs(float(block["headroom_seconds"]) - (stop - summed)) < 1e-9
        ),
        "verdict": "GO" if summed <= stop else "KILL",
        "the_two_unbounded_stages": block["the_two_stages_inside_the_310_s_of_headroom"],
    }


# --- rung 3, the venv ----------------------------------------------------------------------------


def venv_gate(
    record: dict,
    state: dict,
    started_at: str,
    done_at: str | None,
    proof: Path | None,
    now: datetime | None = None,
) -> dict:
    """The first bound this repo has ever put on the venv build — and its first measurement.

    GO is not «the caller said it finished». It is the venv's OWN interpreter printing the stack it
    installed and the card it can see, which also cross-checks rung 0's card from inside the pod
    ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]]).
    """
    entry = rung(record, 3)
    threshold = first_number(entry["rule"])
    card = rung(record, 0)["authorised_cards"]
    text = proof.read_text(encoding="utf-8").strip() if proof and proof.exists() else ""
    named = [one for one in card if one in text or card[one]["gpu_id"] in text]
    took = None if done_at is None else elapsed_since(started_at, stamp(done_at))
    running = elapsed_since(started_at, now)
    ok = bool(text) and bool(named) and took is not None and took <= threshold
    verdict = "GO" if ok else ("KILL" if running >= threshold or (text and not named) else "WAIT")
    return {
        "rung": 3,
        "started_at": started_at,
        "done_at": done_at,
        "measured_seconds": None if took is None else round(took, 1),
        "running_seconds": round(running, 1),
        "threshold_seconds": threshold,
        "seconds_left": round(threshold - running, 1),
        "proof": None if proof is None else rel(proof),
        "proof_exists": bool(text),
        "the_stack_the_venv_reports": text.splitlines()[-1][:300] if text else None,
        "the_card_the_venv_sees": named,
        "the_bound_is_new_and_unmeasured": entry["the_bound_is_NEW_and_unmeasured"],
        "this_measurement_lands_in_the_run_record_not_the_registration": record["artifacts"][
            "the_venv_measurement_lands_here_not_in_this_file"
        ],
        "verdict": verdict,
        "rule": entry["rule"],
        "next_step": (
            "the venv is built and it sees the authorised card; start the download"
            if verdict == "GO"
            else "keep waiting on the pip install; re-run when it returns"
            if verdict == "WAIT"
            else "KILL: delete, prove it by listing, --close-pod, and report"
        ),
        **sibling.clock(record, state, now),
    }


# --- rung 4, the download, on BYTES ---------------------------------------------------------------


def byte_polls(path: Path) -> list[dict]:
    """`{at, bytes}` rows. A torn last line is DROPPED — the file is appended to while it is read."""
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    rows = []
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            if index != len(lines) - 1:
                raise SystemExit(
                    f"{rel(path)} line {index + 1} is not JSON and it is not the last one — that is"
                    " a damaged file, not the mid-write race. Stop and report."
                ) from None
    return rows


def download_gate(
    record: dict,
    state: dict,
    started_at: str,
    polls: Path,
    now: datetime | None = None,
) -> dict:
    """Rung 4 — the deadline, and rung 2's silence clock measured in BYTES.

    Three separable readings, and the gate says which one fired:

    * the DEADLINE, from the download's own start;
    * the SILENCE clock, from the last poll whose byte count actually GREW — rung 2's threshold,
      read from rung 2 and not copied here ([[two_values_for_one_input_get_quoted_kindly]]);
    * COMPLETION, as a byte floor the record registers.

    A gap between polls longer than the registered cadence is recorded as a BLIND WINDOW rather
    than graded. It cannot fire a rung — a stall inside it that recovered is indistinguishable from
    a healthy transfer, and killing on it would kill compliant work — but a KILL that happened
    inside an unpolled window has to be visible as one ([[a_checker_whose_failure_is_silence]]).
    """
    entry = rung(record, 4)
    deadline = first_number(entry["rule"])
    cadence = float(entry["poll_cadence_seconds"])
    silence = float(rung(record, 2)["threshold"])
    floor = int(entry["the_download_is_complete_at_bytes"])

    rows = byte_polls(polls)
    marks = [stamp(one["at"]) for one in rows]
    counts = [int(one["bytes"]) for one in rows]

    grew_at = stamp(started_at)
    for index in range(len(rows)):
        if index == 0 or counts[index] > counts[index - 1]:
            grew_at = marks[index]

    edges = [stamp(started_at), *marks]
    blind = [
        {
            "from": edges[index].isoformat(timespec="seconds"),
            "to": edges[index + 1].isoformat(timespec="seconds"),
            "seconds": round((edges[index + 1] - edges[index]).total_seconds(), 1),
        }
        for index in range(len(edges) - 1)
        if (edges[index + 1] - edges[index]).total_seconds() > cadence
    ]

    running = elapsed_since(started_at, now)
    quiet = elapsed_since(grew_at.isoformat(), now)
    done = bool(counts) and counts[-1] >= floor

    if done:
        verdict, fired = "GO", None
    elif running >= deadline:
        verdict, fired = "KILL", "the 1200 s download deadline"
    elif quiet >= silence:
        verdict, fired = "KILL", "rung 2's silence clock — no byte growth"
    else:
        verdict, fired = "WAIT", None

    return {
        "rung": 4,
        "started_at": started_at,
        "running_seconds": round(running, 1),
        "deadline_seconds": deadline,
        "seconds_left_on_the_deadline": round(deadline - running, 1),
        "polls": rel(polls),
        "polls_seen": len(rows),
        "bytes_now": counts[-1] if counts else None,
        "bytes_first": counts[0] if counts else None,
        "bytes_grew_by": None if len(counts) < 2 else counts[-1] - counts[0],
        "complete_at_bytes": floor,
        "fraction_of_the_floor": None if not counts else round(counts[-1] / floor, 4),
        "last_growth_at": grew_at.isoformat(timespec="seconds"),
        "quiet_seconds": round(quiet, 1),
        "silence_threshold_seconds": silence,
        "silence_threshold_is_rung_2s": "read from rung 2, never restated here",
        "poll_cadence_seconds": cadence,
        "blind_windows_over_the_cadence": blind,
        "the_reading_has_no_holes": not blind,
        "what_fired": fired,
        "verdict": verdict,
        "rule": entry["rule"],
        "next_step": (
            "the weights are on the volume; build nothing else, run the load proof"
            if verdict == "GO"
            else f"poll `du -sb /workspace/hf` again within {cadence:.0f} s and append the row"
            if verdict == "WAIT"
            else "KILL: delete, prove it by listing, --close-pod, and report"
        ),
        **sibling.clock(record, state, now),
    }


# --- rung 5, the load proof -----------------------------------------------------------------------


def load_proof_gate(
    record: dict,
    state: dict,
    started_at: str,
    proof: Path,
    now: datetime | None = None,
) -> dict:
    """Rung 5 — the deliverable. Seconds, VRAM, and the volume proved to be what was READ from.

    A volume nobody loaded from is a hope. A load that re-downloaded is a load from the internet
    with a volume attached — so the pod's own `du -sb /workspace/hf` either side of the load is
    part of the proof, and an unchanged count is what makes «it loaded FROM the volume» a reading.
    """
    entry = rung(record, 5)
    threshold = first_number(entry["rule"])
    running = elapsed_since(started_at, now)
    seen = json.loads(proof.read_text(encoding="utf-8")) if proof.exists() else None

    if seen is None:
        verdict, why = ("KILL" if running >= threshold else "WAIT"), None
        took = None
        unmoved = None
        revision_ok = None
    else:
        took = float(seen["load_seconds"])
        unmoved = int(seen["hf_bytes_before"]) == int(seen["hf_bytes_after"])
        revision_ok = seen["revision"] == record["target"]["revision"]
        good = took <= threshold and unmoved and revision_ok and bool(seen.get("loaded"))
        verdict = "GO" if good else "KILL"
        why = None
        if not good:
            why = (
                "the load exceeded its deadline"
                if took > threshold
                else "the volume's byte count MOVED across the load — something was fetched"
                if not unmoved
                else "the loaded revision is not the pinned one"
                if not revision_ok
                else "the loader did not report a loaded model"
            )

    return {
        "rung": 5,
        "started_at": started_at,
        "running_seconds": round(running, 1),
        "threshold_seconds": threshold,
        "seconds_left": round(threshold - running, 1),
        "proof": rel(proof),
        "proof_exists": seen is not None,
        "load_seconds": took,
        "vram_bytes_allocated": None if seen is None else seen.get("vram_bytes_allocated"),
        "vram_gb_allocated": (
            None
            if seen is None or seen.get("vram_bytes_allocated") is None
            else round(int(seen["vram_bytes_allocated"]) / 1024**3, 3)
        ),
        "vram_gb_reserved": (
            None
            if seen is None or seen.get("vram_bytes_reserved") is None
            else round(int(seen["vram_bytes_reserved"]) / 1024**3, 3)
        ),
        "gpu": None if seen is None else seen.get("gpu"),
        "hf_bytes_before": None if seen is None else seen.get("hf_bytes_before"),
        "hf_bytes_after": None if seen is None else seen.get("hf_bytes_after"),
        "the_volume_was_not_written_during_the_load": unmoved,
        "the_pinned_revision_loaded": revision_ok,
        "what_failed": why,
        "verdict": verdict,
        "rule": entry["rule"],
        "next_step": (
            "the deliverable is bought — stage the packs, then DELETE the pod and prove it"
            if verdict == "GO"
            else "keep copying the proof file back; the load is still running"
            if verdict == "WAIT"
            else "KILL: delete, prove it by listing, --close-pod, and report"
        ),
        **sibling.clock(record, state, now),
    }


MINE = ("--venv", "--download", "--load-proof")


def main(argv: list[str] | None = None, now: datetime | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    with the_gate_reads_the_migration():
        record = sibling.registration()
        frozen = the_frozen_registration_is_unmoved(record)

        if "--pre-create-check" in argv:
            code = sibling.main(argv, now)
            sums = the_stage_bounds_sum_inside_the_hard_stop(record)
            print(
                json.dumps({**sums, "frozen": frozen}, ensure_ascii=False, indent=2, sort_keys=True)
            )
            return code if sums["verdict"] == "GO" else KILL

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
        parser.add_argument("--venv", action="store_true", help="rung 3, the venv build")
        parser.add_argument("--download", action="store_true", help="rung 4, the weights, on bytes")
        parser.add_argument("--load-proof", action="store_true", help="rung 5, the deliverable")
        parser.add_argument("--started-at", required=True, help="when this stage began")
        parser.add_argument("--done-at", help="when the venv's pip install returned")
        parser.add_argument("--polls", type=Path, help="the {at, bytes} poll log")
        parser.add_argument("--proof", type=Path, help="the stage's own output file")
        args = parser.parse_args(argv)

        state = sibling.state_now()
        if args.venv:
            gate = venv_gate(record, state, args.started_at, args.done_at, args.proof, now)
            kind = "venv"
        elif args.download:
            if not args.polls:
                parser.error("--download needs --polls: bytes are the liveness signal")
            gate = download_gate(record, state, args.started_at, args.polls, now)
            kind = "download"
        else:
            if not args.proof:
                parser.error("--load-proof needs --proof: the pod's own load record")
            gate = load_proof_gate(record, state, args.started_at, args.proof, now)
            kind = "load-proof"
        gate["frozen"] = frozen
        sibling.append_gate(state, gate, kind)
        sibling.save(state)
        return show(gate)


if __name__ == "__main__":
    raise SystemExit(main())
