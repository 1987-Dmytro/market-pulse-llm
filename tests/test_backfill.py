"""Offline tests for the backfill cursor, the gate summary and the v1-write refusal."""

import asyncio
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import backfill as runner  # noqa: E402

from market_pulse.backfill import (  # noqa: E402
    GATE_COMMENTS,
    channel_row,
    load_cursor,
    render_summary,
    save_cursor,
    total_comments,
)
from market_pulse.raw_store import RawStore, post_record  # noqa: E402
from market_pulse.registry import Source  # noqa: E402
from test_raw_store import SOURCE, FakeMessage, provenance  # noqa: E402


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


WITH_COMMENTS = Source("varus", "Varus", "official_retail", ("@VARUS_channel",), True, True)
NO_COMMENTS = Source("aggr", "Aggr", "aggregator", ("@msuaaaa",), True, False)


def test_a_v1_comment_walk_is_refused_and_the_refusal_says_why():
    """v1 rows predate `reply_to_msg_id`; appending rows that carry it would leave one file
    whose records differ by a missing key, which reads downstream as `un-refetched`."""
    refusal = runner.v1_write_refusal([(WITH_COMMENTS, "@VARUS_channel")], allow=False)
    assert refusal is not None
    assert runner.V1_COMMENTS in refusal and "@VARUS_channel" in refusal
    assert "reply_to_msg_id" in refusal and "--allow-v1-write" in refusal
    assert "data/raw/comments_v2/" in refusal, "a refusal has to name the way forward"


def test_the_flag_is_the_only_thing_that_permits_it():
    """The negative control: the guard is worth having only if the flag actually lifts it."""
    channels = [(WITH_COMMENTS, "@VARUS_channel")]
    assert runner.v1_write_refusal(channels, allow=True) is None
    # a run that collects no comments at all writes nowhere near v1 and is not stopped
    assert runner.v1_write_refusal([(NO_COMMENTS, "@msuaaaa")], allow=False) is None


def test_main_stops_before_touching_the_network(monkeypatch):
    """The refusal fires on the argument list, before a client, a salt or a session is read."""
    monkeypatch.setattr(
        runner, "load_registry", lambda _: type("R", (), {"sources": [WITH_COMMENTS]})()
    )
    monkeypatch.setattr(
        runner, "build_client", lambda *a, **k: pytest.fail("a refused run built a client")
    )
    with pytest.raises(SystemExit, match="reply_to_msg_id"):
        asyncio.run(runner.main([]))
