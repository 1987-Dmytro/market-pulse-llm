"""`results/prereg_reader_probe_v3.json` — the A+B registration, checked before it can be spent.

A pre-registration is worth what its re-derivation is worth. Every threshold here is the operator's
word, every sha is a live file, and the three claims it makes that a reader cannot check by eye —
what the parser's v3 behaviour IS, what bar 3's fixed predicate does to probe-b's own rows, and how
much slower than probe-b this run may be and still fit the cap — are recomputed rather than read.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_census_w1_reader as reader_cell  # noqa: E402
import probe_b_population as subset  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_reader_prereg_v3 as prereg  # noqa: E402
from test_prompts import (  # noqa: E402
    assert_pinned,
    put_the_sealed_shas_back,
    sealed_sha256,
)

from market_pulse import local_llm, prompts, scorer  # noqa: E402

RECORD_PATH = REPO_ROOT / "results" / "prereg_reader_probe_v3.json"
RECORD = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text(encoding="utf-8"))
PROBE_B_VERDICT = json.loads(
    (REPO_ROOT / "results" / "reader_probe_b_verdict.json").read_text(encoding="utf-8")
)
PROBE_B_ROWS = [
    json.loads(line)
    for line in (REPO_ROOT / "results" / "reader_probe_b_w1.jsonl")
    .read_text(encoding="utf-8")
    .splitlines()
    if line
]


def test_the_committed_registration_is_what_the_producer_writes_today(tmp_path):
    """No clock is stamped, so the record re-derives byte for byte and its date is the date of the
    commit that carries it — which is also the only witness that it preceded the endpoint."""
    out = tmp_path / "again.json"
    assert prereg.main(["--out", str(out)]) == 0
    # `producer.borrowed` is hashed LIVE and `src/market_pulse/prompts.py` moved when v5 registered
    # a fourth reader text. This record froze when v3's endpoint existed and is NOT re-pinned: the
    # one byte range allowed to differ is put back to the sealing commit's, and the swap must fire
    # TWICE in this record: `instruments.parser.sha256` and `producer.borrowed`
    rebuilt = put_the_sealed_shas_back(out.read_bytes(), times=2)
    # and this producer derives `instruments.prompt_sha256` LIVE over `prompts.READER`, so a rebuild
    # today gains the fourth text. The record's own `prompt_rule` says that is expected — «a text
    # registered LATER is not in this map and is not expected to be» — so the later entry is dropped
    # before the comparison, and the drop must FIRE
    later = (
        f',\n      "{prompts.READER_TASK_V5}": "{prompts.prompt_sha256(prompts.READER_TASK_V5)}"'
    ).encode()
    assert rebuilt.count(later) == 1, "the fourth text is not where the repair expects it"
    assert rebuilt.replace(later, b"") == RECORD_PATH.read_bytes()
    assert "generated_at" not in RECORD_PATH.read_text(encoding="utf-8")


def test_it_supersedes_v2_by_sha_and_refuses_to_attribute_the_gain():
    """One registration and not two. The sitting took A and B together and bought no ablation
    between them, so the record has to SAY that where a reader of the result will find it — a report
    that implied the recovered replies were the parser's would be claiming a measurement nobody
    made."""
    older = RECORD["supersedes"]
    assert older["record"] == "results/prereg_reader_probe_v2.json"
    assert older["sha256"] == summary.sha256_of(REPO_ROOT / older["record"])
    assert "ruling 2" in older["ruling"]
    assert len(older["what_it_changes"]) == 4
    assert "may NOT be attributed" in older["no_ablation"]
    # what it keeps is not a slogan: the scorer really is the same bytes v1 and v2 registered
    v2 = json.loads((REPO_ROOT / older["record"]).read_text(encoding="utf-8"))
    assert RECORD["instruments"]["scorer"]["sha256"] == v2["instruments"]["scorer"]["sha256"]
    assert RECORD["money"]["cap_usd_all_in"] == v2["money"]["cap_usd_all_in"] == 0.35


def test_the_population_is_probe_bs_own_and_the_digest_did_not_move():
    """The pairing the whole registration rests on. The digest is a LITERAL in the producer that the
    computed one must match, so a population that quietly became another 23 threads refuses instead
    of re-pinning itself."""
    kept = subset.population()
    pop = RECORD["population"]
    assert (
        prereg.POPULATION_DIGEST
        == "ccef35fa4b9c771fd62506cd7878177f8184c8344702ad1d05c3bec33abbc1f3"
    )
    assert pop["enumeration"]["digest"] == subset.digest(kept) == prereg.POPULATION_DIGEST
    assert (pop["threads"], pop["payable_comments"]) == (23, 134)
    listed = pop["enumeration"]["threads"]
    assert len(listed) == 23
    for one, built in zip(listed, kept, strict=True):
        assert one["thread"] == subset.key(built["channel"], built["post_id"])
        assert one["msg_ids"] == [row["msg_id"] for row in built["comments"]]
        assert one["rendering_sha256"] != "", one["thread"]
    # a thread dropped from the enumeration has to move the digest, or it is not a pin
    assert subset.digest(kept[:-1]) != prereg.POPULATION_DIGEST


def test_the_new_cell_status_is_enumerated_per_thread_and_outside_the_digest():
    """Dv399 — enumerate, do not estimate. And the status is recorded BESIDE the pin: the digest
    line carries `gated|injected` from probe-b's cell, so folding today's cell into it would move the
    digest and end the pairing."""
    cell = RECORD["population"]["under_the_reader_census_cell"]
    live = {f"{one['channel']}:{one['post_id']}" for one in reader_cell.population()}
    listed = RECORD["population"]["enumeration"]["threads"]

    assert cell["cell"] == reader_cell.CELL
    assert cell["sha256"] == summary.sha256_of(reader_cell.OUT)
    for one in listed:
        assert one["in_the_reader_census_cell"] is (one["thread"] in live), one["thread"]
    assert cell["in_the_cell"] == 23 and cell["outside_the_cell"] == []
    # all four of probe-b's injected threads enter — N3 included, which the contract expected to
    # stay injectable. Measured, and the record says the expectation was wrong
    injected = [one["thread"] for one in listed if one["injected_under_probe_b"]]
    assert sorted(injected) == sorted(subset.INJECTED)
    assert sorted(cell["injected_under_probe_b_that_now_enter"]) == sorted(subset.INJECTED)
    assert "WRONG, measured" in cell["measured"]
    # and the payable lists are the SAME under both cells, checked per thread
    assert cell["payable_lists_unchanged"] is True
    assert all(one["payable_list_unchanged_by_the_cell"] for one in listed)
    # the digest's own line still says what probe-b's cell said, or the pairing is gone
    assert "gated|injected" in RECORD["population"]["enumeration"]["digest_rule"]


def test_the_parser_block_is_re_derived_from_the_module_and_driven():
    """The registration states the parser's behaviour, so the statement has to be the code's and not
    a description of it: every repair name is built from `prompts`' own constants, and every one of
    them is made to FIRE here on a reply that produces it."""
    parser = RECORD["instruments"]["parser"]
    assert_pinned("src/market_pulse/prompts.py", parser["sha256"])
    assert parser["function"] == "parse_reply"
    assert parser["repairable_fields"] == list(prompts.READER_LIST_FIELDS)

    verdict = {
        "thread": {"channel": "@c", "post_id": 1},
        "post_summary": "п",
        "discussion_summary": "д",
        "entities": [],
        "signals": [],
        "per_comment": [],
        "noise": [],
    }

    def parse(payload: dict) -> dict:
        return prompts.parse_reply(prompts.READER_TASK_V3, json.dumps(payload, ensure_ascii=False))

    repairs = parser["repairs"]
    # 1 — two objects merged, and the disagreement refused
    head = {key: verdict[key] for key in ("thread", "post_summary", "discussion_summary")}
    tail = {key: verdict[key] for key in prompts.READER_LIST_FIELDS}
    split = f"{json.dumps(head, ensure_ascii=False)}\n{json.dumps(tail, ensure_ascii=False)}"
    assert prompts.parse_reply(prompts.READER_TASK_V3, split)["repairs"] == [
        repairs["1_two_top_level_objects"]["logs"]
    ]
    clash = json.dumps({**head, "post_summary": "інше"}, ensure_ascii=False)
    with pytest.raises(prompts.ParseError, match="two disagreeing objects: post_summary"):
        prompts.parse_reply(
            prompts.READER_TASK_V3, f"{json.dumps(head, ensure_ascii=False)}\n{clash}"
        )
    assert "two disagreeing objects: <key>" in repairs["1_two_top_level_objects"]["refuses_when"]

    # 2 and 3 — one logged name per repairable field, every one of them produced
    for field in prompts.READER_LIST_FIELDS:
        empty = parse({**verdict, field: {}})
        assert empty["repairs"] == [f"{field}: empty object -> empty list"]
        assert empty["repairs"][0] in repairs["2_empty_object_for_an_empty_list"]["logs"]
    mapped = parse({**verdict, "noise": {"47896": {"msg_id": 47896, "class": "плюс_спам"}}})
    assert mapped["repairs"] == ["noise: map keyed by msg_id -> list"]
    assert mapped["repairs"][0] in repairs["3_map_keyed_by_msg_id"]["logs"]
    assert mapped["noise"] == [{"msg_id": 47896, "class": "плюс_спам"}]

    # the refuse list, each reason produced by the parser itself
    signal = {
        "signal_type": "жалоба",
        "subject_type": "сеть_ритейлер",
        "aspect": "quality",
        "reading": "р",
        "evidence": [1],
        "quote": "ц",
    }
    produced = {}
    for payload in (
        {**verdict, "signals": [{**signal, "aspect": None}]},
        {
            **verdict,
            "signals": [
                {**{k: v for k, v in signal.items() if k != "evidence"}, "from_post": True}
            ],
        },
    ):
        with pytest.raises(prompts.ParseError) as err:
            parse(payload)
        produced[err.value.reason] = True
    with pytest.raises(prompts.ParseError) as err:
        prompts.parse_reply(prompts.READER_TASK_V3, '"entities": [], "signals": []')
    produced[err.value.reason] = True
    assert set(parser["refuses"]) == set(produced)


def test_bar_three_is_counted_over_answers_and_probe_bs_own_rows_show_why():
    """probe-b finding 2, tested where it happened. Its bar 3 passed with «0 signals» over five
    threads of which FOUR had no verdict at all — the only gate that cleared, computed over one
    actual answer. The registered predicate is applied to the same rows and does not pass."""
    bar = RECORD["bars"]["3_noise"]
    assert bar["threshold"] == "0 signals"
    assert "counted over the threads that HAVE a parsed verdict" in bar["rule"]
    assert "NEVER a zero" in bar["rule"] and "UNREACHABLE" in bar["rule"]
    assert bar["producer"].startswith("scripts/write_reader_prereg_v3.py::bar_three_over_answers")

    as_scored = PROBE_B_VERDICT["bars"]["3_noise"]["result"]
    assert as_scored["passed"] is True and as_scored["signals"] == 0 and as_scored["threads"] == 5

    answered = {row["thread"] for row in PROBE_B_ROWS if row["parsed"]}
    now = prereg.bar_three_over_answers(as_scored["per_thread"], answered)
    assert now["threads_registered"] == 5
    assert now["threads_with_a_verdict"] == 1, "the count the old bar was really over"
    assert sorted(now["threads_refused"]) == [
        "@retsepty:7312",
        "@retsepty:7325",
        "@retsepty:7327",
        "@sashafitnesslife:3939",
    ]
    assert now["reachable"] is True and now["passed"] is True
    assert set(bar["result_must_carry"]) <= set(now)

    # and the state the fix exists for: no verdict at all is UNREACHABLE and never a pass
    none_read = prereg.bar_three_over_answers(as_scored["per_thread"], set())
    assert none_read["reachable"] is False and none_read["passed"] is False
    assert none_read["signals"] == 0, "zero signals, and still not a pass"
    # a signal in an answered thread fails, which is the direction that keeps this a bar
    noisy = prereg.bar_three_over_answers(
        {**as_scored["per_thread"], "@retsepty:7312": 1}, answered | {"@retsepty:7312"}
    )
    assert noisy["passed"] is False and noisy["signals"] == 1


def test_the_other_four_bars_keep_their_thresholds_and_bar_four_reads_gold_r2():
    bars = RECORD["bars"]
    assert bars["1_flagships"]["threshold"] == "5 of 5 cases"
    assert bars["1_flagships"]["scored_over"] == [one["id"] for one in GOLD["flagships"]]
    assert bars["2_entity_cases"]["threshold"] == "4 of 4 cases"
    assert set(bars["2_entity_cases"]["scored_over"]) == {one["id"] for one in GOLD["entity_cases"]}
    assert bars["3_noise"]["scored_over"] == [one["id"] for one in GOLD["noise_threads"]]

    four = bars["4_per_comment_agreement"]
    assert four["threshold"] == f"rate >= {prereg.AGREEMENT_BAR}" == "rate >= 0.8"
    assert four["gold"]["record"] == "results/reader_gold_w1_r2.json"
    assert four["gold"]["sha256"] == summary.sha256_of(prereg.GOLD_R2)
    assert four["scored_over"] == [one["msg_id"] for one in GOLD["per_comment"]]
    assert len(four["scored_over"]) == 14
    # the threshold is COMPUTED, not rounded: 11 of 14 is 0.786 and fails, 12 is 0.857 and passes
    assert 11 / 14 < prereg.AGREEMENT_BAR <= 12 / 14
    assert "12 of 14" in four["arithmetic"]
    # every scorer the bars name is a function that exists
    for bar in bars.values():
        if "scorer" in bar:
            assert callable(getattr(scorer, bar["scorer"])), bar["scorer"]

    assert bars["5_time_and_cost"]["thresholds"] == {"cap_usd_all_in": 0.35}
    assert "finish_reason" in bars["5_time_and_cost"]["reported_not_gating"]


def test_the_money_is_re_derived_from_the_guards_ledger_and_the_runs_own_rows():
    """Setup from the SETTLED entry the guard wrote and never from a report; the rate and the
    seconds re-summed from probe-b's evidence; and the slowdown the cap can absorb computed rather
    than asserted, because that number is what the go/no-go stops on."""
    sums = RECORD["money"]["arithmetic"]
    ledger = json.loads((REPO_ROOT / "results" / "spend_probe_b.json").read_text(encoding="utf-8"))
    settled = [one for one in ledger["gpu_sessions"] if one.get("closed")][-1]["settled_usd"]
    worker = sum(row["seconds"]["worker"] for row in PROBE_B_ROWS)
    rate = sums["rate_usd_per_second"]

    assert sums["setup_usd"] == round(settled - worker * rate, 4)
    assert f"${settled:.6f}" in sums["setup_rule"]
    at = sums["at_probe_bs_measured_4090_rate"]
    assert at["reading_seconds"] == round(worker, 3)
    assert at["seconds_per_thread"] == round(worker / len(PROBE_B_ROWS), 4)
    assert at["reading_usd"] == round(worker * rate, 4)
    assert at["all_in_usd"] == round(sums["setup_usd"] + at["reading_usd"], 4)
    assert at["all_in_usd"] < prereg.CAP_USD and at["verdict"] == "fits the cap"
    assert at["headroom_usd"] == round(prereg.CAP_USD - sums["setup_usd"] - at["reading_usd"], 4)

    buys = (prereg.CAP_USD - sums["setup_usd"]) / rate
    assert sums["seconds_the_cap_buys_after_setup"] == pytest.approx(buys, abs=0.05)
    assert sums["max_slowdown_vs_probe_b"] == pytest.approx(buys / worker, abs=0.002)
    assert sums["max_slowdown_vs_probe_b"] > 1.0, "the run fits, and this is by how much"
    assert "FLOOR and not a forecast" in sums["slowdown_rule"]
    assert "cycle-2" in RECORD["money"]["line"].lower()


def test_every_instrument_is_pinned_by_the_bytes_it_will_run_with():
    instruments = RECORD["instruments"]
    assert instruments["task"] == prompts.READER_TASK_V3 == "reader_thread_gm4_v3"
    # THREE texts, pinned the day this record was written. v5 registered a fourth AFTER it, and the
    # record's own `prompt_rule` says a later text «is not in this map and is not expected to be» —
    # so the pins are checked one by one and the map is a SUBSET of what is registered today
    assert instruments["prompt_sha256"] == {
        task: prompts.prompt_sha256(task)
        for task in (prompts.READER_TASK, prompts.READER_TASK_V2, prompts.READER_TASK_V3)
    }
    assert set(instruments["prompt_sha256"]) < set(prompts.READER)
    assert prompts.READER_TASK_V5 not in instruments["prompt_sha256"]
    assert instruments["scorer"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "src" / "market_pulse" / "scorer.py"
    )
    assert instruments["ceilings"]["input_chars"] == prompts.READER_MAX_INPUT_CHARS
    assert instruments["ceilings"]["output_tokens"] == local_llm.READER_MAX_NEW_TOKENS
    for name, digest in RECORD["authority"].items():
        assert summary.sha256_of(REPO_ROOT / name) == digest, name
    for name, digest in RECORD["producer"]["borrowed"].items():
        assert_pinned(name, digest)
    assert RECORD["producer"]["borrowed"]["src/market_pulse/prompts.py"] == sealed_sha256(
        "src/market_pulse/prompts.py"
    )
    assert RECORD["producer"]["sha256"] == summary.sha256_of(
        REPO_ROOT / RECORD["producer"]["script"]
    )


def test_the_serving_block_is_probe_bs_own_and_names_the_card():
    """Unchanged, and QUOTED from the registration that carries it rather than retyped: two copies
    of a serving configuration are two configurations that can disagree."""
    v2 = json.loads((REPO_ROOT / "results" / "prereg_reader_probe_v2.json").read_text("utf-8"))
    serving = RECORD["instruments"]["serving"]
    assert serving == v2["instruments"]["serving"]
    assert serving["serving_config"] == "READER"
    assert serving["adapter"] is None and serving["merge_state"] == "base-no-adapter"
    assert serving["forward_batch_size"] == 1 and serving["do_sample"] is False
    assert serving["gpu_class_preference"][0] == "ADA_24"
    assert serving["chat_template"] == dict(local_llm.CHAT_TEMPLATE)
    assert "NAMED in every projection" in RECORD["instruments"]["serving_rule"]


def test_what_the_record_freezes_and_what_it_reports_beside_the_bars():
    frozen = RECORD["frozen_when_the_endpoint_exists"]
    assert "results/prereg_reader_probe_v3.json" in frozen
    assert "results/reader_gold_w1_r2.json" in frozen
    assert "results/gate_census_w1_reader.json" in frozen
    assert f"the {prompts.READER_TASK_V3} prompt text" in frozen
    assert "may not edit it" in RECORD["class"]

    beside = " ".join(RECORD["non_gating"])
    for promised in ("repairs", "finish_reason", "31.6376", "no ablation"):
        assert promised in beside, promised
    assert RECORD["attempt"].startswith("ONE attempt, no retry")
