# STOP — promo-pulse-1, 2026-09-02 (the second of the day)

**Stop-point:** a rung firing — rung 0 on S4's step, before anything is created. Beside it, unchanged: waiting on the team
lead's labels (`docs/labels-promo-dev.jsonl`, `docs/labels-positions-50.jsonl`), which block K6, K8, S9 and S10 either way.

**THE QUESTION — one, and it takes yes or no.** May `--step-cap` for `promo-pulse-1` be **3.95** instead of 3.20 — the cycle's
room today, $7.00 − $0.2528 spent − $2.50 dev loop − $0.30 holdout = **$3.9472** (`results/spend_cycle3.json`, the guard's own
print), which covers the whole step at the dear corner, **$3.6059** (`results/prereg_promo_c2.json :: rung_0.dear_usd`), plus the
cap gate's one-job reserve, **$0.2843** (`results/prereg_5c2_run.json :: stop_rules.per_job_ceiling.worst_case_job_usd_with_drift`)
= **$3.8902**, and the volume's drip over the run's ≈3.3 h (≈$0.03)?
On «yes»: one constant (`scripts/run_promo_c2.py :: STEP_CAP_USD`), a fresh `--register`, then `knowledge/runbooks/promo_c2_paid_leg.md`
top to bottom. On «no»: 3.20 stands as ruled — the run starts and the per-pack cap gate stops it once ≈$2.92 is spent (3.20 −
0.2843); at the cheap corner everything fits, at the dear one about nine pages in ten and none of the 405 text posts, the unbought
channels recorded for a ruling (SPEC 3.17 (10)(b)). Neither answer is narrowed here: the cap is the team lead's.

**Why rung 0 fires.** The 3.20 was set from `results/promo_projection_c2.json :: verdict.c2_priced_usd` = $3.1563, which priced the
VISION leg alone — its own `population.note`: «the text leg is not priced here». The step buys the text leg too (405 posts,
`results/promo_census_c2.json :: selection.post_text`) and pays whatever boots at creation. The whole step at the projection's own
corners, `results/prereg_promo_c2.json :: rung_0.table` (rates: `marginal_bound` 2.623…3.369 s/page; text 2.8132 s registered in
`results/prereg_5c2_run.json` and 0.947 s warm-up in `results/run_5c2_positions.json`; boots 157.449 s derived / 212.041 s measured):

| corner | page s | text s | boots | usd | vs $3.20 |
|---|---|---|---|---|---|
| cheap | 2.623 | 0.947 | 1 | 2.6041 | −18.6 % |
| priced | 3.369 | 2.813 | 1 | 3.5241 | +10.1 % |
| dear | 3.369 | 2.813 | 2 | 3.6059 | +12.7 % |
| reading — 5c2's realised 10.408 s/page on ATB pages | 10.408 | 2.813 | 0 | 9.9695 | +211 % |

The dear corner decides, for K4's own reason («the guard's `spend()` is the pessimistic max and a ceiling blown after the money is
spent cannot be un-spent»). Not weakened and not re-priced at a kinder corner. The room is a clock — $0.2333/day for `mp-srv2` —
so a «yes» given tomorrow leaves C3 ≈$0.23 short of its two caps; the ruling should say which side gives.

**Everything else is done, all $0, this session.** The anchor moved exactly as ruled (`bf1665d`): guard exit 0, `anchor $14.48`,
`CYCLE 3 SPENT $0.2528 of $7.00`, `REMAINING $6.7472`. The census's 3 008 pages are on disk with their manifest
(`results/post_media_promo_c2.json`, per-channel match against `results/promo_pagecount_c2.json`), the driver `scripts/run_promo_c2.py`
reuses `run_5c2`'s transport and gates (11 tests, the served half driven on a stub: rows durable, a second run sends nothing), the
registration carries rung 0, and the runbook names every command of the paid session. Bought: nothing. No endpoint exists
(`runpodctl serverless list` → `[]`). Evidence: `docs/reports/promo-pulse-1.md`.
