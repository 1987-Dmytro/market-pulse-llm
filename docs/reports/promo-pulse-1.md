# promo-pulse-1 — «Что и почём промоутируют сети по молочке и мороженому, и как покупатели на это реагируют — неделя за неделей?»

**Still not answered, and this session says exactly why: the instrument is finished and the money line is not open IN CODE.** `make tick && make promo-screen` runs end to
end on a CLEAN CLONE and renders the screen byte for byte as it renders here (`dashboard/promo.html` `28fffc93c723ab8d…`) out of `results/promo_screen_data.json` and no
other file. It renders 145 positions and **89 rollup rows** over six ISO weeks — 5c2's old population, not the census window — and **zero reactions**:
`attribution/signal/evidence/digest/unsure` all 0 (`results/promo_screen_data.json :: screen.table_rows`), because C2 and C3 are unbought; **2 290 threads are cooled,
waiting to be read** (the tick's count). The ceiling was raised to **$7.00** as the 01.09 (later) ruling says, the guard refuses anyway, and no paid leg ran. STOP:
`docs/plans/promo-pulse-1.STOP.md`.

**The refusal.** `CYCLE3_CAP_USD = 7.00` and the ledger's `note` carry the operator's word (`scripts/runpod_guard.py`, `results/spend_cycle3.json`, `981202b`). The ruling
also says «anchor unchanged», and `enforce()` refuses on a balance above the anchor: **$14.26** over **$4.48**, `CYCLE 3 SPENT $0.2139 of $7.00 · REMAINING $6.7861`,
**exit 1**; rung 0 (`--step promo-pulse-1 --step-cap 3.20`) exits 1 and writes no step ledger. It is the module's documented invariant, not a defect, and re-anchoring is
the operator's by the guard's own words; the same `return 1` precedes the `--note` append, so the note went in by hand. At $7.00 it fits: $3.1563
(`results/promo_projection_c2.json :: verdict.c2_priced_usd`) + $2.50 + $0.30 = **$5.9563**.

**`/code-review` (fresh subagent, `3a614f4 + 0a8d02a + d305953 + 981202b`), the condition before the first paid leg: «BLOCKING — 2 findings» plus 3 notes.** Both fixed in
`97e84e6`. (1) «the live-line `--close` writes the ledger BEFORE the refusal check at `:952`, so a refused run still closes the money line» — the entry is HELD until the
verdict now; re-run live: exit 1, `results/spend_cycle3.json` byte-identical, `sessions` `[]`. (2) «the watch list is still closed by its anchor» — a `CYCLE4_LEDGER` plus
a writer left the suite green, so `conftest.LEDGERS` is now DERIVED from the guard's own `Path` constants, the teardown walks `results/spend_*.json` (44 files, 22 step
ledgers included), and the control edits the guard's source. **Notes 4–5, named debt:** `promo_projection_c2.py` writes «cycle 3 is open at $4.80» into its record
(`:366`), greps `CYCLE 2 SPENT` so `remainder.spent_line` is `""` (`:171`), and ignores the guard's exit code (`:153`) — K4 must not be re-run until then.

**Landed, all $0** — S12–S14 and S5: `make tick`, `make promo-screen`, `draw_truth_20.py`, `draw_positions_50.py`, six promo-table writers and `upsert_digest`. K10 holds
on the LIVE store (zero new per table, export sha unmoved), but five of six tables are at zero there, so the discriminating reading is `tests/test_tick.py` — two ticks
over a store with rows in **all six**, its negative control, and the late-comment delta (one digest, version 1→2, children 101,102 → 101,102,103). K12 on the clone:
source removed → `make: *** [promo-screen] Error 1`, file named. K13: 20 rows, seed 42, twice `3d80c81a9c353130…`, same in the clone. K5: 50 of 145 over 8 chains, twice
`a3f659f9a8d73f5e…` — PRE-C2 population, said so in the record, not yet the file to label. **Dv15** `[cause: process]`: the cooled/digest helpers landed in
`scripts/tick.py`, not `loop.py` as plan §3 names — ten sealed records pin it; same cause as Dv14. No pin moved.

**`make check` at `97e84e6`: 4 266 passed · 2 skipped · exit 0** (4 230 + the 36 new tests). `git status --porcelain src tests scripts config results docs/plans docs/reports` prints nothing.
