# Runbook — `promo-dev-loop` iteration 1 (the BASELINE), one pod, two legs

Authority: ruling 03.09 (c), plan `docs/plans/promo-pulse-1.md` §9 + §9a. The $0 half is DONE and
committed: `results/prereg_promo_dev_loop.json` (rung 0 FITS, dear corner $1.3193 of $2.50) and
`results/promo_dev40_pack.json` (56 units, every sha re-derived on this checkout). **Nothing below
runs until `make check` is green at the HEAD the bundle is cut from.**

Money: cap **$2.50**, floor $2.00, holdout's $0.30 untouchable. Rung 1 refuses a `costPerHr` above
the registered **$0.74**. Rung 3 is the platform's `--terminate-after 90m` — 5 400 s inside the
registered 12 162 s hard stop, $1.11 at the registered price.

## 0 — before the create
```bash
runpodctl pod list -a && runpodctl serverless list      # both [] or STOP
python3.11 scripts/runpod_guard.py                       # the REMAINING the cap was computed from
runpodctl gpu list | grep -A3 '"RTX 4090"'               # the price, read on the day
```

## 1 — create, then rung 1 on the response
```bash
runpodctl pod create --name mp-promo-dev-1 --gpu-id 'NVIDIA GeForce RTX 4090' --gpu-count 1 \
  --network-volume-id qw4nwleanc --container-disk-in-gb 20 --terminate-after 90m \
  --image-name <the image the sibling used> --ports '22/tcp'
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --open --pod-id <ID> \
  --created-at '<the create stamp, UTC ISO8601>' --usd-per-hour <costPerHr> --card '<the card>'
```
A non-zero exit is a KILL: `runpodctl pod delete <ID>`, prove it with `pod list -a`, and STOP.

## 2 — the ssh dead-man, bounded by the CLOCK and never by an iteration count
180 s of THIS pod's create-elapsed (`results/prereg_promo_dev_loop.json :: gates.ssh_deadman_seconds`).
```bash
CREATED=$(date -u -j -f '%Y-%m-%dT%H:%M:%S' '<create stamp without Z>' +%s)
while [ "$(date -u +%s)" -lt $((CREATED + 180)) ]; do
  runpodctl ssh info <ID> | grep -q '"port"' && break; sleep 5
done
runpodctl ssh info <ID>
```
No port by 180 s → delete, prove the listing, recreate (at most twice), then STOP.

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
Then K8 (`scripts/grade_promo_signals.py`) → `results/grade_promo_dev40_iter1.json`, the error table
→ `results/promo_dev40_errors_iter1.json`, and the STOP «iteration 1 read».
