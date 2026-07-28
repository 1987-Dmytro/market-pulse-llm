<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-07-28 11:44:02 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
2cbf47d docs: backfill decision records and index
a54cdf1 chore: record the pristine-baseline shrink as a footgun
f010a7d feat: freeze hybrid sarcasm holdout + SPEC 3.2 + card
b7ff907 feat: label wave-2 candidates
7c714b3 feat: mine and label sarcasm holdout candidates
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `holdout-residual-thread-leak-accepted.md` — Residual holdout/train thread overlap accepted
- `hybrid-sarcasm-holdout-3.2.md` — Hybrid sarcasm holdout for G1b (amendment 3.2, option 1a)

## 📅 Recent daily logs

- `2026-07-28.md`
- `2026-07-27.md`
- `2026-07-26.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-07-28 11:28 (edited by hand / `/close`; the section above is auto-generated — do NOT touch the marker)

## 🔥 What's Hot
**Phases 1 and 2 are DONE and accepted** (2026-07-28), 108 tests, `make check` green after every
commit. SPEC APPROVED rev. 3 + amendments 3.1 and 3.2. Registry: 4 live sources. Raw store
6 057 posts + 11 338 comments. Decision records: `knowledge/decisions/` ([[INDEX]]).

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
- **Phase 3a — scorer + TF-IDF baseline**, locally: implement the `scorer.py` gate functions and
  the TF-IDF+logreg baseline, pre-registered, results file committed (SPEC §8). Every number goes
  through the scorer, nowhere else.
- Then Phase 3b (XLM-R + zero-shot LLM on a rented GPU). The zero-shot run must also score
  `data/frozen/sarcasm_holdout.jsonl` — that scoring is what defines the G1b slice and its actual
  n. The base-model choice is made on those numbers, not on taste (docs/STATUS.md).
- Architecture session with the operator (model candidates, serving, dashboard stack, production
  loop) is the other open item from the 2026-07-28 revision — see docs/STATUS.md.
- Still open from Phase 2: dataset cards for the public augmentation datasets + licence check.

## 🚧 Blockers
**None.** Both former blockers were closed on 2026-07-28:
- *G1a per-language noise* — resolved by the operator's v2 review of all 400 test rows (11
  corrections came out of it), so the "326 rows through neither pass" caveat no longer holds.
- *Holdout/train thread overlap* — accepted with a rationale, see
  [[holdout-residual-thread-leak-accepted]]: the classifier is fed comment text only, so a
  thread-mate in training carries no label information. Compensation is more sarcasm data for
  training, source under discussion.

## ⚠️ Footguns for the next run
- **`scripts/freeze_testsets.py --force` would rebuild the split and destroy v2.** The batch is
  synced, so labels are safe, but a fresh draw differs from v2 by 8 rows. Do not run it.
- `scripts/mine_sarcasm_candidates.py --force` overwrites 746 hand labels and
  `mine_sarcasm_holdout.py --force` another 971; `refreeze_v2.py`, `sync_batch_v2.py` and
  `freeze_sarcasm_holdout.py` are one-shot and refuse or no-op on a second run.
- **`data/annotation/sarcasm_holdout_pool.jsonl` is not training data** — its non-sarcastic
  rows share threads with the holdout. Train on `comments_train.jsonl` + `sarcasm_candidates`
  only.
- **The freeze shrank `sarcasm_candidates.pristine.jsonl` 800 → 746** so the validator would
  not read the moved rows as lost. Legitimate once, audited (the 54 dropped ids are exactly
  the 54 moved into the holdout) — but the validator can be silenced the same way again. Any
  further row loss must be diffed against the baseline before it is believed.
- `RAW_STORE_SALT` in `.env` must never be rotated: a new salt orphans every `sender_anon_id`.
- `packaging` has 19 rows in the test set — G1c is thin by construction, not by accident.

## 🐞 Known harness bug
`knowledge/templates/daily-log.md` hard-codes `2026-07-26` instead of `{{DATE}}` → every daily-log
stub the Stop hook writes is stamped with the wrong date. One-word fix, operator's call.
