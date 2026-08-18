"""pass1-probe-b's transport — every command that READS the registration, driven at $0.

The rule this file exists for is Dv486, promoted from a lesson to a deliverable: **a registered
field no shipped command can read is a red gate here, at $0, and not on a live pod.** pass1-probe
registered `boot_kill_rule`, `read_threads_reader_v4.deadlines` reads `boot_deadline_rule`, and the
`KeyError` fired with a meter running on a record that could no longer be edited.

`--gate` is driven TWICE on purpose. It routes to the boot deadline when no reply has landed and to
the full-pass projection when one has, and those are different sets of record reads — driving only
the empty case would send the projection branch to the pod unexercised
([[a_guard_on_one_path_is_not_a_guard]]).

Nothing here creates anything: the run record, the raw jsonl and the step ledger are all redirected
into `tmp_path`, so the commands are exercised against synthetic state and the real
`results/pass1_probe_b_run.json` is never touched.
"""

import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import read_pass1_probe as p1  # noqa: E402
import read_pass1_probe_b as driver  # noqa: E402

PACK = json.loads((REPO_ROOT / "results" / "pass1_probe_b_pack.json").read_text("utf-8"))
RECORD = json.loads((REPO_ROOT / "results" / "prereg_pass1_probe_b.json").read_text("utf-8"))


@pytest.fixture
def synthetic(tmp_path, monkeypatch):
    """The b-driver pointed at throwaway state, and a ledger that exists."""
    ledger = tmp_path / "spend.json"
    ledger.write_text(json.dumps({"runpod_balance_at_pass1-probe-b_start": 20.0}), "utf-8")
    monkeypatch.setattr(driver, "RECORD", tmp_path / "run.json")
    monkeypatch.setattr(driver, "RAW", tmp_path / "pod.jsonl")
    monkeypatch.setattr(driver, "LEDGER", ledger)
    return tmp_path


def open_a_segment(capsys=None, seconds_ago: float = 10.0) -> str:
    """`--open`, with its own two printed objects DRAINED.

    `capsys` accumulates, so a later assertion that parses «the output» would parse this command's
    segment and gate as well as the one under test.
    """
    created = datetime.now(UTC) - timedelta(seconds=seconds_ago)
    stamp = created.isoformat(timespec="seconds").replace("+00:00", "Z")
    assert (
        driver.main(
            [
                "--open",
                "--pod-id",
                "SYNTHETIC",
                "--created-at",
                stamp,
                "--usd-per-hour",
                "0.74",
                "--card",
                "NVIDIA GeForce RTX 4090",
            ]
        )
        == 0
    )
    if capsys is not None:
        capsys.readouterr()
    return stamp


def test_the_driver_points_at_the_b_attempts_files_and_puts_pass_1s_back():
    """A module left pointing at another attempt's files is the bug that only shows up in the second
    command — which on this transport is the one with a meter running."""
    was = {name: getattr(p1, name) for name in driver.SWAPPED}
    with driver.as_probe_b():
        assert p1.PHASE == "pass1-probe-b"
        assert p1.PREREG.name == "prereg_pass1_probe_b.json"
        assert p1.PACK.name == "pass1_probe_b_pack.json"
        assert p1.RECORD.name == "pass1_probe_b_run.json"
        assert p1.producer is driver.producer
    assert {name: getattr(p1, name) for name in driver.SWAPPED} == was


def test_the_swap_refuses_to_replace_a_name_that_no_longer_exists():
    was = p1.PACK
    try:
        del p1.PACK
        with pytest.raises(SystemExit, match="has no `PACK` any more"):
            with driver.as_probe_b():
                pass
    finally:
        p1.PACK = was


def test_the_committed_pack_rebuilds_byte_for_byte_through_the_b_producer(capsys):
    """`check_pack` rebuilds through `producer.build_pack`, so this also proves the producer swap is
    load-bearing: pass1-probe's producer would name the wrong registration and refuse."""
    assert driver.main(["--pack"]) == 0
    said = json.loads(capsys.readouterr().out)
    assert said == {
        "pack": "results/pass1_probe_b_pack.json",
        "units": 64,
        "gold": 14,
        "census": 50,
        "rebuilds_byte_for_byte": True,
    }


def test_pre_create_check_answers_before_anything_exists(synthetic, capsys):
    assert driver.main(["--pre-create-check"]) == 0
    said = json.loads(capsys.readouterr().out)
    assert said["may_create"] is True
    assert said["segment"] == 0 and said["segments_allowed"] == 3
    assert said["cap_usd_all_in"] == 0.20 and said["cap_left_for_this_segment_usd"] == 0.20


def test_open_records_the_segment_prices_it_against_the_registered_meter_and_gates_zero(synthetic):
    """The segment is read back off the record rather than off the print: what the next command
    reads is the FILE, and a stdout that agrees with a file nobody wrote proves nothing."""
    open_a_segment()
    state = json.loads((synthetic / "run.json").read_text("utf-8"))
    segment = state["segments"][-1]
    assert segment["segment"] == 1 and segment["pod_id"] == "SYNTHETIC"
    assert segment["card_registered"] == RECORD["money"]["meter"]["card_requested"]
    assert segment["usd_per_hour_worked_example"] == 0.74
    assert segment["priced_at_or_under_the_example"] is True
    assert segment["deleted_at"] is None and segment["billed_seconds"] is None
    assert state["gates"][-1]["kind"] == "open"
    assert state["gates"][-1]["threshold_seconds"] == 180.0
    assert state["gates"][-1]["verdict"] == "WAIT"


def test_a_second_open_is_REFUSED_because_two_meters_never_run_at_once(synthetic):
    open_a_segment()
    with pytest.raises(SystemExit, match="Never two pods at once"):
        open_a_segment()


def test_gate_zero_GOes_the_moment_the_endpoint_answers(synthetic, capsys):
    open_a_segment(capsys, seconds_ago=400.0)
    assert driver.main(["--gate0", "--ssh-ok"]) == 0
    gate = json.loads(capsys.readouterr().out.split("VERDICT")[0])
    assert gate["verdict"] == "GO" and gate["ssh_endpoint_answered"] is True
    assert gate["recreates_left"] == 2


def test_deadlines_READS_the_registered_rule_that_pass1_probes_record_did_not_carry(
    synthetic, capsys
):
    """The regression, at the command line. This raised `KeyError: 'boot_deadline_rule'` on a pod
    that was billing at the time ([[a_frozen_record_is_an_input_to_shipped_code]])."""
    open_a_segment(capsys)
    assert driver.main(["--deadlines"]) == 0
    gate = json.loads(capsys.readouterr().out)
    assert gate["rule"] == RECORD["money"]["arithmetic"]["boot_deadline_rule"]
    assert gate["contract_ceiling_seconds"] == 420.0
    assert gate["usable_seconds"] == 913.0
    assert gate["reading_projection_seconds"] == 409.728
    assert gate["affordability_deadline_as_create_elapsed"] == 503.2
    assert gate["verdict"] == "WAIT"


def test_gate_with_no_reply_yet_takes_the_boot_deadline_branch(synthetic, capsys):
    open_a_segment(capsys)
    assert driver.main(["--gate"]) == 3
    said = capsys.readouterr().out
    gate = json.loads(said.split("VERDICT")[0])
    assert gate["rule"] == RECORD["money"]["arithmetic"]["boot_deadline_rule"]
    assert gate["read_from"]["exists"] is False
    assert "VERDICT WAIT" in said


def test_gate_with_replies_takes_the_PROJECTION_branch_and_it_is_a_different_set_of_reads(
    synthetic, capsys
):
    """The branch a single `--gate` drive never reaches. It reads the pack's payable counts, the
    cap left for the segment and the usable seconds — none of which the deadline branch touches."""
    open_a_segment(capsys)
    (synthetic / "pod.jsonl").write_text(
        "".join(
            json.dumps(
                {
                    "id": item["id"],
                    "reply": "{}",
                    "balanced": True,
                    "finish_reason": "stop",
                    "usage": {"prompt_tokens": 900, "completion_tokens": 40},
                    "seconds": 3.0,
                    "emitted_chars": 95,
                }
            )
            + "\n"
            for item in PACK["items"][:2]
        ),
        "utf-8",
    )
    assert driver.main(["--gate"]) == 0
    gate = json.loads(capsys.readouterr().out.split("VERDICT")[0])
    assert gate["units_read"] == 2 and gate["units_unread"] == 62
    assert gate["measured_seconds_per_unit"] == 3.0
    assert gate["usable_seconds"] == 913.0
    assert gate["projections"]["binding"]["which"] == "by_unit"
    assert gate["projections"]["by_unit"] == gate["projections"]["by_payable_comment"], (
        "every pass-1 unit carries exactly one payable comment, so the two legs are one number"
    )
    assert gate["usd"]["cap_usd_all_in"] == 0.20
    assert gate["verdict"] == "GO"


def test_the_gate_snapshots_APPEND_and_carry_their_segment(synthetic):
    open_a_segment()
    driver.main(["--gate0", "--ssh-ok"])
    driver.main(["--deadlines"])
    state = json.loads((synthetic / "run.json").read_text("utf-8"))
    assert [one["kind"] for one in state["gates"]] == ["open", "gate0", "boot_kill"]
    assert {one["segment"] for one in state["gates"]} == {1}
    assert {one["pod_id"] for one in state["gates"]} == {"SYNTHETIC"}
