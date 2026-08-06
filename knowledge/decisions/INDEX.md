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
| 2026-08-02 | [[phase4-gate-verdict]] — both arms trained and scored once; the rule drops synthetic; 2 of 5 Tier-1 gates pass | accepted |
| 2026-08-02 | [[phase45a-ceiling]] — 244 blind verdicts: the per-head ceiling in metric and accuracy units | proposed |
| 2026-08-02 | [[test-v3]] — 38 blind verdicts applied beside v2; intents pending the law review | proposed |
| 2026-08-02 | [[taxonomy-v2-relabel-and-appetite]] — all 1,912 rows up-labelled after the ≥90% gate; three boundary calls ratified; v2 copies beside originals | accepted |
| 2026-08-02 | [[45g-parent-context-and-uplabel]] — the parent post joins the v2 prompts as new revisions; the 97 emptied rows re-asked; the 1,912 up-label goes as a calibrated precheck | accepted |
| 2026-08-03 | [[45g2-captions-and-quiz-rulings]] — the 11/20 quiz applies 11 rows plus one validated pattern; media-only posts get an image caption or a poll transcript; the sitting is resealed | accepted |
| 2026-08-03 | [[45g3-sitting-gates]] — all three strata FAIL (88/89/81); guideline v2.1 from the sitting rulings; the whole 1,912 re-labelled under `precheck_v2.1_with_post` and a fresh blind hundred sealed | accepted |
| 2026-08-03 | [[45g4-v22-affirmative-rewrite]] — the v2.1 rulings restated affirmatively as v2.2 (FORM-ONLY); a 100-row in-sample probe pre-registered and gated before any full re-run | accepted |
| 2026-08-03 | [[45g5-features-over-prompts]] — the probe's KILL closes the prompt-form track; 35 adjudicated verdicts written into the batch; the collector learns `reply_to`; both families measured, and a naive reply rule would cost 62 of 258 judged-correct rows | accepted |
| 2026-08-03 | [[45g6-context-lines-probe]] — six dictated verdicts complete the adjudicated 40; the two features rendered as facts beside the post (RENDER-ONLY, no prompt text moves); KILL at 41/58 preserved with feature-fixed 9/17 — the fact behaved like the rule it was chosen instead of | accepted |
| 2026-08-04 | [[45h-v4-and-the-precheck]] — the confound caught before the money: both arms under the v2 law; test v4 = v3 → the 508-row intents pass → 31+1 operator rulings on top; the 54 single-homed at 917 | accepted |
| 2026-08-05 | [[45h2-ablation-verdict]] — both arms trained and scored once on test v4; the пласт loses G1c by 4.05 pp and is DROPPED; 3 of 5 Tier-1 gates pass, G1c short by 0.0005 and not retried | accepted |
| 2026-08-06 | [[5a-census-api-and-theme-expansion]] — the poll payload was never on disk, so the census fetched (16/16 byte-identical control, $0 held); three themes buy 6.8% of the coverage gap; four more themes and the seed handles authorised, the target itself deferred to the combined ledger | accepted |
| 2026-08-06 | [[5b-parity-abort-and-pod-runtime]] — the pair aborted: no serverless endpoint on this account consumes a job, RunPod's own hub worker included, while the same artifact answers on an A6000 pod; A ships and merging stays closed; production runtime becomes a stop-after pod on AMPERE_48, serverless only via a fresh §(2) measurement | accepted |
| 2026-08-06 | [[5b2-batch-measurement]] — the carve ladder finds every N byte-identical and picks 16; the paid run scores 666 of 758 rows and dies on GPU memory, so the adoption rule has no G1b and cannot run: serving is fixed at batch 1 permanently and the run-rate question returns to the operator | accepted |
