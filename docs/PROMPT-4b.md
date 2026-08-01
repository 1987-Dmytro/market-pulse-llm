# PROMPT-4b — Phase 4b: scorer slice input + trainer + training smoke (rev. 1)

**4a is accepted; amendment 3.5 is approved.** This step teaches the scorer to
read the persisted G1b slice, builds the QLoRA trainer, and smokes it. Two
things this step must NOT do: **no full training runs** (that is 4c, after
this report is accepted) and **no scoring of any frozen set or the holdout by
anything** — the one-attempt gates see a fine-tuned model exactly once, in 4c.

Remaining budget: $24.38 of the $25 Phase 4 cap. Expected 4b pod spend: ~$1.

## Read first (these sections only)

- `docs/SPEC.md` — the **amendment 3.5** block (all three clauses) and §4.
- `knowledge/decisions/phase4-own-pod-anchor.md` — §(c) batch-1 inheritance,
  §(e) the NF4 config dict and the 18.9 GB memory measurement.
- Your own hot.md footguns.

**Read-back check — one line each, before any file change:** the two things
4b must not do; the pre-registered synthetic selection rule; the per-arm hour
ceiling; what "fixed" means for a G1b slice row under amendment 3.5 (3).

## Step 0 — session entry

1. `git status`; expect your own vault/notes state (including whatever your
   escalation session committed or left dirty) plus today's team-lead edits
   (docs/SPEC.md → rev. 3.5, docs/STATUS.md, this file untracked). One
   commit for the docs set:
   `docs: 4a accepted — amendment 3.5, the 4b prompt and the day's records`.
   Team-lead files are commit-only, as always.
2. **Clear the blocker your escalation recorded.** The G1d/G1e
   impossibility you raised is DECIDED: amendment 3.5 (2) replaces "+10 pp"
   with "≥ anchor − 1 pp" (G1d ≥ 0.8984, G1e ≥ 0.8874), with the ordering
   recorded in the spec text. The scorer question you raised is decided by
   3.5 (3) and executed as Step 1 below. Update hot.md's Blockers section
   (none open) and the Next list with pointers to the amendment.

## Step 1 — the scorer learns the slice file (amendment 3.5 (3))

This is the team-lead instruction that authorizes a scorer change:

- The G1b fix-rate function takes the slice as an **explicit id list** plus
  the fine-tuned per-row predictions; the caller loads
  `results/g1b_slice.json` and verifies its sha256 against the own-pod
  record BEFORE use — a corrupted or regenerated slice file must refuse.
- Definition (fixed, not yours to vary): a slice row is FIXED iff the
  fine-tuned model is correct on BOTH sentiment and sarcasm for that row —
  it leaves the union. Fix-rate = fixed / 44. Gate: ≥27 of 44, with the
  existing ≤2 pp overall macro-F1 guard; n=44 is reported beside the verdict.
- Pin the arithmetic with a hand-computed test (work the toy example in the
  test's comment), plus a negative-control test: a slice file with a wrong
  sha is refused.
- Any gate-threshold helper reads its anchors **programmatically** from the
  own-pod record (`config.backend == "local"`) — G1a ≥ anchor + 5 pp with
  per-language floors anchor − 2 pp, G1c ≥ anchor + 5 pp, G1d and G1e ≥
  anchor − 1 pp. No hand-typed anchor numbers anywhere in code or tests.

## Step 2 — the trainer: `scripts/train_qlora.py` + a committed config

- PEFT LoRA over the EXACT NF4 config dict in `src/market_pulse/local_llm.py`
  — one dict already spells eval, training base and serving; do not fork it.
- **Train/eval format identity is an invariant.** A training example = the
  same fixed prompt (T1 or T2) + the gold answer serialized in the same JSON
  schema the parser reads. Assert the prompt SHA equality at dataset build,
  the same way the eval path does.
- Sources: T1 = `comments_train.jsonl` + the scoreable rows of
  `sarcasm_candidates.jsonl`, plus `synthetic_sarcasm.jsonl` ONLY under
  `--with-synthetic`; T2 = `posts_train.jsonl`. Never read `data/frozen/*` or
  `sarcasm_holdout_pool.jsonl` in the trainer. State your assumption on
  `unclear`-labelled rows in the notes (default: train on scoreable rows
  only) with one line of rationale.
- **Arm identity:** build both datasets and assert they differ by exactly the
  600 `synthetic:NNNN` rows — nothing else. Record a content hash of each
  assembled dataset in provenance.
- **Hyperparameters are frozen in the committed config BEFORE 4c**, one-line
  rationale each in the notes (rank, alpha, dropout, LR + schedule, epochs,
  max seq len, micro-batch × grad-accum). Fixed epoch count, NO early
  stopping against any eval. Train loss plus a small train-carve loss are
  logged as a convergence thermometer only — the carve comes from the
  training pool, never from frozen sets, and selects nothing.
- Determinism: seed 42 recorded; gradient checkpointing on; memory sized
  against the 18.9 GB measurement (weights + KV at batch 1). On OOM: halve
  the micro-batch and log it — never silently shrink seq len.
- Checkpoints: adapter-only saves, resumable; the artifact is the adapter
  dir + config, served over the same NF4 base, unmerged.

## Step 3 — training smoke (one pod session, real-only arm)

- ~40–60 optimizer steps on the real-only arm: show loss falling
  (first/last + curve file), save the adapter checkpoint, reload it, and run
  the LOCAL EVAL PATH over ~24 rows carved from the TRAIN pool — mechanics
  only (prompts render, replies parse, scorer arithmetic accepts the
  labels); the numbers are meaningless and must be labelled as such.
  FROZEN SETS AND THE HOLDOUT ARE NOT TOUCHED.
- Smoke the `--with-synthetic` dataset BUILD too (assembly + the diff
  assert); no second training needed.
- **Timing projection per arm**: measured s/step × planned steps → hours and
  $ at $0.53/h. A projection over 4 h per arm → STOP and report (the XLM-R
  pattern; the ceiling is amendment 3.4 (4)).
- Budget guard before and after; update the spend ledger; stop the pod and
  show it stopped.

## Step 4 — RECORD (same session)

- ADR `knowledge/decisions/4b-training-contract.md`: the frozen
  hyperparameters with rationale, the train/eval format-identity invariant,
  the `unclear` assumption, the arm-identity assert, the smoke outcome and
  the per-arm projection. Link it in INDEX.
- hot.md and `implementation-notes.md` § Phase 4b current; **Deviations
  section mandatory** — "none" if none.

## Verify-gate — run and SHOW the output

1. `make check` — green; report the count (new scorer tests included; still
   no torch import anywhere under tests/).
2. Negative control shown: a tampered copy of the slice file is REFUSED by
   the sha check.
3. Smoke evidence: loss first/last, checkpoint reload proof, the train-carve
   eval mechanics output.
4. The projection table per arm (steps · s/step · hours · $) against the 4 h
   ceiling.
5. Spend ledger total + remaining of $25; pod stopped (show status).
6. `git log --oneline` for the session — atomic commits, dependencies first.

## Report

Three plain lines first; the hyperparameter table; the projection table;
Deviations; open questions. Then STOP — full runs need an explicit go on
this report. No self-acceptance.

## DO NOT

- No full training runs. No scoring of any frozen set or the holdout by
  anything in this step — the one-attempt gates see a fine-tuned model
  exactly once, in 4c.
- Do not edit `docs/STATUS.md`, `docs/SPEC.md` or `docs/PROMPT-*.md` —
  team-lead files (File ownership); step 0 commits them, nothing more.
- Do not modify prompts, frozen files, `results/g1b_slice.json`, the spend
  anchors, or any existing record in `results/baselines.json`.
- Synthetic rows enter ONLY via the `--with-synthetic` path; the diff assert
  is not optional.
- Batch size 1 for any eval-path scoring unless batch-invariance is
  re-measured on this stack and recorded (4a ADR §(c)).
- No hand-typed anchors or thresholds — read them from the own-pod record.
- All artifacts in English.

## Autonomy

Trainer design and hyperparameter values are yours — record the rationale.
Anything touching gate definitions, prompts, frozen data, the selection
rule or the slice definition is frozen; a deviation you believe is forced
goes to the Deviations log, and if it is gate-relevant you stop and report
instead of proceeding.
