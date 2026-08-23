"""`lora-c-run`: the close debts, the sibling trainer, and the pre-pod arithmetic.

Every guard is driven in BOTH directions. The two step-0.5 tests exist because
`docs/reports/lora-c-close.md` §«Open» named them as the shape a test replaces: a quotation guard
nobody had watched refuse, and a threshold living as a module constant beside the law that fixed it.
"""

import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import tokenize_lora_c_rows as tokens  # noqa: E402
import train_qlora as trainer  # noqa: E402
import train_qlora_v3 as sibling  # noqa: E402
import write_lora_c_prereg as prereg  # noqa: E402
from market_pulse import pass1_v3, prompts  # noqa: E402

from test_train_qlora_pass1 import FakeTokenizer  # noqa: E402

PREREG = REPO_ROOT / "results" / "prereg_lora_c.json"
TRAIN = REPO_ROOT / "results" / "pass1_sft_v3_train.jsonl"
TOKENS = REPO_ROOT / "results" / "lora_c_tokens.json"
STATUS = REPO_ROOT / "docs" / "STATUS.md"


# ---------------------------------------------------------------- step 0.5 (1)


@pytest.mark.parametrize("name", ("RULING_V", "RULING_K"))
def test_the_status_quotation_refuses_a_paraphrase(name, tmp_path, monkeypatch):
    """`quoted`'s twin of the control `quoted_spec` got in Dv783.

    The two rulings are this registration's entire authority, and until now the grep that holds them
    had only ever been driven on text that satisfies it — a guard nobody has seen refuse is a guard
    nobody has tested ([[guard_selftest_negative_control]]). The planted paraphrase swaps the
    guillemets both rulings quote inside, which is exactly the class of drift a verbatim grep exists
    to catch and which whitespace normalisation cannot forgive.
    """
    ruling = getattr(prereg, name)
    assert "«" in ruling
    copy = tmp_path / "STATUS.md"
    copy.write_text(STATUS.read_text(encoding="utf-8").replace("«", '"'), encoding="utf-8")
    monkeypatch.setattr(prereg, "STATUS", copy)
    with pytest.raises(SystemExit, match="this quotation is not in STATUS.md"):
        prereg.quoted(ruling)
    monkeypatch.setattr(prereg, "STATUS", STATUS)
    assert prereg.quoted(ruling) == ruling


# ---------------------------------------------------------------- step 0.5 (2)


def threshold_in(quotation: str) -> int:
    """The one number inside a quotation of law, digit groups and their spaces joined.

    Parsed rather than typed: a second literal here would be a second home for the threshold, which
    is the very thing this test exists to close ([[a_threshold_that_lives_in_prose]]).
    """
    found = {int(re.sub(r"\s", "", one)) for one in re.findall(r"\d[\d\s]*\d|\d", quotation)}
    if len(found) != 1:
        raise AssertionError(f"{sorted(found)} numbers in {quotation!r} — the quote names one")
    return found.pop()


def test_the_stop_threshold_constant_equals_the_law_it_quotes():
    """`STOP_AT` against amendment 3.26 (2), through the registration's own quotation of it.

    `docs/reports/lora-c-close.md` §«Open» 2: the bar's law lives in `docs/SPEC.md` and its number
    lives as a module constant in `scripts/tokenize_lora_c_rows.py`, with nothing between them. The
    quotation is `quoted_spec`-checked on every build of the record, so binding the constant to the
    quotation binds it to the law ([[a_registered_threshold_that_is_really_a_function]]).
    """
    record = json.loads(PREREG.read_text(encoding="utf-8"))
    quotation = record["authority"]["amendment_3_26"]["2_the_stop_threshold_reads_the_true_count"]
    law = threshold_in(quotation)
    assert tokens.STOP_AT == law
    # the parse is a real reading and not a constant that happens to agree
    assert threshold_in(quotation.replace("8", "9")) != law

    census = json.loads(TOKENS.read_text(encoding="utf-8"))
    assert census["stop_threshold"] == law
    over = census["rows_over_the_stop_threshold"]
    assert over["which_the_amendment_names"].startswith("by_the_true_count")
    # every row over the threshold is among the widest five, so the count is re-derivable here
    assert sum(one["pod_count"] > law for one in census["widest_rows"]) == over["by_the_true_count"]
    assert str(law)[0] in census["verdict"] and census["max_seq_len"] > law


# ------------------------------------------------------------------------- D1


def a_row(**over):
    row = json.loads(TRAIN.read_text(encoding="utf-8").splitlines()[0])
    row.update(over)
    return row


def a_dataset(tmp_path: Path, rows: list[dict], name: str = "rows.jsonl") -> Path:
    out = tmp_path / name
    out.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    return out


def test_the_sibling_accepts_the_registered_arm_a_dataset():
    """Guard 1 and guard 2, both re-bound, on the bytes the registration names."""
    config = {"training": {"max_seq_len": 3072}}
    built, provenance = sibling.build_pass1_v3(config, TRAIN, weighted=True)
    assert len(built["train"]) == 506
    assert built["carve"] == [] and built["kind"] == "pass1" and built["weighted"]
    assert provenance["task"] == pass1_v3.PASS1_TASK_V3
    assert provenance["prompt_sha256"] == {
        pass1_v3.PASS1_TASK_V3: pass1_v3.prompt_sha256(pass1_v3.PASS1_TASK_V3)
    }
    assert provenance["registration"]["file"] == "results/prereg_lora_c.json"
    assert sorted(provenance["class_weights"]) == [
        "null",
        "категория_личное",
        "не_наш_рынок",
        "сеть_ритейлер",
    ]


def test_the_pinned_task_constant_is_put_back():
    """The swap is scoped: line B's trainer reads v1 again the moment the call returns."""
    was = prompts.PASS1_TASK
    with sibling.the_task_is_v3():
        assert prompts.PASS1_TASK == pass1_v3.PASS1_TASK_V3
    assert prompts.PASS1_TASK == was == "pass1_comment_gm4_v1"


def test_the_pinned_trainer_still_refuses_a_v3_row():
    """The re-bind is the sibling's, not an edit: `train_qlora` is exactly as sealed."""
    with pytest.raises(SystemExit, match="is not 'pass1_comment_gm4_v1'"):
        trainer.load_sft(TRAIN)


def test_the_sibling_refuses_a_v1_task_row(tmp_path):
    path = a_dataset(tmp_path, [a_row(task=prompts.PASS1_TASK)])
    with pytest.raises(SystemExit, match="is not 'pass1_comment_gm4_v3'"):
        sibling.build_pass1_v3({"training": {}}, path, weighted=True)


def test_the_sibling_refuses_an_unregistered_dataset(tmp_path):
    """One row short of the registered file is a different file, and the sha says so."""
    rows = [json.loads(one) for one in TRAIN.read_text(encoding="utf-8").splitlines() if one]
    path = a_dataset(tmp_path, rows[:-1])
    with pytest.raises(SystemExit, match="not a registered dataset of this line"):
        sibling.build_pass1_v3({"training": {}}, path, weighted=True)


def test_the_sibling_refuses_a_row_over_the_ceiling():
    """`encode_pass1`'s own refusal, reached through the census — the pod's guard, run at $0."""
    row = a_row()
    with pytest.raises(SystemExit, match="against a max_seq_len of 3072"):
        trainer.encode_pass1(FakeTokenizer(), row, 3072)


def test_the_registration_names_no_arm_b_dataset():
    """The 666-row arm B has a registered ROW COUNT and no registered FILE.

    `legs.arm_b.train_rows` is 666 and `population.train` names one file of 506; the 160 synthetic
    rows live in `results/synthetic_pass1_v1.jsonl` in the raw comment shape, with no `prompt`,
    `target` or `learn_chars`, so nothing on disk is arm B's dataset and no producer renders one.
    This test pins the gap rather than papering over it ([[a_registered_bar_may_have_no_producer]]).
    """
    record = json.loads(PREREG.read_text(encoding="utf-8"))
    assert record["legs"]["arm_b"]["train_rows"] == 666
    assert set(sibling.registered_training_shas()) == {"results/pass1_sft_v3_train.jsonl"}
    synthetic = json.loads(
        (REPO_ROOT / "results" / "synthetic_pass1_v1.jsonl")
        .read_text(encoding="utf-8")
        .split("\n")[0]
    )
    assert not {"prompt", "target", "learn_chars"} & set(synthetic)


def _tokenizer_is_obtainable() -> bool:
    try:
        import transformers  # noqa: F401
        from huggingface_hub import try_to_load_from_cache
    except ImportError:
        return False
    return isinstance(
        try_to_load_from_cache(
            "google/gemma-4-31b-it", "chat_template.jinja", revision=tokens.revision()
        ),
        str,
    )


@pytest.mark.skipif(
    not _tokenizer_is_obtainable(),
    reason="the model tokenizer is not on this machine — the census then describes a measurement"
    " this suite cannot re-run",
)
def test_the_census_agrees_with_the_shipped_token_record():
    """The encode census against `results/lora_c_tokens.json`'s count, on the same rows.

    Two instruments over one quantity: the token record tokenizes `apply_chat_template(prompt)` and
    the target directly, and this runs `encode_pass1` — the function that will refuse on the pod.
    They must agree on the widest row and on the headroom, or one of them is not measuring the
    refusal ([[two_instruments_two_inputs]]).
    """
    census = sibling.census(TRAIN)
    shipped = json.loads(TOKENS.read_text(encoding="utf-8"))
    assert census["refused"] == []
    assert census["rows"] == census["encoded"] == shipped["rows"]
    assert census["tokens"]["max"] == shipped["pod_count"]["max"]
    assert census["headroom"] == shipped["headroom_under_the_ceiling"]["by_the_true_count"]


def test_the_arm_is_read_from_the_record_and_a_tie_is_refused():
    """`arm_of` is a lookup in the registration, and the leg it cannot name it refuses."""
    assert sibling.arm_of(506) == "arm_a"
    assert sibling.arm_of(666) == "arm_b"
    with pytest.raises(SystemExit, match="a training run whose arm"):
        sibling.arm_of(1)


def test_the_derivation_solves_the_cap_inequality_backwards():
    """The pre-pod arithmetic, re-derived here from the record's own terms.

    A verdict in prose is not the verdict ([[gate_verdicts_need_an_artifact]]): the break-even is
    recomputed from the fixed part, the cap and the step count, and the reading that matters — that
    both s/step readings this repo holds sit ABOVE it — is asserted rather than described.
    """
    money = json.loads(PREREG.read_text(encoding="utf-8"))["money"]
    derived = money["pre_pod_arithmetic"]
    cap, steps = money["cap_usd_all_in"], derived["steps"]["total"]
    assert steps == derived["steps"]["arm_a"] + derived["steps"]["arm_b"] == 144
    for price, column in derived["at_each_price"].items():
        budget = cap / float(price) * 3600
        assert round(budget, 1) == column["budget_seconds"]
        left = budget - derived["fixed_seconds"]["total"]
        assert round(left, 1) == column["left_for_training_seconds"]
        assert round(left / steps, 2) == column["break_even_seconds_per_step"]
        # the finding: neither reading this repo holds fits under the bar the cap sets
        assert column["break_even_seconds_per_step"] < prereg.SECONDS_PER_STEP_REGISTERED
        assert column["break_even_seconds_per_step"] < prereg.SECONDS_PER_STEP_MEASURED
    assert derived["hard_stop_seconds"] == round(
        cap / derived["price_usd_per_hour"]["worst"] * 3600, 1
    )
    # and the quotation the whole derivation stands on is law, grepped, not paraphrased
    assert prereg.quoted_spec(derived["authority"]["clause"]) == prereg.AMENDMENT_325_1_PRICE
