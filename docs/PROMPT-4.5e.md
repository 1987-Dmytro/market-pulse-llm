# PROMPT-4.5e — taxonomy v2 re-label: staged files, drift, calibration pack (rev. 1)

**The 4.5d gate is decided (operator, 2026-08-02).** Appetite: ALL 1,912
labelable rows will be up-labelled — but only AFTER this step's re-label
passes the ≥90% calibration; nothing here touches the up-label pool. The
three boundary rulings in guideline v2 are RATIFIED as written (shashlik →
`price`+`service`; both giveaway examples → `service`). The re-label set is
ALL labelled data per amendment 3.8 — non-frozen rows here; frozen
test/holdout rows are 4.5f's (test v4), where the code guard is lifted as a
code change. Budget: **≤$1.50 OpenRouter**, anchored ledger, hard-cap
enforced; everything else $0.

## Step 0

Commit the uncommitted `/save` artifacts (daily log, hot.md, index) +
team-lead edits (docs/STATUS.md, this file):
`docs: the 4.5d gate — appetite decided, and the 4.5e prompt`.

## Step 1 — ADR for the gate

`knowledge/decisions/` + INDEX, status `accepted`, citing
`docs/taxonomy-v2-prep.md` and SPEC amendment 3.8: the appetite decision
(all 1,912, sequenced strictly after the re-label gate), the three ratified
boundary calls, and the staging convention — v2 copies beside originals, a
row's `annotator` field is never rewritten, migration provenance lives in
the run record.

## Step 2 — the re-label

`relabel_intents.py` over EVERY labelled non-frozen row — enumerate the
files with counts in the report (the five files of deviation 5, minus
frozen); `unclear` rows included. The frozen-file refusal stays untouched.
Output: staged v2 files BESIDE the originals (`_tax2` suffix or
equivalent), originals byte-untouched; intents column only, with the same
byte-proof the probe gave. Model `qwen/qwen3.6-27b` at the pinned fp8
endpoint, prompt = the registered `RELABEL_INTENTS_PROMPT` (the fixed
revision that demands the `intents` key). Ledger:
`results/spend_45e.json`, anchored BEFORE the first request, cap $1.50.

## Step 3 — drift, from the rows already paid for

`--from-rows` over the staged output: overall + scoreable/`unclear` split
+ a per-intent churn matrix (which old intents lose rows, which gain,
where `service` came from) — the diagnostic for the drift-without-service
share. No new API calls.

## Step 4 — calibration pack (operator hours: ~1.0)

Per SPEC §8 at the pre-registered bar (≥90% on a 100-row gated sample):
build the review pack — **100 random SCOREABLE rows** (seed 42,
pre-registered here), verdict-style (row text + v2 intents, agree or not),
PLUS **50 changed rows** as a separate DIAGNOSTIC stratum (old vs new
shown; not gated). SPEC §10 discipline: the executor pre-fills, suggests
and comments on nothing beyond the labels under review. Manifest with
shas.

## Verify-gate — show output

1. `make check` green; count. Old prompt SHAs still verify.
2. Staged files: row counts match their sources; every non-intents column
   byte-identical (script output); originals untouched.
3. Drift table + churn matrix; ledger total ≤ $1.50 against the anchor.
4. Pack manifest: 100 + 50, strata named, shas pinned.
5. `git log --oneline` — atomic commits.

## Report

Three plain lines; the file enumeration with counts; drift + churn; the
pack's location and what the operator does with it; Deviations; open
questions. STOP — the operator's verdicts come back, the ≥90% gate decides
the re-label, and only then the up-label (the 1,912) and 4.5f (test v4 →
fresh G1c anchor under the v2 prompt → retrain → new bars pre-registered
BEFORE scoring) get their prompts.

## DO NOT

- No frozen-file changes; no test/holdout rows — the guard stays in place.
- No up-labelling of the 1,912; no training, no pods.
- Never mutate a labelled file in place; originals are read-only inputs.
- The v1 prompt constant, its SHAs and `TASKS` are immutable.
- Do not edit docs/STATUS.md, docs/SPEC.md or docs/PROMPT-*.md — team-lead
  files, commit-only. Artifacts English.
