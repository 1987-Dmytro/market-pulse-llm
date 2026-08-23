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
SYNTH = trainer.assemble(True, CARVE, SEED)  # the with-пласт arm (4.5h2's one variable)


def test_answer_writes_the_gold_in_the_schema_the_parser_reads():
    """The format-identity invariant, on every row of both arms.

    A target the eval parser cannot read back is a target the model would be
    trained to produce and the scorer would count as a parse failure.
    """
    for row in SYNTH["train"] + SYNTH["carve"]:
        rendered = trainer.rendering(row["task"])
        assert prompts.parse_reply(rendered, row["target"]) == json.loads(row["target"])


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
    """Carving before the пласт joins is what keeps the arms one path apart."""
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


def test_the_two_arms_differ_by_exactly_the_plast_rows():
    added = trainer.assert_arm_identity(REAL["train"], SYNTH["train"])
    assert len(added) == len(SYNTH["train"]) - len(REAL["train"]) == 1286
    plast = {row["id"] for row in trainer.load(trainer.PLAST)}
    assert set(added) <= plast


def test_arm_identity_refuses_a_second_difference():
    """The negative control: without it the assert above is decoration.

    One real row dropped from the with-пласт arm is invisible in the counts if
    only the added side is checked — the arm would still be 1,285 rows longer.
    """
    tampered = [row for row in SYNTH["train"] if row["id"] != REAL["train"][0]["id"]]
    with pytest.raises(SystemExit, match="differ by more than the пласт"):
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
    sources = {path for paths in trainer.SOURCES.values() for path in paths} | {trainer.PLAST}
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


# --- resume, the half no stub can prove ---------------------------------------


def test_assert_resumable_accepts_a_state_that_covers_every_trainable_parameter():
    trainer.assert_resumable({"optimizer": {"state": {0: {}, 1: {}, 2: {}}}}, 3)


def test_assert_resumable_refuses_a_state_from_a_different_parameter_list():
    """`load_state_dict` maps by index. A mismatch puts the wrong momentum on the
    wrong tensor and raises nothing at all — so this has to raise instead."""
    with pytest.raises(SystemExit, match="state for 3 parameters and this model has 4"):
        trainer.assert_resumable({"optimizer": {"state": {0: {}, 1: {}, 2: {}}}}, 4)


# --- 4.5h2: the taxonomy the arms are trained in, and the one the gate scores ---


def test_both_arms_train_on_the_taxonomy_v2_sources():
    """SPEC amendment 3.9 (1). The v1 pair holds ZERO `service` rows while the gate
    scores against a v4 test set that IS taxonomy v2 — an arm trained on them would be
    the only arm never shown the class it is graded on, and the selection rule would
    measure taxonomy exposure and record it as data volume."""
    assert [path.name for path in trainer.SOURCES["T1"]] == [
        "comments_train_tax2.jsonl",
        "sarcasm_candidates_tax2.jsonl",
    ]
    for row in REAL["train"]:
        assert not row["source"].endswith(("comments_train.jsonl", "sarcasm_candidates.jsonl"))


def test_the_sixth_class_is_in_both_arms_and_in_the_right_proportion():
    """The confound, counted rather than argued: the label vocabulary on each side."""

    def service(rows):
        return sum(1 for row in rows if "service" in json.loads(row["target"]).get("intents", []))

    assert service(REAL["train"]) > 0
    assert service(SYNTH["train"]) > service(REAL["train"])
    v1 = trainer.FROZEN / "comments_train.jsonl", trainer.ANNOTATION / "sarcasm_candidates.jsonl"
    assert (
        sum(1 for path in v1 for row in trainer.load(path) if "service" in row["intents"]) == 0
    ), "the v1 sources are the confound this amendment removes"


def test_the_row_counts_are_the_precheck_s_and_the_carve_is_shared():
    """`results/precheck_45h.json` priced the ablation at these two numbers, and
    amendment 3.9 (2) requires the arms to hold out the identical carve."""
    assert len(REAL["train"]) == 2171
    assert len(SYNTH["train"]) == 3457
    assert trainer.content_hash(REAL["carve"]) == trainer.content_hash(SYNTH["carve"])


def test_every_comment_example_carries_the_post_it_renders_with():
    """The rendering is with-post, so a row without one would raise at build_messages —
    on the pod, after the weights. And `content_hash` covers the post, so two runs whose
    raw store differed cannot share a dataset hash."""
    for row in SYNTH["train"]:
        if row["task"] == "T1":
            assert set(row["post"]) == {"parent", "caption", "caption_kind"}
        else:
            assert row["post"] is None
    stripped = [dict(row, post=None) for row in REAL["train"]]
    assert trainer.content_hash(stripped) != trainer.content_hash(REAL["train"])


def test_the_run_renders_the_version_it_is_aimed_at():
    assert trainer.TESTSET_VERSION == "v4"
    assert trainer.rendering("T1") == prompts.REVISIONS["v4"]["T1"] == "T1v2_with_post"
    assert trainer.rendering("T2") == "T2"


def test_the_arm_names_do_not_collide_with_phase_4_s():
    """`records.arm_record` refuses two rows for one arm name, and both phases append
    to `results/baselines.json`."""
    assert set(trainer.ARM.values()) == {"without-plast", "with-plast"}
    assert not set(trainer.ARM.values()) & {"real-only", "with-synthetic"}


def test_the_never_read_list_covers_every_version_of_every_test_file():
    """A list that named only v2 stopped covering the test set the moment v3 was frozen
    beside it — and v4 is what this phase scores."""
    names = {path.name for path in trainer.NEVER_READ}
    for stem in ("comments_test", "posts_test", "sarcasm_holdout"):
        for suffix in ("", "_v3", "_v4"):
            assert f"{stem}{suffix}.jsonl" in names, f"{stem}{suffix}"
    for path in trainer.NEVER_READ:
        assert path.exists(), path


def test_the_provenance_names_the_rendering_the_gate_will_check(tmp_path):
    import yaml

    config = yaml.safe_load((REPO_ROOT / "config" / "qlora.yaml").read_text(encoding="utf-8"))
    _, record = trainer.build(config, True)
    assert record["arm"] == "with-plast"
    assert record["added_source"] == "uplabel_precheck_45g2.jsonl"
    assert record["testset_version"] == "v4"
    assert record["prompt_revision_sha256"] == prompts.revision_sha256("v4")
    # the carry-through, not a second copy of the constant: `config/qlora.yaml` is at revision 2
    # (amendment 3.25 (1)) and a literal here would pin the value in a file that does not own it
    assert record["config"]["training"]["max_seq_len"] == config["training"]["max_seq_len"] == 3072
