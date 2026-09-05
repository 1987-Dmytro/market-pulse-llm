#!/usr/bin/env python3
"""K8 — the S2 grader: subject and signal-type agreement on dev-40. $0.

`docs/PHASE-promo-pulse-1.md` §2 S2:

    subject agreement     >= 0.80
    signal-type agreement >= 0.75      on dev-40
    per-stratum agreement is REPORTED BESIDE THEM AS A READING (review 30.08, SP-0 q3)

The two agreements are different shapes and the record says which is which rather than printing one
word twice:

**Subject agreement** is per COMMENT. Gold gives each comment a (subject_type, subject) pair; a
prediction agrees when both halves match after `aggregates.promo_key` normalisation. The
denominator is the gold comments — comments the model said nothing about count as disagreements,
because silence on a comment the codebook labels IS a miss. An abstention is an answer
([[an_abstention_is_an_answer]]): rows the instrument routed to `unsure` are counted and named, and
they still sit in the denominator.

**Signal-type agreement** is per THREAD, over the SET of types. Jaccard — |gold ∩ predicted| over
|gold ∪ predicted| — averaged over threads, so a thread the model over-labels loses as much as one
it under-labels, and a thread where both sides say nothing scores 1.0 rather than dividing by zero.
Stated here because "agreement" has no single meaning and a bar over an undefined metric is not a
bar ([[a_published_ratio_is_not_the_gates]]).

**Split the rate before reporting it.** The draw has two strata and the whole point of stratifying
was to see whether the `decimal`-only half grades worse. Both bars are computed on the whole 40 —
that is what the bar is on — and again per stratum as a reading, which is what the review asked for
([[measure_on_the_rows_the_gate_scores]]).

Written and driven against SYNTHETIC gold (`tests/test_grade_promo_signals.py`); the real run needs
`docs/labels-promo-dev.jsonl`, which is the team lead's and lands after S7's draw.

    python3.11 scripts/grade_promo_signals.py --gold docs/labels-promo-dev.jsonl \\
        --predicted results/promo_dev40_predicted.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse.aggregates import chain_key, promo_key  # noqa: E402

DRAW = REPO_ROOT / "results" / "promo_threads_draw.json"
OUT = REPO_ROOT / "results" / "grade_promo_dev40.json"

BARS = {"subject_agreement": 0.80, "signal_type_agreement": 0.75}


def rows(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path} is missing — the grader may not score against nothing")
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    body = json.loads(text)
    return body if isinstance(body, list) else body["rows"]


def subject(row: dict) -> tuple:
    """(type, name) as the grade compares them — `chain` names folded to the chain's id.

    Codebook v1.1 (б) and ruling 04.09 (j) item 1: «VARUS» and «Варус» are one chain, so both sides
    of the comparison go through `aggregates.chain_key` — gold and prediction alike, and `chain`
    rows only ([[correcting_gold_moves_the_denominator]]: the fold moves no row's gold, it stops
    two spellings of one answer from reading as two answers).
    """
    kind = promo_key(row.get("subject_type") or "")
    name = row.get("subject") or ""
    return (kind, chain_key(name) if kind == "chain" else promo_key(name))


def thread_key(row: dict) -> tuple:
    return (row.get("channel") or "", str(row.get("thread_root") or ""))


def strata_of(draw_path: Path, part: str = "dev") -> dict:
    """(channel, thread_root) → stratum, from the draw record. Absent file = no split, said so.

    ONE arm of the draw, never both: the dev half and the frozen holdout are disjoint populations
    and a map carrying both would give a dev run a stratum for a thread it never scored
    ([[a_second_population_in_a_shared_store_voids_the_first_seal]]). `dev` stays the default, so
    every reading taken before ruling 05.09 (q) means what it meant."""
    if not draw_path.exists():
        return {}
    body = json.loads(draw_path.read_text(encoding="utf-8"))
    return {
        (row["channel"], str(row["thread_root"])): stratum
        for stratum, block in body.get("draw", {}).items()
        for row in block.get(part, [])
    }


def agree(gold: list[dict], predicted: list[dict]) -> dict:
    """The two agreements over one set of threads. Both bounded in [0, 1] by construction."""
    said = {(thread_key(row), str(row.get("msg_id"))): row for row in predicted if row.get("msg_id")}
    comments = [row for row in gold if row.get("msg_id")]
    hits = [
        row
        for row in comments
        if (found := said.get((thread_key(row), str(row["msg_id"])))) is not None
        and subject(found) == subject(row)
    ]

    gold_types, said_types = defaultdict(set), defaultdict(set)
    for row in gold:
        gold_types[thread_key(row)] |= {promo_key(one) for one in (row.get("signal_types") or [])}
    for row in predicted:
        said_types[thread_key(row)] |= {promo_key(one) for one in (row.get("signal_types") or [])}
    threads = sorted(set(gold_types) | {key for key in said_types if key in gold_types})
    jaccard = [
        1.0
        if not (gold_types[key] | said_types[key])
        else len(gold_types[key] & said_types[key]) / len(gold_types[key] | said_types[key])
        for key in threads
    ]
    return {
        "subject_agreement": round(len(hits) / len(comments), 4) if comments else None,
        "subject_comments": len(comments),
        "subject_agreed": len(hits),
        "signal_type_agreement": round(sum(jaccard) / len(jaccard), 4) if jaccard else None,
        "signal_type_threads": len(threads),
    }


def grade(gold: list[dict], predicted: list[dict], strata: dict) -> dict:
    whole = agree(gold, predicted)
    by_stratum = {}
    for stratum in sorted(set(strata.values())):
        keys = {key for key, name in strata.items() if name == stratum}
        by_stratum[stratum] = agree(
            [row for row in gold if thread_key(row) in keys],
            [row for row in predicted if thread_key(row) in keys],
        )
    unsure = [row for row in predicted if row.get("unsure")]
    return {
        "bars": {
            name: {
                "value": whole[name],
                "bar": bar,
                "held": whole[name] is not None and whole[name] >= bar,
            }
            for name, bar in BARS.items()
        },
        "whole_40": whole,
        "by_stratum": by_stratum or {"note": "no draw record — the split could not be reported"},
        "readings": {
            "unsure_rows": len(unsure),
            "note": "an abstention is an answer: `unsure` rows stay in the denominator and are"
            " counted here, never dropped from it",
        },
        "definitions": {
            "subject_agreement": "per COMMENT: (subject_type, subject) after aggregates.promo_key,"
            " with `chain` names folded to the chain id by aggregates.chain_key (ruling 04.09 (j)"
            " item 1) on gold and prediction alike; denominator = gold comments; a comment the"
            " model said nothing about is a miss",
            "signal_type_agreement": "per THREAD: Jaccard over the SET of signal types, averaged;"
            " a thread where both sides say nothing scores 1.0 rather than dividing by zero",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, default=REPO_ROOT / "docs" / "labels-promo-dev.jsonl")
    parser.add_argument("--predicted", type=Path, required=True)
    parser.add_argument("--draw", type=Path, default=DRAW)
    parser.add_argument(
        "--part", default="dev", choices=("dev", "holdout"), help="which arm of the draw it scores"
    )
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    record = {
        "contract": "docs/plans/promo-pulse-1.md K8 — the S2 grader ($0)",
        "gold": str(args.gold),
        "predicted": str(args.predicted),
        "part": args.part,
        **grade(rows(args.gold), rows(args.predicted), strata_of(args.draw, args.part)),
    }
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for name, block in sorted(record["bars"].items()):
        print(f"{name:<24} {block['value']} against {block['bar']} — {'HOLDS' if block['held'] else 'RED'}")
    for stratum, block in sorted(record["by_stratum"].items()):
        if isinstance(block, dict) and "subject_agreement" in block:
            print(
                f"  {stratum:<14} subject {block['subject_agreement']}"
                f" · types {block['signal_type_agreement']}  (reading, no bar)"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
