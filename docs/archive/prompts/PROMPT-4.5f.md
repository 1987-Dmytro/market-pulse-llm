# PROMPT-4.5f — verdicts in: the gate, three rulings, the drop measurement (rev. 1)

**The operator's calibration verdicts are returned** in
`data/annotation/calib_45e/` (spreadsheet round-trip: `;` delimiter, case
variants — expected, the 4.5a precedent). The gate rule is pre-registered
in `results/calib_45e_manifest.json` and is not re-decided here. Three
operator rulings from the diagnostic file are law for their rows
(recorded in docs/STATUS.md): `@VARUS_channel:11972` → `["taste"]`,
`:11960` → `["taste"]`, `:11902` → `["taste"]` (the notes cell of 11902
was transcribed by the team lead from operator dictation — notes are free
text and are never validated). **Everything here is $0 — no API calls.**

## Step 0

Commit stray vault files + team-lead edits (docs/STATUS.md, this file,
the operator-filled pack): `docs: the calibration verdicts are in — and
the 4.5f prompt`.

## Step 1 — the reader (the gate is computed, never eyeballed)

A `normalize_audit_returns`-style acceptance script: rebuild the sealed
pack deterministically (seed 42, staged files + manifest); verify each
returned row equals its sealed row with ONLY `verdict`/`notes` changed —
cell-value equality, not byte equality (the round-trip broke bytes, that
is expected). Map verdict forms by a NAMED table (`correct`/`incorrect`;
`old`/`new`/`neither`; case-insensitive), refuse any other value; a blank
gated verdict counts as disagreement per the registered rule. Compute
`agreement = correct / 100`. Write `results/calib_45e_verdict.json`:
per-row verdicts, the tally, the rule quoted verbatim, shas of the
returned files, PASS/FAIL against 0.90. Tests: a hand-computed tally
fixture + a negative control (an unknown verdict form must refuse).

## Step 2 — apply the three rulings

`apply_review` pattern over the staged `_tax2` files, intents column
only: the three rows → `["taste"]`. The record names each row, old value,
new value, authority (operator diagnostic verdict / chat dictation). Do
NOT recompute the drift block of `results/relabel_45e.json` — append a
`fixes` block beside it.

## Step 3 — the drop measurement ($0, from rows already paid for)

Rows whose intents went non-empty → `[]`: count, text-length distribution
against the rest, share of the 473 changed-without-service. The
hypothesis under measurement: the re-labeller never sees the parent post
(verified — no parent context in `prompts.py` or the eval), so short
context-dependent replies lose their intent. Report the decomposition of
the 15% (explained-by-this-class vs the rest) — numbers only, no
conclusions beyond them.

## Step 4 — the micro-pack (operator ~6 min, not gated)

The 14 unreadable rows as `data/annotation/calib_45e/unreadable14.csv`:
`id;text;intents_v1;intents_v2;notes` with `intents_v2` BLANK — the
operator labels these himself (the model refused them; nothing is
proposed). Pin it in a NEW `results/calib_45e_micro_manifest.json`; the
sealed manifest is never touched.

## Verify-gate — show output

1. `make check` green; count. Reader negative control shown refusing.
2. The three applied rows: before/after diff printed.
3. The gate number, PASS/FAIL, and the verdict record path.
4. Drop-measurement table.
5. `git log --oneline` — atomic commits.

## Report

Three plain lines; the gate number; the fixes; the drop decomposition;
micro-pack location; Deviations; open questions. STOP — with a green
gate the team lead briefs 4.5g: the up-label of the 1,912 under a
full-field v2 precheck + its 3-strata calibration (the operator's ~2.0 h
sitting bundles with the 14 rows).

## DO NOT

- No API spend of any kind; no frozen-file changes.
- Never change a `verdict` cell or the sealed manifest.
- The v1 prompt constants, their SHAs and `TASKS` are immutable.
- Do not edit docs/STATUS.md, docs/SPEC.md or docs/PROMPT-*.md — team-lead
  files, commit-only. Artifacts English.
