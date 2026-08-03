"""Six values a human read out of six notes — and the guards that keep them a transcription.

The risk here is not a bug, it is a typo. Every value in `DICTATED` is legal, passes
`check_labels` and becomes adjudicated truth the moment it is written; nothing downstream can
tell `["service"]` from `["availability"]` after the fact. So the tests below are about
provenance more than about code: the dictated values have to be words the row's own verdict note
already contains, the touched rows have to be exactly six, and the two rows nobody ruled on have
to still be there afterwards.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import apply_dictated_verdicts as dictated  # noqa: E402
import apply_sitting_verdicts as verdicts  # noqa: E402

GATES = REPO_ROOT / "results" / "sitting_45g_gates.json"
BATCH = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g2.jsonl"


@pytest.fixture
def gates():
    return json.loads(GATES.read_text(encoding="utf-8"))


def row(row_id, **overrides):
    base = {
        "id": row_id,
        "channel": row_id.split(":")[0],
        "msg_id": int(row_id.split(":")[1]),
        "text": "щось",
        "sentiment": "neutral",
        "sarcasm": False,
        "intents": [],
        "unclear": False,
        "annotator": "llm-precheck",
        "notes": "",
    }
    return {**base, **overrides}


def lines_of(rows):
    return [json.dumps(item, ensure_ascii=False) for item in rows]


def test_the_dictation_is_six_rows_of_intents_and_nothing_else():
    """One field each, because that is what the briefing named. A second field arriving in this
    table would be a value nobody dictated travelling under the same authority."""
    assert len(dictated.DICTATED) == 6
    assert {field for labels in dictated.DICTATED.values() for field in labels} == {"intents"}
    for labels in dictated.DICTATED.values():
        assert labels["intents"] == sorted(labels["intents"])
        assert labels["intents"], "an empty list is a value; it would have to be dictated as one"


def test_every_dictated_value_is_a_word_its_own_verdict_note_uses(gates):
    """The typo guard, on the real notes. `["taste"]` for `["price"]` is a legal row and an
    invisible defect; the note that ruled on the row is the only thing that can refuse it."""
    notes = dictated.transcribed(dict(dictated.DICTATED), gates)
    assert set(notes) == set(dictated.DICTATED)
    for row_id, labels in dictated.DICTATED.items():
        for value in labels["intents"]:
            assert value in notes[row_id].casefold(), row_id


def test_a_value_the_note_never_states_is_refused(gates):
    """The negative control: without it the check above passes on any note long enough."""
    with pytest.raises(SystemExit, match="never says the word"):
        dictated.transcribed({"@VARUS_channel:7555": {"intents": ["taste"]}}, gates)


def test_a_row_no_verdict_refused_is_refused(gates):
    with pytest.raises(SystemExit, match="not refused rows"):
        dictated.transcribed({"@VARUS_channel:999999": {"intents": ["taste"]}}, gates)


def test_the_two_rows_nobody_ruled_on_are_named_and_still_open(gates):
    """7555 has no stated value and 11876 is held pending law. The run asserts this set rather
    than reporting it, so a seventh row quietly joining the dictation fails."""
    refused = {r["id"] for r in gates["rows"] if r["verdict"] == "incorrect"}
    prior = json.loads((REPO_ROOT / "results" / "verdicts_45g5.json").read_text())["runs"][-1]
    adjudicated = {r["id"] for r in prior["rows"]} | set(dictated.DICTATED)
    assert sorted(refused - adjudicated) == sorted(dictated.UNTOUCHED)
    assert len(refused) == 42 and len(adjudicated) == 40


def test_only_the_named_field_moves_and_the_earlier_clause_survives():
    """9271 came out of 4.5g5 with `unclear` adjudicated. This adds `intents` to it: the other
    three fields stay, and the note keeps the sentence saying where `unclear` came from."""
    before = row(
        "@VARUS_channel:9271",
        sentiment="neutral",
        unclear=False,
        notes="4.5g5: sitting-45g verdict applied (stated in the verdict note) — unclear=false.",
    )
    out, touched = verdicts.apply(
        lines_of([before]),
        {"@VARUS_channel:9271": {"intents": ["service"]}},
        {"@VARUS_channel:9271": dictated.REASON},
        note=dictated.note_for,
    )
    after = json.loads(out[0])
    assert after["intents"] == ["service"]
    assert (after["sentiment"], after["sarcasm"], after["unclear"]) == ("neutral", False, False)
    assert after["annotator"] == "sitting-45g-verdicts"
    assert after["notes"].startswith("4.5g5: ") and " | 4.5g6: " in after["notes"]
    assert 'intents=["service"]' in after["notes"]
    assert touched[0]["fields"] == ["intents"] and touched[0]["moved"]


def test_a_row_with_no_earlier_note_gets_one_clause_and_no_separator():
    out, _ = verdicts.apply(
        lines_of([row("@VARUS_channel:8478")]),
        {"@VARUS_channel:8478": {"intents": ["service"]}},
        {"@VARUS_channel:8478": dictated.REASON},
        note=dictated.note_for,
    )
    assert json.loads(out[0])["notes"].startswith("4.5g6: ")
    assert "|" not in json.loads(out[0])["notes"]


def test_untouched_lines_are_the_same_objects():
    """The diff guard's premise: a line this run does not mean to touch is not re-serialised."""
    lines = lines_of([row("@VARUS_channel:8478"), row("@VARUS_channel:1"), row("@msuaaaa:2")])
    out, _ = verdicts.apply(
        lines,
        {"@VARUS_channel:8478": {"intents": ["service"]}},
        {"@VARUS_channel:8478": dictated.REASON},
        note=dictated.note_for,
    )
    assert verdicts.differing(lines, out) == [0]
    assert out[1] is lines[1] and out[2] is lines[2]


def test_an_illegal_row_stops_the_run():
    with pytest.raises(SystemExit, match="illegal row"):
        verdicts.apply(
            lines_of([row("@VARUS_channel:8478")]),
            {"@VARUS_channel:8478": {"intents": ["nonsense"]}},
            {"@VARUS_channel:8478": dictated.REASON},
            note=dictated.note_for,
        )


def test_already_applied_sees_the_values_not_the_annotator():
    """4.5g5's re-run guard read the annotator, and 9271 already carries it. Ask the fields."""
    rows = [row("@VARUS_channel:8478", intents=["service"], annotator="llm-precheck")]
    assert dictated.already_applied(rows, {"@VARUS_channel:8478": {"intents": ["service"]}}) == [
        "@VARUS_channel:8478"
    ]
    assert dictated.already_applied(rows, {"@VARUS_channel:8478": {"intents": ["taste"]}}) == []


@pytest.mark.skipif(not BATCH.exists(), reason="the batch is gitignored data")
def test_on_the_real_batch_exactly_six_rows_carry_the_dictated_values():
    """After the run: six rows hold what was dictated, and every one of them is a refusal the
    sitting made — a dictated value landing on an accepted row would be law arriving sideways."""
    rows = {json.loads(line)["id"]: json.loads(line) for line in BATCH.read_text().splitlines()}
    gates = json.loads(GATES.read_text(encoding="utf-8"))
    refused = {r["id"] for r in gates["rows"] if r["verdict"] == "incorrect"}
    assert dictated.already_applied(list(rows.values()), dict(dictated.DICTATED)) == sorted(
        dictated.DICTATED
    )
    for row_id in dictated.DICTATED:
        assert row_id in refused
        assert rows[row_id]["annotator"] == "sitting-45g-verdicts"
    for row_id in dictated.UNTOUCHED:
        assert rows[row_id]["annotator"] == "llm-precheck"
