# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## The money, live — read BY HAND from the guard today, never carried from a record
Cycle 3 **SPENT $6.2494, REMAINING $2.7506** of the **$9.00** ceiling; anchor $14.4800 UNMOVED,
balance **$8.2306** at 15:21:06Z. **`promo-iter4` is CLOSED at $0.694815 of $1.20** — settled on its
run record, entry appended, cycle 3 witnessed. `promo-holdout` $0.296617 and `promo-dev-loop`
$1.8462 (balance delta; $1.153372 by run record) are still OPEN; neither carries a new run.

## Done — 05.09 s28: the close the billing lag was holding is SETTLED; the line is shut.
- **Team-lead files committed by path (`c90d143`)** — the (w) addendum (s27 accepted by diff),
  PHASE **v13** §6.1 (a line's gate reference is its POST-RUN `--note`; a line without one closes on
  the walk alone), stop-patterns' seventh stop, STATUS 18:25. Then s27's hook stamps (`d2d498c`).
- **The item was (w)1, retried at the start ritual as the addendum ordered — read-only walk FIRST.**
  It came back **COMPLETE**: **3 363 287 ms of the run record's 3 364 000**, 713 ms short against a
  band of ±33 640 (`MS_BAND` 1%). s27 saw 57.7% at 14:57Z and was right to refuse; the blocker was a
  billing clock and nothing else, and it ran out on its own.
- **`--close` fired exactly as PROGRESS carried it, exit 0.** Settled **$0.694815** — pods only, the
  volume's $0.019444 stays beside the run (`own_resources`) — against the reference **$0.7143**:
  **2.73% off, inside the registered 0.05**. That gap is the always-on volume's drip inside the
  step's wall-clock, the same class `promo-pulse-1` closed on at 3.15%; (w)+ predicted ~3.2%.
- **No `--until`, and that was safe TODAY ONLY.** The walk's ms are POD ms: 12:54Z→15:21Z is ~8.7 M
  ms of wall-clock and the walk returns 3.36 M, so `network-volume` rows carry no `timeBilledMs` and
  the window cannot drift out of the band while it waits. **Once iteration 5's pod exists, an
  unbounded walk over this window swallows it** — no later close on this line may omit the bound.
- **Two files, ONE commit (`f5d5cea`):** the step ledger's closing entry (`settled_usd`,
  `recorded_reading_usd`, `walk_ms`, `expected_ms`) and cycle 3's witness line, written beside it so
  a later refusal cannot take the witness with it. The four tests that read either ledger →
  **89 passed**. No test, pin, guard or ledger ADDED; $0 spent; no pod.

## Next — the second close, then the transport fix, then the buy. Order is (w)+'s: closes → 3 → 4.
1. **`promo-holdout` closes on the WALK ALONE ((w)+, PHASE v13 §6.1).** Its only entry is $0.0 and
   PRE-pod, so `recorded_reading()` returns 0 and the guard SKIPS the tolerance — the line has no
   reference and may never grow one. Two constraints, both fatal if improvised:
   **(a) NEVER a `--note` on this line** — a reading taken now is ≈$1.06 against a settle of
   ~$0.2966 and shuts the gate for ever; **(b) `--until` is MANDATORY** — unbounded, the walk since
   07:50:48Z swallows iteration 4's pod (13:21:09Z→14:17:13Z) and both the ms and the dollars lie.
   Find the bound with a READ-ONLY bounded walk first: any instant between the line's last billing
   row and 13:21:09Z, then `--step promo-holdout --step-cap 1.10 --close --expect-ms 1443000
   --until <that instant> --tolerance 0.05 --note "<why>"`.
2. **Then the transport defect, §4 (ruling (w)3), at $0:** the runner catches a unit's exception,
   writes an ERROR reply for that unit (`error`, the exception's name, the unit) and exits non-zero;
   the Mac reads an error reply among the smoke's three as «the smoke did not come back» and deletes
   AT ONCE instead of waiting out the deadline. ONE test, both directions, in the fix's commit; the
   runner's pin moves with it. It cost $0.62 of waiting on 05.09.
3. **Then iteration 5 — the re-buy, authorised by (w)4:** line `promo-iter5`, cap **$1.40**, card
   **≥ 32 GB** in EU-RO-1 at the day's dearer offer ≤ $0.90/h (RTX PRO 4500 32 GB first, else
   A6000 / L40S), `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, both disclosed in
   `re_emission`; `extractor_version` UNCHANGED. Sequence as (v)4. Last of the registered five.
   Its line takes its POST-RUN `--note` after the pod is deleted and before any next pod (v13 §6.1).

## Open stop — NONE. Nothing waits on the operator or the team lead; the next item is $0 and mine.
**Tree.** Clean at `f5d5cea`; $0 spent this session, no pod, no red test, no test or pin added.

## Named, not built (the phase file forbids adding what it did not ask for)
- **§6.5's ONE test for the OOM fix** — the longest registered render must be proven to fit BEFORE a
  pod, at $0. Named, not written: it belongs to the transport/serving fix's own commit.
- **`--open`/`--close-segment` still write `results/promo_dev_loop_run.json` at BATCH scale, not
  LINE scale** (`latest` reads `OVER`, summing iterations 1–3 with iteration 4): `--expect-ms` MUST
  come from the segment whose `created_at` is at/after the line's anchor — ONE segment, 3364 s.
- **No test for the arm selector** (§4) or the step-aware guard read ((v)3 «no new test»).
