# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## The money, live — read BY HAND from the guard today, never carried from a record
Cycle 3 **SPENT $5.5351, REMAINING $3.4649** of the **$9.00** ceiling; anchor $14.4800 UNMOVED,
balance $8.94. **The new line `promo-iter4` is OPEN and anchored at $8.9546 (12:54:04Z)**, ledger
`results/spend_promo_iter4.json`, cap $1.20, **SPENT $0.0097** — the volume's drip since the anchor
and no pod. **s26 created NO pod and spent $0 on compute.** Its ONE ledger line is taken («pod about
to be created»): it says intent, and no pod followed it. `promo-dev-loop` stays as (r)4 left it at
$1.8462 and carries no new run; `promo-holdout` $0.296617, OPEN.

## Done — 05.09 s26: the (v) stop is ANSWERED and the $0 half of the purchase is committed and green.
- **Four team-lead files by path, unedited (`30cff37`)**: (v), PHASE **v11**, STATUS, stop-patterns.
- **The guard is read WITH its step (`3930fa0`, ruling (v)3).** `guard_reading(step, step_cap)` runs
  `runpod_guard.py --step <name> --step-cap <cap>`; a step line the guard did not print refuses
  exactly as a missing REMAINING does, because pricing against the cycle instead is the false record
  (v) closed. `cap_rule` on BOTH branches — the sibling was fixed too — is now min(the operator's
  number, THIS step's own REMAINING, the cycle's); `step.money` carries the step's line beside it.
- **Negative control, $0:** the same `--register` WITHOUT `--step` still REFUSES on the old line
  («$1.20 cap is reached ($1.8462 spent)» → «the guard refused (exit 1) — no registration is
  written»). With `--step promo-iter4`: SPENT $0.0000 of $1.20, ledger anchored, record written.
- **Rung 0 re-priced on the day and UNMOVED:** cheap **$0.8705** yes · priced $0.9279 · dear $4.9984
  NO → FITS on the MEAN against the $1.2000 cap, hard stop **5838 s**; RTX 4090 at the registered
  **$0.74/h** in EU-RO-1, and stock has fallen Medium → **Low**.
- **The pack (`d964fbd`):** `registration.sha256` 9ded3a79… → 208b227a…, `phase` follows the step
  name; **the 80 units and the three smoke ids are byte-identical**.
- **`make check`: 4320 passed, 1 failed, 2 skipped** — the ONE red,
  `test_the_pack_pins_exactly_what_the_pod_re_derives`, refused on «prereg differs from HEAD»: the
  commit-then-pack ordering, not a defect, and green by name after the two commits (that file 18/18).
  No test added; one existing fixture gained the step line, its invariant unmoved.

## Next — the CREATE, and everything after it is unchanged ((v)4). The $0 half is done.
`STOP_AT = now + 5400 s`: cap $1.2000 − $0.0097 = $1.1903 at $0.74/h = 5790.6 s, and the registered
90-min backstop 5400 s is SMALLER, so it bites. Then `--open --part dev` → dead-man 500 s → bundle →
launch detached → smoke 3 (@msuaaaa:7187 · @VARUS_channel:9461 · @VARUS_channel:8647) → **GO on the
three, no band gate** → the 80 → fetch, `wc -l` = 80 → delete → `--close-segment --replies
…iter4.jsonl` → `--close --expect-ms <THIS segment alone> --tolerance 0.05` → listings `[]` →
`--score --arm dev40` (BAR, K8 `--part dev`) and `--arm dev2` (READING, K8 `--part holdout`) → END.

## Open stop — the harness refuses the create; the step is authorised, the executor cannot execute it
**Stop-point.** `runpodctl pod create …` was DENIED by this session's auto-mode classifier as a paid,
irreversible action. Nothing about the run is unauthorised: ruling (v) opened the line, rung 0 issued
FITS at $0.8705 of $1.20, the registration and pack are committed, `make check` is green by name and
both listings are `[]`. I did not attempt a workaround.
**Question.** Run the create yourself with `!`, or grant `runpodctl pod create` so the session can
finish (v)4 in one go? The exact command — `mp-promo-iter4`, RTX 4090, volume `qw4nwleanc`, EU-RO-1,
SECURE, `--terminate-after` DERIVED from the record and not typed — is in this session's chat; the
pod id, its `costPerHr`, the card and the create stamp are what `--open` needs next.
**Tree.** Clean at `d13d31a`; five commits this session, $0 of compute. NO pod exists, `pod list -a`
and `serverless list` both `[]`, no red test.

## Named, not built (the phase file forbids adding what it did not ask for)
- **No test for the arm selector** (§4) or the step-aware guard read ((v)3 «no new test»): driven at $0 here.
- **`--register` ANCHORS the new line**, because (v)3 puts the guard read inside it: the anchor is
  12:54:04Z, BEFORE the `--note` (v)2 names as the anchoring event. Same session and still before the
  pod — but the $0.0097 on the line is drip measured from that earlier stamp.
- **`--open`/`--close-segment` still write `results/promo_dev_loop_run.json`**, which carries
  iterations 1–3: `--expect-ms` MUST filter segments by `created_at >=` the `promo-iter4` anchor and
  keep exactly ONE, or the close settles this line at iterations 1–3's cost and freezes it.
- **dev-2's units ARE holdout-40's**: the out-file given to `--close-segment` is unchecked against the
  pod, so the run's out-file is `results/promo_dev40_iter4.jsonl` and nothing else ((u)3).
