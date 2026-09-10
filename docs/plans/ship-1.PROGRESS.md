# PROGRESS — ship-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines)

## Done — 10.09 s46 «s2-promote» ($0, PHASE-ship-1 §2 item 3): the feed carries 118 read threads
Start ritual by path: ruling (pp) + PROCESS v2.8 (`8fbb9a4`), the hook-touched `knowledge/` (`013344b`).
**(i) the loop leg's record builder LIFTED** (`3c1f2b8`). `promo_p1_apply.screened()` yields
`(item, answer, record)` per answered thread of a set's arm — the record shaped exactly as
`tick.signal_records` reads one — and `loop()` consumes it where it built it inline. The proof a lift
is a MOVE: re-running it leaves `grade_promo_p1_readings.json` `07401d56…` and
`grade_promo_loop_readings.json` `98e02257…` byte-identical to chain-fold's `b26da6d`.
**(ii) 118 of 120 threads promoted** (`711b847`). `scripts/promote_signals.py` writes one record per
answered thread through that same generator into `results/promo_signals/<channel>_<root>.json`:
dev40 40 · dev2 38 · dev3 40. The two left out are NAMED — `@matusi_ukr/22155` and `/22304`, their
channel `collect: false` in the LIVE registry (the rule `tick.not_collected` applies to the position
rows). Nothing was re-read: the answers are the paid dev loop's, under the four pins of `d598573`.
**(iii) the sentence, and WHICH nothing** (`75d3d32`). `tick.thread_population()` reads the
price-thread frame off `results/promo_threads_draw*.json` (three files, ONE `ids_sha256`, or a
refusal by name — never typed); `threads_read()` subtracts the paused channels and counts the records
on disk; `export` carries it as `screen.threads`, in the screen's CLOSED `REQUIRED` list so a source
that stops being exported refuses instead of blanking a panel. Screen and gate now print
**«118 of 678 price threads read · 548 in the queue · 12 in channels the registry has stopped
collecting»** where they said «the C3 signal leg has not been bought». A row with no reaction has
THREE causes and the gate names the one it means (queued · read and silent · a reaction with its
quote); `read_threads` is that third state's evidence — the feed holds only threads that spoke.
**The checks, run:** first tick over cleared tables — attribution **414** · signal **184** · evidence
**281** · digest **100** · unsure **0** · rollup 0 new (571 stood); `p1: R1 6 · R2 2 · R3 5 over 695
reader rows in 118 threads · 0 threads the store carries no post for`. Second tick — **new 0 in all
six**, export sha `e45860c6…` unmoved (K10). `screen.feed` **281** rows = 280 distinct
`(channel, root, type, msg_id, quote)` EQUAL to the loop leg's P1 signal rows on the same threads
(the repeat is two subjects on one quote, `@VARUS_channel/9277`). `truth_20.json` 20 rows, all queued;
over the whole screen (`--rows 1301`) exactly 1 row's thread is read — `@VARUS_channel/10360` — and it
renders its жалоба and спрос with quotes and msg ids.
**`make check` GREEN at `75d3d32`: ruff clean, 4334 passed / 2 skipped** in four slices (4333 at
`3cc99ad`; the +1 is the parametrised `REQUIRED` case picking up `threads`, not a new test — the two
commits after the reading touch only this file). `make promo-screen`, both producers: porcelain
EMPTY. **$0 this session; nothing created in the cloud.**

## Next — «serve-loop» ($0, PHASE-ship-1 §2 item 4)
**next: serve-loop.** Then «front-1» → «front-2» → «e2e-ship» (11.09) → the operator's gate 11.09 evening, reserve 12.09 12:00.

## Open stop — NONE. Cloud empty: no pod, endpoint or volume; cycle-3 $8.8398 of $10.00, REMAINING $1.1602 (unmoved).

## Deviation — `check`: the item's «unsure > 0» cannot hold on this data
All three sets carry `answers.unsure_comments: 0` in `results/grade_promo_loop_readings.json` — the
readers emitted none on these 120 threads. Whether the class is ever emitted I do not know; the
PLUMBING is exercised (`test_tick`'s record carries one). The clause's other three: 414 / 184 / 281.

## Named, not built (the phase file forbids adding what it did not ask for)
- **No test covers `promote_signals.py`, `tick.thread_population`/`threads_read`, or the gate's third
  state** — §3 closes the door on new tests. The two-frame refusal and the read-and-silent branch have
  no unit behind them, and the second fires on nothing today (0 of 1301 rows: 1 read, and it spoke).
- **`promote_signals.py` never clears its output directory**, so a record renamed by a future change
  would linger and be promoted — deliberate ([[a_rebuild_deletes_its_output_before_it_can_refuse]]).
- Carried from s45, unresolved: `aggregates.promo_by_chain` and `coverage` keep their own
  `WHERE p.window_id = ?` (silently EMPTY on `all`) **and their `source_id` keys are unfolded** —
  (oo) 3 routes both through `positions_source` in «serve-loop», which inherits both
  ([[the_hardening_did_not_reach_the_sibling_reader]]). The fold map still has no validation guard
  (ruled (pp) 2(a): stays named until a two-hop fold is caught).
- Carried unchanged: `spend_promo_c3.json` says `"tolerance": 0.05` where the FLOOR closed it; the gap
  19.828 vs 3.369 s/page; `promo_projection_c2.json` not reproducible from its producer; no test
  asserts `cap_from`/`{leg}`/`{STEP}-s4`, the arm selector, `graded()`'s `rows`, P1/S2/README, the ties.
