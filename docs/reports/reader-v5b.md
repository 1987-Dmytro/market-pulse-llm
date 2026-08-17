# reader-v5b — the ruled order withdrawn on its own gate table, and the run that followed

**Contract:** `docs/PROMPT-reader-v5b.md` · **Registration:**
`results/prereg_reader_probe_v5b.json` (`8122fce0eb25c223…`) · **Pack:**
`results/reader_v5b_pack.json` (`f1f4a74d2f5b35bc…`) · **Baseline:** `make check` 2 782 passed /
2 skipped, measured here and equal to the team lead's own run.

**What happened, in one paragraph.** Step 0, step 0.5 and D1 went as written. D1's own measurement —
the one the contract asked for — said the pack order the operator had ruled makes the registered
full-pass gate **STOP after the FIRST unit**, by 23.2 seconds a unit, on any boot including none at
all. Nothing was created; the finding went to the operator with four orders measured beside it; **the
order ruling was withdrawn the same day, with the cap and gate 0 standing.** The registration and the
pack were rebuilt at $0 in v5's own order, and the withdrawn order's gate table stays inside the
registration as the withdrawal's evidence. **Then the run went the whole way: gate 0 answered in 24
seconds where v5's pod never answered at all, 26 of 26 units were read, all 21 full-pass gates
returned GO, and the pod was deleted after 1 514.0 billed seconds — $0.311211 of a $0.50 cap.**

**And the answer is a negative one.** Bar 2 and bar 3 pass, leg B's four mechanical bars all pass and
the chunking mechanism works on its first outing, the echo duty is obeyed on 117 of 117 requested ids
with none absent — **and bars 1 and 4, the two this whole generation of the instrument existed to
move, both FAIL.** The run COMPLETED, so **the pre-registered programme stop-rule fires: the
prompt-engineering line closes and the next step is an architecture sitting, not a v6.**

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

**When the registration freezes.** At the **FIRST `pod create` of the attempt** — which happened at
`2026-08-17T16:22:10Z`. A recreated pod would have read the SAME frozen record; that is what makes a
replacement a segment of one attempt instead of a second attempt. There was no recreate, and no
frozen file moved after that stamp (§7 lists their shas).

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

### 6.1 The timeline of segment 1

Anchor `results/spend_reader_v5b.json` at $21.4577480282, `2026-08-17T16:21:29Z`, cap $0.50, committed
in `a25ab76` **before** anything was created. Three listings immediately before create: `pod list -a`
`[]`, `serverless list` `[]`, `network-volume list` `qw4nwleanc` `mp-srv2` EU-RO-1 100 GB — the volume
is the positive control that the listing works at all. `--pre-create-check` → `may_create: true`,
segment 0 of 3.

| create-elapsed | wall | what |
|---|---|---|
| 0 s | 16:22:10Z | `pod create` — `r7702vbsrxhz0j`, RTX 4090, RO, `costPerHr` **0.74**, exactly the registered worked example, so no deadline is re-priced |
| 9.8 s | 16:22:20Z | `--open`: segment 1 recorded, gate `open` **WAIT**, 170.2 s left on gate 0 |
| 15 s · 19 s | | `runpodctl ssh info` → `{"error": "pod not ready", "status": "RUNNING"}` |
| **24 s** | 16:22:34Z | **the endpoint answered** — `213.173.111.15:11201`. gate `gate0` **GO**, recreates left 2 |
| 36 s | 16:22:46Z | scp: the 8.76 MB bundle at `a25ab76`, the pack, and BOTH runners |
| ~55 s | | `git clone` → `repo-v5b`; `git rev-parse HEAD` = `a25ab76145ec…` = the Mac's HEAD; `git status --short` empty |
| 77 s | 16:23:27Z | detached launch, `--repo /workspace/repo-v5b` passed explicitly |
| 269 s | 16:26:39Z | `READY · boot 192.1s` (v4's measured boot: 175.119 s) |
| 322 s | 16:27:32Z | reply 1 lands, and the kill clock stops |

**Gate 0 is what this contract bought, and it cost nothing.** v5's pod was listed RUNNING and never
answered `ssh info` across ~150 polls and 727.9 billed seconds; this one answered in **24 s**, three
polls. The dead-man never fired, and the run that follows is the first evidence about the READER this
programme has had since v4.

### 6.2 Dv479 — the detached launch did not return, and the runner was alive anyway

The launch `ssh … 'nohup … & echo launched $!'` printed nothing and did not return; the harness moved
it to the background after 300 s. A SECOND ssh connection, opened while the first still hung, showed
the python process running, the log already at `READY · boot 192.1s`, and two replies on disk. So the
launch worked and only its channel stayed open. `& echo $!` is not proof of anything by itself, and
the proof that counted came from the second connection — which is what Dv454's form is for.
`[cause: the ssh channel stayed open]`

It has one consequence worth writing down: on the pod, `pgrep -f reader_v5_pod_runner.py` matches the
hung `bash -c` wrapper that carries that string AND the watcher's own remote shell, so a
pattern-matching liveness watch can never reach zero and would be silent through a crash. The watch
was rebuilt on `kill -0 <pid>` ([[a_remote_job_outlives_its_watcher]]).

### 6.3 The run completed: 26 of 26, every gate GO, $0.311211 at the meter

| | |
|---|---|
| units read | **26 of 26** — leg A's 23 threads whole, then leg B's 3 chunks |
| gate snapshots | **23, all appended, none overwritten**: 1 `open` (WAIT), 1 `gate0` (GO), **21 `full_pass`, every one GO** — at units 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 20, 22, 23, 24, 25 and 26 |
| tightest full-pass margin | **+3.39 s/unit at unit 2**, headroom 126.4 s — the unit the registration named, and it cleared |
| final gate | unit 26, GO, headroom **880.7 s** |
| billed | 1 514.0 s from create to delete = **$0.311211** at $0.74/h, against a $0.50 cap |
| pod | `r7702vbsrxhz0j`, one segment, no recreate, deleted 1 s after the delete call returned |

Segment closed with `--close-segment`; the three listings after are identical to the three before —
`pod list -a` `[]`, `serverless list` `[]`, and the volume `qw4nwleanc` still there as the positive
control that the listing works at all.

### 6.4 The bars

`results/reader_v5b_verdict.json` (`8c975558b8da31cf…`), scored by v5's own arithmetic through
`scripts/score_reader_v5b.py`:

| bar | verdict | what it measured |
|---|---|---|
| 1 flagships | **FAIL** | 2 of 5 cases answered (threshold 5 of 5). F4 and F5 found; F1, F2, F3 not |
| 2 entity cases | **PASS** | 4 of 4 |
| 3 noise | **PASS** | — |
| 4 per-comment agreement | **FAIL** | rate **0.4286** — 14 rows: 6 agreed, 4 disagreed, **4 absent** |
| 5 time and cost | **OPEN** | the step ledger has no closing entry yet (§6.6) |
| leg B m1–m4 | **ALL PASS** | payable ids exactly once, every chunk finished, every chunk parsed, no duplicate signal survived the merge |

**The programme stop-rule FIRES.** It was pre-registered in v5 and re-registered here verbatim: «if
this run COMPLETES and bars 1 and 4 are not BOTH taken, the prompt-engineering line CLOSES; the next
step is an architecture sitting — two passes, labelled data, a different base — and never a v6 of the
same kind.» The run completed. Bars 1 and 4 both failed. The rule binds the reading of this run's own
numbers because it was written before them.

Bar 4's arithmetic, named: of the seven non-agreed gold rows the contract listed, **two moved** —
`47899` and `48283` now agree. `580124`, `580129`, `47902` and `578951` still disagree, and `21601`
is **absent**, together with `21626`, `21599` and `21629`: all four sit in `@VARUS_channel:10613`,
the one thread whose reply refused with `malformed JSON`. Five of seven was the bar; two moved.

The collapsed and uncollapsed readings agree exactly on both failing bars (2 and 2; 0.4286 and
0.4286), so neither failure is an artefact of the vocabulary collapse.

### 6.5 What the instrument DID buy, beside the bars

- **The echo duty is obeyed, completely.** The three-state census over every parsed row: **117 of 117
  requested ids covered — 109 in `per_comment`, 8 in `noise`, ZERO absent.** v4 could not tell those
  states apart; here the shortfall the census exists to find is empty.
- **The transport stop worked and cost almost nothing.** 26 of 26 replies balanced; **19 units cut, 62
  characters in total**, and `never_balanced` is empty. v4's two «two disagreeing objects» refusals do
  not recur.
- **But the stop has a cost the registration did not name.** Three of the four refusals are short
  replies where the stop took a balanced object that was not the answer: `@VARUS_channel:10529` (116
  tokens, `missing field: entities`), `@mandziak:3701` (`missing field: entities`) and
  `@VARUS_channel:10593` (`missing field: evidence`). The fourth, `@VARUS_channel:10613`, is
  `malformed JSON` at 2 056 tokens. **4 refusals of 23 — exactly v4's count, on different threads.**
- **The 4 000-token ceiling never fired.** Every unit's `finish_reason` is `stop`; the largest reply is
  **2 056 tokens, 51% of the ceiling** — where v4's largest was 97.3% of its 2 000. The raised ceiling
  was bought and not needed, which is the outcome a ceiling should have.
- **Leg B, the chunking mechanism, worked on its first outing.** Three chunks of 16/16/11 rows, all
  three parsed, the merge made with no duplicate signal, `merge_error: null`, and the merged verdict
  carries all 43 payable ids exactly once. It cost **175.1 s against the registration's 320.0 s
  projection** — a 16-row chunk is 64 s, cheaper per row than a thread.

### 6.6 The money, and the one open number

| | |
|---|---|
| meter (create → delete) | 1 514.0 s × $0.000205556 = **$0.311211** |
| guard, right now | **$0.2782 of $0.50**, and it says so as a **LOWER BOUND** — «billing since: UNAVAILABLE (no billing rows yet)» |
| step ledger | `results/spend_reader_v5b.json`, anchored $21.4577480282 at 16:21:29Z, not closed |

Bar 5 is **OPEN, not passed**, and that is the scorer refusing to score a bar against an unsettled
number rather than a failure. reader-v5's walk posted about two hours after its pod died; this one
will settle the same way, and the close is the named debt this report carries. The meter's
$0.311211 and the guard's $0.2782 lower bound bracket it, and both are under the cap.

### 6.7 The counterfactual is no longer a forecast

The registration's table said the withdrawn order would STOP at unit 1 because
`@matusi_ukr:22272` would cost **105.3 s** against **82.1 s** allowed. That thread was read here, as
unit 17: **103.8 seconds.** The forecast was 1.4% high. Under the ruled order this run would have
been deleted after one thread; under the registered one it read 26 units and scored every bar.

The rest of the forecast held too, which is what makes the first number trustworthy: leg A's 23
threads took **1 035.4 s against v4's 907.6 s — a growth of 1.141 where the registration registered
1.127** — and produced 19 200 completion tokens against v4's 18 637.

**Dv480.** `scripts/score_reader_v5.py`'s `main()` printed «every key of the leg-B block whose name
starts with `m`», and `merge_error` does. On the first record that ever carried one — this one — it
raised `TypeError: 'NoneType' object is not subscriptable`, AFTER the verdict file was written, which
is the only reason it cost nothing. Fixed to print the entries that carry a `passed` field, with a
test that drives `main()` and is red against the previous commit. The verdict's sha256 does not move:
the defect was in the printer, never in the arithmetic. `[cause: a-consumer-list-is-not-a-meaning-list]`

---

## 7. Verify

```
$ make check                                   # before step 0.5
2782 passed, 2 skipped in 369.96s
$ make check                                   # at c7e2395, the step 0.5 commit
2789 passed, 2 skipped in 378.42s
$ make check                                   # at 20db35c, before the pod was created
2826 passed, 2 skipped in 453.00s
$ make check                                   # after the run, with the scorer's printer fixed
2828 passed, 2 skipped in 454.28s (0:07:34)
$ python3.11 -m ruff format --check .
337 files already formatted
$ runpodctl pod list -a          # after the delete; serverless [] and the volume still listed
[]
$ shasum -a 256 results/prereg_reader_probe_v5b.json results/reader_v5b_pack.json \
      results/reader_v5b_w1.jsonl results/reader_v5b_verdict.json
8122fce0eb25c223cff6a6983777e92fff69e3fd53db209b00b43fc4218a00c4  results/prereg_reader_probe_v5b.json
f1f4a74d2f5b35bc52b3d127f078f9c53c8d673b7eb1d85529a52cb770d86e89  results/reader_v5b_pack.json
9540a84bc87109ce3589a636fa5640d56feb5c8382bb82adcf8345bd8e858e8c  results/reader_v5b_w1.jsonl
8c975558b8da31cfcd78463eae65ceef54cc9b11e267e8c4343adee4bc49b834  results/reader_v5b_verdict.json
$ PYTHONPATH=src python3.11 scripts/read_threads_reader_v5b.py --pack
pack results/reader_v5b_pack.json · 26 units, every sha matches the record
  leg A 23 threads · leg B 3 chunks
  task reader_thread_gm4_v5 · parser be5a81641afc2aa5… · ceiling 4000 output tokens
```

The registration's own build, with both gate tables:

```
$ PYTHONPATH=src python3.11 scripts/write_reader_prereg_v5b.py
wrote results/prereg_reader_probe_v5b.json  sha256 8122fce0eb25c223…
  cap $0.50 buys 2432.4 s · usable 2372.4 s · reading projection 1454.0 s
  pre-generation budget 198.5 s · affordability deadline 918.5 s
    1 segment(s): usable  2372.4 s · affordability   918.5 s · budget   198.5 s · reading fits True
    2 segment(s): usable  2132.4 s · affordability   678.5 s · budget   -41.5 s · reading fits True
    3 segment(s): usable  1892.4 s · affordability   438.5 s · budget  -281.5 s · reading fits True
  payable, in order: [7, 2, 12, 4, 5, 5, 2, 2, 5, 10, 9, 12, 8, 3, 9, 12, 15, 2, 3, 2, 1, 0, 4]
  full pass over that order: first STOP after None unit(s) · tightest margin 12.93 s/unit at unit 2 (@VARUS_channel:10360)
  unit 1 @VARUS_channel:10348 · 7 payable · expected 41.3 s vs a zero-boot ceiling of 91.2 s -> clears True
  the WITHDRAWN order (descending payable): first STOP after 1 unit(s) · tightest margin -23.16 s/unit at unit 1 (@matusi_ukr:22272)
  gates: ['0_transport_ssh_deadman', '1_staging', '2_boot_kill', '3_the_full_pass']
  bar 5 cap: $0.50
```

The verdict, printed by the scorer:

```
$ PYTHONPATH=src python3.11 scripts/score_reader_v5b.py
wrote results/reader_v5b_verdict.json  sha256 8c975558b8da31cf…
  outcome GO · leg A 23 of 23 · leg B 3 chunks
  bar 1_flagships                SCORED — False (collapsed)
  bar 2_entity_cases             SCORED — True
  bar 3_noise                    SCORED — True
  bar 4_per_comment_agreement    SCORED — False (collapsed)
  bar 5_time_and_cost            OPEN — passed None
  leg B m1_every_payable_id_exactly_once       True
  leg B m2_every_chunk_finished                True
  leg B m3_every_chunk_parses                  True
  leg B m4_the_merge_has_no_duplicate_signal   True
  completeness: 117 of 117 covered · 109 per_comment · 8 noise · 0 ABSENT · 0 in both
  transport stop: 19 units cut, 62 chars
  uncollapsed: {'1_flagships': {'as_the_bar_collapsed': 2, 'uncollapsed': 2}, '4_per_comment_agreement': {'as_the_bar_collapsed': 0.42857142857142855, 'uncollapsed': 0.42857142857142855}}
```

### 7.1 Nothing frozen moved while the pod existed

The registration froze at the first `pod create`. The proof is the git history's own clock, not a
sentence: **the pod was alive from 18:22:10 to 18:47:24 CEST and NO commit was made in that window.**
The last commit before it is `a25ab76` at 18:21:41 — 29 seconds before create — and the next is
`9e7cc5e` at 18:58:16, eleven minutes after the delete.

Every file the registration lists as frozen, with the commit that last touched it:

```
f7e2263 18:11:50  results/prereg_reader_probe_v5b.json     (the registration itself)
1942a74 18:12:36  results/reader_v5b_pack.json
66dc418 15:05:41  results/prereg_reader_probe_v5.json
3131bc0 16.08     results/reader_gold_w1_r2.json
9fe6dd4 12:48:23  src/market_pulse/prompts.py
647b47f 13:56:52  src/market_pulse/reader_v5.py
aa78c14 15.08     src/market_pulse/scorer.py
8bf5a14 15.08     scripts/probe_b_population.py
9f0338d 16.08     results/gate_census_w1_reader.json
f1bb539 16.08     results/prereg_reader_probe_v4.json
```

All ten precede 18:22:10. The two files edited during the run — `scripts/score_reader_v5.py`'s printer
and this report — are on neither the frozen list nor the pack's rendering path.

And the guard, which is the one number still open:

```
$ python3.11 scripts/runpod_guard.py --step reader-v5b --step-cap 0.50
READER-V5B SPENT      $0.2782 of $0.50  (anchor $21.46 from runpod_balance_at_reader-v5b_start)
  balance delta   $0.2782
  billing since   UNAVAILABLE (no billing rows yet) — the delta stands alone as a LOWER BOUND
```

## 8. Deviations

| | what | tag |
|---|---|---|
| **Dv475** | The contract's «~918 s pre-generation budget» is the AFFORDABILITY deadline; the registered `pre_generation_budget_seconds` is 198.5 s. Both positive, both published, the registered formula unchanged. | `[cause: two-readings-of-one-clause]` |
| **Dv476** | «Descending payable» is not a total order — six counts are shared — so the registration registered `(-payable, thread_id)` and named the ties. The key survives in `order_withdrawn` as the tiebreak the ruling would have needed. | `[cause: an-order-key-that-is-not-total]` |
| **Dv477** | D2 was not opened on the ruled order: solved backwards, the registered gate STOPs at unit 1 by 23.2 s/unit on any boot. Reported before any pod; the operator withdrew the order ruling and the run went ahead in v5's order. Unit 17 later measured **103.8 s** against the forecast's 105.3 s. | `[cause: registered-gate-vs-ruled-order]` |
| **Dv478** | `scripts/score_reader_v5.py` points at v5's files by module constant, so bar 5 would have been scored against the reader-v5 ledger. Reached instead by a thin `scripts/score_reader_v5b.py` that CALLS it with its constants swapped (Dv451's idiom). | `[cause: reading-of-the-clause]` |
| **Dv479** | The detached launch's ssh session never returned and printed no pid; the runner was alive and at `READY` on a second connection. A `pgrep -f`-based liveness watch could not have seen it die — the pattern matches its own remote shell — so the watch is by pid. | `[cause: the ssh channel stayed open]` |
| **Dv480** | `score_reader_v5.py`'s `main()` printed every leg-B key whose name starts with «m», and `merge_error` does: `TypeError` on the first record that ever carried one, after the verdict was written. Fixed to print the entries carrying a `passed` field; test red against the previous commit; the verdict's sha does not move. | `[cause: a-consumer-list-is-not-a-meaning-list]` |
| **Dv481** | Bar 5 is OPEN, not passed: the billing walk has not posted, so the step ledger has no closing entry. The meter says $0.311211 and the guard's lower bound says $0.2782, both under the cap. The close is this report's named debt. | `[cause: unreadable-now-versus-never]` |

## Process signals

1. **The contract asked for the measurement that stopped it, and the measurement was right.** «Re-solve
   the gate backwards over the new order» was written expecting a confirmation; it cost $0 and returned
   a refutation. The thread it said would fail the first gate at 105.3 s was read here in **103.8 s**.
2. **Two fixes were ruled together and only one of them was needed.** The $0.50 cap alone turned
   Dv471's 9% margin into 23%; the order change was aimed at the payable leg and landed on the unit
   leg. Pricing them apart is what made the withdrawal possible before any money.
3. **The transport that was bought is the transport that worked.** Gate 0 answered in 24 s where v5's
   pod never answered in 727.9 billed seconds — and the gate never had to fire. The thing the contract
   spent its design budget on turned out to be the thing that did not go wrong this time, which is
   what a dead-man is for.
4. **A negative result arrived with its own rule already written.** The programme stop-rule was
   pre-registered in v5 and re-registered verbatim here, so «bars 1 and 4 both failed» reads as a
   decision that was made before the numbers rather than after them. That is the whole point of
   pre-registration and this is the run that cashed it.
5. **The evidence outlives the verdict.** 26 replies, 27 evidence rows, 23 appended gate snapshots, two
   gate tables inside the registration and a withdrawn ruling with its dates — an architecture sitting
   that starts from this file starts from measurements, not from a memory of them.
