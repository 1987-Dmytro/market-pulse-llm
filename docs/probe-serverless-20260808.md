# Serverless queue-delivery probe — 2026-08-08, evening

**Run by:** team lead, live in the operator's RunPod console (Chrome), on the
operator's explicit go. **Question:** does the 5b wall — "no serverless
endpoint on this account reaches a job-consuming worker"
(`results/parity_verdict_5b.json`, 2026-08-06, 7 observations incl. RunPod's
own hub worker) — still hold today? **Answer: NO. Jobs are consumed and
complete.**

## Setup (billable life ≈ minutes, deleted after answering)

| Field | Value |
|---|---|
| Endpoint | `probe-queue-20260808`, id `8mkl2lbxho3bfa` |
| Image | `runpod/mock-worker:dev` (official RunPod test worker, 167 MB) |
| Config | Queue mode · GPU 16 GB flex · max workers 1 · no volume · no DC pin |
| Created | 2026-08-08 evening, via console wizard (Docker-image source) |

## Observations

| # | Job id | Result | delayTime | executionTime | Worker |
|---|---|---|---|---|---|
| 1 | `ab599b5b-7fe9-41e1-bc0c-4e8647f8ef55-e2` | COMPLETED, output `"Hello World!"` | 10 964 ms | 142 ms | `pri0muyf75j143` |
| 2 | `245c8d88-3134-4886-8c45-293f1b85f256-e1` | COMPLETED, output `"Hello World!"` | 6 800 ms | 144 ms | `pri0muyf75j143` (warm) |

Console showed the full lifecycle: Initializing → Ready → job IN_QUEUE →
worker running → COMPLETED. Billing meter visibly on ($0.00016/s) only while
the worker ran.

## Cleanup

Endpoint deleted the moment the question was answered (typed-name confirm in
the console). **Deletion proven by listing:** the Serverless section returned
to its zero-endpoint "Get started" state. Spend: worker minutes at
$0.00016/s ≈ $0.02–0.04; the exact figure is read from RunPod billing at the
srv-2 acceptance, not invented here.

## What this probe does NOT prove (pre-registered before srv-2)

1. Volume-attached GPU offering TODAY — D7 ("with a volume, serverless
   offers only RTX 4090 24 GB") was measured 2026-08-06 and must be re-read
   with the volume actually attached.
2. GM4 NF4 base fit + batch-1 byte-stability on whatever GPU is offered.
3. Cost per row vs the pod's measured $0.60/1000 (batch 1, A6000).
4. Longevity: n=2 on one evening says "the wall is down today", not "it can
   never return". SPEC 3.11 (2) parity (758 rows vs 4.5h2 anchors) remains
   mandatory before any production number.

**Consequences recorded in SPEC amendment 3.14.** The 5b evidence file is
untouched — it honestly describes 2026-08-06; this file describes 2026-08-08.
