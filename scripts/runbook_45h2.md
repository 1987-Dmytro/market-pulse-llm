# Runbook — Phase 4.5h2: test v4, the fresh anchor, and the пласт ablation

Copy-paste, in order. It assumes `scripts/runbook_4c.md` has been read once: the pod
pattern, the venv, the bundle, the continuous sync. **Three pod sessions**, and the two arm
sessions cannot be repeated — each arm trains in full and is scored on the frozen sets
exactly once. A crash resumes; it never restarts-and-rescores.

**Budget: $9.00 of the $17.53 left under the $25 Phase-4 cap.** Both caps are enforced
before every start by `scripts/runpod_guard.py --step 45h2 --step-cap 9.00`; the step
anchor is `results/spend_45h2.json` and is never regenerated.

**Per-arm ceiling 8.5 h** (operator decision 2026-08-04, on the with-post projection —
amendment 3.9's 6.5 h was set against a rendering without the parent post). A projection
that crosses it mid-run is a stop-and-report, not a thing to ride out.

---

## What is different from 4c, and why each thing bites

| | 4c | 4.5h2 |
|---|---|---|
| test set | `*.jsonl` (v2) | `*_v4.jsonl` — `--testset-version v4` on every eval |
| T1 rendering | `T1` (five intents) | `T1v2_with_post` — six, and the parent post travels |
| training sources | the v1 files | the `_tax2` siblings (amendment 3.9 (1)) |
| the ablation's variable | `synthetic_sarcasm.jsonl` | the пласт, `--with-plast` |
| arm names | `real-only` / `with-synthetic` | `without-plast` / `with-plast` |
| `max_seq_len` | 1024 | 1408 — the post makes the longest row 1 388 tokens |
| G1b slice | `results/g1b_slice.json` | `results/g1b_slice_v4.json`, written by this phase's anchor |

**`data/raw/posts/` is not in git** and the with-post rendering cannot run without it:
`parents.text_for` raises on a missing parent rather than asking a row without its post. It
travels as its own tarball, and **`COPYFILE_DISABLE=1` is not optional on a Mac** — without
it the tar carries `._*` AppleDouble files, `parents.load` globs `*.jsonl`, and the run dies
on a UnicodeDecodeError after the weights have loaded.

## 0. Before the first pod (Mac)

```bash
cd ~/Desktop/Projects/market-pulse-llm
git status --short                       # empty: the pod runs a checkout of HEAD
make check                               # green
ruff format --check .                    # make check does not run the formatter
python3 scripts/runpod_guard.py --step 45h2 --step-cap 9.00
PYTHONPATH=src python3 scripts/train_qlora.py --build-only               # arm A
PYTHONPATH=src python3 scripts/train_qlora.py --build-only --with-plast  # arm B
```

Measured 2026-08-04: arm A `n_train` **2 171**, arm B **3 457**, `carve_sha256`
`8347abd74ae9…` **shared by both** (amendment 3.9 (2): the carve is drawn before the пласт
joins), 1 286 пласт ids added and 0 rows removed.

## 1. The bundle and the posts

```bash
git bundle create /tmp/market-pulse-45h2.bundle HEAD
COPYFILE_DISABLE=1 tar czf /tmp/raw-posts.tgz data/raw/posts
```

**Both arms clone the same bundle file.** The ablation is "identical config and seed,
exactly one data path differs"; a second bundle built from a later HEAD would make the arms
differ by a commit as well. The anchor's bundle is necessarily earlier — the bars and the
verdict script are committed between it and the arms, which is the point of the ordering.

## 2. The pod (once per session)

```bash
runpodctl gpu list --output json | python3 -c "
import json,sys
for g in json.load(sys.stdin):
    if g['displayName'] == 'RTX A6000':
        [print(d['dataCenterId'], d['stockStatus']) for d in g['dataCenterAvailability']]"

python3 scripts/runpod_guard.py --step 45h2 --step-cap 9.00
runpodctl pod create \
  --name market-pulse-45h2-<session> \
  --gpu-id "NVIDIA RTX A6000" --gpu-count 1 \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 \
  --container-disk-in-gb 80 \
  --data-center-ids <DC with stock> --cloud-type SECURE \
  --ports '22/tcp' --ssh \
  --stop-after <UTC ISO8601, a good margin past the projection>

runpodctl pod list -a --output json      # the id
runpodctl ssh info <POD_ID>              # "pod not ready" for a minute or two is normal
```

**The SSH key is `~/.runpod/ssh/runpodctl-ssh-key`, not a `~/.ssh` default.** Plain
`ssh root@…` fails with `Permission denied (publickey)`; pass `-i` on every ssh and scp.

```bash
SSHK=~/.runpod/ssh/runpodctl-ssh-key
SSHOPT="-i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

scp $SSHOPT -P <PORT> /tmp/market-pulse-45h2.bundle /tmp/raw-posts.tgz root@<HOST>:/workspace/
ssh $SSHOPT -p <PORT> root@<HOST>
# --- on the pod ---
cd /workspace && git clone market-pulse-45h2.bundle repo && cd repo
git rev-parse HEAD && git status --short            # equal to the Mac's HEAD, and empty
tar xzf /workspace/raw-posts.tgz -C /workspace/repo
ls data/raw/posts/                                  # exactly four .jsonl, no `._*`
python3 -m venv --system-site-packages /workspace/venv    # PEP 668: do not pip into the image
export HF_HOME=/workspace/hf RUNPOD_POD_ID=<POD_ID>       # NOT inherited over ssh
PY=/workspace/venv/bin/python
$PY -m pip install -e '.[dev,gpu]'
PYTHONPATH=src $PY scripts/eval_zero_shot.py --model google/gemma-4-31b-it \
  --backend local --smoke --testset-version v4      # renders every row, loads no weights
```

That smoke is the cheap version of every refusal the with-post path can raise — a missing
parent, an unregistered rendering, a caption on a post that has text of its own — and it
costs seconds instead of the twelve minutes the weights take to arrive.

## 3. The anchor (session 1, no adapter exists yet)

```bash
setsid nohup env HF_HOME=/workspace/hf RUNPOD_POD_ID=<POD_ID> PYTHONPATH=src \
  $PY -u scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local \
    --batch-size 1 --testset-version v4 \
    --revision 842da3794eaa0b77d5f08bae87a17459d91ff475 \
    --eval-checkpoint /workspace/out/anchor-eval.jsonl \
    --record-out /workspace/out/anchor-record.json \
  > /workspace/out/anchor.log 2>&1 < /dev/null &
pgrep -af eval_zero_shot         # the process is the liveness check, not the log
```

`--revision` is pinned to the config's, the way 4a's anchor pinned it: a floating repo HEAD
would make the anchor and the arms unpaired on the weights themselves. Measured 2026-08-04:
**2.73 s/row**, ~34 minutes for 758 rows.

Home, then — **before any arm** — the bars and the rule:

```bash
# --- on the Mac ---
scp $SSHOPT -P <PORT> root@<HOST>:/workspace/out/anchor-record.json /tmp/
scp $SSHOPT -P <PORT> "root@<HOST>:/workspace/repo/results/predictions/*.jsonl" results/predictions/
scp $SSHOPT -P <PORT> root@<HOST>:/workspace/repo/results/g1b_slice_v4.json results/
python3 scripts/eval_zero_shot.py --append-record /tmp/anchor-record.json
PYTHONPATH=src python3 scripts/gate_bars.py --version v4 --out results/gate_bars_45h.json
PYTHONPATH=src python3 scripts/gate_verdict_45h.py     # refuses: no arm exists yet
git add results/gate_bars_45h.json results/g1b_slice_v4.json … && git commit
runpodctl pod delete <POD_ID>
python3 scripts/runpod_guard.py --step 45h2 --step-cap 9.00 --note "45h2 anchor"
```

**Scoring an arm before that commit is a contract violation** (`docs/PROMPT-4.5h2.md`
DO NOT). No bar and no threshold is typed anywhere: `gate_bars.py` derives all five from the
anchor record it just appended.

## 4. Resume proof — on each arm's pod, before the arm

Its own directory, never the arm's, or the arm inherits two runs' loss curve and a
pre-written adapter.

```bash
$PY scripts/train_qlora.py --out /workspace/out/resume-proof --max-steps 10
$PY scripts/train_qlora.py --out /workspace/out/resume-proof \
   --resume-from /workspace/out/resume-proof --max-steps 15
cat /workspace/out/resume-proof/loss.jsonl
```

PASS is two things and the second is load-bearing: the printed `resumed at epoch 0 row N,
optimizer step 10` continues rather than resets, and the step-15 loss sits on the step-10
trajectory. `PagedAdamW8bit` maps state **by parameter index** — a different parameter order
puts the wrong momentum on the wrong tensor with no exception at all, and only the loss says
so. **Resume fails → STOP.** Do not start a multi-hour arm on a pod that cannot be resumed.

## 5. The arm

```bash
setsid nohup env HF_HOME=/workspace/hf RUNPOD_POD_ID=<POD_ID> PYTHONPATH=src \
  $PY -u scripts/train_qlora.py --out /workspace/out/arm-a \
  > /workspace/out/arm-a.log 2>&1 < /dev/null &
```

`--with-plast` for arm B, `--out /workspace/out/arm-b`. No `--max-steps`: the full 270 (arm
A) or 432 (arm B) steps, 2 fixed epochs, no early stopping.

**Sync continuously, from the Mac, in its own shell.** Nothing may exist only on the pod:

```bash
while true; do
  rsync -az -e "ssh $SSHOPT -p <PORT>" root@<HOST>:/workspace/out/arm-a/ results/train/45h2-arm-a/
  date -u +'%H:%M:%SZ synced'; sleep 900
done
```

`save_every: 100` is the real recovery granularity — a crash costs at most ~100 steps.
Projected from the fit on 4c arm A (s/step ≈ −5.68 + 0.04701 × padded tokens per
micro-batch, validated on 4c arm B to −0.1%): **arm A ≈ 5.0 h, arm B ≈ 8.2 h.** Watch
`seconds_per_step` in `loss.jsonl` against the 8.5 h ceiling from the first logged line.

## 6. The eval — same session, separate process

```bash
setsid nohup env HF_HOME=/workspace/hf RUNPOD_POD_ID=<POD_ID> PYTHONPATH=src \
  $PY -u scripts/eval_zero_shot.py --model google/gemma-4-31b-it --backend local \
    --testset-version v4 --revision 842da3794eaa0b77d5f08bae87a17459d91ff475 \
    --adapter /workspace/out/arm-a/adapter --arm without-plast --batch-size 1 \
    --eval-checkpoint /workspace/out/arm-a-eval.jsonl \
    --record-out /workspace/out/arm-a-record.json \
  > /workspace/out/arm-a-eval.log 2>&1 < /dev/null &
```

`--arm with-plast` for arm B. Everything that could refuse has refused before the weights
load: the v4 anchor, the slice hash, the adapter's own provenance, the arm label, the prompt
hashes **and the prompt revision** — that last one is new, and it is the guard that catches
an adapter trained through a rendering the eval is not scoring through.

**If it crashes, re-run the same command.** `--eval-checkpoint` holds every row already
scored; its header refuses a file another arm or another adapter wrote.

## 7. Home, verify, delete — then the verdict

```bash
rsync -az -e "ssh $SSHOPT -p <PORT>" root@<HOST>:/workspace/out/arm-a/ results/train/45h2-arm-a/
scp $SSHOPT -P <PORT> root@<HOST>:/workspace/out/arm-a-record.json /tmp/
scp $SSHOPT -P <PORT> "root@<HOST>:/workspace/repo/results/predictions/*.jsonl" results/predictions/
PYTHONPATH=src python3 -c "
from market_pulse import records; from pathlib import Path
print(records.artifact_sha256(Path('results/train/45h2-arm-a/adapter')))"   # equals the record's
python3 scripts/eval_zero_shot.py --append-record /tmp/arm-a-record.json
runpodctl pod delete <POD_ID>
python3 scripts/runpod_guard.py --step 45h2 --step-cap 9.00 --note "45h2 arm A"
```

Then repeat from step 2 for arm B. **Arm B launches on the frozen config whatever arm A's
numbers look like** — reading one arm as a result is how a paired ablation stops being one.

```bash
PYTHONPATH=src python3 scripts/gate_verdict_45h.py --record results/verdict_45h2.json
```

Both columns, the rule's inputs and its arithmetic, the selected arm, five verdicts against
bars derived from the v4 anchor. That output is the artifact — the ADR quotes it.

## When something goes wrong

- **The with-post smoke fails on a missing parent.** The raw posts did not travel, or the
  tar carried `._*` files. Fix it before the weights, not after.
- **Resume proof fails.** Stop. The arm does not start.
- **Training crashes.** Resume from the last synced state (`--resume-from` = `--out`) and
  log it. That is not a second attempt; a restart from step 0 would be.
- **The eval crashes.** Re-run with the same `--eval-checkpoint`. Completed rows are never
  re-scored.
- **The projection crosses 8.5 h mid-run.** Stop and report before the ceiling, not after.
- **A slice row does not parse.** The eval refuses to write a record and names the ids. Do
  not read a short slice as a failed G1b — report it.
- **Either cap is reached.** The guard exits 1. An overrun aborts and reports; a cap is not
  raised to finish a run.
- **A gate fails.** Report it plainly. A failed gate closes its question, and nothing is
  retrained.
