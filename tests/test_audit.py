"""The 4.5a audit: blinding, the unclear rule, and the ceiling arithmetic by hand.

Two things have to be checked here that no downstream number would reveal:

- **the blinding**, because a leak makes the operator's verdicts attributions
  rather than judgements, and every number after that is of the wrong thing;
- **the ceiling arithmetic**, pinned against a worked example small enough to
  redo on paper — the same rule ``tests/test_scorer.py`` states for every gate
  metric, and this is the number a phase decision will be read off.

The end-to-end test drives ``audit_ceiling.main`` over a six-row pack whose every
expected figure is computed in the comment above it, so the harness is checked
through its printed output and not through its own internals. That pack carries
one head, so ``metric_ceiling`` is exercised head by head separately: four of its
five branches would otherwise run for the first time on the evening the
operator's verdicts come back, which is the worst moment to meet a shape bug.
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


def written_pack(tmp_path):
    """A two-row pack on disk, written by the builder's own writer."""
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
    path = tmp_path / "comments_sentiment.csv"
    build_audit_pack.write_csv(path, audit.COLUMNS, pack["blinded"]["sentiment"])
    return path


def test_blinding_sweep_passes_a_clean_pack(tmp_path):
    written_pack(tmp_path)
    assert build_audit_pack.blinding_sweep(tmp_path) == []


def test_blinding_sweep_fails_a_planted_attribution(tmp_path):
    """The negative control: a sweep that never fails is a ceremony, not a guard.

    The leak this plants is the realistic one — not a word inside a label, but a
    COLUMN whose name says which side its neighbour came from.
    """
    path = written_pack(tmp_path)
    lines = path.read_text(encoding="utf-8").splitlines()
    planted = [lines[0] + ",label_gold"] + [line + ",yes" for line in lines[1:]]
    path.write_text("\n".join(planted) + "\n", encoding="utf-8")
    found = build_audit_pack.blinding_sweep(tmp_path)
    assert found and all(cell == "label_gold" for _, cell in found)


def test_blinding_sweep_ignores_the_rows_own_text(tmp_path):
    """A comment may legitimately say "модель" — dropping such rows would bias the pack."""
    path = tmp_path / "comments_sentiment.csv"
    build_audit_pack.write_csv(
        path,
        audit.COLUMNS,
        [
            {
                "head": "sentiment",
                "id": "c1",
                "text": "ця модель холодильника — golden standard",
                "label_A": "positive",
                "label_B": "negative",
                "verdict": "",
                "notes": "",
            }
        ],
    )
    assert build_audit_pack.blinding_sweep(tmp_path) == []


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


# --- the perfect model, head by head ----------------------------------------
#
# `metric_ceiling` re-scores a model that answers gold everywhere except the rows
# the operator ruled gold-wrong, where it answers what the model said. Each head
# below is three or four rows with the F1 done by hand, and each carries one row
# whose gold is `None`: the scorer drops that index from BOTH columns, and the
# perfect column is built positionally, so a drop that moved one side and not the
# other would show up here as a wrong number rather than as a wrong ceiling.


def post(row_id, post_type="promo", brands=(), relevant=True):
    return {
        "id": row_id,
        "text": f"text of {row_id}",
        "post_type": post_type,
        "brands": None if brands is None else list(brands),
        "relevant": relevant,
    }


def predicted_for(name, rows):
    return {name: {row["id"]: row for row in rows}}


#   gold [price] [taste] []  · perfect [taste] [taste] []  (i1 ruled gold-wrong)
#   tp 1 · fp 1 · fn 1 -> 2*1 / (2*1 + 1 + 1) = 0.5 · the None row drops out
def test_metric_ceiling_intents():
    gold = [
        comment("i1", "neutral", intents=["price"]),
        comment("i2", "neutral", intents=["taste"]),
        comment("i3", "neutral"),
        comment("i4", "neutral", unclear=True),
    ]
    model = [
        comment("i1", "neutral", intents=["taste"]),
        comment("i2", "neutral", intents=["taste"]),
        comment("i3", "neutral"),
        comment("i4", "neutral", intents=["price"]),
    ]
    unit, score = audit_ceiling.metric_ceiling(
        "intents",
        {"comments_test": gold},
        predicted_for("comments_test", model),
        ALIASES,
        {"i1"},
        [],
    )
    assert unit == "micro-F1"
    assert score == pytest.approx(0.5)


#   gold    [launch, promo, other, launch]
#   perfect [promo,  promo, other, launch]   (p1 ruled gold-wrong)
#   launch tp1 fp0 fn1 -> 2/3 · other tp1 -> 1 · promo tp1 fp1 fn0 -> 2/3
#   macro = (2/3 + 1 + 2/3) / 3 = 7/9
def test_metric_ceiling_post_type():
    gold = [post("p1", "launch"), post("p2", "promo"), post("p3", "other"), post("p4", "launch")]
    model = [post("p1", "promo"), post("p2", "promo"), post("p3", "other"), post("p4", "launch")]
    unit, score = audit_ceiling.metric_ceiling(
        "post_type", {"posts_test": gold}, predicted_for("posts_test", model), ALIASES, {"p1"}, []
    )
    assert unit == "macro-F1"
    assert score == pytest.approx(7 / 9)


#   gold    {rud} {rud} {} · perfect {ласунка} {rud} {}   (b1 ruled gold-wrong)
#   tp 1 · fp 1 · fn 1 -> 0.5. `Рудь` and `рудь` normalise to the same token, so
#   b2 is a hit across two surface forms; the None row drops out.
def test_metric_ceiling_brands():
    rud_gold = [{"mention": "Рудь", "brand_id": "rud"}]
    gold = [
        post("b1", brands=rud_gold),
        post("b2", brands=rud_gold),
        post("b3"),
        post("b4", brands=None),
    ]
    model = [
        post("b1", brands=[{"mention": "Ласунка"}]),
        post("b2", brands=[{"mention": "рудь"}]),
        post("b3"),
        post("b4", brands=[{"mention": "рудь"}]),
    ]
    unit, score = audit_ceiling.metric_ceiling(
        "brands", {"posts_test": gold}, predicted_for("posts_test", model), ALIASES, {"b1"}, []
    )
    assert unit == "F1"
    assert score == pytest.approx(0.5)


#   The slice is s1 s2 s3; s4 is in the holdout and must not be scored.
#   s1 ruled gold-wrong -> perfect answers (negative, False) against gold
#   (negative, True) and does NOT fix it. s2 and s3 keep gold and do.
#   fixed 2 of 3 -> 2/3
def test_metric_ceiling_sarcasm_pair():
    gold = [
        comment("s1", "negative", sarcasm=True),
        comment("s2", "positive", sarcasm=True),
        comment("s3", "neutral", sarcasm=True),
        comment("s4", "negative", sarcasm=True),
    ]
    model = [
        comment("s1", "negative", sarcasm=False),
        comment("s2", "positive", sarcasm=True),
        comment("s3", "negative", sarcasm=False),
        comment("s4", "positive", sarcasm=False),
    ]
    unit, score = audit_ceiling.metric_ceiling(
        "sarcasm_pair",
        {"sarcasm_holdout": gold},
        predicted_for("sarcasm_holdout", model),
        ALIASES,
        {"s1"},
        ["s1", "s2", "s3"],
    )
    assert unit == "fix-rate"
    assert score == pytest.approx(2 / 3)


def test_universe_restricts_the_slice_head_to_the_slice():
    rows = {"sarcasm_holdout": [{"id": "s1"}, {"id": "s4"}]}
    assert [row["id"] for row in audit_ceiling.universe("sarcasm_pair", rows, ["s1"])] == ["s1"]


def test_metric_ceiling_refuses_a_slice_id_the_holdout_lacks():
    gold = [comment("s1", "negative", sarcasm=True)]
    with pytest.raises(ValueError, match="no gold"):
        audit_ceiling.metric_ceiling(
            "sarcasm_pair",
            {"sarcasm_holdout": gold},
            predicted_for("sarcasm_holdout", gold),
            ALIASES,
            set(),
            ["s1", "s2"],
        )


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
        writer = csv.DictWriter(handle, fieldnames=audit.COLUMNS)
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
        writer = csv.DictWriter(handle, fieldnames=audit.CONTROL_COLUMNS)
        writer.writeheader()
        for row_id, label, verdict in (
            ("c4", "positive", "correct"),
            ("c5", "negative", "incorrect"),
        ):
            writer.writerow(
                {
                    "head": "sentiment",
                    "id": row_id,
                    "text": f"text of {row_id}",
                    "label": label,
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


def test_harness_refuses_a_column_a_spreadsheet_added(pack):
    """The realistic corruption: a round-trip through a spreadsheet adds a column.

    Reading by name would not notice, and the extra column can hold anything the
    ingestion would then silently ignore — including a second opinion.
    """
    manifest, directory, _ = pack
    path = directory / "comments_sentiment.csv"
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text(
        "\n".join([lines[0] + ",Column 8"] + [line + "," for line in lines[1:]]) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match=r"unknown column\(s\) \['Column 8'\]"):
        audit_ceiling.main(["--manifest", str(manifest)])


def test_harness_refuses_a_missing_column(pack):
    manifest, directory, _ = pack
    path = directory / "control.csv"
    lines = [line.rsplit(",", 1)[0] for line in path.read_text(encoding="utf-8").splitlines()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match=r"missing column\(s\) \['notes'\]"):
        audit_ceiling.main(["--manifest", str(manifest)])
