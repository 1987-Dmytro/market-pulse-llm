"""`scripts/score_pass1_probe_b.py` — pass1-probe's scorer, pointed at the b-attempt's files.

Only the swap is new, so only the swap is tested: bar P1, the census, the refusal shapes and the
window re-price are `scripts/score_pass1_probe.py`'s and are driven on hand-made evidence in
`tests/test_score_pass1_probe.py`. What has to be true here is that the b-scorer reads the
b-REGISTRATION and writes the b-VERDICT — a scorer left pointing at pass1-probe's own files would
score fourteen ABSENT rows against an unscored attempt and call it a result.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import score_pass1_probe as scoring  # noqa: E402
import score_pass1_probe_b as driver  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_pass1_probe_b.json").read_text("utf-8"))
GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text("utf-8"))
GOLD_BY_ID = {int(row["msg_id"]): row for row in GOLD["per_comment"]}


def test_the_scorer_points_at_the_b_attempts_files_and_puts_pass_1s_back():
    was = {name: getattr(scoring, name) for name in driver.SWAPPED}
    with driver.as_probe_b():
        assert scoring.PHASE == "pass1-probe-b"
        assert scoring.PREREG.name == "prereg_pass1_probe_b.json"
        assert scoring.EVIDENCE.name == "pass1_probe_b_rows.jsonl"
        assert scoring.RUN.name == "pass1_probe_b_run.json"
        assert scoring.OUT.name == "pass1_probe_b_verdict.json"
    assert {name: getattr(scoring, name) for name in driver.SWAPPED} == was


def test_the_swap_refuses_to_replace_a_name_that_no_longer_exists():
    was = scoring.EVIDENCE
    try:
        del scoring.EVIDENCE
        with pytest.raises(SystemExit, match="has no `EVIDENCE` any more"):
            with driver.as_probe_b():
                pass
    finally:
        scoring.EVIDENCE = was


def test_the_verdict_it_writes_names_the_B_registration_and_carries_its_clause(
    tmp_path, monkeypatch
):
    """Driven end to end on a perfect synthetic reading, so the paths are exercised rather than
    asserted: the verdict has to name `prereg_pass1_probe_b.json` and no other record."""
    rows = []
    for one in RECORD["population"]["gold"]["rows"]:
        gold = GOLD_BY_ID[one["msg_id"]]
        rows.append(
            {
                "id": f"{one['thread']}#{one['msg_id']}",
                "thread": one["thread"],
                "msg_id": one["msg_id"],
                "leg": "gold",
                "reply": "…",
                "parsed": {
                    "msg_id": one["msg_id"],
                    "subject_type": gold.get("subject_type"),
                    "subject_id": gold.get("subject_id"),
                    "stance": gold.get("stance"),
                },
                "parse_error": None,
                "balanced": True,
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 900, "completion_tokens": 40},
                "seconds": 3.0,
            }
        )
    evidence = tmp_path / "rows.jsonl"
    evidence.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    monkeypatch.setattr(driver, "EVIDENCE", evidence)
    monkeypatch.setattr(driver, "RUN", tmp_path / "missing_run.json")
    out = tmp_path / "verdict.json"
    monkeypatch.setattr(driver, "OUT", out)
    assert driver.main() == 0
    verdict = json.loads(out.read_text(encoding="utf-8"))
    assert verdict["phase"] == "pass1-probe-b"
    assert verdict["registration"]["record"] == "results/prereg_pass1_probe_b.json"
    assert verdict["pack"]["record"] == "results/pass1_probe_b_pack.json"
    assert verdict["bars"]["P1_per_comment_agreement"]["agreed"] == 14
    assert verdict["outcome"] == "GO"
    assert verdict["return_to_sitting"] == RECORD["return_to_sitting"]
    assert "run" not in verdict, "no run record existed, so the verdict must not claim one"
