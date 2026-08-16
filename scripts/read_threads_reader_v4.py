#!/usr/bin/env python3
"""reader-v4 — the Mac half: the pack, the pod's clock, and the replies turned into evidence.

The generation runs on a rented pod (`scripts/reader_v4_pod_runner.py`); everything that decides
anything runs here. The split is the registration's: the parser and the scorer are the instrument
and they are pinned by sha, and the pod's checkout is deliberately a commit behind.

**The clock starts at `pod create`.** A pod bills for every second it exists — provisioning,
booting, generating, idle — so `results/prereg_reader_probe_v4.json` states the cap in SECONDS and
every gate here is read against seconds since the create response. v3's gates all sat downstream of
a boot that was already spending, and there was no branch that could fire
([[a_gate_downstream_of_the_spend]]).

**Two deadlines, and the tighter one binds.** The contract's twelve minutes is a ceiling measured
from the generation process starting; the other is the affordability deadline — usable seconds minus
the reading projection — measured from `create`, because that is when the meter did. They are put on
one axis before they are compared, and both are printed whenever either is asked for: a gate that
reports only its verdict cannot be checked ([[a_published_ratio_is_not_the_gates]]).

**Nothing here calls RunPod.** The pod id, its create stamp and its price come from the runbook's
own commands and are RECORDED, so the arithmetic can be re-run by hand against the same numbers.

    PYTHONPATH=src python3 scripts/read_threads_reader_v4.py --pack results/reader_v4_pack.json
    PYTHONPATH=src python3 scripts/read_threads_reader_v4.py --open --pod-id <ID> \\
        --created-at 2026-08-16T18:00:00Z --usd-per-hour 0.74 --card 'NVIDIA GeForce RTX 4090'
    PYTHONPATH=src python3 scripts/read_threads_reader_v4.py --deadlines
    PYTHONPATH=src python3 scripts/read_threads_reader_v4.py --gate --raw results/reader_v4_pod.jsonl
    PYTHONPATH=src python3 scripts/read_threads_reader_v4.py --ingest --raw results/reader_v4_pod.jsonl
"""

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import read_threads_probe_b as probe_b  # noqa: E402
import runpod_guard as guard  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_reader_prereg_v2 as writer  # noqa: E402

from market_pulse import prompts  # noqa: E402

PHASE = "reader-v4"
PREREG = REPO_ROOT / "results" / "prereg_reader_probe_v4.json"
LEDGER = guard.step_ledger_path(PHASE)
PACK = REPO_ROOT / "results" / "reader_v4_pack.json"
RAW = REPO_ROOT / "results" / "reader_v4_pod.jsonl"
EVIDENCE = REPO_ROOT / "results" / "reader_v4_w1.jsonl"
RECORD = REPO_ROOT / "results" / "reader_v4_run.json"


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def registration() -> dict:
    """The pre-registration, refused unless it is committed and unmodified.

    A plan that is untracked is not a pre-registration, and a plan that differs from HEAD is one
    somebody could still edit once the numbers are in. This record FREEZES when the pod exists, so
    the second check is the one that matters after create.
    """
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(PREREG)], cwd=REPO_ROOT, capture_output=True
    )
    if tracked.returncode != 0:
        raise SystemExit(
            f"{rel(PREREG)} is not tracked by git. The registration is the pre-registration: until"
            " it is committed, nothing stops it from being rewritten once the numbers are in."
        )
    dirty = subprocess.run(
        ["git", "diff", "HEAD", "--quiet", "--", str(PREREG)], cwd=REPO_ROOT, capture_output=True
    )
    if dirty.returncode != 0:
        raise SystemExit(
            f"{rel(PREREG)} differs from HEAD. The committed registration is the one this run is"
            " read against — and it is FROZEN: restore the file, do not commit the change."
        )
    return json.loads(PREREG.read_text(encoding="utf-8"))


def build_pack(record: dict) -> dict:
    """The 23 requests as the pod will be given them, every one held to the registration's sha.

    `threads_of` is probe-b's own check and does both halves — the population digest says WHICH
    threads and the per-thread rendering sha says WHAT each of them is. It runs here, on the Mac,
    before anything is created: a thread whose text moved costs $0 to discover now and a pod's boot
    to discover later.
    """
    kept = probe_b.threads_of(record)
    task = record["instruments"]["task"]
    pinned = {one["thread"]: one for one in record["population"]["enumeration"]["threads"]}
    items = []
    for one in kept:
        name = probe_b.key_of(one)
        items.append(
            probe_b.job_item(one)
            | {
                "thread": name,
                "rendering_sha256": writer.rendering_sha256(one, task),
                "payable_comments": len(one["comments"]),
                "cases": one["cases"],
                "injected": one["injected"],
            }
        )
        if items[-1]["rendering_sha256"] != pinned[name]["rendering_sha256"]:
            raise SystemExit(f"{name}: the request moved since the registration — stop and report.")
    return {
        "phase": PHASE,
        "registration": {"record": rel(PREREG), "sha256": summary.sha256_of(PREREG)},
        "task": task,
        # COPIED and not aliased: a pack that shares the registration's own dicts can be edited
        # into agreeing with itself, and the pod's whole handshake is that these two differ when
        # the volume is behind
        "instruments": {
            "prompt_sha256": dict(record["instruments"]["prompt_sha256"]),
            "parser": {"sha256": record["instruments"]["parser"]["sha256"]},
        },
        "serving": dict(record["instruments"]["serving"]),
        "items": items,
        "reading": (
            "the pod renders each item itself and refuses unless its sha equals the one above."
            " Shipping the rendered string would only prove the two machines agree about a string;"
            " what has to be true is that the model is shown what the registration registered"
        ),
    }


def stamp(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def elapsed_since(created_at: str, now: datetime | None = None) -> float:
    """Seconds since the create response — the meter's own clock, not the run's."""
    return ((now or datetime.now(UTC)) - stamp(created_at)).total_seconds()


def stamp_generation(state: dict, launched: str | None) -> dict:
    """Record when the on-pod runner started, once — the zero of the contract's twelve minutes.

    Written the first time it is given and never overwritten: the deadline this stamp places is the
    reason the run may be killed, and a stamp that moved forward would push its own deadline out.
    """
    if launched and not state["pod"].get("generation_started_at"):
        state["pod"]["generation_started_at"] = launched
        save(state)
    return state


def rate_of(pod: dict) -> float:
    return float(pod["usd_per_hour"]) / 3600.0


def usable_seconds(record: dict, rate: float) -> float:
    """What the cap buys at the price actually being charged, less the deletion's own margin.

    Recomputed from `rate` rather than read out of the registration: the registered price is the
    4090's, and the registration's own rule says a create response with a different `costPerHr`
    re-prices every number here before the generation process starts.
    """
    cap = float(record["money"]["cap_usd_all_in"])
    margin = float(record["money"]["arithmetic"]["delete_margin_seconds"])
    return cap / rate - margin


def deadlines(
    record: dict, rate: float, elapsed: float, generation_at: float | None = None
) -> dict:
    """When the FIRST reply must land, on one axis: seconds since `pod create`.

    Two deadlines measured from two different zeros, which is why they are put on a common axis here
    rather than compared as they are stated. The contract's twelve minutes runs from the GENERATION
    process starting; affordability runs from `create`, because that is when the meter did. A
    generation that has not started yet has no ceiling on this axis — the ceiling moves with it —
    and what is reported then is the pre-generation budget: the create-elapsed above which the
    twelve minutes stops being the binding number.

    The affordability side charges the WHOLE 23-thread reading projection after the first reply,
    which counts that first thread's own seconds twice — 31.6 s of deliberate conservatism, kept
    because the alternative is an exact formula whose error is in the direction that opens runs.

    `verdict` is KILL or WAIT and it is the whole kill rule, executable. A deadline a human has to
    eyeball is a deadline that is discovered afterwards, in a bill.
    """
    sums = record["money"]["arithmetic"]
    usable = usable_seconds(record, rate)
    ceiling = float(sums["boot_kill_seconds"])
    reading = float(sums["reading_projection_seconds"])
    affordability = usable - reading
    ceiling_on_the_axis = None if generation_at is None else generation_at + ceiling
    deadline = (
        affordability if ceiling_on_the_axis is None else min(ceiling_on_the_axis, affordability)
    )
    return {
        "elapsed_since_create_seconds": round(elapsed, 1),
        "generation_started_at_create_elapsed": (
            None if generation_at is None else round(generation_at, 1)
        ),
        "usable_seconds": round(usable, 1),
        "usd_per_second": round(rate, 9),
        "spent_so_far_usd": round(elapsed * rate, 4),
        "contract_ceiling_seconds": ceiling,
        "contract_ceiling_as_create_elapsed": (
            None if ceiling_on_the_axis is None else round(ceiling_on_the_axis, 1)
        ),
        "affordability_deadline_as_create_elapsed": round(affordability, 1),
        "reading_projection_seconds": reading,
        "pre_generation_budget_seconds": sums["pre_generation_budget_seconds"],
        "first_reply_must_land_by_create_elapsed": round(deadline, 1),
        "seconds_left": round(deadline - elapsed, 1),
        "which_binds": (
            "affordability — the generation has not started, so the contract's twelve minutes has no"
            " place on this axis yet"
            if ceiling_on_the_axis is None
            else "the contract's twelve minutes"
            if ceiling_on_the_axis <= affordability
            else "affordability — the 23 threads no longer fit behind a boot this long"
        ),
        "verdict": "KILL" if elapsed >= deadline else "WAIT",
        "rule": sums["boot_deadline_rule"],
    }


def projection(record: dict, rate: float, rows: list[dict], elapsed: float, of: int) -> dict:
    """The full-pass gate — projected from the threads that HAVE answered, solved for seconds.

    The registration's inequality, with BOTH legs and the pessimistic one binding: elapsed +
    max(unread threads ÷ read threads, unread payable ÷ read payable) × measured seconds ≤ usable.
    probe-a's rule, probe-b's and v3's, kept — a single-leg projection is looser in the one
    direction a cap guard may not be loose in, and these threads carry between 1 and 15 payable
    comments against a prompt that asks for an output row per comment.

    The threshold is published in the unit the gate measures, because the dollars round to four
    decimals and agree on both sides of a margin ([[a_record_must_rederive_from_what_it_publishes]]).
    """
    usable = usable_seconds(record, rate)
    read = len(rows)
    if not read:
        raise SystemExit("no replies yet — there is nothing to project from")
    payable = {
        one["thread"]: one["payable_comments"]
        for one in record["population"]["enumeration"]["threads"]
    }
    measured = sum(float(row["seconds"]) for row in rows)
    per_thread = measured / read
    unread = of - read
    read_payable = sum(payable[row["thread"]] for row in rows) or 1
    unread_payable = sum(payable.values()) - read_payable
    factor = max(unread / read, unread_payable / read_payable)
    projected = elapsed + factor * measured
    affordable = (usable - elapsed) / (factor * read) if unread else float("inf")
    return {
        "threads_read": read,
        "threads_unread": unread,
        "payable_comments_read": read_payable,
        "payable_comments_unread": unread_payable,
        "elapsed_since_create_seconds": round(elapsed, 1),
        "measured_seconds": round(measured, 3),
        "measured_seconds_per_thread": round(per_thread, 3),
        "projections": {
            "by_thread": {
                "factor": round(unread / read, 4),
                "seconds": round(measured * unread / read, 1),
            },
            "by_payable_comment": {
                "factor": round(unread_payable / read_payable, 4),
                "seconds": round(measured * unread_payable / read_payable, 1),
            },
            "binding": {
                "factor": round(factor, 4),
                "seconds": round(factor * measured, 1),
                "which": "by_thread"
                if unread / read >= unread_payable / read_payable
                else ("by_payable_comment"),
            },
        },
        "probe_b_seconds_per_thread": record["money"]["arithmetic"]["probe_b"][
            "seconds_per_thread"
        ],
        "slowdown_vs_probe_b": round(
            per_thread / float(record["money"]["arithmetic"]["probe_b"]["seconds_per_thread"]), 3
        ),
        "usable_seconds": round(usable, 1),
        "projected_total_seconds": round(projected, 1),
        "headroom_seconds": round(usable - projected, 1),
        "seconds_per_thread_that_still_fits": round(affordable, 3),
        "the_verdict_re_derives_from_here": (
            "`measured_seconds_per_thread` ≤ `seconds_per_thread_that_still_fits` IS the verdict."
            " The dollars below are the same statement rounded, and at the margin both sides of it"
            " print the same figure"
        ),
        "usd": {
            "cap_usd_all_in": float(record["money"]["cap_usd_all_in"]),
            "spent_so_far_usd": round(elapsed * rate, 4),
            "projected_total_usd": round(projected * rate, 4),
            "delete_margin_usd": round(
                float(record["money"]["arithmetic"]["delete_margin_seconds"]) * rate, 4
            ),
        },
        "verdict": "GO" if projected <= usable else "STOP",
    }


def ingest(record: dict, raw: list[dict], pack: dict) -> list[dict]:
    """The pod's raw replies turned into the evidence row the contract lists, parsed HERE.

    The parse is the instrument's and it runs on the machine whose `prompts.py` the registration
    pinned. Each row carries the rendered request as well as its sha: the sha proves the request was
    the registered one, and the text is what lets a reader see what the model was actually shown
    when a verdict is argued about afterwards.
    """
    task = record["instruments"]["task"]
    items = {one["thread"]: one for one in pack["items"]}
    rows = []
    for one in raw:
        item = items[one["thread"]]
        if one["rendering_sha256"] != item["rendering_sha256"]:
            raise SystemExit(
                f"{one['thread']}: the pod answered a request whose sha is"
                f" {one['rendering_sha256'][:16]}… and the pack pinned"
                f" {item['rendering_sha256'][:16]}… — stop and report."
            )
        try:
            parsed, reason = prompts.parse_reply(task, one["reply"]), None
        except prompts.ParseError as err:
            parsed, reason = None, err.reason
        rows.append(
            {
                "thread": one["thread"],
                "channel": item["channel"],
                "post_id": item["post_id"],
                "injected": item["injected"],
                "cases": item["cases"],
                "payable_comments": item["payable_comments"],
                "task": task,
                "prompt_sha256": record["instruments"]["prompt_sha256"][task],
                "rendering_sha256": one["rendering_sha256"],
                "request": prompts.reader_messages_gm4(
                    item["channel"],
                    item["post_id"],
                    item["post"],
                    [(int(msg_id), text) for msg_id, text in item["comments"]],
                    task=task,
                )[0]["content"],
                "reply": one["reply"],
                "finish_reason": one.get("finish_reason"),
                "usage": one.get("usage"),
                "parsed": parsed,
                "repairs": None if parsed is None else parsed["repairs"],
                "parse_error": reason,
                "seconds": {"worker": float(one["seconds"])},
                "elapsed_since_start": one.get("elapsed_since_start"),
                "boot_seconds": one.get("boot_seconds"),
            }
        )
    return rows


def raw_rows(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{rel(path)}: the pod has written nothing yet")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def run_record() -> dict:
    if not RECORD.exists():
        raise SystemExit(f"{rel(RECORD)} does not exist — the pod was never opened with --open")
    return json.loads(RECORD.read_text(encoding="utf-8"))


def save(record: dict) -> None:
    RECORD.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main(argv: list[str] | None = None, now: datetime | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", nargs="?", const=str(PACK), help="build and verify the pack")
    parser.add_argument(
        "--open", action="store_true", help="record the pod and print the deadlines"
    )
    parser.add_argument("--pod-id")
    parser.add_argument("--created-at", help="the create response's stamp — the meter's zero")
    parser.add_argument("--usd-per-hour", type=float, help="costPerHr, read back from create")
    parser.add_argument("--card", help="the card the create response actually gave")
    parser.add_argument("--deadlines", action="store_true", help="the boot deadline, right now")
    parser.add_argument("--gate", action="store_true", help="the boot kill rule / the full pass")
    parser.add_argument("--ingest", action="store_true", help="the pod's replies -> the evidence")
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument(
        "--generation-started-at",
        help="when the on-pod runner was launched; stamped into the run record the first time",
    )
    args = parser.parse_args(argv)

    record = registration()

    if args.pack:
        pack = build_pack(record)
        Path(args.pack).write_text(
            json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"pack {args.pack} · {len(pack['items'])} requests, every sha matches the record")
        print(f"  task {pack['task']} · parser {pack['instruments']['parser']['sha256'][:16]}…")
        return 0

    if args.open:
        for name in ("pod_id", "created_at", "usd_per_hour", "card"):
            if getattr(args, name) is None:
                parser.error(f"--open needs --{name.replace('_', '-')}")
        if not LEDGER.exists():
            raise SystemExit(
                f"{rel(LEDGER)} does not exist: the step's spend anchor is written by"
                f" `runpod_guard.py --step {PHASE} --step-cap 0.35` and the runbook writes it"
                " BEFORE anything billable. A pod that exists against no counter is a pod nothing"
                " is measuring."
            )
        pod = {
            "pod_id": args.pod_id,
            "created_at": args.created_at,
            "card": args.card,
            "usd_per_hour": args.usd_per_hour,
            "usd_per_second": round(args.usd_per_hour / 3600.0, 9),
            "card_registered": record["money"]["meter"]["card_requested"],
            "usd_per_hour_registered": record["money"]["meter"]["usd_per_hour"],
            "priced_as_registered": args.usd_per_hour <= record["money"]["meter"]["usd_per_hour"],
        }
        rate = rate_of(pod)
        gate = deadlines(record, rate, elapsed_since(args.created_at, now))
        save({"phase": PHASE, "pod": pod, "deadlines_at_open": gate})
        print(json.dumps(pod, ensure_ascii=False, indent=2))
        print(json.dumps(gate, ensure_ascii=False, indent=2))
        return 0

    if args.deadlines or args.gate:
        state = stamp_generation(run_record(), args.generation_started_at)
        rate = rate_of(state["pod"])
        elapsed = elapsed_since(state["pod"]["created_at"], now)
        launched = state["pod"].get("generation_started_at")
        generation_at = (
            None if not launched else elapsed_since(state["pod"]["created_at"], stamp(launched))
        )
        rows = raw_rows(args.raw) if args.raw.exists() else []

    if args.deadlines or (args.gate and not rows):
        gate = deadlines(record, rate, elapsed, generation_at) | {
            "read_from": {
                "path": rel(args.raw),
                "exists": args.raw.exists(),
                "copied_back_at": (
                    None
                    if not args.raw.exists()
                    else datetime.fromtimestamp(args.raw.stat().st_mtime, UTC).isoformat(
                        timespec="seconds"
                    )
                ),
                "rule": (
                    "«no reply has landed» is a statement about THIS file, and the pod writes to"
                    " its own. Copy the partial jsonl back BEFORE every gate: a KILL read off a"
                    " file nobody refreshed would kill a healthy run and put the wrong reason in"
                    " this record"
                ),
            }
        }
        save(state | {"boot_kill": gate})
        print(json.dumps(gate, ensure_ascii=False, indent=2))
        if not args.gate:
            return 0
        print(
            f"VERDICT {gate['verdict']} — no reply in {rel(args.raw)}"
            f" (copied back at {gate['read_from']['copied_back_at']})"
        )
        return 2 if gate["verdict"] == "KILL" else 3

    if args.gate:
        gate = projection(record, rate, rows, elapsed, of=record["population"]["threads"])
        save(state | {"go_no_go": gate})
        print(json.dumps(gate, ensure_ascii=False, indent=2))
        print(f"VERDICT {gate['verdict']} — {rel(RECORD)}")
        return 0 if gate["verdict"] == "GO" else 2

    if args.ingest:
        pack = json.loads(PACK.read_text(encoding="utf-8"))
        rows = ingest(record, raw_rows(args.raw), pack)
        with EVIDENCE.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
        parsed = sum(1 for row in rows if row["parsed"])
        print(
            f"{rel(EVIDENCE)} · {len(rows)} rows · {parsed} parsed · {len(rows) - parsed} refused"
        )
        for row in rows:
            state = "parsed" if row["parsed"] else f"REFUSED ({row['parse_error']})"
            repairs = f" · repairs {row['repairs']}" if row["repairs"] else ""
            print(
                f"  {row['thread']:32s} {row['payable_comments']:3d} payable ·"
                f" {row['seconds']['worker']:6.1f} s · {state}{repairs}"
                f" · finish {row['finish_reason']}"
            )
        return 0

    raise SystemExit("one of --pack / --open / --deadlines / --gate / --ingest is required")


if __name__ == "__main__":
    raise SystemExit(main())
