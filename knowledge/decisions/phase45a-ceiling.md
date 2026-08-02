---
type: decision
id: dec-2026-08-02-phase45a-ceiling
date: 2026-08-02
status: proposed
tags: [decision]
---

# The 4.5a ceiling: 244 blind verdicts, and what each head can score at best

**Context:** SPEC amendment 3.7 opened Phase 4.5 because the operator's 0.98 target sits above the
instrument — comment gold was calibrated at 96.3% agreement, and no model can score above the gold
it is scored against. 4.5a measured that ceiling instead of arguing about it: every disagreement
between the deliverable arm ([[phase4-gate-verdict]], real-only) and gold was put to the operator
with the two candidate labels blinded, and a control sample of rows where both *agreed* was put to
the same judgement. The operator ruled 244 rows; this record holds what the approved harness
printed over them. **Numbers only — the 4.5a gate review decides what follows from them.**

## (a) What was ruled

| file | rows | verdicts |
|---|---|---|
| `comments_sentiment.csv` | 35 | A 19 · B 16 |
| `comments_intents.csv` | 67 | A 32 · B 33 · ambiguous 2 |
| `slice_unfixed.csv` | 23 | A 3 · B 20 |
| `posts.csv` | 15 | A 7 · B 8 |
| `control.csv` | 104 | correct 81 · incorrect 23 |

`A` / `B` name columns, not sides: which column held the model's label was a per-row seeded coin
flip, and the key that maps them back was sealed outside the operator's folder for the whole
adjudication. The returns were normalized into the pack by `scripts/normalize_audit_returns.py`,
which changes the verdict column and proves it changed nothing else.

## (b) The disagreement stratum — fully observed

| head | gate | n scoreable | disagreements | gold wrong | model wrong | ambiguous |
|---|---|---|---|---|---|---|
| sentiment | G1a | 400 | 35 | 15 | 20 | 0 |
| intents | G1c | 400 | 67 | 31 | 34 | 2 |
| sarcasm_pair | G1b | 44 | 23 | 15 | 8 | 0 |
| post_type | G1d | 250 | 11 | 5 | 6 | 0 |
| brands | G1e | 250 | 4 | 3 | 1 | 0 |

## (c) The agreement stratum — seen through the control sample

| head | agreements | control n | correct | incorrect | ambiguous | gold-error rate |
|---|---|---|---|---|---|---|
| sentiment | 365 | 40 | 40 | 0 | 0 | 0.000 |
| intents | 333 | 40 | 18 | 22 | 0 | 0.550 |
| sarcasm_pair | 21 | 8 | 8 | 0 | 0 | 0.000 |
| post_type | 239 | 8 | 8 | 0 | 0 | 0.000 |
| brands | 246 | 8 | 7 | 1 | 0 | 0.125 |

22 of the 23 `incorrect` verdicts fall in one head. The rate is extrapolated over the whole
agreement stratum, which is where the estimate's uncertainty lives — see (e).

## (d) The ceilings, as printed

| head | metric-unit ceiling (upper bound) | accuracy-unit band | sensitivity: control incorrect → accuracy (high) |
|---|---|---|---|
| sentiment | **0.9613** macro-F1 | 0.9625 .. 0.9625 | 0→0.9625 · 1→0.9397 |
| intents | **0.9148** micro-F1 | 0.4596 .. 0.4646 | 21→0.4854 · 22→0.4646 · 23→0.4438 |
| sarcasm_pair | **0.6591** fix-rate | 0.6591 .. 0.6591 | 0→0.6591 · 1→0.5994 |
| post_type | **0.9683** macro-F1 | 0.9800 .. 0.9800 | 0→0.9800 · 1→0.8605 |
| brands (G1e) | *0.9600 F1* | *0.8650 .. 0.8650* | *0→0.9880 · 1→0.8650 · 2→0.7420* |

The accuracy band collapses to a point wherever both ambiguous counts are zero, which is every head
but `intents`; it is not a missing number.

**G1e is excluded from the ceiling arithmetic** (team-lead decision, 02.08). Its row is in italics
because the harness prints every head; G1e's contribution to this record is the raw verdict counts
in (b) and (c) — 4 disagreements and an 8-row control — and nothing computed from them.

## (e) The formula's assumptions, verbatim from the harness

```
ASSUMPTIONS — this is a formula, not a measurement of the truth
  1. A perfect model outputs the truth, so it loses exactly the rows where gold
     is not the truth. The ceiling is 1 minus that share.
  2. Disagreements are fully observed: gold-wrong there is a count.
  3. Agreements are seen only through the control sample, so their gold-error
     share is EXTRAPOLATED over the whole stratum. That stratum is most of the
     test set and the sample is a few dozen rows — the sensitivity line below
     shows what one more `incorrect` does to the number.
  4. Ambiguous rows are a band, never a point: a perfect model may lose all of
     them (low) or none (high).
  5. WHAT THIS CANNOT SEE: rows where the model and gold are wrong the SAME way
     and that the control sample did not draw. Nothing flags such a row, and the
     only estimate of them is the control's `incorrect` rate in (3).
```

The blind spot in (5) is the reason the control sample exists at all, and the reason its `n` bounds
what this record can claim: a head's agreement stratum is 21–365 rows and its control is 8 or 40.

And the units, verbatim:

```
The two ceilings are in different units and do not bound each other. A macro-F1
bar and an accuracy share are not comparable: put the target in the head's own
unit before reading either against 0.98.
```

The metric-unit column re-scores a simulated perfect model — gold everywhere except the rows the
operator ruled for the model — through `src/market_pulse/scorer.py`, the same judge the gates use.
It is an upper bound: it cannot see the agreement stratum at all.

## (f) Provenance

| what | sha256 / id |
|---|---|
| arm | real-only @ `2026-08-01T18:37:47+00:00`, adapter `c0e462af81aad9f1…` |
| predictions | `results/predictions/google-gemma-4-31b-it--20260801T183747Z.jsonl` — `bdff8a4ad36b60f6…` |
| frozen | `comments_test 14b61724…` · `posts_test 183de2b5…` · `sarcasm_holdout f83a6cf0…` |
| G1b slice | `results/g1b_slice.json` — `222f1e1014808a29…` |
| blinding key | `data/annotation/audit_45a_key.json` — `67bc859658f3663f…` (verified by the harness at run time) |
| raw returns | `comments_sentiment c590192f…` · `comments_intents e1333a8a…` · `slice_unfixed 6f0fd7dd…` · `posts e254499a…` · `control 4410090f…` |
| normalized pack | `comments_sentiment d63899e8…` · `comments_intents e910d591…` · `slice_unfixed 11c3f941…` · `posts 534d36da…` · `control 19cfad71…` |
| records | `results/audit_45a_manifest.json` (pack, built at `f1a1221`) · `results/audit_45b_returns.json` (normalization, at `62784c8`) |

Full digests are in those two files; the pack builder is `scripts/build_audit_pack.py` (seed 42) and
the harness is `scripts/audit_ceiling.py`.

Related: [[phase4-gate-verdict]] — the arm these disagreements come from.
