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
first round number with headroom.

**The datacenter is chosen by an intersection, not by stock alone.** Not every datacenter supports
network volumes, and a volume can only be attached to a pod in **its own** datacenter — picking on
A6000 stock and finding out afterwards means a second volume and a second monthly bill. On
2026-08-01 the A6000 lived in `CA-MTL-3`, `EU-RO-1`, `EU-SE-1`, `US-KS-2` and `US-TX-1`; of those
only `CA-MTL-3` and `EU-RO-1` take network volumes, and `EU-RO-1` had no stock. So: **CA-MTL-3**.
Re-derive it rather than trusting that sentence — both lists move.

```bash
# A6000 stock per datacenter
runpodctl gpu list | python3 -c "import json,sys;[print(g['displayName'],g['dataCenterAvailability']) for g in json.load(sys.stdin) if 'A6000' in g['displayName']]"
# the network-volume datacenters: the error message of a deliberately bad id lists them all
runpodctl network-volume create --name probe --size 1 --data-center-id NOPE

runpodctl network-volume create --name market-pulse-phase4 --size 100 --data-center-id CA-MTL-3
runpodctl network-volume list
```

Keep the volume id — every pod below attaches it.

## 2. The pod

RTX A6000, 48 GB, secure cloud (~$0.53/hr; community is ~$0.33/hr but network-volume support is
the secure-cloud path). The image is the official PyTorch 2.8 / CUDA 12.8 one, so torch is already
present and only the three Phase-4 wheels are installed on top.

`--stop-after` is a belt to the idle-discipline braces: if the session is interrupted, the pod
stops by itself rather than billing overnight. Set it generously — the setup below is a `pip
install`, a 62 GB download and four full NF4 loads before the one run that matters, so a deadline
sized for "the run" expires during the smoke. **Step 6 re-reads it before starting the run.**

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
  --data-center-ids CA-MTL-3 \
  --cloud-type SECURE \
  --ports '22/tcp' \
  --ssh \
  --stop-after <UTC ISO8601, e.g. 2026-08-01T14:30:00Z>

runpodctl pod list
runpodctl ssh info <POD_ID>            # host and port for the ssh/scp lines below
```

`ssh info` reports `pod not ready` for a minute or two after the pod goes `RUNNING`; wait for the
`ip`/`port` rather than concluding the pod is broken.

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

`HF_HOME` on the volume is what makes the download survive a stopped pod. The image's Python is
PEP 668 "externally managed", so a plain `pip install` refuses; a venv **with**
`--system-site-packages` reuses the image's CUDA-matched torch instead of pulling 3 GB of a
possibly different build.

```bash
mkdir -p /workspace/hf /workspace/out          # `tee` below opens its target before python starts
export HF_HOME=/workspace/hf

python3 -m venv --system-site-packages /workspace/venv
/workspace/venv/bin/pip install -e '.[dev,gpu]'
/workspace/venv/bin/python -c "import torch,transformers,bitsandbytes;print(torch.__version__,transformers.__version__,bitsandbytes.__version__,torch.cuda.get_device_name(0))"
nvidia-smi

# 62 GB. Resumable, and it lands on the volume, not the container disk.
/workspace/venv/bin/hf download google/gemma-4-31b-it --revision <SHA>
du -sh /workspace/hf
```

Resolve the revision **before** the download and pass the same SHA to both — a record that names a
moving branch names nothing:

```bash
/workspace/venv/bin/python - <<'PY'
from huggingface_hub import HfApi
print(HfApi().model_info("google/gemma-4-31b-it").sha)
PY
```

## 5. Smoke, in three widening steps

Nothing below writes a record. Each step is a stop-and-report if it fails — and a stop-and-report
means **stop the pod first** (`runpodctl pod stop <POD_ID>`), then write the report.

`RUNPOD_POD_ID` is set for the container's main process and **not** for an SSH session, so the
record's `runtime.pod_id` is `None` unless it is exported by hand. Export it — a rented number that
cannot name the machine it came from is half a provenance.

```bash
cd /workspace/market-pulse
export HF_HOME=/workspace/hf
export RUNPOD_POD_ID=<POD_ID>          # not inherited over ssh; runpodctl pod list has it
PY=/workspace/venv/bin/python

# (a) the whole pipeline with no weights at all — prompts, parser, failure buckets, scorer.
$PY scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local --smoke

# (b) the weights load, quantized, and the environment is what the record will claim.
$PY scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local \
  --revision <SHA> --dry-run

# (c) three real rows per input. Prints the failure table and the per-row labels;
#     still writes nothing.
$PY scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local \
  --revision <SHA> --probe 3
```

**The batch-invariance check — do this before the full run, not after.** Greedy decoding makes
batch size a throughput choice *in principle*; on a real stack, left padding and kernel selection
can move a logit. So measure it: the same rows at batch 1 and at batch 8 must produce the same
parsed **labels**. `--probe` prints one JSON line per scored row, so the diff compares answers and
not counts — an aggregate "scored 8/8 · parse 0" is identical whenever both sizes merely parse,
and a check that cannot fail is not a check.

```bash
$PY scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local \
  --revision <SHA> --probe 8 --batch-size 1 > /tmp/b1.txt 2>&1 || echo "PROBE 1 FAILED"
$PY scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local \
  --revision <SHA> --probe 8 --batch-size 8 > /tmp/b8.txt 2>&1 || echo "PROBE 8 FAILED"
grep '"pred"' /tmp/b1.txt > /tmp/b1.pred; grep '"pred"' /tmp/b8.txt > /tmp/b8.pred
test -s /tmp/b1.pred && test -s /tmp/b8.pred || echo "NO PREDICTIONS — the check proved nothing"
diff /tmp/b1.pred /tmp/b8.pred && echo "batch invariant on $(wc -l < /tmp/b1.pred) rows"
```

Both `test -s` guards matter: two crashed probes produce two empty files, and `diff` on two empty
files is silent success. If the labels differ, the run uses `--batch-size 1` and the deviation is
reported. A faster wrong number is still a wrong number.

**On 2026-08-01 this check failed, and that is why it exists.** One row of 24 came back with
different intents at batch 8 (`[]` at batch 1, `["packaging", "quality"]` at batch 8) — same
weights, same prompt, greedy decoding, temperature 0. Left padding and kernel selection move a
logit, so "greedy, therefore batch-invariant" is false on bitsandbytes NF4 + A6000. **The run went
at `--batch-size 1`.**

Batch 1 is trivially invariant — one row, no padding — but that is an argument, not a measurement,
so measure the other half: the same probe twice must produce identical labels.

```bash
$PY scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local \
  --revision <SHA> --probe 16 --batch-size 1 > /tmp/a1.txt 2>&1
$PY scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local \
  --revision <SHA> --probe 16 --batch-size 1 > /tmp/a2.txt 2>&1
diff <(grep '"pred"' /tmp/a1.txt) <(grep '"pred"' /tmp/a2.txt) && echo "run-to-run identical"
```

It also gives the projection the smoke owes the full run. 2026-08-01: 48 rows in 191 s wall, of
which ~45 s is the model load — **3.04 s/row**, so 758 rows ≈ **39 min**, ≈ **$0.35** at $0.53/hr,
far inside amendment 3.4 (4)'s 4 h per arm. A projection over that ceiling stops the line.

## 6. The run — once

All 758 frozen rows: 400 comments + 250 posts + 108 holdout. One run, no re-run loops. If unusable
rows exceed 2% on any input the runner writes the record marked `gate_anchor_valid: false`, writes
no G1b slice, and exits 3 — that is a stop-and-report, not a retry.

`--record-out` is why the pod's `results/baselines.json` never travels: the pod is a throwaway
checkout, and wholesale-replacing an append-only anchor is the mistake this project already has a
footgun note about. What comes back is the record the scorer built.

Re-read the auto-stop deadline first: it was set before an hour of setup, and a pod that stops
mid-run wastes the whole run.

```bash
# --- on the Mac ---
runpodctl pod get <POD_ID>            # check the auto-stop is still comfortably ahead
date -u +%Y-%m-%dT%H:%M:%SZ

# --- on the pod ---
cd /workspace/market-pulse
mkdir -p /workspace/out
setsid nohup env HF_HOME=/workspace/hf RUNPOD_POD_ID=<POD_ID> \
  /workspace/venv/bin/python scripts/eval_zero_shot.py \
  --model google/gemma-4-31b-it --backend local --revision <SHA> \
  --batch-size 1 \
  --record-out /workspace/out/record.json > /workspace/out/run.log 2>&1 < /dev/null &
pgrep -af eval_zero_shot          # the process is the liveness check, not the log
```

Detached on purpose: 39 minutes is longer than an SSH session should be trusted for, and a dropped
connection must not kill the one paid run. Poll `pgrep -af eval_zero_shot` **and** the log — a
success-only `grep` stays silent through a crash.

## 7. Bring the three artifacts home, then stop the pod

```bash
# --- back on the Mac ---
mkdir -p /tmp/4a results/predictions      # neither exists on a fresh checkout
scp -P <PORT> root@<HOST>:/workspace/out/record.json /tmp/4a/
scp -P <PORT> root@<HOST>:/workspace/out/run.log /tmp/4a/
scp -P <PORT> 'root@<HOST>:/workspace/market-pulse/results/predictions/*.jsonl' results/predictions/
scp -P <PORT> root@<HOST>:/workspace/market-pulse/results/g1b_slice.json results/

```

**Check the hashes before appending, not after.** `results/baselines.json` is append-only; a record
whose artifacts did not survive the copy is a row that can never be removed.

```bash
python3 - <<'PY'
import hashlib, json, pathlib
record = json.loads(pathlib.Path("/tmp/4a/record.json").read_text())
config = record["config"]
for key in [k for k in config if k.endswith("_path") and f"{k[:-5]}_sha256" in config]:
    path = pathlib.Path(config[key])
    ok = path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == config[f"{key[:-5]}_sha256"]
    print(f"{key:<18} {config[key]:<60} {'ok' if ok else 'MISMATCH'}")
PY

python3 scripts/eval_zero_shot.py --append-record /tmp/4a/record.json
python3 scripts/show_results.py --last
make check                        # the artifact ratchet now covers the new row
```

If the record says `gate_anchor_valid: false`, `--append-record` says so on the way in. Append it
anyway — the two `qwen3.6-27b` rows live in the file the same way, and evidence of a bad run beats
a gap — but it anchors nothing without an operator decision.

**Stop the pod the moment the copy is verified.** Not after the report is written, not after the
ADR — the moment the files are on the Mac and their hashes check out.

```bash
runpodctl pod stop <POD_ID>
runpodctl pod get <POD_ID>             # desiredStatus EXITED — this is what goes into the report
runpodctl pod list                     # running pods ONLY: [] means nothing is running, not
                                       # that nothing exists. `pod list -a` shows exited ones.
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

**Every branch below starts the same way: `runpodctl pod stop <POD_ID>`, then write the report.**
A stop-and-report that leaves the GPU running is a stop-and-bill; the pod costs nothing to start
again, and the volume keeps the weights.

```bash
runpodctl pod stop <POD_ID> && runpodctl pod list
python3 scripts/runpod_guard.py --note "4a aborted: <one line on why>"
```

- **The guard refuses.** Read which clause fired. A cap trip is a stop-and-report. A balance above
  the anchor means the account was topped up mid-phase and the ledger has to be re-anchored by an
  operator decision, never by deleting the file.
- **`pod create` cannot find capacity.** A6000 stock moves; re-check `runpodctl gpu list` and, if
  the datacenter that holds the volume has none, say so and stop. Do not create a second volume in
  another datacenter without an operator decision — that is a second monthly bill.
- **The model will not load.** The record is worth nothing without the environment it names, so do
  not work around a load error by dropping quantization or changing dtype: that would silently
  score a different model than step 4b trains. Stop the pod, then report.
- **The BOS assertion fires.** The chat template stopped starting the prompt with `<bos>`, so
  `add_special_tokens=False` would drop it. Not a thing to work around — it changes every prompt.
  Stop the pod and report.
- **The batch-invariance check finds a difference, or proves nothing.** Fall back to
  `--batch-size 1` for the run and record the deviation. Do not skip the check to save pod minutes.
- **Over 2% unusable rows.** The runner already stopped and exited 3. Stop the pod, then report the
  ids and the reasons it printed; do not re-run in a loop hoping for a better draw.
- **You are unsure whether the pod is running.** `runpodctl pod list`. If in doubt, stop it — a
  stopped pod costs nothing to start again, and an idle one bills by the second.
