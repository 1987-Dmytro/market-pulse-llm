# Runbook — pass2-signals D1: five threads, a go/no-go, and 74 that are not bought yet

The order below is the money. `results/prereg_pass2_signals.json` is the law; every deadline here
comes out of it through `scripts/gate_pass2_signals.py`, and **nothing in this file may add a number
the record does not carry**. Where a number appears below it is an illustration of the instrument's
output, never a value to type.

**This is `pass1-window r2`'s runbook with ONE step inserted, and that step is the whole contract.**
The pod answers the reference's five flagship threads, then STOPS and waits. The Mac reads their
seconds off the out-file, computes `charged_full = max(1.5 × smoke_mean, smoke_max)`, and either
writes a token that releases the remaining 74 or does not. **The 74 are not bought when the pod is
created.** They are bought by rung S′, or not at all.

**Why.** This prompt has no rate. Pass-1 replies were ~50 tokens; a pass-2 reply is a list of
signals, and nothing on this stack has measured that decode. The nearest measured shape is the
reader's — v5b's leg A at 45.016 s a thread — and the registration charges the smoke at **120 s/call
as an ASSUMPTION**, which is the only assumption in the record.

**What the numbers are, and where a GO lives:**

| | |
|---|---:|
| smoke, charged | 5 × 120 s = **600 s** |
| pre-generation charged (ssh 500 + stage/launch 150 + load 450) | **1 100 s** |
| overhead | **1 300 s** |
| the smoke's worst case, all in | **3 000 s = $0.6667** |
| cumulative hard stop, platform-held | **6 600 s = $1.4667** of a **$1.50** cap |
| rung S′'s knife edge at a 600 s smoke | **48.6486 s/call** |
| what a GO needs | `smoke_mean ≤ 32.4324` **AND** `smoke_max ≤ 48.6486` |
| widest dead pod that still fits the smoke | **3 600 s** |

**The first rule:** the meter starts at `pod create` and stops at `pod delete`. Not at ssh, not at
the model load, not at the first reply — a pod bills for existing, and `pod stop` does NOT stop it.
**Delete, never stop.**

**The second rule: you do not poll by hand.** `--watch` is a BLOCKING loop. It copies the out-file
and the pod log back, runs the projection gate on EVERY poll, and KILLS when no new row **and no new
log line** have appeared for 600 s from the LAST EVENT. A pass-2 call takes minutes and the go wait
writes no row at all, which is exactly why the log line is an event: `pass2_pod_runner.wait_for_go`
prints one `WAIT` line every 15 s while it waits.

**The third rule, and it is new: a KILL after the smoke's first reply CLOSES the session.** The
recovery clause allows one re-creation for a death at rungs 1–3 only. After the first reply the
replies on the Mac are the evidence and the remainder is a new registration.

**Guard reading at every rung, pasted:**

```bash
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass2-signals --step-cap 1.50 \
  --note "<what this rung is>"
```

## 0 — before anything exists ($0)

```bash
runpodctl pod list -a && runpodctl serverless list && runpodctl network-volume list
git status --porcelain                       # the prereg and the pack must NOT be in it
PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --pre-create-check
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass2-signals --step-cap 1.50 \
  --note "pass2-signals, before the pod"
```

The three listings are the before-state the deletion proof is read against — the volume must appear
in all three, before and after, as the positive control that the listing works at all.
`gate_pass2_signals.py` refuses to run while `results/prereg_pass2_signals.json` is untracked or
differs from HEAD, and it refuses if `scripts/gate_pass1_window.py` has moved: it EXECUTES that
file's rung logic, held to the sha r1's sealed record pins.

**Read `worst_case_ahead_seconds` on that gate and know what it is.** It is **3 000 s — the SMOKE's
worst case, not the run's.** The full run at the registered 120 s/call would be 11 880 s, far outside
the 6 600 s stop, and that is the design: this registration cannot price the full run, so it buys the
measurement and registers the guard that decides on the rest. `terminate_after_window_seconds` is
the number step 1 puts in `--terminate-after`, and it is the WHOLE stop, because the stop has to
cover a GO.

## 1 — create (the meter starts here)

This line does not train. Four pods have served this base on a 24 GB RTX 4090. The volume pins
EU-RO-1.

```bash
runpodctl pod create --name mp-pass2-signals --gpu-id 'NVIDIA GeForce RTX 4090' --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after '<create + the seconds --pre-create-check left>'
```

**Rung 1 is `costPerHr` in the create RESPONSE, not the price on a listing page.** Over $0.80/h →
delete now and STOP. Under it, record the pod:

```bash
PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --price \
  --pod-id <ID> --created-at <the create response's stamp> \
  --usd-per-hour <costPerHr> --card '<the card the response gave>' \
  --terminate-after '<the stamp you actually gave pod create>'
```

`--terminate-after` is the one number this runbook makes you say twice, because the platform flag is
the only thing that enforces rung 6. `--price` re-derives it and REFUSES a window longer than the
cumulative hard stop allows, forgiving only the registered 60 s of overshoot.

**Print both stamps in UTC, side by side, before you go on.** The last D0 commit and the create must
be in that order, and a commit printed in a local zone against a create printed in UTC has read the
wrong way round twice on this line now:

```bash
git log -1 --format='%cI %h' | ( read t h; echo "last commit  $(date -u -j -f '%Y-%m-%dT%H:%M:%S%z' "${t%:*}${t##*:}" +%Y-%m-%dT%H:%M:%SZ) $h" )
echo "pod create   <the create response's stamp>"
```

## 2 — rung 2, the ssh dead-man (≤ 500 s of this pod's create-elapsed)

`runpodctl ssh info` answers `{"error": "pod not ready"}` until the port mapping is published and
then a JSON object carrying `"ip"` and `"port"`. **Poll on `"port"`, and BOUND the loop by the
CLOCK**, never by an iteration count.

```bash
CEIL=$(python3.11 -c "import json;r=json.load(open('results/prereg_pass2_signals.json'));print(int(next(x['deadline_seconds'] for x in r['kill_clock'] if x['rung']==2)))")
CREATED=$(date -u -j -f '%Y-%m-%dT%H:%M:%S' '<the create stamp, UTC, WITHOUT its Z or +00:00>' +%s)
[ -n "$CREATED" ] || { echo "the create stamp did not parse — fix it before polling"; false; }
echo "polling until $(date -u -r $((CREATED + CEIL)) +%Y-%m-%dT%H:%M:%SZ), rung 2's own ceiling"

runpodctl ssh info <POD_ID>
while [ "$(date -u +%s)" -lt $((CREATED + CEIL)) ]; do
  runpodctl ssh info <POD_ID> | grep -q '"port"' && break
  sleep 5
done
runpodctl ssh info <POD_ID>          # the reading the next command asserts
PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --gate0 --ssh-ok   # it answered
```

If it did not come up, `--gate0` KILLs. A dead pod at rung 2 bills ≈ 578.5 s with the measured
deletion tail, well inside the 3 600 s the recovery clause allows.

## 3 — stage and launch, with the GO path prepared

The pack pins the CURRENT parser sha AND the pass-2 module's, so the handshake refuses a stale
checkout by design — before the model is loaded, which is 450 s and about $0.10 earlier than
`check_requests` would. The repo has no remote; the transport is a git bundle.

**zsh does not word-split an unquoted variable holding ssh options.** Spell every flag literally.

```bash
git bundle create /tmp/market-pulse-pass2-signals.bundle HEAD
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> /tmp/market-pulse-pass2-signals.bundle \
  scripts/pass2_pod_runner.py scripts/pass1_fewshot_pod_runner.py \
  scripts/reader_v5_pod_runner.py scripts/reader_v4_pod_runner.py \
  root@<HOST>:/workspace/
```

```bash
ssh -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -p <PORT> root@<HOST>
# on the pod:
cd /workspace && rm -rf repo && git clone -q market-pulse-pass2-signals.bundle repo
cd repo && git rev-parse HEAD && git status --short      # equals the Mac's HEAD, empty
ls -l results/pass2_pack.json                            # the pack arrived with the bundle
ls -d /workspace/venv /workspace/hf && du -sh /workspace/hf   # the volume is warm, or STOP

# FIRST POD of this registration
rm -rf /workspace/run && mkdir -p /workspace/run
ls /workspace/run                                        # empty — the proof, not the hope
```

**On a RE-CREATION** — allowed only for a death at rungs 1–3, so the out-file cannot exist yet — the
clocks of the dead pod must go and nothing else can be there:

```bash
# RE-CREATION ONLY — never on the first pod
ls -l /workspace/run
rm -f /workspace/run/launched_at /workspace/run/pod.log /workspace/run/pass2_go
ls /workspace/run                                        # empty: a death before the first reply
```

`launched_at` must go or the gate refuses it as older than this pod; `pod.log` must go or its line
count is a high-water mark the new pod's real progress never rises above; `pass2_go` must go or the
new pod would read a token this attempt never wrote.

The launch is DETACHED, its stdout is the pod log the watch loop tails, and **it stamps rung 3's
anchor in the same command**. The stamp is written by the POD, in the foreground, the instant before
the runner is exec'd — the `;` is load-bearing, an `&&` before an `&` would put the stamp inside the
backgrounded list:

```bash
ssh ... -p <PORT> root@<HOST> \
  'cd /workspace && date -u +%Y-%m-%dT%H:%M:%S+00:00 > /workspace/run/launched_at; \
   HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src nohup \
   /workspace/venv/bin/python -u /workspace/repo/scripts/pass2_pod_runner.py \
     --pack /workspace/repo/results/pass2_pack.json \
     --outdir /workspace/run --repo /workspace/repo \
     --go /workspace/run/pass2_go --go-deadline 600 \
     > /workspace/run/pod.log 2>&1 & echo $!'
```

**`--go-deadline 600` is rung S's own deadline and it is DERIVED, not chosen** — it is rung 5's
liveness period, because the Mac has one liveness period to answer. `tests/test_pass2_signals.py`
greps this line out of this file and asserts it against
`results/prereg_pass2_signals.json::kill_clock` rung 8's `deadline_seconds`.

**The stamp's name on the POD is `launched_at` and its name on the Mac is
`pass2_signals_launched_at`.** They are different on purpose and neither is free to choose:
`--watch`'s own `pull()` copies `<remote-dir>/launched_at` into `results/<LAUNCH_STAMP>`, so the
remote name is fixed by the gate and the local one is this attempt's. A launch command that wrote
the LOCAL name onto the pod would leave rung 3 with no anchor and `--boot` would be a KILL. The tests
grep this file for both names and assert them against the gate's own code.

**The runner answers five units, prints `WAIT`, and blocks.** That is the whole of what this launch
buys. The model stays in the card — `pass1_fewshot_pod_runner.once` hands the second call the client
the first one built — which is why the registration charges the 1 100 s of pre-generation once.

## 4 — the WATCH, entered IMMEDIATELY (rungs 3, 4, 5 and 6), and not left

```bash
PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --watch \
  --ssh root@<HOST> --ssh-port <PORT>
```

**Enter it the moment the launch returns a pid — do not hand-poll `--boot` first.** The loop arms
rung 3 itself on BOTH of its spans: not one reply 450 s after the launch stamp is a KILL it makes,
and so is not one reply at 1 100 s of create-elapsed even when the stamp is fresh.

**This watch returns GO when FIVE units are answered, not 79.** `gate_pass2_signals.legs_of` reports
what the registration has AUTHORISED, and until rung S′ records a GO that is the smoke. Rung 4 prices
the same five: pricing 79 units at the registered 120 s/call would kill this pod at the first poll.

Once it returns GO, record rung 3. **It takes no stamp**: the gate reads the launch anchor out of the
run record and the first reply out of the out-file's own `elapsed_since_start`.

```bash
PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --boot
```

## 4a — rung S′, THE GO/NO-GO ($0 on the Mac, and it is the decision)

```bash
PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --go-no-go
```

It reads the five replies' `seconds` off `results/pass2_signals_v1.jsonl`, computes
`charged_full = max(1.5 × smoke_mean, smoke_max)`, projects
`cumulative_billed_now + 74 × charged_full + 1 300` against the 6 600 s stop, **appends the verdict
to `results/pass2_signals_run.json`, and only then — only on GO — writes
`results/pass2_signals_go.json`.** That order is the guard: the token is what unblocks the pod, so a
token written before the record would be spend authorised by a file nobody wrote a reason into.

**On GO**, ship the token and re-enter the watch. The pod is polling for it every 15 s and its
deadline is 600 s from its last reply:

```bash
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> results/pass2_signals_go.json root@<HOST>:/workspace/run/pass2_go
PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --watch \
  --ssh root@<HOST> --ssh-port <PORT>
```

The second watch owes 79 and the five already in the file are not re-asked — the shipped runner's
own `already_answered` is what skips them, and it REFUSES an out-file carrying an id this pack never
asked.

**On STOP, do nothing to the pod except step 5.** Do not write the token, do not scp anything to
`/workspace/run/pass2_go`, and do not "just try". The five replies on the Mac are the evidence, the
measured rate is the answer, and the remaining 74 return to the operator as a cap-and-rate decision
with a number in front of it. A STOP is a registered outcome of this contract.

## 5 — scp EVERYTHING, then delete, then prove it

Files come back BEFORE the verdict and before the deletion. Every hash is compared on the pod and on
the Mac. One command per artifact, so a failed copy is visible rather than averaged into a wildcard.

```bash
ssh ... -p <PORT> root@<HOST> 'cd /workspace/run && find . -type f | sort | xargs sha256sum'
# LC_ALL=C sha256sum on the pod; shasum -a 256 on the Mac. Same digest, two tools

scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/pass2_signals_v1.jsonl results/pass2_signals_v1.jsonl
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/launched_at results/pass2_signals_launched_at
scp -i $SSHK -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/pod.log results/pass2_signals_pod.log
shasum -a 256 results/pass2_signals_v1.jsonl results/pass2_signals_launched_at \
  results/pass2_signals_pod.log      # THREE for three

runpodctl pod delete <POD_ID>
runpodctl pod list -a                # []
runpodctl serverless list            # [] — nothing was ever created here
runpodctl network-volume list        # the volume, unchanged: the POSITIVE CONTROL

PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --close \
  --deleted-at <the deletion stamp> --outcome '<why this pod ended>'
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass2-signals --step-cap 1.50 \
  --note "pass2-signals, pod deleted"
```

## 6 — rung 7 and the verdict ($0)

```bash
PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --completeness
PYTHONPATH=src python3.11 scripts/score_pass2_signals.py
```

`--completeness` picks its ARM off the recorded go/no-go: 79 units after a GO, 5 after a STOP. It
counts a **RELABELLING** as its own refusal cause, because a reply that rewrote a pass-1 subject is
not a transport failure — it is pass 2 doing the one thing the ADR says it may not.

`score_pass2_signals.py` writes `results/pass2_signals_verdict.json`: bars 1/2/3 through the reader's
own scorer, the per-flagship scorecard citing the pass-1 label of every row it names, the DROP table,
the `subject_doubt` rate by pass-1 label, the v5b comparison row and the cost table.

## What must NOT change

* No edit to `src/market_pulse/prompts.py`, `src/market_pulse/scorer.py`,
  `results/reader_gold_w1_r2.json`, `results/pass1_window_pack.json`, either pass-1 out-file, or
  `scripts/gate_pass1_window.py` — this gate EXECUTES that file's logic and refuses if it moved.
* No raw unfiltered comment in any request. The pack renders the filtered rows and the post; the
  measurement is of the filter.
* No relabelling accepted, however named.
* No bar on the fourteen.
* **No unit beyond the five without rung S′'s RECORDED GO.**
* Never two billing endpoints at once, and never a third pod.
