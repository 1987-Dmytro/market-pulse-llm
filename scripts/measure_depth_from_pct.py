#!/usr/bin/env python3
"""Can the printed «-N%» badge stand in for the crossed-out old price when depth is what we want? ($0)

The pilot's bar 2 read the badge at 61/61 and the crossed-out old price at 20/61, which reads like
an answer: drop the old price, take depth from the badge. Question 7 wants a weekly median depth,
not a price, so the question is not "which number is transcribed correctly" but "how far from the
true depth does each instrument land". That is measurable on what is already bought, for nothing.

For each of the 61 pairs, against the team lead's own `printed_old`:

* ``true_depth``      = (printed_old − promo) / printed_old — the page's arithmetic
* ``badge_depth``     = discount_pct_printed / 100 — the number the leaflet prints in the badge
* ``extracted_depth`` = (price_old − promo) / price_old — what the pipeline already computes

The third one is not in the brief and is the control that makes the first two mean something: every
dictated error is in the kopiyky (230.0 for 230.90), so an old price that is WRONG as a number can
still be right as a depth. Without that column the record would say "the badge is adequate" and a
reader would hear "and the old price is not", which is a different claim and, on this population,
not the one the numbers make.

    PYTHONPATH=src python3 scripts/measure_depth_from_pct.py

Writes `results/sku_depth_from_pct.json`. NO threshold is registered for any of this — it is an
input to the B′ design session, not a bar, and the adequacy rule it reads against is stated in the
record as this file's own, so nobody can mistake it for something that was pre-registered.
"""

import argparse
import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import apply_sku_pair_verdicts as pair_read  # noqa: E402

from market_pulse import provenance  # noqa: E402

RECORD = REPO_ROOT / "results" / "sku_b_positions_v4.json"
PAIRS = REPO_ROOT / "results" / "sku_b_pair_verdicts.json"
OUT = REPO_ROOT / "results" / "sku_depth_from_pct.json"

CONTRACT = "docs/PROMPT-sku-b-close.md deliverable 4"

ADEQUACY = (
    "adequate for a weekly median = every pair within 2 pp of the true depth AND the median within"
    " 1 pp. STATED HERE, not registered: no bar was pre-registered for this measurement and the"
    " real threshold is the operator's to set at the B′ design session"
)
WITHIN = (0.01, 0.02)
"""The two tolerances the summary counts, as fractions of 1 — 1 pp and 2 pp of depth."""

rel = pair_read.rel
refuse = pair_read.refuse
sha256_of = pair_read.sha256_of


def depth(promo: float, old: float) -> float:
    """`(old − promo) / old` — `positions.Position.depth`, over two loose numbers.

    Not a second implementation of a rule: `Position.depth` reads the fields of a position, and the
    thing being priced here is a price the position does NOT carry (the team lead's `printed_old`).
    The test pins this against the `depth` the dump's own producer wrote, on every pair where the
    two prices are the same number, so a drift between them is a red suite.
    """
    return (old - promo) / old


def measure(pairs: list[dict], read: dict) -> list[dict]:
    """One row per dump pair, joined to the key the team lead ruled on."""
    keys = {(key["file"], key["price_promo"], key["price_old"]): key for key in read["keys"]}
    if len(keys) != len(read["keys"]):
        refuse(f"{len(read['keys'])} keys collapse to {len(keys)} — the read is not keyed uniquely")
    rows = []
    for row in pairs:
        key = keys.get((row["file"], row["price_promo"], row["price_old"]))
        if key is None:
            refuse(f"{row['file']} {row['price_promo']}/{row['price_old']} is in no ruled-on key")
        if row["discount_pct_printed"] is None:
            refuse(f"{row['item']} carries no printed percentage — the badge has nothing to read")
        promo = row["price_promo"]
        true_depth = depth(promo, key["printed_old"])
        badge_depth = row["discount_pct_printed"] / 100
        extracted_depth = depth(promo, row["price_old"])
        rows.append(
            {
                "item": row["item"],
                "page": row["page"],
                "file": row["file"],
                "verdict": key["verdict"],
                "price_promo": promo,
                "price_old_extracted": row["price_old"],
                "price_old_printed": key["printed_old"],
                "discount_pct_printed": row["discount_pct_printed"],
                "true_depth": true_depth,
                "badge_depth": badge_depth,
                "extracted_depth": extracted_depth,
                "delta_badge": badge_depth - true_depth,
                "delta_extracted": extracted_depth - true_depth,
            }
        )
    return rows


def summarise(rows: list[dict], field: str) -> dict:
    """Median and max |delta|, the within-tolerance counts, and the pairs that miss 1 pp."""
    deltas = [row[field] for row in rows]
    absolute = [abs(value) for value in deltas]
    return {
        "n": len(rows),
        "median_abs_delta_pp": statistics.median(absolute) * 100,
        "max_abs_delta_pp": max(absolute) * 100,
        "mean_signed_delta_pp": statistics.mean(deltas) * 100,
        "within_1pp": sum(value <= WITHIN[0] for value in absolute),
        "within_2pp": sum(value <= WITHIN[1] for value in absolute),
        "outside_1pp": [
            {
                "item": row["item"],
                "file": row["file"].rsplit("/", 1)[-1],
                "price_promo": row["price_promo"],
                "delta_pp": row[field] * 100,
            }
            for row in sorted(rows, key=lambda r: -abs(r[field]))
            if abs(row[field]) > WITHIN[0]
        ],
    }


def adequate(summary: dict) -> bool:
    return summary["max_abs_delta_pp"] <= WITHIN[1] * 100 and (
        summary["median_abs_delta_pp"] <= WITHIN[0] * 100
    )


def reading(badge: dict, extracted: dict) -> str:
    """The plain sentence the brief asks for — computed from the two summaries, not written down."""
    verdict = "IS" if adequate(badge) else "is NOT"
    other = "also is" if adequate(extracted) else "is not"
    return (
        f"the badge {verdict} an adequate depth instrument for a weekly median"
        f" (median {badge['median_abs_delta_pp']:.2f} pp, max {badge['max_abs_delta_pp']:.2f} pp,"
        f" {badge['within_2pp']}/{badge['n']} within 2 pp) — and the old price the pipeline already"
        f" extracts {other} ({extracted['median_abs_delta_pp']:.2f} pp median,"
        f" {extracted['max_abs_delta_pp']:.2f} pp max), because every error the team lead found is"
        " in the kopiyky and depth barely moves on them. Bar 2 fails on the printed NUMBER; on this"
        " population it does not fail on the DEPTH that number is used for"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--dump", type=Path, help="default: the record's own dump path")
    parser.add_argument("--pairs", type=Path, default=PAIRS)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    record = json.loads(args.record.read_text(encoding="utf-8"))
    dump_path = args.dump or REPO_ROOT / record["dump"]["path"]
    dump_sha = sha256_of(dump_path)
    read = json.loads(args.pairs.read_text(encoding="utf-8"))
    if read["dump"]["sha256"] != dump_sha:
        refuse(
            f"{rel(args.pairs)} was read over a dump hashing {read['dump']['sha256'][:16]}… and"
            f" {rel(dump_path)} hashes {dump_sha[:16]}… — two different sets of pairs"
        )

    dump = [json.loads(line) for line in dump_path.read_text(encoding="utf-8").splitlines() if line]
    rows = measure(pair_read.pair_rows(dump), read)
    if len(rows) != read["checksums"]["rows"]:
        refuse(f"{len(rows)} pairs measured against the {read['checksums']['rows']} that were read")

    badge = summarise(rows, "delta_badge")
    extracted = summarise(rows, "delta_extracted")
    out = {
        "phase": "sku-b — depth from the printed percentage, on the population already bought",
        "contract": CONTRACT,
        "class": (
            "MEASUREMENT for the B′ design session. NO threshold is registered and nothing here is"
            " a bar: it prices two candidate depth instruments against the team lead's own read of"
            " the pages, so the revision decision has a number under it"
        ),
        "dump": {"path": rel(dump_path), "sha256": dump_sha},
        "read": {"path": rel(args.pairs), "sha256": sha256_of(args.pairs)},
        "definitions": {
            "true_depth": "(printed_old − promo) / printed_old, printed_old from the team lead",
            "badge_depth": "discount_pct_printed / 100 — the leaflet's own «-N%»",
            "extracted_depth": "(price_old − promo) / price_old — what the pipeline computes today",
            "delta": "instrument − true, in depth units; reported in percentage POINTS",
        },
        "n_pairs": len(rows),
        "adequacy_rule": ADEQUACY,
        "instruments": {
            "badge": {**badge, "adequate": adequate(badge)},
            "extracted_old_price": {**extracted, "adequate": adequate(extracted)},
        },
        "reading": reading(badge, extracted),
        "rows": rows,
    }
    out["git"] = provenance.git_state(args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"{rel(dump_path)} — {len(rows)} pairs against the team lead's printed_old")
    for name, summary in out["instruments"].items():
        print(
            f"  {name:20s} median {summary['median_abs_delta_pp']:6.4f} pp ·"
            f" max {summary['max_abs_delta_pp']:6.4f} pp ·"
            f" ≤1pp {summary['within_1pp']}/{summary['n']} ·"
            f" ≤2pp {summary['within_2pp']}/{summary['n']}"
        )
    print(f"  {out['reading']}")
    print(f"wrote {rel(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
