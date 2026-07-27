#!/usr/bin/env python3
"""One-shot: apply the operator's approved corrections and refreeze the test set v2.

The frozen sets are immutable (CLAUDE.md). This script exists because the
operator approved these 11 corrections on 2026-07-27 — before any baseline
number was scored — and it is kept in the repo so the diff between v1 and v2 has
a readable provenance instead of a hand edit nobody can audit.

Ten rows get a label fixed in place. The eleventh, `@msuaaaa:9534`, becomes
`unclear` and so cannot stay in a test set the guidelines keep clear of unclear
rows: it moves to the train pool and a replacement is drawn from that pool in
the same stratum. The replacement must be the only scorable row of its thread —
otherwise its thread-mates would stay behind in train and leak the thread it now
belongs to.

Running it twice fails: the corrected ids are no longer in the test set.

    python3.11 scripts/refreeze_v2.py
"""

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FROZEN = REPO_ROOT / "data" / "frozen"
SEED = 42
APPROVED = "2026-07-27"
REVIEWED = "operator-reviewed"

# Operator's verdicts, 2026-07-27. `@msuaaaa:9534` is the swap — see MOVED.
CORRECTIONS = {
    "@VARUS_channel:10658": {"sarcasm": True},
    "@VARUS_channel:11312": {"sarcasm": True},
    "@VARUS_channel:19177": {"sarcasm": True},
    "@VARUS_channel:58": {"sarcasm": True},
    "@VARUS_channel:7979": {"sarcasm": True},
    "@VARUS_channel:8120": {"sarcasm": True},
    "@VARUS_channel:9797": {"sarcasm": True},
    "@msuaaaa:5534": {"sarcasm": True},
    "@VARUS_channel:15718": {"sentiment": "negative"},
    "@msuaaaa:8175": {"sentiment": "negative", "sarcasm": True},
    "@msuaaaa:9534": {"unclear": True},
}
MOVED = "@msuaaaa:9534"


def load(path: Path) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def thread_of(row: dict) -> tuple:
    return (row["channel"], row["parent_msg_id"])


def is_thin(row: dict) -> bool:
    """The oversampled cells of the split — kept in step with freeze_testsets.py."""
    return bool(row["sarcasm"]) or "packaging" in row["intents"]


def stratum(row: dict) -> tuple:
    return (row["language"], row["sentiment"], is_thin(row))


def scorable(rows: list[dict]) -> list[dict]:
    return [row for row in rows if not row["unclear"]]


def apply_corrections(test: list[dict]) -> list[dict]:
    by_id = {row["id"]: row for row in test}
    changed = []
    for row_id, fields in CORRECTIONS.items():
        row = by_id.get(row_id)
        if row is None:
            raise SystemExit(f"{row_id} is not in the test set — v2 already applied?")
        moves = {name: value for name, value in fields.items() if row[name] != value}
        if not moves:
            raise SystemExit(f"{row_id} already carries {fields} — v2 already applied?")
        print(f"  {row_id}: " + ", ".join(f"{n}: {row[n]!r} -> {v!r}" for n, v in moves.items()))
        row.update(moves, annotator=REVIEWED)
        changed.append(row)
    return changed


def pick_replacement(train: list[dict], want: tuple, test_threads: set) -> dict:
    """A same-stratum row whose whole scorable thread can move to the test side."""
    size = Counter(thread_of(row) for row in scorable(train))
    eligible = sorted(
        (
            row
            for row in scorable(train)
            if stratum(row) == want
            and thread_of(row) not in test_threads
            and size[thread_of(row)] == 1
        ),
        key=lambda row: row["id"],
    )
    if not eligible:
        raise SystemExit(f"no replacement available in stratum {want}")
    print(f"\n{len(eligible)} eligible replacements in stratum {want}")
    return random.Random(SEED).choice(eligible)


def write(rows: list[dict], path: Path) -> None:
    path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False) + "\n"
            for row in sorted(rows, key=lambda r: r["id"])
        ),
        encoding="utf-8",
    )


def main() -> int:
    test_path, train_path = FROZEN / "comments_test.jsonl", FROZEN / "comments_train.jsonl"
    before = {path: digest(path) for path in (test_path, train_path)}
    test, train = load(test_path), load(train_path)
    size = len(test)

    print(f"corrections approved {APPROVED}:")
    apply_corrections(test)

    moved = next(row for row in test if row["id"] == MOVED)
    test.remove(moved)
    train.append(moved)
    print(f"\n{MOVED} moved to the train pool (unclear rows do not belong in a test set)")

    replacement = pick_replacement(train, stratum(moved), {thread_of(row) for row in test})
    train.remove(replacement)
    test.append(replacement)
    print(f"replacement: {replacement['id']}")
    print(f"  {' '.join(replacement['text'].split())}")

    assert len(test) == size, f"test set is {len(test)} rows, not {size}"
    assert not any(row["unclear"] for row in test), "an unclear row is in the test set"
    shared = {thread_of(row) for row in test} & {thread_of(row) for row in scorable(train)}
    assert not shared, f"threads on both sides: {sorted(shared)[:3]}"

    write(test, test_path)
    write(train, train_path)
    hidden = sum(
        1 for row in train if row["unclear"] and thread_of(row) in {thread_of(r) for r in test}
    )
    print(f"\ntest {len(test)} rows · train {len(train)} rows · 0 shared threads")
    print(f"{hidden} unclear train rows sit in a test thread — filter `unclear` before training")
    for path in (test_path, train_path):
        print(f"\n{path.relative_to(REPO_ROOT)}\n  v1 {before[path]}\n  v2 {digest(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
