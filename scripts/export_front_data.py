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

from market_pulse import aggregates, registry, trends  # noqa: E402

OUT = screen.RESULTS / "front_data.json"
REGIONS = REPO_ROOT / "config" / "chain_regions.yaml"
CORRECTIONS = REPO_ROOT / "config" / "price_corrections.yaml"
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
        REGIONS,
        CORRECTIONS,
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

    `by_channel` is the same fold read from the other side: a TELEGRAM HANDLE to the chain id the
    rows above name. The screen's two blocks key on two different id spaces — `positions[].chain.id`
    is a folded registry id and `rollup[].chain` is the raw handle — so the Тренди tab had no way to
    put «Маркетопт» on a bar and printed `+Ejz6ubzm21IyMTQy` instead. The lookup belongs here beside
    the names it resolves to; the app reads a label out of it and folds nothing of its own.
    """
    folds = registry.chain_of_channel()
    table: dict[str, dict] = {}
    by_channel: dict[str, str] = {}
    for source in registry.load_registry(tick.REGISTRY).sources:
        if not source.collect:
            continue
        chain_id = folds.get(source.id, source.id)
        row = table.setdefault(
            chain_id, {"id": chain_id, "name": source.name, "source_type": source.source_type}
        )
        if source.id == chain_id:
            row |= {"name": source.name, "source_type": source.source_type}
        for handle in source.telegram_channels or ():
            by_channel[handle] = chain_id
    return {
        "from": f"{tick.rel(tick.REGISTRY)} :: sources[] where collect (id, name, source_type),"
        " folded by config/chain_aliases.yaml :: chain_of_channel",
        "reading": "the sources the registry is COLLECTING, which is the set a position row's"
        " chain can be — a chain the app meets outside this table keeps the export's own id",
        "rows": list(table.values()),
        "by_channel": dict(sorted(by_channel.items())),
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


PAGE_TRUE_FIELDS = ("promo_price", "size_value")
"""The two figures a correction may carry: the price the tag prints and the size printed beside it —
the two the unit price is computed from. `promo_price` sits on the row and `size_value` inside its
`item`, which is why the two are applied by name below and not by a loop over a field map."""

ENTRY_FIELDS = frozenset(
    {"row_id", "carrier", "page", "reads", "verified_by", "exclude", *PAGE_TRUE_FIELDS}
)
"""Every key an entry of the record may carry. A key outside this set is a REFUSAL and not a key
ignored: a hand-written record whose typo applies nothing would leave the screen publishing the
figure a human already read off the page and corrected ([[a_patch_list_closed_by_enumeration]])."""


def refuse_on_the_record(reason: str) -> None:
    raise SystemExit(
        f"export-front REFUSED: {tick.rel(CORRECTIONS)} {reason} — the record names rows one by one"
        " and a row it names that this export does not carry is a correction that silently did not"
        " happen, which is the defect the record exists to close"
    )


def excluded_from_prices(position: dict) -> str | None:
    """Why this row may carry no price at all — the readers' own sentence, or `None`.

    The two rows it answers for were read off pages that print NO price: the figure in the store was
    invented whole, and there is no page-true number to put in its place. They stay in the window's
    population and are counted on the block that drops them, because a row that quietly disappears
    is a population that moved without a sentence ([[stop_collecting_is_not_delete_the_row]]).
    """
    return (position.get("correction") or {}).get("exclude")


def page_true(positions: list[dict], table: dict) -> list[dict]:
    """The rows as their own leaflet page prints them — `config/price_corrections.yaml`, applied ONCE.

    Ruling (yy) 13.09 option (c). The «price-fix» reading measured the deterministic layers clean and
    found eight rows on six pages whose figure the page contradicts: the model misread a photograph,
    so the repair is a human reading written down, not code. This is the one place it is applied —
    between the screen export and every block this file writes — so a corrected row reads the same
    on the price cards and in the regional cut, and nothing downstream corrects a second time.

    Identity is `(row_id, carrier)` and never `row_id` alone: seven ids in the 1 301-row export name
    two different products, one off the leaflet page and one off the post text, and one of the
    corrected rows is such an id ([[an_exclusion_by_id_is_not_an_exclusion_by_text]]). An entry that
    matches anything but EXACTLY ONE row is a refusal — the check's «names a row the data lacks» and
    «names two products» are the same comparison.

    The correction travels ON the row (`correction`), so the card the app renders can say what a
    human changed and against which page, and an excluded row is marked rather than deleted.
    """
    entries: dict[tuple[str, str], dict] = {}
    for entry in table["rows"]:
        unknown = sorted(set(entry) - ENTRY_FIELDS)
        if unknown:
            refuse_on_the_record(f"carries the unknown key(s) {', '.join(unknown)}")
        entries[(entry["row_id"], entry["carrier"])] = entry
    if len(entries) != len(table["rows"]):
        refuse_on_the_record("names one (row_id, carrier) twice")

    rows, matched = [], dict.fromkeys(entries, 0)
    for position in positions:
        entry = entries.get((position["row_id"], position["carrier"]))
        if entry is None:
            rows.append(position)
            continue
        matched[(position["row_id"], position["carrier"])] += 1
        rows.append(corrected(position, entry))
    unmet = [
        f"{row_id} ({carrier}) matched {hits} rows"
        for (row_id, carrier), hits in matched.items()
        if hits != 1
    ]
    if unmet:
        refuse_on_the_record(
            "names " + "; ".join(unmet) + ", and every entry must name exactly one"
        )
    return rows


def corrected(position: dict, entry: dict) -> dict:
    """One row with the page's own figures in it, carrying what it replaced and who read the page."""
    item = dict(position["item"])
    row = dict(position) | {"item": item}
    was: dict = {}
    if "promo_price" in entry:
        was["promo_price"] = position.get("promo_price")
        row["promo_price"] = entry["promo_price"]
    if "size_value" in entry:
        was["size_value"] = item.get("size_value")
        item["size_value"] = entry["size_value"]
    row["correction"] = {
        "from": tick.rel(CORRECTIONS),
        "page": entry["page"],
        "verified_by": entry["verified_by"],
        "was": was,
    }
    if "exclude" in entry:
        row["correction"]["exclude"] = entry["exclude"]
    return row


UNIT_OF_SIZE = {"г": "uah_per_kg", "мл": "uah_per_l"}
"""The comparable unit a size is quoted in. `positions.parse_size` has already folded кг→г and
л→мл (`market_pulse/positions.py`), so these two are every unit a row can carry and ×1000 is the
whole conversion — no unit table, and no third kind sneaking in unnoticed."""


def unit_price(position: dict) -> tuple[str, float] | None:
    """The price of a kilogram or a litre of this row — `None` when the row cannot carry one.

    `promo_price / (size_value × pack_count) × 1000`. **The pack matters**: where `pack_count` is
    set the size is the size of ONE piece and the price is the price of the pack, so the four
    multipacks in the store (Рудь 6×100 г, Лацяти 10×10 мл) would read six and ten times dear
    without it.

    It is derived from the promo price and the size alone. It touches neither `price_old` nor the
    arithmetic depth, so SPEC 3.17 (3) / 3.21 (4) — which keep the old price off every surface —
    do not reach it: nothing here lets a reader recover a price that was not printed.
    """
    item = position.get("item") or {}
    named = UNIT_OF_SIZE.get(item.get("size_unit"))
    size, price = item.get("size_value"), position.get("promo_price")
    if named is None or not size or price is None:
        return None
    return named, round(price / (size * (item.get("pack_count") or 1)) * 1000, 4)


def position_card(position: dict, pages: dict, names: dict) -> dict:
    """One position as the app shows it: what it is, what it costs, and where to see it printed.

    A field the row does not carry is ABSENT, not null — the same rule the position row itself is
    written under. `page` is the leaflet photo the row was read off, so an extreme the operator
    doubts is one click from its own page; a row whose page did not arrive simply has no `page`
    and the app says so rather than showing a hole.
    """
    item, evidence = position["item"], position["evidence"]
    chain = position["chain"]["id"]
    card = {
        "row_id": position["row_id"],
        "brand": position["brand"]["display"],
        "category": item["category"],
        "chain": chain,
        "chain_name": names.get(chain, chain),
        "channel": evidence["channel"],
        "msg_id": evidence["msg_id"],
    }
    for field in ("line", "size_value", "size_unit", "pack_count"):
        if item.get(field) is not None:
            card[field] = item[field]
    for field in ("promo_price", "printed_pct"):
        if position.get(field) is not None:
            card[field] = position[field]
    priced = unit_price(position)
    if priced is not None:
        card["unit"], card["unit_price"] = priced
    page = pages.get(f"{evidence['channel']}:{evidence['msg_id']}")
    if page is not None:
        card["page"] = page
    if "correction" in position:
        card["correction"] = position["correction"]
    return card


def tracked_categories() -> list[dict]:
    """Every category the registry tracks, in the registry's own order — the law, not the data.

    A group key is also a category a row can carry: `dairy` labels the 39 rows whose subcategory was
    not printed, and `ice-cream` is a group with no split at all. Both are leaves here, and the one
    that doubles as a parent is flagged so the app can say which of the two it is — «Молочні
    продукти» sitting in a list of eleven beside «Сир твердий» would read as the dairy total.
    """
    groups = registry.load_registry(tick.REGISTRY).taxonomy.tracked_groups
    rows = []
    for key, group in groups.items():
        rows.append({"category": key, "name": group["name"], "group": key, "is_group_key": True})
        for sub, name in (group.get("subcategories") or {}).items():
            rows.append({"category": sub, "name": name, "group": key})
    return rows


def on_the_current_week(export: dict, media_block: dict) -> list[dict]:
    """The positions of every chain's CURRENT leaflet week — the flyer gallery's own population.

    «Current week» is per chain, the newest week that chain has pages in (DESIGN-ship-1 §11): the
    newest week over ALL chains is Маркетопт's alone, and a market read through one chain's calendar
    is not the market. A row belongs here when the page it was read off is a page of its chain's
    current set, which is the same membership the gallery's cards are counted by.
    """
    pages = media_block["pages"]
    current = set()
    for flyer in media_block["flyers"]:
        current.update(flyer["pages"])
    return [
        position
        for position in export["screen"]["positions"]
        if pages.get(f"{position['evidence']['channel']}:{position['evidence']['msg_id']}")
        in current
    ]


def category_prices(export: dict, media_block: dict, names: dict) -> dict:
    """What a kilogram costs in each tracked category THIS WEEK — n, the spread, and the two ends.

    The window is every chain's current leaflet, not the whole collected span: «what is cheapest in
    ice cream» is a question about the promo now, and a median over eight weeks of leaflets answers
    a different one (the operator's word, 12.09). It costs reach — 311 rows of 1301 — and the `n`
    beside every median is how the reader sees that.

    Cut by category AND by unit, never by category alone: five of the eleven categories hold both
    gram and millilitre rows, and one median over the two would add ₴/kg to ₴/L and publish the sum
    as a price ([[a_settlement_and_its_reference_measure_different_kinds]]).

    The numbers are `aggregates.spread` and `aggregates.quartiles` — the repository's one spelling
    of a median, called and not re-written. The ends are the rows themselves, because «найдешевший
    сир» is a claim about a particular pack and the operator has to be able to look at it: the
    extraction's own completeness bar is RED, so an extreme is exactly where a misread size lands.

    The rows are the REGISTRY's categories, not the observed ones: a category the market stopped
    promoting keeps its card and says «немає в даних», because a card that quietly disappears is an
    empty state with no sentence (DESIGN-ship-1 §10). `positions` counts every row of the category,
    priced or not, so the difference between it and the bases' `n` is visible rather than silent.
    """
    pages = media_block["pages"]
    week = on_the_current_week(export, media_block)
    priced: dict[tuple[str, str], list] = {}
    held: dict[str, int] = {}
    dropped = []
    without = 0
    for position in week:
        category = position["item"]["category"]
        held[category] = held.get(category, 0) + 1
        if excluded_from_prices(position) is not None:
            dropped.append(position)
            continue
        reading = unit_price(position)
        if reading is None:
            without += 1
            continue
        priced.setdefault((category, reading[0]), []).append(
            (reading[1], position["row_id"], position)
        )
    # the row_id breaks a price tie, so the named end is the same row on every build
    for members in priced.values():
        members.sort(key=lambda member: member[:2])
    return {
        "from": f"{tick.rel(screen.EXPORT)} :: screen.positions[] (promo_price, item.size_value,"
        f" item.size_unit, item.pack_count) on the pages of {tick.rel(OUT)} :: media.flyers, over"
        f" {tick.rel(tick.REGISTRY)} :: taxonomy.tracked_groups",
        "reading": "the promo price of a kilogram or a litre — promo_price / (size_value ×"
        " pack_count) × 1000 — over the positions of every chain's CURRENT leaflet week, read per"
        " category AND per unit, because a category that holds both grams and millilitres has no"
        " single median; n, min, q1, median, q3 and max are aggregates.spread and"
        " aggregates.quartiles, and the two ends are the rows themselves",
        "positions": len(week),
        "rows_without_a_unit_price": without,
        "excluded": {
            "n": len(dropped),
            "from": tick.rel(CORRECTIONS),
            "reading": "rows whose own leaflet page prints NO price: the stored figure was invented"
            " and there is no page-true number to put in its place, so the row stays in the window's"
            " population and is counted here instead of being priced",
            "rows": [
                {
                    "row_id": position["row_id"],
                    "carrier": position["carrier"],
                    "category": position["item"]["category"],
                    "why": excluded_from_prices(position),
                }
                for position in dropped
            ],
        },
        "categories": [
            row
            | {
                "positions": held.get(row["category"], 0),
                "bases": [
                    {"unit": unit}
                    | aggregates.spread([value for value, _, _ in members])
                    | aggregates.quartiles([value for value, _, _ in members])
                    | {
                        "cheapest": position_card(members[0][2], pages, names),
                        "dearest": position_card(members[-1][2], pages, names),
                    }
                    for unit in UNIT_OF_SIZE.values()
                    if (members := priced.get((row["category"], unit)))
                ],
            }
            for row in tracked_categories()
        ],
    }


def regions(export: dict, media_block: dict, names: dict) -> dict:
    """The operator's regional cut: the chains they say serve a region, each on its current week.

    **This is a selection of CHAINS, not a geography of rows.** No source in the registry carries a
    city or an oblast, and the leaflets of the national chains are national issues — so the block
    may say «мережі, присутні в області» and may not say «позиції області». The one chain whose own
    channel names a city is Маркетопт (Толока) м.Кременчук.

    «Current week» is the flyer gallery's, not a second one: per chain, the newest week that chain
    has pages in (DESIGN-ship-1 §11). A chain with no flyer set says so by name — `absent` — and
    shows no rows, because an empty shelf and a chain we hold no pages for are different states.
    """
    config = yaml.safe_load(REGIONS.read_text(encoding="utf-8"))
    pages = media_block["pages"]
    flyers = {flyer["chain"]: flyer for flyer in media_block["flyers"]}
    positions = export["screen"]["positions"]
    cut = []
    for region, block in config.items():
        chains_out = []
        for chain in block["chains"]:
            row = {"chain": chain, "name": names.get(chain, chain)}
            flyer = flyers.get(chain)
            if flyer is None:
                chains_out.append(row | {"absent": "no_pages"})
                continue
            on_the_week = set(flyer["pages"])
            cards = [
                position_card(position, pages, names)
                for position in positions
                if pages.get(f"{position['evidence']['channel']}:{position['evidence']['msg_id']}")
                in on_the_week
                and excluded_from_prices(position) is None
            ]
            cards.sort(
                key=lambda card: (card["category"], card.get("promo_price") or 0.0, card["row_id"])
            )
            chains_out.append(
                row
                | {
                    "week": flyer["week"],
                    "since": flyer["since"],
                    "until": flyer["until"],
                    "positions": cards,
                }
            )
        cut.append({"region": region, "name": block["name"], "chains": chains_out})
    return {
        "from": f"{tick.rel(REGIONS)} :: <region>.chains, each on its own flyer set of"
        f" {tick.rel(OUT)} :: media.flyers",
        "reading": "the chains the OPERATOR says serve the region, each on the newest week it has"
        " leaflet pages in — a selection of chains, not a geography of rows: the registry carries no"
        " region, and the leaflets of the national chains are national",
        "cuts": cut,
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

    # the media block is joined once and read three times: the gallery renders it, and the regional
    # cut and the two priced ends borrow its page names rather than joining the records again
    chain_table = chains()
    media_block = media(promo, manifests)
    names = {row["id"]: row["name"] for row in chain_table["rows"]}

    # the page-true rows, corrected once, for every block that shows a price. The gallery keeps the
    # RAW rows on purpose: `media` joins pages, not figures, and a row dropped from it would move the
    # flyer set the operator browses — the cover in the page population is POST-GATE ((yy) 5).
    record = yaml.safe_load(CORRECTIONS.read_text(encoding="utf-8"))
    printed = promo | {
        "screen": promo["screen"] | {"positions": page_true(promo["screen"]["positions"], record)}
    }

    document = {
        "contract": CONTRACT,
        "chains": chain_table,
        "data_until": data_until(promo),
        "command_center": centre | {"conclusions": builder.conclusions(centre, strings)},
        "model": {
            "from": tick.rel(VERDICT),
            "verdict": json.loads(VERDICT.read_text(encoding="utf-8")),
        },
        "media": media_block,
        "category_prices": category_prices(printed, media_block, names),
        "regions": regions(printed, media_block, names),
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
