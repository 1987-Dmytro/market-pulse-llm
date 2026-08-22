# Runbook — pass2-signals r2 D1: the 75 threads still owed, at a rate this stack has measured

The order below is the money. `results/prereg_pass2_signals_r2.json` is the law; every deadline here
comes out of it through `scripts/gate_pass2_signals_r2.py`, and **nothing in this file may add a
number the record does not carry**. Where a number appears below it is an illustration of the
instrument's output, never a value to type.

**This is r1's runbook MINUS the go/no-go and PLUS one scp.** r1 bought five threads and rung S′
said STOP; the operator's ruling (з) registers the remainder at the smoke's MAX × the measured
pod-class spread. There is no rung to decide anything mid-session: price → ssh → stage → launch →
`--watch` → scp → delete → rung 7.

**The one new step, and it is the one with money attached.** `results/pass2_signals_r2_v1.jsonl` is
SEEDED with the four replies r1 paid for, and it must be **ON THE POD** before the launch.
`reader_v5_pod_runner.already_answered` reads that file to decide what not to re-ask, and
`check_requests` cannot catch its absence because the renderings match by construction. **The
runner REFUSES to start without it** — `carried()` compares the file's `carried_from` rows against
the pack's list before the model is loaded, so a seed that did not land costs 0 s of generation and
a pod that exits at once. Without that guard it would silently re-buy four threads the registration
forbids re-buying, which is what this step exists to make impossible.

**What the numbers are:**

| | |
|---|---:|
| owed by this pod | **75** of 79 (4 carried) |
| charged | **97 s/thread** — `ceil(58.07 × 1.67)`, the smoke's max × v2's measured pod-class spread |
| generation | 75 × 97 = **7 275 s** |
| pre-generation charged (ssh 500 + stage/launch 150 + load 450) | **1 100 s** |
| overhead | **1 300 s** |
| worst case, all in | **9 675 s = 2.6875 h = $2.15** at $0.80/h |
| cumulative hard stop, platform-held | **11 000 s = $2.4444** of a **$2.50** cap |
| rung 4's knife edge at the charged spans | **114.7 s/thread** |
| the same at r1's MEASURED pre-generation (135 s) | **127.5 s/thread** |
| widest dead pod that still fits | **1 325 s** |
| widest create-elapsed at which a KILL is still recoverable | **1 246.5 s** charged · **2 211.5 s** measured |

**Both knife edges are above the charge and above 58.07**, the slowest pass-2 call ever measured.
That is the whole difference from r1: the rate is known before the create, so no rung has to decide
in the middle of a billing session.

**The first rule:** the meter starts at `pod create` and stops at `pod delete`. Not at ssh, not at
the model load, not at the first reply — a pod bills for existing, and `pod stop` does NOT stop it.
**Delete, never stop.**

**The second rule: you do not poll by hand.** `--watch` is a BLOCKING loop. It copies the out-file
and the pod log back, runs the projection gate on EVERY poll, and KILLS when no new row **and no new
log line** have appeared for 600 s from the LAST EVENT.

**The third rule: a KILL after the first NEW reply CLOSES the session.** One re-creation, for a death
at rungs 1–3 only. The four carried rows are NOT a reply of this session and do not close the clause
— `pre_create` counts rows without a `carried_from` field, and a version that counted every line
would refuse this session's very first create.

**Guard reading at every rung, pasted:**

```bash
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass2-signals-r2 --step-cap 2.50 \
  --note "<what this rung is>"
```

## 0 — before anything exists ($0)

```bash
git status --short                       # clean; the record is COMMITTED or the gate refuses it
ls results/pass2_signals_r2_run.json 2>/dev/null && \
  echo "STOP: a run record exists before the first pod. A test or a driver wrote it -- rung 0 will
        read its fixture pod, find no deleted_at and KILL. Delete it and re-run step 0."
: "${SSHK:=$HOME/.ssh/id_ed25519}"; ls -l "$SSHK"   # every scp/ssh below spells -i "$SSHK"
runpodctl pod create --help | grep -E -- "--gpu-id|--network-volume-id|--container-disk-in-gb|--terminate-after"
PYTHONPATH=src python3.11 scripts/build_pass2_r2_pack.py          # 79 units, 4 carried, 75 owed
PYTHONPATH=src python3.11 scripts/build_pass2_r2_pack.py --seed   # the four rows into the out-file
wc -l results/pass2_signals_r2_v1.jsonl  # 4 — and every one carries `carried_from`
make check                               # green
PYTHONPATH=src python3.11 scripts/gate_pass2_signals_r2.py --pre-create-check
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass2-signals-r2 --step-cap 2.50 \
  --note "pass2-signals-r2, before the create"
runpodctl pod list -a                    # [] — nothing of ours is billing
```

`--pre-create-check` RECORDS its verdict in `results/pass2_signals_r2_run.json`. It prints the
`--terminate-after` window the create must use; it is computed, never typed.

## 1 — create (the meter starts here)

```bash
runpodctl pod create --name mp-pass2-signals-r2 --gpu-id 'NVIDIA GeForce RTX 4090' --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after '<create + the seconds --pre-create-check left>'
```

**Every flag above is r1's, changed only in the pod's name.** `runpodctl pod create` takes
`--gpu-id` / `--gpu-count` / `--network-volume-id` / `--image` / `--container-disk-in-gb` —
`runpodctl pod create --help` is the authority and a camelCase spelling of any of them is rejected
at parse time. **`--terminate-after` is what enforces rung 6**, the platform-held hard stop, and a
create that fails to parse invites a retyped line without it.

Read `costPerHr`, the card and the create stamp back OUT of the response and hand them to the gate.
**Rung 1 refuses a price above $0.80/h and a backstop window longer than the hard stop allows.**

```bash
PYTHONPATH=src python3.11 scripts/gate_pass2_signals_r2.py --price --pod-id <ID> \
  --created-at '<the create stamp, UTC ISO8601>' --usd-per-hour <costPerHr> \
  --card '<the card the response gave>' \
  --terminate-after '<the stamp `pod create` was ACTUALLY given>'
```

## 2 — rung 2, the ssh dead-man (≤ 500 s of this pod's create-elapsed)

`runpodctl ssh info` answers `{"error": "pod not ready"}` until the port mapping is published and
then a JSON object carrying `"ip"` and `"port"`. **Poll on `"port"`, and BOUND the loop by the
CLOCK**, never by an iteration count.

```bash
CEIL=$(python3.11 -c "import json;r=json.load(open('results/prereg_pass2_signals_r2.json'));print(int(next(x['deadline_seconds'] for x in r['kill_clock'] if x['rung']==2)))")
CREATED=$(date -u -j -f '%Y-%m-%dT%H:%M:%S' '<the create stamp, UTC, WITHOUT its Z or +00:00>' +%s)
[ -n "$CREATED" ] || { echo "the create stamp did not parse — fix it before polling"; false; }
echo "polling until $(date -u -r $((CREATED + CEIL)) +%Y-%m-%dT%H:%M:%SZ), rung 2's own ceiling"

runpodctl ssh info <POD_ID>
while [ "$(date -u +%s)" -lt $((CREATED + CEIL)) ]; do
  runpodctl ssh info <POD_ID> | grep -q '"port"' && break
  sleep 5
done
runpodctl ssh info <POD_ID>          # the reading the next command asserts
PYTHONPATH=src python3.11 scripts/gate_pass2_signals_r2.py --gate0 --ssh-ok   # it answered
```

If it did not come up, `--gate0` KILLs. A dead pod at rung 2 bills ≈ 578.5 s with the measured
deletion tail, well inside the 1 246.5 s of create-elapsed the recovery clause allows.

## 3 — stage, SEED THE POD, and launch

The pack pins `prompts.py`, `pass2.py` AND `pass2_r2.py`, so the handshake refuses a stale checkout
before the model is loaded — 450 s and about $0.09 earlier than `check_requests` would. The repo has
no remote; the transport is a git bundle.

**zsh does not word-split an unquoted variable holding ssh options.** Spell every flag literally.

```bash
git bundle create /tmp/market-pulse-pass2-signals-r2.bundle HEAD
scp -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> /tmp/market-pulse-pass2-signals-r2.bundle \
  scripts/pass2_r2_pod_runner.py scripts/pass1_fewshot_pod_runner.py \
  scripts/reader_v5_pod_runner.py scripts/reader_v4_pod_runner.py \
  root@<HOST>:/workspace/
```

```bash
ssh -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -p <PORT> root@<HOST>
# on the pod:
cd /workspace && rm -rf repo && git clone -q market-pulse-pass2-signals-r2.bundle repo
cd repo && git rev-parse HEAD && git status --short      # equals the Mac's HEAD, empty
ls -l results/pass2_r2_pack.json                         # the pack arrived with the bundle
ls -d /workspace/venv /workspace/hf && du -sh /workspace/hf   # the volume is warm, or STOP

# FIRST POD of this registration
rm -rf /workspace/run && mkdir -p /workspace/run
ls /workspace/run                                        # empty — the proof, not the hope
```

**Now the seed, and this is the step that has money on it.** The four carried rows go to the pod's
run directory, and their digest is compared on both sides before the launch:

```bash
scp -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> results/pass2_signals_r2_v1.jsonl \
  root@<HOST>:/workspace/run/pass2_signals_r2_v1.jsonl
shasum -a 256 results/pass2_signals_r2_v1.jsonl
ssh ... -p <PORT> root@<HOST> 'sha256sum /workspace/run/pass2_signals_r2_v1.jsonl; \
  wc -l /workspace/run/pass2_signals_r2_v1.jsonl'        # same digest, 4 lines
```

**Without this file on the pod the runner REFUSES and the pod generates nothing.** It prints the
carried ids and the state it found (`does not exist` / `is empty` / the ids it did find) and exits
before the model is loaded — so the symptom of a failed seed is an immediate exit and a rung-3 KILL
at 451 s, not an over-spend. `already_answered` is what then skips the four.

**On a RE-CREATION** — allowed only for a death at rungs 1–3, so no BOUGHT reply can exist yet — the
dead pod's clocks must go and the seed must be copied again:

```bash
# RE-CREATION ONLY — never on the first pod
ls -l /workspace/run
rm -f /workspace/run/launched_at /workspace/run/pod.log
python3 - <<'PY'   # on the pod: keep the carried rows, drop anything this pod bought
import json, pathlib
p = pathlib.Path('/workspace/run/pass2_signals_r2_v1.jsonl')
rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []
assert not [r for r in rows if not r.get('carried_from')], 'a BOUGHT reply exists — no re-creation'
PY
ls /workspace/run                                        # launched_at and pod.log gone
```

`launched_at` must go or the gate refuses it as older than this pod; `pod.log` must go or its line
count is a high-water mark the new pod's real progress never rises above.

The launch is DETACHED, its stdout is the pod log the watch loop tails, and **it stamps rung 3's
anchor in the same command**. The stamp is written by the POD, in the foreground, the instant before
the runner is exec'd — the `;` is load-bearing, an `&&` before an `&` would put the stamp inside the
backgrounded list:

```bash
ssh ... -p <PORT> root@<HOST> \
  'cd /workspace && date -u +%Y-%m-%dT%H:%M:%S+00:00 > /workspace/run/launched_at; \
   HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src nohup \
   /workspace/venv/bin/python -u /workspace/repo/scripts/pass2_r2_pod_runner.py \
     --pack /workspace/repo/results/pass2_r2_pack.json \
     --outdir /workspace/run --repo /workspace/repo \
     > /workspace/run/pod.log 2>&1 & echo $!'
```

**There is no `--go` and no `--go-deadline`.** r2's runner takes neither; the rate is registered and
the leg is answered in one call.

**The stamp's name on the POD is `launched_at` and its name on the Mac is
`pass2_signals_r2_launched_at`.** They are different on purpose and neither is free to choose:
`--watch`'s own `pull()` copies `<remote-dir>/launched_at` into `results/<LAUNCH_STAMP>`, so the
remote name is fixed by the gate and the local one is this attempt's. A launch command that wrote
the LOCAL name onto the pod would leave rung 3 with no anchor and `--boot` would be a KILL.

## 4 — the WATCH, entered IMMEDIATELY (rungs 3, 4, 5 and 6), and not left

```bash
PYTHONPATH=src python3.11 scripts/gate_pass2_signals_r2.py --watch \
  --pack results/pass2_r2_pack.json --ssh root@<HOST> --ssh-port <PORT>
```

**Enter it the moment the launch returns a pid — do not hand-poll `--boot` first.** The loop arms
rung 3 itself on BOTH of its spans: not one BOUGHT reply 450 s after the launch stamp is a KILL it
makes, and so is not one at 1 100 s of create-elapsed even when the stamp is fresh.

**The carried rows do not count as this pod's work anywhere in this loop.** `fingerprint` and
`leg_state` both filter on `carried_from`, so `answered` starts at 0 with four rows on disk, rung 3
is armed, and the rate rung 4 multiplies by the remainder is THIS pod's. Without that filter rung 3
could never fire — the boot branch is `if not cleared and not answered`.

**This watch returns GO when 75 units have been bought**, which is 79 rows in the file.

Once it returns GO, record rung 3. **It takes no stamp**: the gate reads the launch anchor out of the
run record and the first reply out of the out-file's own `elapsed_since_start`.

```bash
PYTHONPATH=src python3.11 scripts/gate_pass2_signals_r2.py --boot
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass2-signals-r2 --step-cap 2.50 \
  --note "pass2-signals-r2, leg answered"
```

## 5 — scp EVERYTHING, then delete, then prove it

Files come back BEFORE the verdict and before the deletion. Every hash is compared on the pod and on
the Mac. One command per artifact, so a failed copy is visible rather than averaged into a wildcard.

```bash
ssh ... -p <PORT> root@<HOST> 'cd /workspace/run && find . -type f | sort | xargs sha256sum'
# LC_ALL=C sha256sum on the pod; shasum -a 256 on the Mac. Same digest, two tools

scp -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/pass2_signals_r2_v1.jsonl results/pass2_signals_r2_v1.jsonl
scp -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/launched_at results/pass2_signals_r2_launched_at
scp -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> root@<HOST>:/workspace/run/pod.log results/pass2_signals_r2_pod.log
shasum -a 256 results/pass2_signals_r2_v1.jsonl results/pass2_signals_r2_launched_at \
  results/pass2_signals_r2_pod.log      # THREE for three

runpodctl pod delete <POD_ID>
runpodctl pod list -a                # []
runpodctl serverless list            # [] — nothing was ever created here
runpodctl network-volume list        # the volume, unchanged: the POSITIVE CONTROL

PYTHONPATH=src python3.11 scripts/gate_pass2_signals_r2.py --close \
  --deleted-at <the deletion stamp> --outcome '<why this pod ended>'
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass2-signals-r2 --step-cap 2.50 \
  --note "pass2-signals-r2, pod deleted"
```

The copied-back out-file **overwrites the seeded one**, and that is correct: the pod's copy is the
seed plus 75 bought rows, and its carried rows are byte-identical to the ones that were sent. The
digest comparison above is what says so.

## 6 — rung 7 and the verdict ($0)

```bash
PYTHONPATH=src python3.11 scripts/gate_pass2_signals_r2.py --completeness \
  --pack results/pass2_r2_pack.json
PYTHONPATH=src python3.11 scripts/score_pass2_signals_r2.py
```

`--completeness` has ONE arm and **FIVE conditions, all of which must hold**: 79 answered of 79 ·
every `rendering_sha256` matching · unreadable replies ≤ 14 · no unknown id and no duplicate · and
the rows carrying `carried_from` are exactly the four the pack names as carried. The last is new in
r2 and it is registered in `results/prereg_pass2_signals_r2.json::bars.completeness`: a
disagreement means the SEED never reached the pod and those four threads were RE-BOUGHT.

It counts a **RELABELLING** as its own refusal cause, because a reply that rewrote a pass-1 subject
is not a transport failure — it is pass 2 doing the one thing the ADR says it may not. It also
counts every REPORT-ONLY field the tolerant reader could not read, and none of those is a refusal:
that count is the measurement Dv702 bought. A field the parser OVERWROTE for its own reasons is
counted separately — «what could the reader not read» and «what did the reader write» are two
questions and one number answers neither.

`score_pass2_signals_r2.py` writes `results/pass2_signals_r2_verdict.json`: bars 1/2/3 through the
reader's own scorer over all 79 threads, the per-flagship scorecard citing the pass-1 label of every
row it names, the DROP table, the `subject_doubt` rate by pass-1 label, the unreadable-field table,
the v5b comparison row and the cost table — with every rate computed over the 75 rows THIS pod
bought and never over the four carried ones.

## What must NOT change

* No edit to `src/market_pulse/prompts.py`, `src/market_pulse/scorer.py`, `src/market_pulse/pass2.py`,
  `results/reader_gold_w1_r2.json`, `results/pass2_pack.json`, `results/pass2_signals_v1.jsonl`,
  `results/prereg_pass2_signals.json`, `scripts/gate_pass2_signals.py` or
  `scripts/gate_pass1_window.py` — this gate EXECUTES those files' logic and refuses if they moved.
* **The prompt text of `pass2_thread_gm4_v1` may not move a byte.** Four carried replies answer it.
* No re-buy of the four carried threads.
* No raw unfiltered comment in any request.
* No relabelling accepted, however named.
* No bar on the fourteen.
* Never two billing endpoints at once, and never a third pod.
