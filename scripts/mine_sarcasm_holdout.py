#!/usr/bin/env python3
"""Mine the second wave of irony candidates — the pool the G1b holdout is cut from.

Wave 1 (`mine_sarcasm_candidates.py`) fed training and only had to stay clear of
the test threads. This wave feeds evaluation, so it has to stay clear of
everything the model will ever be trained on: rows already labelled anywhere, and
any comment whose thread carries a test row or a scoreable train row. A
thread-mate on the training side leaks the post's context into the G1b score.

Two smaller exclusions do the same job at text level: a comment whose text is
already labelled elsewhere would put a verbatim training string into the holdout,
and repeated boilerplate is labelled once.

The funnel is printed step by step because the interesting number is how little
survives it — the corpus is finite and wave 1 has already been through it.

    python3.11 scripts/mine_sarcasm_holdout.py
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
N_CANDIDATES = 1200


def load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path}: not found")
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def thread_of(row: dict) -> tuple:
    return (row["channel"], row["parent_msg_id"])


def normalised(text: str) -> str:
    return " ".join(text.split()).lower()


def labelled() -> tuple[set[str], set[str], set[tuple]]:
    """Ids and texts already labelled anywhere, and the threads training owns."""
    batch = load(OUT / "comments_batch.jsonl")
    mined = load(OUT / "sarcasm_candidates.jsonl")
    test = load(FROZEN / "comments_test.jsonl")
    train = load(FROZEN / "comments_train.jsonl")

    ids = {row["id"] for row in batch} | {row["id"] for row in mined}
    texts = {normalised(row["text"]) for row in batch + mined}
    threads = {thread_of(row) for row in test}
    threads |= {thread_of(row) for row in train if not row["unclear"]}
    return ids, texts, threads


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=N_CANDIDATES)
    parser.add_argument("--force", action="store_true", help="overwrite a labelled pool")
    args = parser.parse_args(argv)

    path = OUT / "sarcasm_holdout_pool.jsonl"
    if path.exists() and not args.force:
        raise SystemExit(f"{path}: exists — a re-run destroys its labels (--force)")

    records = [
        record
        for source in sorted(RAW.glob("*.jsonl"))
        for record in load(source)
        if record["text"].strip()
    ]
    used_ids, used_texts, used_threads = labelled()
    print(f"corpus: {len(records)} comments with text")

    fresh = [
        record for record in records if f"{record['channel']}:{record['msg_id']}" not in used_ids
    ]
    print(f"  - {len(records) - len(fresh):>5} already labelled (batch or wave 1) -> {len(fresh)}")

    free = [record for record in fresh if thread_of(record) not in used_threads]
    print(f"  - {len(fresh) - len(free):>5} in a test or scoreable-train thread -> {len(free)}")

    scored, seen = [], set()
    duplicate_of_labelled = repeat = 0
    for record in free:
        text = normalised(record["text"])
        if text in used_texts:
            duplicate_of_labelled += 1
            continue
        if text in seen:
            repeat += 1
            continue
        seen.add(text)
        points, fired = score(record["text"])
        scored.append((points, record, fired))
    print(f"  - {duplicate_of_labelled:>5} verbatim copies of an already-labelled text")
    print(f"  - {repeat:>5} repeats of another candidate -> {len(scored)} candidates")

    scored.sort(key=lambda item: (-item[0], f"{item[1]['channel']}:{item[1]['msg_id']}"))
    picked = scored[: args.count]
    if len(picked) < args.count:
        print(f"\nasked for {args.count}, the corpus holds {len(picked)} — the pool is exhausted")

    print(f"\nscore distribution of the {len(picked)} picked:")
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
