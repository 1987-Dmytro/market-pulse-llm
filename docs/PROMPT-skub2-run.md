# PROMPT-skub2-run — instrument v2 over all 138: the B′ measurement (cap $0.65)

> Authority: SPEC §3.17 (13)–(14); prereg `results/sku_pilot_prereg_b2.json`;
> serving pin v2 (ceiling 1200); operator go 2026-08-12. ONE session, a FULL
> run (no `--resume` — B1: every element re-asked; v1's answers stay sealed).
> The go/no-go will project ~$0.61 from the registered deep-page probe against
> $0.65 and proceed; the in-run gate protects the middle; measured expectation
> ~$0.25–0.35. Every reading of (9)–(12) is in force.

## Read first (sections, not documents)

- `results/sku_pilot_prereg_b2.json` :: `attempts`, `bars.leaflet_brand_recall.gold`
  — the cap and the 37-pair/10-post gold.
- `docs/reports/sku-b-v4-run.md` §Gates 2–4 and 7 — the staging, template,
  endpoint and teardown pattern that worked twice; repeat it.
- `docs/reports/skub2-prep.md` §Fix — your own constants and guards.

**Read-back — FIRST lines of the report:** the eight gates one line each;
the two (10) stop semantics; "a FULL run — nothing resumed, nothing re-used
from v1's answers"; and the bar-1 gold source in one line (Dv210 wiring).

## Sequence (ordered; each gate blocks the next)

0.5 **The Dv210 wiring, before anything paid:** `sku_bar_verdicts.bar_one`
   reads its gold from the B′ registration's own `gold.per_post` (the
   existing refusal currently stops it — this step is what removes the
   stop); the excluded-posts check compares against B′'s NINE, not the
   sealed reference's four. Tests both ways; own commit; suite green.
1. **$0 gates.** `make check`; preflight in the peft venv exit 0 (rebuild
   if the scratch is gone); balance re-read vs `spend_phase4.json`;
   `pod list -a` → `[]`, `serverless list` → `[]`; driver `--dry-run`
   (NO --resume) shows 138 sources — 108 pages in 7 jobs + 30 rows in 1;
   the constants check fires on the non-resume path (your own new test
   proves the wiring). **Anchor `results/spend_skub2.json` BEFORE anything
   bills** (the Dv149 protocol), committed.
2. **Stage the volume BEFORE any endpoint exists** — REQUIRED this time:
   instrument v2 lives in `src/market_pulse/` (parser, ceiling constant)
   and the worker executes the volume's copy. Bundle → explicit-sha reset
   → CONTENT check: `git rev-parse HEAD` on volume = Mac's sha; grep the
   1200 ceiling constant and one parser-warning string in the volume's
   tree; `start.sh` byte-identical; prompt shas re-rendered = the pin.
   Pod deleted, proven, priced by its own clock against the day's rates
   (the Dv177 check).
3. **NEW template, three variables, no fourth**; never a reused one.
4. **Endpoint:** `ADA_24 · workers-max 1 · idle 60 · execution-timeout
   900`; flags read back from the API answer.
5. **The run, one invocation, detached (`nohup` + PID watch,
   pre-authorised):** `PYTHONPATH=src python3
   scripts/positions_gm4_skub.py --endpoint-id <id>` — identity stop
   (serving pin v2: the worker must say 1200) → the two REGISTERED
   warm-ups → go/no-go vs $0.65-minus-billed → page leg → text leg,
   in-run gate between jobs.
6. **Outcomes.** Completion (expected): merged skub2 artifacts
   (`results/sku_b_positions_skub2.{json,jsonl}`); bar-1 and bar-3
   verdicts through the producer over B′'s gold — numbers from code, no
   prose conclusions; **bar 2 = the dump and its n ONLY** (the pair read
   is the team lead's at acceptance, SPEC §10); parser WARNINGS
   (footnote/multipack/from) counted per page in the record — they are
   v2's fingerprint. A (10)(a) refusal or (10)(b) stop: teardown,
   report, STOP — team-lead ruling.
7. **Teardown, proven** with the positive control (the two 5b-era
   siblings show, yours absent); volume STAYS; balance re-read through
   `spend_or_note`; ledger entry via `log_run` whichever exit runs.
8. **Commits:** team-lead docs verbatim first; the run's artifacts by
   path; the report; vault tail its own commit (the Dv175 reading).

## Recovery clause

After a PROVEN deletion, the endpoint/template MAY be re-created within
this session and cap for a staging/config fix. GOALS: never two billing
endpoints concurrently; nothing left billing after teardown; no bar, leg
or draw re-run after its result.

## Do NOT

- Do not pass `--resume`; do not touch v1's sealed pair or any v1–v4
  registration; do not re-pick the warm-ups; do not edit prompts, the
  parser, the pins mid-session — a cap is not raised and an instrument
  is not edited to finish a run.
- Team-lead files commit-only; frozen family, `baselines.json`,
  `spend_phase4.json`, the stale-256 records untouched; never
  `git add -A`; the volume is never deleted.

## Report — evidence, not assertions

`docs/reports/skub2-run.md`, own commit; chat gets ONLY the path.
Read-back first; listings before/after verbatim; the boot, both warm-up
timings and the go/no-go arithmetic; per-leg marginals; warning counts;
which outcome and its artifacts with shas; the three cost readings kept
distinct; `make check` tail; the per-commit checkout table; Deviations
**Dv225+**, explicitly "none" if none. English. State your assumptions.
