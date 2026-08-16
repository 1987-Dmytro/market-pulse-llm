---
type: decision
date: 2026-08-16
status: accepted
tags: [decision, serving, latency, cost, deferred]
---

# Serving latency is decomposed and the cure is deferred until production

**A $0 team-lead session on 2026-08-16, no executor.** Decomposed from records already on disk:
`results/serving_5b.json` · `results/serving_srv2d_smoke.json`, with the card reading from
`docs/reports/probe-b.md`. Nothing was measured for this decision and nothing was run.

## What the «cosmic» latency is made of

**1. A serverless cold start of ~239 s**, of which **~214 s is the weight load**: 62 GB of bf16
pulled and NF4-compressed on the fly. `idleTimeout: 60` then kills the worker after a minute of
silence, so **every isolated request pays the start again**. That is the whole of the four-minute
figure a single ad-hoc call shows.

**2. A decode of ~5 tok/s**, which is the research stack behaving as chosen: bnb-NF4 plus an
UNMERGED LoRA plus HF `generate` at batch 1 (SPEC 3.11 (2)). The batch-1 pin was taken deliberately
in 5b for parity cleanliness — see [[5b2-batch-measurement]] — and it is the reason the number is
what it is, not evidence that anything is misconfigured.

**3. Neither the runtime nor the card is the culprit, and that is measured.** A warm row costs
**4.07 s on a pod against 4.10 s on serverless** — the same row, two runtimes, no difference worth
naming. The card question was settled separately: the **4090 is the measured price/speed leader**,
2.64× the L4 at the same $/s ([[reader-probe-card-and-interface]]). A warm queue adds ~1 s.

So the cost sits in the weight load and the decode stack, not in the platform choice
[[srv2-program-close]] made.

## The two cures, explained to the operator and not bought

| cure | what it changes | what it costs |
|---|---|---|
| a **pre-quantised base** instead of on-the-fly NF4 | cold start ~239 s → **~1 min** | staging work; the load stops being the dominant term |
| **merge the adapter + vLLM**, under a fresh pre-registration | row **< 1 s**, a thread ~**5 s** | a new registration and a new parity measurement — merging is closed today by [[5b-parity-abort-and-pod-runtime]] |

## The ruling — operator, 2026-08-16

**The cure is DEFERRED until the system is being readied for production** («пока отлаживаем»).
Runtime and cards stay exactly as they are: serverless per SPEC 3.14, classification on class
`AMPERE_48`, the reader on the 4090.

**The unblock criterion is the operator's own word — «готовим прод»** — expected at the entry to
Phase 7 / packaging. It is a criterion and not a date, which is what keeps this on the deliberate-
deferral list rather than in a backlog.

**Until then the accepted price is stated rather than rediscovered:** windows and history run on the
current stack at ~4.1 s a row and 21–32 s a thread, and an isolated single request carries the ~4 min
cold start. That is the price of debugging, not a defect in the configuration — and writing it down
is the point, so the next reader who meets a four-minute reply does not open an investigation into a
question this session already answered.

**No budget line was opened in this session.** The $20 cycle-2 line was opened later the same day, by
the reader sitting — [[reader-sitting-16-08]].

Related: [[architecture-stack]], [[5b-parity-abort-and-pod-runtime]], [[srv2-program-close]],
[[reader-probe-card-and-interface]].
