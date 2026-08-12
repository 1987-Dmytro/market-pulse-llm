"""The v4 session's projection: two measured page marginals that disagree by 2.9x.

v3's projection could be wrong by carrying ONE measured rate as if it were the population's. It was
— the (10)(a) gate then measured a second one on a real unsent page and refused. So the ways this
record can still be wrong are narrower and each is a test below: a marginal quietly recomputed
instead of read off the instrument that acted on it, an n that drifts from the caveat attached to
it, a 3% drift term presented as a measurement, a cap verdict that reads "it fits" without saying by
how much the input would have to move before it does not — and the loudest one, arithmetic that
disagrees with the gate that refused $0.45 on the same inputs.
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


writer = _script("write_sku_projection_v4")

PESSIMISTIC = "the registered probe, a deep unsent page"
OPTIMISTIC = "the population's drawn marginal, 17 first-six pages"


@pytest.fixture(scope="module")
def projection() -> dict:
    return json.loads(writer.RECORD.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def refused() -> dict:
    return json.loads(writer.REFUSED.read_text(encoding="utf-8"))


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
        "results/sku_b_positions_v3.json",
        "results/sku_pilot_prereg_v4.json",
    }


def test_both_page_marginals_are_read_off_the_instruments_that_acted_on_them(projection, refused):
    """Not recomputed. One is the number the (10)(a) gate refused the session with, the other is the
    number the in-run stop ended the first session with, and a second arithmetic path here could
    disagree with the one that actually decided something."""
    run = json.loads(writer.RUN.read_text(encoding="utf-8"))
    probe = projection["marginals"][PESSIMISTIC]
    drawn = projection["marginals"][OPTIMISTIC]
    assert probe["seconds_per_call"] == 14.808
    assert (
        probe["seconds_per_call"]
        == refused["warmup"]["replies"]["positions_post_gm4"]["marginal_seconds"]
    )
    assert (
        drawn["seconds_per_call"] == run["projection"]["per_gate"][0]["marginal_seconds_per_call"]
    )
    assert (probe["n"], drawn["n"]) == (1, 17)
    # the caveat and the n cannot drift apart: each names what its own sample is made of
    assert "DEEP page" in probe["what_it_is"]
    assert "10 of those 17 pages answered `[]`" in drawn["why_it_is_not_the_cap_corner"]


def test_the_text_leg_is_measured_now_and_says_it_is_one_row(projection, refused):
    """v3's projection had to BOUND the text leg by the page marginal — no positions call had ever
    been made on text. This one has a measurement, and one row is not a rate over the pack: the n
    is carried beside the number rather than left for a reader to assume."""
    text = projection["marginals"]["text, measured"]
    assert text["seconds_per_call"] == 3.862
    assert (
        text["seconds_per_call"]
        == refused["warmup"]["replies"]["positions_text_gm4"]["marginal_seconds"]
    )
    assert text["n"] == 1
    assert "One row is not a rate over the pack" in text["what_it_is"]


def test_the_pessimistic_corner_is_the_number_the_gate_refused(projection, refused):
    """The positive control, and it is free: this corner prices the same 121 elements from the same
    marginals the (10)(a) gate used. If the two ever disagree, this record's arithmetic is not the
    arithmetic that spent — and this record is what an authorisation is read from.

    Driven both ways: the equality here, and the producer's own refusal when it is broken.
    """
    gate = refused["projection"]["go_no_go"]
    assert projection["corners"][PESSIMISTIC]["total_usd"] == gate["projected_usd"] == 0.5964
    assert projection["corners"][PESSIMISTIC]["billed_seconds"] == pytest.approx(
        gate["billed_seconds"] + gate["gold_seconds"] + gate["idle_tail_seconds"], abs=1e-3
    )


def test_arithmetic_that_disagrees_with_the_gate_stops_the_write(monkeypatch, tmp_path):
    """The control for the check above. A 10% slower boot moves this record's corner and not the
    gate's recorded figure, and the producer refuses rather than writing a projection whose own
    positive control has failed."""
    moved = json.loads(writer.REFUSED.read_text(encoding="utf-8"))
    moved["projection"]["boot_seconds"] *= 1.1
    fake = tmp_path / "sku_b_positions_v3.json"
    fake.write_text(json.dumps(moved, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(writer, "REFUSED", fake)
    with pytest.raises(SystemExit, match="this record's arithmetic is not the gate's"):
        writer.build(tmp_path / "p.json")


def test_the_drift_is_a_contract_term_and_says_so(projection):
    """3% is what `docs/PROMPT-sku-b-v4-prep.md` requires the pessimistic corner to fit under the
    cap WITH. Nothing in this repository measures run-to-run drift on a serverless worker, so a
    record that presented it as an observed spread would be inventing a number."""
    drift = projection["drift"]
    assert drift["pct"] == writer.DRIFT == 0.03
    assert drift["source"] == "docs/PROMPT-sku-b-v4-prep.md deliverable 3"
    assert "not a measurement" in drift["why"]
    for cell in projection["corners"].values():
        assert cell["with_drift"]["billed_seconds"] == pytest.approx(
            cell["billed_seconds"] * 1.03, rel=1e-6
        )


def test_the_cap_verdict_is_an_inequality_and_both_corners_fit_with_the_drift(projection):
    """ "It fits" is not a decision — the decision is how far the input would have to move first.
    Every term but the page marginal is fixed here, so the break-even is computable and is carried
    per corner rather than as one number that quietly belongs to whichever corner produced it."""
    against = projection["against_the_cap"]
    assert against["cap_usd"] == 0.65
    assert against["fits_at_every_corner"] is True
    assert against["corners_over_the_cap"] == []
    pessimistic = projection["corners"][PESSIMISTIC]
    assert pessimistic["with_drift"]["total_usd"] == 0.6143
    assert pessimistic["with_drift"]["headroom_usd"] == 0.0357
    # 14.808 s/page would have to become ~16.04 before $0.65 is exhausted with the drift on
    assert pessimistic["break_even_page_marginal_seconds"] == pytest.approx(16.04, abs=0.01)
    assert pessimistic["break_even_multiple"] == pytest.approx(
        pessimistic["break_even_page_marginal_seconds"] / 14.808, abs=1e-4
    )
    assert projection["corners"][OPTIMISTIC]["with_drift"]["total_usd"] == 0.3315
    assert (
        "not a licence to run at the pessimistic corner and hope"
        in (against["what_the_headroom_is_not"])
    )


def test_the_break_even_is_the_rate_that_exhausts_the_cap(projection):
    """Recomputed by hand from the record's own terms, in the other direction: put the break-even
    marginal back into the corner and the drifted total must land ON the cap. A break-even that
    cannot be substituted back is arithmetic nobody checked."""
    cell = projection["corners"][PESSIMISTIC]
    rate = projection["rate"]["usd_per_second"]
    pages, rows = projection["population"]["pages"], projection["population"]["rows"]
    per_row = projection["marginals"]["text, measured"]["seconds_per_call"]
    per_page = cell["break_even_page_marginal_seconds"]
    seconds = (
        projection["boot"]["seconds"]
        + projection["idle_tail"]["seconds"]
        + (rows + 1) * per_row
        + (pages + 1) * per_page
    )
    assert seconds * 1.03 * rate == pytest.approx(0.65, abs=5e-4)


def test_the_population_is_the_registrations_and_not_a_count(projection):
    """121 of the wrong elements is still 121. The pages and rows are derived from the v4
    registration's own `unbought` list, which is the list the run will buy."""
    prereg = json.loads(writer.PREREG.read_text(encoding="utf-8"))
    unbought = prereg["resume"]["bought_already"]["unbought"]
    assert projection["population"]["calls"] == len(unbought) == 121
    assert projection["population"]["pages"] == sum(1 for n in unbought if n.startswith("data/"))
    assert projection["population"]["rows"] == 30
    assert projection["against_the_cap"]["cap_source"].startswith(
        "results/sku_pilot_prereg_v4.json :: attempts.cap_usd"
    )
