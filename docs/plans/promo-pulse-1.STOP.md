# STOP — promo-pulse-1, 2026-09-02 (the fourth; the previous STOP was answered by ruling 02.09 (c) and deleted)

**Stop-point:** a design fork the plan does not settle, and it is also a sealed file that would have to move. **The money leg
SUCCEEDED and is closed** — this is not a cap question. `scripts/build_aggregates.py`, the only producer of
`data/derived/pulse.db`, reads the registry THROUGH the 5c2 seal (`registry_through_the_seal`, `results/prereg_5c2_run.json ::
pinned_inputs`), which pins revision `d4e3b237…`. The live registry is r2, `eff8ba5b…`, and the handles r2 added are exactly the
ones S4 just bought pages for: `@ATB_FANatik · @blyzenkoua · @fozzyshopua · @kop1chat · @rrozetka · @sim23_simi ·
@xochydeshevshe`. `segment_for()` refuses them — «carry evidence rows and no registry entry — SPEC 3.20 (1)» — so **every**
rebuild now refuses, and because the script unlinks the database before it builds, `data/derived/pulse.db` is **empty**.
It is gitignored and rebuildable from `data/derived/*.jsonl`, which are intact; nothing bought is lost. Beside this, unchanged:
waiting on the team lead's labels (dev-40, positions-50).

**What ruling 02.09 (c) bought — the whole population, inside the cap.** All **3 008 pages** (`promo_pagecount_c2.json`'s exact
count, verified row for row in `data/derived/leaflet_pages/` against this run's endpoint) and **385 posts** (405 minus the 20
5c2's D cut had already answered). `results/run_promo_c2.json :: runs[1].unbought` = **0 pages, 0 posts**. Positions on disk:
**1 199** leaflet rows in 11 channels (106 before) and **54** post rows in 7. Step ledger: **$3.0335 of $3.95**
(`results/spend_promo_pulse_1.json`, guard `--note`, step left OPEN — the billing walk reads $1.9197 and has not settled);
cycle 3 **$3.3252 of $7.00**, remaining **$3.6748**, so the dev loop keeps its full `min($2.50, …)`. Endpoint `tq5qxmrczx3iap`
and template `g92j8x1wkr` deleted, proven by listing: `serverless list` → `[]`, template gone, `mp-srv2` still listed, `pod list -a` → `[]`.

**The ruling's law, measured.** The text leg's own (10)(a) projected **$0.1867** against $3.8803 and passed; under the retired
whole-step law the same warm-up (**11.726 s**, an ATB leaflet page) would have projected ≈$11 and refused the $0.19 leg a second
time. Every channel was then measured by its own first pack, and the rates run **0.7997 s/page** (`@kop1chat`) to **12.9238**
(`@blyzenkoua`) — a **16×** spread inside one instrument on one endpoint. The carrier measured **5.233 s** where its n=1 warm-up
said 11.726 (over-priced 2.24×). Every one of the 17 channels fitted its room and ran WHOLE; `@blyzenkoua` fitted by $0.063
($1.2010 against $1.2641 of room). One stage reading printed `over_cap: True` and the run correctly continued — that reading is
no longer a gate.

**THE QUESTION — one fork, three shapes; none of them is mine.** How does the C2 window reach `pulse.db`?
1. **A new window and a new pre-registration for C2** (its own `WINDOW_ID`, its own pinned registry = r2), the 5c2 seal untouched.
   Cleanest, and it is a new sealed record — the team lead's to authorise and name.
2. **`segment_for` resolves unknown channels from the LIVE registry** while brands/watchlist stay at the seal. Smallest diff,
   and it weakens exactly what the seal is for («a brand column measured against a different watchlist than the run was priced on»).
3. **The build's input is restricted to the sealed populations** — the C2 rows stay in `data/derived/` and out of the DB until (1).
   Nothing is re-sealed; the screen keeps showing the 5c2 window and S5's re-draw has no C2 population to draw from.

**Blocked behind that fork, all $0:** (c) positions in `pulse.db` per channel · (d) the re-draw of the 50 over what was bought
(`draw_positions_50.py` reads the DB and refuses below 3 chains) · (g) `make tick`'s per-table counts · (h) the clean-clone screen.
**Do not run `make tick` again before the ruling** — it would overwrite `results/promo_screen_data.json` with zeros off the empty DB.

**Check (j) is red in TWO places, and the bigger one is the fork above.** A targeted reading —
`pytest tests/test_aggregates.py tests/test_repair_phase4_ledger.py tests/test_draw_positions_50.py
tests/test_export_dashboard_data.py -q` → **8 failed, 26 passed, 10 errors**: the errors are session
fixtures that BUILD the aggregates from the live derived store, so they refuse for the same SPEC
3.20 (1) reason, and the failures follow the empty database. None of it is weakened here.

**The second, separate ruling for check (j).** `tests/test_repair_phase4_ledger.py:167` types
`LINE_LEDGER = results/spend_cycle2.json` as «the live ledger»; cycle 2 was superseded by cycle 3 on 01.09, so the first step
ledger written under the new line (`results/spend_promo_pulse_1.json`, `d854a63`) reads as SILENT although its witness sits in
`results/spend_cycle3.json` at the same timestamp and the same balance. Three tests red since `d854a63`, none of them from this
session's code. Not touched: a test that must change to pass is a STOP by the predicate (Dv903).

**The $0 ranking instrument the ruling asked for is built and MEASURED, and it says no.** On 5c2's 159 ATB pages (30 positive,
18.9 %): at the ruling's bar, recall ≥ 0.90, the OCR ranker keeps **100 %** — «buy top-ranked» and «buy whole» are the same
purchase. Its only real cut is score ≥ 1: **23 % of pages for recall 0.60**, lift 2.58. The caption ranker scores 0 on all 159.
`results/rank_remainder_c2.json`. It is not needed for THIS remainder (there is none) and stands ready for the next one.

**Deviation to log beside the money:** the harness killed the run's process twice mid-flight (a `TaskStop` on a sibling watcher,
then a plain foreground call), each time discarding one in-flight job — ~$0.09 of pages paid for and not recorded, re-asked on
resume. The third launch was detached with `os.setsid()` and survived. The driver's own resume did its job: markers on disk
subtracted what was answered, and no page was written twice.

On «go»: the ruling's shape for the DB, then `build_aggregates` → `make tick` twice → re-draw the 50 → `make promo-screen` →
the clean-clone check → the report's checks (c) (d) (g) (h) closed. Evidence: `docs/reports/promo-pulse-1.md`.
