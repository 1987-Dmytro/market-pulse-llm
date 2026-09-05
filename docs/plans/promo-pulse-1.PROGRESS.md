# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## The money, live — read BY HAND from the guard today, never carried from a record
Cycle 3 **SPENT $6.2494, REMAINING $2.7506** of the **$9.00** ceiling; anchor $14.4800 UNMOVED,
balance **$8.2306** at 15:28:28Z. **Both closes are done:** `promo-iter4` CLOSED at **$0.694815** of
$1.20 (settled on its run record, 2.73% off its post-run reference) and `promo-holdout` CLOSED at
**$0.298209** of $1.10 (settled on the WALK ALONE — it never had a reference and never took one).
**`promo-dev-loop` is the ONLY line still open and it REFUSES** — $2.5702 of $2.16, **exit 1**: an
UNBOUNDED delta over every pod since 04.09. Cap unraisable, line unclosable ((r)4), so it is **NEVER
NAMED again** — iteration 5 reads FITS with `--step promo-iter5`. A trap, named as one.

## Done — 05.09 s28: both closes settled, and (w)3's transport defect is fixed at $0.
- **Team-lead files committed by path (`c90d143`)** — the (w) addendum, PHASE **v13** §6.1 (a line's
  gate reference is its POST-RUN `--note`), the seventh stop, STATUS 18:25; hooks (`d2d498c`).
- **(w)1 — `promo-iter4`, read-only walk FIRST (`f5d5cea`).** COMPLETE at last: **3 363 287 ms of
  3 364 000**, 713 ms short of a ±33 640 band, where s27 read 57.7%. Settled **$0.694815** against
  the reference **$0.7143** — **2.73%**, inside 0.05. No `--until`: the walk's ms are POD ms.
- **(w)+ — `promo-holdout`, on the WALK ALONE (`e0b68a1`).** Its only reading is $0.0 and PRE-pod,
  so the tolerance is SKIPPED. **No late `--note` was taken** — one would have landed the $1.0708
  delta as the reference and shut the line for ever. The bound came from a READ-ONLY sweep:
  `walk_ms` saturates at **1 443 991** from 08:20Z to 13:21Z; **unbounded, 4 807 278 ms /
  $0.993024** — iteration 4's pod, refused by `complete()`. Settled **$0.298209** of $1.10.
- **(w)3 — the transport defect, $0 (`acfe360`).** POD: `run_or_report` catches a unit's exception,
  appends that unit's ERROR reply (`id`, `error`, `exception`, `unanswered`) and returns non-zero.
  The unit named is DERIVED, not guessed — the reader walks `todo` in order and flushes each row
  before the next. `SystemExit` is NOT caught: a named refusal must not come back as a unit error.
  MAC: `smoke_state` + `--smoke` reads the out-file into the registration's OWN decision-table
  branch — an error reply IS «the smoke did not come back», exit 1, delete at once. WAITING stays a
  poll (no file tells slow from dead): the runbook pairs it with `pgrep`, empty = the same outcome.
- **The fork (w)3 does not settle, resolved inside the file whose pin moves:** `already_answered`
  counts any row with an `id` as ANSWERED, so a resume over an ERROR file would skip the unit that
  killed the pod. That fix belongs to a PINNED shipped runner (§4) — so `refuse_to_resume_over_a_death` refuses first.
- **ONE test, both directions, over both halves**, on the registration's REAL three smoke units.
  Replayed on the real artifact: the old file reads WAITING (the $0.62 ambiguity), the crash
  replayed reads THE SMOKE DID NOT COME BACK. `re_emission`'s «the transport does not move» moved.
- **`make preflight`: the runner is now `43646d52e12f…`, both preregs still pin `102fa524b742…` —
  EXPECTED.** The dev record recomputes `pinned_inputs` from disk at the re-emission;
  `prereg_promo_holdout.json` is SEALED over a run under the old bytes and is NOT re-pinned.

## Next — iteration 5, the last of the five. The $0 half first, then the pod.
1. **Iteration 5 — the re-buy, authorised by (w)4:** line `promo-iter5`, cap **$1.40**, card
   **≥ 32 GB** in EU-RO-1 at the day's dearer offer ≤ $0.90/h (RTX PRO 4500 32 GB first, else
   A6000 / L40S), `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, both disclosed in
   `re_emission`; `extractor_version` UNCHANGED. Sequence as (v)4. Last of the registered five.
   **Its close is v13 §6.1's:** the POST-RUN `--note` after the pod is deleted and BEFORE any next
   pod, and the close carries `--until` — the iter4 window is now a trap for an unbounded walk.
2. **The $0 half runs first and re-emits the registration** — `--register` recomputes
   `pinned_inputs` from disk, so the runner's new sha lands there by construction.

## Open stop — NONE. Nothing waits on the operator or the team lead; the next item is $0 and mine.
**Tree.** Clean at HEAD; $0 spent, no pod, no red test. ONE test added — §4's, for a caught
product defect, in its fix's commit — and the runner's pin moved, both authorised by (w)3.

## Named, not built (the phase file forbids adding what it did not ask for)
- **§6.5's fit proof is STILL not built** — the longest registered render proven to fit BEFORE a
  pod, at $0. (w)3 fixed the REPORTING of a crash, not its prevention; it belongs to iteration 5's
  $0 half, where the card is chosen. Named, not written.
- **`--open`/`--close-segment` write `results/promo_dev_loop_run.json` at BATCH scale, not LINE
  scale:** `--expect-ms` MUST come from the segment at/after the line's anchor — twice today, agreed.
- **No test for the arm selector** (§4) or the step-aware guard read ((v)3 «no new test»).
