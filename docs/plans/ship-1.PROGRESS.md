# PROGRESS — ship-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines)

## Done — 10.09 s45 «chain-fold» ($0, PHASE-ship-1 §2 item 2): ONE Маркетопт on the screen, 83 rows
Start ritual by path: the v2 re-spec (`62512f2`), the hook-touched `knowledge/` files (`10db6e8`).
**(i) the map is read BEFORE the spellings** (`673eb65`). `config/chain_aliases.yaml` gains a
section `chain_of_channel` (`marketopt_private: marketopt_promo`); the flat id→spellings map moves
under `spellings:` and `registry.chain_of_channel()` reads it beside `chain_spellings()`. `chain_key`
tries the channel map first — a channel id is not a NAME, so no spelling of it could match — and the
two stay SEPARATE lookups: merged, a channel id a spelling also normalises to would trip
`_chain_ids()`'s duplicate refusal for no defect. R2/R3 write `chain_key(own.id)` where they wrote
the registry NAME; the screen's `chain.id` is `chain_key(ch.source_id)`, folded ONCE into a local the
row and the sort key both read. R3's aggregator branch is untouched — no owner, and (gg) 2 folds the
OWNER's id.
**(ii) 83, and not one graded number moved** (`6f4a682`). `make tick` twice: `new 0` in all six
tables, export sha unmoved (K10). `screen.positions` **1301**, 1301 distinct `(carrier, row_id)`,
`chain.id == "marketopt_private"` **0**, `marketopt_promo` **83** = 26 (w1's 4 + w2's 22) + 57 —
(oo) 2's number MEASURED on the union it runs on, not arithmetic on the old export.
`draw_truth_20 --json` → population 1301, `truth_20.json` BYTE-IDENTICAL `6958e002…` (it sorts by
`row_id` before sampling); README's S2 block re-derived byte-identical. `promo_p1_apply.py`, two runs
byte-identical: loop **dev40 0.8857/0.8667 · dev2 0.9043/0.8296 · dev3 0.7411/0.7937**, reading dev3
0.7500/0.8021 — every reading, stratum, miss and tie count UNCHANGED. The only moved fields are shas
(`p1.sha256`, two predicted files); the rows moved surface form only (`"Varus"`→`"varus"`,
`subject_id` unchanged), which is why the grader is quiet.
**(iii) (jj) 3's two runbook nits** (`b6100ce`): §3 now names its `--endpoint E` / `-T` placeholders, and `&& [ -n "$RUNPOD_API_KEY" ]` is its second link — `export X=$(…)` takes the ASSIGNMENT's status.
**`make check` GREEN at `b6100ce`: ruff clean, 4333 passed / 2 skipped** (4332 + my one test), in four
slices — the suite is over one call's ceiling. Porcelain EMPTY. **$0 this session.**

## Next — «s2-promote» ($0, PHASE-ship-1 §2 item 3)
**next: s2-promote.** Then «serve-loop» (10.09); «front-1» → «front-2» → «e2e-ship» (11.09) → the
operator's gate 11.09 evening, reserve 12.09 12:00.

## Open stop — NONE. Cloud empty: no pod, endpoint or volume; cycle-3 $8.8398 of $10.00, REMAINING $1.1602 (unmoved).

## Deviation — `process`: three team-lead docs read with `sed -n` before I re-read §4.5
(`PHASE-ship-1.md`, the two reviews). No refusal fired (deny is Edit-only), nothing was written, and
the rest of the session used the Read tool.

## Named, not built (the phase file forbids adding what it did not ask for)
- **The fold has no validation guard and §3 forbids adding one.** Nothing checks that both sides of
  a line are registry ids, or that a folded-FROM id is never a fold TARGET (a two-hop chain resolves
  one hop) ([[a_patch_list_closed_by_enumeration]]).
- **The map is inside `chain_key`, so EVERY `chain` subject in the project folds through it** —
  `subject_id`, the grader, both sides of it — not only the screen and P1 that §2 names. Only a row
  spelled with a registry channel id can move, and nothing is spelled that way today (no graded
  number moved, no Маркетопт thread is in the 120), but the reach is wider than the item's check.
- **The subject a store already holds is not re-folded.** `subject_id` is unchanged, so `INSERT OR
  IGNORE` keeps a «Varus» row where a rebuild writes «varus» — invisible while `screen.feed` is
  empty; «s2-promote» is the first tick that writes signal rows.
- **`grade_promo_p1_readings.json` moved although §2 named only the loop record** — ONE producer
  writes both, and stale against a P1 it no longer describes is worse. No sealed record pins it
  (`preflight`: 0 pins); the bar's pre-registered readings are untouched.
- Carried from s44 with a SECOND defect: `aggregates.promo_by_chain` and `coverage` keep their own
  `WHERE p.window_id = ?` (silently EMPTY on `all`) **and their `source_id` keys are unfolded**, so
  they split Маркетопт where `positions` on the same store shows one — two readers, two chain
  populations. (oo) 3 routes both through `positions_source` in «serve-loop», which inherits both
  ([[the_hardening_did_not_reach_the_sibling_reader]]); nothing ships wrong today (only
  `export_dashboard_data` reaches them, and it pins w1, which has none of the 57).
- Carried unchanged: `spend_promo_c3.json` says `"tolerance": 0.05` where the FLOOR closed it; the gap
  19.828 vs 3.369 s/page; `promo_projection_c2.json` not reproducible from its producer; no test
  asserts `cap_from`/`{leg}`/`{STEP}-s4`, the arm selector, `graded()`'s `rows`, P1/S2/README, the ties.
