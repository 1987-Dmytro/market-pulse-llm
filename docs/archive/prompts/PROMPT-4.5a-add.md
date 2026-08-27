# PROMPT-4.5a-add — control expansion + harness hardening (rev. 1)

The 4.5a pack is ACCEPTED and the ceiling formula APPROVED, with operator
decisions: expand the control stratum for sentiment and intents 8 → 40 each
(+64 rows; the other three heads stay at 8), and two hardenings before any
verdict ingestion. The operator has NOT started judging (verified: all
verdict cells empty, shas match the manifest) — do this now so arbitration
happens in one pass over 244 rows. $0, no pods.

## Step 1 — expand control.csv

- New control for sentiment and intents = the EXISTING 8 rows (byte-kept)
  + 32 new agreement rows each, drawn deterministically (seeded) from the
  remaining agreement pool, excluding the already-sampled ids. The three
  other heads' rows stay byte-identical. Final control.csv: 104 rows.
- Disagreement CSVs do not change at all. The key does not change (control
  rows carry no key). README's row counts updated.
- Rebuild via the builder (verdicts are empty, so a clean rebuild is legal);
  verify: double-build byte-identical; the original 40 control rows appear
  unchanged inside the new 104; blinding sweep re-run over the pack;
  results/audit_45a_manifest.json updated (new CSV shas + strata table),
  old manifest values preserved in git history.

## Step 2 — harness hardening (before ingestion, per team-lead review)

1. `rulings()` refuses any UNKNOWN column in a returned CSV (spreadsheet
   tools add columns silently); named-defect SystemExit.
2. Commit the planted-attribution negative test properly: a test that
   plants a `label_gold` column into a generated pack and asserts the
   blinding sweep FAILS it (the in-session proof from the daily log becomes
   a permanent guard), plus a test for the unknown-column refusal.

## Step 3 — file, do not fix

The brands homoglyph finding is a normalization bug candidate. FILE it
(implementation-notes + hot.md footgun: "registry brand normalization does
not fold Unicode homoglyphs; fix is deferred to the 4.5 follow-ups — a
normalization change mid-audit would silently redefine future G1e numbers
against past ones"). Do NOT change the registry or scorer now.

## Verify-gate — show output

1. `make check` green; count (expect +2 or more tests).
2. Row counts: control 104 (40/40/8/8/8 per head); disagreement CSVs
   byte-identical to the accepted pack (shas shown).
3. Blinding sweep + double-build determinism over the NEW pack.
4. Manifest updated; frozen untouched (shas).
5. `git log --oneline` — atomic commits.

Report in a few lines + Deviations. STOP. The operator then judges the
244-row pack per README-audit.md; the harness still waits for filled CSVs.

DO NOT: touch frozen files, dumps, records, the key, or the disagreement
rows; no verdict pre-filling; no normalization changes; team-lead files
commit-only (this file + today's docs/STATUS.md edits, one commit:
`docs: 4.5a accepted — control expansion and harness hardening`).
