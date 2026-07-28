#!/usr/bin/env python3
"""Print `results/baselines.json`. The sanctioned way to look at a project number.

Read-only by design: it computes nothing and writes nothing, so a number shown
here can only have come from the scorer. A missing file is a loud failure, never
a blank table (SPEC §5, honesty rules).

    python3.11 scripts/show_results.py [--model tfidf-logreg] [--last]
"""

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS = REPO_ROOT / "results" / "baselines.json"


def render(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, dict):
        return "  ".join(f"{k} {render(v)}" for k, v in value.items())
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="show one model instead of all")
    parser.add_argument(
        "--last", action="store_true", help="only the most recent run of each model"
    )
    args = parser.parse_args(argv)

    if not RESULTS.exists():
        raise SystemExit(f"{RESULTS}: no results file — run scripts/run_baseline.py first")
    history = json.loads(RESULTS.read_text(encoding="utf-8"))
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
