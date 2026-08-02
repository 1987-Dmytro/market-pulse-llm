"""The 4.5a audit: blinding, the unclear rule, and the ceiling arithmetic by hand.

Two things have to be checked here that no downstream number would reveal:

- **the blinding**, because a leak makes the operator's verdicts attributions
  rather than judgements, and every number after that is of the wrong thing;
- **the ceiling arithmetic**, pinned against a worked example small enough to
  redo on paper — the same rule ``tests/test_scorer.py`` states for every gate
  metric, and this is the number a phase decision will be read off.

The end-to-end test drives ``audit_ceiling.main`` over a six-row pack whose every
expected figure is computed in the comment above it, so the harness is checked
through its printed output and not through its own internals.
"""

import csv
import json
import random
import sys
from hashlib import sha256
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import audit_ceiling  # noqa: E402
import build_audit_pack  # noqa: E402
from market_pulse import audit  # noqa: E402

ALIASES = {"рудь": "rud"}


def comment(row_id, sentiment, intents=(), sarcasm=False, unclear=False):
    return {
        "id": row_id,
        "text": f"text of {row_id}",
        "language": "ua",
        "sentiment": "unclear" if unclear else sentiment,
        "sarcasm": None if unclear else sarcasm,
        "intents": None if unclear else list(intents),
    }


# --- the canonical value, one function for both sides -----------------------


def test_value_is_the_same_for_gold_and_prediction_shapes():
    gold = comment("c1", "positive", intents=["price", "taste"])
    prediction = {"sentiment": "positive", "sarcasm": False, "intents": ["taste", "price"]}
    for head in ("sentiment", "intents", "sarcasm_pair"):
        assert audit.value(head, gold, ALIASES) == audit.value(head, prediction, ALIASES)


def test_brands_normalise_on_both_sides():
    gold = {"brands": [{"mention": "Рудь", "brand_id": "rud"}]}
    prediction = {"brands": [{"mention": "рудь"}]}
    assert audit.value("brands", gold, ALIASES) == audit.value("brands", prediction, ALIASES)


def test_render_is_order_free_so_a_set_cannot_leak_its_builder():
    left = audit.render("intents", frozenset({"price", "taste"}))
    right = audit.render("intents", frozenset({"taste", "price"}))
    assert left == right == '["price", "taste"]'


def test_render_rejects_an_unknown_head():
    with pytest.raises(KeyError):
        audit.render("sentiment_v2", "positive")


# --- the unclear rule -------------------------------------------------------
#
# The frozen test set happens to carry no unclear rows today, so this is the only
# place the filter is exercised at all: a fixture injects them on purpose.


def test_scoreable_drops_unclear_gold_on_every_head():
    row = comment("c9", "positive", unclear=True) | {"post_type": "unclear", "brands": None}
    assert not any(audit.scoreable(head, row) for head in audit.HEADS)


def test_disagreements_skip_unclear_rows_even_when_the_model_answered():
    rows = [comment("c1", "positive", unclear=True), comment("c2", "positive")]
    predicted = {
        "c1": {"sentiment": "negative", "sarcasm": False, "intents": []},
        "c2": {"sentiment": "negative", "sarcasm": False, "intents": []},
    }
    found = audit.disagreements("sentiment", rows, predicted, ALIASES)
    assert [row["id"] for row in found] == ["c2"]


def test_disagreements_refuse_a_row_the_arm_never_scored():
    with pytest.raises(ValueError, match="never scored"):
        audit.disagreements("sentiment", [comment("c1", "positive")], {}, ALIASES)


# --- the blinding -----------------------------------------------------------


def test_blind_is_a_seeded_coin_flip():
    def draws():
        rng = random.Random(42)
        return [audit.blind(rng) for _ in range(40)]

    assert draws() == draws(), "a rebuild must reproduce the pack, so the flips must repeat"
    assert set(draws()) == {"A", "B"}, "a flip that never lands on both sides is not blinding"


def test_the_pack_never_names_a_side():
    """The vocabulary check the verify-gate runs, as a test that travels with the code."""
    rows = [comment("c1", "positive"), comment("c2", "negative")]
    predicted = {
        "c1": {"sentiment": "negative", "sarcasm": False, "intents": []},
        "c2": {"sentiment": "positive", "sarcasm": False, "intents": []},
    }
    pack, _ = build_audit_pack.build(
        {"comments_test": rows, "posts_test": [], "sarcasm_holdout": []},
        {"comments_test": predicted, "posts_test": {}, "sarcasm_holdout": {}},
        ALIASES,
        [],
    )
    text = json.dumps(pack["blinded"], ensure_ascii=False).casefold()
    for word in ("model", "gold", "pred", "truth", "arm"):
        assert word not in text


def test_has_verdicts_guards_a_filled_pack(tmp_path):
    blank, filled = tmp_path / "a.csv", tmp_path / "b.csv"
    blank.write_text("head,id,verdict\nsentiment,c1,\n", encoding="utf-8")
    assert build_audit_pack.has_verdicts(tmp_path) == []
    filled.write_text("head,id,verdict\nsentiment,c2,A\n", encoding="utf-8")
    assert build_audit_pack.has_verdicts(tmp_path) == ["b.csv"]


# --- the ceiling ------------------------------------------------------------
#
#   100 rows · 20 disagreements, 5 of them ruled gold-wrong and 2 ambiguous
#   80 agreements, seen through a control of 10 with 1 incorrect and 0 ambiguous
#
#   lost to bad gold  = 5 + 80 * 1/10 = 13
#   lost to ambiguity = 2 + 80 * 0/10 =  2
#   high = 1 - 13/100 = 0.87   ·   low = 1 - 15/100 = 0.85
def test_ceiling_matches_the_hand_computed_fixture():
    result = audit.ceiling(100, 20, 5, 2, 10, 1, 0)
    assert result["agreement_n"] == 80
    assert result["lost_gold"] == pytest.approx(13.0)
    assert result["high"] == pytest.approx(0.87)
    assert result["low"] == pytest.approx(0.85)


def test_ceiling_refuses_an_empty_control():
    with pytest.raises(ValueError, match="control sample"):
        audit.ceiling(100, 20, 5, 2, 0, 0, 0)


def test_ceiling_refuses_more_disagreements_than_rows():
    with pytest.raises(ValueError, match="stratum"):
        audit.ceiling(10, 20, 5, 2, 10, 1, 0)


# --- end to end -------------------------------------------------------------
#
# Six comment rows, one head. c1 c2 c3 disagree, c4 c5 c6 agree, control = c4 c5.
#
#       gold      model     ruling
#   c1  positive  negative  for the model  -> gold is wrong here
#   c2  negative  positive  for gold       -> the model is wrong here
#   c3  neutral   positive  ambiguous
#   c4  positive  positive  control: correct
#   c5  negative  negative  control: incorrect  (both wrong the same way)
#
#   accuracy units: lost_gold = 1 + 3 * 1/2 = 2.5 · lost_ambiguous = 1
#                   high = 1 - 2.5/6 = 0.5833 · low = 1 - 3.5/6 = 0.4167
#   sensitivity at incorrect 0 / 1 / 2 -> 1 - 1/6, 1 - 2.5/6, 1 - 4/6
#                                       = 0.8333 / 0.5833 / 0.3333
#
#   macro-F1 units: a perfect model answers gold everywhere but c1, where it
#   answers `negative`. Against unrepaired gold:
#     negative tp 2 (c2 c5) fp 1 (c1) fn 0 -> 4/5
#     neutral  tp 2 (c3 c6) fp 0     fn 0 -> 1
#     positive tp 1 (c4)    fp 0     fn 1 (c1) -> 2/3
#     macro = (0.8 + 1 + 2/3) / 3 = 0.8222
GOLD = {"c1": "positive", "c2": "negative", "c3": "neutral"}
MODEL = {"c1": "negative", "c2": "positive", "c3": "positive"}
MODEL_COLUMN = {"c1": "A", "c2": "B", "c3": "A"}
RULING = {"c1": "A", "c2": "A", "c3": "ambiguous"}


@pytest.fixture
def pack(tmp_path):
    frozen, directory = tmp_path / "frozen", tmp_path / "pack"
    frozen.mkdir()
    directory.mkdir()
    rows = [comment(f"c{i}", sentiment) for i, sentiment in enumerate(GOLD.values(), start=1)]
    rows += [comment("c4", "positive"), comment("c5", "negative"), comment("c6", "neutral")]
    (frozen / "comments_test.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    predictions = tmp_path / "pred.jsonl"
    predictions.write_text(
        "".join(
            json.dumps(
                {
                    "id": row["id"],
                    "input": "comments_test",
                    "pred": {
                        "sentiment": MODEL.get(row["id"], row["sentiment"]),
                        "sarcasm": False,
                        "intents": [],
                    },
                }
            )
            + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )

    key = {}
    with (directory / "comments_sentiment.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=build_audit_pack.COLUMNS)
        writer.writeheader()
        for row_id, column in MODEL_COLUMN.items():
            labels = {
                "label_A": MODEL[row_id] if column == "A" else GOLD[row_id],
                "label_B": GOLD[row_id] if column == "A" else MODEL[row_id],
            }
            key[f"sentiment|{row_id}"] = {"model_column": column, **labels}
            writer.writerow(
                {
                    "head": "sentiment",
                    "id": row_id,
                    "text": f"text of {row_id}",
                    **labels,
                    "verdict": RULING[row_id],
                    "notes": "",
                }
            )
    with (directory / "control.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=build_audit_pack.CONTROL_COLUMNS)
        writer.writeheader()
        for row_id, verdict in (("c4", "correct"), ("c5", "incorrect")):
            writer.writerow(
                {
                    "head": "sentiment",
                    "id": row_id,
                    "text": f"text of {row_id}",
                    "label": GOLD.get(row_id, ""),
                    "verdict": verdict,
                    "notes": "",
                }
            )

    key_path = tmp_path / "key.json"
    key_path.write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "arm": "real-only",
                "arm_record_timestamp": "2026-08-01T18:37:47+00:00",
                "pack_path": str(directory),
                "key_path": str(key_path),
                "key_sha256": sha256(key_path.read_bytes()).hexdigest(),
                "predictions_path": str(predictions),
                "frozen_path": str(frozen),
                "slice_path": str(tmp_path / "slice.json"),
                "strata": {
                    "sentiment": {
                        "gate": "G1a",
                        "input": "comments_test",
                        "scoreable": 6,
                        "disagreements": 3,
                        "agreements": 3,
                        "control": 2,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    return manifest, directory, key_path


def test_harness_prints_the_hand_computed_ceilings(pack, capsys):
    manifest, _, _ = pack
    assert audit_ceiling.main(["--manifest", str(manifest)]) == 0
    out = capsys.readouterr().out
    assert "disagreements n=3    gold wrong 1    model wrong 1    ambiguous 1" in out
    assert "macro-F1 units (disagreements only, UPPER BOUND): 0.8222" in out
    assert "accuracy units (both strata): 0.4167 .. 0.5833" in out
    assert "0->0.8333 · 1->0.5833 · 2->0.3333" in out


def test_harness_refuses_an_empty_verdict(pack):
    manifest, directory, _ = pack
    path = directory / "comments_sentiment.csv"
    path.write_text(path.read_text(encoding="utf-8").replace(",ambiguous,", ",,"), encoding="utf-8")
    with pytest.raises(SystemExit, match="still empty"):
        audit_ceiling.main(["--manifest", str(manifest)])


def test_harness_refuses_an_edited_label(pack):
    manifest, directory, _ = pack
    path = directory / "comments_sentiment.csv"
    path.write_text(
        path.read_text(encoding="utf-8").replace("c3,text of c3,positive", "c3,text of c3,neutral"),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match="differ from the key"):
        audit_ceiling.main(["--manifest", str(manifest)])


def test_harness_refuses_a_regenerated_key(pack):
    manifest, _, key_path = pack
    key_path.write_text(key_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(SystemExit, match="regenerated or edited"):
        audit_ceiling.main(["--manifest", str(manifest)])
