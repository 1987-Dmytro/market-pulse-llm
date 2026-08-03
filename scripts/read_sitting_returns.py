#!/usr/bin/env python3
"""The sitting's verdicts, turned into the three per-stratum gate numbers (4.5g3).

`precheck300.csv` went out with 300 rows drawn 100 from each of three strata and came back
with a verdict on every one. The bar was registered before the pack was handed over — a row
is `correct` only if all four fields are, agreement is per stratum on its own denominator of
100, and a stratum below 0.90 sends back its **whole** population rather than the hundred
judged.

What this refuses, because the gate's authority rests on it:

- **the returned rows are the sealed rows.** The pack is rebuilt from the batch the manifest
  pins and the manifest's own seed, and the rebuild has to reproduce the sha256 it recorded
  before a single verdict is read. Only then are the rows compared cell by cell.
- **only `verdict` and `notes` came back changed.** The whole-file sha256 differs from the
  sealed one by design — two columns were filled in — so identity is proved on the seven
  columns that are the artifact, not on the file.
- **a verdict is a value in a named table.** `correct`/`incorrect`, matched case-insensitively.
  Anything else stops the run rather than being guessed at, and a blank cell counts as
  `incorrect` because `results/sitting_45g2_manifest.json` registered it that way in advance.
- **a total that disagrees with the capture log.** `docs/quiz-sitting-45g-log.md` records
  258 correct / 42 incorrect. The CSV is the authority and nothing is reconciled silently: a
  disagreement prints both numbers and stops.

    PYTHONPATH=src python3 scripts/read_sitting_returns.py

Reads the returned pack and the sealed manifest, writes `results/sitting_45g_gates.json`.
Nothing in the pack is written to.
"""

import argparse
import csv
import io
import json
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))  # the builder is the rebuild

import build_sitting_pack as builder  # noqa: E402
import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from market_pulse import parents  # noqa: E402

MANIFEST = REPO_ROOT / "results" / "sitting_45g2_manifest.json"
RECORD = REPO_ROOT / "results" / "sitting_45g_gates.json"
POSTS = REPO_ROOT / "data" / "raw" / "posts"
LOG = "docs/quiz-sitting-45g-log.md"

MUTABLE = ("verdict", "notes")
"""The two cells the sitting fills. Everything else is the artifact ruled on."""

VERDICT_FORMS = {"correct": "correct", "incorrect": "incorrect"}
"""Every accepted verdict, keyed by its case-folded form. A third form is not guessed at."""

BLANK = "(blank)"
"""What an empty cell is counted as. It is a tally key; the manifest registered it as
`incorrect` before the pack went out, and that is how it is scored."""

RECORDED_IN_LOG = {"correct": 258, "incorrect": 42}
"""What `docs/quiz-sitting-45g-log.md` records after its own correction, and the only number
this run is allowed to disagree with loudly. The log's own line says the CSV is the authority
and that its block arithmetic was off by one — so a second disagreement is not a third
arithmetic slip to absorb, it is a returned file that is not the one the log describes."""

PROVENANCE = "team-lead-LLM triage with operator adjudication and operator spot-check"
"""What produced these verdicts, in the words Amendment 2 of the capture log requires.

Not "operator calibration": SPEC §8 means something specific by that, and 264 of the 300
verdicts here were written by a team-lead LLM whose triage the operator confirmed on a blind
seeded twenty (20/20 against a bar of 18/20). One constant, because every record downstream
has to say the same thing and four hand-typed copies drift."""


def rel(path: Path) -> str:
    return relabel.rel(path)


def serialize(columns: tuple[str, ...], rows: list[dict]) -> bytes:
    """Rows in the builder's own CSV dialect — the format the pack was sealed in."""
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=columns, delimiter=builder.DELIMITER, lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def rebuild(manifest: dict, batch: Path, captions: Path, posts_dir: Path) -> list[dict]:
    """The sealed 300 rows, built again from the batch — or a stop naming why not."""
    for path, pinned, what in (
        (batch, manifest["precheck"]["source_sha256"], "the rows the pack was drawn from"),
        (captions, manifest["media"]["captions_sha256"], "what a media-only post says"),
    ):
        if not path.exists():
            raise SystemExit(f"{rel(path)}: not found — the pack cannot be rebuilt without it")
        found = sha256(path.read_bytes()).hexdigest()
        if found != pinned:
            raise SystemExit(
                f"{rel(path)}: sha256 {found[:16]}…, the manifest pins {pinned[:16]}…."
                f" {what} has moved, so this run would rebuild a different pack."
            )

    rows = builder.load_batch(batch)
    drawn, where = builder.draw(builder.strata(rows), manifest["precheck"]["per_stratum"])
    if where != manifest["precheck"]["stratum_of"]:
        raise SystemExit(
            "the draw no longer reproduces the manifest's stratum_of: these are not the 300 ids"
            " that were judged, so no per-stratum number computed here would be about them."
        )
    loaded = parents.load(posts_dir)
    surrogates = parents.load_captions(captions)
    sealed = [
        {
            "id": row["id"],
            "post": builder.post_of(loaded, surrogates, row),
            "text": row["text"],
            "sentiment": row["sentiment"],
            "sarcasm": str(row["sarcasm"]).lower(),
            "intents": builder.as_label(row["intents"]),
            "unclear": str(row["unclear"]).lower(),
            "verdict": "",
            "notes": "",
        }
        for row in drawn
    ]
    found = sha256(serialize(builder.PRECHECK_COLUMNS, sealed)).hexdigest()
    if found != manifest["sha256"]["precheck300.csv"]:
        raise SystemExit(
            f"the rebuild hashes to {found[:16]}… against the manifest's"
            f" {manifest['sha256']['precheck300.csv'][:16]}…. Seed {manifest['seed']} no longer"
            " draws the pack that went out, so the returned rows cannot be checked against it."
        )
    return sealed


def read_returns(path: Path, columns: tuple[str, ...], delimiter: str) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{rel(path)}: not found — the sitting's returns are not here")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        found = tuple(reader.fieldnames or ())
        if found != columns:
            raise SystemExit(
                f"{path.name}: columns {list(found)}, the pack's are {list(columns)}."
                " The file was re-shaped on the way back, so its rows are not the sealed ones."
            )
        return list(reader)


def canonical(raw: str, where: str) -> str:
    """One returned cell as its tally key — a named verdict, or `(blank)`."""
    form = (raw or "").strip()
    if not form:
        return BLANK
    token = VERDICT_FORMS.get(form.casefold())
    if token is None:
        raise SystemExit(
            f"{where}: verdict {raw!r} is not one of {sorted(VERDICT_FORMS)}. Add it to"
            " VERDICT_FORMS only if the sitting wrote it — a form guessed at here changes what a"
            " cell means between the evening it was written and the number it ends up in."
        )
    return token


def collate(sealed: list[dict], returned: list[dict], columns: tuple[str, ...]) -> list[dict]:
    """The sealed rows with their returned verdicts — or a stop naming the defect."""
    if len(returned) != len(sealed):
        raise SystemExit(
            f"{len(returned)} returned rows against {len(sealed)} sealed ones. A row was added"
            " or dropped, so the returns are not this pack's."
        )
    preserved = tuple(column for column in columns if column not in MUTABLE)
    rows = []
    for line, (back, row) in enumerate(zip(returned, sealed, strict=True), start=2):  # 1 = header
        if back["id"] != row["id"]:
            raise SystemExit(
                f"line {line}: {back['id']!r} where the sealed pack has {row['id']!r}. The rows"
                " came back in a different order, so nothing below this line lines up."
            )
        for column in preserved:
            if back[column] != row[column]:
                raise SystemExit(
                    f"line {line}: {column} of {row['id']} differs from the sealed pack"
                    f" ({back[column]!r} against {row[column]!r}). Only verdict and notes may"
                    " come back changed — the rest is the artifact the sitting ruled on."
                )
        rows.append(
            {
                "id": row["id"],
                "verdict": canonical(back["verdict"], f"precheck300.csv:{row['id']}"),
                "notes": (back["notes"] or "").strip(),
            }
        )
    return rows


def tally(rows: list[dict]) -> dict[str, int]:
    return dict(sorted(Counter(row["verdict"] for row in rows).items()))


def gates(rows: list[dict], stratum_of: dict[str, str], bar: float) -> dict:
    """Per stratum: the denominator it was registered on, and the verdict that follows."""
    out = {}
    for name in sorted({stratum_of[row["id"]] for row in rows}):
        mine = [row for row in rows if stratum_of[row["id"]] == name]
        correct = sum(1 for row in mine if row["verdict"] == "correct")
        agreement = correct / len(mine)
        out[name] = {
            "n": len(mine),
            "correct": correct,
            "tally": tally(mine),
            "agreement": agreement,
            "verdict": "PASS" if agreement >= bar else "FAIL",
        }
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--pack", type=Path, default=None, help="default: the manifest's pack")
    parser.add_argument("--posts", type=Path, default=POSTS)
    parser.add_argument("--record", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    pack = args.pack or REPO_ROOT / manifest["pack"]
    returned_csv = pack / "precheck300.csv"
    columns = builder.PRECHECK_COLUMNS

    sealed = rebuild(
        manifest,
        REPO_ROOT / manifest["precheck"]["source"],
        REPO_ROOT / manifest["media"]["captions"],
        args.posts,
    )
    rows = collate(sealed, read_returns(returned_csv, columns, manifest["delimiter"]), columns)

    counts = tally(rows)
    total_correct = counts.get("correct", 0)
    recount = {"correct": total_correct, "incorrect": len(rows) - total_correct}
    if recount != RECORDED_IN_LOG:
        print(
            f"STOP-RULE 1: {rel(returned_csv)} gives {recount} and {LOG} records"
            f" {RECORDED_IN_LOG}. The CSV is the authority and nothing is reconciled silently —"
            " stopping without writing a gate number.",
            file=sys.stderr,
        )
        return 2

    per_stratum = gates(rows, manifest["precheck"]["stratum_of"], manifest["bar"])
    passed = sorted(name for name, block in per_stratum.items() if block["verdict"] == "PASS")
    failed = sorted(name for name, block in per_stratum.items() if block["verdict"] == "FAIL")
    record = {
        "read_by": "scripts/read_sitting_returns.py",
        "pack": rel(pack),
        "manifest": rel(args.manifest),
        "provenance": PROVENANCE,
        "capture_log": LOG,
        "rule": manifest["precheck"]["rule"],
        "bar": manifest["bar"],
        "second_round": manifest["precheck"]["second_round"],
        "verdict_forms": sorted(VERDICT_FORMS),
        "blank_counts_as": "incorrect",
        "strata": {
            name: {**block, "population": manifest["precheck"]["strata"][name]["population"]}
            for name, block in per_stratum.items()
        },
        "passed": passed,
        "failed": failed,
        "second_round_rows": sum(
            manifest["precheck"]["strata"][name]["population"] for name in failed
        ),
        "totals": {
            "rows": len(rows),
            "correct": total_correct,
            "tally": counts,
            "agreement": total_correct / len(rows),
            "note": (
                "The corpus-wide number, reported and never gated: the bar is per stratum on its"
                " own denominator, and a total is an average over three of them."
            ),
        },
        "recount_matches_log": True,
        "recorded_in_log": RECORDED_IN_LOG,
        "incorrect_in_passed_strata": sorted(
            row["id"]
            for row in rows
            if row["verdict"] != "correct"
            and manifest["precheck"]["stratum_of"][row["id"]] in passed
        ),
        "returned_sha256": sha256(returned_csv.read_bytes()).hexdigest(),
        "sealed_sha256": manifest["sha256"]["precheck300.csv"],
        "sha256_note": (
            "The two differ by design: `verdict` and `notes` came back filled. Identity is"
            " proved on the seven frozen columns cell by cell against a rebuild of the sealed"
            " pack, which reproduces `sealed_sha256` before any verdict is read."
        ),
        "rows": rows,
        "rows_note": (
            "Every verdict and its note, kept here because the returned CSV is gitignored and"
            " this record is the committed copy of an evening nobody will sit through twice."
        ),
        "git": git_state(args.record),
    }
    args.record.parent.mkdir(parents=True, exist_ok=True)
    args.record.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"{rel(returned_csv)} -> {rel(args.record)}")
    print(f"  rebuild reproduces sha256 {record['sealed_sha256'][:16]}… of the sealed pack")
    print(f"  returned file hashes to {record['returned_sha256'][:16]}… (verdict + notes filled)")
    print(f"  recount {recount} matches {LOG}")
    print(f"\nrule: {record['rule']}")
    for name, block in record["strata"].items():
        print(
            f"  {name:<26} {block['correct']:>3}/{block['n']} = {block['agreement']:>6.1%}"
            f"  against {manifest['bar']:.0%}  ==> {block['verdict']}"
            f"   (population {block['population']})"
        )
    print(
        f"  {'TOTAL (not a gate)':<26} {total_correct:>3}/{len(rows)} ="
        f" {record['totals']['agreement']:>6.1%}"
    )
    print(
        f"\npassed: {passed or 'none'}\nfailed: {failed or 'none'}"
        f" -> {record['second_round_rows']} rows go back"
        f"\nincorrect rows sitting in a passed stratum:"
        f" {len(record['incorrect_in_passed_strata'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
