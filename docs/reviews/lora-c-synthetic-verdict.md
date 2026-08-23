# lora-c — review gate 2 VERDICT: the synthetic rows (team lead, 2026-08-23)

**This file is the TEAM LEAD's. The executor acts ONLY on the rulings below, reports counts per
ruling, and flips `reviewed` to `true` on all 160 only after the rewrites land. NO LABEL CHANGES
anywhere in this file — every ruling is a text or rationale rewrite, so the 8/8/8/8/8 balance and
the ±2 rule survive by construction. Re-run contamination (four lists) and the register table
after the rewrites; both go into the application report.**

All 160 rows read. **Drops: 0. Rewrites: 6 named rulings.**

## R1 — the 15 flagged rows: the executor was right, and the fix is the TEXT, not the label

The codebook clause stands and my own labels are the precedent — `@VARUS_channel:10470:21236`
(«кубок ковбасний … нема» — a NON-DAIRY thing out of stock, labelled `сеть_ритейлер`), `21240`,
`10367:20979`. A stock / price / promo / assortment claim about a named chain is `сеть_ритейлер`
even when the thing is non-dairy. So the 15 rows as written teach the opposite of the codebook
**and** of 21 of my 37 `сеть_ритейлер` labels.

**Rewrite the 15 TEXTS, keep the labels.** Each comment must become a claim about the THING
itself (quality, taste, experience of use), with the chain named only as WHERE — because that is
precisely the discrimination `retailer_non_dairy` exists to teach. Shape to follow:
«Корм Брит коту зашёл…» (non_dairy_brand 5) — thing-quality, place incidental. Example of the
transformation: «В АТБ шампунь дешевший ніж в аптеці» (price-at-chain → `сеть_ритейлер` by the
codebook) becomes «Шампунь той самий, що я в аптеці брала, — в АТБ теж норм» → thing-quality,
`не_наш_рынок` honest. Rows: `brand_vs_retailer` 25, 27–32 · `retailer_non_dairy` 9–16.
Rationales follow the new texts.

## R2 — `mention_vs_about` 5 contradicts my gate-1 ruling on its real twin

Gate 1 ruled on `@matusi_ukr:22158#578032`: «Морозиво. Мені чудово допомагає…» is personal USE
of the category product — label `категория_личное` STANDS. Synthetic 5 has the same reading
(«лечусь так с детства», «мне помогает» — habitual personal use of морозиво) labelled
`не_наш_рынок` — one reading, two classes, two files, one training run, on the axis arm B exists
to fix. **Rewrite the TEXT into a genuinely instrumental shape** (the dairy serving another
subject, like rows 1–4 and 6–8: ingredient, prop, means — with no habitual-use-by-the-commenter
reading), label stays `не_наш_рынок`.

## R3 — seven rationales are Russian/hybrid; the rationale language is Ukrainian, always

Lens 2's «7 UA/RU hybrids» live HERE, not in the rationales file (my grep over all 515 real
rationales: zero). The seven: `brand_vs_retailer` 26, 29, 32 · `retailer_non_dairy` 11, 14 ·
`mention_vs_about` 5, 7 — all shaped «лише УПОМИНАЕТ …; на самом деле про …». The supervised
span is one UKRAINIAN sentence regardless of the comment's language (the real corpus does
exactly this — RU comments, UA rationales). Rewrite the seven rationales in Ukrainian:
«лише ЗГАДУЄ …; насправді про …».

## R4 — a real user's handle in «written from scratch» rows

`@olega13` is a real window handle (it appears verbatim in `@VARUS_channel:10466#21387`) and is
reused in `brand_vs_retailer` 35 and `retailer_non_dairy` 33. Synthetic may not carry real
users' handles. Replace with invented handles (not resembling any handle in the window store —
check by substring against the store's author fields), texts otherwise unchanged.

## R5 — the молочный_бренд skeletons: vary the syntax, the class is carried by these 32 rows

16 of 32 `молочный_бренд` rows sit on two skeletons («<Бренд> <продукт> <властивість>» and its
minor variant). Synthetic is the ONLY positive supervision this class gets anywhere in the line
(32 vs 1 real rendered → 0 in arm A), so a skeleton is what the adapter would learn. **Rewrite
enough of the 16 that no single skeleton covers more than a third of the 32**: question forms,
reply-forms, short anecdotes, comparisons — same labels, same subjects, same register rules.
Enumerate before/after skeleton counts in the application report.

## R6 — the newline axis: one seeded pass, ~19 % of rows

Not one of the 160 texts contains a newline against 19.4 % of real comments — a discriminator
separates the corpora on that alone (Dv764). One seeded pass (seed in the producer, registered)
introduces natural line breaks into ~30 rows across all four classes — multi-sentence rows
split, list-ish rows broken — texts otherwise unchanged. Length/question-rate gaps REMAIN
accepted as deliberate and named (the report's reasoning holds); terminal punctuation at −5
stays as is. Re-measure the register table after the pass.

## Consistency with gate 1

«власний формат мережі» in `non_dairy_brand` 25–26 → «формат мережі» (gate 1 named the same
overload on `20696`; «власна торгова марка» in row 27 is the fixed retail term and STAYS).

## Explicitly ACCEPTED

The two name-collision jokes (`Пломбір`-салон, `Сирна лавка`, `Вершкове Сяйво`, `Молочна
кавʼярня`) — this is the 21.4 % subject_doubt class done right. The giveaway-noise nulls
(`brand_vs_retailer` 33–40) — consistent with the N2 ruling. The mixed shape «лише ЗГАДУЄ …;
насправді ні про кого» in `mention_vs_about` 17–19 — matches the real tier-A shape. Balance,
contamination (re-verified by my own 6-gram refuter: zero collisions), and the length rationale.
