# Runbook — `lora-c-run r3`, the ONE paid pod session

The transport, written down before the meter starts. A report proves what happened; it does not
tell the next session how to do it ([[a_report_proves_it_does_not_instruct]]) — and this session
runs for up to five hours, long enough that its own context will be summarised before it ends.

**Registration:** `results/prereg_lora_c_run_r3.json` (committed — the gate refuses an untracked
one). **Frozen input:** `results/prereg_lora_c.json`, sha `4d5a8f1d34765b4a…`. **Cap $7.00 all-in,
hard stop 18 000 s.** Every gate command below is `PYTHONPATH=src python3.11
scripts/gate_lora_c_run_r3.py …`, abbreviated `GATE` from here down.

## Fixed values

| | |
|---|---|
| volume | `mp-lora-c` · id **`soymlju8q0`** · 100 GB · CA-MTL-3 |
| card | `--gpu-id "NVIDIA A100 80GB PCIe"` · displayName `A100 PCIe` · $1.39/h secure |
| image | `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404` · container disk 30 GB |
| revision | `842da3794eaa0b77d5f08bae87a17459d91ff475` |
| on the volume | `/workspace/hf` (59 GiB, pinned) · `/workspace/venv` (editable install bound to `/workspace/repo`) · `/workspace/repo` (checkout at `997a2a2`) |
| this session's outputs | `/workspace/r3/` — nothing else on the volume is written |

**The venv is NOT rebuilt.** `git diff 997a2a2 HEAD -- pyproject.toml` is empty, so the dependency
set has not moved; the one-line stack print is the proof, and 132 s stays out of the plan
([[a_warm_environment_is_bound_to_a_path]]).

## 0 — before the create ($0)

```bash
GATE --read-back                       # the refusal gate: nine numbers, all re-derived
GATE --pre-create-check                # rung 7
python3.11 scripts/runpod_guard.py     # the money, from the guard and never from prose
git bundle create /tmp/mp-r3.bundle HEAD && git rev-parse HEAD
```

## 1 — create, boot, stage

`--terminate-after` is computed from the clock a second BEFORE the create, so the window the
platform gets is never longer than the one the hard stop allows (overshoot is what the gate bounds,
and it tolerates 60 s).

```bash
STOP=$(python3 -c "import datetime;print((datetime.datetime.now(datetime.UTC)+datetime.timedelta(seconds=18000)).strftime('%Y-%m-%dT%H:%M:%SZ'))")
runpodctl pod create --name mp-lora-c-r3 --gpu-id "NVIDIA A100 80GB PCIe" --gpu-count 1 \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --network-volume-id soymlju8q0 --volume-mount-path /workspace \
  --data-center-ids CA-MTL-3 --cloud-type SECURE --ports '22/tcp' --ssh \
  --terminate-after "$STOP"

GATE --open --pod-id <ID> --created-at <ISO> --usd-per-hour <costPerHr> \
     --card '<displayName>' --terminate-after "$STOP"      # rungs 0 and 6 — a KILL here is a delete
runpodctl ssh info <ID>                                    # poll at 3–4 s; «pod not ready» is normal
GATE --gate0 --ssh-ok                                      # rung 1
```

Staging — the bundle lands, and the checkout is updated **in place**. A clone to a new directory is
the Dv19 shape: the editable install resolves imports through `/workspace/repo` and does not follow.

```bash
scp -P <PORT> -o StrictHostKeyChecking=no /tmp/mp-r3.bundle root@<HOST>:/workspace/
ssh -p <PORT> root@<HOST> 'set -e
  cd /workspace/repo
  git fetch -q /workspace/mp-r3.bundle HEAD && git checkout -qf FETCH_HEAD
  git rev-parse HEAD; git status --porcelain --untracked-files=no
  mkdir -p /workspace/r3
  /workspace/venv/bin/python -c "
import torch, transformers, bitsandbytes, market_pulse
from market_pulse import local_llm, pass1_v3, prompts, pass2, pass2_r2, scorer
print(torch.__version__, transformers.__version__, bitsandbytes.__version__,
      torch.cuda.get_device_name(0), market_pulse.__file__)"'
```

`market_pulse.__file__` must read `/workspace/repo/src/market_pulse/__init__.py` — that is what
proves the editable install still resolves to the checkout this session just moved. The import list
is every module this session actually touches, not just the package: a top-level import proves the
finder found the package, and the module that fails is the one nobody imported until the eval leg,
with the model loaded, on a meter — the pass1-probe shape at 427 billed seconds. `git diff --stat
997a2a2 HEAD -- src/` is **empty**, so the failure this guards against is a packaging one, not a
code one — which is exactly the kind that is invisible until it is expensive.

## 2 — the load proof (blob invariant)

```bash
ssh -p <PORT> root@<HOST> 'cd /workspace/repo && HF_HOME=/workspace/hf PYTHONPATH=src \
  /workspace/venv/bin/python -u scripts/load_proof_r3_pod_runner.py \
    --revision 842da3794eaa0b77d5f08bae87a17459d91ff475 --out /workspace/r3/load_proof.json'
scp -P <PORT> root@<HOST>:/workspace/r3/load_proof.json results/lora_c_run_r3_load_proof.json
GATE --load-proof --started-at <ISO> --proof results/lora_c_run_r3_load_proof.json
```

The whole-cache `du` delta is REPORTED and grades nothing; a grown or new blob is the KILL.

## 3 — the smoke: the line's first s/step at 3 072

Every long stage runs under `nohup … &` with its own log. A dropped ssh must not kill a training
run ([[a_remote_job_outlives_its_watcher]]), and the log is what rung 2 is measured against.

```bash
ssh -p <PORT> root@<HOST> 'cd /workspace/repo && mkdir -p /workspace/r3 && \
  HF_HOME=/workspace/hf PYTHONPATH=src nohup /workspace/venv/bin/python -u \
    scripts/train_qlora_v3.py --class-weights --max-steps 6 \
      --data results/pass1_sft_v3_train.jsonl --out /workspace/r3/smoke_a \
    > /workspace/r3/smoke.log 2>&1 & echo $!'
```

Poll every ~120 s (rung 2's deadline is 600 s from the last thing that HAPPENED):

```bash
ssh -p <PORT> root@<HOST> 'date -u +%FT%TZ; wc -c < /workspace/r3/smoke.log; \
  tail -3 /workspace/r3/smoke.log; ls /workspace/r3/smoke_a 2>/dev/null'
GATE --liveness --last-event <the stamp of the last growth>
```

When `provenance.json` exists:

```bash
scp -P <PORT> root@<HOST>:/workspace/r3/smoke_a/provenance.json results/lora_c_run_r3_smoke_provenance.json
scp -P <PORT> root@<HOST>:/workspace/r3/smoke_a/loss.jsonl      results/lora_c_run_r3_smoke_loss.jsonl
GATE --smoke --provenance results/lora_c_run_r3_smoke_provenance.json \
     --loss results/lora_c_run_r3_smoke_loss.jsonl
```

**The rate is `run.seconds_per_step`.** The two loss lines are printed beside it and never averaged
into it: each divides by `log_every: 5` regardless of the window it covers, so the step-6 line reads
about a fifth of the truth (Dv814). An OOM is read out of `run.micro_batch_final` — the trainer
halves and carries on, so the crash the registration imagines may never come.

## 4 — the projection rung, and what it is deciding

```bash
python3.11 scripts/runpod_guard.py            # the reading, in USD
GATE --projection --after smoke --reading <USD>
```

**Read the decomposition beside the verdict.** The gate prints
`the_decomposition_REPORT_ONLY.the_final_steps_isolated_wall_seconds` — the last loss line's ONE step
multiplied back by `log_every`. It grades nothing. It is there because the quotable rate is the
whole loop's wall over its steps and the loop's first step pays CUDA autotuning and the allocator's
first growth: over 6 steps that is amortised over 6, over arm A's 62 it is amortised over 62. If the
projection KILLs at Y s/step while one steady step ran at X < 62.15, that inequality is the finding.

**GO or KILL is not knowable before the smoke.** The registered charge affords **62.15 s/step**
(the hard stop binds before the cap), and the only two readings this repo owns are **61.047** and
**68.442**, both taken at ≤1 222 tokens against this line's 1 445–2 975. A KILL here is compliance:
pull everything bought, tear down, report.

## 5 — arm A, then eval A

```bash
# 62 optimizer steps
ssh … 'cd /workspace/repo && HF_HOME=/workspace/hf PYTHONPATH=src nohup /workspace/venv/bin/python -u \
  scripts/train_qlora_v3.py --class-weights --data results/pass1_sft_v3_train.jsonl \
    --out /workspace/r3/arm_a > /workspace/r3/arm_a.log 2>&1 & echo $!'
# poll every ~120 s AND re-fire the projection: it recomputes against CURRENT elapsed, so a run
# that is degrading flips it to KILL. That is this session's training watchdog — lora-b had
# `gate_lora_b.watchdog` on 5 consecutive over-threshold log lines and r3's rung table has no
# equivalent, so between arm A's start and its end only rung 2 and the platform flag stand.
#   GATE --projection --after smoke --reading <USD>      <- during arm A
# when the adapter is written, PULL IT IMMEDIATELY
scp -rP <PORT> root@<HOST>:/workspace/r3/arm_a results/lora_c_run_r3_artifacts/

# eval A — the v3 leg only, with the adapter it trained
ssh … 'cd /workspace/repo && HF_HOME=/workspace/hf PYTHONPATH=src nohup /workspace/venv/bin/python -u \
  scripts/pass1_v3_pod_runner.py --pack results/lora_c_eval_pack.json --only v3 \
    --outdir /workspace/r3/eval_a --adapter /workspace/r3/arm_a/adapter --repo /workspace/repo \
  > /workspace/r3/eval_a.log 2>&1 & echo $!'
# the rate rung fires DURING the leg, off the growing out-file
scp -P <PORT> root@<HOST>:/workspace/r3/eval_a/lora_c_eval_v3.jsonl results/lora_c_run_r3_eval_a.jsonl
GATE --rate --leg eval_a --replies results/lora_c_run_r3_eval_a.jsonl --started-at <ISO>

# pass 2, rebuilt from arm A's OWN out-file, at the 15 569 ceiling
ssh … 'cd /workspace/repo && PYTHONPATH=src /workspace/venv/bin/python \
  scripts/build_lora_c_pass2_pack.py --out-file /workspace/r3/eval_a/lora_c_eval_v3.jsonl \
    --leg arm_a --out /workspace/r3/pass2_arm_a_pack.json'
ssh … 'cd /workspace/repo && HF_HOME=/workspace/hf PYTHONPATH=src nohup /workspace/venv/bin/python -u \
  scripts/pass2_lora_c_pod_runner.py --pack /workspace/r3/pass2_arm_a_pack.json \
    --outdir /workspace/r3/pass2_a --repo /workspace/repo > /workspace/r3/pass2_a.log 2>&1 & echo $!'

# <N> is READ, never typed: the rebuilt pack's own leg count
python3 -c "import json;print(len(json.load(open('results/lora_c_run_r3_pass2_arm_a_pack.json'))['legs'][0]['items']))"
GATE --projection --after eval_a --reading <USD> --pass-2-threads-realised <N>
```

## 6 — arm B, eval B, the marker census

Identical, with `--data results/pass1_sft_v3_arm_b.jsonl`, `--out /workspace/r3/arm_b`, `--leg
arm_b`, and 82 steps. Then, **after arm B's bar is already scored**, the report-only census:

```bash
ssh … 'cd /workspace/repo && HF_HOME=/workspace/hf PYTHONPATH=src nohup /workspace/venv/bin/python -u \
  scripts/pass1_v3_pod_runner.py --pack results/lora_c_marker_census_pack.json \
    --outdir /workspace/r3/census --adapter /workspace/r3/arm_b/adapter --repo /workspace/repo \
  > /workspace/r3/census.log 2>&1 & echo $!'
GATE --projection --after eval_b --reading <USD>
```

## 7 — teardown, proven

`scp -r host:/workspace/r3 <dir>/` lands as `<dir>/r3/…`. Know the shape before the KILL path,
which is the worst moment to meet a nesting surprise.

```bash
mkdir -p results/lora_c_run_r3_artifacts
scp -rP <PORT> root@<HOST>:/workspace/r3 results/lora_c_run_r3_artifacts/   # -> .../r3/...
ssh -p <PORT> root@<HOST> 'cd /workspace/r3 && find . -type f | sort | xargs shasum -a 256'
runpodctl pod delete <ID>
GATE --close-pod --deleted-at <ISO> --outcome '<why>'
runpodctl pod list -a && runpodctl network-volume list   # BOTH volumes are the positive control
python3.11 scripts/runpod_guard.py
```

The hashes are taken on BOTH sides. A pull nobody hashed is a pull nobody checked.

## Why the tight slack at the end is survivable

At a GO near 61 s/step the arithmetic is 144 × 61 = 8 784 s of training on 9 050 s of fixed part —
**17 834 s against an 18 000 s terminate**, 166 s of slack. The platform may terminate inside the
tail. That is tolerable for one reason and it has to stay true: **everything this session writes
goes to `/workspace/r3`, which is on the network volume `mp-lora-c`.** A terminate destroys the
container, not the volume, and the recovery clause's one re-create can mount and retrieve. Nothing
may be written to the container disk — check every `--out`, `--outdir` and `--out-file` above: all
of them are `/workspace/…`.

## The DO-NOTs that bite on a meter

- never two pods; a KILL means delete, prove by listing, then `--close-pod`;
- `micro_batch_size` is not edited on a pod — an OOM is a KILL and a STOP;
- no retry of a bar and no tuning after any eval output is seen;
- the adapters are never merged;
- `mp-srv2` is not touched — no mount, no write, no delete;
- artifacts already pulled are never re-bought.
