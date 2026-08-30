"""`results/prereg_reader_probe_v4.json` — the pod registration, checked before it can be spent.

v4 changes three things and copies everything else, so this file checks exactly that split: the
three differences are re-derived from the frozen records they claim to restore, and the instrument
is asserted to be v3's byte for byte. The claims a reader cannot check by eye — that the vocabulary
collapse really is symmetric, that the boot deadline is an inequality and not a slogan, and what the
cap buys in SECONDS at the price that was read on the day — are recomputed rather than read.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from test_prompts import with_r2_put_back  # noqa: E402

import score_reader_probe_b as scoring  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_reader_prereg_v3 as v3  # noqa: E402
import write_reader_prereg_v4 as prereg  # noqa: E402
from test_prompts import (  # noqa: E402
    assert_pinned,
    put_the_sealed_shas_back,
    sealed_sha256,
)

from market_pulse import prompts, scorer  # noqa: E402

RECORD_PATH = REPO_ROOT / "results" / "prereg_reader_probe_v4.json"
RECORD = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
V2 = json.loads((REPO_ROOT / "results" / "prereg_reader_probe_v2.json").read_text(encoding="utf-8"))
V3 = json.loads((REPO_ROOT / "results" / "prereg_reader_probe_v3.json").read_text(encoding="utf-8"))
GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text(encoding="utf-8"))


def test_the_committed_registration_is_what_the_producer_writes_today(tmp_path):
    """No clock is stamped, so the record re-derives byte for byte and its date is the date of the
    commit that carries it — which is the only witness that it preceded the pod."""
    out = tmp_path / "again.json"
    assert prereg.main(["--out", str(out)]) == 0
    # `producer.borrowed` is hashed LIVE, and `src/market_pulse/prompts.py` moved when the v5 text
    # was registered. The record is NOT re-pinned — it froze when the pod existed — so the one byte
    # range allowed to differ is put back to what the sealing commit carries, and the swap must fire
    assert with_r2_put_back(put_the_sealed_shas_back(out.read_bytes())) == RECORD_PATH.read_bytes()
    assert "generated_at" not in RECORD_PATH.read_text(encoding="utf-8")


def test_the_instrument_is_v3s_bytes_and_not_a_re_derivation():
    """Difference 3 is about money and differences 1–2 are about scoring; NOTHING about what is
    measured moved. The strongest form of that claim is object equality with the frozen v3 block —
    a re-derived prompt sha would agree today and be free to disagree the day `prompts.py` moves."""
    assert RECORD["instruments"] == V3["instruments"]
    assert RECORD["instruments"]["task"] == prompts.READER_TASK_V3
    # and the pinned bytes are still the live ones, so the record is not pinning a ghost
    assert RECORD["instruments"]["prompt_sha256"][prompts.READER_TASK_V3] == prompts.prompt_sha256(
        prompts.READER_TASK_V3
    )
    # the parser is the MOVED file: v5 registered a fourth reader text, so the pinned bytes are the
    # sealing commit's and the live ones are deliberately different
    assert_pinned("src/market_pulse/prompts.py", RECORD["instruments"]["parser"]["sha256"])
    assert RECORD["instruments"]["parser"]["sha256"] == sealed_sha256("src/market_pulse/prompts.py")
    assert RECORD["instruments"]["scorer"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "src" / "market_pulse" / "scorer.py"
    )
    assert RECORD["population"]["enumeration"]["digest"] == v3.POPULATION_DIGEST


def test_difference_one_restores_v2s_five_threads_and_v2s_own_exclusion():
    """«Verbatim» is a claim about a frozen file, so it is read out of that file and compared —
    and the producer holds a literal beside it, which is the half that can fail."""
    bar = RECORD["bars"]["3_noise"]
    assert bar["scored_over"] == ["N2", "N3", "N4", "N5", "N6"] == prereg.NOISE_THREADS_V2
    assert bar["excluded_with_cause"] == V2["bars"]["3_noise"]["excluded_with_cause"]
    assert list(bar["excluded_with_cause"]) == ["N1"]
    assert (
        bar["n3_is_not_a_discriminating_case"]
        == V2["bars"]["3_noise"]["n3_is_not_a_discriminating_case"]
    )
    # v3 is what this differs from, and it differed by exactly one thread
    assert sorted(set(V3["bars"]["3_noise"]["scored_over"]) - set(bar["scored_over"])) == ["N1"]
    # the threshold, the scorer and the fields the result must carry are v3's, unmoved
    for field in ("threshold", "scorer", "result_must_carry"):
        assert bar[field] == V3["bars"]["3_noise"][field]


def test_difference_one_keeps_v3s_predicate_by_importing_it_and_not_copying_it():
    """The population changed and the predicate did not. Driven on a hand-made pair so «counted
    over answers» is exercised rather than asserted: a refused thread is not a zero."""
    assert (
        "write_reader_prereg_v3.py::bar_three_over_answers" in RECORD["bars"]["3_noise"]["producer"]
    )
    five = {name: 0 for name in RECORD["bars"]["3_noise"]["scored_over"]}
    answered = set(five) - {"N5"}
    bar = v3.bar_three_over_answers(five, answered)
    assert bar["threads_registered"] == 5
    assert bar["threads_with_a_verdict"] == 4
    assert bar["threads_refused"] == ["N5"]
    assert bar["reachable"] and bar["passed"]
    # and with nothing answered it is UNREACHABLE, which is not a pass
    empty = v3.bar_three_over_answers(five, set())
    assert not empty["reachable"] and not empty["passed"]


def test_difference_two_is_symmetric_in_both_directions_with_a_negative_control():
    """The registration says the two words are ONE class on both sides. So: gold «категория» with
    the reader's «категория_личное» agrees, the same pair the other way round agrees, and a THIRD
    subject_type still disagrees — otherwise the rule would not be a collapse but an amnesty."""
    rule = RECORD["scoring_rules"]["vocabulary_collapse"]
    assert rule["symmetric"] is True
    assert rule["applies_to"] == ["1_flagships", "4_per_comment_agreement"]
    assert rule["map"] == scoring.COLLAPSE
    # both words really are in the prompt's own list, which is why the disagreement can happen
    assert {"категория", "категория_личное"} <= set(rule["subject_types_the_prompt_offers"])
    assert set(rule["subject_types_the_prompt_offers"]) == set(prompts.READER_SUBJECT_TYPES)

    def rate(gold_word: str, reader_word: str) -> float:
        row = {"msg_id": 1, "subject_type": gold_word, "scored_fields": ["subject_type"]}
        said = {"msg_id": 1, "subject_type": reader_word}
        collapsed_gold = {**row, "subject_type": scoring.collapse(row["subject_type"])}
        collapsed_said = {**said, "subject_type": scoring.collapse(said["subject_type"])}
        return scorer.reader_comment_agreement([collapsed_gold], [collapsed_said])["rate"]

    assert rate("категория", "категория_личное") == 1.0  # the reference's word, ratified answer
    assert rate("категория_личное", "категория") == 1.0  # the ratified word, reference answer
    assert rate("категория", "бренд") == 0.0  # the control: a third word is still wrong
    assert rate("категория_личное", "бренд") == 0.0
    # and uncollapsed, the first pair is exactly the disagreement the rule exists to close
    assert (
        scorer.reader_comment_agreement(
            [{"msg_id": 1, "subject_type": "категория", "scored_fields": ["subject_type"]}],
            [{"msg_id": 1, "subject_type": "категория_личное"}],
        )["rate"]
        == 0.0
    )


def test_difference_two_names_the_two_bars_it_touches_and_leaves_their_thresholds_alone():
    for name in ("1_flagships", "4_per_comment_agreement"):
        assert "vocabulary collapse applies" in RECORD["bars"][name]["scoring_rule"]
        assert RECORD["bars"][name]["threshold"] == V3["bars"][name]["threshold"]
    # bar 2 compares a subject_type too and is deliberately NOT in the rule's scope: the contract
    # scopes the collapse to bars 1 and 4, and a rule that quietly grew would be a fourth difference
    assert "scoring_rule" not in RECORD["bars"]["2_entity_cases"]
    assert RECORD["bars"]["4_per_comment_agreement"]["gold"]["sha256"] == summary.sha256_of(
        REPO_ROOT / "results" / "reader_gold_w1_r2.json"
    )


def test_the_cap_is_a_stopwatch_and_every_leg_is_hand_computable():
    """A pod bills for existing, so the cap is seconds. Hand-computed at the price that was READ on
    the day — the contract's own worked example is $0.59/h and this is not that number."""
    meter = RECORD["money"]["meter"]
    sums = RECORD["money"]["arithmetic"]
    assert meter["usd_per_hour"] == 0.74
    assert meter["usd_per_second"] == round(0.74 / 3600, 9)
    assert sums["seconds_the_cap_buys"] == round(0.35 * 3600 / 0.74, 3) == 1702.703
    assert sums["usable_seconds"] == round(1702.703 - 60.0, 3) == 1642.703
    # the reading projection is probe-b's WORKER leg and not its wall leg, and the record says why
    assert sums["reading_projection_seconds"] == 727.664 == sums["probe_b"]["worker_seconds"]
    assert sums["probe_b"]["wall_seconds"] == 802.103
    assert "queue" in sums["reading_projection_rule"]
    # the pre-generation budget is what is left once the full twelve minutes and the reading fit
    assert sums["pre_generation_budget_seconds"] == round(1642.703 - 720.0 - 727.664, 3) == 195.039
    assert sums["boot_kill_usd"] == round(720.0 * 0.74 / 3600, 4) == 0.148
    assert "$0.12" in meter["the_contracts_own_example"]


def test_the_boot_table_is_the_inequality_at_five_boots_and_the_last_row_is_the_corner():
    """Both numbers published, per the contract. The 720 s row is where the twelve-minute ceiling
    and the affordability deadline meet: exactly probe-b's reading fits and nothing more."""
    sums = RECORD["money"]["arithmetic"]
    table = {row["boot_seconds"]: row for row in sums["at_each_boot"]}
    assert sorted(table) == [180.0, 300.0, 480.0, 600.0, 720.0]
    for boot, row in table.items():
        left = 1642.703 - 195.039 - boot
        assert row["seconds_left_for_reading"] == round(left, 1)
        assert row["slowdown_vs_probe_b_that_fits"] == round(left / 727.664, 3)
    assert table[720.0]["slowdown_vs_probe_b_that_fits"] == 1.0
    assert table[300.0]["slowdown_vs_probe_b_that_fits"] > 1.5
    # every row is inside the cap by construction — the table prices the plan, it does not test it
    assert all(row["all_in_usd_at_probe_bs_rate"] <= 0.35 for row in table.values())


def test_the_gates_sit_on_the_step_that_spends_and_the_clock_starts_at_create():
    """v3's lesson, registered: a gate downstream of an unbounded step cannot fire. The clock is
    seconds since `pod create`, because the machine is billed for provisioning too."""
    gate = RECORD["go_no_go"]
    assert "pod create" in gate["clock"]
    assert set(gate["gates"]) == {"1_staging", "2_boot_kill", "3_the_full_pass"}
    assert gate["gates"]["1_staging"]["expected_usd"] == 0.0
    assert "min(720 s" in gate["gates"]["2_boot_kill"]["rule"]
    full = gate["gates"]["3_the_full_pass"]
    # BOTH legs and the pessimistic one binding — probe-a's rule, probe-b's and v3's. A single-leg
    # projection is looser in the one direction a cap guard may not be loose in
    assert "PESSIMISTIC" in full["rule"]
    assert "unread payable comments ÷ read payable comments" in full["rule"]
    assert "binding factor × threads read" in full["solved_for_seconds"]
    assert (
        "the pessimistic of the per-thread and per-payable-comment projections"
        in V3["go_no_go"]["binding"]
    ), "v3 registered it in those words and v4 keeps it"
    # the backstop is named as NOT a cap guard, with the arithmetic that says so
    assert gate["backstop"]["terminate_after_minutes"] == 90
    assert "$1.11" in gate["backstop"]["rule"]
    assert round(90 * 60 * 0.74 / 3600, 2) == 1.11


def test_it_supersedes_v3_without_withdrawing_it():
    older = RECORD["supersedes"]
    assert older["record"] == "results/prereg_reader_probe_v3.json"
    assert older["sha256"] == summary.sha256_of(REPO_ROOT / older["record"])
    assert len(older["what_it_changes"]) == 3
    assert "FROZEN" in older["state"]
    assert older["no_ablation"] == V3["supersedes"]["no_ablation"]
    assert RECORD["authority"]["docs/PROMPT-reader-v4.md"] == summary.sha256_of(
        REPO_ROOT / "docs" / "PROMPT-reader-v4.md"
    )


def test_what_freezes_when_the_pod_exists():
    frozen = RECORD["frozen_when_the_pod_exists"]
    assert "results/prereg_reader_probe_v4.json" in frozen
    assert "results/reader_gold_w1_r2.json" in frozen
    assert "src/market_pulse/prompts.py — the parser" in frozen
    assert "src/market_pulse/scorer.py" in frozen
    assert RECORD["transport"]["persisted_per_row"][0].startswith("the rendered request")
    assert "flushed as it lands" in RECORD["transport"]["flush_rule"]
