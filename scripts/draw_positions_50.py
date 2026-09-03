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
import hashlib
import json
import random
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse import aggregates, trends  # noqa: E402

DB = REPO_ROOT / "data" / "derived" / "pulse.db"
MEDIA = REPO_ROOT / "data" / "annotation" / "promo_c2" / "posts_media"
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


POPULATION_STATE = {
    "w1": "5c2 — the first window's sealed 145 positions. K5's file is w2's; this window is here so"
    " the draw's mechanics can be exercised over a population nobody is labelling.",
    "w2": "C2 — the population S4 bought, re-drawn over window w2 (ruling 02.09 (d)). This IS the"
    " file to label: `rows` is the draw, `pages` is the unit the gold is written on (ruling 03.09"
    " (b)) and `predicted` is every extracted row of those pages.",
}
"""What each window's record says it was drawn from. Per window and never one fixed sentence: the
line that shipped through 02.09 still read «C2 is unbought… re-draw after S4» after S4 had run and
the re-draw had happened, because it was a constant ([[a_reading_that_outlived_its_state]])."""


def population_state(window_id: str) -> str:
    """The record's own statement about its population, or a refusal naming the window."""
    if window_id not in POPULATION_STATE:
        raise SystemExit(
            f"draw_positions_50 REFUSED: no population statement for window {window_id!r} — a draw"
            " that could not say which population it came from would be labelled off unknown rows"
        )
    return POPULATION_STATE[window_id]


def image_of(channel: str | None, msg_id) -> str | None:
    """The page's own image under `data/annotation/promo_c2/posts_media/`, or None.

    Ruling 03.09 (b): the labeller reads the PAGE, so the record has to say which file that is. The
    store is gitignored and one leaflet page is one message is one file, `<handle>_<msg_id>.jpg`.
    None is an answer and not a gap: a `post_text` carrier is words, and its link is the whole of it.
    """
    if not channel:
        return None
    path = MEDIA / f"{str(channel).lstrip('@')}_{msg_id}.jpg"
    return str(path.relative_to(REPO_ROOT)) if path.exists() else None


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
        "image": image_of(evidence.get("channel"), evidence.get("msg_id")),
    }


def as_drawn(rows: list[dict]) -> str:
    """The draw's own identity: the rows WITHOUT `image`, hashed.

    `image` is a pointer to a file, not part of what was drawn, and the ruling adds it «a field, not
    a re-draw». So the anchor the labels are owed against is this projection — it is unchanged by
    the addition, while the FILE's sha necessarily moves, and the record says both
    ([[the_guard_hashes_the_half_that_cannot_move]]).
    """
    without = [{k: v for k, v in row.items() if k != "image"} for row in rows]
    return hashlib.sha256(
        json.dumps(without, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def pages_of(rows: list[dict]) -> list[dict]:
    """The distinct messages the drawn rows come from, sorted — the unit the gold is written on."""
    seen = {(row["channel"], row["msg_id"]) for row in rows}
    return [
        {"channel": channel, "msg_id": msg_id, "image": image_of(channel, msg_id)}
        for channel, msg_id in sorted(seen, key=lambda one: (str(one[0]), int(one[1])))
    ]


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
    for_labels = [for_the_labeller(row) for row in drawn]
    pages = pages_of(for_labels)
    # Ruling 03.09 (b): the gold is PAGE-level, so what it is scored against must be too. A page
    # carries up to 10 extracted rows and the labeller is handed no extraction, so a predicted set
    # of only the 50 drawn rows would make `completeness` measure which row the labeller happened
    # to pick. Both carriers, because two legs reading one message are two genuine readings.
    on_those_pages = [
        row for row in rows
        if ((row.get("evidence") or {}).get("channel"), (row.get("evidence") or {}).get("msg_id"))
        in {(page["channel"], page["msg_id"]) for page in pages}
    ]

    predicted_text = "".join(
        json.dumps(predicted(row), ensure_ascii=False, sort_keys=True) + "\n"
        for row in on_those_pages
    )

    record = {
        "contract": "docs/plans/promo-pulse-1.md K5 — the 50 positions the team lead labels into"
        " docs/labels-positions-50.jsonl. Rows carry the carrier and its link, never the"
        " extraction: the labeller must not see what he is grading.",
        "seed": SEED,
        "population": len(rows),
        "population_state": population_state(args.window),
        "chains": chains,
        "rows_drawn": len(drawn),
        "by_chain": {chain: sum(1 for row in drawn if row["chain"] == chain) for chain in chains},
        "rows": for_labels,
        "rows_sha256_as_drawn": as_drawn(for_labels),
        "anchor_note": "`image` is a POINTER added by ruling 03.09 (b), not part of the draw, so"
        " the file's own sha256 moved from 61b4fda7fdc83197… while `rows_sha256_as_drawn` — the"
        " same rows without that field — did not. The labels are owed against the rows, and their"
        " 50 row_ids are the ones the re-draw fixed.",
        "pages": pages,
        "pages_drawn_from": len(pages),
        "predicted_rows": len(on_those_pages),
        "predicted_sha256": hashlib.sha256(predicted_text.encode("utf-8")).hexdigest(),
        "predicted_scope": "every extracted row of the pages above, both carriers — what the"
        " page-level gold is scored against.",
    }
    args.out.write_text(
        json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.predicted.write_text(predicted_text, encoding="utf-8")
    print(f"{len(drawn)} of {len(rows)} positions, seed {SEED}, chains: {', '.join(chains)}")
    print(f"  rows sha256 as drawn  {record['rows_sha256_as_drawn'][:16]}…")
    print(f"  pages                 {len(pages)}, {sum(1 for one in pages if one['image'])} with an image")
    print(
        f"  predicted             {len(on_those_pages)} extracted rows on those pages,"
        f" sha256 {record['predicted_sha256'][:16]}…"
    )
    print(f"wrote {rel(args.out)} and {rel(args.predicted)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
