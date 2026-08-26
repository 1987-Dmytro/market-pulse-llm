#!/usr/bin/env python3
"""The paired table `think-zero-shot` exists to produce: BEFORE · thinking · delta, per stage.

Ruling (ф) buys the SAME registered prompts over the SAME rows with Gemma 4's thinking channel
open, so both halves of every cell are scored by the SAME shipped instrument and neither is
recomputed here. `gate_pass1_fewshot.leg_table` reads a leg's out-file out of a directory by the
leg's own name, and `score_pass2_signals_r2` reads one module constant — so the thinking column is
served by COPYING it under the name the scorer looks for and by pointing that constant at it. No
gate logic moves; if it did, the two columns would be two instruments and the delta would be theirs
([[two_instruments_two_inputs]]).

A stage the pod never bought is `null`, not zero: rung 2 stopped the programme where the cap said,
and an unbought column that reported 0 would read as a collapse ([[an_abstention_is_an_answer]]).

    PYTHONPATH=src python3 scripts/score_think_zero_shot.py
"""

import json
import shutil
import statistics
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS = REPO_ROOT / "results"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_pass1_fewshot as pass1_gate  # noqa: E402
import reader_v5_pod_runner as runner  # noqa: E402
import score_pass2_signals_r2 as pass2_scorer  # noqa: E402

OUT = RESULTS / "think_zero_shot_table.json"
PREREG = RESULTS / "prereg_think_zero_shot.json"
FEWSHOT_PREREG = RESULTS / "prereg_pass1_fewshot.json"


def rows_of(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(one) for one in path.read_text(encoding="utf-8").splitlines() if one.strip()]


def emission(rows: list[dict]) -> dict:
    """What the channel actually did — the reading the contract asks for by name.

    A `length` finish is a COUNTED parse failure and never a retry, and under this template it is
    an unclosed thought: `balanced` is False and the whole emission is working-out. Both are
    counted here rather than inferred from the reply text.
    """
    if not rows:
        return {"n": 0}
    thoughts = [row["thought_tokens"] for row in rows if row.get("thought_tokens") is not None]
    seconds = [row["seconds"] for row in rows]
    cut = [row["cut_chars"] for row in rows]
    return {
        "n": len(rows),
        "length_cutoffs": sum(1 for row in rows if row.get("finish_reason") == "length"),
        "unbalanced": sum(1 for row in rows if not row.get("balanced")),
        "seconds": {
            "mean": round(statistics.fmean(seconds), 3),
            "max": max(seconds),
            "total": round(sum(seconds), 1),
        },
        "thought_tokens": {
            "mean": round(statistics.fmean(thoughts), 1) if thoughts else None,
            "median": round(statistics.median(thoughts), 1) if thoughts else None,
            "min": min(thoughts) if thoughts else None,
            "max": max(thoughts) if thoughts else None,
        },
        "stop_trimmed_the_answer": sum(1 for one in cut if one),
    }


def served(path: Path, as_name: str) -> Path:
    """The thinking file under the name the shipped scorer looks for, in a throwaway directory."""
    where = Path(tempfile.mkdtemp(prefix="think-column-"))
    shutil.copy(path, where / as_name)
    return where


def pass1_leg(pack_name: str, leg_name: str, before: dict) -> dict | None:
    """One dev/holdout leg, both columns, through `leg_table` — and the flips, both ways."""
    pack = json.loads((RESULTS / pack_name).read_text(encoding="utf-8"))
    leg = next(one for one in pack["legs"] if one["name"] == leg_name)
    out = RESULTS / runner.out_name(leg["out"], pack["serving"]["serving_config"])
    rows = rows_of(out)
    if len(rows) < len(leg["items"]):
        return {
            "bought": len(rows),
            "owed": len(leg["items"]),
            "table": None,
            "why": "the stage was not bought — rung 2 stopped the programme before it",
        }
    record = json.loads(FEWSHOT_PREREG.read_text(encoding="utf-8"))
    where = served(out, leg["out"])
    thinking = pass1_gate.leg_table(record, pack, leg_name, where)
    # `leg_table` does not report the refusals, and THIS column has them: a `length` cut-off is
    # an unclosed thought with no answer in it, and it must be COUNTED rather than fall into the
    # class an empty answer lands in ([[empty_class_eats_the_parse_failures]])
    refused = pass1_gate.answers_of(where / leg["out"], leg["items"])[1]
    gold = pass1_gate.labels()
    collapse = pass1_gate.probe_b.collapse
    was = {one["id"]: one for one in pass1_gate.answers_of(RESULTS / leg["out"], leg["items"])[0]}
    now = {one["id"]: one for one in pass1_gate.answers_of(where / leg["out"], leg["items"])[0]}
    won, lost = [], []
    for item in leg["items"]:
        want = collapse(gold[(item["thread"], int(item["msg_id"]))])
        b = collapse(was[item["id"]]["subject_type"]) if item["id"] in was else None
        t = collapse(now[item["id"]]["subject_type"]) if item["id"] in now else None
        if b != want and t == want:
            won.append({"id": item["id"], "gold": want, "before": b})
        elif b == want and t != want:
            lost.append({"id": item["id"], "gold": want, "thinking": t})
    return {
        "before": before,
        "thinking": {
            "agreed": thinking["agreed"],
            "n": thinking["n"],
            "our_agreed": thinking.get("our_agreed"),
            "our_n": thinking.get("our_n"),
            "parse_refusals": len(refused),
            "refused_ids": sorted(
                one["id"] if isinstance(one, dict) else str(one) for one in refused
            ),
        },
        "delta": thinking["agreed"] - before["agreed"],
        "flips": {
            "to_gold": won,
            "away_from_gold": lost,
            "rule": "a row the BEFORE column got wrong and thinking got right, and back",
        },
        "emission": emission(rows),
    }


def pass_2() -> dict:
    """The three bars, re-read by the SHIPPED gate over whatever threads the pod bought."""
    parts = [
        RESULTS / "pass2_signals_r2_reference.READER_THINK.jsonl",
        RESULTS / "pass2_signals_r2_remainder.READER_THINK.jsonl",
    ]
    rows = [row for part in parts for row in rows_of(part)]
    if not rows:
        return {"threads": 0, "bars": None, "why": "no pass-2 thread was bought"}
    merged = Path(tempfile.mkdtemp(prefix="p2-think-")) / "merged.jsonl"
    merged.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    was = pass2_scorer.EVIDENCE
    try:
        pass2_scorer.EVIDENCE = merged
        verdict = pass2_scorer.build()
    finally:
        pass2_scorer.EVIDENCE = was
    return {
        "threads": len(rows),
        "sources": {part.name: len(rows_of(part)) for part in parts},
        "evidence": verdict["evidence"],
        "replies": verdict["replies"],
        "bars": {
            name: {
                "passed": bar.get("passed"),
                "threads_not_read": bar.get("threads_not_read"),
                "collapsed": bar.get("collapsed") or bar.get("result"),
            }
            for name, bar in verdict["bars"].items()
        },
        "unreadable_report_only_fields": verdict["unreadable_report_only_fields"]["rows"],
        "emission": emission(rows),
    }


def build() -> dict:
    record = json.loads(PREREG.read_text(encoding="utf-8"))
    before = record["before_columns"]
    return {
        "contract": "think-zero-shot-d2",
        "registration": {
            "file": "results/prereg_think_zero_shot.json",
            "what_this_is": record["what_this_is"],
        },
        "dev_200_v2": pass1_leg("pass1_dev_pack_think.json", "v2", before["dev_200"]["v2"]),
        "dev_200_v1": pass1_leg("pass1_dev_pack_think.json", "base", before["dev_200"]["base"]),
        "holdout_100": pass1_leg(
            "pass1_holdout_100_think.json",
            "holdout",
            {"agreed": before["holdout_100"]["agreed"], "n": before["holdout_100"]["n"]},
        ),
        "pass_2": pass_2(),
        "pass_2_before": before["pass_2"],
    }


def main(argv: list[str] | None = None) -> int:
    table = build()
    OUT.write_text(
        json.dumps(table, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote results/{OUT.name}")
    for name in ("dev_200_v2", "dev_200_v1", "holdout_100"):
        leg = table[name]
        if leg.get("table") is None and "before" not in leg:
            print(f"  {name:12} NOT BOUGHT — {leg['bought']} of {leg['owed']}")
            continue
        print(
            f"  {name:12} BEFORE {leg['before']['agreed']:>3}/{leg['before']['n']}"
            f" · thinking {leg['thinking']['agreed']:>3}/{leg['thinking']['n']}"
            f" · delta {leg['delta']:+d}"
            f" · flips +{len(leg['flips']['to_gold'])}/-{len(leg['flips']['away_from_gold'])}"
        )
    p2 = table["pass_2"]
    print(f"  pass_2       {p2['threads']} threads read")
    for name, bar in (p2.get("bars") or {}).items():
        state = "UNSCORED" if bar["collapsed"] is None else ("GO " if bar["passed"] else "RED")
        print(f"    {name:16} {state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
