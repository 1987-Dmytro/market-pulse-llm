#!/usr/bin/env python3
"""K5 — the S1 draw: 50 positions, seed 42, for the team lead to label. $0.

    PYTHONPATH=src python3.11 scripts/draw_positions_50.py          # twice → identical sha256

Plan §2 K5: «50 positions, seed 42, from ≥3 chains' flyers/posts of the backfilled 4 weeks; two runs
produce an identical sha. Handed to the team lead.» Two files come out: the DRAW
(`results/positions_draw_50.json`, what the team lead labels from) and the PREDICTED rows
(`results/positions_50_predicted.jsonl`, what `scripts/grade_positions.py` scores those labels
against). Two files because the labeller must not see the extraction he is grading
([[an_exclusion_by_id_is_not_an_exclusion_by_text]] — the same discipline, one level up).

**The population is stated in the record, and today it is the WRONG one.** The draw's population is
supposed to be C2's backfilled four weeks. C2 is unbought, so what is in `data/derived/pulse.db`
today is 5c2's old 145 rows, and `population_state` says so in as many words. The mechanics of K5 —
seed, stratification, two identical shas — are provable now; the FILE is not the deliverable until
S4 has run and this is re-drawn. Handing the team lead 50 rows off a population the phase is about
to replace would spend his labelling on rows the backfill supersedes.

**≥3 chains is a refusal, not a filter.** A draw that quietly returned rows from one chain would be
a sample about that chain, and the bar computed on it would be a fact about ATB
([[a_prefilter_cannot_certify_the_population]]). The draw is stratified by chain — proportional,
with at least one row per chain that has any — so a chain with 3 rows is not lost to a chain with
106.
"""

from __future__ import annotations

import argparse
import json
import random
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse import aggregates, trends  # noqa: E402

DB = REPO_ROOT / "data" / "derived" / "pulse.db"
DRAW = REPO_ROOT / "results" / "positions_draw_50.json"
PREDICTED = REPO_ROOT / "results" / "positions_50_predicted.jsonl"
SEED = 42
ROWS = 50
MIN_CHAINS = 3

CHAINS = ("atb", "varus", "silpo", "novus", "fora", "megamarket", "auchan")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def stratified(rows: list[dict], want: int, seed: int = SEED) -> list[dict]:
    """`want` rows, drawn per chain in proportion to the chain's size, at least one each.

    Deterministic twice over: the strata are walked in sorted order and each is sampled from its own
    `Random(seed)`, so the result does not depend on dict iteration order or on how many strata came
    before. The remainder — `want` minus what the proportional pass gave — is filled from the rows
    not yet taken, again in sorted order, so a rounding-down never returns a short draw.
    """
    strata: dict[str, list[dict]] = {}
    for row in rows:
        strata.setdefault(row["chain"], []).append(row)
    for stratum in strata.values():
        stratum.sort(key=lambda row: row["row_id"])

    total, taken = len(rows), []
    for chain in sorted(strata):
        stratum = strata[chain]
        share = max(1, round(want * len(stratum) / total)) if total else 0
        taken += random.Random(seed).sample(stratum, min(share, len(stratum)))
    chosen = {row["row_id"] for row in taken}
    if len(taken) > want:
        taken = sorted(taken, key=lambda row: row["row_id"])[:want]
    elif len(taken) < want:
        rest = sorted((row for row in rows if row["row_id"] not in chosen), key=lambda r: r["row_id"])
        taken += random.Random(seed).sample(rest, min(want - len(taken), len(rest)))
    return sorted(taken, key=lambda row: row["row_id"])


def population(conn, window_id: str) -> list[dict]:
    """Every position of the window, as the screen carries it, plus its week."""
    weeks = trends.post_weeks()
    rows = []
    for row in aggregates.promo_positions(conn, window_id, CHAINS):
        evidence = row.get("evidence") or {}
        rows.append(
            {
                **row,
                "chain": row["chain"]["id"],
                "week": weeks.get((evidence.get("channel"), int(evidence.get("msg_id", 0)))),
            }
        )
    return sorted(rows, key=lambda row: row["row_id"])


def for_the_labeller(row: dict) -> dict:
    """What the team lead sees: the carrier and where it is — never the extraction he is grading."""
    evidence = row.get("evidence") or {}
    return {
        "row_id": row["row_id"],
        "chain": row["chain"],
        "carrier": row.get("carrier"),
        "channel": evidence.get("channel"),
        "msg_id": evidence.get("msg_id"),
        "week": row.get("week"),
        "link": f"https://t.me/{(evidence.get('channel') or '').lstrip('@')}/{evidence.get('msg_id')}",
    }


def predicted(row: dict) -> dict:
    """What the instrument extracted, in `grade_positions.py`'s shape."""
    item = row.get("item") or {}
    return {
        "row_id": row["row_id"],
        "brand": (row.get("brand") or {}).get("display"),
        "product": item.get("line") or item.get("category"),
        "size_value": item.get("size_value"),
        "size_unit": item.get("size_unit"),
        "price_promo": row.get("promo_price"),
        "badge_pct": row.get("printed_pct"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DB)
    parser.add_argument("--out", type=Path, default=DRAW)
    parser.add_argument("--predicted", type=Path, default=PREDICTED)
    parser.add_argument(
        "--window",
        default="w2",
        help="the C2 window — S5's re-draw is over the population S4 bought (ruling 02.09 (d),"
        " «Then S5's re-draw over the C2 population»); w1 draws 5c2's 145 rows.",
    )
    parser.add_argument("--rows", type=int, default=ROWS)
    args = parser.parse_args(argv)

    if not args.db.exists():
        print(f"draw_positions_50 REFUSED: no store at {args.db}", file=sys.stderr)
        return 1
    conn = sqlite3.connect(args.db)
    rows = population(conn, args.window)
    chains = sorted({row["chain"] for row in rows})
    if len(chains) < MIN_CHAINS:
        print(
            f"draw_positions_50 REFUSED: {len(chains)} chain(s) in the population ({', '.join(chains)}),"
            f" and K5 asks for at least {MIN_CHAINS}. A draw from fewer is a sample about one chain.",
            file=sys.stderr,
        )
        return 1
    drawn = stratified(rows, min(args.rows, len(rows)))

    record = {
        "contract": "docs/plans/promo-pulse-1.md K5 — the 50 positions the team lead labels into"
        " docs/labels-positions-50.jsonl. Rows carry the carrier and its link, never the"
        " extraction: the labeller must not see what he is grading.",
        "seed": SEED,
        "population": len(rows),
        "population_state": "PRE-C2 — these are 5c2's rows, not the backfilled four weeks K5 names."
        " C2 is unbought (the cycle-3 guard refuses; see docs/plans/promo-pulse-1.STOP.md), so this"
        " file proves the DRAW's mechanics and is NOT yet the file to label. Re-draw after S4.",
        "chains": chains,
        "rows_drawn": len(drawn),
        "by_chain": {chain: sum(1 for row in drawn if row["chain"] == chain) for chain in chains},
        "rows": [for_the_labeller(row) for row in drawn],
    }
    args.out.write_text(
        json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.predicted.write_text(
        "".join(
            json.dumps(predicted(row), ensure_ascii=False, sort_keys=True) + "\n" for row in drawn
        ),
        encoding="utf-8",
    )
    print(f"{len(drawn)} of {len(rows)} positions, seed {SEED}, chains: {', '.join(chains)}")
    print(f"wrote {rel(args.out)} and {rel(args.predicted)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
