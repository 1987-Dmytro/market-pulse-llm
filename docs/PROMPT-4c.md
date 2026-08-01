# PROMPT-4c — Phase 4c: the two arms, and the one-attempt gates (rev. 1)

**4b is accepted; amendments 3.5 and 3.6 are approved** (per-arm ceiling now
5 h, config untouched). This is THE one-attempt step: both arms train fully,
each arm is scored on the frozen sets exactly once, the pre-registered rule
selects the arm, and the Tier-1 gates are decided. **After any gate number is
seen, nothing is retrained, re-scored or reconfigured.** A crash resumes; it
never restarts-and-rescores.

Operator decisions in force: one arm per pod session, volume-less wherever
A6000 stock exists (the CA-MTL-3 volume is a bonus if stock coincides at
launch, never a wait condition); every checkpoint and artifact syncs to the
Mac continuously — nothing exists only on a pod. Expected spend ≈ $5.2 of
the $23.88 remaining.

## Read first (these sections only)

- `docs/SPEC.md` — amendments **3.5 and 3.6**, and §5.
- `knowledge/decisions/4b-training-contract.md` (your own contract).
- `knowledge/decisions/phase4-own-pod-anchor.md` §(c) — batch-1 rule.
- Your hot.md footguns, including the unattended-run watching discipline
  (poll the process, not the log; heartbeat carries the current step).

**Read-back check — before anything:** the selection rule verbatim; the five
bars WITH numbers as your threshold helper derives them (not from memory);
what happens after gate numbers are seen; the resume protocol; the per-arm
ceiling.

## Step 0 — session entry (Mac)

Commit today's team-lead edits (docs/SPEC.md → rev. 3.6, docs/STATUS.md,
this file untracked) + the day's records, one docs commit:
`docs: 4b accepted — amendment 3.6 and prompt 4c`.
Team-lead files are commit-only.

## Step 1 — resume proof (first minutes on the first pod, before arm A)

Prove resume against REAL state, not the stub: run ~10 steps, save adapter +
optimizer state (~250 MB), kill the process, reload with the k-bit base and
`is_trainable=True`, `torch.load` the real state, continue ~5 steps. PASS =
the optimizer step counter continues (not resets) and the first resumed
loss sits on the pre-kill trajectory (within its noise). Record both loss
series in the notes. If resume fails: STOP and report — do not start arm A
on a volume-less pod without working resume.

## Step 2 — arm A (real-only), one pod session

1. Budget guard before start; verify the assembled dataset's sha256 equals
   the 4b contract's (`train_sha256` in the smoke provenance) — the arm you
   train must be byte-identically the arm 4b projected.
2. Train the full 272 steps (2 epochs, `config/qlora.yaml`, seed 42).
   Checkpoint sync cadence: adapter + optimizer state rsync'd to the Mac at
   least every 30 minutes and at every save; loss curve file included.
   Ceiling: 5 h on the training loop (amendment 3.6); the $25 cap guard
   stays armed.
3. **Eval, same session:** the local inference path + the arm's adapter
   (unmerged, NF4 base), batch size 1, all 758 frozen rows + the G1b
   fix-rate over the 44-id slice (sha-checked load). Per-row dump (sorted,
   ids + predicted labels only); record appended to `results/baselines.json`
   through the scorer, tagged with arm id, adapter sha256, dataset sha256,
   full provenance. The record carries every gated head PLUS the fix-rate
   and the ≤2 pp guard delta.
4. Sync all artifacts home, verify shas on the Mac side, stop/delete the
   pod (show it), append the spend ledger.

**Crash protocol:** training crash → resume from the last synced state and
log the event; eval crash → resume scoring the remaining rows, never
re-score completed ones. Neither is a second attempt. What IS forbidden:
any config change, any re-run of a completed training or eval, any
"just checking" pass over a frozen set.

## Step 3 — arm B (with-synthetic), second pod session

Identical protocol; 348 steps; the dataset diff-assert against arm A (600
`synthetic:NNNN` rows exactly) runs on the pod before training; ceiling 5 h.

## Step 4 — selection + verdicts (Mac, mechanical)

- Apply the pre-registered rule (amendment 3.4 (3)): synthetic stays iff
  arm B's G1b fix-rate is strictly higher AND no other gated head is more
  than 0.5 pp below arm A's. The rule's inputs come from the two records
  via `scripts/show_results.py`; the application is a script output, not
  prose.
- Produce the gate table for the SELECTED arm — G1a overall + floors, G1b
  (≥27/44, guard ≤2 pp, n=44 beside the verdict), G1c, G1d, G1e — each bar
  derived programmatically from the own-pod record. Five verdicts.
- BOTH arms' full columns are published side by side in the report and the
  ADR. A failed gate closes its question — report it plainly.

## Step 5 — RECORD (same session)

- ADR `knowledge/decisions/phase4-gate-verdict.md`: both columns, the rule's
  application with its inputs, the five verdicts, adapter/dataset shas, the
  resume-proof outcome, cost; Deviations cited. Link in INDEX.
- hot.md: verdicts + next; `implementation-notes.md` § Phase 4c with the
  mandatory Deviations section ("none" if none).

## Verify-gate — run and SHOW the output

1. `make check` — green; count.
2. `scripts/show_results.py` — both arm records present and well-formed.
3. Both dumps + slice-eval artifacts exist; recompute shas; match records.
4. Dataset shas: arm A == 4b contract; arm B − arm A == exactly the 600
   synthetic ids.
5. The selection-rule script output, and the five-verdict table.
6. Ledger total ≤ $25; both pods gone (show); artifacts verified on Mac.
7. `git log --oneline` — atomic commits.

## Report

Three plain lines (which arm, how many gates passed, spend). Then: the
two-column arm table, the verdict table with bars, the fix-rate with n=44,
Deviations, open questions. STOP — no self-acceptance. Phase acceptance
(team-lead verification, operator quiz, RECORD sweep, STATUS) happens on
this report.

## DO NOT

- Nothing is retrained, re-scored or reconfigured after a gate number is
  seen. No third training run exists under any circumstances.
- No frozen-set pass outside the two sanctioned arm evals. The holdout is
  scored only through the slice/fix-rate path of those evals.
- Do not edit `docs/STATUS.md`, `docs/SPEC.md`, `docs/PROMPT-*.md` —
  team-lead files; step 0 commits them, nothing more.
- Do not modify prompts, frozen files, `results/g1b_slice.json`, spend
  anchors, or any existing record; `results/baselines.json` is append-only
  via the scorer.
- Batch size 1 for every eval; prompts byte-identical (assert vs the 3b
  record, as 4a did).
- Keep the heartbeat discipline for both long runs; never leave a pod
  running after its session ends.
- All artifacts in English.

## Autonomy

Mechanics (sync tooling, session babysitting, retry-on-transient inside a
step) are yours. Everything that defines a number — config, data, prompts,
slice, rule, bars — is frozen. A forced deviation goes to the Deviations
log; if it is gate-relevant you STOP and report before proceeding.
