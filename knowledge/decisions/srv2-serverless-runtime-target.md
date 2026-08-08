---
type: decision
id: dec-2026-08-08-srv2-serverless-runtime-target
date: 2026-08-08
status: accepted
tags: [decision]
---

# The 5b wall did not reproduce, and the production runtime target moves back to serverless

**Context:** operator ruling 23, the late evening of 2026-08-08, recorded as **SPEC amendment
3.14**. It supersedes ruling 20 ([[5b-parity-abort-and-pod-runtime]]) **as the target**, not as
evidence: the pod path stays the measured, proven fallback and its numbers stand. What changed is
not an opinion about serverless — it is a re-measurement of the one fact ruling 20 was built on.

## (1) The ruling

The production runtime target is **serverless**: the model resident on a network volume, workers
scaling to zero between passes. The economic case is the ~12 h of idle between the two collection
passes a day that SPEC 3.11 (1) fixes — a stop-after pod pays its boot twice a day and a resident
one pays around the clock, while a scaled-to-zero worker pays for neither.

**All paid 5c1 steps and the launch-composition signing are HELD** by the operator's word until
the serverless track proves out. The hold is on spend, not on $0 work.

## (2) The probe — what was actually run, by whom, and what it cost

Team lead, live in the operator's console, the same evening, on the operator's explicit go.
Record: `docs/probe-serverless-20260808.md`.

| Field | Value |
|---|---|
| Endpoint | `probe-queue-20260808`, id `8mkl2lbxho3bfa` |
| Image | `runpod/mock-worker:dev` — RunPod's own test worker, 167 MB |
| Config | queue mode · GPU 16 GB flex · max workers 1 · **no volume** · no DC pin |

| # | Result | delayTime | executionTime | Worker |
|---|---|---|---|---|
| 1 | COMPLETED, `"Hello World!"` | 10 964 ms | 142 ms | `pri0muyf75j143` |
| 2 | COMPLETED, `"Hello World!"` | 6 800 ms | 144 ms | `pri0muyf75j143` (warm) |

The 5b blocker — "no serverless endpoint on this account reaches a job-consuming worker", seven
observations including RunPod's own hub worker (`results/parity_verdict_5b.json`, 2026-08-06) —
**did not reproduce**. The billing meter ran at $0.00016/s only while the worker ran; the endpoint
was deleted the moment the question was answered and the deletion was proven by the Serverless
section returning to its zero-endpoint state.

Two consequences the operator drew and the team lead recorded:

- **The vendor ticket is unnecessary** and was closed unfiled.
- The operator's "we check now, we wait for no one" was **the correct call**, over the team lead's
  records-first recommendation to trust the 2026-08-06 evidence. A record of a blocked account is a
  record of one day; it was read as a property of the account.

`results/parity_verdict_5b.json` stands untouched. It honestly describes 2026-08-06 and is not
edited to agree with 2026-08-08 — the two files are two dates, and the pair is the finding.

## (3) What the probe does NOT prove — pre-registered before srv-2, not after

Four items, from the probe record itself. They are the reason a two-job probe re-opened a track
but did not close it:

1. **The volume-attached GPU offering today.** D7 (2026-08-06) found that with a volume attached
   serverless offered only RTX 4090 24 GB, while `AMPERE_48`, `ADA_48_PRO` and `AMPERE_80` produced
   no worker. The probe carried **no volume**, so it says nothing about this. A re-read is required.
2. **GM4 NF4 fit and batch-1 byte-stability** on whatever GPU is offered. The model sits at ~20 GiB
   at rest; on a 24 GB card the headroom for KV cache and activations is a measurement, and no
   peak-VRAM figure for batch-1 inference exists in any record.
3. **Cost per row** against the pod's measured $0.5993/1000 (`results/serving_5b.json ::
   adopted.usd_per_1000_rows`, batch 1, A6000).
4. **Longevity.** n=2 on one evening says "the wall is down today", never "it cannot return".

SPEC 3.11 (2) parity — 758 rows of test v4 against the 4.5h2 anchors, batch 1, one attempt —
remains **mandatory before any production number**, unchanged by 3.14.

## (4) The program

- **srv-2a** — executor, $0, local: the serverless worker config reusing the 5b entrypoint proven
  on the pod (`scripts/serve_handler.py` + `scripts/start_5b_worker.sh`), the volume re-creation
  plan, and the runbook `scripts/runbook_srv2b.md`. Executed and accepted the same evening; the one
  code change it demanded was that the worker report the peft that applies the LoRA, since the
  4.5h2 anchor pins no peft field and `assert_runtime_matches` therefore cannot.
- **srv-2b** — one paid session, cap set at its briefing (**$4.00**, `docs/PROMPT-srv-2b.md`):
  volume + weights + endpoint + smoke + the D7 re-read + parity, with the abort ladder in force and
  no rung authorising a retry.

The caption instrument of amendment 3.13 is unchanged, and the vis-a code is runtime-agnostic and
rides along.

## Consequences

- Ruling 20's pod runtime is **not** withdrawn. It is the fallback, and it is the only runtime this
  project has ever scored a full test set on.
- The volume becomes a run-rate line again. Its price is **read from the console at creation** and
  recorded; the repo's $7.20/month and ~$0.24/day are priors and are labelled as such.
- If srv-2b hits any rung of the ladder, the target does not silently revert — the finding goes to
  an operator briefing, because 3.14 is a ruling and only a ruling replaces it.

Related: [[5b-parity-abort-and-pod-runtime]] · [[5b2-batch-measurement]] ·
[[phase4-own-pod-anchor]] · [[gpu-provider-runpod]].
