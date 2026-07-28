#!/usr/bin/env python3
"""Check the generated sarcasm rows against the real corpus and against themselves.

`scripts/validate_annotations.py` says whether the labels are legal; this says
whether the text is honest. Four hard checks, run after every chunk of 100:

    copied      no row reproduces a real comment, verbatim or near (word-3-gram
                Jaccard >= 0.50 against all six real comment files — the frozen
                test set and the G1b holdout included, because a near-copy there
                would make the gate measure the generator)
    repeated    no two generated rows are near-copies of each other (>= 0.60)
    collapsed   no single opening or closing of two words covers more than 8% of
                the file; pairwise similarity cannot see a frame that repeats
    invented    every capitalised word mid-sentence is a registry brand or a
                registry chain. A capitalised word at the START of a comment is
                invisible to this check, so the report prints every capitalised
                token it saw: the guard is the allowlist plus a reader, not the
                regex alone.

The distributions underneath are the steering wheel, not a gate — they are what
the file is compared against while it is being written (docs/frozen-testsets.md
records the targets, measured from the 230 real sarcastic training rows).

    python3 scripts/check_synthetic.py
"""

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse.registry import load_registry
from market_pulse.synthetic import build_index, closest, frame_counts, tokens

SYNTHETIC = REPO_ROOT / "data" / "annotation" / "synthetic_sarcasm.jsonl"
REAL_FILES = (
    "data/annotation/comments_batch.jsonl",
    "data/annotation/sarcasm_candidates.jsonl",
    "data/annotation/sarcasm_holdout_pool.jsonl",
    "data/frozen/comments_train.jsonl",
    "data/frozen/comments_test.jsonl",
    "data/frozen/sarcasm_holdout.jsonl",
)

COPY = 0.50
REPEAT = 0.60
FRAME_SHARE = 0.08
REPORT_FROM = 0.30  # printed for eyeballing, not a failure

ID_PREFIX = "synthetic:"
PROVENANCE_KEYS = {"source", "generator", "date"}
# Real-world names the rows may carry: the registry's own chains and brands. A
# capitalised word outside this list is either an invented retail chain or a
# brand the watchlist does not know — both are defects the ADR forbids.
EXTRA_NAMES = ("Варус", "Сільпо", "Сильпо", "АТБ", "Varus", "MSUa")
# Slavic inflection moves the ending — `Варуса`, `Яготинська` — so a capitalised
# word is matched on its first four characters. A net for invented names, not a
# normalizer: `market_pulse.brands` is where matching brands is done properly.
STEM = 4
CAPITALISED = re.compile(r"[А-ЯЄІЇҐЁA-Z][\w'’-]{3,}")
SENTENCE_START = set(".!?…\n\r«\"'(-—:;•")


def load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path}: not found")
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def normalised(text: str) -> str:
    return " ".join(tokens(text))


def allowed_names(registry_path: Path) -> set[str]:
    registry = load_registry(registry_path)
    names = [name for brand in registry.watchlist for name in brand.display_names]
    names += [source.name for source in registry.sources]
    names += list(EXTRA_NAMES)
    return {word.casefold()[:STEM] for name in names for word in name.split()}


def capitalised_words(text: str) -> tuple[list[str], list[str]]:
    """Capitalised words of ``text``, split into mid-sentence and sentence-initial."""
    middle, initial = [], []
    for match in CAPITALISED.finditer(text):
        before = text[: match.start()].rstrip()
        opening = not before or before[-1] in SENTENCE_START
        (initial if opening else middle).append(match.group())
    return middle, initial


def check_schema(rows: list[dict]) -> list[str]:
    bad = []
    for row in rows:
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id.startswith(ID_PREFIX):
            bad.append(f"{row_id!r}: id must start with {ID_PREFIX!r}")
        if row.get("source_id") != "synthetic":
            bad.append(f"{row_id}: source_id must be 'synthetic', got {row.get('source_id')!r}")
        if row.get("sarcasm") is not True or row.get("unclear") is not False:
            bad.append(f"{row_id}: every generated row is sarcasm=true, unclear=false")
        provenance = row.get("provenance")
        if not isinstance(provenance, dict) or set(provenance) != PROVENANCE_KEYS:
            bad.append(
                f"{row_id}: provenance needs exactly {sorted(PROVENANCE_KEYS)}: {provenance!r}"
            )
        elif provenance["source"] != "synthetic":
            bad.append(
                f"{row_id}: provenance.source must be 'synthetic', got {provenance['source']!r}"
            )
    duplicated = [
        row_id for row_id, count in Counter(r.get("id") for r in rows).items() if count > 1
    ]
    return bad + [f"{row_id}: duplicate id" for row_id in duplicated]


def check_against_real(rows: list[dict], real: list[dict]) -> tuple[list[str], list[tuple]]:
    real_ids = {row["id"] for row in real}
    real_texts = [row["text"] for row in real]
    by_normalised = {normalised(text): row["id"] for text, row in zip(real_texts, real)}
    index = build_index(real_texts)

    bad, close = [], []
    for row in rows:
        if row["id"] in real_ids:
            bad.append(f"{row['id']}: id collides with a real comment")
        twin = by_normalised.get(normalised(row["text"]))
        if twin:
            bad.append(f"{row['id']}: verbatim copy of {twin}")
            continue
        match, score = closest(row["text"], real_texts, index)
        if score >= REPORT_FROM:
            close.append((score, row["id"], real[match]["id"], real_texts[match]))
        if score >= COPY:
            bad.append(f"{row['id']}: near-copy of {real[match]['id']} (jaccard {score:.2f})")
    return bad, sorted(close, reverse=True)


def check_internal(rows: list[dict]) -> list[str]:
    texts = [row["text"] for row in rows]
    seen: dict[str, str] = {}
    bad = []
    for row in rows:
        key = normalised(row["text"])
        if key in seen:
            bad.append(f"{row['id']}: verbatim duplicate of {seen[key]}")
        seen[key] = row["id"]
    for position, row in enumerate(rows):
        earlier = texts[:position]
        if not earlier:
            continue
        match, score = closest(row["text"], earlier, build_index(earlier))
        if score >= REPEAT:
            bad.append(f"{row['id']}: near-duplicate of {rows[match]['id']} (jaccard {score:.2f})")
    return bad


def check_frames(rows: list[dict]) -> list[str]:
    lead, tail = frame_counts([row["text"] for row in rows])
    cap = max(1, int(len(rows) * FRAME_SHARE))
    bad = []
    for name, counts in (("opening", lead), ("closing", tail)):
        for frame, count in counts.most_common(3):
            if count > cap:
                bad.append(f"{name} {frame!r} covers {count}/{len(rows)} rows (cap {cap})")
    return bad


def check_names(rows: list[dict], allowed: set[str]) -> tuple[list[str], Counter]:
    seen: Counter = Counter()
    bad = []
    for row in rows:
        middle, initial = capitalised_words(row["text"])
        seen.update(middle + initial)
        unknown = sorted({word for word in middle if word.casefold()[:STEM] not in allowed})
        if unknown:
            bad.append(f"{row['id']}: capitalised word(s) outside the registry: {unknown}")
    return bad, seen


def report(rows: list[dict], close: list[tuple], names: Counter) -> None:
    lengths = [len(row["text"].split()) for row in rows]
    intents = Counter(intent for row in rows for intent in row["intents"])
    print(f"\nrows: {len(rows)}")
    print(f"language:  {dict(Counter(row['language'] for row in rows).most_common())}")
    print(f"sentiment: {dict(Counter(row['sentiment'] for row in rows).most_common())}")
    print(f"intents:   {dict(intents.most_common())}")
    print(f"           no intent: {sum(1 for row in rows if not row['intents'])}")
    emoji = sum(1 for row in rows if any(ord(char) > 0x2500 for char in row["text"]))
    parens = sum(1 for row in rows if "))" in row["text"])
    print(f"markers:   emoji {emoji} · '))' {parens}")
    print(
        f"words:     min {min(lengths)} · p25 {sorted(lengths)[len(lengths) // 4]}"
        f" · median {statistics.median(lengths):.0f}"
        f" · p75 {sorted(lengths)[3 * len(lengths) // 4]} · max {max(lengths)}"
    )
    lead, tail = frame_counts([row["text"] for row in rows])
    print(f"frames:    top opening {lead.most_common(2)} · top closing {tail.most_common(2)}")
    print(f"names:     {dict(names.most_common(12))}")
    if close:
        print(f"\nnearest real comments (>= {REPORT_FROM}), for eyeballing:")
        for score, row_id, real_id, text in close[:10]:
            print(f"  {score:.2f}  {row_id} ~ {real_id}: {' '.join(text.split())[:90]}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, nargs="?", default=SYNTHETIC)
    parser.add_argument("--registry", type=Path, default=REPO_ROOT / "config" / "registry.yaml")
    args = parser.parse_args(argv)

    rows = load(args.file)
    if not rows:
        raise SystemExit(f"{args.file}: no rows")
    real = [row for name in REAL_FILES for row in load(REPO_ROOT / name)]
    print(f"{args.file}: {len(rows)} generated rows against {len(real)} real comments")

    copied, close = check_against_real(rows, real)
    invented, names = check_names(rows, allowed_names(args.registry))
    failures = {
        "schema": check_schema(rows),
        "copied": copied,
        "repeated": check_internal(rows),
        "collapsed": check_frames(rows),
        "invented": invented,
    }
    report(rows, close, names)

    total = sum(len(problems) for problems in failures.values())
    if not total:
        print("\nVALID: nothing copied, nothing repeated, no collapsed frame")
        return 0
    print(f"\n{total} violation(s):")
    for name, problems in failures.items():
        for line in problems[:15]:
            print(f"  [{name}] {line}")
        if len(problems) > 15:
            print(f"  [{name}] ... and {len(problems) - 15} more")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
