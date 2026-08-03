# PROMPT-4.5g2 — images, captions, the 424 re-checked; quiz rulings applied (rev. 2)

**Context.** The chat quiz on the emptied-97 remedy scored 11/20 against
the pre-registered 18/20 — auto-remedy rejected. The operator named the
root defect: MEDIA-ONLY posts give both the human and the model nothing.
Operator decisions (2026-08-03): fetch the post images AND caption them
with a vision model, so a text description of the post enters the
with-post prompts; re-precheck the 424 media-only up-label rows with
captions; the sitting pack is rebuilt BEFORE any verdict was given
(supersession is legitimate and named, never silent). Verdict table:
`docs/quiz-45g-verdicts.md`. Budget: **≤$0.75 OpenRouter**
(`results/spend_45g2.json`, anchored BEFORE the first request,
hard-cap). Telegram API for media download only.

## Step 0

Commit strays + team-lead edits (docs/quiz-45g-verdicts.md,
docs/STATUS.md, this file):
`docs: the quiz verdicts and the caption decision — the 4.5g2 prompt`.

## Step 1 — ADR

One ADR: the quiz outcome (11/20, auto-remedy rejected), the caption
decision (vision captions as post-text surrogate, tagged in-prompt as an
image description), the pack supersession (resealed before any verdict
existed). `accepted`; cite the verdict table and STATUS.

## Step 2 — apply what the quiz validated

Apply pattern, intents only: (a) the 11 matched rows, authority
`operator-quiz-45g`; (b) the taste family by mechanical rule — v1 ==
`["taste"]` AND short filling/dish answer AND no watchlist brand token
AND media-only parent — authority `quiz-validated-pattern` (10/11);
every id listed. The 9 divergent rows are NOT applied — redo file only.

## Step 3 — fetch the images

Unique parent posts of: the 97, the 424 media-only precheck rows,
`unreadable14.csv`. Existing session machinery; download to
`data/annotation/sitting_45g/posts_media/<channel>_<msg_id>.jpg`.
Unfetchable media is LISTED, never guessed. Session needs re-login →
STOP and say so.

## Step 4 — caption the images (vision model)

A cheap pinned vision endpoint on OpenRouter — ANY model except the
model under test (gemma family); record the pin. The captioning prompt
is a REGISTERED constant with its SHA (beside, `TASKS` untouched):
factual, in the post's language, ≤2 sentences, and it MUST transcribe
any text visible in the image (poll questions, prices, dates). Output:
`data/annotation/post_captions.jsonl` — channel, msg_id, caption, model,
prompt sha, image sha256. Raw posts files are NEVER written. The
with-post plumbing gains: post text if present, else the caption
rendered as `[image description] …` — the model must know it reads a
description, and provenance stays honest.

## Step 5 — re-precheck the 424 with captions

The 424 media-only up-label rows re-run through the full-field precheck
under the caption-fed prompt; staged output replaces their empty-post
rows (append-style record, both runs kept). Report how many of the 424
changed which fields — that diff is the measurement of what captions
buy. Also re-run the ~40 redo-file rows through the caption-fed
re-labeller so the redo file can show the operator an informed model
column (`intents_model`); nothing from it is applied.

## Step 6 — rebuild the sitting (same draw, new seal)

Same 300 ids (seed-42 draw unchanged — the population did not change),
labels refreshed for rows Step 5 touched; `emptied_redo.csv` (the 9 +
whatever Step 2 did not close: `id;text;post_media;caption;intents_v1;
intents_model;intents_final;notes`, final BLANK); `media_map.csv` +
captions beside every media-only row; README updated (images + captions
sit beside; `["taste","service"]` format; `[]` is a full answer). New
manifest `results/sitting_45g2_manifest.json` with all shas and the same
per-stratum rule text; the old manifest is marked superseded IN THE NEW
ONE, never edited.

## Verify-gate — show output

1. `make check` green; count. Old and new prompt SHAs verify.
2. Applied diffs: 11 + taste-family count, before/after.
3. Fetch + caption report: unique parents, fetched, captioned,
   missing-by-name; one caption printed as a sample.
4. The 424 diff: rows changed per field, empty-post vs captioned.
5. New manifest shas; ledger ≤ $0.75 against the anchor.
6. `git log --oneline` — atomic commits.

## Report

Three plain lines; how many of the 97 are closed vs in redo; what
captions changed in the 424; the sitting contents and location;
Deviations; open questions. STOP — the operator sits ONCE, with images
and captions; the reader prompt then closes strata, redo and merge.

## DO NOT

- No new corpus collection beyond the named parents' media.
- Raw store files are immutable; captions live in their own file.
- The gemma family never captions and never labels.
- Sealed 45g manifest: superseded by naming, never edited or deleted.
- Nothing proposed in `intents_final`; the 9 stay unapplied until the
  operator rules with images.
- No frozen-file changes; `TASKS`/v1 SHAs immutable; no training, no
  pods. Team-lead files commit-only. Artifacts English.
