#!/usr/bin/env python3
"""The gate on `docs/labels-pass1-r1.jsonl` — it refuses, prints a distribution, and writes nothing.

**Why a validator and not a reader.** The labels are the TEAM LEAD's file and the executor never
edits it ([[team_lead_owns_the_docs]]), so the only thing that can be done about a bad row is to
REFUSE it and say which row and why. Four ways a labels file can be wrong, and each one is a named
refusal rather than a repair:

* a drawn unit is not answered, or is answered twice — the pack is 500 units and a training set
  built from 499 of them is a different experiment;
* a `subject_type` outside the four readings plus `null` — including the STRING `"null"`, which is
  a value nothing downstream can read;
* a `(thread, msg_id)` that is not in the pack — a row invented, mistyped, or carried in from
  somewhere else;
* a row from one of the excluded threads — the exam, named separately from the line above because
  it is the one defect the honesty frame exists to prevent.

An absent `subject_type` key is NOT `null`: `null` is an answer («this comment is about nobody»)
and a missing key is a row nobody looked at, so they are refused apart.

    PYTHONPATH=src python3.11 scripts/validate_pass1_labels.py docs/labels-pass1-r1.jsonl
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse import prompts  # noqa: E402

PACK = REPO_ROOT / "results" / "pass1_label_pack_r1.json"
LABELS = REPO_ROOT / "docs" / "labels-pass1-r1.jsonl"

VALUES = (*prompts.PASS1_SUBJECT_TYPES, None)
"""The four readings and `null` — from the module the pass-1 prompt answers under, never retyped."""


def read_rows(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as bad:
            raise SystemExit(f"line {number} is not one JSON object: {bad}") from bad
        if not isinstance(row, dict):
            raise SystemExit(f"line {number} is {type(row).__name__} and not an object")
        row["_line"] = number
        rows.append(row)
    return rows


def validate(rows: list[dict], pack: dict) -> dict[str, int]:
    """Refuse on the first class of defect found, naming the rows. Returns the distribution."""
    units = [(one["thread"], int(one["msg_id"])) for one in pack["units"]]
    expected = set(units)
    excluded = set(pack["exclusion"]["threads"])

    missing_field = [
        row["_line"] for row in rows if not {"thread", "msg_id", "subject_type"} <= set(row)
    ]
    if missing_field:
        raise SystemExit(
            f"{len(missing_field)} rows are missing one of thread/msg_id/subject_type, first at"
            f" line {missing_field[0]}. An absent subject_type is not null — null is an answer"
        )

    contaminated = [row for row in rows if row["thread"] in excluded]
    if contaminated:
        raise SystemExit(
            f"{len(contaminated)} rows come from EXCLUDED threads, first"
            f" {contaminated[0]['thread']}:{contaminated[0]['msg_id']} at line"
            f" {contaminated[0]['_line']}. Those threads carry the 64 registered probe units and"
            " the 14 gold rows — this file must never label one"
        )

    answered = [(row["thread"], int(row["msg_id"])) for row in rows]
    unknown = [one for one in answered if one not in expected]
    if unknown:
        raise SystemExit(
            f"{len(unknown)} rows are not units of the pack, first {unknown[0][0]}:{unknown[0][1]}."
            f" Every (thread, msg_id) must be one of the {len(expected)} drawn"
        )

    seen: dict[tuple[str, int], int] = {}
    for one in answered:
        seen[one] = seen.get(one, 0) + 1
    twice = sorted(one for one, count in seen.items() if count > 1)
    if twice:
        raise SystemExit(
            f"{len(twice)} units are answered more than once, first {twice[0][0]}:{twice[0][1]}."
            " Every drawn unit is answered exactly once"
        )
    absent = [one for one in units if one not in seen]
    if absent:
        raise SystemExit(
            f"{len(absent)} of {len(units)} drawn units are not answered, first"
            f" {absent[0][0]}:{absent[0][1]}. A pack labelled in part is a different pack"
        )

    off = [row for row in rows if row["subject_type"] not in VALUES]
    if off:
        raise SystemExit(
            f"{len(off)} rows carry a subject_type outside the taxonomy, first"
            f" {off[0]['subject_type']!r} at line {off[0]['_line']}. The domain is"
            f" {', '.join(str(one) for one in VALUES)} — and JSON null, never the string 'null'"
        )

    distribution: dict[str, int] = {}
    for row in rows:
        key = "null" if row["subject_type"] is None else row["subject_type"]
        distribution[key] = distribution.get(key, 0) + 1
    return distribution


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("labels", nargs="?", type=Path, default=LABELS)
    parser.add_argument("--pack", type=Path, default=PACK)
    args = parser.parse_args(argv)
    if not args.labels.exists():
        raise SystemExit(
            f"no labels file at {args.labels}. The TEAM LEAD writes it; nothing here does"
        )
    pack = json.loads(args.pack.read_text(encoding="utf-8"))
    rows = read_rows(args.labels)
    distribution = validate(rows, pack)
    print(f"OK — {len(rows)} rows, every one of {len(pack['units'])} drawn units answered once")
    width = max(len(one) for one in distribution)
    for value in sorted(distribution, key=lambda one: (-distribution[one], one)):
        count = distribution[value]
        print(f"  {value:<{width}}  {count:>4}   {count / len(rows):6.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
