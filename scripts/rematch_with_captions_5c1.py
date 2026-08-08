#!/usr/bin/env python3
"""Does @atb_market_official carry the taxonomy once its images can be read? ($0, offline.)

Step 4 of the caption pilot. The same matcher, the same lexicon revision and the same watchlist
the yield screen ran with — imported, not restated — read over the same window twice: once on the
posts' own text, and once on text plus the caption a vision model wrote for the silent ones.

The before is not taken on trust. It is re-derived here and checked against
`results/yield_screen_5c1.json`, the record the operator signed against: if this file cannot
reproduce the zero the screen reported, the after is a number about a different instrument.

The bars do not move. `results/yield_bars_5c1.preregistration.json` (sha 1aa89818…) is what bar A
means, and this script only reports which side of it the two readings land on.

    PYTHONPATH=src python3 scripts/rematch_with_captions_5c1.py
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

import yield_screen_5c1 as screen  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

from market_pulse import yield_screen as core  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

HANDLE = "@atb_market_official"
CAPTIONS = REPO_ROOT / "data" / "annotation" / "captions_5c1" / "atb_captions.jsonl"
CAPTION_RECORD = REPO_ROOT / "results" / "captions_5c1.json"
RECORD = REPO_ROOT / "results" / "caption_rematch_5c1.json"

MISS = "a post whose surrogate text the matcher still reads as carrying none of the taxonomy"
"""Stated because «промах» has two readings and only one of them is measurable here. This is the
first: the instrument fired on nothing. The second — it fired on the wrong thing — is a judgement
about a quoted line, so every hit carries its line and the operator reads them."""


def load_captions(path: Path) -> dict[int, dict]:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row["channel"] != HANDLE:
            raise SystemExit(f"{path.name} carries {row['channel']}, not {HANDLE}")
        if row["msg_id"] in rows:
            raise SystemExit(
                f"{path.name}: {row['msg_id']} is captioned twice, so neither is the one"
            )
        rows[row["msg_id"]] = row
    return rows


def read(rows: list[dict], captions: dict, compiled: dict, aliases: list) -> dict:
    """One reading of the window: which posts are relevant, on which terms, on whose evidence."""
    relevant, carried, by_post = [], [], {}
    for row in rows:
        text = row.get("text") or ""
        caption = (captions.get(row["msg_id"]) or {}).get("caption") or ""
        surrogate = "\n".join(part for part in (text, caption) if part.strip())
        terms = core.carriers(surrogate, compiled, aliases)
        by_post[row["msg_id"]] = {
            "msg_id": row["msg_id"],
            "date": row["date"],
            "has_own_text": bool(text.strip()),
            "captioned": bool(caption.strip()),
            "terms": sorted(terms),
            "evidence": core.evidence_line(surrogate, compiled, aliases),
        }
        if terms:
            relevant.append(row["msg_id"])
            carried.append(terms)
    counts: dict[str, int] = {}
    for terms in carried:
        for term in terms:
            counts[term] = counts.get(term, 0) + 1
    return {
        "relevant_posts": len(relevant),
        "relevant_msg_ids": sorted(relevant),
        # The strict reading: posts carried by a CATEGORY term, with every brand alias struck out.
        # «Своя Лінія» is ATB's own label and is printed on a leaflet's diapers as readily as on
        # its cheese, so a pass that needed the brands would be a pass about the leaflet's header.
        "relevant_on_category_alone": sum(
            1 for terms in carried if any(not term.startswith("brand:") for term in terms)
        ),
        "by_term": dict(sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))),
        "carried": carried,
        "posts": by_post,
    }


def refuse_to_overwrite(out: Path) -> None:
    if out == RECORD and RECORD.exists():
        raise SystemExit(
            f"{screen.rel(RECORD)} already exists — a second reading of a bought caption set is a"
            " different measurement: give it --out with another path."
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD)
    parser.add_argument("--captions", type=Path, default=CAPTIONS)
    args = parser.parse_args(argv)
    refuse_to_overwrite(args.out)

    prereg_sha, bars = screen.check_preregistration()
    lexicon = json.loads(screen.LEXICON.read_text(encoding="utf-8"))
    registry = load_registry(screen.REGISTRY)
    compiled = core.compile_categories(lexicon)
    aliases = core.compile_aliases(watchlist_aliases(registry.watchlist))

    posts = screen.load_jsonl(screen.POSTS / f"{HANDLE.lstrip('@')}.jsonl")
    window = screen.window_for(HANDLE, posts, screen.collect_window(), screen.collected_handles())
    rows = screen.in_window(posts, window)
    captions = load_captions(args.captions)

    before = read(rows, {}, compiled, aliases)
    after = read(rows, captions, compiled, aliases)

    signed = json.loads(screen.RECORD.read_text(encoding="utf-8"))
    screened = next(row for row in signed["sources"] if row["handle"] == HANDLE)
    controls = {
        "reproduces the signed screen": {
            "expected": f"{screened['relevant_posts']} relevant posts on text alone",
            "measured": before["relevant_posts"],
            "ok": before["relevant_posts"] == screened["relevant_posts"],
        },
        "same window as the signed screen": {
            "expected": screened["posts"]["in_window"],
            "measured": len(rows),
            "ok": len(rows) == screened["posts"]["in_window"],
        },
        "negative control :: a fitness post with no taxonomy": {
            "expected": "no category and no brand — the yield screen's own control line",
            "measured": sorted(core.carriers(screen.NEGATIVE_CONTROL, compiled, aliases)),
            "ok": not core.carriers(screen.NEGATIVE_CONTROL, compiled, aliases),
        },
    }
    reportable = all(control["ok"] for control in controls.values())

    captioned = [post for post in after["posts"].values() if post["captioned"]]
    misses = [post for post in captioned if not post["terms"]]
    bar = bars["bar_A_relevant_posts_28d"]
    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "5c1 — the ATB caption pilot",
        "contract": "docs/PROMPT-5c1-captions-pilot.md step 4",
        "channel": HANDLE,
        "window": window,
        "instrument": {
            "matcher": "market_pulse.yield_screen — the yield screen's own, imported",
            "lexicon": {
                "path": screen.rel(screen.LEXICON),
                "sha256": screen.sha256_of(screen.LEXICON),
                "status": lexicon["status"],
            },
            "registry": {
                "path": screen.rel(screen.REGISTRY),
                "sha256": screen.sha256_of(screen.REGISTRY),
            },
            "preregistration": {
                "path": screen.rel(screen.PREREGISTRATION),
                "sha256": prereg_sha,
                **bars,
            },
            "captions": {
                "path": screen.rel(args.captions),
                "sha256": hashlib.sha256(args.captions.read_bytes()).hexdigest(),
                "record": screen.rel(CAPTION_RECORD),
                "rows": len(captions),
            },
            "note": "the bars are not touched here; this reports which side of bar A each reading lands on",
        },
        "controls": controls,
        "verdicts_reportable": reportable,
        "posts_in_window": len(rows),
        "before": {
            "reading": "the posts' own text, exactly what the yield screen read",
            "relevant_posts": before["relevant_posts"],
            "bar_A": "PASS" if before["relevant_posts"] >= bar else "FAIL",
            "by_term": before["by_term"],
        },
        "after": {
            "reading": "the posts' own text plus the caption written for the silent ones",
            "relevant_posts": after["relevant_posts"],
            "bar_A": "PASS" if after["relevant_posts"] >= bar else "FAIL",
            "relevant_on_category_alone": after["relevant_on_category_alone"],
            "bar_A_on_category_alone": (
                "PASS" if after["relevant_on_category_alone"] >= bar else "FAIL"
            ),
            "by_term": after["by_term"],
            # The yield screen's own leverage question, asked of this reading: strike one term at
            # a time, does the pass survive? An empty list means it hangs on no single term.
            "bar_A_sole_carriers": core.sole_carriers(after["carried"], bar),
        },
        "captioned_posts": {
            "n": len(captioned),
            "relevant": len(captioned) - len(misses),
            "misses": {
                "definition": MISS,
                "n": len(misses),
                "msg_ids": sorted(post["msg_id"] for post in misses),
            },
        },
        "posts": [after["posts"][msg_id] for msg_id in sorted(after["posts"])],
        "git": git_state(args.out),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"{HANDLE} · {len(rows)} posts in {window['since'][:10]}…{window['until'][:10]}"
        f"\n  before: {before['relevant_posts']:>3} relevant  bar A {record['before']['bar_A']}"
        f"\n  after:  {after['relevant_posts']:>3} relevant  bar A {record['after']['bar_A']}"
        f"  (bar = {bar})"
    )
    for term, count in after["by_term"].items():
        print(f"    {term:<24}{count:>3}")
    print(
        f"\n  captioned {len(captioned)} · misses {len(misses)}: {record['captioned_posts']['misses']['msg_ids']}"
    )
    for name, control in controls.items():
        print(f"control {name:<48}{'OK' if control['ok'] else 'FAILED'}")
    print(f"\nwrote {screen.rel(args.out)}")
    if not reportable:
        print("STOP: a control came back wrong, so the before/after is not reportable.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
