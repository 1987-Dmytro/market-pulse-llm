#!/usr/bin/env python3
"""POST-RUN MEASUREMENT — what probe-b's ten refusals cost, and how much of it is framing.

**This moves no bar and repairs no instrument.** `results/reader_probe_b_verdict.json` is the
registered verdict and stays exactly as it is. What is measured here is the size of the gap between
«the reader was wrong» and «the reply could not be read»: each refused reply is put through a fixed,
ENUMERATED list of container-only repairs — no field is invented, no value is changed, no taxonomy
word is mapped — and the bars are recomputed over the result as a REPORTED number.

The repairs, each one a shape the run actually returned:

1. **two top-level objects.** `{thread, post_summary, discussion_summary}` followed by
   `{entities, signals, per_comment, noise}`. `parse_reply` reads from the first brace, so it sees
   half an answer and reports the other half's first key as missing. Merged.
2. **`signals: {}` / `noise: {}`** — an empty OBJECT where the schema asks for an empty list. Four
   of the five noise threads answered this way, which is exactly where «nothing here» is correct.
3. **a map keyed by the id** — `noise: {"47896": {...}}`. Dv393's shape, one field over.
4. **`aspect: null`** on a signal — dropped, because a signal with no aspect is a signal the schema
   cannot carry and inventing one would be inventing a reading.

`evidence` absent from a `from_post` signal is NOT repaired: an evidence list is what a finding is
made of, and supplying one would be writing the answer.

    PYTHONPATH=src python3 scripts/probe_b_coercion.py
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import score_reader_probe_b as scoring  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import prompts  # noqa: E402

OUT = REPO_ROOT / "results" / "reader_probe_b_coerced.json"
COERCED_EVIDENCE = REPO_ROOT / "results" / "reader_probe_b_coerced.jsonl"

OBJECT_FIELDS = ("entities", "signals", "per_comment", "noise")


def objects(reply: str) -> list[dict]:
    """Every top-level JSON object in the reply, in order — not just the first one."""
    text = reply.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    decoder, found, index = json.JSONDecoder(), [], 0
    while True:
        start = text.find("{", index)
        if start < 0:
            return found
        try:
            value, end = decoder.raw_decode(text[start:])
        except ValueError:
            return found
        if isinstance(value, dict):
            found.append(value)
        index = start + end


def repairs(reply: str) -> tuple[dict | None, list[str]]:
    """The reply with container-only repairs applied, and the list of which ones fired."""
    parts = objects(reply)
    if not parts:
        return None, []
    applied = []
    payload = dict(parts[0])
    for extra in parts[1:]:
        payload.update(extra)
        if "two top-level objects" not in applied:
            applied.append("two top-level objects")
    for field in OBJECT_FIELDS:
        value = payload.get(field)
        if isinstance(value, dict):
            if not value:
                payload[field] = []
                applied.append(f"{field}: empty object -> empty list")
            else:
                # a map keyed by the name or the id — Dv393's shape, one field over
                payload[field] = [
                    {**body, **({"name": key} if field == "entities" else {})}
                    if isinstance(body, dict)
                    else body
                    for key, body in value.items()
                ]
                applied.append(f"{field}: map -> list")
    for signal in payload.get("signals") or []:
        if isinstance(signal, dict) and signal.get("aspect", "") is None:
            signal.pop("aspect")
            applied.append("signals.aspect null -> dropped")
    return payload, applied


def build() -> dict:
    rows = scoring.rows()
    coerced, table = [], []
    for row in rows:
        if row["parsed"]:
            coerced.append(row)
            table.append({"thread": row["thread"], "was": "parsed", "repairs": [], "now": "parsed"})
            continue
        payload, applied = repairs(row["reply"])
        parsed, reason = None, row["parse_error"]
        if payload is not None:
            try:
                parsed = prompts.parse_reply(
                    prompts.READER_TASK_V2, json.dumps(payload, ensure_ascii=False)
                )
                reason = None
            except prompts.ParseError as err:
                reason = err.reason
        coerced.append({**row, "parsed": parsed, "parse_error": reason})
        table.append(
            {
                "thread": row["thread"],
                "was": row["parse_error"],
                "repairs": applied,
                "now": "parsed" if parsed else reason,
            }
        )

    COERCED_EVIDENCE.write_text(
        "\n".join(json.dumps(one, ensure_ascii=False) for one in coerced) + "\n", encoding="utf-8"
    )
    registered = json.loads(
        summary.read_text_or_refuse(REPO_ROOT / "results" / "reader_probe_b_verdict.json")
    )
    scoring.EVIDENCE = COERCED_EVIDENCE
    after = scoring.build()

    def cell(record: dict, bar: str, field: str):
        result = record["bars"][bar]["result"] or {}
        return result.get(field)

    return {
        "class": (
            "POST-RUN MEASUREMENT, reported and never gating. The registered verdict is"
            " results/reader_probe_b_verdict.json and nothing here moves it. This record measures"
            " what the ten refusals cost by applying container-only repairs — no field invented, no"
            " value changed, no taxonomy word mapped"
        ),
        "repairs_allowed": [
            "two top-level objects merged into one",
            "an empty object where the schema asks for an empty list",
            "a map keyed by the name or the id turned into the list it describes",
            "a signal's null aspect dropped rather than invented",
        ],
        "repairs_refused": [
            "an absent `evidence` on a from_post signal — an evidence list is what a finding is"
            " made of, and supplying one would be writing the answer"
        ],
        "per_thread": table,
        "replies": {
            "as_run": {
                "parsed": registered["replies"]["parsed"],
                "refused": registered["replies"]["refused"],
                "by_cause": registered["replies"]["refusals_by_cause"],
            },
            "coerced": {
                "parsed": after["replies"]["parsed"],
                "refused": after["replies"]["refused"],
                "by_cause": after["replies"]["refusals_by_cause"],
            },
            "repairs_that_fired": dict(Counter(one for row in table for one in row["repairs"])),
        },
        "bars": {
            "1_flagships": {
                "as_run": cell(registered, "1_flagships", "cases_answered"),
                "coerced": cell(after, "1_flagships", "cases_answered"),
                "of": 5,
            },
            "2_entity_cases": {
                "as_run": cell(registered, "2_entity_cases", "cases_answered"),
                "coerced": cell(after, "2_entity_cases", "cases_answered"),
                "of": 4,
            },
            "3_noise": {
                "as_run": cell(registered, "3_noise", "signals"),
                "coerced": cell(after, "3_noise", "signals"),
                "reading": (
                    "as run, four of this bar's five threads had no verdict at all, so its zero was"
                    " a count over nothing. The coerced number is the first one computed over five"
                    " actual answers"
                ),
            },
            "4_per_comment_agreement": {
                "as_run": cell(registered, "4_per_comment_agreement", "rate"),
                "coerced": cell(after, "4_per_comment_agreement", "rate"),
                "threshold": 0.80,
            },
        },
        "collapsed_vocabulary": {
            "as_run": registered["collapsed_vocabulary_reading"]["bars"],
            "coerced": after["collapsed_vocabulary_reading"]["bars"],
        },
        "detail": {"coerced_verdict": after["bars"]},
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
        f"  replies as run {record['replies']['as_run']['parsed']}/23 ·"
        f" coerced {record['replies']['coerced']['parsed']}/23"
    )
    print(f"  repairs that fired: {record['replies']['repairs_that_fired']}")
    for name, one in record["bars"].items():
        print(f"  {name:26s} as run {one['as_run']} · coerced {one['coerced']}")
    for row in record["per_thread"]:
        if row["repairs"]:
            print(f"    {row['thread']:28s} {row['was']:34s} -> {row['now']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
