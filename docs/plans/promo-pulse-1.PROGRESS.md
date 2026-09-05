# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## The money, live — read BY HAND from the guard today, never carried from a record
Cycle 3 **SPENT $6.2396, REMAINING $2.7604** of the **$9.00** ceiling; anchor $14.4800 UNMOVED,
balance **$8.2403** at 14:40:49Z. **`promo-iter4` SPENT $0.7143 of $1.20** by the guard's balance
delta; the run record prices the pod at **$0.691489** for 3364 billed seconds, one segment. The line
is **still OPEN**: (w)1's `--close` is refused by the COMPLETENESS gate, not by a decision — see
Next. `promo-dev-loop` $1.8462, carries no new run; `promo-holdout` $0.296617, OPEN.

## Done — 05.09 s27: ruling (w) is committed and the close's missing REFERENCE is on disk.
- **Team-lead files committed by path (`961d425`)** — ruling (w), PHASE **v12** (§6.5: a serving
  failure moves the serving, never the instrument), the day's sixth stop, STATUS 16:40. Then s26's
  own hook checkpoint (`c9db035`). Tree clean before the first command of the item.
- **The item was (w)1: close `promo-iter4` on its run record. As the ledger stood it could not
  pass, and the reason is a gate, not a wish.** `recorded_reading()` takes the LAST NON-CLOSED
  `step_spent_usd` as the tolerance gate's right-hand side. s26 spent its one ledger line BEFORE the
  pod, so that value was **$0.0097** — a settled ~$0.6915 against it is ~**7000%** off, refused
  every time it is run, not once. This is the class the dev-loop line already hit at 33.7% in s21.
- **Every step ledger that has ever closed carries a POST-RUN reading as its last open entry and
  settles against it** — `lora-c` 0.7338 → 0.764952 (4.2%) · `promo-pulse-1` 3.0335 → 2.986741
  (3.15%, tol 0.05) · `srv2b` · `srv2d` — so the reading is the guard's path, not a way around it.
- **The reading is taken and committed (`e75342b`): $0.7143 at 14:40:49Z, balance 8.2403244051** —
  this session's ONE ledger line, `--note` only. It is a BALANCE DELTA and the close's figure is a
  BILLING WALK, so the gate still compares two instruments; the gap it will read (~3.2%) is the
  always-on volume's drip inside the step's wall-clock — exactly what `promo-pulse-1`'s own close
  named at 3.15%. Both writes committed by path: the step ledger and cycle 3's witness line.
- **`--expect-ms 3364000` is READ, not typed:** `promo_dev_loop_run.json` segment 6 — 3364.0 s,
  `kzcnhe01mgdwvk`, `billed_usd 0.691489`. No test, pin, guard or ledger added; nothing paid ran.

## Next — the close is owed on a CLOCK, not on a decision. Then the transport fix, then iteration 5.
1. **`--close` the `promo-iter4` line, unchanged from (w)1** — the one command the item still owes:
   `python scripts/runpod_guard.py --step promo-iter4 --step-cap 1.20 --close --note "<why>"
   --expect-ms 3364000 --tolerance 0.05`. It refuses TODAY because the billing walk over the line's
   window covered **1 647 152 ms of 3 364 000 (49%)** at 14:47Z — `complete()` calls a PARTIAL walk a
   third state and will not settle on it (Dv488). The pod was deleted 14:17:13Z and the walk was
   climbing ~9%/6 min, so the gate opens ~15:20Z; `lora-c` needed until the NEXT DAY. Re-check with
   the read-only walk first, never by firing the close at it. The reference $0.7143 and the settled
   ~$0.691489 sit 3.19% apart; past $0.72788 the 5% band would have closed for good, so the reading's
   timing was the whole of it and it is taken.
2. **Then the transport defect, §4 (ruling (w)3), at $0:** the runner catches a unit's exception,
   writes an ERROR reply for that unit (`error`, the exception's name, the unit) and exits non-zero;
   the Mac reads an error reply among the smoke's three as «the smoke did not come back» and deletes
   AT ONCE instead of waiting out the deadline. ONE test, both directions, in the fix's commit; the
   runner's pin moves with it. It cost $0.62 of waiting on 05.09.
3. **Then iteration 5 — the re-buy, authorised by (w)4:** line `promo-iter5`, cap **$1.40**, card
   **≥ 32 GB** in EU-RO-1 at the day's dearer offer ≤ $0.90/h (RTX PRO 4500 32 GB first, else
   A6000 / L40S), `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, both disclosed in
   `re_emission`; `extractor_version` UNCHANGED. Sequence as (v)4. Last of the registered five.

## Open stop — NONE. The OOM stop is answered by ruling (w); today's blocker is a billing lag.
**Tree.** Clean; six commits this session, $0 spent, no pod, no red test, no test added.

## Named, not built (the phase file forbids adding what it did not ask for)
- **§6.5's ONE test for the OOM fix** — the longest registered render must be proven to fit BEFORE a
  pod, at $0. Named, not written: it belongs to the transport/serving fix's own commit.
- **`--open`/`--close-segment` still write `results/promo_dev_loop_run.json` at BATCH scale, not
  LINE scale:** its `latest` verdict is `OVER` because it sums iterations 1–3 with this one, while
  the line reads $0.7143 of $1.20. `--expect-ms` MUST be taken from the segment whose `created_at`
  is at or after the line's anchor — verified again today: exactly ONE such segment, 3364 s.
- **No test for the arm selector** (§4) or the step-aware guard read ((v)3 «no new test»).
