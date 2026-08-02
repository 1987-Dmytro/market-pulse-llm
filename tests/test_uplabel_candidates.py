"""The counts the gate decides an appetite on, and the doc that quotes them.

The two ways this can be quietly wrong are a missing exclusion — a pool that offers
rows nobody may label — and a document whose tables were true when they were pasted.
Both are checked against the real corpus and the real record.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import uplabel_candidates as up  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "taxonomy-v2-prep.md"
RECORD = REPO_ROOT / "results" / "uplabel_candidates.json"
PROBE = REPO_ROOT / "results" / "relabel_probe_45d.json"


def test_the_pool_holds_no_row_that_may_not_be_labelled():
    """Already labelled, or a thread-mate of an evaluation row — either one makes a
    row unusable for training, and both are easy to leave out of a count."""
    pool, steps = up.funnel()
    ids, _, threads = up.excluded()
    assert pool, "the corpus is not empty"
    assert not {row["id"] for row in pool} & ids
    assert not {up.thread_of(row) for row in pool} & threads
    assert all(row["text"].strip() for row in pool)
    assert steps["labelable pool"] == len(pool)
    assert steps["corpus"] == sum(
        value for name, value in steps.items() if name not in ("corpus", "labelable pool")
    ) + len(pool)


def test_the_forbidden_threads_come_from_every_evaluation_file():
    _, _, threads = up.excluded()
    for path in up.EVALUATION:
        assert {up.thread_of(row) for row in up.load(path)} <= threads


def test_a_row_in_both_strata_is_counted_once_in_each_and_never_in_general():
    ironic_service = "Дякую за доставку, знову зникла, як завжди, обман 😂😂😂"
    counts = up.classify(
        [
            {"text": ironic_service},
            {"text": "Смачне морозиво"},
            {"text": "+"},
        ]
    )
    assert counts["service-rich"] == 1 and counts["sarcasm-rich"] == 1
    assert counts["in both"] == 1
    assert counts["general"] == 2  # the taste row and the bot marker
    assert counts["of the general pool, bot participation markers"] == 1


def test_a_tier_larger_than_the_pool_is_marked_unreachable():
    counts = {"service-rich": 10, "sarcasm-rich": 5, "in both": 2, "general": 20}
    rows = {row["tier"]: row for row in up.tier_table(counts)}
    assert rows["+2k"]["reachable"] is False
    assert rows["+2k"]["from the targeted strata"] == 13  # 10 + 5 - 2, counted once
    small = up.tier_table({"service-rich": 3000, "sarcasm-rich": 0, "in both": 0, "general": 9000})
    assert all(row["reachable"] for row in small)


def test_the_calibration_sample_does_not_grow_with_the_tier():
    """It is the finding, not an oversight: precision depends on the sample."""
    plan = up.calibration()
    sizes = {entry["rows"] for entry in plan["uplabel"].values()}
    assert sizes == {up.CALIBRATION_SAMPLE * len(up.STRATA)}
    assert plan["relabel"]["gated"]["hours"] == pytest.approx(
        up.CALIBRATION_SAMPLE / up.REVIEW_ROWS_PER_HOUR
    )
    low, high = plan["relabel"]["gated"]["band_hours"]
    assert low < plan["relabel"]["gated"]["hours"] < high


def test_the_doc_quotes_the_records_own_tables():
    """The generated tables, not a copy of them that was true on Sunday."""
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")
    for table in up.render(record).split("\n\n"):
        assert table in doc, f"the plan is missing or has edited:\n{table}"


def test_the_docs_probe_numbers_are_the_probes():
    """Four figures the gate will read; each one is in the record it came from."""
    run = json.loads(PROBE.read_text(encoding="utf-8"))["runs"][-1]
    doc = DOC.read_text(encoding="utf-8")
    found, cost = run["drift"], run["cost"]
    assert f"{found['changed']} rows, {found['changed_rate']:.0%}" in doc
    assert f"{found['service_rows']} rows, {found['service_prevalence']:.0%}" in doc
    assert f"${cost['usd_per_row']:.6f} per row" in doc
    for rows in (2746, 3771):
        assert f"**${rows * cost['usd_per_row']:.2f}**" in doc
