"""The selection rule and the five verdicts, driven as the script.

`docs/PROMPT-4c.md` asks for the rule's application to be a script output rather
than prose, so the script is what these tests run. The anchor and the slice come
from the committed results file — the bars must be the real ones — and the two
arms are fixtures, because their numbers do not exist until 4c has run.
"""

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "gate_verdict.py"
spec = importlib.util.spec_from_file_location("gate_verdict", SCRIPT)
verdict = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verdict)

HISTORY = json.loads((REPO_ROOT / "results" / "baselines.json").read_text(encoding="utf-8"))


def arm_record(arm: str, *, g1a, g1b, guard, g1c, g1d, g1e, relevance=0.94) -> dict:
    """One ablation arm's record, in the shape the arm eval writes."""
    return {
        "model": "google/gemma-4-31b-it",
        "timestamp": f"2026-08-02T00:00:00+00:00 {arm}",
        "config": {
            "backend": "local",
            "train_sources": {"comments_train.jsonl": 895},
            "fine_tune": {
                "arm": arm,
                "train_sha256": "d" * 64,
                "adapter_sha256": "a" * 64,
                "n_train": 2171,
            },
        },
        "diagnostics": {"gate_anchor_valid": True},
        "gates": [
            {"gate": "G1a", "metric": "sentiment macro-F1 (comments_test)", "values": g1a},
            {
                "gate": "G1b",
                "metric": "sarcasm slice fix-rate (sarcasm_holdout)",
                "value": g1b / 44,
                "fixed": g1b,
                "n": {"slice": 44},
                "guard": {"delta": guard},
            },
            {"gate": "G1c", "metric": "intents micro-F1 (comments_test)", "value": g1c},
            {"gate": "G1d", "metric": "post_type macro-F1 (posts_test)", "value": g1d},
            {"gate": "G1d", "metric": "relevance macro-F1 (posts_test)", "value": relevance},
            {"gate": "G1e", "metric": "brand extraction F1 (posts_test)", "value": g1e},
        ],
    }


PASSING = {
    "g1a": {"overall": 0.95, "ua": 0.94, "ru": 0.93},
    "g1b": 30,
    "guard": 0.006,
    "g1c": 0.86,
    "g1d": 0.92,
    "g1e": 0.91,
}


def results_file(tmp_path: Path, real: dict, synthetic: dict) -> Path:
    """The committed history plus two arms — the anchor and its slice stay real."""
    history = json.loads(json.dumps(HISTORY))
    history["4c-arms"] = [
        arm_record("real-only", **real),
        arm_record("with-synthetic", **synthetic),
    ]
    path = tmp_path / "baselines.json"
    path.write_text(json.dumps(history), encoding="utf-8")
    return path


def run(tmp_path, real, synthetic, capsys):
    assert verdict.main(["--results", str(results_file(tmp_path, real, synthetic))]) == 0
    return capsys.readouterr().out


def test_the_script_prints_both_columns_the_rule_and_five_verdicts(tmp_path, capsys):
    printed = run(tmp_path, PASSING, {**PASSING, "g1b": 33}, capsys)
    assert "real-only" in printed and "with-synthetic" in printed
    assert "G1b slice fix-rate" in printed
    assert "relevance (reported, not gated)" in printed
    assert printed.count("==>") == 5, "five gates, five verdicts"
    assert "5 of 5 Tier-1 gates pass" in printed


def test_synthetic_stays_when_it_wins_g1b_and_costs_no_other_head(tmp_path, capsys):
    printed = run(tmp_path, PASSING, {**PASSING, "g1b": 33}, capsys)
    assert "SELECTED ARM          with-synthetic  (synthetic stays)" in printed
    assert "lower by > 0.5 pp     none" in printed


def test_synthetic_is_dropped_when_another_head_pays_for_the_fix_rate(tmp_path, capsys):
    """The negative control the rule exists for: a higher fix-rate bought with
    0.6 pp of G1c is not a better arm, it is a trade the operator pre-refused."""
    printed = run(tmp_path, PASSING, {**PASSING, "g1b": 40, "g1c": 0.854}, capsys)
    assert "SELECTED ARM          real-only  (synthetic is dropped)" in printed
    assert "G1c -0.0060" in printed


def test_an_equal_fix_rate_is_not_a_strictly_higher_one(tmp_path, capsys):
    printed = run(tmp_path, PASSING, PASSING, capsys)
    assert "SELECTED ARM          real-only" in printed
    assert "NO" in printed


def test_the_bars_are_the_real_anchors_and_a_failed_gate_says_so(tmp_path, capsys):
    """G1a's bar is the anchor + 5 pp read out of the committed record. A model
    at 0.90 is under it, and the script must say FAIL rather than round it away."""
    failing = {**PASSING, "g1a": {"overall": 0.90, "ua": 0.94, "ru": 0.93}}
    printed = run(tmp_path, failing, failing, capsys)
    assert "0.9418" in printed, "the bar is derived from the anchor, not typed"
    assert "4 of 5 Tier-1 gates pass" in printed


def test_an_arm_scored_twice_is_refused_rather_than_picked(tmp_path):
    """4c scores each arm once. Two rows would make the verdict depend on which
    one a lookup reached first."""
    history = json.loads(json.dumps(HISTORY))
    history["4c-arms"] = [arm_record("real-only", **PASSING)] * 2 + [
        arm_record("with-synthetic", **PASSING)
    ]
    path = tmp_path / "baselines.json"
    path.write_text(json.dumps(history), encoding="utf-8")
    with pytest.raises(SystemExit, match="must be exactly one record, found 2"):
        verdict.main(["--results", str(path)])


def test_an_unscored_arm_is_refused_rather_than_read_as_zero(tmp_path):
    history = json.loads(json.dumps(HISTORY))
    history["4c-arms"] = [arm_record("real-only", **PASSING)]
    path = tmp_path / "baselines.json"
    path.write_text(json.dumps(history), encoding="utf-8")
    with pytest.raises(SystemExit, match="'with-synthetic' arm must be exactly one record"):
        verdict.main(["--results", str(path)])
