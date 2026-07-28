#!/usr/bin/env python3
"""Export 50 generated rows for the operator's pre-registered QA pass.

The gate was fixed before the sample was drawn
(knowledge/decisions/synthetic-sarcasm-augmentation.md): **>= 80% of the 50 rows
must come back `ok`**, or the flagged failure patterns are regenerated once. The
executor does not score this — it exports the sample and stops (SPEC §10).

`operator_verdict` takes the same three forms as the review CSVs, so the syntax
is one the operator already uses (`market_pulse.annotation.parse_verdict`):

    ok                    the text reads as corpus sarcasm and the labels fit
    fix:sentiment=neutral one label is wrong; counts against the 80%
    unclear               not usable as a sarcasm example; counts against the 80%

Seed 42, plain random sample — not stratified: the question is whether the file
as a whole passes, so every row must have the same chance of being looked at.

    python3 scripts/make_synthetic_qa.py
"""

import csv
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse.annotation import row_state

SOURCE = REPO_ROOT / "data" / "annotation" / "synthetic_sarcasm.jsonl"
OUT = REPO_ROOT / "data" / "annotation" / "synthetic_qa.csv"
SEED = 42
SAMPLE = 50
COLUMNS = ("id", "language", "text", "sentiment", "sarcasm", "intents", "operator_verdict")


def main() -> int:
    if not SOURCE.exists():
        raise SystemExit(f"{SOURCE}: not found — generate the rows first")
    rows = [
        json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    unlabelled = [row["id"] for row in rows if row_state(row, "comments") != "labeled"]
    if unlabelled:
        raise SystemExit(
            f"{SOURCE}: {len(unlabelled)} rows are not fully labelled: {unlabelled[:5]}"
        )
    if len(rows) < SAMPLE:
        raise SystemExit(f"{SOURCE}: {len(rows)} rows, need at least {SAMPLE}")

    sample = random.Random(SEED).sample(rows, SAMPLE)
    sample.sort(key=lambda row: row["id"])
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(COLUMNS))
        writer.writeheader()
        for row in sample:
            writer.writerow(
                {
                    **{name: row[name] for name in COLUMNS if name in row},
                    "intents": json.dumps(row["intents"], ensure_ascii=False),
                    "operator_verdict": "",
                }
            )
    print(f"{OUT}: {SAMPLE} of {len(rows)} rows, seed {SEED}")
    print(f"gate: >= 80% 'ok' ({int(SAMPLE * 0.8)} of {SAMPLE}) — scored by the operator, not here")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
