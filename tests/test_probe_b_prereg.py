"""`results/prereg_reader_probe_v2.json` — the registration, checked before it can be spent against.

A pre-registration is worth what its re-derivation is worth. Every threshold here is the operator's
word, every sha is a live file, and the two arithmetic claims it makes — what «≥ 0.80» means over
fourteen rows, and how much faster than probe-a's L4 a card has to be for this population to fit the
cap — are recomputed rather than read.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import probe_b_population as subset  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_reader_prereg_v2 as prereg  # noqa: E402

from market_pulse import local_llm, prompts, scorer  # noqa: E402

RECORD_PATH = REPO_ROOT / "results" / "prereg_reader_probe_v2.json"
RECORD = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1.json").read_text(encoding="utf-8"))


def test_the_committed_registration_is_what_the_producer_writes_today(tmp_path):
    """No clock is stamped, so the record re-derives byte for byte and its date is the date of the
    commit that carries it — which is also the only witness that it preceded the endpoint."""
    out = tmp_path / "again.json"
    assert prereg.main(["--out", str(out)]) == 0
    assert out.read_bytes() == RECORD_PATH.read_bytes()
    assert "generated_at" not in RECORD_PATH.read_text(encoding="utf-8")


def test_it_supersedes_v1_by_sha_and_says_what_it_keeps():
    """A superseding record that did not name the one it replaces would be a second registration of
    the same probe, and nothing could say which one a result was measured under."""
    older = RECORD["supersedes"]
    assert older["record"] == "results/prereg_reader_probe.json"
    assert older["sha256"] == summary.sha256_of(REPO_ROOT / older["record"])
    assert "operator 2026-08-15" in older["ruling"]
    assert len(older["what_it_changes"]) == 3
    # what it keeps is not a slogan: the scorer really is the same bytes v1 registered
    v1 = json.loads((REPO_ROOT / older["record"]).read_text(encoding="utf-8"))
    assert RECORD["instruments"]["scorer"]["sha256"] == v1["instruments"]["scorer"]["sha256"]
    assert RECORD["instruments"]["gold"]["sha256"] == v1["instruments"]["gold"]["sha256"]
    assert (
        RECORD["bars"]["4_per_comment_agreement"]["threshold"]
        == (v1["bars"]["4_per_comment_agreement"]["threshold"])
    )


def test_the_population_is_pinned_as_a_list_with_its_injected_rows_marked():
    kept = subset.population()
    pop = RECORD["population"]
    assert pop["enumeration"]["digest"] == subset.digest(kept)
    assert (pop["threads"], pop["payable_comments"], pop["injected_threads"]) == (23, 134, 4)
    assert pop["gated_threads"] == 19
    assert pop["census_cell"]["sha256"] == summary.sha256_of(
        REPO_ROOT / pop["census_cell"]["record"]
    )
    assert (pop["census_cell"]["threads"], pop["census_cell"]["payable_comments"]) == (111, 912)

    listed = pop["enumeration"]["threads"]
    assert len(listed) == 23
    assert [one["thread"] for one in listed if one["injected"]] == sorted(subset.INJECTED)
    assert sum(one["payable_comments"] for one in listed) == 134
    for one, built in zip(listed, kept, strict=True):
        assert one["thread"] == subset.key(built["channel"], built["post_id"])
        assert one["msg_ids"] == [row["msg_id"] for row in built["comments"]]
        assert one["rendering_sha256"] == prereg.rendering_sha256(built, prompts.READER_TASK_V2)
        assert one["injected"] is not one["in_the_census_cell"]


def test_every_instrument_is_pinned_by_the_bytes_it_will_run_with():
    instruments = RECORD["instruments"]
    assert instruments["task"] == prompts.READER_TASK_V2 == "reader_thread_gm4_v2"
    assert instruments["prompt_sha256"] == {
        task: prompts.prompt_sha256(task) for task in sorted(prompts.READER)
    }
    assert set(instruments["prompt_sha256"]) == set(prompts.READER)
    assert instruments["parser"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "src" / "market_pulse" / "prompts.py"
    )
    assert instruments["scorer"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "src" / "market_pulse" / "scorer.py"
    )
    for name in instruments["scorer"]["functions"]:
        assert callable(getattr(scorer, name)), name
    for name, digest in RECORD["authority"].items():
        assert summary.sha256_of(REPO_ROOT / name) == digest, name
    for name, digest in RECORD["producer"]["borrowed"].items():
        assert summary.sha256_of(REPO_ROOT / name) == digest, name
    assert RECORD["producer"]["sha256"] == summary.sha256_of(
        REPO_ROOT / RECORD["producer"]["script"]
    )


def test_the_ceilings_and_the_serving_block_are_the_code_and_the_rulings():
    ceilings = RECORD["instruments"]["ceilings"]
    assert ceilings["input_chars"] == prompts.READER_MAX_INPUT_CHARS
    assert ceilings["output_tokens"] == local_llm.READER_MAX_NEW_TOKENS
    biggest = max(one["rendered_chars"] for one in RECORD["population"]["enumeration"]["threads"])
    assert biggest < ceilings["input_chars"]
    assert str(biggest) in ceilings["input_rule"]

    serving = RECORD["instruments"]["serving"]
    assert serving["adapter"] is None and serving["merge_state"] == "base-no-adapter"
    assert serving["chat_template"] == dict(local_llm.CHAT_TEMPLATE)
    assert serving["chat_template"]["enable_thinking"] is False
    assert serving["forward_batch_size"] == 1 and serving["do_sample"] is False
    # option B: the class is requested fastest-first and the runtime is what gets reported
    assert serving["gpu_class_preference"][0] == "ADA_24"
    assert list(serving["gpu_class_preference"]) == list(prereg.CARD_PREFERENCE)


def test_the_bars_are_reachable_now_and_their_arithmetic_is_recomputed():
    bars = RECORD["bars"]
    assert bars["1_flagships"]["scored_over"] == ["F1", "F2", "F3", "F4", "F5"]
    assert bars["2_entity_cases"]["threshold"] == "4 of 4 cases"
    assert set(bars["2_entity_cases"]["scored_over"]) == {one["id"] for one in GOLD["entity_cases"]}
    assert bars["3_noise"]["scored_over"] == ["N2", "N3", "N4", "N5", "N6"]
    assert "N1" in bars["3_noise"]["excluded_with_cause"]

    rows = bars["4_per_comment_agreement"]["scored_over"]
    assert rows == [one["msg_id"] for one in GOLD["per_comment"]] and len(rows) == 14
    # the threshold is COMPUTED, not rounded: 11 of 14 is 0.786 and fails, 12 is 0.857 and passes
    assert "12 of 14" in bars["4_per_comment_agreement"]["arithmetic"]
    assert 11 / 14 < prereg.AGREEMENT_BAR <= 12 / 14

    assert bars["5_time_and_cost"]["thresholds"] == {"cap_usd_all_in": 0.35}
    assert "window_minutes_billed" not in bars["5_time_and_cost"]["thresholds"]
    assert bars["5_time_and_cost"]["reported_not_gating"]["window_minutes_billed"] == 30.0


def test_the_cap_is_divided_by_a_measured_rate_before_anything_is_created():
    """probe-a's lesson, applied one contract later and BEFORE a resource exists: at the L4's
    measured seconds this population does not fit $0.35, so the registration states by how much the
    faster card has to be faster and the go/no-go is bought to measure exactly that."""
    money = RECORD["money"]
    assert money["cap_usd_all_in"] == prereg.CAP_USD == 0.35
    sums = money["arithmetic"]
    rate = sums["rate_usd_per_second"]
    assert (
        rate
        == json.loads(
            (REPO_ROOT / "results" / "run_5c2_comments.json").read_text(encoding="utf-8")
        )["rate_usd_per_second"]
    )

    buys = (prereg.CAP_USD - sums["setup_usd"]) / rate
    assert sums["seconds_the_cap_buys_after_setup"] == pytest.approx(buys, abs=0.05)

    l4 = sums["at_the_l4_rate_probe_a_measured"]
    assert l4["by_thread"]["seconds"] == pytest.approx(23 * 54.806, abs=0.05)
    assert l4["by_payable_comment"]["seconds"] == pytest.approx(134 * 14.947, abs=0.05)
    binding = max(l4["by_thread"]["seconds"], l4["by_payable_comment"]["seconds"])
    assert l4["all_in_usd"] == pytest.approx(binding * rate + sums["setup_usd"], abs=0.0005)
    assert l4["all_in_usd"] > prereg.CAP_USD and l4["verdict"] == "does not fit the cap"
    assert sums["break_even_speedup"] == pytest.approx(binding / buys, abs=0.002)
    assert sums["break_even_speedup"] > 1.0


def test_the_go_no_go_projects_the_remainder_and_says_why():
    """The bug this registration will not inherit: v1's driver projected the WHOLE population and
    compared it against what the cap had left AFTER the warm-up, counting those threads twice. At
    111 threads that is 2.7% of the cap; at 23 it is 13%, which is the difference between a STOP and
    a GO on a run the cap can afford."""
    gate = RECORD["go_no_go"]
    assert list(gate["warm_up"]["threads"]) == list(subset.WARM_UP)
    assert "UNREAD remainder" in gate["projection_rule"]
    assert "twice" in gate["projection_rule"]
    assert "STOP before any further call" in gate["stop_rule"]
    ranks = gate["warm_up"]["where_they_sit_in_this_population"]
    assert {one["thread"] for one in ranks} == set(subset.WARM_UP)
    assert all(one["of"] == 23 for one in ranks)
    # the warm-up is SMALLER than the average thread it prices — which is what makes the
    # per-payable projection the one that has to bind
    assert max(one["payable_comments"] for one in ranks) < 134 / 23 + 1


def test_the_vocabulary_split_is_registered_as_a_reported_reading_and_not_as_a_bar():
    """8 of the 14 per-comment gold rows score on `категория`, a word the ratified entity taxonomy
    does not carry and one the plan's own schema example stopped using on 2026-08-15. The bar is
    NOT changed for it — that would be the executor moving the operator's threshold — and the
    collapsed reading is registered beside it so a failure can be told apart from a vocabulary the
    two authorities disagree about."""
    beside = RECORD["non_gating"][0]
    assert "категория" in beside and "категория_личное" in beside
    assert "collapsed" in beside
    stated = [one for one in GOLD["per_comment"] if one["subject_type"] == "категория"]
    assert len(stated) == 8
    assert all("subject_type" in one["scored_fields"] for one in stated)


def test_what_the_record_says_it_freezes_and_what_it_reports_beside_the_bars():
    frozen = RECORD["frozen_when_the_endpoint_exists"]
    assert "results/prereg_reader_probe_v2.json" in frozen
    assert "results/reader_gold_w1.json" in frozen
    assert f"the {prompts.READER_TASK_V2} prompt text" in frozen
    assert "scripts/probe_b_population.py's enumeration" in frozen

    beside = " ".join(RECORD["non_gating"])
    for promised in ("finish_reason", "proposed", "N1", "from_post", "injected", "54.806"):
        assert promised in beside, promised
    assert RECORD["attempt"].startswith("ONE attempt, no retry")
