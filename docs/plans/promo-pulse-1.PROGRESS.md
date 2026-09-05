# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## The money, live — read BY HAND from the guard today, never carried from a record
Cycle 3 **SPENT $5.5059, REMAINING $3.4941** of the **$9.00** ceiling of ruling (s) addendum 8; anchor
$14.4800 and every session line UNMOVED, balance $8.97. **s24 spent $0 and created no pod — no ledger
line.** Iteration 4 is REGISTERED at cap **$1.20** and prices to **$0.8705**. `promo-holdout` $0.296617,
ledger OPEN; `promo-dev-loop` open by (r)4. The line after it — holdout-2 ≤ $0.90 + c3 ≤ $0.50 + the drip — still fits.

## Done — 05.09 s24, ruling (t) items 3–6, four commits, all $0. **The s23 stop is ANSWERED and CLOSED.**
- **The rate (`1ebc321`).** Both halves of the stop were code. `rate_for("dev")` returned the borrowed
  `pass2_r2` and never asked `own_rate()`; `own_rate()` itself read three SMOKE rows built to hold the
  LONGEST thread — 88.772 s/thread, three times anything this instrument has run at. Now: `own_rate()`
  selects on `contract` + `sample == "whole run"`, the MEAN corner takes the slowest pod's whole-run
  mean and the DEAR corner the largest max — two rows on purpose, though one carries both today.
  `rate_for(part)` = `own_rate()`; the `part != "dev"` condition LEAVES `rung_0`, so every leg issues
  dear-when-it-fits, else mean with the cap as the hard stop. Decision table, smoke prefix and gate 3
  follow the CORNER, not the part. **`--measure-run --replies … --pod-id …`** writes one pod's
  whole-run row from the run record; `--close-segment --replies` writes it at the close.
  **Backfilled at $0, exactly (t)4's three:** iteration 2 **17.7118**/88.237,
  iteration 3 **47.6615**/286.248, holdout **25.8263**/149.054, n=40 each, over the committed
  registrations' own leg-A units. Two false fields died with it: `cap_rule` credited the operator's
  $1.20 to ruling (r)3 (which said $1.10), and `floor_usd` reported $2.00 beside a $1.20 cap.
- **Iteration 4's population (`426a7d7`).** A leg is no longer one arm: `ARMS` is bound by `use_part`,
  the dev leg is `("dev", "holdout")` of the FIRST draw — **dev-40 at order[0:40], dev-2 at [40:80]** —
  and what a hard stop cuts is the tail. `ITERATION = 4`; every dev-branch prose field of the record
  now describes iteration 4 (`re_emission`, `authority` = (t)6, `question`, `law.baseline`).
  `--dry-run`: **80 threads · 701 217 chars · longest 14 281 · 80 distinct renders**.
- **The registration (`1ee15f4`), rung 0 on the real leg at the day's own offer ($0.74/h, stock Medium):**
  cheap 47.661 s/thread → 4234.9 s → **$0.8705 yes (−27.5 %)** · priced → $0.9279 yes · dear 286.248 →
  24316.6 s → $4.9984 **NO (+316.5 %)**. **FITS at the MEAN corner · hard stop 5838 s ≈ 97 min.**
  83 units (3 smoke + 80), leg-A digest `0f34cdc2…`, guard read before the write.
- **The pack (`a6a5b1c`) and the red.** 80 leg-A units, 0 leg-B, smoke first (`@msuaaaa:7187`,
  `@VARUS_channel:9461`, `@VARUS_channel:8647`). `test_the_pack_pins_exactly_what_the_pod_re_derives`
  run BY NAME → **1 passed**: the pack moved, no test was weakened.
- **`make check` GREEN.** ruff clean · pytest sliced 1000 + 2028 + 1293 = **4321 passed, 0 failed,
  2 skipped** (floor 4266). s23's «4320 passed, 1 failed» is gone.

## Next — the PAID iteration 4. Nothing blocks it: the cap is the operator's, the record is committed.
`--terminate-after` from `results/prereg_promo_dev_loop.json :: step.cap_usd` $1.20 → 5838 s; the
registered backstop is 90 min = 5400 s and bites FIRST, with room for ≈107 threads. Sequence:
pre-create check → create → `--open` → smoke (3) → **GO on the three replies, no band gate** (mean
corner) → the 80 → delete → `--close-segment --replies …` (it writes the whole-run row now) → listing
shown → the two readings, which need the FIRST item below. Then holdout-2's gold and its ≤$0.90 shot.

## Open stop — NONE. The tree is clean, six commits this session, $0 spent, no pod, no red test.

## Named, not built (the phase file forbids adding what it did not ask for)
- **`--score` cannot grade an 80-thread leg — the loudest debt, and it lands the moment the pod is
  paid for.** It reads ONE `GOLD` and `k8.strata_of(DRAW, PART)`: dev-40's 140-row key against 80
  answered units, dev-2's own `docs/labels-promo-dev2.jsonl` (188 rows, committed) never opened, and
  `answers.leg_a_units_registered` = 80 against a gold that covers 40. It needs an ARM selector (gold
  + strata + the error table's file names per arm). **The registration pins dev-40's gold only** — a
  second pin is §4-forbidden without a word, and the record's `gold.covers` says so out loud.
- The rung-0 test: the mean branch's assertions went INSIDE it (no new test function), and its wide cap moved $2.50 → $5.00 so the dear-issuing leg stays reachable at all.
- Iteration 1's whole-run row was not asked for and moves NEITHER corner (42.6211 < 47.6615, 201.65 < 286.248) — a priced omission, not a gap.
- `decision_table.after_the_smoke_for_40_threads` keeps its key because `project()` reads it by name ·
  `gates.terminate_after_minutes` is still v5b's borrowed 5400 s · `prep()` calls its count
  `draw.dev_threads` · `pod.main` never lifts `close_arrays_too` · `committed_registration()` ignores
  `pinned_inputs` · `check_law` compares only `codebook_version`, so the moved TEMPLATE passes the
  handshake · holdout-2 lives in `DRAW2` and only `CORPUS` reads it · gold 140/208 · ⛔ `1925810730`.
