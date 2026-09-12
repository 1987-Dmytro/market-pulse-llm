#!/usr/bin/env python3
"""The React app's data, from result files ($0) — `results/front_data.json` (PHASE-ship-1 §2).

    PYTHONPATH=src python3.11 scripts/export_front_data.py
    PYTHONPATH=src python3.11 scripts/export_front_data.py --stage dashboard/app/data

**Every field is a field of a file this export names, and nothing here computes a figure.** The
command centre is `results/dashboard_data_w1.json` carried VERBATIM; the three readings beside it
come from `build_dashboard.conclusions` — the rule the static page renders, CALLED, so a reading
that generates prose from figures has one spelling (PHASE-ship-1 §3); the S2 rows come from
`build_promo_screen.s2_readings`, the same reader the README and the promo screen print; S1 is the
grader's own record. The app formats, filters, sorts and links what is written here.

**A missing REQUIRED source is a named, non-zero exit.** The app renders a red panel naming the
file, and this producer writes no partial export: a blank where a number belongs reads as «none in
the market», which is a claim ([[the_empty_row_is_the_answer]]). The optional source — the S1 grade
— arrives as `reading: null` beside the sentence that says which file would carry it.

**No clock.** This export is committed and `git status --porcelain results` must print nothing
after `make front` (§8), so a generation timestamp here would dirty the tree on every build. The
freshness the header can honestly show is the DATA's own: `data_until` is the newest window
boundary the screen export carries. The last tick IS a clock and lives one file over, in
`results/promo_tick.json`, which is gitignored — `GET /api/status` carries it in served mode, and
`status.tick` here is null beside that sentence.

**And no disk.** The `media` block of DESIGN §11 is joined out of the post-media RECORDS, never out
of what `data/annotation/` happens to hold: the photos are gitignored, so a builder that listed the
files it could see would write a different export on a clean clone and dirty `results/` on every
build. `--stage` is the one step that touches the images — it copies what it finds and REPORTS
`referenced · staged · missing`, because a clone with no photos must still build the app.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_dashboard as builder  # noqa: E402
import build_promo_screen as screen  # noqa: E402
import runpod_guard as guard  # noqa: E402
import tick  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import registry, trends  # noqa: E402

OUT = screen.RESULTS / "front_data.json"
VERDICT = screen.RESULTS / "verdict_45h2.json"
GRADE = screen.RESULTS / "grade_positions_50.json"
DRAW = screen.RESULTS / "positions_draw_50.json"

MEDIA_GLOB = "post_media_*.json"
"""The post-media records, by GLOB and not by a list of the five that exist today: the next paid
leg writes a sixth, and a join closed by enumeration would drop that leg's pages without a word
([[a_patch_list_closed_by_enumeration]])."""

MEDIA_DIR = "media"
"""Where `--stage` puts the photos, beside the `data/` it is pointed at — `dashboard/app/media/`."""

CONTRACT = (
    "docs/DESIGN-ship-1.md §7 — written by scripts/export_front_data.py ($0) from the files each"
    " block names; the app computes no figure of its own"
)

APP_FILES = (OUT, screen.EXPORT)
"""What the adapters fetch: this export and the promo screen's own. `--stage` copies exactly these
into the static build's `data/` beside a manifest of their shas — the served mode reads the same two
through `GET /api/exports/{name}`, so one list answers both modes."""


def required() -> tuple[Path, ...]:
    """Every file this export MUST read. Computed on the call rather than frozen at import: the
    money ledger's path follows the ledger it succeeds (`guard.cycle3_path`), and a constant read
    once at import would keep pointing at whichever file that was then
    ([[a_default_argument_freezes_the_constant_it_names]])."""
    return (
        screen.EXPORT,
        builder.EXPORT,
        VERDICT,
        guard.cycle3_path(),
        builder.METRICS,
        builder.STRINGS,
        tick.REGISTRY,
        registry.CHAIN_ALIASES,
        *media_manifests(),
        *(screen.RESULTS / name for name in screen.S2_FILES),
    )


def optional() -> tuple[Path, ...]:
    """The S1 grade and the draw it was read over — absent until «s1-grade» lands its file."""
    return (GRADE, DRAW)


def refuse_on_a_missing_source(paths: tuple[Path, ...]) -> None:
    missing = [tick.rel(path) for path in paths if not path.exists()]
    if missing:
        raise SystemExit(
            "export-front REFUSED: missing required source(s) "
            + ", ".join(missing)
            + " — the app names a missing file in a red panel and this producer writes no partial"
            " export rather than a blank where a figure belongs"
        )


def digest(path: Path) -> dict:
    return {"sha256": summary.sha256_of(path), "bytes": path.stat().st_size}


def money_reading(ledger: dict, label: str) -> dict:
    """The cycle's remaining, as the guard last RECORDED it — a reading of a file, not a balance.

    The last session row of the guard's own ledger, its fields carried over as they were written.
    Nothing is re-computed from a cap and a spend: the guard is the one place that prices a line,
    and a second spelling of that arithmetic is a defect ([[a_published_number_has_one_reader]]).
    `scripts/serve.py` reads the live status through this same function, so the served and the
    static screens cannot disagree about the money they display.
    """
    last = ledger["sessions"][-1]
    return {
        "from": f"{label} :: sessions[-1]",
        "remaining_usd": last["remaining_usd"],
        "spent_usd": last["spent_usd"],
        "cap_usd": ledger["cycle3_cap_usd"],
        "at": last["at"],
        "note": last["note"],
    }


def status(export: dict, ledger: dict, ledger_label: str) -> dict:
    """The status line's fields — the shape `GET /api/status` answers with, from committed files.

    ONE spelling of that shape: `serve.py` calls this and then overrides `tick` with the state file
    it can see and `windows` with the store's own rows when a store is there. The queue is the
    export's own `screen.threads` (ruling 10.09 (qq) 6) and never the tick's «cooled and not yet
    read», which counts threads of channels the product does not read.
    """
    return {
        "tick": {
            "at": None,
            "why": f"{tick.rel(tick.STATE)} is the tick's own clock and is not committed —"
            " `GET /api/status` carries the last tick in served mode",
        },
        "threads": export["screen"]["threads"],
        "table_rows": export["screen"]["table_rows"],
        "money": money_reading(ledger, ledger_label),
        "window_id": export["window_id"],
        "from": f"{tick.rel(screen.EXPORT)} :: windows",
        "windows": export["windows"],
    }


def chains() -> dict:
    """The chains the app NAMES and colours, in the registry's own order, folded like the screen.

    `chain.id` on a position row is a registry id folded by `aggregates.chain_key`, and the export
    carries no display name for it — so «marketopt_promo» would be what the operator reads in a
    table and a legend. The names come from `config/registry.yaml` through its own loader and the
    fold from `chain_aliases.yaml` through `registry.chain_of_channel`, the same two files the
    screen folded by: a label typed into the app would be a second spelling of a name the registry
    already holds, and the first revision of it would leave the app lying ([[a_fold_is_not_a_membership_test]]).

    Order is first appearance in the registry (DESIGN-ship-1 §3: the series slot follows the
    entity, assigned once), and the row that NAMES a folded chain is the chain's own — a second
    channel of one retailer must not lend the pair its name.
    """
    folds = registry.chain_of_channel()
    table: dict[str, dict] = {}
    for source in registry.load_registry(tick.REGISTRY).sources:
        if not source.collect:
            continue
        chain_id = folds.get(source.id, source.id)
        row = table.setdefault(
            chain_id, {"id": chain_id, "name": source.name, "source_type": source.source_type}
        )
        if source.id == chain_id:
            row |= {"name": source.name, "source_type": source.source_type}
    return {
        "from": f"{tick.rel(tick.REGISTRY)} :: sources[] where collect (id, name, source_type),"
        " folded by config/chain_aliases.yaml :: chain_of_channel",
        "reading": "the sources the registry is COLLECTING, which is the set a position row's"
        " chain can be — a chain the app meets outside this table keeps the export's own id",
        "rows": list(table.values()),
    }


def data_until(export: dict) -> dict:
    """The newest window boundary the screen export carries — the data's own freshness.

    Compared on the DATE, because the boundaries come in two spellings: w1's anchor and bounds are
    ISO datetimes and w2/w3's are dates (each seal's own wording, ruling 10.09 (ss) 3). The day is
    what both carry, so the day is what is compared and what is published; no source is rewritten.
    """
    return {
        "date": max(window["until"][:10] for window in export["windows"]),
        "from": f"{tick.rel(screen.EXPORT)} :: windows[].until (by date — w1 is a datetime)",
    }


def media_manifests() -> tuple[Path, ...]:
    """Every post-media record in `results/`, in name order — the order that breaks a tie below."""
    return tuple(sorted(screen.RESULTS.glob(MEDIA_GLOB)))


def media_index(manifests: tuple[Path, ...]) -> dict[tuple[str, int], dict]:
    """`(channel, page msg_id)` → the page's photo, from the records the fetchers wrote.

    A leaflet page IS a message: the album's images carry their own `msg_id`, which is the id a
    position row's evidence points at, so the join is on the IMAGE's id and not on the post's. Two
    collections can hold one page (C2 re-fetched what 5c1 already had) — 63 of them do, and no
    basename in the five records maps to two different sha256s, so the first record by name wins
    and the staged name stays the file's own. The one tie that is NOT broken by name: a record that
    carries no `date` for its post loses to one that does, whatever their names — the dateless entry
    would keep the page out of every flyer set, and two of the five records are dateless throughout.
    """
    index: dict[tuple[str, int], dict] = {}
    for path in manifests:
        record = json.loads(path.read_text(encoding="utf-8"))
        for entry in (record.get("entries") or {}).values():
            for image in entry.get("images") or []:
                key = (entry["channel"], image["msg_id"])
                seen = index.get(key)
                if seen is not None and not (seen["date"] is None and entry.get("date")):
                    continue
                index[key] = {
                    "file": image["file"],
                    "name": Path(image["file"]).name,
                    "bytes": image["bytes"],
                    "date": entry.get("date"),
                    "from": tick.rel(path),
                }
    return index


def media(export: dict, manifests: tuple[Path, ...]) -> dict:
    """The photos the screen shows: a page per position row, and the newest flyer set per chain.

    DESIGN-ship-1 §11. Three readings, one join — `(channel, msg_id)` from a row's evidence into
    the post-media records:

    * `pages` — the staged NAME of the row's own source page, so a table row can show it and open
      it. A row whose page no record carries is simply absent from this map and the table prints
      its absent marker: 25 of the 1 301 rows are post text whose own post NO record covers — the
      channels have thousands of photos between them, it is those posts that were never asked
      about — and a zero-size thumbnail would read as «no leaflet», which is a claim.
    * `flyers` — per chain, the newest week that chain has pages in, with the dates the pages carry.
      The CURRENT week is per CHAIN and not one global week: the newest week over all chains is
      Маркетопт's alone (its leg ran last), and a gallery of one card is not «one card per chain».
      Each card therefore prints its own dates. Its `pages` are the pages of that week a tracked
      position was read off — NOT the leaflet issue, which runs to pages of meat and detergent this
      product never opened — so the card says «N стор. з позиціями» and the cover is the first of
      those pages, in the channel's own message order.
    * `files` — the staging list, and the ONLY list `--stage` copies from: what the app can
      reference and what the build copies are one set by construction, not two that agree today.
    """
    index = media_index(manifests)
    rows = export["screen"]["positions"]

    pages: dict[str, str] = {}
    referenced: dict[str, dict] = {}
    sets: dict[tuple[str, str], dict] = {}
    undated = 0
    pageless = 0
    for row in rows:
        key = (row["evidence"]["channel"], row["evidence"]["msg_id"])
        page = index.get(key)
        if page is None:
            # counted on the ROW, not on the map: a page carries many rows, and 1 301 − 402 would
            # be the pages a row shares with its neighbours, not the rows that have none
            pageless += 1
            continue
        pages[f"{key[0]}:{key[1]}"] = page["name"]
        referenced[page["name"]] = page
        if page["date"] is None:
            undated += 1
            continue
        week = trends.iso_week(page["date"])
        flyer = sets.setdefault(
            (row["chain"]["id"], week),
            {"chain": row["chain"]["id"], "week": week, "names": {}, "positions": 0, "dates": []},
        )
        flyer["positions"] += 1
        if page["name"] not in flyer["names"]:
            flyer["names"][page["name"]] = key[1]
            flyer["dates"].append(page["date"][:10])

    flyers = []
    for chain in sorted({chain for chain, _ in sets}):
        newest = max(week for one, week in sets if one == chain)
        flyer = sets[(chain, newest)]
        # message order is page order, so the cover is the first page of the week THIS product read
        names = [name for name, _ in sorted(flyer["names"].items(), key=lambda pair: pair[1])]
        flyers.append(
            {
                "chain": chain,
                "week": newest,
                "since": min(flyer["dates"]),
                "until": max(flyer["dates"]),
                "pages": names,
                "positions": flyer["positions"],
                "cover": names[0],
            }
        )

    return {
        "from": f"{', '.join(tick.rel(path) for path in manifests)} :: entries[].images[], joined to"
        f" {tick.rel(screen.EXPORT)} :: screen.positions[].evidence on (channel, msg_id)",
        "reading": "the page a position was read off, and per chain the newest week that chain has"
        " pages in — the week is the ISO week of the page's own date through trends.iso_week, and a"
        " flyer set is the pages of that week this product read a position off, not the whole issue",
        "dir": MEDIA_DIR,
        "pages": pages,
        "flyers": flyers,
        "files": [
            {"name": name, "file": referenced[name]["file"], "bytes": referenced[name]["bytes"]}
            for name in sorted(referenced)
        ],
        "rows_without_a_page": pageless,
        "pages_without_a_date": undated,
    }


def s1_reading() -> dict:
    """The S1 bar as `scripts/grade_positions.py` recorded it, over the draw it was read on.

    `reading: null` beside the sentence naming the file, never a zero: an unread bar and a bar read
    as zero are different states and only one of them is a measurement.
    """
    if not GRADE.exists() or not DRAW.exists():
        return {
            "from": tick.rel(GRADE),
            "reading": None,
            "why": f"{tick.rel(GRADE)} is written by `scripts/grade_positions.py` over"
            f" {tick.rel(DRAW)}; one of the two is not in this checkout",
        }
    drawn = json.loads(DRAW.read_text(encoding="utf-8"))
    return {
        "from": tick.rel(GRADE),
        "reading": json.loads(GRADE.read_text(encoding="utf-8")),
        "draw": {
            "from": tick.rel(DRAW),
            "pages": drawn["pages_drawn_from"],
            "population": drawn["population"],
            "rows_drawn": drawn["rows_drawn"],
            "seed": drawn["seed"],
        },
    }


def build(export_path: Path = OUT) -> dict:
    """The whole document, from the sources `required()` and `optional()` name."""
    refuse_on_a_missing_source(required())
    manifests = media_manifests()
    if not manifests:
        raise SystemExit(
            f"export-front REFUSED: no {tick.rel(screen.RESULTS)}/{MEDIA_GLOB} — the flyer gallery"
            " of DESIGN §11 is joined out of the post-media records, and a screen with no photos"
            " and no sentence would read as «the chains printed none»"
        )
    ledger_path = guard.cycle3_path()

    promo = json.loads(screen.EXPORT.read_text(encoding="utf-8"))
    centre = json.loads(builder.EXPORT.read_text(encoding="utf-8"))
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    if not ledger.get("sessions"):
        raise SystemExit(
            f"export-front REFUSED: {tick.rel(ledger_path)} carries no recorded reading — the"
            " money on the screen is a recorded line or it is not shown"
        )

    # the dictionary the app renders, held against the command centre's own pin for it: the
    # definitions beside a figure must be the definitions that figure was computed under
    builder.through_the_provenance(centre, "inputs", "config/metrics.yaml", builder.METRICS)
    dictionary = yaml.safe_load(builder.METRICS.read_text(encoding="utf-8"))
    strings = builder.Strings(builder.STRINGS)

    document = {
        "contract": CONTRACT,
        "chains": chains(),
        "data_until": data_until(promo),
        "command_center": centre | {"conclusions": builder.conclusions(centre, strings)},
        "model": {
            "from": tick.rel(VERDICT),
            "verdict": json.loads(VERDICT.read_text(encoding="utf-8")),
        },
        "media": media(promo, manifests),
        "s2_readings": screen.s2_readings(screen.RESULTS),
        "s2_boundary": screen.S2_BOUNDARY,
        "s1_reading": s1_reading(),
        "status": status(promo, ledger, tick.rel(ledger_path)),
        "dictionary": {
            "from": tick.rel(builder.METRICS),
            "sha256": summary.sha256_of(builder.METRICS),
            "metrics": dictionary["metrics"],
        },
        "sources": {
            tick.rel(path): digest(path)
            for path in (*required(), *(one for one in optional() if one.exists()))
        },
    }
    # the export does not list ITSELF: a file cannot carry its own sha256, and the static build's
    # `data/manifest.json` hashes it from outside ([[provenance_cannot_name_itself]])
    return document


def stage_media(document: dict, target: Path) -> dict:
    """The referenced photos into `dashboard/app/media/` — ONLY those, and never a refusal.

    The list is the export's own `media.files`, so the set the app can reference and the set the
    build copies are one set by construction. The images are gitignored, so a clean clone has none
    of them: a missing photo is COUNTED and named, and the build goes on — refusing here would be a
    build that cannot run on the clone `e2e-ship` runs it on. The export cannot be narrowed to what
    was found instead, or it would differ between checkouts and dirty `results/` on every build; the
    app carries the other half of that bargain and renders «no page» when an `<img>` does not load.
    """
    files = document["media"]["files"]
    target.mkdir(parents=True, exist_ok=True)
    staged, missing, size = [], [], 0
    for row in files:
        source = REPO_ROOT / row["file"]
        if not source.is_file():
            missing.append(row["file"])
            continue
        shutil.copyfile(source, target / row["name"])
        staged.append(row["name"])
        size += row["bytes"]
    return {
        "dir": target.name,
        "referenced": len(files),
        "staged": len(staged),
        "missing": len(missing),
        "bytes": size,
        "missing_files": missing[:10],
        "why": "the photos under data/annotation/ are gitignored, so a checkout without them stages"
        " none: the app builds, and a thumbnail whose file did not arrive falls back to the same"
        " «no page» the export's own pageless rows show — this count is how many did not arrive",
    }


def stage(target: Path) -> tuple[list[dict], dict]:
    """The static build's `data/`: the two files the adapters fetch, and a manifest of their shas.

    Run AFTER `vite build`, which empties its own output directory — a copy staged before the build
    is a copy the build deletes. The photos go one directory over, into `<target>/../media/`, which
    is `dashboard/app/media/` for the build the Makefile runs.
    """
    refuse_on_a_missing_source(APP_FILES)
    target.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in APP_FILES:
        shutil.copyfile(path, target / path.name)
        rows.append({"file": path.name, **digest(path)})
    document = json.loads(OUT.read_text(encoding="utf-8"))
    photos = stage_media(document, target.parent / MEDIA_DIR)
    manifest = {
        "contract": CONTRACT,
        "data_until": document["data_until"],
        "files": rows,
        "media": photos,
    }
    (target / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    return rows, photos


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument(
        "--stage",
        type=Path,
        help="copy the app's data files and a manifest of their shas into this directory, after"
        " `vite build` has written the rest of dashboard/app/",
    )
    args = parser.parse_args(argv)

    if args.stage is not None:
        rows, photos = stage(args.stage)
        for row in rows:
            print(f"  staged {row['file']}  {row['sha256'][:16]}…  {row['bytes'] / 1024:.0f} KB")
        print(
            f"  media  referenced {photos['referenced']} · staged {photos['staged']} · missing"
            f" {photos['missing']} · {photos['bytes'] / 1e6:.1f} MB → {tick.rel(args.stage.parent / MEDIA_DIR)}/"
        )
        print(f"wrote {tick.rel(args.stage / 'manifest.json')}")
        return 0

    document = build(args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {tick.rel(args.out)}  {args.out.stat().st_size / 1024:.0f} KB")
    print(f"  data until    {document['data_until']['date']}")
    print(f"  conclusions   {len(document['command_center']['conclusions'])}")
    print(f"  s2 readings   {len(document['s2_readings'])}")
    print(f"  chains        {len(document['chains']['rows'])}")
    print(
        f"  media         {len(document['media']['files'])} pages · {len(document['media']['flyers'])}"
        f" flyer sets · {document['media']['rows_without_a_page']} rows without a page"
    )
    print(f"  s1 reading    {'read' if document['s1_reading']['reading'] else 'absent'}")
    print(f"  sources       {len(document['sources'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
