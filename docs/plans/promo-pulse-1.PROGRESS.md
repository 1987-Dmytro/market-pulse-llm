# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## Done — 09.09 s43 «kk-close» ($0, ruling (kk) 5): the floor is in, `promo-c3` is CLOSED at $0.2577, the volume is GONE
Start ritual: no team-lead file was modified; the three hook-touched `knowledge/` files by path (`c09404e`).
**(i) the floor.** `DOLLAR_FLOOR = 0.05` beside `MS_FLOOR`, and `runpod_guard.py:911` (was `:897`) becomes
`abs(settled − recorded) > max(DOLLAR_FLOOR, args.tolerance * abs(recorded))`. The refusal now names WHICH of the two
terms the run faced (`the gate is $0.050000: the greater of the $0.05 floor and the band`). `--tolerance` stays 5%.
**(ii) the test, four rows, both ways** (`test_the_dollar_floor_grades_a_sub_dollar_leg_the_relative_band_cannot`):
c3's REAL pair (recorded $0.2272, settled $0.257668) CLOSES · a $0.20 gap on the same recorded reading still REFUSES ·
a $2.99 leg CLOSES at $0.10 and REFUSES at $0.21 — the relative band decides both of those exactly as before, which is
what makes «binds only below a dollar» checkable. Each refusing row asserts the BAND's own message, because at the
fixture's default balance the step CAP refuses them anyway ([[an_inequality_that_holds_for_the_wrong_reason]] — found
and fixed mid-test). **Negative control run:** with the guard change stashed, exactly one row fails, c3's own.
`tests/test_runpod_guard.py` 57 passed; ruff clean. Commit `c5cad96`.
**`make check` GREEN at `c5cad96`: ruff clean, 4330 passed / 2 skipped (11:51)** — 4326 + the four new rows, so the
change moved no existing test. The three commits after it move only the two ledgers (`spend_promo_c3.json`,
`spend_cycle3.json` — the seven test files reading them re-run, **151 passed**), this file, and `knowledge/hot.md`,
whose two grepped literals `tests/test_volume_calc_5c1.py` reads — **10 passed** after the restamp.
**The close.** Read-only walk first: `step resources $0.2577` = `pods $0.030461` + `serverless $0.227207`, the
`network-volume $0.009722` outside by construction. Then the close: **`CLOSED spend_promo_c3.json at $0.2577 — entry
APPENDED`**, `PROMO-C3 CLOSED $0.2577 of $0.80` (settled 18:57:04Z, window from 16:26:09Z, `walk_ms 889500`,
`expected_ms null`). The gap $0.030468 sat under the $0.05 floor while 5% × $0.2272 = $0.0114 — **the floor graded it,
not the band**, which is the whole ruling. One settlement, two ledger files: the step's (`d60b303`) and cycle-3's line
reading (`b361e57`, $8.8398 of $10.00, REMAINING **$1.1602**).
**The volume.** `network-volume delete qw4nwleanc` → `{"deleted": true}`; the listing after is **`[]`**. The ≈$0.24/day
drip is stopped. No pod, no endpoint, no volume — the cloud is empty.

## Deviation — `--window all` is NOT a window id, and the tick empties the screen without an error (cause: contract-gap)
(kk) 5 and `knowledge/hot.md` both carried `make tick --window all`. `--window` takes a window ID; the `windows` table
holds exactly two rows, `w1` and `w2`. `all` matches nothing, and `scripts/tick.py` wrote the shipped screen with
**`positions` 1113 → 0** (−28 967 lines) and no non-zero exit. Nothing was committed: the artifacts were restored from
HEAD and `make tick` was re-run on its real window `w2` — the one ruling 02.09 (d) pins. **The substitution is proven,
not asserted:** after the restore + rebuild, `git status --porcelain results dashboard README.md` prints NOTHING, so
the w2 rebuild reproduces HEAD byte-for-byte and the tick's own §8 (g) claim (a second run on an unchanged store writes
zero new rows) holds — all six counters `new 0`, `rollup 401 → 401`. `make promo-screen` green, both writers.
The hot-cache line is corrected in my own file; the runbook's and (kk) 5's are the team lead's to move.

## Next — «chain-fold» ($0, shape (b), ruling (gg) 2 — P1 re-measured by the product's own functions)
**next: chain-fold.** Then «launch-field» ($0) → clean-clone e2e + `draw_truth_20` → the gate **12.09** (13.09 reserve).

## Open stop — NONE
The band refusal s42 carried is repaired and the line it held open is closed. Nothing is waiting on a decision.
**Tree at 19:02Z:** clause (l)'s porcelain over its seven paths EMPTY. `make check` green at `c5cad96` as above.
Cloud empty on the listing: `serverless []`, `pod list -a []`, `network-volume list []`, templates the two pre-existing.
`promo-c3` CLOSED at $0.2577 of its $0.80 cap; cycle-3 $8.8398 of $10.00, REMAINING $1.1602; **$0 spent this session**.

## Named, not built (the phase file forbids adding what it did not ask for)
- **The closing record does not say which term graded it.** `spend_promo_c3.json`'s entry carries `"tolerance": 0.05`
  while the $0.05 FLOOR is what let it close ([[a_record_must_read_the_gate_its_run_will_face]]). A `dollar_floor`
  field is a ledger field (kk) 5 did not ask for — named here, not written.
- **`--window all` fails silently** (above): a window id the table does not carry deserves a non-zero exit, not an
  empty screen ([[a_checker_whose_failure_is_silence]]). A guard the phase file did not ask for.
- **c3's 57 positions reach no window of the store.** `positions` by window is still `w1 145 · w2 1113`; c3's channel
  has 0 rows there, and `scripts/tick.py` does not read `results/run_promo_c3.json` at all. c3's anchor is 2026-09-05
  and w2 ends 2026-08-31, so the leg's output is on disk in its own record and in no window — §8 (c) reads on the
  store, so this is the team lead's call, not a window I may create.
- **The measured/priced gap stands as s42 left it:** 19.828 s/page against the registered 3.369. No threshold moved.
- Carried unchanged: `promo_projection_c2.json` is not reproducible from its producer (its pin is the proof); no test
  asserts `cap_from`, `{leg}` or the `{STEP}-s4` contract; `tooling.md`'s «plugin disabled», the unfloored arm
  selector, `graded()`'s `rows`, P1/S2/README untested in the tick, the ties; (jj) 3's two nits stay in «chain-fold».
