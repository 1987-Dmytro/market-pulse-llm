# Runbook — reader-topup: 132 units on a pod, and the training set gets its context

The order below is the money. `results/reader_topup_prereg.json` is the law; every deadline here
comes out of it and nothing in this file may add a number the record does not carry.

**The one rule this runbook exists for:** the meter starts at `pod create` and stops at
`pod delete`. Not at ssh, not at the model load, not at the first job — a pod bills for existing.
`pod stop` does NOT stop it. **Delete, never stop.**

**Segment 3 — the last the recovery clause allows, and it runs under ATTEMPT B's registration**
(`results/reader_topup_prereg_b.json`). Segments 1 and 2 billed **485.0 s = $0.099695**, so the cap
this segment is measured against is the REMAINDER: $1.900305, which buys **9 184.7 s** usable at
$0.74/h and **8 491.4 s** at the $0.80/h ceiling (cap ÷ rate × 3600, less the 60 s the deletion
itself is held back for). The generation projection is 6 049 s over 132 units, so the remainder
still fits it with ~2 836 s of slack after a 300 s boot.

**The out-file starts EMPTY, on both machines.** Segment 2's single reply is archived as
`results/reader_topup_pod_segment2.jsonl` and the pod's own
`/workspace/reader_topup_pod.jsonl` is deleted before the launch. This is not tidiness: `--gate`
takes its BOOT-KILL branch only while the raw file is empty (`read_threads_reader_v5b.py`:
`if args.deadlines or (args.gate and not rows)`), so one inherited row from a pod that no longer
exists would make the 720 s boot kill unreachable for the whole segment — and would dilute the
calibration that IS attempt B's cap guard with a measurement this pod never made. The price of
starting clean is re-asking one unit: ~80 s, about $0.016.

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
  --ports '22/tcp' --ssh --terminate-after '<UTC ISO8601, create + 2 h 45 min>'
```

2 h 45 min and not 3 h: the backstop has to sit just above the 9 184.7 s this segment can afford,
not above the full cap the first attempt was written for. It is still not a cap guard — at the
worked example it is $2.04 — it is what deletes the pod if this Mac dies with the run open.

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
rm -f /workspace/reader_topup_pod.jsonl                  # the volume REMEMBERS the last segment
ls -l /workspace/reader_topup_pod.jsonl 2>&1 | tail -1   # "No such file" — the proof, not the hope
```

The `rm` is the pod half of «the out-file starts empty». `/workspace` is the network volume, so a
replacement pod mounts the previous segment's replies and `reader_v5_pod_runner.already_answered`
would resume over them — which is the right behaviour for a resume and the wrong one for a segment
whose kill rule has to be able to fire.

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
**0 = GO**. The first reply must land by generation + 720 s; affordability sits at create + 3 135.8 s
on the REMAINING cap and is the looser of the two, which is why the twelve-minute ceiling binds.

`--gate` reaches the boot-kill branch only while no reply has landed, which is exactly why §3 empties
the out-file on both machines. Until the first reply, `--deadlines` prints the same clock without
depending on that.

After the first reply the gate is ATTEMPT B's — each unread unit projected at its own size, and the
sum calibrated by what this pod has actually done:
`elapsed + max(measured ÷ fitted(read), 1.0) × Σ fitted(unread) ≤ usable`. Attempt A's two legs are
still printed beside it and neither binds. Re-run it as replies land — it costs nothing and it is
what deletes the pod before the cap rather than after.

**Two named risks, from the review that preceded this segment.** The calibration is a single ratio,
so at n=1 it decides all 132 units from one reading: a first unit at ≥1.47× its fit STOPs a run that
would fit, and 2 of the 26 units the line was fitted on are that slow (1 of 9 among units of ≥10
payable). The counter-evidence is direct — this pack's first unit was measured at 77.5 s on a real
pod, 0.96× its fit. And the calibration is multiplicative, so it under-projects a per-unit ADDITIVE
slowdown; the cap, not the gate, is what bounds that case.

**A wall-clock alarm at create + 2 h 33 min** (9 184.7 s — the REMAINING cap at $0.74/h; 2 h 21 min
if the create response prices the card at the $0.80/h ceiling). If the polling stops, the only thing
left is `--terminate-after` at 2 h 45 min.

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
