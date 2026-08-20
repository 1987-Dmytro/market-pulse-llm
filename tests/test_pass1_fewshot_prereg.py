"""`results/prereg_pass1_fewshot.json` — the law, and H6 as the refusal gate it claims to be.

Three things carry the money. Every number the contract prints re-derives, and H6 REFUSES rather
than reporting when one does not — driven in both directions, because a re-derivation that has never
been seen to fail is arithmetic wearing a gate's name ([[guard_selftest_negative_control]]). Every
threshold the gate acts on is in this file and appears nowhere else, so a rung cannot go green after
one of two copies moves. And the dev gate's reachability branch is registered BEFORE the pod, since
the base's dev number is measured with a meter running.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass1_fewshot_packs as packs  # noqa: E402
import write_pass1_fewshot_prereg as prereg  # noqa: E402

from market_pulse import prompts  # noqa: E402

RECORD = json.loads((REPO_ROOT / prereg.OUT_NAME).read_text("utf-8"))
DEV = json.loads((REPO_ROOT / packs.DEV_NAME).read_text("utf-8"))
SHOT = json.loads((REPO_ROOT / packs.SHOT_NAME).read_text("utf-8"))


def test_the_shipped_registration_is_what_the_producer_writes_today(tmp_path):
    assert prereg.main(["--outdir", str(tmp_path)]) == 0
    assert (tmp_path / prereg.OUT_NAME).read_bytes() == (REPO_ROOT / prereg.OUT_NAME).read_bytes()
    assert "generated_at" not in (REPO_ROOT / prereg.OUT_NAME).read_text("utf-8")


def test_every_number_the_contract_prints_re_derives_and_the_arithmetic_closes():
    h6 = RECORD["h6"]
    assert h6["mismatches"] == []
    assert all(row["agrees"] for row in h6["rows"])
    assert len(h6["rows"]) >= 16
    sums = RECORD["money"]["arithmetic"]
    legs = sums["leg_seconds"]
    assert legs["base"] == 200 * 5.162 == 1032.4
    assert sums["seconds_per_call"]["v2"] == 7.743
    assert legs["v2"] == pytest.approx(200 * 7.743)
    assert legs["shot"] == pytest.approx(64 * 7.743)
    assert sums["total_seconds"] == pytest.approx(
        450 + legs["base"] + legs["v2"] + legs["shot"] + 1800
    )
    assert round(sums["total_seconds"], 1) == 5326.6
    assert round(sums["hours"], 4) == 1.4796
    assert round(sums["worst_case_usd_at_the_price_ceiling"], 4) == 1.1837
    # and the three inequalities the cap rests on
    stop = sums["cumulative"]
    assert stop["hard_stop_usd_at_the_price_ceiling"] == 1.40 < RECORD["money"]["cap_usd_all_in"]
    assert sums["worst_case_usd_at_the_price_ceiling"] < RECORD["money"]["cap_usd_all_in"]
    assert stop["session_ceiling_hours"] == 1.875 == 1.50 / 0.80


def test_H6_REFUSES_a_number_that_stops_re_deriving(monkeypatch):
    """The gate, driven. Every mode is exercised — an equality, a rounding and a direction."""
    for name, bent in (
        ("dev_base_seconds", 999.0),
        ("shot_seconds", 999.0),
        ("hard_stop_usd_at_the_ceiling", 0.01),
    ):
        monkeypatch.setitem(prereg.CONTRACT_PRINTS, name, bent)
        with pytest.raises(SystemExit, match="H6 is the step-1 refusal gate"):
            prereg.build()
        monkeypatch.undo()
    # the direction check: a boot ceiling BELOW the worst measured boot is refused
    monkeypatch.setattr(prereg, "BOOT_SECONDS", 300.0)
    with pytest.raises(SystemExit, match="H6 is the step-1 refusal gate"):
        prereg.build()
    monkeypatch.undo()
    # the premise: unbent, it builds
    assert prereg.build()["h6"]["mismatches"] == []


def test_the_boot_ceiling_is_re_derived_from_the_worst_boot_this_stack_has_MEASURED():
    """The contract's parenthetical «worst 293 × 1.5» quotes a worst that lora-b has since beaten.

    450 s is kept — it is rung 3's own threshold and it is still above the true worst — and its
    derivation is corrected here rather than carried forward as a stale multiplier
    ([[a_named_revision_is_not_a_passing_one]]).
    """
    boots = RECORD["money"]["arithmetic"]["boots_measured"]
    worst = max(max(one) for one in boots.values())
    assert worst == 353.0
    assert RECORD["money"]["arithmetic"]["boot_seconds_charged"] == 450.0 >= worst
    assert "353" in RECORD["money"]["arithmetic"]["boot_rule"]
    assert "293" in RECORD["money"]["arithmetic"]["boot_rule"]
    # and rung 3 gates on the same number the money charges
    rung = next(one for one in RECORD["kill_clock"] if one["rung"] == 3)
    assert "450" in rung["rule"]


def test_the_dev_gates_reachability_branch_is_registered_before_the_pod():
    bar = RECORD["bars"]["dev_gate"]
    assert bar["our_rows"] == 49 and bar["our_delta_minimum"] == 10
    assert "39" in bar["reachability"]
    assert "NOT spent" in bar["reachability"]
    assert bar["agreement_delta_minimum"] == -5
    assert set(bar["our_readings"]) == set(packs.OUR)
    row = next(
        one for one in RECORD["h6"]["rows"] if one["name"].startswith("our_delta_is_reachable")
    )
    assert row["re_derived"] == 39 and row["agrees"]


def test_the_kill_clock_has_the_liveness_rung_and_the_script_holds_it():
    rungs = {one["rung"]: one for one in RECORD["kill_clock"]}
    assert sorted(rungs) == list(range(1, 9))
    liveness = rungs[5]
    assert "600" in liveness["rule"] and "LAST EVENT" in liveness["rule"]
    assert "--watch" in liveness["read"]
    assert "9 720" in liveness["rule"], "the rung names the incident it was bought with"
    # rung 8: the shot's own out-file, and when the attempt is spent
    assert "OWN out-file" in rungs[8]["rule"]
    assert "SPENT at the first" in RECORD["attempt"]
    assert "THIRD shot" in RECORD["multiplicity"]


def test_the_registration_pins_the_instruments_the_run_will_actually_use():
    instruments = RECORD["instruments"]
    assert set(instruments["prompt_sha256"]) == set(prompts.PASS1)
    assert instruments["prompt_v1_did_not_move"] is True
    assert instruments["prompt_sha256"][prompts.PASS1_TASK] == prompts.prompt_sha256(
        prompts.PASS1_TASK
    )
    for name, path in (
        ("transport", "scripts/pass1_fewshot_pod_runner.py"),
        ("gate", "scripts/gate_pass1_fewshot.py"),
    ):
        assert instruments[name]["script"] == path
        assert instruments[name]["sha256"] == packs.summary.sha256_of(REPO_ROOT / path)
    assert RECORD["population"]["dev"]["sha256"] == packs.summary.sha256_of(
        REPO_ROOT / packs.DEV_NAME
    )
    assert RECORD["population"]["shot"]["sha256"] == packs.summary.sha256_of(
        REPO_ROOT / packs.SHOT_NAME
    )
    assert RECORD["population"]["gold"]["n"] == 14
    assert len(RECORD["population"]["gold"]["rows"]) == 14


def test_the_frozen_list_names_every_file_a_verdict_would_rest_on():
    frozen = set(RECORD["frozen_when_the_pod_exists"])
    for name in (
        "src/market_pulse/prompts.py",
        "src/market_pulse/scorer.py",
        packs.DEV_NAME,
        packs.SHOT_NAME,
        "results/pass1_probe_b_pack.json",
        "results/pass1_probe_b_verdict.json",
        "results/reader_gold_w1_r2.json",
        prereg.OUT_NAME,
    ):
        assert name in frozen, name
