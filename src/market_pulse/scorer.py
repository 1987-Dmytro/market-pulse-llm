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

import math
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


def macro_f1(y_true: list[Hashable], y_pred: list[Hashable]) -> float:
    """Macro-F1 averaged over the labels present in ``y_true``, unclear rows dropped.

    Public because the gates are not the only numbers that must come from this
    module: a diagnostic reported next to them (the sarcasm head on the comment
    test set, say) has to be computed by the same code, or the results file
    quietly mixes two arithmetics.
    """
    y_true, y_pred = _drop_unclear(y_true, y_pred)
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
    scores = {"overall": macro_f1(y_true, y_pred)}
    for language in sorted(set(languages)):
        rows = [i for i, lang in enumerate(languages) if lang == language]
        scores[language] = macro_f1([y_true[i] for i in rows], [y_pred[i] for i in rows])
    return scores


def sarcasm_slice_fix_rate(
    slice_ids: Iterable[str], gold: dict[str, dict], predicted: dict[str, dict]
) -> dict:
    """G1b — how much of the persisted sarcasm slice the fine-tune repairs.

    The slice is **given, not recomputed** (SPEC amendment 3.5 (3)): it is the
    id list in ``results/g1b_slice.json``, measured once by the own-pod base
    run, and the caller verifies that file's SHA256 against the anchor record
    before it gets here. Recomputing it from a label column — which is what this
    function did until the amendment — would let the slice drift with whatever
    predictions the caller happened to pass, and the base model's error set is
    pre-registered, not re-derivable at gate time.

    A row is **FIXED** iff the fine-tuned model is right on *both* labels of that
    row: the slice is the union of the base model's sentiment and sarcasm errors,
    so a row leaves the union only when neither error is left. Fix-rate is
    ``fixed / len(slice_ids)`` — the pre-registered denominator, which is why a
    slice row this caller cannot answer for raises instead of scoring 0:

    - an id missing from ``predicted`` means the run did not score the whole
      slice, and an incomplete run must not read as a failed gate;
    - an id whose gold is unclear cannot be in a slice built from scoreable rows,
      so it is an input defect; dropping it would silently shrink the
      pre-registered denominator (the one place this module does not apply its
      own ``unclear`` rule, and it is deliberate).

    ``gold`` and ``predicted`` map an id to ``{"sentiment": str, "sarcasm":
    bool}``. Returns ``fixed`` / ``n`` / ``rate``: the gate is a count against
    :func:`gate_thresholds`, and n travels with it (amendment 3.2's fallback
    says the smaller n is reported beside the verdict).

    Gate: ``fixed`` >= 60% of n, while ``overall`` from
    :func:`sentiment_macro_f1` degrades by no more than 2 pp.
    """
    ids = list(slice_ids)
    if not ids:
        raise ValueError("empty slice: G1b has nothing to measure and no default to fall back on")
    if len(set(ids)) != len(ids):
        raise ValueError("the slice repeats an id — its length is the gate's denominator")
    fixed = 0
    for row_id in ids:
        for name, table in (("gold", gold), ("prediction", predicted)):
            if row_id not in table:
                raise ValueError(f"{row_id} is in the slice but has no {name}")
        truth = gold[row_id]
        if truth["sentiment"] == UNCLEAR or truth["sarcasm"] is None:
            raise ValueError(f"{row_id} is unclear, so it cannot be a slice row: check the inputs")
        answer = predicted[row_id]
        if answer["sentiment"] == truth["sentiment"] and answer["sarcasm"] == truth["sarcasm"]:
            fixed += 1
    return {"fixed": fixed, "n": len(ids), "rate": fixed / len(ids)}


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

    **This is the number G1d gates** (amendment 3.3): rev. 3 worded the gate as
    "relevance + 3-class", and the operator resolved it to the 3-class head
    alone. :func:`relevance_macro_f1` is reported beside it, never inside it.

    Gate: fine-tuned >= zero-shot base LLM + 10 pp.
    """
    return macro_f1(y_true, y_pred)


def relevance_macro_f1(y_true: list[bool], y_pred: list[bool]) -> float:
    """Binary category relevance — reported next to G1d, **not gated**.

    The two heads were always two metrics: merging them into one 4-class macro
    average would put an n=1 class (relevant + other) into the denominator and
    let a single row swing the gate. Amendment 3.3 settled which one G1d reads —
    :func:`launch_detection_macro_f1`, the 3-class post type — because relevance
    sits near its ceiling and a +10 pp demand on a blend would be met by the head
    with the least room to give. This number is still published with its own n:
    T2a relevance is on the pipeline's critical path (SPEC §9).
    """
    return macro_f1(y_true, y_pred)


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


# --- the bars ---------------------------------------------------------------
#
# Every Tier-1 gate is stated as a margin over a baseline, so a bar is one
# margin plus one measured anchor. The margins are gate *definitions* and belong
# in code; the anchors are *measurements* and are read out of the own-pod record
# by the caller (amendment 3.5 (1) — "never hand-typed"), because a threshold
# nobody can re-derive from a result file is a threshold nobody can audit.
G1A_MARGIN = 0.05
G1A_LANGUAGE_DROP = 0.02
G1B_FIX_SHARE = 0.60
G1B_MACRO_F1_DROP = 0.02
G1C_MARGIN = 0.05
NO_REGRESSION_DROP = 0.01
"""G1d and G1e: amendment 3.5 (2) replaced "+10 pp" with `anchor - 1 pp`."""


def gate_thresholds(anchors: dict, slice_n: int) -> dict:
    """The pre-registered bars, derived from one anchor row and the margins.

    ``anchors`` is ``{"G1a": {"overall": f, "<lang>": f, ...}, "G1c": f,
    "G1d": f, "G1e": f}`` — the gated values of the zero-shot anchor. Only
    :data:`GATED_LANGUAGES` get floors; a language the record carries but the
    spec does not gate (``other``, amendment 3.1) must not grow one here.

    A bar above 1.0 raises. All five metrics are bounded by 1.0, so "anchor +
    margin" can state a threshold no model can reach — that is arithmetic about
    the gate, not a prediction about the model, and it is exactly what happened
    to G1d and G1e before amendment 3.5 (2). The check is cheap and it fires the
    day an anchor lands, which is the only moment at which a mis-specified gate
    can still be renegotiated honestly.
    """
    if slice_n < 1:
        raise ValueError("the G1b slice is empty: its size is the gate's denominator")
    bars = {
        "G1a": {
            "min": anchors["G1a"]["overall"] + G1A_MARGIN,
            "floors": {
                language: anchors["G1a"][language] - G1A_LANGUAGE_DROP
                for language in GATED_LANGUAGES
            },
        },
        "G1b": {
            # 0.60 * 45 is 27.000000000000004 in binary floating point, and an
            # unrounded ceiling would demand 28 of 45. Round, then ceil.
            "min_fixed": math.ceil(round(G1B_FIX_SHARE * slice_n, 6)),
            "n": slice_n,
            "max_macro_f1_drop": G1B_MACRO_F1_DROP,
        },
        "G1c": {"min": anchors["G1c"] + G1C_MARGIN},
        "G1d": {"min": anchors["G1d"] - NO_REGRESSION_DROP},
        "G1e": {"min": anchors["G1e"] - NO_REGRESSION_DROP},
    }
    unreachable = {
        gate: sorted(
            bar for bar in [block.get("min"), *block.get("floors", {}).values()] if bar > 1
        )
        for gate, block in bars.items()
        if "min" in block
    }
    named = {gate: bars for gate, bars in unreachable.items() if bars}
    if named:
        raise ValueError(
            f"a bar above the 1.0 ceiling of a bounded metric: {named} — the gate is"
            " mis-specified, not failed; report it to the operator (docs/SPEC.md §5 is"
            " a team-lead file and thresholds are immutable without approval)"
        )
    return bars
