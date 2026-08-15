#!/usr/bin/env python3
"""`results/reader_probe_b_w1.jsonl` + the gold → `results/reader_probe_b_verdict.json`.

The five bars, COMPUTED, through `market_pulse.scorer` and nowhere else. probe-a's scorer produced
only a SCORED/UNSCORED state, because its go/no-go stopped the run before a single bar's threads were
read; here every registered case is in the population, so this file does the arithmetic.

**A bar whose cases are not in the evidence is UNSCORED with its reason** — never a zero, and never
a number computed over whatever happened to be read. A rate over three threads says nothing about a
bar living in the other twenty.

**What it always reports, run or stop:** what was bought, what it cost, what the replies did, and
the parse outcomes BY CAUSE — «no signal» and «the reply could not be read» are two different
answers and the second one piles up exactly where the first is counted.

**The collapsed reading, beside every bar that turns on it.** 8 of the 14 per-comment gold rows and
4 of the 7 flagship signals score on `subject_type: категория`, a word the ratified entity taxonomy
does not carry and one the plan's own schema example stopped using on 2026-08-15. The bar is scored
as registered; the same bar with «категория» and «категория_личное» collapsed into one class is
reported beside it, through the SAME scorer function, so a failure on that split can be told apart
from a reading failure.

    PYTHONPATH=src python3 scripts/score_reader_probe_b.py
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_aggregates as builder  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import brands, scorer  # noqa: E402

PREREG = REPO_ROOT / "results" / "prereg_reader_probe_v2.json"
GOLD = REPO_ROOT / "results" / "reader_gold_w1.json"
EVIDENCE = REPO_ROOT / "results" / "reader_probe_b_w1.jsonl"
RUN = REPO_ROOT / "results" / "reader_probe_b_run.json"
OUT = REPO_ROOT / "results" / "reader_probe_b_verdict.json"

COLLAPSE = {"категория_личное": "категория"}
"""The one vocabulary collapse reported beside the bars — never applied to a gating number.

`категория` is in the prompt's SUBJECT list because `docs/PLAN-comment-signals.md` §3's schema
example used it (Dv388); the team lead's edit of 2026-08-15 replaced that example's word with
`категория_личное`, so the gold's 12 `категория` cells now rest on the reference alone while the
plan demonstrates the other word. A reader answering either is answering one of two words two
authorities disagree about, and that is a finding for the sitting rather than a reading error
([[a_rename_the_data_cannot_follow]])."""


def collapse(value):
    return COLLAPSE.get(value, value)


def rows() -> list[dict]:
    if not EVIDENCE.exists():
        raise SystemExit(f"{summary.rel(EVIDENCE)}: no evidence — there is nothing to score")
    return [json.loads(line) for line in EVIDENCE.read_text(encoding="utf-8").splitlines() if line]


def aliases() -> dict[str, str]:
    """The watchlist the census cell was priced with — through the same seal `build_aggregates` uses.

    Resolving a free-text name to a brand is the matcher's job, and the matcher has to be the one the
    gate ran with or bar 2 would be comparing the reader against a registry nobody censused.
    """
    prereg = json.loads(summary.read_text_or_refuse(builder.PREREG))
    registry = summary.registry_through_the_seal(prereg, builder.REGISTRY)
    return brands.watchlist_aliases(registry.watchlist)


def resolved(entities: list[dict], table: dict[str, str]) -> list[dict]:
    """Each reader entity with the brand_ids the matcher finds in its name AND its quote.

    Both fields, because duty (2) asks for the name «as it is written in the text» and the quote is
    where it was read: a reader that writes «Селянське» resolves on the name, one that writes «ТМ
    Селянське 5%» may only resolve on the quote, and either is the same finding.
    """
    out = []
    for one in entities:
        found = sorted(
            {
                hit["brand_id"]
                for field in ("name", "quote")
                for hit in brands.find_watchlist_brands(one.get(field) or "", table)
            }
        )
        out.append({**one, "brand_ids": found})
    return out


def thread_key(channel: str, post_id) -> str:
    return f"{channel}:{post_id}"


def bar_state(wanted: list[str], read: set[str]) -> dict:
    """A bar's state before any number: which of its cases the evidence actually holds."""
    missing = [one for one in wanted if one not in read]
    return {
        "scored": not missing,
        "threads_registered": wanted,
        "threads_in_the_evidence": [one for one in wanted if one in read],
        "threads_not_read": missing,
        "verdict": "UNSCORED" if missing else "SCORED",
        "reason": None
        if not missing
        else (
            "the registered threads carrying this bar's cases were not read: the go/no-go stopped"
            " the run before the population was bought. A bar computed over the threads that WERE"
            " read would be a number about another sample"
        ),
    }


def flagships(gold: dict, verdicts: dict, read: set[str], *, collapsed: bool) -> dict:
    """Bar 1 — a case is found when every gold signal it carries is found."""
    cases, signals_table = [], []
    for case in gold["flagships"]:
        name = thread_key(case["channel"], case["post_id"])
        found_signals = []
        for signal in case["signals"]:
            want = dict(signal)
            answers = (verdicts.get(name) or {}).get("signals") or []
            if collapsed:
                want["subject_type"] = collapse(want.get("subject_type"))
                answers = [
                    {**one, "subject_type": collapse(one.get("subject_type"))} for one in answers
                ]
            hit = scorer.reader_signal_found(want, answers) if name in read else {"found": False}
            found_signals.append({"id": signal["id"], **hit})
            signals_table.append({"case": case["id"], "id": signal["id"], "found": hit["found"]})
        cases.append(
            {
                "id": case["id"],
                "thread": name,
                "answered": all(one["found"] for one in found_signals),
                "signals": found_signals,
            }
        )
    return {
        "cases_answered": sum(one["answered"] for one in cases),
        "cases": len(cases),
        "passed": all(one["answered"] for one in cases),
        "per_case": cases,
        "per_signal": signals_table,
        "per_signal_reading": (
            "plan §5 (1) names five SIGNALS and the reference five THREADS carrying seven; the bar"
            " is the case reading and this table is where the narrower one is read off"
        ),
    }


def entity_cases(gold: dict, verdicts: dict, read: set[str], table: dict[str, str]) -> dict:
    """Bar 2 — through the watchlist matcher, with E4 as the ABSENCE case it is."""
    rows_out = []
    for case in gold["entity_cases"]:
        name = thread_key(case["channel"], case["post_id"])
        want = {
            "brand_id": case["brand_id"],
            "subject_type": case["subject_type"],
            **({"expected": "absent"} if case["subject_type"] is None else {}),
        }
        entities = resolved((verdicts.get(name) or {}).get("entities") or [], table)
        hit = (
            scorer.reader_entity_found(want, entities)
            if name in read
            else {"answered": False, "expected": want.get("expected") or want["subject_type"]}
        )
        rows_out.append({"id": case["id"], "thread": name, "brand_id": case["brand_id"], **hit})
    # E4 is ONE ruling about two threads: both rows must answer it for the case to be answered
    by_case = {}
    for row in rows_out:
        by_case.setdefault(row["id"].rstrip("ab") if row["id"].startswith("E4") else row["id"], [])
        by_case[row["id"].rstrip("ab") if row["id"].startswith("E4") else row["id"]].append(row)
    answered = {case: all(one["answered"] for one in group) for case, group in by_case.items()}
    return {
        "cases_answered": sum(answered.values()),
        "cases": len(answered),
        "passed": all(answered.values()),
        "per_case": answered,
        "per_row": rows_out,
    }


def noise(gold: dict, verdicts: dict, read: set[str], registered: list[str]) -> dict:
    """Bar 3 — signals only. Entities resolved in a noise thread are reported beside the number."""
    threads = {
        one["id"]: thread_key(one["channel"], one["post_id"]) for one in gold["noise_threads"]
    }
    inside = {
        threads[case]: verdicts.get(threads[case]) or {}
        for case in registered
        if threads[case] in read
    }
    counted = scorer.reader_noise_count(inside)
    beside = {
        case: scorer.reader_noise_count({threads[case]: verdicts.get(threads[case]) or {}})
        for case in threads
        if case not in registered and threads[case] in read
    }
    return {
        **counted,
        "passed": counted["signals"] == 0,
        "scored_over": registered,
        "reported_beside": {case: one["signals"] for case, one in beside.items()},
    }


def per_comment(gold: dict, verdicts: dict, read: set[str], *, collapsed: bool) -> dict:
    """Bar 4 — every gold row on the fields the reference states for it, and on no others."""
    wanted, answers = [], []
    for row in gold["per_comment"]:
        name = thread_key(row["channel"], row["evidence_row"]["post_id_in_the_store"])
        if name not in read:
            continue
        one = dict(row)
        said = [
            entry
            for entry in ((verdicts.get(name) or {}).get("per_comment") or [])
            if int(entry["msg_id"]) == int(row["msg_id"])
        ]
        if collapsed:
            one["subject_type"] = collapse(one.get("subject_type"))
            said = [
                {**entry, "subject_type": collapse(entry.get("subject_type"))} for entry in said
            ]
        wanted.append(one)
        answers += said
    if not wanted:
        return {"scored": False, "reason": "none of the gold rows' threads were read"}
    result = scorer.reader_comment_agreement(wanted, answers)
    return {**result, "passed": result["rate"] >= 0.80, "scored": True}


def build() -> dict:
    prereg = json.loads(summary.read_text_or_refuse(PREREG))
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    evidence = rows()
    run = json.loads(RUN.read_text(encoding="utf-8")) if RUN.exists() else {}
    read = {row["thread"] for row in evidence}
    verdicts = {row["thread"]: row["parsed"] for row in evidence if row["parsed"]}
    table = aliases()

    bars = prereg["bars"]
    threads_of = {
        "1_flagships": [
            thread_key(one["channel"], one["post_id"])
            for one in gold["flagships"]
            if one["id"] in bars["1_flagships"]["scored_over"]
        ],
        "2_entity_cases": [
            thread_key(one["channel"], one["post_id"])
            for one in gold["entity_cases"]
            if one["id"] in bars["2_entity_cases"]["scored_over"]
        ],
        "3_noise": [
            thread_key(one["channel"], one["post_id"])
            for one in gold["noise_threads"]
            if one["id"] in bars["3_noise"]["scored_over"]
        ],
        "4_per_comment_agreement": sorted(
            {
                thread_key(one["channel"], one["evidence_row"]["post_id_in_the_store"])
                for one in gold["per_comment"]
                if one["msg_id"] in bars["4_per_comment_agreement"]["scored_over"]
            }
        ),
    }
    states = {name: bar_state(wanted, read) for name, wanted in threads_of.items()}

    computed = {
        "1_flagships": flagships(gold, verdicts, read, collapsed=False),
        "2_entity_cases": entity_cases(gold, verdicts, read, table),
        "3_noise": noise(gold, verdicts, read, bars["3_noise"]["scored_over"]),
        "4_per_comment_agreement": per_comment(gold, verdicts, read, collapsed=False),
    }
    collapsed = {
        "1_flagships": flagships(gold, verdicts, read, collapsed=True),
        "4_per_comment_agreement": per_comment(gold, verdicts, read, collapsed=True),
    }
    for name, state in states.items():
        state["scorer"] = bars[name]["scorer"]
        state["threshold"] = bars[name]["threshold"]
        state["result"] = computed[name] if state["scored"] else None

    parsed = [row for row in evidence if row["parsed"]]
    causes = Counter(row["parse_error"] for row in evidence if row["parse_error"])
    signal_bearing = sum(1 for row in parsed if row["parsed"]["signals"])
    injected = [row for row in evidence if row.get("injected")]
    return {
        "phase": "probe-b",
        "contract": "docs/PROMPT-probe-b.md",
        "registration": {
            "record": summary.rel(PREREG),
            "sha256": summary.sha256_of(PREREG),
            "task": prereg["instruments"]["task"],
            "population_threads": prereg["population"]["threads"],
        },
        "gold": {"record": summary.rel(GOLD), "sha256": summary.sha256_of(GOLD)},
        "evidence": {
            "record": summary.rel(EVIDENCE),
            "sha256": summary.sha256_of(EVIDENCE),
            "threads_read": len(evidence),
            "threads_registered": prereg["population"]["threads"],
            "injected_read": len(injected),
        },
        "outcome": run.get("go_no_go", {}).get("verdict", "UNKNOWN"),
        "go_no_go": run.get("go_no_go"),
        "bars": states,
        "collapsed_vocabulary_reading": {
            "rule": (
                "the same two bars recomputed with «категория_личное» folded into «категория»,"
                " through the same scorer functions. REPORTED and never gating"
            ),
            "why": COLLAPSE
            and (
                "8 of the 14 per-comment gold rows and 4 of the 7 flagship signals score on"
                " «категория». The word is in the prompt because plan §3's schema example used it;"
                " that example now says «категория_личное» and the reference still says «категория»"
            ),
            "bars": {
                name: {
                    "as_registered": (
                        computed[name].get("rate")
                        if "rate" in computed[name]
                        else computed[name].get("cases_answered")
                    ),
                    "collapsed": (
                        collapsed[name].get("rate")
                        if "rate" in collapsed[name]
                        else collapsed[name].get("cases_answered")
                    ),
                }
                for name in collapsed
            },
            "detail": collapsed,
        },
        "replies": {
            "parsed": len(parsed),
            "refused": len(evidence) - len(parsed),
            "refusals_by_cause": dict(causes),
            "finish_reason_length": sum(
                1 for row in evidence if row.get("finish_reason") == "length"
            ),
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
        "injected_threads": {
            "rule": (
                "the four threads the gate removes before payment, read so bars 2 and 3 are"
                " reachable. Reported apart from every other number and never in a production"
                " aggregate or a window price"
            ),
            "read": [row["thread"] for row in injected],
            "signals": {
                row["thread"]: len((row["parsed"] or {}).get("signals") or []) for row in injected
            },
            "entities": {
                row["thread"]: len((row["parsed"] or {}).get("entities") or []) for row in injected
            },
        },
        "non_gating": {
            "completion_tokens": sum(
                int((row.get("usage") or {}).get("completion_tokens") or 0) for row in evidence
            ),
            "prompt_tokens": sum(
                int((row.get("usage") or {}).get("prompt_tokens") or 0) for row in evidence
            ),
            "worker_seconds": round(sum(row["seconds"]["worker"] for row in evidence), 3),
            "seconds_per_thread": round(
                sum(row["seconds"]["worker"] for row in evidence) / len(evidence), 3
            ),
            "gpu": ((run.get("worker") or {}).get("runtime") or {}).get("gpu_name"),
        },
        "scorer": {
            "module": "src/market_pulse/scorer.py",
            "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
            "functions": [
                name
                for name in prereg["instruments"]["scorer"]["functions"]
                if hasattr(scorer, name)
            ],
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
        print(f"  bar {name:26s} {state['verdict']}{got}")
    print(f"  replies: {record['replies']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
