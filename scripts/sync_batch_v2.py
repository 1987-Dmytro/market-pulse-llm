#!/usr/bin/env python3
"""Sync the operator's v2 corrections back into the annotation batch.

`data/frozen/` is the authority for the test set, but the batch it was drawn
from is upstream of `scripts/freeze_testsets.py --force`. Left stale, the batch
still holds the pre-v2 labels for the eleven corrected rows, and a forced
rebuild would quietly resurrect them.

The frozen files are the source of truth here: for every row the test set holds
(plus `@msuaaaa:9534`, which v2 moved to the train pool), the batch row is
brought into line with it. Nothing else is touched — the recalibration of the
train sources is a separate change and is not synced back.

The dry run then rebuilds the test file's bytes out of the synced batch and
compares them with the frozen file. It cannot re-run the split itself: the
corrections move rows between strata, so a fresh draw would legitimately select
different rows. What it proves is the thing that matters — no stale v1 label
survives upstream of the freeze.

    python3.11 scripts/sync_batch_v2.py
"""

import argparse
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH = REPO_ROOT / "data" / "annotation" / "comments_batch.jsonl"
FROZEN = REPO_ROOT / "data" / "frozen"
MOVED = "@msuaaaa:9534"
LABELS = ("sentiment", "sarcasm", "intents", "unclear", "annotator", "notes")


def load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path}: not found")
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def serialise(rows: list[dict]) -> str:
    """The exact bytes freeze_testsets.py and refreeze_v2.py write."""
    return "".join(
        json.dumps(row, ensure_ascii=False) + "\n" for row in sorted(rows, key=lambda r: r["id"])
    )


def truth() -> dict:
    """v2 labels by id: the whole test set plus the row v2 moved out of it."""
    rows = {row["id"]: row for row in load(FROZEN / "comments_test.jsonl")}
    moved = {row["id"]: row for row in load(FROZEN / "comments_train.jsonl")}.get(MOVED)
    if moved is None:
        raise SystemExit(f"{MOVED} is not in the train pool — has v2 been applied?")
    rows[MOVED] = moved
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="dry run only, do not write")
    args = parser.parse_args(argv)

    batch = load(BATCH)
    by_id = {row["id"]: row for row in batch}
    frozen = truth()

    changed = 0
    for row_id, source in frozen.items():
        row = by_id.get(row_id)
        if row is None:
            raise SystemExit(f"{row_id} is in the frozen set but not in the batch")
        moves = {name: source[name] for name in LABELS if row[name] != source[name]}
        if not moves:
            continue
        print(f"  {row_id}: " + ", ".join(f"{n}: {row[n]!r} -> {v!r}" for n, v in moves.items()))
        row.update(moves)
        changed += 1

    print(f"{changed} batch row(s) brought into line with the v2 freeze")
    if changed and not args.check:
        BATCH.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in batch), encoding="utf-8"
        )

    # Dry run: the test set rebuilt out of the synced batch, byte for byte.
    test_path = FROZEN / "comments_test.jsonl"
    rebuilt = serialise([by_id[row_id] for row_id in {r["id"] for r in load(test_path)}])
    frozen_bytes = test_path.read_text(encoding="utf-8")
    same = rebuilt == frozen_bytes
    print(f"\ndry run: {test_path.relative_to(REPO_ROOT)} rebuilt from the batch")
    print(f"  frozen  {hashlib.sha256(frozen_bytes.encode('utf-8')).hexdigest()}")
    print(f"  rebuilt {hashlib.sha256(rebuilt.encode('utf-8')).hexdigest()}")
    print("  BYTE-IDENTICAL" if same else "  DIFFERS — the batch is still out of sync")
    return 0 if same else 1


if __name__ == "__main__":
    raise SystemExit(main())
