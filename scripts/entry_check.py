#!/usr/bin/env python3
"""Phase-2b channel entry check (docs/SPEC.md §2, §8).

For every candidate handle in config/registry.yaml: does the channel exist, is it
the blue-check one, are comments enabled, does it carry traffic? Writes
data/entry_check_report.json (gitignored raw data) and prints the table the
operator reviews before flipping `verified:` in the registry — this script never
edits the registry itself.

Read-only and deliberately slow: one channel at a time, a pause between channels,
no joins, no member lists. FloodWait aborts the run but keeps what was collected.

    python3.11 scripts/entry_check.py

The first run performs an interactive login (phone number + confirmation code).
"""

import json
import sys
import time
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
from market_pulse.registry import load_registry
from market_pulse.telegram_client import build_client

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
REPORT = REPO_ROOT / "data" / "entry_check_report.json"
POST_SAMPLE = 50
PAUSE_SECONDS = 2.0
RESOLVE_ERRORS = (UsernameNotOccupiedError, UsernameInvalidError, ChannelPrivateError, ValueError)


def suggest(client, name: str) -> list[dict]:
    """Global search fallback for a handle that does not resolve, verified first."""
    found = client(functions.contacts.SearchRequest(q=name, limit=10))
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


def sample_traffic(client, entity) -> dict:
    """Traffic over the last POST_SAMPLE posts.

    The comment count comes from each post's reply counter rather than from reading
    the linked group: it is the same number for one request instead of N, and it
    needs no join (SPEC §9 — conservative limits).
    """
    messages = client.get_messages(entity, limit=POST_SAMPLE)
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


def check_channel(client, source, handle: str) -> dict:
    record = {
        "source_id": source.id,
        "source_name": source.name,
        "source_type": source.source_type,
        "handle": handle,
    }

    try:
        entity = client.get_entity(handle)
    except RESOLVE_ERRORS as exc:
        record["resolved"] = False
        record["error"] = f"{type(exc).__name__}: {exc}"
        record["suggestions"] = suggest(client, source.name)
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
        record["suggestions"] = suggest(client, source.name)
        return record | {"verdict": "rejected", "reasons": [record["error"]]}

    full = client(functions.channels.GetFullChannelRequest(channel=entity)).full_chat
    stats = sample_traffic(client, entity)
    record |= {
        "resolved": True,
        "title": entity.title,
        "username": entity.username,
        "telegram_verified": bool(entity.verified),
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


def main() -> int:
    registry = load_registry(REGISTRY)
    records: list[dict] = []
    flood_wait = None

    with build_client() as client:
        for source in registry.sources:
            for handle in source.telegram_channels:
                print(f"checking {handle} ({source.id})...", flush=True)
                try:
                    records.append(check_channel(client, source, handle))
                except FloodWaitError as exc:
                    flood_wait = exc.seconds
                    break
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
                time.sleep(PAUSE_SECONDS)
            if flood_wait is not None:
                break

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "registry": str(REGISTRY.relative_to(REPO_ROOT)),
        "post_sample": POST_SAMPLE,
        "channels": records,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print_table(records)
    print(f"\nreport: {REPORT.relative_to(REPO_ROOT)} ({len(records)} channels)")
    if flood_wait is not None:
        print(f"FloodWait: Telegram asks for {flood_wait}s — stopped early, re-run after that.")
        return 1
    print("Registry stays untouched: the team lead flips `verified:` after reviewing this.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
