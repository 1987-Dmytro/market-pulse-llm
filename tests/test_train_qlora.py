"""The training dataset contract, checked on the real files and without a GPU.

`--build-only` is the whole of it: what enters an arm, what a target looks like,
and what the two arms may differ by. All of that decides a fine-tune the gates
see exactly once, so it is asserted here rather than discovered on a rented
card. Nothing in this file imports torch, transformers or peft.
"""

import ast
import importlib.util
import json
from pathlib import Path

import pytest
from market_pulse import prompts

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "train_qlora.py"
spec = importlib.util.spec_from_file_location("train_qlora", SCRIPT)
trainer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trainer)

CARVE, SEED = 24, 42
REAL = trainer.assemble(False, CARVE, SEED)
SYNTH = trainer.assemble(True, CARVE, SEED)


def test_answer_writes_the_gold_in_the_schema_the_parser_reads():
    """The format-identity invariant, on every row of both arms.

    A target the eval parser cannot read back is a target the model would be
    trained to produce and the scorer would count as a parse failure.
    """
    for row in SYNTH["train"] + SYNTH["carve"]:
        assert prompts.parse_reply(row["task"], row["target"]) == json.loads(row["target"])


def test_answer_normalises_the_way_the_parser_normalises():
    """Repeated intents collapse and sort; a brand keeps its text, not its id."""
    comment = {
        "sentiment": "negative",
        "sarcasm": True,
        "intents": ["price", "taste", "price"],
        "text": "",
    }
    assert json.loads(trainer.answer("T1", comment))["intents"] == ["price", "taste"]
    post = {
        "relevant": True,
        "post_type": "launch",
        "brands": [{"brand_id": "rud", "mention": "  Рудь\n"}],
    }
    assert json.loads(trainer.answer("T2", post))["brands"] == [{"mention": "Рудь"}]


def test_assemble_holds_the_carve_out_of_training():
    ids = {trainer.order(row) for row in REAL["train"]}
    assert len(REAL["carve"]) == CARVE
    assert not ids & {trainer.order(row) for row in REAL["carve"]}


def test_assemble_draws_the_same_carve_for_both_arms():
    """Carving before the synthetic rows join is what keeps the arms one path apart."""
    assert [trainer.order(row) for row in REAL["carve"]] == [
        trainer.order(row) for row in SYNTH["carve"]
    ]


def test_assemble_is_deterministic():
    assert trainer.content_hash(trainer.assemble(False, CARVE, SEED)["train"]) == (
        trainer.content_hash(REAL["train"])
    )


def test_content_hash_is_a_hash_of_the_data_not_of_the_order():
    shuffled = list(reversed(REAL["train"]))
    assert trainer.content_hash(shuffled) == trainer.content_hash(REAL["train"])


def test_the_two_arms_differ_by_exactly_the_synthetic_rows():
    added = trainer.assert_arm_identity(REAL["train"], SYNTH["train"])
    assert len(added) == len(SYNTH["train"]) - len(REAL["train"])
    assert all(row_id.startswith("synthetic:") for row_id in added)


def test_arm_identity_refuses_a_second_difference():
    """The negative control: without it the assert above is decoration.

    One real row dropped from the synthetic arm is invisible in the counts if
    only the added side is checked — the arm would still be 600 rows longer.
    """
    tampered = [row for row in SYNTH["train"] if row["id"] != REAL["train"][0]["id"]]
    with pytest.raises(SystemExit, match="differ by more than the synthetic source"):
        trainer.assert_arm_identity(REAL["train"], tampered)


def test_format_identity_refuses_a_target_the_parser_rejects():
    broken = [dict(REAL["train"][0], target='{"sentiment": "amused"}')]
    with pytest.raises(prompts.ParseError):
        trainer.assert_format_identity(broken)


@pytest.mark.parametrize("path", trainer.NEVER_READ, ids=lambda p: p.name)
def test_training_refuses_to_open_a_frozen_test_input(path):
    """The holdout and the two test sets are seen once, by 4c's gate eval."""
    with pytest.raises(SystemExit, match="never open it"):
        trainer.load(path)


def test_no_training_source_is_a_frozen_test_input():
    sources = {path for paths in trainer.SOURCES.values() for path in paths} | {trainer.SYNTHETIC}
    assert not sources & set(trainer.NEVER_READ)


def test_every_training_row_carries_a_source_and_an_id():
    assert all(row["source"] and row["id"] and row["text"] is not None for row in SYNTH["train"])


def test_unclear_rows_never_enter_a_dataset():
    """The stated assumption, pinned: a row with no decided label teaches none.

    Keyed by (task, id), not by id: 18 posts carry the same `@channel:msg_id` as
    a comment, and the two are different rows with different labels.
    """
    kept = {trainer.order(row) for row in SYNTH["train"] + SYNTH["carve"]}
    for task, paths in trainer.SOURCES.items():
        for path in paths:
            unclear = {(task, row["id"]) for row in trainer.load(path) if row["unclear"]}
            assert not unclear & kept


def test_assemble_refuses_a_repeated_row():
    """A duplicate inside one task would collapse in every arm-comparison set."""
    doubled = dict(trainer.SOURCES, T2=(*trainer.SOURCES["T2"], *trainer.SOURCES["T2"]))
    with pytest.raises(SystemExit, match="repeat"):
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(trainer, "SOURCES", doubled)
            trainer.assemble(False, CARVE, SEED)


def test_the_gpu_extra_never_reaches_module_scope():
    """`--build-only` and this file must both run on a bare checkout."""
    banned = {"torch", "transformers", "bitsandbytes", "accelerate", "peft"}
    for node in ast.parse(SCRIPT.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Import):
            assert not banned & {alias.name.split(".")[0] for alias in node.names}
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in banned
