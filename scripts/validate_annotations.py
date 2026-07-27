#!/usr/bin/env python3
"""Check a labelled annotation batch against the guidelines and its pristine copy.

Run it after every labelling chunk — a red exit means the batch cannot be scored:
an illegal label value, a half-filled row, an edited record field or a lost row.
Coverage is the progress meter: labeled/total plus the per-label distributions.

    python3.11 scripts/validate_annotations.py data/annotation/comments_batch.jsonl
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse.annotation import check_batch
from market_pulse.registry import load_registry

SHOWN = 25


def load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path}: not found")
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def kind_of(path: Path) -> str:
    for kind in ("comments", "posts"):
        if kind in path.name:
            return kind
    raise SystemExit(f"{path.name}: cannot tell comments from posts by the file name")


def print_stats(stats: dict) -> None:
    print(
        f"coverage: {stats['labeled']}/{stats['total']} labelled"
        f" · {stats['partial']} half-done · {stats['unlabeled']} untouched"
    )
    print(f"unclear: {stats['unclear']} of the labelled ({stats['unclear_share']:.1%})")
    for name, counts in stats["dist"].items():
        print(f"\n  {name}")
        for value, count in sorted(counts.items(), key=lambda item: (-item[1], str(item[0]))):
            share = count / stats["labeled"] if stats["labeled"] else 0.0
            print(f"    {str(value):<24}{count:>7}{share:>8.1%}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", type=Path)
    parser.add_argument("--pristine", type=Path, help="default: <batch>.pristine.jsonl")
    parser.add_argument("--registry", type=Path, default=REPO_ROOT / "config" / "registry.yaml")
    parser.add_argument("--kind", choices=("comments", "posts"), help="default: from the file name")
    args = parser.parse_args(argv)

    pristine = args.pristine or args.batch.with_name(
        args.batch.name.replace(".jsonl", ".pristine.jsonl")
    )
    kind = args.kind or kind_of(args.batch)
    brand_ids = tuple(brand.brand_id for brand in load_registry(args.registry).watchlist)

    report = check_batch(load(args.batch), load(pristine), kind, brand_ids)
    print(f"{args.batch} ({kind}, pristine: {pristine})\n")
    print_stats(report.stats)

    if report.ok:
        print("\nVALID: no violations")
        return 0
    print(f"\n{len(report.violations)} violation(s):")
    for line in report.violations[:SHOWN]:
        print(f"  {line}")
    if len(report.violations) > SHOWN:
        print(f"  ... and {len(report.violations) - SHOWN} more")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
