# pass1-window r2 — the 901 still owed, priced on the POD CLASS

**Contract:** `docs/PROMPT-pass1-window-r2.md` — step 0.5 addendum ($0) → D0′ ($0) → D1 (paid, cap
$2.00) → D2 ($0). **Authority:** the operator's ruling of 2026-08-21 (evening), `docs/STATUS.md`
«Открытые решения» п. 1 (е). Deviations from **Dv659**, enum v2.

---

## Read back first, one line each (the contract's own list)

1. **What step 0.5 corrects and why the scorer is not edited.** The report-only readings of the r1
   census were inflated by `msg_id` collisions: `scorer.reader_comment_agreement` keys its answers
   `{int(msg_id): …}` — last-wins — and seven msg_ids inside `membership.labelled_650` live in two
   threads each, so five twins the pod never reached inherited a namesake's reply. The scorer is
   pinned by sealed records and `leg_table` by four of them, so the census path was fixed instead:
   it scores one THREAD at a time, where a msg_id is unique.
2. **The 901, and how the pack is built without re-rendering.** `results/pass1_window_r2_pack.json`
   is the r1 pack's leg MINUS the 131 ids of `results/pass1_window_v2.jsonl`, each verified against
   its pack item's `rendering_sha256` before its id is subtracted. The items are COPIED — a
   re-render would move the shas the pod's handshake, rung 7 and D2's union census all compare a
   reply against.
3. **The rate, its three files, and the knife edge at both spans.** probe-b's base leg 5.161578
   s/call (64 rows) against r2's base leg 2.293075 (200 rows) is a 2.25× spread on ONE prompt;
   v2 over base on the one pod that ran both is 2.725780 / 2.293075 = 1.188701; charged
   5.161578 × 1.188701 = 6.135572 → **6.14**, rounded up. Rung 4's edge is **6.8812** s/call at the
   pre-generation the budget CHARGES and **7.8219** at the one r1's pod MEASURED.
4. **The worst case, the cap, the hard stop, the recovery, the step sum.** 901 × 6.14 = 5 532.14 s
   of generation + 1 100 + 1 300 = **7 932.14 s = 2.203372 h = $1.762698** at $0.80/h ($1.167787 at
   $0.53). Cap **$2.00**, cumulative hard stop **8 600 s = $1.9111**, session ceiling 9 000 s ≥ it.
   Recovery: one dead pod at rung 2 (500 s, $0.111111) + the full worst case = 8 432.14 s ≤ 8 600
   and $1.873809 ≤ $2.00; widest dead pod **667.86 s** of billed seconds; `re_creations_allowed: 1`.
   Step sum $0.173694 + $2.00 = **$2.173694** on a FRESH guard step.
5. **What the volume's file is and is not.** `/workspace/run/pass1_window_v2.jsonl` on `qw4nwleanc`
   is EVIDENCE: copied back before the run directory is cleared, hashed on both sides, its rows
   beyond the Mac's 131 counted and priced. It is never merged — every one of them is inside the 901
   and is bought again here, and two answers for one id is an ambiguity this registration does not
   buy.
6. **Why there is no separate rate rung.** Rung 4 re-prices the remainder on every poll at
   max(mean, last call) against the hard stop and the cap and kills at the first poll that shows a
   pod that cannot finish. A separate rung reading the same number against the same stop would be
   the same check twice, and two gates on one number is how a threshold gets repealed in one of them.

---

## 0 — baselines, at step 0, from the instrument

```
$ make baselines
## Baselines — instrument output, 2026-08-21T17:12:02+00:00

- head: 45285001abc6 on main
- porcelain:
     M docs/STATUS.md
     M knowledge/daily_logs/2026-08-21.md
     M knowledge/hot.md
     M knowledge/index.md
    ?? docs/PROMPT-pass1-window-r2.md
- census: brain-census: 10.0Ktok boot tax
- suite: 3354 passed / 2 skipped — whole suite, stamped 2026-08-21T17:01:22+00:00 at 45285001abc6
- boot files: ~/.claude/CLAUDE.md 1974 B · ~/CLAUDE.md 23 B · CLAUDE.md 4581 B · knowledge/hot.md 11947 B · MEMORY.md 21623 B = 167 lines / 21301 UTF-16 units
- preflight: 1518 pinned paths · 2635 pins · 116 records — 1482 match every pin on them, 36 carry an older pin
```

---

# Step 0.5 — the acceptance addendum ($0, three commits, before D0′)

The full account is the **ADDENDUM** of `docs/reports/pass1-window.md`; what follows is what it cost
and what it proved.

## The collisions, reconciled to the row

Seven msg_ids of the 650 live in two threads each (`@VARUS_channel` ↔ `@klopotenkofood`); five had
exactly one twin answered. Their contribution to the old numbers:

| what the id-only key did | rows |
|---|---:|
| phantom «answered» — an unanswered twin inheriting a reply | **+5** |
| phantom «agreed» — 21209, whose inherited `null` matched its gold | **+1** |
| phantom «our agreed» — 21211 and 21256, where `our_rows` is a LIST and `agreed_ids` a SET | **+2** |

| reading | as first reported | **corrected** |
|---|---|---|
| the 650 labelled rows | 69 / 117 · «our» 23 / 49 | **68 / 112 · «our» 21 / 49** |
| the 450 not in dev-200 | 35 / 65 | **34 / 64** |
| the dev-200 · the fourteen | 34 / 48 · 4 of 5 reached | unchanged — no collision in either |

**And the correction is corroborated from a code path that knows nothing about it.** The r2 pack's
`membership` is keyed on the pair and says the 650 still owe **538** rows: 650 − 538 = **112**
answered, not 117. Two independent derivations, one number.

**Neither pinned function was touched.** `census_pass1_window.py::labelled_reading` hands `leg_table`
one thread at a time and sums. The test builds the 21209 pair and calls BOTH paths on the same pinned
instrument: the id-only key answers `2 answered / 1 agreed`, the pair answers `1 / 0`. Mutation
watched red — `assert 2 == 1`.

## The refusal that was only ever stdout

`--pre-create-check` printed the KILL that ended the r1 session and returned without calling
`append_gate`. It is now an appended, **recomputed** gate in `results/pass1_window_run.json`
(`pre_create` is pure in both arguments, so every field re-derives), with `state["latest"]` left
where the session ended it. Mutation on `projected_attempt_seconds` watched red.

## The 132nd reply

```
[   754.5s] reply 131/1032 @klopotenkofood:6032#21195                5.2s ·   119 chars · cut    1 · balanced True · finish stop
[   759.2s] reply 132/1032 @klopotenkofood:6035#21205                4.7s ·   108 chars · cut    4 · balanced True · finish stop
```

The census now DERIVES this rather than asserting it. 131 rows in the file, 132 replies in the log,
one id named — and 132 is itself a lower bound, because the log is copied once a poll too.

---

# D0′ — at $0, before any pod

## The rate, and the one assumption in it

```
$ PYTHONPATH=src python3.11 scripts/write_pass1_window_prereg_r2.py
wrote results/prereg_pass1_window_r2.json  sha256 6ed7dbf53dbf623d…
  rate: probe-b 5.161578 × uplift 1.188701 = 6.135572 → charged 6.14 s/call  (the pod class spans 2.2509×)
  generation: 901 × 6.14 = 5532.14 s
  worst case: 7932.14 s = 2.203372 h = $1.762698 at $0.8/h  ($1.167787 at $0.53)
  cap $2.00 · hard stop 8600 s = $1.9111 · session ceiling 9000 s
  recovery: one dead pod at rung 2 + worst = 8432.14 s = $1.8738 · widest dead pod 667.86 s
  rung 4 knife edge: 6.8812 s/call at the CHARGED pre-generation · 7.8219 at the measured — slowest call ever measured 6.214
  bar: answered 901 / 901 · sha 0 · refusals ≤ 9   (the window's own completeness: 1032)
  H6: 46 rows, 0 mismatches
```

**The spread is the silicon, and that is a measurement rather than an inference.** probe-b's 64 rows
and r2's 200 dev-base rows ran the SAME prompt (`pass1_comment_gm4_v1`, sha `5a4a3cb6…`, checked and
a refusal if it ever stops being true) at request widths **5.6 %** apart and reply lengths **1.7 %**
apart — and 2.25× apart in seconds. r1 eliminated five causes AFTER the money; this one is eliminated
before it, as an H6 row.

**The one assumption, named.** The uplift 1.189 is charged as a property of the PROMPT and therefore
transferable across pods, while the base rate is charged as a property of the pod. No run has tested
that: no pod has ever run both legs at both ends of the spread. It is checkable against the r1 window
pod — 4.498473 on v2 implies a base of 3.784, which sits INSIDE the measured spread — and it is
stated rather than hidden.

**The rounding is up, and both values are in the record.** 6.135572 derived, 6.14 charged. Rounding
up grows the worst case and SHRINKS the widest dead pod, so it errs toward refusing a create; it is
also the figure the contract prints and every figure the contract prints is computed at it. An H6 row
asserts `charged ≥ derived` and the producer refuses the other direction (driven).

## What the charged edge buys that r1's did not

| | r1 | **r2** |
|---|---:|---:|
| charged s/call | 3.4075 | **6.14** |
| rung 4's edge at the CHARGED pre-generation | 3.9729 | **6.8812** |
| the slowest single call this stack has ever measured | 4.066 | **6.214** |
| headroom | **0.98 — below it** | **1.11 — above it** |
| the same edge at the MEASURED pre-generation | 4.812 | **7.8219** |

r1 went to the pod with its charged-span edge UNDER the worst call it had measured, reported that to
the operator, and was told to proceed. This registration's edge is above it at both spans.

## The pack: a subtraction, and nothing re-rendered

```
$ PYTHONPATH=src python3.11 scripts/build_pass1_window_r2_pack.py
wrote results/pass1_window_r2_pack.json  sha256 7ec190a9d70964b7…
  owed: 901 of 1032 payable comments — 131 answered by r1 and subtracted by id, each verified by sha
  one leg v2 → pass1_window_r2_v2.jsonl · 901 items · 100 threads carry one (27 finished by r1)
  length: widest 8562 chars (@matusi_ukr:22133#577621) · median 4481 · headroom 3438 of 12000
  self-exclusion: 0 items shown their own thread · 523 distinct neighbours used
  membership here: gold_14 9 of 14 · probe_64 47 of 64 · labelled_650 538 of 650 · dev_200 152 of 200
```

**The property the whole subtraction rests on is checked end to end:** all 901 items re-render
through the SHIPPED runner on this checkout to exactly the shas r1's pack pinned
(`test_ALL_901_items_re_render_to_the_shas_r1s_pack_PINNED`). Not a structural argument — the
renderer, run.

## The gate: a sibling that EXECUTES r1's bytes

`scripts/gate_pass1_window.py` is pinned by r1's sealed record, so `--revision r2` was not available
and the contract's fallback — «otherwise a sibling, and say which» — applies. **Which:** the sibling
`importlib`-loads that same source under its own module object, holds it to the sha r1's record pins
BEFORE executing it, and re-binds six path globals (`PHASE`, `PREREG`, `RECORD`, `PACK`, `POD_LOG`,
`LAUNCH_STAMP`). The rung logic is not copied and not re-implemented; it is r1's, executing, against
this registration.

The alternative was r1's own shape — import the pure computations, re-declare the path-bound ones —
which for this file is **569 lines** of `watch`, `main`, `registration`, `run_state`, `save`,
`append_gate`, `tolerance`, `terminate_after` and `launched_at_of`. A copy is where two instruments
start to disagree about the same question, and this one runs the audited bytes by construction.

Three properties, each with a test: `sys.modules` is untouched so the r1 census still imports r1's
module with r1's paths (negative control on all six globals); the pure rungs are the SAME OBJECTS and
the path-bound ones are distinct; and a moved r1 gate is a refusal, not a silent substitution.

**One behaviour changed:** `--pre-create-check` records its verdict, GO and KILL alike.

## The Dv613 sweep, and the threshold audit path by path

`6500`, `3.4075`, `5916.54`, `583.46`, `1.50` and `1.25` appear as NUMBERS **nowhere** in this
record's money block; `supersedes.its_numbers_this_record_REPEALS` quotes them by name. Beyond the
sweep, every numeric leaf that sits at the SAME PATH with the SAME VALUE in both money blocks is
matched against a table of reasons — 60 of them, all measured readings or carried spans — and a path
matching none of them fails the audit. 63 paths moved.

## Verify — outputs, not summaries

```
$ make preflight ARGS='gate_pass1_window.py prereg_pass1_window_r2.json'
[3] pins — 6 of the 19 touched paths are pinned by a record
    scripts/gate_pass1_window.py  <- 2 pin(s): results/prereg_pass1_window.json.instruments.gate.sha256 8b812597c4ea…, results/prereg_pass1_window_r2.json.instruments.gate_runs_the_bytes_of.sha256 8b812597c4ea…
    scripts/gate_pass1_window_r2.py  <- 1 pin(s): results/prereg_pass1_window_r2.json.instruments.gate.sha256 11322f38e985…
    scripts/write_pass1_window_prereg_r2.py  <- 1 pin(s): results/prereg_pass1_window_r2.json.producer.sha256 9242c5f868b7…
[4] digests — sha256 of all 6 pinned paths, against what is pinned
    6 of 6 pinned paths match every digest on them

$ PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --completeness   # before the commit
results/prereg_pass1_window_r2.json is not tracked by git. Until it is committed, nothing stops it
being rewritten once the numbers are in — commit it BEFORE `pod create`.

$ make check
3421 passed, 2 skipped in 523.74s (0:08:43)
```

The suite went 3 354 → 3 421: **+67 tests**, four of them step 0.5's and sixty-three D0′'s — fifty-seven for the pack, the record and the gate, and six that drive D2's union census at $0 on a complete run and on one that stops half way.

---

## The review before the pod: five lenses, 14 findings, 3 survivors

Five lenses — rung logic · arithmetic · what must not move · do the tests fail when the logic breaks ·
clause-by-clause compliance — each finding attacked by a skeptic instructed to default to «refuted»
when uncertain. **14 raised, 3 survived.** Two of the eleven refused ones conceded the arithmetic
outright and refused only on the «costs money» trigger; both were fixed anyway, because a wrong
number in the record that is the law for every rung is a wrong number.

### The survivors, and the mutation each fix carries

| # | what it was | mutation watched red |
|---|---|---|
| 1 | **The worked example is priced at the MEASURED span.** «A pod at 8 s/call dies ≈ 20 calls in, ≈ $0.10, re-creation still reachable» — true at 252.5 s of pre-generation and FALSE at the 1 100 s the budget charges, where the same kill bills 1 260 s and the re-creation is refused. The deciding number was never computed. | the both-arms test asserts `charged + tail > widest_dead_pod` and `measured + tail ≤ it`; the record and the runbook both carry the table |
| 2 | **Rung 2/3/5/6's deadlines are parsed out of PROSE** by `first_number(rule)`. Four words in front of rung 5's rule made the live idle deadline **5 s** with the whole suite green — a single failed scp then kills a healthy pod and burns the one re-creation. | prepended «rung 5 of 7 — »: `assert 5.0 == 600.0` |
| 3 | *(the same defect as 1, raised independently by a second lens)* | — |

**What the first one produced.** The record now derives **589.36 s** — the widest CREATE-ELAPSED at
which any kill leaves the re-creation reachable, which is the widest dead pod in BILLED seconds less
the charged 78.5 s deletion tail — and says which rungs are inside it:

| the kill | bills | recoverable? |
|---|---:|---|
| rung 2, the ssh dead-man | ≤ 578.5 s | **always** |
| rung 4 at 8 s/call, 20 calls in, pre-generation 252.5 s | 491.0 s | **yes** |
| rung 4 at 8 s/call, 20 calls in, pre-generation 1 100 s | 1 338.5 s | **no — STOP** |
| rung 3's create-anchored backstop | 1 178.5 s | **never** |

Four new H6 rows carry the inequalities, including one that exists purely so a sentence cannot come
back: **r1's record said «a KILL at rung 2 or rung 3 is inside that window» and the second half was
never true at these spans.** Two lenses raised that independently; both skeptics conceded the
arithmetic.

### And the tenth defect the review did not have to find, because I found it first

The runbook's launch command told the pod to write `/workspace/run/pass1_window_r2_launched_at` — the
LOCAL name. `--watch`'s own `pull()` copies `<remote-dir>/launched_at`, a literal in r1's gate. Rung 3
would have had no anchor, `--boot` would have been a KILL rather than a WAIT, and the create-anchored
backstop would have been the only bound left. Three tests now grep the runbook against the gate's own
source; the mutation putting the wrong name back was watched red.

---

## Deviations (enum v2)

| # | What | Tag |
|---|---|---|
| **Dv659** | **The report-only readings of the r1 census were keyed on the msg_id alone.** `scorer.reader_comment_agreement` builds a last-wins `{int(msg_id): …}` and `leg_table` derives `agreed_ids` as a SET of msg_ids while `our_rows` stays a LIST — and seven msg_ids of the 650 live in two threads each. Five twins the pod never reached inherited a reply: 650 → 112/68/21 from 117/69/23, 450 → 64/34 from 65/35. Neither pinned function was edited; the census scores one THREAD at a time. The r2 pack's own pair-keyed membership corroborates 112 from a code path that knows nothing about the fix. | `[cause: verify-gap]` `[[id_spaces_that_look_comparable]]` |
| **Dv660** | **`--pre-create-check` printed the refusal that ENDED the r1 paid session and recorded nothing.** No gate entry, no run-record key — the only copy was a paste in the report. Appended as a recomputed gate (`pre_create` is pure in both arguments, so every field re-derives) with `latest` untouched; from r2 on the guard records its verdict at the moment it runs. | `[cause: contract-gap]` `[[gate_verdicts_need_an_artifact]]` |
| **Dv661** | **The pod log reaches one reply further than the out-file beside it.** Dv657 reported 131 as a lower bound and could not name what was missing; the r1 log names `@klopotenkofood:6035#21205` at 759.2 s. The census now DERIVES the difference from the log rather than asserting it — and 132 is itself a lower bound, because the log is copied once a poll too. | `[cause: env]` `[[a_retry_inherits_the_last_attempts_output]]` |
| **Dv662** | **A fourth wrong figure in the r1 report, found while checking the other three.** Its rate table prints the window leg's minimum as 3.799 s; the file's minimum is **3.780** and 3.799 is the second-smallest. Nothing in the argument moves — it runs on the mean and the maximum — and it is named because a fourth one left unnamed is the same class the addendum was correcting. | `[cause: verify-gap]` `[[rederive_doc_numbers]]` |
| **Dv663** | **The gate is a sibling of an unusual kind, and the kind is the deviation.** `scripts/gate_pass1_window.py` is pinned by r1's sealed record, so a `--revision r2` flag was unavailable. Rather than re-declare 569 lines of path-bound code — r1's own sibling shape — this one `importlib`-loads that source under its own module object and re-binds six globals, after holding it to the sha r1's record pins. The rung logic is r1's, executing, not a copy that can drift. Three tests hold the isolation, the sha guard and the shared-object identity of the pure rungs. | `[cause: process]` `[[the_guard_hashes_the_half_that_cannot_move]]` |
| **Dv664** | **The charged rate and the derived rate are two fields, on purpose.** The derivation gives 6.135572 and the contract prints 6.14; the record carries both, an H6 row asserts `charged ≥ derived`, and the producer refuses the other direction. Rounding UP grows the worst case and shrinks the widest dead pod, so it errs toward refusing a create. This is the class that was quoted kindly three times inside r1's own contract; here it is structurally impossible to quote the wrong one. | `[cause: process]` `[[two_values_for_one_input_get_quoted_kindly]]` |
| **Dv665** | **The refusal ceiling moved with its FRACTION and not with r1's count.** r1 registered «≤ 10 (1 %)» over 1 032 rows; 1 % of 901 is **9**. Carrying the count across a population that shrank by 131 rows would have been a threshold that quietly stopped meaning what it said. | `[cause: spec-gap]` `[[a_moved_constant_fails_green]]` |
| **Dv666** | **The runbook told the pod to write the LOCAL name of the launch stamp.** `--watch`'s `pull()` copies `<remote-dir>/launched_at` — a literal in r1's gate — into `results/<LAUNCH_STAMP>`, so the remote name is fixed by the gate and only the local one is this attempt's. Rung 3 would have had no anchor and `--boot` would have been a KILL. Found before the review, fixed, and three tests now grep the runbook against the gate's own source. | `[cause: verify-gap]` `[[a_report_proves_it_does_not_instruct]]` |
| **Dv667** | **The contract's own D0′ test line is arithmetically unsatisfiable.** «A pod at 6.9 s/call after 20 rows → rung 4 KILL with re-creation still allowed» cannot hold: at 20 answered rows the minimum rate for which a KILL still leaves the clause reachable is **7.528 s/call ignoring the deletion tail and 7.6171 with it**. What was implemented instead is BOTH arms — 6.9 s/call is a KILL at the charged pre-generation (where the re-creation is already refused) and a GO at the measured one — with the breakeven derived rather than typed. Returned to the operator. | `[cause: contract-gap]` `[[an_expectation_no_reading_reaches]]` |
| **Dv668** | **The five-lens review's survivor, and it is the span defect a FOURTH time in this programme.** «A pod at 8 s/call dies ≈ 20 calls in, ≈ $0.10, re-creation still reachable» is true at the pre-generation r1 MEASURED and false at the one the budget CHARGES, where the same kill bills 1 260 s against a 667.86 s allowance. The deciding number — 589.36 s of create-elapsed — was never computed anywhere. It is now derived, published in the record and the runbook, and carried by four new H6 rows; one of them exists so that r1's «a KILL at rung 2 or rung 3 is inside that window» — false for rung 3 at these spans, conceded by two skeptics — cannot come back. | `[cause: verify-gap]` `[[a_ceiling_derived_from_one_span_measured_over_another]]` |
| **Dv669** | **Four rung deadlines are properties of PROSE.** `watch` and `gate_boot` read them with `first_number(rule)` — the first digit-run of a sentence — so prepending «rung 5 of 7 — » to one f-string made the live idle deadline **5 s** with all 3 415 tests green. A healthy pod would then die on the first poll that shows no new row, which is what one failed scp looks like, spending the money and burning the one re-creation. The parse is now pinned for rungs 2, 3, 4, 5 and 6, and rung 5 is DRIVEN to fire on an out-file that stops growing — the existing loop test grew the file on every poll, so rung 5 could not fire at any deadline value. | `[cause: verify-gap]` `[[a_checker_whose_failure_is_silence]]` |
| **Dv670** | **The `at` of the appended gate was typed, not read.** It carried `2026-08-21T21:34:00+00:00` — three hours ahead of the machine clock and four hours after the file was written. Every other field of that entry is recomputed and asserted; `at` is one of the four `append_gate` adds and fell outside the loop. It is now taken from the clock the way `append_gate` takes it, with a field naming what it is, and the test pins it between the last gate the session really recorded and now. The review raised it and its skeptic refused it on the «costs money» trigger while conceding the fact; it was fixed anyway. | `[cause: process]` `[[session_metadata_is_queried_not_recalled]]` |
| **Dv671** | **D2's union census exists and is driven at $0 BEFORE the money, on two shapes.** r1's census is where the same defect turned up three times in one sitting, and all three came from a run that ended early. `scripts/census_pass1_window_r2.py` builds the union 131 + 901 as a VIEW — two out-files' lines written into one scratch copy under the r1 pack's leg name, never merged on disk — and is exercised on a complete run (the window closes at 1 032) and on a run that stops half way (every count says so). The paid session only fills it in. | `[cause: process]` `[[a_run_that_ends_early_adds_a_third_state_everywhere]]` |
| **Dv672** | **The volume tail was not in `frozen_when_the_pod_exists`.** It becomes evidence the moment step 3a copies it back, and the directory it came from is cleared by this attempt's first pod — so it is the only place its extra rows exist, and nothing in the record protected it from a later re-creation's cleanup. Added to the frozen list and named in the runbook's recovery section. | `[cause: contract-gap]` `[[fetch_before_you_delete]]` |

---
