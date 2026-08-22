#!/usr/bin/env python3.11
"""`results/pass2_signals_r2_verdict.json` — the reader's own scorer over pass 2's whole population.

D2 of `docs/PROMPT-pass2-signals-r2.md`. The bars, the scorecard, the DROP table, the
`subject_doubt` rate and the accounting are r1's — IMPORTED from `scripts/score_pass2_signals.py`
as the pure functions they are, not copied, so a change to one of them cannot leave the other
behind ([[a_moved_constant_fails_green]]).

**What r2 does not import is the entry point.** r1's `build()` reads `pack["smoke"]["units"]` and
picks its arm off the recorded go/no-go, and r2 has neither: one arm, no smoke leg, 79 units. And
r1's `answers()` binds `market_pulse.pass2.parse_pass2`. **Re-binding that module global would break
r1's scorer for the rest of the process** — its own tests re-parse r1's out-file and expect the
refusal that is r1's record — so the parser is bound HERE and r1's module is left exactly as it is
([[rewriting_a_record_resets_state_you_do_not_own]]).

**Two counts and never one.** 79 rows are SCORED; 75 of them were bought by this pod and 4 are
carried from r1's. Every bar reads all 79. Every rate, every second and every dollar reads the 75.

    PYTHONPATH=src python3.11 scripts/score_pass2_signals_r2.py
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_pass2_signals_r2 as gate  # noqa: E402
import score_pass2_signals as r1score  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import pass2_r2  # noqa: E402

RESULTS = REPO_ROOT / "results"
PREREG = RESULTS / "prereg_pass2_signals_r2.json"
PACK = RESULTS / "pass2_r2_pack.json"
GOLD = RESULTS / "reader_gold_w1_r2.json"
EVIDENCE = RESULTS / "pass2_signals_r2_v1.jsonl"
RUN = RESULTS / "pass2_signals_r2_run.json"
V5B = RESULTS / "reader_v5b_verdict.json"
R1_VERDICT = RESULTS / "pass2_signals_verdict.json"

OUT = RESULTS / "pass2_signals_r2_verdict.json"


def read(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{summary.rel(path)}: no evidence — there is nothing to score")
    return [json.loads(one) for one in path.read_text(encoding="utf-8").splitlines() if one.strip()]


def answers(pack: dict, rows: list[dict]) -> tuple[dict, list[dict], list[dict], list[dict]]:
    """Every reply parsed against the UNIT it was asked about — r2's parser, r1's rule.

    The unit is what makes strict authority checkable: the pass-1 labels a reply is held to are in
    the pack item and nowhere else. The third return is the census of report-only fields the
    tolerant reader could not read, which in r1 did not exist because the first one refused a
    thread.
    """
    by_id = {one["id"]: one for one in pack["legs"][0]["items"]}
    parsed, refused, unreadable, overwritten = {}, [], [], []
    for row in rows:
        item = by_id.get(row.get("id"))
        if item is None:
            refused.append({"id": row.get("id"), "cause": "id the leg never asked", "why": ""})
            continue
        try:
            verdict = pass2_r2.parse_pass2(row["reply"], unit=item)
        except Exception as err:
            refused.append({"id": row["id"], "cause": gate.window.cause_of(err), "why": f"{err}"})
            continue
        parsed[row["id"]] = verdict
        for one in verdict["unreadable_fields"]:
            unreadable.append({"id": row["id"], **one})
        for one in verdict["overwritten_fields"]:
            overwritten.append({"id": row["id"], **one})
    return parsed, refused, unreadable, overwritten


def unreadable_table(rows: list[dict], carried_rows: set[str], rule: str) -> dict:
    """A census of fields, by field and by thread. `carried_rows` is keyed on `carried_from`."""
    return {
        "rows": len(rows),
        "threads": len({one["id"] for one in rows}),
        "by_field": dict(sorted(Counter(one["field"] for one in rows).items())),
        "by_thread": dict(sorted(Counter(one["id"] for one in rows).items())),
        "on_carried_rows": sum(1 for one in rows if one["id"] in carried_rows),
        "on_carried_rows_rule": (
            "counted on the row's own `carried_from` field and never on the pack's id list — the"
            " same key every other census in this file uses, so a thread the pod RE-BOUGHT cannot"
            " be attributed to r1 in one table and to this pod in the next"
        ),
        "sample": rows[:40],
        "rule": rule,
    }


UNREADABLE_RULE = (
    "each of these would have refused its whole thread under r1's parser. `per_comment.note` did"
    " exactly that to F2 and cost bar 1 its hardest case; the rest are the same class caught before"
    " it could fire. A field here is READ and RECORDED, never a refusal. **Only fields the pinned"
    " validator REFUSED are in it** — a field this parser overwrote for its own reasons is in"
    " `overwritten_report_only_fields`, because «what could the reader not read» and «what did the"
    " reader write» are two questions and one list would answer neither"
)

OVERWRITTEN_RULE = (
    "a field this parser CHANGED, with the value the MODEL wrote beside it. Today there is exactly"
    " one: `signals.proposed` is forced True so an unreadable `signal_type` can pass the pinned"
    " domain check, and a reply that said `false` would otherwise be published as having proposed a"
    " sixth signal type. It is NOT counted as unreadable — the model answered it fine"
)


def rate_table(rows: list[dict], record: dict) -> dict:
    """This pod's seconds — over the rows it BOUGHT, beside r1's smoke as the RECORD states it.

    **r1's smoke was FIVE calls and only FOUR are carried.** `@matusi_ukr:22303` was refused by r1's
    parser at 15.801 s — the fastest of the five — so it is OWED and r2 re-buys it. The first
    version averaged the carried rows and published 53.027 s where the registration, the contract
    and r1's own report all say 45.582: a fifth value for one input, on the very line D2 exists to
    print. The smoke is quoted from `money.arithmetic.seconds_per_call.smoke`, which H6 re-derives
    from `results/pass2_signals_v1.jsonl` with that file's sha pinned beside it
    ([[two_values_for_one_input_get_quoted_kindly]], [[trace_the_producer_not_the_result]]).

    And «this pod's rows» is the `carried_from` FIELD and never the pack's id list — a thread the
    pod re-bought because the seed never landed carries no such field and must count as bought.
    """
    mine = [one for one in rows if not one.get("carried_from")]
    seconds = [float(one["seconds"]) for one in mine if one.get("seconds") is not None]
    (leg_name,) = record["money"]["arithmetic"]["calls"]
    smoke = record["money"]["arithmetic"]["seconds_per_call"]["smoke"]
    paired = record["population"]["re_asked_after_a_refusal"]
    charged = float(record["money"]["arithmetic"]["seconds_per_call"][leg_name])
    return {
        "units_bought": len(mine),
        "seconds_per_unit_mean": round(sum(seconds) / max(1, len(seconds)), 3),
        "seconds_per_unit_max": round(max(seconds, default=0.0), 3),
        "seconds_per_unit_min": round(min(seconds, default=0.0), 3),
        "generation_seconds": round(sum(seconds), 1),
        "charged_seconds_per_call": charged,
        "charged_generation_seconds": round(charged * len(mine), 1),
        "ratio_measured_over_charged": round((sum(seconds) / max(1, len(seconds))) / charged, 4),
        "r1_smoke_seconds": list(smoke["seconds"]),
        "r1_smoke_mean": smoke["mean"],
        "r1_smoke_max": smoke["max"],
        "r1_smoke_units": len(smoke["seconds"]),
        "r1_smoke_per_thread": smoke["per_thread"],
        "r1_smoke_source": smoke["record"],
        "the_one_paired_thread": {
            "id": paired,
            "r1_seconds": smoke["per_thread"].get(paired),
            "this_pod_seconds": next(
                (float(one["seconds"]) for one in mine if one["id"] == paired), None
            ),
            "rule": (
                "the ONE thread both pods answered: r1's parser refused its reply, so r2 re-buys"
                " it. Same request, same bytes, greedy decoding — this is the only reading in the"
                " run that prices the POD CLASS directly instead of inferring it from a mean over"
                " different threads ([[a_rate_is_a_property_of_the_pod]])"
            ),
        },
        "the_two_means_are_over_different_threads": (
            "the smoke's five carry 6.0 filtered rows a thread and the 75 carry 3.44, so a ratio of"
            " the two means is part pod and part composition. `completion_tokens` is beside both"
            " for the reader who wants the size-free reading; the paired thread above is the"
            " size-free one"
        ),
        "r1_smoke_rule": (
            "quoted from the registration, which H6 re-derives from that file. It is FIVE calls;"
            " only four are carried, because the fifth was refused by r1's parser and r2 re-buys"
            " it. Averaging the carried rows would publish 53.027 for a smoke the record, the"
            " contract and r1's report all state at 45.582"
        ),
        "the_carried_rows_are_excluded": (
            "their seconds were spent on pod 9rquj8p0lelct3 in r1's session, and «this pod's rows»"
            " is the `carried_from` field and never the pack's id list. A mean over all 79 would be"
            " a rate no pod ever ran at ([[a_rate_is_a_property_of_the_pod]])"
        ),
        "completion_tokens": sum(
            int((one.get("usage") or {}).get("completion_tokens") or 0) for one in mine
        ),
        "emitted_chars_max": max((int(one.get("emitted_chars") or 0) for one in mine), default=0),
        "finish_reason_length": sum(1 for one in mine if one.get("finish_reason") == "length"),
        "replies_that_never_closed_their_object": sum(
            1 for one in mine if one.get("balanced") is False
        ),
    }


def build() -> dict:
    record = json.loads(summary.read_text_or_refuse(PREREG))
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    pack = json.loads(summary.read_text_or_refuse(PACK))
    rows = read(EVIDENCE)
    state = json.loads(RUN.read_text(encoding="utf-8")) if RUN.exists() else {}
    v5b = json.loads(summary.read_text_or_refuse(V5B))
    carried = set(pack["carried"]["ids"])
    carried_rows = {one["id"] for one in rows if one.get("carried_from")}

    by_id = {one["id"]: one for one in pack["legs"][0]["items"]}
    parsed, refused, unreadable, overwritten = answers(pack, rows)
    seen = set(parsed)
    causes = Counter(one["cause"] for one in refused)
    units = len(pack["legs"][0]["items"])
    signals = [one for verdict in parsed.values() for one in verdict["signals"]]

    return {
        "phase": "pass2-signals-r2",
        "contract": "docs/PROMPT-pass2-signals-r2.md D2",
        "registration": {
            "record": summary.rel(PREREG),
            "sha256": summary.sha256_of(PREREG),
            "task": record["instruments"]["task"],
            "population_units": record["population"]["units"],
            "supersedes": record["supersedes"]["record"],
        },
        "gold": {"record": summary.rel(GOLD), "sha256": summary.sha256_of(GOLD)},
        "evidence": {
            "record": summary.rel(EVIDENCE),
            "sha256": summary.sha256_of(EVIDENCE),
            "units_read": len(rows),
            "units_registered": units,
            "units_bought_by_this_pod": len([one for one in rows if not one.get("carried_from")]),
            "units_carried_from_r1": len([one for one in rows if one.get("carried_from")]),
            "carried_ids": sorted(one["id"] for one in rows if one.get("carried_from")),
            "carried_ids_the_pack_names": sorted(carried),
            "carried_disagreement": sorted(
                carried ^ {one["id"] for one in rows if one.get("carried_from")}
            ),
            "carried_rule": pack["carried"]["rule"],
            "carried_is_keyed_on_the_field": (
                "the row's own `carried_from`, never the pack's id list. A thread the pod re-bought"
                " because the seed never landed carries no such field, and keyed on the list it"
                " would be reported as carried — hiding the one thing the contract forbids"
            ),
            "arm": "GO",
            "arm_rule": record["bars"]["completeness"]["arm_rule"],
        },
        "bars": r1score.bar_states(
            record,
            gold,
            parsed,
            seen,
            attempted={one["id"] for one in rows if one.get("id") in by_id} | seen,
            refused_threads={one["id"]: one["cause"] for one in refused if one["id"] in by_id},
        ),
        "scorecard": r1score.scorecard(record, gold, parsed, seen, record["reachability"]),
        "drop_table": r1score.drop_table(pack, parsed),
        "subject_doubt": r1score.doubt_table(pack, parsed),
        "accounting": r1score.accounting(parsed),
        "unreadable_report_only_fields": unreadable_table(
            unreadable, carried_rows, UNREADABLE_RULE
        ),
        "overwritten_report_only_fields": unreadable_table(
            overwritten, carried_rows, OVERWRITTEN_RULE
        ),
        "replies": {
            "parsed": len(parsed),
            "refused": len(refused),
            "refusals_by_cause": dict(sorted(causes.items())),
            "relabellings": sum(
                count for cause, count in causes.items() if "RelabelError" in cause
            ),
            "refusal_rows": refused[:20],
            "refusal_set_is_closed": list(pass2_r2.REFUSALS),
            "signals": len(signals),
            "signal_bearing_units": sum(1 for one in parsed.values() if one["signals"]),
            "no_signal_units": sum(1 for one in parsed.values() if not one["signals"]),
            "signal_types": dict(sorted(Counter(one["signal_type"] for one in signals).items())),
            "proposed_signal_types": sorted(
                {
                    one["signal_type"]
                    for one in signals
                    # `proposed` is forced True by the parser to carry an UNREADABLE word past the
                    # pinned domain check, so a sentinel here is this parser's flag and not the
                    # model's. Publishing it would assert a sixth signal type a reply may have
                    # explicitly denied — see `overwritten_report_only_fields` for who said what
                    if one.get("proposed") and one["signal_type"] != pass2_r2.UNREADABLE
                }
            ),
            "signal_types_the_parser_could_not_read": sum(
                1 for one in signals if one["signal_type"] == pass2_r2.UNREADABLE
            ),
            "subject_types": dict(sorted(Counter(one["subject_type"] for one in signals).items())),
            "per_comment_subject_omitted": sum(
                len(one["per_comment_subject_omitted"]) for one in parsed.values()
            ),
            "vocabulary_synonyms_used": sorted(
                {word for one in parsed.values() for word in one["vocabulary_synonyms_used"]}
            ),
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
            "pass_1_over_the_window_usd": round(
                record["money"]["step_sum"]["the_signal_layer_so_far_usd"]
                - record["money"]["step_sum"]["r1_on_the_clock_usd"],
                6,
            ),
            "pass_2_r1_usd": record["money"]["step_sum"]["r1_on_the_clock_usd"],
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
        "non_gating": rate_table(rows, record),
        "what_this_is_not": record["what_this_run_is_not"],
        "scorer": {
            "module": "src/market_pulse/scorer.py",
            "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
            "bar_scorer": "scripts/score_reader_probe_b.py, IMPORTED",
            "tables": "scripts/score_pass2_signals.py, IMPORTED — r1's own, unmoved",
            "parser": "market_pulse.pass2_r2.parse_pass2",
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
        f"  {verdict['evidence']['units_read']} of {verdict['evidence']['units_registered']} read"
        f" ({verdict['evidence']['units_bought_by_this_pod']} bought,"
        f" {verdict['evidence']['units_carried_from_r1']} carried) ·"
        f" {verdict['replies']['parsed']} parsed · {verdict['replies']['refused']} refused"
        f" ({verdict['replies']['relabellings']} relabellings) ·"
        f" {verdict['unreadable_report_only_fields']['rows']} unreadable report-only fields"
    )
    for name, bar in verdict["bars"].items():
        got = bar.get("collapsed") or bar.get("result")
        if got is None:
            print(f"  bar {name:16s} UNSCORED — {bar['threads_not_read']} not read")
            continue
        print(
            f"  bar {name:16s} {'GO ' if bar['passed'] else 'RED'} — "
            + (
                f"{got['cases_answered']} of {got['cases']} cases"
                if "cases" in got
                else f"{got.get('signals')} signals over {got.get('threads')} threads"
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
