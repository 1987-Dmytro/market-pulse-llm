---
type: decision
id: dec-2026-07-27-train-recalibration-v2
date: 2026-07-27
status: accepted
tags: [decision]
---

# Train sources recalibrated to the v2 sarcasm reading

**Context:** the v2 corrections landed on the test set only, which left the training data
measurably worse labelled than the test set on the very axis G1b scores.

**Decision:** re-read every scoreable `sarcasm: false` row of both train sources that fires the
irony heuristics of `market_pulse.sarcasm`, under the v2 calibration, in chunks of 100 with the
validator after each; changed rows carry `annotator: "llm-recheck-v2"`. Separately, sync the 11
test corrections upstream into `comments_batch.jsonl` so a forced rebuild cannot resurrect a
pre-v2 label.

**Numbers:** 908 candidates → 97 rows changed (60 in `comments_train.jsonl`, 37 in
`sarcasm_candidates.jsonl`); sarcastic rows 37 → 97 and 178 → 215; the sarcastic share of the
scorable train pool 4.1% → 10.7% against 13.0% in test. The pass is one-sided by construction —
only `sarcasm: false` rows were examined, so the number measures the gap narrowing, not agreement.

**Why:** training and test must be labelled the same way on the axis a gate scores, and the test
set is the authority when they disagree.

**Alternatives rejected:** recalibrating the test set instead (immutable) · leaving the gap and
reporting it at Phase 4 · re-reading the whole train pool (cost without evidence of error in the
`sarcasm: true` direction).

**Sources:** docs/frozen-testsets.md changelog · scripts/sync_batch_v2.py · related
[[testset-refreeze-v2]].
