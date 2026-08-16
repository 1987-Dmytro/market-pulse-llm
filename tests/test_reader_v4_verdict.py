"""`scripts/score_reader_v4.py` — the five bars under v4's two scoring differences, driven.

Everything here runs at $0 and BEFORE the pod exists, for the reason probe-b's suite gives: a bar
computation that raises after the money is spent is the one failure this contract cannot absorb. The
evidence file is written by the test, so nothing below reads the run's artefacts and nothing below
is red in the commits that precede them ([[a_test_that_reads_a_shipped_artifact]]).

The fixture is IMPORTED from the v3 suite rather than copied. `perfect()` is a reader built out of
gold r2 and it is the fixture both generations are measured against; two copies of it would let the
two suites disagree about what a perfect answer is, which is the one thing they must not.

What is proved here and could not be proved before:

* bar 3 is over v2's FIVE threads again, and the six-thread column beside it DISAGREES on the same
  evidence — planted, so Dv440 is a measurement rather than a caveat;
* the vocabulary collapse is the BAR: a reader that answers the reference's «категория» everywhere
  now PASSES bar 4, and the uncollapsed column beside it fails at 5 of 14. Under v3 those two were
  the other way round;
* the collapse's SCOPE is held against the registration, in both directions.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import score_reader_v4 as scoring  # noqa: E402
import write_reader_prereg_v3 as v3prereg  # noqa: E402

from test_reader_v3_verdict import (  # noqa: E402
    A_SIGNAL,
    GOLD,
    NOISE_THREADS,
    evidence_file,
    perfect,
)

RECORD = json.loads(
    (REPO_ROOT / "results" / "prereg_reader_probe_v4.json").read_text(encoding="utf-8")
)
FIVE = ["N2", "N3", "N4", "N5", "N6"]


@pytest.fixture
def score(tmp_path, monkeypatch):
    """`build()` over an evidence file this test wrote, with no run record and no ledger beside it."""

    def run(verdicts, *, refused=None, ledger=None):
        monkeypatch.setattr(
            scoring, "EVIDENCE", evidence_file(tmp_path / "evidence.jsonl", verdicts, refused)
        )
        monkeypatch.setattr(scoring, "RUN", tmp_path / "no-such-run.json")
        path = tmp_path / "spend_reader_v4.json"
        if ledger is not None:
            path.write_text(json.dumps(ledger), encoding="utf-8")
        monkeypatch.setattr(scoring, "LEDGER", path)
        return scoring.build()

    return run


def says_the_references_word(verdicts: dict[str, dict]) -> dict[str, dict]:
    """The same perfect reader, answering «категория» wherever gold r2 ratified «категория_личное».

    The disagreement ruling 4 adjudicated, planted: the v3 prompt offers both words, so this is a
    reader that is right about the world and wrong about the vocabulary.
    """
    for body in verdicts.values():
        for row in body["per_comment"] + body["signals"]:
            if row.get("subject_type") == "категория_личное":
                row["subject_type"] = "категория"
    return verdicts


def test_a_perfect_reader_passes_every_bar_and_bar_three_is_over_five_threads(score):
    record = score(perfect())
    assert record["evidence"]["threads_read"] == 23
    assert record["gold"]["revision"] == "r2"
    for name, state in record["bars"].items():
        assert state["verdict"] == "SCORED", name
        assert state["result"]["passed"] is True, name
    bar = record["bars"]["3_noise"]
    assert bar["scored_over"] == FIVE
    assert list(bar["excluded_with_cause"]) == ["N1"]
    assert bar["result"]["threads_registered"] == 5
    assert bar["result"]["threads_with_a_verdict"] == 5
    assert bar["result"]["reachable"] is True
    # and the bars that carry the collapse say so
    assert record["bars"]["1_flagships"]["collapsed"] is True
    assert record["bars"]["4_per_comment_agreement"]["collapsed"] is True
    assert record["bars"]["2_entity_cases"]["collapsed"] is False


def test_bar_three_excludes_N1_and_the_six_thread_column_beside_it_disagrees(score):
    """The whole of Dv440 in one fixture: a signal in N1 — where the reference's own S list reads
    one — leaves the v4 bar passing and fails the reading v3 would have taken."""
    verdicts = perfect()
    verdicts[NOISE_THREADS["N1"]]["signals"].append(dict(A_SIGNAL))
    record = score(verdicts)
    assert record["bars"]["3_noise"]["result"]["signals"] == 0
    assert record["bars"]["3_noise"]["result"]["passed"] is True
    beside = record["beside_the_bars"]["3_noise_over_v3s_six_threads"]
    assert beside["scored_over"] == FIVE + ["N1"] or sorted(beside["scored_over"]) == sorted(
        FIVE + ["N1"]
    )
    assert beside["restored_by_v4"] == ["N1"]
    assert beside["result"]["signals"] == 1
    assert beside["result"]["passed"] is False


def test_the_collapse_is_the_bar_and_the_uncollapsed_reading_is_the_column(score):
    """Under v3 the reference's word was scored wrong and the collapse was a column beside it.
    Ruling 4 turns that round, and this is the fixture that shows which way each reading points."""
    record = score(says_the_references_word(perfect()))
    bar = record["bars"]["4_per_comment_agreement"]["result"]
    assert bar["rate"] == 1.0 and bar["passed"] is True
    beside = record["beside_the_bars"]["uncollapsed_vocabulary_reading"]["bars"]
    assert beside["4_per_comment_agreement"]["as_the_bar_collapsed"] == 1.0
    assert beside["4_per_comment_agreement"]["uncollapsed"] == pytest.approx(5 / 14, abs=0.001)
    # nine of the fourteen gold rows carry the ratified word, and every one of them disagrees
    # with the reference's word until the collapse closes it
    assert sum(1 for row in GOLD["per_comment"] if row["subject_type"] == "категория_личное") == 9
    # bar 1 turns on the same words and moves the same way
    assert record["bars"]["1_flagships"]["result"]["cases_answered"] == 5
    assert beside["1_flagships"]["uncollapsed"] < 5
    # and the record SAYS which of the two is the bar
    assert "COLLAPSED" in record["scoring_rules"]["vocabulary_collapse"]["is_the_bar"]
    assert record["beside_the_bars"]["rule"].startswith("REPORTED")


def test_a_refused_noise_reply_is_never_a_zero_and_an_unreachable_bar_is_not_a_pass(score):
    """Bar 3's fixed predicate, over v4's five threads. A refusal contributes nothing; with every
    one of them refused the bar is UNREACHABLE, which is not a pass."""
    one_refused = score(perfect(), refused={NOISE_THREADS["N2"]: "no JSON object in reply"})
    bar = one_refused["bars"]["3_noise"]["result"]
    assert bar["threads_registered"] == 5 and bar["threads_with_a_verdict"] == 4
    assert bar["threads_refused"] == [NOISE_THREADS["N2"]]
    assert bar["signals"] == 0 and bar["passed"] is True

    all_refused = score(
        perfect(), refused={NOISE_THREADS[name]: "no JSON object in reply" for name in FIVE}
    )
    bar = all_refused["bars"]["3_noise"]["result"]
    assert bar["threads_with_a_verdict"] == 0
    assert bar["reachable"] is False and bar["passed"] is False
    # the predicate is the registration's producer and not a second reading of it
    assert v3prereg.bar_three_over_answers({name: 0 for name in FIVE}, set())["passed"] is False


def test_the_collapse_scope_is_held_against_the_registration_in_both_directions(monkeypatch):
    """The code and the record are two statements of one rule. The premise is asserted first, so a
    refusal that fired for another reason could not pass as this check."""
    assert scoring.assert_the_collapse_is_the_registered_one(RECORD)["symmetric"] is True
    monkeypatch.setattr(scoring, "COLLAPSED_BARS", ("1_flagships",))
    with pytest.raises(SystemExit) as err:
        scoring.assert_the_collapse_is_the_registered_one(RECORD)
    assert "applies the collapse to" in str(err.value)
    monkeypatch.undo()
    monkeypatch.setattr(scoring.probe_b, "COLLAPSE", {"молочный_бренд": "бренд"})
    with pytest.raises(SystemExit) as err:
        scoring.assert_the_collapse_is_the_registered_one(RECORD)
    assert "a rule nobody registered" in str(err.value)


def test_bar_five_reads_the_v4_step_ledger_in_all_three_of_its_states(score):
    """v3's `money` pointed at THIS step's ledger — the parameter is what makes it one reading and
    not two, so all three states are driven here as well."""
    verdicts = perfect()
    absent = score(verdicts)["5_time_and_cost"]
    assert absent["state"] == "NO LEDGER" and absent["passed"] is None
    assert "spend_reader_v4.json" in absent["reason"]

    open_ledger = score(
        verdicts,
        ledger={
            "runpod_balance_at_reader_v4_start": 22.0,
            "anchored_at": "2026-08-16T18:00:00+00:00",
            "gpu_sessions": [{"at": "x", "step_spent_usd": 0.21, "note": "pod deleted"}],
        },
    )["5_time_and_cost"]
    assert open_ledger["state"] == "OPEN"
    assert open_ledger["lower_bound_usd"] == 0.21 and open_ledger["passed"] is None

    closed = score(
        verdicts,
        ledger={
            "runpod_balance_at_reader_v4_start": 22.0,
            "anchored_at": "2026-08-16T18:00:00+00:00",
            "gpu_sessions": [
                {
                    "at": "y",
                    "closed": True,
                    "settled_usd": 0.2604,
                    "window_start": "2026-08-16T18:00:00+00:00",
                    "billing_by_kind": {"pods": 0.2604, "network-volume": 0.01},
                }
            ],
        },
    )["5_time_and_cost"]
    assert closed["state"] == "CLOSED" and closed["settled_usd"] == 0.2604
    assert closed["passed"] is True  # 0.2604 <= the $0.35 cap
    assert closed["billing_by_kind"]["network-volume"] == 0.01  # recorded, outside the step


def test_the_repair_census_names_every_registered_repair_including_the_silent_ones(score):
    record = score(perfect())
    census = record["repairs"]
    registered = []
    for block in RECORD["instruments"]["parser"]["repairs"].values():
        logs = block["logs"]
        registered += [logs] if isinstance(logs, str) else list(logs)
    assert census["registered"] == sorted(registered)
    assert set(census["fired"]) == set(sorted(registered))
    assert all(count == 0 for count in census["fired"].values())  # the fixture repairs nothing
    assert census["threads_read_straight"] == 23
    assert census["unregistered_names_that_fired"] == []


def test_the_output_ceiling_reports_both_denominators(score):
    record = score(perfect())
    ceiling = record["output_ceiling"]
    assert ceiling["max_new_tokens"] == RECORD["instruments"]["ceilings"]["output_tokens"]
    assert ceiling["per_comment_rows_requested"] == 134
    assert ceiling["per_comment_rows_returned"] == len(GOLD["per_comment"])
    assert (
        ceiling["tokens_per_returned_per_comment_row"]
        != (ceiling["tokens_per_requested_per_comment_row"])
    )
    assert ceiling["finish_reason_length"] == 0
    assert len(ceiling["finish_reason_per_thread"]) == 23


def test_the_pairing_says_which_columns_are_the_same_measurement(score):
    record = score(perfect())
    bars = record["pairing"]["bars"]
    assert bars["3_noise"]["reader_v4_scored_over"] == FIVE
    assert "IS paired" in bars["3_noise"]["comparable_column"]
    assert bars["1_flagships"]["comparable_column"].startswith("probe_b_collapsed")
    assert "different golds" in bars["4_per_comment_agreement"]["comparable_column"]
    seconds = record["pairing"]["seconds"]
    assert "serverless worker seconds" in seconds["not_the_same_unit"]
    assert "boot" in seconds["not_the_same_unit"]  # the pod's other legs are NOT in this column


def test_the_scorer_is_the_registered_bytes_and_bar_three_names_its_producer(score):
    record = score(perfect())
    assert record["scorer"]["unchanged"] is True
    assert record["scorer"]["sha256"] == RECORD["instruments"]["scorer"]["sha256"]
    assert (
        record["scorer"]["bar_three_producer"]
        == "scripts/write_reader_prereg_v3.py::bar_three_over_answers"
    )
    assert "by calling it rather than by editing it" in record["scorer"]["borrowed"]
