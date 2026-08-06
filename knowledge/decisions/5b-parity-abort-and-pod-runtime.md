---
type: decision
id: dec-2026-08-06-5b-parity-abort-and-pod-runtime
date: 2026-08-06
status: accepted
tags: [decision]
---

# The pair aborted on a runtime that never took a job, and production moves to a stop-after pod

**Context:** Phase 5b (`docs/PROMPT-5b.md`) was the pre-registered serving-parity pair of SPEC
amendment 3.11 (2): config A (NF4 base + unmerged arm-A adapter) against config B (the same
adapter merged in bf16 and requantized to NF4), each scored **once** on test v4 through the
production **serverless** runtime, hard stop $4.00 of the $8 Phase-5 cap. The pair was never
scored. This record carries the abort, its evidence, and the operator's runtime ruling taken on
it the same day.

## (1) The abort — the runtime the phase pre-registered could not be reached

`results/parity_verdict_5b.json`, `outcome: aborted-runtime-unreachable`, **shipped A**. Five
serverless endpoints across four configurations left their jobs `IN_QUEUE` while the health
endpoint reported a worker:

| endpoint | class | volume | datacenter | worker states seen | job |
|---|---|---|---|---|---|
| `market-pulse-5b-a` (our handler) | AMPERE_48 | `gfwa2an8fn` | CA-MTL-3 | none for 8 min | queued |
| capacity control (our handler) | AMPERE_48 | none | any | `idle`, `ready` in 25 s | — |
| `market-pulse-5b-a` (our handler) | ADA_24 | `gfwa2an8fn` | CA-MTL-3 | `running` for 10 min | queued |
| diagnostic (stock image, inline handler) | ADA_24 | none | any | `running` | queued 5.5 min |
| **RunPod hub vLLM worker** | ADA_24 | none | any | `initializing` ⇄ `throttled` | queued 5 min |

The last row is what closes it: RunPod's **own** published serverless worker, deployed by hub id
with a 0.5 B model reference, no network volume, no datacenter pin and none of this project's
code — and it never consumed its job either. The blocker is not the handler, not the template,
not the network volume and not CA-MTL-3. That control cost about five cents and it is the
difference between a report that says "our worker is broken" and one that says "serverless is
unreachable on this account".

The counter-proof runs the other way. The same worker code, the same venv, the same weights and
the same adapter answered correctly through the identical `start.sh` → `serve_handler.py` →
`runpod.serverless.start` path on an A6000 **pod**: **278.9 s** cold start, `info` naming
`adapter_sha256 b3ca630846c7…` — the sha `results/verdict_45h2.json` records for arm A — and a
three-row T2 batch labelled «Рудь … знижка 20%» → `launch`, «Акція на молоко Яготинське» →
`promo`, «Графік роботи» → `relevant: false, other`. **The artifact serves; the serverless
delivery path is what does not.**

SPEC amendment 3.11 (2) pre-registered the outcome before either config was scored: *"A failed
or aborted pair closes the merge question in favour of A; no retry."* So **A ships and merging
stays forbidden** — config B is adopted only if this measurement selects it, and this
measurement did not happen. No gate number in `results/verdict_45h2.json` is touched. Spend:
**$0.5324 of the $4.00 stop**, $3.47 unspent, no pod, endpoint or template left running.

A second finding rides along and outlives the phase: **serverless capacity is per (datacenter ×
GPU class), and a network volume pins the datacenter.** With the volume attached in CA-MTL-3,
`ADA_24` (RTX 4090, 24 GB) was the only class that allocated a worker at all — `AMPERE_48`,
`ADA_48_PRO` and `AMPERE_80` allocated nothing. Only 18 datacenters support network volumes, so
the intersection of "supports volumes" and "has serverless capacity for a class that fits 18 GB
of NF4 weights" was, that day, one cell.

## (2) The operator's runtime ruling, 2026-08-06 — production is a stop-after pod

Taken on the phase's second-cheapest reading and written into SPEC amendment 3.11 (1) the same
session:

- **Production runtime = a stop-after POD on `AMPERE_48` (A6000), booted per pass.** The same
  card the 4.5h2 anchors were measured on. 5c's loop runs twice a day, not continuously, so a
  pod that is more expensive per hour is cheaper per phase than a runtime that cannot be
  reached at all.
- **Serverless may return later ONLY through a fresh §(2) measurement.** It is not a
  configuration switch: the parity contract is about the runtime the numbers were produced on,
  so a runtime that changes has to be measured again before its numbers reach an aggregate.
- **A support ticket runs in parallel at zero cost.** The hub-worker observation is the ticket.

The A6000 choice is the ruling's substance, not a detail. The only class that allocated
serverless workers with the volume attached was `ADA_24` — 24 GB against 18 GB of NF4 weights,
leaving ~6 GB for KV and activations, on a different card from the anchors. That is a bigger
runtime delta than "the same card, served differently", and it is exactly the delta the parity
measurement exists to keep small. A pod can have the A6000; serverless, that day, could not.

## (3) Consequence

SPEC amendment 3.11 (2) gained a **single-config measurement** in the same session: config A
alone, scored once against test v4 on the pod runtime — the pair stays closed and B stays dead —
one attempt, batch 1, hard stop the **$3.47** remaining under the 5b cap, smoke on the 24-row
arm-A carve, test v4 exposed exactly once. Deltas against `results/verdict_45h2.json` are
reported and never averaged away; no bar moves, and a 4.5h2-passed gate head landing under its
bar is a loud finding for an operator briefing rather than a verdict of that phase. **A failed
attempt stops the line: aggregates cannot take serving numbers without this measurement.** That
is `docs/PROMPT-5b1.md`.

Two team-lead misnames were corrected in the same amendment round rather than smoothed over:
PROMPT-5b's "carve-758" (the arm-A carve is 24 rows, sha `8347abd7…`; 758 is test v4's row
count), and SPEC 3.11 (6)'s "$8.70 remainder", which was true on 2026-08-05 and is now a dated
figure — the live headroom is read from `results/spend_*.json`, and the CA-MTL-3 volume bills
~$0.24/day whether or not anything is attached to it.

Related: [[gpu-provider-runpod]], [[phase4-own-pod-anchor]], [[45h2-ablation-verdict]],
[[architecture-stack]].
