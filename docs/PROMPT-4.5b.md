# PROMPT-4.5b — ingest the returned audit, run the ceiling harness (rev. 1)

**The operator's arbitration is COMPLETE and team-lead-verified: 244/244
verdicts.** The authoritative return set sits in
`data/annotation/audit_45a_returned/` (five CSVs, canonical names) — placed
and sha-pinned by the team lead from the operator's uploads:
`comments_sentiment c590192f…, comments_intents e1333a8a…, slice_unfixed
6f0fd7dd…, posts e254499a…, control 4410090f…`. Treat that directory as
READ-ONLY raw returns. Known return-format quirks (verified harmless, labels
and ids byte-intact vs the originals): semicolon delimiter, and long-form
verdicts like `B — правильная метка label_B`. Any copies of pack files
lying in `data/` are superseded by this return set — leave them untouched.

$0, no pods. The harness formula was approved by the team lead on 02.08.

## Step 0

Commit today's team-lead edits (docs/STATUS.md, this file untracked), one
commit: `docs: the audit returns — prompt 4.5b`.

## Step 1 — normalization (committed, deterministic script)

Raw returns → canonical pack files in `data/annotation/audit_45a/`
(overwriting the empty originals — normalization output, not a builder run):

- utf-8-sig in → utf-8 out; `;` → `,`; verdict long forms → canonical
  tokens (`A`/`B`/`ambiguous`; control `correct`/`incorrect`/`ambiguous`)
  by taking the leading token — the mapping is a table in the script, not
  an LLM call.
- EVERYTHING else byte-preserved: head, id, text, label_A/label_B/label,
  notes. Assert per-row against the empty originals (git HEAD copies):
  same id sets, same labels, same texts. Any mismatch → named-defect stop.
- Record raw + normalized sha256s alongside the pack (extend the manifest
  or a sibling file); raw returns stay untouched.

## Step 2 — run the approved harness

`scripts/audit_ceiling.py` over the normalized pack. Expect its own
refusals to pass (key sha, vocabulary, no empties, row counts). Show the
COMPLETE output: per-head metric-unit ceiling (headline), accuracy-unit
high/low, sensitivity bands, the assumptions block. G1e is excluded from
ceiling arithmetic (team-lead decision 02.08); its 4 rows are reported as
raw verdict counts only.

## Step 3 — RECORD

- ADR `knowledge/decisions/phase45a-ceiling.md` (status: proposed): the
  numbers, per-head gold-wrong / model-wrong / ambiguous counts, the
  formula's assumptions verbatim, the blind-spot statement, provenance
  (all shas). NUMBERS ONLY — no recommendations, no program decisions:
  those belong to the 4.5a gate review. Link in INDEX (proposed).
- hot.md + implementation-notes § Phase 4.5b with mandatory Deviations.

## Verify-gate — show output

1. `make check` green; count.
2. Normalization diff summary: only delimiter/encoding/verdict-token
   changed; per-row label/id/text assertions passed.
3. The full harness stdout.
4. Raw-return shas match the five pinned above; frozen dir untouched.
5. `git log --oneline` — atomic commits.

## Report

Three plain lines, then the per-head ceiling table (metric-unit headline,
accuracy band, verdict counts), Deviations, open questions. STOP — the
4.5a gate review (team lead + operator) decides everything downstream.

## DO NOT

- No edits to raw returns, frozen files, dumps, records, the key, or gold.
- No interpretation beyond the harness's own printout; no recommendations
  in the ADR.
- Team-lead files commit-only. All artifacts English.
