# PROMPT 5b — serving parity: the pre-registered pair on the production runtime

This file is the whole brief. Read ALSO: docs/SPEC.md §3.11 (2) **as amended
2026-08-06** — the pair, the selection rule, the $4 hard stop live there and are
LAW for this phase. Anchor numbers come from `results/verdict_45h2.json`; the
deliverable model is the 4.5h2 arm-A adapter (`results/train/45h2-arm-a/`, sha
`b3ca6308…`) over the NF4 base, rendering `T1v2_with_post`, greedy, batch 1.
`src/market_pulse/scorer.py` is the single judge of every number.

Read-back check before coding: state in one line each — the two configs, the
selection rule, the abort rule, and the one thing 5b must NOT wire up.

## Step 0 — commit the team-lead tail (by path, never `git add -A`)

docs/SPEC.md, docs/STATUS.md, docs/PROMPT-5b.md, docs/CHANNELS-launch.md.
The vault tail (knowledge/hot.md, today's daily log, knowledge/index.md) is
pre-authorised as its OWN separate commit. STOP and report only for paths
neither list explains.

## Deliverable 1 — config A endpoint (the 4.5h2 replica, production runtime)

RunPod **serverless** endpoint serving: NF4 base + UNMERGED arm-A adapter,
batch 1, greedy, `T1v2_with_post`. Before the first paid call:
`results/spend_5b.json` spend anchor is written (pattern of the existing
`results/spend_*.json`). Smoke = 8 rows drawn from the train carve
(`carve-758`) — NEVER from test v4 (no test exposure outside the one paid
run). Record `results/serving_5b.json`: endpoint id, image, dtype, quant
config, adapter sha, batch, and the smoke's latency/cost figures — this file
is what 5c reads to flip `run_loop.ENDPOINT`.

## Deliverable 2 — config B artifact (merge → requantize)

Merge the adapter into the bf16 base, REQUANTIZE to NF4 (bf16 serving does
not fit the GPU class — SPEC names this), package for the same serving image.
Record the merged-artifact sha and the merge/requant tool versions. Same
8-row carve smoke. The merge job's GPU time counts against the $4 stop.

## Deliverable 3 — the paired measurement (the phase's ONE paid event)

Score test v4 through the production endpoint for A and for B: one attempt
each, batch 1, fixed seed, no retries — a crashed or aborted run closes the
merge question in favour of A (SPEC). Records `results/parity_5b_a.json` and
`results/parity_5b_b.json` carry per-gate-head numbers BESIDE the 4.5h2
anchors with explicit deltas; `results/parity_verdict_5b.json` applies the
SPEC selection rule mechanically (code, not prose) and names the shipped
config. Abort rule: if the smoke projects the pair over **$4**, stop before
the paid run and report projections instead.

## DO NOT

- Do not edit docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*.md,
  docs/RESEARCH-*.md, docs/CHANNELS-launch.md — team-lead files.
- Do not touch `run_loop.ENDPOINT` (stays None; 5c flips it after
  acceptance), the scorer, frozen test sets, raw stores, aggregates.
- No batch>1 anywhere (greedy is not batch-invariant on this stack).
- No retries, no second attempts, no config C.

## Verify-gate (evidence, not assertions)

1. `make check` green (state the new total) and `ruff format --check .`.
2. `results/spend_5b.json` totals match the RunPod billing figure — quote it.
3. Both parity records carry seed, config, shas, git provenance; the verdict
   record names the selection-rule outcome per condition, not just a winner.
4. `git status` clean; atomic commits by path.
5. Report: 3-line plain summary → per-gate table A vs B vs 4.5h2 anchor →
   verdict → spend. Numbers point at artifact paths.

`implementation-notes.md` gets a "Phase 5b" section with a **Deviations**
heading — every departure logged and cited; silence is not compliance.
