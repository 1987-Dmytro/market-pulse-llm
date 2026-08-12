---
type: decision
id: dec-2026-08-12-sku-b-pilot-closed-by-measurement
date: 2026-08-12
status: accepted
tags: [decision]
---

# The sku-b pilot closes as "instrument not ready" BY MEASUREMENT: two bars of three failed

**Context:** SPEC 3.17 (6) registered three bars for the position instrument and
`results/sku_pilot_prereg_v4.json :: attempts.on_failure` registered what a failure does, before any
of them could be read: *"a failed bar closes B as 'instrument not ready' BY MEASUREMENT. No retry,
no re-prompt, no second draw: a bar re-run after its own result is not the bar that was
registered."* The population completed on 2026-08-12 (138 of 138 elements, `sku-b-v4`), bars 1 and 3
were computed the same day, and the team lead's bar-2 read landed in `docs/PROMPT-sku-b-close.md`.
Two bars failed. This record is the long form of the closure. **The home of every value below is the
artifact named beside it**, never this file: if the two disagree, the artifact is the contract.

## (1) The three bars

`results/sku_bar_verdicts.json`, over the merged population of 138 sources and its 79-row dump.

| bar | registered | value | verdict | n |
|---|---:|---:|---|---|
| 1 — leaflet brand recall | ≥ 0.75 | **0.3603** | **FAIL** | macro over the 15 posts with gold (R1/R2/R3) |
| 2 — price-pair accuracy | ≥ 0.80 | **0.3279** | **FAIL** | 20 of 61 pairs, read by the team lead 2026-08-12 |
| 3 — text tier accuracy | ≥ 0.85 | **0.8621** | **PASS** | 29 of 30 rows, 1 unreadable (3.3% < 10%, R5) |

Bars 1 and 3 are `market_pulse.scorer`'s; bar 2 is the team lead's read of all 61 pairs against all
22 page images (SPEC §10 — the executor never scores its own sample), transcribed row for row by
`scripts/apply_sku_pair_verdicts.py` into `results/sku_b_pair_verdicts.json` and re-derived from
that file's own keys by the bar producer. The closure block in the verdict record quotes
`attempts.on_failure` out of the registration and names the failed bars from the computed verdicts —
the registered sentence says "a failed bar" in the singular and the pilot failed two.

**State: CLOSED — instrument not ready, BY MEASUREMENT.** No retry, no re-prompt, no second draw.

## (2) The diagnosis: big text perfect, small struck-through text at a third

The team lead's line, carried verbatim into `results/sku_b_pair_verdicts.json :: diagnosis` and
repeated here because it is the finding:

> promo price 61/61 correct · printed % 61/61 correct · crossed-out old price 20/61 — every error is
> confined to the small struck-through number (superscript kopiyky garbled, truncated to .0, or
> digit-shifted), and depth() is wrong wherever the old price is.

Three numbers on one price box, read by one model in one call, and the two large ones are perfect
while the small struck-through one is right a third of the time. That is not a comprehension failure
and it is not a prompt failure — it is a resolution failure on a specific glyph class, and it is the
single most actionable thing the pilot produced.

## (3) Under-reading, never invention — on all three bars

The instrument's errors point one way, and this is what separates "not ready" from "unusable":

* **bar 1** — micro **0.4727 = 26/55**, precision **0.9286 = 26/28**. Of the 28 (post, brand-key)
  pairs it named on a scoreable post, **two** were not in the gold (`raw:three bears` on `…:4340`,
  `raw:komo` on `…:4381`) against **29 gold pairs it never named**.
* **the precision probe (R3)** — on the four posts whose gold set is empty, the model extracted
  **zero** brands. It did not invent a dairy brand on a page of summer non-food.
* **bar 3** — every one of the 4 misses is downward: `position → none` ×1 and
  `product_mention → none` ×3, no row ever placed higher than the operator's ticks.
* **bar 2** — the errors are transcription-scale, not fabrication: see (5).

A model that under-reads can be pushed; a model that invents cannot be trusted at any recall. The
pilot says this one under-reads.

## (4) Bar 1's gold and bar 1's instrument are not defined over the same object

The gold is `results/sku_reference_leaflet.json :: brands_visible` — every dairy brand one reviewer
could SEE across the pages sent for a post (55 pairs over 15 posts: 34 from the watchlist, 21
outside). The instrument returns POSITIONS: all **62** page rows in the dump carry tier `position`,
i.e. a brand with a category and a differentiating attribute. A brand printed on a page without a
priced item beside it is visible and is not a position, and nothing in the pilot asked the model for
it.

This is a candidate explanation with one fact under it (62 of 62 page rows are `position`), **not a
measured cause**: the pilot never counted how many of the 29 unnamed gold pairs sit on unpriced
items. Which is precisely why (7) names a `brands_visible` side-channel — so the bar and the
instrument would measure one thing and the number would mean what it says.

## (5) Depth-from-percent: the badge is adequate, and so is the old price we already extract

`results/sku_depth_from_pct.json`, measured on the 61 bought pairs at $0, against the team lead's own
`printed_old`:

| instrument | median \|Δ\| | max \|Δ\| | ≤ 1 pp | ≤ 2 pp |
|---|---:|---:|---:|---:|
| the printed `-N%` badge | **0.2886 pp** | **1.4171 pp** | 60/61 | **61/61** |
| the extracted old price | **0.1761 pp** | **1.6366 pp** | 56/61 | **61/61** |

Bar 2's 20/61 is a verdict on the printed NUMBER. Depth is not that number: every dictated error is
kopiyky-scale (230.0 where the page prints 230.90), and a 0.4% error on the old price moves depth by
under 2 pp on every pair in the population. So the pilot's tempting reading — "take depth from the
badge and stop extracting the old price" — is only half true: the badge is adequate for a weekly
median, and **the old price already is too**. Dropping it would buy no accuracy.

The adequacy rule (every pair within 2 pp, median within 1 pp) is stated inside that record as the
measuring script's own and is **not registered**. No threshold was pre-registered for this and the
real one is the operator's to set at the B′ design session.

## (6) What the programme cost, and what each stop bought

Three sessions, settled balance deltas: **$0.1965 + $0.1526 + $0.2541 = $0.6032** (Phase 4 stands at
**$23.3209 of $25.00**). `docs/PROMPT-sku-b-close.md` says "$0.62"; the three ledgers sum to
$0.6032 and each is a settled balance delta, itself a floor (Dv33).

| session | cost | cap | what it bought |
|---|---:|---:|---|
| `sku-b` | $0.1965 | $0.35 | 17 of 138 calls, stopped by its own (10)(b) cap gate — and the finding that the go/no-go's PROBE was wrong: a generated 64×64 image answered in **1.436 s** where a real leaflet page cost **5.0772 s**. Produced SPEC 3.17 (11): the resume, and a probe that is a REAL unsent page |
| `sku-b-v3` | $0.1526 | $0.45 | nothing bought and nothing consumed: refused by (10)(a) before the first gold call, 121 calls projected $0.5964 against $0.45. The fixed probe answered in **14.808 s** — a THIRD marginal, and none of the three was the population's. Produced SPEC 3.17 (12): the $0.65 cap sized to the pessimistic corner, on a fresh anchor |
| `sku-b-v4` | $0.2541 | $0.65 | the 121, the completed population, and all three bars readable |

**The probe lesson, in four numbers: 1.436 → 5.0772 → 14.808/14.625 → 4.0161 s per page.** The
registered (11)(c) probe reproduced across sessions to **1.2%** (14.808 in v3, 14.625 in v4) and
still over-priced the completed page leg (**4.0161 s/page over n=91**) by **3.64×** — because its own
selection rule ("one real UNSENT page") makes it a dense back-of-the-leaflet grid by construction,
the sent set being the first six pages of each leaflet. A stable instrument is not a representative
one. Price the next registration from n=91, not from the probe.

## (7) What comes next — CANDIDATES, not commitments

The revision decision is the operator's at the 5c2 briefing. Nothing below is authorised by this
record, and no prompt, parser or serving pin moved in the pilot or in this closure.

1. **A two-stage read** — OCR transcript first, SKU extraction from the text second. The operator's
   2026-08-10 proposal, deferred at [[sku-b-pilot-readings-ratified]] §5 pending exactly this
   evidence. (2) is that evidence: the failure is glyph resolution on a struck-through superscript,
   which is a transcription problem before it is an extraction problem. It costs the spatial link
   between a price and the product printed beside it.
2. **A `brands_visible` side-channel** — ask the model for the brands it can see on the page, beside
   the positions it can build. It makes bar 1's gold and bar 1's instrument the same object (4), and
   it is measurable against the existing gold at no new labelling cost.
3. **The superscript/asterisk parser family** — the kopeck superscript and the `-50%*` asterisk
   qualifier, both named as post-pilot revisions at [[sku-b-run-acceptance-and-resume]] (b) and both
   present in the v4 population's five unreadable replies. Registered beside the frozen prompts, on
   purpose, so applying them could never make the 17 and the 121 two different instruments.

## (8) What this record does NOT decide

* **It does not reopen a bar.** `attempts.on_failure` forbids a retry, a re-prompt and a second
  draw, and the closure is taken on the bars as read.
* **It does not fund B′.** No session, no cap and no registration is authorised here.
* **It does not rule on the badge.** (5) is a measurement with a stated-not-registered rule; the
  threshold that decides whether question 7 needs the old price is the operator's.
* **Bar 3's PASS is not an endorsement of the text leg.** 29 rows over a 0.85 bar move 3.4 pp per
  row, and R5's reachability floor of 20 was cleared by 9.

**Artifacts:** `results/sku_bar_verdicts.json` · `results/sku_b_pair_verdicts.json` ·
`results/sku_depth_from_pct.json` · `results/sku_pilot_prereg_v4.json` ·
`results/sku_b_positions_v4.json` + `.jsonl` · `docs/PROMPT-sku-b-close.md` ·
`docs/reports/sku-b-v4-run.md` · [[sku-b-v3-refusal-and-v4]] ·
[[sku-b-run-acceptance-and-resume]] · [[sku-b-pilot-readings-ratified]] ·
[[sku-b-serving-and-cap-discipline]]
