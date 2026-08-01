# Runbook — Phase 4c: the two arms, and the one attempt

Operator-facing, copy-paste, in order. It assumes `scripts/runbook_4b.md` has been run once: the
pod pattern, the venv, the bundle. **This is the step that cannot be repeated.** Each arm trains in
full and is scored on the frozen sets exactly once; after any gate number is seen nothing is
retrained, re-scored or reconfigured. A crash resumes — it never restarts-and-rescores.

**Budget: $25 across all of Phase 4**, of which $1.14 was spent by 4a and 4b. Expected here:
**~$5.2**. `scripts/runpod_guard.py` runs before every pod start and after every stop.

**One arm per pod session, volume-less wherever the A6000 has stock** (operator decision,
2026-08-01). The CA-MTL-3 volume is a bonus if stock happens to coincide at launch, never a wait
condition. The consequence to plan around: **such a session cannot be paused**, which is why step 1
exists and why step 3 syncs continuously.

---

## 0. Before the first pod (Mac)

```bash
cd ~/Desktop/Projects/market-pulse-llm
git status --short          # empty: the pod runs a checkout of HEAD
make check                  # green
ruff format --check .       # make check does not run the formatter
python3 scripts/runpod_guard.py
PYTHONPATH=src python3 scripts/gate_bars.py                       # the five bars, derived
PYTHONPATH=src python3 scripts/train_qlora.py --build-only        # arm A's two hashes
PYTHONPATH=src python3 scripts/train_qlora.py --build-only --with-synthetic
```

`train_sha256` of the real-only arm **must equal** `train_sha256` in
`results/train/4b-smoke/provenance.json`. If it does not, the arm about to be trained is not the arm
4b projected and measured, and the whole projection is void — stop and report.

Measured 2026-08-01: arm A `d2fa6742…` / 2 171 rows, arm B `d6d3c800…` / 2 771 rows, carve
`527381be…` shared by both, 600 synthetic ids added and 0 rows removed.

## 1. Capacity

Volume-less means the whole A6000 map is in play, not just CA-MTL-3.

```bash
runpodctl gpu list | python3 -c "
import json,sys
for g in json.load(sys.stdin):
    if g['displayName'] == 'RTX A6000':
        [print(d['dataCenterId'], d['stockStatus']) for d in g['dataCenterAvailability']]"
```

Capacity errors say different things and only one is about the datacenter:

- *"There are no longer any instances available with the requested specifications"* — no GPU there.
- *"This machine does not have the resources to deploy your pod"* — the GPU exists and the request
  does not fit it. On 2026-08-01 EU-SE-1 refused a 100, 80 **and** 70 GB container disk this way
  while reporting `Medium` stock; US-TX-1 took 80 GB first try. Vary the disk before believing a
  datacenter is full.

## 2. The pod (once per arm)

80 GB of container disk: the 62 GB of weights plus the checkpoints. `--stop-after` is the backstop —
set it a good margin past the arm's projection (arm A 3.42 h, arm B 4.37 h, both under the 5 h
ceiling of amendment 3.6) plus ~50 min for the load, the tokenization and the eval.

```bash
python3 scripts/runpod_guard.py
runpodctl pod create \
  --name market-pulse-4c-arm-a \
  --gpu-id "NVIDIA RTX A6000" --gpu-count 1 \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 \
  --container-disk-in-gb 80 \
  --data-center-ids <DC with stock> --cloud-type SECURE \
  --ports '22/tcp' --ssh \
  --stop-after <UTC ISO8601, ~6 h ahead>

runpodctl ssh info <POD_ID>        # "pod not ready" for a minute or two is normal
```

Then the bundle, the venv and the dataset check — 4b's steps 3 and 4, unchanged except that a
volume-less pod has no venv and no weights cache yet:

**Both arms clone the same bundle file.** The ablation is "identical config and seed, exactly one
data path differs"; a second bundle built from a later HEAD would make the arms differ by a commit
as well, however harmless that commit looks. Build it once, before arm A, and reuse the file.

```bash
git bundle create /tmp/market-pulse-4c.bundle HEAD      # once, for both arms
scp -P <PORT> /tmp/market-pulse-4c.bundle root@<HOST>:/workspace/

ssh -p <PORT> root@<HOST>
# --- on the pod ---
cd /workspace && git clone market-pulse-4c.bundle repo && cd repo
git rev-parse HEAD && git status --short         # equal to the Mac's HEAD, and empty
ls -l data/annotation/sarcasm_candidates.jsonl data/annotation/synthetic_sarcasm.jsonl
python3 -m venv --system-site-packages /workspace/venv   # PEP 668: do not pip into the image
export HF_HOME=/workspace/hf RUNPOD_POD_ID=<POD_ID>      # RUNPOD_POD_ID is NOT inherited over ssh
PY=/workspace/venv/bin/python
$PY -m pip install -e '.[dev,gpu]'
$PY scripts/train_qlora.py --build-only                  # both hashes equal the Mac's
$PY scripts/train_qlora.py --build-only --with-synthetic # arm B's pod also runs both
```

## 3. Resume proof — first, on the first pod, before arm A

The one thing 4b could only exercise against a stub: the adapter reloaded **with
`is_trainable=True`** onto a k-bit-prepared base, plus `torch.load` on a real paged-AdamW state. An
arm cannot be paused and is 3–4.5 h long; if it dies at hour three, resume is all there is.

Its own directory — never arm A's, or the arm inherits two runs' loss curve and a pre-written
adapter.

```bash
$PY scripts/train_qlora.py --out /workspace/out/resume-proof --max-steps 10
pkill -f train_qlora            # only if it is somehow still alive; --max-steps 10 exits on its own
$PY scripts/train_qlora.py --out /workspace/out/resume-proof --resume-from /workspace/out/resume-proof --max-steps 15
cat /workspace/out/resume-proof/loss.jsonl
```

PASS is two things, and the second is the load-bearing one:

- the printed `resumed at epoch 0 row N, optimizer step 10` — the counter continues, it does not
  reset;
- the step-15 loss sits on the step-10 trajectory. `PagedAdamW8bit` is constructed fresh and
  `load_state_dict` maps state **by parameter index**: if the trainable reload yields a different
  parameter order than `get_peft_model` did, the wrong momentum lands on the wrong tensor with no
  exception at all, and only the loss says so.

Free cross-check while it runs: this is the real-only arm at seed 42 on the frozen config — the 4b
smoke's first ten steps. Step 5 should land near **0.1799** and step 10 near the smoke's step-10
line. A large divergence means the data, the config or the template moved; learn it here for ~11
minutes of A6000 time rather than at hour three.

**Resume fails → STOP and report.** Do not start a 3.4 h arm on a pod that cannot be resumed.

## 4. The arm

```bash
setsid nohup env HF_HOME=/workspace/hf RUNPOD_POD_ID=<POD_ID> \
  $PY -u scripts/train_qlora.py --out /workspace/out/arm-a \
  > /workspace/out/arm-a.log 2>&1 < /dev/null &
pgrep -af train_qlora            # the process is the liveness check, not the log
```

`--with-synthetic` for arm B, `--out /workspace/out/arm-b`. No `--max-steps`: the full 272 (arm A)
or 348 (arm B) steps, 2 fixed epochs, no early stopping.

**Watch the process, not a success grep.** `loss.jsonl` is written open/write/close per line and is
the live view; `python3 -u` above makes the log live too, which 4b's smoke needed and did not have.

**Sync continuously, from the Mac, in its own shell.** Nothing may exist only on the pod:

```bash
# --- on the Mac ---
while true; do
  rsync -az -e "ssh -p <PORT>" root@<HOST>:/workspace/out/arm-a/ results/train/4c-arm-a/
  date -u +'%H:%M:%SZ synced'
  sleep 900
done
```

The adapter and the optimizer state change only at `save_every: 100` — about every 75 minutes at the
measured 45.23 s/step — so most passes copy only `loss.jsonl` and the rest is a no-op. **That save
cadence is the real recovery granularity**: a crash costs at most ~75 minutes of training (~$0.66),
which is inside the budget and is not worth editing a frozen config for. Recorded as a deviation
rather than fixed.

**The 5 h ceiling is on the training loop** (amendment 3.6). `seconds_per_step` in the log times the
remaining steps says whether it will hold; a projection that crosses 5 h mid-run is a stop-and-report,
not a thing to ride out.

## 5. The eval — same session, separate process

The arm's adapter, unmerged, on the NF4 base; batch size 1 because greedy is not batch-invariant on
this stack (measured, ADR `phase4-own-pod-anchor` §(c)). All 758 frozen rows plus the G1b fix-rate
over the sha-verified 44-id slice.

```bash
setsid nohup env HF_HOME=/workspace/hf RUNPOD_POD_ID=<POD_ID> \
  $PY -u scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local \
    --adapter /workspace/out/arm-a/adapter --arm real-only --batch-size 1 \
    --eval-checkpoint /workspace/out/arm-a-eval.jsonl \
    --record-out /workspace/out/arm-a-record.json \
  > /workspace/out/arm-a-eval.log 2>&1 < /dev/null &
```

Everything that could refuse has refused before the weights load: the anchor, the slice hash, the
adapter's own provenance, the arm label, the prompt hashes. Expect ~3 s/row — 39 minutes for 758
rows at 4a's measured rate.

**If it crashes, re-run the same command.** `--eval-checkpoint` holds every row already scored and
the run resumes on what is left; its header refuses a file another arm or another adapter wrote.
Nothing completed is ever re-scored.

## 6. Home, verify, delete

```bash
# --- on the Mac ---
rsync -az -e "ssh -p <PORT>" root@<HOST>:/workspace/out/arm-a/ results/train/4c-arm-a/
scp -P <PORT> root@<HOST>:/workspace/out/arm-a-record.json /tmp/
scp -P <PORT> root@<HOST>:/workspace/out/arm-a-eval.log results/train/4c-arm-a/
# the dump: the record names it relative to the repo root, so it lands at that path
scp -P <PORT> "root@<HOST>:/workspace/repo/results/predictions/*.jsonl" results/predictions/

PYTHONPATH=src python3 -c "
from market_pulse import records; from pathlib import Path
print(records.artifact_sha256(Path('results/train/4c-arm-a/adapter')))"   # equals the record's

python3 scripts/eval_zero_shot.py --append-record /tmp/arm-a-record.json
python3 scripts/show_results.py

runpodctl pod delete <POD_ID>     # volume-less: a stopped pod still bills 80 GB by the month
runpodctl pod list -a
python3 scripts/runpod_guard.py --note "4c arm A"
```

`append-record` refuses a record whose `(model, timestamp)` is already in the file, so a second
append cannot double a row.

Then repeat from step 2 for arm B. **Arm B launches on the frozen config whatever arm A's numbers
look like** — there is no decision until step 7, and reading one arm as a result is how a paired
ablation stops being one.

## 7. The verdict (Mac, mechanical)

```bash
PYTHONPATH=src python3 scripts/gate_verdict.py
```

Both columns, the rule's inputs and its arithmetic, the selected arm, five verdicts against bars
derived from the anchor. That output is the artifact — the ADR quotes it rather than paraphrasing it.

## When something goes wrong

Every branch starts with the pod's state and the ledger, then the report.

- **Resume proof fails.** Stop. Arm A does not start on a pod that cannot be resumed.
- **Training crashes.** Resume from the last synced state
  (`--resume-from /workspace/out/arm-a --out /workspace/out/arm-a`) and log the event. That is not a
  second attempt; a restart from step 0 would be.
- **The eval crashes.** Re-run with the same `--eval-checkpoint`. Completed rows are never re-scored.
- **A slice row does not parse.** The eval refuses to write a record and names the ids. Do not read a
  short slice as a failed G1b — report it.
- **The projection crosses 5 h mid-run.** Stop and report before the ceiling, not after.
- **The dataset hashes differ from the Mac's.** Stop: a file did not travel, or the checkout is not
  HEAD.
- **A gate fails.** Report it plainly. A failed gate closes its question, and nothing is retrained.
