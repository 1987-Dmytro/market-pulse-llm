#!/usr/bin/env python3
"""What the 4-week window actually holds, per channel and per leg. ($0, offline, reads only.)

SPEC amendment 3.18 (4): the backlog is scored as a WINDOW of the most recent ~4 weeks, and that
window is "PRE-REGISTERED BY ROW COUNT — computed by a zero-cost census before the paid session,
never as a date range evaluated at run time". This is that census. It decides nothing: it counts
what is on disk, says CANNOT ANSWER where the store cannot answer, and hands the operator the
composition the window ruling is made on.

**One anchor, and it is an argument.** The window is exactly 28 days back from a single timestamp
recorded inside the record, `since <= date < until` — the yield screen's own half-open rule, so the
bar counts exactly 28 days. Nothing here reads the wall clock: a `datetime.now()` anywhere in this
file would make two runs of the same census different artifacts, and the re-run is the census's own
gate. The anchor this record was written with is the corpus's own last day, and the reasoning is
`yield_screen_5c1.window_for`'s: a window ending later than the store buys days that are empty BY
CONSTRUCTION and drops days that hold rows, which measures the collection schedule rather than the
content. It is the operator's to overturn at the STOP — `anchor_sensitivity` prices the two nearest
alternatives, per column, so the choice is visible rather than argued.

    PYTHONPATH=src python3 scripts/census_5c2.py --anchor 2026-08-09T00:00:00+00:00
"""

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import yield_screen_5c1 as screen  # noqa: E402

from market_pulse import loop  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

POSTS = REPO_ROOT / "data" / "raw" / "posts"
COMMENTS = REPO_ROOT / "data" / "raw" / "comments"
CURSOR = REPO_ROOT / "data" / "loop_cursor.json"
POST_MEDIA = REPO_ROOT / "results" / "post_media_5c1.json"
RECORD = REPO_ROOT / "results" / "census_5c2.json"

WINDOW_DAYS = 28
"""SPEC 3.18 (4), four weeks. `yield_screen_5c1.WINDOW_DAYS` is the same number for the same
reason; it is not imported, because that one is the 3.12 relevance floor's window and the two are
free to be ruled apart."""

CANNOT_ANSWER = "CANNOT ANSWER"
"""What a cell says when the raw records cannot answer it — never 0, and never a guess.

A channel with no comments file has not been read; a channel whose comments file exists and holds
nothing in the window has been read and produced nothing. Those are different facts about a
different thing (collection vs content) and a census that printed 0 for both would price a
collection gap as an empty channel."""

ALTERNATIVE_ANCHORS = (
    (
        "2026-08-14T00:00:00+00:00",
        "the last 28 days ending today (2026-08-13) — the literal reading of «the most recent four"
        " weeks», which buys five days no channel has collected into and drops five that hold rows",
    ),
    (
        "2026-07-28T00:00:00+00:00",
        "the last 28 days of the LEAFLET corpus: the 19 pages posts run 2026-07-01…07-23 and this"
        " is the only 28-day window that contains all of them",
    ),
)


def rel(path: Path) -> str:
    return screen.rel(path)


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def producer() -> dict:
    """Which code wrote this, by its own sha — and NOT `git_state`, deliberately.

    Every other record in this repo carries a `git` block, and this one may not: that block holds
    `git status --porcelain`, so the artifact's bytes change when an unrelated file is committed or
    edited. Byte-identity under the same anchor is this record's own gate, and a provenance field
    that moves with the working tree voids it on the first commit after the record was written —
    measured here, not feared: the record was committed, an unrelated commit landed, and the same
    command produced different bytes. The script's sha is the stronger answer anyway; a commit id
    does not say the file was not dirty when it ran.
    """
    return {
        "script": rel(Path(__file__)),
        "sha256": sha256_of(Path(__file__)),
        "why": "no git block: `git status --porcelain` is a fact about the tree, not the measurement",
    }


def window_of(anchor: str) -> dict:
    """The 28 days ending at ``anchor``, as the two ISO strings every count is filtered on."""
    until = datetime.fromisoformat(anchor).astimezone(UTC)
    return {
        "anchor": until.isoformat(),
        "days": WINDOW_DAYS,
        "since": (until - timedelta(days=WINDOW_DAYS)).isoformat(),
        "until": until.isoformat(),
        "rule": "since <= date < until, half-open, so the window is exactly 28 days",
    }


def has_media(post: dict) -> bool:
    """The media-presence definition of `scripts/image_census_5c1.py`, which is the stored flag.

    That census splits its silent posts on `row["has_media"]` and nothing else, and the flag is
    `raw_store.post_record`'s `message.media is not None`, merged across an album by
    `collapse_albums`. Re-deriving it from anything else here would be a second opinion about the
    corpus that nothing holds to the first.
    """
    return bool(post.get("has_media"))


def store_span(rows: list[dict]) -> dict | str:
    dates = sorted(row["date"] for row in rows if row.get("date"))
    return {"first": dates[0], "last": dates[-1]} if dates else CANNOT_ANSWER


def ids_in_window(rows: list[dict], window: dict) -> list[int]:
    return sorted({row["msg_id"] for row in screen.in_window(rows, window)})


def leg(rows: list[dict], window: dict) -> dict:
    """One channel's one record type inside the window.

    The ids are hashed, not listed: 3.18 (4) pre-registers the window BY ROW COUNT, and 5 075
    comment ids would be most of this file. The sha is what makes the count checkable — it pins
    WHICH rows this anchor selected, so a store that has moved under a later re-run is caught
    instead of quietly producing the same total from different rows.
    """
    inside = ids_in_window(rows, window)
    return {
        "in_store": len(rows),
        "in_window": len(inside),
        "ids_sha256": hashlib.sha256(
            ",".join(str(msg_id) for msg_id in inside).encode("utf-8")
        ).hexdigest(),
        "span": store_span(rows),
    }


def unanswered(inside: list[int], watermark: int | None) -> int:
    """How many of these ids a pass would still owe an answer for. `loop.queue_depth`, not a
    reimplementation: the queue the paid session prices is defined in exactly one place."""
    return loop.queue_depth(inside, watermark)


def channel_row(handle: str, source, window: dict, cursor: dict, pages: dict) -> dict:
    """One channel's window: the two legs, the leaflet column, and what the cursor already owes."""
    post_path = POSTS / f"{handle.lstrip('@')}.jsonl"
    comment_path = COMMENTS / f"{handle.lstrip('@')}.jsonl"
    post_rows = screen.load_jsonl(post_path)
    comment_rows = screen.load_jsonl(comment_path)
    posts = leg(post_rows, window) if post_path.exists() else CANNOT_ANSWER
    comments = leg(comment_rows, window) if comment_path.exists() else CANNOT_ANSWER
    state = cursor.get(handle, {})
    row = {
        "handle": handle,
        "source_id": source.id,
        "audience": source.audience,
        "source_type": source.source_type,
        "comments_enabled": source.comments_enabled,
        "watch": source.watch,
        "posts": posts,
        "posts_with_media_in_window": (
            sum(1 for post in screen.in_window(post_rows, window) if has_media(post))
            if posts != CANNOT_ANSWER
            else CANNOT_ANSWER
        ),
        "comments": comments,
        "watermarks": {
            loop.INFERENCE: state.get(loop.INFERENCE),
            loop.LEAFLET: state.get(loop.LEAFLET),
        },
        "leaflet": pages.get(handle, {"posts_with_pages_in_window": 0, "pages_in_window": 0}),
    }
    row["comments_unanswered_in_window"] = (
        unanswered(ids_in_window(comment_rows, window), state.get(loop.INFERENCE))
        if comments != CANNOT_ANSWER
        else CANNOT_ANSWER
    )
    row["pages_unanswered_in_window"] = unanswered(
        row["leaflet"].get("page_ids_in_window", []), state.get(loop.LEAFLET)
    )
    return row


def leaflet_pages(manifest: dict, window: dict) -> dict:
    """Pages DOWNLOADED per channel, inside the window — the operator's coverage number.

    A page has no date of its own: it is one message of its post's album, and it is in the window
    when its POST is. The manifest carries that post's date and the store is asked to confirm it,
    because a manifest whose dates had drifted from the store would move pages in and out of the
    window without any row moving.
    """
    out: dict[str, dict] = {}
    for entry in sorted(manifest["entries"].values(), key=lambda e: (e["channel"], e["msg_id"])):
        found = out.setdefault(
            entry["channel"],
            {
                "posts_with_pages_in_store": 0,
                "pages_in_store": 0,
                "posts_with_pages_in_window": 0,
                "pages_in_window": 0,
                "page_ids_in_window": [],
                "manifest": rel(POST_MEDIA),
            },
        )
        found["posts_with_pages_in_store"] += 1
        found["pages_in_store"] += len(entry["images"])
        if window["since"] <= entry["date"] < window["until"]:
            found["posts_with_pages_in_window"] += 1
            found["pages_in_window"] += len(entry["images"])
            found["page_ids_in_window"] += [image["msg_id"] for image in entry["images"]]
    for found in out.values():
        found["page_ids_in_window"] = sorted(found["page_ids_in_window"])
    return out


def manifest_agrees_with_the_store(manifest: dict) -> dict:
    """Every manifest entry's date, checked against the post it names in the raw store."""
    drift, missing = [], []
    for entry in sorted(manifest["entries"].values(), key=lambda e: (e["channel"], e["msg_id"])):
        handle = entry["channel"]
        rows = {
            row["msg_id"]: row["date"]
            for row in screen.load_jsonl(POSTS / f"{handle.lstrip('@')}.jsonl")
        }
        if entry["msg_id"] not in rows:
            missing.append(f"{handle}:{entry['msg_id']}")
        elif rows[entry["msg_id"]] != entry["date"]:
            drift.append(
                f"{handle}:{entry['msg_id']} manifest {entry['date']} store {rows[entry['msg_id']]}"
            )
    return {
        "checked": len(manifest["entries"]),
        "not_in_the_store": missing,
        "date_drift": drift,
        "agrees": not missing and not drift,
    }


def concentration(rows: list[dict], value) -> list[dict]:
    """Whose window this is, by enumeration: every channel with a row, largest first, cumulative.

    The concentration question is not answered by reading the tail of a printed table — a reader
    who stops at the top five cannot tell 90% from 40%. Every row carries its own share and the
    running total, so «the top N are X%» is read off the file rather than recomputed by hand.
    """
    counted = [(row["handle"], value(row)) for row in rows if isinstance(value(row), int)]
    total = sum(n for _, n in counted)
    out, running = [], 0
    for handle, n in sorted(counted, key=lambda pair: (-pair[1], pair[0])):
        if not n:
            continue
        running += n
        out.append(
            {
                "handle": handle,
                "n": n,
                "share": round(n / total, 4) if total else 0.0,
                "cumulative": running,
                "cumulative_share": round(running / total, 4) if total else 0.0,
            }
        )
    return out


def totals_for(anchor: str, sources: dict, manifest: dict, cursor: dict) -> dict:
    """Every column of the census, summed, for one anchor. The alternatives are this and no more."""
    window = window_of(anchor)
    pages = leaflet_pages(manifest, window)
    rows = [
        channel_row(handle, source, window, cursor, pages) for handle, source in sources.items()
    ]
    return {
        "window": window,
        "posts_in_window": sum(
            row["posts"]["in_window"] for row in rows if row["posts"] != CANNOT_ANSWER
        ),
        "posts_with_media_in_window": sum(
            row["posts_with_media_in_window"]
            for row in rows
            if row["posts_with_media_in_window"] != CANNOT_ANSWER
        ),
        "comments_in_window": sum(
            row["comments"]["in_window"] for row in rows if row["comments"] != CANNOT_ANSWER
        ),
        "comments_unanswered_in_window": sum(
            row["comments_unanswered_in_window"]
            for row in rows
            if row["comments_unanswered_in_window"] != CANNOT_ANSWER
        ),
        "leaflet_pages_in_window": sum(row["leaflet"]["pages_in_window"] for row in rows),
        "leaflet_posts_in_window": sum(
            row["leaflet"]["posts_with_pages_in_window"] for row in rows
        ),
        "channels_with_a_row": sum(
            1
            for row in rows
            if (row["posts"] != CANNOT_ANSWER and row["posts"]["in_window"])
            or (row["comments"] != CANNOT_ANSWER and row["comments"]["in_window"])
        ),
    }


def outside_the_registry() -> dict:
    """Store files for channels the registry does not carry — rows no pass will ever ask about.

    The loop walks `registry.sources` (`run_loop.channels_of`), so a store file with no registry
    entry is invisible to every number the paid session will produce. It is counted here because a
    reader comparing this census against `du -sh data/raw` has to be able to see the difference.
    """
    registry = load_registry(screen.REGISTRY)
    known = {handle for source in registry.sources for handle in source.telegram_channels}
    out = {}
    for kind, root in (("posts", POSTS), ("comments", COMMENTS)):
        files = sorted(
            f"@{path.stem}" for path in root.glob("*.jsonl") if f"@{path.stem}" not in known
        )
        out[kind] = {
            "channels": files,
            "rows": {
                handle: len(screen.load_jsonl(root / f"{handle.lstrip('@')}.jsonl"))
                for handle in files
            },
        }
    return out


def cannot_answer(rows: list[dict]) -> dict:
    """Every cell the store could not answer, split by WHY — the collection gap named separately.

    A channel with `comments_enabled: false` has no discussion group to read: CANNOT ANSWER there
    is structural and permanent. A channel that is comments-enabled, is not a `watch`, and still has
    no file was never collected — that is a gap, and 3.18 (4)'s window is smaller than it looks by
    exactly that much. The contract's DO NOT is explicit that a gap goes in the report and nothing
    is fetched, so it is counted here and left alone.
    """
    no_posts = [row["handle"] for row in rows if row["posts"] == CANNOT_ANSWER]
    silent = [row for row in rows if row["comments"] == CANNOT_ANSWER]
    return {
        "posts": {
            "channels": sorted(no_posts),
            "why": "no file in data/raw/posts/ — the channel has never been walked",
        },
        "comments": {
            "n": len(silent),
            "no_discussion_group": sorted(
                row["handle"] for row in silent if not row["comments_enabled"]
            ),
            "watch_never_joined": sorted(
                row["handle"] for row in silent if row["comments_enabled"] and row["watch"]
            ),
            "collection_gap": sorted(
                row["handle"] for row in silent if row["comments_enabled"] and not row["watch"]
            ),
            "why": (
                "only `collection_gap` is a gap: those channels have comments and were never read."
                " The rest cannot produce a comment at all, and neither is reported as 0"
            ),
        },
    }


def cross_check(rows: list[dict], outside: dict) -> dict:
    """The whole-corpus reconciliation, which is NOT a window number and says so.

    `docs/reports/5c2-prep-b.md`'s dry pass reported 16 218 rows above the (unset) `inference`
    watermark over the registry's channels. That number is the whole store, not this window, and
    the two are never added: this block re-derives it here so that «the census reads the same
    corpus as the dry pass» is a check rather than a hope.
    """
    in_store = sum(row["comments"]["in_store"] for row in rows if row["comments"] != CANNOT_ANSWER)
    inside = sum(row["comments"]["in_window"] for row in rows if row["comments"] != CANNOT_ANSWER)
    return {
        "what": "comments stored for registry channels, WHOLE corpus — the 5a dry pass's queue",
        "comments_in_store_registry_channels": in_store,
        "comments_in_store_outside_the_registry": sum(outside["comments"]["rows"].values()),
        "comments_on_disk_everywhere": in_store + sum(outside["comments"]["rows"].values()),
        "compare_with": "docs/reports/5c2-prep-b.md — the dry pass over the registry's channels",
        "not_a_window_number": (
            "the dry pass has no window: it counts every stored comment above an unset watermark."
            f" The window's own figure is {inside} and the two are different questions"
        ),
    }


def refuse_to_move_the_anchor(out: Path, window: dict) -> None:
    """D68, narrowed to what this file can actually get wrong.

    The census of a moving composition must not be silently replaced by a census of another one —
    but a re-run under the SAME anchor is the determinism gate and has to be allowed, because it
    writes the same bytes by construction. So the refusal is on the anchor, not on the file: a
    different window under the name the operator's ruling cites is what gets stopped.
    """
    if not out.exists():
        return
    was = json.loads(out.read_text(encoding="utf-8"))["anchor"]["anchor"]
    if was != window["anchor"]:
        raise SystemExit(
            f"{rel(out)} was written with anchor {was} and this run's is {window['anchor']}."
            " A different window is a different measurement: give it --out with another path,"
            " keeping the one the ruling was made on."
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--anchor",
        required=True,
        help="the ONE timestamp the window ends at, ISO 8601. Required on purpose: a default read"
        " from the clock would make two runs of the same census two different artifacts",
    )
    parser.add_argument("--out", type=Path, default=RECORD)
    parser.add_argument(
        "--why",
        default="the corpus's own last day + 1: the newest record in data/raw/ is 2026-08-08, so"
        " this is the most recent 28 days that measures CONTENT rather than the collection"
        " schedule (yield_screen_5c1.window_for's reasoning). The operator's to overturn at the"
        " STOP — anchor_sensitivity prices the alternatives",
        help="why this anchor, recorded beside it",
    )
    args = parser.parse_args(argv)

    window = window_of(args.anchor)
    refuse_to_move_the_anchor(args.out, window)
    registry = load_registry(screen.REGISTRY)
    sources = {handle: source for source in registry.sources for handle in source.telegram_channels}
    cursor = loop.load_cursor(CURSOR)
    manifest = json.loads(POST_MEDIA.read_text(encoding="utf-8"))
    pages = leaflet_pages(manifest, window)

    rows = [
        channel_row(handle, source, window, cursor, pages)
        for handle, source in sorted(sources.items())
    ]
    outside = outside_the_registry()
    totals = totals_for(args.anchor, dict(sorted(sources.items())), manifest, cursor)

    record = {
        "phase": "5c2-prep-c2 — the census of the window",
        "contract": "docs/PROMPT-5c2-prep-c2.md deliverable 1; docs/SPEC.md amendment 3.18 (4)",
        "asks": "what the 4-week window holds, per channel and per leg, before anything is bought",
        "anchor": {
            **window,
            "why": args.why,
            "chosen_by": "the executor; the operator's at the STOP",
        },
        "reads_only": (
            "data/raw/, data/loop_cursor.json, config/registry.yaml and"
            " results/post_media_5c1.json. Nothing is fetched, nothing is written outside --out"
        ),
        "definitions": {
            "posts_with_media": (
                "the stored `has_media` flag — scripts/image_census_5c1.py's own definition"
                ' (`row["has_media"]`), which is `message.media is not None` merged across an'
                " album by raw_store.collapse_albums"
            ),
            "leaflet_page_in_window": (
                "a page whose POST is in the window: a page is one message of its post's album and"
                " has no date of its own"
            ),
            "comments_unanswered": (
                "loop.queue_depth over the in-window ids against this channel's `inference`"
                " watermark. Every one of them is unanswered today because that watermark is unset"
                " on every channel — verified below, not assumed"
            ),
            CANNOT_ANSWER: (
                "the store cannot answer this cell — there is no file for that channel and that"
                " record type. It is NOT zero: a channel that was never read and a channel that was"
                " read and produced nothing are different facts"
            ),
        },
        "scope": {
            "registry": {"path": rel(screen.REGISTRY), "sha256": sha256_of(screen.REGISTRY)},
            "channels": len(sources),
            "verified": sum(1 for source in registry.sources if source.verified),
            "note": (
                "the loop walks the registry (run_loop.channels_of), so these are the channels a"
                " paid pass could ask about at all"
            ),
            "outside_the_registry": outside,
        },
        "watermarks": {
            "cursor": rel(CURSOR),
            "inference_set_on": sorted(
                row["handle"] for row in rows if row["watermarks"][loop.INFERENCE] is not None
            ),
            "leaflet_set_on": sorted(
                row["handle"] for row in rows if row["watermarks"][loop.LEAFLET] is not None
            ),
            "reading": (
                "both lists empty means no comment and no page has ever been answered, so every"
                " in-window row below is a row the paid session would buy"
            ),
        },
        "totals": {key: value for key, value in totals.items() if key != "window"},
        "leaflet_coverage": {
            "asks": "pages DOWNLOADED beside posts-with-media — the gap the ATB-only default is"
            " measured against (operator ruling 13.08)",
            "manifest": {"path": rel(POST_MEDIA), "sha256": sha256_of(POST_MEDIA)},
            "manifest_vs_store": manifest_agrees_with_the_store(manifest),
            # The gap itself, subtracted here rather than in a report: two nearby numbers answer
            # different questions — media posts with no page ANYWHERE, and media posts in channels
            # with no page AT ALL — and a reader who takes the second for the first is out by the
            # whole of ATB. Both are named.
            "gap": {
                "posts_with_media_in_window": totals["posts_with_media_in_window"],
                "posts_with_a_page_downloaded": totals["leaflet_posts_in_window"],
                "posts_with_media_and_no_page": totals["posts_with_media_in_window"]
                - totals["leaflet_posts_in_window"],
                "posts_with_media_in_channels_with_no_page_at_all": sum(
                    row["posts_with_media_in_window"]
                    for row in rows
                    if row["posts_with_media_in_window"] != CANNOT_ANSWER
                    and not row["leaflet"]["pages_in_window"]
                ),
                "channels_with_any_page": sorted(
                    row["handle"] for row in rows if row["leaflet"]["pages_in_window"]
                ),
            },
            "per_channel": {
                row["handle"]: {
                    "posts_with_media_in_window": row["posts_with_media_in_window"],
                    "posts_with_pages_downloaded_in_window": row["leaflet"][
                        "posts_with_pages_in_window"
                    ],
                    "pages_downloaded_in_window": row["leaflet"]["pages_in_window"],
                }
                for row in rows
                if row["posts_with_media_in_window"] != CANNOT_ANSWER
                and (row["posts_with_media_in_window"] or row["leaflet"]["pages_in_window"])
            },
        },
        "concentration": {
            "comments_in_window": concentration(
                rows,
                lambda row: (
                    row["comments"]["in_window"] if row["comments"] != CANNOT_ANSWER else None
                ),
            ),
            "posts_in_window": concentration(
                rows,
                lambda row: row["posts"]["in_window"] if row["posts"] != CANNOT_ANSWER else None,
            ),
        },
        "cannot_answer": cannot_answer(rows),
        "cross_check": cross_check(rows, outside),
        "anchor_sensitivity": [
            {"why": why, **totals_for(anchor, dict(sorted(sources.items())), manifest, cursor)}
            for anchor, why in ALTERNATIVE_ANCHORS
        ],
        "channels": rows,
        "producer": producer(),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"window {window['since'][:10]} .. {window['until'][:10]} (28d, anchor {window['anchor']})"
    )
    for key, value in record["totals"].items():
        print(f"  {key:<32}{value:>8}")
    top = record["concentration"]["comments_in_window"][:5]
    print("\ntop 5 by comments in window:")
    for row in top:
        print(
            f"  {row['handle'][:28]:<30}{row['n']:>7}{row['share']:>8.1%}{row['cumulative_share']:>8.1%} cum"
        )
    print(f"\nwrote {rel(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
