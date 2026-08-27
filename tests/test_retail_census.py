"""Offline tests for the C1 retail census — no Telegram, no session."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import retail_census as census  # noqa: E402

from market_pulse.lexicon import load_lexicon  # noqa: E402
from market_pulse.yield_screen import compile_categories  # noqa: E402

DAY0 = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)
COMPILED = compile_categories(load_lexicon())


def msg(day=0, *, text="", media=False, replies=None, grouped_id=None, service=False):
    return {
        "date": (DAY0 + timedelta(days=day)).isoformat(),
        "grouped_id": grouped_id,
        "is_service": service,
        "replies": replies,
        "has_media": media,
        "text": text,
    }


def stats(rows, *, is_group=False, truncated=False):
    return census.census_stats(rows, truncated=truncated, is_group=is_group, compiled=COMPILED)


# --- the price column, and the deviation from the brief's literal ------------------------------


def test_the_briefs_literal_regex_misses_the_hryvnia_this_corpus_actually_writes():
    """`grn|₴|\\d+[,.]\\d\\d` as written is Latin; UA retail writes «грн».

    This is the whole reason both shares are reported: the deviation is a NUMBER the operator
    can read, not a claim in prose that the brief's pattern was wrong.
    """
    rows = [msg(text="Молоко 1л — 49 грн"), msg(text="Сир 200г — 89 грн")]
    out = stats(rows)
    assert out["price_share"] == 1.0, "«грн» is a price marker"
    assert out["price_share_contract_regex"] == 0.0, "the literal `grn` never fires here"
    assert out["price_branch_hits"] == {"грн": 2, "₴": 0, "grn": 0, "decimal": 0}


def test_the_decimal_branch_fires_on_a_date_and_the_counts_are_what_show_it():
    """«27.08.2026» matches `\\d+[,.]\\d\\d`. An unbroken-out share would hide that."""
    out = stats([msg(text="Акція діє з 27.08 по 30.08")])
    assert out["price_branch_hits"]["decimal"] == 1
    assert out["price_branch_hits"]["грн"] == 0
    assert out["price_share"] == 1.0, "the union still counts it — the branch says why"


def test_the_hryvnia_sign_and_a_real_decimal_price_both_count():
    out = stats([msg(text="Йогурт ₴34"), msg(text="Кефір 32,90")])
    assert out["price_branch_hits"] == {"грн": 0, "₴": 1, "grn": 0, "decimal": 1}
    assert out["price_share_contract_regex"] == 1.0, "both ARE in the brief's own pattern"


# --- the dairy column is the lexicon's own matcher ----------------------------------------------


def test_dairy_share_uses_the_lexicons_own_stems_and_endings():
    rows = [msg(text="Свіже молоко та сир"), msg(text="Пральний порошок"), msg(text="морозиво")]
    out = stats(rows)
    assert out["dairy_share"] == round(2 / 3, 3), "milk+cheese and ice cream, not the detergent"
    assert out["dairy_posts_per_day"] == round(2 / census.WINDOW_DAYS, 3)


def test_dairy_posts_per_day_is_the_product_the_sort_key_multiplies():
    """The sort column is not measured; it is posts/day x dairy share, written into every row."""
    rows = [msg(day=d, text="молоко") for d in range(14)] + [msg(day=d) for d in range(14)]
    out = stats(rows)
    assert out["posts_per_day"] == round(28 / census.WINDOW_DAYS, 3)
    assert out["dairy_share"] == 0.5
    assert out["dairy_posts_per_day"] == round(14 / census.WINDOW_DAYS, 3)


# --- albums are one post, on both sides ---------------------------------------------------------


def test_a_leaflet_album_is_one_post_and_is_judged_on_everything_it_carried():
    """Six pages at once is one post; the caption rides on one item and the media on the rest.

    Judging the collapsed post on whichever item came first would read a six-page leaflet with a
    price in its caption as a post with no price, or no media, depending on the order.
    """
    album = [
        msg(grouped_id=7, media=True),
        msg(grouped_id=7, media=True, text="Знижки тижня: молоко 49 грн"),
        msg(grouped_id=7, media=True),
    ]
    out = stats(album)
    assert out["n_posts"] == 1
    assert out["media_share"] == 1.0
    assert out["price_share"] == 1.0
    assert out["dairy_share"] == 1.0


def test_a_service_message_is_not_a_post():
    out = stats([msg(service=True), msg(text="привіт")])
    assert out["n_posts"] == 1


# --- a group is measured on messages, and never on comments -------------------------------------


def test_a_group_reports_messages_per_day_and_no_comment_rate():
    """The brief: «record messages_open and messages/day instead of comments/day».

    `None` and not `0.0`: nobody comments on a comment, and a zero there would read as a silent
    chat rather than as a column that does not apply.
    """
    out = stats([msg(day=d, text="продам") for d in range(14)], is_group=True)
    assert out["messages_per_day"] == round(14 / census.WINDOW_DAYS, 3)
    assert out["comments_per_day"] is None
    assert out["n_posts_with_comments"] is None


def test_a_channel_reports_a_comment_rate_and_no_message_rate():
    out = stats([msg(replies=10), msg(replies=4), msg(replies=0)])
    assert out["comments_per_day"] == round(14 / census.WINDOW_DAYS, 3)
    assert out["messages_per_day"] is None
    assert out["n_posts_with_comments"] == 2


def test_a_silent_channel_has_shares_of_none_not_of_zero():
    """No posts in the window: there is no denominator, and 0.0 would claim one."""
    out = stats([])
    assert out["n_posts"] == 0
    assert out["dairy_share"] is None and out["price_share"] is None
    assert out["posts_per_day"] == 0.0


# --- the verdict is the entry check's vocabulary -------------------------------------------------


def test_the_three_verdicts_are_the_briefs_three():
    assert census.CENSUS_VERDICTS == ("enter", "posts-only", "reject")


def test_a_channel_with_an_open_group_and_comments_enters():
    record = {
        "resolved": True,
        "telegram_verified": True,
        "comments_enabled": True,
        "broadcast": True,
    }
    out = census.census_verdict(record, stats([msg(replies=3)]), is_group=False, messages_open=True)
    assert out["verdict"] == "enter"


def test_comments_disabled_is_posts_only_with_the_entry_checks_own_reason():
    record = {
        "resolved": True,
        "telegram_verified": True,
        "comments_enabled": False,
        "broadcast": True,
    }
    out = census.census_verdict(record, stats([msg()]), is_group=False, messages_open=True)
    assert out["verdict"] == "posts-only"
    assert "comments disabled (no linked discussion group)" in out["reasons"]


def test_a_group_is_not_posts_onlyed_for_having_no_linked_group():
    """Every chat has `comments_enabled: False`, and build_verdict would posts-only the theme."""
    record = {
        "resolved": True,
        "telegram_verified": False,
        "comments_enabled": False,
        "megagroup": True,
    }
    out = census.census_verdict(
        record, stats([msg(text="продам")], is_group=True), is_group=True, messages_open=True
    )
    assert out["verdict"] == "enter"


def test_a_group_whose_history_needs_a_join_is_rejected_and_says_so():
    record = {
        "resolved": True,
        "telegram_verified": False,
        "comments_enabled": False,
        "megagroup": True,
    }
    out = census.census_verdict(
        record, stats([], is_group=True), is_group=True, messages_open=False
    )
    assert out["verdict"] == "reject"
    assert out["reasons"] == ["history is not readable without joining"]


def test_a_scam_flag_is_a_reject_not_a_posts_only():
    record = {"resolved": True, "telegram_verified": False, "scam": True, "comments_enabled": True}
    out = census.census_verdict(record, stats([msg()]), is_group=False, messages_open=True)
    assert out["verdict"] == "reject"


# --- the bound is logged, never silent -----------------------------------------------------------


BARS = {"retail_chains": 300, "poltava_chats": 100}


def test_a_row_below_the_bar_is_not_checked_and_keeps_its_free_fields():
    rows = [
        {"handle": "@big", "found_by": ["retail_chains:АТБ"], "search": {"subscribers": 5000}},
        {"handle": "@small", "found_by": ["retail_chains:АТБ"], "search": {"subscribers": 12}},
    ]
    picked = census.to_check(rows, BARS, None)
    assert [row["handle"] for row in picked] == ["@big"]


def test_the_check_list_is_ordered_by_reach_so_a_floodwait_costs_the_cheapest_rows():
    rows = [
        {"handle": f"@c{n}", "found_by": ["retail_chains:АТБ"], "search": {"subscribers": n}}
        for n in (400, 9000, 700)
    ]
    assert [row["handle"] for row in census.to_check(rows, BARS, 2)] == ["@c9000", "@c700"]


def test_an_already_checked_row_is_not_checked_again():
    rows = [
        {
            "handle": "@a",
            "checked": True,
            "found_by": ["retail_chains:АТБ"],
            "search": {"subscribers": 5000},
        }
    ]
    assert census.to_check(rows, BARS, None) == []


# --- the sort key is the brief's product, and its ties are named ---------------------------------


def test_the_sort_is_dairy_posts_per_day_times_one_plus_comments_per_day():
    loud = {"handle": "@a", "subscribers": 1, "stats": stats([msg(text="молоко", replies=28)])}
    quiet = {"handle": "@b", "subscribers": 1, "stats": stats([msg(text="молоко")])}
    assert census.sort_key(loud) < census.sort_key(quiet), "the commented row ranks first"


def test_two_zero_dairy_rows_break_their_tie_on_traffic_then_reach_then_handle():
    """Most of the table is zero dairy; without a named tiebreak the order reads as arbitrary."""
    busy = {"handle": "@b", "subscribers": 10, "stats": stats([msg(day=d) for d in range(5)])}
    idle = {"handle": "@a", "subscribers": 99, "stats": stats([msg()])}
    assert census.sort_key(busy) < census.sort_key(idle)


def test_a_store_row_never_outranks_an_api_row_on_a_month_old_number():
    """VARUS reads 15.43 comments/day in the store — a window that ended on 27 July.

    Sorted into one sequence it outranks anything measured this morning, and the ORDER would be
    asserting a comparison no measurement supports. Each instrument sorts inside its own block.
    """
    store = {
        "handle": "@varus",
        "measured_by": "store",
        "subscribers": 1,
        "search": {"subscribers": 1},
        "stats": stats([msg(text="молоко", replies=400)]),
    }
    api = {
        "handle": "@fresh",
        "measured_by": "api",
        "subscribers": 1,
        "search": {"subscribers": 1},
        "stats": stats([msg()]),
    }
    assert census.sort_key(api) < census.sort_key(store)
    assert census.INSTRUMENT_ORDER == {"api": 0, "store": 1}


def test_an_unchecked_row_sorts_last_and_does_not_crash_on_a_missing_stats_block():
    unchecked = {"handle": "@x", "search": {"subscribers": 9_000_000}}
    api = {"handle": "@a", "measured_by": "api", "search": {"subscribers": 1}, "stats": stats([])}
    assert census.sort_key(api) < census.sort_key(unchecked)


def test_the_two_themes_carry_different_bars_and_a_row_is_checked_if_either_wants_it():
    """One bar across both populations would answer «Машівка has no chat» with the budget."""
    bars = BARS
    town = {
        "handle": "@m",
        "found_by": ["poltava_chats:Машівка чат"],
        "search": {"subscribers": 150},
    }
    chain = {"handle": "@c", "found_by": ["retail_chains:АТБ"], "search": {"subscribers": 150}}
    both = {
        "handle": "@b",
        "found_by": ["retail_chains:Коло", "poltava_chats:Полтава чат"],
        "search": {"subscribers": 150},
    }
    assert census.bar_for(town, bars) == 100
    assert census.bar_for(chain, bars) == 300
    assert census.bar_for(both, bars) == 100, "the lower bar wins — either theme may want the row"
    assert [r["handle"] for r in census.to_check([town, chain, both], bars, None)] == ["@m", "@b"]
