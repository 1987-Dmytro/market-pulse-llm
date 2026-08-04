# PROMPT-4.5h2 — test v4, fresh anchor, bars, and the A/B пласт ablation

Team-lead file. Operator: paste everything below the line into Claude Code.

---

You are executing step 4.5h2 of market-pulse-llm — the execution half of
Phase 4.5h. The precheck (results/precheck_45h.json) is accepted; every
design decision below is fixed. Full context up front; do not re-plan.

## Context (3 lines)

Test v4 materializes the v2 intents law into the frozen sets, a fresh own-pod
anchor re-bases every head, bars and the selection rule are committed as code
BEFORE any arm is scored, then the пласт earns or loses its place in one
paired ablation. One attempt; a failed gate closes its question (SPEC §5).

## Fixed decisions (operator sign-off 2026-08-04 + amendment 3.9 — do not relitigate)

1. Per-arm training ceiling **6.5 h** (amendment 3.9; SPEC already updated).
2. 54 dual-home ids — option (i): holdout pool materialized at **917** rows
   as a NEW file beside the pristine 971 (old sha-pins stay valid); v4
   inherits **v3** values on the 4 diverging rows.
3. Migration order: model pass first, the **31 audit rulings + 1 law verdict
   re-applied ON TOP** (operator rulings supersede the model).
4. Arm A trains on the `_tax2` siblings (SOURCES retarget — the precheck
   confound); the 24-row carve is drawn BEFORE the пласт is appended, so
   both arms hold the identical carve.
5. Bars: gate_bars construction from the FRESH anchor (+5 pp margins, ua/ru
   floors, 60% slice, no-regression rescale). No bar number typed by hand.
6. Selection rule, committed as code before scoring: **the пласт stays iff
   arm B's G1c is strictly higher than arm A's AND no other gated head of B
   is lower than A's by more than 0.5 pp** (amendment 3.4 (3) transposed).

## Budget caps (pre-registered; abort over cap, do not shrink scope silently)

- OpenRouter: migration pass ≤ **$0.30** (projection $0.0869; $0.6905 free).
- GPU: phase total ≤ **$9.00** of the $18.01 headroom (projection ≈ $6.5:
  anchor session ~$0.62 + arm A ~$1.80 + arm B ~$2.88 + evals ride the
  training pods + margin). Ledger anchors BEFORE first spend, as always.

## Read first (sections only)

- `docs/SPEC.md` §5, §8, amendment 3.9 (and 3.4 (3) for the rule's wording)
- `knowledge/decisions/test-v3.md` §(a), §(d) — what v4 derives from
- `knowledge/decisions/4b-training-contract.md` §(h) — resume discipline
- `results/precheck_45h.json` — your own numbers; treat them as the plan
- `scripts/runbook_4a.md`, `scripts/runbook_4c.md` — pod mechanics

## Step 0 — hygiene

The tree holds the team lead's session output — commit it as ONE commit,
message: `chore: the 4.5h acceptance, amendment 3.9, PRODUCT.md and the
4.5h2 contract` (expected: docs/SPEC.md, docs/STATUS.md, docs/PRODUCT.md,
docs/PROMPT-4.5h.md, docs/PROMPT-4.5h2.md — committing team-lead files is
fine; editing them is not). Then the hook tail (knowledge/daily_logs/
2026-08-03.md, knowledge/index.md) as its own commit. Refresh hot.md:
"4.5h2 in flight", blocker owner = the gates. make check green; report
the count.

## Step 1 — test v4 (freeze machinery first, then the paid pass)

`scripts/freeze_testsets_v4.py`, same discipline as v3: derived, counted,
refuse-on-mismatch; every untouched row must reproduce its v3 line byte for
byte; no hand edits anywhere.

1. Migration pass (OpenRouter): the 508 gold rows (400 comments_test + 108
   holdout), T1v2.1-with-parent-post prompt revisions already registered,
   [poll]/caption surrogates where the parent is media, batch conventions of
   4.5e. **The pass rewrites the `intents` field ONLY** — sentiment, sarcasm,
   post_type, brands, unclear, text are untouchable. A row the model cannot
   read is reported by id and keeps its v3 intents (flagged, not guessed).
2. Apply ON TOP, in this order: the 31 audit intents rulings, then the 1 law
   verdict (@VARUS_channel:5951). Pre-registered counts: 508 attempted,
   31 + 1 applied; a derivation that lands elsewhere stops instead of writing.
3. The 54: write the 917-row pool as a new file beside the pristine 971;
   sarcasm_holdout_v4 inherits v3 on the 4 diverging rows (ids are in
   precheck_45h.json → dual_home.diverging_columns).
4. posts_test_v4 = v3 content re-serialised under the v4 name (no intents
   field — say so in the manifest).
5. Outputs: `data/frozen/*_v4.jsonl` + `results/frozen_v4.json` (counts,
   sha256, provenance, supersedes-notes) + docs/frozen-testsets.md updated
   (your file). v2/v3 bytes untouched — assert their shas in the script.

## Step 2 — fresh anchor (pod, before any arm exists)

Runbook 4a mechanics: A6000, batch 1, 758 v4 rows, Gemma-4-31B zero-shot,
v2-with-post prompt revisions, per-row dump. All heads. New G1b slice = the
base model's error union on sarcasm_holdout_v4, persisted with sha256 into
`results/g1b_slice_v4.json`. Then, still BEFORE any training:

- `results/gate_bars_45h.json` derived programmatically from the anchor
  record (the gate_bars.py construction, +5 pp / floors / 60% / rescale);
- `scripts/gate_verdict_45h.py` carrying the selection rule verbatim from
  "Fixed decisions" §6, with a test asserting its text;
- commit both. Arm scoring before this commit is a contract violation.

## Step 3 — the ablation (amendment 3.9 mechanics)

1. SOURCES retarget: T1 comment sources → `comments_train_tax2.jsonl` +
   `sarcasm_candidates_tax2.jsonl` (posts_train.jsonl stays — no intents).
   Add a test: the run's provenance must name zero v1-taxonomy T1 files, and
   arm A's assembled pool must contain service rows (precheck says 308+239).
2. Pairing: assemble the arm-A pool, draw the 24-row carve (seed 42), THEN
   append the пласт's scoreable rows for arm B. Assert: n_train A = 2 171,
   B = 3 457, carve ids identical across arms (test it).
3. Per pod, before the full run: the 10-step smoke + resume proof of the 4b
   contract §(h) — stacks drift between pods and it costs cents.
4. Train both arms on the frozen qlora.yaml (only SOURCES differs by
   amendment 3.9), seed 42, ceiling 6.5 h each. Eval each arm on its own
   pod: batch 1, 758 v4 rows, per-row dump, unmerged adapter on NF4.
5. `gate_verdict_45h.py` output verbatim into the report: the rule applied,
   the five verdicts against gate_bars_45h.json, both columns side by side.
   One attempt. No retry, no re-score, no reconfiguration after any number
   is seen. Delete pods when done (volume-less billing).

## Step 4 — RECORD (in the same phase, not later)

1. ADR `45h-v4-and-the-precheck` — the confound, the 54 option (i), the
   migration order, ceiling 3.9, the comparisons verdict (0 full comparisons
   → amendment deferred to the Phase-5 loop counter). Cite
   results/precheck_45h.json and results/categories_45h.json.
2. ADR `45h2-ablation-verdict` — after the numbers: both columns, the rule's
   output, spend. Link both into knowledge/decisions/INDEX.md.
3. `results/spend_45h2.json` — GPU + OpenRouter to the cent, ledger anchors.
4. hot.md: phase state updated; no blocker without an owner.

## Report back to the team lead

(0) read-back FIRST — the steps one line each + the binding DO-NOTs;
(1) v4 manifest numbers (508 / 31+1 / 917 / byte-reproduction assertion);
(2) anchor record + bars + rule commit hashes, in that order;
(3) both arms: rows, steps, hours vs 6.5 ceiling, resume proofs;
(4) verdict output verbatim; (5) Deviations (silence is not compliance);
(6) make check count, git log --oneline, spend to the cent vs both caps.

## DO NOT

- Nothing scored before gate_bars_45h.json + gate_verdict_45h.py are
  committed; no bar or threshold typed by hand anywhere.
- v2/v3 frozen bytes, the пласт, the pristine 971 pool: read-only.
- The migration pass touches `intents` only; gold text is never rewritten.
- No second attempt at any gate; a failed gate closes its question.
- No cap raise, no scope shrink — an overrun aborts and reports.
- Comparisons of v4 numbers to v2/v3 numbers must carry version labels.
- Do not edit docs/STATUS.md, docs/SPEC.md or docs/PROMPT-*.md — team-lead
  files (File ownership). Phase-end facts: implementation-notes.md + daily log.

Language of all artifacts: English. Atomic commits as you go.
