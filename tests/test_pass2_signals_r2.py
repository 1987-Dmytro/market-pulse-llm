"""pass2-signals r2 D0′ — the module, the pack, the seed, the record, the gate, the runner, the runbook.

Every test here runs at $0 on a fake transport. The rungs that cost money are DRIVEN — a liveness
rung nobody ever saw fire is a rung nobody has ([[guard_selftest_negative_control]]).

Two of them are TRIPWIRES rather than tests of r2: `test_r1s_parser_still_REFUSES_F2` and
`test_r1s_pack_still_rebuilds_byte_for_byte` fail the moment r2's siblings start reaching into r1's
sealed artifacts. r1's record says `parse_refusals 1`, and that sentence has to stay true.
"""

import datetime
import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass2_r2_pack as builder  # noqa: E402
import gate_pass2_signals_r2 as gate  # noqa: E402
import pass2_r2_pod_runner as runner  # noqa: E402
import score_pass2_signals_r2 as scoring  # noqa: E402
import write_pass2_prereg_r2 as producer  # noqa: E402

from market_pulse import pass2, pass2_r2, prompts  # noqa: E402

RESULTS = REPO_ROOT / "results"
PACK = json.loads((RESULTS / "pass2_r2_pack.json").read_text(encoding="utf-8"))
RECORD = json.loads((RESULTS / "prereg_pass2_signals_r2.json").read_text(encoding="utf-8"))
R1_PACK = json.loads((RESULTS / "pass2_pack.json").read_text(encoding="utf-8"))
R1_RECORD = json.loads((RESULTS / "prereg_pass2_signals.json").read_text(encoding="utf-8"))
RUNBOOK = (REPO_ROOT / "scripts" / "runbook_pass2_signals_r2.md").read_text(encoding="utf-8")
ITEMS = PACK["legs"][0]["items"]
BY_ID = {one["id"]: one for one in ITEMS}
CARRIED = PACK["carried"]["ids"]
OWED = PACK["owed"]["ids"]
R1_ROWS = {
    json.loads(one)["id"]: json.loads(one)
    for one in (RESULTS / "pass2_signals_v1.jsonl").read_text(encoding="utf-8").splitlines()
    if one.strip()
}
F2 = PACK["owed"]["re_asked_after_a_refusal"]
OUT_NAME = PACK["legs"][0]["out"]


# --- the prompt, the renderings and the ceiling -------------------------------------------------


def test_the_prompt_has_not_moved_a_byte():
    """Four carried replies answer this text. A moved byte makes them answers to nothing."""
    assert (
        pass2.prompt_sha256(pass2.PASS2_TASK_V1)
        == R1_RECORD["instruments"]["prompt_sha256"][pass2.PASS2_TASK_V1]
        == PACK["instruments"]["prompt_sha256"][pass2.PASS2_TASK_V1]
    )
    assert pass2_r2.PASS2 is pass2.PASS2, "r2 imports the map, it does not restate it"


def test_every_unit_renders_to_r1s_own_sha_through_both_modules():
    import hashlib

    for one in ITEMS:
        through_r1 = pass2.pass2_messages_gm4(
            one["channel"],
            one["post_id"],
            one["post"],
            one["entities"],
            one["comments"],
            task=one["task"],
        )[0]["content"]
        through_r2 = pass2_r2.pass2_messages_gm4(
            one["channel"],
            one["post_id"],
            one["post"],
            one["entities"],
            one["comments"],
            task=one["task"],
        )[0]["content"]
        assert through_r1 == through_r2
        assert hashlib.sha256(through_r2.encode("utf-8")).hexdigest() == one["rendering_sha256"]
        assert one["rendering_sha256"] == next(
            item["rendering_sha256"]
            for item in R1_PACK["legs"][0]["items"]
            if item["id"] == one["id"]
        )


def test_the_ceiling_swap_is_restored_after_the_call():
    before = pass2.PASS2_MAX_INPUT_CHARS
    one = ITEMS[0]
    pass2_r2.pass2_messages_gm4(
        one["channel"],
        one["post_id"],
        one["post"],
        one["entities"],
        one["comments"],
        task=one["task"],
    )
    assert pass2.PASS2_MAX_INPUT_CHARS == before == prompts.PASS1_MAX_INPUT_CHARS


def test_the_derived_ceiling_accepts_the_widest_unit_and_refuses_one_character_more():
    widest = max(ITEMS, key=lambda one: one["rendered_chars"])
    assert widest["rendered_chars"] == 11856
    assert pass2_r2.PASS2_MAX_INPUT_CHARS == 15569
    pass2_r2.pass2_messages_gm4(
        widest["channel"],
        widest["post_id"],
        widest["post"],
        widest["entities"],
        widest["comments"],
        task=widest["task"],
    )
    # the same unit with its post padded to exactly one character over the ceiling
    over = pass2_r2.PASS2_MAX_INPUT_CHARS - widest["rendered_chars"] + 1
    with pytest.raises(
        ValueError, match=f"over the registered ceiling of {pass2_r2.PASS2_MAX_INPUT_CHARS}"
    ):
        pass2_r2.pass2_messages_gm4(
            widest["channel"],
            widest["post_id"],
            widest["post"] + "x" * over,
            widest["entities"],
            widest["comments"],
            task=widest["task"],
        )
    # and one character under it is accepted
    pass2_r2.pass2_messages_gm4(
        widest["channel"],
        widest["post_id"],
        widest["post"] + "x" * (over - 1),
        widest["entities"],
        widest["comments"],
        task=widest["task"],
    )


def test_the_ceiling_re_derives_from_the_artifacts_it_names():
    """`4 510 × 3.4523 = 15 569` — both inputs read out of files, neither typed twice."""
    reader_pack = json.loads((RESULTS / "reader_v5b_pack.json").read_text(encoding="utf-8"))
    reader = {one["id"]: one for one in reader_pack["items"]}
    rows = {
        json.loads(one)["id"]: json.loads(one)
        for one in (RESULTS / "reader_v5b_w1.jsonl").read_text(encoding="utf-8").splitlines()
        if one.strip()
    }
    widest = max(
        (one for one in rows if one in reader), key=lambda one: reader[one]["rendered_chars"]
    )
    assert reader[widest]["rendered_chars"] == 15673 > 12000, "the reader read whole threads wider"
    assert rows[widest]["usage"]["prompt_tokens"] == pass2_r2.CEILING["proven_prompt_tokens"]
    assert rows[widest]["finish_reason"] == "stop"
    assert reader_pack["serving"]["output_tokens"] == 4000

    density = min(
        BY_ID[one]["rendered_chars"] / row["usage"]["prompt_tokens"] for one, row in R1_ROWS.items()
    )
    import math

    assert math.floor(density * 10_000) / 10_000 == pass2_r2.CEILING["chars_per_prompt_token"]
    assert pass2_r2.PASS2_MAX_INPUT_CHARS == int(
        pass2_r2.CEILING["proven_prompt_tokens"] * pass2_r2.CEILING["chars_per_prompt_token"]
    )


def test_no_record_on_this_stack_carries_the_models_context_length():
    """The contract asks for a ceiling from «the model's context». It is not here, and the
    derivation says so instead of importing a number from outside."""
    assert "not on this stack" in "".join(pass2_r2.CEILING).lower() or any(
        "context" in key for key in pass2_r2.CEILING
    )
    assert pass2_r2.CEILING["the_model_context_is_not_on_this_stack"]


# --- the parser: what may no longer refuse, and what still does ---------------------------------


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


def test_F2s_exact_r1_reply_parses_and_is_COUNTED():
    """The reply that cost r1 its hardest flagship case, read by r2's parser."""
    verdict = pass2_r2.parse_pass2(R1_ROWS[F2]["reply"], unit=BY_ID[F2])
    assert verdict["signals"] == []
    assert len(verdict["per_comment"]) == 2
    assert [one["subject_doubt"] for one in verdict["per_comment"]] == [False, False]
    assert [one["note"] for one in verdict["per_comment"]] == [None, None]
    assert verdict["unreadable_field_names"] == ["per_comment.note"]
    assert len(verdict["unreadable_fields"]) == 2
    assert all(
        one["why"] == "per_comment.note is not a non-empty string"
        for one in verdict["unreadable_fields"]
    )


def test_r1s_parser_still_REFUSES_F2():
    """The tripwire. r1's sealed record says `parse_refusals 1`, and that sentence stays true."""
    with pytest.raises(prompts.ParseError, match="per_comment.note is not a non-empty string"):
        pass2.parse_pass2(R1_ROWS[F2]["reply"], unit=BY_ID[F2])


def test_all_four_carried_replies_parse_under_r2s_parser():
    for one in CARRIED:
        verdict = pass2_r2.parse_pass2(R1_ROWS[one]["reply"], unit=BY_ID[one])
        assert verdict["thread"]["channel"] == BY_ID[one]["channel"]


def test_a_relabel_still_refuses_in_per_comment_and_in_a_signal():
    with pytest.raises(pass2_r2.RelabelError, match="no authority to relabel"):
        pass2_r2.parse_pass2(
            reply(
                per_comment=[
                    {"msg_id": 7, "subject_type": "молочный_бренд", "aspects": [], "note": None}
                ],
                noise=[],
            ),
            unit=unit(),
        )
    with pytest.raises(pass2_r2.RelabelError, match="no authority to relabel"):
        pass2_r2.parse_pass2(
            reply(
                signals=[
                    {
                        "signal_type": "похвала",
                        "subject_type": "сеть_ритейлер",
                        "subject_id": None,
                        "aspect": "taste",
                        "reading": "r",
                        "evidence": [7],
                        "quote": "q",
                    }
                ]
            ),
            unit=unit(),
        )


def test_a_relabel_error_is_a_parse_error_so_the_gate_counts_it_as_a_refusal():
    assert issubclass(pass2_r2.RelabelError, prompts.ParseError)
    assert pass2_r2.RelabelError is pass2.RelabelError


def test_an_id_that_was_not_in_the_request_is_refused_everywhere_it_can_appear():
    for where in ("per_comment", "noise", "signals"):
        payload = {
            "per_comment": {
                "per_comment": [{"msg_id": 99, "subject_type": "категория_личное", "aspects": []}],
                "noise": [],
            },
            "noise": {"noise": [{"msg_id": 99, "class": "оффтоп"}]},
            "signals": {
                "signals": [
                    {
                        "signal_type": "похвала",
                        "subject_type": "категория_личное",
                        "subject_id": None,
                        "aspect": "taste",
                        "reading": "r",
                        "evidence": [99],
                        "quote": "q",
                    }
                ]
            },
        }[where]
        with pytest.raises(prompts.ParseError, match="was not in this request"):
            pass2_r2.parse_pass2(reply(**payload), unit=unit())


def test_a_signal_with_no_comment_behind_it_is_refused():
    with pytest.raises(prompts.ParseError, match="a signal names no comment"):
        pass2_r2.parse_pass2(
            reply(
                signals=[
                    {
                        "signal_type": "похвала",
                        "subject_type": "категория_личное",
                        "subject_id": None,
                        "aspect": "taste",
                        "reading": "r",
                        "evidence": [],
                        "from_post": True,
                        "quote": "q",
                    }
                ]
            ),
            unit=unit(),
        )


def test_a_reply_about_another_thread_is_refused():
    with pytest.raises(prompts.ParseError, match="the reply is about"):
        pass2_r2.parse_pass2(reply(thread={"channel": "@y", "post_id": 1}), unit=unit())


REPORT_ONLY_POISON = {
    "post_summary": "",
    "discussion_summary": "   ",
    "signals.signal_type": "не_бывает_такого_типа",
    "signals.subject_id": 17,
    "signals.stance": "дуже_позитивно",
    "signals.reading": "",
    "signals.quote": None,
    "signals.proposed": 0,
    "per_comment.subject_id": [],
    "per_comment.stance": "жах",
    "per_comment.aspects": "taste",
    "per_comment.note": "",
    "noise.class": "не_сигнал",
}


def test_every_report_only_field_can_be_unreadable_and_the_thread_survives():
    """One reply with EVERY report-only field poisoned at once. Nothing refuses; all are named."""
    poisoned = reply(
        post_summary="",
        discussion_summary="   ",
        signals=[
            {
                "signal_type": "не_бывает_такого_типа",
                "subject_type": "категория_личное",
                "subject_id": 17,
                "aspect": "taste",
                "stance": "дуже_позитивно",
                "reading": "",
                "proposed": 0,
                "evidence": [7],
                "quote": None,
            }
        ],
        per_comment=[
            {
                "msg_id": 7,
                "subject_type": "категория_личное",
                "subject_id": [],
                "stance": "жах",
                "aspects": "taste",
                "note": "",
                "subject_doubt": "може",
            }
        ],
        noise=[{"msg_id": 8, "class": "не_сигнал"}],
    )
    verdict = pass2_r2.parse_pass2(poisoned, unit=unit())
    assert len(verdict["signals"]) == 1, "a scored field was readable, so the signal survives"
    assert verdict["signals"][0]["evidence"] == [7]
    assert verdict["signals"][0]["aspect"] == "taste"
    # every NON-nullable string keeps a STRING: `prompts._reader` guarantees the type, and two of
    # them are grouped on by consumers -- one of which is a SEALED file
    assert verdict["signals"][0]["signal_type"] == pass2_r2.UNREADABLE
    assert verdict["signals"][0]["reading"] == pass2_r2.UNREADABLE
    assert verdict["signals"][0]["quote"] == pass2_r2.UNREADABLE
    assert verdict["post_summary"] == pass2_r2.UNREADABLE
    assert verdict["discussion_summary"] == pass2_r2.UNREADABLE
    assert verdict["noise"][0]["class"] == pass2_r2.UNREADABLE
    # the nullable ones keep None, which is what the pinned reader returns for an absent value
    assert verdict["per_comment"][0]["note"] is None
    assert verdict["per_comment"][0]["subject_id"] is None
    assert verdict["per_comment"][0]["stance"] is None
    assert verdict["per_comment"][0]["aspects"] == []
    assert verdict["per_comment"][0]["subject_doubt"] is None
    assert verdict["signals"][0]["subject_id"] is None
    assert verdict["signals"][0]["stance"] is None
    assert verdict["subject_doubt_unreadable"] == [7]
    named = set(verdict["unreadable_field_names"])
    assert named == set(REPORT_ONLY_POISON) | {
        "per_comment.subject_doubt",
        "signals.proposed",
    }, named


def test_a_domain_violation_on_a_SCORED_field_still_refuses():
    for field, value, match in (
        ("aspect", "не_аспект", "aspect outside its domain"),
        ("subject_type", "не_субъект", "subject_type outside its domain"),
        ("evidence", "7", "evidence is not a list"),
    ):
        signal = {
            "signal_type": "похвала",
            "subject_type": "категория_личное",
            "subject_id": None,
            "aspect": "taste",
            "reading": "r",
            "evidence": [7],
            "quote": "q",
        }
        signal[field] = value
        with pytest.raises(prompts.ParseError, match=match):
            pass2_r2.parse_pass2(reply(signals=[signal]), unit=unit())


def test_a_missing_answer_list_refuses_and_is_never_defaulted_to_empty():
    """`reader_noise_count({})` returns `signals: 0`, so a defaulted list reads GREEN over nothing."""
    for field in ("signals", "per_comment", "noise", "thread"):
        payload = json.loads(reply())
        payload.pop(field)
        with pytest.raises(prompts.ParseError, match="missing field"):
            pass2_r2.parse_pass2(json.dumps(payload, ensure_ascii=False), unit=unit())


def test_a_row_with_no_readable_id_is_DROPPED_and_counted_not_refused():
    verdict = pass2_r2.parse_pass2(
        reply(
            per_comment=[
                {"subject_type": "категория_личное", "aspects": []},
                {"msg_id": 7, "subject_type": "категория_личное", "aspects": []},
            ],
            noise=[{"class": "оффтоп"}],
        ),
        unit=unit(),
    )
    assert [one["msg_id"] for one in verdict["per_comment"]] == [7]
    assert verdict["noise"] == []
    assert len(verdict["rows_without_a_readable_id"]) == 2
    assert {one["list"] for one in verdict["rows_without_a_readable_id"]} == {
        "per_comment",
        "noise",
    }
    assert verdict["accounting"]["in_neither_list"] == [8]


def test_a_MISSING_subject_type_is_an_omission_and_not_a_relabelling():
    verdict = pass2_r2.parse_pass2(
        reply(per_comment=[{"msg_id": 7, "aspects": []}], noise=[]), unit=unit()
    )
    assert verdict["per_comment_subject_omitted"] == [7]
    assert verdict["per_comment"][0]["subject_type"] is None
    # and a NULL one is the same reading
    null = pass2_r2.parse_pass2(
        reply(per_comment=[{"msg_id": 7, "subject_type": None, "aspects": []}], noise=[]),
        unit=unit(),
    )
    assert null["per_comment_subject_omitted"] == [7]


def test_a_vocabulary_SYNONYM_is_not_a_relabelling():
    import score_reader_probe_b as readerscore

    assert pass2_r2.SUBJECT_SYNONYMS == readerscore.COLLAPSE
    verdict = pass2_r2.parse_pass2(
        reply(
            per_comment=[{"msg_id": 7, "subject_type": "категория", "aspects": []}],
            noise=[],
            signals=[],
        ),
        unit=unit(),
    )
    assert verdict["vocabulary_synonyms_used"] == ["категория"]


def test_the_readers_container_repairs_still_fire_through_r2s_wrapper():
    verdict = pass2_r2.parse_pass2(reply(noise={}), unit=unit())
    assert verdict["noise"] == []
    assert "noise: empty object -> empty list" in verdict["repairs"]


def test_the_refusal_set_is_closed_and_named():
    assert len(pass2_r2.REFUSALS) == 6
    assert any("relabel" in one for one in pass2_r2.REFUSALS)
    assert any("SCORED field" in one for one in pass2_r2.REFUSALS)
    assert RECORD["instruments"]["parser"]["refusal_set"] == list(pass2_r2.REFUSALS)


# --- the pack and the seed ----------------------------------------------------------------------


def test_the_pack_is_r1s_79_units_in_r1s_order():
    assert [one["id"] for one in ITEMS] == [one["id"] for one in R1_PACK["legs"][0]["items"]]
    assert PACK["population"]["units"] == 79
    assert PACK["carried"]["units"] == 4
    assert PACK["owed"]["units"] == 75
    assert set(CARRIED) | set(OWED) == set(BY_ID)
    assert not set(CARRIED) & set(OWED)
    assert F2 in OWED and F2 not in CARRIED


def test_the_pack_rebuilds_byte_for_byte_from_its_own_inputs(tmp_path, monkeypatch):
    out = tmp_path / "pack.json"
    monkeypatch.setattr(builder, "OUT", out)
    assert builder.main([]) == 0
    assert json.loads(out.read_text(encoding="utf-8")) == PACK


def test_r1s_pack_still_rebuilds_byte_for_byte(tmp_path, monkeypatch):
    """The tripwire: r2 may not move a byte of `pass2.py`, and r1's pack pins its sha."""
    import build_pass2_pack as r1builder

    assert (
        r1builder.build()["instruments"]["module"]["sha256"]
        == R1_PACK["instruments"]["module"]["sha256"]
    )


def test_the_builder_STOPS_if_a_rendering_has_moved(monkeypatch):
    shipped = builder.rendered

    def moved(one):
        return shipped(one) + " "

    monkeypatch.setattr(builder, "rendered", moved)
    with pytest.raises(SystemExit, match="answers to nothing"):
        builder.build()


def test_the_builder_STOPS_if_a_unit_is_over_the_derived_ceiling(monkeypatch):
    monkeypatch.setattr(pass2_r2, "PASS2_MAX_INPUT_CHARS", 11_000)
    with pytest.raises(SystemExit, match="STOP-before-any-pod"):
        builder.build()


def test_the_seed_is_the_four_carried_rows_and_never_the_refused_one(tmp_path, monkeypatch):
    seed = tmp_path / OUT_NAME
    monkeypatch.setattr(builder, "SEED", seed)
    assert builder.main(["--seed"]) == 0
    rows = [json.loads(one) for one in seed.read_text(encoding="utf-8").splitlines() if one.strip()]
    assert [one["id"] for one in rows] == CARRIED
    assert F2 not in {one["id"] for one in rows}
    for one in rows:
        assert one["carried_from"]["file"] == "results/pass2_signals_v1.jsonl"
        assert one["rendering_sha256"] == BY_ID[one["id"]]["rendering_sha256"]
        assert one["index"] == [item["id"] for item in ITEMS].index(one["id"])
    assert seed.read_text(encoding="utf-8") == (RESULTS / OUT_NAME).read_text(encoding="utf-8")


def test_the_seed_REFUSES_to_overwrite_a_file_that_carries_a_bought_reply(tmp_path, monkeypatch):
    seed = tmp_path / OUT_NAME
    monkeypatch.setattr(builder, "SEED", seed)
    builder.main(["--seed"])
    with seed.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"id": OWED[0], "seconds": 1.0}) + "\n")
    with pytest.raises(SystemExit, match="already carries 1 BOUGHT"):
        builder.main(["--seed"])


def test_the_seed_REFUSES_a_carried_row_whose_rendering_has_moved(tmp_path, monkeypatch):
    seed = tmp_path / OUT_NAME
    out = tmp_path / "pack.json"
    monkeypatch.setattr(builder, "SEED", seed)
    monkeypatch.setattr(builder, "OUT", out)
    moved = json.loads(json.dumps(PACK))
    moved["legs"][0]["items"][0]["rendering_sha256"] = "0" * 64
    out.write_text(json.dumps(moved, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit, match="answers a different request"):
        builder.main(["--seed"])


# --- the record ----------------------------------------------------------------------------------


def test_H6_re_derives_every_number_the_contract_prints():
    assert RECORD["h6"]["mismatches"] == []
    assert len(RECORD["h6"]["rows"]) >= 70
    assert all(one["agrees"] for one in RECORD["h6"]["rows"])


def test_H6_REFUSES_when_a_registered_number_is_moved(tmp_path, monkeypatch):
    monkeypatch.setattr(producer, "SECONDS_PER_CALL", 96.0)
    with pytest.raises(SystemExit, match="do not re-derive"):
        producer.main(["--out", str(tmp_path / "again.json")])
    assert not (tmp_path / "again.json").exists(), "a refusal writes nothing"


def test_the_record_rebuilds_byte_for_byte(tmp_path):
    assert producer.main(["--out", str(tmp_path / "again.json")]) == 0
    assert json.loads((tmp_path / "again.json").read_text(encoding="utf-8")) == RECORD


def test_every_clock_rung_carries_its_deadline_by_key():
    for one in RECORD["kill_clock"]:
        if int(one["rung"]) in gate.DEADLINE_RUNGS:
            assert isinstance(one["deadline_seconds"], int | float), one["name"]


def test_the_RUNGS_THEMSELVES_read_the_key_and_not_the_prose(tmp_path, monkeypatch):
    """Prepend a digit-run to every rung's prose. The number the rungs act on must not move."""
    poisoned = json.loads(json.dumps(RECORD))
    for one in poisoned["kill_clock"]:
        one["rule"] = f"rung {one['rung']} of 7 — {one['rule']}"
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.window, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    state = json.loads(record.read_text(encoding="utf-8"))
    now = gate.window.stamp("2026-08-22T10:04:00+00:00")
    two = gate.r2.gate_zero(poisoned, state, 400.0, False, now)
    assert two["deadline_seconds" if "deadline_seconds" in two else "seconds_left"] is not None
    assert two["verdict"] == "WAIT", "400 s against a 500 s deadline, not against a 2 s one"
    three = gate.r2.gate_boot(poisoned, state, 400.0, None, None, now)
    assert three["verdict"] in ("WAIT", "KILL")
    assert gate.r2.rung(poisoned, 5)["rule"].startswith("600.0 s — ")


def test_a_clock_rung_with_no_deadline_key_is_REFUSED_and_never_defaulted():
    poisoned = json.loads(json.dumps(RECORD))
    for one in poisoned["kill_clock"]:
        if int(one["rung"]) == 5:
            one.pop("deadline_seconds")
    with pytest.raises(SystemExit, match="carries no `deadline_seconds`"):
        gate.r2.rung(poisoned, 5)


def test_the_record_has_no_go_no_go_rung_and_the_pack_has_no_smoke():
    assert [int(one["rung"]) for one in RECORD["kill_clock"]] == [1, 2, 3, 4, 5, 6, 7]
    assert "smoke" not in PACK
    assert "go_token" not in RECORD["run_record"]
    assert list(RECORD["bars"]["completeness"]["arms"]) == ["GO"]


def test_the_repealed_numbers_appear_only_inside_supersedes():
    """The Dv613 sweep: a repealed threshold that survives elsewhere in the file is the defect."""
    whole = json.dumps(RECORD, ensure_ascii=False)
    inside = json.dumps(RECORD["supersedes"], ensure_ascii=False)
    # the `step_0_5_*` H6 rows re-derive r1's own arithmetic in order to CORRECT it, so they carry
    # r1's numbers by subject. Named here and named in the record, never silently swept over
    corrections = json.dumps(
        [one for one in RECORD["h6"]["rows"] if one["name"].startswith("step_0_5_")],
        ensure_ascii=False,
    )[1:-1]
    outside = whole.replace(inside, "").replace(corrections, "")
    assert corrections, "the step-0.5 corrections must exist, or the exclusion is hiding nothing"
    for number in ("6600", "48.6486", "32.4324"):
        assert number not in outside, number
    assert "1.50" not in outside.replace("$1.50", "")
    for number in ("6600", "48.6486", "32.4324", "120", "12000"):
        assert number in inside, number


def test_the_overhead_is_one_number_in_two_places():
    sums = RECORD["money"]["arithmetic"]
    assert sums["overhead_seconds"] == sums["cumulative"]["projection_gate"]["overhead_seconds"]


def test_the_pack_and_the_record_agree_on_the_key_the_pinned_gate_compares():
    assert PACK["population"]["payable_comments"] == RECORD["population"]["payable_comments"] == 79


def test_the_recovery_window_is_derived_at_both_spans_and_both_rungs_fit():
    rec = RECORD["money"]["arithmetic"]["recovery_arithmetic"]
    assert rec["widest_create_elapsed_at_which_a_KILL_is_still_recoverable_seconds"] == 1246.5
    assert rec["widest_create_elapsed_at_the_measured_pre_generation_seconds"] == 2211.5
    assert rec["rung_2_is_inside_the_window"] is True
    assert rec["rung_3_is_inside_the_window"] is True
    assert (
        rec["dead_pod_plus_worst_case_seconds"]
        <= RECORD["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"]
    )


def test_the_rate_is_the_smokes_MAX_times_the_measured_spread():
    arm = RECORD["money"]["arithmetic"]["seconds_per_call"]
    assert arm["r2"] == 97.0
    assert arm["smoke"]["max"] == 58.07
    assert arm["pod_class_spread"]["v2_spread_registered"] == 1.67
    assert arm["pod_class_spread"]["v2_min"] == 2.694083
    assert arm["pod_class_spread"]["v2_max"] == 4.498473
    assert round(arm["pod_class_spread"]["base_spread"], 4) == 2.2509


# --- the gate --------------------------------------------------------------------------------------


def state_with_pod(**kw) -> dict:
    pod = {
        "pod_id": "p1",
        "created_at": "2026-08-22T10:00:00+00:00",
        "usd_per_hour": 0.74,
        "card": "RTX 4090",
        "terminate_after": "2026-08-22T13:03:00+00:00",
    }
    return {"pods": [{**pod, **kw}], "gates": []}


def seeded(path: Path) -> None:
    path.write_text((RESULTS / OUT_NAME).read_text(encoding="utf-8"), encoding="utf-8")


def bought_rows(path: Path, ids: list[str], seconds, elapsed_base: float = 300.0) -> None:
    """The seeded file plus N rows this pod bought."""
    values = [seconds] * len(ids) if isinstance(seconds, int | float) else seconds
    text = (RESULTS / OUT_NAME).read_text(encoding="utf-8")
    text += "".join(
        json.dumps(
            {
                "index": [one["id"] for one in ITEMS].index(name),
                "id": name,
                "thread": name,
                "rendering_sha256": BY_ID[name]["rendering_sha256"],
                "reply": "{}",
                "balanced": True,
                "seconds": value,
                "elapsed_since_start": elapsed_base + index,
            },
            ensure_ascii=False,
        )
        + "\n"
        for index, (name, value) in enumerate(zip(ids, values, strict=True))
    )
    path.write_text(text, encoding="utf-8")


def test_the_gate_refuses_to_load_if_r1s_gate_has_moved(tmp_path, monkeypatch):
    moved = tmp_path / "gate.py"
    moved.write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setattr(gate, "R1_GATE", moved)
    with pytest.raises(SystemExit, match="may not be edited"):
        gate._load()


def test_loading_r1s_gate_twice_does_not_move_r1s_own_paths():
    import gate_pass2_signals as canonical

    assert canonical.PACK.name == "pass2_pack.json"
    assert canonical.RECORD.name == "pass2_signals_run.json"
    assert gate.r2.PACK.name == "pass2_r2_pack.json"
    assert gate.window.PACK.name == "pass2_r2_pack.json"
    assert gate.window.LAUNCH_STAMP == "pass2_signals_r2_launched_at"


def test_the_whole_leg_is_authorised_from_rung_0_and_it_owes_75():
    assert gate.authorised(PACK) is PACK
    assert gate.legs_of(PACK)[0]["units"] == 75
    assert gate.legs_of(PACK)[0]["out"] == OUT_NAME


def test_leg_state_prices_the_75_and_keeps_r1s_seconds_out_of_the_rate(tmp_path, monkeypatch):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.window, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    out = tmp_path / OUT_NAME
    seeded(out)
    before = gate.leg_state(RECORD, [PACK], tmp_path)
    assert before[0]["answered"] == 0
    assert before[0]["carried_rows_in_the_file"] == 4
    assert before[0]["remaining"] == 75
    assert before[0]["seconds_per_call_used"] == 97.0
    assert before[0]["rate_source"] == "registered"
    bought_rows(out, OWED[:3], 20.0)
    after = gate.leg_state(RECORD, [PACK], tmp_path)
    assert after[0]["answered"] == 3
    assert after[0]["remaining"] == 72
    assert after[0]["measured_seconds_per_call"] == 20.0, (
        "r1's 58.07/40.845/56.462/56.732 are on another pod and are not in this mean"
    )


def test_rung_3_still_FIRES_with_the_four_carried_rows_in_the_file(tmp_path, monkeypatch):
    """The fatal one. `watch`'s boot branch is `if not cleared and not answered`."""
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.window, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    out = tmp_path / OUT_NAME
    seeded(out)
    log = tmp_path / "pod.log"
    log.write_text("boot\n", encoding="utf-8")
    (tmp_path / "pass2_signals_r2_launched_at").write_text(
        "2026-08-22T10:01:00+00:00\n", encoding="utf-8"
    )
    assert gate.fingerprint(tmp_path, gate.legs_of(PACK), log)[0] == 0, (
        "the four carried rows are not this pod's work and must not disarm rung 3"
    )
    verdict = gate.window.watch(
        RECORD,
        json.loads(record.read_text(encoding="utf-8")),
        [PACK],
        where=tmp_path,
        log=log,
        pull=lambda: None,
        kill=lambda: {"deleted": True},
        sleep=lambda _s: None,
        now=gate.window.stamp("2026-08-22T10:20:00+00:00"),
        poll_seconds=0,
    )
    assert verdict["verdict"] == "KILL"
    assert "rung 3" in verdict["cause"]
    assert verdict["answered"] == 0 and verdict["owed"] == 75


def test_rung_3s_READING_is_this_pods_first_reply_and_never_r1s(tmp_path):
    out = tmp_path / OUT_NAME
    seeded(out)
    assert gate.first_reply_after_launch(RECORD, tmp_path) is None, (
        "r1's carried rows carry elapsed_since_start 197.6 and would report a passing rung 3"
    )
    bought_rows(out, OWED[:1], 20.0, elapsed_base=460.0)
    assert gate.first_reply_after_launch(RECORD, tmp_path) == 460.0


def test_rung_4_KILLS_at_115_seconds_a_thread_after_10_and_GOES_at_90(tmp_path, monkeypatch):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.window, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    out = tmp_path / OUT_NAME
    pre_generation = RECORD["money"]["arithmetic"]["pre_generation_seconds"]

    def drive(rate):
        """Ten replies at `rate`, at the create-elapsed those ten actually cost."""
        bought_rows(out, OWED[:10], rate)
        legs = gate.leg_state(RECORD, [PACK], tmp_path)
        at = gate.window.stamp("2026-08-22T10:00:00+00:00") + datetime.timedelta(
            seconds=pre_generation + 10 * rate
        )
        return gate.window.projection(
            RECORD, json.loads(record.read_text(encoding="utf-8")), legs, at
        )

    killed = drive(115.0)
    assert killed["verdict"] == "KILL"
    assert (
        killed["projected_seconds"]
        > RECORD["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"]
    )
    fine = drive(90.0)
    assert fine["verdict"] == "GO"
    edge = next(one for one in RECORD["kill_clock"] if int(one["rung"]) == 4)
    assert edge["knife_edge_at_the_charged_spans"] == 114.6667
    assert edge["knife_edge_at_the_measured_pre_generation"] == 127.5333


def test_the_recovery_clause_allows_the_FIRST_create_with_a_seeded_file(tmp_path, monkeypatch):
    out = tmp_path / OUT_NAME
    seeded(out)
    monkeypatch.setattr(gate, "OUT_FILE", out)
    verdict = gate.pre_create(RECORD, {"pods": [], "gates": []})
    assert verdict["verdict"] == "GO"
    assert verdict["carried_rows_in_the_file"] == 4
    assert verdict["replies_bought_by_this_session"] == 0


def test_the_recovery_clause_refuses_a_pod_after_the_first_BOUGHT_reply(tmp_path, monkeypatch):
    out = tmp_path / OUT_NAME
    monkeypatch.setattr(gate, "OUT_FILE", out)
    dead = {
        "pods": [
            {
                "pod_id": "p1",
                "created_at": "2026-08-22T10:00:00+00:00",
                "usd_per_hour": 0.74,
                "deleted_at": "2026-08-22T10:10:00+00:00",
                "billed_seconds": 600.0,
                "billed_usd": 0.1233,
            }
        ],
        "gates": [],
    }
    seeded(out)
    assert gate.pre_create(RECORD, dead)["verdict"] == "GO", "a death at rungs 1–3 is recoverable"
    bought_rows(out, OWED[:1], 20.0)
    refused = gate.pre_create(RECORD, dead)
    assert refused["verdict"] == "KILL"
    assert refused["replies_bought_by_this_session"] == 1
    assert "AFTER the first new reply" in refused["next_step"]


def test_rung_5_fires_on_a_log_that_stops_and_not_only_on_a_file_that_stops(tmp_path, monkeypatch):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.window, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    log = tmp_path / "pod.log"
    out = tmp_path / OUT_NAME
    bought_rows(out, OWED[:3], 30.0)
    clock = {"now": 0.0}
    lines = {"n": 1}
    log.write_text("boot\n", encoding="utf-8")
    kills = []

    def tick(step: float):
        clock["now"] += step

    def growing_log():
        lines["n"] += 1
        log.write_text(
            "boot\n" + "".join(f"reply {i}\n" for i in range(lines["n"])), encoding="utf-8"
        )

    with pytest.raises(RuntimeError, match="stop the loop"):
        gate.window.watch(
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
            now=gate.window.stamp("2026-08-22T10:05:00+00:00"),
            poll_seconds=0,
        )
    assert kills == []

    clock["now"] = 0.0
    verdict = gate.window.watch(
        RECORD,
        json.loads(record.read_text(encoding="utf-8")),
        [PACK],
        where=tmp_path,
        log=log,
        pull=lambda: None,
        kill=lambda: {"deleted": True},
        sleep=lambda _s: tick(200.0),
        clock_now=lambda: clock["now"],
        now=gate.window.stamp("2026-08-22T10:05:00+00:00"),
        poll_seconds=0,
    )
    assert verdict["verdict"] == "KILL"
    assert "rung 5" in verdict["cause"]
    assert verdict["idle_deadline_seconds"] == 600.0


def test_the_watch_returns_GO_when_the_75_are_bought(tmp_path, monkeypatch):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.window, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    log = tmp_path / "pod.log"
    log.write_text("boot\n", encoding="utf-8")
    out = tmp_path / OUT_NAME
    bought_rows(out, OWED, 30.0)
    verdict = gate.window.watch(
        RECORD,
        json.loads(record.read_text(encoding="utf-8")),
        [PACK],
        where=tmp_path,
        log=log,
        pull=lambda: None,
        kill=lambda: {"deleted": True},
        sleep=lambda _s: None,
        now=gate.window.stamp("2026-08-22T10:05:00+00:00"),
        poll_seconds=0,
    )
    assert verdict["verdict"] == "GO"
    assert verdict["owed"] == 75 and verdict["answered"] == 75
    assert len(out.read_text(encoding="utf-8").splitlines()) == 79


def whole_run(path: Path) -> None:
    """The out-file a complete run leaves: the four carried rows plus 75 real replies."""
    text = (RESULTS / OUT_NAME).read_text(encoding="utf-8")
    for index, name in enumerate(OWED):
        item = BY_ID[name]
        answer = {
            "thread": {"channel": item["channel"], "post_id": item["post_id"]},
            "post_summary": "пост",
            "discussion_summary": "обговорення",
            "signals": [],
            "per_comment": [
                {
                    "msg_id": one["msg_id"],
                    "subject_type": one["subject_type"],
                    "aspects": [],
                    "note": "" if name == OWED[0] else None,
                }
                for one in item["comments"]
            ],
            "noise": [],
        }
        text += (
            json.dumps(
                {
                    "index": [x["id"] for x in ITEMS].index(name),
                    "id": name,
                    "thread": name,
                    "rendering_sha256": item["rendering_sha256"],
                    "reply": json.dumps(answer, ensure_ascii=False),
                    "balanced": True,
                    "emitted_chars": 100,
                    "finish_reason": "stop",
                    "usage": {"prompt_tokens": 2000, "completion_tokens": 300},
                    "seconds": 30.0 + index,
                    "elapsed_since_start": 460.0 + index,
                },
                ensure_ascii=False,
            )
            + "\n"
        )
    path.write_text(text, encoding="utf-8")


def test_rung_7_scores_all_79_and_counts_the_carried_rows_separately(tmp_path, monkeypatch):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.window, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    out = tmp_path / OUT_NAME
    whole_run(out)
    verdict = gate.completeness(
        RECORD,
        json.loads(record.read_text(encoding="utf-8")),
        PACK,
        tmp_path,
        gate.window.stamp("2026-08-22T12:00:00+00:00"),
    )
    assert verdict["verdict"] == "GO"
    assert verdict["arm"] == "GO"
    assert verdict["answered"] == 79 and verdict["owed"] == 79
    assert verdict["carried_count"] == 4
    assert verdict["bought_by_this_pod"] == 75
    assert verdict["parse_refusals"] == 0
    assert verdict["parse_refusals_maximum"] == 14


def test_rung_7_counts_an_unreadable_report_only_field_and_does_NOT_refuse(tmp_path, monkeypatch):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.window, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    out = tmp_path / OUT_NAME
    whole_run(out)
    verdict = gate.completeness(
        RECORD,
        json.loads(record.read_text(encoding="utf-8")),
        PACK,
        tmp_path,
        gate.window.stamp("2026-08-22T12:00:00+00:00"),
    )
    # OWED[0] is the F2 thread and its synthetic reply writes `"note": ""` on every row
    assert verdict["unreadable_report_only_fields"] == len(BY_ID[OWED[0]]["comments"])
    assert verdict["unreadable_report_only_fields_by_name"] == {
        "per_comment.note": len(BY_ID[OWED[0]]["comments"])
    }
    assert verdict["parse_refusals"] == 0, "a report-only field may not refuse"


def test_rung_7_goes_RED_when_a_thread_is_missing(tmp_path, monkeypatch):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.window, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    out = tmp_path / OUT_NAME
    whole_run(out)
    lines = out.read_text(encoding="utf-8").splitlines()
    out.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    verdict = gate.completeness(
        RECORD,
        json.loads(record.read_text(encoding="utf-8")),
        PACK,
        tmp_path,
        gate.window.stamp("2026-08-22T12:00:00+00:00"),
    )
    assert verdict["verdict"] == "RED"
    assert verdict["answered"] == 78 and verdict["unanswered"] == 1


def test_the_go_no_go_flag_is_REFUSED():
    with pytest.raises(SystemExit, match="r2 has no go/no-go"):
        gate.main(["--go-no-go"])


def test_EVERY_gate_command_runs_end_to_end(tmp_path, monkeypatch, capsys):
    """The COMMANDS, not the functions behind them — r1's two fatal defects lived in `main`."""
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.window, "RECORD", record)
    monkeypatch.setattr(gate.window, "registration", lambda: RECORD)
    monkeypatch.setattr(gate, "OUT_FILE", tmp_path / OUT_NAME)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    whole_run(tmp_path / OUT_NAME)
    (tmp_path / "pass2_signals_r2_launched_at").write_text(
        "2026-08-22T10:04:00+00:00\n", encoding="utf-8"
    )
    now = gate.window.stamp("2026-08-22T10:20:00+00:00")
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
    assert (
        gate.main(
            ["--close", "--deleted-at", "2026-08-22T10:30:00+00:00", "--outcome", "test"], now
        )
        == gate.GO
    )
    state = json.loads(record.read_text(encoding="utf-8"))
    assert [one["kind"] for one in state["gates"]][-1] == "close"
    assert state["pods"][0]["billed_seconds"] == 1800.0


def test_the_PRE_CREATE_CHECK_command_runs_and_RECORDS_its_verdict(tmp_path, monkeypatch, capsys):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate, "RECORD", record)
    monkeypatch.setattr(gate.window, "RECORD", record)
    monkeypatch.setattr(gate.window, "registration", lambda: RECORD)
    monkeypatch.setattr(gate, "OUT_FILE", tmp_path / OUT_NAME)
    seeded(tmp_path / OUT_NAME)
    assert gate.main(["--pre-create-check"]) == gate.GO
    state = json.loads(record.read_text(encoding="utf-8"))
    assert state["gates"][-1]["kind"] == "pre-create-check"
    assert state["gates"][-1]["verdict"] == "GO"
    assert state["gates"][-1]["carried_rows_in_the_file"] == 4
    capsys.readouterr()


def test_the_PRICE_command_runs_and_its_backstop_guard_bites_both_ways(
    tmp_path, monkeypatch, capsys
):
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.window, "RECORD", record)
    monkeypatch.setattr(gate.window, "registration", lambda: RECORD)
    monkeypatch.setattr(gate, "OUT_FILE", tmp_path / OUT_NAME)
    seeded(tmp_path / OUT_NAME)
    created = "2026-08-22T10:00:00+00:00"
    stop = RECORD["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"]
    good = (gate.window.stamp(created) + datetime.timedelta(seconds=stop)).isoformat(
        timespec="seconds"
    )
    now = gate.window.stamp("2026-08-22T10:01:00+00:00")

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

    far = (gate.window.stamp(created) + datetime.timedelta(seconds=stop + 600)).isoformat(
        timespec="seconds"
    )
    with pytest.raises(SystemExit, match="beyond the"):
        price(0.74, far)
    state = json.loads(record.read_text(encoding="utf-8"))
    assert state["gates"][-1]["verdict"] == "KILL"
    assert "IS LIVE AND BILLING" in state["gates"][-1]["next_step"]

    assert price(0.95, good) == gate.KILL


# --- the runner --------------------------------------------------------------------------------


def test_the_runner_swaps_exactly_the_two_shipped_names_and_puts_them_back():
    import reader_v5_pod_runner as shipped

    before = {name: getattr(shipped, name) for name in runner.SWAPPED}
    with runner.as_pass2():
        assert shipped.render is runner.render
        assert shipped.check_instrument is runner.check_instrument
    assert {name: getattr(shipped, name) for name in runner.SWAPPED} == before


def test_the_handshake_pins_BOTH_modules(tmp_path):
    repo = REPO_ROOT
    got = runner.check_instrument(PACK, repo, prompts)
    assert got["module_sha256"] == PACK["instruments"]["module"]["sha256"]
    assert got["module_r2_sha256"] == PACK["instruments"]["module_r2"]["sha256"]
    moved = json.loads(json.dumps(PACK))
    moved["instruments"]["module_r2"]["sha256"] = "0" * 64
    with pytest.raises(SystemExit, match="pass2_r2.py hashes"):
        runner.check_instrument(moved, repo, prompts)


def test_a_task_that_is_not_pass_2s_goes_to_the_shipped_render():
    """`ReaderClient.__init__` probes the chat template with the READER task before any item."""
    import reader_v5_pod_runner as shipped

    item = {"channel": "@x", "post_id": 1, "post": "p", "comments": [], "thread": "@x:1"}
    with runner.as_pass2():
        assert shipped.render(prompts, item, prompts.READER_TASK_V2) == runner.SHIPPED_RENDER(
            prompts, item, prompts.READER_TASK_V2
        )


def test_the_runner_REFUSES_a_seeded_file_the_pack_does_not_name(tmp_path):
    out = tmp_path / OUT_NAME
    seeded(out)
    assert runner.carried(out, PACK) == sorted(CARRIED)
    rows = [json.loads(one) for one in out.read_text(encoding="utf-8").splitlines() if one.strip()]
    rows[0]["id"] = OWED[0]
    out.write_text(
        "".join(json.dumps(one, ensure_ascii=False) + "\n" for one in rows), encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="not the one the registration seeded"):
        runner.carried(out, PACK)


def test_a_fake_run_answers_the_75_and_never_re_asks_the_4(tmp_path, capsys):
    """The whole loop on a fake client: the carried rows are skipped, the owed ones are bought."""
    asked = []

    class Client:
        def read(self, task, items):
            asked.extend(one["id"] for one in items)
            return [
                {
                    "content": json.dumps(
                        {
                            "thread": {"channel": one["channel"], "post_id": one["post_id"]},
                            "post_summary": "п",
                            "discussion_summary": "о",
                            "signals": [],
                            "per_comment": [
                                {
                                    "msg_id": row["msg_id"],
                                    "subject_type": row["subject_type"],
                                    "aspects": [],
                                }
                                for row in one["comments"]
                            ],
                            "noise": [],
                        },
                        ensure_ascii=False,
                    ),
                    "finish_reason": "stop",
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1},
                }
                for one in items
            ]

    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps(PACK, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / OUT_NAME
    seeded(out)
    code = runner.main(
        ["--pack", str(pack), "--outdir", str(tmp_path), "--repo", str(REPO_ROOT)],
        loader=lambda *a, **kw: Client(),
    )
    assert code == 0
    assert asked == OWED, "every owed unit once, in pack order, and not one carried unit"
    rows = [json.loads(one) for one in out.read_text(encoding="utf-8").splitlines() if one.strip()]
    assert len(rows) == 79
    assert sum(1 for one in rows if one.get("carried_from")) == 4
    assert capsys.readouterr().out.count("carried and NOT re-asked: 4") == 1


# --- the scorer -----------------------------------------------------------------------------------


def test_the_scorer_reads_all_79_and_prices_only_the_75(tmp_path, monkeypatch):
    out = tmp_path / OUT_NAME
    whole_run(out)
    monkeypatch.setattr(scoring, "EVIDENCE", out)
    monkeypatch.setattr(scoring, "RUN", tmp_path / "run.json")
    (tmp_path / "run.json").write_text(
        json.dumps(
            {
                "pods": [
                    {
                        "pod_id": "p1",
                        "created_at": "2026-08-22T10:00:00+00:00",
                        "usd_per_hour": 0.74,
                        "deleted_at": "2026-08-22T11:00:00+00:00",
                        "billed_seconds": 3600.0,
                        "billed_usd": 0.74,
                    }
                ],
                "gates": [],
            }
        ),
        encoding="utf-8",
    )
    verdict = scoring.build()
    assert verdict["evidence"]["units_read"] == 79
    assert verdict["evidence"]["units_bought_by_this_pod"] == 75
    assert verdict["evidence"]["units_carried_from_r1"] == 4
    assert verdict["non_gating"]["units_bought"] == 75
    assert verdict["non_gating"]["seconds_per_unit_mean"] == round(
        sum(30.0 + i for i in range(75)) / 75, 3
    )
    assert verdict["non_gating"]["r1_smoke_max"] == 58.07
    assert verdict["replies"]["refused"] == 0
    assert verdict["unreadable_report_only_fields"]["by_field"] == {
        "per_comment.note": len(BY_ID[OWED[0]]["comments"])
    }
    for name, bar in verdict["bars"].items():
        assert bar["scored"] is True, name


def test_the_scorer_does_not_move_r1s_own_parser():
    """Re-binding `score_pass2_signals.pass2` would break r1's scorer for the rest of the process."""
    import score_pass2_signals as r1score

    assert r1score.pass2 is pass2
    assert scoring.pass2_r2 is pass2_r2


# --- the runbook ------------------------------------------------------------------------------


def test_the_runbook_scps_the_seeded_out_file_to_the_pod():
    """The step with money on it: without the seed on the pod, four threads are re-bought."""
    assert f"results/{OUT_NAME} \\" in RUNBOOK or f"results/{OUT_NAME}" in RUNBOOK
    assert f"root@<HOST>:/workspace/run/{OUT_NAME}" in RUNBOOK
    assert "REFUSES to start without it" in RUNBOOK
    assert "re-buy" in RUNBOOK


def test_the_runbook_launches_the_r2_runner_with_the_pack():
    assert "scripts/pass2_r2_pod_runner.py" in RUNBOOK
    assert "--pack /workspace/repo/results/pass2_r2_pack.json" in RUNBOOK
    assert "pass2_pod_runner.py" not in RUNBOOK.replace("pass2_r2_pod_runner.py", "")


def test_the_runbook_has_no_go_token_and_no_wait():
    launch = RUNBOOK.split("nohup", 1)[1].split("```", 1)[0]
    assert "--go" not in launch, launch
    assert "pass2_go" not in RUNBOOK
    assert "There is no `--go` and no `--go-deadline`" in RUNBOOK
    assert "go/no-go" in RUNBOOK, "it says the rung is GONE, which is not the same as silence"


def test_the_runbook_writes_the_launch_stamp_under_the_name_the_gate_copies():
    assert "> /workspace/run/launched_at" in RUNBOOK
    assert gate.LAUNCH_STAMP in RUNBOOK
    assert gate.window.LAUNCH_STAMP == gate.LAUNCH_STAMP


def test_the_runbook_names_the_guard_step_and_the_cap_the_record_registers():
    step = RECORD["money"]["guard"]["step"]
    cap = RECORD["money"]["guard"]["step_cap_usd"]
    assert f"--step {step} --step-cap {cap:.2f}" in RUNBOOK


def test_the_runbook_quotes_the_records_own_numbers():
    """Digits only, thin spaces and commas stripped — the runbook writes 7 275, the record 7275."""
    flat = re.sub(r"[\s,]", "", RUNBOOK)
    sums = RECORD["money"]["arithmetic"]
    rec = sums["recovery_arithmetic"]
    rung4 = next(one for one in RECORD["kill_clock"] if int(one["rung"]) == 4)
    for number in (
        f"{sums['generation_seconds']:.0f}",
        f"{sums['total_seconds']:.0f}",
        f"{sums['cumulative']['hard_stop_seconds']:.0f}",
        f"{sums['seconds_per_call']['r2']:.0f}",
        f"{round(rung4['knife_edge_at_the_charged_spans'], 1)}",
        f"{round(rung4['knife_edge_at_the_measured_pre_generation'], 1)}",
        f"{rec['widest_dead_pod_that_still_fits_seconds']:.0f}",
        f"{rec['widest_create_elapsed_at_which_a_KILL_is_still_recoverable_seconds']}",
        f"{rec['widest_create_elapsed_at_the_measured_pre_generation_seconds']}",
    ):
        assert number in flat, number


def test_the_runbook_forbids_what_the_contract_forbids():
    for clause in (
        "may not move a byte",
        "No re-buy of the four carried threads",
        "never a third pod",
        "No bar on the fourteen",
    ):
        assert clause in RUNBOOK, clause


# --- the five-lens review's findings, each pinned so it cannot come back ------------------------


def test_the_verdict_SURVIVES_r1s_SEALED_tables_when_a_report_only_field_is_unreadable():
    """The fatal one: `None` in a field a consumer groups on crashes D2 AFTER the money is spent.

    `score_pass2_signals.drop_table` — a SEALED file — does `sorted(Counter(noise.class).items())`,
    and r2's own verdict producer does the same over `signals.signal_type`. One unreadable field in
    any of 79 threads raised `TypeError: '<' not supported between 'NoneType' and 'str'`, with rung
    7 already GO. The tolerant reader had moved the refusal, not removed it.
    """
    import score_pass2_signals as r1score

    two = unit(
        comments=[
            {
                "msg_id": 7,
                "text": "t",
                "subject_type": "категория_личное",
                "subject_id": None,
                "stance": None,
            },
            {
                "msg_id": 8,
                "text": "u",
                "subject_type": "сеть_ритейлер",
                "subject_id": None,
                "stance": None,
            },
        ]
    )
    good = pass2_r2.parse_pass2(reply(noise=[{"msg_id": 8, "class": "оффтоп"}]), unit=two)
    bad_class = pass2_r2.parse_pass2(reply(noise=[{"msg_id": 8, "class": "не_сигнал"}]), unit=two)
    bad_word = pass2_r2.parse_pass2(
        reply(
            signals=[
                {
                    "signal_type": "не_бывает_такого",
                    "subject_type": "категория_личное",
                    "subject_id": None,
                    "aspect": "taste",
                    "reading": "r",
                    "evidence": [7],
                    "quote": "q",
                }
            ],
            noise=[{"msg_id": 8, "class": "оффтоп"}],
        ),
        unit=two,
    )
    assert bad_class["noise"][0]["class"] == pass2_r2.UNREADABLE
    assert bad_word["signals"][0]["signal_type"] == pass2_r2.UNREADABLE

    # r1's SEALED table, over a verdict carrying an unreadable class
    fake_pack = {
        "legs": [
            {
                "items": [
                    {"id": "@x:1", "comments": two["comments"]},
                    {"id": "@y:1", "comments": two["comments"]},
                ]
            }
        ]
    }
    table = r1score.drop_table(fake_pack, {"@x:1": good, "@y:1": bad_class})
    assert pass2_r2.UNREADABLE in table["by_noise_class"]

    # and r2's own two Counter/sorted lines over an unreadable signal_type
    from collections import Counter

    signals = [*good["signals"], *bad_word["signals"]]
    assert dict(sorted(Counter(one["signal_type"] for one in signals).items()))
    assert sorted({one["signal_type"] for one in signals if one.get("proposed")}) == [
        pass2_r2.UNREADABLE
    ]


def test_an_OVERWRITTEN_proposed_flag_is_RECORDED_in_its_OWN_census():
    """`proposed` is forced True to carry an unreadable word past the pinned domain check.

    Its own list, its own name, the MODEL's raw value, and only when something actually changed.
    Filing it under `unreadable_fields` would inflate the Dv702 measurement this contract was
    bought to take with a field the reader read perfectly well.
    """

    def signal(**kw):
        one = {
            "signal_type": "не_бывает_такого",
            "subject_type": "категория_личное",
            "subject_id": None,
            "aspect": "taste",
            "reading": "r",
            "evidence": [7],
            "quote": "q",
        }
        return pass2_r2.parse_pass2(reply(signals=[{**one, **kw}], noise=[]), unit=unit())

    for label, kw, raw in (
        ("the flag is absent", {}, "null"),
        ("the model said false", {"proposed": False}, "false"),
        ("the model wrote 0, which is not a boolean", {"proposed": 0}, "0"),
    ):
        verdict = signal(**kw)
        assert verdict["signals"][0]["proposed"] is True, label
        assert verdict["signals"][0]["signal_type"] == pass2_r2.UNREADABLE, label
        assert verdict["overwritten_field_names"] == ["signals.proposed"], label
        row = verdict["overwritten_fields"][0]
        assert row["value"] == raw, (label, row)
        assert "overwritten to True" in row["why"], label
        # and the OVERWRITE is not filed as an unreadable field
        assert "signals.proposed" not in [
            one["field"] for one in verdict["unreadable_fields"] if one["why"].startswith("over")
        ], label

    # the model wrote `0`: the flag itself IS unreadable AND it was overwritten — two facts, two
    # lists, and the unreadable row carries the validator's own message
    both = signal(proposed=0)
    assert "signals.proposed" in both["unreadable_field_names"]
    assert [
        one["why"] for one in both["unreadable_fields"] if one["field"] == "signals.proposed"
    ] == ["signals.proposed is not a boolean"]

    # a legitimate `proposed: true` with a sixth word changes nothing and records nothing
    clean = signal(proposed=True)
    assert clean["signals"][0]["signal_type"] == "не_бывает_такого"
    assert clean["signals"][0]["proposed"] is True
    assert clean["unreadable_field_names"] == [] and clean["overwritten_field_names"] == []


def test_D2_does_not_publish_a_sixth_signal_type_the_model_DENIED(tmp_path, monkeypatch):
    """`proposed_signal_types` is the model's list, and the parser's forced True is not in it."""
    out = tmp_path / OUT_NAME
    whole_run(out)
    rows = [json.loads(one) for one in out.read_text(encoding="utf-8").splitlines() if one.strip()]
    target = next(one for one in rows if one["id"] == OWED[1])
    answer = json.loads(target["reply"])
    answer["signals"] = [
        {
            "signal_type": "не_бывает_такого",
            "subject_type": answer["per_comment"][0]["subject_type"],
            "subject_id": None,
            "aspect": "taste",
            "reading": "r",
            "proposed": False,
            "evidence": [answer["per_comment"][0]["msg_id"]],
            "quote": "q",
        }
    ]
    target["reply"] = json.dumps(answer, ensure_ascii=False)
    out.write_text(
        "".join(json.dumps(one, ensure_ascii=False) + "\n" for one in rows), encoding="utf-8"
    )
    monkeypatch.setattr(scoring, "EVIDENCE", out)
    monkeypatch.setattr(scoring, "RUN", tmp_path / "run.json")
    (tmp_path / "run.json").write_text(json.dumps({"pods": [], "gates": []}), encoding="utf-8")
    verdict = scoring.build()
    assert verdict["replies"]["proposed_signal_types"] == []
    assert verdict["replies"]["signal_types_the_parser_could_not_read"] == 1
    assert verdict["overwritten_report_only_fields"]["by_field"] == {"signals.proposed": 1}
    assert "signals.proposed" not in verdict["unreadable_report_only_fields"]["by_field"]
    assert verdict["unreadable_report_only_fields"]["by_field"] == {
        "per_comment.note": len(BY_ID[OWED[0]]["comments"]),
        "signals.signal_type": 1,
    }


def test_a_container_that_is_PRESENT_and_not_a_list_still_REFUSES():
    """Rewriting it to `[]` would answer «this thread dropped nothing» over an unreadable answer.

    Only the `per_comment` and `noise` legs are regressions of the fix — `_tolerate` never rewrote
    `signals`, which has no drop loop, so its leg passes at the pre-fix sha too. It is here because
    the closed refusal set is a claim about ALL THREE containers and a test of two of them is a
    test of two of them ([[a_consumer_list_is_not_a_meaning_list]]).
    """
    for field in ("per_comment", "noise", "signals"):
        payload = json.loads(reply())
        payload[field] = {"a": {"msg_id": 7}}  # a map keyed by something that is not a msg_id
        with pytest.raises(prompts.ParseError, match=f"{field} is not a list"):
            pass2_r2.parse_pass2(json.dumps(payload, ensure_ascii=False), unit=unit())
    # and the sitting's own `{}` -> `[]` repair is untouched
    assert pass2_r2.parse_pass2(reply(noise={}), unit=unit())["noise"] == []


def test_the_runner_REFUSES_an_ABSENT_seed_file(tmp_path):
    """Staging does `rm -rf /workspace/run`, so absence is the DEFAULT state of the run directory.

    The first version returned `[]` for a missing out-file and skipped the whole check, so a seed
    whose scp failed left a pod that bought all 79 and re-bought the four r1 paid for.
    """
    with pytest.raises(SystemExit, match="does not exist and the pack names"):
        runner.carried(tmp_path / "never-copied.jsonl", PACK)
    empty = tmp_path / "empty.jsonl"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(SystemExit, match="is empty and the pack names"):
        runner.carried(empty, PACK)
    # the two states say DIFFERENT things: from the pod log alone, «the scp silently failed» and
    # «the seed is there but empty» need different next steps

    # and the refusal happens through main(), BEFORE the loader is ever called
    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps(PACK, ensure_ascii=False), encoding="utf-8")
    loaded = []
    with pytest.raises(SystemExit, match="does not exist and the pack names"):
        runner.main(
            [
                "--pack",
                str(pack),
                "--outdir",
                str(tmp_path / "empty-run"),
                "--repo",
                str(REPO_ROOT),
            ],
            loader=lambda *a, **kw: loaded.append(1),
        )
    assert loaded == [], "the model must not be loaded — that is 450 s and about $0.09"

    # a TORN LAST line is the mid-write race and not a damaged file
    torn = tmp_path / "torn.jsonl"
    torn.write_text(
        (RESULTS / OUT_NAME).read_text(encoding="utf-8") + '{"id": "@x:1", "sec', encoding="utf-8"
    )
    assert runner.carried(torn, PACK) == sorted(CARRIED)
    damaged = tmp_path / "damaged.jsonl"
    damaged.write_text(
        '{"id": "@x:1", "sec\n' + (RESULTS / OUT_NAME).read_text(encoding="utf-8"), encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="damaged file"):
        runner.carried(damaged, PACK)


def test_rung_7_is_RED_when_the_carried_split_disagrees_with_the_pack(tmp_path, monkeypatch):
    """A thread the pod RE-BOUGHT carries no `carried_from`, and the census must say so."""
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.window, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    out = tmp_path / OUT_NAME
    whole_run(out)
    rows = [json.loads(one) for one in out.read_text(encoding="utf-8").splitlines() if one.strip()]
    for one in rows:
        one.pop("carried_from", None)  # the seed never landed: the pod bought all 79
    out.write_text(
        "".join(json.dumps(one, ensure_ascii=False) + "\n" for one in rows), encoding="utf-8"
    )
    verdict = gate.completeness(
        RECORD,
        json.loads(record.read_text(encoding="utf-8")),
        PACK,
        tmp_path,
        gate.window.stamp("2026-08-22T12:00:00+00:00"),
    )
    assert verdict["verdict"] == "RED"
    assert verdict["carried_count"] == 0
    assert verdict["bought_by_this_pod"] == 79
    assert verdict["carried_disagreement"] == sorted(CARRIED)


def test_the_smoke_D2_publishes_is_the_RECORDs_five_calls_and_not_the_four_carried_rows(
    tmp_path, monkeypatch
):
    """r1's smoke was FIVE calls and only four are carried — the fifth is the one r2 re-buys."""
    out = tmp_path / OUT_NAME
    whole_run(out)
    monkeypatch.setattr(scoring, "EVIDENCE", out)
    monkeypatch.setattr(scoring, "RUN", tmp_path / "run.json")
    (tmp_path / "run.json").write_text(json.dumps({"pods": [], "gates": []}), encoding="utf-8")
    ng = scoring.build()["non_gating"]
    assert ng["r1_smoke_units"] == 5
    assert ng["r1_smoke_mean"] == 45.582
    assert ng["r1_smoke_max"] == 58.07
    assert 15.801 in ng["r1_smoke_seconds"], "the fastest of the five, and the one not carried"
    assert (
        ng["r1_smoke_seconds"]
        == RECORD["money"]["arithmetic"]["seconds_per_call"]["smoke"]["seconds"]
    )


def test_the_WATCH_command_runs_end_to_end_on_a_fake_transport(tmp_path, monkeypatch, capsys):
    """The last gate COMMAND, and it needed only a fake `scp` to be drivable at $0."""
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.window, "RECORD", record)
    monkeypatch.setattr(gate.window, "registration", lambda: RECORD)
    monkeypatch.setattr(gate, "POD_LOG", tmp_path / "pod.log")
    monkeypatch.setattr(gate.window, "POD_LOG", tmp_path / "pod.log")
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    (tmp_path / "pod.log").write_text("boot\n", encoding="utf-8")
    bought_rows(tmp_path / OUT_NAME, OWED, 30.0)
    copied = []
    monkeypatch.setattr(
        gate.window,
        "scp",
        lambda ssh, port, remote, local: copied.append((remote, Path(local).name)),
    )
    monkeypatch.setattr(gate.window, "pod_delete", lambda pod_id: {"deleted": pod_id})
    code = gate.main(
        ["--watch", "--ssh", "root@h", "--ssh-port", "1", "--outdir", str(tmp_path), "--poll", "0"],
        gate.window.stamp("2026-08-22T10:20:00+00:00"),
    )
    assert code == gate.GO
    state = json.loads(record.read_text(encoding="utf-8"))
    assert state["gates"][-1]["kind"] == "watch"
    assert state["gates"][-1]["answered"] == 75 and state["gates"][-1]["owed"] == 75
    assert state["gates"][-1]["legs"][0]["carried_rows_in_the_file"] == 4
    assert copied == [
        ("/workspace/run/pass2_signals_r2_v1.jsonl", OUT_NAME),
        ("/workspace/run/launched_at", gate.LAUNCH_STAMP),
        ("/workspace/run/pod.log", "pod.log"),
    ], "the launch stamp is RENAMED on the way back and the gate is what fixes both names"
    capsys.readouterr()


def create_line(text: str) -> str:
    """The `pod create` COMMAND, and not the `--help` line step 0 uses to check the CLI's flags."""
    return next(
        one for one in text.split("runpodctl pod create")[1:] if one.lstrip().startswith("--name")
    ).split("```", 1)[0]


def test_the_runbook_create_line_is_r1s_OWN_line_flags_AND_values():
    """`runpodctl pod create` rejects a camelCase spelling at parse time, and the natural repair
    of a create that will not parse is a retyped line without `--terminate-after` — rung 6.

    Names AND values: a drifted `--image` or `--network-volume-id` parses cleanly, the pod is
    created, the meter starts, and the failure surfaces as a cold volume at ~$0.10 of billed time.
    """
    create = create_line(RUNBOOK)
    for flag in (
        "--gpu-id",
        "--gpu-count",
        "--network-volume-id",
        "--image",
        "--container-disk-in-gb",
        "--data-center-ids",
        "--cloud-type",
        "--ports",
        "--ssh",
        "--terminate-after",
    ):
        assert flag in create, flag
    for invented in (
        "--gpuType",
        "--gpuCount",
        "--networkVolumeId",
        "--imageName",
        "--containerDiskSize",
    ):
        assert invented not in RUNBOOK, invented

    r1 = create_line(
        (REPO_ROOT / "scripts" / "runbook_pass2_signals.md").read_text(encoding="utf-8")
    )

    def pairs(line: str) -> dict:
        found, tokens = {}, re.findall(r"--[a-z-]+(?:\s+'[^']*'|\s+[^\s\\]+)?", line)
        for token in tokens:
            flag, _, value = token.partition(" ")
            found[flag] = value.strip().strip("'")
        return found

    mine, theirs = pairs(create), pairs(r1)
    assert set(mine) == set(theirs)
    moved = {flag for flag in mine if mine[flag] != theirs[flag]}
    assert moved == {"--name"}, (
        f"«changed only in the pod's name» — these also moved: {sorted(moved)}"
    )
    assert mine["--name"] == "mp-pass2-signals-r2"
    # and the volume and the card are the ones r1's pod actually ran on
    ran = json.loads((RESULTS / "pass2_signals_run.json").read_text(encoding="utf-8"))["pods"][0]
    assert ran["card"] in mine["--gpu-id"]


def test_step_0_makes_the_operator_ask_the_CLI_and_look_for_a_stray_run_record():
    """Two $0 checks the review paid for: CLI drift is silent, and a driver can leave a run record.

    A leftover `results/pass2_signals_r2_run.json` holding a TEST fixture pod with no `deleted_at`
    makes rung 0 return KILL before the first legitimate create, with an instruction to delete a
    pod that never existed.
    """
    step_zero = RUNBOOK.split("## 0 —", 1)[1].split("## 1 —", 1)[0]
    assert "runpodctl pod create --help" in step_zero
    assert "results/pass2_signals_r2_run.json" in step_zero
    assert "runpodctl-ssh-key" in step_zero, (
        'six scp/ssh lines spell -i "$SSHK" and nothing defined it. It is the key every paid'
        " session of this repo has used, named in five other runbooks and dropped from r1's"
    )
    assert "-i $SSHK" not in RUNBOOK, "unquoted, an unset $SSHK makes -i swallow the next -o"
    # the same key five other runbooks of this repo name, and it is on disk
    other = (REPO_ROOT / "scripts" / "runbook_pass1_window_r2.md").read_text(encoding="utf-8")
    assert "~/.runpod/ssh/runpodctl-ssh-key" in other


def test_the_record_carries_no_clause_about_a_rung_r2_REPEALED():
    """r1's `under_a_STOP` text described a rung `main()` now raises on."""
    for bar in ("2_entity_cases", "3_noise"):
        clause = RECORD["bars"][bar]["under_a_STOP"]
        assert "REPEALED WITH THE RUNG" in clause, bar
        assert "rung 7 is RED" in clause, bar
    assert list(RECORD["bars"]["completeness"]["arms"]) == ["GO"]


def test_EVERY_census_in_D2_is_keyed_on_the_carried_FIELD(tmp_path, monkeypatch):
    """`unreadable_table.on_carried_rows` was the last one still asking the pack's id list."""
    out = tmp_path / OUT_NAME
    whole_run(out)
    rows = [json.loads(one) for one in out.read_text(encoding="utf-8").splitlines() if one.strip()]
    for one in rows:
        one.pop("carried_from", None)  # the seed never landed: the pod bought all 79
    out.write_text(
        "".join(json.dumps(one, ensure_ascii=False) + "\n" for one in rows), encoding="utf-8"
    )
    monkeypatch.setattr(scoring, "EVIDENCE", out)
    monkeypatch.setattr(scoring, "RUN", tmp_path / "run.json")
    (tmp_path / "run.json").write_text(json.dumps({"pods": [], "gates": []}), encoding="utf-8")
    verdict = scoring.build()
    assert verdict["evidence"]["units_carried_from_r1"] == 0
    assert verdict["evidence"]["carried_disagreement"] == sorted(CARRIED)
    assert verdict["unreadable_report_only_fields"]["rows"] > 0, "there is something to attribute"
    assert verdict["unreadable_report_only_fields"]["on_carried_rows"] == 0, (
        "one verdict may not say «0 carried» in one table and attribute rows to r1 in the next"
    )
    assert verdict["non_gating"]["units_bought"] == 79


def test_the_FIFTH_red_cause_of_rung_7_is_REGISTERED_and_not_only_coded():
    """A bar may not go RED for a reason the pre-registration does not carry."""
    rule = RECORD["bars"]["completeness"]["rule"]
    assert "All FIVE, or RED" in rule
    assert "carried_from" in rule
    assert RECORD["bars"]["completeness"]["the_fifth_condition"]
    runbook = RUNBOOK.split("## 6 —", 1)[1]
    assert "FIVE conditions" in runbook
    assert "carried_from" in runbook


def test_the_cost_sentence_carries_r1s_own_step_and_not_only_pass_1s():
    """r1's sentence said «pass 1 + this step» and meant ITS step."""
    line = RECORD["bars"]["report_only"]["the_cost_of_the_signal_layer"]
    assert "0.742055" in line and "0.108122" in line and "0.312592" in line


def test_leg_state_prints_BOTH_carried_counts_so_a_missing_seed_is_visible(tmp_path, monkeypatch):
    """`legs_of` cannot ask `carried_from` — it is handed a pack. The watch line shows both."""
    record = tmp_path / "run.json"
    monkeypatch.setattr(gate.window, "RECORD", record)
    record.write_text(json.dumps(state_with_pod()), encoding="utf-8")
    out = tmp_path / OUT_NAME
    bought_rows(out, OWED[:3], 20.0)
    legs = gate.leg_state(RECORD, [PACK], tmp_path)
    assert legs[0]["carried_rows_in_the_file"] == 4
    assert legs[0]["carried_rows_the_pack_names"] == 4
    # the same file with the carried rows stripped: the two counts part, on every poll
    rows = [json.loads(one) for one in out.read_text(encoding="utf-8").splitlines() if one.strip()]
    out.write_text(
        "".join(
            json.dumps({k: v for k, v in one.items() if k != "carried_from"}, ensure_ascii=False)
            + "\n"
            for one in rows
        ),
        encoding="utf-8",
    )
    legs = gate.leg_state(RECORD, [PACK], tmp_path)
    assert legs[0]["carried_rows_in_the_file"] == 0 and legs[0]["carried_rows_the_pack_names"] == 4


def test_D2_publishes_the_smokes_per_thread_seconds_and_the_ONE_paired_thread(
    tmp_path, monkeypatch
):
    """The two means are over different threads; the paired thread is the size-free reading."""
    out = tmp_path / OUT_NAME
    whole_run(out)
    monkeypatch.setattr(scoring, "EVIDENCE", out)
    monkeypatch.setattr(scoring, "RUN", tmp_path / "run.json")
    (tmp_path / "run.json").write_text(json.dumps({"pods": [], "gates": []}), encoding="utf-8")
    ng = scoring.build()["non_gating"]
    assert set(ng["r1_smoke_per_thread"]) == set(CARRIED) | {F2}
    paired = ng["the_one_paired_thread"]
    assert paired["id"] == F2
    assert paired["r1_seconds"] == 15.801
    assert paired["this_pod_seconds"] is not None, "r2 re-buys it, so both sides have a reading"
    assert "composition" in ng["the_two_means_are_over_different_threads"]
