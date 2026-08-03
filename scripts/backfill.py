#!/usr/bin/env python3
"""Phase-2c historical backfill into the raw store (docs/SPEC.md §6).

Posts back to BACKFILL_SINCE for every verified source, plus the full comment
threads of those posts wherever the source has comments enabled. Everything lands
in data/raw/ (gitignored); nothing here filters, labels or scores.

Long by design and safe to stop: records are flushed in chunks, the cursor is
written atomically after every flush, and a rerun resumes from it without storing
anything twice.

    python3.11 scripts/tg_login.py     # once, to create the session
    python3.11 scripts/backfill.py
"""

import argparse
import asyncio
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from telethon.errors import FloodWaitError

from market_pulse.backfill import (
    GATE_COMMENTS,
    channel_row,
    load_cursor,
    render_summary,
    save_cursor,
    total_comments,
)
from market_pulse.raw_store import (
    RawStore,
    collapse_albums,
    comment_record,
    load_salt,
    make_provenance,
    post_record,
)
from market_pulse.registry import load_registry
from market_pulse.telegram_client import build_client

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
CURSOR = REPO_ROOT / "data" / "backfill_cursor.json"

# Pre-registered window. Not to be widened to reach the gate.
BACKFILL_SINCE = datetime(2024, 7, 1, tzinfo=timezone.utc)

CHUNK = 200  # records buffered before a flush; bounds what an interrupt loses
REQUEST_PAUSE = 1.0  # between history requests (100 posts each)
THREAD_PAUSE = 1.0  # between comment threads
CHANNEL_PAUSE = 2.0
FLOOD_RETRIES = 3
PROGRESS_EVERY = 50


V1_COMMENTS = "data/raw/comments/"
"""The comment store as it was collected before 4.5g5 taught the collector `reply_to_msg_id`.

Every row in it predates that field, and this script would append rows that carry it — so one
file would hold two kinds of record distinguishable only by a missing key. `data/raw/comments_v2/`
is where the joined store lives and `scripts/fetch_comments_v2.py` is what writes it; a v1 walk
is now an explicit decision rather than the default (4.5g5, deviation 11)."""


def v1_write_refusal(channels: list[tuple], allow: bool) -> str | None:
    """Why this run may not append to the v1 comment store, or ``None`` if it may.

    Returned rather than raised so the reason can be tested and printed by one caller. Posts are
    untouched by this: their records did not change shape.
    """
    if allow or not any(source.comments_enabled for source, _ in channels):
        return None
    enabled = sorted({handle for source, handle in channels if source.comments_enabled})
    return (
        f"this run would append comments to {V1_COMMENTS} for {', '.join(enabled)}, and every row"
        " already there was collected before the store learned `reply_to_msg_id`. Mixing the two"
        " leaves one file whose rows differ by a missing key, and `measure_families_45g5.py`"
        " counts a row without that key as un-refetched rather than as top-level. Re-fetch into"
        " data/raw/comments_v2/ with scripts/fetch_comments_v2.py, or pass --allow-v1-write if"
        " appending to v1 is what you mean."
    )


@dataclass
class Job:
    """Everything one channel's walk needs, so the helpers stay readable."""

    source: object
    handle: str
    entity: object
    provenance: dict
    store: RawStore
    salt: str
    cursor: dict
    state: dict = field(default_factory=dict)


def flush(job: Job, buffer: list[dict]) -> int:
    """Store a chunk and move the cursor with it."""
    if not buffer:
        return 0
    written = job.store.append(collapse_albums(buffer))
    ids = [record["msg_id"] for record in buffer]
    job.state["newest"] = max(job.state.get("newest") or 0, max(ids))
    job.state["oldest"] = min(job.state.get("oldest") or min(ids), min(ids))
    save_cursor(CURSOR, job.cursor)
    buffer.clear()
    return written


async def walk_posts(client, job: Job, **bounds) -> str:
    """Collect posts in one direction. Returns why the walk stopped.

    Exactly one bound is passed — ``min_id`` for newer posts, ``offset_id`` for
    older ones — rather than passing both and relying on 0 meaning "no bound".
    """
    buffer: list[dict] = []
    stopped = "exhausted"
    try:
        async for message in client.iter_messages(job.entity, wait_time=REQUEST_PAUSE, **bounds):
            if message.action is not None:
                continue  # joins, pins and the like are not posts
            if message.date < BACKFILL_SINCE:
                stopped = "since"
                break
            # Never split an album across a flush: its items must collapse together.
            if len(buffer) >= CHUNK and (
                message.grouped_id is None or message.grouped_id != buffer[-1]["grouped_id"]
            ):
                flush(job, buffer)
            buffer.append(post_record(message, job.source, job.handle, job.provenance))
    finally:
        flush(job, buffer)
    return stopped


async def walk_with_retry(client, job: Job, *, forward: bool) -> str:
    """Walk newer posts (forward) or older history, sleeping out any FloodWait.

    The bounds are re-read from the cursor on every attempt, so a retry picks up
    where the flushed chunk left off instead of starting over.
    """
    for _ in range(FLOOD_RETRIES):
        key = "newest" if forward else "oldest"
        bound = job.state.get(key)
        bounds = {("min_id" if forward else "offset_id"): bound} if bound else {}
        try:
            return await walk_posts(client, job, **bounds)
        except FloodWaitError as exc:
            print(f"  FloodWait: sleeping {exc.seconds}s", flush=True)
            await asyncio.sleep(exc.seconds)
    return "floodwait"


async def fetch_threads(client, job: Job) -> int:
    """Fetch the comment thread of every stored post that still lacks one."""
    posts = job.store.index("post", job.handle)
    done = job.store.index("comment", job.handle).parents
    # A post whose thread is genuinely empty stays on this list and is retried on
    # every run — cheap next to the risk of skipping a thread that does have data.
    todo = sorted(posts.with_replies - done, reverse=True)
    print(f"  {len(todo)} comment threads to fetch", flush=True)

    fetched = 0
    for done_count, parent in enumerate(todo, start=1):
        try:
            records = [
                comment_record(message, job.source, job.handle, parent, job.salt, job.provenance)
                async for message in client.iter_messages(job.entity, reply_to=parent)
                if message.action is None
            ]
            fetched += job.store.append(records)
        except FloodWaitError as exc:
            print(f"  FloodWait: sleeping {exc.seconds}s", flush=True)
            await asyncio.sleep(exc.seconds)
        except Exception as exc:
            # Posts older than the discussion group have no thread to read.
            print(f"  thread {parent}: {type(exc).__name__}", flush=True)
        if done_count % PROGRESS_EVERY == 0:
            print(f"  {done_count}/{len(todo)} threads, {fetched} comments", flush=True)
        await asyncio.sleep(THREAD_PAUSE)
    return fetched


async def backfill_channel(client, job: Job) -> str:
    if job.state.get("newest"):
        await walk_with_retry(client, job, forward=True)
    stopped = await walk_with_retry(client, job, forward=False)
    if job.source.comments_enabled:
        await fetch_threads(client, job)
    return stopped


async def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-v1-write",
        action="store_true",
        help=f"append comments to {V1_COMMENTS}, which no longer carry reply_to_msg_id",
    )
    args = parser.parse_args(argv)

    registry = load_registry(REGISTRY)
    channels = [
        (source, handle)
        for source in registry.sources
        if source.verified
        for handle in source.telegram_channels
    ]
    if refusal := v1_write_refusal(channels, args.allow_v1_write):
        raise SystemExit(refusal)

    salt = load_salt()  # also loads .env, so the session name is available below
    session = os.environ["TELEGRAM_SESSION"]
    store = RawStore()
    cursor = load_cursor(CURSOR)

    rows = {
        handle: channel_row(store, source, handle, "not started") for source, handle in channels
    }

    client = build_client()
    await client.connect()
    try:
        if not await client.is_user_authorized():
            print("No Telegram session. Run: python3.11 scripts/tg_login.py")
            return 2
        for source, handle in channels:
            print(f"\n{handle} ({source.id})", flush=True)
            try:
                job = Job(
                    source=source,
                    handle=handle,
                    entity=await client.get_entity(handle),
                    provenance=make_provenance(source, session),
                    store=store,
                    salt=salt,
                    cursor=cursor,
                    state=cursor.setdefault(handle, {}),
                )
                stopped = await backfill_channel(client, job)
            except FloodWaitError as exc:
                # One throttled channel must not end a run that takes hours.
                print(f"  FloodWait: sleeping {exc.seconds}s", flush=True)
                await asyncio.sleep(exc.seconds)
                stopped = "floodwait"
            rows[handle] = channel_row(store, source, handle, stopped)
            await asyncio.sleep(CHANNEL_PAUSE)
    finally:
        save_cursor(CURSOR, cursor)
        await client.disconnect()

    print()
    print(render_summary(list(rows.values())))
    print(f"\nraw store: {store.root}  cursor: {CURSOR}")
    return 0 if total_comments(list(rows.values())) >= GATE_COMMENTS else 1


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except KeyboardInterrupt:
        # The chunk flush and the atomic cursor already persisted the progress.
        print("\ninterrupted — what was collected is stored, rerun to continue")
        raise SystemExit(130) from None
