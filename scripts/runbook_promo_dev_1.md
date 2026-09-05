# Runbook — `promo-holdout`, the ONE shot, one pod, ONE leg

Authority: rulings 03.09 (c), (d), (e), 04.09 (m), (n), (o) and **05.09 (q)**; `docs/PHASE-promo-pulse-1.md`
§6.1–6.2 v7. The dev loop is CLOSED — iteration 3 took both bars (subject 0.8714, signal 0.9104) on a
complete reading and ruling (q) item 1 accepted it. What follows spends §8 (e)'s ONE holdout attempt.
**The instrument does not move.** (q) item 2 freezes it as iteration 3 bought it: the holdout's
registration pins `docs/CODEBOOK-promo-signals.md`, `promo_prompts.template_version()`,
`scripts/promo_dev_pod_runner.py` and `src/market_pulse/promo_prompts.py` UNCHANGED, so the shot
measures the instrument that took the dev bar, byte for byte. The near-quote «Шикарно…» and the
codebook-document sync queue BEHIND this run ((k)2 as (q)2 amends it).
**Nothing below runs until `make check` is green at the HEAD the bundle is cut from.**

Money, the numbers written down BEFORE the smoke can return one:
cap **$0.90** — the OPERATOR's word of 05.09 ((q) item 3) and not this script's. The $0.30 fence of
plan §6.1 was an ESTIMATE over the borrowed 23.76 s/thread that (c)5 retired; PHASE v7 §6.1 makes a
fence for a later step an estimate re-priced at that step's registration, on the instrument's OWN
measured pace of the SLOWEST pod it has run on. That row is
`results/measurements.jsonl :: promo_dev40_seconds_per_thread` at **88.772 s mean / 201.967 s max**
(n=3, iteration 3's smoke) — read by `own_rate()`, never typed. The step has spent **$0.00**: it is a
NEW step with its own ledger `results/spend_promo_holdout.json` and its own run record
`results/promo_holdout_run.json`, because `promo-dev-loop` is closed and a closed step cannot carry a
new run's spend. `--terminate-after` is the smallest of the money runway at the cap, the cap RULE
re-read at today's REMAINING, and the registration's own `gates.terminate_after_minutes`.
Rungs 1 and 2 stay LIFTED (ruling 03.09 (e) item 2): what bounds the money is rung 0 (the
registration) and rung 3 (the platform's `--terminate-after`), plus ONE ledger line per session.

## 0a — the $0 half, FIRST in the paid session (ruling (q) 5), COMMITTED before any pod exists
```bash
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --dry-run --part holdout
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --register --part holdout \
  --step promo-holdout --cap 0.90 --gold docs/labels-promo-holdout.jsonl
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --pack --part holdout
git add results/promo_holdout40_prep.json results/prereg_promo_holdout.json \
        results/promo_holdout40_pack.json && git commit …
```
`--register` REFUSES while `docs/labels-promo-holdout.jsonl` is absent and says «gold missing -> no
record»: the record PINS the gold by sha256 and a pin over an absent file pins nothing. The pack
refuses while the registration is uncommitted or dirty (`committed_registration()`), so the
registration is committed FIRST and the pack second — git history is the only witness that both
preceded the money. `--register` is run HERE and not a day earlier: its cap rule re-reads the
guard's REMAINING and its price the day's own offer, and both drift ([[a_reading_that_outlived_its_state]]).

The rung-0 table this produced on a $0 dry contact of 05.09, at REMAINING $1.8312 and $0.74/h:
`cheap` (measured mean, one overhead) **$0.8420, −6.4%** · `priced` (mean, TWO overheads — one
dead-man recreate) **$0.8993, −0.1%** · `dear` (measured max on all 43) **$1.8999, +111%**, over the
cap and issued FITS on the mean by (q)3. **The `priced` corner is a knife edge: ONE recreate after a
dead-man leaves $0.0007 of headroom.** A second pod is therefore not a free retry here — if §2's
dead-man fires, re-read rung 0 before the recreate rather than assuming §1's runway.

## 0 — before the create
```bash
runpodctl pod list -a && runpodctl serverless list      # both [] or STOP
runpodctl gpu list | grep -A3 '"RTX 4090"'              # the price, read on the day
python3.11 scripts/runpod_guard.py --step promo-holdout --step-cap 0.90 \
  --note 'promo-holdout, the one shot — pod about to be created'
```
The `--note` line is the session's ledger line and it is taken BEFORE the pod exists, so the step's
anchor precedes this session's spend.

## 1 — create, then open the segment
The volume `qw4nwleanc` lives in EU-RO-1 and the registration priced that cloud. **This is the last
paid run before `c3`; the volume `mp-srv2` is deleted after c3, not here** (operator 05.09, (q)4).
```bash
REMAINING=<the cycle-3 REMAINING the guard printed in §0, typed from its own line>
STOP_AT=$(python3.11 -c "
import json, datetime as d
rec = json.load(open('results/prereg_promo_holdout.json'))
run = json.load(open('results/promo_holdout_run.json')) if __import__('pathlib').Path('results/promo_holdout_run.json').exists() else {'segments': []}
spent = sum(float(one.get('billed_usd') or 0) for one in run['segments'])
cap = min(float(rec['step']['cap_usd']), $REMAINING)      # the cap RULE at TODAY's remaining
left = cap - spent
seconds = left / float(rec['rung_0']['price']['usd_per_hour']) * 3600
seconds = min(seconds, 60.0 * float(rec['gates']['terminate_after_minutes']))  # the REGISTERED stop
print((d.datetime.now(d.timezone.utc) + d.timedelta(seconds=seconds))
      .strftime('%Y-%m-%dT%H:%M:%SZ'))")
echo "$STOP_AT"                                          # empty is a STOP, never a create
runpodctl pod create --name mp-promo-holdout --gpu-id 'NVIDIA GeForce RTX 4090' --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after "$STOP_AT"
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --open --part holdout --pod-id <ID> \
  --created-at '<the create stamp, UTC ISO8601>' --usd-per-hour <costPerHr> --card '<the card>'
```
A KILL from `--open` means the create response's price is not the registered one, so the cap was
computed against another number: `runpodctl pod delete <ID>`, `--close-segment` with the outcome,
prove `pod list -a` is `[]`, and STOP.

## 2 — the ssh dead-man, bounded by the CLOCK and never by an iteration count
**500 s** of THIS pod's create-elapsed, READ from the record and never typed
(`results/prereg_promo_holdout.json :: gates.ssh_deadman_seconds`, which ruling 03.09 (e) item 1
takes from `results/prereg_pass2_signals_r2.json :: kill_clock[rung 2]` — the PRODUCTION sibling,
six readings 14.5 → 262.5 s). The 180 s this runbook used on 2026-09-03 came from a PROBE and killed
two healthy pods before either could publish a port: a gate below the observed maximum of the span
it measures returns KILL before a measurement exists.
```bash
DEAD=$(python3.11 -c "import json;print(int(json.load(open('results/prereg_promo_holdout.json'))['gates']['ssh_deadman_seconds']))")
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
git status --short && git bundle create /tmp/market-pulse-promo-holdout.bundle HEAD
scp -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> /tmp/market-pulse-promo-holdout.bundle root@<HOST>:/workspace/
```
On the pod:
```bash
cd /workspace && rm -rf repo && git clone -q market-pulse-promo-holdout.bundle repo
cd repo && git rev-parse HEAD && git status --short     # equals the Mac's HEAD, empty
ls -d /workspace/venv /workspace/hf && du -sh /workspace/hf   # the volume is warm, or STOP
rm -rf /workspace/run && mkdir -p /workspace/run && ls /workspace/run   # empty — the proof
```

## 4 — launch DETACHED, from the CLONE, with the warm volume on the path (Dv904)
`HF_HOME=/workspace/hf` is load-bearing: without it `google/gemma-4-31b-it` resolves to root's
container disk (30 GB) and 59 GB of weights are re-downloaded on the meter.
```bash
ssh -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -p <PORT> root@<HOST> \
  'cd /workspace && HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src setsid nohup \
   /workspace/venv/bin/python -u /workspace/repo/scripts/promo_dev_pod_runner.py \
     --pack /workspace/repo/results/promo_holdout40_pack.json \
     --out /workspace/run/promo_holdout40.jsonl --repo /workspace/repo \
     --go /workspace/run/promo_go --go-deadline 1800 \
   > /workspace/run/pod.log 2>&1 < /dev/null & echo $!'
```
Watch the PROCESS, not a success-grep: `ssh ... 'pgrep -fa promo_dev_pod_runner; tail -5 /workspace/run/pod.log'`.

## 5 — the smoke, then the decision table
The smoke is **the holdout's OWN first three units** — its shortest, median and longest render by
`results/promo_holdout40_prep.json :: corpus.threads[].chars`, named in the registration's
`population.leg_a.smoke` and shipped first by `build_pack`. They are not the dev loop's three.
```bash
scp ... root@<HOST>:/workspace/run/promo_holdout40.jsonl results/promo_holdout40.jsonl
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --project --part holdout \
  --replies results/promo_holdout40.jsonl
```
**⛔ The bands `--project` reads are the DEV loop's (`GO ≤ $0.80 · GO-THEN-STOP ≤ $1.20 · NO-GO
above`, ruling 03.09 (b)) and its KILL is «the MAX corner over the cap».** Against a $0.90 cap a
$1.20 NO-GO edge is above the cap, and the holdout's max corner is over the cap BY CONSTRUCTION —
(q)3 already accepts that at rung 0 and issues FITS on the mean with the cap as the hard stop.
Applied unchanged, `--project` returns **KILL** on a run rung 0 registered as FITS. **This is the
open stop in `docs/plans/promo-pulse-1.PROGRESS.md`: the team lead names the holdout's decision
table before this line is run.** Do not run §5's gate under the dev bands.
```bash
echo '{"verdict": "GO"}' > /tmp/promo_go && scp ... /tmp/promo_go root@<HOST>:/workspace/run/promo_go
```

## 6 — close: fetch, delete, settle
The pod appends to the SAME out-file, so the fetch overwrites the smoke-only copy with all 40 units.
It keeps the pod's own name: `--score` in §7 reads it.
```bash
scp ... root@<HOST>:/workspace/run/promo_holdout40.jsonl results/promo_holdout40.jsonl
scp ... root@<HOST>:/workspace/run/pod.log results/promo_holdout40_pod.log
wc -l results/promo_holdout40.jsonl                     # 40 units, or the run was cut
runpodctl pod delete <ID>
runpodctl pod list -a && runpodctl serverless list      # both [] — in the transcript
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --close-segment --part holdout \
  --deleted-at '<stamp>' --billed-seconds <create→delete> --outcome '<what landed>'
EXPECT_MS=$(python3.11 -c "
import json, datetime as d
run = json.load(open('results/promo_holdout_run.json'))
anchor = d.datetime.fromisoformat('<the §0 anchor stamp>'.replace('Z', '+00:00'))
print(int(1000 * sum(float(one['billed_seconds']) for one in run['segments']
    if d.datetime.fromisoformat(one['created_at'].replace('Z', '+00:00')) >= anchor)))")
python3.11 scripts/runpod_guard.py --step promo-holdout --step-cap 0.90 \
  --note 'promo-holdout, pod deleted' --close --tolerance 0.05 --expect-ms "$EXPECT_MS"
```
**The `--close` line runs here because the holdout is ONE shot and this pod is its last** — a
closing entry freezes the ledger and `closing_entry` makes that one-way. If §6.5 records this run as
INCOMPLETE and it must be re-bought under the next number, `--close` is WITHHELD until the reading
that counts, exactly as the dev loop withheld it through iterations 1–3.
**`--expect-ms` is not optional here.** Without it `complete()` returns True on any readable walk
(`runpod_guard.py:566`), and RunPod's billing posts 30–40 min late: a close run minutes after the
delete would settle this step at a fraction of its cost and freeze it. With it, an unlanded walk
REFUSES and the ledger stays OPEN and named, which is the recoverable outcome. Retry after §7; if it
still refuses, carry the step open in PROGRESS with the pod-priced figure from
`results/promo_holdout_run.json :: spent_all_segments_usd`, which is the quotable number either way.

## 7 — the join, K8 and the error table, all $0 and after the pod is gone
```bash
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --score --part holdout \
  --gold docs/labels-promo-holdout.jsonl --replies results/promo_holdout40.jsonl
python3.11 scripts/grade_promo_signals.py --part holdout \
  --gold docs/labels-promo-holdout.jsonl \
  --predicted results/promo_holdout40_predicted.jsonl --out results/grade_promo_holdout40.json
```
`--part holdout` is what makes `strata_of` read the holdout arm of the draw; without it every
holdout thread lands in no stratum and the per-stratum reading is empty. `--score` names its files
`promo_holdout40_predicted.jsonl` and `promo_holdout40_errors.json` — no iteration suffix, because
the holdout has no iteration to number.

By ruling 05.09 (q) items 3 and 5: **END at the reading either way.** Green or red, one complete
reading closes S2's question; a red bar does not move the gate, it answers it with a number. An
INCOMPLETE run (any `parse_failures`, any unanswered registered unit) is PHASE §6.5's case: recorded
under its number, never compared to the bars, re-bought under the NEXT number with the law unmoved.
Then «c3» by ruling (l) 2–4 at cap $0.50, and the volume `mp-srv2` is deleted after it.
