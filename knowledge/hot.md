<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-07-28 09:27:18 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
b7ff907 feat: label wave-2 candidates
7c714b3 feat: mine and label sarcasm holdout candidates
33c8613 chore: sync v2 corrections upstream and refresh hot.md
8bbe76e feat: v2 sarcasm recalibration of train sources
a99f9cf chore: pending vault session artifacts
```

## 📅 Recent daily logs

- `2026-07-27.md`
- `2026-07-26.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-07-27 20:43 (edited by hand / `/close`; the section above is auto-generated — do NOT touch the marker)

## 🔥 What's Hot
**Phase 2 is delivered end to end** (2a–2f), 108 tests, `make check` green after every commit.
SPEC APPROVED rev. 3 + amendment 3.1. Registry: 4 live sources. Raw store 6 057 posts +
11 338 comments.

**Frozen test sets are at v2** — `docs/frozen-testsets.md` carries the hashes, the changelog
and the per-gate depth. comments 400/1600, posts 250/750, thread-disjoint, zero `unclear` in
test. v2 = 11 operator-approved corrections (2026-07-27) applied by `scripts/refreeze_v2.py`;
the set is immutable again.

**Training data is two files**: `comments_train.jsonl` (1600) + `sarcasm_candidates.jsonl`
(746 after the holdout took 54). Both recalibrated to the v2 sarcasm reading; 230 sarcastic
scoreable rows left for training (97 + 133).

**G1b runs on a frozen holdout** (2g, amendment 3.2, approved 2026-07-28): 108 rows,
54 fresh-corpus + 54 moved out of the mined pool, all `sarcasm: true`, zero `unclear`,
thread-disjoint from test and train. The slice is whatever the base model gets wrong at
Phase 3 — smaller than 108, unknown until then.

## ⏭️ Next
- **Phase 3 baselines**: TF-IDF+logreg, XLM-R, zero-shot for T1 and T2, pre-registered and
  scored only through `src/market_pulse/scorer.py`; results file committed (SPEC §8).
  Score the zero-shot base model on `data/frozen/sarcasm_holdout.jsonl` in the same run —
  that scoring is what defines the G1b slice.
- Still open from Phase 2: dataset cards for the public augmentation datasets + licence check;
  operator acceptance of Phase 1 and 2a–2g.

## 🚧 Blockers
- **G1a's per-language clause is noise-dominated.** 2 pp on RU (n=86) is ~1.7 rows; the
  2d-2 review measured 2.3% label error per field, ~1.7 rows on the same n. 326 test rows
  have been through neither operator pass. Free to decide now, expensive after the first
  baseline number.
- **One residual leak in the holdout, operator's call.** 25 holdout threads still hold a
  scoreable row of the mined training pool (31 of the 108 rows). Wave 1 excluded test threads
  only, and 2g was allowed to remove moved rows from training and nothing else. Closing it
  means dropping those 31 rows or pulling their mined thread-mates out of training.

## ⚠️ Footguns for the next run
- **`scripts/freeze_testsets.py --force` would rebuild the split and destroy v2.** The batch is
  synced, so labels are safe, but a fresh draw differs from v2 by 8 rows. Do not run it.
- `scripts/mine_sarcasm_candidates.py --force` overwrites 746 hand labels and
  `mine_sarcasm_holdout.py --force` another 971; `refreeze_v2.py`, `sync_batch_v2.py` and
  `freeze_sarcasm_holdout.py` are one-shot and refuse or no-op on a second run.
- **`data/annotation/sarcasm_holdout_pool.jsonl` is not training data** — its non-sarcastic
  rows share threads with the holdout. Train on `comments_train.jsonl` + `sarcasm_candidates`
  only.
- `RAW_STORE_SALT` in `.env` must never be rotated: a new salt orphans every `sender_anon_id`.
- `packaging` has 19 rows in the test set — G1c is thin by construction, not by accident.

## 🐞 Known harness bug
`knowledge/templates/daily-log.md` hard-codes `2026-07-26` instead of `{{DATE}}` → every daily-log
stub the Stop hook writes is stamped with the wrong date. One-word fix, operator's call.
