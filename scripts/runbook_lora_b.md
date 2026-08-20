# Runbook — lora-b D3: two arms, one pre-registered attempt, and every rung executable

The order below is the money. `results/prereg_lora_b.json` is the law; every deadline here comes out
of it through `scripts/gate_lora_b.py`, and **nothing in this file may add a number the record does
not carry**. Where a number appears below it is an illustration of the instrument's output, never a
value to type.

**The one rule this runbook exists for:** the meter starts at `pod create` and stops at
`pod delete`. Not at ssh, not at the model load, not at the first optimizer step — a pod bills for
existing. `pod stop` does NOT stop it. **Delete, never stop.**

**The clock is CUMULATIVE (rung 7).** Every budget check counts across ALL pods of this attempt.
Each pod's `--terminate-after` is that pod's own create plus the 5.5 h hard stop LESS what every
closed pod already billed — **derived from the instrument, and checked by `--open` against the stamp
the platform actually got.** It is the one number this runbook makes you say twice, because the flag
is the only thing that enforces rung 7.

**One attempt.** The bar is `max(gold14(A), gold14(B)) ≥ 12/14` on the sealed gold r2, one shot, no
retry, no tuning. **The attempt is SPENT at the first GOLD-row reply generated** — not at create,
not at a loss line, and not at the format smoke, whose row is a training row outside both the sealed
fourteen and the eval pack. A red bar is an ANSWER: line B closes and the question returns to the
sitting.

**Guard reading at every milestone, pasted.** The rungs act on the READING, never on a projection:

```bash
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step lora-b --step-cap 6.00 \
  --until <ISO> --note "<what this milestone is>"
```

## 0 — before anything exists ($0)

```bash
runpodctl pod list -a && runpodctl serverless list && runpodctl network-volume list
git status --porcelain                       # the prereg must NOT be in it
PYTHONPATH=src python3.11 scripts/gate_lora_b.py --pre-create-check
python3.11 scripts/runpod_guard.py --step lora-b --step-cap 6.00 \
  --note "lora-b anchor, before the pod"
```

The three listings are the before-state the deletion proof is read against — the volume must appear
in all three readings, before and after, as the positive control that the listing works at all.
`--pre-create-check` is the never-two-pods rule and it runs BEFORE the create rather than as a
refusal after the second meter has started. `gate_lora_b.py` refuses to run at all while
`results/prereg_lora_b.json` is untracked or differs from HEAD: the git clock is what proves the
plan predates the money.

## 1 — create (the meter starts here)

```bash
runpodctl pod create --name mp-lora-b --gpu-id 'NVIDIA RTX A6000' --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after '<create + the seconds --pre-create-check left>'
```

`--terminate-after` is a chicken-and-egg on the FIRST pod only: run `--pre-create-check` first, take
the seconds it prints as left in the hard stop, and stamp create + that. From the second pod on, the
number `--pre-create-check` prints is already reduced by what the closed pods billed. Either way
`--open` re-derives the stamp and refuses the one you used if it is longer — the flag is the only
thing enforcing rung 7.

**Read `costPerHr` and the card back out of the create response and stamp the clock immediately:**

```bash
PYTHONPATH=src python3.11 scripts/gate_lora_b.py --open \
  --pod-id <POD_ID> --created-at '<the create response stamp, UTC ISO8601>' \
  --usd-per-hour <costPerHr> --card '<the card the response names>' \
  --terminate-after '<the very stamp `pod create` was given, copied from the command above>'
```

`--terminate-after` is REQUIRED and it is checked: rung 7 is enforced by that platform flag and by
nothing else, so the instrument compares what the platform actually got against `create +
(5.5 h − billed by every closed pod)` and REFUSES a window longer than the cumulative stop allows.
A refusal here means delete the pod and re-create it with the stamp the refusal prints. Rounding the
window down is always accepted — it only shortens it.

A `costPerHr` above **$0.80/h** is rung 1: delete the pod and STOP — no training, no endpoint. Exit
code 2 says so and the record keeps the reading either way.

## 2 — rung 2, the ssh dead-man (≤ 180 s of this pod's create-elapsed)

```bash
runpodctl ssh info <POD_ID>          # "pod not ready" for a minute or two is normal
PYTHONPATH=src python3.11 scripts/gate_lora_b.py --gate0            # WAIT / KILL
PYTHONPATH=src python3.11 scripts/gate_lora_b.py --gate0 --ssh-ok   # it answered
```

Exit codes ARE the rule: **3 = WAIT**, **2 = KILL/STOP**, **0 = GO**. On a KILL: delete, prove it by
listing, `--close-pod`, then `--recreate-check` before any replacement — the recovery clause allows
exactly ONE re-creation and rung 9 prices it before it exists.

## 3 — stage (~3 min, and the repo MUST be at this HEAD)

The pack pins the CURRENT parser sha, so the handshake refuses a stale checkout by design. The repo
has no remote; the transport is a git bundle.

**zsh does not word-split an unquoted variable holding ssh options.** Spell every flag literally.

```bash
SSHK=~/.runpod/ssh/runpodctl-ssh-key
git bundle create /tmp/market-pulse-lora-b.bundle HEAD
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -P <PORT> /tmp/market-pulse-lora-b.bundle \
    results/pass1_probe_b_pack.json results/lora_b_smoke_pack.json \
    scripts/pass1_pod_runner.py scripts/reader_v5_pod_runner.py scripts/reader_v4_pod_runner.py \
    root@<HOST>:/workspace/
```

```bash
ssh -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -p <PORT> root@<HOST>
# on the pod:
cd /workspace && rm -rf repo && git clone -q market-pulse-lora-b.bundle repo
cd repo && git rev-parse HEAD && git status --short      # equals the Mac's HEAD, empty
ls -d /workspace/venv /workspace/hf && du -sh /workspace/hf   # the volume is warm, or STOP
rm -rf /workspace/run                                    # the volume REMEMBERS a previous attempt
ls -d /workspace/run 2>&1 | tail -1                      # "No such file" — the proof, not the hope
```

If `/workspace/hf` is not there the weights are not on the volume, the boot is a 59 GB download, and
this registration did not price one: delete and STOP. The `rm -rf /workspace/run` is not tidiness —
a replacement pod mounts the same network volume, and an adapter directory left by a killed arm
would be mounted by `--adapter` as if this pod had trained it.

## 4 — arm A, watched

The command is the registration's own — `results/prereg_lora_b.json` → `arms.a.command` — and it is
copied from there, never retyped:

```bash
export HF_HOME=/workspace/hf
PYTHONPATH=/workspace/repo/src /workspace/venv/bin/python -u \
  /workspace/repo/scripts/train_qlora.py --data results/pass1_sft_arm_a.jsonl \
  --class-weights --out /workspace/run/arm_a 2>&1 | tee /workspace/run/arm_a.log
```

`-u` is not optional: the kill rules need a clock that can be watched go past. Run it from
`/workspace/repo` so the relative `--data` resolves.

From the Mac, in a second shell — **the scp comes FIRST, every single time**, because the gates read
the file on THIS machine and the pod writes to its own:

```bash
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -P <PORT> root@<HOST>:/workspace/run/arm_a/loss.jsonl results/lora_b_arm_a_loss.jsonl 2>/dev/null
PYTHONPATH=src python3.11 scripts/gate_lora_b.py --boot \
  --training-started-at '<the stamp of the first log line>'      # rung 3, once
PYTHONPATH=src python3.11 scripts/gate_lora_b.py --train --arm a --loss results/lora_b_arm_a_loss.jsonl
```

`--train` is rungs 4 and 8 together and it is re-run at **every** log line — it costs nothing and it
is what deletes the pod before the cap rather than after. Rung 4 kills on five consecutive lines over
122 s/step; rung 8 kills when the projected attempt total — cumulative billed + the remaining steps
at the MEASURED rate + arm B's leg + the eval + the registered overhead — passes either the $6.00 cap
at the live price or the 5.5 h hard stop. On a KILL the prereg's arm-A-only branch applies.

## 5 — the arm-A milestone (rung 5), guard reading PASTED

```bash
python3.11 scripts/runpod_guard.py --step lora-b --step-cap 6.00 --until <ISO> \
  --note "lora-b arm A trained"
PYTHONPATH=src python3.11 scripts/gate_lora_b.py --milestone --reading <the guard's USD>
```

Over **$2.50** and arm B does not start: the session closes with arm A. The STOP is on the READING,
never on a projection.

## 6 — arm B, same rungs

`arms.b.command` from the registration, `--out /workspace/run/arm_b`, its own `loss.jsonl`, and
`--train --arm b` at every log line.

## 7 — the format smoke, per arm, BEFORE its eval (rung 10)

Its own out-file, never an arm's eval file — the shipped runner's resume skips every unit already
answered, so a smoke written into the eval file would make that eval answer one unit fewer and look
complete (Dv560).

```bash
# on the pod, for each arm that trained:
PYTHONPATH=/workspace/repo/src /workspace/venv/bin/python -u /workspace/pass1_pod_runner.py \
  --pack /workspace/lora_b_smoke_pack.json --repo /workspace/repo \
  --out /workspace/run/smoke_arm_a.jsonl --adapter /workspace/run/arm_a/adapter
```

```bash
# on the Mac:
scp ... root@<HOST>:/workspace/run/smoke_arm_a.jsonl results/lora_b_smoke_a.jsonl
PYTHONPATH=src python3.11 scripts/gate_lora_b.py --smoke --arm a --replies results/lora_b_smoke_a.jsonl
```

A KILL means that arm is **NOT evaluated**. If NO arm passes, the session closes, the attempt is
**NOT spent** — no eval output was seen — and it returns to the team lead. This is a
transport-format check and not a bar peek: the row is a training row, asserted outside both the
sealed fourteen and the eval pack's sixty-four by the producer that built the pack and again by the
gate that reads it.

## 8 — eval, each arm into its OWN out-file

`arms.*.eval_command` from the registration. Both arms answer probe-b's own 64-unit pack — 14 gold
and 50 census — and the base is **never re-run**: its per-row verdicts are sealed in
`results/pass1_probe_b_verdict.json` and the arms are paired against them on identical instances.

**The attempt is SPENT at the first gold-row reply this step generates.**

## 9 — scp EVERYTHING, before any verdict

```bash
ssh ... -p <PORT> root@<HOST> 'cd /workspace/run && find . -type f | sort | xargs shasum -a 256'
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -P <PORT> -r root@<HOST>:/workspace/run results/lora_b_run_artifacts
```

Per-row raw replies, both adapters with their hashes, both loss logs, both pod logs, the smoke
out-files. The hashes are taken ON THE POD and again on the Mac: an adapter that arrived truncated
would otherwise be discovered by a verdict that scored it. **No verdict is computed before this
step completes.**

**Then put each arm's eval replies at the paths the scorer reads — one command per arm, and the
names differ on purpose.** The pod writes `eval_arm_<x>.jsonl`; `scripts/score_lora_b.py` reads
`results/lora_b_eval_arm_<x>.jsonl` and the adapter record beside it. A copy that did not happen
would otherwise be reported as «neither arm produced a reply, the attempt is NOT spent» over a
session that spent it ([[fetch_before_you_delete]]):

```bash
for ARM in a b; do
  scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
      -P <PORT> root@<HOST>:/workspace/run/eval_arm_$ARM.jsonl \
      results/lora_b_eval_arm_$ARM.jsonl
  scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
      -P <PORT> root@<HOST>:/workspace/run/eval_arm_$ARM.jsonl.adapter.json \
      results/lora_b_eval_arm_$ARM.jsonl.adapter.json
done
ls -l results/lora_b_eval_arm_*.jsonl*        # every arm that was evaluated, or STOP
wc -l results/lora_b_eval_arm_*.jsonl         # 64 per evaluated arm
```

An arm that was never evaluated — a milestone STOP before arm B, or a smoke KILL — has no file and
that is correct. `score_lora_b.py` reads `results/lora_b_run.json` and REFUSES to score while an arm
whose smoke went GO has no replies on this machine, so the two cases cannot be confused.

## 10 — delete, and prove it

```bash
runpodctl pod delete <POD_ID>
runpodctl pod list -a                # []
runpodctl serverless list            # [] — nothing was ever created here
runpodctl network-volume list        # the volume, unchanged: the POSITIVE CONTROL
PYTHONPATH=src python3.11 scripts/gate_lora_b.py --close-pod \
  --deleted-at '<UTC ISO8601>' --outcome '<why this pod ended>'
python3.11 scripts/runpod_guard.py --step lora-b --step-cap 6.00 \
  --note "lora-b pod deleted; <what was trained and evaluated>"
```

Three listings, and the volume has to be in the last one: a listing that returns `[]` for everything
proves the command runs, not that the pod is gone.

## 11 — D4, on the Mac ($0)

The verdict is the scorer's, never the eyeball, and it is one attempt:

```bash
ls -l results/lora_b_eval_arm_*.jsonl                    # the §9 copy, re-read before scoring
PYTHONPATH=src python3.11 scripts/score_lora_b.py        # gold-14 per arm, census-50 beside it
PYTHONPATH=src python3.11 scripts/score_lora_b.py --outdir /tmp/again   # the determinism pair
make check
python3.11 scripts/runpod_guard.py --step lora-b --step-cap 6.00 --close \
  --until <the last session's `at`> --tolerance 0.07 --note "lora-b settled"
```

The walk posts hours late; `--close` over an unanswered walk is refused by the guard and must be — a
lower bound goes in the report as a named debt instead.
