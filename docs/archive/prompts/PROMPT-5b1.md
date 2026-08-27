# PROMPT 5b.1 — score config A once, on the pod the loop will actually use

This file is the whole brief. Law: docs/SPEC.md §3.11 (1) runtime ruling and
§3.11 (2) single-config measurement, both amended 2026-08-06 after the 5b
abort. Anchors: `results/verdict_45h2.json`. The pair stays closed: no config
B, no serverless attempt, no retry. Read-back before coding: one line each —
what is measured, on what hardware, the budget stop, and the two things that
stay dead.

## Step 0 — the owed RECORD tail, then the team-lead commit

1. ADR `5b-parity-abort-and-pod-runtime.md` + INDEX line: the abort verdict
   (aborted-runtime-unreachable → A ships, merge closed forever; numbers and
   evidence from `results/parity_verdict_5b.json`) AND the operator's runtime
   ruling (stop-after pod on AMPERE_48; serverless returns only via a fresh
   §(2) measurement; the D7 ADA_24 finding as rationale). English, vault style.
2. Update `knowledge/hot.md` curated Next — it still says PROMPT-5b is queued;
   5b is closed-aborted and 5b.1 is the measurement.
3. Commit the team-lead tail by path: docs/SPEC.md, docs/STATUS.md,
   docs/PROMPT-5b1.md. Vault tail (hot.md, daily log, index) — its own commit,
   pre-authorised. STOP only for paths neither list explains.

## The measurement (the phase's ONE paid event)

- Pod: AMPERE_48 / A6000, the `scripts/runbook_5b.md` staging — the volume
  already carries the venv, weights at the pinned revision and the arm-A
  adapter. `assert_serving` (adapter sha `b3ca6308…`, unmerged, NF4) and
  `assert_runtime_matches` (the 4.5h2 stack) must pass before the first
  scored row; a mismatch is a red gate, not a warning.
- Call path = the one production will use in 5c: the same
  `start.sh → serve_handler → market_pulse.local_llm` stack proven in 5b
  staging, batch 1, greedy, `T1v2_with_post`. Record the call path in
  `results/serving_5b.json` — that file now exists and is what 5c reads.
- Smoke first: the 24-row arm-A carve via `scripts/smoke_5b.py` (it hashes
  the carve to the adapter's recorded sha — keep that guard). Project cost
  with `scripts/parity_verdict_5b.py --project` against the **$3.47**
  remaining headroom; over → abort and report projections.
- Then test v4, once: one attempt, no retry, fixed seed. Records:
  `results/parity_5b_a.json` — per-gate-head numbers BESIDE the 4.5h2
  anchors with explicit deltas (reported, never averaged away; no bar
  moves); if any 4.5h2-passed gate head lands under its bar, say it loudly
  as its own finding — the ruling on it is an operator briefing, not this
  phase. `results/serving_5b.json` — pod config, cold-start, measured
  per-row latency and cost (the numbers 5c sizing needs). Spend readings
  appended to `results/spend_5b.json`.
- Delete the pod the moment scoring ends; deletion is PROVEN by
  `runpodctl pod list` output in the report, not by an exit code.

## DO NOT

- No serverless calls of any kind; no config B; no second attempt.
- Do not touch `run_loop.py`, the scorer's gate functions, frozen test sets,
  raw stores, aggregates, or any team-lead file (docs/SPEC.md,
  docs/STATUS.md, docs/PROMPT-*.md, docs/RESEARCH-*.md,
  docs/CHANNELS-launch.md).
- Test v4 is exposed exactly once — in the paid run; never in smoke.

## Verify-gate (evidence, not assertions)

1. `make check` green (state the total) · `ruff format --check .` clean.
2. `shasum -c results/raw_v1_baseline.sha256` → 6/6 (nothing here touches
   raw, prove it anyway).
3. Spend: `results/spend_5b.json` new readings vs the quoted RunPod balance.
4. Pod deletion shown by listing; `git status` clean; atomic commits.
5. Report: 3-line summary → per-gate table A-on-pod vs 4.5h2 anchor with
   deltas → serving figures (cold start, s/row, $/1000 rows) → spend.
   Numbers point at artifact paths. `implementation-notes.md` §"Phase 5b.1"
   with a **Deviations** section — silence is not compliance.
