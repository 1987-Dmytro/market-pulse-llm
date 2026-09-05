# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## The money, live — read BY HAND from the guard today, never carried from a record
Cycle 3 **SPENT $6.2494, REMAINING $2.7506** of the **$9.00** ceiling; anchor $14.4800 UNMOVED,
balance **$8.2306** at 15:28:28Z. **Both closes are done:** `promo-iter4` CLOSED at **$0.694815** of
$1.20 (settled on its run record, 2.73% off its post-run reference) and `promo-holdout` CLOSED at
**$0.298209** of $1.10 (settled on the WALK ALONE — it never had a reference and never took one).
**`promo-dev-loop` is the ONLY line still open** and reads $2.5702 of $2.16 — an UNBOUNDED delta
that has swallowed every pod since 04.09 plus the volume's drip. Open by construction ((r)4); it
carries no new run and gates nothing, and v11 is the rule that stops the next line becoming it.

## Done — 05.09 s28: both closes settled; the phase's money is one open line and it is inert.
- **Team-lead files committed by path (`c90d143`)** — the (w) addendum, PHASE **v13** §6.1 (a line's
  gate reference is its POST-RUN `--note`; a line without one closes on the walk alone),
  stop-patterns' seventh stop, STATUS 18:25. Then s27's hook stamps (`d2d498c`).
- **(w)1 — `promo-iter4`, read-only walk FIRST.** It came back **COMPLETE**: **3 363 287 ms of the
  run record's 3 364 000**, 713 ms short of a ±33 640 band (`MS_BAND` 1%). s27 saw 57.7% at 14:57Z
  and was right; the blocker was a clock and it ran out. `--close` exactly as PROGRESS carried it,
  exit 0: settled **$0.694815** (pods only) against the reference **$0.7143** — **2.73%**, inside
  the registered 0.05, the volume's drip in the step's wall-clock as (w)+ predicted at ~3.2%.
  No `--until`, safe TODAY ONLY: the walk's ms are POD ms, so the window could not drift; once
  iteration 5's pod exists an unbounded walk over that window swallows it. (`f5d5cea`)
- **(w)+ — `promo-holdout`, closed on the WALK ALONE.** Its only reading is $0.0 and PRE-pod, so
  `recorded_reading()` returns 0, the tolerance gate is SKIPPED and the walk is the settlement.
  **No late `--note` was taken** — one now would have landed the $1.0708 balance delta as the
  reference and shut the line for ever. The bound came from a READ-ONLY sweep, not from taste:
  `walk_ms` saturates at **1 443 991** (of 1 443 000, band ±14 430) everywhere from 08:20Z to
  13:21Z with pods flat at $0.298209 — nothing else billed in the gap; **unbounded it reads
  4 807 278 ms / $0.993024**, iteration 4's pod swallowed, and `complete()` refuses. That is the
  negative control and it fired. `--until 08:20:00Z` is the tightest bound in the range, so the
  record carries $0.009722 of always-on volume instead of $0.058333. Settled **$0.298209**; the
  $1.070802 delta is recorded BESIDE it, never as it. (`e0b68a1`)
- **Each close wrote TWO files in ONE commit** — the closing entry and cycle 3's witness line. The
  four tests that read either ledger → **89 passed**, both times. No test, pin, guard or ledger
  ADDED; $0 spent this session; no pod; `--expect-ms` READ from the run records, never typed.

## Next — the transport fix at $0, then the buy. Nothing else is owed before iteration 5.
1. **The transport defect, §4 (ruling (w)3), at $0:** the runner catches a unit's exception, writes
   an ERROR reply for that unit (`error`, the exception's name, the unit) and exits non-zero; the
   Mac reads an error reply among the smoke's three as «the smoke did not come back» and deletes AT
   ONCE instead of waiting out the deadline. ONE test, both directions, in the fix's commit; the
   runner's pin moves with it. It cost $0.62 of waiting on 05.09.
2. **Then iteration 5 — the re-buy, authorised by (w)4:** line `promo-iter5`, cap **$1.40**, card
   **≥ 32 GB** in EU-RO-1 at the day's dearer offer ≤ $0.90/h (RTX PRO 4500 32 GB first, else
   A6000 / L40S), `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, both disclosed in
   `re_emission`; `extractor_version` UNCHANGED. Sequence as (v)4. Last of the registered five.
   **Its close is already specified by v13 §6.1:** the POST-RUN `--note` is taken after the pod is
   deleted and BEFORE any next pod, and the close carries `--until` — the iter4 window is now a
   trap for an unbounded walk, and iter5's becomes one the moment anything else bills.

## Open stop — NONE. Nothing waits on the operator or the team lead; the next item is $0 and mine.
**Tree.** Clean at HEAD; $0 spent this session, no pod, no red test, no test or pin added.

## Named, not built (the phase file forbids adding what it did not ask for)
- **§6.5's ONE test for the OOM fix** — the longest registered render must be proven to fit BEFORE a
  pod, at $0. Named, not written: it belongs to the transport/serving fix's own commit.
- **`--open`/`--close-segment` still write `results/promo_dev_loop_run.json` at BATCH scale, not
  LINE scale** (`latest` reads `OVER`, summing iterations 1–3 with iteration 4): `--expect-ms` MUST
  come from the segment whose `created_at` is at/after the line's anchor — twice today, both agreed.
- **No test for the arm selector** (§4) or the step-aware guard read ((v)3 «no new test»).
