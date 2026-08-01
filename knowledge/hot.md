<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-01 10:02:40 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
759f72d chore: the day's log, hot.md and the index as /close left them
a5f5907 docs: phase 3 closed, as the team lead left it
2b423c8 chore: one writer per file — deny rules, command write-lists, the matrix
8fc81ff chore: hot.md and the log catch up with the finished run
ffcb33e chore: the day's log, hot.md and the index as /close left them
```

## 📋 Recent decisions

- `3b-infra-and-precision.md` — Phase 3b runs on OpenRouter at a pinned precision, not on a rented GPU
- `INDEX.md` — Decision records
- `phase4-base-model-gate.md` — Phase 4 base model = google/gemma-4-31b-it, and the unpaired 27B row cannot flip that

## 📅 Recent daily logs

- `2026-08-01.md`
- `2026-07-31.md`
- `2026-07-30.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-08-01 (`/close` of the 2026-07-31 workday, run just past midnight; edited by hand — the section above is auto-generated, do NOT touch the marker)

## 🔥 What's Hot

**PHASE 3 IS CLOSED — accepted 2026-07-31 late evening. Phase 4 is next**, and its entry
conditions are a RunPod top-up and the briefing (see Next). Phases 1 and 2 DONE and accepted
(2026-07-28); 3a, 3b and 3c all landed on 2026-07-31 — 202 tests, `make check` green after every
commit, **$0.9201 spent of the $8 cap**, the supervised baseline at $0 on this Mac. SPEC APPROVED
rev. 3 + amendments 3.1, 3.2, **3.3**. Registry: 4 live sources. Raw store 6 057 posts + 11 338
comments. 16 ADRs in `knowledge/decisions/` ([[INDEX]]).

**One writer per file, and the layer is live** (`2b423c8`): `docs/STATUS.md`, `docs/SPEC.md` and
`docs/PROMPT-*.md` are **team-lead files** — read them, commit them verbatim, never edit them;
everything else is the executor's. Deny rules in `.claude/settings.json` refuse **both `Edit` and
`Write`** on those three (on Claude Code 2.1.220 only `Edit(path)` rules are consulted, and they
cover every writing tool — a `Write(path)` rule would be dead), proved by refusal on all three
files with `docs/WATCHLIST.md` as the negative control. `docs/STATUS.md` carries the team lead's
Phase-3 closure **uncommitted in the tree** at this close — commit it as it is.

**Phase 4's base model is `google/gemma-4-31b-it`** ([[phase4-base-model-gate]]) — ahead on every
gated head among the candidates, ahead of the Haiku reference row on four cells of five (Haiku
takes G1a `ru` by 0.0300; a reference row never anchors a gate). The 27B row's unpairedness was
closed by a **worst-case bound analysis at $0**, and every head survived: bound vs gap G1a `ua`
0.0186/0.0421 · G1a `ru` 0/0.0021 · G1c 0.0087/0.0376 · G1d 0.0037/0.1293 · G1e 0/0.0292. The
27B rows keep `gate_anchor_valid: false` permanently. **Read the `ru` cell twice**: a 0.0021 lead
against a 0.0298 same-config swing measured on a re-run — on `ru` the two are tied inside
third-party noise, and the selection rests on the other four gaps.

**XLM-R is DONE, committed and accepted** — 2026-07-31 on this Mac's CPU, **101.0 min against its
own 128.0 projection**, no crash and no restart, provenance checked (the record's `git.commit` is
`6d4deb3` with only `knowledge/*` dirty). Row `87e3327`. **The Phase 3 baseline table is
complete**, and the row does not move the Phase 4 choice: XLM-R beats `tfidf-logreg` on G1a by
0.0990 and G1d by 0.0694, ties it on G1c (0.6007 vs 0.6000), and is under `gemma-4-31b-it` on
every comparable cell. Its `holdout_sarcasm_detected 54/108` is a **negative-lean diagnostic**
(107 of those 108 rows are negative), not irony reading and not the G1b slice.

**The baseline table** (`results/baselines.json`, read only via `scripts/show_results.py`),
G1a overall / G1c / G1d 3-class / G1e:
`tfidf-logreg` 0.6834 / 0.6000 / 0.6653 / 0.1964 · **gemma-4-31b-it 0.8944 / 0.7981 / 0.8898 /
0.9211** · qwen3.6-27b 0.8541 / 0.7606 / 0.7605 / 0.8919 (`gate_anchor_valid: false`) ·
qwen3.5-9b 0.7745 / 0.6252 / 0.5077 / 0.6476 · **xlm-roberta-base 0.7824 / 0.6007 / 0.7347 /
NOT COVERED** (per-language G1a: `ua` 0.7859 · `ru` 0.7507 · `other` 0.7575; relevance 0.6610
reported beside G1d, not gated) · ref `claude-haiku-4.5` 0.8708 / 0.7739 / 0.7718 / 0.8537.
G1b is `null` everywhere: its fix-rate needs a fine-tune. **The G1b slice = the union of
sentiment ∪ sarcasm errors, and it is defined by the chosen model's re-run on our own pod during
the Phase 4 smoke** — OpenRouter's 40/108 is a preview, not the slice.

**3b ran on OpenRouter at pinned fp8** ([[3b-infra-and-precision]]), not on a rented GPU: 758
short requests per model is a token bill, not a GPU-hour. fp8 because `qwen/qwen3.6-27b` offers no
bf16 endpoint anywhere and the rule was fixed before the probe. Pins `parasail/fp8` ·
`io-net/fp8` · `venice/fp8`, `allow_fallbacks: false`. Gemma 4's licence is **Apache-2.0**.

**The scorer computes, and it is the only thing that may.** `src/market_pulse/scorer.py` holds
every gate function plus a public `macro_f1` so diagnostics use the same arithmetic. Two
conventions the numbers hang on: macro averages run over the labels **gold** supports (never over
what a model predicted — that breaks paired comparison), and the `unclear` exclusion lives in the
scorer, driven by a sentinel the caller passes. Both pinned by hand-computed tests; a public
function without one fails the suite.

**Frozen test sets are at v2** — `docs/frozen-testsets.md` has the hashes, changelog and per-gate
depth. comments 400/1600, posts 250/750, thread-disjoint, zero `unclear` in test. **Training data
is three files**: `comments_train.jsonl` (1600) + `sarcasm_candidates.jsonl` (746) — 230 sarcastic
scoreable rows between them — plus `synthetic_sarcasm.jsonl`, 600 generated rows, **ablation-gated,
QA passed 2026-07-30** ([[synthetic-sarcasm-augmentation]]). **G1b's holdout** is 108 rows, all
`sarcasm: true`, thread-disjoint from test and train ([[hybrid-sarcasm-holdout-3.2]]).

## ⏭️ Next

1. **RunPod top-up ~$30–40** — the operator's call, owed before any training
   ([[gpu-provider-runpod]]). At a $0 balance, pods without a network volume are deleted
   irreversibly.
2. **Phase 4 briefing** — a joint working session, not a prompt. Settles the LoRA fork and
   schedules the chosen model's **zero-shot re-run on our own pod** — the cross-check against its
   third-party-served row, the run that defines the **G1b slice**, and the anchor for G1d/G1e.
   Also on the agenda: the synthetic-ablation plan, and G1a–e as **one pre-registered attempt**.
   **Working hypothesis: branch (2), 4-bit QLoRA on an A6000** — Gemma-4-31B needs
   ~70 GB in bf16, which does not fit a 48 GB A6000, and production is the quantized serverless
   path decided 2026-07-28. Training cost is NOT the deciding argument (~2 950 short rows, 1–1.5 h,
   single dollars apart); the criterion is **train in the precision you serve**. Confirmed at the
   briefing, not before. Three branches in `docs/STATUS.md`.
3. Still open from Phase 2 (not a blocker): dataset cards for the public augmentation datasets +
   licence check.

## 🚧 Blockers

**None.** Phase 3's one blocker — XLM-R over its 60-minute ceiling on both devices — was lifted by
the operator and the run finished clean in 101.0 min.

**Uncommitted in the tree at this close, by design:** `docs/STATUS.md`, the team lead's Phase-3
closure. The executor commits it **verbatim** and never edits it (the deny rules make that
mechanical, not a matter of care).

**This Mac's device numbers, if anything is ever trained locally again:** 2 193 steps across
9 heads, **CPU 3.5 s/step**, **MPS 48.1 s/step** and OOM at 9.07 GiB unless the 250k×768 embedding
matrix is frozen. Local training is an evening job, not an interactive one — and CPU beats MPS by
14×, which is the opposite of the intuition.

## ⚠️ Footguns for the next run

- **`docs/STATUS.md`, `docs/SPEC.md`, `docs/PROMPT-*.md` are team-lead files.** Read and commit,
  never edit — the deny rules refuse `Edit` *and* `Write` on them, without a restart. Phase-end
  facts go to the daily log or `implementation-notes.md`. The refusal reads "File is in a directory
  that is denied", but the rules are file-scoped: the rest of `docs/` is still writable.
- **A ceiling lifted by the operator is not a ceiling lifted in code.** `train_xlmr_baseline.py`
  refuses to train above `--time-budget-min` and exits **3** — it prints a projection and leaves no
  process, which reads exactly like a crash. Grep your own guards before any unattended launch.
- **The six 3b zero-shot records carry no per-row predictions — never claim paired re-scoring from
  them.** They hold `scored_ids_sha256` (a hash of the id list) and error counts, nothing that can
  be re-scored. Dumps exist only from step 3c onward, and the six are **not** backfilled: they
  cannot be reconstructed and a synthesized dump would be worse than the gap.
- **A prediction dump must be sorted before it is hashed.** Rows come back from four workers; a
  digest in completion order is a hash of the scheduler, not of the data. And it carries ids and
  predicted labels **only** — no gold, no source text, or it becomes a second copy of a frozen file.
- **`results/spend_3b.json` is the $8 cap's anchor and must not be regenerated.** It stores the
  lifetime OpenRouter usage as of the first 3b request; delete it and the next run re-anchors at
  today's usage, silently resetting the phase counter to zero.
- **Never use `anthropic/claude-haiku-4.5:batch`** — served only through `/api/beta/batches`, 404s
  on `/chat/completions`. The runner refuses the slug on purpose.
- **The reference row is marked in the record, not just the filename.** `build_record` rewrites
  every `gate` field of a `--reference-only` run to `ref`, so a lookup for `G1d` cannot find it.
  Do not "fix" those entries back to gate ids.
- **A run that trips the cap writes no record** — a partial run must never become a gate anchor.
  Do not re-run with a bigger `--max-run-usd` to get the record.
- **`GET /api/v1/generation?id=` 404s for our generations** at every delay tried (2 s to 60 s).
  Spend reads `usage.cost` and reconciles against `/credits`; do not "restore" that path.
- **Endpoint health readings are point-in-time.** The pins were chosen on status/uptime as read at
  pin time; `deepinfra/fp8` was deranked then and healthy hours later. The precision *rule* is
  pre-registered; re-pinning a provider is legal — but say so if you do it.
- **`scripts/freeze_testsets.py --force` would rebuild the split and destroy v2.** A fresh draw
  differs from v2 by 8 rows. Do not run it. Likewise `mine_sarcasm_candidates.py --force`
  (746 hand labels) and `mine_sarcasm_holdout.py --force` (971); `refreeze_v2.py`,
  `sync_batch_v2.py` and `freeze_sarcasm_holdout.py` are one-shot.
- **`data/annotation/sarcasm_holdout_pool.jsonl` is not training data** — its non-sarcastic rows
  share threads with the holdout.
- **Never merge `synthetic_sarcasm.jsonl` into a real-source file.** The Phase-4 ablation has to
  drop it by dropping one path. `data/annotation/*` is gitignored, so the file survives only
  through an explicit `!` exception — do not "tidy" that line away.
- **The generated rows passed QA but carry no QA number, and that is not an oversight.** ≥80% `ok`
  was pre-registered before the 50-row draw; the operator ruled it passed without returning the
  marked-up CSV. The executor never scores its own sample (SPEC §10), so the empty
  `operator_verdict` column stays empty. The ADR is the authority on the verdict.
- **The freeze shrank `sarcasm_candidates.pristine.jsonl` 800 → 746** so the validator would not
  read the moved rows as lost. Legitimate once, audited — but the validator can be silenced the
  same way again. Any further row loss must be diffed against the baseline before it is believed.
- **`results/baselines.json` is append-only and never hand-edited.** Numbers reach it only through
  the scorer; `scripts/show_results.py` only reads. A hand-typed number there is invisible.
- **A results record cannot name the commit that contains it**, so provenance is `commit` + the
  `dirty` paths at run time; the runner shouts if any is under `src/`, `scripts/` or `config/`.
- sklearn lives in the `baseline` extra and torch/transformers in `xlmr` — no test may import
  either, or `make check` stops being runnable on a bare checkout.
- `RAW_STORE_SALT` in `.env` must never be rotated: a new salt orphans every `sender_anon_id`.
- `packaging` has 19 rows in the test set — G1c is thin by construction, not by accident.
- **Do not merge a QLoRA adapter into bf16 base weights without measuring it (Phase 5).** An
  adapter trained against a 4-bit NF4 base learned to compensate THAT base's quantization error;
  merged into unquantized weights it corrects errors that are no longer there. Second-order but
  measurable — so measure it: score the final artefact in the EXACT configuration that will serve
  production. Safe default: serve the same 4-bit base plus the adapter, unmerged.
- **XLM-R cannot do G1e** without a token-classification head. An empty G1e cell means "not
  attempted", never "scored zero" — the two must never be conflated in a comparison table.

## 🐞 Known harness bug

Fixed 2026-07-28: `knowledge/templates/daily-log.md` now carries `{{DATE}}`, the placeholder
`scripts/brain-session-end.py` actually substitutes; `tests/test_templates.py` keeps the pair
honest.
