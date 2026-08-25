#!/usr/bin/env python3
"""The vramprobe's rungs — a SIBLING of `scripts/gate_lora_c.py`, which is a sibling of lora-b's.

`docs/PROMPT-lora-c-vramprobe.md` registers a boot gate, a liveness deadline, a smoke ceiling, a
hard stop and a cap. Four of those already have an instrument one line up, reading a record through
module-level constants; this file re-binds those constants for the length of one call and CALLS
them, so rung 0's three conditions, rung 1's dead-man, rung 2's silence clock, the cumulative clock,
the `--terminate-after` backstop and the close-pod arithmetic exist here in zero new copies
([[a_self_pinning_producer_cannot_grow_a_parameter]]).

Two things are written here because the sibling cannot answer them:

- **the hard stop is re-solved at the price the create actually returned.** `$0.30 / $0.72 × 3600`
  is 1 500 s exactly — the cap and the hard stop are one constraint with no headroom — so a pod at
  any other price makes the registered 1 500 either an overspend or a waste. Rung 0 already refuses
  an unregistered price by equality; this refuses the arithmetic BEHIND it, which is the half a
  price column cannot check ([[one_constant_answering_two_questions]]).
- **rung 3, the smoke.** `gate_lora_c.smoke_gate` prices its steps out of a leg table this probe has
  no legs for, waits for six loss lines where `log_every: 5` produces two, and takes the OOM as a
  flag from its caller. This one reads the pod's own log for the verdict, derives the affordable
  s/step from the cap and this pod's measured preamble, and reports which of the two registered
  bounds actually binds.

    PYTHONPATH=src python3.11 scripts/gate_lora_c_vramprobe.py --pre-create-check
    PYTHONPATH=src python3.11 scripts/gate_lora_c_vramprobe.py --open --pod-id <id> \\
        --created-at <ISO> --usd-per-hour <costPerHr> --card '<displayName>' \\
        --terminate-after '<the stamp given to pod create>'
    PYTHONPATH=src python3.11 scripts/gate_lora_c_vramprobe.py --gate0 [--ssh-ok]
    PYTHONPATH=src python3.11 scripts/gate_lora_c_vramprobe.py --liveness --last-event <ISO>
    PYTHONPATH=src python3.11 scripts/gate_lora_c_vramprobe.py --smoke --started-at <ISO> \\
        --log results/lora_c_vramprobe_smoke.log \\
        [--loss results/lora_c_vramprobe_loss.jsonl] \\
        [--provenance results/lora_c_vramprobe_provenance.json] \\
        [--environ results/lora_c_vramprobe_environ.txt]
    PYTHONPATH=src python3.11 scripts/gate_lora_c_vramprobe.py --close-pod --deleted-at <ISO> \\
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

PHASE = "lora-c-vramprobe"
PREREG = REPO_ROOT / "results" / "prereg_lora_c_vramprobe.json"
RECORD = REPO_ROOT / "results" / "lora_c_vramprobe.json"

GO, KILL, WAIT = sibling.GO, sibling.KILL, sibling.WAIT

rel = sibling.rel
elapsed_since = sibling.elapsed_since
first_number = sibling.first_number
rung = sibling.rung
log_lines = sibling.log_lines
show = sibling.show
stamp = sibling.stamp
live_pod = sibling.sibling.live_pod
"""`gate_lora_b.live_pod`, two modules up: the last pod of the record, unless it has a deleted_at."""

OOM_MARK = "torch.OutOfMemoryError"
TRACEBACK_MARK = "Traceback (most recent call last):"
FALLBACK_MARK = "OOM: micro_batch ->"


@contextlib.contextmanager
def the_gate_reads_the_probe():
    """`gate_lora_c`'s file constants point at the probe, for the length of one call.

    That module re-binds lora-b's constants from its OWN module globals at call time, so moving
    these three moves the whole chain — registration, run state, gate append, save — onto this
    probe's two files. The `finally` is what keeps lora-c's own gates true in the same process.
    """
    was = (sibling.PHASE, sibling.PREREG, sibling.RECORD)
    sibling.PHASE, sibling.PREREG, sibling.RECORD = PHASE, PREREG, RECORD
    try:
        yield
    finally:
        sibling.PHASE, sibling.PREREG, sibling.RECORD = was


HARD_STOP_TOLERANCE_SECONDS = 1.0
"""How far the registered hard stop may sit from the one the observed price solves for. A second of
rounding is slop; anything more is a plan solved at another price."""


def the_hard_stop_is_solved_at_the_observed_price(record: dict, usd_per_hour: float) -> dict:
    """`cap / price × 3600`, re-solved on the create response, against the registered literal.

    Rung 0 runs FIRST and owns the refusal: a price with no registered column is its KILL, not this
    function's. What this adds is the half a price column cannot check — that the number the plan
    was solved TO still follows from the price it was solved AT. The hard stop is a literal in the
    record and the cap is another; at $0.79/h the pair says 1 500 s where the cap buys 1 367, and
    with one registered column that mismatch can only come from an edit to this hand-written file.
    """
    block = record["money"]["pre_pod_arithmetic"]
    registered = float(block["hard_stop_seconds"])
    cap = float(record["money"]["cap_usd_all_in"])
    solved = cap / usd_per_hour * 3600.0
    drift = solved - registered
    if abs(drift) > HARD_STOP_TOLERANCE_SECONDS:
        raise SystemExit(
            f"the cap ${cap:.2f} at ${usd_per_hour}/h buys {solved:.1f} s, and"
            f" {rel(PREREG)} registers a hard stop of {registered:.1f} s — {drift:+.1f} s apart."
            f" The formula is {block['hard_stop_formula']!r}. DELETE the pod and STOP: the"
            " backstop this session would be given is not the one the cap allows."
        )
    return {
        "cap_usd_all_in": cap,
        "usd_per_hour": usd_per_hour,
        "hard_stop_formula": block["hard_stop_formula"],
        "hard_stop_solved_seconds": round(solved, 1),
        "hard_stop_registered_seconds": registered,
        "drift_seconds": round(drift, 3),
    }


# --- rung 3, the smoke ---------------------------------------------------------------------------


def expected_log_steps(steps: int, log_every: int) -> list[int]:
    """The optimizer steps `train_qlora.train` actually writes a loss line at.

    `step % log_every == 0 or step == total` — at 6 steps and `log_every: 5` that is [5, 6], two
    lines and not six. A rung counting to six waits for a line the run will never write
    ([[the_expectation_no_reading_reaches]]).
    """
    return [one for one in range(1, steps + 1) if one % log_every == 0 or one == steps]


def budget(record: dict, pod: dict, started_at: str) -> dict:
    """What this pod can still afford per optimizer step, and which registered bound binds.

    Two bounds are registered on one run: 181.5 s/step, and a 1 500 s hard stop that IS the $0.30
    cap. The affordable rate is what the cap leaves after the preamble this pod actually spent, the
    model load and the teardown; the smaller of the two is the one that can fire
    ([[an_absolute_bar_needs_a_reachability_state]]).
    """
    entry = rung(record, 3)
    ceiling = first_number(entry["rule"])
    steps = int(entry["steps"])
    load = float(entry["load_allowance_seconds"])
    margin = float(entry["teardown_margin_seconds"])
    stop = float(record["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"])
    preamble = elapsed_since(pod["created_at"], stamp(started_at))
    affordable = (stop - preamble - margin - load) / steps
    binding = min(ceiling, affordable)
    return {
        "steps": steps,
        "log_every": int(entry["log_every"]),
        "load_allowance_seconds": load,
        "teardown_margin_seconds": margin,
        "hard_stop_seconds": stop,
        "preamble_seconds": round(preamble, 1),
        "registered_ceiling_seconds_per_step": ceiling,
        "affordable_seconds_per_step": round(affordable, 2),
        "binding_seconds_per_step": round(binding, 2),
        "what_binds": "the $0.30 cap" if affordable < ceiling else "the registered 181.5 ceiling",
    }


def read_the_log(log: Path) -> dict:
    """The verdict, out of the pod's own stdout — not out of a flag the caller sets.

    A `--oom` switch records the reading its caller gave it and calls that a gate
    ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]]). The three marks below are the trainer's
    and torch's own strings, and the fallback line is a signal in its own right: it says the shipped
    halving fired, which on a surviving run means the card only just held.
    """
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    return {
        "log": rel(log),
        "log_exists": log.exists(),
        "out_of_memory": OOM_MARK in text,
        "traceback": TRACEBACK_MARK in text,
        "the_trainers_own_halving_fired": FALLBACK_MARK in text,
        "tail": text.strip().splitlines()[-1][:400] if text.strip() else None,
    }


def smoke_gate(
    record: dict,
    state: dict,
    started_at: str,
    log: Path,
    loss: Path | None = None,
    provenance: Path | None = None,
    environ: Path | None = None,
    now: datetime | None = None,
) -> dict:
    """Five outcomes, on readings: the log, the two output files, and the process's environment."""
    pod = live_pod(state)
    if pod is None:
        raise SystemExit("no pod is live — the smoke rung has nothing to measure")
    bounds = budget(record, pod, started_at)
    seen = read_the_log(log)
    rows = log_lines(loss) if loss and loss.exists() else []
    finished = (
        json.loads(provenance.read_text(encoding="utf-8"))
        if provenance and provenance.exists()
        else None
    )
    run = (finished or {}).get("run") or {}
    proof = environ.read_text(encoding="utf-8") if environ and environ.exists() else ""
    env = record["instrument"]["env"].split("=", 1)[1]

    marks = expected_log_steps(bounds["steps"], bounds["log_every"])
    ahead = [one for one in marks if len(rows) < marks.index(one) + 1]
    running = elapsed_since(started_at, now)
    deadline = (
        None
        if not ahead
        else bounds["load_allowance_seconds"] + ahead[0] * bounds["binding_seconds_per_step"]
    )

    if seen["out_of_memory"]:
        verdict, outcome = "KILL", "OOM"
    elif seen["traceback"]:
        verdict, outcome = "KILL", "OTHER"
    elif run.get("steps", 0) >= bounds["steps"]:
        verdict, outcome = "GO", "SURVIVED"
    elif deadline is not None and running > deadline:
        verdict = "KILL"
        outcome = "SURVIVED_NO_RATE" if rows else "UNRESOLVED"
    else:
        verdict, outcome = "WAIT", None

    answer = {
        "question": record["question"],
        "env": record["instrument"]["env"],
        "outcome": outcome,
        "what_it_means": None if outcome is None else record["outcomes"][outcome],
        "the_env_var_reached_the_training_process": bool(proof) and env in proof,
        "environ_proof": rel(environ) if environ and environ.exists() else None,
        "optimizer_steps_logged": None if not rows else int(rows[-1]["step"]),
        "seconds_per_step_whole_loop": run.get("seconds_per_step"),
        "seconds_per_step_step_5_line": next(
            (round(float(one["seconds_per_step"]), 3) for one in rows if int(one["step"]) == 5),
            None,
        ),
        "gpu_gb_peak": run.get("gpu_gb_peak"),
        "micro_batch_final": run.get("micro_batch_final"),
        "grad_accum_final": run.get("grad_accum_final"),
        "the_two_rates_are_not_averaged": rung(record, 3)["the_step_6_line_is_not_a_rate"],
    }
    gate = {
        "rung": 3,
        "started_at": started_at,
        "running_seconds": round(running, 1),
        "loss_lines_expected_at_steps": marks,
        "loss_lines_seen": len(rows),
        "next_line_due_by_seconds_into_the_smoke": None if deadline is None else round(deadline, 1),
        **bounds,
        **seen,
        "answer": answer,
        "verdict": verdict,
        "rule": rung(record, 3)["rule"],
        "next_step": (
            "SURVIVED — pull loss.jsonl, provenance.json and the environ proof, discard the adapter"
            " ON the pod, delete, prove it by listing"
            if verdict == "GO"
            else "keep copying the log back; the loss log only appears at step 5"
            if verdict == "WAIT"
            else "KILL and STOP: pull the log (and the two files if they exist), discard the"
            " adapter, delete, prove it by listing, --close-pod, report"
        ),
        **sibling.clock(record, state, now),
    }
    if verdict != "WAIT":
        state["answer"] = answer
    return gate


def main(argv: list[str] | None = None, now: datetime | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    with the_gate_reads_the_probe():
        record = sibling.registration()

        if "--open" in argv:
            code = sibling.main(argv, now)
            if code != GO:
                return code
            peek = argparse.ArgumentParser(add_help=False)
            peek.add_argument("--usd-per-hour", type=float)
            known, _ = peek.parse_known_args(argv)
            print(
                json.dumps(
                    the_hard_stop_is_solved_at_the_observed_price(record, known.usd_per_hour),
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
            )
            return code

        if "--smoke" not in argv:
            return sibling.main(argv, now)

        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--smoke", action="store_true", help="rung 3, the whole probe")
        parser.add_argument("--started-at", required=True, help="when the trainer was launched")
        parser.add_argument("--log", type=Path, required=True, help="the pod's stdout, copied back")
        parser.add_argument("--loss", type=Path, help="<out>/loss.jsonl — absent on the OOM path")
        parser.add_argument("--provenance", type=Path, help="<out>/provenance.json — same")
        parser.add_argument("--environ", type=Path, help="the training process's own environment")
        args = parser.parse_args(argv)

        state = sibling.state_now()
        gate = smoke_gate(
            record,
            state,
            args.started_at,
            args.log,
            args.loss,
            args.provenance,
            args.environ,
            now,
        )
        sibling.append_gate(state, gate, "smoke")
        sibling.save(state)
        return show(gate)


if __name__ == "__main__":
    raise SystemExit(main())
