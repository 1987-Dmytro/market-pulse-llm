#!/usr/bin/env python3
"""The sitting's adjudicated answers, written into the up-label batch (4.5g5, Task 1).

Three prompt revisions tried to teach a model what the operator already decided, and the
pre-registered probe killed the last of them. This puts the decisions into the data instead:
where a verdict says outright what a row's label should be, that value goes on the row.

What it will and will not touch:

- **only rulings that name a value.** `expected()` — the same parser the 4.5g3 wave-2 pack
  used — reads the notes that say `unclear should be true`. A note saying a label is
  "unsupported by text" names the error, not the answer, and its row is left alone and listed.
- **plus the two families the guideline settled by pattern.** P5 (promo-mechanics questions)
  and P6 (unmarked support boilerplate) state their value in the rule's prose rather than in
  each row's note, so the parser cannot see them. Their ids come from the guideline's own
  bracket, never from a second list here, and their values are asserted back against the
  guideline text by test.
- **exactly the named fields.** A ruling about `unclear` says nothing about `intents`, so the
  model's `intents` stays. Overwriting the rest would launder unjudged model output as
  adjudicated truth.
- **nothing outside the touched rows.** Untouched lines are copied byte for byte, and the run
  refuses to write unless the set of lines that differ is exactly the set of ids it meant to
  touch.

    PYTHONPATH=src python3 scripts/apply_sitting_verdicts.py --dry-run
    PYTHONPATH=src python3 scripts/apply_sitting_verdicts.py

Rewrites `data/annotation/uplabel_precheck_45g2.jsonl` in place and writes
`results/verdicts_45g5.json`.
"""

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from build_wave2_pack import expected  # noqa: E402  — the 4.5g3 stated-ruling parser, reused
from run_v22_probe import families  # noqa: E402  — the guideline's own P-numbered brackets

from market_pulse import annotation  # noqa: E402

BATCH = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g2.jsonl"
GATES = REPO_ROOT / "results" / "sitting_45g_gates.json"
GUIDELINE = REPO_ROOT / "docs" / "annotation" / "comments.md"
RECORD = REPO_ROOT / "results" / "verdicts_45g5.json"

ANNOTATOR = "sitting-45g-verdicts"
"""What a row carries once a human decision is on it. Deliberately not `sitting-45g`: those are
the 89 rows hand-labelled from images, and these are model rows corrected by a verdict."""

FAMILY_VALUES = {
    "P5": {"intents": ["service"]},
    "P6": {"unclear": True},
}
"""The two rulings the guideline states in prose instead of per row.

P5 is rule 4 of §"Cases the sitting settled" — a promo-mechanics or promo-terms question is
`["service"]`, not `[]`. P6 is rule 2 — unmarked support boilerplate is still the corporate
voice, and is `unclear: true`. Both are grepped back to the guideline by test rather than
trusted here, because a value copied out of prose is a value that can drift from it.
"""

FIELDS = ("sentiment", "sarcasm", "intents", "unclear")


def rel(path: Path) -> str:
    return relabel.rel(path)


def wanted(gates: dict, guideline: Path) -> tuple[dict[str, dict], dict[str, str]]:
    """Every id this run may touch, with the labels its verdict states, and why.

    A row can be named by both its note and a family — `@VARUS_channel:1271` is — and the two
    have to agree. They cannot be merged silently: a family value contradicting the row's own
    note would mean the guideline and the sitting disagree, which is a thing to stop on.
    """
    fams = families(guideline)
    unknown = set(FAMILY_VALUES) - set(fams)
    if unknown:
        raise SystemExit(f"{rel(guideline)} names no {sorted(unknown)} bracket — the law moved")

    want: dict[str, dict] = {}
    why: dict[str, str] = {}
    for row in gates["rows"]:
        if row["verdict"] != "incorrect":
            continue
        stated = expected(row["notes"])
        if stated:
            want[row["id"]] = stated
            why[row["id"]] = "stated in the verdict note"

    for name, ids in fams.items():
        if name not in FAMILY_VALUES:
            continue
        for row_id in ids:
            value = FAMILY_VALUES[name]
            clash = {
                field: (want[row_id][field], setting)
                for field, setting in value.items()
                if row_id in want and field in want[row_id] and want[row_id][field] != setting
            }
            if clash:
                raise SystemExit(f"{row_id}: verdict note and family {name} disagree — {clash}")
            want.setdefault(row_id, {}).update(value)
            why[row_id] = f"{why[row_id]}; pattern {name}" if row_id in why else f"pattern {name}"
    return want, why


def refused_without_a_value(gates: dict, want: dict) -> list[dict]:
    """The refused rows this run leaves alone, each with the note that refused it."""
    return [
        {"id": row["id"], "notes": row["notes"]}
        for row in gates["rows"]
        if row["verdict"] == "incorrect" and row["id"] not in want
    ]


def note_for(labels: dict, reason: str) -> str:
    """One line saying which ruling moved this row and to what."""
    stated = ", ".join(
        f"{field}={json.dumps(labels[field])}" for field in FIELDS if field in labels
    )
    return f"4.5g5: sitting-45g verdict applied ({reason}) — {stated}. Source: {rel(GATES)}"


def apply(lines: list[str], want: dict, why: dict) -> tuple[list[str], list[dict]]:
    """The rewritten file and one record per touched row. Untouched lines are the same objects."""
    out, touched = list(lines), []
    seen = {}
    for index, line in enumerate(lines):
        row = json.loads(line)
        seen[row["id"]] = index
        labels = want.get(row["id"])
        if labels is None:
            continue
        before = {field: row[field] for field in FIELDS}
        after = {**row, **labels, "annotator": ANNOTATOR, "notes": note_for(labels, why[row["id"]])}
        bad = annotation.check_labels(after, "comments")
        if bad:
            raise SystemExit(f"{row['id']}: the verdict produces an illegal row — {bad}")
        out[index] = json.dumps(after, ensure_ascii=False)
        touched.append(
            {
                "id": row["id"],
                "reason": why[row["id"]],
                "fields": sorted(labels),
                "before": before,
                "after": {field: after[field] for field in FIELDS},
                "moved": any(before[field] != after[field] for field in labels),
            }
        )

    missing = sorted(set(want) - set(seen))
    if missing:
        raise SystemExit(f"{len(missing)} adjudicated ids are not in the batch: {missing}")
    return out, touched


def differing(before: list[str], after: list[str]) -> list[int]:
    """Line numbers that changed — the only claim worth making about a diff."""
    if len(before) != len(after):
        raise SystemExit(f"line count moved: {len(before)} -> {len(after)}")
    return [i for i, (old, new) in enumerate(zip(before, after)) if old != new]


def counts(touched: list[dict]) -> dict:
    """Per-field and per-reason totals, derived from the rows rather than typed."""
    per_field = Counter(field for row in touched for field in row["fields"])
    return {
        "rows_touched": len(touched),
        "rows_moved": sum(1 for row in touched if row["moved"]),
        "rows_already_matching": sum(1 for row in touched if not row["moved"]),
        "per_field": dict(sorted(per_field.items())),
        "by_reason": dict(sorted(Counter(row["reason"] for row in touched).items())),
    }


def population(rows: list[dict]) -> dict:
    """What the batch is after the write, counted the same way before and after."""
    return {
        "rows": len(rows),
        "by_annotator": dict(sorted(Counter(row["annotator"] for row in rows).items())),
        "unclear_true": sum(1 for row in rows if row["unclear"]),
        "with_no_intent": sum(1 for row in rows if not row["intents"]),
        "intents": dict(sorted(Counter(i for row in rows for i in row["intents"]).items())),
        "sarcasm_true": sum(1 for row in rows if row["sarcasm"]),
        "sentiment": dict(sorted(Counter(row["sentiment"] for row in rows).items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report, write nothing")
    parser.add_argument("--batch", type=Path, default=BATCH)
    parser.add_argument("--gates", type=Path, default=GATES)
    parser.add_argument("--guideline", type=Path, default=GUIDELINE)
    parser.add_argument("--record", type=Path, default=RECORD)
    args = parser.parse_args()

    gates = json.loads(args.gates.read_text(encoding="utf-8"))
    want, why = wanted(gates, args.guideline)
    skipped = refused_without_a_value(gates, want)

    lines = args.batch.read_text(encoding="utf-8").splitlines()
    before = [json.loads(line) for line in lines]
    rewritten, touched = apply(lines, want, why)

    # A rerun changes nothing, and "nothing changed" would otherwise be reported as the
    # diff guard failing, which reads like a defect rather than like an idempotent no-op.
    done = [item for item in before if item["id"] in want and item["annotator"] == ANNOTATOR]
    if want and len(done) == len(want):
        raise SystemExit(f"{rel(args.batch)}: these verdicts are already on it — nothing to apply")

    changed = differing(lines, rewritten)
    intended = sorted(json.loads(lines[i])["id"] for i in changed)
    if intended != sorted(row["id"] for row in touched):
        raise SystemExit("the changed lines are not the rows this run meant to touch")

    after = [json.loads(line) for line in rewritten]
    record = {
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "applied_by": "scripts/apply_sitting_verdicts.py",
        "authority": "team-lead-LLM triage with operator adjudication and operator spot-check",
        "batch": rel(args.batch),
        "gates": rel(args.gates),
        "guideline": rel(args.guideline),
        "annotator": ANNOTATOR,
        "scope": (
            "rulings that name a value: the parseable stated rulings of "
            f"{rel(args.gates)} plus the P5/P6 family values the guideline states in prose"
        ),
        "batch_sha256_before": sha256("\n".join(lines).encode() + b"\n").hexdigest(),
        "batch_sha256_after": sha256("\n".join(rewritten).encode() + b"\n").hexdigest(),
        "supersedes": {
            "manifest": "results/sitting_45g2_manifest.json",
            "what_moved": (
                "That manifest pins precheck.source_sha256 to the batch as it was sealed for the "
                "sitting, and this run moved 35 of its rows. The pin is now stale by design and "
                "is not to be re-pinned: it describes the corpus the 300 verdicts were passed on, "
                "and this file is the only place the chain to today's bytes is written down. "
                "scripts/build_sitting_pack.py will refuse against the new bytes, and that "
                "refusal is correct — the same shape results/relabel_45e.json records for "
                "results/calib_45e_manifest.json."
            ),
        },
        "counts": counts(touched),
        "refused_rows": len([r for r in gates["rows"] if r["verdict"] == "incorrect"]),
        "skipped_no_value": skipped,
        "changed_lines": len(changed),
        "population_before": population(before),
        "population_after": population(after),
        "rows": touched,
        "git": git_state(args.record),
    }

    print(f"{rel(args.batch)}: {len(touched)} rows touched, {len(changed)} lines changed")
    print(
        f"  moved {record['counts']['rows_moved']}, already matching "
        f"{record['counts']['rows_already_matching']}"
    )
    print(f"  per field: {record['counts']['per_field']}")
    print(f"  left alone (verdict names no value): {len(skipped)}")
    for row in skipped:
        print(f"    {row['id']}: {row['notes'][:90]}")

    if args.dry_run:
        print("dry run — nothing written")
        return 0

    args.batch.write_text("\n".join(rewritten) + "\n", encoding="utf-8")
    relabel.append_record(args.record, record)
    print(f"wrote {rel(args.batch)} and {rel(args.record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
