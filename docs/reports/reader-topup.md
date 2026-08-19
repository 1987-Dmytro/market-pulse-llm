# Report — `reader-topup` (branch B): COMPLETE at $1.2259, in three segments and two registrations

The operator ruled «выполни ветку B» on 2026-08-19, and then ruled the corrected estimator after
attempt A's gate stopped its own run. **The pass is complete: 132 of 132 units, $1.225934 of a
$2.00 cap, three segments and no fourth.** The pass-1 training set now carries the context its eval
prompts carry — 630 of its 650 topics are bought reader summaries instead of cut post fragments,
and 282 of its rows carry an entity block where 39 did.

The two segments before it were defects in MY registration, both found on a running meter, and the
second is the one worth reading: the full-pass gate returned STOP at its first reading, by
construction, on a run whose own measurement confirmed it would have fitted.

Artefacts: `results/reader_topup_projection.json` · `results/reader_topup_prereg.json` ·
`results/reader_topup_pack.json` · `results/reader_topup_run.json` ·
`results/reader_topup_pod.jsonl` · `results/spend_reader_topup.json` ·
`scripts/runbook_reader_topup.md`.

## What was registered, at $0, before any endpoint

The report that opened the fork priced branch B at «105 × the MEAN 51.3 s ≈ $1.20». That is a mean
of one population applied to another, and the first thing this contract did was re-price it from
the thread sizes themselves:

```
POPULATION  105 threads with no verdict · 857 payable comments (min 1 · median 2 · max 125)
MODEL       seconds ≈ 22.2242 + 3.63508 × payable  (n=26); out of sample 1.0829× on v4
PROJECTION  132 items · 6049 s of generation + 450 s boot = 1.81 h
            $1.34 at $0.74/h · $1.44 at the $0.80/h ceiling · $1.56 at the ceiling × the v4 ratio
```

132 UNITS and not 105 threads: ten threads run past the 16-payable chunk line and three past 100
comments. The fit's error bar is the v4 run and not its own in-sample total — least squares with an
intercept forces the residuals to sum to zero, so «it reproduces the total» is arithmetic.

The same record priced what the buy CHANGES, because a buy that closes half a finding should say so
before the money: the topic half completely (559 rows stop carrying a cut post fragment; the 372
branch-C ellipsis markers against the eval's 0 disappear), the entity half **partially** — 39 of 650
rows carry a block today and ~279 are expected at the 43% rate measured inside the threads already
bought, against the gate's 12 of 14. Ten of the 24 bought verdicts resolve no entity at all.

Cap **$2.00**: the executor's derivation from a price the operator ruled over, sized so the worst
boot on record (1 200 s) at the worse price still leaves 1.28× the projection. The record says whose
derivation it is.

## Segment 1 — 23 s: a registered field no shipped command could read

`--open` raised `KeyError: 'threshold_seconds'` with the meter running. Five fields were spelled the
way the registration's author found natural and not the way the shipped gates read them:
`threshold_seconds`, `boot_kill_seconds`, `reading_projection_seconds`,
`pre_generation_budget_seconds`, `boot_deadline_rule`. The pod was deleted 23 s after create
(**$0.004728**), proven by three listings, and no segment was opened.

Dv486's rule is exactly this — «a registered field no shipped command can read is a red gate at $0
and not on a live pod» — and the reason it fired anyway is worth naming: **the PACK was driven
against the pod runner at $0 before the create, and the DRIVER was not.** The fix restored the
consumers' spelling and proved that nothing else moved by flattening both records and diffing every
path: two renames carrying identical values, one field that already existed elsewhere under gate 1,
and `.producer.sha256`. Then the block that should have existed first landed: **31 tests driving
every command and every gate on synthetic state** — `--pre-create-check`, `--open` and its
second-open refusal, `--gate0` on all three verdicts, `--deadlines`, `--gate` on both branches,
`--close-segment`, and `--ingest` merging a chunked thread's eight parts into one verdict.

## Segment 2 — 462 s: the boot was the best on record and the gate stopped the run

```
[   156.3s] READY · boot 156.3s
[   233.8s] reply  1/132 @matusi_ukr:22058#1of8   77.5s · 3841 chars · cut 4 · balanced True · finish stop
```

156.3 s is the fastest boot this stack has measured (the previous four: 179, 192, 267–293, 373 s);
the volume was warm, 59 GB of weights in place. And **the one unit this run bought confirms the
projection it was priced on**: the fit says 22.2242 + 3.63508 × 16 = **80.4 s** and the pod took
**77.5 s**.

Then the registered full-pass gate returned STOP:

```
units read 1 of 132 | payable read 16 of 857
by_unit factor    131.0   -> projects 10 156 s
by_payable factor  52.56  -> projects  4 075 s
the rule takes max(...)   -> elapsed + 10 156 s = 10 557 s against 9 646.7 usable
                          -> $2.1702 against a $2.00 cap -> STOP
the registration's own fit for the whole read: 6 049 s
```

The pod was deleted on the rule — scp first, then delete, three listings with the volume as the
positive control — and segment 2 closed at 462.0 s = **$0.094967**.

### The defect is in the specification, and it is mine

`max(by_unit, by_payable)` is conservative when the units are the same size. v5b's were: whole
threads, nearly all under 16 payable. **This population spans 1 to 16 payable per unit with a median
of 2**, so the by-unit leg extrapolates the largest unit across all 132 — and the «expensive first»
ordering, borrowed from v5b precisely because it makes the early rate the worst, guarantees that the
wrongest possible reading is the FIRST one. The gate did not discover that the run was
unaffordable; it discovered that its own estimator does not survive a skewed population.

The correction, computed on the evidence this run bought rather than on an argument — the
registration's own model applied to the units still unread:

```
model over the 131 unread units: 5 968 s
elapsed 462 + 5 968 = 6 430 s against usable 9 670  -> GO
and at the 1.08× out-of-sample ratio: 6 908 s      -> GO
```

**That change is not mine to make.** Re-specifying a gate after seeing its verdict is the one thing
a pre-registration exists to forbid, whatever the arithmetic says afterwards. The second attempt and
its estimator are the operator's ruling.

## Attempt B — the estimator the operator ruled, and the review that preceded it

The correction, in `scripts/read_threads_reader_topup.py::projection` (swapped onto v5 the way
`build_pack` is, so the pinned `read_threads_reader_v5.py` is not edited):

```
remaining = max(measured ÷ fitted(read), 1.0) × Σ fitted(unread)
fitted(unit) = intercept + slope × unit.payable_comments
```

Each unread unit is projected at its OWN size, so a pack whose units span 1–16 payable comments is
not extrapolated from whichever unit happened to be read; the calibration is floored at the fit,
because a fast start is not a licence to run long. `results/reader_topup_prereg_b.json` is built
FROM attempt A's record and **refuses unless the only paths that moved are the ones the ruling
covers** — 27 paths moved and every one is on that list; the cap, the meter, the population, all
132 units and all 132 rendering shas are byte-identical.

**A seven-probe adversarial review ran before the pod, and it earned its keep.** Two probes found
nothing (every registration path any of the seven commands can read is answered — the Dv566 class
is closed, with a negative control proving the probe can fail; and no pod behaviour can walk the
projector past the cap). Two returned material findings that are named rather than filed: the
calibration is a single ratio, so at n=1 it decides 132 units from one reading and a first unit at
≥1.47× its fit would STOP a run that fits (2 of the 26 fitted units are that slow; this pack's own
first unit had been measured at 0.96×), and being multiplicative it under-projects a per-unit
ADDITIVE slowdown, where the cap and not the gate is the bound. Both went into the runbook where
the polling happens.

**And one probe returned a BLOCKER, at $0, about the last segment.** Two of them, in fact:

1. `read_threads_reader_v5b.main` routes `--gate` to its boot-kill branch only while the raw file
   is empty. Segment 2's single reply sat in `results/reader_topup_pod.jsonl` **and on the network
   volume the replacement pod mounts**, so segment 3's first gate would have read a measurement
   from a pod that no longer existed: the 720 s boot kill unreachable for the whole segment, and
   the calibration that IS attempt B's cap guard diluted by 77.5 s this pod never spent. Driven,
   not argued — empty raw → exit 2 KILL; the committed row → exit 0 GO with `units_read: 1`.
2. The runbook's wall-clock alarm was still attempt A's FULL cap. Segments 1–2 had billed
   $0.099695, so segment 3 is measured against $1.900305 = **9 184.7 s** usable at $0.74/h, not
   9 669.7 s.

Both were fixed before the create: segment 2's reply is archived as
`results/reader_topup_pod_segment2.jsonl`, the runbook deletes `/workspace/reader_topup_pod.jsonl`
and proves it with an `ls`, the alarm moved to create + 2 h 33 min and `--terminate-after` to
2 h 45 min. The live run then showed `usable_seconds: 9184.7` in its first `--deadlines`, which is
the fix working in the path that spends money.

## Segment 3 — the pass

```
[   146.8s] READY · boot 146.8s
[   233.6s] reply   1/132 @matusi_ukr:22058#1of8   76.8s · 3841 chars · balanced True · finish stop
[  4926.9s] reply 132/132 @ya_Nenka:834            12.2s ·  528 chars · balanced True · finish stop
[  4926.9s] DONE · 132 generated here · 132 replies
```

146.8 s is the best boot this stack has recorded (the previous five: 156.3, 179, 192, 267–293, 373).
The first unit — the same one attempt A stopped on — took 76.8 s against a fitted 80.4, and the
corrected gate returned **GO** where attempt A returned STOP. Twenty gate readings followed and
every one was GO, with the calibration pinned at 1.0 and the headroom growing from 2 806 s to
3 935 s as the small units landed.

The ingest: **142 evidence rows** (132 units plus 10 merged threads), **134 parsed, 8 refused** —
seven units whose reply omitted `entities` and the merged thread that inherits one of them. **99 of
the 105 threads came back with a usable verdict.**

## What the buy bought, against what it was priced at

| | before | after | the projection said |
|---|---:|---:|---:|
| arm B rows with an entity block | 39 of 650 | **282 of 650** | ~279 |
| arm B rows with a BOUGHT topic | 91 | **630** | — |
| rows carrying branch C's ellipsis marker | 372 | **6** | — |
| rows dropped for length | 0 | 0 | — |
| the topic envelope, measured | 147 chars over 24 verdicts | 161 over 123 | — |

**The projection was right to within 1% on the number that decided the ruling.** And what it also
said holds: the gap does not close all the way. The gate's own rows carry 12 of 14 and arm B now
carries 43%, because a reader verdict resolves entities only where the thread HAS them — ten of the
first 24 bought resolved none, and recipe and marketplace threads name nobody. That residual is a
property of the population and no amount of money closes it.

`results/prereg_lora_b.json` is rebuilt on the new datasets and **H6 still re-derives all fourteen**
registered numbers.

## Money



| | | |
|---|---:|---|
| segment 1 | 23.0 s = $0.004728 | the field the shipped gate could not read |
| segment 2 | 462.0 s = $0.094967 | attempt A's by-unit leg, STOP at n=1 |
| segment 3 | 5 479.0 s = $1.126239 | 132 of 132 |
| **the attempt** | **5 964.0 s = $1.225934 of $2.00** | three segments, the maximum the clause allows |
| guard, balance-delta arm | $1.2551 | the pessimistic reading, and it is the one quoted |
| cycle 2 | $3.2707 of $20.00 | remaining $16.7293 |

All three pods deleted and proven: `runpodctl pod list -a` and `serverless list` return `[]` and the
network volume is unchanged in the same reading, which is the positive control that the listing
works at all. The registered projection was $1.34 at this card's rate; the pass came in at $1.126
for its own segment and $1.226 including the two segments that bought the findings.

## What exists now that did not before, and what the failures cost

- the population, priced from its own sizes with an out-of-sample error bar, and what the buy
  changes measured beside it;
- a registration whose every consumer path is probed by a test;
- a driver, a pack builder and a runbook for a reader pass over an arbitrary population, with the
  chunk/merge path driven at $0;
- a boot measurement (156.3 s) and a seconds measurement (77.5 s at 16 payable) that VALIDATE the
  model the projection rests on;
- `build_pass1_sft` reading the top-up evidence when it exists, so a completed pass is one producer
  run away from the datasets.

The two failed segments cost **$0.0997** and bought two defects that would otherwise have been
found later and more expensively — a registration the shipped code could not read, and a cap gate
that cannot survive a population whose units are not alike. The third segment cost **$1.1262** and
bought 99 reader verdicts.

## Deviations from Dv566

| # | finding | tag |
|---|---|---|
| **Dv566** | **The pack was driven at $0 and the driver was not.** Every request was re-rendered against the shipped pod runner with a stub client before the create — handshake, per-item shas, balanced stop, persistence — and the Mac-side driver, which is what reads the registration, was never run at all. `--open` then raised `KeyError: 'threshold_seconds'` on a live meter. Five fields were involved and enumerating them took one grep of `record[...]` across three drivers; doing it after the create cost $0.0047 and a segment. | `[cause: verify-gap]` `[[a-registered-bar-may-have-no-producer]]` |
| **Dv567** | **A cap gate that stops its own run at the first reading.** `max(unread units ÷ read, unread payable ÷ read payable)` extrapolates from the units read, and with sizes spanning 1–16 payable (median 2) ordered expensive-first, the first reading projects the largest unit across all 132: 10 156 s against a 6 049 s fit. STOP at n=1 was not a possible outcome of this registration, it was the certain one. The ordering was copied from v5b for its conservatism and the estimator from v5b for the same reason; neither is wrong on a homogeneous population, and this one is not homogeneous. | `[cause: verify-gap]` `[[a-new-leg-joins-the-gates-denominator]]` |
| **Dv568** | **The published price of branch B was a mean over the wrong population.** «105 × 51.3 s ≈ $1.20» applied the mean seconds of 27 already-read threads to 105 unread ones and ignored that ten of them chunk into 37 units. Re-priced from the sizes: 132 units, $1.34 at the card's own rate. The operator ruled over the wrong number, the correction is upward and small, and it is in the record the ruling is executed under. | `[cause: process]` `[[projected-rate-versus-measured-rate]]` |
| **Dv569** | **The branch's benefit is half of what «closing the context gap» sounds like.** A bought verdict resolves entities only where the thread has them: 14 of the 24 already bought do, 8 of the 15 labelled ones, and 43% of their rows. So the entity block goes from 39 of 650 to ~279 expected, not to 650, while the TOPIC half closes completely. Measured and registered before the money rather than discovered after it. | `[cause: process]` `[[compute-the-ceiling-first]]` |
| **Dv570** | **The review's blocker was invisible to every $0 check that had already passed.** The registration was probed field by field, the pack was driven against the pod runner, all seven driver commands ran green — and none of them asks «what does `--gate` read on a segment that INHERITS a reply». `/workspace` is the network volume: a replacement pod mounts the previous segment's out-file, `read_threads_reader_v5b.main` routes `--gate` to its boot-kill branch only while the raw file is empty, and one inherited row would have made the 720 s kill unreachable for the whole segment while diluting the calibration with 77.5 s another pod spent. Found by an adversarial probe before the create; fixed by archiving segment 2's reply, deleting the volume's copy and proving it with an `ls`. | `[cause: verify-gap]` `[[the-hardening-did-not-reach-the-sibling-reader]]` |
| **Dv571** | **The runbook's wall-clock alarm was the FULL cap on a segment that had already spent 5%.** `usable_seconds` is computed by the code against the remainder — `charged()` nets the closed segments off before `v5.usable_seconds` ever sees the cap — but the hand-held half of the runbook still carried attempt A's 9 669.7 s and «create + 2 h 40 min». For segment 3 the number is 9 184.7 s and 2 h 33 min, and the alarm is exactly the thing that runs when the polling has stopped. The code was right and the instructions a human follows were not, which is the half that has no test. | `[cause: contract-gap]` `[[a-report-proves-it-does-not-instruct]]` |
| **Dv572** | **The projection's own numbers survived contact with the pod, and the residual it predicted survived too.** 279 entity blocks projected, 282 measured; 6 049 s projected, 4 927 s spent; $1.34 projected, $1.126 billed. What the same record said would NOT close did not close: the gate's rows carry 12 of 14 and arm B carries 43%, because a verdict resolves entities only where the thread has them. A projection that publishes what it cannot buy is worth more than one that publishes only what it can. | `[cause: process]` `[[compute-the-ceiling-first]]` |

## Process signals

1. **The proof I built covered the half of the transport I had written.** The pack, the renderer and
   the pod runner were driven at $0; the driver, which is the half that reads the registration, was
   not. Both halves have to be driven, and the one that reads the record is the one that fails
   loudly on a meter.
2. **A conservative rule borrowed from a homogeneous population is not conservative.** Both the
   estimator and the ordering came from v5b with their reasons attached, and the reasons stopped
   holding when the max/median of the unit sizes went from ~3 to 8. A rule that travels needs the
   property it depends on written down beside it.
3. **The stopped run bought exactly one number and it was the one that carried the next one.**
   77.5 s against a predicted 80.4 s validated the model the whole projection rests on, before a
   single dollar of the pass was spent — and segment 3 then read the same unit at 76.8 s. A stopped
   run is not a run with no result.
4. **The gate cost $0.09 and it worked.** It deleted the pod before the cap rather than after, on a
   rule written before the numbers. That its estimator is wrong for this population is a finding
   about the specification; the machinery around it did exactly what it was built to do.
5. **Two defects, both mine, both on the meter — and the second was not invisible at $0 after
   all.** The first was findable by running a command and I did not run it. The second looked like
   it needed a measurement, because the gate's verdict depends on the first unit's seconds. It does
   not: substituting the registration's OWN fitted seconds for the first unit and asking what the
   gate prints at n=1 is a $0 question with the same answer. It is now
   `test_ATTEMPT_A_s_gate_stops_at_its_own_fitted_first_reading`, and its pair
   `test_ATTEMPT_B_s_gate_goes_on_the_same_reading` is the correction — the two beside each other
   are what a reader can check.
6. **The review found what the checks that had already passed could not.** Field probes, a pack
   driven against the pod runner, all seven commands green — and the blocker was a question none of
   them asks: what does the gate read on a segment that INHERITS a reply from the volume. It cost
   nothing to ask and it would have cost the last segment to discover.
7. **Both halves of the run were priced before it, and both prices held.** 279 entity blocks
   projected against 282 measured, $1.34 projected against $1.126 billed — and the residual the
   same record said would NOT close did not close. The projection earned its cost twice: once by
   correcting the $1.20 that was a mean over the wrong population, and once by being checkable
   afterwards.

[[a-new-leg-joins-the-gates-denominator]]
