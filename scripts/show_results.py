#!/usr/bin/env python3
"""Print `results/baselines.json`. The sanctioned way to look at a project number.

Read-only by design: it computes nothing and writes nothing, so a number shown
here can only have come from the scorer. A missing file is a loud failure, never
a blank table (SPEC §5, honesty rules).

    python3.11 scripts/show_results.py [--model tfidf-logreg] [--last]
    python3.11 scripts/show_results.py --gold v3   # the v3 re-scores beside their v2 numbers
"""

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS = REPO_ROOT / "results" / "baselines.json"
RESCORES = REPO_ROOT / "results" / "rescores_v3.json"


def render(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, dict):
        return "  ".join(f"{k} {render(v)}" for k, v in value.items())
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def show_v3(rescores: list[dict], history: dict) -> int:
    """The v3 re-scores beside the v2 numbers they correct — program measurements.

    A v3 row is what the same predictions would have scored had gold been right; the
    Tier-1 verdicts were decided once, against v2, and this view never restates them.
    """
    by_timestamp = {run["timestamp"]: run for runs in history.values() for run in runs}
    for record in rescores:
        source = by_timestamp[record["source"]["record_timestamp"]]
        arm = record["arm"] or "own-pod base (no adapter)"
        print(f"\n=== {record['model']} · {record['source']['record_timestamp']} · {arm}")
        print(f"gold v3 ({record['derivation']['frozen_v3_record']}) · v2 -> v3")
        for entry in record["gates"]:
            was = next(
                (
                    old.get("values", old.get("value"))
                    for old in source["gates"]
                    if old["gate"] == entry["gate"] and old["metric"] == entry["metric"]
                ),
                None,
            )
            now = entry.get("values", entry.get("value"))
            print(f"  {entry['gate']:<5} {entry['metric']:<40} {render(was)} -> {render(now)}")
        for name, block in record["g1b"].items():
            found = block["entry"]
            print(
                f"  G1b   {name + ' (n=' + str(block['n']) + ')':<40} "
                + (
                    f"{found['fixed']}/{found['n']['slice']} = {render(found['value'])}"
                    if found
                    else "— (a base run scores no fix-rate)"
                )
            )
        print(f"  note: {record['derivation']['note']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="show one model instead of all")
    parser.add_argument(
        "--last", action="store_true", help="only the most recent run of each model"
    )
    parser.add_argument(
        "--gold", choices=("v2", "v3"), default="v2", help="v3: the re-scores beside the v2 numbers"
    )
    args = parser.parse_args(argv)

    if not RESULTS.exists():
        raise SystemExit(f"{RESULTS}: no results file — run scripts/run_baseline.py first")
    history = json.loads(RESULTS.read_text(encoding="utf-8"))
    if args.gold == "v3":
        if not RESCORES.exists():
            raise SystemExit(f"{RESCORES}: no v3 re-scores — run scripts/rescore_v3.py first")
        return show_v3(json.loads(RESCORES.read_text(encoding="utf-8")), history)
    if args.model:
        if args.model not in history:
            raise SystemExit(
                f"{args.model}: not in {RESULTS.name} ({', '.join(history) or 'empty'})"
            )
        history = {args.model: history[args.model]}

    for model, runs in history.items():
        for run in runs[-1:] if args.last else runs:
            git = run["git"]
            code = [p for p in git["dirty"] if p.startswith(("src/", "scripts/", "config/"))]
            print(f"\n=== {model} · {run['timestamp']} ===")
            print(f"commit {git['commit'][:9]}" + (f" + uncommitted {code}" if code else ""))
            config = run["config"]
            print(f"seed {config['seed']} · {config['heads']['T1']}")
            print(f"{' ' * 13}{config['heads']['T2']}")
            print("  train " + render(config["train_sources"]))
            print("\n  gate  metric                                   value")
            for entry in run["gates"]:
                value = entry["values"] if "values" in entry else entry["value"]
                print(f"  {entry['gate']:<5} {entry['metric']:<40} {render(value)}")
                print(f"  {'':<5} {'n:':<40} {render(entry['n'])}")
                if entry.get("note"):
                    print(f"  {'':<5} note: {entry['note']}")
            print("\n  diagnostics (not gates)")
            for key, value in run["diagnostics"].items():
                if key != "note":
                    print(f"    {key:<44} {render(value)}")
            print(f"    {run['diagnostics']['note']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
