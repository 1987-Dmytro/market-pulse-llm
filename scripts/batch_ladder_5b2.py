#!/usr/bin/env python3
"""The batch ladder: the same 24 carve rows at four batch sizes, and which N answers identically.

SPEC amendment 3.11 (2), the batch measurement pre-registered 2026-08-06: *"Candidate ladder
{16, 8, 4}: the 24-row carve is smoked at each N; the largest N whose carve outputs are
byte-identical to the batch-1 smoke picks the candidate (a pre-filter on training rows — no
test exposure); if none is identical, the candidate is 8."*

So this is a **pre-filter, not a gate**. It spends about two cents, opens no frozen test file,
and its only output is which N the one paid run is scored at. The rows are the arm's own
held-out carve, rebuilt and checked against the sha arm A's provenance recorded — the same
guard `scripts/smoke_5b.py` applies, imported from it rather than copied.

Three things this records that the answer depends on and a bare "identical: yes/no" would lose:

``chunks``
    which rows shared a padded batch with which. Byte-identity is a property of a row *and its
    neighbours* — greedy is not batch-invariant on this stack (ADR phase4-own-pod-anchor §(c),
    measured 2026-08-01), and the mechanism is padding and reduction order, not N as a number.
    The carve is 19 `T1v2_with_post` rows and 5 `T2`, and a call carries one rendering, so
    ``max_chunk`` at N=16 is 16 for T1 and 5 for T2. What was exercised is not what was asked.
``1-repeat``
    the batch-1 arm, run a second time and compared to the first. Without it "N differs from 1"
    cannot be told from "this stack differs from itself", and the whole ladder would be reading
    noise as a batching effect. It costs one arm's worth of seconds and it is the control.
``wall_seconds`` per row
    the chunk's wall divided by its rows. At batch N there is no per-row latency to measure —
    this is the definition the projection then uses, stated once here rather than assumed there.

    PYTHONPATH=src python3 scripts/batch_ladder_5b2.py \\
        --endpoint-id <POD_ID> --endpoint-url http://127.0.0.1:8000 --serving-config A
"""

import argparse
import importlib.util
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from market_pulse import prompts, records, serving  # noqa: E402

RECORD = REPO_ROOT / "results" / "batch_ladder_5b2.json"
ADAPTER = REPO_ROOT / "results" / "train" / "45h2-arm-a" / "adapter"

LADDER = (16, 8, 4)
"""SPEC amendment 3.11 (2)'s candidates, largest first — the order the rule reads them in."""

FALLBACK_N = 8
"""SPEC: *"if none is identical, the candidate is 8"*. Given that greedy is already **measured**
non-invariant on this stack, this is the expected path and not the exception."""

CARVE_ROWS = 24


def smoker():
    """`scripts/smoke_5b.py` as a module — the carve has one builder and one guard."""
    spec = importlib.util.spec_from_file_location("smoke_5b", REPO_ROOT / "scripts" / "smoke_5b.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def chunks(rows: list[dict], size: int) -> list[list[dict]]:
    """Rows grouped by rendering, then cut into batches of ``size``. Order preserved.

    One call carries one task, so a batch cannot straddle the two renderings — grouping
    first is what makes N mean the same thing for both. The carve's order inside a
    rendering is the carve's, never re-sorted: a row's neighbours are part of the answer.
    """
    out = []
    for task in sorted({row["task"] for row in rows}):
        group = [row for row in rows if row["task"] == task]
        out.extend(group[start : start + size] for start in range(0, len(group), size))
    return out


def run_arm(client, rows: list[dict], size: int) -> dict:
    """One pass over the carve at batch ``size``: every row's reply, and what it shared a call with.

    A chunk that raises is recorded and the arm is marked failed rather than raising on: an
    out-of-memory at N=16 is a ladder outcome ("this machine cannot serve 16"), which is exactly
    the kind of answer the ladder is for. The remaining arms still run.
    """
    scored, composition, failure = [], [], None
    started = time.monotonic()
    for index, chunk in enumerate(chunks(rows, size)):
        texts = [row["text"] for row in chunk]
        posts = [row["post"] for row in chunk] if any(row.get("post") for row in chunk) else None
        task = chunk[0]["task"]
        at = time.monotonic()
        try:
            replies = client.batch(task, texts, posts)
        except Exception as err:  # noqa: BLE001 — the arm's outcome, not this script's crash
            failure = f"chunk {index} ({task}, {len(chunk)} rows): {type(err).__name__}: {err}"
            break
        wall = time.monotonic() - at
        composition.append(
            {
                "chunk": index,
                "task": task,
                "rows": len(chunk),
                "ids": [row["id"] for row in chunk],
                "wall_seconds": round(wall, 3),
            }
        )
        for row, reply in zip(chunk, replies):
            parsed, parse_failure = None, None
            try:
                parsed = prompts.parse_reply(row["task"], reply["content"])
            except prompts.ParseError as err:
                parse_failure = err.reason
            scored.append(
                {
                    "id": row["id"],
                    "task": row["task"],
                    # the reply itself — the ladder's whole question is byte-identity, and a
                    # record that stored only "parsed: true" could not answer it afterwards
                    "content": reply["content"],
                    "finish_reason": reply.get("finish_reason"),
                    "parsed": parsed is not None,
                    "parse_failure": parse_failure,
                    "chunk": index,
                    "chunk_rows": len(chunk),
                    # a batch has no per-row latency; this is the definition, stated where it
                    # is made rather than assumed by whatever divides by it later
                    "wall_seconds": round(wall / len(chunk), 3),
                    "usage": reply.get("usage"),
                }
            )
    wall = time.monotonic() - started
    per_task = {}
    for entry in composition:
        per_task[entry["task"]] = max(per_task.get(entry["task"], 0), entry["rows"])
    return {
        "batch_size": size,
        "asked": len(rows),
        "scored": len(scored),
        "parsed": sum(1 for row in scored if row["parsed"]),
        "failed": failure,
        "calls": len(composition),
        "max_chunk_per_task": per_task,
        "wall_seconds": round(wall, 3),
        "seconds_per_row_wall": round(wall / len(scored), 3) if scored else None,
        "chunks": composition,
        "rows": scored,
    }


def compare(reference: dict, arm: dict) -> dict:
    """Is this arm byte-identical to the reference, and where is it not.

    Keyed by id and length-checked: an arm that lost rows to a failed chunk is **not**
    identical, however identical the rows it did produce are. A comparison that quietly
    ran over the intersection would report the missing rows as agreement.
    """
    if arm.get("failed") or arm["scored"] != reference["scored"]:
        return {
            "identical": False,
            "why": arm.get("failed")
            or f"{arm['scored']} rows against the reference's"
            f" {reference['scored']} — an arm that lost rows cannot be identical",
            "differing_ids": [],
        }
    was = {row["id"]: row["content"] for row in reference["rows"]}
    differ = [row["id"] for row in arm["rows"] if was.get(row["id"]) != row["content"]]
    first = next((row for row in arm["rows"] if row["id"] in differ), None)
    return {
        "identical": not differ,
        "why": "every reply is byte-identical to the batch-1 arm"
        if not differ
        else f"{len(differ)} of {arm['scored']} replies differ",
        "differing_ids": differ,
        "first_difference": None
        if first is None
        else {
            "id": first["id"],
            "task": first["task"],
            "chunk_rows": first.get("chunk_rows"),
            "batch_1": was[first["id"]],
            f"batch_{arm['batch_size']}": first["content"],
        },
    }


SELECTION_RULE = (
    "the largest N in {16, 8, 4} whose carve replies are byte-identical to the batch-1 arm;"
    " if none is identical the candidate is 8 (SPEC amendment 3.11 (2), pre-registered"
    " 2026-08-06, before any of these rows was generated)"
)


def candidate(verdicts: dict) -> dict:
    """The rule applied, with every condition's outcome beside the answer."""
    identical = [size for size in LADDER if verdicts[size]["identical"]]
    chosen = max(identical) if identical else FALLBACK_N
    return {
        "rule": SELECTION_RULE,
        "ladder": list(LADDER),
        "identical_to_batch_1": identical,
        "candidate": chosen,
        "by": "largest-identical" if identical else "spec-fallback-none-identical",
        "exercised_max_chunk": None,  # filled by main, which holds the arms
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint-id", required=True, help="the pod id, the record's label")
    parser.add_argument("--endpoint-url", default=serving.POD_BASE_URL)
    parser.add_argument("--serving-config", choices=("A", "B"), default="A")
    parser.add_argument("--adapter", type=Path, default=ADAPTER)
    parser.add_argument("--rows", type=int, default=CARVE_ROWS)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument(
        "--carve-only", action="store_true", help="rebuild and check the carve, send nothing"
    )
    args = parser.parse_args(argv)

    smoke = smoker()
    provenance = json.loads((args.adapter.parent / "provenance.json").read_text(encoding="utf-8"))
    carve, carve_sha, carve_n = smoke.carve_rows(provenance["carve_sha256"], args.rows)
    rows = [row | {"task": smoke.rendering(row["task"])} for row in carve]
    print(f"carve          {carve_sha} ({carve_n} rows, {len(rows)} asked)")
    for task in sorted({row["task"] for row in rows}):
        print(f"  {task:<18} {sum(1 for row in rows if row['task'] == task)} rows")
    print("  test v4 is NOT opened by this run — the carve is training data")
    if args.carve_only:
        return 0

    from eval_zero_shot import arm_runtime, runpod_api_key  # noqa: PLC0415

    key = "" if args.endpoint_url else runpod_api_key()
    client = serving.EndpointClient(args.endpoint_id, key, base_url=args.endpoint_url or None)
    info = serving.assert_serving(
        client.info(),
        {
            "serving_config": args.serving_config,
            "merge_state": "unmerged-adapter",
            "adapter_sha256": records.artifact_sha256(args.adapter),
        },
    )
    serving.assert_runtime_matches(info.get("runtime") or {}, arm_runtime())
    handshake = client.timing()
    print(f"endpoint       {args.endpoint_id} · config {args.serving_config}")
    print(f"  adapter      {info.get('adapter_sha256')}")
    print(f"  cold start   {handshake['wall_seconds']}s wall")

    # Batch 1 first, because it is what every other arm is compared against; then the repeat,
    # which is the control on the comparison itself; then the ladder, largest first.
    arms = {}
    print(f"\n{'arm':>10}{'calls':>8}{'scored':>8}{'parsed':>8}{'wall s':>10}{'s/row':>9}")
    for label, size in [("1", 1), ("1-repeat", 1), *[(str(n), n) for n in LADDER]]:
        arm = run_arm(client, rows, size)
        arms[label] = arm
        print(
            f"{label:>10}{arm['calls']:>8}{arm['scored']:>8}{arm['parsed']:>8}"
            f"{arm['wall_seconds']:>10.1f}{arm['seconds_per_row_wall'] or 0:>9.3f}"
            + ("   FAILED: " + arm["failed"] if arm["failed"] else "")
        )

    reference = arms["1"]
    control = compare(reference, arms["1-repeat"])
    verdicts = {size: compare(reference, arms[str(size)]) for size in LADDER}
    picked = candidate(verdicts) | {
        "exercised_max_chunk": {str(size): arms[str(size)]["max_chunk_per_task"] for size in LADDER}
    }

    print("\n--- byte-identity against the batch-1 arm ---")
    print(f"{'batch 1 repeat':>16}  {control['identical']!s:<6} {control['why']}")
    for size in LADDER:
        print(
            f"{'batch ' + str(size):>16}  {verdicts[size]['identical']!s:<6} {verdicts[size]['why']}"
        )
    print(f"\ncandidate N    {picked['candidate']}  ({picked['by']})")

    record = {
        "step": "5b.2 batch ladder",
        "written_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "endpoint_id": args.endpoint_id,
        "serving_config": args.serving_config,
        "transport": "pod-loopback" if args.endpoint_url else "serverless-api",
        "endpoint_url": args.endpoint_url or serving.BASE_URL,
        "worker": info,
        "carve": {"sha256": carve_sha, "n": carve_n, "asked": len(rows)},
        "cold_start": handshake,
        "prompt_sha256": {task: prompts.prompt_sha256(task) for task in prompts.TASKS},
        "arms": arms,
        "control": control,
        "verdicts": {str(size): verdicts[size] for size in LADDER},
        "selection": picked,
        "note": (
            "A PRE-FILTER, NOT A GATE. The rows are the arm's own held-out carve — training"
            " data — so nothing here is a gate number and no frozen test file was opened. The"
            " '1-repeat' arm is the control: if it is not identical to '1', this stack is not"
            " deterministic run to run and no verdict below it means anything. wall_seconds per"
            " row is the chunk's wall divided by its rows, which is the only per-row latency a"
            " batch has. max_chunk_per_task says what each N actually exercised: the carve holds"
            " 5 T2 rows, so no arm above 5 batches more than 5 of them."
        ),
    }
    args.record.parent.mkdir(parents=True, exist_ok=True)
    args.record.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"record         {args.record.relative_to(REPO_ROOT)}")

    if not control["identical"]:
        print(
            "\nSTOP AND REPORT: the batch-1 arm does not reproduce itself. Every identity"
            " verdict above is then a reading of noise, and the candidate cannot be picked"
            " from them."
        )
        return 3
    if any(arm["parsed"] != arm["scored"] for arm in arms.values()):
        print("\nSTOP AND REPORT: a carve row did not parse. The path is not proven at that N.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
