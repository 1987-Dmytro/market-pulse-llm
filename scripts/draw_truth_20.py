#!/usr/bin/env python3
"""K13 — the product-truth gate: 20 rows under seed 42, for the operator to judge in his own words.

    PYTHONPATH=src python3.11 scripts/draw_truth_20.py          # renders the 20 rows, writes the record
    PYTHONPATH=src python3.11 scripts/draw_truth_20.py --json   # the record only

Phase spec §2, end-to-end: «20 rows under seed 42 (flyer/post · extracted position · comment ·
signal · quote) rendered for the operator, who says in his own words what is right and wrong». The
gate is HIS WORDS — this script computes no score and prints no bar. Its whole job is to put the
five columns side by side so a disagreement is visible without opening a database.

**Deterministic, and drawn from the screen's own export.** Population = the positions on the screen,
sorted by `row_id` and sampled with `random.Random(42)`, so two draws over one export are identical
and the rows are the ones the operator can actually see rendered. Reading the export rather than the
database is the same choice `make promo-screen` makes: the gate must run where the screen runs.

**A column with nothing in it says WHICH nothing.** The comment/signal/quote columns are filled from
the `feed` block — the reaction leg — and an empty one has THREE causes, not one: the thread is
still in the queue, or it was read and said nothing of the five kinds, or the leg was never bought
at all. The row names which, off `screen.threads` rather than off the feed's silence: an empty cell
reads as «this position drew no comment», which is a claim about the market, and «not read» is a
claim about us ([[empty_field_hides_several_states]]).

**No old price, here either.** The row shows what the screen shows — brand · product · volume ·
promo price · printed `−N%` — because a gate rendering a column the screen may not print would ask
the operator to bless a number he will never see again (SPEC 3.21 (4), 3.22 (1)).
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

EXPORT = REPO_ROOT / "results" / "promo_screen_data.json"
OUT = REPO_ROOT / "results" / "truth_20.json"
SEED = 42
ROWS = 20



def rel(path: Path) -> str:
    """The path as a reader of this repo names it, and the absolute one when it is outside."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)

def population(document: dict) -> list[dict]:
    """The screen's positions, sorted — the sample frame, stated before it is sampled."""
    return sorted(document["screen"]["positions"], key=lambda row: row["row_id"])


def reactions(document: dict) -> dict[tuple[str, int], list[dict]]:
    """The feed, indexed by the thread a position's post is the root of."""
    out: dict[tuple[str, int], list[dict]] = {}
    for row in document["screen"]["feed"]:
        out.setdefault((row["channel"], int(row["thread_root"])), []).append(row)
    return out


def was_read(document: dict) -> set[tuple[str, int]]:
    """The threads `results/promo_signals/` holds an answer for, as the export names them.

    The FEED cannot answer this: it carries only the threads that said something the codebook names,
    so a thread read in silence and a thread nobody has opened look identical in it. The export's
    `screen.threads.read_threads` is the third state's evidence
    ([[a_run_that_ends_early_adds_a_third_state_everywhere]]).
    """
    out = set()
    for key in document["screen"]["threads"]["read_threads"]:
        channel, _, root = key.rpartition("/")
        out.add((channel, int(root)))
    return out


def draw(document: dict, rows: int = ROWS, seed: int = SEED) -> list[dict]:
    """`rows` positions with their reactions. A short population is a SHORT DRAW, never a refusal:
    145 positions are on disk today and the gate is meant to run on whatever the screen holds."""
    frame = population(document)
    chosen = random.Random(seed).sample(frame, min(rows, len(frame)))
    feed = reactions(document)
    read = was_read(document)
    out = []
    for position in sorted(chosen, key=lambda row: row["row_id"]):
        item = position.get("item") or {}
        evidence = position.get("evidence") or {}
        thread = (evidence.get("channel"), int(evidence.get("msg_id", 0)))
        hits = feed.get(thread, [])
        out.append(
            {
                "row_id": position["row_id"],
                "thread_read": thread in read,
                "carrier": position.get("carrier"),
                "post": f"{evidence.get('channel')}/{evidence.get('msg_id')}",
                "brand": (position.get("brand") or {}).get("display"),
                "product": item.get("line") or item.get("category"),
                "volume": None
                if item.get("size_value") is None
                else f"{item['size_value']:g} {item.get('size_unit') or ''}".strip(),
                "promo_price": position.get("promo_price"),
                "printed_pct": position.get("printed_pct"),
                "reactions": [
                    {"signal": hit["type"], "quote": hit["quote"], "msg_id": hit["msg_id"]}
                    for hit in sorted(hits, key=lambda hit: (hit["type"], hit["msg_id"]))
                ],
            }
        )
    return out


def render(rows: list[dict], threads: dict) -> str:
    """The 20 rows as the operator reads them — one block per row, the five columns in §2's order."""
    out = [
        f"THE PRODUCT-TRUTH GATE — {len(rows)} rows, seed {SEED}, from results/promo_screen_data.json",
        f"Reactions: {threads['read']} of {threads['population']} price threads read ·"
        f" {threads['queue']} in the queue.",
        "Say in your own words what is right and wrong. Nothing here is scored.",
        "",
    ]
    for n, row in enumerate(rows, 1):
        price = "—" if row["promo_price"] is None else f"{row['promo_price']:g}"
        printed = "" if row["printed_pct"] is None else f"  (−{row['printed_pct']:g}%)"
        out.append(f"{n:2d}. {row['post']}  [{row['carrier']}]  {row['row_id']}")
        out.append(
            f"    position : {row['brand'] or '—'} · {row['product'] or '—'} ·"
            f" {row['volume'] or '—'} · {price} грн{printed}"
        )
        if not row["reactions"] and row["thread_read"]:
            out.append("    reaction : read, and nothing the codebook names was said in it —")
            out.append("               this IS «no one said anything of the five kinds»")
        elif not row["reactions"]:
            out.append("    reaction : not read — this thread is one of the"
                       f" {threads['queue']} still in the queue;")
            out.append("               this is not «no one commented»")
        for hit in row["reactions"]:
            out.append(f"    {hit['signal']:<9}: «{hit['quote']}»  (msg {hit['msg_id']})")
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", type=Path, default=EXPORT)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--rows", type=int, default=ROWS)
    parser.add_argument("--json", action="store_true", help="write the record, print nothing else")
    args = parser.parse_args(argv)

    if not args.export.exists():
        print(
            f"draw_truth_20 REFUSED: missing {args.export} — `make tick` writes it.", file=sys.stderr
        )
        return 1
    document = json.loads(args.export.read_text(encoding="utf-8"))
    rows = draw(document, args.rows)
    record = {
        "contract": "docs/PHASE-promo-pulse-1.md §2 — the product-truth gate. The gate is the"
        " operator's words; this record carries no score and no bar.",
        "seed": SEED,
        "population": len(population(document)),
        "rows_drawn": len(rows),
        "read_from": rel(args.export),
        "threads": document["screen"]["threads"],
        "rows": rows,
    }
    args.out.write_text(
        json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not args.json:
        print(render(rows, document["screen"]["threads"]))
    print(f"wrote {rel(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
