#!/usr/bin/env python3
"""`results/reader_v3_w1.jsonl` + gold r2 → `results/reader_v3_verdict.json`.

The five bars of `results/prereg_reader_probe_v3.json`, COMPUTED — bars 1, 2 and 4 through
`market_pulse.scorer` and through probe-b's own scoring functions, so the paired columns are the
same arithmetic on both sides and not two readings of one word; bar 3 through the registration's own
reference implementation, imported rather than re-implemented; bar 5 from the step ledger the guard
wrote.

**Bar 3 is not re-stated here.** `write_reader_prereg_v3.bar_three_over_answers` IS the predicate,
and the registration says the run's scorer «reproduces this predicate and may not invent a second
reading of it». The strongest available form of that is to call it ([[a_registered_bar_may_have_no_
producer]] one turn later: the producer exists, so use it).

**Two things are reported beside the bars and gate nothing**, both because a reader of the result
would otherwise have to work them out:

* **bar 3's population grew from five threads to six.** v2 registered N2–N6 and excluded N1 with a
  cause — the reference's own S list reads a signal inside that thread (S1, msg 21420), so a bar
  that failed the reader for agreeing with the reference would measure nothing. v3's producer takes
  every noise id from the gold and the exclusion did not come with it. Scored as REGISTERED, over
  six, and recomputed over v2's five beside it.
* **the vocabulary collapse.** Gold r2 relabels twelve «категория» cells to «категория_личное» and
  IS the bar now, but the v3 prompt still offers both words in its signal subject list, so a reader
  answering the reference's word is scored wrong against the ratified one. The collapsed reading is
  reported beside bars 1 and 4, applied to gold and to the answers alike.

**What it always reports, run or stop:** what was bought, what it cost, what the replies did, the
refusal census BY SHAPE against probe-b's own two baselines, the repair census, `finish_reason` per
thread and the tokens-per-`per_comment`-row reading Dv433 asked for.

    PYTHONPATH=src python3 scripts/score_reader_v3.py
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import runpod_guard as guard  # noqa: E402
import score_reader_probe_b as probe_b  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_reader_prereg_v3 as prereg  # noqa: E402

from market_pulse import prompts, scorer  # noqa: E402

PHASE = "reader-v3"
PREREG = REPO_ROOT / "results" / "prereg_reader_probe_v3.json"
GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
EVIDENCE = REPO_ROOT / "results" / "reader_v3_w1.jsonl"
RUN = REPO_ROOT / "results" / "reader_v3_run.json"
LEDGER = guard.step_ledger_path(PHASE)
OUT = REPO_ROOT / "results" / "reader_v3_verdict.json"

PROBE_B_EVIDENCE = REPO_ROOT / "results" / "reader_probe_b_w1.jsonl"
PROBE_B_VERDICT = REPO_ROOT / "results" / "reader_probe_b_verdict.json"
PROBE_B_PREREG = REPO_ROOT / "results" / "prereg_reader_probe_v2.json"


def rows() -> list[dict]:
    if not EVIDENCE.exists():
        raise SystemExit(f"{summary.rel(EVIDENCE)}: no evidence — there is nothing to score")
    return [json.loads(line) for line in EVIDENCE.read_text(encoding="utf-8").splitlines() if line]


def probe_b_rows() -> list[dict]:
    return [
        json.loads(line)
        for line in PROBE_B_EVIDENCE.read_text(encoding="utf-8").splitlines()
        if line
    ]


def bar_three(gold: dict, verdicts: dict, read: set[str], registered: list[str]) -> dict:
    """Bar 3, through the registration's own producer and over the ids IT registers.

    `noise_signals` is built over every registered noise thread that was READ — a refused reply
    lands in it with a zero, and `bar_three_over_answers` is what then removes it from the count and
    names it in `threads_refused`. That split is the whole fix: a bar whose predicate is «zero of X»
    counted over an unreadable reply is a pass nobody measured.
    """
    threads = {
        one["id"]: probe_b.thread_key(one["channel"], one["post_id"])
        for one in gold["noise_threads"]
    }
    inside = {
        threads[case]: verdicts.get(threads[case]) or {}
        for case in registered
        if threads[case] in read
    }
    counted = scorer.reader_noise_count(inside)
    answered = {name for name in inside if name in verdicts}
    bar = prereg.bar_three_over_answers(counted["per_thread"], answered)
    return {
        **bar,
        "scored_over": registered,
        "threads": {case: threads[case] for case in registered},
        "entities_beside_the_number": {
            name: count for name, count in counted["entities"].items() if name in answered
        },
    }


def bar_three_over_probe_bs_five(gold: dict, verdicts: dict, read: set[str]) -> dict:
    """The same bar over the five threads v2 registered — REPORTED and never gating.

    v2's registration excluded N1 with a stated cause and v3's producer, which takes every noise id
    from the gold, did not carry the exclusion. The two bars are therefore over different
    populations, and a paired column that did not say so would be comparing two questions.
    """
    five = list(
        json.loads(PROBE_B_PREREG.read_text(encoding="utf-8"))["bars"]["3_noise"]["scored_over"]
    )
    return {
        "scored_over": five,
        "excluded_by_v2": sorted(set(prereg.bars(gold)["3_noise"]["scored_over"]) - set(five)),
        "result": bar_three(gold, verdicts, read, five),
    }


def refusal_census(evidence: list[dict]) -> dict:
    """Which shapes refused, against probe-b's TWO baselines — both derived, neither transcribed.

    probe-b's report counts «six shapes» in prose, its verdict record holds five causes over ten
    refusals, and the v3 registration names a seventh reply that only the refuse-on-conflict clause
    catches. A hand-copied table would be wrong about which shapes are new, so both baselines are
    computed: the causes probe-b's run actually recorded, and the causes its same replies produce
    under TODAY's parser — which is the one this run's refusals are comparable to.
    """
    mine = Counter(row["parse_error"] for row in evidence if row["parse_error"])
    as_run = Counter(
        json.loads(PROBE_B_VERDICT.read_text(encoding="utf-8"))["replies"]["refusals_by_cause"]
    )
    under_v3 = Counter()
    for row in probe_b_rows():
        try:
            prompts.parse_reply(row["task"], row["reply"])
        except prompts.ParseError as err:
            under_v3[err.reason] += 1
    return {
        "as_run": dict(mine),
        "refused": sum(mine.values()),
        "per_thread": {row["thread"]: row["parse_error"] for row in evidence if row["parse_error"]},
        "probe_b_as_run_under_v2": dict(as_run),
        "probe_b_replies_under_todays_parser": dict(under_v3),
        "new_against_probe_b": sorted(set(mine) - set(as_run) - set(under_v3)),
        "did_not_return": sorted(set(as_run) - set(mine)),
        "still_refusing_after_the_container_tolerance": sorted(set(mine) & set(under_v3)),
        "reading": (
            "«probe_b_replies_under_todays_parser» is probe-b's own 23 replies re-read by the v3"
            " parser — the measurement the registration published as 19 of 23, recomputed here so"
            " the comparison is between two runs of one instrument and not between a run and a"
            " sentence in a report. It moves no probe-b number: that run's verdict is"
            " results/reader_probe_b_verdict.json"
        ),
    }


def repair_census(evidence: list[dict], record: dict) -> dict:
    """Which of the three registered container repairs fired, and how often — half A's measurement.

    The registered names are read out of the registration and every one of them is reported, zero
    included: a census that listed only what fired could not say which repair was bought and never
    used.
    """
    registered = []
    for block in record["instruments"]["parser"]["repairs"].values():
        logs = block["logs"]
        registered += [logs] if isinstance(logs, str) else list(logs)
    fired = Counter(name for row in evidence for name in (row.get("repairs") or ()))
    parsed = [row for row in evidence if row["parsed"]]
    return {
        "registered": sorted(registered),
        "fired": {name: fired.get(name, 0) for name in sorted(registered)},
        "unregistered_names_that_fired": sorted(set(fired) - set(registered)),
        "threads_repaired": sorted(row["thread"] for row in parsed if row["repairs"]),
        "threads_read_straight": sum(1 for row in parsed if not row["repairs"]),
        "reading": (
            "gates nothing. A and B are ONE instrument and no ablation between them was bought, so"
            " a reply that parses here may not be attributed to the parser or to the prompt"
        ),
    }


def output_ceiling(evidence: list[dict], record: dict) -> dict:
    """Dv433's unlock — `finish_reason` per thread, and tokens per `per_comment` row, denominators
    named.

    Two denominators and they are different questions. RETURNED rows is what the tokens actually
    paid for; REQUESTED rows is what v3 asked for (one per payable comment), and a model that
    under-delivers makes the first flatter than the second. The window re-price needs the second —
    the 129-thread cell's largest thread carries 125 payable comments against a 2 000-token ceiling
    — so both are here and neither is called «the» rate.
    """
    parsed = [row for row in evidence if row["parsed"]]
    completion = sum(int((row.get("usage") or {}).get("completion_tokens") or 0) for row in parsed)
    returned = sum(len(row["parsed"]["per_comment"]) for row in parsed)
    requested = sum(row["payable_comments"] for row in parsed)
    return {
        "max_new_tokens": record["instruments"]["ceilings"]["output_tokens"],
        "finish_reason_per_thread": {row["thread"]: row.get("finish_reason") for row in evidence},
        "finish_reason_length": sum(1 for row in evidence if row.get("finish_reason") == "length"),
        "probe_b_finish_reason_length": json.loads(PROBE_B_VERDICT.read_text(encoding="utf-8"))[
            "replies"
        ]["finish_reason_length"],
        "completion_tokens_over_parsed_threads": completion,
        "per_comment_rows_returned": returned,
        "per_comment_rows_requested": requested,
        "tokens_per_returned_per_comment_row": round(completion / returned, 2)
        if returned
        else None,
        "tokens_per_requested_per_comment_row": (
            round(completion / requested, 2) if requested else None
        ),
        "rows_returned_over_rows_requested": (
            round(returned / requested, 3) if requested else None
        ),
        "window_reading": (
            "the reader census cell's largest thread carries 125 payable comments"
            " (results/gate_census_w1_reader.json). At the requested-row rate above that is what a"
            " window pass would owe in output tokens for that one thread, against the ceiling on"
            " the line above — computed here, decided nowhere: no window pass is opened by this"
            " contract"
        ),
    }


def money(record: dict, ledger_path: Path | None = None, phase: str = PHASE) -> dict:
    """Bar 5 — from the step ledger the guard wrote, in whichever of its two states it is in.

    A step ledger that has been CLOSED is priced by its closing entry's settled figure. An OPEN one
    can only report the balance delta its own entries carry, and that is a LOWER BOUND and never a
    pass: the billing walk settles hours late and the always-on volume drains into the same delta
    (Dv412). Nothing here calls RunPod — the live reading is the guard's, and its output goes in the
    report beside this record.

    The ledger and the step are parameters with THIS step's defaults so that reader-v4 can point the
    same three states at its own ledger instead of writing a second reading of them. Bar 5 is the
    one bar whose arithmetic is about the guard's file rather than about the model, and two copies
    of it would be two answers to one question.
    """
    # resolved at CALL time and not bound as a default: `LEDGER` is the module's live constant and
    # a default evaluated at import would be a constant nothing reads any more
    # ([[a_monkeypatch_is_not_a_reader]])
    ledger_path = LEDGER if ledger_path is None else ledger_path
    cap = float(record["money"]["cap_usd_all_in"])
    if not ledger_path.exists():
        return {
            "cap_usd_all_in": cap,
            "state": "NO LEDGER",
            "passed": None,
            "reason": f"{summary.rel(ledger_path)} does not exist — the step was never anchored",
        }
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    sessions = ledger.get("gpu_sessions") or []
    shut = guard.closing_entry(sessions)
    block = {
        "cap_usd_all_in": cap,
        "ledger": summary.rel(ledger_path),
        "sha256": summary.sha256_of(ledger_path),
        "anchor": ledger.get(guard.anchor_key_in(ledger, phase) or ""),
        "anchored_at": ledger.get("anchored_at"),
        "sessions": len(sessions),
    }
    if shut is not None:
        settled = float(shut["settled_usd"])
        return block | {
            "state": "CLOSED",
            "settled_usd": settled,
            "billing_by_kind": shut.get("billing_by_kind"),
            "window_start": shut.get("window_start"),
            "passed": settled <= cap,
            "reading": (
                "the step's OWN resources, the always-on network volume excluded by kind and not by"
                " arithmetic (SPEC 3.23 (4), Dv412)"
            ),
        }
    readings = [float(one["step_spent_usd"]) for one in sessions if "step_spent_usd" in one]
    return block | {
        "state": "OPEN",
        "lower_bound_usd": max(readings) if readings else None,
        "passed": None,
        "reason": (
            "the step ledger carries no closing entry, so there is no settled figure. The largest"
            " balance-delta reading its sessions hold is a LOWER BOUND — it also carries the"
            " always-on volume, which belongs to no step — and closing is a named debt for the next"
            " guard run, never a number invented here"
        ),
    }


def pairing(evidence: list[dict], bars: dict, collapsed: dict) -> dict:
    """probe-b's numbers beside this run's, on the rows that exist in both.

    Only where the row exists in both: the two runs are paired on population and on data by
    construction, and any figure that is not is named rather than aligned.
    """
    theirs = json.loads(PROBE_B_VERDICT.read_text(encoding="utf-8"))
    their_rows = {row["thread"]: row for row in probe_b_rows()}
    mine = {row["thread"]: row for row in evidence}
    both = sorted(set(mine) & set(their_rows))
    their_bars = theirs["bars"]
    return {
        "threads_in_both": len(both),
        "replies_parsed": {
            "probe_b": theirs["replies"]["parsed"],
            "reader_v3": sum(1 for row in evidence if row["parsed"]),
            "of": len(evidence),
        },
        "per_thread": {
            name: {
                "probe_b": their_rows[name]["parse_error"] or "parsed",
                "reader_v3": mine[name]["parse_error"] or "parsed",
                "probe_b_seconds": their_rows[name]["seconds"]["worker"],
                "reader_v3_seconds": mine[name]["seconds"]["worker"],
            }
            for name in both
        },
        "bars": {
            "1_flagships": {
                "probe_b": their_bars["1_flagships"]["result"]["cases_answered"],
                "reader_v3": bars["1_flagships"]["result"]
                and bars["1_flagships"]["result"]["cases_answered"],
                "of": 5,
            },
            "2_entity_cases": {
                "probe_b": their_bars["2_entity_cases"]["result"]["cases_answered"],
                "reader_v3": bars["2_entity_cases"]["result"]
                and bars["2_entity_cases"]["result"]["cases_answered"],
                "of": 4,
            },
            "3_noise": {
                "probe_b": their_bars["3_noise"]["result"]["signals"],
                "probe_b_scored_over": their_bars["3_noise"]["result"]["scored_over"],
                "reader_v3": bars["3_noise"]["result"] and bars["3_noise"]["result"]["signals"],
                "reader_v3_scored_over": bars["3_noise"]["scored_over"],
                "not_the_same_bar": (
                    "v2 registered five noise threads and v3 registers six — the paired column is"
                    " over different populations and the recomputation over v2's five is beside it"
                ),
            },
            "4_per_comment_agreement": {
                "probe_b_against_gold_v1": their_bars["4_per_comment_agreement"]["result"]["rate"],
                "probe_b_collapsed": theirs["collapsed_vocabulary_reading"]["bars"][
                    "4_per_comment_agreement"
                ]["collapsed"],
                "reader_v3_against_gold_r2": bars["4_per_comment_agreement"]["result"]
                and bars["4_per_comment_agreement"]["result"]["rate"],
                "reader_v3_collapsed": collapsed["4_per_comment_agreement"].get("rate"),
                "gold_note": (
                    "probe-b scored against gold v1 and this run against r2, which is the sitting's"
                    " ruling 4 applied to twelve cells. The two rates are not the same measurement"
                    " and the collapsed columns are what makes them comparable"
                ),
            },
        },
        "seconds": {
            "probe_b_per_thread": theirs["non_gating"]["seconds_per_thread"],
            "reader_v3_per_thread": round(
                sum(row["seconds"]["worker"] for row in evidence) / len(evidence), 3
            ),
            "probe_b_gpu": theirs["non_gating"]["gpu"],
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
        "1_flagships": probe_b.flagships(gold, verdicts, read, collapsed=False),
        "2_entity_cases": probe_b.entity_cases(gold, verdicts, read, table),
        "3_noise": bar_three(gold, verdicts, read, bars["3_noise"]["scored_over"]),
        "4_per_comment_agreement": probe_b.per_comment(gold, verdicts, read, collapsed=False),
    }
    collapsed = {
        "1_flagships": probe_b.flagships(gold, verdicts, read, collapsed=True),
        "4_per_comment_agreement": probe_b.per_comment(gold, verdicts, read, collapsed=True),
    }
    for name, state in states.items():
        state["scorer"] = bars[name]["scorer"]
        state["threshold"] = bars[name]["threshold"]
        state["result"] = computed[name] if state["scored"] else None
    states["3_noise"]["scored_over"] = bars["3_noise"]["scored_over"]

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
        "contract": "docs/PROMPT-reader-v3-run.md",
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
        "outcome": run.get("go_no_go", {}).get("verdict", "UNKNOWN"),
        "go_no_go": run.get("go_no_go"),
        "bars": states,
        "5_time_and_cost": money(record),
        "beside_the_bars": {
            "rule": "REPORTED and never gating — neither number moves a verdict above",
            "3_noise_over_v2s_five_threads": bar_three_over_probe_bs_five(gold, verdicts, read),
            "collapsed_vocabulary_reading": {
                "why": (
                    "gold r2 relabels twelve «категория» cells to «категория_личное» and IS the bar"
                    " now, but the v3 prompt still offers BOTH words in its signal subject list"
                    " (prompts.READER_SUBJECT_TYPES). Ruling 4 adjudicated them as ONE class, so a"
                    " reader answering the reference's word is scored wrong against the ratified"
                    " one — this column is what says whether that happened"
                ),
                "map": probe_b.COLLAPSE,
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
        "refusals": refusal_census(evidence),
        "repairs": repair_census(evidence, record),
        "output_ceiling": output_ceiling(evidence, record),
        "pairing": pairing(evidence, states, collapsed),
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
    cost = record["5_time_and_cost"]
    print(f"  bar 5_time_and_cost            {cost['state']} — passed {cost['passed']}")
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
