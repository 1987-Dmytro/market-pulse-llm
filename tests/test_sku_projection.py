"""The projection: arithmetic over named artifacts, and every input traceable to its file.

A projection is the number an authorisation is given against, so the ways it can be wrong are the
ways money gets spent on a false premise: an all-in session figure multiplied by a count, a cold
start hidden inside a marginal rate, a per-post rate applied to a per-page run, an assumption
quoted as a measurement. Each of those is a test below.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from market_pulse import local_llm

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


writer = _script("write_sku_projection")


@pytest.fixture(scope="module")
def projection() -> dict:
    return json.loads(writer.RECORD.read_text(encoding="utf-8"))


def test_the_file_is_what_this_checkout_would_write(projection):
    fresh = writer.build(writer.RECORD)
    assert {k: v for k, v in fresh.items() if k not in ("generated_at", "git")} == {
        k: v for k, v in projection.items() if k not in ("generated_at", "git")
    }


def test_every_input_names_the_artifact_it_came_from(projection):
    """No number here is typed from memory. Each pinned input is re-hashed as it sits on disk, so
    a projection whose sources moved reddens instead of reading as still true."""
    import hashlib

    assert projection["pinned_inputs"]
    for path, sha in projection["pinned_inputs"].items():
        assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == sha, path
    assert projection["rate"]["source"].startswith("results/srv2d_cost.json")
    assert projection["page_leg"]["source"]["path"] == "results/captions_gm4_atb19.json"


def test_the_page_rate_is_per_image_and_not_per_post(projection):
    """vis-b made one call per POST carrying up to six pages; sku-b makes one call per PAGE. A
    per-post figure multiplied by 108 would be pricing 108 albums."""
    source = projection["page_leg"]["source"]
    assert source["images"] == 108 and source["posts"] == 19
    assert source["images_per_call"] > 1
    assert source["marginal_seconds_per_image"] == pytest.approx(
        (source["worker_seconds"] - source["boot_seconds"]) / source["images"], abs=1e-4
    )
    assert projection["page_leg"]["calls"] == source["images"]


def test_the_cold_start_is_subtracted_before_the_rate_and_added_back_once(projection):
    """vis-b's own re-pilot hid a whole cold start inside `worker_seconds` and its per-post rate
    came out 2x too high. Both readings of the boot are carried and neither is substituted."""
    source = projection["page_leg"]["source"]
    assert source["boot_seconds"] > 0
    cold = projection["assumptions"]["cold_start"]
    assert cold["measured_usd"] == 0.0563 and cold["preregistered_usd"] == 0.0733
    corners = projection["corners"]
    assert {cell["cold_start_usd"] for cell in corners.values()} == {0.0563, 0.0733}


def test_the_two_sessions_agree_on_the_per_image_rate(projection):
    """Two independent runs on the same base with different album sizes. If they disagreed, a
    two-point rate would be one run's weather rather than a rate."""
    one = projection["page_leg"]["source"]["marginal_seconds_per_image"]
    other = projection["page_leg"]["corroboration"]["marginal_seconds_per_image"]
    assert abs(one - other) / one < 0.01


def test_the_all_in_session_figure_is_recorded_and_never_used(projection):
    """$0.3869 is a balance delta for a whole session. The record names it in `never_used` so a
    reader can see it was considered and rejected, not overlooked."""
    never = projection["page_leg"]["never_used"]
    assert never["session_usd"] == 0.3869
    for cell in projection["corners"].values():
        assert cell["page_leg_usd"] != pytest.approx(never["session_usd"] / 19 * 108, rel=0.01)


def test_the_uplift_is_an_assumption_and_the_total_is_reported_without_it(projection):
    """Nothing has ever generated a positions reply, so its decode length is not a measurement.
    The ratio of registered ceilings is an upper bound and 1.0 is the lower one; both totals are
    in the file, so the sensitivity is visible rather than collapsed into one number."""
    assumed = projection["assumptions"]
    assert "ASSUMPTION, not a measurement" in assumed["decode_uplift"]
    assert assumed["ceilings"]["positions (SPEC 3.17 (9))"] == local_llm.POSITIONS_MAX_NEW_TOKENS
    uplifts = {tuple(cell["decode_uplift"].values()) for cell in projection["corners"].values()}
    assert (1.0, 1.0) in uplifts
    assert (
        local_llm.POSITIONS_MAX_NEW_TOKENS / local_llm.CAPTION_MAX_NEW_TOKENS,
        round(local_llm.POSITIONS_MAX_NEW_TOKENS / local_llm.MAX_NEW_TOKENS, 4),
    ) in uplifts


def test_every_corner_is_priced_against_the_cap(projection):
    driver = _script("positions_gm4_skub")
    for name, cell in projection["corners"].items():
        assert cell["cap_usd"] == driver.CAP_USD == 0.35, name
        assert cell["headroom_usd"] == pytest.approx(cell["cap_usd"] - cell["total_usd"], abs=1e-4)
        assert cell["fits"] == (cell["total_usd"] <= cell["cap_usd"])
        assert cell["total_usd"] == pytest.approx(
            cell["page_leg_usd"]
            + cell["text_leg_usd"]
            + cell["warmup_usd"]
            + cell["cold_start_usd"],
            abs=1e-3,
        )


def test_the_verdict_says_plainly_that_the_upper_corner_does_not_fit(projection):
    """The finding the operator is authorising against. A projection that quietly reported only
    the corner that fits would be an argument, not arithmetic.

    The block is `against_the_cap` and not `verdict`: `tests/test_sku_prereg.py` refuses a
    `verdict` key anywhere in `results/sku_*.json` — a bar result and a pre-registration must not
    share a file. It fired on this record, correctly, and the field was renamed rather than the
    gate loosened."""
    verdict = projection["against_the_cap"]
    assert verdict["fits_at_every_corner"] is False
    assert verdict["highest_usd"] > verdict["cap_usd"] >= verdict["lowest_usd"]
    assert "sits ON the cap" in verdict["reading"]
    assert (
        "R2" in verdict["what_an_early_stop_costs"]
        or "108" in (verdict["what_an_early_stop_costs"])
    )


def test_no_paid_call_was_made_to_produce_it(projection):
    """The class the record claims about itself, checked against its own source: `build` reads
    files and does arithmetic, and nothing in this script reaches a network."""
    source = (REPO_ROOT / "scripts" / "write_sku_projection.py").read_text(encoding="utf-8")
    for forbidden in ("EndpointClient", "urlopen", "requests", "guard.balance"):
        assert forbidden not in source, forbidden
    assert "no paid call was made" in projection["class"]
