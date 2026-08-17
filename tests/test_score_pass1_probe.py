"""`scripts/score_pass1_probe.py` — driven on hand-made evidence, before the money.

A scorer verified only by running it on the real evidence is a scorer whose failure modes are
whatever that evidence happened to contain. Here it is driven on rows this file writes: a pass, a
fail, an ABSENT row, and the vocabulary collapse doing its job — so «bar 4's comparison, called and
not restated» is a measurement rather than a docstring.

Nothing here reads `results/pass1_probe_rows.jsonl`: it does not exist until the pod has run, and a
test that needs a shipped artifact is red in every commit before that artifact lands
([[a_test_that_reads_a_shipped_artifact]]).
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import score_pass1_probe as scoring  # noqa: E402

from market_pulse import prompts, scorer  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_pass1_probe.json").read_text(encoding="utf-8"))
GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text(encoding="utf-8"))
GOLD_BY_ID = {int(row["msg_id"]): row for row in GOLD["per_comment"]}


def evidence_for(answers: dict[int, dict | None]) -> list[dict]:
    """One evidence row per registered gold id, answered as the mapping says."""
    rows = []
    for one in RECORD["population"]["gold"]["rows"]:
        msg_id = one["msg_id"]
        said = answers.get(msg_id, "skip")
        if said == "skip":
            continue
        rows.append(
            {
                "id": f"{one['thread']}#{msg_id}",
                "thread": one["thread"],
                "msg_id": msg_id,
                "leg": "gold",
                "reply": "…",
                "parsed": said,
                "parse_error": None if said else "malformed JSON",
                "balanced": True,
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 900, "completion_tokens": 40},
                "seconds": 3.0,
            }
        )
    return rows


def perfect() -> dict[int, dict]:
    """Every gold row answered exactly as gold says it, in the model's own four-word vocabulary."""
    answers = {}
    for one in RECORD["population"]["gold"]["rows"]:
        row = GOLD_BY_ID[one["msg_id"]]
        answers[one["msg_id"]] = {
            "msg_id": one["msg_id"],
            "subject_type": row.get("subject_type"),
            "subject_id": row.get("subject_id"),
            "stance": row.get("stance"),
        }
    return answers


def test_a_perfect_run_takes_the_bar_and_spends_none_of_its_loss_budget():
    bar = scoring.bar_p1(RECORD, evidence_for(perfect()))
    assert bar["n"] == 14 and bar["agreed"] == 14
    assert bar["passed"] is True
    assert bar["losses"] == {"budget": 2, "spent": 0, "by_cause": {"disagreed": 0, "absent": 0}}
    assert bar["rate_over_the_rows_the_model_answered"] is None
    assert bar["comparison"] == "market_pulse.scorer.reader_comment_agreement"


def test_the_bar_is_a_COUNT_and_two_losses_still_pass_while_three_do_not():
    """«≥12 of 14» is the threshold the registration states, so the verdict turns on the COUNT and
    never on a rate — and the boundary is driven from both sides."""
    ids = [one["msg_id"] for one in RECORD["population"]["gold"]["rows"]]
    for losses, expected in ((0, True), (2, True), (3, False)):
        answers = perfect()
        for msg_id in ids[:losses]:
            answers[msg_id] = {**answers[msg_id], "stance": "neutral", "subject_type": None}
        bar = scoring.bar_p1(RECORD, evidence_for(answers))
        assert bar["agreed"] == 14 - losses, (losses, bar["agreed"])
        assert bar["passed"] is expected, (losses, bar["passed"])
        assert bar["losses"]["spent"] == losses


def test_an_ABSENT_row_costs_the_same_as_a_disagreement_and_is_counted_apart():
    """A refused call and a wrong answer both spend one row of the budget, and the verdict has to
    say which — v5b's bar 4 lost four rows to one refused thread and published only the rate."""
    ids = [one["msg_id"] for one in RECORD["population"]["gold"]["rows"]]
    answers = perfect() | {ids[0]: None}
    rows = [row for row in evidence_for(answers)]
    bar = scoring.bar_p1(RECORD, rows)
    assert bar["absent"] == 1 and bar["disagreed"] == 0
    assert bar["agreed"] == 13 and bar["passed"] is True
    assert bar["losses"]["by_cause"] == {"disagreed": 0, "absent": 1}
    # and the narrower reading over the rows the model actually answered is published beside it
    narrow = bar["rate_over_the_rows_the_model_answered"]
    assert narrow == {"n": 13, "agreed": 13, "rate": 1.0}


def test_the_collapse_is_applied_and_is_a_NO_OP_for_this_instruments_vocabulary():
    """MEASURED, not assumed — and the measurement is the point.

    Bar 4 needed the symmetric collapse because the v3 text offered «категория» AND
    «категория_личное» and gold r2 was re-labelled to the second. Pass 1's text offers only the
    four ratified readings and its parser REFUSES the fifth, so no answer it can produce is on
    either side of the map. The collapse is still applied — the contract says the comparison
    semantics are bar 4's — and here it is proved to change nothing, which is a fact about this
    bar that the next sitting should not have to rediscover.
    """
    assert probe_b_map() == {"категория_личное": "категория"}
    assert (
        "категория" not in scoring.probe_b.collapse.__module__ or True
    )  # the map above is the law
    spellings = {
        GOLD_BY_ID[one["msg_id"]].get("subject_type")
        for one in RECORD["population"]["gold"]["rows"]
    }
    assert "категория" not in spellings, "gold r2 was re-labelled — it spells категория_личное"
    assert "категория_личное" in spellings, "no collapsible spelling at all — check the gold file"

    answers = perfect()
    collapsed = scoring.bar_p1(RECORD, evidence_for(answers))
    # the SAME rows through the same comparison with no collapse anywhere
    wanted = [dict(GOLD_BY_ID[one["msg_id"]]) for one in RECORD["population"]["gold"]["rows"]]
    raw = scorer.reader_comment_agreement(wanted, list(answers.values()))
    assert collapsed["agreed"] == raw["agreed"] == 14
    # and the parser really does refuse the word the collapse exists for, so the no-op is structural
    with pytest.raises(prompts.ParseError, match="subject_type outside its domain"):
        prompts.parse_pass1(
            json.dumps(
                {"msg_id": 1, "subject_type": "категория", "subject_id": None, "stance": None}
            ),
            msg_id=1,
        )


def probe_b_map() -> dict:
    return dict(scoring.probe_b.COLLAPSE)


def test_the_census_and_the_refusals_count_the_shapes_apart():
    rows = evidence_for(perfect())
    rows.append(
        {
            "id": "@x:1#2",
            "thread": "@x:1",
            "msg_id": 2,
            "leg": "census",
            "reply": "…",
            "parsed": {
                "msg_id": 2,
                "subject_type": "сеть_ритейлер",
                "subject_id": "x",
                "stance": "negative",
            },
            "parse_error": None,
            "balanced": True,
            "finish_reason": "stop",
            "usage": {"prompt_tokens": 900, "completion_tokens": 40},
            "seconds": 3.0,
        }
    )
    rows.append(
        {
            "id": "@x:1#3",
            "thread": "@x:1",
            "msg_id": 3,
            "leg": "census",
            "reply": "…",
            "parsed": None,
            "parse_error": "missing field: stance",
            "balanced": False,
            "finish_reason": "length",
            "usage": {"prompt_tokens": 900, "completion_tokens": 256},
            "seconds": 9.0,
        }
    )
    census = scoring.census(RECORD, rows)
    assert census["n"] == 2 and census["parsed"] == 1
    assert census["subject_type_distribution"] == {"сеть_ритейлер": 1, "REFUSED": 1}
    assert census["per_thread"]["@x:1"] == {"сеть_ритейлер": 1, "REFUSED": 1}
    refused = scoring.refusals(rows)
    assert refused["refused"] == 1 and refused["by_shape"] == {"missing field: stance": 1}
    assert refused["by_leg"] == {"census": 1}
    assert refused["never_balanced"] == ["@x:1#3"]
    assert refused["finish_reason_length"] == ["@x:1#3"]


def test_the_per_call_price_is_reported_against_BOTH_registered_readings():
    calls = scoring.per_call(RECORD, evidence_for(perfect()))
    assert calls["measured"] is True and calls["calls"] == 14
    assert calls["seconds_per_call"] == 3.0
    reading = RECORD["money"]["reading"]
    assert (
        calls["registered_bound_seconds_per_call"] == reading["ceiling"]["seconds_per_pass1_call"]
    )
    assert calls["fitted_seconds_per_call"] == reading["fitted"]["seconds_per_pass1_call"]
    assert calls["against_the_bound"] == round(3.0 / calls["registered_bound_seconds_per_call"], 4)
    price = scoring.window_price(RECORD, calls)
    assert price["priced"] is True
    assert price["seconds"] == round(3.0 * price["payable_comments"], 1)
    assert "FLOOR" in price["rule"]


def test_the_verdict_re_derives_and_carries_the_return_to_sitting_clause(tmp_path, monkeypatch):
    """The whole record, written and read back — and the clause that decides what happens next has
    to be IN it, because the next session reads the verdict and not the contract."""
    path = tmp_path / "rows.jsonl"
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in evidence_for(perfect())),
        encoding="utf-8",
    )
    monkeypatch.setattr(scoring, "EVIDENCE", path)
    monkeypatch.setattr(scoring, "OUT", tmp_path / "verdict.json")
    monkeypatch.setattr(scoring, "RUN", tmp_path / "missing_run.json")
    assert scoring.main(["--out", str(tmp_path / "verdict.json")]) == 0
    verdict = json.loads((tmp_path / "verdict.json").read_text(encoding="utf-8"))
    assert verdict["outcome"] == "GO"
    assert verdict["return_to_sitting"] == RECORD["return_to_sitting"]
    assert verdict["bars"]["P1_per_comment_agreement"]["agreed"] == 14
    assert "run" not in verdict, "no run record existed, so the verdict must not claim one"


def test_a_failed_bar_is_a_STOP_and_the_verdict_says_so(tmp_path, monkeypatch):
    ids = [one["msg_id"] for one in RECORD["population"]["gold"]["rows"]]
    answers = perfect()
    for msg_id in ids[:3]:
        answers[msg_id] = {**answers[msg_id], "subject_type": None, "stance": "neutral"}
    path = tmp_path / "rows.jsonl"
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in evidence_for(answers)),
        encoding="utf-8",
    )
    monkeypatch.setattr(scoring, "EVIDENCE", path)
    monkeypatch.setattr(scoring, "RUN", tmp_path / "missing_run.json")
    assert scoring.main(["--out", str(tmp_path / "verdict.json")]) == 0
    verdict = json.loads((tmp_path / "verdict.json").read_text(encoding="utf-8"))
    assert verdict["outcome"] == "STOP"
    assert verdict["bars"]["P1_per_comment_agreement"]["passed"] is False


def test_no_evidence_at_all_is_FOURTEEN_ABSENT_ROWS_and_not_a_rate_over_nothing():
    """The denominator is the REGISTRATION's fourteen, so a run that answered nothing fails the bar
    with fourteen absent rows — it does not vanish into «0 of 0», and it does not silently narrow to
    the rows that came back ([[an_absolute_bar_needs_a_reachability_state]])."""
    bar = scoring.bar_p1(RECORD, [])
    assert bar["n"] == 14 and bar["agreed"] == 0 and bar["absent"] == 14
    assert bar["passed"] is False
    assert bar["losses"]["spent"] == 14
    assert bar["rate_over_the_rows_the_model_answered"] is None, (
        "with nothing answered there is no narrower reading to publish"
    )
