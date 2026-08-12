"""The B′ projection: measured rates, two corners the measurement cannot close, and the cap.

This is the first sku-b projection with a completed session behind it, so the failure mode is no
longer "the estimate was invented" — it is "a measured second was quoted as if the instrument that
billed it had not changed". Every rate below was billed at an 800-token ceiling and (13)(a) raises
it to 1200; what this suite holds is that the record says so, carries both corners, and never
averages them into one number.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse import local_llm  # noqa: E402


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


writer = _script("write_sku_projection_b2")


@pytest.fixture(scope="module")
def projection():
    return json.loads(writer.RECORD.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def v4_run():
    return json.loads(writer.RUN_V4.read_text(encoding="utf-8"))


def test_every_rate_is_read_off_the_completed_session(projection, v4_run):
    marg = projection["marginals"]
    gates = v4_run["projection"]["per_gate"]
    assert marg["page_seconds_per_call"]["value"] == gates[-1]["marginal_seconds_per_call"]
    assert marg["page_seconds_per_call"]["n"] == gates[-1]["calls_done"] == 91
    assert marg["warmup_seconds"]["value"] == v4_run["projection"]["warmup_seconds"]
    assert marg["boot_seconds"]["low"] == v4_run["projection"]["boot_seconds"]
    assert projection["rate_usd_per_second"] == 0.00030669


def test_the_text_marginal_is_derived_and_the_arithmetic_reproduces(projection, v4_run):
    """The one number no single field of the record holds: the gates report one marginal across
    both legs, so the text rate is the billed total less the page leg. Re-derived here by hand
    rather than by calling the producer's function, which would only prove it is deterministic."""
    gates = v4_run["projection"]["per_gate"]
    gold = v4_run["timing"]["worker_seconds"] - v4_run["projection"]["opened_seconds"]
    by_hand = (gold - gates[-1]["calls_done"] * gates[-1]["marginal_seconds_per_call"]) / 30
    assert projection["marginals"]["text_seconds_per_row"]["value"] == round(by_hand, 4)
    assert projection["marginals"]["text_seconds_per_row"]["value"] == pytest.approx(2.82, abs=0.01)
    # a third of a page and nowhere near any ceiling — which is why the uplift barely touches it
    assert by_hand < gates[-1]["marginal_seconds_per_call"]


def test_the_boot_is_a_range_and_is_never_averaged(projection):
    """Two same-configuration readings 1.96x apart, n=1 each. An average of them would be a number
    neither session measured, and it would sit under the cap while the high corner does not."""
    boot = projection["marginals"]["boot_seconds"]
    assert boot["low"] == 205.518 and boot["high"] == 402.586
    booted = {cell["boot_seconds"] for cell in projection["corners"].values()}
    assert booted == {boot["low"], boot["high"]}
    assert (boot["low"] + boot["high"]) / 2 not in booted


def test_the_ceiling_is_a_bound_and_not_a_rate(projection):
    """4.0161 s/page was billed at 800 tokens. The pessimistic corner is 1200/800 — an upper bound,
    because no reply can generate past the ceiling — and the optimistic one leaves it alone."""
    uplift = projection["decode_uplift"]
    assert uplift["none"]["factor"] == 1.0
    assert uplift["the whole ceiling"]["factor"] == local_llm.POSITIONS_MAX_NEW_TOKENS / 800 == 1.5
    assert writer.CEILING_WAS == 800
    assert {cell["decode_uplift"] for cell in projection["corners"].values()} == {1.0, 1.5}
    assert "UPPER bound" in uplift["the whole ceiling"]["reading"]


def test_all_four_corners_are_priced_and_the_arithmetic_reproduces(projection):
    rate = projection["rate_usd_per_second"]
    assert len(projection["corners"]) == 4
    for name, cell in projection["corners"].items():
        seconds = (
            cell["boot_seconds"]
            + cell["warmup_seconds"]
            + cell["page_leg_seconds"]
            + cell["text_leg_seconds"]
            + cell["idle_tail_seconds"]
        )
        assert cell["billed_seconds"] == pytest.approx(seconds, abs=0.01), name
        assert cell["usd"] == pytest.approx(cell["billed_seconds"] * rate, abs=0.0001), name
        assert cell["usd_with_drift"] == pytest.approx(cell["usd"] * 1.03, abs=0.0001), name


def test_the_population_is_138_and_the_legs_add_up(projection):
    assert projection["population"] == {
        "pages": 108,
        "text_rows": 30,
        "elements": 138,
        "reading": projection["population"]["reading"],
    }
    assert "13)(d)" in projection["population"]["reading"]
    marg = projection["marginals"]
    cheap = projection["corners"]["boot low · decode none"]
    assert cheap["page_leg_seconds"] == pytest.approx(108 * marg["page_seconds_per_call"]["value"])
    assert cheap["text_leg_seconds"] == pytest.approx(30 * marg["text_seconds_per_row"]["value"])


def test_the_dearest_corner_fits_the_ruled_cap_and_the_bound_did_not_move(projection):
    """The finding this file surfaced, and what was ruled on it. The hard upper bound is $0.4004 —
    unchanged, because nothing about the arithmetic moved — and against (13)(d)'s $0.40 it was over
    by four hundredths of a cent. SPEC 3.17 (14)(e) set the cap at $0.65 on exactly that reading,
    so the same bound now fits with $0.2496 to spare.

    The bound is asserted BEFORE the cap here on purpose: if a later edit ever moves a corner, this
    must fail on the corner rather than pass because the cap is roomy.
    """
    verdict = projection["against_the_cap"]
    assert verdict["dearest_usd"] == 0.4004
    assert verdict["dearest_usd_without_drift"] == 0.3888
    assert verdict["cap_usd"] == 0.65
    assert verdict["fits"] is True and verdict["fits_without_drift"] is True
    assert verdict["headroom_usd"] == pytest.approx(0.2496)
    assert verdict["headroom_without_drift_usd"] == pytest.approx(0.2612)
    assert verdict["dearest_usd"] > 0.40, "and it is still over the cap (13)(d) had written"
    assert "3.17 (14)(e)" in verdict["reading"]


def test_the_cheapest_corner_is_the_one_the_measurement_actually_supports(projection):
    """Named so the overshoot is not read as "the run costs $0.40": if the boot is v4's own and the
    ceiling binds only the page v4 recorded as truncated, the session costs $0.25."""
    verdict = projection["against_the_cap"]
    assert verdict["cheapest_usd"] == 0.2534
    assert verdict["cheapest_usd"] < verdict["cap_usd"] * 0.7


def test_the_job_timeout_property_was_re_checked_at_the_new_ceiling(projection):
    """A ceiling change is exactly what could quietly break "no single job can out-bill the cap".
    It did not, and the record says the check was made rather than leaving it to be assumed."""
    block = projection["job_timeout_headroom"]
    assert block["job_timeout_s"] == 900.0
    assert block["still_twice_the_conservative_job"] is True
    assert block["twice_the_conservative_job_s"] < block["job_timeout_s"]
    assert block["longest_job_measured_rates_s"] < block["longest_job_conservative_s"]


def test_it_pins_the_records_it_read(projection):
    for path, sha in projection["pinned_inputs"].items():
        assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == sha, path
    assert set(projection["pinned_inputs"]) == {
        "results/srv2d_cost.json",
        "results/sku_b_positions_v4.json",
        "results/sku_b_positions_v3.json",
    }


def test_it_says_what_it_does_not_configure(projection):
    """The driver's constants moved at skub2-fix (Dv208). A projection that had moved them itself
    would be a run configured by the file that prices it — so the note now says where they moved
    and what holds them there, and the driver's own cap is checked against the registration rather
    than against this record."""
    driver = _script("positions_gm4_skub")
    note = projection["not_in_scope"]["the driver's constants"]
    assert "Dv208 paid" in note and "does not configure the run" in note
    assert projection["class"].startswith("PROJECTION")
    assert driver.CAP_USD == projection["cap_usd"] == 0.65
    assert "attempts.cap_usd" in projection["cap_source"]


def test_the_shipped_projection_is_the_one_this_script_writes(projection, tmp_path):
    fresh = writer.build(tmp_path / "p.json")
    for record in (fresh, projection):
        record.pop("generated_at"), record.pop("git")
    assert fresh == projection
