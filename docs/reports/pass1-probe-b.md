# pass1-probe-b — the same instrument, one boot constant, and the second attempt

**Read back, one line each.**

- **What may NOT move:** the `pass1_comment_gm4_v1` text and its sha `5a4a3cb6…`, the parser and its
  four subject types, gold r2, the 64-unit population and its per-item rendering shas, bar P1
  ≥12/14 with its loss budget and bar 4's own comparison, the census rules, the one-attempt class
  and the return-to-sitting clause.
- **The one constant that moves:** the boot — CHARGED 192.13 → **300.0 s** (the max of this stack's
  two measurements) and the CEILING `BOOT_KILL_S` 300 → **420 s**. The cap stays $0.20.
- **The old step's close:** `pass1-probe` may be closed only on a COMPLETE pod-scoped walk
  (~427 000 ms). It is still **PARTIAL — 300 000 ms** — so it is NOT closed and the debt is carried
  named, below.
- **The four commands the record was driven through, at $0:** `--pre-create-check`, `--open`,
  `--deadlines`, `--gate` — the last one **twice**, because it routes to two different sets of
  record reads.
- **When the b-registration freezes:** at the **FIRST `pod create` of this attempt**. A recreated
  pod reads the SAME record, which is what makes a replacement a segment rather than a second
  attempt.

---

## Step 0 — the tail, and the close that may not happen

### The tail, by path, in two commits

```
$ git status --porcelain      # at the start of this session
 M docs/STATUS.md
 M knowledge/daily_logs/2026-08-17.md
 M knowledge/hot.md
 M knowledge/index.md
?? docs/PROMPT-pass1-probe-b.md
?? knowledge/daily_logs/2026-08-18.md
```

`a68699e chore(brain): /save checkpoint` — the four `knowledge/` files, staged by path.
`59151ae docs(team-lead): STATUS accepts pass1-probe, and PROMPT-pass1-probe-b authorises …` — the
two team-lead files, **committed verbatim, never edited**, in their own commit. No `git add -A` at
any point.

### The close: REFUSED, and the debt carried with its figure

The Dv488 discriminator, run before anything else:

```
$ runpodctl billing pods --pod-id rx89zok35e5ca6 --grouping podId --bucket-size hour \
    --start-time 2026-08-17T00:00:00Z --end-time 2026-08-19T00:00:00Z
[
  {
    "amount": 0.061666667461395264,
    "diskSpaceBilledGb": 30,
    "podId": "rx89zok35e5ca6",
    "time": "2026-08-17 18:00:00",
    "timeBilledMs": 300000
  }
]
```

The pod lived 18:41:24Z → 18:48:31Z, entirely inside one hour bucket, so that single row is the
whole walk. It reads **300 000 ms against the run record's 427 000 ms — 70.3 % of the truth.**
A close on it would settle `pass1-probe` at the walk's `pods` line of **$0.0617** instead of its own
**$0.087772**, and `closing_record()` settles from the walk's rounded `billing_by_kind` with the
always-on kinds excluded, so there is no second reading to save it. **Not closed. The debt is
`pass1-probe`, 300 000 of ~427 000 ms observed at 2026-08-18T09:0xZ.**

### And the open ledger is now over its own cap — for a reason that is not the pod

```
$ python3.11 scripts/runpod_guard.py --step pass1-probe --step-cap 0.20
REFUSED: pass1-probe's $0.20 cap is reached ($0.2075 spent). …
PASS1-PROBE SPENT      $0.2075 of $0.20  (anchor $21.13 from runpod_balance_at_pass1-probe_start)
  balance delta   $0.2075
  billing since   $0.1978 (read)
    pods            $0.0617
    network-volume  $0.1361   <- always on, beside the run and never inside it
    serverless      $0.0000
  step resources   $0.0617   (every kind except the always-on ones)
CYCLE 2 SPENT     $1.5915 of $20.00
REMAINING         $18.4085
```

The step's **balance-delta** leg counts the network volume, which bills whether or not a pod exists,
so an open step drifts upward at the volume's rate forever. The pod-scoped truth is $0.0617 read /
$0.087772 recorded. **This refusal does not block this attempt** — `pass1-probe-b` is a separate
ledger with its own anchor, and the cycle-2 line has $18.4085 left. It is reported because it is the
cost of a step that cannot be closed, and it grows.

---

## D1 ($0) — the b-registration, driven before it was frozen

### The object-equality proof is a REFUSAL, not a claim

`scripts/write_pass1_prereg_b.py` calls `write_pass1_prereg.build()` **with no swaps first** and
refuses unless it rebuilds `results/prereg_pass1_probe.json` byte for byte. Only then does it build
again under the swap. So everything bar P1 is scored on is object-equal *by construction*, and the
two negative controls prove the refusal fires:

```
$ PYTHONPATH=src python3.11 -m pytest tests/test_pass1_prereg_b.py -q
18 passed
```

- `test_the_producer_refuses_unless_pass1_probes_own_producer_still_rebuilds_its_frozen_record` —
  moves `BAR_P1_MIN` to 13 and asserts `SystemExit: … no longer rebuilds from its own producer`.
- `test_the_swap_refuses_to_replace_a_name_that_no_longer_exists` — deletes `p1.BOOT_KILL_S` and
  asserts the swap STOPs rather than silently using the shipped constant.
- `test_the_enumeration_refuses_a_path_it_does_not_name` — both directions: a moved path that is not
  enumerated, and an enumerated path that did not move.

### The whole diff — 28 paths, enumerated, asserted both ways

```
authority.docs/reports/pass1-probe.md            money.arithmetic.pre_generation_budget_seconds
authority.results/pass1_probe_pack.json          money.arithmetic.which_leg_binds
authority.results/pass1_probe_run.json           money.arithmetic.worst_case
authority.results/prereg_pass1_probe.json        money.guard
contract.docs/PROMPT-pass1-probe-b.md            money.reading.boot.charged
frozen_when_the_pod_exists                       money.reading.boot.measurements
go_no_go.gates.2_boot_kill.boot_kill_seconds     money.reading.boot.rule
money.arithmetic.boot_deadline_rule              money.reading.boot.seconds
money.arithmetic.boot_kill_rule                  money.reading.boot.why_the_max
money.arithmetic.boot_kill_seconds               phase
money.arithmetic.boot_seconds_charged            producer.calls
money.arithmetic.full_pass_over_the_registered_order   producer.script
                                                 producer.sha256
                                                 supersedes
                                                 transport.boot_kill_seconds
                                                 transport.pod_log
```

`instruments`, `population`, `bars`, `attempt`, `return_to_sitting`, `class` and `non_gating` are
**not** in that list — they are the frozen record's own objects. The pack's whole diff is
`phase` and `registration.record`; `PACK["items"]` is asserted object-equal, all 64 of them.

**The gate table is let through as one opaque range and that hole is closed separately.** The table
carries 64 rows whose headroom and margin move by construction; enumerating 128 leaves would bury
the discrimination. So `the_registered_order_is_unmoved()` compares the unit sequence, every
verdict, `first_stop_after_units`, `per_call_seconds` and the zero-boot corner directly — with a
negative control that flips one verdict to `STOP` and asserts the refusal.

### The re-solved table at boot 300 / ceiling 420

```
$ PYTHONPATH=src python3.11 scripts/write_pass1_prereg_b.py
wrote results/prereg_pass1_probe_b.json  sha256 a29e85ad6e856f6f…
wrote results/pass1_probe_b_pack.json  sha256 bbbe64203f9c909a…
  cap $0.20 buys 973.0 s · usable 913.0 s · 64 units at 6.402 s
  reading projection 409.7 s · boot charged 300.0 s · ceiling 420 s · budget 83.2 s · affordability 503.2 s
  worst case 889.7 s = $0.18289 of $0.20 -> fits True  (the contract's $0.175 = $0.17533, the delete margin charged twice)
  full pass: first STOP after None unit(s) · tightest margin 3.226 s/unit at unit 1 (@VARUS_channel:10348#20594)
  the whole diff against results/prereg_pass1_probe.json: 28 paths, enumerated
```

| | pass1-probe | pass1-probe-b |
|---|---|---|
| usable seconds | 912.973 | **912.973** — unchanged |
| reading projection (64 × 6.402) | 409.728 | **409.728** — unchanged |
| affordability deadline | 503.245 | **503.245** — unchanged |
| boot charged | 192.13 | **300.0** |
| boot ceiling `BOOT_KILL_S` | 300 | **420** |
| pre-generation budget | 203.245 | **+83.245** |
| first STOP in the full pass | none | **none** |
| tightest margin | 4.938 s/unit at unit 1 | **3.226 s/unit at unit 1** |
| headroom at unit 1 | 311.1 s | **203.2 s** |
| zero-boot corner (`usable ÷ units`) | 14.265 s | **14.265 s** — no boot in it |

Four of the five numbers the contract asked to be **reproduced rather than trusted** reproduce
exactly. The fifth does not, and the deviation is registered rather than quietly corrected — see
Dv490.

**Which leg binds is now a live question, and the record says so.** `pre_generation_budget_seconds`
IS the create-elapsed above which the boot ceiling stops binding: below 83.2 s the ceiling binds, and
above it the money does. pass1-probe's staging took **92 s**, on the far side of that line, so on the
only evidence there is **the affordability deadline at 503.2 s of create-elapsed is what binds this
attempt** and the boot ceiling is not the constraint any more. Both are printed at every gate and
both land in the run record.

### The registration driven through every command that reads it, at $0

The Dv486 rule, promoted from a lesson to a deliverable. `registration()`'s git provenance check runs
for real on the committed file; the only redirection is where the run record, the raw jsonl and the
step ledger LIVE, so a synthetic segment cannot land in the artifact the paid run will write.

```
$ … read_pass1_probe_b.py --pre-create-check
{ "may_create": true, "segment": 0, "segments_allowed": 3,
  "cap_usd_all_in": 0.2, "cap_left_for_this_segment_usd": 0.2 }                      [exit 0]

$ … --open --pod-id SYNTHETIC --created-at 2026-08-18T09:42:11Z --usd-per-hour 0.74 --card 'NVIDIA GeForce RTX 4090'
{ "segment": 1, "card_registered": "NVIDIA GeForce RTX 4090",
  "usd_per_hour_worked_example": 0.74, "priced_at_or_under_the_example": true, … }
{ "elapsed_since_this_segments_create_seconds": 30.3, "threshold_seconds": 180.0,
  "seconds_left": 149.7, "ssh_endpoint_answered": false, "verdict": "WAIT", … }      [exit 0]

$ … --gate0 --ssh-ok
{ "elapsed_since_this_segments_create_seconds": 30.3, "ssh_endpoint_answered": true,
  "recreates_left": 2, "verdict": "GO", "next_step": "stage and launch" }            [exit 0]

$ … --deadlines --generation-started-at 2026-08-18T09:42:36Z
{ "generation_started_at_create_elapsed": 25.0, "usable_seconds": 913.0,
  "contract_ceiling_seconds": 420.0, "contract_ceiling_as_create_elapsed": 445.0,
  "affordability_deadline_as_create_elapsed": 503.2, "reading_projection_seconds": 409.728,
  "pre_generation_budget_seconds": 83.245,
  "first_reply_must_land_by_create_elapsed": 445.0, "seconds_left": 414.6,
  "verdict": "WAIT",
  "rule": "min(boot_kill_seconds 420 s measured from the generation process starting,
           usable_seconds - reading projection measured from `pod create`) …" }      [exit 0]

$ … --gate                     # no reply on disk -> the BOOT DEADLINE branch
{ … same block …, "read_from": { "exists": false, "copied_back_at": null } }
VERDICT WAIT — no reply in …/pod.jsonl                                               [exit 3]

$ … --gate                     # two synthetic replies -> the PROJECTION branch
{ "units_read": 2, "units_unread": 62, "legs_read": ["census"],
  "payable_comments_read": 2, "payable_comments_unread": 62,
  "measured_seconds_per_unit": 3.0, "usable_seconds": 913.0,
  "projections": { "by_unit": {"factor": 31.0, "seconds": 186.0},
                   "by_payable_comment": {"factor": 31.0, "seconds": 186.0},
                   "binding": {"factor": 31.0, "which": "by_unit"} },
  "projected_total_seconds": 216.4, "headroom_seconds": 696.5,
  "seconds_per_unit_that_still_fits": 14.234, "verdict": "GO",
  "read_from": { "exists": true, "copied_back_at": "2026-08-18T09:42:41+00:00" } }
VERDICT GO                                                                            [exit 0]
```

**`--gate` was driven twice on purpose.** It routes to the boot deadline when nothing has landed and
to the full-pass projection when something has, and those are different sets of record reads — the
projection branch reads the pack's payable counts, the cap left for the segment and the usable
seconds, none of which the deadline branch touches. Driving only the empty case would have sent the
projection branch to a live pod unexercised, which is the exact shape of the defect that cost the
last gate. All eleven of those command drives are also in the suite:
`tests/test_pass1_transport_b.py`, on `tmp_path` state.

**`money.arithmetic.boot_deadline_rule` is the fix for Dv486**, and the regression is pinned in two
places: `v4.deadlines(FROZEN, …)` is asserted to raise `KeyError: 'boot_deadline_rule'` and
`v4.deadlines(RECORD, …)` to return the rule. A field the shipped code reads by name is now a red
test, not a live gate.

**One thing to read with care during the run:** the `which_binds` sentence is v4's sealed
reader-era prose and it prints «the contract's twelve minutes» / «the 23 threads no longer fit» on a
pass-1 record. The NUMBERS beside it (445.0, 503.2, `seconds_left`) are correct and are what the gate
is decided on. `read_threads_reader_v4.py` is pinned by sha inside frozen records and is not this
contract's to edit.

### The freeze commit ran its own suite

The Dv487 rule. `9b9e7a5 prereg(pass1-probe-b): the same instrument, one boot constant, before the
pod exists` carries the producer, the record, the pack, the two thin drivers and the three test
files — and `producer.sha256` pins bytes that are IN it:

```
$ git worktree add --detach <scratch> 9b9e7a5 && cd <scratch>
$ shasum -a 256 results/prereg_pass1_probe_b.json results/pass1_probe_b_pack.json
a29e85ad6e856f6fafa032b3f5ede0e635046171778cbe7a6902b64fa57bacad  results/prereg_pass1_probe_b.json
bbbe64203f9c909a2d2e8aeab03d8d61c0fd6604d4854e13462d0e190bc4e113  results/pass1_probe_b_pack.json
producer.sha256   3e2ee8b12647aa89a8faacbf335e958f4be08b4ee1d4270a99b5c89fc81eed21
bytes in commit   3e2ee8b12647aa89a8faacbf335e958f4be08b4ee1d4270a99b5c89fc81eed21   MATCH True
calls pinned      16dee2f4590597b55a5b31e38be88cab88a1d4f7bbf3d21f7bab7c8e897ab6c6
calls in commit   16dee2f4590597b55a5b31e38be88cab88a1d4f7bbf3d21f7bab7c8e897ab6c6   MATCH True
```

```
$ git log --oneline -1 && git status --porcelain && make check     # HEAD = 9b9e7a5, tree clean
9b9e7a5 prereg(pass1-probe-b): the same instrument, one boot constant, before the pod exists
2911 passed, 2 skipped in 484.03s (0:08:04)
```

Baseline before this contract, on the same tree: **2 879 passed, 2 skipped** — the team lead's own
figure, reproduced. 2 879 + 32 = 2 911, and the 32 are 18 registration + 11 transport + 3 scorer.
The first attempt to run this on a bare `git worktree` failed at collection: `data/` is gitignored
except `data/frozen/`, so a detached checkout has no store to read and `tests/test_train_qlora.py`
raises before a single test runs. The suite therefore ran in the primary tree with `HEAD` at the
freeze commit and `git status --porcelain` empty — the same bytes, and the only place they can be
executed. See Dv492.

---

## D2 — the run

Anchor `results/spend_pass1_probe_b.json` at **$20.9182116007, 2026-08-18T09:47:08Z**, cap $0.20,
committed in `dfdf636` **before** anything was created. Three listings immediately before create:
`pod list -a` `[]`, `serverless list` `[]`, `network-volume list` `qw4nwleanc` `mp-srv2` EU-RO-1
100 GB — the volume is the positive control that the listing works at all. `--pack` rebuilt the
committed pack byte for byte (64 units = 14 gold + 50 census); `--pre-create-check` →
`may_create: true`, segment 0 of 3.

| create-elapsed | wall | what |
|---|---|---|
| 0 s | 09:47:42Z | `pod create` — **`zn3chzmo1xricf`**, RTX 4090, RO, `costPerHr` **0.74**, exactly the registered worked example, so no deadline is re-priced |
| 5.1 s | 09:47:47Z | `--open`: segment 1 recorded, gate `open` **WAIT**, 174.9 s left on gate 0 |
| 10 s | 09:47:52Z | **the endpoint answered** — `213.173.99.21:19441`, on the FIRST poll |
| 14.5 s | 09:47:56Z | gate `gate0` **GO**, 165.5 s unused, recreates left 2 |
| 26 s | 09:48:08Z | scp: the 8.70 MB bundle at `dfdf636`, the b-pack, and all three runners |
| 54 s | 09:48:36Z | `git clone` → **`repo-pass1b`** (a NEW directory); `HEAD = dfdf63672868fcd5…` = the Mac's HEAD; `git status --short` empty; `/workspace/hf` 59 G |
| 66 s | 09:48:48Z | detached launch, `--repo /workspace/repo-pass1b` passed explicitly |
| 66.2 s | | `instrument OK · parser a4a5a5d08546f53a…` · **64 requests match the registration's per-item shas** · `ceiling 256 output tokens · stop at the brace` |
| 303.2 s | 09:52:45Z | `READY · boot 237.2s` |
| 308.2 s | 09:52:50Z | **reply 1/64**, 5.0 s |
| 392.7 s | 09:54:14Z | jsonl **and log** scp'd together, then `--gate` → **GO**: 17 read, 5.069 s/unit, projected 630.9 s of 913.0, headroom 282.1 s, $0.1297 of $0.20 |
| 633.7 s | 09:58:16Z | `DONE · 64 generated here · 64 replies` at 567.7 s of process-elapsed |
| 657.0 s | 09:58:39Z | `pod delete` → `{"deleted": true}`; `pod list -a` `[]`, `serverless list` `[]`, the volume unchanged |

**Segment 1 closed: 657.0 s = $0.135050 of the $0.20 cap.** One segment, no recreate, no kill.

**Gate 0 has now gone GO on three independent creates** — 23.4 s, 24 s and **14.5 s** against a
180 s dead-man. The transport difference reader-v5b paid 727.9 billed seconds to discover is
measured and settled.

### The boot, measured a third time — and the constant this contract moved was not the one that bound

| run | boot | kind |
|---|---|---|
| reader-v5b | 192.13 s | reading |
| pass1-probe | [267, 293] s | bound (the pod died; the witness is an ALIVE/DEAD pair) |
| **pass1-probe-b** | **237.2 s** | **reading — the runner printed it** |

The three span **1.53×** on the same card, the same volume and the same weights. The registered
charge of 300 s sat 62.8 s above tonight's boot, which is what a bound is for; the registered
ceiling of 420 s was never approached.

**But the honest reading is that the lift did not save this run.** The first reply landed at
**308.2 s** of create-elapsed. Under the OLD ceiling — launch 66 s + 300 s = 366 s — it would have
cleared by **57.8 s**. pass1-probe came within 0.6–26.6 s of that same ceiling because its boot was
30–56 s slower, not because 300 s was wrong. What killed pass1-probe was the `KeyError`; the boot
ceiling was a near miss, and tonight it was not close. See Dv496.

### The scp of the pod's log, registered and honoured

`transport.pod_log` says the log travels beside the jsonl before every gate. Both files were copied
in ONE `scp` invocation, twice: at 09:54:12Z before the full-pass gate, and at 09:58:2xZ before the
delete. `results/pass1_probe_b_pod.log` is committed — 72 lines, the boot line, all 64 reply lines
and `DONE`. **That is the artifact pass1-probe lost**; its only traceback survived as a screen read
and died with the pod.

---

## D3 — scoring

```
$ PYTHONPATH=src python3.11 scripts/read_pass1_probe_b.py --ingest
wrote results/pass1_probe_b_rows.jsonl  64 of 64 units
  read 64 · parsed 64

$ PYTHONPATH=src python3.11 scripts/score_pass1_probe_b.py
wrote results/pass1_probe_b_verdict.json  sha256 4f3a0cbf226a06a8…

BAR P1  9 of 14 agreed  (12 of 14 rows agreed)  -> False
  disagreed 5 · absent 0 · losses 5 of a budget of 2
…
REFUSALS 0 of 64
PER CALL 5.162 s · 42.2 completion tokens · 0.81x the registered bound · 1.76x the fit
WINDOW   1032 payable comments -> 5327 s = $1.0950 of generation at the worked example (a FLOOR, no boot in it)

OUTCOME STOP
```

### Bar P1 — 9 of 14, and the whole table

Each gold row is scored on the fields **that row** states, which is bar 4's own rule: 11 rows score
`subject_type` alone, 2 score `subject_type` and `stance`, and 1 scores `stance` alone.

| msg_id | scored on | gold | pass 1 | |
|---|---|---|---|---|
| 21626 | subject_type, stance | `сеть_ритейлер` · `negative` | `сеть_ритейлер` · `negative` | ok |
| 21599 | subject_type | `категория_личное` | `категория_личное` | ok |
| **21601** | subject_type | `категория_личное` | **`None`** | **X** |
| 21629 | stance | `positive` | `positive` | ok |
| **580124** | subject_type, stance | `молочный_бренд` · `negative` | **`сеть_ритейлер`** · `negative` | **X** |
| 580129 | subject_type | `категория_личное` | `категория_личное` | ok |
| 47899 | subject_type | `категория_личное` | `категория_личное` | ok |
| **47902** | subject_type | `категория_личное` | **`молочный_бренд`** | **X** |
| 48276 | subject_type | `категория_личное` | `категория_личное` | ok |
| **48283** | subject_type | `категория_личное` | **`None`** | **X** |
| 579379 | subject_type | `категория_личное` | `категория_личное` | ok |
| **579457** | subject_type | `категория_личное` | **`не_наш_рынок`** | **X** |
| 578951 | subject_type | `не_наш_рынок` | `не_наш_рынок` | ok |
| 20664 | subject_type | `сеть_ритейлер` | `сеть_ритейлер` | ok |

**Both denominators, and there is only one.** No row is `absent` — every unit was answered — so the
registered fourteen and the answered fourteen are the same set and the narrower reading is `None`
by construction. `9 / 14 = 0.643` against a threshold of `12 / 14`.

**Every one of the five losses is `subject_type`.** `stance` is scored on three rows and is right on
all three. Split by what gold says:

| | agreed | of |
|---|---|---|
| `subject_type` where gold says `категория_личное` | 5 | 9 |
| `subject_type`, every other reading | 3 | 4 |
| `stance` | 3 | 3 |
| **the bar** | **9** | **14** |

Two of the five losses are rows the model **declined to type at all** (`subject_type: null` where
gold says `категория_личное`) — a legal answer under the registered schema, parsed without a
refusal. The other three are a different reading of the same comment, and one of them —
`молочный_бренд` → `сеть_ритейлер` on 580124 — is a subject confusion rather than a granularity one.
**The symmetric collapse changed nothing here**: gold r2 spells `категория_личное`, the pass-1 text
offers that exact reading, and five rows agreed on it. The vocabulary was never the obstacle.

### The census — 50 neighbour rows, and half of them untyped

```
@VARUS_channel:10348   {None: 4,  не_наш_рынок: 1,  сеть_ритейлер: 1}
@VARUS_channel:10613   {сеть_ритейлер: 3, None: 2,  категория_личное: 1}
@mandziak:3676         {None: 7}
@mandziak:3703         {категория_личное: 4, None: 3}
@matusi_ukr:22242      {не_наш_рынок: 7, None: 2, категория_личное: 2}
@matusi_ukr:22272      {категория_личное: 4, None: 7, молочный_бренд: 2}
overall  {None: 25, категория_личное: 11, не_наш_рынок: 8, сеть_ритейлер: 4, молочный_бренд: 2}
```

**25 of 50 census rows carry no `subject_type` and 24 carry no `stance`** — and not one of them is a
refusal. **`REFUSALS 0 of 64`**: every reply was a single balanced object, `finish_reason: stop` on
all 64, and the 256-token ceiling never fired. The abstention is the model's ANSWER, not a parse
failure — which is exactly the distinction pass1-probe's registration built the refusal census to
keep apart, and it is the census's most useful number: on the neighbour rows the instrument declines
half the time.

### What one call costs, against both registered readings

| | seconds/call | this run against it |
|---|---|---|
| the registered BOUND (v5b's cheapest call) | 6.402 | **0.81×** — the bound held |
| the fitted line (extrapolated below its own range) | 2.934 | **1.76×** — the fit under-predicted |

**measured 5.162 s/call**, 42.19 completion tokens, 871.27 prompt tokens. The registration published
both readings and said the difference was what the run would measure; it did. A gate solved on the
fit would have been optimistic by 1.76×.

**The window pass-1 re-price:** 1 032 payable comments × 5.162 s = **5 327 s = $1.0950** of
generation at $0.74/h. That is a **FLOOR** — no boot, no staging, no second pod — and it is the
number a window-wide pass 1 has to be judged against, not a quote.

### The verdict is a STOP and the clause is armed

```
"outcome": "STOP"
"return_to_sitting": "**A FAILED BAR GOES BACK TO THE SITTING, never to a prompt iteration.** …"
```

Nothing in this session iterates on the prompt, the parser, the population or the bar. The
registration's one-attempt clause and the contract's DO NOT both say the sitting owns the next move.

---

## Verify

```
$ make check                                      # before this contract
2879 passed, 2 skipped in 458.00s (0:07:38)

$ git log --oneline -1 && git status --porcelain && make check     # ON the freeze commit 9b9e7a5
9b9e7a5 prereg(pass1-probe-b): the same instrument, one boot constant, before the pod exists
2911 passed, 2 skipped in 484.03s (0:08:04)

$ make check                                      # after the run
2911 passed, 2 skipped in 480.22s (0:08:00)

$ runpodctl pod list -a                           # after
[]
$ runpodctl serverless list
[]
$ runpodctl network-volume list                   # the positive control
[{"dataCenterId": "EU-RO-1", "id": "qw4nwleanc", "name": "mp-srv2", "size": 100}]

$ python3.11 scripts/runpod_guard.py --step pass1-probe-b --step-cap 0.20
CYCLE 2 SPENT     $1.6769 of $20.00
REMAINING         $18.3231
PASS1-PROBE-B SPENT      $0.0853 of $0.20  (anchor $20.92 from runpod_balance_at_pass1-probe-b_start)
  balance delta   $0.0853
  billing since   UNAVAILABLE (no billing rows yet) — the delta stands alone as a LOWER BOUND

$ shasum -a 256 results/prereg_pass1_probe_b.json results/pass1_probe_b_pack.json
a29e85ad6e856f6fafa032b3f5ede0e635046171778cbe7a6902b64fa57bacad  results/prereg_pass1_probe_b.json
bbbe64203f9c909a2d2e8aeab03d8d61c0fd6604d4854e13462d0e190bc4e113  results/pass1_probe_b_pack.json

$ PYTHONPATH=src python3.11 scripts/write_pass1_prereg_b.py --out /tmp/again.json --pack /tmp/again_pack.json
  # byte-identical to both committed files — asserted in
  # tests/test_pass1_prereg_b.py::test_the_committed_registration_and_pack_are_what_the_producer_writes_today

$ PYTHONPATH=src python3.11 -m pytest tests/test_pass1_prereg_b.py tests/test_pass1_transport_b.py \
      tests/test_score_pass1_probe_b.py -q
32 passed
```

**The step is NOT closed.** `pass1-probe-b`'s own pod-scoped walk answers `[]` — the billing rows
have not posted yet — and the balance delta of $0.0853 is a LOWER BOUND against the run record's own
**$0.135050**. Closing on either would freeze a figure below the truth. Second named debt, below.

---

## Deviations from Dv490

| # | what | cause |
|---|---|---|
| **Dv490** | **The contract's worst-case figure does not reproduce.** $0.175 is `(usable_seconds − delete_margin) × rate` = 852.973 s = **$0.17533** — and `usable_seconds` has already had the 60 s margin taken off, so that construction charges it twice. The reachable worst case is the boot ceiling burned in full plus all 64 units at the bound plus the margin: 420 + 409.728 + 60 = 889.728 s = **$0.18289**. Registered as `money.arithmetic.worst_case` with its arithmetic and with the contract's own figure named beside it. Every construction is inside the $0.20 cap, so nothing about go/no-go turned on it; actual spend was **$0.13505**. The other four numbers (913.0 · 409.7 · 503.3 · +83.3) reproduce exactly. | `[cause: the-hand-typed-number-fails-the-total]` |
| **Dv491** | **`pass1-probe` could not be closed and the open ledger is now over its own cap for a reason that is not the pod.** The pod-scoped walk reads **300 000 ms of 427 000 ms** — a close would settle the step at the walk's $0.0617 instead of its recorded $0.087772. Meanwhile the step's balance-delta leg reads **$0.2075 of $0.20**, because the network volume bills whether a pod exists or not and an open step drifts upward at its rate forever. The refusal is correct and does not block a separate ledger; the cost of a step that cannot be closed is that it keeps growing. | `[cause: a-settlement-is-a-reading-too]` |
| **Dv492** | **The freeze commit's suite cannot run in a detached `git worktree`.** `data/*` is gitignored except `data/frozen/`, so a clean checkout has no store and `tests/test_train_qlora.py` raises `ValueError: …/data/raw/posts: no stored posts` at COLLECTION, before a single test runs. Dv487's ritual was executed instead in the primary tree with `HEAD` at the freeze commit and `git status --porcelain` empty — the same bytes, and the only place they can be executed. `producer.sha256` was separately proved against `git show`'s bytes in a worktree. | `[cause: a-test-that-reads-a-shipped-artifact]` |
| **Dv493** | **`--gate` is two commands and only one of them had ever been driven before a pod.** It routes to the boot deadline when nothing has landed and to the full-pass projection when something has, and the projection branch reads the pack's payable counts, the cap left for the segment and the usable seconds — none of which the deadline branch touches. Both are now driven at $0 and both are in the suite. Found by driving, not by reading: the first drive raised `TypeError: float() argument must be … not 'dict'` on a malformed synthetic row, which is how the branch got exercised at all. | `[cause: a-guard-on-one-path-is-not-a-guard]` |
| **Dv494** | **`bars.P1_per_comment_agreement.scored_fields` is `[]` in the registration and the real rule lives in the gold file.** `_fields_of` reads `scored_fields` off the registered gold rows, which carry only `msg_id` and `thread`, so the union is empty. What actually decides each row is the GOLD row's own `scored_fields`: 11 rows score `subject_type`, 2 score `subject_type` and `stance`, 1 scores `stance` alone. The bar is correct — `scorer.reader_comment_agreement` reads the gold row — but the registration publishes a field that says nothing about it. **Not repaired here**: it is object-equal to the frozen record and this contract may not move it. | `[cause: a-registered-bar-may-have-no-producer]` |
| **Dv495** | **`which_binds` prints reader-era prose on a pass-1 record.** `read_threads_reader_v4.deadlines` returns «the contract's twelve minutes» or «affordability — the 23 threads no longer fit behind a boot this long»; this contract has no twelve minutes and no 23 threads. The NUMBERS beside it (`contract_ceiling_as_create_elapsed`, `affordability_deadline_as_create_elapsed`, `first_reply_must_land_by_create_elapsed`, `seconds_left`) are correct and are what every gate here was decided on. `read_threads_reader_v4.py` is pinned by sha inside frozen records; reported, not edited. | `[cause: a-rename-the-data-cannot-follow]` |
| **Dv496** | **The constant this contract moved was not the one that bound on the night.** Boot measured **237.2 s**, 30–56 s faster than pass1-probe's [267, 293] s. Under the OLD 300 s ceiling the first reply (308.2 s of create-elapsed, launch at 66 s) would have cleared by **57.8 s**. The lift to 420 s bought margin that was not needed, and the 300 s CHARGE was conservative by 62.8 s — which is what a bound is for. The three boots now span 1.53× with nothing in the runs to explain it, so the charge is still right and the ceiling is still unexercised. **This is not an argument that the ruling was wrong**: the ceiling was a near miss last time and a deadline is bought against the worst case, not the observed one. | `[cause: the-fix-that-was-not-a-fix]` |
| **Dv497** | **The runbook's detached-launch idiom still held the ssh channel.** `setsid nohup env … > log 2>&1 < /dev/null &` with both streams redirected launched the runner correctly — `setsid` detached it, PID 155 ran to `DONE` — but the ssh invocation itself did not return and was moved to the background at the 300 s harness timeout. No cost: the process was already running and every later command opened a fresh channel. The next runbook should add a trailing `exit` or `ssh -f`; Dv454 named the shortcut that fails, not the one that half-works. | `[cause: a-remote-job-outlives-its-watcher]` |
| **Dv498** | **One full-pass gate fired during the run, not several.** The registered rule is «after every unit»; what ran was one `--gate` at 392.7 s (17 units read, headroom 282.1 s, projected $0.1297) and then a poll loop reading the pod's own row count until the runner exited. The projection was never within 280 s of the cap and the run finished 264 s later, so nothing was at risk — but the artifact records three gates where a gate-per-batch practice would have recorded six or seven, and «the gate is what deletes the pod before the cap» is weaker evidence with one reading than with six. Both files were scp'd before that gate and before the delete, so the registered log rule was met. | `[cause: a-paced-log-is-an-interleavable-clock]` |
| **Dv499** | **`pass1-probe-b`'s step is also NOT closed, for the same reason, and this is now the second named debt.** Its pod-scoped walk answers `[]` and the balance delta reads $0.0853 against the run record's $0.135050. Closing on either freezes a figure below the truth. **Two ledgers are now open** — `pass1-probe` at 300 000 of 427 000 ms and `pass1-probe-b` at 0 of ~657 000 ms — and both accrue the network volume's drip on their delta leg for as long as they stay open. | `[cause: a-watermark-past-a-window-buries-the-backlog]` |

---

## Process signals

1. **Driving the registration through every command found the branch that reading it did not.** The
   `--deadlines` fix was known from Dv486 and went in as a registered key with a regression test.
   The `--gate` projection branch was NOT known — it surfaced only because the drive was done twice,
   once empty and once with rows. A command with a routing decision inside it is two commands.
2. **The producer that CALLS the previous producer makes «nothing moved» a refusal.** Three negative
   controls fire: a moved bar, a renamed constant, and an enumerated path that did not move. The
   28-path diff is a fact about the record rather than a claim in a commit message.
3. **The opaque range in an enumerated diff has to be closed by hand.** The gate table went through
   as one path and would have hidden a reordered pack or a flipped verdict; the order and every
   verdict are compared directly, with a negative control that flips one.
4. **A near miss is not the cause.** The ceiling was lifted because pass1-probe came within 0.6 s of
   it; tonight's boot cleared the OLD ceiling by 57.8 s. Moving a constant after a near miss is
   right, and reporting that it was not what mattered is also right — otherwise the next contract
   inherits a fix credited with a result it did not produce.
5. **A step that cannot be closed keeps spending.** `pass1-probe`'s ledger has drifted from $0.0878
   of pod to $0.2075 of balance delta in fourteen hours, entirely on the volume. Two are open now.
   The guard's `--until` contract, already queued, is what closes them.

---

## What IS decided, and what is NOT

**Decided.** Pass 1 was measured. Under the registered instrument — a short per-comment
classification with the thread's already-bought entity context — **bar P1 is 9 of 14 against a
threshold of 12, and the attempt is a STOP.** The failure is entirely `subject_type` and entirely on
the substance of the reading, not on the vocabulary, the parser or the transport: zero refusals, 64
of 64 parsed, `stance` right on all three rows that score it, and the symmetric collapse a no-op
because the model and gold share the exact spelling that was in question.

The transport is settled. Gate 0 has gone GO on three creates. The instrument, the registration, the
pack, the two thin drivers and the scorer are committed, green at 2 911 and re-derivable. The run
cost **$0.135050** of a $0.20 cap, inside the registered worst case of $0.18289.

**Not decided, and not this contract's to decide.** The registered clause is explicit: a failed bar
P1 goes back to the sitting — **B (labelled `subject_type` data + LoRA)** or **C (a different
base)** — and never to a prompt iteration. The numbers the sitting now has that it did not have:

- a per-comment call costs **5.162 s**, 0.81× the registered bound and 1.76× the fitted line;
- a window-wide pass 1 over 1 032 payable comments is **$1.0950 of generation as a FLOOR**;
- the instrument abstains on **half** the neighbour comments while refusing none of them;
- what it gets wrong is `subject_type` on `категория_личное`-shaped rows — 5 of 9 — while `stance`
  and the other subject readings are 6 of 7 together.

**The two open ledgers are the operator's next call.** Neither `pass1-probe` (300 000 of 427 000 ms)
nor `pass1-probe-b` (0 of ~657 000 ms) can be closed until its walk is complete, and both accrue the
volume's drip until they are. The guard `--until` contract is already queued behind this one.
