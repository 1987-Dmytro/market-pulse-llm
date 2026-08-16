#!/usr/bin/env python3
"""reader-v3 — the v3 instrument over probe-b's same 23 threads, warm-up first and the gate between.

**What this run may do.** Exactly what `results/prereg_reader_probe_v3.json` registered before any
endpoint existed: read the 23 threads of that record's enumeration — the SAME threads probe-b read,
so the two passes are paired on data and only the instrument moved — one call per thread, through
`reader_thread_gm4_v3` on the READER config. One attempt, no retry.

**Everything the go/no-go does is probe-b's arithmetic, unchanged**, and the pieces that cannot
differ are IMPORTED from that driver rather than retyped: the population and per-request checks, the
handshake, the reply-count reading. What is new here is what the registration made new — the task,
the ledger, and the comparison the projection is against (probe-b's 4090 rather than probe-a's L4).

**The stop threshold, stated rather than left implicit.** The registration's `max_slowdown_vs_probe_b`
of 1.165 is a bound on the WHOLE pass (847.8 billed seconds ÷ probe-b's 727.664). The predicate this
gate actually stops on is stricter, because the warm-up's own seconds are inside the total and the
remainder is projected from them: with 3 warm-up threads / 11 payable against 20 / 123 unread, the
per-payable projection binds at 11.18x and the warm-up may bill at most (cap − setup) ÷ (rate × 12.18)
= 69.59 s. probe-b billed 62.276 s for exactly this draw, so the room is **1.117x**, not 1.165x. Both
numbers land in the record; conflating them is how a gate says GO on a run the cap cannot pay for.

**Which reading of «billed» is taken is recorded, not assumed.** `EndpointClient.timing()` starts its
wall clock at the first request of the PROCESS, which is `info()`. Run against a cold endpoint that
call blocks through the boot and the boot lands inside `wall_seconds` — a ~180 s reading on a gate
whose threshold is 69.59 s, i.e. a STOP that is an artefact of where a process began. The pessimistic
max is kept (it is probe-b's rule and the pairing rests on it) and all three legs are persisted, with
a loud line when wall runs far ahead of the per-job sum.

**Every reply is persisted raw** to `results/reader_v3_w1.jsonl` as it arrives — the rendered request
itself and its sha, the reply verbatim, the parse outcome with `repairs` or the refusal's reason, the
timings, the billed seconds and `finish_reason`. The contract's sitting rule: a row that exists only
in an aggregate cannot be shown to the operator afterwards.

    PYTHONPATH=src python3 scripts/read_threads_reader_v3.py --endpoint <ID> --handshake
    PYTHONPATH=src python3 scripts/read_threads_reader_v3.py --endpoint <ID> --warm-up
    PYTHONPATH=src python3 scripts/read_threads_reader_v3.py --endpoint <ID> --run
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import eval_zero_shot as runner  # noqa: E402
import read_threads_probe_b as probe_b  # noqa: E402
import runpod_guard as guard  # noqa: E402
import write_reader_prereg_v2 as writer  # noqa: E402

from market_pulse import prompts, serving  # noqa: E402

PHASE = "reader-v3"
PREREG = REPO_ROOT / "results" / "prereg_reader_probe_v3.json"
LEDGER = guard.step_ledger_path(PHASE)
EVIDENCE = REPO_ROOT / "results" / "reader_v3_w1.jsonl"
RECORD = REPO_ROOT / "results" / "reader_v3_run.json"
PROBE_B_RUN = REPO_ROOT / "results" / "reader_probe_b_run.json"

ENDPOINT_ENV = "RUNPOD_READER_V3_ENDPOINT"

JOB_TIMEOUT_S = 900.0
JOB_TTL_S = 1800.0
"""One thread per job, the endpoint's own execution budget. `serving.execution_policy` is the one
place these seconds become the milliseconds the API stores."""

BOOT_IN_THE_WINDOW_S = 30.0
"""How far `wall_seconds` may run ahead of the per-job sum before the reading is called out.

Not a threshold anything branches on — the pessimistic max is taken either way. probe-b's warm-up
read 62.276 s wall against 54.4 s of per-job execution, so ~8 s is the ordinary overhead of three
sequential jobs; a gap the size of a boot is a different fact and has to be visible in the record
rather than inferred from a verdict."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def registration() -> dict:
    """The pre-registration, refused unless it is committed and unmodified.

    probe-b's two checks, kept local rather than imported: they are the money path's outermost
    guard and they name THIS record's path in both messages. A plan that is untracked is not a
    pre-registration, and a plan that differs from HEAD is one somebody could still edit once the
    numbers are in.
    """
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(PREREG)], cwd=REPO_ROOT, capture_output=True
    )
    if tracked.returncode != 0:
        raise SystemExit(
            f"{rel(PREREG)} is not tracked by git. The registration is the pre-registration:"
            " until it is committed, nothing stops it from being rewritten once the numbers are in."
        )
    dirty = subprocess.run(
        ["git", "diff", "HEAD", "--quiet", "--", str(PREREG)], cwd=REPO_ROOT, capture_output=True
    )
    if dirty.returncode != 0:
        raise SystemExit(
            f"{rel(PREREG)} differs from HEAD. The committed registration is the one this run is"
            " read against — and this one is FROZEN: restore the file, do not commit the change."
        )
    return json.loads(PREREG.read_text(encoding="utf-8"))


def anchor(balance: float, record: dict) -> dict:
    """The step's spend anchor, written BEFORE the first request and never regenerated.

    In the runbook's order `runpod_guard --step reader-v3 --step-cap 0.35` writes this file before
    the staging pod, so this branch never fires; it exists so a driver run without the guard still
    cannot spend against a counter that does not exist.
    """
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {
        guard.step_anchor_key(PHASE): balance,
        f"{PHASE}_cap_usd": float(record["money"]["cap_usd_all_in"]),
        "anchored_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "note": (
            "reader-v3's own anchor. Step spend = this balance minus the balance now, corroborated"
            " by the guard's billing walk over the same window. Written before the first request;"
            " regenerating it would reset the counter to today's balance."
        ),
        "gpu_sessions": [],
    }


def save_ledger(record: dict) -> None:
    LEDGER.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def persist(rows: list[dict]) -> None:
    """Append the evidence, one JSON object per line, flushed as it arrives."""
    with EVIDENCE.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()


def evidence_rows() -> list[dict]:
    if not EVIDENCE.exists():
        return []
    return [json.loads(line) for line in EVIDENCE.read_text(encoding="utf-8").splitlines() if line]


def already_read() -> set[str]:
    """Which threads the evidence file already holds — the warm-up is not bought twice."""
    return {row["thread"] for row in evidence_rows()}


def read_threads(client, record: dict, batch: list[dict]) -> list[dict]:
    """Send a slice of threads one job at a time, persisting each reply as it lands.

    The row carries the rendered REQUEST as well as its sha (the contract's step 6): the sha proves
    the request is the registered one, and only the text itself lets a reader see what the model was
    actually shown when a verdict is argued about afterwards.
    """
    task = record["instruments"]["task"]
    rows = []
    for thread in batch:
        before = client.timing() or {}
        started = time.monotonic()
        replies = client.read(task, [probe_b.job_item(thread)])
        after = client.timing() or {}
        reply = replies[0]
        try:
            parsed, reason = prompts.parse_reply(task, reply["content"]), None
        except prompts.ParseError as err:
            parsed, reason = None, err.reason
        row = {
            "thread": probe_b.key_of(thread),
            "channel": thread["channel"],
            "post_id": thread["post_id"],
            "injected": thread["injected"],
            "cases": thread["cases"],
            "payable_comments": len(thread["comments"]),
            "task": task,
            "prompt_sha256": record["instruments"]["prompt_sha256"][task],
            "rendering_sha256": writer.rendering_sha256(thread, task),
            "request": writer.rendering(thread, task),
            "reply": reply["content"],
            "finish_reason": reply.get("finish_reason"),
            "usage": reply.get("usage"),
            "parsed": parsed,
            "repairs": None if parsed is None else parsed["repairs"],
            "parse_error": reason,
            "seconds": {
                "wall": round(time.monotonic() - started, 3),
                "worker": round(
                    float(after.get("worker_seconds") or 0)
                    - float(before.get("worker_seconds") or 0),
                    3,
                ),
            },
        }
        persist([row])
        rows.append(row)
        state = "parsed" if parsed else f"REFUSED ({reason})"
        repairs = f" · repairs {row['repairs']}" if row["repairs"] else ""
        print(
            f"  {row['thread']:32s} {row['payable_comments']:3d} payable ·"
            f" {row['seconds']['worker']:6.1f} s worker · {state}{repairs}"
            f" · finish {row['finish_reason']}"
        )
    return rows


def billed_readings(client, rows: list[dict]) -> dict:
    """The three readings of what the warm-up was billed, and which one the gate takes.

    probe-b's rule, kept: the pessimistic maximum of the client's own two figures and the sum the
    persisted rows carry, because `worker_seconds` misses the gaps a `workersMax: 1` endpoint is up
    and charged through, and a `--warm-up` re-invoked after the draw was already bought sends no job
    at all. What is new is that all three are RECORDED, so a wall clock that swallowed a cold boot
    is visible in the artefact instead of arriving as an unexplained STOP.
    """
    timing = client.timing() or {}
    live_worker = float(timing.get("worker_seconds") or 0.0)
    live_wall = float(timing.get("wall_seconds") or 0.0)
    persisted = sum(float(row["seconds"]["worker"]) for row in rows)
    taken = max(live_worker, live_wall, persisted)
    return {
        "live_worker_seconds": round(live_worker, 3),
        "live_wall_seconds": round(live_wall, 3),
        "persisted_worker_seconds": round(persisted, 3),
        "taken": round(taken, 3),
        "which": (
            "live_wall_seconds"
            if taken == live_wall
            else "live_worker_seconds"
            if taken == live_worker
            else "persisted_worker_seconds"
        ),
        "wall_ahead_of_the_jobs_by": round(live_wall - persisted, 3),
        "reading": (
            "the pessimistic maximum, probe-b's rule. `wall_seconds` starts at this PROCESS's first"
            " request, which is the handshake: run against a cold endpoint it carries the boot, and"
            f" a gap over {BOOT_IN_THE_WINDOW_S:.0f} s says so on the line below rather than in a"
            " verdict nobody can explain"
        ),
    }


def probe_b_warm_up() -> dict:
    """probe-b's own warm-up figures, read from the record ITS driver wrote.

    Never from a sentence in a report: the same three threads on the same card is the only paired
    comparison this gate has, and a hand-typed 62.276 would be a second reading of it.
    """
    run = json.loads(PROBE_B_RUN.read_text(encoding="utf-8"))
    warm = run["go_no_go"]["warm_up"]
    return {
        "billed_seconds": warm["billed_seconds"],
        "seconds_per_thread": warm["seconds_per_thread"],
        "seconds_per_payable_comment": warm["seconds_per_payable_comment"],
        "endpoint": run["endpoint"],
        "gpu": ((run.get("worker") or {}).get("runtime") or {}).get("gpu"),
        "record": rel(PROBE_B_RUN),
    }


def projection(rows: list[dict], kept: list[dict], record: dict, billed: dict, rate: float) -> dict:
    """The go/no-go: what the UNREAD remainder will cost, on top of what is already spent.

    probe-b's corrected arithmetic byte for byte — the remainder is projected and never the whole
    population, the measured setup is inside the total, and both projections are computed with the
    pessimistic one binding. What this version adds is the threshold read backwards out of the same
    inequality: the billed seconds the warm-up may spend and still fit. A gate that only reports its
    verdict cannot be checked against the registration's 1.165x, and the two are different numbers.
    """
    done = {row["thread"] for row in rows}
    remainder = [one for one in kept if probe_b.key_of(one) not in done]
    seconds = float(billed["taken"])
    warm_threads = len(rows)
    warm_payable = sum(row["payable_comments"] for row in rows) or 1
    per_thread = seconds / warm_threads
    per_payable = seconds / warm_payable

    left_threads = len(remainder)
    left_payable = sum(len(one["comments"]) for one in remainder)
    by_thread = per_thread * left_threads
    by_payable = per_payable * left_payable
    binding = max(by_thread, by_payable)

    setup = float(record["money"]["arithmetic"]["setup_usd"])
    cap = float(record["money"]["cap_usd_all_in"])
    spent = setup + seconds * rate
    total = spent + binding * rate

    # the same inequality, solved for the seconds instead of for the dollars
    factor = max(left_threads / warm_threads, left_payable / warm_payable)
    affordable = (cap - setup) / (rate * (1 + factor))
    paired = probe_b_warm_up()
    return {
        "warm_up": {
            "threads": warm_threads,
            "payable_comments": warm_payable,
            "billed_seconds": round(seconds, 3),
            "billed_readings": billed,
            "seconds_per_thread": round(per_thread, 3),
            "seconds_per_payable_comment": round(per_payable, 3),
            "probe_b_on_the_same_draw": paired,
            "slowdown_vs_probe_bs_warm_up": round(seconds / float(paired["billed_seconds"]), 3),
        },
        "remainder": {"threads": left_threads, "payable_comments": left_payable},
        "rate_usd_per_second": rate,
        "projections": {
            "by_thread": {
                "seconds": round(by_thread, 1),
                "usd": round(by_thread * rate, 4),
                "rule": f"mean seconds per thread × {left_threads} unread",
            },
            "by_payable_comment": {
                "seconds": round(by_payable, 1),
                "usd": round(by_payable * rate, 4),
                "rule": f"seconds ÷ warm-up payable × {left_payable} unread payable",
            },
            "binding": {
                "seconds": round(binding, 1),
                "usd": round(binding * rate, 4),
                "which": "by_thread" if by_thread >= by_payable else "by_payable_comment",
            },
        },
        "money": {
            "cap_usd_all_in": cap,
            "setup_usd": setup,
            "warm_up_usd": round(seconds * rate, 4),
            "spent_so_far_usd": round(spent, 4),
            "projected_total_usd": round(total, 4),
            "headroom_usd": round(cap - total, 4),
        },
        "stop_threshold": {
            "warm_up_billed_seconds_that_still_fit": round(affordable, 3),
            "binding_factor": round(factor, 4),
            "as_a_ratio_to_probe_bs_warm_up": round(
                affordable / float(paired["billed_seconds"]), 3
            ),
            "registered_max_slowdown_vs_probe_b": record["money"]["arithmetic"][
                "max_slowdown_vs_probe_b"
            ],
            "reading": (
                "the registered 1.165x bounds the WHOLE pass (the seconds the cap buys after setup ÷"
                " probe-b's 727.664). This gate stops on the warm-up, whose own seconds are also"
                " inside the total, so the room it has is (cap − setup) ÷ (rate × (1 + binding"
                " factor)) — the stricter of the two, and the one a GO here actually means"
            ),
            "the_verdict_re_derives_from_here": (
                "`warm_up.billed_seconds` ≤ this threshold IS the verdict, and it is the pair to"
                " check it against. The money block is published rounded to four decimals, and at"
                " the margin $0.3500064 prints as $0.3500 — a reader adding those figures up would"
                " get a GO out of a STOP ([[a_record_must_re_derive_from_what_it_publishes]])"
            ),
        },
        "verdict": "GO" if total <= cap else "STOP",
        "reading": (
            "the projection is of the UNREAD remainder and is added to what has already been"
            " billed, setup included. A projection of the whole population compared against the"
            " cap's leftover counts the warm-up twice"
        ),
    }


def main(argv: list[str] | None = None, client_factory=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", default=os.environ.get(ENDPOINT_ENV))
    parser.add_argument("--handshake", action="store_true", help="info only, then stop")
    parser.add_argument("--warm-up", action="store_true", help="the registered draw, then the gate")
    parser.add_argument("--run", action="store_true", help="the rest of the population, after a GO")
    parser.add_argument("--rate", type=float, default=None, help="usd per billed second")
    args = parser.parse_args(argv)

    record = registration()
    kept = probe_b.threads_of(record)
    by_key = {probe_b.key_of(one): one for one in kept}
    rate = (
        args.rate
        if args.rate is not None
        else float(record["money"]["arithmetic"]["rate_usd_per_second"])
    )

    if not args.endpoint:
        raise SystemExit(f"--endpoint or {ENDPOINT_ENV} is required")
    factory = client_factory or (
        lambda: serving.EndpointClient(
            args.endpoint,
            runner.runpod_api_key(),
            retries=0,
            forward_batch_size=1,
            policy=serving.execution_policy(JOB_TIMEOUT_S, JOB_TTL_S),
            job_timeout=JOB_TIMEOUT_S,
            submit="run",
        )
    )
    client = factory()

    ledger = anchor(guard.balance(), record)
    ledger[f"{PHASE}_cap_usd"] = float(record["money"]["cap_usd_all_in"])
    save_ledger(ledger)

    info = probe_b.handshake(client, record)
    print(
        f"handshake OK · worker {info.get('serving_config')} · commit {info.get('repo_commit')}"
        f" · runtime {(info.get('runtime') or {}).get('gpu_name')}"
    )
    if args.handshake:
        return 0

    drawn = list(record["go_no_go"]["warm_up"]["threads"])
    done = already_read()

    if args.warm_up:
        batch = [by_key[name] for name in drawn if name not in done]
        if batch:
            print(f"warm-up: {len(batch)} of {len(drawn)} threads")
            read_threads(client, record, batch)
        rows = [row for row in evidence_rows() if row["thread"] in drawn]
        billed = billed_readings(client, rows)
        if billed["wall_ahead_of_the_jobs_by"] > BOOT_IN_THE_WINDOW_S:
            print(
                f"  NOTE: wall runs {billed['wall_ahead_of_the_jobs_by']:.1f} s ahead of the jobs'"
                " own seconds — a cold boot inside this process's window would look exactly like"
                " this, and the gate is taking the larger reading.",
                file=sys.stderr,
            )
        gate = projection(rows, kept, record, billed, rate)
        RECORD.write_text(
            json.dumps(
                {"phase": PHASE, "endpoint": args.endpoint, "go_no_go": gate, "worker": info},
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(json.dumps(gate["projections"], ensure_ascii=False, indent=2))
        print(json.dumps(gate["money"], ensure_ascii=False, indent=2))
        print(json.dumps(gate["stop_threshold"], ensure_ascii=False, indent=2))
        print(f"VERDICT {gate['verdict']} — {rel(RECORD)}")
        return 0 if gate["verdict"] == "GO" else 2

    if args.run:
        gate = json.loads(RECORD.read_text(encoding="utf-8"))["go_no_go"]
        if gate["verdict"] != "GO":
            raise SystemExit(
                f"the go/no-go verdict is {gate['verdict']} — the run may not open."
                " The attempt stays intact and the measured rate goes to the operator."
            )
        batch = [one for one in kept if probe_b.key_of(one) not in done]
        print(f"run: {len(batch)} threads of {len(kept)} ({len(done)} already read)")
        read_threads(client, record, batch)
        seconds = billed_readings(client, evidence_rows())
        print(f"billed so far: {seconds['taken'] * rate:.4f} usd ({seconds['which']})")
        return 0

    raise SystemExit("one of --handshake / --warm-up / --run is required")


if __name__ == "__main__":
    raise SystemExit(main())
