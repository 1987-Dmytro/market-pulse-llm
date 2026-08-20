#!/usr/bin/env python3
"""pass1-fewshot — the Mac half of the ONE paid session: every rung, and the loop that HOLDS them.

`results/prereg_pass1_fewshot.json` is the law. Every threshold below is READ out of it and none is
typed here — a gate whose number lives in two files goes green after one of them moves
([[preregistration_is_a_file_not_a_constant]]).

**`--watch` is why this contract exists in this shape.** lora-b's arm A finished at 14:38Z and was
found at 17:20Z: 9 720 seconds of billed idle, $1.43, and the arm B that never ran. Every rung of
that registration read the training log, so every one of them went quiet when the log stopped
growing — no rung watched a pod that had STOPPED working ([[no_rung_watches_an_idle_pod]]). Here the
liveness rung is a blocking loop the executor stays inside for the whole generation: it copies the
out-files and the pod log back, and it KILLS when no new row and no new log line have appeared for
the registered deadline, measured from the LAST event and never from create.

**Exit codes ARE the rule** — 0 GO, 2 KILL/STOP, 3 WAIT — because a deadline a human has to eyeball
is a deadline that gets discovered in a bill.

    PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --pre-create-check
    PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --price --pod-id <ID> \\
        --created-at <UTC ISO8601> --usd-per-hour <costPerHr> --card '<the card>' \\
        --terminate-after '<the stamp `pod create` was actually given>'
    PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --gate0 [--ssh-ok]
    PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --boot [--first-reply-at <UTC ISO8601>]
    PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --watch --pack results/pass1_dev_pack.json \\
        --ssh root@<HOST> --ssh-port <PORT>
    PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --projection --pack results/pass1_dev_pack.json
    PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --dev-gate
    PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --close --deleted-at <UTC ISO8601> \\
        --outcome '<why this pod ended>'
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import read_threads_reader_v4 as v4  # noqa: E402
import score_reader_probe_b as probe_b  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import prompts, scorer  # noqa: E402

PHASE = "pass1-fewshot"
PREREG = REPO_ROOT / "results" / "prereg_pass1_fewshot.json"
RECORD = REPO_ROOT / "results" / "pass1_fewshot_run.json"
DEV_PACK = REPO_ROOT / "results" / "pass1_dev_pack.json"
LABELS = (
    REPO_ROOT / "results" / "labels_pass1_r1.jsonl",
    REPO_ROOT / "results" / "labels_pass1_r2.jsonl",
)
POD_LOG = REPO_ROOT / "results" / "pass1_fewshot_pod.log"

GO, KILL, WAIT = 0, 2, 3

rel = v4.rel
stamp = v4.stamp
elapsed_since = v4.elapsed_since
rate_of = v4.rate_of

SSH_OPTIONS = (
    "-o",
    "StrictHostKeyChecking=no",
    "-o",
    "UserKnownHostsFile=/dev/null",
    "-o",
    "LogLevel=ERROR",
)
SSH_KEY = Path.home() / ".runpod" / "ssh" / "runpodctl-ssh-key"


def registration() -> dict:
    """The pre-registration, refused unless it is committed AND equal to what is committed."""
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
    """The one number inside a registered rule, so a threshold is never typed twice."""
    digits = "".join(one if one.isdigit() or one == "." else " " for one in text).split()
    if not digits:
        raise SystemExit(f"no number to read out of {text!r} — stop and report.")
    return float(digits[0])


def run_state() -> dict:
    if not RECORD.exists():
        raise SystemExit(
            f"{rel(RECORD)} does not exist — no pod of this attempt was opened with --price. A pod"
            " that exists against no counter is a pod nothing is measuring."
        )
    return json.loads(RECORD.read_text(encoding="utf-8"))


def save(state: dict) -> None:
    RECORD.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def append_gate(state: dict, gate: dict, kind: str) -> dict:
    """Every snapshot APPENDED, none overwritten, and every one stamped with its pod."""
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
    """What every CLOSED pod billed: seconds, and dollars at each pod's OWN price."""
    closed = [one for one in state.get("pods", []) if one.get("deleted_at")]
    return (
        sum(float(one["billed_seconds"]) for one in closed),
        sum(float(one["billed_usd"]) for one in closed),
    )


def live_pod(state: dict) -> dict | None:
    pods = state.get("pods") or []
    return pods[-1] if pods and not pods[-1].get("deleted_at") else None


def clock(record: dict, state: dict, now: datetime | None = None) -> dict:
    """The attempt's accounting on ONE axis, with every field named for what it measures."""
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
window down is always safe — it shortens it — so only overshoot is bounded."""


def terminate_after(record: dict, state: dict, created_at: str, given: str) -> dict:
    """This pod's backstop stamp: its own create plus what the hard stop has LEFT — and a CHECK.

    The stamp handed to `pod create` is a REQUIRED argument, because rung 6 is enforced by a
    platform flag this instrument cannot read back. Recomputing the right answer after the pod
    exists and never comparing it to the one the platform got is a guard built and then bypassed
    ([[the_guard_you_built_and_then_bypassed]]).
    """
    stop = float(record["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"])
    seconds_before, _ = billed_before(state)
    left = stop - seconds_before
    if left <= 0:
        raise SystemExit(
            f"the closed pods have already billed {seconds_before:.0f} s of the {stop:.0f} s hard"
            " stop. There is no window left to create a pod in — STOP."
        )
    computed = stamp(created_at) + timedelta(seconds=left)
    overshoot = (stamp(given) - computed).total_seconds()
    if overshoot > BACKSTOP_TOLERANCE_SECONDS:
        raise SystemExit(
            f"--terminate-after was given as {given}, which is {overshoot:.0f} s beyond the"
            f" {computed.isoformat(timespec='seconds')} the cumulative hard stop allows this pod"
            f" ({left:.0f} s of {stop:.0f}, {seconds_before:.0f} already billed). DELETE the pod and"
            " re-create it with the computed stamp — rung 6 is enforced by that flag and by nothing"
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
            "stage the repo and launch the dev legs"
            if verdict == "GO"
            else "keep polling `runpodctl ssh info` at 3-4 s"
            if verdict == "WAIT"
            else "delete, prove it by listing, --close, and the attempt is NOT spent"
        ),
        **clock(record, state, now),
    }


def gate_boot(record: dict, state: dict, elapsed: float, first_reply: str | None, now=None) -> dict:
    """Rung 3 — boot to the FIRST REPLY, on this pod's create-elapsed. Three outcomes, not two."""
    rule = rung(record, 3)["rule"]
    threshold = first_number(rule)
    at = None if first_reply is None else round(elapsed_since_create(state, first_reply), 1)
    verdict = (
        "GO" if at is not None and at <= threshold else "KILL" if elapsed >= threshold else "WAIT"
    )
    return {
        "rung": 3,
        "elapsed_on_this_pod_seconds": round(elapsed, 1),
        "first_reply_at_create_elapsed_seconds": at,
        "threshold_seconds": threshold,
        "seconds_left": round(threshold - elapsed, 1),
        "verdict": verdict,
        "rule": rule,
        "next_step": (
            "the dev legs are generating — stay inside --watch"
            if verdict == "GO"
            else "keep watching the pod log for the first reply"
            if verdict == "WAIT"
            else "KILL: delete, prove it by listing, --close; the attempt is NOT spent"
        ),
        **clock(record, state, now),
    }


def elapsed_since_create(state: dict, when: str) -> float:
    return (stamp(when) - stamp(state["pods"][-1]["created_at"])).total_seconds()


def rows_of(path: Path) -> list[dict]:
    """A copied-back out-file's whole lines. A torn LAST line is dropped, never refused.

    The copy is taken while the pod is still appending, so its final line can be half written. A
    `JSONDecodeError` on the kill path would turn a slow run into a crashed gate
    ([[the_hardening_did_not_reach_the_sibling_reader]]).
    """
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            if index != len(lines) - 1:
                raise SystemExit(
                    f"{rel(path)} line {index + 1} is not JSON and it is not the last one. That is"
                    " a damaged file, not the mid-write race — stop and report."
                ) from None
    return out


def legs_of(pack: dict) -> list[dict]:
    return [
        {"name": one["name"], "task": one["task"], "out": one["out"], "units": len(one["items"])}
        for one in pack["legs"]
    ]


def leg_state(record: dict, packs: list[dict], where: Path) -> list[dict]:
    """Per leg: how many units it owes, how many are answered, and the s/call it is running at.

    A leg with no reply yet is priced at its REGISTERED rate or at the worst rate measured on this
    pod so far, whichever is larger. Pricing an unstarted leg at a number smaller than what the pod
    is demonstrably doing is the compliant-slow path a projection gate exists to close.
    """
    registered = record["money"]["arithmetic"]["seconds_per_call"]
    out = []
    worst = 0.0
    for pack in packs:
        for one in legs_of(pack):
            rows = rows_of(where / one["out"])
            seen = [float(row["seconds"]) for row in rows if row.get("seconds")]
            measured = max(sum(seen) / len(seen), seen[-1]) if seen else None
            if measured:
                worst = max(worst, measured)
            out.append({**one, "answered": len(rows), "measured_seconds_per_call": measured})
    for one in out:
        floor = float(registered[one["name"]])
        one["seconds_per_call_used"] = round(
            one["measured_seconds_per_call"] or max(floor, worst), 4
        )
        one["rate_source"] = "measured" if one["measured_seconds_per_call"] else "registered"
        one["remaining"] = max(0, one["units"] - one["answered"])
    return out


def projection(record: dict, state: dict, legs: list[dict], now=None) -> dict:
    """Rung 4 — the projected attempt total at MEASURED rates, against BOTH bounds.

    Every leg still owed is priced, not only the one that is running: the shot's 64 calls are the
    reason the dev legs are affordable at all, and a projection that ignored them would open a run
    the cap closes ([[a_negative_pre_generation_budget_is_a_forecast]]).
    """
    sums = record["money"]["arithmetic"]
    gate = sums["cumulative"]["projection_gate"]
    now_clock = clock(record, state, now)
    pod = live_pod(state)
    if pod is None:
        raise SystemExit("no pod is live — there is nothing to project")
    rate = rate_of(pod)
    ahead = sum(one["remaining"] * one["seconds_per_call_used"] for one in legs)
    ahead += float(gate["overhead_seconds"])
    projected_seconds = now_clock["cumulative_billed_seconds"] + ahead
    projected_usd = (
        now_clock["spent_closed_pods_usd"]
        + (now_clock["elapsed_on_this_pod_seconds"] + ahead) * rate
    )
    over_cap = projected_usd > now_clock["cap_usd_all_in"]
    over_stop = projected_seconds > now_clock["hard_stop_seconds"]
    return {
        "rung": 4,
        "legs": legs,
        "calls_answered": sum(one["answered"] for one in legs),
        "calls_remaining": sum(one["remaining"] for one in legs),
        "seconds_remaining": round(ahead - float(gate["overhead_seconds"]), 1),
        "overhead_seconds": float(gate["overhead_seconds"]),
        "projected_seconds": round(projected_seconds, 1),
        "projected_hours": round(projected_seconds / 3600, 4),
        "projected_usd": round(projected_usd, 4),
        "over_the_cap": over_cap,
        "over_the_hard_stop": over_stop,
        "verdict": "KILL" if over_cap or over_stop else "GO",
        "formula": gate["formula"],
        "rule": rung(record, 4)["rule"],
        "next_step": (
            "KILL: delete the pod, prove it by listing, --close. The attempt is spent only if a"
            " gold row was answered"
            if over_cap or over_stop
            else "continue; --watch re-runs this every registered interval"
        ),
        **now_clock,
    }


# --- rung 5: the liveness loop the executor stays inside -------------------------------------------


def scp(target: str, port: int, remote: str, local: Path) -> bool:
    """One file back from the pod. A failed copy is NOT an event and is not fatal.

    A transient scp failure must not delete a working pod, and it must not refresh the deadline
    either: it simply does not advance `last_event`, so a pod that has genuinely stopped is killed
    on the same clock whether the copy is failing or the pod is silent.
    """
    local.parent.mkdir(parents=True, exist_ok=True)
    done = subprocess.run(
        [
            "scp",
            "-i",
            str(SSH_KEY),
            *SSH_OPTIONS,
            "-P",
            str(port),
            f"{target}:{remote}",
            str(local),
        ],
        capture_output=True,
        text=True,
    )
    return done.returncode == 0


def pod_delete(pod_id: str) -> dict:
    """`runpodctl pod delete` — `pod terminate` does not exist. The listing is still the proof."""
    done = subprocess.run(["runpodctl", "pod", "delete", pod_id], capture_output=True, text=True)
    return {
        "command": f"runpodctl pod delete {pod_id}",
        "returncode": done.returncode,
        "stdout": done.stdout.strip(),
        "stderr": done.stderr.strip(),
    }


def boot_is_cleared(state: dict) -> bool:
    """Has rung 3 already gone GO on THIS pod? Then the watch does not re-arm it.

    The shot is a second launch on a pod whose model is already loaded, so its watch starts with
    zero answered rows at an hour of create-elapsed. Re-arming a create-anchored boot ceiling there
    would kill a perfectly healthy pod on its way to the one measurement the session is for.
    """
    pod = len(state.get("pods", []))
    return any(
        one.get("kind") == "boot" and one.get("verdict") == "GO" and one.get("pod") == pod
        for one in state.get("gates", [])
    )


def fingerprint(where: Path, legs: list[dict], log: Path) -> tuple[int, int]:
    """What «an event» is: one more answered row anywhere, or one more line in the pod log."""
    rows = sum(len(rows_of(where / one["out"])) for one in legs)
    lines = len(log.read_text(encoding="utf-8").splitlines()) if log.exists() else 0
    return rows, lines


def watch(
    record: dict,
    state: dict,
    packs: list[dict],
    *,
    where: Path,
    log: Path,
    pull,
    kill,
    sleep=time.sleep,
    now=None,
    clock_now=time.monotonic,
    poll_seconds: float = 20.0,
) -> dict:
    """Rung 5 — BLOCK until every unit is answered, or KILL after the registered idle deadline.

    The deadline is measured from the LAST EVENT and never from create: a pod that is working
    slowly is not the failure this rung exists for, and a pod that has finished and is waiting is.

    **An event is a RISE, and that asymmetry is the whole guard.** The fingerprint is a HIGH-WATER
    mark: `pull` is scp and scp fails, and a failed copy can leave a local file shorter than it was
    a poll ago. Refreshing the deadline on any CHANGE would make a dead pod behind a flapping link
    immortal — N → 0 → N → 0 is four «events» and the deadline never expires — which is precisely
    the state this rung was bought for. A drop is a failed copy, never work.

    Rung 4 is re-run on EVERY poll and not every `every` calls. The registered interval is a floor:
    the projection is a pure computation over local files and costs nothing, while a slowdown that
    starts just after a checkpoint would otherwise run unexamined for twenty more calls — and at a
    degraded rate twenty calls can outlast the hard stop. The cumulative stop is checked directly
    beside it, because a run can leave the window without any leg changing its rate.

    `pull` and `kill` are arguments so the whole loop is driven at $0 on a fake transport: a KILL on
    a frozen out-file, a KILL on one that flaps, and a GO on one that advances are all tests, and a
    liveness rung nobody ever saw fire is a rung nobody has
    ([[guard_selftest_negative_control]]).
    """
    deadline = first_number(rung(record, 5)["rule"])
    every = int(
        first_number(record["money"]["arithmetic"]["cumulative"]["projection_gate"]["every"])
    )
    boot_ceiling = first_number(rung(record, 3)["rule"])
    cleared = boot_is_cleared(state)
    legs = [one for pack in packs for one in legs_of(pack)]
    owed = sum(one["units"] for one in legs)
    started = clock_now()
    last_event = started
    high = (0, 0)
    while True:
        pull()
        mark = fingerprint(where, legs, log)
        if mark[0] > high[0] or mark[1] > high[1]:
            last_event = clock_now()
            high = (max(high[0], mark[0]), max(high[1], mark[1]))
        answered, lines = high
        idle = clock_now() - last_event
        current = leg_state(record, packs, where)
        common = {
            "rung": 5,
            "answered": answered,
            "owed": owed,
            "pod_log_lines": lines,
            "idle_seconds": round(idle, 1),
            "idle_deadline_seconds": deadline,
            "seconds_before_kill": round(deadline - idle, 1),
            "legs": current,
            "rule": rung(record, 5)["rule"],
            "watched_seconds": round(clock_now() - started, 1),
            "copied_back_this_poll": {"rows": mark[0], "log_lines": mark[1]},
            "boot_ceiling_armed": not cleared,
            "projection_every": (
                f"EVERY poll. The registration's «{every} calls» is the floor and this is"
                " strictly stronger — the computation is local and free"
            ),
        }
        if answered >= owed:
            return {
                **common,
                "verdict": "GO",
                "next_step": "every unit is answered — scp the log, then the next gate on the Mac",
                **clock(record, state, now),
            }
        ahead = projection(record, state, current, now)
        if not cleared and not answered and ahead["elapsed_on_this_pod_seconds"] >= boot_ceiling:
            killed = kill()
            return {
                **common,
                "verdict": "KILL",
                "cause": (
                    f"rung 3 — {ahead['elapsed_on_this_pod_seconds']:.0f} s of this pod's"
                    f" create-elapsed and NOT ONE reply, against a {boot_ceiling:.0f} s ceiling"
                ),
                "delete": killed,
                "next_step": "prove the deletion by LISTING, with the volume as positive control",
                **clock(record, state, now),
            }
        if ahead["verdict"] == "KILL" or ahead["cumulative_seconds_left"] <= 0:
            killed = kill()
            return {
                **common,
                "verdict": "KILL",
                "cause": (
                    "rung 4 — the projection left the cap or the hard stop"
                    if ahead["verdict"] == "KILL"
                    else "rung 6 — the cumulative hard stop has no seconds left"
                ),
                "projection": ahead,
                "delete": killed,
                "next_step": "prove the deletion by LISTING, with the volume as positive control",
                **clock(record, state, now),
            }
        if idle >= deadline:
            killed = kill()
            return {
                **common,
                "verdict": "KILL",
                "cause": (
                    f"rung 5 — {idle:.0f} s with no new row and no new log line, against a"
                    f" {deadline:.0f} s deadline measured from the last event"
                ),
                "delete": killed,
                "next_step": "prove the deletion by LISTING, with the volume as positive control",
                **clock(record, state, now),
            }
        print(
            f"  watch · {answered}/{owed} answered · log {lines} lines · idle {idle:.0f} s of"
            f" {deadline:.0f} · projected ${ahead['projected_usd']:.4f} of"
            f" ${ahead['cap_usd_all_in']:.2f} · {common['watched_seconds']:.0f} s watched",
            flush=True,
        )
        sleep(poll_seconds)


# --- rung 7: the dev gate --------------------------------------------------------------------------


def labels() -> dict[tuple[str, int], str | None]:
    out = {}
    for path in LABELS:
        for line in summary.read_text_or_refuse(path).splitlines():
            if line.strip():
                row = json.loads(line)
                out[(row["thread"], int(row["msg_id"]))] = row.get("subject_type")
    return out


def answers_of(path: Path, items: list[dict]) -> tuple[list[dict], list[dict]]:
    """Every reply parsed against the unit it was asked about, and the refusals beside them.

    An unparseable reply is NOT dropped: it is a disagreement, and it is counted by cause. The
    empty-class trap is the reason — unreadable replies pile up wherever the answer is the
    quiet one ([[the_empty_class_eats_the_parse_failures]]).
    """
    by_id = {one["id"]: one for one in items}
    parsed, refused = [], []
    for row in rows_of(path):
        item = by_id.get(row["id"])
        if item is None:
            raise SystemExit(f"{rel(path)} carries {row['id']}, which this leg never asked — stop.")
        if row.get("rendering_sha256") != item["rendering_sha256"]:
            raise SystemExit(f"{row['id']}: answered a request whose sha is not the pack's — stop.")
        try:
            answer = prompts.parse_pass1(row["reply"], msg_id=int(item["msg_id"]))
        except Exception as err:  # the parser's own refusal, whatever it names itself
            refused.append({"id": row["id"], "why": f"{type(err).__name__}: {err}"})
            continue
        parsed.append({**answer, "id": row["id"], "thread": item["thread"]})
    return parsed, refused


def leg_table(record: dict, pack: dict, name: str, where: Path) -> dict:
    """One dev leg scored against the team lead's labels, through bar 4's own comparison."""
    leg = next(one for one in pack["legs"] if one["name"] == name)
    gold = labels()
    our = set(record["bars"]["dev_gate"]["our_readings"])
    wanted, said = [], []
    parsed, refused = answers_of(where / leg["out"], leg["items"])
    by_id = {one["id"]: one for one in parsed}
    for item in leg["items"]:
        label = gold[(item["thread"], int(item["msg_id"]))]
        wanted.append(
            {
                "msg_id": int(item["msg_id"]),
                "subject_type": probe_b.collapse(label),
                "scored_fields": ["subject_type"],
            }
        )
        answer = by_id.get(item["id"])
        if answer is not None:
            said.append(
                {
                    "msg_id": int(item["msg_id"]),
                    "subject_type": probe_b.collapse(answer["subject_type"]),
                }
            )
    result = scorer.reader_comment_agreement(wanted, said)
    agreed_ids = {row["msg_id"] for row in result["rows"] if row["agreed"]}
    our_rows = [
        int(item["msg_id"])
        for item in leg["items"]
        if gold[(item["thread"], int(item["msg_id"]))] in our
    ]
    per_class: dict[str, dict[str, int]] = {}
    for item in leg["items"]:
        label = probe_b.collapse(gold[(item["thread"], int(item["msg_id"]))])
        cell = per_class.setdefault("null" if label is None else label, {"n": 0, "agreed": 0})
        cell["n"] += 1
        cell["agreed"] += int(int(item["msg_id"]) in agreed_ids)
    return {
        "leg": name,
        "task": leg["task"],
        "file": rel(where / leg["out"]),
        "answered": len(parsed),
        "refused": refused,
        "n": result["n"],
        "agreed": result["agreed"],
        "disagreed": result["disagreed"],
        "absent": result["absent"],
        "rate": round(result["rate"], 6),
        "our_n": len(our_rows),
        "our_agreed": sum(1 for one in our_rows if one in agreed_ids),
        "per_class": per_class,
        "rows": result["rows"],
    }


def dev_gate(record: dict, state: dict, pack: dict, where: Path, now=None) -> dict:
    """Rung 7 — the two pre-registered inequalities, paired on the same 200 rows. Both or no shot."""
    bar = record["bars"]["dev_gate"]
    base = leg_table(record, pack, "base", where)
    v2 = leg_table(record, pack, "v2", where)
    our_delta = v2["our_agreed"] - base["our_agreed"]
    agree_delta = v2["agreed"] - base["agreed"]
    our_minimum = int(bar["our_delta_minimum"])
    agree_minimum = int(bar["agreement_delta_minimum"])
    reachable = base["our_agreed"] + our_minimum <= base["our_n"]
    passed = our_delta >= our_minimum and agree_delta >= agree_minimum
    verdict = "GO" if passed else "RED"
    return {
        "rung": 7,
        "base": base,
        "v2": v2,
        "our_delta": our_delta,
        "our_delta_minimum": our_minimum,
        "our_delta_passed": our_delta >= our_minimum,
        "agreement_delta": agree_delta,
        "agreement_delta_minimum": agree_minimum,
        "agreement_delta_passed": agree_delta >= agree_minimum,
        "reachability": {
            "our_rows": base["our_n"],
            "base_correct": base["our_agreed"],
            "highest_base_that_leaves_the_delta_reachable": base["our_n"] - our_minimum,
            "reachable": reachable,
            "rule": bar["reachability"],
        },
        "verdict": verdict if reachable else "STOP",
        "rule": bar["rule"],
        "next_step": (
            "GO: the shot may be fired — ONE attempt, SPENT at the first gold-row reply"
            if passed and reachable
            else "the base already answers too many «our» rows for a +10 delta to exist. The gate"
            " cannot be met by any v2 — STOP, delete, and return the table to the operator"
            if not reachable
            else "RED: the line closes. Delete, prove it by listing, and the attempt is NOT spent —"
            " no gold row was answered. The dev table goes back to the team lead"
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
    parser.add_argument("--pre-create-check", action="store_true", help="never two endpoints")
    parser.add_argument(
        "--price",
        "--open",
        dest="price",
        action="store_true",
        help="rung 1: record the pod, check costPerHr against the ceiling and the backstop stamp",
    )
    parser.add_argument("--pod-id")
    parser.add_argument("--created-at", help="the create response's stamp — the meter's zero")
    parser.add_argument("--usd-per-hour", type=float, help="costPerHr, read back from create")
    parser.add_argument("--card", help="the card the create response actually gave")
    parser.add_argument(
        "--terminate-after",
        help="the backstop stamp ACTUALLY handed to `pod create` — checked against the cumulative"
        " hard stop and refused if the window is longer than rung 6 allows",
    )
    parser.add_argument("--gate0", action="store_true", help="rung 2, the ssh dead-man")
    parser.add_argument("--ssh-ok", action="store_true", help="the endpoint answered")
    parser.add_argument("--boot", action="store_true", help="rung 3, boot to the first reply")
    parser.add_argument("--first-reply-at", help="when the first reply landed, UTC ISO8601")
    parser.add_argument(
        "--projection", action="store_true", help="rung 4, once, on what is on disk"
    )
    parser.add_argument("--watch", action="store_true", help="rung 5, the blocking liveness loop")
    parser.add_argument("--dev-gate", action="store_true", help="rung 7, the paired dev table")
    parser.add_argument("--close", action="store_true", help="this pod is deleted")
    parser.add_argument("--deleted-at", help="the deletion's stamp — the meter's end")
    parser.add_argument("--outcome", help="why this pod ended")
    parser.add_argument("--clock", action="store_true", help="the cumulative reading, right now")
    parser.add_argument(
        "--pack", action="append", type=Path, help="a pack whose legs are being watched or priced"
    )
    parser.add_argument("--ssh", help="user@host of the pod, for --watch")
    parser.add_argument("--ssh-port", type=int, help="the ssh port `runpodctl ssh info` gave")
    parser.add_argument("--remote-dir", default="/workspace/run")
    parser.add_argument("--remote-log", default="/workspace/run/pod.log")
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT / "results")
    parser.add_argument("--poll", type=float, default=20.0, help="seconds between copies")
    args = parser.parse_args(argv)

    record = registration()

    if args.pre_create_check:
        state = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {}
        pod = live_pod(state)
        if pod is not None:
            print(
                f"pod {pod['pod_id']} is OPEN in {rel(RECORD)} and has no deleted_at. Never two"
                " billing endpoints at once — delete it, prove it by listing, and --close first."
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

    if args.price:
        for name in ("pod_id", "created_at", "usd_per_hour", "card", "terminate_after"):
            if getattr(args, name) is None:
                parser.error(f"--price needs --{name.replace('_', '-')}")
        state = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {"pods": []}
        if live_pod(state) is not None:
            raise SystemExit(
                f"pod {live_pod(state)['pod_id']} is still open in {rel(RECORD)}. Never two billing"
                " endpoints at once — close it with --close first."
            )
        ceiling = float(record["money"]["meter"]["price_ceiling_usd_per_hour"])
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
            "terminate_after_rule": rung(record, 6)["rule"],
            "verdict": "GO" if args.usd_per_hour <= ceiling else "KILL",
            "rule": rung(record, 1)["rule"],
            "next_step": (
                "the backstop the platform holds is inside the cumulative stop; poll --gate0"
                if args.usd_per_hour <= ceiling
                else "DELETE the pod now and STOP — no generation of any kind"
            ),
            **clock(record, state, now),
        }
        append_gate(state, gate, "price")
        return show(gate)

    state = run_state()

    if args.clock:
        print(json.dumps(clock(record, state, now), ensure_ascii=False, indent=2, sort_keys=True))
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
            record, state, elapsed_since(pod["created_at"], now), args.first_reply_at, now
        )
        append_gate(state, gate, "boot")
        return show(gate)

    packs = [json.loads(one.read_text(encoding="utf-8")) for one in (args.pack or ())]

    if args.projection:
        if not packs:
            parser.error("--projection needs at least one --pack")
        gate = projection(record, state, leg_state(record, packs, args.outdir), now)
        append_gate(state, gate, "projection")
        return show(gate)

    if args.watch:
        if not packs:
            parser.error("--watch needs at least one --pack")
        if not args.ssh or not args.ssh_port:
            parser.error("--watch needs --ssh and --ssh-port: it copies the files back itself")
        pod = live_pod(state)
        if pod is None:
            raise SystemExit("no pod is live — --watch has nothing to watch")
        names = [one["out"] for pack in packs for one in legs_of(pack)]

        def pull() -> None:
            for name in names:
                scp(args.ssh, args.ssh_port, f"{args.remote_dir}/{name}", args.outdir / name)
            scp(args.ssh, args.ssh_port, args.remote_log, POD_LOG)

        def kill() -> dict:
            return pod_delete(pod["pod_id"])

        try:
            gate = watch(
                record,
                state,
                packs,
                where=args.outdir,
                log=POD_LOG,
                pull=pull,
                kill=kill,
                now=now,
                poll_seconds=args.poll,
            )
        except BaseException as err:
            # the loop is the only thing watching a billed pod. Whatever ends it — an exception, a
            # broken pipe, Ctrl-C — has to leave a RECORD and an instruction, and then re-raise:
            # swallowing the cause in the cleanup arm is how a crash becomes a silent bill
            # ([[cleanup_in_the_except_arm_can_eat_the_cause]])
            append_gate(
                state,
                {
                    "rung": 5,
                    "verdict": "KILL",
                    "cause": f"the watch loop ended on {type(err).__name__}: {err}",
                    "verdict_is_an_instruction": True,
                    "next_step": (
                        f"NOTHING IS WATCHING POD {pod['pod_id']} — delete it NOW:"
                        f" `runpodctl pod delete {pod['pod_id']}`, then --close and prove it by"
                        " listing. The platform backstop is the only guard left"
                    ),
                    **clock(record, state, now),
                },
                "watch-ended",
            )
            print(
                f"\n!!! THE WATCH LOOP ENDED AND POD {pod['pod_id']} IS STILL BILLING !!!\n"
                f"    runpodctl pod delete {pod['pod_id']}\n",
                flush=True,
            )
            raise
        append_gate(state, gate, "watch")
        return show(gate)

    if args.dev_gate:
        pack = json.loads(DEV_PACK.read_text(encoding="utf-8"))
        gate = dev_gate(record, state, pack, args.outdir, now)
        append_gate(state, gate, "dev-gate")
        return show(gate)

    if args.close:
        if not args.deleted_at:
            parser.error("--close needs --deleted-at: this pod's billed end")
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
        append_gate(state, gate, "close")
        return show(gate)

    parser.error(
        "one of --pre-create-check / --price / --gate0 / --boot / --projection / --watch /"
        " --dev-gate / --close / --clock"
    )
    return KILL


if __name__ == "__main__":
    raise SystemExit(main())
