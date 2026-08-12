"""Depth from the printed badge: the arithmetic by hand, and the control that keeps it honest.

The fixture is three pairs chosen so the two instruments land on opposite sides of the adequacy
rule — the badge inside it, the extracted old price outside — because a measurement whose reading
line only has one branch is a sentence, not a measurement.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import measure_depth_from_pct as measurer  # noqa: E402

#         promo   old(dump)  printed_old   badge     true   badge_d  extracted_d
#   A      50.0      100.0        100.0     50.0      0.50    0.00 pp     0.00 pp
#   B      75.0      100.0        125.0     40.0      0.40    0.00 pp   -15.00 pp
#   C      60.0      100.0        100.0     41.0      0.40   +1.00 pp     0.00 pp
FIXTURE = [
    ("A", 50.0, 100.0, 100.0, 50.0, "correct"),
    ("B", 75.0, 100.0, 125.0, 40.0, "wrong"),
    ("C", 60.0, 100.0, 100.0, 41.0, "correct"),
]


def pairs_and_read():
    pairs, keys = [], []
    for name, promo, old, printed, badge, verdict in FIXTURE:
        pairs.append(
            {
                "item": f"@a:{name}",
                "page": 1,
                "file": f"media/{name}.jpg",
                "price_promo": promo,
                "price_old": old,
                "discount_pct_printed": badge,
            }
        )
        keys.append(
            {
                "file": f"media/{name}.jpg",
                "price_promo": promo,
                "price_old": old,
                "verdict": verdict,
                "printed_old": printed,
            }
        )
    return pairs, {"keys": keys, "checksums": {"rows": len(keys)}}


def test_the_three_depths_are_the_hand_computed_ones():
    pairs, read = pairs_and_read()
    rows = measurer.measure(pairs, read)
    assert [row["true_depth"] for row in rows] == [0.5, 0.4, 0.4]
    assert [row["badge_depth"] for row in rows] == [0.5, 0.4, 0.41]
    assert [row["extracted_depth"] for row in rows] == [0.5, 0.25, 0.4]
    assert [round(row["delta_badge"], 10) for row in rows] == [0.0, 0.0, 0.01]
    assert [round(row["delta_extracted"], 10) for row in rows] == [0.0, -0.15, 0.0]


def test_the_summary_counts_the_tolerances_and_names_what_misses_one_point():
    pairs, read = pairs_and_read()
    rows = measurer.measure(pairs, read)
    badge = measurer.summarise(rows, "delta_badge")
    assert badge["median_abs_delta_pp"] == pytest.approx(0.0)
    assert badge["max_abs_delta_pp"] == pytest.approx(1.0)
    assert badge["mean_signed_delta_pp"] == pytest.approx(1 / 3)
    assert (badge["within_1pp"], badge["within_2pp"]) == (3, 3)  # 1 pp is inside a 1 pp tolerance
    assert badge["outside_1pp"] == []

    extracted = measurer.summarise(rows, "delta_extracted")
    assert extracted["max_abs_delta_pp"] == pytest.approx(15.0)
    assert (extracted["within_1pp"], extracted["within_2pp"]) == (2, 2)
    assert [row["item"] for row in extracted["outside_1pp"]] == ["@a:B"]


def test_the_reading_line_reads_both_instruments_and_has_both_branches():
    pairs, read = pairs_and_read()
    rows = measurer.measure(pairs, read)
    badge = measurer.summarise(rows, "delta_badge")
    extracted = measurer.summarise(rows, "delta_extracted")
    assert measurer.adequate(badge) and not measurer.adequate(extracted)
    line = measurer.reading(badge, extracted)
    assert line.startswith("the badge IS an adequate depth instrument for a weekly median")
    assert "already extracts is not" in line
    # the control: swap them and the sentence swaps with them
    flipped = measurer.reading(extracted, badge)
    assert flipped.startswith("the badge is NOT an adequate depth instrument")
    assert "already extracts also is" in flipped


def test_it_refuses_a_pair_no_ruled_on_key_covers():
    pairs, read = pairs_and_read()
    read["keys"] = read["keys"][:-1]
    with pytest.raises(SystemExit, match="media/C.jpg 60.0/100.0 is in no ruled-on key"):
        measurer.measure(pairs, read)


def test_it_refuses_a_read_that_is_not_keyed_uniquely():
    pairs, read = pairs_and_read()
    read["keys"].append(dict(read["keys"][0]))
    with pytest.raises(SystemExit, match="4 keys collapse to 3"):
        measurer.measure(pairs, read)


def test_it_refuses_a_pair_with_no_printed_percentage():
    pairs, read = pairs_and_read()
    pairs[1]["discount_pct_printed"] = None
    with pytest.raises(SystemExit, match="the badge has nothing to read"):
        measurer.measure(pairs, read)


# --- the real population -------------------------------------------------------


def test_main_measures_the_sixty_one_bought_pairs(tmp_path, capsys):
    out = tmp_path / "depth.json"
    assert measurer.main(["--out", str(out)]) == 0
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["n_pairs"] == 61 and len(written["rows"]) == 61

    badge = written["instruments"]["badge"]
    assert badge["median_abs_delta_pp"] == pytest.approx(0.2886, abs=5e-5)
    assert badge["max_abs_delta_pp"] == pytest.approx(1.4171, abs=5e-5)
    assert (badge["within_1pp"], badge["within_2pp"]) == (60, 61)

    extracted = written["instruments"]["extracted_old_price"]
    assert extracted["median_abs_delta_pp"] == pytest.approx(0.1761, abs=5e-5)
    assert extracted["max_abs_delta_pp"] == pytest.approx(1.6366, abs=5e-5)
    assert (extracted["within_1pp"], extracted["within_2pp"]) == (56, 61)

    assert badge["adequate"] and extracted["adequate"]
    assert "IS an adequate depth instrument" in written["reading"]
    assert "61 pairs" in capsys.readouterr().out


def test_the_depth_here_is_the_depth_the_dump_s_own_producer_wrote():
    """The control against a second implementation: on every pair the team lead marked correct the
    printed old price IS the extracted one, so this file's `depth` and `Position.depth` are being
    asked the same question and have to answer it identically on all 20 of them."""
    dump = REPO_ROOT / "results" / "sku_b_positions_v4.jsonl"
    rows = [json.loads(line) for line in dump.read_text(encoding="utf-8").splitlines() if line]
    read = json.loads((REPO_ROOT / "results" / "sku_b_pair_verdicts.json").read_text("utf-8"))
    keys = {(k["file"], k["price_promo"], k["price_old"]): k for k in read["keys"]}
    checked = 0
    for row in measurer.pair_read.pair_rows(rows):
        key = keys[(row["file"], row["price_promo"], row["price_old"])]
        if key["verdict"] != "correct":
            continue
        assert measurer.depth(row["price_promo"], key["printed_old"]) == pytest.approx(row["depth"])
        checked += 1
    assert checked == 20, "the 20 correct pairs are the ones both implementations can be asked"
