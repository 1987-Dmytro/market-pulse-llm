# promo-pulse-1 — «Что и почём промоутируют сети по молочке и мороженому, и как покупатели на это реагируют — неделя за неделей?»

**Still not answered, and this session got the money line open and the first paid step priced — where rung 0 fires.** The anchor moved
exactly as ruling 02.09 says (`results/spend_cycle3.json`, `bf1665d`): `scripts/runpod_guard.py` → exit 0, `anchor $14.48`, `balance now $14.23`,
`CYCLE 3 SPENT $0.2528 of $7.00`, `REMAINING $6.7472`. S4's step was then priced WHOLE before anything was created — `results/prereg_promo_c2.json ::
rung_0` — and the dear corner is **$3.6059** against the ruling's `--step-cap 3.20` (+12.7 %; the priced corner $3.5241, +10.1 %; only the cheap corner,
$2.6041, fits). The 3.20 was set from `results/promo_projection_c2.json :: verdict.c2_priced_usd` = $3.1563, which priced the vision leg alone («the text leg
is not priced here»); the step buys 405 text posts too (`results/promo_census_c2.json :: selection.post_text`) and pays a second boot. `--run` refuses at
rung 0 before a key or a client exists (`run exit=1`); nothing was created, nothing bought (`runpodctl serverless list` → `[]`). STOP with ONE yes/no
question — the cap — in `docs/plans/promo-pulse-1.STOP.md`. The screen is still the pre-C2 one (`dashboard/promo.html` `28fffc93c723ab8d…`).

**Rung 0's table, every rate a file** (`results/prereg_promo_c2.json :: rung_0.rates`): pages 2.623…3.369 s (`results/promo_projection_c2.json ::
verdict.marginal_bound`), text 0.947 s warm-up (`results/run_5c2_positions.json :: go_no_go`) / 2.8132 s registered (`results/prereg_5c2_run.json ::
prices.post_text`), boots 157.449 s derived / 212.041 s measured (`results/smoke_vision_c2.json :: rung_0`), tail 60 s, $0.00030669/s. 5c2's realised
10.408 s/page is carried as a READING ($9.9695) beside the corners. The per-pack cap gate reserves one wedged job ($0.2843, `results/prereg_5c2_run.json ::
stop_rules.per_job_ceiling`) below the cap, so 3.20 has ≈$2.92 usable.

**Landed this session, all $0.** (1) `scripts/fetch_promo_media_c2.py` → `results/post_media_promo_c2.json`: 968 posts, **3 008 of 3 008** photo members
on disk (`data/annotation/promo_c2/posts_media/`, gitignored), `totals.channels_matching_pagecount` 17 of 17 against `results/promo_pagecount_c2.json`,
188 non-photo members recorded (the pagecount's 146 video + 3 poll + 39 other); a download the harness killed mid-write was re-fetched (`intact()`, tested).
(2) `scripts/run_promo_c2.py` — `--register` / `--dry-run` / `--run`; transport, money gates and legs are `run_5c2`'s by import; pages from the manifest,
text posts pinned by id off the live store (`ids_sha256` `b6bc2f67…` / `590f91e4…`); stages in the phase spec §3's order; a re-projection after every
channel; the guard (`--step promo-pulse-1 --step-cap 3.20`) runs before the first call. `tests/test_run_promo_c2.py`: 12 tests, the served half driven
on a stub through the real passes — rows durable, a second `--run` sends nothing, a refusing (10)(a) gate makes no gold call and still writes the record.
(3) `knowledge/runbooks/promo_c2_paid_leg.md`, the paid session's commands; plan §8 lists every choice. **Debts unchanged:** `scripts/promo_projection_c2.py`
(`:366` / `:171` / `:153`) — K4 not re-run until fixed; Dv15 `[cause: process]`. No pin moved. Labels owed: dev-40, positions-50 (re-drawn after S4).

**`make check` at `50ef7d9`: `ruff` «All checks passed!» · `4278 passed, 2 skipped in 685.64s (0:11:25)` · `make check exit=0`** (4 266 + the 12 new; no test
file deleted, none changed to pass). `git status --porcelain src tests scripts config results docs/plans docs/reports` prints nothing.
