#!/usr/bin/env python3
"""The three operator rulings from the calibration diagnostic, applied (4.5f).

The gated hundred accepted the re-label; the diagnostic fifty disagreed on three
rows, and those three are law for their rows. They are not a guideline change —
two are the same failure (a short reply under a poll-style post, whose intent
lives in a parent the re-labeller never sees) and the third was dictated in chat.

What this refuses:

- **a ruling with no authority behind it.** Every id must carry the stated
  non-`new` verdict in `results/calib_45e_verdict.json`, which is the artifact the
  reader derived from the operator's own file. A constant in this script that no
  returned cell backs is a label invented here.
- **`old` that is not the old value.** A row ruled `old` takes the v1 label out of
  its *source* file, compared against the ruling as written. A transcription slip
  would otherwise put a plausible label in under the operator's name.
- **more than one column moving.** Each rewritten line has to reproduce its staged
  line byte for byte once the previous intents are put back.
- **a second run doing it again.** A row already carrying its ruling is counted as
  applied, not applied twice, and a run that changes nothing writes nothing.

    PYTHONPATH=src python3 scripts/apply_calibration_rulings.py

Rewrites the staged `_tax2` files, intents column only, and appends a `fixes`
block to `results/relabel_45e.json`. The drift block there is the re-labeller's
own output and is never recomputed.
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))  # the staging convention lives there

import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

VERDICTS = REPO_ROOT / "results" / "calib_45e_verdict.json"
RECORD = REPO_ROOT / "results" / "relabel_45e.json"

RULINGS = (
    {
        "id": "@VARUS_channel:11972",
        "intents": ["taste"],
        "verdict": "old",
        "authority": (
            "operator diagnostic verdict `old` — the v1 label was right, and the row is"
            " a reply under a poll-style post that the re-labeller does not see"
        ),
    },
    {
        "id": "@VARUS_channel:11960",
        "intents": ["taste"],
        "verdict": "old",
        "authority": (
            "operator diagnostic verdict `old` — same class as 11972: a two-word reply"
            " whose intent is in the parent post"
        ),
    },
    {
        "id": "@VARUS_channel:11902",
        "intents": ["taste"],
        "verdict": "neither",
        "authority": (
            "operator diagnostic verdict `neither`, correct set dictated in chat"
            " 2026-08-02 and transcribed by the team lead into the notes cell of"
            " changed.csv and docs/STATUS.md — notes are free text and are never"
            " validated, so the ruling is carried by this table and the verdict cell"
        ),
    },
)
"""The three rows, their new labels, and what makes each one law.

A `neither` ruling names a label no cell contains, so its value can only come from
the dictation; an `old` ruling names the v1 label, and that one is checked against
the source file rather than trusted."""


def body(lines: list[str]) -> str:
    return "".join(line + "\n" for line in lines)


def index(paths: dict[str, Path]) -> dict[str, tuple[str, int]]:
    """id -> (file key, position). Two files claiming one id is a stop, not a pick."""
    where: dict[str, tuple[str, int]] = {}
    for key, path in paths.items():
        for position, row in enumerate(relabel.load(path)[0]):
            if row["id"] in where:
                raise SystemExit(
                    f"{row['id']} is in both {where[row['id']][0]} and {key} — a ruling cannot"
                    " name one row when two files claim the id."
                )
            where[row["id"]] = (key, position)
    return where


def authorised(verdicts: dict) -> dict[str, dict]:
    """The operator's diagnostic verdicts, keyed by id — the authority for the rulings."""
    return {row["id"]: row for row in verdicts["rows"]["changed"]}


def apply_all(rulings, verdicts: dict, staged: dict[str, Path], sources: dict[str, Path]) -> dict:
    """Every ruling checked against its authority and written — or a stop naming why not."""
    ruled = authorised(verdicts)
    source_rows = {
        key: {row["id"]: row for row in relabel.load(path)[0]} for key, path in sources.items()
    }
    where = index(staged)
    loaded = {key: relabel.load(path) for key, path in staged.items()}
    for key, path in staged.items():
        # `load` drops blank lines, so joining them back is only lossless if there were
        # none. Proved here rather than assumed: this run rewrites the whole file.
        if body(loaded[key][1]) != path.read_text(encoding="utf-8"):
            raise SystemExit(
                f"{relabel.rel(path)}: its lines do not join back into the file it was read"
                " from, so rewriting it would change lines no ruling names."
            )
    touched: dict[str, list[str]] = {}
    applied, matching = [], []

    for ruling in rulings:
        row_id, wanted = ruling["id"], sorted(ruling["intents"])
        returned = ruled.get(row_id)
        if returned is None or returned["verdict"] != ruling["verdict"]:
            raise SystemExit(
                f"{row_id}: {relabel.rel(VERDICTS)} has"
                f" {returned and returned['verdict']!r} where this ruling claims"
                f" {ruling['verdict']!r}. A ruling no returned cell backs is a label"
                " invented here."
            )
        if row_id not in where:
            raise SystemExit(f"{row_id}: not in any staged file — there is nothing to rule on")
        key, position = where[row_id]
        if ruling["verdict"] == "old":
            was = sorted(source_rows[key][row_id]["intents"])
            if was != wanted:
                raise SystemExit(
                    f"{row_id}: ruled `old`, but the v1 label in {relabel.rel(sources[key])} is"
                    f" {was} and this ruling writes {wanted}. `old` means the old value."
                )

        rows, lines = loaded[key]
        row, line = rows[position], lines[position]
        before = sorted(row["intents"])
        if before == wanted:
            matching.append({**ruling, "file": relabel.rel(staged[key])})
            continue
        lines[position] = relabel.relabelled(row, line, wanted)
        rows[position] = {**row, "intents": wanted}
        touched.setdefault(key, []).append(row_id)
        applied.append(
            {
                "id": row_id,
                "file": relabel.rel(staged[key]),
                "old": before,
                "new": wanted,
                "verdict": ruling["verdict"],
                "authority": ruling["authority"],
            }
        )
        print(f"  {row_id}  {before} -> {wanted}   ({relabel.rel(staged[key])})")

    before_sha = {relabel.rel(staged[key]): digest(staged[key]) for key in touched}
    for key in touched:
        staged[key].write_text(body(loaded[key][1]), encoding="utf-8")
    after_sha = {relabel.rel(staged[key]): digest(staged[key]) for key in touched}
    return {"applied": applied, "matching": matching, "before": before_sha, "after": after_sha}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verdicts", type=Path, default=VERDICTS)
    parser.add_argument("--record", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    verdicts = json.loads(args.verdicts.read_text(encoding="utf-8"))
    staged = {key: relabel.staged(path) for key, path in relabel.SOURCES.items()}
    print(f"{len(RULINGS)} rulings from {relabel.rel(args.verdicts)}:")
    outcome = apply_all(RULINGS, verdicts, staged, relabel.SOURCES)

    for ruling in outcome["matching"]:
        print(f"  {ruling['id']}  already {sorted(ruling['intents'])} — nothing to apply")
    if not outcome["applied"]:
        print("nothing changed, so nothing is recorded")
        return 0

    history = json.loads(args.record.read_text(encoding="utf-8"))
    history.setdefault("fixes", []).append(
        {
            "applied_by": "scripts/apply_calibration_rulings.py",
            "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
            "authority": relabel.rel(args.verdicts),
            "rows": outcome["applied"],
            "staged_sha256_before": outcome["before"],
            "staged_sha256_after": outcome["after"],
            "note": (
                "Operator rulings applied to the intents column of the staged files after the"
                " run above. The drift and churn in `runs` are the re-labeller's own output and"
                " are deliberately NOT recomputed: they are what the calibration judged, and a"
                " block silently corrected by its own verdicts stops describing the thing that"
                " was verdicted. `results/calib_45e_manifest.json` pins the staged bytes as they"
                " were sealed; `staged_sha256_after` is where they are now."
            ),
            "git": git_state(args.record),
        }
    )
    relabel.write_json(args.record, history)
    print(
        f"\n{len(outcome['applied'])} row(s) rewritten, intents only ·"
        f" {len(outcome['matching'])} already matching\nrecorded in {relabel.rel(args.record)}"
        " as a `fixes` block — the drift block is untouched"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
