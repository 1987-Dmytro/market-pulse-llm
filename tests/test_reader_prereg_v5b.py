"""`results/prereg_reader_probe_v5b.json` — the same instrument, three transport differences.

The claim this registration lives or dies on is that NOTHING the reader is scored on moved, so this
file asserts object equality against the frozen v5 record key by key and then enumerates the whole
diff: a record that says «object-equal» and is checked by eye is a record whose fourth difference
nobody notices. The re-solved full-pass gate is asserted too, verdict and all — a finding that only
lives in a report is a finding the next contract can lose.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import read_threads_reader_v5 as driver  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_reader_prereg_v5 as v5writer  # noqa: E402
import write_reader_prereg_v5b as prereg  # noqa: E402

RECORD_PATH = REPO_ROOT / "results" / "prereg_reader_probe_v5b.json"
RECORD = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
V5_PATH = REPO_ROOT / "results" / "prereg_reader_probe_v5.json"
V5 = json.loads(V5_PATH.read_text(encoding="utf-8"))

SCORED_ON = ("instruments", "attempt", "completeness", "programme_stop_rule", "scoring_rules")
"""The top-level keys that carry what the reader is measured with and measured against. Every one of
them must be the frozen record's own object, not a re-derivation that agrees today."""

THE_WHOLE_DIFF = {
    "authority",
    "bars",
    "class",
    "contract",
    "frozen_when_the_pod_exists",
    "go_no_go",
    "money",
    "non_gating",
    "phase",
    "population",
    "producer",
    "supersedes",
    "transport",
}


def test_the_committed_registration_is_what_the_producer_writes_today(tmp_path):
    """No clock is stamped, so the record re-derives byte for byte and its date is the date of the
    commit that carries it — the only witness that it preceded the first pod."""
    out = tmp_path / "again.json"
    assert prereg.main(["--out", str(out)]) == 0
    assert out.read_bytes() == RECORD_PATH.read_bytes()
    assert "generated_at" not in RECORD_PATH.read_text(encoding="utf-8")


# --- the instrument does not move ----------------------------------------------------------------


def test_everything_the_reader_is_SCORED_ON_is_object_equal_to_the_frozen_v5_record():
    for key in SCORED_ON:
        assert RECORD[key] == V5[key], key
    assert RECORD["instruments"]["task"] == "reader_thread_gm4_v5"
    assert RECORD["instruments"]["ceilings"]["output_tokens"] == 4000
    assert RECORD["instruments"]["gold"] == V5["instruments"]["gold"]
    assert RECORD["instruments"]["scorer"] == V5["instruments"]["scorer"]
    assert RECORD["instruments"]["serving"] == V5["instruments"]["serving"]


def test_bars_one_to_four_and_leg_bs_four_are_object_equal_and_only_bar_five_is_re_priced():
    moved = sorted(name for name in RECORD["bars"] if RECORD["bars"][name] != V5["bars"][name])
    assert moved == ["5_time_and_cost"]
    assert set(RECORD["bars"]) == set(V5["bars"])
    assert RECORD["bars"]["5_time_and_cost"]["thresholds"] == {"cap_usd_all_in": 0.50}
    assert V5["bars"]["5_time_and_cost"]["thresholds"] == {"cap_usd_all_in": 0.45}
    assert "segment of it, dead pods included" in RECORD["bars"]["5_time_and_cost"]["segments"]


def test_the_whole_diff_against_v5_is_the_enumerated_one():
    """The other half of object equality: a key that moved and is not on this list is a difference
    nobody registered ([[a_consumer_list_is_not_a_meaning_list]])."""
    moved = {key for key in set(RECORD) | set(V5) if RECORD.get(key) != V5.get(key)}
    assert moved == THE_WHOLE_DIFF
    assert set(RECORD) == set(V5)
    assert not moved & set(SCORED_ON)


def test_the_producer_refuses_unless_v5s_own_producer_still_rebuilds_v5s_frozen_record():
    """«The instrument does not move» is a refusal here and not a sentence: the v5 producer is called
    and its output compared to the frozen file before one key is overridden."""
    assert prereg.SUPERSEDES == V5_PATH
    assert RECORD["producer"]["calls"]["scripts/write_reader_prereg_v5.py"] == summary.sha256_of(
        REPO_ROOT / "scripts" / "write_reader_prereg_v5.py"
    )
    assert "this is a refusal" in RECORD["producer"]["calls"]["rule"]
    assert RECORD["supersedes"]["sha256"] == summary.sha256_of(V5_PATH)


# --- difference 1: the cap ------------------------------------------------------------------------


def test_the_cap_is_the_only_input_the_money_block_changed():
    """Both projections are the SAME numbers: the cap moves what is affordable, never what the
    reading is expected to cost."""
    assert RECORD["money"]["cap_usd_all_in"] == prereg.CAP_USD == 0.50
    old, new = V5["money"]["arithmetic"], RECORD["money"]["arithmetic"]
    assert new["leg_a"] == old["leg_a"] and new["leg_b"] == old["leg_b"]
    assert new["reading_projection_seconds"] == old["reading_projection_seconds"] == 1454.0
    assert new["boot_kill_seconds"] == old["boot_kill_seconds"] == 720.0
    assert new["delete_margin_seconds"] == old["delete_margin_seconds"] == 60.0
    assert new["seconds_the_cap_buys"] == round(0.50 * 3600 / 0.74, 3) == 2432.432
    assert new["usable_seconds"] == round(0.50 * 3600 / 0.74 - 60, 3) == 2372.432


def test_the_pre_generation_budget_is_POSITIVE_and_the_two_readings_are_published_apart():
    """The contract's «~918 s» and the registered `pre_generation_budget_seconds` are two different
    quantities and both are positive at this cap; v5's budget was −44.785 and that sign was the
    statement ([[two_readings_of_one_clause]])."""
    sums = RECORD["money"]["arithmetic"]
    usable, projection = sums["usable_seconds"], sums["reading_projection_seconds"]
    # both are computed at full precision against a projection published rounded to a tenth, so
    # a re-derivation off the published fields lands within 0.1 s and the record says so
    assert sums["affordability_deadline_as_create_elapsed"] == pytest.approx(
        usable - projection, abs=0.1
    )
    assert sums["pre_generation_budget_seconds"] == pytest.approx(
        usable - 720.0 - projection, abs=0.1
    )
    assert "within 0.1 s of it" in RECORD["money"]["segments"]["rounding"]
    assert (
        sums["pre_generation_budget_seconds"]
        > 0
        > V5["money"]["arithmetic"]["pre_generation_budget_seconds"]
    )
    assert (
        "~918 s with one segment» is the AFFORDABILITY"
        in (RECORD["money"]["segments"]["budget_reading"])
    )


def test_the_budget_is_reported_and_gates_nothing_in_the_boot_rule():
    """It is a forecast about a leg nobody has measured on this stack, so the KILL/WAIT branches may
    not read it. Driven through the deadline function rather than read off the record."""
    rate = 0.74 / 3600.0
    gate = driver.deadlines(RECORD, rate, elapsed=10.0, generation_at=5.0)
    assert gate["verdict"] == "WAIT"
    assert gate["which_binds"].startswith("the contract's twelve minutes")
    # the twelve minutes now binds where v5's affordability did, and the budget appears beside them
    assert gate["first_reply_must_land_by_create_elapsed"] == 725.0
    assert gate["pre_generation_budget_seconds"] > 0
    later = driver.deadlines(RECORD, rate, elapsed=10.0, generation_at=400.0)
    assert later["which_binds"].startswith("affordability")


# --- difference 2: the ssh dead-man and the segments ----------------------------------------------


def test_gate_zero_is_registered_with_its_threshold_its_ceiling_and_the_third_pod_stop():
    gate = RECORD["go_no_go"]["gates"]["0_transport_ssh_deadman"]
    assert gate["threshold_seconds"] == prereg.SSH_DEADMAN_S == 180.0
    assert gate["max_recreates"] == prereg.MAX_RECREATES == 2
    assert "DATACENTER STATE" in gate["third_pod_is_a_stop"]
    assert "BEFORE `pod create`" in gate["never_two_pods"]
    assert gate["expected_usd"] == 0.0
    # the gates v5 registered are still there and 1 and 3's staging and binding rules did not move
    assert set(RECORD["go_no_go"]["gates"]) == {
        "0_transport_ssh_deadman",
        "1_staging",
        "2_boot_kill",
        "3_the_full_pass",
    }
    assert RECORD["go_no_go"]["gates"]["1_staging"] == V5["go_no_go"]["gates"]["1_staging"]
    for key in ("binding", "rule", "solved_for_seconds", "re_checked_after_every_thread"):
        assert (
            RECORD["go_no_go"]["gates"]["3_the_full_pass"][key]
            == V5["go_no_go"]["gates"]["3_the_full_pass"][key]
        )


def test_the_segment_table_derives_from_the_published_one_segment_figures():
    """Row one IS the published number, so a reader cannot find two answers to one question; the
    later rows are it minus what a dead pod bills."""
    sums = RECORD["money"]["arithmetic"]
    segments = RECORD["money"]["segments"]
    dead = segments["a_dead_segment_costs_seconds"]
    assert dead == prereg.SSH_DEADMAN_S + sums["delete_margin_seconds"] == 240.0
    rows = segments["at_each_segment_count"]
    assert [one["segments"] for one in rows] == [1, 2, 3]
    assert rows[0]["usable_seconds"] == round(sums["usable_seconds"], 1)
    assert rows[0]["affordability_deadline_as_segment_elapsed"] == round(
        sums["affordability_deadline_as_create_elapsed"], 1
    )
    assert rows[0]["pre_generation_budget_seconds"] == round(
        sums["pre_generation_budget_seconds"], 1
    )
    for index, row in enumerate(rows):
        assert row["billed_before_this_segment_seconds"] == round(index * dead, 1)
        assert row["usable_seconds"] == round(rows[0]["usable_seconds"] - index * dead, 1)


def test_the_third_segment_can_STILL_afford_the_whole_reading():
    """The ruling caps the recreates; this is what caps their cost. Two dead pods at 240 s each is
    480 s of the 918.5 s the affordability leg allows before the reading stops fitting."""
    segments = RECORD["money"]["segments"]
    reach = segments["reachability"]
    bound = reach["billed_seconds_before_the_reading_no_longer_fits"]
    assert bound == round(
        RECORD["money"]["arithmetic"]["affordability_deadline_as_create_elapsed"], 1
    )
    assert bound > prereg.MAX_RECREATES * segments["a_dead_segment_costs_seconds"]
    assert reach["per_dead_segment_at_the_ceiling_seconds"] == round(bound / 2, 1)
    assert all(one["the_reading_still_fits"] for one in segments["at_each_segment_count"])
    # and one more dead pod does not fit, which is what makes the bound a bound
    assert bound < (prereg.MAX_RECREATES + 2) * segments["a_dead_segment_costs_seconds"]


def test_the_resume_protocol_normalizes_the_file_BEFORE_it_goes_back_up():
    """The chain the two step-0.5 fixes do not close on their own: a torn last line that travels
    becomes a torn MIDDLE line on the replacement pod, which raises on the kill-rule path."""
    protocol = RECORD["transport"]["resume_protocol"]
    assert "NORMALIZES" in protocol and "byte prefix" in protocol
    assert "torn unit is UNANSWERED and is re-asked" in protocol
    assert "never re-asked" in protocol


# --- difference 3: the order ----------------------------------------------------------------------


def test_the_order_is_descending_payable_with_a_TOTAL_key_and_the_tiebreak_registered():
    """`-payable` alone is not a total order here: six counts are shared by two or three threads, so
    two builds of one registration could produce two packs ([[an_order_key_that_is_not_total]])."""
    threads = RECORD["population"]["leg_a"]["enumeration"]["threads"]
    counts = [one["payable_comments"] for one in threads]
    assert counts == sorted(counts, reverse=True)
    assert counts == [15, 12, 12, 12, 10, 9, 9, 8, 7, 5, 5, 5, 4, 4, 3, 3, 2, 2, 2, 2, 2, 1, 0]
    keys = [prereg.order_key(one) for one in threads]
    assert keys == sorted(keys) and len(set(keys)) == len(keys)
    assert RECORD["population"]["leg_a"]["order"] == [one["thread"] for one in threads]
    assert "ties broken by the thread id ascending" in (RECORD["population"]["leg_a"]["order_rule"])
    # the ties are named, so a reader can see the tiebreak had work to do
    assert "[12, 9, 5, 4, 3, 2]" in RECORD["population"]["leg_a"]["order_rule"]


def test_only_the_ORDER_moved_and_not_one_unit_of_the_population():
    """The pairing three contracts have paid for: same 23 threads, same 23 rendering shas, same
    digest, same leg B. A re-ordered enumeration that also re-rendered anything would be a new
    population wearing the old digest."""
    old = V5["population"]["leg_a"]["enumeration"]
    new = RECORD["population"]["leg_a"]["enumeration"]
    assert new["digest"] == old["digest"]
    assert {json.dumps(one, sort_keys=True) for one in new["threads"]} == {
        json.dumps(one, sort_keys=True) for one in old["threads"]
    }
    assert {(one["thread"], one["rendering_sha256"]) for one in new["threads"]} == {
        (one["thread"], one["rendering_sha256"]) for one in old["threads"]
    }
    assert RECORD["population"]["leg_b"] == V5["population"]["leg_b"]
    assert sum(one["payable_comments"] for one in new["threads"]) == 134


def test_the_registered_order_makes_the_FIRST_full_pass_gate_STOP():
    """The finding this registration was measured for, asserted so it cannot quietly disappear.

    Reading the payable-dense threads first removes v5's knife-edge at unit 2 and creates a worse one
    at unit 1: the by-UNIT leg extrapolates 25 unread units off whatever the first reply cost, and the
    first unit is now the second-slowest thread v4 measured.
    """
    gate = RECORD["money"]["arithmetic"]["full_pass_over_the_registered_order"]
    assert gate["first_stop_after_units"] == 1
    assert gate["rows"][0]["unit"] == "@matusi_ukr:22272"
    assert gate["rows"][0]["binding"] == "by_unit" and gate["rows"][0]["factor"] == 25.0
    assert gate["rows"][0]["verdict"] == "STOP"
    assert gate["tightest_margin"]["after_units"] == 1
    assert gate["tightest_margin"]["seconds"] < 0
    assert all(one["verdict"] == "GO" for one in gate["rows"][1:])
    assert "not a threshold" in gate["reported_not_gating"]


def test_the_first_gates_verdict_does_not_depend_on_the_boot_at_all():
    """The loosest possible reading of the first gate charges NO provisioning and no model load, and
    the first unit still does not fit — so the STOP is arithmetic and not a forecast about a boot."""
    free = RECORD["money"]["arithmetic"]["full_pass_over_the_registered_order"][
        "the_first_gate_is_boot_free"
    ]
    usable = RECORD["money"]["arithmetic"]["usable_seconds"]
    assert free["ceiling_at_zero_boot_seconds"] == round(usable / 26, 1)
    assert free["expected_seconds"] > free["ceiling_at_zero_boot_seconds"]
    assert free["clears_at_zero_boot"] is False
    assert free["first_unit_payable_comments"] == 15


def test_the_table_was_solved_with_the_LIVE_gates_own_function_at_v4s_measured_seconds():
    """A table computed by a second spelling of the inequality would prove nothing about the gate
    that runs on the pod. The seconds are v4's own, off v4's own evidence file."""
    gate = RECORD["money"]["arithmetic"]["full_pass_over_the_registered_order"]
    assert "read_threads_reader_v5.projection" in gate["method"]
    growth = RECORD["money"]["arithmetic"]["leg_a"]["growth_vs_v4"]
    measured = {row["thread"]: row["seconds"]["worker"] for row in v5writer.v4_rows()}
    assert len(gate["rows"]) == 26
    for row in gate["rows"][:23]:
        assert row["expected_seconds"] == round(measured[row["unit"]] * growth, 1)
    for row in gate["rows"][23:]:
        assert row["unit"].startswith("@klopotenkofood:6040#")


# --- the freeze ----------------------------------------------------------------------------------


def test_the_registration_freezes_at_the_FIRST_pod_create_and_a_recreate_reads_the_same_record():
    assert "FIRST `pod create` of the attempt" in RECORD["class"]
    assert "a recreated pod reads the SAME frozen" in RECORD["class"]
    frozen = RECORD["frozen_when_the_pod_exists"]
    assert frozen[:3] == [
        "results/prereg_reader_probe_v5b.json",
        "results/prereg_reader_probe_v5.json",
        "results/reader_v5b_pack.json",
    ]
    assert frozen[3:] == V5["frozen_when_the_pod_exists"][1:]
    assert "docs/PROMPT-reader-v5b.md" in RECORD["authority"]
    assert RECORD["authority"]["results/reader_v5_run.json"] == summary.sha256_of(
        REPO_ROOT / "results" / "reader_v5_run.json"
    )
    assert RECORD["phase"] == "reader-v5b" and RECORD["contract"] == "docs/PROMPT-reader-v5b.md"
