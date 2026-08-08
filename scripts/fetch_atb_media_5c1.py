#!/usr/bin/env python3
"""The images of the 19 posts that made the yield screen refuse to report. ($0, network.)

@atb_market_official published 25 times in its screen window and 19 of those posts carry no text
at all — the whole reason the pre-registered positive control failed. This fetches exactly those
19, so that step 3 can ask a vision model what they say. The population is READ from
`results/image_census_5c1.json` rather than recomputed: the census named the ids, it is committed,
and a fetch that re-derived its own list could quietly buy captions for a different 19.

The 4.5g2 pattern, with its parts imported rather than copied: `album_ids` (a stored album is one
record under its first item's id, and the informative picture is usually not that one), `download`
(a photo is a photo; a video is named as missing, never guessed at) and `poll_of` (a poll's
question is text Telegram has been carrying all along, and reading it costs nothing).

One thing is NOT the 4.5g2 pattern. Its `fetch_channel` sleeps a FloodWait out in full; this
account lost 20 hours to one such wall in phase 5c1, so a wait longer than `MAX_FLOOD_SLEEP` stops
the run and prints the ids still owed. A pilot that hangs overnight is not graceful.

`data/raw/**` is opened read-only. Verify it with `shasum -c results/raw_v1_baseline.sha256`
before and after — `data/` is gitignored, so `git status` proves nothing in either direction.

    python3.11 scripts/fetch_atb_media_5c1.py --dry-run
    python3.11 scripts/fetch_atb_media_5c1.py
"""

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import fetch_post_media as pattern  # noqa: E402
import yield_screen_5c1 as screen  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

HANDLE = "@atb_market_official"
CENSUS = REPO_ROOT / "results" / "image_census_5c1.json"
MEDIA = REPO_ROOT / "data" / "annotation" / "captions_5c1" / "posts_media"
MANIFEST = REPO_ROOT / "results" / "post_media_5c1.json"

MAX_FLOOD_SLEEP = 300
"""Seconds of FloodWait this will sit through before stopping and reporting what is left. The
account behind `marketpulse.session` has met a 20-hour wall on this phase; sleeping through one
inside a pilot would turn a $0.01 experiment into an overnight job nobody is watching."""


def population(census: dict, handle: str) -> list[int]:
    """The msg_ids the census counted as unreadable, straight from the record."""
    row = next((row for row in census["sources"] if row["handle"] == handle), None)
    if row is None:
        raise SystemExit(f"{screen.rel(CENSUS)} has no row for {handle}")
    ids = row["uncaptioned_msg_ids"]
    if len(ids) != row["states"]["no_text_and_no_caption"]:
        raise SystemExit(
            f"{handle}: the census counts {row['states']['no_text_and_no_caption']} unreadable"
            f" posts and names {len(ids)} of them — the population is not the one that was priced"
        )
    return sorted(ids)


async def fetch(handle: str, targets: dict, directory: Path) -> tuple[dict, list[int]]:
    """Every wanted post of one channel, album items included, with a bounded FloodWait."""
    from telethon.errors import FloodWaitError

    from market_pulse.telegram_client import build_client

    client = build_client()
    await client.connect()
    out, owed = {}, []
    try:
        if not await client.is_user_authorized():
            raise SystemExit(
                "No Telegram session — these images cannot be fetched without one. Run"
                " `python3.11 scripts/tg_login.py` and start this again."
            )
        entity = await client.get_entity(handle)
        pending = sorted(targets, key=lambda key: key[1])
        for position, key in enumerate(pending):
            record = targets[key]
            try:
                messages = await client.get_messages(entity, ids=pattern.album_ids(record))
            except FloodWaitError as exc:
                if exc.seconds > MAX_FLOOD_SLEEP:
                    owed = [k[1] for k in pending[position:]]
                    print(
                        f"  FloodWait {exc.seconds}s > {MAX_FLOOD_SLEEP}s cap — stopping with"
                        f" {len(owed)} post(s) still owed: {owed}",
                        flush=True,
                    )
                    break
                print(f"  FloodWait: sleeping {exc.seconds}s", flush=True)
                await asyncio.sleep(exc.seconds)
                messages = await client.get_messages(entity, ids=pattern.album_ids(record))
            found = [message for message in messages if message is not None]
            if record.get("grouped_id") is not None:
                found = [msg for msg in found if msg.grouped_id == record["grouped_id"]]
            items = []
            for message in found:
                items.append(await pattern.download(client, handle, message, directory))
                await asyncio.sleep(pattern.PAUSE)
            poll = next((question for msg in found if (question := pattern.poll_of(msg))), None)
            out[key] = {"items": items, "poll": poll}
            got = sum(1 for item in items if "file" in item)
            print(
                f"  {handle}:{key[1]:<7} {got}/{len(items)} image(s){'  + poll' if poll else ''}",
                flush=True,
            )
    finally:
        await client.disconnect()
    return out, owed


def entries_for(targets: dict, posts: dict, fetched: dict) -> dict:
    """One entry per wanted post, in the shape `caption_posts.population` reads."""
    entries = {}
    for key in sorted(targets, key=lambda key: key[1]):
        record = posts[key]
        result = fetched.get(key, {"items": [], "missing": "not fetched"})
        entries[f"{key[0]}:{key[1]}"] = {
            "channel": key[0],
            "msg_id": key[1],
            "date": record["date"],
            "post_has_text": bool(record["text"].strip()),
            "has_media": record["has_media"],
            "album": record.get("grouped_id") is not None,
            "images": [item for item in result["items"] if "file" in item],
            "poll": result.get("poll"),
            "missing": [item for item in result["items"] if "file" not in item]
            + ([{"reason": result["missing"]}] if result.get("missing") else []),
        }
    return entries


def main(argv: list[str] | None = None, runner=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--media", type=Path, default=MEDIA)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--census", type=Path, default=CENSUS)
    parser.add_argument("--posts", type=Path, default=screen.POSTS)
    parser.add_argument("--dry-run", action="store_true", help="the population, then stop")
    args = parser.parse_args(argv)

    census = json.loads(args.census.read_text(encoding="utf-8"))
    wanted = population(census, HANDLE)
    posts = pattern.posts_index(args.posts)
    targets = {}
    for msg_id in wanted:
        key = (HANDLE, msg_id)
        if key not in posts:
            raise SystemExit(f"{HANDLE}:{msg_id} is named by the census and is not in the store")
        if posts[key]["text"].strip():
            raise SystemExit(f"{HANDLE}:{msg_id} has text of its own — it is not a silent post")
        targets[key] = posts[key]

    albums = sum(1 for record in targets.values() if record.get("grouped_id") is not None)
    print(
        f"{len(targets)} silent posts of {HANDLE}, named by {screen.rel(args.census)}"
        f"\n  {albums} are albums (up to {pattern.ALBUM_SCAN} items each are scanned)"
        f"\n  {sum(1 for r in targets.values() if not r['has_media'])} carry no media at all"
    )
    if args.dry_run:
        for (_, msg_id), record in sorted(targets.items()):
            print(f"  {msg_id:<8}{record['date'][:10]}  media={record['has_media']}")
        return 0

    args.media.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat(timespec="seconds")
    run = runner or (lambda: asyncio.run(fetch(HANDLE, targets, args.media)))
    fetched, owed = run()
    entries = entries_for(targets, posts, fetched)

    with_image = [name for name, entry in entries.items() if entry["images"]]
    blind = sorted(
        name for name, entry in entries.items() if not entry["images"] and not entry["poll"]
    )
    manifest = {
        "generated_at": started,
        "phase": "5c1 — the ATB caption pilot",
        "contract": "docs/PROMPT-5c1-captions-pilot.md step 2",
        "channel": HANDLE,
        "population": {
            "source": screen.rel(args.census),
            "asked": len(targets),
            "msg_ids": wanted,
            "note": (
                "the ids the census counted as no_text_and_no_caption in this channel's screen"
                " window — read from the record, never re-derived here"
            ),
        },
        "media": screen.rel(args.media),
        "posts": len(entries),
        "images": sum(len(entry["images"]) for entry in entries.values()),
        "posts_with_an_image": len(with_image),
        "posts_without_an_image": sorted(set(entries) - set(with_image)),
        "polls": sorted(name for name, entry in entries.items() if entry["poll"]),
        "media_only_posts": sorted(entries),
        "media_only_with_nothing_to_say": blind,
        "still_owed": owed,
        "flood_wait": {
            "max_sleep_seconds": MAX_FLOOD_SLEEP,
            "note": (
                "a longer wall stops the run and leaves the owed ids in `still_owed` rather than"
                " sleeping through it; this account has met a 20-hour wall on this phase"
            ),
        },
        "raw_store": "read-only; verify with `shasum -c results/raw_v1_baseline.sha256`",
        "entries": entries,
        "git": git_state(args.manifest),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"\n{len(entries)} posts · {manifest['images']} images ·"
        f" {len(with_image)} with at least one · {len(blind)} with nothing to say"
        f"\nwrote {screen.rel(args.manifest)}"
    )
    return 1 if owed else 0


if __name__ == "__main__":
    raise SystemExit(main())
