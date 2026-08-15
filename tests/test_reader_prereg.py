"""`results/prereg_reader_probe.json` — the registration, checked before it can be spent against.

A pre-registration is only worth what its re-derivation is worth: every threshold here is the
operator's word, every sha is a live file, and the one arithmetic claim it makes — what «≥ 0.80»
means over thirteen rows — is recomputed rather than read.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import reader_population as population  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_reader_prereg as prereg  # noqa: E402

from market_pulse import local_llm, prompts, scorer  # noqa: E402

RECORD_PATH = REPO_ROOT / "results" / "prereg_reader_probe.json"
RECORD = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1.json").read_text(encoding="utf-8"))


def test_the_committed_registration_is_what_the_producer_writes_today(tmp_path):
    """No clock is stamped, so the record re-derives byte for byte and its date is the date of the
    commit that carries it — which is also the only witness that it preceded the endpoint."""
    out = tmp_path / "again.json"
    assert prereg.main(["--out", str(out)]) == 0
    assert out.read_bytes() == RECORD_PATH.read_bytes()
    assert "generated_at" not in RECORD_PATH.read_text(encoding="utf-8")


def test_the_population_is_pinned_as_a_list_and_not_as_a_count():
    """111 is a count and a count cannot be run. The digest is over the enumeration itself, so a
    population that quietly became another 111 threads breaks the pin."""
    kept = population.population()
    assert RECORD["population"]["enumeration"]["digest"] == prereg.population_digest(kept)
    assert RECORD["population"]["sha256"] == population.census_sha256()
    assert (RECORD["population"]["threads"], RECORD["population"]["payable_comments"]) == (111, 912)
    assert prereg.population_digest(kept[:-1]) != RECORD["population"]["enumeration"]["digest"]


def test_every_instrument_is_pinned_by_the_bytes_it_will_run_with():
    instruments = RECORD["instruments"]
    assert instruments["task"] == prompts.READER_TASK
    assert instruments["prompt_sha256"] == prompts.prompt_sha256(prompts.READER_TASK)
    assert instruments["scorer"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "src" / "market_pulse" / "scorer.py"
    )
    assert instruments["parser"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "src" / "market_pulse" / "prompts.py"
    )
    for name in instruments["scorer"]["functions"]:
        assert callable(getattr(scorer, name)), name
    for name, digest in RECORD["authority"].items():
        assert summary.sha256_of(REPO_ROOT / name) == digest, name
    for name, digest in RECORD["producer"]["borrowed"].items():
        assert summary.sha256_of(REPO_ROOT / name) == digest, name


def test_the_ceilings_and_the_serving_block_are_the_code_and_the_rulings():
    ceilings = RECORD["instruments"]["ceilings"]
    assert ceilings["input_chars"] == prompts.READER_MAX_INPUT_CHARS
    assert ceilings["output_tokens"] == local_llm.READER_MAX_NEW_TOKENS
    assert ceilings["input_chars"] > RECORD["population"]["sizes"]["rendered_chars"]["max"]
    serving = RECORD["instruments"]["serving"]
    # the two things that are OFF and asserted, and the two that fix the measurement
    assert serving["adapter"] is None and serving["merge_state"] == "base-no-adapter"
    assert serving["chat_template"] == dict(local_llm.CHAT_TEMPLATE)
    assert serving["chat_template"]["enable_thinking"] is False
    assert serving["forward_batch_size"] == 1 and serving["do_sample"] is False
    assert serving["model"] == local_llm.MODEL_ID
    assert serving["quantization"] == dict(local_llm.QUANTIZATION)


def test_the_bar_that_carries_a_threshold_carries_its_arithmetic():
    """«≥ 0.80» over thirteen rows is eleven, not ten: 10/13 is 0.769. A threshold read off a
    percentage and never divided is how a bar passes on a number below it
    ([[relative_thresholds_can_exceed_the_metric]], the same trap from the other side)."""
    bar = RECORD["bars"]["4_per_comment_agreement"]
    rows = bar["scored_over"]
    assert len(rows) == 13
    assert 11 / 13 >= prereg.AGREEMENT_BAR > 10 / 13
    assert "the bar is 11 of 13 (0.846) — 10 agreements scores 0.769 and fails" in bar["arithmetic"]
    assert bar["threshold"] == "rate >= 0.8"
    assert set(rows) == set(GOLD["reachability"]["per_comment"]["inside_the_population"])
    assert bar["unreachable"] == [578951]


def test_each_bar_partitions_the_golds_cases_and_names_every_exclusion():
    """Nothing may fall out of a bar silently. Every case of the gold is either scored, unreachable
    with a measured cause, or excluded with a stated one."""
    entities = RECORD["bars"]["2_entity_cases"]
    assert entities["scored_over"] == ["E2", "E3"]
    assert sorted(entities["unreachable"]) == ["E1", "E4a", "E4b"]
    assert entities["the_contract_asked_for"] == "4 of 4"
    for cause in entities["unreachable"].values():
        assert cause["passes_the_gate_with_no_silencer"] is True
        assert cause["removed_by"] == ["varto_rule"]
    noise = RECORD["bars"]["3_noise"]
    assert noise["scored_over"] == ["N2", "N4", "N5", "N6"]
    assert sorted(noise["unreachable"]) == ["N3"]
    assert sorted(noise["excluded_with_cause"]) == ["N1"]
    everything = {one["id"] for one in GOLD["noise_threads"]}
    assert everything == set(noise["scored_over"]) | set(noise["unreachable"]) | set(
        noise["excluded_with_cause"]
    )
    cases = {one["id"] for one in GOLD["entity_cases"]}
    assert cases == set(entities["scored_over"]) | set(entities["unreachable"])
    flagships = RECORD["bars"]["1_flagships"]
    assert flagships["scored_over"] == ["F1", "F2", "F3", "F4", "F5"]
    # five cases, seven signals — F1 alone carries three, and the case reading demands all of them
    assert flagships["gold_signals"] == ["F1a", "F1b", "F1c", "F2a", "F3a", "F4a", "F5a"]


def test_the_warm_up_is_drawn_from_the_middle_and_is_reproducible():
    """Three threads, three distinct ranks, all inside the middle third of the population by size —
    and never the head, because a registered price names its sample."""
    kept = population.population()
    drawn = RECORD["go_no_go"]["warm_up"]["drawn"]
    assert prereg.draw(kept) == drawn
    ranks = [one["rank_by_size"] for one in drawn]
    assert len(set(ranks)) == 3
    band = {(one["channel"], one["post_id"]) for one in prereg.middle_third(kept)}
    for one in drawn:
        assert (one["channel"], one["post_id"]) in band
        assert one["rendered_chars"] < prompts.READER_MAX_INPUT_CHARS
    assert min(ranks) >= len(kept) // 3
    assert 0 not in ranks and len(kept) - 1 not in ranks
    assert RECORD["go_no_go"]["warm_up"]["threads"] == 3 == len(drawn)


def test_the_stop_rule_names_both_ceilings_and_what_a_stop_costs():
    money = RECORD["money"]
    assert money["cap_usd_all_in"] == prereg.CAP_USD == 0.20
    bar = RECORD["bars"]["5_time_and_cost"]["thresholds"]
    assert bar == {"cap_usd_all_in": 0.20, "window_minutes_billed": 30.0}
    assert "STOP before any further call" in RECORD["go_no_go"]["stop_rule"]
    assert RECORD["go_no_go"]["what_a_stop_costs"].startswith("the warm-up's own spend")
    assert "ONE attempt, no retry" in RECORD["attempt"]
    frozen = RECORD["frozen_when_the_endpoint_exists"]
    assert "results/prereg_reader_probe.json" in frozen
    assert "results/reader_gold_w1.json" in frozen


def test_the_non_gating_column_keeps_the_empty_class_apart_from_the_failures():
    """«нет сигнала» and «the reply could not be read» are two answers, and the second one piles up
    exactly where the first is counted ([[the_empty_class_eats_the_parse_failures]])."""
    assert any("apart from replies that failed to parse" in one for one in RECORD["non_gating"])
    assert any("parse failures by reason" in one for one in RECORD["non_gating"])


@pytest.mark.parametrize(
    "name", ["1_flagships", "2_entity_cases", "3_noise", "4_per_comment_agreement"]
)
def test_every_gating_bar_names_the_scorer_function_that_computes_it(name):
    """The single judge of SPEC §5: a bar computed anywhere but in the scorer is a second scorer."""
    assert RECORD["bars"][name]["scorer"] in RECORD["instruments"]["scorer"]["functions"]
