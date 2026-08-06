"""The 5b verdict script: the abort rule, and the selection rule applied to the pair.

The bars, the anchor and the 4.5h2 verdict are the repository's real files — re-deriving
the v4 bars and finding them equal to what `results/verdict_45h2.json` recorded is a
positive control this suite gets for free, and the one thing no synthetic fixture could
give. Only the two parity records are built here, because they are what a paid run would
produce and this suite must be green before one exists.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
spec = importlib.util.spec_from_file_location(
    "parity_verdict_5b", REPO_ROOT / "scripts" / "parity_verdict_5b.py"
)
verdict = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verdict)

# The 4.5h2 arm-A numbers, so a parity record built from these reproduces its gate verdicts.
ARM_A = {
    "G1a": {"overall": 0.9214075146604309, "ua": 0.9306036598902109, "ru": 0.8697089947089948},
    "G1b": {"value": 0.6052631578947368, "fixed": 23, "slice": 38, "guard_delta": 0.0243988},
    "G1c": 0.8478260869565217,
    "G1d": 0.9585858585858587,
    "G1e": 0.961038961038961,
}


def gates(values: dict) -> list[dict]:
    """An eval record's gates block, in `records.arm_values`' shape."""
    return [
        {"gate": "G1a", "metric": "sentiment macro-F1 (comments_test)", "values": values["G1a"]},
        {
            "gate": "G1b",
            "metric": "sarcasm slice fix-rate (sarcasm_holdout)",
            "value": values["G1b"]["value"],
            "fixed": values["G1b"]["fixed"],
            "n": {"slice": values["G1b"]["slice"]},
            "guard": {"delta": values["G1b"]["guard_delta"]},
        },
        {"gate": "G1c", "metric": "intents micro-F1 (comments_test)", "value": values["G1c"]},
        {"gate": "G1d", "metric": "post_type macro-F1 (posts_test)", "value": values["G1d"]},
        {"gate": "G1d", "metric": "relevance macro-F1 (posts_test)", "value": 1.0},
        {"gate": "G1e", "metric": "brand extraction F1 (posts_test)", "value": values["G1e"]},
    ]


def parity_record(config: str, values: dict) -> dict:
    return {
        "model": "google/gemma-4-31b-it",
        "timestamp": "2026-08-06T18:00:00+00:00",
        "config": {
            "backend": "endpoint",
            "testset_version": "v4",
            "serving": {
                "endpoint_id": "ep-1",
                "config": config,
                "merge_state": "unmerged-adapter" if config == "A" else "merged-requantized",
                "timing": {"worker_seconds": 2100.0},
            },
        },
        "gates": gates(values),
    }


@pytest.fixture
def paths(tmp_path, monkeypatch):
    """Redirect only what a paid run writes; the anchors stay the repository's own."""
    written = {
        "A": tmp_path / "parity_5b_a.json",
        "B": tmp_path / "parity_5b_b.json",
    }
    monkeypatch.setattr(verdict, "PARITY", written)
    monkeypatch.setattr(verdict, "PROJECTION", tmp_path / "parity_5b_projection.json")
    monkeypatch.setattr(verdict, "VERDICT", tmp_path / "parity_verdict_5b.json")
    return written


def write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


# --- the anchors: the positive control --------------------------------------


def test_the_v4_bars_rederive_to_what_45h2_recorded():
    """Never typed, and asserted equal: a bar that moved would rewrite the gate."""
    bars, recorded = verdict.bars_from_anchor()
    assert bars == recorded["bars"]
    assert bars["G1b"]["n"] == 38


def test_the_required_gates_are_read_off_the_record():
    _, recorded = verdict.bars_from_anchor()
    assert verdict.passed_at_45h2(recorded) == ["G1b", "G1d", "G1e"]
    assert recorded["decision"]["selected"] == "without-plast"


def test_the_anchor_column_is_the_shipped_arms_numbers():
    _, recorded = verdict.bars_from_anchor()
    anchor = verdict.anchor_values(recorded)
    assert anchor["G1c"] == pytest.approx(0.8478260869565217)
    assert anchor["G1b"] == pytest.approx(0.6052631578947368)


# --- the abort rule ---------------------------------------------------------


def args(**kwargs):
    defaults = {
        "seconds_per_row": 3.0,
        "usd_per_second": 0.0005,
        "cold_start_seconds": 200.0,
        "merge_usd": 1.0,
        "rows": 758,
    }
    return type("Args", (), defaults | kwargs)


def test_a_projection_over_the_cap_writes_the_verdict_as_well(paths, capsys):
    #   per run = 758 x 6.0 + 200 = 4748 s; x2 x $0.0005 = $4.748; + $1.00 = $5.748
    assert verdict.run_projection(args(seconds_per_row=6.0)) == 0
    record = json.loads(verdict.VERDICT.read_text(encoding="utf-8"))
    assert record["outcome"] == "aborted-over-cap"
    assert record["shipped"] == "A"
    assert record["projection"]["projected_usd"] == pytest.approx(5.748)
    assert "closes the merge question in favour of A" in record["why"]
    assert "OVER THE CAP" in capsys.readouterr().out


def test_a_projection_that_clears_writes_no_verdict_but_still_leaves_an_artifact(paths):
    """A measured "it clears" and a projection nobody ran must not look the same."""
    assert verdict.run_projection(args(seconds_per_row=1.0)) == 0
    assert not verdict.VERDICT.exists()
    projection = json.loads(verdict.PROJECTION.read_text(encoding="utf-8"))
    assert projection["over_cap"] is False
    assert projection["projection"]["projected_usd"] == pytest.approx(1.958)
    assert projection["cap_usd"] == 4.00


def test_the_projection_needs_the_smoke_to_have_measured_something(paths):
    with pytest.raises(SystemExit):
        verdict.main(["--project", "--seconds-per-row", "3.0"])


# --- the pair ---------------------------------------------------------------


def test_an_identical_pair_adopts_b(paths, capsys):
    write(paths["A"], parity_record("A", ARM_A))
    write(paths["B"], parity_record("B", ARM_A))
    assert verdict.main([]) == 0
    out = capsys.readouterr().out
    assert "SHIPPED CONFIG                      B" in out
    assert "gates passed ['G1b', 'G1d', 'G1e']" in out


def test_a_pair_where_b_loses_a_required_gate_ships_a(paths, tmp_path):
    #   G1d bar is 0.9090105074; 0.85 fails it, and G1d passed at 4.5h2.
    write(paths["A"], parity_record("A", ARM_A))
    write(paths["B"], parity_record("B", ARM_A | {"G1d": 0.85}))
    record = tmp_path / "verdict.json"
    assert verdict.main(["--record", str(record)]) == 0
    payload = json.loads(record.read_text(encoding="utf-8"))
    assert payload["shipped"] == "A"
    assert payload["decision"]["gates_lost"] == ["G1d"]
    assert payload["configs"]["B"]["verdicts"]["G1d"]["pass"] is False
    assert payload["configs"]["A"]["passed"] == 3


def test_the_record_names_the_outcome_per_condition_not_just_a_winner(paths, tmp_path):
    write(paths["A"], parity_record("A", ARM_A))
    write(paths["B"], parity_record("B", ARM_A))
    record = tmp_path / "verdict.json"
    verdict.main(["--record", str(record)])
    payload = json.loads(record.read_text(encoding="utf-8"))
    assert payload["decision"]["must_stay_passing"] == {"G1b": True, "G1d": True, "G1e": True}
    assert set(payload["decision"]["head_deltas"]) == {"G1a", "G1b", "G1c", "G1d", "G1e"}
    assert payload["required_gates"] == ["G1b", "G1d", "G1e"]
    assert payload["anchor_values_45h2"]["G1c"] == pytest.approx(ARM_A["G1c"])
    assert payload["outcome"] == "pair-scored"


def test_a_missing_config_is_a_refusal_not_a_one_sided_verdict(paths):
    write(paths["A"], parity_record("A", ARM_A))
    with pytest.raises(SystemExit, match="config B was not scored"):
        verdict.main([])


def test_a_record_that_served_the_other_config_is_refused(paths):
    write(paths["A"], parity_record("A", ARM_A))
    write(paths["B"], parity_record("A", ARM_A))  # copy-paste of the A run
    with pytest.raises(SystemExit, match="says it served config 'A', not 'B'"):
        verdict.main([])


def test_a_pod_record_is_not_a_serving_record(paths):
    write(paths["A"], parity_record("A", ARM_A))
    pod = parity_record("B", ARM_A)
    del pod["config"]["serving"]
    write(paths["B"], pod)
    with pytest.raises(SystemExit, match="carries no serving block"):
        verdict.main([])
