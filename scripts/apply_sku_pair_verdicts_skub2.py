#!/usr/bin/env python3
"""Bar 2 under B′: the team lead's read of the 80 price pairs, onto instrument v2's own rows. ($0)

The same shape as `scripts/apply_sku_pair_verdicts.py` and none of its numbers. That file holds the
v4 read — 45 keys over 61 rows, the pilot's sealed evidence — and this one holds B′'s, so the guards
are imported and the dictation is local: a table of numbers is the artifact here, and a second copy
of the matcher would be a second rule.

Two things this read has that the first one did not:

- **a checksum line the table contradicts.** `docs/PROMPT-skub2-close.md` states 54 keys; the table
  under it dictates 64, which is also how many distinct `(file, promo, old)` boxes the dump carries.
  See `EXPECTED` — the number is not quietly retyped, it is asserted, deviated and printed.
- **a prior read it extends.** 61 of the 80 rows are the v4 dictation, unchanged; `carried_forward`
  checks that against the sealed file rather than believing the contract's sentence about it, and
  refuses any pair whose verdict moved.

    PYTHONPATH=src python3 scripts/apply_sku_pair_verdicts_skub2.py

Writes `results/sku_b_pair_verdicts_skub2.json`, which `scripts/sku_bar_verdicts.py` reads to give
bar 2 its value. The v4 read, the v4 dump and every registration are untouched.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import apply_sku_pair_verdicts as applier  # noqa: E402

RECORD = REPO_ROOT / "results" / "sku_b_positions_skub2.json"
OUT = REPO_ROOT / "results" / "sku_b_pair_verdicts_skub2.json"
PRIOR = REPO_ROOT / "results" / "sku_b_pair_verdicts.json"

PHASE = "sku-b (B′) — bar 2, the team lead's read applied to the skub2 dump"
CONTRACT = "docs/PROMPT-skub2-close.md — the team lead's verdicts table"
READ_SCOPE = (
    "all 80 pairs over 26 page images — 74 against the team lead's documented printed values from"
    " the v4 and decomposition reads (same reader, same pages) and 6 from the one new page 4446,"
    " read 2026-08-12"
)

DICTATED = (
    ("4341.jpg", 37.9, 75.9, 1, "correct", None),
    ("4341.jpg", 131.5, 264.5, 1, "wrong", 264.90),
    ("4342.jpg", 66.9, 135.2, 1, "wrong", 135.90),
    ("4342.jpg", 75.9, 152.2, 1, "wrong", 152.90),
    ("4343.jpg", 17.9, 29.9, 1, "correct", None),
    ("4344.jpg", 27.9, 39.99, 1, "wrong", 39.90),
    ("4350.jpg", 49.9, 71.9, 1, "wrong", 71.50),
    ("4352.jpg", 12.9, 19.99, 1, "wrong", 19.90),
    ("4352.jpg", 30.9, 44.9, 1, "wrong", 44.40),
    ("4360.jpg", 21.9, 40.9, 1, "correct", None),
    ("4360.jpg", 23.5, 42.5, 2, "wrong", 42.90),
    ("4360.jpg", 42.9, 80.9, 1, "correct", None),
    ("4360.jpg", 24.9, 46.9, 1, "correct", None),
    ("4360.jpg", 29.9, 55.9, 1, "correct", None),
    ("4381.jpg", 74.5, 149.0, 1, "wrong", 149.50),
    ("4381.jpg", 99.5, 199.0, 1, "wrong", 199.90),
    ("4382.jpg", 24.5, 49.0, 2, "correct", None),
    ("4382.jpg", 39.5, 79.0, 2, "wrong", 79.90),
    ("4383.jpg", 13.9, 19.9, 1, "correct", None),
    ("4383.jpg", 119.9, 159.9, 2, "correct", None),
    ("4384.jpg", 15.5, 26.75, 2, "wrong", 26.80),
    ("4385.jpg", 59.9, 89.9, 2, "wrong", 89.40),
    ("4385.jpg", 59.9, 90.0, 1, "wrong", 90.70),
    ("4385.jpg", 68.9, 103.0, 1, "wrong", 103.70),
    ("4402.jpg", 46.9, 79.9, 1, "correct", None),
    ("4403.jpg", 79.9, 111.9, 1, "correct", None),
    ("4404.jpg", 11.7, 17.7, 1, "wrong", 17.80),
    ("4404.jpg", 20.5, 29.5, 1, "correct", None),
    ("4404.jpg", 26.9, 39.9, 1, "wrong", 39.70),
    ("4404.jpg", 26.5, 39.9, 1, "wrong", 39.80),
    ("4404.jpg", 15.9, 22.9, 1, "correct", None),
    ("4404.jpg", 119.9, 171.9, 1, "wrong", 171.30),
    ("4405.jpg", 26.5, 51.9, 1, "wrong", 51.50),
    ("4405.jpg", 41.5, 80.9, 1, "wrong", 80.50),
    ("4405.jpg", 39.9, 76.9, 1, "correct", None),
    ("4405.jpg", 16.3, 29.9, 1, "correct", None),
    ("4405.jpg", 17.5, 31.9, 1, "correct", None),
    ("4405.jpg", 18.9, 34.9, 1, "correct", None),
    ("4405.jpg", 33.9, 61.9, 1, "correct", None),
    ("4405.jpg", 22.3, 40.9, 1, "correct", None),
    ("4405.jpg", 24.5, 44.9, 1, "correct", None),
    ("4426.jpg", 103.9, 230.0, 3, "wrong", 230.90),
    ("4427.jpg", 17.9, 35.0, 1, "wrong", 35.80),
    ("4427.jpg", 22.3, 44.0, 1, "wrong", 44.90),
    ("4428.jpg", 25.5, 37.0, 2, "wrong", 37.90),
    ("4428.jpg", 117.9, 157.0, 2, "wrong", 157.90),
    ("4440.jpg", 64.5, 93.0, 3, "wrong", 93.90),
    ("4446.jpg", 36.9, 68.9, 1, "correct", None),
    ("4446.jpg", 24.9, 46.9, 1, "wrong", 46.40),
    ("4446.jpg", 105.9, 196.9, 1, "correct", None),
    ("4446.jpg", 114.9, 212.9, 1, "correct", None),
    ("4446.jpg", 88.9, 165.9, 1, "correct", None),
    ("4446.jpg", 17.5, 32.9, 1, "correct", None),
    ("4467.jpg", 68.9, 139.9, 1, "wrong", 139.40),
    ("4467.jpg", 75.9, 152.9, 1, "correct", None),
    ("4468.jpg", 18.3, 40.0, 1, "wrong", 40.90),
    ("4468.jpg", 26.5, 58.0, 1, "wrong", 58.90),
    ("4468.jpg", 36.3, 80.0, 1, "wrong", 80.90),
    ("4470.jpg", 16.9, 29.99, 1, "wrong", 29.80),
    ("4471.jpg", 28.9, 41.99, 2, "wrong", 41.90),
    ("4508.jpg", 29.9, 55.9, 2, "correct", None),
    ("4508.jpg", 21.9, 36.9, 2, "wrong", 36.50),
    ("4508.jpg", 24.9, 46.9, 1, "correct", None),
    ("4508.jpg", 22.9, 41.9, 2, "correct", None),
)
"""`docs/PROMPT-skub2-close.md` §"The team lead's verdicts", transcribed row for row.

`(file suffix, price_promo, price_old, n, verdict, printed_old)`, same columns as the v4 table and
resolved against the dump the same way — a suffix that reaches two pages is a refusal, not a pick."""

CONTRACT_CHECKSUMS = {
    "keys": 54,
    "rows": 80,
    "correct_rows": 33,
    "wrong_rows": 47,
    "accuracy_4dp": 0.4125,
}
"""The contract's checksum line, transcribed verbatim: "keys 54, rows Σn = 80, correct = 33,
wrong = 47, accuracy = 33/80 = 0.4125". Kept as its own constant because `EXPECTED` departs from
it in exactly one field and a reader has to be able to see both."""

EXPECTED = {**CONTRACT_CHECKSUMS, "keys": 64}
"""What is asserted. Four of the five numbers are the contract's own; `keys` is 64 because the table
above dictates 64 of them and the dump carries exactly 64 distinct `(file, promo, old)` boxes.

Dv237. `keys` is the one field in that line the join OVER-DETERMINES: every dump pair row is claimed
exactly once and no row is claimed twice, which forces the key count and leaves it unable to hide a
mistyped verdict. The four that CAN hide one — rows, correct, wrong, accuracy — are the contract's
untouched, and all four verify. 54 is a slip off the v4 line's 45 (same shape, digits swapped); no
reading of this population gives 54 (keys with n=1 give 50, pages give 26, the v4 read gives 45)."""

STATED_WHY = (
    "the contract states 54 keys and its own table dictates 64, which is also how many distinct"
    " (file, promo, old) price boxes the dump carries. The join claims every one of the 80 pair"
    " rows exactly once and none twice, so 64 is forced by the data and cannot conceal a"
    " transcription error; the four counts that could — rows, correct, wrong, accuracy — are the"
    " contract's, unedited, and all four hold. Dv237 of docs/reports/skub2-run.md"
)

DIAGNOSIS = (
    "promo 80/80 correct · printed % 80/80 correct · crossed-out old 33/80 — the superscript family"
    " again; dense multi-item pages read their olds better (4405: 7/9, 4446: 5/6) than single-hero"
    " posters"
)
"""The team lead's diagnosis line, carried verbatim into this record and into the ADR."""

THIS = applier.Read(
    phase=PHASE,
    contract=CONTRACT,
    scope=READ_SCOPE,
    dictated=DICTATED,
    expected=EXPECTED,
    diagnosis=DIAGNOSIS,
    record=RECORD,
    out=OUT,
    stated=CONTRACT_CHECKSUMS,
    stated_why=STATED_WHY,
    prior=PRIOR,
)


def main(argv: list[str] | None = None) -> int:
    return applier.main(argv, THIS)


if __name__ == "__main__":
    raise SystemExit(main())
