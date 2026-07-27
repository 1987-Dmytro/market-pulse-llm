#!/usr/bin/env python3
"""Freeze the held-out test sets and write their dataset card.

Comments are split by thread: every comment of one post lands on one side, so a
test comment's thread-mates can never be trained on. Test rows are stratified by
(language, sentiment) with the sarcasm and packaging-intent cells drawn 2x — the
two slices G1b and G1c are thinnest in. Posts are stratified by post_type with
half of the launch rows in test, because G1d is scored on the class the corpus
has least of. `unclear` rows are excluded from test by the guidelines; they stay
in the train pool carrying their flag, and filtering them restores strict
thread-disjointness (the card records how many that is).

The four files are immutable once committed (CLAUDE.md), so a re-run refuses to
overwrite them without --force.

    python3.11 scripts/freeze_testsets.py
"""

import argparse
import csv
import hashlib
import json
import random
import sys
import textwrap
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse.annotation import grouped_split, stratified_sample

DATA = REPO_ROOT / "data" / "annotation"
FROZEN = REPO_ROOT / "data" / "frozen"
CARD = REPO_ROOT / "docs" / "frozen-testsets.md"
SEED = 42
N_COMMENTS_TEST = 400
N_POSTS_TEST = 250
OVERSAMPLE = 2
REVIEWED = "operator-reviewed"


def load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path}: not found — label the batch first")
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def scorable(rows: list[dict]) -> list[dict]:
    return [row for row in rows if not row["unclear"]]


def thread_of(row: dict) -> tuple:
    return (row["channel"], row["parent_msg_id"])


def is_thin(row: dict) -> bool:
    """The two slices the corpus is thinnest in — oversampled into the test set."""
    return bool(row["sarcasm"]) or "packaging" in row["intents"]


def split_comments(rows: list[dict], rng: random.Random) -> tuple[list, list, dict]:
    test, table = grouped_split(
        scorable(rows),
        group_of=thread_of,
        key=lambda row: (row["language"], row["sentiment"], is_thin(row)),
        total=N_COMMENTS_TEST,
        rng=rng,
        weight_of=lambda name: OVERSAMPLE if name[2] else 1,
    )
    drawn = {row["id"] for row in test}
    return test, [row for row in rows if row["id"] not in drawn], table


def split_posts(rows: list[dict], rng: random.Random) -> tuple[list, list, dict]:
    pool = scorable(rows)
    launch = sorted((row for row in pool if row["post_type"] == "launch"), key=lambda r: r["id"])
    half = rng.sample(launch, len(launch) // 2)  # ~50% launch coverage in test

    rest, table = stratified_sample(
        [row for row in pool if row["post_type"] != "launch"],
        key=lambda row: row["post_type"],
        total=N_POSTS_TEST - len(half),
        rng=rng,
    )
    test = half + rest
    drawn = {row["id"] for row in test}
    table = {"launch": (len(launch), len(half)), **table}
    return test, [row for row in rows if row["id"] not in drawn], table


def leakage(test: list[dict], train: list[dict]) -> tuple[set, int]:
    """Threads on both sides once `unclear` is filtered, and the rows that flag hides."""
    test_threads = {thread_of(row) for row in test}
    shared = test_threads & {thread_of(row) for row in scorable(train)}
    hidden = sum(1 for row in train if row["unclear"] and thread_of(row) in test_threads)
    return shared, hidden


def write(rows: list[dict], name: str, force: bool) -> tuple[Path, str]:
    path = FROZEN / name
    if path.exists() and not force:
        raise SystemExit(f"{path}: already frozen — immutable without operator approval (--force)")
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(
        json.dumps(row, ensure_ascii=False) + "\n" for row in sorted(rows, key=lambda r: r["id"])
    )
    path.write_text(body, encoding="utf-8")
    return path, hashlib.sha256(body.encode("utf-8")).hexdigest()


def reviewed_ids(name: str) -> set[str]:
    """The ids the operator actually looked at — only corrected rows are stamped."""
    path = DATA / name
    if not path.exists():
        return set()
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["id"] for row in csv.DictReader(handle) if row["operator_verdict"].strip()}


def wrap(text: str) -> str:
    """Prose at the width the rest of docs/ is written to; tables pass through."""
    out = []
    for paragraph in text.split("\n\n"):
        if paragraph.startswith("|"):
            out.append(paragraph)
        elif paragraph.startswith("-"):
            out.append(
                "\n".join(
                    textwrap.fill(line, 92, subsequent_indent="  ", break_on_hyphens=False)
                    for line in paragraph.split("\n")
                )
            )
        else:
            out.append(textwrap.fill(paragraph, 92, break_on_hyphens=False))
    return "\n\n".join(out)


def table_md(header: tuple[str, ...], rows: list[tuple]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def comment_rows_md(table: dict) -> str:
    body = [
        (language, sentiment, "yes" if thin else "-", pool, quota, taken)
        for (language, sentiment, thin), (pool, quota, taken) in table.items()
    ]
    body.append(
        (
            "**total**",
            "",
            "",
            sum(pool for pool, _, _ in table.values()),
            sum(quota for _, quota, _ in table.values()),
            sum(taken for _, _, taken in table.values()),
        )
    )
    return table_md(("language", "sentiment", "sarcasm/packaging", "pool", "quota", "taken"), body)


def card(sections: dict) -> str:
    return "\n\n".join(f"## {title}\n\n{wrap(body)}" for title, body in sections.items())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="overwrite an existing freeze")
    args = parser.parse_args(argv)
    rng = random.Random(SEED)

    comments = load(DATA / "comments_batch.jsonl")
    posts = load(DATA / "posts_batch.jsonl")
    c_test, c_train, c_table = split_comments(comments, rng)
    p_test, p_train, p_table = split_posts(posts, rng)

    shared, hidden = leakage(c_test, c_train)
    if shared:
        raise SystemExit(f"LEAK: {len(shared)} thread(s) on both sides, e.g. {sorted(shared)[:3]}")
    print("leakage check: 0 threads shared between the comment test set and the train pool")
    print(f"  {hidden} unclear train rows sit in a test thread — filter `unclear` before training")

    files = []
    for rows, name in (
        (c_test, "comments_test.jsonl"),
        (c_train, "comments_train.jsonl"),
        (p_test, "posts_test.jsonl"),
        (p_train, "posts_train.jsonl"),
    ):
        path, digest = write(rows, name, args.force)
        files.append((path.relative_to(REPO_ROOT), len(rows), digest))
        print(f"{path.relative_to(REPO_ROOT)}: {len(rows)} rows  {digest}")

    language = Counter(row["language"] for row in c_test)
    gated = language["ua"] + language["ru"]
    seen = reviewed_ids("review_comments.csv")
    reviewed = sum(1 for row in c_test if row["id"] in seen)
    corrected = sum(1 for row in c_test if row["annotator"] == REVIEWED)
    intents = Counter(intent for row in c_test for intent in row["intents"])
    relevant = sum(1 for row in p_test if row["relevant"])
    mentions = sum(len(row["brands"]) for row in p_test)
    train_scorable = len(scorable(c_train))

    CARD.write_text(
        "# Frozen test sets (Phase 2, step 2e)\n\n"
        + wrap(
            "**Immutable without operator approval** (CLAUDE.md). Regenerating them invalidates "
            "every number scored against them; `scripts/freeze_testsets.py` refuses to overwrite "
            "an existing freeze without `--force`."
        )
        + "\n\n"
        + card(
            {
                "Files": table_md(
                    ("file", "rows", "sha256"),
                    [(f"`{path}`", rows, f"`{digest}`") for path, rows, digest in files],
                ),
                "Provenance": (
                    f"Built by `scripts/freeze_testsets.py`, seed {SEED}, from "
                    f"`data/annotation/comments_batch.jsonl` ({len(comments)} rows) and "
                    f"`posts_batch.jsonl` ({len(posts)} rows) — the 2d-2 batches after "
                    f"`scripts/apply_review.py` applied the operator's review verdicts. "
                    f"Labels follow `docs/annotation/comments.md` and `posts.md`; the value sets are "
                    f"enforced by `scripts/validate_annotations.py`."
                ),
                "Leakage control": (
                    f"Comments are split by thread (`channel`, `parent_msg_id`): every comment of one "
                    f"post is on one side only. Verified at build time — 0 threads shared between the "
                    f"test set and the scorable train pool.\n\n"
                    f"`unclear` rows are excluded from both test sets (SPEC §5 excludes them from "
                    f"every gate) but remain in the train pool with the flag set: "
                    f"{len(c_train) - train_scorable} of {len(c_train)} comment train rows and "
                    f"{len(p_train) - len(scorable(p_train))} of {len(p_train)} post train rows. "
                    f"{hidden} of those comment rows share a thread with a test row — **filter "
                    f"`unclear` before training** and thread-disjointness is strict."
                ),
                "Comments test set": (
                    f"{len(c_test)} rows of the {len(scorable(comments))} scorable comments; "
                    f"train pool {len(c_train)} rows ({train_scorable} scorable).\n\n"
                    + comment_rows_md(c_table)
                ),
                "Posts test set": (
                    f"{len(p_test)} rows of the {len(scorable(posts))} scorable posts; train pool "
                    f"{len(p_train)} rows. Half the launch rows are in test by design.\n\n"
                    + table_md(
                        ("post_type", "pool", "taken"),
                        [(name, pool, taken) for name, (pool, taken) in p_table.items()],
                    )
                ),
                "Depth of what the gates measure": (
                    "The split is fixed by the operator's design; these are the counts the gates "
                    "will be computed on, recorded before any model exists.\n\n"
                    + table_md(
                        ("gate", "what it needs", "rows in test"),
                        [
                            (
                                "G1a",
                                "per-language sentiment, UA + RU (amendment 3.1)",
                                f"UA {language['ua']}, RU {language['ru']} = {gated} gated; "
                                f"`other` {language['other']}, EN {language['en']} ungated",
                            ),
                            ("G1b", "sarcasm", sum(1 for row in c_test if row["sarcasm"])),
                            ("G1c", "packaging intent", intents["packaging"]),
                            ("G1d", "relevant posts", relevant),
                            ("G1e", "brand mentions", mentions),
                        ],
                    )
                    + f"\n\n- **G1a's 2 pp per-language margin is thinner than it looks**: on RU "
                    f"(n={language['ru']}) 2 pp is under two rows, so a per-language verdict there is "
                    f"one or two comments wide.\n"
                    f"- **`language: other` is {language['other']} test rows** — the langid heuristic's "
                    f"failures, not a fourth language. They are scored in the overall macro-F1 and in "
                    f"no per-language gate.\n"
                    f"- **EN rounds out again**: {sum(1 for r in comments if r['language'] == 'en' and not r['unclear'])} "
                    f"scorable EN comments across the strata gave it {language['en']} test rows. "
                    f"Expected under amendment 3.1, noted so it is not a surprise twice.\n"
                    f"- **Two sarcasm calibrations exist in the labelled data.** {reviewed} of the "
                    f"{len(c_test)} test rows were in the operator's review sample, and the "
                    f"review changed the labels of {corrected} of them (`annotator: {REVIEWED}`); "
                    f"the other {len(c_test) - reviewed} were never reviewed and were labelled "
                    f"before the "
                    f"review showed sarcasm and negativity were under-flagged. The mined pool "
                    f"(`scripts/mine_sarcasm_candidates.py`) is labelled under the corrected "
                    f"calibration, so it feeds training, never this test set."
                ),
            }
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\n{CARD.relative_to(REPO_ROOT)} written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
