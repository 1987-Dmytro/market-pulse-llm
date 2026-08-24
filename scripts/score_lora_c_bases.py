#!/usr/bin/env python3
"""The two BEFORE columns `lora-c-run r2` bought — base v2 and base v3 on the shared pool.

The session STOPped at rung 4 with no adapter, so **no bar is scored here and none can be**: the
registered three are per ARM and neither arm exists. What the pod did buy is the pair of base
columns the whole line is measured against, 198 replies each on eval set E, and this reads them.

`scorer.reader_comment_agreement` is the shipped judge and is CALLED — the single judge of all
numbers, never forked. Each leg is parsed by the parser that OWNS its task: `prompts.parse_pass1`
for v2, `pass1_v3.parse_pass1_v3` for v3. A reply the parser refuses is counted as a refusal and is
not repaired; a labelled row with no reply is `absent`, which is a disagreement and is counted
separately so the two failure modes never hide inside one rate
([[measure_on_the_rows_the_gate_scores]]).

The join is on `(thread, msg_id)` and never on `msg_id` alone: E draws from eight channels and a
Telegram id is unique inside a channel, not across them ([[id_spaces_that_look_comparable]]). The
shipped scorer keys on `msg_id`, so it is called per thread and the rows are summed.

    PYTHONPATH=src python3.11 scripts/score_lora_c_bases.py
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

from market_pulse import pass1_v3, prompts, scorer  # noqa: E402

EVAL_PACK = REPO_ROOT / "results" / "lora_c_eval_pack.json"
HOLDOUT = REPO_ROOT / "results" / "pass1_holdout_100.json"
LABELS = tuple(REPO_ROOT / "results" / f"labels_pass1_r{n}.jsonl" for n in (1, 2, 3))
LEGS = {
    "base_v2": (REPO_ROOT / "results" / "lora_c_base_v2.jsonl", "v2"),
    "base_v3": (REPO_ROOT / "results" / "lora_c_base_v3.jsonl", "v3"),
}
OUT = REPO_ROOT / "results" / "lora_c_bases_verdict.json"

OUR = ("категория_личное", "молочный_бренд")


def gold() -> dict:
    """The team lead's labels on the (thread, msg_id) key, r3 last — the delta rule, unchanged."""
    rows: dict[tuple[str, int], str | None] = {}
    for path in LABELS:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                one = json.loads(line)
                rows[(one["thread"], int(one["msg_id"]))] = one.get("subject_type")
    return rows


def parsed(path: Path, task: str) -> tuple[dict, list]:
    """Every reply through the parser that owns its task. A refusal is COUNTED, never repaired."""
    answers, refused = {}, []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        thread, _, msg = row["id"].rpartition("#")
        try:
            if task == pass1_v3.PASS1_TASK_V3:
                answer = pass1_v3.parse_pass1_v3(row["reply"], msg_id=int(msg))
            else:
                answer = prompts.parse_pass1(row["reply"], msg_id=int(msg))
        except Exception as refusal:
            refused.append({"id": row["id"], "why": f"{type(refusal).__name__}: {refusal}"})
            continue
        answers[(thread, int(msg))] = answer
    return answers, refused


def agreement(answers: dict, labels: dict, only: set | None = None) -> dict:
    """`scorer.reader_comment_agreement`, called PER THREAD and summed.

    The shipped judge keys its answers on `msg_id`, which is unique inside a channel and not across
    them. Calling it per thread is what keeps the key a key; summing its rows is what keeps the rate
    the judge's own arithmetic and not a second one written here.
    """
    by_thread: dict[str, list] = {}
    for (thread, msg), label in labels.items():
        if only is not None and (thread, msg) not in only:
            continue
        by_thread.setdefault(thread, []).append(
            {"msg_id": msg, "subject_type": label, "scored_fields": ["subject_type"]}
        )
    rows, totals = [], Counter()
    for thread, gold_rows in sorted(by_thread.items()):
        per_comment = [
            {"msg_id": msg, **answer} for (one, msg), answer in answers.items() if one == thread
        ]
        one = scorer.reader_comment_agreement(gold_rows, per_comment)
        for row in one["rows"]:
            rows.append({**row, "thread": thread})
        for key in ("n", "agreed", "disagreed", "absent"):
            totals[key] += one[key]
    return {
        **dict(totals),
        "rate": totals["agreed"] / totals["n"] if totals["n"] else None,
        "rows": rows,
    }


def per_class(answers: dict, labels: dict) -> dict:
    """Agreement by the gold class — and the cell this whole line targets, printed both ways."""
    table: dict[str, Counter] = {}
    cell = Counter()
    for (thread, msg), label in labels.items():
        answer = answers.get((thread, msg))
        got = None if answer is None else answer.get("subject_type")
        key = str(label)
        table.setdefault(key, Counter())["n"] += 1
        table[key]["agreed"] += got == label
        table[key]["absent"] += answer is None
        if label == "не_наш_рынок":
            cell["denominator"] += 1
            cell["to_категория_личное"] += got == "категория_личное"
            cell["to_our"] += got in OUR
    return {
        "by_class": {
            name: {**dict(counts), "rate": counts["agreed"] / counts["n"]}
            for name, counts in sorted(table.items())
        },
        "the_mention_cell": {
            "what": "`не_наш_рынок` gold answered `категория_личное` — the cell this line targets",
            **dict(cell),
            "before_on_holdout_100": "18 of 52 — results/prereg_lora_c.json::bars.report_only",
            "note": (
                "this denominator is E's `не_наш_рынок` rows, NOT the holdout's 52. The two"
                " populations differ and the numbers are not comparable across them"
            ),
        },
    }


def build() -> dict:
    labels = gold()
    pack = json.loads(EVAL_PACK.read_text(encoding="utf-8"))
    holdout = {
        (one["thread"], int(one["msg_id"]))
        for leg in pack["legs"]
        for one in leg["items"]
        if one["membership"]["holdout_100"]
    }
    e_keys = {(one["thread"], int(one["msg_id"])) for leg in pack["legs"] for one in leg["items"]}
    in_e = {key: value for key, value in labels.items() if key in e_keys}
    legs = {}
    for name, (path, leg_name) in LEGS.items():
        task = next(one["task"] for one in pack["legs"] if one["name"] == leg_name)
        answers, refused = parsed(path, task)
        legs[name] = {
            "file": summary.rel(path),
            "sha256": summary.sha256_of(path),
            "task": task,
            "replies": len(answers) + len(refused),
            "parsed": len(answers),
            "refused": refused,
            "labelled_rows_in_E": len(in_e),
            "agreement_on_every_labelled_row_of_E": agreement(answers, in_e),
            "agreement_on_the_holdout_rows_of_E": agreement(answers, in_e, only=holdout),
            **per_class(answers, in_e),
        }
    return {
        "phase": "lora-c",
        "contract": "docs/PROMPT-lora-c-run-r2.md — REPORT ONLY: no arm exists, so no bar is scored",
        "what_this_is": (
            "the two BEFORE columns the paid session bought before rung 4 KILLED it. base v2 and"
            " base v3 on eval set E, parsed by the parser that owns each task and scored by"
            " scorer.reader_comment_agreement, called"
        ),
        "no_bar_is_scored": (
            "results/prereg_lora_c.json::bars registers three bars PER ARM and neither arm exists —"
            " the smoke OOMed before a single optimizer step. A bar computed over a base leg would"
            " be a number for a question nobody asked"
        ),
        "population": {
            "eval_set_E": len(e_keys),
            "labelled_by_the_team_lead": len(in_e),
            "holdout_100_rows_inside_E": len(holdout),
            "join": "(thread, msg_id) — a Telegram id is unique inside a channel, not across them",
        },
        "legs": legs,
        "produced_by": {
            "script": "scripts/score_lora_c_bases.py",
            "judge": "market_pulse.scorer.reader_comment_agreement, CALLED",
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
    print(f"wrote {summary.rel(args.out)}")
    print(
        f"  E {record['population']['eval_set_E']} ·"
        f" labelled {record['population']['labelled_by_the_team_lead']} ·"
        f" holdout rows inside E {record['population']['holdout_100_rows_inside_E']}"
    )
    for name, leg in record["legs"].items():
        whole = leg["agreement_on_every_labelled_row_of_E"]
        held = leg["agreement_on_the_holdout_rows_of_E"]
        print(
            f"  {name:<8} parsed {leg['parsed']}/{leg['replies']} · refused {len(leg['refused'])}"
            f" · agreement {whole['agreed']}/{whole['n']} = {whole['rate']:.3f}"
            f" · on holdout rows {held['agreed']}/{held['n']} = {held['rate']:.3f}"
        )
        print(
            "           by class "
            + " · ".join(
                f"{one}: {cell['agreed']}/{cell['n']}" for one, cell in leg["by_class"].items()
            )
        )
        print(f"           mention cell {leg['the_mention_cell']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
