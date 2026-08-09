---
type: decision
id: dec-2026-08-09-srv2-program-close
date: 2026-08-09
status: accepted
tags: [decision]
---

# The srv-2 programme closes: serverless is the runtime, and its price is a finding against it

**Context:** [[srv2-serverless-runtime-target]] opened the programme on 2026-08-08 with a ruling
(23 / SPEC amendment 3.14) and four things the console probe did **not** prove. This record closes
it. Every number below is read out of the artifact named beside it; nothing is re-derived here,
and the per-step spends are deliberately **not summed** — each is a balance delta read at its own
moment, and adding floors taken hours apart produces a figure no reading supports (Dv33, and the
`one balance, one moment` correction of 2026-08-09).

## The ledger, step by step

| step | what it bought | spend | artifact |
|---|---|---|---|
| probe | two jobs COMPLETED on RunPod's own mock worker; the 5b wall did not reproduce | ~$0.03 (meter at $0.00016/s; the record says $0.02–0.04 and does not pretend to more) | `docs/probe-serverless-20260808.md` |
| srv-2a | the serverless worker config, the volume plan, `scripts/runbook_srv2b.md` | $0.00 | 1 270 tests green, no billable resource created |
| srv-2b | ABORT at the handshake rung — and the OOM question closed on the way (19 874 of 24 564 MiB), the D7 re-read, a live volume | **$0.9999** of $4.00 | `results/spend_srv2b.json`, `results/d7_reread_srv2b.json` |
| srv-2c | the boot log, and the operator-bought control on srv-2b's **unwrapped** argv | **$0.1377** of $0.75 | `results/srv2c_bootlog.json` (`step_spent_usd_at_close`) |
| srv-2d | the SPEC 3.11 (2) parity attempt, spent, 758/758 scored | **$1.2383** of $2.00 | `results/spend_srv2d.json` (anchor), `results/srv2d_cost.json` (`cross_check_against_the_balance`) |

`results/spend_srv2d.json`'s last logged session reads **$1.2332** at 22:13:58Z and
`results/srv2d_cost.json` reads **$1.2383** at 22:27:29Z. Both are correct; the second is the
settled one and is the figure this record and `docs/STATUS.md` carry. The pair is kept rather
than tidied, because it is what "a balance delta is a floor" looks like on disk.

## (1) Serverless is the production runtime

Ruling 23 / amendment 3.14, and srv-2d is what earns it. `results/parity_srv2.json`: **758/758
rows scored, zero parse, api or generation failures**, config A on `ADA_24` in EU-RO-1 off the
volume. Both clauses of 3.11 (2) hold — `under_bar: []`, `passed: 4`, and the drop rule's
**`worst_drop: 0.0`** against `results/parity_5b_a.json`, the pod reading of the identical
config. G1c rose 0.0018 and G1e 0.0133; G1a fails its bar exactly as it did on the pod and at
4.5h2, to the same sixteen digits, which is the deferred 3.11 question and not a new finding.
Row-level agreement with the pod is **751/758 = 99.08%** (implementation-notes, Phase 5 srv-2d) —
description, gated on nothing.

Nothing was appended to `results/baselines.json`: a parity measurement is not a gate anchor, and
the pod's own reading of 2026-08-06 is not in there either.

## (2) srv-2b's failure was the platform, not our container

srv-2b's own diagnosis — "our container does not start" — is **falsified twice**, and the second
one is the decisive one:

- `results/srv2c_bootlog.json`: the wrapped start command reaches the job loop, prints, and a job
  COMPLETES. So the container starts.
- The operator then bought a control running srv-2b's **exact unwrapped argv** on the same volume,
  region and class, twenty minutes later: also COMPLETED. So the wrapper was not the cause either.

What is left is the platform: on 2026-08-08 between 18:06 and 18:59 UTC a worker on this account
sat `running` for 31 minutes at $0.00031/s with its job stuck IN_QUEUE. **Transient**, and named
as such rather than explained away — n=1, no root cause from the vendor, ticket closed unfiled.
The engineering consequence is already in the code: `serve_handler.assert_sdk_version` refuses to
boot below `runpod 1.10.1`, the release that fixes the per-worker job-tracking corruption RunPod
documents for 1.7.11–1.10.0.

## (3) The cost is a finding AGAINST the chosen path, and it goes to the 5c2 briefing

`results/srv2d_cost.json` against `results/serving_5b.json :: adopted`:

| | serverless (RTX 4090) | pod (A6000) | ratio |
|---|---|---|---|
| per 758-row pass | **$1.0825** | **$0.4611** | **×2.35** |
| per 1000 rows | $1.4281 | $0.5993 | ×2.38 |
| seconds per row | 4.262 | 4.071 | ×1.047 |
| $/hour equivalent | $1.1041 | $0.53 | ×2.08 |

The two ratios differ because the denominators differ, and both are in the record. **The gap is
the machine's price, not the model's speed** — the 4090 generates within 4.7% of the A6000's
per-row time and bills about twice its hourly rate. Two independent readings agree to 1%: the
endpoint's own settled ledger rate ($0.00030669/s) applied to measured seconds, and the account
balance delta. Dv33 makes both **floors**, so the ratio is a lower bound.

This is recorded as a finding against the runtime that was chosen, not as an argument for
reversing the ruling. It is the operator's to price, and it belongs to the **5c2 briefing** —
where the run-rate of two collection passes a day is decided.

## (4) What is NOT measured: the scale-to-zero saving

The economic case in [[srv2-serverless-runtime-target]] (1) is the ~12 h of daily idle between the
two passes SPEC 3.11 (1) fixes: a pod pays for that idle and a scaled-to-zero worker does not.
**No number in this programme measures it.** srv-2d measured one dense pass, where scale-to-zero
buys nothing by construction — the worker is busy throughout, and its `idle_share` is 0.0091.

So the ×2.35 above and the unmeasured idle saving pull in opposite directions, and this record
refuses to net them: a comparison of a measured cost against an estimated saving would read as
arithmetic and be an argument. The saving is measurable — two passes a day, wall-clock, against
the volume's settled **$0.009722/h** — and nobody has measured it.

## Consequences

- **5c1 comes off HOLD.** The hold of 3.14 (1) was on paid steps pending proof; the proof exists.
  `docs/PROMPT-5c1-vis-a.md` is re-issued against the endpoint.
- **The volume `qw4nwleanc` is the only standing resource** — 100 GB, EU-RO-1, settled at
  $0.009722/h, holding `hf/` at revision `842da379…`, the pinned venv, `repo/`, the adapter and
  `start.sh`. Everything else is deleted and proven deleted by listing.
- **`results/parity_verdict_5b.json` stays untouched.** It is the honest record of 2026-08-06 and
  must not be cited as current state; this record and 3.14 are what superseded it.
- The pod remains the measured fallback. Nothing in srv-2 withdrew ruling 20's numbers.

Related: [[srv2-serverless-runtime-target]] · [[5b-parity-abort-and-pod-runtime]] ·
[[5b2-batch-measurement]] · [[5c1-relevance-floor-and-discovery]].
