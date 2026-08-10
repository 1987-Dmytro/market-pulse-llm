#!/usr/bin/env python3
"""The text leg's sample frame: which corpus rows the position pre-filter passes ($0, offline).

SPEC amendment 3.17 (4) — "text extraction runs only on rows passed by a DETERMINISTIC pre-filter" —
and deliverable 3 of `docs/PROMPT-sku-a.md`. This counts that filter over the whole signed
composition and writes the frame the sku-b text leg draws from.

Two currencies, never blended, the same way the yield screen keeps them apart: a post's own text
(`carrier: post_text`) and a comment (`carrier: comment`). They are different price origins in SPEC
3.17 (4) and a pooled yield would hide which of the two the pilot is actually about.

What this does NOT read, and why it matters: **captions**. A caption is a model's sample of a
picture, so a size or a price inside one is the captioner's transcription and not the source's own
words — the leaflet leg exists to read those pages directly, per page. Counting caption text here
would put GM4's transcription into a frame labelled "text rows".

The lexicon is a SCREENING instrument, never the category law (`draft-not-law`, 5c3 owns the law).
This screen decides nothing: it counts, and the pack that follows draws.

    PYTHONPATH=src python3 scripts/sku_prefilter_census.py
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

from market_pulse import positions, yield_screen  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
LEXICON = REPO_ROOT / "data" / "category_lexicon_draft.json"
POSTS = REPO_ROOT / "data" / "raw" / "posts"
COMMENTS = REPO_ROOT / "data" / "raw" / "comments"
RECORD = REPO_ROOT / "results" / "sku_prefilter_census.json"

CARRIER_OF = {"post": "post_text", "comment": "comment"}
"""The store directory a row came from → its carrier (SPEC 3.17 (4))."""

COMMENTS_V2_NOTE = (
    "data/raw/comments_v2/ is NOT read: it holds the same two channels re-fetched with"
    " reply_to_msg_id (4.5g5), and its msg_id sets are identical to data/raw/comments/'s —"
    " @VARUS_channel 6,410 and @msuaaaa 4,928 in both, measured, zero rows either-only. The yield"
    " screen reads the same directory, so the two instruments see one corpus"
)
"""Written as a constant rather than as an attribute docstring: this sentence goes INTO the record,
and `SomeDict.__doc__` is `dict`'s docstring at runtime, not the line above it."""

POSITIVE_CONTROL = "Молоко Яготинське 2,5% 900 г — 39,90 грн"
"""A leaflet line of the exact shape the frame exists to catch: a watchlist brand, a category term,
a fat percentage, a size and a price. If the filter misses this, no yield it reports means anything."""

NEGATIVE_CONTROLS = {
    "a fitness post with a discount and no taxonomy": (
        "Розклад тренувань на тиждень: понеділок — ноги, середа — спина, п'ятниця — руки."
        " Реєстрація за посиланням, знижка 20% до кінця місяця."
    ),
    "a category with no number beside it": "Люблю сир і морозиво!",
    "a price with no category and no brand": "Кросівки, розмір 37, 1499 грн",
}
"""Three shapes that must NOT pass. The first is the yield screen's own negative control, reused on
purpose: it has the SHAPE of a hit — a food-adjacent feed, a discount, a percentage — and the
conjunction is what has to reject it. Without them, "this channel passed 0 rows" and "the filter
passes nothing" look the same."""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # a damaged line is not a row; results/collect_5c1.json counts them
    return rows


def row_id(handle: str, row: dict) -> str:
    return f"{handle}:{row['msg_id']}"


def screen_rows(handle: str, rows: list[dict], compiled: dict, aliases: list) -> dict:
    """One channel, one carrier: how many rows carry text, how many the filter passes, and how many
    the looser row-level reading would pass.

    `row_level` is reported rather than used. It is the same two primitives with the same-line
    requirement dropped, so the cost of the strict rule is a number a reader can weigh instead of a
    design argument nobody can check.
    """
    texted = [row for row in rows if (row.get("text") or "").strip()]
    passed, row_level, by_hit = [], 0, {}
    kinds = dict.fromkeys(("currency", "percent", "size"), 0)
    for row in texted:
        text = row.get("text") or ""
        anywhere = (
            bool(
                yield_screen.category_hits(text, compiled) or yield_screen.brand_hits(text, aliases)
            )
            and positions.size_price_pattern(text) is not None
        )
        row_level += anywhere
        found = positions.prefilter(row, compiled, aliases)
        if found is None:
            continue
        present = sorted({positions.pattern_kind(p) for p in positions.size_price_patterns(text)})
        for kind in present:
            kinds[kind] += 1
        passed.append(
            {"id": row_id(handle, row), "date": row.get("date"), **found, "pattern_kinds": present}
        )
        by_hit[found["hit"]] = by_hit.get(found["hit"], 0) + 1
    return {
        "rows": len(rows),
        "with_text": len(texted),
        "passed": len(passed),
        "passed_row_level": row_level,
        "share_of_texted": round(len(passed) / len(texted), 4) if texted else 0.0,
        # rows, not matches: a passing row is counted once per kind it carries anywhere in its text
        "passed_carrying": kinds,
        "by_hit": dict(sorted(by_hit.items(), key=lambda pair: (-pair[1], pair[0]))),
        "_passed": passed,
    }


def run_controls(compiled: dict, aliases: list) -> dict:
    """The filter's exam, taken before its yield is read."""
    out = {
        "positive :: a leaflet line with brand, category, size, fat and price": {
            "kind": "positive",
            "line": POSITIVE_CONTROL,
            "expected": "passes, on one line",
            "measured": positions.prefilter({"text": POSITIVE_CONTROL}, compiled, aliases),
        }
    }
    for name, text in NEGATIVE_CONTROLS.items():
        out[f"negative :: {name}"] = {
            "kind": "negative",
            "line": text,
            "expected": "does not pass — the rule is a conjunction",
            "measured": positions.prefilter({"text": text}, compiled, aliases),
        }
    for entry in out.values():
        entry["ok"] = bool(entry["measured"]) == (entry["kind"] == "positive")
    return out


def refuse_to_overwrite(out: Path) -> None:
    """The census IS the sample frame the pack is drawn from, and the pack's manifest pins its sha.

    Same refusal the yield screen, the census and the market screen carry (D68). A second pass over
    a moved corpus is a different frame, and a pack whose manifest cites this path would silently
    describe a draw from the other one.
    """
    if out == RECORD and RECORD.exists():
        raise SystemExit(
            f"{rel(RECORD)} already exists — it is the frame the sku-b text sample is drawn from,"
            " and results/sku_text_pack_manifest.json pins its sha256. A pass over a moved corpus"
            " is a different frame: give it --out with another path."
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD, help="where to write the record")
    parser.add_argument("--only", metavar="HANDLE", nargs="+", help="census only these handles")
    args = parser.parse_args(argv)
    refuse_to_overwrite(args.out)

    lexicon = json.loads(LEXICON.read_text(encoding="utf-8"))
    registry = load_registry(REGISTRY)
    compiled = yield_screen.compile_categories(lexicon)
    aliases = yield_screen.compile_aliases(watchlist_aliases(registry.watchlist))

    sources = {handle: source for source in registry.sources for handle in source.telegram_channels}
    handles = list(sources)
    if args.only:
        if missing := set(args.only) - set(handles):
            raise SystemExit(f"--only names handles the registry does not carry: {sorted(missing)}")
        handles = [handle for handle in handles if handle in args.only]

    rows, frame = [], []
    for handle in handles:
        stem = handle.lstrip("@")
        cells = {
            CARRIER_OF["post"]: screen_rows(
                handle, load_jsonl(POSTS / f"{stem}.jsonl"), compiled, aliases
            ),
            CARRIER_OF["comment"]: screen_rows(
                handle, load_jsonl(COMMENTS / f"{stem}.jsonl"), compiled, aliases
            ),
        }
        for carrier, cell in cells.items():
            for entry in cell.pop("_passed"):
                frame.append({**entry, "carrier": carrier, "channel": handle})
        source = sources[handle]
        rows.append(
            {
                "handle": handle,
                "audience": source.audience,
                "source_type": source.source_type,
                "watch": source.watch,
                "carriers": cells,
                "passed": sum(cell["passed"] for cell in cells.values()),
            }
        )

    frame.sort(key=lambda entry: (entry["channel"], entry["carrier"], entry["id"]))
    ids = [entry["id"] for entry in frame]
    if len(set(ids)) != len(ids):
        raise SystemExit("the frame carries a row twice — an id must select exactly one row")

    live = {handle.lstrip("@") for handle in sources}
    outside = {
        rel(path): len(load_jsonl(path))
        for folder in (POSTS, COMMENTS)
        for path in sorted(folder.glob("*.jsonl"))
        if path.stem not in live
    }

    controls = run_controls(compiled, aliases)
    by_carrier = {
        carrier: {
            "rows": sum(row["carriers"][carrier]["rows"] for row in rows),
            "with_text": sum(row["carriers"][carrier]["with_text"] for row in rows),
            "passed": sum(row["carriers"][carrier]["passed"] for row in rows),
            "passed_row_level": sum(row["carriers"][carrier]["passed_row_level"] for row in rows),
            "passed_carrying": {
                kind: sum(row["carriers"][carrier]["passed_carrying"][kind] for row in rows)
                for kind in ("currency", "percent", "size")
            },
        }
        for carrier in CARRIER_OF.values()
    }
    for cell in by_carrier.values():
        cell["share_of_texted"] = (
            round(cell["passed"] / cell["with_text"], 4) if cell["with_text"] else 0.0
        )

    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "sku-a — the position layer's text-leg sample frame",
        "contract": "docs/PROMPT-sku-a.md deliverable 3; docs/SPEC.md amendment 3.17 (4)",
        "asks": "which corpus rows a deterministic pre-filter passes to the text extraction leg",
        "report_only": (
            "nothing is extracted, nothing is spent and nothing enters a gate. This is the frame"
            " the seed-42 text pack is drawn from and the denominator the text bar of 3.17 (6)"
            " will be read against"
        ),
        "rule": {
            "conjunction": (
                "a watchlist brand or a tracked category term AND a size/price pattern, both on the"
                " SAME line"
            ),
            "brands": (
                "market_pulse.brands.find_watchlist_brands' rule — the display name as written,"
                " casefolded, bounded by non-word characters, nested aliases resolved to the longer"
                " span. The matcher G1e is scored against"
            ),
            "categories": (
                "the lexicon's own matcher and endings as shipped, tracked half only: dairy and"
                " ice-cream are the taxonomy, the draft families beside them are other people's"
            ),
            "size_price": (
                f"число + one of {list(positions.SIZE_PRICE_UNITS)}, the unit bounded by a non-word"
                " character. The six the contract names; «500 грам» and «5 гривень» are outside it"
            ),
            "same_line": (
                "both halves on one line. `passed_row_level` beside every count is the same two"
                " primitives with that requirement dropped — the price of the strict reading,"
                " reported as a number rather than argued"
            ),
            "pattern_kinds": (
                "`passed_carrying` counts passing ROWS by which units they carry anywhere in their"
                " text: currency (грн), percent (%) or size (г/кг/л/мл). The filter cannot tell an"
                " OFFER from a recipe — «Кефір — 400 мл» is a category term beside a size and it is"
                " an ingredient list — so a currency marker is the cheapest deterministic reading of"
                " «is this line priced at all». `percent` is its own bucket because «82,5%» is a fat"
                " content and «-38%» is a discount, and nothing here can tell them apart"
            ),
            "captions_excluded": (
                "a caption is a model's SAMPLE of a picture, so a size or a price inside one is the"
                " captioner's transcription and not the source's words. The leaflet leg reads those"
                " pages directly, per page (3.17 (4))"
            ),
            "carriers_never_blended": (
                "posts and comments are separate rows in every cell: SPEC 3.17 (4) gives them"
                " different price origins and consumer quotes never enter promo aggregates"
            ),
        },
        "sources_read": {
            "registry": {
                "path": rel(REGISTRY),
                "sha256": sha256_of(REGISTRY),
                "channels": len(sources),
            },
            "lexicon": {
                "path": rel(LEXICON),
                "sha256": sha256_of(LEXICON),
                "status": lexicon["status"],
                "known_collision": lexicon["known_collision"],
            },
            "watchlist_brands": len(registry.watchlist),
            "stores": [rel(POSTS), rel(COMMENTS)],
            "comments_v2_note": COMMENTS_V2_NOTE,
            "outside_the_registry": outside,
        },
        "controls": controls,
        "frame_reportable": all(control["ok"] for control in controls.values()),
        "frame": {
            "rows": len(frame),
            "ids_sha256": hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest(),
            "ids_sha256_note": (
                "sha256 of the passing ids, newline-joined in this record's order. The pack builder"
                " re-derives the frame from the stores and refuses if this does not match — a hash"
                " of ids cannot re-score them, but it can prove the draw came from this frame"
            ),
            "by_carrier": by_carrier,
        },
        "summary": {
            "channels": len(rows),
            "passed": len(frame),
            "channels_with_a_pass": sum(1 for row in rows if row["passed"]),
            "top_channels": {
                row["handle"]: row["passed"]
                for row in sorted(rows, key=lambda row: -row["passed"])[:10]
                if row["passed"]
            },
        },
        "channels": sorted(rows, key=lambda row: (-row["passed"], row["handle"])),
        "rows": frame,
        "git": git_state(args.out),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    header = f"{'channel':<30}{'posts':>7}{'pass':>6}{'cmts':>7}{'pass':>6}   top hit"
    print(f"\n{header}\n{'-' * len(header)}")
    for row in record["channels"][:20]:
        post, comment = row["carriers"]["post_text"], row["carriers"]["comment"]
        hits = {**post["by_hit"], **comment["by_hit"]}
        top = next(iter(sorted(hits.items(), key=lambda pair: -pair[1])), ("—", 0))
        print(
            f"{row['handle'][:29]:<30}{post['with_text']:>7}{post['passed']:>6}"
            f"{comment['with_text']:>7}{comment['passed']:>6}   {top[0]} ×{top[1]}"
        )
    for carrier, cell in by_carrier.items():
        print(
            f"\n{carrier:<12} {cell['with_text']} texted rows · {cell['passed']} passed"
            f" ({cell['share_of_texted']:.2%}) · row-level reading {cell['passed_row_level']}"
            f"\n{'':<12} of the passed: {cell['passed_carrying']}"
        )
    for name, control in controls.items():
        print(f"control {name[:60]:<62}{'OK' if control['ok'] else 'FAILED'}")
    print(f"\nframe {len(frame)} rows · ids {record['frame']['ids_sha256'][:16]}…")
    print(f"wrote {rel(args.out)}")
    if not record["frame_reportable"]:
        print("STOP: a control came back wrong, so the frame is not reportable.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
