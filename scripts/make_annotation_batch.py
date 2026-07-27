#!/usr/bin/env python3
"""Export the stratified batches the annotator labels (docs/annotation/).

Comments are stratified by (source_id, language, year), posts by (source_id, year)
with posts that carry comments oversampled 2x — they are the ones whose reactions
T1 will be scored against. Seed 42, so a rerun reproduces the same batch.

Rows with empty text are skipped: an album caption that lives only in the image
cannot be labelled from the text, and neither guideline lets the annotator guess.

    python3.11 scripts/make_annotation_batch.py
"""

import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse.annotation import allocate, comment_row, post_row
from market_pulse.langid import detect

RAW = REPO_ROOT / "data" / "raw"
OUT = REPO_ROOT / "data" / "annotation"
SEED = 42
N_COMMENTS = 2000
N_POSTS = 1000
REPLY_OVERSAMPLE = 2


def load(kind: str) -> list[dict]:
    """Every stored record of one kind that has text to label."""
    records = []
    for path in sorted((RAW / kind).glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if record["text"].strip():
                records.append(record)
    return records


def group(records: list[dict], key) -> dict:
    """Stratum key -> records, ordered by msg_id so sampling is reproducible."""
    strata: dict = {}
    for record in records:
        strata.setdefault(key(record), []).append(record)
    for pool in strata.values():
        pool.sort(key=lambda record: record["msg_id"])
    return strata


def draw(strata: dict, quota: dict, rng: random.Random) -> list[dict]:
    picked = []
    for key in sorted(strata, key=str):
        picked += rng.sample(strata[key], quota[key])
    return picked


def print_table(title: str, strata: dict, quota: dict) -> None:
    print(f"\n{title}")
    header = f"{'stratum':<40}{'pool':>8}{'picked':>8}"
    print(header)
    print("-" * len(header))
    for key in sorted(strata, key=str):
        label = " / ".join(str(part) for part in (key if isinstance(key, tuple) else (key,)))
        print(f"{label:<40}{len(strata[key]):>8}{quota[key]:>8}")
    print(f"{'TOTAL':<40}{sum(len(pool) for pool in strata.values()):>8}{sum(quota.values()):>8}")


def build_comments(rng: random.Random) -> list[dict]:
    records = load("comments")
    for record in records:
        record["language"] = detect(record["text"])
    strata = group(records, lambda r: (r["source_id"], r["language"], r["date"][:4]))
    quota = allocate({key: len(pool) for key, pool in strata.items()}, N_COMMENTS)
    print_table("comments — stratified by (source_id, language, year)", strata, quota)
    return [comment_row(r, r["language"]) for r in draw(strata, quota, rng)]


def build_posts(rng: random.Random) -> list[dict]:
    records = load("posts")
    outer_strata = group(records, lambda r: (r["source_id"], r["date"][:4]))
    outer = allocate({key: len(pool) for key, pool in outer_strata.items()}, N_POSTS)

    # Inside each stratum, split the quota between posts that drew comments and the
    # rest, weighted so a commented post is twice as likely to be drawn.
    strata: dict = {}
    quota: dict = {}
    for key, pool in outer_strata.items():
        pools = {bool(flag): [] for flag in (True, False)}
        for record in pool:
            pools[bool(record["reply_count"])].append(record)
        sizes = {flag: len(subset) for flag, subset in pools.items() if subset}
        inner = allocate(sizes, outer[key], weight={True: REPLY_OVERSAMPLE})
        for flag, count in inner.items():
            name = (*key, "with-comments" if flag else "no-comments")
            strata[name] = pools[flag]
            quota[name] = count

    print_table("posts — stratified by (source_id, year), commented posts 2x", strata, quota)
    return [post_row(r, detect(r["text"])) for r in draw(strata, quota, rng)]


def write(rows: list[dict], name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    return path


def main() -> int:
    rng = random.Random(SEED)
    comments = write(build_comments(rng), "comments_batch.jsonl")
    posts = write(build_posts(rng), "posts_batch.jsonl")
    print(f"\nseed {SEED}")
    for path, rows in ((comments, N_COMMENTS), (posts, N_POSTS)):
        count = len(path.read_text(encoding="utf-8").splitlines())
        print(f"{path.relative_to(REPO_ROOT)}: {count} rows (target {rows})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
