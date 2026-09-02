# promo-pulse-1 — «Что и почём промоутируют сети по молочке и мороженому, и как покупатели на это реагируют — неделя за неделей?»

**Still not answered; this session bought the first paid step's warm-ups and its own gate refused the step.** Ruling 02.09 (b) was applied
at `f17d966` (`scripts/run_promo_c2.py :: STEP_CAP_USD` = 3.95, the text leg = stage 0, `results/prereg_promo_c2.json :: rung_0.fits` true — dear
$3.6059, −8.7 %). The guard anchored the step (`results/spend_promo_pulse_1.json`, `fba2d79`, $14.19) and passed inside the run (exit 0, both caps);
endpoint `1w2cn98hcikl7b` served the pin; the SPEC 3.17 (10)(a) gate then read the warm-ups — **page 13.466 s** on `atb_market_official_4571.jpg`,
text 0.794 s — and projected the whole step at **$12.5928 against $3.95** (+218.8 %): `refuse: true`, no gold call (`results/run_promo_c2.json ::
runs[0].go_no_go`, `results/run_promo_c2.log`). **Spend of the paid leg: $0.0579** at the rate (`runs[0].billed_usd_at_the_rate`, worker 163.348 s =
one 149 s boot + the two warm-ups); the step ledger (`d854a63`, `gpu_sessions[0]`): `PROMO-PULSE-1 SPENT $0.0599 of $3.95` at 13:30 UTC — balance delta, billing rows
not yet settled, a LOWER BOUND holding 34 min of drip; cycle `CYCLE 3 SPENT $0.3516 of $7.00`, `REMAINING $6.6484`. Torn down, proven by listing (`serverless list`
→ `[]`, template `ih2rh0mvox` gone, `mp-srv2` listed, `pod list -a` → `[]`). Nothing landed in `data/derived/`. STOP with the ruling's table and
three questions (per-leg gate · which page marginal · order under a partial buy): `docs/plans/promo-pulse-1.STOP.md`. The step stays OPEN.

**The rungs, logged.** (0) `rung_0` FITS in the registration (cheap $2.6041 · priced $3.5241 · dear $3.6059, every rate a file); (1) the create:
`executionTimeoutMs` 900 000, `workersMax` 1, `retries=0` in the client; (2) the (10)(a) gate above — the projection over the cap stopped the run
before any gold call; (3) the per-pack cap gate: not reached. Why 13.466 s is neither 5c2's 1.729 s warm-up on the same channel nor the smoke's
2.623…3.369 s: the STOP walks the files (`run_5c2_positions.json`, `smoke_vision_c2.json`, `prereg_smoke_vision_c2.json`). A (10)(a) refusal now
records `outcome.unbought` too (`8b7b965`, tested); run 1 predates it, so the STOP derives its table from `queued` and the registration.
**The $0 checks, each run in the transcript.** (a) `results/promo_pagecount_c2.json`: 17 channels, `pages_exact` 3 008 = `pages` 3 008, 0 unreachable;
`results/promo_projection_c2.json :: verdict.c2_priced_usd` = 3.1563, one number at `marginal_bound`. (b) `tests/test_collect_5c1.py -k collect`: 23 passed,
both directions (`…paused_source_is_not_collected…`, `…same_source_collecting_is_collected`). (d) `scripts/draw_positions_50.py` twice → one sha
`a3f659f9a8d73f5e…`, porcelain clean (pre-C2 population, 50 of 145; the re-draw waits for S4). (f) `tests/test_trends_sql.py`: 10 passed. (g) `make tick`
twice: `new 0` on attribution · signal · evidence · digest · unsure · rollup, `results/promo_screen_data.json` `a64f5489…` both times. (h) clean clone at
`8b7b965`: `make tick` → «no store … nothing written», `make promo-screen` renders `dashboard/promo.html` `28fffc93…` from the result file; the source removed
→ «promo-screen REFUSED: missing source …», exit 2. (i) `scripts/draw_truth_20.py`: 20 rows, seed 42, `results/truth_20.json` byte-identical. (c), (e),
(d)'s grade: wait on S4 and the labels. Debts unchanged: `scripts/promo_projection_c2.py` (`:366` / `:171` / `:153`), K4 not re-run; Dv15.

**`make check-stamped` at `b61f6b8`: `BEFORE HEAD b61f6b8` · `ruff` «All checks passed!» · `4279 passed, 2 skipped in 728.51s (0:12:08)` · `AFTER HEAD
b61f6b8` · `suite make check → exit 0` · `reading HOLDS`** (4 266 + the 13 new; no test file deleted, none weakened — the cap test was tightened). After it:
the ledger's `--note`, this report, `knowledge/`. `git status --porcelain src tests scripts config results docs/plans docs/reports` prints nothing.
