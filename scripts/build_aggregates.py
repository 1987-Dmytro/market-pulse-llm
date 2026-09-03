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
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import postcut_c3b  # noqa: E402
import run_loop  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import aggregates, brands, loop  # noqa: E402

DERIVED = REPO_ROOT / "data" / "derived"
LIVE = REPO_ROOT / "data" / "derived_w2"
"""The live derived root — `run_loop.LIVE_DERIVED_ROOT`, read from here.

Ruling 03.09 (b), fork 1: window 1's root is frozen at the bytes its seal hashed and window 2
writes beside it. Both roots are READ here and the rows are pooled, because a row belongs to a
window by that window's pinned population ids and by nothing else — the same law shape 1 wrote,
with the store no longer having to hold two populations in one file. The 20 D-cut posts answered
in BOTH windows stay in w1's root and w2 reads them from there."""
PREREG = REPO_ROOT / "results" / "prereg_5c2_run.json"
PREREG_C2 = REPO_ROOT / "results" / "prereg_promo_c2.json"
CENSUS = REPO_ROOT / "results" / "census_5c2.json"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
RULES = REPO_ROOT / "config" / "watchlist_rules.yaml"
ANCHOR = REPO_ROOT / "results" / "window_summary_5c2.json"
OUT = DERIVED / "pulse.db"

CARRIER = "comment"
"""Which text the revised matcher is told it is reading. SPEC 3.21 (1) scopes the `garmonija` rule
to comment text, and `find_watchlist_brands` refuses a revision without the carrier named — so this
constant is the layer saying out loud that the r1 cut it fills is the COMMENT cut and no other."""

WINDOW_ID = "w1"
"""The first window's id. A NAME and not a date, because `windows.anchor` already carries the date
and a key that is also a fact drifts the day the anchor is re-cut."""

WINDOW_ID_C2 = "w2"
"""The C2 window's id, as `results/prereg_promo_c2.json :: addendum[0].window_id` names it — ruling
02.09 (d) item 1. Read from the record rather than restated here would be one indirection for a
two-letter constant; the build ASSERTS the two agree instead ([[a_moved_constant_fails_green]])."""

PINNED_CENSUS = "results/census_5c2.json"
PINNED_POSTS = "results/census_c3a_posts.json"
PINNED_CUT = "results/postcut_c3b.json"
PINNED_CENSUS_C2 = "results/promo_census_c2.json"
PINNED_MANIFEST_C2 = "results/post_media_promo_c2.json"

POPULATIONS = ("comment", "leaflet_page", "post_text")
"""The three legs `windows` stores a bought-count for, in the order `add_window` reads them."""


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


def revised_hits(comments: list[dict], aliases: dict, rules) -> list[dict]:
    """The same rows, matched again under the named revision — SPEC 3.21 (1).

    Matched again rather than filtered down from the anchor's hits: a rule is a requirement on the
    TEXT, and a filter over `verdict["brands"]` would have to re-read that text anyway to check it.
    Both passes read `summary.comment_text`, so the two tables differ in the rules and in nothing
    else — which is the whole claim the anchor-parity split rests on.
    """
    return [
        {
            "channel": row["channel"],
            "msg_id": row["msg_id"],
            "brands": [
                found["brand_id"]
                for found in brands.find_watchlist_brands(
                    summary.comment_text(row), aliases, rules, carrier=CARRIER
                )
            ],
        }
        for row in comments
    ]


# --- which rows are which window's ---------------------------------------------------------------


def manifest_pages(manifest: dict) -> set[tuple[str, str]]:
    """(channel, page msg_id) for every page a media manifest names — `run_loop.pages_of`'s answer.

    The loop's own reader rather than a second walk of `entries`: these are the pages the run was
    built from, album members and skipped-because-absent files included, and a private re-walk here
    would be a second opinion about a population that is already registered
    ([[trace_the_producer_not_the_result]]).
    """
    handles = {entry["channel"] for entry in manifest["entries"].values()}
    return {
        (page["channel"], str(page["msg_id"]))
        for handle in sorted(handles)
        for page in run_loop.pages_of(manifest, handle)
    }


def refuse_unless(name: str, got: set, total: int) -> set:
    """A derived id set against the count its seal registered. A short set is a silent window."""
    if len(got) != total:
        raise SystemExit(
            f"{name}: the seal registers {total} rows and its own pinned inputs derive {len(got)}"
            " — the window this layer would build is not the one that was bought. Stop and report."
        )
    return got


def selection_5c2(prereg: dict) -> dict[str, set]:
    """The 5c2 window's rows, by id, out of its own seal — 159 pages, 44 posts, every comment.

    Pages come from the media manifest the registration pins by path AND sha (`selection_pin`).
    Posts are the D cut RE-COMPUTED from the pinned census and checked against
    `results/postcut_c3b.json :: kept.ids_sha256`, because that record keeps the cut's ids only as
    a hash: the cut is a pure filter over sealed bytes, and the pin is what says the filter still
    answers what the run bought. `comment` is None and not a set — 5c2 bought every comment row in
    the store and C2 bought none, so an id set there would be 5 075 ids written down to say "all".
    """
    pin = prereg["populations"]["leaflet_page"]["selection_pin"]
    manifest = through_the_seal(
        {"pinned_inputs": {pin["path"]: pin["sha256"]}}, REPO_ROOT / pin["path"], pin["path"]
    )
    posts_census = through_the_seal(prereg, REPO_ROOT / PINNED_POSTS, PINNED_POSTS)
    cut = through_the_seal(prereg, REPO_ROOT / PINNED_CUT, PINNED_CUT)
    types = {row["handle"]: row["source_type"] for row in posts_census["channels"]}
    kept = [
        row for row in posts_census["rows"] if postcut_c3b.kept_by(row, types[row["channel"]])
    ]
    found = postcut_c3b.ids_sha256(kept)
    if found != cut["kept"]["ids_sha256"]:
        raise SystemExit(
            f"the D cut re-computed from {PINNED_POSTS} hashes to {found[:16]}… and"
            f" {PINNED_CUT} pins {cut['kept']['ids_sha256'][:16]}… — the 44 posts this window"
            " would claim are not the 44 it bought. Stop and report."
        )
    return {
        "leaflet_page": refuse_unless(
            "w1 leaflet_page", manifest_pages(manifest), prereg["populations"]["leaflet_page"]["rows"]
        ),
        "post_text": refuse_unless(
            "w1 post_text",
            {(row["channel"], row["id"].rsplit(":", 1)[-1]) for row in kept},
            prereg["populations"]["post_text"]["rows"],
        ),
        "comment": None,
    }


def selection_c2(prereg: dict) -> dict[str, set]:
    """The C2 window's rows, by id, out of `results/prereg_promo_c2.json` — 3 008 pages, 405 posts.

    Both halves come back through that registration's OWN pinned inputs: the media manifest for the
    pages and the census's `text_price_msg_ids` for the posts. The 20 posts 5c2's D cut had already
    answered are in BOTH windows' sets and that is the ruling's answer — one position row, two
    windows, `window_id` a key of the aggregate tables and never of the row's identity.
    """
    manifest = through_the_seal(prereg, REPO_ROOT / PINNED_MANIFEST_C2, PINNED_MANIFEST_C2)
    census = through_the_seal(prereg, REPO_ROOT / PINNED_CENSUS_C2, PINNED_CENSUS_C2)
    return {
        "leaflet_page": refuse_unless(
            "w2 leaflet_page", manifest_pages(manifest), prereg["population"]["pages"]["total"]
        ),
        "post_text": refuse_unless(
            "w2 post_text",
            {
                (entry["channel"], str(one))
                for entry in census["channels"]
                for one in entry["text_price_msg_ids"]
            },
            prereg["population"]["posts"]["total"],
        ),
        "comment": set(),
    }


def keep(rows: list[dict], ids: set | None) -> list[dict]:
    """The rows of one leg that belong to one window. `None` = the whole leg."""
    if ids is None:
        return rows
    return [row for row in rows if (row["channel"], str(row["msg_id"])) in ids]


def c2_anchor(census: dict) -> dict:
    """The C2 census's window in the shape `windows` stores. `until` IS the anchor: the census's own
    rule is «since <= date < anchor, half-open», so a second date would be a second definition."""
    window = census["window"]
    return {
        "anchor": window["anchor"],
        "days": window["days"],
        "since": window["since"],
        "until": window["anchor"],
    }


def build(derived: Path, prereg_path: Path, registry_path: Path, out: Path, live: Path = LIVE):
    """The database, and the sha256 of every file it was built from.

    TWO windows into the one database, each through ITS OWN seal — ruling 02.09 (d), shape 1. The
    store holds both populations because C2 appended to the same per-channel files, so a row belongs
    to a window by that window's PINNED POPULATION IDS and by nothing else: no live-registry read,
    no date arithmetic, no provenance field. `segment_for` keeps its law per window, against the
    registry that window was registered under (5c2 → r1, C2 → r2).

    The sources come back with the connection rather than being enumerated again by the export: two
    walks of the same directory are two answers to "what was read", and the one that ends up in
    `provenance` has to be the one the rows actually came from.
    """
    prereg = json.loads(summary.read_text_or_refuse(prereg_path))
    prereg_c2 = json.loads(summary.read_text_or_refuse(PREREG_C2))
    named = prereg_c2["addendum"][0]["window_id"]
    if named != WINDOW_ID_C2:
        raise SystemExit(
            f"{rel(PREREG_C2)} names window {named!r} and this layer builds {WINDOW_ID_C2!r} —"
            " the registration and the build disagree about which window was bought"
        )
    registry = summary.registry_through_the_seal(prereg, registry_path)
    registry_c2 = summary.registry_through_the_seal(prereg_c2, registry_path)
    census = through_the_seal(prereg, REPO_ROOT / PINNED_CENSUS, PINNED_CENSUS)
    census_c2 = through_the_seal(prereg_c2, REPO_ROOT / PINNED_CENSUS_C2, PINNED_CENSUS_C2)
    rules = brands.load_watchlist_rules(RULES)
    # the rules file is an INPUT to the r1 table and belongs in the same block as the evidence: the
    # export's provenance answers "what bytes made this record", and a matcher revision is bytes.
    sources: dict[str, str] = {rel(RULES): summary.sha256_of(RULES)}

    def load(record_type: str) -> list[dict]:
        """Both roots, w1's first. Only w1's files enter `sources`.

        `sources` is what the w1 export's `provenance.evidence` says made THAT record, so it names
        the sealed root's files and nothing else: no leaf of window 1 is computed from a byte the
        live root holds. A live leg that is silently absent is not caught here — `refuse_unless` holds
        each window's derived id set against the count its own seal registered, which is where a
        short window has always been refused.
        """
        rows: list[dict] = []
        for path in summary.leg_files(derived, record_type):
            sources[rel(path)] = summary.sha256_of(path)
            rows += summary.read_rows(path)
        folder = live / f"{record_type}s"
        for path in sorted(folder.glob("*.jsonl")) if folder.is_dir() else ():
            rows += summary.read_rows(path)
        return rows

    comments = load(loop.RECORD_TYPE)
    pages = load(loop.PAGE_RECORD_TYPE)
    posts = load(loop.POST_RECORD_TYPE)
    page_positions = load(loop.POSITION_RECORD_TYPE)
    post_positions = load(loop.POST_POSITION_RECORD_TYPE)

    out.parent.mkdir(parents=True, exist_ok=True)
    conn = aggregates.connect(":memory:")
    for window_id, seal, reg, selection, anchor, populations in (
        (
            WINDOW_ID,
            prereg,
            registry,
            selection_5c2(prereg),
            census["anchor"],
            {kind: prereg["populations"][kind]["rows"] for kind in POPULATIONS},
        ),
        (
            WINDOW_ID_C2,
            prereg_c2,
            registry_c2,
            selection_c2(prereg_c2),
            c2_anchor(census_c2),
            {
                "comment": 0,
                "leaflet_page": prereg_c2["population"]["pages"]["total"],
                "post_text": prereg_c2["population"]["posts"]["total"],
            },
        ),
    ):
        del seal
        aliases = brands.watchlist_aliases(reg.watchlist)
        mine = {kind: keep(rows, selection[kind]) for kind, rows in (
            ("comment", comments), ("leaflet_page", pages), ("post_text", posts)
        )}
        mine["page_position"] = keep(page_positions, selection["leaflet_page"])
        mine["post_position"] = keep(post_positions, selection["post_text"])

        verdicts = summary.comment_verdicts(mine["comment"], aliases)
        for verdict, row in zip(verdicts, mine["comment"], strict=True):
            verdict["task"] = row["task"]
        text_less = sum(1 for row in verdicts if row["empty_text"])

        everyone = segments_of(reg)
        aggregates.add_window(
            conn,
            window_id,
            anchor,
            populations,
            {"payable": len(verdicts) - text_less, "text_less": text_less},
            len(everyone),
        )
        touched = {
            row["channel"]
            for kind in ("comment", "leaflet_page", "post_text", "page_position", "post_position")
            for row in mine[kind]
        }
        aggregates.add_channels(conn, window_id, segment_for(everyone, touched))
        aggregates.add_segments(conn, window_id, everyone)
        aggregates.add_watchlist(conn, window_id, list(reg.watchlist))
        aggregates.add_comments(conn, window_id, verdicts)
        aggregates.add_revised_brands(
            conn,
            window_id,
            {"revision": rules.revision, "dated": rules.dated, "sha256": summary.sha256_of(RULES)},
            revised_hits(mine["comment"], aliases, rules),
        )
        aggregates.add_markers(conn, window_id, loop.CARRIER, mine["leaflet_page"])
        aggregates.add_markers(conn, window_id, loop.POST_CARRIER, mine["post_text"])
        aggregates.add_positions(conn, window_id, mine["page_position"] + mine["post_position"])
    conn.commit()
    return conn, sources


def settle(conn, out: Path) -> None:
    """The built database onto disk, AFTER every gate has passed.

    The old order unlinked `out` and built into it, so a correct refusal left an EMPTY file where a
    dashboard reads ([[a_rebuild_deletes_its_output_before_it_can_refuse]] — it happened, 02.09).
    Building in memory and backing up at the end means a refusal leaves yesterday's database alone.
    """
    out.unlink(missing_ok=True)
    target = sqlite3.connect(out)
    with target:
        conn.backup(target)
    target.close()


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
    parser.add_argument("--live-root", type=Path, default=LIVE)
    parser.add_argument("--prereg", type=Path, default=PREREG)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--anchor", type=Path, default=ANCHOR)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    conn, _ = build(args.derived_root, args.prereg, args.registry, args.out, args.live_root)
    verdict = check_convergence(conn, args.anchor)
    settle(conn, args.out)
    if args.quiet:
        return 0

    for window_id in (WINDOW_ID, WINDOW_ID_C2):
        window = conn.execute(
            "SELECT anchor, days, bought, payable, text_less FROM windows WHERE window_id = ?",
            (window_id,),
        ).fetchone()
        print(
            f"wrote {rel(args.out)}  window {window_id}  anchor {window[0][:10]}  {window[1]} days"
        )
        print(f"  comments      {window[2]} bought · {window[3]} payable · {window[4]} text-less")
        for table in (
            "channels",
            "segments",
            "watchlist",
            "comments",
            "comment_intents",
            "comment_brands",
            "comment_brands_r1",
            "markers",
            "positions",
            "position_warnings",
        ):
            (rows,) = conn.execute(
                f"SELECT COUNT(*) FROM {table} WHERE window_id = ?", (window_id,)
            ).fetchone()
            print(f"  {table:18s} {rows}")
    print(
        f"  convergence   {len(verdict['agreed'])}/{verdict['leaves']} numeric leaves of"
        f" {rel(args.anchor)} re-derived from SQL, 0 disagreed, 0 missing"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
