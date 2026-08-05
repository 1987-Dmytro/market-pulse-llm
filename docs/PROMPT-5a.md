# PROMPT-5a — Phase 5 opening: loop skeleton, poll census, channel discovery

**Contract:** `docs/SPEC.md` amendment **3.11** — read §3.11 only, not the
whole spec. This is sub-phase **5a**: $0 GPU, no serving, no aggregates.
All artifacts in English. This file is the whole brief.

**Context in three lines:** Phase 4.5 closed 2026-08-05 — 3/5 gates on
arm A, the пласт dropped by measurement. Phase 5 (production loop) opened
the same day at the team-lead briefing. 5a builds the loop's verifier
skeleton and the data-side groundwork; serving parity is 5b, aggregates
and the category layer are 5c.

## Step 0 — commit the team-lead tail

`git status --short` should show exactly: `docs/STATUS.md` (compacted by
the team lead to ~190 lines), `docs/SPEC.md` (amendment 3.11),
`docs/PROMPT-5a.md` (this file, untracked), `knowledge/daily_logs/2026-08-05.md`,
`knowledge/index.md`. Stage BY PATH (never `git add -A`), one commit:
`docs: Phase 5 opened — SPEC 3.11, STATUS compacted to the map, PROMPT-5a`.
Anything unexpected in the status → STOP and report.

## Deliverable 1 — channel discovery with a coverage ledger ($0, API-only)

Authorised 2026-08-04; coverage target recorded 2026-08-05 (SPEC 3.11 (4)).

- Build `scripts/discover_channels.py` (new; follow the shape of the
  existing `data/discovery_*.json` artifacts — 27.07 examples on disk),
  using `marketpulse.session`. Search UA channels for three themes:
  mothers/kids, healthy lifestyle (ЗОЖ), baby food.
- Per candidate: title, @handle, subscriber count, linked discussion
  group (yes/no), posts/week over the last 4 weeks, rough language mix,
  last-post date.
- Coverage ledger in `results/discovery_5a.json`: per-candidate rows +
  the summed subscribers of the CURRENT five registry channels + the
  cumulative candidate sum + the gap to the **10,000,000** target. Print
  both caveats verbatim in the record: "summed subscribers != unique
  reach" and "subscribers != comment flow".
- Candidates only: do NOT touch `config/registry.yaml` — entry is the
  operator's choice through the track-R gate.

## Deliverable 2 — poll census + poll text beside raw v1 ($0, no API)

The poll payload already sits in the stored raw messages (4.5g2 took its
transcripts from them; the collector just never surfaced it as text).

- Surface it as a derived column/file BESIDE the raw v1 stores — same
  pattern as reply_to in 4.5g5; raw v1 bytes untouched.
- Census storewide → `results/poll_census_5a.json`: of all posts stored
  with empty text — how many are polls, per channel and total (the
  4.5g2 sample said 16/41). Count giveaways / video / voice separately
  (reported only; no third surrogate is built in 5a).

## Deliverable 3 — loop skeleton (verifier before features)

- `src/market_pulse/loop.py`: cursor state (follow the
  `data/backfill_cursor.json` pattern), idempotent ingest (a re-run adds
  no dupes — proven by a test), `--dry-run` that prints what WOULD be
  fetched and what WOULD go to inference, and an inert spend-guard hook
  point (no GPU exists in 5a).
- `scripts/run_loop.py --once --dry-run`; NO serverless or GPU calls
  anywhere in 5a.
- Smoke: one dry-run pass over one channel → `results/smoke/loop_5a.json`.
- Tests: cursor advance/rollback, idempotency, dry-run purity (no
  network writes).

## Verification — evidence, not assertions

`make check` green (show the tail). Quote the key numbers from all three
result files with their paths. `git log --oneline` for your commits;
`git status` clean at the end. State your assumptions explicitly.

## Budget

OpenRouter $0 expected — if any model call seems needed, STOP and report
instead. GPU $0. Telegram API is free; respect the collector's existing
backoff.

## DO NOT

- edit `docs/STATUS.md`, `docs/SPEC.md`, `docs/PROMPT-*.md` — team-lead
  files (File ownership); committing them in Step 0 is the task, editing
  them is forbidden;
- touch `data/frozen/*`, raw v1 stores (derived columns beside only),
  `results/baselines.json`, scorer defaults, `config/qlora.yaml`,
  `prompts.TASKS`;
- add channels to `config/registry.yaml`;
- widen discovery beyond the three authorised themes — a wider round is
  an operator decision taken on the ledger's gap.

## Report

`implementation-notes.md` with a **Deviations** section — silence is not
compliance. Autonomy: mechanics high (counters, pipelines — mechanically
verifiable); at any design fork take the smallest thing that passes the
tests and note the alternative in the report rather than building it.
