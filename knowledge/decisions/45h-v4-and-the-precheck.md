---
type: decision
id: dec-2026-08-04-45h-v4-and-the-precheck
date: 2026-08-04
status: accepted
tags: [decision]
---

# Test v4, and the confound the precheck caught before the money

**Context:** [[45g6-context-lines-probe]] closed the relabel gate-program with the third of three
pre-registered KILLs, so the пласт — 1 912 up-labelled rows — stopped being something a re-run
could justify and became something an **ablation** has to price. `docs/PROMPT-4.5h` split that
into a $0 precheck and a paid execution. This ADR records what the precheck found, what it changed
about the phase that was about to run, and what test set v4 is. The ablation's own numbers are a
separate record: [[45h2-ablation-verdict]].

## (a) The finding: the two arms would not have differed only in volume

`results/precheck_45h.json`. The ablation was specified as a volume — arm A, arm B = A + the
пласт, one variable, everything else paired. The row counts checked out, the ids did not overlap
at all, the seed and config were identical. And the arms still differed in something nobody had
written down:

| | `service` rows among scoreable | what the gate scores in |
|---|---|---|
| arm A's sources (`train_qlora.SOURCES`, v1) | **0** | |
| the `_tax2` siblings staged beside them | 308 + 239 = **547** | |
| the пласт | **652** | |
| test v4 (`comments_test_v4` + `sarcasm_holdout_v4`) | 189 of 508 | **taxonomy v2** |

The 4.5e re-label had written its output into `_tax2` copies beside each source — a good staging
convention — and `train_qlora.SOURCES` still named the originals. Nothing errors: both arms train,
both score, the numbers are plausible and paired. Arm B would simply have been the only arm ever
shown the class it is graded on, would have won the pre-registered selection rule, and the phase
would have recorded that as "the data was worth it". Both files hold the same 906 / 540 scoreable
rows, so the fix costs nothing and moves no projection — the whole cost was in not looking.

Adopted verbatim as **SPEC amendment 3.9 (1)**: both arms train on the `_tax2` siblings.

## (b) What else the precheck settled

- **The пласт is genuinely additive** — 0 of its 1 286 scoreable rows carries an id any training
  source already holds — which is *why* arm B breached the ceiling. Had they overlapped, arm B
  would have been a relabel of arm A and no hour would have moved. Amendment 3.9 raised the
  per-arm ceiling 5 h → 6.5 h; the with-post rendering later took it to 8.5 h (§(d)).
- **STATUS's "arm A = 2 346" was a different quantity**: the comment rows of both T1 sources
  *before* the `unclear` filter, posts excluded. The trainer's own count is 2 195 scoreable /
  **2 171** after the carve, which is exactly `4c-arm-a/provenance.json`.
- **The carve had to move.** `assemble` draws it from the assembled real pool, which is why
  Phase 4's arms held out the same 24 rows — the synthetic source joined *after* the draw. A
  пласт entering as a source would be drawn from. Amendment 3.9 (2): the carve is drawn **before**
  the пласт is appended, and `carve_sha256` is identical across arms (`8347abd74ae9…`).
- **Leakage is zero** on rows the 2026-07-28 freeze never saw: 0 ids, 0 threads, 0 verbatim texts
  against `comments_test`, `sarcasm_holdout` and both v3 siblings.
- **The 54 dual-home ids** had one second home, `data/annotation/sarcasm_holdout_pool.jsonl`, and
  it is in `train_qlora.NEVER_READ` — so the premise largely dissolved. Resolved by option (i)
  anyway (§(c)).
- **The comparison case is not observable at this n.** Over 11 338 comments: 227 name a watchlist
  brand, 241 carry a comparison marker somewhere, 10 name two brands, 3 put a marker in the same
  sentence as a brand, and **a∩b = 0** in both brand readings on all three populations. The
  per-(brand+position) amendment is **DEFERRED on the numbers**, and measure №4 becomes a free
  counter in the Phase-5 loop (`results/categories_45h.json`, `docs/PRODUCT.md`).
- **The instrument could not see the operator's own example.** «Морозиво пломбір Рудь смачніший за
  Гармонію» scores one brand under the exact matcher `market_pulse.brands` — the watchlist says
  `Гармонія`, the sentence says `Гармонію`, and exact matching is correct for grading a prediction
  and wrong for asking how often people mention a brand. Both readings are reported side by side
  and neither is gated.

## (c) Test v4 — the derivation, and the hole in it

**v4 does not replace v3 and v3 does not replace v2.** Four new files; every older sha stands, and
Phase 4's Tier-1 verdict is still the v2 result it was decided as. What v4 adds is the one column
v3 deliberately left alone. Order, fixed by amendment 3.9 (3) and executed by
`scripts/freeze_testsets_v4.py`:

    v3 -> the migration pass (`intents` only, 508 rows) -> the 31 audit rulings -> the 1 law verdict

"On top" is observable on **23 rows**, where the operator's ruling and the pass disagree; there the
operator's answer is gold. 213 of 400 comment rows and 61 of 108 holdout rows move; **189 of the
508 now carry `service`**, which no v3 gold row could say — that is what makes G1c scoreable at
all. `posts_test_v4` is byte-identical to `posts_test_v3`: posts carry no `intents` column.

**The instrument is `relabel_intents_v2_with_post`** (`qwen/qwen3.6-27b`, pinned fp8, seed 42,
$0.1080 over 555 requests against a $0.30 cap). The contract named "T1v2.1-with-parent-post"; the
only registered prompt of that family is `precheck_v2.1_with_post`, and **v2.1 failed its own
pre-registered gate** at preserved 20/58 against v2's 58/58. Operator decision of 2026-08-04: the
prompt that asks for `intents` alone, carries the v2 law no gate killed, and takes the parent post
gold was annotated under (`docs/annotation/comments.md` §Unit).

**39 rows the pass could not read, and the failure mode is named rather than smoothed.** The model
answered a bare `{}` — a JSON object with no `intents` key — and the *same ids* failed on a
re-ask, so it is the model on those rows and not the transport. 4 are covered by an operator
ruling that supersedes the pass either way. Of the remaining 35: **31 already carry `[]`**, which
is what `{}` appears to mean, and **4 carry a v1 label v4 did not revisit**. `[]` is the majority
answer, so coercing would have filled the hole exactly where the instrument failed and where the
answer was most likely to look right. Every id is listed in `results/frozen_v4.json`.

**The 54 are resolved by option (i):** the holdout pool is materialized at **917 rows** as a new
file beside the pristine 971, so each id lives in exactly one place and the four records pinning
the original's sha stay valid.

## (d) What the execution had to change that the contract did not foresee

Amendment 3.9 (1) is not executable as "only SOURCES differs": 547 of the retargeted rows carry
`service`, `parse_reply("T1", …)` refuses it, and the build stops. So the training prompt has to
move to a v2 revision — and the trainer's core invariant, train/eval format identity, moves the
eval's with it, which is what the contract already says for the anchor ("v2-with-post"). Measured
exactly, on the cached tokenizer at the pinned revision, with an s/step model fitted on 4c arm A
(r = +0.850) and validated on 4c arm B it never saw (43.36 predicted against 43.417 observed):

| arm | rendering | steps | padded tok | s/step | hours | rows over 1024 |
|---|---|---|---|---|---|---|
| A | `T1v2` | 270 | 1 276 | 54.29 | 4.07 | 1 |
| A | `T1v2_with_post` | 270 | 1 543 | 66.86 | **5.01** | 52 |
| B | `T1v2` | 432 | 1 249 | 53.01 | 6.36 | 1 |
| B | `T1v2_with_post` | 432 | 1 567 | 67.97 | **8.16** | 79 |

Operator decision of 2026-08-04: **with the post** — 4.5f measured what dropping it costs (97 rows
emptied). Two consequences, both authorised in the same breath and both needing a team-lead
amendment: the per-arm ceiling **6.5 h → 8.5 h**, and **`max_seq_len` 1024 → 1408**. The cap is a
guard threshold and not a pad width — `collate` pads per micro-batch — so raising it moves no step
time; every row of both arms encodes under it, checked by driving `encode` over all 5 676.

## (e) Provenance

| what | value |
|---|---|
| precheck | `results/precheck_45h.json` · `scripts/precheck_45h.py` ($0, no model call, no pod) |
| category measurements | `results/categories_45h.json` · `data/category_lexicon_draft.json` (`draft-not-law`) |
| migration pass | `results/migration_45h2.json` · `results/migration_45h2_rows.jsonl` · `scripts/migrate_intents_v4.py` |
| v4 | `scripts/freeze_testsets_v4.py` → `results/frozen_v4.json`; the card is `docs/frozen-testsets.md` §v4 |
| ledger | `results/spend_45h2.json` — OpenRouter $0.1080 of $0.30; GPU anchored at $27.5333, cap $9.00 |
| deviations | `implementation-notes.md` § Phase 4.5h2, D1–D18 |

Related: [[45g6-context-lines-probe]] — the KILL that turned the пласт into an ablation;
[[test-v3]] — what v4 derives from; [[taxonomy-v2-relabel-and-appetite]] — the law v4 materializes;
[[4b-training-contract]] — the frozen config this phase amended in one value;
[[45h2-ablation-verdict]] — the numbers.
