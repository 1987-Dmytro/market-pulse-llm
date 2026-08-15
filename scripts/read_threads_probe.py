#!/usr/bin/env python3
"""probe-a D5 — the reader over window-1's threads, warm-up first and the go/no-go between.

**What this run may do.** Exactly what `results/prereg_reader_probe.json` registered before any
endpoint existed: read the 111 threads of the census cell `narrow|silencers_on`, one call per
thread, through `reader_thread_gm4` on the READER config. One attempt, no retry.

**The order is the money.** The warm-up's three threads are drawn by the registration, not by this
script; their measured seconds are projected two ways — per thread and per payable comment — and the
PESSIMISTIC projection is what the two ceilings are read against. Over either one, the run STOPS
before any further call: the attempt stays intact and the measured rate goes back to the operator.

**What it refuses before it spends.**

- a registration that is untracked or MODIFIED — tracked-but-edited is the case a shallow check
  misses, and it is the one that would let the plan be rewritten once the numbers are in;
- an endpoint that is not serving what the registration pinned (`assert_serving`), including the
  reader prompt's sha as THIS checkout renders it — a volume a session behind fails the handshake
  instead of reading happily under the old text;
- a thread that is not in the registered population, or a population whose digest has moved.

**Every reply is persisted raw** to `results/reader_probe_w1.jsonl` as it arrives — the rendering's
sha, the reply verbatim, the parse outcome, the timings and the billed seconds. The sitting is
unbuildable without per-row evidence, and a run that dies at thread 90 must leave 89 behind.

    PYTHONPATH=src python3 scripts/read_threads_probe.py --endpoint <ID> --handshake
    PYTHONPATH=src python3 scripts/read_threads_probe.py --endpoint <ID> --warm-up
    PYTHONPATH=src python3 scripts/read_threads_probe.py --endpoint <ID> --run
"""

import argparse
import hashlib
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
import reader_population as population  # noqa: E402
import runpod_guard as guard  # noqa: E402

from market_pulse import prompts, serving  # noqa: E402

PHASE = "probe-a"
PREREG = REPO_ROOT / "results" / "prereg_reader_probe.json"
LEDGER = REPO_ROOT / "results" / "spend_probe_a.json"
EVIDENCE = REPO_ROOT / "results" / "reader_probe_w1.jsonl"
RECORD = REPO_ROOT / "results" / "reader_probe_run.json"

ENDPOINT_ENV = "RUNPOD_PROBE_A_ENDPOINT"
API_KEY_ENV = "RUNPOD_API_KEY"

JOB_TIMEOUT_S = 900.0
JOB_TTL_S = 1800.0
"""One thread per job, so 900 s is ~30× the longest reading anyone expects and still far under the
endpoint's own budget. The ttl clock starts at SUBMISSION and has to outlast the queue as well as
the execution — `serving.execution_policy` is the one place seconds become milliseconds."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def registration() -> dict:
    """The pre-registration, refused unless it is committed and unmodified.

    A plan that is untracked is not a pre-registration, and a plan that differs from HEAD is one
    somebody could still edit once the numbers are in. Both are checked against git rather than
    inferred, because both are cheap to check and impossible to notice afterwards.
    """
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(PREREG)],
        cwd=REPO_ROOT,
        capture_output=True,
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
            " read against — commit the change, or restore the file, before spending on it."
        )
    return json.loads(PREREG.read_text(encoding="utf-8"))


def threads_of(record: dict) -> list[dict]:
    """The registered population, re-derived and held to the digest the registration pinned."""
    kept = population.population()
    digest = record["population"]["enumeration"]["digest"]
    body = "\n".join(
        f"{one['channel']}:{one['post_id']}\t"
        + ",".join(str(row["msg_id"]) for row in one["comments"])
        for one in kept
    )
    got = hashlib.sha256(body.encode("utf-8")).hexdigest()
    if got != digest:
        raise SystemExit(
            f"the population's digest is {got[:16]}… and the registration pinned {digest[:16]}…."
            " This run would be reading a different 111 threads than the one it registered."
        )
    return kept


def key_of(thread: dict) -> str:
    return serving.reader_key(thread)


def job_item(thread: dict) -> dict:
    """One thread in the shape the worker's `ReaderClient` renders from."""
    return {
        "channel": thread["channel"],
        "post_id": thread["post_id"],
        "post": thread["post_text"],
        "comments": [[row["msg_id"], row["text"]] for row in thread["comments"]],
    }


def rendering_sha256(thread: dict) -> str:
    """The sha of the request the worker will render — computed HERE from the same function.

    Not the reply's and not the thread's: what a record has to be able to say is that the string
    the model read is the string this checkout renders. The worker renders it from the same
    `prompts.reader_messages_gm4`, so a volume a session behind moves this number as well as the
    prompt sha the handshake already compares.
    """
    content = prompts.reader_messages_gm4(
        thread["channel"],
        thread["post_id"],
        thread["post_text"],
        [(row["msg_id"], row["text"]) for row in thread["comments"]],
    )[0]["content"]
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def expected_worker(record: dict) -> dict:
    """What `assert_serving` compares the endpoint's `info` against — read from the registration."""
    serving_block = record["instruments"]["serving"]
    return {
        "serving_config": serving_block["serving_config"],
        "merge_state": serving_block["merge_state"],
        "adapter_sha256": None,
        "quantization": serving_block["quantization"],
        "chat_template": serving_block["chat_template"],
        "max_new_tokens": record["instruments"]["ceilings"]["output_tokens"],
        "model": serving_block["model"],
        "revision_requested": serving_block["model_revision"],
        "reader_prompt_sha256": record["instruments"]["prompt_sha256"],
    }


def handshake(client, record: dict) -> dict:
    """`info`, compared whole against the registration. A mismatch is a STOP, not a warning."""
    info = client.info()
    # the prompt FIRST, and against what this checkout renders rather than against the pin.
    # `assert_serving` would refuse the same row one line later with a message about a
    # configuration, and the cause is not a configuration: it is a volume a session behind, which
    # is the failure that actually happens ([[a_new_guard_can_be_shadowed_by_an_old_one]] — read
    # the message, not the exit)
    live = prompts.prompt_sha256(prompts.READER_TASK)
    if info.get("reader_prompt_sha256") != live:
        raise SystemExit(
            f"the worker serves reader prompt {str(info.get('reader_prompt_sha256'))[:12]}… and"
            f" this checkout renders {live[:12]}…. The volume is not at this session's commit."
        )
    serving.assert_serving(info, expected_worker(record))
    return info


def anchor(balance: float) -> dict:
    """The session's spend anchor, written BEFORE the first request and never regenerated.

    Same footgun as every other `spend_*.json` in this repo: delete it and the counter silently
    restarts at today's balance. `runpod_guard` walks pods and volumes only, so serverless spend is
    invisible to it — this anchor and the endpoint's own clock are the two readings that see it.
    """
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    record = {
        f"runpod_balance_at_{PHASE}_start": balance,
        f"{PHASE}_cap_usd": None,  # filled below from the registration, never typed
        "anchored_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "note": (
            "probe-a's own anchor. Session spend = this balance minus the balance now. Written"
            " before the first request; regenerating it would reset the counter to today's balance."
        ),
        "sessions": [],
    }
    return record


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


def already_read() -> set[str]:
    """Which threads the evidence file already holds — the warm-up is not bought twice."""
    if not EVIDENCE.exists():
        return set()
    return {
        json.loads(line)["thread"]
        for line in EVIDENCE.read_text(encoding="utf-8").splitlines()
        if line
    }


def read_threads(client, record: dict, batch: list[dict]) -> list[dict]:
    """Send a slice of threads one job at a time, persisting each reply as it lands."""
    rows = []
    for thread in batch:
        before = client.timing() or {}
        started = time.monotonic()
        replies = client.read(prompts.READER_TASK, [job_item(thread)])
        after = client.timing() or {}
        reply = replies[0]
        try:
            parsed, reason = prompts.parse_reply(prompts.READER_TASK, reply["content"]), None
        except prompts.ParseError as err:
            parsed, reason = None, err.reason
        row = {
            "thread": key_of(thread),
            "channel": thread["channel"],
            "post_id": thread["post_id"],
            "payable_comments": len(thread["comments"]),
            "task": prompts.READER_TASK,
            "prompt_sha256": record["instruments"]["prompt_sha256"],
            "rendering_sha256": rendering_sha256(thread),
            "reply": reply["content"],
            "finish_reason": reply.get("finish_reason"),
            "usage": reply.get("usage"),
            "parsed": parsed,
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
        print(
            f"  {row['thread']:34s} {row['payable_comments']:3d} payable ·"
            f" {row['seconds']['worker']:6.1f} s worker · {state}"
        )
    return rows


def billed_seconds(client) -> float:
    """What the session has been billed, in the unit serverless charges: the larger of the two.

    `worker_seconds` is per-job execution and misses the gaps a `workersMax: 1` endpoint is up and
    charged through; `wall_seconds` is the span the client held it. The pessimistic one wins.
    """
    timing = client.timing() or {}
    return max(float(timing.get("worker_seconds") or 0.0), float(timing.get("wall_seconds") or 0.0))


def projection(rows: list[dict], record: dict, billed: float, rate: float) -> dict:
    """Both projections of the window, and the ceilings they are read against.

    Per thread and per payable comment, because a rate is a property of the sample it was measured
    on and the warm-up's threads are middle-sized ones. The PESSIMISTIC projection binds — the same
    rule `runpod_guard` uses for two readings of a balance.
    """
    threads = record["population"]["threads"]
    payable = record["population"]["payable_comments"]
    warm_threads = len(rows)
    warm_payable = sum(row["payable_comments"] for row in rows) or 1
    per_thread = billed / warm_threads
    per_payable = billed / warm_payable
    by_thread = per_thread * threads
    by_payable = per_payable * payable
    binding = max(by_thread, by_payable)
    cap = float(record["money"]["cap_usd_all_in"])
    minutes = float(record["bars"]["5_time_and_cost"]["thresholds"]["window_minutes_billed"])
    return {
        "warm_up": {
            "threads": warm_threads,
            "payable_comments": warm_payable,
            "billed_seconds": round(billed, 3),
            "seconds_per_thread": round(per_thread, 3),
            "seconds_per_payable_comment": round(per_payable, 3),
        },
        "rate_usd_per_second": rate,
        "projections": {
            "by_thread": {
                "seconds": round(by_thread, 1),
                "usd": round(by_thread * rate, 4),
                "rule": f"mean seconds per thread × {threads}",
            },
            "by_payable_comment": {
                "seconds": round(by_payable, 1),
                "usd": round(by_payable * rate, 4),
                "rule": f"seconds ÷ warm-up payable × {payable}",
            },
            "binding": {
                "seconds": round(binding, 1),
                "usd": round(binding * rate, 4),
                "which": "by_thread" if by_thread >= by_payable else "by_payable_comment",
            },
        },
        "ceilings": {
            "cap_usd_all_in": cap,
            "already_billed_usd": round(billed * rate, 4),
            "remaining_usd": round(cap - billed * rate, 4),
            "window_minutes_billed": minutes,
        },
        "verdict": (
            "STOP" if binding * rate > cap - billed * rate or binding / 60.0 > minutes else "GO"
        ),
        "reading": (
            "the projection is of the WHOLE window; it is compared against what the cap has left"
            " after the warm-up, because the warm-up's own spend is inside the same cap"
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
    kept = threads_of(record)
    by_key = {key_of(one): one for one in kept}
    rate = (
        args.rate
        if args.rate is not None
        else float(record["bars"]["5_time_and_cost"]["prior"]["rate_usd_per_second"])
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

    ledger = anchor(guard.balance())
    ledger[f"{PHASE}_cap_usd"] = float(record["money"]["cap_usd_all_in"])
    save_ledger(ledger)

    info = handshake(client, record)
    print(f"handshake OK · worker {info.get('serving_config')} · commit {info.get('repo_commit')}")
    if args.handshake:
        return 0

    drawn = [key_of(one) for one in record["go_no_go"]["warm_up"]["drawn"]]
    done = already_read()

    if args.warm_up:
        batch = [by_key[key] for key in drawn if key not in done]
        if batch:
            print(f"warm-up: {len(batch)} of {len(drawn)} threads")
            read_threads(client, record, batch)
        gate = projection(
            [
                json.loads(line)
                for line in EVIDENCE.read_text(encoding="utf-8").splitlines()
                if line and json.loads(line)["thread"] in drawn
            ],
            record,
            billed_seconds(client),
            rate,
        )
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
        print(f"VERDICT {gate['verdict']} — {rel(RECORD)}")
        return 0 if gate["verdict"] == "GO" else 2

    if args.run:
        gate = json.loads(RECORD.read_text(encoding="utf-8"))["go_no_go"]
        if gate["verdict"] != "GO":
            raise SystemExit(
                f"the go/no-go verdict is {gate['verdict']} — the run may not open."
                " The attempt stays intact and the measured rate goes to the operator."
            )
        batch = [one for one in kept if key_of(one) not in done]
        print(f"run: {len(batch)} threads of {len(kept)} ({len(done)} already read)")
        read_threads(client, record, batch)
        print(f"billed so far: {billed_seconds(client) * rate:.4f} usd")
        return 0

    raise SystemExit("one of --handshake / --warm-up / --run is required")


if __name__ == "__main__":
    raise SystemExit(main())
