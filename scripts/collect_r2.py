#!/usr/bin/env python3
"""Registry revision r2: collect the A1 composition's window ($0, Telegram only).

S2 of `docs/plans/promo-pulse-1.md`. The population §1 measures does not exist on disk: the newest
post across every A1 channel is 2026-08-08 and eight of the 18 A1 entries have no store file at all.
This fills that in — and nothing else. It COLLECTS; scoring is the paid step and lives elsewhere.

A sibling of `scripts/collect_5c1.py` rather than a flag on it, for two reasons that are facts
about that script and not preferences: it is gated on `results/entry_gate_5c1.json`, which knows
nothing about r2's eight new rows, and it REFUSES the six raw-v1 baseline channels at channel level
— which are exactly the incumbents this step has to top up. The shared machinery (`RawStore`,
`post_record`, `comment_record`, `collapse_albums`, the client factory) is imported, not copied.

Three phases, each resumable on its own, because each fails differently:

``--plan``    what would be collected, and what is already there. No Telegram at all.
``--posts``   the 28-day window for every collected A1 channel, newest-first, stopping at `since`.
              Dedup is `RawStore`'s on (channel, msg_id), so a re-run costs requests and no rows.
``--join``    join the discussion group of an A1 channel that has one, paced at one per
              ``JOIN_PAUSE`` and logged to `results/joins_r2.jsonl`, which is also the cursor.
``--comments``the threads of stored posts, in groups this account is in.

`collect: false` is honoured: revision r2 takes 39 sources out of COLLECTION without taking them
out of the registry, and this is the reader that makes that mean something. A paused row is skipped
here and still resolves everywhere else.

    PYTHONPATH=src python3.11 scripts/collect_r2.py --plan
    PYTHONPATH=src python3.11 scripts/collect_r2.py --posts
    PYTHONPATH=src python3.11 scripts/collect_r2.py --join --max 4
    PYTHONPATH=src python3.11 scripts/collect_r2.py --comments
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from collect_5c1 import protected  # noqa: E402
from registry_revision_proposal import bucket  # noqa: E402
from telethon import functions  # noqa: E402
from telethon.errors import FloodWaitError  # noqa: E402

from market_pulse.raw_store import (  # noqa: E402
    ARCHIVE_ROOT,
    LIVE_ROOT,
    RawStore,
    collapse_albums,
    comment_record,
    load_salt,
    make_provenance,
    post_record,
)
from market_pulse.registry import load_registry  # noqa: E402
from market_pulse.telegram_client import build_client  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
RECORD = REPO_ROOT / "results" / "collect_r2.json"
JOIN_LOG = REPO_ROOT / "results" / "joins_r2.jsonl"
STORE_ROOT = LIVE_ROOT
"""SP-4 ruling (a) (review 2026-08-30): the top-up lands in the ONE live root for EVERY collected
channel — the four pinned incumbents and the sixteen free ones alike, so no later reader has to
know which of the two roots a channel's rows came from. `data/raw/` is an archive from here on."""

WINDOW_DAYS = 28
"""`scripts/collect_5c1.py::WINDOW_DAYS` and the census's — both instruments measure 28 days, and a
window of a different length here would make the census price a population it never read."""

JOIN_PAUSE = 900.0
"""Fifteen minutes between joins, from `collect_5c1`. Joining is the one action here that WRITES on
Telegram's side, and its rate limit is measured in hours."""
REQUEST_PAUSE = 1.0
CHANNEL_PAUSE = 2.0
THREAD_PAUSE = 1.0
CHUNK = 200
PROGRESS_EVERY = 25


def a1_sources(registry) -> list[tuple]:
    """(source, handle) for every A1 channel revision r2 still collects.

    Bucket A is `scripts/registry_revision_proposal.py::bucket` — imported, not re-derived: it is
    SPEC v2 §3's own division and a second copy of it would be free to disagree with the section it
    implements. `collect` is the r2 flag; B (Poltava) is deferred to phase B and is not read here.
    """
    return [
        (source, handle)
        for source in registry.sources
        if source.collect and bucket(source) == "A"
        for handle in source.telegram_channels
    ]


def refuse_pinned(channels, store) -> None:
    """The raw v1 files are PINNED, and this script would have appended to four of them.

    `results/raw_v1_baseline.sha256` pins six store files and all six verify today. Four A1
    channels map onto them — `@atb_market_official`, `@silposilpo`, `@VARUS_channel`, `@msuaaaa` —
    and they are exactly the incumbents S2 was told to top up, which is why `collect_5c1` refuses
    them at channel level and why this sibling exists at all. The refusal did not come with it.

    An append here is worse than an ordinary mistake: `data/` is gitignored, so `git status` is
    silent in both directions and there is no history to restore the file from. The write is
    irreversible and the pin is the only durable evidence the store was never written
    ([[baseline_before_the_run_not_after]]).

    `protected()` is IMPORTED from the guard that already owns the pinned set. A second list here
    would be free to drift, and this is the copy that holds the writer
    ([[a_moved_guard_that_left_its_copy]]).

    Under SP-4 ruling (a) this check now PASSES rather than fires: `STORE_ROOT` is the live root,
    so no channel's write path is in `protected()`. It is kept, not deleted — it refuses BEFORE
    the Telegram session is opened, and it is what would fire again if the root were ever pointed
    back at the archive. The refusal that actually holds the writer today is
    `RawStore.append`'s (plan §5.14).
    """
    guarded = protected()
    hit = sorted(
        {
            handle
            for _, handle in channels
            for kind in ("post", "comment")
            if store.path(kind, handle).resolve() in guarded
        }
    )
    if hit:
        raise SystemExit(
            "refusing to collect: these channels write into pinned raw v1 files —\n  "
            + "\n  ".join(hit)
            + "\n`results/raw_v1_baseline.sha256` pins them and `data/` is gitignored, so the"
            " append cannot be undone.\nThis is SP-4 (docs/plans/promo-pulse-1.md §4): the operator"
            " decides whether the top-up goes to a\nsecond store root, or whether these four stay"
            " at the bytes the baseline holds."
        )


def join_state() -> dict:
    """The last logged outcome per channel — the log IS the cursor."""
    state: dict[str, dict] = {}
    if JOIN_LOG.exists():
        for line in JOIN_LOG.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                state[row["channel"]] = row
    return state


def log_join(row: dict) -> None:
    JOIN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with JOIN_LOG.open("a", encoding="utf-8") as out:
        out.write(json.dumps(row, ensure_ascii=False) + "\n")


def channel_row(store, source, handle: str, added=None) -> dict:
    """One channel's line. `store` is the union; `added` is the LIVE root alone.

    Two stores, on purpose: «what the corpus holds» and «what this step added» are different
    questions and one number cannot answer both. The union is what the census prices; the live
    root alone is what S2 is accountable for.
    """
    posts = store.index("post", handle)
    comments = store.index("comment", handle)
    fresh_posts = added.index("post", handle) if added is not None else None
    fresh_comments = added.index("comment", handle) if added is not None else None
    return {
        "posts_added_r2": fresh_posts.count if fresh_posts is not None else None,
        "comments_added_r2": fresh_comments.count if fresh_comments is not None else None,
        "channel": handle,
        "source_id": source.id,
        "source_type": source.source_type,
        "audience": source.audience,
        "comments_enabled": source.comments_enabled,
        "posts_stored": posts.count,
        "posts_first": posts.first_date,
        "posts_last": posts.last_date,
        "comments_stored": comments.count,
        "threads_with_comments": len(comments.parents),
        "damaged_lines": posts.damaged_lines + comments.damaged_lines,
    }


async def walk_window(client, entity, source, handle, since, store, provenance) -> dict:
    """Posts newer than `since`, flushed in chunks so an interrupt keeps what it read."""
    buffer, stored = [], 0
    async for message in client.iter_messages(entity, wait_time=REQUEST_PAUSE):
        if message.action is not None:
            continue
        if message.date < since:
            break
        if len(buffer) >= CHUNK and (
            message.grouped_id is None or message.grouped_id != buffer[-1]["grouped_id"]
        ):
            stored += store.append(collapse_albums(buffer))
            buffer.clear()
        buffer.append(post_record(message, source, handle, provenance))
    stored += store.append(collapse_albums(buffer))
    return {"posts_stored": stored}


async def fetch_threads(client, entity, source, handle, store, salt, provenance) -> dict:
    """The comment threads of stored posts that do not have one yet."""
    posts = store.index("post", handle)
    todo = sorted(posts.with_replies - store.index("comment", handle).parents, reverse=True)
    stored, failed = 0, 0
    for done, parent in enumerate(todo, start=1):
        try:
            records = [
                comment_record(message, source, handle, parent, salt, provenance)
                async for message in client.iter_messages(entity, reply_to=parent)
                if message.action is None
            ]
            stored += store.append(records)
        except FloodWaitError as exc:
            print(f"    FloodWait {exc.seconds}s — sleeping", flush=True)
            await asyncio.sleep(exc.seconds)
        except Exception as exc:  # noqa: BLE001 — one bad thread must not end the channel
            failed += 1
            print(f"    thread {parent}: {type(exc).__name__}: {exc}", flush=True)
        if done % PROGRESS_EVERY == 0:
            print(f"    {done}/{len(todo)} threads, {stored} comments", flush=True)
        await asyncio.sleep(THREAD_PAUSE)
    return {"threads": len(todo), "comments_stored": stored, "threads_failed": failed}


async def join_group(client, handle: str) -> dict:
    """Join one channel's linked discussion group, or say why there is nothing to join."""
    row = {"at": datetime.now(UTC).isoformat(timespec="seconds"), "channel": handle}
    entity = await client.get_entity(handle)
    full = await client(functions.channels.GetFullChannelRequest(channel=entity))
    linked = full.full_chat.linked_chat_id
    if linked is None:
        return row | {"outcome": "no group", "group_id": None}
    chat = next((c for c in full.chats if getattr(c, "id", None) == linked), None)
    if chat is None:
        return row | {"outcome": "group not returned", "group_id": linked}
    row |= {"group_id": linked, "group_title": getattr(chat, "title", None)}
    if not getattr(chat, "left", True):
        return row | {"outcome": "already_member"}
    await client(functions.channels.JoinChannelRequest(channel=chat))
    return row | {"outcome": "joined"}


def since_of(record: dict | None) -> datetime:
    """The window's start, FIXED by the first run and read back afterwards.

    A `since` recomputed on every run is a sliding window: a resume two days later would collect a
    different 28 days and the census would price a population nobody enumerated
    ([[a_stock_window_needs_the_create_not_a_poll]] is the same mistake in the money domain).
    """
    held = (record or {}).get("since")
    if held:
        return datetime.fromisoformat(held)
    return datetime.now(UTC) - timedelta(days=WINDOW_DAYS)


def write_record(rows: list[dict], since: datetime, extra: dict) -> dict:
    prior = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {}
    record = {
        **prior,
        "contract": "docs/plans/promo-pulse-1.md S2 — registry r2, A1 collection ($0)",
        "since": since.isoformat(),
        "window_days": WINDOW_DAYS,
        "channels": rows,
        **extra,
    }
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return record


def render(rows: list[dict]) -> str:
    head = (
        f"{'channel':<24}{'posts':>7}{'+r2':>6}{'first':>13}{'last':>13}"
        f"{'comments':>10}{'+r2':>6}{'threads':>9}"
    )
    lines = [head, "-" * len(head)]
    for row in rows:
        lines.append(
            f"{row['channel']:<24}{row['posts_stored']:>7}{str(row['posts_added_r2']):>6}"
            f"{str(row['posts_first'])[:10]:>13}{str(row['posts_last'])[:10]:>13}"
            f"{row['comments_stored']:>10}{str(row['comments_added_r2']):>6}"
            f"{row['threads_with_comments']:>9}"
        )
    return "\n".join(lines)


async def run(args, registry) -> dict:
    # `STORE_ROOT`, not `live_store()`: the root is this module's, so a test can point it at a
    # scratch directory and still exercise the real union.
    store = RawStore(STORE_ROOT, archives=(ARCHIVE_ROOT,))
    added = RawStore(STORE_ROOT)
    channels = a1_sources(registry)
    if args.only:
        wanted = {one.lstrip("@").lower() for one in args.only}
        channels = [pair for pair in channels if pair[1].lstrip("@").lower() in wanted]
    prior = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else None
    since = since_of(prior)
    if not args.plan:
        # Before the client, not after: a refusal that has already opened a session has already
        # done the one thing this phase promised not to do.
        refuse_pinned(channels, store)
    extra: dict = {}

    if args.plan:
        rows = [channel_row(store, source, handle, added) for source, handle in channels]
        print(f"window since {since.isoformat(timespec='seconds')} ({WINDOW_DAYS} days)")
        print(render(rows))
        empty = [row["channel"] for row in rows if row["posts_stored"] == 0]
        print(f"\n{len(rows)} A1 channels collected by r2; {len(empty)} with no posts yet: {empty}")
        return write_record(rows, since, {"phase": "plan"})

    salt = load_salt()
    client = build_client()
    await client.start()
    try:
        if args.join:
            state, joined = join_state(), []
            for source, handle in channels:
                if not source.comments_enabled or state.get(handle, {}).get("outcome") in (
                    "joined",
                    "already_member",
                    "no group",
                ):
                    continue
                if args.max is not None and len(joined) >= args.max:
                    break
                if joined:
                    print(f"  pacing {JOIN_PAUSE:.0f}s before the next join", flush=True)
                    await asyncio.sleep(JOIN_PAUSE)
                try:
                    row = await join_group(client, handle)
                except FloodWaitError as exc:
                    clears = datetime.now(UTC) + timedelta(seconds=exc.seconds)
                    row = {
                        "at": datetime.now(UTC).isoformat(timespec="seconds"),
                        "channel": handle,
                        "outcome": "floodwait",
                        "seconds": exc.seconds,
                        "clears_at": clears.isoformat(timespec="seconds"),
                    }
                    log_join(row)
                    print(f"  {handle}: FloodWait {exc.seconds}s — stopping the join phase")
                    break
                except Exception as exc:  # noqa: BLE001 — one refusal must not end the phase
                    row = {
                        "at": datetime.now(UTC).isoformat(timespec="seconds"),
                        "channel": handle,
                        "outcome": f"{type(exc).__name__}: {exc}",
                    }
                log_join(row)
                joined.append(row)
                print(f"  {handle}: {row['outcome']}", flush=True)
            extra["joins"] = joined

        if args.posts:
            for source, handle in channels:
                try:
                    entity = await client.get_entity(handle)
                    # Per source, not once for the run: `source_type` and `comments_enabled` are
                    # the SOURCE's, so one provenance hoisted out of this loop would stamp every
                    # channel with whichever came first.
                    provenance = make_provenance(source, "collect_r2")
                    got = await walk_window(client, entity, source, handle, since, store, provenance)
                    print(f"  {handle}: +{got['posts_stored']} posts", flush=True)
                except FloodWaitError as exc:
                    print(f"  {handle}: FloodWait {exc.seconds}s — sleeping", flush=True)
                    await asyncio.sleep(exc.seconds)
                except Exception as exc:  # noqa: BLE001 — a dead handle must not end the run
                    print(f"  {handle}: {type(exc).__name__}: {exc}", flush=True)
                await asyncio.sleep(CHANNEL_PAUSE)

        if args.comments:
            state = join_state()
            for source, handle in channels:
                if not source.comments_enabled:
                    continue
                if state.get(handle, {}).get("outcome") not in ("joined", "already_member"):
                    print(f"  {handle}: group not joined — skipped", flush=True)
                    continue
                try:
                    entity = await client.get_entity(handle)
                    provenance = make_provenance(source, "collect_r2")
                    got = await fetch_threads(
                        client, entity, source, handle, store, salt, provenance
                    )
                    print(f"  {handle}: +{got['comments_stored']} comments", flush=True)
                except Exception as exc:  # noqa: BLE001
                    print(f"  {handle}: {type(exc).__name__}: {exc}", flush=True)
                await asyncio.sleep(CHANNEL_PAUSE)
    finally:
        await client.disconnect()

    rows = [channel_row(store, source, handle, added) for source, handle in channels]
    print(render(rows))
    phases = [name for name in ("join", "posts", "comments") if getattr(args, name)]
    return write_record(rows, since, {"phase": "+".join(phases), **extra})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true", help="what would be collected; no Telegram")
    parser.add_argument("--join", action="store_true", help="join A1 discussion groups, paced")
    parser.add_argument("--posts", action="store_true", help="the 28-day post window")
    parser.add_argument("--comments", action="store_true", help="threads of stored posts")
    parser.add_argument("--max", type=int, default=None, help="cap on joins this run")
    parser.add_argument("--only", nargs="*", help="restrict to these handles")
    args = parser.parse_args(argv)
    if not any((args.plan, args.join, args.posts, args.comments)):
        parser.error("choose --plan, --join, --posts or --comments")

    registry = load_registry(REGISTRY)
    asyncio.run(run(args, registry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
