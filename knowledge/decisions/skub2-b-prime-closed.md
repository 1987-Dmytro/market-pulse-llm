---
type: decision
id: dec-2026-08-12-skub2-b-prime-closed
date: 2026-08-12
status: accepted
tags: [decision]
---

# B′ closes as "instrument not ready" BY MEASUREMENT: two bars pass, and the one that fails is the same glyph it always was

**Context:** the sku-b pilot closed on 2026-08-12 with two bars of three failed
([[sku-b-pilot-closed-by-measurement]]). SPEC 3.17 (13)(d) granted exactly one re-measurement:
instrument v2 — a parser family for three refusal classes, a 1200-token ceiling, three Latin display
aliases — over the same 138 elements, under a B′ registration written beside v4's and never over it.
`results/sku_pilot_prereg_b2.json :: attempts.on_failure` registered the consequence before any of it
could be read: *"a failed bar closes B as 'instrument not ready' BY MEASUREMENT. No retry, no
re-prompt, no second draw: a bar re-run after its own result is not the bar that was registered."*
The 138 were bought in one session on 2026-08-12 for $0.2764, the team lead read all 80 price pairs
against 26 page images, and one bar failed. **The home of every value below is the artifact named
beside it**, never this file: if the two disagree, the artifact is the contract.

## (1) The three bars, both instruments

`results/sku_bar_verdicts.json` (v1, over the v4 population) and `results/sku_bar_verdicts_skub2.json`
(v2, over B′'s). Both are `market_pulse.scorer`'s for bars 1 and 3; bar 2 is the team lead's read in
both, transcribed by `scripts/apply_sku_pair_verdicts.py` and
`scripts/apply_sku_pair_verdicts_skub2.py` respectively (SPEC §10 — the executor never scores its own
sample).

| bar | registered | v1 | v2 | n (v2) |
|---|---:|---:|---:|---|
| 1 — leaflet brand recall | ≥ 0.75 | 0.3603 FAIL | **0.9800 PASS** | macro over the 10 posts with a non-empty B′ gold (R1/R2/R3) |
| 2 — price-pair accuracy | ≥ 0.80 | 0.3279 FAIL | **0.4125 FAIL** | 33 of 80 pairs, read by the team lead 2026-08-12 |
| 3 — text tier accuracy | ≥ 0.85 | 0.8621 PASS | **0.8667 PASS** | 30 of 30 rows, 0 unreadable (R5) |

**State: CLOSED — instrument not ready, BY MEASUREMENT.** One of three bars failed. No retry, no
re-prompt, no second draw. The closure block quotes `attempts.on_failure` out of the registration and
names the failed bar from the computed verdicts.

**Bar 1's two numbers are not one number.** 0.3603 and 0.9800 are each instrument against ITS OWN
registered gold, and 3.17 (13)(c) re-scoped the gold between them: 55 pairs over 15 posts became 37
over 10 when the class-b and class-c pairs left the denominator. The like-for-like READING is the
team lead's, quoted from 3.17 (14) and not re-derived here (SPEC §10): **v1 on the B′ gold reads
0.703** against v2's 0.9800 on the same gold. What that 0.277 is MADE of is not measured — three
amendments landed in one instrument, and [[sku-b-pilot-closed-by-measurement]] §4 named a fourth
candidate that is not the instrument at all (the gold counts brands a reviewer could SEE, the
instrument returns POSITIONS), which (13)(c) addresses by moving the denominator. See (7) and Dv236.

## (2) What (13) fixed, measured

Every number here is a difference between `results/sku_b_positions_v4.json` and
`results/sku_b_positions_skub2.json` over the same 138 elements and the same 108 pages.

| | v1 | v2 |
|---|---:|---:|
| unreadable replies | 5 | **0** |
| — of them page answers | 4 | **0** |
| replies truncated at the ceiling (`finish_reason: length`) | 1 | **0** |
| bar 1's unreadable pages | 4 | **0** |
| bar 3's scoreable rows | 29 of 30 | **30 of 30** |
| price pairs the dump carries | 61 | **80** |
| positions extracted | 79 | **101** |

The four refused page answers were `4342` and `4467` (`printed discount '-50%*' is not a
percentage`), `4405` (`malformed JSON`, and the one reply v4 hit the 800-token ceiling on) and `4446`
(`size '6х100 г' is a multipack`). All four came back clean under v2, and bar 1's precision probe
stayed at zero false positives on the nine empty-gold posts: the recall was bought without buying
invention.

## (3) What it never touched: the superscript is still the superscript

Bar 2 moved 0.3279 → 0.4125 and **not one of the 61 verdicts the two reads share moved**.
`results/sku_b_pair_verdicts_skub2.json :: extends` carries the split, checked against the sealed v4
read rather than asserted:

| | keys | rows | correct | accuracy |
|---|---:|---:|---:|---:|
| shared with the v4 read, verdict and printed_old unchanged | 45 | 61 | 20 | **0.3279** |
| new under v2 | 19 | 19 | 13 | **0.6842** |
| all | 64 | 80 | 33 | **0.4125** |

The 19 new pairs sit on exactly the four pages v1 refused — 4342 (2), 4405 (9), 4446 (6), 4467 (2) —
which is why the widening is not a re-adjudication: (13) opened four pages, and those four pages
brought 19 more price boxes with them. On the 61 pairs both instruments produced, the crossed-out old
price reads exactly as badly as it did before the parser family, the ceiling and the aliases.

The team lead's diagnosis line, verbatim from
`results/sku_b_pair_verdicts_skub2.json :: diagnosis`:

> promo 80/80 correct · printed % 80/80 correct · crossed-out old 33/80 — the superscript family
> again; dense multi-item pages read their olds better (4405: 7/9, 4446: 5/6) than single-hero
> posters

Three numbers on one price box; the two large ones are perfect on all 80 and the small struck-through
one is right two fifths of the time. (13) was a parsing and vocabulary amendment and the failure is a
**resolution failure on a glyph class**. Nothing in v2 addressed it and the measurement says so.

## (4) Depth: adequate under both instruments, on both populations

`results/sku_depth_from_pct.json` (61 pairs, 22 pages) and `results/sku_depth_from_pct_skub2.json`
(80 pairs, 26 pages), both against the team lead's own `printed_old`, both under the same rule and
the same code.

| instrument | population | median \|Δ\| | max \|Δ\| | ≤ 1 pp | ≤ 2 pp |
|---|---|---:|---:|---:|---:|
| the printed `-N%` badge | v1, n=61 | 0.2886 pp | 1.4171 pp | 60/61 | 61/61 |
| the printed `-N%` badge | **v2, n=80** | **0.3212 pp** | **1.4171 pp** | 79/80 | **80/80** |
| the extracted old price | v1, n=61 | 0.1761 pp | 1.6366 pp | 56/61 | 61/61 |
| the extracted old price | **v2, n=80** | **0.1670 pp** | **1.6366 pp** | 75/80 | **80/80** |

The widening did not move the reading: the 19 new pairs are inside the rule on both instruments, and
the largest gap between a printed old price and the extracted one anywhere in the 80 is **0.90 UAH**
(199.90 printed, 199.0 extracted). Bar 2 fails on the printed NUMBER; on this population neither
instrument fails on the DEPTH that number is used for, because every dictated error is kopiyky-scale
and depth barely moves on them.

The adequacy rule — every pair within 2 pp, median within 1 pp — is stated inside both records as the
measuring script's own and is **not registered**. It was deliberately left unchanged between the two
readings: two measurements taken under two rules are not two measurements of the same thing.

## (5) What the programme cost

Four sessions, settled balance deltas, each a FLOOR by Dv33:

| session | cost | cap | what it bought |
|---|---:|---:|---|
| `sku-b` | $0.1965 | $0.35 | 17 of 138, stopped by its own (10)(b) gate; the finding that the go/no-go probe was a 64×64 thumbnail |
| `sku-b-v3` | $0.1526 | $0.45 | nothing bought: refused by (10)(a) before the first gold call, 121 calls projected $0.5964 against $0.45 |
| `sku-b-v4` | $0.2541 | $0.65 | the 121, the completed population, all three bars readable — and the pilot's closure |
| `skub2` | $0.2764 | $0.65 | the 138 re-asked with instrument v2, 0 unreadable, and this closure |

**$0.8796 for the position instrument end to end.** Phase 4 stands at **$23.6653 of $25.00**. This
closing session cost **$0**: every deliverable in it is arithmetic over files already bought.

## (6) The product reading — a CANDIDATE for the operator's 5c2 ruling

Nothing here is authorised by this record. It is what the two measurements support, offered to the
ruling that has to be made anyway:

1. **Question 7 (weekly median depth) is served by the promo price and the printed `-N%` badge.**
   Both are 80/80 correct under the team lead's read, and the badge lands within 2 pp of the true
   depth on every pair in the population.
2. **The extracted old price stays, and stays flagged.** It is the more accurate depth instrument of
   the two (0.17 pp median against 0.32 pp) despite being right as a NUMBER only 41% of the time, and
   dropping it would buy no accuracy — but it is the number to distrust to the kopiyka, and any
   surface that prints it as a price rather than as an input to depth is printing a wrong number on
   47 of 80 pairs.
3. **The crossed-out number is never trusted to the kopiyka.** Not for a price comparison, not for a
   "was/now" claim, not for anything a reader would check against the leaflet.

Everything [[sku-b-pilot-closed-by-measurement]] §7 listed as a candidate stands, minus what (13)
already spent: the parser family shipped and worked, and the two-stage OCR read is now the only
remaining candidate that addresses (3) — the failure it targets is exactly the one v2 left untouched.

## (7) What this record does NOT decide

* **It does not reopen a bar.** `attempts.on_failure` forbids a retry, a re-prompt and a second draw,
  and the closure is taken on the bars as read. B′ was the one re-measurement (13)(d) granted.
* **It does not authorise a third instrument.** No session, no cap and no registration is opened here.
* **It does not rule on the badge.** (4) is a measurement with a stated-not-registered rule; the
  threshold that decides whether question 7 needs the old price is the operator's at 5c2.
* **It does not explain bar 1's move.** 0.703 → 0.9800 is v2 against the B′ gold and the gain is real,
  but the run bought no per-cause decomposition of it: three amendments landed at once (parser
  family, 1200 ceiling, three aliases) and no artifact says which supplied what. Dv236.
* **It does not close what bar 2's parser warnings would have shown.** The (13)(a) warnings were
  never written into the run record (Dv232), so which warning kept which position alive is
  unrecoverable for this run.
* **Bar 3's PASS is not an endorsement of the text leg.** 30 rows over a 0.85 bar move 3.3 pp per row,
  and R5's reachability floor of 20 was cleared by 10.

**Artifacts:** `results/sku_bar_verdicts_skub2.json` · `results/sku_b_pair_verdicts_skub2.json` ·
`results/sku_depth_from_pct_skub2.json` · `results/sku_pilot_prereg_b2.json` ·
`results/sku_b_positions_skub2.json` + `.jsonl` · `results/spend_skub2.json` ·
`docs/PROMPT-skub2-close.md` · `docs/reports/skub2-run.md` ·
[[sku-b-pilot-closed-by-measurement]] · [[sku-b-v3-refusal-and-v4]] ·
[[sku-b-run-acceptance-and-resume]] · [[sku-b-pilot-readings-ratified]] ·
[[sku-b-serving-and-cap-discipline]]
