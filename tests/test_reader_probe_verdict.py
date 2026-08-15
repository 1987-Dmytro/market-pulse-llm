"""`results/reader_probe_verdict.json` — what the probe bought, and what it did NOT score.

The record's whole job is to keep a stop honest: four bars that were never reached must read
UNSCORED with the reason, never 0.0, and the parse outcomes must stay apart from «no signal».
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import score_reader_probe as scoring  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

RECORD_PATH = REPO_ROOT / "results" / "reader_probe_verdict.json"
RECORD = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
PREREG = json.loads(
    (REPO_ROOT / "results" / "prereg_reader_probe.json").read_text(encoding="utf-8")
)
EVIDENCE = [
    json.loads(line)
    for line in (REPO_ROOT / "results" / "reader_probe_w1.jsonl").read_text("utf-8").splitlines()
    if line
]


def test_the_committed_verdict_is_what_the_producer_writes_today(tmp_path):
    out = tmp_path / "again.json"
    assert scoring.main(["--out", str(out)]) == 0
    assert out.read_bytes() == RECORD_PATH.read_bytes()


def test_a_bar_that_was_never_reached_reads_unscored_and_says_why():
    """Not 0.0 and not «failed»: the go/no-go stopped the run before the threads carrying these
    cases were bought, and a bar computed over the three that WERE read is a number about another
    sample ([[an_absolute_bar_needs_a_reachability_state]] one layer out)."""
    assert RECORD["outcome"] == "STOP"
    assert RECORD["evidence"]["threads_read"] == 3
    assert RECORD["evidence"]["threads_registered"] == 111
    for name, state in RECORD["bars"].items():
        assert state["verdict"] == "UNSCORED", name
        assert state["cases_in_the_evidence"] == [], name
        assert state["cases_not_read"], name
        assert "stopped the run before the population was bought" in state["reason"]
        assert state["scorer"].startswith("reader_")


def test_the_refusals_are_counted_by_cause_and_never_as_an_empty_answer():
    """All three replies were refused for one reason, and `no_signal` counts PARSED replies only —
    an unreadable verdict piling up in the empty class is the failure this column exists to stop
    ([[the_empty_class_eats_the_parse_failures]])."""
    replies = RECORD["replies"]
    assert replies["parsed"] + replies["refused"] == len(EVIDENCE) == 3
    assert replies["refusals_by_cause"] == {"entities is not a list": 3}
    assert replies["no_signal"] == 0 and replies["signal_bearing"] == 0
    assert replies["finish_reason_length"] == 0, "no verdict hit the token ceiling"


def test_the_evidence_carries_the_rendering_and_the_reply_of_every_thread_bought():
    for row in EVIDENCE:
        assert len(row["rendering_sha256"]) == 64
        assert row["reply"].strip().startswith("{")
        assert row["seconds"]["worker"] > 0
        assert row["prompt_sha256"] == PREREG["instruments"]["prompt_sha256"]
        assert row["task"] == "reader_thread_gm4"
    assert {row["thread"] for row in EVIDENCE} == {
        "@mandziak:3701",
        "@VARUS_channel:10451",
        "@tarilka_malyuka:715",
    }


def test_the_measured_rate_is_the_one_the_gate_read():
    """54.8 s a thread against the census's lower bound of 4.247 — the number this probe was
    bought for, and the reason the gate said STOP."""
    gate = RECORD["go_no_go"]
    assert gate["verdict"] == "STOP"
    assert gate["warm_up"]["threads"] == 3
    assert RECORD["non_gating"]["seconds_per_thread"] > 50
    assert gate["projections"]["binding"]["usd"] > RECORD["go_no_go"]["ceilings"]["cap_usd_all_in"]
    assert RECORD["scorer"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "src" / "market_pulse" / "scorer.py"
    )
