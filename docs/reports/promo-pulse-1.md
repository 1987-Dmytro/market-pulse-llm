# REPORT — `promo-pulse-1`, session 5 (2026-09-03): the C2 window is IN, the phase stops on w1's seals

**Question (`docs/PHASE-promo-pulse-1.md` §1):** «Что и почём промоутируют сети по молочке и мороженому, и как
покупатели на это реагируют — неделя за неделей?»

**Answer, half of it now real.** The WHAT and the POČЁM are in the database: `data/derived/pulse.db` carries the C2
window `w2` — **17 channels · 3 397 markers · 1 113 position rows** (`scripts/build_aggregates.py` stdout) — and the
screen renders from it: **401 rollup rows** over the C2 weeks (`make tick`, `results/promo_screen_data.json ::
window_id = w2`). The REACTION half is still unbought: `attribution/signal/evidence/digest/unsure` are 0→0 because
S9's first paid call has not run, and ruling 03.09 puts the team lead's read of the re-rendered prompt before it.
Ruling 02.09 (d) shape 1 is implemented and `w1` is intact where it can be: **902/902** numeric leaves of the sealed
`results/window_summary_5c2.json` re-derived from SQL, 0 disagreed, 0 missing. The phase stops because shape 1 alone
does not restore w1's SEALED artifacts — see `docs/plans/promo-pulse-1.STOP.md`.

**Money.** Nothing created, nothing bought. `PROMO-PULSE-1 SPENT $3.1909 of $3.95` · `CYCLE 3 SPENT $3.4826 of $7.00`
· `REMAINING $3.5174` (`scripts/runpod_guard.py --step promo-pulse-1 --step-cap 3.95`). The step's two paid legs,
named: **$0.0599** (run 1, the (10)(a) gate refused the whole step at a 13.466 s warm-up — 0 pages bought) and
**$3.0335** (run 2, 3 008 pages + 385 posts) — `results/spend_promo_pulse_1.json :: gpu_sessions`. The step is not
CLOSED: `--close --tolerance` takes a fraction the plan does not name (STOP item 3).

**Checks.** (a) `results/promo_pagecount_c2.json` 17 channels, **3 008** pages exact from store metadata;
`results/promo_projection_c2.json :: verdict.c2_priced_usd` **$3.1563**, ONE number at the marginal. (b)
`tests/test_collect_5c1.py` **23 passed** — `collect: false` refused and `collect: true` collected. (c) positions per
channel above; five channels read 0 and it is an ANSWER (`unreadable` 0, `n_positions` sums to 0 — DIY, coupon and
electronics channels). (d) `results/positions_draw_50.json` drawn twice, identical sha **`61b4fda7fdc83197…`**, 50 of
1 113 from 12 chains — the grader waits on `docs/labels-positions-50.jsonl`. (e) `promo_prompts.CODEBOOK` re-rendered
from `docs/CODEBOOK-promo-signals.md` v1, `codebook_version()` **`a97d3c71b8cf9b14…`**; the gold passed all four hooks
as a fixture — **140 about rows, 84 signal rows, 0 failures**, 140/140 comments with text covered. (f)
`tests/test_trends_sql.py` **10 passed**. (g) `make tick` twice: **zero new rows in all six tables**, `unsure`
included, rollup 401→401. (h) clean clone `make tick && make promo-screen` exit 0; source removed → **exit 2** with
«promo-screen REFUSED: missing source …». (i) `scripts/draw_truth_20.py` 20 rows, seed 42. (l) porcelain clean.

**Deviations.** `[cause: ruling]` `tests/test_repair_phase4_ledger.py` derives its live lines from the guard's
constants (02.09 (d)) — 12 passed, the 3 Dv903 reds are gone. `[cause: the data]` `positions` gains `carrier` in its
PRIMARY KEY: 7 C2 posts were read by both legs and `channel:msg_id:ordinal` cannot tell them apart; no stored id
moves; `test_positions_is_untouched` is RED and named, not weakened. `[cause: the run]` **16 of the 405 pinned C2
posts have no evidence row** — `runs[1].post_text` is `[]` (lost to the harness kills), so `unbought` 0/0 is a claim
about the page stages only.

**`make check`:** **21 failed · 4 254 passed · 2 skipped · 7 errors in 731.25 s** (baseline 18/4 247/17 = 35 red; now 28, passed +7). Of the 28: **19 are fork 1** (`test_window_summary_5c2` 2, `test_export_dashboard_data` 2, `test_build_dashboard` 4+7, `test_build_validate_pack` 4), **1 is fork 2** (`test_positions_is_untouched`), **7 are the window default** — `test_draw_positions_50` (6) and `test_tick::test_the_first_tick_fills_all_six_tables` build a `w1` fixture and call the script with its default, which is now `w2`: fixture wiring, named here and NOT weakened. Nothing else is red.
