"""`results/prereg_lora_b.json` — the registration, and the two things a registration can get wrong.

It can register a bar its scorer cannot read: the test below hands this record to
`score_pass1_probe.bar_p1`, the function D4 will actually score with, and makes it produce a
verdict. And it can register numbers nobody re-derived: H6 is a block of the record and three of
its rows come out RED on purpose, so the test asserts the mismatch rather than a green table.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import score_pass1_probe as scoring  # noqa: E402
import write_lora_b_prereg as producer  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_lora_b.json").read_text("utf-8"))
PROBE = json.loads((REPO_ROOT / "results" / "prereg_pass1_probe_b.json").read_text("utf-8"))
GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text("utf-8"))
SFT = json.loads((REPO_ROOT / "results" / "pass1_sft.json").read_text("utf-8"))


def evidence(wrong: int = 0) -> list[dict]:
    """One answered row per gold unit, `wrong` of them answered with the wrong class."""
    rows = []
    for index, one in enumerate(GOLD["per_comment"]):
        said = one["subject_type"] if index >= wrong else "не_наш_рынок"
        if index < wrong and one["subject_type"] == "не_наш_рынок":
            said = "сеть_ритейлер"
        rows.append(
            {
                "id": f"x#{one['msg_id']}",
                "leg": "gold",
                "thread": "t",
                "msg_id": int(one["msg_id"]),
                "parse_error": None,
                "parsed": {
                    "msg_id": int(one["msg_id"]),
                    "subject_type": said,
                    "subject_id": one["subject_id"],
                    "stance": one["stance"],
                },
            }
        )
    return rows


def test_the_record_rebuilds_byte_identical(tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"
    assert producer.main(["--outdir", str(first)]) == 0
    assert producer.main(["--outdir", str(second)]) == 0
    name = producer.OUT_NAME
    assert (first / name).read_bytes() == (second / name).read_bytes()
    assert str(tmp_path) not in (first / name).read_text("utf-8")


def test_the_shipped_record_is_what_the_producer_builds_today(tmp_path):
    assert producer.main(["--outdir", str(tmp_path)]) == 0
    assert (tmp_path / producer.OUT_NAME).read_bytes() == (
        REPO_ROOT / producer.OUT_NAME
    ).read_bytes()


def test_the_scorer_that_will_grade_the_arms_can_read_this_registration():
    """The consumer decides the shape. `bar_p1` is what D4 calls, and it is called here."""
    perfect = scoring.bar_p1(RECORD, evidence())
    assert perfect["n"] == 14 and perfect["agreed"] == 14 and perfect["passed"] is True
    assert perfect["minimum_agreed"] == 12
    two_wrong = scoring.bar_p1(RECORD, evidence(wrong=2))
    assert two_wrong["agreed"] == 12 and two_wrong["passed"] is True  # exactly at the bar
    three_wrong = scoring.bar_p1(RECORD, evidence(wrong=3))
    assert three_wrong["agreed"] == 11 and three_wrong["passed"] is False
    assert three_wrong["losses"]["budget"] == 2


def test_the_bar_block_is_probe_bs_own_with_the_arm_rule_added():
    bar = RECORD["bars"]["P1_per_comment_agreement"]
    borrowed = PROBE["bars"]["P1_per_comment_agreement"]
    for key, value in borrowed.items():
        assert bar[key] == value, key
    assert bar["arm_rule"] == "max(gold14(arm A), gold14(arm B)) ≥ 12 of 14"
    assert "double the false-pass odds" in bar["multiplicity"]
    assert "arm B" in bar["tie"]
    assert "CLOSED" in bar["red"]


def test_the_gold_rows_are_re_derived_and_refuse_to_disagree_with_the_probe_registration(
    monkeypatch,
):
    assert RECORD["population"]["gold"]["rows"] == producer.gold_rows()
    assert len(RECORD["population"]["gold"]["rows"]) == 14
    stale = json.loads(json.dumps(PROBE))
    stale["population"]["gold"]["rows"] = stale["population"]["gold"]["rows"][:-1]
    monkeypatch.setattr(
        producer,
        "read",
        lambda path: stale if "prereg_pass1" in str(path) else json.loads(path.read_text("utf-8")),
    )
    with pytest.raises(SystemExit, match="not the fourteen probe-b registered"):
        producer.gold_rows()


def test_h6_re_derives_every_registered_number_and_none_of_them_moved():
    """Green now, and it was RED on seven rows until the operator ruled branch C.

    The arms were registered at 500 and 650 LABELS and the trainable set was 464 and 607 — every
    row that rendered past the frozen `max_seq_len` had been dropped, and steps, seconds and the
    worst case moved with them. Cutting a substituted topic to the envelope a bought one occupies
    put every row back under the ceiling, and the contract's own numbers re-derive exactly. The
    test asserts the values, not merely the absence of mismatches: `mismatches: []` would also be
    what an empty table prints.
    """
    table = RECORD["h6"]
    assert {row["name"] for row in table["rows"]} == set(producer.REGISTERED)
    assert table["mismatches"] == []
    assert table["reading"] == "every registered number re-derives"
    got = {row["name"]: row for row in table["rows"]}
    assert got["arm_a_rows"]["re_derived"] == got["arm_a_rows"]["registered"] == 500
    assert got["arm_b_rows"]["re_derived"] == got["arm_b_rows"]["registered"] == 650
    assert got["arm_a_steps"]["re_derived"] == 64 and got["arm_b_steps"]["re_derived"] == 82
    assert abs(got["worst_case_usd"]["re_derived"] - 2.63) < 0.03
    assert all(row["agrees"] for row in table["rows"])


def test_nothing_is_dropped_for_length_any_more_and_the_record_says_so():
    dropped = RECORD["dropped_for_length"]
    assert dropped["n"] == 0 and dropped["ids"] == [] and dropped["by_pack"] == {}
    assert dropped["longest_kept"] <= RECORD["training"]["max_seq_len"]
    assert RECORD["reachability"]["the_context_the_gate_carries"]["topic_envelope_chars"] == 161


def test_the_labels_distribution_the_contract_registered_re_derives():
    row = next(one for one in RECORD["h6"]["rows"] if one["name"] == "combined_distribution")
    assert row["agrees"] is True
    assert row["re_derived"]["молочный_бренд"] == 2
    assert sum(row["re_derived"].values()) == 650


def test_the_worst_case_fits_the_cap_and_the_milestone_sits_under_its_stop():
    sums = RECORD["money"]["arithmetic"]
    assert sums["worst_case_usd"] < RECORD["money"]["cap_usd_all_in"]
    assert sums["cap_headroom_usd"] > 0
    assert sums["projected_usd_at_the_arm_a_milestone"] < producer.MILESTONE_USD
    # `hours` is published rounded and the dollars are the product of the unrounded value, so the
    # two agree to a hundredth of a cent and not to the last digit
    assert abs(sums["worst_case_usd"] - sums["hours"] * 0.80) < 1e-3
    assert sums["steps"] == {
        "a": SFT["census"]["arms"]["a"]["steps"],
        "b": SFT["census"]["arms"]["b"]["steps"],
    }


def test_the_kill_clock_is_the_contracts_six_rungs_in_order_each_before_its_milestone():
    """The parent contract's six, unchanged. D3a may only APPEND to this list — the test below is
    what says so, and this one is what would catch a tightening that edited a rung instead."""
    rungs = RECORD["kill_clock"]
    assert [one["rung"] for one in rungs[:6]] == [1, 2, 3, 4, 5, 6]
    assert all(one["before"] and one["rule"] for one in rungs)
    assert "0.80" in rungs[0]["rule"] and "no endpoint" in rungs[0]["rule"]
    assert "180 s" in rungs[1]["rule"]
    assert "450 s" in rungs[2]["rule"]
    assert "122 s" in rungs[3]["rule"]
    assert "2.50" in rungs[4]["rule"] and "arm B does not start" in rungs[4]["rule"]
    assert "7.5 h" in rungs[5]["rule"]
    assert not any(one.get("added") for one in rungs[:6])


def test_d3a_only_gained_rungs_and_every_one_of_them_says_so():
    rungs = RECORD["kill_clock"]
    gained = [one for one in rungs if one.get("added") == "D3a"]
    assert [one["rung"] for one in gained] == [7, 8, 9, 10]
    assert gained == rungs[6:]  # appended, never interleaved
    assert "CUMULATIVE" in gained[0]["rule"]
    assert "5.5 h" in gained[0]["rule"] and "4.40" in gained[0]["rule"]
    assert "projection gate" in gained[1]["rule"] and "MEASURED" in gained[1]["rule"]
    assert "6.00" in gained[2]["rule"] and "MEASURED rates" in gained[2]["rule"]
    assert "TRAINING-set prompt" in gained[3]["rule"] and "OWN out-file" in gained[3]["rule"]
    assert all(one["read"].startswith("money.arithmetic.cumulative") for one in gained[1:])


def test_the_hard_stop_sits_under_the_cap_and_over_the_sanctioned_recreation():
    """Three inequalities the two clauses would otherwise contradict each other on."""
    block = RECORD["money"]["arithmetic"]["cumulative"]
    cap = RECORD["money"]["cap_usd_all_in"]
    cases = block["worst_cases_usd"]
    assert block["hard_stop_hours"] == 5.5
    assert block["hard_stop_seconds"] == 5.5 * 3600
    assert cases["cumulative_hard_stop"] == 4.40 < cap
    assert cases["no_incident"] < cases["sanctioned_recreation"]
    assert (
        cases["sanctioned_recreation_with_the_registered_overhead"] < cases["cumulative_hard_stop"]
    )
    ceiling = next(r for r in RECORD["h6"]["rows"] if r["name"] == "session_ceiling_hours")
    assert block["hard_stop_hours"] < ceiling["registered"]  # under the absolute session ceiling


def test_the_projection_gates_two_tightenings_are_what_close_the_compliant_slow_path():
    """The rung's own worked examples: 121 s/step clears the watchdog and the contract's letter, and
    is KILLED once arm B is priced at the measured rate and the hard stop is one of the bounds."""
    gate = RECORD["money"]["arithmetic"]["cumulative"]["projection_gate"]
    worked = gate["worked_examples"]
    assert worked["measured"]["verdict"] == "GO"
    assert worked["measured"]["projected_usd_at_the_price_ceiling"] == pytest.approx(
        RECORD["money"]["arithmetic"]["worst_case_usd"], abs=0.001
    )
    assert worked["compliant_slow"]["seconds_per_step"] == 121.0 < 122
    assert worked["compliant_slow"]["verdict"] == "KILL"
    assert worked["compliant_slow_by_the_contracts_letter"]["verdict"] == "GO"
    assert (
        worked["compliant_slow_by_the_contracts_letter"]["projected_seconds"]
        < worked["compliant_slow"]["projected_seconds"]
    )
    assert gate["overhead_seconds"] == 1800.0
    assert "LARGER of the" in gate["arm_b_leg"]


def test_the_attempt_names_when_it_is_spent_and_the_smoke_is_not_that_moment():
    assert "SPENT at the" in RECORD["attempt"] and "GOLD-row reply" in RECORD["attempt"]
    smoke = RECORD["money"]["arithmetic"]["cumulative"]["format_smoke"]
    assert smoke["pack"] == "results/lora_b_smoke_pack.json"
    assert "NEITHER the sealed fourteen" in smoke["not_a_bar_peek"]
    assert "resume skips" in smoke["out_file_rule"]
    assert RECORD["instruments"]["smoke_pack"]["file"] == smoke["pack"]
    assert "results/lora_b_smoke_pack.json" in RECORD["frozen_when_the_pod_exists"]


def test_the_registration_says_it_was_tightened_before_any_pod_and_the_bars_were_not():
    note = RECORD["tightened_at_d3a"]
    assert "TIGHTENED BEFORE ANY POD, BARS UNTOUCHED" in note
    assert "strictly SAFER" in note
    for block in ("bars", "population.gold", "instruments.prompt_sha256", "money.cap_usd_all_in"):
        assert block in note


def test_the_supervised_boundary_registered_here_is_the_one_the_datasets_carry():
    """The tightening's own number, read back off the shipped rows rather than off its prose."""
    supervision = RECORD["training"]["supervision"]
    assert supervision["boundary_char"] == ","
    assert "AND the one separator character" in supervision["learn_chars"]
    rows = [
        json.loads(line)
        for line in (REPO_ROOT / "results" / "pass1_sft_arm_b.jsonl")
        .read_text("utf-8")
        .splitlines()
        if line
    ]
    assert len(rows) == 650
    for row in rows:
        label = "null" if row["subject_type"] is None else f'"{row["subject_type"]}"'
        assert row["target"][: row["learn_chars"]].endswith(f"{label},")
        assert not row["target"][: row["learn_chars"] - 1].endswith(",")


def test_the_reachability_block_prices_the_rows_the_arm_must_turn():
    reach = RECORD["reachability"]["to_pass"]
    assert reach["agreed_now"] == 9 and reach["minimum_agreed"] == 12
    assert reach["rows_the_arm_must_turn"] == 3
    assert len(reach["the_five_missed"]) == 5
    assert reach["by_gold_class"] == {"категория": 4, "молочный_бренд": 1}
    assert reach["training_rows_behind_them"]["молочный_бренд"] == 2  # both, since branch C
    assert reach["training_rows_behind_them"]["категория_личное"] == 47


def test_the_stance_arithmetic_that_decided_the_mask_is_in_the_record():
    block = RECORD["reachability"]["stance_is_not_trained"]
    assert block["gold_rows_scoring_stance"] == 3
    assert block["reachable_maximum_if_stance_were_taught_null"] == 11
    assert block["reachable_maximum_if_stance_were_taught_null"] < 12


def test_the_context_gap_is_registered_as_a_risk_before_the_attempt():
    block = RECORD["reachability"]["the_context_the_gate_carries"]
    assert block["gate_rows_with_an_entity_block"] == 12 and block["gate_rows"] == 14
    # branch B was bought and executed: 39 -> 282 of 650, against the gate's own 12 of 14
    assert block["arm_b_rows_with_an_entity_block"] == 282 and block["arm_b_rows"] == 650
    assert "reader pass" in block["the_open_ruling"]
    assert "SEPARATE session" in block["the_open_ruling"]
    # branch C moved the length half and NOT this one: the ratio is the same 39 over more rows
    assert "bought no verdict" in block["cause"]
    assert "leaves this one open" in block["the_open_ruling"]


def test_the_cut_marker_is_a_training_only_token_and_the_record_says_so():
    """Branch C's own asymmetry, registered before the attempt rather than found after it.

    A shortened topic ends in an ellipsis and a BOUGHT topic is never cut, so the marker sits on
    most of the training set and on none of the 64 eval prompts. Both counts are re-derived here
    off the artefacts themselves, because a registered asymmetry nobody can re-check is a sentence.
    """
    marker = RECORD["reachability"]["the_context_the_gate_carries"]["the_cut_marker"]
    pack = json.loads((REPO_ROOT / "results" / "pass1_probe_b_pack.json").read_text("utf-8"))
    assert marker["eval_items"] == len(pack["items"]) == 64
    assert (
        marker["eval_items_marked"]
        == sum(1 for one in pack["items"] if one["topic"].rstrip().endswith("…"))
        == 0
    )
    rows = [
        json.loads(line)
        for line in (REPO_ROOT / "results" / "pass1_sft_arm_b.jsonl")
        .read_text("utf-8")
        .splitlines()
        if line
    ]
    marked = sum(1 for row in rows if row["context"]["topic_cut"])
    # branch B bought 99 verdicts, so the marker's asymmetry all but disappeared: 372 -> 6
    assert marker["training_rows_marked"] == marked == 6
    assert marker["of"] == len(rows) == 650


def test_the_recovery_clause_knows_there_is_no_mid_arm_checkpoint():
    """`save_every` is 100 and the arms are 64 and 82 steps, so nothing is written until the end."""
    import yaml

    block = RECORD["money"]["recovery"]["there_is_no_mid_arm_checkpoint"]
    config = yaml.safe_load((REPO_ROOT / "config" / "qlora.yaml").read_text("utf-8"))
    assert block["save_every"] == config["training"]["save_every"] == 100
    assert block["arm_steps"] == {"a": 64, "b": 82}
    assert not any(
        step % block["save_every"] == 0 for step in range(1, max(block["arm_steps"].values()) + 1)
    )
    assert "loses that arm whole" in block["reading"]
    assert "PROVEN by listing" in RECORD["money"]["recovery"]["rule"]


def test_each_arm_evaluates_into_its_own_file_because_the_resume_would_skip():
    outs = {arm: block["eval_command"] for arm, block in RECORD["arms"].items()}
    assert len(set(outs.values())) == 2
    assert "eval_arm_a.jsonl" in outs["a"] and "eval_arm_b.jsonl" in outs["b"]
    assert "--adapter /workspace/run/arm_a/adapter" in outs["a"]
    assert "resume skips" in RECORD["instruments"]["transport"]["adapter_flag"]


def test_the_producer_pins_itself_and_what_it_borrowed():
    import hashlib

    live = hashlib.sha256(
        (REPO_ROOT / "scripts" / "write_lora_b_prereg.py").read_bytes()
    ).hexdigest()
    assert RECORD["producer"]["sha256"] == live
    for path, sha in RECORD["producer"]["borrowed"].items():
        assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == sha, path


def test_every_path_frozen_when_the_pod_exists_is_on_disk():
    for path in RECORD["frozen_when_the_pod_exists"]:
        assert (REPO_ROOT / path).exists(), path
