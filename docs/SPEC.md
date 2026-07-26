# market-pulse-llm — Project Specification (Phase 0, rev. 2)

**Status:** APPROVED by operator 2026-07-26.
**Date:** 2026-07-26 · **Team lead:** Fable session · **Executor:** Claude Code
**Repo folder:** `/Users/hdv_1987/Desktop/Projects/market-pulse-llm`

## 1. Mission

**Competitor Intelligence System** — the company's key marketing-research
instrument for the food / snack / confectionery market (RU / UA / EN). Operator
registers 2–3 direct competitors; the system monitors their **Telegram channels**,
detects new-product/flavor launch announcements in competitor posts, classifies
audience reactions in comments (sentiment, sarcasm/irony, hidden intents:
taste / price / packaging / quality / availability), and turns this into
comparative launch analytics. Core = one fine-tuned open LLM (QLoRA on rented
NVIDIA GPU) handling both tasks in a multi-task instruction format.

**MVP constraint (operator decision 2026-07-26): Telegram-only, $0 data budget.**
X API, FB/IG scrapers, and website monitoring are future extensions behind a
source-agnostic connector interface — out of MVP scope, no code for them.

## 2. Data reality

| Item | Tag | Notes |
|---|---|---|
| Telegram: competitor channels (posts) + discussion-group comments via MTProto API (Telethon), free api_id/api_hash | [REAL] | ONLY MVP source. Reading channel history/comments is low-risk; verified 2026-07. Constraints: dedicated account, conservative rate limits, graceful FloodWait handling, no member-list harvesting, must join discussion groups to read comments |
| Telegram: broader food/snack community channels | [REAL] | Extra training corpus for slang/sarcasm beyond competitor channels |
| Public datasets (RuSentiment, RuReviews, SemEval-2018 irony, UA sentiment corpora) | [ASSUMED] | Pre-training/augmentation only; licenses verified in Phase 2 before use |
| Domain annotation: 1–2k labeled comments + 0.5–1k labeled competitor posts (launch/promo/other) | [PLANNED] | Operator-in-the-loop; annotation guidelines are Phase 2 deliverables |
| Future: X API pay-per-use ($0.005/read), FB/IG via managed scrapers (~$0.75–2.30/1k, Meta ToS gray zone), competitor websites | [DEFERRED] | Researched & costed 2026-07; excluded from MVP by operator decision |

## 3. Model tasks

One base LLM, QLoRA fine-tuned, multi-task via instruction prefixes:

- **T1 — Comment classification:** sentiment (pos/neg/neutral) + sarcasm flag +
  multi-label intents (taste/price/packaging/quality/availability). Ambiguous
  cases get explicit `unclear`, excluded from gates.
- **T2 — Post classification (launch detection):** competitor post →
  {new-product/flavor launch, promo/ad, other}. Trained from the start
  (operator decision), zero-shot base LLM kept as its baseline.

## 4. Success metrics (pre-registered; the scorer is the judge)

**Tier 1 — Model (primary project gate), one attempt after full training:**
- G1a: frozen held-out comment test set (per-language RU/UA/EN): fine-tuned
  sentiment macro-F1 ≥ best baseline + 5 pp overall; no language below its
  baseline by more than 2 pp.
- G1b: sarcasm slice (150–200 curated examples the base model gets wrong):
  fine-tuned fixes ≥60% while overall macro-F1 degrades ≤2 pp.
- G1c: intents multi-label micro-F1 ≥ baseline + 5 pp.
- G1d: launch detection (T2) macro-F1 ≥ zero-shot base LLM + 10 pp on a frozen
  post test set.
- A failed gate closes the question; negative result is a result.

**Tier 2 — Pipeline:** smoke run: 1,000 real Telegram comments + 200 posts
end-to-end (collect → classify → aggregate → dashboard), ≥99% processed without
error; latency budget fixed before the run.

**Tier 3 — Business signal:** on ≥2 real competitor launches the system (a)
detects the launch post, (b) produces a reaction verdict that agrees with a human
check of 50 random comments (≥85% agreement).

Honesty rules: every published number has fixed seed + saved config + provenance;
comparisons paired on identical instances; comparison tables always include the
cheapest realistic baseline (TF-IDF+logreg and zero-shot); dashboard/README read
numbers only from result files and fail loudly if a source is missing.

## 5. Architecture (MVP)

competitor registry (YAML: competitor → TG channels) → Telegram collector
(Telethon; incremental backfill + polling; append-only raw store JSONL/Parquet
with provenance) → normalize/dedup/lang-id → model service (fine-tuned LLM,
batch) → aggregation store (per-competitor, per-launch, per-intent rollups) →
dashboard: launch feed + reaction scorecards + negative-share by intent,
competitor vs competitor. Connector interface is source-agnostic so X/FB/IG/web
can be added later without touching the core.

## 6. Model plan

- Base candidates (choice = Phase 4 gate, decided on baseline numbers, not
  vibes): Qwen3-8B/14B, Llama-3.1-8B, Gemma-3-12B — must be strong RU/UA.
- QLoRA on rented NVIDIA GPU (Vast.ai / RunPod, 24–48 GB); training budget
  time-boxed before Phase 4. Smoke run (tiny subset, loss falls, eval improves)
  mandatory before any long run.
- Baselines BEFORE fine-tuning (pre-registered "before" numbers), per task:
  (a) TF-IDF + logistic regression, (b) fine-tuned XLM-R encoder, (c) zero-shot
  base LLM with fixed prompt.

## 7. Phases & verify-gates

| Phase | Deliverable | Gate |
|---|---|---|
| 0 | This spec approved; folder, git init, brain-init | Operator approval |
| 1 | Repo skeleton: pytest + ruff + CI green on empty project; scorer module stub; competitor registry schema | All checks green |
| 2 | Telegram collector (rate-limited, incremental, provenance); competitor + community channel corpus; dataset licenses verified; annotation guidelines (comments + posts); 1–2k comment labels, 0.5–1k post labels; FROZEN test sets (comments RU/UA/EN + sarcasm slice; posts) | Dataset cards; label QA (self-agreement ≥90% on relabel sample); test-set hashes committed |
| 3 | Baselines a/b/c for T1 and T2 scored by the shared scorer; numbers pre-registered | Scorer is single source of truth; results file committed |
| 4 | QLoRA multi-task fine-tune: smoke → full; gates G1a–d evaluated once | Tier-1 gates |
| 5 | Production loop: polling collector + batch inference + aggregation | Tier-2 smoke (1k comments + 200 posts) |
| 6 | Dashboard (launch feed, reaction scorecards, negative-share by intent) reading result files only | No hand-typed numbers; loud failure on missing source |
| 7 | Real-launch validation on ≥2 competitor launches + packaging (README, honest "what we learned", repro) | Tier-3 gate |
| R (deferred, off critical path) | X / FB-IG / website connectors: legal, cost, go/no-go decision records | Decision record per source |

## 8. Failure modes & risks

- Competitor channels may have comments disabled or low volume → verify during
  competitor selection (Phase 2 entry check); fall back to community channels
  mentioning the competitor/brand.
- Telegram account restrictions → dedicated account, conservative limits,
  channel-history reads only, graceful FloodWait; collector resumes from cursor.
- Launch labels are scarce (launches are rare events) → augment with historical
  backfill of competitor channels (months of history) + community announcements.
- Public-dataset domain mismatch → domain test set is the arbiter; public data
  is augmentation only.
- Label noise / sarcasm subjectivity → guideline with examples; `unclear` label.
- GPU rental cost creep → time-boxed budget fixed before Phase 4.

## 9. Conventions

- Chat: Russian. All artifacts (code, comments, commits, docs, vault): English.
- Small diffs, atomic commits, executor never self-accepts; every phase ends
  with a report reviewed against the gate checklist.
