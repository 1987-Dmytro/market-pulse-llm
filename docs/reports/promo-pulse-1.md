# promo-pulse-1 — «Что и почём промоутируют сети по молочке и мороженому, и как покупатели на это реагируют — неделя за неделей?»

**Not answered yet, but the paid step is DONE: the whole C2 population is bought, inside the cap, and the phase now stops on a $0 fork.**
Ruling 02.09 (c) put the (10)(a) gate per LEG and the room per CHANNEL (`3ed9c36`); re-registered at `3c617de`. The text leg's own gate
projected **$0.1867** against $3.8803 and passed (`results/run_promo_c2.json :: runs[1].go_no_go`) — under the retired whole-step law its
own warm-up (**11.726 s**, an ATB leaflet page) would have projected ≈$11 and refused a $0.19 leg for the second day running. Each channel
was then measured by its own first pack: **0.7997 s/page** (`@kop1chat`) to **12.9238** (`@blyzenkoua`), a **16× spread on one endpoint**
(`runs[1].measured`, one row per channel in `results/measurements.jsonl`). All seventeen fitted their room and ran WHOLE — `@blyzenkoua`
by $0.063 ($1.2010 against $1.2641). Bought: **3 008 of 3 008 pages** and **385 posts**, `runs[1].unbought` = 0 and 0; **1 199** position
rows now in `data/derived/position_rows/` (106 before) and **54** post positions. **Spend: `PROMO-PULSE-1 SPENT $3.0335 of $3.95`**
(`results/spend_promo_pulse_1.json`, guard `--note`, step OPEN — the billing walk reads $1.9197 and has not settled); `CYCLE 3 SPENT
$3.3252 of $7.00`, `REMAINING $3.6748`, so the dev loop keeps its full $2.50. Endpoint `tq5qxmrczx3iap` / template `g92j8x1wkr` deleted,
proven by listing: `serverless list` → `[]`, template gone, `mp-srv2` still listed, `pod list -a` → `[]`.

**The fork that stops the phase (`docs/plans/promo-pulse-1.STOP.md`).** `scripts/build_aggregates.py` — the only producer of
`data/derived/pulse.db`, and the fixture `tests/test_aggregates.py` builds from — reads the registry THROUGH the 5c2 seal, which pins
revision `d4e3b237…`; the live r2 registry is `eff8ba5b…` and adds exactly the handles S4 bought for (`@ATB_FANatik @blyzenkoua
@fozzyshopua @kop1chat @rrozetka @sim23_simi @xochydeshevshe`). `segment_for()` refuses them by SPEC 3.20 (1), so every rebuild refuses —
since the text leg landed, before any page. The script unlinks the DB first, so `pulse.db` is empty; it is gitignored and rebuildable from
`data/derived/*.jsonl`, which are intact. Three shapes are possible and none is the executor's: a new C2 window and pre-registration · a
live-registry fallback in `segment_for` · restricting the build to the sealed populations. **Do not `make tick` before the ruling.**

**The $0 ranker the ruling asked for is built and measured, and it says no** (`results/rank_remainder_c2.json`, `b2af6c7`): on 5c2's 159 ATB
pages (30 positive, 18.9 %) the OCR ranker reaches recall ≥ 0.90 only by keeping **100 %**, so «buy top-ranked» = «buy whole»; its real cut
is score ≥ 1 — 23 % of pages, recall 0.60, lift 2.58. The caption ranker scores 0 on all 159. No remainder needs it: there is none.

**Deviations.** Dv902 `[cause: ruling]` the gate per leg and per channel, plan §8c. Dv903 `[cause: verify-gap]`
`tests/test_repair_phase4_ledger.py:167` types `spend_cycle2.json` as «the live ledger»; cycle 3 superseded it on 01.09, so the step ledger
written at `d854a63` reads as silent though its witness is in `spend_cycle3.json` at the same timestamp and balance — 3 tests red since
`d854a63`, not from this session's code, not touched. Dv904 `[cause: tooling]` the harness killed the run's process twice mid-flight,
discarding one in-flight job each time (~$0.09 of pages paid for and re-asked); the third launch was detached with `os.setsid()` and
survived, and the driver's own resume re-asked nothing already on disk.

**Checks.** (a) (b) (f) (i) (k) (l) shown in the transcript · (c) bought and durable, blocked from `pulse.db` by the fork · (d) (g) (h)
blocked behind the same fork · (e) waiting on the team lead's labels · (j) below.
