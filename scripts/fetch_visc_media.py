#!/usr/bin/env python3
"""The images of every silent post the caption pilot has NOT already bought. ($0, network.)

vis-b captioned @atb_market_official's 19. This fetches the rest of what
`results/image_census_5c1.json` counted as `no_text_and_no_caption` — 25 channels — so that
vis-c can caption them and the yield screen can be re-run with the pictures read.

`scripts/fetch_atb_media_5c1.py` did this for one channel; the parts it borrowed from
`fetch_post_media.py` are borrowed here too rather than copied (`album_ids`, `download`,
`poll_of`), and its one departure is kept: a FloodWait longer than `MAX_FLOOD_SLEEP` STOPS the
run and names the posts still owed. This account lost 20 hours to one such wall in phase 5c1.

**One client on `marketpulse.session`, always.** Telethon writes that file; a second client
against it corrupts the session, so the whole 25-channel sweep runs inside one connect.

Three states, and a post is in exactly one:

  fetchable  at least one image landed (or a poll question, which is text Telegram already had)
  blind      nothing can speak for it — no media in the store, or the media is gone, expired or
             not an image. COUNTED and reported; it is a fact about the corpus.
  owed       the run stopped on a FloodWait before asking. NOT blind: that would file a transport
             failure as a fact about the data and put it in the screen's denominator.

    python3.11 scripts/fetch_visc_media.py --dry-run
    python3.11 scripts/fetch_visc_media.py
    python3.11 scripts/fetch_visc_media.py --only-channels @maudau --manifest results/x.json
"""

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

import fetch_atb_media_5c1 as atb  # noqa: E402
import fetch_post_media as pattern  # noqa: E402
import yield_screen_5c1 as screen  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

ALREADY_BOUGHT = "@atb_market_official"
"""vis-b's 19. `results/captions_gm4_atb19.json` is a paid record and is not re-bought."""

CENSUS = REPO_ROOT / "results" / "image_census_5c1.json"
MEDIA = REPO_ROOT / "data" / "annotation" / "captions_5c1" / "posts_media"
MANIFEST = REPO_ROOT / "results" / "post_media_visc.json"

MAX_FLOOD_SLEEP = atb.MAX_FLOOD_SLEEP


def population(census: dict, skip: str = ALREADY_BOUGHT) -> dict[str, list[int]]:
    """Every channel's unreadable msg_ids, straight from the census, minus the bought channel.

    The census named the ids and is committed; re-deriving the list here could quietly buy
    captions for a different population than the one the screen refused over.

    `uncaptioned_msg_ids` names only the posts that HAVE media — the census's own
    `uncaptioned_without_media` counts the rest and never names them, so they cannot be asked
    for and are blind before a request (see :func:`unnamed_without_media`). A check against
    `no_text_and_no_caption` would therefore fire on four honest channels.
    """
    wanted = {}
    for row in census["sources"]:
        if row["handle"] == skip or not row["uncaptioned_msg_ids"]:
            continue
        ids = sorted(row["uncaptioned_msg_ids"])
        if len(ids) != row["uncaptioned_with_media"]:
            raise SystemExit(
                f"{row['handle']}: the census counts {row['uncaptioned_with_media']} unreadable"
                f" posts with media and names {len(ids)} of them — the population is not the"
                " one that was counted"
            )
        wanted[row["handle"]] = ids
    return wanted


def unnamed_without_media(census: dict, skip: str = ALREADY_BOUGHT) -> dict[str, int]:
    """Unreadable posts the census counted and did NOT name, because they carry no media.

    They are blind by construction and are reported so the manifest's arithmetic closes on the
    census's whole `no_text_and_no_caption` population rather than on the fetchable part of it.
    """
    return {
        row["handle"]: row["uncaptioned_without_media"]
        for row in census["sources"]
        if row["handle"] != skip and row["uncaptioned_without_media"]
    }


def targets_for(wanted: dict[str, list[int]], posts: dict) -> dict:
    """(channel, msg_id) → the stored post record, refusing anything that is not silent."""
    targets = {}
    for handle, ids in wanted.items():
        for msg_id in ids:
            key = (handle, msg_id)
            if key not in posts:
                raise SystemExit(
                    f"{handle}:{msg_id} is named by the census and is not in the store"
                )
            if posts[key]["text"].strip():
                raise SystemExit(f"{handle}:{msg_id} has text of its own — it is not a silent post")
            targets[key] = posts[key]
    return targets


async def fetch(targets: dict, directory: Path) -> tuple[dict, list[str]]:
    """Every wanted post of every channel, on ONE client, with a bounded FloodWait."""
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
        pending = sorted(targets, key=lambda key: (key[0], key[1]))
        entities, position = {}, 0
        while position < len(pending):
            key = pending[position]
            handle, record = key[0], targets[key]
            try:
                if handle not in entities:
                    entities[handle] = await client.get_entity(handle)
                    print(
                        f"{handle}: {sum(1 for k in pending if k[0] == handle)} posts", flush=True
                    )
                messages = await client.get_messages(
                    entities[handle], ids=pattern.album_ids(record)
                )
            except FloodWaitError as exc:
                if exc.seconds > MAX_FLOOD_SLEEP:
                    owed = [f"{k[0]}:{k[1]}" for k in pending[position:]]
                    print(
                        f"  FloodWait {exc.seconds}s > {MAX_FLOOD_SLEEP}s cap — stopping with"
                        f" {len(owed)} post(s) still owed",
                        flush=True,
                    )
                    break
                print(f"  FloodWait: sleeping {exc.seconds}s", flush=True)
                await asyncio.sleep(exc.seconds)
                continue  # the same post is retried, and the cap still applies next time
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
            position += 1
    finally:
        await client.disconnect()
    return out, owed


def buckets(entries: dict, owed: list[str]) -> dict:
    """Every post in exactly one state, and the arithmetic that proves it."""
    owed_set = set(owed)
    fetchable = sorted(
        name for name, e in entries.items() if name not in owed_set and (e["images"] or e["poll"])
    )
    blind = sorted(
        name
        for name, e in entries.items()
        if name not in owed_set and not e["images"] and not e["poll"]
    )
    assert len(fetchable) + len(blind) + len(owed_set) == len(entries), "a post is in two states"
    return {"fetchable": fetchable, "blind": blind, "owed": sorted(owed_set)}


def blind_reasons(entries: dict, blind: list[str]) -> dict[str, str]:
    """Why each blind post is blind — 'no media in the store' is not 'the media is gone'."""
    reasons = {}
    for name in blind:
        entry = entries[name]
        if not entry["has_media"]:
            reasons[name] = "no media in the store"
        else:
            named = [item.get("missing") or item.get("reason") for item in entry["missing"]]
            reasons[name] = "; ".join(sorted({str(x) for x in named if x})) or "nothing returned"
    return reasons


def main(argv: list[str] | None = None, runner=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--media", type=Path, default=MEDIA)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--census", type=Path, default=CENSUS)
    parser.add_argument("--posts", type=Path, default=screen.POSTS)
    parser.add_argument("--only-channels", nargs="+", default=None, help="these handles only")
    parser.add_argument("--dry-run", action="store_true", help="the population, then stop")
    args = parser.parse_args(argv)

    if args.manifest.exists() and not args.dry_run:
        raise SystemExit(f"{screen.rel(args.manifest)} exists — name a new path, never overwrite")

    census = json.loads(args.census.read_text(encoding="utf-8"))
    wanted = population(census)
    if args.only_channels:
        missing = sorted(set(args.only_channels) - set(wanted))
        if missing:
            raise SystemExit(f"not in the census population: {', '.join(missing)}")
        wanted = {h: ids for h, ids in wanted.items() if h in args.only_channels}
    posts = pattern.posts_index(args.posts)
    targets = targets_for(wanted, posts)

    albums = sum(1 for record in targets.values() if record.get("grouped_id") is not None)
    no_media = sum(1 for record in targets.values() if not record["has_media"])
    print(
        f"{len(targets)} silent posts across {len(wanted)} channels, named by"
        f" {screen.rel(args.census)}"
        f"\n  {albums} are albums (up to {pattern.ALBUM_SCAN} items each are scanned)"
        f"\n  {no_media} carry no media at all — blind before a single request"
    )
    if args.dry_run:
        for handle, ids in sorted(wanted.items()):
            print(f"  {handle:<30}{len(ids):>4}  {ids[:6]}{' …' if len(ids) > 6 else ''}")
        return 0

    args.media.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat(timespec="seconds")
    run = runner or (lambda: asyncio.run(fetch(targets, args.media)))
    fetched, owed = run()
    entries = atb.entries_for(targets, posts, fetched)
    state = buckets(entries, owed)

    images = [item for entry in entries.values() for item in entry["images"]]
    unnamed = unnamed_without_media(census)
    if args.only_channels:
        unnamed = {h: n for h, n in unnamed.items() if h in args.only_channels}
    fetchable_set, blind_set, owed_set = (set(state[key]) for key in ("fetchable", "blind", "owed"))
    by_channel = {}
    for handle in sorted(set(wanted) | set(unnamed)):
        mine = [name for name in entries if name.startswith(f"{handle}:")]
        by_channel[handle] = {
            "asked": len(mine),
            "fetchable": sum(1 for name in mine if name in fetchable_set),
            "blind": sum(1 for name in mine if name in blind_set),
            "owed": sum(1 for name in mine if name in owed_set),
            "blind_unnamed_no_media": unnamed.get(handle, 0),
            "images": sum(len(entries[name]["images"]) for name in mine),
        }
    manifest = {
        "generated_at": started,
        "phase": "5c1 vis-c — the manifest of every silent post not already captioned",
        "contract": "docs/PROMPT-5c1-vis-c.md, the work (1)",
        "channels": sorted(wanted),
        "population": {
            "source": screen.rel(args.census),
            "asked": len(targets),
            "excluded": {ALREADY_BOUGHT: "captioned at vis-b, results/captions_gm4_atb19.json"},
            "msg_ids": {handle: ids for handle, ids in sorted(wanted.items())},
        },
        "media": screen.rel(args.media),
        "posts": len(entries),
        "images": len(images),
        "images_sha256": sha256(
            "".join(sorted(item["sha256"] for item in images)).encode()
        ).hexdigest(),
        "states": {
            **{key: len(value) for key, value in state.items()},
            "blind_unnamed_no_media": sum(unnamed.values()),
        },
        "unreadable_population": len(entries) + sum(unnamed.values()),
        "fetchable": state["fetchable"],
        "blind": state["blind"],
        "blind_reasons": blind_reasons(entries, state["blind"]),
        "blind_unnamed_no_media": unnamed,
        "still_owed": state["owed"],
        "by_channel": by_channel,
        "polls": sorted(name for name, entry in entries.items() if entry["poll"]),
        "flood_wait": {
            "max_sleep_seconds": MAX_FLOOD_SLEEP,
            "note": "a longer wall stops the run and leaves the owed ids in `still_owed` rather"
            " than sleeping through it; this account has met a 20-hour wall on this phase."
            " `still_owed` is NOT `blind` — a transport failure is not a fact about the corpus",
        },
        "raw_store": "read-only; verify with `shasum -c results/raw_v1_baseline.sha256`",
        "entries": entries,
        "git": git_state(args.manifest),
    }
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"\n{screen.rel(args.manifest)}: {len(entries)} posts asked —"
        f" {len(state['fetchable'])} fetchable, {len(state['blind'])} blind,"
        f" {len(state['owed'])} owed; {len(images)} images."
        f" Plus {sum(unnamed.values())} the census counted without media and never named:"
        f" {len(entries) + sum(unnamed.values())} unreadable posts in all"
    )
    return 0 if not state["owed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
