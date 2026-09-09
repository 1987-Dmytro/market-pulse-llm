#!/usr/bin/env python3
"""The EXACT page count of C2's pinned population ($0, Telegram metadata only).

Clause (a) of the phase's `/goal`. `results/promo_census_c2.json` could only BOUND the pages
(1 022 … 9 653) for one reason, and it is a property of the store rather than of Telegram:
`RawStore.collapse_albums` merges an album into one record and keeps `has_media` as a bool, so the
member count is discarded at write time and no reader can recover it. The gap to the next stored
`msg_id` recovers it for 240 of the 258 posts the media manifests measure — and over-counts on the
other 18, never under — so the store alone yields an upper bound, not the number C2 is priced on.

The number itself is one metadata pass over the SAME window, counting album members instead of
collapsing them. No media is downloaded, nothing is written to the raw store, and the population is
the census's pinned ids — never a date range re-evaluated now (SPEC 3.18 (4)): a re-derived window
would silently widen what C2 pays for by every post published since the census froze.

Three states per pinned post, because a post that has been deleted since 31.08 is not a post with
zero pages: `exact` (the re-read saw it), `unreachable` (it did not — priced at the store's gap
upper bound, never at 0). A page is a PHOTO member; a video, a poll or a document carries no
leaflet page and vision would be billed for nothing.

    python3.11 scripts/promo_pagecount_c2.py --plan   # offline: the pinned population and the bound
    PYTHONPATH=src python3.11 scripts/promo_pagecount_c2.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

CENSUS = REPO_ROOT / "results" / "promo_census_c2.json"
RECORD = REPO_ROOT / "results" / "promo_pagecount_c2.json"
STORES = (REPO_ROOT / "data" / "raw" / "posts", REPO_ROOT / "data" / "raw_r2" / "posts")
REQUEST_PAUSE = 1.0
"""`scripts/collect_r2.py::REQUEST_PAUSE`. The same account, so the same pacing."""


def page_kind(message) -> str:
    """What ONE message contributes to a leaflet: a page, or nothing.

    `post_record` stores `has_media = message.media is not None`, which is true of a video, a poll
    and a PDF alike. Vision is billed per image, so the count has to name the kind rather than
    inherit that bool.
    """
    media = getattr(message, "media", None)
    if media is None:
        return "none"
    if getattr(message, "photo", None) is not None:
        return "photo"
    if getattr(message, "video", None) is not None:
        return "video"
    if getattr(message, "poll", None) is not None:
        return "poll"
    if getattr(message, "document", None) is not None:
        return "document"
    return "other"


def fold(messages: list) -> dict[int, dict]:
    """Album members folded onto the msg_id the store keyed the album by.

    `collapse_albums` keeps `min(msg_id)` for a group, so that is the join key back to the census's
    pinned ids. An ungrouped message is its own group of one.
    """
    groups: dict[object, dict] = {}
    for message in messages:
        key = message.grouped_id if message.grouped_id is not None else ("solo", message.id)
        row = groups.setdefault(key, {"msg_id": message.id, "pages": 0, "kinds": {}})
        row["msg_id"] = min(row["msg_id"], message.id)
        kind = page_kind(message)
        row["kinds"][kind] = row["kinds"].get(kind, 0) + 1
        if kind == "photo":
            row["pages"] += 1
    return {row["msg_id"]: row for row in groups.values()}


def store_ids(channel: str) -> list[int]:
    """Every msg_id stored for one channel, across the archive and the live root, sorted."""
    ids: set[int] = set()
    for root in STORES:
        for path in root.glob("*.jsonl"):
            with path.open(encoding="utf-8") as handle:
                first = handle.readline()
                if not first or json.loads(first)["channel"] != channel:
                    continue
                ids.add(int(json.loads(first)["msg_id"]))
                ids.update(int(json.loads(line)["msg_id"]) for line in handle if line.strip())
    return sorted(ids)


def gap_bound(ids: list[int], msg_id: int) -> int:
    """The store's own upper bound on one post's pages: the distance to the next stored id.

    An album occupies consecutive message ids and the store kept only the lowest, so the distance
    covers exactly the members it dropped — plus anything else deleted or filtered in between,
    which is why it can only over-count. Measured against the manifests: exact on 240 of 258.
    """
    after = [other for other in ids if other > msg_id]
    return max(1, after[0] - msg_id) if after else 1


def channel_rows(census: dict) -> list[dict]:
    """The pinned population per channel, with the store's bound for every row."""
    rows = []
    for entry in census["channels"]:
        pinned = [int(one) for one in entry["media_msg_ids"]]
        if not pinned:
            continue
        ids = store_ids(entry["channel"])
        rows.append(
            {
                "channel": entry["channel"],
                "source_id": entry["source_id"],
                "pinned": pinned,
                "bound": {msg_id: gap_bound(ids, msg_id) for msg_id in pinned},
            }
        )
    return rows


def price(row: dict, folded: dict[int, dict]) -> dict:
    """One channel's exact pages, and the bound standing in for what the re-read could not see."""
    exact = [msg_id for msg_id in row["pinned"] if msg_id in folded]
    unreachable = [msg_id for msg_id in row["pinned"] if msg_id not in folded]
    kinds: dict[str, int] = {}
    for msg_id in exact:
        for kind, n in folded[msg_id]["kinds"].items():
            kinds[kind] = kinds.get(kind, 0) + n
    pages_exact = sum(folded[msg_id]["pages"] for msg_id in exact)
    pages_unreachable = sum(row["bound"][msg_id] for msg_id in unreachable)
    return {
        "channel": row["channel"],
        "source_id": row["source_id"],
        "pinned_media_posts": len(row["pinned"]),
        "rows_exact": len(exact),
        "rows_unreachable": len(unreachable),
        "unreachable_msg_ids": [str(one) for one in sorted(unreachable)],
        "pages_exact": pages_exact,
        "pages_unreachable_bound": pages_unreachable,
        "pages": pages_exact + pages_unreachable,
        "pages_store_upper_bound": sum(row["bound"].values()),
        "kinds": kinds,
    }


def totals(priced: list[dict]) -> dict:
    keys = (
        "pinned_media_posts",
        "rows_exact",
        "rows_unreachable",
        "pages_exact",
        "pages_unreachable_bound",
        "pages",
        "pages_store_upper_bound",
    )
    out = {key: sum(row[key] for row in priced) for key in keys}
    kinds: dict[str, int] = {}
    for row in priced:
        for kind, n in row["kinds"].items():
            kinds[kind] = kinds.get(kind, 0) + n
    out["kinds"] = kinds
    return out


def render(priced: list[dict]) -> str:
    head = (
        f"{'channel':<24}{'posts':>7}{'exact':>7}{'unreach':>8}"
        f"{'pages':>7}{'bound':>7}{'storeUB':>9}"
    )
    lines = [head, "-" * len(head)]
    for row in sorted(priced, key=lambda one: -one["pages"]):
        lines.append(
            f"{row['channel']:<24}{row['pinned_media_posts']:>7}{row['rows_exact']:>7}"
            f"{row['rows_unreachable']:>8}{row['pages_exact']:>7}"
            f"{row['pages_unreachable_bound']:>7}{row['pages_store_upper_bound']:>9}"
        )
    return "\n".join(lines)


async def reread(rows: list[dict], since, anchor) -> dict[str, dict[int, dict]]:
    """One metadata pass per channel over the census's window. Serial, paced, read-only."""
    from collect_r2 import resolvable
    from market_pulse.telegram_client import build_client

    client = build_client()
    await client.start()
    out: dict[str, dict[int, dict]] = {}
    try:
        for row in rows:
            handle = row["channel"]
            # `collect_r2.resolvable`, not a second spelling of it: the registry's handle for a
            # private channel IS its invite hash, and Telethon resolves `t.me/+hash` but not the
            # bare `+hash` (449cab1). That fix reached the collector and not this reader, which is
            # why c3's first re-read died on `Cannot find any entity corresponding to
            # "+Ejz6ubzm21IyMTQy"`. The resolve ARGUMENT only — `handle` stays the store key.
            entity = await client.get_entity(resolvable(handle))
            seen = []
            async for message in client.iter_messages(entity, wait_time=REQUEST_PAUSE):
                if message.action is not None:
                    continue
                if message.date < since:
                    break
                if message.date >= anchor:
                    continue
                seen.append(message)
            out[handle] = fold(seen)
            print(
                f"  {handle:<24} {len(seen):>5} messages → {len(out[handle]):>5} posts", flush=True
            )
    finally:
        await client.disconnect()
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true", help="offline: the population and the bound")
    parser.add_argument("--census", type=Path, default=CENSUS, help="the census to price")
    parser.add_argument("--out", type=Path, default=RECORD, help="where the page count lands")
    args = parser.parse_args(argv)
    record_path = args.out

    census = json.loads(args.census.read_text(encoding="utf-8"))
    rows = channel_rows(census)
    window = census["window"]
    print(
        f"population: {census['selection']['leaflet_page']['posts']} media posts,"
        f" ids_sha256 {census['selection']['ids_sha256'][:16]}"
        f" · window {window['since']} … {window['anchor']}"
    )

    if args.plan:
        priced = [price(row, {}) for row in rows]
        print(render(priced))
        print(f"store upper bound: {totals(priced)['pages_store_upper_bound']} pages")
        return 0

    since = datetime.fromisoformat(window["since"]).replace(tzinfo=UTC)
    anchor = datetime.fromisoformat(window["anchor"]).replace(tzinfo=UTC)
    folded = asyncio.run(reread(rows, since, anchor))
    priced = [price(row, folded.get(row["channel"], {})) for row in rows]
    record = {
        "contract": "docs/PHASE-promo-pulse-1.md §8 clause (a) — the exact page count ($0)",
        "method": "Telegram metadata re-read of the census's pinned ids; a page is a photo member"
        " of the post's album; an unreachable pinned post is priced at the store's gap bound",
        "window": window,
        "selection": {
            "ids_sha256": census["selection"]["ids_sha256"],
            "posts": census["selection"]["leaflet_page"]["posts"],
        },
        "channels": sorted(priced, key=lambda one: one["channel"]),
        "totals": totals(priced),
    }
    record_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(render(priced))
    where = (
        record_path.relative_to(REPO_ROOT)
        if record_path.is_relative_to(REPO_ROOT)
        else record_path
    )
    print(f"\n{where} — {record['totals']['pages']} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
