"""Offline tests for Phase-5a channel discovery — no Telegram, no session."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

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
