#!/usr/bin/env python3
"""K4 — the C2 projection: a RANGE, against a freshly re-read remainder. $0.

S3 of `docs/plans/promo-pulse-1.md`, and the other half of the table SP-1 is decided on. It emits a
range and cannot emit a single figure, for a reason that is a fact about a file:
`results/measurements.jsonl` carries fifteen rows and **no vision seconds-per-page row at all**. The
projection precedent hard-exits on exactly that — `scripts/project_think_zero_shot.py:107`, «the
smoke writes it — project nothing until it has» — and that refusal is right for a projection whose
job is a number. It is wrong for this one, whose job is to show the operator how wide the band is
BEFORE anything is bought. So the missing row is declared, not fatal, and the band is built from the
two rates that were actually measured:

    1.729 s   `run_5c2_positions.json :: go_no_go.page_marginal_seconds` — a two-call WARM-UP
              marginal. A sample of one pair; Dv310 has it under-pricing a leg 2.4× across two
              boots, because the warm-up page happened to be empty.
    10.408 s  `run_5c2_positions.json :: timing.seconds_per_row` over 205 rows / 2 133.705 worker
              seconds — the realised rate, and the number 5c2's closing ruling says the next
              registration starts from.

Between them sits a `fitted_middle`. It is an INTERPOLATION and says so in its own row: the
geometric mean of the two corners, chosen because they are 6.0× apart and an arithmetic mean of a
rate spanning that much sits against the slow end. It carries `measured: false`, and the thing that
would replace it is named — S4's smoke, which writes the vision row the ledger lacks.

Pages are a bound, not a count (`promo_census_c2.py`), so every corner is priced at both ends of it.
The remainder is READ from the guard here, at this moment, and its raw line is kept as evidence —
never quoted from a document ([[a_reading_that_outlived_its_state]]).

This is a STOP, not a pass/fail: the operator chooses cycle-3, a narrower C2, or a pod runner on
this table (plan §4 SP-1, phase spec §6.1).

    PYTHONPATH=src python3.11 scripts/promo_projection_c2.py
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

CENSUS = REPO_ROOT / "results" / "promo_census_c2.json"
RUN_5C2 = REPO_ROOT / "results" / "run_5c2_positions.json"
LEDGER = REPO_ROOT / "results" / "measurements.jsonl"
GUARD = REPO_ROOT / "scripts" / "runpod_guard.py"
OUT = REPO_ROOT / "results" / "promo_projection_c2.json"

VISION_RATE_NAME = "vision_seconds_per_page"
"""The row `results/measurements.jsonl` does not have. Named so the absence is greppable, and so
the smoke that writes it knows what to call it."""


def read(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"{path.relative_to(REPO_ROOT)} is missing — run its producer first")
    return json.loads(path.read_text(encoding="utf-8"))


def ledger_names() -> list[str]:
    """Every rate the measurement ledger holds, by name — read, so the absence is a reading."""
    if not LEDGER.exists():
        return []
    names = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("name"):
                names.append(row["name"])
    return sorted(set(names))


def remainder() -> dict:
    """The cycle-2 remainder, READ from the guard now, with the line it was read off kept.

    Read-only: the guard writes only under `--note`, and this passes none. The raw line is carried
    into the record because a number without the reading behind it is a number somebody typed.
    """
    proc = subprocess.run(
        [sys.executable, str(GUARD)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")},
    )
    line = next(
        (one for one in proc.stdout.splitlines() if one.startswith("REMAINING")),
        None,
    )
    if line is None:
        raise SystemExit(
            "the guard printed no REMAINING line — a projection against an unread remainder is a"
            f" projection against nothing. stdout: {proc.stdout[-400:]!r}"
            f" stderr: {proc.stderr[-400:]!r}"
        )
    usd = float(re.search(r"\$([0-9.]+)", line).group(1))
    spent = next((one for one in proc.stdout.splitlines() if one.startswith("CYCLE 2 SPENT")), "")
    return {"usd": usd, "read_from": "scripts/runpod_guard.py", "line": line.strip(),
            "spent_line": spent.strip()}


def corners(run: dict) -> list[dict]:
    marginal = run["go_no_go"]["page_marginal_seconds"]
    realised = run["timing"]["seconds_per_row"]
    middle = round((marginal * realised) ** 0.5, 4)
    return [
        {
            "name": "warm_up_marginal",
            "seconds": marginal,
            "measured": True,
            "field": "results/run_5c2_positions.json :: go_no_go.page_marginal_seconds",
            "sample": "two warm-up calls, n=1 pair — Dv310 has this shape under-pricing a leg 2.4×"
            " across two boots, because the warm-up page was empty. A FLOOR, never an estimate.",
        },
        {
            "name": "fitted_middle",
            "seconds": middle,
            "measured": False,
            "field": "derived here",
            "sample": "INTERPOLATION, not a measurement: the geometric mean of the two corners,"
            f" which are {round(realised / marginal, 2)}× apart. Geometric and not arithmetic"
            " because an arithmetic mean of a rate spanning that much sits against the slow end."
            f" The row that would replace it is `{VISION_RATE_NAME}`, which S4's smoke writes.",
        },
        {
            "name": "realised_5c2",
            "seconds": realised,
            "measured": True,
            "field": "results/run_5c2_positions.json :: timing.seconds_per_row",
            "sample": f"n={run['timing']['rows']} rows over {run['timing']['worker_seconds']}"
            " worker seconds — the number 5c2's closing ruling says the next registration starts"
            " from.",
        },
    ]


def build(census_path: Path = CENSUS) -> dict:
    census = read(census_path)
    run = read(RUN_5C2)
    usd_per_second = run["rate_usd_per_second"]
    leaflet = census["selection"]["leaflet_page"]
    texts = census["selection"]["post_text"]["posts"]
    left = remainder()

    table = []
    for corner in corners(run):
        row = dict(corner)
        for end in ("floor", "ceiling"):
            pages = leaflet[f"pages_{end}"]
            row[f"pages_{end}"] = pages
            row[f"usd_{end}"] = round(pages * corner["seconds"] * usd_per_second, 4)
        row["fits_at_floor"] = row["usd_floor"] <= left["usd"]
        row["fits_at_ceiling"] = row["usd_ceiling"] <= left["usd"]
        table.append(row)

    return {
        "contract": "docs/plans/promo-pulse-1.md S3 / K4 — the C2 projection ($0). A STOP, not a"
        " pass/fail: the operator decides cycle-3 / narrowing / a pod runner on this table.",
        "reads": {
            "census": str(census_path.relative_to(REPO_ROOT))
            if census_path.is_relative_to(REPO_ROOT)
            else str(census_path),
            "census_ids_sha256": census["selection"]["ids_sha256"],
            "window": census["window"],
            "rates": "results/run_5c2_positions.json",
        },
        "why_a_range_and_not_a_number": {
            "missing_rate": VISION_RATE_NAME,
            "ledger": "results/measurements.jsonl",
            "ledger_rows": len(ledger_names()),
            "ledger_names": ledger_names(),
            "precedent": "scripts/project_think_zero_shot.py:107 hard-exits on a missing named"
            " rate. That is right for a projection whose job is a number and wrong for one whose"
            " job is to show the band BEFORE anything is bought, so the absence is declared here"
            " and the band is built from the two rates that were measured.",
            "pages_are_bounded_too": census["page_bound"],
        },
        "population": {
            "leaflet_posts": leaflet["posts"],
            "pages_floor": leaflet["pages_floor"],
            "pages_ceiling": leaflet["pages_ceiling"],
            "pages_known_from_a_manifest": leaflet["pages_known"],
            "text_price_posts": texts,
            "note": "the text leg is not priced here: `text_marginal_seconds` is a warm-up marginal"
            " like the page one, and the vision leg is what the money question is about.",
        },
        "rate_usd_per_second": usd_per_second,
        "remainder": left,
        "table": table,
        "verdict": {
            "cheapest_corner_usd": min(row["usd_floor"] for row in table),
            "dearest_corner_usd": max(row["usd_ceiling"] for row in table),
            "fits_anywhere": any(row["fits_at_floor"] for row in table),
            "fits_everywhere": all(row["fits_at_ceiling"] for row in table),
            "decision": "SP-1 — the operator's, on this table: (a) open cycle-3 and name the sum,"
            " (b) narrow C2 and say which chains are dropped, (c) pay to build a positions POD"
            " runner (2.383× cheaper per 1 000 rows, results/srv2d_cost.json).",
        },
    }


def render(record: dict) -> str:
    head = f"{'rate':<18}{'s/page':>9}{'measured':>10}{'$ @pages≥':>12}{'$ @pages≤':>12}{'fits':>8}"
    lines = [head, "-" * len(head)]
    for row in record["table"]:
        fits = "≥ only" if row["fits_at_floor"] and not row["fits_at_ceiling"] else (
            "yes" if row["fits_at_ceiling"] else "NO"
        )
        lines.append(
            f"{row['name']:<18}{row['seconds']:>9}{str(row['measured']):>10}"
            f"{row['usd_floor']:>12.4f}{row['usd_ceiling']:>12.4f}{fits:>8}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--census", type=Path, default=CENSUS)
    args = parser.parse_args(argv)

    record = build(args.census)
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    population = record["population"]
    print(
        f"pages {population['pages_floor']}…{population['pages_ceiling']}"
        f" from {population['leaflet_posts']} media posts"
        f" ({population['pages_known_from_a_manifest']} known)"
    )
    print(f"remainder read now: {record['remainder']['line']}")
    print(render(record))
    print(f"\nSTOP — {record['verdict']['decision']}")
    where = args.out.relative_to(REPO_ROOT) if args.out.is_relative_to(REPO_ROOT) else args.out
    print(f"wrote {where}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
