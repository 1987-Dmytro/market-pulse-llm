#!/usr/bin/env python3
"""reader-v5b — the Mac half: one attempt, up to three pod SEGMENTS, and the same instrument.

Nothing about the pack, the projection, the ingest or the parse is new: `read_threads_reader_v5` is
IMPORTED and its module constants are swapped for this phase's for the length of a call, so the pack
is built by the same function that built v5's and the cap gate is the same inequality. What is new is
the transport the sitting of 2026-08-17 ruled after a pod was billed 727.9 s and never answered ssh.

**1. Transport gate 0 — an ssh dead-man.** If `runpodctl ssh info` has not answered with a
connectable endpoint by 180 s of THIS segment's create-elapsed, the pod is killed and replaced. At
most two recreates; a third dead pod is a datacenter state and a STOP.

**2. One attempt, several segments, one cap.** Each segment carries its own create stamp and its own
`costPerHr`; the boot deadlines are measured from the segment's own create, and the affordability leg
is the ATTEMPT's — the cap less what every closed segment billed. Never two pods at once, and the
check for it runs BEFORE `pod create` rather than as a refusal after the second meter has started.

**3. The resume protocol.** The partial jsonl is copied back inside the poll loop; before it goes
back UP to a replacement pod it is NORMALIZED here — a torn last line dropped as a byte prefix — or
the fragment travels, the replacement appends onto it, and the next gate reads a torn MIDDLE line and
raises on the kill-rule path.

    PYTHONPATH=src python3.11 scripts/read_threads_reader_v5b.py --pack
    PYTHONPATH=src python3.11 scripts/read_threads_reader_v5b.py --pre-create-check
    PYTHONPATH=src python3.11 scripts/read_threads_reader_v5b.py --open --pod-id <ID> \\
        --created-at 2026-08-17T18:00:00Z --usd-per-hour <costPerHr> --card '<the card>'
    PYTHONPATH=src python3.11 scripts/read_threads_reader_v5b.py --gate0
    PYTHONPATH=src python3.11 scripts/read_threads_reader_v5b.py --gate0 --ssh-ok
    PYTHONPATH=src python3.11 scripts/read_threads_reader_v5b.py --close-segment \\
        --deleted-at 2026-08-17T18:05:00Z --outcome "gate 0 KILL, unreachable"
    PYTHONPATH=src python3.11 scripts/read_threads_reader_v5b.py --gate --raw results/reader_v5b_pod.jsonl
    PYTHONPATH=src python3.11 scripts/read_threads_reader_v5b.py --normalize --raw results/reader_v5b_pod.jsonl
    PYTHONPATH=src python3.11 scripts/read_threads_reader_v5b.py --ingest --raw results/reader_v5b_pod.jsonl
"""

import argparse
import json
import sys
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import read_threads_reader_v5 as v5  # noqa: E402
import runpod_guard as guard  # noqa: E402

PHASE = "reader-v5b"
PREREG = REPO_ROOT / "results" / "prereg_reader_probe_v5b.json"
LEDGER = guard.step_ledger_path(PHASE)
PACK = REPO_ROOT / "results" / "reader_v5b_pack.json"
RAW = REPO_ROOT / "results" / "reader_v5b_pod.jsonl"
EVIDENCE = REPO_ROOT / "results" / "reader_v5b_w1.jsonl"
RECORD = REPO_ROOT / "results" / "reader_v5b_run.json"

SWAPPED = ("PHASE", "PREREG", "LEDGER", "PACK", "RAW", "EVIDENCE", "RECORD")


def _ours() -> dict:
    """This phase's constants, read at call time and not frozen into a dict at import.

    A snapshot taken at import would go stale the moment a test — or a `--raw` on the command line —
    pointed one of these somewhere else, and the swap below would then hand the sibling module the
    ORIGINAL path while this one used the new one. One reader, one moment.
    """
    return {name: globals()[name] for name in SWAPPED}


rel = v5.rel
stamp = v5.stamp
elapsed_since = v5.elapsed_since
rate_of = v5.rate_of
raw_rows = v5.raw_rows


@contextmanager
def as_this_phase():
    """v5's module constants swapped for v5b's for the length of one call, and put back after.

    `scripts/read_threads_reader_v5.py` is pinned BY SHA inside the frozen v5b registration
    (`producer.borrowed`) — it produced the gate table the registration publishes — so it cannot grow
    the parameters this phase would like it to have. Swapping its constants around the call is how the
    pack builder, the registration check, the projection and the ingest stay ONE implementation
    instead of two spellings of a cap guard. Restored in a `finally`, because a module left pointing
    at another phase's files is the kind of bug that only shows up in the second command.
    """
    ours = _ours()
    keep = {name: getattr(v5, name) for name in ours}
    for name, value in ours.items():
        setattr(v5, name, value)
    try:
        yield
    finally:
        for name, value in keep.items():
            setattr(v5, name, value)


def registration() -> dict:
    with as_this_phase():
        return v5.registration()


def run_record() -> dict:
    if not RECORD.exists():
        raise SystemExit(
            f"{rel(RECORD)} does not exist — no segment of this attempt has been opened with"
            " --open. A pod that exists against no counter is a pod nothing is measuring."
        )
    return json.loads(RECORD.read_text(encoding="utf-8"))


def save(state: dict) -> None:
    RECORD.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def append_gate(state: dict, gate: dict, kind: str) -> dict:
    """v5's appended-gate rule, with the SEGMENT stamped on every snapshot.

    A list cannot lose a reading, and with several pods in one attempt it also has to say which pod a
    reading came off — otherwise two segments' boot gates are indistinguishable in the record.
    """
    segment = state["segments"][-1] if state.get("segments") else {}
    state.setdefault("gates", []).append(
        {
            "kind": kind,
            "at": datetime.now(UTC).isoformat(timespec="seconds"),
            "segment": len(state.get("segments", [])),
            "pod_id": segment.get("pod_id"),
            **gate,
        }
    )
    state["latest"] = {
        "kind": kind,
        "verdict": gate["verdict"],
        "segment": len(state.get("segments", [])),
    }
    save(state)
    return state


def spent_before(state: dict) -> tuple[float, float]:
    """What every CLOSED segment billed: seconds, and dollars at each segment's own price.

    Never a balance delta — that prices the account and not the leg ([[a_balance_delta_is_not_a_per_leg_cost]]).
    A segment with no `deleted_at` is the live one and is not counted here; its seconds are the
    `elapsed` the gates measure.
    """
    closed = [one for one in state.get("segments", []) if one.get("deleted_at")]
    seconds = sum(float(one["billed_seconds"]) for one in closed)
    usd = sum(float(one["billed_usd"]) for one in closed)
    return seconds, usd


def charged(record: dict, spent_usd: float) -> dict:
    """The registration with the cap REDUCED by what earlier segments billed.

    The point of doing it this way: `usable_seconds`, `deadlines` and `projection` stay v5's own
    functions, and «(cap − spent across all segments) ÷ the rate − one delete margin» is exactly what
    they compute when the cap they read is the remainder. One inequality, not two.
    """
    money = record["money"] | {
        "cap_usd_all_in": round(float(record["money"]["cap_usd_all_in"]) - spent_usd, 9)
    }
    return record | {"money": money}


def segment_context(record: dict, state: dict) -> dict:
    """The attempt's accounting, named so no field means two things.

    `elapsed_since_create_seconds` in a gate snapshot is THIS segment's; the money is the attempt's.
    Those are two axes and a snapshot that used one name for both would be unreadable a day later
    ([[id_spaces_that_look_comparable]]).
    """
    seconds, usd = spent_before(state)
    cap = float(record["money"]["cap_usd_all_in"])
    return {
        "segment": len(state.get("segments", [])),
        "segments_allowed": int(
            record["go_no_go"]["gates"]["0_transport_ssh_deadman"]["max_recreates"]
        )
        + 1,
        "billed_seconds_closed_segments": round(seconds, 1),
        "spent_closed_segments_usd": round(usd, 6),
        "cap_usd_all_in": cap,
        "cap_left_for_this_segment_usd": round(cap - usd, 6),
    }


def gate_zero(record: dict, state: dict, elapsed: float, ssh_ok: bool) -> dict:
    """The ssh dead-man, executable. WAIT, GO or KILL, on this segment's own create-elapsed.

    GO means the endpoint answered and the segment is alive; KILL means it did not by the registered
    threshold and the pod is deleted, proven by a listing, and replaced — unless this was the last
    segment the ruling allows, in which case the attempt STOPs.
    """
    gate = record["go_no_go"]["gates"]["0_transport_ssh_deadman"]
    threshold = float(gate["threshold_seconds"])
    context = segment_context(record, state)
    last = context["segment"] >= context["segments_allowed"]
    verdict = "GO" if ssh_ok else ("KILL" if elapsed >= threshold else "WAIT")
    return {
        "elapsed_since_this_segments_create_seconds": round(elapsed, 1),
        "threshold_seconds": threshold,
        "seconds_left": round(threshold - elapsed, 1),
        "ssh_endpoint_answered": ssh_ok,
        "recreates_left": max(0, context["segments_allowed"] - context["segment"]),
        "next_step": (
            "stage and launch"
            if verdict == "GO"
            else "keep polling `runpodctl ssh info` at 3-4 s"
            if verdict == "WAIT"
            else (
                "STOP — this is the last segment the ruling allows, so a dead pod here is a"
                " datacenter state and the attempt closes"
                if last
                else "delete, prove it by listing, then create the replacement"
            )
        ),
        "verdict": verdict,
        "rule": gate["rule"],
        **context,
    }


def deadlines(record: dict, state: dict, elapsed: float, generation_at: float | None) -> dict:
    """v5's boot deadline over the REMAINING cap, with the attempt's accounting beside it."""
    context = segment_context(record, state)
    rate = rate_of(state["segments"][-1])
    gate = v5.deadlines(
        charged(record, context["spent_closed_segments_usd"]), rate, elapsed, generation_at
    )
    return gate | {
        "usable_seconds_this_segment": gate["usable_seconds"],
        "spent_so_far_usd": round(context["spent_closed_segments_usd"] + elapsed * rate, 4),
        "spent_this_segment_usd": round(elapsed * rate, 4),
        **context,
    }


def projection(record: dict, state: dict, rows: list[dict], elapsed: float, pack: dict) -> dict:
    """The registered full-pass inequality, over the cap the attempt has LEFT."""
    context = segment_context(record, state)
    rate = rate_of(state["segments"][-1])
    with as_this_phase():
        gate = v5.projection(
            charged(record, context["spent_closed_segments_usd"]), rate, rows, elapsed, pack
        )
    return gate | {
        "usable_seconds_this_segment": gate["usable_seconds"],
        "usd": gate["usd"]
        | {
            "cap_usd_all_in": context["cap_usd_all_in"],
            "cap_left_for_this_segment_usd": context["cap_left_for_this_segment_usd"],
            "spent_this_segment_usd": round(elapsed * rate, 4),
            "spent_all_segments_usd": round(
                context["spent_closed_segments_usd"] + elapsed * rate, 4
            ),
            "reading": (
                "`cap_usd_all_in` is the ATTEMPT's and never shrinks; what shrinks is"
                " `cap_left_for_this_segment_usd`, and the inequality above is solved against that"
            ),
        },
        **context,
    }


def normalize(path: Path) -> dict:
    """Drop a torn LAST line from the partial jsonl before it goes back up to a replacement pod.

    The copy is taken while the dying pod is still appending, so its final line can be half written.
    Left in place it becomes a torn MIDDLE line on the replacement — the one case both readers refuse
    loudly, on the kill-rule path, on a billed pod. The drop is a byte PREFIX, so every reply that
    landed is left exactly as the pod wrote it, sha and all.
    """
    if not path.exists():
        raise SystemExit(
            f"{rel(path)}: there is nothing to normalize — no reply has been copied back"
        )
    text = path.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line]
    torn = None
    for index, line in enumerate(lines):
        try:
            json.loads(line)
        except json.JSONDecodeError:
            if index != len(lines) - 1:
                raise SystemExit(
                    f"{rel(path)}: line {index + 1} of {len(lines)} is not JSON and it is not the"
                    " last one. That is a damaged file, not the mid-write race — do not send it back"
                    " up. Stop and report."
                ) from None
            torn = line
    if torn is not None:
        path.write_text(text[: len(text) - len(torn)], encoding="utf-8")
    return {
        "path": rel(path),
        "rows": len(lines) - (1 if torn else 0),
        "dropped_chars": 0 if torn is None else len(torn),
        "dropped_a_torn_last_line": torn is not None,
    }


def main(argv: list[str] | None = None, now: datetime | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", nargs="?", const=str(PACK), help="build and verify the pack")
    parser.add_argument(
        "--pre-create-check",
        action="store_true",
        help="the never-two-pods check, to be run BEFORE `pod create`",
    )
    parser.add_argument("--open", action="store_true", help="record a SEGMENT and print its gates")
    parser.add_argument("--pod-id")
    parser.add_argument(
        "--created-at", help="this segment's create response stamp — its meter's zero"
    )
    parser.add_argument("--usd-per-hour", type=float, help="costPerHr, read back from create")
    parser.add_argument("--card", help="the card the create response actually gave")
    parser.add_argument("--gate0", action="store_true", help="the ssh dead-man")
    parser.add_argument("--ssh-ok", action="store_true", help="the endpoint answered: gate 0 GOes")
    parser.add_argument("--close-segment", action="store_true", help="this pod is deleted")
    parser.add_argument("--deleted-at", help="the delete's stamp — the segment's billed end")
    parser.add_argument("--outcome", help="why this segment ended")
    parser.add_argument("--deadlines", action="store_true", help="the boot deadline, right now")
    parser.add_argument("--gate", action="store_true", help="the boot kill rule / the full pass")
    parser.add_argument(
        "--normalize", action="store_true", help="drop a torn last line, before scp"
    )
    parser.add_argument("--ingest", action="store_true", help="the pod's replies -> the evidence")
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--generation-started-at", help="when the on-pod runner was launched")
    args = parser.parse_args(argv)

    if args.normalize:
        print(json.dumps(normalize(args.raw), ensure_ascii=False, indent=2))
        return 0

    record = registration()

    if args.pack or args.ingest:
        with as_this_phase():
            return v5.main(
                ["--pack", args.pack] if args.pack else ["--ingest", "--raw", str(args.raw)]
            )

    if args.pre_create_check:
        state = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {}
        context = segment_context(record, state)
        live = [one for one in state.get("segments", []) if not one.get("deleted_at")]
        if live:
            raise SystemExit(
                f"segment {len(state['segments'])} ({live[-1]['pod_id']}) has no `deleted_at`: as far"
                " as this record knows it is still running, and the ruling is that two meters never"
                " run at once. Delete it, prove it by listing, close it with --close-segment, and"
                " only then create the replacement."
            )
        if context["segment"] >= context["segments_allowed"]:
            raise SystemExit(
                f"{context['segment']} segments are already on record and the ruling allows"
                f" {context['segments_allowed']}. A third dead pod is a DATACENTER STATE, not bad"
                " luck: the attempt STOPs here and the finding is infrastructural."
            )
        print(json.dumps({"may_create": True, **context}, ensure_ascii=False, indent=2))
        return 0

    if args.open:
        for name in ("pod_id", "created_at", "usd_per_hour", "card"):
            if getattr(args, name) is None:
                parser.error(f"--open needs --{name.replace('_', '-')}")
        if not LEDGER.exists():
            raise SystemExit(
                f"{rel(LEDGER)} does not exist: the step's spend anchor is written by"
                f" `runpod_guard.py --step {PHASE} --step-cap"
                f" {record['money']['cap_usd_all_in']}` BEFORE anything billable, and every segment"
                " of this attempt bills that one step."
            )
        state = (
            json.loads(RECORD.read_text(encoding="utf-8"))
            if RECORD.exists()
            else {
                "phase": PHASE,
                "segments": [],
                "gates": [],
            }
        )
        live = [one for one in state["segments"] if not one.get("deleted_at")]
        if live:
            raise SystemExit(
                f"segment {len(state['segments'])} ({live[-1]['pod_id']}) is still open in"
                f" {rel(RECORD)}. Never two pods at once — close it with --close-segment first."
            )
        meter = record["money"]["meter"]
        state["segments"].append(
            {
                "segment": len(state["segments"]) + 1,
                "pod_id": args.pod_id,
                "created_at": args.created_at,
                "card": args.card,
                "usd_per_hour": args.usd_per_hour,
                "usd_per_second": round(args.usd_per_hour / 3600.0, 9),
                "card_registered": meter["card_requested"],
                "usd_per_hour_worked_example": meter["worked_example_usd_per_hour"],
                "priced_at_or_under_the_example": args.usd_per_hour
                <= meter["worked_example_usd_per_hour"],
                "deleted_at": None,
                "billed_seconds": None,
                "billed_usd": None,
                "outcome": None,
            }
        )
        elapsed = elapsed_since(args.created_at, now)
        gate = gate_zero(record, state, elapsed, ssh_ok=False)
        append_gate(state, gate, "open")
        print(json.dumps(state["segments"][-1], ensure_ascii=False, indent=2))
        print(json.dumps(gate, ensure_ascii=False, indent=2))
        return 0

    if args.close_segment:
        if not args.deleted_at:
            parser.error("--close-segment needs --deleted-at: the segment's billed end")
        state = run_record()
        segment = state["segments"][-1]
        if segment.get("deleted_at"):
            raise SystemExit(
                f"segment {segment['segment']} ({segment['pod_id']}) is already closed at"
                f" {segment['deleted_at']} — a second close would rewrite a billed length"
                " ([[rewriting_a_record_resets_state_you_do_not_own]])."
            )
        billed = elapsed_since(segment["created_at"], stamp(args.deleted_at))
        segment["deleted_at"] = args.deleted_at
        segment["billed_seconds"] = round(billed, 1)
        segment["billed_usd"] = round(billed * rate_of(segment), 6)
        segment["outcome"] = args.outcome
        save(state)
        seconds, usd = spent_before(state)
        print(json.dumps(segment, ensure_ascii=False, indent=2))
        print(
            f"closed segment {segment['segment']}: {segment['billed_seconds']} s ="
            f" ${segment['billed_usd']:.6f} · the attempt has billed {round(seconds, 1)} s ="
            f" ${usd:.6f} of ${record['money']['cap_usd_all_in']:.2f}"
        )
        return 0

    state = run_record()
    segment = state["segments"][-1]
    if args.generation_started_at and not segment.get("generation_started_at"):
        segment["generation_started_at"] = args.generation_started_at
        save(state)
    elapsed = elapsed_since(segment["created_at"], now)
    launched = segment.get("generation_started_at")
    generation_at = None if not launched else elapsed_since(segment["created_at"], stamp(launched))

    if args.gate0:
        gate = gate_zero(record, state, elapsed, ssh_ok=args.ssh_ok)
        append_gate(state, gate, "gate0")
        print(json.dumps(gate, ensure_ascii=False, indent=2))
        print(f"VERDICT {gate['verdict']} — {gate['next_step']}")
        return {"GO": 0, "WAIT": 3}.get(gate["verdict"], 2)

    if not PACK.exists():
        raise SystemExit(
            f"{rel(PACK)} does not exist, and the gate reads it for the per-unit payable counts the"
            " projection's second leg needs. Run `--pack` first — and write it to THAT path, because"
            " this is where every later command looks."
        )
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    rows = raw_rows(args.raw) if args.raw.exists() else []

    if args.deadlines or (args.gate and not rows):
        gate = deadlines(record, state, elapsed, generation_at) | {
            "read_from": v5._read_from(args.raw)
        }
        append_gate(state, gate, "boot_kill")
        print(json.dumps(gate, ensure_ascii=False, indent=2))
        if not args.gate:
            return 0
        print(
            f"VERDICT {gate['verdict']} — no reply in {rel(args.raw)}"
            f" (copied back at {gate['read_from']['copied_back_at']})"
        )
        return 2 if gate["verdict"] == "KILL" else 3

    if args.gate:
        gate = projection(record, state, rows, elapsed, pack) | {
            "read_from": v5._read_from(args.raw)
        }
        append_gate(state, gate, "full_pass")
        print(json.dumps(gate, ensure_ascii=False, indent=2))
        print(f"VERDICT {gate['verdict']} — {rel(RECORD)}")
        return 0 if gate["verdict"] == "GO" else 2

    raise SystemExit(
        "one of --pack / --pre-create-check / --open / --gate0 / --close-segment / --deadlines /"
        " --gate / --normalize / --ingest is required"
    )


if __name__ == "__main__":
    raise SystemExit(main())
