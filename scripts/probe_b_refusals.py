#!/usr/bin/env python3
"""POST-RUN ANALYSIS — which of probe-b's bar cases fell on a reply that could not be read.

**This file moves no bar.** The bars are `results/reader_probe_b_verdict.json`'s, computed by an
instrument committed before the endpoint existed, and they stay exactly as that record states them.
What is written here is the join that record cannot make and the report cannot do in prose: for
every registered case, whether its thread's reply PARSED — because a bar scored over an unreadable
reply says «the reader missed the case» when the truth is «the reply could not be read», and those
are two different answers ([[the_empty_class_eats_the_parse_failures]]).

The run made that distinction load-bearing in both directions:

- bar 3 «zero signals in the noise threads» PASSES, and four of its five threads have no verdict at
  all. A count of zero over an empty answer is not evidence of anything;
- bars 1 and 2 FAIL on cases whose threads were refused, so part of their failure is an interface
  defect rather than a reading one.

Every number below is REPORTED. The registered verdict is the one that gates.

    PYTHONPATH=src python3 scripts/probe_b_refusals.py
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import score_reader_probe_b as scoring  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

VERDICT = REPO_ROOT / "results" / "reader_probe_b_verdict.json"
OUT = REPO_ROOT / "results" / "reader_probe_b_refusals.json"


def build() -> dict:
    gold = json.loads(summary.read_text_or_refuse(scoring.GOLD))
    verdict = json.loads(summary.read_text_or_refuse(VERDICT))
    rows = {row["thread"]: row for row in scoring.rows()}
    parsed = {name for name, row in rows.items() if row["parsed"]}

    def state(thread: str) -> dict:
        row = rows[thread]
        return {
            "thread": thread,
            "parsed": bool(row["parsed"]),
            "parse_error": row["parse_error"],
            "payable_comments": row["payable_comments"],
        }

    cases = {}
    for one in gold["flagships"]:
        cases[one["id"]] = state(scoring.thread_key(one["channel"], one["post_id"]))
    for one in gold["entity_cases"]:
        cases[one["id"]] = state(scoring.thread_key(one["channel"], one["post_id"]))
    for one in gold["noise_threads"]:
        cases[one["id"]] = state(scoring.thread_key(one["channel"], one["post_id"]))

    bars = verdict["bars"]
    flagship_missed = {
        one["id"]: one["thread"]
        for one in bars["1_flagships"]["result"]["per_case"]
        if not one["answered"]
    }
    entity_missed = {
        one["id"]: one["thread"]
        for one in bars["2_entity_cases"]["result"]["per_row"]
        if not one["answered"]
    }
    noise_over = bars["3_noise"]["result"]["per_thread"]
    agreement = bars["4_per_comment_agreement"]["result"]
    per_comment_thread = {
        one["msg_id"]: scoring.thread_key(
            one["channel"], one["evidence_row"]["post_id_in_the_store"]
        )
        for one in gold["per_comment"]
    }
    return {
        "class": (
            "POST-RUN ANALYSIS, reported and never gating. Written after"
            " results/reader_probe_b_verdict.json and moving nothing in it: this is the join"
            " between a bar's cases and whether their replies could be read at all"
        ),
        "verdict": {"record": summary.rel(VERDICT), "sha256": summary.sha256_of(VERDICT)},
        "replies": {
            "read": len(rows),
            "parsed": len(parsed),
            "refused": len(rows) - len(parsed),
            "by_cause": dict(
                Counter(row["parse_error"] for row in rows.values() if row["parse_error"])
            ),
        },
        "cases_on_a_refused_reply": {name: one for name, one in cases.items() if not one["parsed"]},
        "1_flagships": {
            "missed": flagship_missed,
            "missed_on_a_refused_reply": {
                name: thread for name, thread in flagship_missed.items() if thread not in parsed
            },
            "missed_while_the_reply_parsed": {
                name: thread for name, thread in flagship_missed.items() if thread in parsed
            },
        },
        "2_entity_cases": {
            "missed": entity_missed,
            "missed_on_a_refused_reply": {
                name: thread for name, thread in entity_missed.items() if thread not in parsed
            },
            "missed_while_the_reply_parsed": {
                name: thread for name, thread in entity_missed.items() if thread in parsed
            },
        },
        "3_noise": {
            "signals": bars["3_noise"]["result"]["signals"],
            "passed": bars["3_noise"]["result"]["passed"],
            "threads_with_a_verdict": {
                thread: count for thread, count in noise_over.items() if thread in parsed
            },
            "threads_with_no_verdict": {
                thread: rows[thread]["parse_error"] for thread in noise_over if thread not in parsed
            },
            "reading": (
                "the bar counts SIGNALS, and a refused reply has none — so a thread whose verdict"
                " could not be read contributes a zero that looks exactly like a clean pass. This"
                " bar's 0 is computed over"
                f" {len([t for t in noise_over if t in parsed])} of {len(noise_over)} threads with"
                " an actual verdict"
            ),
        },
        "4_per_comment_agreement": {
            "rate": agreement["rate"],
            "n": agreement["n"],
            "agreed": agreement["agreed"],
            "disagreed": agreement["disagreed"],
            "absent": agreement["absent"],
            "absent_on_a_refused_reply": [
                row["msg_id"]
                for row in agreement["rows"]
                if row["absent"] and per_comment_thread[row["msg_id"]] not in parsed
            ],
            "absent_while_the_reply_parsed": [
                row["msg_id"]
                for row in agreement["rows"]
                if row["absent"] and per_comment_thread[row["msg_id"]] in parsed
            ],
            "disagreements": {
                row["msg_id"]: row["disagreed_on"]
                for row in agreement["rows"]
                if not row["agreed"] and not row["absent"]
            },
            "rate_over_the_rows_whose_reply_parsed": (
                agreement["agreed"]
                / max(
                    1,
                    sum(
                        1
                        for row in agreement["rows"]
                        if per_comment_thread[row["msg_id"]] in parsed
                    ),
                )
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
    print(f"  replies {record['replies']}")
    for bar in ("1_flagships", "2_entity_cases"):
        print(
            f"  {bar:16s} missed on a refused reply:"
            f" {sorted(record[bar]['missed_on_a_refused_reply'])} ·"
            f" missed while it parsed: {sorted(record[bar]['missed_while_the_reply_parsed'])}"
        )
    noise = record["3_noise"]
    print(
        f"  3_noise          passed={noise['passed']} over"
        f" {len(noise['threads_with_a_verdict'])} threads with a verdict and"
        f" {len(noise['threads_with_no_verdict'])} without"
    )
    row = record["4_per_comment_agreement"]
    print(
        f"  4_per_comment    rate {row['rate']:.4f} · absent on a refused reply"
        f" {row['absent_on_a_refused_reply']} · absent while it parsed"
        f" {row['absent_while_the_reply_parsed']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
