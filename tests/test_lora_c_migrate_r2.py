"""The r2 migration's rungs, DRIVEN — every outcome, at $0 and with no pod and no volume.

`results/prereg_lora_c_migrate_r2.json` is hand-written, like the vramprobe's, and this file is
what stops it drifting. Four jobs:

* **every registered number is greppable back into `docs/PROMPT-lora-c-migrate-r2.md`** — the
  contract is where they came from ([[preregistration_is_a_file_not_a_constant]]);
* **the money arithmetic is RE-DERIVED, not read back.** The contract says «derived not asserted»,
  so the stage sum is recomputed from the rungs and the affordable window from the cap and the
  price; the registration's own summary of both has to agree with the recomputation;
* **every rung fires both ways**, including the two branches that only exist to refuse:
  the affordability inequality, driven on a synthetic pair because at THIS cap it coincides with
  rung 0's ceiling and can never fail ([[guard_selftest_negative_control]]);
* **the frozen registration is untouched** and the two ruff-format-drifted files are still pinned.
"""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_lora_c as parent  # noqa: E402
import gate_lora_c_migrate_r2 as gate  # noqa: E402
import load_proof_pod_runner as proof_runner  # noqa: E402

PREREG = json.loads((REPO_ROOT / "results" / "prereg_lora_c_migrate_r2.json").read_text("utf-8"))
CONTRACT = " ".join((REPO_ROOT / "docs" / "PROMPT-lora-c-migrate-r2.md").read_text("utf-8").split())
"""Whitespace-normalised — the contract wraps its clauses wherever the line ran out, and a raw grep
for a quotation the source wrapped finds nothing and reads as «absent»
([[verbatim_quotes_must_be_grepped]])."""

CREATE = "2026-08-25T20:00:00+00:00"
PRICE = 1.39
FLOOR = 55 * 1024**3


def at(seconds: float, created: str = CREATE) -> datetime:
    return gate.stamp(created) + timedelta(seconds=seconds)


def a_pod(created: str = CREATE, usd_per_hour: float = PRICE) -> dict:
    return {
        "pods": [{"pod_id": "mp-mig-r2-1", "created_at": created, "usd_per_hour": usd_per_hour}]
    }


def view() -> dict:
    return parent.as_the_sibling_reads_it(PREREG)


@pytest.fixture
def run(tmp_path, monkeypatch):
    """This step's record redirected into `tmp_path`, the registration handed over directly.

    `gate.RECORD` and not `parent.RECORD`: the contextmanager copies THIS module's globals into the
    parent's on every call, so patching the parent's would be undone a microsecond later and the
    test would write into `results/`.
    """
    monkeypatch.setattr(gate, "RECORD", tmp_path / "lora_c_migrate_r2.json")
    monkeypatch.setattr(parent, "registration", lambda: view())
    return gate


def rung(number: int) -> dict:
    return gate.rung(PREREG, number)


# --- the contract's numbers are the registration's ------------------------------------------------


@pytest.mark.parametrize(
    "quote",
    [
        "cap $1.50",
        "datacenter `CA-MTL-3`",
        "volume 100 GB there",
        "card **`A100 PCIe`** by displayName",
        "at $1.39/h the affordable hard stop is `1.50/1.39×3600 = 3 884 s`",
        "registered hard stop **3 600 s**",
        "boot 500 + download **1 200**",
        "venv build 900 — a NEW rung",
        "load proof 600 + teardown margin 90 = **3 290 ≤ 3 600**",
        "growth of `du -sb /workspace/hf` between stamped polls",
        "(≤120 s apart)",
        "zero growth starts the 600 s liveness clock",
        "The liveness deadline is its own registered FIELD",
        "the pinned revision `842da379…`",
        "Registration `results/prereg_lora_c_migrate_r2.json`",
        "Report `docs/reports/lora-c-migrate-r2.md`",
    ],
)
def test_the_contract_says_what_this_registration_registers(quote):
    """Each number below is quoted from the contract, not remembered from it."""
    assert quote in CONTRACT, quote


def test_every_registered_threshold_matches_the_contract():
    assert PREREG["money"]["cap_usd_all_in"] == 1.50
    assert PREREG["money"]["pre_pod_arithmetic"]["hard_stop_seconds"] == 3600.0
    assert rung(0)["threshold"] == 1.50
    assert rung(1)["threshold"] == 500.0
    assert rung(2)["threshold"] == 600.0
    assert rung(3)["threshold"] == 900.0
    assert rung(4)["threshold"] == 1200.0
    assert rung(4)["poll_cadence_seconds"] == 120.0
    assert rung(5)["threshold"] == 600.0
    assert rung(6)["threshold"] == 3600.0
    assert PREREG["target"]["datacenter"] == "CA-MTL-3"
    assert PREREG["target"]["card"] == "A100 PCIe"
    assert PREREG["target"]["volume_gb"] == 100
    assert PREREG["target"]["revision"] == "842da3794eaa0b77d5f08bae87a17459d91ff475"


def test_the_liveness_deadline_has_exactly_one_home():
    """Rung 4 carries the CADENCE and reads the silence deadline out of rung 2.

    The contract asks for the liveness deadline as its own registered FIELD rather than the second
    number of a prose rule. It is rung 2's `threshold`, and rung 4 must not hold a second copy of
    it — a threshold with two homes acquires two values
    ([[two_values_for_one_input_get_quoted_kindly]]).
    """
    assert gate.first_number(rung(2)["rule"]) == rung(2)["threshold"] == 600.0
    assert not [key for key, value in rung(4).items() if value == 600.0]
    assert "600" not in rung(4)["rule"]


# --- Dv825: first_number reads a PRICE, not a model number ----------------------------------------


def test_first_number_reads_the_price_out_of_the_registered_rule():
    """The byte-identical string, not a paraphrase of it ([[a_threshold_that_lives_in_prose]])."""
    assert gate.first_number(rung(0)["rule"]) == 1.50


def test_a_card_first_wording_would_have_fed_it_the_model_number():
    """Dv825, reproduced. This is why rung 0's rule is worded price-first."""
    assert gate.first_number("card A100 PCIe at ≤$1.50/h") == 100.0
    assert gate.first_number("card RTX A6000 at ≤$0.60/h") == 6000.0


# --- the money, RE-DERIVED ------------------------------------------------------------------------


def test_the_stage_bounds_are_recomputed_from_the_rungs_and_fit():
    got = gate.the_stage_bounds_sum_inside_the_hard_stop(PREREG)
    assert got["stage_thresholds_by_rung"] == {1: 500.0, 3: 900.0, 4: 1200.0, 5: 600.0}
    assert got["summed_seconds"] == 3290.0
    assert got["headroom_seconds"] == 310.0
    assert got["the_registrations_own_summary_agrees"]
    assert got["verdict"] == "GO"


def test_the_stage_sum_refuses_a_plan_that_crosses_its_own_stop():
    """The previous contract's own arithmetic: boot 500 + download 2 400 + load 600 = 3 500 of
    3 600, with the venv, the mount, the bundle, the packs and the teardown unnamed (Dv822)."""
    broken = json.loads(json.dumps(PREREG))
    for one in broken["kill_clock"]:
        if one["rung"] == 4:
            one["threshold"] = 2400.0
    got = gate.the_stage_bounds_sum_inside_the_hard_stop(broken)
    assert got["summed_seconds"] == 4490.0
    assert got["verdict"] == "KILL"
    assert not got["the_registrations_own_summary_agrees"]


def test_the_cap_affords_the_hard_stop_at_the_registered_price():
    got = gate.the_cap_affords_the_hard_stop(PREREG, PRICE)
    assert got["what_the_cap_buys_seconds"] == 3884.9
    assert got["slack_seconds"] == 284.9
    assert got["the_full_stop_would_cost_usd"] == 1.39
    assert got["cap_left_if_the_stop_is_reached_usd"] == 0.11


def test_the_inequality_refuses_a_stop_the_cap_cannot_pay_for():
    """It cannot fail at THIS cap — `cap / stop × 3600` is $1.50, which IS rung 0's ceiling — so the
    refusing branch is driven on a synthetic pair. A guard whose failing branch has never run is a
    guard nobody has seen work ([[guard_selftest_negative_control]])."""
    tighter = json.loads(json.dumps(PREREG))
    tighter["money"]["cap_usd_all_in"] = 1.00
    with pytest.raises(SystemExit) as err:
        gate.the_cap_affords_the_hard_stop(tighter, PRICE)
    assert "2589.9 s" in str(err.value)
    assert "1010.1 s more than the cap can pay for" in str(err.value)


def test_the_inequality_and_rung_0_coincide_at_this_cap():
    """Stated in the record, and checked here: the break-even price is the rung-0 ceiling."""
    cap = PREREG["money"]["cap_usd_all_in"]
    stop = PREREG["money"]["pre_pod_arithmetic"]["hard_stop_seconds"]
    assert cap / stop * 3600.0 == rung(0)["threshold"] == 1.50


# --- rung 0 ---------------------------------------------------------------------------------------


def test_rung_0_admits_the_ruling_s_card_at_the_read_price():
    got = parent.price_gate(PREREG, PRICE, "A100 PCIe")
    assert got["verdict"] == "GO"
    assert got["price_ceiling_usd_per_hour"] == 1.50


@pytest.mark.parametrize(
    "usd,card,why",
    [
        (PRICE, "RTX PRO 6000", "a different card at the authorised price"),
        (PRICE, "NVIDIA A100-SXM4-80GB", "the SXM sibling, whose gpu_id is not the registered one"),
        (1.09, "A100 PCIe", "a CHEAPER price the plan holds no column for"),
        (1.59, "A100 PCIe", "over the ceiling"),
    ],
)
def test_rung_0_refuses_everything_the_plan_was_not_solved_at(usd, card, why):
    assert parent.price_gate(PREREG, usd, card)["verdict"] == "KILL", why


def test_rung_0_accepts_the_platform_s_own_gpu_id_as_well_as_the_display_name():
    assert parent.price_gate(PREREG, PRICE, "NVIDIA A100 80GB PCIe")["verdict"] == "GO"


# --- rung 3, the venv -----------------------------------------------------------------------------


STACK = "2.8.0 5.5.1 0.45.0 NVIDIA A100 80GB PCIe"


def test_the_venv_rung_waits_while_pip_is_still_running(run, tmp_path):
    got = gate.venv_gate(view(), a_pod(), CREATE, None, None, at(300))
    assert got["verdict"] == "WAIT"
    assert got["seconds_left"] == 600.0


def test_the_venv_rung_needs_the_venv_s_own_interpreter_to_speak(run, tmp_path):
    """«the caller said it finished» is not a reading
    ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]])."""
    got = gate.venv_gate(view(), a_pod(), CREATE, at(400).isoformat(), None, at(410))
    assert got["verdict"] == "WAIT"
    assert got["proof_exists"] is False


def test_the_venv_rung_goes_on_a_proof_that_names_the_authorised_card(run, tmp_path):
    written = tmp_path / "venv.txt"
    written.write_text(STACK + "\n", encoding="utf-8")
    got = gate.venv_gate(view(), a_pod(), CREATE, at(400).isoformat(), written, at(410))
    assert got["verdict"] == "GO"
    assert got["measured_seconds"] == 400.0
    assert got["the_card_the_venv_sees"] == ["A100 PCIe"]


def test_the_venv_rung_kills_when_the_pod_reports_a_different_card(run, tmp_path):
    """The venv's proof cross-checks rung 0 from INSIDE the pod: `costPerHr` and the card the
    driver actually enumerates are two readings ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]])."""
    written = tmp_path / "venv.txt"
    written.write_text("2.8.0 5.5.1 0.45.0 NVIDIA GeForce RTX 4090\n", encoding="utf-8")
    got = gate.venv_gate(view(), a_pod(), CREATE, at(400).isoformat(), written, at(410))
    assert got["verdict"] == "KILL"
    assert got["the_card_the_venv_sees"] == []


def test_the_venv_rung_kills_at_its_deadline(run, tmp_path):
    got = gate.venv_gate(view(), a_pod(), CREATE, None, None, at(900))
    assert got["verdict"] == "KILL"
    assert got["seconds_left"] == 0.0


def test_the_venv_measurement_is_told_to_land_outside_the_registration(run, tmp_path):
    """§2 says «record the measured seconds in the registration for every future plan», and the
    registration is committed before the create and frozen by it. The gate says where the number
    actually goes rather than writing it back into a frozen record."""
    written = tmp_path / "venv.txt"
    written.write_text(STACK + "\n", encoding="utf-8")
    got = gate.venv_gate(view(), a_pod(), CREATE, at(400).isoformat(), written, at(410))
    assert (
        "results/lora_c_migrate_r2.json"
        in got["this_measurement_lands_in_the_run_record_not_the_registration"]
    )


# --- rung 4, the download, on BYTES ---------------------------------------------------------------


def polls(tmp_path, rows: list[tuple[float, int]]) -> Path:
    written = tmp_path / "bytes.jsonl"
    written.write_text(
        "".join(
            json.dumps({"at": at(seconds).isoformat(), "bytes": count}) + "\n"
            for seconds, count in rows
        ),
        encoding="utf-8",
    )
    return written


def test_the_download_waits_while_the_bytes_grow(run, tmp_path):
    got = gate.download_gate(
        view(), a_pod(), CREATE, polls(tmp_path, [(100, 10**9), (200, 9 * 10**9)]), at(210)
    )
    assert got["verdict"] == "WAIT"
    assert got["quiet_seconds"] == 10.0
    assert got["bytes_grew_by"] == 8 * 10**9


def test_the_download_is_complete_at_the_registered_byte_floor(run, tmp_path):
    got = gate.download_gate(
        view(), a_pod(), CREATE, polls(tmp_path, [(100, 10**9), (400, FLOOR)]), at(410)
    )
    assert got["verdict"] == "GO"
    assert got["complete_at_bytes"] == FLOOR
    assert got["fraction_of_the_floor"] == 1.0


def test_the_download_kills_on_silence_measured_in_bytes(run, tmp_path):
    """Progress lines keep printing through a stalled transfer; a byte count does not
    ([[no_rung_watches_an_idle_pod]])."""
    rows = [(100, 10**9)] + [(100 + 120 * one, 5 * 10**9) for one in range(1, 7)]
    got = gate.download_gate(view(), a_pod(), CREATE, polls(tmp_path, rows), at(830))
    assert got["verdict"] == "KILL"
    assert got["what_fired"] == "rung 2's silence clock — no byte growth"
    assert got["quiet_seconds"] == 610.0


def test_the_download_kills_at_its_own_deadline_even_while_growing(run, tmp_path):
    rows = [(120 * one, one * 10**9) for one in range(1, 11)]
    got = gate.download_gate(view(), a_pod(), CREATE, polls(tmp_path, rows), at(1200))
    assert got["verdict"] == "KILL"
    assert got["what_fired"] == "the 1200 s download deadline"


def test_the_first_poll_is_a_baseline_and_is_never_graded_for_growth(run, tmp_path):
    """It has no predecessor. The silence clock runs from the download's own start until a second
    poll exists."""
    got = gate.download_gate(view(), a_pod(), CREATE, polls(tmp_path, [(60, 10**9)]), at(70))
    assert got["verdict"] == "WAIT"
    assert got["last_growth_at"] == at(60).isoformat(timespec="seconds")
    assert got["bytes_grew_by"] is None


def test_a_gap_longer_than_the_cadence_is_listed_and_does_not_fire_a_rung(run, tmp_path):
    """A stall inside an unpolled window that recovered is indistinguishable from a healthy
    transfer, so it cannot KILL — but it must be visible
    ([[a_checker_whose_failure_is_silence]])."""
    got = gate.download_gate(
        view(), a_pod(), CREATE, polls(tmp_path, [(100, 10**9), (400, 9 * 10**9)]), at(410)
    )
    assert got["verdict"] == "WAIT"
    assert got["the_reading_has_no_holes"] is False
    assert [one["seconds"] for one in got["blind_windows_over_the_cadence"]] == [300.0]


def test_a_reading_with_no_holes_says_so(run, tmp_path):
    got = gate.download_gate(
        view(), a_pod(), CREATE, polls(tmp_path, [(100, 10**9), (200, 9 * 10**9)]), at(210)
    )
    assert got["the_reading_has_no_holes"] is True
    assert got["blind_windows_over_the_cadence"] == []


def test_a_torn_last_poll_is_dropped_and_an_earlier_one_is_not(run, tmp_path):
    written = polls(tmp_path, [(100, 10**9), (200, 9 * 10**9)])
    written.write_text(written.read_text("utf-8") + '{"at": "2026-08', encoding="utf-8")
    assert len(gate.byte_polls(written)) == 2
    written.write_text('{"at": "2026-08\n' + written.read_text("utf-8"), encoding="utf-8")
    with pytest.raises(SystemExit):
        gate.byte_polls(written)


# --- rung 5, the load proof -----------------------------------------------------------------------


def a_proof(tmp_path, **over) -> Path:
    written = tmp_path / "load_proof.json"
    written.write_text(
        json.dumps(
            {
                "load_seconds": 177.3,
                "loaded": True,
                "revision": PREREG["target"]["revision"],
                "hf_bytes_before": 63_000_000_000,
                "hf_bytes_after": 63_000_000_000,
                "vram_bytes_allocated": 20 * 1024**3,
                "vram_bytes_reserved": 21 * 1024**3,
                "gpu": "NVIDIA A100 80GB PCIe",
                **over,
            }
        ),
        encoding="utf-8",
    )
    return written


def test_the_load_proof_goes_on_seconds_an_unmoved_volume_and_the_pinned_revision(run, tmp_path):
    got = gate.load_proof_gate(view(), a_pod(), CREATE, a_proof(tmp_path), at(200))
    assert got["verdict"] == "GO"
    assert got["load_seconds"] == 177.3
    assert got["vram_gb_allocated"] == 20.0
    assert got["the_volume_was_not_written_during_the_load"] is True


def test_the_load_proof_kills_when_the_volume_s_bytes_moved(run, tmp_path):
    """A load that quietly re-fetched a missing shard reads exactly like a successful one."""
    written = a_proof(tmp_path, hf_bytes_after=63_000_000_001)
    got = gate.load_proof_gate(view(), a_pod(), CREATE, written, at(200))
    assert got["verdict"] == "KILL"
    assert "MOVED" in got["what_failed"]


def test_the_load_proof_kills_on_an_unpinned_revision(run, tmp_path):
    got = gate.load_proof_gate(view(), a_pod(), CREATE, a_proof(tmp_path, revision="main"), at(200))
    assert got["verdict"] == "KILL"
    assert got["the_pinned_revision_loaded"] is False


def test_the_load_proof_kills_over_its_deadline(run, tmp_path):
    got = gate.load_proof_gate(
        view(), a_pod(), CREATE, a_proof(tmp_path, load_seconds=601.0), at(700)
    )
    assert got["verdict"] == "KILL"
    assert got["what_failed"] == "the load exceeded its deadline"


def test_the_load_proof_waits_while_the_file_is_not_there_and_kills_at_the_deadline(run, tmp_path):
    missing = tmp_path / "nothing.json"
    assert gate.load_proof_gate(view(), a_pod(), CREATE, missing, at(100))["verdict"] == "WAIT"
    assert gate.load_proof_gate(view(), a_pod(), CREATE, missing, at(600))["verdict"] == "KILL"


# --- the load-proof runner, driven with a stub ----------------------------------------------------


def test_the_runner_calls_the_shipped_loader_and_writes_what_the_gate_reads(tmp_path):
    """Driven as `main()`, not imported: an import proves the file parses
    ([[stub_driven_script_verification]]). The stub stands in for the 62 GB and the card, and
    everything around it — the two `du` readings, the record, the print — is the real path."""
    home = tmp_path / "hf"
    home.mkdir()
    seen = {}

    def loader(model_id, revision):
        seen["called"] = (model_id, revision)
        return object(), object()

    out = tmp_path / "run" / "load_proof.json"
    code = proof_runner.main(
        ["--revision", PREREG["target"]["revision"], "--hf-home", str(home), "--out", str(out)],
        loader=loader,
        du=lambda path, run=None: 63_000_000_000,
    )
    assert code == 0
    assert seen["called"] == ("google/gemma-4-31b-it", PREREG["target"]["revision"])
    written = json.loads(out.read_text("utf-8"))
    assert written["loaded"] is True
    assert written["hf_bytes_before"] == written["hf_bytes_after"] == 63_000_000_000
    assert written["load_seconds"] >= 0
    assert gate.load_proof_gate(view(), a_pod(), CREATE, out, at(200))["verdict"] == "GO"


def test_the_runner_refuses_a_volume_with_no_cache_rather_than_downloading_one(tmp_path):
    """This contract prices ONE download, on rung 4. A loader that falls back to fetching would
    spend the rung's budget invisibly ([[the_empty_row_is_the_answer]])."""
    with pytest.raises(SystemExit) as err:
        proof_runner.main(
            [
                "--revision",
                "abc",
                "--hf-home",
                str(tmp_path / "gone"),
                "--out",
                str(tmp_path / "o"),
            ],
            loader=lambda *a: (object(), object()),
            du=lambda path, run=None: None,
        )
    assert "does not price a download here" in str(err.value)


def test_the_runner_finds_the_snapshot_directory_of_the_pinned_revision(tmp_path):
    revision = PREREG["target"]["revision"]
    made = tmp_path / "hub" / "models--google--gemma-4-31b-it" / "snapshots" / revision
    made.mkdir(parents=True)
    assert proof_runner.snapshot_dir(str(tmp_path), "google/gemma-4-31b-it", revision) == str(made)
    assert proof_runner.snapshot_dir(str(tmp_path), "google/gemma-4-31b-it", "main") is None


# --- the DO-NOT list, made checkable --------------------------------------------------------------


def test_the_frozen_registration_is_the_sha_this_plan_was_built_against():
    got = hashlib.sha256((REPO_ROOT / "results" / "prereg_lora_c.json").read_bytes()).hexdigest()
    assert got == PREREG["this_is_not_the_registered_attempt"]["sha256"]
    assert gate.the_frozen_registration_is_unmoved(PREREG)["unmoved"] is True


def test_a_moved_frozen_registration_stops_the_gate(monkeypatch, tmp_path):
    """The first DO-NOT, made checkable rather than promised ([[a_claim_no_number_can_check]])."""
    decoy = tmp_path / "prereg_lora_c.json"
    decoy.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(gate, "FROZEN", decoy)
    with pytest.raises(SystemExit) as err:
        gate.the_frozen_registration_is_unmoved(PREREG)
    assert "first DO-NOT" in str(err.value)


@pytest.mark.parametrize(
    "script,record,field",
    [
        ("scripts/write_lora_c_prereg.py", "results/prereg_lora_c.json", "producer"),
        (
            "scripts/build_lora_c_marker_census.py",
            "results/lora_c_marker_census_pack.json",
            "producer",
        ),
    ],
)
def test_both_ruff_format_drifted_files_are_still_pinned_by_a_record(script, record, field):
    """`make fmt` stays forbidden repo-wide while these hold. `make check` runs `ruff check`, not
    `ruff format --check`, and sees neither ([[the_formatter_voids_a_frozen_producer_pin]])."""
    got = hashlib.sha256((REPO_ROOT / script).read_bytes()).hexdigest()
    assert got in (REPO_ROOT / record).read_text("utf-8"), (
        f"{script} is no longer pinned by {record}"
    )
    drifted = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", script],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert drifted.returncode != 0, f"{script} is no longer ruff-format-drifted — re-read the note"
