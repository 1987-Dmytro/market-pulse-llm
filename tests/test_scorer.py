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


# --- the ablation's pre-registered decision ----------------------------------
#
# Amendment 3.4 (3): synthetic stays iff its arm's G1b fix-rate is strictly
# higher AND no other gated head is lower by more than 0.5 pp. Every fixture
# here is invented; the two arms' real numbers do not exist yet.

REAL = {
    "G1a": {"overall": 0.90, "ua": 0.89, "ru": 0.88},
    "G1b": 0.50,
    "G1c": 0.80,
    "G1d": 0.91,
    "G1e": 0.90,
}


def arm(**overrides) -> dict:
    return {**REAL, **overrides}


def test_select_arm_keeps_synthetic_when_it_wins_g1b_and_costs_nothing_material():
    #   G1b 0.50 -> 0.60 (higher) · G1a overall -0.001, others 0 -> no regression
    decision = scorer.select_arm(
        REAL, arm(G1b=0.60, G1a={"overall": 0.899, "ua": 0.89, "ru": 0.88})
    )
    assert decision["keep_synthetic"] is True
    assert decision["selected"] == "with-synthetic"
    assert decision["head_deltas"] == pytest.approx(
        {"G1a": -0.001, "G1c": 0.0, "G1d": 0.0, "G1e": 0.0}
    )
    assert decision["regressions"] == {}


def test_select_arm_rejects_synthetic_when_another_head_pays_for_the_fix_rate():
    #   G1b 0.50 -> 0.70, but G1c 0.80 -> 0.794 is -0.6 pp, past the 0.5 pp tolerance
    decision = scorer.select_arm(REAL, arm(G1b=0.70, G1c=0.794))
    assert decision["keep_synthetic"] is False
    assert decision["selected"] == "real-only"
    assert decision["regressions"] == pytest.approx({"G1c": -0.006})


def test_select_arm_reads_lower_by_more_than_as_more_than():
    #   G1c 0.80 -> 0.795 is exactly -0.5 pp: the rule says "MORE than 0.5 pp",
    #   so this is not a regression, and the subtraction's last bit must not decide it.
    decision = scorer.select_arm(REAL, arm(G1b=0.70, G1c=0.795))
    assert decision["head_deltas"]["G1c"] == -0.005
    assert decision["regressions"] == {}
    assert decision["keep_synthetic"] is True


def test_select_arm_needs_g1b_strictly_higher_not_merely_equal():
    assert scorer.select_arm(REAL, arm())["keep_synthetic"] is False
    assert scorer.select_arm(REAL, arm(G1b=0.49999))["keep_synthetic"] is False


def test_select_arm_protects_every_head_the_records_carry_not_a_typed_list():
    """The heads come from the data, so a gate added to the record cannot fall
    outside the rule by being forgotten here."""
    real = {"G1b": 0.5, "G1z": 0.90}
    assert scorer.select_arm(real, {"G1b": 0.9, "G1z": 0.80})["regressions"] == {"G1z": -0.1}
    with pytest.raises(ValueError, match="different heads"):
        scorer.select_arm(real, {"G1b": 0.9})


# --- the five verdicts -------------------------------------------------------
#
#   anchors G1a overall 0.90 (ua 0.90, ru 0.89) · G1c 0.80 · G1d 0.91 · G1e 0.89
#   bars    G1a >= 0.95 (ua >= 0.88, ru >= 0.87) · G1b >= 27 of 44, guard >= -0.02
#           G1c >= 0.85 · G1d >= 0.90 · G1e >= 0.88

VERDICT_ANCHORS = {
    "G1a": {"overall": 0.90, "ua": 0.90, "ru": 0.89},
    "G1c": 0.80,
    "G1d": 0.91,
    "G1e": 0.89,
}
VERDICT_BARS = scorer.gate_thresholds(VERDICT_ANCHORS, 44)
ON_THE_BAR = {
    "G1a": {"overall": 0.95, "ua": 0.88, "ru": 0.87},
    "G1b": {"fixed": 27, "guard_delta": -0.02},
    "G1c": 0.85,
    "G1d": 0.90,
    "G1e": 0.88,
}


def test_gate_verdicts_passes_a_run_that_lands_exactly_on_every_bar():
    """The gates are ">=". A model on its bar passes, and no addition's last bit
    may decide otherwise."""
    verdicts = scorer.gate_verdicts(ON_THE_BAR, VERDICT_BARS)
    assert [gate for gate, v in verdicts.items() if not v["pass"]] == []
    assert verdicts["G1b"]["n"] == 44


def test_gate_verdicts_fails_g1a_on_a_language_floor_the_overall_hides():
    """G1a is one gate with three checks: an overall above the bar does not buy
    a language that fell 2 pp."""
    values = {**ON_THE_BAR, "G1a": {"overall": 0.96, "ua": 0.88, "ru": 0.8699}}
    verdicts = scorer.gate_verdicts(values, VERDICT_BARS)
    assert verdicts["G1a"]["pass"] is False
    assert [c["what"] for c in verdicts["G1a"]["checks"] if not c["pass"]] == ["ru"]


def test_gate_verdicts_fails_g1b_when_the_guard_moves_even_if_the_slice_is_fixed():
    """ "Fixes >=60% WHILE overall macro-F1 degrades <=2 pp" — both halves are
    the gate, and a guard nobody checks is half a gate."""
    values = {**ON_THE_BAR, "G1b": {"fixed": 44, "guard_delta": -0.0201}}
    verdicts = scorer.gate_verdicts(values, VERDICT_BARS)
    assert verdicts["G1b"]["pass"] is False
    assert [c["what"] for c in verdicts["G1b"]["checks"] if not c["pass"]] == ["guard delta"]


def test_gate_verdicts_reports_each_no_regression_gate_against_its_own_bar():
    values = {**ON_THE_BAR, "G1d": 0.8999, "G1e": 0.9500}
    verdicts = scorer.gate_verdicts(values, VERDICT_BARS)
    assert verdicts["G1d"]["pass"] is False
    assert verdicts["G1e"]["pass"] is True
    assert verdicts["G1d"]["checks"][0]["bar"] == 0.90


# --- the same rule, transposed onto another head (4.5h2) ----------------------
#
# Amendment 3.4 (3) transposed, fixed before any 4.5h2 code or GPU spend: the
# пласт stays iff arm B's G1c is strictly higher AND no other gated head is
# lower by more than 0.5 pp. Every fixture here is invented.

PLAST_RULE = "the пласт stays iff arm B's G1c is strictly higher AND no other gated head is lower"
ARMS = ("without-plast", "with-plast")


def by_g1c(base, other):
    return scorer.select_arm_by(base, other, pivot="G1c", rule=PLAST_RULE, names=ARMS)


def test_select_arm_by_turns_on_the_pivot_it_is_given():
    """The same two arms decide differently under the two rules — which is the whole
    reason the pivot is a parameter and not a constant."""
    base = {"G1a": {"overall": 0.90}, "G1b": 0.60, "G1c": 0.80, "G1d": 0.90, "G1e": 0.90}
    other = base | {"G1b": 0.599, "G1c": 0.82}  # G1b a shade down, G1c up
    assert by_g1c(base, other)["selected"] == "with-plast"
    assert scorer.select_arm(base, other)["selected"] == "real-only"


def test_select_arm_by_protects_the_head_the_other_rule_turns_on():
    """Transposing the rule does not retire G1b — it demotes it to a protected head, so
    an arm that buys intents with a collapsed sarcasm slice is dropped."""
    base = {"G1a": {"overall": 0.90}, "G1b": 0.60, "G1c": 0.80, "G1d": 0.90, "G1e": 0.90}
    other = base | {"G1b": 0.50, "G1c": 0.95}
    decision = by_g1c(base, other)
    assert decision["g1c"]["strictly_higher"] is True
    assert decision["regressions"] == {"G1b": -0.1}
    assert decision["selected"] == "without-plast"


def test_select_arm_by_drops_the_arm_on_a_regression_however_good_the_pivot():
    base = {"G1a": {"overall": 0.90}, "G1b": 0.60, "G1c": 0.80, "G1d": 0.90, "G1e": 0.90}
    other = base | {"G1c": 0.95, "G1d": 0.89}  # 1 pp down: more than the tolerance
    decision = by_g1c(base, other)
    assert decision["regressions"] == {"G1d": -0.01}
    assert decision["keep"] is False and decision["selected"] == "without-plast"


def test_select_arm_by_treats_exactly_the_tolerance_as_no_regression():
    """ "lower by MORE than 0.5 pp" — and 0.90 - 0.895 is 0.005000000000000004."""
    base = {"G1a": {"overall": 0.90}, "G1b": 0.60, "G1c": 0.80, "G1d": 0.90, "G1e": 0.90}
    other = base | {"G1c": 0.81, "G1d": 0.895}
    assert by_g1c(base, other)["regressions"] == {}
    assert by_g1c(base, other)["keep"] is True


def test_select_arm_by_needs_the_pivot_to_be_reported():
    with pytest.raises(ValueError, match="the rule turns on G1c"):
        by_g1c({"G1a": 0.9}, {"G1a": 0.9})


def test_select_arm_by_names_the_arms_it_was_given():
    base = {"G1a": {"overall": 0.90}, "G1b": 0.60, "G1c": 0.80}
    decision = by_g1c(base, base | {"G1c": 0.81})
    assert decision["arms"] == list(ARMS)
    assert decision["g1c"][ARMS[0]] == 0.80 and decision["g1c"][ARMS[1]] == 0.81
    assert decision["rule"] == PLAST_RULE and decision["pivot"] == "G1c"


def test_select_arm_is_byte_identical_to_what_phase_4_recorded():
    """The wrapper must not move 4c's output: its ADR quotes the printed table."""
    base = {"G1a": {"overall": 0.9107}, "G1b": 0.4773, "G1c": 0.8212, "G1d": 0.9386}
    other = {"G1a": {"overall": 0.9172}, "G1b": 0.5455, "G1c": 0.8073, "G1d": 0.9159}
    decision = scorer.select_arm(base, other)
    assert decision["rule"] == scorer.SELECTION_RULE
    assert decision["g1b"]["strictly_higher"] is True
    assert decision["keep_synthetic"] is False
    assert decision["selected"] == "real-only"
    assert set(decision["regressions"]) == {"G1c", "G1d"}
