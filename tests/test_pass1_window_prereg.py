"""The window registration — the copy, the thresholds that MOVED, and H6 as an input audit.

`results/prereg_pass1_fewshot_r2.json` is the record this one copies its instruments and its kill
clock from, and a block copied for its ALGORITHM brings its NUMBERS with it — the class r2 itself
shipped as Dv613, when rung 4 priced r2's run with r1's repealed 1 800 s overhead
([[an_audit_of_pins_is_not_an_audit_of_thresholds]]). So the two numbers that had to move are
checked for having moved, and r2's own values are checked for being ABSENT from the money block.

H6 is checked for what it can actually catch. A money block's arithmetic is the same multiplication
done twice and cannot disagree with itself; what H6 audits is the INPUTS — the 1 032 (called, never
typed), the 2.726 s/call (re-summed from the 200 rows that produced it), the allowances carried from
r2 with their reasons, and the reachability of the bar's own two numbers.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass1_window_pack as pack_producer  # noqa: E402
import write_pass1_window_prereg as producer  # noqa: E402

RECORD = json.loads((REPO_ROOT / producer.OUT_NAME).read_text("utf-8"))
R2 = json.loads((REPO_ROOT / producer.R2_NAME).read_text("utf-8"))
PACK = json.loads((REPO_ROOT / pack_producer.OUT_NAME).read_text("utf-8"))
SUMS = RECORD["money"]["arithmetic"]


def rows_by_name() -> dict[str, dict]:
    return {one["name"]: one for one in RECORD["h6"]["rows"]}


def test_the_shipped_registration_is_what_the_producer_writes_today(tmp_path):
    assert producer.main(["--outdir", str(tmp_path)]) == 0
    assert (tmp_path / producer.OUT_NAME).read_text("utf-8") == (
        REPO_ROOT / producer.OUT_NAME
    ).read_text("utf-8")


def test_the_record_is_committed_and_equal_to_what_is_committed():
    """A pre-registration nobody committed is not a pre-registration — the gate refuses one."""
    path = REPO_ROOT / producer.OUT_NAME
    assert (
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path)], cwd=REPO_ROOT, capture_output=True
        ).returncode
        == 0
    ), "commit the registration BEFORE the pod exists"


# --- the copy, and its refusal -----------------------------------------------------------------------


def test_the_instruments_are_r2s_with_exactly_two_pins_MOVED():
    ours, theirs = RECORD["instruments"], R2["instruments"]
    for name in ("parser", "scorer", "transport", "prompt_sha256", "renderer"):
        assert ours[name] == theirs[name], name
    assert ours["v2_is_v1_plus_two_paragraphs"] == theirs["v2_is_v1_plus_two_paragraphs"]
    assert ours["prompt_v1_did_not_move"] is True
    # the two that move
    assert ours["gate"]["script"] == "scripts/gate_pass1_window.py" != theirs["gate"]["script"]
    assert ours["packs"]["producer"] == "scripts/build_pass1_window_pack.py"
    assert ours["packs"]["sha256"] != theirs["packs"]["sha256"]
    # r2's gate is IMPORTED, so it is pinned as an instrument and it is r2's own sealed sha
    assert ours["gate_imported_from"]["sha256"] == theirs["gate"]["sha256"]
    # and the one that is dropped says why
    assert "scorer_pass1_fewshot" not in ours
    assert "scorer_pass1_fewshot" in ours["dropped_from_r2"]


def test_every_copied_pin_resolves_against_the_LIVE_file():
    for path, value in producer.live_pins().items():
        assert producer.dig(RECORD["instruments"], path) == value, path
    assert RECORD["instruments"]["gate"]["sha256"] == producer.sha(producer.GATE)
    assert RECORD["instruments"]["packs"]["sha256"] == PACK["producer"]["sha256"]
    assert RECORD["population"]["sha256"] == producer.sha(producer.PACK)


def test_the_copy_REFUSES_when_a_copied_pin_stops_describing_this_checkout(monkeypatch):
    monkeypatch.setattr(
        producer, "live_pins", lambda: {"parser.sha256": "0" * 64, "scorer.sha256": "0" * 64}
    )
    with pytest.raises(SystemExit, match="no longer describes this checkout"):
        producer.instruments(R2)


def test_a_record_read_from_a_DIRTY_file_is_refused(tmp_path, monkeypatch):
    untracked = tmp_path / "not-committed.json"
    untracked.write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit, match="not tracked by git"):
        producer.sealed(untracked, "not-committed.json")


# --- the thresholds that HAD to move ------------------------------------------------------------------


def test_the_two_numbers_that_moved_off_r2_moved_and_r2s_values_survive_nowhere():
    assert RECORD["money"]["cap_usd_all_in"] == 1.50
    assert R2["money"]["cap_usd_all_in"] == 1.38
    assert SUMS["cumulative"]["hard_stop_seconds"] == 6500.0
    assert R2["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"] == 6100.0

    # a block copied for its algorithm carries its NUMBERS — so r2's are hunted for by VALUE, over
    # the numeric leaves. Prose that says «1 032 calls and not 464» is the point and must survive
    def leaves(node):
        if isinstance(node, dict):
            for key, value in node.items():
                yield from leaves(value)
        elif isinstance(node, list):
            for value in node:
                yield from leaves(value)
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            yield float(node)

    numbers = set(leaves(RECORD["money"]["arithmetic"]))
    for repealed in (6100.0, 1.38, 3076.552, 5476.552, 1.217012, 5976.552, 1.328123, 623.448):
        assert repealed not in numbers, repealed
    # 464 survives ONLY as r2's registered row count beside the measured 400, and it is named
    assert RECORD["money"]["arithmetic"]["overhead_measured_on_r2"]["rows_r2_registered"] == 464
    assert RECORD["money"]["arithmetic"]["overhead_measured_on_r2"]["rows_answered"] == 400


def test_the_allowances_r2_kept_are_kept_and_each_one_names_its_reading():
    assert SUMS["ssh_seconds_charged"] == 500.0
    assert SUMS["stage_launch_seconds_charged"] == 150.0
    assert SUMS["boot_seconds_charged"] == 450.0
    assert SUMS["overhead_seconds"] == 1300.0
    assert SUMS["cumulative"]["backstop_tolerance_seconds"] == 60.0
    assert SUMS["recovery_arithmetic"]["re_creations_allowed"] == 1
    # the boot ceiling is above every boot this stack has measured, r2's new FLOOR included
    every = [one for values in SUMS["boots_measured"].values() for one in values]
    assert SUMS["boot_seconds_charged"] >= max(every)
    assert 142.709 in every, "r2 measured a new floor and it belongs in the table"
    # the ssh spread carries all four readings, and the ceiling is above the widest lower bound
    assert len(SUMS["ssh_readings"]) == 4
    assert SUMS["ssh_seconds_charged"] >= max(SUMS["ssh_readings"].values())


def test_rung_4_and_the_money_block_charge_ONE_overhead():
    assert SUMS["cumulative"]["projection_gate"]["overhead_seconds"] == SUMS["overhead_seconds"]
    assert rows_by_name()["the_projection_gate_and_the_money_block_charge_ONE_overhead"]["agrees"]


def test_the_kill_clock_has_seven_rungs_and_rung_7_is_the_COMPLETENESS_bar():
    numbers = [one["rung"] for one in RECORD["kill_clock"]]
    assert numbers == [1, 2, 3, 4, 5, 6, 7]
    rung7 = RECORD["kill_clock"][-1]
    assert rung7["rule"] == RECORD["bars"]["completeness"]["rule"]
    assert "1032 / 1032" in rung7["rule"] or "1032" in rung7["rule"]
    # r2's rung 8 — the shot — has no counterpart here and was not carried over
    assert all("shot" not in json.dumps(one, ensure_ascii=False) for one in RECORD["kill_clock"])


# --- the money, re-derived ----------------------------------------------------------------------------


def test_the_money_is_derived_from_the_CALLED_population_and_the_MEASURED_rate():
    assert SUMS["calls"]["v2"] == len(PACK["legs"][0]["items"]) == 1032
    rate = producer.measured_v2_rate()
    assert SUMS["seconds_per_call"]["measured_mean"] == round(rate["mean"], 6)
    assert rate["rows"] == 200
    assert SUMS["seconds_per_call"]["sample"] == producer.R2_SAMPLE
    assert "8tpx8lf05n6skc" in SUMS["seconds_per_call"]["sample"]
    assert SUMS["seconds_per_call"]["sample_sha256"] == producer.sha(producer.DEV_V2_ROWS)
    # the charged rate is the ROUNDED measurement × the margin, and the rounding is conservative
    assert SUMS["seconds_per_call"]["v2"] >= rate["mean"] * SUMS["seconds_per_call"]["margin"]
    assert SUMS["generation_seconds"] == pytest.approx(1032 * SUMS["seconds_per_call"]["v2"])


def test_the_measured_rate_REFUSES_a_sample_that_is_not_the_one_it_names(tmp_path, monkeypatch):
    short = tmp_path / "short.jsonl"
    short.write_text(json.dumps({"seconds": 2.5}) + "\n", encoding="utf-8")
    monkeypatch.setattr(producer, "DEV_V2_ROWS", short)
    with pytest.raises(SystemExit, match="the sample this rate is named for is 200"):
        producer.measured_v2_rate()


def test_the_recovery_clause_is_REACHABLE_and_the_knife_edge_is_wider_than_rung_2():
    recovery = SUMS["recovery_arithmetic"]
    assert recovery["then_the_full_worst_case_seconds"] <= SUMS["cumulative"]["hard_stop_seconds"]
    assert recovery["then_the_full_worst_case_usd"] <= RECORD["money"]["cap_usd_all_in"]
    assert recovery["widest_dead_pod_that_still_fits_seconds"] == pytest.approx(
        SUMS["cumulative"]["hard_stop_seconds"] - SUMS["total_seconds"]
    )
    assert recovery["widest_dead_pod_that_still_fits_seconds"] > SUMS["ssh_seconds_charged"]
    # and the session ceiling is not what binds — the PLATFORM-held stop is
    assert SUMS["cumulative"]["session_ceiling_seconds"] >= SUMS["cumulative"]["hard_stop_seconds"]


def test_the_step_opens_with_no_pods_of_its_own():
    assert RECORD["money"]["step_sum"] == {
        "step_budget_usd": 1.50,
        "prior_pods_usd": 0.0,
        "sum_usd": 1.50,
        "rule": RECORD["money"]["step_sum"]["rule"],
    }
    assert RECORD["money"]["reading"]["step"] == "pass1-window"
    assert (
        not (REPO_ROOT / "results" / "pass1_window_run.json").exists()
        or json.loads((REPO_ROOT / "results" / "pass1_window_run.json").read_text("utf-8")).get(
            "pods"
        )
        == []
    )


# --- the bar -------------------------------------------------------------------------------------------


def test_the_bar_is_three_numbers_and_a_refusal_is_an_ANSWERED_row():
    bar = RECORD["bars"]["completeness"]
    assert (bar["owed"], bar["answered_minimum"]) == (1032, 1032)
    assert bar["sha_mismatches_maximum"] == 0
    assert bar["parse_refusals_maximum"] == 10 == int(1032 * bar["parse_refusals_fraction"])
    # the two numbers are only jointly satisfiable under this reading, and the record SAYS it
    assert "NOT disjoint" in bar["answered_means"]
    assert rows_by_name()["REASON — the bar's two numbers are jointly reachable"]["agrees"]


def test_the_report_only_readings_are_named_and_none_of_them_is_a_bar():
    block = RECORD["bars"]["report_only"]
    for name in (
        "the_fourteen",
        "the_650_labelled_rows",
        "the_450_not_in_dev_200",
        "the_dev_200",
        "the_label_distribution",
        "the_pass_2_filter_table",
    ):
        assert name in block, name
    assert "never a bar" in block["rule"] or "not a bar" in block["rule"]
    # the multiplicity sentence, and the refusal to promote it
    back = RECORD["return_to_the_operator"]
    assert "FOURTH" in back
    assert "cannot be promoted" in back
    assert "NOT an evaluation" in RECORD["what_this_run_is_not"]


def test_the_membership_counts_the_report_only_rows_need_are_in_the_record():
    assert RECORD["population"]["membership"] == {
        "gold_14": 14,
        "probe_64": 64,
        "labelled_650": 650,
        "dev_200": 200,
    }


# --- H6 --------------------------------------------------------------------------------------------------


def test_every_number_the_contract_prints_re_derives():
    assert RECORD["h6"]["mismatches"] == []
    rows = rows_by_name()
    printed = {
        "population_payable_comments": 1032,
        "population_threads": 129,
        "v2_seconds_per_call_measured": 2.726,
        "rate_margin": 1.25,
        "generation_seconds": 3516.54,
        "total_seconds": 5916.54,
        "hours": 1.6435,
        "worst_case_usd_at_the_price_ceiling": 1.3148,
        "worst_case_usd_at_the_lora_b_price": 0.8710,
        "hard_stop_usd_at_the_price_ceiling": 1.4444,
        "session_ceiling_seconds": 6750.0,
        "one_dead_pod_at_rung_2_usd": 0.1111,
        "one_dead_pod_then_the_full_worst_case_seconds": 6416.54,
        "one_dead_pod_then_the_full_worst_case_usd": 1.4259,
        "widest_dead_pod_that_still_fits_seconds": 583.46,
        "parse_refusals_maximum": 10,
    }
    for name, value in printed.items():
        assert rows[name]["registered"] == value, name
        assert rows[name]["agrees"], name


def test_H6_carries_rows_that_check_a_REASON_and_not_only_a_number():
    reasons = [one for one in RECORD["h6"]["rows"] if one["name"].startswith("REASON")]
    assert len(reasons) == 7
    assert all(one["agrees"] for one in reasons)
    # the margin's own reason is MEASURED on the two packs, not asserted: the entity blocks nearly
    # double and the request they sit in grows ~1 %, so the margin is bought against a growth an
    # order of magnitude smaller than itself
    width = SUMS["request_width"]
    margin = next(one for one in reasons if "margin exceeds" in one["name"])
    assert margin["registered"] == width["ratio"] < margin["re_derived"] == 1.25
    assert width["mean_entities_population"] > width["mean_entities_sample"]
    assert width["dev_200_rows_rendered_identically_in_both_packs"] == 200
    overhead = next(one for one in reasons if "400 → 1032" in one["name"])
    measured = SUMS["overhead_measured_on_r2"]
    assert (measured["rows_answered"], measured["rows_r2_registered"]) == (400, 464)
    assert overhead["registered"] == measured["scaled_to_this_population_seconds"]
    assert overhead["re_derived"] == SUMS["overhead_seconds"] >= overhead["registered"]
    assert measured["headroom_multiple"] > 1


def test_H6_REFUSES_a_number_that_stops_re_deriving(monkeypatch):
    monkeypatch.setattr(producer, "CHARGED_SECONDS_PER_CALL", 3.0)
    rate = producer.measured_v2_rate()
    overhead = producer.r2_overhead_reading(
        producer.sealed(producer.R2_RUN, "results/pass1_fewshot_r2_run.json")
    )
    tail = producer.deletion_tail(producer.sealed(producer.R1_RUN, producer.R1_RUN_NAME))
    sums = producer.arithmetic(rate, 1032, overhead, tail)
    sums["cumulative"]["projection_gate"]["single_call_sensitivity"] = producer.rung_4_sensitivity(
        sums, 1032, rate
    )
    block = producer.h6(sums, rate, 1032, 129)
    assert block["mismatches"], "a rate that no longer matches the contract must be a STOP"
    assert "generation_seconds" in {one["name"] for one in block["mismatches"]}
    assert block["reading"].endswith("this is a STOP")


def test_H6_REFUSES_a_hard_stop_that_no_longer_covers_the_recovery_clause(monkeypatch):
    monkeypatch.setattr(producer, "HARD_STOP_SECONDS", 6000.0)
    rate = producer.measured_v2_rate()
    overhead = producer.r2_overhead_reading(
        producer.sealed(producer.R2_RUN, "results/pass1_fewshot_r2_run.json")
    )
    tail = producer.deletion_tail(producer.sealed(producer.R1_RUN, producer.R1_RUN_NAME))
    sums = producer.arithmetic(rate, 1032, overhead, tail)
    sums["cumulative"]["projection_gate"]["single_call_sensitivity"] = producer.rung_4_sensitivity(
        sums, 1032, rate
    )
    block = producer.h6(sums, rate, 1032, 129)
    failed = {one["name"] for one in block["mismatches"]}
    assert "the_recovery_clause_fits_the_hard_stop" in failed
    assert "the_knife_edge_is_wider_than_rung_2" in failed


def test_the_overhead_reading_comes_from_r2s_OWN_gate_record():
    measured = SUMS["overhead_measured_on_r2"]
    run = json.loads((REPO_ROOT / "results" / "pass1_fewshot_r2_run.json").read_text("utf-8"))
    pod = run["pods"][-1]
    watch = next(one for one in run["gates"] if one["kind"] == "watch" and one["verdict"] == "GO")
    assert measured["pod"] == pod["pod_id"]
    assert measured["billed_seconds"] == pod["billed_seconds"]
    assert (
        measured["create_elapsed_at_the_watch_GO_seconds"] == watch["elapsed_on_this_pod_seconds"]
    )
    assert measured["measured_after_the_last_row_seconds"] == pytest.approx(
        pod["billed_seconds"] - watch["elapsed_on_this_pod_seconds"]
    )
    # the stamp is the poll that SAW completion, not the instant the last row landed — which makes
    # the measured span a LOWER bound and the scaling conservative
    assert "not the instant the last row landed" in measured["what_that_stamp_is"]


# --- the two readings the review before the pod added ------------------------------------------------


def test_the_recovery_clause_is_priced_with_the_MEASURED_deletion_tail():
    """Rung 2's ceiling is a create-elapsed; the meter stops at `pod delete`, not when it fires.

    r1 killed two pods on that rung and kept billing 78.5 s and 0.1 s past it. Charging the ceiling
    alone advertises 83.46 s of slack the stack has never achieved; the real margin is 4.96 s
    ([[a_ceiling_derived_from_one_span_measured_over_another]]).
    """
    recovery = SUMS["recovery_arithmetic"]
    tail = recovery["deletion_tail"]
    run = json.loads((REPO_ROOT / "results" / "pass1_fewshot_run.json").read_text("utf-8"))
    measured = {}
    for pod in run["pods"]:
        for gate in run["gates"]:
            if (
                gate.get("kind") == "gate0"
                and gate.get("verdict") == "KILL"
                and gate.get("pod_id") == pod["pod_id"]
            ):
                measured[pod["pod_id"]] = round(
                    pod["billed_seconds"] - gate["elapsed_on_this_pod_seconds"], 1
                )
    assert tail["measured_seconds"] == measured
    assert tail["charged_seconds"] == max(measured.values()) == 78.5
    assert recovery["one_dead_pod_at_rung_2_with_the_measured_tail_seconds"] == 578.5
    assert recovery["with_the_tail_then_the_full_worst_case_seconds"] == pytest.approx(
        578.5 + SUMS["total_seconds"]
    )
    assert (
        recovery["with_the_tail_then_the_full_worst_case_seconds"]
        <= SUMS["cumulative"]["hard_stop_seconds"]
    )
    assert recovery["margin_after_the_tail_seconds"] == pytest.approx(4.96)
    assert rows_by_name()[
        "REASON — the recovery clause is reachable WITH the measured deletion tail"
    ]["agrees"]


def test_rung_4s_knife_edge_is_computed_at_BOTH_spans_and_the_worse_one_is_the_headline():
    """The record carries two values for one span, and the flattering one must not be the claim.

    At `pre_generation_measured` (254.6 s) the edge is ~4.81 s/call and the worst call this stack
    has measured (4.066 s) is safe by 1.18x. At the `pre_generation_seconds` the money block CHARGES
    (1 100 s) the edge is ~3.99 — BELOW the measured worst. A curve computed over one span and
    quoted about a budget that pays for the other is the class this program keeps buying
    ([[a_ceiling_derived_from_one_span_measured_over_another]]).
    """
    block = SUMS["cumulative"]["projection_gate"]["single_call_sensitivity"]
    stop = SUMS["cumulative"]["hard_stop_seconds"]
    overhead = SUMS["overhead_seconds"]
    mean = block["measured_mean_seconds_per_call"]

    for key, pre in (
        (
            "at_the_MEASURED_pre_generation",
            block["at_the_MEASURED_pre_generation"]["pre_generation_seconds"],
        ),
        ("at_the_CHARGED_pre_generation", SUMS["pre_generation_seconds"]),
    ):
        arm = block[key]
        assert arm["pre_generation_seconds"] == pre
        for row in arm["curve"]:
            at = row["at_call"]
            assert row["kill_above_seconds_per_call"] == pytest.approx(
                (stop - overhead - pre - at * mean) / (1032 - at), abs=0.001
            )
        assert arm["tightest_kill_above_seconds_per_call"] == min(
            one["kill_above_seconds_per_call"] for one in arm["curve"]
        )

    measured = block["at_the_MEASURED_pre_generation"]
    charged = block["at_the_CHARGED_pre_generation"]
    # the CHARGED span is the tighter one, and it does NOT clear the worst call measured
    assert (
        charged["tightest_kill_above_seconds_per_call"]
        < measured["tightest_kill_above_seconds_per_call"]
    )
    assert charged["headroom_over_the_slowest_call_measured"] < 1.0
    assert measured["headroom_over_the_slowest_call_measured"] > 1.0
    assert block["sustained_rate_the_charged_pre_generation_can_pay_for"] == pytest.approx(
        (stop - overhead - SUMS["pre_generation_seconds"]) / 1032, abs=0.0001
    )
    assert (
        block["sustained_rate_the_charged_pre_generation_can_pay_for"]
        < block["slowest_call_in_the_sample"]
    )
    # and the headline quotes the WORSE arm, not the flattering one
    assert "the measured worst is ABOVE it" in block["the_headline"]
    assert "closes with no verdict" in block["what_it_costs_if_it_fires"]
    assert rows_by_name()["REASON — the budget's own sustained rate covers the rate it charges"][
        "agrees"
    ]


def test_the_entity_block_is_measured_as_RENDERED_and_not_as_a_python_repr():
    """It prices pass2-signals, so it has to be the chars a model reads.

    `len(str(entities))` carries quotes, braces and `: ` the renderer never emits and overstates
    the block ~3x on this population.
    """
    import sys as _sys

    _sys.path.insert(0, str(REPO_ROOT / "src"))
    from market_pulse import prompts as _prompts

    table = {one["thread"]: one for one in PACK["per_thread"]}
    widest = max(PACK["per_thread"], key=lambda one: one["entity_block_chars"])
    item = next(one for one in PACK["legs"][0]["items"] if one["thread"] == widest["thread"])

    def render(entities):
        return _prompts.pass1_messages_gm4(
            item["channel"],
            item["post_id"],
            item["topic"],
            entities,
            item["msg_id"],
            item["text"],
            task=item["task"],
            examples=item["examples"],
        )[0]["content"]

    rendered = len(render(item["entities"])) - len(render([]))
    assert widest["entity_block_chars"] == rendered
    assert rendered < sum(len(str(one)) for one in item["entities"])
    assert all(one["entity_block_chars"] >= 0 for one in table.values())


def test_the_fourteen_have_a_NAMED_producer_that_is_a_CENSUS_and_not_a_bar():
    """The reading D2 owes over the gold, DRIVEN at $0 from what the record actually carries.

    Two instruments are refused by name and the refusals are CHECKED, not asserted: `leg_table`
    compares against the LABEL map and no gold pair is in it (0 of 14), and `bar_p1` returns
    `passed` — it is a BAR, and this contract may not take one on the fourteen. What is left is the
    comparison both of them use, run here on the record's own registered rows to prove D2 can
    compute the census without inventing anything after the money.
    """
    import sys as _sys

    _sys.path.insert(0, str(REPO_ROOT / "scripts"))
    _sys.path.insert(0, str(REPO_ROOT / "src"))
    import gate_pass1_fewshot as r2gate
    import score_pass1_probe as bar
    import score_reader_probe_b as probe_b

    from market_pulse import scorer

    gold = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text("utf-8"))
    pairs = {
        (
            f"{row['channel']}:{(row.get('evidence_row') or {}).get('post_id_in_the_store')}",
            int(row["msg_id"]),
        )
        for row in gold["per_comment"]
    }
    assert len(pairs) == 14
    assert not (pairs & set(r2gate.labels())), "leg_table's map holds none of the fourteen"

    block = RECORD["instruments"]["gold"]
    assert block["sha256"] == producer.sha(REPO_ROOT / "results" / "reader_gold_w1_r2.json")
    assert block["comparison"] == "market_pulse.scorer.reader_comment_agreement"
    assert block["collapse_sha256"] == producer.sha(
        REPO_ROOT / "scripts" / "score_reader_probe_b.py"
    )
    assert "CENSUS ROW" in block["rule"]

    rows = RECORD["population"]["gold"]["rows"]
    assert {(one["thread"], int(one["msg_id"])) for one in rows} == pairs

    assert "P1_per_comment_agreement" not in RECORD["bars"]
    with pytest.raises(KeyError):
        bar.bar_p1(RECORD, [])

    by_id = {int(row["msg_id"]): row for row in gold["per_comment"]}
    wanted, said = [], []
    for one in rows:
        row = by_id[int(one["msg_id"])]
        wanted.append(
            {
                "msg_id": int(one["msg_id"]),
                "subject_type": probe_b.collapse(row.get("subject_type")),
                "scored_fields": ["subject_type"],
            }
        )
        said.append(
            {
                "msg_id": int(one["msg_id"]),
                "subject_type": probe_b.collapse(row.get("subject_type")),
            }
        )
    result = scorer.reader_comment_agreement(wanted, said)
    assert (result["n"], result["agreed"], result["absent"]) == (14, 14, 0)
    assert "passed" not in result and "minimum_agreed" not in result
