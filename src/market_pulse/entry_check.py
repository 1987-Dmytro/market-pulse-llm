"""Offline core of the Phase-2b channel entry check (docs/SPEC.md §2, §9).

Everything here is pure: it takes facts already read from Telegram and turns them
into the numbers and the verdict the operator reviews. The network half lives in
``scripts/entry_check.py`` so this module stays testable without a session.
"""

import re
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
    broadcast: bool = True,
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
    if not broadcast:
        # A supergroup resolves like a channel but is a chat: it may be the aggregator's
        # own community, or the discussion group of the channel we were actually after.
        reasons.append("supergroup, not a broadcast channel — confirm this is the right entity")
    if not stats.get("n_posts"):
        reasons.append("no posts in the sampled window")
    if not comments_enabled:
        reasons.append("comments disabled (no linked discussion group)")
        return {"verdict": "posts-only", "reasons": reasons}
    if stats.get("share_with_comments") == 0:
        reasons.append("linked group present but no comments on the sampled posts")
    return {"verdict": "usable", "reasons": reasons}


# --- Phase-5c1: the track-R entry gate over the launch composition -------------------------
#
# `build_verdict` above grades CAPABILITY (can this channel be collected from at all). The
# gate below grades ENTRY: the operator has already chosen the composition
# (docs/CHANNELS-launch.md, verdict 2026-08-06), and each channel is verified against the
# bucket it was chosen into before it reaches config/registry.yaml.

_CYRILLIC = re.compile(r"[Ѐ-ӿ]")
_LETTER = re.compile(r"[^\W\d_]")

GATE_MIN_LETTERED_TEXTS = 10
GATE_CYRILLIC_MIN = 0.5
"""Pre-registered before the run (PROMPT-5c1 D1: FAIL on "non-UA/RU dominant").

Below GATE_MIN_LETTERED_TEXTS the share is described and never decisive — five short posts
cannot carry a verdict. The controls the thresholds were picked on are in
`results/discovery_5a1.json`, the 2026-08-06 scan of the same candidates: @MAMIPEKER1 (Turkish,
excluded) reads 150 texts at cyrillic_share 0, while @berlin_food — excluded for its TOPIC —
writes Ukrainian, so language and theme are separate findings and only the first is mechanical.
"""

BUCKETS = {
    # posts_expected: canon lists a positive posting rate. group_expected: canon's class.
    "comments": {"posts_expected": True, "group_expected": True},
    "posts": {"posts_expected": True, "group_expected": False},
    "watch": {"posts_expected": False, "group_expected": True},
    # The late addition enters to have its class decided, so neither is asserted.
    "late": {"posts_expected": True, "group_expected": None},
    # A Poltava-oblast city feed ("Дозаявка №3"). Its class is not the gate's to decide either,
    # but for the opposite reason: the standing ruling already fixed it as posts-only because the
    # 5c2 thread filter does not exist yet, NOT because these channels lack groups — 11 of the 16
    # have one. Holding them to `posts` would raise "a discussion group is linked" against 11
    # channels whose linked group the ruling that placed them already accounted for. The group is
    # still measured and recorded; it is only not turned into a verdict.
    "city": {"posts_expected": True, "group_expected": None},
}

PRE_REGISTERED_FLAGS = {
    "@kolyastravinsky": "theme check (PROMPT-5c1 D1)",
    "@whowears": "theme check (PROMPT-5c1 D1)",
    "@marketopt_official": "class + comments confirm (PROMPT-5c1 D1)",
}
"""Flagged whatever the measurement says — the operator asked for these three by name."""


def script_mix(texts: list[str]) -> dict:
    """Share of the posts written in Cyrillic, over the posts that carry any letter at all.

    `langid.detect` cannot answer "is this a UA/RU channel": its ``other`` bucket holds both
    "no letters" (an emoji caption) and "Cyrillic, ua and ru tied" (any short comment), and on
    the 2026-08-06 scan that put channels the operator chose — @Wellosophy_Lesya, six texts —
    at a detect ua+ru share of 0.5. Script presence separates the actual failure mode (a
    Turkish or German channel) from the ambiguity, and the finer ua/ru/en mix stays beside it
    as description.
    """
    lettered = [text for text in texts if _LETTER.search(text)]
    cyrillic = [text for text in lettered if _CYRILLIC.search(text)]
    return {
        "n_texts": len(texts),
        "n_with_letters": len(lettered),
        "n_cyrillic": len(cyrillic),
        "cyrillic_share": round(len(cyrillic) / len(lettered), 2) if lettered else None,
        "decisive": len(lettered) >= GATE_MIN_LETTERED_TEXTS,
    }


def gate_verdict(*, handle: str, bucket: str, record: dict, window: dict, script: dict) -> dict:
    """PASS / FAIL / FLAG for one candidate, against the bucket the operator chose it into.

    FAIL is a closed list (PROMPT-5c1 D1): does not resolve · dead against its bucket's
    expectation · non-UA/RU dominant. Telegram's own scam/fake mark is mapped onto it — a
    channel Telegram flags may not enter a registry by silence — and the mapping is named in
    the record rather than left as an unhandled path.

    "Dead" is canon's own conjunction, not a rate test. `docs/CHANNELS-launch.md` excluded six
    channels as *"мёртв: ни постов за 28 дней, ни группы"* and put fourteen equally silent ones
    with a group into the watch bucket. Eight launch channels sit at a canon rate of 0.2-0.5
    posts/week, where zero posts in a 28-day window is the expected reading — a rate test would
    FAIL the operator's own picks on noise. Silence with a group present is a FLAG: the shape
    of a watch channel, and a bucket change is the operator's call.
    """
    if not record.get("resolved"):
        reason = record.get("error") or "handle does not resolve"
        return {"verdict": "FAIL", "fails": [f"does not resolve — {reason}"], "flags": []}

    fails, flags = [], []
    if record.get("scam") or record.get("fake"):
        mark = "scam" if record.get("scam") else "fake"
        fails.append(f"Telegram flags this channel as {mark}")

    share = script.get("cyrillic_share")
    if share is not None and share < GATE_CYRILLIC_MIN:
        text = f"non-UA/RU dominant — cyrillic_share {share} over {script['n_with_letters']} posts"
        (fails if script["decisive"] else flags).append(
            text
            if script["decisive"]
            else f"{text} (under {GATE_MIN_LETTERED_TEXTS}, not decisive)"
        )

    expectation = BUCKETS[bucket]
    group = record.get("discussion_group") or {}
    has_group = bool(record.get("comments_enabled"))
    posts = window.get("n_posts", 0)

    if expectation["posts_expected"] and posts == 0:
        if has_group:
            flags.append("silent in the 28-day window but the group is present — watch shape")
        else:
            fails.append("dead against its bucket — no posts in 28 days and no discussion group")
    if not expectation["posts_expected"] and posts:
        flags.append(f"watch bucket expects silence, {posts} posts in the 28-day window")

    if expectation["group_expected"] is True and not has_group:
        flags.append("bucket expects a discussion group, none is linked")
    if expectation["group_expected"] is False and has_group:
        flags.append("posts-only bucket, but a discussion group is linked")
    if has_group and not group.get("open"):
        flags.append(f"discussion group is not open — {', '.join(group.get('closed_because', []))}")
    if has_group and group.get("min"):
        flags.append("discussion group came back as a min object — its flags are not reliable")
    # The comment counters are the 50-post sample's, not the window's: they are read off each
    # post's reply counter (scripts/entry_check.py:70), and the window sample does not keep them.
    traffic = record.get("traffic") or {}
    if bucket == "comments" and has_group and traffic.get("share_with_comments") == 0:
        flags.append("group present but no comments on any of the sampled posts")

    if not record.get("broadcast", True):
        flags.append("supergroup, not a broadcast channel")
    if handle in PRE_REGISTERED_FLAGS:
        flags.append(f"pre-registered: {PRE_REGISTERED_FLAGS[handle]}")

    verdict = "FAIL" if fails else ("FLAG" if flags else "PASS")
    return {"verdict": verdict, "fails": fails, "flags": flags}
