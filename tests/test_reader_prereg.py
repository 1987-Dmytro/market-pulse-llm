"""`results/prereg_reader_probe.json` — the registration, checked before it can be spent against.

A pre-registration is only worth what its re-derivation is worth: every threshold here is the
operator's word, every sha is a live file, and the one arithmetic claim it makes — what «≥ 0.80»
means over thirteen rows — is recomputed rather than read.
"""

import hashlib
import json
import re
import subprocess
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

SEALING_COMMIT = "8c68107"
"""probe-a's last commit — the tree this registration was spent against.

This record's own `frozen_when_the_endpoint_exists` names itself first, and the endpoint has existed
and been deleted. A pinned file that moves afterwards is therefore never re-pinned: it joins the list
below with its reason, `git show` keeps the sealed bytes recoverable, and the re-derivation test goes
on claiming what it claimed on the day of the run rather than what is true today.
"""

MOVED_BY_THE_RATIFIED_WORDS = ("docs/PLAN-comment-signals.md",)
"""The one pinned file the team lead's edit of 2026-08-15 (evening) moved: §3's schema example took
the ratified `сеть_ритейлер` and `категория_личное` in place of `сеть` and `категория`. No threshold,
no population and no instrument in this record moves — the edit is two words in an authority
document, and `results/reader_gold_w1.json` rebuilds byte for byte beside it.
"""

MOVED_BY_THE_V2_READER = ("src/market_pulse/prompts.py", "src/market_pulse/local_llm.py")
"""The two pinned files `docs/PROMPT-probe-b.md` D1 moved — a SECOND tuple, because the two groups
are checked by different witnesses and a shared branch would assert the plan's about a file that
never met it ([[an_invariant_the_new_member_cannot_satisfy]]).

D1 registers `reader_thread_gm4_v2` BESIDE the sixteen prompts already in `prompts.PROMPTS`, teaches
`parse_reply` the `from_post` signal, and lets `ReaderClient` render either registered text. The v1
prompt's TEXT does not move — `instruments.prompt_sha256` below is still derived LIVE and is
deliberately not relaxed — so every number registered here still describes the instrument that ran.
Both files stay RECOVERABLE:

    git show 8c68107:src/market_pulse/prompts.py
    git show 8c68107:src/market_pulse/local_llm.py
"""

MOVED_BY_NAMING_THE_TASK = ("scripts/write_reader_prereg.py",)
"""The producer itself, and a THIRD tuple because its witness is its own.

probe-b made v2 the default of `prompts.reader_messages_gm4`. This producer measures `rendered_chars`
and the input-ceiling headroom, so left on the default it would re-derive a FROZEN record under a
prompt no thread was ever sent with; `rendering()` now names `task=prompts.READER_TASK`. One line,
and it is the line that keeps every other byte of this record true
([[a_sealed_caller_forces_the_default]]).

    git show 8c68107:scripts/write_reader_prereg.py
"""

MOVED = MOVED_BY_THE_RATIFIED_WORDS + MOVED_BY_THE_V2_READER + MOVED_BY_NAMING_THE_TASK
WITNESS = {
    **dict.fromkeys(MOVED_BY_THE_RATIFIED_WORDS, '"subject_type": "сеть_ритейлер"'),
    # the registry key in the module that owns it, the constant in the module that reads it —
    # a shared token would have to be one that means something in both files, and the only such
    # string here is the weaker one
    "src/market_pulse/prompts.py": "reader_thread_gm4_v2",
    "src/market_pulse/local_llm.py": "READER_TASK_V2",
    "scripts/write_reader_prereg.py": "task=prompts.READER_TASK",
}

NAMED_IN_THE_RECORD = {
    "docs/PLAN-comment-signals.md": 1,  # authority
    "src/market_pulse/prompts.py": 2,  # instruments.parser.sha256 AND producer.borrowed
    "src/market_pulse/local_llm.py": 1,  # producer.borrowed
    "scripts/write_reader_prereg.py": 1,  # producer.sha256
}
"""How many times each moved file's sha appears in the record — stated, so a swap that put back one
of two mentions cannot pass. `prompts.py` is named twice on purpose: once as the parser this run's
replies were read by, once as a borrowed producer input."""
"""What each moved file learned, read BOTH ways below — absent from the sealed blob and present on
disk — so a recovery from the wrong commit fails instead of passing."""


def sealed_blob(path: str) -> bytes:
    """`path` as :data:`SEALING_COMMIT` carried it — git, and nothing on disk."""
    return subprocess.run(
        ["git", "show", f"{SEALING_COMMIT}:{path}"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
    ).stdout


def sealed_sha256(path: str) -> str:
    return hashlib.sha256(sealed_blob(path)).hexdigest()


def put_the_sealed_shas_back(produced: bytes) -> bytes:
    """Swap every MOVED file's live sha for its sealed one — each swap must FIRE.

    A substitution that matched nothing would leave the byte comparison passing for a file that had
    silently gone back to the sealed bytes.
    """
    for path in MOVED:
        live, sealed = summary.sha256_of(REPO_ROOT / path), sealed_sha256(path)
        assert live != sealed, path
        token = WITNESS[path]
        assert token not in sealed_blob(path).decode("utf-8"), path
        assert token in (REPO_ROOT / path).read_text(encoding="utf-8"), path
        produced, count = re.subn(live.encode(), sealed.encode(), produced)
        assert count == NAMED_IN_THE_RECORD[path], (path, count)
    return produced


def assert_pinned(name: str, digest: str) -> None:
    """A pinned file is its live sha — or, on the MOVED list, the sha :data:`SEALING_COMMIT` has."""
    live = summary.sha256_of(REPO_ROOT / name)
    if name in MOVED:
        assert live != digest and sealed_sha256(name) == digest, name
    else:
        assert live == digest, name


def test_the_committed_registration_is_what_the_producer_writes_today(tmp_path):
    """No clock is stamped, so the record re-derives byte for byte and its date is the date of the
    commit that carries it — which is also the only witness that it preceded the endpoint."""
    out = tmp_path / "again.json"
    assert prereg.main(["--out", str(out)]) == 0
    assert put_the_sealed_shas_back(out.read_bytes()) == RECORD_PATH.read_bytes()
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
    # the parser is one of the MOVED files: probe-b taught it `from_post` and registered a second
    # reader text beside v1. The v1 prompt's own sha above is still LIVE and unrelaxed, which is
    # what says this registration's instrument did not move — only the module around it
    assert_pinned("src/market_pulse/prompts.py", instruments["parser"]["sha256"])
    for name in instruments["scorer"]["functions"]:
        assert callable(getattr(scorer, name)), name
    for name, digest in RECORD["authority"].items():
        assert_pinned(name, digest)
    for name, digest in RECORD["producer"]["borrowed"].items():
        assert_pinned(name, digest)


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
    """The cap is the operator's, raised 0.20 → 0.45 on 2026-08-15 once the arithmetic of the
    report's §5 showed the smaller one could not buy the registered run. The raise moves the
    ceiling and nothing else: the ruling is IN the record, and the population digest, the bars and
    the stop rule are the ones registered before it."""
    money = RECORD["money"]
    assert money["cap_usd_all_in"] == prereg.CAP_USD == 0.45
    bar = RECORD["bars"]["5_time_and_cost"]["thresholds"]
    assert bar == {"cap_usd_all_in": 0.45, "window_minutes_billed": 30.0}
    assert any("raised from $0.20 to $0.45 all-in" in one for one in RECORD["rulings"])
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
