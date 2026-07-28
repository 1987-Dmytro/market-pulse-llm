---
type: decision
id: dec-2026-07-28-holdout-residual-thread-leak-accepted
date: 2026-07-28
status: accepted
tags: [decision]
---

# Residual holdout/train thread overlap accepted

**Context:** wave-1 mining excluded test threads only, so its rows are spread through threads the
holdout also draws from. Step 2g was scoped to removing the moved rows from training and nothing
else, so part of that overlap survived the freeze.

**Decision (operator, 2026-07-28):** accepted. The affected holdout rows stay; the risk is
recorded here rather than closed. Compensation is widening the sarcasm data available for
*training* (source under discussion), not shrinking the holdout.

**Numbers:** 25 holdout threads still hold a scoreable row of the mined training pool, covering
31 of the 108 holdout rows (28.7%); the other 77 rows are thread-clean. Unaffected: 0 threads
shared with the test set, 0 threads shared with the scoreable train pool, 0 ids in common with
any training file, 0 verbatim text overlap with any remaining training row.

**Why (operator's rationale):** the classifier is fed the comment text alone — no thread context,
no sibling comments — so a thread-mate in training carries no label information about a holdout
row. The overlap is a provenance smell, not a label leak.

**Alternatives rejected:** dropping the 31 rows (holdout falls to 77, and G1b's slice with it) ·
pulling the mined thread-mates out of training (costs training data on the exact axis G1b
scores, and the change was not in scope).

**Sources:** docs/frozen-testsets.md, "Leakage, and the one residual" · docs/STATUS.md,
"Решения ревизии подхода (2026-07-28)" · related [[hybrid-sarcasm-holdout-3.2]].
