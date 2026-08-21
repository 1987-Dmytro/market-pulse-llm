#!/usr/bin/env python3
"""pass1-window — the Mac half of the ONE paid session: every rung, and the loop that HOLDS them.

`results/prereg_pass1_window.json` is the law. Every threshold below is READ out of it and none is
typed here — a gate whose number lives in two files goes green after one of them moves
([[preregistration_is_a_file_not_a_constant]]).

**This is a SIBLING of `scripts/gate_pass1_fewshot.py`, and here is exactly what that means.**
r2's gate is pinned by r2's sealed record and is never edited. What is IMPORTED from it is every
rung computation that is pure — a function of the record and the state it is handed:

    rung · first_number · billed_before · live_pod · clock · pre_create · gate_zero · gate_boot
    elapsed_since_create · rows_of · legs_of · leg_state · projection · scp · pod_delete
    boot_is_cleared · fingerprint · show

What is RE-DECLARED, and why each one had to be:

* `registration` / `run_state` / `save` / `append_gate` bind to r2's own PREREG and RECORD paths.
  Importing them would have this contract's watch loop WRITE INTO `results/pass1_fewshot_r2_run.json`
  — a sealed record of a closed session ([[rewriting_a_record_resets_state_you_do_not_own]]).
* `tolerance` and `terminate_after` name the registration in their refusal, and a refusal that
  names the wrong file sends the operator to the wrong file.
* `launched_at_of` reads its stamp by NAME, and r2's name is on a stale file left in `results/` by
  the closed session. This contract's stamp has its own name and its own log.
* `first_reply_after_launch` read `population.dev.legs[0]` — a shape this record does not have. It
  reads the leg this record NAMES. Dv620's defect was a scan that took a minimum across legs and
  got the leg whose clock had been re-zeroed; with one leg there is no minimum to take, and the fix
  is still to READ the named leg rather than to scan the directory.
* `watch` calls `launched_at_of`, so importing it would import r2's stamp and r2's record with it.
* Rung 7 is a COMPLETENESS bar here and a dev gate there — a different question entirely.

**Rung 7 counts what r2's `answers_of` refuses on.** That function raises on a sha mismatch, which
is right for a gate whose next step is a shot and wrong for a bar whose third number IS the mismatch
count. The parser is the same one (`prompts.parse_pass1`); what differs is that a mismatch here is a
RED with a number beside it and not a stack trace ([[count_the_kind_not_the_rows]]).

**Exit codes ARE the rule** — 0 GO, 2 KILL/STOP, 3 WAIT — because a deadline a human has to eyeball
is a deadline that gets discovered in a bill.

    PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --pre-create-check
    PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --price --pod-id <ID> \\
        --created-at <UTC ISO8601> --usd-per-hour <costPerHr> --card '<the card>' \\
        --terminate-after '<the stamp `pod create` was actually given>'
    PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --gate0 [--ssh-ok]
    PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --boot
    PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --watch --ssh root@<HOST> --ssh-port <PORT>
    PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --projection
    PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --completeness
    PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --close --deleted-at <UTC ISO8601> \\
        --outcome '<why this pod ended>'
"""

import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_pass1_fewshot as r2gate  # noqa: E402

from market_pulse import prompts  # noqa: E402

# the pure rung computations, imported rather than copied. Each is a function of the record and the
# state it is handed, and none of them reads a module global of r2's
rung = r2gate.rung
first_number = r2gate.first_number
billed_before = r2gate.billed_before
live_pod = r2gate.live_pod
clock = r2gate.clock
pre_create = r2gate.pre_create
gate_zero = r2gate.gate_zero
gate_boot = r2gate.gate_boot
elapsed_since_create = r2gate.elapsed_since_create
rows_of = r2gate.rows_of
legs_of = r2gate.legs_of
leg_state = r2gate.leg_state
projection = r2gate.projection
scp = r2gate.scp
pod_delete = r2gate.pod_delete
boot_is_cleared = r2gate.boot_is_cleared
fingerprint = r2gate.fingerprint
show = r2gate.show

rel = r2gate.rel
stamp = r2gate.stamp
elapsed_since = r2gate.elapsed_since
GO, KILL, WAIT = r2gate.GO, r2gate.KILL, r2gate.WAIT

PHASE = "pass1-window"
PREREG = REPO_ROOT / "results" / "prereg_pass1_window.json"
RECORD = REPO_ROOT / "results" / "pass1_window_run.json"
PACK = REPO_ROOT / "results" / "pass1_window_pack.json"
POD_LOG = REPO_ROOT / "results" / "pass1_window_pod.log"
LAUNCH_STAMP = "pass1_window_launched_at"
"""This contract's own names for the two files `--watch` copies back. `results/` already holds
`pass1_fewshot_r2_launched_at` and `pass1_fewshot_pod.log` from the closed session, and a rung that
read one of them would be reading another attempt's clock."""


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


def tolerance(record: dict) -> float:
    """Rung 6's overshoot allowance — READ from the record, never defaulted (Dv603)."""
    cumulative = record["money"]["arithmetic"]["cumulative"]
    if "backstop_tolerance_seconds" not in cumulative:
        raise SystemExit(
            f"{rel(PREREG)} carries no"
            " money.arithmetic.cumulative.backstop_tolerance_seconds. Rung 6's overshoot allowance"
            " is a number this gate ACTS on, so it belongs in the record and this instrument will"
            " not supply one — re-register it."
        )
    return float(cumulative["backstop_tolerance_seconds"])


def terminate_after(record: dict, state: dict, created_at: str, given: str) -> dict:
    """This pod's backstop stamp: its own create plus what the hard stop has LEFT — and a CHECK.

    The stamp handed to `pod create` is a REQUIRED argument, because rung 6 is enforced by a
    platform flag this instrument cannot read back ([[the_guard_you_built_and_then_bypassed]]).
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
    if overshoot > tolerance(record):
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
        "tolerance_seconds": tolerance(record),
        "billed_by_closed_pods_seconds": round(seconds_before, 1),
    }


def launched_at_of(record: dict, state: dict, where: Path, now=None) -> str | None:
    """Rung 3's ANCHOR: the stamp the runner's own launch wrote, or None while it has none.

    A READING and not a flag: a stamp the executor types is an assertion, and this particular
    assertion can only ever move a deadline LATER
    ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]]). The create-anchored backstop bounds it
    either way, and it is written into the pod ONCE and never overwritten.
    """
    pod = live_pod(state)
    if pod is None:
        return None
    if pod.get("launched_at"):
        return pod["launched_at"]
    path = where / LAUNCH_STAMP
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    try:
        when = stamp(text)
    except ValueError:
        raise SystemExit(
            f"{rel(path)} holds {text!r}, which is not a UTC ISO8601 stamp. Rung 3's anchor is"
            " unreadable — stop, delete the pod and report."
        ) from None
    created = stamp(pod["created_at"])
    skew = tolerance(record)
    if when < created - timedelta(seconds=skew):
        raise SystemExit(
            f"{rel(path)} says the runner launched at {when.isoformat(timespec='seconds')}, BEFORE"
            f" this pod was created at {pod['created_at']}. That stamp is a previous attempt's —"
            " the run directory was not cleared. Stop, delete the pod and report."
        )
    if when > (now or datetime.now(UTC)) + timedelta(seconds=skew):
        raise SystemExit(
            f"{rel(path)} says the runner launched at {when.isoformat(timespec='seconds')}, in the"
            " FUTURE. A launch anchor ahead of the clock would hand rung 3 a window nobody priced."
            " Stop, delete the pod and report."
        )
    pod["launched_at"] = when.isoformat(timespec="seconds")
    save(state)
    return pod["launched_at"]


def first_reply_after_launch(record: dict, where: Path) -> float | None:
    """Seconds from the runner's launch to the FIRST reply — READ off the out-file, never typed.

    `elapsed_since_start` is monotonic seconds from the runner's own start to that row, so the
    smallest one is «launch → first reply» and the gate reads it instead of being told. The file is
    the one this RECORD names: a scan of the run directory is what let Dv620 take a minimum across
    two legs and land on the one whose clock the shipped `run()` had re-zeroed. There is one leg
    here, and it is still read by name.
    """
    seen = [
        float(row["elapsed_since_start"])
        for row in rows_of(where / record["population"]["out_file"])
        if row.get("elapsed_since_start") is not None
    ]
    return min(seen) if seen else None


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

    r2's loop, re-declared because it calls `launched_at_of` and that name binds to a module. The
    logic is r2's and every threshold is still read out of THIS record.

    **An event is a RISE, and that asymmetry is the whole guard.** The fingerprint is a HIGH-WATER
    mark: `pull` is scp and scp fails, and a failed copy can leave a local file shorter than it was
    a poll ago. Refreshing the deadline on any CHANGE would make a dead pod behind a flapping link
    immortal.

    Rung 4 is re-run on EVERY poll and not every `every` calls — the registered interval is a floor
    and the projection is a pure computation over local files. Rungs 3 and 6 are checked beside it.

    `pull` and `kill` are arguments so the whole loop is driven at $0 on a fake transport
    ([[guard_selftest_negative_control]]).
    """
    deadline = first_number(rung(record, 5)["rule"])
    every = int(
        first_number(record["money"]["arithmetic"]["cumulative"]["projection_gate"]["every"])
    )
    boot_ceiling = first_number(rung(record, 3)["rule"])
    backstop = float(rung(record, 3)["backstop_seconds"])
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
        launched = launched_at_of(record, state, where, now)
        since_launch = None if launched is None else elapsed_since(launched, now)
        current = leg_state(record, packs, where)
        common = {
            "rung": 5,
            "answered": answered,
            "owed": owed,
            "launched_at": launched,
            "seconds_since_launch": None if since_launch is None else round(since_launch, 1),
            "boot_backstop_seconds": backstop,
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
                "next_step": "every unit is answered — scp the log, then rung 7 on the Mac",
                **clock(record, state, now),
            }
        ahead = projection(record, state, current, now)
        if not cleared and not answered:
            create_elapsed = ahead["elapsed_on_this_pod_seconds"]
            over_anchor = since_launch is not None and since_launch >= boot_ceiling
            over_backstop = create_elapsed >= backstop
            if over_anchor or over_backstop:
                killed = kill()
                return {
                    **common,
                    "verdict": "KILL",
                    "cause": (
                        f"rung 3 — {since_launch:.0f} s since the runner's own launch and NOT ONE"
                        f" reply, against a {boot_ceiling:.0f} s ceiling"
                        if over_anchor
                        else f"rung 3's create-anchored BACKSTOP — {create_elapsed:.0f} s of this"
                        f" pod's create-elapsed and NOT ONE reply, against {backstop:.0f} s"
                        + ("" if launched else " and no launch stamp has been copied back at all")
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


# --- rung 7: the completeness bar -------------------------------------------------------------------


def cause_of(err: BaseException) -> str:
    """A refusal's CAUSE, short enough to group on and specific enough to act on.

    The parser's message carries the offending fragment, which would make every refusal its own
    class; the head of it does not. Refusals are grouped by `(type, head)` so the census can say
    «eleven replies ended mid-object» rather than «eleven distinct errors»
    ([[count_the_kind_not_the_rows]]).
    """
    head = str(err).split(":")[0].strip()
    return f"{type(err).__name__}: {head}" if head else type(err).__name__


def completeness(record: dict, state: dict, pack: dict, where: Path, now=None) -> dict:
    """Rung 7 — the three numbers of the bar, each of them a COUNT and never an exception.

    `gate_pass1_fewshot.answers_of` raises on a sha mismatch and on an id the leg never asked. That
    is right for a gate whose next step is a shot; here the mismatch count IS the bar's third
    number, so both are counted and reported. The parser is the same `prompts.parse_pass1`.
    """
    bar = record["bars"]["completeness"]
    leg = pack["legs"][0]
    items = leg["items"]
    by_id = {one["id"]: one for one in items}
    rows = rows_of(where / leg["out"])

    seen: dict[str, dict] = {}
    duplicates, unknown, mismatched = [], [], []
    refusals, not_balanced = [], []
    parsed = 0
    for row in rows:
        row_id = row.get("id")
        item = by_id.get(row_id)
        if item is None:
            unknown.append(row_id)
            continue
        if row_id in seen:
            duplicates.append(row_id)
            continue
        seen[row_id] = row
        if row.get("rendering_sha256") != item["rendering_sha256"]:
            mismatched.append(row_id)
        if row.get("balanced") is False:
            not_balanced.append(row_id)
        try:
            prompts.parse_pass1(row["reply"], msg_id=int(item["msg_id"]))
        except Exception as err:  # the parser's own refusal, whatever it names itself
            refusals.append({"id": row_id, "cause": cause_of(err), "why": f"{err}"})
            continue
        parsed += 1

    owed = int(bar["owed"])
    unanswered = [one["id"] for one in items if one["id"] not in seen]
    by_cause = Counter(one["cause"] for one in refusals)
    answered_ok = len(seen) >= int(bar["answered_minimum"])
    sha_ok = len(mismatched) <= int(bar["sha_mismatches_maximum"])
    refusals_ok = len(refusals) <= int(bar["parse_refusals_maximum"])
    clean = not unknown and not duplicates
    verdict = "GO" if answered_ok and sha_ok and refusals_ok and clean else "RED"
    return {
        "rung": 7,
        "file": rel(where / leg["out"]),
        "rows_in_the_file": len(rows),
        "owed": owed,
        "answered": len(seen),
        "answered_minimum": int(bar["answered_minimum"]),
        "answered_passed": answered_ok,
        "parsed": parsed,
        "sha_mismatches": len(mismatched),
        "sha_mismatch_ids": mismatched[:20],
        "sha_mismatches_maximum": int(bar["sha_mismatches_maximum"]),
        "sha_passed": sha_ok,
        "parse_refusals": len(refusals),
        "parse_refusals_maximum": int(bar["parse_refusals_maximum"]),
        "parse_refusals_passed": refusals_ok,
        "parse_refusals_by_cause": dict(sorted(by_cause.items())),
        "parse_refusal_rows": refusals[:20],
        "replies_that_never_closed_their_object": len(not_balanced),
        "unanswered": len(unanswered),
        "unanswered_ids": unanswered[:20],
        "ids_the_leg_never_asked": unknown[:20],
        "duplicate_ids": duplicates[:20],
        "answered_means": bar["answered_means"],
        "verdict": verdict,
        "rule": bar["rule"],
        "next_step": (
            "GO: the out-file is complete and is the INPUT of pass 2 — write the census and the"
            " report"
            if verdict == "GO"
            else "RED: the out-file goes back to the team lead WITH its refusals by cause and its"
            " mismatches. Nothing already bought is deleted and nothing is re-asked without the"
            " recovery clause"
        ),
        **clock(record, state, now),
    }


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
    parser.add_argument(
        "--boot",
        action="store_true",
        help="rung 3: launch → the first reply, both READ off the run directory. It takes no stamp",
    )
    parser.add_argument(
        "--projection", action="store_true", help="rung 4, once, on what is on disk"
    )
    parser.add_argument("--watch", action="store_true", help="rung 5, the blocking liveness loop")
    parser.add_argument(
        "--completeness", action="store_true", help="rung 7, the bar: answered · shas · refusals"
    )
    parser.add_argument("--close", action="store_true", help="this pod is deleted")
    parser.add_argument("--deleted-at", help="the deletion's stamp — the meter's end")
    parser.add_argument("--outcome", help="why this pod ended")
    parser.add_argument("--clock", action="store_true", help="the cumulative reading, right now")
    parser.add_argument("--pack", type=Path, default=PACK, help="the pack whose leg is watched")
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
        gate = pre_create(record, state)
        print(json.dumps(gate, ensure_ascii=False, indent=2, sort_keys=True))
        print(f"\n{gate['verdict']}  ·  {gate['next_step']}")
        return GO if gate["verdict"] == "GO" else KILL

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
        # the recovery clause, read on the state BEFORE this pod joins it (Dv615). The pod is
        # RECORDED either way — a pod that exists against no counter is a pod nothing is measuring
        recovery = pre_create(record, state)
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
            "recovery": recovery,
            "verdict": (
                "GO" if args.usd_per_hour <= ceiling and recovery["verdict"] == "GO" else "KILL"
            ),
            "rule": rung(record, 1)["rule"],
            "next_step": (
                "the backstop the platform holds is inside the cumulative stop; poll --gate0"
                if args.usd_per_hour <= ceiling and recovery["verdict"] == "GO"
                else "DELETE the pod now and STOP — no generation of any kind. "
                + (
                    "the live price is over the registered ceiling"
                    if args.usd_per_hour > ceiling
                    else recovery["next_step"]
                )
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
            record,
            state,
            elapsed_since(pod["created_at"], now),
            first_reply_after_launch(record, args.outdir),
            launched_at_of(record, state, args.outdir, now),
            now,
        )
        append_gate(state, gate, "boot")
        return show(gate)

    pack = json.loads(args.pack.read_text(encoding="utf-8"))
    if pack["population"]["payable_comments"] != record["population"]["payable_comments"]:
        raise SystemExit(
            f"{rel(args.pack)} carries {pack['population']['payable_comments']} payable comments and"
            f" {rel(PREREG)} registers {record['population']['payable_comments']}. The gate would"
            " be measuring a population nobody priced — stop and report."
        )

    if args.projection:
        gate = projection(record, state, leg_state(record, [pack], args.outdir), now)
        append_gate(state, gate, "projection")
        return show(gate)

    if args.watch:
        if not args.ssh or not args.ssh_port:
            parser.error("--watch needs --ssh and --ssh-port: it copies the files back itself")
        pod = live_pod(state)
        if pod is None:
            raise SystemExit("no pod is live — --watch has nothing to watch")
        names = [one["out"] for one in legs_of(pack)]

        def pull() -> None:
            for name in names:
                scp(args.ssh, args.ssh_port, f"{args.remote_dir}/{name}", args.outdir / name)
            # rung 3's anchor comes back with them: the launch stamp is a file the POD wrote
            scp(
                args.ssh,
                args.ssh_port,
                f"{args.remote_dir}/launched_at",
                args.outdir / LAUNCH_STAMP,
            )
            scp(args.ssh, args.ssh_port, args.remote_log, POD_LOG)

        def kill() -> dict:
            return pod_delete(pod["pod_id"])

        try:
            gate = watch(
                record,
                state,
                [pack],
                where=args.outdir,
                log=POD_LOG,
                pull=pull,
                kill=kill,
                now=now,
                poll_seconds=args.poll,
            )
        except BaseException as err:
            # the loop is the only thing watching a billed pod. Whatever ends it has to leave a
            # RECORD and an instruction, and then re-raise — swallowing the cause in the cleanup arm
            # is how a crash becomes a silent bill ([[cleanup_in_the_except_arm_can_eat_the_cause]])
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

    if args.completeness:
        gate = completeness(record, state, pack, args.outdir, now)
        append_gate(state, gate, "completeness")
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
        pod["billed_usd"] = round(billed * r2gate.rate_of(pod), 6)
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
        " --completeness / --close / --clock"
    )
    return KILL


if __name__ == "__main__":
    raise SystemExit(main())
