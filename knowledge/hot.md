<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-07-30 11:49:19 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
5088f7a chore: ignore .DS_Store
88ddad7 chore: daily logs and hot-cache refresh
162876d docs: record the synthetic QA verdict in its ADR
ab25618 docs: 3b handoff and the executor prompt
9a83604 docs: quote the achieved numbers, not the targets
```

## 📋 Recent decisions

- `synthetic-sarcasm-augmentation.md` — 600 synthetic sarcastic comments as a fourth, ablation-gated training source
- `INDEX.md` — Decision records
- `g1d-gate-clarification-3-3.md` — G1d gates the 3-class post type, not a relevance blend (amendment 3.3)

## 📅 Recent daily logs

- `2026-07-30.md`
- `2026-07-28.md`
- `2026-07-27.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-07-30 11:45 (edited by hand / `/save`; the section above is auto-generated — do NOT touch the marker)

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
ablation-gated, QA passed 2026-07-30** ([[synthetic-sarcasm-augmentation]]). The generated file is
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
  **Closed 2026-07-30 — the operator confirmed the gate passed**; the verdict lives in
  [[synthetic-sarcasm-augmentation]], the CSV cells stay empty. Nothing further is owed here.
- **Phase 3b — re-scoped on 2026-07-31: zero-shot runs on the OpenRouter API, no GPU is rented.**
  The operator funded OpenRouter ($9.84) and left RunPod at $0.00, so the rented-A6000 premise of
  rev. 1 is gone. RunPod stays the Phase-4 training provider ([[gpu-provider-runpod]]); its top-up
  is deliberately deferred to the Phase-4 gate. The zero-shot run must still score
  `data/frozen/sarcasm_holdout.jsonl`: that scoring is what defines the G1b slice and its actual n.
  The base-model choice is made on those numbers, not on taste (docs/STATUS.md).
  The executor prompt is rewritten and frozen at **`docs/PROMPT-3b.md` rev. 2, paste without
  edits** ($8 hard cap · OpenRouter only · fixed candidates · precision RULE · XLM-R on local MPS ·
  no QLoRA, no scorer changes). Its header keeps the diff against rev. 1.
- **The precision rule is pre-registered and must not be re-litigated after numbers exist:**
  probe `/api/v1/models/<slug>/endpoints` for all three candidates first — `bf16` for all three if
  every candidate offers it, otherwise `fp8` for all three, never mixed, routing pinned with
  `allow_fallbacks: false`, provider + quantization in every provenance record. The honest caveat
  (third-party serving, not our hardware) is paid off by ONE zero-shot re-run of the CHOSEN model
  on our own pod during the Phase-4 smoke.
- Candidates are FIXED by the operator (live search done 2026-07-31, do not re-select):
  `google/gemma-4-31b-it`, `qwen/qwen3.6-27b`, `qwen/qwen3.5-9b`. Reference row is
  `anthropic/claude-haiku-4.5:batch` **through OpenRouter** — no Anthropic key anywhere.
- Operator pre-flight for 3b: create an OpenRouter key (cap it at $8 in their dashboard too), add
  `OPENROUTER_API_KEY` to `.env` (template is in `.env.example`), and install `runpodctl`
  (`brew install runpod/runpodctl/runpodctl`, then `runpodctl doctor`) — money on RunPod waits.
- The frontier-API reference row (Claude Haiku, ~$1–3) belongs to the same table —
  reference only, gates stay on the three primary baselines
  ([[frontier-api-reference-baseline]]).
- **Open Phase-4 fork raised by the operator 2026-07-31 — bf16 LoRA vs 4-bit QLoRA.** Plain LoRA
  on an unquantized base is on the table and is decided at the Phase-4 gate together with the
  model. VRAM (base + adapters + activations): Gemma-4-31B ~70 GB bf16 / ~24 GB 4-bit ·
  Qwen3.6-27B ~62 / ~21 · **Qwen3.5-9B ~22 / ~8, so bf16 fits a 48 GB A6000.** Training cost is
  NOT the deciding argument — the dataset is ~2 950 short rows, a run is 1-1.5 h, and A6000
  QLoRA ($0.53/h) vs A100-80 bf16 LoRA ($1.39/h) differ by single dollars. The principle is
  train-in-the-precision-you-serve: an adapter trained against a quantized base and merged into
  bf16 weights drifts, and so does the mirror case. Details and the three branches are in
  docs/STATUS.md.
- Still open from Phase 2: dataset cards for the public augmentation datasets + licence check.

## 🚧 Blockers
**None.** 3b is free to start.

The synthetic QA gate closed on 2026-07-30: the operator confirmed ≥80% `ok`, and
[[synthetic-sarcasm-augmentation]] now carries the verdict, so `synthetic_sarcasm.jsonl` is
cleared for the Phase-4 ablation and owes no regeneration round. One caveat that outlives the
blocker: **the ruling is recorded without the 50-row tally** — `data/annotation/synthetic_qa.csv`
still has every `operator_verdict` cell empty and was deliberately not filled in from a spoken
verdict (SPEC §10). The gate is pass/fail and it passed; nothing downstream needs the counts.

The older "STATUS.md is stale" note is closed too: the 2026-07-30 rewrite refreshed the Phase 3
row with the achieved numbers and replaced "следующие шаги" with a HANDOFF block. Still true that
nothing outside it and `docs/frozen-testsets.md` points at `results/baselines.json`.

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
- **The generated rows passed QA but carry no QA number, and that is not an oversight.** ≥80%
  `ok` was pre-registered before the 50-row draw; the operator ruled it passed on 2026-07-30
  without returning the marked-up CSV. The executor never scores its own sample (SPEC §10), so
  the empty `operator_verdict` column stays empty — do not back-fill it to make the record look
  tidy. The ADR is the authority on the verdict.
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
