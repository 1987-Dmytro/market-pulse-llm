"""Scorer — the single judge of every pre-registered number (docs/SPEC.md §4).

Phase 1 ships signatures only. The implementations land in Phase 3, where the
baselines (TF-IDF+logreg, fine-tuned XLM-R, zero-shot base LLM) are scored by
this very module; the same code is then reused unchanged for the one-shot
Tier-1 evaluation in Phase 4. One scorer, one set of numbers.

Rules every implementation here must honour:
- items labelled ``unclear`` are excluded from the gates (SPEC §3);
- comparisons are paired on identical instances (SPEC §4);
- callers pass explicit labels — this module never loads a model or a dataset.
"""


def sentiment_macro_f1(
    y_true: list[str], y_pred: list[str], languages: list[str]
) -> dict[str, float]:
    """G1a — sentiment macro-F1 per language (RU/UA/EN) plus an ``overall`` key.

    Gate: fine-tuned ``overall`` >= best baseline + 5 pp, and no single language
    below its own baseline by more than 2 pp.
    """
    raise NotImplementedError("Phase 3: scorer implementation")


def sarcasm_slice_fix_rate(y_true: list[str], base_pred: list[str], tuned_pred: list[str]) -> float:
    """G1b — share of the curated sarcasm slice that the fine-tune repairs.

    The slice holds 150-200 examples the base model gets wrong, so the rate is
    computed over exactly those. Gate: >= 0.60 fixed while the overall macro-F1
    from :func:`sentiment_macro_f1` degrades by no more than 2 pp.
    """
    raise NotImplementedError("Phase 3: scorer implementation")


def intents_micro_f1(y_true: list[set[str]], y_pred: list[set[str]]) -> float:
    """G1c — multi-label micro-F1 over the intents
    (taste / price / packaging / quality / availability).

    Gate: fine-tuned >= baseline + 5 pp.
    """
    raise NotImplementedError("Phase 3: scorer implementation")


def launch_detection_macro_f1(y_true: list[str], y_pred: list[str]) -> float:
    """G1d — macro-F1 of post classification (launch / promo / other) on the
    frozen post test set.

    Gate: fine-tuned >= zero-shot base LLM + 10 pp.
    """
    raise NotImplementedError("Phase 3: scorer implementation")
