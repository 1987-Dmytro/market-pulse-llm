# PROMPT-5c2-validate-prep — the sitting pack, and three report debts

**Contract:** SPEC **3.18 (6)** (the operator sitting — read that clause and the
`validate_consequence` block of `results/prereg_5c2_run.json`) and this file.
**$0 session:** no pod, no endpoint, no serverless job, no OpenRouter call, no
Telegram client. All artifacts in English EXCEPT the operator-facing pack
rendering, which is in Russian (it is an operator-comprehension artifact, the
STATUS.md exception). Team-lead files are read-and-commit, never edit.

**Context in three lines:** the run bought the whole window and its evidence is
complete (5 423 rows, 0 failures). The phase cannot close without the operator
sitting of 3.18 (6). This contract builds the pack the sitting reads from —
drawn under a RECORDED seed, from result files only, failing loudly on any gap.

## Step 0 — the tail, and three debts of the accepted run report

Live `git status --short`, verified at issue: `docs/STATUS.md` (M — team-lead
hand), `knowledge/daily_logs/2026-08-14.md`, `knowledge/index.md` (M — session
end), `docs/PROMPT-5c2-validate-prep.md` (untracked, this file). Two commits by
path (`docs:` and `docs(vault):`), then the debts, each its own commit:

1. **Dv307 settled by measurement, not by re-reading.** The acceptance's review
   found `except BaseException` now wraps both `assert_serving` call sites, so
   a refused handshake likely DOES write a ledger row — contradicting Dv307's
   "not fixed". Write the test that drives `main()` into a handshake refusal
   (stubbed transport answering a wrong `info()`) and asserts what `finalise`
   leaves on disk. Whatever it measures, amend Dv307 with the answer and the
   nodeid. Both directions: the test must also show the refusal itself fires.
2. **The $0.8451 citation.** The Endpoint-B go/no-go budget used `--already-usd
   0.8451`, an operator-typed safer-reading; the persisted ledger row says
   0.8230. Report addendum: state its provenance (the balance read it came
   from, if the session transcript holds one; otherwise say plainly it was a
   hand-typed conservative reading), and print 0.8230 beside it with the Dv33
   floor sentence. A hand-supplied number in a money path is legal only when
   the record names it as such.
3. **calls 55 vs 53 packs + 1 warm-up.** One line in the addendum naming the
   extra call (the `assert_serving` handshake, if that is what it is —
   verified against `run_5c2_comments.json`, not asserted).

## Deliverable 1 — the window summary record (the aggregates the rows wear)

3.18 (6) captions every shown row with "the aggregate the row belongs to", so
the aggregates must exist as a record before the pack can wear them.
`scripts/window_summary_5c2.py` → `results/window_summary_5c2.json`, reading
ONLY `data/derived/` + the sealed registration:

- comments: per-head distributions over the 5 075 (sentiment incl. per-language,
  sarcasm rate, intents frequency, brand attributions), per channel and total;
- positions: per-channel counts, tier distribution over the 145 position rows,
  promo/depth fields present-vs-absent counts (depth values only where (1)'s
  law allows them to surface);
- post_text: the 44 — positions found / empty / unreadable, by channel;
- house hygiene: `producer.sha256` + borrowed-module hashes, no clock, no git
  block; determinism pair (two runs, both sha256); every number a test can
  re-derive — this record will feed Phase 6's dashboard, so no hand-typed
  numbers anywhere downstream of it.

## Deliverable 2 — the sitting pack

Builder in the house pattern of `scripts/build_sitting_pack.py` (SEED
constant, seeded draw over sorted ids, seeded shuffle — read it first, reuse
its shapes). New script, e.g. `scripts/build_validate_pack.py` →
`results/validate_5c2_pack.json` + an operator-readable rendering
`results/validate_5c2_pack.html` (Russian, images inline or repo-relative
paths resolved via `loop.page_file`):

- **the draw:** ≥5 leaflet POSTS (a post = its pages + every position extracted
  from them) and ≥5 comments, drawn under a RECORDED seed from the window's own
  output — never picked. Stratify lightly so the comment draw is not all
  `@matusi_ukr` (e.g. one per channel for the top-5 channels by volume, seeded
  within each) — state the strata in the record; a hand-picked example is a
  demo, not a validation.
- **per leaflet post (3.18 (6) verbatim):** the page image as it was SENT, the
  positions returned, and field by field what made each a POSITION rather than
  a product_mention (brand, line, category, size, attribute), the price fields
  with (1)'s depth, and the tier the ladder assigned — with the ladder inputs
  shown so the rung can be re-derived at the table.
- **per comment:** the comment as written, its parent post, the exact rendering
  the model was given, and every head's verdict (sentiment, sarcasm, intents,
  brand attribution) — each captioned with the aggregate it belongs to from
  Deliverable 1, so a single row is never read as the population.
- **honesty rails:** reads from `data/derived/` + `results/` only; FAILS LOUDLY
  on a missing source (negative control: point it at a sandbox copy with one
  file removed and show the refusal); the seed, the strata and the drawn ids
  are IN the record; re-run under the same seed is byte-identical (pair shown).
- **the sitting's paperwork, pre-built:** a `findings` skeleton in the record —
  one slot per shown row for `ratified | disputed` plus a free-text note —
  which the team lead fills DURING the sitting; findings become watchlist,
  lexicon or prompt-revision ORDERS in the REVIEW class of 3.16 (1), never
  re-scored numbers and never a moved bar (write that sentence into the
  rendering's header so it is on the table during the sitting).

## Do NOT

- Spend anything; nothing cloud-touching at all.
- Do not modify, re-score or re-order anything under `data/derived/` — the
  pack READS the run's output; a sitting over edited evidence validates the
  editor. Do not touch the sealed registration, the run records, cap-30
  records, team-lead files. No `git add -A`.
- Do not pre-fill a single `findings` slot.

## Report

`docs/reports/5c2-validate-prep.md`, three plain sentences first; the debts'
evidence (the Dv307 test output both directions); the determinism pairs; the
negative control's refusal message; Deviations **Dv316+** with `[cause: …]`
tags and the **Process signals** section (≤5 lines).

**Read-back before you start:** one line each — where the aggregates the rows
wear come from; what the pack does on a missing source; who fills `findings`
and when; and the one thing this session must never edit.
