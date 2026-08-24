# Runbook — lora-c-run r2: four legs, one attempt, and every rung executable

The order below is the money. `results/prereg_lora_c.json` is the law; every deadline here comes out
of it through `scripts/gate_lora_c.py`, and **nothing in this file may add a number the record does
not carry**. Where a number appears below it is an illustration of the instrument's output, never a
value to type.

**The meter starts at `pod create` and stops at `pod delete`.** Not at ssh, not at the model load. A
pod bills for existing and `pod stop` does NOT stop it. **Delete, never stop.**

**The create is the FREEZE.** `results/prereg_lora_c.json` says `state: DRAFT — frozen only by
lora-c-run's first pod create`. Nothing under `frozen_when_the_pod_exists` is written after it — and
`scripts/gate_lora_c.py` refuses to run at all while that record is untracked or differs from HEAD,
which is what proves the plan predates the money.

**One attempt.** Three bars per arm, all-or-RED, `results/prereg_lora_c.json::bars`. The attempt is
**SPENT at the first reply an ADAPTER leg generates against eval set E** — rung 8. The base legs are
the BEFORE column and spend nothing; the smoke trains and generates no eval reply.

**Guard reading at every milestone, PASTED.** The rungs act on the READING, never on a projection:

```bash
python3.11 scripts/runpod_guard.py --step lora-c --step-cap 4.00 --until <ISO> \
  --note "<what this milestone is>"
```

## 0 — before anything exists ($0)

```bash
runpodctl pod list -a && runpodctl serverless list && runpodctl network-volume list
git status --porcelain                      # the prereg must NOT be in it
PYTHONPATH=src python3.11 scripts/gate_lora_c.py --pre-create-check      # rung 7
python3.11 scripts/runpod_guard.py --step lora-c --step-cap 4.00 \
  --note "lora-c anchor, before the pod"
```

The three listings are the before-state the deletion proof is read against — the volume must appear
in all three readings, before and after, as the positive control that the listing works at all.

## 1 — create (the meter starts here)

Ruling (о) names the card: **RTX PRO 4500, 32 GB, $0.72/h secure, EU-RO-1** — the network volume's
own datacenter. `results/lora_c_stock_probe.json` read A6000 as `none` there. **If the create is
refused for stock, ONE fallback create on a 4090 at $0.74 is pre-authorized; anything else is a
STOP.**

The `--gpu-id` strings below are the PLATFORM's own, copied out of
`results/lora_c_stock_probe.json` — `NVIDIA RTX PRO 4500 Blackwell` and, for the fallback,
`NVIDIA GeForce RTX 4090`. A name this repo invented is refused by the create, and that refusal
reads exactly like a stock refusal while burning one of the two creates the recovery clause allows.
Rung 0 grades BOTH the price and the card name.

```bash
runpodctl pod create --name mp-lora-c --gpu-id 'NVIDIA RTX PRO 4500 Blackwell' --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after '<create + the seconds --pre-create-check left>'
```

A REFUSED create costs $0, creates nothing and does not spend the attempt. Prove it with
`runpodctl pod list -a` → `[]` and do NOT run `--open`.

**Read `costPerHr` and the card back out of the create response and stamp the clock immediately:**

```bash
PYTHONPATH=src python3.11 scripts/gate_lora_c.py --open \
  --pod-id <POD_ID> --created-at '<the create response stamp, UTC ISO8601>' \
  --usd-per-hour <costPerHr> --card '<the displayName the response names>' \
  --terminate-after '<the very stamp `pod create` was given, copied from the command above>'
```

Rungs 0 and 6 together. **Rung 0 refuses a price this record holds no column for — including one
CHEAPER than every column**, because every projection rung divides by the price and the plan was
never solved at an unregistered one. Rung 6 re-derives the backstop and refuses a window longer than
the cumulative hard stop allows: that platform flag is the only thing enforcing it.

## 2 — rung 1, the boot gate (≤ 500 s of this pod's create-elapsed)

```bash
runpodctl ssh info <POD_ID>          # "pod not ready" for a minute or two is normal
PYTHONPATH=src python3.11 scripts/gate_lora_c.py --gate0            # WAIT / KILL
PYTHONPATH=src python3.11 scripts/gate_lora_c.py --gate0 --ssh-ok   # it answered
```

Exit codes ARE the rule: **3 = WAIT**, **2 = KILL/STOP**, **0 = GO**. On a KILL: delete, prove it by
listing, `--close-pod`. ONE re-creation is authorised; a third pod is a STOP.

## 3 — stage (~3 min, and the repo MUST be at this HEAD)

The packs pin the current parser and renderer shas, so a stale checkout is refused by the handshake
BEFORE the model is loaded. The repo has no remote; the transport is a git bundle.

**zsh does not word-split an unquoted variable holding ssh options.** Spell every flag literally.

```bash
SSHK=~/.runpod/ssh/runpodctl-ssh-key
git bundle create /tmp/market-pulse-lora-c.bundle HEAD
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -P <PORT> /tmp/market-pulse-lora-c.bundle root@<HOST>:/workspace/
```

```bash
ssh -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -p <PORT> root@<HOST>
# on the pod:
cd /workspace && rm -rf repo && git clone -q market-pulse-lora-c.bundle repo
cd repo && git rev-parse HEAD && git status --short      # equals the Mac's HEAD, empty
ls -d /workspace/venv /workspace/hf && du -sh /workspace/hf   # the volume is warm, or STOP
rm -rf /workspace/run                                    # the volume REMEMBERS a previous attempt
ls -d /workspace/run 2>&1 | tail -1                      # "No such file" — the proof, not the hope
```

If `/workspace/hf` is not there the weights are not on the volume, the boot is a 59 GB download and
this registration did not price one: delete and STOP. The `rm -rf /workspace/run` is not tidiness —
a replacement pod mounts the same volume, and an adapter directory left by a killed arm would be
mounted by `--adapter` as if this pod had trained it.

Everything the pod runs is IN the bundle: `scripts/pass1_v3_pod_runner.py`,
`scripts/pass2_lora_c_pod_runner.py` and `scripts/train_qlora_v3.py`, with their shas in
`results/prereg_lora_c.json::transport`. Each was driven against this line's frozen packs with a
fake client before the pod existed — the handshake and every per-item rendering sha.

## 4 — base v2 and base v3, ONE load, watched on the rate

```bash
export HF_HOME=/workspace/hf
PYTHONPATH=/workspace/repo/src /workspace/venv/bin/python -u \
  /workspace/repo/scripts/pass1_v3_pod_runner.py \
  --pack /workspace/repo/results/lora_c_eval_pack.json \
  --outdir /workspace/run/base --repo /workspace/repo 2>&1 | tee /workspace/run/base.log
```

Both legs, one model load — the boot is charged per load, not per leg. `-u` is not optional: the
rungs need a clock that can be watched go past.

From the Mac, in a second shell — **the scp comes FIRST, every time**, because the gates read the
file on THIS machine:

```bash
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -P <PORT> root@<HOST>:/workspace/run/base/lora_c_eval_v2.jsonl results/lora_c_base_v2.jsonl
PYTHONPATH=src python3.11 scripts/gate_lora_c.py --rate --leg base_v2 \
  --replies results/lora_c_base_v2.jsonl --started-at '<the first reply line's stamp>'
PYTHONPATH=src python3.11 scripts/gate_lora_c.py --liveness --last-event '<the last log line>'
```

**Rung 3 is the reason this leg is watched and lora-b's first leg was not.** Every charged second in
the plan was measured on a 4090; ruling (о) names a card this repo has never billed, and this
stack's own card-to-card spread on identical work is 1.65×. The rung extends the leg's REALISED
s/call over everything still to be bought and refuses a card that cannot pay for the plan — before
the second base leg, not after the smoke.

## 5 — the smoke: 6 optimizer steps, s/step AND the VRAM (rung 4)

```bash
PYTHONPATH=/workspace/repo/src /workspace/venv/bin/python -u \
  /workspace/repo/scripts/train_qlora_v3.py --class-weights --max-steps 6 \
  --data results/pass1_sft_v3_train.jsonl --out /workspace/run/smoke \
  2>&1 | tee /workspace/run/smoke.log
```

```bash
scp ... root@<HOST>:/workspace/run/smoke/loss.jsonl results/lora_c_smoke_loss.jsonl
PYTHONPATH=src python3.11 scripts/gate_lora_c.py --smoke --loss results/lora_c_smoke_loss.jsonl
```

This buys **the only s/step this line may use** — no reading exists at 3 072 and neither lora-b
reading is one. **An OOM here is a KILL and a STOP, with no branch:** `micro_batch_size` is frozen
law in `config/qlora.yaml` and is NOT edited on a pod. 32 GB against the 48 GB every prior reading
of this stack was taken on is exactly why ruling (о) makes the smoke the VRAM test. Pass `--oom`
to record it.

## 6 — the projection rung, after the smoke and after EVERY leg (rung 5)

```bash
python3.11 scripts/runpod_guard.py --step lora-c --step-cap 4.00 --until <ISO> \
  --note "lora-c smoke measured"
PYTHONPATH=src python3.11 scripts/gate_lora_c.py --projection --after smoke --reading <the guard's USD>
```

`--after` is one of `base_v2 · base_v3 · smoke · arm_a · eval_a · arm_b · eval_b · marker_census`,
and the remainder after each is derived from the registration's own leg table. A KILL here is
compliance: pull the artifacts, prove the teardown by listing, STOP with the ledger.

## 7 — arm A, then its eval; then arm B, then its eval

```bash
# on the pod — the arm:
PYTHONPATH=/workspace/repo/src /workspace/venv/bin/python -u \
  /workspace/repo/scripts/train_qlora_v3.py --class-weights \
  --data results/pass1_sft_v3_train.jsonl --out /workspace/run/arm_a \
  2>&1 | tee /workspace/run/arm_a.log
# and its eval — the v3 leg only, with the adapter it just trained:
PYTHONPATH=/workspace/repo/src /workspace/venv/bin/python -u \
  /workspace/repo/scripts/pass1_v3_pod_runner.py \
  --pack /workspace/repo/results/lora_c_eval_pack.json --only v3 \
  --outdir /workspace/run/eval_a --repo /workspace/repo \
  --adapter /workspace/run/arm_a/adapter 2>&1 | tee /workspace/run/eval_a.log
```

**The attempt is SPENT at the first reply this eval generates.** Arm B is the same two commands with
`--data results/pass1_sft_v3_arm_b.jsonl`, `--out /workspace/run/arm_b` and
`--outdir /workspace/run/eval_b`. `--liveness` at every log line; `--projection` after each.

Pass 2 per arm, rebuilt on the Mac from THAT arm's out-file and copied back:

```bash
# the arm's eval replies come back first — the pack is rebuilt from THEM, on the Mac:
scp ... root@<HOST>:/workspace/run/eval_a/lora_c_eval_v3.jsonl results/lora_c_eval_arm_a.jsonl
PYTHONPATH=src python3.11 scripts/build_lora_c_pass2_pack.py --leg arm_a \
  --out-file results/lora_c_eval_arm_a.jsonl --out results/lora_c_pass2_arm_a.json
scp ... results/lora_c_pass2_arm_a.json root@<HOST>:/workspace/
PYTHONPATH=/workspace/repo/src /workspace/venv/bin/python -u \
  /workspace/repo/scripts/pass2_lora_c_pod_runner.py \
  --pack /workspace/lora_c_pass2_arm_a.json --outdir /workspace/run/pass2_a \
  --repo /workspace/repo 2>&1 | tee /workspace/run/pass2_a.log
```

**`--out` is REQUIRED here and the builder refuses without it:** its default is
`results/lora_c_pass2_pack.json`, which the registration pins and the create freezes. This rebuild
happens while a pod is billing, and the frozen path is one keystroke away.

**The runner is `pass2_lora_c_pod_runner.py`, not the r2 one.** r2's renders through
`pass2.pass2_messages_gm4` at 12 000 characters while this line's pack declares — and renders at —
r2's own 15 569. One reference thread, `@matusi_ukr:22272`, reaches 12 399 in the worst case and it
is a FLAGSHIP thread of bar 1, so it cannot be dropped. The bound is in the pack:
`ceiling_reachability`.

**The thread count is a READING, not the charged 11.** An adapter marks more or fewer rows `OURS`
than base v2 did; the reachable maximum is 15. The money block carries what that costs
(`the_pass_2_thread_count_is_a_READING_of_the_arms_labels`) and the projection rung sees it.

Ruling (н): pass 2 runs for the two ARMS only. Base v2's end-to-end BEFORE column is
`pass2-signals-r2`'s registered 4/5 · 2 signals and is not re-bought; base v3 takes no bar.

## 8 — the marker census (report-only, ~$0.05, LAST)

```bash
PYTHONPATH=/workspace/repo/src /workspace/venv/bin/python -u \
  /workspace/repo/scripts/pass1_v3_pod_runner.py \
  --pack /workspace/repo/results/lora_c_marker_census_pack.json --only marker_census \
  --outdir /workspace/run/marker --repo /workspace/repo \
  --adapter /workspace/run/arm_b/adapter 2>&1 | tee /workspace/run/marker.log
```

Forty requests — twenty E units, each answered twice by arm B's adapter, differing in the header
alone. It is answered AFTER both bars are scored and it is never a bar. A projection rung that
cannot afford it drops it and loses a report-only table.

## 9 — scp EVERYTHING, before any verdict

```bash
ssh ... -p <PORT> root@<HOST> 'cd /workspace/run && find . -type f | sort | xargs shasum -a 256'
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -P <PORT> -r root@<HOST>:/workspace/run results/lora_c_run_artifacts
```

Per-row raw replies, both adapters with their hashes, both loss logs, every pod log. The hashes are
taken ON THE POD and again on the Mac: an adapter that arrived truncated would otherwise be
discovered by a verdict that scored it. **No verdict is computed before this step completes**, and
nothing is deleted before it does ([[fetch_before_you_delete]]).

## 10 — delete, and prove it

```bash
runpodctl pod delete <POD_ID>
runpodctl pod list -a                # []
runpodctl serverless list            # [] — nothing was ever created here
runpodctl network-volume list        # the volume, unchanged: the POSITIVE CONTROL
PYTHONPATH=src python3.11 scripts/gate_lora_c.py --close-pod \
  --deleted-at '<UTC ISO8601>' --outcome '<why this pod ended>'
python3.11 scripts/runpod_guard.py --step lora-c --step-cap 4.00 \
  --note "lora-c pod deleted; <what was trained and evaluated>"
```

Three listings, and the volume has to be in the last one: a listing that returns `[]` for everything
proves the command runs, not that the pod is gone. Volume rent is named separately — it is beside
the run and never inside it.

## 11 — D3, on the Mac ($0)

The verdict is the scorer's, never the eyeball, and it is ONE attempt: no retry, no second draw, no
tuning after any eval output is seen.

```bash
make check-stamped
python3.11 scripts/runpod_guard.py --step lora-c --step-cap 4.00 --close \
  --until <the last session's `at`> --tolerance 0.07 --note "lora-c settled"
```

The walk posts hours late; `--close` over an unanswered walk is refused by the guard and must be —
a lower bound goes in the report as a named debt instead.
