# Runbook — pass1-window r2 D1: the 901 still owed, priced on the POD CLASS, and a loop you do not leave

The order below is the money. `results/prereg_pass1_window_r2.json` is the law; every deadline here
comes out of it through `scripts/gate_pass1_window_r2.py`, and **nothing in this file may add a
number the record does not carry**. Where a number appears below it is an illustration of the
instrument's output, never a value to type.

**This is r1's runbook, corrected, with ONE thing added and every price re-derived.** What is added
is step 3a: the r1 pod's out-file survives on the network volume and is copied back as EVIDENCE
before anything clears the run directory. What MOVED off r1: the population is **901** and not
1 032, the rate charged is **6.14 s/call** and not 3.4075, the cumulative hard stop is **8 600 s**
and the cap is **$2.00**. The guard step is **`pass1-window-r2`**, a FRESH ledger; r1's step stays
open for `money-anchors` and its pod's $0.173694 is not charged against this cap.

**Why the rate moved, in one line.** r1 priced the window off a rate measured on another pod and the
pod it rented ran 1.65× slower. A rate is a property of the POD, so this registration charges the
TOP of the spread this stack has measured — probe-b's base leg times v2's uplift — and rung 4 kills
anything slower than that at the first poll that shows it.

**What this run is NOT.** No dev gate, no second leg, no paired arm, no bar on v2's quality, no
attempt to spend. The nine gold rows r1 never reached are answered because they are IN the
population; their agreement is a report-only census row in D2, the FIFTH look at those fourteen, and
can never be quoted as «v2 takes N of 14».

**The one rule this runbook exists for:** the meter starts at `pod create` and stops at
`pod delete`. Not at ssh, not at the model load, not at the first reply — a pod bills for existing.
`pod stop` does NOT stop it. **Delete, never stop.**

**The second rule: you do not poll by hand.** `--watch` is a BLOCKING loop. It copies the out-file
and the pod log back, runs the projection gate on EVERY poll, and KILLS — deletes the pod, records
the gate — when no new row and no new log line have appeared for 600 s, measured from the LAST
EVENT. This leg is ~5 500 s of charged generation. **Start the watch and stay in it.**

**Guard reading at every rung, pasted:**

```bash
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-window-r2 --step-cap 2.00 \
  --note "<what this rung is>"
```

## 0 — before anything exists ($0)

```bash
runpodctl pod list -a && runpodctl serverless list && runpodctl network-volume list
git status --porcelain                       # the prereg and the pack must NOT be in it
PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --pre-create-check
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-window-r2 --step-cap 2.00 \
  --note "pass1-window r2, before the pod"
```

The three listings are the before-state the deletion proof is read against — the volume must appear
in all three readings, before and after, as the positive control that the listing works at all.
`gate_pass1_window_r2.py` refuses to run at all while `results/prereg_pass1_window_r2.json` is
untracked or differs from HEAD, and it refuses if `scripts/gate_pass1_window.py` has moved: it
EXECUTES that file's rung logic, held to the sha r1's sealed record pins.

**`--pre-create-check` IS the recovery clause, and now it RECORDS its verdict.** r1's printed the
refusal that ended its session to a terminal and wrote nothing down; this one appends a
`pre-create-check` gate to `results/pass1_window_r2_run.json` every time it runs, GO and KILL alike.
It prints the whole arithmetic: the seconds against the 8 600 s hard stop, the dollars against the
$2.00 cap, and the pod count against the ONE re-creation. Its `terminate_after_window_seconds` is
the number step 1 puts in `--terminate-after`. **`--price` runs the same check again**: a pod created
without step 0 is still RECORDED and `--price` then returns KILL with the delete instruction.

## 1 — create (the meter starts here)

This line does NOT train, so it does not need 48 GB. Three pods have served this base on a 24 GB
RTX 4090. The volume pins EU-RO-1.

```bash
runpodctl pod create --name mp-pass1-window-r2 --gpu-id 'NVIDIA GeForce RTX 4090' --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after '<create + the seconds --pre-create-check left>'
```

**Rung 1 is `costPerHr` in the create RESPONSE, not the price on a listing page.** Over $0.80/h →
delete now and STOP, no generation of any kind. Under it, record the pod:

```bash
PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --price \
  --pod-id <ID> --created-at <the create response's stamp> \
  --usd-per-hour <costPerHr> --card '<the card the response gave>' \
  --terminate-after '<the stamp you actually gave pod create>'
```

`--terminate-after` is the one number this runbook makes you say twice, because the platform flag is
the only thing that enforces rung 6. `--price` re-derives it and REFUSES a window longer than the
cumulative hard stop allows, forgiving only the registered 60 s of overshoot.

**And the price is not the rate.** r1's pod cost $0.74/h and ran at 4.498 s/call; probe-b's pod cost
the same and ran its base leg at 5.162. Rung 1 bounds the dollars per second and says nothing at all
about the seconds per call — that is rung 4's job, from the first reply onward.

## 2 — rung 2, the ssh dead-man (≤ 500 s of this pod's create-elapsed)

`runpodctl ssh info` answers `{"error": "pod not ready"}` until the port mapping is published and
then a JSON object carrying `"ip"` and `"port"`. **Poll on `"port"`, and BOUND the loop by the
CLOCK**, never by an iteration count: each turn pays for an API call on top of its sleep, and a
nominally 170 s loop has been measured at **226 s** of wall clock — 6.65 s a turn, not 5.

```bash
CEIL=$(python3.11 -c "import json;print(int(json.load(open('results/prereg_pass1_window_r2.json'))['money']['arithmetic']['ssh_seconds_charged']))")
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
PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --gate0 --ssh-ok   # it answered
```

**If it did not come up, do not linger.** The loop ends at the rung and `--gate0` KILLs a second
later. r1 measured a 78.5 s tail between the rung firing and the meter stopping; here the widest
dead pod the recovery clause still absorbs is **667.86 s**, so a 500 s rung plus that tail leaves
**89.36 s** of margin — eighteen times r1's 4.96 s, and still not a reason to linger.

**`--gate0` run WITHOUT `--ssh-ok` asserts that the endpoint has NOT answered** — that form is a KILL
past 500 s of create-elapsed whether or not the pod is actually up, because what the gate records is
the reading you gave it. Run it as a poll only while you are inside the deadline.

The ceiling is a SPREAD, not a measurement: 14.5 s on 2026-08-18, still not up at 262.5 s and 231.9 s
on 2026-08-20 (both LOWER bounds), ≤ 50 s and 29 s on 2026-08-21 (both UPPER bounds). Five readings,
no measurement of the worst case.

## 3a — the VOLUME's surviving out-file, copied back BEFORE anything clears (new in r2)

The r1 pod was killed inside the watch loop, so every row it generated between the last poll and the
deletion is on the volume and nowhere else. `/workspace/run/pass1_window_v2.jsonl` is still there and
the r1 pod's own log names at least one row the Mac never got
(`@klopotenkofood:6035#21205`, reply 132/1032 at 759.2 s). **Copy it before the run directory is
touched. It is EVIDENCE and it is never merged.**

```bash
SSHK=~/.runpod/ssh/runpodctl-ssh-key
ssh -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -p <PORT> root@<HOST> 'ls -l /workspace/run && LC_ALL=C sha256sum /workspace/run/*.jsonl'
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/pass1_window_v2.jsonl \
  results/pass1_window_volume_tail.jsonl
shasum -a 256 results/pass1_window_volume_tail.jsonl     # equal to the pod's digest, or STOP
PYTHONPATH=src python3.11 scripts/volume_tail_pass1_window.py \
  --tail results/pass1_window_volume_tail.jsonl
```

The module counts what the volume holds beyond the Mac's 131 and refuses a row that belongs to no
population. Every extra row is inside the 901 this contract buys, so it is **bought twice** — the
census names the count and the cost (`rows × the measured s/call of THIS pod`), and
`--seconds-per-call` is handed that rate at D2, not now.

**It is not merged, and the reason is not tidiness.** Merging would put two answers in play for one
id: the volume's, written by a pod that was killed, and this run's. Which one a later reader picks
is an ambiguity this registration does not buy.

If the file is NOT on the volume, that is a finding and not a blocker: record what `ls -l` showed,
note that Dv657's lower bound can no longer be closed, and go on. Nothing downstream depends on it.

## 3b — stage, clear the dead pod's clocks, and launch the ONE leg

The pack pins the CURRENT parser sha, so the handshake refuses a stale checkout by design. The repo
has no remote; the transport is a git bundle. The r2 pack is **~4.0 MB** and travels inside it.

**zsh does not word-split an unquoted variable holding ssh options.** Spell every flag literally.

```bash
git bundle create /tmp/market-pulse-pass1-window-r2.bundle HEAD
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> /tmp/market-pulse-pass1-window-r2.bundle \
  scripts/pass1_fewshot_pod_runner.py scripts/pass1_pod_runner.py \
  scripts/reader_v5_pod_runner.py scripts/reader_v4_pod_runner.py \
  root@<HOST>:/workspace/
```

```bash
ssh -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -p <PORT> root@<HOST>
# on the pod:
cd /workspace && rm -rf repo && git clone -q market-pulse-pass1-window-r2.bundle repo
cd repo && git rev-parse HEAD && git status --short      # equals the Mac's HEAD, empty
ls -l results/pass1_window_r2_pack.json                  # the pack arrived with the bundle
ls -d /workspace/venv /workspace/hf && du -sh /workspace/hf   # the volume is warm, or STOP

# FIRST POD of this registration — step 3a has ALREADY copied the r1 file back
rm -rf /workspace/run && mkdir -p /workspace/run
ls /workspace/run                                        # empty — the proof, not the hope
```

**Do not run this until step 3a's scp and sha have both passed.** `rm -rf /workspace/run` deletes the
r1 pod's surviving out-file, and that file is the only place its extra rows exist.

**On a RE-CREATION this step is DIFFERENT, and the difference is the recovery clause.** The volume is
the same one, so `/workspace/run/pass1_window_r2_v2.jsonl` holds every reply the dead pod of THIS
attempt bought — and «a KILL mid-leg costs the boot, not the leg» is exactly that file. What must go
is every clock that belongs to the DEAD pod; what must stay is the answers:

```bash
# RE-CREATION ONLY — never on the first pod
ls -l /workspace/run                                        # what the dead pod left
rm -f /workspace/run/launched_at /workspace/run/pod.log
wc -l /workspace/run/pass1_window_r2_v2.jsonl               # the replies that survive, COUNTED
ls /workspace/run                                           # exactly one file, the out-file
```

`launched_at` must go or the gate refuses it as older than this pod; `pod.log` must go or its line
count is a high-water mark the new pod's real progress never rises above, and the watch would either
kill a working pod on the liveness rung or return GO having watched nothing.

If `/workspace/hf` is not there the weights are not on the volume, the boot is a 59 GB download and
this registration priced no such thing: delete and STOP.

The launch is DETACHED, its stdout is the pod log the watch loop tails, and **it stamps rung 3's
anchor in the same command**. The stamp is written by the POD, in the foreground, the instant before
the runner is exec'd — the `;` is load-bearing, an `&&` before an `&` would put the stamp inside the
backgrounded list:

```bash
ssh ... -p <PORT> root@<HOST> \
  'cd /workspace && date -u +%Y-%m-%dT%H:%M:%S+00:00 > /workspace/run/launched_at; \
   HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src nohup \
   /workspace/venv/bin/python -u /workspace/repo/scripts/pass1_fewshot_pod_runner.py \
     --pack /workspace/repo/results/pass1_window_r2_pack.json --only v2 \
     --outdir /workspace/run --repo /workspace/repo \
     > /workspace/run/pod.log 2>&1 & echo $!'
```

**The runner is r2's, unedited, and `--only v2` is what makes a one-leg pack legal there.** It was
driven against this exact pack on a fake transport before any pod existed: the handshake passes, all
901 items re-render to the shas the pack pinned — the same shas r1's pod verified on all 1 032,
because these ARE r1's items — and the replies land in `pass1_window_r2_v2.jsonl`.

**The stamp's name on the POD is `launched_at` and its name on the Mac is
`pass1_window_r2_launched_at`.** They are different on purpose and neither is free to choose:
`--watch`'s own `pull()` copies `<remote-dir>/launched_at` into `results/<LAUNCH_STAMP>`, so the
remote name is fixed by the gate and the local one is this attempt's. A launch command that wrote
the LOCAL name onto the pod would leave `--watch` copying a file that does not exist — rung 3 would
have no anchor, `--boot` would be a KILL, and the create-anchored backstop would be the only bound
left. `tests/test_gate_pass1_window_r2.py` greps this runbook for both names and asserts them
against the gate's own code.

**Why the stamp is a file the pod writes and not a flag you type.** Rung 3 measures 450 s from the
runner's launch, and a stamp taken late can only ever move that deadline OUTWARD. A number the
executor types is an assertion; this one is a reading, and `--watch` copies it back into
`results/pass1_window_r2_launched_at` — **its own name**, because `results/` still holds
`pass1_window_launched_at` and `pass1_fewshot_r2_launched_at` from two closed sessions.

## 4 — the WATCH, entered IMMEDIATELY (rungs 3, 4, 5 and 6), and not left

```bash
PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --watch \
  --ssh root@<HOST> --ssh-port <PORT>
```

**Enter it the moment the launch returns a pid — do not hand-poll `--boot` first.** The loop arms
rung 3 itself, on BOTH of its spans: not one reply 450 s after the launch stamp is a KILL it makes,
and so is not one reply at 1 100 s of create-elapsed even when the stamp is fresh.

The watch prints one line per poll and returns only on GO (every unit answered) or KILL. On KILL it
has ALREADY deleted the pod — go to step 6 and prove it by listing.

Once the watch returns GO, record rung 3. **It takes no stamp**: the gate reads the launch anchor out
of the run record and the first reply out of `results/pass1_window_r2_v2.jsonl`'s own
`elapsed_since_start`.

```bash
PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --boot
```

**READ `first_reply_at_create_elapsed_seconds` OFF THAT GATE — it decides which run you are in.**
Rung 4 prices every remaining call at the LARGER of the leg's mean and its LAST call, so the seconds
the hard stop can lend depend on what the pre-generation already spent:

| pre-generation at the first reply | the sustained rate the stop can pay for | against |
|---|---:|---|
| 252.5 s — what r1's pod MEASURED | **7.82 s/call** | 1.26× the slowest call ever measured (6.214) |
| 1 100 s — what the budget CHARGES | **6.88 s/call** | 1.11× it — and 1.12× the 6.14 charged |

Both arms are above the worst single call this stack has seen, which is the one thing r1's
registration could not say: its charged-span edge was 3.97 against a measured worst of 4.066. **What
still changes it is step 3:** the charged 1 100 is ssh 500 + stage/launch 150 + load 450, and the
staging half is hand-driven — r1 measured ssh at 29 s, stage + launch at 54 s and the load at
164.9 s, 252.5 s against 1 100 charged. Every second between the ssh GO and the launch is a second
rung 4 will not lend to the rate.

**And know what a KILL costs before it happens — AT BOTH SPANS, because the answer reverses.** The
recovery clause is checked on BILLED seconds and the meter runs to `pod delete`, so what decides it
is the create-elapsed at the kill plus the charged 78.5 s tail against 667.86 s:

| the kill | create-elapsed at the kill | recoverable? |
|---|---:|---|
| rung 2, the ssh dead-man | ≤ 500 s → bills 578.5 | **always** |
| rung 4 at 8 s/call, 20 calls in, pre-generation 252.5 s (what r1 MEASURED) | 412.5 s → bills 491.0 | **yes, ≈ $0.11** |
| rung 4 at 8 s/call, 20 calls in, pre-generation 1 100 s (what the budget CHARGES) | 1 260 s → bills 1 338.5 | **no — STOP** |
| rung 3's create-anchored backstop | 1 100 s → bills 1 178.5 | **never** |

**The widest create-elapsed at which any kill stays recoverable is 589.36 s**, and the record
derives it (`money.arithmetic.recovery_arithmetic.which_KILLS_stay_recoverable`). At the
pre-generation the budget charges, that line is already crossed before the first call lands, so in
that world every rate KILL is a STOP and not a recovery. This is why step 3 is hand-driven and why
`first_reply_at_create_elapsed_seconds` is the reading to take: **it does not only tell you which
knife edge you are under, it tells you whether a kill can be recovered at all.** The whole curve,
both spans, is in the record at
`money.arithmetic.cumulative.projection_gate.single_call_sensitivity`.

It reports GO only with the launch anchor beside the reply. **A `--boot` with no `launched_at` in the
run record is a KILL and not a WAIT.** And on a pod the watch has already killed, `--boot` has
nothing live to measure: rung 3 is then read off the artifacts — the launch stamp, the first row's
`boot_seconds` and `elapsed_since_start` — and reported from them, never back-filled.

## 5 — scp EVERYTHING, then delete, then prove it

Files come back BEFORE the verdict and before the deletion. Every hash is compared on the pod and on
the Mac; a file that only ever existed on the pod is evidence nobody can re-score. One command per
artifact, so a failed copy is visible rather than averaged into a wildcard.

```bash
ssh ... -p <PORT> root@<HOST> 'cd /workspace/run && find . -type f | sort | xargs sha256sum'
# LC_ALL=C sha256sum on the pod; shasum -a 256 on the Mac. Same digest, two tools

scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/pass1_window_r2_v2.jsonl results/pass1_window_r2_v2.jsonl
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/launched_at results/pass1_window_r2_launched_at
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/pod.log results/pass1_window_r2_pod.log
shasum -a 256 results/pass1_window_r2_v2.jsonl results/pass1_window_r2_launched_at \
  results/pass1_window_r2_pod.log      # THREE for three — one leg means three files

runpodctl pod delete <POD_ID>
runpodctl pod list -a                # []
runpodctl serverless list            # [] — nothing was ever created here
runpodctl network-volume list        # the volume, unchanged: the POSITIVE CONTROL

PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --close \
  --deleted-at <the deletion stamp> --outcome '<why this pod ended>'
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-window-r2 --step-cap 2.00 \
  --note "pod deleted, the step is closed"
```

## 6 — rung 7, the completeness bar (on the Mac, $0)

```bash
PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --completeness
```

Three numbers, and the gate COUNTS all three rather than raising on any of them:

* **answered 901 / 901**, by DISTINCT id. A duplicate id or an id the leg never asked is RED on its
  own — the first would inflate the count and the second means the file is not this leg's.
* **`rendering_sha256` mismatches: 0.** The pod refuses the whole leg on a sha it cannot reproduce,
  so a mismatch here means the out-file and the pack parted AFTER the run.
* **parse refusals ≤ 9 (1 %), counted by CAUSE.** A refusal is an ANSWERED row whose reply the
  parser refused; the two counts are not disjoint, which is the only reason «901 answered» and
  «≤ 9 refusals» are satisfiable together.

**This bar is over the 901 and not over the window.** D2 reports the window's own completeness —
131 + answered, against 1 032 — BESIDE it. A GO here with the union short of 1 032 is a GO on this
contract and an open window, and the report says both.

**RED does not delete anything already bought and does not re-run the pod.**

## 7 — D2, the census ($0, after the pod is closed)

`results/pass1_window_r2_census.json` and `docs/reports/pass1-window-r2.md`. The census is over the
UNION 131 + 901 = 1 032, keyed on the PAIR `(thread, msg_id)` — seven msg_ids of the 650 labelled
rows live in two threads each, so a union keyed on the msg_id would merge two channels' comments into
one row. The label distribution in three states; the per-thread pass-2 filter table over the WHOLE
window — this is what prices `pass2-signals`; the report-only readings pair-keyed; the volume tail's
rows-bought-twice with their cost; and the measured spans beside what was charged, with THIS pod's
s/call beside 2.726, 4.498 and 5.162.

## Recovery — ONE re-creation, and never two endpoints

Only after a deletion PROVEN by listing, and only if the arithmetic still closes. It is not yours to
paste: `--pre-create-check` computes both bounds and the count, and records its verdict.

**Clear the Mac's copies of the dead pod's run directory first, and ONLY this contract's** (Dv621).
r1's `pass1_window_v2.jsonl`, `pass1_window_launched_at`, `pass1_window_pod.log` and the volume tail
are that session's committed evidence and are frozen — the record lists them.

```bash
rm -f results/pass1_window_r2_launched_at results/pass1_window_r2_pod.log \
      results/pass1_window_r2_v2.jsonl
ls results/pass1_window_r2_v2.jsonl 2>&1        # "No such file" — the proof
git status --porcelain results/                 # r1's evidence is untouched: nothing of it listed
PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --pre-create-check   # then step 1 again
```

**The Mac's copies go and the POD's out-file stays.** They are not the same file: the local one is a
copy the watch pulls and the pod's is what the resume reads. Clearing the local one costs one scp;
clearing the pod's costs the whole leg.

**Take BOTH readings and let the stricter bind.** `--pre-create-check` computes from the gate's own
ledger — the closed pods' billed seconds on the pod clock, timely and exact. The guard reads the
balance delta and the billing walk, which is what the cap is defined against and which lags (on r1
the walk reported `pods $0.0000` for a pod that had run 845 s). Two meters, neither one the other:

```bash
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-window-r2 --step-cap 2.00 \
  --note "before the re-creation — the MONEY reading beside the gate's clock"
PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --pre-create-check
```

**And read `--pre-create-check`'s own arithmetic before believing the clause.** It prices the FULL
worst case ahead — 7 932.14 s — and not the calls that actually remain, so a re-creation is refused
once the dead pod billed more than **667.86 s**, whatever the resume would have saved. A KILL at rung
2 or rung 3 is inside that window; a KILL deep inside the generation is NOT, and the clause is then a
STOP rather than a recovery. **This is exactly what closed r1**: its pod had billed 845 s against an
allowance of 583.46, and the refusal came on seconds while the money still fitted.

**A THIRD pod is a STOP.** The registration buys ONE re-creation, and after a second dead pod nothing
fits: the session closes with no verdict and the question goes back to the operator. Paste the
check's output either way — it is the reading the report quotes.

## DO NOT

* No change to prompt v2, the neighbour rule, the labels, the gold or any sealed record.
* No change to `results/pass1_window_pack.json`, `results/pass1_window_v2.jsonl` or
  `results/prereg_pass1_window.json` — r1's pack, replies and record are sealed INPUTS of this pack.
* No merge of the volume's surviving out-file. It is copied, counted, priced and left alone.
* No second leg — the base was measured in r2 and is not re-run. No dev gate; this contract has none.
* No re-purchase of reader context: the v5b / v4 / topup verdicts are read, never bought.
* Never leave `--watch` while a pod is billing.
* Never two billing endpoints; delete, never stop; no cap raise; no third pod.
* Never edit `scripts/gate_pass1_window.py` or `scripts/gate_pass1_fewshot.py` — this contract's gate
  EXECUTES the first and IMPORTS the second, and both are pinned by sealed records.
* Never quote the fourteen, the 650 or the 450 as a bar. They are census rows with a multiplicity,
  and the fourteen are now on their FIFTH look.
