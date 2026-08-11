---
type: decision
id: dec-2026-08-10-sku-b-pilot-readings-ratified
date: 2026-08-10
status: accepted
tags: [decision]
---

# sku-b's five readings are ratified, the text gold is adjudicated, and bar 3's denominator is all 30 rows

**Context:** the three sku-b bars are quoted verbatim out of SPEC amendment 3.17 (6), but a bar is a
ratio and SPEC states no denominator for any of them. `results/sku_pilot_prereg.json`
(`b1bfa40d1f5073ec…`) therefore registered five readings as **the executor's**, in a
`ratification_required` block, before the pilot exists — sku-b is ONE paid attempt with a $0.35 cap
and a failed bar closes B "by measurement", so a denominator nobody agreed to is the paid session
spent against a void. The operator ratified all five on 2026-08-10 after a quiz. This record is the
English long form; **the home of the readings is the pre-registration itself**, and the text below is
read out of that file, not out of a chat transcript. SPEC 3.17 (7) carries the same ratification as
law since 2026-08-11 — as a marker-wrapped block, because the prereg pins SPEC byte-for-byte and the
registered law is the stripped text.

## (1) The five readings, as registered

| id | bar | the registered reading | if it had been refused |
|---|---|---|---|
| **R1** | leaflet_brand_recall | "the bar says 'per page' and the gold is per POST. Registered reading: recall per post over the union of its page answers, macro-averaged over the 15 posts with a non-empty gold set" | "per-page gold does not exist and building it is a new adjudication. sku-b must NOT run until this line is ratified" |
| **R2** | leaflet_brand_recall | "the page set is the 108 pages the caption run SENT, not the 159 available. For 15 of 19 posts that is the first six pages of a longer leaflet" | "reading all 159 pages means brands with no gold behind them, which would score as false positives for being correct" |
| **R3** | leaflet_brand_recall | "the 4 posts with an empty gold set are out of the recall average: `@atb_market_official:4370`, `:4415`, `:4455`, `:4519`" | "recall is undefined there; the alternative is a bar that fails by arithmetic" |
| **R4** | price_pair_accuracy | "n >= 10 pairs to score the bar; 1..9 reports and does not score; 0 is NOT_REACHABLE" | "the team lead sets another n, in writing, before the run" |
| **R5** | text_tier_accuracy | "unreadable replies are excluded and counted (>10% blocks the bar); n >= 20 adjudicated rows to score; both carriers pooled as drawn" | "a stratified redraw is a different pack and this one is already built" |

Two consequences worth stating separately, because they are the parts a later reader will reach for:

* **R1 does not widen the bar.** The macro mean over the 15 scoreable posts is what gates. The micro
  reading over all 55 pairs is *reported beside it and gates nothing*, and precision on the same 15
  posts is reported and never gated — the gold is one reviewer's reading in the REVIEW class of SPEC
  3.16 (1), so a brand the pilot finds and the reviewer did not is not evidence of a false positive.
* **R3's four posts are not discarded, they change job.** They are the precision probe: every brand
  extracted on their pages is a false positive and is reported with its page.

**Thresholds (0.75 / 0.80 / 0.85), the $0.35 cap and the one-attempt clause never moved.** The
ratification touches denominators and reachability only.

## (2) The text gold: 30 rows, adjudicated 2026-08-10

`data/annotation/sku_a_text/text30.csv`, ~25 minutes of operator time, every row touched.
`PYTHONPATH=src python3 scripts/validate_sku_text_pack.py` reports 30 rows / 30 touched, zero
defects, the ladder `b497c07200db7413…` equal to the manifest's (`results/sku_text_pack_manifest.json`,
`2b941243274febde…`), and the given columns hashing to what the pack was built against.

**Composition, from the ticks through `positions.tier_from_presence`:**

| tier | rows | what it prices |
|---|---|---|
| `position` | 11 | the top rung — brand + category + ≥1 differentiating attribute |
| `product_mention` | 3 | brand + product, no attributes |
| `brand_mention` | 0 | the rung the draw did not reach |
| `none` | 16 | **12** rows carry ticks but no brand (no rung starts below one) and **4** are all-empty |

The 4 all-empty rows are the pre-filter's direct false positives and each names a different way the
conjunction fires without an offer behind it: `@VARUS_channel:7440` (a bonus complaint),
`@VARUS_channel:8297` (a giveaway), `@VARUS_channel:1775` (delivery), `@silposilpo:2529` (a biscuit).
Carriers as drawn: 26 `post_text`, 4 `comment`.

### Two rows the team-lead triage raised, and how the operator ruled

* **`@VARUS_channel:1912` → category, not line.** The post lists «Сметана 15% ТМ Харківська» among
  four unrelated items. The operator ticked brand + category + fat and wrote in the file: *«триаж
  10.08: категория (сметана), не линейка»*. Tier `position`. The distinction is the one SPEC 3.17 (2)
  makes: `line` is the producer's named product line, and «сметана» is the category the item sits in.
* **`@silposilpo:2529` → all-empty, out of taxonomy.** The discounted item is бісквіт «Барні» with a
  milk filling; the operator left every cell blank and wrote: *«пусто: бісквіт вне таксономии,
  «молочна начинка» — свойство (триаж 10.08)»*. A milk filling is a property of a biscuit, not a
  dairy position. Tier `none`, and one of the four all-empty rows above.

## (3) The registered bar-3 denominator is ALL 30 adjudicated legal rows

The pre-registration says the denominator is "the adjudicated rows that came back with a legal tick
set. A row the operator left untouched is not gold and is not counted." All 30 came back and all 30
are legal, so **the denominator is 30.**

**Gold `none` is a value, not a missing answer.** The prereg's own `comparison` clause: "a row whose
ticks are all empty has gold `none` — the model must return `[]` to agree with it." So the 16 `none`
rows price the **refusal discipline** and the 14 rung-carrying rows price **tiering**, and the bar
distinguishes both ways of failing: a model that answers `[]` to everything scores 16/30 = 0.53 and a
model that names a position everywhere scores 14/30 = 0.47 — both well under 0.85.

**A narrowing of the denominator to 14 is REFUSED** (team-lead ruling, 2026-08-11). It was proposed as
"the rows that have a tier to get right"; it is a post-hoc change of a registered bar, it deletes the
half of the sample that prices refusal, and it would raise the measured accuracy by construction. The
denominator is what the pre-registration says it is.

Unreadable replies remain outside the denominator under R5: counted by reason, listed by id, never
scored as `none`, and above 10% of the adjudicated set the bar is NOT_SCORED — the instrument did not
answer, which is a different finding from a wrong answer.

## (4) The caption quiz corroborates the audit rather than adding a measurement

On 2026-08-10 the operator compared five ATB posts (page 1 + the GM4 caption + the gold brands) at
$0: **«не совпадає» — 4381, 4401; «частково» — 4360, 4377; 4436 — no verdict.** Method caveat stated
at the time: the judgment is on page 1 of 4–6, while the caption was written over the whole album.

That reading sits inside what the Opus audit already recorded for the same channel.
`results/opus_audit_5c1.json` (`608560ded8e389fb…`), `caption_candidates.by_channel`:

```
"@atb_market_official": {"judged": 19, "faithful": 9, "partial": 10, "wrong": 0,
                         "faithful_rate_candidate": 0.4737}
```

Nine faithful, ten partial, zero wrong — the same shape as 2 bad / 2 partial / 1 undecided on a
five-post look, and the same story: the captioner is not lying, it is **sampling**. The audit's
`brands_visible_missed` names four of the five quiz posts directly: `:4401` misses eight watchlist
brands at once (`svoia-liniia`, `ferma`, `rud`, `try-vedmedi`, `selianske`, `molokija`, `zlahoda`,
`halychyna`), `:4360` misses `svoia-liniia` and `limo`, `:4436` misses `svoia-liniia`, `:4381` misses
`lasunka`. **Nothing here is a gate number** — 3.16 (1) puts the whole review class outside the gates,
and bar 1's gold is pinned and did not move. It is the motivation for the position layer: a ~230-
character caption is a sample of a leaflet page carrying dozens of products, so sku-b measures a NEW
per-page instrument at recall 0.75, and captions stay in the loop for themes and coverage, never for
brands. See [[opus-review-programme-close]] and [[sitting-2026-08-10-composition-signed]].

## (5) The alternative that is deferred, not rejected

A two-stage reading of leaflets — OCR transcript first, SKU extraction from the text second — is the
operator's 2026-08-10 proposal and is recorded under "Отложено СОЗНАТЕЛЬНО" in `docs/STATUS.md`: it
buys a checkable transcript artefact and cheap stage-2 re-runs, and it costs the spatial link between
a price and the product it is printed beside. The decision is **after** the sku-b pilot and is read
off its dump; the pre-registration does not change either way.

## What this record does not do

It registers nothing new. Every reading above already exists in `results/sku_pilot_prereg.json`, and
nothing in this file may be cited in place of it — if the two ever disagree, the pre-registration is
the contract. The 5c3 named revision («Варто» text matching off, «Селянське» anchored) is **not**
applied in sku-b, and the 141 open-extraction names stay outside the watchlist, resolving to `raw:`
keys symmetrically on both sides of bar 1. See [[sitting-2026-08-10-composition-signed]].
