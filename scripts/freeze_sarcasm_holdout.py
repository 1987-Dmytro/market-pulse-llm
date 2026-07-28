#!/usr/bin/env python3
"""Freeze the hybrid G1b holdout (operator-approved 2026-07-28, option 1a).

The fresh corpus alone cannot fill a sarcasm holdout — wave 2 mined every
comment outside the test and train threads and found 971, of which only a small
share are ironic. The approved fallback tops the fresh rows up from the mined
training pool: those rows are *moved*, not copied, so nothing that is scored
here can ever be trained on.

Two constraints bound the top-up, and they are the reason the holdout is smaller
than the 180 the operator asked for:

* a mined row whose thread also holds a scoreable `comments_train.jsonl` row
  cannot move — the train row stays in training and would leak the thread;
* a mined row whose text appears verbatim in a training row cannot move either.

What is left after those two filters is taken whole (seed 42 only decides which
rows are dropped when more are eligible than needed).

    python3.11 scripts/freeze_sarcasm_holdout.py
"""

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

ANNOTATION = REPO_ROOT / "data" / "annotation"
FROZEN = REPO_ROOT / "data" / "frozen"
POOL = ANNOTATION / "sarcasm_holdout_pool.jsonl"
MINED = ANNOTATION / "sarcasm_candidates.jsonl"
HOLDOUT = FROZEN / "sarcasm_holdout.jsonl"
SEED = 42
TARGET = 180


def load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path}: not found")
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def write(rows: list[dict], path: Path) -> None:
    path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False) + "\n"
            for row in sorted(rows, key=lambda r: r["id"])
        ),
        encoding="utf-8",
    )


def thread_of(row: dict) -> tuple:
    return (row["channel"], row["parent_msg_id"])


def normalised(text: str) -> str:
    return " ".join(text.split()).lower()


def sarcastic(rows: list[dict]) -> list[dict]:
    return [row for row in rows if row["sarcasm"] and not row["unclear"]]


def table(rows: list[dict], field: str) -> str:
    counts = Counter(row[field] for row in rows)
    return " · ".join(f"{name} {count}" for name, count in sorted(counts.items()))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="overwrite an existing freeze")
    args = parser.parse_args(argv)
    if HOLDOUT.exists() and not args.force:
        raise SystemExit(f"{HOLDOUT}: already frozen — immutable without operator approval")

    pool, mined = load(POOL), load(MINED)
    train = load(FROZEN / "comments_train.jsonl")
    test = load(FROZEN / "comments_test.jsonl")

    train_threads = {thread_of(row) for row in train if not row["unclear"]}
    test_threads = {thread_of(row) for row in test}
    train_texts = {normalised(row["text"]) for row in train if not row["unclear"]}

    fresh = sarcastic(pool)
    print(f"wave-2 pool: {len(pool)} labelled · {len(fresh)} sarcastic and scoreable")

    pot = sarcastic(mined)
    blocked_thread = [row for row in pot if thread_of(row) in train_threads | test_threads]
    eligible = [
        row
        for row in pot
        if row not in blocked_thread and normalised(row["text"]) not in train_texts
    ]
    blocked_text = len(pot) - len(blocked_thread) - len(eligible)
    print(f"mined pool: {len(pot)} sarcastic and scoreable")
    print(f"  - {len(blocked_thread):>3} share a thread with a scoreable train row")
    print(f"  - {blocked_text:>3} repeat a training row's text verbatim")
    print(f"  = {len(eligible):>3} movable")

    need = TARGET - len(fresh)
    if len(eligible) > need:
        moved = random.Random(SEED).sample(sorted(eligible, key=lambda r: r["id"]), need)
    else:
        moved = eligible
        print(f"\nshort of the {TARGET}-row target by {need - len(moved)}: the pool is exhausted")

    holdout = fresh + moved
    kept = [row for row in mined if row["id"] not in {r["id"] for r in moved}]

    holdout_threads = {thread_of(row) for row in holdout}
    assert not holdout_threads & test_threads, "holdout shares a thread with the test set"
    assert not holdout_threads & train_threads, "holdout shares a thread with the train pool"
    remaining_texts = train_texts | {normalised(row["text"]) for row in kept if not row["unclear"]}
    overlap = [row["id"] for row in holdout if normalised(row["text"]) in remaining_texts]
    assert not overlap, f"holdout text also in a training row: {overlap[:3]}"

    write(holdout, HOLDOUT)
    write(kept, MINED)
    # The pristine copy is the validator's diff baseline; the moved rows are gone
    # from the batch on purpose, so they leave the baseline too.
    pristine = MINED.with_suffix(".pristine.jsonl")
    if pristine.exists():
        write(
            [row for row in load(pristine) if row["id"] in {r["id"] for r in kept}],
            pristine,
        )

    left = len(sarcastic(kept)) + len(sarcastic(train))
    print(f"\nholdout: {len(holdout)} rows · {len(fresh)} fresh corpus · {len(moved)} moved")
    print(f"  language  {table(holdout, 'language')}")
    print(f"  sentiment {table(holdout, 'sentiment')}")
    print(f"  threads   {len(holdout_threads)} · 0 shared with test · 0 shared with train")
    print(f"  sha256    {hashlib.sha256(HOLDOUT.read_bytes()).hexdigest()}")
    print(
        f"\ntraining keeps {left} sarcastic scoreable rows"
        f" ({len(sarcastic(kept))} mined + {len(sarcastic(train))} train pool)"
    )
    mined_threads = {thread_of(row) for row in kept if not row["unclear"]}
    print(
        f"residual: {len(holdout_threads & mined_threads)} holdout thread(s) still hold a"
        " scoreable row of the mined training pool"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
