# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## The money, live — read BY HAND from the guard today, never carried from a record
Cycle 3 **SPENT $5.4962, REMAINING $1.5038** of $7.00 (`scripts/runpod_guard.py`, 09:05). **`promo-holdout`
is BOUGHT: $0.296617** — `results/promo_holdout_run.json :: gates[1].spent_all_segments_usd`, equal to
`segments[0].billed_usd`: 1443 s at the registered $0.74/h, against a $1.10 cap and under even the cheap
corner $0.8420. The guard reads balance-delta $0.3177 and a billing walk of $0.2130, still landing.
**The ledger is OPEN, twice refused, never forced (below).** Next money: c3 ≤ min($0.50, REMAINING), then
`mp-srv2` is deleted. `promo-dev-loop` also stays open by construction ((r)4), at $1.153372.

## Done — 05.09 s22, the ONE item of ruling (r) item 5, carried to the reading
- **The part branch (`0726665`).** (r) names FOUR decision-bearing fields; the audit of the built record
  found **seven** (each named in that commit), plus `step.cap_rule` and `threads_note`. `make check`
  **4320 passed, 2 skipped** pre-pod AND after the run (three disjoint slices + `ruff`), nothing changed.
- **§0a at $0, committed before any pod existed** (`50959b5` prereg, `582a655` pack, `26d4373` ledger at
  $0.0000). Rung 0: cheap $0.8420 · priced $0.8993 · dear $1.8999 (named, not hidden) → **FITS on the
  mean, hard stop 5351.4 s = 89.2 min** = (r)3's «≈89 min». Instrument byte-identical to the dev-bar
  registration's pins ((q)2); gold `6fa804880d5d14db…`; prep re-derived byte-identical before the pin.
- **The shot** (`ea1c615`, `5174f2b`). Pod `pcu2fqc7ebwfcw` 07:52:12Z → 08:16:15Z, **1443 s**. Rung 1 GO
  (price and card both registered); dead-man port in ~57 s of 500; pod HEAD == Mac HEAD; `/workspace/hf`
  59 GB warm. §5 ran the liveness/shape check and **never `--project`**: the smoke answered 8.8 / 5.3 /
  149.1 s, all balanced, all `finish=stop`, and their arrival WAS the GO (08:00:01Z). The pod ran **3.4×
  faster than its registered rate** (mean 25.826 against 88.772, max 149.054 against 201.967). Out-file
  AND pod log fetched BEFORE the delete; both listings `[]` in the transcript.
- **THE READING** (`6c6b37f`) — `--score`, then the grader itself as the judge of record:
  **signal_type_agreement 0.7958 against 0.75 — HOLDS · subject_agreement 0.7181 against 0.80 — RED.**
  Strata (no bar): currency 0.6786 / 0.8283 · decimal_only 0.8333 / 0.7633. **COMPLETE by §6.5, so it
  COUNTS:** 188 rows from **40 of 40** registered units, **0 unparsed**, every
  `finish_reason` `stop`, none unbalanced, the id set equal to the registration's order with no duplicate
  and no extra — checked by ID SET, because `wc -l == 40` also passes a duplicate plus a miss. Against
  the dev bar the same frozen instrument took (0.8714 / 0.9104), subject falls **0.1533**, signal 0.1146
  on the disjoint half of one seed-42 draw. Of 53 subject misses the visible cluster is **chain vs brand
  on the partner-bank thread `@VARUS_channel:4422`** (`izibank`, `OTP банк`). The cause is the lead's.

## Next — by (r)5 the reading ENDS the shot either way; a red bar answers S2, it does not move the gate.
The team lead's call on a RED subject bar, then «c3» ((l)2–4), then the volume; nothing was re-scored, re-run or re-bought, and the near-quote and codebook-doc sync are unblocked.

## Open stop — NONE. The reading answers the question; what follows S2 red is the team lead's.
**The ledger is OPEN and named, not forced.** `--close` with `--expect-ms 1443000` and `--tolerance 0.05`
REFUSED: «the billing walk … answered "no billing rows yet" and covered 0 ms against the run record's
1443000 … a PARTIAL walk is a third state». Without `--expect-ms`, `complete()` returns True on any
readable walk and the step freezes cheap. **A retry at 09:05, past the billing lag, ALSO did not close**
(no `closing_entry`; its walk read $0.2130 against $0.296617). **Both refusals wrote NOTHING** —
`gpu_sessions` holds exactly ONE entry, §0's. Carried open as (r)4 carries `promo-dev-loop`.
**Tree state:** every path committed, `git status` clean, no pod exists, both listings `[]`.

## Named, not built (the phase file forbids adding what it did not ask for)
- **The holdout's measured rate never reaches `measurements.jsonl`.** `write_measurement()` is called
  ONLY from the `--project` branch (`promo_dev_pass.py:1538`) and (r)2 does not run `--project`, so
  `own_rate()`'s promise that «the holdout's own smoke WRITES under `promo_holdout40_…`» is orphaned.
  Nothing reads it today (the pace survives in the replies' `seconds` and the pod log), but a future leg
  priced on `own_rate()` still reads the DEV row — 88.772 s where this pod measured 25.826.
- **`gates.terminate_after_minutes` is v5b's borrowed 5400 s, 49 s ABOVE this record's own 5351.4 s**
  (`usd_at_the_backstop` $1.11, a cent over the cap). §1's `STOP_AT` takes the `min()`. Not a KILL.
- **A field added to the record later is unbranched until someone notices** — seven is what today's
  audit found, not a closed list; §4 v8's «or the emitter refuses» half is unbuilt.
- Holdout branches carry no test (§4 forbids one) · `prep()` still calls its count `draw.dev_threads`
  (that key IS pinned, `tests/test_promo_dev_pass.py:61`; `threads_note` never was) · `pod.main` never
  lifts `close_arrays_too` · `committed_registration()` ignores `pinned_inputs` · `check_law` compares
  `codebook_version` only · **gold covers 140 of 208** · `1925810730`.
