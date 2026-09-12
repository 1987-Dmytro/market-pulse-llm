# prices-and-region — per-category promo prices, and the operator's Poltava cut

**Question.** Can the marketing director open the app and see, per category, how many positions are
in promo this week, which pack is cheapest, which is dearest and what the median costs — and see
the region's chains as SKU cards?

**Answer: yes, both, at $0, and the app still computes no figure of its own.** Three blocks were
added to `results/front_data.json` and two screens now render them. The one new derived number is
the price of a kilogram or a litre; the median, the quartiles and the extremes come out of
`aggregates.spread` and `aggregates.quartiles`, CALLED — this repository still holds exactly one
spelling of a median. `make check` is green at **4340 passed, 2 skipped**, run on the final tree.

Commits: `0761a70` (producer + config) · `a4f87d8` (screens + two Тренди fixes) · `e7e3ef6`
(the category block's window).

---

## What the operator asked, and what shipped

| asked | shipped |
|---|---|
| «Полтавська область» block on Позиції, dairy positions of Маркетопт / Сільпо / АТБ / ЕКО Маркет, as cards with SKUs, kept fresh by the loop | `front_data.json :: regions` + a block under the Позиції sources line. 47 cards: Маркетопт 7 (W36), АТБ 38 (W35), ЕКО Маркет 2 (W35), Сільпо — a sentence, not a zero |
| per category: how many positions, the cheapest, the dearest, the median | `front_data.json :: category_prices` + a `ChartCard` of cards on Тренди. 11 categories × unit = 13 groups this week |
| «make studying the statistics more convenient» | the tab no longer opens on an empty chart; bars carry chain names, not telegram handles |
| median leads, extremes carry evidence, no sanity corridor | the median is the card's figure; each end carries its leaflet page and its post link. **No threshold was introduced anywhere** |
| 11 categories as they are | keyed off `config/registry.yaml :: taxonomy.tracked_groups`; no new taxonomy |

---

## The numbers as rendered (not as planned)

Current week = every chain's own newest leaflet week, the flyer gallery's ruled definition
(`DESIGN-ship-1.md:87`). **311 positions of 1301; 8 of them carry no price per unit.**

| category | unit | rows | n | min | median | max |
|---|---|---:|---:|---:|---:|---:|
| ice-cream | ₴/kg | 99 | 95 | 106 | **299** | 2007 |
| cheese | ₴/kg | 67 | 62 | 253 | **390** | 4993 |
| yogurt | ₴/kg | 39 | 39 | 12 | **100** | 214 |
| curd | ₴/kg | 23 | 23 | 100 | **298** | 767 |
| dairy-desserts | ₴/kg | 18 | 18 | 113 | **161** | 278 |
| sour-cream | ₴/kg | 17 | 15 | 70 | **135** | 400 |
| butter | ₴/kg | 14 | 13 | 277 | **366** | 474 |
| milk | ₴/kg | 13 | 13 | 41 | **48** | 177 |
| dairy | ₴/kg · ₴/l | 13 | 6 · 7 | 134 · 54 | **200 · 380** | 504 · 570 |
| kefir-ryazhanka | ₴/kg | 6 | 6 | 46 | **55** | 71 |
| ice-cream | ₴/l | 99 | 4 | 94 | **106** | 210 |
| plant-based-analogs | ₴/l | 2 | 2 | 136 | **136** | 136 |

⚠️ **A number in the approved plan is stale and is not a regression.** The plan's check line quotes
medians 288 / 399 / 108. The screen reads 299 / 390 / 100. Two corrections happened between the
plan's prototype and the shipped block, both deliberate: the prototype POOLED grams and millilitres
(illegal under the unit-split rule the plan then adopted — ice cream 288 was 408 gram rows plus 7
millilitre rows in one median), and the window moved from all three windows to the current week.
Neither is a defect; a later reader comparing the two files should not file one.

---

## The three findings that shaped the design

**1. Five of eleven categories mix grams and millilitres.** ice-cream 408/7, yogurt 152/2, milk
46/10, dairy 27/10, plant-based 4/8. A single median per category would have added ₴/kg to ₴/L and
published the sum as a price. Every category is read per unit; no number sits over mixed units.

**2. Four rows are multipacks** (`item.pack_count`): Рудь 6×100 г за 88,90, Рудь 6×60 г за 94,90
(twice), Лацяти 10×10 мл за 25,99. There `size_value` is the piece and `promo_price` is the pack,
so the naive division reads six and ten times dear. The formula divides by `pack_count`.

**3. The current week cleans the extremes without a threshold.** Over all windows the cheapest
cheese was «Преміалле Моцарелла 180 г за 1,97» — 10,94 ₴/kg, a parse artefact. That row is on no
current leaflet: this week's minimum is 253,33 ₴/kg. The operator declined a sanity corridor and
did not need one.

---

## Provenance and the rules that bound the work

- **The app computes nothing.** `DESIGN-ship-1.md:3`. Every figure is a field; the only arithmetic
  in the frontend diff counts rows to choose a default brand.
- **One median.** `aggregates.spread()` (`aggregates.py:685`) returns `{n, min, median, max}` and
  its docstring forbids a second implementation. `quartiles()` (`:958`) supplies q1/q3. Verified
  safe to call from a new place: both are pure functions over a list, called today only from the
  depth block, and no test pins their call sites.
- **The byte pin was not touched.** `aggregates.promo_positions()` keeps its exact field set, so
  `tests/test_export_dashboard_data.py:108` (byte identity of `dashboard_data_w1.json`) and its
  field-set assertions cannot move. The new blocks are top-level keys of `front_data.json`, which
  nothing pins.
- **No old price, no arithmetic depth** anywhere in the new blocks — SPEC 3.17 (3) / 3.21 (4). The
  cards show the promo price and the printed badge.
- **Determinism**: two consecutive producer runs are byte-identical, and `make front` leaves
  `git status --porcelain results` empty.

### The region block is a selection of chains, not a geography

No source in `config/registry.yaml` carries a city, a region or an oblast —
`market_pulse.registry.Source` has no such field. `audience: regional` marks only the 17 Poltava
COMMUNITY channels, all `collect: false`. The one geographic signal near a retail chain is free
text inside a display name, «Маркетопт (Толока) м.Кременчук», which nothing parses.

So `config/chain_regions.yaml` records **whose stores the operator says serve the oblast** and its
header says what the block may not claim. The screen prints `region.claim` in the reader's
language: a selection of CHAINS, not a geography of rows; the leaflets of АТБ, Сільпо and ЕКО
Маркет are national issues.

⚠️ **Terminology collision for the team lead.** `docs/SPEC-v2-promo-pulse.md:45-52` already owns the
phrase «Полтавская область» — there it is stage 2 and the CONSUMER VOICE in open chats. This is a
cut across retail chains, a different object. Naming the difference is the point of this paragraph.

Two decisions inside that block, both the operator's word 12.09: the aggregator channels
`atb_aktsiyi` (154 rows) and `atb_fanatik` (95) are **not** in it — they republish АТБ's own
leaflet and would put one retailer in twice — and ice cream **stays**, because removing it would
leave ЕКО Маркет with zero cards (both its current-week positions are ice cream).

---

## Found, and deliberately NOT fixed

Each is outside the approved plan. Naming them is the report's job; fixing them is a ruling.

1. **`colourByIndex` colours a series by its position in the chart's handle list**
   (`frontend/src/tabs/Trends.tsx`, chart 1). A chain therefore changes colour when the brand
   filter changes — colour must follow the entity (`DESIGN-ship-1.md §3`). The `chains.by_channel`
   map shipped here is what a fix would read.
2. **Тренди overflows horizontally at phone width.** Measured at a 500 px viewport: 7 offending
   elements in `nav.tabs` (the fourteen tabs do not wrap) and 72 inside the two older charts.
   **Zero inside the new blocks** — the cards collapse to one column as designed.
3. **`quartiles()` can return q1 below min on a two-point group.** yogurt/мл, n=2: min 74, q1 73 —
   `statistics.quantiles` interpolating outside the sample. Inert today (no screen renders q1) but
   the field is in the export, and a later reader of it would draw a quartile under the minimum.
4. **`marketopt_promo` reaches the rollup through two handles** (`@marketopt_promo` and the private
   invite). They stay two series — merging them would be a sum across channels no file carries — so
   the label keeps the handle when one chain contributes two.

---

## Stop-points still open (team-lead files, which the executor may not edit)

1. **New §7 rows** in `docs/DESIGN-ship-1.md` for `category_prices` and `regions`, and possibly a
   line in `docs/PHASE-ship-1.md` §2. The tab←data map is a closed contract.
2. **The region rule and its honesty sentence** — approved by the operator, unruled by the team lead.
3. **The terminology collision** with SPEC-v2's stage-2 «Полтавская область».
4. **Tests.** `docs/PHASE-ship-1.md:35` allows one test per caught product defect and forbids the
   rest without authorisation, so **no new test file was written**. `scripts/export_front_data.py`
   has no Python test at all — including `refuse_on_a_missing_source()`, which this work added a
   source to. Asking for one file, `tests/test_export_front_data.py`, with the unit-price rule
   (the multipack both ways), the no-silent-zeros rule, and the missing-config refusal.

## Out of scope, named

The old price and the arithmetic depth (forbidden); folding АТБ's three chain ids into one retailer
(it would move accepted numbers); a per-week price series in the rollup; the command-centre tabs
T0–T8 (front-2). All work here was $0 and local.

## Verification

```
PYTHONPATH=src python3.11 scripts/export_front_data.py   # twice — byte-identical
make front                                               # 402 photos staged, manifest rewritten
cd frontend && npm run check && npm test                 # tsc clean · 21 tests
make check
```

`make check` tail — run twice, on `a4f87d8` and again on the final tree `e7e3ef6`:

```
4340 passed, 2 skipped in 712.84s (0:11:52)     # a4f87d8
4340 passed, 2 skipped in 691.08s (0:11:31)     # e7e3ef6, the tree as it stands
```

Screens verified in the browser at `localhost:8000` (served) and `localhost:8001` (static build):
Позиції and Тренди in both themes and both languages, and all six routes render with no
`SourceMissing` panel. The served-only guard still holds: `#/promo/quality` on the static build
answers with the refusal sentence, cold and on a hash-only transition.
