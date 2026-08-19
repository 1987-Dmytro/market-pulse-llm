#!/usr/bin/env python3
"""What a reader top-up over the uncovered threads would COST and what it would CHANGE.

**Why this record exists before any pack.** `docs/reports/lora-b.md` priced branch B at «105 ×
51.3 s ≈ $1.20» — the mean seconds of the 27 threads the reader has already read, applied to a
population whose sizes are not theirs. That is the projected-rate-versus-measured-rate defect in its
usual clothing, and it is worth exactly one afternoon of arithmetic to find out before a pod exists
([[projected_rate_versus_measured_rate]]). This module prices the buy from the thread sizes
themselves and, in the same record, prices what it BUYS — because the operator ruled branch B to
close a train/eval gap, and a buy that closes half of it should say so before the money and not
after.

**The model.** `seconds ≈ intercept + slope × payable`, least squares over the 26 v5b items that
carry both. The in-sample total is NOT evidence — OLS with an intercept forces the residuals to sum
to zero, so «the fit reproduces the total» is arithmetic, not accuracy. The out-of-sample check is
the v4 run: the v5b fit predicts its 22 items 1.08× high, which is the honest error bar and the
reason the projection is published beside a multiple rather than alone.

**What this record does NOT do: authorise anything.** It carries no cap. Caps in this repo come
from the operator, and this is the arithmetic that ruling needs.

    PYTHONPATH=src python3.11 scripts/project_reader_topup.py
    PYTHONPATH=src python3.11 scripts/project_reader_topup.py --outdir /tmp/again
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pass1_sft as sft  # noqa: E402
import gate_census_w1_reader as cell  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

V5B = REPO_ROOT / "results" / "reader_v5b_w1.jsonl"
V4 = REPO_ROOT / "results" / "reader_v4_w1.jsonl"
V5B_PACK = REPO_ROOT / "results" / "reader_v5b_pack.json"
ARM_B = REPO_ROOT / "results" / "pass1_sft_arm_b.jsonl"
SFT_RECORD = REPO_ROOT / "results" / "pass1_sft.json"
OUT_NAME = "results/reader_topup_projection.json"

CHUNK = 16
"""Payable comments per reader request, from the v5b pack's own largest item.

Not a preference: v5b split its 43-comment thread into 16 / 16 / 11 and read every other thread
whole, so 16 is the largest unit that instrument has ever been asked to read. The three threads over
100 comments in this population are the reason the rule has to be stated at all."""

PRICE = {"reader_card_example": 0.74, "ceiling": 0.80}
"""$0.74/h is what reader-v5b was BILLED at on a 24 GB card — the class this run asks for — and
$0.80/h is the ceiling lora-b's kill-clock uses. Both are worked, because the first is what this
run is likely to pay and the second is what it may not exceed."""

BOOT_SECONDS = 450
"""Charged in full, from lora-b's own rung: the worst boot this stack has measured (293 s) × 1.5.
A leg cannot cost more than the clock that kills it."""


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in summary.read_text_or_refuse(path).splitlines() if line]


def seconds_of(row: dict) -> float | None:
    value = row.get("seconds")
    if isinstance(value, dict):
        return sum(float(one) for one in value.values() if isinstance(one, (int, float)))
    return float(value) if value else None


def measured(path: Path) -> list[tuple[int, float]]:
    out = []
    for row in jsonl(path):
        size, taken = row.get("payable_comments"), seconds_of(row)
        if size and taken:
            out.append((int(size), taken))
    return out


def fit(pairs: list[tuple[int, float]]) -> dict:
    n = len(pairs)
    sx = sum(one[0] for one in pairs)
    sy = sum(one[1] for one in pairs)
    sxx = sum(one[0] ** 2 for one in pairs)
    sxy = sum(one[0] * one[1] for one in pairs)
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    intercept = (sy - slope * sx) / n
    residuals = sorted(taken - (intercept + slope * size) for size, taken in pairs)
    return {
        "intercept_seconds": round(intercept, 4),
        "slope_seconds_per_payable": round(slope, 5),
        "n": n,
        "line": "seconds ≈ intercept + slope × payable comments, least squares",
        "residuals": {
            "min": round(residuals[0], 2),
            "median": round(residuals[n // 2], 2),
            "max": round(residuals[-1], 2),
        },
        "in_sample_total_is_not_evidence": (
            "least squares with an intercept forces the residuals to sum to zero, so this line"
            " reproduces the total of its OWN 26 items exactly. That is arithmetic. The check below"
            " is the one that carries information"
        ),
    }


def out_of_sample(model: dict) -> dict:
    """The v4 run, predicted by the v5b fit — the only error bar this projection is entitled to."""
    pairs = measured(V4)
    predicted = sum(
        model["intercept_seconds"] + model["slope_seconds_per_payable"] * s for s, _ in pairs
    )
    actual = sum(one[1] for one in pairs)
    return {
        "run": "reader-v4",
        "record": summary.rel(V4),
        "items": len(pairs),
        "measured_seconds": round(actual, 1),
        "predicted_seconds": round(predicted, 1),
        "ratio": round(predicted / actual, 4),
        "reading": (
            "the v5b fit predicts v4's threads 1.08× high — a different prompt revision on the same"
            " instrument family, which is the closest thing to a held-out set this run has"
        ),
    }


def population() -> dict:
    """The threads that carry training rows and have NO bought verdict, with their sizes."""
    context = sft.verdicts()
    rows = jsonl(ARM_B)
    threads = {row["thread"] for row in rows}
    need = sorted(one for one in threads if one not in context)
    have = sorted(one for one in threads if one in context)
    sizes = {}
    for one in cell.population():
        name = f"{one['channel']}:{one['post_id']}"
        if name in need:
            sizes[name] = [int(row["msg_id"]) for row in one["comments"]]
    if sorted(sizes) != need:
        raise SystemExit(
            f"{len(need)} threads need a verdict and the reader cell enumerates {len(sizes)} of"
            " them — the training set and the cell have parted. Stop and report."
        )
    digest = hashlib.sha256(
        "\n".join(
            f"{name}\t{','.join(str(one) for one in sizes[name])}" for name in sorted(sizes)
        ).encode("utf-8")
    ).hexdigest()
    counts = sorted(len(one) for one in sizes.values())
    return {
        "threads_needing_a_verdict": len(need),
        "threads_already_bought": len(have),
        "payable_comments": sum(counts),
        "per_thread": {"min": counts[0], "median": counts[len(counts) // 2], "max": counts[-1]},
        "largest": sorted(
            ({"thread": name, "payable": len(ids)} for name, ids in sizes.items()),
            key=lambda one: (-one["payable"], one["thread"]),
        )[:5],
        "enumeration_sha256": digest,
        "enumeration_rule": (
            "sha256 over `channel:post_id\\tpayable msg_ids` per thread in sorted order. A pack"
            " built later is held to THIS list rather than re-deriving a population that may have"
            " moved"
        ),
        "sizes": {name: len(ids) for name, ids in sorted(sizes.items())},
    }


def chunks_of(size: int) -> list[int]:
    if size <= 0:
        return [0]
    whole, rest = divmod(size, CHUNK)
    return [CHUNK] * whole + ([rest] if rest else [])


def projection(model: dict, pop: dict) -> dict:
    pieces = [one for size in pop["sizes"].values() for one in chunks_of(size)]
    generation = sum(
        model["intercept_seconds"] + model["slope_seconds_per_payable"] * one for one in pieces
    )
    all_in = generation + BOOT_SECONDS
    return {
        "chunk_payable_max": CHUNK,
        "chunk_rule": (
            "the largest unit v5b ever read is 16 payable comments — it split its 43-comment thread"
            " into 16/16/11. Three threads here hold 105, 108 and 125, so the rule decides the item"
            " count and not just the order"
        ),
        "items": len(pieces),
        "generation_seconds": round(generation, 1),
        "boot_seconds_charged": BOOT_SECONDS,
        "all_in_seconds": round(all_in, 1),
        "all_in_hours": round(all_in / 3600, 4),
        "usd": {name: round(all_in / 3600 * rate, 4) for name, rate in sorted(PRICE.items())},
        "at_the_out_of_sample_ratio": {
            name: round(all_in / 3600 * rate * 1.08, 4) for name, rate in sorted(PRICE.items())
        },
        "what_the_report_published": {
            "usd": 1.2,
            "how": "105 threads × the MEAN 51.3 s of the 27 already read",
            "why_it_was_wrong": (
                "the mean of one population applied to another. These threads are smaller on"
                " average and there are more items than threads, and the two errors do not cancel"
            ),
        },
    }


def what_it_buys() -> dict:
    """What the verdicts would change in the training set — measured where it can be measured."""
    rows = jsonl(ARM_B)
    context = sft.verdicts()
    covered = [row for row in rows if row["thread"] in context]
    with_block = sum(1 for row in rows if row["context"]["entities"])
    cut = sum(1 for row in rows if row["context"]["topic_cut"])
    record = json.loads(summary.read_text_or_refuse(SFT_RECORD))
    gate = record["census"]["the_gate_s_own_rows"]
    threads_with_entities = sum(
        1 for _, verdict in context.values() if (verdict.get("entities") or [])
    )
    rate = sum(1 for row in covered if row["context"]["entities"]) / len(covered)
    return {
        "topic": {
            "rows_whose_topic_is_substituted_today": len(rows) - len(covered),
            "rows_whose_topic_is_cut_and_marked_today": cut,
            "after": (
                "every one of the 650 topics becomes a bought reader summary — the same kind the"
                " eval prompts carry. The branch-C ellipsis marker, which sits on 372 training rows"
                " and 0 eval prompts, disappears entirely"
            ),
            "this_is_the_half_the_buy_closes_completely": True,
        },
        "entity_block": {
            "rows_with_one_today": with_block,
            "of": len(rows),
            "rate_inside_the_threads_already_bought": round(rate, 4),
            "threads_resolving_at_least_one_entity": f"{threads_with_entities} of {len(context)}",
            "expected_after": round(with_block + (len(rows) - len(covered)) * rate),
            "expected_rule": (
                f"the {len(covered)} rows in bought threads carry a block at {rate:.0%}, measured on"
                " 15 threads and 91 rows — a thin sample, and the only one there is. Applied to the"
                " rows in the unbought threads it projects the count below"
            ),
            "the_gate_for_comparison": (
                f"{gate['with_an_entity_block']} of {gate['n']} gate rows carry a block"
            ),
            "this_is_the_half_the_buy_closes_PARTIALLY": True,
            "why": (
                "a reader verdict resolves entities only where the thread HAS them. Ten of the 24"
                " threads already bought resolve none at all — recipe and marketplace threads name"
                " nobody — while the gate's rows sit in exam threads chosen for carrying signal."
                " The residual gap is a property of the population and no amount of money closes it"
            ),
        },
    }


def build() -> dict:
    pairs = measured(V5B)
    model = fit(pairs)
    pop = population()
    return {
        "authorises_nothing": (
            "this record prices a buy and measures what it would change. It carries NO cap: caps in"
            " this repo are the operator's word, and a projection that named one would be a"
            " registration nobody ruled"
        ),
        "buys": what_it_buys(),
        "contract": "docs/reports/lora-b.md — branch B of the fork, ruled by the operator 2026-08-19",
        "instrument": {
            "measured_on": summary.rel(V5B),
            "pack": summary.rel(V5B_PACK),
            "sha256": summary.sha256_of(V5B),
            "model": model,
            "out_of_sample": out_of_sample(model),
        },
        "population": pop,
        "producer": {"script": "scripts/project_reader_topup.py"},
        "projection": projection(model, pop),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    record = build()
    record["producer"]["sha256"] = summary.sha256_of(Path(__file__))
    out = args.outdir / OUT_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUT_NAME}  sha256 {summary.sha256_of(out)[:16]}…")

    pop, proj = record["population"], record["projection"]
    model = record["instrument"]["model"]
    print(
        f"\nPOPULATION  {pop['threads_needing_a_verdict']} threads with no verdict ·"
        f" {pop['payable_comments']} payable comments"
        f" (min {pop['per_thread']['min']} · median {pop['per_thread']['median']} ·"
        f" max {pop['per_thread']['max']})"
    )
    print(f"            largest: {', '.join(one['thread'] for one in pop['largest'][:3])}")
    print(
        f"MODEL       seconds ≈ {model['intercept_seconds']} +"
        f" {model['slope_seconds_per_payable']} × payable  (n={model['n']});"
        f" out of sample {record['instrument']['out_of_sample']['ratio']}× on v4"
    )
    print(
        f"PROJECTION  {proj['items']} items ·"
        f" {proj['generation_seconds']:.0f} s of generation + {proj['boot_seconds_charged']} s boot"
        f" = {proj['all_in_hours']:.2f} h"
    )
    print(
        f"            ${proj['usd']['reader_card_example']:.2f} at $0.74/h ·"
        f" ${proj['usd']['ceiling']:.2f} at the $0.80/h ceiling ·"
        f" ${proj['at_the_out_of_sample_ratio']['ceiling']:.2f} at the ceiling × the v4 ratio"
    )
    print(
        f"            the report published ${proj['what_the_report_published']['usd']:.2f} —"
        f" {proj['what_the_report_published']['how']}"
    )
    buys = record["buys"]
    print(
        f"\nBUYS        topic: {buys['topic']['rows_whose_topic_is_substituted_today']} substituted"
        f" rows become bought summaries; the {buys['topic']['rows_whose_topic_is_cut_and_marked_today']}"
        " ellipsis markers go to 0 — the half it closes COMPLETELY"
    )
    entity = buys["entity_block"]
    print(
        f"            entity block: {entity['rows_with_one_today']} of {entity['of']} today ->"
        f" ~{entity['expected_after']} expected, at the {entity['rate_inside_the_threads_already_bought']:.0%}"
        f" rate measured inside the bought threads ({entity['threads_resolving_at_least_one_entity']}"
        f" resolve any). {entity['the_gate_for_comparison']} — the half it closes PARTIALLY"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
