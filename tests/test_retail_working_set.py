"""The working set's two judgements: what a channel is FOR, and why a district centre is empty.

Both are places where one word would cover several states the operator prices differently.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from retail_working_set import (  # noqa: E402
    FORMER_UA_BAR,
    POLTAVA_TOWNS,
    R1,
    poltava_rows,
    towns_of,
    why_empty,
)


def test_the_causes_of_an_empty_district_centre_stay_apart():
    """«Not covered» is several states, and only some of them money can fix.

    After the r3 scan: Чутове found nothing at any bar — no budget changes that. Диканька and
    Козельщина were measured and their chats resolve, are OPEN, and hold ZERO messages in the
    window — they exist and are silent, which is a third thing again. One word for all of them
    would price a dead chat and an unbought one the same.
    """
    rows = json.loads(R1.read_text(encoding="utf-8"))["rows"]
    assert "nothing found at any bar" in why_empty("Чутове", rows)
    for town in ("Диканька", "Козельщина"):
        assert "ZERO messages" in why_empty(town, rows), town


def test_the_lifted_language_bar_admits_the_chats_it_used_to_hide():
    """The operator lifted `ua >= 0.5` on 2026-08-30; language is a column now, not a filter.

    Котельва's only chat is `ua 0.38` — under the old bar the centre read as «not covered», which
    is a filter's decision wearing the shape of a coverage gap.
    """
    chats = poltava_rows()
    kotelva = [c for c in chats if "Котельва" in " ".join(c.get("found_by", []))]
    assert kotelva, "Котельва's chat must be in the working set now"
    share = (kotelva[0].get("stats") or {}).get("language_mix", {}).get("ua", 0)
    assert share < FORMER_UA_BAR, "this is the chat the old bar excluded"
    assert all(c.get("verdict") == "enter" for c in chats)


def test_a_town_with_chats_is_not_reported_as_empty():
    rows = json.loads(R1.read_text(encoding="utf-8"))["rows"]
    # A negative control on the helper itself: Полтава has eight chats, so no «empty» wording
    # may apply to it. Without this, a helper that always returned the same string would pass.
    assert "nothing found" not in why_empty("Полтава", rows)


def test_every_chat_is_filed_under_a_district_centre_the_spec_authorises():
    """A chat filed under a town SPEC v2 §3 never named would be collection outside the ruling."""
    rows = json.loads(R1.read_text(encoding="utf-8"))["rows"]
    chats = [r for r in rows if any(f.startswith("poltava_chats") for f in r.get("found_by", []))]
    assert chats, "the r1 record should carry the Poltava chats"
    for chat in chats:
        for town in towns_of(chat):
            assert town in POLTAVA_TOWNS, f"{chat['handle']} filed under unauthorised «{town}»"


def test_a_channel_with_comments_closed_never_reaches_the_comments_list():
    """A2 answers «where can the customer speak». A deep promo share does not qualify a row.

    ЕКО's price share is the highest of any chain and its comments are closed: if the two lists
    were one, it would sort to the top of a table about the customer's voice and contribute none.
    """
    from retail_working_set import build

    table = {r["name"]: r for r in build()}
    eko = table["ЕКО маркет"]
    assert eko["price_share"] > 0.8 and eko["comments_enabled"] is False
    working_set = (Path(__file__).resolve().parents[1] / "results" / "working_set.md").read_text(
        encoding="utf-8"
    )
    a2 = working_set.split("## A2")[1].split("## B")[0]
    assert "@ekomarket_shop" not in a2, "a closed channel is in the comments list"
    assert "@VARUS_channel" in a2
