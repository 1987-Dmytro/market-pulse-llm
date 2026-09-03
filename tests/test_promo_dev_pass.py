"""S9's $0 half: the join back to the grader's row shape, and the record `--dry-run` writes.

An import proves nothing ([[stub_driven_script_verification]]) and `--dry-run` that stopped before
the write would leave the write path untested ([[exercise_the_write_path_not_just_the_compute]]), so
the entry point is DRIVEN here and the file it leaves behind is read back.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import promo_dev_pass as dev  # noqa: E402

from market_pulse import promo_prompts  # noqa: E402

ROW = {"channel": "@c", "thread_root": "1"}


def test_the_join_is_per_comment_and_a_silent_comment_is_not_invented():
    """Gold is one row per comment with a LIST of types; the model answers `about` + free-standing
    `signals`. The join is on `msg_id`, and a comment the model placed but said nothing about keeps
    its row with an empty list — that is a neutral answer, and the grader scores it as one."""
    answer = {
        "about": [
            {"msg_id": 10, "subject_type": "chain", "subject": "VARUS", "source": "explicit"},
            {"msg_id": 11, "subject_type": "post", "subject": "1", "source": "post_context"},
        ],
        "signals": [
            {"type": "жалоба", "msg_id": 10, "quote": "x"},
            {"type": "цена", "msg_id": 10, "quote": "y"},
            # a signal for a comment with NO about-row: it must not conjure one
            {"type": "спрос", "msg_id": 99, "quote": "z"},
        ],
    }
    rows = dev.predicted_rows(ROW, answer)
    assert [one["msg_id"] for one in rows] == ["10", "11"], "one row per about-row, and no more"
    assert rows[0]["signal_types"] == ["жалоба", "цена"]
    assert rows[1]["signal_types"] == [], "a neutral comment keeps its subject and no signal"
    assert all(one["channel"] == "@c" and one["thread_root"] == "1" for one in rows)


def test_a_comment_the_model_never_placed_produces_no_row():
    """Silence is an answer the grader must be able to see as a MISS ([[an_abstention_is_an_answer]]),
    so it is a row the gold has and the prediction does not — never a row invented here."""
    assert dev.predicted_rows(ROW, {"about": [], "signals": []}) == []


def test_the_dry_run_writes_the_record_and_every_number_in_it_is_derived(tmp_path):
    out = tmp_path / "prep.json"
    assert dev.main(["--dry-run", "--out", str(out)]) == 0
    record = json.loads(out.read_text(encoding="utf-8"))

    assert record["law"]["codebook_version"] == promo_prompts.codebook_version()
    assert record["law"]["vocabulary"]["signal_types"] == list(promo_prompts.SIGNAL_TYPES)
    assert record["draw"]["dev_threads"] == len(dev.dev_threads()) == 40

    bound = record["bound"]
    borrowed = bound["borrowed_from"]
    assert bound["seconds_at_the_borrowed_mean"] == round(borrowed["value"] * bound["threads"], 1)
    assert bound["usd_at_the_borrowed_max"] == round(
        borrowed["max"] * bound["threads"] * bound["usd_per_second"], 4
    )
    assert borrowed["source"] != "results/promo_dev40_prep.json", "a bound may not cite itself"
    assert "BORROWED" in bound["is_a_bound_and_not_a_price"].upper()

    corpus = record["corpus"]
    assert corpus["distinct_renders"] == bound["threads"], "40 threads, 40 different prompts"
    assert corpus["chars_max"] <= corpus["chars_total"]


def test_a_missing_rate_row_prices_nothing(tmp_path, monkeypatch):
    """The negative control on the borrow. A projection with no NAMED rate projects nothing — and a
    default that quietly stood in for the missing row is exactly the failure this refuses."""
    empty = tmp_path / "measurements.jsonl"
    empty.write_text('{"name": "something_else", "value": 1.0}\n', encoding="utf-8")
    monkeypatch.setattr(dev, "MEASUREMENTS", empty)
    with pytest.raises(SystemExit, match="no rate to borrow"):
        dev.borrowed_rate()
