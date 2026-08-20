#!/usr/bin/env python3
"""lora-b — the Mac half of the ONE paid session: the cumulative clock and every rung, executable.

`results/prereg_lora_b.json` is the law. Every threshold below is READ out of it and none is typed
here — a gate whose number lives in two files is a gate that goes green after one of them moves
([[preregistration_is_a_file_not_a_constant]]).

**The clock is CUMULATIVE (D3a rung 7).** A pod bills for existing, an attempt may own more than one
pod, and every budget check here counts across ALL of them. `--open` stamps the next pod's
`--terminate-after` at that pod's own create plus the hard stop LESS what every closed pod already
billed, so two pods cannot each be handed a fresh window. The stamp is read off this instrument and
never typed ([[a_budget_is_not_an_elapsed]]).

**Exit codes ARE the rule** — 0 GO, 2 KILL/STOP, 3 WAIT — because a deadline a human has to eyeball
is a deadline that gets discovered in a bill.

    PYTHONPATH=src python3.11 scripts/gate_lora_b.py --pre-create-check
    PYTHONPATH=src python3.11 scripts/gate_lora_b.py --open --pod-id <ID> \\
        --created-at <UTC ISO8601> --usd-per-hour <costPerHr> --card '<the card>' \\
        --terminate-after '<the stamp `pod create` was actually given>'
    PYTHONPATH=src python3.11 scripts/gate_lora_b.py --gate0 [--ssh-ok]
    PYTHONPATH=src python3.11 scripts/gate_lora_b.py --boot [--training-started-at <UTC ISO8601>]
    PYTHONPATH=src python3.11 scripts/gate_lora_b.py --train --arm a --loss results/lora_b_arm_a_loss.jsonl
    PYTHONPATH=src python3.11 scripts/gate_lora_b.py --milestone --reading <USD>
    PYTHONPATH=src python3.11 scripts/gate_lora_b.py --smoke --arm a --replies results/lora_b_smoke_a.jsonl
    PYTHONPATH=src python3.11 scripts/gate_lora_b.py --recreate-check --reading <USD> --arms-left b
    PYTHONPATH=src python3.11 scripts/gate_lora_b.py --clock
    PYTHONPATH=src python3.11 scripts/gate_lora_b.py --close-pod --deleted-at <UTC ISO8601> \\
        --outcome '<why this pod ended>'
"""

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import read_threads_reader_v4 as v4  # noqa: E402

from market_pulse import prompts  # noqa: E402

PHASE = "lora-b"
PREREG = REPO_ROOT / "results" / "prereg_lora_b.json"
SMOKE_PACK = REPO_ROOT / "results" / "lora_b_smoke_pack.json"
RECORD = REPO_ROOT / "results" / "lora_b_run.json"

GO, KILL, WAIT = 0, 2, 3

rel = v4.rel
stamp = v4.stamp
elapsed_since = v4.elapsed_since
rate_of = v4.rate_of


def registration() -> dict:
    """The pre-registration, refused unless it is committed AND equal to what is committed.

    A plan that is untracked is not a pre-registration, and a plan that differs from HEAD is one
    somebody could still edit once the numbers are in. The git clock is what proves the plan
    predates the money; this is what proves the plan the gates read is that one.
    """
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(PREREG)], cwd=REPO_ROOT, capture_output=True
    )
    if tracked.returncode != 0:
        raise SystemExit(
            f"{rel(PREREG)} is not tracked by git. Until it is committed, nothing stops it being"
            " rewritten once the numbers are in — commit it BEFORE `pod create`."
        )
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", str(PREREG)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if dirty.stdout.strip():
        raise SystemExit(
            f"{rel(PREREG)} differs from HEAD: {dirty.stdout.strip()}. The gates would then read a"
            " registration nobody committed. Stop and report."
        )
    return json.loads(PREREG.read_text(encoding="utf-8"))


def rung(record: dict, number: int) -> dict:
    for one in record["kill_clock"]:
        if int(one["rung"]) == number:
            return one
    raise SystemExit(f"the registration has no kill-clock rung {number} — stop and report.")


def first_number(text: str) -> float:
    """The one number inside a registered rule, so a threshold is never typed twice.

    The rules this reads each carry exactly one figure — 180 s, 450 s, 122 s, $2.50 — and reading it
    out of the registration is what keeps the gate and the record from drifting apart
    ([[preregistration_is_a_file_not_a_constant]])."""
    digits = "".join(one if one.isdigit() or one == "." else " " for one in text).split()
    if not digits:
        raise SystemExit(f"no number to read out of {text!r} — stop and report.")
    return float(digits[0])


def run_state() -> dict:
    if not RECORD.exists():
        raise SystemExit(
            f"{rel(RECORD)} does not exist — no pod of this attempt was opened with --open. A pod"
            " that exists against no counter is a pod nothing is measuring."
        )
    return json.loads(RECORD.read_text(encoding="utf-8"))


def save(state: dict) -> None:
    RECORD.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def append_gate(state: dict, gate: dict, kind: str) -> dict:
    """Every snapshot APPENDED, none overwritten, and every one stamped with its pod.

    A list cannot lose a reading, and with several pods in one attempt a snapshot also has to say
    which pod it came off ([[gate_verdicts_need_an_artifact]]).
    """
    pod = state["pods"][-1] if state.get("pods") else {}
    state.setdefault("gates", []).append(
        {
            "kind": kind,
            "at": datetime.now(UTC).isoformat(timespec="seconds"),
            "pod": len(state.get("pods", [])),
            "pod_id": pod.get("pod_id"),
            **gate,
        }
    )
    state["latest"] = {"kind": kind, "verdict": gate["verdict"], "pod": len(state.get("pods", []))}
    save(state)
    return state


def billed_before(state: dict) -> tuple[float, float]:
    """What every CLOSED pod billed: seconds, and dollars at each pod's OWN price.

    Never a balance delta — that prices the account and not the leg
    ([[a_balance_delta_is_not_a_per_leg_cost]]). The live pod is not counted here; its seconds are
    the `elapsed` the gates measure.
    """
    closed = [one for one in state.get("pods", []) if one.get("deleted_at")]
    return (
        sum(float(one["billed_seconds"]) for one in closed),
        sum(float(one["billed_usd"]) for one in closed),
    )


def live_pod(state: dict) -> dict | None:
    pods = state.get("pods") or []
    return pods[-1] if pods and not pods[-1].get("deleted_at") else None


def clock(record: dict, state: dict, now: datetime | None = None) -> dict:
    """The attempt's accounting on ONE axis, with every field named for what it measures.

    `elapsed_on_this_pod_seconds` is this pod's; everything called `cumulative` is the attempt's.
    Those are two axes and one name for both is unreadable a day later
    ([[id_spaces_that_look_comparable]]).
    """
    sums = record["money"]["arithmetic"]["cumulative"]
    cap = float(record["money"]["cap_usd_all_in"])
    stop = float(sums["hard_stop_seconds"])
    seconds_before, usd_before = billed_before(state)
    pod = live_pod(state)
    elapsed = 0.0 if pod is None else elapsed_since(pod["created_at"], now)
    rate = 0.0 if pod is None else rate_of(pod)
    spent = usd_before + elapsed * rate
    return {
        "pods_opened": len(state.get("pods", [])),
        "pod_is_live": pod is not None,
        "usd_per_hour": None if pod is None else float(pod["usd_per_hour"]),
        "billed_seconds_closed_pods": round(seconds_before, 1),
        "spent_closed_pods_usd": round(usd_before, 6),
        "elapsed_on_this_pod_seconds": round(elapsed, 1),
        "spent_this_pod_usd": round(elapsed * rate, 6),
        "cumulative_billed_seconds": round(seconds_before + elapsed, 1),
        "cumulative_spent_usd": round(spent, 6),
        "hard_stop_seconds": stop,
        "cumulative_seconds_left": round(stop - seconds_before - elapsed, 1),
        "cap_usd_all_in": cap,
        "cap_left_usd": round(cap - spent, 6),
        "reading_rule": (
            "these are the CLOCK's numbers. The rungs that name a guard reading act on"
            " `scripts/runpod_guard.py`'s reading and never on this projection"
        ),
    }


BACKSTOP_TOLERANCE_SECONDS = 60.0
"""How far the stamp actually given to `pod create` may sit BEYOND the computed one. Rounding the
window down is always safe — it shortens it — so only overshoot is bounded, and it is bounded at a
minute of clock slop rather than left to judgement."""


def terminate_after(record: dict, state: dict, created_at: str, given: str) -> dict:
    """This pod's backstop stamp: its own create plus what the hard stop has LEFT — and a CHECK.

    Not a fresh window per pod: that is the defect rung 7 exists for, and two pods each stamped
    «create + 5.5 h» bill eleven hours against a stop that says five and a half.

    The stamp that was actually handed to `pod create` is a REQUIRED argument, because rung 7 is
    enforced by a platform flag this instrument cannot read back. Recomputing the right answer after
    the pod exists and never comparing it to the one the platform got is a guard built and then
    bypassed — so the caller has to SAY the value, and a window longer than the hard stop allows is
    a refusal ([[the_guard_you_built_and_then_bypassed]]).
    """
    stop = float(record["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"])
    seconds_before, _ = billed_before(state)
    left = stop - seconds_before
    if left <= 0:
        raise SystemExit(
            f"the closed pods have already billed {seconds_before:.0f} s of the"
            f" {stop:.0f} s hard stop. There is no window left to create a pod in — STOP."
        )
    computed = stamp(created_at) + timedelta(seconds=left)
    overshoot = (stamp(given) - computed).total_seconds()
    if overshoot > BACKSTOP_TOLERANCE_SECONDS:
        raise SystemExit(
            f"--terminate-after was given as {given}, which is {overshoot:.0f} s beyond the"
            f" {computed.isoformat(timespec='seconds')} the cumulative hard stop allows this pod"
            f" ({left:.0f} s of {stop:.0f}, {seconds_before:.0f} already billed). DELETE the pod and"
            " re-create it with the computed stamp — rung 7 is enforced by that flag and by nothing"
            " else."
        )
    return {
        "computed": computed.isoformat(timespec="seconds"),
        "given": given,
        "window_seconds": round(left, 1),
        "overshoot_seconds": round(overshoot, 1),
        "billed_by_closed_pods_seconds": round(seconds_before, 1),
    }


def gate_zero(record: dict, state: dict, elapsed: float, ssh_ok: bool, now=None) -> dict:
    """Rung 2 — the ssh dead-man, on THIS pod's own create-elapsed."""
    rule = rung(record, 2)["rule"]
    threshold = first_number(rule)
    verdict = "GO" if ssh_ok else ("KILL" if elapsed >= threshold else "WAIT")
    return {
        "rung": 2,
        "elapsed_on_this_pod_seconds": round(elapsed, 1),
        "threshold_seconds": threshold,
        "seconds_left": round(threshold - elapsed, 1),
        "ssh_endpoint_answered": ssh_ok,
        "verdict": verdict,
        "rule": rule,
        "next_step": (
            "stage, then launch arm A"
            if verdict == "GO"
            else "keep polling `runpodctl ssh info` at 3-4 s"
            if verdict == "WAIT"
            else "delete, prove it by listing, --close-pod, then --recreate-check before any replacement"
        ),
        **clock(record, state, now),
    }


def gate_boot(record: dict, state: dict, elapsed: float, training_at: str | None, now=None) -> dict:
    """Rung 3 — boot to the FIRST optimizer step, on this pod's create-elapsed.

    Three outcomes and not two: WAIT while the deadline is still ahead and nothing has started, GO
    when the first step logged inside it, KILL when the clock passed it. A gate with only GO and
    KILL would kill every poll taken before the model finished loading.
    """
    rule = rung(record, 3)["rule"]
    threshold = first_number(rule)
    at = None if training_at is None else round(elapsed_since_create(state, training_at), 1)
    verdict = (
        "GO" if at is not None and at <= threshold else "KILL" if elapsed >= threshold else "WAIT"
    )
    return {
        "rung": 3,
        "elapsed_on_this_pod_seconds": round(elapsed, 1),
        "training_started_at_create_elapsed_seconds": at,
        "threshold_seconds": threshold,
        "seconds_left": round(threshold - elapsed, 1),
        "verdict": verdict,
        "rule": rule,
        "next_step": (
            "arm A is training — poll --train at every log line"
            if verdict == "GO"
            else "keep watching the pod log for the first optimizer step"
            if verdict == "WAIT"
            else "KILL: delete, prove it by listing, --close-pod"
        ),
        **clock(record, state, now),
    }


def elapsed_since_create(state: dict, when: str) -> float:
    return (stamp(when) - stamp(state["pods"][-1]["created_at"])).total_seconds()


def log_lines(path: Path) -> list[dict]:
    """The trainer's own loss lines, copied back from the pod. A torn last line is DROPPED.

    The copy is taken while the pod is still appending, so its final line can be half written. It is
    dropped rather than refused: this reader runs on the kill path and a `JSONDecodeError` there
    would turn a slow run into a crashed gate ([[the_hardening_did_not_reach_the_sibling_reader]]).
    """
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
                    f"{rel(path)} line {index + 1} is not JSON and it is not the last one. That is"
                    " a damaged file, not the mid-write race — stop and report."
                ) from None
    return rows


def measured_step(rows: list[dict]) -> float:
    """The s/step the remaining steps are priced at: the LARGER of the mean so far and the last.

    The mean is the run's own cumulative rate and the last line is where it is heading; taking the
    larger prices a run that is degrading at what it is degrading TO. A projection built on the best
    of the readings is a projection that has already spent its margin.
    """
    seen = [float(one["seconds_per_step"]) for one in rows if one.get("seconds_per_step")]
    if not seen:
        raise SystemExit("no log line carries seconds_per_step — there is nothing measured yet")
    return max(sum(seen) / len(seen), seen[-1])


def watchdog(record: dict, rows: list[dict]) -> dict:
    """Rung 4 — s/step over the threshold across 5 CONSECUTIVE log lines."""
    rule = rung(record, 4)["rule"]
    threshold = first_number(rule)
    window = [float(one["seconds_per_step"]) for one in rows if one.get("seconds_per_step")][-5:]
    over = len(window) == 5 and all(one > threshold for one in window)
    return {
        "threshold_seconds_per_step": threshold,
        "last_five": [round(one, 2) for one in window],
        "consecutive_over": over,
        "verdict": "KILL" if over else "GO",
        "rule": rule,
    }


def projection(record: dict, state: dict, arm: str, rows: list[dict], now=None) -> dict:
    """Rung 8 — the projected attempt total at the MEASURED rate, against BOTH bounds.

    Two deviations from the contract's letter, registered in the record and repeated here because
    this is where they act: arm B's leg is priced at the rate the pod is ACTUALLY running (the
    larger of the fitted seconds and the measured), and the projection is measured against the
    cumulative hard stop as well as the cap. Both can only close runs the letter would open, and
    without them the rung does not close the compliant-slow path it was written for.
    """
    sums = record["money"]["arithmetic"]
    gate = sums["cumulative"]["projection_gate"]
    now_clock = clock(record, state, now)
    pod = live_pod(state)
    if pod is None:
        raise SystemExit("no pod is live — there is nothing to project")
    rate = rate_of(pod)
    steps = {key: int(value) for key, value in sums["steps"].items()}
    done = max((int(one["step"]) for one in rows if one.get("step")), default=0)
    measured = measured_step(rows)
    remaining = max(0, steps[arm] - done) * measured
    leg = 0.0 if arm == "b" else max(float(sums["train_seconds"]["b"]), steps["b"] * measured)
    ahead = remaining + leg + float(gate["eval_seconds"]) + float(gate["overhead_seconds"])
    projected_seconds = now_clock["cumulative_billed_seconds"] + ahead
    projected_usd = (
        now_clock["spent_closed_pods_usd"]
        + (now_clock["elapsed_on_this_pod_seconds"] + ahead) * rate
    )
    over_cap = projected_usd > now_clock["cap_usd_all_in"]
    over_stop = projected_seconds > now_clock["hard_stop_seconds"]
    return {
        "rung": 8,
        "arm": arm,
        "steps_done": done,
        "steps_remaining": max(0, steps[arm] - done),
        "measured_seconds_per_step": round(measured, 3),
        "seconds_remaining_this_arm": round(remaining, 1),
        "arm_b_leg_seconds": round(leg, 1),
        "eval_seconds": float(gate["eval_seconds"]),
        "overhead_seconds": float(gate["overhead_seconds"]),
        "projected_seconds": round(projected_seconds, 1),
        "projected_hours": round(projected_seconds / 3600, 4),
        "projected_usd": round(projected_usd, 4),
        "over_the_cap": over_cap,
        "over_the_hard_stop": over_stop,
        "verdict": "KILL" if over_cap or over_stop else "GO",
        "formula": gate["formula"],
        "next_step": (
            "KILL: delete the pod, prove it by listing, and the prereg's arm-A-only branch applies"
            if over_cap or over_stop
            else "continue; re-run at the next log line"
        ),
        **now_clock,
    }


def milestone(record: dict, state: dict, reading: float, now=None) -> dict:
    """Rung 5 — the guard READING after arm A, never a projection."""
    rule = rung(record, 5)["rule"]
    threshold = first_number(rule)
    return {
        "rung": 5,
        "guard_reading_usd": reading,
        "threshold_usd": threshold,
        "verdict": "GO" if reading <= threshold else "STOP",
        "rule": rule,
        "next_step": (
            "arm B may start"
            if reading <= threshold
            else "arm B does NOT start; the session closes with arm A"
        ),
        **clock(record, state, now),
    }


def recreate_check(
    record: dict, state: dict, reading: float, arms_left: list[str], now=None
) -> dict:
    """Rung 9 — the ONE allowed re-creation, priced at MEASURED rates before it is created.

    The reading is the meter and the remaining is the forecast; the rung acts on their sum. The
    worst case charged is a full boot at the registered ceiling, every arm still owed re-trained
    from step 0 (there is no mid-arm checkpoint — the registration says so), the eval for every
    adapter that will exist, and the registered overhead.
    """
    sums = record["money"]["arithmetic"]
    gate = sums["cumulative"]["projection_gate"]
    cap = float(record["money"]["cap_usd_all_in"])
    steps = {key: int(value) for key, value in sums["steps"].items()}
    measured = float(state.get("measured_seconds_per_step") or sums["seconds_per_step"])
    trained = [one for one in sorted(steps) if one not in arms_left]
    adapters = min(2, len(trained) + len(arms_left))
    seconds = (
        float(sums["boot_seconds_charged"])
        + sum(steps[one] * measured for one in arms_left)
        + adapters / 2 * float(gate["eval_seconds"])
        + float(gate["overhead_seconds"])
    )
    pod = live_pod(state)
    rate = (
        rate_of(pod)
        if pod
        else float(record["money"]["meter"]["worked_example_usd_per_hour"]) / 3600
    )
    total = reading + seconds * rate
    stop = float(sums["cumulative"]["hard_stop_seconds"])
    billed, _ = billed_before(state)
    return {
        "rung": 9,
        "guard_reading_usd": reading,
        "arms_left": arms_left,
        "measured_seconds_per_step": round(measured, 3),
        "worst_case_remaining_seconds": round(seconds, 1),
        "worst_case_remaining_usd": round(seconds * rate, 4),
        "reading_plus_remaining_usd": round(total, 4),
        "cap_usd_all_in": cap,
        "cumulative_seconds_after_it": round(billed + seconds, 1),
        "hard_stop_seconds": stop,
        "verdict": "GO" if total <= cap and billed + seconds <= stop else "STOP",
        "rule": sums["cumulative"]["recreation_budget_check"],
        "next_step": (
            "the ONE re-creation is affordable; --pre-create-check, then create"
            if total <= cap and billed + seconds <= stop
            else "the session closes with what exists"
        ),
    }


def smoke(record: dict, state: dict, arm: str, replies: Path, now=None) -> dict:
    """Rung 10 — one TRAINING-row reply per arm, and it must be one balanced four-key object.

    A transport-format check and NOT a bar peek: the row is asserted outside the sealed fourteen and
    the eval pack by the producer that built the pack, and this reads the same assertion back. The
    attempt is spent at the first GOLD-row reply generated, and no gold row is in this file.
    """
    pack = json.loads(SMOKE_PACK.read_text(encoding="utf-8"))
    item = pack["items"][0]
    barred = {int(one["msg_id"]) for one in record["population"]["gold"]["rows"]}
    if int(item["msg_id"]) in barred:
        raise SystemExit(
            f"{item['id']} is a gold row. This is not a smoke, it is a peek at the bar — stop."
        )
    rows = [json.loads(line) for line in replies.read_text(encoding="utf-8").splitlines() if line]
    row = next((one for one in rows if one["id"] == item["id"]), None)
    parsed, failure = None, None
    if row is None:
        failure = "no reply for the smoke row landed in the file"
    elif row.get("rendering_sha256") != item["rendering_sha256"]:
        failure = "the pod answered a request whose sha is not the pack's"
    elif not row.get("balanced"):
        failure = "the reply never closed a top-level object"
    else:
        try:
            parsed = prompts.parse_pass1(row["reply"], msg_id=int(item["msg_id"]))
        except Exception as err:  # the parser's own refusal, whatever it names itself
            failure = f"{type(err).__name__}: {err}"
    return {
        "rung": 10,
        "arm": arm,
        "row": item["id"],
        "replies": rel(replies),
        "balanced": bool(row and row.get("balanced")),
        "parsed_keys": None if parsed is None else sorted(parsed),
        "failure": failure,
        "verdict": "GO" if failure is None else "KILL",
        "rule": record["money"]["arithmetic"]["cumulative"]["format_smoke"]["rule"],
        "next_step": (
            f"arm {arm} may be evaluated — and the attempt is SPENT at its first gold-row reply"
            if failure is None
            else f"arm {arm} is NOT evaluated. If no arm passes, the session closes and the attempt"
            " is NOT spent"
        ),
        **clock(record, state, now),
    }


def show(gate: dict) -> int:
    print(json.dumps(gate, ensure_ascii=False, indent=2, sort_keys=True))
    verdict = gate["verdict"]
    print(f"\n{verdict}  ·  {gate.get('next_step', '')}")
    return {"GO": GO, "WAIT": WAIT}.get(verdict, KILL)


def main(argv: list[str] | None = None, now: datetime | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pre-create-check", action="store_true", help="never two billing endpoints"
    )
    parser.add_argument("--open", action="store_true", help="record a pod and print its deadlines")
    parser.add_argument("--pod-id")
    parser.add_argument("--created-at", help="the create response's stamp — the meter's zero")
    parser.add_argument("--usd-per-hour", type=float, help="costPerHr, read back from create")
    parser.add_argument("--card", help="the card the create response actually gave")
    parser.add_argument(
        "--terminate-after",
        help="the backstop stamp ACTUALLY handed to `pod create` — checked against the cumulative"
        " hard stop and refused if the window is longer than rung 7 allows",
    )
    parser.add_argument("--gate0", action="store_true", help="rung 2, the ssh dead-man")
    parser.add_argument("--ssh-ok", action="store_true", help="the endpoint answered")
    parser.add_argument("--boot", action="store_true", help="rung 3, boot to the first step")
    parser.add_argument("--training-started-at", help="when the first optimizer step logged")
    parser.add_argument("--train", action="store_true", help="rungs 4 and 8, on the loss log")
    parser.add_argument("--arm", choices=("a", "b"))
    parser.add_argument("--loss", type=Path, help="the trainer's loss.jsonl, copied back")
    parser.add_argument("--milestone", action="store_true", help="rung 5, on the guard reading")
    parser.add_argument("--reading", type=float, help="the guard's reading in USD")
    parser.add_argument("--recreate-check", action="store_true", help="rung 9")
    parser.add_argument("--arms-left", help="comma-separated arms a re-creation still owes")
    parser.add_argument("--smoke", action="store_true", help="rung 10, the format smoke")
    parser.add_argument("--replies", type=Path, help="the smoke's own out-file")
    parser.add_argument("--clock", action="store_true", help="the cumulative reading, right now")
    parser.add_argument("--close-pod", action="store_true", help="this pod is deleted")
    parser.add_argument("--deleted-at", help="the deletion's stamp — the meter's end")
    parser.add_argument("--outcome", help="why this pod ended")
    args = parser.parse_args(argv)

    record = registration()

    if args.pre_create_check:
        state = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {}
        pod = live_pod(state)
        if pod is not None:
            print(
                f"pod {pod['pod_id']} is OPEN in {rel(RECORD)} and has no deleted_at. Never two"
                " billing endpoints at once — delete it, prove it by listing, and --close-pod first."
            )
            return KILL
        stop = float(record["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"])
        billed, spent = billed_before(state)
        print(
            f"no pod is open · {len(state.get('pods', []))} closed, {billed:.0f} s"
            f" = ${spent:.4f} billed · the hard stop leaves {stop - billed:.0f} s"
            f" for the next pod's --terminate-after"
        )
        return GO if billed < stop else KILL

    if args.open:
        for name in ("pod_id", "created_at", "usd_per_hour", "card", "terminate_after"):
            if getattr(args, name) is None:
                parser.error(f"--open needs --{name.replace('_', '-')}")
        state = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {"pods": []}
        if live_pod(state) is not None:
            raise SystemExit(
                f"pod {live_pod(state)['pod_id']} is still open in {rel(RECORD)}. Never two billing"
                " endpoints at once — close it with --close-pod first."
            )
        ceiling = float(record["money"]["meter"]["worked_example_usd_per_hour"])
        backstop = terminate_after(record, state, args.created_at, args.terminate_after)
        state.setdefault("pods", []).append(
            {
                "pod_id": args.pod_id,
                "created_at": args.created_at,
                "usd_per_hour": args.usd_per_hour,
                "card": args.card,
                "terminate_after": backstop["given"],
                "terminate_after_computed": backstop["computed"],
            }
        )
        save(state)
        gate = {
            "rung": 1,
            "usd_per_hour": args.usd_per_hour,
            "price_ceiling_usd_per_hour": ceiling,
            "card": args.card,
            "backstop": backstop,
            "terminate_after_rule": rung(record, 7)["rule"],
            "verdict": "GO" if args.usd_per_hour <= ceiling else "KILL",
            "rule": rung(record, 1)["rule"],
            "next_step": (
                "the backstop the platform holds is inside the cumulative stop; poll --gate0"
                if args.usd_per_hour <= ceiling
                else "DELETE the pod now and STOP — no generation, no training"
            ),
            **clock(record, state, now),
        }
        append_gate(state, gate, "price")
        return show(gate)

    state = run_state()

    if args.clock:
        reading = clock(record, state, now)
        print(json.dumps(reading, ensure_ascii=False, indent=2, sort_keys=True))
        return GO

    if args.gate0:
        pod = live_pod(state)
        if pod is None:
            raise SystemExit("no pod is live — --gate0 has nothing to measure")
        gate = gate_zero(record, state, elapsed_since(pod["created_at"], now), args.ssh_ok, now)
        append_gate(state, gate, "gate0")
        return show(gate)

    if args.boot:
        pod = live_pod(state)
        if pod is None:
            raise SystemExit("no pod is live — --boot has nothing to measure")
        gate = gate_boot(
            record, state, elapsed_since(pod["created_at"], now), args.training_started_at, now
        )
        append_gate(state, gate, "boot")
        return show(gate)

    if args.train:
        if not args.arm or not args.loss:
            parser.error("--train needs --arm and --loss")
        rows = log_lines(args.loss)
        if not rows:
            print(f"{rel(args.loss)} carries no log line yet — WAIT and copy it back again")
            return WAIT
        dog = watchdog(record, rows)
        gate = projection(record, state, args.arm, rows, now)
        gate["watchdog"] = dog
        if dog["verdict"] == "KILL":
            gate["verdict"] = "KILL"
            gate["next_step"] = "KILL on rung 4: five consecutive log lines over the watchdog"
        state["measured_seconds_per_step"] = gate["measured_seconds_per_step"]
        append_gate(state, gate, f"train-{args.arm}")
        return show(gate)

    if args.milestone:
        if args.reading is None:
            parser.error("--milestone needs --reading, and it is the guard's number")
        gate = milestone(record, state, args.reading, now)
        append_gate(state, gate, "milestone")
        return show(gate)

    if args.recreate_check:
        if args.reading is None or not args.arms_left:
            parser.error("--recreate-check needs --reading and --arms-left")
        gate = recreate_check(
            record, state, args.reading, [one for one in args.arms_left.split(",") if one], now
        )
        append_gate(state, gate, "recreate")
        return show(gate)

    if args.smoke:
        if not args.arm or not args.replies:
            parser.error("--smoke needs --arm and --replies")
        gate = smoke(record, state, args.arm, args.replies, now)
        append_gate(state, gate, f"smoke-{args.arm}")
        return show(gate)

    if args.close_pod:
        if not args.deleted_at:
            parser.error("--close-pod needs --deleted-at: this pod's billed end")
        pod = live_pod(state)
        if pod is None:
            raise SystemExit("no pod is open — there is nothing to close")
        billed = (stamp(args.deleted_at) - stamp(pod["created_at"])).total_seconds()
        pod["deleted_at"] = args.deleted_at
        pod["billed_seconds"] = round(billed, 1)
        pod["billed_usd"] = round(billed * rate_of(pod), 6)
        pod["outcome"] = args.outcome
        save(state)
        gate = {
            "billed_seconds": pod["billed_seconds"],
            "billed_usd": pod["billed_usd"],
            "outcome": args.outcome,
            "verdict": "GO",
            "next_step": "prove the deletion by LISTING, with the volume as the positive control",
            **clock(record, state, now),
        }
        append_gate(state, gate, "close-pod")
        return show(gate)

    parser.error(
        "one of --pre-create-check / --open / --gate0 / --boot / --train / --milestone /"
        " --recreate-check / --smoke / --clock / --close-pod"
    )
    return KILL


if __name__ == "__main__":
    raise SystemExit(main())
