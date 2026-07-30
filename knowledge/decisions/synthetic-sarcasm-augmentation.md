---
type: decision
id: dec-2026-07-28-synthetic-sarcasm-augmentation
date: 2026-07-28
status: accepted
tags: [decision]
---

# 600 synthetic sarcastic comments as a fourth, ablation-gated training source

**Context:** the corpus is out of real sarcasm. Wave-2 mining swept every comment outside the test
and scoreable-train threads and returned 54 sarcastic scoreable rows from 971 candidates
([[hybrid-sarcasm-holdout-3.2]]); training keeps **230** sarcastic scoreable rows for a gate (G1b)
that is scored on 108 held-out ones. [[holdout-residual-thread-leak-accepted]] accepted a residual
thread leak explicitly on the promise that sarcasm data for *training* would be widened instead.

**Decision (2026-07-28, operator):** generate **600 synthetic sarcastic comments** into
`data/annotation/synthetic_sarcasm.jsonl` as a **separate fourth training source**. Three
conditions bind it:

- **Ablation-gated.** Phase 4 trains with and without the file and keeps it only if the gates
  improve. It is never merged into a real-source file, so the ablation can drop it by dropping one
  path — and every row carries a `synthetic:NNNN` id and `source_id: "synthetic"`, so a merge
  would still be visible.
- **Never in test or holdout.** The frozen sets are immutable (`docs/frozen-testsets.md`); a
  synthetic row in either would make the gate measure the generator.
- **Operator QA, pre-registered at ≥80%.** 50 rows (seed 42) export to
  `data/annotation/synthetic_qa.csv` with an `operator_verdict` column. Below 80% `ok`, the
  flagged failure patterns are regenerated **once**. The threshold was fixed before the sample was
  drawn, and the executor does not score it — SPEC §10.

**QA outcome — gate passed (operator, 2026-07-28; confirmed to the executor 2026-07-30).** The
≥80% `ok` threshold is met, so the file is cleared for the Phase-4 ablation and no regeneration
round is owed. The verdict is the operator's and is recorded here as given: the per-row
`operator_verdict` column in `data/annotation/synthetic_qa.csv` was **not** filled in, so this ADR
carries the ruling without the 50-row tally behind it. The CSV was left untouched — SPEC §10 keeps
the executor out of its own sample, and that includes transcribing a spoken verdict into the
column that is supposed to produce it. If the marked-up CSV turns up, add the counts here; nothing
downstream needs them, because the gate is pass/fail and it passed.

**Numbers:** 600 rows against 230 real sarcastic scoreable training rows, written to proportions
measured from those 230 — UA:RU 70:30, 96% negative, half the rows with no intent at all (the
guideline sends rigged-giveaway and service complaints to `intents: []`), then price ~30%,
availability ~17%, quality ~7%, packaging ~3%, taste ~1%. **Targets and achieved figures are
tabulated side by side in docs/frozen-testsets.md, "The third source is generated, and
conditional" — including the two the file misses**: no-intent rows land at 49.2% against 52.6%,
and the length tail is short (median 12 against 13, p75 20 against 27) because the brief caps a
row at 40 words while real complaints run past 100.

**Why:** the alternative to synthetic rows is not more real rows — that ceiling was measured, not
assumed. G1b asks the fine-tune to repair the base model on sarcasm, and 230 examples is thin for
a signal the annotation guideline itself calls the hardest. Generating them is cheap and, unlike
the public irony corpora, the register is this corpus' own: Ukrainian retail-chain comment threads,
UA/RU code-switching, `)))` and emoji markers, promo and giveaway framing.

**What keeps it honest:** `scripts/check_synthetic.py` fails the file on a verbatim or
near-verbatim copy of any real comment (word-3-gram Jaccard against all six real comment files,
test and holdout included), on internal near-duplicates, and on frame collapse — a single opening
or closing that eats more than 8% of the rows. Brands come from the registry watchlist or stay
generic, and no retail chain outside the registry is invented.

**Alternatives rejected:** public irony corpora (SemEval-2018, RuSentiment) — domain mismatch is
already a listed risk (SPEC §9) and their register is not retail comments; they remain augmentation
candidates once their licences are checked. Merging the synthetic rows into `comments_train.jsonl`
— cheaper to train, impossible to ablate, and it would put generated text behind a frozen hash.
Mining deeper for real sarcasm — the corpus was swept to exhaustion; only 89 of the last 971
candidates fired an irony heuristic at all.

**Sources:** docs/frozen-testsets.md ("Training sources", "Why 108 and not 180") ·
docs/annotation/comments.md · docs/SPEC.md §5 G1b, §9 · [[2026-07-28]] · related
[[hybrid-sarcasm-holdout-3.2]], [[holdout-residual-thread-leak-accepted]],
[[train-recalibration-v2]].
