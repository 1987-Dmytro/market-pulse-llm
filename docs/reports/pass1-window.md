# pass1-window — RED at rung 7, killed by rung 4, and the rate is a property of the POD

**The completeness bar is RED: 131 of 1 032 answered.** One pod, `xpz3zb7yxus5cw`, 845.0 s,
**$0.173694 of the $1.50 cap**. Rung 4 deleted it at 131 rows because the projection left the 6 500 s
hard stop — while the cap was never near it, $1.3948 of $1.50. The recovery clause then REFUSED on
seconds, so there is no second pod and the question returns to the operator.

**Nothing was lost that a bar owns.** The transport is clean — 131 replies, 131 parsed, 0 sha
mismatches, 0 refusals, 0 duplicates. The out-file, its census and the per-thread pass-2 table are on
disk and committed. No gold row was scored against a threshold, and the fourteen the pod did reach
are a census row with their multiplicity named.

**The one reading that outlives the RED:** this pod ran at **4.498 s/call against the 2.726 the
registration's sample measured — 1.65×** — with the request width, a cold leg, the prompt, the card
model, the datacenter and the population each ruled out in turn. A rate is a property of the pod it
was measured on, and `pass2-signals` and every future window pass must be priced on that.

## Read back first, one line each (the contract's own list)

* **The population and who derives it** — 1 032 payable comments of 129 threads, cell
  `narrow|varto_off|plus_spam+scam`, derived by CALLING `gate_census_w1_reader.population()`. It was
  called; it returned exactly that; the contract's figures are the expectation the producer refuses
  on, never the source.
* **The five neighbours and what they exclude** — one nearest labelled comment per class (four
  subject types + null) by Jaccard over lower-cased character 3-grams, from the 650 labels MINUS
  every row of the query's own thread. A comment never sees its own label or its thread's.
* **The completeness bar, three numbers** — answered 1 032 / 1 032 by DISTINCT id · every row's
  `rendering_sha256` equals its pack item's, 0 mismatches · parse refusals ≤ 10 (1 %), counted by
  cause and never dropped.
* **Why the fourteen are a census row and never a bar** — this is the FOURTH look at the same
  fourteen (base 9/14, arm A 9/14, v2 registered and never fired, v2 inside a production pass). The
  multiplicity is in `return_to_the_operator`, the ADR binds the team lead to it, and the producer
  is deliberately the comparison WITHOUT its threshold arm so no `passed` field can exist.
* **The worst case, the cap, the hard stop, the recovery arithmetic** — 5 916.54 s = 1.6435 h =
  **$1.3148** at $0.80/h; cap **$1.50**; cumulative hard stop **6 500 s = $1.4444**; one dead pod at
  rung 2 (500 s = $0.1111) + the full worst case = 6 416.54 ≤ 6 500 and $1.4259 ≤ $1.50; the widest
  dead pod that still fits is 583.46 s. **With r1's measured deletion tail it is 578.5 s and the
  margin is 4.96 s, not 83.46** — see Dv631.
* **The liveness rung** — 600 s with no new answered row and no new pod-log line → KILL, measured
  from the LAST EVENT, held by a blocking `--watch` the executor does not leave.
* **Which record blocks are COPIED from r2 and which are new** — copied: `instruments` (every pin
  re-resolved against the live file, two re-pinned by name, one dropped with its reason), the
  kill-clock rungs by name, the allowances 500/150/450/1 300 and the 60 s tolerance. New:
  `population`, `bars` (a completeness bar and a report-only block, no dev gate), `money` with
  1 032 calls and a 6 500 s stop, `return_to_the_operator`, `what_this_run_is_not`, `attempt`.

## 0 — baselines, at step 0, from the instrument

```
## Baselines — instrument output, 2026-08-21T14:17:41+00:00

- head: c5eb5eaa1e4e on main
- porcelain:
     M docs/STATUS.md
     M knowledge/daily_logs/2026-08-21.md
     M knowledge/hot.md
     M knowledge/index.md
    ?? docs/PROMPT-pass1-window.md
- census: brain-census: 10.0Ktok boot tax
- suite: 3266 passed / 2 skipped — whole suite, stamped 2026-08-21T14:03:20+00:00 at c5eb5eaa1e4e
- boot files: ~/.claude/CLAUDE.md 1974 B · ~/CLAUDE.md 23 B · CLAUDE.md 4581 B · knowledge/hot.md 12439 B · MEMORY.md 21176 B = 164 lines / 20860 UTF-16 units
- preflight: 1513 pinned paths · 2612 pins · 113 records — 1478 match every pin on them, 35 carry an older pin
```

The porcelain is the team lead's own tail and the untracked contract; both went into the first
commit verbatim, `4714e4d`, before any executor file existed.

## The six checks that came before any code

Each one could have reshaped D0, and one of them is the whole contract's foundation.

| check | reading |
|---|---|
| `population()` — CALLED, not typed | **129 threads / 1 032 payable comments**, exactly the contract's figures. 2 threads carry no payable comment; the widest carries 125. |
| `PASS1_MAX_INPUT_CHARS` | 12 000, as the contract types it. The window's widest rendered request is **8 562** — headroom 3 438, median 4 456, no breach. |
| the pod runner on a one-leg pack | `--only` already exists and narrows without reordering. **There is no finding**, and the pack is driven through the unedited runner on a fake transport in the suite. |
| `sft.request()`'s shape | takes `{thread, msg_id, text, store}`; the store is `build_pass1_label_pack_r2.raw_threads()`, the SFT producer's own. Asserted equal to the census's record on the post and on every payable comment's text, one at a time. |
| the two `молочный_бренд` rows | they sit in **two different threads** (`@VARUS_channel:10367`, `@mandziak:3721`), so `neighbours()` can never run out of that class for any query. No build-time STOP. |
| the `pass1-window` step ledger | did not exist. The step opens with **no pods of its own**, so the step cap and the contract cap are the same $1.50, and `pass1-fewshot`'s $0.397133 stays in its own closed step. |

**Four subsets are all inside the population, checked**: the fourteen gold rows (14/14), probe-b's
sixty-four (64/64), the 650 labelled rows (650/650) and the dev-200 (200/200) — so every report-only
reading D2 owes has its rows.

## The strongest D0 verification, and it was not asked for

The 200 dev rows are in this population, and **the window pack renders all 200 byte for byte as the
dev pack did — the same `rendering_sha256`, 200 of 200.** That makes r2's own 200 v2 replies valid
rows of this contract's out-file, so both halves of D2 were driven at $0 on replies a pod actually
generated:

```
RUNG 7 on 200 REAL replies:  GO | answered 200 | parsed 200 | sha mismatches 0 | refusals 0 {}
D2 READING through gate_pass1_fewshot.leg_table:
        agreed 136/200 (0.6800) · our 38/49 · refused 0 · absent 0
r2 reported: agreed 136/200 (0.6800) · our 38/49        REPRODUCES: True
```

The completeness bar and the report-only reading are therefore not promises. Both are in the suite
(`test_rung_7_and_D2s_reading_are_driven_on_r2s_REAL_replies`), and the reproduction is what proves
the instrument is the same one — a structural argument would not have.

It also surfaced a real D0 defect: `leg_table` reads `bars.dev_gate.our_readings`, a key this record
does not have and must not invent. See Dv626.

## Rung 4 and the span I quoted the wrong one of

**This is the finding of the session and it was aimed at my own work.**

Rung 4 prices every call still owed at the LARGER of the leg's mean and its LAST call, so one slow
reply is priced as if all of them were that slow. I found the knife edge, registered it in
`money.arithmetic.cumulative.projection_gate.single_call_sensitivity`, and wrote a headline that
said «the edge sits 1.19× above the slowest call measured — margin, not comfort».

The review's arithmetic lens, and then its skeptic, took the same block apart on one point: the
curve was computed at r2's **MEASURED** pre-generation (254.6 s), and the same record **CHARGES**
1 100 s for that span — and makes the same 1 100 rung 3's create-anchored backstop. At the value the
budget pays for:

```
(hard_stop − overhead − pre_generation) / calls  =  (6500 − 1300 − 1100) / 1032  =  3.9729 s/call
the slowest call this stack has ever measured                                    =  4.066  s/call
```

The measured worst is **above** the sustained rate the hard stop can pay for. Driven on the real
`projection()` with the real 1 032-item pack, one 4.066 s call landing as the most recent row:

| pre-generation at the first reply | 10 answered | 50 answered | 200 answered |
|---|---|---|---|
| 254.6 s (r2's own reading) | GO 5 737 s | GO 5 684 s | GO 5 483 s |
| 700 s | GO 6 183 s | GO 6 129 s | GO 5 928 s |
| 1 050 s | **KILL 6 533 s** | GO 6 479 s | GO 6 278 s |
| 1 100 s (what the budget charges) | **KILL 6 583 s** | **KILL 6 529 s** | GO 6 328 s |

The dollars never bind — $1.35 of $1.50 at the kill point. **The seconds bind**, because the hard
stop is 6 500 against a worst case of 5 916.54 and the projection spends that 583.46 s of slack on
the spike. And a KILL past 583.46 s of billed seconds ALSO refuses the re-creation, so the session
would close with no verdict on a run that was working.

**What was done.** The block now computes both arms and publishes the worse as the headline —
headroom **0.98**, not 1.19 — with what it costs and what the executor can do about it. Nothing was
loosened: `leg_state` and `projection` are r2's, pinned by its sealed record, and pricing the
remainder at the mean is the permissive direction these rungs exist to close.

**What the executor can do, and it is real.** The charged 1 100 is ssh 500 + stage/launch 150 + load
450, and the staging half is HAND-DRIVEN — probe-b bounds ssh + staging + launch together at
≤ 89.5 s and r2's whole pre-generation was 254.6 s. Every second between the ssh GO and the launch
is a second rung 4 will not lend to the rate. The runbook now carries the table and reads
`first_reply_at_create_elapsed_seconds` off rung 3's GO, so the executor knows which world the pod
is in before the generation is far along.

**What returns to the operator.** A hard stop of **6 700 s is $1.4889 — still inside the registered
$1.50 cap** — and puts the charged-span edge at 4.167 s/call, above the measured worst. That is a
change to a number `docs/PROMPT-pass1-window.md` prints, so it is a re-registration and the
operator's word. **It was not taken here.** The contract as written is executable and the risk is
inside its own arithmetic; it is named rather than absorbed.

## The review before the pod: 21 findings, 12 standing, and a caveat on the count

Five lenses — rung logic · arithmetic · what must not move · do the tests fail when the logic breaks
· clause-by-clause compliance — each attacked by a skeptic instructed to default to «refuted» when
uncertain. 21 raised, 12 survived.

**The count is not the evidence, and here is why.** Several fixes landed while the review was still
running, so the skeptics read already-corrected code and refuted findings that had been real an hour
earlier. A «refuted» verdict on any of those is worth nothing. What every fix below rests on instead
is a demonstration the executor ran and can show: a grep that found no guard, a measured number
beside a wrong one, a bisected threshold, a mutation watched red. **Nine defects were found and
closed before the money, and none of them is asserted.**

### The mutations, watched

Every fix carries one, run and seen RED:

| fix | mutation | what went red |
|---|---|---|
| gold keyed on the pair | key on `msg_id` alone | the collision test names `@klopotenkofood:6031#21164` as the extra row |
| the pod recorded before the refusal | restore the old order | the test dies on a run-record file that does not exist |
| the pack held to its sha | `if False:` around the guard | a tampered pack is graded instead of refused |
| `.resolve()` on both paths | `==` instead | the detour case passes an impostor |
| `min` in `first_reply_after_launch` | `max` | a 140 s boot reads as 900 and KILLs |
| all three `store_agrees` refusals | — | each driven; the green path first, then each refusal |

## Verify — outputs, not summaries

```
$ PYTHONPATH=src python3.11 scripts/build_pass1_window_pack.py
wrote results/pass1_window_pack.json  sha256 …
  population: 129 threads · 1032 payable comments  (contract 129 · 1032)
  one leg v2 → pass1_window_v2.jsonl · 1032 items · 2 threads carry no payable comment
  length: widest 8562 chars (@matusi_ukr:22133#577621) · median 4456 · headroom 3438 of 12000
  self-exclusion: 0 items shown their own thread · 968 items had 15583 labels withheld · 545 distinct neighbours used
  balance: {'молочный_бренд': 1032, 'сеть_ритейлер': 1032, 'категория_личное': 1032, 'не_наш_рынок': 1032, 'null': 1032}
  membership: gold_14 14 · probe_64 64 · labelled_650 650 · dev_200 200
  context: envelope 161 chars · 122 of 129 cell threads carry a bought verdict · 121 of 127 that carry an item

$ PYTHONPATH=src python3.11 scripts/write_pass1_window_prereg.py
  generation: 1032 × 3.4075 s = 3516.54 s   (measured mean 2.72578 over 200 dev rows, pod 8tpx8lf05n6skc)
  worst case: 5916.54 s = 1.643483 h = $1.314787 at $0.8/h  ($0.871046 at $0.53/h)
  cap $1.50 · hard stop 6500 s = $1.4444 · session ceiling 6750 s
  recovery: one dead pod 500 s ($0.111111) + the worst case = 6416.54 s ≤ 6500 and $1.425898 ≤ $1.50
            · widest dead pod that fits 583.46 s
  bar: answered 1032/1032 · sha mismatches 0 · parse refusals ≤ 10
  H6: 35 rows · 0 mismatches — every registered number re-derives

$ make preflight ARGS='gate_pass1_window.py prereg_pass1_window.json'
[3] pins — 3 of the 10 touched paths are pinned by a record
    scripts/build_pass1_window_pack.py  <- results/pass1_window_pack.json.producer.sha256 cc8e2343dd01…
    scripts/gate_pass1_window.py        <- results/prereg_pass1_window.json.instruments.gate.sha256 8b812597c4ea…
    scripts/write_pass1_window_prereg.py <- results/prereg_pass1_window.json.producer.sha256 de2c85cb8cfc…
[4] digests — 3 of 3 pinned paths match every digest on them

$ PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --pre-create-check
  verdict GO · pods_opened 0 · re_creations_allowed 1
  projected_attempt_seconds 5916.54 of 6500 · projected_attempt_usd 1.314787 of 1.50
  widest_dead_pod_that_still_fits_seconds 583.46
  next: create with --terminate-after = create + 6500 s

$ PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-window --step-cap 1.50
CYCLE 2 SPENT     $6.3837 of $20.00      REMAINING  $13.6163
PASS1-WINDOW SPENT      $0.0000 of $1.50   (anchor $16.13, committed before any endpoint existed)
```

`--pre-create-check` runs the real `registration()`, which refuses while the record is untracked or
differs from HEAD — so its GO is also the proof that the plan predates the money.

## Deviations (enum v2)

| # | What | Tag |
|---|---|---|
| **Dv623** | The pack producer is a SIBLING of `build_pass1_fewshot_packs.py`, not a mode of it. That producer hashes ITSELF into two sealed packs, so a parameter added to it stops both rebuilding byte for byte. It is IMPORTED instead — `neighbours` / `rendered_item` / `context` / `pool` / `balance` / `ceiling_check` — so the window is rendered by the dev leg's own functions. | `[cause: process]` `[[provenance_cannot_name_itself]]` |
| **Dv624** | The gate is a sibling too, and the split is enumerated in its docstring. Imported: every rung computation that is a pure function of the record and state. Re-declared: `registration` / `run_state` / `save` / `append_gate` (they bind to r2's PREREG and RECORD — importing them would have this run WRITE INTO a sealed record), `tolerance` / `terminate_after` (their refusal names the registration), `launched_at_of` (reads its stamp by NAME, and r2's name is on a stale file in `results/`), `first_reply_after_launch` (r2's read `population.dev.legs[0]`), `watch` (it calls `launched_at_of`). The negative control is a sentinel in r2's record path that the whole flow is driven over. | `[cause: contract-gap]` `[[rewriting_a_record_resets_state_you_do_not_own]]` |
| **Dv625** | **Found by a test.** `threads_with_a_bought_verdict` was one field over two denominators: 122 of the cell's 129 threads, but 121 of the 127 that actually carry an item — two threads carry no payable comment and one of THEM has a verdict. Both counts are published now, with why they differ. | `[cause: verify-gap]` `[[count_the_kind_not_the_rows]]` |
| **Dv626** | **Found by driving D2 at $0.** `gate_pass1_fewshot.py::leg_table` — the function D2's clause names — reads `bars.dev_gate.our_readings`, a key this record does not have and must not invent, because this contract has no dev gate. `bars.report_only.our_readings` carries the two labels and D2 hands `leg_table` a view under the name it reads. Without it D2 would have re-implemented the comparison after the money. | `[cause: contract-gap]` `[[a_registered_bar_may_have_no_producer]]` |
| **Dv627** | **Found by a test.** The overhead's REASON row scaled r2's measured post-last-row span by the rows it covered, and named «464 → 1 032» while dividing by 400. r2 REGISTERED 464 (400 dev + the shot's 64) and MEASURED 400, because its shot never fired. The scaling divides by the MEASURED count — the smaller denominator, the more expensive per row — and both numbers are now named. | `[cause: verify-gap]` `[[a_count_in_prose_is_not_the_enumeration]]` |
| **Dv628** | The contract buys the ×1.25 margin «for the window's larger entity blocks» and nothing re-derived that reason. Measured on the two packs: entities per request **0.96 → 1.80**, and the rendered request they sit in **4 672.4 → 4 725.8 chars, a ratio of 1.0114**. The margin is bought against a growth an order of magnitude smaller than itself, and it is an H6 row now rather than a sentence. | `[cause: spec-gap]` `[[a_borrowed_rule_carries_an_unstated_population]]` |
| **Dv629** | **Found in review, before the pod.** `--price` recorded the pod AFTER `terminate_after` could refuse — and by the time it refuses the pod exists and is billing. An overshooting `--terminate-after` left a LIVE endpoint in no ledger, no rung and no `--pre-create-check`, under a comment claiming «the pod is RECORDED either way». The pod is written FIRST now and the refusal is a recorded rung-1 KILL carrying the delete command. | `[cause: verify-gap]` `[[the_guard_you_built_and_then_bypassed]]` |
| **Dv630** | **Found in review, before the pod, and it would have cost the session.** `single_call_sensitivity` computed rung 4's knife edge at the MEASURED pre-generation (254.6 s) and claimed 1.19× of margin, while the same record CHARGES 1 100 s for that span. At the charged value the sustained rate is 3.9729 s/call against a measured worst call of 4.066 — headroom **0.98**. Both arms are computed now, the worse is the headline, and the trade that would fix it (6 700 s = $1.4889, inside the cap) is the operator's. | `[cause: verify-gap]` `[[a_ceiling_derived_from_one_span_measured_over_another]]` |
| **Dv631** | **Found in review, before the pod.** The recovery clause charged rung 2's CEILING (500 s) and the meter stops at `pod delete`, not when the rung fires. r1's own gate record measures the two tails at **78.5 s and 0.1 s**; the worse is charged, so a real rung-2 death bills 578.5 s and the honest margin under the hard stop is **4.96 s**, not the 83.46 the ceiling alone implies. | `[cause: verify-gap]` `[[a_ceiling_derived_from_one_span_measured_over_another]]` |
| **Dv632** | **Found in review, before the pod.** The runbook's staging step wiped `/workspace/run` on every pod — deleting, on a re-creation, the replies the recovery clause promises the resume keeps. A re-creation now clears only the dead pod's CLOCKS (`launched_at`, `pod.log`) and COUNTS the surviving out-file; the wipe is the first pod's and only the first pod's. | `[cause: contract-gap]` `[[a_retry_inherits_the_last_attempts_output]]` |
| **Dv633** | **Found in review, before the pod.** «A KILL mid-leg costs the boot, not the leg» is only reachable while the dead pod billed under 583.46 s — `--pre-create-check` prices a re-creation at the FULL worst case ahead and not at the calls that remain. Registered as a named window rather than left as an unconditional promise. It is the registration's arithmetic and not a defect: pricing at «only what remains» would open a run the cap closes. | `[cause: spec-gap]` `[[the_contracts_scope_is_narrower_than_the_rulings]]` |
| **Dv634** | **Found in review, before the pod.** `entity_block_chars` was `len(str(entities))` — a Python dict repr with quotes, braces and `: ` the renderer never emits: **1 268 chars where the renderer contributes 393**, on the widest thread. It prices `pass2-signals`. Measured now by rendering the same item with the block and without it — and the record says it SIZES pass 2's context and does not price its call, because pass 2's prompt does not exist yet. | `[cause: verify-gap]` `[[a_literal_below_the_minimum_is_a_unit_error]]` |
| **Dv635** | **Found by the advisor, confirmed by measurement.** `gold_14` was keyed on `msg_id` alone while its three sibling sets use `(thread, msg_id)`. A msg_id is unique per CHANNEL: **13 msg_ids of this population are carried by two threads each.** The two keys select the same fourteen here — that is a reading of this population, not a property of the key — and the pair key is used everywhere now, with the collisions recorded. | `[cause: verify-gap]` `[[id_spaces_that_look_comparable]]` |
| **Dv636** | **Found in review, before the pod.** The gate held the pack to its COUNT and never to the sha the record pins — while rung 7 grades every reply's `rendering_sha256` against that very file. A pack rebuilt with the same 1 032 rows and a different rendering would have passed. Guarded, and the guard compares `.resolve()` on both sides: `--pack results/…` typed from the repo root is a RELATIVE Path and `==` would have skipped the check on exactly that spelling. | `[cause: verify-gap]` `[[the_guard_hashes_the_half_that_cannot_move]]` |
| **Dv637** | **Found in review, before the pod, and deeper than reported.** The fourteen are a D2 reading with no producer: `leg_table` compares against the LABEL map and **0 of 14** gold pairs are in it. The obvious replacement, `score_pass1_probe.py::bar_p1`, is the right COMPARISON and the wrong INSTRUMENT — it returns `passed`, `minimum_agreed` and a loss budget: it is a BAR, and this contract may not take one on the fourteen at all. Registered as `scorer.reader_comment_agreement` + `probe_b.collapse` alone, which is what `bar_p1` computes before its threshold arm; `population.gold.rows` carries the fourteen by pair; the census row is driven at $0 in the suite. | `[cause: contract-gap]` `[[a_flag_that_asserts_turns_a_poll_into_a_verdict]]` |
| **Dv638** | **Found in review, before the pod.** `first_reply_after_launch`'s `min → max` survived all 39 gate tests, because every one of them wrote a SINGLE row into the out-file. `max` is the permissive direction's opposite here — it would KILL a pod that booted in 140 s once the file was 400 rows deep. Three rows decide it now. | `[cause: verify-gap]` `[[guard_selftest_negative_control]]` |
| **Dv639** | **Found in review, before the pod.** All three of `store_agrees`' refusals could be deleted with the whole pack suite staying green. Each is driven now — the green path first, then a thread missing from the store, a moved post text and a moved comment text. | `[cause: verify-gap]` `[[guard_selftest_negative_control]]` |
| **Dv640** | **Found in review, before the pod.** The pack builder's 12 000-char STOP was unreachable: `prompts.pass1_messages_gm4` raises `ValueError` on an over-ceiling request, so `rendered_item` never returns one and the branch could not execute. The dead branch is gone; the record names where the STOP actually lives, and a test drives the renderer past the ceiling on the widest REAL item and watches it refuse. | `[cause: verify-gap]` `[[an_empty_class_is_the_definitions_answer]]` |
| **Dv641** | **Found in review, before the pod.** The «no typed thresholds» test greps the gate's source for `= <value>` and could not see the bar's own three numbers at all — they reach the gate as `int(bar[...])` and never as a literal. It asserts the SHAPE now: every number rung 7 acts on is read out of the record's bar. | `[cause: verify-gap]` `[[a_gate_that_checks_position_not_presence]]` |
| **Dv642** | **Found in review, before the pod.** The recovery clause was registered against the GUARD reading and computed from the GATE's own ledger. They are two meters: the gate's is the pod clock, timely and exact; the guard's is the balance delta and the billing walk, which is what the cap is defined against and lags by up to ~32 min. Both are named, the runbook takes both before a re-creation, and the stricter binds. | `[cause: process]` `[[a_balance_delta_is_not_a_per_leg_cost]]` |
| **Dv643** | **Found in review, before the pod.** `create_elapsed_at_the_last_row_seconds` was the watch loop's GO POLL, not the instant the last row landed — the loop polls at 20 s, so the true last row is up to 20 s earlier. Renamed, and the record says the reading is the later end and therefore the conservative direction for the overhead scaling. | `[cause: verify-gap]` `[[a_paced_log_is_an_interleavable_clock]]` |
| **Dv644** | The contract's D1 says «sha256 on the pod and on the Mac, **four for four**». That is r2's file count — two dev legs plus the stamp and the log. One leg means **three** files, and the runbook says three for three with the difference named in place rather than silently delivered. | `[cause: contract-gap]` `[[the_old_record_with_one_field_replaced]]` |
| **Dv645** | `instruments.scorer_pass1_fewshot` is DROPPED from the copied block with its reason: it is r2's D2 judge for a dev gate and a gold bar, and this contract calls neither. A pin naming a script this run never runs is a pin nobody checks. Conversely `gate_imported_from` and `window_summary_5c2` are ADDED — an imported instrument is an instrument, and the gate hashes the pack through the latter. | `[cause: process]` `[[a_consumer_list_is_not_a_meaning_list]]` |
| **Dv646** | The self-exclusion block publishes a DENOMINATOR beside its zero. «0 items shown a neighbour from their own thread» is free on a query whose thread carries no label, and window-1 is the population the 650 labels were drawn from — so the record also carries the **968 items whose own thread carries labels** and the **15 583 label-instances withheld** from them. The 64 the rule cannot bite on are exactly probe-b's, whose threads were removed from the labelling population whole. | `[cause: spec-gap]` `[[a_prefilter_cannot_certify_the_population]]` |

## D1 — the paid session, rung by rung

```
pod xpz3zb7yxus5cw   created 2026-08-21T15:32:18Z   deleted 15:46:23Z   845.0 s   $0.173694
                     RTX 4090, costPerHr 0.74, EU-RO-1, volume qw4nwleanc

15:32:26Z  price     rung 1  GO    elapsed     8.0   0.74 ≤ 0.80; --terminate-after 17:20:38Z,
                                                     equal to the computed stamp to the second
15:33:00Z  gate0     rung 2  GO    elapsed    41.5   ssh answered at 29 s on a clock-bounded poll
   (live in every     rung 3  ·)   launched_at 15:33:41 = 83 s of create-elapsed; load 164.9 s;
    watch poll)                    first reply 169.5 s of launch, 252.5 s of create — of 450/1100
15:46:23Z  watch     rung 5  KILL  elapsed   845.6   131/1032 answered, watched 748.2 s, never idle
                     rung 4        the projection left the HARD STOP: 6 785.7 s of 6 500
                                   the cap was never near it: $1.3948 of $1.50
15:46:23Z  delete            GO    {"deleted": true} — three listings, the volume as the control
```

**Rung 3 was checked live in every watch poll and never recorded as a standalone gate**, because
`--boot` needs a live pod and the watch's KILL deletes it inside the loop. The reading is
unambiguous in the artifacts — the pod wrote `launched_at` at 15:33:41, the first row carries
`boot_seconds 164.915` and `elapsed_since_start 169.505` — so launch → first reply was 169.5 s of a
450 s ceiling and 252.5 s of create-elapsed of an 1 100 s backstop. Reported from the artifacts,
never back-filled (Dv649).

### What rung 4 did, and why it was right

`leg_state` prices every call still owed at the LARGER of the leg's mean and its LAST call. At the
killing poll the last call was **5.151 s**, the mean was 4.498, and 901 calls were still owed:

```
845.6 (elapsed) + 901 × 5.151 (the last call) + 1300 (overhead) = 6 785.7 s  >  6 500   KILL
                                                                  $1.3948    ≤  $1.50
```

The dollars were never in danger. **The seconds are what the platform holds**, exactly as the
registration says, and rung 4 did precisely what it was registered to do.

### The reading of the session: a rate is a property of the POD

|  | n | mean | min | max |
|---|---:|---:|---:|---:|
| r2's dev-200 v2 leg, pod `8tpx8lf05n6skc` | 200 | **2.726** | 2.092 | 4.066 |
| this window leg, pod `xpz3zb7yxus5cw` | 131 | **4.498** | 3.799 | 5.798 |
| ratio | | **1.65×** | | |

Five explanations were ruled out one at a time, with numbers, before this was written down:

* **the request** — the window's rendered requests are 1.14 % wider than dev-200's (4 725.8 against
  4 672.4 chars). The entity blocks nearly double, 0.96 → 1.80 a request, and contribute almost
  nothing to the width. This is the H6 row the registration already carried (Dv628);
* **a cold leg** — r2's BASE leg ran first, straight off the model load, and its first ten calls
  averaged **2.199 s**. There is no warm-up effect on this stack that could explain 1.65×;
* **the prompt** — identical family, identical shas, and the pod's own handshake matched all 1 032
  per-item shas before the first call;
* **the card model and the place** — RTX 4090 both times, EU-RO-1 both times, the same volume;
* **the population** — the 200 dev rows are INSIDE this window and render byte for byte the same.

What is left is the pod. **The registration charged 3.4075 s/call — 2.726 × a 1.25 margin — and the
live rate is 1.32× the charge and 1.65× the sample.** The margin was bought against the growth of
the request; what moved was the silicon (Dv647).

### The recovery clause, pasted either way

```
$ PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --pre-create-check
  pods_opened                      1        re_creations_allowed              1
  billed_by_closed_pods_seconds  845.0      spent_closed_pods_usd      0.173694
  worst_case_ahead_seconds      5916.54     widest_dead_pod_that_fits    583.46
  projected_attempt_seconds     6761.54  >  hard_stop_seconds            6500.0
  projected_attempt_usd         1.488481 ≤  cap_usd_all_in                  1.50
  fits_the_hard_stop  False · fits_the_cap  True · fits_the_re_creation_count  True
  verdict  KILL
  STOP: this create cannot be paid for by the registration. The attempt is NOT spent —
  return it to the operator
```

It refused on SECONDS while the money still fitted — the shape the registration predicted. **No
second pod was created.** Two of the three tests passed and the stricter bound.

**Whether one pod would have finished depends on the span the record carries two values for — and
the answer reverses.** This is the same defect the review caught in `single_call_sensitivity`, so
both arms are given:

| pre-generation | total | at $0.80/h | at the $0.74 this pod cost | against 6 500 s |
|---|---:|---:|---:|---|
| **252.5 s** — what this pod MEASURED | 6 194.9 s | $1.3766 | $1.2734 | **fits, by 305 s** |
| **1 100 s** — what the registration CHARGES | 7 042.4 s | **$1.5650** | $1.4476 | **does not fit — and $1.5650 is outside the cap** |

So «the run was affordable» is true of the pod that ran and **false of the pod the registration
priced**. A continuation's pre-generation is unknown, so the charged row is the one that governs
it — and at the charged span the whole run does not fit in one pod at this rate, in seconds or in
money. What killed THIS pod is narrower: it was paying pod 1's 845 s out of 305 s of remaining
slack, so the restart was refused while the run itself was still inside the stop.

## D2 — the census ($0)

`results/pass1_window_census.json`. **Rung 7 is RED on completeness and green on everything else.**

```
$ PYTHONPATH=src python3.11 scripts/gate_pass1_window.py --completeness
  rows_in_the_file  131      answered  131 of 1032       parsed  131
  sha_mismatches      0      parse_refusals    0  {}      replies that never closed an object  0
  duplicate_ids      []      ids the leg never asked   []
  VERDICT  RED
```

131 replies, 131 parsed, not one transport defect. The instrument is sound; the bar failed on the
one number the money model could not deliver.

**131 is what the Mac holds and a LOWER BOUND on what was paid for.** The watch pulls the out-file
once a poll and the kill happens inside the loop, so rows generated between the last copy and the
deletion are on the network volume and not in this file. The pod is gone, so the difference is
unverifiable without spending again — and `/workspace/run/pass1_window_v2.jsonl` survives on volume
`qw4nwleanc`, which makes it an asset a continuation can RESUME from rather than re-buy.

### What v2 said, in THREE states

| | rows |
|---|---:|
| `сеть_ритейлер` | 46 |
| `категория_личное` | 36 |
| `None` | 37 |
| `молочный_бренд` | 9 |
| `не_наш_рынок` | 3 |
| REFUSED — answered and unparseable | **0** |
| UNANSWERED — the pod was killed first | **901** |

The last two rows are the point. Folding 901 never-asked comments into a refusal class would put the
pod's death in the parser's column — and writing this census is where that mistake was caught, three
times, in three places, in my own code (Dv650).

### Report-only readings — BOTH denominators, and none of them a bar

| reading | over the registered rows | over the rows answered | «our» |
|---|---|---|---|
| the 650 labelled rows | 69 / 650 | **69 / 117** = 0.590 | 23 / 49 |
| the 450 not in dev-200 | 35 / 450 | **35 / 65** = 0.538 | **0 / 0 — structurally** |
| the dev-200 | 34 / 200 | **34 / 48** = 0.708 | 21 / 49 |
| the fourteen | 4 / 14 | **4 of the 5 reached** | — |

**None of these is comparable to r2's 136/200 · 38/49, and the dev-200 row is NOT a reproduction of
it.** Eighty-three per cent of those rows were never asked: the first column counts them as
disagreements and is comparable to nothing, the second is a reading over a handful (Dv651).

**The 450's zero is structural and permanent** (Dv652): `dev_units` takes ALL 49 «our» rows into
dev-200 whole, so the 450 outside it contain none of the class this programme is about — that
reading can never say anything about «our» rows, on this run or any other.

**The fourteen: the pod reached FIVE and agreed on four.**

```
@VARUS_channel:10348#20664   сеть_ритейлер   ->  сеть_ритейлер   ✓
@VARUS_channel:10613#21599   категория       ->  категория       ✓
@VARUS_channel:10613#21601   категория       ->  категория       ✓
@VARUS_channel:10613#21626   сеть_ритейлер   ->  сеть_ритейлер   ✓
@VARUS_channel:10613#21629   None            ->  категория       ✗
the other nine                                   UNANSWERED — never reached
```

The fourth look at these rows and the thinnest of the four. A census row, not comparable to the
base's 9/14 or arm A's 9/14 — both taken on complete runs — and not quotable as a verdict on v2.

### The pass-2 filter table — the one output that survives the RED for what it is

**91 filtered rows across 24 of the 127 callable threads, 5 963 characters.** Partial by the same
fraction as the run: it prices `pass2-signals` per ANSWERED thread and the whole-window figure has
to be bought again. The per-thread rows, their label tallies and their entity-block sizes are in the
census.

### Measured spans, beside what was charged

| span | measured | charged |
|---|---:|---:|
| ssh publish | **29 s** (the gate recorded 41.5 of create-elapsed) | 500 |
| stage + launch | **54 s** | 150 |
| model load | **164.9 s** | 450 |
| pre-generation, whole | **252.5 s** | 1 100 |
| s/call | **4.498** (slowest 5.798) | 3.4075 |
| billed | **845.0 s = $0.173694** | 5 916.54 s = $1.3148 |

Every pre-generation line came in at a third to a half of its allowance. The one line that was
UNDER-charged is the only one that mattered.

**The per-poll copy-back, BOUNDED** — the fourth thing D2 owes, and this run could only bound it.
`append_gate` records ONE watch gate however many times the loop polls, so «watch gates in the
record» is 1 and is not a poll count; it is renamed in the census for exactly that reason. What the
loop does carry is `watched_seconds` 748.2 and a fixed 20 s sleep it does not take before returning,
which pins the poll count to 37 or 38 and the per-poll cost with it:

| polls | seconds per poll, everything but the sleep |
|---:|---:|
| 37 | **0.76** |
| 38 | **0.22** |

A poll copied the out-file (70 704 bytes at the end), the launch stamp and the pod log, computed the
fingerprint and ran the projection — under a second, on a file a fifth of the final size. That is
the number the overhead line was kept at 1 300 s for, and it is a bound rather than a measurement
because the file never reached 1 032 rows.

## Deviations added by the paid session

| # | What | Tag |
|---|---|---|
| **Dv647** | **The finding the whole session turns on.** `money.arithmetic.seconds_per_call` charged 3.4075 = the MEASURED 2.726 × 1.25, and named the margin «for the window's larger entity blocks». The live rate on `xpz3zb7yxus5cw` is **4.498 s/call — 1.65× the sample and 1.29× the charge**. Five candidate causes were eliminated with numbers before this was written: request width (+1.14 %), a cold leg (r2's own base leg, first off the load, ran 2.199), the prompt (identical shas, handshake matched all 1 032), the card model (RTX 4090 both) and the population (the 200 dev rows are inside this window and render byte for byte). The sample was reproducible and it was not representative. | `[cause: env]` `[[a_reproducible_probe_can_be_unrepresentative]]` |
| **Dv648** | `pre_create` prices a re-creation at the REGISTERED worst case and `projection` prices the running leg at the MEASURED rate, so the two halves of the same clause disagree about the same run — and the one that authorises the spend is the optimistic one. It did not bite here (the clause refused on seconds anyway) but it is the shape that would have bought a second pod that could not finish. | `[cause: verify-gap]` `[[two_instruments_two_inputs]]` |
| **Dv649** | Rung 3 is checked live in every watch poll and **cannot be recorded as a standalone gate on a killed pod** — `--boot` needs a live pod and the watch's KILL deletes it inside the loop. The reading is unambiguous in the artifacts (launch 15:33:41, `boot_seconds 164.915`, `elapsed_since_start 169.505`) and is reported from them rather than back-filled. r2 carried the same shape as a post-hoc note. | `[cause: contract-gap]` `[[a_registered_bar_may_have_no_producer]]` |
| **Dv650** | **Found while writing the census, in my own code, three times.** The label distribution folded 901 never-asked rows into a `REFUSED` class; the pass-2 table carried one `threads_total` over two denominators (129 in the cell, 127 callable); and the fourteen's `v2` column printed `None` for both «answered null» and «never reached», on nine of fourteen rows. All three now carry the distinction explicitly. A run that ends early makes every count in a census ambiguous, and the census is written after the money. | `[cause: verify-gap]` `[[the_empty_class_eats_the_parse_failures]]` |
| **Dv651** | Every report-only reading publishes TWO denominators — the registered rows and the rows the pod answered — because 83 % of the population was never asked. The dev-200 row is NOT a reproduction of r2's 136/200: it is 34/200 counting 152 unasked rows as disagreements, or 34/48 over what was reached. | `[cause: spec-gap]` `[[measure_on_the_rows_the_gate_scores]]` |
| **Dv652** | The «450 not in dev-200» reading the contract asks for has **`our_n` = 0 by construction and always will**: `build_pass1_fewshot_packs.py::dev_units` takes all 49 «our» rows into dev-200 whole. It is a reading of overall agreement on untuned rows and can say nothing about the class the programme is about — on this run or any other. | `[cause: contract-gap]` `[[an_empty_class_is_the_definitions_answer]]` |
| **Dv655** | **The same span defect, a third time, in the sentence the operator reads first.** «One pod doing the whole run fits — 6 195 s of 6 500» is true at THIS pod's measured 252.5 s of pre-generation and false at the 1 100 s the registration charges (7 042.4 s, $1.5650, outside the cap). I had documented the class in `single_call_sensitivity`, fixed it there by publishing both arms, and then wrote the headline off the flattering arm one section later. Both arms are given now, in the D1 table and in the operator's question, because a continuation's pre-generation is unknown and the CHARGED span is the one that governs it. | `[cause: verify-gap]` `[[a_ceiling_derived_from_one_span_measured_over_another]]` |
| **Dv656** | **`watch_polls` counted GATES, not polls.** `append_gate` is called once, after the loop returns, so the census read 1 where the loop polled 37 or 38 times. Renamed `watch_gates_recorded`, and D2's fourth item — the per-poll copy-back — is now BOUNDED from the loop's own `watched_seconds` and its fixed sleep: **0.76 s a poll at 37 polls, 0.22 at 38**, copying a 70 704-byte out-file, the launch stamp and the pod log. A bound and not a measurement, because the file never reached 1 032 rows. | `[cause: verify-gap]` `[[count_the_kind_not_the_rows]]` |
| **Dv657** | **131 is what the Mac holds, not what was bought.** The watch copies once a poll and the KILL happens inside the loop, so rows generated between the last copy and the deletion are on the network volume and not in the file. The pod is deleted, so the difference is unverifiable without spending — and `/workspace/run/pass1_window_v2.jsonl` SURVIVES on volume `qw4nwleanc`, which makes it an asset a continuation resumes from rather than re-buys. Reported as a lower bound. | `[cause: env]` `[[a_retry_inherits_the_last_attempts_output]]` |
| **Dv658** | **Three money figures exist for one step and the report first quoted the wandering one.** The gate's clock says $0.173694 and is final; the guard's balance delta read $0.1599 at 15:48Z and $0.1938 at 16:22Z and goes on growing at the volume's rate; the billing WALK reports **`pods $0.0000`** for a pod that ran 845 s and was deleted. That last is the sharpest Dv504 instance this programme has — not «lags 32 minutes» but «reports nothing for a resource that ran». All four readings are tabled with their moment, the clock is named as the one to quote, and the step is left OPEN for `money-anchors`. | `[cause: env]` `[[unreadable_now_versus_never]]` |
| **Dv654** | **The suite went red on a test of mine that had to flip.** `test_the_step_opens_with_no_pods_of_its_own` asserted that `results/pass1_window_run.json` holds no pods — true at D0 and false the moment the contract did the one thing it exists to do, with no code involved. This project has the class registered ([[the_absence_test_is_a_clock_and_flips_with_its_artifact]]) and I wrote another one anyway. It now asserts the DURABLE fact instead: the step ledger's cap is $1.50 and every pod in the run record was created AFTER `anchored_at` — which is what «the step opens with no pods of its own» actually means. | `[cause: verify-gap]` `[[the_absence_test_is_a_clock_and_flips_with_its_artifact]]` |
| **Dv653** | `gate_pass1_fewshot.py::leg_table` refuses any out-file row its leg never asked, which is right for a gate reading one leg's own file and wrong for a census taking three overlapping readings out of one. The census FILTERS the out-file to each subset in a scratch directory and hands `leg_table` the same lines, selected — the function is not modified and the rows are not touched. | `[cause: process]` `[[a_consumer_list_is_not_a_meaning_list]]` |

## Process signals (five lines)

1. **The rate was the one input nobody put on the suspect list — not the review's five lenses, not
   the skeptics, not me.** Every one of us attacked what the rate would be MULTIPLIED by: the
   margin's reason, the span the curve was computed over, the knife edge, the deletion tail. The
   registration even carried an H6 row measuring the margin's own justification and finding it
   generous by an order of magnitude. All of that was true and none of it mattered, because 2.726
   s/call over 200 rows on pod `8tpx8lf05n6skc` does not describe pod `xpz3zb7yxus5cw`. The 5c2
   retro's rule — «beside every price, name what it was measured ON» — was followed to the letter:
   the sample is named in the record, in the money block and in the report. Naming the sample is not
   the same as asking whether the sample is the population, and on a rented GPU the population is
   the pod.
2. **The review before the pod found nine defects and the tenth was the one it could not see.** It
   raised 21 findings, 12 survived, and every fix carries a mutation watched red — the guard that
   would have graded a tampered pack, the `--price` that left a billing pod unrecorded, the runbook
   that deleted the replies its own recovery clause promised to keep. Two of those would have ended
   the session at a cost. What the review could not do is question a number that had a measurement
   behind it: 2.726 was real, reproducible and sourced. A review checks whether the arithmetic
   follows from the inputs; it cannot check whether the inputs will still be true on hardware nobody
   has rented yet.
3. **Rung 4 was right, and I reached for the flattering counterfactual one section after
   documenting that exact mistake.** The gate was correct: 5.151 s/call projected 6 785.7 s against
   a 6 500 s stop, and letting it run would have discovered the overrun in a bill. What I first
   wrote beside it was «at the mean the run fits in one pod — 6 195 s of 6 500» — TRUE at this pod's
   measured 252.5 s of pre-generation and FALSE at the 1 100 s the registration charges, where the
   same arithmetic gives 7 042.4 s and $1.5650, outside the cap. Third instance of one span with two
   values in this record, and the third time I quoted the kind one. The claim now carries both arms,
   and the honest version is narrower: THIS pod was inside the stop and could not afford a restart,
   because it was paying its own 845 s out of 305 s of remaining slack.
4. **Writing the census found the same defect three times in my own code, after the money.** Never-
   asked rows folded into a refusal class, one `threads_total` over two denominators, and a `None`
   column meaning both «said null» and «never reached» on nine of fourteen gold rows. Each is the
   class I had already found and fixed twice during D0. A run that ends early makes every count in a
   census ambiguous at once, and the census is the artifact written when the evidence can no longer
   be re-bought.
5. **What survived the RED is worth more than the run would have been.** The transport is proven on
   1 032 registered requests and 131 real replies with zero defects of any kind; the completeness
   bar, its refusal semantics and D2's whole reading path were driven at $0 on r2's own replies
   before the create; and the session returns a measured rate for this pod class that re-prices
   `pass2-signals`, the remaining 901 comments and any future window pass. $0.1737 bought a number
   the programme did not have.

## What returns to the operator

**The bar is RED and the reason is a rate, not a defect.** 131 of 1 032, 845.0 s.

**Three money figures exist for this step and only one is stable.** Say which reading, and when:

| reading | figure | what it is |
|---|---:|---|
| the gate's CLOCK | **$0.173694** | 845.0 s × $0.74/h, exact and final. **This is the number to quote.** |
| the guard's balance delta, 15:48Z | $0.1599 | the account moved by this much between the anchor and that moment |
| the guard's balance delta, 16:22Z | $0.1938 | the same delta later — it goes on growing at the volume's ~$0.24/day |
| the guard's billing WALK | $0.0097, **`pods $0.0000`** | the walk reports ZERO for a pod that demonstrably ran 845 s and was deleted |

The walk's `pods $0.0000` is the sharpest instance of the Dv504 class this programme has: not «the
billing history lags ~32 minutes» but «it reports nothing at all for a resource that ran and is
gone» ([[unreadable_now_versus_never]] — unreadable NOW is not never). **The step is left OPEN**, as
r2's was; `money-anchors` owns the settled close. Cycle 2 reads $6.5436 of $20.00 at the same moment
as the $0.1599 row.

**Three things need your word, and the first two are the same decision seen twice.**

1. **The 901 comments still owed have to be re-priced before they are re-bought, and the price
   depends on a span nobody can measure in advance.** At 4.498 s/call the remaining rows are
   901 × 4.498 = **4 053 s of generation**. With THIS pod's measured pre-generation and the
   registered overhead that is 5 606 s = **$1.2457 at the $0.80/h ceiling**; with the pre-generation
   the registration CHARGES it is 6 453 s = **$1.4340**, and both of those sit under a 6 500 s stop
   only because pod 1's 845 s are NOT counted against them — under this registration they are, and
   nothing fits. A continuation needs its own registration, with a rate charged on the POD CLASS
   rather than on a sibling run and a pre-generation charged as the spread it is: `pass1-window r2`,
   in the shape `pass1-fewshot r2` took.
2. **6 700 s was already the right question and it arrived through the other door.** Before the
   create I reported that 6 700 s = $1.4889 stays inside the $1.50 cap and moves rung 4's edge to
   4.167 s/call; you ruled «proceed as registered» on a risk described as one outlier call. The
   actual failure needed no outlier: the whole rate sat above the edge. At 4.498 s/call a hard stop
   of **7 000 s = $1.5556** would be needed and that is OUTSIDE the cap — so this is not a
   hard-stop tweak any more. It is the cap and the rate together, and it belongs in the next
   registration rather than in an amendment to this one.
3. **`pass2-signals` cannot be priced from this census as it stands.** The contract says it is
   priced from THIS run's census, and the census covers 24 of 127 callable threads — 91 filtered
   rows of an unknown whole. The per-thread shape is sound and the extrapolation is not mine to
   make.

**And the reminder the record binds regardless of the RED.** The fourteen: the pod reached five and
agreed on four. That is a census row with its multiplicity named — the fourth look at those rows and
the thinnest of the four — and it is not comparable to the base's 9/14 or arm A's 9/14, both taken
on complete runs. It may not be quoted as a verdict on v2 by this report, by the acceptance, or by
the next registration.

---

# ADDENDUM — the team lead's acceptance, 2026-08-21 (evening)

**Appended, never rewritten.** Everything above is the report as it was accepted; this section
carries what the acceptance found and what was changed because of it. Where a number below differs
from one in the body, **the number below is the one to quote** — the body's is named here so a later
reader can see which reading was corrected and why, instead of finding two values and picking the
kind one. Written under `docs/PROMPT-pass1-window-r2.md` step 0.5, at $0, before any r2 code. Its
Deviations are enumerated with r2's, from Dv659, in `docs/reports/pass1-window-r2.md` — one
enumeration for one contract.

## 1 — the report-only readings were inflated by msg_id collisions

**A msg_id is unique per CHANNEL and not per window, and the scoring path keyed on it alone.**

`src/market_pulse/scorer.py::reader_comment_agreement` builds `answers = {int(one["msg_id"]): one
for one in per_comment}` — a last-wins map — and `scripts/gate_pass1_fewshot.py::leg_table` derives
`agreed_ids` as a **set** of msg_ids while `our_rows` stays a **list** of them. Seven msg_ids inside
`membership.labelled_650` live in two threads each, `@VARUS_channel` against `@klopotenkofood`, and
the pack's own `gold_id_collisions` block had already named all thirteen collisions in the
population — for the GOLD rows, where the two keys agree. Nobody carried the same question to the
labelled readings.

Five of the seven pairs had exactly one twin answered, so five twins the pod never reached inherited
their namesake's reply and were scored as present:

| msg_id | `@VARUS_channel` | `@klopotenkofood` | what the id-only key did to the 650 |
|---|---|---|---|
| 21164 | answered · said `молочный_бренд` · gold `не_наш_рынок` | answered · said `категория` · gold `не_наш_рынок` | both answered — nothing inherited, both disagree either way |
| 21195 | answered · said `null` · gold `сеть_ритейлер` | answered · said `категория` · gold `категория` («our») | both answered — the map kept one reply, and the reading is the same on either |
| 21209 | answered · said `null` · gold `сеть_ритейлер` | **never answered** · gold `null` | +1 answered, **and +1 AGREED** — the inherited `null` matched the twin's gold |
| 21211 | answered · said `сеть_ритейлер` · gold `сеть_ритейлер` | **never answered** · gold `категория` («our») | +1 answered, **+1 our_agreed** — `our_rows` holds 21211 and `agreed_ids` holds it too |
| 21236 | answered · said `сеть_ритейлер` · gold `сеть_ритейлер` | **never answered** · gold `не_наш_рынок` | +1 answered |
| 21239 | answered · said `сеть_ритейлер` · gold `сеть_ритейлер` | **never answered** · gold `не_наш_рынок` | +1 answered |
| 21256 | answered · said `сеть_ритейлер` · gold `сеть_ритейлер` | **never answered** · gold `категория` («our») | +1 answered, **+1 our_agreed** |

**+5 answered · +1 agreed · +2 «our» agreed** — and that is exactly the gap, to the row:

| reading | the body says | **corrected** | what moved |
|---|---|---|---|
| the 650 labelled rows | 69 / 117 · «our» 23 / 49 | **68 / 112 · «our» 21 / 49** | five inherited replies, one inherited agreement, two inherited «our» agreements |
| the 450 not in dev-200 | 35 / 65 | **34 / 64** | it carries one of the seven, 21209 — the one that inherited an agreement |
| the dev-200 | 34 / 48 · «our» 21 / 49 | **34 / 48 · «our» 21 / 49** | nothing: dev-200 carries no collision at all |
| the fourteen | 4 of the 5 reached | **4 of the 5 reached** | nothing: the gold pairs carry no collision either |

The rates over the registered rows move with them: the 650 reads 68/650 and the 450 reads 34/450.
None of these was ever a bar and none of them becomes one by being corrected.

**The scorer is NOT edited, and neither is `leg_table`.** `src/market_pulse/scorer.py` is the single
judge of every number in this programme and is pinned by sealed records;
`scripts/gate_pass1_fewshot.py` is pinned by four of them, r2's sealed registration included, and is
the instrument D2's own clause names. Editing either to fix a census would move bytes a closed
session's record certifies. What changed is the census path: `census_pass1_window.py::labelled_reading`
now hands `leg_table` **one thread at a time** and sums the tables. Within a thread a msg_id is
unique, so the collision cannot occur and every row is still scored by the function the contract
names.

**The rule this establishes, and it binds the next contract.** *Comment identity anywhere in this
window is the PAIR `(thread, msg_id)`.* `pass2-signals` assembles per thread over rows pass 1
labelled, and a table keyed on msg_id would merge two comments of two different channels into one
row of one thread. The pack already keys `membership` on the pair; the census now does; the next
registration must say so in its own record.

**The check that survives.** `tests/test_pass1_window_census.py` builds the 21209 pair — one twin
answered, one never — and calls **both paths on the same pinned instrument**: the id-only key
answers `2 answered / 1 agreed`, the pair answers `1 / 0`. The mutation (one group instead of one
group per thread) was watched red: `assert 2 == 1`.

## 2 — the refusal that ended the session was never a record

`--pre-create-check` printed its KILL and returned exit 2 **without calling `append_gate`**. The
paste in «The recovery clause, pasted either way» above was the only place it existed: no gate entry,
no run-record key, nothing a later reader could re-derive. A guard whose verdict lives in a terminal
is not a record.

It is now appended to `results/pass1_window_run.json` as a `pre-create-check` gate, marked
`recorded_after_the_fact`, carrying the stdout line as the command printed it. It is not a typed
recollection: `pre_create(record, state)` is pure in both arguments, so it was **recomputed** from
the committed registration and the recorded state and reproduces every field —
`projected_attempt_seconds 6761.54 > hard_stop 6500.0`, `projected_attempt_usd 1.488481 ≤ 1.50`,
`widest_dead_pod_that_still_fits_seconds 583.46`, verdict `KILL`. `state["latest"]` was left where the
session ended it (`completeness · RED`): an entry appended a day later may not rewrite how the run
finished. The moment it actually ran is **not** in the record and cannot be — it ran after the
15:46:23Z deletion and before rung 7, and nothing stamped it.

`tests/test_gate_pass1_window.py` re-derives every field of the entry from the record and the state;
the mutation (`projected_attempt_seconds` 6761.54 → 6500.0) was watched red. **From r2 on,
`--pre-create-check` records its verdict at the moment it runs** — that lands in the r2 sibling,
because `scripts/gate_pass1_window.py` is pinned by this contract's sealed registration and may not
be edited to gain the behaviour.

## 3 — the pod log names the 132nd reply, and the file does not hold it

Dv657 reported 131 as a lower bound and could not name what was missing. The pod's own log can:

```
[   754.5s] reply 131/1032 @klopotenkofood:6032#21195                5.2s ·   119 chars · cut    1 · balanced True · finish stop
[   759.2s] reply 132/1032 @klopotenkofood:6035#21205                4.7s ·   108 chars · cut    4 · balanced True · finish stop
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^ absent from results/pass1_window_v2.jsonl
```

The runner writes its log line as the reply lands, so the log reaches one row further than the
out-file that is copied beside it. The census now derives this rather than asserting it
(`replies_the_mac_does_not_hold`): 131 rows in the file, 132 replies in the log, one id named. **132
is itself a lower bound** — the log is copied once a poll too. The rows themselves survive at
`/workspace/run/pass1_window_v2.jsonl` on volume `qw4nwleanc`; r2 copies that file back as EVIDENCE,
counts what it holds beyond the Mac's 131 and prices it, and does not merge it.

## 4 — one more figure in the body, found while checking the others

The rate table in «a rate is a property of the POD» prints the window leg's minimum as **3.799 s**.
The file's minimum is **3.780**; 3.799 is the second-smallest of the 131. The mean (4.498), the max
(5.798) and every dev-200 figure beside them re-derive exactly. It changes nothing — the argument
runs on the mean and the maximum — and it is named here because the acceptance was already
correcting three readings in this file and a fourth one left unnamed is the same class again.

## What this addendum does NOT change

The bar is still **RED at 131 of 1 032**. The pod, its 845.0 s and its $0.173694 are unmoved. Rung 4
was right, the transport was clean on every row it bought, and the pass-2 filter table still covers
24 of 127 callable threads and still cannot price `pass2-signals`. The step is still **OPEN** for
`money-anchors`. The fourteen are still a census row with their multiplicity named — the pod reached
five and agreed on four — and this addendum does not promote them either.
