#!/usr/bin/env python3
"""`results/reader_v5_w1.jsonl` + gold r2 → `results/reader_v5_verdict.json`.

**Bars 1-4 are v4's arithmetic, called and not re-implemented.** `score_reader_probe_b.flagships`,
`.entity_cases` and `.per_comment` under the symmetric collapse, `write_reader_prereg_v3
.bar_three_over_answers` for bar 3, `score_reader_v3.money` for bar 5 — the same functions probe-b,
reader-v3 and reader-v4 reported through, so every paired column is one arithmetic on both sides.
A generation of this instrument has never edited the one before it (Dv451) and this one does not
either.

**What is new is exactly the registration's two additions.**

* **The completeness census** — per leg-A thread: rows requested, answered in `per_comment`,
  answered in `noise`, in BOTH lists, and the absent ids NAMED. Reported beside the bars and gating
  none of them. Three states and not two, because reader-v4's 93-of-111 line is not a shortfall:
  its other 18 ids are in `noise` and the union covers 111 of 111
  ([[count_the_kind_not_the_rows]]).
* **Leg B's four MECHANICAL bars** — m1 the payable ids exactly once, m2 every chunk finished, m3
  every chunk parsed, m4 no duplicate signal survived the merge. None of them reads gold, and leg
  B's rows are excluded from every bar of leg A by construction rather than by hope.

    PYTHONPATH=src python3.11 scripts/score_reader_v5.py
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
import score_reader_v4 as v4  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import reader_v5  # noqa: E402

PHASE = "reader-v5"
PREREG = REPO_ROOT / "results" / "prereg_reader_probe_v5.json"
GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
EVIDENCE = REPO_ROOT / "results" / "reader_v5_w1.jsonl"
RUN = REPO_ROOT / "results" / "reader_v5_run.json"
LEDGER = guard.step_ledger_path(PHASE)
OUT = REPO_ROOT / "results" / "reader_v5_verdict.json"

COLLAPSED_BARS = v4.COLLAPSED_BARS
"""Which bars are scored through the vocabulary collapse — v4's tuple, imported. Two copies of a
registered scope are two scopes, and the run is where they would part."""


def rows() -> list[dict]:
    if not EVIDENCE.exists():
        raise SystemExit(f"{summary.rel(EVIDENCE)}: no evidence — there is nothing to score")
    return [json.loads(line) for line in EVIDENCE.read_text(encoding="utf-8").splitlines() if line]


def completeness(evidence: list[dict]) -> dict:
    """The three-state census over leg A — reported, never gating.

    A census that printed «93 of 111» again would re-publish the misreading it exists to correct:
    the states are answered in `per_comment`, answered in `noise`, and ABSENT, and only the third
    is a shortfall. `in_both_lists` is counted apart again, because its cause is different — the
    prompt's «at most one of the two» broken, which the parser deliberately does not refuse.
    """
    per_thread = {}
    for row in evidence:
        if row["leg"] != "A" or not row.get("echo"):
            continue
        echo = row["echo"]
        per_thread[row["thread"]] = {
            "requested": echo["requested"],
            "in_per_comment": len(echo["in_per_comment"]),
            "in_noise": len(echo["in_noise"]),
            "in_both_lists": echo["in_both_lists"],
            "absent": echo["absent"],
            "extra": echo["extra"],
            "in_list_order": echo["in_list_order"],
        }
    totals = {
        name: sum(one[name] for one in per_thread.values())
        for name in ("requested", "in_per_comment", "in_noise")
    }
    absent = {name: one["absent"] for name, one in per_thread.items() if one["absent"]}
    return {
        "rule": "REPORTED and never gating — no number here moves a bar",
        "threads_censused": len(per_thread),
        "totals": totals
        | {
            "covered": totals["in_per_comment"] + totals["in_noise"],
            "absent": sum(len(one["absent"]) for one in per_thread.values()),
            "extra": sum(len(one["extra"]) for one in per_thread.values()),
            "in_both_lists": sum(len(one["in_both_lists"]) for one in per_thread.values()),
        },
        "absent_ids_by_thread": absent,
        "threads_out_of_list_order": sorted(
            name for name, one in per_thread.items() if not one["in_list_order"]
        ),
        "per_thread": per_thread,
        "v4_baseline": {
            "per_comment_rows_requested": 111,
            "per_comment_rows_returned": 93,
            "answered_only_in_noise": 18,
            "in_both_lists": 3,
            "absent": 0,
            "reading": (
                "over reader-v4's 19 parsed threads the union covered 111 of 111 with nothing"
                " absent, so the number to watch here is `absent` and the per_comment/noise SPLIT —"
                " not a 93-of-111 ratio, which is a statement about the split and not about"
                " completeness"
            ),
        },
    }


def leg_b(evidence: list[dict], record: dict) -> dict:
    """The four mechanical bars, computed over leg B's chunks and their merge."""
    registered = record["population"]["leg_b"]
    chunks = sorted(
        (row for row in evidence if row["leg"] == "B" and row["part"]),
        key=lambda row: row["part"][0],
    )
    merged = next((row for row in evidence if row["leg"] == "B" and row["part"] is None), None)
    verdict = (merged or {}).get("parsed")
    echo = (merged or {}).get("echo") or {}
    keys = (
        []
        if verdict is None
        else [tuple(one.get(field) for field in reader_v5.SIGNAL_KEY) for one in verdict["signals"]]
    )
    # «no duplicate ACROSS PARTS» is the registered rule, so `duplicated` (one id twice in the same
    # list) is what gates and `in_both_lists` is REPORTED beside it. The second is the prompt's «at
    # most one of the two» broken, which the parser tolerates by design and reader-v4 did on 3 of
    # 111 ids with no chunking in sight ([[an_absolute_bar_needs_a_reachability_state]])
    m1 = bool(echo) and not echo["absent"] and not echo["extra"] and not echo["duplicated"]
    return {
        "thread": registered["thread"],
        "chunks_registered": registered["chunks"],
        "chunks_answered": [row["payable_comments"] for row in chunks],
        "merge_error": (merged or {}).get("merge_error"),
        "m1_every_payable_id_exactly_once": {
            "requested": echo.get("requested"),
            "covered": echo.get("covered"),
            "absent": echo.get("absent"),
            "extra": echo.get("extra"),
            "duplicated": echo.get("duplicated"),
            "in_both_lists": echo.get("in_both_lists"),
            "in_both_lists_gates_nothing": (
                "the prompt's «at most one of per_comment and noise» broken, not a chunking defect."
                " reader-v4's baseline on unchunked threads is 3 of 111"
            ),
            "merge_error": (merged or {}).get("merge_error"),
            "passed": (
                m1
                and echo.get("covered") == registered["payable_comments"]
                and (merged or {}).get("merge_error") is None
            ),
        },
        "m2_every_chunk_finished": {
            "finish_reason": {row["id"]: row.get("finish_reason") for row in chunks},
            "balanced": {row["id"]: row.get("balanced") for row in chunks},
            "passed": bool(chunks)
            and len(chunks) == len(registered["chunks"])
            and all(row.get("finish_reason") == "stop" for row in chunks),
        },
        "m3_every_chunk_parses": {
            "refusals": {row["id"]: row["parse_error"] for row in chunks if row.get("parse_error")},
            "passed": bool(chunks)
            and len(chunks) == len(registered["chunks"])
            and all(row["parsed"] for row in chunks),
        },
        "m4_the_merge_has_no_duplicate_signal": {
            "signals": len(keys),
            "distinct_keys": len(set(keys)),
            "dedupe_key": list(reader_v5.SIGNAL_KEY),
            "passed": verdict is not None and len(keys) == len(set(keys)),
        },
        "cannot_touch_leg_a": registered["class"],
    }


def build() -> dict:
    record = json.loads(summary.read_text_or_refuse(PREREG))
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    evidence = rows()
    run = json.loads(RUN.read_text(encoding="utf-8")) if RUN.exists() else {}
    leg_a_rows = [row for row in evidence if row["leg"] == "A"]
    read = {row["thread"] for row in leg_a_rows}
    verdicts = {row["thread"]: row["parsed"] for row in leg_a_rows if row["parsed"]}
    table = probe_b.aliases()
    rule = v4.assert_the_collapse_is_the_registered_one(record)

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
        )

    parsed = [row for row in leg_a_rows if row["parsed"]]
    return {
        "phase": PHASE,
        "contract": "docs/PROMPT-reader-v5-prep.md",
        "registration": {
            "record": summary.rel(PREREG),
            "sha256": summary.sha256_of(PREREG),
            "task": record["instruments"]["task"],
            "leg_a_threads": record["population"]["leg_a"]["threads"],
            "leg_b_chunks": record["population"]["leg_b"]["chunks"],
            "attempt": record["attempt"],
            "programme_stop_rule": record["programme_stop_rule"],
        },
        "gold": {
            "record": summary.rel(GOLD),
            "sha256": summary.sha256_of(GOLD),
            "revision": gold["revision"]["name"],
        },
        "evidence": {
            "record": summary.rel(EVIDENCE),
            "sha256": summary.sha256_of(EVIDENCE),
            "leg_a_read": len(leg_a_rows),
            "leg_a_registered": record["population"]["leg_a"]["threads"],
            "leg_b_units": sum(1 for row in evidence if row["leg"] == "B" and row["part"]),
        },
        "outcome": (run.get("latest") or {}).get("verdict", "UNKNOWN"),
        "pod": run.get("pod"),
        "gates": run.get("gates"),
        "bars": states,
        "5_time_and_cost": v3.money(record, LEDGER, PHASE),
        "leg_b_mechanical": leg_b(evidence, record),
        "completeness": completeness(evidence),
        "scoring_rules": {
            "vocabulary_collapse": {
                "applied_to": list(COLLAPSED_BARS),
                "map": rule["map"],
                "symmetric": rule["symmetric"],
                "is_the_bar": (
                    "the numbers in `bars` above are the COLLAPSED ones; the uncollapsed reading is"
                    " under `beside_the_bars` and gates nothing"
                ),
            }
        },
        "beside_the_bars": {
            "rule": "REPORTED and never gating — no number here moves a verdict above",
            "uncollapsed_vocabulary_reading": {
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
            "transport_stop": {
                "rule": (
                    "what the first-balanced-object stop actually removed, per unit. It is the"
                    " measurement ruling (b) was bought for and it gates nothing"
                ),
                "units_cut": sorted(row["id"] for row in evidence if row.get("cut_chars")),
                "chars_cut": sum(int(row.get("cut_chars") or 0) for row in evidence),
                "never_balanced": sorted(
                    row["id"] for row in evidence if row.get("balanced") is False
                ),
            },
        },
        "replies": {
            "parsed": len(parsed),
            "refused": len(leg_a_rows) - len(parsed),
            "reading": (
                "over LEG A only. Leg B's chunks are counted in `leg_b_mechanical` and never added"
                " to a leg-A count — they are a different population and a different question"
            ),
        },
        "refusals": v3.refusal_census(leg_a_rows),
        "repairs": v3.repair_census(leg_a_rows, record),
        "output_ceiling": v3.output_ceiling(leg_a_rows, record),
        "non_gating": {
            "completion_tokens": sum(
                int((row.get("usage") or {}).get("completion_tokens") or 0) for row in evidence
            ),
            "generation_seconds": round(
                sum(
                    row["seconds"]["worker"]
                    for row in evidence
                    if row["part"] is not None or row["leg"] == "A"
                ),
                3,
            ),
            "leg_a_seconds_per_thread": round(
                sum(row["seconds"]["worker"] for row in leg_a_rows) / len(leg_a_rows), 3
            )
            if leg_a_rows
            else None,
            "v4_seconds_per_thread": 39.461,
            "card": (run.get("pod") or {}).get("card"),
        },
        "scorer": {
            "module": "src/market_pulse/scorer.py",
            "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
            "registered_sha256": record["instruments"]["scorer"]["sha256"],
            "unchanged": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "scorer.py")
            == record["instruments"]["scorer"]["sha256"],
            "borrowed": (
                "bars 1/2/4 through scripts/score_reader_probe_b.py, bar 3 through"
                " scripts/write_reader_prereg_v3.py::bar_three_over_answers, the censuses and bar 5"
                " through scripts/score_reader_v3.py, the collapse scope through"
                " scripts/score_reader_v4.py — every one of them CALLED, none of them edited"
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
        f"  outcome {record['outcome']} · leg A {record['evidence']['leg_a_read']} of"
        f" {record['evidence']['leg_a_registered']} · leg B"
        f" {record['evidence']['leg_b_units']} chunks"
    )
    for name, state in record["bars"].items():
        result = state["result"]
        got = "" if result is None else f" — {result.get('passed')}"
        mark = " (collapsed)" if state["collapsed"] else ""
        print(f"  bar {name:26s} {state['verdict']}{got}{mark}")
    cost = record["5_time_and_cost"]
    print(f"  bar 5_time_and_cost            {cost['state']} — passed {cost['passed']}")
    mechanical = record["leg_b_mechanical"]
    # the four bars are the entries that CARRY a verdict, not the entries whose name starts with «m»:
    # `merge_error` does too, and on the first run that ever produced leg-B evidence it is None and
    # this line was a TypeError — after the verdict file had been written, which is the only reason it
    # cost nothing ([[a_consumer_list_is_not_a_meaning_list]])
    for name, state in sorted(mechanical.items()):
        if isinstance(state, dict) and "passed" in state:
            print(f"  leg B {name:38s} {state['passed']}")
    totals = record["completeness"]["totals"]
    print(
        f"  completeness: {totals['covered']} of {totals['requested']} covered ·"
        f" {totals['in_per_comment']} per_comment · {totals['in_noise']} noise ·"
        f" {totals['absent']} ABSENT · {totals['in_both_lists']} in both"
    )
    if record["completeness"]["absent_ids_by_thread"]:
        print(f"  absent ids: {record['completeness']['absent_ids_by_thread']}")
    stop = record["beside_the_bars"]["transport_stop"]
    print(f"  transport stop: {len(stop['units_cut'])} units cut, {stop['chars_cut']} chars")
    print(f"  uncollapsed: {record['beside_the_bars']['uncollapsed_vocabulary_reading']['bars']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
