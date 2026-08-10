---
type: decision
id: dec-2026-08-10-opus-review-programme-close
date: 2026-08-10
status: accepted
tags: [decision]
---

# The Opus review programme closes: the matcher is acquitted on 498 rows, and every miss prices the captions

**Context:** SPEC amendment 3.16 authorised a second instrument — Opus 5 inside Claude Code, under a
committed audit protocol — to read the 5c1 corpus and say what the deterministic matcher and the
GM4 captions had missed. 3.16 (1) fixed the output class: **REVIEW, never measurement.** Nothing
this programme produced may enter a gate, the screen or `results/baselines.json`; the deterministic
matcher stays the sole judge of screen and G1e numbers; screen v2 verdicts are not re-scored; the
pre-registered bars do not move. 3.16 (3) made the findings a **deferral criterion for the launch
signature**. This record closes the programme. Every number below is read out of
`results/opus_audit_5c1.json` (`608560de…`), not out of prose.

## (1) Coverage: the whole declared population, and nothing inferred

`coverage`: **25 of 25** packs returned, **498 of 498** items in the manifest answered,
`rows_read` 498, `unanswered` **[]**, `items_in_returned_packs == items_in_all_packs == 498`.

The strata are the manifest's, committed before a pack was opened
(`results/opus_audit_manifest.json`, `b2708885…`, pinned by the record): S1 75 caption-decided
screen hits · S2 145 matcher brand-hit posts (precision probe, per-channel cap 10) · S3 197
relevant posts the matcher found no brand in (recall probe, cap 10) · S4 194 committed caption rows,
163 of them judgeable for faithfulness. An item carries **every** stratum it belongs to, so the
strata overlap by construction and **their FN columns do not sum to the total** — 92 + 6 + 35 + 97 =
230 against an overall 102. The overall row is the enumeration; the strata are cuts of it.

Corpus integrity was proved *before* the split rather than assumed: `matcher_strings` re-derived
**9,343** posts, reproduced **66** channels × **6** cells against the signed screen record, and
re-checked **498 of 498** item verdicts against the manifest. A post edited in place leaves all six
counters equal and changes the string under them, which is why the per-row check exists.

## (2) The verdict: `fn_matcher = 0` on all 498, and the shape of that zero is the finding

`matcher_candidates.overall`: **tp 93 · fp 104 · fn 102**, `precision_candidate` 0.4721,
`recall_candidate` 0.4769 over 498 items judged. One (item, brand_id) pair per brand.

The team lead's 2026-08-10 ruling had the reader split FN deterministically, by the matcher's **own**
rule — the pinned watchlist's aliases compiled through `market_pulse.yield_screen.compile_aliases`,
casefolded and bounded by non-word characters, searched over the exact string the matcher read (the
post's text, the caption standing in for it, or the two joined). Not a substring test.

| bucket | pairs | owner |
|---|---|---|
| `fn_matcher` — the name was in the string and the matcher stayed silent | **0** | the lexicon and the alias table |
| `fn_image_only` — the name was never in the string the matcher read | **102** | caption coverage |
| `substring_would_disagree` | 1 | @atb_aktsiyi:3087 / «лімо» inside «лимон» — word-boundary being right |

**The zero is structural, and saying so is what makes it usable.** A word-boundary matcher over its
own alias table finds *every* alias literally present, so `fn_matcher` can only be non-empty through
the nested-alias rule («Яготинське» inside «Яготинське для дітей») or a reviewer naming a brand the
text does not spell. Neither happened in 498 rows. The consequence: **the entire FN column measures
the captions' coverage, and `recall_candidate` 0.4769 is not the matcher's recall.** Any future
reader who quotes it as one is quoting a number about a captioner.

The strata separate the way they were drawn to. S2 — posts the matcher spoke about — returns
precision 0.3774 and recall 0.9091: where it speaks it is often wrong and rarely incomplete. S1/S4 —
caption-decided — return precision 0.9104 and recall 0.3987 / 0.3861: right when they speak, blind
most of the time. S3 returns 35 misses, 0 hits and `recall_is_definitional`: the matcher emitted
nothing there, so its tp is 0 before any reviewer looked (Dv99).

## (3) The captions: 163 of 163 judged, and 3 are wrong

`caption_candidates`: denominator **163** — items whose caption a model wrote over images that are
on disk under the sha the caption row recorded. `judged` 163, `declined_n_a` 0.

| verdict | rows |
|---|---|
| faithful | **117** |
| partial | **43** |
| wrong | **3** |

`faithful_rate_candidate` **0.7178**. The 31 S4 rows that are *not* in this denominator are poll
transcriptions with no model and no image (Dv82): counting them would put free deterministic rows
into GM4's rate.

What the misses look like, in the reviewer's own notes: a six-page leaflet's caption transcribes
**one** page and not the first (@atb_aktsiyi:3164 renders the loyalty-card cover, the only page with
no products); a caption truncated mid-token at the doorstep of the album's two dairy pages
(@atb_aktsiyi:3087, «…180 г Т»); a whole ice-cream page reduced to «акціями на морозиво»
(@VARUS_channel:10562). This is the vis-b bridge finding at 25× the sample: **a ~230-character
caption is a sample of a dense leaflet, not a description of it** — and it is what SPEC 3.17 (4)'s
per-page extraction exists to answer.

The brands being lost are our own. **Two tables carry that, they are not the same table, and the
difference is itself a finding:**

| table | denominator | pairs | brands |
|---|---|---|---|
| `matcher_candidates.missed_brand_candidates` | the matcher's FN over all 498 | 102 | 15 |
| `caption_candidates.brands_visible_missed` | the 163 judgeable caption rows | 95 | 14 |

The matcher-side table: Своя Лінія ×17 · Варто ×13 · Рудь ×11 · Три Ведмеді ×10 · Ферма ×9 · Ласунка
×9 · Лімо / Селянське / Яготинське ×6 · Молокія / Злагода ×5 · Галичина ×2 · Хладик / Премія /
Волошкове поле ×1.

The **7 pairs in the first and not the second** are the interesting ones, and they split 5 / 2:

* **5** sit on rows with no image and no caption at all (@msuaaaa:10533, @silposilpo:3776, :3791,
  :3805, @ekomarket_shop:1450 — `images.named: 0`). No caption exists to have missed anything, so
  they are outside the caption table's denominator by construction.
* **2** are rows where the caption **did** name the brand and the matcher still missed it:
  @atb_market_official:4340 and @atb_aktsiyi:3134, both `try-vedmedi`. GM4 transcribed the pack as it
  is printed — «морозиво брендів **Three Bears**, Рудь, Своя Лінія» — and the watchlist holds
  «Три Ведмеді» only. So the string carried the brand in **Latin script** and no alias matched it.

That second pair bounds the acquittal in §2 exactly. `fn_matcher = 0` is a true statement about the
matcher: it emitted every alias literally present. It is **not** a statement that the alias table is
complete — «Three Bears» for Три Ведмеді, and the declension forms below, are gaps in the table, and
they belong to the 5c3 named revision. It also confirms, from the record's own arithmetic, which
caption was in the string those two rows were matched on: the qwen caption for 4340 writes ТМ
«Три Ведмеді» in Cyrillic, and had the matcher read *that* string `fn_matcher` could not have been 0.

## (4) The false positives are one word and one office, and they stay raw

`false_positive_candidates`: **varto 69 · president 24 · varus-pl 5 · ferma 2 · garmonija 2 ·
premia 1 · selianske 1** — 104 pairs, of which **93 are varto + president**: the ordinary Ukrainian
adverb «варто» and «Президент України / Офісу Президента». `varus-pl ×5` is VARUS naming its own
store.

They are **not** split in the record, by the team lead's ruling: splitting them would need a
committed list of collisions the operator has already ruled on and there is none, so reading them is
the sitting's prose and not the reader script's arithmetic. That reading happened — see
[[sitting-2026-08-10-composition-signed]].

**The line that is easy to miss by reading the two tables separately: `varto` stands in BOTH
columns** — 13 misses and 69 false positives. The reviewer saw it on packaging; the matcher fired on
the adverb. It is the most consequential row in the whole record.

## (5) Open extraction: 141 names the watchlist does not carry

`open_extraction_candidates`: **141** distinct dairy / ice-cream names outside the watchlist, 196
mentions, **117 of them singletons**. Eight names reach ≥4 mentions and are the top tier the record
leaves as a candidate list: Розумний вибір 8 · Каштан 7 · Київський Пломбір 6 · Комо 6 · День у День
5 · Laska 4 · ПростоНаше 4 · Щоденний збір 4. Against **12** names on the 40-row pilot — this is the
deliverable the strata were drawn for and the sitting's largest single input.

Beside it, a lexicon finding the reviewer's notes carry and no counter does: **the canon lists only
the neuter forms.** Leaflets print «ТМ Яготинська» (ряжанка, сметана), «ТМ Яготинський» (кефір), «ТМ
Селянська» (ряжанка) — feminine and masculine agreement with the product noun — while the watchlist
holds Яготинське / Селянське. Every one of those is a miss the alias table cannot see.

## (6) What the programme cost, and what it can prove about itself

$0 on metered money: 25 Claude Code sessions on the subscription. The pin that was possible was
made and the pin that was not is declared: `instrument.model` = `claude-opus-5` as **declared** on
the session's first line under the protocol's rule 1; `protocol_sha` `d02ed1f4…` for
`docs/PROMPT-opus-audit-protocol.md`, committed before any pack was opened; the pack manifest
sha-pinned. `declared_not_verified` says the rest in the field itself: a returns file cannot prove
which model wrote it, and price is unpinnable on a subscription — **which is why the output class is
review**.

Artifacts, all committed:

| what | path | sha256 |
|---|---|---|
| the record | `results/opus_audit_5c1.json` | `608560de…` |
| the sealed manifest | `results/opus_audit_manifest.json` | `b2708885…` |
| the protocol | `docs/PROMPT-opus-audit-protocol.md` | `d02ed1f4…` |
| 25 returns files | `results/opus_audit_returns/*.jsonl` | `eb3a0f30…` (concatenated) |

One ruling of the run is recorded here because it set a precedent: **pack_08 declared the model on
its third line instead of its first, the driver halted, and the operator counted the pack while
leaving the gate strict.** Position of a line adds nothing to a guarantee the class already refuses
to make — but a gate loosened mid-run to keep a run moving is a gate the next surprise walks
through. Cost of the ruling: zero. Cost of the alternative: one subscription session.

## (7) What this decides, and what it does not

**Decided:** the programme is closed and complete — 25 of 25 packs, 498 of 498 rows, all validating.
The matcher is **acquitted**: not one miss in a readable string. The FN column is re-labelled for
every future reader as a measurement of caption coverage, not of matching. The findings were
presented at the sitting, which discharges SPEC 3.16 (3)'s deferral criterion.

**Not decided here:** nothing about the watchlist, the lexicon or the composition. The `varto` and
«Селянське» readings, the 141 names and the launch signature are the operator's and live in
[[sitting-2026-08-10-composition-signed]]. The three `wrong` captions have no re-do order.

**A consequence of the signature, recorded where it is a footgun:** the 2026-08-10 stamp moved
`config/registry.yaml`'s bytes, so `scripts/validate_opus_returns.py` and
`scripts/read_opus_audit.py` now refuse to run against the sealed manifest — correctly, the same way
`read_calibration_returns.py` does. `results/opus_audit_5c1.json` is final; re-deriving it means
checking the registry out at `d832477` first, never re-pinning the manifest.

Related: [[sitting-2026-08-10-composition-signed]] · [[5c1-vis-b-caption-instrument]] ·
[[5c1-relevance-floor-and-discovery]] · [[phase45a-ceiling]] · [[2026-08-10]]
