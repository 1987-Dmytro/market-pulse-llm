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
