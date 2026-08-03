# PROMPT-4.5g5 — adjudicated truth into the batch + reply_to collection + family measurement

You are the executor on market-pulse-llm. This file is self-contained; do not
re-read docs/SPEC.md. Read only: `results/sitting_45g_gates.json` (the `rows`
array: id/verdict/notes), the 4.5g3 stated-rulings parser, the batch file your
4.5g3 merge wrote (the one carrying the 89 hand rows, annotator: sitting-45g),
and the collector module for comments.

## Context (3 lines)

The v2.2 probe KILLed on both counters — the prompt-form track is closed by
pre-registration. The team lead's raw-store measurements located the two error
families: channel-identity senders (~7 of 42; `sender_anon_id` exists, but a
blanket unclear-rule would break 10/45 of their judged-correct rows) and
replies-to-commenters (~10–12 of 42; NO reply data exists — parent_msg_id of
all 11.3k comments points at a post). The operator chose path A: hand-apply
the adjudicated verdicts, teach the collector reply_to, re-fetch, measure.

## Budget

**$0.00 in completion requests — no model is called in this phase.** Create
`results/spend_45g5.json` with a fresh provider anchor before any work; at
phase end show that the delta is $0.00 (the anchor guards against accidents).
Telegram re-fetch uses the existing collector session and its rate limits.

## Task 0 — tree sweep

If the vault hook wrote after the last commit (daily log, index), commit that
tail as a chore. If anything else is dirty, stop and report.

## Task 1 — apply the adjudicated verdicts to the batch

Scope: ONLY rulings that name a value — the 29 parseable stated rulings
(reuse the 4.5g3 parser) plus the P5/P6 family values fixed in the quiz log
(P5 → intents ["service"]; P6 → per the recorded rulings). Per touched row:
set exactly the named fields, leave unnamed fields as they are, set
`annotator: sitting-45g-verdicts`, add a note naming the source ruling. Rows
whose notes name the error but no value: untouched, listed in the report by
id. Guards: `check_labels` runs on every touched row; the file diff is
exactly the touched rows; population and derived counts re-derived by script.

## Task 2 — collector learns reply_to

Persist the raw Telegram reply target for comments (the client library's
reply-to message id) in the collector. Store the raw value; derive nothing at
collection time. Unit test on a fabricated message object. Do NOT touch post
collection and do NOT add `message.poll` handling — that is a named Phase-5
debt, deliberately not bundled here. No new channels.

## Task 3 — re-fetch the two comment stores, join, measure drift

Fresh fetch of @VARUS_channel and @msuaaaa comments into
`data/raw/comments_v2/` — a NEW directory; the v1 files stay byte-untouched
(labels were made on v1 texts, and v1 text remains law). Join by
(channel, msg_id): a v2 record = the v1 record + `reply_to` from the fresh
fetch. Report drift honestly, counts only: v1 messages missing from the
fresh fetch (deleted), texts that differ (edited — v1 text stays
authoritative), fresh-only messages (out of corpus, ignored).

## Task 4 — measure the families

`results/features_45g5.json`, every number script-derived:

- replies-to-comments (reply target is another comment, not the post):
  among all comments · among the 1912 batch · among the 42 errors · among
  the 300 judged, split by verdict — the judged-correct hits measure the
  "accuses the retailer directly" exception, i.e. the cost of any naive rule;
- channel-identity rows (the two hyperactive `sender_anon_id`s): the same
  four counts, re-deriving the team lead's numbers (219 / 46 / 7 errors,
  and the 10-of-45 judged-correct rows with unclear=false) programmatically
  for the record;
- the overlap of the two families.

These numbers feed the next briefing: pre-registration of a probe of the
**v2 prompt + context lines** (NOT the v2.2 rules). Do not register any
prompt and do not call any model in this phase.

## Hard stops

- Zero completion requests.
- `data/annotation/wave2_45g3/` untouched — re-verify both manifest hashes
  at the end and show the check.
- Frozen test sets untouched; raw v1 comment files byte-identical at the
  end (show the check).
- Do not edit docs/STATUS.md, docs/SPEC.md or docs/PROMPT-*.md — team-lead
  files (File ownership).
- State your assumptions; if the batch file, the parser or the collector
  are not shaped as this prompt assumes — stop and report rather than
  inventing a workaround.

## RECORD

ADR `knowledge/decisions/45g5-features-over-prompts.md` (+ INDEX): the KILL
closure, the two families with measured sizes, the overlay-unsafety finding
(10/45), the path-A decision, and what the next probe will be. hot.md Next
updated.

## Commits (atomic, repo green after each)

1. chore: tree sweep (if needed)
2. feat: adjudicated verdicts applied + guards
3. feat: collector persists reply_to + test
4. feat: comments_v2 fetch + join + drift report
5. feat: family measurement + ADR + zero-spend ledger

## Before executing

Read back in one line each: the zero-request rule, what stays
byte-untouched, and the verdict-apply scope (named values only).

## Report

Touched-row counts per field; skipped rows with reasons; drift counts
(deleted / edited / fresh-only); the family table; the zero-spend proof;
make check count; Deviations section in `implementation-notes.md` cited in
full — silence is not compliance.
