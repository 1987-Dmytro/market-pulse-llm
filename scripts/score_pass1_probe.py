#!/usr/bin/env python3
"""`results/pass1_probe_verdict.json` — bar P1, the census, and what a window pass-1 would cost.

**Bar P1 CALLS bar 4's own comparison.** `scorer.reader_comment_agreement` is the function the reader
was scored with, and `score_reader_probe_b.collapse` is the collapse it was scored under; both are
imported, neither is restated. The ABSENT state and the per-row `scored_fields` come with them, which
is exactly why a fresh equality loop here would be a second definition of the bar
([[a_new_gate_can_subsume_the_old_one]]).

The census gates NOTHING. It buys the per-thread distribution over the neighbour rows, the refusals
by shape, the seconds and tokens per call, and the one number the next contract needs: what a pass-1
over the whole window would cost, at this run's own measured per-comment price.

    PYTHONPATH=src python3.11 scripts/score_pass1_probe.py
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import score_reader_probe_b as probe_b  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import scorer  # noqa: E402

PHASE = "pass1-probe"
PREREG = REPO_ROOT / "results" / "prereg_pass1_probe.json"
PACK = REPO_ROOT / "results" / "pass1_probe_pack.json"
EVIDENCE = REPO_ROOT / "results" / "pass1_probe_rows.jsonl"
RUN = REPO_ROOT / "results" / "pass1_probe_run.json"
GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
CENSUS_CELL = REPO_ROOT / "results" / "gate_census_w1_reader.json"
OUT = REPO_ROOT / "results" / "pass1_probe_verdict.json"


def rows() -> list[dict]:
    return [
        json.loads(line)
        for line in summary.read_text_or_refuse(EVIDENCE).splitlines()
        if line.strip()
    ]


def bar_p1(record: dict, evidence: list[dict]) -> dict:
    """The gating bar, through bar 4's own comparison and bar 4's own collapse.

    The answers handed in are only the ones whose UNIT was read: a gold row whose call never came
    back is `absent`, which the comparison already counts apart from a disagreement. Both readings
    are reported — over the registered fourteen, and over the rows the model actually answered —
    because a bar whose denominator can shrink through a transport failure has to publish both
    ([[measure_on_the_rows_the_gate_scores]]).
    """
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    registered = {(row["thread"], row["msg_id"]) for row in record["population"]["gold"]["rows"]}
    answered = {row["msg_id"]: row["parsed"] for row in evidence if row["parsed"]}

    wanted, answers = [], []
    for row in gold["per_comment"]:
        thread = f"{row['channel']}:{row['evidence_row']['post_id_in_the_store']}"
        if (thread, int(row["msg_id"])) not in registered:
            continue
        one = dict(row)
        one["subject_type"] = probe_b.collapse(one.get("subject_type"))
        wanted.append(one)
        said = answered.get(int(row["msg_id"]))
        if said is not None:
            answers.append({**said, "subject_type": probe_b.collapse(said.get("subject_type"))})

    result = scorer.reader_comment_agreement(wanted, answers)
    over_answered = None
    if result["absent"]:
        present = [one for one in wanted if int(one["msg_id"]) in answered]
        if present:
            narrow = scorer.reader_comment_agreement(present, answers)
            over_answered = {"n": narrow["n"], "agreed": narrow["agreed"], "rate": narrow["rate"]}
    threshold = int(record["bars"]["P1_per_comment_agreement"]["minimum_agreed"])
    return {
        **result,
        "threshold": record["bars"]["P1_per_comment_agreement"]["threshold"],
        "minimum_agreed": threshold,
        "passed": result["agreed"] >= threshold,
        "rate_over_the_rows_the_model_answered": over_answered,
        "losses": {
            "budget": int(
                record["bars"]["P1_per_comment_agreement"]["loss_budget"]["rows_that_may_be_lost"]
            ),
            "spent": result["n"] - result["agreed"],
            "by_cause": {"disagreed": result["disagreed"], "absent": result["absent"]},
        },
        "comparison": "market_pulse.scorer.reader_comment_agreement",
        "collapse": {"map": probe_b.COLLAPSE, "symmetric": True},
        "scored": True,
    }


def census(record: dict, evidence: list[dict]) -> dict:
    """Everything the neighbour rows bought, and not one number here moves P1."""
    neighbours = [row for row in evidence if row["leg"] == "census"]
    per_thread: dict[str, Counter] = {}
    for row in neighbours:
        got = (row["parsed"] or {}).get("subject_type") if row["parsed"] else "REFUSED"
        per_thread.setdefault(row["thread"], Counter())[str(got)] += 1
    return {
        "rule": "REPORTED and never gating — no number here moves bar P1",
        "n": len(neighbours),
        "parsed": sum(1 for row in neighbours if row["parsed"]),
        "subject_type_distribution": dict(
            Counter(
                str((row["parsed"] or {}).get("subject_type") if row["parsed"] else "REFUSED")
                for row in neighbours
            )
        ),
        "per_thread": {name: dict(counts) for name, counts in sorted(per_thread.items())},
        "stance_distribution": dict(
            Counter(str((row["parsed"] or {}).get("stance")) for row in neighbours if row["parsed"])
        ),
    }


def refusals(evidence: list[dict]) -> dict:
    shapes = Counter(row["parse_error"] for row in evidence if row["parse_error"])
    return {
        "refused": sum(shapes.values()),
        "of": len(evidence),
        "by_shape": dict(sorted(shapes.items())),
        "by_leg": dict(Counter(row["leg"] for row in evidence if row["parse_error"])),
        "never_balanced": sorted(row["id"] for row in evidence if row.get("balanced") is False),
        "finish_reason_length": sorted(
            row["id"] for row in evidence if row.get("finish_reason") == "length"
        ),
    }


def per_call(record: dict, evidence: list[dict]) -> dict:
    """What one pass-1 call actually cost, beside the two readings the registration published."""
    timed = [row for row in evidence if isinstance(row.get("usage"), dict) and row.get("seconds")]
    if not timed:
        return {"measured": False, "reason": "no row carries both a timing and a usage block"}
    seconds = sum(float(row["seconds"]) for row in timed)
    tokens = sum(int(row["usage"]["completion_tokens"]) for row in timed)
    prompt = sum(int(row["usage"]["prompt_tokens"]) for row in timed)
    reading = record["money"]["reading"]
    return {
        "measured": True,
        "calls": len(timed),
        "seconds": round(seconds, 3),
        "seconds_per_call": round(seconds / len(timed), 3),
        "completion_tokens_per_call": round(tokens / len(timed), 2),
        "prompt_tokens_per_call": round(prompt / len(timed), 2),
        "registered_bound_seconds_per_call": reading["ceiling"]["seconds_per_pass1_call"],
        "fitted_seconds_per_call": reading["fitted"]["seconds_per_pass1_call"],
        "against_the_bound": round(
            (seconds / len(timed)) / float(reading["ceiling"]["seconds_per_pass1_call"]), 4
        ),
        "against_the_fit": round(
            (seconds / len(timed)) / float(reading["fitted"]["seconds_per_pass1_call"]), 4
        ),
    }


def window_price(record: dict, calls: dict) -> dict:
    """What a pass-1 over the whole reader census cell would cost at THIS run's measured rate."""
    cell = json.loads(summary.read_text_or_refuse(CENSUS_CELL))
    payable = int(cell["measured"]["comments_payable"])
    rate = float(record["money"]["meter"]["worked_example_usd_per_hour"]) / 3600.0
    if not calls.get("measured"):
        return {"priced": False, "reason": calls.get("reason")}
    per_second = float(calls["seconds_per_call"])
    return {
        "priced": True,
        "cell": cell["cell"],
        "record": summary.rel(CENSUS_CELL),
        "sha256": summary.sha256_of(CENSUS_CELL),
        "payable_comments": payable,
        "seconds_per_call": per_second,
        "seconds": round(per_second * payable, 1),
        "usd_at_the_worked_example": round(per_second * payable * rate, 4),
        "rule": (
            "generation seconds only, at the worked example price and this run's own measured"
            " seconds per call. It carries no boot, no staging and no second pod — it is a FLOOR"
            " for a window pass-1, not a quote"
        ),
    }


def build() -> dict:
    record = json.loads(summary.read_text_or_refuse(PREREG))
    evidence = rows()
    pack = json.loads(summary.read_text_or_refuse(PACK))
    calls = per_call(record, evidence)
    verdict = {
        "phase": PHASE,
        "registration": {"record": summary.rel(PREREG), "sha256": summary.sha256_of(PREREG)},
        "pack": {"record": summary.rel(PACK), "sha256": summary.sha256_of(PACK)},
        "evidence": {
            "record": summary.rel(EVIDENCE),
            "sha256": summary.sha256_of(EVIDENCE),
            "units_registered": len(pack["items"]),
            "units_read": len(evidence),
        },
        "gold": {
            "record": summary.rel(GOLD),
            "sha256": summary.sha256_of(GOLD),
            "revision": "r2",
        },
        "scorer": {
            "module": "src/market_pulse/scorer.py",
            "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
            "borrowed": (
                "bar P1 through scorer.reader_comment_agreement and"
                " scripts/score_reader_probe_b.py::collapse — the reader's own comparison and the"
                " reader's own collapse, called and never restated"
            ),
        },
        "bars": {"P1_per_comment_agreement": bar_p1(record, evidence)},
        "census": census(record, evidence),
        "refusals": refusals(evidence),
        "per_call": calls,
        "window_pass1_price": window_price(record, calls),
        "return_to_sitting": record["return_to_sitting"],
    }
    verdict["outcome"] = "GO" if verdict["bars"]["P1_per_comment_agreement"]["passed"] else "STOP"
    if RUN.exists():
        state = json.loads(RUN.read_text(encoding="utf-8"))
        verdict["run"] = {
            "record": summary.rel(RUN),
            "sha256": summary.sha256_of(RUN),
            "segments": len(state.get("segments", [])),
            "gates": len(state.get("gates", [])),
            "billed_seconds": sum(
                float(one.get("billed_seconds") or 0) for one in state.get("segments", [])
            ),
            "billed_usd": round(
                sum(float(one.get("billed_usd") or 0) for one in state.get("segments", [])), 6
            ),
        }
    return verdict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    verdict = build()
    args.out.write_text(
        json.dumps(verdict, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")

    bar = verdict["bars"]["P1_per_comment_agreement"]
    print(
        f"\nBAR P1  {bar['agreed']} of {bar['n']} agreed  ({bar['threshold']})  -> {bar['passed']}"
    )
    print(
        f"  disagreed {bar['disagreed']} · absent {bar['absent']} ·"
        f" losses {bar['losses']['spent']} of a budget of {bar['losses']['budget']}"
    )
    if bar["rate_over_the_rows_the_model_answered"]:
        narrow = bar["rate_over_the_rows_the_model_answered"]
        print(f"  over answered rows: {narrow['agreed']} of {narrow['n']} = {narrow['rate']:.4f}")
    for row in bar["rows"]:
        if row["absent"]:
            print(f"    {row['msg_id']:>8}  ABSENT")
        elif row["agreed"]:
            print(f"    {row['msg_id']:>8}  agreed")
        else:
            said = ", ".join(
                f"{name}: gold {one['gold']!r} vs pass1 {one['reader']!r}"
                for name, one in sorted(row["disagreed_on"].items())
            )
            print(f"    {row['msg_id']:>8}  {said}")

    print(f"\nCENSUS  {verdict['census']['n']} rows, {verdict['census']['parsed']} parsed")
    for name, counts in verdict["census"]["per_thread"].items():
        print(f"  {name:26s} {counts}")
    print(f"  overall {verdict['census']['subject_type_distribution']}")

    print(f"\nREFUSALS {verdict['refusals']['refused']} of {verdict['refusals']['of']}")
    for shape, count in verdict["refusals"]["by_shape"].items():
        print(f"  {shape}: {count}")

    calls = verdict["per_call"]
    if calls.get("measured"):
        print(
            f"\nPER CALL {calls['seconds_per_call']:.3f} s ·"
            f" {calls['completion_tokens_per_call']:.1f} completion tokens ·"
            f" {calls['against_the_bound']:.2f}x the registered bound ·"
            f" {calls['against_the_fit']:.2f}x the fit"
        )
    price = verdict["window_pass1_price"]
    if price.get("priced"):
        print(
            f"WINDOW   {price['payable_comments']} payable comments ->"
            f" {price['seconds']:.0f} s = ${price['usd_at_the_worked_example']:.4f}"
            " of generation at the worked example (a FLOOR, no boot in it)"
        )
    print(f"\nOUTCOME {verdict['outcome']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
