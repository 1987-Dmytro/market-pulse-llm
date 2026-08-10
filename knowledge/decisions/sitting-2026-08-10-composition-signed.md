---
type: decision
id: dec-2026-08-10-sitting-composition-signed
date: 2026-08-10
status: accepted
tags: [decision]
---

# The 2026-08-10 sitting: «Варто» loses text matching, «Селянське» needs an anchor, the 141 names wait for the position layer, and the composition is signed

**Context:** SPEC amendment 3.16 (3) sent the Opus review's findings to an operator sitting and made
those findings a **deferral criterion for the launch signature** — the composition frozen on
2026-08-08 could not be signed while they were outstanding. They were presented in full on
2026-08-10 ([[opus-review-programme-close]], `results/opus_audit_5c1.json`, `608560de…`). This record
holds what the sitting decided. Four rulings; the evidence for each is read out of that record.

## (1) «Варто» — text matching OFF

**Ruling:** the watchlist brand `varto` no longer produces a hit from a channel's text. Its hits come
from captions and images, or from text where a brand marker stands beside the name (`ТМ «Варто»`,
`Varto` as printed on the pack). Implemented as part of the 5c3 **named** revision, through the
two-level watchlist of SPEC 3.17 (2) and its `requires_anchor` flag. **G1e history is never
re-scored on it.**

**Why it is the most consequential row in the record: `varto` stands in both columns.**

| column | count | what fired |
|---|---|---|
| false positives | **69** of 104 | the ordinary Ukrainian adverb «варто» — "it is worth" |
| missed brands | **13** of 102 | the pack's own printing, seen by the reviewer on images |

69 of the 104 false-positive pairs in the whole audit are this one alias, across
`@dpssgovua`, `@educationwithloven`, `@mandziak`, `@matusi_ukr`, `@klopotenkofood` — feeds where
nobody is selling dairy and everybody writes "варто". The yield screen had already found the same
thing from the other side on 2026-08-08: `@polyakova_fitness` cleared bar A on `brand:varto` **alone**
and was ruled below the bar for it ([[5c1-relevance-floor-and-discovery]]). The audit is that ruling
at 25× the sample.

Note what the ruling does **not** cost. The watchlist carries `varto` as `("Varto", "Варто")`, so the
Latin pack spelling survives the ruling as an anchored form; and the 13 image-side finds were never
text hits to begin with.

## (2) «Селянське» — a hit only with a Гармонія marker beside it

**Ruling:** `selianske` matches only when a marker of the brand stands next to it. Bare «селянське»
in running text is not a hit. Same vehicle as (1): the 5c3 named revision, `requires_anchor`.

**Why:** the string is three different things on Ukrainian leaflets, and the reviewer's notes catch
all three on the same pages.

* **the TM** — «Масло солодковершкове «Селянське» ТМ «Молокія»» (@atb_market_official:4401);
* **a butter grade** — «МАСЛО 73% Селянське ТМ Столиця смаку» (@VARUS_channel:10410) and
  «МАСЛО солодковершкове селянське ТМ ЦХТ» (@VARUS_channel:10552), where the word is a descriptor
  and the trade mark is somebody else's;
* **another brand's product line** — «МОРОЗИВО СЕЛЯНСЬКЕ ТМ Рудь» (@VARUS_channel:10562), where a
  string matcher scores a hit on a different entity entirely.

@VARUS_channel:10410 carries the two readings **on one page**: «РЯЖАНКА ТМ Селянська» (a true miss,
and a declension the canon does not hold) beside «МАСЛО 73% Селянське» (a false positive). The record
counts `selianske` as 6 misses and 1 false positive; the ruling is about which of the two a bare
token is allowed to be, and the answer is neither.

## (3) The 141-name watchlist revision — DEFERRED, deliberately, into the position layer

**Ruling:** the 141 dairy / ice-cream names the audit found outside the watchlist do **not** become
watchlist rows today. The operator raised the design question they exposed — **brand + SKU**: a line
or a position is identified *when the brand is* — and that question is answered first. It was
answered the same day as **variant B, the full position**, and is now SPEC amendment **3.17**; the
name revision executes inside it, as the 5c3 two-level watchlist (brand → `lines[]` with
`requires_anchor`).

The candidate list stays in the record rather than in the registry. **141** distinct names, 196
mentions, **117 singletons**; the eight names at ≥4 mentions are the top tier:

| name (as written) | mentions |
|---|---|
| Розумний вибір | 8 |
| Каштан | 7 |
| Київський Пломбір | 6 |
| Комо | 6 |
| День у День | 5 |
| Laska | 4 |
| ПростоНаше | 4 |
| Щоденний збір | 4 |

Two structural gaps travel with them, and neither is a new brand — both are the alias table failing
on names it already holds:

* **declension.** Leaflets print «ТМ Яготинська» (ряжанка, сметана), «ТМ Яготинський» (кефір), «ТМ
  Селянська» (ряжанка) — agreement with the product noun — while the canon holds only the neuter
  «Яготинське» / «Селянське».
* **script.** GM4 transcribed «Три Ведмеді» as its pack prints it, «Three Bears», on
  @atb_market_official:4340 and @atb_aktsiyi:3134. The caption was right and the matcher still
  missed, because the watchlist has no Latin alias for that brand — unlike `varto` and `president`,
  which do carry theirs.

Deferring is the cheaper mistake here: a watchlist edit today would be an unnamed revision under a
data model that is being replaced this week, and G1e history would have to be protected from it
twice.

## (4) The launch composition is SIGNED — 66 = launch 59 + watch 7, unchanged

**Ruling:** the composition is signed **as it stands**. The 2026-08-08 freeze is lifted, and every
row of the day-2 diff that stood PROVISIONAL pending the yield signature is now signed. **No row, no
bucket and no flag moves on this signature.**

It lands in `config/registry.yaml` provenance as a comment stamp (contract `docs/PROMPT-sku-a.md`
step 0). Verified rather than transcribed: the file parses to **66** sources, **59** launch + **7**
watch, and stripping the stamp back out reproduces the pre-stamp bytes `c82d0cff…` — so "the stamp
changed no row" is a test, not a sentence.

**What the signature cost, recorded because it is a live footgun:** the stamp moves the registry's
sha256, and five sealed records pin the signed bytes — `results/yield_screen_5c1.json`, `…_v2.json`,
`caption_rematch_5c1.json`, `caption_rematch_gm4_5c1.json`, `results/opus_audit_manifest.json`.
`scripts/validate_opus_returns.py` and `scripts/read_opus_audit.py` therefore **refuse to run**, the
same way `read_calibration_returns.py` has since the 4.5f rulings. That is correct: a sealed manifest
describes the watchlist its sessions were given. Nothing is re-pinned; the re-derivation path is to
check the registry out at `d832477` first.

## (5) What this decides, and what it does not

**Decided:** the two matcher rulings above, as 5c3 work with a named revision and no re-scoring of
G1e history; the 141 names deferred into the position layer rather than into the registry; the launch
composition signed at 66. 5c1 is closed. SPEC 3.16 (3)'s deferral criterion is discharged.

**Not decided here:** which of the 141 names become watchlist rows, and at what tier — 5c3's, on the
two-level watchlist. Nothing about the three `wrong` captions (no re-do order was given). Nothing
about the 400-token caption ceiling. And nothing about the position layer's own gates: those are
pre-registered in `results/sku_pilot_prereg.json` and belong to sku-b.

Related: [[opus-review-programme-close]] · [[5c1-relevance-floor-and-discovery]] ·
[[5c1-vis-b-caption-instrument]] · [[5c1-day2-composition-and-search]] · [[category-and-watchlist]] ·
[[2026-08-10]]
