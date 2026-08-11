#!/usr/bin/env python3
"""Read the returned sku-a text pack: are the ticks legal, and what tier do they make? ($0)

The other half of deliverable 4(b) — "schema'd returns, validator". It reads
`data/annotation/sku_a_text/text30.csv` back after the operator has ticked it and answers three
questions, in this order:

1. **Is it the same pack?** The columns the operator was told not to touch are hashed in
   `results/sku_text_pack_manifest.json` and re-checked here. A row whose `text` moved is a row
   adjudicated against a different question.
2. **Are the answers in the schema?** Every tick cell is `y` or empty and nothing else. A `?`, a
   `1`, a «так» or a stray space is a refusal, not a guess — the same rule the reply parser follows.
3. **What tier does each row reach?** `positions.tier_from_presence`, the SAME function that tiers a
   model's answer. Empty in all five columns = no position at all, which is the pre-filter's own
   false positive and a legitimate answer.

**It computes no gate number.** Bar 3 of SPEC 3.17 (6) is scored in sku-b against the model's
answers; this only says what came back and whether it can be scored at all.

    PYTHONPATH=src python3 scripts/validate_sku_text_pack.py
"""

import argparse
import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_sku_text_pack as builder  # noqa: E402

from market_pulse import positions  # noqa: E402


def read_pack(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=builder.DELIMITER))


def check(rows: list[dict], manifest: dict) -> tuple[list[dict], list[str]]:
    """Every defect, named, and never repaired. Returns (readings, defects)."""
    defects = []
    if [row["id"] for row in rows] != manifest["ids"]:
        defects.append(
            f"the ids or their order moved: {len(rows)} rows against the manifest's"
            f" {len(manifest['ids'])}"
        )
    given = builder.given_sha256(rows) if not defects else None
    if given is not None and given != manifest["given_sha256"]:
        defects.append(
            f"the given columns hash {given[:16]}… and the manifest pins"
            f" {manifest['given_sha256'][:16]}… — a row was adjudicated against a different question"
        )
    if manifest["ladder"]["sha256"] != positions.ladder_sha256():
        defects.append(
            f"the ladder moved: this code hashes {positions.ladder_sha256()[:16]}… and the pack was"
            f" built against {manifest['ladder']['sha256'][:16]}…. The gold would move with it"
        )
    readings = []
    for row in rows:
        ticks = {}
        for field in positions.PRESENCE_FIELDS:
            # the CSV carries the dairy instruments' wire names (`fat`), the ladder takes the
            # schema's (`attribute`) — SPEC 3.17 (8). Reading `row[field]` here would find no
            # column, score every tick as blank and report 30 rows of `none`, silently.
            column = positions.wire_key(field)
            value = row.get(column) or ""
            if value not in builder.TICK_VALUES:
                defects.append(
                    f"{row['id']}: {column} is {value!r}, and the cell takes y or nothing"
                )
            ticks[field] = value == "y"
        readings.append(
            {
                "id": row["id"],
                "carrier": row["carrier"],
                "ticks": ticks,
                "tier": positions.tier_from_presence(**ticks) or "none",
                "notes": (row.get("notes") or "").strip(),
            }
        )
    return readings, defects


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=builder.PACK)
    parser.add_argument("--manifest", type=Path, default=builder.MANIFEST)
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    rows = read_pack(args.pack)
    readings, defects = check(rows, manifest)

    adjudicated = [row for row in readings if any(row["ticks"].values()) or row["notes"]]
    by_tier = {
        tier: sum(1 for row in readings if row["tier"] == tier)
        for tier in (*positions.TIERS, "none")
    }
    print(f"{builder.rel(args.pack)}  {len(rows)} rows · {len(adjudicated)} touched")
    print(f"  tiers from the ticks: {by_tier}")
    print(
        f"  ladder {positions.ladder_sha256()[:16]}… (manifest {manifest['ladder']['sha256'][:16]}…)"
    )
    for row in readings:
        if row["tier"] == "none" and any(row["ticks"].values()):
            print(f"  {row['id']}: ticks without a brand — no rung starts below one")
    if defects:
        print(f"\n{len(defects)} defect(s):")
        for defect in defects:
            print(f"  - {defect}")
        print("\nSTOP: nothing here is scoreable until they are fixed. No cell was repaired.")
        return 1
    blank = len(rows) - len(adjudicated)
    if blank:
        print(
            f"\n{blank} row(s) still untouched — the pack is not finished, and nothing is assumed."
        )
        return 0
    print("\nEvery row came back. Bar 3 is scored in sku-b, not here.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
