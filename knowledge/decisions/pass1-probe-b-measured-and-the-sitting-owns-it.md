---
type: decision
date: 2026-08-18
status: accepted
tags: [decision, phase6, comment-signals, pass1, stop-rule, architecture, decomposition, money]
---

# pass 1 is MEASURED, bar P1 is 9 of 14 against 12, and the sitting owns the next move

**The record debt of the accepted step.** `pass1-probe-b` completed: 64 of 64 units read, every
bar computed, the pod deleted by the runner itself. The bar FAILED and the pre-registered clause
fired. This record states what was decided; the argument is in `docs/reports/pass1-probe-b.md`
and is not re-run here.

## What the run measured

Verdict `results/pass1_probe_b_verdict.json` (`4f3a0cbf226a06a8…`), rows
`results/pass1_probe_b_rows.jsonl`, run record `results/pass1_probe_b_run.json`, registration
`results/prereg_pass1_probe_b.json` — frozen at the first `pod create` of the attempt.

| | reading |
|---|---|
| bar **P1** `per_comment_agreement` | **FAIL — 9 of 14 agreed** against a threshold of 12; disagreed 5, absent 0, losses 5 of a budget of 2 |
| rows agreed (row-level, non-gating) | 12 of 14 |
| refusals | **0 of 64** — every reply a single balanced object, `finish_reason: stop` on all 64 |
| per call | 5.162 s · 42.19 completion tokens · **0.81×** the registered bound, **1.76×** the fitted line |
| outcome | **STOP**, return-to-sitting clause armed |

**The failure is one field.** All five losses are `subject_type`; `stance` is scored on three rows
and is right on all three. Two of the five are rows the model declined to type at all
(`subject_type: null`) — an abstention, not a parse failure, and the census says the same at scale:
**25 of 50 neighbour rows carry no `subject_type`** with zero refusals behind it. The vocabulary was
never the obstacle: `категория_личное` is offered by the prompt and five rows agreed on it.

**The transport is settled and is not the question.** Gate 0 went **GO at 14.5 s** with 165.5 s of
its dead-man unused — the third consecutive GO on this stack. Boot **237.2 s**, inside the ceiling
raised to 420 s, and the stack's three measured boots now span 192.13 / 237.2 / [267, 293] s — a
**1.53× spread that is registered, never averaged**. One segment, no recreate, `DONE` on its own.
The run cost **$0.135050** of the $0.20 cap over 657.0 billed seconds.

## What was decided

1. **The step is ACCEPTED as an honest negative.** The registration's one-attempt clause is spent.
   No prompt iteration, no parser change, no re-scoring, no v2 of the same instrument.
2. **The next move belongs to the SITTING**, by the clause the registration carries in as many
   words: *a failed bar goes back to the sitting, never to a prompt iteration*. The two branches
   the sitting weighs are **B** — labelled `subject_type` + LoRA — and **C** — another base. This
   record does not choose between them and nothing in this contract may.
3. **The window's pass-1 floor is on the record**: 1 032 payable comments × 5.162 s = 5 327 s =
   **$1.0950** of generation at $0.74/h, with no boot, no staging and no second pod inside it. It is
   a floor and the number a window-wide pass 1 is judged against.
4. **The money debt is carried NAMED, not closed.** `pass1-probe` may be closed only on a COMPLETE
   pod-scoped walk of ~427 000 ms; it read **300 000 ms** at acceptance and still reads 300 000 ms.
   `pass1-probe-b`'s own ledger stays OPEN. Both closes belong to the `--until` contract, which is
   where the guard's missing end bound is fixed — `docs/reports/guard-until.md`.

## What this record does not say

The reader's prompt-engineering programme was already closed by its own stop-rule
([[reader-programme-closed-and-the-architecture-sitting-17-08]]); this is the first measurement
*after* that closure and it does not reopen it. `pass1-probe` stays FROZEN and is not withdrawn:
its instrument was never exercised, which is why `pass1-probe-b` re-registered rather than revised.
