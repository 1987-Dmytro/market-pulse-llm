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
    # The out-paths are read at call time, so the `paths` fixture's redirects are what
    # these pick up — a default captured at import would write into the repository.
    defaults = {
        "seconds_per_row": 3.0,
        "usd_per_second": 0.0005,
        "cold_start_seconds": 200.0,
        "merge_usd": 1.0,
        "spent_usd": 0.0,
        "rows": 758,
        "runs": 2,
        "projection_out": verdict.PROJECTION,
        "verdict_out": verdict.VERDICT,
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


def test_what_5b_already_spent_can_tip_a_clearing_projection_over(paths):
    """$1.958 of pair clears $4 on its own; on top of $2.20 already spent it does not."""
    assert verdict.run_projection(args(seconds_per_row=1.0, spent_usd=2.20)) == 0
    record = json.loads(verdict.VERDICT.read_text(encoding="utf-8"))
    assert record["outcome"] == "aborted-over-cap"
    assert record["projection"]["total_usd"] == pytest.approx(4.158)
    assert "which is on the phase, not on the pair" in record["why"]


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


# --- the projection's inputs, read off the smoke rather than typed -----------
#
#   test v4 is 508 rows of T1v2_with_post + 250 of T2. The with-post rendering carries
#   the parent and is the slower one, so a smoke drawn evenly across the two tasks
#   under-predicts a run that is two-thirds the slow kind:
#     flat mean of 4.0 and 2.0                       = 3.00 s/row
#     weighted 508/758 x 4.0 + 250/758 x 2.0         = 3.34 s/row
def test_the_task_mix_is_counted_off_the_frozen_files():
    assert verdict.task_mix() == {"T1v2_with_post": 508, "T2": 250}


def test_seconds_per_row_is_weighted_to_the_paid_runs_mix():
    rows = [
        {"task": "T1v2_with_post", "wall_seconds": 4.0},
        {"task": "T2", "wall_seconds": 2.0},
    ]
    assert verdict.weighted_seconds_per_row(rows, verdict.task_mix()) == pytest.approx(
        3.34, abs=5e-3
    )


def test_a_smoke_that_never_timed_a_rendering_cannot_weight_it():
    """The T2-only smoke would project the whole run at T2 speed and clear too easily."""
    with pytest.raises(SystemExit, match="a projection that weights a rendering it never timed"):
        verdict.weighted_seconds_per_row([{"task": "T2", "wall_seconds": 2.0}], verdict.task_mix())


def smoke_record(**cost) -> dict:
    return {
        "rows": [
            {"task": "T1v2_with_post", "wall_seconds": 4.0},
            {"task": "T2", "wall_seconds": 2.0},
        ],
        "cold_start": {"wall_seconds": 300.0},
        "timing": {"wall_seconds": 330.0},
        "cost": {
            "usd": 0.20,
            "usd_per_second": 0.0006,
            "floor_usd_per_second": 0.53 / 3600,
            "above_pod_floor": True,
        }
        | cost,
    }


def test_the_projection_reads_its_inputs_from_the_smoke_artifact(tmp_path):
    path = tmp_path / "serving_5b.json"
    path.write_text(json.dumps(smoke_record()), encoding="utf-8")
    derived = verdict.from_smoke(path)
    assert derived["seconds_per_row"] == pytest.approx(3.34, abs=5e-3)
    assert derived["usd_per_second"] == 0.0006
    assert derived["cold_start_seconds"] == 300.0


def test_a_rate_below_the_pod_floor_is_a_stale_balance_not_a_cheap_run(tmp_path):
    """Serverless never bills under the pod class it runs on; a near-zero rate would
    make the projection clear trivially and authorise a pair the phase cannot afford."""
    path = tmp_path / "serving_5b.json"
    path.write_text(
        json.dumps(smoke_record(usd_per_second=0.000001, above_pod_floor=False)), encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="below the A6000 pod floor"):
        verdict.from_smoke(path)


def test_a_smoke_with_no_dollars_cannot_be_projected_from(tmp_path):
    path = tmp_path / "serving_5b.json"
    record = smoke_record()
    del record["cost"]
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(SystemExit, match="carries no cost block"):
        verdict.from_smoke(path)


# --- the third outcome: the runtime could not be reached --------------------


def abort_args(**kwargs):
    defaults = {
        "blocker": "no serverless worker reaches a job-consuming state",
        "evidence": ["RunPod's own hub vLLM worker cycled initializing/throttled"],
        "spent_usd": 0.5324,
        "verdict_out": verdict.VERDICT,
    }
    return type("Args", (), defaults | kwargs)


def test_a_runtime_that_could_not_be_reached_still_ships_a(paths, capsys):
    """SPEC: a failed or aborted pair closes the merge question in favour of A."""
    assert verdict.run_abort(abort_args()) == 0
    record = json.loads(verdict.VERDICT.read_text(encoding="utf-8"))
    assert record["outcome"] == "aborted-runtime-unreachable"
    assert record["shipped"] == "A"
    assert "merging stays forbidden" in record["why"]
    assert record["evidence"]
    assert "hub vLLM worker" in capsys.readouterr().out


def test_a_cost_abort_and_a_runtime_abort_are_not_confusable(paths):
    """Same shipped config, different cause. A reader six weeks out must be able to
    tell "we priced it and stopped" from "we could not reach the runtime at all"."""
    verdict.run_abort(abort_args())
    runtime_abort = json.loads(verdict.VERDICT.read_text(encoding="utf-8"))
    verdict.run_projection(args(seconds_per_row=6.0))
    cost_abort = json.loads(verdict.VERDICT.read_text(encoding="utf-8"))
    assert runtime_abort["outcome"] != cost_abort["outcome"]
    assert runtime_abort["shipped"] == cost_abort["shipped"] == "A"
    assert "projection" in cost_abort and "projection" not in runtime_abort


def test_an_abort_with_no_evidence_is_refused(paths):
    with pytest.raises(SystemExit):
        verdict.main(["--abort", "--blocker", "something went wrong"])


# --- the single-config measurement (SPEC amendment 3.11 (2), 2026-08-06) -----


def single_args(paths, **kwargs):
    defaults = {"parity_record": paths["A"], "verdict_out": verdict.VERDICT}
    return type("Args", (), defaults | kwargs)


def pod_record(values: dict) -> dict:
    record = parity_record("A", values)
    record["config"]["serving"] |= {"transport": "pod-loopback", "endpoint_id": "pod-77"}
    return record


def test_the_single_config_measurement_reports_deltas_beside_the_anchor(paths, capsys):
    """A on the pod against the 4.5h2 pod numbers. Reported, not ruled on.

    Fed the arm's own 4.5h2 values, so every delta is zero by construction — which is
    what makes a non-zero one in the real run mean something rather than being lost in
    a column of noise.
    """
    write(paths["A"], pod_record(ARM_A))
    assert verdict.run_single(single_args(paths)) == 0
    stamped = json.loads(paths["A"].read_text(encoding="utf-8"))["parity"]
    assert stamped["outcome"] == "single-config-scored"
    assert stamped["runtime"] == "pod-loopback"
    assert stamped["deltas_vs_45h2"] == {head: 0.0 for head in verdict.HEADS}
    assert stamped["under_bar"] == []
    assert stamped["passed"] == 3
    assert stamped["required_gates"] == ["G1b", "G1d", "G1e"]
    assert "no bar moves" in stamped["not_a_gate"]
    # the pair's verdict is a committed decision, and this measurement does not re-open it
    assert not verdict.VERDICT.exists()
    assert "delta" in capsys.readouterr().out


def test_a_head_that_lands_under_its_bar_is_a_loud_finding_and_not_a_verdict(paths, capsys):
    """SPEC amendment 3.11 (2): no bar moves, and the ruling is an operator briefing."""
    write(paths["A"], pod_record(ARM_A | {"G1d": 0.80}))
    assert verdict.run_single(single_args(paths)) == 0
    stamped = json.loads(paths["A"].read_text(encoding="utf-8"))["parity"]
    assert stamped["under_bar"] == ["G1d"]
    assert stamped["deltas_vs_45h2"]["G1d"] < 0
    assert stamped["bars"] == verdict.bars_from_anchor()[0]  # unmoved
    assert "LOUD FINDING" in capsys.readouterr().out
    assert not verdict.VERDICT.exists()


def test_the_single_config_projection_is_one_run_not_two(paths, capsys):
    """The pair is closed, so a projection that still prices two runs would abort a run
    the phase can afford — the $4 stop is on the phase and `spent_usd` carries the rest."""
    assert verdict.run_projection(args(runs=1, merge_usd=0.0, spent_usd=0.5324)) == 0
    one = json.loads(verdict.PROJECTION.read_text(encoding="utf-8"))
    assert one["runs"] == 1
    assert one["over_cap"] is False
    assert one["projection"]["scored_usd"] == pytest.approx(1.2370, abs=1e-4)
    assert one["projection"]["total_usd"] == pytest.approx(1.7694, abs=1e-4)
    assert not verdict.VERDICT.exists()


def test_an_over_cap_single_run_writes_its_abort_where_it_is_told(paths, capsys):
    """The 5b verdict file is not a scratch pad: a later phase's abort gets its own path."""
    elsewhere = verdict.VERDICT.parent / "parity_5b1_verdict.json"
    assert verdict.run_projection(args(runs=1, seconds_per_row=12.0, verdict_out=elsewhere)) == 0
    assert json.loads(elsewhere.read_text(encoding="utf-8"))["outcome"] == "aborted-over-cap"
    assert not verdict.VERDICT.exists()
