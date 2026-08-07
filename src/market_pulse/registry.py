"""Source registry: sources, category taxonomy and brand watchlist (docs/SPEC.md §3).

Validation is strict on purpose. A typo in a handle silently collects nothing, and a
duplicate id silently merges two sources' (or two brands') data into one rollup — both
are failures that only surface as wrong analytics much later.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

# Telegram public username: 5-32 chars, starts with a letter, letters/digits/underscore.
_HANDLE = re.compile(r"^@[A-Za-z][A-Za-z0-9_]{4,31}$")

SOURCE_TYPES = ("official_retail", "aggregator", "community", "government")
"""``government`` was added at the 5c1 registry write (team-lead ruling 2026-08-07): the launch
composition carries @dpssgovua, Держпродспоживслужба, and a state food-safety inspectorate is
none of the other three. It is the falsification-watch source SPEC 3.11 (4) authorised."""

AUDIENCES = (
    "retail_official",
    "supermarket_deals",
    "cooking_recipes",
    "mothers_kids",
    "baby_food",
    "health_fitness",
    "food_quality",
    "regional",
)
"""Whose audience a source speaks to — operator ruling 2026-08-08, canon
`docs/CHANNELS-launch.md`, "Сегментация источников — audience". A closed list of exactly eight,
kept at this granularity so a report can fold them into whatever coarse grouping it needs (retail
= official + deals, mothers = mothers_kids + baby_food) — folding is reversible, a coarse field
is not. Which source carries which value is the canon's table, never derived here.

`food_quality` was `food_quality_gov` until the operator's wave-3 ruling of 2026-08-08: who runs a
source is what `source_type` answers, so the segment carries no `_gov` — an NGO running its own lab
checks on counterfeit dairy speaks to the same audience as the state service does."""


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    source_type: str
    telegram_channels: tuple[str, ...]
    verified: bool = False
    # Set from the entry check. False means the source carries launches but no
    # reactions — those come from another source (SPEC §9 fallback).
    comments_enabled: bool = False
    # 5c1 watch bucket: posts are collected, the discussion group is NEVER joined until the
    # channel posts again (SPEC 3.11 (4), operator 2026-08-06). A silent channel keeps its
    # group, so `comments_enabled` alone cannot say "do not join" — this flag does.
    watch: bool = False
    # The third registry dimension, beside source_type ("who runs it") and the product taxonomy
    # ("what is discussed"): whose audience this source speaks to. 5c2 keys aggregates on it, so
    # a report can say "mothers think X, the regions think Y" with the sources behind it.
    audience: str | None = None


@dataclass(frozen=True)
class Taxonomy:
    """Tracked groups: group key -> {name: UA display, subcategories: {key: UA display}}.

    Kept as the raw mapping — the collector only needs the keys, the dashboard only
    needs the display names, and neither justifies a second dataclass yet.
    """

    tracked_groups: dict


@dataclass(frozen=True)
class WatchlistBrand:
    brand_id: str
    display_names: tuple[str, ...]
    own: bool = False


@dataclass(frozen=True)
class Registry:
    sources: tuple[Source, ...]
    taxonomy: Taxonomy
    watchlist: tuple[WatchlistBrand, ...]


def load_registry(path: str | Path) -> Registry:
    """Load and validate the registry, or raise ``ValueError`` naming the defect."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return Registry(
        _sources(path, data.get("sources")),
        _taxonomy(path, data.get("taxonomy")),
        _watchlist(path, data.get("watchlist")),
    )


def _sources(path: str | Path, entries) -> tuple[Source, ...]:
    if not entries:
        raise ValueError(f"{path}: no sources defined")

    sources: list[Source] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError(f"{path}: each source must be a mapping, got {entry!r}")
        sid, name = entry.get("id"), entry.get("name")
        if not sid or not name:
            raise ValueError(f"{path}: source needs both 'id' and 'name': {entry!r}")
        if sid in seen:
            raise ValueError(f"{path}: duplicate source id {sid!r}")
        seen.add(sid)
        source_type = entry.get("source_type")
        if source_type not in SOURCE_TYPES:
            raise ValueError(
                f"{path}: source {sid!r} has unknown source_type {source_type!r}, "
                f"expected one of {', '.join(SOURCE_TYPES)}"
            )
        channels = entry.get("telegram_channels") or []
        if not channels:
            raise ValueError(f"{path}: source {sid!r} has no telegram_channels")
        for channel in channels:
            if not isinstance(channel, str) or not _HANDLE.match(channel):
                raise ValueError(f"{path}: source {sid!r} has a malformed handle {channel!r}")
        watch = entry.get("watch", False)
        if not isinstance(watch, bool):
            # Strict where it is load-bearing: `watch: "no"` is truthy, and a watch channel read
            # as a launch channel is a group join the operator forbade.
            raise ValueError(f"{path}: source {sid!r} has a non-boolean watch {watch!r}")
        audience = entry.get("audience")
        if audience is not None and audience not in AUDIENCES:
            # A closed list: a typo'd segment would silently make its own bucket in every
            # aggregate 5c2 keys on this field, and read as a real audience nobody chose.
            raise ValueError(
                f"{path}: source {sid!r} has unknown audience {audience!r}, "
                f"expected one of {', '.join(AUDIENCES)}"
            )
        sources.append(
            Source(
                sid,
                name,
                source_type,
                tuple(channels),
                bool(entry.get("verified")),
                bool(entry.get("comments_enabled")),
                watch,
                audience,
            )
        )
    return tuple(sources)


def _taxonomy(path: str | Path, data) -> Taxonomy:
    groups = (data or {}).get("tracked_groups")
    if not isinstance(groups, dict) or not groups:
        raise ValueError(f"{path}: taxonomy needs a non-empty 'tracked_groups' mapping")
    return Taxonomy(groups)


def _watchlist(path: str | Path, entries) -> tuple[WatchlistBrand, ...]:
    brands: list[WatchlistBrand] = []
    seen: set[str] = set()
    for entry in entries or []:
        if not isinstance(entry, dict) or not entry.get("brand_id"):
            raise ValueError(f"{path}: watchlist entry needs a 'brand_id': {entry!r}")
        bid = entry["brand_id"]
        if bid in seen:
            raise ValueError(f"{path}: duplicate brand_id {bid!r}")
        seen.add(bid)
        names = entry.get("display_names") or []
        if not names:
            raise ValueError(f"{path}: brand {bid!r} has no display_names")
        brands.append(WatchlistBrand(bid, tuple(names), bool(entry.get("own"))))
    return tuple(brands)


if __name__ == "__main__":
    import sys

    registry = load_registry(sys.argv[1])
    for source in registry.sources:
        state = "verified" if source.verified else "UNVERIFIED"
        comments = "comments" if source.comments_enabled else "posts-only"
        channels = " ".join(source.telegram_channels)
        print(f"{source.id}\t{source.source_type}\t{state}\t{comments}\t{channels}")
    print(f"tracked groups: {', '.join(registry.taxonomy.tracked_groups)}")
    print(f"watchlist: {len(registry.watchlist)} brands")
