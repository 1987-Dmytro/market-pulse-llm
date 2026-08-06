"""Offline tests for Phase-5a channel discovery — no Telegram, no session."""

import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from telethon.errors import FloodWaitError

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import discover_channels as discovery  # noqa: E402

DAY0 = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)


def samples(*offsets, grouped_id=None):
    """`(date, comment_count, grouped_id, is_service)` rows, the shape entry_check collapses."""
    return [(DAY0 + timedelta(days=d), 0, grouped_id, False) for d in offsets]


def row(handle, subscribers, *, verdict="usable", ppw=1.0, comments=True):
    return {
        "handle": handle,
        "title": handle,
        "subscribers": subscribers,
        "discussion_group": comments,
        "posts_per_week": ppw,
        "language_mix": {},
        "last_post": None,
        "verdict": verdict,
    }


# --- the four-week window ----------------------------------------------------------------


def test_posts_per_week_is_over_the_fixed_window_not_the_sample_span():
    """14 posts in 28 days is 3.5/week however tightly they are bunched."""
    stats = discovery.window_stats(samples(*range(14)), [], truncated=False)
    assert stats["n_posts"] == 14
    assert stats["posts_per_week"] == 3.5
    assert stats["window_days"] == 28


def test_an_album_counts_as_one_post():
    stats = discovery.window_stats(samples(0, 0, 0, grouped_id=777), [], truncated=False)
    assert stats["n_posts"] == 1, "six pictures at once is one post, not six"


def test_the_language_mix_is_shares_of_the_texts_that_exist():
    stats = discovery.window_stats(
        samples(0, 1, 2), ["Дякую за знижки", "Спасибо за скидки"], False
    )
    assert stats["language_mix"] == {"ru": 0.5, "ua": 0.5}
    assert stats["n_texts"] == 2


def test_a_channel_silent_in_the_window():
    stats = discovery.window_stats([], [], truncated=False)
    assert stats["n_posts"] == 0
    assert stats["posts_per_week"] == 0.0
    assert stats["last_post"] is None
    assert stats["language_mix"] == {}


def test_a_truncated_scan_says_so():
    assert discovery.window_stats(samples(0), [], truncated=True)["window_truncated"] is True


# --- the row builder ---------------------------------------------------------------------


def test_a_candidate_row_survives_a_handle_that_did_not_resolve():
    """An unresolved entry_check record has no title, no subscribers and no traffic at all."""
    record = {"handle": "@dead", "resolved": False, "verdict": "unresolved", "reasons": ["gone"]}

    built = discovery.candidate_row(
        record, discovery.window_stats([], [], False), ["mothers_kids:мами"]
    )

    assert built["subscribers"] is None
    assert built["title"] is None
    assert built["discussion_group"] is False


# --- the coverage ledger -------------------------------------------------------------------


def test_the_ledger_sums_the_registry_and_ranks_the_candidates():
    ledger = discovery.build_ledger(
        [row("@a", 100_000), row("@b", 78_372)],
        [row("@small", 1_000), row("@big", 9_000)],
    )

    assert ledger["registry_subscribers"] == 178_372
    assert ledger["candidate_subscribers_total"] == 10_000
    assert [r["handle"] for r in ledger["ranked"]] == ["@big", "@small"], "ranked by size"
    assert [r["cumulative_subscribers"] for r in ledger["ranked"]] == [187_372, 188_372]
    assert ledger["ranked"][-1]["gap_after"] == discovery.COVERAGE_TARGET - 188_372


def test_a_channel_nothing_can_collect_from_adds_nothing_to_the_portfolio():
    ledger = discovery.build_ledger(
        [row("@a", 100)],
        [row("@dead", 500_000, verdict="unresolved"), row("@scam", 900_000, verdict="rejected")],
    )
    assert ledger["candidates_counted"] == 0
    assert ledger["portfolio_if_all_counted_entered"] == 100


def test_the_ledger_splits_the_silent_channels_out():
    """The second caveat as a number: subscribers of a channel that never posts are not flow."""
    ledger = discovery.build_ledger(
        [row("@a", 1_000)],
        [row("@live", 2_000, ppw=5.0), row("@silent", 400_000, ppw=0.0)],
    )

    assert ledger["candidates_posting_in_the_window"] == 1
    assert ledger["candidates_silent_in_the_window"] == 1
    assert ledger["portfolio_if_all_counted_entered"] == 403_000
    assert ledger["portfolio_if_only_live_entered"] == 3_000
    assert ledger["gap_if_only_live_entered"] == discovery.COVERAGE_TARGET - 3_000


def test_the_ledger_counts_the_channels_that_can_carry_comments():
    ledger = discovery.build_ledger([], [row("@a", 1, comments=True), row("@b", 2, comments=False)])
    assert ledger["with_a_discussion_group"] == 1


# --- the pre-registered scope ----------------------------------------------------------------


def test_only_the_three_authorised_themes_are_searched():
    assert set(discovery.THEMES) == {"mothers_kids", "healthy_lifestyle", "baby_food"}


def test_the_two_caveats_are_the_briefs_own_words():
    """Verbatim means verbatim — docs/PROMPT-5a.md spells them with ASCII `!=`."""
    assert discovery.CAVEATS == (
        "summed subscribers != unique reach",
        "subscribers != comment flow",
    )


def test_the_coverage_target_is_the_operators_number():
    assert discovery.COVERAGE_TARGET == 10_000_000


# --- re-deriving the ledger without a rescan --------------------------------------------------


def test_rebuild_ledger_re_derives_from_the_record_and_talks_to_nobody(monkeypatch, tmp_path):
    """A ledger rule that changed is recomputed from the rows already measured.

    The two fields that must not blur into each other: `generated_at` is when the channels were
    read, `ledger_rebuilt_at` is when the arithmetic over them was redone. A rebuild that moved
    the first would turn a re-derivation into a claim about a day nobody measured.
    """
    path = tmp_path / "discovery_5a.json"
    held = {
        "generated_at": "2026-08-05T18:00:00+00:00",
        "registry": {"path": "config/registry.yaml", "rows": [row("@a", 1_000)], "note": "x"},
        "candidates": [row("@live", 2_000, ppw=5.0), row("@silent", 400_000, ppw=0.0)],
        "ledger": {"stale": True},
    }
    path.write_text(json.dumps(held, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(discovery, "RECORD", path)
    monkeypatch.setattr(
        discovery, "build_client", lambda *a, **k: pytest.fail("a rebuild talked to Telegram")
    )

    assert discovery.main(["--rebuild-ledger"]) == 0

    rebuilt = json.loads(path.read_text(encoding="utf-8"))
    assert rebuilt["generated_at"] == held["generated_at"], "a rebuild is not a new measurement"
    assert rebuilt["ledger_rebuilt_at"] is not None
    assert rebuilt["candidates"] == held["candidates"], "rows are re-read, never re-measured"
    assert rebuilt["ledger"]["portfolio_if_only_live_entered"] == 3_000
    assert "stale" not in rebuilt["ledger"]


def test_a_normal_run_leaves_the_rebuild_stamp_empty(monkeypatch, tmp_path):
    """The negative control: the stamp has to be absent when nothing was rebuilt."""
    path = tmp_path / "discovery_5a.json"
    monkeypatch.setattr(discovery, "RECORD", path)

    async def scanned(_channels):
        return {
            "registry_rows": [row("@a", 1_000)],
            "candidates": [row("@live", 2_000, ppw=5.0)],
            "generated_at": datetime(2026, 8, 5, 18, tzinfo=timezone.utc),
            "flood_wait_seconds": None,
        }

    monkeypatch.setattr(discovery, "run", scanned)

    assert discovery.main([]) == 0

    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["ledger_rebuilt_at"] is None
    assert written["scan_complete"] is True


# --- F1: a rate limit is a wait, not a verdict -------------------------------------------------


class FakeClient:
    """Enough Telethon for `run()` to walk its loop. Nothing here reaches the network."""

    async def connect(self):
        pass

    async def is_user_authorized(self):
        return True

    async def disconnect(self):
        pass


def scan_over(monkeypatch, three_handles, blow_up_on):
    """Run the candidate loop over three handles, raising `blow_up_on(handle)` in `measure`."""
    checked = []

    async def measure(_client, _source, handle, _now):
        checked.append(handle)
        if (exc := blow_up_on(handle)) is not None:
            raise exc
        return (
            {"handle": handle, "resolved": True, "verdict": "usable", "subscribers": 1},
            discovery.window_stats([], [], False),
        )

    async def search(_client):
        return {handle: {"source": None, "found_by": ["t:q"]} for handle in three_handles}

    monkeypatch.setattr(discovery, "build_client", lambda *a, **k: FakeClient())
    monkeypatch.setattr(discovery, "search_themes", search)
    monkeypatch.setattr(discovery, "measure", measure)
    monkeypatch.setattr(discovery.entry_check, "PAUSE_SECONDS", 0)
    return asyncio.run(discovery.run([])), checked


def test_a_floodwait_aborts_the_scan_and_keeps_what_it_collected(monkeypatch):
    """PROMPT-5a1 F1. Telethon raises a wait; the generic handler below would call it a verdict.

    Two separate harms, and the test names both: the rate-limited channel is written down as
    `error` — a permanent judgement on a temporary state, which a ledger reader cannot tell
    from a channel that is genuinely broken — and the loop walks on into the next request
    while Telegram is still refusing.
    """
    result, checked = scan_over(
        monkeypatch,
        ["@one", "@two", "@three"],
        lambda handle: FloodWaitError(request=None, capture=42) if handle == "@two" else None,
    )

    assert [row["handle"] for row in result["candidates"]] == ["@one"]
    assert result["flood_wait_seconds"] == 42
    assert checked == ["@one", "@two"], "the scan kept hammering after the wait"
    assert "@two" not in {row["handle"] for row in result["candidates"]}


def test_an_ordinary_failure_is_still_one_bad_row_and_not_an_abort(monkeypatch):
    """The negative control for F1: only FloodWait aborts.

    Without this, "the scan stopped" passes for both the fix and a rewrite that gives up on
    the first channel with a broken handle — which is the behaviour the generic handler was
    written to prevent in the first place.
    """
    result, checked = scan_over(
        monkeypatch,
        ["@one", "@two", "@three"],
        lambda handle: RuntimeError("resolve blew up") if handle == "@two" else None,
    )

    assert [row["handle"] for row in result["candidates"]] == ["@one", "@two", "@three"]
    assert checked == ["@one", "@two", "@three"]
    assert result["flood_wait_seconds"] is None
    assert result["candidates"][1]["verdict"] == "error"
    assert "RuntimeError" in result["candidates"][1]["error"]


def test_a_scan_cut_short_says_so_in_the_record(monkeypatch, tmp_path):
    """A truncated scan writes a ledger that reads as complete unless the record admits it."""
    path = tmp_path / "discovery.json"
    monkeypatch.setattr(discovery, "RECORD", path)

    async def scanned(_channels):
        return {
            "registry_rows": [],
            "candidates": [row("@live", 2_000, ppw=5.0)],
            "generated_at": datetime(2026, 8, 6, 12, tzinfo=timezone.utc),
            "flood_wait_seconds": 300,
        }

    monkeypatch.setattr(discovery, "run", scanned)

    assert discovery.main([]) == 0

    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["scan_complete"] is False
    assert written["flood_wait_seconds"] == 300
