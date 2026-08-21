# Runbook — pass1-fewshot r2 D1: two dev legs, one dev gate, one shot, and a loop you do not leave

The order below is the money. `results/prereg_pass1_fewshot_r2.json` is the law; every deadline here
comes out of it through `scripts/gate_pass1_fewshot.py`, and **nothing in this file may add a number
the record does not carry**. Where a number appears below it is an illustration of the instrument's
output, never a value to type.

**What r2 moved, and it is only this.** Rung 2's ssh dead-man is 500 s of create-elapsed, not 180 —
180 was pass1-probe's reading of one night and it failed on both pods of 2026-08-20. Rung 3's 450 s
ceiling is anchored on the **runner's own launch**, a stamp the pod writes in step 3 and `--watch`
copies back, with a create-anchored **backstop at 1 100 s** beside it. `--pre-create-check` now
holds the recovery clause itself and refuses a create that will not fit. The step's budget is
unchanged at $1.50 all-in: r1's two pods bought $0.117783 of it, and **r2's cap is $1.38**.

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
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-fewshot-r2 --step-cap 1.38 \
  --note "<what this rung is>"
```

## 0 — before anything exists ($0)

```bash
runpodctl pod list -a && runpodctl serverless list && runpodctl network-volume list
git status --porcelain                       # the prereg must NOT be in it
PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --pre-create-check
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-fewshot-r2 --step-cap 1.38 \
  --note "pass1-fewshot-r2 anchor, before the pod"
```

The three listings are the before-state the deletion proof is read against — the volume must appear
in all three readings, before and after, as the positive control that the listing works at all.
`gate_pass1_fewshot.py` refuses to run at all while `results/prereg_pass1_fewshot_r2.json` is
untracked or differs from HEAD: the git clock is what proves the plan predates the money.

**`--pre-create-check` IS the recovery clause.** It prints the whole arithmetic and returns KILL when
the create cannot be paid for — the seconds against the hard stop, the dollars against the cap, and
the number of pods against the ONE re-creation the registration buys. r1 did this by hand and it
worked because a person did it; here it is a gate, and **`--price` runs the same check again**: a
pod created without step 0 is still RECORDED (a pod nothing counts is worse than a pod that should
not exist) and `--price` then returns KILL with the delete instruction. Its
`terminate_after_window_seconds` is the number step 1 puts in `--terminate-after`.

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

## 2 — rung 2, the ssh dead-man (≤ 500 s of this pod's create-elapsed)

`runpodctl ssh info` answers `{"error": "pod not ready"}` until the port mapping is published and
then a JSON object carrying `"ip"` and `"port"`. **Poll on `"port"`, and BOUND the loop below the
dead-man**, so a poller that is looking for the wrong thing cannot spend the deadline being blind:

**BOUND THE LOOP BY THE CLOCK, NOT BY AN ITERATION COUNT.** Each turn pays for a `runpodctl ssh
info` API call on top of its sleep: r1's pod 2 ran a nominally 170 s loop (34 × 5 s) and took
**226 s** of wall clock — 6.65 s a turn, not 5. Ninety-five turns would be ~631 s, past the 500 s
rung AND past the 623 s at which the ONE re-creation stops fitting. The deadline below is rung 2's
own ceiling, read out of the record so it cannot drift:

```bash
CEIL=$(python3.11 -c "import json;print(int(json.load(open('results/prereg_pass1_fewshot_r2.json'))['money']['arithmetic']['ssh_seconds_charged']))")
CREATED=$(date -u -j -f '%Y-%m-%dT%H:%M:%S' '<the create stamp, UTC, WITHOUT its Z or +00:00>' +%s)
# a deadline that failed to parse is an EMPTY variable, and an empty variable makes the loop below
# exit before one API call — silently, and then you hand-poll, which is the class that cost r1 pod 1
[ -n "$CREATED" ] || { echo "the create stamp did not parse — fix it before polling"; false; }
echo "polling until $(date -u -r $((CREATED + CEIL)) +%Y-%m-%dT%H:%M:%SZ), rung 2's own ceiling"

runpodctl ssh info <POD_ID>          # "pod not ready" for FOUR minutes was normal on 2026-08-20
while [ "$(date -u +%s)" -lt $((CREATED + CEIL)) ]; do
  runpodctl ssh info <POD_ID> | grep -q '"port"' && break
  sleep 5
done
runpodctl ssh info <POD_ID>          # the reading the next command asserts
PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --gate0 --ssh-ok   # it answered
```

**If it did not come up, do not linger.** The loop ends at the rung, `--gate0` KILLs a second later,
and r1 measured a 78.5 s tail between the rung firing and the meter stopping — about **578 s** of
billed pod against the **623.448 s** at which the ONE re-creation stops fitting. That is ~45 s of
margin: delete immediately, then `--close`.

**`--gate0` run WITHOUT `--ssh-ok` asserts that the endpoint has NOT answered** — that form is a
KILL past 500 s of create-elapsed whether or not the pod is actually up, because what the gate
records is the reading you gave it. Run it as a poll only while you are inside the deadline. On 2026-08-20 this cost a pod:
the loop grepped `"host"`, a key `runpodctl` never emits, spun for 240 s, and the `--gate0` after it
recorded a dead-man nobody could prove either way ([[a_checker_whose_failure_is_silence]]).

The ceiling is a SPREAD, not a measurement: probe-b saw ssh at 14.5 s on this card in this
datacenter on 2026-08-18, and on 2026-08-20 two pods were still `pod not ready` at 262.5 s and
231.9 s — both LOWER bounds, because ssh was never seen up on either. One dead pod under this rung
costs $0.1111 and the registration is built so that ONE re-creation still fits.

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

The launch is DETACHED, its stdout is the pod log the watch loop tails, and **it stamps rung 3's
anchor in the same command**. `/workspace/run/launched_at` is written by the POD, in the foreground,
the instant before the runner is exec'd — the `;` is load-bearing, an `&&` before an `&` would put
the stamp inside the backgrounded list:

```bash
ssh ... -p <PORT> root@<HOST> \
  'cd /workspace && date -u +%Y-%m-%dT%H:%M:%S+00:00 > /workspace/run/launched_at; \
   HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src nohup \
   /workspace/venv/bin/python -u /workspace/repo/scripts/pass1_fewshot_pod_runner.py \
     --pack /workspace/repo/results/pass1_dev_pack.json \
     --outdir /workspace/run --repo /workspace/repo \
     > /workspace/run/pod.log 2>&1 & echo $!'
```

**Why the stamp is a file the pod writes and not a flag you type.** Rung 3 measures 450 s from the
runner's launch, and a stamp taken late can only ever move that deadline OUTWARD. A number the
executor types is an assertion; this one is a reading, and `--watch` copies it back with the
out-files. The `rm -rf /workspace/run` above is what keeps a previous attempt's stamp from being
read as this one's — and the gate refuses a stamp older than the pod anyway.

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
3 itself, on BOTH of its spans: not one reply 450 s after the launch stamp is a KILL it makes, and
so is not one reply at 1 100 s of create-elapsed even when the stamp is fresh. If the stamp never
arrives at all — a pod that died during staging — the backstop is the only bound left and it fires
on its own. The runner's own progress lines land in the log before the load starts, so the silent
`load_captioner` window sits comfortably inside the 600 s liveness deadline.

The watch prints one line per poll and returns only on GO (every unit answered) or KILL. On KILL it
has ALREADY deleted the pod — go to step 7 and prove it by listing. If the loop ends any other way
it records a gate and prints the pod id with the delete command: run it immediately, because at that
moment nothing is watching a billed pod except the platform backstop.

Once the watch returns GO, record rung 3. **It takes no stamp**: the gate reads the launch anchor
out of the run record and the first reply out of `results/pass1_dev_base.jsonl`'s own
`elapsed_since_start`, which the runner measures from its own start. r1 asked the executor to type
`create + the first row's boot_seconds`, and under a launch anchor that recipe subtracts the ssh
wait and the staging a second time — a 460 s load would have read as 415 s and this rung would have
reported GO on the very condition it was re-anchored to catch.

```bash
PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --boot
```

It reports GO only with the launch anchor beside the reply. **A `--boot` with no `launched_at` in
the run record is a KILL and not a WAIT**: a rung whose deadline cannot be demonstrated has not been
passed, which is the ruling r1 closed its first pod under. If that happens the stamp did not come
back — check `results/pass1_fewshot_r2_launched_at` and the pod's `/workspace/run/` before anything
else.

## 5 — rung 7, the dev gate (on the Mac, $0)

```bash
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/pod.log results/pass1_fewshot_pod.log
PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --dev-gate
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-fewshot-r2 --step-cap 1.38 \
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

The shot's watch does NOT re-arm rung 3 — the model is already loaded and rung 3 went GO on this pod
once already — so a stalled shot dies on the liveness rung, which is the right rung for it. The shot
does not re-stamp `launched_at` either: the pod's entry keeps the first stamp it was given.

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
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-fewshot-r2 --step-cap 1.38 \
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

Only after a deletion PROVEN by listing, and only if the arithmetic still closes. It is no longer
yours to paste: `--pre-create-check` computes both bounds and the count, and returns KILL when the
create cannot be paid for. Every reply already on disk is kept — the shipped resume re-asks only
what has no answer, so a KILL mid-leg costs the load and not the leg.

**Clear the Mac's copies of the dead pod's run directory first.** The replacement pod clears
`/workspace/run` in step 3, so anything still on the Mac is the previous attempt's: a stale
`launched_at` makes `--watch` refuse with a live pod («BEFORE this pod was created»), and stale
out-file rows are a high-water mark the new pod's real progress never rises above — it would die on
the liveness rung while working, or the loop would return GO having watched nothing.

```bash
rm -f results/pass1_fewshot_r2_launched_at results/pass1_fewshot_pod.log \
      results/pass1_dev_base.jsonl results/pass1_dev_v2.jsonl results/pass1_fewshot_shot.jsonl
ls results/pass1_dev_*.jsonl results/pass1_fewshot_r2_launched_at 2>&1   # "No such file" — the proof
PYTHONPATH=src python3.11 scripts/gate_pass1_fewshot.py --pre-create-check   # then step 1 again
```

**A THIRD pod is a STOP.** The registration buys ONE re-creation, and after a second dead pod
nothing fits: the session closes with the attempt NOT spent and the question goes back to the
operator. Paste the check's output either way — it is the reading the report quotes.

## DO NOT

* No training, no adapter, no second prompt variant, no tuning after any eval output.
* Never edit `results/prereg_pass1_probe_b.json`, `results/pass1_probe_b_pack.json`, the gold, the
  labels or the base verdict. The base is NOT re-run on the fourteen.
* Never touch the sealed fourteen before the dev gate says GO.
* Never leave `--watch` while a pod is billing.
* Never two billing endpoints; delete, never stop; no cap raise; no third pod.
* Never edit `results/prereg_pass1_fewshot.json` — r1 is sealed, superseded and never re-opened.
