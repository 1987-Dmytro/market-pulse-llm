#!/usr/bin/env python3
"""Mine irony candidates from the raw comment corpus for hand-labelling.

G1b wants 150–200 curated sarcastic comments the base model gets wrong, and the
2,000-row batch yielded 81 sarcastic rows in total. This ranks the rest of the
corpus by the heuristics in `market_pulse.sarcasm` and writes the top slice out
in the comment batch's own schema, so the same validator checks it.

Two exclusions keep the frozen split honest: rows already in the batch, and any
comment whose thread is on the test side — the mined pool feeds training, and a
thread-mate of a test comment would leak it.

    python3.11 scripts/mine_sarcasm_candidates.py
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse.annotation import comment_row
from market_pulse.langid import detect
from market_pulse.sarcasm import score

RAW = REPO_ROOT / "data" / "raw" / "comments"
OUT = REPO_ROOT / "data" / "annotation"
FROZEN = REPO_ROOT / "data" / "frozen"
# 600 candidates yielded 140 sarcastic rows; the pool needs 250, so the ranked
# list is mined 200 deeper rather than the labels being read more generously.
N_CANDIDATES = 800


def load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path}: not found")
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def corpus() -> list[dict]:
    records = []
    for path in sorted(RAW.glob("*.jsonl")):
        records += [record for record in load(path) if record["text"].strip()]
    return records


def already_used() -> tuple[set[str], set[tuple]]:
    """Ids in the labelled batch, and the threads the frozen test set owns."""
    ids = {row["id"] for row in load(OUT / "comments_batch.jsonl")}
    threads = {
        (row["channel"], row["parent_msg_id"]) for row in load(FROZEN / "comments_test.jsonl")
    }
    return ids, threads


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=N_CANDIDATES)
    parser.add_argument("--force", action="store_true", help="overwrite a labelled pool")
    args = parser.parse_args(argv)

    path = OUT / "sarcasm_candidates.jsonl"
    if path.exists() and not args.force:
        raise SystemExit(f"{path}: exists — a re-run destroys its labels (--force)")

    records = corpus()
    used_ids, test_threads = already_used()
    print(f"corpus: {len(records)} comments with text")

    scored = []
    seen_text: set[str] = set()
    for record in records:
        if f"{record['channel']}:{record['msg_id']}" in used_ids:
            continue
        if (record["channel"], record["parent_msg_id"]) in test_threads:
            continue
        points, fired = score(record["text"])
        if not points:
            continue
        # Boilerplate repeats dozens of times; one copy is enough to label.
        text = " ".join(record["text"].split()).lower()
        if text in seen_text:
            continue
        seen_text.add(text)
        scored.append((points, record, fired))

    print(f"  {len(used_ids)} already in the batch · {len(test_threads)} test threads excluded")
    print(f"  {len(scored)} distinct comments scored above zero")

    scored.sort(key=lambda item: (-item[0], f"{item[1]['channel']}:{item[1]['msg_id']}"))
    picked = scored[: args.count]
    print(f"\nscore distribution of the {len(picked)} picked (of {len(scored)} scored):")
    for points, count in sorted(Counter(item[0] for item in picked).items(), reverse=True):
        print(f"  score {points:>2}: {count:>4}")
    print("\nsignals firing in the picked slice:")
    for name, count in Counter(name for _, _, fired in picked for name in fired).most_common():
        print(f"  {name:<14}{count:>5}")

    rows = [comment_row(record, detect(record["text"])) for _, record, _ in picked]
    body = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    path.write_text(body, encoding="utf-8")
    path.with_suffix(".pristine.jsonl").write_text(body, encoding="utf-8")
    print(f"\n{path.relative_to(REPO_ROOT)}: {len(rows)} rows to label (+ pristine copy)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
