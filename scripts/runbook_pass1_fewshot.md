# Runbook — pass1-fewshot D1: two dev legs, one dev gate, one shot, and a loop you do not leave

The order below is the money. `results/prereg_pass1_fewshot.json` is the law; every deadline here
comes out of it through `scripts/gate_pass1_fewshot.py`, and **nothing in this file may add a number
the record does not carry**. Where a number appears below it is an illustration of the instrument's
output, never a value to type.

**The one rule this runbook exists for:** the meter starts at `pod create` and stops at
`pod delete`. Not at ssh, not at the model load, not at the first reply — a pod bills for existing.
`pod stop` does NOT stop it. **Delete, never stop.**

**The second rule, and it is new: you do not poll by hand.** `--watch` is a BLOCKING loop. It copies
the out-files and the pod log back, it runs the projection gate on EVERY poll (the registration's «every 20 calls» is the floor), and it
KILLS — deletes the pod, records the gate — when no new row and no new log line have appeared for
600 s, measured from the LAST EVENT. lora-b's arm A finished at 14:38Z and was found at 17:20Z:
9 720 s of billed idle, $1.43, and the arm that never ran. Every rung of that registration read the
training log, so all of them went quiet together. **Start the watch and stay in it.**

**One attempt.** The bar is `gold14(v2) ≥ 12/14` on the sealed gold r2. The attempt is SPENT at the
first GOLD-row reply generated — not at create, not at a dev reply, not at the dev gate. A RED dev
gate closes the session with the attempt NOT spent, and the dev table goes back to the team lead.

**Guard reading at every rung, pasted:**

```bash
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-fewshot --step-cap 1.50 \
  --note "<what this rung is>"
```

## 0 — before anything exists ($0)

```bash
runpodctl pod list -a && runpodctl serverless list && runpodctl network-volume list
git status --porcelain                       # the prereg must NOT be in it
PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --pre-create-check
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-fewshot --step-cap 1.50 \
  --note "pass1-fewshot anchor, before the pod"
```

The three listings are the before-state the deletion proof is read against — the volume must appear
in all three readings, before and after, as the positive control that the listing works at all.
`gate_pass1_fewshot.py` refuses to run at all while `results/prereg_pass1_fewshot.json` is untracked
or differs from HEAD: the git clock is what proves the plan predates the money.

## 1 — create (the meter starts here)

This line does NOT train, so it does not need 48 GB. probe-b served this same base on a 24 GB RTX
4090 at $0.74/h, which is the card and the class the 5.162 s/call sample was measured on. An A6000
under the ceiling is allowed. The volume pins EU-RO-1.

```bash
runpodctl pod create --name mp-pass1-fewshot --gpu-id 'NVIDIA GeForce RTX 4090' --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after '<create + the seconds --pre-create-check left>'
```

**Rung 1 is `costPerHr` in the create RESPONSE, not the price on a listing page.** Over $0.80/h →
delete now and STOP, no generation of any kind. Under it, record the pod:

```bash
PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --price \
  --pod-id <ID> --created-at <the create response's stamp> \
  --usd-per-hour <costPerHr> --card '<the card the response gave>' \
  --terminate-after '<the stamp you actually gave pod create>'
```

`--terminate-after` is the one number this runbook makes you say twice, because the platform flag is
the only thing that enforces rung 6. `--price` re-derives it and REFUSES a window longer than the
cumulative hard stop allows.

## 2 — rung 2, the ssh dead-man (≤ 180 s of this pod's create-elapsed)

`runpodctl ssh info` answers `{"error": "pod not ready"}` until the port mapping is published and
then a JSON object carrying `"ip"` and `"port"`. **Poll on `"port"`, and BOUND the loop below the
dead-man**, so a poller that is looking for the wrong thing cannot spend the deadline being blind:

```bash
runpodctl ssh info <POD_ID>          # "pod not ready" for a minute or two is normal
for i in $(seq 1 34); do            # 34 x 5 s = 170 s, inside the 180 s rung
  runpodctl ssh info <POD_ID> | grep -q '"port"' && break
  sleep 5
done
runpodctl ssh info <POD_ID>          # the reading the next command asserts
PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --gate0 --ssh-ok   # it answered
```

**`--gate0` without `--ssh-ok` asserts that the endpoint has NOT answered.** Run it as a poll only
while you are inside the deadline; past 180 s it is a KILL, and it is a KILL whether the endpoint is
up or not, because what the gate records is the reading you gave it. On 2026-08-20 this cost a pod:
the loop grepped `"host"`, a key `runpodctl` never emits, spun for 240 s, and the `--gate0` after it
recorded a dead-man nobody could prove either way ([[a_checker_whose_failure_is_silence]]).

## 3 — stage, and launch BOTH dev legs in one process

The packs pin the CURRENT parser sha, so the handshake refuses a stale checkout by design. The repo
has no remote; the transport is a git bundle.

**zsh does not word-split an unquoted variable holding ssh options.** Spell every flag literally.

```bash
SSHK=~/.runpod/ssh/runpodctl-ssh-key
git bundle create /tmp/market-pulse-pass1-fewshot.bundle HEAD
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> /tmp/market-pulse-pass1-fewshot.bundle \
  scripts/pass1_fewshot_pod_runner.py scripts/pass1_pod_runner.py \
  scripts/reader_v5_pod_runner.py scripts/reader_v4_pod_runner.py \
  root@<HOST>:/workspace/
```

```bash
ssh -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -p <PORT> root@<HOST>
# on the pod:
cd /workspace && rm -rf repo && git clone -q market-pulse-pass1-fewshot.bundle repo
cd repo && git rev-parse HEAD && git status --short      # equals the Mac's HEAD, empty
ls -d /workspace/venv /workspace/hf && du -sh /workspace/hf   # the volume is warm, or STOP
rm -rf /workspace/run && mkdir -p /workspace/run         # the volume REMEMBERS a previous attempt
ls /workspace/run                                        # empty — the proof, not the hope
```

If `/workspace/hf` is not there the weights are not on the volume, the boot is a 59 GB download and
this registration priced no such thing: delete and STOP. The `rm -rf /workspace/run` is not
tidiness — a replacement pod mounts the same network volume, and an out-file left by a killed leg
would be RESUMED over, so the run would answer fewer units and look complete.

The launch is DETACHED and its stdout is the pod log the watch loop tails:

```bash
ssh ... -p <PORT> root@<HOST> \
  'cd /workspace && HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src nohup \
   /workspace/venv/bin/python -u /workspace/repo/scripts/pass1_fewshot_pod_runner.py \
     --pack /workspace/repo/results/pass1_dev_pack.json \
     --outdir /workspace/run --repo /workspace/repo \
     > /workspace/run/pod.log 2>&1 & echo $!'
```

**Both dev legs, one invocation, one model load.** The base leg runs first and the v2 leg second;
each answers into its own file (`pass1_dev_base.jsonl`, `pass1_dev_v2.jsonl`) because the shipped
resume skips every id it already sees. The 59 GB of weights are loaded once — a second invocation
would pay the boot twice, and the boot is 350 s of a 5 326 s budget.

## 4 — the WATCH, entered IMMEDIATELY (rungs 3, 4, 5 and 6), and not left

```bash
PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --watch \
  --pack results/pass1_dev_pack.json --ssh root@<HOST> --ssh-port <PORT>
```

**Enter it the moment the launch returns a pid — do not hand-poll `--boot` first.** Polling a gate
by hand through a 350 s model load is the habit rung 5 was bought to remove, and the loop arms rung
3 itself: not one reply at 450 s of this pod's create-elapsed is a KILL it makes. The runner's own
progress lines land in the log before the load starts, so the silent `load_captioner` window sits
comfortably inside the 600 s liveness deadline.

The watch prints one line per poll and returns only on GO (every unit answered) or KILL. On KILL it
has ALREADY deleted the pod — go to step 7 and prove it by listing. If the loop ends any other way
it records a gate and prints the pod id with the delete command: run it immediately, because at that
moment nothing is watching a billed pod except the platform backstop.

Once the watch returns GO, record rung 3 with the reply the run actually produced — it is the gate
whose reading the report quotes, and the boot it measures is the number the next contract prices:

```bash
PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --boot \
  --first-reply-at <create + the first row's boot_seconds, off results/pass1_dev_base.jsonl>
```

## 5 — rung 7, the dev gate (on the Mac, $0)

```bash
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/pod.log results/pass1_fewshot_pod.log
PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --dev-gate
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-fewshot --step-cap 1.50 \
  --note "dev legs answered, before the shot"
```

* **GO** — both inequalities hold. The shot may be fired, and step 6 is the first gold row.
* **RED** — the line closes here. Delete, prove it by listing, `--close`. **The attempt is NOT
  spent**: no gold row was answered. Nothing iterates in-session.
* **STOP** — the base already answers more than 39 of the 49 «our» rows, so a +10 delta cannot exist
  for any v2. Same close, and the reading goes to the operator with the table.

## 6 — the shot (GO only). The attempt is SPENT at the first gold-row reply

```bash
ssh ... -p <PORT> root@<HOST> \
  'cd /workspace && HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src nohup \
   /workspace/venv/bin/python -u /workspace/repo/scripts/pass1_fewshot_pod_runner.py \
     --pack /workspace/repo/results/pass1_probe_b_pack_v2.json \
     --outdir /workspace/run --repo /workspace/repo \
     >> /workspace/run/pod.log 2>&1 & echo $!'

PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --watch \
  --pack results/pass1_probe_b_pack_v2.json --ssh root@<HOST> --ssh-port <PORT>
```

The shot's watch does NOT re-arm rung 3 — the model is already loaded and the ceiling is anchored on
create — so a stalled shot dies on the liveness rung, which is the right rung for it.

Its own out-file (`pass1_fewshot_shot.jsonl`), never a dev leg's — the pack names it and the runner
obeys the pack.

## 7 — scp EVERYTHING, then delete, then prove it

```bash
ssh ... -p <PORT> root@<HOST> 'cd /workspace/run && find . -type f | sort | xargs shasum -a 256'
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:'/workspace/run/*' results/
shasum -a 256 results/pass1_dev_base.jsonl results/pass1_dev_v2.jsonl \
  results/pass1_fewshot_shot.jsonl results/pass1_fewshot_pod.log   # against the pod's listing

runpodctl pod delete <POD_ID>
runpodctl pod list -a                # []
runpodctl serverless list            # [] — nothing was ever created here
runpodctl network-volume list        # the volume, unchanged: the POSITIVE CONTROL

PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --close \
  --deleted-at <the deletion stamp> --outcome '<why this pod ended>'
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-fewshot --step-cap 1.50 \
  --note "pod deleted, the step is closed"
```

**Files come back BEFORE the verdict and before the deletion.** Every hash is compared on the pod
and on the Mac; a file that only ever existed on the pod is evidence nobody can re-score.

## 8 — D2, the verdict ($0, after the last append to the run record)

```bash
PYTHONPATH=src python3.11 scripts/score_pass1_fewshot.py
```

It REFUSES while the run record says a shot happened and its replies are not on this machine.

## Recovery — ONE re-creation, and never two endpoints

Only after a deletion PROVEN by listing, and only if the guard reading plus the worst case remaining
at MEASURED rates is inside the cap and the cumulative stop. Every reply already on disk is kept: the
shipped resume re-asks only what has no answer, so a KILL mid-leg costs the boot and not the leg.

```bash
PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --pre-create-check   # then step 1 again
```

## DO NOT

* No training, no adapter, no second prompt variant, no tuning after any eval output.
* Never edit `results/prereg_pass1_probe_b.json`, `results/pass1_probe_b_pack.json`, the gold, the
  labels or the base verdict. The base is NOT re-run on the fourteen.
* Never touch the sealed fourteen before the dev gate says GO.
* Never leave `--watch` while a pod is billing.
* Never two billing endpoints; delete, never stop; no cap raise.
