#!/usr/bin/env python3
"""`results/reader_v4_w1.jsonl` + gold r2 → `results/reader_v4_verdict.json`.

**The contract says «score with `scripts/score_reader_v3.py` … pointed at v4's bars», and that is
what this file does — by CALLING it.** Every census, every ceiling reading and bar 5's three ledger
states are v3's functions, imported; bars 1, 2 and 4 are probe-b's scoring functions, the same
arithmetic on both sides of every paired column; bar 3 is the registration's own producer, two
generations old and still the only reading of it. What is new here is exactly the registration's
three differences and nothing else. A second file rather than an edit, because v3's scorer is a
shipped artefact whose bytes a daily log records, and because a generation of this instrument has
never edited the one before it.

**The two differences that change a number**, both of them registered:

* **bar 3 is over FIVE threads** — v2's N2–N6, with N1 excluded by v2's own cause. v3's six-thread
  reading is recomputed BESIDE it and labelled, so the two registrations stay comparable (Dv440).
* **bars 1 and 4 are scored COLLAPSED** — «категория» ≡ «категория_личное» on both sides. That is
  the BAR now, not a column beside it; the uncollapsed reading is what gets reported beside, for
  continuity with v3 and probe-b (Dv441).

The scope of the collapse is checked against the registration rather than trusted: the bars this
file scores collapsed must be exactly `scoring_rules.vocabulary_collapse.applies_to`, and the map it
applies must be the registered map. A rule that quietly grew by one bar would be a fourth
difference.

    PYTHONPATH=src python3 scripts/score_reader_v4.py
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import runpod_guard as guard  # noqa: E402
import score_reader_probe_b as probe_b  # noqa: E402
import score_reader_v3 as v3  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

PHASE = "reader-v4"
PREREG = REPO_ROOT / "results" / "prereg_reader_probe_v4.json"
GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
EVIDENCE = REPO_ROOT / "results" / "reader_v4_w1.jsonl"
RUN = REPO_ROOT / "results" / "reader_v4_run.json"
LEDGER = guard.step_ledger_path(PHASE)
OUT = REPO_ROOT / "results" / "reader_v4_verdict.json"

V3_PREREG = REPO_ROOT / "results" / "prereg_reader_probe_v3.json"
PROBE_B_VERDICT = REPO_ROOT / "results" / "reader_probe_b_verdict.json"

COLLAPSED_BARS = ("1_flagships", "4_per_comment_agreement")
"""Which bars this file scores through the collapse. Held against the registration's own
`applies_to` before anything is computed — the code and the record are two statements of one rule
and the run is where they would part."""


def rows() -> list[dict]:
    if not EVIDENCE.exists():
        raise SystemExit(f"{summary.rel(EVIDENCE)}: no evidence — there is nothing to score")
    return [json.loads(line) for line in EVIDENCE.read_text(encoding="utf-8").splitlines() if line]


def assert_the_collapse_is_the_registered_one(record: dict) -> dict:
    """The scope and the map, checked against the record before a bar is computed."""
    rule = record["scoring_rules"]["vocabulary_collapse"]
    if tuple(rule["applies_to"]) != COLLAPSED_BARS:
        raise SystemExit(
            f"the registration applies the collapse to {rule['applies_to']} and this scorer applies"
            f" it to {list(COLLAPSED_BARS)}. One of the two moved — stop and report."
        )
    if rule["map"] != probe_b.COLLAPSE:
        raise SystemExit(
            f"the registered collapse map is {rule['map']} and score_reader_probe_b.COLLAPSE is"
            f" {probe_b.COLLAPSE}. The bar would be scored under a rule nobody registered."
        )
    return rule


def bar_three_over_v3s_six(gold: dict, verdicts: dict, read: set[str]) -> dict:
    """The same bar over the SIX threads v3 registered — reported, never gating.

    v3's producer took every noise id from the gold and lost v2's exclusion of N1 with it. The two
    bars are therefore over different populations, and a column that did not say so would be
    comparing two questions.
    """
    six = list(json.loads(V3_PREREG.read_text(encoding="utf-8"))["bars"]["3_noise"]["scored_over"])
    return {
        "scored_over": six,
        "restored_by_v4": sorted(
            set(six)
            - set(json.loads(PREREG.read_text(encoding="utf-8"))["bars"]["3_noise"]["scored_over"])
        ),
        "result": v3.bar_three(gold, verdicts, read, six),
        "reading": (
            "v3 scored the reader on N1, whose signal the reference's own S list asserts (S1, msg"
            " 21420). This column is what the v4 bar would have been under v3's registration"
        ),
    }


def pairing(evidence: list[dict], bars: dict, uncollapsed: dict) -> dict:
    """probe-b's numbers beside this run's, on the rows that exist in both.

    Only where the row exists in both, and every column that is NOT the same measurement says so.
    Three of them are not: probe-b scored bar 4 against gold v1 and this run against r2; probe-b's
    bar 1 and 4 were uncollapsed and these are the collapsed ones; probe-b's seconds are serverless
    WORKER seconds and these are a pod's generation seconds.
    """
    theirs = json.loads(PROBE_B_VERDICT.read_text(encoding="utf-8"))
    their_rows = {row["thread"]: row for row in v3.probe_b_rows()}
    mine = {row["thread"]: row for row in evidence}
    both = sorted(set(mine) & set(their_rows))
    their_bars = theirs["bars"]

    def got(name, field):
        result = bars[name]["result"]
        return result and result.get(field)

    return {
        "threads_in_both": len(both),
        "replies_parsed": {
            "probe_b": theirs["replies"]["parsed"],
            "reader_v4": sum(1 for row in evidence if row["parsed"]),
            "of": len(evidence),
        },
        "per_thread": {
            name: {
                "probe_b": their_rows[name]["parse_error"] or "parsed",
                "reader_v4": mine[name]["parse_error"] or "parsed",
                "probe_b_worker_seconds": their_rows[name]["seconds"]["worker"],
                "reader_v4_seconds": mine[name]["seconds"]["worker"],
            }
            for name in both
        },
        "bars": {
            "1_flagships": {
                "probe_b_uncollapsed": their_bars["1_flagships"]["result"]["cases_answered"],
                "probe_b_collapsed": theirs["collapsed_vocabulary_reading"]["bars"]["1_flagships"][
                    "collapsed"
                ],
                "reader_v4_collapsed": got("1_flagships", "cases_answered"),
                "reader_v4_uncollapsed": uncollapsed["1_flagships"].get("cases_answered"),
                "of": 5,
                "comparable_column": "probe_b_collapsed against reader_v4_collapsed",
            },
            "2_entity_cases": {
                "probe_b": their_bars["2_entity_cases"]["result"]["cases_answered"],
                "reader_v4": got("2_entity_cases", "cases_answered"),
                "of": 4,
                "comparable_column": "both, unchanged — the collapse does not reach this bar",
            },
            "3_noise": {
                "probe_b": their_bars["3_noise"]["result"]["signals"],
                "probe_b_scored_over": their_bars["3_noise"]["result"]["scored_over"],
                "reader_v4": got("3_noise", "signals"),
                "reader_v4_scored_over": bars["3_noise"]["scored_over"],
                "comparable_column": (
                    "both — v4 restores exactly the five threads v2 registered and probe-b was"
                    " scored on, which is what makes this the one bar-3 column that IS paired"
                ),
            },
            "4_per_comment_agreement": {
                "probe_b_against_gold_v1": their_bars["4_per_comment_agreement"]["result"]["rate"],
                "probe_b_collapsed": theirs["collapsed_vocabulary_reading"]["bars"][
                    "4_per_comment_agreement"
                ]["collapsed"],
                "reader_v4_against_gold_r2_collapsed": got("4_per_comment_agreement", "rate"),
                "reader_v4_uncollapsed": uncollapsed["4_per_comment_agreement"].get("rate"),
                "comparable_column": (
                    "probe_b_collapsed against reader_v4_against_gold_r2_collapsed, and even those"
                    " two rest on different golds — r2 moved twelve cells to the ratified word."
                    " Under the collapse that difference is closed by construction, which is the"
                    " whole reason the collapse is the bar"
                ),
            },
        },
        "seconds": {
            "probe_b_worker_per_thread": theirs["non_gating"]["seconds_per_thread"],
            "reader_v4_per_thread": round(
                sum(row["seconds"]["worker"] for row in evidence) / len(evidence), 3
            )
            if evidence
            else None,
            "probe_b_gpu": theirs["non_gating"]["gpu"],
            "not_the_same_unit": (
                "probe-b's are billed serverless worker seconds; these are a pod's generation"
                " seconds, measured around one `ReaderClient.read` call. The pod also bills for its"
                " boot and its idle, and none of that is in this column — bar 5 is where the money"
                " is, and it comes from the guard's ledger"
            ),
        },
    }


def build() -> dict:
    record = json.loads(summary.read_text_or_refuse(PREREG))
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    evidence = rows()
    run = json.loads(RUN.read_text(encoding="utf-8")) if RUN.exists() else {}
    read = {row["thread"] for row in evidence}
    verdicts = {row["thread"]: row["parsed"] for row in evidence if row["parsed"]}
    table = probe_b.aliases()
    rule = assert_the_collapse_is_the_registered_one(record)

    bars = record["bars"]
    threads_of = {
        "1_flagships": [
            probe_b.thread_key(one["channel"], one["post_id"])
            for one in gold["flagships"]
            if one["id"] in bars["1_flagships"]["scored_over"]
        ],
        "2_entity_cases": [
            probe_b.thread_key(one["channel"], one["post_id"])
            for one in gold["entity_cases"]
            if one["id"] in bars["2_entity_cases"]["scored_over"]
        ],
        "3_noise": [
            probe_b.thread_key(one["channel"], one["post_id"])
            for one in gold["noise_threads"]
            if one["id"] in bars["3_noise"]["scored_over"]
        ],
        "4_per_comment_agreement": sorted(
            {
                probe_b.thread_key(one["channel"], one["evidence_row"]["post_id_in_the_store"])
                for one in gold["per_comment"]
                if one["msg_id"] in bars["4_per_comment_agreement"]["scored_over"]
            }
        ),
    }
    states = {name: probe_b.bar_state(wanted, read) for name, wanted in threads_of.items()}

    computed = {
        "1_flagships": probe_b.flagships(gold, verdicts, read, collapsed=True),
        "2_entity_cases": probe_b.entity_cases(gold, verdicts, read, table),
        "3_noise": v3.bar_three(gold, verdicts, read, bars["3_noise"]["scored_over"]),
        "4_per_comment_agreement": probe_b.per_comment(gold, verdicts, read, collapsed=True),
    }
    uncollapsed = {
        "1_flagships": probe_b.flagships(gold, verdicts, read, collapsed=False),
        "4_per_comment_agreement": probe_b.per_comment(gold, verdicts, read, collapsed=False),
    }
    for name, state in states.items():
        state["scorer"] = bars[name]["scorer"]
        state["threshold"] = bars[name]["threshold"]
        state["collapsed"] = name in COLLAPSED_BARS
        state["result"] = computed[name] if state["scored"] else None
    states["3_noise"]["scored_over"] = bars["3_noise"]["scored_over"]
    states["3_noise"]["excluded_with_cause"] = bars["3_noise"]["excluded_with_cause"]

    missing = [
        field for field in bars["3_noise"]["result_must_carry"] if field not in computed["3_noise"]
    ]
    if missing:
        raise SystemExit(
            f"bar 3's result is missing {missing}, which the registration says it must carry."
            " The producer is scripts/write_reader_prereg_v3.py::bar_three_over_answers and this"
            " scorer calls it — a field missing here means the two have parted."
        )

    parsed = [row for row in evidence if row["parsed"]]
    signal_bearing = sum(1 for row in parsed if row["parsed"]["signals"])
    return {
        "phase": PHASE,
        "contract": "docs/PROMPT-reader-v4.md",
        "registration": {
            "record": summary.rel(PREREG),
            "sha256": summary.sha256_of(PREREG),
            "task": record["instruments"]["task"],
            "population_threads": record["population"]["threads"],
            "attempt": record["attempt"],
        },
        "gold": {
            "record": summary.rel(GOLD),
            "sha256": summary.sha256_of(GOLD),
            "revision": gold["revision"]["name"],
        },
        "evidence": {
            "record": summary.rel(EVIDENCE),
            "sha256": summary.sha256_of(EVIDENCE),
            "threads_read": len(evidence),
            "threads_registered": record["population"]["threads"],
        },
        "outcome": (run.get("go_no_go") or run.get("boot_kill") or {}).get("verdict", "UNKNOWN"),
        "pod": run.get("pod"),
        "go_no_go": run.get("go_no_go"),
        "boot_kill": run.get("boot_kill"),
        "bars": states,
        "5_time_and_cost": v3.money(record, LEDGER, PHASE),
        "scoring_rules": {
            "vocabulary_collapse": {
                "applied_to": list(COLLAPSED_BARS),
                "map": rule["map"],
                "symmetric": rule["symmetric"],
                "is_the_bar": (
                    "the numbers in `bars` above are the COLLAPSED ones. The uncollapsed reading is"
                    " under `beside_the_bars` and gates nothing — the opposite of v3, where the"
                    " collapse was the column and the reference's word was the bar"
                ),
            }
        },
        "beside_the_bars": {
            "rule": "REPORTED and never gating — no number here moves a verdict above",
            "3_noise_over_v3s_six_threads": bar_three_over_v3s_six(gold, verdicts, read),
            "uncollapsed_vocabulary_reading": {
                "why": (
                    "what bars 1 and 4 would read if «категория» and «категория_личное» were still"
                    " two classes. The gap between this and the bar IS what ruling 4 was worth"
                ),
                "bars": {
                    name: {
                        "as_the_bar_collapsed": (
                            computed[name].get("rate")
                            if "rate" in computed[name]
                            else computed[name].get("cases_answered")
                        ),
                        "uncollapsed": (
                            uncollapsed[name].get("rate")
                            if "rate" in uncollapsed[name]
                            else uncollapsed[name].get("cases_answered")
                        ),
                    }
                    for name in uncollapsed
                },
                "detail": uncollapsed,
            },
        },
        "replies": {
            "parsed": len(parsed),
            "refused": len(evidence) - len(parsed),
            "signal_bearing": signal_bearing,
            "no_signal": len(parsed) - signal_bearing,
            "from_post_signals": sum(
                1
                for row in parsed
                for signal in row["parsed"]["signals"]
                if signal.get("from_post")
            ),
            "proposed_signal_types": sorted(
                {
                    signal["signal_type"]
                    for row in parsed
                    for signal in row["parsed"]["signals"]
                    if signal.get("proposed")
                }
            ),
            "reading": (
                "«no signal» is counted over PARSED replies only. A reply that could not be read is"
                " not a thread with nothing in it, and the two are never added together"
            ),
        },
        "refusals": v3.refusal_census(evidence),
        "repairs": v3.repair_census(evidence, record),
        "output_ceiling": v3.output_ceiling(evidence, record),
        "pairing": pairing(evidence, states, uncollapsed),
        "non_gating": {
            "completion_tokens": sum(
                int((row.get("usage") or {}).get("completion_tokens") or 0) for row in evidence
            ),
            "prompt_tokens": sum(
                int((row.get("usage") or {}).get("prompt_tokens") or 0) for row in evidence
            ),
            "generation_seconds": round(sum(row["seconds"]["worker"] for row in evidence), 3),
            "seconds_per_thread": round(
                sum(row["seconds"]["worker"] for row in evidence) / len(evidence), 3
            ),
            "boot_seconds": next(
                (row["boot_seconds"] for row in evidence if row.get("boot_seconds")), None
            ),
            "card": (run.get("pod") or {}).get("card"),
            "injected_under_probe_b": {
                "rule": (
                    "probe-b's flag, carried because the population digest carries it. Under the"
                    " reader's own census cell all 23 threads are production-reachable (Dv427) —"
                    " and a probe row still never enters a production aggregate or a window price"
                ),
                "threads": sorted(row["thread"] for row in evidence if row["injected"]),
            },
        },
        "scorer": {
            "module": "src/market_pulse/scorer.py",
            "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
            "registered_sha256": record["instruments"]["scorer"]["sha256"],
            "unchanged": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "scorer.py")
            == record["instruments"]["scorer"]["sha256"],
            "functions": record["instruments"]["scorer"]["functions"],
            "bar_three_producer": "scripts/write_reader_prereg_v3.py::bar_three_over_answers",
            "borrowed": (
                "bars 1/2/4 through scripts/score_reader_probe_b.py, the censuses and bar 5 through"
                " scripts/score_reader_v3.py — the contract's «score with score_reader_v3.py,"
                " pointed at v4's bars», satisfied by calling it rather than by editing it"
            ),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    record = build()
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    print(
        f"  outcome {record['outcome']} · {record['evidence']['threads_read']} of"
        f" {record['evidence']['threads_registered']} threads read"
    )
    for name, state in record["bars"].items():
        result = state["result"]
        got = "" if result is None else f" — {result.get('passed')}"
        mark = " (collapsed)" if state["collapsed"] else ""
        print(f"  bar {name:26s} {state['verdict']}{got}{mark}")
    cost = record["5_time_and_cost"]
    print(f"  bar 5_time_and_cost            {cost['state']} — passed {cost['passed']}")
    beside = record["beside_the_bars"]
    print(f"  bar 3 over v3's six threads:   {beside['3_noise_over_v3s_six_threads']['result']}")
    print(f"  uncollapsed:                   {beside['uncollapsed_vocabulary_reading']['bars']}")
    print(
        f"  replies: {record['replies']['parsed']} parsed · {record['replies']['refused']} refused"
    )
    print(f"  refusals by shape: {record['refusals']['as_run']}")
    print(f"  repairs fired: {record['repairs']['fired']}")
    print(
        f"  finish_reason length: {record['output_ceiling']['finish_reason_length']}"
        f" · tokens per requested per_comment row:"
        f" {record['output_ceiling']['tokens_per_requested_per_comment_row']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
