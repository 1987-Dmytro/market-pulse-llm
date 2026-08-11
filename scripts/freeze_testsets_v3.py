#!/usr/bin/env python3
"""v3 of the frozen test sets: the operator's blind verdicts, applied mechanically (4.5c).

Gate 4.5 approved 38 point fixes — the rows where the operator, ruling blind, chose
the answer the arm gave over the one gold carried. This applies them and nothing
else:

- **v2 is never touched.** v3 is three NEW files beside it, so every record, bar and
  manifest that references a v2 sha keeps meaning what it meant. A test set that
  changes underneath a published number is not a correction, it is a lost result.
- **`intents` is untouched everywhere**, pending the law decision the review pack was
  built for. The 31 intents rows the operator ruled for the arm are derived here and
  deliberately not applied — one constant says so and the changelog records it.
- **the fix is a copy, not a judgement.** A ruled row takes the arm's own value for
  that head's field(s) straight out of the dump the audit was built from. The only
  derived thing is a brand entry's ``brand_id``, which comes from the watchlist the
  scorer already normalises through.
- **every unchanged row is proved unchanged.** Re-serialising a row that took no fix
  must reproduce its v2 line byte for byte, or the run stops: that is what makes "v3
  differs from v2 in 38 rows" a check rather than a claim.

    python3.11 scripts/freeze_testsets_v3.py

Reads the audit manifest, the filled pack, the sealed key and the arm's dump; writes
``data/frozen/*_v3.jsonl`` and ``results/frozen_v3.json``, and prints the changelog
table for docs/frozen-testsets.md.
"""

import argparse
import csv
import json
import sys
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse import audit, provenance  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

MANIFEST = REPO_ROOT / "results" / "audit_45a_manifest.json"
RECORD = REPO_ROOT / "results" / "frozen_v3.json"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"

HEAD_FIELDS = {
    "sentiment": ("sentiment",),
    "sarcasm_pair": ("sentiment", "sarcasm"),
    "post_type": ("post_type",),
    "brands": ("brands",),
}
"""What a ruling for the arm rewrites. The G1b slice head is a *pair*: a row leaves
the base model's error union only when both labels are right, so the operator ruled
on both and both are applied."""

LAW_PENDING = ("intents",)
"""Heads whose rulings are derived and NOT applied (gate 4.5, 2026-08-02). The
control sample says 22 of 40 agreed `intents` rows carry a label the operator
considers wrong and 19 of them agreed on the empty set — a disagreement about the
annotation law, not about these 400 rows. Applying disagreement fixes while the law
is open would half-relabel the head against two different readings at once."""

EXPECTED = {"sentiment": 15, "sarcasm_pair": 15, "post_type": 5, "brands": 3}
"""The gate's own arithmetic, pre-registered: 38 fixes as 15 + 15 + 5 + 3. Derived
counts that differ mean the pack, the key or the dump is not the one the gate read."""

ANNOTATOR = "operator-blind-audit-45a"
"""Stamped on every changed row, the way v2 stamped `operator-reviewed`: a frozen row
should say where its label came from without a changelog lookup."""


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def git_state(mine: Path) -> dict:
    """`market_pulse.provenance.git_state`, unsorted — `freeze_testsets_v4` imports this name."""
    return provenance.git_state(mine)


def read_pack(pack: Path, key: dict) -> dict[str, list[str]]:
    """Row ids the operator ruled for the arm, per head — the fixes, still anonymous.

    ``verdict == model_column`` is the whole de-anonymization: the key is the only
    thing that knows which column the arm's label was in, and it is read here rather
    than anywhere the operator could see it.
    """
    ruled: dict[str, list[str]] = {head: [] for head in audit.HEADS}
    for name in sorted({audit.CSV_OF[head] for head in audit.HEADS}):
        with (pack / name).open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != audit.COLUMNS:
                raise SystemExit(f"{name}: not a filled disagreement CSV of the pack")
            for row in reader:
                entry = key.get(f"{row['head']}|{row['id']}")
                if entry is None:
                    raise SystemExit(f"{name}: {row['id']} ({row['head']}) is not in the key")
                if (row["label_A"], row["label_B"]) != (entry["label_A"], entry["label_B"]):
                    raise SystemExit(f"{name}: the labels of {row['id']} differ from the key")
                if not row["verdict"].strip():
                    raise SystemExit(f"{name}: {row['id']} is unruled — v3 is not derivable yet")
                if row["verdict"].strip() == entry["model_column"]:
                    ruled[row["head"]].append(row["id"])
    return ruled


def brand_entries(entries: list[dict], aliases: dict[str, str]) -> list[dict]:
    """The arm's brand mentions in the frozen schema.

    ``docs/annotation/posts.md`` makes both keys mandatory and a prediction carries
    only the mention, so the ``brand_id`` is looked up the way
    :func:`scorer.normalise_brand` looks it up — same table, same casefolding, so the
    written row scores identically to the entry it came from.
    """
    out = []
    for entry in entries:
        mention = entry["mention"]
        found = entry.get("brand_id") or aliases.get(" ".join(mention.split()).casefold())
        out.append({"brand_id": found, "mention": mention})
    return out


def fixes(ruled: dict[str, list[str]], predicted: dict, aliases: dict) -> dict:
    """``{input: {id: {field: value}}}`` — every applied fix, merged per row.

    A row can be ruled under two heads (`post_type` and `brands` share posts_test),
    so the fields are merged before anything is written; a per-head write would drop
    one of the two silently.
    """
    applied: dict[str, dict[str, dict]] = {}
    for head, ids in ruled.items():
        if head in LAW_PENDING:
            continue
        source = predicted[audit.INPUT_OF[head]]
        for row_id in ids:
            values = {
                field: brand_entries(source[row_id][field], aliases)
                if field == "brands"
                else source[row_id][field]
                for field in HEAD_FIELDS[head]
            }
            into = applied.setdefault(audit.INPUT_OF[head], {}).setdefault(row_id, {})
            for field, value in values.items():
                if field in into and into[field] != value:
                    raise SystemExit(
                        f"{row_id}: two heads rule {field} differently ({into[field]!r} against"
                        f" {value!r}). The pack cannot be applied without a human reading both."
                    )
                into[field] = value
    return applied


def apply_to(lines: list[str], applied: dict[str, dict]) -> tuple[list[str], list[dict]]:
    """v3's lines and its changelog — and a stop if an untouched row would move.

    A field the ruling confirms rather than moves is not a change: 13 of the 15 pair
    rulings leave `sentiment` where it was, and a changelog line reading
    ``negative -> negative`` is noise in the one document that has to be read row by
    row. The rulings themselves are counted per head in the record.
    """
    out, changes = [], []
    for line in lines:
        row = json.loads(line)
        fix = {
            field: value
            for field, value in applied.get(row["id"], {}).items()
            if row[field] != value
        }
        if not fix:
            if json.dumps(row, ensure_ascii=False) != line:
                raise SystemExit(
                    f"{row['id']}: re-serialising an unchanged row does not reproduce its v2 line."
                    " v3 would differ from v2 in rows nobody ruled, so nothing is written."
                )
            out.append(line)
            continue
        for field, value in fix.items():
            changes.append({"id": row["id"], "field": field, "from": row[field], "to": value})
            row[field] = value
        row["annotator"] = ANNOTATOR
        out.append(json.dumps(row, ensure_ascii=False))
    return out, changes


def changelog_table(changes: dict[str, list[dict]]) -> str:
    """The doc's table, generated: a hand-typed changelog is a second source of truth."""
    lines = ["| file | id | field | v2 | v3 |", "|---|---|---|---|---|"]
    for name, rows in changes.items():
        for change in rows:
            was, now = (json.dumps(change[k], ensure_ascii=False) for k in ("from", "to"))
            lines.append(f"| `{name}` | `{change['id']}` | `{change['field']}` | {was} | {now} |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--out", type=Path, default=None, help="default: the manifest's frozen dir")
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    frozen = REPO_ROOT / manifest["frozen_path"]
    out_dir = args.out or frozen
    key_path, dump = REPO_ROOT / manifest["key_path"], REPO_ROOT / manifest["predictions_path"]
    for path, expected, what in (
        (key_path, manifest["key_sha256"], "the blinding key"),
        (dump, manifest["predictions_sha256"], "the arm's dump"),
    ):
        if digest(path) != expected:
            raise SystemExit(
                f"{path}: sha256 is not the manifest's — {what} is not the audited one"
            )
    for name, expected in manifest["frozen_sha256"].items():
        if digest(frozen / name) != expected:
            raise SystemExit(
                f"{frozen / name}: sha256 is not the manifest's. v2 is immutable; a v2 file that"
                " already moved cannot be the base of v3."
            )

    key = json.loads(key_path.read_text(encoding="utf-8"))
    ruled = read_pack(REPO_ROOT / manifest["pack_path"], key)
    counts = {head: len(ids) for head, ids in ruled.items() if head not in LAW_PENDING}
    if counts != EXPECTED:
        raise SystemExit(
            f"the pack yields {counts}, the gate approved {EXPECTED}. The fixes are not the ones"
            " the gate ruled on, so nothing is written."
        )

    predicted: dict[str, dict[str, dict]] = {}
    for line in dump.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        predicted.setdefault(row["input"], {})[row["id"]] = row["pred"]
    aliases = watchlist_aliases(load_registry(args.registry).watchlist)
    applied = fixes(ruled, predicted, aliases)

    written, changes, shas = {}, {}, {}
    # Every input the audit's heads read gets a v3 file, including one that took no
    # fix: "v3" has to name a whole test set, or a later run scores two versions at
    # once and nothing in the record says which row came from where.
    for name in sorted({audit.INPUT_OF[head] for head in audit.HEADS}):
        source = frozen / f"{name}.jsonl"
        lines, changed = apply_to(
            source.read_text(encoding="utf-8").splitlines(), applied.get(name, {})
        )
        target = out_dir / f"{name}_v3.jsonl"
        body = "\n".join(lines) + "\n"
        target.write_text(body, encoding="utf-8")
        written[target.name] = {
            "rows": len(lines),
            "rows_changed": len({change["id"] for change in changed}),
            "fields_changed": len(changed),
        }
        changes[target.name] = changed
        shas[target.name] = sha256(body.encode("utf-8")).hexdigest()

    record = {
        "derived_by": "scripts/freeze_testsets_v3.py",
        "gate": "4.5 (operator, 2026-08-02): 38 point fixes from the blind audit",
        "law_pending": list(LAW_PENDING),
        "law_pending_rulings": {head: len(ruled[head]) for head in LAW_PENDING},
        "source": {
            "manifest": rel(args.manifest),
            "pack": manifest["pack_path"],
            "returns_record": "results/audit_45b_returns.json",
            "arm": manifest["arm"],
            "predictions_path": manifest["predictions_path"],
            "predictions_sha256": manifest["predictions_sha256"],
            "key_sha256": manifest["key_sha256"],
        },
        "v2_sha256": manifest["frozen_sha256"],
        "v3_sha256": shas,
        "rows": written,
        "fixes": counts,
        "changes": changes,
        "git": git_state(args.record),
    }
    args.record.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"v3 written to {rel(out_dir)} — v2 untouched")
    for name, sizes in written.items():
        print(
            f"  {name:<26} {sizes['rows']:>4} rows · {sizes['rows_changed']:>2} rows changed"
            f" ({sizes['fields_changed']} fields) · {shas[name][:16]}…"
        )
    print(f"  rulings applied: {counts} = {sum(counts.values())}")
    print(f"  intents: {len(ruled['intents'])} rulings derived, 0 applied (law pending)")
    print(f"\n{changelog_table(changes)}\n\nrecord: {rel(args.record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
