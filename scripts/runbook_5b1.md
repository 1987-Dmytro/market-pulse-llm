# Runbook — Phase 5b.1: config A, scored once, on the runtime production will use

Copy-paste, in order. **Budget: the $3.4676 left under the $4.00 5b stop**, anchored in
`results/spend_5b.json` (never regenerated) and enforced by
`scripts/runpod_guard.py --step 5b --step-cap 4.00`. SPEC amendment 3.11 (2), as amended
2026-08-06: **config A alone, once, on the pod runtime. The pair is closed and config B is
dead.** One attempt, batch 1, no retry.

## What is different from 5b, and why each thing bites

| | 5b (aborted) | 5b.1 |
|---|---|---|
| where the weights run | a **serverless** endpoint that never took a job | a **stop-after pod**, A6000, CA-MTL-3 |
| how the worker is started | RunPod calls `/runpod-volume/start.sh` | the same `start.sh`, plus `--rp_serve_api` |
| where the driver runs | the Mac, over RunPod's API | **the pod**, over loopback |
| what the client talks to | `https://api.runpod.ai/v2/<id>/runsync` | `http://127.0.0.1:8000/runsync` |
| what is measured | which of two configs to ship | what the production runtime costs the gate numbers |

The stack under the HTTP is unchanged and that is the whole point: `start.sh` →
`serve_handler.py` → `market_pulse.local_llm`, the same chat template, the same
`add_special_tokens=False`, the same greedy `generate`. **Proven on the Mac before the pod
boots** — the real `Worker` behind the real SDK server with a stub loader answered `info` and
a batch, a raising handler came back as `ApiError`, and `assert_serving` refused a wrong
config (`implementation-notes.md`, Phase 5b.1).

**The driver runs on the pod, not on the Mac.** A 35-minute single-attempt run behind an SSH
tunnel makes the laptop's network a way to lose the phase's one authorised exposure of test
v4. `setsid nohup`, and the process is the liveness check — not the log.

**`timing.worker_seconds` is 0 on this transport, by construction.** The SDK's own server
reports no `executionTime`, so `seconds_per_call` reads 0 and `idle_share` null. `wall_seconds`
is the measurement, and on a pod it is also the billed quantity — which is simpler than
serverless, where they differ.

## Rulings taken BEFORE the pod boots

- **A crash is terminal.** SPEC: *"A failed attempt stops the line — aggregates cannot take
  serving numbers without this measurement."* `--eval-checkpoint` is passed so that a partial
  run leaves per-row evidence, and **it is never resumed**: resuming is the second attempt the
  amendment forbids. Fetch the checkpoint, report, stop.
- **The cost floor is not the serverless one.** `--stamp-cost` refuses a reading below the
  A6000 pod rate because serverless cannot bill under the class it runs on. A pod bills *at*
  that rate, so the same check would fire on a correctly-priced run. On the pod transport pass
  `--pod-usd-per-hour`, which puts the floor at half the machine's posted rate: what still has
  to be caught is an unsettled balance, and that reads as ~0.
- **Nothing is appended to `results/baselines.json`.** A serving row is not a gate anchor.
  (`records.anchor` narrows on `backend == "local"`, so it could not be selected as one — but
  the run does not offer it either.)
- **The smoke is 24 rows, the whole arm-A carve.** SPEC names "the 24-row arm-A carve"; the
  earlier brief said eight. 24 is a superset of that reading, costs about a cent, and gives
  the projection a per-rendering mean over more than four rows a side.

## 0. Before anything (Mac)

```bash
cd ~/Desktop/Projects/market-pulse-llm
git status --short                       # empty
make check                               # green
ruff format --check .                    # make check does not run the formatter
shasum -c results/raw_v1_baseline.sha256 # 6/6 — nothing here touches raw, prove it anyway
python3 scripts/runpod_guard.py --step 5b --step-cap 4.00
PYTHONPATH=src python3 scripts/smoke_5b.py --endpoint-id x --serving-config A --carve-only
runpodctl pod list -a && runpodctl serverless list     # both empty before, both empty after
```

The carve line costs nothing and is the check that matters most: it rebuilds the arm's carve
and refuses unless it hashes to `8347abd74ae9…`, the sha arm A's own provenance recorded.
**The smoke never opens a frozen test file** — the one paid run is test v4's only exposure.

## 1. The pod

A6000 in CA-MTL-3, because that is where the volume lives and a network volume pins the
region. `--terminate-after` is not optional.

```bash
COPYFILE_DISABLE=1 tar czf /tmp/raw-posts-5b1.tgz data/raw/posts     # ._* files break parents.load
git bundle create /tmp/market-pulse-5b1.bundle HEAD

runpodctl pod create --name mp-5b1 --gpu-id "NVIDIA RTX A6000" --gpu-count 1 \
  --network-volume-id gfwa2an8fn --data-center-ids CA-MTL-3 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after <UTC ISO8601, ~3 h out>
runpodctl pod list -a                    # exactly one pod, and its costPerHr
runpodctl ssh info <POD_ID>
```

## 2. Stage (the volume already holds the expensive half)

`gfwa2an8fn` carries the HF cache (`google/gemma-4-31b-it` at
`842da3794eaa0b77d5f08bae87a17459d91ff475`, 59 GB), the venv with the exact 4.5h2 stack, and
`/workspace/adapter_model.safetensors` from the 5b staging. Only the checkout and the raw
posts move.

```bash
SSHK=~/.runpod/ssh/runpodctl-ssh-key
SSHOPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
scp -i $SSHK $SSHOPT -P <PORT> /tmp/market-pulse-5b1.bundle /tmp/raw-posts-5b1.tgz root@<HOST>:/workspace/
```

On the pod — **the volume is `/workspace` here and `/runpod-volume` on a worker**, and
`start.sh` names the worker path:

```bash
ln -sfn /workspace /runpod-volume
cd /workspace && rm -rf repo && git clone -q market-pulse-5b1.bundle repo
cd repo && git rev-parse HEAD && git status --short          # equals the Mac's HEAD, empty
tar xzf /workspace/raw-posts-5b1.tgz -C /workspace/repo      # data/raw/posts is gitignored
cp /workspace/adapter_model.safetensors results/train/45h2-arm-a/adapter/
cp scripts/start_5b_worker.sh /workspace/start.sh && chmod +x /workspace/start.sh
/workspace/venv/bin/pip list | grep -Ei "^(torch|transformers|bitsandbytes|peft|runpod|fastapi|uvicorn) "
PYTHONPATH=src /workspace/venv/bin/python -c "
import sys; sys.path.insert(0,'src')
from pathlib import Path; from market_pulse import records
print(records.artifact_sha256(Path('results/train/45h2-arm-a/adapter')))"   # b3ca630846c7…
```

**List the venv rather than installing into it.** `runpod` pulls fastapi and uvicorn, so they
are already there from the 5b staging; a `pip install` that drags a newer torch turns config A
into a different instrument, and `assert_runtime_matches` would catch it 279 s into a cold
start — the expensive place to find out.

## 3. The free positive control, before the model loads

```bash
cd /workspace/repo && PYTHONPATH=src /workspace/venv/bin/python scripts/smoke_5b.py \
  --endpoint-id x --serving-config A --carve-only
```

This is the exact failure that killed 5b's `podcheck.py`: `data/raw/posts` is gitignored and
did not travel, so the carve rebuild died. It costs nothing here and the pod is already up.

## 4. The worker

```bash
cd /workspace/repo && setsid nohup bash /workspace/start.sh \
  --rp_serve_api --rp_api_host 127.0.0.1 --rp_api_port 8000 \
  > /workspace/out/worker.log 2>&1 < /dev/null &
pgrep -af serve_handler.py                 # the process is the liveness check
grep -m1 "Uvicorn running" /workspace/out/worker.log
```

The model loads lazily, at the first job — so uvicorn answers long before the worker can.
The cold start is paid by `info`, which has its own 1800 s budget.

## 5. The smoke, on the pod, and the projection, on the Mac

```bash
cd /workspace/repo && PYTHONPATH=src /workspace/venv/bin/python scripts/smoke_5b.py \
  --endpoint-id <POD_ID> --endpoint-url http://127.0.0.1:8000 --serving-config A --rows 24
```

PASS is three things: `info` names `adapter_sha256 b3ca630846c7…`, all 24 carve rows parse,
and the per-row seconds are in the region 4.5h2 measured (2.73 s/row). Then, on the Mac:

```bash
scp -i $SSHK $SSHOPT -P <PORT> root@<HOST>:/workspace/repo/results/serving_5b.json results/
python3 scripts/runpod_guard.py --step 5b --step-cap 4.00 --note "5b.1 staging + carve smoke"
PYTHONPATH=src python3 scripts/smoke_5b.py --stamp-cost <the guard's step delta> \
  --pod-usd-per-hour <costPerHr> --pod-id <POD_ID>
PYTHONPATH=src python3 scripts/parity_verdict_5b.py --project --runs 1 \
  --smoke-record results/serving_5b.json --spent-usd <5B SPENT from the guard> \
  --projection-out results/parity_5b1_projection.json \
  --verdict-out results/parity_5b1_verdict.json
```

`--runs 1` because the pair is closed, and the out-paths because
`results/parity_verdict_5b.json` is the committed verdict of the aborted pair and not a
scratch pad. Over the cap → the phase stops there and reports projections; the artifact is
already written.

## 6. The paid run — the phase's ONE paid event

```bash
cd /workspace/repo && mkdir -p /workspace/out && setsid nohup env PYTHONPATH=src \
  /workspace/venv/bin/python -u scripts/eval_zero_shot.py --model google/gemma-4-31b-it \
  --backend endpoint --endpoint-id <POD_ID> --endpoint-url http://127.0.0.1:8000 \
  --serving-config A --batch-size 1 --testset-version v4 \
  --adapter results/train/45h2-arm-a/adapter --arm without-plast \
  --eval-checkpoint /workspace/out/parity-5b1.jsonl \
  --record-out /workspace/out/parity_5b_a.json \
  > /workspace/out/parity-5b1.log 2>&1 < /dev/null &
pgrep -af eval_zero_shot                   # NOT a grep of the log for a success line
```

It refuses before the first row unless the worker's own `info` names the registered adapter
sha, merge state and quantization, and unless its library stack is the one 4.5h2 measured.

**Fetch everything before deleting the pod** — a partial run's only evidence is in these files:

```bash
scp -i $SSHK $SSHOPT -P <PORT> root@<HOST>:/workspace/out/parity_5b_a.json results/
scp -i $SSHK $SSHOPT -P <PORT> root@<HOST>:/workspace/out/parity-5b1.log results/train/
scp -i $SSHK $SSHOPT -P <PORT> root@<HOST>:/workspace/out/parity-5b1.jsonl /tmp/
scp -i $SSHK $SSHOPT -P <PORT> "root@<HOST>:/workspace/repo/results/predictions/*.jsonl" results/predictions/
scp -i $SSHK $SSHOPT -P <PORT> root@<HOST>:/workspace/repo/results/serving_5b.json results/
runpodctl pod delete <POD_ID> && runpodctl pod list -a       # deletion is PROVEN by the listing
python3 scripts/runpod_guard.py --step 5b --step-cap 4.00 --note "5b.1 config A scored on the pod"
```

## 7. The comparison

```bash
PYTHONPATH=src python3 scripts/parity_verdict_5b.py --single
```

Stamps the per-head numbers, the 4.5h2 anchors and the deltas into
`results/parity_5b_a.json`. **No bar moves**; a 4.5h2-passed head under its bar is printed as
a LOUD FINDING and goes to an operator briefing, not into a verdict here.

## When something goes wrong

- **The handshake times out.** `info()` has its own 1800 s budget. If it is not enough, the
  weights are not where `HF_HOME` says — check `/workspace/hf`, do not re-run the eval.
- **`assert_serving` or `assert_runtime_matches` refuses.** The pod is not serving what the
  phase registered. Do not pass the check by editing the expectation.
- **A row fails.** `retries=0` by design, and a failed attempt stops the line. Report it.
- **The projection is over the remaining headroom.** Stop. `--project` already wrote the
  artifact.
- **The guard exits 1.** A cap is not raised to finish a run.
- **A pod is left running.** `runpodctl pod list -a` after every session, and read the output:
  the volume alone bills ~$0.24/day whether or not anything is attached to it.
