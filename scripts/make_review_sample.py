#!/usr/bin/env python3
"""Export the slice of the labelled batches the operator reviews by hand.

300 comments stratified by (language, sentiment) with the sarcastic cells drawn 3x,
and 150 posts by post_type with `launch` drawn 3x: both flags are the ones the
guidelines call hardest, so the review budget goes where a wrong label costs most.
`operator_verdict` is left empty for the reviewer — `ok`, `fix:<value>` or `unclear`.

Amendment 3.1 removes EN from the gates, not from review: all four languages the
batch carries are stratified over. Seed 42, so a rerun reproduces the same sample.

    python3.11 scripts/make_review_sample.py
"""

import csv
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse.annotation import COMMENT_LABELS, POST_LABELS, row_state, stratified_sample

OUT = REPO_ROOT / "data" / "annotation"
SEED = 42
N_COMMENTS = 300
N_POSTS = 150
OVERSAMPLE = 3
JSON_CELLS = ("intents", "brands")


def load_labeled(name: str, kind: str) -> list[dict]:
    path = OUT / name
    if not path.exists():
        raise SystemExit(f"{path}: not found — label the batch first")
    rows = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    labeled = [row for row in rows if row_state(row, kind) == "labeled"]
    if not labeled:
        raise SystemExit(f"{path}: no labelled rows to review")
    print(f"{path.name}: {len(labeled)} labelled of {len(rows)}")
    return labeled


def print_table(title: str, table: dict) -> None:
    print(f"\n{title}")
    header = f"{'stratum':<36}{'pool':>8}{'picked':>8}"
    print(header)
    print("-" * len(header))
    for name, (pool, picked) in table.items():
        label = " / ".join(str(part) for part in (name if isinstance(name, tuple) else (name,)))
        print(f"{label:<36}{pool:>8}{picked:>8}")
    total = (sum(pool for pool, _ in table.values()), sum(picked for _, picked in table.values()))
    print(f"{'TOTAL':<36}{total[0]:>8}{total[1]:>8}")


def write(rows: list[dict], labels: dict, name: str) -> Path:
    columns = ["id", "text", *labels, "operator_verdict"]
    path = OUT / name
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            cell = {key: row[key] for key in columns if key in row}
            for key in JSON_CELLS:
                if key in cell:
                    cell[key] = json.dumps(cell[key], ensure_ascii=False)
            writer.writerow({**cell, "operator_verdict": ""})
    return path


def count_rows(path: Path) -> int:
    """Data rows, not physical lines — a post text carries its own newlines."""
    with path.open(encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.reader(handle)) - 1


def main() -> int:
    rng = random.Random(SEED)

    comments, table = stratified_sample(
        load_labeled("comments_batch.jsonl", "comments"),
        key=lambda row: (row["language"], row["sentiment"], row["sarcasm"]),
        total=N_COMMENTS,
        rng=rng,
        weight_of=lambda name: OVERSAMPLE if name[2] else 1,
    )
    print_table("comments — (language, sentiment, sarcasm), sarcastic cells 3x", table)

    posts, table = stratified_sample(
        load_labeled("posts_batch.jsonl", "posts"),
        key=lambda row: row["post_type"],
        total=N_POSTS,
        rng=rng,
        weight_of=lambda name: OVERSAMPLE if name == "launch" else 1,
    )
    print_table("posts — post_type, launch 3x", table)

    print(f"\nseed {SEED}")
    for path in (
        write(comments, COMMENT_LABELS, "review_comments.csv"),
        write(posts, POST_LABELS, "review_posts.csv"),
    ):
        print(f"{path}: {count_rows(path)} rows for review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
