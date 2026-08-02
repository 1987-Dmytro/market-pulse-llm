#!/usr/bin/env python3
"""Re-score every dumped run against the v3 test sets — from dumps only, no model calls (4.5c).

v3 fixed 38 gold rows the operator ruled wrong while blind. Every number the project
has published was measured against v2, and a corrected test set does not un-measure
them: it says what those same predictions would have scored had gold been right. That
is a program measurement, not a gate result, and this script only produces the first:

- **the predictions are the audited ones.** Each run's dump is verified against the
  sha256 its own record stored, and a run without a dump is named and skipped rather
  than quietly missing from the table. Nothing calls a model.
- **the judge is the same one.** ``eval_zero_shot.build_gates`` computes every head,
  so a v3 number and a v2 number come from one code path.
- **G1b is reported twice, and neither reading replaces Phase 4's verdict.** (a) the
  ORIGINAL 44-id slice re-scored against v3, comparable row-for-row with the verdict
  row; (b) the slice recomputed from the base model's own v3 errors, with its own n.
  The base model's error set moves when gold moves, and a fix-rate over a different
  denominator is a different question — so both are printed and labelled.

    python3.11 scripts/rescore_v3.py

Appends to ``results/rescores_v3.json``; `results/baselines.json` is never written.
"""

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))  # build_gates lives with the eval

import eval_zero_shot as evaluator  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

RESULTS = REPO_ROOT / "results" / "baselines.json"
FROZEN_V3 = REPO_ROOT / "results" / "frozen_v3.json"
OUT = REPO_ROOT / "results" / "rescores_v3.json"
SLICE = REPO_ROOT / "results" / "g1b_slice.json"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
INPUTS = ("comments_test", "posts_test", "sarcasm_holdout")


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def dumped(history: dict) -> tuple[list[dict], list[str]]:
    """Runs whose per-row predictions still exist, and the names of those without.

    The six 3b zero-shot rows carry only a hash of the id list, so they cannot be
    re-scored at all. They are printed rather than dropped: a table that silently
    covers half the runs reads as if it covered all of them.
    """
    with_dump, without = [], []
    for model, runs in history.items():
        for run in runs:
            if run.get("config", {}).get("predictions_path"):
                with_dump.append(run)
            else:
                without.append(f"{model} @ {run['timestamp']}")
    return with_dump, without


def labels_for(predicted: dict, rows: list[dict], name: str, run: str) -> list[dict]:
    """The dump's predictions in the gold rows' order — or a stop naming what is missing."""
    missing = [row["id"] for row in rows if row["id"] not in predicted.get(name, {})]
    if missing:
        raise SystemExit(
            f"{run}: {len(missing)} rows of {name} are not in the dump ({missing[:3]}). A partial"
            " re-score is not a re-score; the dump is the only prediction source here."
        )
    return [predicted[name][row["id"]] for row in rows]


def gate_value(record: dict, gate: str, metric_starts: str):
    for entry in record["gates"]:
        if entry["gate"] == gate and entry["metric"].startswith(metric_starts):
            return entry.get("values", entry.get("value"))
    return None


def rescore(run: dict, gold: dict, aliases: dict, gate_slice: dict | None) -> dict:
    """One run's heads under v3, through the same builder the gates were scored with."""
    path = REPO_ROOT / run["config"]["predictions_path"]
    found = digest(path)
    if found != run["config"]["predictions_sha256"]:
        raise SystemExit(
            f"{path}: sha256 {found}, the record says {run['config']['predictions_sha256']}."
            " These are not the predictions that were scored, so re-scoring them measures"
            " something else."
        )
    predicted: dict[str, dict[str, dict]] = {}
    for row in load_jsonl(path):
        predicted.setdefault(row["input"], {})[row["id"]] = row["pred"]
    name = f"{run['model']} @ {run['timestamp']}"
    inputs = {
        input_name: (gold[input_name], labels_for(predicted, gold[input_name], input_name, name))
        for input_name in INPUTS
    }
    gates, diagnostics, slice_ids = evaluator.build_gates(inputs, aliases, gate_slice)
    return {"gates": gates, "diagnostics": diagnostics, "slice_ids": slice_ids, "inputs": inputs}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=RESULTS)
    parser.add_argument("--frozen-v3", type=Path, default=FROZEN_V3)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--frozen", type=Path, default=REPO_ROOT / "data" / "frozen")
    parser.add_argument("--slice", dest="slice_path", type=Path, default=SLICE)
    args = parser.parse_args(argv)

    frozen_v3 = json.loads(args.frozen_v3.read_text(encoding="utf-8"))
    gold = {}
    for name in INPUTS:
        path = args.frozen / f"{name}_v3.jsonl"
        expected = frozen_v3["v3_sha256"][path.name]
        if digest(path) != expected:
            raise SystemExit(f"{path}: sha256 is not {args.frozen_v3.name}'s — v3 moved")
        gold[name] = load_jsonl(path)

    history = json.loads(args.results.read_text(encoding="utf-8"))
    runs, without = dumped(history)
    for name in without:
        print(f"SKIPPED, no per-row dump: {name}")
    aliases = watchlist_aliases(load_registry(args.registry).watchlist)

    base = [run for run in runs if not run["config"].get("fine_tune")]
    if len(base) != 1:
        raise SystemExit(
            f"expected exactly one dumped run without an adapter, found {len(base)}."
            " The base model's v3 errors are what the second G1b reading is defined from."
        )
    base_v3 = rescore(base[0], gold, aliases, None)
    anchor_overall = gate_value(  # the ≤2 pp guard is measured against the anchor, under v3
        {"gates": base_v3["gates"]}, "G1a", "sentiment macro-F1"
    )["overall"]
    v3_slice = base_v3["slice_ids"]["union"]
    original_slice = json.loads(args.slice_path.read_text(encoding="utf-8"))["ids"]

    written = []
    for run in runs:
        arm = (run["config"].get("fine_tune") or {}).get("arm")
        if arm is None:
            result, g1b_v3_slice = base_v3, None
        else:
            result = rescore(
                run, gold, aliases, {"ids": original_slice, "anchor_overall": anchor_overall}
            )
            holdout, holdout_labels = result["inputs"]["sarcasm_holdout"]
            g1b_v3_slice = evaluator.g1b_fix_rate(
                holdout,
                holdout_labels,
                {"ids": v3_slice, "anchor_overall": anchor_overall},
                gate_value({"gates": result["gates"]}, "G1a", "sentiment macro-F1")["overall"],
            )
        written.append(
            {
                "gold_version": "v3",
                "model": run["model"],
                "arm": arm,
                "source": {
                    "record_timestamp": run["timestamp"],
                    "predictions_path": run["config"]["predictions_path"],
                    "predictions_sha256": run["config"]["predictions_sha256"],
                    "gold_v2_sha256": frozen_v3["v2_sha256"],
                },
                "derivation": {
                    "rescored_by": "scripts/rescore_v3.py",
                    "judge": "scripts/eval_zero_shot.py:build_gates",
                    "frozen_v3_record": rel(args.frozen_v3),
                    "v3_sha256": frozen_v3["v3_sha256"],
                    "note": (
                        "a program measurement of a corrected test set, never a gate result:"
                        " the Tier-1 verdicts of Phase 4 were decided once, against v2"
                    ),
                },
                "gates": result["gates"],
                "diagnostics": result["diagnostics"],
                "g1b": {
                    "original_slice": {
                        "definition": (
                            "the pre-registered 44 ids of results/g1b_slice.json, re-scored vs v3"
                            " — the reading comparable with the Phase 4 verdict row"
                        ),
                        "n": len(original_slice),
                        "entry": next(
                            (e for e in result["gates"] if e["gate"] == "G1b" and arm), None
                        ),
                    },
                    "v3_slice": {
                        "definition": (
                            "the base model's error union recomputed vs v3 from its own dump — a"
                            " different denominator, so a different question"
                        ),
                        "n": len(v3_slice),
                        "ids": v3_slice,
                        "entry": g1b_v3_slice,
                    },
                },
            }
        )

    done = json.loads(args.out.read_text(encoding="utf-8")) if args.out.exists() else []
    fresh = [
        record
        for record in written
        if not any(
            old["source"]["record_timestamp"] == record["source"]["record_timestamp"]
            and old["derivation"]["v3_sha256"] == record["derivation"]["v3_sha256"]
            for old in done
        )
    ]
    args.out.write_text(
        json.dumps(done + fresh, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\n{len(fresh)} record(s) appended to {rel(args.out)} ({len(done)} already there)\n")

    print(
        f"v2 | v3, every dumped run · G1b slice under v3: n={len(v3_slice)} (v2: {len(original_slice)})"
    )
    for run, record in zip(runs, written):
        label = record["arm"] or "own-pod base (no adapter)"
        print(f"\n=== {run['model']} @ {run['timestamp']} · {label}")
        for gate, metric in (
            ("G1a", "sentiment macro-F1"),
            ("G1c", "intents micro-F1"),
            ("G1d", "post_type macro-F1"),
            ("G1d", "relevance macro-F1"),
            ("G1e", "brand extraction F1"),
        ):
            was, now = gate_value(run, gate, metric), gate_value(record, gate, metric)
            # A v2 record may carry a key this one does not (or none at all): the table
            # says so rather than raising, because it is printed beside a stop-on-defect
            # pipeline and a formatting crash here would look like a data defect.
            for key, value in (now or {}).items() if isinstance(now, dict) else ((None, now),):
                before = (was or {}).get(key) if isinstance(was, dict) else was
                label = f"{metric} {key}" if key else metric
                print(
                    f"  {gate:<4} {label:<34}"
                    f" {'—' if before is None else format(before, '.4f')} ->"
                    f" {'—' if value is None else format(value, '.4f')}"
                )
        was = next((entry for entry in run["gates"] if entry["gate"] == "G1b"), {})
        for title, block in (
            ("original slice", record["g1b"]["original_slice"]),
            ("v3 slice, v3 only", record["g1b"]["v3_slice"]),
        ):
            entry = block["entry"]
            if entry is None:
                print(f"  G1b  {title} (n={block['n']}){'':<11} — (a base run scores no fix-rate)")
                continue
            before = (
                f"{was['fixed']}/{was['n']['slice']} = {was['value']:.4f}"
                if title == "original slice" and was.get("value") is not None
                else "—"
            )
            print(
                f"  G1b  {title} (n={block['n']}){'':<11} {before} ->"
                f" {entry['fixed']}/{entry['n']['slice']} = {entry['value']:.4f}"
            )
    print(
        "\nProgram measurements. The Tier-1 verdicts of Phase 4 stand against v2 and are not reopened."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
