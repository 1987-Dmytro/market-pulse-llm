# PROMPT-4.5g — parent context, the 97, the up-label precheck + its pack (rev. 1)

**The 4.5f gate is green and the operator decided (2026-08-02):**
(1) v2 prompts gain the PARENT POST now, before the anchor and the
retrain; (2) the 97 emptied rows are re-labelled by the with-post model
and checked by an operator sample; (3) the 1,912-row up-label goes ahead
(4.5d appetite) under a full-field v2 precheck. Budget: **≤$1.25
OpenRouter** (`results/spend_45g.json`, anchored BEFORE the first
request, hard-cap); everything else $0.

## Step 0

Commit stray vault files + team-lead edits (docs/STATUS.md, this file):
`docs: the 4.5f gate — parent context decided, and the 4.5g prompt`.

## Step 1 — ADR

One ADR for the 4.5f gate decisions: parent context (why now — T1v2 has
no recorded runs, the fresh anchor is not yet taken, the 97-row class is
unlabelable without it), the 97-row remedy (model-with-post + sampled
verdicts, fallback pre-registered below), the up-label go. `accepted`,
citing `results/drop_45f.json` and docs/STATUS.md.

## Step 2 — parent context, as new registered revisions

`T1v2` and the re-label/precheck prompts gain the parent post text as
NEW registered revisions BESIDE the existing ones — new SHAs, `TASKS`
untouched, every recorded run still verifies (extend the negative
control). Plumbing: the parent is `msg_id == parent_msg_id` in
`data/raw/posts/<channel>.jsonl`; every comment's parent exists by
collection — a missing parent is a STOP, not a skip. Tests: a rendered
prompt fixture with the parent embedded; the registry tests extended.

## Step 3 — the 97, re-labelled with the post

Run the 97 emptied rows through the with-post re-labeller (~$0.02),
apply to the staged `_tax2` files with the fixes-block provenance
pattern. Operator check, PRE-REGISTERED here: a seeded 40-of-97
contrastive sample (`intents_v1` vs the with-post set,
verdict old/new/neither); **rows marked `new` / 40 ≥ 0.90 accepts the
batch of 97; below the bar, ALL 97 go to the operator by hand.** The
sample file joins the sitting pack of Step 5.

## Step 4 — the up-label precheck (nothing merges into train here)

Full-field v2 precheck of the 1,912 labelable rows: sentiment, sarcasm,
intents (6-class), unclear — Phase-2 batch machinery, the with-post
prompt, `qwen/qwen3.6-27b` at the pinned fp8 endpoint. Output: staged
annotation batch file(s), `annotator: "llm-precheck"`; NOTHING merges
into any train file until the strata gates pass.

## Step 5 — the sitting pack (operator ~2.5 h, one sitting)

Calibration of the precheck at the pre-registered bar, per stratum
≥90%, row-level `correct`/`incorrect` (a row is correct only if every
field is): strata (a) service-rich draw 100, (b) short-text ≤30 chars
100 (the known weak class), (c) general 100. Seeded, blind (nothing in
a pack file says which stratum a row is in or what the model was unsure
of), denominators written in the manifest BEFORE handover, one manifest
sha-pinning every file. A stratum below 90% sends its whole batch back
(second-round rule). The sitting bundles: the 300, `unreadable14.csv`,
and the 40-of-97 sample.

## Verify-gate — show output

1. `make check` green; count. Old AND new prompt SHAs verify; negative
   control shown.
2. A rendered with-post prompt for one row, and the parent-missing STOP
   demonstrated on a fabricated id (test, not corpus).
3. The 97: applied diff summary + the 40-row sample manifest.
4. Precheck: row counts (1,912 in → staged out + unusable named), ledger
   ≤ $1.25 against the anchor.
5. Sitting-pack manifest: 300 + 14 + 40, strata sizes, shas.
6. `git log --oneline` — atomic commits.

## Report

Three plain lines; what the with-post re-label did to the 97 (how many
regained a label, which); precheck unusable count; the sitting pack's
location and the operator's instructions; Deviations; open questions.
STOP — the operator's sitting comes back, the strata gates decide the
merge, then the team lead briefs 4.5h (test v4, the lifted guard, the
54 dual-home ids, the fresh with-post G1c anchor, the retrain, new bars
BEFORE scoring).

## DO NOT

- No frozen-file changes; no test/holdout rows anywhere.
- Nothing merges into train/candidates files in this prompt.
- `TASKS`, the v1 prompts and every recorded SHA are immutable; new
  revisions register BESIDE, never replace.
- Originals and `_tax2` staged files: `_tax2` may be touched ONLY by the
  Step-3 fixes-pattern applier; originals are read-only.
- No training, no pods. Team-lead files commit-only. Artifacts English.
