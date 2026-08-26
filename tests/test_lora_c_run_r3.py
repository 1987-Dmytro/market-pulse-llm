"""`lora-c-run r3`'s rungs, DRIVEN — every command and both refusal branches, at $0 and with no pod.

`results/prereg_lora_c_run_r3.json` is hand-written, like the migration's and the vramprobe's, and
this file is what stops it drifting. Five jobs:

* **every registered number is greppable back into `docs/PROMPT-lora-c-run-r3.md`** — the contract
  is where they came from ([[preregistration_is_a_file_not_a_constant]]);
* **the money arithmetic is RE-DERIVED, not read back**: the fixed part from its own addends, the
  break-even table from the cap and the rates, the affordability inequality from the price;
* **every rung fires both ways**, the four defects this gate exists to fix included — the blob
  invariant against a PLANTED blob growth, the smoke against a two-line loss log and against a
  trainer that halved its way out of an OOM;
* **the eval-leg rate rung charges the MEASURED s/step** once the smoke has bought one;
* **nothing pinned is touched**: the frozen registration, and the three files the SEALED
  `docs/reports/lora-c-migrate-r2.md` hashes.
"""

import hashlib
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_lora_c as parent  # noqa: E402
import gate_lora_c_run_r3 as gate  # noqa: E402
import load_proof_r3_pod_runner as proof_runner  # noqa: E402

PREREG = json.loads((REPO_ROOT / "results" / "prereg_lora_c_run_r3.json").read_text("utf-8"))
FROZEN = json.loads((REPO_ROOT / "results" / "prereg_lora_c.json").read_text("utf-8"))
CONTRACT = " ".join((REPO_ROOT / "docs" / "PROMPT-lora-c-run-r3.md").read_text("utf-8").split())
"""Whitespace-normalised — the contract wraps its clauses wherever the line ran out, and a raw grep
for a quotation the source wrapped finds nothing and reads as «absent»
([[verbatim_quotes_must_be_grepped]])."""

CREATE = "2026-08-26T12:00:00+00:00"
PRICE = 1.39
REVISION = "842da3794eaa0b77d5f08bae87a17459d91ff475"


def at(seconds: float, created: str = CREATE) -> datetime:
    return gate.stamp(created) + timedelta(seconds=seconds)


def a_pod(created: str = CREATE, usd_per_hour: float = PRICE) -> dict:
    return {"pods": [{"pod_id": "mp-r3-1", "created_at": created, "usd_per_hour": usd_per_hour}]}


def view() -> dict:
    return parent.as_the_sibling_reads_it(PREREG)


def rung(number: int) -> dict:
    return gate.rung(PREREG, number)


@pytest.fixture
def run(tmp_path, monkeypatch):
    """This session's record redirected into `tmp_path`, the registration handed over directly.

    `gate.RECORD` and not `parent.RECORD`: the contextmanager copies THIS module's globals into the
    parent's on every call, so patching the parent's would be undone a microsecond later and the
    test would write into `results/`.
    """
    monkeypatch.setattr(gate, "RECORD", tmp_path / "lora_c_run_r3.json")
    monkeypatch.setattr(parent, "registration", lambda: view())
    return gate


# --- the contract's numbers are the registration's ------------------------------------------------


@pytest.mark.parametrize(
    "quote",
    [
        "cap $7.00 all-in for this session's pod",
        "pass-1 v3 **9.20 s/call** (never 6.14; v2 leg is already bought)",
        "pass-2 **97 s/thread**",
        "at the **bound of 15 threads/leg**",
        "smoke ceiling 6 × 181.5 s",
        "`cap/price×3600 ≥ hard_stop`",
        "at $1.39/h the cap buys 18 129 s — register hard stop **18 000 s**",
        "0 price-first equality («≤$1.50/h, card `A100 PCIe`»)",
        "1 ssh ≤500 s",
        "2 liveness **600 s from the LAST log line or byte-growth poll, at every stage**",
        "3 realised-rate reading after every eval leg",
        "5 projection after smoke and after EVERY leg",
        "6 platform backstop at create",
        "7 never two billing resources",
        "ONE re-create after a proven deletion",
        "Rung 5's invariant becomes «no BLOB grows»",
        "negative control: a planted blob-growth must still KILL",
        "`log_every: 5` → expect TWO loss lines (steps 5, 6)",
        "the quotable rate is `provenance.json::run.seconds_per_step`",
        "print both, never average them",
        "Clone the fresh bundle OVER `/workspace/repo`",
        "Rebuild the venv ONLY if `pyproject.toml`'s dependency set moved (price known: 132 s)",
        "40 requests, 20 pairs differing in the header alone",
        "report-only, never a bar",
    ],
)
def test_the_contract_says_what_this_registration_registers(quote):
    """Each number below is quoted from the contract, not remembered from it."""
    assert quote in CONTRACT, quote


def test_every_registered_threshold_matches_the_contract():
    assert PREREG["money"]["cap_usd_all_in"] == 7.00
    assert PREREG["money"]["pre_pod_arithmetic"]["hard_stop_seconds"] == 18000.0
    assert rung(0)["threshold"] == 1.50
    assert rung(1)["threshold"] == 500.0
    assert rung(2)["threshold"] == 600.0
    assert rung(3)["threshold"] == 7.00
    assert rung(4)["threshold"] == 181.5
    assert rung(4)["steps"] == 6
    assert rung(5)["threshold"] == 7.00
    assert rung(6)["threshold"] == 18000.0
    assert rung(7)["threshold"] == 1.0
    assert PREREG["the_load_proof"]["threshold"] == 600.0
    assert PREREG["target"]["card"] == "A100 PCIe"
    assert PREREG["target"]["datacenter"] == "CA-MTL-3"
    assert PREREG["target"]["revision"] == REVISION


def test_every_rule_string_yields_its_own_threshold():
    """`first_number` reads the rule, and a card-first wording would hand it «100» (Dv825)."""
    for number in (0, 1, 2, 3, 4, 5, 6, 7):
        assert gate.first_number(rung(number)["rule"]) == rung(number)["threshold"], number
    assert gate.first_number(PREREG["the_load_proof"]["rule"]) == 600.0


def test_the_frozen_registration_is_the_one_this_record_was_built_against():
    path = REPO_ROOT / "results" / "prereg_lora_c.json"
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest() == PREREG["the_frozen_registration"]["sha256"]
    )
    assert gate.the_frozen_registration_is_unmoved(PREREG)["unmoved"] is True


def test_a_moved_frozen_registration_stops_the_session(tmp_path, monkeypatch):
    """The negative control: the sha assert has to be seen refusing ([[guard_selftest_negative_control]])."""
    moved = tmp_path / "prereg_lora_c.json"
    moved.write_text(json.dumps(FROZEN) + "\n", encoding="utf-8")
    monkeypatch.setattr(gate, "FROZEN", moved)
    with pytest.raises(SystemExit, match="first DO-NOT"):
        gate.the_frozen_registration_is_unmoved(PREREG)


def test_the_record_this_session_writes_is_not_r2s():
    """`scripts/check_lora_c_vramprobe_report.py` sums EVERY pod row of `results/lora_c_run.json`.

    An append there would re-derive a SEALED report's money against this session's pod — the Dv828
    shape one contract later ([[a_sealed_reports_checker_reads_a_live_file]]).
    """
    assert gate.RECORD.name == "lora_c_run_r3.json"
    assert gate.RECORD != parent.RECORD
    assert "results/lora_c_run_r3.json" in PREREG["artifacts"]


# --- the money, re-derived rather than read back ---------------------------------------------------


def test_the_fixed_part_is_the_sum_of_its_own_addends():
    fixed = PREREG["money"]["pre_pod_arithmetic"]["fixed_seconds"]
    addends = {k: v for k, v in fixed.items() if isinstance(v, int | float) and k != "total"}
    assert round(sum(addends.values()), 4) == fixed["total"] == 9050.2
    assert set(addends) == set(fixed["what_each_addend_is"])


def test_every_priced_addend_is_its_own_rate_times_its_own_count():
    arithmetic = PREREG["money"]["pre_pod_arithmetic"]
    fixed, rates = arithmetic["fixed_seconds"], arithmetic["rates_used"]
    call = float(rates["pass_1_seconds_per_call"])
    assert fixed["pass_1_evals_of_the_two_adapters"] == 2 * 198 * call
    assert fixed["pass_2"] == 2 * 15 * float(rates["pass_2_seconds_per_thread"])
    assert fixed["marker_census"] == 40 * call
    assert fixed["training_smoke"] == rung(4)["steps"] * rung(4)["threshold"]
    assert fixed["boot"] == rung(1)["threshold"]


def test_the_stage_sum_and_its_headroom_are_the_training():
    block = PREREG["money"]["pre_pod_arithmetic"]["the_stage_bounds_SUM_inside_the_stop"]
    fixed = PREREG["money"]["pre_pod_arithmetic"]["fixed_seconds"]["total"]
    stop = PREREG["money"]["pre_pod_arithmetic"]["hard_stop_seconds"]
    assert block["summed_seconds"] == fixed
    assert round(block["headroom_seconds"], 4) == round(stop - fixed, 4)
    steps = sum(PREREG["money"]["formulas"]["steps"].values())
    assert steps == 144
    assert round((stop - fixed) / steps, 2) == 62.15


@pytest.mark.parametrize(
    "row",
    PREREG["money"]["pre_pod_arithmetic"]["the_break_even_is_a_FUNCTION_not_a_number"]["rows"],
)
def test_every_break_even_row_re_derives(row):
    """Four corners of two unmeasured rates. Each is recomputed from the cap, never read back."""
    cap = PREREG["money"]["cap_usd_all_in"]
    stop = PREREG["money"]["pre_pod_arithmetic"]["hard_stop_seconds"]
    thread = float(PREREG["money"]["pre_pod_arithmetic"]["rates_used"]["pass_2_seconds_per_thread"])
    call, threads = row["pass_1_seconds_per_call"], row["pass_2_threads_per_leg"]
    fixed = (
        rung(1)["threshold"]
        + 180.0
        + 60.0
        + rung(4)["steps"] * rung(4)["threshold"]
        + 2 * 198 * call
        + 2 * threads * thread
        + 40 * call
        + 300.0
    )
    usd = fixed / 3600 * PRICE
    left_seconds = (cap - usd) / PRICE * 3600
    assert round(fixed, 1) == row["fixed_seconds"]
    assert round(usd, 4) == row["fixed_usd"]
    assert round(left_seconds / 144, 2) == row["break_even_seconds_per_step"]
    assert round((stop - fixed) / 144, 2) == row["hard_stop_bound_seconds_per_step"]
    assert row["hard_stop_bound_seconds_per_step"] < row["break_even_seconds_per_step"]


def test_the_charged_row_lands_between_the_two_readings_this_repo_owns():
    """The whole reason a KILL after the smoke is a live outcome, and it is stated, not hoped."""
    block = PREREG["money"]["pre_pod_arithmetic"]["the_break_even_is_a_FUNCTION_not_a_number"]
    charged = next(
        one
        for one in block["rows"]
        if one["pass_1_seconds_per_call"] == 9.20 and one["pass_2_threads_per_leg"] == 15
    )
    low = block["readings_this_repo_holds"]["registered_by_lora_b"]
    high = block["readings_this_repo_holds"]["measured_on_lora_b_arm_a"]
    assert low < charged["hard_stop_bound_seconds_per_step"] < high


def test_what_the_two_readings_would_cost_re_derives():
    arithmetic = PREREG["money"]["pre_pod_arithmetic"]
    fixed = arithmetic["fixed_seconds"]["total"]
    stop, cap = arithmetic["hard_stop_seconds"], PREREG["money"]["cap_usd_all_in"]
    for rate, said in arithmetic["what_the_two_readings_this_repo_holds_would_cost"].items():
        if not isinstance(said, dict):
            continue
        training = float(rate) * 144
        session = fixed + training
        assert round(training, 1) == said["training_seconds"]
        assert round(session, 1) == said["session_seconds"]
        assert said["over_the_stop"] is (session > stop)
        assert said["over_the_cap"] is (session / 3600 * PRICE > cap)


def test_the_hard_stop_is_an_inequality_the_cap_can_pay_for():
    got = gate.the_cap_affords_the_hard_stop(PREREG, PRICE)
    assert got["what_the_cap_buys_seconds"] == 18129.5
    assert got["hard_stop_registered_seconds"] == 18000.0
    assert got["slack_seconds"] == 129.5
    assert (
        PREREG["money"]["pre_pod_arithmetic"]["at_each_price"]["1.39"]["hard_stop_buys_seconds"]
        == got["what_the_cap_buys_seconds"]
    )


def test_a_price_the_cap_cannot_afford_the_stop_at_refuses():
    """Driven on a synthetic price, because no price rung 0 admits can fail it at this cap."""
    with pytest.raises(SystemExit, match="more than the cap can pay for"):
        gate.the_cap_affords_the_hard_stop(PREREG, 2.00)


# --- the read-back, the contract's own refusal gate -------------------------------------------------


def test_the_read_back_re_derives_every_registered_number():
    got = gate.read_back(PREREG)
    assert got["verdict"] == "GO", got["findings"]
    assert [one["what"] for one in got["read_back"] if not one["holds"]] == []
    printed = {one["what"]: one["reading"] for one in got["read_back"]}
    assert "arm A 62 / arm B 82 (planned 64/84)" in printed["optimizer steps"]
    assert printed["training rows"] == "506 / 666"
    assert "3072 / 2975" in printed["the encode ceiling and the widest row"]
    assert printed["pass-2 threads charged, per leg"].startswith("15 ")


def test_the_read_back_refuses_when_a_registered_number_moves():
    moved = json.loads(json.dumps(PREREG))
    moved["money"]["formulas"]["steps"]["arm_a"] = 64
    got = gate.read_back(moved)
    assert got["verdict"] == "KILL"
    assert got["findings"] == ["optimizer steps"]
    assert "FINDING" in got["next_step"]


def test_the_read_back_refuses_a_re_bought_base_leg():
    moved = json.loads(json.dumps(PREREG))
    moved["legs"]["base_v2"]["eval_calls"] = 198
    assert gate.read_back(moved)["findings"] == ["the base legs are BOUGHT and are not re-bought"]


# --- rung 0, the price and the card -----------------------------------------------------------------


def test_rung_0_admits_the_card_and_the_price_the_plan_was_solved_at():
    """A rung that has only ever been seen refusing is what ends a session at minute one."""
    got = parent.price_gate(view(), PRICE, "A100 PCIe")
    assert got["verdict"] == "GO"
    assert got["price_has_a_registered_column"] and got["card_is_authorised"]
    assert parent.price_gate(view(), PRICE, "NVIDIA A100 80GB PCIe")["verdict"] == "GO"


@pytest.mark.parametrize(
    "price,card,why",
    [
        (1.39, "RTX PRO 4500", "card_is_authorised"),
        (1.64, "A100 PCIe", "price_has_a_registered_column"),
        (1.51, "A100 PCIe", "over_the_ceiling"),
    ],
)
def test_rung_0_refuses(price, card, why):
    got = parent.price_gate(view(), price, card)
    assert got["verdict"] == "KILL"
    assert got[why] is (why == "over_the_ceiling")
    assert "DELETE the pod now" in got["next_step"]


# --- rungs 1 and 2 -----------------------------------------------------------------------------------


def test_the_boot_gate_has_three_outcomes(run):
    record, state = view(), a_pod()
    assert parent.boot_gate(record, state, True, at(30))["verdict"] == "GO"
    assert parent.boot_gate(record, state, False, at(120))["verdict"] == "WAIT"
    assert parent.boot_gate(record, state, False, at(500))["verdict"] == "KILL"


def test_liveness_measures_from_the_last_thing_that_happened(run):
    record, state = view(), a_pod()
    last = at(1000).isoformat()
    assert parent.liveness(record, state, last, at(1500))["verdict"] == "GO"
    assert parent.liveness(record, state, last, at(1600))["verdict"] == "KILL"


# --- the load proof, on BLOBS -------------------------------------------------------------------------

BLOBS = {"hub/models--google--gemma-4-31b-it/blobs/a": 62578686256, "hub/x/blobs/b": 1024}


def a_proof(tmp_path: Path, **moved) -> Path:
    """The migration's OWN reading: the whole cache moved 40 bytes and no blob did."""
    record = {
        "revision": REVISION,
        "load_seconds": 40.22,
        "loaded": True,
        "gpu": "NVIDIA A100 80GB PCIe",
        "vram_bytes_allocated": 18_253_611_008,
        "vram_bytes_total": 84_974_239_744,
        "hf_bytes_before": 62580183517,
        "hf_bytes_after": 62580183557,
        "blob_bytes_before": dict(BLOBS),
        "blob_bytes_after": dict(BLOBS),
        **moved,
    }
    path = tmp_path / "load_proof.json"
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    return path


def test_the_forty_bytes_that_killed_the_migration_are_a_GO_here(run, tmp_path):
    """The remedy, stated as a reading: `refs/main` plus four absence markers, 0 blobs written."""
    got = gate.load_proof_gate(view(), a_pod(), CREATE, a_proof(tmp_path), at(200))
    assert got["verdict"] == "GO"
    assert got["whole_cache_moved_by_bytes"] == 40
    assert got["no_blob_grew"] is True
    assert got["blobs_that_grew"] == []
    assert got["blob_bytes_total"] == sum(BLOBS.values())


def test_a_planted_blob_growth_still_KILLs(run, tmp_path):
    """The contract's own negative control — a rung nobody has watched refuse is not a rung."""
    grown = dict(BLOBS)
    grown["hub/models--google--gemma-4-31b-it/blobs/a"] += 4096
    got = gate.load_proof_gate(
        view(), a_pod(), CREATE, a_proof(tmp_path, blob_bytes_after=grown), at(200)
    )
    assert got["verdict"] == "KILL"
    assert "GREW across the load" in got["what_failed"]
    assert got["blobs_that_grew"] == [
        {
            "blob": "hub/models--google--gemma-4-31b-it/blobs/a",
            "bytes_before": BLOBS["hub/models--google--gemma-4-31b-it/blobs/a"],
            "bytes_after": BLOBS["hub/models--google--gemma-4-31b-it/blobs/a"] + 4096,
            "grew_by": 4096,
        }
    ]


def test_a_NEW_blob_is_a_growth_too(run, tmp_path):
    fetched = {**BLOBS, "hub/models--google--gemma-4-31b-it/blobs/fresh": 1}
    got = gate.load_proof_gate(
        view(), a_pod(), CREATE, a_proof(tmp_path, blob_bytes_after=fetched), at(200)
    )
    assert got["verdict"] == "KILL"
    assert [one["blob"] for one in got["blobs_that_grew"]] == [
        "hub/models--google--gemma-4-31b-it/blobs/fresh"
    ]


@pytest.mark.parametrize(
    "moved,why",
    [
        ({"revision": "main"}, "not the pinned one"),
        ({"loaded": False}, "did not report a loaded model"),
        ({"load_seconds": 601.0}, "exceeded its deadline"),
    ],
)
def test_the_load_proof_refuses_each_way(run, tmp_path, moved, why):
    got = gate.load_proof_gate(view(), a_pod(), CREATE, a_proof(tmp_path, **moved), at(200))
    assert got["verdict"] == "KILL" and why in got["what_failed"]


def test_a_missing_load_proof_waits_and_then_kills(run, tmp_path):
    missing = tmp_path / "not_yet.json"
    assert gate.load_proof_gate(view(), a_pod(), CREATE, missing, at(100))["verdict"] == "WAIT"
    assert gate.load_proof_gate(view(), a_pod(), CREATE, missing, at(700))["verdict"] == "KILL"


# --- the pod-side producer, driven with a fake loader --------------------------------------------------


def test_the_pod_runner_inventories_blobs_around_the_load(tmp_path):
    """Driven end to end with a fake client — an import proves nothing
    ([[stub_driven_script_verification]])."""
    home = tmp_path / "hf"
    blobs = home / "hub" / "models--google--gemma-4-31b-it" / "blobs"
    blobs.mkdir(parents=True)
    (blobs / "a").write_bytes(b"x" * 100)
    snapshots = home / "hub" / "models--google--gemma-4-31b-it" / "snapshots" / REVISION
    snapshots.mkdir(parents=True)
    out = tmp_path / "load_proof.json"

    seen = {}

    def loader(model, revision):
        seen["called"] = (model, revision)
        (blobs / "a").write_bytes(b"x" * 100)  # a read that rewrites nothing
        return object(), object()

    code = proof_runner.main(
        ["--revision", REVISION, "--hf-home", str(home), "--out", str(out)],
        loader=loader,
        du=lambda path, run=None: 100,
    )
    assert code == 0
    assert seen["called"] == ("google/gemma-4-31b-it", REVISION)
    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["no_blob_grew"] is True
    assert record["blobs_counted"] == 1
    assert record["blob_bytes_total"] == 100
    assert gate.load_proof_gate(view(), a_pod(), CREATE, out, at(200))["verdict"] == "GO"


def test_the_pod_runner_catches_a_blob_the_load_fetched(tmp_path):
    home = tmp_path / "hf"
    blobs = home / "hub" / "models--google--gemma-4-31b-it" / "blobs"
    blobs.mkdir(parents=True)
    (blobs / "a").write_bytes(b"x" * 100)
    out = tmp_path / "load_proof.json"

    def loader(model, revision):
        (blobs / "shard-2").write_bytes(b"y" * 4096)  # the thing the invariant is about
        return object(), object()

    proof_runner.main(
        ["--revision", REVISION, "--hf-home", str(home), "--out", str(out)],
        loader=loader,
        du=lambda path, run=None: 100,
    )
    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["no_blob_grew"] is False
    assert list(record["blobs_that_grew"]) == ["hub/models--google--gemma-4-31b-it/blobs/shard-2"]
    assert gate.load_proof_gate(view(), a_pod(), CREATE, out, at(200))["verdict"] == "KILL"


def test_an_empty_cache_is_refused_before_the_model_loads(tmp_path):
    (tmp_path / "hf").mkdir()
    with pytest.raises(SystemExit, match="holds no blob files"):
        proof_runner.main(
            [
                "--revision",
                REVISION,
                "--hf-home",
                str(tmp_path / "hf"),
                "--out",
                str(tmp_path / "o.json"),
            ],
            loader=lambda *a: (object(), object()),
        )


# --- rung 4, the smoke ---------------------------------------------------------------------------------


def a_smoke(tmp_path: Path, seconds_per_step: float = 55.0, **moved) -> tuple[Path, Path]:
    """The two files the smoke leaves: `provenance.json` and a TWO-line loss log."""
    run_block = {
        "steps": 6,
        "seconds": round(seconds_per_step * 6, 1),
        "seconds_per_step": seconds_per_step,
        "micro_batch_final": 2,
        "grad_accum_final": 8,
        "gpu_gb_peak": 41.7,
        **moved,
    }
    provenance = tmp_path / "provenance.json"
    provenance.write_text(json.dumps({"run": run_block}) + "\n", encoding="utf-8")
    loss = tmp_path / "loss.jsonl"
    loss.write_text(
        "\n".join(
            json.dumps(one)
            for one in (
                {"step": 5, "loss": 1.9, "seconds_per_step": seconds_per_step, "micro_batch": 2},
                # step 6 closes the run: ONE step's wall divided by log_every 5 (Dv814)
                {
                    "step": 6,
                    "loss": 1.8,
                    "seconds_per_step": seconds_per_step / 5,
                    "micro_batch": 2,
                },
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return provenance, loss


def test_the_smoke_grades_the_provenance_rate_and_two_loss_lines_are_enough(run, tmp_path):
    """Dv813 and Dv814 in one reading: the sibling would WAIT for ever and grade the wrong number."""
    provenance, loss = a_smoke(tmp_path, 55.0)
    state = a_pod()
    got = gate.smoke_gate(view(), state, provenance, loss, at(2000))
    assert got["verdict"] == "GO"
    assert got["measured_seconds_per_step"] == 55.0
    assert len(got["loss_lines"]) == 2
    assert [one["seconds_per_step_as_logged"] for one in got["loss_lines"]] == [55.0, 11.0]
    assert state["measured_seconds_per_step"] == 55.0
    # the number the sibling would have handed the projection, from the same two lines
    assert parent.sibling.measured_step(gate.log_lines(loss)) == 33.0
    assert got["measured_seconds_per_step"] != 33.0


def test_the_smoke_refuses_a_rate_over_the_ceiling(run, tmp_path):
    provenance, loss = a_smoke(tmp_path, 200.0)
    state = a_pod()
    got = gate.smoke_gate(view(), state, provenance, loss, at(2000))
    assert got["verdict"] == "KILL" and "over the registered 181.5" in got["why"]
    assert "measured_seconds_per_step" not in state


def test_the_smoke_reads_the_OOM_out_of_micro_batch_and_not_out_of_a_flag(run, tmp_path):
    """`train_qlora.train` halves micro_batch on OOM and CARRIES ON — the arm becomes another arm."""
    provenance, loss = a_smoke(tmp_path, 55.0, micro_batch_final=1, grad_accum_final=16)
    got = gate.smoke_gate(view(), a_pod(), provenance, loss, at(2000))
    assert got["verdict"] == "KILL"
    assert "halved its way out of an OOM" in got["why"]
    assert got["the_instrument_is_the_registered_one"] is False


def test_the_smoke_refuses_a_short_run(run, tmp_path):
    provenance, loss = a_smoke(tmp_path, 55.0, steps=4)
    got = gate.smoke_gate(view(), a_pod(), provenance, loss, at(2000))
    assert got["verdict"] == "KILL" and "4 of 6 optimizer steps" in got["why"]


def test_the_smoke_waits_while_the_loop_is_still_running(run, tmp_path):
    _, loss = a_smoke(tmp_path, 55.0)
    got = gate.smoke_gate(view(), a_pod(), tmp_path / "absent.json", loss, at(500))
    assert got["verdict"] == "WAIT"
    assert len(got["loss_lines_so_far"]) == 2


def test_the_registered_micro_batch_is_the_configs():
    import yaml

    training = yaml.safe_load((REPO_ROOT / "config" / "qlora.yaml").read_text("utf-8"))["training"]
    assert gate.the_registered_micro_batch() == (
        training["micro_batch_size"],
        training["grad_accum"],
    )
    assert training["log_every"] == 5, "the two-line loss log is a consequence of this number"


# --- rung 3, the realised rate of an EVAL leg -----------------------------------------------------------


def replies(tmp_path: Path, rows: int) -> Path:
    path = tmp_path / "eval.jsonl"
    path.write_text(
        "".join(json.dumps({"id": one}) + "\n" for one in range(rows)), encoding="utf-8"
    )
    return path


def test_the_rate_rung_fires_on_an_eval_leg_which_the_sibling_could_not(run, tmp_path):
    assert gate.RATEABLE == ("eval_a", "eval_b")
    got = parent.rate_gate(view(), a_pod(), "eval_a", replies(tmp_path, 20), CREATE, at(200))
    assert got["rows_answered"] == 20
    assert got["realised_seconds_per_call"] == 10.0
    assert got["verdict"] in {"GO", "KILL"}


def test_the_rate_rung_charges_the_measured_step_once_the_smoke_has_bought_one():
    floor = rung(3)["steps_charged_at_seconds_per_step"]
    _, cold = gate.the_rate_rung_charges_the_measured_step(PREREG, {})
    assert cold == {"steps_charged_at": floor, "the_charge_is_measured": False}

    warm_view, warm = gate.the_rate_rung_charges_the_measured_step(
        PREREG, {"measured_seconds_per_step": 70.0}
    )
    assert warm["steps_charged_at"] == 70.0 and warm["the_charge_is_measured"] is True
    assert warm["the_registered_floor_it_replaces"] == floor
    assert gate.rung(warm_view, 3)["steps_charged_at_seconds_per_step"] == 70.0
    assert rung(3)["steps_charged_at_seconds_per_step"] == floor, "the record itself never moved"


def test_a_slow_eval_leg_kills_before_the_next_one(run, tmp_path):
    """One reply in 600 s is 600 s/call, and no cap survives that."""
    got = parent.rate_gate(view(), a_pod(), "eval_a", replies(tmp_path, 1), CREATE, at(600))
    assert got["verdict"] == "KILL"
    assert got["projected_usd"] > got["cap_usd_all_in"]
    assert "finding is the card" in got["next_step"]


# --- rung 5, the projection ------------------------------------------------------------------------------


def test_the_projection_adds_the_teardown_tail_the_sibling_cannot_see(run):
    state = {**a_pod(), "measured_seconds_per_step": 55.0}
    record = view()
    inner = parent.projection(record, state, "smoke", 0.77, at(2000))
    got = gate.projection(record, state, "smoke", 0.77, None, at(2000))
    tail = PREREG["money"]["pre_pod_arithmetic"]["fixed_seconds"]["teardown_and_pull"]
    assert got["seconds_ahead_with_the_tail"] == round(inner["seconds_ahead"] + tail, 1)
    assert got["projected_usd"] > inner["projected_usd"]
    assert got["teardown_and_pull_tail_seconds"] == tail


def test_the_projection_says_GO_at_a_step_the_plan_affords(run):
    state = {**a_pod(), "measured_seconds_per_step": 55.0}
    got = gate.projection(view(), state, "smoke", 0.77, None, at(2000))
    assert got["verdict"] == "GO"
    assert got["seconds_per_step_is_measured"] is True
    assert got["remaining_work"] == {"pass_1_calls": 436, "steps": 144, "pass_2_threads": 30}


def test_the_projection_KILLs_at_a_step_the_plan_does_not(run):
    state = {**a_pod(), "measured_seconds_per_step": 90.0}
    got = gate.projection(view(), state, "smoke", 0.77, None, at(2000))
    assert got["verdict"] == "KILL"
    assert got["over_the_cap"] or got["over_the_hard_stop"]
    assert "A KILL here is compliance" in got["next_step"]


def test_the_projection_reports_what_the_thread_bound_charged(run):
    state = {**a_pod(), "measured_seconds_per_step": 55.0}
    got = gate.projection(view(), state, "smoke", 0.77, 11, at(2000))
    bound = got["the_pass_2_bound"]
    assert bound["pass_2_threads_charged_per_leg"] == 15
    assert bound["pass_2_threads_realised_per_leg"] == 11
    assert bound["seconds_the_bound_charges_over_the_realised_count"] == (15 - 11) * 97 * 2


def test_a_projection_with_no_measured_step_charges_the_smoke_ceiling(run):
    """The state handoff matters: a lost write turns a healthy smoke into a KILL on 181.5."""
    got = gate.projection(view(), a_pod(), "smoke", 0.77, None, at(2000))
    assert got["seconds_per_step_is_measured"] is False
    assert got["seconds_per_step_used"] == rung(4)["threshold"]
    assert got["verdict"] == "KILL"


# --- rungs 6 and 7, and the plan table ---------------------------------------------------------------------


def test_the_backstop_is_the_stop_less_what_a_closed_pod_billed(run):
    state = {
        "pods": [
            {
                "pod_id": "dead",
                "created_at": CREATE,
                "usd_per_hour": PRICE,
                "deleted_at": at(600).isoformat(),
                "billed_seconds": 600.0,
                "billed_usd": 0.2317,
            }
        ]
    }
    second = at(700).isoformat()
    got = parent.sibling.terminate_after(
        view(), state, second, (at(700) + timedelta(seconds=17400)).isoformat()
    )
    assert got["window_seconds"] == 17400.0
    assert got["overshoot_seconds"] == 0.0


def test_a_backstop_longer_than_the_stop_allows_is_refused(run):
    with pytest.raises(SystemExit, match="beyond the"):
        parent.sibling.terminate_after(
            view(), {"pods": []}, CREATE, (at(0) + timedelta(seconds=19000)).isoformat()
        )


def test_the_plan_table_is_derived_from_the_registration(run):
    table = parent.plan(view())
    assert table == {
        "base_v2": {"pass_1_calls": 0},
        "base_v3": {"pass_1_calls": 0},
        "smoke": {"steps": 6},
        "arm_a": {"steps": 62},
        "eval_a": {"pass_1_calls": 198, "pass_2_threads": 15},
        "arm_b": {"steps": 82},
        "eval_b": {"pass_1_calls": 198, "pass_2_threads": 15},
        "marker_census": {"pass_1_calls": 40},
    }
    assert parent.remaining_after(view(), "eval_b") == {
        "pass_1_calls": 40,
        "steps": 0,
        "pass_2_threads": 0,
    }


# --- the commands, driven ------------------------------------------------------------------------------------


def test_the_read_back_command_exits_GO(run, capsys):
    assert gate.main(["--read-back"]) == gate.GO
    printed = capsys.readouterr().out
    assert '"verdict": "GO"' in printed and "arm A 62 / arm B 82" in printed


def test_the_pre_create_check_passes_with_no_pod(run, capsys):
    run.RECORD.write_text(json.dumps({"pods": []}) + "\n", encoding="utf-8")
    assert gate.main(["--pre-create-check"]) == gate.GO
    assert "no pod is open" in capsys.readouterr().out


def test_the_pre_create_check_refuses_while_a_pod_is_open(run, capsys):
    run.RECORD.write_text(json.dumps(a_pod()) + "\n", encoding="utf-8")
    assert gate.main(["--pre-create-check"]) == gate.KILL
    assert "never two billing resources" in capsys.readouterr().out


def test_open_records_the_pod_and_prints_the_affordability(run, capsys):
    code = gate.main(
        [
            "--open",
            "--pod-id",
            "mp-r3-1",
            "--created-at",
            CREATE,
            "--usd-per-hour",
            str(PRICE),
            "--card",
            "A100 PCIe",
            "--terminate-after",
            (at(0) + timedelta(seconds=18000)).isoformat(),
        ],
        at(1),
    )
    assert code == gate.GO
    printed = capsys.readouterr().out
    assert '"what_the_cap_buys_seconds": 18129.5' in printed
    state = json.loads(run.RECORD.read_text(encoding="utf-8"))
    assert state["pods"][0]["card"] == "A100 PCIe"
    assert state["gates"][-1]["verdict"] == "GO"


def test_open_refuses_a_second_pod_while_one_is_live(run):
    run.RECORD.write_text(json.dumps(a_pod()) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="Rung 7"):
        gate.main(
            [
                "--open",
                "--pod-id",
                "two",
                "--created-at",
                CREATE,
                "--usd-per-hour",
                str(PRICE),
                "--card",
                "A100 PCIe",
                "--terminate-after",
                (at(0) + timedelta(seconds=18000)).isoformat(),
            ],
            at(1),
        )


def test_the_smoke_and_the_load_proof_are_appended_to_the_record(run, tmp_path, capsys):
    run.RECORD.write_text(json.dumps(a_pod()) + "\n", encoding="utf-8")
    assert (
        gate.main(
            ["--load-proof", "--started-at", CREATE, "--proof", str(a_proof(tmp_path))], at(200)
        )
        == gate.GO
    )
    provenance, loss = a_smoke(tmp_path, 55.0)
    assert (
        gate.main(["--smoke", "--provenance", str(provenance), "--loss", str(loss)], at(2000))
        == gate.GO
    )
    capsys.readouterr()
    state = json.loads(run.RECORD.read_text(encoding="utf-8"))
    assert [one["kind"] for one in state["gates"]] == ["load-proof", "smoke"]
    assert state["measured_seconds_per_step"] == 55.0
    assert all(one["frozen"]["unmoved"] for one in state["gates"])


def test_close_pod_prices_the_pod_by_its_own_clock(run, capsys):
    run.RECORD.write_text(json.dumps(a_pod()) + "\n", encoding="utf-8")
    assert (
        gate.main(
            ["--close-pod", "--deleted-at", at(3600).isoformat(), "--outcome", "done"], at(3601)
        )
        == gate.GO
    )
    state = json.loads(run.RECORD.read_text(encoding="utf-8"))
    assert state["pods"][0]["billed_seconds"] == 3600.0
    assert state["pods"][0]["billed_usd"] == PRICE
    assert "prove the deletion by LISTING" in capsys.readouterr().out


def test_the_gate_puts_the_siblings_constants_back(run):
    """The `finally` is what keeps lora-c's and the migration's own gates true in one process."""
    before = (parent.PHASE, parent.PREREG, parent.RECORD)
    gate.main(["--read-back"])
    assert (parent.PHASE, parent.PREREG, parent.RECORD) == before


# --- step 0.5 (3): the `[-1]` selectors over `results/` ledgers ------------------------------------


def test_no_lora_c_report_checker_selects_a_ledger_row_by_its_last_index():
    """The enumeration, kept closed — by an AST scan, because prose about `[-1]` is not `[-1]`.

    Dv828 was this shape: a SEALED report's checker read `results/spend_cycle2.json`'s last row and
    a later contract appended to it. `smokes[-1]` survived that fix because its ledger had not been
    written since — «not written yet» is not «cannot be written»
    ([[a_sealed_reports_checker_reads_a_live_file]], [[select_one_row_refuse_ambiguity]]). Three of
    these files DISCUSS `[-1]` in their docstrings, which is why a grep cannot answer this and the
    parser can ([[a_count_in_prose_is_not_the_enumeration]]).
    """
    import ast

    offenders = []
    for path in sorted((REPO_ROOT / "scripts").glob("check_lora_c_*.py")):
        tree = ast.parse(path.read_text("utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Subscript):
                continue
            index = node.slice
            if (
                isinstance(index, ast.UnaryOp)
                and isinstance(index.op, ast.USub)
                and isinstance(index.operand, ast.Constant)
                and index.operand.value == 1
            ):
                offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == [], offenders


def test_the_ast_scan_would_see_a_last_row_selector(tmp_path):
    """The scan's own negative control — a checker that has never been seen finding one is not one."""
    import ast

    tree = ast.parse('rows = ledger["gates"]\nlast = rows[-1]\n')
    found = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Subscript)
        and isinstance(node.slice, ast.UnaryOp)
        and isinstance(node.slice.op, ast.USub)
    ]
    assert found == [2]


def test_the_vramprobe_checker_ignores_a_row_appended_after_its_reading(monkeypatch):
    """The negative control the fix needs: a LATER row must not move the selection."""
    import importlib.util

    monkeypatch.chdir(REPO_ROOT)
    spec = importlib.util.spec_from_file_location(
        "vramprobe_checker", REPO_ROOT / "scripts" / "check_lora_c_vramprobe_report.py"
    )
    checker = importlib.util.module_from_spec(spec)
    with pytest.raises(SystemExit) as exited:  # the checker IS its exit code, at module level
        spec.loader.exec_module(checker)
    assert exited.value.code == 0, "the sealed report still re-derives, 61 of 61"

    rows = [
        {"at": checker.THE_SMOKE_WAIT_AT, "verdict": "WAIT"},
        {"at": checker.THE_SMOKE_KILL_AT, "verdict": "KILL"},
        {"at": "2026-08-27T09:00:00+00:00", "verdict": "GO"},  # a later session's row
    ]
    assert checker.the_row_at(rows, checker.THE_SMOKE_KILL_AT)["verdict"] == "KILL"
    assert checker.the_row_at(rows, checker.THE_SMOKE_WAIT_AT)["verdict"] == "WAIT"
    with pytest.raises(SystemExit, match="a reading must be exactly one row"):
        checker.the_row_at(rows, "2026-08-28T00:00:00+00:00")
    with pytest.raises(SystemExit, match="a reading must be exactly one row"):
        checker.the_row_at(rows + [dict(rows[1])], checker.THE_SMOKE_KILL_AT)


def test_the_smoke_prints_the_final_steps_isolated_wall_and_grades_none_of_it():
    """Dv814 run backwards: the last window holds ONE step and still divides by `log_every`."""
    rows = [
        {"step": 5, "seconds_per_step": 55.0},
        {"step": 6, "seconds_per_step": 10.0},  # 50 s of wall, divided by log_every 5
    ]
    assert gate.the_last_windows_isolated_wall(rows, 5, 6) == 50.0
    assert gate.the_last_windows_isolated_wall(rows, 5, 8) is None, "the line is not the last step"
    assert gate.the_last_windows_isolated_wall(rows[:1], 5, 6) is None
    assert (
        gate.the_last_windows_isolated_wall(
            [{"step": 5, "seconds_per_step": 55.0}, {"step": 10, "seconds_per_step": 10.0}], 5, 10
        )
        is None
    ), "a five-step window is not one step"


def test_the_decomposition_separates_start_up_from_the_card(run, tmp_path):
    provenance, loss = a_smoke(tmp_path, 55.0)
    got = gate.smoke_gate(view(), a_pod(), provenance, loss, at(2000))
    block = got["the_decomposition_REPORT_ONLY"]
    assert block["log_every"] == 5
    assert block["the_final_steps_isolated_wall_seconds"] == 55.0  # 11.0 as logged × 5
    assert block["the_graded_rate_seconds_per_step"] == 55.0
    assert block["the_loop_wall_seconds"] == 330.0
    assert block["the_amortised_start_up_seconds"] == 0.0
    assert got["verdict"] == "GO", "the decomposition grades nothing"


def test_a_smoke_whose_start_up_is_the_whole_gap_still_grades_on_the_loop(run, tmp_path):
    """The case the block exists for: the loop reads over the break-even, one steady step does not."""
    provenance = tmp_path / "provenance.json"
    provenance.write_text(
        json.dumps(
            {
                "run": {
                    "steps": 6,
                    "seconds": 390.0,  # 65.0 s/step graded
                    "seconds_per_step": 65.0,
                    "micro_batch_final": 2,
                    "grad_accum_final": 8,
                }
            }
        ),
        encoding="utf-8",
    )
    loss = tmp_path / "loss.jsonl"
    loss.write_text(
        json.dumps({"step": 5, "seconds_per_step": 68.0})
        + "\n"
        + json.dumps({"step": 6, "seconds_per_step": 10.0})  # one step of 50 s
        + "\n",
        encoding="utf-8",
    )
    got = gate.smoke_gate(view(), a_pod(), provenance, loss, at(2000))
    block = got["the_decomposition_REPORT_ONLY"]
    assert got["measured_seconds_per_step"] == 65.0, "the graded rate is the loop's"
    assert block["the_final_steps_isolated_wall_seconds"] == 50.0
    assert block["the_amortised_start_up_seconds"] == 90.0
    assert got["verdict"] == "GO", (
        "65.0 is under the 181.5 ceiling — the projection decides the rest"
    )


def test_the_thread_bound_is_what_makes_the_plan_knife_edge():
    """Measured at $0 before the create: a v3-shaped pass-1 leg put TEN threads in the pack.

    At the charged bound of 15 the break-even is 62.15 s/step and lora-b's 68.442 does not fit; at
    10 it is 68.89 and both readings this repo owns do. The charge does not move — the contract
    fixes 15 — but a KILL between those two rates is attributable to the BOUND and not to the card
    ([[name_what_the_range_protects]]).
    """
    block = PREREG["money"]["pre_pod_arithmetic"]["the_break_even_is_a_FUNCTION_not_a_number"]
    by_threads = {
        one["pass_2_threads_per_leg"]: one
        for one in block["rows"]
        if one["pass_1_seconds_per_call"] == 9.20
    }
    high = block["readings_this_repo_holds"]["measured_on_lora_b_arm_a"]
    assert by_threads[15]["hard_stop_bound_seconds_per_step"] < high
    assert by_threads[10]["hard_stop_bound_seconds_per_step"] > high
    measured = block["the_ten_thread_reading_taken_at_0_before_the_create"]
    assert "10 of 16 reference threads" in measured["reading"]
    assert measured["r2s_v2_leg_produced"] == 11
    # the charge itself is untouched: the plan still prices 15 threads a leg
    assert sibling_plan_threads() == 15


def sibling_plan_threads() -> int:
    return parent.plan(view())["eval_a"]["pass_2_threads"]


def test_every_number_in_the_report_is_re_derived_from_the_file_that_owns_it():
    """`scripts/check_lora_c_run_r3_report.py`, driven as a COMMAND — its exit code is the claim.

    The report says «73 of 73 re-derived»; this is what makes that sentence checkable rather than
    something I once ran ([[a_claim_no_number_can_check]]). It reads the paid session's artifacts,
    so it is red in every commit before they land, which is the correct direction for a claim about
    them ([[a_test_that_reads_a_shipped_artifact]]).
    """
    import subprocess

    got = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "check_lora_c_run_r3_report.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert got.returncode == 0, got.stdout + got.stderr


def test_the_sibling_gate_would_have_passed_this_smoke():
    """The report's central counterfactual, driven here too — it is why r3's gate exists.

    `gate_lora_b.measured_step` grades the loss lines, and on this session's own log it reads 53.690
    against a loop that ran at 89.961. Under the 68.05 s/step the cap afforded, so the projection
    would have said GO and the session would have burned $6.95 into the terminate flag with no
    adapter, no eval and no bar ([[projected_rate_versus_measured_rate]]).
    """
    loss = REPO_ROOT / "results" / "lora_c_run_r3_smoke_loss.jsonl"
    if not loss.exists():  # red before the paid session's artifacts land, green after
        pytest.skip("the paid session's loss log has not landed yet")
    lines = parent.sibling.log_lines(loss)
    run = json.loads(
        (REPO_ROOT / "results" / "lora_c_run_r3_smoke_provenance.json").read_text("utf-8")
    )["run"]
    assert round(parent.sibling.measured_step(lines), 3) == 53.690
    assert run["seconds_per_step"] == 89.961
    assert round(parent.sibling.measured_step(lines) / run["seconds_per_step"], 3) == 0.597
