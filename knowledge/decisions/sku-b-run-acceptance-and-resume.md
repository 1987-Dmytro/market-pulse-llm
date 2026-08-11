---
type: decision
id: dec-2026-08-11-sku-b-run-acceptance-and-resume
date: 2026-08-11
status: accepted
tags: [decision]
---

# sku-b-run accepted at 17 of 138: the probe priced the run, not the cap, and the (10)(b) stop resolves as a resume

**Context:** the single paid session SPEC 3.17 (6) bought was run on 2026-08-11 and stopped by its
own cap gate after 17 of 138 gold calls, having spent **$0.1965**. Nothing about that number is a
surprise in the direction people expect: the cap was adequate, the arithmetic was right, and the
gate that should have refused the run before it started did not refuse it. This record is the long
form of the acceptance and of SPEC 3.17 **(11)**, the amendment it produced. **The home of every
value below is the artifact named beside it**, never this file: if the two disagree, the artifact
is the contract.

## (1) What was bought, and what stopped it

`results/sku_b_positions.json` is the session's whole output. 17 leaflet pages of the registered
108 were asked, in one job; 14 positions came back, 13 of them carrying a crossed-out price; one
reply was refused by the strict parser (`printed discount '-50%*' is not a percentage`), 10 pages
answered `[]`, and the text leg never opened.

The stop is SPEC 3.17 **(10)(b)** — the in-run projection gate, firing between jobs:

| reading | value | source |
|---|---|---|
| settled rate | $0.00030669/s | `results/srv2d_cost.json :: rate.usd_per_second` |
| boot | 391.369 s = $0.1200 | `results/sku_b_positions.json :: projection.boot_seconds` |
| warm-up marginals | 1.436 s (page) · 0.756 s (text) | `… :: warmup.replies` |
| go/no-go projection | **$0.1936** against $0.3403 → proceed | `… :: projection.go_no_go` |
| measured page marginal | **5.0772 s/call**, n=17 | `… :: projection.per_gate[0]` |
| in-run projection | **$0.3540** against $0.3403 → STOP | `… :: projection.per_gate[0].projected_usd` |

Three cost readings were kept apart and none of them collapsed into the others: **$0.0943** the
balance delta at the moment the record was written, **$0.1472** the billed seconds the gate acted
on, **$0.1965** the anchor delta re-read after settlement. The first is a floor by construction
(Dv33) and the last is the one the ledger carries.

## (2) The finding: the probe, not the cap and not the instrument

The go/no-go of 3.17 (10)(a) exists to refuse a run that cannot be finished — "never buy half a
pilot" — and it passed this one. Everything inside it was correct. The boot landed on the `info`
handshake and not on either warm-up call, so `billed_seconds` was right; the idle tail was in the
arithmetic; the multiplication was right.

**The INPUT was wrong.** The warm-up sent a generated 64×64 image. It answered in 1.436 s. A real
ATB leaflet page cost **5.0772 s — 3.54×**. The gate sees seconds, and both numbers are seconds:
nothing inside it could tell that a thumbnail and a 7 MB leaflet page are the same op on different
work. A warm-up chosen to be cheap and non-gold was chosen along an axis that has nothing to do
with cost.

That is the whole finding, and it is about the **instrument's probe**, not about the cap (which the
resumed session fits at every corner) and not about the extraction (no bar was scored). It is
recorded as a durable lesson as well as a law.

**What was NOT the finding, and is still open:** the 391.369 s boot is **2.13×** vis-c's 183.58 s on
the same base (`results/captions_gm4_visc.json`). Nothing in this repository explains it. The
session's `worker-boot.log` is on volume `qw4nwleanc` and a staging pod can read it for near-free.

## (3) The team lead's calibration read — 13 pairs, 6 correct, NON-GATING

The 17-page prefix produced 13 price pairs and the team lead read them against the page images.
**6 of 13 correct**, and the error is one-sided:

* promo price **13/13** correct; printed discount percentage **13/13**; brands read excellently;
* every miss is the **crossed-out old price**, and every miss is the **kopeck superscript**:
  264⁹⁰ → 264.5, 39⁹⁰ → 39.99, 71⁵⁰ → 71.9, 19⁹⁰ → 19.99, 44⁴⁰ → 44.9, 42⁹⁰ → 42.5;
* plus a duplicate «Каштан 75 г» and one promo-without-old row where two products share a price tag.

This read **gates nothing** (SPEC 3.17 (11)(e)). Bar 2 is registered over the pairs of the COMPLETED
population and 13 pairs from a 17-page prefix of one layout family is not that sample. It is
recorded because it is the strongest available signal about what the resumed session will measure:
if the remaining 91 pages behave the same way, bar 2 (≥ 0.80) fails and B closes **by measurement**,
which is exactly what the pre-registration says should happen.

## (4) The ruling: RESUME, and the four things it fixes — SPEC 3.17 (11)

The operator's decision was to **finish the measurement** rather than to rule on it. B is decided by
measurement, not by inference from n=13.

**(a) Each element is bought EXACTLY ONCE across the program.** The resumed session buys only the
121 recorded as unbought; the 17 existing answers — the parse refusal included — enter the bars as
they stand and are never re-asked. Pinned in `results/sku_pilot_prereg_v3.json ::
resume.bought_already`, enforced by four refusals in `scripts/positions_gm4_skub.py --resume`.

**(b) The instrument is FROZEN as registered.** Prompts, parser and serving pin unchanged. The
superscript and asterisk findings of (3) are a **post-pilot named revision** — applying them
mid-pilot would make the 17 bought answers and the 121 resumed ones two different instruments under
one set of bars. (The two-stage-OCR idea recorded on 10.08 now has its evidence and is where that
revision would start.)

**(c) The warm-up becomes REPRESENTATIVE.** One real UNSENT leaflet page (of the 51 outside R2's
gold) and one real pre-filtered text row outside the 30-row pack. Both are picked once by the
producer, **registered by sha**, and re-verified by the driver against the bytes — a rule the paid
run re-derives could disagree with the one that was registered, and the disagreement would land on
the go/no-go's input.

**(d) The resumed cap is $0.45**, priced from the measured marginals; every reading of (10) applies
unchanged against it. `results/sku_projection_v3.json` puts the resumed session at **$0.3300** at
its worst corner, and states the decision as an inequality: the measured page marginal would have
to reach **8.26 s/call (1.63×)** before the cap is exhausted.

**(e) The calibration read of (3) is non-gating**, per above.

## (5) Consequences already landed

* `results/sku_pilot_prereg_v3.json` — registered BESIDE v2, exactly four moves, every bar and
  reading byte-equal, asserted leaf by leaf.
* `scripts/positions_gm4_skub.py --resume` — the narrowed population, the four refusals, the merged
  bar input where every row names the session that bought it, its own anchor and its own cap.
* `scripts/runpod_guard.py` — hyphen ≡ underscore for step ledgers. `--step sku-b` had created a
  SECOND anchor beside the driver's own, holding a post-spend balance and a `step_spent_usd` of 0.0
  (Dv151). Caught and deleted while untracked; now impossible.
* `cost.jobs` split into `jobs_planned` / `jobs_submitted` (Dv153): the interrupted run recorded 8
  where 4 jobs ran, because the field was the packing PLAN.

Related: [[sku-b-serving-and-cap-discipline]], [[sku-b-pilot-readings-ratified]].
