"""K6's grader, driven on SYNTHETIC gold — because the real gold is the team lead's and lands later.

A grader written after its gold arrives is a grader nobody could have checked before it was used on
the only 50 rows there will be. So the shapes it has to get right are pinned here first: the
denominator the ruling fixed, the match rule, and the two readings that carry no bar.
"""

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

spec = importlib.util.spec_from_file_location("grade_positions", REPO_ROOT / "scripts" / "grade_positions.py")
grader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grader)


def row(**over):
    base = {
        "row_id": "@atb_market_official:4340:0",
        "brand": "Яготинське",
        "product": "молоко ультрапастеризоване 2.5%",
        "volume": "900 г",
        "price_promo": "49,90",
        "badge_pct": 20,
        "price_old": "62,40",
    }
    return {**base, **over}


def predicted(**over):
    base = {
        "brand": "Яготинське",
        "product": "молоко ультрапастеризоване 2.5%",
        "volume": "900г",
        "price_promo": 49.9,
        "discount_pct_printed": 20,
        "price_old": 62.4,
    }
    return {**base, **over}


def test_a_perfect_read_holds_both_bars():
    got = grader.grade([row()], [predicted()])
    assert got["bars"]["completeness"]["value"] == 1.0
    assert got["bars"]["price_accuracy"]["value"] == 1.0
    assert all(block["held"] for block in got["bars"].values())


def test_the_volume_is_matched_on_value_and_unit_not_on_text():
    """«900 г» and «900г» are one volume; «0.9 кг» is not, and a rule that folded them would forgive
    a real extraction error."""
    assert grader.grade([row()], [predicted(volume="900  г")])["bars"]["completeness"]["value"] == 1.0
    assert grader.grade([row()], [predicted(volume="0.9 кг")])["bars"]["completeness"]["value"] == 0.0


def test_the_price_bar_denominates_over_the_PROMO_price_only():
    """The 30.08 ruling. At the PAIR the bar is unreachable by measurement — 0.4125 on 33 of 80 —
    so a wrong OLD price must not move the bar, and it must still be reported."""
    got = grader.grade([row()], [predicted(price_old=999.0)])
    assert got["bars"]["price_accuracy"]["value"] == 1.0, "the old price is not in the denominator"
    assert got["readings"]["price_old"] == {
        "n": 1,
        "agree": 0,
        "note": got["readings"]["price_old"]["note"],
    }


def test_a_wrong_promo_price_is_the_only_thing_that_moves_the_price_bar():
    got = grader.grade([row()], [predicted(price_promo=51.0)])
    assert got["bars"]["price_accuracy"]["value"] == 0.0
    assert got["bars"]["completeness"]["value"] == 1.0, "it is still the same position"


def test_the_price_is_compared_as_a_NUMBER_and_not_as_text():
    """`49,90`, `49.90` and `49.9` are one price. A string compare would score formatting."""
    for form in ("49.90", "49,90", 49.9, " 49.9 "):
        assert grader.grade([row()], [predicted(price_promo=form)])["bars"]["price_accuracy"]["value"] == 1.0


def test_one_prediction_matches_at_most_one_gold_row():
    """A dict keyed by the triple would be last-wins and would forgive a duplicate: two gold rows
    and one prediction is 50% complete, not 100% ([[select_one_row_refuse_ambiguity]])."""
    gold = [row(row_id="a"), row(row_id="b")]
    got = grader.grade(gold, [predicted()])
    assert got["bars"]["completeness"]["value"] == 0.5
    assert got["readings"]["gold_rows_no_prediction_reached"] == 1


def test_a_prediction_no_gold_row_claims_is_reported_and_never_lifts_a_bar():
    """Precision is not a bar here, and a hallucinated row must not be silent either."""
    got = grader.grade([row()], [predicted(), predicted(brand="Молокія")])
    assert got["bars"]["completeness"]["value"] == 1.0
    assert got["readings"]["predicted_rows_no_gold_row_claims"] == 1


def test_a_gold_row_with_no_promo_price_leaves_the_price_denominator_and_not_completeness():
    """The two bars have two denominators, and folding them would let a missing gold price lift or
    sink the wrong number ([[measure_on_the_rows_the_gate_scores]])."""
    got = grader.grade([row(price_promo=None)], [predicted()])
    assert got["bars"]["completeness"]["value"] == 1.0
    assert got["bars"]["price_accuracy"]["scored"] == 0
    assert got["bars"]["price_accuracy"]["value"] is None


def test_the_bars_are_the_phase_specs_and_the_record_prints_them(tmp_path):
    assert grader.BARS == {"completeness": 0.90, "price_accuracy": 0.95}
    gold, pred, out = tmp_path / "g.jsonl", tmp_path / "p.jsonl", tmp_path / "o.json"
    gold.write_text(json.dumps(row(), ensure_ascii=False) + "\n", encoding="utf-8")
    pred.write_text(json.dumps(predicted(), ensure_ascii=False) + "\n", encoding="utf-8")
    assert grader.main(["--gold", str(gold), "--predicted", str(pred), "--out", str(out)]) == 0
    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["bars"]["completeness"]["bar"] == 0.90
    assert "brand surface form" in record["match_rule"]


def test_the_prediction_files_size_fields_are_the_same_volume_and_a_row_with_none_matches_nothing():
    """The defect of 10.09 (rr), both ways: `results/positions_50_predicted.jsonl` writes
    `size_value` + `size_unit` (and `badge_pct`) where the gold writes `volume` — that IS the row's
    volume and it matches; a prediction row carrying no volume in either spelling matches nothing
    and is counted, never a crash and never an empty key two such rows share."""
    sized = {
        k: v for k, v in predicted().items() if k not in ("volume", "discount_pct_printed", "price_old")
    }
    got = grader.grade([row()], [{**sized, "size_value": 900.0, "size_unit": "г", "badge_pct": 20}])
    assert got["bars"]["completeness"]["value"] == 1.0
    assert got["readings"]["printed_badge"] == {"n": 1, "agree": 1, "note": got["readings"]["printed_badge"]["note"]}
    assert "not carried" in got["readings"]["price_old"]["note"], "no prediction carries price_old"

    blind = grader.grade([row(volume=None), row()], [dict(sized)])
    assert blind["bars"]["completeness"]["value"] == 0.0, "no volume in either spelling matches nothing"
    assert blind["readings"]["gold_rows_no_prediction_reached"] == 2
    assert blind["readings"]["predicted_rows_no_gold_row_claims"] == 1
