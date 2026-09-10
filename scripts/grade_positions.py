#!/usr/bin/env python3
"""K6 — the S1 grader: completeness and price accuracy against the team lead's 50 positions. $0.

`docs/PHASE-promo-pulse-1.md` §2 S1, as ruled at the 30.08 review (SP-0 q1):

    completeness    >= 0.90   gold positions matched on (brand surface form, product, volume)
    price accuracy  >= 0.95   over the PROMO PRICE ONLY — the green leg, 80/80 — exact after
                              normalisation
    printed -N% and the extracted old price are READINGS, no bar.

The denominator is the ruling's, and it is the whole reason this grader can be written before the
gold exists: at the PAIR the bar is unreachable by measurement — `results/sku_bar_verdicts_skub2.json`
reads 0.4125 on 33 of 80 pairs — so a grader that scored the pair would have been measuring a bar
nothing can pass. The old price is still reported, beside the bar and never inside it.

**The match rule is stated, not implied.** Completeness needs to decide when a predicted row IS a
gold row, and every choice in that rule moves the number. This one: brand surface form, product and
volume, each normalised by `aggregates.promo_key` (NFC, lower, whitespace-collapsed), volume
additionally split into (value, unit) so «900 г» and «900г» are one thing and «0.9 кг» is not. A
prediction matches at most one gold row and a gold row is matched at most once — a dict keyed by the
triple would be last-wins and would quietly forgive a duplicate ([[select_one_row_refuse_ambiguity]]).

Written and driven against SYNTHETIC gold before any real gold existed (`tests/test_grade_positions.py`)
— and it read the sample, not the schema: the real `results/positions_50_predicted.jsonl` carries
`size_value` + `size_unit` where the gold carries `volume`, and `badge_pct` where the synthetic row
carried `discount_pct_printed`, so as shipped this grader scored 0.0 with all 205 rows unmatched
(ruling 10.09 (rr)). Both spellings are read below; neither the match rule nor the bars moved.

    python3.11 scripts/grade_positions.py --gold docs/labels-positions-50.jsonl \\
        --predicted results/positions_50_predicted.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse.aggregates import promo_key  # noqa: E402

OUT = REPO_ROOT / "results" / "grade_positions_50.json"

BARS = {"completeness": 0.90, "price_accuracy": 0.95}
"""The phase spec's two, as ruled. Named here so the record can print the bar beside the reading."""

_VOLUME = re.compile(r"^\s*([0-9]+(?:[.,][0-9]+)?)\s*([^\d\s]+)\s*$")
"""«900 г» → (900.0, 'г'). A volume that does not parse is compared as normalised text instead —
refusing it would drop a gold row out of the denominator and lift the metric
([[an_exclusion_rule_built_from_failures]])."""


def rows(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path} is missing — the grader may not score against nothing")
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def volume_key(value) -> tuple:
    match = _VOLUME.match(str(value or ""))
    if not match:
        return ("text", promo_key(value or ""))
    return ("qty", float(match.group(1).replace(",", ".")), promo_key(match.group(2)))


def volume_surface(row: dict) -> str | None:
    """The row's volume as printed — one field with two spellings, not two fields.

    The gold writes `volume` («400 г»); `positions_50_predicted.jsonl` writes `size_value` +
    `size_unit` (400.0 · «г»), because `draw_positions_50.predicted()` reads the store's own columns.
    A row carrying neither has no volume at all: `None` here, no identity below, matched by nothing
    and counted — never a crash and never an empty key that two such rows share (ruling (rr) 3).
    """
    if row.get("volume") not in (None, ""):
        return str(row["volume"])
    value, unit = row.get("size_value"), row.get("size_unit")
    if value in (None, "") or unit in (None, ""):
        return None
    return f"{value} {unit}"


def identity(row: dict) -> tuple | None:
    """The triple a prediction and a gold row are matched on. One rule, one place."""
    volume = volume_surface(row)
    if volume is None:
        return None
    return (promo_key(row.get("brand") or ""), promo_key(row.get("product") or ""), volume_key(volume))


def printed_badge(row: dict):
    """The printed −N% of a prediction row: `badge_pct` as the producer writes it, else the older
    `discount_pct_printed` spelling. A reading, never a bar (review 30.08 SP-0 q1)."""
    if row.get("badge_pct") is not None:
        return row["badge_pct"]
    return row.get("discount_pct_printed")


def price(value) -> float | None:
    """A price as a number, or None. `49,90` and `49.90` are one price; `49.9` is the same number.

    Comparison is on the NUMBER after this, not on the text: a grader that compared strings would
    score the model's formatting and call it accuracy.
    """
    if value in (None, ""):
        return None
    try:
        return round(float(str(value).replace(",", ".").replace(" ", "")), 2)
    except ValueError:
        return None


def grade(gold: list[dict], predicted: list[dict]) -> dict:
    unmatched = list(predicted)
    matched, missed = [], []
    for want in gold:
        key = identity(want)
        hit = None if key is None else next((row for row in unmatched if identity(row) == key), None)
        if hit is None:
            missed.append(want)
            continue
        unmatched.remove(hit)
        matched.append((want, hit))

    scored = [(want, got) for want, got in matched if price(want.get("price_promo")) is not None]
    right = [pair for pair in scored if price(pair[0]["price_promo"]) == price(pair[1].get("price_promo"))]

    badge = [
        (want.get("badge_pct"), printed_badge(got))
        for want, got in matched
        if want.get("badge_pct") is not None
    ]
    carries_old = any(row.get("price_old") is not None for row in predicted)
    old = (
        [
            (price(want.get("price_old")), price(got.get("price_old")))
            for want, got in matched
            if want.get("price_old") is not None
        ]
        if carries_old
        else []
    )
    return {
        "bars": {
            "completeness": {
                "value": round(len(matched) / len(gold), 4) if gold else None,
                "bar": BARS["completeness"],
                "matched": len(matched),
                "gold": len(gold),
                "held": (len(matched) / len(gold)) >= BARS["completeness"] if gold else False,
            },
            "price_accuracy": {
                "value": round(len(right) / len(scored), 4) if scored else None,
                "bar": BARS["price_accuracy"],
                "right": len(right),
                "scored": len(scored),
                "denominator": "the PROMO price only, over matched rows whose gold carries one —"
                " review 30.08 SP-0 q1",
                "held": (len(right) / len(scored)) >= BARS["price_accuracy"] if scored else False,
            },
        },
        "readings": {
            "printed_badge": {
                "n": len(badge),
                "agree": sum(1 for want, got in badge if want == got),
                "note": "a reading, no bar (review 30.08 SP-0 q1)",
            },
            "price_old": {
                "n": len(old),
                "agree": sum(1 for want, got in old if want == got),
                "note": "stored and flagged, never printed on the screen — SPEC 3.21 (4), 3.18 (1)"
                if carries_old
                else "not carried — the prediction file has no price_old field; a reading with no"
                " prediction is not a disagreement",
            },
            "predicted_rows_no_gold_row_claims": len(unmatched),
            "gold_rows_no_prediction_reached": len(missed),
        },
        "match_rule": "(brand surface form, product, volume) each normalised by"
        " aggregates.promo_key; volume additionally split into (value, unit). One prediction"
        " matches at most one gold row and one gold row is matched at most once.",
        "missed": [identity(row) for row in missed],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, default=REPO_ROOT / "docs" / "labels-positions-50.jsonl")
    parser.add_argument("--predicted", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    record = {
        "contract": "docs/plans/promo-pulse-1.md K6 — the S1 grader ($0)",
        "gold": str(args.gold),
        "predicted": str(args.predicted),
        **grade(rows(args.gold), rows(args.predicted)),
    }
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for name, block in sorted(record["bars"].items()):
        print(f"{name:<16} {block['value']} against {block['bar']} — {'HOLDS' if block['held'] else 'RED'}")
    print(f"readings: {json.dumps(record['readings'], ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
