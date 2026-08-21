"""The window registration — the copy, the thresholds that MOVED, and H6 as an input audit.

`results/prereg_pass1_fewshot_r2.json` is the record this one copies its instruments and its kill
clock from, and a block copied for its ALGORITHM brings its NUMBERS with it — the class r2 itself
shipped as Dv613, when rung 4 priced r2's run with r1's repealed 1 800 s overhead
([[an_audit_of_pins_is_not_an_audit_of_thresholds]]). So the two numbers that had to move are
checked for having moved, and r2's own values are checked for being ABSENT from the money block.

H6 is checked for what it can actually catch. A money block's arithmetic is the same multiplication
done twice and cannot disagree with itself; what H6 audits is the INPUTS — the 1 032 (called, never
typed), the 2.726 s/call (re-summed from the 200 rows that produced it), the allowances carried from
r2 with their reasons, and the reachability of the bar's own two numbers.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass1_window_pack as pack_producer  # noqa: E402
import write_pass1_window_prereg as producer  # noqa: E402

RECORD = json.loads((REPO_ROOT / producer.OUT_NAME).read_text("utf-8"))
R2 = json.loads((REPO_ROOT / producer.R2_NAME).read_text("utf-8"))
PACK = json.loads((REPO_ROOT / pack_producer.OUT_NAME).read_text("utf-8"))
SUMS = RECORD["money"]["arithmetic"]


def rows_by_name() -> dict[str, dict]:
    return {one["name"]: one for one in RECORD["h6"]["rows"]}


def test_the_shipped_registration_is_what_the_producer_writes_today(tmp_path):
    assert producer.main(["--outdir", str(tmp_path)]) == 0
    assert (tmp_path / producer.OUT_NAME).read_text("utf-8") == (
        REPO_ROOT / producer.OUT_NAME
    ).read_text("utf-8")


def test_the_record_is_committed_and_equal_to_what_is_committed():
    """A pre-registration nobody committed is not a pre-registration — the gate refuses one."""
    path = REPO_ROOT / producer.OUT_NAME
    assert (
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path)], cwd=REPO_ROOT, capture_output=True
        ).returncode
        == 0
    ), "commit the registration BEFORE the pod exists"


# --- the copy, and its refusal -----------------------------------------------------------------------


def test_the_instruments_are_r2s_with_exactly_two_pins_MOVED():
    ours, theirs = RECORD["instruments"], R2["instruments"]
    for name in ("parser", "scorer", "transport", "prompt_sha256", "renderer"):
        assert ours[name] == theirs[name], name
    assert ours["v2_is_v1_plus_two_paragraphs"] == theirs["v2_is_v1_plus_two_paragraphs"]
    assert ours["prompt_v1_did_not_move"] is True
    # the two that move
    assert ours["gate"]["script"] == "scripts/gate_pass1_window.py" != theirs["gate"]["script"]
    assert ours["packs"]["producer"] == "scripts/build_pass1_window_pack.py"
    assert ours["packs"]["sha256"] != theirs["packs"]["sha256"]
    # r2's gate is IMPORTED, so it is pinned as an instrument and it is r2's own sealed sha
    assert ours["gate_imported_from"]["sha256"] == theirs["gate"]["sha256"]
    # and the one that is dropped says why
    assert "scorer_pass1_fewshot" not in ours
    assert "scorer_pass1_fewshot" in ours["dropped_from_r2"]


def test_every_copied_pin_resolves_against_the_LIVE_file():
    for path, value in producer.live_pins().items():
        assert producer.dig(RECORD["instruments"], path) == value, path
    assert RECORD["instruments"]["gate"]["sha256"] == producer.sha(producer.GATE)
    assert RECORD["instruments"]["packs"]["sha256"] == PACK["producer"]["sha256"]
    assert RECORD["population"]["sha256"] == producer.sha(producer.PACK)


def test_the_copy_REFUSES_when_a_copied_pin_stops_describing_this_checkout(monkeypatch):
    monkeypatch.setattr(
        producer, "live_pins", lambda: {"parser.sha256": "0" * 64, "scorer.sha256": "0" * 64}
    )
    with pytest.raises(SystemExit, match="no longer describes this checkout"):
        producer.instruments(R2)


def test_a_record_read_from_a_DIRTY_file_is_refused(tmp_path, monkeypatch):
    untracked = tmp_path / "not-committed.json"
    untracked.write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit, match="not tracked by git"):
        producer.sealed(untracked, "not-committed.json")


# --- the thresholds that HAD to move ------------------------------------------------------------------


def test_the_two_numbers_that_moved_off_r2_moved_and_r2s_values_survive_nowhere():
    assert RECORD["money"]["cap_usd_all_in"] == 1.50
    assert R2["money"]["cap_usd_all_in"] == 1.38
    assert SUMS["cumulative"]["hard_stop_seconds"] == 6500.0
    assert R2["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"] == 6100.0

    # a block copied for its algorithm carries its NUMBERS — so r2's are hunted for by VALUE, over
    # the numeric leaves. Prose that says «1 032 calls and not 464» is the point and must survive
    def leaves(node):
        if isinstance(node, dict):
            for key, value in node.items():
                yield from leaves(value)
        elif isinstance(node, list):
            for value in node:
                yield from leaves(value)
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            yield float(node)

    numbers = set(leaves(RECORD["money"]["arithmetic"]))
    for repealed in (6100.0, 1.38, 3076.552, 5476.552, 1.217012, 5976.552, 1.328123, 623.448):
        assert repealed not in numbers, repealed
    # 464 survives ONLY as r2's registered row count beside the measured 400, and it is named
    assert RECORD["money"]["arithmetic"]["overhead_measured_on_r2"]["rows_r2_registered"] == 464
    assert RECORD["money"]["arithmetic"]["overhead_measured_on_r2"]["rows_answered"] == 400


def test_the_allowances_r2_kept_are_kept_and_each_one_names_its_reading():
    assert SUMS["ssh_seconds_charged"] == 500.0
    assert SUMS["stage_launch_seconds_charged"] == 150.0
    assert SUMS["boot_seconds_charged"] == 450.0
    assert SUMS["overhead_seconds"] == 1300.0
    assert SUMS["cumulative"]["backstop_tolerance_seconds"] == 60.0
    assert SUMS["recovery_arithmetic"]["re_creations_allowed"] == 1
    # the boot ceiling is above every boot this stack has measured, r2's new FLOOR included
    every = [one for values in SUMS["boots_measured"].values() for one in values]
    assert SUMS["boot_seconds_charged"] >= max(every)
    assert 142.709 in every, "r2 measured a new floor and it belongs in the table"
    # the ssh spread carries all four readings, and the ceiling is above the widest lower bound
    assert len(SUMS["ssh_readings"]) == 4
    assert SUMS["ssh_seconds_charged"] >= max(SUMS["ssh_readings"].values())


def test_rung_4_and_the_money_block_charge_ONE_overhead():
    assert SUMS["cumulative"]["projection_gate"]["overhead_seconds"] == SUMS["overhead_seconds"]
    assert rows_by_name()["the_projection_gate_and_the_money_block_charge_ONE_overhead"]["agrees"]


def test_the_kill_clock_has_seven_rungs_and_rung_7_is_the_COMPLETENESS_bar():
    numbers = [one["rung"] for one in RECORD["kill_clock"]]
    assert numbers == [1, 2, 3, 4, 5, 6, 7]
    rung7 = RECORD["kill_clock"][-1]
    assert rung7["rule"] == RECORD["bars"]["completeness"]["rule"]
    assert "1032 / 1032" in rung7["rule"] or "1032" in rung7["rule"]
    # r2's rung 8 — the shot — has no counterpart here and was not carried over
    assert all("shot" not in json.dumps(one, ensure_ascii=False) for one in RECORD["kill_clock"])


# --- the money, re-derived ----------------------------------------------------------------------------


def test_the_money_is_derived_from_the_CALLED_population_and_the_MEASURED_rate():
    assert SUMS["calls"]["v2"] == len(PACK["legs"][0]["items"]) == 1032
    rate = producer.measured_v2_rate()
    assert SUMS["seconds_per_call"]["measured_mean"] == round(rate["mean"], 6)
    assert rate["rows"] == 200
    assert SUMS["seconds_per_call"]["sample"] == producer.R2_SAMPLE
    assert "8tpx8lf05n6skc" in SUMS["seconds_per_call"]["sample"]
    assert SUMS["seconds_per_call"]["sample_sha256"] == producer.sha(producer.DEV_V2_ROWS)
    # the charged rate is the ROUNDED measurement × the margin, and the rounding is conservative
    assert SUMS["seconds_per_call"]["v2"] >= rate["mean"] * SUMS["seconds_per_call"]["margin"]
    assert SUMS["generation_seconds"] == pytest.approx(1032 * SUMS["seconds_per_call"]["v2"])


def test_the_measured_rate_REFUSES_a_sample_that_is_not_the_one_it_names(tmp_path, monkeypatch):
    short = tmp_path / "short.jsonl"
    short.write_text(json.dumps({"seconds": 2.5}) + "\n", encoding="utf-8")
    monkeypatch.setattr(producer, "DEV_V2_ROWS", short)
    with pytest.raises(SystemExit, match="the sample this rate is named for is 200"):
        producer.measured_v2_rate()


def test_the_recovery_clause_is_REACHABLE_and_the_knife_edge_is_wider_than_rung_2():
    recovery = SUMS["recovery_arithmetic"]
    assert recovery["then_the_full_worst_case_seconds"] <= SUMS["cumulative"]["hard_stop_seconds"]
    assert recovery["then_the_full_worst_case_usd"] <= RECORD["money"]["cap_usd_all_in"]
    assert recovery["widest_dead_pod_that_still_fits_seconds"] == pytest.approx(
        SUMS["cumulative"]["hard_stop_seconds"] - SUMS["total_seconds"]
    )
    assert recovery["widest_dead_pod_that_still_fits_seconds"] > SUMS["ssh_seconds_charged"]
    # and the session ceiling is not what binds — the PLATFORM-held stop is
    assert SUMS["cumulative"]["session_ceiling_seconds"] >= SUMS["cumulative"]["hard_stop_seconds"]


def test_the_step_opens_with_no_pods_of_its_own():
    assert RECORD["money"]["step_sum"] == {
        "step_budget_usd": 1.50,
        "prior_pods_usd": 0.0,
        "sum_usd": 1.50,
        "rule": RECORD["money"]["step_sum"]["rule"],
    }
    assert RECORD["money"]["reading"]["step"] == "pass1-window"
    assert (
        not (REPO_ROOT / "results" / "pass1_window_run.json").exists()
        or json.loads((REPO_ROOT / "results" / "pass1_window_run.json").read_text("utf-8")).get(
            "pods"
        )
        == []
    )


# --- the bar -------------------------------------------------------------------------------------------


def test_the_bar_is_three_numbers_and_a_refusal_is_an_ANSWERED_row():
    bar = RECORD["bars"]["completeness"]
    assert (bar["owed"], bar["answered_minimum"]) == (1032, 1032)
    assert bar["sha_mismatches_maximum"] == 0
    assert bar["parse_refusals_maximum"] == 10 == int(1032 * bar["parse_refusals_fraction"])
    # the two numbers are only jointly satisfiable under this reading, and the record SAYS it
    assert "NOT disjoint" in bar["answered_means"]
    assert rows_by_name()["REASON — the bar's two numbers are jointly reachable"]["agrees"]


def test_the_report_only_readings_are_named_and_none_of_them_is_a_bar():
    block = RECORD["bars"]["report_only"]
    for name in (
        "the_fourteen",
        "the_650_labelled_rows",
        "the_450_not_in_dev_200",
        "the_dev_200",
        "the_label_distribution",
        "the_pass_2_filter_table",
    ):
        assert name in block, name
    assert "never a bar" in block["rule"] or "not a bar" in block["rule"]
    # the multiplicity sentence, and the refusal to promote it
    back = RECORD["return_to_the_operator"]
    assert "FOURTH" in back
    assert "cannot be promoted" in back
    assert "NOT an evaluation" in RECORD["what_this_run_is_not"]


def test_the_membership_counts_the_report_only_rows_need_are_in_the_record():
    assert RECORD["population"]["membership"] == {
        "gold_14": 14,
        "probe_64": 64,
        "labelled_650": 650,
        "dev_200": 200,
    }


# --- H6 --------------------------------------------------------------------------------------------------


def test_every_number_the_contract_prints_re_derives():
    assert RECORD["h6"]["mismatches"] == []
    rows = rows_by_name()
    printed = {
        "population_payable_comments": 1032,
        "population_threads": 129,
        "v2_seconds_per_call_measured": 2.726,
        "rate_margin": 1.25,
        "generation_seconds": 3516.54,
        "total_seconds": 5916.54,
        "hours": 1.6435,
        "worst_case_usd_at_the_price_ceiling": 1.3148,
        "worst_case_usd_at_the_lora_b_price": 0.8710,
        "hard_stop_usd_at_the_price_ceiling": 1.4444,
        "session_ceiling_seconds": 6750.0,
        "one_dead_pod_at_rung_2_usd": 0.1111,
        "one_dead_pod_then_the_full_worst_case_seconds": 6416.54,
        "one_dead_pod_then_the_full_worst_case_usd": 1.4259,
        "widest_dead_pod_that_still_fits_seconds": 583.46,
        "parse_refusals_maximum": 10,
    }
    for name, value in printed.items():
        assert rows[name]["registered"] == value, name
        assert rows[name]["agrees"], name


def test_H6_carries_rows_that_check_a_REASON_and_not_only_a_number():
    reasons = [one for one in RECORD["h6"]["rows"] if one["name"].startswith("REASON")]
    assert len(reasons) == 3
    assert all(one["agrees"] for one in reasons)
    overhead = next(one for one in reasons if "400 → 1032" in one["name"])
    measured = SUMS["overhead_measured_on_r2"]
    assert (measured["rows_answered"], measured["rows_r2_registered"]) == (400, 464)
    assert overhead["registered"] == measured["scaled_to_this_population_seconds"]
    assert overhead["re_derived"] == SUMS["overhead_seconds"] >= overhead["registered"]
    assert measured["headroom_multiple"] > 1


def test_H6_REFUSES_a_number_that_stops_re_deriving(monkeypatch):
    monkeypatch.setattr(producer, "CHARGED_SECONDS_PER_CALL", 3.0)
    rate = producer.measured_v2_rate()
    overhead = producer.r2_overhead_reading(
        producer.sealed(producer.R2_RUN, "results/pass1_fewshot_r2_run.json")
    )
    block = producer.h6(producer.arithmetic(rate, 1032, overhead), rate, 1032, 129)
    assert block["mismatches"], "a rate that no longer matches the contract must be a STOP"
    assert "generation_seconds" in {one["name"] for one in block["mismatches"]}
    assert block["reading"].endswith("this is a STOP")


def test_H6_REFUSES_a_hard_stop_that_no_longer_covers_the_recovery_clause(monkeypatch):
    monkeypatch.setattr(producer, "HARD_STOP_SECONDS", 6000.0)
    rate = producer.measured_v2_rate()
    overhead = producer.r2_overhead_reading(
        producer.sealed(producer.R2_RUN, "results/pass1_fewshot_r2_run.json")
    )
    block = producer.h6(producer.arithmetic(rate, 1032, overhead), rate, 1032, 129)
    failed = {one["name"] for one in block["mismatches"]}
    assert "the_recovery_clause_fits_the_hard_stop" in failed
    assert "the_knife_edge_is_wider_than_rung_2" in failed


def test_the_overhead_reading_comes_from_r2s_OWN_gate_record():
    measured = SUMS["overhead_measured_on_r2"]
    run = json.loads((REPO_ROOT / "results" / "pass1_fewshot_r2_run.json").read_text("utf-8"))
    pod = run["pods"][-1]
    watch = next(one for one in run["gates"] if one["kind"] == "watch" and one["verdict"] == "GO")
    assert measured["pod"] == pod["pod_id"]
    assert measured["billed_seconds"] == pod["billed_seconds"]
    assert (
        measured["create_elapsed_at_the_last_row_seconds"] == watch["elapsed_on_this_pod_seconds"]
    )
    assert measured["measured_after_the_last_row_seconds"] == pytest.approx(
        pod["billed_seconds"] - watch["elapsed_on_this_pod_seconds"]
    )
