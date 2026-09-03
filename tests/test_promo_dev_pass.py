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


# --- the PAID half's $0 gates: driven without a pod, each with its negative control ---------------


class _Done:
    def __init__(self, stdout="", returncode=0, stderr=""):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


GUARD_SAYS = "CYCLE 3 SPENT     $3.5409 of $7.00\nREMAINING         $3.4591\n"


def test_the_smoke_is_a_rule_and_not_a_pick():
    """Shortest, median, longest by the prep record's own `chars` — and the ROLES are named, so a
    reader of the registration can re-derive the three without trusting this function."""
    threads = [
        {"channel": "@c", "thread_root": str(i), "chars": chars}
        for i, chars in enumerate([700, 100, 500, 900, 300])
    ]
    picked = dev.smoke_units([dict(one) for one in threads])
    assert [one["chars"] for one in picked] == [100, 500, 900]
    assert [one["smoke_role"] for one in picked] == ["shortest", "median", "longest"]


def test_the_guard_line_is_read_and_an_unreadable_headroom_refuses(monkeypatch):
    """The cycle's headroom is the guard's number. A run that cannot find the line refuses rather
    than reading a missing prior as unlimited — the negative control is the second half."""
    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done(GUARD_SAYS))
    assert dev.guard_reading()["remaining_usd"] == 3.4591

    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done("nothing of the sort\n"))
    with pytest.raises(SystemExit, match="REMAINING"):
        dev.guard_reading()


def test_a_refusing_guard_stops_the_registration(monkeypatch):
    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done(GUARD_SAYS, returncode=3))
    with pytest.raises(SystemExit, match="the guard refused"):
        dev.guard_reading()


def test_the_price_is_the_dearer_offer_and_a_missing_card_is_a_stop(monkeypatch):
    """The create response's `costPerHr` is what bills; a registration written at the cheaper of two
    offers would be a ceiling the run can exceed with no gate firing. And a card the datacenter does
    not have today is the operator's word, not a substitution this script may make."""
    offered = [
        {
            "displayName": "RTX 4090",
            "securePricePerHr": 0.74,
            "communityPricePerHr": 0.34,
            "dataCenterAvailability": [{"dataCenterId": "EU-RO-1", "stockStatus": "Medium"}],
        }
    ]
    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done(json.dumps(offered)))
    assert dev.offered_price()["usd_per_hour"] == 0.74

    elsewhere = [dict(offered[0], dataCenterAvailability=[{"dataCenterId": "US-KS-2"}])]
    monkeypatch.setattr(dev.subprocess, "run", lambda *a, **k: _Done(json.dumps(elsewhere)))
    with pytest.raises(SystemExit, match="not offered in EU-RO-1"):
        dev.offered_price()


def test_the_transport_gates_are_read_from_the_frozen_record_and_not_typed():
    """Plan §9a's borrow: v5b's numbers, and the 180 s dead-man DERIVED from the two fields that
    bound it rather than retyped out of that record's prose."""
    v5b = dev.load(dev.BORROWED_GATES)
    gates = dev.borrowed_gates()
    assert gates["boot_kill_seconds"] == v5b["money"]["arithmetic"]["boot_kill_seconds"]
    assert gates["delete_margin_seconds"] == v5b["money"]["arithmetic"]["delete_margin_seconds"]
    assert gates["max_recreates"] == v5b["go_no_go"]["gates"]["0_transport_ssh_deadman"][
        "max_recreates"
    ]
    assert (
        gates["ssh_deadman_seconds"] + gates["delete_margin_seconds"]
        == v5b["money"]["segments"]["a_dead_segment_costs_seconds"]
    )


def test_rung_zero_fits_at_the_dear_corner_and_refuses_when_the_cap_shrinks():
    """The gate's own inequality, both directions. A rung-0 that can only say yes is not a rung
    ([[guard_selftest_negative_control]]): the same table against a cap of ten cents does not fit,
    and the verdict is the DEAR corner's, never the cheap one's."""
    price = {"card": dev.CARD, "datacenter": "EU-RO-1", "stock": "Medium", "usd_per_hour": 0.74}
    threads = [{"channel": "@c", "thread_root": str(i)} for i in range(40)]
    wide = dev.rung_0(cap=2.50, price=price, threads=threads, n_posts=16)
    assert wide["fits"] and wide["dear_usd"] < 2.50
    assert wide["threads"] == dev.SMOKE_N + 40

    narrow = dev.rung_0(cap=0.10, price=price, threads=threads, n_posts=16)
    assert not narrow["fits"]
    assert narrow["table"][0]["fits"] is False
    assert "FITS" in dev.render_rung_0(wide) and "DOES NOT FIT" in dev.render_rung_0(narrow)


def test_the_bill_is_not_the_generation():
    """The sibling's overhead is a POSITIVE number read off a settled pod — boot, the 31B load, the
    scp and the delete. A corner that priced generation alone would price the wrong quantity."""
    overhead = dev.sibling_overhead()
    pod = dev.load(dev.SIBLING)["pods"][0]
    assert overhead["seconds"] > 0
    assert overhead["seconds"] == round(pod["billed_seconds"] - dev.borrowed_rate()["value"] * 75, 1)


def test_leg_b_pins_ids_and_not_a_count():
    """The 16 posts are enumerated from the store by S4's own subtraction; a count in prose is not
    the enumeration ([[count_in_prose_is_not_the_enumeration]])."""
    posts = dev.leg_b_posts()
    assert posts["posts"] == sum(len(ids) for ids in posts["by_channel"].values())
    assert posts["task"] == "positions_text_gm4"
    assert all(one.isdigit() for ids in posts["by_channel"].values() for one in ids)
