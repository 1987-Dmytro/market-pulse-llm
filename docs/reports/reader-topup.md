# Report — `reader-topup` (branch B): two segments, $0.0997, and a gate that stopped its own run

The operator ruled «выполни ветку B» on 2026-08-19. This is the paid reader pass that would give
the pass-1 training set the context its eval prompts carry. **It did not complete.** One unit of 132
was read, both pods were deleted and proven gone, and the attempt billed **$0.099695 of a $2.00
cap**. The two things that ended the segments were defects in MY registration, both found on a
running meter, and the second one is the interesting one: the full-pass gate returned STOP at its
first reading, by construction, on a run whose own measurement confirms it would have fitted.

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

## Money

| | |
|---|---:|
| segment 1 | 23.0 s = $0.004728 |
| segment 2 | 462.0 s = $0.094967 |
| **the attempt** | **485.0 s = $0.099695 of $2.00** |
| guard, balance-delta arm (a lower bound) | $0.0772 |
| cycle 2 | $2.1154 of $20.00 · remaining $17.8846 |

Both pods deleted and proven; `runpodctl pod list -a` and `serverless list` return `[]` and the
network volume is unchanged in the same reading, which is the positive control that the listing
works at all. One segment of the three the recovery clause allows is left.

## What exists now that did not before

- the population, priced from its own sizes with an out-of-sample error bar, and what the buy
  changes measured beside it;
- a registration whose every consumer path is probed by a test;
- a driver, a pack builder and a runbook for a reader pass over an arbitrary population, with the
  chunk/merge path driven at $0;
- a boot measurement (156.3 s) and a seconds measurement (77.5 s at 16 payable) that VALIDATE the
  model the projection rests on;
- `build_pass1_sft` reading the top-up evidence when it exists, so a completed pass is one producer
  run away from the datasets.

The one verdict bought is chunk 1 of 8 of a 125-comment thread, so it merges into nothing on its
own; it is kept as evidence, not as context.

## Deviations from Dv566

| # | finding | tag |
|---|---|---|
| **Dv566** | **The pack was driven at $0 and the driver was not.** Every request was re-rendered against the shipped pod runner with a stub client before the create — handshake, per-item shas, balanced stop, persistence — and the Mac-side driver, which is what reads the registration, was never run at all. `--open` then raised `KeyError: 'threshold_seconds'` on a live meter. Five fields were involved and enumerating them took one grep of `record[...]` across three drivers; doing it after the create cost $0.0047 and a segment. | `[cause: verify-gap]` `[[a-registered-bar-may-have-no-producer]]` |
| **Dv567** | **A cap gate that stops its own run at the first reading.** `max(unread units ÷ read, unread payable ÷ read payable)` extrapolates from the units read, and with sizes spanning 1–16 payable (median 2) ordered expensive-first, the first reading projects the largest unit across all 132: 10 156 s against a 6 049 s fit. STOP at n=1 was not a possible outcome of this registration, it was the certain one. The ordering was copied from v5b for its conservatism and the estimator from v5b for the same reason; neither is wrong on a homogeneous population, and this one is not homogeneous. | `[cause: verify-gap]` `[[a-new-leg-joins-the-gates-denominator]]` |
| **Dv568** | **The published price of branch B was a mean over the wrong population.** «105 × 51.3 s ≈ $1.20» applied the mean seconds of 27 already-read threads to 105 unread ones and ignored that ten of them chunk into 37 units. Re-priced from the sizes: 132 units, $1.34 at the card's own rate. The operator ruled over the wrong number, the correction is upward and small, and it is in the record the ruling is executed under. | `[cause: process]` `[[projected-rate-versus-measured-rate]]` |
| **Dv569** | **The branch's benefit is half of what «closing the context gap» sounds like.** A bought verdict resolves entities only where the thread has them: 14 of the 24 already bought do, 8 of the 15 labelled ones, and 43% of their rows. So the entity block goes from 39 of 650 to ~279 expected, not to 650, while the TOPIC half closes completely. Measured and registered before the money rather than discovered after it. | `[cause: process]` `[[compute-the-ceiling-first]]` |

## Process signals

1. **The proof I built covered the half of the transport I had written.** The pack, the renderer and
   the pod runner were driven at $0; the driver, which is the half that reads the registration, was
   not. Both halves have to be driven, and the one that reads the record is the one that fails
   loudly on a meter.
2. **A conservative rule borrowed from a homogeneous population is not conservative.** Both the
   estimator and the ordering came from v5b with their reasons attached, and the reasons stopped
   holding when the max/median of the unit sizes went from ~3 to 8. A rule that travels needs the
   property it depends on written down beside it.
3. **The run bought exactly one number and it was the one worth having.** 77.5 s against a predicted
   80.4 s validates the model the whole projection rests on, and 156.3 s is the best boot on record.
   A stopped run is not a run with no result.
4. **The gate cost $0.09 and it worked.** It deleted the pod before the cap rather than after, on a
   rule written before the numbers. That its estimator is wrong for this population is a finding
   about the specification; the machinery around it did exactly what it was built to do.
5. **Two defects, both mine, both on the meter — and the second was not invisible at $0 after
   all.** The first was findable by running a command and I did not run it. The second looked like
   it needed a measurement, because the gate's verdict depends on the first unit's seconds. It does
   not: substituting the registration's OWN fitted seconds for the first unit and asking what the
   gate prints at n=1 is a $0 question with the same answer. It is now
   `test_the_gate_stops_at_its_own_fitted_first_reading`, green against this registration and
   written to be edited deliberately by the next one.

[[a-new-leg-joins-the-gates-denominator]]
