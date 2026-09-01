---
type: decision
date: 2026-08-30
status: proposed
tags: [decision, sources, poltava, watchlist]
---

# The Poltava chats carry category voice, not brand voice

**Finding (executor, 2026-08-30, `retail-census` r2+r3).** The 61 collectable chats of Полтавщина do
not carry dairy-BRAND discussion. They carry a little dairy-CATEGORY talk. The two are different
questions and only the first was ever measured, so the census's `dairy_share` column had been
answering a neighbouring question to the operator's («де ми зможемо шукати інформацію про Гармонію»).

**Status: proposed.** What follows is measurement. The ruling it asks for — whether ~78 category
messages a month is worth collecting, and whether to buy the remaining 81 candidates — is the team
lead's and the operator's, not the executor's.

## Three independent checks, all negative

**(1) Direct reading.** 4 507 messages from the four liveliest chats in the oblast
(`results/poltava_brand_probe.json`). The watchlist fired **4 times and all four are false
positives**, hand-read: `president` on «третій **президент** України» — Yushchenko, the office — and
`ferma` three times on job ads, «**Ферма** клубники 6600/день», «Ферма яблок 6400/день». Real count:
**0**. The matcher is word-bounded, which is what stops «Ферма» matching «фермерське»; nothing stops
it matching the common noun. On a classifieds-and-job-ads corpus the watchlist manufactures signal
(Dv898) — a count of 4 and a count of 0 are the same file unless the verification sits beside them.

**(2) A different query genre.** The operator caught the gap: «Ты искал региональные каналы с
украинским написанием Підслухано Чутово?» No — `discover_channels.CHAT_TERMS` is
('чат', 'спільнота', 'оголошення', 'барахолка'), all four select classifieds, and «підслухано» did
not appear anywhere in the repo. So the null risked being a fact about the QUERY. Swept across all
24 district centres, 48 queries: **«типове» returns 0 hits in every one of the 24**; «підслухано»
returns 9 handles of which exactly one is a real town channel — `@svitlo5s` «Підслухано Кременчук.»,
1 865 subs, comments OPEN at **0.107/day (~3 a month)** and **dairy 0.000**;
`@pidsluhanolubnyofficial` (177) posts nothing at all. **Чутове returns 0 under this genre too.**
The gap was real and the conclusion did not move (Dv900).

**(3) Geolocation.** `contacts.getLocated` answers `Updates` with **0 chats and 0 users** for
Полтава (49.5883, 34.5514) and Кременчук (49.0632, 33.4225), the oblast's two largest cities. And
structurally it returns GEOCHATS — supergroups whose admin explicitly attached a location — so a chat
merely NAMED «Полтава чат» could never appear there even with a live index. Safety read from the
documented contract, not recalled: `self_expires` is the field that publishes the account's own
location and the docs state «if the flag isn't set, no changes will be applied»; the calls omitted
it, so nothing about this account was published (Dv901).

## The ceiling, computed before buying coverage

The 61 chats total 860 messages/day and **2.6 dairy-CATEGORY messages/day — ~78 a month** for the
whole oblast, before any brand filter. Independently, across the **16 324 comments already in
`data/raw/`** the watchlist is named 228 times, **198 of them `varus-pl` inside Varus's own channel**,
~30 are real competitor dairy brands, and **Гармонія is 0** — which reproduces SPEC v2 §0's own
«≈40, Гармонію — 0» from a different direction and on a different corpus (Dv899).

## What this does NOT settle

One branch is untested and it is the only one left that could rescue the premise: whether people
discuss dairy **without naming a brand** — «взяла молоко в АТБ, кисле». The category lexicon catches
that and the watchlist never will. It is free to test on text already collected, and it should be
tested before the ruling, not after.

Coverage itself is not the constraint: it went 18 → **21 of 24** district centres this session. The
three still empty are three different states — Чутове found nothing at any bar under either genre;
Диканька and Козельщина have chats that resolve, are OPEN and carry ZERO messages in 28 days.

Related: [[a_new_instrument_needs_the_old_ones_answers]], [[the_query_genre_defines_the_finding]],
[[a_verified_zero_is_not_a_raw_count]], [[compute_the_ceiling_first]].
