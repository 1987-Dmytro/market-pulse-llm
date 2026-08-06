#!/usr/bin/env python3
"""What the failed batch-16 run left behind — and why it is not the measurement.

SPEC amendment 3.11 (2)'s batch measurement got one attempt and lost it: the paid run at the
ladder's candidate N=16 scored comments_test 400/400 and posts_test 250/250 with zero failures,
then the worker raised `torch.OutOfMemoryError` on the second batch of sarcasm_holdout. The
eval re-raises an out-of-memory rather than charging it to rows (it is a fact about the
machine), so the process died before it wrote a record or a prediction dump. **The adoption
rule cannot run**: it requires every 4.5h2-passed gate to stay passing, those are G1b/G1d/G1e,
and G1b is the sarcasm-holdout slice — 16 of 108 rows. Under the amendment that fixes serving
at batch 1 permanently and returns the money question to the operator.

What survives is `--eval-checkpoint`, which was passed for exactly this: 666 rows with their
labels. This script reads them and answers the one question the operator's fork needs — *did
batch 16 change what the model said, or did it only run out of memory* — and writes the answer
into a record whose outcome says, at the top, that the measurement failed.

Deliberately NOT `parity_verdict_5b.py --batch`. That mode stamps a `parity` block into a
parity record and applies the adoption rule; a table of heads under a familiar name is
indistinguishable from the measurement's own output to the next reader. Everything here is
subordinate to `outcome`, and G1b is reported as missing rather than omitted.

    PYTHONPATH=src python3 scripts/salvage_5b2.py --checkpoint <parity-5b2.jsonl>
"""

import argparse
import importlib.util
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from market_pulse import scorer  # noqa: E402

RESULTS = REPO_ROOT / "results"
VERDICT = RESULTS / "batch_5b2_verdict.json"
CHECKPOINT = RESULTS / "batch_5b2_checkpoint.jsonl"
BATCH_1_DUMP = RESULTS / "predictions" / "google-gemma-4-31b-it--20260806T154612Z.jsonl"
BASELINE = RESULTS / "parity_5b_a.json"
LADDER = RESULTS / "batch_ladder_5b2.json"

COMPLETE = ("comments_test", "posts_test")
"""The two inputs the run finished. Named, because "the heads we could compute" is not a
description of a measurement — it is a description of where it stopped."""


def script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scored(checkpoint: Path) -> tuple[dict, dict]:
    """The checkpoint's header and its ``(input, id) -> labels``, refusing a row scored twice."""
    header, labels = None, {}
    for line in checkpoint.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if "header" in row:
            header = row["header"]
            continue
        outcome = row["outcome"]
        if "labels" not in outcome:  # a failed row carries a reason instead
            continue
        key = (row["input"], outcome["id"])
        if key in labels:
            raise SystemExit(f"{checkpoint} scored {key} twice — a checkpoint is append-once")
        labels[key] = outcome["labels"]
    if header is None:
        raise SystemExit(f"{checkpoint} has no header — it cannot say what produced it")
    return header, labels


def paired(runner, name: str, filename: str, labels: dict) -> tuple[list, list]:
    """The frozen rows of one input beside this run's labels, in file order.

    Refuses a partial input rather than scoring what is there: a head computed over the
    rows that happened to finish is a different measurement wearing the same name.
    """
    rows = runner.load(runner.FROZEN / filename)
    missing = [row["id"] for row in rows if (name, row["id"]) not in labels]
    if missing:
        raise SystemExit(
            f"{name}: {len(missing)} of {len(rows)} rows were never scored — this input is"
            " partial and no head may be computed from it"
        )
    return rows, [labels[(name, row["id"])] for row in rows]


def heads(runner, inputs: dict, aliases: dict) -> dict:
    """G1a and G1c on comments_test, G1d and G1e on posts_test — through the scorer.

    Called exactly as `eval_zero_shot.build_gates` calls them, argument for argument, because
    a number that reaches a table beside the batch-1 column has to have been produced the same
    way. `build_gates` itself cannot be reused: it takes all three inputs and computes G1b,
    which is the one this run does not have.
    """
    gold = runner.gold
    comments, comment_labels = inputs["comments_test"]
    posts, post_labels = inputs["posts_test"]
    return {
        "G1a": scorer.sentiment_macro_f1(
            gold(comments, "sentiment"),
            [x["sentiment"] for x in comment_labels],
            [row["language"] for row in comments],
        ),
        "G1c": scorer.intents_micro_f1(
            gold(comments, "intents", unclear=None), [x["intents"] for x in comment_labels]
        ),
        "G1d": scorer.launch_detection_macro_f1(
            gold(posts, "post_type"), [x["post_type"] for x in post_labels]
        ),
        "G1e": scorer.brand_extraction_f1(
            gold(posts, "brands", unclear=None), [x["brands"] for x in post_labels], aliases
        ),
    }


def agreement(labels: dict, dump: dict) -> dict:
    """Row for row against the batch-1 run, per input. The strongest thing here.

    Stronger than the heads, and reported first for that reason: four aggregates can hide two
    rows that moved in opposite directions, and a per-row count cannot.
    """
    shared = sorted(set(labels) & set(dump))
    per, agree = {}, []
    for key in shared:
        name = key[0]
        seen = per.setdefault(name, {"rows": 0, "agree": 0})
        seen["rows"] += 1
        if labels[key] == dump[key]:
            seen["agree"] += 1
            agree.append(key)
    differ = [key for key in shared if labels[key] != dump[key]]
    return {
        "compared": len(shared),
        "agree": len(agree),
        "rate": round(len(agree) / len(shared), 6) if shared else None,
        "per_input": {
            name: seen | {"rate": round(seen["agree"] / seen["rows"], 6)}
            for name, seen in sorted(per.items())
        },
        "disagreeing": [
            {
                "input": name,
                "id": row_id,
                "batch_1": dump[(name, row_id)],
                "batch_16": labels[(name, row_id)],
            }
            for name, row_id in differ
        ],
    }


def stamp_unadopted(path: Path, payload: dict, baseline: dict, usd_per_hour: float, cold: float):
    """What 5c reads when the measurement failed: the batch-1 numbers, said to be batch 1.

    `parity_verdict_5b.stamp_adopted` is the same idea for a measurement that ran; this one
    exists because the rule could not run at all, and the numbers therefore come from the
    batch-1 record rather than from the attempt. Written by a script and not by hand, for the
    reason every number in this repository is: a block typed into a record cannot be re-derived
    when someone asks where it came from.
    """
    timing = baseline["config"]["serving"]["timing"]
    rows = sum(block["rows"] for block in baseline["diagnostics"]["failures"])
    seconds_per_row = round(timing["wall_seconds"] / rows, 3)
    record = json.loads(path.read_text(encoding="utf-8"))
    record["adopted"] = {
        "decided_at": payload["written_at"],
        "batch_size": 1,
        "measured_at_batch_size": payload["attempt"]["batch_size"],
        "adopted": False,
        "why": payload["rule_could_not_run"],
        "rows": rows,
        "wall_seconds": timing["wall_seconds"],
        "seconds_per_row": seconds_per_row,
        "usd_per_hour": usd_per_hour,
        "usd_per_1000_rows": round(seconds_per_row * usd_per_hour / 3600 * 1000, 4),
        "cold_start_seconds": cold,
        "usd_per_pass": round((cold + rows * seconds_per_row) * usd_per_hour / 3600, 4),
        "source": (
            "results/batch_5b2_verdict.json — the batch measurement FAILED. These are the"
            " batch-1 numbers of results/parity_5b_a.json, which is what production still is."
        ),
        "note": (
            "seconds_per_row is the 5b.1 paid run's whole wall over its rows, so it carries the"
            " handshake call on an already-warm worker and no cold start; usd_per_pass adds the"
            " cold start once, which is what a stop-after pod pays per pass. SPEC amendment"
            " 3.11 (2) fixes serving at batch 1 permanently on a failed measurement — only a"
            " new pre-registered measurement may move it."
        ),
    }
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"record: {path} — batch 1 stays,"
        f" ${record['adopted']['usd_per_1000_rows']}/1000 rows,"
        f" ${record['adopted']['usd_per_pass']}/pass"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=CHECKPOINT)
    parser.add_argument("--serving-record", type=Path, help="stamp what 5c reads")
    parser.add_argument("--usd-per-hour", type=float, default=0.0)
    parser.add_argument(
        "--cold-start-seconds",
        type=float,
        default=0.0,
        help="measured this session; a stop-after pod pays it once per pass",
    )
    parser.add_argument("--baseline-record", type=Path, default=BASELINE)
    parser.add_argument("--ladder-record", type=Path, default=LADDER)
    parser.add_argument("--baseline-dump", type=Path, default=BATCH_1_DUMP)
    parser.add_argument("--verdict-out", type=Path, default=VERDICT)
    parser.add_argument("--blocker", required=True, help="one line: what ended the run")
    parser.add_argument("--evidence", action="append", default=[], help="repeatable, one fact")
    args = parser.parse_args(argv)

    runner, pv = script("eval_zero_shot"), script("parity_verdict_5b")
    header, labels = scored(args.checkpoint)
    counted = Counter(name for name, _ in labels)
    resolved = {name: filename for name, _, filename in runner.inputs_for("v4")}
    inputs = {name: paired(runner, name, resolved[name], labels) for name in COMPLETE}
    aliases = runner.watchlist_aliases(
        runner.load_registry(REPO_ROOT / "config" / "registry.yaml").watchlist
    )

    ladder = json.loads(args.ladder_record.read_text(encoding="utf-8"))
    worker_commit = (ladder.get("worker") or {}).get("repo_commit")
    if not worker_commit:
        raise SystemExit(
            f"{args.ladder_record} names no worker.repo_commit — the record could not then say"
            " which checkout produced its rows, and a verdict that cannot is not one"
        )

    bars, recorded = pv.bars_from_anchor()
    anchor = pv.anchor_values(recorded)
    base = pv.flat(runner.records.arm_values(json.loads(args.baseline_record.read_text("utf-8"))))
    now = heads(runner, inputs, aliases)
    rows = agreement(labels, pv.predictions(args.baseline_dump))

    print(f"batch size claimed by the checkpoint: {header.get('batch_size')}")
    print(f"rows with labels: {sum(counted.values())} — {dict(counted)}")
    print(f"\nrow agreement vs the batch-1 dump: {rows['agree']}/{rows['compared']}")
    for name, seen in rows["per_input"].items():
        print(f"  {name:<18} {seen['agree']:>4}/{seen['rows']:<5} {seen['rate']:.6f}")
    print(f"\n{'':22}{'batch 16':>12}{'batch 1':>12}{'4.5h2':>12}{'Δ vs 1':>11}{'bar':>12}")
    for head in ("G1a", "G1c", "G1d", "G1e"):
        value, was = pv.head_value(now[head]), pv.head_value(base[head])
        bar = bars[head].get("min", bars[head].get("min_fixed"))
        print(
            f"{head:22}{value:>12.4f}{was:>12.4f}{pv.head_value(anchor[head]):>12.4f}"
            f"{value - was:>+11.4f}{bar:>12.4f}"
        )
    print(
        "\nG1b                   NOT COMPUTABLE — 16 of 108 sarcasm_holdout rows. It is one of"
        "\n                      the three gates the adoption rule requires to stay passing,"
        "\n                      so the rule cannot run at all: batch 1 stays, permanently."
    )

    payload = {
        "outcome": "failed-measurement-oom",
        "step": "5b.2 batch measurement",
        "testset_version": "v4",
        "cap_usd": pv.CAP_USD,
        "written_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "adopted_batch_size": 1,
        "blocker": args.blocker,
        "evidence": args.evidence,
        "rule_could_not_run": (
            "SPEC amendment 3.11 (2) adopts N only if every 4.5h2-passed gate stays passing."
            " Those are G1b, G1d, G1e. G1b is the sarcasm_holdout slice and this run scored 16"
            " of 108 rows, so the rule has no input for it — an unmeasured gate is not a"
            " passing one. A failed measurement fixes serving at batch 1 permanently and"
            " returns the money question to the operator. One attempt, no retry, no second N."
        ),
        # Two commits, because they are two different things. `git` is this machine when the
        # salvage ran; `worker_repo_commit` is the pod's own checkout, which is what actually
        # generated the rows — read off the ladder record's `worker` block, where the worker
        # answered for itself ([[provenance_cannot_name_itself]]).
        "git": runner.git_state(),
        "worker_repo_commit": worker_commit,
        "attempt": {
            "batch_size": header.get("batch_size"),
            "adapter_sha256": header.get("adapter_sha256"),
            "prompt_revision_sha256": header.get("prompt_revision_sha256"),
            "rows_scored": dict(counted),
            "rows_expected": {"comments_test": 400, "posts_test": 250, "sarcasm_holdout": 108},
            "failures_before_the_oom": 0,
            "record_written": False,
            "predictions_dump_written": False,
        },
        "salvage": {
            "what_this_is": (
                "NOT the measurement. The checkpoint's rows, read after the fact, so the"
                " operator can tell 'batch 16 changed the answers' from 'batch 16 ran out of"
                " memory'. No bar moves, nothing is adopted, and G1b is absent rather than"
                " estimated.",
            ),
            "complete_inputs": list(COMPLETE),
            "row_agreement_vs_batch_1": rows,
            "heads": {"batch_16": now, "batch_1": base, "anchor_45h2": anchor, "bars": bars},
            "deltas_vs_batch_1": {
                head: round(pv.head_value(now[head]) - pv.head_value(base[head]), 6)
                for head in ("G1a", "G1c", "G1d", "G1e")
            },
            "g1b": "not computable — 16 of 108 sarcasm_holdout rows were scored",
        },
    }
    pv.write(args.verdict_out, payload)
    if args.serving_record:
        if not args.usd_per_hour:
            raise SystemExit("--serving-record needs --usd-per-hour: 5c reads a price")
        stamp_unadopted(
            args.serving_record,
            payload,
            json.loads(args.baseline_record.read_text(encoding="utf-8")),
            args.usd_per_hour,
            args.cold_start_seconds,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
