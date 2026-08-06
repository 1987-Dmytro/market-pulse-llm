#!/usr/bin/env python3
"""The 5b smoke: eight TRAIN-CARVE rows through the endpoint, and what they cost (D1).

`docs/PROMPT-5b.md` Deliverable 1 fixes the smoke at eight rows "drawn from the train carve
— NEVER from test v4 (no test exposure outside the one paid run)". So this exists instead of
`eval_zero_shot.py --probe`: every input that script knows about is a frozen test file, and
one probe through it would spend the phase's single attempt before the paid run.

The carve is `train_qlora.assemble`'s, rebuilt here and **checked against the sha the arm-A
adapter's own provenance recorded** (`8347abd7…`). That check is the whole reason this is
safe to call a carve run: the rows are reproducible, they are the ones the adapter held out,
and no frozen test file is opened at all. `carve_mechanics` on the 4.5h2 pod ran exactly this
path, so a reply that parses here parses for the same reason it did there.

What it measures — and Deliverable 1 says 5c reads this file to flip `run_loop.ENDPOINT`:

- the endpoint's own account of what it loaded, asserted against the registered config;
- latency per row, and the wall-clock span the endpoint was held, which is the unit
  serverless bills in;
- cold start, taken as the first call's wall time minus its executed time.

Nothing is scored against a gate and nothing is appended to `results/baselines.json`. The
carve is training data; a number from it measures the path, never the model.

    PYTHONPATH=src python3 scripts/smoke_5b.py --endpoint-id <id> --serving-config A \\
        --adapter results/train/45h2-arm-a/adapter
"""

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from market_pulse import prompts, records, serving  # noqa: E402

RECORD = REPO_ROOT / "results" / "serving_5b.json"
ADAPTER = REPO_ROOT / "results" / "train" / "45h2-arm-a" / "adapter"
SMOKE_ROWS = 8
"""PROMPT-5b Deliverable 1. Eight, not "a few": the projection divides by this."""


def trainer():
    """`scripts/train_qlora.py` as a module — the carve has exactly one builder."""
    spec = importlib.util.spec_from_file_location(
        "train_qlora", REPO_ROOT / "scripts" / "train_qlora.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def carve_rows(expected_sha: str, n: int) -> list[dict]:
    """The first ``n`` rows of the arm's own held-out carve, or a refusal.

    Rebuilt rather than read off disk, and then checked: a carve file that drifted,
    or a rebuild against moved training sources, would put test-adjacent rows into a
    run whose whole claim is that it touched no test data.
    """
    import yaml

    module = trainer()
    settings = yaml.safe_load(module.CONFIG.read_text(encoding="utf-8"))["training"]
    built = module.assemble(False, settings["carve_rows"], settings["seed"])
    digest = module.content_hash(built["carve"])
    if digest != expected_sha:
        raise SystemExit(
            f"the rebuilt carve hashes to {digest}, not the {expected_sha} the adapter's"
            " provenance recorded. These are not the rows arm A held out — stop and report."
        )
    if len(built["carve"]) < n:
        raise SystemExit(f"the carve holds {len(built['carve'])} rows, fewer than the {n} asked")
    return balanced(built["carve"], n), digest, len(built["carve"])


def balanced(carve: list[dict], n: int) -> list[dict]:
    """``n`` rows, round-robin across the tasks the carve holds. Deterministic.

    The carve is sorted, so a plain head slice comes back all-T1 and all-one-channel —
    and T2 is the rendering that carries the parent post, the one path that can fail on
    the worker with a missing parent the way `parents.text_for` refuses. A smoke that
    never renders it proves the half that was never in doubt.
    """
    tasks = sorted({row["task"] for row in carve})
    queues = {task: [row for row in carve if row["task"] == task] for task in tasks}
    picked = []
    while len(picked) < n and any(queues.values()):
        for task in tasks:
            if queues[task] and len(picked) < n:
                picked.append(queues[task].pop(0))
    return picked


POD_USD_PER_SECOND = 0.53 / 3600
"""What an A6000 **pod** costs, and therefore a floor no serverless rate can be under.

The derived dollars-per-second is `balance spent / wall seconds held`, and a balance
RunPod has not settled yet reads as almost no spend at all — which would make the
projection clear trivially and authorise a pair the phase cannot afford. Serverless
bills at a premium over the pod class it runs on, never below it, so a derived rate
under this floor means the reading is stale, not that the run was cheap.
"""

POD_FLOOR_SHARE = 0.5
"""The same guard, re-derived for the runtime SPEC amendment 3.11 (1) actually ships on.

On a **pod** the derived rate does not sit above the pod rate — it sits *at* it, so the
serverless inequality would fire on rounding, on a minute of boot the guard's balance delta
covers and the wall clock does not, or on the volume's own daily charge landing inside the
reading. Firing there would stop a run for being priced correctly. What the check still has
to catch is the unsettled balance, and that reads as **~0**, not as "a bit low". Half the
machine's posted rate separates those two cases and nothing else does.
"""


def cli(*args):
    out = subprocess.run(
        ["runpodctl", *args, "--output", "json"], capture_output=True, text=True, check=True
    )
    return json.loads(out.stdout)


def pod_deployment(pod_id: str) -> dict:
    """What RunPod says the **pod** is — image, GPU, volume, hourly price.

    Its own function because the smoke that measures a pod runs *on* that pod, where
    `runpodctl` does not exist and no API key is staged. So the record leaves the field
    pending and the Mac stamps it in afterwards — the shape `--stamp-cost` already
    established for the one number a run cannot know about itself.
    """
    try:
        pod = cli("pod", "get", pod_id)
    except (OSError, subprocess.CalledProcessError, ValueError, KeyError) as err:
        return {"unreadable": f"{type(err).__name__}: {err}"}
    if isinstance(pod, list):  # `pod get` answers with a one-row list
        pod = pod[0] if pod else {}
    return {"runtime": "pod", "pod": pod}


def deployment(endpoint_id: str) -> dict:
    """What RunPod itself says is deployed — image, start command, env, GPU, limits.

    Read back from the API rather than repeated from the create call: PROMPT-5b
    Deliverable 1 asks the record to name the image and the batch, and an image
    named from memory describes what was intended, not what is serving.
    """
    try:
        endpoint = cli("serverless", "get", endpoint_id)
        template = cli("template", "get", endpoint["templateId"])
    except (OSError, subprocess.CalledProcessError, ValueError, KeyError) as err:
        return {"unreadable": f"{type(err).__name__}: {err}"}
    return {
        "endpoint": {
            key: endpoint.get(key)
            for key in (
                "id",
                "name",
                "gpuIds",
                "locations",
                "workersMax",
                "idleTimeout",
                "executionTimeoutMs",
                "networkVolumeId",
                "templateId",
            )
        },
        "template": {
            key: template.get(key)
            for key in ("id", "imageName", "dockerStartCmd", "env", "containerDiskInGb")
        },
    }


def rendering(task: str) -> str:
    """The carve rows carry `T1`/`T2`; the endpoint renders the v4 revision of them."""
    return trainer().rendering(task)


def ask(client, rows: list[dict]) -> list[dict]:
    """One row per call, batch 1 — what the pair is scored at, and what this times."""
    out = []
    for row in rows:
        task = rendering(row["task"])
        before = client.timing()
        started = time.monotonic()
        reply = client.batch(task, [row["text"]], [row["post"]] if row.get("post") else None)[0]
        wall = time.monotonic() - started
        after = client.timing()
        parsed, failure = None, None
        try:
            parsed = prompts.parse_reply(task, reply["content"])
        except prompts.ParseError as err:
            failure = err.reason
        out.append(
            {
                "id": row["id"],
                "task": task,
                "finish_reason": reply.get("finish_reason"),
                "parsed": parsed is not None,
                "parse_failure": failure,
                "worker_seconds": round(
                    after["worker_seconds"] - (before["worker_seconds"] or 0), 3
                ),
                "wall_seconds": round(wall, 3),
                "usage": reply.get("usage"),
            }
        )
    return out


def stamp_cost(path: Path, usd: float, pod_usd_per_hour: float = 0.0, pod_id: str = "") -> dict:
    """The dollars the guard measured, written into the record after the fact.

    A run cannot know what it cost while it is running — RunPod settles the charge
    against the account balance, and `runpod_guard.py` is the only reader of that.
    So the same shape `poll_census.py --stamp-sidecar-sha` established: the record is
    written by the run, and the number that can only be known afterwards is stamped
    in, named, and timestamped. ``usd_per_second`` is that spend over the **wall**
    seconds the endpoint was held, which is what serverless bills.
    """
    record = json.loads(path.read_text(encoding="utf-8"))
    wall = record["timing"]["wall_seconds"]
    if not wall:
        raise SystemExit(f"{path} holds no wall_seconds — there is nothing to divide")
    rate = usd / wall
    floor = (
        POD_USD_PER_SECOND if not pod_usd_per_hour else pod_usd_per_hour / 3600 * POD_FLOOR_SHARE
    )
    record["cost"] = {
        "usd": round(usd, 4),
        "wall_seconds": wall,
        "usd_per_second": rate,
        "source": (
            "the pod's posted rate applied to the seconds this run held it; the rate itself is"
            " checked against results/spend_5b.json's balance delta over the pod's uptime"
            if pod_usd_per_hour
            else "results/spend_5b.json balance delta across this smoke, via runpod_guard.py"
        ),
        "stamped_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "floor_usd_per_second": floor,
        "floor_basis": (
            f"{POD_FLOOR_SHARE} x the pod's posted ${pod_usd_per_hour}/h — on a pod the derived"
            " rate lands AT the machine's rate, so the guard catches an unsettled balance (~0),"
            " not a rate that is merely lower than serverless would be"
            if pod_usd_per_hour
            else "the A6000 pod rate, which serverless cannot bill under"
        ),
        "above_pod_floor": rate >= floor,
    }
    if pod_id:
        record["deployment"] = pod_deployment(pod_id)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"usd            ${usd:.4f} over {wall}s wall")
    print(f"usd_per_second {rate:.8f}  (floor {floor:.8f})")
    if pod_id:
        print(f"deployment     stamped from runpodctl pod get {pod_id}")
    if rate < floor:
        print(
            "\nSTOP AND REPORT: the derived rate is BELOW the floor. The balance has not"
            " settled — re-read the guard and stamp again rather than projecting on this"
            " number.",
        )
        return 3
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint-id", default="", help="not needed with --stamp-cost")
    parser.add_argument(
        "--endpoint-url",
        default="",
        help="the pod runtime of SPEC amendment 3.11 (1): the worker's own server, e.g."
        f" {serving.POD_BASE_URL}. Without it the client talks to RunPod's serverless API,"
        " and --endpoint-id is the label the record carries either way",
    )
    parser.add_argument("--serving-config", choices=("A", "B"), default="")
    parser.add_argument("--adapter", type=Path, default=ADAPTER)
    parser.add_argument("--merged-sidecar", type=Path, help="config B: the merge sidecar")
    parser.add_argument("--rows", type=int, default=SMOKE_ROWS)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--carve-only", action="store_true", help="rebuild and check, no network")
    parser.add_argument(
        "--stamp-cost",
        type=float,
        metavar="USD",
        help="write the guard's measured spend into an existing record and derive $/s;"
        " scores nothing and sends no request",
    )
    parser.add_argument(
        "--pod-usd-per-hour",
        type=float,
        default=0.0,
        help="--stamp-cost on a pod: the machine's posted rate, which moves the floor off the"
        " serverless inequality onto one a correctly-priced pod run can pass",
    )
    parser.add_argument(
        "--pod-id",
        default="",
        help="--stamp-cost on a pod: fill the record's deployment block from runpodctl, which"
        " the pod-side run could not read for itself",
    )
    args = parser.parse_args(argv)

    if args.stamp_cost is not None:
        return stamp_cost(args.record, args.stamp_cost, args.pod_usd_per_hour, args.pod_id)
    if not (args.endpoint_id and args.serving_config):
        parser.error("--endpoint-id and --serving-config are required for a smoke run")

    provenance = json.loads((args.adapter.parent / "provenance.json").read_text(encoding="utf-8"))
    rows, carve_sha, carve_n = carve_rows(provenance["carve_sha256"], args.rows)
    print(f"carve          {carve_sha} ({carve_n} rows, {len(rows)} asked)")
    print(f"  ids          {[row['id'] for row in rows]}")
    print(f"  tasks        {sorted({row['task'] for row in rows})}")
    print("  test v4 is NOT opened by this run — the carve is training data")
    if args.carve_only:
        return 0

    merged = (
        json.loads(args.merged_sidecar.read_text(encoding="utf-8")) if args.merged_sidecar else None
    )
    expected = {
        "serving_config": args.serving_config,
        "merge_state": "merged-requantized" if merged else "unmerged-adapter",
        "adapter_sha256": (
            merged["adapter_sha256"] if merged else records.artifact_sha256(args.adapter)
        ),
    }
    if merged:
        expected["merged_sha256"] = merged["merged_sha256"]

    # eval_zero_shot's own key, so a script that imports it here needs no second copy
    from eval_zero_shot import arm_runtime, runpod_api_key  # noqa: PLC0415

    # A pod's own server authenticates nothing and is reached over loopback; asking for the
    # Mac's API key there would refuse a run for want of a credential it never sends.
    key = "" if args.endpoint_url else runpod_api_key()
    client = serving.EndpointClient(args.endpoint_id, key, base_url=args.endpoint_url or None)
    info = serving.assert_serving(client.info(), expected)
    serving.assert_runtime_matches(info.get("runtime") or {}, arm_runtime())
    handshake = client.timing()
    print(f"endpoint       {args.endpoint_id} · config {args.serving_config}")
    for field in ("merge_state", "adapter_sha256", "merged_sha256", "weights_dir"):
        print(f"  {field:<14} {info.get(field)}")
    print(f"  cold start    {handshake['wall_seconds']}s wall, {handshake['worker_seconds']}s exec")

    scored = ask(client, rows)
    timing = client.timing()
    parsed = sum(1 for row in scored if row["parsed"])
    # The handshake carried the cold start; the rows after it are the steady state.
    row_wall = (timing["wall_seconds"] or 0) - (handshake["wall_seconds"] or 0)
    per_row = round(row_wall / len(scored), 3) if scored else None
    record = {
        "step": "5b smoke",
        "written_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "endpoint_id": args.endpoint_id,
        "serving_config": args.serving_config,
        "batch_size": 1,
        "transport": "pod-loopback" if args.endpoint_url else "serverless-api",
        "endpoint_url": args.endpoint_url or serving.BASE_URL,
        "deployment": (
            {"pending": "runpodctl does not run on the pod — stamp with --stamp-cost --pod-id"}
            if args.endpoint_url
            else deployment(args.endpoint_id)
        ),
        "worker": info,
        "carve": {"sha256": carve_sha, "n": carve_n, "asked": len(rows)},
        "rows": scored,
        "parsed": parsed,
        "of": len(scored),
        "timing": timing,
        "cold_start": handshake,
        "seconds_per_row_wall": per_row,
        "prompt_sha256": {task: prompts.prompt_sha256(task) for task in prompts.TASKS},
        "note": (
            "MECHANICS AND LATENCY ONLY. The rows are the arm's own held-out carve — training"
            " data — so nothing here is a gate number and no frozen test file was opened."
            " seconds_per_row_wall excludes the cold start, which is reported separately"
            " because the projection scales the two differently."
            " On the pod transport timing.worker_seconds is 0 BY CONSTRUCTION: the worker's own"
            " server reports no executionTime, so seconds_per_call reads 0 and idle_share null."
            " wall_seconds is the measurement, and on a pod it is also the billed quantity."
        ),
    }
    args.record.parent.mkdir(parents=True, exist_ok=True)
    args.record.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"\nparsed         {parsed}/{len(scored)}")
    print(f"per row        {per_row}s wall (cold start excluded)")
    print(f"held           {timing['wall_seconds']}s wall, {timing['worker_seconds']}s executed")
    print(f"record         {args.record.relative_to(REPO_ROOT)}")
    if parsed != len(scored):
        print("\nSTOP AND REPORT: a carve row did not parse. The path is not proven.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
