"""The scorer is the single judge of every project number, so every expected
value below is computed by hand on a fixture small enough to check on paper.

A metric asserted against its own implementation proves nothing; a metric
asserted against an arithmetic anyone can redo catches the day the implementation
drifts. The final test replaces the Phase-1 mechanism (which enumerated the
module and demanded ``NotImplementedError``) with the same reflective idea one
phase on: a public function without a hand-computed test is a number nobody has
checked.
"""

import inspect

import pytest
from market_pulse import scorer

PUBLIC = [
    name
    for name, fn in vars(scorer).items()
    if inspect.isfunction(fn) and fn.__module__ == scorer.__name__ and not name.startswith("_")
]


# --- the shared average -----------------------------------------------------
#
#   gold [a, a, b, c] vs pred [a, b, b, c]
#   a: tp 1, fp 0, fn 1 -> 2/3 · b: tp 1, fp 1, fn 0 -> 2/3 · c: tp 1, fp 0, fn 0 -> 1.0
#   macro = (2/3 + 2/3 + 1) / 3 = 7/9
def test_macro_f1_matches_the_hand_computed_fixture():
    assert scorer.macro_f1(["a", "a", "b", "c"], ["a", "b", "b", "c"]) == pytest.approx(7 / 9)


def test_macro_f1_excludes_unclear_rows():
    assert scorer.macro_f1(
        ["a", "a", "b", "c", scorer.UNCLEAR], ["a", "b", "b", "c", "a"]
    ) == pytest.approx(7 / 9)


# --- G1a: sentiment ---------------------------------------------------------
#
#   idx  gold      pred      lang
#    0   positive  positive  ua
#    1   positive  negative  ua
#    2   negative  negative  ua
#    3   negative  negative  ru
#    4   neutral   neutral   ru
#    5   neutral   positive  ru
#
# overall  positive: tp 1, fp 1 (idx5), fn 1 (idx1) -> 2/(2+1+1)     = 0.5
#          negative: tp 2, fp 1 (idx1), fn 0        -> 4/(4+1+0)     = 0.8
#          neutral:  tp 1, fp 0,        fn 1 (idx5) -> 2/(2+0+1)     = 2/3
#          macro = (0.5 + 0.8 + 2/3) / 3                             = 0.6555...
# ua       positive: tp 1, fp 0, fn 1 -> 2/3 · negative: tp 1, fp 1, fn 0 -> 2/3
#          macro (two gold labels)                                   = 2/3
# ru       negative: tp 1, fp 0, fn 0 -> 1.0 · neutral: tp 1, fp 0, fn 1 -> 2/3
#          macro                                                     = 5/6
SENTIMENT_GOLD = ["positive", "positive", "negative", "negative", "neutral", "neutral"]
SENTIMENT_PRED = ["positive", "negative", "negative", "negative", "neutral", "positive"]
SENTIMENT_LANG = ["ua", "ua", "ua", "ru", "ru", "ru"]


def test_sentiment_macro_f1_matches_the_hand_computed_fixture():
    scores = scorer.sentiment_macro_f1(SENTIMENT_GOLD, SENTIMENT_PRED, SENTIMENT_LANG)
    assert scores == pytest.approx({"overall": (0.5 + 0.8 + 2 / 3) / 3, "ua": 2 / 3, "ru": 5 / 6})


def test_sentiment_macro_f1_excludes_unclear_rows():
    """An unclear row must change nothing — not the score, not the denominator."""
    gold = [*SENTIMENT_GOLD, scorer.UNCLEAR]
    scores = scorer.sentiment_macro_f1(gold, [*SENTIMENT_PRED, "positive"], [*SENTIMENT_LANG, "ua"])
    assert scores == pytest.approx(
        scorer.sentiment_macro_f1(SENTIMENT_GOLD, SENTIMENT_PRED, SENTIMENT_LANG)
    )


def test_sentiment_macro_f1_scores_a_class_the_model_never_predicts_as_zero():
    # gold [pos, pos, neg] vs pred [pos, pos, pos]
    #   positive: tp 2, fp 1, fn 0 -> 4/5 · negative: tp 0, fp 0, fn 1 -> 0.0
    scores = scorer.sentiment_macro_f1(
        ["positive", "positive", "negative"], ["positive"] * 3, ["ua"] * 3
    )
    assert scores["overall"] == pytest.approx((0.8 + 0.0) / 2)


def test_sentiment_macro_f1_averages_over_gold_labels_only():
    """A label the model invents must not enter the denominator.

    gold [pos, pos] vs pred [pos, neutral]: positive tp 1, fp 0, fn 1 -> 2/3.
    Averaging in the invented `neutral` (F1 0.0) would give 1/3 and would make
    the denominator depend on the model — two models, two denominators.
    """
    scores = scorer.sentiment_macro_f1(
        ["positive", "positive"], ["positive", "neutral"], ["ru"] * 2
    )
    assert scores["overall"] == pytest.approx(2 / 3)


def test_sentiment_macro_f1_on_a_single_language_repeats_the_overall_score():
    scores = scorer.sentiment_macro_f1(SENTIMENT_GOLD[3:], SENTIMENT_PRED[3:], ["ru"] * 3)
    assert set(scores) == {"overall", "ru"}
    assert scores["overall"] == pytest.approx(scores["ru"]) == pytest.approx(5 / 6)


def test_sentiment_macro_f1_rejects_an_all_unclear_input():
    with pytest.raises(ValueError, match="no scoreable rows"):
        scorer.sentiment_macro_f1([scorer.UNCLEAR], ["positive"], ["ua"])


# --- G1b: the persisted sarcasm slice ---------------------------------------
#
# Amendment 3.5 (3): the slice is the id list the anchor run persisted, and a
# row is FIXED only when the fine-tune is right on BOTH labels — it leaves the
# union of sentiment and sarcasm errors that put it there.
#
#   id   gold (sentiment, sarcasm)  tuned (sentiment, sarcasm)  in slice?  fixed?
#    a   negative  True             negative  True              yes        yes
#    b   negative  True             negative  False             yes        no (sarcasm)
#    c   positive  False            negative  False             yes        no (sentiment)
#    d   neutral   False            negative  True              NO         (broken outside it)
#
# fixed 1 of n 3 -> rate 1/3
SLICE_IDS = ["a", "b", "c"]
SLICE_GOLD = {
    "a": {"sentiment": "negative", "sarcasm": True},
    "b": {"sentiment": "negative", "sarcasm": True},
    "c": {"sentiment": "positive", "sarcasm": False},
    "d": {"sentiment": "neutral", "sarcasm": False},
}
SLICE_TUNED = {
    "a": {"sentiment": "negative", "sarcasm": True},
    "b": {"sentiment": "negative", "sarcasm": False},
    "c": {"sentiment": "negative", "sarcasm": False},
    "d": {"sentiment": "negative", "sarcasm": True},
}


def test_sarcasm_slice_fix_rate_counts_a_row_only_when_both_labels_are_right():
    assert scorer.sarcasm_slice_fix_rate(SLICE_IDS, SLICE_GOLD, SLICE_TUNED) == pytest.approx(
        {"fixed": 1, "n": 3, "rate": 1 / 3}
    )


def test_sarcasm_slice_fix_rate_scores_the_given_slice_and_never_recomputes_one():
    """Row `d` is wrong on both labels and outside the slice: it must not appear.

    This is the whole point of the amendment — a slice recomputed from whatever
    predictions the caller passed is not the pre-registered slice.
    """
    with_d = scorer.sarcasm_slice_fix_rate([*SLICE_IDS, "d"], SLICE_GOLD, SLICE_TUNED)
    assert with_d["n"] == 4 and with_d["fixed"] == 1  # the id list decides, nothing else
    assert scorer.sarcasm_slice_fix_rate(SLICE_IDS, SLICE_GOLD, SLICE_TUNED)["n"] == 3


def test_sarcasm_slice_fix_rate_refuses_a_slice_row_it_was_given_no_prediction_for():
    """An incomplete run must not read as a failed gate."""
    with pytest.raises(ValueError, match="no prediction"):
        scorer.sarcasm_slice_fix_rate(SLICE_IDS, SLICE_GOLD, {"a": SLICE_TUNED["a"]})


def test_sarcasm_slice_fix_rate_refuses_an_unclear_slice_row():
    """Dropping it would shrink the pre-registered denominator in silence."""
    gold = dict(SLICE_GOLD, b={"sentiment": scorer.UNCLEAR, "sarcasm": None})
    with pytest.raises(ValueError, match="unclear"):
        scorer.sarcasm_slice_fix_rate(SLICE_IDS, gold, SLICE_TUNED)


def test_sarcasm_slice_fix_rate_refuses_a_repeated_id():
    with pytest.raises(ValueError, match="repeats an id"):
        scorer.sarcasm_slice_fix_rate(["a", "a"], SLICE_GOLD, SLICE_TUNED)


def test_sarcasm_slice_fix_rate_refuses_an_empty_slice():
    with pytest.raises(ValueError, match="empty slice"):
        scorer.sarcasm_slice_fix_rate([], SLICE_GOLD, SLICE_TUNED)


# --- G1c: intents -----------------------------------------------------------
#
#   idx  gold                   pred        tp  fp  fn
#    0   {price}                {price}      1   0   0
#    1   {taste, price}         {taste}      1   0   1
#    2   {}                     {price}      0   1   0
#    3   {quality}              {}           0   0   1
#                                     total  2   1   2
# micro-F1 = 2*2 / (2*2 + 1 + 2) = 4/7
INTENT_GOLD = [{"price"}, {"taste", "price"}, set(), {"quality"}]
INTENT_PRED = [{"price"}, {"taste"}, {"price"}, set()]


def test_intents_micro_f1_matches_the_hand_computed_fixture():
    assert scorer.intents_micro_f1(INTENT_GOLD, INTENT_PRED) == pytest.approx(4 / 7)


def test_intents_micro_f1_excludes_unclear_rows():
    """`None` is the unclear marker where a label is a collection."""
    assert scorer.intents_micro_f1(
        [*INTENT_GOLD, None], [*INTENT_PRED, {"taste", "price"}]
    ) == pytest.approx(4 / 7)


def test_intents_micro_f1_scores_an_intent_nobody_predicts_through_recall():
    # gold [{packaging}, {price}] vs pred [{}, {price}]: tp 1, fp 0, fn 1 -> 2/3
    assert scorer.intents_micro_f1([{"packaging"}, {"price"}], [set(), {"price"}]) == pytest.approx(
        2 / 3
    )


# --- G1d: posts -------------------------------------------------------------
#
#   gold  [launch, promo, promo, other] vs pred [promo, promo, promo, other]
#   launch: tp 0, fp 0, fn 1 -> 0.0 · promo: tp 2, fp 1, fn 0 -> 4/5 · other: 1.0
#   macro = (0 + 0.8 + 1) / 3 = 0.6
def test_launch_detection_macro_f1_matches_the_hand_computed_fixture():
    score = scorer.launch_detection_macro_f1(
        ["launch", "promo", "promo", "other"], ["promo", "promo", "promo", "other"]
    )
    assert score == pytest.approx(0.6)


def test_launch_detection_macro_f1_excludes_unclear_rows():
    score = scorer.launch_detection_macro_f1(
        ["launch", "promo", "promo", "other", scorer.UNCLEAR],
        ["promo", "promo", "promo", "other", "launch"],
    )
    assert score == pytest.approx(0.6)


# gold [True, True, False, False] vs pred [True, False, False, False]
#   True:  tp 1, fp 0, fn 1 -> 2/3 · False: tp 2, fp 1, fn 0 -> 4/5
#   macro = (2/3 + 4/5) / 2 = 11/15
def test_relevance_macro_f1_matches_the_hand_computed_fixture():
    score = scorer.relevance_macro_f1([True, True, False, False], [True, False, False, False])
    assert score == pytest.approx(11 / 15)


def test_relevance_macro_f1_collapsing_to_one_class_still_scores_the_other_as_zero():
    """The realistic baseline failure: 26 relevant posts in 250, model says False.

    True: tp 0, fp 0, fn 1 -> 0.0 · False: tp 3, fp 1, fn 0 -> 6/7. macro = 3/7.
    """
    score = scorer.relevance_macro_f1([True, False, False, False], [False] * 4)
    assert score == pytest.approx((0.0 + 6 / 7) / 2)


# --- G1e: brands ------------------------------------------------------------
ALIASES = {"рудь": "rud", "ласунка": "lasunka", "яготинське": "yagotynske"}
#
#   post  gold                                    pred                       normalised
#    0    [{rud, "Рудь"}]                         [{null, "рудь"}]           gold {rud}  pred {rud}
#    1    [{null, "Dziugas"}]                     []                         gold {dziugas} pred {}
#    2    []                                      [{null, "Ласунка"}]        gold {} pred {lasunka}
#    3    [{null, "Комо"}, {null, "комо"}]        [{null, "Комо"}]           gold {комо} pred {комо}
#   tp 2 (rud, комо) · fp 1 (lasunka) · fn 1 (dziugas)
#   F1 = 2*2 / (2*2 + 1 + 1) = 2/3
BRAND_GOLD = [
    [{"brand_id": "rud", "mention": "Рудь"}],
    [{"brand_id": None, "mention": "Dziugas"}],
    [],
    [{"brand_id": None, "mention": "Комо"}, {"brand_id": None, "mention": "комо"}],
]
BRAND_PRED = [
    [{"brand_id": None, "mention": "рудь"}],
    [],
    [{"brand_id": None, "mention": "Ласунка"}],
    [{"brand_id": None, "mention": "Комо"}],
]


def test_brand_extraction_f1_matches_the_hand_computed_fixture():
    assert scorer.brand_extraction_f1(BRAND_GOLD, BRAND_PRED, ALIASES) == pytest.approx(2 / 3)


def test_brand_extraction_f1_keeps_brands_outside_the_watchlist_in_the_gold_set():
    """Dropping `Dziugas` would turn a miss into a free pass: 2/3 -> 1.0."""
    assert scorer.brand_extraction_f1(BRAND_GOLD, BRAND_PRED, ALIASES) < 1.0


def test_brand_extraction_f1_excludes_unclear_posts():
    assert scorer.brand_extraction_f1(
        [*BRAND_GOLD, None], [*BRAND_PRED, [{"brand_id": None, "mention": "Мгарське"}]], ALIASES
    ) == pytest.approx(2 / 3)


def test_normalise_brand_trusts_the_gold_brand_id_over_the_alias_map():
    """`Яготинська` is inflected — no casefolded lookup reproduces the human match."""
    entry = {"brand_id": "yagotynske", "mention": "Яготинська"}
    assert scorer.normalise_brand(entry, ALIASES) == "yagotynske"
    assert scorer.normalise_brand({"brand_id": None, "mention": " Рудь "}, ALIASES) == "rud"
    assert scorer.normalise_brand({"brand_id": None, "mention": "Baltais"}, ALIASES) == "baltais"


# --- the bars ---------------------------------------------------------------
#
# Anchors invented for the fixture on purpose: the real ones are measurements
# and live in `results/baselines.json` (amendment 3.5 (1)). A test that typed
# them would be the second copy that drifts.
#
#   G1a  overall 0.80 + 5 pp = 0.85 · floors ua 0.75 - 2 pp = 0.73, ru 0.70 - 2 pp = 0.68
#   G1b  ceil(0.60 * 44) = ceil(26.4) = 27 of 44
#   G1c  0.60 + 5 pp = 0.65 · G1d 0.90 - 1 pp = 0.89 · G1e 0.85 - 1 pp = 0.84
ANCHORS = {
    "G1a": {"overall": 0.80, "ua": 0.75, "ru": 0.70, "other": 0.60},
    "G1c": 0.60,
    "G1d": 0.90,
    "G1e": 0.85,
}


def test_gate_thresholds_matches_the_hand_computed_bars():
    bars = scorer.gate_thresholds(ANCHORS, slice_n=44)
    assert bars["G1a"]["min"] == pytest.approx(0.85)
    assert bars["G1a"]["floors"] == pytest.approx({"ua": 0.73, "ru": 0.68})
    assert bars["G1b"] == {"min_fixed": 27, "n": 44, "max_macro_f1_drop": 0.02}
    assert bars["G1c"]["min"] == pytest.approx(0.65)
    assert bars["G1d"]["min"] == pytest.approx(0.89)
    assert bars["G1e"]["min"] == pytest.approx(0.84)


def test_gate_thresholds_floors_only_the_languages_the_spec_gates():
    """`other` is in the record and out of the gate (amendment 3.1)."""
    assert set(scorer.gate_thresholds(ANCHORS, 44)["G1a"]["floors"]) == set(scorer.GATED_LANGUAGES)


def test_gate_thresholds_refuses_a_bar_above_the_metric_ceiling():
    """The negative control, and the situation amendment 3.5 (2) had to repair.

    An anchor of 0.97 with a +5 pp margin demands 1.02 of a macro-F1 — arithmetic
    about the gate, not a prediction about the model.
    """
    saturated = dict(ANCHORS, G1c=0.97)
    with pytest.raises(ValueError, match="above the 1.0 ceiling"):
        scorer.gate_thresholds(saturated, 44)


def test_gate_thresholds_rounds_the_g1b_count_up_without_the_binary_artefact():
    """0.60 * 45 is 27.000000000000004 in floating point: the bar is 27, not 28."""
    assert scorer.gate_thresholds(ANCHORS, 45)["G1b"]["min_fixed"] == 27
    assert scorer.gate_thresholds(ANCHORS, 46)["G1b"]["min_fixed"] == 28  # ceil(27.6)


# --- the mechanism ----------------------------------------------------------
def test_every_public_scorer_function_has_a_hand_computed_test():
    """Phase 1 asserted every gate refuses to run; from Phase 3 on it must be checked.

    Naming is the contract: a test for `foo` is named `test_foo_<what it pins>`.
    """
    tests = list(globals())
    uncovered = [name for name in PUBLIC if not any(t.startswith(f"test_{name}_") for t in tests)]
    assert PUBLIC, "scorer exposes no public functions"
    assert not uncovered, f"no hand-computed test for {uncovered}"
