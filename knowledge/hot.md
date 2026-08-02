<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-02 16:51:53 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
471cc64 feat: the returns normalized into the sealed pack, one column at a time
62784c8 docs: the audit returns — prompt 4.5b
492502c test: one blinding check, one word list
64ac276 docs: the homoglyph finding, filed with the reason it stays unfixed
bc88a9f feat: control 40 -> 104, and a harness that refuses a spreadsheet's column
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `phase45a-ceiling.md` — The 4.5a ceiling: 244 blind verdicts, and what each head can score at best
- `phase4-gate-verdict.md` — The one attempt: two arms trained, each scored once, and the Tier-1 gates decided

## 📅 Recent daily logs

- `2026-08-02.md`
- `2026-08-01.md`
- `2026-07-31.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-08-02 16:50 (`PROMPT-4.5b` executed — **244/244 verdicts ingested and the approved harness has RUN ONCE**; the per-head ceilings are in [[phase45a-ceiling]] (`proposed`) and the 4.5a gate review is next. Phase 4 stays closed at 2 of 5; edited by hand — the section above is auto-generated, do NOT touch the marker)

## 🔥 What's Hot

**THE 244 VERDICTS ARE IN AND THE CEILINGS ARE COMPUTED (2026-08-02) — awaiting the 4.5a gate
review.** The numbers, per head, metric-unit first (upper bound, disagreements only) then the
accuracy band over both strata: **sentiment 0.9613 macro-F1 · 0.9625** · **intents 0.9148 micro-F1
· 0.4596..0.4646** · **sarcasm_pair 0.6591 fix-rate · 0.6591** · **post_type 0.9683 macro-F1 ·
0.9800**. G1e is excluded from the ceiling arithmetic (team-lead decision 02.08) and contributes
raw verdict counts only: 4 disagreements (gold wrong 3), control 8 (incorrect 1). **The two units
do not bound each other and neither is a gate bar** — read [[phase45a-ceiling]] before quoting any
of them. Gold-wrong in the disagreement stratum: 15/35 · 31/67 · 15/23 · 5/11. Control `incorrect`:
**22 of the 23 fall in `intents`** (22 of its 40 rows), everything else is 0 except brands 1 of 8.
**The decisions that follow belong to the gate review, not to this record.**

**Amendment 3.7 inserted Phase 4.5 — a ceiling-driven quality program — before Phase 5**, because
the operator's 0.98 target sits above the instrument: comment gold was calibrated at 96.3%
agreement. The adjudication pack is `data/annotation/audit_45a/` (gitignored data;
`scripts/build_audit_pack.py` is the committed, deterministic builder, seed 42): 140 blinded
disagreements — sentiment **35** · intents **67** · slice pair **23** · posts **15** (post_type 11 +
brands 4) — plus **control 104** (sentiment 40 · intents 40 · the other three 8 each). **Every
disagreement row showed two candidate labels as `label_A`/`label_B` in per-row random order and
NOTHING said which was whose** — the key is `data/annotation/audit_45a_key.json`, outside the folder
the operator opened, sha-pinned in `results/audit_45a_manifest.json`. **The executor pre-filled,
suggested and commented on nothing** (SPEC §10). Nothing was judged, re-scored, or written back to a
frozen file.

**The returns were normalized, not retyped.** The operator's five CSVs came back through a
spreadsheet (semicolons, verdicts as `B — правильная метка label_B`);
`scripts/normalize_audit_returns.py` maps the five forms by table, derives every verdict twice
(table and leading token must agree), refuses any return set outside the team lead's five pinned
sha256, and rebuilds each row from the **sealed** row with one cell replaced — then blanks the
verdicts again and requires the sealed bytes back. Verified outside the script: **244 verdict cells
filled, 0 non-verdict cells changed**, and the tallies reproduce the team lead's independent count
(A19/B16 · A32/B33/amb2 · A3/B20 · A7/B8 · 81/23). Every sha is in
`results/audit_45b_returns.json`.

**The expansion did not resample the accepted pack.** All four disagreement CSVs and the key are
byte-identical to the accepted build, and the accepted 40 control rows are present verbatim inside
the 104: every head draws its first 8 before any head draws a top-up, so the seeded stream that
produced them is untouched. Widening a stratum by resampling it would make "the same pack,
expanded" a claim nobody could check.

**`scripts/audit_ceiling.py` HAS RUN, once, on the filled pack** — every refusal passed on the way
(key sha256, no empty cell, no unknown column, no edited label, row counts against the key). It
prints **two ceilings that are not interchangeable**: the *metric-unit* one re-scores a simulated
perfect model through `scorer.py` (comparable to a G1a/G1c bar, and an **upper bound** — it sees
only the disagreement stratum), and the *accuracy-unit* one counts both strata and is **not
comparable to an F1 bar**. The agreement stratum is ~90% of every head, so the harness prints a
sensitivity line beside the point estimate. **What the expansion bought:** one extra `incorrect`
now moves sentiment **2.28 pp** and intents **2.08 pp**, against **11.41** and **10.41 pp** at n=8.
The other three heads still sit at n=8 and their ceilings are read at that resolution.

**PHASE 4 IS CLOSED AT 2 OF 5 (2026-08-02) — accepted, and the one attempt is spent.** The team
lead recomputed every verdict number **bit-exact from the per-row dumps**, re-ran the selection
rule (output matched word for word), confirmed the one-attempt protocol from artefacts, and the
operator's quiz came back **2/2**. [[phase4-gate-verdict]] is `accepted`. Both ablation arms
trained in full on the frozen config, each scored on the frozen sets **exactly once**; **nothing
was retrained, re-scored or reconfigured after a gate number was seen** — arm B launched while arm
A's three failures were already on screen. **348 tests**, `make check` green after every commit.
**21 ADRs** ([[INDEX]]).

**THE DELIVERABLE: `results/train/4c-arm-a/adapter`** — the real-only LoRA adapter, sha256
`c0e462af81aad9f1…`, served **UNMERGED** on the same NF4 4-bit base every gate was scored through.
**Phase 5 is PAUSED** and Phase 4.5 (quality program, amendment 3.7) comes first — an operator
sequencing decision.

**THE VERDICT: 2 of 5 Tier-1 gates pass, on the real-only arm.**
G1d **0.9386** ≥ 0.8984 **PASS** · G1e **0.9333** ≥ 0.8874 **PASS** ·
G1a **0.9107** < 0.9418 FAIL · G1b **21/44** < 27 FAIL · G1c **0.8212** < 0.8436 FAIL.
The two that pass are the no-regression gates of amendment 3.5 (2), and they pass by **+3.02** and
**+3.59 pp above the anchor**, not by holding a line — the multi-task forgetting risk they were
rewritten to measure did not materialise. The three that fail are margin gates and they fail **by
margin, never by regression**: every gated head of both arms is above the zero-shot anchor. G1a
asked +5 pp and got +1.89, G1c asked +5 pp and got +2.76, G1b needed 27 of the base model's own 44
errors and fixed 21. A failed gate closes its question (SPEC §5) — nothing is retried.

**THE SYNTHETIC SOURCE IS DROPPED, on the half of the rule it was written for.** with-synthetic won
G1b outright — **24/44 against 21/44**, the largest single-head move either arm made — and lost the
second clause: G1c −1.39 pp and G1d −2.27 pp, both past the 0.5 pp tolerance. Exactly the trade
amendment 3.4 (3) pre-refused before any number existed. **Read this beside it and do not confuse
it with the verdict:** with-synthetic's G1a `ru` is **+4.44 pp** over real-only (0.9364 vs 0.8919),
the biggest per-language gap in the table — the strongest sign the generated Russian rows did
something real, and it changed nothing, because the rule was fixed first. Both columns are
published; there is no third run.

**Both arms, every gated head** (anchor → real-only → with-synthetic):
G1a overall 0.8918 → **0.9107** → 0.9172 · `ua` 0.8918 → 0.9146 → 0.9171 · `ru` 0.8849 → 0.8919 →
**0.9364** · G1b — → **21/44** → 24/44 · G1c 0.7936 → **0.8212** → 0.8073 · G1d 0.9084 →
**0.9386** → 0.9159 · G1e 0.8974 → **0.9333** → 0.9577 · relevance (not gated) 0.9415 → 0.9894 →
0.9891. Both arms' ≤2 pp G1b guard is **positive** (+0.0189, +0.0254): neither traded overall
sentiment for the slice.

**What G1b's failure is made of** — read off the committed dumps, nothing re-scored: of the 23
slice rows real-only misses, **15 are wrong on sarcasm only, 8 on both, 0 on sentiment only**. On
the full 108-row holdout (every row gold `sarcasm: true`) real-only detects **82** and
with-synthetic **83**, against the base model's **64**. Both arms moved that head ~19 rows and
neither cleared a bar defined as 60% of the base model's own errors.

**Beside the deliverable:** merging into bf16 stays forbidden until measured. The with-synthetic
adapter (`0566900e3f42451e…`) is kept next to arm A's — the ablation's second column is evidence,
not waste.

**Both arms ran clean and inside every box.** Arm A **270 steps in 3.40 h**, arm B **346 steps in
4.17 h** — both under 4b's own projections (3.42 / 4.37 h) and well under the 5 h ceiling. Peak GPU
30.86 / 30.84 GB of 48; micro-batch 2 × accum 8 held throughout, the OOM branch never fired.
**758/758 rows scored on both evals with zero failures of any kind** — no parse, no generation, no
truncation. Adapter hashes computed on the pod and on the Mac matched before either record was
appended.

**RESUME IS PROVED against the real stack** — 4b's [[4b-training-contract]] §(h) question, closed
in the first ten minutes of the first pod. Ten steps, reload with `is_trainable=True` onto the
k-bit base, `torch.load` of a real 238 MiB paged-AdamW state, five more steps: the optimizer step
counter continued (10 → 15, no reset) and the loss stayed on trajectory (0.10974 → **0.05680**,
carve 0.11247 → 0.05915). `assert_resumable` — added for this — stayed silent.

**TRAINING IS NOT BIT-REPRODUCIBLE ON THIS STACK.** Arm A's step-5 loss is **0.18010**; the resume
proof, on identical data, identical seed 42 and identical config on the same pod, gave **0.18051**.
Cause not isolated — NF4 reduction order (the family 4a measured when greedy turned out not to be
batch-invariant) or the `lora_dropout: 0.05` mask sequence. **Say "the ablation is paired on data
and config", never "identical"**; amendment 3.4 (3)'s "identical config and seed" reads stronger
than the hardware delivers, and the rule's 0.5 pp tolerance is what absorbs it.

**GPU money: $6.9903 of the $25 cap; remaining $18.01**, read at the close-out after the last pod
was deleted. 4c itself cost **$5.74** against ~$5.2 projected. **No pods exist any more** —
`pod list -a` is empty; the stale 4a pod `gxkdecf3g7k3y7` was deleted here. **The 100 GB CA-MTL-3
network volume `gfwa2an8fn` is KEPT on purpose** — its fate is a Phase 5 briefing decision, and it
is the only thing still billing (~$7/month, and the $0.11 between the 00:00 reading and the
close-out reading is what that looks like).

**The own-pod row is baseline (c) EVERYWHERE** — operator decision 2026-08-01
([[phase4-own-pod-anchor]] §(f)). **The bars, as amendment 3.5 leaves them:** G1a overall
**≥ 0.9418** (floors `ua` 0.8718 · `ru` 0.8649) · G1b **≥ 27 of 44** with the ≤2 pp macro-F1 guard ·
G1c **≥ 0.8436** · **G1d ≥ 0.8984** · **G1e ≥ 0.8874**. **Every one is derived in code from the
own-pod record — none is typed anywhere**; `PYTHONPATH=src python3 scripts/gate_bars.py` prints the
table and `scripts/gate_verdict.py` prints the rule's arithmetic and the verdicts.

**The own-pod row anchors G1d/G1e** ([[phase4-own-pod-anchor]]): `google/gemma-4-31b-it` at
revision `842da379…`, NF4 4-bit, RTX A6000, **758/758 rows scored, zero failures**,
`gate_anchor_valid: true`. Gated heads: G1a `ua` **0.8918** · `ru` **0.8849** · G1c **0.7936** ·
G1d **0.9084** · G1e **0.8974**; relevance 0.9415, not gated. **The own-pod number anchors
regardless of the OpenRouter disagreement — nothing is averaged.**

**The G1b slice is a file: `results/g1b_slice.json`, n = 44**, sha256 in the record and verified on
every load. Sentiment errors **13 ⊂** sarcasm errors **44**. 44 < 100 → amendment 3.2's
pre-registered fallback: report the smaller n beside the verdict, top nothing up. **An arm READS
this file and never writes it** — `build_gates` returns `None` for the slice on the fine-tuned
branch, so `write_slice` cannot be reached even by accident.

**GREEDY IS NOT BATCH-INVARIANT on bitsandbytes NF4 + A6000.** Measured 2026-08-01: one probe row
of 24 flipped its intents between batch 8 and batch 1. **Every gate eval ran at `--batch-size 1`**,
and the arm path *refuses* any other value by name rather than defaulting it.

**One writer per file, and the layer is live** (`2b423c8`): `docs/STATUS.md`, `docs/SPEC.md` and
`docs/PROMPT-*.md` are **team-lead files** — read them, commit them verbatim, never edit them.
Deny rules in `.claude/settings.json` refuse **both `Edit` and `Write`**.

**Phase 4's base model is `google/gemma-4-31b-it`** ([[phase4-base-model-gate]]) — ahead on every
gated head among the candidates. The 27B row's unpairedness was closed by a worst-case bound
analysis at $0; those rows keep `gate_anchor_valid: false` permanently.

**The Phase 3 baseline table** (`results/baselines.json`, read only via `scripts/show_results.py`),
G1a overall / G1c / G1d 3-class / G1e:
`tfidf-logreg` 0.6834 / 0.6000 / 0.6653 / 0.1964 · **gemma-4-31b-it (OpenRouter fp8) 0.8944 /
0.7981 / 0.8898 / 0.9211** · qwen3.6-27b 0.8541 / 0.7606 / 0.7605 / 0.8919 (`gate_anchor_valid:
false`) · qwen3.5-9b 0.7745 / 0.6252 / 0.5077 / 0.6476 · **xlm-roberta-base 0.7824 / 0.6007 /
0.7347 / NOT COVERED** · ref `claude-haiku-4.5` 0.8708 / 0.7739 / 0.7718 / 0.8537. That is the
**Phase 3** table; the own-pod anchor and the two Phase 4 arms are separate rows.

**The scorer computes, and it is the only thing that may.** `src/market_pulse/scorer.py` holds
every gate function, the margins, the selection rule and the verdicts. Bars and head deltas round
to ten decimals: `0.90 + 0.05` is 0.9500000000000001 and the gates are ">=", so a model exactly on
its bar must not fail on the last bit of an addition. A public function without a hand-computed
test fails the suite.

**Frozen test sets are at v2** — `docs/frozen-testsets.md` has the hashes and per-gate depth.
comments 400/1600, posts 250/750, thread-disjoint, zero `unclear` in test. **Training data is three
files**: `comments_train.jsonl` (1600) + `sarcasm_candidates.jsonl` (746) plus
`synthetic_sarcasm.jsonl`, 600 generated rows — **now measured and dropped by the ablation**
([[synthetic-sarcasm-augmentation]] stands as the record of how it was made and QA'd).
**G1b's holdout** is 108 rows, all `sarcasm: true`, thread-disjoint ([[hybrid-sarcasm-holdout-3.2]]).

## ⏭️ Next

1. **The 4.5a gate review (team lead + operator) reads [[phase45a-ceiling]] and decides everything
   downstream** — targeted re-labelling, synthetic v2, a dev-set search, test-set v3. The ADR is
   `proposed` and deliberately carries no recommendation; nothing moves until that review happens.
2. **Open for the review, in the ADR's own terms:** `intents` control says 22 of 40 agreement rows
   carry a wrong gold, against the 96.3% agreement the whole phase was premised on — do the two
   readings measure the same thing? One count from the returned data, no conclusion attached:
   **19 of those 22 are rows where both sides agreed on the EMPTY set `[]`** (3 are non-empty), and
   6 of the 18 `correct` rows are `[]` too. And the harness prints one number per head per unit;
   **which of them the 4.5 program calls "the ceiling" is still unnamed** — a macro-F1 bound and an
   accuracy share cannot both be read against 0.98.
3. **The filled pack is now the only copy of 244 verdicts.** `build_audit_pack.py --force` would
   destroy them and there is still no snapshot in the flow — the question the team lead has not
   ruled on. `normalize_audit_returns.py` is safe to re-run (it no-ops on an already-normalized
   pack), and the raw returns in `data/annotation/audit_45a_returned/` are the backup, sha-pinned
   in `results/audit_45b_returns.json`.
4. **Phase 5 is still PAUSED** — nothing Phase-5-shaped is scoped, planned or started; 4.5 comes
   first (operator sequencing decision, amendment 3.7). Everything after 4.5a — targeted
   re-labelling at scale, synthetic v2, a dev-set hyperparameter search — is **DEFERRED until the
   4.5a gate review rules on the numbers**, and each gets its own pre-registered gate.
5. **Still the operator's, carried out of Phase 4:** Phase 5's first measurement is already named —
   **do not merge the adapter into bf16 without scoring the merged artefact in the configuration
   production serves**; and the 100 GB CA-MTL-3 volume is kept pending the Phase 5 briefing.
6. **Six findings for Phase 5, none gate-relevant, all in [[phase4-gate-verdict]] §(f):** `planned`
   over-counts steps by one per epoch (272 planned, 270 run); leftover micro-batch gradients carry
   across the epoch boundary; the post-loop `save()` records the loop variable rather than the stop
   position after an early `--max-steps`; `seconds_per_step` in a resumed provenance is understated;
   training is not bit-reproducible; and the eval's last-line crash that the stub caught.
7. Still open from Phase 2 (not a blocker): dataset cards for the public augmentation datasets +
   licence check.

## 🚧 Blockers

**None open, and Phase 4 closed without leaving one.** 4c raised no escalation: the one
pre-registered stop it could have hit — a projection crossing the 5 h per-arm ceiling — did not
fire (3.40 h and 4.17 h, both under 4b's own
projections). Every earlier escalation came back decided at the next acceptance: 4b's three closed
by SPEC rev. 3.6 (the ceiling to 5 h/arm, an arm is a volume-less pod session, resume proved first
on the 4c pod — **done, and it passed**), and 4a's two by amendment 3.5 (G1d/G1e rescaled to
no-regression bars, the scorer taught to read the persisted slice).

**This Mac's device numbers, if anything is ever trained locally again:** 2 193 steps across
9 heads, **CPU 3.5 s/step**, **MPS 48.1 s/step** and OOM at 9.07 GiB unless the 250k×768 embedding
matrix is frozen. CPU beats MPS by 14×, which is the opposite of the intuition.

## ⚠️ Footguns for the next run

- **`data/annotation/audit_45a/` now holds 244 verdicts and gitignored data has no HEAD to restore
  from.** `build_audit_pack.py --force` is the only path that overwrites a filled pack and it takes
  no snapshot — do not run it to "regenerate" anything. What can be re-run safely:
  `normalize_audit_returns.py` (no-ops once the pack matches `results/audit_45b_returns.json`) and
  `audit_ceiling.py` (reads only). The verdicts survive in the raw returns under
  `data/annotation/audit_45a_returned/`, sha-pinned in the normalizer and in that record; treat that
  directory as read-only.
- **Registry brand normalization does not fold Unicode homoglyphs.** A mention spelled with a
  Cyrillic `о` inside a Latin-script brand casefolds to a token the watchlist alias table misses,
  so two strings that render identically score as two different entities — one FP and one FN on
  G1e. Found on the 4.5a brands stratum (n=4, so at least a quarter of it). **The fix is deferred
  to the 4.5 follow-ups on purpose: a normalization change mid-audit would silently redefine future
  G1e numbers against past ones** — Phase 3, the own-pod anchor and both arms were all scored
  through today's `normalise_brand`. Do not "just fix" it; it is a re-scoring decision with a plan,
  and every old run can be re-scored from its dump at $0 (`implementation-notes.md`, Phase 4.5a).
- **The results record holds TWO rows under the gate id `G1d`** — post_type, which gates, and
  relevance, which amendment 3.3 reports beside it and never inside it. A dict keyed by gate id
  returns the relevance number and a bar that looks entirely plausible (0.9315 instead of 0.8984).
  `records.anchor_values` selects on the metric name and refuses anything but one match.
- **Gemma 4's chat template drops the thinking channel when you render a full assistant turn.**
  The generation prompt ends `<|turn>model\n<|channel>thought\n<channel|>`; the turn form ends
  `<|turn>model\n` and then the content. Build a training example from the turn form and the model
  is conditioned on a context no gate row carries — silent, and it only shows up as gates lower
  than the smoke suggested. Take the prompt from the eval call, the end-of-turn marker from the
  turn form.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. If the pod exists only for one session, **delete** it
  (`runpodctl pod delete` — there is no `pod terminate`), do not stop it.
- **Python buffers stdout when it is redirected to a file.** 15 minutes into the 4b smoke the log
  still held nothing after the model load. `loss.jsonl` is written open/write/close per line and is
  the live view; `python3 -u` fixes the log itself.
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

- **A print statement can crash a run after the record is written.** The G1b-slice line at the end
  of `eval_zero_shot.main` was guarded by `anchor_valid` alone; on a fine-tuned arm `slice_ids` is
  `None`. It would have raised at the end of a 45-minute eval following a 3.4 h training run. Drive
  `main` through `--record-out` with a stub: `--smoke` returns before the record is built and
  `--probe` before it is written, so neither exercises that path.
- **`planned` is not `steps`.** `ceil(rows / (micro × accum)) × epochs` over-counts by one step per
  epoch whenever the epoch's micro-batches do not divide by the accumulation, and those leftovers'
  gradients are never zeroed — they fold into the next epoch's first step. 272 planned, 270 run.
- **Two runs of the same arm at the same seed give different losses** (0.18010 vs 0.18051 at step 5,
  same pod, same data, same config). Never write "identical" about two runs on this stack.
- **A test fixture that copies the real results file will collide with reality.** `test_gate_verdict`
  adds two fixture arms to the committed history; once the real arms existed that was two rows per
  arm and the suite failed on its own setup. It now strips records carrying `config.fine_tune`.

## 🐞 Known harness bug

Fixed 2026-07-28: `knowledge/templates/daily-log.md` now carries `{{DATE}}`, the placeholder
`scripts/brain-session-end.py` actually substitutes; `tests/test_templates.py` keeps the pair
honest.
