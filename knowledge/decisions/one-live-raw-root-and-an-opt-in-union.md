---
type: decision
date: 2026-08-30
status: implemented
tags: [decision, store, collection, promo-pulse-1]
---

# One live raw root, and a union that is opt-in

**Ruling (team lead, 2026-08-30, «Acceptance of the scaffold slice»), implemented the same day in
`80a9d10`.** SP-4 stopped S2 because four A1 channels write into the four pinned files of
`results/raw_v1_baseline.sha256`, and `data/` is gitignored — the append would have been invisible
to `git status` in both directions and impossible to undo. The ruling took option (a) and widened
it from the top-up to the whole loop.

## The three rules

1. **`data/raw/` is an archive**, read-only forever. The baseline stays the proof, because it is
   the only durable one.
2. **One live root, `data/raw_r2/`**, takes the top-up for EVERY collected channel — the pinned
   four and the free sixteen alike, so no reader has to know which root a channel's rows came from.
3. A reader that wants the corpus reads **v1 ∪ r2, deduplicated on (channel, msg_id), r2 winning**
   — and **the union is opt-in, never the default**.

## Why opt-in is the load-bearing half

Nine consumers were counted, and the column that decides the design is *which root*, not the
filename. Two of them want opposite things:

- `scripts/promo_census_c2.py` MUST see r2: it prices the topped-up corpus, and reading v1 alone
  would pre-register a population that no longer exists.
- `scripts/draw_promo_threads.py` MUST NOT: its population is the frozen 678 price threads, the
  holdout is frozen at the draw, and a union there would move 678/488 with nothing in the file to
  say so.

A union that defaulted on would have been correct for eight consumers and silently wrong for the
one whose output is a frozen exam. See [[a_consumer_list_is_not_a_meaning_list]].

**Measured control, twice.** The draw's sha was `6f9fa245b9d70254` before the top-up, after
+1 340 posts, and again after +1 190 comments — comments being exactly what it reads. A leak would
have moved it.

## The guard is at the chokepoint, not in the caller

`collect_r2.py::refuse_pinned` guarded a channel LIST. The moment the collector was retargeted at
the live root that guard passed trivially and protected nothing — so the refusal moved into
`RawStore.append`, which every writer goes through, and `refuse_pinned` stayed as the earlier
refusal that fires before a Telegram session is even opened.
Two consequences accepted deliberately: `collect_5c1.py` and `backfill.py` are r1 writers whose
writes the guard now refuses, and they are left in place rather than deleted — they are how the
archive was built. See [[a_moved_guard_that_left_its_copy]], [[the_guard_you_built_and_then_bypassed]].

## Named, not folded in

`scripts/fetch_comments_v2.py` writes a THIRD root, `data/raw_fresh_45g5/` (two comment files). The
ruling says «v1 ∪ r2» and does not mention it; nothing in this phase reads it, so it is a named
debt rather than a root I folded in on my own word.
