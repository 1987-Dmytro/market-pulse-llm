"""`scripts/score_reader_v3.py` — the five bars, driven over verdicts built for the purpose.

Everything here runs at $0 and BEFORE the endpoint exists, for the reason probe-b's own suite gives:
a bar computation that raises after the money is spent is the one failure this contract cannot
absorb. The evidence file is written by the test, so nothing below reads the run's artefacts and
nothing below is red in the commits that precede them ([[a_test_that_reads_a_shipped_artifact]]).

Four things are proved that probe-b's suite could not have:

* bar 3 is the registration's own producer and not a second reading of it — asserted by computing
  both and comparing, and by the two states «unreachable» and «a refusal is not a zero»;
* bar 3's population GREW from five threads to six between v2 and v3, and the two bars can disagree
  on the same evidence — planted here, so the beside-column is a measurement and not a caveat;
* gold r2 is the bar, and a reader that answers the reference's «категория» is scored WRONG by it
  while the collapsed reading beside it says right — which is what the vocabulary column is for;
* the refusal census DERIVES probe-b's baselines from its own rows instead of transcribing a table.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import probe_b_population as subset  # noqa: E402
import score_reader_v3 as scoring  # noqa: E402
import write_reader_prereg_v3 as prereg  # noqa: E402

from market_pulse import prompts  # noqa: E402

GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text(encoding="utf-8"))
RECORD = json.loads(
    (REPO_ROOT / "results" / "prereg_reader_probe_v3.json").read_text(encoding="utf-8")
)

BRAND_NAMES = {
    "garmonija": "Гармонія",
    "selianske": "Селянське",
    "varus-pl": "Varus",
    "varto": "варто",
}
"""Names the watchlist matcher really resolves — its premise is asserted below, so a registry change
fails loudly instead of reading as «the reader missed the case»."""

NOISE_THREADS = {one["id"]: f"{one['channel']}:{one['post_id']}" for one in GOLD["noise_threads"]}

A_SIGNAL = {
    "signal_type": "жалоба",
    "proposed": False,
    "from_post": False,
    "subject_type": "категория",
    "subject_id": None,
    "aspect": "price",
    "stance": "negative",
    "reading": "читання",
    "evidence": [1],
    "quote": "ц",
}


def empty(thread: str) -> dict:
    channel, post_id = thread.rsplit(":", 1)
    return {
        "thread": {"channel": channel, "post_id": int(post_id)},
        "post_summary": "п",
        "discussion_summary": "д",
        "entities": [],
        "signals": [],
        "per_comment": [],
        "noise": [],
        "repairs": [],
    }


def perfect() -> dict[str, dict]:
    """A reader that answers every gold r2 case exactly — the fixture every failing case breaks."""
    verdicts = {
        subset.key(one["channel"], one["post_id"]): empty(
            subset.key(one["channel"], one["post_id"])
        )
        for one in subset.population()
    }
    for case in GOLD["flagships"]:
        body = verdicts[subset.key(case["channel"], case["post_id"])]
        for signal in case["signals"]:
            body["signals"].append(
                {
                    "signal_type": signal["signal_type"],
                    "proposed": False,
                    "from_post": False,
                    "subject_type": signal["subject_type"],
                    "subject_id": None,
                    "aspect": signal["aspect"],
                    "stance": signal.get("stance"),
                    "reading": "читання",
                    "evidence": list(signal["evidence"]),
                    "quote": "цитата",
                }
            )
    for case in GOLD["entity_cases"]:
        if case["subject_type"] is None:  # E4: the ruling is that NOTHING is reported
            continue
        body = verdicts[subset.key(case["channel"], case["post_id"])]
        body["entities"].append(
            {
                "name": BRAND_NAMES[case["brand_id"]],
                "msg_id": case["msg_id"],
                "subject_type": case["subject_type"],
                "reading": "читання",
                "quote": BRAND_NAMES[case["brand_id"]],
            }
        )
    for row in GOLD["per_comment"]:
        body = verdicts[subset.key(row["channel"], row["evidence_row"]["post_id_in_the_store"])]
        body["per_comment"].append(
            {
                "msg_id": row["msg_id"],
                "subject_type": row["subject_type"],
                "subject_id": row.get("subject_id"),
                "stance": row.get("stance"),
                "aspects": [],
                "note": None,
            }
        )
    return verdicts


def evidence_file(path: Path, verdicts: dict[str, dict], refused: dict[str, str] | None = None):
    """The run's per-row evidence, in the shape the driver writes it — refusals included.

    `refused` maps a thread to the reason its reply could not be read: the row still exists, still
    carries its seconds and its `finish_reason`, and carries no verdict. That is the state bar 3's
    fixed predicate exists for.
    """
    refused = refused or {}
    kept = {subset.key(one["channel"], one["post_id"]): one for one in subset.population()}
    lines = []
    for thread, body in verdicts.items():
        one = kept[thread]
        reason = refused.get(thread)
        lines.append(
            {
                "thread": thread,
                "channel": one["channel"],
                "post_id": one["post_id"],
                "injected": one["injected"],
                "cases": one["cases"],
                "payable_comments": len(one["comments"]),
                "task": prompts.READER_TASK_V3,
                "prompt_sha256": prompts.prompt_sha256(prompts.READER_TASK_V3),
                "rendering_sha256": "0" * 64,
                "request": "…",
                "reply": "unreadable" if reason else json.dumps(body, ensure_ascii=False),
                "finish_reason": "stop",
                "usage": {"completion_tokens": 100, "prompt_tokens": 2000},
                "parsed": None if reason else body,
                "repairs": None if reason else body["repairs"],
                "parse_error": reason,
                "seconds": {"wall": 1.0, "worker": 1.0},
            }
        )
    path.write_text(
        "\n".join(json.dumps(one, ensure_ascii=False) for one in lines) + "\n", encoding="utf-8"
    )
    return path


@pytest.fixture
def score(tmp_path, monkeypatch):
    """`build()` over an evidence file this test wrote, with no run record and no ledger beside it."""

    def run(verdicts, *, refused=None, ledger=None):
        monkeypatch.setattr(
            scoring, "EVIDENCE", evidence_file(tmp_path / "evidence.jsonl", verdicts, refused)
        )
        monkeypatch.setattr(scoring, "RUN", tmp_path / "no-such-run.json")
        path = tmp_path / "spend_reader_v3.json"
        if ledger is not None:
            path.write_text(json.dumps(ledger), encoding="utf-8")
        monkeypatch.setattr(scoring, "LEDGER", path)
        return scoring.build()

    return run


def test_the_fixture_names_brands_the_matcher_really_resolves():
    table = scoring.probe_b.aliases()
    for brand_id, name in BRAND_NAMES.items():
        entity = scoring.probe_b.resolved([{"name": name, "quote": name}], table)[0]
        assert entity["brand_ids"] == [brand_id], name


def test_a_perfect_reader_passes_every_bar_and_bar_three_is_over_six_threads(score):
    record = score(perfect())
    assert record["evidence"]["threads_read"] == 23
    assert record["gold"]["revision"] == "r2"
    for name, state in record["bars"].items():
        assert state["verdict"] == "SCORED", name
        assert state["result"]["passed"] is True, name
    assert record["bars"]["1_flagships"]["result"]["cases_answered"] == 5
    assert record["bars"]["2_entity_cases"]["result"]["cases_answered"] == 4
    agreement = record["bars"]["4_per_comment_agreement"]["result"]
    assert (agreement["n"], agreement["agreed"], agreement["rate"]) == (14, 14, 1.0)

    three = record["bars"]["3_noise"]["result"]
    assert record["bars"]["3_noise"]["scored_over"] == ["N1", "N2", "N3", "N4", "N5", "N6"]
    assert three["threads_registered"] == three["threads_with_a_verdict"] == 6
    assert three["signals"] == 0 and three["reachable"] is True
    for field in RECORD["bars"]["3_noise"]["result_must_carry"]:
        assert field in three, field


def test_bar_three_is_the_registrations_producer_and_not_a_second_reading(score):
    """The registration says the run's scorer «reproduces this predicate and may not invent a second
    reading of it». It is the same function, and this is what says so: the bar recomputed from the
    per-thread counts the record publishes equals the bar the record published."""
    record = score(perfect())
    three = record["bars"]["3_noise"]["result"]
    again = prereg.bar_three_over_answers(three["per_thread"], set(three["per_thread"]))
    assert {key: three[key] for key in again} == again


def test_a_refused_noise_reply_is_never_a_zero_and_an_unreadable_bar_is_not_a_pass(score):
    """probe-b's finding 2, both halves. Five of the six refuse and the sixth carries a signal:
    the bar is REACHABLE, counts one signal and fails. Then all six refuse: zero signals, and it
    still fails — «zero of nothing» is unreachable, which is not a pass."""
    verdicts = perfect()
    verdicts[NOISE_THREADS["N2"]]["signals"].append(dict(A_SIGNAL))
    five = {NOISE_THREADS[case]: "signals is not a list" for case in ("N1", "N3", "N4", "N5", "N6")}
    record = score(verdicts, refused=five)
    three = record["bars"]["3_noise"]["result"]
    assert three["threads_registered"] == 6
    assert three["threads_with_a_verdict"] == 1
    assert sorted(three["threads_refused"]) == sorted(five)
    assert three["signals"] == 1 and three["reachable"] is True and three["passed"] is False

    all_six = {name: "signals is not a list" for name in NOISE_THREADS.values()}
    blind = score(perfect(), refused=all_six)["bars"]["3_noise"]["result"]
    assert blind["threads_with_a_verdict"] == 0
    assert blind["signals"] == 0
    assert blind["reachable"] is False and blind["passed"] is False


def test_bar_three_grew_from_five_threads_to_six_and_the_two_can_disagree(score):
    """v2 registered N2–N6 and excluded N1 with a cause: the reference's own S list reads a signal
    inside that thread (S1, msg 21420). v3's producer takes every noise id from the gold and the
    exclusion did not come with it, so a reader that agrees with the reference now FAILS bar 3.

    Planted here rather than argued: one signal in N1's thread, and the registered bar fails while
    the bar over v2's five passes on the same evidence.
    """
    verdicts = perfect()
    verdicts[NOISE_THREADS["N1"]]["signals"].append(dict(A_SIGNAL))
    record = score(verdicts)

    assert record["bars"]["3_noise"]["result"]["passed"] is False
    assert record["bars"]["3_noise"]["result"]["signals"] == 1
    beside = record["beside_the_bars"]["3_noise_over_v2s_five_threads"]
    assert beside["excluded_by_v2"] == ["N1"]
    assert beside["scored_over"] == ["N2", "N3", "N4", "N5", "N6"]
    assert beside["result"]["passed"] is True and beside["result"]["signals"] == 0


def test_gold_r2_is_the_bar_and_the_collapsed_reading_sits_beside_it(score):
    """Ruling 4 adjudicated «категория» and «категория_личное» as ONE class and r2 applies it to
    twelve gold cells — but the v3 prompt still offers BOTH words, so a reader answering the
    reference's word is scored WRONG by the bar it is now scored against. As registered the eight
    per-comment rows r2 moved disagree; collapsed, they agree. Both numbers are in the record."""
    # the cells r2 itself says it moved, read out of its revision block — a filter on the value
    # would also catch the one row that already read «категория_личное» under v1 (580129)
    moved = [
        GOLD["per_comment"][int(cell.split("[")[1].split("]")[0])]["msg_id"]
        for cell in GOLD["revision"]["cells"]
        if cell.startswith(".per_comment[")
    ]
    assert len(moved) == 8, "the r2 relabel is what this test is about"
    assert 580129 not in moved, "that row read «категория_личное» in v1 and r2 did not move it"

    verdicts = perfect()
    for body in verdicts.values():
        for row in body["per_comment"]:
            if row["msg_id"] in moved:
                row["subject_type"] = "категория"
    record = score(verdicts)

    bar = record["bars"]["4_per_comment_agreement"]["result"]
    assert bar["agreed"] == 14 - len(moved) and bar["passed"] is False
    collapsed = record["beside_the_bars"]["collapsed_vocabulary_reading"]
    assert collapsed["bars"]["4_per_comment_agreement"]["as_registered"] == bar["rate"]
    assert collapsed["bars"]["4_per_comment_agreement"]["collapsed"] == 1.0


def test_the_repair_census_names_every_registered_repair_including_the_ones_that_did_not_fire(
    score,
):
    verdicts = perfect()
    verdicts["@retsepty:7327"]["repairs"] = ["noise: empty object -> empty list"]
    record = score(verdicts)
    census = record["repairs"]
    assert census["fired"]["noise: empty object -> empty list"] == 1
    assert census["fired"][prompts.TWO_OBJECTS_MERGED] == 0
    assert census["unregistered_names_that_fired"] == []
    assert census["threads_repaired"] == ["@retsepty:7327"]
    assert census["threads_read_straight"] == 22
    # every name the registration lists is in the census, fired or not
    for field in prompts.READER_LIST_FIELDS:
        assert f"{field}: map keyed by msg_id -> list" in census["fired"]


def test_the_refusal_census_derives_probe_bs_baselines_from_its_own_rows(score):
    """probe-b's report counts «six shapes» in prose, its verdict record holds five causes over ten
    refusals, and the registration names a seventh reply. A transcribed table would be wrong about
    which shapes are new, so both baselines are computed — and the second one is probe-b's own 23
    replies re-read by TODAY's parser, which is the measurement the registration published as 19 of
    23."""
    record = score(perfect(), refused={"@retsepty:7327": "a brand new shape"})
    census = record["refusals"]
    assert census["as_run"] == {"a brand new shape": 1}
    assert census["new_against_probe_b"] == ["a brand new shape"]
    assert sum(census["probe_b_as_run_under_v2"].values()) == 10
    assert sum(census["probe_b_replies_under_todays_parser"].values()) == 4, (
        "the registration's own measurement: 19 of probe-b's 23 replies parse under v3"
    )
    assert len(census["did_not_return"]) == len(census["probe_b_as_run_under_v2"])


def test_bar_five_reads_the_step_ledger_in_all_three_of_its_states(score):
    verdicts = perfect()
    absent = score(verdicts)["5_time_and_cost"]
    assert absent["state"] == "NO LEDGER" and absent["passed"] is None

    open_ledger = {
        "runpod_balance_at_reader-v3_start": 22.50,
        "anchored_at": "2026-08-16T17:00:00+00:00",
        "gpu_sessions": [{"at": "…", "balance": 22.4, "step_spent_usd": 0.1, "note": "mid-run"}],
    }
    live = score(verdicts, ledger=open_ledger)["5_time_and_cost"]
    assert live["state"] == "OPEN" and live["passed"] is None
    assert live["lower_bound_usd"] == 0.1

    closed = dict(open_ledger)
    closed["gpu_sessions"] = [
        *open_ledger["gpu_sessions"],
        {
            "at": "…",
            "closed": True,
            "settled_usd": 0.31,
            "billing_by_kind": {"pods": 0.02, "serverless": 0.29, "network-volume": 0.13},
            "window_start": "2026-08-16T17:00:00+00:00",
        },
    ]
    shut = score(verdicts, ledger=closed)["5_time_and_cost"]
    assert shut["state"] == "CLOSED" and shut["settled_usd"] == 0.31
    assert shut["passed"] is True

    over = json.loads(json.dumps(closed))
    over["gpu_sessions"][-1]["settled_usd"] = 0.41
    assert score(verdicts, ledger=over)["5_time_and_cost"]["passed"] is False


def test_the_output_ceiling_reading_names_both_of_its_denominators(score):
    """Dv433. Returned rows are what the tokens paid for; requested rows are what v3 asked for, one
    per payable comment. A model that under-delivers makes the first flatter than the second, and
    the window re-price needs the second — so neither is called «the» rate."""
    verdicts = perfect()
    record = score(verdicts)
    ceiling = record["output_ceiling"]
    returned = sum(len(body["per_comment"]) for body in verdicts.values())
    assert ceiling["per_comment_rows_returned"] == returned == 14
    assert ceiling["per_comment_rows_requested"] == RECORD["population"]["payable_comments"] == 134
    assert ceiling["tokens_per_returned_per_comment_row"] == round(23 * 100 / returned, 2)
    assert ceiling["tokens_per_requested_per_comment_row"] == round(23 * 100 / 134, 2)
    assert ceiling["finish_reason_length"] == 0
    assert ceiling["probe_b_finish_reason_length"] == 0
    assert ceiling["max_new_tokens"] == 2000


def test_the_scorer_module_is_the_one_the_registration_pinned(score):
    """Dv431: `scorer.py` is deliberately untouched and four sealed records pin its bytes. The
    verdict says so out of its own reading rather than leaving it to be assumed."""
    record = score(perfect())
    assert record["scorer"]["unchanged"] is True
    assert record["scorer"]["sha256"] == RECORD["instruments"]["scorer"]["sha256"]
