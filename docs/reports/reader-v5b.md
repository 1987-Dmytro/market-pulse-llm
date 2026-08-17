# reader-v5b — the ruled order withdrawn on its own gate table, and the run that followed

**Contract:** `docs/PROMPT-reader-v5b.md` · **Registration:**
`results/prereg_reader_probe_v5b.json` (`8122fce0eb25c223…`) · **Pack:**
`results/reader_v5b_pack.json` (`f1f4a74d2f5b35bc…`) · **Baseline:** `make check` 2 782 passed /
2 skipped, measured here and equal to the team lead's own run.

**What happened, in one paragraph.** Step 0, step 0.5 and D1 went as written. D1's own measurement —
the one the contract asked for — said the pack order the operator had ruled makes the registered
full-pass gate **STOP after the FIRST unit**, by 23.2 seconds a unit, on any boot including none at
all. Nothing was created; the finding went to the operator with the four orders measured beside it;
**the order ruling was withdrawn the same day, with the cap and gate 0 standing.** Leg A is v5's
enumeration order again, the registration and the pack were rebuilt at $0, and the withdrawn order's
gate table stays inside the registration as the withdrawal's evidence. D2 then ran on that.

---

## 0. Read back, one line each

**What may NOT move — the instrument.** Prompt v5 (`reader_thread_gm4_v5`) and the four registered
reader texts, the parser, `market_pulse.reader_v5`, gold r2, the population digest and its 23
threads, leg B's thread and its three chunks, the 4 000-token output ceiling, the symmetric
vocabulary collapse, N1's exclusion, the echo duty, bars 1–4 with their thresholds, leg B's four
mechanical bars, the serving configuration, the scorer's bytes, the one-attempt class and the
programme stop-rule. In this registration that is not a promise: the v5b producer CALLS v5's producer
and refuses unless it rebuilds v5's frozen record byte for byte, so those keys are the frozen
record's own objects (§3.1).

**The three that were ruled, and the two that moved — all transport, all operator rulings of 17.08.**
The cap $0.45 → **$0.50**; a transport **gate 0** (ssh dead-man at 180 s with at most 2 recreates);
and leg A by **descending payable comments** — which was ruled, measured before any pod, and
**withdrawn on that measurement the same day** (§4, §5). The registered order is v5's own.

**Gate 0 and the third pod.** If `runpodctl ssh info` has not answered with a connectable endpoint
by **180 s of that segment's own create-elapsed**, the pod is deleted, the deletion is proven by a
listing, and a replacement of the same card class in the same datacenter is created — **at most
twice. A third dead pod is a datacenter state, not bad luck: the attempt STOPs** and the finding is
infrastructural rather than about the reader.

**Segment accounting, one sentence.** One attempt may span up to three pod segments and never two at
once; each segment's boot gates are measured from its OWN create response, and the affordability leg
is always the attempt's — the cap less what every closed segment billed, priced at each segment's own
`costPerHr` and never at a balance delta.

**The re-solved unit-2 margin.** On the registered order — v5's own — at the new cap it is
**+12.9 s/unit**: 55.5 s allowed against 42.6 s expected, 23% of margin where $0.45 left 9%, and it is
the tightest point of all 26 units. Under the withdrawn order unit 2 was no better (**+1.0 s/unit**,
82.1 s of mean against 83.1 s allowed, 1.2%) and the STOP had already fired one unit earlier (§4.2).

**When the registration freezes.** At the **FIRST `pod create` of the attempt**. A recreated pod reads
the SAME frozen record — that is what makes a replacement a segment of one attempt instead of a second
attempt. Nothing has frozen yet.

---

## 1. Step 0 — the tail and the v5 close

### 1.1 The tail, by live `git status`, by path

```
 M docs/STATUS.md
 M knowledge/daily_logs/2026-08-17.md
 M knowledge/hot.md
 M knowledge/index.md
?? docs/PROMPT-reader-v5b.md
```

- `c8a2271` — `knowledge/**`, three files (the 17:04 `/save` checkpoint), staged by path.
- `4f30f57` — `docs/STATUS.md` and `docs/PROMPT-reader-v5b.md`, **verbatim**, in their own commit.
  Both are the team lead's: read and committed, never edited. The untracked prompt was read before it
  was staged, and `git add -A` was never used.

**The baseline was green this time:** `make check` → **2 782 passed, 2 skipped in 369.96s**, equal to
the number the contract quotes. Dv469's class (a curated vault file that `volume_calc_5c1.py` greps
as a priced input) did not recur — the `/save` that preceded this session kept both literals, and
they were verified through the READER (`calc.quoted`) and never by running the producer (Dv474).

### 1.2 The `reader-v5` step is CLOSED

The walk had posted. `python3.11 scripts/runpod_guard.py --step reader-v5 --step-cap 0.45 --close
--note "reader-v5 settled"`:

```
CLOSED spend_reader_v5.json at $0.1501 — entry APPENDED
READER-V5 CLOSED     $0.1501 of $0.45  (settled at 2026-08-17T15:23:06+00:00, window from 2026-08-17T13:08:32+00:00)
  pods            $0.1501
  network-volume  $0.0097   <- always on, beside the run and never inside it
  serverless      $0.0000
CYCLE 2 SPENT     $1.0423 of $20.00
REMAINING         $18.9577
```

**$0.150095, pods only** — the whole price of a pod that was billed 727.9 s and never answered ssh.
Both ledgers committed in `424bab0`; the closing entry is appended, and the anchor was not
regenerated.

---

## 2. Step 0.5 — the two fresh-context findings, red before green

Commit `c7e2395`. Seven new tests; **all seven fail against the previous commit** and two
pre-existing tests were selected alongside them as controls and stayed green:

```
$ python3.11 -m pytest tests/test_read_threads_reader_v5.py -q \
    -k "torn or DUPLICATE or foreign or duplicate or DROP or UNANSWERED"
6 failed, 2 passed, 33 deselected in 6.26s
$ python3.11 -m pytest tests/test_read_threads_reader_v5.py -q \
    -k "test_a_row_whose_id_THIS_pack_never_asked_for_is_REFUSED_by_name"
E   KeyError: '@somebody_else:1'          # scripts/read_threads_reader_v5.py:203, in projection
1 failed, 40 deselected in 4.75s
```

That filter selects **eight** tests: six of the seven new ones, all six red, and two pre-existing ones
as controls that stayed green — `test_a_torn_LAST_line_is_dropped_and_a_torn_middle_one_still_raises`
(Dv473's, the Mac side of the same rule) and `test_m1_fails_on_a_duplicate_across_chunks_and_names_it`.
The seventh new test's name matches no word in the filter and was run on its own, above.

After: **41 passed** in that file, and `make check` **2 789 passed, 2 skipped in 378.42s** at that
commit — the suite the commit itself has to pass, run on the commit.

### 2.1 `already_answered()` got the tolerant reader — and the file, not just the count

The bare `json.loads` is gone. `whole_lines()` states the rule the Mac's `raw_rows` states (last line
forgiven, a torn line anywhere else refused loudly and by position), and a torn last unit counts as
**UNANSWERED** and is re-asked.

The half the finding did not name and the code needed anyway: `--out` is opened in **append** mode, so
a final line with no newline would have the next reply concatenated onto it — one corrupt middle line,
manufactured by the resume itself. So the fragment is dropped from the FILE, as a **byte prefix**,
which leaves every reply that did land exactly as the pod wrote it, sha and all.

The two implementations cannot share a module: one runs on a rented pod with two files beside it, the
other inside the repo on the Mac. Their agreement on one fixture is therefore a test —
`test_the_pod_runner_and_the_mac_driver_DROP_THE_SAME_torn_line` — and it drives both sides over the
same bytes, in both directions.

### 2.2 The Mac gate counts UNIQUE unit ids, and refuses by name

`unit_ids()` is the whole fix, on the gate AND the ingest path:

| defect | before | after |
|---|---|---|
| duplicate row | counted as two units read | `SystemExit`, naming the id and the count |
| id not in the pack | `KeyError` at `payable[row["id"]]`, on the kill-rule path | `SystemExit`, naming the id and the pack |

The arithmetic the refusal stops is in the test, not in prose: thirteen units answered twice make 26
rows against a 26-unit pack, `units_unread` goes to 0, the binding factor with it, and the gate
returns a trivial **GO** on a run that has already spent five times its cap. The negative control is
the same seconds over thirteen UNIQUE ids, which is the **STOP** it should be.

`main`'s `--gate` path no longer decorates rows with their leg by a dict lookup before the projection
sees them — that lookup was itself the `KeyError` site, so the refusal now arrives before it, and the
test drives it through `main`.

---

## 3. D1 — the registration and the re-ordered pack

Commits `c88da32` (registration, producer, 18 tests) and `cdf0e58` (pack, driver, 18 tests).

### 3.1 «The instrument does not move» is a refusal, not a sentence

`scripts/write_reader_prereg_v5b.py` calls `write_reader_prereg_v5.build()` and compares it to the
frozen `results/prereg_reader_probe_v5.json` before overriding one key; a mismatch names the differing
keys and stops. Every key it does not override is therefore the frozen record's own object.

Measured on the two committed files:

```
top-level keys identical : attempt · completeness · instruments · programme_stop_rule · scoring_rules
top-level keys that moved: authority · bars · class · contract · frozen_when_the_pod_exists ·
                           go_no_go · money · non_gating · phase · population · producer ·
                           supersedes · transport
bars that moved          : 5_time_and_cost   (bars 1-4 and leg_b_mechanical: object-equal)
population that moved    : leg_a  ->  enumeration.threads only, and as a SET it is unchanged
go_no_go that moved      : gates ->  0_transport_ssh_deadman (new), 2_boot_kill (+segments),
                           3_the_full_pass (+order, +identities_not_rows)
```

`test_the_whole_diff_against_v5_is_the_enumerated_one` asserts that set exactly, so a fourteenth
difference cannot arrive unnoticed, and `test_everything_the_reader_is_SCORED_ON_is_object_equal…`
asserts the other half. The registration is byte-identical on rebuild
(`test_the_committed_registration_is_what_the_producer_writes_today`) and carries no clock, so the
commit that holds it is the only witness that it preceded the money.

### 3.2 Difference 1 — the cap, and the two readings of «the budget»

Every second below is computed by **v5's own `money()`** with one number swapped, not by a second
spelling of the arithmetic: v5's producer hashes itself into a frozen record, so it cannot grow a
parameter, and the constant is swapped around the call and restored in a `finally`.

| | $0.45 (v5) | $0.50 (v5b) |
|---|---|---|
| seconds the cap buys | 2 189.189 | **2 432.432** |
| usable (less one delete margin) | 2 129.189 | **2 372.432** |
| reading projection (leg A 1 134.0 + leg B 320.0) | 1 454.0 | **1 454.0 — unchanged** |
| affordability deadline, as create-elapsed | 675.2 | **918.5** |
| `pre_generation_budget_seconds` | **−44.785** | **+198.5** |

**Dv475.** The contract reads «minus one 60 s delete margin per pod segment, minus the reading
projection 1 454.0 s → the pre-generation budget is finally POSITIVE (~918 s with one segment)». The
**~918 s is the affordability deadline**; the registered quantity called
`pre_generation_budget_seconds` is `usable − the twelve-minute ceiling − the projection` and equals
**198.5 s**. Both are positive, so the contract's claim holds under either reading, and both are
published apart with the identity spelled out (`money.segments.budget_reading`). The registered
formula was not re-derived to fit the prose. `[cause: two-readings-of-one-clause]`

The consequence is worth naming: at $0.45 the affordability leg bound from the first second; at $0.50
the **twelve-minute ceiling** binds first, until pre-generation plus boot passes 198.5 s, after which
affordability binds again. The gate prints which, and
`test_the_budget_is_reported_and_gates_nothing_in_the_boot_rule` drives both sides of that switch.

**Segments** (new, `money.segments`). A dead segment costs `180 + 60 = 240 s` at the pessimistic
corner. Every row derives from the published one-segment figures, so the one-segment row **is** the
number above rather than a second computation that rounds differently:

| segments | dead | billed before | usable | affordability | budget | reading still fits |
|---|---|---|---|---|---|---|
| 1 | 0 | 0.0 s | 2 372.4 s | 918.5 s | +198.5 s | yes |
| 2 | 1 | 240.0 s | 2 132.4 s | 678.5 s | −41.5 s | yes |
| 3 | 2 | 480.0 s | 1 892.4 s | 438.5 s | −281.5 s | yes |

And the bound the recreate COUNT cannot see, because a pod can die slowly:
`billed_seconds_before_the_reading_no_longer_fits = 918.5 s` — which **is** the affordability
deadline, and that is an identity and not a coincidence (`usable − billed ≥ projection` rearranges to
`billed ≤ usable − projection`). Two dead segments at the pessimistic corner cost 480 s of it.

### 3.3 Difference 2 — gate 0, and the guard that has to run before `pod create`

`go_no_go.gates.0_transport_ssh_deadman`: threshold 180 s of the segment's own create-elapsed, 2
recreates, and on the last allowed segment the verdict's own `next_step` says **STOP** rather than
recreate. Driven at 179 s (WAIT, 1.0 s left), at 180 s (KILL), and with the endpoint answering late
(GO — the threshold is a dead-man and not a schedule).

**Never two pods** is a `--pre-create-check`, not a refusal inside `--open`: a refusal there fires
after the second meter has already started. It refuses while any segment lacks a `deleted_at`, and it
refuses when three segments are already on record — before anything is created.

### 3.4 Difference 3 — the order: ruled, measured, withdrawn

**Dv476.** The ruling said «descending payable». That is **not a total order** on this population:
six payable counts are shared — 12 by three threads, and 9, 5, 4, 3, 2 by two or more — so the
registration registered the key as `(-payable_comments, thread_id)`. Without the tiebreak, «the pack
is in descending payable order» is unverifiable and two builds of one registration could produce two
packs. `[cause: an-order-key-that-is-not-total]`

The order was then solved through the live gate (§4), the operator withdrew the ruling on that
measurement, and the registered order is v5's enumeration order — element for element, not merely as
a set. `population.leg_a.order_withdrawn` keeps the whole episode inside the record: what was ruled,
when it was ruled and withdrawn, why each, what removed the knife-edge instead, and the tiebreak the
withdrawn key would have needed.

The pack: **26 units, `AAAAAAAAAAAAAAAAAAAAAAABBB`**, payable
`7 2 12 4 5 5 2 2 5 10 9 12 8 3 9 12 15 2 3 2 1 0 4` then `16 16 11`, sha256
`f1f4a74d2f5b35bc…`. Built by the same function that built v5's pack, and its id list is asserted
equal to the registration's own leg-A enumeration followed by leg B's three chunks — not to a
hand-typed permutation.

---

## 4. The measurement the contract asked for — and what it says

### 4.1 Method

`money.arithmetic.full_pass_over_the_registered_order` in the registration itself, computed by
**`read_threads_reader_v5.projection` — the function the live gate calls** — over synthetic rows at
v4's own measured seconds times this registration's own growth factor (1.127), leg B's chunks at the
registration's own 106.7 s each, starting from 214.1 s of create-elapsed (v4's measured
pre-generation 39.0 s + its measured boot 175.119 s). Reported and gating nothing; the gate itself
compares MEASURED seconds. This is Dv471's method at the order and the cap being registered.

### 4.2 The ruled order STOPped at unit 1

| after | unit | payable | mean s/unit | binding | factor | allowed s/unit | headroom | verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | `@matusi_ukr:22272` | 15 | **105.3** | `by_unit` | 25.00 | **82.1** | −578.9 | **STOP** |
| 2 | `@VARUS_channel:10366` | 12 | 82.1 | `by_unit` | 12.00 | 83.1 | 24.0 | GO |
| 3 | `@mandziak:3684` | 12 | 71.2 | `by_unit` | 7.67 | 84.6 | 306.9 | GO |
| 4 | `@matusi_ukr:22242` | 12 | 66.2 | `by_unit` | 5.50 | 86.1 | 437.9 | GO |

The mechanism, in one line: the first gate fires after the FIRST reply, and there the **by-unit** leg
extrapolates the 25 unread units off whatever that one reply cost. Reading the payable-dense threads
first puts `@matusi_ukr:22272` — 15 payable comments and **the second-slowest thread v4 measured**,
93.415 s, which is 105.3 s at the registered growth — in that position, against 82.1 s allowed.

And it is not only the first unit. Reading the slowest threads first holds the running MEAN just under
the by-unit ceiling for the whole first half. Off the registration's own table: 82.1 s of mean
against 83.1 s allowed at unit 2 (+1.0), 71.2 against 84.6 at unit 3 (+13.3), 74.2 against 85.1 at
unit 5 (+10.9). Exempting unit 1 would buy a run that spends the front of leg A within seconds of a
KILL, which is the opposite of what the ruling was for.

**It does not depend on the boot.** Charging NO provisioning and NO model load at all, the first gate
still requires `m1 ≤ usable ÷ 26 = 91.2 s`. The expected 105.3 s clears that only if v5 turns out
**faster** than v4 on that thread, under a registration that projects it 12.7% slower. Published as
`the_first_gate_is_boot_free` and asserted in
`test_the_first_gates_verdict_does_not_depend_on_the_boot_at_all`.

**And the one mechanism that could have made v5 faster does not apply to this thread.** v5's transport
stops generation at the first balanced object, so a unit v4 overshot could come back cheaper — but off
`results/reader_v4_w1.jsonl`, `@matusi_ukr:22272` **parsed cleanly at 1 819 completion tokens with
`finish_reason: stop`**: it closed its object and stopped on its own, and there is nothing for the
transport stop to cut. Under v5 it gets the echo duty's row for each of its 15 comments, so 105.3 s is
the optimistic end. (The threads that DID overshoot are `@VARUS_channel:10529` at 615 tokens and
`@mandziak:3676` at 1 136 — neither is first in this order.)

### 4.3 Four candidate orders through the same live gate, at the same cap

$0, and the reason the finding was a decision and not just a number — this is the table the ruling
was withdrawn on. Same function, same record, same expected seconds; only leg A's order differs:

| order | first STOP | tightest margin |
|---|---|---|
| **A.** v5's enumeration order — **now the registered one** | none — GO through all 26 | **+12.9** s/unit at unit 2 |
| **B.** descending payable — **ruled, then withdrawn** | **unit 1** (105.3 vs 82.1 allowed) | −23.2 s/unit at unit 1 |
| **C.** ascending payable | unit 2 (7.8 vs 6.1 allowed) | −9.5 s/unit at unit 6 |
| **D.** descending payable per second | none — GO through all 26 | +24.7 s/unit at unit 1 |

Two readings of the same table. **The knife-edge the ruling was written to remove was removed by the
cap raise alone**: Dv471's 9% of margin at unit 2 under $0.45 is 23% under $0.50, on the order that is
already frozen in v5, already built and already tested. And the two legs of the registered inequality
pull in opposite directions — the by-unit leg wants the FAST units first, the by-payable leg wants the
payable-DENSE ones first — which is why C fails too, and why an order that satisfies both exists (D)
without anybody having ruled it. If D were ever ruled it would need a registered tiebreak of its own:
`-payable ÷ seconds` is a float key with no natural ties today, and «no ties today» is not a total
order (Dv476 is the same lesson one column over).

---

## 5. The ruling — the order withdrawn, before any pod

**Dv477.** The contract's D2 was not opened on the ruled order. Under the registered gate it reads one
thread and STOPs: that spends the one attempt this registration allows, closes the reader question for
it, and — because the programme stop-rule fires only «if the run COMPLETES» — leaves the programme
exactly where reader-v5 left it, minus about $0.06. Every $0 item of the contract was done and
committed first; then the finding went to the operator with §4.3's four orders beside it, and the
question was put narrowly: the descending-payable ruling is arithmetically incompatible with the
registered full-pass gate — is the ORDER ruling withdrawn, or is something else authorised?
`[cause: registered-gate-vs-ruled-order]`

**The ruling: the order ruling is withdrawn. The cap $0.50 and gate 0 stand. Leg A returns to v5's
enumeration order.** Given at 2026-08-17, on the table above, before any pod of this attempt existed.

What it cost to apply, all of it $0: `ruled_order()` became `registered_order()` and
`withdrawn_order()` in `scripts/write_reader_prereg_v5b.py`, the registration rebuilt
(`6e2023de…` → **`8122fce0eb25c223…`**), the pack rebuilt (`187fff23…` → **`f1f4a74d2f5b35bc…`**,
same 26 units, same 26 rendering shas, only the sequence), five tests rewritten and one added.
Commits `f7e2263` and `1942a74`.

**The withdrawal's evidence lives in the record it changed**, not only here: both gate tables are
published in `money.arithmetic` — `full_pass_over_the_registered_order` (no STOP, GO through all 26,
tightest +12.9 s/unit at unit 2) and `full_pass_over_the_withdrawn_order` (STOP after unit 1, −23.2
s/unit) — and `population.leg_a.order_withdrawn` carries the dates and the reasons. A withdrawal whose
evidence lives only in a report is a withdrawal the next contract can re-decide.

**Dv478, named now rather than discovered later.** The Verify block calls
`PYTHONPATH=src python3.11 scripts/score_reader_v5.py`, and that script's `PHASE`, `PREREG`,
`EVIDENCE`, `RUN`, `LEDGER` and `OUT` are module constants pointing at v5's files — bar 5 would be
scored against the v5 ledger, and its refusal names `results/reader_v5_w1.jsonl` (§7). It is reached
the way this stack reaches a shipped artefact it may not edit: a thin caller (Dv451's idiom, the same
one the v5b registration and driver already use). `[cause: reading-of-the-clause]`

---

## 6. D2 — the run

*(written as it happened; every figure points at `results/reader_v5b_run.json` or the step ledger)*

**At the moment this commit was made the run had not been opened yet**: the anchor is next, then
the three listings, then `--pre-create-check`, then `pod create`. This section is filled in after
the pod is deleted. If it still reads like this, the session ended between the ruling and the
anchor and nothing was billed — `results/spend_reader_v5b.json` and `results/reader_v5b_run.json`
are the two files that would say otherwise.

---

## 7. Verify

```
$ make check                                   # before step 0.5
2782 passed, 2 skipped in 369.96s
$ make check                                   # at c7e2395, the step 0.5 commit
2789 passed, 2 skipped in 378.42s
$ make check                                   # at cdf0e58, after D1
<see §7.1>
$ python3.11 -m ruff format --check .
336 files already formatted
$ runpodctl pod list -a
[]
$ shasum -a 256 results/prereg_reader_probe_v5b.json results/reader_v5b_pack.json
6e2023deaffe8ef15fc18451ad1479b70c753a188623f86e5aa237b2b13412f2  results/prereg_reader_probe_v5b.json
187fff2311969a74efaf14513a2a680893a1fb66c99fb0d4ce6788d178d8077a  results/reader_v5b_pack.json
$ PYTHONPATH=src python3.11 scripts/read_threads_reader_v5b.py --pack
pack results/reader_v5b_pack.json · 26 units, every sha matches the record
  leg A 23 threads · leg B 3 chunks
  task reader_thread_gm4_v5 · parser be5a81641afc2aa5… · ceiling 4000 output tokens
```

The registration's own build, and the gate table it publishes:

```
$ PYTHONPATH=src python3.11 scripts/write_reader_prereg_v5b.py
wrote results/prereg_reader_probe_v5b.json  sha256 6e2023deaffe8ef1…
  cap $0.50 buys 2432.4 s · usable 2372.4 s · reading projection 1454.0 s
  pre-generation budget 198.5 s · affordability deadline 918.5 s
    1 segment(s): usable  2372.4 s · affordability   918.5 s · budget   198.5 s · reading fits True
    2 segment(s): usable  2132.4 s · affordability   678.5 s · budget   -41.5 s · reading fits True
    3 segment(s): usable  1892.4 s · affordability   438.5 s · budget  -281.5 s · reading fits True
  payable, in order: [15, 12, 12, 12, 10, 9, 9, 8, 7, 5, 5, 5, 4, 4, 3, 3, 2, 2, 2, 2, 2, 1, 0]
  full pass over that order: first STOP after 1 unit(s) · tightest margin -23.16 s/unit at unit 1 (@matusi_ukr:22272)
  unit 1 @matusi_ukr:22272 · 15 payable · expected 105.3 s vs a zero-boot ceiling of 91.2 s -> clears False
  gates: ['0_transport_ssh_deadman', '1_staging', '2_boot_kill', '3_the_full_pass']
  bar 5 cap: $0.50
```

No verdict record — and the refusal is Dv478's own evidence, because the file it names is **v5's**:

```
$ PYTHONPATH=src python3.11 scripts/score_reader_v5.py
results/reader_v5_w1.jsonl: no evidence — there is nothing to score
```

### 7.1 The suite, after D1

```
$ make check
2825 passed, 2 skipped in 448.76s (0:07:28)
```

2 782 at the baseline + 7 (step 0.5) + 18 (the v5b registration) + 18 (the v5b transport) = 2 825, and
the arithmetic closes. The minute the suite gained is the registration's own byte-identical rebuild:
the v5b producer calls v5's, so that one test rebuilds two records.

---

## 8. Deviations

| | what | tag |
|---|---|---|
| **Dv475** | The contract's «~918 s pre-generation budget» is the AFFORDABILITY deadline; the registered `pre_generation_budget_seconds` is 198.5 s. Both positive, both published, the registered formula unchanged. | `[cause: two-readings-of-one-clause]` |
| **Dv476** | «Descending payable» is not a total order — six counts are shared — so the registration registers `(-payable, thread_id)` and names the ties. | `[cause: an-order-key-that-is-not-total]` |
| **Dv477** | D2 was not opened. The ruled order makes the registered gate STOP at unit 1, by 23.2 s/unit and on any boot; the attempt is unspent and awaits a ruling (§5). | `[cause: registered-gate-vs-ruled-order]` |
| **Dv478** | `scripts/score_reader_v5.py` points at v5's files by module constant; when there is evidence, bar 5 will be reached by a thin v5b caller rather than by editing it (Dv451). Nothing scored today. | `[cause: reading-of-the-clause]` |

## Process signals

1. **The contract asked for the measurement that stopped it.** «Re-solve the gate backwards over the
   new order and publish the table» was written expecting a confirmation; it cost $0 and returned a
   refutation. The instruction to measure before spending is doing exactly what it is for.
2. **A cap raise and an order change were ruled together and only one of them was needed.** The
   $0.50 cap alone turns Dv471's 9% margin into 23%. The order change was aimed at the payable leg
   and landed on the unit leg.
3. **A ruling can be under-specified in a way only the data shows.** «Descending payable» reads total
   and is not; the tiebreak had work to do on six groups.
4. **Two guards on one number found each other.** The resume mechanism made the out-file readable
   twice, which turned every row count into an identity question — and the torn-line defence written
   for one reader had to be written again for the other, with a test standing between them.
5. **The freeze line is where the report should already exist.** This file was written and committed
   before any `pod create`, so a session that dies with a question open leaves the finding on disk
   rather than in a chat.
