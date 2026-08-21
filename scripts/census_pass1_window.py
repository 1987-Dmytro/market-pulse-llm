#!/usr/bin/env python3
"""`results/pass1_window_census.json` — D2, at $0, from the out-file the paid session bought.

**What this is for.** `docs/PROMPT-pass1-window.md` D2, in its own four parts: the completeness bar,
the label distribution and the per-thread table that PRICES `pass2-signals`, the report-only
readings, and the spans measured beside what was charged.

**The bar is not recomputed here.** `scripts/gate_pass1_window.py::completeness` is the instrument
rung 7 recorded its verdict with, and it is CALLED — a second implementation of a bar is a second
bar nobody diffed. What this file adds is everything the bar deliberately does not look at.

**Every reading below the bar is a CENSUS ROW and none of them is a bar.** They are captioned so in
the record and the reason is in `results/prereg_pass1_window.json::return_to_the_operator`: the
fourteen gold rows are the FOURTH look at the same rows, and a reading taken on rows this program
has looked at three times cannot be promoted to a verdict on v2. The same holds for the 650 labelled
rows and the 450 outside dev-200 — bigger samples, still readings.

**Two comparisons, and they are the ones the registration names.** The labelled rows go through
`gate_pass1_fewshot.py::leg_table` — the function D2's clause names — handed a view carrying
`bars.report_only.our_readings` under the key it reads, because this contract has no dev gate. The
fourteen cannot go through it at all: they are GOLD and not labels, and no gold pair is in the map
`leg_table` scores against. They go through `scorer.reader_comment_agreement` with
`probe_b.collapse`, which is what `score_pass1_probe.py::bar_p1` computes BEFORE its threshold arm —
and the threshold arm is exactly what may not exist here.

    PYTHONPATH=src python3.11 scripts/census_pass1_window.py
    PYTHONPATH=src python3.11 scripts/census_pass1_window.py --out /tmp/again.json   # the pair
"""

import argparse
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_pass1_fewshot as r2gate  # noqa: E402
import gate_pass1_window as gate  # noqa: E402
import score_reader_probe_b as probe_b  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import prompts, scorer  # noqa: E402

OUT = REPO_ROOT / "results" / "pass1_window_census.json"
GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
RESULTS = REPO_ROOT / "results"

OURS = ("категория_личное", "молочный_бренд", "сеть_ритейлер")
"""The pass-2 FILTER, from the operator's ruling (г): «комменты, которые проход-1 пометил
«наши»/`сеть_ритейлер`». Wider than the dev gate's two «our» readings by `сеть_ритейлер`, and that
is the ruling's own wording — the two sets are different questions and are counted apart below."""


def answers(pack: dict, where: Path) -> tuple[dict[str, dict], list[dict]]:
    """Every reply parsed against the unit it was asked about, and the refusals beside them."""
    leg = pack["legs"][0]
    by_id = {one["id"]: one for one in leg["items"]}
    parsed, refused = {}, []
    for row in gate.rows_of(where / leg["out"]):
        item = by_id.get(row.get("id"))
        if item is None:
            continue
        try:
            answer = prompts.parse_pass1(row["reply"], msg_id=int(item["msg_id"]))
        except Exception as err:
            refused.append({"id": row["id"], "cause": gate.cause_of(err)})
            continue
        parsed[row["id"]] = answer
    return parsed, refused


def subset(pack: dict, ids: set[str]) -> dict:
    leg = pack["legs"][0]
    return {**pack, "legs": [{**leg, "items": [one for one in leg["items"] if one["id"] in ids]}]}


def labelled_reading(record: dict, pack: dict, where: Path, ids: set[str], caption: str) -> dict:
    """One report-only reading over labelled rows, through `leg_table` and nothing else.

    The out-file is FILTERED to the subset before `leg_table` reads it, because its `answers_of`
    refuses any row the leg it was handed never asked — a guard that is right for a gate reading one
    leg's own file and wrong for a census taking three overlapping readings out of one. The rows are
    not touched: what is written to the scratch copy is the same lines, selected.
    """
    view = {
        **record,
        "bars": {
            **record["bars"],
            "dev_gate": {"our_readings": record["bars"]["report_only"]["our_readings"]},
        },
    }
    cut = subset(pack, ids)
    name = cut["legs"][0]["out"]
    with tempfile.TemporaryDirectory() as scratch:
        scratch = Path(scratch)
        (scratch / name).write_text(
            "".join(
                line + "\n"
                for line in summary.read_text_or_refuse(where / name).splitlines()
                if line.strip() and json.loads(line).get("id") in ids
            ),
            encoding="utf-8",
        )
        table = r2gate.leg_table(view, cut, pack["legs"][0]["name"], scratch)
    scored = table["n"] - table["absent"]
    return {
        "caption": caption,
        "not_a_bar": True,
        "n": table["n"],
        "agreed": table["agreed"],
        "rate": table["rate"],
        "our_n": table["our_n"],
        "our_agreed": table["our_agreed"],
        "refused": len(table["refused"]),
        "absent": table["absent"],
        "rows_the_pod_actually_answered": scored,
        "rate_over_the_rows_answered": round(table["agreed"] / scored, 6) if scored else None,
        "denominator_rule": (
            "TWO rates, because the pod was killed at rung 4 with most of the population never"
            f" asked. `rate` is over the {table['n']} rows this reading was registered over and"
            f" counts the {table['absent']} unasked ones as disagreements;"
            " `rate_over_the_rows_answered` is over the"
            f" {scored} rows that have a reply. Neither is comparable to a reading taken on a"
            " complete run, and the first is not comparable to anything at all"
            " ([[measure_on_the_rows_the_gate_scores]]). `our_agreed` / `our_n` carries the SAME"
            " absence: `our_n` is the registered count of «our» rows in this subset and"
            " `our_agreed` counts only the ones with a reply, so the pair is a floor and never a"
            " rate"
        ),
        "per_class": table["per_class"],
        "instrument": "gate_pass1_fewshot.py::leg_table — the function D2's clause names",
    }


def the_fourteen(record: dict, parsed: dict[str, dict]) -> dict:
    """The gold rows' agreement — the comparison and the collapse, and NOT the threshold arm."""
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    by_id = {int(row["msg_id"]): row for row in gold["per_comment"]}
    wanted, said, rows = [], [], []
    for one in record["population"]["gold"]["rows"]:
        msg_id = int(one["msg_id"])
        want = probe_b.collapse(by_id[msg_id].get("subject_type"))
        wanted.append({"msg_id": msg_id, "subject_type": want, "scored_fields": ["subject_type"]})
        row_id = f"{one['thread']}#{msg_id}"
        answer = parsed.get(row_id)
        got = None if answer is None else probe_b.collapse(answer.get("subject_type"))
        if answer is not None:
            said.append({"msg_id": msg_id, "subject_type": got})
        # «v2 said null» and «the pod never reached this row» are DIFFERENT states and a single
        # `None` column would read as the first while meaning the second on nine of these fourteen
        rows.append(
            {
                "id": row_id,
                "gold": want,
                "v2": got,
                "state": "answered" if answer is not None else "UNANSWERED — never reached",
                "agreed": bool(answer is not None and got == want),
            }
        )
    result = scorer.reader_comment_agreement(wanted, said)
    reached = [one for one in rows if one["state"] == "answered"]
    return {
        "rows_the_pod_actually_reached": len(reached),
        "agreed_among_those": sum(1 for one in reached if one["agreed"]),
        "denominator_rule": (
            f"the pod reached {len(reached)} of these fourteen before rung 4 killed it. `agreed`"
            f" below is over all 14 and counts the {result['absent']} it never reached as"
            " disagreements; `agreed_among_those` is over the rows that have a reply. NEITHER is"
            " comparable to the base's 9/14 or arm A's 9/14, which were taken on complete runs —"
            " and neither is a bar"
        ),
        "caption": (
            "the fourteen — A CENSUS ROW AND NEVER A BAR. This is the FOURTH look at these same"
            " rows: the base (pass1-probe-b, 9/14), arm A of the LoRA line (lora-b, 9/14), v2"
            " registered for a shot it never fired, and now v2 inside a production pass registered"
            " for transport. It cannot be promoted to «v2 takes N of 14» by this report, by the"
            " acceptance or by the next registration — a bar on the fourteen needs a NEW"
            " registration with its own attempt, its own threshold and the operator's word"
        ),
        "not_a_bar": True,
        "multiplicity": 4,
        "n": result["n"],
        "agreed": result["agreed"],
        "disagreed": result["disagreed"],
        "absent": result["absent"],
        "rate": round(result["rate"], 6),
        "rows": rows,
        "instrument": {
            "comparison": "market_pulse.scorer.reader_comment_agreement",
            "collapse": "score_reader_probe_b.py::collapse",
            "why_not_bar_p1": (
                "bar_p1 is the same comparison plus a THRESHOLD arm — `passed`, `minimum_agreed`,"
                " a loss budget. That arm is exactly what may not exist on this row"
            ),
            "why_not_leg_table": "leg_table scores against the LABEL map, and 0 of 14 gold pairs are in it",
        },
    }


def state_of(item: dict, parsed: dict, refused_ids: set) -> str:
    if item["id"] in parsed:
        return str(parsed[item["id"]].get("subject_type"))
    return "REFUSED" if item["id"] in refused_ids else "UNANSWERED"


def pass_2_filter(pack: dict, parsed: dict[str, dict], refused_ids: set, threads: int) -> dict:
    """What prices `pass2-signals`: per thread, the rows pass 1 marked and what they weigh."""
    by_thread: dict[str, dict] = {}
    sizes = {one["thread"]: one for one in pack["per_thread"]}
    for item in pack["legs"][0]["items"]:
        answer = parsed.get(item["id"])
        label = None if answer is None else answer.get("subject_type")
        cell = by_thread.setdefault(
            item["thread"],
            {
                "thread": item["thread"],
                "payable_comments": 0,
                "filtered_rows": 0,
                "filtered_chars": 0,
                "unreadable": 0,
                "unanswered": 0,
                "by_label": Counter(),
                "entity_block_chars": sizes[item["thread"]]["entity_block_chars"],
                "entities": sizes[item["thread"]]["entities"],
                "topic_chars": sizes[item["thread"]]["topic_chars"],
            },
        )
        cell["payable_comments"] += 1
        cell["by_label"][state_of(item, parsed, refused_ids)] += 1
        if item["id"] in refused_ids:
            cell["unreadable"] += 1
        elif answer is None:
            cell["unanswered"] += 1
        elif label in OURS:
            cell["filtered_rows"] += 1
            cell["filtered_chars"] += len(item["text"])

    table = []
    for cell in by_thread.values():
        table.append({**cell, "by_label": dict(sorted(cell["by_label"].items()))})
    table.sort(key=lambda one: (-one["filtered_rows"], one["thread"]))
    with_rows = [one for one in table if one["filtered_rows"]]
    return {
        "rule": (
            "pass 2 is ONE call per THREAD over the rows pass 1 labelled"
            f" {' / '.join(OURS)} — the operator's ruling (г). This table is that call's input,"
            " per thread, and it is what `pass2-signals` prices its own registration from"
        ),
        "filter": list(OURS),
        "threads_in_the_cell": threads,
        "threads_carrying_a_payable_comment": len(table),
        "why_two_denominators": (
            f"{threads - len(table)} threads of the cell carry no payable comment at all, so they"
            " produce no pass-1 request and pass 2 has nothing to call over them. The cell's count"
            " and the callable count are different questions"
        ),
        "threads_with_at_least_one_filtered_row": len(with_rows),
        "threads_pass_2_would_not_call": len(table) - len(with_rows),
        "filtered_rows_total": sum(one["filtered_rows"] for one in table),
        "filtered_chars_total": sum(one["filtered_chars"] for one in table),
        "entity_block_chars_total": sum(one["entity_block_chars"] for one in with_rows),
        "widest_thread_filtered_rows": max((one["filtered_rows"] for one in table), default=0),
        "widest_thread_filtered_chars": max((one["filtered_chars"] for one in table), default=0),
        "what_this_does_NOT_price": (
            "the per-call cost. These are the chars of a PASS-1 rendering; pass 2's prompt does not"
            " exist yet and will not render them the same way. This table sizes the input and"
            " `pass2-signals` prices its own call on its own renderer"
            " ([[the_smokes_rate_carries_the_smokes_transport]])"
        ),
        "per_thread": table,
    }


def spans(record: dict, state: dict, pack: dict, where: Path) -> dict:
    """What the pod actually did, beside what the registration charged for it."""
    rows = gate.rows_of(where / pack["legs"][0]["out"])
    seconds = [float(one["seconds"]) for one in rows if one.get("seconds") is not None]
    boots = {float(one["boot_seconds"]) for one in rows if one.get("boot_seconds") is not None}
    gates = {one["kind"]: one for one in state.get("gates", [])}
    pod = state["pods"][-1]
    sums = record["money"]["arithmetic"]
    first_reply = min(
        (float(one["elapsed_since_start"]) for one in rows if one.get("elapsed_since_start")),
        default=None,
    )
    return {
        "pod": pod["pod_id"],
        "card": pod.get("card"),
        "usd_per_hour": pod.get("usd_per_hour"),
        "created_at": pod["created_at"],
        "deleted_at": pod.get("deleted_at"),
        "billed_seconds": pod.get("billed_seconds"),
        "billed_usd": pod.get("billed_usd"),
        "measured": {
            "ssh_publish_seconds": gates.get("gate0", {}).get("elapsed_on_this_pod_seconds"),
            "launched_at": pod.get("launched_at"),
            "model_load_seconds": sorted(boots),
            "launch_to_first_reply_seconds": first_reply,
            "first_reply_at_create_elapsed_seconds": gates.get("boot", {}).get(
                "first_reply_at_create_elapsed_seconds"
            ),
            "seconds_per_call_mean": round(sum(seconds) / len(seconds), 6) if seconds else None,
            "seconds_per_call_slowest": max(seconds) if seconds else None,
            "seconds_per_call_fastest": min(seconds) if seconds else None,
            "generation_seconds": round(sum(seconds), 1) if seconds else None,
            "watch_polls": len([one for one in state.get("gates", []) if one["kind"] == "watch"]),
            "watched_seconds": gates.get("watch", {}).get("watched_seconds"),
        },
        "charged": {
            "ssh_seconds": sums["ssh_seconds_charged"],
            "stage_launch_seconds": sums["stage_launch_seconds_charged"],
            "model_load_seconds": sums["boot_seconds_charged"],
            "pre_generation_seconds": sums["pre_generation_seconds"],
            "seconds_per_call": sums["seconds_per_call"]["v2"],
            "generation_seconds": sums["generation_seconds"],
            "overhead_seconds": sums["overhead_seconds"],
            "total_seconds": sums["total_seconds"],
            "worst_case_usd_at_the_price_ceiling": sums["worst_case_usd_at_the_price_ceiling"],
        },
        "rung_4_which_world_the_pod_was_in": {
            "rule": (
                "the knife edge depends on the pre-generation, and the record carries two values"
                " for it. This is the one the pod measured"
            ),
            **{
                key: value
                for key, value in sums["cumulative"]["projection_gate"][
                    "single_call_sensitivity"
                ].items()
                if key
                in (
                    "sustained_rate_the_charged_pre_generation_can_pay_for",
                    "slowest_call_in_the_sample",
                )
            },
        },
    }


def build() -> dict:
    record = gate.registration()
    state = json.loads(summary.read_text_or_refuse(gate.RECORD))
    pack = json.loads(summary.read_text_or_refuse(gate.PACK))
    where = RESULTS

    parsed, refused = answers(pack, where)
    bar = gate.completeness(record, state, pack, where)

    membership = pack["membership"]
    labelled = set(membership["labelled_650"]["ids"])
    dev = set(membership["dev_200"]["ids"])
    answered_ids = {row["id"] for row in gate.rows_of(where / pack["legs"][0]["out"])}
    refused_ids = {one["id"] for one in refused}

    def three_states(one: dict) -> str:
        if one["id"] in parsed:
            return str(parsed[one["id"]].get("subject_type"))
        if one["id"] in refused_ids:
            return "REFUSED — answered, and the parser refused the reply"
        return "UNANSWERED — the pod was killed before this row"

    distribution = Counter(three_states(one) for one in pack["legs"][0]["items"])
    return {
        "phase": "pass1-window",
        "contract": "docs/PROMPT-pass1-window.md D2",
        "registration": {
            "record": summary.rel(gate.PREREG),
            "sha256": summary.sha256_of(gate.PREREG),
        },
        "what_this_run_is_not": record["what_this_run_is_not"],
        "completeness": {
            key: value
            for key, value in bar.items()
            if key
            in (
                "rung",
                "file",
                "rows_in_the_file",
                "owed",
                "answered",
                "parsed",
                "sha_mismatches",
                "parse_refusals",
                "parse_refusals_by_cause",
                "parse_refusal_rows",
                "replies_that_never_closed_their_object",
                "unanswered",
                "unanswered_ids",
                "duplicate_ids",
                "ids_the_leg_never_asked",
                "verdict",
                "rule",
            )
        },
        "label_distribution": {
            "over_the_population": dict(sorted(distribution.items())),
            "refusals_by_cause": dict(sorted(Counter(one["cause"] for one in refused).items())),
            "answered": len(answered_ids),
            "owed": len(pack["legs"][0]["items"]),
            "rule": (
                "what v2 SAID, in THREE states and not two. A row with no reply is UNANSWERED and"
                " not refused: this run was killed at rung 4 with 901 rows never asked, and folding"
                " them into a refusal class would put the pod's death in the parser's column"
                " ([[the_empty_class_eats_the_parse_failures]] read the other way round). A"
                " distribution is not an accuracy either way"
            ),
        },
        "pass_2_filter": pass_2_filter(pack, parsed, refused_ids, pack["population"]["threads"]),
        "report_only": {
            "rule": record["bars"]["report_only"]["rule"],
            "the_650_labelled_rows": labelled_reading(
                record,
                pack,
                where,
                labelled,
                "every labelled row inside this population — a reading, not a bar",
            ),
            "the_450_not_in_dev_200": labelled_reading(
                record,
                pack,
                where,
                labelled - dev,
                "the labelled rows NO prompt was ever tuned against — and its «our» denominator"
                " is ZERO BY CONSTRUCTION: build_pass1_fewshot_packs.py::dev_units takes ALL 49"
                " «our» rows into dev-200 whole, so the 450 outside it contain none of the class"
                " this programme is about. It is a reading of overall agreement on untuned rows and"
                " it can say nothing about «our» rows, ever",
            ),
            "the_dev_200": {
                **labelled_reading(
                    record,
                    pack,
                    where,
                    dev,
                    "the rows r2 measured. It should reproduce 136/200 and 38/49 up to decoding"
                    " noise; a difference is STATED and not explained away",
                ),
                "r2_reported": {"agreed": 136, "n": 200, "our_agreed": 38, "our_n": 49},
            },
            "the_fourteen": the_fourteen(record, parsed),
        },
        "spans": spans(record, state, pack, where),
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
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

    bar = record["completeness"]
    print(
        f"  BAR {bar['verdict']} — answered {bar['answered']}/{bar['owed']} · parsed"
        f" {bar['parsed']} · sha mismatches {bar['sha_mismatches']} · refusals"
        f" {bar['parse_refusals']} {bar['parse_refusals_by_cause']}"
    )
    print(f"  said: {record['label_distribution']['over_the_population']}")
    filt = record["pass_2_filter"]
    print(
        f"  pass-2 filter: {filt['filtered_rows_total']} rows in"
        f" {filt['threads_with_at_least_one_filtered_row']} of {filt['threads_carrying_a_payable_comment']} callable threads ({filt['threads_in_the_cell']} in the cell) ·"
        f" {filt['filtered_chars_total']} chars · widest thread"
        f" {filt['widest_thread_filtered_rows']} rows"
    )
    for name, block in record["report_only"].items():
        if not isinstance(block, dict):
            continue
        print(
            f"  [not a bar] {name}: {block['agreed']}/{block['n']}"
            + (
                f" · our {block['our_agreed']}/{block['our_n']}"
                if "our_n" in block
                else f" (multiplicity {block.get('multiplicity')})"
            )
        )
    spans_block = record["spans"]["measured"]
    print(
        f"  measured: ssh {spans_block['ssh_publish_seconds']} s · load"
        f" {spans_block['model_load_seconds']} · {spans_block['seconds_per_call_mean']} s/call"
        f" (slowest {spans_block['seconds_per_call_slowest']}) · billed"
        f" {record['spans']['billed_seconds']} s = ${record['spans']['billed_usd']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
