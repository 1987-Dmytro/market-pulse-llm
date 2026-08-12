# PROMPT-sku-b-v4-run — the completing session: buy the 121, close the pilot (cap $0.65)

> Authority: SPEC §3.17 (12); prereg `results/sku_pilot_prereg_v4.json`
> (committed, sealed chain v1←v2←v3←v4); operator go 2026-08-11
> ($0.65, fresh ledger). ONE session, the SAME 121 elements, the SAME
> frozen instrument and registered warm-ups. The gate's own pessimistic
> projection (~$0.60–0.61 with drift) FITS this cap, so the expected
> outcome is COMPLETION; a (10)(b) mid-leg stop remains a team-lead
> ruling, never a silent continuation.

## Read first (sections, not documents)

- `results/sku_pilot_prereg_v4.json` :: `attempts`, `resume` — the cap,
  the ledger, the pins.
- `docs/reports/sku-b-v3-run.md` §Gates 2–4 — the staging and
  template/endpoint pattern that worked twice; repeat it.
- `docs/reports/sku-b-v4-prep.md` §Dv170 — the three v3-references in
  the bar producer; this contract pays that debt (step 0.5).

**Read-back check — FIRST lines of the report:** the eight gates one
line each; the two (10) stop semantics; "each element bought exactly
once — nothing re-asked"; and the Dv170 fix in one line.

## Sequence (ordered; each gate blocks the next)

0.5 **Dv170 debt, before anything paid:** `scripts/sku_bar_verdicts.py`
   defaults move to the v4 record/prereg, and the provenance string it
   writes names THIS contract and amendments (6), (11), (12); a test
   pins the string. Own commit, suite green.
1. **$0 gates.** `make check`; the preflight in the peft venv exit 0
   (rebuild the scratch venv if gone — the Dv160/Dv173 pattern; note
   the recurring tax in the report); balance re-read vs
   `results/spend_phase4.json`; `pod list -a` → `[]`,
   `serverless list` → `[]`; `--resume --dry-run` shows 91+30 in 6+1
   under the v4 registration ($0.65 · sku-b-v4). **Anchor
   `results/spend_sku_b_v4.json` BEFORE anything bills**, via the
   driver's own `read_ledger`, committed.
2. **Stage the volume BEFORE any endpoint exists:** `repo/` on
   `qw4nwleanc` to HEAD by git bundle (real ref, explicit-sha reset,
   CONTENT check; `start.sh` byte-identical, prompt shas re-rendered on
   the volume = the serving pin). No boot-log work this time — the
   diagnosis is done. Pod deleted, proven.
3. **NEW template, three variables, no fourth** (the twice-proven §A.1
   pattern). 4. **Endpoint:** `ADA_24`, one worker, idle 60,
   execution-timeout 900; flags read back from the API answer.
5. **The run, one invocation, detached (`nohup` + PID watch,
   pre-authorised):** `PYTHONPATH=src python3
   scripts/positions_gm4_skub.py --resume --endpoint-id <id>`.
   Expected wall ~20–30 min at the pessimistic marginal. The driver
   owns the order: identity stop → the two REGISTERED warm-ups →
   go/no-go vs $0.65-minus-billed → page leg (6 jobs) → text leg
   (1 job), in-run gate between jobs.
6. **Outcomes.** **Completion (expected):** merged artifacts
   `results/sku_b_positions_v4.{json,jsonl}` (`bought_by` per row, the
   17 first-session answers as they stand); bar-1 and bar-3 verdict
   records through the FIXED producer (step 0.5) over the merged
   population — numbers from code, no adjudication, no prose verdicts;
   **bar 2 = the merged dump and its n ONLY** (team-lead read at
   acceptance, SPEC §10). **Go/no-go refusal** (would need the probe
   ~1.08× worse than its own registered price): teardown, report,
   STOP — attempt intact, back to the team lead. **(10)(b) mid-leg
   stop:** teardown, report, STOP — team-lead ruling.
7. **Teardown, proven:** endpoint then template deleted;
   `template list --type user` shows the two 5b-era siblings live and
   yours absent; `serverless list` → `[]`; `pod list -a` → `[]`; the
   volume STAYS. Balance re-read through `spend_or_note`; the ledger
   entry via `log_run` whichever exit runs.
8. **Commits.** Team-lead docs verbatim first (`docs/PROMPT-sku-b-v4-run.md`,
   `docs/STATUS.md`); the run's artifacts by path; the report; vault
   tail its own commit (final unless the checkout table's own tail
   needs one more — the Dv175 reading stands).

## Recovery clause

After a PROVEN deletion (listing, positive-controlled), the endpoint
and/or template MAY be re-created within this session and cap when a
staging or config fix must land mid-session. GOALS: **never two billing
endpoints concurrently; nothing re-asked — no element carrying an
answer is ever bought again; nothing left billing after teardown.**

## Do NOT

- Do not bypass the driver's stops (identity, the four resume refusals,
  the constants check, go/no-go, in-run gate, `JobExpired`); a cap is
  not raised to finish a run.
- Do not re-ask ANY element carrying an answer (the 17 included); do
  not re-pick the warm-ups; do not touch the sealed
  `results/sku_b_positions*.{json,jsonl}` pairs of the two previous
  sessions beyond reading.
- Do not edit registered prompts, the parser, the serving pin, any
  `results/sku_pilot_*` registration, frozen family, `baselines.json`,
  `spend_phase4.json`, the two stale 256 records.
- Team-lead files commit-only; never `git add -A`; the volume is never
  deleted.

## Report — evidence, not assertions

`docs/reports/sku-b-v4-run.md`, own commit; chat gets ONLY the path.
Read-back lines first; every listing before/after verbatim; the driver
console tail with warm-up timings and the go/no-go arithmetic; the
three cost readings kept distinct; which outcome and its artifacts with
shas; if completed — the bar-1/bar-3 verdict record paths and bar 2's n,
WITHOUT any bar-2 value; `make check` tail; the per-commit checkout
table; Deviations **Dv176+**, explicitly "none" if none. English. State
your assumptions.
