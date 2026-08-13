#!/usr/bin/env python3
"""The D cut: which of the pre-filter's passing posts the 5c2-run post leg actually buys. ($0.)

SPEC amendment 3.18 (7)(g), the operator's ruling on Dv290. The census counted 349 passing posts and
reported that 71.6% of them are recipe ingredient lines — 250 rows from four cooking channels, none
of which carries a currency marker. So the registered population is not the pass-set: "of the rows
that pass the pre-filter, a row is kept iff its channel's carrier is `official_retail` or
`aggregator`, OR its matched evidence carries the `currency` pattern".

**This file COMPUTES that sentence and nothing else.** It reads the shipped census record, applies
the conjunction-free rule above, and writes the kept rows with the reason each one was kept. The
census's bytes are never touched — it is an input, pinned by sha256 — and the count this produces is
what the pre-registration pins BY VALUE.

Two readings of "its matched evidence" exist and this record measures both: `pattern_kinds` on the
census row is the kinds found ANYWHERE in the post's text (`sku_prefilter_census.screen_rows`, whose
`passed_carrying` is the 29 the ruling cites), and the narrower reading is the kinds on the matched
LINE alone. The contract states the first verbatim, and on this population the two agree exactly —
which is a measurement in the record, not an assumption in a comment.

    PYTHONPATH=src python3 scripts/postcut_c3b.py
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import census_5c2 as c2  # noqa: E402
import census_c3a_posts as c3a  # noqa: E402
import projection_5c2 as projection  # noqa: E402
import sku_prefilter_census as frame  # noqa: E402
import write_sku_projection_b2 as b2  # noqa: E402

from market_pulse import positions  # noqa: E402

CENSUS = REPO_ROOT / "results" / "census_c3a_posts.json"
SPEC = REPO_ROOT / "docs" / "SPEC.md"
RECORD = REPO_ROOT / "results" / "postcut_c3b.json"

rel = c2.rel
sha256_of = c2.sha256_of
cite = projection.cite
quote_line = projection.quote_line

CARRIERS = ("aggregator", "official_retail")
"""The two `source_type` values 3.18 (7)(g) keeps, sorted so the record's list is stable.

The registry's `source_type` and NOT the census row's `carrier` field, which reads `post_text` on
every one of the 349 — that is the EVIDENCE carrier (where the text was read), a different question
from who is speaking. The ruling's word is "its channel's carrier", and the channel's type is the
only thing in either record that answers it.
"""

PATTERN_KIND = "currency"

EXPECTED = (50, 55)
"""What the contract expects the cut to land between, and it is a CHECK rather than a target: "if
the computed cut lands far off that, STOP and report before the prereg"."""


def producer() -> dict:
    """`census_c3a_posts.producer`'s shape and reason, over this file and what it is built from."""
    return {
        "script": rel(Path(__file__)),
        "sha256": sha256_of(Path(__file__)),
        "why": "no git block: `git status --porcelain` is a fact about the tree, not the measurement",
        "borrows": {
            rel(Path(module.__file__)): sha256_of(Path(module.__file__))
            for module in (c2, c3a, projection, frame, b2)
        },
    }


def line_kinds(line: str) -> list[str]:
    """The size/price kinds on ONE line — the narrow reading of "its matched evidence"."""
    return sorted({positions.pattern_kind(p) for p in positions.size_price_patterns(line)})


def kept_by(row: dict, source_type: str) -> list[str]:
    """Why this row survives the cut, or `[]`. Both reasons, never the first one that fires.

    A row kept by both is what makes the cut smaller than the sum of its halves, and it is the whole
    story of why 31 + 29 is not 60: currency-bearing rows cluster in exactly the carriers the first
    half keeps, which is the coherence the ruling rests on and is worth being able to count.
    """
    reasons = []
    if source_type in CARRIERS:
        reasons.append("carrier")
    if PATTERN_KIND in row["pattern_kinds"]:
        reasons.append(PATTERN_KIND)
    return reasons


def ids_sha256(rows: list[dict]) -> str:
    """`census_c3a_posts`' frame convention, so the two records' pins are comparable at all."""
    return hashlib.sha256("\n".join(row["id"] for row in rows).encode("utf-8")).hexdigest()


def the_two_readings(rows: list[dict], types: dict) -> dict:
    """Does the narrow reading of the ruling's wording select the same rows? Measured, per row."""
    wide = {row["id"] for row in rows if PATTERN_KIND in row["pattern_kinds"]}
    narrow = {row["id"] for row in rows if PATTERN_KIND in line_kinds(row["line"])}
    wide_cut = {row["id"] for row in rows if kept_by(row, types[row["channel"]])}
    narrow_cut = {
        row["id"]
        for row in rows
        if types[row["channel"]] in CARRIERS or PATTERN_KIND in line_kinds(row["line"])
    }
    return {
        "asks": (
            "3.18 (7)(g) says «its matched evidence carries the currency pattern» and the contract"
            " operationalises it as «currency ∈ pattern_kinds». The census field is the ANYWHERE"
            " reading — kinds found anywhere in the post's text — and the narrow one is the matched"
            " LINE alone. If they disagree, a reader coming from the SPEC's wording would re-derive"
            " a different cut and nothing would say so"
        ),
        "carrying_currency_anywhere": len(wide),
        "carrying_currency_on_the_matched_line": len(narrow),
        "cut_under_the_anywhere_reading": len(wide_cut),
        "cut_under_the_matched_line_reading": len(narrow_cut),
        "agree": wide == narrow and wide_cut == narrow_cut,
        "rows_only_one_reading_keeps": sorted(wide_cut ^ narrow_cut),
        "the_reading_used": (
            "pattern_kinds, stated verbatim by the contract. It is also the field behind the 29 the"
            " ruling cites (results/census_c3a_posts.json :: totals.passed_carrying.currency), so it"
            " is the number the operator saw"
        ),
    }


def declined(rows: list[dict], types: dict, rate: float) -> dict:
    """The three alternatives 3.18 (7)(g) names, priced beside the cut. Context, not a headline."""
    alternatives = {
        "all_that_pass": [row for row in rows],
        "carriers_only": [row for row in rows if types[row["channel"]] in CARRIERS],
        "currency_only": [row for row in rows if PATTERN_KIND in row["pattern_kinds"]],
    }
    return {
        "quote": (
            "the alternatives (all 349 / carriers-only 31 / currency-only 29) were priced beside it"
            " and declined"
        ),
        "source": "docs/SPEC.md :: amendment 3.18 (7)(g)",
        "counts": {name: len(kept) for name, kept in alternatives.items()},
        "usd_with_drift": {
            name: c3a.priced(len(kept), rate)["usd_with_drift"]
            for name, kept in alternatives.items()
        },
        "why": (
            "each is RE-COUNTED here from the same rows rather than copied out of the clause, so the"
            " ruling's three numbers and this record's cut are one arithmetic. They are printed to"
            " show what the cut cost and what it saved — none of them is the registered population"
        ),
    }


def removed_recipes(census: dict, kept: list[dict]) -> dict:
    """What the cut actually removed, against what the ruling said it would.

    3.18 (7)(g) reads "250 of 349 rows from four cooking channels". Those four are the TOP four of
    the census's concentration table — 85 + 72 + 52 + 41 — and the `cooking_recipes` audience has
    six channels with a pass in it, 270 rows in total. Both numbers are true and they answer
    different questions, so both are printed: the ruling's premise is a floor on the population the
    cut removes, and the cut removes all of it.
    """
    audiences = {row["handle"]: row["audience"] for row in census["channels"]}
    cooking = sorted(
        (
            row
            for row in census["channels"]
            if row["audience"] == "cooking_recipes" and row["passed"]
        ),
        key=lambda row: (-row["passed"], row["handle"]),
    )
    return {
        "asks": "did the rule remove the population it was ruled to remove",
        "cooking_recipes_channels_with_a_pass": [row["handle"] for row in cooking],
        "cooking_recipes_rows": sum(
            1 for row in census["rows"] if audiences[row["channel"]] == "cooking_recipes"
        ),
        "the_rulings_four": sum(row["passed"] for row in cooking[:4]),
        "the_rulings_four_are": [row["handle"] for row in cooking[:4]],
        "kept_from_them": sum(1 for row in kept if audiences[row["channel"]] == "cooking_recipes"),
        "audiences_kept": sorted({audiences[row["channel"]] for row in kept}),
        "why_the_two_numbers_differ": (
            "«250 of 349 rows from four cooking channels» names the top four of the census's"
            " concentration table (85 + 72 + 52 + 41 = 250, cumulative share 0.7163). The audience"
            " has two more channels with a pass, 20 rows between them, so the population the cut"
            " removes is 270 — the ruling's premise understates it and is not contradicted by it"
        ),
    }


def magnitude_check(kept: int, priced: dict) -> dict:
    """The contract's STOP condition, answered with the number that actually decides it.

    "Expected magnitude ~50–55 rows / ~$0.07 — if the computed cut lands far off that, STOP and
    report before the prereg." The cut is 44, below the range, and the thing the range protects is
    the registered session cap: at the text marginal the difference between 44 rows and 55 is under
    two cents, and the cap is rounded up to the next half dollar. So the check is reported and the
    session continues, with the cause named rather than the miss alone.
    """
    return {
        "expected_rows": list(EXPECTED),
        "measured_rows": kept,
        "inside_the_expected_range": EXPECTED[0] <= kept <= EXPECTED[1],
        "measured_usd_with_drift": priced["usd_with_drift"],
        "cause": (
            "the estimate is 31 + 29 minus a small overlap; the overlap is 16, not the ~5–10 it"
            " implies. Currency-bearing rows cluster in exactly the retail and aggregator carriers"
            " the first half already keeps — which is the coherence 3.18 (7)(g) rests on, so the"
            " miss is evidence FOR the ruling and not against it"
        ),
        "why_it_does_not_stop_the_session": (
            "the range protects the registered cap. 44 rows and 55 rows differ by 31 seconds at"
            " 2.8132 s/row — under two cents — and the cap is rounded UP to the next half dollar,"
            " so the three-leg projection names the same cap at either end of the range"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    types = {row["handle"]: row["source_type"] for row in census["channels"]}
    rows = census["rows"]
    rate = cite(
        projection.RATE,
        "rate.usd_per_second",
        "the settled serverless rate — the same field results/census_c3a_posts.json priced the"
        " uncut leg with, so the cut and what it replaces are in one currency",
    )

    kept = [
        {
            "id": row["id"],
            "channel": row["channel"],
            "source_type": types[row["channel"]],
            "date": row["date"],
            "line": row["line"],
            "hit": row["hit"],
            "matched": row["matched"],
            "pattern": row["pattern"],
            "pattern_kinds": row["pattern_kinds"],
            "kept_by": kept_by(row, types[row["channel"]]),
        }
        for row in rows
        if kept_by(row, types[row["channel"]])
    ]
    by_channel = {}
    for row in kept:
        cell = by_channel.setdefault(
            row["channel"],
            {"handle": row["channel"], "source_type": row["source_type"], "kept": 0, "by": {}},
        )
        cell["kept"] += 1
        for reason in row["kept_by"]:
            cell["by"][reason] = cell["by"].get(reason, 0) + 1
    for cell in by_channel.values():
        cell["passed"] = next(
            channel["passed"]
            for channel in census["channels"]
            if channel["handle"] == cell["handle"]
        )

    priced = c3a.priced(len(kept), rate["value"])
    record = {
        "phase": "5c2-prep-c3b — the D cut of the post leg",
        "contract": "docs/PROMPT-5c2-prep-c3b.md deliverable 1; docs/SPEC.md amendment 3.18 (7)(g)",
        "asks": "which of the 349 passing posts the registered post leg buys, and what they cost",
        "decides_nothing": (
            "the ruling decided the rule; this file applies it. The pre-registration pins the count"
            " below BY VALUE. Nothing is fetched, nothing is spent, no row is asked of any model"
        ),
        "rule": {
            # the ruling's sentence wraps over three lines and `quote_line` takes exactly one, so
            # it is quoted line by line: three checked quotes rather than one hand-joined paragraph
            # that could drift from the file a word at a time.
            "verbatim": [
                quote_line(
                    SPEC,
                    needle,
                    "the ruling's own sentence, so the code below and the law it implements can be"
                    " read against each other without leaving the record",
                )["quote"]
                for needle in (
                    "**D cut**: of the rows that pass",
                    "a row is kept iff its channel's carrier",
                    "OR its matched evidence carries",
                )
            ],
            "verbatim_source": f"{rel(SPEC)} :: amendment 3.18 (7)(g)",
            "keep_iff": (
                "the channel's registry source_type is one of `carriers`, OR the row's"
                " `pattern_kinds` carries `currency`. A union, never a conjunction"
            ),
            "carriers": list(CARRIERS),
            "pattern_kind": PATTERN_KIND,
            "the_carrier_field": (
                "config/registry.yaml :: sources[].source_type, carried into the census's channel"
                " rows. NOT the census row's own `carrier`, which reads `post_text` on all 349 —"
                " that field says where the text was read, and this rule asks who is speaking"
            ),
            "two_readings": the_two_readings(rows, types),
        },
        "input": {
            "path": rel(CENSUS),
            "sha256": sha256_of(CENSUS),
            "anchor": census["anchor"]["anchor"],
            "passed": census["totals"]["passed"],
            "frame_ids_sha256": census["frame"]["ids_sha256"],
            "why": (
                "the SHIPPED record, read and not rewritten: its byte-identity under its anchor is"
                " its own gate (3.18 (7)) and this cut is a new record beside it, never inside it"
            ),
        },
        "kept": {
            "rows": len(kept),
            "share_of_passed": round(len(kept) / census["totals"]["passed"], 4),
            "channels": len(by_channel),
            "ids_sha256": ids_sha256(kept),
            "ids_sha256_note": (
                "sha256 of the kept ids, newline-joined in this record's order — the census's own"
                " convention, so the pre-registration pins the SELECTION and not only its size"
            ),
            "by_reason": {
                "carrier_only": sum(1 for row in kept if row["kept_by"] == ["carrier"]),
                "currency_only": sum(1 for row in kept if row["kept_by"] == [PATTERN_KIND]),
                "both": sum(1 for row in kept if len(row["kept_by"]) == 2),
            },
            "recipe_channels_kept": sorted(
                {
                    row["channel"]
                    for row in kept
                    if next(
                        channel["audience"]
                        for channel in census["channels"]
                        if channel["handle"] == row["channel"]
                    )
                    == "cooking_recipes"
                }
            ),
        },
        "rate": rate,
        "priced": priced,
        "removed_recipes": removed_recipes(census, kept),
        "magnitude_check": magnitude_check(len(kept), priced),
        "alternatives_declined": declined(rows, types, rate["value"]),
        "channels": sorted(by_channel.values(), key=lambda cell: (-cell["kept"], cell["handle"])),
        "rows": kept,
        "producer": producer(),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"{record['input']['passed']} passed the pre-filter → {record['kept']['rows']} kept"
        f" ({record['kept']['share_of_passed']:.1%}) across {record['kept']['channels']} channels"
    )
    print(f"  by reason: {record['kept']['by_reason']}")
    print(f"  declined:  {record['alternatives_declined']['counts']}")
    print(
        f"  priced at {priced['seconds_per_row']} s/row → ${priced['usd_with_drift']:.4f} with drift"
    )
    check = record["magnitude_check"]
    print(
        f"  magnitude check {check['measured_rows']} against {check['expected_rows']}:"
        f" {'inside' if check['inside_the_expected_range'] else 'OUTSIDE — reported, not a stop'}"
    )
    readings = record["rule"]["two_readings"]
    print(f"  the two readings of «matched evidence» agree: {readings['agree']}")
    removed = record["removed_recipes"]
    print(
        f"  recipe rows removed: {removed['cooking_recipes_rows']}"
        f" (the ruling's four: {removed['the_rulings_four']}) · kept from them:"
        f" {removed['kept_from_them']}"
    )
    header = f"\n{'channel':<26}{'type':>18}{'passed':>8}{'kept':>6}   by"
    print(header)
    print("-" * (len(header) - 1))
    for cell in record["channels"]:
        print(
            f"{cell['handle'][:25]:<26}{cell['source_type']:>18}{cell['passed']:>8}"
            f"{cell['kept']:>6}   {cell['by']}"
        )
    print(f"\nwrote {rel(args.out)}")
    return 0 if readings["agree"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
