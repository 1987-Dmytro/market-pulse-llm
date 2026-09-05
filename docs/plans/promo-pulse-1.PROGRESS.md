# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## The money, live — read BY HAND from the guard today, never carried from a record
Cycle 3 **SPENT $5.5157, REMAINING $3.4843** of the **$9.00** ceiling of ruling (s) addendum 8; anchor
$14.4800 and every session line UNMOVED, balance $8.96 (the $0.0098 since s24 is the volume's drip).
**s25 spent $0 and created no pod — no ledger line.** Iteration 4 is
REGISTERED at cap **$1.20** and re-prices on the day to **$0.8705**, so the line after it — holdout-2
≤$0.90 + c3 ≤$0.50 + the drip — still fits. `promo-holdout` $0.296617, ledger OPEN; `promo-dev-loop`
open by (r)4.

## Done — 05.09 s25, (u) item 2, ONE item, two commits, $0 — ACCEPTED by the (u) addendum 14:20.
- **The arm is a parameter, and the reading's key is PINNED (`705e2d1`).** The debt this file named
  is paid BEFORE the pod. `--score` read ONE gold over the WHOLE leg: dev-40's 140-row key against
  80 answered units, dev-2's own 188-row key never opened. Now `DEV_ARMS` names the leg's two arms
  by LABEL (`dev40`, `dev2`), each carrying its part of the FIRST draw, its file stem and its own
  key, and `DEV_FILES["arms"]` is DERIVED from it so one population is never listed twice. The label
  space and the draw's part space collide on the word «holdout» — dev-2 IS the spent holdout-40 — so
  `use_arm` REFUSES any arm outside `--part dev`, and it binds the SCORER alone: binding the gold on
  a `--register` run would pin a reading arm's key as the leg's BAR key. `score()` grades ONE arm —
  its own units of the pack, its own gold, `strata_of` on its own part — and the record now names
  the arm and the key it read. `--score` with no `--arm` REFUSES on a leg of two arms; the holdout
  leg is one arm and its runbook line is untouched. `leg_golds()` is the ONE list the registration
  pins: `pinned_inputs` gains `docs/labels-promo-dev2.jsonl 4b60ab99…`; `gold.covers` names both arms.
- **Driven at $0 on replies that already exist** (`--suffix _armdrive`, outputs deleted), and it
  proves the PLUMBING and no performance — both reply files predate codebook v1.2: `--arm dev40` on
  `promo_dev40_iter3.jsonl` → **40 of 40** units, gold 140 rows, subject **0.8714** / signal
  **0.9104**, iteration 3's own numbers re-derived; `--arm dev2` on `promo_holdout40.jsonl` → **40 of
  40**, gold 188 rows, subject **0.7394** / signal **0.7833**, per-stratum 20+20 threads — NOT a
  dev-2 reading under v1.2, only the old replies against the RE-READ key (0.7181/0.7958 was the old
  key; a corrected gold moves the denominator). The arms' thread sets are DISJOINT.
- **Rung 0 re-priced on the day and UNMOVED:** cheap $0.8705 yes · priced $0.9279 yes · dear $4.9984
  NO → FITS on the MEAN corner against the $1.2000 cap, hard stop 5838 s.
- **The pack (`0bb62fb`):** only `registration.sha256` moves, 037267dc… → 9ded3a79…; the 80 units are byte-identical.
- **`make check` GREEN.** ruff clean · pytest in four slices 656 + 1092 + 2152 + 421 = **4321 passed,
  0 failed, 2 skipped** (floor 4266) — unchanged from s24, and no test was added or deleted.

## Next — the PAID iteration 4, and the (u) addendum item 5 puts it in the NEXT session, (u)4 unchanged.
`--terminate-after` from `results/prereg_promo_dev_loop.json :: step.cap_usd` $1.20 → 5838 s; the registered backstop is 90 min =
5400 s and bites FIRST, with room for ≈107 threads at the mean rate. Sequence ((u)4): pre-create check → create → `--open` →
smoke (3) → **GO on the three replies, no band gate** → the 80 → delete → `--close-segment --replies
results/promo_dev40_iter4.jsonl` → listings `[]` → `--score --arm dev40 --gold docs/labels-promo-dev.jsonl` (the BAR, 0.80/0.75)
and K8 → `grade_promo_dev40_iter4.json` · `--score --arm dev2 --gold docs/labels-promo-dev2.jsonl` (the READING) and K8 →
`grade_promo_dev2_iter4.json` → END at the readings. Then holdout-2's gold (team lead) and its ≤$0.90 shot.

## Open stop — NONE. The tree is clean, three commits this session, $0 spent, no pod, no red test.

## Named, not built (the phase file forbids adding what it did not ask for)
- **No test was added for the arm selector** — s24's precedent and §4: both refusals were driven in
  the transcript instead (no `--arm` on a two-arm leg; `--arm dev2` under `--part holdout`). The test
  worth asking for pins «one arm → one gold, one unit set, one stratum map», with the empty stratum
  map of the WRONG part as its negative control.
- **The pack's order is not strictly dev-40-then-dev-2** (accepted by (u)3): the smoke is a RULE over the leg's corpus and two
  of its units are dev-2 renders promoted to the front, so on the pack the pod is given, **dev-40 completes at unit 42 of 80** —
  far inside the 5400 s backstop, and the other 38 are the tail a stop would cut.
- **dev-2's units ARE holdout-40's**, so the dev order accepts `promo_holdout40.jsonl` and would write a plausible dev row from
  it: the out-file given to `--close-segment` is not checked against the pod. The run's out-file is
  `results/promo_dev40_iter4.jsonl` and nothing else ((u)3).
- `decision_table.after_the_smoke_for_40_threads` keeps its key because `project()` reads it by name · `gates.terminate_after_minutes`
  is v5b's borrowed 5400 s · `prep()` calls its count `draw.dev_threads` · `pod.main` never lifts
  `close_arrays_too` · ⛔ `1925810730`.
