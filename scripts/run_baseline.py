#!/usr/bin/env python3
"""Baseline (a) for Phase 3: TF-IDF + logistic regression, scored by the scorer.

This is the cheapest realistic baseline SPEC §5 requires every comparison table
to carry. It is deliberately untuned — one pre-registered config, seed 42, no
search. A head that collapses to the majority class is the honest number for a
bag-of-character-ngrams model on 1,446 rows, not a bug to iterate away.

Every number leaves this script through `market_pulse.scorer` and lands in
`results/baselines.json`; nothing here computes a metric of its own.

    pip install -e '.[baseline]'
    python3.11 scripts/run_baseline.py --model tfidf-logreg
"""

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse import provenance, scorer  # noqa: E402
from market_pulse.brands import find_watchlist_brands, watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

FROZEN = REPO_ROOT / "data" / "frozen"
ANNOTATION = REPO_ROOT / "data" / "annotation"
RESULTS = REPO_ROOT / "results" / "baselines.json"
SEED = 42

VECTORIZER = {
    # Character n-grams, not words: UA/RU comments are morphologically rich and
    # unstemmed, so `молока`/`молоко`/`молоком` share nothing at word level.
    "analyzer": "char_wb",
    "ngram_range": (3, 5),
    "min_df": 2,
    "sublinear_tf": True,
}
CLASSIFIER = {
    # `balanced` pairs with macro-averaged gates: without it the rare classes
    # (packaging n=19, relevant n=26) are free to disappear. Chosen before the
    # run, not after seeing which setting scored better.
    "max_iter": 1000,
    "class_weight": "balanced",
    "random_state": SEED,
}


def load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path}: not found")
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def scoreable(rows: list[dict]) -> list[dict]:
    return [row for row in rows if not row["unclear"]]


def normalised(text: str) -> str:
    return " ".join(text.split()).lower()


def gold(rows: list[dict], field: str, unclear=scorer.UNCLEAR):
    """Gold labels with the unclear sentinel — the scorer drops those rows."""
    return [unclear if row["unclear"] else row[field] for row in rows]


def fit_predict(train_rows: list[dict], test_sets: list[list[dict]], labels: list) -> list[list]:
    """One TF-IDF + logreg head: fit on the train rows, predict each test set."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression

    vectorizer = TfidfVectorizer(**VECTORIZER)
    x_train = vectorizer.fit_transform([row["text"] for row in train_rows])
    model = LogisticRegression(**CLASSIFIER).fit(x_train, labels)
    return [
        list(model.predict(vectorizer.transform([row["text"] for row in rows]))) if rows else []
        for rows in test_sets
    ]


def git_state() -> dict:
    """`market_pulse.provenance.git_state`, sorted, ignoring the results file it appends to."""
    return provenance.git_state(RESULTS, sort=True)


def append(record: dict) -> None:
    """Append-only: a model's runs accumulate, none is ever overwritten."""
    RESULTS.parent.mkdir(exist_ok=True)
    history = json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.exists() else {}
    history.setdefault(record["model"], []).append(record)
    RESULTS.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["tfidf-logreg"], required=True)
    args = parser.parse_args(argv)

    comments_train = load(FROZEN / "comments_train.jsonl")
    mined = load(ANNOTATION / "sarcasm_candidates.jsonl")
    posts_train = load(FROZEN / "posts_train.jsonl")
    comments_test = load(FROZEN / "comments_test.jsonl")
    posts_test = load(FROZEN / "posts_test.jsonl")
    holdout = load(FROZEN / "sarcasm_holdout.jsonl")

    t1_train = scoreable(comments_train) + scoreable(mined)
    t2_train = scoreable(posts_train)

    # The freeze moved these rows out of training; if one ever comes back, every
    # holdout number becomes a memorisation score. `sarcasm_holdout_pool.jsonl`
    # is not a training source either — its non-sarcastic rows share holdout
    # threads (docs/frozen-testsets.md).
    train_texts = {normalised(row["text"]) for row in t1_train}
    leaked = [row["id"] for row in holdout if normalised(row["text"]) in train_texts]
    assert not leaked, f"holdout text present in the training pool: {leaked[:3]}"

    print(f"T1 train: {len(t1_train)} scoreable rows")
    print(f"  comments_train        {len(scoreable(comments_train)):>5} of {len(comments_train)}")
    print(f"  sarcasm_candidates    {len(scoreable(mined)):>5} of {len(mined)} (sarcasm-enriched)")
    print(f"T2 train: {len(t2_train)} of {len(posts_train)} scoreable posts")
    print(f"test: comments {len(comments_test)} · holdout {len(holdout)} · posts {len(posts_test)}")

    print("\nfitting T1 heads (sentiment · sarcasm · 5 intents)…")
    sentiment_pred, holdout_sentiment = fit_predict(
        t1_train, [comments_test, holdout], [row["sentiment"] for row in t1_train]
    )
    sarcasm_pred, holdout_sarcasm = fit_predict(
        t1_train, [comments_test, holdout], [row["sarcasm"] for row in t1_train]
    )
    intent_pred: list[set[str]] = [set() for _ in comments_test]
    for intent in scorer.INTENTS:
        (flags,) = fit_predict(
            t1_train, [comments_test], [intent in row["intents"] for row in t1_train]
        )
        for row, flag in zip(intent_pred, flags):
            if flag:
                row.add(intent)

    print("fitting T2 heads (relevance · post_type)…")
    (relevance_pred,) = fit_predict(t2_train, [posts_test], [row["relevant"] for row in t2_train])
    (post_type_pred,) = fit_predict(t2_train, [posts_test], [row["post_type"] for row in t2_train])
    aliases = watchlist_aliases(load_registry(REPO_ROOT / "config" / "registry.yaml").watchlist)
    brand_pred = [find_watchlist_brands(row["text"], aliases) for row in posts_test]

    languages = [row["language"] for row in comments_test]
    sentiment = scorer.sentiment_macro_f1(
        gold(comments_test, "sentiment"), sentiment_pred, languages
    )
    holdout_langs = [row["language"] for row in holdout]
    holdout_sentiment_f1 = scorer.sentiment_macro_f1(
        gold(holdout, "sentiment"), holdout_sentiment, holdout_langs
    )
    base_errors = [
        row["id"]
        for row, pred in zip(holdout, holdout_sentiment)
        if not row["unclear"] and row["sentiment"] != pred
    ]
    gates = [
        {
            "gate": "G1a",
            "metric": "sentiment macro-F1 (comments_test)",
            "values": sentiment,
            "n": {"overall": len(comments_test), **Counter(languages)},
            "gated_languages": list(scorer.GATED_LANGUAGES),
        },
        {
            "gate": "G1b",
            "metric": "sarcasm slice fix-rate (sarcasm_holdout)",
            "value": None,
            "n": {"holdout": len(holdout)},
            "note": (
                "not computable at 3a: amendment 3.2 defines the slice by the zero-shot base"
                " LLM's errors and the fix-rate needs a fine-tune. Both land in 3b/4."
            ),
        },
        {
            "gate": "G1c",
            "metric": "intents micro-F1 (comments_test)",
            "value": scorer.intents_micro_f1(
                gold(comments_test, "intents", unclear=None), intent_pred
            ),
            "n": {"overall": len(comments_test)},
        },
        {
            "gate": "G1d",
            "metric": "post_type macro-F1 (posts_test)",
            "value": scorer.launch_detection_macro_f1(
                gold(posts_test, "post_type"), post_type_pred
            ),
            "n": {"overall": len(posts_test), **Counter(row["post_type"] for row in posts_test)},
        },
        {
            "gate": "G1d",
            "metric": "relevance macro-F1 (posts_test)",
            "value": scorer.relevance_macro_f1(gold(posts_test, "relevant"), relevance_pred),
            "n": {
                "overall": len(posts_test),
                "relevant": sum(1 for row in posts_test if row["relevant"]),
            },
            "note": "second head of G1d; SPEC §5 says 'relevance + 3-class', reported separately",
        },
        {
            "gate": "G1e",
            "metric": "brand extraction F1 (posts_test)",
            "value": scorer.brand_extraction_f1(
                gold(posts_test, "brands", unclear=None), brand_pred, aliases
            ),
            "n": {
                "overall": len(posts_test),
                "posts_with_brands": sum(1 for row in posts_test if row["brands"]),
                "gold_entities": sum(
                    len({scorer.normalise_brand(b, aliases) for b in row["brands"]})
                    for row in posts_test
                ),
            },
        },
    ]
    diagnostics = {
        "sarcasm_binary_macro_f1_comments_test": scorer.macro_f1(
            gold(comments_test, "sarcasm"), sarcasm_pred
        ),
        "holdout_sentiment_macro_f1": holdout_sentiment_f1,
        "holdout_sentiment_errors": len(base_errors),
        "holdout_sarcasm_detected": sum(1 for flag in holdout_sarcasm if flag),
        "note": (
            "diagnostics, not gates. The holdout error count is this baseline's error set,"
            " NOT the G1b slice — amendment 3.2 defines that one by the zero-shot base LLM."
            " Read the holdout scores against its base rate: 107 of 108 rows are negative, so"
            " a model trained on a sarcasm-enriched pool scores well there by leaning negative,"
            " not by reading irony — which is what holdout_sarcasm_detected (of 108) shows."
        ),
    }

    record = {
        "model": args.model,
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "git": git_state(),
        "config": {
            "seed": SEED,
            "vectorizer": {**VECTORIZER, "ngram_range": list(VECTORIZER["ngram_range"])},
            "classifier": CLASSIFIER,
            "heads": {
                "T1": "sentiment 3-class · sarcasm binary · intents 5x binary",
                "T2": "relevance binary · post_type 3-class · brands = watchlist string match",
            },
            "brand_match": "watchlist display_names, casefolded, word-bounded; watchlist-only",
            "train_sources": {
                "data/frozen/comments_train.jsonl": len(scoreable(comments_train)),
                "data/annotation/sarcasm_candidates.jsonl": len(scoreable(mined)),
                "data/frozen/posts_train.jsonl": len(t2_train),
            },
            "train_note": (
                "sarcasm_candidates is sarcasm-enriched (378 of 540 scoreable rows negative),"
                " so the T1 sentiment prior is shifted against the test set's 212/400"
            ),
        },
        "gates": gates,
        "diagnostics": diagnostics,
    }
    append(record)
    print(f"\nwrote {RESULTS.relative_to(REPO_ROOT)} — read it with scripts/show_results.py")
    code = [p for p in record["git"]["dirty"] if p.startswith(("src/", "scripts/", "config/"))]
    if code:
        print(
            f"WARNING: uncommitted code — {record['git']['commit'][:9]} does not reproduce: {code}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
