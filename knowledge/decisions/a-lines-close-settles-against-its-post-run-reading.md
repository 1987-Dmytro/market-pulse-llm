---
type: decision
date: 2026-09-05
status: accepted
authority: team lead — ruling 05.09 (w) addendum → PHASE-promo-pulse-1 v13 §6.1
tags: [decision, money, guard]
---

# A step line's close settles against its POST-RUN reading

## What was decided

A money line's tolerance gate compares the settled walk against **the line's LAST OPEN reading**, so
that reading has to be taken **after the pod is deleted and BEFORE any next pod**. One `--note` on
the line, at that moment, is what makes the line closable at all.

A line whose readings **all predate its pod** — its last reading is `0` or absent — closes **on the
walk alone** (the guard skips the tolerance on a `0`/`None` reading) and **NEVER takes a late
reading**: a `--note` taken later carries the balance delta of everything billed since, which is not
this line's money.

## Why

`recorded_reading()` returns the last non-closed `step_spent_usd`. `promo-iter4` carried exactly one
entry, the PRE-pod $0.0097 that opened the line, so a settled ~$0.6915 read **~7000% off** — refused
every time it is run, not once. The reference was never going to appear on its own.

Every line that ever closed under a tolerance had settled against a POST-run reading: `lora-c`
0.7338 → 0.764952 (4.2%) · `promo-pulse-1` 3.0335 → 2.986741 (3.15%) · `srv2b` · `srv2d` · `45h2`.
The reading is the guard's own path, not a way around it.

The mirror case is `promo-holdout`: its one entry reads 0.0 and predates the pod, so the tolerance is
skipped and the walk settles it at **$0.298209**. A `--note` on it that evening would have read
**$1.0708** — the balance delta swallowing iteration 4's pod — and shut the gate for ever.

## How it is applied

1. Pod deleted → **one `--note` on the line**, before anything else is created.
2. `--close --expect-ms <the run record's billed span> --until <a bound inside the line's window>
   --tolerance <the registered band>`. `--until` is not optional once a later pod exists: an
   unbounded walk swallows it and `complete()` reads a third state.
3. The close can still be refused **by a clock**: billing posts 30–40 min late and a PARTIAL walk is
   not a settlement. Retry it at the next session's start, read-only walk FIRST.

Related: [[the-holdout-gate-is-rung-0-fits-plus-the-hard-stop]].
