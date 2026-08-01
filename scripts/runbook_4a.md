# Runbook — Phase 4a: pod bootstrap and the own-pod zero-shot re-run

Operator-facing. Copy-paste, in order. Every number these commands produce goes through
`src/market_pulse/scorer.py` into `results/baselines.json`, append-only; nothing here is ever
hand-edited. The decisions behind the commands are SPEC amendment 3.4 and
`knowledge/decisions/phase4-own-pod-anchor.md`.

**Budget: $25 hard cap across all of Phase 4**, checked before every start by
`scripts/runpod_guard.py` against RunPod's own figures. 4a is expected to spend **$1–2** of it.
The cap is never raised to finish a run — a trip is a stop-and-report.

**Two things that are easy to get wrong and cost money:**

- **A stopped pod is not a stopped bill.** The network volume is charged by the month whether or
  not a pod is attached (~$0.07/GB/month, so ~$7/month for 100 GB). Only the balance delta sees
  it; that is why the guard reads the balance and not just the pod billing rows.
- **A pod without a network volume is deleted, unrecoverably, at a $0 balance.** Create the volume
  first, always attach it, and keep the weights on it — a re-download is 62 GB of pod time.

---

## 0. What must be true before you start

- `runpodctl` is authenticated (`~/.runpod/config.toml`, or `RUNPOD_API_KEY`) and an SSH key is
  registered — `runpodctl ssh list-keys` must print one.
- `results/spend_phase4.json` exists and is committed. It anchors the balance as it stood when
  Phase 4 opened. **Never regenerate it**: delete it and the counter silently restarts at today's
  balance, exactly the way `results/spend_3b.json` would.
- `make check` is green and the working tree is clean. The pod runs a checkout of `HEAD`, and the
  record stamps that commit; uncommitted code under `src/`, `scripts/` or `config/` means the
  recorded commit does not reproduce the numbers, and the runner says so.

```bash
cd ~/Desktop/Projects/market-pulse-llm
git status --short
make check
runpodctl ssh list-keys
python3 scripts/runpod_guard.py          # exit 0 = under the cap; exit 1 = stop and report
```

## 1. The network volume

100 GB: the weights are 62 GB and the HF cache holds a blob plus a snapshot link, so 100 GB is the
first round number with headroom. `EU-SE-1` is the datacenter that had A6000 stock at
`Medium` — check before creating, because a volume can only be attached to a pod in **its own**
datacenter and moving one means creating another.

```bash
runpodctl gpu list | python3 -c "import json,sys;[print(g['displayName'],g['dataCenterAvailability']) for g in json.load(sys.stdin) if 'A6000' in g['displayName']]"
runpodctl network-volume create --name market-pulse-phase4 --size 100 --data-center-id EU-SE-1
runpodctl network-volume list
```

Keep the volume id — every pod below attaches it.

## 2. The pod

RTX A6000, 48 GB, secure cloud (~$0.53/hr; community is ~$0.33/hr but network-volume support is
the secure-cloud path). The image is the official PyTorch 2.8 / CUDA 12.8 one, so torch is already
present and only the three Phase-4 wheels are installed on top.

`--stop-after` is a belt to the idle-discipline braces: if the session is interrupted, the pod
stops by itself rather than billing overnight. Set it to a couple of hours out, in UTC.

```bash
python3 scripts/runpod_guard.py                       # before every start, without exception

runpodctl pod create \
  --name market-pulse-4a \
  --gpu-id "NVIDIA RTX A6000" \
  --gpu-count 1 \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 \
  --container-disk-in-gb 40 \
  --network-volume-id <VOLUME_ID> \
  --volume-mount-path /workspace \
  --data-center-ids EU-SE-1 \
  --cloud-type SECURE \
  --ports '22/tcp' \
  --ssh \
  --stop-after <UTC ISO8601, e.g. 2026-08-01T14:00:00Z>

runpodctl pod list
runpodctl ssh info <POD_ID>            # host and port for the ssh/scp lines below
```

## 3. The code and the frozen inputs

The repo has no remote, so it travels as a git bundle — 1 MB, whole history, and the pod ends up
with a real checkout whose `git rev-parse HEAD` is the commit the record will name.

```bash
git bundle create /tmp/market-pulse.bundle HEAD
scp -P <PORT> /tmp/market-pulse.bundle root@<HOST>:/workspace/

ssh -p <PORT> root@<HOST>
# --- on the pod, from here down ---
cd /workspace
git clone market-pulse.bundle market-pulse && cd market-pulse
git rev-parse HEAD                     # must equal the local HEAD
git status --short                     # must be empty
```

## 4. The environment and the weights

`HF_HOME` on the volume is what makes the download survive a stopped pod.

```bash
export HF_HOME=/workspace/hf
pip install -e '.[dev,gpu]'
python3 -c "import torch,transformers,bitsandbytes;print(torch.__version__,transformers.__version__,bitsandbytes.__version__,torch.cuda.get_device_name(0))"
nvidia-smi

# 62 GB. Resumable, and it lands on the volume, not the container disk.
hf download google/gemma-4-31b-it --revision main
du -sh /workspace/hf
```

Record the revision the download resolved to — it goes into the run as `--revision` so the record
names a commit and not a moving branch:

```bash
python3 - <<'PY'
from huggingface_hub import HfApi
print(HfApi().model_info("google/gemma-4-31b-it").sha)
PY
```

## 5. Smoke, in three widening steps

Nothing below writes a record. Each step is a stop-and-report if it fails.

```bash
export HF_HOME=/workspace/hf

# (a) the whole pipeline with no weights at all — prompts, parser, failure buckets, scorer.
python3 scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local --smoke

# (b) the weights load, quantized, and the environment is what the record will claim.
python3 scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local \
  --revision <SHA> --dry-run

# (c) three real rows per input. Prints the failure table; still writes nothing.
python3 scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local \
  --revision <SHA> --probe 3
```

**The batch-invariance check — do this before the full run, not after.** Greedy decoding makes
batch size a throughput choice *in principle*; on a real stack, left padding and kernel selection
can move a logit. So measure it: the same rows at batch 1 and at batch 8 must produce the same
parsed labels. Two probes and a `diff` are enough, because `--probe` prints per-row outcomes and
the dump writer is not involved.

```bash
python3 scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local \
  --revision <SHA> --probe 8 --batch-size 1 | tee /tmp/b1.txt
python3 scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local \
  --revision <SHA> --probe 8 --batch-size 8 | tee /tmp/b8.txt
diff <(grep -A4 'scored' /tmp/b1.txt) <(grep -A4 'scored' /tmp/b8.txt) && echo "batch invariant"
```

If they differ, the run uses `--batch-size 1` and the deviation is reported. A faster wrong number
is still a wrong number.

## 6. The run — once

All 758 frozen rows: 400 comments + 250 posts + 108 holdout. One run, no re-run loops. If unusable
rows exceed 2% on any input the runner writes the record marked `gate_anchor_valid: false`, writes
no G1b slice, and exits 3 — that is a stop-and-report, not a retry.

`--record-out` is why the pod's `results/baselines.json` never travels: the pod is a throwaway
checkout, and wholesale-replacing an append-only anchor is the mistake this project already has a
footgun note about. What comes back is the record the scorer built.

```bash
cd /workspace/market-pulse
export HF_HOME=/workspace/hf
python3 scripts/eval_zero_shot.py \
  --model google/gemma-4-31b-it --backend local --revision <SHA> \
  --batch-size 8 \
  --record-out /workspace/out/record.json | tee /workspace/out/run.log
```

## 7. Bring the three artifacts home, then stop the pod

```bash
# --- back on the Mac ---
mkdir -p /tmp/4a
scp -P <PORT> root@<HOST>:/workspace/out/record.json /tmp/4a/
scp -P <PORT> root@<HOST>:/workspace/out/run.log /tmp/4a/
scp -P <PORT> 'root@<HOST>:/workspace/market-pulse/results/predictions/*.jsonl' results/predictions/
scp -P <PORT> root@<HOST>:/workspace/market-pulse/results/g1b_slice.json results/

python3 scripts/eval_zero_shot.py --append-record /tmp/4a/record.json
python3 scripts/show_results.py --last
```

**Stop the pod the moment the copy is verified.** Not after the report is written, not after the
ADR — the moment the files are on the Mac and their hashes check out.

```bash
runpodctl pod stop <POD_ID>
runpodctl pod list                     # show the stopped state; this goes into the report
python3 scripts/runpod_guard.py --note "4a own-pod zero-shot run"
```

The volume is deliberately **not** deleted: step 4b trains against the same weights, and
re-downloading 62 GB costs more pod time than the volume costs to keep. It does keep billing —
which is why the guard is run again at the end of every session, not only at the start.

## 8. Verify what came back

```bash
shasum -a 256 results/predictions/*.jsonl results/g1b_slice.json
python3 - <<'PY'
import json, pathlib
record = json.loads(pathlib.Path("results/baselines.json").read_text())["google/gemma-4-31b-it"][-1]
config = record["config"]
for key in ("predictions_path", "g1b_slice_path"):
    path = pathlib.Path(config[key])
    import hashlib
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(key, path, digest == config[key.replace("_path", "_sha256")])
print("prompt_sha256 equal to the 3b row:", config["prompt_sha256"])
PY
```

## When something goes wrong

- **The guard refuses.** Read which clause fired. A cap trip is a stop-and-report. A balance above
  the anchor means the account was topped up mid-phase and the ledger has to be re-anchored by an
  operator decision, never by deleting the file.
- **`pod create` cannot find capacity.** A6000 stock moves; re-check `runpodctl gpu list` and, if
  the datacenter that holds the volume has none, say so and stop. Do not create a second volume in
  another datacenter without an operator decision — that is a second monthly bill.
- **The model will not load.** The record is worth nothing without the environment it names, so do
  not work around a load error by dropping quantization or changing dtype: that would silently
  score a different model than step 4b trains. Stop and report.
- **Over 2% unusable rows.** The runner already stopped. Report the ids and the reasons it printed;
  do not re-run in a loop hoping for a better draw.
- **You are unsure whether the pod is running.** `runpodctl pod list`. If in doubt, stop it — a
  stopped pod costs nothing to start again, and an idle one bills by the second.
