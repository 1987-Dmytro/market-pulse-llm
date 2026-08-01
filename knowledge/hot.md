<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-01 12:24:33 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
35c44c1 docs: baseline (c) is the own-pod row everywhere — and G1d's bar is 1.0084
50686ff docs: the second open question, and a phase-spend figure that names its clock
dc15f92 chore: the day's log for step 4a
c2eb510 docs: the 4a record — ADR, notes and hot.md
18a1b29 feat: the own-pod zero-shot row, and the G1b slice it defines
```

## 📋 Recent decisions

- `phase4-own-pod-anchor.md` — The own-pod zero-shot row anchors G1d/G1e, and it is the run that defines the G1b slice
- `INDEX.md` — Decision records
- `3b-infra-and-precision.md` — Phase 3b runs on OpenRouter at a pinned precision, not on a rented GPU

## 📅 Recent daily logs

- `2026-08-01.md`
- `2026-07-31.md`
- `2026-07-30.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-08-01 12:29 (4a ACCEPTED, amendment 3.5 lands — both blockers decided, step 4b opens; edited by hand — the section above is auto-generated, do NOT touch the marker)

## 🔥 What's Hot

**STEP 4a IS ACCEPTED (2026-08-01) and 4b is live** — the scorer's slice input, the QLoRA trainer
and a training smoke; **no full runs (4c) and no frozen set or holdout touched by anything in 4b**.
Phase 3 closed and committed (`952e5dd`); Phase 4 opened at the 2026-08-01 briefing with **SPEC
amendment 3.4** and the 4a acceptance added **amendment 3.5**. `make check` green after every
commit. Phases 1 and 2 accepted 2026-07-28; 3a/3b/3c 2026-07-31.
Registry: 4 live sources. Raw store 6 057 posts + 11 338 comments. **17 ADRs** ([[INDEX]]).

**The own-pod row is baseline (c) EVERYWHERE** — operator decision 2026-08-01, pre-registered
before 4b trains ([[phase4-own-pod-anchor]] §(f)). Not just the G1d/G1e anchor: SPEC §7 makes
zero-shot baseline (c) for every task, so G1a and G1c measure from it too. The OpenRouter row stays
in the Phase 3 table and is no longer a baseline candidate for any Tier-1 gate. **The bars, as
amendment 3.5 leaves them:** G1a overall **≥ 0.9418** (floors `ua` 0.8718 · `ru` 0.8649) ·
G1b **≥ 27 of 44** with the ≤2 pp macro-F1 guard · G1c **≥ 0.8436** · **G1d ≥ 0.8984** ·
**G1e ≥ 0.8874**. G1d/G1e are `anchor − 1 pp` **no-regression** gates now (3.5 (2) replaced
"+10 pp", which was unreachable on a saturated base); improvement is reported, never gated. **Every
one of those numbers is derived in code from the own-pod record — none is typed anywhere.**

**The own-pod row anchors G1d/G1e** ([[phase4-own-pod-anchor]]): `google/gemma-4-31b-it` at
revision `842da379…`, NF4 4-bit, RTX A6000, **758/758 rows scored, zero failures of any kind**,
`gate_anchor_valid: true`. Gated heads, own-pod vs its OpenRouter fp8 row:
G1a `ua` **0.8918** (-0.0039) · G1a `ru` **0.8849** (+0.0162) · G1c **0.7936** (-0.0046) ·
G1d **0.9084** (+0.0187) · G1e **0.8974** (-0.0236); relevance 0.9415, not gated. **The own-pod
number anchors regardless of the disagreement — nothing is averaged.** So G1d's 10 pp bar is now
measured from 0.9084 (harder than the Phase 3 table implied) and G1e's from 0.8974 (easier). The
selection of the base model is NOT reopened: one model re-measured on new hardware is not a paired
comparison against rows nobody re-measured.

**The G1b slice exists as a file: `results/g1b_slice.json`, n = 44**, sha256 in the record.
Sentiment errors **13 ⊂** sarcasm errors **44**, so the union is 44 — the containment the
OpenRouter preview showed at 10 ⊂ 40 held at different numbers. **44 < 100 → amendment 3.2's
pre-registered fallback**: report the smaller n beside the gate verdict, top nothing up. The
OpenRouter 40 was a preview and is now superseded.

**GREEDY IS NOT BATCH-INVARIANT on bitsandbytes NF4 + A6000.** Measured, not assumed: one probe
row of 24 came back with different intents at batch 8 than at batch 1, same weights, same prompt,
`do_sample: false`. **The run went at `--batch-size 1`** — 3.04 s/row, 39 min for 758 rows, $0.35,
against a 4 h/arm ceiling, so the correctness win was free. Batch 1's own claim was measured too:
the same 48-row probe twice, byte-identical labels. **4b's ablation arms inherit batch size 1**
unless someone re-measures on the training stack and records it.

**GPU money: $0.6456 of the $25 Phase 4 cap, read 10:15 UTC** ($0.6203 when the pod stopped at
09:52 — the volume bills continuously, so a phase figure without its timestamp is stale by
construction). `results/spend_phase4.json` anchors the balance at
$35.00 as of 2026-08-01T08:34:09Z — **never regenerate it**, same footgun as `spend_3b.json`.
`scripts/runpod_guard.py` refuses at the cap and on a mid-phase top-up. Pod `gxkdecf3g7k3y7`
**EXITED**; network volume `gfwa2an8fn` (100 GB, CA-MTL-3) **kept on purpose** for 4b — it bills
~$7/month whether or not a pod is attached, which is why the guard reads the account balance and
not just the pod billing rows.

**One writer per file, and the layer is live** (`2b423c8`): `docs/STATUS.md`, `docs/SPEC.md` and
`docs/PROMPT-*.md` are **team-lead files** — read them, commit them verbatim, never edit them;
everything else is the executor's. Deny rules in `.claude/settings.json` refuse **both `Edit` and
`Write`** on those three (on Claude Code 2.1.220 only `Edit(path)` rules are consulted, and they
cover every writing tool — a `Write(path)` rule would be dead). Re-probed 2026-08-01 with the
Write tool on `docs/STATUS.md`: *"File is in a directory that is denied by your permission
settings."*, and the file was not touched.

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
G1b is `null` everywhere: its fix-rate needs a fine-tune. That table is the **Phase 3** table and
its gemma column is the OpenRouter row; the own-pod row is a Phase 4 row and lives above. **The G1b
slice question is closed**: 44 ids in `results/g1b_slice.json`, measured on our own pod — the
preview's 40 is superseded.

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

1. **Step 4b, live** (`docs/PROMPT-4b.md`): the scorer learns the slice file (amendment 3.5 (3)),
   `scripts/train_qlora.py` + a committed hyperparameter config, and ONE pod session for a
   40–60-step training smoke on the real-only arm. Frozen sets and the holdout stay shut.
2. **Team-lead review of 4b**, then **4c**: the two ablation arms (with and without
   `synthetic_sarcasm.jsonl`, identical config and seed, one data path differing) and the gates,
   one attempt. The selection rule is fixed: the synthetic source stays **iff** its arm's G1b
   fix-rate is strictly higher **and** no other gated head is lower by more than 0.5 pp; both
   columns published, no third run, no retraining after gate numbers are seen. 4b's smoke must
   project the full run and a projection over **4 h per arm** stops the line.
3. Still open from Phase 2 (not a blocker): dataset cards for the public augmentation datasets +
   licence check.

## 🚧 Blockers

**None open.** Both of 4a's escalations came back decided at the acceptance, in **SPEC amendment
3.5** — the executor flagged, the operator ruled, nothing was worked around:

- **G1d's unreachable bar → 3.5 (2).** "+10 pp" is replaced by a no-regression gate, fine-tuned
  ≥ anchor − 1 pp (G1d ≥ 0.8984, G1e ≥ 0.8874); improvement is reported beside the verdict and
  never gated. The spec records the ordering honestly (the impossibility was arithmetically
  visible in the 3b numbers on 2026-07-31 and was named only at the 4a acceptance) and records
  why the rescaled-ambition alternative — relative error reduction ≥25% — was rejected: near the
  ceiling it collides with label noise. **The phase's ambition burden now lies on G1a, G1b, G1c;
  T2's heads gate forgetting.**
- **The scorer could not read the slice file → 3.5 (3),** which is a team-lead instruction to
  change the fix-rate function: it takes the 44 ids explicitly, FIXED means correct on **both**
  sentiment and sarcasm, the rate is fixed/44 and the gate is **≥27**. Executed in 4b Step 1.

**This Mac's device numbers, if anything is ever trained locally again:** 2 193 steps across
9 heads, **CPU 3.5 s/step**, **MPS 48.1 s/step** and OOM at 9.07 GiB unless the 250k×768 embedding
matrix is frozen. Local training is an evening job, not an interactive one — and CPU beats MPS by
14×, which is the opposite of the intuition.

## ⚠️ Footguns for the next run

- **`results/spend_phase4.json` is the $25 cap's anchor and must not be regenerated.** It stores
  the RunPod balance as Phase 4 opened; delete it and the counter silently restarts at today's
  balance. The guard also refuses when the balance is *above* the anchor — a mid-phase top-up means
  the delta stopped measuring this phase, and re-anchoring is an operator decision.
- **A stopped pod is not a stopped bill.** The 100 GB network volume bills by the month with no pod
  attached. `runpodctl billing pods` cannot see it; only the account-balance delta can, which is why
  the guard reads both and takes the larger.
- **`runpodctl pod list` shows running pods only.** An empty list is "nothing running", not
  "nothing exists". Use `pod list -a` or `pod get <id>` to show a stopped pod's `EXITED` state.
- **Network volumes live in a different datacenter set than the A6000 does.** `EU-SE-1` had the
  best A6000 stock and takes no volumes at all; the intersection was `CA-MTL-3`. Pick on the
  intersection or pay for a second volume.
- **`RUNPOD_POD_ID` is not inherited over ssh** — export it in the run command or the record's
  `runtime.pod_id` is `None` and the number cannot name its machine.
- **The RunPod PyTorch image's python is PEP 668 managed.** `pip install` refuses; use
  `python3 -m venv --system-site-packages` so the image's CUDA-matched torch is reused rather than
  a 3 GB re-download of a possibly different build.
- **Greedy decoding is NOT batch-invariant on bitsandbytes NF4 + A6000** — measured 2026-08-01, one
  row of 24 flipped its intents between batch 8 and batch 1. Every gate run goes at `--batch-size 1`
  until someone re-measures and records the result. Batch 1 is run-to-run identical, also measured.
- **`add_special_tokens=False` is load-bearing and now asserted.** Gemma 4's chat template emits
  `<bos>` itself; a template revision that stopped would silently make every prompt worse, so
  `LocalClient` refuses to construct if the rendered prompt does not start with the BOS token.
- **Gemma 4 has a thinking channel.** `enable_thinking=False` + `add_generation_prompt=True` emits
  an already-closed `<|channel>thought\n<channel|>` — the local equivalent of 3b's
  `reasoning: {"enabled": false}`. It is the current default and is passed explicitly anyway: with
  thinking on, `parse_reply` would read the first brace inside the reasoning text.
- **A `--probe` is not a smoke test unless it prints rows.** Aggregate counts are identical whenever
  two configurations merely parse, so a check built on them cannot fail. The batch-invariance check
  diffs the per-row prediction lines and guards with `test -s` — two crashed probes produce two
  empty files, and `diff` on those is silent success.

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
