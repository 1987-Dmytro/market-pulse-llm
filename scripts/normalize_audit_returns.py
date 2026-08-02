#!/usr/bin/env python3
"""The operator's returned CSVs, put back into the sealed pack's own format (4.5b).

The pack went out as five UTF-8, comma-separated CSVs and came back through a
spreadsheet: semicolons, and verdicts written out in words
(``B — правильная метка label_B``). None of that is a defect and none of it is
the harness's business, so it is fixed here, once, by a table — never by a model
and never by hand.

Three guarantees, because the ceiling's authority rests on them:

- **only the verdict column changes.** Every output row is the *sealed* row with
  one cell replaced, and the file is proved byte-identical to the sealed one once
  those cells are blanked again. A round-trip that reproduces the sealed bytes
  says more than a field-by-field comparison: it also covers quoting, column
  order and line endings.
- **a verdict is derived twice.** An exact-form table and the cell's leading
  token have to agree, or the cell is named and the run stops. One derivation
  alone would accept ``не A, а B``.
- **the returns are the pinned ones.** The team lead sha-pinned the authoritative
  return set; a file that is not one of those five is not normalized.

    python3.11 scripts/normalize_audit_returns.py

Reads the raw returns and the sealed pack, writes the pack and
``results/audit_45b_returns.json``. The raw returns are never written to. A
second run over an already-normalized pack is a no-op, not a second overwrite.
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
sys.path.insert(0, str(Path(__file__).resolve().parent))  # git_state lives with the builder

from build_audit_pack import git_state  # noqa: E402
from market_pulse import audit  # noqa: E402

RETURNS = REPO_ROOT / "data" / "annotation" / "audit_45a_returned"
MANIFEST = REPO_ROOT / "results" / "audit_45a_manifest.json"
RECORD = REPO_ROOT / "results" / "audit_45b_returns.json"

PINNED = {
    "comments_sentiment.csv": "c590192f404958ef4df976a1c58dce8f91769f55d5506b7334726c351e15d427",
    "comments_intents.csv": "e1333a8aaf5f8aedddc2dc3df2518e093c8663c80f7ea49d72690df75e7f0d77",
    "slice_unfixed.csv": "6f0fd7ddc8f5622da70048774cd83aa0036f9dd1916b53e0c1588a6aa26885bd",
    "posts.csv": "e254499abf40e25723e06fd985e1aa6779f6f06ba84d24bd6ec8c9c8dddec93f",
    "control.csv": "4410090fa95f0c01aa936ce97218d67f4ab308569945e88807bbaab8adc02dbd",
}
"""The authoritative return set, sha-pinned by the team lead in docs/PROMPT-4.5b
(first eight hex digits there, full digests here). The adjudication happened
once; a return file that is not one of these is somebody's other copy."""

VERDICT_FORMS = {
    "A — правильная метка label_A": "A",
    "B — правильная метка label_B": "B",
    "ambiguous — по тексту решить нельзя": "ambiguous",
    "correct": "correct",
    "incorrect": "incorrect",
}
"""Every form the returns carry, verbatim, mapped to the canonical token.

The keys are the operator's own words and are quoted rather than translated: a
mapping table that paraphrases its input matches nothing. Anything outside this
table stops the run — silently guessing at a sixth form is how a verdict changes
meaning between the evening it was written and the number it ends up in."""


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def read_csv(path: Path, columns: tuple[str, ...], delimiter: str, encoding: str) -> list[dict]:
    with path.open(encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        found = tuple(reader.fieldnames or ())
        if found != columns:
            raise SystemExit(
                f"{path.name}: columns {list(found)}, the pack's are {list(columns)}."
                " The file was re-shaped on the way back, so its rows are not the sealed ones."
            )
        return list(reader)


def serialize(columns: tuple[str, ...], rows: list[dict]) -> bytes:
    """Rows in the builder's own CSV dialect — the format the pack was sealed in."""
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def canonical(raw: str, vocabulary: tuple[str, ...], where: str) -> str:
    """One long form as its canonical token, agreed on by the table and the words."""
    form = raw.strip()
    table = VERDICT_FORMS.get(form)
    token = form.split(maxsplit=1)[0] if form else ""
    if table is None:
        raise SystemExit(
            f"{where}: verdict {raw!r} is not one of the forms the returns carry"
            f" ({list(VERDICT_FORMS)}). Add it to the table only if the operator wrote it."
        )
    if table != token:
        raise SystemExit(
            f"{where}: verdict {raw!r} reads as {token!r} but the table maps it to {table!r}."
            " The two derivations disagree, so the cell does not say what it looks like."
        )
    if table not in vocabulary:
        raise SystemExit(f"{where}: verdict {table!r} is not one of {vocabulary} for this file")
    return table


def normalize(
    name: str,
    columns: tuple[str, ...],
    vocabulary: tuple[str, ...],
    returns: Path,
    pack: Path,
) -> tuple[list[dict], bytes]:
    """The sealed rows with their verdict cells filled — or a stop naming the defect."""
    raw = read_csv(returns / name, columns, ";", "utf-8-sig")
    sealed = read_csv(pack / name, columns, ",", "utf-8")
    if len(raw) != len(sealed):
        raise SystemExit(
            f"{name}: {len(raw)} returned rows against {len(sealed)} sealed ones."
            " A row was added or dropped, so the returns are not this pack's."
        )
    preserved = tuple(column for column in columns if column != "verdict")
    rows = []
    for line, (back, row) in enumerate(zip(raw, sealed), start=2):  # 2: the header is line 1
        for column in preserved:
            if back[column] != row[column]:
                raise SystemExit(
                    f"{name} line {line}: {column} of {row['id']!r} differs from the sealed pack"
                    f" ({back[column]!r} against {row[column]!r}). Only the verdict column may"
                    " come back changed — the rest is the artifact the operator ruled on."
                )
        rows.append(
            {**row, "verdict": canonical(back["verdict"], vocabulary, f"{name}:{row['id']}")}
        )

    blanked = serialize(columns, [{**row, "verdict": ""} for row in rows])
    if blanked != (pack / name).read_bytes():
        raise SystemExit(
            f"{name}: blanking the verdicts again does not reproduce the sealed file byte for"
            " byte, so this run would change more than one column."
        )
    return rows, serialize(columns, rows)


def main(argv: list[str] | None = None, pins: dict[str, str] = PINNED) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--returns", type=Path, default=RETURNS)
    parser.add_argument("--pack", type=Path, default=None, help="default: the manifest's pack_path")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--record", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    pack = args.pack or REPO_ROOT / manifest["pack_path"]
    sealed_sha = {name: digest(pack / name) for name in manifest["csv"]}
    expected = {name: entry["sha256"] for name, entry in manifest["csv"].items()}
    if sealed_sha != expected:
        done = json.loads(args.record.read_text(encoding="utf-8")) if args.record.exists() else {}
        if sealed_sha == {n: e["normalized_sha256"] for n, e in done.get("files", {}).items()}:
            print(f"{rel(pack)}: already normalized, every file matches {rel(args.record)}")
            return 0
        moved = [name for name in expected if sealed_sha[name] != expected[name]]
        raise SystemExit(
            f"{rel(pack)}: {moved} match neither the sealed pack in {rel(args.manifest)} nor a"
            " completed normalization. The pack this would overwrite is not the one that went out."
        )
    for name, pinned in pins.items():
        found = digest(args.returns / name)
        if found != pinned:
            raise SystemExit(
                f"{args.returns / name}: sha256 {found}, the team lead pinned {pinned}."
                " This is not the authoritative return set."
            )

    files, bodies = {}, {}
    for name in manifest["csv"]:
        control = name == "control.csv"
        columns = audit.CONTROL_COLUMNS if control else audit.COLUMNS
        vocabulary = audit.CONTROL_VERDICTS if control else audit.VERDICTS
        rows, body = normalize(name, columns, vocabulary, args.returns, pack)
        bodies[name] = body
        files[name] = {
            "rows": len(rows),
            "raw_sha256": digest(args.returns / name),
            "sealed_sha256": sealed_sha[name],
            "normalized_sha256": sha256(body).hexdigest(),
            "verdicts": dict(sorted(Counter(row["verdict"] for row in rows).items())),
        }

    for name, body in bodies.items():  # nothing is written until every file has passed
        (pack / name).write_bytes(body)
    record = {
        "normalized_by": "scripts/normalize_audit_returns.py",
        "returns_path": rel(args.returns),
        "pack_path": rel(pack),
        "manifest_path": rel(args.manifest),
        "key_sha256": manifest["key_sha256"],
        "verdict_forms": VERDICT_FORMS,
        "files": files,
        "git": git_state(args.record),
    }
    args.record.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"{rel(args.returns)} -> {rel(pack)}  (semicolon -> comma, utf-8-sig -> utf-8)")
    for name, entry in files.items():
        tally = " · ".join(f"{verdict} {n}" for verdict, n in entry["verdicts"].items())
        print(f"  {name:<24} {entry['rows']:>4} rows · {tally}")
    print(
        "only the verdict column changed: blanking it again reproduces every sealed file byte"
        f" for byte.\nrecord: {rel(args.record)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
