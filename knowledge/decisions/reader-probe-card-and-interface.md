---
type: decision
date: 2026-08-15
status: accepted
tags: [decision, phase6, comment-signals, serving, cost]
---

# The reader probe: the card question is closed, the interface is the binding constraint

**Two paid probes on 2026-08-15, $0.4173 together, and what they settle.**
`docs/reports/probe-a.md` · `docs/reports/probe-b.md` ·
`results/prereg_reader_probe.json` · `results/prereg_reader_probe_v2.json`

## What is decided

**1. The serving card is `ADA_24`, and every rate must name the card it was measured on.**
probe-a asked for the display name «NVIDIA L4», the endpoint answered `gpuIds: AMPERE_24`, and the
worker turned out to be an L4 — a card **2.64× slower** than the `ADA_24` (RTX 4090) the
`$0.00030669/s` in every projection of this repo was actually measured on
(`docs/reports/5c2-run.md`). Same price, slower instrument, and the whole $1.87–$4.18 window
projection was a property of a card nobody chose.

probe-b requested the 4090 and read `gpuIds` back **out of the create call's own response** —
creation is free, only requests bill — before a single job existed. Measured: **20.759 s a thread**,
**5.661 s a payable comment**, against a break-even of 2.007× registered before anything was created.
The 111-thread window now prices at **$0.71 by thread / $1.58 by payable comment**.

Rule: request the CLASS id, read `gpuIds` back from the create response, take the actual card from
the worker's `runtime.gpu` (the two can disagree), and never carry a `$/s` between contracts without
the card beside it. Do NOT assert the card as a guard — arithmetic catches a slow one for free.

**2. Two of the operator's obligatory cases are only reachable past the production gate.**
SPEC 3.21 (1)'s marker rule removes E1, E4a, E4b and N3 before payment: the reader is never shown
them, so a 4-of-4 entity bar fails by arithmetic rather than by reading. probe-b bought those four
threads directly, marked `injected: true`, and they answered **2 of the 4 entity cases** — E1
«Гармонія» as `не_наш_рынок` and E4 as the absence it is, on both threads. Injected rows never enter
a production aggregate or a window price, and they cost money like any other thread.

That is the measured argument that the hygiene rule the plan calls «временная гигиена
детерминированной витрины … не закон смысла» is a **payment gate for the reader**. Whether
production should deliver those threads is the sitting's question, and it now has evidence.

**3. The binding constraint is the interface, not the reading — and it is measured, not argued.**
v2 closed both defects probe-a measured (`entities` as a map, `evidence: [null]`) and neither
returned. Ten of 23 replies were still refused, across **six other shapes of the same class**:
`"signals": {}` for an empty list (4, all of them noise threads), the answer split into two top-level
JSON objects (2), `noise` as a map keyed by msg_id (1), `aspect: null` (1), a `from_post` signal with
no `evidence` key (2). Container-only coercion — no field invented, no value changed, no taxonomy
word mapped — takes replies **13 → 19 of 23** and entity cases **2 → 3 of 4**.

The reading gap is real and smaller: coerced and with the vocabulary collapsed, the per-comment bar
is **0.643** against 0.80 and flagships **3 of 5**. **No bar clears its threshold under any reading.**

**4. A bar that counts «zero of X» is passed by a reply that could not be read.**
Bar 3 was the only gate probe-b cleared, and four of its five threads had no verdict at all. Any
future bar with that predicate must be registered over answers that EXIST, and the distinction
belongs in the bar rather than in a post-run analysis.

## What is NOT decided, and is the operator's

Four options, priced from what is now measured (`docs/reports/probe-b.md` §9):

| | cost | what it buys |
|---|---|---|
| **A** container-tolerant parser, DOMAIN strictness untouched | $0 of GPU, a day's work | +6 replies, +1 entity case. Not free: it needs a ruling on what happens when two top-level objects disagree, a re-registration of what «refused» means, and another `prompts.py` sha move through three pinned records |
| **B** a v3 prompt («ONE JSON object», «`[]` when there is nothing») | ~$0.08 + a new registration | whether the framing defects are promptable at all |
| **C** the reading gap — F1b, F1c, F2a and four absent per-comment rows in threads that PARSED | a sitting, $0 | what the reader actually misses once the interface stops accounting for most of it |
| **D** the sitting's two standing questions | $0 | the marker rule (above) and `категория` vs `категория_личное` — 8 of the 14 per-comment gold rows score on a word `docs/PLAN-comment-signals.md`'s own schema example stopped using on 2026-08-15 |

## Money, and the two readings that are not the same number

By the BILLING lines: probe-a **≈$0.075** of $0.45, probe-b **$0.31316** of $0.35 — both inside
their caps, and the serverless leg prices at **$0.0003067/s** against the **$0.00030669/s** the
registration carried, so the 5c2 prior is exact for this card.

By the BALANCE DELTA the guard uses for a step, probe-b reads **$0.4493** and REFUSES. The difference
is the 100 GB network volume, which bills ~$0.0092/h whether or not anything runs. Two rules fall out
and both are blockers, not notes:

- **a step meter built on a balance delta measures the ACCOUNT, not the step, and never stops**
  (Dv412): $0.2907 at deletion, $0.3132 at two hours, $0.4493 at thirteen. Price a step from
  `runpodctl billing <kind> --start-time <anchor>`, excluding the always-on kinds BY KIND
  ([[a-step-meter-on-a-balance-delta-never-stops]]);
- `--step` has only ONE reading where the phase takes `max(delta, billing walk)` (Dv411). Neither is
  fixed: it is a money path, and both were found by USING the guard on two consecutive mornings.

Related: [[an-absolute-bar-needs-a-reachability-state]], [[one-object-per-name-reads-as-a-map]],
[[the-setup-is-inside-the-cap]], [[5c2-closed-the-sitting-and-the-shelf-life-redesign]].
