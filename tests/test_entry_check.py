"""Offline tests for the entry-check core — no Telegram, no session."""

from datetime import datetime, timedelta

from market_pulse.entry_check import build_verdict, collapse_albums, traffic_stats

DAY0 = datetime(2026, 7, 1, 12, 0)


def posts(*offsets_and_counts):
    return [(DAY0 + timedelta(days=d), c) for d, c in offsets_and_counts]


def test_traffic_stats_over_a_known_window():
    stats = traffic_stats(posts((0, 0), (2, 4), (4, 10), (10, 2)))

    assert stats["n_posts"] == 4
    assert stats["window_days"] == 10.0
    assert stats["posts_per_day"] == 0.4
    assert stats["share_with_comments"] == 0.75
    assert stats["median_comments"] == 3.0
    assert stats["first_post"] == DAY0.isoformat()


def test_traffic_stats_floors_the_window_at_one_day():
    # Three posts within an hour describe a day of traffic, not an infinite rate.
    same_day = [(DAY0, 1), (DAY0 + timedelta(minutes=20), 2), (DAY0 + timedelta(hours=1), 3)]
    assert traffic_stats(same_day)["posts_per_day"] == 3.0


def test_traffic_stats_of_an_empty_sample():
    stats = traffic_stats([])
    assert stats["n_posts"] == 0
    assert stats["posts_per_day"] == 0.0
    assert stats["first_post"] is None


def test_unknown_comment_counts_are_not_zeros():
    # Comments disabled: every count is None, so no median is invented.
    stats = traffic_stats(posts((0, None), (1, None)))
    assert stats["share_with_comments"] == 0.0
    assert stats["median_comments"] == 0


def test_collapse_albums_keeps_one_row_per_post():
    samples = [
        (DAY0, None, 111, False),  # album item without the reply counter
        (DAY0, 7, 111, False),  # ... and the one that carries it
        (DAY0 + timedelta(days=1), 3, None, False),
        (DAY0 + timedelta(days=2), None, None, True),  # service message
    ]
    assert collapse_albums(samples) == [(DAY0, 7), (DAY0 + timedelta(days=1), 3)]


def test_verdict_unresolved_handle():
    verdict = build_verdict(
        resolved=False,
        telegram_verified=False,
        scam=False,
        fake=False,
        comments_enabled=False,
        stats={},
    )
    assert verdict["verdict"] == "unresolved"


def test_verdict_rejects_scam_channel():
    verdict = build_verdict(
        resolved=True,
        telegram_verified=False,
        scam=True,
        fake=False,
        comments_enabled=True,
        stats=traffic_stats(posts((0, 5))),
    )
    assert verdict["verdict"] == "rejected"


def test_verdict_posts_only_without_a_discussion_group():
    verdict = build_verdict(
        resolved=True,
        telegram_verified=True,
        scam=False,
        fake=False,
        comments_enabled=False,
        stats=traffic_stats(posts((0, None), (1, None))),
    )
    assert verdict["verdict"] == "posts-only"
    assert any("comments disabled" in r for r in verdict["reasons"])


def test_verdict_flags_a_supergroup():
    verdict = build_verdict(
        resolved=True,
        telegram_verified=True,
        scam=False,
        fake=False,
        comments_enabled=True,
        stats=traffic_stats(posts((0, 4))),
        broadcast=False,
    )
    assert any("supergroup" in r for r in verdict["reasons"])


def test_verdict_usable_channel_flags_a_missing_blue_check():
    verdict = build_verdict(
        resolved=True,
        telegram_verified=False,
        scam=False,
        fake=False,
        comments_enabled=True,
        stats=traffic_stats(posts((0, 4), (1, 9))),
    )
    assert verdict["verdict"] == "usable"
    assert any("blue check" in r for r in verdict["reasons"])
