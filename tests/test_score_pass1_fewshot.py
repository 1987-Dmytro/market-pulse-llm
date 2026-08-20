"""D2's scorer — its two STATES and its one refusal, driven before the pod exists.

The verdict has to be right in three worlds and only one of them involves a green shot. A session
that closed at the dev gate produces `not_evaluated` with a reason and never a 0 of 14, because a
zero would read a year later as «v2 answered and was wrong». A session whose replies were never
copied back is REFUSED rather than published as «no reading». And the paired fourteen is three
readings of the same instances, two of them files that already exist and are not re-run.

Everything here runs on synthetic replies in `tmp_path`: the real `results/` is never written and
no cloud call is made.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass1_fewshot_packs as packs  # noqa: E402
import gate_pass1_fewshot as gate  # noqa: E402
import score_pass1_fewshot as scorer  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_pass1_fewshot.json").read_text("utf-8"))
DEV = json.loads((REPO_ROOT / packs.DEV_NAME).read_text("utf-8"))
SHOT = json.loads((REPO_ROOT / packs.SHOT_NAME).read_text("utf-8"))


def replies(items: list[dict], answers: dict) -> str:
    return "".join(
        json.dumps(
            {
                "id": item["id"],
                "thread": item["thread"],
                "rendering_sha256": item["rendering_sha256"],
                "reply": json.dumps(
                    {
                        "msg_id": int(item["msg_id"]),
                        "subject_type": answers.get(item["id"], "не_наш_рынок"),
                        "subject_id": None,
                        "stance": None,
                    },
                    ensure_ascii=False,
                ),
                "balanced": True,
                "emitted_chars": 90,
                "cut_chars": 0,
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 900, "completion_tokens": 40},
                "seconds": 6.0,
                "elapsed_since_start": 100.0,
                "boot_seconds": 240.0,
            },
            ensure_ascii=False,
        )
        + "\n"
        for item in items
    )


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """The scorer pointed at throwaway results — nothing under the repo's own results/ is read."""
    where = tmp_path / "results"
    where.mkdir()
    monkeypatch.setattr(scorer, "RUN", where / "pass1_fewshot_run.json")
    monkeypatch.setattr(scorer, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gate, "REPO_ROOT", tmp_path)
    return where


def test_a_session_that_closed_at_the_dev_gate_is_NOT_EVALUATED_and_never_a_zero(sandbox):
    gold = {
        item["id"]: label
        for item, label in zip(
            next(one for one in DEV["legs"] if one["name"] == "base")["items"],
            [None] * len(next(one for one in DEV["legs"] if one["name"] == "base")["items"]),
        )
    }
    for leg in DEV["legs"]:
        (sandbox / leg["out"]).write_text(replies(leg["items"], gold), encoding="utf-8")
    record = scorer.build(sandbox.parent)
    assert record["shot"]["evaluated"] is False
    assert "NOT spent" in record["shot"]["why"]
    assert record["verdict"].startswith("CLOSED AT THE DEV GATE")
    assert record["dev_gate"]["scored"] is True
    # the paired table still carries the two sealed columns and an empty third
    paired = record["paired_fourteen"]
    assert set(paired["agreed"]) == {"base", "arm_a"}
    assert all(row.get("v2") is None for row in paired["rows"])
    assert len(paired["rows"]) == 14


def test_a_run_that_says_the_gate_went_GO_with_no_replies_on_disk_is_REFUSED(sandbox):
    scorer.RUN.write_text(
        json.dumps({"gates": [{"kind": "dev-gate", "verdict": "GO"}]}), encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="attempt is SPENT"):
        scorer.build(sandbox.parent)
    # and the same record with the shot's replies present does NOT refuse
    (sandbox / SHOT["legs"][0]["out"]).write_text(
        replies(SHOT["legs"][0]["items"], {}), encoding="utf-8"
    )
    assert scorer.refuse_a_missing_copy() is True


def test_the_gold_bar_is_probe_bs_own_and_a_perfect_shot_is_GREEN(sandbox):
    leg = SHOT["legs"][0]
    gold = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text("utf-8"))
    truth = {int(row["msg_id"]): row.get("subject_type") for row in gold["per_comment"]}
    answers = {
        item["id"]: (
            "категория_личное"
            if truth[int(item["msg_id"])] == "категория"
            else truth[int(item["msg_id"])]
        )
        for item in leg["items"]
        if int(item["msg_id"]) in truth
    }
    (sandbox / leg["out"]).write_text(replies(leg["items"], answers), encoding="utf-8")
    record = scorer.build(sandbox.parent)
    bar = record["shot"]["bar"]
    assert bar["n"] == 14
    assert bar["comparison"] == "market_pulse.scorer.reader_comment_agreement"
    assert bar["collapse"]["map"] == {"категория_личное": "категория"}
    # every gold row answered with its own gold subject_type: the three stance rows still miss,
    # because this contract does not train stance and the gold scores it on them
    assert bar["agreed"] >= 11
    assert record["verdict"] in ("GREEN", "RED")
    assert record["paired_fourteen"]["agreed"]["base"] == 9
    assert record["paired_fourteen"]["agreed"]["arm_a"] == 9


def test_the_paired_columns_are_READ_from_the_sealed_verdicts_and_never_re_run(sandbox):
    for leg in DEV["legs"]:
        (sandbox / leg["out"]).write_text(replies(leg["items"], {}), encoding="utf-8")
    record = scorer.build(sandbox.parent)
    sources = record["paired_fourteen"]["sources"]
    assert sources["base"]["record"] == "results/pass1_probe_b_verdict.json"
    assert sources["arm_a"]["record"] == "results/lora_b_verdict.json"
    for block in sources.values():
        assert len(block["sha256"]) == 64
    assert "never re-run" in record["paired_fourteen"]["rule"]


def test_the_provenance_names_the_neighbours_per_item_and_the_seeds(sandbox):
    for leg in DEV["legs"]:
        (sandbox / leg["out"]).write_text(replies(leg["items"], {}), encoding="utf-8")
    provenance = scorer.build(sandbox.parent)["provenance"]
    assert provenance["seeds"]["dev_draw"] == packs.SEED
    per_item = provenance["neighbours"]["per_item"]
    assert len(per_item["dev_v2"]) == 200 and len(per_item["shot"]) == 64
    assert all(len(one) == 5 for one in per_item["shot"].values())
    assert set(provenance["instruments"]["prompt_sha256"]) == {
        "pass1_comment_gm4_v1",
        "pass1_comment_gm4_v2",
    }
