# Runbook — Phase 5b: serving parity on the production serverless runtime

> **STOP — §3 onwards did not run, and following them costs money for nothing.**
> On **2026-08-06** no RunPod serverless endpoint on this account reached a job-consuming
> worker. Five endpoints across four configurations left their jobs `IN_QUEUE`, and so did
> **RunPod's own hub vLLM worker** — their template, their image, no network volume, no
> datacenter pin, none of this project's code. The verdict and the seven observations behind
> it are in `results/parity_verdict_5b.json` (`outcome: aborted-runtime-unreachable`, shipped
> A). §1–2 below are **proven and worth reusing**: the volume is staged and the worker
> answered correctly on a pod. §3–6 are written but unexecuted, and they must not be run
> until the runtime question is answered — see implementation-notes.md, "three cheapest
> readings".

Copy-paste, in order. **Budget: $4.00 of the $8 Phase-5 cap**, anchored in
`results/spend_5b.json` and enforced before every start by
`scripts/runpod_guard.py --step 5b --step-cap 4.00`. The anchor is committed and is never
regenerated. The pair is scored **once each**; a crashed or aborted run closes the merge
question in favour of A (SPEC amendment 3.11 (2)) and nothing is retried. **$0.5324 of the
$4.00 was spent reaching the abort; $3.47 is unspent.**

---

## What is different from 4.5h2, and why each thing bites

| | 4.5h2 | 5b |
|---|---|---|
| where the weights run | a pod this session owns | a **serverless** endpoint |
| the image | `runpod/pytorch:…` + `pip install -e .` | the same image, **unchanged** |
| where the code lives | the pod's container disk | the **network volume**, `/runpod-volume/repo` |
| the mount path | `/workspace` | `/workspace` on a pod, **`/runpod-volume` on a worker** |
| what is measured | which arm to keep | what the runtime costs the gate numbers |
| the client | `local_llm.LocalClient` in-process | `serving.EndpointClient` over HTTP — **same worker-side client** |

**There are no container-registry credentials for this project** (`runpodctl registry list`
→ `null`, `~/.docker/config.json` has empty `auths`). A custom worker image cannot be
pushed, so the stock image runs `/runpod-volume/start.sh`, which execs this repo's
`scripts/serve_handler.py` out of a venv on the volume. Every 5b artifact lives on the
volume; nothing is baked.

**The volume already held most of it.** `gfwa2an8fn` (100 GB, CA-MTL-3) carries Phase 4a's
`hf/` cache — `google/gemma-4-31b-it` at the pinned revision
`842da3794eaa0b77d5f08bae87a17459d91ff475`, 59 GB — and a venv with the exact stack the
4.5h2 record names: torch 2.8.0+cu128, transformers 5.14.1, bitsandbytes 0.50.0. That is
why config A is a replica and not a rebuild. Only `peft` and `runpod` had to be added.

## 0. Before anything (Mac)

```bash
cd ~/Desktop/Projects/market-pulse-llm
git status --short                       # empty
make check                               # green
ruff format --check .                    # make check does not run the formatter
python3 scripts/runpod_guard.py --step 5b --step-cap 4.00
PYTHONPATH=src python3 scripts/smoke_5b.py --endpoint-id x --serving-config A --carve-only
```

The last line costs nothing and is the check that matters most: it rebuilds the arm's carve
and refuses unless it hashes to `8347abd74ae9…`, the sha arm A's own provenance recorded.
**The smoke never opens a frozen test file** — the one paid run is test v4's only exposure.

## 1. The staging pod (one session, ~15 min, $0.53/h) — DONE, the volume is staged

A6000 in CA-MTL-3, because that is where the volume lives and a network volume pins the
region. `runpodctl datacenter list` reported A6000 stock as `""`/`none` there and the pod
created anyway — **the stock field is not a reservation and not a refusal; the create call
is the only real test.** Probe by creating one pod at a time and delete it the moment it is
not the one you want: a loop that creates before it reads bills every hit.

```bash
runpodctl pod create --name mp-5b-stage --gpu-id "NVIDIA RTX A6000" --gpu-count 1 \
  --network-volume-id gfwa2an8fn --data-center-ids CA-MTL-3 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after <UTC ISO8601, a couple of hours out>
runpodctl pod list -a                    # confirm exactly one pod, and its costPerHr
runpodctl ssh info <POD_ID>
```

`--terminate-after` is not optional. A staging pod is small enough to forget and bills the
same as a working one.

```bash
SSHK=~/.runpod/ssh/runpodctl-ssh-key
SSHOPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

git bundle create /tmp/market-pulse-5b.bundle HEAD
scp -i $SSHK $SSHOPT -P <PORT> /tmp/market-pulse-5b.bundle root@<HOST>:/workspace/
scp -i $SSHK $SSHOPT -P <PORT> results/train/45h2-arm-a/adapter/adapter_model.safetensors \
    root@<HOST>:/workspace/adapter_model.safetensors      # 467 MB, gitignored — ~3 min
```

On the pod — **the volume is `/workspace` here and `/runpod-volume` on a worker**:

```bash
cd /workspace && rm -rf repo && git clone -q market-pulse-5b.bundle repo
cd repo && git rev-parse HEAD && git status --short          # equals the Mac's HEAD, empty
cp /workspace/adapter_model.safetensors results/train/45h2-arm-a/adapter/
PYTHONPATH=src /workspace/venv/bin/python -c "
from pathlib import Path; import sys; sys.path.insert(0,'src')
from market_pulse import records
print(records.artifact_sha256(Path('results/train/45h2-arm-a/adapter')))"   # b3ca630846c7…
/workspace/venv/bin/pip install -q peft runpod
cp scripts/start_5b_worker.sh /workspace/start.sh && chmod +x /workspace/start.sh
```

## 2. Prove the cold start ON THE POD, before a serverless second is billed — DONE, 278.9 s

The pod bills $0.53/h; the serverless class bills ~3× that, and a cold start that fails
there costs the boot *and* the handshake. So the worker's real load path runs here first:

```bash
setsid nohup env SERVING_CONFIG=A BASE_WEIGHTS=google/gemma-4-31b-it \
  ADAPTER_DIR=/workspace/repo/results/train/45h2-arm-a/adapter \
  MODEL_REVISION=842da3794eaa0b77d5f08bae87a17459d91ff475 \
  HF_HOME=/workspace/hf HF_HUB_OFFLINE=1 \
  /workspace/venv/bin/python -u /workspace/podcheck.py > /workspace/podcheck.log 2>&1 &
pgrep -af podcheck.py             # the process is the liveness check, not the log
```

`HF_HUB_OFFLINE=1` is load-bearing: without it a cold start can decide to re-fetch 59 GB at
worker rates, and nothing in the log would say that is what it is doing.

PASS is three things: the `info` block names `adapter_sha256 b3ca630846c7…`, all eight carve
rows parse, and the per-row seconds are in the region 4.5h2 measured (2.73 s/row). Any of
them failing is a staging problem, and it is far cheaper to see it here.

**Then delete the pod** and log the reading:

```bash
runpodctl pod delete <POD_ID>
python3 scripts/runpod_guard.py --step 5b --step-cap 4.00 --note "5b staging + pod cold-start proof"
```

## 3. The endpoint (creation is free; workers bill only on a request) — BLOCKED, unexecuted

```bash
runpodctl template create --name market-pulse-5b-a --serverless \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --docker-start-cmd "bash,/runpod-volume/start.sh" \
  --env '{"SERVING_CONFIG":"A","ADAPTER_DIR":"/runpod-volume/repo/results/train/45h2-arm-a/adapter","BASE_WEIGHTS":"google/gemma-4-31b-it","MODEL_REVISION":"842da3794eaa0b77d5f08bae87a17459d91ff475","HF_HOME":"/runpod-volume/hf"}'

runpodctl serverless create --name market-pulse-5b-a --template-id <TEMPLATE_ID> \
  --gpu-id "NVIDIA RTX A6000" --gpu-count 1 --workers-max 1 \
  --network-volume-id gfwa2an8fn --data-center-ids CA-MTL-3 \
  --idle-timeout 60 --execution-timeout 900 --flash-boot
```

Three flags are money and two of them default wrong:

- **`--workers-max 1`.** The default is 3, and 758 sequential `runsync` calls will happily
  spin up three workers — three 31 B cold starts, all billed, for a run that is batch 1 by
  contract.
- **`--execution-timeout 900`.** The default is `-1`. The flag takes **seconds** and stores
  milliseconds: `--execution-timeout 600000` becomes a 600 000-second ceiling, which is a
  week of a hung worker. `serverless update` cannot change it — delete and recreate.
- **`--idle-timeout 60`.** Long enough that sequential rows keep one warm worker, short
  enough that a finished run stops billing.

## 4. The smoke, the projection, and the fork — BLOCKED, unexecuted

```bash
PYTHONPATH=src python3 scripts/smoke_5b.py --endpoint-id <ID> --serving-config A
python3 scripts/runpod_guard.py --step 5b --step-cap 4.00 --note "5b config A smoke"
```

`results/serving_5b.json` is what Deliverable 1 says 5c reads to flip `run_loop.ENDPOINT`.
Take `usd_per_second` from the guard's own balance delta over the smoke divided by the
smoke's **wall** seconds — not by summed `executionTime`. A worker bills while it is up,
including the gaps between sequential rows, and an 8-row smoke's idle share is nothing like
a 758-row run's.

```bash
PYTHONPATH=src python3 scripts/parity_verdict_5b.py --project \
  --seconds-per-row <measured> --usd-per-second <measured> \
  --cold-start-seconds <measured> --merge-usd <the config B pod's projected cost>
```

Over $4 → it writes `results/parity_verdict_5b.json` as `aborted-over-cap`, ships A, and the
phase stops there. That is a complete Deliverable 3, not a failure: SPEC says an aborted
pair closes the merge question in favour of A, and merging stays forbidden because this
measurement is what would have permitted it.

## 5. Config B, only if the projection cleared — NOT BUILT (the projection never happened)

```bash
runpodctl pod create --name mp-5b-merge --gpu-id "NVIDIA RTX A6000" --gpu-count 1 \
  --network-volume-id gfwa2an8fn --data-center-ids CA-MTL-3 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 150 \
  --ports '22/tcp' --ssh --terminate-after <UTC ISO8601>
```

**150 GB of container disk, not 30.** The merged bf16 checkpoint is ~62 GB and the volume
has only ~40 GB free under the HF cache; scratch goes to container disk and the NF4 result
(~20 GB) goes to the volume. Container disk is pennies per hour — running out of it after
the merge is an hour of GPU time thrown away.

The A6000 host has 456 GB of RAM, so `merge_requantize.py`'s bar (62 GB × 1.15) clears with
room. It is checked before the weights load, and it refuses rather than OOM-ing an hour in.

```bash
PYTHONPATH=src /workspace/venv/bin/python /workspace/repo/scripts/merge_requantize.py \
  --adapter /workspace/repo/results/train/45h2-arm-a/adapter \
  --out /workspace/merged-nf4 --bf16-scratch /merge-scratch \
  --sidecar /workspace/out/merged_5b.json \
  --revision 842da3794eaa0b77d5f08bae87a17459d91ff475
```

Fetch the sidecar to `results/merged_5b.json` **before deleting the pod**, then a second
template/endpoint with `SERVING_CONFIG=B` and `MERGED_DIR=/runpod-volume/merged-nf4`, and
its own 8-row carve smoke.

## 6. The pair — the phase's one paid event — ABORTED, see results/parity_verdict_5b.json

```bash
PYTHONPATH=src python3 scripts/eval_zero_shot.py --model google/gemma-4-31b-it \
  --backend endpoint --endpoint-id <A_ID> --serving-config A --batch-size 1 \
  --testset-version v4 --adapter results/train/45h2-arm-a/adapter --arm without-plast \
  --eval-checkpoint /tmp/parity-5b-a.jsonl --record-out results/parity_5b_a.json
```

`--serving-config B --merged-sidecar results/merged_5b.json` and no `--adapter` for B.
Both refuse before the first paid row unless the worker's own `info` names the registered
adapter sha, merge state and quantization.

```bash
PYTHONPATH=src python3 scripts/parity_verdict_5b.py --record results/parity_verdict_5b.json
runpodctl serverless delete <A_ID>; runpodctl serverless delete <B_ID>
python3 scripts/runpod_guard.py --step 5b --step-cap 4.00 --note "5b pair scored"
```

## When something goes wrong

- **The handshake times out.** `info()` has its own 1800 s budget; a 300 s one would abort
  the run and still be billed for the boot. If 1800 s is not enough, the weights are not
  where `HF_HOME` says — check on a pod, not by re-running the endpoint.
- **`assert_serving` refuses.** The endpoint is not serving what the phase registered. Do
  not pass the check by editing the expectation; find out what the worker loaded.
- **A row fails.** `retries=0` by design. A failed pair closes the merge question in
  favour of A — report it, do not re-ask.
- **The projection is over $4.** Stop. `--project` has already written the artifact.
- **Either cap is reached.** The guard exits 1. A cap is not raised to finish a run.
- **A pod is left running.** `runpodctl pod list -a` after every session. The volume alone
  bills ~$0.24/day whether or not anything is attached to it.

## What the next attempt should check first, before staging anything

The staging half of this runbook is proven and the volume still holds its output. What is
not proven is the delivery path, so the cheapest possible first step is the **hub control**:

```bash
runpodctl hub search vllm                 # a SERVERLESS listing id
runpodctl serverless create --name hub-control --hub-id <id> \
  --gpu-id "NVIDIA GeForce RTX 4090" --workers-max 1 --idle-timeout 5 \
  --execution-timeout 300 \
  --model-reference https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct:main
# submit one job, watch /health and /status, DELETE the endpoint either way
```

If RunPod's own worker completes a job, serverless is back and §3 onwards can run as
written. If it does not, nothing in this repository can make it, and the phase's outcome
stands. That control cost about five cents and it is what separated "our handler is broken"
from "serverless is unreachable" — run it before anything else, every time.

**Verify deletions by listing, never by an exit code.** Two `probe-cls` endpoints survived a
delete call that silently targeted a mangled id and were only found ~25 minutes later by
`runpodctl serverless list`. Every session ends with `pod list -a`, `serverless list` and
`network-volume list`, read out loud.
