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

OUT = screen.RESULTS / "front_data.json"
VERDICT = screen.RESULTS / "verdict_45h2.json"
GRADE = screen.RESULTS / "grade_positions_50.json"
DRAW = screen.RESULTS / "positions_draw_50.json"

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
        "data_until": data_until(promo),
        "command_center": centre | {"conclusions": builder.conclusions(centre, strings)},
        "model": {
            "from": tick.rel(VERDICT),
            "verdict": json.loads(VERDICT.read_text(encoding="utf-8")),
        },
        "s2_readings": screen.s2_readings(screen.RESULTS),
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


def stage(target: Path) -> list[dict]:
    """The static build's `data/`: the two files the adapters fetch, and a manifest of their shas.

    Run AFTER `vite build`, which empties its own output directory — a copy staged before the build
    is a copy the build deletes.
    """
    refuse_on_a_missing_source(APP_FILES)
    target.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in APP_FILES:
        shutil.copyfile(path, target / path.name)
        rows.append({"file": path.name, **digest(path)})
    manifest = {
        "contract": CONTRACT,
        "data_until": json.loads(OUT.read_text(encoding="utf-8"))["data_until"],
        "files": rows,
    }
    (target / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    return rows


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
        for row in stage(args.stage):
            print(f"  staged {row['file']}  {row['sha256'][:16]}…  {row['bytes'] / 1024:.0f} KB")
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
    print(f"  s1 reading    {'read' if document['s1_reading']['reading'] else 'absent'}")
    print(f"  sources       {len(document['sources'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
