"""pass2-signals D0 — the module, the pack, the record, the gate, the runner and the runbook.

Every test here runs at $0 on a fake transport. The rungs that cost money are DRIVEN — a liveness
rung nobody ever saw fire is a rung nobody has ([[guard_selftest_negative_control]]).
"""

import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass2_pack as builder  # noqa: E402
import gate_pass2_signals as gate  # noqa: E402
import pass2_pod_runner as runner  # noqa: E402
import score_pass2_signals as scoring  # noqa: E402
import write_pass2_prereg as producer  # noqa: E402

from market_pulse import pass2, prompts  # noqa: E402

RESULTS = REPO_ROOT / "results"
PACK = json.loads((RESULTS / "pass2_pack.json").read_text(encoding="utf-8"))
RECORD = json.loads((RESULTS / "prereg_pass2_signals.json").read_text(encoding="utf-8"))
RUNBOOK = (REPO_ROOT / "scripts" / "runbook_pass2_signals.md").read_text(encoding="utf-8")
ITEMS = PACK["legs"][0]["items"]
BY_ID = {one["id"]: one for one in ITEMS}


# --- the population and the pack -------------------------------------------------------------


def test_the_pack_is_the_censuss_own_filter_thread_for_thread():
    census = json.loads((RESULTS / "pass1_window_r2_census.json").read_text(encoding="utf-8"))
    wanted = {
        one["thread"]: one["filtered_rows"]
        for one in census["pass_2_filter"]["per_thread"]
        if one["filtered_rows"]
    }
    assert {one["id"]: len(one["comments"]) for one in ITEMS} == wanted
    assert len(ITEMS) == 79
    assert sum(len(one["comments"]) for one in ITEMS) == 281


def test_the_pack_rebuilds_byte_for_byte_from_its_own_inputs():
    """[[reproducible_means_try_it]] — the pack is DERIVED, so building it again must give it back."""
    again = builder.build()
    assert json.dumps(again, ensure_ascii=False, sort_keys=True) == json.dumps(
        PACK, ensure_ascii=False, sort_keys=True
    )


def test_the_builder_REFUSES_when_its_selection_leaves_the_censuss_filter(monkeypatch):
    """The filter is the authority and the selection is what is being checked — watched red."""
    real = builder.r1census.pass_2_filter

    def one_row_short(pack, parsed, refused_ids, threads):
        table = real(pack, parsed, refused_ids, threads)
        moved = json.loads(json.dumps(table))
        for cell in moved["per_thread"]:
            if cell["filtered_rows"]:
                cell["filtered_rows"] -= 1
                break
        return moved

    monkeypatch.setattr(builder.r1census, "pass_2_filter", one_row_short)
    with pytest.raises(SystemExit, match="first disagreement"):
        builder.build()


def test_the_builder_REFUSES_an_entity_block_that_has_moved_since_the_window(monkeypatch):
    monkeypatch.setattr(builder.sft, "verdicts", dict)
    with pytest.raises(SystemExit, match="a context pass 1 never saw"):
        builder.build()


def test_the_smoke_leg_is_exactly_the_five_F_threads_and_it_is_a_prefix():
    gold = json.loads((RESULTS / "reader_gold_w1_r2.json").read_text(encoding="utf-8"))
    wanted = [f"{one['channel']}:{one['post_id']}" for one in gold["flagships"]]
    assert PACK["smoke"]["ids"] == wanted
    assert [one["id"] for one in ITEMS[:5]] == wanted
    assert PACK["smoke"]["units"] == 5
    assert PACK["smoke"]["cases"] == ["F1", "F2", "F3", "F4", "F5"]


def test_every_comment_carries_a_pass_2_filter_label_and_no_gold_label():
    for item in ITEMS:
        for row in item["comments"]:
            assert row["subject_type"] in pass2.PASS2_SUBJECT_TYPES


def test_the_membership_flags_cannot_reach_the_rendered_request():
    """The pod is shown five fields and the exam's own membership is not one of them."""
    assert PACK["contamination"]["renderings_that_move_without_the_membership_flags"] == []
    assert PACK["contamination"]["requests_naming_a_case_id"] == []
    item = BY_ID["@VARUS_channel:10613"]
    assert item["membership"]["F"] == ["F1"]
    content = pass2.pass2_messages_gm4(
        item["channel"], item["post_id"], item["post"], item["entities"], item["comments"]
    )[0]["content"]
    assert "F1" not in content
    assert "membership" not in content


def test_every_item_re_renders_to_the_sha_the_pack_pinned():
    import build_pass1_fewshot_packs as fewshot

    for item in ITEMS:
        content = pass2.pass2_messages_gm4(
            item["channel"], item["post_id"], item["post"], item["entities"], item["comments"]
        )[0]["content"]
        assert fewshot.sha_text(content) == item["rendering_sha256"]
        assert len(content) == item["rendered_chars"]


def test_no_request_is_over_the_registered_input_ceiling():
    assert pass2.PASS2_MAX_INPUT_CHARS == prompts.PASS1_MAX_INPUT_CHARS == 12_000
    assert max(one["rendered_chars"] for one in ITEMS) <= pass2.PASS2_MAX_INPUT_CHARS
    assert PACK["length"]["headroom_chars"] > 0


def test_a_thread_with_no_filtered_comment_is_refused_rather_than_rendered_empty():
    with pytest.raises(ValueError, match="no filtered comment"):
        pass2.pass2_messages_gm4("@x", 1, "post", [], [])


def test_a_comment_labelled_outside_the_filter_is_refused():
    with pytest.raises(ValueError, match="not one of the pass-2 filter"):
        pass2.pass2_messages_gm4(
            "@x",
            1,
            "post",
            [],
            [{"msg_id": 1, "text": "t", "subject_type": "не_наш_рынок", "stance": None}],
        )


def test_the_entity_block_renders_its_emptiness_explicitly():
    assert pass2.entity_block([]) == "(this thread resolved no entity)"


# --- the parser: strict authority, both directions ---------------------------------------------


def unit(**kw) -> dict:
    base = {
        "channel": "@x",
        "post_id": 1,
        "entities": [
            {
                "name": "Rud",
                "msg_id": None,
                "subject_type": "молочный_бренд",
                "reading": "бренд",
                "quote": "Rud",
            }
        ],
        "comments": [
            {
                "msg_id": 7,
                "text": "смачно",
                "subject_type": "категория_личное",
                "subject_id": None,
                "stance": "positive",
            },
            {
                "msg_id": 8,
                "text": "+",
                "subject_type": "сеть_ритейлер",
                "subject_id": "varus",
                "stance": None,
            },
        ],
    }
    return {**base, **kw}


def reply(**kw) -> str:
    base = {
        "thread": {"channel": "@x", "post_id": 1},
        "post_summary": "пост",
        "discussion_summary": "обговорення",
        "signals": [
            {
                "signal_type": "похвала",
                "subject_type": "категория_личное",
                "subject_id": "морозиво",
                "aspect": "taste",
                "stance": "positive",
                "reading": "смачно",
                "evidence": [7],
                "quote": "смачно",
            }
        ],
        "per_comment": [
            {
                "msg_id": 7,
                "subject_type": "категория_личное",
                "subject_id": None,
                "stance": "positive",
                "aspects": ["taste"],
                "subject_doubt": False,
                "note": None,
            }
        ],
        "noise": [{"msg_id": 8, "class": "плюс_спам"}],
    }
    return json.dumps({**base, **kw}, ensure_ascii=False)


def test_a_reply_that_relabels_a_comment_is_REFUSED_by_cause():
    with pytest.raises(pass2.RelabelError, match="no authority to relabel"):
        pass2.parse_pass2(
            reply(
                per_comment=[
                    {
                        "msg_id": 7,
                        "subject_type": "молочный_бренд",
                        "subject_id": None,
                        "stance": None,
                        "aspects": [],
                        "subject_doubt": False,
                        "note": None,
                    }
                ]
            ),
            unit=unit(),
        )


def test_a_signal_that_relabels_the_subject_of_its_evidence_is_REFUSED():
    with pytest.raises(pass2.RelabelError):
        pass2.parse_pass2(
            reply(
                signals=[
                    {
                        "signal_type": "похвала",
                        "subject_type": "молочный_бренд",
                        "subject_id": "rud",
                        "aspect": "taste",
                        "stance": "positive",
                        "reading": "x",
                        "evidence": [7],
                        "quote": "смачно",
                    }
                ]
            ),
            unit=unit(),
        )


def test_a_relabel_error_is_a_parse_error_so_the_gate_counts_it_as_a_refusal():
    assert issubclass(pass2.RelabelError, prompts.ParseError)


def test_a_signal_citing_two_rows_may_take_the_label_of_either():
    verdict = pass2.parse_pass2(
        reply(
            signals=[
                {
                    "signal_type": "жалоба",
                    "subject_type": "сеть_ритейлер",
                    "subject_id": "varus",
                    "aspect": "service",
                    "stance": "negative",
                    "reading": "x",
                    "evidence": [7, 8],
                    "quote": "смачно",
                }
            ]
        ),
        unit=unit(),
    )
    assert verdict["signals"][0]["subject_type"] == "сеть_ритейлер"


def test_an_id_that_was_not_in_the_request_is_refused_everywhere_it_can_appear():
    for kw in (
        {"noise": [{"msg_id": 99, "class": "скам"}]},
        {
            "per_comment": [
                {
                    "msg_id": 99,
                    "subject_type": "категория_личное",
                    "subject_id": None,
                    "stance": None,
                    "aspects": [],
                    "subject_doubt": False,
                    "note": None,
                }
            ]
        },
        {
            "signals": [
                {
                    "signal_type": "похвала",
                    "subject_type": "категория_личное",
                    "subject_id": "x",
                    "aspect": "taste",
                    "stance": None,
                    "reading": "x",
                    "evidence": [99],
                    "quote": "q",
                }
            ]
        },
    ):
        with pytest.raises(prompts.ParseError, match="not in this request"):
            pass2.parse_pass2(reply(**kw), unit=unit())


def test_a_signal_with_no_comment_behind_it_is_refused():
    """`from_post` is the hole the relabelling refusal would otherwise be walked around through."""
    with pytest.raises(prompts.ParseError, match="names no comment"):
        pass2.parse_pass2(
            reply(
                signals=[
                    {
                        "signal_type": "тренд",
                        "subject_type": "молочный_бренд",
                        "subject_id": "rud",
                        "aspect": "taste",
                        "stance": None,
                        "reading": "x",
                        "evidence": [],
                        "quote": "q",
                        "from_post": True,
                    }
                ]
            ),
            unit=unit(),
        )
    assert "from_post" not in pass2.PASS2_THREAD_PROMPT


def test_a_reply_about_another_thread_is_refused():
    with pytest.raises(prompts.ParseError, match="the reply is about"):
        pass2.parse_pass2(reply(thread={"channel": "@y", "post_id": 1}), unit=unit())


def test_the_entity_block_is_INJECTED_and_the_model_is_never_asked_for_it():
    verdict = pass2.parse_pass2(reply(), unit=unit())
    assert verdict["entities"] == unit()["entities"]
    assert '"entities"' not in pass2.PASS2_THREAD_PROMPT
    # and a reply that tries to supply one is overwritten, not merged
    other = json.loads(reply())
    other["entities"] = [
        {
            "name": "Ласунка",
            "msg_id": 7,
            "subject_type": "молочный_бренд",
            "reading": "x",
            "quote": "q",
        }
    ]
    again = pass2.parse_pass2(json.dumps(other, ensure_ascii=False), unit=unit())
    assert again["entities"] == unit()["entities"]


def test_a_DROP_lands_in_noise_and_removes_nothing_from_per_comment():
    kept = pass2.parse_pass2(
        reply(
            per_comment=[
                {
                    "msg_id": 7,
                    "subject_type": "категория_личное",
                    "subject_id": None,
                    "stance": "positive",
                    "aspects": ["taste"],
                    "subject_doubt": False,
                    "note": None,
                },
                {
                    "msg_id": 8,
                    "subject_type": "сеть_ритейлер",
                    "subject_id": "varus",
                    "stance": None,
                    "aspects": [],
                    "subject_doubt": False,
                    "note": None,
                },
            ],
            noise=[],
        ),
        unit=unit(),
    )
    dropped = pass2.parse_pass2(reply(), unit=unit())
    assert kept["accounting"]["kept"] == [7, 8]
    assert dropped["accounting"]["kept"] == [7]
    assert dropped["accounting"]["dropped"] == [8]
    # the row that stayed is untouched, field for field
    assert [one for one in kept["per_comment"] if one["msg_id"] == 7] == [
        one for one in dropped["per_comment"] if one["msg_id"] == 7
    ]
    assert dropped["accounting"]["in_neither_list"] == []


def test_a_comment_in_neither_list_is_counted_and_not_refused():
    verdict = pass2.parse_pass2(reply(noise=[]), unit=unit())
    assert verdict["accounting"]["in_neither_list"] == [8]


def test_subject_doubt_survives_the_readers_parser_which_would_drop_it():
    verdict = pass2.parse_pass2(
        reply(
            per_comment=[
                {
                    "msg_id": 7,
                    "subject_type": "категория_личное",
                    "subject_id": None,
                    "stance": None,
                    "aspects": [],
                    "subject_doubt": True,
                    "note": "мова про бренд, не про категорію",
                }
            ]
        ),
        unit=unit(),
    )
    payload, _ = prompts._reader_object(reply())
    payload["entities"] = unit()["entities"]
    assert "subject_doubt" not in prompts._reader(payload)["per_comment"][0]
    assert verdict["per_comment"][0]["subject_doubt"] is True
    assert verdict["per_comment"][0]["note"] == "мова про бренд, не про категорію"


def test_the_readers_container_repairs_still_fire_through_pass_2s_wrapper():
    body = json.loads(reply())
    body["noise"] = {}
    verdict = pass2.parse_pass2(json.dumps(body, ensure_ascii=False), unit=unit())
    assert verdict["noise"] == []
    assert "noise: empty object -> empty list" in verdict["repairs"]


# --- the record ---------------------------------------------------------------------------------


def test_H6_re_derives_every_number_the_contract_prints():
    assert RECORD["h6"]["mismatches"] == []
    assert len(RECORD["h6"]["rows"]) >= 35
    assert all(one["agrees"] for one in RECORD["h6"]["rows"])


def test_H6_REFUSES_when_a_registered_number_is_moved(monkeypatch, tmp_path):
    """The mutation the step-1 gate exists for, watched red."""
    monkeypatch.setattr(producer, "SMOKE_SECONDS_PER_CALL", 130.0)
    with pytest.raises(SystemExit, match="do not re-derive"):
        producer.main(["--out", str(tmp_path / "moved.json")])
    assert not (tmp_path / "moved.json").exists()


def test_every_clock_rung_carries_its_deadline_by_key():
    for one in RECORD["kill_clock"]:
        if int(one["rung"]) in gate.DEADLINE_RUNGS:
            assert isinstance(one["deadline_seconds"], int | float)


def poisoned_record() -> dict:
    """Every rung's prose prefixed with its own index — Dv669's exact mutation."""
    poisoned = json.loads(json.dumps(RECORD))
    for one in poisoned["kill_clock"]:
        one["rule"] = f"rung {one['rung']} of 9 — {one['rule']}"
    return poisoned


def test_the_prose_of_a_rung_can_no_longer_move_its_deadline():
    """Dv669: `first_number("rung 5 of 7 — 600 s …")` is 5, and the suite stays green."""
    poisoned = poisoned_record()
    assert gate.r1.first_number(gate._SHIPPED["rung"](poisoned, 5)["rule"]) == 5
    assert gate.r1.first_number(gate.rung(poisoned, 5)["rule"]) == 600.0
    assert gate.r1.first_number(gate.rung(poisoned, 2)["rule"]) == 500.0
    assert gate.r1.first_number(gate.rung(poisoned, 3)["rule"]) == 450.0


def test_the_RUNGS_THEMSELVES_read_the_key_and_not_the_prose(tmp_path, monkeypatch):
    """Rebinding `rung` reaches `watch` and NOT `gate_zero`/`gate_boot`, which are defined in
    another module — so every one of the three is driven here, on a poisoned record."""
    poisoned = poisoned_record()
    state = state_with_pod()
    # rung 2: 500 s is the deadline, and the poisoned prose leads with a 2
    early = gate.gate_zero(poisoned, state, 400.0, False)
    late = gate.gate_zero(poisoned, state, 501.0, False)
    assert early["threshold_seconds"] == 500.0 and early["verdict"] == "WAIT"
    assert late["verdict"] == "KILL"
    # rung 3: 450 s from the launch anchor
    boot = gate.gate_boot(poisoned, state, 600.0, 460.0, "2026-08-22T10:04:00+00:00")
    assert boot["threshold_seconds"] == 450.0 and boot["verdict"] == "KILL"
    assert (
        gate.gate_boot(poisoned, state, 600.0, 440.0, "2026-08-22T10:04:00+00:00")["verdict"]
        == "GO"
    )
    # rung 5: 600 s of idle, through the watch loop itself
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.r1, "RECORD", record)
    record.write_text(json.dumps(state), encoding="utf-8")
    log = tmp_path / "pod.log"
    log.write_text("boot\n", encoding="utf-8")
    out_rows(tmp_path / "pass2_signals_v1.jsonl", list(PACK["smoke"]["ids"])[:3], 30.0)
    clock = {"now": 0.0}
    verdict = gate.watch(
        poisoned,
        state,
        [PACK],
        where=tmp_path,
        log=log,
        pull=lambda: None,
        kill=lambda: {"deleted": True},
        sleep=lambda _s: clock.__setitem__("now", clock["now"] + 100.0),
        clock_now=lambda: clock["now"],
        now=gate.r1.stamp("2026-08-22T10:05:00+00:00"),
        poll_seconds=0,
    )
    assert verdict["idle_deadline_seconds"] == 600.0, "not 5, which is what the prose leads with"
    assert verdict["verdict"] == "KILL" and "rung 5" in verdict["cause"]


def test_a_clock_rung_with_no_deadline_key_is_REFUSED_and_never_defaulted():
    poisoned = json.loads(json.dumps(RECORD))
    for one in poisoned["kill_clock"]:
        if int(one["rung"]) == 5:
            one["deadline_seconds"] = None
    with pytest.raises(SystemExit, match="carries no `deadline_seconds`"):
        gate.rung(poisoned, 5)


def test_the_registered_bars_name_their_expectation_and_do_not_move():
    one = RECORD["bars"]["1_flagships"]
    assert one["threshold"] == "5 of 5 cases"
    assert one["expectation"]["F2"]["expected"] == "RED"
    assert RECORD["reachability"]["unreachable_flagship_signals"] == ["F2a"]
    assert "F5a" in one["expectation"]["reachable_signals"]


def test_bar_2_is_computed_before_the_pod_and_E1_is_the_unreachable_case():
    two = RECORD["bars"]["2_entity_cases"]["computed"]
    assert two["cases_answered"] == 3
    assert two["passed"] is False
    assert two["per_case"] == {"E1": False, "E2": True, "E3": True, "E4": True}
    assert RECORD["reachability"]["unreachable_entity_cases"] == ["E1"]


def test_bar_3_is_scored_over_the_one_noise_thread_pass_2_calls():
    three = RECORD["bars"]["3_noise"]
    assert three["scored_over"] == ["N2"]
    assert "N1" in three["excluded_with_cause"]
    assert set(three["not_called"]) == {"N3", "N4", "N5", "N6"}


def test_no_bar_on_the_fourteen_is_registered():
    assert "4_per_comment_agreement" not in RECORD["bars"]
    assert (
        "SIXTH look" in RECORD["bars"]["report_only"]["4_per_comment_agreement_is_NOT_registered"]
    )


def test_the_money_authorises_the_smoke_and_not_the_run():
    sums = RECORD["money"]["arithmetic"]
    assert sums["total_seconds"] == 3000.0
    assert sums["cumulative"]["hard_stop_seconds"] == 6600.0
    assert sums["worst_case_usd_at_the_price_ceiling"] < RECORD["money"]["cap_usd_all_in"]
    full = 79 * 120.0 + 1100.0 + 1300.0
    assert full > sums["cumulative"]["hard_stop_seconds"]
    assert sums["the_full_run_is_priced_by_rung_S_prime"]["knife_edge_seconds_per_call"] == 48.6486


def test_the_knife_edge_prose_carries_the_BILLED_wait():
    """The pod sits in `wait_for_go` while the Mac decides and those seconds are billed. The
    contract's 48.6486 is the arm at a ZERO wait; the record publishes the band and says the gate
    uses neither ([[two_values_for_one_input_get_quoted_kindly]])."""
    arm = RECORD["money"]["arithmetic"]["the_full_run_is_priced_by_rung_S_prime"]
    assert "go_wait_seconds" in arm["knife_edge_formula"]
    assert arm["knife_edge_at_a_zero_go_wait"] == 48.6486
    assert arm["knife_edge_at_the_full_go_wait"] == 40.5405
    assert arm["knife_edge_at_the_full_go_wait"] < arm["knife_edge_at_a_zero_go_wait"]
    wait = next(one["deadline_seconds"] for one in RECORD["kill_clock"] if int(one["rung"]) == 8)
    assert round((6600 - 1300 - 1100 - 600 - wait) / 74, 4) == arm["knife_edge_at_the_full_go_wait"]
    assert "cumulative_billed_seconds" in arm["the_wait_is_billed_and_the_band_is_why"]


def test_the_overhead_is_one_number_in_two_places():
    sums = RECORD["money"]["arithmetic"]
    assert sums["overhead_seconds"] == sums["cumulative"]["projection_gate"]["overhead_seconds"]


# --- the gate: the authorised leg, rung S′, rung 5, rung 7 --------------------------------------


def state_with_pod(**kw) -> dict:
    pod = {
        "pod_id": "p1",
        "created_at": "2026-08-22T10:00:00+00:00",
        "usd_per_hour": 0.74,
        "card": "RTX 4090",
        "terminate_after": "2026-08-22T11:50:00+00:00",
    }
    return {"pods": [{**pod, **kw}], "gates": []}


def state_created_now(**kw) -> dict:
    """A pod created NOW — for the tests that drive a command which reads the REAL clock.

    `run_go_no_go` calls `go_no_go(where)` with no `now`, so rung S′ projects from
    `datetime.now(UTC)` minus the pod's `created_at`. With a FIXED create stamp that elapsed term
    grows every minute the suite is not run: at 30 s/call the charge is 45, `74 × 45 + 1 300 =
    4 630`, and the GO half of `test_the_go_token_is_written_only_after_the_verdict_is_recorded`
    stopped passing at `created_at + 1 970 s` — **10:32:50Z on 2026-08-22**, which is when it went
    red with no commit behind it. The STOP halves are safe in the other direction, so only the GO
    needed a stamp that moves with the clock it is measured against
    ([[a_git_clock_proof_needs_more_than_a_minute]] read the other way round: an assertion whose
    truth depends on WHEN it runs is a clock, not a test).
    """
    now = datetime.now(UTC)
    return state_with_pod(
        created_at=now.isoformat(timespec="seconds"),
        terminate_after=(now + timedelta(seconds=6600)).isoformat(timespec="seconds"),
        **kw,
    )


def with_go(state: dict, verdict: str = "GO") -> dict:
    return {
        **state,
        "gates": [*state["gates"], {"kind": gate.GO_KIND, "verdict": verdict, "pod": 1}],
    }


def test_the_authorised_leg_is_the_smoke_until_the_go_and_the_whole_leg_after(
    tmp_path, monkeypatch
):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.r1, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    assert gate.legs_of(PACK)[0]["units"] == 5
    assert len(gate.authorised(PACK)["legs"][0]["items"]) == 5
    record.write_text(json.dumps(with_go(state_with_pod())), encoding="utf-8")
    assert gate.legs_of(PACK)[0]["units"] == 79
    assert len(gate.authorised(PACK)["legs"][0]["items"]) == 79
    # a STOP is not a GO
    record.write_text(json.dumps(with_go(state_with_pod(), "STOP")), encoding="utf-8")
    assert gate.legs_of(PACK)[0]["units"] == 5


def test_the_projection_prices_the_authorised_leg_and_not_the_whole_pack(tmp_path, monkeypatch):
    """`leg_state` is defined in gate_pass1_fewshot, so its own `legs_of` is NOT the rebound one.

    The wrapper hands it an already-truncated pack instead, and this is the test that says so: with
    no reply on disk the leg is priced at the registered 120 s/call, and 79 × 120 + 1 300 against a
    6 600 s stop would kill the pod at the first poll.
    """
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.r1, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    (tmp_path / "pass2_signals_v1.jsonl").write_text("", encoding="utf-8")
    before = gate.leg_state(RECORD, [PACK], tmp_path)
    assert [one["remaining"] for one in before] == [5]
    assert before[0]["seconds_per_call_used"] == 120.0
    ahead = gate.r1.projection(
        RECORD,
        json.loads(record.read_text(encoding="utf-8")),
        before,
        gate.r1.stamp("2026-08-22T10:05:00+00:00"),
    )
    assert ahead["verdict"] == "GO", "the smoke must not be killed before it has answered anything"
    record.write_text(json.dumps(with_go(state_with_pod())), encoding="utf-8")
    after = gate.leg_state(RECORD, [PACK], tmp_path)
    assert [one["remaining"] for one in after] == [79]
    killed = gate.r1.projection(
        RECORD,
        json.loads(record.read_text(encoding="utf-8")),
        after,
        gate.r1.stamp("2026-08-22T10:05:00+00:00"),
    )
    assert killed["verdict"] == "KILL", (
        "79 units at the registered rate is 11 880 s against a 6 600 s stop — which is why the"
        " authorisation may not be given before the smoke has measured the rate"
    )


def out_rows(path: Path, ids: list[str], seconds: float | list[float]) -> None:
    values = [seconds] * len(ids) if isinstance(seconds, int | float) else seconds
    path.write_text(
        "".join(
            json.dumps(
                {
                    "index": index,
                    "id": one,
                    "thread": one,
                    "rendering_sha256": BY_ID[one]["rendering_sha256"],
                    "reply": "{}",
                    "balanced": True,
                    "seconds": value,
                    "elapsed_since_start": 300.0 + index,
                },
                ensure_ascii=False,
            )
            + "\n"
            for index, (one, value) in enumerate(zip(ids, values, strict=True))
        ),
        encoding="utf-8",
    )


def drive_go_no_go(tmp_path, monkeypatch, seconds, elapsed=1500.0):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.r1, "RECORD", record)
    monkeypatch.setattr(gate.r1, "registration", lambda: RECORD)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    out_rows(tmp_path / "pass2_signals_v1.jsonl", list(PACK["smoke"]["ids"]), seconds)
    created = gate.r1.stamp("2026-08-22T10:00:00+00:00")
    now = created + __import__("datetime").timedelta(seconds=elapsed)
    return gate.go_no_go(tmp_path, now=now)


def test_rung_S_prime_says_GO_at_30_seconds_a_call_and_STOP_at_60(tmp_path, monkeypatch):
    fast = drive_go_no_go(tmp_path, monkeypatch, 30.0)
    assert fast["verdict"] == "GO"
    assert fast["charged_full_seconds_per_call"] == 45.0
    slow = drive_go_no_go(tmp_path, monkeypatch, 60.0)
    assert slow["verdict"] == "STOP"
    assert slow["charged_full_seconds_per_call"] == 90.0


def test_rung_S_prime_charges_the_larger_of_its_two_arms(tmp_path, monkeypatch):
    """One slow call among four fast ones is charged at the MAXIMUM, not at 1.5 × the mean."""
    spiky = drive_go_no_go(tmp_path, monkeypatch, [10.0, 10.0, 10.0, 10.0, 100.0])
    assert spiky["charged_arm"] == "the maximum call"
    assert spiky["charged_full_seconds_per_call"] == 100.0
    assert spiky["verdict"] == "STOP"
    flat = drive_go_no_go(tmp_path, monkeypatch, [28.0, 28.0, 28.0, 28.0, 28.0])
    assert flat["charged_arm"] == "1.5 × mean"
    assert flat["charged_full_seconds_per_call"] == 42.0
    assert flat["verdict"] == "GO"


def test_rung_S_prime_publishes_both_projection_arms(tmp_path, monkeypatch):
    one = drive_go_no_go(tmp_path, monkeypatch, 30.0)
    assert one["projected_cumulative_seconds"] == one["projected_create_elapsed_seconds"]
    assert one["the_cap_cannot_bind_before_the_stop"] is True


def test_rung_S_prime_WAITS_while_the_smoke_is_unanswered(tmp_path, monkeypatch):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.r1, "RECORD", record)
    monkeypatch.setattr(gate.r1, "registration", lambda: RECORD)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    out_rows(tmp_path / "pass2_signals_v1.jsonl", list(PACK["smoke"]["ids"])[:3], 30.0)
    verdict = gate.go_no_go(tmp_path)
    assert verdict["verdict"] == "WAIT"
    assert len(verdict["smoke_missing"]) == 2


def test_rung_5_fires_on_a_log_that_stops_and_not_only_on_a_file_that_stops(tmp_path, monkeypatch):
    """A pod that is WAITING keeps the log rising; one that is wedged does not."""
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.r1, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    log = tmp_path / "pod.log"
    out = tmp_path / "pass2_signals_v1.jsonl"
    out_rows(out, list(PACK["smoke"]["ids"])[:3], 30.0)
    clock = {"now": 0.0}
    lines = {"n": 1}

    def tick(step: float):
        clock["now"] += step

    log.write_text("boot\n", encoding="utf-8")
    kills = []

    def growing_log():
        lines["n"] += 1
        log.write_text(
            "boot\n" + "".join(f"WAIT {i}\n" for i in range(lines["n"])), encoding="utf-8"
        )

    # the file never grows; the LOG does — and the pod survives past the 600 s deadline
    with pytest.raises(RuntimeError, match="stop the loop"):
        gate.r1.watch(
            RECORD,
            json.loads(record.read_text(encoding="utf-8")),
            [PACK],
            where=tmp_path,
            log=log,
            pull=growing_log,
            kill=lambda: kills.append("killed"),
            sleep=lambda _s: (
                (tick(200.0), None)[1]
                if clock["now"] < 1400
                else (_ for _ in ()).throw(RuntimeError("stop the loop"))
            ),
            clock_now=lambda: clock["now"],
            now=gate.r1.stamp("2026-08-22T10:05:00+00:00"),
            poll_seconds=0,
        )
    assert kills == []

    # now the log stops too: the same loop kills on rung 5
    clock["now"] = 0.0
    verdict = gate.r1.watch(
        RECORD,
        json.loads(record.read_text(encoding="utf-8")),
        [PACK],
        where=tmp_path,
        log=log,
        pull=lambda: None,
        kill=lambda: {"deleted": True},
        sleep=lambda _s: tick(200.0),
        clock_now=lambda: clock["now"],
        now=gate.r1.stamp("2026-08-22T10:05:00+00:00"),
        poll_seconds=0,
    )
    assert verdict["verdict"] == "KILL"
    assert "rung 5" in verdict["cause"]
    assert verdict["idle_deadline_seconds"] == 600.0


def test_the_watch_returns_GO_at_the_smoke_and_not_at_79(tmp_path, monkeypatch):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.r1, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    log = tmp_path / "pod.log"
    log.write_text("boot\n", encoding="utf-8")
    out_rows(tmp_path / "pass2_signals_v1.jsonl", list(PACK["smoke"]["ids"]), 30.0)
    verdict = gate.r1.watch(
        RECORD,
        json.loads(record.read_text(encoding="utf-8")),
        [PACK],
        where=tmp_path,
        log=log,
        pull=lambda: None,
        kill=lambda: {"deleted": True},
        sleep=lambda _s: None,
        now=gate.r1.stamp("2026-08-22T10:05:00+00:00"),
        poll_seconds=0,
    )
    assert verdict["verdict"] == "GO"
    assert verdict["owed"] == 5


def test_rung_7_picks_its_arm_off_the_recorded_verdict(tmp_path, monkeypatch):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.r1, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    out = tmp_path / "pass2_signals_v1.jsonl"
    out.write_text(
        "".join(
            json.dumps(
                {
                    "id": one,
                    "rendering_sha256": BY_ID[one]["rendering_sha256"],
                    "reply": synthetic_reply(BY_ID[one]),
                    "balanced": True,
                    "seconds": 30.0,
                },
                ensure_ascii=False,
            )
            + "\n"
            for one in PACK["smoke"]["ids"]
        ),
        encoding="utf-8",
    )
    stop = gate.completeness(RECORD, json.loads(record.read_text(encoding="utf-8")), PACK, tmp_path)
    assert stop["arm"] == "STOP"
    assert stop["owed"] == 5
    assert stop["verdict"] == "GO"

    record.write_text(json.dumps(with_go(state_with_pod())), encoding="utf-8")
    go = gate.completeness(RECORD, json.loads(record.read_text(encoding="utf-8")), PACK, tmp_path)
    assert go["arm"] == "GO"
    assert go["owed"] == 79
    assert go["verdict"] == "RED"
    assert go["unanswered"] == 74


def synthetic_reply(item: dict, drop_one: bool = False, relabel: bool = False) -> str:
    rows = item["comments"]
    body = {
        "thread": {"channel": item["channel"], "post_id": item["post_id"]},
        "post_summary": "пост",
        "discussion_summary": "обговорення",
        "signals": [],
        "per_comment": [
            {
                "msg_id": row["msg_id"],
                "subject_type": (
                    "молочный_бренд"
                    if relabel and row["subject_type"] != "молочный_бренд"
                    else row["subject_type"]
                ),
                "subject_id": row["subject_id"],
                "stance": row["stance"],
                "aspects": [],
                "subject_doubt": False,
                "note": None,
            }
            for row in (rows[1:] if drop_one else rows)
        ],
        "noise": ([{"msg_id": rows[0]["msg_id"], "class": "плюс_спам"}] if drop_one else []),
    }
    return json.dumps(body, ensure_ascii=False)


def test_rung_7_counts_a_relabelling_as_its_own_refusal_cause(tmp_path, monkeypatch):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.r1, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    out = tmp_path / "pass2_signals_v1.jsonl"
    out.write_text(
        "".join(
            json.dumps(
                {
                    "id": one,
                    "rendering_sha256": BY_ID[one]["rendering_sha256"],
                    "reply": synthetic_reply(BY_ID[one], relabel=True),
                    "balanced": True,
                    "seconds": 30.0,
                },
                ensure_ascii=False,
            )
            + "\n"
            for one in PACK["smoke"]["ids"]
        ),
        encoding="utf-8",
    )
    verdict = gate.completeness(
        RECORD, json.loads(record.read_text(encoding="utf-8")), PACK, tmp_path
    )
    assert verdict["relabellings_refused"] >= 4
    assert any("RelabelError" in cause for cause in verdict["parse_refusals_by_cause"])
    # the TRANSPORT was clean, and rung 7 is the transport bar: it says GO and says loudly what it
    # is not saying. A relabelling is the ADR's line arriving as a measurement, and bars 1/2/3 are
    # where it lands — spending the readability budget on it would price a finding as a defect
    assert verdict["unreadable_replies"] == 0
    assert verdict["verdict"] == "GO"
    assert "RELABELLINGS" in verdict["next_step"]


def test_the_refusal_budget_is_derived_from_the_only_measurement_this_schema_has():
    """`int(0.01 × 79)` is ZERO — a transport bar a 17 %-refusing instrument cannot pass."""
    bar = RECORD["bars"]["completeness"]
    assert bar["parse_refusals_fraction"] == 0.174
    assert bar["arms"]["GO"]["parse_refusals_maximum"] == 14
    assert bar["arms"]["STOP"]["parse_refusals_maximum"] == 1, "ceil, so five units carry one"
    assert int(79 * 0.01) == 0
    v5b = json.loads((RESULTS / "reader_v5b_verdict.json").read_text(encoding="utf-8"))
    measured = v5b["replies"]["refused"] / (v5b["replies"]["refused"] + v5b["replies"]["parsed"])
    assert round(measured, 3) == 0.174


def test_the_bars_PROSE_carries_the_number_it_enforces():
    """[[two_values_for_one_input_get_quoted_kindly]] — the record said «≤ 1 % of N» in two places
    while enforcing 14 of 79, and the report pastes the rung-7 JSON."""
    blob = json.dumps(RECORD, ensure_ascii=False)
    assert "≤ 1 % of N" not in blob
    for rule in (
        RECORD["bars"]["completeness"]["rule"],
        next(one["rule"] for one in RECORD["kill_clock"] if int(one["rung"]) == 7),
    ):
        assert "17.4%" in rule
        assert "relabellings excluded" in rule or "relabellings excluded and counted" in rule


def test_the_prompt_carries_the_two_clauses_the_reader_line_PAID_for():
    """`READER_ASPECT_V5` IS F1(б) — «а є морозиво без цукру?» is availability and never taste —
    and `READER_NOT_A_SIGNAL_V3` IS F1(в), a two-word «дуже смачне» that still counts as похвала.
    F1 is all-or-nothing and its three signals are the only gold signals that state an aspect."""
    assert prompts.READER_ASPECT_V5 in pass2.PASS2_THREAD_PROMPT
    assert prompts.READER_NOT_A_SIGNAL_V3 in pass2.PASS2_THREAD_PROMPT
    assert prompts.READER_ASPECT_V3 not in pass2.PASS2_THREAD_PROMPT
    assert "@PRAISE@" not in pass2.PASS2_THREAD_PROMPT
    gold = json.loads((RESULTS / "reader_gold_w1_r2.json").read_text(encoding="utf-8"))
    stated = [one["id"] for case in gold["flagships"] for one in case["signals"] if one["aspect"]]
    assert stated == ["F1a", "F1b", "F1c", "F2a"], "aspect is compared where the gold states one"


def test_an_OMITTED_subject_type_is_not_a_relabelling():
    """`prompts._reader` permits a null there, and a null rewrote nothing. Refusing it would report
    the ADR's cardinal violation — exempt from the transport budget, so unbounded — for a row that
    failed to echo ([[an_abstention_is_an_answer]])."""
    said = json.loads(reply())
    said["per_comment"][0]["subject_type"] = None
    verdict = pass2.parse_pass2(json.dumps(said, ensure_ascii=False), unit=unit())
    assert verdict["per_comment_subject_omitted"] == [7]
    assert verdict["per_comment"][0]["subject_type"] is None, "the label is not invented either"
    assert verdict["accounting"]["kept"] == [7]
    # a WRONG word is still a relabelling
    said["per_comment"][0]["subject_type"] = "молочный_бренд"
    with pytest.raises(pass2.RelabelError):
        pass2.parse_pass2(json.dumps(said, ensure_ascii=False), unit=unit())


def test_the_record_carries_ONE_label_per_gold_evidence_row():
    """Built from the pack alone, a row outside the filter reported `null` while the same record's
    F5 expectation said `не_наш_рынок` in prose ([[two_values_for_one_input_get_quoted_kindly]])."""
    import build_pass1_window_r2_pack as r2builder

    answers, _table, _refusals = builder.filtered(r2builder.r1_pack())
    gold = json.loads((RESULTS / "reader_gold_w1_r2.json").read_text(encoding="utf-8"))
    rows = {one["id"]: one for one in RECORD["reachability"]["flagship_signals"]}
    for case in gold["flagships"]:
        thread = f"{case['channel']}:{case['post_id']}"
        for signal in case["signals"]:
            said = rows[signal["id"]]["pass_1_labels_of_the_cited_rows"]
            for msg_id in signal["evidence"]:
                truth = answers[f"{thread}#{msg_id}"]["subject_type"]
                assert said[str(msg_id)] == truth, f"{signal['id']}#{msg_id}"
    f5 = rows["F5a"]
    assert f5["pass_1_labels_of_the_cited_rows"]["579457"] == "не_наш_рынок"
    assert f5["evidence_rows_outside_the_filter"] == [579457]
    assert f5["reachable"] is True
    assert "не_наш_рынок" in RECORD["bars"]["1_flagships"]["expectation"]["F5"]["why"]
    assert None not in f5["pass_1_labels_of_the_cited_rows"].values()


def test_a_vocabulary_SYNONYM_is_not_a_relabelling():
    """«категория» and «категория_личное» are the two words two authorities disagree about, and the
    project's own scorer folds them. Refusing one as the ADR's cardinal violation would report an
    architecture breach on three of the five flagship cases."""
    import score_reader_probe_b as readerscore

    assert pass2.SUBJECT_SYNONYMS == readerscore.COLLAPSE
    said = json.loads(reply())
    for row in said["per_comment"]:
        row["subject_type"] = "категория"
    said["signals"][0]["subject_type"] = "категория"
    verdict = pass2.parse_pass2(json.dumps(said, ensure_ascii=False), unit=unit())
    assert verdict["vocabulary_synonyms_used"] == ["категория"]
    assert verdict["signals"][0]["subject_type"] == "категория", "the word is not rewritten"
    # and the collapse folds ONE pair and no other: сеть_ритейлер is still a relabelling
    said["signals"][0]["subject_type"] = "сеть_ритейлер"
    with pytest.raises(pass2.RelabelError):
        pass2.parse_pass2(json.dumps(said, ensure_ascii=False), unit=unit())


def test_an_unreadable_reply_does_spend_the_budget(tmp_path, monkeypatch):
    """The negative control: the budget still exists and still bites."""
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.r1, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    (tmp_path / "pass2_signals_v1.jsonl").write_text(
        "".join(
            json.dumps(
                {
                    "id": one,
                    "rendering_sha256": BY_ID[one]["rendering_sha256"],
                    "reply": "not json at all",
                    "balanced": False,
                    "seconds": 30.0,
                },
                ensure_ascii=False,
            )
            + "\n"
            for one in PACK["smoke"]["ids"]
        ),
        encoding="utf-8",
    )
    verdict = gate.completeness(
        RECORD, json.loads(record.read_text(encoding="utf-8")), PACK, tmp_path
    )
    assert verdict["unreadable_replies"] == 5
    assert verdict["unreadable_replies_maximum"] == 1
    assert verdict["relabellings_refused"] == 0
    assert verdict["verdict"] == "RED"


def test_the_go_token_is_written_only_after_the_verdict_is_recorded(tmp_path, monkeypatch):
    record = tmp_path / "run.json"
    token = tmp_path / "go.json"
    monkeypatch.setattr(gate.r1, "RECORD", record)
    monkeypatch.setattr(gate, "GO_TOKEN", token)
    monkeypatch.setattr(gate.r1, "registration", lambda: RECORD)
    record.write_text(json.dumps(state_created_now()), encoding="utf-8")
    out_rows(tmp_path / "pass2_signals_v1.jsonl", list(PACK["smoke"]["ids"]), 300.0)
    assert gate.run_go_no_go(["--go-no-go", "--outdir", str(tmp_path)]) == gate.KILL
    state = json.loads(record.read_text(encoding="utf-8"))
    assert state["gates"][-1]["kind"] == gate.GO_KIND
    assert state["gates"][-1]["verdict"] == "STOP"
    assert not token.exists()

    out_rows(tmp_path / "pass2_signals_v1.jsonl", list(PACK["smoke"]["ids"]), 20.0)
    assert gate.run_go_no_go(["--go-no-go", "--outdir", str(tmp_path)]) == gate.GO
    assert json.loads(token.read_text(encoding="utf-8"))["verdict"] == "GO"


def test_a_stale_GO_token_beside_a_STOP_verdict_is_refused(tmp_path, monkeypatch):
    record = tmp_path / "run.json"
    token = tmp_path / "go.json"
    token.write_text('{"verdict": "GO"}\n', encoding="utf-8")
    monkeypatch.setattr(gate.r1, "RECORD", record)
    monkeypatch.setattr(gate, "GO_TOKEN", token)
    monkeypatch.setattr(gate.r1, "registration", lambda: RECORD)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    out_rows(tmp_path / "pass2_signals_v1.jsonl", list(PACK["smoke"]["ids"]), 300.0)
    with pytest.raises(SystemExit, match="exists and this verdict is"):
        gate.run_go_no_go(["--go-no-go", "--outdir", str(tmp_path)])


def test_EVERY_gate_command_runs_end_to_end(tmp_path, monkeypatch, capsys):
    """The COMMANDS, not the functions behind them.

    `gate_pass1_window.main` hard-subscripts `pack["population"]["payable_comments"]` and the same
    key in the record before every rung that reads a pack, and that file is pinned by a sealed
    record. Driving `watch`/`completeness`/`projection` directly walks straight past that line: the
    five-lens review found the KeyError it raises, and it would have landed on `--watch`, on a pod
    that was already billing, with nothing watching it ([[a_proof_can_cover_the_sibling_branch]],
    [[drive_the_consumer_not_only_the_producer]]).
    """
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.r1, "RECORD", record)
    monkeypatch.setattr(gate.r1, "registration", lambda: RECORD)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    out_rows(tmp_path / "pass2_signals_v1.jsonl", list(PACK["smoke"]["ids"]), 30.0)
    (tmp_path / "pass2_signals_launched_at").write_text(
        "2026-08-22T10:04:00+00:00\n", encoding="utf-8"
    )
    now = gate.r1.stamp("2026-08-22T10:20:00+00:00")
    common = ["--outdir", str(tmp_path)]
    for argv in (
        ["--clock", *common],
        ["--gate0", "--ssh-ok", *common],
        ["--boot", *common],
        ["--projection", *common],
        ["--completeness", *common],
    ):
        code = gate.main(argv, now)
        assert code in (gate.GO, gate.KILL, gate.WAIT), argv
        assert "Traceback" not in capsys.readouterr().out
    # and --close, which ends the pod
    assert (
        gate.main(
            ["--close", "--deleted-at", "2026-08-22T10:30:00+00:00", "--outcome", "test"], now
        )
        == gate.GO
    )
    state = json.loads(record.read_text(encoding="utf-8"))
    assert [one["kind"] for one in state["gates"]][-1] == "close"
    assert state["pods"][0]["billed_seconds"] == 1800.0


def test_the_PRICE_command_runs_and_its_backstop_guard_bites_both_ways(
    tmp_path, monkeypatch, capsys
):
    """`--price` is the command that runs while a pod is already billing, so a crash in it is the
    most expensive kind there is. Driven at $0: an accepted window, an over-long one, and a price
    above the ceiling."""
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.r1, "RECORD", record)
    monkeypatch.setattr(gate.r1, "registration", lambda: RECORD)
    monkeypatch.setattr(gate, "OUT_FILE", tmp_path / "pass2_signals_v1.jsonl")
    created = "2026-08-22T10:00:00+00:00"
    stop = RECORD["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"]
    good = (gate.r1.stamp(created) + __import__("datetime").timedelta(seconds=stop)).isoformat(
        timespec="seconds"
    )
    now = gate.r1.stamp("2026-08-22T10:01:00+00:00")

    def price(usd, terminate):
        record.write_text(json.dumps({"pods": [], "gates": []}), encoding="utf-8")
        return gate.main(
            [
                "--price",
                "--pod-id",
                "p1",
                "--created-at",
                created,
                "--usd-per-hour",
                str(usd),
                "--card",
                "NVIDIA GeForce RTX 4090",
                "--terminate-after",
                terminate,
                "--outdir",
                str(tmp_path),
            ],
            now,
        )

    assert price(0.74, good) == gate.GO
    state = json.loads(record.read_text(encoding="utf-8"))
    assert state["gates"][-1]["rung"] == 1
    assert state["gates"][-1]["backstop"]["window_seconds"] == stop
    assert state["gates"][-1]["recovery"]["fits_the_recovery_clause"] is True
    capsys.readouterr()

    # a window longer than rung 6 allows, beyond the registered tolerance
    far = (gate.r1.stamp(created) + __import__("datetime").timedelta(seconds=stop + 600)).isoformat(
        timespec="seconds"
    )
    with pytest.raises(SystemExit, match="beyond the"):
        price(0.74, far)
    state = json.loads(record.read_text(encoding="utf-8"))
    assert state["gates"][-1]["verdict"] == "KILL"
    assert "IS LIVE AND BILLING" in state["gates"][-1]["next_step"], "the pod is already real"

    # a price over the registered ceiling
    assert price(0.95, good) == gate.KILL


def test_the_pack_and_the_record_agree_on_the_key_the_pinned_gate_compares():
    assert PACK["population"]["payable_comments"] == RECORD["population"]["payable_comments"] == 79
    source = (REPO_ROOT / "scripts" / "gate_pass1_window.py").read_text(encoding="utf-8")
    assert 'pack["population"]["payable_comments"]' in source


def test_a_half_copied_go_token_is_KEEP_WAITING_and_never_a_STOP(tmp_path):
    """scp writes into place over seconds and a poll can land in the middle of it."""
    token = tmp_path / "pass2_go"
    for body in ('{"verdict": "G', "", "not json", '{"verdict": "MAYBE"}', "[]"):
        token.write_text(body, encoding="utf-8")
        assert runner.read_token(token) is None, body
    token.write_text('{"verdict": "GO"}', encoding="utf-8")
    assert runner.read_token(token)["verdict"] == "GO"
    token.write_text('{"verdict": "STOP"}', encoding="utf-8")
    assert runner.read_token(token)["verdict"] == "STOP"


def test_the_wait_keeps_polling_through_a_truncated_token(tmp_path, capsys):
    token = tmp_path / "pass2_go"
    token.write_text('{"verdict": "G', encoding="utf-8")
    ticks = {"n": 0}

    def sleep(_seconds):
        ticks["n"] += 1
        if ticks["n"] == 2:
            token.write_text('{"verdict": "GO"}', encoding="utf-8")

    assert runner.wait_for_go(token, 600.0, 0.0, sleep=sleep)["verdict"] == "GO"
    assert capsys.readouterr().out.count("WAIT for the go") == 2


def test_the_recovery_clause_refuses_a_pod_after_the_first_reply(tmp_path, monkeypatch):
    """«ONE re-creation, ONLY for a death BEFORE the smoke's first reply» — enforced, not written.

    After a rung-4 or rung-5 KILL the seconds still fit, so the shipped pod-and-seconds arithmetic
    reports GO on a create the record forbids ([[a_claim_no_number_can_check]]).
    """
    out = tmp_path / "pass2_signals_v1.jsonl"
    monkeypatch.setattr(gate, "OUT_FILE", out)
    dead = {
        **state_with_pod()["pods"][0],
        "deleted_at": "2026-08-22T10:20:00+00:00",
        "billed_seconds": 1200.0,
        "billed_usd": 0.2467,
    }
    state = {"pods": [dead], "gates": []}
    # a death BEFORE the first reply: one re-creation, and the arithmetic still fits
    out.write_text("", encoding="utf-8")
    clean = gate.pre_create(RECORD, state)
    assert clean["replies_already_bought"] == 0
    assert clean["fits_the_recovery_clause"] is True
    assert clean["verdict"] == "GO"
    # the same seconds, with three replies bought: the clause refuses what the arithmetic allows
    out_rows(out, list(PACK["smoke"]["ids"])[:3], 30.0)
    after = gate.pre_create(RECORD, state)
    assert after["replies_already_bought"] == 3
    assert after["fits_the_hard_stop"] is True, "the SECONDS still fit — that is the whole point"
    assert after["fits_the_cap"] is True
    assert after["fits_the_recovery_clause"] is False
    assert after["verdict"] == "KILL"
    assert "new registration" in after["next_step"]
    # and the first create of all is untouched: no pod, no reply
    assert gate.pre_create(RECORD, {"pods": [], "gates": []})["verdict"] == "GO"


def test_a_second_go_no_go_is_REFUSED_once_a_GO_is_recorded(tmp_path, monkeypatch):
    """`go_recorded` reads the LAST verdict, so a second STOP would de-authorise a live run."""
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.r1, "RECORD", record)
    monkeypatch.setattr(gate, "GO_TOKEN", tmp_path / "go.json")
    monkeypatch.setattr(gate.r1, "registration", lambda: RECORD)
    record.write_text(json.dumps(with_go(state_with_pod())), encoding="utf-8")
    out_rows(tmp_path / "pass2_signals_v1.jsonl", list(PACK["smoke"]["ids"]), 300.0)
    with pytest.raises(SystemExit, match="already recorded a GO"):
        gate.run_go_no_go(["--go-no-go", "--outdir", str(tmp_path)])
    assert gate.legs_of(PACK)[0]["units"] == 79, "the authorisation is untouched"


def test_the_gate_refuses_to_load_if_r1s_gate_has_moved(monkeypatch):
    monkeypatch.setattr(gate.summary, "sha256_of", lambda _p: "0" * 64)
    with pytest.raises(SystemExit, match="a different instrument answering the same question"):
        gate._load()


def test_loading_r1s_gate_twice_does_not_move_r1s_own_paths():
    import gate_pass1_window as r1real

    assert r1real.PREREG.name == "prereg_pass1_window.json"
    assert gate.r1.PREREG.name == "prereg_pass2_signals.json"
    assert gate.r1 is not r1real


# --- the bars, driven on synthetic replies -------------------------------------------------------


def score(verdicts: dict) -> dict:
    import score_reader_probe_b as readerscore

    record = json.loads((RESULTS / "reader_gold_w1_r2.json").read_text(encoding="utf-8"))
    return readerscore.flagships(record, verdicts, set(verdicts), collapsed=True)


def f1_signals(minus: int | None = None) -> list[dict]:
    rows = [
        {
            "signal_type": "жалоба",
            "subject_type": "сеть_ритейлер",
            "subject_id": "varus",
            "aspect": "quality",
            "stance": "negative",
            "reading": "x",
            "evidence": [21626],
            "quote": "q",
        },
        {
            "signal_type": "спрос",
            "subject_type": "категория_личное",
            "subject_id": "морозиво без цукру",
            "aspect": "availability",
            "stance": None,
            "reading": "x",
            "evidence": [21599, 21601],
            "quote": "q",
        },
        {
            "signal_type": "похвала",
            "subject_type": "категория_личное",
            "subject_id": None,
            "aspect": "taste",
            "stance": "positive",
            "reading": "x",
            "evidence": [21629],
            "quote": "q",
        },
    ]
    return [one for index, one in enumerate(rows) if index != minus]


def test_bar_1_finds_F1s_three_signals_and_goes_RED_one_short():
    whole = score({"@VARUS_channel:10613": {"signals": f1_signals(), "entities": []}})
    assert [one["answered"] for one in whole["per_case"] if one["id"] == "F1"] == [True]
    for missing in (0, 1, 2):
        short = score(
            {"@VARUS_channel:10613": {"signals": f1_signals(minus=missing), "entities": []}}
        )
        assert [one["answered"] for one in short["per_case"] if one["id"] == "F1"] == [False]
        assert short["passed"] is False


def test_bar_3_goes_RED_when_the_noise_thread_10366_carries_a_signal():
    import score_reader_probe_b as readerscore

    gold = json.loads((RESULTS / "reader_gold_w1_r2.json").read_text(encoding="utf-8"))
    name = "@VARUS_channel:10366"
    clean = readerscore.noise(gold, {name: {"signals": [], "entities": []}}, {name}, ["N2"])
    assert clean["passed"] is True
    dirty = readerscore.noise(
        gold,
        {name: {"signals": [{"signal_type": "жалоба", "evidence": [20916]}], "entities": []}},
        {name},
        ["N2"],
    )
    assert dirty["passed"] is False
    assert dirty["signals"] == 1


def test_F2_cannot_be_taken_without_a_relabelling():
    """The registered expectation, DRIVEN: the only reply that answers F2 is one the parser refuses."""
    item = BY_ID["@matusi_ukr:22303"]
    labels = {row["msg_id"]: row["subject_type"] for row in item["comments"]}
    assert labels[580124] == "сеть_ритейлер"
    body = {
        "thread": {"channel": item["channel"], "post_id": item["post_id"]},
        "post_summary": "пост",
        "discussion_summary": "обговорення",
        "signals": [
            {
                "signal_type": "жалоба",
                "subject_type": "молочный_бренд",
                "subject_id": "lasunka",
                "aspect": "availability",
                "stance": "negative",
                "reading": "x",
                "evidence": [580124],
                "quote": "q",
            }
        ],
        "per_comment": [
            {
                "msg_id": row["msg_id"],
                "subject_type": row["subject_type"],
                "subject_id": row["subject_id"],
                "stance": row["stance"],
                "aspects": [],
                "subject_doubt": False,
                "note": None,
            }
            for row in item["comments"]
        ],
        "noise": [],
    }
    with pytest.raises(pass2.RelabelError):
        pass2.parse_pass2(json.dumps(body, ensure_ascii=False), unit=item)


def test_F5_is_reachable_from_the_one_evidence_row_inside_the_filter():
    item = BY_ID["@matusi_ukr:22272"]
    inside = {row["msg_id"] for row in item["comments"]}
    assert 579379 in inside and 579457 not in inside
    scored = score(
        {
            "@matusi_ukr:22272": {
                "signals": [
                    {
                        "signal_type": "привычка",
                        "subject_type": "категория_личное",
                        "subject_id": "baby-food",
                        "aspect": None,
                        "stance": None,
                        "reading": "x",
                        "evidence": [579379],
                        "quote": "q",
                    }
                ],
                "entities": [],
            }
        }
    )
    assert [one["answered"] for one in scored["per_case"] if one["id"] == "F5"] == [True]


def test_under_a_STOP_bar_3_is_UNSCORED_and_not_a_false_GREEN():
    """`scorer.reader_noise_count({})` returns `signals: 0`, so a bar that did not ask whether its
    cases were READ would report GREEN over zero threads ([[a_checker_whose_failure_is_silence]])."""
    gold = json.loads((RESULTS / "reader_gold_w1_r2.json").read_text(encoding="utf-8"))
    smoke = list(PACK["smoke"]["ids"])
    verdicts = {
        one: {"entities": BY_ID[one]["entities"], "signals": [], "per_comment": [], "noise": []}
        for one in smoke
    }
    bars = scoring.bar_states(RECORD, gold, verdicts, set(smoke))
    assert bars["3_noise"]["verdict"] == "UNSCORED"
    assert bars["3_noise"]["passed"] is None
    assert bars["3_noise"]["result"] is None
    assert bars["3_noise"]["threads_not_read"] == ["@VARUS_channel:10366"]
    # and the same defect the other way round: bar 2 would read 0 of 4 against a registered 3 of 4
    assert bars["2_entity_cases"]["verdict"] == "UNSCORED"
    assert bars["2_entity_cases"]["passed"] is None
    # bar 1 survives a STOP, because the five F threads ARE the smoke
    assert bars["1_flagships"]["verdict"] == "SCORED"
    assert bars["1_flagships"]["passed"] is False


def test_over_the_whole_population_every_bar_is_SCORED():
    gold = json.loads((RESULTS / "reader_gold_w1_r2.json").read_text(encoding="utf-8"))
    verdicts = {
        one["id"]: {
            "entities": one["entities"],
            "signals": [],
            "per_comment": [],
            "noise": [],
        }
        for one in ITEMS
    }
    bars = scoring.bar_states(RECORD, gold, verdicts, set(verdicts))
    assert [bars[name]["verdict"] for name in bars] == ["SCORED", "SCORED", "SCORED"]
    assert bars["2_entity_cases"]["result"]["cases_answered"] == 3
    assert bars["2_entity_cases"]["agrees_with_the_registration"] is True
    assert bars["3_noise"]["passed"] is True


def echo_reply(item: dict, relabel: str | None = None, doubt=False) -> str:
    """A reply that repeats every pass-1 label — the shape the parser is supposed to accept."""
    return json.dumps(
        {
            "thread": {"channel": item["channel"], "post_id": item["post_id"]},
            "post_summary": "пост",
            "discussion_summary": "обговорення",
            "signals": [],
            "per_comment": [
                {
                    "msg_id": row["msg_id"],
                    "subject_type": (
                        relabel
                        if relabel and index == 0 and row["subject_type"] != relabel
                        else row["subject_type"]
                    ),
                    "subject_id": row["subject_id"],
                    "stance": row["stance"],
                    "aspects": [],
                    "subject_doubt": doubt,
                    "note": None,
                }
                for index, row in enumerate(item["comments"])
            ],
            "noise": [],
        },
        ensure_ascii=False,
    )


def test_a_REFUSED_reply_is_not_an_unread_thread_and_bar_3_says_which():
    """A relabelling on N2 used to delete bar 3 with «the go/no-go stopped the run» — which is
    false about a unit the pod answered ([[the_empty_class_eats_the_parse_failures]])."""
    gold = json.loads((RESULTS / "reader_gold_w1_r2.json").read_text(encoding="utf-8"))
    rows = [
        {
            "id": one["id"],
            "rendering_sha256": one["rendering_sha256"],
            "reply": echo_reply(
                one, relabel="категория_личное" if one["id"] == "@VARUS_channel:10366" else None
            ),
            "balanced": True,
            "seconds": 30.0,
        }
        for one in ITEMS
    ]
    parsed, refused = scoring.answers(PACK, rows)
    assert len(refused) == 1 and "RelabelError" in refused[0]["cause"]
    bars = scoring.bar_states(
        RECORD,
        gold,
        parsed,
        set(parsed),
        attempted={one["id"] for one in rows},
        refused_threads={one["id"]: one["cause"] for one in refused},
    )
    three = bars["3_noise"]
    assert three["verdict"] == "UNSCORED"
    assert three["threads_answered_and_refused"] == ["@VARUS_channel:10366"]
    assert "ANSWERED these threads and the parser refused" in three["unscored_reason"]
    assert "go/no-go stopped the run" not in three["unscored_reason"]
    assert three["threads_not_read"] == [], "the thread WAS read"
    # the bars whose cases parsed are untouched
    assert bars["1_flagships"]["verdict"] == "SCORED"
    assert bars["2_entity_cases"]["verdict"] == "SCORED"


def test_subject_doubt_is_REPORT_ONLY_and_cannot_refuse_a_thread():
    """`prompts._flag` raises on 0, on null and on a Ukrainian yes. A field the contract says
    changes nothing downstream may not throw away a thread's signals."""
    item = BY_ID["@VARUS_channel:10613"]
    for value in (0, None, "ні", "так", 1.5, []):
        verdict = pass2.parse_pass2(echo_reply(item, doubt=value), unit=item)
        assert len(verdict["per_comment"]) == len(item["comments"])
        assert verdict["per_comment"][0]["subject_doubt"] is None
        assert verdict["subject_doubt_unreadable"] == sorted(
            row["msg_id"] for row in item["comments"]
        )
    # and a boolean still reads as one, both ways
    assert (
        pass2.parse_pass2(echo_reply(item, doubt=True), unit=item)["per_comment"][0][
            "subject_doubt"
        ]
        is True
    )
    assert (
        pass2.parse_pass2(echo_reply(item, doubt=False), unit=item)["subject_doubt_unreadable"]
        == []
    )


def test_no_request_carries_a_subject_word_the_prompt_does_not_define():
    """The entity block used to render pass 1's four-word taxonomy above comments carrying one of
    three — so F2's own request offered `Ласунка → молочный_бренд` over a comment pass 1 labelled
    `категория_личное`, and the natural signal was a RelabelError the request invited."""
    for item in ITEMS:
        block = pass2.entity_block(item["entities"])
        for word in prompts.READER_ENTITY_TYPES:
            assert word not in block, f"{item['id']} renders {word}"
    # the type is still in the BLOCK, which is what bar 2 is scored on
    f2 = BY_ID["@matusi_ukr:22303"]
    assert any(one["subject_type"] == "молочный_бренд" for one in f2["entities"])
    assert "Ласунка" in pass2.entity_block(f2["entities"])


def test_the_row_weighted_reading_is_computed_beside_the_charge_and_gates_nothing(
    tmp_path, monkeypatch
):
    """The smoke carries 6.0 filtered rows a thread against the population's 3.56."""
    verdict = drive_go_no_go(tmp_path, monkeypatch, [40.0, 20.0, 35.0, 45.0, 45.0])
    beside = verdict["the_row_weighted_reading"]
    assert beside["smoke_rows_per_thread"] == 6.0
    assert beside["remaining_rows_per_thread"] < beside["smoke_rows_per_thread"]
    assert beside["seconds_per_filtered_row"] > 0
    assert beside["predicted_mean_seconds_per_call"] < verdict["charged_full_seconds_per_call"]
    assert verdict["verdict"] in ("GO", "STOP")
    assert beside["would_have_said"] in ("GO", "STOP")
    assert "REPORT-ONLY" in beside["and_it_does_not_gate"]


def test_the_row_weighted_reading_does_not_divide_by_zero_on_a_flat_smoke(tmp_path, monkeypatch):
    leg = json.loads(json.dumps(PACK["legs"][0]))
    for one in leg["items"][:5]:
        one["comments"] = one["comments"][:2]
    rows = {one: {"seconds": 30.0} for one in PACK["smoke"]["ids"]}
    beside = gate.row_weighted(leg, list(PACK["smoke"]["ids"]), rows, overhead=1300.0)
    assert beside["degenerate"] is True
    assert beside["seconds_per_filtered_row"] == 0.0
    assert beside["predicted_mean_seconds_per_call"] == 30.0


# --- the runner ----------------------------------------------------------------------------------


def test_the_runner_swaps_exactly_the_two_shipped_names_and_puts_them_back():
    import reader_v5_pod_runner as shipped

    before = {name: getattr(shipped, name) for name in runner.SWAPPED}
    with runner.as_pass2():
        assert shipped.render is runner.render
        assert shipped.check_instrument is runner.check_instrument
    assert {name: getattr(shipped, name) for name in runner.SWAPPED} == before


def test_a_task_that_is_not_pass_2s_goes_to_the_shipped_render():
    """`ReaderClient.__init__` probes the chat template with a READER task before it builds."""
    probe = {"channel": "@probe", "post_id": 1, "post": "проба", "comments": []}
    content = runner.render(prompts, probe, prompts.READER_TASK_V2)
    assert content.startswith(prompts.PROMPTS[prompts.READER_TASK_V2][:40])


def test_the_runner_renders_a_pass_2_item_to_the_pinned_sha():
    import build_pass1_fewshot_packs as fewshot

    item = ITEMS[0]
    content = runner.render(prompts, item, pass2.PASS2_TASK_V1)
    assert fewshot.sha_text(content) == item["rendering_sha256"]


def test_the_handshake_refuses_a_moved_pass_2_module(tmp_path):
    pod = {"instruments": {**PACK["instruments"]}}
    pod["instruments"] = json.loads(json.dumps(PACK["instruments"]))
    pod["instruments"]["module"]["sha256"] = "0" * 64
    with pytest.raises(SystemExit, match="src/market_pulse/pass2.py hashes"):
        runner.check_instrument(pod, REPO_ROOT, prompts)


def test_the_handshake_refuses_a_moved_prompt(tmp_path):
    pod = json.loads(json.dumps(PACK))
    pod["instruments"]["prompt_sha256"][pass2.PASS2_TASK_V1] = "0" * 64
    with pytest.raises(SystemExit, match="not the registered instrument"):
        runner.check_instrument(pod, REPO_ROOT, prompts)


def test_the_smoke_leg_the_runner_takes_is_the_packs_own_prefix():
    leg = PACK["legs"][0]
    assert [one["id"] for one in runner.smoke_leg(PACK, leg)] == list(PACK["smoke"]["ids"])
    poisoned = json.loads(json.dumps(PACK))
    poisoned["legs"][0]["items"] = list(reversed(poisoned["legs"][0]["items"]))
    with pytest.raises(SystemExit, match="smoke leg is a PREFIX"):
        runner.smoke_leg(poisoned, poisoned["legs"][0])


def test_the_go_wait_polls_prints_and_returns_the_verdict(tmp_path, capsys):
    token = tmp_path / "pass2_go"
    ticks = {"n": 0}

    def sleep(_seconds):
        ticks["n"] += 1
        if ticks["n"] == 3:
            token.write_text('{"verdict": "GO"}', encoding="utf-8")

    gateway = runner.wait_for_go(token, 600.0, 0.0, sleep=sleep)
    assert gateway["verdict"] == "GO"
    printed = capsys.readouterr().out
    assert printed.count("WAIT for the go") == 3
    assert "GO token read" in printed


def test_the_go_wait_gives_up_at_its_deadline_and_says_so(tmp_path, capsys):
    token = tmp_path / "pass2_go"
    clock = {"now": 0.0}
    import time as _time

    real = _time.monotonic
    try:
        _time.monotonic = lambda: clock["now"]
        gateway = runner.wait_for_go(
            token, 30.0, 0.0, sleep=lambda _s: clock.__setitem__("now", clock["now"] + 20.0)
        )
    finally:
        _time.monotonic = real
    assert gateway["verdict"] == "NO-TOKEN"
    assert "WAIT gave up" in capsys.readouterr().out


def test_a_STOP_token_answers_nothing_beyond_the_smoke(tmp_path, monkeypatch, capsys):
    """The whole run, driven on a fake transport: five units, a STOP, and no sixth call."""
    asked = []

    class FakeClient:
        def read(self, task, items):
            asked.append(items[0]["id"])
            return [
                {
                    "content": synthetic_reply(BY_ID[items[0]["id"]]),
                    "finish_reason": "stop",
                    "usage": {"completion_tokens": 100},
                }
            ]

    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps(PACK, ensure_ascii=False), encoding="utf-8")
    token = tmp_path / "go"
    token.write_text('{"verdict": "STOP"}', encoding="utf-8")
    code = runner.main(
        [
            "--pack",
            str(pack),
            "--outdir",
            str(tmp_path),
            "--repo",
            str(REPO_ROOT),
            "--go",
            str(token),
            "--go-deadline",
            "600",
        ],
        loader=lambda _pack, _repo: FakeClient(),
    )
    assert code == 0
    assert asked == list(PACK["smoke"]["ids"])
    rows = (tmp_path / "pass2_signals_v1.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(rows) == 5
    assert "no unit beyond the smoke" in capsys.readouterr().out


def test_a_GO_token_releases_the_remaining_units_and_never_re_asks_the_smoke(tmp_path):
    asked = []

    class FakeClient:
        def read(self, task, items):
            asked.append(items[0]["id"])
            return [
                {
                    "content": synthetic_reply(BY_ID[items[0]["id"]]),
                    "finish_reason": "stop",
                    "usage": {"completion_tokens": 100},
                }
            ]

    built = []

    def loader(_pack, _repo):
        built.append(1)
        return FakeClient()

    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps(PACK, ensure_ascii=False), encoding="utf-8")
    token = tmp_path / "go"
    token.write_text('{"verdict": "GO"}', encoding="utf-8")
    assert (
        runner.main(
            [
                "--pack",
                str(pack),
                "--outdir",
                str(tmp_path),
                "--repo",
                str(REPO_ROOT),
                "--go",
                str(token),
                "--go-deadline",
                "600",
            ],
            loader=loader,
        )
        == 0
    )
    assert len(asked) == 79
    assert asked[:5] == list(PACK["smoke"]["ids"])
    assert len(set(asked)) == 79
    assert built == [1], "the model is loaded ONCE — the go/no-go's whole cost argument"


def test_every_reply_the_fake_run_wrote_parses_and_scores(tmp_path):
    """The consumer is driven too, not only the producer ([[drive_the_consumer_not_only_the_producer]])."""
    rows = []
    for index, item in enumerate(ITEMS):
        rows.append(
            {
                "index": index,
                "id": item["id"],
                "thread": item["thread"],
                "rendering_sha256": item["rendering_sha256"],
                "reply": synthetic_reply(item, drop_one=True),
                "balanced": True,
                "emitted_chars": 500,
                "finish_reason": "stop",
                "usage": {"completion_tokens": 200},
                "seconds": 30.0,
                "elapsed_since_start": 300.0 + index,
            }
        )
    out = tmp_path / "pass2_signals_v1.jsonl"
    out.write_text(
        "".join(json.dumps(one, ensure_ascii=False) + "\n" for one in rows), encoding="utf-8"
    )
    parsed, refused = scoring.answers(PACK, rows)
    assert refused == []
    assert len(parsed) == 79
    drops = scoring.drop_table(PACK, parsed)
    assert drops["dropped_rows"] == 79
    assert drops["rows_offered"] == 281
    doubt = scoring.doubt_table(PACK, parsed)
    assert doubt["kept_rows"] == 281 - 79
    assert doubt["doubted_rows"] == 0
    acct = scoring.accounting(parsed)
    assert acct["rows_in_neither_list"] == []
    assert acct["rows_in_both_lists"] == []


# --- the runbook -----------------------------------------------------------------------------


def test_the_runbook_launches_the_pass_2_runner_with_the_pack_and_the_go():
    assert "scripts/pass2_pod_runner.py" in RUNBOOK
    assert "--pack /workspace/repo/results/pass2_pack.json" in RUNBOOK
    assert "--go /workspace/run/pass2_go --go-deadline 600" in RUNBOOK


def test_the_runbooks_go_deadline_is_the_records_own_rung_S_deadline():
    """The literal in a command line, held to the field it came out of."""
    wanted = next(one["deadline_seconds"] for one in RECORD["kill_clock"] if int(one["rung"]) == 8)
    assert f"--go-deadline {int(wanted)}" in RUNBOOK
    assert wanted == next(
        one["deadline_seconds"] for one in RECORD["kill_clock"] if int(one["rung"]) == 5
    )


def test_the_runbook_writes_the_launch_stamp_under_the_name_the_gate_copies():
    """The r2 defect, watched: `pull()` copies `<remote-dir>/launched_at`, not the local name."""
    assert "> /workspace/run/launched_at;" in RUNBOOK
    assert gate.LAUNCH_STAMP == "pass2_signals_launched_at"
    assert gate.LAUNCH_STAMP not in RUNBOOK.split("## 5")[0].split("date -u")[1].split(";")[0]
    source = (REPO_ROOT / "scripts" / "gate_pass1_window.py").read_text(encoding="utf-8")
    assert 'f"{args.remote_dir}/launched_at"' in source


def test_the_runbook_scps_every_file_the_pod_runner_needs():
    for name in (
        "scripts/pass2_pod_runner.py",
        "scripts/pass1_fewshot_pod_runner.py",
        "scripts/reader_v5_pod_runner.py",
        "scripts/reader_v4_pod_runner.py",
    ):
        assert name in RUNBOOK


def test_the_runbook_ships_the_token_only_after_the_go_no_go():
    order = RUNBOOK.index("--go-no-go"), RUNBOOK.index("results/pass2_signals_go.json root@")
    assert order[0] < order[1]
    assert "On STOP, do nothing to the pod except step 5" in RUNBOOK


def test_the_runbook_names_the_guard_step_and_the_cap_the_record_registers():
    assert RECORD["money"]["guard"]["step"] == "pass2-signals"
    assert RECORD["money"]["guard"]["step_cap_usd"] == 1.50
    assert "--step pass2-signals --step-cap 1.50" in RUNBOOK


def test_the_runbook_forbids_what_the_contract_forbids():
    for line in (
        "No raw unfiltered comment in any request",
        "No relabelling accepted",
        "No bar on the fourteen",
        "No unit beyond the five without rung S′'s RECORDED GO",
    ):
        assert line in RUNBOOK
