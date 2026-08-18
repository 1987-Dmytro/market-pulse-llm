# Runbook — reader-v4: 23 threads on a pod, with the boot in plain sight

The order below is the money. `results/prereg_reader_probe_v4.json` is the law; every deadline here
comes out of it and nothing in this file may add a number the record does not carry.

**The one rule this runbook exists for:** the meter starts at `pod create` and stops at
`pod delete`. Not at ssh, not at the model load, not at the first job — a pod bills for existing.
`pod stop` does NOT stop it: a stopped pod keeps billing its disk. **Delete, never stop.**

Cap $0.35 = **1 702.7 s** of pod at $0.74/h, of which **1 642.7 s** are usable (60 s held back so
the deletion itself is inside the cap).

## 0 — before anything exists ($0)

```bash
runpodctl pod list -a && runpodctl serverless list && runpodctl network-volume list
PYTHONPATH=src python3.11 scripts/read_threads_reader_v4.py --pack results/reader_v4_pack.json
python3.11 scripts/runpod_guard.py --step reader-v4 --step-cap 0.35 --note "reader-v4 anchor, before the pod"
git add results/spend_reader_v4.json results/reader_v4_pack.json && git commit
```

The three listings are the before-state the deletion proof is read against — the volume must appear
in all three readings, before and after, as the positive control that the listing works at all.

## 1 — create (the meter starts here)

`--terminate-after` is 90 minutes out: a runaway backstop, NOT a cap guard (90 min = $1.11, three
caps). What guards the cap is the gate in §3.

```bash
runpodctl pod create --name mp-reader-v4 --gpu-id 'NVIDIA GeForce RTX 4090' --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after '<UTC ISO8601, create + 90 min>'
```

**Read `costPerHr` and the card back out of the response and stamp the clock immediately:**

```bash
PYTHONPATH=src python3.11 scripts/read_threads_reader_v4.py --open \
  --pod-id <POD_ID> --created-at '<the create response's stamp, UTC ISO8601>' \
  --usd-per-hour <costPerHr> --card '<the card the response names>'
```

A `costPerHr` above $0.74 re-prices every deadline; a projection that no longer fits deletes the pod
and STOPS. A card other than the 4090 also ends the paired seconds comparison with probe-b.

## 2 — stage ($0 expected, ~2 min)

The volume already carries `repo/` at `aa0ca18` and `src/` has not moved since, so nothing is
re-staged: the runner VERIFIES and refuses. `HF_HOME=/workspace/hf` holds the weights.

**zsh does not word-split an unquoted variable holding ssh options.** Spell every flag literally —
a `$SSHOPT` that works in bash cost reader-v3 five minutes of billed pod and ≈$0.02 (Dv442).

```bash
runpodctl ssh info <POD_ID>          # "pod not ready" for a minute or two is normal
scp -i ~/.runpod/ssh/runpodctl-ssh-key -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -P <PORT> \
    results/reader_v4_pack.json scripts/reader_v4_pod_runner.py root@<HOST>:/workspace/
```

The runner lands in `/workspace/`, **never inside `/workspace/repo/`**: the checkout stays clean and
`git status --short` on the pod is still the proof that it does.

## 3 — generate, watched

```bash
ssh -i ~/.runpod/ssh/runpodctl-ssh-key -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -p <PORT> root@<HOST>
# on the pod:
cd /workspace/repo && git rev-parse HEAD && git status --short      # aa0ca18, clean
export HF_HOME=/workspace/hf
/workspace/venv/bin/python -u /workspace/reader_v4_pod_runner.py \
  --pack /workspace/reader_v4_pack.json --out /workspace/reader_v4_pod.jsonl \
  --repo /workspace/repo 2>&1 | tee /workspace/reader_v4_pod.log
```

`-u` is not optional: the kill rule needs a clock that can be watched go past. Every line carries
seconds since the process started, the instrument checks run BEFORE the load, and `READY` names the
boot in seconds.

From the Mac, in a second shell, stamp the generation's start and then poll. **The scp comes FIRST,
every single time** — `--gate` reads `results/reader_v4_pod.jsonl` on THIS machine and the pod
writes to its own. A gate run against a file nobody refreshed reports «no reply has landed» when one
has, kills a healthy run, and writes that reason into the run record. The `read_from` block in the
output names the file and the moment it was copied back, so a stale reading is visible in the
artefact; do not let it get there.

```bash
scp -i ~/.runpod/ssh/runpodctl-ssh-key -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -P <PORT> \
    root@<HOST>:/workspace/reader_v4_pod.jsonl results/reader_v4_pod.jsonl 2>/dev/null
PYTHONPATH=src python3.11 scripts/read_threads_reader_v4.py --gate \
  --generation-started-at '<UTC ISO8601 of the launch above>'
```

Exit codes ARE the rule: **3 = WAIT** (no reply yet, still inside the deadline), **2 = KILL/STOP**,
**0 = GO**. The deadline printed is `min(generation start + 720 s, 915.0 s since create)` and both
numbers are in the output. On a 2, go straight to §5.

## 4 — the rest of the pass

After the first reply the same pair of commands projects the full pass from what has been measured,
BOTH ways, and the pessimistic one binds:
`elapsed + max(unread threads ÷ read, unread payable ÷ read payable) × measured ≤ 1 642.7`. Re-run
it as replies land — it costs nothing and it is what deletes the pod before the cap rather than
after. The log comes back too, and always before a kill:

```bash
scp -i ~/.runpod/ssh/runpodctl-ssh-key -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -P <PORT> \
    root@<HOST>:/workspace/reader_v4_pod.log results/reader_v4_pod.log
```

**A wall-clock alarm at create + 27 minutes** (1 642.7 s). If the polling stops, the only thing left
is `--terminate-after` at 90 min, which is three caps.

## 5 — delete, and prove it

```bash
runpodctl pod delete <POD_ID>
runpodctl pod list -a                # []
runpodctl serverless list            # [] — nothing was ever created here
runpodctl network-volume list        # the volume, unchanged: the positive control
python3.11 scripts/runpod_guard.py --step reader-v4 --step-cap 0.35 --note "reader-v4 pod deleted"
```

Three listings, and the volume has to be in the last one: a listing that returns `[]` for everything
proves the command runs, not that the pod is gone.

## 6 — score, on the Mac

```bash
PYTHONPATH=src python3.11 scripts/read_threads_reader_v4.py --ingest
PYTHONPATH=src python3.11 scripts/score_reader_v4.py
python3.11 scripts/runpod_guard.py --step reader-v4 --step-cap 0.35 --close \
  --until <the last session's `at`> --tolerance 0.07 \
  --note "reader-v4 settled"          # only once the billing walk answers
```

The walk posts hours late. `--close` over an unanswered walk is refused by the guard and must be —
a lower bound goes in the report as a named debt instead.

---

## Corrections carried forward — 2026-08-17, at the acceptance of reader-v4

This file is the order that WAS followed; `docs/reports/reader-v4.md` holds the transcript of the
session that followed it, unedited. Two things are corrected here so the next runbook inherits them
instead of rediscovering them, and both were paid for.

**1 — a detached launch must not hold the ssh channel (Dv454).** §3 above runs the generation inside
an interactive ssh session and that is what worked. The trap is the shortcut that looks equivalent:
`ssh … "nohup … &"` STILL holds the channel and times out at two minutes although the runner has
already started, which is what happened and cost a confused minute of billed pod. If the launch is
detached, detach it completely and verify it separately:

```bash
ssh <OPTS> -p <PORT> root@<HOST> \
  'cd /workspace && nohup /workspace/venv/bin/python -u /workspace/<runner>.py … \
     </dev/null >/workspace/<run>.log 2>&1 & echo launched $!'
ssh <OPTS> -p <PORT> root@<HOST> 'pgrep -af <runner>.py'    # the check, not the launch, proves it
```

`</dev/null` and the redirection of BOTH streams are what free the channel; `ssh -f` is the other
spelling. And never let a `pgrep -f` pattern match the shell that runs it
([[a_remote_job_outlives_its_watcher]]).

**2 — every verify command names `python3.11` explicitly.** The eight call sites above were rewritten
from bare `python3` on this date. The team lead's own re-run of the scorer failed on a system
`python3` that is 3.9 and reproduced byte-identically on 3.11 — a runbook whose commands only work
on the author's PATH is a runbook nobody else can verify with.
