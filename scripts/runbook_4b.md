# Runbook — Phase 4b: the training smoke

Operator-facing, copy-paste, in order. It assumes `scripts/runbook_4a.md` has been run once: the
network volume exists, it holds the 62 GB of weights and the venv, and the pod pattern is the one
described there. **This step trains nothing to completion** — 40–60 optimizer steps on the
real-only arm, a checkpoint reloaded, ~24 carved training rows scored for mechanics, and a
projection. The full runs are 4c, and they need an explicit go.

**Budget: $25 across all of Phase 4**, of which $0.66 was spent by 4a. Expected here: **~$1**.
`scripts/runpod_guard.py` is run before the pod starts and after it stops, without exception.

**Frozen sets and the holdout are not opened by anything in this step.** `scripts/train_qlora.py`
refuses to read them by name, and the mechanics eval runs on rows carved out of the training pool.

---

## 0. Before you start

```bash
cd ~/Desktop/Projects/market-pulse-llm
git status --short          # empty: the pod runs a checkout of HEAD
make check                  # green
python3 scripts/runpod_guard.py
PYTHONPATH=src python3 scripts/train_qlora.py --build-only          # note the two sha256 fields
```

The two dataset hashes printed here are the ones the pod must reproduce. They are the check that
the pod is training on the same rows this checkout assembled — a bundle that lost a file, or a
`data/annotation/*` path that is gitignored and did not travel, shows up here and nowhere else.

## 1. Capacity, before anything else

**A network volume cannot move between datacenters, and the pod must be in the volume's.** Ours is
`gfwa2an8fn` in **CA-MTL-3**, which means the A6000 has to be in stock *there*; EU-SE-1 having
plenty is irrelevant. On 2026-08-01 at 10:49 UTC CA-MTL-3 was `none` and the 4a pod's host had no
free GPU either, so the session waited for stock rather than paying for a second volume.

```bash
runpodctl gpu list | python3 -c "
import json,sys
for g in json.load(sys.stdin):
    if g['displayName'] == 'RTX A6000':
        [print(d['dataCenterId'], d['stockStatus']) for d in g['dataCenterAvailability']]"
```

- **CA-MTL-3 has stock** → step 2.
- **CA-MTL-3 is `none`** → poll (`scratchpad/wait_stock.sh` in the 4b session is 30 tries, 3 min
  apart, and creates nothing). Do **not** create a second network volume in another datacenter:
  that is a second monthly bill and an operator decision. Running volume-less in another
  datacenter re-downloads 62 GB and is a fallback with a price, not a shortcut — it is only worth
  it if the wait is long, and it goes in the deviations log.
- Restarting the exited 4a pod (`runpodctl pod start gxkdecf3g7k3y7`) is worth one try and costs
  nothing, but "not enough free GPUs on the host machine" is a normal answer: a stopped pod holds
  no reservation.

## 2. The pod

Same shape as 4a. `--stop-after` matters more here than it did there: a training smoke ends when it
ends, and an idle A6000 bills at $0.53/hr whether or not anyone is watching. `pod start` has no
such flag, which is one reason to create rather than restart.

```bash
python3 scripts/runpod_guard.py
runpodctl pod create \
  --name market-pulse-4b \
  --gpu-id "NVIDIA RTX A6000" --gpu-count 1 \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 \
  --container-disk-in-gb 40 \
  --network-volume-id gfwa2an8fn --volume-mount-path /workspace \
  --data-center-ids CA-MTL-3 --cloud-type SECURE \
  --ports '22/tcp' --ssh \
  --stop-after <UTC ISO8601, ~2.5 h ahead>

runpodctl pod list
runpodctl ssh info <POD_ID>        # "pod not ready" for a minute or two is normal
```

zsh does not word-split an unquoted variable holding ssh options, so a `$SSH_OPTS` that works in
bash hands `scp` one giant filename. Spell the flags out, or drive ssh/scp from a bash script with
a real array.

## 3. Code and dependencies

The repo travels as a git bundle again — the volume still holds the 4a checkout, but it is a
different commit and `git status` on the pod has to be empty for the provenance to mean anything.

```bash
git bundle create /tmp/market-pulse-4b.bundle HEAD
scp -P <PORT> /tmp/market-pulse-4b.bundle root@<HOST>:/workspace/

ssh -p <PORT> root@<HOST>
# --- on the pod ---
cd /workspace
rm -rf market-pulse-4b
git clone market-pulse-4b.bundle market-pulse-4b && cd market-pulse-4b
git rev-parse HEAD && git status --short        # equal to the Mac's HEAD, and empty
```

`data/annotation/*` is gitignored except for explicit `!` exceptions, and the trainer reads two
files from there. Confirm they arrived before spending a model load on finding out:

```bash
ls -l data/annotation/sarcasm_candidates.jsonl data/annotation/synthetic_sarcasm.jsonl
```

The venv on the volume already has torch, transformers and bitsandbytes from 4a; `peft` is new.

```bash
export HF_HOME=/workspace/hf
/workspace/venv/bin/pip install -e '.[dev,gpu]'
/workspace/venv/bin/python -c "import peft,torch;print(peft.__version__, torch.cuda.get_device_name(0))"
du -sh /workspace/hf            # the weights should still be there — no re-download
```

## 4. The dataset, before the GPU

`--build-only` loads no weights. It asserts the prompt SHA256 against the recorded runs, sends
every target back through the eval parser, and asserts the two arms differ by exactly the 600
synthetic ids. **Both hashes must equal the ones the Mac printed in step 0.**

```bash
cd /workspace/market-pulse-4b
PY=/workspace/venv/bin/python
$PY scripts/train_qlora.py --build-only
$PY scripts/train_qlora.py --build-only --with-synthetic
```

A mismatch is a stop-and-report: it means the pod is training on different rows than the ones this
project assembled, and no smoke on top of that would mean anything.

## 5. The smoke — one run

40–60 optimizer steps at the frozen config (effective batch 16, so ~50 steps is ~800 rows, a third
of an epoch). It writes `loss.jsonl`, saves an adapter, reloads it and scores the 24 carved
**training** rows for mechanics only.

```bash
export RUNPOD_POD_ID=<POD_ID>          # not inherited over ssh; the provenance needs it
mkdir -p /workspace/out
setsid nohup env HF_HOME=/workspace/hf RUNPOD_POD_ID=<POD_ID> \
  $PY scripts/train_qlora.py --out /workspace/out/smoke --max-steps 50 --carve-eval \
  > /workspace/out/smoke.log 2>&1 < /dev/null &
pgrep -af train_qlora                  # the process is the liveness check, not the log
tail -f /workspace/out/smoke.log
```

Detached for the same reason 4a's run was: a dropped SSH session must not kill a paid run. Poll the
process **and** the log — a grep for the success line is silent through a crash.

What the log must show, and what each line means if it does not:

- `LoRA on N modules` — if this refuses, the base names its projections differently from
  `config/qlora.yaml`'s suffixes. Stop and report; do not guess names on a rented card.
- falling `loss`, and a `carve_loss` every 25 steps. The carve is a thermometer, not a selector:
  nothing branches on it, and a smoke's numbers are meaningless by construction.
- `OOM: micro_batch -> …` if it appears at all — the trainer halves the micro-batch and doubles the
  accumulation, holding the effective batch. It never shrinks `max_seq_len`; a truncated row would
  teach a cut-off label. Record the value it settled on: it changes the projection.
- `carve_mechanics` with `parse_failures: []`. A parse failure here is the format-identity
  invariant failing in practice, and it is a stop-and-report.

Also build the second arm's dataset — assembly only, no second training:

```bash
$PY scripts/train_qlora.py --build-only --with-synthetic
```

## 6. The projection, and the ceiling

`provenance.json` carries `seconds_per_step`; the steps per epoch are printed as `steps_per_epoch`.
Per arm: `steps_per_epoch × epochs × seconds_per_step`, at $0.53/hr.

```bash
$PY - <<'PY'
import json, pathlib
run = json.loads(pathlib.Path("/workspace/out/smoke/provenance.json").read_text())
sps = run["run"]["seconds_per_step"]
for arm, rows in (("real-only", run["n_train"]), ("with-synthetic", run["n_train"] + 600)):
    steps = -(-rows // 16) * 2          # effective batch 16, 2 epochs
    hours = steps * sps / 3600
    print(f"{arm:15} {steps:4} steps x {sps:5.2f} s = {hours:4.2f} h  ${hours * 0.53:5.2f}")
PY
```

**A projection over 4 h per arm stops the line** (amendment 3.4 (4)) — report it, do not start the
run and hope. The XLM-R baseline is the precedent: its projection was honoured and it landed at
101 min against a 128 min projection.

## 7. Home, then stop the pod

```bash
# --- on the Mac ---
mkdir -p results/train
scp -P <PORT> -r root@<HOST>:/workspace/out/smoke results/train/4b-smoke
scp -P <PORT> root@<HOST>:/workspace/out/smoke.log results/train/4b-smoke/

runpodctl pod stop <POD_ID>
runpodctl pod get <POD_ID>        # desiredStatus EXITED — this goes in the report
python3 scripts/runpod_guard.py --note "4b training smoke"
```

The adapter is a smoke artifact: it proves the checkpoint round-trips, and it is **not** a model
anyone scores. 4c trains from scratch with the same config on the full data.

Keep the network volume. 4c needs the same weights, and re-downloading 62 GB costs more pod time
than the volume costs to hold — which is exactly why the guard reads the account balance and not
just the pod's billing rows.

## When something goes wrong

Every branch starts with `runpodctl pod stop <POD_ID>`, then the report.

- **No capacity in CA-MTL-3.** Wait, or report. Never a second volume without an operator decision.
- **The dataset hashes differ from the Mac's.** Stop. A file did not travel, or the checkout is not
  HEAD.
- **The prompt SHA assert fires.** The prompts moved since the anchor was measured. Nothing about
  this is fixable on the pod: the anchor, the arms and the gates all hash the same prompt.
- **`LoRA on 0 modules`** cannot happen — the trainer refuses first. If it refuses, report the
  module names it saw rather than loosening the suffix list to whatever matches.
- **OOM at micro-batch 1.** The trainer re-raises rather than shrinking the sequence. Report the
  peak memory the log printed; 4a measured 18.9 GB for inference at batch 1, and a training figure
  far above that is a fact about the config, not a reason to truncate.
- **The carve eval reports parse failures.** Stop and report: the training targets and the eval
  parser have drifted apart, which is the one thing this step exists to prevent.
