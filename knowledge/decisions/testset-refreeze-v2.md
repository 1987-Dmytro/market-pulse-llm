---
type: decision
id: dec-2026-07-27-testset-refreeze-v2
date: 2026-07-27
status: accepted
tags: [decision]
---

# Test-set refreeze v2 — 11 operator-approved corrections

**Context:** frozen test sets are immutable without operator approval. A second, independent
operator pass over the frozen comment test set found label errors of one kind: sarcasm and
negativity under-flagged. No baseline number existed yet.

**Decision:** apply the 11 corrections and refreeze as v2, by `scripts/refreeze_v2.py`, kept in
the repo so the v1→v2 diff has provenance instead of being a hand edit. After v2 the set is
immutable again.

**Numbers:** 10 rows fixed in place (8 × sarcasm, 1 × sentiment, 1 × both). The 11th,
`@msuaaaa:9534`, became `unclear` and could not stay in a test set the guideline keeps clear of
unclear rows: it moved to the train pool and `@msuaaaa:12604` replaced it, seed 42, same stratum,
the only scorable row of its thread. Test stays 400 rows, train 1600, sarcastic rows 43 → 52,
`unclear` in test 0, shared threads 0. sha256 `14b6172472e4…`.

**Why:** corrections before baselines are free; after them they invalidate every published number.

**Alternatives rejected:** leaving the errors in place · rebuilding the split from the corrected
batch — a fresh draw differs from v2 by 8 of 400 rows, so the freeze would not have been the same
set.

**Sources:** docs/frozen-testsets.md changelog · scripts/refreeze_v2.py · related
[[train-recalibration-v2]].
