# PROMPT-5c2-close — the sitting's returns, amendment 3.19's consumers, the phase retro

**Contract:** SPEC 3.18 (6) (the sitting — now HELD, both halves ratified),
amendment **3.19** (the Dv324 ruling, in its own marked block), and this file.
**$0 session.** Team-lead files read-and-commit, never edit. All artifacts in
English.

**Context in four lines:** the operator held the sitting 2026-08-14: the
leaflet half — 6 posts / 36 positions — RATIFIED verbatim («распознавание SKU
идеальное»), the comment half — 5 of 5 — RATIFIED, zero disputed, zero orders.
His Dv324 ruling became amendment 3.19 (team-lead hand, already in SPEC), and
the amendment's arrival reddened SIX tests — the DESIGNED refusals whose
message says "add its name here and look at it". This contract writes the
returns, teaches the enumerations the new name, and closes the phase.

## Step 0 — the tail

Live `git status --short` at issue: `docs/SPEC.md` (M — amendment 3.19,
team-lead hand; the amendment-index block is UNTOUCHED — verify byte-identity
of that block against `50c5727` before committing, it is inside a sealed pin),
`docs/STATUS.md` (M — team-lead hand), `knowledge/daily_logs/2026-08-14.md`,
`knowledge/index.md` (M), `docs/PROMPT-5c2-close.md` (untracked, this file).
Commits by path: `docs:` (SPEC + STATUS + this prompt) and `docs(vault):`.
NOTE: the tree is expected RED at step 0 (six failures, listed below) — the
step-0 commits are docs-only and land red by design; step 0.5 is what greens
the tree, and `make check` gates every commit AFTER it.

## Step 0.5 — amendment 3.19's consumers (one root, six tests)

The four direct failures and their fixes, verified against disk before editing:

| consumer | fix |
|---|---|
| `scripts/write_prereg_5c2.py:101` block-set refusal | the write-path enumeration learns `amendment-3.19` (a FUTURE registration may be written over the grown law); the SEALED record's own pin still verifies through the TEN-block keep — do not touch the record |
| `tests/test_prereg_5c2.py::test_the_registered_law_is_the_spec_with_every_block_it_carries_today` | reformulate: the sealed pin DERIVES from today's file through the ten-block keep (`registered_law` strips 3.19); "every block it carries today" had a shelf life — the law grows, the pin survives, and that is the design being asserted |
| `tests/test_prereg_5c2.py::test_an_eleventh_marked_block_is_refused_rather_than_stripped` | the planted intruder becomes `amendment-3.20` (a TWELFTH); the refusal still fires |
| `tests/test_sku_prereg.py:248` block-list enumeration | learns the name; then verify the sku pins still derive exactly (their regime strips the whole family, so 3.19 is stripped anyway) |
| `tests/test_run_5c2.py::test_every_pinned_input_is_byte_identical_today` | decouple `docs/SPEC.md` the cap-in-force way: the RUN is complete and sealed — the live check becomes "the ten-keep strip of today's file equals the sha the sealed record pins" (the bytes the run consumed are recoverable), never a raw-byte-identity with a shelf life |
| `tests/test_run_5c2.py::test_a_refused_handshake_writes_the_ledger_row_and_the_record` + `test_the_registration_refuses_while_the_suite_is_red` | expected green once the gates above pass — verify, and if either is still red the cause is NOT this table: STOP and report |

Both directions on each edited guard: the old failure planted (a genuinely
moved KEPT block must still refuse; a raw-identity check must still catch a
strip that stops deriving).

## Deliverable 1 — the sitting's returns

`scripts/write_validate_returns.py` → `results/validate_5c2_returns.json` (the
`read_sitting_returns.py` pattern — read it first). The record pins the pack it
answers (`results/validate_5c2_pack.json` sha `2fad5339…`) and carries:

- sitting held 2026-08-14, asynchronous, verdicts relayed through the team
  lead; operator time actual as relayed;
- leaflet half: 6 posts / 36 positions — **ratified**, operator's verbatim:
  «распознавание SKU идеальное» (quote it as data, in Russian, untranslated);
- comment half: 5 of 5 — **ratified**;
- disputed: **0** · orders issued: **0** · the one RULING the sitting produced:
  amendment 3.19 (reference, not restatement);
- every `findings` slot of the pack resolved to `ratified` — the record REFUSES
  if any slot is unaccounted or if the pack sha does not match;
- house hygiene: producer.sha256 + borrows, no clock, no git block,
  determinism pair shown.

## Deliverable 2 — `witness_phase_ledger` wired (the run's open question 2)

Team-lead ruling, now due (this IS the next code-touching contract):
`run_5c2.finalise` invokes the witness from BOTH arms, so no future paid exit
leaves the phase ledger silent. Both directions: a finalise that skips the
witness fails a test; a witnessed exit appends the anchor-relative entry the
repair pattern expects. No live ledger is touched in tests (fixtures only).

## Deliverable 3 — the phase retro (the self-improvement loop, PHASE close)

`docs/reports/5c2-close.md` §Retro — aggregate the WHOLE 5c2 program's cause
tags (Dv249–Dv324): the tally per tag, and per REPEATED tag the routed lesson
with its home:

- `[model]` cluster (warm-up sampling, price-vs-sample, correlated draws) →
  the one-line rule "beside every price, name what it was measured ON; beside
  every draw, measure a rank" — propose its home (CLAUDE.md vs the prereg
  producer's docstring) and ROUTE it in this session;
- `[contract-gap]` cluster → the two template lines the next cycle's contracts
  inherit (fakes must model transport LIMITS, not only answers; verify-gate
  numbers are re-measured when their artifact moves);
- `[tooling]` (pipefail, worktree linker, id-hash conventions) → already fixed
  in-code; list the commits;
- `[process]` (suite shelf-life) → the redesign pattern is now precedent ×3
  (cap-in-force, derived-root snapshot, ten-keep strip) — name it once in the
  ADR so the next flip cites it instead of rediscovering it.

ADR in `knowledge/decisions/` + INDEX: the 3.19 ruling, the sitting's verdict,
and the record-vs-live decoupling pattern (its third instance makes it a named
house pattern). hot.md curated: no stale "open" items, every deferred debt with
its owner — the four that survive the phase: empty-comment queue rule (next
cycle's prep implements 3.19 (1)), leaflet collection beyond ATB (authorized),
the 11 143 under-watermark history, the leaflet reference price 10.408 s/page
for the next registration.

## Do NOT

- Spend anything; touch `data/derived/`, the sealed registration, the run
  records, cap-30 records; edit the amendment-index block or ANY kept block's
  bytes; re-pin any sealed record. Team-lead files commit-only. No
  `git add -A`.

## Report

`docs/reports/5c2-close.md`, three plain sentences first; the six-test table
with both-directions evidence; the returns record's pair; the retro with the
tag tally; Deviations **Dv325+** `[cause:]`-tagged; Process signals (≤5 lines).

**Read-back before you start:** the block whose bytes must not move even by
one newline; why the tree is red at step 0 and what greens it; who ratified
what at the sitting, in one line.
