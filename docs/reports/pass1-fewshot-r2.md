# pass1-fewshot r2 — D0′: the same line re-registered, and four defects caught before the pod

**Verdict on D0′.** Everything `docs/PROMPT-pass1-fewshot-r2.md` asks for at $0 is built, driven and
committed: the r2 registration by a **sibling producer**, the gate amended on its four points, the
guard anchor, the runbook, and tests in both directions on a fake transport. r1 is untouched — the
file on disk is still byte for byte `c7cbfd1` and a test says so. **The adversarial review before the
first `pod create` raised 21 findings, 7 survived refutation, and they collapse into four defects —
two of them would have deleted a healthy pod with the attempt unspent.** All four are fixed, each
with a mutation that was watched to go red.

*(This report is written at the D0′ boundary and is extended after D1/D2. The paid session's own
section is below.)*

## Read back first, one line each (the contract's own list)

- **Rung 2's new ceiling, and why 500 and not 600.** ssh dead-man **≤ 500 s of create-elapsed**, else
  KILL. At 600 the worst case itself grows to 5 576.552 s, so one dead pod plus that worst case is
  **6 176.552 s > 6 100** — the recovery clause stops being reachable. The dollars would still fit;
  the seconds do not, and the seconds are what the platform holds.
- **What rung 3 is anchored on, and the backstop.** The 450 s ceiling is measured from
  **`launched_at`** — a stamp the pod writes into `/workspace/run/launched_at` in the same command
  that execs the runner, copied back by `--watch`. Beside it a create-anchored **backstop of
  1 100 s** = ssh 500 + stage/launch 150 + load 450, which is what bounds a late stamp.
- **The worst case, the cap, the hard stop, the step sum.** 5 476.552 s = 1.5213 h → **$1.2170** at
  $0.80/h ($0.8063 at $0.53); cap **$1.38**; cumulative hard stop **6 100 s = $1.3556 < $1.38**; step
  sum r1 $0.117783 + r2 $1.38 = **$1.497783 ≤ $1.50**.
- **Which blocks are byte-identical to r1.** `what_this_line_is`, `bars` (judge · dev gate · the gold
  bar · census-50), `population` (dev pack · shot pack · gold · holdout), `attempt`, `multiplicity`,
  `return_to_the_operator` and the whole of `instruments` — with exactly two declared exceptions:
  `instruments.gate.sha256` (the one instrument r2 amends) and the new
  `instruments.scorer_pass1_fewshot`. They are **copied out of the sealed record**, not recomputed.
- **When the attempt is SPENT.** At the first GOLD-row reply generated. Not at create, not at a dev
  reply, not at the dev gate. Every rung before rung 8 closes the session with it intact.
- **What a SECOND dead pod means.** STOP. The registration pays for ONE re-creation
  (`re_creations_allowed: 1`); after a second death neither the seconds nor the count fit, the
  session closes with the attempt not spent, and the question returns to the operator.

## 0 — baselines, at step 0, from the instrument

```
## Baselines — instrument output, 2026-08-21T11:16:50+00:00

- head: 13b827dd41a0 on main
- porcelain:  M docs/STATUS.md · M docs/reports/pass1-fewshot.md · M knowledge/daily_logs/2026-08-20.md
              M knowledge/decisions/lora-b-red-and-line-b-closes.md
              M knowledge/decisions/pass1-fewshot-closes-at-the-ssh-dead-man.md
              M knowledge/hot.md · M knowledge/index.md
              ?? docs/PROMPT-pass1-fewshot-r2.md · ?? knowledge/daily_logs/2026-08-21.md
- census: brain-census: 10.3Ktok boot tax
- suite: 3239 passed / 2 skipped — whole suite, stamped 2026-08-21T11:09:20+00:00 at 13b827dd41a0
- boot files: … = 161 lines / 20 362 UTF-16 units
- preflight: 1508 pinned paths · 2577 pins · 111 records — 1474 match every pin, 34 carry an older pin
```

The nine dirty paths are the team lead's own handover — the D0 acceptance, the r2 ruling in
`docs/STATUS.md`, the prompt, and the previous session's `/close` tail. They are committed **verbatim**
as `fd09753`, the first commit of this session, and none of them is this contract's work.

## The producer: a SIBLING, and why

The contract offered the choice — `--revision r2` on `scripts/write_pass1_fewshot_prereg.py`, or a
sibling. **It is a sibling, `scripts/write_pass1_fewshot_prereg_r2.py`**, for a reason that is
checkable rather than aesthetic: the r1 producer writes `producer.sha256 = sha256_of(__file__)` into
the record it produces, and `tests/test_pass1_fewshot_prereg.py` compares that record's BYTES against
a fresh rebuild. A flag added to that file moves the pin and r1 stops rebuilding — the one property
the contract asks acceptance to diff against `c7cbfd1`. A sibling leaves it untouched (**Dv607**).

**The copied half is a REFUSAL, not a convenience.** Every pin inside a copied block is resolved
against the live file it names, and one divergence is a `SystemExit` before a byte is written:

```
  bars.judge.module_sha256 · population.dev.sha256 · population.shot.sha256
  population.shot.sealed_source.sha256 · population.gold.sha256 · population.holdout.sha256
  instruments.parser.sha256 · instruments.scorer.sha256 · instruments.transport.sha256
  instruments.packs.sha256
```

Driven in both directions: `test_the_copy_REFUSES_when_a_copied_pin_stops_describing_this_checkout`
bends `population.dev.sha256` in a fake r1 and the producer stops, naming the path.

The call counts are **not** copied. They are re-derived from the live packs through the r1
producer's own `counts()` and then compared with what r1 registered — two independent derivations
that agree, rather than a quotation (H6 row `the_live_packs_still_carry_r1s_call_counts`, and a
negative control that bends `shot` to 63).

## The four amendments, as built

| # | Amendment | Where it lives now |
|---|---|---|
| 1 | rung 2: 180 → **500 s** of create-elapsed | `kill_clock[2].rule`; the two 20.08 readings are read out of r1's own gate record, never typed |
| 2 | rung 3: the 450 s ceiling on **`launched_at`**, backstop **1 100 s** from create | `kill_clock[3].anchor` / `.rule` / `.backstop_seconds` |
| 3 | `scripts/score_pass1_fewshot.py` pinned; the overshoot tolerance into the record | `instruments.scorer_pass1_fewshot`, `money.arithmetic.cumulative.backstop_tolerance_seconds` |
| 4 | money re-derived — cap $1.38, hard stop 6 100 s, overhead 1 300 s | `money.*`, 31 H6 rows |

**Rung 3's rule carries two numbers, and `first_number` reads positionally.** The gate takes the
ceiling as the first number of the rung's sentence, so a reordered clause could silently make 1 100
the ceiling. The backstop therefore has its own **named field** the gate reads by key, and the test
asserts `first_number(rung 3) == 450 != backstop_seconds` (**Dv610**).

**The launch stamp is a READING, not a flag.** The runbook has the pod write it, in the foreground,
in the same shell command that execs the runner; `--watch` copies it back with the out-files;
`launched_at_of` writes it into the pod's entry **once** and never moves it forward. A stamp the
executor types is an assertion, and this particular assertion can only ever move a deadline outward.
Three refusals, each driven: a stamp before the pod's create (a previous attempt's — the run
directory was not cleared), a stamp in the future, and an unreadable one (**Dv611**).

**The overshoot tolerance left the gate's source.** `make preflight ARGS='… BACKSTOP_TOLERANCE_SECONDS'`
now finds the name in the r2 producer and in `scripts/gate_lora_b.py` — a different, sealed
registration — and **nowhere in `scripts/gate_pass1_fewshot.py`**. Its absence from the record is a
`SystemExit`, not a default.

## The review before the pod: 21 findings, 7 standing, four defects

Five independent lenses over the uncommitted diff — the rung logic, the arithmetic, what must not
move, whether the tests fail when the logic breaks, and clause-by-clause contract compliance — each
finding then attacked by a skeptic told to default to refuted. **14 were refuted, 7 stood, and they
are four distinct defects.** Two of them end the session at a cost:

### Dv613 — rung 4 was still pricing r2's run with r1's repealed 1 800 s overhead

`money.arithmetic.cumulative.projection_gate` was deep-copied whole from r1. `projection()` adds
`projection_gate.overhead_seconds` on **every poll of the watch**, so rung 4 charged 1 800 s of
overhead against a hard stop r2 had also LOWERED from 6 300 to 6 100 — while the money block beside
it certified «nothing is counted twice». The same copied block's `verdict` still read «exceeds $1.50
… or the 6300 s hard stop», both r1 numbers, inside a record whose cap is $1.38.

Driven against the shipped gate on the real shot pack: after one dead pod at rung 2 the recovery pod
passes `--pre-create-check` (5 976.552 s / 6 100, $1.328123 / $1.38), runs both dev legs GO — and the
shot's **first** poll projects 6 476.6 s / 6 100 and KILLs, deleting the pod before one gold row
exists. With 1 300 the same state is GO at 5 976.6 s / $1.3281, which reproduces the record's own
`then_the_full_worst_case_seconds` to six digits. Cost avoided: ~$1.0 of pod, both pods deleted, a
third refused, the attempt unspent and nothing measured.

Fixed in the producer (the gate already reads the number from the record, which is the architecture
working), with an H6 row so the two copies cannot diverge again and a sweep test that hunts **every**
repealed r1 value as a NUMBER anywhere in r2's money block:

```
H6  the_projection_gate_charges_the_registered_overhead   1300.0  equals  1300.0
test_no_number_r2_REPEALED_survives_anywhere_in_its_money_block
  -> {1.5: ['money.step_sum.step_budget_usd']}      # the STEP budget the ruling kept, and only it
```

### Dv612 — the first reply was still being typed, on r1's create-anchored recipe

The contract moved rung 3's anchor and left the runbook's `--first-reply-at` recipe alone: `create +
the first row's boot_seconds`. But `boot_seconds` is written by the runner **from its own start**
(`scripts/reader_v5_pod_runner.py:236,259`), so adding it to CREATE and then subtracting the launch
stamp takes the ssh wait and the staging off twice. A 460 s load — over the registered ceiling —
would have read as 415 s and rung 3 would have reported **GO on exactly the condition it was
re-anchored to catch**; with a 540 s ssh wait it would have recorded a negative load.

This is Dv605 with the sign flipped, and the fix is to stop typing the number at all: **`--boot` now
takes no stamp.** It reads the launch anchor out of the run record and the first reply out of the
dev out-files' own `elapsed_since_start`, which is monotonic seconds from the runner's start to that
row — literally «launch → first reply». The flag is gone.

### Dv614 — the ssh poll was bounded by ITERATIONS, and iterations are not seconds

The runbook's loop read `for i in $(seq 1 95)` annotated «95 × 5 s = 475 s, inside the 500 s rung».
The bound counts only the sleeps. r1's own gate record prices the other term: pod `juupgp6y77jvuz`
ran a nominally 170 s loop (34 × 5 s) between `price GO` at 21:03:46 and the `gate0 KILL` at
21:07:32 — **226 s of wall clock, 6.65 s a turn**. Ninety-five turns is ~631 s, past the 500 s rung
and past the **623.448 s** at which the ONE re-creation stops fitting
(`widest_dead_pod_that_still_fits_seconds` = 6 100 − 5 476.552). The dead-man case — ssh never comes
up, which is what happened on both pods of 20.08 — would have burned the recovery clause the whole
500-not-600 derivation exists to protect.

The loop is now bounded by the **clock**, against rung 2's own ceiling read out of the record:

```bash
CEIL=$(python3.11 -c "…['money']['arithmetic']['ssh_seconds_charged']")
CREATED=$(date -u -j -f '%Y-%m-%dT%H:%M:%S' '<the create response stamp>' +%s)
while [ "$(date -u +%s)" -lt $((CREATED + CEIL)) ]; do … ; sleep 5; done
```

### Dv615 — `--price` did not run the recovery clause the runbook promised it ran

`pre_create()` was reachable only from `--pre-create-check`, a step a human runs. The runbook said
«`--price` will not open a pod the check refused» and the record said the check «refuses the create
itself»; neither was true, and a third pod created without step 0 was recorded with a GO. The
verifiers refuted the *money* half of this — `--terminate-after` still bounds the platform — but a
guard that fires only when someone remembers to ask is the habit rung 5 was bought to remove. Now
`--price` runs the same check on the state **before** this pod joins it, **records the pod either
way** (a pod that exists against no counter is a pod nothing is measuring) and returns KILL with the
delete instruction.

### The mutations, watched

A finding that has never been seen to fail is arithmetic wearing a gate's name. Each fix was
reverted on a scratch copy and the suite re-run:

| mutation | what goes red |
|---|---|
| `projection_gate.overhead_seconds` back to 1 800 | H6 refuses; the producer will not write the record |
| `first_reply_after_launch` always returns `None` | `…without_a_launch_stamp_can_NEVER_report_GO`, `…watch_arms_rung_3…` |
| the `and at_create <= backstop` conjunct deleted | `test_the_create_anchored_BACKSTOP_kills_a_pod_with_a_FRESH_launch_stamp` |
| `--price` ignores the recovery verdict | `test_pre_create_check_refuses_a_THIRD_pod_even_when_the_seconds_would_fit` |

## H6 — 31 rows, and three of them check REASONS rather than numbers

```
  H6: 31 rows, every registered number re-derives
  seconds: ssh 500 + stage/launch 150 + load 450 + generation 3076.552 + overhead 1300
           = 5476.552 = 1.5213 h
  worst case $1.2170 at $0.8/h ($0.8063 at $0.53/h) against a cap of $1.38
  hard stop 6100 s = $1.3556 < cap · session ceiling 1.725 h = 6210 s
  recovery: one dead pod 500 s + the worst case = 5976.552 s ≤ 6100 and $1.3281 ≤ $1.38
            — the widest dead pod that still fits is 623.448 s
  STEP SUM: r1 pods $0.117783 + r2 cap $1.38 = $1.497783 ≤ $1.50
  rungs: 2 → 500 s from create · 3 → 450 s from `launched_at` with a 1100 s create-anchored backstop
```

The three that check a claim the contract makes in prose and no number would otherwise reach:

- `a_600_s_rung_2_would_put_the_recovery_past_the_hard_stop` — 6 176.552 ≥ 6 100. This is the whole
  reason rung 2 is 500. Dv605 shipped a bound that double-counted the ssh wait because nothing
  re-derived it.
- `the_overhead_reduction_is_covered_by_the_new_lines` — ssh 500 + stage/launch 150 = **650 ≥ 500**,
  the amount the overhead fell. Nothing is double-counted and nothing is dropped.
- `rows_copied_back` — 200 + 200 + 64 = **464**, which is what the 1 300 s overhead scp's.

## Verify — outputs, not summaries

```
$ PYTHONPATH=src python3.11 scripts/write_pass1_fewshot_prereg_r2.py
wrote results/prereg_pass1_fewshot_r2.json  sha256 69422f09b62f0362…
  supersedes results/prereg_pass1_fewshot.json bd731e53126b7fbd… — closed at rung 2 twice,
             attempt NOT spent, recovery used
  H6: 31 rows, every registered number re-derives

$ make preflight ARGS='gate_pass1_fewshot.py prereg_pass1_fewshot.json BACKSTOP_TOLERANCE_SECONDS'
QUERY gate_pass1_fewshot.py
[3] pins — 6 of the 15 touched paths are pinned by a record
    scripts/gate_pass1_fewshot.py   <- 2 pin(s): prereg_pass1_fewshot.json…gate.sha256 eda56fdef296…,
                                        prereg_pass1_fewshot_r2.json…gate.sha256 923d8b18aa8a…
    scripts/score_pass1_fewshot.py  <- 1 pin(s): prereg_pass1_fewshot_r2.json
                                        .instruments.scorer_pass1_fewshot.sha256 39b648efba94…
    results/prereg_pass1_fewshot.json <- 3 pin(s): … prereg_pass1_fewshot_r2.json.supersedes.sha256
                                        bd731e53126b…
[4] digests — sha256 of all 6 pinned paths, against what is pinned
    scripts/gate_pass1_fewshot.py  live 923d8b18aa8a4e11…  DIFFERS
        results/prereg_pass1_fewshot.json.instruments.gate.sha256 pins eda56fdef296f58f…
        — the file has moved since                         # the ONE ruled move, and it is r1's pin
    5 of 6 pinned paths match every digest on them

QUERY BACKSTOP_TOLERANCE_SECONDS
    scripts/gate_lora_b.py:199                   BACKSTOP_TOLERANCE_SECONDS = 60.0   # another step
    scripts/write_pass1_fewshot_prereg_r2.py:66  BACKSTOP_TOLERANCE_SECONDS = 60.0   # the producer
    scripts/write_pass1_fewshot_prereg_r2.py:307 "backstop_tolerance_seconds": BACKSTOP_TOLERANCE_SECONDS
    tests/test_gate_pass1_fewshot.py:210         assert "BACKSTOP_TOLERANCE_SECONDS" not in (…)
    # and NOT scripts/gate_pass1_fewshot.py — the name left the gate, and a test keeps it out

$ make check
3265 passed, 2 skipped in 519.18s          # 3239/2 at step 0; +26 tests
$ ruff format --check . && ruff check .
394 files already formatted · All checks passed!

$ git show c7cbfd1:results/prereg_pass1_fewshot.json | shasum -a 256
bd731e53126b7fbd9339585228df1272f14aa36aa613fafa305c7fa1b21fd8b6  -
$ shasum -a 256 results/prereg_pass1_fewshot.json
bd731e53126b7fbd9339585228df1272f14aa36aa613fafa305c7fa1b21fd8b6   # r1 is never edited

$ runpodctl pod list -a && runpodctl serverless list && runpodctl network-volume list
[]
[]
[{"dataCenterId": "EU-RO-1", "id": "qw4nwleanc", "name": "mp-srv2", "size": 100}]   # the control

$ PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-fewshot-r2 --step-cap 1.38
CYCLE 2 SPENT     $6.0739 of $20.00
REMAINING         $13.9261
PASS1-FEWSHOT-R2 SPENT      $0.0000 of $1.38  (anchor $16.44 from runpod_balance_at_pass1-fewshot-r2_start)
  billing since   UNAVAILABLE (no billing rows yet) — the delta stands alone as a LOWER BOUND
```

## Deviations (enum v2)

| # | What | Tag |
|---|---|---|
| **Dv607** | The contract offered `--revision r2` or a sibling producer. **Sibling**, because the r1 producer hashes ITSELF into the record it writes and r1's rebuild is compared byte for byte — a flag on that file moves `producer.sha256` and r1 stops rebuilding, which is the one property acceptance diffs against `c7cbfd1`. | `[cause: process]` `[[provenance_cannot_name_itself]]` |
| **Dv608** | The gate is amended IN PLACE, as the contract names it, so r1's `instruments.gate.sha256` is «moved since». r1's byte-identical rebuild test is NARROWED — not deleted — to an enumerated diff DERIVED from which paths of the rebuild carry the gate's live sha, and a new test asserts the file on disk is still byte for byte `c7cbfd1`. | `[cause: contract-gap]` `[[the_identity_field_stops_covering_the_change]]` |
| **Dv609** | «gate+tests · r2 record» are ONE commit and not two. The record pins the gate's sha and the gate's tests import the record, so every split ordering leaves a red commit — Dv600's reasoning, one contract later. The runbook, the guard anchor and the vault tail stay separate as asked. | `[cause: contract-gap]` `[[a_test_that_reads_a_shipped_artifact]]` |
| **Dv610** | Rung 3's rule has to express two deadlines and the gate reads its threshold POSITIONALLY (`first_number`). The backstop is registered as its own named FIELD the gate reads by key, and a test asserts the ceiling is the first number of the sentence — a reordered clause must not be able to make 1 100 the ceiling. | `[cause: verify-gap]` `[[a_gate_that_checks_position_not_presence]]` |
| **Dv611** | «the runbook stamps `launched_at` into the run directory» is implemented as a file the POD writes and `--watch` copies back, never a flag. A typed stamp is an assertion, and this one can only move a deadline OUTWARD. Written into the pod's entry once and never moved forward; three refusals driven — before create, in the future, unreadable. | `[cause: spec-gap]` `[[a_flag_that_asserts_turns_a_poll_into_a_verdict]]` |
| **Dv612** | **Found in review, before the pod.** The contract moved rung 3's anchor and left r1's `--first-reply-at` recipe (`create + boot_seconds`) in the runbook; `boot_seconds` is measured from the RUNNER's start, so the recipe subtracts ssh+staging twice and a 460 s load reads as 415 s — GO on the condition the amendment exists to catch. `--boot` now takes no stamp and reads `elapsed_since_start` off the out-file. | `[cause: contract-gap]` `[[a_flag_that_asserts_turns_a_poll_into_a_verdict]]` |
| **Dv613** | **The finding that would have cost the session.** `money.arithmetic.cumulative.projection_gate` was copied whole from r1, so rung 4 — which runs on EVERY poll of the watch — charged the repealed 1 800 s overhead against a hard stop r2 lowered to 6 100, and its verdict text still named $1.50 and 6 300 s. On the recovery path the shot's first poll KILLs a healthy pod. Re-derived, with an H6 row and a sweep test for every repealed r1 value in r2's money block. | `[cause: verify-gap]` `[[the_old_record_with_one_field_replaced]]` |
| **Dv614** | The runbook's ssh poll was bounded by an ITERATION COUNT annotated as seconds. r1's own record prices a turn at 6.65 s (34 turns, 226 s of wall clock), so 95 turns is ~631 s — past the 500 s rung AND past the 623.448 s at which the recovery stops fitting. Bounded by the clock now, against rung 2's ceiling read out of the record. | `[cause: verify-gap]` `[[a_paced_log_is_an_interleavable_clock]]` |
| **Dv615** | `pre_create()` was reachable only from `--pre-create-check`, while the runbook and the record both said the create itself was refused. `--price` runs the same check now — recording the pod either way, because a pod that exists against no counter is worse than a pod that should not exist. | `[cause: verify-gap]` `[[the_guard_you_built_and_then_bypassed]]` |
| **Dv616** | `scripts/score_pass1_fewshot.py` carried its own copies of the registration and run-record paths. Left as literals they would have gone on scoring r1's law over r2's session; they are `gate.PREREG` / `gate.RECORD` by reference now, which is also why the scorer's sha moved and is pinned. | `[cause: verify-gap]` `[[preregistration_is_a_file_not_a_constant]]` |
| **Dv617** | The two sealed packs carry `"record": "results/prereg_pass1_fewshot.json"` and are byte-frozen, so they name a superseded law and cannot be rewritten. `supersedes` in the r2 record is what closes the loop; named here so a reader of the packs is not sent to r1 without knowing it. | `[cause: env]` `[[a_citation_is_not_a_record]]` |
| **Dv618** | The guard anchor is taken at session start as the contract asks, so the volume drip across the whole D0′ window lands on r2's balance delta — Dv604's class, expected this time rather than discovered. The gate's own clock is the per-leg figure; the delta is the account's. | `[cause: env]` `[[a_balance_delta_is_not_a_per_leg_cost]]` |
| **Dv619** | The launch stamp's clock-skew allowance REUSES the registered backstop tolerance — one constant answering two questions. It is bounded and named rather than fixed: an accepted stale stamp makes rung 3 fire EARLIER, never later, and the create-anchored backstop reads `backstop_seconds` and never touches the tolerance, so no value of the field can buy a window nobody priced. | `[cause: process]` `[[one_constant_answering_two_questions]]` |
