---
type: decision
date: 2026-09-03
status: accepted
tags: [decision, promo-pulse-1, money, s9]
---

# `--terminate-after` is derived from the cap LESS what the step already spent

**Executor's decision, applied in `scripts/runbook_promo_dev_1.md` §1.** Ruling 03.09 (e) item 2
lifts rungs 1 and 2 for steps of ≤$3.00 and leaves exactly two bounds standing: rung 0 (the
registration) and rung 3 (the platform's `--terminate-after`). This decides which number rung 3 gets.

## The defect it closes

`results/prereg_promo_dev_loop.json :: rung_0.hard_stop_seconds` is **12 162.2 s** — the seconds the
WHOLE $2.50 cap buys at the registered $0.74/h. The step had already spent **$0.089622** on the two
pods of 2026-09-03. A stop derived from the whole cap therefore permits $2.50 ON TOP of that:
**$2.5896 against a $2.50 registered cap**, with nothing else left to catch it now that rungs 1–2
are lifted, and each allowed recreate gets a fresh full-cap runway.

## The rule

`STOP_AT = now + (step.cap_usd − Σ segments' billed_usd) / usd_per_hour × 3600`, recomputed before
EVERY create, reading `results/promo_dev_loop_run.json` — the same record `close_segment` sums the
cap against, so the platform stop and the segment gate bound the same quantity.

On 2026-09-03 that was **11 725 s = $2.4102**, and the run's own bill was $0.435778. Worst case
under this rule: $0.089622 + $2.4102 = **$2.4998 ≤ $2.50**.

## Why this is execution and not a scope change

The registered cap is $2.50 for the STEP, and `close_segment` has always enforced it against every
segment of the run record. Deriving the platform stop from the same remainder makes rung 3 honour
the number rung 0 registered, and it is strictly more conservative than the record's own
`hard_stop_seconds` field — which stays as the registration wrote it, describing the whole cap.
Related: [[a_cap_set_from_one_legs_price]] · [[lifted_ceiling_is_not_lifted_code]].
