#!/usr/bin/env python3
"""Phase-5a: what the 815 text-less stored posts actually are, and the poll text beside them.

`raw_store.post_record` stores `message.raw_text`, which a poll leaves empty, so a poll is
recorded storewide as a post with nothing to say. 4.5g2 measured that on one sitting pack —
16 of 41 media-only parents of @VARUS_channel were polls — and deferred the storewide count
to the Phase 5 contract (STATUS «Отложено»: `message.poll`, медиа, розыгрыши).

This is that count, over every stored post, plus the transcripts themselves.

**The poll payload is not in the store.** A v1 post record has ten keys and none of them is a
poll; `results/post_media_45g2.json` got its 16 from a live fetch, not from bytes on disk. So
the census re-reads the empty-text ids from Telegram — the same shape `scripts/fetch_comments_v2.py`
used to backfill `reply_to_msg_id` in 4.5g5: fetch, then write a derived file BESIDE v1.
`data/raw/posts/*.jsonl` is opened read-only and its bytes never change.

The transcript format is not invented here: `caption_posts.poll_caption` writes it and
`prompts.POST_SURROGATE["poll"]` renders it, both since 4.5g2. The sidecar is written in the
record shape `parents.load_captions` already reads, so nothing downstream needs a second reader.

    PYTHONPATH=src python3 scripts/poll_census.py --plan          # the population, no API
    PYTHONPATH=src python3 scripts/poll_census.py --limit 20      # a smoke over 20 ids
    PYTHONPATH=src python3 scripts/poll_census.py

Writes `data/raw/post_polls.jsonl` and `results/poll_census_5a.json`. $0 — the Telegram API is
free and no model is called.
"""

import argparse
import asyncio
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from caption_posts import poll_caption  # noqa: E402
from fetch_post_media import poll_of  # noqa: E402
from telethon.errors import FloodWaitError  # noqa: E402

from market_pulse.telegram_client import build_client  # noqa: E402

POSTS = REPO_ROOT / "data" / "raw" / "posts"
SIDECAR = REPO_ROOT / "data" / "raw" / "post_polls.jsonl"
RECORD = REPO_ROOT / "results" / "poll_census_5a.json"
CAPTIONS_45G2 = REPO_ROOT / "data" / "annotation" / "post_captions.jsonl"

BATCH = 100  # ids per get_messages call — Telegram's own limit for an id list
PAUSE = 1.0  # between batches, the pacing scripts/backfill.py pays between requests
FLOOD_RETRIES = 3

SURROGATE_BUILT = ("poll",)
"""Which kinds this run turns into text. Giveaways, video and voice are counted and named,
and that is all: `docs/PROMPT-5a.md` builds no third surrogate in 5a."""


def media_kind(message) -> str:
    """What one message carries, in one word.

    Read off the media class name, which is what `fetch_post_media.download` already keys on:
    a `MessageMediaDocument` is a video, a voice message or a file depending on its attributes,
    and lumping the three together would answer the question 5a is asking with "media".
    """
    media = getattr(message, "media", None)
    if media is None:
        return "no_media"
    name = type(media).__name__
    if name == "MessageMediaPoll":
        return "poll"
    if name in ("MessageMediaGiveaway", "MessageMediaGiveawayResults"):
        return "giveaway"
    if name == "MessageMediaPhoto":
        return "photo"
    if name != "MessageMediaDocument":
        return name
    for attribute in getattr(getattr(media, "document", None), "attributes", None) or []:
        kind = type(attribute).__name__
        if kind == "DocumentAttributeAudio":
            return "voice" if getattr(attribute, "voice", False) else "audio"
        if kind == "DocumentAttributeVideo":
            return "video"
    return "document"


def stored_posts(directory: Path) -> list[dict]:
    """Every stored post record. Read-only: this script never writes into the v1 store."""
    records = []
    for path in sorted(directory.glob("*.jsonl")):
        records += [
            json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line
        ]
    if not records:
        raise SystemExit(f"{relabel.rel(directory)}: no stored posts, so nothing to census")
    return records


def population(records: list[dict]) -> dict[str, list[int]]:
    """The census population: the ids stored with empty text, per channel.

    Empty *text*, not "media-only": the two differ, and the question the contract asks is
    about what the corpus records as having nothing to say.
    """
    empty: dict[str, list[int]] = {}
    for record in records:
        if not (record.get("text") or "").strip():
            empty.setdefault(record["channel"], []).append(record["msg_id"])
    return {channel: sorted(ids) for channel, ids in sorted(empty.items())}


def sidecar_record(channel: str, msg_id: int, poll: dict) -> dict:
    """One poll transcript, in the record shape `parents.load_captions` already reads.

    `kind` is "poll" because `parents.STATE_OF` counts it under that name and
    `prompts.POST_SURROGATE["poll"]` renders it — a second vocabulary here would be a second
    surrogate nothing downstream could tell from the first.
    """
    return {
        "channel": channel,
        "msg_id": msg_id,
        "kind": "poll",
        "caption": poll_caption(poll),
        "model": None,
        "prompt_sha256": None,
        "poll": poll,
        "source": "scripts/poll_census.py",
    }


def census(found: dict[tuple[str, int], str], empty: dict[str, list[int]], total: dict) -> dict:
    """Per channel and total: how many of the text-less posts each kind accounts for."""
    per_channel = {}
    for channel, ids in empty.items():
        kinds = Counter(found.get((channel, msg_id), "not_fetched") for msg_id in ids)
        per_channel[channel] = {
            "posts_stored": total[channel],
            "empty_text": len(ids),
            "polls": kinds.get("poll", 0),
            "poll_share_of_empty": round(kinds.get("poll", 0) / len(ids), 4) if ids else 0.0,
            "kinds": dict(sorted(kinds.items())),
        }
    kinds = Counter()
    for row in per_channel.values():
        kinds.update(row["kinds"])
    empty_total = sum(len(ids) for ids in empty.values())
    return {
        "per_channel": per_channel,
        "total": {
            "posts_stored": sum(total.values()),
            "empty_text": empty_total,
            "polls": kinds.get("poll", 0),
            "poll_share_of_empty": round(kinds.get("poll", 0) / empty_total, 4)
            if empty_total
            else 0.0,
            "kinds": dict(sorted(kinds.items())),
        },
    }


def cross_check(rows: list[dict], captions: Path) -> dict:
    """The 4.5g2 poll rows against this run's — the positive control on the whole fetch.

    16 polls were transcribed in 4.5g2 from a live fetch of one sitting pack. If a storewide
    census that re-reads the same field disagrees with any of them, either the read or the
    format has moved, and every count in this file is suspect. Computed here rather than
    asserted in a report: a claim nobody can recompute is a claim nobody can check.
    """
    if not captions.exists():
        return {"captions": relabel.rel(captions), "found": False}
    mine = {(row["channel"], row["msg_id"]): row["caption"] for row in rows}
    theirs = {
        (record["channel"], record["msg_id"]): record["caption"]
        for record in map(json.loads, captions.read_text(encoding="utf-8").splitlines())
        if record["kind"] == "poll"
    }
    missing = sorted(f"{c}:{m}" for c, m in theirs.keys() - mine.keys())
    differ = sorted(
        f"{c}:{m}" for c, m in theirs.keys() & mine.keys() if theirs[(c, m)] != mine[(c, m)]
    )
    return {
        "captions": relabel.rel(captions),
        "found": True,
        "rows_45g2": len(theirs),
        "also_found_here": len(theirs) - len(missing),
        "transcripts_identical": len(theirs) - len(missing) - len(differ),
        "missing_from_this_run": missing,
        "transcripts_that_differ": differ,
    }


async def read_batch(client, entity, batch: list[int]):
    """One id batch, sleeping out a FloodWait. ``None`` if it never came back.

    `scripts/backfill.py`'s policy — sleep `exc.seconds` and retry, up to FLOOD_RETRIES — rather
    than `scripts/entry_check.py`'s abort-and-keep-what-you-have: this job is bounded (nine
    requests) and a batch that is simply missing would land 100 ids in `not_fetched` and make the
    census look like a measurement with a hole in it.
    """
    for _ in range(FLOOD_RETRIES):
        try:
            return await client.get_messages(entity, ids=batch)
        except FloodWaitError as exc:
            print(f"  FloodWait: sleeping {exc.seconds}s", flush=True)
            await asyncio.sleep(exc.seconds)
    return None


async def fetch_kinds(client, empty: dict[str, list[int]], limit: int | None) -> tuple[dict, dict]:
    """The kind of every text-less post, and the poll payload of the ones that are polls.

    A message Telegram no longer has comes back as ``None`` and is counted as ``gone`` — never
    as "not a poll", which would quietly move a deletion into the denominator's other side.
    """
    kinds: dict[tuple[str, int], str] = {}
    polls: dict[tuple[str, int], dict] = {}
    for channel, ids in empty.items():
        wanted = ids[:limit] if limit else ids
        entity = await client.get_entity(channel)
        print(f"{channel}: {len(wanted)} text-less posts to read", flush=True)
        for start in range(0, len(wanted), BATCH):
            batch = wanted[start : start + BATCH]
            messages = await read_batch(client, entity, batch)
            if messages is None:
                print(f"  {channel}: FloodWait survived {FLOOD_RETRIES} sleeps, batch left unread")
                continue  # the ids stay `not_fetched` in the census, never "not a poll"
            for msg_id, message in zip(batch, messages, strict=True):
                if message is None:
                    kinds[(channel, msg_id)] = "gone"
                    continue
                kinds[(channel, msg_id)] = media_kind(message)
                if found := poll_of(message):
                    polls[(channel, msg_id)] = found
            print(f"  {min(start + BATCH, len(wanted))}/{len(wanted)}", flush=True)
            await asyncio.sleep(PAUSE)
    return kinds, polls


def write_sidecar(path: Path, polls: dict[tuple[str, int], dict]) -> list[dict]:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        sidecar_record(channel, msg_id, poll) for (channel, msg_id), poll in sorted(polls.items())
    ]
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true", help="print the population and stop, no API")
    parser.add_argument("--limit", type=int, help="read at most N ids per channel (smoke)")
    args = parser.parse_args(argv)

    records = stored_posts(POSTS)
    total = Counter(record["channel"] for record in records)
    empty = population(records)
    for channel, ids in empty.items():
        print(f"{channel:<26}{total[channel]:>6} posts, {len(ids):>5} with empty text")
    print(
        f"{'TOTAL':<26}{sum(total.values()):>6} posts, {sum(len(i) for i in empty.values()):>5} with empty text"
    )
    if args.plan:
        return 0

    async def run():
        client = build_client()
        await client.connect()
        try:
            if not await client.is_user_authorized():
                raise SystemExit("No Telegram session. Run: python3 scripts/tg_login.py")
            return await fetch_kinds(client, empty, args.limit)
        finally:
            await client.disconnect()

    kinds, polls = asyncio.run(run())
    sidecar_rows = write_sidecar(SIDECAR, polls)
    counts = census(kinds, empty, total)

    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "population": (
            "every post in data/raw/posts/*.jsonl whose stored `text` is empty, storewide"
        ),
        "limit_per_channel": args.limit,
        "counts": counts,
        "sidecar": {
            "path": relabel.rel(SIDECAR),
            "rows": len(sidecar_rows),
            "cross_check_45g2": cross_check(sidecar_rows, CAPTIONS_45G2),
            "kinds_built": list(SURROGATE_BUILT),
            "format": (
                "caption_posts.poll_caption — the question, then its options one per line;"
                " rendered by prompts.POST_SURROGATE['poll'] and read by parents.load_captions."
            ),
            "note": (
                "Derived, beside the v1 store. data/raw/posts/*.jsonl is opened read-only and"
                " its bytes are unchanged — the same rule 4.5g5 followed for reply_to_msg_id."
            ),
        },
        "not_a_continuation_of_16_of_41": (
            "results/post_media_45g2.json counted 16 polls among the 41 media-only parents of"
            " ONE sitting pack, one channel. This run counts polls among every text-less post"
            " in the store. Different populations: the rates are not comparable and the 4.5g2"
            " number is not superseded by this one."
        ),
        "giveaways_video_voice": (
            "counted and named only — docs/PROMPT-5a.md builds no third surrogate in 5a."
            " `giveaway` here is Telegram's own MessageMediaGiveaway (the premium-subscription"
            " feature), NOT a retail «розыгрыш»: that one is an ordinary image post whose TEXT"
            " announces a draw, so it is not text-less and is outside this population entirely."
            " `voice` is the DocumentAttributeAudio voice flag, not a mime type — an uploaded"
            " audio file and a voice note share audio/ogg and are counted apart."
        ),
        "git": git_state(RECORD),
    }
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print()
    for channel, row in counts["per_channel"].items():
        print(
            f"{channel:<26}{row['polls']:>5} polls of {row['empty_text']:>5} empty  {row['kinds']}"
        )
    total_row = counts["total"]
    print(f"{'TOTAL':<26}{total_row['polls']:>5} polls of {total_row['empty_text']:>5} empty")
    print(f"kinds: {total_row['kinds']}")
    print(
        f"\nwrote {relabel.rel(SIDECAR)} ({len(sidecar_rows)} transcripts) and {relabel.rel(RECORD)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
