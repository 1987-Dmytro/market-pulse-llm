# Runbook — `promo-dev-loop` iteration 1 (the BASELINE), one pod, two legs

Authority: ruling 03.09 (c), plan `docs/plans/promo-pulse-1.md` §9 + §9a. The $0 half is DONE and
committed: `results/prereg_promo_dev_loop.json` (rung 0 FITS, dear corner $1.3193 of $2.50) and
`results/promo_dev40_pack.json` (56 units, every sha re-derived on this checkout). **Nothing below
runs until `make check` is green at the HEAD the bundle is cut from.**

Money: cap **$2.50**, floor $2.00, holdout's $0.30 untouchable. Rung 1 refuses a `costPerHr` above
the registered **$0.74**. Rung 3 is the platform stop at the CAP, and `--terminate-after` is a
DATETIME, not a duration (`runpodctl pod create --help`): the value is create + the seconds the cap
buys at the registered price — `results/prereg_promo_dev_loop.json :: rung_0.hard_stop_seconds`,
**12 162.2 s**, read from the record and never typed (ruling 03.09 (d); the old `90m` was 5 400 s,
inside the dear corner's own ≈107 min, and would have cut this run inside its own registration).

## 0 — before the create
```bash
runpodctl pod list -a && runpodctl serverless list      # both [] or STOP
python3.11 scripts/runpod_guard.py                       # the REMAINING the cap was computed from
runpodctl gpu list | grep -A3 '"RTX 4090"'               # the price, read on the day
```

## 1 — create, then rung 1 on the response
Every flag is the sibling's (`scripts/runbook_pass2_signals_r2.md:89`), changed only in the name and
the stop; the volume `qw4nwleanc` lives in EU-RO-1 and the registration priced that cloud.
```bash
STOP_AT=$(python3.11 -c "import json,datetime as d; s=json.load(open('results/prereg_promo_dev_loop.json'))['rung_0']['hard_stop_seconds']; print((d.datetime.now(d.timezone.utc)+d.timedelta(seconds=s)).strftime('%Y-%m-%dT%H:%M:%SZ'))")
runpodctl pod create --name mp-promo-dev-1 --gpu-id 'NVIDIA GeForce RTX 4090' --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after "$STOP_AT"
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --open --pod-id <ID> \
  --created-at '<the create stamp, UTC ISO8601>' --usd-per-hour <costPerHr> --card '<the card>'
```
A non-zero exit is a KILL: `runpodctl pod delete <ID>`, prove it with `pod list -a`, and STOP.

## 2 — the ssh dead-man, bounded by the CLOCK and never by an iteration count
**500 s** of THIS pod's create-elapsed, READ from the record and never typed
(`results/prereg_promo_dev_loop.json :: gates.ssh_deadman_seconds`, which ruling 03.09 (e) item 1
takes from `results/prereg_pass2_signals_r2.json :: kill_clock[rung 2]` — the PRODUCTION sibling,
six readings 14.5 → 262.5 s). The 180 s this runbook used on 2026-09-03 came from a PROBE and killed
two healthy pods before either could publish a port: a gate below the observed maximum of the span
it measures returns KILL before a measurement exists.
```bash
DEAD=$(python3.11 -c "import json;print(int(json.load(open('results/prereg_promo_dev_loop.json'))['gates']['ssh_deadman_seconds']))")
CREATED=$(date -u -j -f '%Y-%m-%dT%H:%M:%S' '<create stamp without Z>' +%s)
while [ "$(date -u +%s)" -lt $((CREATED + DEAD)) ]; do
  runpodctl ssh info <ID> | grep -q '"port"' && break; sleep 5
done
runpodctl ssh info <ID>
```
No port by the deadline → delete, prove the listing, ONE recreate, then STOP — never a third pod
(ruling 03.09 (e) item 3). The dead-man is a LIVENESS check only.

## 3 — stage. The repo has no remote; the transport is a git bundle.
```bash
: "${SSHK:=$HOME/.runpod/ssh/runpodctl-ssh-key}"
git bundle create /tmp/market-pulse-promo-dev-1.bundle HEAD
scp -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> /tmp/market-pulse-promo-dev-1.bundle results/promo_dev40_pack.json \
  scripts/promo_dev_pod_runner.py scripts/pass2_pod_runner.py scripts/pass1_fewshot_pod_runner.py \
  scripts/reader_v5_pod_runner.py scripts/reader_v4_pod_runner.py root@<HOST>:/workspace/
```
On the pod:
```bash
cd /workspace && rm -rf repo && git clone -q market-pulse-promo-dev-1.bundle repo
cd repo && git rev-parse HEAD && git status --short     # equals the Mac's HEAD, empty
ls -d /workspace/venv /workspace/hf && du -sh /workspace/hf   # the volume is warm, or STOP
rm -rf /workspace/run && mkdir -p /workspace/run && ls /workspace/run   # empty — the proof
cp /workspace/promo_dev40_pack.json /workspace/run/
```

## 4 — launch DETACHED. The harness kills its own background children (Dv904).
```bash
ssh ... -p <PORT> root@<HOST> 'cd /workspace && setsid nohup /workspace/venv/bin/python \
  /workspace/promo_dev_pod_runner.py --pack /workspace/run/promo_dev40_pack.json \
  --out /workspace/run/promo_dev40_iter1.jsonl --repo /workspace/repo \
  --go /workspace/run/promo_go --go-deadline 1800 > /workspace/run/pod.log 2>&1 < /dev/null &'
```
Watch the PROCESS, not a success-grep: `ssh ... 'pgrep -fa promo_dev_pod_runner; tail -5 /workspace/run/pod.log'`.

## 5 — the smoke, then the decision table (ruling 03.09 (b), quoted, not moved)
Three replies land (`@msuaaaa:6523`, `@VARUS_channel:9006`, `@VARUS_channel:6009`), then the runner
blocks on the GO. Copy them back, read the rate, project 40 threads:
* **≤ $0.80** → GO, run iteration 1 now.
* **$0.80–$1.20** → GO, then STOP with the error table.
* **> $1.20** → NO GO: write no token, delete the pod, show the listings, STOP.

```bash
scp ... root@<HOST>:/workspace/run/promo_dev40_iter1.jsonl results/
echo '{"verdict": "GO"}' > /tmp/promo_go && scp ... /tmp/promo_go root@<HOST>:/workspace/run/promo_go
```
The measured rate goes to `results/measurements.jsonl` under this instrument's OWN name and the
projection names it — the borrow is never reused after the smoke.

## 6 — close: fetch, delete, settle
```bash
scp ... root@<HOST>:/workspace/run/promo_dev40_iter1.jsonl results/promo_dev40_predicted_iter1.jsonl
runpodctl pod delete <ID>
runpodctl pod list -a && runpodctl serverless list      # both [] — in the transcript
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --close-segment --deleted-at '<stamp>' \
  --billed-seconds <create→delete> --outcome '<what landed>'
python3.11 scripts/runpod_guard.py --step promo-dev-loop --step-cap 2.50 \
  --note 'promo-dev-loop, pod deleted' --close --tolerance 0.05
```
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
