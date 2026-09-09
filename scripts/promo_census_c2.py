#!/usr/bin/env python3
"""K3 — the C2 census: what the paid backfill would buy, per channel, at $0.

S3 of `docs/plans/promo-pulse-1.md`. This is half of the table the operator decides SP-1 on; the
other half is `scripts/promo_projection_c2.py`, which prices what this counts.

**The window's anchor is read here, after S2, and never carried in from a document.** The corpus's
own last day + 1 is the ratified precedent (`5c2-stop-ruling-and-cap-33` (a)): a later anchor buys
days that are empty by construction and measures the collection schedule instead of the content.
S2 moves that day, so a census run before the top-up would pre-register a population that no longer
exists by the time it is bought. The record states the anchor date it used.

**The population is pinned by its ids, not by a date range** (SPEC 3.18 (4)): `selection.ids_sha256`
is taken over the sorted (channel, msg_id) of every row the paid pass would read, so a range
re-evaluated at run time cannot quietly buy a different set.

**Pages are counted where a manifest knows them and BOUNDED where none does.** The paid vision leg
is priced per PAGE, and the store does not carry a page count: `raw_store.post_record` keeps
`has_media` as a bool merged across an album, and the page count lives in the media manifests
(`results/post_media_*.json`), which between them cover 367 posts of three channels. For every other
channel the honest answer is an inequality, not a number: a media post has at least one page, and
the largest album those 367 posts contain is ten. Both ends are measured here and printed as
`pages_floor` / `pages_ceiling`, so the projection can range over them instead of inventing a mean
([[bound_instead_of_recompute]]).

    python3.11 scripts/promo_census_c2.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

from registry_revision_proposal import bucket  # noqa: E402
from retail_census import PRICE_BRANCHES  # noqa: E402

from market_pulse.raw_store import live_store  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

STORE = live_store()
"""v1 ∪ r2, r2 winning (plan §5.14). The census prices the corpus AFTER S2's top-up, so reading
`data/raw/` alone would price the pre-top-up store and pre-register a population that no longer
exists — the same failure §5.1 fixes for the anchor, one root down."""
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
MANIFESTS = ("post_media_5c1.json", "post_media_45g2.json", "post_media_visc.json")
OUT = REPO_ROOT / "results" / "promo_census_c2.json"

WINDOW_DAYS = 28
"""`scripts/collect_5c1.py::WINDOW_DAYS`, `scripts/collect_r2.py`'s and `census_5c2`'s. One length,
three instruments — a census over a different window would price a population nobody collected."""


def rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def price_branches(text: str) -> list[str]:
    return sorted(name for name, pattern in PRICE_BRANCHES.items() if pattern.search(text or ""))


def manifests() -> tuple[dict, dict]:
    """(pages per (channel, msg_id), the album-size evidence the ceiling is measured on).

    Read from every manifest on disk rather than from the one this phase happens to know: the
    ceiling is a claim about what an album can hold in THIS corpus, and a claim measured on 19
    posts of one channel would be a claim about that channel.
    """
    pages: dict[tuple[str, str], int] = {}
    sizes: list[int] = []
    for name in MANIFESTS:
        path = REPO_ROOT / "results" / name
        if not path.exists():
            continue
        for entry in (json.loads(path.read_text(encoding="utf-8")).get("entries") or {}).values():
            n = len(entry.get("images") or [])
            sizes.append(n)
            if n:
                pages[(entry["channel"], str(entry["msg_id"]))] = n
    return pages, {
        "manifests": [name for name in MANIFESTS if (REPO_ROOT / "results" / name).exists()],
        "posts_measured": len(sizes),
        "images_measured": sum(sizes),
        "largest_album": max(sizes) if sizes else 0,
        "note": "the ceiling is the largest album these manifests contain, measured — not the"
        " platform's documented limit, which this repo has no file for",
    }


def anchor_of(collected: list[str]) -> date:
    """The corpus's own last day + 1, over the channels r2 collects — read, never carried in."""
    days = [
        (post.get("date") or "")[:10]
        for handle in collected
        for post in STORE.rows("post", handle)
        if post.get("date")
    ]
    if not days:
        raise SystemExit(
            "no post on disk for any collected A1 channel — the census cannot anchor a window on an"
            " empty corpus, and S2 is what fills it"
        )
    return date.fromisoformat(max(days)) + timedelta(days=1)


def channel_row(handle: str, source, since: date, anchor: date, pages: dict, ceiling: int) -> dict:
    in_window = [
        post
        for post in STORE.rows("post", handle)
        if post.get("date") and since <= date.fromisoformat(post["date"][:10]) < anchor
    ]
    media = [post for post in in_window if post.get("has_media")]
    text_price = [post for post in in_window if price_branches(post.get("text") or "")]
    known = [(handle, str(post["msg_id"])) for post in media if (handle, str(post["msg_id"])) in pages]
    return {
        "channel": handle,
        "source_id": source.id,
        "source_type": source.source_type,
        "audience": source.audience,
        "posts_in_window": len(in_window),
        "posts_with_media_in_window": len(media),
        "media_share": round(len(media) / len(in_window), 4) if in_window else None,
        "text_price_posts_in_window": len(text_price),
        "price_share": round(len(text_price) / len(in_window), 4) if in_window else None,
        "pages_known": sum(pages[key] for key in known),
        "posts_with_pages_known": len(known),
        "pages_floor": sum(pages[key] for key in known) + (len(media) - len(known)),
        "pages_ceiling": sum(pages[key] for key in known) + (len(media) - len(known)) * ceiling,
        "media_msg_ids": sorted(str(post["msg_id"]) for post in media),
        "text_price_msg_ids": sorted(str(post["msg_id"]) for post in text_price),
    }


def ids_sha256(selection: list[tuple[str, str, str]]) -> str:
    blob = "\n".join(f"{leg}\x1f{channel}\x1f{msg_id}" for leg, channel, msg_id in sorted(selection))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def selected(a1: list[tuple], channels: list[str] | None) -> list[tuple]:
    """The A1 pairs `--channels` names, by the REGISTRY's spelling — or all of them.

    The spelling is `registry.yaml :: telegram_channels`, whatever shape it has: `@marketopt_promo`
    for a public handle, `+Ejz6ubzm21IyMTQy` for a channel joined by invite. A handle the registry
    lacks is refused here rather than priced as an empty channel, because `promo_post.owner()`
    matches that same list verbatim — a record written with a file stem (`marketopt_promo`) or with
    an `@` the registry does not carry (`@marketopt_private`) resolves to no source at all and would
    silently never fire R2/R3 (ruling 08.09 (dd) item 5).
    """
    if channels is None:
        return a1
    known = {handle for _, handle in a1}
    unknown = [one for one in channels if one not in known]
    if unknown:
        raise SystemExit(
            "not an A1 channel of config/registry.yaml: "
            + ", ".join(unknown)
            + " — the census prices the registry's own spelling (`telegram_channels`), never a"
            " file stem and never a handle the registry lacks"
        )
    wanted = set(channels)
    return [(source, handle) for source, handle in a1 if handle in wanted]


def build(channels: list[str] | None = None, anchor: date | None = None) -> dict:
    registry = load_registry(REGISTRY)
    a1 = selected(
        [
            (source, handle)
            for source in registry.sources
            if source.collect and bucket(source) == "A"
            for handle in source.telegram_channels
        ],
        channels,
    )
    pages, evidence = manifests()
    ceiling = evidence["largest_album"] or 1
    anchor_pinned = anchor is not None
    anchor = anchor or anchor_of([handle for _, handle in a1])
    since = anchor - timedelta(days=WINDOW_DAYS)

    rows_ = [channel_row(handle, source, since, anchor, pages, ceiling) for source, handle in a1]
    rows_.sort(key=lambda row: (-row["posts_with_media_in_window"], row["channel"]))
    selection = [
        ("leaflet_page", row["channel"], msg_id) for row in rows_ for msg_id in row["media_msg_ids"]
    ] + [
        ("post_text", row["channel"], msg_id)
        for row in rows_
        for msg_id in row["text_price_msg_ids"]
    ]
    return {
        "contract": "docs/plans/promo-pulse-1.md S3 / K3 — the C2 census ($0)",
        "window": {
            "anchor": anchor.isoformat(),
            "since": since.isoformat(),
            "days": WINDOW_DAYS,
            "rule": "since <= date < anchor, half-open",
            "anchor_rule": (
                "pinned by --anchor: the registration's own date, not a reading of the store"
                if anchor_pinned
                else "the corpus's own last day + 1, read after S2's top-up —"
                " 5c2-stop-ruling-and-cap-33 (a), plan §5.1 as corrected by the 30.08 review"
            ),
        },
        "channels": rows_,
        "page_bound": evidence,
        "selection": {
            "leaflet_page": {
                "posts": sum(row["posts_with_media_in_window"] for row in rows_),
                "pages_floor": sum(row["pages_floor"] for row in rows_),
                "pages_ceiling": sum(row["pages_ceiling"] for row in rows_),
                "pages_known": sum(row["pages_known"] for row in rows_),
            },
            "post_text": {"posts": sum(row["text_price_posts_in_window"] for row in rows_)},
            "ids_sha256": ids_sha256(selection),
            "rows": len(selection),
            "pinned_by": "row ids, not a date range evaluated at run time — SPEC 3.18 (4)",
        },
        "totals": {
            "channels": len(rows_),
            "posts_in_window": sum(row["posts_in_window"] for row in rows_),
            "posts_with_media_in_window": sum(row["posts_with_media_in_window"] for row in rows_),
            "text_price_posts_in_window": sum(row["text_price_posts_in_window"] for row in rows_),
        },
    }


def render(record: dict) -> str:
    head = (
        f"{'channel':<24}{'posts':>7}{'media':>7}{'media_sh':>10}"
        f"{'txt$':>6}{'pages≥':>8}{'pages≤':>8}"
    )
    lines = [head, "-" * len(head)]
    for row in record["channels"]:
        share = "—" if row["media_share"] is None else f"{row['media_share']:.3f}"
        lines.append(
            f"{row['channel']:<24}{row['posts_in_window']:>7}{row['posts_with_media_in_window']:>7}"
            f"{share:>10}{row['text_price_posts_in_window']:>6}"
            f"{row['pages_floor']:>8}{row['pages_ceiling']:>8}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument(
        "--channels",
        nargs="+",
        metavar="HANDLE",
        help="price only these A1 channels, by the registry's own spelling"
        " (default: every A1 channel)",
    )
    parser.add_argument(
        "--anchor",
        type=date.fromisoformat,
        metavar="YYYY-MM-DD",
        help="pin the window's anchor (default: the corpus's own last day + 1)",
    )
    args = parser.parse_args(argv)

    record = build(args.channels, args.anchor)
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    window = record["window"]
    print(f"window {window['since']} … {window['anchor']} ({window['days']} days, {window['rule']})")
    print(render(record))
    selection = record["selection"]
    print(
        f"\nleaflet posts {selection['leaflet_page']['posts']}"
        f" → pages {selection['leaflet_page']['pages_floor']}…"
        f"{selection['leaflet_page']['pages_ceiling']}"
        f" ({selection['leaflet_page']['pages_known']} known from a manifest)"
        f" · text-price posts {selection['post_text']['posts']}"
    )
    print(f"selection.ids_sha256 {selection['ids_sha256'][:16]}… over {selection['rows']} rows")
    where = args.out.relative_to(REPO_ROOT) if args.out.is_relative_to(REPO_ROOT) else args.out
    print(f"wrote {where}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
