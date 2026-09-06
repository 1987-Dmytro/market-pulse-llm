# Runbook — iteration 5, the LAST of the five, one pod, ONE leg of two arms

Authority: rulings 03.09 (c), (d), (e), 04.09 (m), (n), (o), 05.09 (q), (r), (s), (t), (u), (v),
**(w)**, **(x)** and **(y)**; `docs/PHASE-promo-pulse-1.md` §6.1 **v14** and §6.5 v12,
`docs/PROCESS.md` «Money» **v2.1**. Iteration 4 was bought on
2026-09-05 and came back INCOMPLETE: **CUDA OOM in `gemma4._norm` on the smoke's LONGEST render**
(`@VARUS_channel:8647`, 14 281 chars — 338 MiB refused at 23.19 of 23.52 GiB), no GO, none of the 80
threads read, $0.6948 of which $0.62 was the Mac waiting out a GO deadline for a pod that was
already dead. Ruling (w): **the instrument does not move, the SERVING does.**
**§2 allows five dev runs and this is the fifth.** A red bar closes S2's question with a number and
the next word is the operator's.
**Nothing below §0a runs until `make check` is green at the HEAD the bundle is cut from — that
HEAD is §0a's second commit, and §0a is where the suite is run.**

What (w) and (x) moved, and it is all serving:
* **the card — a PARAMETER of the record now, not a constant.** `promo_dev_pass.CARDS` is
  `("RTX PRO 4500", "RTX A6000", "L40S")` in (w)2's own order and `offered_price()` takes the FIRST
  with **≥ 32 GB**, stock in **EU-RO-1** and a dearer offer **≤ $0.90/h**. On 2026-09-06 that is
  `RTX PRO 4500`, **32 GB**, gpu-id **`NVIDIA RTX PRO 4500 Blackwell`**, **$0.72/h** secure, stock
  High. The listing carries `RTX PRO 4500 SE` at the same price in another cloud — the match is
  EXACT and the SE row is a different card.
* **`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`** in the launch line (§4). An environment
  variable: it touches no pinned byte and is disclosed in the record's `re_emission`.
* **the runner reports a death where the Mac looks** ((w)3, `acfe360`): a unit's exception becomes
  that unit's ERROR reply in the out-file and the process exits non-zero. `--smoke` reads it as
  «the smoke did not come back» and the pod is deleted AT ONCE — never a second GO deadline.
* **the Mac reads that reply EVERYWHERE it reads replies** ((x)4): `--smoke` through the pod
  runner's `whole_lines` (a torn last line is the scp race and reads as WAITING, never a traceback),
  and `--close-segment`'s rate row, `--project` and `--score` count a dead unit as UNANSWERED
  instead of dying on the `seconds` it never had.
* **`--terminate-after` is the CAP's own minutes** ((x)3), no longer v5b's borrowed 90: at $1.40 on
  a $0.72/h card the cap pays for **116 min** and 90 would have killed a FITS run at $1.08.

Money, the numbers written down BEFORE the smoke can return one:
line **`promo-iter5`**, its own ledger `results/spend_promo_iter5.json` and its own run record
`results/promo_dev_loop_run.json`; cap **$1.40** — the OPERATOR's word of 05.09 16:35 ((w), quoted in
STATUS) and not this script's. Ruling (v) item 2: a paid run is bought under its OWN step line and
`promo-dev-loop` carries no new run — **that line is never named again**; its guard REFUSES (exit 1,
$2.5799 of its own $2.50) and `--register` without `--step` would call it.
Rung 0 on 2026-09-06 at $0.72/h, 83 threads, cap $1.40, priced from this instrument's OWN whole-run
row (`promo_dev40_seconds_per_thread`, 47.6615 s mean / 286.248 s max over iteration 3's 40):
`cheap` (mean, one overhead) **$0.8470, −39.5 %** · `priced` (mean, TWO overheads — one dead-man
recreate) **$0.9028, −35.5 %** · `dear` (max on all 83) **$4.8633, +247 %**, over the cap and issued
**FITS on the mean** by (t)3 — which (r)2 makes this leg's ONLY money gate. Hard stop **7000 s**.
Rungs 1 and 2 stay LIFTED (03.09 (e) item 2): what bounds the money is rung 0 and rung 3
(`--terminate-after`), plus **ONE ledger line per session**.

## 0a — the line's OPENING, the first minutes of THIS paid session
Ruling **(y)** and PROCESS «Money» v2.1: `--register` reads the guard WITH `--step`, and that
reading CREATES and anchors `results/spend_promo_iter5.json` — **the registration IS the opening of
the line**, so it runs here, minutes before the create, and never a session earlier. (x)2's «prep
ends at the committed registration» is WITHDRAWN: the close settles on `own_resources` while its
reference is a balance delta with the volume's drip IN, so the anchor's AGE is the drift and the
5 % band shuts at ≈ 4 h of age (§6). In front of these commands only the start ritual — no
development, and the runbook itself was fixed the session before.
```bash
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --dry-run --part dev
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --register --part dev \
  --step promo-iter5 --cap 1.40                          # FITS shown; this ANCHORS the line
git add results/promo_dev40_prep.json results/prereg_promo_dev_loop.json \
        results/spend_promo_iter5.json && git commit …    # the registration FIRST
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --pack --part dev
git add results/promo_dev40_pack.json && git commit …     # the pack SECOND, and it is its own commit
```
**Two commits, in that order, and it is not a style.** `build_pack()` opens the record through
`committed_registration()`, which runs `git ls-files --error-unmatch` and `git diff HEAD --quiet`
on `results/prereg_promo_dev_loop.json` and raises `SystemExit` on either — so a `--pack` placed
between `--register` and its commit REFUSES on the file `--register` has just rewritten (the
verifier's bite of 06.09, at $0 but with the anchor already live). Git history is the only witness
that both preceded the money.
**`--step promo-iter5` is not optional.** Without it the emitter falls back to `STEP` =
`promo-dev-loop`, whose guard refuses — a loud failure, not a silent mis-pricing, but the command is
written with the step every time. `--register` re-reads the guard's REMAINING, the day's own offer
and `pinned_inputs` from disk (so the runner's new sha lands there by construction); all three drift
([[a_reading_that_outlived_its_state]]).
Then **`make check` at THAT HEAD** ((y)3: its tests read the committed record; it is also the HEAD
§3 cuts the bundle from). The suite is ~12 min — over one call's ceiling — so it runs as `ruff` plus
three slices, each its own command. **Neither the coverage nor the floor is judged by eye**: on
2026-09-05 three green `passed` lines summed to 3900 of 4321 because the slices had stopped covering
the list, and nothing said so. Both are commands here, and the arithmetic is never the operator's:
```bash
ruff check .
test "$(ls tests/test_*.py | wc -l)" -eq "$(for R in '1,60p' '61,145p' '146,$p'; do \
  ls tests/test_*.py | sed -n "$R" | wc -l; done | paste -sd+ - | bc)" \
  && echo 'SLICES COVER THE LIST' || echo 'SLICES DO NOT COVER THE LIST — STOP'
PYTHONPATH=src python3.11 -m pytest -q $(ls tests/test_*.py | sed -n '1,60p')   | tail -1 | tee /tmp/s1
PYTHONPATH=src python3.11 -m pytest -q $(ls tests/test_*.py | sed -n '61,145p') | tail -1 | tee /tmp/s2
PYTHONPATH=src python3.11 -m pytest -q $(ls tests/test_*.py | sed -n '146,$p')  | tail -1 | tee /tmp/s3
S=$(cat /tmp/s1 /tmp/s2 /tmp/s3 | sed -n 's/^\([0-9]*\) passed.*/\1/p' | paste -sd+ - | bc); echo "$S"
[ "$S" -ge 4266 ] && echo 'FLOOR HOLDS' || echo 'BELOW §8 (j) — STOP before the create'
```
The tail slice is OPEN-ENDED (`'146,$p'`), so a grown `tests/` moves the boundary and never drops off
the end. A red or a STOP here costs $0 and the pod does not exist yet — after the create it costs the
pod, and the anchor is already live either way.

## 0 — before the create
```bash
runpodctl pod list -a && runpodctl serverless list        # both [] or STOP
runpodctl gpu list | python3.11 -c "import json,sys; [print(g['displayName'], g['memoryInGb'], g['gpuId'], g['securePricePerHr'], g['communityPricePerHr'], [d for d in g['dataCenterAvailability'] or [] if d['dataCenterId']=='EU-RO-1']) for g in json.load(sys.stdin) if g['displayName'] in ('RTX PRO 4500','RTX A6000','L40S')]"
python3.11 scripts/runpod_guard.py --step promo-iter5 --step-cap 1.40 \
  --note 'promo-iter5, iteration 5 — pod about to be created'
```
The `--note` line is the session's ledger line and it is taken BEFORE the pod exists. The listing is
read for the same two names the registration used: the **`displayName`** it matched on and the
**`gpuId`** §1 types. A card whose price moved above the registered one is a KILL at rung 1 — re-read
rung 0 with `--register` rather than creating against the old number.

## 1 — create, then open the segment
The volume `qw4nwleanc` lives in EU-RO-1 and the registration priced that cloud. **The volume
`mp-srv2` is deleted after c3, not here** (operator 05.09, (q)4).
```bash
REMAINING=<the cycle-3 REMAINING the guard printed in §0, typed from its own line>
STOP_AT=$(python3.11 -c "
import json, datetime as d
rec = json.load(open('results/prereg_promo_dev_loop.json'))
run = json.load(open('results/promo_dev_loop_run.json')) if __import__('pathlib').Path('results/promo_dev_loop_run.json').exists() else {'segments': []}
anchor = d.datetime.fromisoformat(json.load(open('results/spend_promo_iter5.json'))['anchored_at'])
spent = sum(float(one.get('billed_usd') or 0) for one in run['segments']
            if d.datetime.fromisoformat(one['created_at'].replace('Z','+00:00')) >= anchor)
cap = min(float(rec['step']['cap_usd']), $REMAINING)      # the cap RULE at TODAY's remaining
left = cap - spent
seconds = left / float(rec['rung_0']['price']['usd_per_hour']) * 3600
seconds = min(seconds, 60.0 * float(rec['gates']['terminate_after_minutes']))  # the REGISTERED stop
print((d.datetime.now(d.timezone.utc) + d.timedelta(seconds=seconds))
      .strftime('%Y-%m-%dT%H:%M:%SZ'))")
echo "$STOP_AT"                                          # empty is a STOP, never a create
CARD=$(python3.11 -c "import json;print(json.load(open('results/prereg_promo_dev_loop.json'))['rung_0']['price']['card'])")
echo "$CARD"    # the gpu-id THIS record was written on — rung 1 compares the create against it
runpodctl pod create --name mp-promo-iter5 \
  --gpu-id "$CARD" --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after "$STOP_AT"
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --open --part dev --pod-id <ID> \
  --created-at '<the create stamp, UTC ISO8601>' --usd-per-hour <costPerHr> --card "$CARD"
```
**The gpu-id is READ from the committed record, never typed from this page.** `offered_price` picks
the card on the day and rung 1 KILLs a pod whose card is not `rung_0.price.card` — so a registration
re-emitted when `RTX PRO 4500` is out of stock names A6000 instead, and a literal here would KILL a
correctly created pod. Same class as the constant (x)3 removed ([[a_shifted_constant_has_physical_consumers]]).
The `spent` above sums only the segments created at or after **this line's** anchor: the run record
is written at BATCH scale and carries every dev-loop pod since iteration 1, so an unfiltered sum
prices iteration 5 against four runs it did not buy.
A KILL from `--open` means the create response's price or CARD is not the registered one, so the cap
was computed against another number: `runpodctl pod delete <ID>`, `--close-segment` with the outcome,
prove `pod list -a` is `[]`, and STOP.

## 2 — the ssh dead-man, bounded by the CLOCK and never by an iteration count
**500 s** of THIS pod's create-elapsed, READ from the record and never typed
(`results/prereg_promo_dev_loop.json :: gates.ssh_deadman_seconds`, which ruling 03.09 (e) item 1
takes from `results/prereg_pass2_signals_r2.json :: kill_clock[rung 2]` — the PRODUCTION sibling,
six readings 14.5 → 262.5 s). The 180 s this runbook used on 2026-09-03 came from a PROBE and killed
two healthy pods before either could publish a port.
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
listing, then ONE recreate from §1 with `STOP_AT` recomputed — never a third pod (03.09 (e) item 3).

## 3 — stage. The repo has no remote; the transport is a git bundle.
The bundle carries every script the runner imports, so no import closure can go stale:
`promo_dev_pod_runner` → `pass2_pod_runner` → `pass1_fewshot_pod_runner` → `pass1_pod_runner` →
`reader_v4_pod_runner`, and `reader_v5_pod_runner` beside them.
```bash
: "${SSHK:=$HOME/.runpod/ssh/runpodctl-ssh-key}"
git status --short && git bundle create /tmp/market-pulse-promo-iter5.bundle HEAD
scp -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> /tmp/market-pulse-promo-iter5.bundle root@<HOST>:/workspace/
```
On the pod:
```bash
cd /workspace && rm -rf repo && git clone -q market-pulse-promo-iter5.bundle repo
cd repo && git rev-parse HEAD && git status --short     # equals the Mac's HEAD, empty
ls -d /workspace/venv /workspace/hf && du -sh /workspace/hf   # the volume is warm, or STOP
rm -rf /workspace/run && mkdir -p /workspace/run && ls /workspace/run   # empty — the proof
```

## 4 — launch DETACHED, from the CLONE, with the warm volume and the ALLOCATOR on the path
`HF_HOME=/workspace/hf` is load-bearing: without it `google/gemma-4-31b-it` resolves to root's
container disk (30 GB) and 59 GB of weights are re-downloaded on the meter.
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` is ruling (w) item 2's other half — the OOM that
ended iteration 4 refused 338 MiB at 23.19 of 23.52 GiB, which is fragmentation as much as size.
```bash
ssh -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -p <PORT> root@<HOST> \
  'cd /workspace && HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src \
   PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True setsid nohup \
   /workspace/venv/bin/python -u /workspace/repo/scripts/promo_dev_pod_runner.py \
     --pack /workspace/repo/results/promo_dev40_pack.json \
     --out /workspace/run/promo_dev40_iter5.jsonl --repo /workspace/repo \
     --go /workspace/run/promo_go --go-deadline 1800 \
   > /workspace/run/pod.log 2>&1 < /dev/null & echo $!'
```
Watch the PROCESS, not a success-grep:
`ssh ... 'pgrep -fa promo_dev_pod_runner; tail -5 /workspace/run/pod.log'`.
**`pgrep` empty while the smoke is short of its three IS «the smoke did not come back»** — delete at
once, do not sit out the GO deadline. Iteration 4's OOM cost $0.62 of exactly that wait.

## 5 — the smoke, then GO. There is no band gate on this leg (ruling 05.09 (r) item 2).
The smoke is the dev leg's shortest, median and **longest** render by
`results/promo_dev40_prep.json :: corpus.threads[].chars`, named in the registration's
`population.leg_a.smoke` and shipped first by `build_pack`. **The longest is where iteration 4 died,
so the smoke IS the fit proof PHASE §6.5 asks for, at the cost of minutes** — the $0 proof stays a
named debt in PROGRESS and this is what stands in for it.
**The money gate already fired**: rung 0 issued FITS on the mean corner and the cap rides as
`--terminate-after`. The three replies landing IS the GO.
```bash
scp ... root@<HOST>:/workspace/run/promo_dev40_iter5.jsonl results/promo_dev40_iter5.jsonl
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --smoke --part dev \
  --replies results/promo_dev40_iter5.jsonl
```
It prints the branch of the registration's OWN decision table and exits 0 only on «3 replies are
in». **An ERROR reply among them is «the smoke did not come back»** and needs no second reading —
delete the pod at once ((w)3). WAITING is a poll, not a verdict: pair it with the `pgrep` above, and
no runner alive is the same outcome as an error. A torn last line is the scp race and also reads
WAITING — re-fetch and read again ((x)4). A torn line that is NOT the last one is a DAMAGED file and
refuses by name («move it aside and stop»): re-fetch once, and if it stands, the pod is deleted on
the `pgrep` reading like any other death.
A missing unit, or a `finish_reason` that is not the model stopping on its own, is **not** a band
verdict: nothing is written to `promo_go`, the pod is deleted, `--close-segment` records it, the
listing is shown, and the run is PHASE §6.5's INCOMPLETE reading — recorded under its number, never
compared to the bars, re-bought only after the operator's money word. **There is no sixth run under
this phase's §2**, so an incomplete iteration 5 is a STOP and the operator's decision.
```bash
echo '{"verdict": "GO"}' > /tmp/promo_go && scp ... /tmp/promo_go root@<HOST>:/workspace/run/promo_go
```
**Why `--project` is not run here.** Its bands are the DEV loop's absolute dollars (`GO ≤ $0.80 ·
GO-THEN-STOP ≤ $1.20 · NO-GO above`, ruling 03.09 (b)) and its KILL is «the MAX corner over the
cap» — and this leg's max corner is over the cap BY CONSTRUCTION ($4.8633), which rung 0 already
accepts. Applied unchanged it returns KILL on a run this very registration issued as FITS. Ruling
(r)2 keeps the gate that was priced and leaves `project()` and its literals untouched: do not run it.

## 6 — close: fetch, delete, the POST-RUN reading, then settle
The pod appends to the SAME out-file, so the fetch overwrites the smoke-only copy with all 80 units.
```bash
scp ... root@<HOST>:/workspace/run/promo_dev40_iter5.jsonl results/promo_dev40_iter5.jsonl
scp ... root@<HOST>:/workspace/run/pod.log results/promo_dev40_iter5_pod.log
wc -l results/promo_dev40_iter5.jsonl                   # 80 units, or the run was cut
runpodctl pod delete <ID>
runpodctl pod list -a && runpodctl serverless list      # both [] — in the transcript
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --close-segment --part dev \
  --deleted-at '<stamp>' --billed-seconds <create→delete> --outcome '<what landed>' \
  --replies results/promo_dev40_iter5.jsonl
python3.11 scripts/runpod_guard.py --step promo-iter5 --step-cap 1.40 \
  --note 'promo-iter5 POST-RUN reading, the reference the close settles against: pod <ID> <created>Z -> <deleted>Z, <n> billed s, <what landed>'
```
**PHASE v13 §6.1 — the `--note` above is the gate's reference and its moment is load-bearing.** It
is taken AFTER the pod is deleted and **BEFORE any next pod**: `recorded_reading()` takes the line's
LAST OPEN reading as the right-hand side of the tolerance gate, so a reading taken before the pod
refuses for ever (`promo-iter4`'s $0.0097 = 7000 % off) and one taken after a LATER pod carries that
pod's money. `--close-segment` carries `--replies` so the whole-run rate row is written for the next
leg; without it the command says so and writes none.
```bash
EXPECT_MS=$(python3.11 -c "
import json, datetime as d
run = json.load(open('results/promo_dev_loop_run.json'))
anchor = d.datetime.fromisoformat(json.load(open('results/spend_promo_iter5.json'))['anchored_at'])
print(int(1000 * sum(float(one['billed_seconds']) for one in run['segments']
    if d.datetime.fromisoformat(one['created_at'].replace('Z', '+00:00')) >= anchor)))")
echo "$EXPECT_MS"                                        # 0 is a STOP: the filter found no segment
python3.11 scripts/runpod_guard.py --step promo-iter5 --step-cap 1.40 \
  --note 'promo-iter5 settled' --close --tolerance 0.05 \
  --expect-ms "$EXPECT_MS" --until '<an instant after this pod and before any next>'
```
**`--expect-ms` is not optional and `--until` is not either.** Without `--expect-ms`, `complete()`
returns True on any readable walk and RunPod's billing posts 30–40 min late, so a close minutes
after the delete settles the line at a fraction of its cost and freezes it. Without `--until` the
walk is unbounded and swallows every later pod — `promo-holdout` closed at $0.2982 only because its
walk was bounded that way. Billing may REFUSE for hours: that is a delay, not a decision — repeat in
the start ritual of the next session, read-only walk FIRST.
**Known trap, carried OPEN in `docs/plans/promo-pulse-1.PROGRESS.md`:** the settled figure leaves the
always-on kinds out (`own_resources`) while the `--note` reference is a balance delta that includes
them, so the network volume's ≈ $0.0079/h drips into the reference and not into the settlement.
Iteration 4's whole 2.73 % drift was exactly that. The drift is `drip·H / (pods + drip·H)` where `H`
is the hours from the §0a anchor to the post-run `--note` — at $0.85 of pod it passes 5 % at about
six hours. **Under (y) they are ALWAYS the same session** (§0a): `H` is the minutes from the
registration to this `--note`, so the drip is a rounding error here and never a term.

## 7 — the join, K8 and the error table, all $0 and after the pod is gone
The leg is TWO arms in ONE out-file since iteration 4 ((s)3, (t)5, (u)2): **dev-40 carries the bars,
dev-2 is a reading beside them**. `--score` grades ONE arm — its units, its answer key, its part of
the draw — and refuses without `--arm`, because 80 answered units against a 40-row key is a grade of
neither.
```bash
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --score --part dev --iteration 5 \
  --arm dev40 --replies results/promo_dev40_iter5.jsonl        # the BAR
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --score --part dev --iteration 5 \
  --arm dev2  --replies results/promo_dev40_iter5.jsonl        # the READING
python3.11 scripts/grade_promo_signals.py --part dev \
  --gold docs/labels-promo-dev.jsonl \
  --predicted results/promo_dev40_predicted_iter5.jsonl --out results/grade_promo_dev40_iter5.json
```
`--score` prints any unit the run recorded as DEAD and counts it UNANSWERED, never as a parse
failure ((x)4). An INCOMPLETE run (any unanswered registered unit) is PHASE §6.5's case and is not
compared to the bars.

By ruling (w): **iteration 5 is the last of the five.** GREEN on dev-40 → the team lead draws the
holdout-2 reference blind, then the executor fires `promo-holdout2` at ≤ $0.90 and S2 closes on that
second reading. RED → the question is closed red under this registration and the next word is the
operator's. Then «c3» by ruling (l) 2–4 at cap $0.50, and the volume `mp-srv2` is deleted after it.
