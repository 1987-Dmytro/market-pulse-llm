#!/usr/bin/env python3
"""What the sitting decided, written into the staged taxonomy-v2 files (4.5g3).

Three questions came back from one sitting and they merge on different terms:

- **the up-label precheck** merges only per stratum, and only the strata that passed. Its
  rows are model output until a stratum's agreement clears the bar registered before the pack
  went out; `results/sitting_45g_gates.json` is the only thing allowed to say which did.
- **the 75 emptied rows** are hand-decided labels for rows the 4.5e re-label emptied. They go
  into the `intents` column of the staged `_tax2` copies, where the re-labeller's answer for
  them is.
- **the 14 unreadable rows** were never in a staged file at all: the re-labeller refused them
  four passes running, so they stayed on their v1 labels. Now that the column is filled they
  join, in their source file's own row order.

What it refuses:

- **merging a stratum on the corpus average.** Each stratum is read from the gate record by
  name, and a passed one stops this run rather than being merged blind — where an accepted
  up-label row lands is a decision nobody has taken, and none of the 1,912 ids is in any
  source file today.
- **a returned file that is not the one the pack sealed.** Row for row, the ids and the two
  frozen cells (`text`, the v1 label) have to be what this repo derives for them.
- **a half-filled column.** `[]` is an answer and empty is not, so every cell is required to
  parse as a JSON list — a truthiness test would read 40 rows of `[]` as unfilled.
- **more than the three columns it names.** Each rewritten line has to reproduce its staged
  line byte for byte once `intents`, `notes` and `annotator` are put back.
- **a population that stops deriving.** The 97 are re-derived after the writes, with this
  run's own fix block in the history, and have to still be 97.

    PYTHONPATH=src python3 scripts/merge_sitting_returns.py --dry-run
    PYTHONPATH=src python3 scripts/merge_sitting_returns.py

Rewrites the staged `_tax2` files, writes `results/merge_45g3.json` and appends one `fixes`
block to `results/relabel_45e.json`.
"""

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_sitting_pack as builder  # noqa: E402
import measure_empty_drop as drop  # noqa: E402
import relabel_intents as relabel  # noqa: E402
from apply_calibration_rulings import body, digest, index  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from read_sitting_returns import PROVENANCE  # noqa: E402  (one home for what wrote the verdicts)
from relabel_emptied import population  # noqa: E402
from market_pulse import annotation  # noqa: E402

GATES = REPO_ROOT / "results" / "sitting_45g_gates.json"
MANIFEST = REPO_ROOT / "results" / "sitting_45g2_manifest.json"
MICRO_MANIFEST = REPO_ROOT / "results" / "calib_45e_micro_manifest.json"
DROP = REPO_ROOT / "results" / "drop_45f.json"
RELABEL_RECORD = REPO_ROOT / "results" / "relabel_45e.json"
QUIZ_RECORD = REPO_ROOT / "results" / "quiz_rulings_45g2.json"
RECORD = REPO_ROOT / "results" / "merge_45g3.json"

APPLIED_BY = "scripts/merge_sitting_returns.py"
ANNOTATOR = "sitting-45g"
"""What the merged rows say produced their label. The staged rows carried `llm-precheck`,
`llm-holdout` or `llm-recheck-v2`, which named the run that wrote the label being replaced;
leaving it would describe these rows as model output after a human decided them."""

FIELDS = ("intents", "notes", "annotator")
"""The three columns this merge may move, and the three a rewritten line has to reproduce
its source in once they are put back."""


def rel(path: Path) -> str:
    return relabel.rel(path)


def csv_rows(path: Path, delimiter: str = builder.DELIMITER) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{rel(path)}: not found — the sitting's returns are not here")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def as_intents(cell: str, where: str) -> list[str]:
    """One filled cell as a label set. `[]` is an answer; blank is not, and neither is prose."""
    text = (cell or "").strip()
    if not text:
        raise SystemExit(
            f"{where}: the cell is empty. `[]` is a full answer and empty is a row nobody"
            " decided, so this merge stops rather than reading one as the other."
        )
    try:
        value = json.loads(text)
    except ValueError:
        raise SystemExit(f"{where}: {text!r} is not a JSON list") from None
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SystemExit(f"{where}: {text!r} is not a list of labels")
    return sorted(set(value))


def rewritten(row: dict, line: str, changes: dict) -> str:
    """The row with `changes` applied — proved by putting the old values back.

    `relabel.relabelled`'s discipline over three columns rather than one: a field-by-field
    comparison would miss key order, spacing and escaping, and the only statement worth making
    is that this line differs from its source in exactly the values named here.
    """
    produced = json.dumps({**row, **changes}, ensure_ascii=False)
    back = {**json.loads(produced), **{field: row[field] for field in changes}}
    if json.dumps(back, ensure_ascii=False) != line:
        raise SystemExit(
            f"{row['id']}: restoring {sorted(changes)} does not reproduce the staged line byte"
            " for byte, so this merge changed more than the columns it names. Stop and report."
        )
    return produced


def note_for(returned: str, existing: str) -> str:
    """The sitting's own note, kept whole — it carries the per-row authorship Amendment 2 asks
    for (`tl-llm` / `verdict: operator`) — behind whatever the row already said."""
    mine = f"{ANNOTATOR}: {returned.strip()}" if returned.strip() else ANNOTATOR
    return f"{existing.strip()}; {mine}" if existing.strip() else mine


def gate_verdicts(path: Path, manifest_path: Path) -> dict:
    """The gate record, checked to be about this manifest before a stratum name is read."""
    if not path.exists():
        raise SystemExit(
            f"{rel(path)}: not found — run scripts/read_sitting_returns.py first. Which strata"
            " passed is not a thing this script is allowed to work out for itself."
        )
    record = json.loads(path.read_text(encoding="utf-8"))
    if record["manifest"] != rel(manifest_path):
        raise SystemExit(
            f"{rel(path)} reads {record['manifest']} and this run was given"
            f" {rel(manifest_path)} — two sittings, and the strata do not transfer."
        )
    return record


def uplabel_scope(gates: dict) -> list[str]:
    """The strata whose whole population the up-label precheck merges — or a stop.

    Nothing merged in 4.5g3: all three strata came back under the bar. The path is deliberately
    unbuilt rather than written blind, because none of the 1,912 precheck ids exists in any
    source file today, so accepting one is a decision about which file it joins and under what
    annotator — and with nothing to exercise it, code written for that would be guesswork
    shipped into the one place a mistake is unrecoverable.
    """
    if gates["passed"]:
        raise SystemExit(
            f"{gates['passed']} passed the bar and their rows are not merged here. The 1,912"
            " precheck rows are in no source file, so accepting a stratum means deciding which"
            " file its rows join and under which annotator; 4.5g3 had no passing stratum to"
            " build that against and refuses to invent it. Take the decision, then extend this."
        )
    return []


def redo_ingest(path: Path, derived: dict, staged_rows: dict) -> list[dict]:
    """The 75 hand-decided rows, checked against what this repo derives for them."""
    rows = csv_rows(path)
    if {row["id"] for row in rows} != set(derived):
        raise SystemExit(
            f"{rel(path)} holds {len(rows)} ids and the emptied population still open derives as"
            f" {len(derived)}. The returned file is not the pack that went out."
        )
    out = []
    for row in rows:
        row_id = row["id"]
        staged = staged_rows[row_id]
        if row["text"] != staged["text"]:
            raise SystemExit(f"{row_id}: the returned text is not the staged row's text")
        if json.loads(row["intents_v1"]) != derived[row_id]["before"]:
            raise SystemExit(
                f"{row_id}: the returned intents_v1 is {row['intents_v1']} and the v1 label"
                f" derives as {derived[row_id]['before']} — the file describes other rows."
            )
        out.append(
            {
                "id": row_id,
                "intents": as_intents(row["intents_final"], f"{path.name}:{row_id}"),
                "notes": row["notes"] or "",
            }
        )
    return out


def unreadable_ingest(path: Path, micro: dict, source_rows: dict) -> list[dict]:
    """The 14 rows the re-labeller never answered, now that their column is filled."""
    rows = csv_rows(path)
    if [row["id"] for row in rows] != micro["ids"]:
        raise SystemExit(
            f"{rel(path)}: its ids are not the ones {micro['pack']} was sealed with, in order."
        )
    out = []
    for row in rows:
        source = source_rows[row["id"]]
        if row["text"] != source["text"]:
            raise SystemExit(f"{row['id']}: the returned text is not the source row's text")
        if json.loads(row["intents_v1"]) != sorted(source["intents"]):
            raise SystemExit(f"{row['id']}: the returned intents_v1 is not the source's v1 label")
        out.append(
            {
                "id": row["id"],
                "intents": as_intents(row["intents_v2"], f"{path.name}:{row['id']}"),
                "notes": row["notes"] or "",
            }
        )
    return out


def apply_redo(
    rulings: list[dict], staged: dict[str, Path], loaded: dict, relabelled: dict[str, list[str]]
) -> list[dict]:
    """Every decided label written into the staged intents column, three columns and no more.

    `old` is the label the **re-labeller** produced, not the value found on disk — that is what
    `measure_empty_drop.reversals` means by the word, and 27 of these rows already carry a
    later fix's answer. Recording the disk value would make the reversal restore that answer
    instead, and the 97 would stop deriving as the class the re-labeller emptied. What was
    actually overwritten is in `replaced`.
    """
    where = index(staged)
    applied = []
    for ruling in rulings:
        key, position = where[ruling["id"]]
        rows, lines = loaded[key]
        row, line = rows[position], lines[position]
        changes = {
            "intents": ruling["intents"],
            "notes": note_for(ruling["notes"], row.get("notes") or ""),
            "annotator": ANNOTATOR,
        }
        lines[position] = rewritten(row, line, changes)
        rows[position] = {**row, **changes}
        replaced = sorted(row["intents"])
        applied.append(
            {
                "id": ruling["id"],
                "file": rel(staged[key]),
                "old": sorted(relabelled.get(ruling["id"], replaced)),
                "replaced": replaced,
                "new": ruling["intents"],
                "moved": replaced != ruling["intents"],
                "authority": PROVENANCE,
            }
        )
    return applied


def apply_appends(
    rulings: list[dict], staged: dict[str, Path], loaded: dict, sources: dict[str, Path]
) -> list[dict]:
    """The rows that were never staged, inserted where their source file has them.

    Position is not cosmetic: a `_tax2` copy exists to diff against its source line for line,
    and rows appended at the end would show up in that diff as every following row moving.
    """
    by_id = {ruling["id"]: ruling for ruling in rulings}
    added = []
    for key, source in sources.items():
        source_rows, _ = relabel.load(source)
        mine = [row for row in source_rows if row["id"] in by_id]
        if not mine:
            continue
        rows, lines = loaded[key]
        held = {row["id"] for row in rows}
        order = {row["id"]: position for position, row in enumerate(source_rows)}
        for row in mine:
            if row["id"] in held:
                raise SystemExit(f"{row['id']} is already in {rel(staged[key])} — nothing to add")
            ruling = by_id[row["id"]]
            new = {
                **row,
                "intents": ruling["intents"],
                "notes": note_for(ruling["notes"], row.get("notes") or ""),
                "annotator": ANNOTATOR,
            }
            if bad := annotation.check_labels(new, "comments"):
                raise SystemExit(f"{row['id']}: the merged row is not a legal annotation ({bad})")
            rows.append(new)
            lines.append(json.dumps(new, ensure_ascii=False))
            added.append(
                {
                    "id": row["id"],
                    "file": rel(staged[key]),
                    "v1": sorted(row["intents"]),
                    "v2": ruling["intents"],
                    "authority": PROVENANCE,
                }
            )
        paired = sorted(zip(rows, lines, strict=True), key=lambda pair: order[pair[0]["id"]])
        loaded[key] = ([row for row, _ in paired], [line for _, line in paired])
    return added


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gates", type=Path, default=GATES)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--micro-manifest", type=Path, default=MICRO_MANIFEST)
    parser.add_argument("--drop", type=Path, default=DROP)
    parser.add_argument("--relabel-record", type=Path, default=RELABEL_RECORD)
    parser.add_argument("--quiz-record", type=Path, default=QUIZ_RECORD)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--dry-run", action="store_true", help="what would be written, then stop")
    args = parser.parse_args(argv)

    gates = gate_verdicts(args.gates, args.manifest)
    uplabel_scope(gates)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    micro = json.loads(args.micro_manifest.read_text(encoding="utf-8"))

    staged = {key: relabel.staged(path) for key, path in relabel.SOURCES.items()}
    loaded = {key: relabel.load(path) for key, path in staged.items()}
    for key, path in staged.items():
        # `load` drops blank lines, so joining them back is only lossless if there were none.
        if body(loaded[key][1]) != path.read_text(encoding="utf-8"):
            raise SystemExit(
                f"{rel(path)}: its lines do not join back into the file it was read from, so"
                " rewriting it would change lines this merge does not name."
            )
    staged_rows = {row["id"]: row for key in staged for row in loaded[key][0]}
    source_rows = {
        row["id"]: row for source in relabel.SOURCES.values() for row in relabel.load(source)[0]
    }
    forbidden = relabel.forbidden_ids()

    labelled = dict(source_rows)
    derived = {
        row["id"]: row
        for row in builder.redo_population(
            args.drop, args.relabel_record, args.quiz_record, labelled
        )
    }
    redo = redo_ingest(args.root / manifest["pack"] / "emptied_redo.csv", derived, staged_rows)
    unreadable = unreadable_ingest(args.root / micro["pack"], micro, source_rows)
    if trespass := sorted({row["id"] for row in redo + unreadable} & forbidden):
        raise SystemExit(f"{trespass} sit in a frozen test file and may not be labelled here")

    # Before a byte is written, not after: the 75 rewritten rows reverse to the re-labeller's
    # own answer and cannot move the emptied class, but the 14 appended ones are new pairs in
    # it — one whose v1 label is non-empty and whose v2 answer is `[]` would join the 97, and a
    # guard that notices that after the files are rewritten is not a guard.
    joining = [
        row["id"] for row in unreadable if source_rows[row["id"]]["intents"] and not row["intents"]
    ]
    if joining:
        raise SystemExit(
            f"{joining} would join the emptied class by being added: their v1 label is not empty"
            " and the sitting answered `[]`. The 97 are a population other steps derive, so"
            " widening it is a decision, not a side effect of a merge."
        )

    print(
        f"gates: passed {gates['passed'] or 'none'} · failed {gates['failed']}"
        f"\n  up-label rows merged: 0 of {manifest['precheck']['rows'] and 1912}"
        f" (no stratum cleared {gates['bar']:.0%})"
        f"\n  emptied redo: {len(redo)} rows decided by hand"
        f"\n  unreadable: {len(unreadable)} rows joining the staged files"
    )
    if args.dry_run:
        for row in redo + unreadable:
            print(f"  {row['id']:<24} -> {row['intents']}")
        return 0

    before_sha = {rel(path): digest(path) for path in staged.values()}
    applied = apply_redo(redo, staged, loaded, drop.reversals(args.relabel_record))
    added = apply_appends(unreadable, staged, loaded, relabel.SOURCES)
    for key, path in staged.items():
        path.write_text(body(loaded[key][1]), encoding="utf-8")
    after_sha = {rel(path): digest(path) for path in staged.values()}

    timestamp = datetime.now(UTC).isoformat(timespec="seconds")
    history = json.loads(args.relabel_record.read_text(encoding="utf-8"))
    history.setdefault("fixes", []).append(
        {
            "applied_by": APPLIED_BY,
            "timestamp": timestamp,
            "authority": rel(args.gates),
            "rows": [
                {key: row[key] for key in ("id", "file", "old", "replaced", "new", "authority")}
                for row in applied
            ],
            "staged_sha256_before": before_sha,
            "staged_sha256_after": after_sha,
            "note": (
                "The 75 emptied rows the 4.5g sitting decided by hand, with the parent post in"
                " front of the decider. `old` is what the RE-LABELLER produced, which is what a"
                " reversal has to restore; `replaced` is the value actually overwritten, and for"
                " 27 rows it is a later fix's answer rather than the re-labeller's. The 14"
                " unreadable rows joined the staged files in the same run and are NOT in this"
                " block: the re-labeller never answered them, so it has no answer to revert to."
            ),
            "git": git_state(args.relabel_record),
        }
    )
    relabel.write_json(args.relabel_record, history)

    still = population(args.drop, args.relabel_record)
    record = {
        "timestamp": timestamp,
        "merged_by": APPLIED_BY,
        "provenance": PROVENANCE,
        "gates": {
            "record": rel(args.gates),
            "bar": gates["bar"],
            "passed": gates["passed"],
            "failed": gates["failed"],
            "strata": {name: block["agreement"] for name, block in gates["strata"].items()},
        },
        "uplabel": {
            "rows_merged": 0,
            "rows_held": gates["second_round_rows"],
            "note": (
                "Nothing from the 1,912 precheck rows merged: every stratum came back under the"
                " bar, so each sends its whole population back rather than the hundred judged."
            ),
        },
        "redo": {
            "rows": len(applied),
            "moved": sum(1 for row in applied if row["moved"]),
            "already_matching": sum(1 for row in applied if not row["moved"]),
            "intents": dict(
                Counter(
                    intent for row in applied for intent in (row["new"] or ["(none)"])
                ).most_common()
            ),
            "empty_answers": sum(1 for row in applied if not row["new"]),
            "source": rel(args.root / manifest["pack"] / "emptied_redo.csv"),
            "rows_detail": applied,
        },
        "unreadable": {
            "rows": len(added),
            "source": micro["pack"],
            "by_file": dict(Counter(row["file"] for row in added)),
            "flips_from_v1": sum(1 for row in added if row["v1"] != row["v2"]),
            "rows_detail": added,
            "note": (
                "Never in a staged file before this: the re-labeller refused them four passes"
                " running, so they sat on their v1 labels. Inserted at their source file's own"
                " position, because a `_tax2` copy exists to diff against its source."
            ),
        },
        "fields_written": list(FIELDS),
        "annotator": ANNOTATOR,
        "staged_sha256_before": before_sha,
        "staged_sha256_after": after_sha,
        "emptied_population_still": len(still),
        "git": git_state(args.record),
        "note": (
            "Two of the sitting's three questions merge here. The third — the up-label"
            " precheck — merges per stratum and no stratum passed, so its 1,912 rows are"
            " untouched model output still."
        ),
    }
    relabel.append_record(args.record, record)

    print(
        f"\n{len(applied)} redo rows written ({record['redo']['moved']} moved a label,"
        f" {record['redo']['empty_answers']} are `[]`)"
        f"\n{len(added)} unreadable rows added: {record['unreadable']['by_file']}"
        f"\nthe emptied population still derives as {len(still)} rows after the fix block"
        f"\nwrote {rel(args.record)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
