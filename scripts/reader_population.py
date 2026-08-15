#!/usr/bin/env python3
"""The probe's population, ENUMERATED — the 111 threads `results/gate_census_w1.json` counted.

**Why this file exists.** The census records a COUNT: `grid["narrow|silencers_on"].threads == 111`,
`comments_payable == 912`. A probe cannot read a count; it reads threads, and «111» in prose is not
the list ([[count_in_prose_is_not_the_enumeration]]). So the keep predicate of `gate_census_w1.cell`
is applied here to name each one — and the enumeration is held to the census it claims to be, on
both numbers, by :func:`assert_is_the_census_cell`. That assertion is the test of this restatement:
if the two ever disagree, one of them is describing a population nobody priced.

**Why it is not a change to the census.** `scripts/gate_census_w1.py` is pinned by its own record
(`producer.sha256`) and `tests/test_gate_census_w1.py` re-derives the whole file, so a comment added
there would redden a sealed record for a reason nobody could connect to it
([[a_comment_only_edit_moves_the_files_hash]]). Every silencer, every lexicon and the carrier rule
are IMPORTED from it; what is written here is the ten lines `cell` keeps to itself.

**What a thread carries.** The post's text and its PAYABLE comments — the ones SPEC 3.19 (1) does
not skip before payment — each with the msg_id the reader's evidence will name. Text-less comments
are counted and never sent, exactly as the census priced them.

    PYTHONPATH=src python3 scripts/reader_population.py
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_aggregates as builder  # noqa: E402
import gate_census_w1 as census  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import brands, loop  # noqa: E402

CENSUS = REPO_ROOT / "results" / "gate_census_w1.json"
CELL = "narrow|silencers_on"
"""The cell `docs/PROMPT-probe-a.md` D3 fixes as the population: the LAW's vocabulary (dairy and
ice cream) with the three implementable silencers running."""


def gate():
    """The matcher the census cell was priced with: its aliases, its rules, its vocabulary."""
    prereg = json.loads(summary.read_text_or_refuse(builder.PREREG))
    registry = summary.registry_through_the_seal(prereg, builder.REGISTRY)
    return (
        brands.watchlist_aliases(registry.watchlist),
        brands.load_watchlist_rules(builder.RULES),
        census.compiled(wide=False),
    )


def window() -> list[dict]:
    """Every thread of the window: one post and the comments that reply to it."""
    comments = []
    for path in summary.leg_files(builder.DERIVED, loop.RECORD_TYPE):
        comments += summary.read_rows(path)
    threads, orphans = census.threads(comments, census.raw_posts())
    if orphans:
        raise SystemExit(f"{len(orphans)} threads have no post in the raw store: {orphans[:3]}")
    return threads


def population() -> list[dict]:
    """The 111, in the census's own order — channel, post id, post text, payable comments."""
    aliases, rules, categories = gate()
    kept = []
    for thread in window():
        surviving = [
            row for row in thread["comments"] if not census.silenced_comment(row, census.SILENCERS)
        ]
        # (text, carrier) per text and not one constant: SPEC 3.21 (1) scopes the garmonija rule to
        # comment text, and passing the comment carrier for the post would drop threads the census
        # kept — the census's own comment, and the reason this loop borrows its `hits`
        texts = [(thread["post_text"], census.POST_CARRIER)] + [
            (summary.comment_text(row), census.CARRIER) for row in surviving
        ]
        if not any(
            one["brands"] or one["categories"]
            for one in (
                census.hits(text, categories, aliases, rules, carrier) for text, carrier in texts
            )
        ):
            continue
        payable = [
            {"msg_id": int(row["msg_id"]), "text": summary.comment_text(row)}
            for row in surviving
            if loop.has_text(summary.comment_text(row))
        ]
        kept.append(
            {
                "channel": thread["channel"],
                "post_id": thread["post_id"],
                "post_text": thread["post_text"],
                "comments": payable,
                "silenced": len(thread["comments"]) - len(surviving),
                "text_less": len(surviving) - len(payable),
            }
        )
    assert_is_the_census_cell(kept)
    return kept


def assert_is_the_census_cell(kept: list[dict]) -> None:
    """Refuse unless this enumeration IS the cell — on the threads AND on the payable comments.

    Two numbers and not one: a restatement of the keep predicate that dropped a comment inside a
    thread it still kept would pass a thread count and change what every one of those threads costs.
    """
    cell = json.loads(summary.read_text_or_refuse(CENSUS))["grid"][CELL]
    payable = sum(len(one["comments"]) for one in kept)
    if (len(kept), payable) != (cell["threads"], cell["comments_payable"]):
        raise SystemExit(
            f"the enumeration is {len(kept)} threads and {payable} payable comments; the census"
            f" cell {CELL} is {cell['threads']} and {cell['comments_payable']}. One of the two"
            " describes a population nobody priced — stop and report."
        )


def census_sha256() -> str:
    """What the pre-registration pins the population BY: the record, not the count."""
    return summary.sha256_of(CENSUS)


def main(argv: list[str] | None = None) -> int:
    kept = population()
    sizes = sorted(len(one["comments"]) for one in kept)
    print(f"population {CELL}: {len(kept)} threads · {sum(sizes)} payable comments")
    print(f"  census {summary.rel(CENSUS)} sha256 {census_sha256()[:16]}…")
    print(
        f"  payable per thread: min {sizes[0]} · median {sizes[len(sizes) // 2]} · max {sizes[-1]}"
    )
    for one in sorted(kept, key=lambda one: -len(one["comments"]))[:3]:
        print(f"  largest: {one['channel']}:{one['post_id']} — {len(one['comments'])} payable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
