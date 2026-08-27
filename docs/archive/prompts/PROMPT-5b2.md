# PROMPT 5b.2 — the batch measurement: does greedy survive N>1 on this stack?

This file is the whole brief. Law: docs/SPEC.md §3.11 (2), the **batch
measurement pre-registration** added 2026-08-06 — ladder, selection rule,
one attempt, $2.77 hard stop all live there. Baseline to beat nothing:
`results/parity_5b_a.json` is the batch-1 anchor, and its committed per-row
dump makes row-level agreement reportable this time. Read-back before
coding: one line each — the ladder, how the candidate N is picked, the
adoption rule, the stop, and what stays batch 1 forever.

## Step 0 — commit the team-lead tail

By path: docs/SPEC.md, docs/STATUS.md, docs/PROMPT-5b2.md. Vault tail
(hot.md, daily log, index) — its own commit, pre-authorised. STOP only for
unexplained paths. ADR for the batch ruling lands at the END of this phase
with the measured numbers in it (the decision record without its numbers
would be furniture).

## Deliverable 1 — batched generation behind the same door

Extend the serving path (`market_pulse.local_llm` / `scripts/serve_handler.py`)
to batched greedy generation. Two guards, both as tests:
- batch=1 through the NEW code reproduces the recorded 5b.1 smoke outputs
  byte-for-byte (the batch-1 path must not move — SPEC);
- padding correctness: left/right padding and attention masks such that a
  row's output does not depend on its neighbours' lengths in the trivial
  cases the test can pin (same-length rows batched vs solo).

## Deliverable 2 — the carve ladder (free of test exposure)

On the pod, smoke the 24-row arm-A carve at N ∈ {16, 8, 4} plus the batch-1
reference. Candidate N = the largest whose outputs are BYTE-IDENTICAL to
batch-1; none identical → candidate is 8 (SPEC). Record the ladder outcome
(per-N identical yes/no, wall s/row) in `results/batch_ladder_5b2.json`.
Project the paid run with the existing projection instrument against the
**$2.77** stop; over → abort and report.

## Deliverable 3 — the ONE paid scoring

Test v4 once at the candidate N, same pod runtime, `assert_serving` +
`assert_runtime_matches` before the first scored row. Records:
- `results/parity_5b2.json`: per-gate heads BESIDE `parity_5b_a.json` and
  the 4.5h2 anchors, explicit deltas, the adoption rule applied AS CODE
  (`scorer.select_serving_config` family), row-level agreement % vs the
  5b.1 dump as DESCRIPTION;
- `results/serving_5b.json` updated: adopted batch, measured s/row and
  $/1000 rows at the adopted config — the numbers 5c reads;
- spend readings appended to `results/spend_5b.json`.
Verdict: adopted N or "batch 1 permanently" — either way recorded, no
retry. Delete the pod; deletion proven by listing.

## DO NOT

- No changes to gate-eval machinery: gate evals stay batch 1 (SPEC).
- No serverless. No config B. No second paid attempt at another N.
- Test v4 is opened exactly once — in the paid run.
- No team-lead file edits (docs/SPEC.md, docs/STATUS.md, docs/PROMPT-*.md,
  docs/RESEARCH-*.md, docs/CHANNELS-launch.md).

## Verify-gate (evidence, not assertions)

1. `make check` green (state the total) · `ruff format --check .` clean.
2. Both new records carry seed/config/shas/git provenance; the verdict
   names each rule condition's outcome, not just a winner.
3. Spend vs quoted RunPod balance; pod deletion by listing; `git status`
   clean; atomic commits by path.
4. Report: 3-line summary → ladder table → per-gate table (N vs batch-1 vs
   4.5h2) with row-agreement % → adopted config and its $/1000 rows →
   spend. Numbers point at artifact paths. `implementation-notes.md`
   §"Phase 5b.2" with a **Deviations** section — silence is not compliance.
