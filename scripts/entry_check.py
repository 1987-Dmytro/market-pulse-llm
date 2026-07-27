#!/usr/bin/env python3
"""Phase-2b channel entry check (docs/SPEC.md §2, §8).

For every candidate handle in config/registry.yaml: does the channel exist, is it
the blue-check one, are comments enabled, does it carry traffic? Writes
data/entry_check_report.json (gitignored raw data) and prints the table the
operator reviews before flipping `verified:` in the registry — this script never
edits the registry itself.

`--discover "<query>"` runs the same check over Telegram's global search instead of
the registry: SPEC §9 falls back to aggregator and community channels wherever a
chain has comments disabled, and this is how those candidates are found.

Read-only and deliberately slow: one channel at a time, a pause between channels,
no joins, no member lists. FloodWait aborts the run but keeps what was collected.

    python3.11 scripts/tg_login.py     # once, to create the session
    python3.11 scripts/entry_check.py
    python3.11 scripts/entry_check.py --discover "молочні продукти"
"""

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from telethon import functions, types
from telethon.errors import (
    ChannelPrivateError,
    FloodWaitError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
)

from market_pulse.entry_check import build_verdict, collapse_albums, traffic_stats
from market_pulse.registry import Source, load_registry
from market_pulse.telegram_client import build_client

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
DATA_DIR = REPO_ROOT / "data"
POST_SAMPLE = 50
PAUSE_SECONDS = 2.0
DISCOVER_LIMIT = 15
RESOLVE_ERRORS = (UsernameNotOccupiedError, UsernameInvalidError, ChannelPrivateError, ValueError)


async def suggest(client, name: str) -> list[dict]:
    """Global search fallback for a handle that does not resolve, verified first."""
    found = await client(functions.contacts.SearchRequest(q=name, limit=10))
    matches = [
        {
            "title": chat.title,
            "username": getattr(chat, "username", None),
            "telegram_verified": bool(getattr(chat, "verified", False)),
            "subscribers": getattr(chat, "participants_count", None),
        }
        for chat in found.chats
        if getattr(chat, "username", None)
    ]
    matches.sort(key=lambda m: not m["telegram_verified"])
    return matches


async def sample_traffic(client, entity) -> dict:
    """Traffic over the last POST_SAMPLE posts.

    The comment count comes from each post's reply counter rather than from reading
    the linked group: it is the same number for one request instead of N, and it
    needs no join (SPEC §9 — conservative limits).
    """
    messages = await client.get_messages(entity, limit=POST_SAMPLE)
    samples = [
        (
            m.date,
            m.replies.replies if m.replies else None,
            m.grouped_id,
            m.action is not None,
        )
        for m in messages
    ]
    return traffic_stats(collapse_albums(samples))


async def check_channel(client, source, handle: str) -> dict:
    record = {
        "source_id": source.id,
        "source_name": source.name,
        "source_type": source.source_type,
        "handle": handle,
    }

    try:
        entity = await client.get_entity(handle)
    except RESOLVE_ERRORS as exc:
        record["resolved"] = False
        record["error"] = f"{type(exc).__name__}: {exc}"
        record["suggestions"] = await suggest(client, source.name)
        return record | build_verdict(
            resolved=False,
            telegram_verified=False,
            scam=False,
            fake=False,
            comments_enabled=False,
            stats={},
        )

    if not isinstance(entity, types.Channel):
        record["resolved"] = False
        record["error"] = f"resolves to {type(entity).__name__}, not a channel"
        record["suggestions"] = await suggest(client, source.name)
        return record | {"verdict": "rejected", "reasons": [record["error"]]}

    full = (await client(functions.channels.GetFullChannelRequest(channel=entity))).full_chat
    stats = await sample_traffic(client, entity)
    record |= {
        "resolved": True,
        "title": entity.title,
        "username": entity.username,
        "telegram_verified": bool(entity.verified),
        # A supergroup resolves as a Channel too — record which one it really is.
        "broadcast": bool(entity.broadcast),
        "megagroup": bool(entity.megagroup),
        "scam": bool(entity.scam),
        "fake": bool(entity.fake),
        "subscribers": full.participants_count,
        "discussion_group_id": full.linked_chat_id,
        "comments_enabled": full.linked_chat_id is not None,
        "traffic": stats,
    }
    return record | build_verdict(
        resolved=True,
        telegram_verified=record["telegram_verified"],
        scam=record["scam"],
        fake=record["fake"],
        comments_enabled=record["comments_enabled"],
        stats=stats,
        broadcast=record["broadcast"],
    )


def cell(value, width: int) -> str:
    text = "—" if value is None else str(value)
    # width - 1 keeps at least one space between columns.
    text = text if len(text) < width else text[: width - 2] + "…"
    return text.ljust(width)


def print_table(records: list[dict]) -> None:
    header = (
        f"{'source':<11}{'handle':<22}{'title':<24}{'blue':<5}"
        f"{'subs':<9}{'comm':<6}{'posts/d':<9}{'%comm':<7}{'med':<5}verdict"
    )
    print(f"\n{header}\n{'-' * len(header)}")
    for r in records:
        traffic = r.get("traffic", {})
        print(
            cell(r["source_id"], 11)
            + cell(r["handle"], 22)
            + cell(r.get("title"), 24)
            + cell("yes" if r.get("telegram_verified") else "no", 5)
            + cell(r.get("subscribers"), 9)
            + cell("yes" if r.get("comments_enabled") else "no", 6)
            + cell(traffic.get("posts_per_day"), 9)
            + cell(traffic.get("share_with_comments"), 7)
            + cell(traffic.get("median_comments"), 5)
            + r["verdict"]
        )
        for reason in r.get("reasons", []):
            print(f"{'':<11}  ! {reason}")
        for match in r.get("suggestions", [])[:5]:
            check = "✓" if match["telegram_verified"] else " "
            print(f"{'':<11}  ? @{match['username']} {check} {match['title']}")


async def collect(client, candidates: list[tuple[Source, str]], records: list[dict]) -> int | None:
    """Check every (source, handle) pair, appending records. Returns FloodWait seconds."""
    for source, handle in candidates:
        print(f"checking {handle} ({source.id})...", flush=True)
        try:
            records.append(await check_channel(client, source, handle))
        except FloodWaitError as exc:
            return exc.seconds
        except Exception as exc:
            # One unusable channel must not discard the rest of the run.
            records.append(
                {
                    "source_id": source.id,
                    "source_name": source.name,
                    "source_type": source.source_type,
                    "handle": handle,
                    "resolved": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "verdict": "error",
                    "reasons": ["unexpected failure, see error"],
                }
            )
        await asyncio.sleep(PAUSE_SECONDS)
    return None


async def search_channels(client, query: str) -> list[tuple[Source, str]]:
    """Top public channels for a query, as candidates for the same per-channel check.

    Everything found is `community` until the operator decides otherwise — a real
    aggregator gets that source_type when it is added to the registry by hand.
    """
    found = await client(functions.contacts.SearchRequest(q=query, limit=DISCOVER_LIMIT))
    candidates = []
    for chat in found.chats:
        username = getattr(chat, "username", None)
        if not username:
            continue  # private or invite-only: not collectable
        handle = f"@{username}"
        source = Source("found", chat.title, "community", (handle,))
        candidates.append((source, handle))
    return candidates


def report_path(query: str | None) -> Path:
    if query is None:
        return DATA_DIR / "entry_check_report.json"
    # One file per query: three discovery runs must not overwrite each other, and
    # re-running a scan costs another rate-limited pass.
    slug = re.sub(r"\W+", "-", query.strip()).strip("-").lower()
    return DATA_DIR / f"discovery_{slug}.json"


def rank(record: dict) -> tuple:
    """Discovery order: channels that carry comments first, liveliest first."""
    return (
        bool(record.get("comments_enabled")),
        record.get("traffic", {}).get("median_comments", 0),
    )


async def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Telegram channel entry check.")
    parser.add_argument(
        "--discover",
        metavar="QUERY",
        help="check the top public channels Telegram returns for QUERY instead of the registry",
    )
    args = parser.parse_args(argv)

    records: list[dict] = []
    flood_wait = None

    client = build_client()
    await client.connect()
    try:
        if not await client.is_user_authorized():
            print("No Telegram session. Run: python3.11 scripts/tg_login.py")
            return 2
        if args.discover:
            candidates = await search_channels(client, args.discover)
            print(f"{len(candidates)} public channels found for {args.discover!r}")
        else:
            candidates = [
                (source, handle)
                for source in load_registry(REGISTRY).sources
                for handle in source.telegram_channels
            ]
        flood_wait = await collect(client, candidates, records)
    finally:
        await client.disconnect()

    if args.discover:
        records.sort(key=rank, reverse=True)

    path = report_path(args.discover)
    path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "query": args.discover,
        "registry": None if args.discover else str(REGISTRY.relative_to(REPO_ROOT)),
        "post_sample": POST_SAMPLE,
        "channels": records,
    }
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print_table(records)
    print(f"\nreport: {path.relative_to(REPO_ROOT)} ({len(records)} channels)")
    if flood_wait is not None:
        print(f"FloodWait: Telegram asks for {flood_wait}s — stopped early, re-run after that.")
        return 1
    print("Registry stays untouched: the team lead edits it after reviewing this.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
