# PROMPT-4.5a — the audit pack + ceiling harness (rev. 1)

**Phase 4 is closed at 2 of 5. Amendment 3.7 opens Phase 4.5** (quality
program, quality BEFORE the production loop — operator sequencing decision).
This step builds the error-audit pack the operator will adjudicate, and the
harness that turns the returned verdicts into a per-head ceiling estimate.
**This step judges nothing, changes no data, rents no pod. $0.**

## Step 0 — close-out check

If PROMPT-4-close.md has not run yet (check: `phase4-gate-verdict.md`
front-matter still `proposed`, or `runpodctl` still lists `gxkdecf3g7k3y7`)
— execute that file's five items first, then continue here. Then commit
today's team-lead edits (docs/SPEC.md → rev. 3.7, docs/STATUS.md, this file
untracked), one commit:
`docs: phase 4.5 opens — amendment 3.7 and the audit prompt`.

## Read first

- `docs/SPEC.md` — the **amendment 3.7** block only.
- Sources for the pack: arm A's per-row dump (the deliverable adapter's
  predictions), the frozen files (texts + gold), `results/g1b_slice.json`.

## Step 1 — the anonymized adjudication pack

Build `data/annotation/audit_45a/` (data gitignored; the BUILDER script is
committed, deterministic, seed 42). Contents:

1. `comments_sentiment.csv` — every comments_test row where arm A's
   sentiment ≠ gold.
2. `comments_intents.csv` — every row with any intent-set mismatch (both
   full sets shown).
3. `slice_unfixed.csv` — the 23 slice rows arm A did not fix (sentiment +
   sarcasm labels shown).
4. `posts.csv` — post_type mismatches and brand-extraction mismatches.
5. `control.csv` — 30–40 random AGREEMENT rows (arm A == gold), stratified
   across tasks: single label shown, verdict correct / incorrect /
   ambiguous. This measures gold noise where nobody disagrees.

**Anonymization protocol — the audit's validity rests on it:**

- In every disagreement row the two candidate labels appear as `label_A` /
  `label_B` in per-row RANDOM order (seeded coin flip). NOTHING in any CSV
  reveals which is the model's and which is gold.
- The de-anonymization key is written to a separate file beside the pack;
  its sha256 goes into the builder's provenance so it cannot be quietly
  regenerated. The executor NEVER pre-fills, suggests, or comments on
  verdicts (SPEC §10 — the arbiter's sample stays untouched).
- Row fields: `id`, `text` (from the frozen file), `label_A`, `label_B`,
  empty `verdict` (vocabulary: `A` / `B` / `ambiguous`; control:
  `correct` / `incorrect` / `ambiguous`), empty `notes`.
- `README-audit.md` — **in Russian** (operator-facing artifact, the same
  sanctioned exception as docs/STATUS.md): what the audit is, how to fill
  the verdict column, the vocabulary, «суди метку, не автора метки», no
  time pressure, and where to put the finished files.

Report the row count of every CSV so the operator knows the evening's size.

## Step 2 — the ceiling harness (built now, run only when the CSVs return)

A committed script that ingests the filled CSVs + the key and prints, per
head: model-wrong / gold-wrong / ambiguous counts and rates, and a ceiling
estimate. The formula is printed WITH its assumptions and is subject to
team-lead review before any verdict is ingested. Keep it simple and
transparent, e.g.:

- gold-error rate on disagreements = share of rows ruled for the model's
  label; gold-error rate on agreements = `incorrect` share of control.
- ceiling_head ≈ 1 − (extrapolated gold-wrong + ambiguous share across the
  whole test, weighted by the disagreement/agreement strata sizes).
- State plainly what the audit CANNOT see: rows where model and gold are
  wrong the same way outside the control sample.

Pin the ingestion arithmetic with a hand-computed test (worked example in
the test's comment). The script must REFUSE to run while any verdict cell
is empty, and must never print the key's mapping row-by-row into the
report (the operator may audit again later; the blinding stays reusable).

## Verify-gate — run and SHOW the output

1. `make check` — green; count.
2. The pack exists; per-CSV row counts printed; README in place.
3. Blinding negative control: a test (or grep) proving no CSV contains the
   words model/gold/pred or any attribution; key sha256 recorded.
4. Builder determinism: rebuild → byte-identical CSVs and key (shas shown).
5. Frozen files untouched: `git status` clean of data/frozen; shas of the
   frozen dir match `docs/frozen-testsets.md`.
6. `git log --oneline` — atomic commits.

## Report

Three plain lines (pack size per head, where it lives, what the operator
does next); the counts table; Deviations ("none" if none); open questions.
STOP. The team lead reviews; the operator adjudicates on their own clock;
the harness runs only after the team lead approves its formula AND the
operator returns the CSVs.

## DO NOT

- No changes to frozen files, gold, dumps, records, or the slice. No
  re-scoring of anything. No training, no pods, no spend.
- No verdict pre-filling, no "obvious fixes" of labels, no commentary on
  specific rows anywhere the operator will read before judging.
- Do not edit docs/STATUS.md, docs/SPEC.md, docs/PROMPT-* — team-lead
  files; step 0 commits them, nothing more.
- All artifacts in English EXCEPT `README-audit.md` (operator-facing,
  Russian — sanctioned exception, like docs/STATUS.md).
