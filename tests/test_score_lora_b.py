"""D4's verdict, DRIVEN on fabricated arms — the gate, the tie, the ablation and the missing arm.

The scorer will be run exactly once, on evidence that cost money, so every branch of it is exercised
here first on replies this file writes. The replies are built from the eval pack and the sealed gold
so the fabrication is only in WHAT the arm answered, never in which rows it was asked
([[a_frozen_record_is_an_input_to_shipped_code]]).

The branch that matters most is the one no fixture would produce by accident: an arm with no
evidence file is `not_evaluated`, never 0 of 14. A zero there would read a year later as «the
adapter answered and was wrong», and the run that produces it — a milestone STOP before arm B, or a
format smoke that killed an arm — is the ordinary shape of a session that ends early.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import score_lora_b as verdict  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_lora_b.json").read_text("utf-8"))
PACK = json.loads((REPO_ROOT / "results" / "pass1_probe_b_pack.json").read_text("utf-8"))
GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text("utf-8"))
BASE = json.loads((REPO_ROOT / "results" / "pass1_probe_b_verdict.json").read_text("utf-8"))

GOLD_IDS = [int(one["msg_id"]) for one in RECORD["population"]["gold"]["rows"]]
BY_ID = {int(one["msg_id"]): one for one in GOLD["per_comment"]}
BASE_ROWS = {
    int(one["msg_id"]): bool(one["agreed"])
    for one in BASE["bars"]["P1_per_comment_agreement"]["rows"]
}


def answer(item: dict, agree: bool) -> str:
    """A reply that agrees with the gold row, or one that cannot.

    The disagreeing answer is a subject_type the gold row does not carry — never a refusal, because
    a refusal and a disagreement are two different losses and the bar counts them apart.
    """
    msg_id = int(item["msg_id"])
    gold = BY_ID.get(msg_id)
    if gold is not None and agree:
        said = {name: gold.get(name) for name in gold["scored_fields"]}
    else:
        said = {"subject_type": "не_наш_рынок", "subject_id": None, "stance": None}
        if gold is not None and gold.get("subject_type") == "не_наш_рынок":
            said["subject_type"] = "сеть_ритейлер"
    body = {"msg_id": msg_id, "subject_type": None, "subject_id": None, "stance": None} | said
    return json.dumps(body, ensure_ascii=False)


def raw_for(agreed_gold_ids: set[int]) -> str:
    """One raw reply per pack item, in the pack's own order — the shape the pod persists."""
    lines = []
    for index, item in enumerate(PACK["items"]):
        msg_id = int(item["msg_id"])
        lines.append(
            json.dumps(
                {
                    "index": index,
                    "id": item["id"],
                    "thread": item["thread"],
                    "part": None,
                    "rendering_sha256": item["rendering_sha256"],
                    "reply": answer(item, msg_id in agreed_gold_ids),
                    "balanced": True,
                    "emitted_chars": 90,
                    "cut_chars": 0,
                    "finish_reason": "stop",
                    "usage": {"prompt_tokens": 800, "completion_tokens": 36},
                    "seconds": 5.1,
                    "elapsed_since_start": 5.1 + index,
                    "boot_seconds": 200.0,
                },
                ensure_ascii=False,
            )
        )
    return "\n".join(lines) + "\n"


@pytest.fixture
def scored(tmp_path, monkeypatch):
    """`build` pointed at fabricated raw files, an outdir of its own, and NO run record.

    The run record is redirected too. Once a real session ships `results/lora_b_run.json`, the
    missing-copy refusal would read THAT file and see an arm the real run evaluated — and every
    fabricated case with a missing arm would raise. A fixture that reads a shipped artifact is green
    only until the artifact lands ([[a-test-that-reads-a-shipped-artifact]]).
    """
    monkeypatch.setattr(verdict, "RUN", tmp_path / "lora_b_run.json")

    def run(arms: dict[str, set[int] | None]):
        raws = {}
        for arm, agreed in arms.items():
            if agreed is None:
                raws[arm] = tmp_path / f"missing_{arm}.jsonl"  # deliberately not written
                continue
            path = tmp_path / f"raw_{arm}.jsonl"
            path.write_text(raw_for(agreed), encoding="utf-8")
            raws[arm] = path
        monkeypatch.setattr(verdict, "RAW", raws)
        monkeypatch.setattr(
            verdict, "ADAPTER_RECORD", {arm: tmp_path / "none.json" for arm in raws}
        )
        return verdict.build(tmp_path)

    return run


def test_twelve_agreed_on_one_arm_is_a_green_gate_and_that_arm_ships(scored):
    twelve = set(GOLD_IDS[:12])
    out = scored({"a": twelve, "b": set(GOLD_IDS[:9])})
    gate = out["gate"]
    assert gate["agreed_by_arm"] == {"a": 12, "b": 9}
    assert gate["max_agreed"] == 12 and gate["minimum_agreed"] == 12
    assert gate["verdict"] == "GREEN" and gate["passed"] is True
    assert gate["ships"] == "a"
    assert "double the false-pass odds" in gate["multiplicity"]


def test_eleven_of_fourteen_is_RED_and_the_verdict_carries_the_return_to_the_sitting(scored):
    out = scored({"a": set(GOLD_IDS[:11]), "b": set(GOLD_IDS[:10])})
    gate = out["gate"]
    assert gate["max_agreed"] == 11 < 12
    assert gate["verdict"] == "RED" and gate["passed"] is False and gate["ships"] is None
    assert "line B is CLOSED" in gate["reading"]
    assert gate["next"] == RECORD["return_to_sitting"]


def test_a_tie_ships_arm_b_because_it_was_named_before_the_numbers_existed(scored):
    twelve = set(GOLD_IDS[:12])
    out = scored({"a": twelve, "b": twelve})
    gate = out["gate"]
    assert gate["agreed_by_arm"] == {"a": 12, "b": 12}
    assert gate["tie"] is True
    assert gate["ships"] == "b"
    assert "tie ships arm B" in gate["tie_rule"]


def test_an_arm_with_no_evidence_is_not_evaluated_and_is_never_scored_zero(scored):
    out = scored({"a": set(GOLD_IDS[:12]), "b": None})
    assert out["arms"]["b"]["evaluated"] is False
    assert "never scored 0 of 14" in out["arms"]["b"]["why"]
    assert "bar" not in out["arms"]["b"]
    gate = out["gate"]
    assert gate["agreed_by_arm"] == {"a": 12}
    assert gate["arms_not_evaluated"] == ["b"]
    assert gate["verdict"] == "GREEN"  # one arm can still take the bar
    assert "arm_b" not in out["ablation"]["agreed"]


def test_neither_arm_evaluated_is_NO_READING_and_the_attempt_is_not_spent(scored):
    out = scored({"a": None, "b": None})
    gate = out["gate"]
    assert gate["scored"] is False
    assert gate["verdict"] == "NO READING"
    assert "NOT spent" in gate["reading"]


def test_the_ablation_is_paired_per_row_against_the_sealed_base_which_is_never_re_run(scored):
    twelve = set(GOLD_IDS[:12])
    out = scored({"a": twelve, "b": set(GOLD_IDS[:9])})
    table = out["ablation"]
    assert table["agreed"]["base"] == RECORD["population"]["base"]["agreed"] == 9
    assert table["agreed"]["arm_a"] == 12 and table["agreed"]["arm_b"] == 9
    assert [row["msg_id"] for row in table["rows"]] == GOLD_IDS
    assert table["base_record"]["sha256"] == RECORD["population"]["base"]["sha256"]
    # every row's base column is the sealed record's, cell for cell
    for row in table["rows"]:
        assert row["base"] == BASE_ROWS[row["msg_id"]]
    # turned and lost are computed against that same column, both directions
    for arm in ("arm_a", "arm_b"):
        for msg_id in table["turned"][arm]:
            assert BASE_ROWS[msg_id] is False
        for msg_id in table["lost"][arm]:
            assert BASE_ROWS[msg_id] is True


def test_the_census_fifty_is_reported_beside_the_bar_and_gates_nothing(scored):
    out = scored({"a": set(GOLD_IDS[:12]), "b": None})
    census = out["census_50"]
    assert census["gating"] is False
    assert census["base_none"] == 25
    assert "OBSERVATION ONLY" in census["rule"]
    assert sum(out["arms"]["a"]["census_50"]["subject_type_distribution"].values()) == 50


def test_the_provenance_names_the_registration_the_datasets_and_the_frozen_gold(scored):
    out = scored({"a": set(GOLD_IDS[:12]), "b": set(GOLD_IDS[:12])})
    prov = out["provenance"]
    assert prov["registration"]["sha256"] == verdict.summary.sha256_of(verdict.PREREG)
    assert prov["training"]["seed"] == 42
    assert prov["training"]["supervision"]["boundary_char"] == ","
    for arm in ("a", "b"):
        assert prov["arms"][arm]["dataset"]["sha256"] == RECORD["arms"][arm]["dataset"]["sha256"]
        assert prov["arms"][arm]["sampler_weights"] == RECORD["arms"][arm]["sampler_weights"]
        assert "--adapter" in prov["arms"][arm]["eval_command"]
    assert prov["gold"]["sha256"] == RECORD["population"]["gold"]["sha256"]


def test_the_ablation_refuses_a_base_record_that_is_not_the_one_registered(
    scored, monkeypatch, tmp_path
):
    """The pairing's own precondition: a base column from an unregistered file is not paired."""
    fake = tmp_path / "base.json"
    fake.write_text(json.dumps(BASE, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(verdict, "BASE_VERDICT", fake)
    with pytest.raises(SystemExit, match="not the record the registration pinned"):
        scored({"a": set(GOLD_IDS[:12]), "b": None})


def test_the_scorer_REFUSES_when_the_run_record_says_an_arm_was_evaluated_and_the_copy_is_missing(
    scored, tmp_path, monkeypatch
):
    """«NO READING» must never be the report of a session that spent the attempt.

    The run record is the other witness: an arm whose format smoke went GO was evaluated, so its
    replies exist on the pod. If they are not on this machine the scp did not happen, and scoring
    would print «neither arm produced a reply, the attempt is NOT spent» over a bill
    ([[a_checker_whose_failure_is_silence]]).
    """
    run_record = tmp_path / "lora_b_run.json"
    run_record.write_text(
        json.dumps(
            {
                "gates": [
                    {"kind": "smoke-a", "arm": "a", "verdict": "GO"},
                    {"kind": "smoke-b", "arm": "b", "verdict": "KILL"},
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(verdict, "RUN", run_record)
    with pytest.raises(SystemExit, match="never copied back"):
        scored({"a": None, "b": None})

    # arm b's smoke KILLed, so its missing file is a STATE and the scorer proceeds on arm a alone
    out = scored({"a": set(GOLD_IDS[:12]), "b": None})
    assert out["cleared_for_eval_by_the_run_record"] == ["a"]
    assert out["gate"]["verdict"] == "GREEN"
    assert out["arms"]["b"]["evaluated"] is False


def test_the_runbook_copies_the_eval_replies_to_the_paths_this_scorer_reads():
    """The seam no unit test can see: the pod's file name, the runbook's scp, and the scorer's path.

    Three files name the same artifact and only two of them are code. A rename in any one of them
    leaves the verdict reading an absent file and reporting NO READING, so the chain is asserted
    end to end here rather than trusted ([[a_report_proves_it_does_not_instruct]]).
    """
    runbook = (REPO_ROOT / "scripts" / "runbook_lora_b.md").read_text("utf-8")
    template = "results/lora_b_eval_arm_$ARM.jsonl"
    assert template in runbook
    assert f"{template}.adapter.json" in runbook
    for arm in ("a", "b"):
        assert str(verdict.RAW[arm].relative_to(REPO_ROOT)) == template.replace("$ARM", arm)
        assert (
            str(verdict.ADAPTER_RECORD[arm].relative_to(REPO_ROOT))
            == f"{template.replace('$ARM', arm)}.adapter.json"
        )
        # and the source of that copy is the file the REGISTRATION's own eval command writes
        on_pod = f"/workspace/run/eval_arm_{arm}.jsonl"
        assert f"--out {on_pod}" in RECORD["arms"][arm]["eval_command"]
        assert "eval_arm_$ARM.jsonl" in runbook
    assert str(verdict.RUN.relative_to(REPO_ROOT)) == "results/lora_b_run.json"


def test_each_arm_ingests_into_its_OWN_evidence_file(scored, tmp_path):
    out = scored({"a": set(GOLD_IDS[:12]), "b": set(GOLD_IDS[:9])})
    files = {out["arms"][arm]["evidence"]["file"] for arm in ("a", "b")}
    assert len(files) == 2
    shas = {out["arms"][arm]["evidence"]["sha256"] for arm in ("a", "b")}
    assert len(shas) == 2  # different answers, different bytes — the two arms did not share a file
    assert all(out["arms"][arm]["evidence"]["rows"] == 64 for arm in ("a", "b"))
