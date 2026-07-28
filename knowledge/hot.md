<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-07-28 17:55:56 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
3e16392 feat: synthetic sarcasm training source
a9c6d7b docs: amendment 3.3 and decision records
8bc7d66 docs: record architecture-session decisions
fa98055 fix: record every dirty path, not the first one minus a character
e6e93b4 feat: tfidf-logreg baseline and results file
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `synthetic-sarcasm-augmentation.md` — 600 synthetic sarcastic comments as a fourth, ablation-gated training source
- `g1d-gate-clarification-3-3.md` — G1d gates the 3-class post type, not a relevance blend (amendment 3.3)

## 📅 Recent daily logs

- `2026-07-28.md`
- `2026-07-27.md`
- `2026-07-26.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-07-28 19:40 (edited by hand / `/close`; the section above is auto-generated — do NOT touch the marker)

## 🔥 What's Hot
**Phases 1 and 2 are DONE and accepted** (2026-07-28); **Phase 3a is done** — 142 tests,
`make check` green after every commit. SPEC APPROVED rev. 3 + amendments 3.1, 3.2 and **3.3**.
Registry: 4 live sources. Raw store 6 057 posts + 11 338 comments. Decision records:
`knowledge/decisions/` ([[INDEX]]), 14 ADRs ([[architecture-stack]], [[gpu-provider-runpod]],
[[frontier-api-reference-baseline]], [[g1d-gate-clarification-3-3]],
[[synthetic-sarcasm-augmentation]]).

**The scorer computes, and it is the only thing that may.** `src/market_pulse/scorer.py` has every
gate function plus a public `macro_f1` so diagnostics use the same arithmetic. Two conventions the
numbers hang on: macro averages run over the labels **gold** supports (never over what a model
predicted — that would break paired comparison), and the `unclear` exclusion lives in the scorer,
driven by a sentinel the caller passes. Both are pinned by hand-computed tests, and a public
function without one now fails the suite.

**First real numbers — `results/baselines.json`, read via `scripts/show_results.py`.**
`tfidf-logreg`: G1a 0.6834 overall (ua 0.6982 · ru 0.6730) · G1c 0.6000 · **G1d 0.6653** (the
3-class post type — amendment 3.3; relevance 0.8119 is reported beside it and not gated) ·
G1e 0.1964 (tp 11 · fp 65 · fn 25, low by construction — the extractor only knows the watchlist).
G1b is `null`: amendment 3.2 defines its slice by the zero-shot base LLM's errors, which is 3b
work. Cross-checked against `sklearn.metrics.f1_score` to 6 decimals.

**Frozen test sets are at v2** — `docs/frozen-testsets.md` carries the hashes, the changelog
and the per-gate depth. comments 400/1600, posts 250/750, thread-disjoint, zero `unclear` in
test. v2 = 11 operator-approved corrections (2026-07-27) applied by `scripts/refreeze_v2.py`;
the set is immutable again.

**Training data is three files now**: `comments_train.jsonl` (1600) + `sarcasm_candidates.jsonl`
(746 after the holdout took 54) — both recalibrated to the v2 sarcasm reading, 230 sarcastic
scoreable rows between them (97 + 133) — plus `synthetic_sarcasm.jsonl`, **600 generated rows,
ablation-gated and QA-pending** ([[synthetic-sarcasm-augmentation]]). The generated file is
checked by `scripts/check_synthetic.py`, not by eye: nothing copied from the six real comment
files (test and holdout included), nothing repeated inside it, no frame over 8%.

**G1b runs on a frozen holdout** (2g, amendment 3.2, approved 2026-07-28): 108 rows,
54 fresh-corpus + 54 moved out of the mined pool, all `sarcasm: true`, zero `unclear`,
thread-disjoint from test and train. The slice is whatever the base model gets wrong at
Phase 3 — smaller than 108, unknown until then.

## ⏭️ Next
- **Operator QA of the generated rows** — `data/annotation/synthetic_qa.csv`, 50 rows, seed 42,
  `operator_verdict` per row (`ok` / `unclear` / `fix:field=value`). The gate is **≥80% `ok`**,
  pre-registered before the sample was drawn; below it the flagged patterns are regenerated once.
  Nothing downstream may use the file's numbers until this comes back.
- **Phase 3b — XLM-R + zero-shot LLM on RunPod** ([[gpu-provider-runpod]]). The zero-shot run must
  also score `data/frozen/sarcasm_holdout.jsonl`: that scoring is what defines the G1b slice and
  its actual n. The base-model choice is made on those numbers, not on taste (docs/STATUS.md), and
  the Phase-4 candidate list gets refreshed by live search in 3b.
- The frontier-API reference row (Claude Haiku, ~$1–3) belongs to the same table —
  reference only, gates stay on the three primary baselines
  ([[frontier-api-reference-baseline]]).
- Still open from Phase 2: dataset cards for the public augmentation datasets + licence check.

## 🚧 Blockers
**None.** One thing is waiting on the operator and does not block 3b:
- **The synthetic QA verdicts** (see Next). The file may sit in the repo unscored; it may not be
  trained on, cited or counted before the 80% gate is answered.

Open, not blocking: **`docs/STATUS.md` is committed but stale in content** — it still shows
Phase 3 as ⏸ ПРИОСТАНОВЛЕНА, calls the SPEC "rev. 3.2" (3.3 since today), says "108 тестов"
(142 now), schedules the RunPod ADR "промтом шага 3b" (added 2026-07-28), and lists Phase 3a as
a pending next step. It is the team lead's
document, so it is recorded here rather than rewritten. Nothing outside it and
`docs/frozen-testsets.md` points at `results/baselines.json`.

Three former blockers were closed on 2026-07-28: *G1a per-language noise* — resolved by the
operator's v2 review of all 400 test rows; *holdout/train thread overlap* — accepted with a
rationale, see [[holdout-residual-thread-leak-accepted]]; *which head G1d reads* — decided by
amendment 3.3, see [[g1d-gate-clarification-3-3]].

## ⚠️ Footguns for the next run
- **`scripts/freeze_testsets.py --force` would rebuild the split and destroy v2.** The batch is
  synced, so labels are safe, but a fresh draw differs from v2 by 8 rows. Do not run it.
- `scripts/mine_sarcasm_candidates.py --force` overwrites 746 hand labels and
  `mine_sarcasm_holdout.py --force` another 971; `refreeze_v2.py`, `sync_batch_v2.py` and
  `freeze_sarcasm_holdout.py` are one-shot and refuse or no-op on a second run.
- **`data/annotation/sarcasm_holdout_pool.jsonl` is not training data** — its non-sarcastic
  rows share threads with the holdout. Train on `comments_train.jsonl` + `sarcasm_candidates`
  (+ `synthetic_sarcasm.jsonl` only inside the ablation) and nothing else.
- **Never merge `synthetic_sarcasm.jsonl` into a real-source file.** The Phase-4 ablation has to
  drop it by dropping one path; merged, it cannot be removed and it sits behind a frozen hash.
  `data/annotation/*` is gitignored, so the file survives only through an explicit `!` exception —
  do not "tidy" that line away.
- **The generated rows carry no QA number, and that is not an oversight.** 50 rows are exported
  for the operator; ≥80% `ok` was pre-registered before the draw. The executor never scores its
  own sample (SPEC §10), so any number here must come back from the operator's CSV.
- **The freeze shrank `sarcasm_candidates.pristine.jsonl` 800 → 746** so the validator would
  not read the moved rows as lost. Legitimate once, audited (the 54 dropped ids are exactly
  the 54 moved into the holdout) — but the validator can be silenced the same way again. Any
  further row loss must be diffed against the baseline before it is believed.
- **`results/baselines.json` is append-only and never hand-edited.** A run is a record; a second
  run of the same model appends a second one. Numbers reach it only through the scorer, and
  `scripts/show_results.py` only reads. A hand-typed number there is invisible — nothing
  re-derives that file.
- **A results record cannot name the commit that contains it**, so provenance is `commit` + the
  list of `dirty` paths at run time; the runner shouts if any of them is under `src/`, `scripts/`
  or `config/`, because then the recorded commit does not reproduce the numbers.
- sklearn lives in the `baseline` extra (`pip install -e '.[baseline]'`), not the runtime deps —
  no test may import it or `make check` stops being runnable on a bare checkout.
- `RAW_STORE_SALT` in `.env` must never be rotated: a new salt orphans every `sender_anon_id`.
- `packaging` has 19 rows in the test set — G1c is thin by construction, not by accident.

## 🐞 Known harness bug
Fixed 2026-07-28: `knowledge/templates/daily-log.md` now carries `{{DATE}}`, the placeholder
`scripts/brain-session-end.py` actually substitutes; `tests/test_templates.py` keeps the pair
honest. The three stubs the bug already stamped 2026-07-26 were re-stamped with their own dates.
