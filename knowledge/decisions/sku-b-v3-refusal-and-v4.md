---
type: decision
id: dec-2026-08-11-sku-b-v3-refusal-and-v4
date: 2026-08-11
status: accepted
tags: [decision]
---

# The v3 session was refused by its own gate: three marginals, a fresh ledger, and a $0.65 cap

**Context:** the resumed session SPEC 3.17 (11) authorised was opened on 2026-08-11 under
`results/sku_pilot_prereg_v3.json` and a $0.45 cap. It never reached a gold call. The (10)(a)
go/no-go — the gate that re-prices the whole run from the session's own warm-up before the first
gold call — projected **$0.5964** against **$0.45** and refused. The attempt was NOT consumed, no
element changed hands, and the session cost **$0.1526**: a 402.586 s boot, two warm-up calls and a
staging pod. This record is the long form of that acceptance and of SPEC 3.17 **(12)**, the
amendment it produced. **The home of every value below is the artifact named beside it**, never this
file: if the two disagree, the artifact is the contract.

## (1) The gate did what it was built to do

sku-b-run's acceptance ([[sku-b-run-acceptance-and-resume]]) found the go/no-go's arithmetic right
and its PROBE wrong: a generated 64×64 image answered in 1.436 s where a real leaflet page cost
5.0772 s, so the gate passed the run it exists to refuse. SPEC 3.17 (11)(c) fixed the probe — the
warm-up became a REAL unsent leaflet page and a REAL pre-filtered text row, both registered by hash
before the session.

The fixed probe answered in **14.808 s**, and the same gate refused. Nothing was re-run to get a
different number. `results/sku_b_positions_v3.json` is the whole output of the session:
`stopped_before_gold: true`, `population.asked: 0`, `dump.path: null`.

| reading | value | source |
|---|---|---|
| settled rate | $0.00030669/s | `results/srv2d_cost.json :: rate.usd_per_second` |
| boot | 402.586 s | `results/sku_b_positions_v3.json :: projection.boot_seconds` |
| page marginal, registered probe | 14.808 s | `… :: warmup.replies.positions_post_gm4.marginal_seconds` |
| text marginal, registered row | 3.862 s | `… :: warmup.replies.positions_text_gm4.marginal_seconds` |
| projected, 121 gold calls | $0.5964 | `… :: projection.go_no_go.projected_usd` |
| budget left of the $0.45 cap | $0.3248 | `… :: projection.go_no_go.budget_usd` |
| session cost, balance delta | $0.1416 | `… :: cost.usd` (a floor, Dv33) |

## (2) Three marginals, and none of them is the population's rate

| s/page | n | what the sample is | reading |
|---|---|---|---|
| 1.436 | 1 | a generated 64×64 thumbnail | garbage on the axis being measured; it is why (11)(c) exists |
| 5.0772 | 17 | the first pages of three ATB posts, one /run job | drawn from the gold population — but 10 of the 17 answered `[]`, and an empty answer decodes early |
| 14.808 | 1 | one page of the 51 the caption run never sent | structurally DEEP: the sent set is the first six pages of each leaflet, so the unsent pages are the dense grids |

The operator's reading, which is what (12)(a) is built on: **the probe is structurally pessimistic
and the drawn marginal is structurally optimistic.** Neither is wrong; they measure different kinds
of page. The break-even at the $0.45 cap was 9.5622 s/page — between the two — so the refusal was
not a rounding question, and neither is a cap that has to admit the pessimistic corner.

## (3) The rulings (SPEC 3.17 (12), operator, 2026-08-11)

**(a) One more session, cap $0.65.** Sized to admit the gate's own pessimistic projection of
~$0.60, whose probe prices above the first-six-page population's drawn marginal. A cap that only
fits the optimistic corner is a cap that refuses on the day. The in-run gate of (10)(b) still
protects the middle: this is not a licence to run at the pessimistic corner and hope.

**(b) A refusal charges the PHASE, never the next attempt's cap.** Each registered attempt runs
under its own fresh anchor with its cap, ledger and phase constants set TOGETHER. This is the Dv167
finding, and it was not academic: `RESUME_CAP_USD`, `RESUME_LEDGER` and `RESUME_PHASE` were three
module constants with nothing binding them, and `read_ledger` returns the existing anchor whenever
its key is present. A second `--resume` under the old three would have got $0.45 − $0.1526 =
**$0.2974**, below even the optimistic $0.3248 — refusing on the refused session's boot rather than
on any price, with no flag anywhere saying that had been decided.

**(c) The warm-up inputs are not re-picked.** The same unsent page (`atb_market_official_4476.jpg`)
and the same non-pack row (`@silposilpo:3370`), re-verified by hash. A probe re-drawn after it
produced an inconvenient number is a probe chosen for its answer.

**(d) Everything else of (10) and (11) applies unchanged.** The population is still the 121 unbought
elements; each of the 138 is bought exactly once across the program.

## (4) The cap arithmetic

`results/sku_projection_v4.json`, registered beside v3's. Both marginals as corners, the 3% drift a
contract term rather than a measurement, and the pessimistic corner asserted equal to the gate's own
$0.5964 when the record is built — same marginals, same population, so a disagreement would mean the
projection's arithmetic is not the arithmetic that spent.

| corner | s/page | total | with 3% drift | headroom | fits |
|---|---|---|---|---|---|
| the registered probe, a deep unsent page | 14.808 (n=1) | $0.5964 | $0.6143 | $0.0357 | yes |
| the population's drawn marginal | 5.0772 (n=17) | $0.3218 | $0.3315 | $0.3185 | yes |

Fixed in both: boot 402.586 s ($0.1235), idle tail 60 s ($0.0184), text leg 30 × 3.862 s (n=1 — the
first positions call ever made on text). The decision is an inequality: at this boot the page
marginal would have to reach **16.04 s/call — 1.08× the probe's own 14.808** — before $0.65 is
exhausted with the drift on. That margin is real and it is thin, which is what the in-run gate is
for.

## (5) What the pilot has cost, and what it was quoted at

$0.1965 (sku-b-run) + $0.1526 (v3, refused) + ≤$0.65 (v4) ≈ **≤$1.00** against SPEC 3.17 (6)'s
original $0.35. The overrun is entirely the price of honest gates: the first session's cap held and
its probe did not, the second session's probe held and its cap did not, and neither ever bought an
element twice. Phase 4 stands at ≈$22.95 of $25.

## (6) What this does not decide

* **No bar is scored.** v3 measured nothing a bar can read. Bar 1 and bar 3 are computed by
  `scripts/sku_bar_verdicts.py` over the MERGED population once v4 completes; bar 2 is the team
  lead's read of the merged dump at acceptance.
* **The boot is not fixed.** 402.586 s is 2.19× vis-c's 183.58 s on the same base; 112 s of it is a
  cold read of 1188 shards off the network volume and 267.6 s is unattributed for want of timestamps
  (`docs/reports/sku-b-v3-run.md` §2). Shard consolidation is the lever and it is deferred to 5c.
* **The two prompt findings stay post-pilot.** The kopeck superscript and the asterisk qualifier are
  a NAMED revision registered beside the frozen prompts, never an edit inside the measurement.

**Artifacts:** `docs/SPEC.md` 3.17 (12) · `results/sku_pilot_prereg_v4.json` ·
`results/sku_projection_v4.json` · `results/sku_b_positions_v3.json` ·
`docs/reports/sku-b-v3-run.md` · `docs/reports/sku-b-v4-prep.md` ·
[[sku-b-run-acceptance-and-resume]] · [[sku-b-serving-and-cap-discipline]] ·
[[sku-b-pilot-readings-ratified]]
