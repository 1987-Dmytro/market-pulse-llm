"""Offline tests for the 5c1 volume calculation — no network, no spend.

The brief's rule for this deliverable is "every input names its source artifact — no hand-typed
numbers". That promise is only worth something if breaking it fails, so what is tested here is
the guard, the decomposition (never one blended number), and the arithmetic behind the row the
recommendation picks.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import volume_calc_5c1 as calc  # noqa: E402


def test_every_input_names_an_artifact_that_exists():
    for key, entry in calc.inputs().items():
        assert entry["source"], key
        artifact = entry["source"].split(" ::")[0].split(" §")[0].split(" (")[0]
        artifact = artifact.split(",")[0].strip()
        assert (REPO_ROOT / artifact).exists(), f"{key} names {artifact}, which is not there"


def test_a_number_whose_artifact_stopped_carrying_it_stops_the_run(tmp_path):
    """The guard that makes "no hand-typed numbers" true rather than aspirational: a runbook
    edited to say something else must break the calculation, not be silently outvoted by it."""
    artifact = tmp_path / "runbook.md"
    artifact.write_text("the download took ~4 min\n", encoding="utf-8")
    assert calc.quoted(artifact, "~4 min", 4.0) == 4.0
    with pytest.raises(SystemExit, match="is not in the file"):
        calc.quoted(artifact, "~9 min", 9.0)


def test_the_json_inputs_are_read_by_key_and_not_typed():
    numbers = calc.inputs()
    assert numbers["usd_per_hour"]["value"] == calc.read_json(calc.SERVING, "adopted.usd_per_hour")
    assert numbers["cold_start_local_s"]["value"] == calc.read_json(
        calc.SERVING, "adopted.cold_start_seconds"
    )


def test_every_option_is_decomposed_and_carries_its_risk():
    """ "never one blended number without its parts" — the storage and boot terms must add up to
    the total on every row, and no row may ship without the risk that goes with it."""
    for row in calc.options(calc.inputs()):
        assert row["risk"] and row["storage_basis"] and row["boot_basis"]
        assert round(row["storage_usd_per_month"] + row["boot_usd_per_month"], 4) == round(
            row["total_usd_per_month"], 4
        )


def test_the_boot_term_is_the_cold_start_times_the_cadence_times_the_rate():
    numbers = calc.inputs()
    rate, passes = numbers["usd_per_hour"]["value"], calc.PASSES_PER_DAY * calc.DAYS
    rows = {row["option"]: row for row in calc.options(numbers)}

    volume = numbers["cold_start_volume_s"]["value"]
    assert rows["a"]["boot_seconds_per_pass"] == volume
    assert rows["a"]["boot_usd_per_month"] == round(volume * passes / 3600 * rate, 4)

    # (b) is the faster cold start PLUS the download that buys it — the point of the row.
    local = numbers["cold_start_local_s"]["value"]
    assert rows["b"]["boot_seconds_per_pass"] == round(
        local + numbers["stage_minutes"]["value"] * 60, 3
    )
    assert rows["b"]["boot_seconds_per_pass"] > rows["a"]["boot_seconds_per_pass"]
    assert rows["c"]["boot_seconds_per_pass"] == local


def test_deleting_the_volume_is_the_only_row_with_no_storage_bill():
    rows = {row["option"]: row for row in calc.options(calc.inputs())}
    assert rows["b"]["storage_usd_per_month"] == 0.0
    assert rows["a"]["storage_usd_per_month"] == rows["c"]["storage_usd_per_month"] > 0


def test_the_stopped_pod_row_says_resume_is_not_guaranteed():
    """The capacity clause pins the GPU class, never one pod. A row that priced (c) without that
    sentence would read as the cheap fast option it is not."""
    row = next(r for r in calc.options(calc.inputs()) if r["option"] == "c")
    assert "resume is NOT guaranteed" in row["risk"]


def test_the_idle_rate_is_reported_as_a_bound_not_as_an_estimate():
    """Every interval between two spend sessions contains whatever ran inside it, so the balance
    deltas cannot isolate the volume — they can only cap it."""
    bound = calc.idle_rate_bound()
    assert "upper bound" in bound["reading"]
    assert bound["quietest_interval"]["usd_per_day"] > calc.inputs()["volume_usd_per_day"]["value"]


def test_the_compute_term_is_kept_out_of_the_rows_it_would_not_decide():
    """It is identical in all three options and its size is an assumption (test v4's row count).
    Inside the rows it would swamp the difference the operator is actually deciding."""
    totals = [row["total_usd_per_month"] for row in calc.options(calc.inputs())]
    per_pass = calc.inputs()["usd_per_pass"]["value"] * calc.PASSES_PER_DAY * calc.DAYS
    assert all(total < per_pass for total in totals)


def test_the_recommendation_names_a_row_and_leaves_the_decision_open():
    text = calc.recommendation(calc.options(calc.inputs()))
    assert text.startswith("RECOMMENDATION: (b)")
    assert "DECISION is the operator's" in text
