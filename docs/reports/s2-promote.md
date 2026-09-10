# s2-promote — the bought reactions reach the feed ($0, s46, PHASE-ship-1 §2 item 3)

## Answer
**Do the reactions the paid dev loop bought reach the screen's feed, and does the screen stop saying
«not bought»?** — **Yes, both.** `results/promo_screen_data.json :: screen.feed` = **281** rows where
it was `[]`; `screen.threads` = **118 read of 678 · 548 in the queue · 12 in channels the registry has
stopped collecting**, printed by the screen and the gate where they said «the C3 signal leg has not
been bought». `results/promo_signals/` holds **118** records — 120 registered, `@matusi_ukr/22155`
and `/22304` left out and named (`collect: false`, live registry). The feed's 281 rows are 280
distinct `(channel, root, type, msg_id, quote)`, a set **equal** to the loop leg's P1 signal rows on
the same threads; `grade_promo_loop_readings.json` `98e02257…` and `grade_promo_p1_readings.json`
`07401d56…` byte-identical to chain-fold's `b26da6d` — no graded number moved.

## Evidence
- `3c1f2b8` `promo_p1_apply.screened()` lifted out of `loop()`: ONE generator yields the record
  `tick.signal_records` reads, both legs consume it — proof it is a move and not a second spelling:
  re-run → the two graded records byte-identical, `git status --porcelain results` empty.
- `711b847` `scripts/promote_signals.py` → `results/promo_signals/`: `dev40 40 · dev2 38 · dev3 40`.
- `75d3d32` `tick.thread_population()` reads the frame off `results/promo_threads_draw*.json` (three
  files, ONE `ids_sha256`, else a refusal by name); `threads_read()` subtracts the paused channels and
  counts the records; `export` carries `screen.threads` in the CLOSED `REQUIRED` list. `make tick`
  first: `attribution 414 · signal 184 · evidence 281 · digest 100 · unsure 0 · rollup 0 new (571
  stood)`, `p1: R1 6 · R2 2 · R3 5 over 695 reader rows in 118 threads · 0 without a post`; second and
  third: **new 0 in all six**, export sha `e45860c6…` unmoved (K10); `make promo-screen` (both
  producers) → porcelain EMPTY. A row with no reaction now says WHICH nothing (queued ·
  read-and-silent · a reaction): `truth_20.json` 20 rows all queued, `--rows 1301` → exactly 1 read
  thread, `@VARUS_channel/10360`, rendering its жалоба and спрос with quotes and msg ids. Tests:
  **none added** (§3); two fixtures gained `screen.threads`, «WHICH nothing» reads the record (§4.4).

## Deviations
`Dv1 [cause: spec-gap]` «unsure > 0» cannot hold — all three sets carry `answers.unsure_comments: 0`
in `grade_promo_loop_readings.json`; measured, not manufactured, and the plumbing is exercised by
`test_tick`'s own record. The clause's other three: 414 / 184 / 281.

## Debts (named in PROGRESS, not built)
No unit test for `promote_signals.py`, `tick.thread_population`/`threads_read` or the gate's third
state (§3), which fires on nothing today; `promote_signals.py` does not clear its output directory,
deliberately. Carried: `promo_by_chain`/`coverage` (empty on `all`, unfolded `source_id`) →
«serve-loop»; the fold map's missing validation guard, ruled (pp) 2(a).

## make check
`ruff check .` clean · `pytest -q` in four slices at `75d3d32`: `963` · `1574` · `961` · `836 passed,
2 skipped` = **4334 / 2** (4333 at `3cc99ad`; the +1 is the parametrised `REQUIRED` case picking up
`threads`). HEAD **`b94cc01`**, porcelain EMPTY, **$0 this session**.
