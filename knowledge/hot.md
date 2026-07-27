<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-07-27 20:36:19 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
a99f9cf chore: pending vault session artifacts
0124f52 docs: v2 hashes, changelog and train-source card
f59bf31 feat: operator-approved test-set corrections, refreeze v2
a6b774b feat: sarcasm candidate mining and labeled pool
e444284 feat: leakage-controlled split and frozen test sets
```

## 📅 Recent daily logs

- `2026-07-27.md`
- `2026-07-26.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-07-27 21:40 (edited by hand / `/close`; the section above is auto-generated — do NOT touch the marker)

## 🔥 What's Hot
**Phase 2 is delivered end to end** (2a–2f), 108 tests, `make check` green after every commit.
SPEC APPROVED rev. 3 + amendment 3.1. Registry: 4 live sources. Raw store 6 057 posts +
11 338 comments.

**Frozen test sets are at v2** — `docs/frozen-testsets.md` carries the hashes, the changelog
and the per-gate depth. comments 400/1600, posts 250/750, thread-disjoint, zero `unclear` in
test. v2 = 11 operator-approved corrections (2026-07-27) applied by `scripts/refreeze_v2.py`;
the set is immutable again.

**Training data is two files**: `comments_train.jsonl` (1600) + `sarcasm_candidates.jsonl`
(800 mined + hand-labelled). Both recalibrated to the v2 sarcasm reading — sarcasm now 10.7%
of the scorable train pool against 13.0% in test.

## ⏭️ Next
- **Phase 3 baselines**: TF-IDF+logreg, XLM-R, zero-shot for T1 and T2, pre-registered and
  scored only through `src/market_pulse/scorer.py`; results file committed (SPEC §8).
- Before scoring: decide whether G1a's per-language clause is usable — expected label noise on
  RU (n=86) is ~1.7 rows, the same width as the 2 pp margin (card, "Depth" section).
- Still open from Phase 2: dataset cards for the public augmentation datasets + licence check;
  operator acceptance of Phase 1 and 2a–2f.

## 🚧 Blockers
- none

## ⚠️ Footguns for the next run
- **`scripts/freeze_testsets.py --force` would rebuild the split and destroy v2.** The batch is
  synced, so labels are safe, but a fresh draw differs from v2 by 8 rows. Do not run it.
- `scripts/mine_sarcasm_candidates.py --force` overwrites 800 hand labels; `refreeze_v2.py` and
  `sync_batch_v2.py` are one-shot and refuse or no-op on a second run.
- `RAW_STORE_SALT` in `.env` must never be rotated: a new salt orphans every `sender_anon_id`.
- `packaging` has 19 rows in the test set — G1c is thin by construction, not by accident.

## 🐞 Known harness bug
`knowledge/templates/daily-log.md` hard-codes `2026-07-26` instead of `{{DATE}}` → every daily-log
stub the Stop hook writes is stamped with the wrong date. One-word fix, operator's call.
