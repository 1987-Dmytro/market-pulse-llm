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
| 2026-08-08 | [[5c1-day2-composition-and-search]] — three "city feeds" were chats; the search for replacements reached feeds the town-name scan never returned (137,221 against a 16,056 chat); five flags cleared, one FAIL moved to watch; registry 39 → 67, all of it provisional pending the yield screen | accepted |
| 2026-08-08 | [[5c1-relevance-floor-and-discovery]] — 66 channels had passed four gates and none of them ever asked whether the tracked category was in there; the yield screen refuses to report because АТБ's own 28 days carry 0 relevant posts (19 of 25 image-only), and «варто» — a private label and the ordinary word for "it is worth" — outfires every real brand | accepted |
| 2026-08-08 | [[srv2-serverless-runtime-target]] — the 5b wall did not reproduce: a two-job console probe consumed and completed both, so the production runtime target moves back to serverless (ruling 20 stays the measured fallback); four things the probe does not prove are pre-registered, and 3.11 (2) parity remains mandatory | accepted |
| 2026-08-09 | [[srv2-program-close]] — the programme closes: parity 758/758 with worst head movement 0.0000 earns serverless as the runtime, srv-2b's hang is charged to the platform by the operator's unwrapped control, and the price is a finding AGAINST the chosen path ($1.0825/pass vs the pod's $0.4611, ×2.35) that goes to the 5c2 briefing; the scale-to-zero saving is NOT measured | accepted |
| 2026-08-09 | [[5c1-vis-b-caption-instrument]] — the project's own Gemma 4 is the caption instrument: 19 of 19 silent ATB posts captioned and bar A taken 0 → 14 against a bar of 4 (qwen 13), so the pre-registered instrument-failure rule did not fire; the 8-of-18 bridge against qwen sits on inputs proven byte-identical, which makes it a finding about the task — a caption is a SAMPLE of a six-page leaflet — and a 5c2 design input rather than a captioner defect | accepted |
| 2026-08-10 | [[opus-review-programme-close]] — 25 of 25 packs and 498 of 498 rows close the second-instrument review: the matcher is acquitted (`fn_matcher` 0, every one of the 102 misses image-only, so `recall_candidate` 0.4769 measures the CAPTIONS), 163 captions judged 117 faithful / 43 partial / 3 wrong, 93 of the 104 false positives are «варто» and «Президент», and two misses expose a Latin-script alias gap the caption got right | accepted |
| 2026-08-10 | [[sitting-2026-08-10-composition-signed]] — the sitting rules «Варто» text-matching OFF (it stands in both columns: 69 false positives, 13 image-side misses) and «Селянське» anchored-only (TM, butter grade and Рудь's ice-cream line on the same pages), defers the 141 unlisted names into the position layer rather than the registry, and SIGNS the launch composition 66 = launch 59 + watch 7 unchanged — a stamp that moves the registry's sha and no row of it | accepted |
| 2026-08-10 | [[sku-b-pilot-readings-ratified]] — all five executor readings of sku-b's denominators are ratified (R1 recall per POST macro-averaged over 15, R2 the 108 sent pages, R3 four empty-gold posts as a precision probe, R4 n ≥ 10 pairs, R5 unreadable replies excluded and counted); the 30-row text gold comes back 11 position · 3 product_mention · 16 none with two triage rulings, and bar 3's denominator is ALL 30 rows — narrowing it to the 14 rung-carrying ones is refused as a post-hoc change that would delete the half of the sample pricing refusal | accepted |
| 2026-08-11 | [[sku-b-serving-and-cap-discipline]] — the record debt of sku-b-prep: the prep/run split, the POSITIONS pin (NF4 base with the adapter OFF, greedy, batch 1, 800-token ceiling) and the warm-up on non-gold inputs behind SPEC 3.17 (9); the three cap readings of (10) — go/no-go before the first gold call consumes NO attempt, a mid-leg stop is a finding about the CAP, and no single job may out-bill the cap; and the security pass that motivated (c), where a 1800 s job timeout could bill $0.5520 against a $0.35 cap | accepted |
| 2026-08-11 | [[sku-b-run-acceptance-and-resume]] — the single paid session is ACCEPTED at 17 of 138 gold calls ($0.1965, stopped by its own (10)(b) cap gate): the go/no-go's arithmetic was right and its PROBE was not — a generated 64×64 image answered in 1.436 s where a real leaflet page cost 5.0772 s (3.54×), so the gate passed the run it exists to refuse; no bar is scored, the team lead's 13-pair calibration read (6 correct, every miss the kopeck superscript) is NON-GATING, and SPEC 3.17 (11) resolves the stop as a RESUME — buy exactly the 121 unbought elements, instrument FROZEN, the warm-up becomes representative, cap $0.45 | accepted |
