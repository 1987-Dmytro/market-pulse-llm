# PROGRESS — ship-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; created at s44's start from `docs/plans/promo-pulse-1.PROGRESS.md` per ruling (nn) 4)

## Done — 10.09 s44 «w3» ($0, PHASE-ship-1 §2 item 1): c3's 57 positions are on the screen beside w2's 1113
Start ritual: the re-spec by path (`c22c80f`), the hook-touched `knowledge/` files (`69e75cd`), this
file created with «next: w3» (`5937ad0`).
**(i) the addendum branches on `--step`** (`6f5dbaf`). `WINDOW_ID = "w2"` was read at IMPORT and
`repoint()` never rebound it — fork (c), so c3 would have written w2's answer into its own record.
`STEP_WINDOWS` + `window_for()` resolve the window BEFORE the pin is computed: three legs, not two.
`prereg_promo_c3.json :: addendum[0]` = `window_id w3` · registry `eff8ba5b…` (unmoved since C2's
pin) · `dated 2026-09-10` · `authority` (mm). Preflight: 0 touched paths pinned by any record —
`run_promo_c3.json` names the registration by PATH, so the addendum breaks no pin. Test extended to
both legs + the refusing third (`promo-c4` → «has no window», registration BYTE-EQUAL); c2 untouched.
**(ii) three windows through three seals** (`3692703`). A leg is four values in `PROMO_LEGS`;
`selection_c2`/`c2_anchor` become `selection_promo_leg(prereg, window_id, census_key, manifest_key)`
/`promo_anchor`, `refuse_unless` labelled with the leg's OWN window. `positions` → **`w1|145 ·
w2|1113 · w3|57`**; w3 anchor **2026-09-05 · 28 d · since 2026-08-08** off the census; populations
0 · 30 · 8; the w1 convergence gate still re-derives 902/902 leaves, 0 disagreed.
**(iii) the screen is EVERY window** (`a7b9f74`). `aggregates.positions_source(window_id, excluded)`
is the ONE statement saying which rows the screen may read — a window, or the newest reading of each
`(carrier, row_id)` by anchor. Both trend statements read it, so `deduped()` lost `window_id` from
its partition — MEASURED, not asserted: `--window w2` on a rebuilt store returns the pre-change
export's rollup (401), depth (119), weeks W32–W35 and positions ROW FOR ROW. `--window all` is the
DEFAULT. **`screen.positions` = 1301** = 1244 (w1∪w2 deduped, paused channel out) + 57, all distinct
by `(carrier, row_id)`; the 57 carry `chain.id marketopt_private` (named, until chain-fold); weeks
W27–W36; rollup 571; `not_collected {channels, position_rows: 9}` = @telegraf_kremenchuk's;
`windows` carries all three anchors beside `window_id: "all"`. The refusal sits BEFORE
`ensure_promo_tables` and the first insert: `--window w9` exits 1 naming `['w1','w2','w3']`, both
artefacts byte-identical. One test both ways; **negative control**: with the guard stubbed out
exactly that test fails, having written the empty screen the 09.09 slip produced. K10: a second tick
writes `new 0` in all six tables and the export's sha does not move; a rebuild + retick reproduces it
byte for byte. `make promo-screen` green; `draw_truth_20.py --json` → **population 1301**; the S1
draw and its gold untouched.
**`make check` GREEN at `a7b9f74`: ruff clean, 4332 passed / 2 skipped** (4330 + my two new tests),
in four slices — the suite is over one call's ceiling. Tree porcelain EMPTY. **$0 this session.**

## Next — «chain-fold» ($0, PHASE-ship-1 §2 item 2)
**next: chain-fold.** Then «s2-promote» → «serve-loop» (10.09); «front-1» → «front-2» → «e2e-ship»
(11.09) → the operator's gate 11.09 evening, reserve 12.09 12:00.

## Open stop — NONE. Cloud empty: no pod, endpoint or volume; cycle-3 $8.8398 of $10.00, REMAINING $1.1602 (unmoved).

## Named, not built (the phase file forbids adding what it did not ask for)
- **chain-fold's registered check reads a number the union just moved.** §2 item 2 and (mm) 2(d)
  expect `marketopt_promo` = **79** (22 + 57). That 22 was w2 ALONE: the store carries
  `marketopt_promo w1|4 · w2|22`, so the folded count on the shipped screen is **83** (26 + 57)
  ([[a_ceiling_derived_from_one_span_measured_over_another]]). Not touched — the next item's
  threshold is the team lead's to move or confirm.
- **Fork decided (§4.2), the line §2 lacks:** «rollup/weeks over the same union» attaches the
  `collect: false` clause to positions only. I fed the exclusion to the TRENDS too — a rollup over
  rows the screen does not show is a second population ([[the_shipped_layer_is_fed_the_screened_rows]]).
- **Two sibling readers keep their own `WHERE p.window_id = ?`** — `aggregates.promo_by_chain` and
  `coverage` return silently EMPTY if ever called with `all`, the 09.09 shape one function over
  ([[the_hardening_did_not_reach_the_sibling_reader]]). Latent, not live: only
  `export_dashboard_data` reaches them and it pins w1. «serve-loop» is where it would bite.
- **The closing record does not say which term graded it** — `spend_promo_c3.json` carries
  `"tolerance": 0.05` while the $0.05 FLOOR closed it ([[a_record_must_read_the_gate_its_run_will_face]]).
- **The measured/priced gap stands as s42 left it:** 19.828 s/page against the registered 3.369.
- Carried unchanged: `promo_projection_c2.json` not reproducible from its producer (its pin is the
  proof); no test asserts `cap_from`, `{leg}`, `{STEP}-s4`; `tooling.md`'s «plugin disabled», the
  unfloored arm selector, `graded()`'s `rows`, P1/S2/README untested in the tick, the ties, (jj) 3.
