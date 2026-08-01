---
type: index
tags: [decision]
---

# Decision records

One ADR per recorded decision, backfilled 2026-07-28 from docs/SPEC.md revisions, docs/STATUS.md
and the docs/frozen-testsets.md changelog. Russian summaries of the same decisions live in
docs/STATUS.md; these are the English long form with the numbers.

| date | decision | status |
|---|---|---|
| 2026-07-26 | [[telegram-only-mvp]] — Telegram only, $0 data budget | accepted |
| 2026-07-26 | [[retail-chains-pivot]] — observe retail chains, not producers | accepted |
| 2026-07-26 | [[category-and-watchlist]] — dairy + ice cream, 20-brand watchlist | accepted |
| 2026-07-27 | [[en-out-of-gates-3.1]] — EN out of the per-language gates | accepted |
| 2026-07-27 | [[znizhki-ua-removed]] — dead aggregator dropped from the registry | accepted |
| 2026-07-27 | [[testset-refreeze-v2]] — 11 operator-approved test-set corrections | accepted |
| 2026-07-27 | [[train-recalibration-v2]] — train sources recalibrated to the v2 reading | accepted |
| 2026-07-28 | [[hybrid-sarcasm-holdout-3.2]] — hybrid 108-row holdout for G1b | accepted |
| 2026-07-28 | [[holdout-residual-thread-leak-accepted]] — 31 rows share threads with training | accepted |
| 2026-07-28 | [[architecture-stack]] — serverless inference · Mac cron · SQLite · Streamlit | accepted |
| 2026-07-28 | [[gpu-provider-runpod]] — RunPod, Vast.ai as the experiment fallback | accepted |
| 2026-07-28 | [[frontier-api-reference-baseline]] — Claude Haiku as a reference row, not a gate | accepted |
| 2026-07-28 | [[g1d-gate-clarification-3-3]] — G1d gates the 3-class post type; relevance reported only | accepted |
| 2026-07-28 | [[synthetic-sarcasm-augmentation]] — 600 synthetic sarcastic rows, ablation-gated | accepted |
| 2026-07-31 | [[3b-infra-and-precision]] — 3b zero-shot on OpenRouter at pinned fp8, $8 cap | accepted |
| 2026-07-31 | [[phase4-base-model-gate]] — base model gemma-4-31b-it; the unpaired 27B row cannot flip it | accepted |
| 2026-08-01 | [[phase4-own-pod-anchor]] — the own-pod NF4 row anchors G1d/G1e; G1b slice = 44 ids; greedy is not batch-invariant | accepted |
| 2026-08-01 | [[4b-training-contract]] — frozen QLoRA hyperparameters; a training example is an eval prompt; the second arm projects over the 4 h ceiling | accepted |
