# PROMPT-4.5g6 — six dictated verdicts + backfill guard + v2-with-context probe (pre-registered)

You are the executor on market-pulse-llm. Self-contained; do not re-read
docs/SPEC.md. Read only: `results/sitting_45g_gates.json` (rows named below),
`results/features_45g5.json` (family membership), `results/verdicts_45g5.json`
(record form to mirror), `src/market_pulse/prompts.py` (v2 assembly and
build_messages), and the 45g4 probe machinery (plan/runner/scorer — reuse).

## Context (3 lines)

4.5g5 measured the families: replies-to-commenters and channel-identity
explain 17 of 42 refusals, union 885/1912 batch rows; a blind rule would
break 62 judged-correct rows, so the features go to the MODEL as lines of
FACT while the law stays in v2's UNCLEAR_RULE. The operator approved the
probe: v2 prompt + context lines, same 100 ids, thresholds below. The
operator also ruled row 11876 pending-law (untouched this phase).

## Budget

~100 completion requests ≈ $0.037 (per-row cost of the 45g4 probe). Ledger
`results/spend_45g6.json`, fresh anchor BEFORE the first request. Shared cap
$1.50; prior phases' spend is read from their ledger files ($0.7794 total),
divergence over a cent stops the run.

## Task 0 — tree sweep

Commit the vault hook tail and the team-lead files the tree came back with
(docs/STATUS.md refreshed upstream, this file) — verbatim, staged by path.
Anything else dirty: stop and report.

## Task 1 — six dictated verdicts into the batch

Same mechanics, guards and record form as 4.5g5 (new record
`results/verdicts_45g6.json`, chain from `batch_sha256_after` of 45g5;
annotator `sitting-45g-verdicts`; note cites the source ruling; diff exactly
6 rows; check_labels on touched rows; re-run refuses). Values are dictated
by the team lead from the verdict notes — transcribe, do not interpret:

- `@VARUS_channel:8478`  → intents `["service"]`   (note: operator-P7 retroactive — [] should be ["service"])
- `@VARUS_channel:14759` → intents `["availability"]` (note: ["price"] should be ["availability"])
- `@VARUS_channel:11615` → intents `["taste"]`     (note: [] should be ["taste"], dish answer under food poll)
- `@VARUS_channel:18839` → intents `["service"]`   (note: queue at the till is service by the guideline letter)
- `@VARUS_channel:8932`  → intents `["quality","taste"]` (note: explicit taste beside quality; label both)
- `@VARUS_channel:9271`  → intents `["service"]`   (note: promo-reward reaction, service family; unclear already false since 45g5)

Untouched and listed: `@VARUS_channel:7555` (no value named),
`@msuaaaa:11876` (pending-law, operator decision 03.08).

## Task 2 — backfill guard (4.5g5 deviation 11)

`scripts/backfill.py` must refuse to write into `data/raw/comments/` (v1)
unless an explicit `--allow-v1-write` flag is passed; the refusal names the
reason (v1 homogeneity: rows collected before reply_to would sit beside rows
with it). Test both branches.

## Task 3 — register the v2-with-context revision

New registered prompt beside the old ones (follow registry naming
conventions; suggestion: `precheck_v2ctx_with_post`): the v2 base text is
UNCHANGED — the revision differs only in rendering, where build_messages adds
up to two optional context blocks beside [post]/[poll]/[image description],
rendered from data:

- Reply block, rendered when the reply discriminator of
  features_45g5 fires (reply target is not the thread head):
  `[reply] Addressed to another commenter in the thread.`
- Sender block, rendered only for the two channel-identity ids:
  for 2fa2b73f…: `[sender] The channel's own identity of @VARUS_channel is speaking — the retailer itself.`
  for 58805a36…: `[sender] The channel's own identity of @msuaaaa is speaking — an aggregator that reposts retail offers.`

Templates verbatim — transcribe, do not improve. These are statements of
fact; the law stays in UNCLEAR_RULE, unchanged. Register in all registry
tables the way v2 precheck is registered (four fields). Changelog section
`v2ctx changelog` in docs/annotation/comments.md: what renders when, marked
RENDER-ONLY (prompt text identical to v2).

Guards: (1) transcription test on the three templates
(whitespace-insensitive); (2) negation-scan on the templates (same regex as
the v2.2 guard) — they are written to pass it; (3) **byte-identity guard:
for a row with no feature, the rendered v2ctx prompt equals the rendered v2
prompt byte-for-byte** — unit test on a real featureless row.

## Task 4 — pre-register the probe plan (BEFORE any request)

`results/v2ctx_probe_plan.json`, committed before the run:

- Same 100 ids as results/v22_probe_plan.json (fifth paired column).
- References: sealed-pack labels + named-value rulings (the 35 of 45g5 plus
  the 6 of Task 1). `preserved` and `fixed` defined exactly as in 45g4.
- Two denominators, both computed and written into the plan: preserved
  n=58; `feature_named` = named-value rulings whose row carries a feature
  per features_45g5 (expected ≈17 — compute the exact n).
- Gate, one attempt: **PASS = preserved ≥ 55/58 AND feature-fixed ≥
  ceil(0.70·n). KILL = preserved < 52/58 OR feature-fixed < ceil(0.50·n).**
  Between: the operator decides. Non-feature named rulings: reported,
  ungated. In-sample caveat as before. Reference points: on feature-named
  rulings v2 = 0, v2.2 = 2.

## Task 5 — run the probe

`precheck_v2ctx_with_post` (or your registered name) on the 100 ids, same
model `qwen/qwen3.6-27b`, same pinned endpoint, same posts/surrogates —
plus the context blocks where features fire. Score per plan into
`results/v2ctx_probe_results.json` with the paired columns (v2, v2.1, v2.2,
v2ctx); per-family fixed breakdown; preserved_lost ids; per-field moves.
Rows file beside it. Ledger updated. Print the gate table.

## Hard stops

- No requests beyond the ~100 named. No surgical batch run this phase — it
  is the NEXT briefing's decision, on these numbers.
- One attempt; no re-prompting, no threshold edits after the plan commit.
- `data/annotation/wave2_45g3/`, frozen sets, raw v1 comment files —
  untouched; re-verify wave2 manifest hashes and show the check.
- Do not edit docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*.md (team-lead
  files, File ownership).
- State assumptions; if the probe machinery or registry shape differs from
  what this prompt assumes — stop and report.

## RECORD

ADR `knowledge/decisions/45g6-context-lines-probe.md` (+ INDEX): facts-not-
rules decision with the 62-vs-10 number, the six dictated values, the 11876
deferral, the gate formula with computed n. hot.md Next updated.

## Commits (atomic, repo green after each; runner-before-run as you did)

1. chore: tree sweep
2. feat: six dictated verdicts + chain record
3. feat: backfill v1-write guard
4. feat: v2ctx registration + template/byte-identity guards + changelog
5. feat: probe plan pre-registered (with computed n)
6. feat: probe run + paired results + ledger + ADR

## Before executing

Read back in one line each: the gate formula with both denominators, the
byte-identity guard, the hard stops, and the file-ownership line.

## Report

Gate table with verdict and all paired columns; feature-fixed breakdown by
family; preserved_lost ids; the exact n and how it was computed; spend;
make check count; Deviations in implementation-notes.md — silence is not
compliance.
