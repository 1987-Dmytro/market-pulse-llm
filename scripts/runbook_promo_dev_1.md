# Runbook — holdout-2, the ONE shot on the instrument FROZEN as iteration 5 bought it; one pod, ONE leg of ONE arm

Authority: rulings 05.09 (q), (r), (s) item 3 (b), (t), (v), (w), (x), 06.09 (y) and **(z)**;
`docs/PHASE-promo-pulse-1.md` §2 and §6.1–6.2 **v16** and §6.5 v12, `docs/PROCESS.md` «Money» **v2.1**.
Iteration 5 was bought on 2026-09-06 and came back **GREEN on a COMPLETE reading** — 80/80 units,
0 unparsed, dev-40 subject **0.8857** · signal **0.8667** (`results/grade_promo_dev40_iter5.json`),
dev-2 0.8883 / 0.8296 read beside it. Ruling (z) item 3: **the instrument is FROZEN as bought** — the
four pins of `d598573` (the codebook, the template it renders, `src/market_pulse/promo_prompts.py`,
`scripts/promo_dev_pod_runner.py`), byte for byte, and **a pin that moves before the shot is a STOP.**
**§8 (e) spends the holdout ONCE.** A complete reading closes S2's question green or red on this
second population; an incomplete one is PHASE §6.5's case, recorded under its number and re-bought
under the next number only after the operator's money word.
**Nothing below §0a runs until `make check` is green at the HEAD the bundle is cut from — that
HEAD is §0a's second commit, and §0a is where the suite is run.**

What this shot inherits, and what the executor changed at $0 in «holdout-2 prep» (ruling (z) item 4):
* **the population is the SECOND draw** (`results/promo_threads_draw_2.json`, ruling (s) item 3 (b):
  seed 42 over the PRODUCT's population — the frozen v1 678 minus the channels registry r2 has on
  `collect: false` minus the 80 threads the first draw spent). `--part holdout2` binds it: its
  `holdout` arm, 20 + 20, its own gold `docs/labels-promo-holdout2.jsonl` (the team lead's, BLIND,
  112 rows over the 40 threads, sha `5525ddf1…`, committed by path 06.09 — (z) addendum 2, PHASE v16
  §2), its own line `promo-holdout2`, its own files `results/promo_holdout2_*` and
  `results/prereg_promo_holdout2.json`. Every decision field of the record is written for THIS leg by
  name (`by_part`) and a leg the table has no text for is REFUSED, never handed a neighbour's.
* **the serving is iteration 5's**, disclosed as fields and never constants: the card is a
  PARAMETER (`offered_price()` — the FIRST of `RTX PRO 4500` / `RTX A6000` / `L40S` with ≥ 32 GB,
  stock in EU-RO-1 and a dearer offer ≤ $0.90/h; on 2026-09-06 `RTX PRO 4500`, 32 GB, gpu-id
  `NVIDIA RTX PRO 4500 Blackwell`, $0.72/h secure, stock High — the `SE` row is a different card),
  `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` in the launch line (§4), the pinned runner's
  ERROR reply on a death ((w)3), `--terminate-after` = the CAP's own minutes ((x)3).
* **the Mac reads a death by the `exception` field** ((y)4 risk 2, fixed): a unit whose exception
  carried an EMPTY message used to read as ANSWERED in `--smoke`, the rate row and `--score`; `died()`
  is the one spelling every reader keys on. The runner does not move for it.
* **`--close-segment` sums THIS line's segments** ((y)4 risk 3, fixed): the segments created at or
  after the line's anchor (`anchored_at` of the ledger the committed registration names) — iteration 5
  printed a false `verdict OVER` over seven pods; the shot's own run record starts empty anyway.
* the longest holdout-2 render is **10 529 chars** (`results/promo_holdout2_prep.json`), under the
  14 281 that iteration 5 answered on this card in 313.9 s — the fit is iteration 5's own reading.

Money, the numbers written down BEFORE the smoke can return one — **and PHASE §6.2's STOP notice
to the operator, given BEFORE this session is opened** (ruling (z) item 4: the notice IS the dry
run's figure): line **`promo-holdout2`**, its own ledger `results/spend_promo_holdout2.json` and its
own run record `results/promo_holdout2_run.json`; cap **$0.90** — the operator's FENCE of PHASE §6.1
(«holdout-2 ≤ $0.90 on the measured pace»), an ESTIMATE re-priced at `--register` on the day, never
this script's number. Rung 0 read-only on 2026-09-06 at $0.72/h, 43 threads, cap $0.90, priced from
this instrument's OWN whole-run row (`promo_dev40_seconds_per_thread`, **53.6254 s mean / 313.867 s
max over iteration 5's 80** on the 32 GB card — the slowest pod seen): `cheap` (mean, one overhead)
**$0.5170, −42.6 %** · `priced` (mean, TWO overheads — one dead-man recreate) **$0.5728, −36.4 %** ·
`dear` (max on all 43) **$2.8109, +212 %**, over the cap and issued **FITS on the mean** by (t)3 —
which (r)2 makes this leg's ONLY money gate. Hard stop **4500 s = 75 min**. A `--register` that
loses FITS on the day (the offer moved, the card is gone) ENDS the session before any create — the
cap is the operator's word and nothing here substitutes for it. Cycle 3: ceiling **$10.00**
((z) addendum), REMAINING **$2.5821** at the 14:21Z close of `promo-iter5`; the volume drips
≈ $0.24/day. Rungs 1 and 2 stay LIFTED (03.09 (e) item 2): what bounds the money is rung 0 and
rung 3 (`--terminate-after`), plus **ONE ledger line per session**.

## 0a — the line's OPENING, the first minutes of THIS paid session
Ruling **(y)** and PROCESS «Money» v2.1: `--register` reads the guard WITH `--step`, and that
reading CREATES and anchors `results/spend_promo_holdout2.json` — **the registration IS the opening
of the line**, so it runs here, minutes before the create, and never a session earlier (the close
settles on `own_resources` while its reference is a balance delta with the volume's drip IN, so the
anchor's AGE is the drift and the 5 % band shuts at ≈ 4 h of age, §6). In front of these commands
only the start ritual — no development. **The gold must be COMMITTED before the first line**: the
registration pins it by sha256 and `--register` REFUSES while `docs/labels-promo-holdout2.jsonl`
is absent — a pin over an absent file pins nothing.
```bash
git ls-files --error-unmatch docs/labels-promo-holdout2.jsonl && git diff HEAD --quiet -- docs/labels-promo-holdout2.jsonl \
  && echo 'GOLD COMMITTED' || echo 'GOLD NOT COMMITTED — STOP: a team-lead file the executor never edits'
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --dry-run --part holdout2
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --register --part holdout2 \
  --step promo-holdout2 --cap 0.90                       # FITS shown; this ANCHORS the line
python3.11 -c "
import json, subprocess
new = json.load(open('results/prereg_promo_holdout2.json'))
old = json.loads(subprocess.check_output(['git', 'show', 'd598573:results/prereg_promo_dev_loop.json']))
pins = ['docs/CODEBOOK-promo-signals.md', 'src/market_pulse/promo_prompts.py', 'scripts/promo_dev_pod_runner.py']
moved = [p for p in pins if new['pinned_inputs'][p] != old['pinned_inputs'][p]]
moved += ['template'] if new['law']['template_sha256'] != old['law']['template_sha256'] else []
print('THE FOUR PINS HOLD — the instrument is d598573, byte for byte' if not moved else f'PIN MOVED — STOP: {moved}')"
git add results/promo_holdout2_prep.json results/prereg_promo_holdout2.json \
        results/spend_promo_holdout2.json && git commit …  # the registration FIRST
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --pack --part holdout2
git add results/promo_holdout2_pack.json && git commit …  # the pack SECOND, and it is its own commit
```
**The pin check is the §6.2 clause as a command**: the four instrument pins of THIS record equal
those of the dev-bar registration at `d598573` or the shot is a STOP before any anchor is spent.
**Two commits, in that order, and it is not a style.** `build_pack()` opens the record through
`committed_registration()`, which runs `git ls-files --error-unmatch` and `git diff HEAD --quiet`
on `results/prereg_promo_holdout2.json` and raises `SystemExit` on either — so a `--pack` placed
between `--register` and its commit REFUSES on the file `--register` has just rewritten (the
verifier's bite of 06.09). Git history is the only witness that both preceded the money.
**`--part holdout2` is the load-bearing flag; `--step promo-holdout2 --cap 0.90` are written
beside it every time.** `HOLDOUT2_FILES` binds the step and the gold by construction. A `--step
promo-holdout2` typed WITHOUT `--part holdout2` is the DEV leg under the holdout-2 line — 80 dev
threads, `results/prereg_promo_dev_loop.json` — and `--register` would anchor
`spend_promo_holdout2.json` over the wrong population and overwrite the frozen iteration-5 record
before `committed_registration()` refuses the pack: $0, but a live anchor and a `git checkout` of the
record. The cross-leg `--step` refusal is NAMED in PROGRESS, not built. `--register --part holdout2`
WITHOUT `--cap` REFUSES before the guard is read: the cap is the operator's number, never the dev
loop's derived rule. `--register` re-reads the guard's REMAINING, the day's own offer and
`pinned_inputs` from disk; all three drift ([[a_reading_that_outlived_its_state]]).
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
python3.11 scripts/runpod_guard.py --step promo-holdout2 --step-cap 0.90 \
  --note 'promo-holdout2, the one shot — pod about to be created'
```
The `--note` line is the session's ledger line and it is taken BEFORE the pod exists. The listing is
read for the same two names the registration used: the **`displayName`** it matched on and the
**`gpuId`** §1 types. A card whose price moved above the registered one is a KILL at rung 1 — re-read
rung 0 with `--register` rather than creating against the old number.

## 1 — create, then open the segment
The volume `qw4nwleanc` lives in EU-RO-1 and the registration priced that cloud. **The volume
`mp-srv2` is deleted after c3, not here** (operator 05.09, (q)4; (z)5).
```bash
REMAINING=<the cycle-3 REMAINING the guard printed in §0, typed from its own line>
STOP_AT=$(python3.11 -c "
import json, datetime as d
rec = json.load(open('results/prereg_promo_holdout2.json'))
run = json.load(open('results/promo_holdout2_run.json')) if __import__('pathlib').Path('results/promo_holdout2_run.json').exists() else {'segments': []}
anchor = d.datetime.fromisoformat(json.load(open('results/spend_promo_holdout2.json'))['anchored_at'])
spent = sum(float(one.get('billed_usd') or 0) for one in run['segments']
            if d.datetime.fromisoformat(one['created_at'].replace('Z','+00:00')) >= anchor)
cap = min(float(rec['step']['cap_usd']), $REMAINING)      # the cap RULE at TODAY's remaining
left = cap - spent
seconds = left / float(rec['rung_0']['price']['usd_per_hour']) * 3600
seconds = min(seconds, 60.0 * float(rec['gates']['terminate_after_minutes']))  # the REGISTERED stop
print((d.datetime.now(d.timezone.utc) + d.timedelta(seconds=seconds))
      .strftime('%Y-%m-%dT%H:%M:%SZ'))")
echo "$STOP_AT"                                          # empty is a STOP, never a create
CARD=$(python3.11 -c "import json;print(json.load(open('results/prereg_promo_holdout2.json'))['rung_0']['price']['card'])")
echo "$CARD"    # the gpu-id THIS record was written on — rung 1 compares the create against it
runpodctl pod create --name mp-promo-holdout2 \
  --gpu-id "$CARD" --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after "$STOP_AT"
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --open --part holdout2 --pod-id <ID> \
  --created-at '<the create stamp, UTC ISO8601>' --usd-per-hour <costPerHr> --card "$CARD"
```
**The gpu-id is READ from the committed record, never typed from this page.** `offered_price` picks
the card on the day and rung 1 KILLs a pod whose card is not `rung_0.price.card` — so a registration
re-emitted when `RTX PRO 4500` is out of stock names A6000 instead, and a literal here would KILL a
correctly created pod ([[a_shifted_constant_has_physical_consumers]]). The `spent` above sums only
the segments created at or after **this line's** anchor — the shot's run record is its own and
starts empty, so the filter is the rule and not a workaround; it stays the rule for any recreate.
A KILL from `--open` means the create response's price or CARD is not the registered one, so the cap
was computed against another number: `runpodctl pod delete <ID>`, `--close-segment` with the outcome,
prove `pod list -a` is `[]`, and STOP.

## 2 — the ssh dead-man, bounded by the CLOCK and never by an iteration count
**500 s** of THIS pod's create-elapsed, READ from the record and never typed
(`results/prereg_promo_holdout2.json :: gates.ssh_deadman_seconds`, which ruling 03.09 (e) item 1
takes from `results/prereg_pass2_signals_r2.json :: kill_clock[rung 2]` — the PRODUCTION sibling,
six readings 14.5 → 262.5 s). The 180 s this runbook used on 2026-09-03 came from a PROBE and killed
two healthy pods before either could publish a port.
```bash
DEAD=$(python3.11 -c "import json;print(int(json.load(open('results/prereg_promo_holdout2.json'))['gates']['ssh_deadman_seconds']))")
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
git status --short && git bundle create /tmp/market-pulse-promo-holdout2.bundle HEAD
scp -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> /tmp/market-pulse-promo-holdout2.bundle root@<HOST>:/workspace/
```
On the pod:
```bash
cd /workspace && rm -rf repo && git clone -q market-pulse-promo-holdout2.bundle repo
cd repo && git rev-parse HEAD && git status --short     # equals the Mac's HEAD, empty
ls -d /workspace/venv /workspace/hf && du -sh /workspace/hf   # the volume is warm, or STOP
rm -rf /workspace/run && mkdir -p /workspace/run && ls /workspace/run   # empty — the proof
```

## 4 — launch DETACHED, from the CLONE, with the warm volume and the ALLOCATOR on the path
`HF_HOME=/workspace/hf` is load-bearing: without it `google/gemma-4-31b-it` resolves to root's
container disk (30 GB) and 59 GB of weights are re-downloaded on the meter.
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` is ruling (w) item 2's other half and iteration 5's
proven serving — the OOM that ended iteration 4 refused 338 MiB at 23.19 of 23.52 GiB on 24 GB.
```bash
ssh -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -p <PORT> root@<HOST> \
  'cd /workspace && HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src \
   PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True setsid nohup \
   /workspace/venv/bin/python -u /workspace/repo/scripts/promo_dev_pod_runner.py \
     --pack /workspace/repo/results/promo_holdout2_pack.json \
     --out /workspace/run/promo_holdout2.jsonl --repo /workspace/repo \
     --go /workspace/run/promo_go --go-deadline 1800 \
   > /workspace/run/pod.log 2>&1 < /dev/null & echo $!'
```
Watch the PROCESS, not a success-grep — and by PID, not by name: `pgrep -f promo_dev_pod_runner`
matches the launch wrapper and the probe's own remote shell too, so it never reads 0 (s31). Take the
PID the launch line echoed:
`ssh ... 'cat /proc/<PID>/cmdline | tr "\0" " "; [ -d /proc/<PID> ] && echo ALIVE || echo GONE; tail -5 /workspace/run/pod.log'`.
**GONE while the smoke is short of its three IS «the smoke did not come back»** — delete at once,
do not sit out the GO deadline. Iteration 4's OOM cost $0.62 of exactly that wait.

## 5 — the smoke, then GO. There is no band gate on this leg (ruling 05.09 (r) item 2).
The smoke is holdout-2's shortest, median and **longest** render by
`results/promo_holdout2_prep.json :: corpus.threads[].chars`, named in the registration's
`population.leg_a.smoke` and shipped first by `build_pack`. The longest is 10 529 chars — under the
14 281 this card answered in iteration 5 — so the smoke is the fit proof at the cost of minutes.
**The money gate already fired**: rung 0 issued FITS on the mean corner and the cap rides as
`--terminate-after`. The three replies landing IS the GO.
```bash
scp ... root@<HOST>:/workspace/run/promo_holdout2.jsonl results/promo_holdout2.jsonl
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --smoke --part holdout2 \
  --replies results/promo_holdout2.jsonl
```
It prints the branch of the registration's OWN decision table and exits 0 only on «3 replies are
in». **An ERROR reply among them is «the smoke did not come back»** — read by the `exception` field,
so a death with an empty message is a death too — and needs no second reading: delete the pod at
once ((w)3). WAITING is a poll, not a verdict: pair it with the PID reading above, and no runner
alive is the same outcome as an error. A torn last line is the scp race and also reads WAITING —
re-fetch and read again ((x)4). A torn line that is NOT the last one is a DAMAGED file and refuses
by name («move it aside and stop»): re-fetch once, and if it stands, the pod is deleted on the PID
reading like any other death.
A missing unit, or a `finish_reason` that is not the model stopping on its own, is **not** a band
verdict: nothing is written to `promo_go`, the pod is deleted, `--close-segment` records it, the
listing is shown, and the run is PHASE §6.5's INCOMPLETE reading — recorded under its number, never
compared to the bars, re-bought under the next number only after the operator's money word.
```bash
echo '{"verdict": "GO"}' > /tmp/promo_go && scp ... /tmp/promo_go root@<HOST>:/workspace/run/promo_go
```
**Why `--project` is not run here.** Its bands are the DEV loop's absolute dollars (`GO ≤ $0.80 ·
GO-THEN-STOP ≤ $1.20 · NO-GO above`, ruling 03.09 (b)) and its KILL is «the MAX corner over the
cap» — and this leg's max corner is over the cap BY CONSTRUCTION ($2.8109), which rung 0 already
accepts. Applied unchanged it returns KILL on a run this very registration issued as FITS. Ruling
(r)2 keeps the gate that was priced and leaves `project()` and its literals untouched: do not run it.

## 6 — close: fetch, delete, the POST-RUN reading, then settle
The pod appends to the SAME out-file, so the fetch overwrites the smoke-only copy with all 40 units.
```bash
scp ... root@<HOST>:/workspace/run/promo_holdout2.jsonl results/promo_holdout2.jsonl
scp ... root@<HOST>:/workspace/run/pod.log results/promo_holdout2_pod.log
wc -l results/promo_holdout2.jsonl                      # 40 units, or the run was cut
runpodctl pod delete <ID>
runpodctl pod list -a && runpodctl serverless list      # both [] — in the transcript
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --close-segment --part holdout2 \
  --deleted-at '<stamp>' --billed-seconds <create→delete> --outcome '<what landed>' \
  --replies results/promo_holdout2.jsonl
python3.11 scripts/runpod_guard.py --step promo-holdout2 --step-cap 0.90 \
  --note 'promo-holdout2 POST-RUN reading, the reference the close settles against: pod <ID> <created>Z -> <deleted>Z, <n> billed s, <what landed>'
```
`--close-segment` prints `spent_this_line_usd` over the segments at or after THIS line's anchor and
its verdict is the line's (GO under $0.90) — the false `OVER` of iteration 5 cannot recur. It carries
`--replies` so the whole-run rate row `promo_holdout2_seconds_per_thread` is written for the next
leg; without it the command says so and writes none.
**PHASE v13 §6.1 — the `--note` above is the gate's reference and its moment is load-bearing.** It
is taken AFTER the pod is deleted and **BEFORE any next pod**: `recorded_reading()` takes the line's
LAST OPEN reading as the right-hand side of the tolerance gate, so a reading taken before the pod
refuses for ever (`promo-iter4`'s $0.0097 = 7000 % off) and one taken after a LATER pod carries that
pod's money.
```bash
EXPECT_MS=$(python3.11 -c "
import json, datetime as d
run = json.load(open('results/promo_holdout2_run.json'))
anchor = d.datetime.fromisoformat(json.load(open('results/spend_promo_holdout2.json'))['anchored_at'])
print(int(1000 * sum(float(one['billed_seconds']) for one in run['segments']
    if d.datetime.fromisoformat(one['created_at'].replace('Z', '+00:00')) >= anchor)))")
echo "$EXPECT_MS"                                        # 0 is a STOP: the filter found no segment
python3.11 scripts/runpod_guard.py --step promo-holdout2 --step-cap 0.90 \
  --note 'promo-holdout2 settled' --close --tolerance 0.05 \
  --expect-ms "$EXPECT_MS" --until '<an instant after this pod and before any next>'
```
**`--expect-ms` is not optional and `--until` is not either.** Without `--expect-ms`, `complete()`
returns True on any readable walk and RunPod's billing posts 30–60 min late, so a close minutes
after the delete settles the line at a fraction of its cost and freezes it. Without `--until` the
walk is unbounded and swallows every later pod. Billing may REFUSE for hours: that is a delay, not a
decision — repeat in the start ritual of the next session, read-only walk FIRST (`promo-iter5`
settled that way on 2026-09-06, 0.47 % off its reading). The drift is the anchor's AGE,
`drip·H / (pods + drip·H)`; under (y) the anchor and the `--note` are the same session, so it is a
rounding error here and never a term.

## 7 — the join, K8 and the error table, all $0 and after the pod is gone
The leg is ONE arm in ONE out-file: holdout-2 carries the bars and there is no reading beside it.
`--score` on this part takes no `--arm` and no `--iteration`; its files carry no iteration tag.
```bash
PYTHONPATH=src python3.11 scripts/promo_dev_pass.py --score --part holdout2 \
  --replies results/promo_holdout2.jsonl                    # the BAR, both bars
python3.11 scripts/grade_promo_signals.py --part holdout --draw results/promo_threads_draw_2.json \
  --gold docs/labels-promo-holdout2.jsonl \
  --predicted results/promo_holdout2_predicted.jsonl --out results/grade_promo_holdout2.json
```
K8 is given the SECOND draw and its `holdout` arm by name — `--part` there is the draw's arm, not
this emitter's leg — so the per-stratum readings are holdout-2's own. `--score` prints any unit the
run recorded as DEAD and counts it UNANSWERED, never as a parse failure ((x)4). An INCOMPLETE run
(any unanswered registered unit) is PHASE §6.5's case and is not compared to the bars.

By ruling (z): **the holdout is spent ONCE.** GREEN → S2 closes green on the product's own population
and the team lead writes the reading into STATUS. RED → S2 closes red with the number under this
registration and the next word is the operator's. Either way, then «c3» by ruling (l) 2–4 at cap
$0.50, and the volume `mp-srv2` is deleted after it ((z) item 5).
