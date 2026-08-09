# PROMPT-opus-audit-protocol — one Opus 5 session, one pack (REVIEW class)

> Authority: SPEC §3.16. You are the SECOND instrument reviewing the
> first (the deterministic brand matcher and the GM4 captioner). Your
> output is REVIEW FINDINGS for an operator sitting — it will never be a
> gate number. Honesty over helpfulness: an empty finding ("the matcher
> missed nothing here") is a good finding.

## Session rules

1. FIRST line of your output: the model you are running as. If it is not
   Opus 5 (claude-opus-5), STOP and say so — the whole point of this
   review is the stronger model.
2. ONE pack per session (`data/annotation/opus_audit_5c1/pack_NN.md`),
   assigned by the operator. Do not open other packs; do not re-read
   project docs — the pack is self-contained on purpose.
3. Write your rows to `data/annotation/opus_audit_5c1/returns_NN.jsonl`,
   one row per item, schema exactly as the pack's empty rows show. Never
   edit the pack file itself.
4. You may read the image files the pack names (S4 items) — that is the
   task. Read the images BEFORE judging the caption.

## What to judge, per item

- **Closed-book:** which watchlist brands (the canon table at the top of
  the pack, all display_names, declensions and homoglyph variants count)
  are ACTUALLY mentioned in this post's text / visible in its images?
  List them — independently of what the matcher said.
- **Open extraction:** any OTHER dairy or ice-cream brand names present
  (UA/RU spelling as seen). Not general food brands — dairy and ice
  cream only.
- **S4 caption check:** with the images open, verdict on the GM4 caption:
  `faithful` (describes what is there) / `partial` (true but misses
  category-relevant content) / `wrong` (describes things not present).
  Then `brands_visible_missed`: brand names readable in the image that
  the caption does not carry.
- **Note (one line):** anything patterned — a declension the lexicon
  would miss, a brand that only ever appears in images, a private label
  spelling, a systematic caption blind spot.

## What NOT to do

- Do not re-score, re-grade or second-guess the screen's PASS/FAIL bars —
  out of scope by SPEC 3.16 (1).
- Do not edit any file except your own `returns_NN.jsonl`.
- Do not average, total or conclude across packs — the reader script
  aggregates; your job is rows.
- Do not consult the internet or outside knowledge for "what brands
  exist" — only what is IN the post text and images counts as a mention.

## Close of session

Last lines: items judged / items in pack, and a one-line honest summary
("matcher missed N candidate mentions, captions wrong on M of K").
English rows; the note field may quote UA/RU text verbatim.
