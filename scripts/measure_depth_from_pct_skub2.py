#!/usr/bin/env python3
"""Depth from the printed badge again, over B′'s 80 pairs — the product reading beside the bar. ($0)

Bar 2 has just failed at 0.4125, and the question the failure does not answer is the one question 7
actually asks: not "is the crossed-out number transcribed correctly" but "how far from the true
depth does each instrument land". The v1 measurement answered it on 61 pairs from 22 pages; this
one answers it on 80 from 26, including the four pages the old instrument could not read at all.

Same arithmetic, same three columns, same adequacy rule — deliberately, because two readings taken
under two rules are not two readings of the same thing. `scripts/measure_depth_from_pct.py` is the
implementation; what moves here is the population, the contract and the decision this is an input
to (the operator's 5c2 ruling, not the B′ design session, which has since happened).

    PYTHONPATH=src python3 scripts/measure_depth_from_pct_skub2.py

Writes `results/sku_depth_from_pct_skub2.json`. NO threshold is registered for any of it: it is a
candidate reading for the ruling, and its adequacy rule says in the record that it is this file's
own.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import measure_depth_from_pct as measurer  # noqa: E402

RECORD = REPO_ROOT / "results" / "sku_b_positions_skub2.json"
PAIRS = REPO_ROOT / "results" / "sku_b_pair_verdicts_skub2.json"
OUT = REPO_ROOT / "results" / "sku_depth_from_pct_skub2.json"

CONTRACT = "docs/PROMPT-skub2-close.md deliverable 2 — depth-from-pct v2 over the 80 pairs"

CLASS = (
    "MEASUREMENT for the operator's 5c2 ruling. NO threshold is registered and nothing here is a"
    " bar: it prices two candidate depth instruments against the team lead's own read of the pages,"
    " on the population B′ bought, so the product decision has a number under it"
)

ADEQUACY = (
    "adequate for a weekly median = every pair within 2 pp of the true depth AND the median within"
    " 1 pp. STATED HERE, not registered — the same rule the v1 measurement stated, unchanged so the"
    " two readings are comparable. The real threshold is the operator's to set at the 5c2 ruling"
)


def main(argv: list[str] | None = None) -> int:
    return measurer.main(
        argv,
        contract=CONTRACT,
        class_note=CLASS,
        adequacy=ADEQUACY,
        record=RECORD,
        pairs=PAIRS,
        out=OUT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
