---
type: decision
id: dec-2026-08-13-the-d-cut-and-the-fourth-kind
date: 2026-08-13
status: accepted
tags: [decision]
---

# The post leg's population is the D cut — 44 of 349 — and the marker row that makes its resume exact

**Context:** the c3a census answered the question 3.18 (7)(e) asked and produced a number nobody had
expected to have to rule on. `results/census_c3a_posts.json`: **349 of the window's 9 158 posts pass
the relevance pre-filter**, and **71.6% of that pass-set is recipe ingredient lines** — the four
biggest cooking channels alone are 250 rows, and not one of them carries a currency marker. The
filter's own docstring had always said it cannot tell «Кефір — 400 мл» in an ingredient list from an
offer; c3a is the first time that sentence had a number under it. The operator ruled on those
numbers on 2026-08-13 as **SPEC amendment 3.18 (7)(g)**, and the team lead ruled the Dv285 fork the
same day. **The home of every value below is the artifact named beside it**; if the two disagree,
the artifact is the contract.

## The rule, and it is a UNION

> of the rows that pass the prefilter, a row is kept iff its channel's carrier is `official_retail`
> or `aggregator`, OR its matched evidence carries the `currency` pattern

Computed by `scripts/postcut_c3b.py` into `results/postcut_c3b.json`, from the SHIPPED census whose
bytes are an input and were never touched. **44 rows across 10 channels, $0.0581 with drift.**

Two things in that sentence needed reading rather than assuming, and both are measured in the
record instead of decided in a comment:

* **"its channel's carrier" is the registry's `source_type`**, not the census row's own `carrier`
  field — which reads `post_text` on all 349, because that field says where the text was READ and
  the rule asks who is SPEAKING. A producer reading the row's field would have kept all 349 or none,
  and the count would not have moved at all;
  `tests/test_postcut_c3b.py::test_the_carrier_read_is_the_channels_type_and_not_the_rows_own_carrier_field`
  demotes a channel and watches one row leave while its `carrier` never changes.
* **"its matched evidence carries the currency pattern" has two readings** — the kinds found
  anywhere in the post's text (`pattern_kinds`, which is the field behind the **29** the ruling
  cites) and the kinds on the matched LINE alone. The contract operationalises the first verbatim.
  On this population **they select exactly the same rows** — 29 either way, 44 either way — so the
  ambiguity is closed by measurement, and the producer EXITS NON-ZERO on a population where they
  part.

## The three alternatives, re-counted rather than quoted

| alternative | rows | $ with drift | |
|---|---|---|---|
| all that pass | 349 | 0.3291 | declined — 71.6% recipes |
| carriers only | 31 | 0.0465 | declined |
| currency only | 29 | 0.0447 | declined |
| **the D cut** | **44** | **0.0581** | **registered** |

Each is recounted from the same rows by the producer, so the ruling's three numbers and the cut are
one arithmetic. **The cut is 44 and not the ~50–55 the contract expected**, and the cause is the one
that makes the ruling coherent rather than the one that would undermine it: the overlap is **16**,
not the ~5–10 that 31 + 29 implies, because currency-bearing rows cluster in exactly the retail and
aggregator carriers the first half already keeps. It changes no decision — at 2.8132 s/row the whole
50–55 range is under two cents wide, and the registered cap rounds to **$8.00** at either end.

**One number in the ruling is a floor rather than a total.** "250 of 349 rows from four cooking
channels" names the top four of the concentration table (85 + 72 + 52 + 41, cumulative share
0.7163). The `cooking_recipes` audience has **six** channels with a pass in it and **270** rows
between them. The cut removes all 270 — the clause understates what it removes and is not
contradicted by it (`removed_recipes` in the record).

## Why `POST_PRICE_ORIGIN`'s inheritance is now defensible

`market_pulse.loop.POST_PRICE_ORIGIN` is `retail_leaflet`, and it is INHERITED rather than decided:
`positions.CARRIER_ORIGIN` has no `post_text` row and `origin_of` raises rather than guess, because
"a retail chain's post and an aggregator's repost are the retailer speaking, and a community
channel's post about prices may not be". The paid skub2 text leg already answered `retail_leaflet`
for this carrier and its bar-3 measurement (0.8667) is what 3.18 (2) admitted the leg on, so a
second answer here would mean the rows the pilot scored and the rows the loop writes are not the
same observation.

Under the raw pass-set that inheritance was uncomfortable and the ruling says so: a recipe channel's
ingredient line stamped `retail_leaflet` is a price origin nobody measured. **The D cut is what
makes it defensible — recipe carriers no longer reach it.** Of the 44 kept rows, 30 are
`retail_official`, 13 `regional` and 1 `supermarket_deals`; the 13 regional ones are kept by the
currency half, which is to say they carry a price on the line that fired.

## The fourth evidence kind — the team lead's ruling on Dv285

c3a measured a gap and named the shape of the fix without taking it: the post leg wrote rows only
when the model found something, so a post that answered `[]` or came back unparseable left the disk
**indistinguishable from a post nobody had asked**, and an interrupted pass re-bought every one of
them. The sibling legs have never had that hole — a comment always writes its `comment` row and a
page always writes its `leaflet_page` row.

Ruled: `evidence.KINDS` grows **`post_text`**, `KIND_FIELDS["post_text"] = ()` (the `comment` shape
— a post's text IS its `rendering`, so there is no second artifact to name), and `REQUIRED` does not
change. `post_pass` writes the marker LAST per post, exactly as the page leg does, and the marker
carries no `row_id` so its `raw_store.dedup_key` is its msg_id and a second append collapses.

Measured in both directions rather than asserted:

* the c3a scenario planted unchanged — three posts, the middle two finding nothing, the cursor never
  saved — now re-asks **nothing**, with the OLD key kept beside it as the negative control, where
  the same store still yields the two;
* the exhausted-queue smoke goes from **2 transport calls to 0**, on the real corpus (27 posts asked,
  then 0, derived store byte-identical);
* the ORDER is measured, not asserted: a store that dies after the first file leaves the positions
  and no marker, and the post stays queued.

**Why it belongs in a decision record and not only in a commit:** it is the first change to
`evidence.KINDS` since the table was written, and the table is the one place SPEC 3.18 (6)'s sitting
is defined from. Nothing in the suite asserted the MEMBERSHIP of `KINDS` before this — `post_text`
was added and everything stayed green — so the amendment's cost is now one literal in
`tests/test_evidence.py::test_the_kinds_are_enumerated_literally_and_every_one_has_a_row_in_the_table`
and a reader. A fifth kind changes what the operator is shown; it may not land quietly.

## What this ruling does NOT do

* it does not re-open `results/census_c3a_posts.json` — the cut is a NEW record beside it and the
  census's bytes are unchanged (`4a7e755b73d6…`, the pair re-measured this session);
* it does not touch `REQUIRED`, `src/market_pulse/positions.py`, or any sealed sku artifact;
* it does not change what the pre-filter passes — 349 is still 349, and the cut is a registered
  POPULATION, not a new instrument;
* it does not start 5c2-run. The run is its own session under `results/prereg_5c2_run.json`.

Related: [[5c2-stop-ruling-and-cap-33]] (the ruling this one completes),
[[skub2-b-prime-closed]] (the bar-3 measurement the text leg was admitted on),
[[the-law-grows-inside-marked-blocks]] (why 3.18 (7)(g) is inside a strip block at all).
