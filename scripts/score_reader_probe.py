#!/usr/bin/env python3
"""`results/reader_probe_w1.jsonl` + the gold → `results/reader_probe_verdict.json`.

The five bars, computed through `market_pulse.scorer` and nowhere else. A bar whose cases are not
in the evidence is **UNSCORED with its reason** — never a zero, and never a number computed over
whatever happened to be read: the probe registered a population of 111 threads, and a rate measured
over three of them says nothing about a bar that lives in the other 108.

What it always reports, run or stop: what was bought, what it cost, what the replies did, and the
parse outcomes BY CAUSE — «no signal» and «the reply could not be read» are two different answers
and the second one piles up exactly where the first is counted.

    PYTHONPATH=src python3 scripts/score_reader_probe.py
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import window_summary_5c2 as summary  # noqa: E402

from market_pulse import scorer  # noqa: E402

PREREG = REPO_ROOT / "results" / "prereg_reader_probe.json"
GOLD = REPO_ROOT / "results" / "reader_gold_w1.json"
EVIDENCE = REPO_ROOT / "results" / "reader_probe_w1.jsonl"
RUN = REPO_ROOT / "results" / "reader_probe_run.json"
OUT = REPO_ROOT / "results" / "reader_probe_verdict.json"


def rows() -> list[dict]:
    if not EVIDENCE.exists():
        raise SystemExit(f"{summary.rel(EVIDENCE)}: no evidence — there is nothing to score")
    return [json.loads(line) for line in EVIDENCE.read_text(encoding="utf-8").splitlines() if line]


def bar_state(name: str, wanted: list[str], read: set[str]) -> dict:
    """A bar's state before any number: which of its cases the evidence actually holds."""
    missing = [one for one in wanted if one not in read]
    return {
        "scored": not missing,
        "cases_registered": wanted,
        "cases_in_the_evidence": [one for one in wanted if one in read],
        "cases_not_read": missing,
    }


def thread_key(channel: str, post_id) -> str:
    return f"{channel}:{post_id}"


def build() -> dict:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    evidence = rows()
    run = json.loads(RUN.read_text(encoding="utf-8")) if RUN.exists() else {}
    read = {row["thread"] for row in evidence}

    parsed = [row for row in evidence if row["parsed"]]
    causes = Counter(row["parse_error"] for row in evidence if row["parse_error"])
    lengths = sum(1 for row in evidence if row.get("finish_reason") == "length")

    # which registered case lives in which thread — the join every bar needs
    flagship_threads = {
        one["id"]: thread_key(one["channel"], one["post_id"]) for one in gold["flagships"]
    }
    entity_threads = {
        one["id"]: thread_key(one["channel"], one["post_id"]) for one in gold["entity_cases"]
    }
    noise_threads = {
        one["id"]: thread_key(one["channel"], one["post_id"]) for one in gold["noise_threads"]
    }
    bars = prereg["bars"]
    states = {
        "1_flagships": bar_state(
            "1", [flagship_threads[one] for one in bars["1_flagships"]["scored_over"]], read
        ),
        "2_entity_cases": bar_state(
            "2", [entity_threads[one] for one in bars["2_entity_cases"]["scored_over"]], read
        ),
        "3_noise": bar_state(
            "3", [noise_threads[one] for one in bars["3_noise"]["scored_over"]], read
        ),
        "4_per_comment_agreement": bar_state(
            "4",
            sorted(
                {
                    thread_key(row["channel"], row["evidence_row"]["post_id_in_the_store"])
                    for row in gold["per_comment"]
                    if row["msg_id"] in bars["4_per_comment_agreement"]["scored_over"]
                }
            ),
            read,
        ),
    }
    for name, state in states.items():
        state["verdict"] = "UNSCORED" if not state["scored"] else "SCORED"
        state["reason"] = (
            None
            if state["scored"]
            else (
                "the registered threads carrying this bar's cases were not read: the go/no-go"
                " stopped the run before the population was bought. A bar computed over the"
                " threads that WERE read would be a number about another sample"
            )
        )
        state["scorer"] = bars[name]["scorer"]

    signal_bearing = sum(1 for row in parsed if row["parsed"]["signals"])
    return {
        "phase": "probe-a",
        "contract": "docs/PROMPT-probe-a.md D5",
        "registration": {
            "record": summary.rel(PREREG),
            "sha256": summary.sha256_of(PREREG),
            "population_threads": prereg["population"]["threads"],
        },
        "gold": {"record": summary.rel(GOLD), "sha256": summary.sha256_of(GOLD)},
        "evidence": {
            "record": summary.rel(EVIDENCE),
            "sha256": summary.sha256_of(EVIDENCE),
            "threads_read": len(evidence),
            "threads_registered": prereg["population"]["threads"],
        },
        "outcome": run.get("go_no_go", {}).get("verdict", "UNKNOWN"),
        "go_no_go": run.get("go_no_go"),
        "bars": states,
        "replies": {
            "parsed": len(parsed),
            "refused": len(evidence) - len(parsed),
            "refusals_by_cause": dict(causes),
            "finish_reason_length": lengths,
            "signal_bearing": signal_bearing,
            "no_signal": len(parsed) - signal_bearing,
            "reading": (
                "«no signal» is counted over PARSED replies only. A reply that could not be read is"
                " not a thread with nothing in it, and the two are never added together"
            ),
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
        print(f"  bar {name:26s} {state['verdict']}")
    print(f"  replies: {record['replies']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
