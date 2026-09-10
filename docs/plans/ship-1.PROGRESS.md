# PROGRESS — ship-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines)

## Done — 10.09 s48 «s1-grade» ($0, PHASE-ship-1 §2 item 5, ruling (rr) 3): the S1 bar is READ, and it is RED
Start ritual by path: six team-lead files (`eb47806` — PHASE v6, PROCESS v2.9, PROMPT-standing v3, STATUS,
the rulings log through (ss), the day's stop-patterns). The gold was ALREADY in HEAD from s47 (`7a00463`):
`git show HEAD:docs/labels-positions-50.jsonl | shasum -a 256` = `44242b2a…`, 180 lines — verified, not
re-committed (the item's «committed by path FIRST» happened a session early).
**The fix** (`80457f7`). `volume_surface()` is the ONE place that knows the two spellings of one field: the
gold's `volume` («400 г») and the prediction's `size_value` + `size_unit` (400.0 · «г» — the store's own
columns, written by `draw_positions_50.predicted()`). `printed_badge()` reads `badge_pct` first, then the
older `discount_pct_printed`. A row with NEITHER volume spelling has no identity at all (`identity() → None`,
the search skipped before it runs) — matched by nothing, counted on both sides, never a crash and never an
empty key two such rows would share. `price_old` says «not carried» when no prediction row has the field,
instead of 42 silent disagreements. The match rule, the bars, the gold and the prediction file did NOT move.
**The reading, run:** `python3.11 scripts/grade_positions.py --gold docs/labels-positions-50.jsonl
--predicted results/positions_50_predicted.jsonl` → `completeness 0.2333 against 0.9 — RED` ·
`price_accuracy 0.9524 against 0.95 — HOLDS`, badge 40/42, `price_old` «not carried», 163 predictions
unmatched, 138 gold rows unreached — the team lead's snapshot reading (rr) 2 reproduced FIELD BY FIELD, no
difference to name. `results/grade_positions_50.json` sha `6669663b…` committed by path. The bar is
published RED; not the gold, not the match rule, not the bar was loosened.
**Negative control:** the pre-fix grader (`git show HEAD:scripts/grade_positions.py`, run from the
scratchpad) on the SAME two files still prints `0.0 · None · 205 unmatched` — (rr) 2's defect, and the
measure of the fix.
**The test, one, both ways** (§3's standing permission), `tests/test_grade_positions.py`:
`test_the_prediction_files_size_fields_are_the_same_volume_and_a_row_with_none_matches_nothing` — a
size-field row matches its gold row and its badge agrees; a row with no volume in either spelling matches
nothing and both counters see it.
**`make check` GREEN at `80457f7`: ruff clean, 4340 passed / 2 skipped / 0 failed** in five slices whose
union is PROVEN equal to `ls tests/test_*.py` (231 files, no gap, no overlap — the control asserts the union
before a slice runs); 819 + 974 + 1185 + 770 + 592 = 4340 = s47's 4339 + the one new test. Porcelain over
`src tests scripts config results docs/plans docs/reports frontend dashboard` EMPTY. **$0; cloud untouched.**

## Next — «front-1» ($0, §2 item 6; `docs/DESIGN-ship-1.md` decides every UI fork and a fork it does not settle is NOT a stop — §4.2). Then «front-2» → «e2e-ship» (11.09) → the gate 11.09 evening.

## Open stop — NONE. Cloud empty: no pod, endpoint or volume; cycle-3 $8.8398 of $10.00, REMAINING $1.1602 (unmoved).

## Deviations
- **None of substance.** `make check` in five slices is the executor's mechanic since PROCESS v2.9 (the
  totals are the claim, the proven union the method). The module docstring's «lands after S5» sentence was
  corrected in the same commit as the defect it describes — prose beside the fix, no behaviour.

## Named, not built (the phase file forbids adding what it did not ask for)
- **The S1 loss is in `product`, not in the grader.** (rr) 2's decomposition on these same inputs: brand
  alone 143/180, brand + volume 136/180 (0.756), the triple 42 — the prediction writes free text where the
  law wants the line or the category, brand surface forms drift, and one small-print grid page is misread
  wholesale. A re-extraction is a pod — OUT of ship-1. The Якість tab shows the red number with its file.
- **`record["missed"]` would write `null` for a gold row carrying no volume in either spelling** — none of
  the 180 does, so the list is 138 triples today; the gold is the team lead's and no guard was added.
- Carried from s47: no test covers `loop_daemon.py` (checked by `--once`; its two other `reading()` branches
  were fired by hand); `tick.SCHEDULE_DEFAULT`'s note still says «the schedule UI is out of scope (§6)» —
  false, corrected in front-1's commit as prose (ruling (ss) 3); `results/loop*.log` gitignored, a clock.
- Carried from s46: no test for `promote_signals.py`, `thread_population` or the gate's third state; it
  never clears its output dir; the fold map has no guard ((pp) 2(a)).
- Carried unchanged: `spend_promo_c3.json` says `"tolerance": 0.05` where the FLOOR closed it; 19.828 vs
  3.369 s/page; `promo_projection_c2.json` not reproducible from its producer; no test asserts
  `cap_from`/`{leg}`/`{STEP}-s4`, the arm selector, `graded()`'s `rows`, P1/S2/README, the ties.
