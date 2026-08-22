#!/usr/bin/env python3
"""`results/pass2_signals_v1.jsonl` + the gold → `results/pass2_signals_verdict.json`.

The reader's scorer, IMPORTED over pass 2's out-file. Not a fork and not a re-implementation:
`scripts/score_reader_probe_b.py::flagships` / `::entity_cases` / `::noise` are called with pass 2's
verdicts in the same shape probe-b's had, so the bars this run reports and the bars v5b reported are
the same functions over the same gold. `src/market_pulse/scorer.py` is the single judge of all
numbers and is never forked.

**A bar whose cases pass 2 does not CALL is UNSCORED with its reason**, never a zero. The pass-2
population is the 79 threads carrying a filtered row, and that is not the reader probe's population:
E1's thread carries none and is not called, while E4's two threads — which the reader's own gate
silenced before payment — are in. `results/prereg_pass2_signals.json::reachability` registered both
before the pod and this file reports against it.

**Everything else here is the answer of the contract beside the bars** — the per-flagship scorecard
citing the pass-1 label of every row it names, the DROP table, the `subject_doubt` rate by pass-1
label, and the v5b comparison row quoted from its own sealed verdict. Report-only, captioned, and
the multiplicity of any reading over the fourteen named.

    PYTHONPATH=src python3.11 scripts/score_pass2_signals.py
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_pass2_signals as gate  # noqa: E402
import score_reader_probe_b as readerscore  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import pass2  # noqa: E402

RESULTS = REPO_ROOT / "results"
PREREG = RESULTS / "prereg_pass2_signals.json"
PACK = RESULTS / "pass2_pack.json"
GOLD = RESULTS / "reader_gold_w1_r2.json"
EVIDENCE = RESULTS / "pass2_signals_v1.jsonl"
RUN = RESULTS / "pass2_signals_run.json"
V5B = RESULTS / "reader_v5b_verdict.json"
OUT = RESULTS / "pass2_signals_verdict.json"


def read(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{summary.rel(path)}: no evidence — there is nothing to score")
    return [json.loads(one) for one in path.read_text(encoding="utf-8").splitlines() if one.strip()]


def answers(pack: dict, rows: list[dict]) -> tuple[dict, list[dict]]:
    """Every reply parsed against the UNIT it was asked about, and the refusals beside them.

    The unit is what makes strict authority checkable — the pass-1 labels a reply is held to are in
    the pack item and nowhere else — so a row whose id the pack never asked is a refusal with its
    own cause rather than a row scored against another thread's labels.
    """
    by_id = {one["id"]: one for one in pack["legs"][0]["items"]}
    parsed, refused = {}, []
    for row in rows:
        item = by_id.get(row.get("id"))
        if item is None:
            refused.append({"id": row.get("id"), "cause": "id the leg never asked", "why": ""})
            continue
        try:
            parsed[row["id"]] = pass2.parse_pass2(row["reply"], unit=item)
        except Exception as err:
            refused.append({"id": row["id"], "cause": gate.r1.cause_of(err), "why": f"{err}"})
    return parsed, refused


def scorecard(record: dict, gold: dict, verdicts: dict, seen: set[str], reach: dict) -> list[dict]:
    """Per flagship signal: found / missing, and WHY — citing the pass-1 label of the row it names.

    The «why» is the contract's own ask and it is not prose: for every gold signal the table carries
    the pass-1 label of each evidence row, whether that row is inside the filter at all, and what
    the reply said about the same evidence. A miss that is a strict-authority miss and a miss that
    is a reading miss look nothing alike here, and they used to look identical in a bar's 0.
    """
    reachable = {one["id"]: one for one in reach["flagship_signals"]}
    scored = readerscore.flagships(gold, verdicts, seen, collapsed=True)
    per_signal = {one["id"]: one for case in scored["per_case"] for one in case["signals"]}
    rows = []
    for case in gold["flagships"]:
        name = f"{case['channel']}:{case['post_id']}"
        answered = (verdicts.get(name) or {}).get("signals") or []
        for signal in case["signals"]:
            hit = per_signal[signal["id"]]
            about = reachable[signal["id"]]
            cited = [one for one in answered if set(one["evidence"]) & set(signal["evidence"])]
            rows.append(
                {
                    "id": signal["id"],
                    "case": case["id"],
                    "thread": name,
                    "thread_was_read": name in seen,
                    "found": hit["found"],
                    "gold": {
                        "signal_type": signal["signal_type"],
                        "subject_type": signal["subject_type"],
                        "aspect": signal["aspect"],
                        "evidence": signal["evidence"],
                    },
                    "pass_1_labels_of_the_cited_rows": about["pass_1_labels_of_the_cited_rows"],
                    "evidence_rows_inside_the_filter": about["evidence_rows_inside_the_filter"],
                    "registered_reachable": about["reachable"],
                    "what_pass_2_said_about_the_same_evidence": [
                        {
                            "signal_type": one["signal_type"],
                            "subject_type": one["subject_type"],
                            "aspect": one["aspect"],
                            "evidence": one["evidence"],
                        }
                        for one in cited
                    ],
                    "why": (
                        "found"
                        if hit["found"]
                        else "the thread was not read"
                        if name not in seen
                        else "UNREACHABLE by construction: no cited row carries the gold's"
                        f" subject_type under pass 1 — {about['pass_1_labels_of_the_cited_rows']}"
                        if not about["reachable"]
                        else "no signal cites any of the gold's evidence rows"
                        if not cited
                        else "a signal cites the evidence and disagrees on subject_type or aspect"
                    ),
                }
            )
    return rows


def drop_table(pack: dict, verdicts: dict) -> dict:
    """The filtered rows pass 2 sent to `noise` — the FP reading of the pass-1 filter.

    By thread and by pass-1 label, because «what did the filter get wrong» is a question about the
    LABEL and not about the count. A row dropped out of a thread pass 1 called `сеть_ритейлер` is
    the mention-vs-about confusion arriving as a measurement.
    """
    labels = {
        one["id"]: {int(row["msg_id"]): row["subject_type"] for row in one["comments"]}
        for one in pack["legs"][0]["items"]
    }
    by_label: Counter = Counter()
    by_class: Counter = Counter()
    given_by_label: Counter = Counter()
    per_thread = []
    for name, verdict in sorted(verdicts.items()):
        for msg_id, label in labels[name].items():
            given_by_label[label] += 1
        dropped = [
            {
                "msg_id": one["msg_id"],
                "pass_1_label": labels[name].get(one["msg_id"]),
                "class": one["class"],
            }
            for one in verdict["noise"]
        ]
        for one in dropped:
            by_label[one["pass_1_label"]] += 1
            by_class[one["class"]] += 1
        if dropped:
            per_thread.append({"thread": name, "dropped": len(dropped), "rows": dropped})
    total = sum(by_label.values())
    return {
        "rule": (
            "a filtered row pass 2 sent to `noise`. Pass 2 may DROP a comment and may not relabel"
            " one, so this table is the whole of what it says about the filter's false positives"
        ),
        "dropped_rows": total,
        "rows_offered": sum(given_by_label.values()),
        "drop_rate": round(total / max(1, sum(given_by_label.values())), 4),
        "by_pass_1_label": dict(sorted(by_label.items())),
        "offered_by_pass_1_label": dict(sorted(given_by_label.items())),
        "rate_by_pass_1_label": {
            label: round(by_label.get(label, 0) / count, 4)
            for label, count in sorted(given_by_label.items())
        },
        "by_noise_class": dict(sorted(by_class.items())),
        "per_thread": per_thread,
    }


def doubt_table(pack: dict, verdicts: dict) -> dict:
    """`subject_doubt` by pass-1 label — the FP/FN reading ruling (б) asked for.

    Report-only by construction: the field changes nothing downstream, and that is what makes it an
    honest reading of disagreement rather than a relabelling wearing a different name.
    """
    labels = {
        one["id"]: {int(row["msg_id"]): row["subject_type"] for row in one["comments"]}
        for one in pack["legs"][0]["items"]
    }
    doubted: Counter = Counter()
    kept: Counter = Counter()
    examples = defaultdict(list)
    for name, verdict in sorted(verdicts.items()):
        for one in verdict["per_comment"]:
            label = labels[name].get(one["msg_id"])
            kept[label] += 1
            if one.get("subject_doubt"):
                doubted[label] += 1
                if len(examples[label]) < 10:
                    examples[label].append(
                        {"thread": name, "msg_id": one["msg_id"], "note": one.get("note")}
                    )
    return {
        "rule": (
            "one row per comment pass 2 kept, with the pass-1 label it was given. REPORT-ONLY: a"
            " doubt changes nothing downstream and pass 2 has no authority to act on it"
        ),
        "kept_rows": sum(kept.values()),
        "doubted_rows": sum(doubted.values()),
        "rate": round(sum(doubted.values()) / max(1, sum(kept.values())), 4),
        "by_pass_1_label": {
            label: {
                "kept": count,
                "doubted": doubted.get(label, 0),
                "rate": round(doubted.get(label, 0) / count, 4),
            }
            for label, count in sorted(kept.items())
        },
        "examples": {label: rows for label, rows in sorted(examples.items())},
    }


def accounting(verdicts: dict) -> dict:
    """Every given comment in exactly one of the two lists — counted, never refused.

    The reader's own parser calls a comment in both lists a bookkeeping slip whose two rows are each
    readable, and this file does not overrule it. A comment in NEITHER is the other half of the same
    question and it is what would make the DROP table's denominator wrong if it were not counted.
    """
    both, neither, given, kept, dropped = [], [], 0, 0, 0
    for name, verdict in sorted(verdicts.items()):
        acct = verdict["accounting"]
        given += len(acct["given"])
        kept += len(acct["kept"])
        dropped += len(acct["dropped"])
        both += [f"{name}#{one}" for one in acct["in_both_lists"]]
        neither += [f"{name}#{one}" for one in acct["in_neither_list"]]
    return {
        "rows_given": given,
        "rows_kept": kept,
        "rows_dropped": dropped,
        "rows_in_both_lists": both,
        "rows_in_neither_list": neither,
        "accounted_for": given - len(neither),
        "rule": (
            "the prompt says every comment appears exactly once, in `per_comment` or in `noise`."
            " A breach is COUNTED and not refused: refusing a whole thread's signals over an"
            " incomplete list would trade the measurement for the bookkeeping"
        ),
    }


def threads_of(gold: dict, key: str, cases: list[str]) -> list[str]:
    """The threads a bar's registered cases live in — the input `bar_state` needs."""
    return sorted(
        {
            f"{one['channel']}:{one['post_id']}"
            for one in gold[key]
            if one["id"].rstrip("ab") in cases or one["id"] in cases
        }
    )


def bar_states(
    record: dict,
    gold: dict,
    verdicts: dict,
    seen: set[str],
    attempted: set[str] | None = None,
    refused_threads: dict[str, str] | None = None,
) -> dict:
    """The three bars, each with its reachability named beside its number.

    **Every bar goes through `readerscore.bar_state` first**, and that is not decoration. Under a
    STOP at rung S′ only the five F threads are read, and the two failure modes are opposite and
    both silent: `scorer.reader_noise_count({})` returns `signals: 0`, so bar 3 would report GREEN
    over zero threads read, while `entity_cases` would report 0 of 4 against a registration that
    says 3 of 4. A bar whose cases are not in the evidence is UNSCORED with its reason — never a
    zero and never a pass ([[a_checker_whose_failure_is_silence]]).
    """
    registered = record["bars"]
    reach = record["reachability"]
    table = readerscore.aliases()
    wanted = {
        "1_flagships": threads_of(gold, "flagships", registered["1_flagships"]["scored_over"]),
        "2_entity_cases": threads_of(
            gold, "entity_cases", registered["2_entity_cases"]["scored_over"]
        ),
        "3_noise": threads_of(gold, "noise_threads", registered["3_noise"]["scored_over"]),
    }
    # a case whose thread the POPULATION never carried is a registered reachability fact and not a
    # thread this run failed to read: it is named in the record and excluded from the readable set
    unreachable = set(reach["unreachable_entity_cases"])
    wanted["2_entity_cases"] = [
        one
        for one in wanted["2_entity_cases"]
        if one not in {row["thread"] for row in reach["entity_cases"] if row["id"] in unreachable}
    ]
    # a thread whose reply was ANSWERED and REFUSED is not a thread that was never read, and the
    # two must not share a state: the shipped reason says «the go/no-go stopped the run before the
    # population was bought», which is false about a unit the pod answered. A bar cannot be reported
    # off a reply nobody could read either — so it is UNSCORED with the REFUSAL as its cause
    # ([[the_empty_class_eats_the_parse_failures]], [[an_empty_field_hides_several_states]])
    attempted = seen if attempted is None else attempted
    refused_threads = refused_threads or {}
    state = {}
    for name, threads in wanted.items():
        one = readerscore.bar_state(threads, attempted)
        unreadable = [thread for thread in threads if thread in refused_threads]
        if unreadable and one["scored"]:
            one = {
                **one,
                "scored": False,
                "verdict": "UNSCORED",
                "threads_answered_and_refused": unreadable,
                "reason": (
                    "the pod ANSWERED these threads and the parser refused the replies —"
                    f" {', '.join(f'{thread} ({refused_threads[thread]})' for thread in unreadable)}."
                    " That is not a thread nobody read and it is not a number: this bar cannot be"
                    " reported off a reply nobody could read, and a REFUSAL is its own finding"
                ),
            }
        one.setdefault("threads_answered_and_refused", [])
        state[name] = one
    one = readerscore.flagships(gold, verdicts, seen, collapsed=False)
    one_collapsed = readerscore.flagships(gold, verdicts, seen, collapsed=True)
    two = readerscore.entity_cases(gold, verdicts, seen, table)
    three = readerscore.noise(gold, verdicts, seen, registered["3_noise"]["scored_over"])
    computed = {
        "1_flagships": {
            "threshold": registered["1_flagships"]["threshold"],
            "scorer": registered["1_flagships"]["scorer"],
            "as_registered": one,
            "collapsed": one_collapsed,
            "quoted": "collapsed — the reading v5b's own verdict quotes",
            "passed": one_collapsed["passed"],
            "expectation": registered["1_flagships"]["expectation"],
            "unreachable_signals": reach["unreachable_flagship_signals"],
            "reading": (
                "the bar is 5 of 5 and it was registered knowing F2 could not be taken. What the"
                " number says is what the signal layer AS BUILT reaches, and the scorecard beside"
                " it says why each miss is a miss"
            ),
        },
        "2_entity_cases": {
            "threshold": registered["2_entity_cases"]["threshold"],
            "scorer": registered["2_entity_cases"]["scorer"],
            "result": two,
            "passed": two["passed"],
            "registered_before_the_pod": registered["2_entity_cases"]["computed"],
            "agrees_with_the_registration": two["cases_answered"]
            == registered["2_entity_cases"]["computed"]["cases_answered"],
            "reading": (
                "INHERITED. The `entities` list is the bought v5b/v4/topup block passed through, so"
                " this number was computable at $0 and is registered as such. It is reported as"
                " «held» and is never pass 2's own"
            ),
            "unreachable_cases": reach["unreachable_entity_cases"],
        },
        "3_noise": {
            "threshold": registered["3_noise"]["threshold"],
            "scorer": registered["3_noise"]["scorer"],
            "result": three,
            "passed": three["passed"],
            "scored_over": registered["3_noise"]["scored_over"],
            "excluded_with_cause": registered["3_noise"]["excluded_with_cause"],
            "not_called": registered["3_noise"]["not_called"],
            "the_case_this_bar_is_really_about": registered["3_noise"][
                "the_case_this_bar_is_really_about"
            ],
            "under_a_STOP": registered["3_noise"]["under_a_STOP"],
        },
    }
    return {
        name: {
            **bar,
            "scored": state[name]["scored"],
            "verdict": state[name]["verdict"],
            "threads_registered": state[name]["threads_registered"],
            "threads_not_read": state[name]["threads_not_read"],
            "unscored_reason": state[name]["reason"],
            "threads_answered_and_refused": state[name]["threads_answered_and_refused"],
            # a bar whose cases were not read has NO result — not a zero and not a pass
            **(
                {} if state[name]["scored"] else {"passed": None, "result": None, "collapsed": None}
            ),
        }
        for name, bar in computed.items()
    }


def build() -> dict:
    record = json.loads(summary.read_text_or_refuse(PREREG))
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    pack = json.loads(summary.read_text_or_refuse(PACK))
    rows = read(EVIDENCE)
    state = json.loads(RUN.read_text(encoding="utf-8")) if RUN.exists() else {}
    v5b = json.loads(summary.read_text_or_refuse(V5B))

    by_id = {one["id"]: one for one in pack["legs"][0]["items"]}
    parsed, refused = answers(pack, rows)
    seen = set(parsed)
    causes = Counter(one["cause"] for one in refused)
    go = [one for one in state.get("gates", []) if one.get("kind") == gate.GO_KIND]
    arm = "GO" if any(one.get("verdict") == "GO" for one in go) else "STOP"
    units = len(pack["legs"][0]["items"])
    smoke = int(pack["smoke"]["units"])

    signals = [one for verdict in parsed.values() for one in verdict["signals"]]
    return {
        "phase": "pass2-signals",
        "contract": "docs/PROMPT-pass2-signals.md D2",
        "registration": {
            "record": summary.rel(PREREG),
            "sha256": summary.sha256_of(PREREG),
            "task": record["instruments"]["task"],
            "population_units": record["population"]["units"],
        },
        "gold": {"record": summary.rel(GOLD), "sha256": summary.sha256_of(GOLD)},
        "evidence": {
            "record": summary.rel(EVIDENCE),
            "sha256": summary.sha256_of(EVIDENCE),
            "units_read": len(rows),
            "units_registered": units,
            "units_authorised": smoke if arm == "STOP" else units,
            "arm": arm,
            "arm_rule": record["bars"]["completeness"]["arm_rule"],
        },
        "go_no_go": go[-1] if go else None,
        "bars": bar_states(
            record,
            gold,
            parsed,
            seen,
            attempted={one["id"] for one in rows if one.get("id") in by_id} | seen,
            refused_threads={one["id"]: one["cause"] for one in refused if one["id"] in by_id},
        ),
        "scorecard": scorecard(record, gold, parsed, seen, record["reachability"]),
        "drop_table": drop_table(pack, parsed),
        "subject_doubt": doubt_table(pack, parsed),
        "accounting": accounting(parsed),
        "replies": {
            "parsed": len(parsed),
            "refused": len(refused),
            "refusals_by_cause": dict(sorted(causes.items())),
            "relabellings": sum(
                count for cause, count in causes.items() if "RelabelError" in cause
            ),
            "refusal_rows": refused[:20],
            "signals": len(signals),
            "signal_bearing_units": sum(1 for one in parsed.values() if one["signals"]),
            "no_signal_units": sum(1 for one in parsed.values() if not one["signals"]),
            "signal_types": dict(sorted(Counter(one["signal_type"] for one in signals).items())),
            "proposed_signal_types": sorted(
                {one["signal_type"] for one in signals if one.get("proposed")}
            ),
            "subject_types": dict(sorted(Counter(one["subject_type"] for one in signals).items())),
            "repairs": dict(
                sorted(
                    Counter(
                        one for verdict in parsed.values() for one in verdict["repairs"]
                    ).items()
                )
            ),
            "reading": (
                "«no signal» is counted over PARSED replies only. A reply that could not be read is"
                " not a thread with nothing in it, and the two are never added together"
                " ([[the_empty_class_eats_the_parse_failures]])"
            ),
        },
        "the_v5b_comparison_row": {
            "record": summary.rel(V5B),
            "sha256": summary.sha256_of(V5B),
            "v5b_bar_1_collapsed": v5b["bars"]["1_flagships"]["result"]["cases_answered"],
            "v5b_bar_2": v5b["bars"]["2_entity_cases"]["result"]["cases_answered"],
            "v5b_threads_read": v5b["evidence"]["leg_a_read"],
            "v5b_cost_usd": v5b["5_time_and_cost"]["settled_usd"],
            "v5b_seconds_per_thread": v5b["non_gating"]["leg_a_seconds_per_thread"],
            "rule": record["bars"]["report_only"]["the_v5b_comparison_row"]["rule"],
        },
        "cost": {
            "pass_1_over_the_window_usd": 0.742055,
            "this_step_usd": round(
                sum(float(one.get("billed_usd") or 0) for one in state.get("pods", [])), 6
            ),
            "this_step_billed_seconds": round(
                sum(float(one.get("billed_seconds") or 0) for one in state.get("pods", [])), 1
            ),
            "cap_usd": record["money"]["cap_usd_all_in"],
            "the_one_shot_reader_usd": v5b["5_time_and_cost"]["settled_usd"],
            "rule": (
                "the gate's CLOCK — create-elapsed × the pod's own price. The billing walk lags and"
                " is reconciled in the report, never quoted as the step's number"
            ),
        },
        "non_gating": {
            "seconds_per_unit": round(
                sum(float(one["seconds"]) for one in rows) / max(1, len(rows)), 3
            ),
            "seconds_max": round(max((float(one["seconds"]) for one in rows), default=0.0), 3),
            "completion_tokens": sum(
                int((one.get("usage") or {}).get("completion_tokens") or 0) for one in rows
            ),
            "emitted_chars_max": max(
                (int(one.get("emitted_chars") or 0) for one in rows), default=0
            ),
            "finish_reason_length": sum(1 for one in rows if one.get("finish_reason") == "length"),
            "replies_that_never_closed_their_object": sum(
                1 for one in rows if one.get("balanced") is False
            ),
            "reading": (
                "the FIRST measurement of a pass-2 decode this stack owns. It is the number the"
                " next registration prices from, and it is a property of THIS pod"
                " ([[a_rate_is_a_property_of_the_pod]])"
            ),
        },
        "what_this_is_not": record["what_this_run_is_not"],
        "scorer": {
            "module": "src/market_pulse/scorer.py",
            "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
            "bar_scorer": "scripts/score_reader_probe_b.py, IMPORTED",
            "functions": record["instruments"]["scorer"]["functions"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    verdict = build()
    args.out.write_text(
        json.dumps(verdict, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    print(
        f"  arm {verdict['evidence']['arm']} ·"
        f" {verdict['evidence']['units_read']} of {verdict['evidence']['units_authorised']}"
        f" authorised units read · {verdict['replies']['parsed']} parsed ·"
        f" {verdict['replies']['refused']} refused"
        f" ({verdict['replies']['relabellings']} relabellings)"
    )
    for name, bar in verdict["bars"].items():
        got = bar.get("collapsed") or bar.get("result")
        if got is None:
            print(f"  bar {name:16s} UNSCORED — {bar['threads_not_read']} not read")
            continue
        print(
            f"  bar {name:16s} {'GO ' if bar['passed'] else 'RED'} — "
            + (
                f"{got['cases_answered']} of {got['cases']}"
                if "cases" in got
                else f"{got['signals']} signals out of {got['threads']} noise threads"
            )
        )
    drops = verdict["drop_table"]
    print(
        f"  DROP: {drops['dropped_rows']} of {drops['rows_offered']} filtered rows"
        f" ({drops['drop_rate']:.1%}) · by label {drops['by_pass_1_label']}"
    )
    doubt = verdict["subject_doubt"]
    print(f"  subject_doubt: {doubt['doubted_rows']} of {doubt['kept_rows']} ({doubt['rate']:.1%})")
    print(
        f"  vs v5b: bar-1 {verdict['the_v5b_comparison_row']['v5b_bar_1_collapsed']}/5 · bar-2"
        f" {verdict['the_v5b_comparison_row']['v5b_bar_2']}/4 · ${verdict['cost']['the_one_shot_reader_usd']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
