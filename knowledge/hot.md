<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-07-31 18:05:17 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
6d4deb3 chore: hot.md at the gate's close, plus the team-lead files as they were left
8918709 feat: every scoring run dumps its per-row predictions
632b40c docs: the base-model gate, and the bound that closes the unpaired row
6017721 docs: qwen3.6-27b re-run, and STATUS.md brought up to 3b's close
5b723af docs: the three candidate rows are not paired, and the install form used
```

## 📋 Recent decisions

- `3b-infra-and-precision.md` — Phase 3b runs on OpenRouter at a pinned precision, not on a rented GPU
- `INDEX.md` — Decision records
- `phase4-base-model-gate.md` — Phase 4 base model = google/gemma-4-31b-it, and the unpaired 27B row cannot flip that

## 📅 Recent daily logs

- `2026-07-31.md`
- `2026-07-30.md`
- `2026-07-28.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-07-31 (`/close`; edited by hand — the section above is auto-generated, do NOT touch the marker)

## 🔥 What's Hot

**Phases 1 and 2 DONE and accepted** (2026-07-28). **Phase 3a done.** **Phase 3b done and
accepted** at the gate review of 2026-07-31 — 202 tests, `make check` green after every commit,
**$0.9201 spent of the $8 cap**. SPEC APPROVED rev. 3 + amendments 3.1, 3.2, **3.3**. Registry:
4 live sources. Raw store 6 057 posts + 11 338 comments. 16 ADRs in `knowledge/decisions/`
([[INDEX]]).

**Phase 4's base model is `google/gemma-4-31b-it`** ([[phase4-base-model-gate]]) — ahead on every
gated head among the candidates, ahead of the Haiku reference row on four cells of five (Haiku
takes G1a `ru` by 0.0300; a reference row never anchors a gate). The 27B row's unpairedness was
closed by a **worst-case bound analysis at $0**, and every head survived: bound vs gap G1a `ua`
0.0186/0.0421 · G1a `ru` 0/0.0021 · G1c 0.0087/0.0376 · G1d 0.0037/0.1293 · G1e 0/0.0292. The
27B rows keep `gate_anchor_valid: false` permanently. **Read the `ru` cell twice**: a 0.0021 lead
against a 0.0298 same-config swing measured on a re-run — on `ru` the two are tied inside
third-party noise, and the selection rests on the other four gaps.

**XLM-R was IN FLIGHT at close** — launched 2026-07-31 17:43 on this Mac's CPU, PID 3931,
projected 128.0 min. First job of the morning is `tail -n 30 xlmr_full_run.log`, then
`scripts/show_results.py --model xlm-roberta-base`, then commit the record. See Blockers for what
a finished and a dead run look like.

**The baseline table so far** (`results/baselines.json`, read only via `scripts/show_results.py`),
G1a overall / G1c / G1d 3-class / G1e:
`tfidf-logreg` 0.6834 / 0.6000 / 0.6653 / 0.1964 · **gemma-4-31b-it 0.8944 / 0.7981 / 0.8898 /
0.9211** · qwen3.6-27b 0.8541 / 0.7606 / 0.7605 / 0.8919 (`gate_anchor_valid: false`) ·
qwen3.5-9b 0.7745 / 0.6252 / 0.5077 / 0.6476 · ref `claude-haiku-4.5` 0.8708 / 0.7739 / 0.7718 /
0.8537. G1b is `null` everywhere: its fix-rate needs a fine-tune. **The G1b slice = the union of
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

1. **Commit the XLM-R record** (see What's Hot). Its **G1b is `null`** and its **G1e says NOT
   COVERED** — "not attempted", never "scored zero", in any comparison table.
2. **Close Phase 3** — team lead's, once the baseline table is complete.
3. **RunPod top-up**, deferred to the Phase 4 gate by operator decision, still owed before any
   training ([[gpu-provider-runpod]]).
4. **Phase 4 briefing.** Settles the LoRA fork and schedules the chosen model's **zero-shot re-run
   on our own pod** — the cross-check against its third-party-served row *and* the run that defines
   the G1b slice. **Working hypothesis: branch (2), 4-bit QLoRA on an A6000** — Gemma-4-31B needs
   ~70 GB in bf16, which does not fit a 48 GB A6000, and production is the quantized serverless
   path decided 2026-07-28. Training cost is NOT the deciding argument (~2 950 short rows, 1–1.5 h,
   single dollars apart); the criterion is **train in the precision you serve**. Confirmed at the
   briefing, not before. Three branches in `docs/STATUS.md`.
5. Still open from Phase 2: dataset cards for the public augmentation datasets + licence check.

## 🚧 Blockers

**None.** The day's one blocker — XLM-R over its 60-minute ceiling on both devices — was lifted by
the operator and the run launched the same evening.

**Reading the overnight run.** Finished: the log ends with `full run took … min (projected 128.0)`
and `wrote results/baselines.json`. Dead: it stops mid-head with no such line and no new record —
nothing is corrupted, the file is written only at the end, and it restarts with
`caffeinate -i nohup python3.11 scripts/train_xlmr_baseline.py --device cpu --time-budget-min 600
> xlmr_full_run.log 2>&1 &`. **`caffeinate -i` suppresses idle sleep only** — lid open, Mac on
mains. The measurement that produced the blocker still stands and is why it runs overnight:
2 193 steps across 9 heads, **CPU 3.5 s/step → ~130 min**, **MPS 48.1 s/step → 1764 min** (and MPS
OOMs at 9.07 GiB unless the 250k×768 embedding matrix is frozen, which it is).

What must NOT happen even now that the clock is open: fewer epochs, a shared-encoder rewrite, a
shorter `MAX_LENGTH`. Each is tuning a pre-registered baseline to a wall clock.

## ⚠️ Footguns for the next run

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
