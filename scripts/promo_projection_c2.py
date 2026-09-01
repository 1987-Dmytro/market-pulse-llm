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


SMOKE = REPO_ROOT / "results" / "smoke_vision_c2.json"


def marginal_bound(usd_per_second: float, pages_floor: int, pages_ceiling: int) -> dict | None:
    """The per-page cost with the cold start paid ONCE, bounded from the smoke's own fields.

    The ledger's `vision_seconds_per_page` is boot-inclusive: the smoke made two calls — the
    `info` call, which carries the cold start, and the 30 pages — and `worker_seconds` covers
    both. Over 30 pages one boot is most of the bill; over a thousand it is a rounding error, and
    a paid pass pays it ONCE. Projecting 1 022 pages at a rate with 34 boots baked into it would
    over-price the leg by roughly 2.5x and answer SP-1 with the wrong sign.

    So the marginal is BOUNDED rather than invented ([[bound_instead_of_recompute]]), both ends
    from fields the smoke record already carries:

    * upper — the positions call's own wall clock (`wall_seconds_client`, which includes whatever
      queue that call waited), divided by the pages. It cannot have cost more worker time than it
      took wall time.
    * lower — total `worker_seconds` minus the info call's wall (`wall_seconds` minus
      `wall_seconds_client`), i.e. everything the boot could not have been.

    Neither end is a reading of the marginal itself; the pair is a proof of where it lies.
    """
    if not SMOKE.exists():
        return None
    smoke = read(SMOKE)
    timing, pages = smoke["timing"], smoke["pages"]
    info_wall = round(timing["wall_seconds"] - timing["wall_seconds_client"], 3)
    upper = round(timing["wall_seconds_client"] / pages, 3)
    lower = round((timing["worker_seconds"] - info_wall) / pages, 3)
    one_boot_usd = round(info_wall * usd_per_second, 4)
    return {
        "seconds_per_page_lower": lower,
        "seconds_per_page_upper": upper,
        "one_boot_seconds": info_wall,
        "one_boot_usd": one_boot_usd,
        "derived_from": "results/smoke_vision_c2.json :: timing"
        " (worker_seconds, wall_seconds, wall_seconds_client) — no number typed",
        "usd_at_pages_floor": [
            round(pages_floor * lower * usd_per_second + one_boot_usd, 4),
            round(pages_floor * upper * usd_per_second + one_boot_usd, 4),
        ],
        "usd_at_pages_ceiling": [
            round(pages_ceiling * lower * usd_per_second + one_boot_usd, 4),
            round(pages_ceiling * upper * usd_per_second + one_boot_usd, 4),
        ],
        "why_this_and_not_the_ledger_row": "the ledger row is the measurement and stays what it"
        " is; this is what that measurement implies for a population that pays one boot, and the"
        " two answer different questions.",
    }


def measured_rate() -> dict | None:
    """The smoke's row, or None while the ledger has not got one.

    The LAST row wins: a rate is a property of the pod it was measured on, so a second
    measurement supersedes rather than averages with the first ([[a_rate_is_a_property_of_the_pod]]).
    """
    if not LEDGER.exists():
        return None
    found = None
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("name") == VISION_RATE_NAME:
                found = row
    return found


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


PAGECOUNT = REPO_ROOT / "results" / "promo_pagecount_c2.json"


def exact_pages() -> dict | None:
    """The counted pages, once `promo_pagecount_c2.py` has read them off Telegram.

    While the store was the only source the page count could only be BOUNDED, and this projection
    was a range for that reason and no other. The pagecount record collapses the bound: every
    pinned post reached, every album member counted, a page defined as a PHOTO member. So the two
    ends of the population stop being two numbers and the projection can do what clause (a) asks —
    price C2 as ONE number.
    """
    if not PAGECOUNT.exists():
        return None
    record = read(PAGECOUNT)
    if record["totals"]["rows_unreachable"]:
        # Not fatal, and not silent: an unreachable row is priced at the store's gap bound, so the
        # total is still an upper bound on the truth. The reader is told which it is holding.
        pass
    return record


def build(census_path: Path = CENSUS) -> dict:
    census = read(census_path)
    run = read(RUN_5C2)
    usd_per_second = run["rate_usd_per_second"]
    leaflet = dict(census["selection"]["leaflet_page"])
    counted = exact_pages()
    if counted:
        pages = counted["totals"]["pages"]
        leaflet["pages_floor"] = leaflet["pages_ceiling"] = pages
    texts = census["selection"]["post_text"]["posts"]
    left = remainder()

    smoke = measured_rate()
    all_corners = corners(run)
    if smoke:
        all_corners.append(
            {
                "name": "measured_smoke",
                "seconds": float(smoke["value"]),
                "measured": True,
                "field": f"results/measurements.jsonl :: {VISION_RATE_NAME}",
                "sample": f"n={smoke['n']} pages, {smoke['instrument']}, {smoke['measured_on']}."
                " BOOT-INCLUSIVE: the smoke's two calls are the info call (which carries the cold"
                " start) and the 30 pages, and `worker_seconds` covers both — so over a population"
                " large enough to amortise one boot this rate is an UPPER bound, not a centre"
                " ([[projected_rate_versus_measured_rate]] is the same trap from the other side).",
            }
        )

    table = []
    for corner in all_corners:
        row = dict(corner)
        for end in ("floor", "ceiling"):
            pages = leaflet[f"pages_{end}"]
            row[f"pages_{end}"] = pages
            row[f"usd_{end}"] = round(pages * corner["seconds"] * usd_per_second, 4)
        row["fits_at_floor"] = row["usd_floor"] <= left["usd"]
        row["fits_at_ceiling"] = row["usd_ceiling"] <= left["usd"]
        table.append(row)

    bound = marginal_bound(usd_per_second, leaflet["pages_floor"], leaflet["pages_ceiling"])
    # The ONE number clause (a) asks for: counted pages × the marginal's dear end + one boot.
    c2_priced = bound["usd_at_pages_ceiling"][1] if bound and counted else None

    return {
        "contract": "docs/PHASE-promo-pulse-1.md §8 clause (a) — the C2 projection ($0). SP-1 was"
        " ANSWERED 2026-09-01 («Цикл-3 = весь баланс, потолок $4.8»), so this is no longer a"
        " stop-point but the price of the leg, against the cycle-3 remainder read below.",
        "reads": {
            "census": str(census_path.relative_to(REPO_ROOT))
            if census_path.is_relative_to(REPO_ROOT)
            else str(census_path),
            "census_ids_sha256": census["selection"]["ids_sha256"],
            "window": census["window"],
            "rates": "results/run_5c2_positions.json",
        },
        "why_a_range_and_not_a_number": {
            "state": "MEASURED — the smoke wrote the row and the table carries the measured corner;"
            " what remains a range is the PAGE COUNT, not the rate"
            if smoke
            else "the rate is missing and the band is built from the two that were measured",
            "measured_rate_row": smoke,
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
            "pages_exact": counted["totals"]["pages"] if counted else None,
            "pages_counted_by": "results/promo_pagecount_c2.json" if counted else None,
            "pages_state": (
                f"COUNTED — {counted['totals']['rows_exact']} of"
                f" {counted['totals']['pinned_media_posts']} pinned posts re-read off Telegram,"
                f" {counted['totals']['rows_unreachable']} unreachable and priced at the store's"
                f" gap bound. The census's own bound was"
                f" {census['selection']['leaflet_page']['pages_floor']}…"
                f"{census['selection']['leaflet_page']['pages_ceiling']}; the store-only upper"
                f" bound was {counted['totals']['pages_store_upper_bound']}."
                if counted
                else "BOUNDED — no pagecount record; the two ends are the census's"
            ),
            "text_price_posts": texts,
            "note": "the text leg is not priced here: `text_marginal_seconds` is a warm-up marginal"
            " like the page one, and the vision leg is what the money question is about.",
        },
        "rate_usd_per_second": usd_per_second,
        "remainder": left,
        "table": table,
        "verdict": {
            "c2_priced_usd": c2_priced,
            "c2_priced_means": "THE one number clause (a) asks for: the C2 vision leg at the"
            f" MARGINAL rate. {leaflet['pages_ceiling']} counted pages"
            f" (results/promo_pagecount_c2.json) at the marginal's PESSIMISTIC end"
            f" ({bound['seconds_per_page_upper']} s/page) plus ONE cold start"
            f" (${bound['one_boot_usd']}), which is what a pass this size pays. The optimistic end"
            f" is ${bound['usd_at_pages_floor'][0]}; both are readings of the same smoke, and the"
            " dear one is what the leg is priced at, because the guard's own `spend()` is the"
            " pessimistic max and a ceiling blown after the money is spent cannot be un-spent."
            if bound and counted
            else None,
            "c2_priced_fits_remainder": (c2_priced <= left["usd"]) if c2_priced else None,
            "the_one_number_usd": next(
                (row["usd_floor"] for row in table if row["name"] == "measured_smoke"), None
            ),
            "the_one_number_means": "the same population at the BOOT-INCLUSIVE measured rate."
            " It is not what C2 costs — over 30 pages one cold start is most of the bill and over"
            " 3 008 it is a rounding error — and it is kept because it is the only rate anything"
            " measured directly. `c2_priced_usd` above is the price; this is the ceiling that"
            " price has to sit under, and the gap between them IS the amortised boot."
            if smoke
            else None,
            "at_the_ceiling_usd": next(
                (row["usd_ceiling"] for row in table if row["name"] == "measured_smoke"), None
            ),
            "marginal_bound": bound,
            "remainder_usd": left["usd"],
            "cap_rule": "docs/PROCESS.md — cap = 2x the registry estimate, one paid run per prompt,"
            " and «a cap is not raised to finish a run». The smoke ran under its own $0.35 cap;"
            " the C2 pass needs a cap of its own, registered before it, and the projection above"
            " is what that cap is set from.",
            "cheapest_corner_usd": min(row["usd_floor"] for row in table),
            "dearest_corner_usd": max(row["usd_ceiling"] for row in table),
            "fits_anywhere": any(row["fits_at_floor"] for row in table),
            "fits_everywhere": all(row["fits_at_ceiling"] for row in table),
            "decision": "SP-1 is CLOSED (operator, 2026-09-01): cycle 3 is open at $4.80. What"
            " this table decides is no longer WHETHER but HOW MUCH of C2 fits beside C3's own"
            " caps ($2.50 dev loop + $0.30 holdout), which is the even-cut question of the same"
            " ruling.",
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
