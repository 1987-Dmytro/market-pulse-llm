# pass1-window — D0 delivered and reviewed, and the review overturned my own registration of rung 4

**Status at the time of writing: D0 is complete, committed and green; no pod has been created.**
Everything below is at $0. The paid session's sections are marked and are empty until it runs.

The one thing the team lead should read first is **Process signal 1** and the section
[Rung 4 and the span I quoted the wrong one of](#rung-4-and-the-span-i-quoted-the-wrong-one-of).
It carries a number that decides whether $1.50 is enough, and it is a question for the operator.

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

## Process signals (five lines)

1. **The review before the pod found a defect in the block I wrote to register a risk, and that is
   the most useful thing that happened today.** I measured rung 4's knife edge, wrote it into the
   record, and computed it over the pre-generation r2 MEASURED while the same record CHARGES a
   different value for the same span. The headline I published — «1.19×, margin not comfort» — was
   false at the number the budget pays for, where the real figure is 0.98. Every ingredient was
   already in my own record; what I lacked was a reader who would not take my framing. The lesson is
   not «measure the span» — I did — it is that **a derived number must be recomputed at every value
   the record carries for its inputs**, and a record that holds two values for one span is a record
   that will be quoted at the flattering one.
2. **Driving D2 at $0 on r2's real replies was worth more than any argument about the instrument.**
   The 200 dev rows render byte for byte in both packs, so 200 replies a pod actually generated are
   valid rows of this out-file — and running them through rung 7 and through `leg_table` reproduced
   136/200 and 38/49 exactly. That single check verified the completeness bar against a real
   transport, proved D2's clause is satisfiable, and surfaced the missing `our_readings` key. Two
   packs sharing anchors is usually a hazard; here it was an instrument, and it was free.
3. **Nine of the twelve surviving findings were about numbers I had already written down.** Not one
   was about missing code. The pattern across Dv625, Dv627, Dv630, Dv631, Dv634, Dv635 and Dv643 is
   the same shape seven times: a quantity that is right about one population, one span or one key,
   carried into a sentence about another. Registering a risk is not the same as registering it in
   the units the risk is measured in.
4. **The skeptic pass was contaminated by my own fixes and the report says so rather than quoting a
   ratio.** Findings were repaired while the lenses were still running, so «refuted» sometimes means
   «already fixed» and sometimes means «never real», and nothing distinguishes them from the
   outside. What every fix rests on instead is a demonstration in this session's own output — a grep
   that found no guard, a bisected threshold, a mutation watched red. A review whose verdicts cannot
   be trusted is still worth its findings; a report that quoted its verdicts would not be.
5. **The contract is executable as written and one number in it is worth the operator's attention.**
   6 500 s buys $1.4444 of a $1.50 cap and leaves 583.46 s of slack over the worst case — and rung 4
   spends that slack as a rate allowance, which is why one 4.066 s call can end a healthy run. 6 700 s
   is $1.4889, still inside the cap, and moves the edge above the worst call this stack has measured.
   That is a re-registration and it was not taken here.

## What returns to the operator

**One question, with its arithmetic.** The registered hard stop of 6 500 s makes rung 4 kill a
healthy pod on a single 4.066 s reply whenever the pre-generation runs near the 1 100 s the budget
charges — and such a kill also refuses the one re-creation, closing the session with no verdict.
6 700 s is $1.4889 of the same $1.50 cap and puts the edge at 4.167 s/call. **Raising it is the
operator's word and was not taken.** The run is authorised and executable either way; the executor's
mitigation is to stage briskly, and the runbook now says so with the table beside it.

**One reminder the record already binds.** The fourteen inside this population are answered because
they are IN it. Their agreement is a census row with its multiplicity named — the fourth look at the
same rows — and it can never be promoted to «v2 takes N of 14», by this report, by the acceptance,
or by the next registration. The same holds for the 650 labelled rows and the 450 outside dev-200.

## D1 — the paid session

*Not run. This section is written after the pod, rung by rung, with the guard reading at each one.*

## D2 — the census ($0)

*Not run. `results/pass1_window_census.json` and the four numbered readings the contract lists.*
