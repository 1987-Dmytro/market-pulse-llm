"""Offline core of the Phase-2b channel entry check (docs/SPEC.md §2, §9).

Everything here is pure: it takes facts already read from Telegram and turns them
into the numbers and the verdict the operator reviews. The network half lives in
``scripts/entry_check.py`` so this module stays testable without a session.
"""

from datetime import datetime
from statistics import median

# A post whose comment count is unknown (no linked discussion group) is None, not 0 —
# "comments disabled" and "nobody commented" are different findings.
Post = tuple[datetime, int | None]
Sample = tuple[datetime, int | None, int | None, bool]  # + grouped_id, is_service


def collapse_albums(samples: list[Sample]) -> list[Post]:
    """Reduce raw messages to one row per post.

    Retail channels post grouped media constantly and Telegram returns one message
    per album item, only one of which carries the reply counter. Counting them as
    separate posts inflates posts/day and deflates the share with comments.
    """
    posts: list[Post] = []
    index: dict[int, int] = {}
    for date, comments, grouped_id, is_service in samples:
        if is_service:
            continue
        if grouped_id is None:
            posts.append((date, comments))
            continue
        seen = index.get(grouped_id)
        if seen is None:
            index[grouped_id] = len(posts)
            posts.append((date, comments))
        elif comments is not None and posts[seen][1] is None:
            posts[seen] = (posts[seen][0], comments)
    return posts


def traffic_stats(posts: list[Post]) -> dict:
    """Posting rate and comment activity over the sampled window."""
    if not posts:
        return {
            "n_posts": 0,
            "first_post": None,
            "last_post": None,
            "window_days": 0.0,
            "posts_per_day": 0.0,
            "share_with_comments": 0.0,
            "median_comments": 0,
        }

    dates = sorted(date for date, _ in posts)
    window_days = (dates[-1] - dates[0]).total_seconds() / 86400
    counts = [c for _, c in posts if c is not None]
    return {
        "n_posts": len(posts),
        "first_post": dates[0].isoformat(),
        "last_post": dates[-1].isoformat(),
        "window_days": round(window_days, 1),
        # Floor of one day: a sample inside a single day still describes a day of traffic.
        "posts_per_day": round(len(posts) / max(window_days, 1.0), 2),
        "share_with_comments": round(len([c for c in counts if c > 0]) / len(posts), 2),
        "median_comments": median(counts) if counts else 0,
    }


def build_verdict(
    *,
    resolved: bool,
    telegram_verified: bool,
    scam: bool,
    fake: bool,
    comments_enabled: bool,
    stats: dict,
) -> dict:
    """Grade one channel. The verdict is about capability, the reasons about quality.

    Verdicts: ``unresolved`` (handle is dead), ``rejected`` (scam/fake — never
    collect from it), ``posts-only`` (launches yes, reactions no — SPEC §9 falls
    back to aggregators for those), ``usable`` (posts + comments).
    """
    reasons: list[str] = []
    if not resolved:
        return {"verdict": "unresolved", "reasons": ["handle does not resolve"]}
    if scam or fake:
        flag = "scam" if scam else "fake"
        return {"verdict": "rejected", "reasons": [f"Telegram flags this channel as {flag}"]}

    if not telegram_verified:
        reasons.append("no blue check — confirm this is the official channel")
    if not stats.get("n_posts"):
        reasons.append("no posts in the sampled window")
    if not comments_enabled:
        reasons.append("comments disabled (no linked discussion group)")
        return {"verdict": "posts-only", "reasons": reasons}
    if stats.get("share_with_comments") == 0:
        reasons.append("linked group present but no comments on the sampled posts")
    return {"verdict": "usable", "reasons": reasons}
