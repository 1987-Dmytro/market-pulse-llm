"""The projection's own gate: every figure in it is re-read out of the file it cites.

`docs/PROMPT-5c2-prep-c2.md` deliverable 2 asks for exactly this — "a test that asserts every
projected number's `source` path exists and the quoted figure matches the file it cites". The
record is walked, not sampled: a citation added later is checked by the same loop, and a source
that moved leaves a stale copy that fails here rather than in a briefing.
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import positions_gm4_skub as driver  # noqa: E402
import projection_5c2 as projection  # noqa: E402
import runpod_guard as guard  # noqa: E402

RECORD = json.loads(projection.RECORD.read_text(encoding="utf-8"))


def dig(data, dotted: str):
    """A second implementation of `projection.dig`, on purpose: two readers, one source string."""
    for step in re.findall(r"[^.\[\]]+|\[-?\d+\]", dotted):
        data = data[int(step[1:-1])] if step.startswith("[") else data[step]
    return data


def walk(node):
    """Every dict in the record, so a citation cannot hide by being nested one level deeper."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


def cited():
    return [node for node in walk(RECORD) if "source" in node and "value" in node]


def quoted():
    return [node for node in walk(RECORD) if "source" in node and "quote" in node]


def test_the_record_carries_citations_at_all():
    """The negative control for the two loops below: an empty walk would pass them both."""
    assert len(cited()) >= 6
    assert len(quoted()) >= 1


def test_every_cited_number_is_the_one_its_file_holds():
    for node in cited():
        path, _, dotted = node["source"].partition(" :: ")
        assert (REPO_ROOT / path).exists(), f"{path} is cited and not on disk"
        found = dig(json.loads((REPO_ROOT / path).read_text(encoding="utf-8")), dotted)
        assert found == node["value"], f"{node['source']}: record {node['value']}, file {found}"


def test_every_quoted_line_is_in_the_file_it_names():
    for node in quoted():
        path = REPO_ROOT / node["source"]
        assert path.exists(), f"{node['source']} is quoted and not on disk"
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
        assert node["quote"] in lines, f"{node['source']} no longer holds: {node['quote']}"


def test_every_source_path_in_the_record_exists():
    """Including the ones with no `value` beside them — a block that names a file it cannot open
    is a citation a reader would trust and nothing would check.

    The path is the LAST token before ` :: `, not everything before it: several `why` strings name
    a field mid-sentence, and a greedy parse would hand this loop half a paragraph to open.
    """
    named = 0
    for node in walk(RECORD):
        for value in node.values():
            if not isinstance(value, str):
                continue
            for path in re.findall(r"(\S+) :: ", value):
                named += 1
                assert (REPO_ROOT / path).exists(), f"{path} is named and not on disk"
    assert named >= 8, "the loop found no citations to check"


def test_the_window_is_the_shipped_census_by_sha():
    """The projection prices ONE census. A record pointing at a file that has since been rewritten
    would project a window nobody measured."""
    import hashlib

    window = RECORD["window"]
    census = json.loads((REPO_ROOT / window["path"]).read_text(encoding="utf-8"))
    assert window["sha256"] == hashlib.sha256((REPO_ROOT / window["path"]).read_bytes()).hexdigest()
    assert window["anchor"] == census["anchor"]["anchor"]
    assert window["comments_unanswered"] == census["totals"]["comments_unanswered_in_window"]
    assert window["leaflet_pages"] == census["totals"]["leaflet_pages_in_window"]


def test_the_comment_legs_arithmetic_recomputed_by_hand():
    """5 075 rows at $1.4281 per 1 000, plus the 60 s idle tail, times the 3% drift."""
    leg = RECORD["legs"]["comment"]
    rate = RECORD["rate"]["value"]
    corner = leg["corners"]["unit_cost"]

    expected = (5075 * 1.4281 / 1000 + 60.0 * rate) * 1.03
    assert leg["window_rows"] == 5075
    assert corner["value"] == 1.4281
    assert corner["usd_with_drift"] == round(expected, 4) == 7.4840


def test_the_leaflet_legs_arithmetic_recomputed_by_hand():
    """78 pages at 4.2794 s, plus a 230.118 s boot, 18.811 s of warm-up and the 60 s tail."""
    leg = RECORD["legs"]["leaflet_page"]
    rate = RECORD["rate"]["value"]
    corner = leg["corners"]["marginal_plus_boot"]

    seconds = 78 * 4.2794 + 230.118 + 18.811 + 60.0
    assert leg["window_pages"] == 78
    assert corner["billed_seconds"] == round(seconds, 1) == 642.7
    assert corner["usd_with_drift"] == round(seconds * rate * 1.03, 4) == 0.2030


def test_the_page_marginal_is_measured_over_the_pages_and_not_over_the_138():
    """The briefing says the skub2 session «bought 138 pages»; the record says 138 SOURCES, 108 of
    them pages. The marginal cited is the gate whose `calls_done` is that 108."""
    skub2 = json.loads((REPO_ROOT / "results" / "sku_b_positions_skub2.json").read_text("utf-8"))
    gate = skub2["projection"]["per_gate"][-1]
    population = RECORD["legs"]["leaflet_page"]["paid_measurement"]["population"]

    assert gate["calls_done"] == population["pages_sent"] == 108
    assert population["asked"] == 138 and population["text_rows"] == 30
    assert RECORD["legs"]["leaflet_page"]["seconds_per_page"] == gate["marginal_seconds_per_call"]


def test_the_pod_rates_appear_only_in_the_block_that_says_they_are_context():
    """SPEC 3.18 (4) names 0.5993 and 0.4611 as POD numbers that are not this runtime's. They may
    be printed as context and may not reach a headline row — so every occurrence in the record is
    inside the block that says so, twice each: the field, and the amendment's own sentence."""
    whole = json.dumps(RECORD, ensure_ascii=False)
    block = json.dumps(RECORD["context_not_a_headline"], ensure_ascii=False)

    for number in ("0.5993", "0.4611"):
        assert block.count(number) >= 1
        assert whole.count(number) == block.count(number), f"{number} escaped the context block"


def test_no_leg_is_marked_no_paid_measurement_and_the_unused_candidate_is_named():
    """Both legs have a paid serverless measurement, so the marker is empty — and the candidate
    that was read and did NOT become a source is named with what it actually holds."""
    block = RECORD["no_paid_measurement"]
    parity = json.loads(
        (REPO_ROOT / block["candidate_read_and_not_used"]["path"]).read_text("utf-8")
    )

    assert block["legs"] == []
    assert block["candidate_read_and_not_used"]["block"] == "diagnostics"
    # the claim in that block, checked: the file carries rows and failures and no price at all
    assert "usd" not in json.dumps(parity["diagnostics"])
    assert [entry["rows"] for entry in parity["diagnostics"]["failures"]] == [400, 250, 108]


def test_every_cap_row_stays_under_its_cap_at_the_rate_it_was_solved_for():
    """The row count comes from the conservative rate, so that is the number that must fit. The
    wall clock comes from the marginal one — one field from each model, each saying which."""
    for row in RECORD["caps"]:
        assert row["at_the_conservative_rate"]["usd_with_drift"] <= row["cap_usd"]
        assert row["at_the_marginal_rate"]["usd_with_drift"] <= row["cap_usd"]
        assert row["buys"]["comments_optimistic"] >= row["buys"]["comments_conservative"]


def test_every_cap_row_carries_seconds_and_a_job_count():
    """A cap that fits in dollars can still be a session the transport cannot run in one sitting:
    one worker, a 900 s execution timeout, and the seconds are serial."""
    for row in RECORD["caps"]:
        marginal = row["at_the_marginal_rate"]
        assert marginal["billed_seconds"] > 0 and marginal["hours"] > 0
        assert marginal["jobs_at_the_execution_timeout"] >= marginal["billed_seconds"] / 900
    assert RECORD["job_shape"]["execution_timeout_s"] == driver.JOB_TIMEOUT_S
    assert RECORD["job_shape"]["workers_max"] == 1


def test_the_budget_is_the_ledgers_last_logged_reading_and_the_guards_own_cap():
    """Read, never restated: the cap comes from the line that ENFORCES it and the remainder from
    the ledger's last entry, which is what it is called in the record."""
    ledger = json.loads((REPO_ROOT / "results" / "spend_phase4.json").read_text("utf-8"))
    last = ledger["sessions"][-1]
    budget = RECORD["budget"]

    assert budget["phase_cap_usd"] == guard.PHASE_CAP_USD == ledger["phase4_cap_usd"]
    assert (budget["spent_usd"], budget["remaining_usd"]) == (
        last["spent_usd"],
        last["remaining_usd"],
    )
    assert budget["read_at"] == last["at"]


def test_the_whole_window_does_not_fit_and_the_record_says_so():
    """The finding this contract ends on, asserted rather than described: if a later re-run makes
    it fit, this test is what makes somebody notice the STOP has changed shape."""
    whole = RECORD["whole_window"]

    assert whole["usd_with_drift"] > whole["remaining_usd"]
    assert whole["fits"] is False


def test_a_rerun_writes_the_same_bytes(tmp_path):
    """The projection is a pure function of the files it cites — no clock, no sampling."""
    projection.main(["--out", str(tmp_path / "first.json")])
    projection.main(["--out", str(tmp_path / "second.json")])

    assert (tmp_path / "first.json").read_bytes() == (tmp_path / "second.json").read_bytes()
