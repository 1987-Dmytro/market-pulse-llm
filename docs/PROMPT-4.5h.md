# PROMPT-4.5h — Precheck for test v4 + two free category measurements ($0 phase)

Team-lead file. Operator: paste everything below the line into Claude Code.

---

You are executing step 4.5h-precheck of market-pulse-llm. Full context up front;
do not re-plan the phase yourself.

## Context (3 lines)

The relabel gate-program closed with three pre-registered KILLs; the пласт
(1 912 rows: v2 labels + 41 manual verdicts) earns its place via a retrain
ablation. Phase 4.5h = test v4 → fresh own-pod anchor → bars → A/B ablation.
THIS prompt is the precheck half only: read-only analysis, $0 spend, no freeze.

## Operator decisions already fixed (2026-08-03 briefing — do not relitigate)

1. Bars for the 4.5h gate: same construction as Phase 4 — derived
   programmatically from the FRESH anchor by `scripts/gate_bars.py` logic
   (+5 pp margin gates, floors, 60% slice, no-regression rescale). No number
   is typed by hand anywhere.
2. Arm-selection rule: amendment 3.4 (3) transposed — the пласт stays iff
   arm B's G1c is strictly higher AND no other gated head is lower by more
   than 0.5 pp. Committed as code BEFORE any scoring (in 4.5h2, not now).
3. Fresh full anchor on our pod (all heads, new G1b slice) — approved.
4. Two category measurements ride along at $0 (Step 2 below).

## Read first (sections only — not whole documents)

- `docs/SPEC.md` §5 (gates), §8 (phases)
- `knowledge/decisions/test-v3.md` (what v3 is; the held-back intents rulings)
- `docs/frozen-testsets.md` — section "Sarcasm holdout (G1b)" only
- `results/features_45g5.json` (families/пласт numbers, if needed)

## Step 0 — hygiene (before anything else)

1. `git status` shows 4 modified files: docs/STATUS.md (the 4.5g6 close AND
   the team lead's 4.5h briefing record — both expected), knowledge/daily_logs/
   2026-08-03.md, knowledge/hot.md, knowledge/index.md. Commit them as one
   commit: `chore: the 4.5g6 close and the 4.5h briefing — status, log, vault tail`.
   (Committing team-lead files is fine; editing them is not.)
2. Refresh knowledge/hot.md via the /save pattern: Now/Next/Blockers must say
   "4.5h precheck in flight"; no stale open items; blockers named with owner.
3. `make check` green before and after; report the test count.

## Step 1 — v4 design precheck (read-only, $0, no code changes)

Write `results/precheck_45h.json` + a `scripts/precheck_45h.py` that produces
it (so every number below is reproducible). Report each item with file paths.

1. **Dual-home inventory (the 54).** The 54 rows moved from the mined pool to
   the holdout on 2026-07-28. For each id: (a) does its id or verbatim text
   still appear in any training-side store today (`sarcasm_candidates.jsonl`
   post-move, the 1 912-row пласт, `comments_train.jsonl`)? (b) which columns
   diverge between its homes right now (intents v1 in frozen vs v2 in the
   annotation stores; sentiment/sarcasm after v3)? Output: counts + the id
   list. Then present exactly TWO reconciliation options with their numbers —
   (i) single-home materialization in v4, (ii) scoring-time dedup — costs and
   what each does to the G1b denominator. No recommendation without numbers.
2. **Guard inventory.** Locate the code guard(s) that held intents at v1 in
   the v3 freeze (`freeze_testsets_v3.py` and anywhere else). Name file:line
   in the report. Do NOT change code.
3. **v4 intents migration counts.** Of the 508 gold rows (400 comments_test +
   108 holdout): how many already have a v2-taxonomy intents value in the
   annotation stores vs need a fresh relabel pass; projected OpenRouter cost
   at the observed 4.5e per-row rate. State the ledger anchor (balance) BEFORE
   any projection math. Confirm posts_test carries no intents field and say
   what v4 posts therefore is.
4. **Also reconcile on paper:** the 31 derived-but-unapplied intents rulings
   of v3 (audit) and the 3 operator law verdicts — do they collide with the
   v2 relabel values on the same ids? Counts only.
5. **B-arm projection.** Recompute arm A's exact scoreable train row count
   under the v2 law (STATUS says 2 346 — verify, do not trust). B = A + the
   пласт's scoreable rows (unclear excluded by `train_qlora.py` line ~126).
   Project steps, hours and $ at $0.53/h for both arms against the 5 h
   per-arm ceiling of amendment 3.6. If B exceeds the ceiling, say so plainly
   — the team lead will amend SPEC before 4.5h2; do not shrink the run.
6. **Anchor + eval budget.** Projected $ and minutes for: 1 anchor run + 2
   arm evals, batch 1, 758 rows each, from the observed 4a/4c rates.

## Step 2 — two category measurements ($0, no LLM, no gold touched)

Amendment-candidate of 2026-08-03 (category is a property of the POST;
comments inherit via parent_msg_id). Write `scripts/measure_categories.py` →
`results/categories_45h.json`:

1. **Post category coverage.** Over the ~6 057 posts: what fraction carries a
   readable category signal from a DRAFT keyword lexicon — seed it from
   `config/registry.yaml` tracked_groups display names, plus draft entries
   for non-tracked families seen in posts (вареники, кімчі, …). Commit it as
   `data/category_lexicon_draft.json` marked `"status": "draft-not-law"` —
   the taxonomy itself is the operator's word later; this only measures
   coverage feasibility.
2. **Cross-category comment share.** Comments whose text names a lexicon
   category different from their parent post's draft category (the
   «а сметана кисла під варениками» case). Report the share over all comments
   and over scoreable train rows; include 10 example rows for each measure
   (id, channel, text, post category, comment category).
3. **Position (SKU) mention share** (operator request, 2026-08-03 briefing).
   Over the same posts: what fraction names a concrete position — heuristic
   draft: a pack-size/volume token (число + г|кг|мл|л|шт|%) within the same
   line as a lexicon category or watchlist brand hit. Report the share, split
   by source_type (official_retail vs aggregator), + 10 example posts with
   the matched span. Draft measure for the Phase 5/6 SKU-layer design — not
   law, no extraction, no new fields in any store.

4. **Comparison / comment-side position share** (operator design question,
   2026-08-03: per-brand sentiment in comparative comments). Over all
   comments, scoreable train and the 400-row test separately: (a) share
   naming ≥2 distinct watchlist brands; (b) share with a comparison marker
   (краще|гірше|ніж|за|смачніше|дешевше|дорожче|лучше|хуже|чем|вкуснее|
   дешевле — draft list, extend as seen) within the same sentence as a brand
   hit; (c) share where the comment itself carries a pack-size/variant/
   position token (the Step-2.3 heuristic plus category-lexicon words applied
   to comments). Also report the INTERSECTIONS — a∩b (two brands compared)
   and a∩b∩c (full position comparisons, the operator's canonical case:
   «Морозиво пломбір Рудь смачніший за Гармонію») — these are the rows a
   future per-(brand+position)-sentiment amendment would exist for. 10
   example rows per measure with ids. Measured BEFORE any schema change is
   designed; no relabel, no law change now.

All four measures: counts + shares + examples in the JSON; no train, no
frozen, no пласт file is modified.

## Report back to the team lead

Structure: (0) read-back FIRST — list the steps in one line each and the
DO-NOTs you consider binding, before doing anything; (1) Step 0 evidence;
(2) precheck numbers with file paths; (3) category numbers; (4) Deviations
section — every departure from this contract, however small; silence is not
compliance (keep `implementation-notes.md` current); (5) `make check` count,
`git log --oneline` of your commits, ledger line proving $0 spent.

## DO NOT

- No freeze files created or modified; nothing under `data/frozen/` changes.
- No GPU pods, no OpenRouter requests — projections only, from recorded rates.
- No changes to scorer, trainer, config, prompts registry.
- No пласт mutations; no gold mutations.
- Do not edit docs/STATUS.md, docs/SPEC.md or docs/PROMPT-*.md — team-lead
  files (File ownership). Phase-end facts go to implementation-notes.md and
  the daily log.
- Do not proceed to freeze/anchor/retrain — that is 4.5h2, a separate prompt
  after the team lead signs off on this precheck.

Language of all artifacts: English. Atomic commits as you go.
