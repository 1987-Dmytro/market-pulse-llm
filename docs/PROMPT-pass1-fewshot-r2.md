# PROMPT — pass1-fewshot r2: the SAME line, re-registered on the environment reading of 20.08 (D0′ $0 → D1 paid, cap $1.38 → D2 $0)

**Fresh executor session. Authority:** the operator's ruling of 2026-08-21 in the
team-lead session (registered in `docs/STATUS.md`, очередь п. 3): *re-register,
the STEP budget stays $1.50 all-in* — r1's $0.1178 of pods already bought +
r2's cap $1.38 = $1.4978. Read: this file → `docs/PROMPT-pass1-fewshot.md`
(the contract; every clause not amended here stands) →
`docs/reports/pass1-fewshot.md` §D1 and Dv601–Dv606 →
`results/prereg_pass1_fewshot.json` (r1, the record r2 supersedes — r1 is
never edited). Deviations from **Dv607**, enum v2; five-line Process signals;
team-lead files verbatim; never `git add -A`.

## What r2 changes — and ONLY this (state your assumptions against it)

The question, the bars, the packs, the prompt, the holdout, the dev gate, the
attempt and its multiplicity are r1's, byte-identical — acceptance diffs those
blocks against r1. What moved is the environment reading: on 20.08 ssh on two
4090s in EU-RO-1 was still `pod not ready` at 262.5 s and 231.9 s after create
(probe-b on 18.08: 14.5 s). Four amendments, each from a named finding:

1. **Rung 2 (Dv602):** ssh dead-man ceiling 180 → **500 s from create**, else
   KILL. Derivation: the two readings are LOWER bounds of ssh-ready time (never
   observed ready) — 500 = 231.9 × 2.16, registered as a spread (14.5 s … >262.5
   s), not a measurement. One dead pod under rung 2 costs ≤ 500 × 0.80/3600 =
   **$0.1111**. Why not 600: the recovery clause must stay REACHABLE after one
   dead pod (rung 6 below) — at 600 it is not.
2. **Rung 3 (Dv605):** «launch → first reply ≤ 450 s» is anchored on the
   RUNNER LAUNCH — the runbook stamps `launched_at` (UTC) into the run
   directory the moment the runner process starts; the gate and the watch read
   that stamp, never create. Ceiling 450 unchanged (max measured load 353 s ×
   1.2748). Plus a create-anchored BACKSTOP: first reply ≤ 500 + 150 + 450 =
   **1 100 s** from create, else KILL — 150 s is the staging+launch allowance
   (probe-b: ≤ 89.5 s INCLUDING its ssh wait; ×1.68).
3. **Pins (Dv606, Dv603):** `scripts/score_pass1_fewshot.py` sha into
   `instruments.scorer_pass1_fewshot`; `BACKSTOP_TOLERANCE_SECONDS = 60.0`
   into the record, and the gate reads it FROM the record.
4. **Money re-derived for the new allowances** (H6 block, step-1 refusal):
   seconds = ssh 500 + stage/launch 150 + load 450 + generation (1 032.4 +
   1 548.6 + 495.552 = 3 076.552) + overhead 1 300 = **5 476.552 s = 1.5213 h →
   worst $1.2170 at $0.80/h** ($0.8063 at $0.53/h). **Cap $1.38**; **cumulative
   hard stop 6 100 s = $1.3556 < $1.38**; session ceiling 1.38/0.80 = 1.725 h =
   6 210 s ≥ hard stop. **Recovery reachability, asserted in the record:** one
   dead pod at rung 2 (500 s) + the full worst case = 5 976.552 ≤ 6 100 ✓ and
   $0.1111 + $1.2170 = $1.3281 ≤ $1.38 ✓ — so ONE re-creation fits by the
   registered arithmetic; after a SECOND dead pod nothing fits and the session
   closes (third pod = STOP). Overhead 1 300 s (was 1 800) because ssh and
   staging now have their own lines — no double count; name what 1 300 covers
   (scp of ≤ 464 rows, the dev gate on the Mac, delete + listing).

## D0′ — at $0, before any pod

- `scripts/write_pass1_fewshot_prereg.py` gains `--revision r2` (or a sibling
  producer — your call, say which) writing `results/prereg_pass1_fewshot_r2.json`
  with `supersedes: results/prereg_pass1_fewshot.json` + its sha, and r1's
  closing state quoted (`closed at rung 2 twice, attempt NOT spent, recovery
  used`). r1 stays byte-identical — acceptance diffs it against `c7cbfd1`.
- `scripts/gate_pass1_fewshot.py`: rung 2 ceiling, the `launched_at` anchor
  for rung 3, the create-anchored backstop, tolerance from the record; the
  watch arms rung 3 from the stamp and checks the backstop beside it. Tests in
  BOTH directions on the fake transport: 499 s no-ssh → WAIT, 501 → KILL;
  launch+451 without a reply → KILL while create-elapsed is small; create+1 101
  without a reply → KILL even with a fresh launch stamp; recovery arithmetic —
  dead pod 500 s → re-creation allowed, dead pod 624 s → refused; a run record
  without `launched_at` → the boot rung REFUSES to report GO.
- Guard step **`pass1-fewshot-r2`**, anchor at session start, `--step-cap
  1.38`; the report carries the STEP SUM line: r1 pods $0.1178 (clock) + r2.
  Run record `results/pass1_fewshot_r2_run.json`; out-files as the packs name
  them (none exist yet).
- `make check` green; `make preflight ARGS='gate_pass1_fewshot.py
  prereg_pass1_fewshot.json BACKSTOP_TOLERANCE_SECONDS'` pasted; H6 runs and
  refuses on any mismatch; commits: gate+tests · r2 record · runbook · vault
  tail separately — ALL before the first `pod create`.

## D1 / D2 — as r1 wrote them

The runbook order, the one invocation for both dev legs (Dv599), the dev gate
on the Mac, the shot into its own out-file, scp before delete, deletion by
listing with the volume as positive control, the scorer after the last append
— unchanged. The rung-2 poll is the runbook's corrected one (`"port"`, bounded
INSIDE the new ceiling: 95 × 5 s = 475 s). Attempt SPENT at the first gold-row
reply; dev RED → STOP, attempt not spent; dev gate unreachable (our_base > 39)
→ STOP, distinct from RED. Report: `docs/reports/pass1-fewshot-r2.md`,
path-only in chat; the ADR `pass1-fewshot` gains the r2 section.

## Read back FIRST, one line each

rung 2's new ceiling and why 500 not 600 · what rung 3 is anchored on and the
backstop · the worst case, the cap, the hard stop, the step sum · which blocks
must be byte-identical to r1 · when the attempt is spent · what a SECOND dead
pod means.

## DO NOT

No change to bars, packs, prompt v2, holdout, dev gate, neighbours, or the
sealed r1 record; no third pod; no generation before H6 and the commits; no
re-run of the base on the fourteen; never leave `--watch`; never two billing
endpoints; team-lead files verbatim (docs/STATUS.md, docs/SPEC.md,
docs/PROMPT-*.md).
