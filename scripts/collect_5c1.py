#!/usr/bin/env python3
"""Phase-5c1 Deliverable 2: join the authorised groups, collect the four-week window ($0).

Ruling 22 (SPEC §3.11 (6)): the backlog is a WINDOW of the most recent ~4 weeks. Scoring it is
5c2's paid event — this script only COLLECTS, and talks to nothing but Telegram.

Three phases, run separately so each is resumable and reportable on its own:

``--join``
    join the discussion group of every channel the rulings authorised — the 26 comment-capable
    launch channels, and nothing else. NEVER a watch channel: a watch channel keeps its group
    precisely so it can be joined later, once it posts again and the operator says so. Paced at
    one join per JOIN_PAUSE (four an hour), FloodWait waits and resumes, and every attempt is
    appended to `results/joins_5c1.jsonl` — which is also the cursor: a channel already logged
    as joined is not attempted twice. Spreading this over 2-3 days is the expected shape.

``--posts``
    the posts window for every newly registered channel INCLUDING watch. `since` is fixed at
    the first run and read back from the record afterwards, so a resume days later collects the
    same window rather than a sliding one.

``--comments``
    the threads of the window's posts, in joined groups only. A channel whose join has not
    landed yet is skipped and said so; its comments start once it has.

The store is `RawStore` and idempotency is its dedup on (channel, msg_id), not a second one
written here. The six raw v1 files pinned by `results/raw_v1_baseline.sha256` belong to the
four original registry channels and are refused at channel level, before a single record is
built for them.

    PYTHONPATH=src python3 scripts/collect_5c1.py --plan
    PYTHONPATH=src python3 scripts/collect_5c1.py --join --max 8
    PYTHONPATH=src python3 scripts/collect_5c1.py --posts
    PYTHONPATH=src python3 scripts/collect_5c1.py --comments
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_audit_pack import git_state  # noqa: E402
from telethon import functions  # noqa: E402
from telethon.errors import FloodWaitError  # noqa: E402

from market_pulse import loop  # noqa: E402
from market_pulse.raw_store import (  # noqa: E402
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
GATE_RECORD = REPO_ROOT / "results" / "entry_gate_5c1.json"
RECORD = REPO_ROOT / "results" / "collect_5c1.json"
JOIN_LOG = REPO_ROOT / "results" / "joins_5c1.jsonl"
BASELINE = REPO_ROOT / "results" / "raw_v1_baseline.sha256"
CURSOR = REPO_ROOT / "data" / "loop_cursor.json"
STORE_ROOT = REPO_ROOT / "data" / "raw"

WINDOW_DAYS = 28
JOIN_PAUSE = 900.0
"""Fifteen minutes between joins — four an hour, the brief's "a few per hour at most". Joining
is the one action here that writes on Telegram's side, and a rate limit on it is measured in
hours, not seconds."""
REQUEST_PAUSE = 1.0
CHANNEL_PAUSE = 2.0
THREAD_PAUSE = 1.0
CHUNK = 200
PROGRESS_EVERY = 25


def protected() -> set[Path]:
    """The raw v1 files pinned by the baseline — the four original channels' stores.

    Read off the pin file rather than listed here: the guard and the check the task report runs
    (`shasum -c`) then cannot drift apart.
    """
    paths = set()
    for line in BASELINE.read_text(encoding="utf-8").splitlines():
        # The pin file carries `shasum -c` comment lines; a row is `<hash>  <path>`.
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            raise SystemExit(f"{BASELINE}: cannot read the pinned path from {line!r}")
        paths.add((REPO_ROOT / parts[1].strip()).resolve())
    if not paths:
        raise SystemExit(f"{BASELINE}: no pinned files parsed — refusing to run unguarded")
    return paths


def collectable(registry, gate: dict) -> list[tuple]:
    """The channels this phase may collect from: everything the 5c1 rulings added.

    The four original sources are excluded by name — they are out of the gate's scope and their
    stores are pinned — and the guard is then re-stated against the pin file, because a list
    derived correctly and a list that cannot touch the protected files are two different claims.
    """
    entered = {handle for handles in gate["rulings"]["composition"].values() for handle in handles}
    rows = [
        (source, handle)
        for source in registry.sources
        if source.verified
        for handle in source.telegram_channels
        if handle in entered
    ]
    store, guarded = RawStore(STORE_ROOT), protected()
    for _, handle in rows:
        for record_type in ("post", "comment"):
            if store.path(record_type, handle).resolve() in guarded:
                raise SystemExit(f"{handle} maps onto a pinned raw v1 file — refusing to collect")
    return rows


def joinable(registry, gate: dict) -> list[tuple]:
    """The groups this phase may join: the rulings' own list, cross-checked against the registry.

    Two independent derivations of the same set. If they disagree, something moved between the
    ruling and the registry write, and the answer is to stop rather than to pick one.
    """
    authorised = set(gate["rulings"]["joins_authorised"])
    fresh = collectable(registry, gate)
    # The four original channels are already joined and out of the gate's scope, so the registry
    # side is read over the newly entered channels only.
    from_registry = {
        handle for source, handle in fresh if source.comments_enabled and not source.watch
    }
    if from_registry != authorised:
        raise SystemExit(
            "the registry and the rulings disagree about which groups may be joined: "
            f"registry-only {sorted(from_registry - authorised)}, "
            f"rulings-only {sorted(authorised - from_registry)}"
        )
    return [(source, handle) for source, handle in fresh if handle in authorised]


def join_state() -> dict:
    """What `results/joins_5c1.jsonl` already records, newest attempt per channel."""
    if not JOIN_LOG.exists():
        return {}
    state = {}
    for line in JOIN_LOG.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            state[row["channel"]] = row
    return state


def log_join(row: dict) -> None:
    JOIN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with JOIN_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


async def join_group(client, handle: str) -> dict:
    """Join one channel's linked discussion group. Returns the row to log."""
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


async def leave_group(client, handle: str) -> dict:
    """Leave one channel's discussion group. The reverse of `join_group`, logged the same way.

    Logged rather than done by hand: `results/joins_5c1.jsonl` is the record of what this account
    is a member of, and a membership that ended outside it would make the log a lie. The `left`
    row is also what stops `--comments` collecting from a group the operator threw out — the
    cursor reads the LAST row per channel.
    """
    row = {"at": datetime.now(UTC).isoformat(timespec="seconds"), "channel": handle}
    entity = await client.get_entity(handle)
    full = await client(functions.channels.GetFullChannelRequest(channel=entity))
    linked = full.full_chat.linked_chat_id
    chat = next((c for c in full.chats if getattr(c, "id", None) == linked), None)
    if chat is None:
        return row | {"outcome": "no group", "group_id": linked}
    row |= {"group_id": linked, "group_title": getattr(chat, "title", None)}
    await client(functions.channels.LeaveChannelRequest(channel=chat))
    return row | {"outcome": "left"}


def seconds_until_next_join(state: dict, now: datetime) -> float:
    """How long to wait before the next join, measured from the last one the LOG records.

    Wall-clock, not process-local. The log is already the cursor; an in-process timer would be
    reset by every restart, and a run stopped and resumed for other work would fire its next join
    seconds after the previous one — exactly the burst the pace exists to avoid. A failed attempt
    counts too: it still made requests.
    """
    stamps = [datetime.fromisoformat(row["at"]) for row in state.values() if row.get("at")]
    if not stamps:
        return 0.0
    return max(0.0, JOIN_PAUSE - (now - max(stamps)).total_seconds())


async def run_joins(client, channels: list[tuple], limit: int | None) -> dict:
    state = join_state()
    todo = [
        (source, handle)
        for source, handle in channels
        if state.get(handle, {}).get("outcome") not in ("joined", "already_member")
    ]
    if limit is not None:
        todo = todo[:limit]
    print(
        f"{len(channels)} authorised, {len(channels) - len(todo)} already landed, {len(todo)} now"
    )

    done = 0
    for _, handle in todo:
        wait = seconds_until_next_join(join_state(), datetime.now(UTC))
        if wait:
            print(f"  pacing {wait:.0f}s before {handle}...", flush=True)
            await asyncio.sleep(wait)
        try:
            row = await join_group(client, handle)
        except FloodWaitError as exc:
            log_join(
                {
                    "at": datetime.now(UTC).isoformat(timespec="seconds"),
                    "channel": handle,
                    "outcome": "floodwait",
                    "seconds": exc.seconds,
                }
            )
            print(f"  FloodWait {exc.seconds}s at {handle} — stopping, the log is the cursor")
            return {"attempted": done + 1, "landed": done, "flood_wait_seconds": exc.seconds}
        except Exception as exc:
            row = {
                "at": datetime.now(UTC).isoformat(timespec="seconds"),
                "channel": handle,
                "outcome": "error",
                "error": f"{type(exc).__name__}: {exc}",
            }
        log_join(row)
        done += row["outcome"] in ("joined", "already_member")
        print(f"  {handle}: {row['outcome']}", flush=True)
    return {"attempted": len(todo), "landed": done, "flood_wait_seconds": None}


async def walk_window(client, entity, source, handle, since, store, provenance) -> dict:
    """Posts newer than `since`, stored in chunks so an interrupt keeps what it read."""
    buffer, stored = [], 0
    async for message in client.iter_messages(entity, wait_time=REQUEST_PAUSE):
        if message.action is not None:
            continue
        if message.date < since:
            break
        # Never split an album across a flush: its items must collapse together.
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
        except Exception as exc:
            failed += 1
            print(f"    thread {parent}: {type(exc).__name__}: {exc}", flush=True)
        if done % PROGRESS_EVERY == 0:
            print(f"    {done}/{len(todo)} threads, {stored} comments", flush=True)
        if THREAD_PAUSE:
            await asyncio.sleep(THREAD_PAUSE)
    return {"threads": len(todo), "comments_stored": stored, "threads_failed": failed}


def held(record: dict | None, key: str, default):
    """A value fixed by the first run and never recomputed — the window's `since` above all."""
    return (record or {}).get(key, default)


def channel_row(store, source, handle: str) -> dict:
    posts = store.index("post", handle)
    comments = store.index("comment", handle)
    return {
        "channel": handle,
        "source_id": source.id,
        "source_type": source.source_type,
        "watch": source.watch,
        "comments_enabled": source.comments_enabled,
        "posts_stored": posts.count,
        "posts_first": posts.first_date,
        "posts_last": posts.last_date,
        "comments_stored": comments.count,
        "threads_with_comments": len(comments.parents),
        "damaged_lines": posts.damaged_lines + comments.damaged_lines,
    }


def write_record(registry, gate, rows: list[dict], since, first_run, extra: dict) -> dict:
    prior = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {}
    record = {
        **prior,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "5c1",
        "deliverable": "2 — joins and the four-week collection window",
        "contract": "docs/SPEC.md §3.11 (6) ruling 22; docs/PROMPT-5c1.md Deliverable 2",
        "window": {
            "days": WINDOW_DAYS,
            "since": since.isoformat(),
            "first_run_at": first_run,
            "note": (
                "`since` is fixed by the first run and read back from this record afterwards: a"
                " resume days later must collect the same window, not a sliding one."
            ),
        },
        "channels": rows,
        "totals": {
            "channels": len(rows),
            "posts_stored": sum(row["posts_stored"] for row in rows),
            "comments_stored": sum(row["comments_stored"] for row in rows),
            "damaged_lines": sum(row["damaged_lines"] for row in rows),
            "channels_with_posts": sum(1 for row in rows if row["posts_stored"]),
            "channels_with_comments": sum(1 for row in rows if row["comments_stored"]),
        },
        "joins": {**prior.get("joins", {}), **extra.get("joins", {})},
        "phases_run": sorted(set(prior.get("phases_run", [])) | set(extra.get("phases_run", []))),
        "protected": {
            "pin": str(BASELINE.relative_to(REPO_ROOT)),
            "note": (
                "The four original registry channels are out of the gate's scope and their six"
                " raw v1 files are refused at channel level, before a record is built."
            ),
        },
        "git": git_state(RECORD),
    }
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def render(rows: list[dict]) -> str:
    header = f"{'channel':<30}{'type':<16}{'posts':>7}{'comments':>10}{'threads':>9}  watch"
    lines = [header, "-" * len(header)]
    for row in sorted(rows, key=lambda r: -r["posts_stored"]):
        lines.append(
            f"{row['channel'][:29]:<30}{row['source_type']:<16}{row['posts_stored']:>7}"
            f"{row['comments_stored']:>10}{row['threads_with_comments']:>9}"
            f"  {'yes' if row['watch'] else ''}"
        )
    return "\n".join(lines)


async def run(args, registry, gate) -> dict:
    prior = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else None
    first_run = held(prior, "window", {}).get("first_run_at") or datetime.now(UTC).isoformat(
        timespec="seconds"
    )
    since = datetime.fromisoformat(
        held(prior, "window", {}).get("since")
        or (datetime.fromisoformat(first_run) - timedelta(days=WINDOW_DAYS)).isoformat()
    )

    channels = collectable(registry, gate)
    salt = load_salt()  # also loads .env, so the session name is available below
    session = os.environ["TELEGRAM_SESSION"]
    store = RawStore(STORE_ROOT)
    cursor = loop.load_cursor(CURSOR)
    extra = {"phases_run": [], "joins": {}}

    client = build_client()
    await client.connect()
    try:
        if not await client.is_user_authorized():
            raise SystemExit("No Telegram session. Run: python3 scripts/tg_login.py")

        if args.join:
            extra["joins"] = await run_joins(client, joinable(registry, gate), args.max)
            extra["phases_run"].append("join")

        if args.posts or args.comments:
            # The LAST row per channel wins, so a `left` row takes a group back out of scope.
            joined = {
                handle
                for handle, row in join_state().items()
                if row["outcome"] in ("joined", "already_member")
            }
            for source, handle in channels:
                print(f"{handle} ({source.id})", flush=True)
                entity = await client.get_entity(handle)
                provenance = make_provenance(source, session)
                state = loop.channel_state(cursor, handle)
                if args.posts:
                    got = await walk_window(
                        client, entity, source, handle, since, store, provenance
                    )
                    ids = store.index("post", handle).ids
                    loop.advance(state, loop.POSTS, ids)
                    print(f"  {got['posts_stored']} new posts", flush=True)
                if args.comments and source.comments_enabled and not source.watch:
                    if handle not in joined:
                        print("  join has not landed — comments skipped", flush=True)
                    else:
                        got = await fetch_threads(
                            client, entity, source, handle, store, salt, provenance
                        )
                        print(f"  {got['comments_stored']} comments in {got['threads']} threads")
                loop.save_cursor(CURSOR, cursor)
                await asyncio.sleep(CHANNEL_PAUSE)
            extra["phases_run"] += ["posts"] * args.posts + ["comments"] * args.comments
    finally:
        loop.save_cursor(CURSOR, cursor)
        await client.disconnect()

    rows = [channel_row(store, source, handle) for source, handle in channels]
    return write_record(registry, gate, rows, since, first_run, extra)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="5c1 Deliverable 2: joins and the 28-day window.")
    parser.add_argument("--join", action="store_true", help="join the authorised groups, paced")
    parser.add_argument("--posts", action="store_true", help="collect the posts window")
    parser.add_argument("--comments", action="store_true", help="collect threads in joined groups")
    parser.add_argument("--max", type=int, help="cap the joins attempted in this invocation")
    parser.add_argument(
        "--leave", metavar="HANDLE", nargs="+", help="leave these channels' discussion groups"
    )
    parser.add_argument("--plan", action="store_true", help="print the scope and stop, no client")
    args = parser.parse_args(argv)

    registry = load_registry(REGISTRY)
    gate = json.loads(GATE_RECORD.read_text(encoding="utf-8"))
    if not gate.get("registry_written"):
        raise SystemExit("the rulings have not been applied yet — run apply_gate_rulings_5c1.py")

    channels = collectable(registry, gate)
    joins = joinable(registry, gate)
    if args.leave:
        authorised = {handle for _, handle in joins}
        unknown = set(args.leave) - authorised
        if unknown:
            raise SystemExit(f"not groups this phase ever joined: {sorted(unknown)}")

        async def run_leave():
            client = build_client()
            await client.connect()
            try:
                if not await client.is_user_authorized():
                    raise SystemExit("No Telegram session. Run: python3 scripts/tg_login.py")
                for handle in args.leave:
                    row = await leave_group(client, handle)
                    log_join(row)
                    print(f"  {handle}: {row['outcome']} — {row.get('group_title')}")
            finally:
                await client.disconnect()

        asyncio.run(run_leave())
        print(f"\nlogged in {JOIN_LOG.relative_to(REPO_ROOT)}; --comments will skip these now")
        return 0

    if args.plan or not (args.join or args.posts or args.comments):
        state = join_state()
        landed = sum(
            1
            for h in (h for _, h in joins)
            if state.get(h, {}).get("outcome") in ("joined", "already_member")
        )
        print(f"collect: {len(channels)} channels ({sum(1 for s, _ in channels if s.watch)} watch)")
        print(f"joins:   {len(joins)} authorised, {landed} landed, {len(joins) - landed} to go")
        print(f"window:  {WINDOW_DAYS} days · pace {JOIN_PAUSE:.0f}s between joins")
        print(f"protected: {len(protected())} raw v1 files, refused at channel level")
        return 0

    record = asyncio.run(run(args, registry, gate))
    print()
    print(render(record["channels"]))
    totals = record["totals"]
    print(
        f"\n{totals['channels']} channels · {totals['posts_stored']} posts ·"
        f" {totals['comments_stored']} comments · {totals['damaged_lines']} damaged lines"
    )
    print(f"window since {record['window']['since']} · record: {RECORD.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
