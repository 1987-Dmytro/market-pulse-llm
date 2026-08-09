# PROMPT-5c1-vis-b — the paid caption session on the endpoint (cap $1.00)

> Authority: operator go 2026-08-09; SPEC §3.13 (4) gates + §3.15 runtime
> (serverless-endpoint session; the "one pod session" wording of 3.13 is
> superseded by 3.15 (1)). The normative procedure is
> `scripts/runbook_vis_b.md` — accepted at vis-a-r; execute it end to end.
> ONE paid attempt per rung, no retries past the abort ladder.

## Read first

- `scripts/runbook_vis_b.md` — whole (it IS the procedure).
- `docs/SPEC.md` §3.13 (4) and §3.15 only.
- `knowledge/hot.md` footguns: a failing worker bills like a working one —
  watch the FIRST job's status and delete the endpoint on the first worker
  restart; Dv33 — balance delta and ledger are both FLOORS; `smoke_5b.py
  --record` defaults to the pod cost anchor — always pass a path; the
  request policy is milliseconds — `serving.execution_policy` is the only
  conversion point.

**Read-back check — FIRST lines of your report, before creating anything
billable:** list the §A/§B/§C gates and ALL stop rules (cap $1.00 hard;
§C.1 >$0.50 projection STOP; instrument-failure rule — bar-A fail while
qwen-PASS stands = STOP to the operator with the bridge table; worker
restart = delete endpoint), one line each.

## Step 0 (commits pre-authorised)

1. Team-lead docs, content unedited, commit only: `docs/SPEC.md` (3.15),
   `docs/STATUS.md`, `docs/PROMPT-5c1-vis-b.md`.
2. Vault tail: `knowledge/hot.md`, `knowledge/index.md`,
   `knowledge/daily_logs/2026-08-09.md`.
3. Spend anchor `results/spend_5c1_vis.json` — written and committed
   BEFORE the first billable action (the runbook's own first step).

## Execution

- Follow the runbook: §A template + endpoint (env per §A.1; policy via
  `serving.execution_policy` only) → §B one-post smoke, dump read back
  byte-for-byte, `--record` to a NEW path → §C.1 measured rate + $-projection
  gate → re-pilot of the 19 ATB posts (8 jobs per the 10 MB transport
  ceiling, SPEC 3.15 (2)) → GM4-vs-qwen bridge on identical posts
  (`results/captions_5c1.json` is the bought qwen side) → screen-pilot
  check against the untouched prereg (verify
  `results/yield_bars_5c1.preregistration.json` by shasum BEFORE use).
- Every caption record carries `caption_source: "gm4-nf4-base"`.
- Spend readings at every rung: balance delta AND itemised ledger, both
  reported as floors (Dv33). STOP over $1.00; a partial session reports
  what it bought.

## Cleanup — regardless of outcome

Template AND endpoint deleted at session end; deletion proven by listings
(`runpodctl serverless list`, `runpodctl pod list -a`) pasted into the
report. The volume `qw4nwleanc` stays.

## Do NOT

- Do not edit `docs/STATUS.md`, `docs/SPEC.md`, `docs/PROMPT-*.md` —
  team-lead files (File ownership); commit-only.
- No second endpoint; no retry of a failed rung; no `--record` defaults.
- `data/frozen/**`, `results/baselines.json`, `results/verdict_*.json`,
  `results/parity_*.json`, `results/serving_5b.json`, the adapter — untouched.
- Never `git add -A`; stage by path; vault tail of this session → its own
  final commit.

## Report — evidence, not assertions

Per §-gate: the command and what it returned; dump paths on the volume;
the bridge table; the screen-pilot verdict with prereg sha echoed; both
spend floors and the closing balance; `implementation-notes.md` Deviations
section (silence is not compliance). Report in English.

---

## RESUME addendum — 2026-08-09, operator go after the boot-rung stop

> The stop was correct: a guard defect (fixed in `d408034`) plus a worker
> that held the old module left no lever except a new endpoint, and the
> original DO-NOT banned it by letter. This addendum amends exactly that
> line and nothing else. Deviations continue from Dv61.

1. **Recovery clause — amends "No second endpoint".** The rule's GOAL is
   "never two BILLING endpoints concurrently". ONE replacement endpoint may
   be created after the previous endpoint's deletion is proven; this
   addendum authorises exactly one such replacement for this resume.
2. **Step R0 — $0, on the Mac, BEFORE anything billable:** exercise the
   fixed guard against the REAL transformers PeftAdapterMixin, both
   directions — it ACCEPTS a bare real model and REFUSES an adapter-carrying
   one. The mixin is what is under test, so a tiny config-built real model
   is a valid subject; a stub is NOT. If the Mac venv cannot express the
   check honestly, STOP and say so. Paste the command and its output.
3. **Step R1:** template re-created (free), the replacement endpoint, then
   the runbook from §B unchanged. Every stop stands: cap remainder
   **$0.8419** on the SAME anchor (`results/spend_5c1_vis.json` continues,
   never re-anchored); §C.1 >$0.50 projection STOP; instrument-failure
   STOP; worker restart = delete.
4. **Boot proof before the first job:** the boot log must name the repo
   commit the RUNNING worker imported (`d408034`) — a fix staged on the
   volume is not deployed until the running process names it.
5. **Deletion proofs use positive-controlled listings** (this session's
   template-list finding): first show the listing CAN display a known-live
   object of that kind (or use the API that names it), then show it gone.
6. **§C.1 arithmetic:** the pre-registered cold-start constant $0.0733
   stays in the formula (a pre-registration is a file, not a preference);
   the cheaper measured start is reported BESIDE it, never swapped in.
