#!/usr/bin/env python3
"""`data/derived/pulse.db` → `results/weekly/positions_<ISO-week>.jsonl` — the week the store
does not keep.

**Why it exists.** A rerun of the aggregate build does not add a week to the derived rows, it
REPLACES them: `build_aggregates.settle()` unlinks the database and backs a freshly built one over
it, so the store holds exactly the windows the run's own record files describe and nothing an
earlier run put there. Measured, not assumed — a planted window and a sentinel table both vanish
across a second run into the same `--out`, and the two files are byte-identical
(`docs/plans/ship-1.PROGRESS.md`, item «data-shape»). Every week the operator collects would
therefore be the only week on disk, and the future price model would have one week to learn from.

So the weekly rows are written out, one file per ISO week, and a week is only ever rewritten by a
run that still carries it: a file for a week this run knows nothing about is left exactly where it
is. That is the whole of the accumulation — no index, no ledger, no state.

**The home is `results/weekly/`, which git carries** (ruling (ccc) 4 13.09). The first home was
`data/derived/weekly/` beside the store, and `data/**` is gitignored: the ten weeks written there
were reconstructible on a clean clone only because the committed exports still hold today's rows,
and week N+1 would have had no such copy — the operator's ML history would have lived on one
laptop. Under `results/` a collected week is a diff the operator commits, and `make tick` therefore
dirties `results/weekly/` until he does (the tick's own clock stays gitignored one file over).

**The rows are the store's own**, through `aggregates.positions_source`, the one statement every
reader of the positions table shares: the union of the windows, one row per `(carrier, row_id)` with
the newest window winning, the live registry's `collect: false` channels already dropped.

**The week is the row's own message date.** A leaflet page IS a message and carries its own
`msg_id`, so its date lives in the post-media records and nowhere else — `export_front_data`'s
`media_index` is the one reader of those, and it is imported here rather than spelled a second time
(PHASE-ship-1 §3). A post-text row's date comes from the raw store through `trends.post_weeks`.
Both sides end in `trends.iso_week`, the repository's one spelling of a week. Today the join dates
every row of the store (1301 of 1301, W27–W36); the raw store alone would date 346 of them.

A row whose message no record dates is COUNTED and printed by carrier, never bucketed under a
guessed week — an unknown week is not a week (`market_pulse.trends`).

    PYTHONPATH=src python3 scripts/weekly_positions.py
    PYTHONPATH=src python3 scripts/weekly_positions.py --out /tmp/weekly --quiet
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from market_pulse import aggregates, trends  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

import tick  # noqa: E402

DB = REPO_ROOT / "data" / "derived" / "pulse.db"
OUT = REPO_ROOT / "results" / "weekly"


def front():
    """`scripts/export_front_data.py` as a module — imported by path, the way `build_aggregates`
    imports `window_summary_5c2`: it is a script and not a package, and its `media_index` is the
    only reader of `results/post_media_*.json` there is."""
    spec = importlib.util.spec_from_file_location(
        "export_front_data", REPO_ROOT / "scripts" / "export_front_data.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def store_rows(conn: sqlite3.Connection, window_id: str, excluded: tuple[str, ...]) -> list[dict]:
    """The positions the screen's own statement returns, as plain dicts.

    `newest` is the dedupe's own working column and not a fact about a position, so it leaves here
    rather than travelling into a dataset a model would read it from.
    """
    source, params = aggregates.positions_source(window_id, excluded)
    conn.row_factory = sqlite3.Row
    rows = [dict(row) for row in conn.execute(f"SELECT * FROM ({source})", params)]
    for row in rows:
        row.pop("newest", None)
    return rows


def week_index(module) -> dict[tuple[str, int], str]:
    """`(channel, msg_id)` → ISO week, over both kinds of message a position is read off."""
    weeks = dict(trends.post_weeks())
    for key, page in module.media_index(module.media_manifests()).items():
        if page["date"] is not None:
            weeks[key] = trends.iso_week(page["date"])
    return weeks


def by_week(rows: list[dict], weeks: dict[tuple[str, int], str]) -> tuple[dict, Counter]:
    """The rows bucketed by their own week, and what could not be dated, by carrier."""
    dated: dict[str, list[dict]] = {}
    undated: Counter = Counter()
    for row in rows:
        week = weeks.get((row["channel"], int(row["msg_id"])))
        if week is None:
            undated[row["carrier"]] += 1
            continue
        dated.setdefault(week, []).append({"week": week} | row)
    for week in dated:
        # `(carrier, row_id)` is the row's identity in the store, so it is the file's order too:
        # two runs over an unchanged store write the same bytes.
        dated[week].sort(key=lambda row: (row["carrier"], row["row_id"]))
    return dated, undated


def write(out: Path, dated: dict[str, list[dict]]) -> list[tuple[Path, int]]:
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for week, rows in sorted(dated.items()):
        path = out / f"positions_{week}.jsonl"
        path.write_text(
            "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )
        written.append((path, len(rows)))
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DB)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--window", default=aggregates.ALL_WINDOWS)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    if not args.db.exists():
        # a clean clone has no store, and `make tick` says so and exits 0 — this runs beside it
        print(f"weekly: no store at {tick.rel(args.db)} — nothing to write", file=sys.stderr)
        return 0

    conn = sqlite3.connect(args.db)
    excluded = tick.not_collected(load_registry(tick.REGISTRY))
    rows = store_rows(conn, args.window, excluded)
    dated, undated = by_week(rows, week_index(front()))
    written = write(args.out, dated)

    if args.quiet:
        return 0
    for path, count in written:
        print(f"wrote {tick.rel(path)}  {count} rows")
    print(
        f"weekly: {sum(count for _, count in written)} of {len(rows)} rows dated into"
        f" {len(written)} weeks"
        + (
            ""
            if not undated
            else " · undated and left out: "
            + " · ".join(f"{carrier} {n}" for carrier, n in sorted(undated.items()))
            + " (no record carries their message's date — an unknown week is not a week)"
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
