#!/usr/bin/env python3
"""probe-b — the v2 reader over the registered subset, warm-up first and the go/no-go between.

**What this run may do.** Exactly what `results/prereg_reader_probe_v2.json` registered before any
endpoint existed: read the 23 threads of that record's enumeration — 19 from the census cell and 4
injected past the gate so bars 2 and 3 are reachable — one call per thread, through
`reader_thread_gm4_v2` on the READER config. One attempt, no retry.

**The order is the money, and the arithmetic is not v1's.** probe-a's driver projected the WHOLE
population and compared it against what the cap had left AFTER the warm-up, counting the warm-up's
threads twice; at 111 threads that is 2.7% of the cap and at 23 it is 13%, which is the difference
between a STOP and a GO on a run the cap can afford. Here the UNREAD remainder is what is projected,
and the measured setup plus the warm-up's own billed seconds are added to it. Both projections are
computed — per thread and per payable comment — and the PESSIMISTIC one binds, because this
population's threads are larger than the warm-up's.

**What it refuses before it spends.**

- a registration that is untracked or MODIFIED — tracked-but-edited is the case a shallow check
  misses, and it is the one that would let the plan be rewritten once the numbers are in;
- an endpoint that is not serving what the registration pinned (`assert_serving`), including a sha
  for EVERY registered reader text as this checkout renders them — a volume a session behind fails
  the handshake instead of reading happily under the old wording;
- a thread that is not in the registered population, a population whose digest has moved, or a
  thread whose rendered request does not hash to what the registration pinned for it.

**Every reply is persisted raw** to `results/reader_probe_b_w1.jsonl` as it arrives — the rendering's
sha, the reply verbatim, the parse outcome, the timings and the billed seconds. The sitting is
unbuildable without per-row evidence, and a run that dies at thread 20 must leave 19 behind.

    PYTHONPATH=src python3 scripts/read_threads_probe_b.py --endpoint <ID> --handshake
    PYTHONPATH=src python3 scripts/read_threads_probe_b.py --endpoint <ID> --warm-up
    PYTHONPATH=src python3 scripts/read_threads_probe_b.py --endpoint <ID> --run
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
import probe_b_population as subset  # noqa: E402
import runpod_guard as guard  # noqa: E402
import write_reader_prereg_v2 as writer  # noqa: E402

from market_pulse import prompts, serving  # noqa: E402

PHASE = "probe-b"
PREREG = REPO_ROOT / "results" / "prereg_reader_probe_v2.json"
LEDGER = guard.step_ledger_path(PHASE)
EVIDENCE = REPO_ROOT / "results" / "reader_probe_b_w1.jsonl"
RECORD = REPO_ROOT / "results" / "reader_probe_b_run.json"

ENDPOINT_ENV = "RUNPOD_PROBE_B_ENDPOINT"

JOB_TIMEOUT_S = 900.0
JOB_TTL_S = 1800.0
"""One thread per job, so 900 s is ~16x the longest reading probe-a measured and still far under the
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
            " read against — commit the change, or restore the file, before spending on it."
        )
    return json.loads(PREREG.read_text(encoding="utf-8"))


def threads_of(record: dict) -> list[dict]:
    """The registered population, re-derived and held to the digest AND to every request's sha.

    Two checks and not one: the digest says which threads, and the per-thread rendering sha says
    what each of them is. A comment edited in the store since the registration moves the second and
    not the first, and it would otherwise reach the model as an unregistered request.
    """
    kept = subset.population()
    digest = record["population"]["enumeration"]["digest"]
    got = subset.digest(kept)
    if got != digest:
        raise SystemExit(
            f"the population's digest is {got[:16]}… and the registration pinned {digest[:16]}…."
            " This run would be reading a different subset than the one it registered."
        )
    task = record["instruments"]["task"]
    pinned = {
        one["thread"]: one["rendering_sha256"]
        for one in record["population"]["enumeration"]["threads"]
    }
    for one in kept:
        name = key_of(one)
        live = writer.rendering_sha256(one, task)
        if live != pinned[name]:
            raise SystemExit(
                f"{name}: the request renders to {live[:16]}… and the registration pinned"
                f" {pinned[name][:16]}…. The thread's text moved since the registration — stop and"
                " report it rather than paying for a request nobody registered."
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


def expected_worker(record: dict) -> dict:
    """What `assert_serving` compares the endpoint's `info` against — read from the registration."""
    block = record["instruments"]["serving"]
    return {
        "serving_config": block["serving_config"],
        "merge_state": block["merge_state"],
        "adapter_sha256": None,
        "quantization": block["quantization"],
        "chat_template": block["chat_template"],
        "max_new_tokens": record["instruments"]["ceilings"]["output_tokens"],
        "model": block["model"],
        "revision_requested": block["model_revision"],
        # `reader_prompt_sha256` is deliberately NOT here, and its absence is checked separately in
        # `handshake` rather than left to be noticed. `assert_serving` compares dicts WHOLE, and the
        # registration's map names the reader texts that existed when it was written — two of them.
        # A third registered text makes whole-dict equality an invariant no worker at this checkout
        # can satisfy, and re-pinning a sealed registration to green it is refused
        # ([[an_invariant_the_new_member_cannot_satisfy]]). What the record can still demand is that
        # each text IT registered is served with the bytes it registered, and that is a different
        # comparison with a different message.
    }


def handshake(client, record: dict) -> dict:
    """`info`, compared whole against the registration. A mismatch is a STOP, not a warning."""
    info = client.info()
    # the prompts FIRST, and against what THIS checkout renders rather than against the pin.
    # `assert_serving` would refuse the same row one line later with a message about a
    # configuration, and the cause is not a configuration: it is a volume a session behind, which is
    # the failure that actually happens ([[a_new_guard_can_be_shadowed_by_an_old_one]] — read the
    # message, not the exit). Every REGISTERED reader text, because a worker that matched only the
    # one this run reads with could still be a session behind on the other.
    live = {task: prompts.prompt_sha256(task) for task in sorted(prompts.READER)}
    served = info.get("reader_prompt_sha256")
    if served != live:
        # a worker that answers with a SCALAR is probe-a's shape and is named as that rather than
        # diffed key by key — the two are not the same kind of disagreement
        wrong = (
            "the field is not a per-task map"
            if not isinstance(served, dict)
            else ", ".join(
                task
                for task in sorted(set(live) | set(served))
                if served.get(task) != live.get(task)
            )
        )
        raise SystemExit(
            f"the worker's reader prompts are {served} and this checkout renders {live}."
            f" Disagreement: {wrong}. The volume is not at this session's commit."
        )
    # and SECOND, the registration's own texts — the comparison `expected_worker` cannot make any
    # more, kept here so that dropping it from there did not drop it altogether. A distinct message
    # on purpose: «the volume is behind» and «this worker is not serving what this run registered»
    # are two different failures and only one of them is fixed by fetching the volume.
    registered = record["instruments"]["prompt_sha256"]
    moved = [task for task, sha in registered.items() if served.get(task) != sha]
    if moved:
        raise SystemExit(
            f"the registration pins {[registered[task][:12] for task in moved]} for {moved} and the"
            f" worker serves {[str(served.get(task))[:12] for task in moved]}. The check above"
            " passed, so fetching the volume fixes nothing: this worker is not serving what this"
            " run registered."
        )
    serving.assert_serving(info, expected_worker(record))
    return info


def anchor(balance: float, record: dict) -> dict:
    """The session's spend anchor, written BEFORE the first request and never regenerated.

    Same footgun as every other `spend_*.json` in this repo: delete it and the counter silently
    restarts at today's balance. `runpod_guard` walks pods and volumes only, so serverless spend is
    invisible to it — this anchor and the endpoint's own clock are the two readings that see it.
    """
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {
        f"runpod_balance_at_{PHASE}_start": balance,
        f"{PHASE}_cap_usd": float(record["money"]["cap_usd_all_in"]),
        "anchored_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "note": (
            "probe-b's own anchor. Session spend = this balance minus the balance now. Written"
            " before the first request; regenerating it would reset the counter to today's balance."
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
    task = record["instruments"]["task"]
    rows = []
    for thread in batch:
        before = client.timing() or {}
        started = time.monotonic()
        replies = client.read(task, [job_item(thread)])
        after = client.timing() or {}
        reply = replies[0]
        try:
            parsed, reason = prompts.parse_reply(task, reply["content"]), None
        except prompts.ParseError as err:
            parsed, reason = None, err.reason
        row = {
            "thread": key_of(thread),
            "channel": thread["channel"],
            "post_id": thread["post_id"],
            "injected": thread["injected"],
            "cases": thread["cases"],
            "payable_comments": len(thread["comments"]),
            "task": task,
            "prompt_sha256": record["instruments"]["prompt_sha256"][task],
            "rendering_sha256": writer.rendering_sha256(thread, task),
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
            f"  {'INJ' if row['injected'] else '   '} {row['thread']:32s}"
            f" {row['payable_comments']:3d} payable · {row['seconds']['worker']:6.1f} s worker"
            f" · {state}"
        )
    return rows


def billed_seconds(client, rows: list[dict] | None = None) -> float:
    """What the warm-up has been billed, in the unit serverless charges: the largest reading.

    `worker_seconds` is per-job execution and misses the gaps a `workersMax: 1` endpoint is up and
    charged through; `wall_seconds` is the span the client held it. The pessimistic one wins.

    And a THIRD reading, from the persisted rows, because the first two are properties of THIS
    process. A `--warm-up` re-invoked after the draw was already bought sends no job, so the client
    reports 0 s and the gate would divide zero by three threads and say GO on a run nobody priced.
    The evidence file is what survives the process, so it is what the projection falls back to.
    """
    timing = client.timing() or {}
    live = max(float(timing.get("worker_seconds") or 0.0), float(timing.get("wall_seconds") or 0.0))
    persisted = sum(float(row["seconds"]["worker"]) for row in rows or ())
    return max(live, persisted)


def projection(
    rows: list[dict], kept: list[dict], record: dict, billed: float, rate: float
) -> dict:
    """The go/no-go: what the UNREAD remainder will cost, on top of what is already spent.

    Three corrections to v1's arithmetic, all in the same direction — towards the truth rather than
    towards a GO:

    - the remainder is projected, never the whole population, so the warm-up's threads are not
      counted twice;
    - the measured SETUP is inside the total, because the cap is all-in and the rung that produces
      nothing is inside it;
    - both projections are computed and the pessimistic binds, because this population's threads are
      larger than the warm-up's and a rate is a property of the sample it was measured on.
    """
    done = {row["thread"] for row in rows}
    remainder = [one for one in kept if key_of(one) not in done]
    warm_threads = len(rows)
    warm_payable = sum(row["payable_comments"] for row in rows) or 1
    per_thread = billed / warm_threads
    per_payable = billed / warm_payable

    left_threads = len(remainder)
    left_payable = sum(len(one["comments"]) for one in remainder)
    by_thread = per_thread * left_threads
    by_payable = per_payable * left_payable
    binding = max(by_thread, by_payable)

    setup = float(record["money"]["arithmetic"]["setup_usd"])
    cap = float(record["money"]["cap_usd_all_in"])
    spent = setup + billed * rate
    total = spent + binding * rate
    return {
        "warm_up": {
            "threads": warm_threads,
            "payable_comments": warm_payable,
            "billed_seconds": round(billed, 3),
            "seconds_per_thread": round(per_thread, 3),
            "seconds_per_payable_comment": round(per_payable, 3),
            "probe_a_on_an_l4": {
                "seconds_per_thread": writer.L4_SECONDS_PER_THREAD,
                "seconds_per_payable_comment": writer.L4_SECONDS_PER_PAYABLE,
                "speedup_per_thread": round(writer.L4_SECONDS_PER_THREAD / per_thread, 3),
                "speedup_per_payable_comment": round(
                    writer.L4_SECONDS_PER_PAYABLE / per_payable, 3
                ),
                "break_even_registered": record["money"]["arithmetic"]["break_even_speedup"],
            },
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
            "warm_up_usd": round(billed * rate, 4),
            "spent_so_far_usd": round(spent, 4),
            "projected_total_usd": round(total, 4),
            "headroom_usd": round(cap - total, 4),
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
    kept = threads_of(record)
    by_key = {key_of(one): one for one in kept}
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
    # OUTSIDE `anchor`, and that is the point: in the runbook's order `runpod_guard --step probe-b
    # --step-cap 0.35` writes this file before the first pod, so by the time the driver runs the
    # anchor branch never fires and a cap key written only inside it would never land. The anchor
    # itself is never overwritten ([[a_guard_on_one_path_is_not_a_guard]]).
    ledger[f"{PHASE}_cap_usd"] = float(record["money"]["cap_usd_all_in"])
    save_ledger(ledger)

    info = handshake(client, record)
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
        rows = [
            json.loads(line)
            for line in EVIDENCE.read_text(encoding="utf-8").splitlines()
            if line and json.loads(line)["thread"] in drawn
        ]
        gate = projection(rows, kept, record, billed_seconds(client, rows), rate)
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
