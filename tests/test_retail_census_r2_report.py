"""Every count the r2 report states, re-derived from the record it was built from.

The report's first paragraph is the deliverable: the operator decides on those numbers. Three of
them were wrong when first written — «exactly one row has open comments and dairy» (three do), a
no-channel breakdown that summed to 28 of 23 rows, and a bot list that counted a florist's channel
as a bot. A number in prose is not the enumeration ([[count_in_prose_is_not_the_enumeration]]), so
the enumeration checks the prose here.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from retail_chains_report import AGGREGATORS, build  # noqa: E402

REPORT = Path(__file__).resolve().parents[1] / "docs" / "reports" / "retail-census-r2.md"


def counts() -> dict:
    table = build()
    with_channel = [r for r in table if r.get("handle")]
    no_channel = [r for r in table if not r.get("handle")]
    open_comments = [r for r in with_channel if r.get("comments_enabled")]
    return {
        "rows": len(table),
        "with_channel": len(with_channel),
        "open": len(open_comments),
        "open_with_dairy": len([r for r in open_comments if (r.get("dairy_share") or 0) > 0]),
        "no_channel": len(no_channel),
        "bot_only": len(
            [
                r
                for r in no_channel
                if r.get("site_status") == "ok"
                and any(r.get("kinds", {}).get(h) == "bot" for h in r.get("handles", []))
            ]
        ),
        "read_no_link": len([r for r in no_channel if r.get("site_status") == "no-link"]),
        "other_brand": len([r for r in no_channel if r.get("not_the_chains_channel")]),
        "never_read": len(
            [r for r in no_channel if r.get("site_status") in ("blocked", "shell", "dns")]
        ),
        "no_site": len([r for r in no_channel if r.get("site_status") == "no-site-verified"]),
        "screened": len([r for r in no_channel if r["name"] in AGGREGATORS]),
    }


def test_the_no_channel_reasons_partition_the_no_channel_rows():
    c = counts()
    assert c["with_channel"] + c["no_channel"] == c["rows"]
    parts = (
        c["bot_only"]
        + c["read_no_link"]
        + c["other_brand"]
        + c["never_read"]
        + c["no_site"]
        + c["screened"]
    )
    assert parts == c["no_channel"], (
        "the report's breakdown must account for every channel-less row exactly once"
    )


def test_every_row_was_read():
    """«Дочитай все»: no row may end on a fetch that never produced a page.

    `blocked` (Cloudflare), `shell` (a client-rendered stub) and `dns` are all «we never saw the
    page» — a state that must not survive into the deliverable as if it were «the chain has no
    channel». Zero of them is the claim the report makes; this is where it is checked.
    """
    assert counts()["never_read"] == 0, "a row is still unread"


def test_the_report_states_the_counts_the_record_supports():
    c = counts()
    text = REPORT.read_text(encoding="utf-8")
    for phrase in (
        f"{c['with_channel']} of {c['rows']} rows have a channel",
        f"{c['open']} of those have comments open",
        f"**{c['no_channel']} rows have no channel**",
        f"{c['bot_only']} link a bot and nothing else",
        f"{c['read_no_link']} were read and carry no `t.me`",
        f"{c['no_site']} have no verifiable site",
        f"{c['screened']} aggregators screened out",
    ):
        assert phrase in text, f"the report does not state: {phrase!r}"


def test_the_promo_thread_yield_is_the_number_the_report_leads_with():
    """The operator's ruling: only threads under PRICE posts count, the rest is noise.

    «16.6 comments/day» counts a thread under a recipe the same as a thread under a flyer. The
    report leads with the filtered number instead, so the filtered number is what is checked.
    """
    yielded = json.loads(
        (Path(__file__).resolve().parents[1] / "results" / "promo_comment_yield.json").read_text(
            encoding="utf-8"
        )
    )["total"]
    text = REPORT.read_text(encoding="utf-8")
    assert f"{yielded['under_price']:,}".replace(",", " ") in text
    assert f"{yielded['price_threads']} price threads" in text
    # Every comment is filed under exactly one bucket, or the headline is drawn from a partition
    # that loses rows.
    assert (
        yielded["under_price"] + yielded["under_no_price"] + yielded["orphan"]
        == yielded["comments"]
    )


def test_the_brand_probe_result_is_reported_as_verified_zero():
    """Four raw hits, hand-read, all false positives — the report must not carry the raw four.

    A count of 4 and a count of 0 are the same file unless the verification is recorded beside
    them, and the difference is «Гармонія is discussed in Poltava» versus «it is not» (Dv898).
    """
    probe = json.loads(
        (Path(__file__).resolve().parents[1] / "results" / "poltava_brand_probe.json").read_text(
            encoding="utf-8"
        )
    )
    assert probe["brand_hits_verified"] == 0
    assert probe["garmonija"] == 0
    assert probe["hand_verification"]["verdict"].startswith("ALL")
    text = REPORT.read_text(encoding="utf-8")
    assert f"{probe['texts_read']:,}".replace(",", " ") in text
    assert "ZERO real dairy-brand mentions" in text


def test_the_headline_row_is_the_one_the_record_ranks_first():
    """Varus is named as the answer; the record must still agree that it earns the naming."""
    table = {r["name"]: r for r in build()}
    varus = table["Varus"]
    assert varus["comments_enabled"] and varus["dairy_share"] > 0
    metro = table["METRO"]
    assert metro["comments_enabled"] and metro["dairy_share"] > 0
    # METRO's channel resolved to «HoReCaНець» — its B2B arm. The claim is not «only Varus has
    # both», it is «only Varus has both on a channel aimed at shoppers».
    assert "HoReCa" in (metro.get("channel_note") or ""), "the B2B note must stay on METRO's row"
    assert varus["comments_per_day"] > metro["comments_per_day"] * 100
