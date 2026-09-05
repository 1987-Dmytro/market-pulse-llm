# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## The money, live — read BY HAND from the guard today, never carried from a record
Cycle 3 **SPENT $5.5254, REMAINING $3.4746** of the **$9.00** ceiling of ruling (s) addendum 8; anchor
$14.4800 and every session line UNMOVED, balance $8.95. The CYCLE line is not what refused — the
**STEP** line did: `promo-dev-loop` stands at **$1.8462** against the $1.20 the registration names.
**s26 spent $0, created no pod and took NO ledger line** — no `--note` run, because nothing exists to
anchor. `promo-holdout` $0.296617, ledger OPEN; `promo-dev-loop` OPEN by (r)4, anchored 03.09 at $10.80.

## Done — 05.09 s26: the start ritual, then ONE item — the money gate BEFORE the create. $0, no pod.
- **The two modified team-lead files committed by path, unread and unedited (`c4d6c1c`)**: STATUS at
  14:20 and the (u) addendum 5. The hooks' s25 checkpoint (`knowledge/**` + this file) went in as
  `1bb5f2c`. Tree clean before any paid step; `pod list -a` and `serverless list` both `[]`.
- **The gate the runbook takes BEFORE the create REFUSES, and it is not a near miss:**
  `python3.11 scripts/runpod_guard.py --step promo-dev-loop --step-cap 1.20` → **exit 1**, «REFUSED:
  promo-dev-loop's $1.20 cap is reached ($1.8462 spent)». `results/spend_promo_dev_loop.json` is
  anchored **2026-09-03T20:17:16Z at $10.8008** and carries iterations 1–3, so the operator's per-LEG
  $1.20 was written into a STEP line that already stands above it.
- **The old number does not fund it either.** At the ledger's own `promo-dev-loop_gpu_cap_usd` **$2.50**
  the guard exits 0 and leaves **$0.6538** — under iteration 4's registered MEAN corner **$0.8705**,
  let alone its $1.20 hard stop. Neither number the operator has named buys this run.
- **What the enforced figure is made of** (the guard's own decomposition): balance delta **$1.8462** =
  pods **$1.4573** + network-volume **$0.3792** + serverless $0.0000; «step resources» $1.4573. The
  volume drip is INSIDE the enforced figure, so this OPEN line grows ≈$0.24/day with no pod running —
  a number named on it erodes by itself ([[a_step_meter_on_a_balance_delta_never_stops]]).
- **Why the registration reads FITS anyway — a CAUSE, named and NOT fixed:** `guard_reading()`
  (`scripts/promo_dev_pass.py:515`) runs the guard with **no `--step`**, so `--register`'s `cap_rule`
  min($1.20, REMAINING) read CYCLE 3's $3.4843 and never the step's own $1.8462-of-$1.20 — which is
  why `step.money` in the record holds the cycle line alone. Passing `--step` there decides the stop.

## Next — the PAID iteration 4 ((u)4), unchanged, and BLOCKED by the stop below and by nothing else.
`--terminate-after` from `step.cap_usd` $1.20 → 5838 s; the registered 90-min backstop 5400 s bites FIRST.
The sequence is ruling (u) item 4's, verbatim and unmoved: create → `--open` → smoke (3) → GO on the three
replies → the 80 → delete → `--close-segment --replies …iter4.jsonl` → `--score --arm dev40` (the BAR
0.80/0.75) and `--arm dev2` (the READING), each with its own `--gold` and K8 → END at the readings.

## Open stop — the STEP ledger refuses iteration 4 at BOTH numbers, and the line is not mine to choose
**Stop-point.** PHASE §6.1's money gate, taken before the create as the runbook's §0 orders, refuses:
`--step promo-dev-loop --step-cap 1.20` → exit 1, $1.8462 spent of $1.20. At $2.50 it passes and leaves
$0.6538, under the registered mean $0.8705. `promo-dev-loop` is ONE OPEN line whose anchor (03.09,
$10.80) is iteration 1's, so iterations 1–3 sit inside every number named on it.
**Question.** Under what LINE is iteration 4 bought? (a) a NEW step with its own name, anchor and ledger
at the operator's $1.20 — the `promo-holdout` precedent, where a new authorisation opened a new budget
line instead of a bigger number in an old one; or (b) a number named on the open `promo-dev-loop` line
covering iterations 1–3 plus this run — $1.8462 + the cap, eroding at the volume's ≈$0.24/day for as
long as the line stays open. Both move a registered threshold, so neither is mine: I have created no
ledger, invented no step name and re-registered nothing.
**Tree.** Clean at HEAD; two commits this session, both $0. No pod was created and no ledger line taken;
`runpodctl pod list -a` and `serverless list` both `[]` in the transcript; no red test.

## Named, not built (the phase file forbids adding what it did not ask for)
- **No test for the arm selector** (s24's precedent, §4): the one worth asking for pins «one arm → one
  gold, one unit set, one stratum map», with the WRONG part's empty stratum map as its negative control.
- **`scripts/runbook_promo_dev_1.md` is the HOLDOUT's**, and says «the dev loop is CLOSED» — stale since (s).
- **The pack's order is not strictly dev-40-then-dev-2** ((u)3): dev-40 completes at unit 42 of 80.
- **dev-2's units ARE holdout-40's**: the out-file handed to `--close-segment` is unchecked against the
  pod; the run's out-file is `results/promo_dev40_iter4.jsonl` and nothing else ((u)3).
- `decision_table.after_the_smoke_for_40_threads` keeps its key because `project()` reads it by name ·
  `gates.terminate_after_minutes` is v5b's borrowed 5400 s · `prep()` calls its count `draw.dev_threads` ·
  `pod.main` never lifts `close_arrays_too` · ⛔ `1925810730`.
