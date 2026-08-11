# PROMPT-sku-b-v3-run — the resumed session: buy the 121, complete the pilot (cap $0.45)

> Authority: SPEC §3.17 (11); prereg `results/sku_pilot_prereg_v3.json`
> (registered, committed); serving pin unchanged; operator go 2026-08-11
> («завершить замер»). ONE resumed session, cap **$0.45**, buying EXACTLY
> the 121 unbought elements. Every reading of (10) applies against this
> cap; the go/no-go now probes from REPRESENTATIVE warm-ups ((11)(c)),
> so a refusal — unlikely at break-even 1.63× — would be real prices
> talking, and comes home with the attempt intact.

## Read first (sections, not documents)

- `results/sku_pilot_prereg_v3.json` :: `resume` — the population, the
  registered warm-up inputs, the pins the driver refuses on.
- `docs/reports/sku-b-run.md` §Gate 2 and §Gates 3–4 — the staging and
  template/endpoint pattern that worked; repeat it, do not reinvent it.
- `docs/reports/sku-b-v3-prep.md` §D2 — your own resume mode.

**Read-back check — FIRST lines of the report:** the eight gates one
line each; the two (10) stop semantics one line each; then "each
element bought exactly once across the program — nothing is re-asked".

## Sequence (ordered; each gate blocks the next)

1. **$0 gates.** `make check` green; the preflight in the peft venv
   exit 0 (rebuild it if the scratch is gone — Dv160 pattern); balance
   re-read against `results/spend_phase4.json`; `pod list -a` → `[]`,
   `serverless list` → `[]`; driver `--resume --dry-run` shows 91+30 in
   6+1 jobs and the four refusal guards green in the suite. **Anchor
   BEFORE anything bills** (the Dv149 protocol, now standard): write
   `results/spend_sku_b_v3.json` via the driver's own `read_ledger`.
2. **Stage the volume BEFORE any endpoint exists.** `repo/` on
   `qw4nwleanc` to HEAD by git bundle; content check names the terrain
   (`git rev-parse HEAD` on the volume = the Mac's sha; `start.sh`
   byte-identical to `scripts/start_5b_worker.sh`). **On the same
   staging pod, READ `worker-boot.log`** — the 391 s boot (2.13× the
   vis-c 183.58 s) gets its diagnosis here for near-free: where the
   time went (weights? venv? container?), verbatim tail into the
   report. Pod deleted, proven by `pod list -a`.
3. **NEW template, three variables, no fourth** (the sku-b-run §A.1
   repeat): `SERVING_CONFIG=POSITIONS`, `BASE_WEIGHTS`, the full
   `MODEL_REVISION`. Never reuse or edit an old template.
4. **Endpoint:** `--gpu-id ADA_24 --workers-max 1 --idle-timeout 60
   --execution-timeout 900`; flags read back from the API answer into
   the report.
5. **The run, one invocation:** `PYTHONPATH=src python3
   scripts/positions_gm4_skub.py --resume --endpoint-id <id>`.
   Expected wall ~15–20 min (boot ~390 s + 121 calls) — **launch
   detached (`nohup` + PID watch), pre-authorised:** the harness caps a
   foreground call at 600 s, so the Dv148 pattern is the rule here, not
   a deviation. Watch the PID (`pgrep -f "[p]ositions_gm4_skub"`),
   never `tail -f` alone. The driver owns the order: identity stop →
   the two REGISTERED warm-ups (page 4476 + row @silposilpo:3370) →
   go/no-go against $0.45-minus-billed → page leg (6 jobs) → text leg
   (1 job), in-run gate between jobs.
6. **Outcomes.**
   **Go/no-go refusal** (real-probe prices exceed the cap): teardown,
   report, STOP — attempt intact, the re-registration decision is the
   team lead's. **(10)(b) mid-leg stop:** teardown, report, STOP — a
   team-lead ruling, never a silent continuation. **Completion:** write
   the merged artifacts (`results/sku_b_positions_v3.{json,jsonl}`,
   `bought_by` on every row); compute the bar-1 and bar-3 verdict
   records THROUGH the registered readings (R1–R5) over the MERGED
   population — numbers from code, no adjudication, no prose
   conclusions; **bar 2 = the merged dump and its n ONLY** (the pair
   verdicts are the team lead's read at acceptance, SPEC §10). The 17
   first-session answers enter as they stand — the parse refusal
   included, never re-asked.
7. **Teardown, proven:** `serverless delete`, `template delete`;
   `template list --type user` shows the two 5b-era siblings live and
   yours absent; `serverless list` → `[]`; `pod list -a` → `[]`; the
   volume STAYS. Balance re-read into the record and the ledger
   (`spend_or_note` — a dead read must not lose the record).
8. **Commits.** Step 0 first: team-lead docs verbatim
   (`docs/PROMPT-sku-b-v3-run.md`, `docs/STATUS.md`); then the run's
   artifacts by path; vault tail → its own final commit (the ADR of
   this session's decisions is written at ACCEPTANCE, on team-lead
   instruction — not pre-emptively).

## Recovery clause

After a PROVEN deletion (listing, positive-controlled), the endpoint
and/or template MAY be re-created within this session and cap when a
staging or config fix must land mid-session. GOALS every prohibition
serves: **never two billing endpoints concurrently; nothing re-asked —
no element that carries an answer is ever bought again; nothing left
billing after teardown.** A recovery that respects the goals is
allowed; one that re-runs a measurement to get a different number is
not.

## Do NOT

- Do not bypass the driver's stops (identity, four resume refusals,
  go/no-go, in-run gate, `JobExpired`) with flags or edits; a cap is
  not raised to finish a run.
- Do not re-ask ANY element that carries an answer — including the 17
  and the parse-refused page; do not re-pick the warm-up inputs (they
  are registered; the driver reads them).
- Do not edit registered prompts, the parser, any
  `results/sku_pilot_*` registration, the sealed
  `results/sku_b_positions.{json,jsonl}` pair, the frozen family,
  `baselines.json`, `spend_phase4.json`, the two stale 256 records.
- Do not edit `docs/STATUS.md`, `docs/SPEC.md`, `docs/PRODUCT.md`,
  `docs/PROMPT-*.md` — team-lead files; commit-only.
- Never `git add -A`; the volume is never deleted.

## Report — evidence, not assertions

`docs/reports/sku-b-v3-run.md`, own commit `docs(report): sku-b-v3-run`;
chat gets ONLY the path. Read-back lines first. Then: every listing
before/after verbatim; the boot-log diagnosis (§2); the driver console
tail with both warm-up timings and the go/no-go arithmetic; which
outcome and its artifacts with shas; the three cost readings kept
distinct (balance-delta floor / billed-seconds / anchor re-read);
`make check` tail; **the per-commit checkout table is back this
phase** (stash first, print HEAD + a content fact per row); Deviations
**Dv161+**, explicitly "none" if none. English. State your assumptions.
