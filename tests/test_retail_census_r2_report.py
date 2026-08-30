"""Every count the r2 report states, re-derived from the record it was built from.

The report's first paragraph is the deliverable: the operator decides on those numbers. Two of
them were wrong when first written — «exactly one row has open comments and dairy» (three do) and
a no-channel breakdown that summed to 28 of 23 rows. A number in prose is not the enumeration
([[count_in_prose_is_not_the_enumeration]]), so the enumeration checks the prose here.
"""

import re
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
            [r for r in no_channel if r.get("site_status") == "ok" and r.get("handles")]
        ),
        "read_no_link": len([r for r in no_channel if r.get("site_status") == "no-link"]),
        "never_read": len([r for r in no_channel if r.get("site_status") in ("blocked", "shell")]),
        "dns": len([r for r in no_channel if r.get("site_status") == "dns"]),
        "no_site": len([r for r in no_channel if r.get("site_status") == "no-site-verified"]),
        "screened": len([r for r in no_channel if r["name"] in AGGREGATORS]),
    }


def test_the_no_channel_reasons_partition_the_no_channel_rows():
    c = counts()
    assert c["with_channel"] + c["no_channel"] == c["rows"]
    parts = c["bot_only"] + c["read_no_link"] + c["never_read"] + c["dns"] + c["no_site"]
    assert parts + c["screened"] == c["no_channel"], (
        "the report's breakdown must account for every channel-less row exactly once"
    )


def test_the_report_states_the_counts_the_record_supports():
    c = counts()
    text = REPORT.read_text(encoding="utf-8")
    for phrase in (
        f"{c['with_channel']} of {c['rows']} rows have a channel",
        f"{c['open']} of those have comments",
        f"{c['open_with_dairy']} of those {c['open']} also carry dairy",
        f"**{c['no_channel']} rows have no channel**",
        f"{c['read_no_link']} site READ",
        f"{c['bot_only']} bot-only",
        f"{c['never_read']} sites never read",
        f"{c['dns']} domains that do not resolve",
        f"{c['no_site']} names with no verifiable site",
        f"{c['screened']} aggregators screened out",
    ):
        assert phrase in text, f"the report does not state: {phrase!r}"


def test_the_headline_row_is_the_one_the_record_ranks_first():
    """Varus is named as the answer; the record must still agree that it earns the naming."""
    table = {r["name"]: r for r in build()}
    varus = table["Varus"]
    assert varus["comments_enabled"] and varus["dairy_share"] > 0
    metro = table["METRO"]
    assert metro["comments_enabled"] and metro["dairy_share"] > 0
    # The claim is not «only Varus has both» — it is «only Varus has both WITH comment traffic».
    assert varus["comments_per_day"] > metro["comments_per_day"] * 100
    for number in (varus["comments_per_day"], metro["comments_per_day"]):
        assert re.search(rf"{number}", REPORT.read_text(encoding="utf-8")), number
