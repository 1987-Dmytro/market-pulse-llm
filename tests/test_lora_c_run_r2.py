"""`lora-c-run r2` — the marker fix, the re-derived money, and every rung DRIVEN at $0.

Three things this file is for, in the order the contract buys them:

* **step 0.75, the marker fix.** Ruling (о) forbids the FALSE production string in a synthetic
  header. What is asserted is not that the constant exists but the two counts that make the fix
  real: `prompts.NO_POST_TEXT` in 0 of the 160, and the registered constant in 160 of the 160 and 0
  of the 506 — the confound that remains, named rather than hidden.
* **D2's money.** The card ruling (о) names has a price column, the marker census is charged where
  it actually falls, and the break-even is re-derived rather than quoted.
The nine session rungs are the third piece and they have their own file, `tests/test_gate_lora_c.py`
— the shape `tests/test_gate_lora_b.py` already has for line B.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_lora_c_data as data  # noqa: E402
import check_stamped  # noqa: E402

from market_pulse import prompts  # noqa: E402

PREREG = json.loads((REPO_ROOT / "results" / "prereg_lora_c.json").read_text("utf-8"))
ARM_B = json.loads((REPO_ROOT / "results" / "lora_c_arm_b.json").read_text("utf-8"))
CENSUS = json.loads((REPO_ROOT / "results" / "lora_c_encode_census_arm_b.json").read_text("utf-8"))
ROWS = [
    json.loads(one)
    for one in (REPO_ROOT / "results" / "pass1_sft_v3_arm_b.jsonl").read_text("utf-8").splitlines()
    if one
]
REAL, SYNTHETIC = ROWS[:506], ROWS[506:]


# --- step 0.75: the marker fix -------------------------------------------------------------------


def test_the_false_production_string_is_in_no_synthetic_header():
    """Ruling (о)'s whole point, counted on the shipped bytes rather than read off the producer.

    `prompts.NO_POST_TEXT` says «this post has no text of its own — it is an image or a video». That
    is TRUE of the real image posts the eval genuinely contains and FALSE of a synthetic row, and it
    used to mark 160 of 160 against 0 of 506 — a perfect separator built out of a sentence about
    something else. Both sides are counted: the fix is worth nothing if it merely moved the string.
    """
    assert sum(prompts.NO_POST_TEXT in one["prompt"] for one in SYNTHETIC) == 0
    assert sum(prompts.NO_POST_TEXT in one["prompt"] for one in REAL) == 0

    fix = PREREG["population"]["train"]["the_marker_fix"]
    assert fix["the_false_string_it_replaces"]["value"] == prompts.NO_POST_TEXT
    assert fix["the_false_string_it_replaces"]["in_the_160"] == 0
    assert fix["the_false_string_it_replaces"]["was_before_the_fix"]["in_the_160"] == 160


def test_the_registered_constant_marks_all_160_and_none_of_the_506():
    """The confound that REMAINS, published as its counts.

    A synthetic row has no post; every honest topic line saying so is a line none of the 506
    renders. The fix moves the marker onto a string production never emits — it does not remove it,
    and the record says the number rather than the reassurance
    ([[a_default_is_a_marker_when_nothing_takes_it]]).
    """
    line = data.SYNTHETIC_NO_POST
    assert line != prompts.NO_POST_TEXT
    assert sum(line in one["prompt"] for one in SYNTHETIC) == 160
    assert sum(line in one["prompt"] for one in REAL) == 0

    fix = PREREG["population"]["train"]["the_marker_fix"]
    assert fix["constant"]["value"] == line
    assert fix["the_registered_string"] == {"in_the_160": 160, "in_the_506": 0}
    assert fix["the_marker_that_remains"]["synthetic_rows_marked_by_at_least_one_tell"] == 160
    assert line in fix["the_marker_that_remains"]["tells"]


def test_the_tell_table_is_re_derived_from_the_shipped_prompts():
    """Every «0 of the 506» in the record, recounted here off the file the pod will train on."""
    tell = ARM_B["isolation"]["5_the_header_tell"]
    for cell in tell["header_lines_of_the_160"]:
        assert cell["synthetic_rows_carrying_it"] == sum(
            cell["line"] in one["prompt"] for one in SYNTHETIC
        )
        assert cell["real_rows_carrying_it"] == sum(cell["line"] in one["prompt"] for one in REAL)
    assert tell["tells"] == [
        cell["line"]
        for cell in tell["header_lines_of_the_160"]
        if cell["real_rows_carrying_it"] == 0
    ]


def test_the_tell_table_is_ordered_deterministically():
    """A record whose row order changes with PYTHONHASHSEED cannot be pinned by anything.

    `header_tell` fills its table from a `set`, and every prompt paragraph shares the sort cell
    (506, −160). Without the line itself as the third key the file differs on every run and the
    byte-for-byte producer test can never hold it — which is how it was found.
    """
    table = ARM_B["isolation"]["5_the_header_tell"]["header_lines_of_the_160"]
    assert table == sorted(
        table,
        key=lambda cell: (
            cell["real_rows_carrying_it"],
            -cell["synthetic_rows_carrying_it"],
            cell["line"],
        ),
    )


def test_the_506_prefix_did_not_move_with_the_marker_fix():
    """The ablation's one variable, on BYTES — arm A's shipped file against arm B's opening."""
    arm_a = (REPO_ROOT / "results" / "pass1_sft_v3_train.jsonl").read_bytes()
    arm_b = (REPO_ROOT / "results" / "pass1_sft_v3_arm_b.jsonl").read_bytes()
    assert arm_b.startswith(arm_a)
    assert arm_b[len(arm_a) :].decode("utf-8").count("\n") == 160


def test_every_row_still_encodes_and_the_widest_is_a_real_one():
    """The census re-taken after the re-render: 666 encoded, 0 refused, the ceiling untouched.

    The widest row matters as much as the count. The new topic line is SHORTER than the one it
    replaces, so nothing may have moved at the top — and it is checked rather than inferred: the
    widest row is still a REAL one, and it is the same real one the ceiling ruling was taken on.
    """
    assert CENSUS["rows"] == 666
    assert CENSUS["encoded"] == 666
    assert CENSUS["refused"] == []
    assert CENSUS["max_seq_len"] == 3072
    assert CENSUS["tokens"]["max"] == 2975
    assert CENSUS["headroom"] == 97
    widest = CENSUS["tokens"]["widest_row"]
    assert widest == "@tarilka_malyuka:746#83"
    assert any(one["id"] == widest for one in REAL), "the widest row is a real one, not a synthetic"
    assert CENSUS["sha256"] == PREREG["population"]["train"]["files"][1]["sha256"]


def test_the_registration_pins_the_re_rendered_file():
    """A re-render that did not reach the registration would train on bytes nobody registered."""
    import hashlib

    for one in PREREG["population"]["train"]["files"]:
        on_disk = hashlib.sha256((REPO_ROOT / one["file"]).read_bytes()).hexdigest()
        assert one["sha256"] == on_disk, one["file"]


# --- step 0.5: the widened whitelist -------------------------------------------------------------


def test_the_whitelist_carries_both_hook_outputs_and_not_hot_md():
    """Ruling (о) amendment 5, at the level of the constant the instrument actually reads."""
    assert "knowledge/index.md" in check_stamped.WHITELIST
    assert "knowledge/daily_logs/" in check_stamped.WHITELIST
    assert not any("hot.md" in one for one in check_stamped.WHITELIST)


# --- D2: the money -------------------------------------------------------------------------------


def test_the_ruled_card_has_a_price_column():
    """Ruling (о) names RTX PRO 4500 at $0.72/h and the derivation had no column for it.

    Every projection rung divides by a price. A create at a price the plan was never derived at
    would leave every rung after it computing against a number nobody registered
    ([[a_rate_is_a_property_of_the_pod]]).
    """
    at = PREREG["money"]["pre_pod_arithmetic"]["at_each_price"]
    assert "0.72" in at
    cell = at["0.72"]
    fixed = PREREG["money"]["pre_pod_arithmetic"]["fixed_seconds"]["total"]
    cap = PREREG["money"]["cap_usd_all_in"]
    assert cell["budget_seconds"] == pytest.approx(cap / 0.72 * 3600, abs=0.1)
    assert cell["left_for_training_seconds"] == pytest.approx(
        cell["budget_seconds"] - fixed, abs=0.1
    )
    assert cell["break_even_seconds_per_step"] == pytest.approx(
        cell["left_for_training_seconds"] / 144, abs=0.01
    )
    assert set(PREREG["money"]["pre_pod_arithmetic"]["readings_under_the_break_even"]["0.72"]) == {
        "registered_by_lora_b",
        "measured_on_lora_b_arm_a",
    }


def test_the_marker_census_is_charged_where_it_actually_falls():
    """The contract says «inside the fixed part» and the fixed part has no room for it.

    8 885.88 s decomposes exactly into boot + load + two base legs + pass 2 + smoke + two adapter
    evals. 40 more calls are not inside that sum, so they are charged BESIDE it with what they cost
    the decision published per price — a new leg joining the denominator moves the knife-edge even
    when the rule does not move ([[a_new_leg_joins_the_gates_denominator]]).
    """
    arithmetic = PREREG["money"]["pre_pod_arithmetic"]
    fixed = arithmetic["fixed_seconds"]
    assert fixed["total"] == pytest.approx(
        sum(value for key, value in fixed.items() if key != "total"), abs=0.01
    )
    census = arithmetic["the_marker_census_is_not_inside_the_fixed_part"]
    assert census["seconds"] == pytest.approx(
        20 * 2 * arithmetic["rates_used"]["pass_1_seconds_per_call"], abs=0.01
    )
    for price, cell in arithmetic["at_each_price"].items():
        with_it = census["break_even_seconds_per_step_with_it_charged"][price]
        assert with_it < cell["break_even_seconds_per_step"], price
        assert with_it == pytest.approx(
            (cell["left_for_training_seconds"] - census["seconds"]) / 144, abs=0.01
        )
    # the finding: at the WORST price a create is allowed at, the margin is under one second a step
    worst = census["break_even_seconds_per_step_with_it_charged"]["0.80"]
    registered = arithmetic["readings_this_repo_holds"]["registered_by_lora_b"]
    assert 0 < worst - registered < 1


def test_the_hard_stop_is_the_worst_price_and_not_the_ruled_one():
    """A backstop that assumes the good case is not a backstop."""
    arithmetic = PREREG["money"]["pre_pod_arithmetic"]
    cap = PREREG["money"]["cap_usd_all_in"]
    assert arithmetic["hard_stop_seconds"] == pytest.approx(cap / 0.80 * 3600, abs=0.1)
    assert arithmetic["hard_stop_seconds"] < cap / 0.72 * 3600


def test_the_trainer_unreachability_reads_closed_by_sibling():
    """Ruling (о) amendment 5: the block STAYS and its state moves — and the sibling is on disk."""
    block = PREREG["reachability"]["the_pinned_trainer_refuses_a_v3_dataset"]
    assert block["state"] == "CLOSED-BY-SIBLING"
    assert block["refusals_driven_at_zero_dollars"], "the refusals that made it real are still here"
    closer = block["the_sibling_that_closes_it"]
    path = REPO_ROOT / closer["path"]
    assert path.exists()
    assert closer["sha256"] == data.sha_text(path.read_text(encoding="utf-8"))
    assert block["sha256"] == data.sha_text(
        (REPO_ROOT / "scripts" / "train_qlora.py").read_text(encoding="utf-8")
    ), "the PINNED trainer did not move"
