<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-07-27 19:06:20 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
19c2385 fix: count CSV rows, not physical lines, in the review sample summary
e3441dc feat: review sample export
6da48e3 feat: annotation validator
e845840 docs: amendment 3.1 drops EN from per-language gates
385ea1d docs: quote the corpus exactly in the annotation guidelines
```

## 📅 Recent daily logs

- `2026-07-27.md`
- `2026-07-26.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-07-27 19:02 (edited by hand / `/close`; the section above is auto-generated — do NOT touch the marker)

## 🔥 What's Hot
SPEC Phase 2 steps **2a–2d-2 delivered**, 91 tests, `make check` green after every commit.
SPEC is **APPROVED rev. 3 + amendment 3.1** (EN out of the per-language gates). Registry:
4 live sources (silpo, atb posts-only; varus, msuaaaa with comments). Raw store holds
**6 057 posts + 11 338 comments** back to 2024-07-01; the pre-registered 5 000-comment
gate reads PASSED — never self-accepted, 1/2a-2d still await the operator.

**All 3 000 rows carry `annotator: "llm-precheck"` labels** and both files validate clean.
Comments: unclear 694 (34.7%) → **1306 usable**, sarcasm 74, intents led by price 261 /
availability 235. Posts: relevant 115, launch 61, 143 brand mentions. Operator review
slices exported: `data/annotation/review_{comments,posts}.csv` (300 + 150, seed 42,
`operator_verdict` empty).

## ⏭️ Next
- **Operator decides two open calls** (both in the 19:02 log, affected ids listed):
  posts hold four rules I extrapolated rather than marked unclear — worst of them,
  "an incidental mention makes a post relevant" (7 posts); and EN survived labelling
  but rounds out of the review sample.
- Fill `operator_verdict` in the review CSVs → then the §8 QA gate: self-agreement ≥90%
  on a re-labelled random 100.
- Step **2e**: FROZEN test sets + committed hashes; dataset cards; public-dataset licences.
- Then Phase 3 baselines (TF-IDF+logreg, XLM-R, zero-shot) through `scorer.py`.

## 🚧 Blockers
- none

## ⚠️ Footguns for the next run
- `scripts/make_annotation_batch.py` overwrites `data/annotation/*.jsonl` without asking —
  a rerun now destroys 3 000 labels. `*.pristine.jsonl` are the blank originals; verified
  untouched, keep them that way.
- `RAW_STORE_SALT` in `.env` was generated 2026-07-27 and must never be rotated: a new salt
  orphans every `sender_anon_id` in the store.
- **G1b needs 150–200 sarcasm examples; this batch yields 74.** And `packaging` has 38 rows
  in 2 000 — single digits once 2e freezes the split. Both need a plan before Phase 4.

## 🐞 Known harness bug
`knowledge/templates/daily-log.md` hard-codes `2026-07-26` instead of `{{DATE}}` → every daily-log
stub the Stop hook writes is stamped with the wrong date. One-word fix, operator's call.
