#!/usr/bin/env python3
"""`make promo-screen` — C5's one promo screen, rendered from result files and nothing else.

    make tick && make promo-screen        # the end-to-end of phase spec §2, on a clean clone
    PYTHONPATH=src python3.11 scripts/build_promo_screen.py --export /tmp/x.json --out /tmp/x.html

**One source for the market, named.** `results/promo_screen_data.json`, which `make tick` writes.
Not the database, not the raw store, not the registry: a clean clone has none of those (`data/` is
gitignored) and the phase's end-to-end check is exactly that the screen still renders there. Every
figure about the market comes from that file; this script computes no aggregate of its own.

**Four sources for the instrument's own grade, named, the SHIPPED one first.** The S2 block
(ruling 06.09 (cc) addendum: «ship as measured» — both numbers with their files on the screen)
prints the holdout readings of the comment reader straight from the graders' records,
:data:`S2_SOURCES`. The first row is the product's own pipeline end to end — the four hooks of §2
S4 and then P1, measured by the product's own functions (ruling 08.09 (dd)); the three below it
graded the model's RAW answer, before the product's filter, and are labelled «reading» because that
is what they are: the bar's record, never rewritten. Each value sits beside its bar and the file's
own `held` flag, and the tie count comes from the reading the ruling pins it to. Committed result
files, so a clean clone has them; no number here is typed.

**A missing source is a NAMED, non-zero exit.** All three kinds: the export itself, any of
:data:`REQUIRED` inside it, and any of the S2 files or the block read from it. A screen that
renders a blank panel over a missing input is worse than one that refuses — the blank reads as «no
promo this week», which is a claim about the market ([[the_empty_row_is_the_answer]]). That is
K12's negative control and it is what `--check` runs.

**What the row may say, and what it may not.** brand · product · volume · promo price · printed
`−N%`. The extracted old price is NOT on this page (SPEC 3.21 (4), 3.18 (1)) and neither is the
arithmetic depth beside a row's own promo price (3.22 (1)), because `promo ÷ (1 − depth)` gives the
old price back. Depth appears once, in its own panel, aggregated per chain and brand — which is the
form 3.22 (1) allows. The export's own `depth` field is the PRINTED badge's reading and is rendered
as the badge, never as a second number.

**Nothing leaves the page:** no `<script src>`, no stylesheet link, no webfont, no remote image —
`scripts/build_dashboard.py`'s rule, and the same reason: a screen that phones home is a screen the
operator cannot open on a train.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

EXPORT = REPO_ROOT / "results" / "promo_screen_data.json"
OUT = REPO_ROOT / "dashboard" / "promo.html"

REQUIRED = ("positions", "depth_by_chain_and_brand", "weeks", "rollup", "feed", "table_rows")
"""Every block the page renders. Named as a closed list so a source that stops being exported is a
refusal here rather than an empty section nobody notices."""

RESULTS = REPO_ROOT / "results"
S2_SOURCES = (
    (
        "holdout-2 · loop (hooks + P1) — shipped",
        "grade_promo_loop_readings.json",
        ("sets", "dev3"),
        False,
    ),
    ("holdout-2 · with P1 — reading", "grade_promo_p1_readings.json", ("sets", "dev3"), True),
    ("holdout-2 · raw — reading", "grade_promo_holdout2.json", (), False),
    ("holdout-40 · raw — reading", "grade_promo_holdout40.json", (), False),
)
"""label · file under `results/` · the path to the block inside it · does this row carry the TIE
sentence. A set's reading lives under `sets.<name>` with `after` / `bars_after` / `misses_after` —
the loop record and the P1 record share that shape; a grader's record keeps its one reading at the
top under `whole_40` / `bars`. Closed like REQUIRED: a missing file or block is a refusal, never a
blank row.

The tie flag is a FIELD and not «whichever files happen to carry `misses_after`»: two rows now do,
their counts differ by the row the hooks drop, and two unlabelled tie paragraphs under one table
would read as the same set counted twice. Ruling 08.09 (dd) item 6 pins the published tie count to
the P1 reading (16 of 28), so exactly one row here is True."""

S2_FILES = tuple(filename for _, filename, _, _ in S2_SOURCES)
"""The source filenames, unpacked ONCE. Both refusals name the closed list, and the shape of a
source row had already grown a field under two spellings of that name — one of which was in a
message only `--check` reaches ([[a_patch_list_closed_by_enumeration]])."""

S2_BOUNDARY = (
    "The shipped row is the product's pipeline end to end: every answer through the four hooks of"
    " §2 S4 — a signal row whose quote is not a substring of the comment it cites is dropped — and"
    " then P1. The readings below it graded the model's raw answer, upstream of that filter, so"
    " they are the model's numbers and stand at or above the product's (ruling 08.09 (dd))."
)
"""The one sentence that says what separates the shipped row from the readings under it. Defined
once and rendered on both surfaces, like `s2_readings` itself — a boundary explained two ways is
two boundaries."""


def s2_readings(results: Path = RESULTS) -> list[dict]:
    """The S2 rows the screen and the README print — value, bar and `held` as the files say them.

    One reader for both surfaces, so they cannot disagree. Refuses a missing file, and a file that
    lacks the block it is read for, by name.
    """
    rows = []
    for label, filename, inside, ties in S2_SOURCES:
        path = results / filename
        if not path.exists():
            raise SystemExit(
                f"promo-screen REFUSED: missing S2 source {path} — the S2 block reads"
                f" {', '.join(S2_FILES)} and prints no number it did not read"
            )
        block = json.loads(path.read_text(encoding="utf-8"))
        try:
            for key in inside:
                block = block[key]
            reading = block["after"] if inside else block["whole_40"]
            rows.append(
                {
                    "label": label,
                    "file": f"results/{filename}",
                    "block": ".".join((*inside, "after")) if inside else "whole_40",
                    "bars": block["bars_after"] if inside else block["bars"],
                    "agreed": reading["subject_agreed"],
                    "comments": reading["subject_comments"],
                    "misses": block["misses_after"] if ties else None,
                }
            )
        except KeyError as error:
            raise SystemExit(
                f"promo-screen REFUSED: {path} carries no {error} under"
                f" {'.'.join(inside) or 'its top level'} — the S2 block will not print a blank"
            ) from error
    return rows


def s2_table(rows: list[dict]) -> str:
    """Reader agreement on the frozen holdouts — subject per comment, signal per thread — each
    beside its bar and the grader's own verdict, and the tie count the P1 record carries."""
    body = "".join(
        "<tr>"
        f"<td>{html.escape(row['label'])}</td>"
        f"<td class='num'>{sub['value']:.4f} ({row['agreed']}/{row['comments']})"
        f" {'✅' if sub['held'] else '❌'} bar {sub['bar']:.2f}</td>"
        f"<td class='num'>{sig['value']:.4f} {'✅' if sig['held'] else '❌'} bar {sig['bar']:.2f}</td>"
        f"<td><code>{html.escape(row['file'])}</code> :: {html.escape(row['block'])}</td>"
        "</tr>"
        for row in rows
        for sub, sig in ((row["bars"]["subject_agreement"], row["bars"]["signal_type_agreement"]),)
    )
    ties = "".join(
        f"<p>Of the {row['misses']['total']} comments still missed with P1, "
        f"{row['misses']['gold_unsure']} are rows the gold itself marked <code>unsure</code> — "
        "the codebook allows two readings there (a store-stock complaint: the chain or the product;"
        " a post in the chain's own channel: the chain or the post).</p>"
        for row in rows
        if row["misses"]
    )
    return (
        "<table><tr><th>reading</th><th>subject — what the comment is about (per comment)</th>"
        "<th>signal — what it says (per thread)</th><th>file</th></tr>" + body + "</table>"
        + f"<p>{html.escape(S2_BOUNDARY)}</p>" + ties
    )

CSS = """
body{font:14px/1.45 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#faf9f7;color:#1c1b19}
main{max-width:1100px;margin:0 auto;padding:24px}
h1{font-size:20px;margin:0 0 4px} h2{font-size:15px;margin:28px 0 8px}
p.sub{color:#6b675f;margin:0 0 18px}
table{border-collapse:collapse;width:100%;font-size:13px;background:#fff}
th,td{border-bottom:1px solid #eae7e1;padding:6px 8px;text-align:left;vertical-align:top}
th{background:#f2efe9;font-weight:600}
td.num{text-align:right;font-variant-numeric:tabular-nums}
.badge{background:#e8f3ea;color:#1d6b2f;border-radius:3px;padding:1px 5px;font-weight:600}
.empty{color:#8a857c;font-style:italic}
.counts span{display:inline-block;margin-right:14px}
"""


def load(path: Path) -> dict:
    """The export, or a named refusal. Both failure modes exit non-zero with the path in the text."""
    if not path.exists():
        raise SystemExit(
            f"promo-screen REFUSED: missing source {path} — `make tick` writes it, and this screen"
            " reads no other file. Run `make tick` first."
        )
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(f"promo-screen REFUSED: {path} is not readable JSON ({error})") from error
    screen = document.get("screen")
    if not isinstance(screen, dict):
        raise SystemExit(f"promo-screen REFUSED: {path} carries no `screen` block")
    missing = [name for name in REQUIRED if name not in screen]
    if missing:
        raise SystemExit(
            f"promo-screen REFUSED: {path} is missing {', '.join(missing)} — the screen renders"
            f" every one of {', '.join(REQUIRED)} and will not print a blank panel instead."
        )
    return document


def volume(item: dict) -> str:
    """The product's volume as the leaflet printed it — absent when the leaflet printed none."""
    if item.get("size_value") is None:
        return ""
    value = item["size_value"]
    shown = f"{value:g}"
    return f"{shown} {item.get('size_unit') or ''}".strip()


def rows_table(positions: list[dict]) -> str:
    """brand · product · volume · promo price · printed −N%. The five columns SP-0 q2 ruled, and
    nothing derived from a price the screen may not print."""
    if not positions:
        return "<p class='empty'>No positions yet — the C2 leg has not been bought.</p>"
    body = []
    for row in sorted(positions, key=lambda r: (r["chain"]["id"], r["row_id"])):
        item = row.get("item") or {}
        printed = row.get("printed_pct")
        price = row.get("promo_price")
        price_cell = "" if price is None else f"{price:g}"
        printed_cell = "" if printed is None else f"<span class='badge'>−{printed:g}%</span>"
        body.append(
            "<tr>"
            f"<td>{html.escape(row['chain']['id'])}</td>"
            f"<td>{html.escape((row.get('brand') or {}).get('display') or '')}</td>"
            f"<td>{html.escape(item.get('line') or item.get('category') or '')}</td>"
            f"<td>{html.escape(volume(item))}</td>"
            f"<td class='num'>{price_cell}</td>"
            f"<td class='num'>{printed_cell}</td>"
            "</tr>"
        )
    return (
        "<table><tr><th>chain</th><th>brand</th><th>product</th><th>volume</th>"
        "<th>promo price</th><th>printed</th></tr>" + "".join(body) + "</table>"
    )


def depth_table(rows: list[dict]) -> str:
    """Depth per chain and brand, per week — the WINDOW aggregate of SPEC 3.22 (1), in its own
    panel so it never sits in a row beside that row's own promo price."""
    if not rows:
        return "<p class='empty'>No depth readings yet.</p>"
    body = "".join(
        "<tr>"
        f"<td>{html.escape(row['week'])}</td>"
        f"<td>{html.escape(row['chain'])}</td>"
        f"<td>{html.escape(row['brand'] or '')}</td>"
        f"<td class='num'>{row['depth_mean'] * 100:.1f}%</td>"
        "</tr>"
        for row in rows
    )
    return (
        "<table><tr><th>week</th><th>chain</th><th>brand</th><th>mean depth</th></tr>"
        + body
        + "</table>"
    )


def feed_table(rows: list[dict]) -> str:
    """The reaction feed: signal · quote · msg_id · thread — §1's four fields, in that order."""
    if not rows:
        return (
            "<p class='empty'>No reactions yet — the C3 signal leg has not been bought, so no"
            " thread has been read.</p>"
        )
    body = "".join(
        "<tr>"
        f"<td>{html.escape(row['type'])}</td>"
        f"<td>{html.escape(row['quote'])}</td>"
        f"<td class='num'>{row['msg_id']}</td>"
        f"<td>{html.escape(row['channel'])} / {row['thread_root']}</td>"
        "</tr>"
        for row in rows
    )
    return (
        "<table><tr><th>signal</th><th>quote</th><th>msg_id</th><th>thread</th></tr>"
        + body
        + "</table>"
    )


def render(document: dict, s2: list[dict]) -> str:
    screen = document["screen"]
    weeks = screen["weeks"]
    counts = "".join(
        f"<span>{html.escape(name)}: <b>{value}</b></span>"
        for name, value in sorted(screen["table_rows"].items())
    )
    return (
        "<!doctype html><html lang='uk'><meta charset='utf-8'>"
        "<title>Promo pulse — тижнева витрина</title>"
        f"<style>{CSS}</style><main>"
        "<h1>Що і почём промоутують мережі — тиждень за тижнем</h1>"
        f"<p class='sub'>window <code>{html.escape(document['window_id'])}</code> · weeks "
        f"{html.escape(', '.join(weeks)) if weeks else '<i>none</i>'} · rendered from "
        "<code>results/promo_screen_data.json</code> only</p>"
        f"<p class='counts'>{counts}</p>"
        "<h2>Промо-позиції</h2>" + rows_table(screen["positions"]) +
        "<h2>Глибина знижки — per chain and brand (window aggregate)</h2>"
        + depth_table(screen["depth_by_chain_and_brand"]) +
        "<h2>Реакція покупців</h2>" + feed_table(screen["feed"]) +
        "<h2>S2 — the reader's grade on the frozen holdouts (shipped as measured)</h2>"
        + s2_table(s2) +
        "</main></html>\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", type=Path, default=EXPORT)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument(
        "--results", type=Path, default=RESULTS,
        help="the directory the S2 sources are read from (default: results/)",
    )
    parser.add_argument("--check", action="store_true", help="load the sources and render nothing")
    args = parser.parse_args(argv)

    document = load(args.export)
    s2 = s2_readings(args.results)
    if args.check:
        print(
            f"promo-screen: {args.export} is complete — {', '.join(REQUIRED)} all present;"
            f" S2 sources {', '.join(S2_FILES)} read from {args.results}"
        )
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(document, s2), encoding="utf-8")
    print(f"wrote {args.out} from {args.export} + {len(s2)} S2 readings under {args.results}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
