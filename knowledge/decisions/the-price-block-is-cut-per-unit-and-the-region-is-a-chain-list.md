---
type: decision
date: 2026-09-12
status: accepted by the operator; the team lead's ruling on §7 and on the region rule is OPEN
authority: operator's own decisions of 12.09, taken on the plan
  `docs/plans/` → `~/.claude/plans/zany-drifting-dragon.md`, before any code was written
tags: [decision, front, prices, region, poltava]
---

# The price block is cut per UNIT, and the region block is a list of CHAINS

## What was decided

Five rules, all the operator's, all taken before implementation:

1. **A category is read per unit, never pooled.** `₴/kg` over the gram rows and `₴/L` over the
   millilitre rows, each with its own `n`. Five of the eleven tracked categories mix the two
   (ice-cream 408/7, yogurt 152/2, milk 46/10, dairy 27/10, plant-based 4/8), so one median per
   category would have added two different kinds and published the sum as a price.
2. **The median leads; the extremes carry proof.** The card's figure is the median; the cheapest
   and the dearest rows each carry the leaflet page they were read off and a link to the post.
   **No sanity corridor** — the operator refused thresholds, and none was introduced anywhere.
3. **The window is the current week** — every chain's own newest leaflet week, the rule that
   already feeds the flyer gallery (`docs/DESIGN-ship-1.md:87`), not a second definition. It is
   what removed the parse artefacts a corridor would have been for: cheese's cheapest went from
   10.94 ₴/kg («Преміалле Моцарелла 180 г за 1,97», on no current leaflet) to 253.33 ₴/kg.
4. **Eleven categories as they are** — keyed off `config/registry.yaml :: taxonomy.tracked_groups`.
   No new grouping, no «all dairy» row.
5. **Полтавська область is a SELECTION OF CHAINS, not a geography of rows.** No source in the
   registry carries a city, a region or an oblast — `market_pulse.registry.Source` has no such
   field — and the leaflets of АТБ, Сільпо and ЕКО Маркет are national issues. The operator's list
   lives in `config/chain_regions.yaml`; the screen prints the sentence that says what the block
   may not claim (`region.claim`). Inside it: the aggregator channels `atb_aktsiyi` (154 rows) and
   `atb_fanatik` (95) are **excluded** — they republish АТБ's own leaflet and would put one
   retailer in twice — and **ice cream stays**, because removing it would leave ЕКО Маркет with
   zero cards.

## Why

The marketing director's question is «what does a kilogram cost in this category this week», and
every previous surface answered a different one (depth, SKU counts, positions with a price). The
one derived number this adds is the price of a kilogram or a litre; the median, the quartiles and
the extremes come out of `aggregates.spread()` and `aggregates.quartiles()` **called**, so the
repository still holds exactly one spelling of a median and the app still computes no figure
([[a-published-number-has-one-reader]], `docs/DESIGN-ship-1.md:3`).

Rule 1 is a correctness rule, not a threshold: it introduces no number and needs no ruling. Rule 3
is the same shape — a better-defined population rather than a guard over values, which is why the
absurd extremes left without anyone choosing a cut-off.

Multipacks are the second trap in the same formula: `promo_price` is the pack and `size_value` the
piece, so four rows (Рудь 6×100 г, Рудь 6×60 г twice, Лацяти 10×10 мл) read 6× and 10× dear unless
the division carries `pack_count`.

## What it is NOT

It is **not** stage 2's «Полтавская область» of `docs/SPEC-v2-promo-pulse.md:45-52`, which is the
CONSUMER VOICE in open chats ([[poltava-chats-carry-category-voice-not-brand-voice]]). Same words,
different object — the collision is named here so a ruling does not read one as the other.

## Evidence as it renders

Current week: 311 rows of 1301, 8 without a unit price, 13 category×unit groups. Ice-cream 299 ₴/kg
(n=95) · cheese 390 (n=62) · yogurt 100 (n=39) · curd 298 (n=23) · dairy-desserts 161 (n=18) ·
sour-cream 135 (n=15) · butter 366 (n=13) · milk 48 (n=13) · dairy 200 ₴/kg and 380 ₴/L ·
kefir-ryazhanka 55 (n=6) · ice-cream 106 ₴/L (n=4) · plant-based 136 ₴/L (n=2). The region block:
47 cards — Маркетопт 7 (W36, 01.09–04.09), АТБ 38 (W35, 25.08–26.08), ЕКО Маркет 2 (W35, 24.08),
Сільпо `absent: no_pages`, a sentence rather than a zero.

Built at `0761a70` · `a4f87d8` · `e7e3ef6`, reported in `docs/reports/prices-and-region.md`,
`make check` **4340 passed / 2 skipped** run twice. Related lessons:
[[a_category_that_mixes_units_has_no_single_median]], [[the_right_population_beats_the_right_guard]].

## Open — the team lead's, not the executor's

New §7 rows in `docs/DESIGN-ship-1.md` for `category_prices` and `regions`; a ruling on the region
rule and its honesty sentence; the terminology collision above; and authorisation for one test file
`tests/test_export_front_data.py` (`docs/PHASE-ship-1.md:35` forbids the rest without it).
