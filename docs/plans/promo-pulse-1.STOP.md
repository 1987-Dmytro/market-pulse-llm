# STOP — promo-pulse-1, 2026-09-02 (the third of the day)

**Stop-point:** a rung firing — PROCESS rung 2, the SPEC 3.17 (10)(a) gate: after the two warm-ups the WHOLE step projected at
**$12.5928** against the **$3.95** step cap (+218.8 %), so the run made no gold call and ended (`results/run_promo_c2.json ::
runs[0].go_no_go`, `results/run_promo_c2.log`). Ruling 02.09 (b) item 3: a stop on any gate is the next STOP with the table — the
cap is not raised, the gate is not re-priced here. Beside it, unchanged: waiting on the team lead's labels (dev-40, positions-50).

**What was bought.** Ruling (b) applied at `f17d966` (cap 3.95, text leg = stage 0, rung 0 FITS at the dear corner $3.6059 / −8.7 %);
the step anchored by the guard at $14.19 (`results/spend_promo_pulse_1.json`, `fba2d79`); endpoint `1w2cn98hcikl7b` on template
`ih2rh0mvox` (ADA_24 · EU-RO-1 · 900 s · workers-max 1 · flash-boot) served the pin (`runs[0].info.revision_requested` =
`842da379…`, POSITIONS, base, no adapter); the boot took 149.1 s inside `info()`; warm-ups: **page 13.466 s** on
`atb_market_official_4571.jpg` (481 808 bytes, the first queued page of stage 1), **text 0.794 s**; projection 3 008 × 13.466 +
385 × 0.794 + 60 = 40 811 s → $12.5928, `refuse: true`. Billed: worker 163.348 s, wall 188.918 s → **$0.0579** at the rate
(`runs[0].billed_usd_at_the_rate`); the step ledger's reading is in the report. Torn down and proven by listing: `serverless list`
→ `[]`, the template gone, `mp-srv2` still listed, `pod list -a` → `[]`. Queued posts 385 of 405: twenty were already answered on
disk by 5c2's D cut and the loop subtracts them. Nothing else ran; the derived store did not move (`make tick` twice → 0 new rows).

**Why 13.466 s is not rung 0's 3.369 s — from files, not a diagnosis.**
- The smoke's 2.623…3.369 s/page (`results/promo_projection_c2.json :: verdict.marginal_bound`) is ONE 30-page job's worker time less
  a boot (`results/smoke_vision_c2.json :: timing.calls` = 2, worker 236.15 s) on VARUS 18 · atb_aktsiyi 6 · msuaaaa 4 · two others
  (`results/prereg_smoke_vision_c2.json :: population.rows`): a packed marginal on promo photos.
- 5c2 on the SAME channel (`results/run_5c2_positions.json`): its (10)(a) warm-up page read **1.729 s**; it then realised **10.408 s/row**
  over 205 rows in 24 calls — 159 ATB pages in 11 packs, 106 positions (0.7 per page: the pages are sparse, the output short).
- So one page alone has read 1.7 s and 13.5 s on the same channel, and the packed transport 2.6–3.4 s (promo photos) and ≈10 s
  (ATB leaflet pages). An n = 1 warm-up carries a job's fixed cost and its own variance, and the gate's law multiplies it by 3 008.

**The table (b) asked for** — `results/prereg_promo_c2.json :: population.pages.by_channel` × `runs[0].go_no_go.page_marginal_seconds`
× `rung_0.rates.rate_usd_per_second`; run 1 predates the `outcome.unbought` fix (`8b7b965`), and nothing was bought, so every page is left:

| channel | pages left | $ at 13.466 s/page | channel | pages left | $ at 13.466 s/page |
|---|---:|---:|---|---:|---:|
| `@atb_market_official` | 209 | 0.8631 | `@silposilpo` | 34 | 0.1404 |
| `@ATB_FANatik` | 133 | 0.5493 | `@fozzyshopua` | 3 | 0.0124 |
| `@atb_aktsiyi` | 259 | 1.0696 | `@sim23_simi` | 57 | 0.2354 |
| `@VARUS_channel` | 515 | 2.1269 | `@rrozetka` | 113 | 0.4667 |
| `@ekomarket_shop` | 17 | 0.0702 | `@msuaaaa` | 268 | 1.1068 |
| `@epicentrk_sale` | 78 | 0.3221 | `@kop1chat` | 528 | 2.1806 |
| `@forainfo` | 11 | 0.0454 | `@xochydeshevshe` | 7 | 0.0289 |
| `@marketopt_promo` | 52 | 0.2148 | `@kopiyochka1` | 396 | 1.6354 |
| `@blyzenkoua` | 328 | 1.3546 | **total** | **3 008** | **12.4227** |

Text leg: 385 × 0.794 s = **$0.0938**. Room after the text leg, the cap gate's reserve ($0.2843) and run 1 ($0.0579): **$3.5140** →
851 pages at 13.466 s · ≈1 160 at 5c2's realised 10.408 s · all 3 008 at the smoke's 3.369 s. Each re-run pays one boot (≈$0.046
at 149 s) inside the step cap. The cycle's room is a clock: $0.2333/day.

**THE QUESTIONS — the executor's table, not a decision; the cap stays $3.95 in every row.**
1. **May the (10)(a) gate be applied PER LEG?** Today it is whole-step, so the $0.09 text leg was refused because of the $12.42 page
   leg — the opposite of (b) item 2's intent. Per leg: the text leg projected on its own (385 × 0.794 s) and bought as stage 0.
2. **Which marginal may the page projection read?** (a) the n = 1 warm-up as now — a re-run reads somewhere between 1.7 and 13.5 s and
   the gate is a coin toss; (b) the first PACK of stage 1 as the warm-up (≈15 pages, ≈$0.05 at 10.4 s — «the rate on the transport
   the paid pass would use», the smoke's own question), the whole step projected off it; (c) no whole-step page gate — the stage
   projection after every channel and the per-pack cap gate carry rung 2 and the run stops where the money stops (the table says where).
3. **If the page rate on ATB leaflets is ≈10–13 s, the cap buys 850–1 160 of 3 008 pages.** §3's order as ruled puts ATB's 601 pages
   first; whether the order is re-ranked by pages per dollar is the team lead's, not this file's.

On «go» with the answers: one constant / one gate change in `scripts/run_promo_c2.py` with its test, a fresh `--register`, the runbook
§2–§5 (one boot inside the cap), the same step ledger (left OPEN: no `--close`, a `--note` reading only). Evidence and the checks
(a) (b) (d) (f) (g) (h) (i) (j) (k) (l): `docs/reports/promo-pulse-1.md`.
