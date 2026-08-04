"""The 4.5h2 rule, committed before any arm was scored.

The tests that matter are about the rule itself — its text, its pivot, and its refusal to
decide anything before both arms exist. The arithmetic is `scorer.select_arm_by`'s and is
hand-computed in `tests/test_scorer.py`.
"""

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "gate_verdict_45h.py"
spec = importlib.util.spec_from_file_location("gate_verdict_45h", SCRIPT)
verdict = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verdict)

CONTRACT = (REPO_ROOT / "docs" / "PROMPT-4.5h2.md").read_text(encoding="utf-8")


def test_the_rule_is_the_contracts_own_words():
    """A rule that can be reworded after the numbers are in is not pre-registered. The
    contract wraps its lines, so both are compared with whitespace collapsed."""
    clauses = (
        "the пласт stays iff arm B's G1c is strictly higher than arm A's",
        "no other gated head of B is lower than A's by more than 0.5 pp",
    )
    contract = " ".join(CONTRACT.split())
    rule = " ".join(verdict.SELECTION_RULE.split())
    for clause in clauses:
        assert clause in contract, clause
        assert clause in rule, clause


def test_the_rule_turns_on_g1c_and_the_tolerance_is_the_spec_s():
    from market_pulse import scorer

    assert verdict.PIVOT == "G1c"
    assert scorer.SYNTHETIC_HEAD_TOLERANCE == 0.005
    assert verdict.ARMS == ("without-plast", "with-plast")


def test_the_verdict_reads_the_v4_anchor_and_not_phase_4_s():
    """Scoring a v4 arm against the v2 anchor would compare a six-class head to a
    five-class baseline and call the difference a fine-tune."""
    assert verdict.VERSION == "v4"


def test_it_refuses_before_both_arms_exist(tmp_path):
    """Read-only and loud: no arm, no verdict. Today `results/baselines.json` holds
    neither of this phase's arms, so the refusal is the live behaviour, not a fixture."""
    with pytest.raises(SystemExit, match="refused:"):
        verdict.main([])


def test_it_refuses_a_results_file_with_no_v4_anchor(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text(json.dumps({}), encoding="utf-8")
    with pytest.raises(SystemExit, match="test set v4 must be exactly one record, found 0"):
        verdict.main(["--results", str(path)])


def test_the_arm_names_are_this_phase_s_and_not_phase_4_s():
    """`records.arm_record` refuses two rows for one arm name, and both phases append to
    the same file — so each of this phase's arms must appear at most once, and never
    under a name Phase 4 already used."""
    from market_pulse import records

    history = json.loads((REPO_ROOT / "results" / "baselines.json").read_text(encoding="utf-8"))
    assert not set(verdict.ARMS) & {"real-only", "with-synthetic"}
    for arm in verdict.ARMS:
        rows = [
            record
            for runs in history.values()
            for record in runs
            if record.get("config", {}).get("fine_tune", {}).get("arm") == arm
        ]
        assert len(rows) <= 1, f"{arm} is recorded {len(rows)} times"
        if rows:
            assert records.arm_record(history, arm) is rows[0]
