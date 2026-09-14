#!/usr/bin/env python3
"""Stage-2 regional collection: the channels of `config/region_channels.yaml` ($0, Telegram only).

PHASE-ship-1 §2 «region-collect» (ii), ruling (ggg) 14.09. Posts and comments of the eighteen
Poltava-oblast channels land in the NEW root `data/raw_region/{posts,comments}/<channel>.jsonl`.

A SIBLING of `scripts/collect_r2.py` rather than a `--region` flag on it, which is the fork §2 (ii)
leaves to the executor. Three facts decide it and none of them is a preference:

* check (ii) asks that NO promo reader walk `data/raw_region/`, and a flag would make the promo
  collector one — the grep that proves the roots are separate would have to except its own file;
* `collect_r2.py :: a1_sources()` selects `source.collect and bucket(source) == "A"`, and the
  regional set is bucket B with `collect: false`: the region run reads a different source of truth
  (the side file), not a different subset of the same one;
* `collect_r2.py` writes into `LIVE_ROOT` (`data/raw_r2/`), which ruling (ggg) 4 keeps free of
  regional rows.

The shared machinery — `RawStore`, `post_record`, `comment_record`, `collapse_albums`,
`make_provenance`, `build_client` — is IMPORTED. A second spelling of any of it would be free to
disagree with the one the promo pipeline reads.

No `--join` phase, and that is measured rather than assumed: a comment thread of these channels
reads through `iter_messages(channel, reply_to=<post>)` with the account joining nothing (probed on
@mo3ambik, @h_kremenchug, @poltava_pvp and @dikankaa before this script was written — three
messages each). Joining is the one action a collector takes that WRITES on Telegram's side and
`collect_r2` paces it at fifteen minutes; a phase that does not need it does not get it.

    PYTHONPATH=src python3.11 scripts/collect_region.py --plan
    PYTHONPATH=src python3.11 scripts/collect_region.py --posts
    PYTHONPATH=src python3.11 scripts/collect_region.py --comments

Every mode ends by writing `results/region_collect_report.json` — the thread coverage the Регіон
tab prints (ruling (hhh) 3). `--plan` writes it without a single Telegram call.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from telethon import functions  # noqa: E402
from telethon.errors import FloodWaitError  # noqa: E402

from market_pulse.raw_store import (  # noqa: E402
    ARCHIVE_ROOT,
    RawStore,
    collapse_albums,
    comment_record,
    load_salt,
    make_provenance,
    post_record,
)
from market_pulse.registry import Source  # noqa: E402
from market_pulse.telegram_client import build_client  # noqa: E402

SIDE_FILE = REPO_ROOT / "config" / "region_channels.yaml"
REGION_ROOT = REPO_ROOT / "data" / "raw_region"
"""Ruling (ggg) 4: region monitoring is a DIFFERENT population from the promo pipeline and its root
says so. Nothing under `data/raw_r2/` or `data/raw/` is written here."""

REPORT = REPO_ROOT / "results" / "region_collect_report.json"
"""The comment population is a SAMPLE and the screen has to say so (ruling (hhh) 3).

`--max-threads` reads the newest N threads per channel and PRINTS what it left; that print is a
line in a terminal nobody keeps. The three figures it names — threads_total, threads_read,
outstanding — become a file so `scripts/export_front_data.py` can carry them into the Регіон tab's
coverage table, where the honesty is in front of the operator instead of in a progress note."""

FALLBACK_WINDOW_DAYS = 28
"""Only for a channel with NO archived post at all. All eighteen have one today, so this is the
shape of an empty case and not the window any of them is actually collected over."""

REQUEST_PAUSE = 1.0
CHANNEL_PAUSE = 2.0
THREAD_PAUSE = 1.0
CHUNK = 200
PROGRESS_EVERY = 25
"""`collect_r2.py`'s pacing, copied deliberately: these are the rates that have not tripped a
FloodWait on this account since 30.08, and a regional sweep is the same kind of traffic."""


def side_channels() -> list[str]:
    """The handles, in file order. The file is the only list; nothing re-derives it."""
    loaded = yaml.safe_load(SIDE_FILE.read_text(encoding="utf-8"))
    handles = [entry["handle"] for entry in loaded["channels"]]
    # On the STORE KEY, not the literal spelling: `RawStore.path` strips the `@`, and a
    # case-insensitive filesystem then resolves `@poltava20` and `@Poltava20` to ONE file, which
    # a spelling-only check would let through. `scripts/region_sentinel.py :: load_channels`
    # makes the same refusal on the same key — two readers of one file must not drift.
    keys = [one.lstrip("@").casefold() for one in handles]
    if len(set(keys)) != len(keys):
        doubled = sorted({key for key in keys if keys.count(key) > 1})
        raise SystemExit(
            f"{SIDE_FILE}: {', '.join(doubled)} listed more than once — one store file would be"
            " written twice under two spellings of one channel"
        )
    return handles


def region_store() -> RawStore:
    """Writes into `data/raw_region/`, READS the v1 archive first.

    The archive is where these eighteen already have 6 769 posts, so it is what a collected row is
    deduplicated against: without it every re-run would write the July–August window a second time
    into the new root and the sentinel would count each of those posts twice. `RawStore.append`
    refuses to write into the archive itself, so reading it here cannot grow it.
    """
    return RawStore(REGION_ROOT, archives=(ARCHIVE_ROOT,))


def region_source(handle: str, store: RawStore) -> Source:
    """A `Source` for the record functions — built from the side file, never from the registry.

    `comments_enabled` is MEASURED, not declared: the promo registry says `false` for all
    seventeen, and that flag is the promo pipeline's (`collect_r2` skips a channel on it). Ruling
    (ggg) 5's criterion is the archive's own — «comments arrive where posts carry `reply_count` >
    0» — so that is what the provenance of a regional row carries. What the channel's discussion
    group actually answers today is a different question, and `--comments` asks it live.
    """
    return Source(
        id=handle.lstrip("@"),
        name=handle,
        source_type="community",
        telegram_channels=(handle,),
        comments_enabled=bool(store.index("post", handle).with_replies),
        audience="regional",
    )


def since_of(handle: str) -> datetime:
    """The window start: the last post the FROZEN v1 archive holds for this channel.

    Derived from a read-only root, so it is the same value on every run and on a resume — which is
    the property `collect_r2.since_of` buys with a cursor file in `results/`. A `since` read back
    from the growing store would not have it: `walk_window` collects newest-first, so an interrupted
    run leaves the NEWEST rows stored, and the next run would start at them and never come back for
    the middle. A channel with nothing archived falls back to a plain window.
    """
    last = RawStore(ARCHIVE_ROOT).index("post", handle).last_date
    return (
        datetime.fromisoformat(last)
        if last
        else datetime.now(UTC) - timedelta(days=FALLBACK_WINDOW_DAYS)
    )


async def walk_window(client, entity, source, handle, since, store, provenance, written) -> int:
    """Posts newer than `since`, flushed in chunks so an interrupt keeps what it read.

    `written` is the channel's row in the summary and is updated after EVERY flush, not returned at
    the end: the rows are already on disk by then, and a raise on the next page would leave the
    caller with no number to print for rows that exist ([[log_the_side_effect_that_already_happened]]).
    """
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
            written["posts"] = stored
            buffer.clear()
        buffer.append(post_record(message, source, handle, provenance))
    stored += store.append(collapse_albums(buffer))
    written["posts"] = stored
    return stored


async def linked_group(client, entity):
    """The channel's discussion group id, or None when it has none to read."""
    full = await client(functions.channels.GetFullChannelRequest(channel=entity))
    return full.full_chat.linked_chat_id


async def fetch_threads(client, entity, source, handle, store, salt, provenance, cap) -> dict:
    """The comment threads of stored posts that have none yet, newest post first."""
    posts = store.index("post", handle)
    todo = sorted(posts.with_replies - store.index("comment", handle).parents, reverse=True)
    left = todo[cap:] if cap is not None else []
    todo = todo[:cap] if cap is not None else todo
    stored, failed, read = 0, 0, 0
    for done, parent in enumerate(todo, start=1):
        try:
            records = [
                comment_record(message, source, handle, parent, salt, provenance)
                async for message in client.iter_messages(
                    entity, reply_to=parent, wait_time=REQUEST_PAUSE
                )
                if message.action is None
            ]
            stored += store.append(records)
            read += 1
        except FloodWaitError as exc:
            # The thread is ABANDONED, not retried, so it is a failure and not a read. `len(todo)`
            # as the read count would report coverage of a thread whose comments were never
            # fetched — and this number is the item's own evidence of what was collected. The
            # thread returns to `todo` on the next run: `todo` is «has replies, has no stored
            # comment», so an abandoned thread is still outstanding and resumes for free.
            failed += 1
            print(f"    FloodWait {exc.seconds}s — thread {parent} left, sleeping", flush=True)
            await asyncio.sleep(exc.seconds)
        except Exception as exc:  # noqa: BLE001 — one bad thread must not end the channel
            failed += 1
            print(f"    thread {parent}: {type(exc).__name__}: {exc}", flush=True)
        if done % PROGRESS_EVERY == 0:
            print(f"    {done}/{len(todo)} threads, {stored} comments", flush=True)
        await asyncio.sleep(THREAD_PAUSE)
    return {
        "threads_read": read,
        "comments_stored": stored,
        "threads_failed": failed,
        "threads_left": len(left),
    }


def channel_row(store: RawStore, handle: str, written: dict) -> dict:
    """One channel's line: what the corpus holds, and what THIS run wrote into the region root."""
    posts = store.index("post", handle)
    comments = store.index("comment", handle)
    return {
        "channel": handle,
        "posts_stored": posts.count,
        "posts_first": posts.first_date,
        "posts_last": posts.last_date,
        "comments_stored": comments.count,
        "threads_with_comments": len(comments.parents),
        "threads_with_replies": len(posts.with_replies),
        "posts_written": written.get("posts"),
        "comments_written": written.get("comments"),
        "discussion": written.get("discussion"),
        "damaged_lines": posts.damaged_lines + comments.damaged_lines,
    }


def report(store: RawStore) -> dict:
    """Thread coverage per channel, read off the STORE and never off this run's counters.

    Over `side_channels()` whatever `--only` says: the three figures are properties of what is on
    disk, not of what one invocation touched, and a report rebuilt from a filtered run would
    silently shrink the committed artifact to the channels that run happened to name
    ([[a_shrunk_population_is_a_test_change]]). Two runs over an unchanged store therefore write
    identical bytes.

    `threads_total` is «posts that carry replies», `threads_read` is «posts a stored comment points
    back at» and `outstanding` is the difference — the same three quantities `fetch_threads` works
    from (`todo = with_replies - parents`), so the queue the screen prints is the queue the next run
    will actually drain.
    """
    rows = []
    for handle in side_channels():
        posts = store.index("post", handle)
        comments = store.index("comment", handle)
        total, read = len(posts.with_replies), len(comments.parents)
        rows.append(
            {
                "channel": handle,
                "threads_total": total,
                "threads_read": read,
                "outstanding": total - read,
            }
        )
    return {
        "contract": "PHASE-ship-1 §2 «reactions-region» (ruling (hhh) 3) — the comment SAMPLE as a"
        " field the screen can print",
        "from": "data/raw_region/ ∪ the frozen data/raw/ archive, through market_pulse.raw_store:"
        " threads_total = posts with reply_count > 0, threads_read = posts a stored comment names"
        " as its parent",
        "channels": rows,
        "totals": {
            "channels": len(rows),
            "threads_total": sum(row["threads_total"] for row in rows),
            "threads_read": sum(row["threads_read"] for row in rows),
            "outstanding": sum(row["outstanding"] for row in rows),
        },
    }


def write_report(store: RawStore, path: Path = REPORT) -> dict:
    """Write the coverage report and return it. Called at the END of every mode, `--plan` included.

    The plan mode makes no Telegram call at all, so the file is reproducible at $0 by anyone with
    the store — which is what lets `make front` be re-run without a collection.
    """
    body = report(store)
    path.write_text(
        json.dumps(body, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        f"\n{path.relative_to(REPO_ROOT)}: {body['totals']['threads_read']} of"
        f" {body['totals']['threads_total']} threads read ·"
        f" {body['totals']['outstanding']} outstanding",
        flush=True,
    )
    return body


def render(rows: list[dict]) -> str:
    head = (
        f"{'channel':<22}{'posts':>7}{'+new':>6}{'first':>12}{'last':>12}"
        f"{'thr':>6}{'comments':>10}{'+new':>6}{'read':>6}  discussion"
    )
    lines = [head, "-" * len(head)]
    for row in rows:
        lines.append(
            f"{row['channel']:<22}{row['posts_stored']:>7}{str(row['posts_written']):>6}"
            f"{str(row['posts_first'])[:10]:>12}{str(row['posts_last'])[:10]:>12}"
            f"{row['threads_with_replies']:>6}{row['comments_stored']:>10}"
            f"{str(row['comments_written']):>6}{row['threads_with_comments']:>6}"
            f"  {row['discussion'] or ''}"
        )
    return "\n".join(lines)


async def run(args) -> list[dict]:
    store = region_store()
    handles = side_channels()
    if args.only:
        wanted = {one.lstrip("@").lower() for one in args.only}
        handles = [one for one in handles if one.lstrip("@").lower() in wanted]
    written: dict[str, dict] = {one: {} for one in handles}

    if args.plan:
        for handle in handles:
            since = since_of(handle)
            written[handle] = {"discussion": f"would collect since {since.isoformat()[:10]}"}
        rows = [channel_row(store, handle, written[handle]) for handle in handles]
        print(render(rows))
        print(f"\n{len(rows)} regional channels; no Telegram call was made.")
        write_report(store)
        return rows

    salt = load_salt()
    client = build_client()
    await client.start()
    try:
        for handle in handles:
            source = region_source(handle, store)
            provenance = make_provenance(source, "collect_region")
            try:
                entity = await client.get_entity(handle)
            except Exception as exc:  # noqa: BLE001 — a dead handle must not end the run
                print(f"  {handle}: {type(exc).__name__}: {exc}", flush=True)
                written[handle]["discussion"] = f"unresolved: {type(exc).__name__}"
                continue

            if args.posts:
                since = since_of(handle)
                try:
                    got = await walk_window(
                        client, entity, source, handle, since, store, provenance, written[handle]
                    )
                    print(f"  {handle}: +{got} posts since {since.isoformat()[:10]}", flush=True)
                except FloodWaitError as exc:
                    print(f"  {handle}: FloodWait {exc.seconds}s — sleeping", flush=True)
                    await asyncio.sleep(exc.seconds)
                except Exception as exc:  # noqa: BLE001
                    print(f"  {handle}: {type(exc).__name__}: {exc}", flush=True)

            if args.comments:
                try:
                    linked = await linked_group(client, entity)
                except Exception as exc:  # noqa: BLE001 — one channel must not end the sweep
                    # `GetFullChannelRequest` is a SEPARATE rpc from `get_entity`, which telethon
                    # can answer from the session cache without a network call — so this is the one
                    # place in the loop a live failure lands. Unguarded it killed the whole run AND
                    # `render(rows)` below it, so the per-channel counts §2 (ii) requires printed
                    # were lost for the channels already collected. A channel that has gone private
                    # would take every channel after it in file order with it, on every run.
                    #
                    # The recorded outcome is the ERROR, never `comments: 0`: a zero here is a
                    # measured fact about a channel with no discussion group, and an rpc that did
                    # not answer is not that fact ([[a_stub_replaces_the_guard_it_should_trigger]]).
                    written[handle]["discussion"] = f"unread: {type(exc).__name__}: {exc}"
                    print(
                        f"  {handle}: {type(exc).__name__}: {exc} — comments not read", flush=True
                    )
                    await asyncio.sleep(CHANNEL_PAUSE)
                    continue
                if linked is None:
                    # §2 (ii): a channel without a linked discussion is a printed ZERO, never a
                    # failure. The promo registry's `comments_enabled: false` is NOT this answer —
                    # it is the promo pipeline's flag and says nothing about what the group holds.
                    written[handle] |= {"comments": 0, "discussion": "no linked group"}
                    print(f"  {handle}: no linked discussion group — 0 comments", flush=True)
                else:
                    got = await fetch_threads(
                        client, entity, source, handle, store, salt, provenance, args.max_threads
                    )
                    written[handle] |= {
                        "comments": got["comments_stored"],
                        "discussion": f"group {linked} · {got['threads_read']} threads read"
                        + (f" · {got['threads_failed']} failed" if got["threads_failed"] else "")
                        + (f" · {got['threads_left']} LEFT" if got["threads_left"] else ""),
                    }
                    print(
                        f"  {handle}: +{got['comments_stored']} comments over"
                        f" {got['threads_read']} threads",
                        flush=True,
                    )
            await asyncio.sleep(CHANNEL_PAUSE)
    finally:
        await client.disconnect()

    rows = [channel_row(store, handle, written[handle]) for handle in handles]
    print(render(rows))
    write_report(store)
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true", help="what is stored today; no Telegram")
    parser.add_argument("--posts", action="store_true", help="posts newer than the archive's last")
    parser.add_argument("--comments", action="store_true", help="threads of stored posts")
    parser.add_argument("--only", nargs="*", help="restrict to these handles")
    parser.add_argument(
        "--max-threads",
        type=int,
        default=None,
        help="read at most N threads per channel; the rest are PRINTED as left, never dropped"
        " silently",
    )
    args = parser.parse_args(argv)
    if not any((args.plan, args.posts, args.comments)):
        parser.error("choose --plan, --posts or --comments")
    asyncio.run(run(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
