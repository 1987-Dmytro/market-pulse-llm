#!/usr/bin/env python3
"""Apply the operator's review verdicts back onto the labelled batches.

The review CSVs come back with one `operator_verdict` per sampled row: `ok`,
`unclear`, or `fix:field=value[,field=value...]`. Only the rows a verdict
actually changes are rewritten, and those get `annotator: "operator-reviewed"`
so the provenance of every corrected label is visible in the batch itself.

Re-running is a no-op: a verdict whose values are already in place is counted as
matching, not applied again.

    python3.11 scripts/apply_review.py
"""

import argparse
import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse.annotation import check_labels, parse_verdict
from market_pulse.registry import load_registry

DATA = REPO_ROOT / "data" / "annotation"
REVIEWED = "operator-reviewed"
PAIRS = (
    ("review_comments.csv", "comments_batch.jsonl", "comments"),
    ("review_posts.csv", "posts_batch.jsonl", "posts"),
)


def load_rows(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path}: not found")
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def apply_one(review: Path, batch: Path, kind: str, brand_ids: tuple[str, ...]) -> int:
    rows = load_rows(batch)
    by_id = {row["id"]: row for row in rows}
    with review.open(encoding="utf-8", newline="") as handle:
        verdicts = list(csv.DictReader(handle))

    changed = matching = unreviewed = 0
    print(f"\n{review.name} -> {batch.name} ({len(verdicts)} reviewed rows)")
    for line, entry in enumerate(verdicts, start=2):  # line 1 is the header
        try:
            wanted = parse_verdict(entry["operator_verdict"], kind)
        except ValueError as bad:
            raise SystemExit(f"{review.name} line {line}: {bad}") from bad
        if wanted is None:
            unreviewed += 1
            continue
        row = by_id.get(entry["id"])
        if row is None:
            raise SystemExit(f"{review.name} line {line}: {entry['id']} is not in {batch.name}")

        applied = {name: value for name, value in wanted.items() if row[name] != value}
        if not applied:
            matching += 1
            continue
        moves = ", ".join(f"{name}: {row[name]!r} -> {value!r}" for name, value in applied.items())
        row.update(applied, annotator=REVIEWED)
        bad = check_labels(row, kind, brand_ids)
        if bad:
            raise SystemExit(f"{review.name} line {line}: fix makes the row illegal: {bad[0]}")
        print(f"  {row['id']}: {moves}")
        changed += 1

    print(f"  {changed} changed · {matching} already matching · {unreviewed} without a verdict")
    if changed:
        batch.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
        )
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA, help=f"default: {DATA}")
    parser.add_argument("--registry", type=Path, default=REPO_ROOT / "config" / "registry.yaml")
    args = parser.parse_args(argv)

    brand_ids = tuple(brand.brand_id for brand in load_registry(args.registry).watchlist)
    total = sum(
        apply_one(args.data / review, args.data / batch, kind, brand_ids)
        for review, batch, kind in PAIRS
    )
    print(f"\n{total} row(s) rewritten with annotator {REVIEWED!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
