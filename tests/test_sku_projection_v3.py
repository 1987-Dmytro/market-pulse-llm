"""The resumed session's projection: the marginal is measured now, and that changes what can go wrong.

`results/sku_projection.json` could be wrong by extrapolating from a neighbouring run — and was, by
3.54x, in exactly the quantity the go/no-go multiplies. This record cannot make that mistake with
the page leg, because that leg was measured. So the ways it can still be wrong are narrower and
each is a test below: a measured rate quietly recomputed instead of read off the gate that acted on
it, an n that drifts from the caveat attached to it, an unmeasured text leg reported as a
measurement, a boot range whose ends are different transports, and a verdict that says "it fits"
without saying by how much the input would have to move before it does not.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


writer = _script("write_sku_projection_v3")


@pytest.fixture(scope="module")
def projection() -> dict:
    return json.loads(writer.RECORD.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def run() -> dict:
    return json.loads(writer.RUN.read_text(encoding="utf-8"))


def test_the_file_is_what_this_checkout_would_write(projection):
    fresh = writer.build(writer.RECORD)
    assert {k: v for k, v in fresh.items() if k not in ("generated_at", "git")} == {
        k: v for k, v in projection.items() if k not in ("generated_at", "git")
    }


def test_every_input_names_the_artifact_it_came_from(projection):
    """No number here is typed from memory, and each pinned input is re-hashed as it sits on disk:
    a projection whose sources moved reddens instead of reading as still true."""
    assert projection["pinned_inputs"]
    for path, sha in projection["pinned_inputs"].items():
        assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == sha, path
    assert set(projection["pinned_inputs"]) == {
        "results/srv2d_cost.json",
        "results/sku_b_positions.json",
        "results/sku_pilot_prereg_v3.json",
        "results/captions_gm4_visc.json",
        "results/d7_reread_srv2b.json",
    }


def test_the_page_rate_is_read_off_the_gate_that_acted_on_it(projection, run):
    """Not recomputed. `per_gate[0]` is the number the cap stop used to end the run, and a second
    arithmetic path here could disagree with the one that spent the money — with this record being
    the one an authorisation is read from."""
    gate = run["projection"]["per_gate"][0]
    page = projection["page_leg"]
    assert page["seconds_per_call"] == gate["marginal_seconds_per_call"] == 5.0772
    assert page["n"] == gate["calls_done"] == 17
    assert page["source"].endswith("per_gate[0].marginal_seconds_per_call")
    # the caveat cannot drift from the figure: the n in the prose is the n in the field
    assert f"{page['n']}" in page["caveats"]
    assert "ONE job" in page["caveats"] and "layout family" in page["caveats"]


def test_the_population_is_the_registered_121_and_not_the_whole_pilot(projection):
    """SPEC 3.17 (11)(a): the 17 already bought are never re-asked, so they are never priced."""
    prereg = json.loads(writer.PREREG.read_text(encoding="utf-8"))
    unbought = prereg["resume"]["bought_already"]["unbought"]
    assert projection["population"]["calls"] == len(unbought) == 121
    assert projection["population"]["pages"] == 91
    assert projection["population"]["rows"] == 30
    assert projection["population"]["source"].endswith("resume.bought_already.unbought")


def test_the_unmeasured_text_leg_is_bounded_and_says_so(projection):
    """No positions call has ever been made on text. The stated corner BOUNDS the 30 rows by the
    measured page marginal and the assumption is written out; srv-2d's row rate is carried beside
    it as a neighbour and is never the stated rate — it is a different instrument at a 256-token
    ceiling, which is the same class of substitution that made the first projection wrong."""
    text = projection["text_leg"]
    assert "ASSUMPTION" in text["assumption"]
    assert "cannot be slower" in text["assumption"]
    assert text["srv2d"]["seconds_per_row"] == 4.262
    assert "not a bound" in text["srv2d"]["why_not_the_stated_rate"]
    stated = [cell for cell in projection["corners"].values() if "bounded" in cell["text_rate"]]
    other = [cell for cell in projection["corners"].values() if "srv-2d" in cell["text_rate"]]
    assert stated and other
    # the bound is the more expensive reading, which is the safe direction for a cap
    assert min(cell["text_leg_usd"] for cell in stated) > max(
        cell["text_leg_usd"] for cell in other
    )


def test_the_warm_up_is_priced_at_the_page_marginal_and_never_at_a_warm_up(projection):
    """The finding of the interrupted session, applied to its own successor: a warm-up marginal
    does not price a gold call, so (11)(c)'s two real inputs are priced at the measured page rate."""
    assert projection["warmup"]["calls"] == 2
    per_page = projection["page_leg"]["seconds_per_call"]
    for cell in projection["corners"].values():
        assert cell["warmup_seconds"] == pytest.approx(2 * per_page, abs=1e-3)


def test_the_boot_range_names_what_each_end_measured(projection):
    """The ends are not the same measurement: one is this endpoint class yesterday, one is another
    serverless config, one is a POD — which pays no container start and is a floor for a different
    thing. A range whose ends are different transports has to say so, or the cheapest number reads
    as an expectation."""
    boots = projection["boot"]
    named = {key: cell for key, cell in boots.items() if isinstance(cell, dict)}
    assert len(named) == 3
    for cell in named.values():
        assert cell["transport"] and cell["source"] and cell["seconds"] > 0
    pod = next(cell for key, cell in named.items() if "pod" in key)
    assert "not a serverless worker" in pod["transport"]
    assert pod["seconds"] == 175.791
    assert named["measured on this endpoint class yesterday"]["seconds"] == 391.369
    # the boot regression is named rather than assumed away by quietly using the cheaper figure
    assert "worker-boot.log" in boots["regression_not_diagnosed"]


def test_the_arithmetic_of_every_corner_re_derives_by_hand(projection):
    """boot + 2 warm-up calls + 91 pages + 30 rows + the idle tail, at the settled rate. Computed
    here from the record's own inputs rather than from the writer's function: a test that called
    `corner()` would agree with it by construction."""
    rate = projection["rate"]["usd_per_second"]
    per_page = projection["page_leg"]["seconds_per_call"]
    srv2d = projection["text_leg"]["srv2d"]["seconds_per_row"]
    idle = projection["idle_tail"]["seconds"]
    for name, cell in projection["corners"].items():
        text_rate = per_page if "bounded" in cell["text_rate"] else srv2d
        seconds = cell["boot_seconds"] + 2 * per_page + 91 * per_page + 30 * text_rate + idle
        assert cell["billed_seconds"] == pytest.approx(seconds, abs=1e-3), name
        assert cell["total_usd"] == pytest.approx(seconds * rate, abs=1e-4), name
        assert cell["headroom_usd"] == pytest.approx(cell["cap_usd"] - cell["total_usd"], abs=1e-4)
        assert cell["fits"] is (cell["total_usd"] <= cell["cap_usd"])


def test_the_cap_is_the_registered_one_and_the_verdict_is_an_inequality(projection):
    """ "It fits" is not a decision — how far the input can move before it stops fitting is. The
    interrupted session's error was 3.54x in exactly the quantity this break-even is stated in, so
    the margin is checkable rather than reassuring."""
    prereg = json.loads(writer.PREREG.read_text(encoding="utf-8"))
    against = projection["against_the_cap"]
    assert against["cap_usd"] == prereg["attempts"]["cap_usd"] == 0.45
    assert against["fits_at_every_corner"] is True
    assert against["corners_over_the_cap"] == []

    rate = projection["rate"]["usd_per_second"]
    idle = projection["idle_tail"]["seconds"]
    worst = max(projection["corners"].values(), key=lambda cell: cell["total_usd"])
    assert against["highest_usd"] == worst["total_usd"]
    # at the break-even marginal the worst corner lands exactly on the cap: 2 warm-up + 91 + 30
    # calls all priced at it, everything else fixed
    marginal = against["break_even_page_marginal_seconds"]
    seconds = worst["boot_seconds"] + idle + (2 + 91 + 30) * marginal
    assert seconds * rate == pytest.approx(against["cap_usd"], abs=1e-4)
    assert marginal > projection["page_leg"]["seconds_per_call"]


def test_it_does_not_claim_to_replace_the_gate_or_the_first_projection(projection):
    """Two things this record is not. The go/no-go re-prices from the session's OWN warm-up before
    the first gold call and is what refuses; and `results/sku_projection.json` is what the $0.35 cap
    was set against, so it stands as history rather than being rewritten under a new answer."""
    assert "3.17 (10)(a)" in projection["against_the_cap"]["what_this_is_not"]
    assert "results/sku_projection.json" in projection["class"]
    assert (REPO_ROOT / "results" / "sku_projection.json").exists()
    assert "verdict" not in projection, "a projection that scores itself is not one"
