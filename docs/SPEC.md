# market-pulse-llm — Project Specification (rev. 3.1)

**Status:** APPROVED rev. 3 (2026-07-26); amendment 3.1 approved 2026-07-27.
**Amendment 3.1:** EN removed from per-language gates — the collected corpus
contains 8 EN comments out of 2,000 sampled (retail channels post in UA); a
per-language metric over n=8 is meaningless. Gates run on UA and RU. The model
stays multilingual; EN support is untested, not claimed. Decided BEFORE
baselines were scored.
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
- G1b: sarcasm slice (150–200 curated examples the base model gets wrong):
  fine-tuned fixes ≥60% while overall macro-F1 degrades ≤2 pp.
- G1c: intents multi-label micro-F1 ≥ baseline + 5 pp.
- G1d: T2 post classification (relevance + 3-class) macro-F1 ≥ zero-shot base
  LLM + 10 pp on the frozen post test set.
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
