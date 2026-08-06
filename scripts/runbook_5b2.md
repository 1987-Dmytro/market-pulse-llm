# Runbook — Phase 5b.2: does greedy survive N>1 on this stack?

Copy-paste, in order. **Budget: what is left under the $4.00 5b stop** — $2.7676 when the brief
was written, and **less by the hour**: the CA-MTL-3 volume bills ~$0.24/day whether or not
anything is attached to it, so the guard is the number, not the brief. Anchored in
`results/spend_5b.json` (never regenerated), enforced by
`scripts/runpod_guard.py --step 5b --step-cap 4.00`.

Law: SPEC amendment 3.11 (2), the **batch measurement** pre-registered 2026-08-06 — ladder
{16, 8, 4}, largest byte-identical N picks the candidate, none identical ⇒ 8, test v4 scored
ONCE at the candidate, adopted only if every 4.5h2-passed gate holds and no head drops more
than 0.005 vs `results/parity_5b_a.json`. **Gate evals stay batch 1 regardless.**

## What is different from 5b.1

| | 5b.1 | 5b.2 |
|---|---|---|
| what is measured | what the pod runtime costs the gate numbers | what **batching** costs them |
| baseline | `results/verdict_45h2.json` (the 4.5h2 anchors) | `results/parity_5b_a.json` (batch 1, with its per-row dump) |
| paid events | one | one — the ladder is carve rows and costs ~4 cents |
| what can be adopted | nothing (A was already shipped) | batch N, or nothing and batch 1 forever |
| the run rate at stake | — | ~$28/mo at batch 1 vs the $9–12 ceiling of SPEC §3.11 (6) |

The stack under the HTTP is unchanged: `start.sh` → `serve_handler.py` →
`market_pulse.local_llm`, same chat template, same `add_special_tokens=False`, same greedy
`generate`. **The batching is not new code in the generation path** — `LocalClient.batch`
already padded and generated; what 5b.2 added is permission to use it (`--batch-measurement`),
the ladder that picks N, and three guards. `make check` 1016 passed before the pod boots.

## Rulings taken BEFORE the pod boots

Each of these is a judgement that would otherwise be made with a number in front of me.

- **No N byte-identical ⇒ the candidate is 8.** SPEC's own path, not an abort. Greedy is
  already *measured* non-invariant on this stack (ADR `phase4-own-pod-anchor` §(c), 2026-08-01:
  one row of 24 flipped between batch 8 and batch 1), so this is the **expected** outcome. The
  ladder selects; the paid run decides.
- **An out-of-memory at N=16 is a ladder outcome**, recorded as `failed`, and the remaining arms
  still run. `classify_local` re-raises OOM rather than counting it against rows, and
  `compare()` refuses to call an arm that lost rows identical.
- **A ladder call that hits the 300 s per-call timeout is data.** `DEFAULT_TIMEOUT` is a *per-row*
  budget and a batch of 16 should take far less than 16 of them; if it fires, that is the answer,
  not a reason to raise the timeout.
- **The `1-repeat` arm is the control.** If batch 1 does not reproduce itself, every identity
  verdict below it is noise and no candidate can be picked from them — the script exits 3.
- **The batch-1 path must not have moved.** The ladder's batch-1 arm is regressed against the
  5b.1 smoke's own 24 rows. **This is NOT byte-for-byte**: `results/serving_5b.json` stores
  `finish_reason`, `parsed` and the token counts, never the reply text, so those four fields are
  the strongest check the committed artifact supports. Byte-identity is measured *inside* this
  run, arm against arm. Say it that way in the report — the brief asks for byte-for-byte and the
  artifact cannot answer it (Deviation).
- **Mixed batch.** If `solo_retried` is non-empty in the paid run, `classify_local`'s fallback
  re-generated those rows at batch 1 while the record says N. The parity number is then **mixed**
  and is reported as mixed — never averaged away, and the ids are in the record.
- **A crash in the paid run is terminal.** One attempt, no retry, no second N.
  `--eval-checkpoint` exists so a partial run leaves per-row evidence; it is never resumed.
- **Cost is attributed on a pod**, posted rate × seconds held, cross-checked against the guard's
  balance delta — not derived from it (a delta across boot and a 59 GB download divided by a
  five-minute ladder prices the ladder at ten machines).
- **Nothing is appended to `results/baselines.json`.** A serving row is not a gate anchor.
- **Test v4 opens exactly once**, in the paid run. No `--probe` against a frozen file at any N.

## 0. Before anything (Mac)

```bash
cd ~/Desktop/Projects/market-pulse-llm
git status --short                       # empty
make check                               # green, state the total
ruff format --check .
shasum -c results/raw_v1_baseline.sha256 # 6/6
python3 scripts/runpod_guard.py --step 5b --step-cap 4.00     # the live headroom
PYTHONPATH=src python3 scripts/batch_ladder_5b2.py --endpoint-id x --carve-only
runpodctl pod list -a && runpodctl serverless list             # both empty before, both after
```

## 1. The pod — read availability, do not probe it

`runpodctl gpu list` reports `dataCenterAvailability` **per datacenter**;
`runpodctl datacenter list` prints `stockStatus: ""` for everything and answers nothing. Reading
the wrong one cost 45 minutes and 31 refused `pod create` calls on 06.08.

```bash
runpodctl gpu list --output json | python3 -c "
import json,sys
for g in json.load(sys.stdin):
    if 'A6000' in (g.get('displayName') or '') or 'A40' in (g.get('displayName') or ''):
        print(g['displayName'], g.get('dataCenterAvailability'))"
```

Capacity clause (SPEC 3.11 (1), operator 2026-08-06): **the CLASS is the contract, the
datacenter is not.** A6000 in any datacenter first; A40 is the authorised in-class fallback with
the card written into the run's provenance; A100 is not authorised.

```bash
COPYFILE_DISABLE=1 tar czf /tmp/raw-posts-5b2.tgz data/raw/posts     # ._* break parents.load
git bundle create /tmp/market-pulse-5b2.bundle HEAD

runpodctl pod create --name mp-5b2 --gpu-id "NVIDIA RTX A6000" --gpu-count 1 \
  --data-center-ids US-TX-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 \
  --container-disk-in-gb 30 --volume-in-gb 120 --ports '22/tcp' --ssh \
  --terminate-after <UTC ISO8601, ~3 h out>
runpodctl pod list -a                    # exactly one pod, and its costPerHr
runpodctl ssh info <POD_ID>
```

## 2. Stage (fresh, as 5b.1 proved is cheaper than the volume)

Weights land on local NVMe: 59 GB in ~4 min, and the cold start is **53 s** against 278.9 s off
the network volume. Every `-o` is spelled out — `SSHOPT="-o A -o B"` unquoted is one argument in
zsh and the copy dies.

```bash
SSHK=~/.runpod/ssh/runpodctl-ssh-key
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> /tmp/market-pulse-5b2.bundle /tmp/raw-posts-5b2.tgz root@<HOST>:/workspace/
```

On the pod — `start.sh` names `/runpod-volume`, and **a pod has no endpoint template**, so every
variable the serverless worker got from `--env` is the launcher's job now (5b.1 D8):

```bash
ln -sfn /workspace /runpod-volume
cd /workspace && rm -rf repo && git clone -q market-pulse-5b2.bundle repo
cd repo && git rev-parse HEAD && git status --short        # equals the Mac's HEAD, empty
tar xzf /workspace/raw-posts-5b2.tgz -C /workspace/repo    # data/raw/posts is gitignored
python3 -m venv --system-site-packages /workspace/venv    # inherit the IMAGE's torch
/workspace/venv/bin/pip install -q transformers==5.14.1 bitsandbytes==0.50.0 \
  peft==0.18.0 accelerate runpod pyyaml     # PINNED, and deliberately NO torch
```

**Check the stack string before the 59 GB, not after it.** The anchor is `torch 2.8.0+cu128`
and `assert_runtime_matches` compares exactly; a PyPI `torch==2.8.0` wheel can report `2.8.0`
with no local version, which would refuse the run at the first `info` — one cold start too late.
The image `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404` already carries the right build,
which is why the venv inherits rather than installs it.

```bash
cd /workspace/repo && PYTHONPATH=src /workspace/venv/bin/python -c "
import sys; sys.path.insert(0,'src'); sys.path.insert(0,'scripts')
import torch, transformers, bitsandbytes
from eval_zero_shot import arm_runtime
from market_pulse import serving
seen = {'torch': torch.__version__, 'transformers': transformers.__version__,
        'bitsandbytes': bitsandbytes.__version__}
print(seen); print(arm_runtime())
serving.assert_runtime_matches(seen, arm_runtime()); print('stack matches the 4.5h2 anchor')"
```

Only then the weights:

```bash
HF_HOME=/workspace/hf /workspace/venv/bin/hf download google/gemma-4-31b-it \
  --revision 842da3794eaa0b77d5f08bae87a17459d91ff475
cp scripts/start_5b_worker.sh /workspace/start.sh && chmod +x /workspace/start.sh
```

The adapter travels in the bundle except for `adapter_model.safetensors` (gitignored) — copy it
from the Mac and check the sha the phase registered:

```bash
PYTHONPATH=src /workspace/venv/bin/python -c "
import sys; sys.path.insert(0,'src')
from pathlib import Path; from market_pulse import records
print(records.artifact_sha256(Path('results/train/45h2-arm-a/adapter')))"   # b3ca630846c7…
```

## 3. The free positive control, before the model loads

```bash
cd /workspace/repo && PYTHONPATH=src /workspace/venv/bin/python scripts/batch_ladder_5b2.py \
  --endpoint-id x --carve-only
```

Rebuilds the carve and refuses unless it hashes to `8347abd74ae9…`. This is the exact failure
that killed 5b's `podcheck.py`: `data/raw/posts` is gitignored and did not travel.

## 4. The worker

```bash
cd /workspace/repo && setsid nohup env SERVING_CONFIG=A \
  ADAPTER_DIR=/workspace/repo/results/train/45h2-arm-a/adapter \
  BASE_WEIGHTS=google/gemma-4-31b-it \
  MODEL_REVISION=842da3794eaa0b77d5f08bae87a17459d91ff475 \
  HF_HOME=/workspace/hf bash /workspace/start.sh \
  --rp_serve_api --rp_api_host 127.0.0.1 --rp_api_port 8000 \
  > /workspace/out/worker.log 2>&1 < /dev/null &
pgrep -af serve_handler.py                 # the process is the liveness check, not the log
grep -m1 "Uvicorn running" /workspace/out/worker.log
```

## 5. The ladder (~4 cents) and the projection

```bash
cd /workspace/repo && PYTHONPATH=src /workspace/venv/bin/python scripts/batch_ladder_5b2.py \
  --endpoint-id <POD_ID> --endpoint-url http://127.0.0.1:8000 --serving-config A
```

PASS is four things: `info` names `adapter_sha256 b3ca630846c7…`, every arm parses 24/24, the
`1-repeat` arm is identical to `1`, and the batch-1 arm has not moved against the 5b.1 smoke.
Then, on the Mac:

```bash
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/repo/results/batch_ladder_5b2.json results/
python3 scripts/runpod_guard.py --step 5b --step-cap 4.00 --note "5b.2 staging + carve ladder"
PYTHONPATH=src python3 scripts/parity_verdict_5b.py --project --runs 1 \
  --ladder-record results/batch_ladder_5b2.json --ladder-arm <CANDIDATE> \
  --usd-per-second <costPerHr/3600> --cold-start-seconds 0 \
  --spent-usd <5B SPENT from the guard> \
  --projection-out results/batch_5b2_projection.json \
  --verdict-out results/batch_5b2_verdict.json
```

`--cold-start-seconds 0` because the worker is already warm from the ladder and the paid run
does not pay it again; the 53 s cold start belongs to the **per-pass** model 5c builds, not to
this projection. Over the remaining headroom → the phase stops there and reports; the artifact
is already written. **Do not re-fetch `results/serving_5b.json`** — the Mac's copy carries the
cost and deployment blocks stamped in after the fact, and the pod's does not.

## 6. The paid run — the phase's ONE paid event

```bash
cd /workspace/repo && mkdir -p /workspace/out && setsid nohup env PYTHONPATH=src HF_HOME=/workspace/hf \
  /workspace/venv/bin/python -u scripts/eval_zero_shot.py --model google/gemma-4-31b-it \
  --backend endpoint --endpoint-id <POD_ID> --endpoint-url http://127.0.0.1:8000 \
  --serving-config A --batch-size <CANDIDATE> --batch-measurement --testset-version v4 \
  --adapter results/train/45h2-arm-a/adapter --arm without-plast \
  --eval-checkpoint /workspace/out/parity-5b2.jsonl \
  --record-out /workspace/out/parity_5b2.json \
  > /workspace/out/parity-5b2.log 2>&1 < /dev/null &
pgrep -af eval_zero_shot                   # NOT a grep of the log for a success line
```

It refuses before the first row unless the worker's `info` names the registered adapter sha,
merge state and quantization, and unless its library stack is the one 4.5h2 measured.

**Fetch everything before deleting the pod.**

```bash
SCPOPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
scp -i $SSHK $SCPOPT -P <PORT> root@<HOST>:/workspace/out/parity_5b2.json results/
scp -i $SSHK $SCPOPT -P <PORT> root@<HOST>:/workspace/out/parity-5b2.log results/train/
scp -i $SSHK $SCPOPT -P <PORT> root@<HOST>:/workspace/out/parity-5b2.jsonl /tmp/
scp -i $SSHK $SCPOPT -P <PORT> "root@<HOST>:/workspace/repo/results/predictions/*.jsonl" results/predictions/
runpodctl pod delete <POD_ID> && runpodctl pod list -a      # deletion is PROVEN by the listing
python3 scripts/runpod_guard.py --step 5b --step-cap 4.00 --note "5b.2 test v4 at batch <N>"
```

(`$SCPOPT` unquoted works here because every `-o` is its own word; the trap is quoting the
*value*, as `SSHOPT="-o A -o B"` did.)

## 7. Read the record before comparing anything

`read_parity` checks only that the record claims config A. What `run_batch` adds — and what to
read by eye anyway:

- `config.generation.batch_size` is the candidate, and the baseline's is 1. The verdict refuses
  otherwise, because mislabelling this comparison puts a number under a heading that decides the
  run rate.
- **`scored == rows` on all three inputs.** A run that lost rows is a *failed attempt* under
  §(2), not a lower number — the verdict raises.
- `diagnostics.failures[*].solo_retried` empty, or the measurement is mixed.
- `config.serving.transport == "pod-loopback"`, `prompt_revision_sha256` equal to the anchor's
  (`495b43d1…` T1, `6a7e66ef…` T2), input hashes equal.

## 8. The verdict

```bash
PYTHONPATH=src python3 scripts/parity_verdict_5b.py --batch \
  --parity-record results/parity_5b2.json --baseline-record results/parity_5b_a.json \
  --batch-dump results/predictions/<the new dump>.jsonl \
  --baseline-dump results/predictions/google-gemma-4-31b-it--20260806T154612Z.jsonl \
  --serving-record results/serving_5b.json --usd-per-hour <costPerHr>
```

Applies `scorer.select_serving_config` under `BATCH_SELECTION_RULE`, stamps the comparison into
`results/parity_5b2.json`, and writes the adopted batch and its $/1000 rows **beside** the 5b.1
smoke in `results/serving_5b.json`. Row agreement against the batch-1 dump is printed and
recorded as description — it gates nothing.

## When something goes wrong

- **`assert_serving` or `assert_runtime_matches` refuses.** The pod is not serving what the phase
  registered. Do not pass the check by editing the expectation.
- **The `1-repeat` arm differs from `1`.** Stop. The ladder cannot pick anything.
- **An arm OOMs.** Recorded, the ladder continues, and that N is not identical by definition.
- **A row fails in the paid run.** `retries=0` by design; a failed attempt fixes batch 1 forever
  and returns the money question to the operator. Report it.
- **The projection is over the remaining headroom.** Stop. `--project` already wrote the artifact.
- **The guard exits 1.** A cap is not raised to finish a run.
- **A pod is left running.** `runpodctl pod list -a` after every session, and read the output.
