#!/usr/bin/env python3
"""$0 ranking for S4's unbought remainder — measured on pages 5c2 has already paid for.

Ruling 02.09 (c): «a $0 RANKING instrument for the remainder, measured before it is trusted:
caption-lexicon rank for photo posts (dairy/ice-cream terms of `lexicon.yaml`, read-only) and, if
`tesseract` + `ukr` install in one `brew` command, OCR rank for leaflet pages — page-level recall
on 5c2's 159 ATB pages against `results/run_5c2_positions.json` (pages with >= 1 position); the
table shows $ whole vs $ top-ranked at recall >= 0.90.»

Two rankers, one scorer — `yield_screen.compile_categories` under `config/lexicon.yaml`, the law
the pre-filter already reads, so a term that fires here is a term the product tracks. The OCR
ranker reads the page image through `tesseract -l ukr`; the caption ranker reads the media post's
own caption out of the live store. Neither buys anything and neither writes to `data/derived`.

**The ground truth is the model's own answer, not a human's.** A page counts as positive when 5c2's
paid pass wrote at least one position row for THAT IMAGE (`data/derived/position_rows`, joined on
`image_path`). So the recall below is «how much of what the instrument WOULD have found does the
ranker keep» — which is the question the money asks — and not «how much is on the page».

    PYTHONPATH=src python3.11 scripts/rank_remainder_c2.py --measure   # $0: OCR, rank, recall
    PYTHONPATH=src python3.11 scripts/rank_remainder_c2.py --table     # $0: $ whole vs $ ranked
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_promo_c2 as driver  # noqa: E402

from market_pulse import yield_screen  # noqa: E402
from market_pulse.lexicon import load_lexicon  # noqa: E402
from market_pulse.raw_store import RawStore, live_store  # noqa: E402

RUN_5C2 = REPO_ROOT / "results" / "run_5c2_positions.json"
DERIVED = REPO_ROOT / "data" / "derived"
CHANNEL = "@atb_market_official"
EVIDENCE = REPO_ROOT / "results" / "rank_remainder_c2.jsonl"
RECORD = REPO_ROOT / "results" / "rank_remainder_c2.json"
RECALL_BAR = 0.90
"""Ruling 02.09 (c): «$ whole vs $ top-ranked at recall >= 0.90». The bar is the team lead's."""


def ocr(path: Path) -> str:
    """One page through tesseract with the Ukrainian model. A failure is empty text, not a crash —
    an unreadable page must rank LAST, and a raise here would lose the whole measurement."""
    done = subprocess.run(
        ["tesseract", str(path), "stdout", "-l", "ukr"],
        check=False,
        capture_output=True,
        text=True,
    )
    return done.stdout if done.returncode == 0 else ""


def scorer():
    compiled = yield_screen.compile_categories(load_lexicon())
    return lambda text: yield_screen.category_terms(text or "", compiled)


def truth() -> tuple[list[dict], set[str]]:
    """5c2's pages and the ones its paid pass found a position on — read off the derived store.

    Joined on `image_path`, which is the only field that names ONE page. `parent_msg_id` names the
    album's key post, so every page of an 18-page album shares it: joining on it collapses 159
    pages onto 50 posts and reports 11 positives where there are 30 ([[id_spaces_that_look_comparable]]).

    Filtered by `served_by` and not merely by channel: S4 writes ITS @atb_market_official pages into
    the same store, and a population that grew after the truth was fixed would silently re-scope the
    recall below. The endpoint is 5c2's own, read from its record.
    """
    endpoint = json.loads(RUN_5C2.read_text(encoding="utf-8"))["endpoint"]
    store = RawStore(DERIVED)
    pages = [row for row in store.rows("leaflet_page", CHANNEL) if row["served_by"] == endpoint]
    positive = {
        row["image_path"]
        for row in store.rows("position_row", CHANNEL)
        if row["served_by"] == endpoint
    }
    return pages, positive & {row["image_path"] for row in pages}


def captions() -> dict[int, str]:
    """`{post msg_id: caption}` for this channel, out of the live store (v1 ∪ r2)."""
    return {row["msg_id"]: row.get("text") or "" for row in live_store().rows("post", CHANNEL)}


def recall_curve(ranked: list[dict], positive: set[int]) -> dict:
    """Walk the ranking and answer ONE question: how many pages must be bought for `RECALL_BAR`.

    Ties are kept together — a cut inside a tie would report a recall the ranker cannot deliver,
    because nothing in the score distinguishes the page kept from the page dropped.
    """
    found, out = 0, []
    for index, row in enumerate(ranked, 1):
        found += row["msg_id"] in positive
        out.append({"k": index, "found": found, "recall": round(found / max(len(positive), 1), 4)})
    keep = next((row for row in out if row["recall"] >= RECALL_BAR), None)
    if keep:
        cut = ranked[keep["k"] - 1]["score"]
        keep = dict(keep, k=sum(1 for row in ranked if row["score"] >= cut), cut_score=cut)
        keep["found"] = sum(1 for row in ranked[: keep["k"]] if row["msg_id"] in positive)
        keep["recall"] = round(keep["found"] / max(len(positive), 1), 4)
    base = len(positive) / max(len(ranked), 1)
    by_score = []
    for cut in sorted({row["score"] for row in ranked}, reverse=True):
        kept = [row for row in ranked if row["score"] >= cut]
        found = sum(1 for row in kept if row["msg_id"] in positive)
        by_score.append(
            {
                "score_at_least": cut,
                "pages_kept": len(kept),
                "keep_fraction": round(len(kept) / len(ranked), 4),
                "found": found,
                "recall": round(found / max(len(positive), 1), 4),
                "precision": round(found / len(kept), 4),
                "lift": round((found / len(kept)) / base, 2) if base else None,
            }
        )
    return {
        "pages": len(ranked),
        "positive": len(positive),
        "base_rate": round(base, 4),
        "at_the_bar": keep,
        "keep_fraction": round(keep["k"] / len(ranked), 4) if keep else None,
        # The cuts the ranker can actually make: a score is the only thing that separates two pages,
        # so a k between two scores is a cut nothing implements ([[a_saturated_proxy_cannot_discriminate]]).
        "by_score": by_score,
        "curve": [row for row in out if row["k"] % 10 == 0 or row["k"] == len(out)],
    }


def measure() -> dict:
    """Both rankers on 5c2's own pages, and what each would have kept at the bar."""
    term = scorer()
    caption = captions()
    pages, positive = truth()
    rows = []
    for index, page in enumerate(sorted(pages, key=lambda one: one["msg_id"]), 1):
        path = REPO_ROOT / page["image_path"]
        if not path.exists():
            raise SystemExit(
                f"{page['image_path']} is not on disk — the page 5c2 was served cannot be re-read,"
                " and a ranker measured on a different image measures nothing"
            )
        text = ocr(path)
        ocr_terms = term(text)
        caption_terms = term(caption.get(page["parent_msg_id"], ""))
        rows.append(
            {
                "msg_id": page["msg_id"],
                "parent_msg_id": page["parent_msg_id"],
                "file": page["image_path"],
                "ocr_chars": len(text.strip()),
                "ocr_terms": sorted(set(ocr_terms)),
                "ocr_score": len(set(ocr_terms)),
                "caption_terms": sorted(set(caption_terms)),
                "caption_score": len(set(caption_terms)),
                "positive": page["image_path"] in positive,
            }
        )
        print(f"  {index:>3}/{len(pages)} {page['msg_id']} ocr {len(set(ocr_terms))}", flush=True)
    EVIDENCE.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    ranked = {
        name: sorted(
            ({"msg_id": row["msg_id"], "score": row[f"{name}_score"]} for row in rows),
            key=lambda one: (-one["score"], one["msg_id"]),
        )
        for name in ("ocr", "caption")
    }
    positive_ids = {row["msg_id"] for row in rows if row["positive"]}
    record = {
        "question": "does a $0 ranking keep what the paid pass would have found — and how much of"
        " the remainder can then be left unbought? (ruling 02.09 (c), «before the next STOP»)",
        "authority": "docs/reviews/2026-08-30-plan-promo-pulse-1.md «Ruling 02.09 (c)»",
        "instrument": {
            "scorer": "market_pulse.yield_screen.compile_categories over config/lexicon.yaml"
            " (status: law) — the count of DISTINCT tracked stems the text names",
            "ocr": "tesseract -l ukr, one page image at a time, stdout",
            "tesseract": subprocess.run(
                ["tesseract", "--version"], check=False, capture_output=True, text=True
            ).stdout.splitlines()[0],
            "caption": "the media post's own caption out of the live store (v1 ∪ r2)",
        },
        "population": {
            "pages": len(pages),
            "source": "data/derived/leaflet_pages/atb_market_official.jsonl, the rows whose"
            f" served_by is 5c2's endpoint ({driver.rel(RUN_5C2)} :: selection.leaflet_page.rows)",
            "truth": "data/derived/position_rows/atb_market_official.jsonl :: image_path — a page"
            " is positive when 5c2's PAID pass wrote at least one position for THAT image",
            "positive": len(positive),
        },
        "recall_bar": RECALL_BAR,
        "ocr": recall_curve(ranked["ocr"], positive_ids),
        "caption": recall_curve(ranked["caption"], positive_ids),
        "evidence": driver.rel(EVIDENCE),
    }
    RECORD.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return record


def table() -> dict:
    """The remainder priced twice: whole, and at the keep fraction the measurement earned.

    The rate is the channel's OWN measured one where the run measured it, and the run's worst
    measured rate where it did not — an unmeasured channel is priced at the dearest thing seen,
    never at the cheapest ([[a_reproducible_probe_can_be_unrepresentative]]).
    """
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    run = json.loads(driver.RECORD.read_text(encoding="utf-8"))["runs"][-1]
    prereg = json.loads(driver.PREREG.read_text(encoding="utf-8"))
    rate = float(prereg["rung_0"]["rates"]["rate_usd_per_second"])
    measured = run.get("measured") or {}
    worst = max(measured.values(), default=float(run["go_no_go"]["page_marginal_seconds"]))
    keep = record["ocr"]["keep_fraction"]
    # The cut the ranker can actually make below «keep everything» — the ruling's bar may not be
    # reachable, and a table that only priced the bar would hide the option that exists.
    usable = max(
        (row for row in record["ocr"]["by_score"] if row["keep_fraction"] < 1.0),
        key=lambda row: row["recall"],
        default=None,
    )
    rows = []
    for handle, pages in sorted(run["unbought"]["pages"].items(), key=lambda one: -one[1]):
        seconds = measured.get(handle, worst)
        whole = pages * seconds * rate
        rows.append(
            {
                "channel": handle,
                "pages_left": pages,
                "seconds_per_page": round(seconds, 4),
                "measured": handle in measured,
                "usd_whole": round(whole, 4),
                "pages_top_ranked": math.ceil(pages * keep) if keep else None,
                "usd_top_ranked": round(whole * keep, 4) if keep else None,
                "pages_usable_cut": math.ceil(pages * usable["keep_fraction"]) if usable else None,
                "usd_usable_cut": round(whole * usable["keep_fraction"], 4) if usable else None,
            }
        )
    out = {
        "rule": "ruling 02.09 (c): «the table shows $ whole vs $ top-ranked at recall >= 0.90»",
        "keep_fraction": keep,
        "keep_fraction_from": f"{driver.rel(RECORD)} :: ocr.keep_fraction (measured on"
        f" {record['ocr']['pages']} ATB leaflet pages; every other channel is an EXTRAPOLATION"
        " from that one carrier, and the caption ranker is the honest instrument for photo posts)",
        "usable_cut": usable,
        "usable_cut_note": "the deepest cut the ranker can make below «keep everything»; it is"
        " BELOW the ruling's recall bar and is priced here because the bar itself buys nothing",
        "worst_measured_seconds_per_page": round(worst, 4),
        "rows": rows,
        "totals": {
            "pages_left": sum(row["pages_left"] for row in rows),
            "usd_whole": round(sum(row["usd_whole"] for row in rows), 4),
            "usd_top_ranked": round(sum(row["usd_top_ranked"] or 0.0 for row in rows), 4),
            "usd_usable_cut": round(sum(row["usd_usable_cut"] or 0.0 for row in rows), 4),
        },
    }
    record["remainder_table"] = out
    RECORD.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return out


def render(record: dict) -> str:
    lines = []
    for name in ("ocr", "caption"):
        one = record[name]
        bar = one["at_the_bar"]
        lines.append(
            f"{name:<8} {one['pages']} pages, {one['positive']} positive"
            f" ({one['base_rate']:.1%}) → "
            + (
                f"keep {bar['k']} ({one['keep_fraction']:.1%}) for recall {bar['recall']:.2f}"
                f" at score >= {bar['cut_score']}"
                if bar
                else f"NEVER reaches recall {record['recall_bar']}"
            )
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measure", action="store_true", help="$0: OCR, rank, the recall curve")
    parser.add_argument("--table", action="store_true", help="$0: the remainder priced twice")
    args = parser.parse_args(argv)
    if args.measure:
        record = measure()
        print(render(record))
        print(f"wrote {driver.rel(RECORD)} and {driver.rel(EVIDENCE)}")
    if args.table:
        out = table()
        print(f"  {'channel':<24}{'left':>5}{'s/page':>10}{'$ whole':>9}{'$ bar':>9}{'$ cut':>9}")
        for row in out["rows"]:
            print(
                f"  {row['channel']:<24}{row['pages_left']:>5}"
                f"{row['seconds_per_page']:>9.3f}{'' if row['measured'] else '*'}"
                f"{row['usd_whole']:>9.4f}{row['usd_top_ranked']:>9.4f}"
                f"{row['usd_usable_cut']:>9.4f}"
            )
        print(
            f"  {'TOTAL':<24}{out['totals']['pages_left']:>5}{'':>10}"
            f"{out['totals']['usd_whole']:>9.4f}{out['totals']['usd_top_ranked']:>9.4f}"
            f"{out['totals']['usd_usable_cut']:>9.4f}"
        )
        print("  * priced at the run's WORST measured rate — this channel was never measured")
        cut = out["usable_cut"]
        print(
            f"  $ bar = recall >= {RECALL_BAR} (keeps {out['keep_fraction']:.0%} — the bar buys"
            f" nothing); $ cut = score >= {cut['score_at_least']}: {cut['keep_fraction']:.0%} of the"
            f" pages for recall {cut['recall']:.2f} at lift {cut['lift']}"
            if cut
            else "  the ranker makes no cut below «keep everything»"
        )
    if not (args.measure or args.table):
        parser.error("choose --measure or --table")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
