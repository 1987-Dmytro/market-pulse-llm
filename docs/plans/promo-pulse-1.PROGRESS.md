# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## The money, live — read BY HAND from the guard today, never carried from a record
Cycle 3 **SPENT $6.1943, REMAINING $2.8057** of the **$9.00** ceiling; anchor $14.4800 UNMOVED,
balance $8.29. **`promo-iter4` (ruling (v)) SPENT $0.6690 of $1.20** by the guard's delta; the
pod-priced figure is **$0.691489** for 3364 billed seconds, one segment. The line is **OPEN — its
`--close` is WITHHELD** because §6.5 re-buys an incomplete reading under the NEXT number and a
closing entry is one-way. ONE ledger line this session, taken before the pod.
`promo-dev-loop` $1.8462, carries no new run; `promo-holdout` $0.296617, OPEN.

## Done — 05.09 s26: the (v) stop answered, iteration 4 BOUGHT, and it came back INCOMPLETE.
- **The guard is read WITH its step (`3930fa0`).** `guard_reading(step, step_cap)` runs the guard as
  `--step <name> --step-cap <cap>`; a step line it did not print refuses as a missing REMAINING does.
  `cap_rule` on BOTH branches = min(the operator's number, THIS step's REMAINING, the cycle's).
  **Negative control, $0:** the same `--register` without `--step` still REFUSES on the old line and
  writes no record. Pack (`d964fbd`) re-pinned to 208b227a…; **the 80 units are byte-identical**.
  `make check` **4320 passed, 1 failed** — the red was the commit-then-pack ordering, green by name
  after both commits (that file 18/18). No test added.
- **The pod (`badbc8d`).** kzcnhe01mgdwvk, RTX 4090 at the registered $0.74/h, EU-RO-1, created
  13:21:09Z with `--terminate-after` 5400 s DERIVED, deleted 14:17:13Z. Rung 1 **GO** (price and card
  equal the registered); ssh port at **42 s** of a 500 s dead-man; pod HEAD = the Mac's `3e2c538`,
  volume warm (59 G), `run/` empty before the launch.
- **The smoke did not come back, so NO GO was written and none of the 80 was bought.** Two of three
  answered, balanced, finish stop: @msuaaaa:7187 **6.4 s** (shortest) · @VARUS_channel:9461 **9.5 s**
  (median). The third, @VARUS_channel:8647 at **14281 chars — the longest render, which the smoke
  rule picks on purpose** — died on `torch.OutOfMemoryError`: **338 MiB refused with 23.19 of the
  23.52 GiB already in use**. That is the registration's own decision-table branch, taken as written:
  no GO · delete · close the segment · show the listing · PHASE **§6.5 incomplete reading**.
- **`--close-segment` ran WITHOUT `--replies`:** two units are not a whole run, and (t)4 prices every
  later leg on such a row. Its «OVER» verdict is the run record summing iterations 1–3 with this one.

## Next — the transport fix, then the re-buy under the NEXT number. §6.5 calls this NOT a stop.
§6.5: the defect is fixed with its ONE test (§4) and re-bought under the next number inside the cap
and the 5-run ceiling, the diff named in the error table; this run is recorded under its number and
**never compared to the bars**. The law does NOT move — codebook v1.2 and the 80 units stand. What is
undecided is HOW the longest render is made to fit, and that is the stop below. The two seconds
readings (6.4 · 9.5) are a smoke and are NOT a rate: no whole-run row exists for this pod.

## Open stop — the OOM fix is an instrument change the plan does not settle, and it needs a new line
**Stop-point.** The instrument cannot render its own registered longest unit on a 24 GiB 4090:
23.19 GiB was already resident when 338 MiB was refused. Every remedy I can see CHANGES the
instrument under test — truncating the render, lowering the 4000-token ceiling, `expandable_segments`,
a smaller dtype, or a larger card — and plan §9a item 3 puts render and decoding changes behind a new
`extractor_version`. Moving any of them while codebook v1.2 is the law under test confounds the very
reading iteration 4 exists to take. Money compounds it: `promo-iter4` has **$0.5310** left of its
$1.20 and a full 80-unit run prices at **$0.8705**, so the re-buy does not fit this line.
**Question.** (a) Which remedy, and does it re-register as iteration 5 with a new `extractor_version`,
or is the render frozen and the card raised instead? (b) Which line pays for it — (v)2 says one paid
run is one line, so `promo-iter5` with its own anchor and the operator's cap. Neither is mine.
**Tree.** Clean at `badbc8d`; eight commits, $0.6915 of compute on a line that stays OPEN and named.
No pod exists, `pod list -a` and `serverless list` both `[]`, no red test.

## Named, not built (the phase file forbids adding what it did not ask for)
- **§6.5 asks for ONE test with the fix** — the OOM's own: the longest registered render must be
  proven to fit BEFORE a pod, at $0. It is named here, not written, because the remedy is the stop.
- **`--open`/`--close-segment` still write `results/promo_dev_loop_run.json`**, which carries
  iterations 1–3: its `spent_all_segments_usd` and its OVER/left verdicts are per-PART, not per-LINE,
  and read $1.9345 where the line reads $0.6690. `--expect-ms` MUST filter by `created_at >=` the
  line's anchor — verified here, exactly ONE segment (3364000 ms).
- **No test for the arm selector** (§4) or the step-aware guard read ((v)3 «no new test»).
