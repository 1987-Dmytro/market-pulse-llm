# PROMPT 4.5g3 — sitting reader: per-stratum gates, fixes, merge, wave-2 pack

Paste into Claude Code as-is. All artifacts in English. Do NOT edit
docs/STATUS.md, docs/SPEC.md or docs/PROMPT-*.md — team-lead files
(File ownership). Read-back check: before starting, list in one line
each: the three gates you will compute, the two stop-rules, and the two
things this prompt forbids you to judge.

## Context (read only these)

- docs/quiz-sitting-45g-log.md — WHOLE file (it is short): Amendment 1
  (bar and verdict rule), Amendment 2 (provenance naming), the 7 operator
  rulings + 12621 amendment, control-20 PASS, redo/unreadable completion,
  operator decisions for this step: (a) adjudicated fixes are applied
  row-by-row in PASSED strata; (b) FAILED strata re-run with a
  v2.1-augmented prompt + fresh sealed 100-row gate pack.
- data/annotation/sitting_45g/README-sitting.md — pack semantics.
- data/annotation/calib_45e/README-unreadable14.md — ingest rule for the 14.
- results/sitting_45g2_manifest.json — strata composition (stratum_of),
  integrity fields.

## Step 0 — vault + commits (before any code)

1. Run /save (hot.md is stale — refresh it).
2. Commit the team-lead session artifacts (committing TL files is allowed,
   editing them is not), atomic, in this order:
   - "sitting: control-20 on team lead passed 20/20" —
     data/annotation/sitting_45g/check20_blind.csv,
     docs/quiz-sitting-45g-check20.md, docs/quiz-sitting-45g-log.md,
     docs/STATUS.md
   - "sitting: TL labels for redo-75 and unreadable14 (Amendment 2)" —
     data/annotation/sitting_45g/emptied_redo.csv,
     data/annotation/calib_45e/unreadable14.csv, docs/PROMPT-4.5g3.md
3. git status must be clean afterwards; show it.

## Task 1 — reader script + per-stratum gates

scripts/read_sitting_returns.py (+ tests): parse precheck300.csv
(semicolon, utf-8-sig, csv module only), validate against
sitting_45g2_manifest.json (unknown columns / changed frozen columns =
REFUSE, same discipline as the 4.5f harness). Compute per stratum
(stratum_of from the manifest): agreement = correct/100, bar >= 0.90,
pre-registered in Amendment 1. Also recount the total; the log records
258 correct / 42 incorrect — STOP-RULE 1: if your recount disagrees with
the CSV-derived total you compute, report both numbers and stop; the CSV
is the authority, nothing is reconciled silently. Write
results/sitting_45g_gates.json: per-stratum n/correct/agreement/verdict,
totals, sha256 of precheck300.csv, and echo of the bar. Numbers reach the
report ONLY via this script's output.

## Task 2 — apply adjudicated fixes in PASSED strata (operator decision)

For the incorrect rows whose stratum PASSED: where the verdict's notes
determine the correct value unambiguously (e.g. "taste" = taste missing,
"unclear" = unclear:true, pattern rulings P1/P6/P7 as written in the
log), apply the fix to the staged doraz-labels with provenance
"fix: sitting-verdict" in the row's notes/annotator trail. Where the note
does NOT determine the value — do not guess; list those ids in the report
as PENDING. Show a per-field diff count. Rows in FAILED strata are NOT
fixed here — their whole пласт goes to wave 2.

## Task 3 — merge

- PASSED strata of the 1 912 doraz rows: accept into the train sources
  per the staging layout of 4.5d/4.5e (v2 columns law; frozen sets and
  v1 copies untouched — same non-mutation rules as 4.5e).
- Ingest emptied_redo.csv intents_final (75/75, adjudicated) into the
  relabel column per README-sitting §2 semantics.
- Ingest unreadable14.csv intents_v2 (14/14) per its README (rows join
  the _tax2 files now that the column is filled).
- Provenance names the capture honestly everywhere:
  "team-lead-LLM triage with operator adjudication and operator
  spot-check" (Amendment 2) — never "operator calibration".
- STOP-RULE 2: any sha/manifest mismatch, or harness refusal on a
  returned file → stop and report; do not edit the returned files.

## Task 4 — guideline v2.1

Append a "v2.1 changelog" section to docs/annotation/comments.md (your
file): the 7 operator rulings + the 12621 amendment, verbatim in
substance, each tagged with its source row ids from the log. Do not touch
any v2 rule text; v2.1 is additive law.

## Task 5 — wave-2 pack for FAILED strata (build, do NOT judge)

- Register prompt revision T1v2.1 BESIDE the existing revisions in
  config/registry.yaml (old SHAs immutable): T1v2 + the v2.1 rules
  distilled into instruction lines. Same parent-post/caption inputs.
- Re-run the model on the ENTIRE пласт of every failed stratum with
  T1v2.1. Ledger anchored to /credits BEFORE the first request; hard cap
  $1.50 total — projected overrun = stop and report.
- Build a fresh sealed gate pack: 100 rows sampled from the re-run пласт
  (seed 42, draw convention of build_sitting_pack.py), blind (no model
  attribution), manifest with sha256 + verdicts_present: 0. Bar stays
  >= 0.90. FORBIDDEN: judging this pack, and re-judging precheck300 —
  verdicts belong to the operator/team-lead sitting, next session.

## Task 6 — RECORD + report

ADR knowledge/decisions/45g3-sitting-gates.md: per-stratum numbers, the
two operator decisions (fixes in passed strata; wave-2 = model+v2.1+new
gate), merge scope, wave-2 size and spend. INDEX updated. make check
green — show the count. Report back with: gates table from the script
output, fixes diff counts + PENDING ids, merge summary, wave-2 pack
paths+shas, ledger, and a Deviations section (silence is not compliance).
Out of scope: 54 dual-home ids (4.5h), any Phase-4/frozen artifact, any
retrain.
