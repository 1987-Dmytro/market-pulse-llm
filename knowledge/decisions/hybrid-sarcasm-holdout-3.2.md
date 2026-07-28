---
type: decision
id: dec-2026-07-28-hybrid-sarcasm-holdout-3.2
date: 2026-07-28
status: accepted
tags: [decision]
---

# Hybrid sarcasm holdout for G1b (amendment 3.2, option 1a)

**Context:** G1b in rev. 3 needed 150–200 curated sarcastic examples the base model gets wrong.
The frozen test set holds 52. Wave-2 mining then showed the corpus cannot supply a fresh-only
holdout: every comment in a thread disjoint from test and train had already been mined or does
not exist.

**Decision (operator, 2026-07-28, option 1a):** freeze a hybrid holdout at
`data/frozen/sarcasm_holdout.jsonl` — fresh-corpus sarcastic rows topped up with rows *moved out*
of the mined training pool, removed from training rather than copied. SPEC amendment 3.2 makes
the G1b slice the subset of the holdout the zero-shot base model misclassifies at Phase 3, with
the gate arithmetic unchanged (≥60% fixed, ≤2 pp overall macro-F1 loss) and a recorded fallback:
below 100 slice rows, the smaller n is reported next to the verdict.

**Numbers:** mining funnel 7,224 comments with text → 4,424 unlabelled → 1,068 outside test and
train threads → 971 candidates, all labelled; 54 sarcastic and scoreable (5.6%, against the
15–25% expected). Of the 187 sarcastic scoreable mined rows only 54 were movable — 131 share a
thread with a scoreable train row and 2 repeat a training row's text. Holdout: 108 rows
(54 fresh + 54 moved), ua 66 / ru 29 / other 13, 107 negative + 1 positive, sha256
`f83a6cf0fecd…`. The mined pool drops 800 → 746 rows; training keeps 230 sarcastic scoreable rows
(97 + 133).

**Why:** the fresh corpus is exhausted, and rows that move out of training can be scored without
leaking. The binding constraint was never the labelling yield — it was the top-up.

**Alternatives rejected:** relaxing thread-disjointness from the train pool (would raise the
ceiling to ~180 but permanently weakens every G1b number and cannot be undone after training) ·
collecting more corpus (reopens Phase 2) · leaving G1b unmeetable as written.

**Sources:** docs/SPEC.md amendment 3.2 and §5 · docs/frozen-testsets.md, "Sarcasm holdout (G1b)"
· [[2026-07-28]] · related [[holdout-residual-thread-leak-accepted]].
