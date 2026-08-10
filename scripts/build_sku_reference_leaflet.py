#!/usr/bin/env python3
"""The leaflet leg's ground truth: 19 ATB posts, the brands an Opus reviewer saw on their pages.

Deliverable 4(a) of `docs/PROMPT-sku-a.md`. Built from the Opus-audit **S4** rows — the stratum
whose question was "a committed caption row standing in for a silent post; where a model wrote it
over images, its faithfulness is judged too" — narrowed to `@atb_market_official`, which is the 19
posts vis-b captioned and the population SPEC 3.17 (6) names for the sku-b leaflet leg.

**This file is SCORING input and never model input.** The blind rebuild of the audit packs took the
matcher's answer out of the packs on purpose (Dv87) so a reviewer could not be anchored by it; the
same logic applies in reverse here — the pilot's request carries one image and nothing else, and this
record is what its answer is compared against afterwards.

Three facts about the gold this record has to state out loud, because the bar of 3.17 (6) is
computed over it:

1. **The gold is per POST, not per page.** One reviewer judged the whole set of pages sent for a post
   and named the brands visible across them. Nothing here attributes a brand to a page.
2. **The pages are a SLICE.** The caption run sent at most 6 images per post — 108 of the 159
   available — so for 15 of the 19 posts the reviewer saw the first six pages of a longer leaflet.
   `pages_not_sent` names the rest, and no brand on them is in the gold.
3. **Four of the 19 posts have an EMPTY gold brand set** (summer non-food and similar). Recall over
   an empty denominator is undefined, so those four cannot enter a recall average; they are a
   precision probe instead, where any brand extracted is a false positive.

    PYTHONPATH=src python3 scripts/build_sku_reference_leaflet.py
"""

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_audit_pack import git_state  # noqa: E402

from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
AUDIT = REPO_ROOT / "results" / "opus_audit_5c1.json"
MANIFEST = REPO_ROOT / "results" / "opus_audit_manifest.json"
RETURNS = REPO_ROOT / "results" / "opus_audit_returns"
CAPTIONS = REPO_ROOT / "data" / "annotation" / "captions_5c1" / "gm4_atb19.jsonl"
CAPTION_RECORD = REPO_ROOT / "results" / "captions_gm4_atb19.json"
POST_MEDIA = REPO_ROOT / "results" / "post_media_5c1.json"
RECORD = REPO_ROOT / "results" / "sku_reference_leaflet.json"

CHANNEL = "@atb_market_official"
STRATUM = "S4"
EXPECTED_POSTS = 19
"""vis-b captioned 19 of 19 silent ATB posts and SPEC 3.17 (6) names them as the pilot's leaflet
population. A different count means the audit or the caption file moved, and the reference is not
the population the bar was pre-registered over — so it is checked rather than trusted."""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def returns_rows() -> dict[str, dict]:
    """Every judged row, keyed by item. One reviewer, one row per item (the audit checked that)."""
    rows: dict[str, dict] = {}
    for path in sorted(RETURNS.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row["item"] in rows:
                raise SystemExit(f"{row['item']} is judged twice — the pack draw is not one row")
            rows[row["item"]] = row
    return rows


def caption_rows() -> dict[str, dict]:
    rows = {}
    for line in CAPTIONS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[f"{row['channel']}:{row['msg_id']}"] = row
    return rows


def gold_key(name: str, aliases: dict[str, str]) -> str:
    """A brand the reviewer named → the key recall is computed on.

    The watchlist id when the name resolves to one, and `raw:` + the casefolded name when it does
    not. Two halves of one field: `watchlist_hits` comes back as ids already and
    `other_dairy_brands` as the name as printed, and a comparison that mixed the two spaces would
    score «Каштан» against `kashtan` and call it a miss.
    """
    folded = " ".join(str(name).split()).casefold()
    return aliases.get(folded) or f"raw:{folded}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    aliases = watchlist_aliases(load_registry(REGISTRY).watchlist)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    media = json.loads(POST_MEDIA.read_text(encoding="utf-8"))["entries"]
    caption_record = json.loads(CAPTION_RECORD.read_text(encoding="utf-8"))
    truncated = set(caption_record["images"]["posts_truncated"])
    judged = returns_rows()
    captions = caption_rows()

    items = sorted(
        (
            item
            for item in manifest["items"]
            if STRATUM in item["strata"] and item["channel"] == CHANNEL
        ),
        key=lambda item: item["msg_id"],
    )
    if len(items) != EXPECTED_POSTS:
        raise SystemExit(
            f"{len(items)} {CHANNEL} rows in stratum {STRATUM}, expected {EXPECTED_POSTS} — the"
            " audit population moved, and this reference would not be the one the bar was"
            " pre-registered over"
        )

    rows, verified, missing, differs = [], 0, [], []
    for item in items:
        key = item["item"]
        answer, caption = judged[key], captions[key]
        sent = caption["images"]
        available = media[key]["images"]
        if item["images"]["named"] != len(sent) or item["images"]["sha_matched"] != len(sent):
            raise SystemExit(
                f"{key}: the manifest counts {item['images']} images and the caption row carries"
                f" {len(sent)} — the pages the reviewer saw are not the pages on record"
            )
        if not set(answer["brands_visible_missed"]) <= set(answer["watchlist_hits"]):
            raise SystemExit(
                f"{key}: brands_visible_missed is not a subset of watchlist_hits, so the two fields"
                " no longer describe one reading"
            )
        pages = []
        for index, image in enumerate(sent, start=1):
            path = REPO_ROOT / image["file"]
            if not path.exists():
                missing.append(image["file"])
            elif sha256_of(path) != image["sha256"]:
                differs.append(image["file"])
            else:
                verified += 1
            pages.append({"page": index, "file": image["file"], "sha256": image["sha256"]})
        gold = sorted(
            {gold_key(name, aliases) for name in answer["watchlist_hits"]}
            | {gold_key(name, aliases) for name in answer["other_dairy_brands"]}
        )
        rows.append(
            {
                "item": key,
                "channel": item["channel"],
                "msg_id": item["msg_id"],
                "date": item["date"],
                "audit_pack": item["pack"],
                "brands_visible": {
                    "gold_keys": gold,
                    "watchlist": sorted(answer["watchlist_hits"]),
                    "other_dairy_brands": answer["other_dairy_brands"],
                    "missed_by_the_matcher": sorted(answer["brands_visible_missed"]),
                    "n": len(gold),
                },
                "pages_sent": pages,
                "pages_available": len(available),
                "pages_not_sent": [image["file"] for image in available[len(sent) :]],
                "caption": {
                    "text": caption["caption"],
                    "source": caption["caption_source"],
                    "verdict": answer["caption_verdict"],
                    "truncated": key in truncated,
                },
                "reviewer_note": answer["note"],
            }
        )

    if missing or differs:
        raise SystemExit(
            f"{len(missing)} page(s) missing and {len(differs)} with a moved sha256 — the pilot"
            f" cannot be scored against pages that are not the ones judged: {(missing + differs)[:3]}"
        )

    scoreable = [row for row in rows if row["brands_visible"]["n"]]
    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "sku-a — the leaflet leg's ground truth",
        "contract": "docs/PROMPT-sku-a.md deliverable 4(a); docs/SPEC.md amendment 3.17 (6)",
        "class": (
            "SCORING input, never model input. The pilot's request carries one image and nothing"
            " else; this record is what its answer is compared against afterwards. Same discipline"
            " as the blind pack rebuild (Dv87), which took the matcher's answer out of the packs so"
            " a reviewer could not be anchored by it"
        ),
        "provenance": (
            "the brands are one Opus reviewer's reading under a committed protocol, in the REVIEW"
            " class of SPEC 3.16 (1): candidates for a bar, never a gate number of their own"
        ),
        "population": {
            "channel": CHANNEL,
            "stratum": STRATUM,
            "posts": len(rows),
            "pages_sent": sum(len(row["pages_sent"]) for row in rows),
            "pages_available": sum(row["pages_available"] for row in rows),
            "posts_whose_pages_were_truncated": sorted(
                row["item"] for row in rows if row["caption"]["truncated"]
            ),
        },
        "gold": {
            "definition": (
                "brands_visible = watchlist_hits + other_dairy_brands, deduplicated on the gold key:"
                " the watchlist id when the name resolves to one, `raw:` + the casefolded name when"
                " it does not. The two fields arrive in different spaces — ids and names as printed"
                " — and comparing them unnormalised would score «Каштан» against a brand_id"
            ),
            "pairs": sum(row["brands_visible"]["n"] for row in rows),
            "from_the_watchlist": sum(len(row["brands_visible"]["watchlist"]) for row in rows),
            "outside_the_watchlist": sum(
                len(row["brands_visible"]["other_dairy_brands"]) for row in rows
            ),
            "per_post_not_per_page": (
                "one reviewer judged the whole set of pages sent for a post and named what was"
                " visible across them. NOTHING here attributes a brand to a page, so a per-page"
                " recall cannot be computed from this file — see results/sku_pilot_prereg.json,"
                " which states the reading the bar is scored under and flags it for ratification"
            ),
            "pages_are_a_slice": (
                "the caption run sent at most 6 images per post, 108 of 159 available, so for 15 of"
                " the 19 posts the reviewer saw the first six pages of a longer leaflet."
                " `pages_not_sent` names the rest and no brand on them is in this gold"
            ),
            "posts_with_a_non_empty_gold_set": len(scoreable),
            "posts_with_an_empty_gold_set": [
                row["item"] for row in rows if not row["brands_visible"]["n"]
            ],
            "empty_set_note": (
                "recall over an empty denominator is undefined, so these posts cannot enter a recall"
                " average. They are a precision probe: any brand extracted on their pages is a false"
                " positive, and the reviewer's note says what is on them"
            ),
        },
        "sources": {
            rel(path): sha256_of(path)
            for path in (AUDIT, MANIFEST, CAPTIONS, CAPTION_RECORD, POST_MEDIA, REGISTRY)
        },
        "returns_sha256": hashlib.sha256(
            b"".join(path.read_bytes() for path in sorted(RETURNS.glob("*.jsonl")))
        ).hexdigest(),
        "audit_instrument": audit["instrument"],
        "images_verified": {
            "checked": sum(len(row["pages_sent"]) for row in rows),
            "sha_matched": verified,
            "missing": missing,
            "sha_differs": differs,
        },
        "caption_verdicts": {
            verdict: sum(1 for row in rows if row["caption"]["verdict"] == verdict)
            for verdict in ("faithful", "partial", "wrong", "n/a")
        },
        "posts": rows,
        "git": git_state(args.out),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{len(rows)} posts · {record['gold']['pairs']} gold (post, brand) pairs")
    print(
        f"  {record['gold']['from_the_watchlist']} watchlist +"
        f" {record['gold']['outside_the_watchlist']} outside it"
    )
    print(
        f"  {record['population']['pages_sent']} pages sent of"
        f" {record['population']['pages_available']} available ·"
        f" {len(record['population']['posts_whose_pages_were_truncated'])} replies truncated"
    )
    print(
        f"  {len(scoreable)} posts carry a non-empty gold set, {len(rows) - len(scoreable)} do not"
    )
    print(f"  every page verified on disk: {verified}/{record['images_verified']['checked']}")
    print(f"  caption verdicts {record['caption_verdicts']}")
    print(f"wrote {rel(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
