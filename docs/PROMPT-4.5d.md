# PROMPT-4.5d — taxonomy v2 prep: guideline, pipeline, probe, counts (rev. 1)

**The intents law gate is decided — SPEC amendment 3.8** (read that block
first, it is the law): taxonomy v2 adds a sixth intent **`service`** with the
WIDE boundary, availability keeps product presence/stock/delivery-of-the-
product, co-occurrence allowed; 17 of 19 disputed `[]` rows stand under the
old law (context artifact, recorded). This step PREPARES everything and
probes cost/drift; the full re-label, test v4 and the retrain are 4.5e,
after the appetite gate. Budget: **≤$2 OpenRouter** for the probe, hard-cap
enforced; everything else $0.

## Step 0

Commit team-lead edits (docs/SPEC.md → rev. 3.8, docs/STATUS.md, this file)
+ day records: `docs: the intents law — amendment 3.8 and the 4.5d prompt`.

## Step 1 — guideline v2 (docs/annotation/comments.md)

- Add `service` to §intents with the amendment 3.8 definition as law;
  examples drawn from the audited rows (giveaway distrust, the hotline
  rant, the promo-mechanics questions — they are now citable law examples).
- Update the sections that previously sent these cases to `[]` (off-topic
  replies; the promo-mechanic sentence under `price`; giveaway noise stays
  `unclear` as before — bot `+` spam is not `service`).
- A short "guideline v2 changelog" block at the top: what moved, why, date,
  the amendment reference. Old law stays readable in git history.

## Step 2 — pipeline + prompt versioning

- The intents re-labeler: Phase-2 pipeline machinery, 6 classes, INTENTS
  COLUMN ONLY (sentiment/sarcasm/unclear untouched by construction —
  assert it).
- The T1 eval prompt grows the sixth class as **prompt v2** REGISTERED
  BESIDE v1: new constant, new SHA; the v1 constant and every recorded SHA
  stay untouched — old records must keep verifying.

## Step 3 — the probe (≤$2, train rows only)

Re-label ~50 ALREADY-labeled TRAIN rows (seeded sample; never test rows):
report old-vs-new drift rate, estimated `service` prevalence, per-row cost,
and the projected cost of the full re-label (comments_train + candidates +
test = ~2 746 rows). Ledger: extend the OpenRouter spend pattern (anchored,
enforced before start).

## Step 4 — up-label candidate counts ($0)

From the raw corpus (11 338 comments): counts of (a) service-rich rows by
keyword heuristics (delivery/order/support/app/checkout, UA+RU forms),
(b) sarcasm-rich rows by the existing irony heuristic, (c) the remaining
general pool. Counts and overlaps only — label nothing.

## Step 5 — calibration plan

Per the pre-registered ≥90% agreement threshold: sample sizes and estimated
operator hours for (i) the re-label calibration and (ii) up-label
calibration at three appetite tiers (~+2k / +5k / +9k rows).

## Verify-gate — show output

1. `make check` green; count. Old prompt SHAs still verify (test shown).
2. Guideline v2 diff summary; the changelog block.
3. Probe: drift table, prevalence, cost per row, projection; ledger ≤$2.
4. Candidate-count table with the heuristics named.
5. `git log --oneline` — atomic commits.

## Report

Three plain lines; probe drift + prevalence; the candidate counts; the
calibration-hours table by tier; Deviations; open questions. STOP — the
4.5d gate decides the appetite and gives the go for 4.5e.

## DO NOT

- No changes to any frozen file, any gold, v2/v3 test sets, or dumps.
- No labeling beyond the 50-row probe; no test-row labeling at all.
- No training, no pods. The v1 prompt constant and SHAs are immutable.
- Team-lead files commit-only. Artifacts English (guideline included).
