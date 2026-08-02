"""Three operator rulings written into a labelled corpus — the narrowest write there is.

A ruling changes one cell of one row under the operator's name, so the failures worth
testing are the quiet ones: a label the returned verdicts do not back, an `old` that is
not the old value, a second run applying the same fix twice, and any column other than
`intents` moving. The fixtures are throwaway files: the real `_tax2` corpus is what this
script edits, and a suite that read it would go red the moment it worked.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import apply_calibration_rulings as rulings  # noqa: E402
import relabel_intents as relabel  # noqa: E402

RULED = "@VARUS_channel:11972"


def row(row_id, intents, text="Картопля з печінкою"):
    return {
        "id": row_id,
        "channel": "@VARUS_channel",
        "text": text,
        "sentiment": "neutral",
        "intents": list(intents),
        "unclear": False,
        "annotator": "operator-blind-audit-45a",
    }


def corpus(tmp_path, staged_intents, source_intents=("taste",)):
    """A source file and its staged copy, one ruled row and one bystander."""
    source = tmp_path / "comments.jsonl"
    stage = relabel.staged(source)
    for path, ruled in ((source, list(source_intents)), (stage, list(staged_intents))):
        path.write_text(
            json.dumps(row(RULED, ruled), ensure_ascii=False)
            + "\n"
            + json.dumps(row("@VARUS_channel:1", ["price"], "інше"), ensure_ascii=False)
            + "\n",
            encoding="utf-8",
        )
    return {"comments": source}, {"comments": stage}


def verdicts(verdict="old", row_id=RULED):
    return {"rows": {"changed": [{"id": row_id, "verdict": verdict, "notes": ""}]}}


ONE = ({"id": RULED, "intents": ["taste"], "verdict": "old", "authority": "the operator"},)


def test_a_ruling_moves_the_intents_column_and_nothing_else(tmp_path):
    sources, staged = corpus(tmp_path, staged_intents=[])
    before = staged["comments"].read_text(encoding="utf-8").splitlines()

    outcome = rulings.apply_all(ONE, verdicts(), staged, sources)
    assert [(f["id"], f["old"], f["new"]) for f in outcome["applied"]] == [(RULED, [], ["taste"])]

    after = staged["comments"].read_text(encoding="utf-8").splitlines()
    assert after[1] == before[1], "the bystander row is byte-identical"
    assert json.loads(after[0]) == {**json.loads(before[0]), "intents": ["taste"]}
    assert list(json.loads(after[0])) == list(json.loads(before[0])), "key order survives"
    assert outcome["before"] != outcome["after"], "the file's sha is recorded on both sides"


def test_a_second_run_counts_the_row_as_applied_and_writes_nothing(tmp_path):
    sources, staged = corpus(tmp_path, staged_intents=[])
    rulings.apply_all(ONE, verdicts(), staged, sources)
    settled = staged["comments"].read_bytes()

    outcome = rulings.apply_all(ONE, verdicts(), staged, sources)
    assert outcome["applied"] == [] and len(outcome["matching"]) == 1
    assert staged["comments"].read_bytes() == settled


def test_a_ruling_the_returned_verdicts_do_not_back_is_refused(tmp_path):
    sources, staged = corpus(tmp_path, staged_intents=[])
    with pytest.raises(SystemExit, match="is a label invented here"):
        rulings.apply_all(ONE, verdicts(verdict="new"), staged, sources)
    with pytest.raises(SystemExit, match="is a label invented here"):
        rulings.apply_all(ONE, verdicts(row_id="@VARUS_channel:999"), staged, sources)
    assert json.loads(staged["comments"].read_text().splitlines()[0])["intents"] == []


def test_old_that_is_not_the_old_value_is_refused(tmp_path):
    """`old` means the v1 label — read out of the source, never retyped into the table."""
    sources, staged = corpus(tmp_path, staged_intents=[], source_intents=["quality"])
    with pytest.raises(SystemExit, match="`old` means the old value"):
        rulings.apply_all(ONE, verdicts(), staged, sources)

    dictated = ({**ONE[0], "verdict": "neither"},)
    outcome = rulings.apply_all(dictated, verdicts(verdict="neither"), staged, sources)
    assert outcome["applied"][0]["new"] == ["taste"], "a dictated set is not checked against v1"


def test_a_row_two_files_both_claim_is_a_stop_and_not_a_pick(tmp_path):
    sources, staged = corpus(tmp_path, staged_intents=[])
    twin = tmp_path / "twin_tax2.jsonl"
    twin.write_text(json.dumps(row(RULED, [], "інше"), ensure_ascii=False) + "\n", "utf-8")
    with pytest.raises(SystemExit, match="a ruling cannot name one row"):
        rulings.apply_all(ONE, verdicts(), {**staged, "twin": twin}, sources)


def test_the_three_rulings_are_the_ones_the_prompt_ratified():
    """The table is the law here; a fourth id or a different label is a code change."""
    assert [(r["id"], r["intents"], r["verdict"]) for r in rulings.RULINGS] == [
        ("@VARUS_channel:11972", ["taste"], "old"),
        ("@VARUS_channel:11960", ["taste"], "old"),
        ("@VARUS_channel:11902", ["taste"], "neither"),
    ]
