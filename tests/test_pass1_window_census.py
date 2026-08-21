"""D2's census — the readings, and the one property that makes them safe to publish.

The census is the half of this contract nobody gates on, which is exactly why it needs a test: a
number that cannot fail a run can still be quoted as a verdict. So the assertions here are about
CAPTIONS and INSTRUMENTS as much as about arithmetic — that every report-only reading says it is
not a bar, that the fourteen carry their multiplicity, and that the two comparisons are the ones the
registration names rather than a third spelling nobody diffed.

The bar itself is not re-checked here. `census_pass1_window` CALLS
`gate_pass1_window.completeness`, and `tests/test_gate_pass1_window.py` drives that function's every
branch; a second assertion of the same verdict would be a second bar.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import census_pass1_window as census  # noqa: E402

CENSUS = json.loads((REPO_ROOT / "results" / "pass1_window_census.json").read_text("utf-8"))
RECORD = json.loads((REPO_ROOT / "results" / "prereg_pass1_window.json").read_text("utf-8"))
PACK = json.loads((REPO_ROOT / "results" / "pass1_window_pack.json").read_text("utf-8"))


def test_the_census_is_what_the_producer_writes_today(tmp_path):
    assert census.main(["--out", str(tmp_path / "again.json")]) == 0
    assert (tmp_path / "again.json").read_text("utf-8") == (
        REPO_ROOT / "results" / "pass1_window_census.json"
    ).read_text("utf-8")


def test_the_completeness_row_is_the_GATE_s_and_not_a_second_bar():
    """The census reports rung 7's verdict; the run record holds the gate's own append of it."""
    state = json.loads((REPO_ROOT / "results" / "pass1_window_run.json").read_text("utf-8"))
    recorded = [one for one in state["gates"] if one["kind"] == "completeness"]
    assert recorded, "rung 7 must have been recorded by the gate before D2 quotes it"
    bar = CENSUS["completeness"]
    assert bar["verdict"] == recorded[-1]["verdict"]
    for name in ("answered", "owed", "sha_mismatches", "parse_refusals"):
        assert bar[name] == recorded[-1][name], name
    assert bar["rule"] == RECORD["bars"]["completeness"]["rule"]


def test_every_report_only_reading_says_it_is_not_a_bar():
    block = CENSUS["report_only"]
    readings = [one for one in block.values() if isinstance(one, dict)]
    assert len(readings) == 4
    for one in readings:
        assert one["not_a_bar"] is True
        assert one["caption"]
        assert "passed" not in one and "minimum_agreed" not in one and "threshold" not in one


def test_the_fourteen_carry_their_multiplicity_and_their_refusals_by_name():
    block = CENSUS["report_only"]["the_fourteen"]
    assert block["multiplicity"] == 4
    assert "FOURTH look" in block["caption"]
    assert "never a bar" in block["caption"].lower()
    assert block["n"] == 14 == len(block["rows"])
    assert {
        (one["thread"], int(one["msg_id"])) for one in RECORD["population"]["gold"]["rows"]
    } == {(one["id"].rsplit("#", 1)[0], int(one["id"].rsplit("#", 1)[1])) for one in block["rows"]}
    # the two instruments that are NOT used, and why each is refused
    assert block["instrument"]["comparison"] == "market_pulse.scorer.reader_comment_agreement"
    assert "THRESHOLD arm" in block["instrument"]["why_not_bar_p1"]
    assert "0 of 14" in block["instrument"]["why_not_leg_table"]


def test_the_labelled_readings_go_through_the_function_the_contract_names():
    block = CENSUS["report_only"]
    for name in ("the_650_labelled_rows", "the_450_not_in_dev_200", "the_dev_200"):
        assert "leg_table" in block[name]["instrument"], name
    assert block["the_650_labelled_rows"]["n"] == 650
    assert block["the_450_not_in_dev_200"]["n"] == 450
    assert block["the_dev_200"]["n"] == 200
    # the 450 are the 650 minus the dev-200, so the three readings are one partition and not three
    # overlapping samples
    assert (
        block["the_450_not_in_dev_200"]["n"] + block["the_dev_200"]["n"]
        == block["the_650_labelled_rows"]["n"]
    )
    assert block["the_dev_200"]["r2_reported"] == {
        "agreed": 136,
        "n": 200,
        "our_agreed": 38,
        "our_n": 49,
    }


def test_the_pass_2_filter_table_covers_every_thread_and_names_what_it_does_not_price():
    filt = CENSUS["pass_2_filter"]
    assert filt["filter"] == list(census.OURS)
    # two denominators, both named: the cell's threads and the ones that carry a payable comment
    assert filt["threads_in_the_cell"] == len(PACK["per_thread"]) == 129
    assert filt["threads_carrying_a_payable_comment"] == len(filt["per_thread"]) == 127
    assert "carry no payable comment" in filt["why_two_denominators"]
    assert sum(one["payable_comments"] for one in filt["per_thread"]) == 1032
    assert filt["filtered_rows_total"] == sum(one["filtered_rows"] for one in filt["per_thread"])
    assert (
        filt["threads_with_at_least_one_filtered_row"] + filt["threads_pass_2_would_not_call"]
        == 127
    )
    # every thread's own label tally sums to its payable comments — no row is dropped or double-counted
    for one in filt["per_thread"]:
        assert sum(one["by_label"].values()) == one["payable_comments"], one["thread"]
    assert "does not exist yet" in filt["what_this_does_NOT_price"]


def test_the_filter_is_the_RULINGS_three_labels_and_not_the_dev_gates_two():
    """«наши»/`сеть_ритейлер` is the operator's own wording — a wider set than the dev gate's."""
    assert set(census.OURS) == {"категория_личное", "молочный_бренд", "сеть_ритейлер"}
    assert set(RECORD["bars"]["report_only"]["our_readings"]) == {
        "категория_личное",
        "молочный_бренд",
    }
    assert set(census.OURS) > set(RECORD["bars"]["report_only"]["our_readings"])


def test_the_spans_are_MEASURED_beside_what_was_CHARGED():
    spans = CENSUS["spans"]
    charged = spans["charged"]
    measured = spans["measured"]
    sums = RECORD["money"]["arithmetic"]
    assert charged["total_seconds"] == sums["total_seconds"]
    assert charged["seconds_per_call"] == sums["seconds_per_call"]["v2"]
    assert charged["overhead_seconds"] == sums["overhead_seconds"]
    for name in ("ssh_publish_seconds", "seconds_per_call_mean", "generation_seconds"):
        assert measured[name] is not None, name
    # the pod is closed and its bill is on the clock, not on a projection
    assert spans["deleted_at"] and spans["billed_seconds"] and spans["billed_usd"]
    assert spans["billed_seconds"] <= sums["cumulative"]["hard_stop_seconds"]
    assert spans["billed_usd"] <= RECORD["money"]["cap_usd_all_in"]
