#!/usr/bin/env python3
"""The images of the parent posts the operator and the model are about to judge (4.5g2).

The 4.5g quiz failed at 11/20 and the operator named the reason: the rows in that class hang
under posts that are **images**, and the MVP collected text only. Judging them blind is a guess
for the human and for the model alike, so the media of exactly the posts in play is fetched here
— the parents of the 97 emptied rows, of the 424 media-only up-label rows, and of the 14
unreadable rows the 4.5f micro-pack holds.

Nothing about the corpus changes. `data/raw/posts/*.jsonl` is immutable and is only read; the
images land beside the sitting pack, and what could not be fetched is listed by name rather than
guessed at from a thumbnail.

Albums are the reason this is not one message per post: `raw_store.collapse_albums` stores an
album under the id of its **first** item, and the informative image is often not that one. So a
post with a `grouped_id` has its neighbours scanned and every item of the album downloaded.

    python3.11 scripts/tg_login.py            # once, if the session has expired
    python3.11 scripts/fetch_post_media.py --dry-run
    python3.11 scripts/fetch_post_media.py

Writes `data/annotation/sitting_45g/posts_media/<channel>_<msg_id>.jpg` (gitignored, like every
pack file) and the manifest `results/post_media_45g2.json`.
"""

import argparse
import asyncio
import csv
import json
import sys
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from relabel_emptied import DROP, RELABEL_RECORD, population  # noqa: E402

MEDIA = REPO_ROOT / "data" / "annotation" / "sitting_45g" / "posts_media"
MANIFEST = REPO_ROOT / "results" / "post_media_45g2.json"
BATCH = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g.jsonl"
PRECHECK = REPO_ROOT / "results" / "precheck_45g.json"
MICRO_MANIFEST = REPO_ROOT / "results" / "calib_45e_micro_manifest.json"
POSTS = REPO_ROOT / "data" / "raw" / "posts"

ALBUM_SCAN = 10
"""How far past an album's first item to look. Telegram numbers an album's messages
consecutively and caps it at ten, so this is the whole album and never the next post."""

PAUSE = 0.4  # between downloads, the same courtesy the backfill pays between threads
FLOOD_RETRIES = 3


def posts_index(directory: Path) -> dict[tuple[str, int], dict]:
    """The whole stored post record per (channel, msg_id) — `has_media` and `grouped_id` too."""
    found = {}
    for path in sorted(directory.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                record = json.loads(line)
                found[(record["channel"], record["msg_id"])] = record
    if not found:
        raise SystemExit(f"{relabel.rel(directory)}: no stored posts, so no parent to fetch")
    return found


def wanted(labelled: dict, emptied: list[dict], batch: list[dict], micro: list[dict]) -> dict:
    """Every parent in play, and which of the three groups asked for it."""
    groups = {
        "emptied_97": [labelled[row["id"]] for row in emptied],
        "uplabel_media_only": batch,
        "unreadable_14": [labelled[row["id"]] for row in micro],
    }
    asked: dict[tuple[str, int], set[str]] = {}
    for name, rows in groups.items():
        for row in rows:
            asked.setdefault((row["channel"], row["parent_msg_id"]), set()).add(name)
    return {key: sorted(names) for key, names in asked.items()}


def media_only(batch: list[dict], posts: dict) -> list[dict]:
    """The up-label rows whose parent has no text of its own — the class captions are for."""
    return [
        row for row in batch if not posts[(row["channel"], row["parent_msg_id"])]["text"].strip()
    ]


def stem(channel: str, msg_id: int) -> str:
    return f"{channel.lstrip('@')}_{msg_id}"


def album_ids(record: dict) -> list[int]:
    """The ids to ask Telegram for. One, unless the stored post is a collapsed album."""
    first = record["msg_id"]
    if record.get("grouped_id") is None:
        return [first]
    return list(range(first, first + ALBUM_SCAN))


def unreadable_ids(manifest: Path, root: Path = REPO_ROOT) -> list[dict]:
    sealed = json.loads(manifest.read_text(encoding="utf-8"))
    path = root / sealed["pack"]
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def poll_of(message) -> dict | None:
    """A poll's question and options — the post's own words, in a field nothing here read.

    16 of the 41 media-only parents are polls, the two the quiz's varenyky family hangs under
    among them. `raw_store.post_record` stores `message.raw_text`, which a poll leaves empty, so
    the corpus records these posts as having nothing to say while Telegram has been carrying the
    question all along. Reading it is not a guess at an image and it is not new collection: it is
    the message this run already fetched, read one field further.
    """
    media = getattr(message, "poll", None)
    if media is None:
        return None
    poll = getattr(media, "poll", media)
    question = getattr(poll.question, "text", poll.question)
    return {
        "question": question,
        "options": [getattr(answer.text, "text", answer.text) for answer in poll.answers],
    }


async def download(client, handle: str, message, directory: Path) -> dict:
    """One message's image on disk, or a named reason there is none."""
    from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

    kind = type(message.media).__name__ if message.media else None
    if isinstance(message.media, MessageMediaDocument):
        mime = getattr(message.media.document, "mime_type", "") or ""
        if not mime.startswith("image/"):
            return {"msg_id": message.id, "missing": f"media is {mime or kind}, not an image"}
    elif not isinstance(message.media, MessageMediaPhoto):
        return {"msg_id": message.id, "missing": f"media is {kind or 'absent'}"}
    target = directory / f"{stem(handle, message.id)}.jpg"
    written = await client.download_media(message, file=str(target))
    if written is None:
        return {"msg_id": message.id, "missing": "telegram returned no file"}
    path = Path(written)
    return {
        "msg_id": message.id,
        "file": relabel.rel(path),
        "sha256": sha256(path.read_bytes()).hexdigest(),
        "bytes": path.stat().st_size,
    }


async def fetch_channel(client, handle: str, targets: dict, directory: Path) -> dict:
    """Every wanted post of one channel, its album items included."""
    from telethon.errors import FloodWaitError

    entity = await client.get_entity(handle)
    out = {}
    for key, record in sorted(targets.items(), key=lambda item: item[0][1]):
        ids = album_ids(record)
        for attempt in range(FLOOD_RETRIES):
            try:
                messages = await client.get_messages(entity, ids=ids)
                break
            except FloodWaitError as exc:
                print(f"  FloodWait: sleeping {exc.seconds}s", flush=True)
                await asyncio.sleep(exc.seconds)
        else:
            out[key] = {"items": [], "missing": "floodwait"}
            continue
        found = [msg for msg in messages if msg is not None]
        # an album is exactly the run of neighbours sharing the stored grouped_id
        if record.get("grouped_id") is not None:
            found = [msg for msg in found if msg.grouped_id == record["grouped_id"]]
        items = []
        for message in found:
            items.append(await download(client, handle, message, directory))
            await asyncio.sleep(PAUSE)
        poll = next((found_poll for msg in found if (found_poll := poll_of(msg))), None)
        out[key] = {"items": items, "poll": poll}
        got = sum(1 for item in items if "file" in item)
        print(
            f"  {handle}:{key[1]:<7} {got}/{len(items)} image(s){'  + poll' if poll else ''}",
            flush=True,
        )
    return out


def report(targets: dict, posts: dict, fetched: dict) -> dict:
    """One entry per wanted post: what was asked for, what landed, what did not."""
    entries = {}
    for key, groups in sorted(targets.items()):
        record = posts[key]
        result = fetched.get(key, {"items": [], "missing": "not fetched"})
        images = [item for item in result["items"] if "file" in item]
        entries[f"{key[0]}:{key[1]}"] = {
            "channel": key[0],
            "msg_id": key[1],
            "asked_by": groups,
            "post_has_text": bool(record["text"].strip()),
            "has_media": record["has_media"],
            "album": record.get("grouped_id") is not None,
            "images": images,
            "poll": result.get("poll"),
            "missing": [item for item in result["items"] if "file" not in item]
            + ([{"reason": result["missing"]}] if result.get("missing") else []),
        }
    return entries


async def run(targets: dict, directory: Path) -> dict:
    from market_pulse.telegram_client import build_client

    client = build_client()
    await client.connect()
    try:
        if not await client.is_user_authorized():
            raise SystemExit(
                "No Telegram session — the media of these posts cannot be fetched without one."
                " Run `python3.11 scripts/tg_login.py` and start this again. Stopping rather than"
                " continuing: a sitting built without the images is the sitting that failed."
            )
        fetched = {}
        for handle in sorted({key[0] for key in targets}):
            mine = {key: record for key, record in targets.items() if key[0] == handle}
            print(f"{handle}: {len(mine)} parent posts", flush=True)
            fetched |= await fetch_channel(client, handle, mine, directory)
        return fetched
    finally:
        await client.disconnect()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--media", type=Path, default=MEDIA)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--batch", type=Path, default=BATCH)
    parser.add_argument("--precheck", type=Path, default=PRECHECK)
    parser.add_argument("--micro-manifest", type=Path, default=MICRO_MANIFEST)
    parser.add_argument("--posts", type=Path, default=POSTS)
    parser.add_argument("--drop", type=Path, default=DROP)
    parser.add_argument("--relabel-record", type=Path, default=RELABEL_RECORD)
    parser.add_argument("--dry-run", action="store_true", help="the population, then stop")
    args = parser.parse_args(argv)

    posts = posts_index(args.posts)
    labelled = {
        row["id"]: row for source in relabel.SOURCES.values() for row in relabel.load(source)[0]
    }
    emptied = population(args.drop, args.relabel_record)
    batch = relabel.load(args.batch)[0]
    media = media_only(batch, posts)
    recorded = json.loads(args.precheck.read_text(encoding="utf-8"))["runs"][-1]["pool"]
    if len(media) != recorded["parent_is_media_only"] or len(batch) != recorded["rows"]:
        raise SystemExit(
            f"{relabel.rel(args.batch)} derives as {len(media)} media-only rows of {len(batch)}"
            f" and {relabel.rel(args.precheck)} recorded"
            f" {recorded['parent_is_media_only']} of {recorded['rows']} — the class captions are"
            " being fetched for is not the class that was prechecked."
        )
    micro = unreadable_ids(args.micro_manifest)
    targets = wanted(labelled, emptied, media, micro)
    missing_from_store = [key for key in targets if key not in posts]
    if missing_from_store:
        raise SystemExit(f"{missing_from_store}: parents that are not in the stored posts")

    print(
        f"{len(targets)} unique parent posts"
        f"\n  {sum(1 for key in targets if not posts[key]['text'].strip())} have no text of their"
        " own — the ones a caption has to speak for"
        f"\n  {sum(1 for key in targets if posts[key]['grouped_id'] is not None)} are albums"
        f"\n  {sum(1 for key in targets if not posts[key]['has_media'])} carry no media at all"
    )
    if args.dry_run:
        for key, groups in sorted(targets.items()):
            print(f"  {key[0]}:{key[1]:<7} {','.join(groups)}")
        return 0

    args.media.mkdir(parents=True, exist_ok=True)
    to_fetch = {key: posts[key] for key in targets if posts[key]["has_media"]}
    fetched = asyncio.run(run(to_fetch, args.media))
    entries = report(targets, posts, fetched)

    images = sum(len(entry["images"]) for entry in entries.values())
    without = sorted(name for name, entry in entries.items() if not entry["images"])
    silent = {name: entry for name, entry in entries.items() if not entry["post_has_text"]}
    blind = sorted(
        name for name, entry in silent.items() if not entry["images"] and not entry["poll"]
    )
    manifest = {
        "media": relabel.rel(args.media),
        "posts": len(entries),
        "images": images,
        "posts_with_an_image": len(entries) - len(without),
        "posts_without_an_image": without,
        "polls": sorted(name for name, entry in entries.items() if entry["poll"]),
        "media_only_posts": sorted(silent),
        "media_only_with_nothing_to_say": blind,
        "media_only_note": (
            "A media-only post is not always a picture: 16 of these are polls, whose question and"
            " options Telegram carries in a field `raw_store.post_record` never read"
            " (`message.raw_text` is empty for a poll). Those are transcribed rather than"
            " captioned — same posts, same fetch, one field further, no vision model involved."
            " What is left in `media_only_with_nothing_to_say` is a video, an audio message and"
            " two giveaways: named here, never guessed at."
        ),
        "sources": {
            "emptied_97": len(emptied),
            "uplabel_media_only": len(media),
            "unreadable_14": len(micro),
        },
        "entries": entries,
        "git": git_state(args.manifest),
        "note": (
            "The parent media of the rows 4.5g2 puts in front of the operator and the model."
            " data/raw/posts/*.jsonl is read-only here; nothing about the corpus changed. A post"
            " whose media could not be fetched is named in `posts_without_an_image` and is"
            " rendered as having no text at all, never as a guess."
        ),
    }
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"\n{images} images for {manifest['posts_with_an_image']} of {len(entries)} posts"
        f"\n  {len(manifest['polls'])} posts are polls and their question was transcribed"
        f"\n  of the {len(silent)} media-only posts, {len(blind)} have neither an image nor a"
        f" poll: {', '.join(blind) or '—'}"
        f"\nwrote {relabel.rel(args.manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
