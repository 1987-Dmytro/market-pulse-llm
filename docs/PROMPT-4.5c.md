# PROMPT-4.5c — the intents law-review pack + test-set v3 (rev. 1)

Gate 4.5 decisions (operator, 2026-08-02): (1) the intents law question is
decided AFTER a face-to-face review — this step only prepares the pack;
(2) **test v3 approved**: point-fix the gold on the operator's blind
verdicts — sentiment 15, sarcasm-holdout 15 (pair labels), post_type 5,
brands 3 — **intents untouched everywhere**, pending the law decision.
$0, Mac-only, no model calls anywhere in this step.

## Step 0

Commit today's team-lead edits (docs/STATUS.md, this file untracked), one
commit: `docs: gate 4.5 — the law review and test v3 are ordered`.

## Step 1 — intents law-review pack (operator-facing, Russian)

`data/annotation/audit_45a/intents-law-review.md`: (a) the EXACT empty-set
rules quoted verbatim from the Phase-2 annotation guideline (cite file +
section); (b) the 19 agreed-`[]` control rows the operator ruled
`incorrect` — text + the agreed label, one per block; (c) for contrast,
the 6 agreed-`[]` rows he ruled `correct`; (d) the 3 non-empty `incorrect`
control rows. NO recommendations, NO commentary, NO model/gold attribution
anywhere — the pack informs a law decision, it does not argue one.

## Step 2 — freeze v3 (v2 stays immutable forever)

- NEW files (`data/frozen/comments_test_v3.jsonl`, `sarcasm_holdout_v3.jsonl`,
  `posts_test_v3.jsonl`); v2 files are not touched — every existing record
  and manifest keeps referencing their shas.
- The 38 fixes are derived MECHANICALLY from the returned verdicts + the
  sealed key (a ruling for the model's label rewrites gold to that label;
  pair rows rewrite the pair). No hand edits; the deriver is a committed
  script with a test.
- `docs/frozen-testsets.md` gains a v3 section: per-file changelog (every
  changed id + old → new), new sha256s, provenance (audit manifest + returns
  shas), and the sentence that v3's intents column equals v2's pending the
  law decision.

## Step 3 — re-score every dumped run against v3, from dumps only

- For every run with a per-row dump (both arms, own-pod base; list any
  runs that have no dump and skip them loudly): recompute all heads vs v3
  through the scorer. NO model calls — dumps are the only prediction source.
- Results → a new append-only `results/rescores_v3.json` (records carry
  `gold_version: "v3"`, source dump sha, derivation provenance);
  `scripts/show_results.py --gold v3` renders them beside the v2 numbers.
- **G1b under v3, both readings, clearly labelled:** (a) fix-rate of each
  arm on the ORIGINAL 44-id slice re-scored vs v3 (comparable with the
  Phase 4 verdict row); (b) the v3-slice (base-model errors recomputed vs
  v3 from its dump) with its n, and fix-rates on it. Neither replaces the
  Phase 4 verdict — that verdict stands against v2, permanently.

## Step 4 — RECORD

ADR `knowledge/decisions/test-v3.md` (proposed): the 38 fixes with their
audit provenance, what v3 does and does not reopen (Phase 4 verdict: does
not), both G1b readings, the re-score table. INDEX; hot.md; notes with
Deviations.

## Verify-gate — show output

1. `make check` green; count.
2. v2 shas unchanged (all five, vs docs/frozen-testsets.md).
3. v3 changelog row count == 38 (15+15+5+3), ids match the de-anonymized
   verdict set exactly; intents column of v3 == v2 byte-wise.
4. The full re-score table (v2 | v3 side by side per run per head).
5. `git log --oneline` — atomic commits.

## Report

Three plain lines; the v2|v3 table; both G1b readings; the law-review pack
location; Deviations; open questions. STOP — the operator then does the
10–15 min law review, and the next gate decides intents + the rest of the
program (re-labelling appetite, synthetic v2, dev-sweep).

## DO NOT

- Intents gold: no changes anywhere. v2 files: no changes ever.
- No model calls, no pods, no training. Dumps are the only source.
- No edits to Phase 4 records or verdicts; no reading of v3 numbers as a
  gate result — they are program measurements.
- The law-review pack carries zero recommendations.
- Team-lead files commit-only. Artifacts English except the two
  operator-facing packs (sanctioned exception).
