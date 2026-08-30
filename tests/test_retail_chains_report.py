"""The r2 table's three judgements: who represents a name, who is Ukrainian, what a column means.

Each is a place where the table could state something the measurement does not support.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from retail_chains_report import (  # noqa: E402
    UA_BAR,
    pick_aggregator,
    screen,
    sort_key,
    traffic,
)

# The four rows r1's name search returned for «MSUa», trimmed to the fields the picker reads.
MSUA = [
    {
        "handle": "@msualayi",
        "subscribers": 8319,
        "verdict": "enter",
        "stats": {"language_mix": {"en": 0.98, "other": 0.02}},
    },
    {"handle": "@msuauditorium", "subscribers": 385, "verdict": "reject", "stats": {}},
    {"handle": "@msuarabia", "subscribers": 185, "verdict": "reject", "stats": {}},
]
ZNISHKOM = [
    {
        "handle": "@znishkom",
        "subscribers": 7166,
        "verdict": "enter",
        "stats": {"language_mix": {"ua": 1.0}},
    },
    {
        "handle": "@znizkomn",
        "subscribers": 2322,
        "verdict": "enter",
        "stats": {"language_mix": {"ua": 0.77, "other": 0.1, "ru": 0.08, "en": 0.05}},
    },
]


def test_the_biggest_row_is_not_the_answer_when_it_is_moscow_state_university():
    # @msualayi has the most subscribers and an `enter` verdict, and it is a university in Moscow.
    # A picker keyed on size alone puts it in the census as Ukraine's promo aggregator «MSUa».
    assert pick_aggregator(MSUA) is None


def test_the_picker_takes_the_most_subscribed_row_that_survives_the_screen():
    assert pick_aggregator(ZNISHKOM)["handle"] == "@znishkom"


def test_a_verified_site_carries_the_row_that_its_language_would_not():
    # Varus posts 17% non-Ukrainian; the handle came off varus.ua, so the screen keeps it on the
    # site, not on the language. Rejecting a chain's own channel for its post mix is the failure.
    mixed = {"language_mix": {"ua": 0.83, "other": 0.17}}
    assert screen(from_own_site=True, stats=mixed)["ukraine_screen"] == "keep"
    russian = {"language_mix": {"ru": 1.0}}
    assert screen(from_own_site=True, stats=russian)["ukraine_screen"] == "keep"


def test_a_handle_with_no_site_behind_it_is_screened_on_language():
    # @skidka7 is `ru 1.00` and reached the census only through a name search — r1's Dv871 route.
    assert (
        "reject"
        in screen(from_own_site=False, stats={"language_mix": {"ru": 1.0}})["ukraine_screen"]
    )
    at_the_bar = {"language_mix": {"ua": UA_BAR}}
    assert screen(from_own_site=False, stats=at_the_bar)["ukraine_screen"] == "keep"


def test_a_group_reports_messages_and_says_so():
    # `com/d` on a megagroup is messages/day: the group has no comments under posts, and an
    # unmarked number would sort against broadcasts' comment rates as if it were one.
    group = {"is_group": True, "messages_per_day": 22.071, "comments_per_day": None}
    assert traffic(group) == "22.071*"
    broadcast = {"is_group": False, "comments_per_day": 16.643}
    assert traffic(broadcast) == "16.643"
    # A broadcast that genuinely has no reading still reads as unmeasured, not as zero.
    assert traffic({"is_group": False, "comments_per_day": None}) == "—"


def test_rows_sort_by_comments_then_price_and_channelless_rows_sink():
    rows = [
        {"name": "no-channel", "handle": None, "price_share": 0.9},
        {"name": "closed-high", "handle": "@a", "comments_enabled": False, "price_share": 0.88},
        {"name": "open-low", "handle": "@b", "comments_enabled": True, "price_share": 0.10},
        {"name": "open-high", "handle": "@c", "comments_enabled": True, "price_share": 0.76},
    ]
    assert [r["name"] for r in sorted(rows, key=sort_key)] == [
        "open-high",
        "open-low",
        "closed-high",
        "no-channel",
    ]
