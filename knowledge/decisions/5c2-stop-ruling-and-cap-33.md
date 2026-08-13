---
type: decision
id: dec-2026-08-13-5c2-stop-ruling-and-cap-33
date: 2026-08-13
status: accepted
tags: [decision]
---

# The prep-c2 STOP is answered by raising the line, not by cutting the window — and the records written under the old cap are never re-scored

**Context:** `docs/PROMPT-5c2-prep-c2.md` ended, by design, in a STOP with numbers rather than a
decision: the census of the 4-week window (`results/census_5c2.json`, anchor
`2026-08-09T00:00:00+00:00`) and the projection built on it (`results/projection_5c2.json`) reported
that the two priced legs cost **$7.6870 with drift against $6.1690 remaining** — 1.25× the budget —
and that a third row type the ruling scoped, post text, was in scope with **no writer in the code at
all** and a $8.1573 bound of its own. The operator ruled on those numbers on 2026-08-13 and the
ruling is law: **SPEC amendment 3.18 (7)**, inside the strip block, six clauses. This file is the
record of what was decided and what each clause binds. **The home of every value below is the
artifact named beside it**; if the two disagree, the artifact is the contract.

## (a) The anchor is ratified — and the alternatives were seen

`2026-08-09T00:00:00+00:00`, the corpus's own last day + 1, so the window is 2026-07-12 …
2026-08-09. The reasoning is `yield_screen_5c1.window_for`'s: a window ending later buys days that
are empty BY CONSTRUCTION and drops days that hold rows, which measures the collection schedule
rather than the content.

What makes this a ratification and not an acceptance-by-default: the census priced the two nearest
alternatives per column before the ruling (`anchor_sensitivity`), and the leaflet column alone moves
45 / 78 / 159 pages across them. Both were **seen and declined**.

The selection is pinned by `channels[].posts.ids_sha256` and not by a row count — a store that moved
under a later re-run produces the same total from different rows, and only the hash sees it.
`results/census_c3a_posts.json :: selection_pin` re-derives all 59 of them and agrees.

## (b) The phase cap moves 30 → 33 US dollars — and the past is not re-scored

Same mechanics as 3.18 (3): both homes in one commit — `scripts/runpod_guard.py :: PHASE_CAP_USD`
(what the guard ENFORCES) and `results/spend_phase4.json :: phase4_cap_usd` (documentation, which
moves with it or contradicts it). The anchor (35.00 read 2026-08-01T08:34:09Z), `anchored_at` and
all 35 logged sessions are untouched. **No money was added** — the balance is 11.1690 at the
ledger's last reading — so the raise lifts an artificial line and the refusal on a balance ABOVE the
anchor stays in force.

**The clause that binds the team lead, and it is the reason this ADR exists.** Records written under
the 30 cap — the prep-c2 projection and its `fits: false` against $6.1690 remaining — are true
statements of their write moment. They are **NEVER regenerated to fit the new cap.** Their tests
decouple from the live guard by the cap-in-force pattern the ledger repair already established
(`repair_phase4_ledger.CAP_IN_FORCE_USD = 25.00`, asserted DIFFERENT from what the guard enforces).

That rule has teeth in exactly two places today and both are green:

| what | how it is decoupled |
|---|---|
| `results/projection_5c2.json :: budget.phase_cap_usd` | `tests/test_projection_5c2.py :: CAP_IN_FORCE_AT_WRITE_USD = 30.00`, asserted `!= guard.PHASE_CAP_USD == 33.00` |
| the same record's `whole_window.fits: false` | the test now asserts BOTH halves — the record's sentence about $6.1690, and the live reading where $7.6870 fits inside the $9.1690 that remains |

The second one is the trap this clause is for. `fits: false` stayed **green** across the raise while
its meaning inverted: nothing would have gone red, and the STOP would have read as unresolved
forever. A record that cannot be regenerated needs its tests to say WHEN it was true.

## (c) Composition: the session buys the WHOLE two-leg window

All 5 075 comments plus the leaflet leg of (d) — ≈$7.80 with drift at the conservative corner — so
**no ordering or tie-break clause exists** to cut it. Stop rules for a mid-run truncation are the
pre-registration's to state, not this ruling's.

This is the answer to the STOP's actual question. The executor's report offered composition options
against a $6.1690 remainder; the operator moved the line instead of the population.

## (d) The leaflet leg's population is the corpus ON DISK, not the window's share of it

`results/post_media_5c1.json`: **159 pages under 19 posts**, all `@atb_market_official`, 2026-07-01
… 07-23 — re-counted from the manifest in `results/census_c3a_posts.json :: leaflet_corpus`, with
the clause's own sentence quoted beside it. The window holds 78 of those 159, and the leg buys all
159: *"leaflets follow their own weekly cadence, and the window clause of (4) binds the comment and
post legs only."*

ATB-only stands for this cycle. Collecting other chains' leaflets is **authorised as a separate
zero-cost collection task** — a prep, never inside the paid session.

## (e) The post leg enters FILTERED, never raw — and its writer did not exist

The projection's 9 158-post raw bound "enters no cap and no session". What enters is the population
the relevance pre-filter passes — `positions.prefilter`, the lexicon-over-post-text instrument of
`scripts/sku_prefilter_census.py`, **never the channel entry gate of 3.12, which gates CHANNELS**.

Two things prep-c3a produced against this clause:

* **the writer.** `market_pulse.loop.post_pass`, the third `*_pass` beside `inference_pass` and
  `page_pass`, on the SAME instrument as the leaflet leg and its other input shape (a string, not a
  one-image album). One property of the sibling legs it cannot carry, and it is a team-lead fork:
  there is no `evidence.KINDS` member for "a post was read and yielded nothing", so a post that
  comes back `[]` or unparseable writes no row and an INTERRUPTED pass re-buys it. Measured against
  the leaflet leg as a control, 2 re-asked against 0, on the same stub answers.
* **the population.** `results/census_c3a_posts.json`: **349 of the 9 158 posts pass (3.81%)**, at
  2.8132 s/row = **$0.3291 with drift**. And the finding the pre-registration needs before it names
  that number: 328 of the 349 carry a size, **29 carry a currency marker**, and four cooking
  channels are 71.6% of the population. The filter's rule cannot tell «Кефір — 400 мл» in an
  ingredient list from an offer — its own docstring says so, and this is the first time that
  sentence has a number under it.

## (f) The pre-registration is prep-c3b, and it pins by VALUE

Unblocked by this ruling. It exact-pins the chosen numbers with **equality** tests, not ceilings —
the prep-c2 review's finding that a caps table pinned by inequalities cannot see a number move
binds here.

## What this ruling does NOT do

* it does not reopen a bar, re-score anything, or move a threshold — 3.18 (2) stands unchanged;
* it does not add money to the account (balance 11.1690);
* it does not authorise a post leg in 5c2-run by itself: the writer now exists and the fourth
  evidence kind it needs for exact idempotence does not, which is prep-c3b's or the team lead's;
* it does not regenerate one byte of `results/census_5c2.json` or `results/projection_5c2.json`.

Related: [[skub2-b-prime-closed]] (the instrument the legs of (2) were admitted on),
[[the-law-grows-inside-marked-blocks]] (why 3.18 (7) is inside a strip block at all),
[[sku-b-serving-and-cap-discipline]] (the cap readings this raise sits under).
