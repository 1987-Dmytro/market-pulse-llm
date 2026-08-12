"""Depth v2 over B′'s 80 pairs: the same arithmetic, a wider population, and one sentence checked.

The measurement's rules are `tests/test_measure_depth_from_pct.py`'s and are not re-tested here.
What is tested is what a second population can break: the numbers on the real 80, the adequacy rule
still being the v1 one (two readings under two rules are not comparable), and the clause of the
reading line that is PROSE rather than arithmetic — "every error is in the kopiyky" was true of 61
pairs from 22 pages and rides along onto 19 rows from four pages v1 never read.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import measure_depth_from_pct as measurer  # noqa: E402
import measure_depth_from_pct_skub2 as skub2  # noqa: E402


def real_rows() -> list[dict]:
    dump = REPO_ROOT / "results" / "sku_b_positions_skub2.jsonl"
    rows = [json.loads(line) for line in dump.read_text(encoding="utf-8").splitlines() if line]
    read = json.loads(skub2.PAIRS.read_text(encoding="utf-8"))
    return measurer.measure(measurer.pair_read.pair_rows(rows), read)


def test_main_measures_the_eighty_bought_pairs(tmp_path, capsys):
    out = tmp_path / "depth.json"
    assert skub2.main(["--out", str(out)]) == 0
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["n_pairs"] == 80 and len(written["rows"]) == 80

    badge = written["instruments"]["badge"]
    assert badge["median_abs_delta_pp"] == pytest.approx(0.3212, abs=5e-5)
    assert badge["max_abs_delta_pp"] == pytest.approx(1.4171, abs=5e-5)
    assert (badge["within_1pp"], badge["within_2pp"]) == (79, 80)

    extracted = written["instruments"]["extracted_old_price"]
    assert extracted["median_abs_delta_pp"] == pytest.approx(0.1670, abs=5e-5)
    assert extracted["max_abs_delta_pp"] == pytest.approx(1.6366, abs=5e-5)
    assert (extracted["within_1pp"], extracted["within_2pp"]) == (75, 80)

    assert badge["adequate"] and extracted["adequate"]
    assert "IS an adequate depth instrument" in written["reading"]
    assert written["read"]["path"].endswith("sku_b_pair_verdicts_skub2.json")
    assert "80 pairs" in capsys.readouterr().out


def test_the_reading_lines_causal_clause_is_true_on_this_population():
    """The one part of `reading()` that is not computed: "every error the team lead found is in the
    kopiyky and depth barely moves on them". It was measured on 61 pairs and this record ships it
    over 80 — including 19 the old instrument never produced, where a hryvnia-scale error would
    make the sentence false while every number around it stayed green."""
    rows = real_rows()
    errors = [row for row in rows if row["verdict"] == "wrong"]
    assert len(errors) == 47
    worst = max(abs(row["price_old_printed"] - row["price_old_extracted"]) for row in errors)
    assert worst < 1.0, "an error of a whole hryvnia is not 'in the kopiyky'"
    assert max(abs(row["delta_extracted"]) for row in rows) * 100 < 2.0
    assert max(abs(row["delta_badge"]) for row in rows) * 100 < 2.0


def test_the_nineteen_pages_v1_never_read_do_not_move_the_reading():
    """Where the widening could have bitten: the four newly readable pages are dense multi-item
    leaflets, and their olds read BETTER than the population's. Both instruments stay inside the
    rule on them, so the widened measurement says what the narrow one said."""
    new_pages = ("4342", "4405", "4446", "4467")
    fresh = [row for row in real_rows() if any(page in row["file"] for page in new_pages)]
    assert len(fresh) == 19
    for field in ("delta_badge", "delta_extracted"):
        assert measurer.adequate(measurer.summarise(fresh, field))


def test_the_adequacy_rule_is_the_v1_one_and_only_the_pending_ruling_moved():
    """The arithmetic is shared code, so it cannot drift; the SENTENCE could, and a rule that
    quietly widened between two readings would make the comparison meaningless."""
    assert measurer.WITHIN == (0.01, 0.02)
    for rule in (skub2.ADEQUACY, measurer.ADEQUACY):
        assert "within 2 pp of the true depth AND the median within 1 pp" in rule
        assert "STATED HERE, not registered" in rule
    assert "5c2 ruling" in skub2.ADEQUACY and "B′ design session" not in skub2.ADEQUACY
    assert "B′ design session" in measurer.ADEQUACY
    assert "5c2" in skub2.CLASS and skub2.CONTRACT.split()[0] == "docs/PROMPT-skub2-close.md"
    assert (REPO_ROOT / skub2.CONTRACT.split()[0]).exists()


def test_the_v1_measurement_still_writes_exactly_what_its_sealed_record_says():
    """The parameterisation lifted v1's `class` out of the dict into a constant. The pilot's record
    is sealed evidence: if that lift changed one character, the shipped file and the producer stop
    agreeing, and this is the only place that would notice."""
    sealed = json.loads((REPO_ROOT / "results" / "sku_depth_from_pct.json").read_text("utf-8"))
    assert sealed["class"] == measurer.CLASS
    assert sealed["adequacy_rule"] == measurer.ADEQUACY
    assert sealed["contract"] == measurer.CONTRACT
    assert sealed["n_pairs"] == 61
    assert (measurer.RECORD.name, measurer.OUT.name) == (
        "sku_b_positions_v4.json",
        "sku_depth_from_pct.json",
    )
    assert (skub2.OUT != measurer.OUT) and (skub2.PAIRS != measurer.PAIRS)


def test_the_depth_here_is_the_depth_the_skub2_dumps_own_producer_wrote():
    """The control against a second implementation, re-run on this population: on every pair the
    team lead marked correct the printed old price IS the extracted one, so this file's `depth` and
    `Position.depth` are being asked the same question on all 33 of them."""
    dump = REPO_ROOT / "results" / "sku_b_positions_skub2.jsonl"
    rows = [json.loads(line) for line in dump.read_text(encoding="utf-8").splitlines() if line]
    read = json.loads(skub2.PAIRS.read_text(encoding="utf-8"))
    keys = {(key["file"], key["price_promo"], key["price_old"]): key for key in read["keys"]}
    checked = 0
    for row in measurer.pair_read.pair_rows(rows):
        key = keys[(row["file"], row["price_promo"], row["price_old"])]
        if key["verdict"] != "correct":
            continue
        assert measurer.depth(row["price_promo"], key["printed_old"]) == pytest.approx(row["depth"])
        checked += 1
    assert checked == 33, "the 33 correct pairs are the ones both implementations can be asked"
