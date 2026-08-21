# Runbook — pass1-window D1: ONE leg, 1 032 comments, a completeness bar, and a loop you do not leave

The order below is the money. `results/prereg_pass1_window.json` is the law; every deadline here
comes out of it through `scripts/gate_pass1_window.py`, and **nothing in this file may add a number
the record does not carry**. Where a number appears below it is an illustration of the instrument's
output, never a value to type.

**This is r2's runbook with ONE leg and no dev gate.** Rung 2's ssh dead-man is 500 s of
create-elapsed. Rung 3's 450 s ceiling is anchored on the **runner's own launch**, a stamp the pod
writes in step 3 and `--watch` copies back, with a create-anchored **backstop at 1 100 s** beside it.
`--pre-create-check` holds the recovery clause and refuses a create that will not fit. What MOVED
off r2: the cumulative hard stop is **6 500 s** (r2: 6 100) and the cap is **$1.50** (r2: $1.38),
because this population is 1 032 calls and not 464. The step `pass1-window` opens with no pods of
its own, so the step cap IS the contract cap.

**What this run is NOT.** There is no dev gate, no second leg, no paired arm, no bar on v2's quality
and no attempt to spend. The fourteen gold rows and probe-b's sixty-four are answered because they
are IN the population; their agreement is a report-only census row in D2 and can never be quoted as
«v2 takes N of 14».

**The one rule this runbook exists for:** the meter starts at `pod create` and stops at
`pod delete`. Not at ssh, not at the model load, not at the first reply — a pod bills for existing.
`pod stop` does NOT stop it. **Delete, never stop.**

**The second rule: you do not poll by hand.** `--watch` is a BLOCKING loop. It copies the out-file
and the pod log back, it runs the projection gate on EVERY poll (the registration's «every 20 calls»
is the floor), and it KILLS — deletes the pod, records the gate — when no new row and no new log
line have appeared for 600 s, measured from the LAST EVENT. lora-b's arm A finished at 14:38Z and
was found at 17:20Z: 9 720 s of billed idle, $1.43, and the arm that never ran. **Start the watch
and stay in it.** This leg is ~3 500 s of generation, which is more than twice r2's — the loop is
the only thing between a stall and the hard stop.

**Guard reading at every rung, pasted:**

```bash
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-window --step-cap 1.50 \
  --note "<what this rung is>"
```

## 0 — before anything exists ($0)

```bash
runpodctl pod list -a && runpodctl serverless list && runpodctl network-volume list
git status --porcelain                       # the prereg and the pack must NOT be in it
PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --pre-create-check
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-window --step-cap 1.50 \
  --note "pass1-window, before the pod"
```

The three listings are the before-state the deletion proof is read against — the volume must appear
in all three readings, before and after, as the positive control that the listing works at all.
`gate_pass1_window.py` refuses to run at all while `results/prereg_pass1_window.json` is untracked or
differs from HEAD: the git clock is what proves the plan predates the money.

**`--pre-create-check` IS the recovery clause.** It prints the whole arithmetic and returns KILL when
the create cannot be paid for — the seconds against the 6 500 s hard stop, the dollars against the
$1.50 cap, and the number of pods against the ONE re-creation the registration buys. **`--price`
runs the same check again**: a pod created without step 0 is still RECORDED (a pod nothing counts is
worse than a pod that should not exist) and `--price` then returns KILL with the delete instruction.
Its `terminate_after_window_seconds` is the number step 1 puts in `--terminate-after`.

## 1 — create (the meter starts here)

This line does NOT train, so it does not need 48 GB. probe-b and r2 both served this base on a 24 GB
RTX 4090, and r2's 2.726 s/call was measured on one at $0.74/h. An A6000 under the ceiling is
allowed. The volume pins EU-RO-1.

```bash
runpodctl pod create --name mp-pass1-window --gpu-id 'NVIDIA GeForce RTX 4090' --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after '<create + the seconds --pre-create-check left>'
```

**Rung 1 is `costPerHr` in the create RESPONSE, not the price on a listing page.** Over $0.80/h →
delete now and STOP, no generation of any kind. Under it, record the pod:

```bash
PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --price \
  --pod-id <ID> --created-at <the create response's stamp> \
  --usd-per-hour <costPerHr> --card '<the card the response gave>' \
  --terminate-after '<the stamp you actually gave pod create>'
```

`--terminate-after` is the one number this runbook makes you say twice, because the platform flag is
the only thing that enforces rung 6. `--price` re-derives it and REFUSES a window longer than the
cumulative hard stop allows, forgiving only the registered 60 s of overshoot.

## 2 — rung 2, the ssh dead-man (≤ 500 s of this pod's create-elapsed)

`runpodctl ssh info` answers `{"error": "pod not ready"}` until the port mapping is published and
then a JSON object carrying `"ip"` and `"port"`. **Poll on `"port"`, and BOUND the loop by the
CLOCK**, never by an iteration count: each turn pays for an API call on top of its sleep, and r1's
pod 2 ran a nominally 170 s loop in **226 s** of wall clock — 6.65 s a turn, not 5.

```bash
CEIL=$(python3.11 -c "import json;print(int(json.load(open('results/prereg_pass1_window.json'))['money']['arithmetic']['ssh_seconds_charged']))")
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
PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --gate0 --ssh-ok   # it answered
```

**If it did not come up, do not linger.** The loop ends at the rung and `--gate0` KILLs a second
later. r1 measured a 78.5 s tail between the rung firing and the meter stopping; here the widest
dead pod the recovery clause still absorbs is **583.46 s**, so a 500 s rung plus that tail leaves
about 5 s of margin — delete immediately, then `--close`.

**`--gate0` run WITHOUT `--ssh-ok` asserts that the endpoint has NOT answered** — that form is a KILL
past 500 s of create-elapsed whether or not the pod is actually up, because what the gate records is
the reading you gave it. Run it as a poll only while you are inside the deadline. On 2026-08-20 this
cost a pod: the loop grepped `"host"`, a key `runpodctl` never emits, spun for 240 s, and the
`--gate0` after it recorded a dead-man nobody could prove either way
([[a_checker_whose_failure_is_silence]]).

The ceiling is a SPREAD, not a measurement: 14.5 s on 2026-08-18, still not up at 262.5 s and 231.9 s
on 2026-08-20 (both LOWER bounds), ≤ 50 s on 2026-08-21 (an UPPER bound). Four readings, no
measurement of the worst case.

## 3 — stage, and launch the ONE leg

The pack pins the CURRENT parser sha, so the handshake refuses a stale checkout by design. The repo
has no remote; the transport is a git bundle. The pack is **4.6 MB** and travels inside it.

**zsh does not word-split an unquoted variable holding ssh options.** Spell every flag literally.

```bash
SSHK=~/.runpod/ssh/runpodctl-ssh-key
git bundle create /tmp/market-pulse-pass1-window.bundle HEAD
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> /tmp/market-pulse-pass1-window.bundle \
  scripts/pass1_fewshot_pod_runner.py scripts/pass1_pod_runner.py \
  scripts/reader_v5_pod_runner.py scripts/reader_v4_pod_runner.py \
  root@<HOST>:/workspace/
```

```bash
ssh -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -p <PORT> root@<HOST>
# on the pod:
cd /workspace && rm -rf repo && git clone -q market-pulse-pass1-window.bundle repo
cd repo && git rev-parse HEAD && git status --short      # equals the Mac's HEAD, empty
ls -l results/pass1_window_pack.json                     # the pack arrived with the bundle
ls -d /workspace/venv /workspace/hf && du -sh /workspace/hf   # the volume is warm, or STOP

# FIRST POD of this registration — nothing on the volume is this attempt's
rm -rf /workspace/run && mkdir -p /workspace/run
ls /workspace/run                                        # empty — the proof, not the hope
```

**On a RE-CREATION this step is DIFFERENT, and the difference is the recovery clause.** The volume is
the same one, so `/workspace/run/pass1_window_v2.jsonl` still holds every reply the dead pod bought —
and «a KILL mid-leg costs the boot, not the leg» is exactly that file. Wiping the directory would
delete what the clause promises and re-ask 1 032 comments the registration cannot afford twice. What
must go is every clock that belongs to the DEAD pod; what must stay is the answers:

```bash
# RE-CREATION ONLY — never on the first pod
ls -l /workspace/run                                     # what the dead pod left
rm -f /workspace/run/launched_at /workspace/run/pod.log  # rung 3's anchor and rung 5's event count
wc -l /workspace/run/pass1_window_v2.jsonl               # the replies that survive, COUNTED
ls /workspace/run                                        # exactly one file, the out-file
```

`launched_at` must go or the gate refuses it as older than this pod; `pod.log` must go or its line
count is a high-water mark the new pod's real progress never rises above, and the watch would either
kill a working pod on the liveness rung or return GO having watched nothing.

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
     --pack /workspace/repo/results/pass1_window_pack.json --only v2 \
     --outdir /workspace/run --repo /workspace/repo \
     > /workspace/run/pod.log 2>&1 & echo $!'
```

**The runner is r2's, unedited, and `--only v2` is what makes a one-leg pack legal there.** It was
driven against this exact pack on a fake transport before any pod existed
(`tests/test_gate_pass1_window.py::test_the_shipped_runner_answers_a_ONE_leg_pack_unchanged`): the
handshake passes, all 1 032 items re-render to the shas the pack pinned, and the replies land in
`pass1_window_v2.jsonl`. There is no finding to report here.

**The first thing the runner does is re-render all 1 032 requests and compare each sha**, before the
model is loaded. It is CPU-only and it is not a cost: measured on the Mac against this pack,
`check_requests` over all 1 032 items takes **0.01 s** and `check_instrument` under 0.001 s. It sits
inside the 450 s load ceiling with nothing to spare from, and it is why a moved request stops the
leg instead of being served.

**Why the stamp is a file the pod writes and not a flag you type.** Rung 3 measures 450 s from the
runner's launch, and a stamp taken late can only ever move that deadline OUTWARD. A number the
executor types is an assertion; this one is a reading, and `--watch` copies it back with the
out-file, into `results/pass1_window_launched_at` — **its own name**, because `results/` still holds
`pass1_fewshot_r2_launched_at` from the closed session and a shared name would read a dead pod's
clock.

## 4 — the WATCH, entered IMMEDIATELY (rungs 3, 4, 5 and 6), and not left

```bash
PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --watch \
  --ssh root@<HOST> --ssh-port <PORT>
```

**Enter it the moment the launch returns a pid — do not hand-poll `--boot` first.** Polling a gate
by hand through a model load is the habit rung 5 was bought to remove, and the loop arms rung 3
itself, on BOTH of its spans: not one reply 450 s after the launch stamp is a KILL it makes, and so
is not one reply at 1 100 s of create-elapsed even when the stamp is fresh. If the stamp never
arrives at all — a pod that died during staging — the backstop is the only bound left and it fires
on its own.

The watch prints one line per poll and returns only on GO (every unit answered) or KILL. On KILL it
has ALREADY deleted the pod — go to step 6 and prove it by listing. If the loop ends any other way
it records a gate and prints the pod id with the delete command: run it immediately, because at that
moment nothing is watching a billed pod except the platform backstop.

Once the watch returns GO, record rung 3. **It takes no stamp**: the gate reads the launch anchor out
of the run record and the first reply out of `results/pass1_window_v2.jsonl`'s own
`elapsed_since_start`, which the runner measures from its own start.

```bash
PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --boot
```

**READ `first_reply_at_create_elapsed_seconds` OFF THAT GATE — it decides which run you are in.**
Rung 4 prices every remaining call at the LARGER of the leg's mean and its LAST call, so one slow
reply is priced as if all 1 032 were that slow, and the seconds the hard stop can lend depend on
what the pre-generation already spent:

| pre-generation at the first reply | one call KILLs above | the worst call this stack has measured |
|---|---:|---:|
| 254.6 s — what r2 actually measured | 4.81 s | 4.066 s — safe by 1.18× |
| ~700 s | ~4.4 s | safe |
| 1 100 s — what the budget CHARGES | **3.99 s** | **4.066 s — the measured worst is ABOVE it** |

So a pod whose first reply lands near the 1 100 s backstop is one outlier call away from a rung-4
KILL, and a KILL past 583.46 s of billed seconds also refuses the re-creation. Nothing after the
create changes this. **What changes it is step 3:** the charged 1 100 is ssh 500 + stage/launch 150 +
load 450, and the staging half is hand-driven — probe-b bounds ssh + staging + launch TOGETHER at
≤ 89.5 s. Every second between the ssh GO and the launch is a second rung 4 will not lend to the
rate, so stage without pause and do not read anything on the pod that is not on the list.

The whole curve, both spans, is in the record at
`money.arithmetic.cumulative.projection_gate.single_call_sensitivity` — including the trade the
executor may NOT take: a 6 700 s hard stop would be $1.4889, still inside the $1.50 cap, and would
put the charged-span edge at 4.167 s/call. That is the operator's word and nobody else's.

It reports GO only with the launch anchor beside the reply. **A `--boot` with no `launched_at` in the
run record is a KILL and not a WAIT**: a rung whose deadline cannot be demonstrated has not been
passed. If that happens the stamp did not come back — check `results/pass1_window_launched_at` and
the pod's `/workspace/run/` before anything else.

## 5 — scp EVERYTHING, then delete, then prove it

Files come back BEFORE the verdict and before the deletion. Every hash is compared on the pod and on
the Mac; a file that only ever existed on the pod is evidence nobody can re-score. One command per
artifact, so a failed copy is visible rather than averaged into a wildcard.

```bash
ssh ... -p <PORT> root@<HOST> 'cd /workspace/run && find . -type f | sort | xargs sha256sum'
# LC_ALL=C sha256sum on the pod; shasum -a 256 on the Mac. Same digest, two tools

scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/pass1_window_v2.jsonl results/pass1_window_v2.jsonl
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/launched_at results/pass1_window_launched_at
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/pod.log results/pass1_window_pod.log
shasum -a 256 results/pass1_window_v2.jsonl results/pass1_window_launched_at \
  results/pass1_window_pod.log        # THREE for three — the contract says «four for four», which
                                      # is r2's file count (two dev legs + stamp + log). One leg
                                      # means three files. Named as a deviation, not silently done

runpodctl pod delete <POD_ID>
runpodctl pod list -a                # []
runpodctl serverless list            # [] — nothing was ever created here
runpodctl network-volume list        # the volume, unchanged: the POSITIVE CONTROL

PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --close \
  --deleted-at <the deletion stamp> --outcome '<why this pod ended>'
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-window --step-cap 1.50 \
  --note "pod deleted, the step is closed"
```

## 6 — rung 7, the completeness bar (on the Mac, $0)

```bash
PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --completeness
```

Three numbers, and the gate COUNTS all three rather than raising on any of them:

* **answered 1 032 / 1 032**, by DISTINCT id. A duplicate id or an id the leg never asked is RED on
  its own — the first would inflate the count and the second means the file is not this leg's.
* **`rendering_sha256` mismatches: 0.** The pod refuses the whole leg on a sha it cannot reproduce,
  so a mismatch here means the out-file and the pack parted AFTER the run — a copy-back error or a
  rebuilt pack. Either is RED.
* **parse refusals ≤ 10 (1 %), counted by CAUSE.** A refusal is an ANSWERED row whose reply the
  parser refused; the two counts are not disjoint, which is the only reason «1 032 answered» and
  «≤ 10 refusals» are satisfiable together.

**RED does not delete anything already bought and does not re-run the pod.** The out-file, its
refusals by cause and its mismatches go back to the team lead with the census. A second pod is the
recovery clause's, and the recovery clause allows one.

## 7 — D2, the census ($0, after the pod is closed)

`results/pass1_window_census.json` and `docs/reports/pass1-window.md`. The label distribution over
the 1 032 and per thread; the pass-2 filter table that prices `pass2-signals`; and the report-only
readings, each captioned «not a bar» — the 650 labelled rows, the 450 outside dev-200, the dev-200
themselves against r2's 136/200 · 38/49, and the fourteen with the multiplicity sentence the record
carries in `return_to_the_operator`.

## Recovery — ONE re-creation, and never two endpoints

Only after a deletion PROVEN by listing, and only if the arithmetic still closes. It is not yours to
paste: `--pre-create-check` computes both bounds and the count. Every reply already on disk is kept
on the POD's volume — the shipped resume re-asks only what has no answer, so a KILL mid-leg costs the
load and not the leg.

**Clear the Mac's copies of the dead pod's run directory first, and ONLY this contract's** (Dv621).
r2's `pass1_dev_base.jsonl`, `pass1_dev_v2.jsonl`, `pass1_fewshot_r2_launched_at` and
`pass1_fewshot_pod.log` are that session's committed evidence and are frozen — the record lists them.

```bash
rm -f results/pass1_window_launched_at results/pass1_window_pod.log results/pass1_window_v2.jsonl
ls results/pass1_window_v2.jsonl results/pass1_window_launched_at 2>&1   # "No such file" — the proof
git status --porcelain results/                # r2's evidence is untouched: nothing of it listed
PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --pre-create-check   # then step 1 again
```

**The Mac's copies go and the POD's out-file stays.** They are not the same file: the local one is a
copy the watch pulls and the pod's is what the resume reads. Clearing the local one costs one scp;
clearing the pod's costs the whole leg.

**Take BOTH readings and let the stricter bind.** `--pre-create-check` computes from the gate's own
ledger — the closed pods' billed seconds on the pod clock, timely and exact. The guard reads the
balance delta and the billing walk, which is what the cap is defined against and which lags by up to
~32 min. Two meters, neither one the other:

```bash
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-window --step-cap 1.50 \
  --note "before the re-creation — the MONEY reading beside the gate's clock"
PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --pre-create-check
```

**And read `--pre-create-check`'s own arithmetic before believing the clause.** It prices the FULL
worst case ahead — 5 916.54 s — and not the calls that actually remain, so a re-creation is refused
once the dead pod billed more than **583.46 s**, whatever the resume would have saved. A KILL at rung
2 or rung 3 is inside that window; a KILL deep inside the generation is NOT, and the clause is then a
STOP rather than a recovery. That is the registration's arithmetic and not a bug to work around: the
seconds are what the platform holds.

A stale `launched_at` makes `--watch` refuse with a live pod («BEFORE this pod was created»), and
stale out-file rows are a high-water mark the new pod's real progress never rises above — it would
die on the liveness rung while working, or the loop would return GO having watched nothing.

**A THIRD pod is a STOP.** The registration buys ONE re-creation, and after a second dead pod nothing
fits: the session closes with no verdict and the question goes back to the operator. Paste the
check's output either way — it is the reading the report quotes.

## DO NOT

* No change to prompt v2, the neighbour rule, the labels, the gold or any sealed record.
* No second leg — the base was measured in r2 and is not re-run. No dev gate; this contract has none.
* No re-purchase of reader context: the v5b / v4 / topup verdicts are read, never bought.
* Never leave `--watch` while a pod is billing.
* Never two billing endpoints; delete, never stop; no cap raise; no third pod.
* Never edit `results/prereg_pass1_fewshot.json` or `_r2.json` — both sealed, superseded, never
  re-opened. `scripts/gate_pass1_fewshot.py` is IMPORTED by this contract's gate and never edited.
* Never quote the fourteen, the 650 or the 450 as a bar. They are census rows with a multiplicity.
