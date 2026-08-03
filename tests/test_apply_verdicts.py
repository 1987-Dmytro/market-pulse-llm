"""The adjudicated verdicts land on the rows they name, and on nothing else (4.5g5, Task 1)."""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import apply_sitting_verdicts as verdicts  # noqa: E402

GUIDELINE = REPO_ROOT / "docs" / "annotation" / "comments.md"
BATCH = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g2.jsonl"
GATES = REPO_ROOT / "results" / "sitting_45g_gates.json"


def row(row_id, **over):
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
    return json.dumps({**base, **over}, ensure_ascii=False)


def gates(*rows):
    return {"rows": [{"id": i, "verdict": v, "notes": n} for i, v, n in rows]}


def guideline(tmp_path, p5="`@a:1`", p6="`@a:2`"):
    text = f"4. A promo question ({p5} — pattern P5.)\n2. Support voice ({p6} — pattern P6.)\n"
    path = tmp_path / "comments.md"
    path.write_text(text, encoding="utf-8")
    return path


# --- the two family values are the guideline's, not this script's ------------------------


def test_the_family_values_are_the_ones_the_guideline_states():
    """A value copied out of prose drifts from the prose. Grep it back, every run."""
    text = GUIDELINE.read_text(encoding="utf-8")
    rules = {}
    for name in ("P5", "P6"):
        found = [block for block in text.split("\n\n") if name in block]
        # Two blocks and the wrong one could satisfy every assertion below.
        assert len(found) == 1, f"{name} is named in {len(found)} places"
        rules[name] = found[0]

    assert '`["service"]`' in rules["P5"]
    assert "promo" in rules["P5"].lower()
    assert verdicts.FAMILY_VALUES["P5"] == {"intents": ["service"]}

    assert "`unclear: true`" in rules["P6"]
    assert "support boilerplate" in rules["P6"]
    assert verdicts.FAMILY_VALUES["P6"] == {"unclear": True}


def test_a_family_the_guideline_no_longer_names_stops_the_run(tmp_path):
    path = tmp_path / "comments.md"
    path.write_text("4. A promo question (`@a:1` — pattern P5.)\n", encoding="utf-8")
    with pytest.raises(SystemExit, match=r"no \['P6'\] bracket"):
        verdicts.wanted(gates(), path)


# --- what may be touched ----------------------------------------------------------------


def test_only_a_note_that_names_a_value_selects_a_row(tmp_path):
    want, why = verdicts.wanted(
        gates(
            ("@b:1", "incorrect", "unclear should be true"),
            ("@b:2", "incorrect", "tl-llm: intents unsupported by the text"),
            ("@b:3", "correct", "unclear should be true"),
        ),
        guideline(tmp_path),
    )
    assert want == {
        "@b:1": {"unclear": True},
        "@a:1": {"intents": ["service"]},
        "@a:2": {"unclear": True},
    }
    assert why["@b:1"] == "stated in the verdict note"
    assert why["@a:1"] == "pattern P5"


def test_a_row_named_by_both_its_note_and_its_family_records_both(tmp_path):
    want, why = verdicts.wanted(
        gates(("@a:2", "incorrect", "unclear should be true")), guideline(tmp_path)
    )
    assert want["@a:2"] == {"unclear": True}
    assert why["@a:2"] == "stated in the verdict note; pattern P6"


def test_a_family_contradicting_a_verdict_note_stops_the_run(tmp_path):
    with pytest.raises(SystemExit, match="verdict note and family P6 disagree"):
        verdicts.wanted(
            gates(("@a:2", "incorrect", "unclear should be false")), guideline(tmp_path)
        )


def test_the_rows_left_alone_carry_the_note_that_refused_them(tmp_path):
    state = gates(
        ("@b:1", "incorrect", "unclear should be true"),
        ("@b:2", "incorrect", "tl-llm: ['availability'] wrong — queue joke"),
        ("@b:3", "correct", ""),
    )
    want, _ = verdicts.wanted(state, guideline(tmp_path))
    assert verdicts.refused_without_a_value(state, want) == [
        {"id": "@b:2", "notes": "tl-llm: ['availability'] wrong — queue joke"}
    ]


# --- what the write does --------------------------------------------------------------


def test_only_the_named_field_moves_and_the_rest_of_the_row_survives():
    lines = [row("@b:1", intents=["price"], sentiment="negative", sarcasm=True)]
    out, touched = verdicts.apply(lines, {"@b:1": {"unclear": True}}, {"@b:1": "note"})
    after = json.loads(out[0])
    assert after["unclear"] is True
    assert (after["intents"], after["sentiment"], after["sarcasm"]) == (["price"], "negative", True)
    assert after["annotator"] == verdicts.ANNOTATOR
    assert touched[0]["fields"] == ["unclear"]
    assert touched[0]["moved"] is True


def test_an_untouched_line_is_the_same_bytes():
    lines = [row("@b:1"), row("@b:2")]
    out, touched = verdicts.apply(lines, {"@b:2": {"unclear": True}}, {"@b:2": "note"})
    assert out[0] is lines[0]
    assert verdicts.differing(lines, out) == [1]
    assert [r["id"] for r in touched] == ["@b:2"]


def test_a_ruling_already_matching_is_recorded_as_not_moved():
    lines = [row("@b:1", unclear=True)]
    _, touched = verdicts.apply(lines, {"@b:1": {"unclear": True}}, {"@b:1": "note"})
    assert touched[0]["moved"] is False


def test_a_verdict_that_would_produce_an_illegal_row_stops_the_run():
    lines = [row("@b:1")]
    with pytest.raises(SystemExit, match="illegal row"):
        verdicts.apply(lines, {"@b:1": {"intents": ["vibes"]}}, {"@b:1": "note"})


def test_an_adjudicated_id_missing_from_the_batch_stops_the_run():
    with pytest.raises(SystemExit, match="not in the batch"):
        verdicts.apply([row("@b:1")], {"@b:9": {"unclear": True}}, {"@b:9": "note"})


def test_a_line_count_that_moved_is_not_a_diff_worth_reading():
    with pytest.raises(SystemExit, match="line count moved: 2 -> 1"):
        verdicts.differing([row("@b:1"), row("@b:2")], [row("@b:1")])


def test_the_note_names_the_ruling_and_its_value():
    note = verdicts.note_for({"intents": ["service"]}, "pattern P5")
    assert "pattern P5" in note
    assert 'intents=["service"]' in note
    assert "results/sitting_45g_gates.json" in note


def test_the_counts_are_derived_from_the_touched_rows():
    lines = [row("@b:1"), row("@b:2", unclear=True)]
    _, touched = verdicts.apply(
        lines,
        {"@b:1": {"unclear": True}, "@b:2": {"unclear": True}},
        {"@b:1": "pattern P6", "@b:2": "stated in the verdict note"},
    )
    counts = verdicts.counts(touched)
    assert counts["rows_touched"] == 2
    assert counts["rows_moved"] == 1
    assert counts["per_field"] == {"unclear": 2}
    assert counts["by_reason"] == {"pattern P6": 1, "stated in the verdict note": 1}


# --- the real thing ---------------------------------------------------------------------


def test_the_sitting_names_a_value_for_35_of_its_42_refusals():
    """29 notes state one outright; P5 and P6 state six more in the guideline's prose."""
    state = json.loads(GATES.read_text(encoding="utf-8"))
    want, why = verdicts.wanted(state, GUIDELINE)
    refused = [r["id"] for r in state["rows"] if r["verdict"] == "incorrect"]

    assert len(refused) == 42
    assert len(want) == 35
    assert set(want) <= set(refused)
    assert sum(1 for reason in why.values() if reason.startswith("stated")) == 29
    assert len(verdicts.refused_without_a_value(state, want)) == 7
    assert all(len(labels) == 1 for labels in want.values())
