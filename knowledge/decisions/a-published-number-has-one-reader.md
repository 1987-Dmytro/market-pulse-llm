---
type: decision
date: 2026-09-06
status: accepted
authority: executor, under ruling 06.09 (cc) addendum → PHASE-promo-pulse-1 v19 («the numbers and
  the tie analysis on the screen and in the README from result files»)
tags: [decision, reporting, s2]
---

# A published number has ONE reader, and a missing source is a refusal by name

## What was decided

A number that appears on more than one surface is read by **one function**, from a **named result
file**, and every surface calls it. For S2 that function is
`scripts/build_promo_screen.py :: s2_readings()`; `build_readme_results.py` imports it rather than
re-deriving anything, so the promo screen and the README cannot print two values for one reading.

The sources are a **closed list** (`S2_SOURCES`): label · file under `results/` · the path to the
block inside it. A file that is missing, or present without the block it is read for, is a
**non-zero exit naming what is missing** — never a blank row.

Everything printed comes off the record, including the bars: the value, the bar and the `held`
verdict are the grader's own fields, and the tie count is the P1 record's `misses_after`.

## Why

The phase's own rule is «numbers only from result files through the scorer, never typed». Two
surfaces that each format their own copy is how the same reading gets published twice with
different values — the failure this repo already carries as [[two_gates_on_one_spend_read_different_corners]]
and [[the_cheap_file_gets_the_expected_number]]. One reader makes that impossible by construction
rather than by discipline.

The by-name refusal is the other half. A screen that renders a blank panel over a missing grade
reads as «not measured», which is a claim about the instrument — the same argument
`build_promo_screen`'s K12 control already makes for the market blocks.

The bars were the near miss: they were first typed into the README block's header prose as «bar
0.80» / «bar 0.75» while every cell beside them read its file. Deriving them left the file's bytes
identical, which is the proof the typed values had been right — and no protection at all against
the day a bar moves ([[a_threshold_that_lives_in_prose]]).

## How it is applied

1. A new published number gets a row in `S2_SOURCES` (or its analogue), never a literal.
2. Its surface calls the shared reader; a second surface imports that reader.
3. The refusal is demonstrated, not asserted in prose: `--results <empty dir>` exits 1 and names the
   first missing file.
4. The README block lives between markers and is regenerated, never edited. It has **no caller yet**
   — no Makefile target, no test — so it goes stale silently when a number moves; naming that is
   part of this record, and building the guard is a ruling, not an executor's addition.

Related: [[the_shipped_layer_is_fed_the_screened_rows]] — the same day's lesson about the number
itself, one layer down: publishing a value correctly does not make the shipped path reproduce it.
