#!/usr/bin/env python3
"""`data/derived/` back to the bytes window 1 was sealed over; the C2 rows to `data/derived_w2/`.

**Why this exists.** Ruling 03.09 (b), fork 1. The C2 run appended its evidence to the SAME
per-channel files window 1's seal had hashed, so every w1 record that says «these bytes made this»
stopped being true — not because a number moved (all 4 474 data leaves of
`results/dashboard_data_w1.json` are identical) but because the statement about the store did. A
seal whose bytes move is not re-scoped into prose, it is restored, and the derived store splits the
way the raw store split on 30.08: `data/raw` frozen, `data/raw_r2` live.

**Where the split point comes from — the seal, not a guess.** For every one of the 38 sources
`results/window_summary_5c2.json` hashes, this script walks the file line by line and finds the k
whose prefix sha256 IS the sealed digest. That k is not read from a manifest and not inferred from
an id set: it is the boundary the seal itself proves, and a file for which no k exists stops the
run. 23 files resolve at k == their line count (untouched by C2), 15 at a shorter k (appended to).
A file the seal never named is wholly C2's and moves whole.

**Order of operations is the safety.** Plan → refuse → back up → COPY the tail to the C2 root →
VERIFY (every sealed prefix hashes to its sealed value, and w1 + w2 line counts add up to today's)
→ only then truncate. Nothing is deleted before its replacement has been written and checked
([[a_rebuild_deletes_its_output_before_it_can_refuse]]), and the backup exists before the first cut
because `data/` is gitignored and there is no second copy anywhere else.

    python3.11 scripts/split_derived_w2.py --dry-run   # the plan and the refusals, no write
    python3.11 scripts/split_derived_w2.py             # the split
"""

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SEAL = REPO_ROOT / "results" / "window_summary_5c2.json"
W1_ROOT = REPO_ROOT / "data" / "derived"
W2_ROOT = REPO_ROOT / "data" / "derived_w2"


def sealed_sources() -> dict[str, str]:
    """The 38 paths window 1 hashed, out of the sealed record itself."""
    record = json.loads(SEAL.read_text(encoding="utf-8"))
    return record["sources"]


def lines_of(path: Path) -> list[bytes]:
    """The file as newline-terminated lines. The store writes one JSON object per line and always
    ends with a newline, so a re-join of this list is the file byte for byte."""
    raw = path.read_bytes()
    if not raw:
        return []
    if not raw.endswith(b"\n"):
        raise SystemExit(f"{path}: does not end with a newline — not a store file this can split")
    return [line + b"\n" for line in raw.split(b"\n")[:-1]]


def seal_boundary(lines: list[bytes], digest: str) -> int | None:
    """How many leading lines hash to `digest`, or None. The empty prefix counts: a file the seal
    hashed as empty would resolve at 0 rather than looking like a file with no boundary."""
    running = hashlib.sha256()
    if running.hexdigest() == digest:
        return 0
    for k, line in enumerate(lines, 1):
        running.update(line)
        if running.hexdigest() == digest:
            return k
    return None


def store_files(root: Path) -> list[Path]:
    """Every channel file of every leg, sorted — the same `<record_type>s/<handle>.jsonl` layout
    `window_summary_5c2.leg_files` globs."""
    return sorted(p for d in sorted(root.iterdir()) if d.is_dir() for p in sorted(d.glob("*.jsonl")))


def plan(sealed: dict[str, str]) -> tuple[list[dict], list[str]]:
    """One row per file: where its w1 half ends and how many lines belong to C2. Plus the refusals.

    A sealed file whose digest no prefix reaches is the one thing this cannot proceed past: it would
    mean the C2 run did more than append, and the tail this script would cut is then not the tail.
    """
    rows, refusals = [], []
    seen = set()
    for path in store_files(W1_ROOT):
        rel = str(path.relative_to(REPO_ROOT))
        lines = lines_of(path)
        if rel not in sealed:
            rows.append({"path": path, "rel": rel, "keep": 0, "total": len(lines), "sealed": False})
            continue
        seen.add(rel)
        keep = seal_boundary(lines, sealed[rel])
        if keep is None:
            refusals.append(f"{rel}: no prefix of {len(lines)} lines hashes to the sealed digest")
            continue
        rows.append({"path": path, "rel": rel, "keep": keep, "total": len(lines), "sealed": True})
    for rel in sorted(set(sealed) - seen):
        refusals.append(f"{rel}: sealed source is not on disk")
    return rows, refusals


def verify(rows: list[dict], sealed: dict[str, str]) -> list[str]:
    """The closing arithmetic, run BEFORE the truncation and again after it.

    Three claims, and the third is the one a copy-then-cut can get wrong: the w1 prefix hashes to
    its sealed value, the C2 file holds the rest, and the two counts add up to what was on disk.
    """
    wrong = []
    for row in rows:
        w1_lines = lines_of(row["path"])[: row["keep"]] if row["path"].exists() else []
        if row["sealed"]:
            got = hashlib.sha256(b"".join(w1_lines)).hexdigest()
            if got != sealed[row["rel"]]:
                wrong.append(f"{row['rel']}: w1 half is {got[:16]}…, sealed {sealed[row['rel']][:16]}…")
        target = W2_ROOT / row["path"].relative_to(W1_ROOT)
        moved = len(lines_of(target)) if target.exists() else 0
        if row["keep"] + moved != row["total"]:
            wrong.append(
                f"{row['rel']}: {row['keep']} kept + {moved} moved != {row['total']} on disk today"
            )
    return wrong


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print the plan and stop")
    parser.add_argument(
        "--backup",
        type=Path,
        default=REPO_ROOT / "data" / "derived_backup_2026-09-03",
        help="where the whole store is copied before the first truncation",
    )
    args = parser.parse_args(argv)

    sealed = sealed_sources()
    rows, refusals = plan(sealed)
    if refusals:
        print(f"REFUSED: {len(refusals)} source(s) the seal cannot place", file=sys.stderr)
        for line in refusals:
            print(f"  {line}", file=sys.stderr)
        return 2

    grew = [r for r in rows if r["sealed"] and r["keep"] != r["total"]]
    same = [r for r in rows if r["sealed"] and r["keep"] == r["total"]]
    whole = [r for r in rows if not r["sealed"]]
    print(f"sealed sources placed   {len(same) + len(grew)}/{len(sealed)}")
    print(f"  unchanged by C2       {len(same)}")
    print(f"  appended to           {len(grew)}  ({sum(r['total'] - r['keep'] for r in grew)} lines to w2)")
    print(f"files the seal never named {len(whole)}  ({sum(r['total'] for r in whole)} lines to w2)")
    if args.dry_run:
        for row in grew + whole:
            print(f"  {row['rel']}  keep {row['keep']} of {row['total']}")
        return 0

    if W2_ROOT.exists() and any(W2_ROOT.rglob("*.jsonl")):
        print(f"REFUSED: {W2_ROOT} already holds store files — the split has already run", file=sys.stderr)
        return 2

    if args.backup.exists():
        print(f"REFUSED: backup {args.backup} already exists", file=sys.stderr)
        return 2
    shutil.copytree(W1_ROOT, args.backup)
    print(f"backed up {W1_ROOT} -> {args.backup}")

    for row in rows:
        tail = lines_of(row["path"])[row["keep"] :]
        if not tail:
            continue
        target = W2_ROOT / row["path"].relative_to(W1_ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"".join(tail))
    print(f"copied the C2 half -> {W2_ROOT}")

    wrong = verify(rows, sealed)
    if wrong:
        print(f"REFUSED before truncating: {len(wrong)} check(s) failed", file=sys.stderr)
        for line in wrong:
            print(f"  {line}", file=sys.stderr)
        return 2
    print("verified: every sealed prefix hashes to its seal, every line is accounted for")

    for row in rows:
        if row["keep"] == 0:
            row["path"].unlink()
        elif row["keep"] != row["total"]:
            row["path"].write_bytes(b"".join(lines_of(row["path"])[: row["keep"]]))
    print(f"truncated {len(grew)} file(s), removed {len(whole)} that the seal never named")

    after = {rel: hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest() for rel in sealed}
    broken = [rel for rel, got in after.items() if got != sealed[rel]]
    print(f"the seal, re-read from disk: {len(sealed) - len(broken)}/{len(sealed)} sources match")
    return 2 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
