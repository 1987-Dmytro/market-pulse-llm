"""Scorer — the single judge of every pre-registered number (docs/SPEC.md §5).

Every gate metric in this project is computed here and nowhere else: baselines
(Phase 3), the fine-tune (Phase 4) and the dashboard all call these functions, so
a change here changes every number at once. That is the point.

Rules every implementation honours:

- rows labelled ``unclear`` are excluded from the gates (SPEC §4). The exclusion
  lives in this module, not in the callers: pass ``UNCLEAR`` (or ``None`` where a
  label is a collection) as the *gold* label and the pair is dropped. A model
  that *predicts* ``unclear`` on a scoreable row is simply wrong there.
- macro averages run over the labels the **gold** data supports, never over the
  labels a model happened to predict. Otherwise two models are averaged over
  different denominators and "comparisons paired on identical instances"
  (SPEC §5) quietly stops being true. A supported label the model never predicts
  scores 0.0 and counts; an unsupported label a model invents costs it recall on
  the true class and nothing else.
- pure functions: no model, no dataset, no file is loaded here.
"""

from collections.abc import Hashable, Iterable

UNCLEAR = "unclear"
"""Gold sentinel for a row the annotator could not decide. Excluded from gates."""

SENTIMENT_LABELS = ("positive", "negative", "neutral")
POST_TYPES = ("launch", "promo", "other")
INTENTS = ("taste", "price", "packaging", "quality", "availability")
GATED_LANGUAGES = ("ua", "ru")
"""Languages G1a gates. EN dropped by SPEC amendment 3.1 (n=8 in 2,000 sampled)."""


def _drop_unclear(y_true: list, *predictions: list) -> tuple[list, ...]:
    """Drop every index whose gold label is ``UNCLEAR`` (or ``None``)."""
    for pred in predictions:
        if len(pred) != len(y_true):
            raise ValueError(f"length mismatch: {len(y_true)} gold vs {len(pred)} predicted")
    keep = [i for i, gold in enumerate(y_true) if gold is not None and gold != UNCLEAR]
    return tuple([column[i] for i in keep] for column in (y_true, *predictions))


def _f1(true_positives: int, false_positives: int, false_negatives: int) -> float:
    denominator = 2 * true_positives + false_positives + false_negatives
    return 2 * true_positives / denominator if denominator else 0.0


def _macro_f1(y_true: list[Hashable], y_pred: list[Hashable]) -> float:
    """Macro-F1 averaged over the labels present in ``y_true``."""
    if not y_true:
        raise ValueError("no scoreable rows: every row was unclear or the input was empty")
    labels = sorted(set(y_true), key=str)
    scores = [
        _f1(
            sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label),
            sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label),
            sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label),
        )
        for label in labels
    ]
    return sum(scores) / len(scores)


def sentiment_macro_f1(
    y_true: list[str], y_pred: list[str], languages: list[str]
) -> dict[str, float]:
    """G1a — sentiment macro-F1 per language plus an ``overall`` key.

    ``overall`` covers every scoreable row of the frozen test set, whatever its
    language; the per-language keys report each language present, but only
    :data:`GATED_LANGUAGES` are gated (amendment 3.1 dropped EN).

    Gate: fine-tuned ``overall`` >= best baseline + 5 pp, and no gated language
    below its own baseline by more than 2 pp.
    """
    y_true, y_pred, languages = _drop_unclear(y_true, y_pred, languages)
    scores = {"overall": _macro_f1(y_true, y_pred)}
    for language in sorted(set(languages)):
        rows = [i for i, lang in enumerate(languages) if lang == language]
        scores[language] = _macro_f1([y_true[i] for i in rows], [y_pred[i] for i in rows])
    return scores


def sarcasm_slice_fix_rate(y_true: list[str], base_pred: list[str], tuned_pred: list[str]) -> float:
    """G1b — share of the sarcasm slice that the fine-tune repairs.

    The slice is defined by the base model: exactly the rows of the frozen
    sarcasm holdout it gets wrong (amendment 3.2, which replaced rev. 3's curated
    150-200 examples). Its size is whatever that error set is — the amendment
    records the fallback for fewer than 100 rows, so a small slice is legal and
    only its ``n`` has to be reported next to the verdict. An *empty* slice is
    not: there is nothing to fix and the caller must not silently read 0.0 or 1.0
    into that.

    Gate: >= 0.60 fixed while ``overall`` from :func:`sentiment_macro_f1`
    degrades by no more than 2 pp.
    """
    y_true, base_pred, tuned_pred = _drop_unclear(y_true, base_pred, tuned_pred)
    slice_rows = [i for i, gold in enumerate(y_true) if base_pred[i] != gold]
    if not slice_rows:
        raise ValueError("empty slice: the base model got every scoreable row right")
    return sum(1 for i in slice_rows if tuned_pred[i] == y_true[i]) / len(slice_rows)


def intents_micro_f1(y_true: list[Iterable[str] | None], y_pred: list[Iterable[str]]) -> float:
    """G1c — multi-label micro-F1 over the intents
    (taste / price / packaging / quality / availability).

    Gold ``None`` marks an unclear row. Micro-averaging sums TP/FP/FN over every
    (row, label) pair, so a row with no intents contributes only through the
    labels a model wrongly puts on it.

    Gate: fine-tuned >= baseline + 5 pp.
    """
    y_true, y_pred = _drop_unclear(y_true, y_pred)
    if not y_true:
        raise ValueError("no scoreable rows: every row was unclear or the input was empty")
    gold = [set(row) for row in y_true]
    pred = [set(row) for row in y_pred]
    return _f1(
        sum(len(g & p) for g, p in zip(gold, pred)),
        sum(len(p - g) for g, p in zip(gold, pred)),
        sum(len(g - p) for g, p in zip(gold, pred)),
    )


def launch_detection_macro_f1(y_true: list[str], y_pred: list[str]) -> float:
    """G1d — macro-F1 of post classification (launch / promo / other) on the
    frozen post test set. Every post carries a ``post_type``, relevant or not
    (docs/annotation/posts.md), so this runs on the whole scoreable set.

    Gate: fine-tuned >= zero-shot base LLM + 10 pp.
    """
    return _macro_f1(*_drop_unclear(y_true, y_pred))


def relevance_macro_f1(y_true: list[bool], y_pred: list[bool]) -> float:
    """G1d, second head — macro-F1 of the binary category-relevance decision.

    SPEC §5 words G1d as "relevance + 3-class"; the two heads are reported
    separately, each with its own n, because merging them into one 4-class macro
    average would put an n=1 class (relevant + other) into the denominator and
    let a single row swing the gate. Which of the two the gate reads is an
    operator decision recorded before Phase 4.
    """
    return _macro_f1(*_drop_unclear(y_true, y_pred))


def normalise_brand(entry: dict, aliases: dict[str, str]) -> str:
    """One brand mention -> the token G1e matches on.

    The frozen labels are the authority: a gold entry already carries the
    ``brand_id`` a human matched "on meaning, not on characters"
    (docs/annotation/posts.md), and inflected forms such as ``Яготинська`` or the
    transliterated ``Rud`` are exactly the cases no casefolded lookup would
    reproduce. A prediction carries no ``brand_id``, so it goes through the
    watchlist aliases; anything off the watchlist stands as its own casefolded
    text, which is what keeps non-watchlist brands inside the metric.
    """
    if entry.get("brand_id"):
        return entry["brand_id"]
    mention = " ".join(entry["mention"].split()).casefold()
    return aliases.get(mention, mention)


def brand_extraction_f1(
    y_true: list[list[dict] | None], y_pred: list[list[dict]], aliases: dict[str, str]
) -> float:
    """G1e — brand-mention extraction F1, exact match after normalization.

    Micro-averaged over posts (TP/FP/FN summed, not a mean of per-post scores):
    the gate is about entities found, and a per-post mean would weigh a post with
    one brand like a post with four. Repeats of one brand inside a post collapse,
    per the guideline's "the same brand named twice -> one entry". ``aliases``
    maps a casefolded watchlist ``display_name`` to its ``brand_id``.

    The gold set is never filtered to the watchlist: a dairy brand outside it is
    a real mention the model has to find (SPEC §3 — the watchlist prioritises,
    it never filters).

    Gate: fine-tuned >= zero-shot base LLM + 10 pp.
    """
    y_true, y_pred = _drop_unclear(y_true, y_pred)
    if not y_true:
        raise ValueError("no scoreable rows: every row was unclear or the input was empty")
    gold = [{normalise_brand(e, aliases) for e in row} for row in y_true]
    pred = [{normalise_brand(e, aliases) for e in row} for row in y_pred]
    return _f1(
        sum(len(g & p) for g, p in zip(gold, pred)),
        sum(len(p - g) for g, p in zip(gold, pred)),
        sum(len(g - p) for g, p in zip(gold, pred)),
    )
