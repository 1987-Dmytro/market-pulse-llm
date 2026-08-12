#!/usr/bin/env python3
"""Bar 1's 29 missed gold pairs, laid out for the team lead's read of the page images. ($0)

`docs/PROMPT-sku-miss-pack.md`. Bar 1 (leaflet brand recall) failed at 0.3603 vs 0.75 over 15 posts:
26 of 55 gold keys were found and 29 were missed. A missed key can mean three different things and
the number cannot tell them apart — the brand may be printed with a price box (a real under-read),
visible without one (the bar asks for something the instrument does not extract), or not on the
sent pages at all (gold noise). Only the images answer that, so this file lays the table and the
team lead rules; SPEC §10 runs both ways and nothing here is a verdict.

Everything scored is recomputed through `sku_bar_verdicts.bar_one` — the same function, the same
`gold_key` on both halves — and then checked against the per-post rows of the shipped verdict
record. A second matching rule invented here would decompose a different bar's misses.

Two derived flags ride on **every** missed row rather than on its post's header, because the read
is dictated one row at a time and a fact in a header is lost for exactly the rows it decides:

* **unreadable pages** — a page the extractor refused contributes no brand to its post's union, so
  a brand only on that page is missed for a reason that is not the reader's. 16 of the 29 sit on
  such a post.
* **unmatched extractions** — a brand the instrument DID extract on this post that is in no gold
  key (bar 1's own `not_in_gold`). Carried verbatim and paired with nothing: any substring or
  transliteration pairing written here would be the new matching rule this file must not have.

    PYTHONPATH=src python3 scripts/build_sku_miss_pack.py
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_sku_reference_leaflet as leaflet  # noqa: E402
import sku_bar_verdicts as bars  # noqa: E402

from market_pulse import provenance  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry_as_pinned  # noqa: E402

PREREG = REPO_ROOT / "results" / "sku_pilot_prereg_v4.json"
RECORD = REPO_ROOT / "results" / "sku_b_positions_v4.json"
REFERENCE = REPO_ROOT / "results" / "sku_reference_leaflet.json"
VERDICTS = REPO_ROOT / "results" / "sku_bar_verdicts.json"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
OUT = REPO_ROOT / "results" / "sku_miss_pack.json"
SHEET = REPO_ROOT / "results" / "sku_miss_pack.md"

CONTRACT = "docs/PROMPT-sku-miss-pack.md — the pack IS the deliverable"

EXPECTED = {"posts": 15, "missed": 29, "found": 26}
"""Transcribed from the contract's own sentence ("missed pairs = 29, found = 26, over the 15
scoreable posts"), never computed from the rows below. A checksum derived from the thing it checks
agrees with every defect in it."""

CLASSES = {
    "a": "the brand is PRINTED on a sent page WITH a price box — a real under-read",
    "b": "the brand is VISIBLE on a sent page WITHOUT a price box — bar-vs-instrument mismatch",
    "c": "the brand is NOT VISIBLE on the sent pages at all — gold noise",
}
"""The contract's three classes, verbatim in substance. The vocabulary is the team lead's: this file
must not add a fourth even where a row fits none of them — it reports the flags and stops."""


def refuse(reason: str) -> None:
    raise SystemExit(f"refused: {reason}")


def display_names(post: dict, aliases: dict) -> dict[str, list[dict]]:
    """gold key → the reviewer's own strings behind it, with the field each was written in.

    `watchlist_hits` comes back as watchlist ids and `other_dairy_brands` as the name as printed;
    both are reproduced exactly as written, parentheticals included, because that string is what a
    (c) verdict is evidence about.
    """
    names: dict[str, list[dict]] = {}
    for field, source in (("watchlist", "watchlist_hits"), ("other_dairy_brands", None)):
        for name in post["brands_visible"][field]:
            key = leaflet.gold_key(name, aliases)
            names.setdefault(key, []).append({"source": source or field, "written": name})
    return names


def registry_names(gold_key: str, brands) -> list[str]:
    """The registry's display names for a key that is a watchlist brand id — a READING AID.

    Not part of the gold key and never compared with anything: `raw:svoia-liniia` is the key
    because the reviewer wrote the id, and «Своя Лінія» is what is actually printed on the page the
    team lead is about to open.
    """
    wanted = gold_key.removeprefix("raw:")
    for brand in brands:
        if brand.brand_id == wanted:
            return list(brand.display_names)
    return []


def page_answers(post: dict, record: dict, dump: list[dict]) -> list[dict]:
    """Per sent page, in order: what the instrument answered. Three states, never a fourth."""
    outcomes = {
        (out["item"], out["source"]): out for out in record["outcomes"] if out["leg"] == "page"
    }
    rows: dict[tuple[str, int], list[dict]] = {}
    for row in dump:
        if row["page"] is not None:
            rows.setdefault((row["item"], row["page"]), []).append(row)

    answers = []
    for page in post["pages_sent"]:
        outcome = outcomes.get((post["item"], page["file"]))
        if outcome is None:
            refuse(
                f"{post['item']} page {page['page']} {page['file']} has no outcome in the record"
            )
        extracted = rows.get((post["item"], page["page"]), [])
        # the outcome is found by FILE and the positions by PAGE NUMBER, two numberings that both
        # descend from the caption run's image order and are nowhere asserted to agree. If they
        # ever part, the sheet prints one page's brands under another page's name and sha, and the
        # team lead opens the wrong image — silently, for every row of the post.
        elsewhere = {row["file"] for row in extracted} - {page["file"]}
        if elsewhere:
            refuse(
                f"{post['item']} page {page['page']} is {page['file']} in the reference and the"
                f" dump files its positions under {sorted(elsewhere)}"
            )
        if outcome["unreadable"]:
            answer, reason = "unreadable", outcome["unreadable"]
            if extracted:
                refuse(
                    f"{post['item']} page {page['page']} is unreadable in the record and carries"
                    f" {len(extracted)} dump row(s) — the two halves describe different answers"
                )
        else:
            answer, reason = ("positions" if extracted else "empty"), None
            if outcome["n_positions"] != len(extracted):
                refuse(
                    f"{post['item']} page {page['page']}: the record counts"
                    f" {outcome['n_positions']} positions and the dump carries {len(extracted)}"
                )
        answers.append(
            {
                "page": page["page"],
                "file": page["file"],
                "sha256": page["sha256"],
                "answer": answer,
                "unreadable_reason": reason,
                "brand_raw": [row["brand_raw"] for row in extracted],
                "brand_id": [row["brand_id"] for row in extracted],
            }
        )
    return answers


def carriers(item: str, gold_key: str, dump: list[dict], aliases: dict) -> list[dict]:
    """The page(s) whose positions carried a FOUND key — the control half of the sheet.

    One row per page, because that is what the contract asks for; two positions of the same brand
    on one page are one page, and their count is kept beside the names they were written under.
    """
    on: dict[int, dict] = {}
    for row in dump:
        if row["item"] != item or row["page"] is None:
            continue
        if leaflet.gold_key(row["brand_id"] or row["brand_raw"], aliases) != gold_key:
            continue
        page = on.setdefault(
            row["page"], {"page": row["page"], "file": row["file"], "brand_raw": [], "positions": 0}
        )
        page["positions"] += 1
        if row["brand_raw"] not in page["brand_raw"]:
            page["brand_raw"].append(row["brand_raw"])
    return [on[page] for page in sorted(on)]


def build(record: dict, dump: list[dict], prereg: dict, reference: dict, aliases: dict, brands):
    bar = bars.bar_one(record, dump, prereg, reference, aliases)
    posts = {post["item"]: post for post in reference["posts"]}

    packed, missed, found = [], [], []
    for row in bar["per_post"]:
        post = posts[row["item"]]
        names = display_names(post, aliases)
        answers = page_answers(post, record, dump)
        unreadable = [
            {"page": page["page"], "file": page["file"], "reason": page["unreadable_reason"]}
            for page in answers
            if page["answer"] == "unreadable"
        ]
        packed.append(
            {
                "item": row["item"],
                "msg_id": post["msg_id"],
                "recall": row["recall"],
                "gold_keys": row["gold"],
                "found": row["found"],
                "missed": row["missed"],
                "unmatched_extractions": row["not_in_gold"],
                "pages_sent": len(answers),
                "pages_available": post["pages_available"],
                "pages_not_sent": len(post["pages_not_sent"]),
                "unreadable_pages": unreadable,
                "pages": answers,
                "reviewer_note": post["reviewer_note"],
            }
        )
        for key in row["missed"]:
            missed.append(
                {
                    "n": len(missed) + 1,
                    "item": row["item"],
                    "msg_id": post["msg_id"],
                    "gold_key": key,
                    "written_by_the_reviewer": names.get(key, []),
                    "registry_display_names": registry_names(key, brands),
                    "unreadable_pages": unreadable,
                    "unmatched_extractions_on_this_post": row["not_in_gold"],
                    "pages": answers,
                    "verdict": None,
                }
            )
        for key in row["found"]:
            found.append(
                {
                    "item": row["item"],
                    "msg_id": post["msg_id"],
                    "gold_key": key,
                    "written_by_the_reviewer": names.get(key, []),
                    "carried_by": carriers(row["item"], key, dump, aliases),
                }
            )

    for row in missed + found:
        if not row["written_by_the_reviewer"]:
            refuse(f"{row['item']} {row['gold_key']} has no name behind it in the reference")
    keys = [(row["item"], row["gold_key"]) for row in missed]
    if len(set(keys)) != len(keys):
        refuse(
            "two missed rows carry the same (post, gold key) — a dictated verdict could not join"
        )

    counted = {"posts": len(packed), "missed": len(missed), "found": len(found)}
    if counted != EXPECTED:
        refuse(f"the pack counts {counted} and the contract states {EXPECTED}")
    return bar, packed, missed, found, counted


def check_the_shipped_bar_is_this_bar(bar: dict, shipped: dict) -> None:
    """The recomputation against the record the pilot closed on — same route or a different bar."""
    theirs = shipped["bars"]["leaflet_brand_recall"]
    if bar["value"] != theirs["value"]:
        refuse(f"bar 1 recomputes to {bar['value']} and the shipped record says {theirs['value']}")
    mine = {
        row["item"]: (row["found"], row["missed"], row["not_in_gold"]) for row in bar["per_post"]
    }
    other = {
        row["item"]: (row["found"], row["missed"], row["not_in_gold"]) for row in theirs["per_post"]
    }
    if mine != other:
        differ = sorted(item for item in mine | other if mine.get(item) != other.get(item))
        refuse(f"the shipped per-post rows and this recomputation differ on {differ}")


def sheet(pack: dict) -> str:
    """The read-sheet: grouped by post, for reading the images beside it."""
    out = [
        "# sku-b bar 1 — the 29 missed gold pairs, packed for the team lead's read",
        "",
        f"Bar 1 read {pack['bar']['value']:.4f} vs {pack['bar']['threshold']:.2f} — "
        f"{pack['bar']['verdict']} — over {pack['checksums']['posts']} posts with a non-empty gold"
        f" set: {pack['checksums']['found']} of {pack['bar']['n_gold_keys']} gold keys found,"
        f" {pack['checksums']['missed']} missed. This file decomposes the misses and rules on"
        " nothing — the verdicts are the team lead's, from the page images.",
        "",
        "**The gold is per POST, not per page**: one reviewer named the brands visible across the"
        " pages sent for a post, so a missed key is missed by the post's whole union of page"
        " answers. **The pages are a slice** — `pages_available` names how many the post really"
        " has, and no brand on an unsent page is in this gold.",
        "",
        "Each page below is in one of three states: the `brand_raw` list the instrument extracted,"
        " `[]` (it answered and named nothing), or `UNREADABLE` with the reason the extractor"
        " refused the reply.",
        "",
        "## The three classes",
        "",
        *[f"- **{name}** — {text}" for name, text in CLASSES.items()],
        "",
        "## The posts",
        "",
    ]
    for post in pack["posts"]:
        out += [
            f"### {post['item']} — gold {len(post['gold_keys'])} · found {len(post['found'])} ·"
            f" missed {len(post['missed'])} · recall {post['recall']:.4f}",
            "",
            f"{post['pages_sent']} pages sent of {post['pages_available']} available"
            f" ({post['pages_not_sent']} not sent, and no brand on them is in this gold).",
            "",
            "| page | file | sha256 | the instrument answered |",
            "| --- | --- | --- | --- |",
        ]
        for page in post["pages"]:
            if page["answer"] == "unreadable":
                said = f"**UNREADABLE** — {page['unreadable_reason']}"
            elif page["answer"] == "empty":
                said = "`[]`"
            else:
                said = " · ".join(f"«{name}»" for name in page["brand_raw"])
            out.append(
                f"| {page['page']} | {Path(page['file']).name} | `{page['sha256'][:12]}…` | {said} |"
            )
        # an empty bold heading reads as missing data in a document a human scans, and both halves
        # are legitimately empty here: 4426 missed nothing and six posts found nothing
        out += ["", "**MISSED — to be ruled on**", ""] + (
            [] if post["missed"] else ["- — none", ""]
        )
        for row in pack["missed"]:
            if row["item"] != post["item"]:
                continue
            written = " · ".join(
                f"`{name['written']}` ({name['source']})" for name in row["written_by_the_reviewer"]
            )
            line = f"- **{row['n']}.** `{row['gold_key']}` — the reviewer wrote {written}"
            if row["registry_display_names"]:
                line += " · registry: " + " / ".join(
                    f"«{name}»" for name in row["registry_display_names"]
                )
            out.append(line)
            for flag in flags(row):
                out.append(f"  - {flag}")
        out += ["", "**FOUND — the control half**", ""] + (
            [] if post["found"] else ["- — none", ""]
        )
        for row in pack["found"]:
            if row["item"] != post["item"]:
                continue
            out.append(f"- `{row['gold_key']}` — {' · '.join(carried(row))}")
        out += ["", f"> Reviewer's note: {post['reviewer_note']}", ""]

    out += [
        "## The verdict template",
        "",
        "One line per missed pair. Write `a`, `b` or `c` in the last column; the classes are above."
        " The flag columns are facts about the post, carried onto every one of its rows so that a"
        " line can be ruled on without scrolling back — they are not a verdict and they pair with"
        " nothing.",
        "",
        "| # | post | gold key | reading as | unreadable pages | extracted here, in no gold key |"
        " verdict (a\\|b\\|c) |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in pack["missed"]:
        reading = " / ".join(f"«{name}»" for name in row["registry_display_names"]) or " · ".join(
            f"«{name['written']}»" for name in row["written_by_the_reviewer"]
        )
        unreadable = (
            ", ".join(f"p{page['page']}" for page in row["unreadable_pages"])
            if row["unreadable_pages"]
            else "—"
        )
        unmatched = (
            ", ".join(f"`{key}`" for key in row["unmatched_extractions_on_this_post"])
            if row["unmatched_extractions_on_this_post"]
            else "—"
        )
        out.append(
            f"| {row['n']} | {row['msg_id']} | `{row['gold_key']}` | {reading} | {unreadable} |"
            f" {unmatched} |  |"
        )
    # the constants, not the arguments: `--out`/`--sheet` exist for the tests, and the footer of
    # the read-sheet points at the pair a reader will actually open
    out += ["", f"Pack: `{OUT.relative_to(REPO_ROOT)}` · contract: `{CONTRACT.split()[0]}`", ""]
    return "\n".join(out)


def carried(row: dict) -> list[str]:
    """`p4 «Своя Лінія»` per page, with the position count when the page carried more than one."""
    said = []
    for hit in row["carried_by"]:
        names = "/".join(f"«{name}»" for name in hit["brand_raw"])
        count = "" if hit["positions"] == 1 else f" ×{hit['positions']}"
        said.append(f"p{hit['page']} {names}{count}")
    return said


def flags(row: dict) -> list[str]:
    """The two derived flags, worded the same in the JSON's reader and on the sheet."""
    said = []
    if row["unreadable_pages"]:
        pages = ", ".join(
            f"page {page['page']} ({page['reason']})" for page in row["unreadable_pages"]
        )
        said.append(
            f"⚠ this post has an unreadable page — {pages}. A page the extractor refused"
            " contributes no brand to the post's union"
        )
    if row["unmatched_extractions_on_this_post"]:
        keys = ", ".join(f"`{key}`" for key in row["unmatched_extractions_on_this_post"])
        said.append(
            f"⚠ the instrument extracted {keys} on this post and no gold key matches it. Stated as"
            " a fact about the post; nothing here claims it is this brand"
        )
    return said


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--dump", type=Path, help="default: the record's own dump path")
    parser.add_argument("--prereg", type=Path, default=PREREG)
    parser.add_argument("--reference", type=Path, default=REFERENCE)
    parser.add_argument("--verdicts", type=Path, default=VERDICTS)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--sheet", type=Path, default=SHEET)
    args = parser.parse_args(argv)

    record = json.loads(args.record.read_text(encoding="utf-8"))
    prereg = json.loads(args.prereg.read_text(encoding="utf-8"))
    shipped = json.loads(args.verdicts.read_text(encoding="utf-8"))
    args.dump = args.dump or REPO_ROOT / record["dump"]["path"]

    pins = bars.check_the_inputs_are_the_registered_ones(record, prereg, args)
    pins["record"] = {"path": bars.rel(args.record), "sha256": bars.sha256_of(args.record)}
    pins["verdicts"] = {"path": bars.rel(args.verdicts), "sha256": bars.sha256_of(args.verdicts)}

    reference = json.loads(args.reference.read_text(encoding="utf-8"))
    # the table the pre-registration pins, the same call `sku_bar_verdicts` makes: SPEC 3.17 (13)(b)
    # resolves «Three Bears» today and did not when this population was bought, and a pack built
    # through the new table would decompose 28 misses against a record that says 29
    watchlist = load_registry_as_pinned(
        prereg["pinned_inputs"]["config/registry.yaml"], REGISTRY
    ).watchlist
    dump = [json.loads(line) for line in args.dump.read_text(encoding="utf-8").splitlines() if line]
    bar, posts, missed, found, counted = build(
        record, dump, prereg, reference, watchlist_aliases(watchlist), watchlist
    )
    check_the_shipped_bar_is_this_bar(bar, shipped)

    pack = {
        "phase": "sku-b — bar 1's misses, packed for the team-lead read",
        "contract": CONTRACT,
        "class": (
            "PACK. Nothing here is scored and nothing is adjudicated: bar 1 is recomputed through"
            " sku_bar_verdicts.bar_one (the same gold_key on both halves) and checked against the"
            " shipped verdict record, and every verdict field is null until the team lead dictates"
        ),
        "pins": pins,
        "bar": {
            "value": bar["value"],
            "threshold": bar["threshold"],
            "verdict": bar["verdict"],
            "n_posts": bar["n_posts"],
            "n_gold_keys": bar["n_gold_keys"],
            "recomputed_by": "sku_bar_verdicts.bar_one",
            "checked_against": "results/sku_bar_verdicts.json bars.leaflet_brand_recall.per_post",
        },
        "checksums": counted,
        "checksums_source": "docs/PROMPT-sku-miss-pack.md, transcribed — not computed from the rows",
        "classes": CLASSES,
        "flags": {
            "unreadable_pages": (
                "a page the extractor refused contributes no brand to its post's union, so a brand"
                " printed only there is missed for a reason the images do not show"
            ),
            "unmatched_extractions_on_this_post": (
                "bar 1's own not_in_gold: a key the instrument extracted on this post that is in no"
                " gold key. Carried verbatim and paired with nothing — a pairing rule written here"
                " would be a second matching rule, and bar 1 has exactly one"
            ),
        },
        "posts": posts,
        "missed": missed,
        "found": found,
        "sheet": bars.rel(args.sheet),
    }
    pack["git"] = provenance.git_state(args.out)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(pack, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.sheet.write_text(sheet(pack), encoding="utf-8")

    on_unreadable = sum(1 for row in missed if row["unreadable_pages"])
    on_unmatched = sum(1 for row in missed if row["unmatched_extractions_on_this_post"])
    print(
        f"bar 1 {bar['value']:.4f} vs {bar['threshold']:.2f} {bar['verdict']} —"
        f" {counted['missed']} missed, {counted['found']} found, over {counted['posts']} posts"
    )
    print(f"  {on_unreadable} of the missed sit on a post with an unreadable page")
    print(f"  {on_unmatched} sit on a post where the instrument extracted an unmatched brand")
    print(f"wrote {bars.rel(args.out)} and {bars.rel(args.sheet)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
