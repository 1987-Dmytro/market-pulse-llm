#!/usr/bin/env python3
"""`data/derived/` → `data/derived/pulse.db` — the aggregate layer of SPEC 3.20 (2).

**One reader.** Not a line of this script parses a derived row. The reading path is
`scripts/window_summary_5c2.py`'s — `leg_files`, `read_rows`, `sent_parts`, `comment_text`,
`comment_verdicts` — imported, the way `scripts/build_validate_pack.py` imports it, and the ONLY
reply parser anywhere below it is `market_pulse.prompts.parse_reply`. It is imported and not lifted
into `src/` on purpose: two sealed records (`results/window_summary_5c2.json`,
`results/validate_5c2_pack.json`) pin that file's sha256 in `producer.borrowed`, a lift would add a
KEY to that block, and no sha substitution rescues a key that is not there while `results/` is
frozen. `MOVED_BY_THE_SKIP` in `tests/test_window_summary_5c2.py` says the same thing from the other
end: a third file joining it is a day to look at, not to relax.

**Everything through a seal.** `config/registry.yaml` (the segment join and the watchlist) and
`results/census_5c2.json` (the window's anchor and its 28 days) are both read only after
`results/prereg_5c2_run.json`'s own pin agrees with the bytes on disk. A segment column computed
against a registry that moved since the run would be a join to a different set of channels.

**The database is not an artifact.** It is gitignored, rebuildable, and no number is ever typed
into it. What ships is the export (`scripts/export_dashboard_data.py`), and what proves the layer is
the convergence verdict this script prints: every numeric leaf of the sealed window summary,
re-derived from SQL. A disagreement is a refusal here, not a note in a report.

    PYTHONPATH=src python3 scripts/build_aggregates.py
    PYTHONPATH=src python3 scripts/build_aggregates.py --out /tmp/pulse.db --quiet
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import window_summary_5c2 as summary  # noqa: E402

from market_pulse import aggregates, brands, loop  # noqa: E402

DERIVED = REPO_ROOT / "data" / "derived"
PREREG = REPO_ROOT / "results" / "prereg_5c2_run.json"
CENSUS = REPO_ROOT / "results" / "census_5c2.json"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
ANCHOR = REPO_ROOT / "results" / "window_summary_5c2.json"
OUT = DERIVED / "pulse.db"

WINDOW_ID = "w1"
"""The first window's id. A NAME and not a date, because `windows.anchor` already carries the date
and a key that is also a fact drifts the day the anchor is re-cut."""

PINNED_CENSUS = "results/census_5c2.json"


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def through_the_seal(prereg: dict, path: Path, key: str) -> dict:
    """A pinned input's bytes, checked against the seal before anything reads them.

    `window_summary_5c2.registry_through_the_seal` is this rule for the registry and returns a
    `Registry`; this is the same rule for a JSON record, and both refuse rather than read.
    """
    pinned = prereg["pinned_inputs"][key]
    found = summary.sha256_of(path)
    if found != pinned:
        raise SystemExit(
            f"{rel(path)} hashes to {found[:16]}… and the sealed registration pins {pinned[:16]}…"
            " — the window this layer would aggregate is not the one the run was registered"
            " against. Stop and report."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def segments_of(registry) -> dict:
    """`@handle` → the source it belongs to and its audience segment, from the registry.

    A handle with no source is impossible by construction — the loop walks the registry to decide
    what to collect — so this map is total over anything the store can hold, and
    :func:`segment_for` refuses loudly if it ever is not.
    """
    return {
        handle: {
            "source_id": source.id,
            "source_type": source.source_type,
            "segment": source.audience,
        }
        for source in registry.sources
        for handle in source.telegram_channels
    }


def segment_for(segments: dict, channels: set) -> dict:
    unknown = sorted(channels - set(segments))
    if unknown:
        raise SystemExit(
            f"{unknown} carry evidence rows and no registry entry — SPEC 3.20 (1) fails loudly on a"
            " missing source rather than aggregating a channel with an empty segment column"
        )
    return {handle: segments[handle] for handle in sorted(channels)}


def build(derived: Path, prereg_path: Path, registry_path: Path, out: Path):
    """The database, and the sha256 of every file it was built from.

    The sources come back with the connection rather than being enumerated again by the export: two
    walks of the same directory are two answers to "what was read", and the one that ends up in
    `provenance` has to be the one the rows actually came from.
    """
    prereg = json.loads(summary.read_text_or_refuse(prereg_path))
    registry = summary.registry_through_the_seal(prereg, registry_path)
    census = through_the_seal(prereg, REPO_ROOT / PINNED_CENSUS, PINNED_CENSUS)
    aliases = brands.watchlist_aliases(registry.watchlist)
    sources: dict[str, str] = {}

    def load(record_type: str) -> list[dict]:
        rows: list[dict] = []
        for path in summary.leg_files(derived, record_type):
            sources[rel(path)] = summary.sha256_of(path)
            rows += summary.read_rows(path)
        return rows

    comments = load(loop.RECORD_TYPE)
    pages = load(loop.PAGE_RECORD_TYPE)
    posts = load(loop.POST_RECORD_TYPE)
    positions = load(loop.POSITION_RECORD_TYPE) + load(loop.POST_POSITION_RECORD_TYPE)

    verdicts = summary.comment_verdicts(comments, aliases)
    for verdict, row in zip(verdicts, comments, strict=True):
        verdict["task"] = row["task"]

    text_less = sum(1 for row in verdicts if row["empty_text"])
    populations = {
        kind: prereg["populations"][kind]["rows"]
        for kind in ("comment", "leaflet_page", "post_text")
    }

    everyone = segments_of(registry)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.unlink(missing_ok=True)
    conn = aggregates.connect(out)
    aggregates.add_window(
        conn,
        WINDOW_ID,
        census["anchor"],
        populations,
        {"payable": len(verdicts) - text_less, "text_less": text_less},
        {
            "channels": len(everyone),
            "segments": len({one["segment"] for one in everyone.values() if one["segment"]}),
        },
    )
    aggregates.add_channels(
        conn,
        WINDOW_ID,
        segment_for(everyone, {row["channel"] for row in comments + pages + posts + positions}),
    )
    aggregates.add_watchlist(conn, WINDOW_ID, list(registry.watchlist))
    aggregates.add_comments(conn, WINDOW_ID, verdicts)
    aggregates.add_markers(conn, WINDOW_ID, loop.CARRIER, pages)
    aggregates.add_markers(conn, WINDOW_ID, loop.POST_CARRIER, posts)
    aggregates.add_positions(conn, WINDOW_ID, positions)
    conn.commit()
    return conn, sources


def check_convergence(conn, anchor_path: Path) -> dict:
    """The gate: the sealed window summary's numbers, re-derived from the database.

    Refusing here rather than in the test is what SPEC 3.20 (1) asks of the build — a layer that
    disagrees with the record it was built beside must not leave an artifact behind for a dashboard
    to read.
    """
    anchor = json.loads(summary.read_text_or_refuse(anchor_path))
    verdict = aggregates.converge(anchor, aggregates.mirror(conn, WINDOW_ID))
    if verdict["disagreed"] or verdict["missing"]:
        raise SystemExit(
            f"the aggregate layer does not converge with {rel(anchor_path)}:"
            f" {len(verdict['disagreed'])} of {verdict['leaves']} numeric leaves disagree and"
            f" {len(verdict['missing'])} have no answer in the database —"
            f" {json.dumps(dict(list(verdict['disagreed'].items())[:5]), ensure_ascii=False)}"
            f" {verdict['missing'][:5]}"
        )
    return verdict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derived-root", type=Path, default=DERIVED)
    parser.add_argument("--prereg", type=Path, default=PREREG)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--anchor", type=Path, default=ANCHOR)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    conn, _ = build(args.derived_root, args.prereg, args.registry, args.out)
    verdict = check_convergence(conn, args.anchor)
    if args.quiet:
        return 0

    window = conn.execute(
        "SELECT anchor, days, bought, payable, text_less FROM windows WHERE window_id = ?",
        (WINDOW_ID,),
    ).fetchone()
    print(f"wrote {rel(args.out)}  window {WINDOW_ID}  anchor {window[0]}  {window[1]} days")
    print(f"  comments      {window[2]} bought · {window[3]} payable · {window[4]} text-less")
    for table in (
        "channels",
        "watchlist",
        "comments",
        "comment_intents",
        "comment_brands",
        "markers",
        "positions",
        "position_warnings",
    ):
        (rows,) = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        print(f"  {table:18s} {rows}")
    print(
        f"  convergence   {len(verdict['agreed'])}/{verdict['leaves']} numeric leaves of"
        f" {rel(args.anchor)} re-derived from SQL, 0 disagreed, 0 missing"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
