# Runbook — reader-topup: 132 units on a pod, and the training set gets its context

The order below is the money. `results/reader_topup_prereg.json` is the law; every deadline here
comes out of it and nothing in this file may add a number the record does not carry.

**The one rule this runbook exists for:** the meter starts at `pod create` and stops at
`pod delete`. Not at ssh, not at the model load, not at the first job — a pod bills for existing.
`pod stop` does NOT stop it. **Delete, never stop.**

Cap **$2.00** = 9 729.7 s of pod at $0.74/h, of which **9 669.7 s** are usable (60 s held back so
the deletion itself is inside the cap). The generation projection is **6 049 s** over 132 units, so
the cap fits it 1.40× even after a 1 200 s boot, and 1.28× at the $0.80/h ceiling.

**What this buys:** 559 of the 650 pass-1 training rows get a bought topic instead of a cut post
fragment, and the entity block is expected to reach ~279 of 650 against 39 today. The numbers and
their error bars are in `results/reader_topup_projection.json`; the ruling is the operator's
«выполни ветку B» of 2026-08-19.

## 0 — before anything exists ($0)

```bash
runpodctl pod list -a && runpodctl serverless list && runpodctl network-volume list
PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --pack
python3.11 scripts/runpod_guard.py --step reader-topup --step-cap 2.00 \
  --note "reader-topup anchor, before the pod"
git add results/spend_reader_topup.json results/reader_topup_pack.json && git commit
PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --pre-create-check
```

The three listings are the before-state the deletion proof is read against — the volume must appear
in all three readings, before and after, as the positive control that the listing works at all.
`--pre-create-check` is the never-two-pods rule, and it runs BEFORE the create rather than as a
refusal after the second meter has started.

## 1 — create (the meter starts here)

`--terminate-after` is 3 hours out: a runaway backstop, NOT a cap guard (3 h = $2.22 at the worked
example, over the cap). What guards the cap is gate 2 in §4.

```bash
runpodctl pod create --name mp-reader-topup --gpu-id 'NVIDIA GeForce RTX 4090' --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after '<UTC ISO8601, create + 3 h>'
```

**Read `costPerHr` and the card back out of the response and stamp the clock immediately:**

```bash
PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --open \
  --pod-id <POD_ID> --created-at '<the create response's stamp, UTC ISO8601>' \
  --usd-per-hour <costPerHr> --card '<the card the response names>'
```

A `costPerHr` above **$0.80/h** deletes the pod and STOPS — no generation. Between $0.74 and $0.80
the run continues and every deadline is recomputed from the rate actually charged, which is what
`--open` prints.

## 2 — gate 0, the ssh dead-man (≤ 180 s of this segment's create-elapsed)

```bash
runpodctl ssh info <POD_ID>          # "pod not ready" for a minute or two is normal
PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --gate0            # WAIT / KILL
PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --gate0 --ssh-ok   # it answered
```

On a KILL: delete, prove it by listing, `--close-segment`, then `--pre-create-check` before the
replacement. At most two recreates; a third dead pod is a datacenter state and a STOP.

## 3 — stage (~3 min, and the repo MUST be at this HEAD)

`src/market_pulse/prompts.py` has moved since the volume's `repo/` was last written, and the pack
pins the CURRENT parser sha — so the handshake refuses a stale checkout by design. The repo has no
remote; the transport is a git bundle, the same one `scripts/runbook_srv2b.md` §staging uses.

**zsh does not word-split an unquoted variable holding ssh options.** Spell every flag literally.

```bash
SSHK=~/.runpod/ssh/runpodctl-ssh-key
git bundle create /tmp/market-pulse-topup.bundle HEAD
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -P <PORT> /tmp/market-pulse-topup.bundle results/reader_topup_pack.json \
    scripts/reader_v5_pod_runner.py root@<HOST>:/workspace/
```

The runner lands in `/workspace/`, **never inside `/workspace/repo/`**: the checkout stays clean and
`git status --short` on the pod is still the proof that it does.

```bash
ssh -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -p <PORT> root@<HOST>
# on the pod:
cd /workspace && rm -rf repo && git clone -q market-pulse-topup.bundle repo
cd repo && git rev-parse HEAD && git status --short      # equals the Mac's HEAD, empty
ls -d /workspace/venv /workspace/hf && du -sh /workspace/hf   # the volume is warm, or STOP
```

If `/workspace/hf` is not there the weights are not on the volume, the boot is a 59 GB download,
and this registration did not price one: delete and STOP.

## 4 — generate, watched

```bash
export HF_HOME=/workspace/hf
/workspace/venv/bin/python -u /workspace/reader_v5_pod_runner.py \
  --pack /workspace/reader_topup_pack.json --out /workspace/reader_topup_pod.jsonl \
  --repo /workspace/repo 2>&1 | tee /workspace/reader_topup_pod.log
```

`-u` is not optional: the kill rule needs a clock that can be watched go past. The instrument checks
run BEFORE the load and `READY` names the boot in seconds.

From the Mac, in a second shell. **The scp comes FIRST, every single time** — `--gate` reads the
file on THIS machine and the pod writes to its own.

```bash
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -P <PORT> root@<HOST>:/workspace/reader_topup_pod.jsonl results/reader_topup_pod.jsonl 2>/dev/null
PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --gate \
  --generation-started-at '<UTC ISO8601 of the launch above>'
```

Exit codes ARE the rule: **3 = WAIT** (no reply yet, still inside the deadline), **2 = KILL/STOP**,
**0 = GO**. The first reply must land by generation + 720 s; affordability sits at create + 3 621 s
and is the looser of the two on this registration, which is why the twelve-minute ceiling binds.

After the first reply the same pair projects the full pass BOTH ways and the pessimistic one binds:
`elapsed + max(unread units ÷ read, unread payable ÷ read payable) × measured ≤ usable`. Re-run it
as replies land — it costs nothing and it is what deletes the pod before the cap rather than after.
The units are ordered **expensive first**, so the early seconds-per-unit is the worst this run will
see and the projection it feeds is pessimistic by construction.

**A wall-clock alarm at create + 2 h 40 min** (9 669.7 s). If the polling stops, the only thing left
is `--terminate-after` at 3 h.

Bring the log back too, and always before a kill:

```bash
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    -P <PORT> root@<HOST>:/workspace/reader_topup_pod.log results/reader_topup_pod.log
```

## 5 — delete, and prove it

```bash
runpodctl pod delete <POD_ID>
runpodctl pod list -a                # []
runpodctl serverless list            # [] — nothing was ever created here
runpodctl network-volume list        # the volume, unchanged: the positive control
PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --close-segment \
  --deleted-at '<UTC ISO8601>' --outcome '<why this segment ended>'
python3.11 scripts/runpod_guard.py --step reader-topup --step-cap 2.00 \
  --note "reader-topup pod deleted; <n> of 132 units read"
```

Three listings, and the volume has to be in the last one: a listing that returns `[]` for everything
proves the command runs, not that the pod is gone.

## 6 — ingest and rebuild, on the Mac ($0)

```bash
PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --normalize \
  --raw results/reader_topup_pod.jsonl        # drop a torn last line BEFORE the ingest
PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --ingest
PYTHONPATH=src python3.11 scripts/build_pass1_sft.py --census   # the context census, after
PYTHONPATH=src python3.11 scripts/build_pass1_sft.py
PYTHONPATH=src python3.11 scripts/write_lora_b_prereg.py
make check
python3.11 scripts/runpod_guard.py --step reader-topup --step-cap 2.00 --close \
  --until <the last session's `at`> --tolerance 0.07 --note "reader-topup settled"
```

`build_pass1_sft` reads whatever verdicts exist, so a partial pass is a partial improvement and
never a broken dataset. The walk posts hours late; `--close` over an unanswered walk is refused by
the guard and must be — a lower bound goes in the report as a named debt instead.
