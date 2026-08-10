#!/usr/bin/env python3
"""The Opus review's rows, aggregated for the operator's sitting (SPEC 3.16 (3)).

Every number this writes is a CANDIDATE. 3.16 (1) puts the whole program in the
REVIEW class: the deterministic matcher stays the sole judge of screen and G1e
numbers, screen v2 verdicts are not re-scored, and nothing here may reach
`results/baselines.json`. So the record says `review, not measurement` in the fields
themselves rather than in a header a later reader can skip, and every ratio is
carried beside the enumeration it was computed from — a per-channel-capped sample
judged by one reviewer produces a ratio that is a prompt for a sitting, not a rate.

What it refuses:

- **unvalidated rows.** `scripts/validate_opus_returns.py` is imported, not
  reimplemented; a file with any defect stops the run instead of contributing.
- **a protocol that moved.** The sha in the manifest is what the sessions were given.
  If `docs/PROMPT-opus-audit-protocol.md` at HEAD no longer hashes to it, the rows
  were produced under different instructions than the record would claim.
- **a model nobody declared.** `--model` defaults to `claude-opus-5` and is recorded
  as a DECLARATION: the returns file cannot prove which model wrote it, and 3.16 (2)
  says so — the pin that is possible is mandatory, the rest is why the class is review.

    PYTHONPATH=src python3 scripts/read_opus_audit.py

Reads the manifest and every returns file, writes `results/opus_audit_5c1.json`.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_opus_audit_packs as builder  # noqa: E402
import validate_opus_returns as validator  # noqa: E402
import yield_screen_5c1 as screen  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from build_opus_audit_packs import MANIFEST, PACK_DIR, digest, protocol_pin, rel  # noqa: E402
from market_pulse import yield_screen as core  # noqa: E402

RECORD = REPO_ROOT / "results" / "opus_audit_5c1.json"
MODEL = "claude-opus-5"

REVIEW = "review, not measurement"
"""The label 3.16 (1) requires on every candidate number, in the record itself."""

CONTEXT = 40
"""Characters kept either side of a matched alias, so the sitting can see the word it sits in."""


def protocol_at_head(manifest: dict) -> dict:
    """The protocol's sha at HEAD, and a stop if it is not the one the packs carry.

    `protocol_pin` is the same check the builder ran — tracked, and identical to HEAD —
    so the sha it returns IS the sha at HEAD, and the file is not read a second way to
    say so. What is new here is the comparison against the manifest: the protocol may
    move between building the packs and reading them, and the sessions were given the
    one the packs name.
    """
    pin = protocol_pin(REPO_ROOT / manifest["protocol"]["path"])
    if pin["sha256"] != manifest["protocol"]["sha256"]:
        raise SystemExit(
            f"{manifest['protocol']['path']}: sha256 {pin['sha256'][:16]}… at HEAD but the packs"
            f" were built against {manifest['protocol']['sha256'][:16]}…. The sessions were given"
            " the manifest's protocol; a record naming today's would describe instructions nobody"
            " ran under."
        )
    return pin


def brand_tallies(pairs: list[tuple[str, str]]) -> dict:
    """`{brand_id: {count, items}}` for a list of `(item, brand_id)`, biggest first."""
    out: dict[str, dict] = {}
    for item, brand_id in pairs:
        entry = out.setdefault(brand_id, {"count": 0, "items": []})
        entry["count"] += 1
        entry["items"].append(item)
    for entry in out.values():
        entry["items"] = sorted(entry["items"])
    return dict(sorted(out.items(), key=lambda pair: (-pair[1]["count"], pair[0])))


def ratio(numerator: int, denominator: int) -> float | None:
    """`None`, not 0.0, when there is nothing to divide by — the two are different findings."""
    return round(numerator / denominator, 4) if denominator else None


def verdicts_still_hold(manifest: dict, derived: dict[str, dict]) -> int:
    """Every manifest item's matcher verdict, re-derived today, against the one it was drawn with.

    `builder.reproduction` compares six aggregate cells per channel, and an aggregate cannot
    see a post whose text changed in place — the counts stay equal while the string the split
    reads underneath them does not. This is the same question asked per row, which is the
    granularity the split's claim is made at.
    """
    for entry in manifest["items"]:
        today = derived.get(entry["item"])
        if today is None:
            raise SystemExit(
                f"{entry['item']} is in the manifest but not in today's re-derivation. The post"
                " the reviewer judged is gone from the corpus, and a split over the rest would"
                " quietly drop it."
            )
        if today["matcher"]["watchlist_brands"] != entry["matcher"]["watchlist_brands"]:
            raise SystemExit(
                f"{entry['item']}: the matcher reads {today['matcher']['watchlist_brands']} today,"
                f" the manifest recorded {entry['matcher']['watchlist_brands']}. The corpus moved"
                " under the packs — the string this split would search is not the one the matcher"
                " was judged on."
            )
    return len(manifest["items"])


def matcher_strings(manifest: dict) -> tuple[dict[str, str], dict]:
    """The exact string the matcher read, per item, rebuilt from the screen's own inputs.

    Not a second implementation of anything: the screen record names its inputs, `check_pins`
    re-checks them, and `rederive` is the builder's own re-emission of screen v2 per post —
    which `surrogates` defines as the post's text, the caption that stands in for it, or the
    two joined. That string is what «is the brand name in the text or the caption» has to be
    asked against; asking it of anything else would price a different instrument.

    Three gates, because a split is only as good as the string under it: the screen record
    must still hash to what the manifest pinned, its six cells per channel must still
    reproduce, and every drawn item's verdict must still be the one the manifest recorded.
    The counts they were passed on come back beside the strings — a guard that leaves no
    number behind is indistinguishable from one a refactor stopped calling.
    """
    path = REPO_ROOT / manifest["screen"]["path"]
    if (found := digest(path)) != manifest["screen"]["sha256"]:
        raise SystemExit(
            f"{manifest['screen']['path']}: sha256 {found[:16]}…, the manifest pins"
            f" {manifest['screen']['sha256'][:16]}…. The packs were drawn from that record; the"
            " split cannot be re-derived from a different one."
        )
    record = json.loads(path.read_text(encoding="utf-8"))
    builder.check_pins(record)
    files = [REPO_ROOT / entry["path"] for entry in record["captions"]["files"]]
    captions, _ = screen.read_caption_files(
        files, [REPO_ROOT / entry["path"] for entry in record["captions"]["records"]]
    )
    derived = builder.rederive(record, captions, builder.caption_rows(files))
    reproduced = builder.reproduction(record, derived)
    index = {item["item"]: item for items in derived.values() for item in items}
    provenance = {
        "rebuilt_from": manifest["screen"]["path"],
        "sha256": found,
        "posts_rederived": len(index),
        "channels_reproduced": reproduced["channels"],
        "cells_per_channel": reproduced["cells_per_channel"],
        "verdicts_rechecked": verdicts_still_hold(manifest, index),
        "note": (
            "the string every split below searched. Screen v2 re-emitted per post, its six"
            " aggregate cells per channel equal to the record's, and every drawn item's matcher"
            " verdict equal to the one the manifest recorded — the last is the row-level check"
            " the aggregate one cannot make"
        ),
    }
    return {name: item["read_as"] or "" for name, item in index.items()}, provenance


def quote(haystack: str, start: int, end: int) -> str:
    """The matched alias with its neighbours, on one line — the sitting's own evidence.

    Casefolded, because that is the string the matcher searched: «Лимо» inside «Лимон» is
    only legible as a finding if the reader can see the word it was refused out of.
    """
    left = "…" if start > CONTEXT else ""
    right = "…" if end + CONTEXT < len(haystack) else ""
    window = haystack[max(0, start - CONTEXT) : end + CONTEXT]
    return f"{left}{' '.join(window.split())}{right}"


def fn_split(missed: list[tuple[str, str]], strings: dict[str, str], compiled: list) -> dict:
    """The reviewer's misses, divided by whether the name was in the string the matcher read.

    The team lead's ruling of 2026-08-10: a raw FN column reads as the matcher's recall and is
    nothing of the kind while the reviewer has the images and the matcher has a caption. So the
    misses are split deterministically — `fn_matcher`, where the brand's own name was in the
    text or the caption and the matcher did not emit it, against `fn_image_only`, where it was
    never in that string at all. The first is the lexicon's to answer, the second the
    captioner's; they have different owners and different remedies.

    The discriminator is `compile_aliases`' own patterns — casefolded and bounded by non-word
    characters — and not a substring test. The difference is not academic: the only «Лимо» in
    the pilot's @atb_aktsiyi:3087 sits inside «Лимон», which a bare `in` reads as the name
    being present and the matcher being wrong. `substring_would_disagree` carries exactly those
    pairs, so the choice of test is a field in the record rather than a footnote about it.
    """
    by_brand: dict[str, list[tuple]] = {}
    for pattern, brand_id, alias in compiled:
        by_brand.setdefault(brand_id, []).append((pattern, alias))

    on_the_matcher, image_only, loose = [], [], []
    for item, brand_id in missed:
        if item not in strings:
            raise SystemExit(
                f"{item}: no re-derived string, so «was the name in it» has no answer. An"
                " unsplit miss is not an image-only one."
            )
        if brand_id not in by_brand:
            raise SystemExit(
                f"{brand_id!r} is not a brand_id on the pinned watchlist. The misses and the"
                " alias table are in different id spaces, and every pair would fall through to"
                " fn_image_only without one alias ever being tried."
            )
        low = strings[item].casefold()
        hit = next(
            (
                (match, alias)
                for pattern, alias in by_brand[brand_id]
                if (match := pattern.search(low))
            ),
            None,
        )
        if hit:
            match, alias = hit
            on_the_matcher.append(
                {
                    "item": item,
                    "brand_id": brand_id,
                    "alias": alias,
                    "context": quote(low, match.start(), match.end()),
                }
            )
            continue
        image_only.append({"item": item, "brand_id": brand_id})
        for _, alias in by_brand[brand_id]:
            if (at := low.find(alias)) >= 0:
                loose.append(
                    {
                        "item": item,
                        "brand_id": brand_id,
                        "alias": alias,
                        "context": quote(low, at, at + len(alias)),
                    }
                )
                break
    return {
        "label": REVIEW,
        "ruling": (
            "docs/STATUS.md, team lead, 2026-08-10: the reader splits FN deterministically. The"
            " false positives stay raw on purpose — there is no committed list of already-ruled"
            " collisions, so reading them is the sitting's prose and not this script's arithmetic"
        ),
        "rule": (
            "the brand's own aliases from the pinned watchlist, compiled by"
            " market_pulse.yield_screen.compile_aliases — casefolded, bounded by non-word"
            " characters — searched over the exact string the matcher read (the post's text, the"
            " caption standing in for it, or the two joined). Not a substring test"
        ),
        "counts": {
            "pairs": len(on_the_matcher) + len(image_only),
            "fn_matcher": len(on_the_matcher),
            "fn_image_only": len(image_only),
            "substring_would_disagree": len(loose),
        },
        "fn_matcher": {
            "asks": "the name was in the string the matcher read and it did not emit the brand",
            "owner": "the lexicon and the alias table",
            "pairs": on_the_matcher,
        },
        "fn_image_only": {
            "asks": "the name was never in that string — the reviewer read it off the image",
            "owner": "the caption's coverage, not the matcher's recall",
            "pairs": image_only,
        },
        "substring_would_disagree": {
            "asks": (
                "pairs a bare `in` test would have called fn_matcher and the word-boundary rule"
                " refuses. Each one is the matcher being right, and each one is a row where a"
                " count taken the loose way differs from the count above"
            ),
            "pairs": loose,
        },
    }


def matcher_candidates(manifest: dict, rows: list[dict], strings: dict, compiled: list) -> dict:
    """The matcher against the reviewer, per channel, as (item, brand_id) pairs.

    Judged at the pair level rather than the post level: a post where the matcher found
    one of two brands is neither a hit nor a miss, and rolling it up to the post would
    have to decide which. Precision is over what the matcher emitted, recall over what
    the reviewer found, and both denominators are per-channel-capped samples — which is
    why every cell carries its enumeration and the label above.
    """
    items = {entry["item"]: entry for entry in manifest["items"]}
    by_channel: dict[str, dict] = {}
    false_positives: list[tuple[str, str]] = []
    missed: list[tuple[str, str]] = []
    by_stratum: dict[str, Counter] = {}
    for row in rows:
        matcher = set(items[row["item"]]["matcher"]["watchlist_brands"])
        reviewer = set(row["watchlist_hits"])
        entry = by_channel.setdefault(
            row["channel"],
            {"items_judged": 0, "tp": 0, "fp": 0, "fn": 0, "false_positives": [], "missed": []},
        )
        entry["items_judged"] += 1
        entry["tp"] += len(matcher & reviewer)
        for brand_id in sorted(matcher - reviewer):
            entry["fp"] += 1
            entry["false_positives"].append({"item": row["item"], "brand_id": brand_id})
            false_positives.append((row["item"], brand_id))
        for brand_id in sorted(reviewer - matcher):
            entry["fn"] += 1
            entry["missed"].append({"item": row["item"], "brand_id": brand_id})
            missed.append((row["item"], brand_id))
        for stratum in row["strata"]:
            tally = by_stratum.setdefault(stratum, Counter())
            tally["items_judged"] += 1
            tally["tp"] += len(matcher & reviewer)
            tally["fp"] += len(matcher - reviewer)
            tally["fn"] += len(reviewer - matcher)
    for entry in by_channel.values():
        entry["precision_candidate"] = ratio(entry["tp"], entry["tp"] + entry["fp"])
        entry["recall_candidate"] = ratio(entry["tp"], entry["tp"] + entry["fn"])
    totals = {key: sum(entry[key] for entry in by_channel.values()) for key in ("tp", "fp", "fn")}
    return {
        "label": REVIEW,
        "definition": (
            "one (item, brand_id) pair per brand. TP the matcher and the reviewer agree, FP the"
            " matcher emitted and the reviewer did not confirm, FN the reviewer named and the"
            " matcher did not. Precision over the matcher's emissions, recall over the reviewer's"
            " finds"
        ),
        "not_a_rate": (
            "S2 and S3 are per-channel samples capped at 10, drawn for leverage and not"
            " proportionally, and one reviewer judged them. These ratios are a prompt for the"
            " sitting of 3.16 (3); the matcher's own numbers are the screen's and do not move"
        ),
        "overall": {
            **totals,
            "items_judged": sum(entry["items_judged"] for entry in by_channel.values()),
            "precision_candidate": ratio(totals["tp"], totals["tp"] + totals["fp"]),
            "recall_candidate": ratio(totals["tp"], totals["tp"] + totals["fn"]),
        },
        "by_stratum": {
            name: {
                **dict(tally),
                "precision_candidate": ratio(tally["tp"], tally["tp"] + tally["fp"]),
                "recall_candidate": ratio(tally["tp"], tally["tp"] + tally["fn"]),
                **(
                    {}
                    if tally["tp"] + tally["fp"]
                    else {
                        "recall_is_definitional": (
                            "the matcher emitted nothing on this stratum, so tp is 0 by how the"
                            " stratum was drawn and the recall above is a definition, not a floor."
                            " S3 is the relevant posts the matcher found no brand in. Precision"
                            " comes back null for the same reason and the recall only looks like a"
                            " number because its denominator is not empty"
                        )
                    }
                ),
            }
            for name, tally in sorted(by_stratum.items())
        },
        "by_channel": dict(sorted(by_channel.items())),
        "false_positive_candidates": brand_tallies(false_positives),
        "false_positives_not_split": (
            "raw on purpose (team-lead ruling, 2026-08-10). Splitting them would need a committed"
            " list of collisions the operator has already ruled on, and there is none — «Президент»"
            " the head of state and «варто» the ordinary word are read at the sitting, not here"
        ),
        "missed_brand_candidates": brand_tallies(missed),
        "fn_split": fn_split(missed, strings, compiled),
    }


def caption_candidates(manifest: dict, rows: list[dict]) -> dict:
    """GM4's faithfulness, over the items that had something to be faithful to."""
    items = {entry["item"]: entry for entry in manifest["items"]}
    judgeable = [row for row in rows if items[row["item"]]["judgeable_caption"]]
    judged = [row for row in judgeable if row["caption_verdict"] != "n/a"]
    tally = Counter(row["caption_verdict"] for row in judged)
    by_channel: dict[str, dict] = {}
    for row in judged:
        entry = by_channel.setdefault(
            row["channel"], {"judged": 0, **{v: 0 for v in ("faithful", "partial", "wrong")}}
        )
        entry["judged"] += 1
        entry[row["caption_verdict"]] += 1
    for entry in by_channel.values():
        entry["faithful_rate_candidate"] = ratio(entry["faithful"], entry["judged"])
    return {
        "label": REVIEW,
        "instrument_judged": "gm4-nf4-base captions over their sha-matched sent images",
        "denominator": (
            "items whose caption a model wrote over images that are on disk under the sha the"
            " caption row recorded. Poll transcriptions carry no image and no model and are not in"
            " it — they would otherwise put free deterministic rows into GM4's rate"
        ),
        "judgeable": len(judgeable),
        "judged": len(judged),
        "declined_n_a": len(judgeable) - len(judged),
        "tally": dict(sorted(tally.items())),
        "faithful_rate_candidate": ratio(tally.get("faithful", 0), len(judged)),
        "by_channel": dict(sorted(by_channel.items())),
        "brands_visible_missed": brand_tallies(
            [(row["item"], brand_id) for row in judged for brand_id in row["brands_visible_missed"]]
        ),
    }


def open_extraction(rows: list[dict]) -> dict:
    """Dairy and ice-cream names outside the watchlist, as the reviewer spelled them.

    Not normalised beyond whitespace and case: the spelling IS the finding when the
    question is whether the watchlist is missing an entity, and folding «Дольче» into
    «дольче» is as far as a script may go before the sitting has ruled.
    """
    out: dict[str, dict] = {}
    for row in rows:
        for name in row["other_dairy_brands"]:
            entry = out.setdefault(name.casefold(), {"count": 0, "as_written": [], "items": []})
            entry["count"] += 1
            entry["items"].append(row["item"])
            if name not in entry["as_written"]:
                entry["as_written"].append(name)
    for entry in out.values():
        entry["items"] = sorted(entry["items"])
    return dict(sorted(out.items(), key=lambda pair: (-pair[1]["count"], pair[0])))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--pack", type=Path, default=PACK_DIR)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--model", default=MODEL, help="the model the sessions declared")
    parser.add_argument("returns", type=Path, nargs="*", help="default: every returns_NN.jsonl")
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    protocol = protocol_at_head(manifest)
    paths = args.returns or sorted(args.pack.glob("returns_*.jsonl"))
    if not paths:
        raise SystemExit(
            f"no returns_NN.jsonl in {rel(args.pack)}. The sessions are the operator's to run"
            " (docs/PROMPT-opus-audit-a.md), and an aggregate over nothing is not a finding"
        )

    by_pack, defects, covered = validator.collect(manifest, list(paths))
    if defects:
        raise SystemExit(
            f"{len(defects)} defect(s) in the returns — aggregating them would launder a bad row"
            f" into a candidate number. Run scripts/validate_opus_returns.py:\n  "
            + "\n  ".join(defects[:5])
        )
    rows = [row for pack in sorted(by_pack) for row in by_pack[pack]]
    strings, provenance = matcher_strings(manifest)
    compiled = core.compile_aliases(validator.aliases(manifest))

    record = {
        "read_by": "scripts/read_opus_audit.py",
        "class": (
            "REVIEW, never measurement (SPEC 3.16 (1)). Nothing in this file may enter a gate, the"
            " screen or results/baselines.json. The deterministic matcher remains the sole judge of"
            " screen and G1e numbers; screen v2 verdicts are not re-scored; the prereg bars do not"
            " move. These are candidates for the operator sitting of 3.16 (3)"
        ),
        "instrument": {
            "model": args.model,
            "protocol_sha": protocol["sha256"],
            "protocol_path": protocol["path"],
            "protocol_head": protocol["head"],
            "declared_not_verified": (
                "the model is what the session declared on its first line, per the protocol's rule"
                " 1 — a returns file cannot prove which model wrote it. Price is unpinnable"
                " (subscription). 3.16 (2): the pin that is possible is mandatory, and the rest is"
                " why the output class is review"
            ),
        },
        "manifest": {"path": rel(args.manifest), "sha256": digest(args.manifest)},
        "matcher_strings": provenance,
        "seed": manifest["seed"],
        "coverage": {
            "packs_in_manifest": len(manifest["packs"]),
            "packs_returned": sorted(by_pack),
            "items_in_returned_packs": sum(entry["items"] for entry in covered),
            "items_in_all_packs": manifest["items_total"],
            "rows_read": len(rows),
            "unanswered": sorted(item for entry in covered for item in entry["unanswered"]),
            "by_pack": covered,
            "note": (
                "packs the operator has not run are absent, not zero. Every rate below is over the"
                " rows that came back and names its own denominator"
            ),
        },
        "matcher_candidates": matcher_candidates(manifest, rows, strings, compiled),
        "caption_candidates": caption_candidates(manifest, rows),
        "open_extraction_candidates": {
            "label": REVIEW,
            "asks": "dairy / ice-cream names present that the watchlist does not carry",
            "names": open_extraction(rows),
        },
        "notes": [
            {"item": row["item"], "channel": row["channel"], "note": row["note"]}
            for row in rows
            if row["note"]
        ],
        "git": git_state(args.record),
    }
    args.record.parent.mkdir(parents=True, exist_ok=True)
    args.record.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    matcher, captions = record["matcher_candidates"], record["caption_candidates"]
    print(f"{len(rows)} rows from {len(by_pack)} of {len(manifest['packs'])} packs")
    print(
        f"matcher candidates: tp {matcher['overall']['tp']} · fp {matcher['overall']['fp']} ·"
        f" fn {matcher['overall']['fn']} · precision {matcher['overall']['precision_candidate']}"
        f" · recall {matcher['overall']['recall_candidate']}   [{REVIEW}]"
    )
    print(
        f"captions: {captions['judged']}/{captions['judgeable']} judged · {captions['tally']}"
        f" · faithful rate {captions['faithful_rate_candidate']}   [{REVIEW}]"
    )
    print(f"missed-brand candidates: {len(matcher['missed_brand_candidates'])} brand(s)")
    split = matcher["fn_split"]["counts"]
    print(
        f"fn split: {split['fn_matcher']} on the matcher (the name was in the string it read) ·"
        f" {split['fn_image_only']} image-only · a substring test would disagree on"
        f" {split['substring_would_disagree']}"
    )
    print(f"open extraction: {len(record['open_extraction_candidates']['names'])} name(s)")
    print(f"\nwrote {rel(args.record)} — candidates for the sitting, never gate numbers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
