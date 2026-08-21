"""The r2 registration — and the audit the contract asks for: pin by pin AND threshold by threshold.

r1's record was a copy of r2's with its numbers re-derived, and the class it was written against is
Dv613: a threshold copied for its ALGORITHM brings its number with it, and a repealed figure goes on
gating a run nobody priced it for. This record copies more than r1's did — the items are r1's items
and the gate EXECUTES r1's bytes — so the audit here is stricter: every numeric leaf that appears at
the same path in both money blocks is either MOVED, or it is CARRIED and named below with why.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import write_pass1_window_prereg_r2 as producer  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_pass1_window_r2.json").read_text("utf-8"))
R1 = json.loads((REPO_ROOT / "results" / "prereg_pass1_window.json").read_text("utf-8"))
PACK = json.loads((REPO_ROOT / "results" / "pass1_window_r2_pack.json").read_text("utf-8"))


def numeric_paths(node, prefix="", out=None):
    out = {} if out is None else out
    if isinstance(node, dict):
        for key, value in node.items():
            numeric_paths(value, f"{prefix}.{key}" if prefix else key, out)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            numeric_paths(value, f"{prefix}[{index}]", out)
    elif isinstance(node, (int, float)) and not isinstance(node, bool):
        out[prefix] = float(node)
    return out


def test_the_record_is_what_the_producer_writes_today(tmp_path):
    assert producer.main(["--out", str(tmp_path / "again.json")]) == 0
    assert (tmp_path / "again.json").read_text("utf-8") == (
        REPO_ROOT / "results" / "prereg_pass1_window_r2.json"
    ).read_text("utf-8")


def test_H6_re_derives_every_number_the_contract_prints():
    h6 = RECORD["h6"]
    assert h6["mismatches"] == []
    assert len(h6["rows"]) >= 40
    for row in h6["rows"]:
        assert row["agrees"] is True, row["name"]
        assert row["mode"] in ("equals", "at_least", "below"), row["name"]
        assert row["formula"], row["name"]
    # the rows the contract's own read-back names
    named = {row["name"]: row for row in h6["rows"]}
    assert named["population_owed"]["re_derived"] == 901
    assert named["generation_seconds"]["re_derived"] == 5532.14
    assert named["total_seconds"]["re_derived"] == 7932.14
    assert named["widest_dead_pod_that_still_fits_seconds"]["re_derived"] == 667.86
    assert named["rung_4_knife_edge_at_the_CHARGED_pre_generation"]["re_derived"] == 6.8812
    assert named["rung_4_knife_edge_at_the_MEASURED_pre_generation"]["re_derived"] == 7.8219
    assert named["step_sum_usd"]["re_derived"] == 2.173694


def test_the_rate_is_derived_from_THREE_files_and_the_rounding_is_UP():
    """Re-summed here from the same rows — a rate typed into a record is a rate nobody re-derived."""

    def mean(name):
        rows = [
            json.loads(line)
            for line in (REPO_ROOT / "results" / name).read_text("utf-8").splitlines()
            if line.strip()
        ]
        return sum(float(one["seconds"]) for one in rows) / len(rows)

    probe = mean("pass1_probe_b_rows.jsonl")
    base = mean("pass1_dev_base.jsonl")
    v2 = mean("pass1_dev_v2.jsonl")
    charged = RECORD["money"]["arithmetic"]["seconds_per_call"]

    assert charged["the_pod_class"]["slowest_base_pod_seconds_per_call"] == round(probe, 6)
    assert charged["the_pod_class"]["fastest_base_pod_seconds_per_call"] == round(base, 6)
    assert charged["the_uplift"]["v2_over_base"] == round(v2 / base, 6)
    assert charged["derived"] == round(probe * (v2 / base), 6)
    # the charge is the contract's printed figure, rounded UP from the derivation
    assert charged["charged"] == charged["v2"] == 6.14
    assert charged["charged"] >= charged["derived"]
    assert charged["charged"] - charged["derived"] < 0.01
    # and it is above every v2 rate this line has measured on a window pod
    assert charged["charged"] > 4.498473


def test_the_two_base_legs_ran_ONE_prompt_so_the_spread_is_the_POD():
    """The claim the whole price rests on, and it is checkable rather than argued."""
    rows = [
        json.loads(line)
        for line in (REPO_ROOT / "results" / "pass1_probe_b_rows.jsonl")
        .read_text("utf-8")
        .splitlines()
        if line.strip()
    ]
    dev = json.loads((REPO_ROOT / "results" / "pass1_dev_pack.json").read_text("utf-8"))
    base_prompt = dev["instruments"]["prompt_sha256"]["pass1_comment_gm4_v1"]
    assert {one["prompt_sha256"] for one in rows} == {base_prompt}
    assert {one["task"] for one in rows} == {"pass1_comment_gm4_v1"}
    # and neither the request nor the reply length explains a 2.25x gap
    width = RECORD["money"]["arithmetic"]["the_pod_class_is_not_a_width"]
    spread = RECORD["money"]["arithmetic"]["seconds_per_call"]["the_pod_class"]["spread"]
    assert spread > 2.2
    assert width["request_ratio"] < 1.1
    assert width["emitted_ratio"] < 1.1
    assert spread > width["request_ratio"] and spread > width["emitted_ratio"]


def test_a_charge_below_the_derivation_is_REFUSED(monkeypatch):
    """The rounding is deliberate and one-directional; the producer refuses the other direction."""
    monkeypatch.setattr(producer, "CHARGED_SECONDS_PER_CALL", 6.0)
    with pytest.raises(SystemExit, match="BELOW the derivation"):
        producer.rate()


def test_a_probe_that_ran_ANOTHER_prompt_is_REFUSED(monkeypatch, tmp_path):
    """If the two base legs ever stop being the same question, the spread stops being the pod."""
    rows = (REPO_ROOT / "results" / "pass1_probe_b_rows.jsonl").read_text("utf-8").splitlines()
    tampered = tmp_path / "probe.jsonl"
    tampered.write_text(
        "\n".join(
            json.dumps({**json.loads(line), "prompt_sha256": "0" * 64}, ensure_ascii=False)
            for line in rows
            if line.strip()
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(producer, "PROBE_B_ROWS", tampered)
    with pytest.raises(SystemExit, match="property of the\n? *POD|property of the POD"):
        producer.rate()


# ---- the threshold audit, path by path -------------------------------------------------------

CARRIED = {
    "arithmetic.boots_measured": "measured boots — historical readings, and the ceiling is their max",
    "arithmetic.ssh_readings": "the ssh spread — readings, not thresholds; r2 adds one more",
    "arithmetic.overhead_measured_on_r2": "what r2's overhead line actually bought, measured once",
    "deletion_tail": "r1's two measured rung-2 tails; the worse is charged",
    "curve[": "the curve's SAMPLE POINTS (at_call) — a shape, not a threshold",
    "arithmetic.ssh_seconds_charged": "rung 2's ceiling — a span, unmoved: the spread did not narrow",
    "arithmetic.stage_launch_seconds_charged": "the staging span — unmoved, and r1 measured 54 s of it",
    "arithmetic.boot_seconds_charged": "the load ceiling — ≥ the worst boot measured, unmoved",
    "arithmetic.overhead_seconds": "the overhead span — its own H6 reason row scales it to 901",
    "arithmetic.cumulative.projection_gate.overhead_seconds": "the SAME overhead, asserted equal by H6",
    "arithmetic.pre_generation_seconds": "ssh + stage/launch + load, all three unmoved",
    "at_the_CHARGED_pre_generation.pre_generation_seconds": "the same charged span, in the curve",
    "arithmetic.cumulative.backstop_tolerance_seconds": "rung 6's overshoot allowance — unmoved",
    "one_dead_pod_at_rung_2": "a dead pod at rung 2 is rung 2's ceiling, which did not move",
    "re_creations_allowed": "one re-creation, unmoved — the count is not a function of the population",
    "meter.price_ceiling_usd_per_hour": "the card price ceiling — unmoved, and read on the day anyway",
    "meter.usd_per_second_at_the_ceiling": "the ceiling divided by 3600 — unmoved with it",
    "arithmetic.request_width.mean_entities_sample": "the dev-200 sample did not move",
    "arithmetic.request_width.mean_rendered_chars_sample": "the dev-200 sample did not move",
    "arithmetic.request_width.widest_sample": "the dev-200 sample did not move",
    "arithmetic.request_width.widest_population": "the window's widest request is one of the 901",
    "step_sum.prior_pods_usd": "0.0 — this step is FRESH and opens with no pods of its own",
}
"""Every numeric leaf that sits at the same path with the same value in both money blocks, and the
reason it is the same number rather than a copied threshold. A path that matches none of these keys
fails the audit — which is the point: a new coincidence has to be looked at by a human."""

REPEALED = (
    "arithmetic.cumulative.hard_stop_seconds",
    "arithmetic.seconds_per_call.v2",
    "arithmetic.total_seconds",
    "arithmetic.recovery_arithmetic.widest_dead_pod_that_still_fits_seconds",
    "cap_usd_all_in",
)


def test_every_number_that_did_NOT_move_is_named_and_reasoned():
    r1 = numeric_paths(R1["money"])
    r2 = numeric_paths(RECORD["money"])
    carried = [path for path in sorted(set(r1) & set(r2)) if r1[path] == r2[path]]
    assert carried, "an audit with nothing in it is not an audit"
    unexplained = [path for path in carried if not any(key in path for key in CARRIED)]
    assert unexplained == [], unexplained


def test_the_five_repealed_thresholds_all_MOVED():
    """Dv613's own list, from the contract: each of these must be a different number here."""
    r1 = numeric_paths(R1["money"])
    r2 = numeric_paths(RECORD["money"])
    for path in REPEALED:
        assert r1[path] != r2[path], path
    assert r2["arithmetic.cumulative.hard_stop_seconds"] == 8600.0
    assert r2["arithmetic.seconds_per_call.v2"] == 6.14
    assert r2["arithmetic.total_seconds"] == 7932.14
    assert r2["arithmetic.recovery_arithmetic.widest_dead_pod_that_still_fits_seconds"] == 667.86
    assert r2["cap_usd_all_in"] == 2.0


def test_the_repealed_numbers_survive_ONLY_where_supersedes_quotes_them():
    """They may be NAMED, once, in the block whose job is to name them — and nowhere else."""
    money = json.dumps(RECORD["money"], ensure_ascii=False)
    import re

    for value in ("6500", "6 500", "3.4075", "5916.54", "5 916.54", "583.46", "1.50", "1.25"):
        found = re.findall(r"(?<![\d.])" + re.escape(value) + r"(?![\d])", money)
        assert found == [], f"{value} survives in the money block"
    quoted = RECORD["supersedes"]["its_numbers_this_record_REPEALS"]
    assert quoted["hard_stop_seconds"] == 6500.0
    assert quoted["seconds_per_call"] == 3.4075
    assert quoted["total_seconds"] == 5916.54
    assert quoted["widest_dead_pod_that_still_fits_seconds"] == 583.46
    assert quoted["cap_usd_all_in"] == 1.5


# ---- the pins, the bar, the rungs ------------------------------------------------------------


def test_every_pin_resolves_against_the_live_file():
    import window_summary_5c2 as summary

    block = RECORD["instruments"]
    assert block["gate"]["script"] == "scripts/gate_pass1_window_r2.py"
    assert block["gate"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "scripts" / "gate_pass1_window_r2.py"
    )
    assert block["packs"]["producer"] == "scripts/build_pass1_window_r2_pack.py"
    assert block["packs"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "scripts" / "build_pass1_window_r2_pack.py"
    )
    # the gate EXECUTES r1's bytes, so r1's gate is an instrument of this record too
    assert block["gate_runs_the_bytes_of"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "scripts" / "gate_pass1_window.py"
    )
    assert block["gate_runs_the_bytes_of"]["sha256"] == R1["instruments"]["gate"]["sha256"], (
        "the sibling runs the file r1's sealed record pins, at that record's sha"
    )
    for name, value in {
        "parser.sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
        "scorer.sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
        "transport.sha256": summary.sha256_of(
            REPO_ROOT / "scripts" / "pass1_fewshot_pod_runner.py"
        ),
    }.items():
        node = block
        for key in name.split("."):
            node = node[key]
        assert node == value, name
    # the pack this record registers is the pack on disk
    assert RECORD["population"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "results" / "pass1_window_r2_pack.json"
    )


def test_the_bar_is_over_the_901_and_the_window_is_reported_beside_it():
    bar = RECORD["bars"]["completeness"]
    assert bar["owed"] == bar["answered_minimum"] == 901 == PACK["population"]["payable_comments"]
    assert bar["sha_mismatches_maximum"] == 0
    assert bar["parse_refusals_maximum"] == 9 == int(901 * 0.01)
    assert bar["parse_refusals_fraction"] == 0.01
    window = RECORD["bars"]["the_windows_completeness"]
    assert window["not_a_bar_of_this_registration"] is True
    assert window["owed"] == 1032
    assert "PAIR" in window["keyed_on"]
    # and no report-only reading carries a threshold
    for name, value in RECORD["bars"]["report_only"].items():
        if isinstance(value, str):
            assert "passed" not in value.lower().split(), name


def test_the_kill_clock_is_seven_rungs_and_rung_4_is_the_rate_rung():
    rungs = RECORD["kill_clock"]
    assert [one["rung"] for one in rungs] == [1, 2, 3, 4, 5, 6, 7]
    assert all(one["rule"] for one in rungs)
    four = next(one for one in rungs if one["rung"] == 4)
    assert "this_is_the_rate_rung" in four
    gate = RECORD["money"]["arithmetic"]["cumulative"]["projection_gate"]
    assert "why_there_is_no_separate_rate_rung" in gate
    assert gate["overhead_seconds"] == RECORD["money"]["arithmetic"]["overhead_seconds"]
    # rung 3's backstop is the charged pre-generation and nothing else
    three = next(one for one in rungs if one["rung"] == 3)
    assert three["backstop_seconds"] == RECORD["money"]["arithmetic"]["pre_generation_seconds"]


def test_both_arms_of_the_knife_edge_are_published_and_the_charged_one_is_the_headline():
    gate = RECORD["money"]["arithmetic"]["cumulative"]["projection_gate"]["single_call_sensitivity"]
    charged = gate["at_the_CHARGED_pre_generation"]
    measured = gate["at_the_MEASURED_pre_generation"]
    assert charged["pre_generation_seconds"] == 1100.0
    assert measured["pre_generation_seconds"] == 252.5
    edge = charged["sustained_rate_the_hard_stop_can_pay_for"]
    assert edge == 6.8812
    assert measured["sustained_rate_the_hard_stop_can_pay_for"] == 7.8219
    assert edge < measured["sustained_rate_the_hard_stop_can_pay_for"], "the worse arm is charged"
    # the edge is above the slowest single call this stack has ever measured — r1's was below it
    assert edge > gate["slowest_call_in_the_stack"] == 6.214
    assert charged["headroom_over_the_slowest_call_measured"] > 1.0
    # and above the rate this record charges, which is what makes the budget self-consistent
    assert edge > RECORD["money"]["arithmetic"]["seconds_per_call"]["charged"]


def test_supersedes_names_r1_by_sha_and_by_outcome():
    import window_summary_5c2 as summary

    block = RECORD["supersedes"]
    assert block["record"] == "results/prereg_pass1_window.json"
    assert block["sha256"] == summary.sha256_of(REPO_ROOT / "results" / "prereg_pass1_window.json")
    assert "closed RED at rung 7, 131 of 1 032" in block["closing_state"]
    assert "killed by rung 4 on the rate" in block["closing_state"]
    assert "recovery refused on seconds" in block["closing_state"]
    assert block["what_it_bought"]["answered"] == 131
    assert block["what_it_bought"]["billed_usd"] == 0.173694
    assert block["what_it_bought"]["transport_defects"] == 0


def test_the_money_closes_on_every_inequality_the_contract_states():
    money = RECORD["money"]
    sums = money["arithmetic"]
    cumulative = sums["cumulative"]
    recovery = sums["recovery_arithmetic"]
    assert money["cap_usd_all_in"] == 2.00
    assert sums["worst_case_usd_at_the_price_ceiling"] < money["cap_usd_all_in"]
    assert cumulative["hard_stop_usd_at_the_price_ceiling"] < money["cap_usd_all_in"]
    assert cumulative["hard_stop_seconds"] > sums["total_seconds"]
    assert cumulative["session_ceiling_seconds"] >= cumulative["hard_stop_seconds"]
    assert recovery["then_the_full_worst_case_seconds"] <= cumulative["hard_stop_seconds"]
    assert recovery["then_the_full_worst_case_usd"] <= money["cap_usd_all_in"]
    assert (
        recovery["with_the_tail_then_the_full_worst_case_seconds"]
        <= cumulative["hard_stop_seconds"]
    )
    assert recovery["widest_dead_pod_that_still_fits_seconds"] > 500.0
    assert recovery["re_creations_allowed"] == 1
    # the step: a fresh ledger, and the window's total cost stated separately
    assert money["step_sum"]["step"] == "pass1-window-r2"
    assert money["step_sum"]["prior_pods_usd"] == 0.0
    assert money["step_sum"]["step_budget_usd"] == 2.00
    assert money["step_sum"]["the_windows_total_cost_usd"] == 2.173694


def test_the_fourteen_carry_their_FIFTH_look_and_no_bar():
    assert "FIFTH LOOK" in RECORD["return_to_the_operator"].upper()
    assert "may not be promoted" in RECORD["return_to_the_operator"]
    assert RECORD["population"]["gold"]["owed_here"] == 9
    assert RECORD["population"]["gold"]["answered_by_r1"] == 5
    assert len(RECORD["population"]["gold"]["rows"]) == 14
