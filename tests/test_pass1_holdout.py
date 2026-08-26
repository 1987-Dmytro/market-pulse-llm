"""`results/pass1_holdout_100.json` — the draw, the floor that makes it reachable, and the seal.

Four things carry weight here. The record on disk is what the producer builds today, so a hundred
rows that a future line may never train on are reproducible from the file rather than remembered.
The allocation is the registered tuple AND the floor is load-bearing — the test computes what plain
largest remainder would have drawn, because «52:33:7:7:1» is only a rule if the alternative is
written down. Every unit is a real label carrying the label the record states. And the four
contamination lists are empty with a matcher that is proven able to find something
([[guard_selftest_negative_control]]).
"""

import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import moved_pins  # noqa: E402
import write_pass1_holdout as holdout  # noqa: E402

RECORD = json.loads((REPO_ROOT / holdout.OUT_NAME).read_text("utf-8"))
GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text("utf-8"))
PROBE = json.loads((REPO_ROOT / "results" / "pass1_probe_b_pack.json").read_text("utf-8"))


def test_the_shipped_record_is_what_the_producer_builds_today(tmp_path):
    assert holdout.main(["--outdir", str(tmp_path)]) == 0
    again = json.loads((tmp_path / holdout.OUT_NAME).read_text(encoding="utf-8"))
    shipped = json.loads((REPO_ROOT / holdout.OUT_NAME).read_text(encoding="utf-8"))
    # EXCEPT where it pins `src/market_pulse/prompts.py`, moved again by ruling (ф)'s parser change
    moved_pins.assert_only_the_prompts_pin_moved(shipped, again)


def test_the_draw_is_the_registered_tuple_and_the_floor_is_what_makes_it_reachable():
    """The negative control on the RULE: plain largest remainder loses `молочный_бренд` entirely."""
    counts = {name: n for name, n in RECORD["population"]["distribution"].items() if n}
    assert counts == {
        "молочный_бренд": 2,
        "сеть_ритейлер": 48,
        "категория_личное": 47,
        "не_наш_рынок": 340,
        "null": 213,
    }
    assert holdout.allocate(counts, holdout.TARGET) == holdout.REGISTERED_ALLOCATION

    total = sum(counts.values())
    floors = {name: holdout.TARGET * n // total for name, n in counts.items()}
    remainder = {name: holdout.TARGET * counts[name] / total - floors[name] for name in counts}
    plain = dict(floors)
    for name in sorted(counts, key=lambda one: (-remainder[one], one))[
        : holdout.TARGET - sum(floors.values())
    ]:
        plain[name] += 1
    assert sum(plain.values()) == holdout.TARGET
    assert plain["молочный_бренд"] == 0, plain
    assert plain != holdout.REGISTERED_ALLOCATION


def test_the_units_are_a_hundred_distinct_real_labels_carrying_the_label_the_record_states():
    units = RECORD["units"]
    assert len(units) == holdout.TARGET
    keys = {(one["thread"], one["msg_id"]) for one in units}
    assert len(keys) == holdout.TARGET
    labelled = {(row["thread"], row["msg_id"]): row["subject_type"] for row in holdout.labels()}
    for one in units:
        assert (one["thread"], one["msg_id"]) in labelled, one
        assert labelled[(one["thread"], one["msg_id"])] == one["subject_type"], one
    counted = Counter(holdout.key(one["subject_type"]) for one in units)
    assert dict(counted) == holdout.REGISTERED_ALLOCATION


def test_the_four_contamination_lists_are_empty_and_the_matcher_can_find_something():
    block = RECORD["contamination"]
    lists = [
        "holdout_ids_in_the_gold_14",
        "holdout_threads_in_the_gold_threads",
        "holdout_ids_in_the_eval_pack_64",
        "holdout_threads_in_the_eval_pack_threads",
    ]
    for name in lists:
        assert block[name] == [], (name, block[name])

    # the negative control: the same intersections over a set that DOES overlap must be non-empty
    gold_ids = {int(row["msg_id"]) for row in GOLD["per_comment"]}
    probe_ids = {int(one["msg_id"]) for one in PROBE["items"]}
    probe_threads = {one["thread"] for one in PROBE["items"]}
    assert len(gold_ids) == 14 and len(probe_ids) == 64 and probe_threads
    planted = {one["msg_id"] for one in RECORD["units"]} | gold_ids
    assert sorted(planted & gold_ids) == sorted(gold_ids)
    assert probe_ids & gold_ids == gold_ids, "the gold rows ARE inside the eval pack"


def test_the_rule_says_evaluation_only_and_names_the_producer_that_enforces_it():
    assert RECORD["evaluation_only"] is True
    assert "EVALUATION ONLY" in RECORD["rule"] or "EVALUATION" in RECORD["rule"].upper()
    assert "scripts/build_pass1_sft.py" in RECORD["rule"]
    # the overlap this line accepts is DECLARED, not discovered later
    assert RECORD["overlap"]["sealed_arms"]["b"]["holdout_rows_inside_it"] == holdout.TARGET
    assert "trains NOTHING" in RECORD["overlap"]["rule"]
