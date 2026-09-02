#!/usr/bin/env python3
"""C2's pages on disk ($0, Telegram only): the photo members of the census's pinned posts.

The paid pass reads a page through `run_loop.pages_of(manifest, handle)` — a manifest that maps a
post to the files of its album — and the three manifests on disk cover 367 of the census's 968
pinned posts. This fetch writes the fourth, for that population and nothing else: the pinned ids
of `results/promo_census_c2.json`, never a window re-evaluated now (SPEC 3.18 (4)). A page is a
PHOTO member exactly as `scripts/promo_pagecount_c2.py` counted it, so the files per channel are
checked against `results/promo_pagecount_c2.json :: pages_exact` and a mismatch is PRINTED and
recorded, never silently priced.

Resumable: a file already on disk is hashed and kept, not fetched twice — a FloodWait in the middle
of 3 008 downloads costs the wait, not the pages before it. Nothing is written to the raw store.

    python3.11 scripts/fetch_promo_media_c2.py --plan     # offline: owed vs on disk, per channel
    PYTHONPATH=src python3.11 scripts/fetch_promo_media_c2.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import promo_pagecount_c2 as pagecount  # noqa: E402

MEDIA = REPO_ROOT / "data" / "annotation" / "promo_c2" / "posts_media"
MANIFEST = REPO_ROOT / "results" / "post_media_promo_c2.json"
DOWNLOAD_PAUSE = 0.4
"""`scripts/fetch_post_media.py::PAUSE` — the same courtesy between downloads."""
FLOOD_RETRIES = 3


def stem(channel: str, msg_id: int) -> str:
    return f"{channel.lstrip('@')}_{msg_id}"


def albums(messages: list) -> dict[int, list]:
    """Album members grouped under the msg_id the store keyed the album by — `min(msg_id)`.

    `pagecount.fold`'s key exactly, with the messages kept instead of counted: the fold is what
    joins a Telegram group back to the census's pinned id, and the members are what gets fetched.
    """
    groups: dict[object, list] = {}
    for message in messages:
        key = message.grouped_id if message.grouped_id is not None else ("solo", message.id)
        groups.setdefault(key, []).append(message)
    return {
        min(member.id for member in members): sorted(members, key=lambda one: one.id)
        for members in groups.values()
    }


def on_disk(channel: str, directory: Path = MEDIA) -> list[Path]:
    return sorted(directory.glob(f"{channel.lstrip('@')}_*.jpg"))


def expected(record: dict) -> dict[str, dict]:
    """Per channel: the pinned posts and the exact page count the pagecount re-read."""
    return {row["channel"]: row for row in record["channels"]}


async def download(client, handle: str, message, directory: Path) -> dict:
    """One photo on disk — fetched once, hashed every time."""
    from telethon.errors import FloodWaitError

    target = directory / f"{stem(handle, message.id)}.jpg"
    if not target.exists():
        for _attempt in range(FLOOD_RETRIES):
            try:
                written = await client.download_media(message, file=str(target))
                break
            except FloodWaitError as exc:
                print(f"  FloodWait: sleeping {exc.seconds}s", flush=True)
                await asyncio.sleep(exc.seconds)
        else:
            return {"msg_id": message.id, "missing": "floodwait"}
        if written is None:
            return {"msg_id": message.id, "missing": "telegram returned no file"}
        target = Path(written)
        await asyncio.sleep(DOWNLOAD_PAUSE)
    data = target.read_bytes()
    return {
        "msg_id": message.id,
        "file": target.relative_to(REPO_ROOT).as_posix(),
        "sha256": sha256(data).hexdigest(),
        "bytes": len(data),
    }


async def fetch_channel(client, handle: str, pinned: set[int], since, anchor, directory) -> dict:
    """One metadata pass over the window (the pagecount's), then the pinned albums' photos."""
    entity = await client.get_entity(handle)
    seen = []
    async for message in client.iter_messages(entity, wait_time=pagecount.REQUEST_PAUSE):
        if message.action is not None:
            continue
        if message.date < since:
            break
        if message.date >= anchor:
            continue
        seen.append(message)
    out = {}
    for msg_id, members in albums(seen).items():
        if msg_id not in pinned:
            continue
        images, missing = [], []
        for message in members:
            kind = pagecount.page_kind(message)
            if kind == "photo":
                got = await download(client, handle, message, directory)
                (images if "file" in got else missing).append(got)
            elif kind != "none":
                missing.append({"msg_id": message.id, "missing": f"media is {kind}"})
        out[msg_id] = {
            "channel": handle,
            "msg_id": msg_id,
            "date": min(member.date for member in members).isoformat(),
            "album": any(member.grouped_id is not None for member in members),
            "images": images,
            "missing": missing,
        }
    return out


def channel_summary(handle: str, want: dict, entries: dict) -> dict:
    mine = [entry for entry in entries.values() if entry["channel"] == handle]
    images = sum(len(entry["images"]) for entry in mine)
    return {
        "channel": handle,
        "pinned_media_posts": want["pinned_media_posts"],
        "posts_fetched": len(mine),
        "posts_unreachable": want["pinned_media_posts"] - len(mine),
        "images": images,
        "pages_exact": want["pages_exact"],
        "matches_pagecount": images == want["pages_exact"],
    }


def render(rows: list[dict]) -> str:
    head = f"{'channel':<24}{'posts':>6}{'fetched':>8}{'images':>7}{'exact':>7}  match"
    lines = [head, "-" * len(head)]
    for row in rows:
        lines.append(
            f"{row['channel']:<24}{row['pinned_media_posts']:>6}{row['posts_fetched']:>8}"
            f"{row['images']:>7}{row['pages_exact']:>7}  {'ok' if row['matches_pagecount'] else 'MISMATCH'}"
        )
    return "\n".join(lines)


def write_manifest(census: dict, record: dict, entries: dict, by_channel: list[dict]) -> None:
    manifest = {
        "contract": "docs/plans/promo-pulse-1.md S4 — the census's pages on disk ($0, Telegram)",
        "window": census["window"],
        "selection": {
            "ids_sha256": census["selection"]["ids_sha256"],
            "posts": census["selection"]["leaflet_page"]["posts"],
            "pages_expected": record["totals"]["pages_exact"],
            "pages_expected_from": "results/promo_pagecount_c2.json :: totals.pages_exact",
        },
        "media": MEDIA.relative_to(REPO_ROOT).as_posix(),
        "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "by_channel": by_channel,
        "totals": {
            "posts_fetched": sum(row["posts_fetched"] for row in by_channel),
            "posts_unreachable": sum(row["posts_unreachable"] for row in by_channel),
            "images": sum(row["images"] for row in by_channel),
            "pages_expected": record["totals"]["pages_exact"],
            "channels_matching_pagecount": sum(row["matches_pagecount"] for row in by_channel),
            "channels": len(by_channel),
        },
        "entries": {f"{entry['channel']}:{entry['msg_id']}": entry for entry in entries.values()},
    }
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


async def run(census: dict, record: dict) -> tuple[dict, list[dict]]:
    from market_pulse.telegram_client import build_client

    window = census["window"]
    since = datetime.fromisoformat(window["since"]).replace(tzinfo=UTC)
    anchor = datetime.fromisoformat(window["anchor"]).replace(tzinfo=UTC)
    want = expected(record)
    pinned = {
        entry["channel"]: {int(one) for one in entry["media_msg_ids"]}
        for entry in census["channels"]
        if entry["media_msg_ids"]
    }
    MEDIA.mkdir(parents=True, exist_ok=True)
    client = build_client()
    await client.start()
    entries: dict = {}
    by_channel: list[dict] = []
    try:
        for handle in sorted(pinned):
            print(f"{handle}: {len(pinned[handle])} pinned posts", flush=True)
            got = await fetch_channel(client, handle, pinned[handle], since, anchor, MEDIA)
            entries |= {(handle, msg_id): entry for msg_id, entry in got.items()}
            by_channel.append(channel_summary(handle, want[handle], entries))
            print(f"  {render([by_channel[-1]]).splitlines()[-1]}", flush=True)
            write_manifest(census, record, entries, by_channel)  # partial on purpose: resumable
    finally:
        await client.disconnect()
    return entries, by_channel


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true", help="offline: owed vs on disk")
    args = parser.parse_args()

    census = json.loads(pagecount.CENSUS.read_text(encoding="utf-8"))
    record = json.loads(pagecount.RECORD.read_text(encoding="utf-8"))
    print(
        f"population: {census['selection']['leaflet_page']['posts']} media posts,"
        f" {record['totals']['pages_exact']} pages exact · window"
        f" {census['window']['since']} … {census['window']['anchor']}"
    )
    if args.plan:
        rows = []
        for handle, want in sorted(expected(record).items()):
            files = len(on_disk(handle))
            rows.append(
                {
                    "channel": handle,
                    "pinned_media_posts": want["pinned_media_posts"],
                    "posts_fetched": 0,
                    "images": files,
                    "pages_exact": want["pages_exact"],
                    "matches_pagecount": files == want["pages_exact"],
                }
            )
        print(render(rows))
        print(f"on disk: {sum(row['images'] for row in rows)} of {record['totals']['pages_exact']}")
        return 0

    _entries, by_channel = asyncio.run(run(census, record))
    print()
    print(render(by_channel))
    total = sum(row["images"] for row in by_channel)
    print(f"\n{MANIFEST.relative_to(REPO_ROOT)} — {total} of {record['totals']['pages_exact']} pages")
    return 0 if all(row["matches_pagecount"] for row in by_channel) else 2


if __name__ == "__main__":
    raise SystemExit(main())
