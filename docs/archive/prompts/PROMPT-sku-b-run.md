# PROMPT-sku-b-run — the position-layer pilot, the ONE paid attempt (cap $0.35)

> Authority: SPEC §3.17 (6)–(10); prereg `results/sku_pilot_prereg_v2.json`;
> serving pin `results/sku_pilot_serving.json`; operator go 2026-08-11 (STATUS,
> «авторизация sku-b-run»). ONE paid session, cap **$0.35**, ONE attempt.
> **Named upfront: the LIKELY first outcome is a go/no-go refusal** — both
> stated projection corners sit over the cap ($0.3580/$0.3750). Per (10)(a)
> that refusal costs ~$0.08–0.10, buys the measured decode price, consumes NO
> attempt, and comes home for a v3. It is a designed outcome, not a failure.

## Read first (sections, not documents)

- `docs/SPEC.md` §3.17 (9)–(10) — the serving law and the three cap readings.
- `results/sku_pilot_serving.json` :: `expected_worker` — the identity stop.
- `scripts/runbook_vis_b.md` §A.1–A.2 — the template/endpoint pattern to
  mirror (three env variables and no fourth; POSITIONS instead of CAPTION).
- `docs/reports/sku-b-prep.md` — your own fix pass: F1–F6 semantics.

**Read-back check — FIRST lines of the report:** the eight sequence gates
below, one line each; then the two stop semantics in one line each
((10)(a) before-gold / (10)(b) mid-leg); then "one attempt — no bar, leg
or draw is ever re-run after its result".

## Sequence (ordered; each gate blocks the next)

1. **$0 gates, before anything exists.** `make check` green;
   `scripts/preflight_serving_guards.py` in the peft venv (Dv138) exit 0
   — an unrunnable preflight is a finding, never a pass; balance/guard
   re-read against `results/spend_phase4.json`; `runpodctl pod list -a`
   → `[]` and `serverless list` → `[]` (nothing bills before we start);
   driver `--dry-run` shows 108+30 sources in 7+1 jobs.
2. **Stage the volume BEFORE any endpoint exists** (a running worker
   holds the code it booted with). Update `repo/` on volume `qw4nwleanc`
   to HEAD via git bundle; `git bundle list-heads` names the real ref —
   `Already up to date.` is the signature of a no-op. End with a CONTENT
   check of what the runtime executes: `grep POSITIONS` in the volume's
   `scripts/serve_handler.py` and the presence of
   `src/market_pulse/provenance.py`. This re-stage also deploys the
   describe() fix. `start.sh` stays byte-identical to
   `scripts/start_5b_worker.sh` — verify, do not edit.
3. **NEW template, exactly three variables** (§A.1 pattern, name
   `market-pulse-sku-positions`): `SERVING_CONFIG=POSITIONS`,
   `BASE_WEIGHTS=google/gemma-4-31b-it`, `MODEL_REVISION=842da379…`
   (full sha from the pin). Never edit or reuse the srv-2d-era
   templates — `settings()` refuses their environment by design.
4. **Endpoint from that template** (§A.2 pattern): `--gpu-id ADA_24`,
   `--workers-max 1`, `--idle-timeout 60`,
   `--execution-timeout 900` — SECONDS on the flag, stored as ms;
   900 matches the driver's `JOB_TIMEOUT_S`, and no single job can
   out-bill the cap ((10)(c)).
5. **The run, exactly one invocation:**
   `PYTHONPATH=src python3 scripts/positions_gm4_skub.py
   --endpoint-id <id>` — ledgered, both legs. The driver owns the
   order: identity stop → two NON-gold warm-up calls → go/no-go →
   page leg → text leg, in-run gate between jobs. Foreground with a
   generous bash timeout — never `run_in_background` (the harness
   kills long background work; expected wall < 25 min).
6. **Outcome A — the go/no-go refuses** (`stopped_before_gold: true`,
   no dump, nothing gold bought): proceed straight to teardown (7) and
   the report. No cap raise, no retry, no second warm-up, no v3 in this
   session — the v3 registration is the TEAM LEAD's, from your measured
   warm-up numbers ((10)(a)). The attempt is intact and the record says
   so.
   **Outcome B — the run completes:** write the bar-1 and bar-3 verdict
   records THROUGH the registered readings (R1–R5: macro over the 15
   non-empty-gold posts, micro reported ungated, the 4 empty-gold posts
   as precision probe; unreadable counted by reason, >10% blocks bar 3,
   n-rules as registered). Numbers from code, no adjudication, no
   prose conclusions — on_failure/on_success rulings are the team
   lead's at acceptance. **Bar 2: the per-position dump and its n
   ONLY** — the pair verdicts are the team lead's read against the
   images (SPEC §10); you never score your own sample.
7. **Teardown, proven not asserted:** `serverless delete`, then
   `template delete`; prove by listing WITH the positive control —
   `template list --type user` must first SHOW the two live 5b-era
   siblings (`unfcr3ja0t`, `0g6zg73ptq`), then show yours absent;
   `serverless list` → `[]`; `pod list -a` → `[]`. The volume STAYS.
   Balance re-read; session spend into the record and the ledger.
8. **Step 0 / tail commits.** Team-lead docs verbatim at the start
   (`docs/PROMPT-sku-b-run.md`, `docs/STATUS.md` as handed over); the
   run's artifacts by path; vault tail → its own final commit. The
   graphify post-commit hook covers code; no manual `--update` needed.

## Recovery clause (a PAID contract carries one)

After a PROVEN deletion (listing, positive-controlled), the endpoint
and/or template MAY be re-created within this same session and cap when
a staging or config fix must land mid-session — e.g. a worker that
booted stale code is stopped only by `serverless delete`; fix the
volume, re-create, continue. The GOALS every prohibition serves:
**never two billing endpoints concurrently; never a second attempt at
any bar, leg or draw; nothing left billing after teardown.** A recovery
that respects the goals is allowed; one that re-runs a measurement to
get a different number is not.

## Do NOT

- Do not bypass the driver's own stops (identity, go/no-go, in-run
  gate, `JobExpired`) with flags, edits or a bigger
  `--project-stop-usd` — a cap is not raised to finish a run.
- Do not re-run a bar, a leg, a job or the warm-up after seeing its
  result; do not read the 159 available pages (the driver reads the
  108 — do not override `--reference`).
- Do not edit registered prompts, `results/sku_pilot_prereg*.json`,
  `results/sku_pilot_serving.json`, the frozen family, frozen sets,
  `results/baselines.json`, `results/spend_phase4.json`, or the two
  stale `max_new_tokens: 256` records (witnesses, not bugs).
- Do not edit `docs/STATUS.md`, `docs/SPEC.md`, `docs/PRODUCT.md`,
  `docs/PROMPT-*.md` — team-lead files; commit-only.
- Never `git add -A`; the volume is never deleted.

## Report — evidence, not assertions

`docs/reports/sku-b-run.md`, own commit `docs(report): sku-b-run`; chat
gets ONLY the path. Read-back lines first. Then: every listing
before/after (verbatim), the driver's console tail, every record path
with its sha, balance before/after against the ledger to the cent,
which outcome (A or B) and its artifacts, `make check` tail, Deviations
**Dv148+** (explicitly "none" if none). English. State your
assumptions.
