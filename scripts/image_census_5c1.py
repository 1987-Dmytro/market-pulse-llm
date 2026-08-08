#!/usr/bin/env python3
"""How much of the registry's window is unreadable, and what reading it would cost. ($0, offline.)

The yield screen refused to report because @atb_market_official — the channel the project was
built on — yielded nothing: 19 of its 25 windowed posts carry no text at all. That is a finding
about the corpus and not about one channel, and the operator's direction is to price the fix
before buying it. So this counts, over every registry channel's collected window, which of the
four states `parents.context` can return each post is in:

    post_text · image_caption · poll_text · no_text_and_no_caption

The states are not restated here — `market_pulse.parents.context` is the one place that decides
what stands in for a post's missing text, and every labelling pass in the repo already goes
through it. A census that re-implemented the rule would be a second opinion about the corpus that
nothing holds to the first.

Two guards make the number citable rather than fresh:

* the window is the yield screen's own (`window_for`, imported, raw-v1 rule included), and
* every channel's split is reconciled against `results/yield_screen_5c1.json` — the record the
  operator signed against. A mismatch is a STOP, because a census that disagrees with the screen
  about how many posts are readable is measuring a different corpus than the one under discussion.

The price projection is the decision this file exists for, and it is deliberately two numbers: an
upper bound, and the same bound discounted by the population split 4.5g2 actually measured.

    PYTHONPATH=src python3 scripts/image_census_5c1.py
"""

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import yield_screen_5c1 as screen  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

from market_pulse import parents  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

CAPTIONS = REPO_ROOT / "data" / "annotation" / "post_captions.jsonl"
"""The 4.5g2 captions, read-only. Without them `image_caption` and `poll_text` could not occur in
this census at all, and a state that cannot occur is not a state that was counted."""

CAPTION_RECORD = REPO_ROOT / "results" / "captions_45g2.json"
RECORD = REPO_ROOT / "results" / "image_census_5c1.json"
YIELD_RECORD = REPO_ROOT / "results" / "yield_screen_5c1.json"

STATES = ("post_text", "image_caption", "poll_text", "no_text_and_no_caption")

SPLIT_45G2 = {"image": 21, "poll": 16, "nothing": 4}
"""What the 41 media-only posts of 4.5g2 turned out to be once Telegram was asked. Offline this
census cannot tell a poll from a photo — `has_media` is true for both and `raw_store.post_record`
stores `message.raw_text`, which a poll leaves empty — so this measured split is the only honest
discount available. Polls cost nothing (their question is transcribed, no model), and the four
that were a video, an audio message and two giveaways cost nothing because nothing can speak for
them."""


def caption_rate() -> dict:
    """What one caption cost in 4.5g2, read out of that phase's own record."""
    run = json.loads(CAPTION_RECORD.read_text(encoding="utf-8"))["runs"][0]
    posts, usd, sent = run["cost"]["requests"], run["cost"]["usd"], run["images"]["sent"]
    return {
        "source": screen.rel(CAPTION_RECORD),
        "model": run["model"],
        "posts_captioned": posts,
        "usd_total": usd,
        "usd_per_post": round(usd / posts, 8),
        "images_sent": sent,
        "images_per_post": round(sent / posts, 2),
        "usd_per_image_sent": round(usd / sent, 8),
        "note": (
            "one request per post, the whole album in it, capped at 6 images. A channel that"
            " posts albums sits at or above this average rather than below it"
        ),
    }


def census_channel(handle: str, window: dict, posts: list[dict], index: dict, caps: dict) -> dict:
    """One channel's window, split by what a reader of that post would actually have."""
    rows = screen.in_window(posts, window)
    counts = dict.fromkeys(STATES, 0)
    silent_with_media, silent_without_media = [], []
    for row in rows:
        state = parents.context(index, caps, {"channel": handle, "parent_msg_id": row["msg_id"]})[
            "state"
        ]
        counts[state] += 1
        if state == "no_text_and_no_caption":
            (silent_with_media if row["has_media"] else silent_without_media).append(row["msg_id"])
    return {
        "handle": handle,
        "window": {"since": window["since"], "until": window["until"], "source": window["source"]},
        "posts_in_window": len(rows),
        "states": counts,
        # What a caption could reach. A silent post with no media at all is not a captioning
        # target and is not in the projection — it is a post that says nothing in any modality.
        "uncaptioned_with_media": len(silent_with_media),
        "uncaptioned_without_media": len(silent_without_media),
        "uncaptioned_msg_ids": sorted(silent_with_media),
    }


def reconcile(rows: list[dict], record: dict) -> None:
    """The census and the screen must agree about which posts are readable, or neither is read.

    They share `window_for` and the same store, so a disagreement means one of the two moved: a
    different window rule, a different text test, a file loaded differently. The screen is the
    record the operator signed against, so it is the one this defers to — and a census that
    quietly diverged from it would price a population nobody has seen.
    """
    screened = {row["handle"]: row for row in record["sources"]}
    drift = []
    for row in rows:
        other = screened.get(row["handle"])
        if other is None:
            drift.append(f"{row['handle']}: not in {YIELD_RECORD.name}")
            continue
        silent = row["posts_in_window"] - row["states"]["post_text"]
        expected = (
            other["posts"]["in_window"],
            other["posts"]["with_text"],
            other["posts"]["without_text"],
        )
        measured = (row["posts_in_window"], row["states"]["post_text"], silent)
        if measured != expected:
            drift.append(f"{row['handle']}: census {measured} vs screen {expected}")
    if drift:
        raise SystemExit(
            "the census does not read the same window as the screen the operator signed against:\n"
            + "\n".join(f"  {line}" for line in drift)
        )


def projection(rows: list[dict], rate: dict) -> dict:
    """What captioning every silent post with an image would cost — bounded, then discounted."""
    targets = sum(row["uncaptioned_with_media"] for row in rows)
    unreachable = sum(row["uncaptioned_without_media"] for row in rows)
    share = SPLIT_45G2["image"] / sum(SPLIT_45G2.values())
    return {
        "captionable_posts_upper_bound": targets,
        "usd_upper_bound": round(targets * rate["usd_per_post"], 4),
        "expected_image_share": round(share, 3),
        "expected_captions": round(targets * share, 1),
        "usd_expected": round(targets * share * rate["usd_per_post"], 4),
        "posts_with_nothing_to_caption": unreachable,
        "rate": rate,
        "split_45g2": SPLIT_45G2,
        "reading": (
            "upper bound = every silent post with media, priced as if all of them were photos."
            " The expected figure discounts it by the split 4.5g2 measured when it asked Telegram"
            f" what those posts were: {SPLIT_45G2['image']} photos, {SPLIT_45G2['poll']} polls"
            " (transcribed free, no model) and"
            f" {SPLIT_45G2['nothing']} with nothing any model could read, of"
            f" {sum(SPLIT_45G2.values())}. Both are per ONE pass over the current windows"
        ),
    }


def refuse_to_overwrite(out: Path) -> None:
    """D68: a dated measurement of a moving composition gets a dated file, never the same name."""
    if out == RECORD and RECORD.exists():
        raise SystemExit(
            f"{screen.rel(RECORD)} already exists — it is the census of the windows as they stood"
            " when the price was quoted. A later pass is a different measurement: give it --out"
            " with another path."
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD, help="where to write the record")
    parser.add_argument("--captions", type=Path, default=CAPTIONS)
    args = parser.parse_args(argv)
    refuse_to_overwrite(args.out)

    registry = load_registry(screen.REGISTRY)
    index = parents.load(screen.POSTS)
    caps = parents.load_captions(args.captions)
    shared, collected = screen.collect_window(), screen.collected_handles()

    rows = []
    for source in registry.sources:
        for handle in source.telegram_channels:
            posts = screen.load_jsonl(screen.POSTS / f"{handle.lstrip('@')}.jsonl")
            window = screen.window_for(handle, posts, shared, collected)
            rows.append(
                {**census_channel(handle, window, posts, index, caps), "audience": source.audience}
            )
    rows.sort(key=lambda row: (row["audience"] or "", row["handle"].lower()))

    signed = json.loads(YIELD_RECORD.read_text(encoding="utf-8"))
    reconcile(rows, signed)

    totals = {state: sum(row["states"][state] for row in rows) for state in STATES}
    totals["posts_in_window"] = sum(row["posts_in_window"] for row in rows)
    by_audience: dict[str, dict] = {}
    for row in rows:
        bucket = by_audience.setdefault(
            row["audience"] or "unassigned", {"n": 0, "posts": 0, **dict.fromkeys(STATES, 0)}
        )
        bucket["n"] += 1
        bucket["posts"] += row["posts_in_window"]
        for state in STATES:
            bucket[state] += row["states"][state]

    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "5c1 — the image census",
        "asks": "how many posts of each channel's collected window carry no readable text",
        "contract": "docs/PROMPT-5c1-captions-pilot.md step 1",
        "states": {
            "source": "market_pulse.parents.context — the one rule the labelling passes use",
            "post_text": "the post has text of its own",
            "image_caption": "no text; a vision model's description stands in for it",
            "poll_text": "no text; Telegram's own poll question and options stand in for it",
            "no_text_and_no_caption": "no text and nothing standing in for it — unreadable today",
        },
        "captions_read": {
            "path": screen.rel(args.captions),
            "sha256": hashlib.sha256(args.captions.read_bytes()).hexdigest(),
            "rows": len(caps),
            "rows_inside_a_censused_window": totals["image_caption"] + totals["poll_text"],
            "note": (
                "4.5g2's captions, read-only. They are the only reason two of the four states can"
                " occur at all — and they land on none of these windows: all 37 are @VARUS_channel"
                " parents of labelled comments, dated 2025-06-17…2026-06-22, and every window"
                " censused here starts later. So `image_caption` and `poll_text` read 0 because"
                " the corpus has no captions in these 28 days, not because the file went unread"
            ),
        },
        "window": {
            "days": screen.WINDOW_DAYS,
            "shared": {"since": shared[0], "until": shared[1]},
            "rule": "screen.window_for — the yield screen's own, raw-v1 originals included",
        },
        "reconciled_with": {
            "path": screen.rel(YIELD_RECORD),
            "sha256": hashlib.sha256(YIELD_RECORD.read_bytes()).hexdigest(),
            "check": (
                "per channel: posts_in_window, post_text == screen.posts.with_text, and the sum of"
                " the other three states == screen.posts.without_text. A mismatch stops the run"
            ),
        },
        "totals": totals,
        "projection": projection(rows, caption_rate()),
        "by_audience": dict(sorted(by_audience.items())),
        "sources": rows,
        "git": git_state(args.out),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    silent = totals["no_text_and_no_caption"]
    print(f"{len(rows)} channels · {totals['posts_in_window']} posts in window")
    for state in STATES:
        share = totals[state] / totals["posts_in_window"] if totals["posts_in_window"] else 0
        print(f"  {state:<24}{totals[state]:>7}  {share:>6.1%}")
    proj = record["projection"]
    print(
        f"\nunreadable today: {silent}"
        f" — {proj['captionable_posts_upper_bound']} of them carry media,"
        f" {proj['posts_with_nothing_to_caption']} carry none"
        f"\nprice of one full pass: ${proj['usd_upper_bound']:.2f} upper bound,"
        f" ${proj['usd_expected']:.2f} expected"
        f" at ${proj['rate']['usd_per_post']:.6f}/caption ({proj['rate']['source']})"
        f"\n\nwrote {screen.rel(args.out)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
