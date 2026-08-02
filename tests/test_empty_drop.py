"""The emptied-row measurement: arithmetic over rows already paid for (4.5f).

Three ways this number could be wrong without looking wrong — it could be measured on
the corrected corpus instead of the re-labeller's output, it could describe a skewed
length distribution with a mean, and it could keep citing a missing parent post after
somebody starts threading one into the prompt. One test each.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import measure_empty_drop as drop  # noqa: E402
import relabel_intents as relabel  # noqa: E402


def row(row_id, before, after, text="x", unclear=False, parent=7):
    return {
        "id": row_id,
        "source": "fixture",
        "text": text,
        "unclear": unclear,
        "parent_msg_id": parent,
        "before": sorted(before),
        "after": sorted(after),
    }


def test_a_hand_counted_population_is_what_the_shares_say():
    rows = [
        row("a", ["taste"], []),  # emptied — and drift v2 does not explain
        row("b", ["price"], []),  # emptied
        row("c", ["price"], ["availability"]),  # changed, no service
        row("d", ["price"], ["service"]),  # changed, explained
        row("e", ["taste"], ["taste"]),  # unmoved
        row("f", [], ["service"]),  # changed, explained
    ]
    found = drop.measure(rows)
    assert (found["rows"], found["changed"]) == (6, 5)
    assert found["changed_without_service"] == 3
    assert found["emptied"] == 2
    assert found["share_of_changed_without_service"] == pytest.approx(2 / 3)
    assert found["share_of_rows"] == pytest.approx(2 / 6)
    assert found["emptied_from"] == {"taste": 1, "price": 1}


def test_the_measurement_is_of_the_model_and_not_of_the_corrected_corpus(tmp_path):
    """A ruling that fixes an emptied row must not shrink the class it is evidence for."""
    source = tmp_path / "c.jsonl"
    staged = relabel.staged(source)
    base = {"id": "@c:1", "text": "З вишнею", "unclear": False, "parent_msg_id": 7}
    source.write_text(json.dumps({**base, "intents": ["taste"]}) + "\n", encoding="utf-8")
    staged.write_text(json.dumps({**base, "intents": ["taste"]}) + "\n", encoding="utf-8")

    assert drop.measure(drop.pairs({"fixture": source}, {}))["emptied"] == 0, "corrected: invisible"

    run = tmp_path / "run.json"
    run.write_text(
        json.dumps(
            {"runs": [], "fixes": [{"rows": [{"id": "@c:1", "old": [], "new": ["taste"]}]}]}
        ),
        encoding="utf-8",
    )
    put_back = drop.reversals(run)
    assert put_back == {"@c:1": []}
    assert drop.measure(drop.pairs({"fixture": source}, put_back))["emptied"] == 1


def test_the_length_of_a_skewed_class_is_given_as_quantiles():
    rows = [row(str(n), ["taste"], [], text="x" * n) for n in (5, 10, 20, 40, 4000)]
    found = drop.spread(rows)
    assert (found["rows"], found["chars_median"], found["chars_max"]) == (5, 20, 4000)
    assert found["chars_p25"] < found["chars_median"] < found["chars_p75"] < 4000
    assert found["reply_share"] == 1.0


def test_a_prompt_that_started_carrying_the_parent_ends_the_explanation(tmp_path):
    source = tmp_path / "c.jsonl"
    raw = {
        "id": "@c:1",
        "text": "З вишнею",
        "intents": [],
        "unclear": False,
        "parent_msg_id": 4242,
        "msg_id": 1,
        "channel": "@ch",
        "date": "2026-01-01",
    }
    source.write_text(json.dumps(raw) + "\n", encoding="utf-8")
    rows = [row("@c:1", [], [])]

    assert drop.premise(rows, {"fixture": source})["row_fields_in_the_prompt"] == ["text"]

    original = drop.prompts.build_messages
    drop.prompts.build_messages = lambda task, text: [
        {"role": "user", "content": f"parent 4242 said something\n{text}"}
    ]
    try:
        with pytest.raises(SystemExit, match="reach the prompt"):
            drop.premise(rows, {"fixture": source})
    finally:
        drop.prompts.build_messages = original


def test_a_population_with_no_replies_cannot_check_the_premise(tmp_path):
    source = tmp_path / "c.jsonl"
    source.write_text(
        json.dumps({"id": "@c:1", "text": "x", "intents": [], "unclear": False}) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match="cannot be checked against anything"):
        drop.premise([row("@c:1", [], [], parent=None)], {"fixture": source})
