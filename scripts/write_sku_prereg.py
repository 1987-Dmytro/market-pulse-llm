#!/usr/bin/env python3
"""Write `results/sku_pilot_prereg.json` — sku-b's three bars, before sku-b exists ($0).

Deliverable 5 of `docs/PROMPT-sku-a.md`. A pre-registration that is not committed is not a
pre-registration, and a pre-registration committed after the artifact it judges is a rationalisation:
git history is the only witness to the ordering, so this file goes in its own commit and no pilot
artifact exists in the repo yet.

Three things it carries, and the second is the one that costs work:

* **the bars, verbatim.** Quoted out of `docs/SPEC.md` amendment 3.17 (6) and checked against it on
  every run — a bar retyped is a bar that can drift from the law it claims to be.
* **the procedure for each one.** A ratio needs a denominator, and every denominator here had a
  question SPEC does not answer: the leaflet gold exists per POST while the bar says "per page", 4 of
  the 19 posts have an empty gold set, and bar 2's denominator is discovered by the run itself. Each
  reading is written down with what it excludes, and the ones that are the EXECUTOR's rather than
  SPEC's are listed in `ratification_required` — sku-b is one paid attempt and a failed bar closes B
  by measurement, so a denominator nobody ratified is a session spent against a void.
* **the inputs, pinned.** The reference record, the pack manifest, the census frame, the tier
  ladder's own hash and both prompt shas. Bar 3's gold is computed from the operator's ticks by
  `positions.tier_from_presence`, so the ladder is an input like any other. `docs/SPEC.md` is
  pinned as its REGISTERED LAW — the file with amendment 3.17 (7)'s marked block stripped, see
  `registered_law` — because that amendment records the ratification of readings already in here
  and a pin that follows the file is not a pin.

    PYTHONPATH=src python3 scripts/write_sku_prereg.py
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_audit_pack import git_state  # noqa: E402

from market_pulse import positions, prompts  # noqa: E402

SPEC = REPO_ROOT / "docs" / "SPEC.md"
REFERENCE = REPO_ROOT / "results" / "sku_reference_leaflet.json"
PACK_MANIFEST = REPO_ROOT / "results" / "sku_text_pack_manifest.json"
CENSUS = REPO_ROOT / "results" / "sku_prefilter_census.json"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
RECORD = REPO_ROOT / "results" / "sku_pilot_prereg.json"

BARS = {
    "leaflet_brand_recall": "leaflet brand-recall ≥ 0.75 per page vs audit-visible brands",
    "price_pair_accuracy": (
        "price-pair accuracy ≥ 0.80 on positions carrying a crossed-out price (verified by"
        " team-lead read of the per-position dump against the images at acceptance)"
    ),
    "text_tier_accuracy": "text tier-assignment accuracy ≥ 0.85 vs adjudicated rows",
}
"""The three bars of SPEC 3.17 (6), word for word. Checked against the file on every run."""

ONE_ATTEMPT = (
    "sku-b (one paid session, cap $0.35 GPU): the two-leg pilot (19 ATB posts page-wise; ~30"
    ' adjudicated text rows), one attempt; a failed bar closes B as "instrument not ready" by'
    " measurement."
)
GREEN_GATE = "Integration into the 5c2 loop only on a green gate."


def verbatim(spec: Path) -> str:
    """The amendment as one line, so a quote can be checked against it regardless of wrapping."""
    return " ".join(spec.read_text(encoding="utf-8").split())


def check_the_bars_are_the_laws(spec: Path) -> None:
    law = verbatim(spec)
    for name, bar in {**BARS, "one_attempt": ONE_ATTEMPT, "green_gate": GREEN_GATE}.items():
        if bar not in law:
            raise SystemExit(
                f"{name}: this text is not in docs/SPEC.md as written. A pre-registration that"
                " paraphrases its own bar cannot be held to it"
            )


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


RATIFICATION_BEGIN = "<!-- sku-b-ratification begin"
RATIFICATION_END = "<!-- sku-b-ratification end -->"
RATIFICATION_NAME = re.compile(r"^<!-- (sku-b-ratification(?:-\d+)?) begin", re.MULTILINE)
"""Every marked ratification block, by name. 3.17 (7) wears `sku-b-ratification` and 3.17 (8)
`sku-b-ratification-2`; a third would be `-3` and would be stripped by this same expression."""


def registered_law(spec: Path) -> bytes:
    """`docs/SPEC.md` with EVERY marked ratification block cut out, marker lines included.

    A ratification amendment records that readings this record already carries were accepted — it
    moves no bar, no threshold and no denominator — but it moves the file's bytes, and the pin
    predates it. Re-pinning would make the pin follow the file instead of holding it, so each such
    block wears its own markers and the REGISTERED LAW is what is left when they all come off.
    Stripping ALL of them (uni-b, for 3.17 (8)) rather than the first is what keeps the v1 pin
    `973c8789…` re-derivable after the second amendment lands: a strip that knew one block would
    leave (8) in the hash and the pre-registration would stop verifying at this commit.

    One implementation, called by the producer and by `tests/test_sku_prereg.py`: a second copy of
    this strip would drift from the one that writes the record and nothing downstream could see it.
    """
    text = spec.read_text(encoding="utf-8")
    for name in RATIFICATION_NAME.findall(text):
        begin, end_marker = f"<!-- {name} begin", f"<!-- {name} end -->"
        if text.count(begin) != 1 or text.count(end_marker) != 1:
            raise SystemExit(f"{rel(spec)}: ratification block {name} must appear exactly once")
        start = text.index(begin)
        end = text.index(end_marker, start) + len(end_marker)
        if (start and text[start - 1] != "\n") or not text[end:].startswith("\n"):
            raise SystemExit(f"{rel(spec)}: ratification block {name} does not own whole lines")
        text = text[:start] + text[end + 1 :]
    return text.encode("utf-8")


def pinned_sha256(path: Path) -> str:
    """What the pre-registration pins: for `docs/SPEC.md` the registered law, else the file."""
    return hashlib.sha256(registered_law(path) if path == SPEC else path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD)
    args = parser.parse_args(argv)
    check_the_bars_are_the_laws(SPEC)

    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    pack = json.loads(PACK_MANIFEST.read_text(encoding="utf-8"))
    scoreable = reference["gold"]["posts_with_a_non_empty_gold_set"]
    empty = reference["gold"]["posts_with_an_empty_gold_set"]

    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "sku-b — the position-layer pilot, pre-registered",
        "written_by": "sku-a (executor, $0), docs/PROMPT-sku-a.md deliverable 5",
        "authority": "docs/SPEC.md amendment 3.17 (6)",
        "class": (
            "PRE-REGISTRATION. Committed in its own commit before any sku-b artifact exists in the"
            " repo; git history is the only witness to that ordering. Nothing here is a result"
        ),
        "attempts": {
            "verbatim": ONE_ATTEMPT,
            "count": 1,
            "cap_usd": 0.35,
            "on_failure": (
                "a failed bar closes B as 'instrument not ready' BY MEASUREMENT. No retry, no"
                " re-prompt, no second draw: a bar re-run after its own result is not the bar that"
                " was registered"
            ),
            "on_success": GREEN_GATE,
        },
        "bars": {
            "leaflet_brand_recall": {
                "verbatim": BARS["leaflet_brand_recall"],
                "threshold": 0.75,
                "direction": ">=",
                "gold": {
                    "path": rel(REFERENCE),
                    "sha256": sha256_of(REFERENCE),
                    "pairs": reference["gold"]["pairs"],
                    "key": reference["gold"]["definition"],
                },
                "extraction_unit": (
                    "one PAGE, one call, under the registered prompt positions_post_gm4 (SPEC"
                    " 3.17 (4)). The page set is EXACTLY the 108 pages the reference names as sent —"
                    " not the 159 available. A brand printed on an unsent page is not in the gold,"
                    " so reading one would be scored as a false positive for being right"
                ),
                "denominator": (
                    "the 15 posts whose gold brand set is non-empty. Recall is computed PER POST as"
                    " |extracted ∩ gold| / |gold|, over the union of that post's page answers, and"
                    " the bar reads the MACRO MEAN of those 15 values. The micro reading over all 55"
                    " pairs is reported beside it and gates nothing"
                ),
                "why_not_per_page": (
                    "the bar says 'per page' and the gold cannot be split that way: one Opus"
                    " reviewer judged the whole sent set of a post and named what was visible across"
                    " it, so no artifact in this repo attributes a brand to a page. Building"
                    " per-page gold would be a new adjudication and is not in this contract. THIS IS"
                    " THE EXECUTOR'S READING — see ratification_required"
                ),
                "excluded": {
                    "posts": empty,
                    "why": (
                        "an empty gold set makes recall undefined, and an absolute bar over it fails"
                        " by arithmetic rather than by measurement"
                    ),
                    "instead": (
                        "they are a PRECISION probe: every brand extracted on their pages is a false"
                        " positive and is reported with its page. Their reviewer notes say what is"
                        " actually on them (summer non-food and similar)"
                    ),
                },
                "reported_never_gated": (
                    "precision on the 15 scoreable posts. The gold is ONE reviewer's reading in the"
                    " REVIEW class of SPEC 3.16 (1), so a brand the pilot finds and the reviewer did"
                    " not is not evidence of a false positive — SPEC gates recall only, and this"
                    " pre-registration does not widen it"
                ),
                "reachable": (
                    f"yes, measured before the run: {scoreable} of 19 posts carry a non-empty"
                    " gold set and 55 pairs sit on them"
                ),
            },
            "price_pair_accuracy": {
                "verbatim": BARS["price_pair_accuracy"],
                "threshold": 0.80,
                "direction": ">=",
                "denominator": (
                    "extracted positions carrying a crossed-out price — `price_old is not None` on a"
                    " position whose carrier is leaflet_page. Discovered BY THE RUN: nothing before"
                    " it can say how many of the 108 pages print an old price"
                ),
                "numerator": (
                    "positions whose (price_promo, price_old) pair the team lead marks correct"
                    " against the page image at acceptance. Both numbers, as one verdict: a right"
                    " promo beside a wrong old price is a wrong pair, because depth is computed from"
                    " the two of them"
                ),
                "procedure": (
                    "sku-b writes a per-position dump — one row per extracted position carrying"
                    " item, page number, the page's file and sha256, brand_raw, brand_id, line,"
                    " category, size, fat, price_promo, price_old, discount_pct_printed,"
                    " price_qualifier, the code-assigned tier, depth() and"
                    " depth_disagrees_with_printed(). The team lead opens each cited page image and"
                    " marks the pair correct or incorrect. The executor never scores its own sample"
                    " (SPEC §10), and the dump is what makes the read possible without re-running"
                    " anything"
                ),
                "reachability": {
                    "rule": (
                        "n >= 10 pairs: the bar is SCORED. 1 <= n < 10: the accuracy is REPORTED"
                        " with its n and the bar is NOT_SCORED — neither a PASS nor a closure of B,"
                        " and the team lead rules at acceptance whether the small-n reading stands."
                        " n = 0: NOT_REACHABLE, and the finding is that the pages carry no"
                        " crossed-out prices at all"
                    ),
                    "why": (
                        "at a 0.80 bar one error costs 10 pp at n=10 and 33 pp at n=3, so a small"
                        " denominator makes the threshold an artefact of arithmetic. Fixed here"
                        " rather than after the run, when the n is known and the temptation is"
                        " obvious. THIS IS THE EXECUTOR'S THRESHOLD — see ratification_required"
                    ),
                },
                "printed_percentage": (
                    "never substitutes the pair (SPEC 3.17 (3)). A position with a printed % and one"
                    " price is not in this denominator, and depth() returns None there"
                ),
            },
            "text_tier_accuracy": {
                "verbatim": BARS["text_tier_accuracy"],
                "threshold": 0.85,
                "direction": ">=",
                "gold": {
                    "pack": pack["pack"],
                    "manifest": rel(PACK_MANIFEST),
                    "manifest_sha256": sha256_of(PACK_MANIFEST),
                    "rows": pack["rows"],
                    "by_carrier": pack["draw"]["by_carrier"],
                    "computed_by": pack["ladder"]["function"],
                    "ladder_sha256": pack["ladder"]["sha256"],
                },
                "denominator": (
                    "the adjudicated rows that came back with a legal tick set. A row the operator"
                    " left untouched is not gold and is not counted"
                ),
                "comparison": (
                    "per ROW, the gold tier against the model's tier, both from the SAME function:"
                    " positions.tier_from_presence for the ticks, positions.tier for each parsed"
                    " position. A row naming several products is compared on its HIGHEST rung, and a"
                    " row whose ticks are all empty has gold `none` — the model must return [] to"
                    " agree with it"
                ),
                "unreadable_rows": (
                    "a reply the strict parser refuses is NOT scored as `none`. It is counted by its"
                    " reason, listed by id, and excluded from the denominator: an unreadable reply"
                    " and an empty answer are different outcomes, and conflating them would report"
                    " parse failures as rows with nothing in them. If unreadable rows exceed 10% of"
                    " the adjudicated set the bar is NOT_SCORED — the instrument did not answer"
                ),
                "reachability": {
                    "rule": (
                        "n >= 20 adjudicated rows: SCORED. Below that, REPORTED with its n and"
                        " NOT_SCORED"
                    ),
                    "why": "30 are drawn; a bar at 0.85 over fewer than 20 rows moves 5 pp per row",
                },
                "carrier": (
                    f"pooled over both carriers as drawn: {pack['draw']['by_carrier']}. Comments are"
                    f" {census['frame']['by_carrier']['comment']['passed']} of the frame's"
                    f" {census['frame']['rows']} rows, so this bar prices the POST leg. Whether the"
                    " comment carrier needs a bar of its own is a team-lead ruling — see"
                    " ratification_required"
                ),
                "also_measures": (
                    "the pre-filter's precision. A drawn row adjudicated as naming no position is a"
                    " pre-filter false positive; the frame is dominated by recipe feeds"
                    " (results/sku_prefilter_census.json), and this sample is the only thing that"
                    " prices it. Reported, not gated — SPEC does not put a bar on the filter"
                ),
            },
        },
        "ratification_required": [
            {
                "id": "R1",
                "bar": "leaflet_brand_recall",
                "question": (
                    "the bar says 'per page' and the gold is per POST. Registered reading: recall"
                    " per post over the union of its page answers, macro-averaged over the 15"
                    " posts with a non-empty gold set"
                ),
                "if_refused": (
                    "per-page gold does not exist and building it is a new adjudication. sku-b must"
                    " NOT run until this line is ratified: one attempt against a denominator nobody"
                    " agreed to is the paid session wasted"
                ),
            },
            {
                "id": "R2",
                "bar": "leaflet_brand_recall",
                "question": (
                    "the page set is the 108 pages the caption run SENT, not the 159 available. For"
                    " 15 of 19 posts that is the first six pages of a longer leaflet"
                ),
                "if_refused": (
                    "reading all 159 pages means brands with no gold behind them, which would score"
                    " as false positives for being correct"
                ),
            },
            {
                "id": "R3",
                "bar": "leaflet_brand_recall",
                "question": f"the 4 posts with an empty gold set are out of the recall average: {empty}",
                "if_refused": "recall is undefined there; the alternative is a bar that fails by arithmetic",
            },
            {
                "id": "R4",
                "bar": "price_pair_accuracy",
                "question": "n >= 10 pairs to score the bar; 1..9 reports and does not score; 0 is NOT_REACHABLE",
                "if_refused": "the team lead sets another n, in writing, before the run",
            },
            {
                "id": "R5",
                "bar": "text_tier_accuracy",
                "question": (
                    "unreadable replies are excluded and counted (>10% blocks the bar); n >= 20"
                    " adjudicated rows to score; both carriers pooled as drawn"
                ),
                "if_refused": "a stratified redraw is a different pack and this one is already built",
            },
        ],
        "instruments": {
            "positions_post_gm4": prompts.prompt_sha256("positions_post_gm4"),
            "positions_text_gm4": prompts.prompt_sha256("positions_text_gm4"),
            "note": (
                "the two registered prompts of SPEC 3.17 (5), pinned here so the pilot cannot be"
                " run under a revised text and reported against these bars. A revision is a new"
                " registration beside them, never an edit"
            ),
        },
        "pinned_inputs": {
            rel(path): pinned_sha256(path)
            for path in (SPEC, REFERENCE, PACK_MANIFEST, CENSUS, REGISTRY)
        },
        "ladder": {
            "sha256": positions.ladder_sha256(),
            "table": positions.ladder_table(),
            "why": (
                "bar 3's gold is computed from the operator's ticks by this ladder and the model's"
                " tier by the same function, so the ladder is an INPUT to the bar. Pinned as its"
                " whole 32-row table, not only as a hash, so a future reader can see what was"
                " registered without running this code"
            ),
        },
        "not_in_scope": {
            "the 5c3 rulings": (
                "«Варто» text-matching OFF and «Селянське» anchored-only are the 5c3 named revision"
                " (knowledge/decisions/sitting-2026-08-10-composition-signed.md) and are NOT applied"
                " to brand resolution here. A «Варто» the model reads off a page resolves like any"
                " other name, and the leaflet gold contains it because the reviewer saw it printed"
            ),
            "the 141 names": (
                "still outside the watchlist, so they resolve to `raw:` keys on both sides of bar 1."
                " That is symmetric and does not move the recall"
            ),
            "the frozen family": "T1v2, the frozen sets, results/baselines.json and the adapter are untouched",
            "aggregates": (
                "no promo aggregate is computed anywhere in sku-b. Question 7's brand x category x"
                " week rollup is 5c2's, and consumer quotes never enter it (SPEC 3.17 (4))"
            ),
        },
        "git": git_state(args.out),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {rel(args.out)}")
    for name, bar in record["bars"].items():
        print(f"  {name:<22} {bar['direction']} {bar['threshold']}  ({bar['verbatim'][:52]}…)")
    print(
        f"  {len(record['ratification_required'])} line(s) need a team-lead word before sku-b runs"
    )
    print(
        f"  ladder {positions.ladder_sha256()[:16]}… · prompts {record['instruments']['positions_post_gm4'][:8]}…/"
        f"{record['instruments']['positions_text_gm4'][:8]}…"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
