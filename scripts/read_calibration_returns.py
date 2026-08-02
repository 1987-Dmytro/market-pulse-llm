#!/usr/bin/env python3
"""The operator's calibration verdicts, turned into the gate number (4.5f).

The pack went out as UTF-8, comma-separated CSVs and came back through a
spreadsheet: semicolons, a BOM, and `Old`/`New` where the pack said `old`/`new`.
None of that is a defect — it is the 4.5a precedent — and none of it is allowed
to reach the number, so it is fixed here, once, by a table.

What this refuses, because the gate's authority rests on it:

- **the returned rows are the sealed rows.** The pack is rebuilt from the staged
  files and the manifest's own seed, and the rebuild has to reproduce every
  sha256 the manifest pins before a single verdict is read. A spreadsheet
  re-encodes bytes, so the rows are then compared cell by cell — but the file
  they are compared against is proved byte-identical to the one that went out.
- **only `verdict` and `notes` came back changed.** Every other cell must match
  the sealed row. `notes` is mutable on purpose: 11902 carries a transcription.
- **a verdict is a value in a named table.** `correct`/`incorrect` for the gate,
  `old`/`new`/`neither` for the diagnostic, matched case-insensitively. Anything
  else stops the run rather than being guessed at.
- **the denominator is the pre-registered one.** A blank gated cell is not a
  missing row: `results/calib_45e_manifest.json` registered it as disagreement
  before the pack was handed over, and that is what it counts as here.

    PYTHONPATH=src python3 scripts/read_calibration_returns.py

Reads the returned pack and the sealed manifest, writes
`results/calib_45e_verdict.json`. Nothing in the pack is written to.
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

import build_calibration_pack as builder  # noqa: E402
import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

MANIFEST = REPO_ROOT / "results" / "calib_45e_manifest.json"
RECORD = REPO_ROOT / "results" / "calib_45e_verdict.json"

MUTABLE = ("verdict", "notes")
"""The two cells the operator fills. Everything else is the artifact ruled on."""

VERDICT_FORMS = {
    "gated.csv": {"correct": "correct", "incorrect": "incorrect"},
    "changed.csv": {"old": "old", "new": "new", "neither": "neither"},
}
"""Every accepted verdict, per file, keyed by its case-folded form.

A spreadsheet capitalises the first letter of a cell and the returns carry both
`old` and `Old`. Case is therefore normalised — by this table and nothing else.
A sixth form is not silently guessed at: it stops the run and is added here only
if the operator wrote it."""

BLANK = "(blank)"
"""What an empty cell is counted as. It is a tally key, never a verdict."""


def rel(path: Path) -> str:
    return relabel.rel(path)


def serialize(columns: tuple[str, ...], rows: list[dict]) -> bytes:
    """Rows in the builder's own CSV dialect — the format the pack was sealed in.

    `lineterminator` is not a detail: the default is CRLF, the builder wrote LF,
    and a rebuild that differs by one byte per line proves nothing about a sha.
    """
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def rebuild(manifest: dict) -> dict[str, tuple[tuple[str, ...], list[dict]]]:
    """The sealed pack, built again from the staged rows — or a stop naming why not.

    The seed and the two sample sizes come out of the manifest rather than the
    builder's constants: what has to be reproduced is the pack that went out, and
    a constant edited afterwards would quietly redefine that.
    """
    for group in ("staged", "sources"):
        for name, pinned in manifest[group].items():
            path = REPO_ROOT / name
            if not path.exists():
                raise SystemExit(f"{name}: not found — the pack cannot be rebuilt without it")
            found = sha256(path.read_bytes()).hexdigest()
            if found != pinned:
                raise SystemExit(
                    f"{name}: sha256 {found[:16]}…, the sealed manifest pins {pinned[:16]}…."
                    " The rows the pack was drawn from have moved, so this run would rebuild a"
                    f" different pack. If the 4.5f rulings are already applied, the gate was"
                    f" computed before them and is recorded in {rel(RECORD)}."
                )

    pairs, _ = builder.load_pairs()
    drawn = builder.strata(
        pairs,
        manifest["composition"]["gated"]["rows"],
        manifest["composition"]["changed"]["rows"],
    )
    files = {
        "gated.csv": (builder.GATED_COLUMNS, builder.gated_rows(drawn["gated"])),
        "changed.csv": (builder.DIAGNOSTIC_COLUMNS, builder.diagnostic_rows(drawn["changed"])),
    }
    for name, (columns, rows) in files.items():
        found = sha256(serialize(columns, rows)).hexdigest()
        if found != manifest["sha256"][name]:
            raise SystemExit(
                f"{name}: the rebuild hashes to {found[:16]}… against the manifest's"
                f" {manifest['sha256'][name][:16]}…. Seed {manifest['seed']} no longer draws the"
                " pack that went out, so the returned rows cannot be checked against it."
            )
    return files


def read_returns(path: Path, columns: tuple[str, ...]) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{rel(path)}: not found — the operator's returns are not here")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        found = tuple(reader.fieldnames or ())
        if found != columns:
            raise SystemExit(
                f"{path.name}: columns {list(found)}, the pack's are {list(columns)}."
                " The file was re-shaped on the way back, so its rows are not the sealed ones."
            )
        return list(reader)


def canonical(raw: str, forms: dict[str, str], where: str) -> str:
    """One returned cell as its tally key — a named verdict, or `(blank)`."""
    form = (raw or "").strip()
    if not form:
        return BLANK
    token = forms.get(form.casefold())
    if token is None:
        raise SystemExit(
            f"{where}: verdict {raw!r} is not one of {sorted(forms)}. Add it to VERDICT_FORMS"
            " only if the operator wrote it — a form guessed at here changes what a cell means"
            " between the evening it was written and the number it ends up in."
        )
    return token


def collate(name: str, columns: tuple[str, ...], sealed: list[dict], path: Path) -> list[dict]:
    """The sealed rows with their returned verdicts — or a stop naming the defect."""
    returned = read_returns(path, columns)
    if len(returned) != len(sealed):
        raise SystemExit(
            f"{name}: {len(returned)} returned rows against {len(sealed)} sealed ones."
            " A row was added or dropped, so the returns are not this pack's."
        )
    forms = VERDICT_FORMS[name]
    preserved = tuple(column for column in columns if column not in MUTABLE)
    rows = []
    for line, (back, row) in enumerate(zip(returned, sealed), start=2):  # 2: the header is line 1
        if back["id"] != row["id"]:
            raise SystemExit(
                f"{name} line {line}: {back['id']!r} where the sealed pack has {row['id']!r}."
                " The rows came back in a different order, so nothing below this line lines up."
            )
        for column in preserved:
            if back[column] != row[column]:
                raise SystemExit(
                    f"{name} line {line}: {column} of {row['id']} differs from the sealed pack"
                    f" ({back[column]!r} against {row[column]!r}). Only verdict and notes may"
                    " come back changed — the rest is the artifact the operator ruled on."
                )
        rows.append(
            {
                "id": row["id"],
                "verdict": canonical(back["verdict"], forms, f"{name}:{row['id']}"),
                "notes": (back["notes"] or "").strip(),
            }
        )
    return rows


def tally(rows: list[dict]) -> dict[str, int]:
    return dict(sorted(Counter(row["verdict"] for row in rows).items()))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--pack", type=Path, default=None, help="default: the manifest's pack")
    parser.add_argument("--record", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    pack = args.pack or REPO_ROOT / manifest["pack"]
    files = rebuild(manifest)
    collated = {
        name: collate(name, columns, rows, pack / name) for name, (columns, rows) in files.items()
    }

    gated = collated["gated.csv"]
    counts = tally(gated)
    agreement = counts.get("correct", 0) / len(gated)
    passed = agreement >= manifest["bar"]
    record = {
        "read_by": "scripts/read_calibration_returns.py",
        "pack": rel(pack),
        "manifest": rel(args.manifest),
        "rule": manifest["rule"],
        "bar": manifest["bar"],
        "gate": {
            "rows": len(gated),
            "correct": counts.get("correct", 0),
            "tally": counts,
            "agreement": agreement,
            "verdict": "PASS" if passed else "FAIL",
        },
        "diagnostic": {
            "rows": len(collated["changed.csv"]),
            "tally": tally(collated["changed.csv"]),
            "note": (
                "Not gated and it does not move the verdict above — the manifest registered the"
                " gate on gated.csv alone. It stands beside the gate number rather than under it:"
                " the diagnostic shows the old label beside the new one and is the sharper"
                " instrument, so a disagreement here is a signal about the re-label that the"
                " gated hundred, judging a label with no contrast, cannot produce."
            ),
        },
        "verdict_forms": VERDICT_FORMS,
        "blank_counts_as": BLANK,
        "returned_sha256": {name: sha256((pack / name).read_bytes()).hexdigest() for name in files},
        "sealed_sha256": {name: manifest["sha256"][name] for name in files},
        "rows": {name.removesuffix(".csv"): rows for name, rows in collated.items()},
        "git": git_state(args.record),
    }
    args.record.parent.mkdir(parents=True, exist_ok=True)
    args.record.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"{rel(pack)} -> {rel(args.record)}  (semicolon + BOM -> the sealed dialect)")
    print(f"  rebuild reproduces every sha256 in {rel(args.manifest)}")
    for name, rows in collated.items():
        shown = " · ".join(f"{verdict} {n}" for verdict, n in tally(rows).items())
        print(f"  {name:<14} {len(rows):>4} rows · {shown}")
    print(f"\nrule: {manifest['rule']}")
    print(
        f"gate: {record['gate']['correct']}/{record['gate']['rows']} ="
        f" {agreement:.2%} against {manifest['bar']:.0%}  ==> {record['gate']['verdict']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
