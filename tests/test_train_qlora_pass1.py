"""The pass-1 seam of the trainer: the masked encode, the weighted sampler, and the dataset pin.

Every branch here is driven at $0 on a bare checkout — no torch, no weights, no pod. The fakes are
deliberately literal: a character-level tokenizer makes the supervised span countable, and a fake
`peft` lets the pass-1 loader be DRIVEN rather than read, because the thing worth proving about it
is which of `local_llm`'s two loaders it calls ([[a_stub_replaces_the_guard_it_should_trigger]]).
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import train_qlora as trainer  # noqa: E402

from market_pulse import local_llm, prompts  # noqa: E402

ARM_A = REPO_ROOT / "results" / "pass1_sft_arm_a.jsonl"
ARM_B = REPO_ROOT / "results" / "pass1_sft_arm_b.jsonl"
CONFIG = REPO_ROOT / "config" / "qlora.yaml"


def rows(subject_types: list) -> list[dict]:
    return [{"subject_type": one} for one in subject_types]


def sft_row(msg_id: int = 21626, subject_type: str = "сеть_ритейлер") -> dict:
    target = (
        json.dumps({"msg_id": msg_id, "subject_type": subject_type}, ensure_ascii=False)[:-1]
        + ', "subject_id": null, "stance": null}'
    )
    # through the value AND the separator that closes it — D3a's boundary
    learn = target.index(', "subject_id"') + 1
    return {
        "id": f"@ch:1#{msg_id}",
        "msg_id": msg_id,
        "prompt": "a rendered pass-1 request",
        "target": target,
        "learn_chars": learn,
        "subject_type": subject_type,
        "task": prompts.PASS1_TASK,
    }


class FakeTokenizer:
    """One token per character, so the supervised span is countable by hand."""

    pad_token_id = 7
    eos_token_id = 9

    def apply_chat_template(self, messages, tokenize=False, **kwargs):
        assert kwargs == local_llm.CHAT_TEMPLATE
        return "<t>" + messages[0]["content"] + "<m>"

    def __call__(self, text, add_special_tokens=False, return_offsets_mapping=False):
        out = {"input_ids": [ord(one) % 997 for one in text]}
        if return_offsets_mapping:
            out["offset_mapping"] = [(index, index + 1) for index in range(len(text))]
        return out


class MergingTokenizer(FakeTokenizer):
    """A tokenizer whose merges straddle the boundary: one token covers the cut."""

    def __init__(self, cut: int):
        self.cut = cut

    def __call__(self, text, add_special_tokens=False, return_offsets_mapping=False):
        if not return_offsets_mapping:
            return {"input_ids": [ord(one) % 997 for one in text]}
        spans = []
        index = 0
        while index < len(text):
            width = 2 if index == self.cut - 1 else 1
            spans.append((index, min(index + width, len(text))))
            index += width
        return {
            "input_ids": [ord(text[start]) % 997 for start, _ in spans],
            "offset_mapping": spans,
        }


class BlindTokenizer(FakeTokenizer):
    def __call__(self, text, add_special_tokens=False, return_offsets_mapping=False):
        return {"input_ids": [1, 2, 3]}


# --- the sampler ------------------------------------------------------------


def test_class_weights_are_the_pre_registered_formula_capped():
    table = trainer.class_weights(rows(["a"] * 300 + ["b"] * 100 + [None] * 2))
    assert table["a"] == round(402 / (5 * 300), 6)
    assert table["b"] == round(402 / (5 * 100), 6)
    assert table["null"] == trainer.PASS1_WEIGHT_CAP  # 402/(5*2) = 40.2, capped
    assert trainer.PASS1_K == 5


def test_the_weighted_sampler_draws_the_dataset_s_own_size_per_epoch():
    """The property the registered step count rests on: n draws, not a balanced n."""
    weights = [1.0] * 90 + [8.0] * 10
    order = trainer.sampling_order(100, weights, seed=42)
    assert len(order) == 100
    assert all(0 <= index < 100 for index in order)
    rare = sum(1 for index in order if index >= 90)
    assert rare > 10  # the rare class really is oversampled...
    assert len(order) == 100  # ...and the epoch is still the dataset's own length


def test_the_default_sampler_is_the_shuffle_it_has_always_been():
    order = trainer.sampling_order(50, None, seed=42)
    assert sorted(order) == list(range(50))
    assert order != list(range(50))


def test_both_sampler_branches_are_deterministic_in_the_seed():
    for weights in (None, [1.0] * 20 + [4.0] * 5):
        assert trainer.sampling_order(25, weights, 7) == trainer.sampling_order(25, weights, 7)
        assert trainer.sampling_order(25, weights, 7) != trainer.sampling_order(25, weights, 8)


# --- the masked encode ------------------------------------------------------


def test_encode_pass1_supervises_the_head_and_masks_the_unlabelled_tail():
    row = sft_row()
    encoded = trainer.encode_pass1(FakeTokenizer(), row, max_seq_len=4096)
    prompt_width = len("<t>" + row["prompt"] + "<m>")
    labels = encoded["labels"]
    assert len(labels) == prompt_width + len(row["target"])
    assert labels[:prompt_width] == [-100] * prompt_width
    supervised = [one for one in labels[prompt_width:] if one != -100]
    assert len(supervised) == row["learn_chars"]
    assert labels[prompt_width + row["learn_chars"]] == -100  # the tail starts here
    assert encoded["input_ids"][prompt_width:] == [ord(one) % 997 for one in row["target"]]


def supervised_text(tokenizer, row: dict) -> str:
    """The characters of the target that survive the mask, as a string.

    Counting surviving TOKENS cannot see this tightening: a merge that is masked and a merge that is
    supervised whole both change the count by one, and the question is which CHARACTERS are left
    ([[check_granularity_matches_the_claim]]).
    """
    encoded = trainer.encode_pass1(tokenizer, row, max_seq_len=4096)
    prompt_width = len("<t>" + row["prompt"] + "<m>")
    spans = tokenizer(row["target"], return_offsets_mapping=True)["offset_mapping"]
    return "".join(
        row["target"][start:end]
        for (start, end), label in zip(spans, encoded["labels"][prompt_width:])
        if label != -100
    )


def test_the_quote_and_comma_merge_is_supervised_whole_and_the_old_boundary_ate_it():
    """D3a's tightening, with the boundary it replaced as the negative control.

    `MergingTokenizer(learn - 1)` is the real merge: one token covering the value's closing quote
    and the separator after it. Under the boundary this run registers that token ENDS on the cut and
    is supervised whole. Under the boundary before it — one character earlier — the same token ends
    PAST the cut, is masked, and the label loses its closing quote out of the loss. Same tokenizer,
    same row, two boundaries: the assertion is the difference between them
    ([[guard_selftest_negative_control]]).
    """
    row = sft_row()
    merge_at = row["learn_chars"] - 1
    kept = supervised_text(MergingTokenizer(merge_at), row)
    assert kept.endswith(f'"сеть_ритейлер"{trainer.SUPERVISED_SEPARATOR}')

    eroded = supervised_text(MergingTokenizer(merge_at), {**row, "learn_chars": merge_at})
    assert eroded.endswith("сеть_ритейлер")
    assert not eroded.endswith('сеть_ритейлер"')


def test_a_token_that_reaches_past_the_separator_is_still_masked():
    """The rule still errs toward supervising LESS — the tightening moved the cut, not the rule.

    A merge that starts ON the separator ends past the boundary and is dropped, so the separator can
    still go unsupervised. What it can no longer do is take the value's own tail with it.
    """
    row = sft_row()
    kept = supervised_text(MergingTokenizer(row["learn_chars"]), row)
    assert kept.endswith('"сеть_ритейлер"')
    assert not kept.endswith(trainer.SUPERVISED_SEPARATOR)


def test_the_separator_the_builder_writes_is_the_one_the_trainer_masks_on():
    """Two files, one constant. The trainer does not import the builder — it runs on the pod, where
    the builder's Mac-side imports do not belong — so the agreement is asserted here instead
    ([[one_constant_answering_two_questions]])."""
    import build_pass1_sft as builder

    assert builder.SEPARATOR == trainer.SUPERVISED_SEPARATOR


def test_encode_pass1_refuses_a_tokenizer_that_cannot_locate_the_span():
    with pytest.raises(SystemExit, match="no offset mapping"):
        trainer.encode_pass1(BlindTokenizer(), sft_row(), max_seq_len=4096)


def test_encode_pass1_refuses_a_row_over_the_frozen_ceiling():
    with pytest.raises(SystemExit, match="max_seq_len"):
        trainer.encode_pass1(FakeTokenizer(), sft_row(), max_seq_len=8)


def test_a_learn_chars_of_zero_would_train_on_nothing_and_is_refused():
    row = {**sft_row(), "learn_chars": 0}
    with pytest.raises(SystemExit, match="every target token is masked"):
        trainer.encode_pass1(FakeTokenizer(), row, max_seq_len=4096)


# --- the dataset and its pin ------------------------------------------------


def write(tmp_path: Path, rows_out: list[dict]) -> Path:
    path = tmp_path / "sft.jsonl"
    path.write_text(
        "".join(json.dumps(one, ensure_ascii=False, sort_keys=True) + "\n" for one in rows_out),
        encoding="utf-8",
    )
    return path


def test_load_sft_refuses_a_target_the_parser_cannot_read(tmp_path):
    row = {**sft_row(), "target": '{"msg_id": 21626, "subject_type": "сеть_ритейлер"}'}
    with pytest.raises(prompts.ParseError):
        trainer.load_sft(write(tmp_path, [row]))


def test_load_sft_refuses_a_learn_chars_that_stops_short_of_the_label(tmp_path):
    """The defect a mask can have and a suite cannot see: it goes green and trains on nothing."""
    row = sft_row()
    with pytest.raises(SystemExit, match="does not end at"):
        trainer.load_sft(write(tmp_path, [{**row, "learn_chars": 12}]))


def test_load_sft_refuses_the_boundary_this_run_replaced(tmp_path):
    """The old boundary — ON the value, one character short of the separator — is now a REFUSAL.

    Without this the guard would accept both boundaries, a regenerated dataset could ship the old
    one, and nothing in the suite would say which of the two was trained.
    """
    row = sft_row()
    with pytest.raises(SystemExit, match="does not end at"):
        trainer.load_sft(write(tmp_path, [{**row, "learn_chars": row["learn_chars"] - 1}]))


def test_load_sft_refuses_a_learn_chars_that_runs_past_the_separator(tmp_path):
    """The mirror of the short boundary: one that starts teaching the fields nobody labelled."""
    row = sft_row()
    past = row["target"].index('"subject_id"') + len('"subject_id"')
    with pytest.raises(SystemExit, match="does not end at"):
        trainer.load_sft(write(tmp_path, [{**row, "learn_chars": past}]))


def test_load_sft_refuses_a_row_under_another_prompt(tmp_path):
    with pytest.raises(SystemExit, match="is not"):
        trainer.load_sft(write(tmp_path, [{**sft_row(), "task": "reader_thread_gm4_v5"}]))


def test_load_sft_refuses_two_rows_with_one_id(tmp_path):
    with pytest.raises(SystemExit, match="share an id"):
        trainer.load_sft(write(tmp_path, [sft_row(), sft_row()]))


def test_build_pass1_refuses_a_dataset_the_record_does_not_register(tmp_path):
    """A path is not an identity: the bytes have to be the ones the registration named."""
    import yaml

    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    with pytest.raises(SystemExit, match="not a registered dataset"):
        trainer.build_pass1(config, write(tmp_path, [sft_row()]), weighted=False)


@pytest.mark.parametrize("path,arm", [(ARM_A, "a"), (ARM_B, "b")])
def test_build_pass1_accepts_the_shipped_arms_and_names_which_one(path, arm):
    import yaml

    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    built, record = trainer.build_pass1(config, path, weighted=True)
    assert built["kind"] == "pass1" and built["weighted"] is True
    assert built["carve"] == []
    assert record["arm"] == arm
    assert record["n_train"] == len(built["train"])
    assert record["class_weights"] == trainer.class_weights(built["train"])
    assert "TEAM LEAD" in record["labelled_by"]
    assert record["prompt_sha256"] == {
        prompts.PASS1_TASK: prompts.prompt_sha256(prompts.PASS1_TASK)
    }


def test_the_default_arm_carries_no_weights_and_says_so():
    import yaml

    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    built, record = trainer.build_pass1(config, ARM_A, weighted=False)
    assert built["weighted"] is False
    assert record["class_weights"] is None
    assert "unchanged" in record["sampler"]


# --- the command line -------------------------------------------------------


def test_the_two_experiments_cannot_be_run_as_one():
    with pytest.raises(SystemExit, match="Pick one"):
        trainer.main(["--data", str(ARM_A), "--with-plast", "--build-only"])


def test_class_weights_without_a_pass1_dataset_is_refused():
    with pytest.raises(SystemExit, match="needs the pass-1 dataset"):
        trainer.main(["--class-weights", "--build-only"])


def test_build_only_on_an_arm_prints_its_provenance_and_touches_no_gpu(capsys):
    assert trainer.main(["--data", str(ARM_B), "--class-weights", "--build-only"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["arm"] == "b"
    assert printed["dataset"]["file"] == "results/pass1_sft_arm_b.jsonl"
    assert printed["class_weights"]["молочный_бренд"] == 8.0


# --- which loader the pass-1 branch calls -----------------------------------


class StubModel:
    class Config:
        use_cache = True

    def __init__(self):
        self.config = StubModel.Config()

    def named_modules(self):
        return [
            ("language_model.layers.0.self_attn.q_proj", None),
            ("language_model.layers.0.mlp.down_proj", None),
            ("vision_tower.blocks.0.attn.q_proj", None),
        ]


@pytest.fixture
def fake_peft(monkeypatch):
    import types

    module = types.ModuleType("peft")
    module.LoraConfig = lambda **kwargs: kwargs
    module.PeftModel = type("PeftModel", (), {})
    module.get_peft_model = lambda model, config: model
    module.prepare_model_for_kbit_training = lambda model, use_gradient_checkpointing: model
    monkeypatch.setitem(sys.modules, "peft", module)
    return module


def test_the_pass1_branch_trains_through_the_processor_the_eval_path_serves(
    monkeypatch, fake_peft, capsys
):
    """Train/eval format identity, held by construction: the chat template is the processor's."""
    import yaml

    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    called = []
    monkeypatch.setattr(
        local_llm,
        "load_captioner",
        lambda **kwargs: (called.append(("captioner", kwargs)), (FakeTokenizer(), StubModel()))[1],
    )
    monkeypatch.setattr(
        local_llm,
        "load",
        lambda **kwargs: (called.append(("tokenizer", kwargs)), (FakeTokenizer(), StubModel()))[1],
    )
    trainer.load_for_training(config, pass1=True)
    assert [name for name, _ in called] == ["captioner"]
    assert called[0][1]["revision"] == config["base"]["revision"]

    called.clear()
    trainer.load_for_training(config, pass1=False)
    assert [name for name, _ in called] == ["tokenizer"]


def test_the_pad_id_is_found_through_a_processor_as_well_as_a_tokenizer():
    class Processor:
        tokenizer = FakeTokenizer()

    assert trainer.pad_id_of(FakeTokenizer()) == 7
    assert trainer.pad_id_of(Processor()) == 7
