#!/usr/bin/env python3
"""The pass-2 pack for the 16 reference threads, built from ONE pass-1 out-file — per leg.

`docs/PROMPT-lora-c-prep.md` D0. Bars 1 and 3 of `lora-c-run` are pass-2 readings, and pass 2's
input is pass 1's output — so each of the four legs gets its own pass-2 pack, built from that leg's
own out-file through `census_pass1_window.pass_2_filter`. Bar 2 is inherited and reported «held»:
its entity cases are a reader-verdict property and no pass-1 adapter moves them.

**This file is a SIBLING of `build_pass2_pack.py`, not an edit of it.** That builder reads the
window's own two out-files by name and is pinned by `results/prereg_pass2_signals.json`, a sealed
record of a closed paid session; its `filtered()` hard-codes `census_pass1_window_r2.union_view`.
Here the out-file is an ARGUMENT, so the same machinery has to be reachable with a different input
([[a_pinned_file_is_not_edited_to_grow_a_parameter]]).

**Its test is that it reproduces r2 on r2's own input.** Driven at $0 over the existing window
out-files and restricted to the 16 reference threads, the bars it selects must come back
**bar 1 = 4 of 5** and **bar 3 = RED at 2 signals** — the readings
`results/pass2_signals_r2_verdict.json` already holds. A builder whose reference-thread selection
had drifted would move those two numbers, and nothing else in this contract would notice
([[trace_the_producer_not_the_result]]).

    PYTHONPATH=src python3.11 scripts/build_lora_c_pass2_pack.py --reproduce
    PYTHONPATH=src python3.11 scripts/build_lora_c_pass2_pack.py \\
        --out-file results/pass1_window_v2.jsonl --out-file results/pass1_window_r2_v2.jsonl \\
        --leg base_v2 --out results/lora_c_pass2_base_v2_pack.json
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_lora_c_data as data  # noqa: E402
import build_pass1_label_pack_r2 as r2pack  # noqa: E402
import build_pass2_pack as p2  # noqa: E402
import census_pass1_window as census  # noqa: E402
import score_pass2_signals as r1score  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
from market_pulse import pass2_r2  # noqa: E402

WINDOW_PACK = REPO_ROOT / "results" / "pass1_window_pack.json"
WINDOW_OUT = (
    REPO_ROOT / "results" / "pass1_window_v2.jsonl",
    REPO_ROOT / "results" / "pass1_window_r2_v2.jsonl",
)
R2_PREREG = REPO_ROOT / "results" / "prereg_pass2_signals_r2.json"
R2_EVIDENCE = REPO_ROOT / "results" / "pass2_signals_r2_v1.jsonl"
GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
OUT = REPO_ROOT / "results" / "lora_c_pass2_pack.json"

EXPECTED_BAR_1 = "4 of 5"
EXPECTED_BAR_3_SIGNALS = 2
"""What r2 measured over the whole 79, and what bars 1 and 3 must still say when the population is
cut to the 16 reference threads — both bars read only reference threads, so the cut may not move
them. `results/pass2_signals_r2_verdict.json` is the authority and the reproduction reads it."""


def filtered(pack: dict, out_files: tuple[Path, ...]) -> tuple[dict, dict, set]:
    """`census_pass1_window.pass_2_filter`, CALLED over ONE leg's replies.

    `build_pass2_pack.filtered` does the same job and cannot take an argument: it names the window's
    two out-files through `census_pass1_window_r2.union_view`. The union view here is built the same
    way — a scratch copy under the pack's own leg name, never a merge on disk — so the only thing
    that differs between this and the sealed builder is WHICH replies are copied in.
    """
    (leg,) = pack["legs"]
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp)
        merged = scratch / leg["out"]
        merged.write_text(
            "".join(
                path.read_text(encoding="utf-8").rstrip("\n") + "\n"
                for path in out_files
                if path.read_text(encoding="utf-8").strip()
            ),
            encoding="utf-8",
        )
        parsed, refused = census.answers(pack, scratch)
    refused_ids = {one["id"] for one in refused}
    table = census.pass_2_filter(pack, parsed, refused_ids, pack["population"]["threads"])
    return parsed, table, refused_ids


def build(out_files: tuple[Path, ...], leg_name: str) -> dict:
    """The pass-2 units for the 16 reference threads under one leg's pass-1 answers."""
    pack = json.loads(summary.read_text_or_refuse(WINDOW_PACK))
    reference = set(data.reference_threads())
    parsed, table, refused_ids = filtered(pack, out_files)
    blocks = p2.entity_block(pack)
    store = r2pack.raw_threads()
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    flags = p2.membership(gold)

    by_thread: dict[str, list[dict]] = {}
    for item in pack["legs"][0]["items"]:
        if item["thread"] not in reference:
            continue
        answer = parsed.get(item["id"])
        if answer is None or answer.get("subject_type") not in census.OURS:
            continue
        by_thread.setdefault(item["thread"], []).append({**item, **answer})

    cells = {one["thread"]: one for one in table["per_thread"]}
    units = []
    for thread in sorted(by_thread):
        rows = sorted(by_thread[thread], key=lambda one: int(one["msg_id"]))
        cell = cells.get(thread)
        if cell is None or cell["filtered_rows"] != len(rows):
            raise SystemExit(
                f"{thread}: this build selects {len(rows)} filtered rows and"
                f" census_pass1_window.pass_2_filter counts"
                f" {None if cell is None else cell['filtered_rows']}. The filter is the authority"
                " and this selection is what is being checked — stop and report."
            )
        units.append(p2.unit(thread, rows, store, blocks[thread], flags.get(thread, {})))

    empty = sorted(one for one in reference if one not in by_thread)
    return {
        "phase": "lora-c-prep",
        "contract": "docs/PROMPT-lora-c-prep.md D0 — the pass-2 eval pack, per leg",
        "leg": leg_name,
        "built_from": [summary.rel(path) for path in out_files],
        "population": {
            "rule": (
                "the 16 reference threads, restricted to the rows THIS leg's pass 1 labelled"
                f" {' / '.join(census.OURS)} — census_pass1_window.pass_2_filter, called"
            ),
            "reference_threads": sorted(reference),
            "threads_with_at_least_one_filtered_row": len(units),
            "threads_with_none": empty,
            "filtered_rows": sum(len(one["comments"]) for one in units),
            "unreadable_pass_1_rows": len(
                [one for one in refused_ids if one.split("#")[0] in reference]
            ),
        },
        "bars": {
            "scored_here": ["1_flagships", "3_noise"],
            "inherited": {
                "2_entity_cases": (
                    "HELD at pass2-signals-r2's reading. Its cases are resolved from the READER's"
                    " bought verdicts, which no pass-1 adapter moves — so the bar is reported and"
                    " not re-scored, and saying so is the difference between an inherited number"
                    " and a measured one"
                )
            },
            "scored_by": "score_pass2_signals.bar_states, through prereg_pass2_signals_r2.json",
        },
        "legs": [
            {
                "name": leg_name,
                "task": pass2_r2.PASS2_TASK_V1,
                "out": f"lora_c_pass2_{leg_name}.jsonl",
                "items": units,
            }
        ],
        # The serving block is `results/pass2_r2_pack.json`'s, READ from that file rather than
        # restated: `reader_v5_pod_runner.run` and `load_reader` both read it, and this line's
        # pass-2 legs are the same instrument on the same card class asking the same question. A
        # second copy of the model id, the revision, the quantization and the 4 000-token ceiling
        # is four more numbers that can drift ([[preregistration_is_a_file_not_a_constant]]).
        "serving": serving_of(PASS2_R2_PACK),
        # `scripts/pass2_r2_pod_runner.carried` reads this block and REFUSES when the out-file it
        # would resume into carries rows the pack does not name. lora-c carries nothing: each leg's
        # pack is rebuilt from THAT leg's pass-1 out-file, so there is no earlier run to inherit
        # from — and an empty list is the assertion «this out-file must be empty», not the absence
        # of a check ([[the_empty_row_is_the_answer]]).
        "carried": {
            "ids": [],
            "units": 0,
            "from": None,
            "rule": (
                "nothing is carried into a lora-c pass-2 leg. Each leg is rebuilt from its own"
                " arm's pass-1 out-file, so a row already in the target file would be a row from"
                " another leg and the runner stops before the model is loaded"
            ),
        },
        "instruments": {
            # The SHAPE is `scripts/pass2_r2_pod_runner.check_instrument`'s, not this file's taste:
            # that handshake reads `parser.sha256`, `module.sha256` and `module_r2.sha256` and it is
            # pinned by pass2-signals-r2's sealed record, so the pack bends and the runner does not.
            # Until lora-c-run r2 drove it at $0 this block was a flat `module_sha256` string and
            # every pass-2 leg of this line would have died on a KeyError with the model loaded
            # ([[a_frozen_record_is_an_input_to_shipped_code]]).
            "parser": {
                "path": "src/market_pulse/prompts.py",
                "entry_point": "market_pulse.pass2_r2.parse_pass2",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
            },
            "module": {
                "path": "src/market_pulse/pass2.py",
                "rule": "the TEXT and the RENDERER — r1's, unmoved, and what the pod renders from",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "pass2.py"),
            },
            "module_r2": {
                "path": "src/market_pulse/pass2_r2.py",
                "rule": "the ceiling and the tolerant parser the Mac reads these replies with",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "pass2_r2.py"),
            },
            "prompt_sha256": {
                pass2_r2.PASS2_TASK_V1: pass2_r2.prompt_sha256(pass2_r2.PASS2_TASK_V1)
            },
            "unit_shape": "build_pass2_pack.unit, CALLED — the sealed builder's own renderer",
            "filter": "census_pass1_window.pass_2_filter, CALLED",
            "ceiling_chars": pass2_r2.PASS2_MAX_INPUT_CHARS,
            "widest_request": max((one["rendered_chars"] for one in units), default=0),
        },
        "produced_by": {
            "script": "scripts/build_lora_c_pass2_pack.py",
            "sha256": data.sha_text(Path(__file__).read_text(encoding="utf-8")),
        },
    }


def reproduce() -> dict:
    """Drive this builder over the WINDOW's own out-files and re-score bars 1 and 3.

    The pack is rebuilt from the same replies `pass2-signals-r2` was priced on, then r2's OWN paid
    replies are re-parsed for the threads this builder selected and handed to the r2 registration's
    own bar function. If the selection has drifted, the two numbers move.
    """
    built = build(WINDOW_OUT, "reproduce")
    record = json.loads(summary.read_text_or_refuse(R2_PREREG))
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    by_id = {one["id"]: one for one in built["legs"][0]["items"]}
    mine = set(by_id)
    parsed, refused = {}, {}
    for line in R2_EVIDENCE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row["id"] not in mine:
            continue
        try:
            parsed[row["id"]] = pass2_r2.parse_pass2(row["reply"], unit=by_id[row["id"]])
        except Exception as err:  # noqa: BLE001 — the cause is what the bar needs to see
            refused[row["id"]] = type(err).__name__
    seen = set(parsed)
    bars = r1score.bar_states(
        record, gold, parsed, seen, attempted=seen | set(refused), refused_threads=refused
    )
    one, three = bars["1_flagships"], bars["3_noise"]
    cell = one["collapsed"]
    got_one = f"{cell['cases_answered']} of {cell['cases']}"
    got_three = three["result"]["signals"]
    return {
        "threads_selected": len(mine),
        "threads": sorted(mine),
        "replies_parsed": len(parsed),
        "replies_refused": sorted(refused),
        "bar_1": one,
        "bar_3": three,
        "bar_1_reading": got_one,
        "bar_3_signals": got_three,
        "expected_bar_1": EXPECTED_BAR_1,
        "expected_bar_3_signals": EXPECTED_BAR_3_SIGNALS,
        "agrees": got_one == EXPECTED_BAR_1 and got_three == EXPECTED_BAR_3_SIGNALS,
    }


PASS2_R2_PACK = REPO_ROOT / "results" / "pass2_r2_pack.json"
"""pass2-signals-r2's own pack — the serving block this line inherits, by reading it."""


def serving_of(path: Path) -> dict:
    """r2's serving block, with the adapter slot said out loud.

    `adapter: null` is r2's value and it stays: a lora-c pass-2 leg reads a pass-1 out-file that an
    ADAPTER produced, but pass 2 itself is the base model both times — that is what makes the two
    arms' end-to-end bars comparable at all. The runner mounts nothing here.
    """
    block = json.loads(path.read_text(encoding="utf-8"))["serving"]
    if block.get("adapter") is not None:
        raise SystemExit(
            f"{summary.rel(path)} serves an adapter and pass 2 of this line is the BASE model on"
            " both arms. Stop rather than inherit a serving block that changes the instrument."
        )
    return block


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-file", type=Path, action="append", default=None)
    parser.add_argument("--leg", default="leg")
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument(
        "--reproduce",
        action="store_true",
        help="drive over the window's out-files and re-score bars 1 and 3 against r2's readings",
    )
    args = parser.parse_args(argv)

    if args.reproduce:
        check = reproduce()
        print(f"threads selected: {check['threads_selected']} of the 16 reference threads")
        print(f"  replies parsed {check['replies_parsed']} · refused {check['replies_refused']}")
        print(f"  bar 1: {check['bar_1_reading']}  (r2 measured {check['expected_bar_1']})")
        print(
            f"  bar 3: {check['bar_3_signals']} signals"
            f"  (r2 measured {check['expected_bar_3_signals']})"
        )
        print(f"  AGREES: {check['agrees']}")
        return 0 if check["agrees"] else 1

    out_files = tuple(args.out_file or WINDOW_OUT)
    record = build(out_files, args.leg)
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    block = record["population"]
    print(f"wrote {summary.rel(args.out)}  leg {record['leg']}")
    print(
        f"  {block['threads_with_at_least_one_filtered_row']} of 16 reference threads carry a"
        f" filtered row · {block['filtered_rows']} rows"
    )
    print(f"  threads with none: {block['threads_with_none']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
