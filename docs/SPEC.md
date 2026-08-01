# market-pulse-llm — Project Specification (rev. 3.4)

**Status:** APPROVED rev. 3 (2026-07-26); amendment 3.1 approved 2026-07-27;
amendments 3.2 and 3.3 approved 2026-07-28; amendment 3.4 approved 2026-08-01.
**Amendment 3.1:** EN removed from per-language gates — the collected corpus
contains 8 EN comments out of 2,000 sampled (retail channels post in UA); a
per-language metric over n=8 is meaningless. Gates run on UA and RU. The model
stays multilingual; EN support is untested, not claimed. Decided BEFORE
baselines were scored.
**Amendment 3.2:** G1b's slice is drawn from the frozen sarcasm holdout
(`data/frozen/sarcasm_holdout.jsonl`): fresh-corpus sarcastic rows (wave-2
mining of threads disjoint from test and train) topped up with rows moved OUT of
the mined training pool — removed from training, not copied (option 1a). At
Phase 3 the zero-shot base model is scored on the holdout; the G1b slice = the
holdout rows the base model misclassifies. The gate itself is unchanged: the
fine-tuned model fixes ≥60% of the slice with ≤2 pp overall macro-F1 loss.
Fallback recorded: if the base model errs on fewer than 100 holdout rows, the
slice is whatever it errs on, and the smaller n is reported next to the gate
verdict. The corpus bounded the freeze at 108 rows (54 fresh + 54 moved) —
counts and provenance in `docs/frozen-testsets.md`. Decided BEFORE baselines
were scored.
**Amendment 3.3:** G1d gates the **3-class post-type** macro-F1 alone. The
rev. 3 wording "relevance + 3-class" named two distinct metrics and read as one
number; scoring them separately at Phase 3a showed why the difference matters —
relevance is already near its ceiling (TF-IDF+logreg 0.8119 against post-type
0.6653), so demanding +10 pp on a blended number would be arithmetically
dishonest: the blend would move on the head with the least room to give.
Relevance macro-F1 is REPORTED next to the gate with its own n and never enters
it. The threshold and the test set are unchanged. Unlike 3.1 and 3.2 this
amendment was decided AFTER a baseline was scored (2026-07-28, the TF-IDF+logreg
run) — it disambiguates a gate that was never one metric, and no fine-tuned
number exists yet, but the ordering is recorded rather than smoothed over.
**Amendment 3.4 (Phase 4 briefing, 2026-08-01):** four operator decisions, all
pre-registered before any Phase 4 code or GPU spend.
(1) **Base + precision — branch (2).** The base model is `google/gemma-4-31b-it`
(gate decision 2026-07-31, ADR `phase4-base-model-gate`; supersedes §7's
candidate list, which predates the 2026-07-31 live search). Training is QLoRA:
frozen base quantized NF4 4-bit (bf16 compute dtype) + LoRA adapters, on a
RunPod A6000 48 GB. Rationale: train in the precision you serve — production is
the quantized serverless path (2026-07-28); bf16 needs ~70 GB and does not fit
a 48 GB card. The deliverable artefact is the 4-bit base plus the UNMERGED
adapter, and every gate is scored in exactly that configuration. Merging the
adapter into bf16 weights is forbidden until measured (Phase 5).
(2) **Own-pod zero-shot re-run** — the first smoke step: the base model, the
same NF4 config, the same frozen inputs and byte-identical prompts as 3b, with
per-row prediction dumps. It anchors G1d/G1e, defines the G1b slice (the union
of sentiment ∪ sarcasm errors on the 108-row holdout, gate-review decision of
2026-07-31), and cross-checks the OpenRouter fp8 row; on material disagreement
the own-pod number anchors and the disagreement is recorded, never averaged.
The Phase 4 gate eval reuses this same local inference path, the adapter being
the only difference.
(3) **Ablation protocol for the synthetic source.** Two arms — with and without
`data/annotation/synthetic_sarcasm.jsonl` — identical config and seed, exactly
one data path differs. BOTH arms are scored on the frozen sets. Selection rule,
fixed now: the synthetic source stays iff its arm's G1b fix-rate is strictly
higher AND no other gated head is lower by more than 0.5 pp. The Tier-1 gate
verdict is the selected arm's; both columns are published side by side; there
is no third run. No retraining after gate numbers are seen — a failed gate
closes the question.
(4) **Budget time-box (§7/§9).** Hard cap **$25** GPU spend across all of
Phase 4, checked against RunPod billing before every start; the smoke must
project the full run, and a projection over **4 h per arm** stops the line for
an operator decision. Top-up $35 with a ~100 GB network volume (pods without a
volume are deleted unrecoverably at $0 balance).
**Date:** 2026-07-26 · **Team lead:** Fable session · **Executor:** Claude Code
**Repo folder:** `/Users/hdv_1987/Desktop/Projects/market-pulse-llm`
**rev. 3 change (operator decision):** producers in Ukraine barely use Telegram for
consumer communication → observation points switch to **retail-chain channels**
(АТБ, Сільпо, Varus) + discount aggregators; tracked category fixed: **dairy (all
subcategories) + ice cream**, category-wide with a brand watchlist.

## 1. Mission

**Category Intelligence System** — the company's key marketing-research instrument
for the Ukrainian food retail market (UA / RU / EN). The system monitors Telegram
channels of leading retail chains (АТБ, Сільпо, Varus) and discount aggregators,
filters the stream to the tracked category (**dairy — all subcategories — and ice
cream**), detects new-product announcements and promos, extracts brand/product
mentions, and classifies audience reactions in comments (sentiment, sarcasm/irony,
hidden intents: taste / price / packaging / quality / availability). Output:
comparative analytics per brand (watchlist highlighted) and per launch. Core = one
fine-tuned open LLM (QLoRA on rented NVIDIA GPU), multi-task instruction format.

**MVP constraint (operator decision): Telegram-only, $0 data budget.**
X API, FB/IG scrapers, and website monitoring are future extensions behind a
source-agnostic connector interface — out of MVP scope, no code for them.

## 2. Data reality

| Item | Tag | Notes |
|---|---|---|
| Retail-chain Telegram channels via MTProto API (Telethon), free. Candidate handles — operator-provided: @silpoua, @atb_market_official, @varus_ua; search-found: @silposilpo, @VARUS_channel | [REAL: channels exist; exact handles UNVERIFIED] | PRIMARY sources. Phase 2 entry check resolves each chain via Telegram global search to the verified (blue-check) channel, then checks comments enabled + traffic. Loyalty chat-bots (@silpo_bot etc.) are OUT of scope. Constraints: dedicated account, conservative rate limits, graceful FloodWait, no member-list harvesting, join discussion groups to read comments |
| Discount aggregator channels: @znizhki_ua, «Хочу дешевше» and similar | [REAL: channels exist] | SECONDARY sources, tagged separately in provenance (deal-hunter audience bias). Same entry check |
| Broader UA food/dairy community channels | [ASSUMED] | Extra training corpus for slang/sarcasm; candidates collected in Phase 2 |
| Public datasets (RuSentiment, RuReviews, SemEval-2018 irony, UA sentiment corpora) | [ASSUMED] | Augmentation only; licenses verified in Phase 2 before use |
| Domain annotation: 1–2k labeled comments + 0.5–1k labeled retailer posts | [PLANNED] | Operator-in-the-loop; annotation guidelines are Phase 2 deliverables |
| Future: X API pay-per-use, FB/IG via managed scrapers, retailer/producer websites | [DEFERRED] | Researched & costed 2026-07; excluded from MVP by operator decision |

## 3. Registry (three entities, extensible without code changes)

- **Sources:** chain/aggregator → Telegram channels; `source_type:
  official_retail | aggregator | community`.
- **Category taxonomy:** tracked group = dairy with ALL subcategories (milk,
  kefir/ryazhanka, yogurt, curd/сирки, sour cream, butter, cheese, dairy
  desserts, plant-milk analogs) + ice cream. New groups are added by registry
  edit only.
- **Brand watchlist:** operator's own + priority competitor brands; highlighted
  in analytics. Category-wide coverage remains (watchlist prioritizes, never
  filters out the rest). Initial watchlist = Phase 2 deliverable (operator
  confirms).

## 4. Model tasks

One base LLM, QLoRA fine-tuned, multi-task via instruction prefixes:

- **T1 — Comment classification:** sentiment (pos/neg/neutral) + sarcasm flag +
  multi-label intents (taste/price/packaging/quality/availability). Ambiguous
  cases get explicit `unclear`, excluded from gates.
- **T2 — Retailer-post analysis:** (a) relevance to tracked category (binary);
  (b) for relevant posts: {new-product announcement, promo/discount, other};
  (c) extraction of brand + product mentions (normalized to watchlist entries
  where applicable). Trained from the start; zero-shot base LLM is its baseline.

## 5. Success metrics (pre-registered; the scorer is the judge)

**Tier 1 — Model (primary project gate), one attempt after full training:**
- G1a: frozen held-out comment test set (per-language UA/RU; EN excluded by
  amendment 3.1): fine-tuned sentiment macro-F1 ≥ best baseline + 5 pp overall;
  no gated language below its baseline by more than 2 pp.
- G1b: sarcasm slice — the rows of the frozen sarcasm holdout that the base
  model gets wrong (amendment 3.2 replaces the 150–200 curated examples of
  rev. 3): fine-tuned fixes ≥60% while overall macro-F1 degrades ≤2 pp.
- G1c: intents multi-label micro-F1 ≥ baseline + 5 pp.
- G1d: T2 post-type classification (3-class: launch / promo / other) macro-F1 ≥
  zero-shot base LLM + 10 pp on the frozen post test set. Binary relevance
  macro-F1 is reported beside it with its own n and is not gated (amendment
  3.3, which reads rev. 3's "relevance + 3-class" as the two metrics it is).
- G1e: T2 brand-mention extraction F1 (exact match after normalization) ≥
  zero-shot base LLM + 10 pp on the same frozen post test set.
- A failed gate closes the question; negative result is a result.

**Tier 2 — Pipeline:** smoke run: 1,000 real comments + 200 retailer posts
end-to-end (collect → filter → classify → aggregate → dashboard), ≥99% processed
without error; latency budget fixed before the run.

**Tier 3 — Business signal:** on ≥2 real new-product announcements in the dairy /
ice-cream category the system (a) detects the announcement post, (b) attributes
the correct brand, (c) produces a reaction verdict agreeing with a human check of
50 random comments (≥85% agreement).

Honesty rules: every published number has fixed seed + saved config + provenance;
comparisons paired on identical instances; comparison tables always include the
cheapest realistic baseline (TF-IDF+logreg and zero-shot); dashboard/README read
numbers only from result files and fail loudly if a source is missing.

## 6. Architecture (MVP)

source registry (sources + taxonomy + watchlist, YAML) → Telegram collector
(Telethon; incremental backfill + polling; append-only raw store JSONL/Parquet
with provenance incl. source_type) → normalize/dedup/lang-id → **category
relevance filter (T2a)** → model service (fine-tuned LLM, batch: T2b/c on posts,
T1 on comments of relevant posts) → aggregation store (per-brand, per-launch,
per-intent rollups; watchlist flag) → dashboard: launch feed + reaction
scorecards + negative-share by intent, brand vs brand. Connector interface is
source-agnostic so X/FB/IG/web can be added later without touching the core.

## 7. Model plan

- Base candidates (choice = Phase 4 gate, decided on baseline numbers, not
  vibes): Qwen3-8B/14B, Llama-3.1-8B, Gemma-3-12B — must be strong UA/RU.
- QLoRA on rented NVIDIA GPU (Vast.ai / RunPod, 24–48 GB); training budget
  time-boxed before Phase 4. Smoke run mandatory before any long run.
- Baselines BEFORE fine-tuning (pre-registered "before" numbers), per task:
  (a) TF-IDF + logistic regression (+ keyword rules for T2a relevance),
  (b) fine-tuned XLM-R encoder, (c) zero-shot base LLM with fixed prompt.

## 8. Phases & verify-gates

| Phase | Deliverable | Gate |
|---|---|---|
| 0 | Spec approved; folder, git init, second-brain layer, /init | DONE (rev. 2); rev. 3 approval pending |
| 1 | Repo skeleton: pytest + ruff green; scorer stubs; registry | DONE 2026-07-26 |
| 2 | Registry migration (sources+taxonomy+watchlist); Telegram collector; channel entry checks (АТБ handle found, comments enabled, traffic); corpus backfill; licenses verified; annotation guidelines (comments + posts); 1–2k comment labels, 0.5–1k post labels; FROZEN test sets | Entry-check report per channel; dataset cards; label QA (self-agreement ≥90%); test-set hashes committed |
| 3 | Baselines a/b/c for T1 and T2 scored by the shared scorer; numbers pre-registered | Scorer is single source of truth; results file committed |
| 4 | QLoRA multi-task fine-tune: smoke → full; gates G1a–e evaluated once | Tier-1 gates |
| 5 | Production loop: polling collector + batch inference + aggregation | Tier-2 smoke (1k comments + 200 posts) |
| 6 | Dashboard (launch feed, brand scorecards, negative-share by intent) reading result files only | No hand-typed numbers; loud failure on missing source |
| 7 | Real-launch validation on ≥2 category announcements + packaging | Tier-3 gate |
| R (deferred) | X / FB-IG / website connectors: legal, cost, go/no-go | Decision record per source |

## 9. Failure modes & risks

- Retail channels are high-volume and promo-dominated → T2a relevance filter is
  on the critical path; measure its precision/recall on the frozen post set.
- Some chain channels may have comments disabled → entry check per channel;
  fall back to aggregator/community channels for reactions.
- Aggregator audience bias (deal hunters skew negative on price) → source_type
  in provenance; report per-source splits, never blend silently.
- Brand extraction ambiguity (private labels, sub-brands, UA/RU spellings) →
  normalization table in registry; `unknown-brand` bucket reported explicitly.
- Telegram account restrictions → dedicated account, conservative limits,
  history reads only, graceful FloodWait, cursor resume.
- Launch labels are rare → months of historical backfill across all channels.
- Public-dataset domain mismatch → domain test set is the arbiter.
- Label noise / sarcasm subjectivity → guideline with examples; `unclear` label.
- GPU rental cost creep → time-boxed budget fixed before Phase 4.

## 10. Conventions

- Chat: Russian. All artifacts (code, comments, commits, docs, vault): English.
- Small diffs, atomic commits, executor never self-accepts; every phase ends
  with a report reviewed against the gate checklist.
