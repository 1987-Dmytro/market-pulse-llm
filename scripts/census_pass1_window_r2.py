#!/usr/bin/env python3
"""`results/pass1_window_r2_census.json` — D2 over the UNION 131 + 901, at $0.

**What this is for.** `docs/PROMPT-pass1-window-r2.md` D2: the completeness bar of THIS registration
(901 / 901) AND the window's own completeness (1 032 / 1 032) beside it; the label distribution in
three states; the per-thread pass-2 filter table over the WHOLE window — the one output that prices
`pass2-signals`; the report-only readings pair-keyed; the volume tail's rows bought twice; and the
measured spans beside what was charged.

**The union is a VIEW and not a merge.** r1's out-file holds 131 replies and this contract's holds
901, and every reading below the bar is over both. The view is built by writing the two files' lines
into ONE scratch copy under the r1 pack's own leg name — the r1 pack is the WINDOW's pack, its 1 032
items are the population, and the r2 items ARE its items. Nothing is written back into either real
out-file, and the two are never combined on disk: a merged out-file would be a fourth artefact
nobody registered ([[a_retry_inherits_the_last_attempts_output]]).

**It is keyed on the PAIR `(thread, msg_id)`, everywhere.** Seven msg_ids of the 650 labelled rows
live in two threads each, so a union keyed on the msg_id would merge two channels' comments into one
row. The labelled readings go through `census_pass1_window.labelled_reading`, which scores one THREAD
at a time for exactly that reason — the step 0.5 correction, whose own producer is imported here
rather than copied.

**Every reading below the bar is a CENSUS ROW and none of them is a bar.** The fourteen are on their
FIFTH look and may not be promoted to «v2 takes N of 14» by this report, by the acceptance or by the
next registration.

    PYTHONPATH=src python3.11 scripts/census_pass1_window_r2.py
    PYTHONPATH=src python3.11 scripts/census_pass1_window_r2.py --out /tmp/again.json   # the pair
"""

import argparse
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import census_pass1_window as r1census  # noqa: E402
import gate_pass1_window_r2 as gate  # noqa: E402
import volume_tail_pass1_window as volume  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

OUT = REPO_ROOT / "results" / "pass1_window_r2_census.json"
RESULTS = REPO_ROOT / "results"
R1_PACK = RESULTS / "pass1_window_pack.json"
R1_OUT = RESULTS / "pass1_window_v2.jsonl"
VOLUME_TAIL = RESULTS / "pass1_window_volume_tail.jsonl"

OURS = r1census.OURS


def union_view(scratch: Path) -> tuple[dict, Path]:
    """The WINDOW's pack and an out-file holding both halves — a view, never a merge on disk."""
    pack = json.loads(summary.read_text_or_refuse(R1_PACK))
    name = pack["legs"][0]["out"]
    lines = []
    for path in (R1_OUT, RESULTS / "pass1_window_r2_v2.jsonl"):
        if path.exists():
            lines += [one for one in path.read_text(encoding="utf-8").splitlines() if one.strip()]
    (scratch / name).write_text("".join(one + "\n" for one in lines), encoding="utf-8")
    return pack, scratch


def replies_the_mac_does_not_hold(out_file: Path, log: Path) -> dict:
    """Dv657 on THIS pod: the runner's log reaches one reply further than the file beside it."""
    if not log.exists():
        return {"reading": f"{summary.rel(log)} is not on disk — nothing to read"}
    replies = re.findall(
        r"^\[\s*([\d.]+)s\]\s+reply\s+(\d+)/(\d+)\s+(\S+)",
        summary.read_text_or_refuse(log),
        flags=re.M,
    )
    in_file = {row["id"] for row in gate.r1.rows_of(out_file)} if out_file.exists() else set()
    beyond = [
        {"n": int(n), "id": one, "log_elapsed_seconds": float(at)}
        for at, n, _total, one in replies
        if one not in in_file
    ]
    return {
        "rows_in_the_copied_back_file": len(in_file),
        "replies_the_pod_log_reports": max((int(n) for _at, n, _t, _i in replies), default=0),
        "replies_named_by_the_log_and_absent_from_the_file": beyond,
        "rule": (
            "the watch copies once a poll and a KILL happens inside the loop, so the log — copied by"
            " the same poll — can reach one row further than the out-file. An empty list here means"
            " the run ended with the file and the log agreeing, which is what a GO looks like"
        ),
        "instrument": f"{summary.rel(log)} — the pod's own line, read and not typed",
    }


def per_poll_copy_back(watch: dict, out_file: Path, owed: int) -> dict:
    """What a poll cost, BOUNDED — `append_gate` records one gate however many times it polled."""
    watched = watch.get("watched_seconds")
    if watched is None or not out_file.exists():
        return {"reading": "no watch gate on this record — nothing to bound"}
    poll = 20.0
    bounds = {}
    for polls in (int(watched // poll), int(watched // poll) + 1):
        if polls > 0:
            bounds[polls] = round((watched - (polls - 1) * poll) / polls, 2)
    rows = len(gate.r1.rows_of(out_file))
    return {
        "rule": (
            "the loop's own watched_seconds less the sleeps it took, over the polls it can have"
            " taken. Both candidate poll counts are published because the record does not carry the"
            " count itself — a BOUND and not a measurement (Dv656)"
        ),
        "poll_seconds": poll,
        "watched_seconds": watched,
        "seconds_per_poll_by_poll_count": bounds,
        "bytes_copied_at_the_end": out_file.stat().st_size,
        "rows_at_the_end": rows,
        "what_it_bounds": (
            f"a poll copied the out-file ({out_file.stat().st_size} bytes at the end, {rows} rows of"
            f" {owed}), the launch stamp and the pod log, computed the fingerprint and ran the"
            f" projection — all of it inside {max(bounds.values())} s at worst. The registration"
            f" charges 1 300 s of overhead for the copy-back of ≤ {owed} rows plus the gate on the"
            " Mac plus the delete"
        ),
    }


def the_rate_of_this_pod(spans: dict) -> dict:
    """This pod's s/call beside every other reading this stack owns — the census row of the class."""
    measured = spans["measured"].get("seconds_per_call_mean")
    return {
        "this_pod": {"pod": spans["pod"], "seconds_per_call": measured},
        "the_readings_this_class_has": {
            "pass1-probe-b, base (v1), 64 rows": 5.161578,
            "pass1-fewshot r2, base (v1), 200 dev rows, pod 8tpx8lf05n6skc": 2.293075,
            "pass1-fewshot r2, v2, 200 dev rows, pod 8tpx8lf05n6skc": 2.725780,
            "pass1-window r1, v2, 131 window rows, pod xpz3zb7yxus5cw": 4.498473,
        },
        "charged_here": spans["charged"]["seconds_per_call"],
        "over_the_charge": round(measured / spans["charged"]["seconds_per_call"], 4)
        if measured
        else None,
        "rule": (
            "a rate is a property of the POD (Dv647). This registration charged the TOP of the"
            " measured spread rather than a sibling run's figure, and this pod is one more reading"
            " of the class — not a rate the programme owns. If it came in under the charge, that is"
            " a third point on a spread with two, and the next registration still charges the top"
        ),
    }


def build() -> dict:
    record = gate.r1.registration()
    state = json.loads(summary.read_text_or_refuse(gate.r1.RECORD))
    r2_pack = json.loads(summary.read_text_or_refuse(gate.r1.PACK))
    r2_out = RESULTS / r2_pack["legs"][0]["out"]

    bar = gate.r1.completeness(record, state, r2_pack, RESULTS)

    with tempfile.TemporaryDirectory() as scratch:
        scratch = Path(scratch)
        window, where = union_view(scratch)
        parsed, refused = r1census.answers(window, where)
        membership = window["membership"]
        labelled = set(membership["labelled_650"]["ids"])
        dev = set(membership["dev_200"]["ids"])
        refused_ids = {one["id"] for one in refused}
        union_rows = {row["id"] for row in gate.r1.rows_of(where / window["legs"][0]["out"])}

        def three_states(one: dict) -> str:
            if one["id"] in parsed:
                return str(parsed[one["id"]].get("subject_type"))
            if one["id"] in refused_ids:
                return "REFUSED — answered, and the parser refused the reply"
            return "UNANSWERED — no reply in either half of the union"

        distribution = Counter(three_states(one) for one in window["legs"][0]["items"])
        readings = {
            "rule": record["bars"]["report_only"]["rule"],
            "keyed_on": (
                "the PAIR (thread, msg_id), over the UNION of both out-files. Seven msg_ids of the"
                " 650 live in two threads each and the scorer's answer map is keyed on the msg_id"
                " alone, so every labelled reading is taken one THREAD at a time and summed — the"
                " step 0.5 correction, whose producer this file imports rather than copies"
            ),
            "the_650_labelled_rows": r1census.labelled_reading(
                record,
                window,
                where,
                labelled,
                "every labelled row of the window — a reading, not a bar",
            ),
            "the_450_not_in_dev_200": r1census.labelled_reading(
                record,
                window,
                where,
                labelled - dev,
                "the labelled rows NO prompt was ever tuned against — and its «our» denominator is"
                " ZERO BY CONSTRUCTION and always will be (Dv652)",
            ),
            "the_dev_200": {
                **r1census.labelled_reading(
                    record,
                    window,
                    where,
                    dev,
                    "the rows r2 measured. It should reproduce 136/200 and 38/49 up to decoding"
                    " noise; a difference is STATED and not explained away",
                ),
                "r2_reported": {"agreed": 136, "n": 200, "our_agreed": 38, "our_n": 49},
            },
            "the_fourteen": r1census.the_fourteen(record, parsed),
        }
        table = r1census.pass_2_filter(window, parsed, refused_ids, window["population"]["threads"])

    spans = r1census.spans(record, state, r2_pack, RESULTS)
    spans["measured"]["per_poll_copy_back"] = per_poll_copy_back(
        {one["kind"]: one for one in state.get("gates", [])}.get("watch", {}),
        r2_out,
        int(record["bars"]["completeness"]["owed"]),
    )

    tail = (
        volume.account(VOLUME_TAIL, R1_OUT, r2_pack, spans["measured"].get("seconds_per_call_mean"))
        if VOLUME_TAIL.exists()
        else {
            "reading": (
                f"{summary.rel(VOLUME_TAIL)} is not on disk — step 3a of the runbook did not copy"
                " the volume's surviving out-file back, or there was none. Dv657's lower bound stays"
                " open"
            )
        }
    )

    return {
        "phase": "pass1-window-r2",
        "contract": "docs/PROMPT-pass1-window-r2.md D2",
        "registration": {
            "record": summary.rel(gate.r1.PREREG),
            "sha256": summary.sha256_of(gate.r1.PREREG),
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
        "the_windows_completeness": {
            "not_a_bar_of_this_registration": True,
            "owed": window["population"]["payable_comments"],
            "answered": len(union_rows),
            "answered_by_r1": len(union_rows) - bar["answered"],
            "answered_here": bar["answered"],
            "complete": len(union_rows) == window["population"]["payable_comments"],
            "rule": record["bars"]["the_windows_completeness"]["rule"],
        },
        "replies_the_mac_does_not_hold": replies_the_mac_does_not_hold(r2_out, gate.r1.POD_LOG),
        "the_volume_tail": tail,
        "label_distribution": {
            "over_the_window": dict(sorted(distribution.items())),
            "refusals_by_cause": dict(sorted(Counter(one["cause"] for one in refused).items())),
            "answered": len(union_rows),
            "owed": len(window["legs"][0]["items"]),
            "rule": (
                "what v2 SAID over the whole window, in THREE states and not two. A row with no"
                " reply in EITHER half is UNANSWERED and not refused: folding never-asked rows into"
                " a refusal class would put a pod's death in the parser's column"
                " ([[the_empty_class_eats_the_parse_failures]] read the other way round, and the"
                " defect r1's census carried three times before it was caught). A distribution is"
                " not an accuracy either way"
            ),
        },
        "pass_2_filter": table,
        "report_only": readings,
        "spans": spans,
        "the_rate_of_this_pod": the_rate_of_this_pod(spans),
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "imported": {
                "scripts/census_pass1_window.py": summary.sha256_of(
                    REPO_ROOT / "scripts" / "census_pass1_window.py"
                ),
                "rule": (
                    "the readings are r1's census functions, unedited — including the per-thread"
                    " `labelled_reading` step 0.5 corrected. What is new here is the UNION view they"
                    " are handed and the blocks this contract adds"
                ),
            },
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    census = build()
    args.out.write_text(
        json.dumps(census, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    bar = census["completeness"]
    window = census["the_windows_completeness"]
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    print(
        f"  BAR {bar['verdict']} — answered {bar['answered']}/{bar['owed']} ·"
        f" parsed {bar['parsed']} · sha mismatches {bar['sha_mismatches']} ·"
        f" refusals {bar['parse_refusals']} {bar['parse_refusals_by_cause']}"
    )
    print(
        f"  the WINDOW: {window['answered']} of {window['owed']}"
        f" ({window['answered_by_r1']} from r1 + {window['answered_here']} here) ·"
        f" complete {window['complete']}"
    )
    print(f"  said: {census['label_distribution']['over_the_window']}")
    filt = census["pass_2_filter"]
    print(
        f"  pass-2 filter: {filt['filtered_rows_total']} rows in"
        f" {filt['threads_with_at_least_one_filtered_row']} of"
        f" {filt['threads_carrying_a_payable_comment']} callable threads ·"
        f" {filt['filtered_chars_total']} chars"
    )
    for name, one in census["report_only"].items():
        if isinstance(one, dict) and "agreed" in one:
            print(
                f"  [not a bar] {name}: {one['agreed']}/{one['n']}"
                + (f" · our {one['our_agreed']}/{one['our_n']}" if "our_n" in one else "")
            )
    rate = census["the_rate_of_this_pod"]
    print(
        f"  rate of this pod: {rate['this_pod']['seconds_per_call']} s/call against"
        f" {rate['charged_here']} charged ({rate['over_the_charge']}x)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
