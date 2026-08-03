#!/usr/bin/env python3
"""The six verdicts the team lead read out of the notes, written onto their rows (4.5g6, Task 1).

4.5g5 applied every ruling a parser could read a value out of and left seven rows alone, each
because its note named the error without naming the answer in a form the parser takes. The team
lead has now read six of those answers out by hand. This transcribes them — it does not derive
them: the values below are the ones `docs/PROMPT-4.5g6.md` §Task 1 dictates, and the only thing
this file decides is whether they are legal to write.

What it guards:

- **transcription, not interpretation.** Every intent this dictates has to appear as a word in
  that row's own verdict note (`results/sitting_45g_gates.json`), so a mistyped label fails here
  rather than becoming adjudicated truth. The check is a test as well as a run-time assert.
- **exactly the named fields.** `@VARUS_channel:9271` already carries `unclear: false` from
  4.5g5; this adds `intents` and leaves the rest, and its note gains a clause rather than losing
  the one that says where `unclear` came from.
- **the chain.** The batch's sha256 before this run has to be the sha256 4.5g5 recorded when it
  finished. Two hands on one file is exactly what the record exists to make visible.
- **the rows nobody dictated.** `@VARUS_channel:7555` (the note names no value) and
  `@msuaaaa:11876` (pending law, operator decision of 03.08) stay untouched and are listed.

    PYTHONPATH=src python3 scripts/apply_dictated_verdicts.py --dry-run
    PYTHONPATH=src python3 scripts/apply_dictated_verdicts.py

Rewrites `data/annotation/uplabel_precheck_45g2.jsonl` in place and writes
`results/verdicts_45g6.json`.
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import apply_sitting_verdicts as verdicts  # noqa: E402
import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

BATCH = verdicts.BATCH
GATES = verdicts.GATES
PRIOR = REPO_ROOT / "results" / "verdicts_45g5.json"
RECORD = REPO_ROOT / "results" / "verdicts_45g6.json"

ANNOTATOR = verdicts.ANNOTATOR
FIELDS = verdicts.FIELDS

DICTATED = {
    "@VARUS_channel:8478": {"intents": ["service"]},
    "@VARUS_channel:14759": {"intents": ["availability"]},
    "@VARUS_channel:11615": {"intents": ["taste"]},
    "@VARUS_channel:18839": {"intents": ["service"]},
    "@VARUS_channel:8932": {"intents": ["quality", "taste"]},
    "@VARUS_channel:9271": {"intents": ["service"]},
}
"""`docs/PROMPT-4.5g6.md` §Task 1, transcribed field for field.

Six rows and one field each, because that is what the team lead named. A seventh row of the
4.5g5 skip list (`@VARUS_channel:7555`) still has no stated value, and an eighth
(`@msuaaaa:11876`) is held pending law — neither is guessed at here."""

UNTOUCHED = ("@VARUS_channel:7555", "@msuaaaa:11876")
"""The refusals that stay unadjudicated, named so the count can be asserted rather than eyeballed."""

REASON = "dictated by the team lead from the verdict note (docs/PROMPT-4.5g6.md Task 1)"


def rel(path: Path) -> str:
    return relabel.rel(path)


def transcribed(want: dict, gates: dict) -> dict[str, str]:
    """Each dictated row's own verdict note — after checking the dictated values appear in it.

    The one failure a dictation has is a typo, and a typo is invisible: `["service"]` for
    `["availability"]` is a legal row, passes `check_labels`, and becomes truth. So every label
    written here has to be a word the note that ruled on the row already contains.
    """
    notes = {row["id"]: row["notes"] for row in gates["rows"] if row["verdict"] == "incorrect"}
    missing = sorted(set(want) - set(notes))
    if missing:
        raise SystemExit(f"{missing} are not refused rows of {rel(GATES)} — nothing ruled on them")
    for row_id, labels in want.items():
        unsupported = [
            value for value in labels.get("intents", []) if value not in notes[row_id].casefold()
        ]
        if unsupported:
            raise SystemExit(
                f"{row_id}: dictated {unsupported} but its verdict note never says the word —"
                f" transcribe the note, do not interpret it. Note: {notes[row_id]}"
            )
    return {row_id: notes[row_id] for row_id in want}


def note_for(labels: dict, reason: str, row: dict) -> str:
    """This run's clause, appended to whatever an earlier run wrote rather than over it.

    `@VARUS_channel:9271` carries the 4.5g5 note saying where its `unclear` came from. Replacing
    it would leave a row with two adjudicated fields and a note explaining one of them.
    """
    mine = (
        f"4.5g6: sitting-45g verdict applied ({reason}) —"
        f" {verdicts.stated_as(labels)}. Source: {rel(GATES)}"
    )
    earlier = (row.get("notes") or "").strip()
    return f"{earlier} | {mine}" if earlier else mine


def already_applied(rows: list[dict], want: dict) -> list[str]:
    """The dictated rows whose fields already hold the dictated values."""
    at = {row["id"]: row for row in rows}
    return sorted(
        row_id
        for row_id, labels in want.items()
        if row_id in at and all(at[row_id][field] == value for field, value in labels.items())
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report, write nothing")
    parser.add_argument("--batch", type=Path, default=BATCH)
    parser.add_argument("--gates", type=Path, default=GATES)
    parser.add_argument("--prior", type=Path, default=PRIOR)
    parser.add_argument("--record", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    gates = json.loads(args.gates.read_text(encoding="utf-8"))
    want = {row_id: dict(labels) for row_id, labels in DICTATED.items()}
    notes = transcribed(want, gates)
    why = dict.fromkeys(want, REASON)

    lines = args.batch.read_text(encoding="utf-8").splitlines()
    before = [json.loads(line) for line in lines]

    # "is there work to do" is asked before "is this the file I expect": after a successful run
    # the batch legitimately no longer matches 4.5g5's sha, and a rerun must say so as an
    # idempotent no-op rather than as a broken chain.
    if len(already_applied(before, want)) == len(want):
        raise SystemExit(f"{rel(args.batch)}: these verdicts are already on it — nothing to apply")

    # the chain: these six land on the file 4.5g5 left behind, not on some other copy of it
    chained_from = json.loads(args.prior.read_text(encoding="utf-8"))["runs"][-1]
    sha_before = sha256("\n".join(lines).encode() + b"\n").hexdigest()
    if sha_before != chained_from["batch_sha256_after"]:
        raise SystemExit(
            f"{rel(args.batch)} is {sha_before[:16]}… and {rel(args.prior)} left it at"
            f" {chained_from['batch_sha256_after'][:16]}…. Something else wrote to the batch"
            " between the two runs — stop and report."
        )

    rewritten, touched = verdicts.apply(lines, want, why, note=note_for)
    changed = verdicts.differing(lines, rewritten)
    intended = sorted(json.loads(lines[i])["id"] for i in changed)
    if intended != sorted(want):
        raise SystemExit("the changed lines are not the rows this run meant to touch")

    refused = [row["id"] for row in gates["rows"] if row["verdict"] == "incorrect"]
    adjudicated = {row["id"] for row in chained_from["rows"]} | set(want)
    still_open = sorted(set(refused) - adjudicated)
    if still_open != sorted(UNTOUCHED):
        raise SystemExit(
            f"refusals left unadjudicated are {still_open}, expected {list(UNTOUCHED)}"
        )

    after = [json.loads(line) for line in rewritten]
    record = {
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "applied_by": "scripts/apply_dictated_verdicts.py",
        "authority": (
            "team-lead dictation in docs/PROMPT-4.5g6.md Task 1, transcribed field for field;"
            " every dictated value read back to the row's own verdict note"
        ),
        "batch": rel(args.batch),
        "gates": rel(args.gates),
        "annotator": ANNOTATOR,
        "scope": "the six rulings the team lead read out of the notes 4.5g5 could not parse",
        "batch_sha256_before": sha_before,
        "batch_sha256_after": sha256("\n".join(rewritten).encode() + b"\n").hexdigest(),
        "chained_from": {
            "record": rel(args.prior),
            "timestamp": chained_from["timestamp"],
            "batch_sha256_after": chained_from["batch_sha256_after"],
            "rows": len(chained_from["rows"]),
        },
        "supersedes": chained_from["supersedes"],
        "counts": verdicts.counts(touched),
        "refused_rows": len(refused),
        "adjudicated_so_far": len(adjudicated),
        "still_unadjudicated": [
            {"id": row["id"], "notes": row["notes"]}
            for row in gates["rows"]
            if row["id"] in set(still_open)
        ],
        "source_notes": notes,
        "changed_lines": len(changed),
        "population_before": verdicts.population(before),
        "population_after": verdicts.population(after),
        "rows": touched,
        "git": git_state(args.record),
    }

    print(f"{rel(args.batch)}: {len(touched)} rows touched, {len(changed)} lines changed")
    print(f"  per field: {record['counts']['per_field']}")
    for row in touched:
        print(f"    {row['id']:<24} {row['before']['intents']} -> {row['after']['intents']}")
    print(
        f"  adjudicated {len(adjudicated)} of {len(refused)} refusals; still open:"
        f" {', '.join(still_open)}"
    )
    if args.dry_run:
        print("dry run — nothing written")
        return 0

    args.batch.write_text("\n".join(rewritten) + "\n", encoding="utf-8")
    relabel.append_record(args.record, record)
    print(f"wrote {rel(args.batch)} and {rel(args.record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
