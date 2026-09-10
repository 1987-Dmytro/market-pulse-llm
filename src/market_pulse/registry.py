"""Source registry: sources, category taxonomy and brand watchlist (docs/SPEC.md §3).

Validation is strict on purpose. A typo in a handle silently collects nothing, and a
duplicate id silently merges two sources' (or two brands') data into one rollup — both
are failures that only surface as wrong analytics much later.
"""

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

_USERNAME = r"@[A-Za-z][A-Za-z0-9_]{4,31}"
"""Telegram public username: 5-32 chars, starts with a letter, letters/digits/underscore."""

_INVITE = r"\+[A-Za-z0-9_-]{16,}"
"""A private channel's join hash, as `t.me/+<hash>` writes it — base64url, 16 chars and up."""

_CHAT_ID = r"-?\d{6,}"
"""A bare chat id, for an entity that has no username at all. Both the raw form and the
`-100`-prefixed form are accepted; which one resolves is the client's business, not the
registry's."""

_HANDLE = re.compile(rf"^(?:{_USERNAME}|{_INVITE}|{_CHAT_ID})$")
"""What may stand in `telegram_channels`: a union of the three things Telegram addresses an entity
by, and not a loosened username.

Revision r2's A1 list carries two entries that are not public usernames and cannot be written down
under the username rule alone. Маркетопт's private channel is an invite hash —
`+Ejz6ubzm21IyMTQy`, `results/retail_chains.json` records its kind as `invite` — and
@ATB_FANatik's discussion group «АТБ / ЗНИЖКИ» has `username: null` and only an id, 1925810730
(`results/retail_census.json`). A sibling field would have been the other way to say this, and it
is the wrong way: `telegram_channels` may not be empty (`_sources` raises, and
`test_shipped_registry_loads` asserts every source has one), so a row addressed only by an id would
have had to carry an empty list and would have failed both. Widening the accepted entry keeps every
existing assertion true, and `chan_without_at` still matches none of the three."""

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
    # Revision r2 (operator ruling 2026-08-30, SPEC v2 §3): a source leaves COLLECTION without
    # leaving the registry — «выводится из сбора… данные и замороженные тесты остаются». The
    # alternative, deleting the paused rows, breaks the build at $0: `build_aggregates.segment_for`
    # raises `SystemExit` for any channel that carries evidence rows and has no registry entry, and
    # 21 of the 28 channels on disk are in that position. So the row stays and says it is not
    # collected; the collector reads this flag and every historical reader keeps resolving the row.
    collect: bool = True


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
    return load_registry_text(Path(path).read_text(encoding="utf-8"), path)


def load_registry_text(text: str, path: str | Path) -> Registry:
    """The same, from bytes that are not on disk — a reconstruction of what a record pinned.

    ``path`` is carried for the error messages only: a defect has to say which file it is in, and
    a reconstruction is still that file, at an earlier revision of it.
    """
    data = yaml.safe_load(text) or {}
    return Registry(
        _sources(path, data.get("sources")),
        _taxonomy(path, data.get("taxonomy")),
        _watchlist(path, data.get("watchlist")),
    )


RATIFIED_COMMENT = "# (13)(b)"

LATIN_ALIASES_13B = (
    ('display_names: ["Рудь", "Rud"]', 'display_names: ["Рудь"]'),
    (
        'display_names: ["Три Ведмеді", "Три Медведя", "Three Bears"]',
        'display_names: ["Три Ведмеді", "Три Медведя"]',
    ),
    ('display_names: ["Лімо", "Лимо", "LIMO"]', 'display_names: ["Лімо", "Лимо"]'),
)
"""Every ``display_names`` list SPEC 3.17 (13)(b) touched, as it is now and as it was.

Written out one pair per line, and literally: a reader deciding whether an alias is justified is
looking at one brand, and the enumeration is also what makes the next amendment impossible to land
unseen — it will have to be added here or the reconstruction below stops re-deriving."""


R2_MARK = "# (r2)"
"""The trailing marker on every line revision r2 added INSIDE a row r1 already had."""

R2_OPENS = "  # --- r2 BEGIN"
R2_CLOSES = "  # --- r2 END"
"""The brackets around the one block of rows r2 APPENDED."""


def registry_before_r2(path: str | Path) -> bytes:
    """``config/registry.yaml`` as revision r1 — the bytes the records pinning `d4e3b237…` read.

    Revision r2 (operator ruling 2026-08-30, `docs/PHASE-promo-pulse-1.md` §3) does exactly two
    things to this file: it appends eight A1 sources inside ONE bracketed block, and it puts
    ``collect: false`` with its two provenance keys on the 39 rows that leave collection. Neither
    moves a row r1 had. Both are written so that undoing them is a line filter — which is the
    whole reason the r1 pins keep holding instead of being re-pinned to follow the file. Same
    shape and the same reason as :func:`registry_before_the_latin_aliases`, one revision later.

    Strict in both directions: the block must be exactly one open/close pair, and at least one
    marked line must exist. A reconstruction that silently found nothing to undo would return
    today's bytes and quietly satisfy a pin it never reached.
    """
    lines = Path(path).read_text(encoding="utf-8").splitlines(keepends=True)
    opens = [i for i, line in enumerate(lines) if line.startswith(R2_OPENS)]
    closes = [i for i, line in enumerate(lines) if line.startswith(R2_CLOSES)]
    if len(opens) != 1 or len(closes) != 1 or closes[0] < opens[0]:
        raise ValueError(
            f"{path}: the r2 additions are one `{R2_OPENS}` … `{R2_CLOSES}` pair, written once —"
            f" found {len(opens)} open and {len(closes)} close markers"
        )
    block = range(opens[0], closes[0] + 1)
    marked = [i for i, line in enumerate(lines) if line.rstrip("\n").endswith(R2_MARK)]
    if not marked:
        raise ValueError(f"{path}: no line carries `{R2_MARK}` — this is not the r2 registry")
    dropped = set(block) | set(marked)
    return "".join(line for i, line in enumerate(lines) if i not in dropped).encode("utf-8")


def registry_before_the_latin_aliases(path: str | Path) -> bytes:
    """``config/registry.yaml`` as it stood before SPEC 3.17 (13)(b) — the bytes v1–v4 pin.

    The three Latin forms are a ratified edit that moves the file's sha256, and four sealed
    pre-registrations, the leaflet gold and two 5c1 screens all pin the bytes from before it. A pin
    re-pinned is a pin that follows the file instead of holding it, so the chain is written down
    here instead: undo the enumerated ``display_names`` lists and drop the comment lines the
    amendment added, and what is left is what those records read.

    The chain grew a link on 2026-08-30. This function's contract is "the bytes v1–v4 pin", and
    those bytes are now two revisions back, so it walks r2 off first through
    :func:`registry_before_r2` and undoes the aliases on r1's bytes. The (13)(b) check is made on
    the file as it is, before either undo, so a registry the amendment never touched still refuses
    with the sentence it always did rather than with r2's.

    One implementation, called by the producers that recompute a sealed bar and by the tests that
    re-verify the pins. A second copy of this would drift from the one the records are checked with.
    """
    text = Path(path).read_text(encoding="utf-8")
    if not any(line.lstrip().startswith(RATIFIED_COMMENT) for line in text.splitlines()):
        raise ValueError(f"{path}: no `{RATIFIED_COMMENT}` line — this is not the amended registry")
    kept = [
        line
        for line in registry_before_r2(path).decode("utf-8").splitlines(keepends=True)
        if not line.lstrip().startswith(RATIFIED_COMMENT)
    ]
    before = "".join(kept)
    for now, then in LATIN_ALIASES_13B:
        if before.count(now) != 1:
            raise ValueError(f"{path}: `{now}` appears {before.count(now)} times, expected once")
        before = before.replace(now, then)
    return before.encode("utf-8")


def registry_revisions(path: str | Path) -> list[tuple[str, bytes]]:
    """Every revision of `config/registry.yaml` this checkout can produce, newest first.

    Named, because a record that reads the registry has to be able to say WHICH revision it read —
    "byte-identical" is a lie about a file reached through two undos. One list, so a fourth
    revision is added in one place and every consumer gains it at once.
    """
    return [
        ("r2, byte-identical", Path(path).read_bytes()),
        ("r1, through the r2 undo", registry_before_r2(path)),
        (
            "pre-(13)(b), through the r2 undo and the alias undo",
            registry_before_the_latin_aliases(path),
        ),
    ]


def registry_revision_reaching(pin: str, path: str | Path) -> tuple[str, bytes] | None:
    """(revision name, its bytes) for the revision whose sha256 is `pin` — or ``None``.

    The one question every consumer of a pinned registry actually asks. `None` is a refusal at the
    caller's own severity: a producer raises `SystemExit`, a loader raises `ValueError`, and a test
    asserts — and none of them has to re-implement the walk to do it.
    """
    for name, blob in registry_revisions(path):
        if hashlib.sha256(blob).hexdigest() == pin:
            return name, blob
    return None


def load_registry_as_pinned(pin: str, path: str | Path) -> Registry:
    """The registry a record pins: today's file when it still hashes to it, else the reconstruction.

    A record scored under one alias table must keep being recomputed under that table — SPEC 3.17
    (13)(b) is an instrument change, and re-deriving an old bar through it would re-score a sealed
    measurement rather than reproduce it. A pin no revision reaches is a refusal: it means the
    registry has moved in some way nobody wrote down.

    Three revisions today, one per change this file has had since a record last pinned it: r2
    (today's bytes), r1 (:func:`registry_before_r2`) and pre-(13)(b). Seven records pin r1 and eight
    pin pre-(13)(b), which is why both have to be reachable and not merely described.
    """
    reached = registry_revision_reaching(pin, path)
    if reached is None:
        raise ValueError(
            f"{path} pins {pin[:16]}… and no revision this checkout can reconstruct hashes to it —"
            " the registry has moved in a way nothing here can reconstruct"
        )
    return load_registry_text(reached[1].decode("utf-8"), path)


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
        collect = entry.get("collect", True)
        if not isinstance(collect, bool):
            # Strict for the reason `watch` is: `collect: "no"` is truthy, and a paused source
            # read as collectable is exactly the collection the ruling stopped.
            raise ValueError(f"{path}: source {sid!r} has a non-boolean collect {collect!r}")
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
                collect,
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


CHAIN_ALIASES = Path(__file__).resolve().parents[2] / "config" / "chain_aliases.yaml"
"""The chain sidecar — ruling 04.09 (j) item 1, option (a), two sections since (gg) item 2 (b).

A sidecar and not a field: `config/registry.yaml` is pinned by 21 sealed records and may not grow.
It is read HERE, beside the registry it is a sidecar to, because this module is where the project
reads config — `aggregates.py` is handed rows and never opens a path
(`tests/test_aggregates.py::test_the_layer_reads_nothing_and_parses_nothing`)."""


def _aliases(path: Path | None) -> dict:
    """The sidecar's body. `path` is read at CALL time: a default binds the module's value once."""
    path = path or CHAIN_ALIASES
    body = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(body, dict):
        raise ValueError(f"{path}: expected a mapping with a `spellings` section")
    return body


def chain_spellings(path: Path | None = None) -> dict[str, tuple[str, ...]]:
    """chain id -> its spellings, validated the way every other registry file is.

    Strict for `load_registry`'s reason: a spelling that is not a string, or an id whose value is
    not a list, would fold silently into something nobody wrote. The FOLD itself is not here — it
    needs `aggregates.promo_key`'s normalisation, and this module knows nothing about that.
    """
    out = {}
    for chain_id, spellings in (_aliases(path).get("spellings") or {}).items():
        if not isinstance(spellings, list) or not all(isinstance(one, str) for one in spellings):
            raise ValueError(f"{path}: {chain_id!r} must carry a list of spellings, got {spellings!r}")
        out[str(chain_id)] = tuple(spellings)
    return out


def chain_of_channel(path: Path | None = None) -> dict[str, str]:
    """own-channel id -> the chain id it belongs to; every channel the section omits is its own.

    Ruling 09.09 (gg) item 2, shape (b). A spelling may name only one chain, so `marketopt_private`
    — a second channel of the same retailer — cannot say whose it is in `spellings`; it says it
    here, and `aggregates.chain_key` reads this before the spellings.
    """
    out = {}
    for channel_id, chain_id in (_aliases(path).get("chain_of_channel") or {}).items():
        if not isinstance(chain_id, str):
            raise ValueError(f"{path}: {channel_id!r} must fold to one chain id, got {chain_id!r}")
        out[str(channel_id)] = chain_id
    return out


if __name__ == "__main__":
    import sys

    registry = load_registry(sys.argv[1])
    for source in registry.sources:
        state = "verified" if source.verified else "UNVERIFIED"
        comments = "comments" if source.comments_enabled else "posts-only"
        collect = "collect" if source.collect else "NOT-COLLECTED"
        channels = " ".join(source.telegram_channels)
        print(f"{source.id}\t{source.source_type}\t{state}\t{comments}\t{collect}\t{channels}")
    collected = [source for source in registry.sources if source.collect]
    print(f"sources: {len(registry.sources)} — collected {len(collected)}, "
          f"not collected {len(registry.sources) - len(collected)}")
    print(f"tracked groups: {', '.join(registry.taxonomy.tracked_groups)}")
    print(f"watchlist: {len(registry.watchlist)} brands")
