# Runbook — `promo-dev-loop` iteration 1 (the BASELINE), one pod, two legs

Authority: rulings 03.09 (c), (d) and (e); plan `docs/plans/promo-pulse-1.md` §9 + §9a. The $0 half
is DONE and committed: `results/prereg_promo_dev_loop.json` (rung 0 FITS, dear corner $1.3193 of
$2.50) and `results/promo_dev40_pack.json` (56 units, every sha re-derived on this checkout).
**Nothing below runs until `make check` is green at the HEAD the bundle is cut from.**

Money: cap **$2.50**, floor $2.00, holdout's $0.30 untouchable. Ruling 03.09 (e) item 2 LIFTS rungs
1 and 2 for this step: what bounds the money is rung 0 (the registration) and rung 3 (the platform's
`--terminate-after`), plus ONE ledger line per session — `--note` at create, `--close` at delete.
`--terminate-after` is a DATETIME (`runpodctl pod create --help`) and is derived from the cap LESS
what this step has already spent (`results/promo_dev_loop_run.json`, $0.089622 on 2026-09-03), so a
recreate never gets a fresh full-cap runway. `--open`/`--close-segment` still run: they are the only
thing that opens and prices a segment, and their rung-1 verdict is now a reading, not a ladder.

## 0 — before the create
```bash
runpodctl pod list -a && runpodctl serverless list      # both [] or STOP
runpodctl gpu list | grep -A3 '"RTX 4090"'              # the price, read on the day
python3.11 scripts/runpod_guard.py --step promo-dev-loop --step-cap 2.50 \
  --note 'promo-dev-loop iteration 1 — pod about to be created'
```
The `--note` line is the session's ledger line and it is taken BEFORE the pod exists, so the step's
anchor precedes this session's spend. It cannot precede the $0.089622 of 2026-09-03 — that money was
spent before any ledger for this step was opened, and it is carried by the run record instead.

## 1 — create, then open the segment
Every flag is the sibling's (`scripts/runbook_pass2_signals_r2.md:89`), changed only in the name and
the stop; the volume `qw4nwleanc` lives in EU-RO-1 and the registration priced that cloud.
```bash
STOP_AT=$(python3.11 -c "
import json, datetime as d
rec = json.load(open('results/prereg_promo_dev_loop.json'))
run = json.load(open('results/promo_dev_loop_run.json'))
spent = sum(float(one.get('billed_usd') or 0) for one in run['segments'])
left = float(rec['step']['cap_usd']) - spent
print((d.datetime.now(d.timezone.utc)
       + d.timedelta(seconds=left / float(rec['rung_0']['price']['usd_per_hour']) * 3600)
      ).strftime('%Y-%m-%dT%H:%M:%SZ'))")
echo "$STOP_AT"                                          # empty is a STOP, never a create
runpodctl pod create --name mp-promo-dev-1 --gpu-id 'NVIDIA GeForce RTX 4090' --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after "$STOP_AT"
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --open --pod-id <ID> \
  --created-at '<the create stamp, UTC ISO8601>' --usd-per-hour <costPerHr> --card '<the card>'
```
A KILL from `--open` means the create response's price is not the registered one, so the cap was
computed against another number: `runpodctl pod delete <ID>`, `--close-segment` with the outcome,
prove `pod list -a` is `[]`, and STOP.

## 2 — the ssh dead-man, bounded by the CLOCK and never by an iteration count
**500 s** of THIS pod's create-elapsed, READ from the record and never typed
(`results/prereg_promo_dev_loop.json :: gates.ssh_deadman_seconds`, which ruling 03.09 (e) item 1
takes from `results/prereg_pass2_signals_r2.json :: kill_clock[rung 2]` — the PRODUCTION sibling,
six readings 14.5 → 262.5 s). The 180 s this runbook used on 2026-09-03 came from a PROBE and killed
two healthy pods before either could publish a port: a gate below the observed maximum of the span
it measures returns KILL before a measurement exists.
```bash
DEAD=$(python3.11 -c "import json;print(int(json.load(open('results/prereg_promo_dev_loop.json'))['gates']['ssh_deadman_seconds']))")
: "${DEAD:?the deadline is unreadable — an unreadable dead-man is a ZERO-second one, so STOP}"
CREATED=$(date -u -j -f '%Y-%m-%dT%H:%M:%S' '<create stamp without Z>' +%s)
while [ "$(date -u +%s)" -lt $((CREATED + DEAD)) ]; do
  runpodctl ssh info <ID> | grep -q '"port"' && break; sleep 5
done
runpodctl ssh info <ID>
```
No port by the deadline → `runpodctl pod delete <ID>`, **`--close-segment` for that pod** (nothing
else writes its bill, and the next `--open` refuses while a segment is still open), prove the
listing, then ONE recreate from §1 with `STOP_AT` recomputed — never a third pod (ruling 03.09 (e)
item 3). The dead-man is a LIVENESS check only.

## 3 — stage. The repo has no remote; the transport is a git bundle.
The bundle carries every script the runner imports, so nothing else is copied and no import closure
can go stale: `promo_dev_pod_runner` → `pass2_pod_runner` → `pass1_fewshot_pod_runner` →
`pass1_pod_runner` → `reader_v4_pod_runner`, and `reader_v5_pod_runner` beside them.
```bash
: "${SSHK:=$HOME/.runpod/ssh/runpodctl-ssh-key}"
git status --short && git bundle create /tmp/market-pulse-promo-dev-1.bundle HEAD
scp -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> /tmp/market-pulse-promo-dev-1.bundle root@<HOST>:/workspace/
```
On the pod:
```bash
cd /workspace && rm -rf repo && git clone -q market-pulse-promo-dev-1.bundle repo
cd repo && git rev-parse HEAD && git status --short     # equals the Mac's HEAD, empty
ls -d /workspace/venv /workspace/hf && du -sh /workspace/hf   # the volume is warm, or STOP
rm -rf /workspace/run && mkdir -p /workspace/run && ls /workspace/run   # empty — the proof
```

## 4 — launch DETACHED, from the CLONE, with the warm volume on the path (Dv904)
`HF_HOME=/workspace/hf` is load-bearing: without it `google/gemma-4-31b-it` resolves to root's
container disk (30 GB) and 59 GB of weights are re-downloaded on the meter. The sibling's line,
changed only in the runner and its flags (`scripts/runbook_pass2_signals_r2.md:205`).
```bash
ssh -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -p <PORT> root@<HOST> \
  'cd /workspace && HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src setsid nohup \
   /workspace/venv/bin/python -u /workspace/repo/scripts/promo_dev_pod_runner.py \
     --pack /workspace/repo/results/promo_dev40_pack.json \
     --out /workspace/run/promo_dev40_iter1.jsonl --repo /workspace/repo \
     --go /workspace/run/promo_go --go-deadline 1800 \
   > /workspace/run/pod.log 2>&1 < /dev/null & echo $!'
```
Watch the PROCESS, not a success-grep: `ssh ... 'pgrep -fa promo_dev_pod_runner; tail -5 /workspace/run/pod.log'`.

## 5 — the smoke, then the decision table (ruling 03.09 (b), quoted, not moved)
Three replies land (`@msuaaaa:6523`, `@VARUS_channel:9006`, `@VARUS_channel:6009`), then the runner
blocks on the GO. Copy them back and let the gate read its own number — the projection is `corner()`
at the MEASURED rate, in the units the bands were written in, and it writes the rate to
`results/measurements.jsonl` under this instrument's own name.
```bash
scp ... root@<HOST>:/workspace/run/promo_dev40_iter1.jsonl results/promo_dev40_iter1.jsonl
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --project \
  --replies results/promo_dev40_iter1.jsonl
```
`GO` (≤ $0.80) → run iteration 1 now · `GO-THEN-STOP` ($0.80–$1.20) → run it, then STOP with the
error table · `NO-GO` (> $1.20) or `KILL` (the max corner is over the cap) → write no token, delete
the pod, close the segment, show the listings, STOP.
```bash
echo '{"verdict": "GO"}' > /tmp/promo_go && scp ... /tmp/promo_go root@<HOST>:/workspace/run/promo_go
```

## 6 — close: fetch, delete, settle
The pod appends to the SAME out-file, so the fetch overwrites the smoke-only copy with all 56 units.
It keeps the pod's own name: `--score` in §7 reads it and writes the predicted file, and a fetch that
renamed it here would be overwritten by that write after the pod is gone.
```bash
scp ... root@<HOST>:/workspace/run/promo_dev40_iter1.jsonl results/promo_dev40_iter1.jsonl
scp ... root@<HOST>:/workspace/run/pod.log results/promo_dev40_iter1_pod.log
wc -l results/promo_dev40_iter1.jsonl                   # 56 units, or the run was cut
runpodctl pod delete <ID>
runpodctl pod list -a && runpodctl serverless list      # both [] — in the transcript
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --close-segment --deleted-at '<stamp>' \
  --billed-seconds <create→delete> --outcome '<what landed>'
EXPECT_MS=$(python3.11 -c "
import json, datetime as d
run = json.load(open('results/promo_dev_loop_run.json'))
anchor = d.datetime.fromisoformat('<the §0 anchor stamp>'.replace('Z', '+00:00'))
print(int(1000 * sum(float(one['billed_seconds']) for one in run['segments']
    if d.datetime.fromisoformat(one['created_at'].replace('Z', '+00:00')) >= anchor)))")
python3.11 scripts/runpod_guard.py --step promo-dev-loop --step-cap 2.50 \
  --note 'promo-dev-loop, pod deleted' --close --tolerance 0.05 --expect-ms "$EXPECT_MS"
```
**`--expect-ms` is not optional here.** Without it `complete()` returns True on any readable walk
(`runpod_guard.py:566`), and RunPod's billing posts 30–40 min late: a close run minutes after the
delete would settle this step at a fraction of its cost and freeze it — «a PARTIAL walk is a third
state and settling on it freezes a number that is never re-derived», the guard's own words. With it,
an unlanded walk REFUSES and the ledger stays OPEN and named, which is the recoverable outcome.
Retry after §7; if it still refuses, carry the step open in PROGRESS with the pod-priced figure from
`results/promo_dev_loop_run.json :: spent_all_segments_usd`, which is the quotable number either way.

## 7 — the join, K8 and the error table, all $0 and after the pod is gone
The pod writes the reader family's rows; K8 scores the GOLD shape. `--score` joins them, keeps the
`extractor_version` of every row, counts the answers that never parsed by cause, and writes the
error table (the grade's own numbers, the top-10 subject misses with the gold row beside the
model's, the Jaccard per thread).
```bash
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --score \
  --replies results/promo_dev40_iter1.jsonl --iteration 1
python3.11 scripts/grade_promo_signals.py \
  --predicted results/promo_dev40_predicted_iter1.jsonl --out results/grade_promo_dev40_iter1.json
```
Iteration 1 is the BASELINE: an unparseable answer is COUNTED, never repaired — answer repair is a
knob ruling 03.09 (c) item 3 gives iterations 2–5, each a new `extractor_version`.

Then the STOP «iteration 1 read» in `docs/plans/promo-pulse-1.PROGRESS.md`.
