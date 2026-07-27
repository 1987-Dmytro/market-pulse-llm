"""Offline tests for the backfill cursor and the gate summary."""

from market_pulse.backfill import (
    GATE_COMMENTS,
    channel_row,
    load_cursor,
    render_summary,
    save_cursor,
    total_comments,
)
from market_pulse.raw_store import RawStore, post_record
from market_pulse.registry import Source
from test_raw_store import SOURCE, FakeMessage, provenance


def row(channel, *, posts=0, comments=0, stopped="since"):
    return {
        "channel": channel,
        "source_id": "varus",
        "comments_enabled": True,
        "n_posts": posts,
        "n_comments": comments,
        "first_post": "2024-07-01T08:00:00+00:00",
        "last_post": "2026-07-27T08:00:00+00:00",
        "stopped": stopped,
    }


def test_cursor_round_trip(tmp_path):
    path = tmp_path / "cursor.json"
    assert load_cursor(path) == {}

    save_cursor(path, {"@a": {"newest": 900, "oldest": 100}})
    assert load_cursor(path) == {"@a": {"newest": 900, "oldest": 100}}

    cursor = load_cursor(path)
    cursor["@a"]["oldest"] = 50
    save_cursor(path, cursor)
    assert load_cursor(path)["@a"] == {"newest": 900, "oldest": 50}


def test_a_damaged_cursor_restarts_the_walk_instead_of_the_run(tmp_path):
    path = tmp_path / "cursor.json"
    path.write_text('{"@a": {"newest": 9', encoding="utf-8")
    assert load_cursor(path) == {}


def test_channel_row_counts_the_store_not_the_run(tmp_path):
    store = RawStore(tmp_path)
    store.append(
        [post_record(FakeMessage(i, replies=1), SOURCE, "@c", provenance()) for i in (1, 2, 3)]
    )

    built = channel_row(store, SOURCE, "@c", "since")

    assert built["n_posts"] == 3
    assert built["n_comments"] == 0
    assert built["first_post"] == "2026-07-01T12:00:00+00:00"
    assert built["stopped"] == "since"


def test_a_posts_only_source_reports_no_comments(tmp_path):
    posts_only = Source("atb", "АТБ", "official_retail", ("@atb_market_official",), True, False)
    built = channel_row(RawStore(tmp_path), posts_only, "@atb_market_official", "exhausted")
    assert built["comments_enabled"] is False
    assert built["n_comments"] == 0


def test_gate_passes_on_the_total_across_channels():
    rows = [row("@a", comments=3000), row("@b", comments=2000)]
    assert total_comments(rows) == GATE_COMMENTS

    summary = render_summary(rows)
    assert "TOTAL comments: 5000 / 5000" in summary
    assert "GATE PASSED" in summary


def test_gate_fails_loudly_when_the_walk_was_complete():
    summary = render_summary([row("@a", comments=1200), row("@b", comments=300)])
    assert "GATE FAILED" in summary
    assert "team lead escalates" in summary


def test_an_unfinished_walk_is_not_reported_as_a_verdict():
    summary = render_summary([row("@a", comments=10, stopped="floodwait")])
    assert "GATE FAILED" in summary
    assert "rerun to completion" in summary
    assert "@a" in summary


def test_summary_lists_every_channel():
    summary = render_summary([row("@a", posts=10), row("@b", posts=20, stopped="not started")])
    assert "@a" in summary and "@b" in summary
    assert "not started" in summary
