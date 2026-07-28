"""Guards for generated training rows — copied text and collapsed templates.

`data/annotation/synthetic_sarcasm.jsonl` is written by an LLM session anchored on
real comments, so it fails in two ways that reading a sample will not show: rows
that reproduce the anchors, and two hundred rows built on one frame. Both are
cheap to measure, so they are measured after every chunk of 100 rather than at the
end, when a collapse costs the whole batch.

Similarity is word-3-gram Jaccard: it ignores emoji and punctuation, which is
where a paraphrase differs least, and an inverted index keeps 600 x 12,000
comparisons to the pairs that share at least one shingle.
"""

import re
from collections import Counter

SHINGLE = 3
WORD = re.compile(r"\w+")


def tokens(text: str) -> list[str]:
    return WORD.findall(text.casefold())


def shingles(text: str, n: int = SHINGLE) -> set[str]:
    """Word n-grams of ``text``; a text shorter than ``n`` words is one shingle."""
    words = tokens(text)
    if not words:
        return set()
    if len(words) < n:
        return {" ".join(words)}
    return {" ".join(words[i : i + n]) for i in range(len(words) - n + 1)}


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def build_index(texts: list[str], n: int = SHINGLE) -> dict[str, set[int]]:
    """shingle -> the rows holding it, so a query only meets plausible matches."""
    index: dict[str, set[int]] = {}
    for row, text in enumerate(texts):
        for shingle in shingles(text, n):
            index.setdefault(shingle, set()).add(row)
    return index


def closest(
    text: str, texts: list[str], index: dict[str, set[int]], n: int = SHINGLE
) -> tuple[int, float]:
    """The most similar row of ``texts`` and its score; ``(-1, 0.0)`` if none shares a shingle."""
    query = shingles(text, n)
    candidates: set[int] = set()
    for shingle in query:
        candidates |= index.get(shingle, set())
    best, score = -1, 0.0
    for row in sorted(candidates):
        similarity = jaccard(query, shingles(texts[row], n))
        if similarity > score:
            best, score = row, similarity
    return best, score


def frame_counts(texts: list[str], edge: int = 2) -> tuple[Counter, Counter]:
    """How often each opening and each closing of ``edge`` words repeats.

    Pairwise similarity does not see this: two hundred rows that all open "Ага," and
    close ")))" are pairwise distinct and still read as one machine. Counted over
    words, so emoji and punctuation cannot disguise a repeated frame.
    """
    lead: Counter = Counter()
    tail: Counter = Counter()
    for text in texts:
        words = tokens(text)
        if not words:
            continue
        lead[" ".join(words[:edge])] += 1
        tail[" ".join(words[-edge:])] += 1
    return lead, tail
