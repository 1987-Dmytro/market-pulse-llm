"""The cycle-2 batch projection — every citation re-resolved, every sum re-added.

A projection is only worth the sources it names, so the load-bearing tests here are the boring
ones: the record is what the producer writes today, and each `source` string is walked by a SECOND
resolver written from scratch below. Two readers, one string — a citation nobody re-resolves is
prose with a colon in it.
"""

import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import projection_batch_cycle2 as projection  # noqa: E402

RECORD = REPO_ROOT / "results" / "batch_cycle2_projection.json"
CONTRACT = REPO_ROOT / "docs" / "PROMPT-cycle2-prep-a.md"


@pytest.fixture(scope="module")
def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def resolve(dotted: str):
    """`results/x.json :: a.b[-1].c` → the value. Written from scratch, not `projection_5c2.dig`.

    The point of the second implementation: if the record's `source` strings and the resolver that
    wrote them share a bug, one reader cannot see it.
    """
    where, path = dotted.split(" :: ")
    data = json.loads((REPO_ROOT / where).read_text(encoding="utf-8"))
    for step in re.findall(r"[^.\[\]]+|\[-?\d+\]", path):
        data = data[int(step[1:-1])] if step.startswith("[") else data[step]
    return data


def citations(node, path="") -> list[tuple[str, dict]]:
    """Every {value, source} pair anywhere in the record, with where it sits."""
    found = []
    if isinstance(node, dict):
        if "value" in node and " :: " in str(node.get("source", "")):
            found.append((path, node))
        for key, value in node.items():
            found += citations(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found += citations(value, f"{path}[{index}]")
    return found


def test_the_committed_record_is_what_the_producer_writes_today(tmp_path):
    """No clock and no git block, so the record IS its own determinism pair."""
    out = tmp_path / "again.json"
    assert projection.main(["--out", str(out)]) == 0
    assert out.read_bytes() == RECORD.read_bytes()
    assert "at" not in json.loads(out.read_text(encoding="utf-8"))


def test_every_cited_number_re_resolves_to_the_file_it_names(record):
    found = citations(record)
    assert len(found) >= 15, "the record stopped citing its sources"
    for where, cited in found:
        assert resolve(cited["source"]) == cited["value"], where


def test_every_price_names_the_sample_it_was_measured_on(record):
    """`.claude/rules/registrations-and-draws.md`: a rate is a property of its SAMPLE."""
    for name, price in record["prices"].items():
        assert price["sample"], name
        assert price["why"], name


def test_the_anchors_are_on_disk_and_the_two_extras_are_declared(record):
    anchors = record["provenance"]["anchors"]
    named = {entry["path"] for entry in anchors if entry["named_by_the_contract"]}
    assert named == {projection.rel(path) for path in projection.CONTRACT_ANCHORS}
    extra = {entry["path"] for entry in anchors if not entry["named_by_the_contract"]}
    assert extra == {projection.rel(projection.RUN_COMMENTS), projection.rel(projection.WINDOW)}
    for entry in anchors:
        assert (REPO_ROOT / entry["path"]).exists(), entry["path"]
        assert entry["why"], entry["path"]


def test_the_memory_bound_is_the_verdicts_own_sentence(record):
    """The four figures of (a) are parsed out of the blocker, and the quote travels with them."""
    oom = record["a_batch_candidates"]["recorded_oom"]
    assert oom["quote"] == resolve(oom["source"])
    read, derivable = oom["read"], record["a_batch_candidates"]["derivable"]

    demand = read["allocated_gib"] + read["requested_gib"]
    assert derivable["demand_at_the_failing_step_gib"] == round(demand, 3)
    assert derivable["above_the_weights_gib"] == round(demand - read["weights_at_rest_gib"], 3)
    per_row = (demand - read["weights_at_rest_gib"]) / read["batch_size"]
    largest = derivable["largest_batch_the_inequality_admits"]
    assert largest * per_row <= derivable["headroom_on_24gb_above_the_weights_gib"]
    assert (largest + 1) * per_row > derivable["headroom_on_24gb_above_the_weights_gib"]
    assert derivable["ruled_out"] == [n for n in (3, 4, 8, 16) if n > largest]


def test_a_rewritten_blocker_stops_the_producer(monkeypatch):
    """The negative control: the figures live in prose, so a reworded sentence must REFUSE.

    Without it the regex could quietly stop matching and (a) would print a bound from a sentence
    that no longer says it.
    """
    monkeypatch.setattr(
        projection, "load", lambda _path: {"blocker": "the worker ran out of memory"}
    )
    with pytest.raises(SystemExit, match="no longer carries"):
        projection.oom_reading()


def test_a_memory_reading_in_another_unit_is_refused():
    assert projection.mib("24564 MiB") == 24564
    with pytest.raises(SystemExit, match="not comparable"):
        projection.mib("24 GB")


def test_the_savings_and_the_break_even_are_one_arithmetic(record):
    """Every dollar in (d) re-adds from the row price, and break-even is its own inverse."""
    price = record["d_break_even"]["row_price_usd"]
    arms = {
        arm["rows_per_arm"]: arm["with_a_batch_1_control_usd"]
        for arm in record["c_measurement_session_cost"]["arms"]
    }
    for label, depth in record["d_break_even"]["depths"].items():
        share = 0.30 if label == "minus_30_pct" else 0.50
        delta = depth["saving_per_row_usd"]
        assert delta == round(price * share, 7)
        for name, usd in depth["saving_by_volume_usd"].items():
            rows = record["d_break_even"]["volumes"][name]["rows"]
            assert usd == round(rows * delta, 4)
        for key, rows in depth["break_even_rows"].items():
            cost = arms[int(key.split("_")[0])]
            assert rows * delta >= cost and (rows - 1) * delta < cost, key


def test_the_arm_costs_are_the_fixed_cost_plus_the_rows(record):
    fixed = record["c_measurement_session_cost"]["fixed"]["usd"]
    price = record["c_measurement_session_cost"]["per_row_usd"]
    for arm in record["c_measurement_session_cost"]["arms"]:
        rows = arm["rows_per_arm"]
        assert arm["one_arm_usd"] == round(rows * price, 4)
        assert arm["candidate_only_usd"] == round(fixed + rows * price, 4)
        assert arm["with_a_batch_1_control_usd"] == round(fixed + 2 * rows * price, 4)
        # the detection column is what says a 24-row arm cannot see the defect that killed batch 16
        assert arm["blind_to_the_identity_defect"] == pytest.approx(
            resolve("results/batch_5b2_verdict.json :: salvage.row_agreement_vs_batch_1.rate")
            ** rows,
            abs=5e-5,
        )


def test_the_one_number_no_record_holds_is_the_contracts_own(record):
    """HISTORY_ROWS is not read out of a result file — so it is grepped back out of both places
    that state it, or the projection is quoting itself."""
    spelled = f"{projection.HISTORY_ROWS:,}".replace(",", " ")
    assert spelled in CONTRACT.read_text(encoding="utf-8")
    assert spelled in (REPO_ROOT / "scripts" / "run_5c2.py").read_text(encoding="utf-8")
    assert record["d_break_even"]["volumes"]["history_backlog"]["rows"] == projection.HISTORY_ROWS


def test_the_record_says_what_it_cannot_say(record):
    """The contract's fourth kind of answer: marked NOT MEASURABLE, never estimated into a number.

    Asserted because it is the property a projection loses silently — a bound that has quietly
    become a figure reads exactly like a measurement.
    """
    assert "no prereg is written" in record["asks"]
    unknown = record["a_batch_candidates"]["not_measurable"]
    assert unknown["claim"] and len(unknown["why"]) >= 3
    assert "NOT MEASURABLE" in json.dumps(record, ensure_ascii=False)
    assert "NOT ANSWERED HERE" in json.dumps(record["d_break_even"], ensure_ascii=False)
