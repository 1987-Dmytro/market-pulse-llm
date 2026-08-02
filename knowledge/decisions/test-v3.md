---
type: decision
id: dec-2026-08-02-test-v3
date: 2026-08-02
status: proposed
tags: [decision]
---

# Test set v3: 38 blind verdicts applied, and what they do not reopen

**Context:** [[phase45a-ceiling]] measured how often gold is wrong. Gate 4.5 (operator, 2026-08-02)
approved the obvious consequence for the rows where the answer is already known: the 38
disagreements where the operator, ruling blind, chose the deliverable arm's label over gold's. This
record is what was built from that decision — the fixes, their provenance, and the re-scores of
every run that still has a per-row dump.

**Decision (gate 4.5):** v3 is three NEW files beside v2; v2 is immutable forever; `intents` is not
touched, pending the annotation-law review; every existing number keeps its version.

## (a) The 38 fixes

| head | gate | rulings applied | what a ruling rewrites |
|---|---|---|---|
| sentiment | G1a | 15 | `sentiment` |
| sarcasm_pair | G1b | 15 | the `sentiment` + `sarcasm` pair |
| post_type | G1d | 5 | `post_type` |
| brands | G1e | 3 | `brands` |
| **intents** | G1c | **31 derived, 0 applied** | — law pending |

| file | rows | rows changed | sha256 |
|---|---|---|---|
| `data/frozen/comments_test_v3.jsonl` | 400 | 15 | `d993ca6ff057060e…` |
| `data/frozen/sarcasm_holdout_v3.jsonl` | 108 | 15 | `9164d6f9aad24a46…` |
| `data/frozen/posts_test_v3.jsonl` | 250 | 7 | `a476414e26c410c1…` |

37 distinct rows carry 39 field-level changes for 38 rulings: `@msuaaaa:9676` is ruled under two
heads, and 13 of the 15 pair rulings confirm `sentiment` while moving only `sarcasm`. Every changed
row carries `annotator: "operator-blind-audit-45a"`. The per-id changelog is in
`docs/frozen-testsets.md` and, machine-readable, in `results/frozen_v3.json`.

Derived by `scripts/freeze_testsets_v3.py` from the sealed key and the arm's dump — no hand edits.
The count is pre-registered in the script: a derivation that does not yield 15/15/5/3 stops instead
of writing. Every row that took no fix is re-serialised and required to reproduce its v2 line byte
for byte.

## (b) What v3 does not reopen

- **Phase 4's Tier-1 verdict — 2 of 5 — stands.** It was decided once, against v2, under the
  one-attempt protocol ([[phase4-gate-verdict]]). The v3 numbers below are program measurements of
  a corrected instrument, not gate results, and they live in `results/rescores_v3.json`, never in
  `results/baselines.json`.
- **No bar moves.** The bars are derived from the own-pod anchor's v2 record
  ([[phase4-own-pod-anchor]]); nothing in v3 re-derives them.
- **v2 keeps its hashes**, so every published number keeps meaning what it meant.
- **`intents` is byte-identical to v2 in v3.** The operator ruled for the arm on 31 intents
  disagreements; none is applied while the control sample's reading of the head is undecided
  ([[phase45a-ceiling]] §(c): 22 of 40 agreed rows ruled wrong, 19 of them agreed on `[]`).

## (c) Every dumped run, v2 → v3

| head | own-pod base v2 → v3 | arm A (real-only) v2 → v3 | arm B (with-synthetic) v2 → v3 |
|---|---|---|---|
| G1a overall | 0.8918 → **0.9067** | 0.9107 → **0.9499** | 0.9172 → **0.9456** |
| G1a ua | 0.8918 → **0.8944** | 0.9146 → **0.9511** | 0.9171 → **0.9469** |
| G1a ru | 0.8849 → **0.9297** | 0.8919 → **0.9584** | 0.9364 → **0.9590** |
| G1c | 0.7936 → **0.7936** | 0.8212 → **0.8212** | 0.8073 → **0.8073** |
| G1d post_type | 0.9084 → **0.9190** | 0.9386 → **0.9705** | 0.9159 → **0.9357** |
| G1d relevance | 0.9415 → **0.9415** | 0.9894 → **0.9894** | 0.9891 → **0.9891** |
| G1e | 0.8974 → **0.9383** | 0.9333 → **0.9744** | 0.9577 → **0.9189** |

G1c and relevance are unchanged by construction — no `intents` row and no `relevant` row was
touched. **Eight runs have no per-row dump and are not in this table**: `tfidf-logreg`, both
`qwen3.5-9b` rows, the OpenRouter `gemma-4-31b-it` row, both `qwen3.6-27b` rows, the
`claude-haiku-4.5` reference and `xlm-roberta-base`. They cannot be re-scored at any price — their
records store a hash of the scored id list, not predictions — and the script names them on every
run rather than leaving the table looking complete.

**The fixes were derived from arm A's dump.** Where the operator ruled for the arm, v3's gold now
holds arm A's own label, so arm A's v3 numbers are not independent of v3 in the way arm B's and the
base model's are. It is the same 38 rows for all three columns, and the effect has a sign: on G1e,
where 3 of the 4 disagreements were arm A's, arm A rises (0.9333 → 0.9744) and arm B falls
(0.9577 → 0.9189).

## (d) G1b, both readings

| run | v2, original slice | v3, original slice (n=44) | v3, v3 slice (n=29) |
|---|---|---|---|
| arm A (real-only) | 21/44 = 0.4773 | **36/44 = 0.8182** | 21/29 = 0.7241 |
| arm B (with-synthetic) | 24/44 = 0.5455 | **29/44 = 0.6591** | 19/29 = 0.6552 |

- **the original slice** is the pre-registered 44 ids of `results/g1b_slice.json`, re-scored against
  v3 — the reading that is comparable row-for-row with the Phase 4 verdict row, and the one the
  gate's own denominator names. Fifteen of those 44 rows had gold wrong.
- **the v3 slice** is the base model's error union recomputed against v3 from its own dump: **29
  ids**, not 44, because 15 of the base model's "errors" were gold's. A fix-rate over a different
  denominator answers a different question, so both are reported and neither is called *the* G1b.
  The 29 ids are persisted in `results/rescores_v3.json` so the reading can be re-derived.

Against the pre-registered bar of 27 of 44 (60% of the base model's own errors), arm A's v3 reading
on the original slice is 36. **This does not change the gate**: G1b failed against v2, a failed gate
closes its question (SPEC §5), and nothing is retried. What the number says is what the audit was
run to find out — how much of that failure was the instrument.

## (e) Provenance

| what | value |
|---|---|
| audit manifest | `results/audit_45a_manifest.json` (pack built at `f1a1221`, seed 42) |
| returned verdicts | `results/audit_45b_returns.json` — 244/244, five sha-pinned CSVs |
| blinding key | `data/annotation/audit_45a_key.json` — `67bc859658f3663f…` |
| arm dump | `results/predictions/google-gemma-4-31b-it--20260801T183747Z.jsonl` — `bdff8a4ad36b60f6…` |
| v2 | `comments_test 14b61724…` · `posts_test 183de2b5…` · `sarcasm_holdout f83a6cf0…` |
| derivation | `scripts/freeze_testsets_v3.py` → `results/frozen_v3.json` |
| re-scores | `scripts/rescore_v3.py` → `results/rescores_v3.json`, judge `eval_zero_shot.build_gates` |

Related: [[phase45a-ceiling]] — the ceiling these fixes came out of; [[phase4-gate-verdict]] — the
verdict they do not reopen; [[testset-refreeze-v2]] — the v2 corrections, three of which v3 amends.
