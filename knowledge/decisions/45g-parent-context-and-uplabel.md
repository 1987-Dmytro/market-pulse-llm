---
type: decision
id: dec-2026-08-02-45g-parent-context-and-uplabel
date: 2026-08-02
status: accepted
tags: [decision]
---

# The parent post enters the v2 prompts, the 97 emptied rows are re-asked, and the up-label goes

**Context:** the pre-registered ≥90% calibration of the taxonomy-v2 re-label passed at
**100/100** (`results/calib_45e_verdict.json`), so the re-labelled `intents` column is accepted
and [[taxonomy-v2-relabel-and-appetite]]'s sequencing condition — "no row is up-labelled until
this re-label passes" — is discharged. The same phase measured a defect in the instrument that
produced it: **97 rows carried an intent under v1 and none under v2**, 20.5% of all the drift the
taxonomy does not explain and **30.9%** of it on the rows a gate scores (`results/drop_45f.json`).
Their median length is 18 characters against 55 for the rest, every one of them is a reply, and
`results/drop_45f.json` records that the rendered prompt carries `["text"]` of a row and nothing
else. The 4.5f gate (operator, 2026-08-02) decided the three things below off those numbers.

## (a) The parent post joins the v2 prompts — as new revisions, and as a bug fix

**The prompts contradicted the guideline.** `docs/annotation/comments.md` §Unit has said since
Phase 2, of the annotator: *"Judge the comment on its own text, plus the parent post only when the
comment is meaningless without it (`Так`, `+`, (constructed) `А коли?`). Never label from the
thread's mood or from other comments."* — and it names the plumbing in the next paragraph: *"The
parent post is the row with `msg_id == parent_msg_id` in `data/raw/posts/<channel>.jsonl` — the
same channel as the comment. Every parent is there, because comments were collected from the
threads of stored posts."* Every prompt in `src/market_pulse/prompts.py` says the opposite:
*"Judge the text you are given, never the thread around it."*

So the model was scored against gold produced under a law it was not given. That is not a
taxonomy question and it is not a v2 question — it is a gap between the instrument and the
guideline, and the 97 emptied rows are what it costs on exactly the class the guideline wrote
that clause for: `Так`, `+`, a two-word answer to a poll. Adding the post makes the prompt agree
with the law the gold was written under; it does not widen the law.

**Now, before the anchor and the retrain.** Three reasons, in the order that decides it:

1. **`T1v2` has no recorded run.** No record in `results/baselines.json` carries `T1v2` in its
   `prompt_sha256` map — every one is `{T1, T2}`. Its hash is pinned only as a bystander field in
   `results/relabel_45e.json` and `results/relabel_probe_45d.json`, which is why the revision is
   registered **beside** it and never over it: those two records must keep verifying.
2. **The fresh G1c anchor has not been taken.** SPEC amendment 3.8's v2 anchor and the retrain
   after it are both still ahead. Moving the prompt now costs nothing; moving it after the anchor
   would invalidate the anchor and the training set built against it (SPEC §7 — the prompt is part
   of the measurement).
3. **The 97-row class cannot be labelled without it.** `Так` under an invisible post has no
   labelable content. No amount of re-asking the same prompt recovers it.

**Registered beside, never instead.** `TASKS` stays `("T1", "T2")` — a third member would make
every stored record fail `records.assert_prompt_sha`. The three with-post prompts get their own
keys and their own SHA256s, the four existing prompts keep theirs byte for byte, and a test reads
the `prompt_sha256` maps out of `results/relabel_45e.json` and `results/relabel_probe_45d.json`
and requires the checkout to still reproduce them.

**A missing parent is a STOP.** The guideline's claim that every parent is stored is checked, not
trusted: the lookup refuses a comment whose `(channel, parent_msg_id)` is not in
`data/raw/posts/`, rather than quietly rendering a prompt without the post it promises. Measured
before the decision: **0 of 97** and **0 of 1,912** are missing. A parent that exists but carries
no text (a media-only post) is a different state and is rendered as such — 23 of the 97 and 424
of the 1,912 — because an empty tag would read as "the post said nothing".

## (b) The 97: the with-post model first, the operator only if it fails

**Re-asked, not handed over.** The 97 go through the with-post re-labeller (~$0.02) and land in
the staged `_tax2` files through the `fixes`-block provenance pattern that
`scripts/apply_calibration_rulings.py` established: the drift block of `results/relabel_45e.json`
is what the calibration judged and is never recomputed.

**A row already under an operator ruling is never overwritten.** Two of the three 4.5f rulings
(`@VARUS_channel:11960`, `:11972`) are in this class by construction. They are re-asked — what the
with-post model says about a row the operator has already decided is free evidence — and their
answer is recorded, never written. The hold is derived from the data (a row whose staged label
differs from what the 4.5e run produced), so a fourth ruling applied later is protected without
editing a constant.

**The check on the batch is pre-registered here, before the requests go out.** A seeded 40-of-97
contrastive sample (`intents_v1` against the with-post set, verdict `old` / `new` / `neither`).
**`new` / 40 ≥ 0.90 accepts all 97; below the bar, all 97 go to the operator by hand.** Two
readings of the awkward cell are settled in advance rather than after the counts land:

- a row whose with-post set **equals** its v1 set counts as **`new`** — the model recovered the
  annotator's label, which is the thing being tested. The operator sees two identical cells and
  the README says so; the count of such rows is reported separately in the manifest's composition
  block, so `new / 40` is recomputable from the rule alone.
- a blank cell counts as **not `new`**, the same direction the 4.5e denominator counts a blank.

## (c) The up-label goes ahead: all 1,912, under a full-field v2 precheck

[[taxonomy-v2-relabel-and-appetite]] §(a) took the whole labelable pool as the appetite and made
it conditional on this gate. The gate passed, so the pool is labelled — but as a **precheck the
operator calibrates**, not as labels. The precheck asks all four comment fields (`sentiment`,
`sarcasm`, `intents` over the six v2 classes, `unclear`) with the parent post, writes
`annotator: "llm-precheck"`, and **merges into no train file** until the strata gates pass.

`unclear` is asked rather than defaulted: 37% of the labelled corpus carries it, and writing
`false` into 1,912 rows would be a coercion of exactly the field that decides whether a row is
scored at all. Asking it needs a prompt that does not exist under v1, so the full-field precheck
prompt is new rather than a revision — it is registered with the other two and hashed the same
way.

**The calibration is three strata of 100, gated per stratum at ≥90%, row-level.** A row is
`correct` only if **every** field is correct; (a) service-rich, (b) short text ≤30 characters —
the class this phase just proved is the weak one — and (c) general. A stratum below the bar sends
its whole batch back, and that second-round rule is registered before handover with the
denominators. The pack is one shuffled file: nothing in it says which stratum a row is in, and
the map lives in the manifest, for the reason `scripts/build_calibration_pack.py` states — a pack
that describes its own composition is not blind.

## What this does not decide

Test v4, the 54 ids with two homes, the fresh with-post G1c anchor, the retrain and the bars that
have to be set before anything is scored are 4.5h and are not touched here
([[phase4-gate-verdict]] closed the Phase 4 gates on the v1 taxonomy). Nothing merges into any
train or candidates file in 4.5g.
