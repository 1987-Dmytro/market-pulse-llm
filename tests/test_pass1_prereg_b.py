"""`results/prereg_pass1_probe_b.json` — the same instrument, one boot constant.

The claim this registration lives or dies on is that NOTHING bar P1 is scored on moved, so this file
asserts object equality against the frozen pass1-probe record key by key and then enumerates the
WHOLE diff, both ways. A record that says «object-equal» and is checked by eye is a record whose
fourth difference nobody notices.

Three things here are not paperwork:

* the boot charge is asserted to be the MAXIMUM of the two measurements this stack has, and the
  budget is re-derived from it — a constant charged from a sample of one is what put the last
  attempt 0.6 s from a kill it never reached;
* `money.arithmetic.boot_deadline_rule` is driven through `read_threads_reader_v4.deadlines`, the
  shipped function that reads it BY NAME and raised `KeyError` on a live pod;
* the re-solved gate table is asserted for ORDER and VERDICT, not only for its numbers, because the
  enumerated diff lets the table through as one opaque range.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import read_threads_reader_v4 as v4  # noqa: E402
import write_pass1_prereg as p1  # noqa: E402
import moved_pins  # noqa: E402
import write_pass1_prereg_b as prereg  # noqa: E402

RECORD_PATH = REPO_ROOT / "results" / "prereg_pass1_probe_b.json"
RECORD = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
PACK_PATH = REPO_ROOT / "results" / "pass1_probe_b_pack.json"
PACK = json.loads(PACK_PATH.read_text(encoding="utf-8"))

FROZEN_PATH = REPO_ROOT / "results" / "prereg_pass1_probe.json"
FROZEN = json.loads(FROZEN_PATH.read_text(encoding="utf-8"))
FROZEN_PACK = json.loads((REPO_ROOT / "results" / "pass1_probe_pack.json").read_text("utf-8"))

SCORED_ON = (
    "instruments",
    "population",
    "bars",
    "attempt",
    "return_to_sitting",
    "class",
    "non_gating",
)
"""The top-level keys that carry what bar P1 is measured WITH and measured AGAINST. Every one of
them must be the frozen record's own object, not a re-derivation that happens to agree today."""


def test_the_committed_registration_and_pack_are_what_the_producer_writes_today(tmp_path):
    """The rebuild is byte-identical EXCEPT where it pins `src/market_pulse/prompts.py`.

    `docs/PROMPT-pass1-fewshot.md` D0.2 registered `pass1_comment_gm4_v2` in that module and ruled
    old records' pins of it «moved since», never re-pinned. What the b-registration means rests on
    the registered TEXT, and `pass1_comment_gm4_v1`'s own sha has not moved — asserted below beside
    the diff, and by the producer's own refusal.
    """
    out, pack = tmp_path / "again.json", tmp_path / "pack.json"
    assert prereg.main(["--out", str(out), "--pack", str(pack)]) == 0
    # the record also pins THIS producer, which this contract edited; the pack does not
    for shipped_path, rebuilt_path, also in (
        (RECORD_PATH, out, (REPO_ROOT / "scripts" / "write_pass1_prereg_b.py",)),
        (PACK_PATH, pack, ()),
    ):
        shipped = json.loads(shipped_path.read_text(encoding="utf-8"))
        rebuilt = json.loads(rebuilt_path.read_text(encoding="utf-8"))
        moved_pins.assert_only_the_prompts_pin_moved(shipped, rebuilt, *also)
        assert shipped["instruments"]["prompt_sha256"] == rebuilt["instruments"]["prompt_sha256"]
    assert "generated_at" not in out.read_text(encoding="utf-8")


def test_everything_bar_P1_is_SCORED_ON_is_object_equal_to_the_frozen_record():
    for key in SCORED_ON:
        assert RECORD[key] == FROZEN[key], key
    # and the two that decide what the number MEANS, spelled out rather than left to the loop above
    assert RECORD["instruments"]["prompt_sha256"] == {
        "pass1_comment_gm4_v1": FROZEN["instruments"]["prompt_sha256"]["pass1_comment_gm4_v1"]
    }
    assert RECORD["bars"]["P1_per_comment_agreement"]["minimum_agreed"] == 12
    assert RECORD["return_to_sitting"].startswith("**A FAILED BAR GOES BACK TO THE SITTING")


def test_the_whole_diff_against_the_frozen_record_is_the_enumerated_one():
    """Both directions. A path that moved and is not enumerated is an instrument change wearing a
    transport contract's clothes; a path enumerated that did NOT move is an enumeration that has
    gone stale and stopped discriminating."""
    assert prereg.moved_paths(FROZEN, RECORD) == sorted(prereg.MOVED)
    assert prereg.moved_paths(FROZEN_PACK, PACK, opaque=()) == sorted(prereg.PACK_MOVED)
    assert PACK["items"] == FROZEN_PACK["items"], "the 64 units are the measurement itself"


def test_the_enumeration_refuses_a_path_it_does_not_name():
    """The negative control the enumeration is worthless without: a moved key outside the list has
    to REFUSE, and the refusal has to name it ([[guard_selftest_negative_control]])."""
    was = prereg.MOVED
    try:
        prereg.MOVED = tuple(name for name in was if name != "money.guard")
        with pytest.raises(SystemExit, match=r"unexpected: \['money.guard'\]"):
            prereg.build()
    finally:
        prereg.MOVED = was
    try:
        # a path that genuinely does not move. `instruments.parser.sha256` was the old choice and
        # it stopped discriminating the day D0.2 registered a second pass-1 text: the module pins
        # are now DERIVED into the allowed set, so enumerating one there proves nothing
        prereg.MOVED = (*was, "attempt")
        with pytest.raises(SystemExit, match=r"enumerated but unmoved: \['attempt'\]"):
            prereg.build()
    finally:
        prereg.MOVED = was


def test_the_producer_refuses_unless_pass1_probes_own_producer_still_rebuilds_its_frozen_record():
    """The object-equality claim rests on that rebuild, so breaking it must STOP rather than
    quietly register a b-record built on a moved instrument."""
    was = p1.BAR_P1_MIN
    try:
        p1.BAR_P1_MIN = 13
        with pytest.raises(SystemExit, match="no longer rebuilds from its own producer"):
            prereg.build()
    finally:
        p1.BAR_P1_MIN = was


def test_the_swap_refuses_to_replace_a_name_that_no_longer_exists():
    """A rename in the shipped producer must be loud here, not a silent second implementation."""
    was = p1.BOOT_KILL_S
    try:
        del p1.BOOT_KILL_S
        with pytest.raises(SystemExit, match="has no `BOOT_KILL_S` any more"):
            with prereg.as_probe_b():
                pass
    finally:
        p1.BOOT_KILL_S = was


def test_the_boot_is_charged_at_the_MAXIMUM_of_the_two_measurements_and_both_are_published():
    boot = RECORD["money"]["reading"]["boot"]
    assert boot["seconds"] == 300.0 == prereg.BOOT_CHARGED_S
    readings = {one["run"]: one for one in boot["measurements"]}
    assert set(readings) == {"reader-v5b", "pass1-probe"}
    assert readings["reader-v5b"]["seconds"] == FROZEN["money"]["reading"]["boot"]["seconds"]
    assert readings["pass1-probe"]["seconds_bound"] == [267, 293]
    assert boot["seconds"] >= max(
        readings["reader-v5b"]["seconds"], *readings["pass1-probe"]["seconds_bound"]
    ), "the charge is the MAX of what was measured, never a mean and never the older reading"
    assert readings["pass1-probe"]["kind"].startswith("BOUND"), (
        "the crash moment has no reading — the pod is gone and the witness is an ALIVE/DEAD pair"
    )


def test_the_budget_re_derives_at_the_new_ceiling_and_is_still_POSITIVE():
    """The four numbers the contract asks to be reproduced rather than trusted."""
    sums = RECORD["money"]["arithmetic"]
    assert sums["usable_seconds"] == 912.973
    assert sums["reading_projection_seconds"] == 409.728
    assert sums["affordability_deadline_seconds"] == 503.245
    assert sums["boot_kill_seconds"] == 420.0 == prereg.BOOT_KILL_S
    assert sums["pre_generation_budget_seconds"] == round(912.973 - 420.0 - 409.728, 3) == 83.245
    assert sums["pre_generation_budget_seconds"] > 0
    # the cap did not move, and neither did what one call is charged
    assert RECORD["money"]["cap_usd_all_in"] == FROZEN["money"]["cap_usd_all_in"] == 0.20
    assert sums["seconds_per_call_registered"] == 6.402
    assert sums["units"] == 64


def test_the_worst_case_re_derives_from_what_it_publishes_and_fits_the_cap():
    """And the contract's own figure is NAMED with the arithmetic that produces it, because a number
    nobody can re-derive is a number that gets re-decided ([[the_hand_typed_number_fails_the_total]]).
    """
    worst = RECORD["money"]["arithmetic"]["worst_case"]
    seconds = (
        worst["boot_kill_seconds"]
        + worst["reading_projection_seconds"]
        + worst["delete_margin_seconds"]
    )
    assert worst["seconds"] == round(seconds, 3) == 889.728
    assert worst["usd_at_the_worked_example"] == round(seconds * 0.74 / 3600.0, 6) == 0.182889
    assert worst["fits_the_cap"] is True and worst["usd_at_the_worked_example"] < 0.20
    stated = worst["the_contracts_figure"]
    assert stated["stated_usd"] == 0.175
    assert stated["seconds"] == round(912.973 - 60.0, 3)
    assert round(stated["usd"], 3) == 0.175, "the contract's figure charges the delete margin twice"
    assert stated["usd"] < worst["usd_at_the_worked_example"] < 0.20, (
        "both readings are inside the cap, so the deviation decides nothing about go/no-go"
    )


def test_the_re_solved_gate_table_kept_the_ORDER_and_every_VERDICT():
    """The enumerated diff lets the table through as one opaque range, so the discrimination it
    would otherwise carry is asserted here directly."""
    was = FROZEN["money"]["arithmetic"]["full_pass_over_the_registered_order"]
    now = RECORD["money"]["arithmetic"]["full_pass_over_the_registered_order"]
    assert [one["unit"] for one in now["per_unit"]] == [one["unit"] for one in was["per_unit"]]
    assert [one["unit"] for one in now["per_unit"]] == [one["id"] for one in PACK["items"]]
    assert {one["verdict"] for one in now["per_unit"]} == {"GO"}
    assert now["first_stop_after_units"] is None and was["first_stop_after_units"] is None
    assert now["unit_one_without_any_boot"] == was["unit_one_without_any_boot"], (
        "the zero-boot corner has no boot in it, so a boot charge cannot move it"
    )
    # what the extra 107.87 s of charged boot DID do, measured
    assert now["boot_seconds_charged"] == 300.0
    assert now["tightest"]["margin_seconds_per_unit"] == 3.226
    assert was["tightest"]["margin_seconds_per_unit"] == 4.938
    assert now["per_unit"][0]["headroom_seconds"] == 203.2
    assert was["per_unit"][0]["headroom_seconds"] == 311.1


def test_the_order_check_refuses_a_flipped_verdict():
    """Negative control for the check above: the guard must fire on the one change it exists for."""
    tampered = json.loads(json.dumps(RECORD))
    tampered["money"]["arithmetic"]["full_pass_over_the_registered_order"]["per_unit"][7][
        "verdict"
    ] = "STOP"
    assert prereg.the_registered_order_is_unmoved(FROZEN, tampered) == [
        "a unit's gate verdict changed"
    ]
    assert prereg.the_registered_order_is_unmoved(FROZEN, RECORD) == []


def test_the_boot_deadline_rule_is_the_key_the_SHIPPED_deadline_function_reads_by_name():
    """The regression that cost a live gate. `read_threads_reader_v4.deadlines` reads
    `money.arithmetic.boot_deadline_rule`; pass1-probe's record spelled it `boot_kill_rule` and the
    command raised `KeyError` with the meter running, on a record that could no longer be edited
    ([[a_frozen_record_is_an_input_to_shipped_code]])."""
    rate = 0.74 / 3600.0
    with pytest.raises(KeyError, match="boot_deadline_rule"):
        v4.deadlines(FROZEN, rate, 100.0, 92.0)
    gate = v4.deadlines(RECORD, rate, 100.0, 92.0)
    assert gate["rule"] == RECORD["money"]["arithmetic"]["boot_deadline_rule"]
    assert gate["contract_ceiling_seconds"] == 420.0
    assert gate["contract_ceiling_as_create_elapsed"] == 512.0
    assert gate["affordability_deadline_as_create_elapsed"] == 503.2
    assert gate["first_reply_must_land_by_create_elapsed"] == 503.2, (
        "at a 420 s ceiling and a 92 s staging the MONEY binds again, not the boot"
    )
    assert gate["verdict"] == "WAIT"


def test_the_binding_leg_flips_at_the_pre_generation_budget_and_the_record_says_which():
    """`pre_generation_budget_seconds` IS the create-elapsed above which the ceiling stops binding,
    and pass1-probe's own staging took 92 s — on the far side of it."""
    rate = 0.74 / 3600.0
    budget = RECORD["money"]["arithmetic"]["pre_generation_budget_seconds"]
    early = v4.deadlines(RECORD, rate, 10.0, budget - 1)
    late = v4.deadlines(RECORD, rate, 10.0, budget + 1)
    assert early["first_reply_must_land_by_create_elapsed"] == round(budget - 1 + 420.0, 1)
    assert late["first_reply_must_land_by_create_elapsed"] == 503.2
    assert "the MONEY binds this attempt" in RECORD["money"]["arithmetic"]["which_leg_binds"]


def test_the_transport_moved_the_ceiling_in_every_cell_that_carries_it():
    """Three cells state the same constant and a run that read a stale one would be gated by it."""
    assert RECORD["transport"]["boot_kill_seconds"] == 420.0
    assert RECORD["go_no_go"]["gates"]["2_boot_kill"]["boot_kill_seconds"] == 420.0
    assert RECORD["money"]["arithmetic"]["boot_kill_seconds"] == 420.0
    assert RECORD["transport"]["gate_0_ssh_deadman_seconds"] == 180.0, "gate 0 does NOT move"
    assert RECORD["go_no_go"]["gates"]["0_transport_ssh_deadman"]["max_recreates"] == 2


def test_the_pod_log_travels_with_the_jsonl_and_the_registration_says_so():
    """pass1-probe's only traceback was read off a screen and died with the pod
    ([[an_evidence_artifact_cannot_be_rederived]])."""
    assert "scp'd back INSIDE the poll loop" in RECORD["transport"]["pod_log"]
    assert "before" in RECORD["transport"]["pod_log"] and "gate" in RECORD["transport"]["pod_log"]


def test_the_registration_freezes_at_the_FIRST_pod_create_and_names_its_own_frozen_files():
    assert RECORD["class"] == FROZEN["class"]
    assert "FREEZES at the FIRST `pod create`" in RECORD["class"]
    assert RECORD["frozen_when_the_pod_exists"][:2] == [
        "results/prereg_pass1_probe_b.json",
        "results/pass1_probe_b_pack.json",
    ]
    assert RECORD["frozen_when_the_pod_exists"][2:] == FROZEN["frozen_when_the_pod_exists"][2:]


def test_the_supersedes_block_states_what_pass1_probe_measured_and_it_is_NOTHING():
    older = RECORD["supersedes"]
    assert older["record"] == "results/prereg_pass1_probe.json"
    assert "UNSCORED" in older["state"] and "427.0" in older["run_record"]["reading"]
    assert older["sha256"] == prereg.summary.sha256_of(FROZEN_PATH)
    assert any("boot CHARGE" in one for one in older["what_it_changes"])
    assert any("boot CEILING" in one for one in older["what_it_changes"])


def test_the_producer_pins_the_producer_it_CALLS_and_not_a_copy_of_it():
    called = RECORD["producer"]["calls"]
    assert "scripts/write_pass1_prereg.py" in called
    assert called["scripts/write_pass1_prereg.py"] == prereg.summary.sha256_of(
        REPO_ROOT / "scripts" / "write_pass1_prereg.py"
    )
    assert RECORD["producer"]["script"] == "scripts/write_pass1_prereg_b.py"
    assert RECORD["producer"]["borrowed"] == FROZEN["producer"]["borrowed"]
