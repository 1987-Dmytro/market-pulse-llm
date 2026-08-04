#!/usr/bin/env python3
"""Print the pre-registered Tier-1 bars, derived from the anchor record.

Read-only, and the only place the Phase 4 thresholds exist as numbers: SPEC
amendment 3.5 (1) says the anchors are read programmatically from the own-pod
zero-shot row and never hand-typed, so this is what 4c's gate verdict will call
and what a reviewer runs to see the same table without trusting prose. The G1b
slice is loaded through the SHA256 the anchor stored — `--slice` exists so that
refusal can be demonstrated on a tampered copy.

`--version` picks which frozen test set's anchor the bars come from; `--out` persists
them, because a bar that only ever existed in a terminal is not pre-registered.

    PYTHONPATH=src python3 scripts/gate_bars.py
    PYTHONPATH=src python3 scripts/gate_bars.py --version v4 --out results/gate_bars_45h.json
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse import records, scorer  # noqa: E402

RESULTS = REPO_ROOT / "results" / "baselines.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slice", type=Path, help="G1b slice file (default: the anchor's own)")
    parser.add_argument("--version", default=records.DEFAULT_TESTSET_VERSION)
    parser.add_argument("--out", type=Path, help="persist the derived bars")
    args = parser.parse_args(argv)

    try:
        anchor = records.anchor(json.loads(RESULTS.read_text(encoding="utf-8")), args.version)
        path = args.slice or REPO_ROOT / anchor["config"]["g1b_slice_path"]
        ids = records.slice_ids(path.read_text(encoding="utf-8"), anchor)
        values = records.anchor_values(anchor)
        bars = scorer.gate_thresholds(values, len(ids))
    except (ValueError, OSError) as err:
        raise SystemExit(f"refused: {err}") from None

    print(
        f"anchor: {anchor['model']} @ {anchor['timestamp']} ({anchor['git']['commit'][:7]})"
        f" — test set {args.version}"
    )
    print(f"slice:  {path.name} — {len(ids)} ids, sha256 verified against the record\n")
    print(f"{'gate':5} {'anchor':>8} {'bar':>8}  rule")
    print(f"G1a   {values['G1a']['overall']:8.4f} {bars['G1a']['min']:8.4f}  anchor + 5 pp overall")
    for language, floor in bars["G1a"]["floors"].items():
        print(f"  {language:3} {values['G1a'][language]:8.4f} {floor:8.4f}  anchor - 2 pp (floor)")
    print(
        f"G1b   {'—':>8} {bars['G1b']['min_fixed']:8d}  >= 60% of n={bars['G1b']['n']}, with"
        f" <= {bars['G1b']['max_macro_f1_drop'] * 100:.0f} pp overall macro-F1 loss"
    )
    print(f"G1c   {values['G1c']:8.4f} {bars['G1c']['min']:8.4f}  anchor + 5 pp")
    for gate in ("G1d", "G1e"):
        print(f"{gate}   {values[gate]:8.4f} {bars[gate]['min']:8.4f}  anchor - 1 pp (3.5 (2))")

    if args.out:
        args.out.write_text(
            json.dumps(
                {
                    "derived_by": "scripts/gate_bars.py",
                    "testset_version": args.version,
                    "rule": "SPEC amendment 3.5: G1a anchor + 5 pp with per-language floors at"
                    " anchor - 2 pp, G1b >= 60% of the slice with <= 2 pp macro-F1 loss, G1c"
                    " anchor + 5 pp, G1d/G1e anchor - 1 pp (no-regression). No number typed.",
                    "anchor": {
                        "model": anchor["model"],
                        "timestamp": anchor["timestamp"],
                        "commit": anchor["git"]["commit"],
                        "prompt_revision_sha256": anchor["config"].get("prompt_revision_sha256"),
                        "g1b_slice_path": anchor["config"]["g1b_slice_path"],
                        "g1b_slice_sha256": anchor["config"]["g1b_slice_sha256"],
                    },
                    "anchor_values": values,
                    "bars": bars,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
