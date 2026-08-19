"""The pass-1 SFT datasets — the transport's own request, the team lead's answer, and the mask.

Three properties carry the money here. The pairs are the request the eval path sends, rebuilt from
the frozen prompt and re-parsed by the parser the pod reads replies with. The supervised span stops
at the label, so the two fields nobody labelled teach nothing — the test below computes what
training them WOULD cost against the sealed bar, because that arithmetic is the reason the mask
exists. And every row fits `config/qlora.yaml`'s frozen `max_seq_len`, bounded here at $0 instead
of discovered inside a training loop on a billed pod.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass1_sft as sft  # noqa: E402

from market_pulse import prompts  # noqa: E402

GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text("utf-8"))
BASE_VERDICT = json.loads((REPO_ROOT / "results" / "pass1_probe_b_verdict.json").read_text("utf-8"))


@pytest.fixture(scope="module")
def state():
    return sft.measure()


@pytest.fixture(scope="module")
def built(state):
    return sft.build(state)


def test_every_target_is_read_back_by_the_parser_the_pod_reads_replies_with(state):
    for row in state["rows"]:
        parsed = prompts.parse_pass1(row["target"], msg_id=row["msg_id"])
        assert parsed["subject_type"] == row["subject_type"]
        assert parsed["msg_id"] == row["msg_id"]
        assert parsed["subject_id"] is None and parsed["stance"] is None


def test_every_prompt_is_the_frozen_pass1_request(state):
    for row in state["rows"][:40]:
        assert row["prompt"].startswith(prompts.PASS1_COMMENT_PROMPT)
        assert row["prompt"].count("<comment ") == 1
        assert f'<comment msg_id="{row["msg_id"]}"' in row["prompt"]
        assert row["task"] == prompts.PASS1_TASK


def test_the_supervised_span_ends_at_the_label_and_never_reaches_the_unlabelled_fields(state):
    for row in state["rows"]:
        head = row["target"][: row["learn_chars"]]
        tail = row["target"][row["learn_chars"] :]
        label = "null" if row["subject_type"] is None else f'"{row["subject_type"]}"'
        assert head.endswith(label), row["id"]
        assert "subject_id" not in head and "stance" not in head
        assert tail.startswith(', "subject_id": null') and tail.endswith("}")


def test_training_the_unlabelled_stance_would_put_the_bar_out_of_reach():
    """Why the mask exists, computed rather than argued.

    Three of the fourteen sealed gold rows score `stance` against a NON-NULL gold value, so a
    target that taught `stance: null` would put all three out of reach whatever the model answered
    about the subject — 21629 scores stance alone, and the other two score it beside subject_type.
    14 − 3 = 11 against a threshold of 12: the gate would be unreachable before the pod was
    created. Two of the three are rows the base agrees on TODAY, which is what the arm would be
    spending them for.
    """
    scored_stance = [row for row in GOLD["per_comment"] if "stance" in row["scored_fields"]]
    assert len(scored_stance) == 3
    assert {row["msg_id"]: row["stance"] for row in scored_stance} == {
        21626: "negative",
        21629: "positive",
        580124: "negative",
    }
    assert all(row["stance"] is not None for row in scored_stance)
    agreed = {
        row["msg_id"]
        for row in BASE_VERDICT["bars"]["P1_per_comment_agreement"]["rows"]
        if row["agreed"]
    }
    assert {row["msg_id"] for row in scored_stance} & agreed == {21626, 21629}
    reachable = len(GOLD["per_comment"]) - len(scored_stance)
    assert reachable == 11 < BASE_VERDICT["bars"]["P1_per_comment_agreement"]["minimum_agreed"]


def test_no_row_can_exceed_the_frozen_max_seq_len(state):
    assert state["max_seq_len"] == 1408
    assert all(row["bound_tokens"] <= state["max_seq_len"] for row in state["rows"])
    assert all(row["bound_tokens"] > state["max_seq_len"] for row in state["dropped"])


def test_the_bound_is_the_worst_ratio_probe_b_measured_not_the_mean(state):
    per = state["ratio"]
    assert per["rows"] == 64
    assert 0.29 < per["tokens_per_char_max"] < 0.30
    assert "maximum" in per["rule"]
    # and it really is the maximum of the file, re-derived here off the same two records
    pack = json.loads((REPO_ROOT / "results" / "pass1_probe_b_pack.json").read_text("utf-8"))
    chars = {one["id"]: int(one["rendered_chars"]) for one in pack["items"]}
    rows = [
        json.loads(line)
        for line in (REPO_ROOT / "results" / "pass1_probe_b_rows.jsonl")
        .read_text("utf-8")
        .splitlines()
        if line
    ]
    worst = max(int(row["usage"]["prompt_tokens"]) / chars[row["id"]] for row in rows)
    assert round(worst, 6) == per["tokens_per_char_max"]


def test_arm_a_is_a_subset_of_arm_b_and_that_is_the_whole_ablation(state):
    a = {row["id"] for row in sft.arm_rows(state, "a")}
    b = {row["id"] for row in sft.arm_rows(state, "b")}
    assert a < b
    assert {row["pack"] for row in sft.arm_rows(state, "a")} == {"r1"}
    assert {row["pack"] for row in sft.arm_rows(state, "b")} == {"r1", "r2"}


def test_no_gold_row_and_no_exam_thread_is_trained_on(state):
    gold = {int(row["msg_id"]) for row in GOLD["per_comment"]}
    r1 = json.loads((REPO_ROOT / "results" / "pass1_label_pack_r1.json").read_text("utf-8"))
    exam = set(r1["exclusion"]["threads"])
    everything = state["rows"] + state["dropped"]
    assert [row for row in everything if row["msg_id"] in gold] == []
    assert [row for row in everything if row["thread"] in exam] == []


def test_the_sampler_weights_are_the_pre_registered_formula(state):
    """One implementation: the builder publishes what the trainer will sample with."""
    import train_qlora

    for arm in ("a", "b"):
        rows = sft.arm_rows(state, arm)
        assert sft.sampler_weights(rows) == train_qlora.class_weights(rows)
        weights = sft.sampler_weights(rows)
        assert weights["молочный_бренд"] == 8.0  # the cap bites on the one row of the class
        assert all(0 < value <= 8.0 for value in weights.values())
        total = len(rows)
        counts = {name: n for name, n in sft.distribution(rows).items() if n}
        for name, n in counts.items():
            assert weights[name] == round(min(total / (5 * n), 8.0), 6)


def test_the_record_names_the_context_the_gate_carries_and_the_training_set_does_not(built):
    """The finding this record exists to publish, asserted so it cannot quietly stop being true."""
    record, _ = built
    gate = record["census"]["the_gate_s_own_rows"]
    arm_b = record["census"]["arms"]["b"]["context"]
    assert gate["n"] == 14 and gate["with_an_entity_block"] == 12
    assert record["census"]["eval_pack"]["with_an_entity_block"] == 55
    assert arm_b["with_an_entity_block"] < arm_b["of"] * 0.1


def test_the_datasets_rebuild_byte_identical(tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"
    assert sft.main(["--outdir", str(first)]) == 0
    assert sft.main(["--outdir", str(second)]) == 0
    for name in (*sft.ARM_NAMES.values(), sft.RECORD_NAME):
        assert (first / name).read_bytes() == (second / name).read_bytes(), name
    assert str(tmp_path) not in (first / sft.RECORD_NAME).read_text("utf-8")


def test_the_shipped_datasets_are_what_the_producer_builds_today(tmp_path):
    assert sft.main(["--outdir", str(tmp_path)]) == 0
    for name in (*sft.ARM_NAMES.values(), sft.RECORD_NAME):
        assert (tmp_path / name).read_bytes() == (REPO_ROOT / name).read_bytes(), name


def test_the_census_run_writes_nothing(capsys):
    before = sorted((one.name, one.stat().st_mtime_ns) for one in (REPO_ROOT / "results").iterdir())
    assert sft.main(["--census"]) == 0
    after = sorted((one.name, one.stat().st_mtime_ns) for one in (REPO_ROOT / "results").iterdir())
    assert after == before
    out = capsys.readouterr().out
    assert "DROPPED FOR LENGTH" in out and "wrote" not in out


def test_the_producer_pins_itself():
    record = json.loads((REPO_ROOT / "results" / "pass1_sft.json").read_text("utf-8"))
    live = subprocess.run(
        ["shasum", "-a", "256", "scripts/build_pass1_sft.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()[0]
    assert record["producer"]["sha256"] == live
    assert record["producer"]["script"] == "scripts/build_pass1_sft.py"
