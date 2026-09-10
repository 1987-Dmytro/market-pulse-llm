# PROGRESS — ship-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines)

## Done — 10.09 s45 «chain-fold» ($0, PHASE-ship-1 §2 item 2): ONE Маркетопт on the screen, 83 rows
Start ritual: the v2 re-spec by path (`62512f2`), the hook-touched `knowledge/` files (`10db6e8`).
**(i) the map is read BEFORE the spellings** (`673eb65`). `config/chain_aliases.yaml` gains a second
section `chain_of_channel` (one line: `marketopt_private: marketopt_promo`); the flat id→spellings
map moves under `spellings:`, and `registry.chain_of_channel()` reads it beside `chain_spellings()`
over one `_aliases()` body. `chain_key` tries the channel map first — a channel id is not a NAME, so
no spelling of it could match — and the two tables stay SEPARATE lookups: merged into `_chain_ids()`,
a channel id a spelling also normalises to would trip the duplicate refusal for no defect. R2/R3
write `chain_key(own.id)` where they wrote the registry NAME; the screen's `chain.id` is
`chain_key(ch.source_id)`, folded ONCE into a local that the row and the sort key both read. R3's
aggregator branch is untouched — it has no owner, and (gg) 2 folds the OWNER's id.
**(ii) 83, and not one graded number moved** (`6f4a682`). `make tick` twice: `new 0` in all six
tables, export sha unmoved (K10). `screen.positions` **1301**, 1301 distinct `(carrier, row_id)`,
`chain.id == "marketopt_private"` **0**, `marketopt_promo` **83** = 26 (w1's 4 + w2's 22) + 57 —
(oo) 2's number MEASURED on the union it runs on, not arithmetic on the old export;
`named_by_amendment_3_20` false on all 83. `draw_truth_20 --json` → population 1301 and
`truth_20.json` BYTE-IDENTICAL `6958e002…` (it sorts by `row_id` before sampling, so the new order
never reaches it); README's S2 block re-derived byte-identical. `promo_p1_apply.py`, two runs
byte-identical: loop **dev40 0.8857/0.8667 · dev2 0.9043/0.8296 · dev3 0.7411/0.7937**, reading
dev3 0.7500/0.8021 — every reading, stratum, miss and tie count UNCHANGED. The only moved fields in
either record are shas (`p1.sha256` b2c0e2b9…→74132120…, two predicted files); the rows moved
surface form only (`"Varus"`→`"varus"`, `subject_id` unchanged), which is why the grader is quiet.
**(iii) (jj) 3's two runbook nits** (`b6100ce`): §3 names `--endpoint E` / `-T` as placeholders, and
`&& [ -n "$RUNPOD_API_KEY" ]` is now its second link — `export X=$(…)` takes the assignment's status.
**`make check` GREEN at `b6100ce`: ruff clean, 4333 passed / 2 skipped** (4332 + my one test), in
four slices — the suite is over one call's ceiling. Tree porcelain EMPTY. **$0 this session.**

## Next — «s2-promote» ($0, PHASE-ship-1 §2 item 3)
**next: s2-promote.** Then «serve-loop» (10.09); «front-1» → «front-2» → «e2e-ship» (11.09) → the
operator's gate 11.09 evening, reserve 12.09 12:00.

## Open stop — NONE. Cloud empty: no pod, endpoint or volume; cycle-3 $8.8398 of $10.00, REMAINING $1.1602 (unmoved).

## Deviation — `process`: I read three team-lead docs with `sed -n` before re-reading §4.5
`docs/PHASE-ship-1.md`, `docs/reviews/2026-08-30-plan-promo-pulse-1.md`,
`docs/reviews/2026-09-10-stop-patterns.md` — §4.5 says team-lead paths are read with the Read tool
and never named to a Bash file command. No refusal fired (the deny rules are Edit-only) and nothing
was written; the rest of the session used the Read tool. Named, not repeated.

## Named, not built (the phase file forbids adding what it did not ask for)
- **The fold has no validation guard and §3 forbids adding one.** Nothing checks that both sides of
  a `chain_of_channel` line are ids the registry carries, or that a folded-FROM id is never also a
  fold TARGET (a two-hop chain silently resolves one hop). One line, one reader, one caller today
  — the need is named here ([[a_patch_list_closed_by_enumeration]]).
- **The subject a store already holds is not re-folded.** `subject_id` is unchanged by the fold, so
  `INSERT OR IGNORE` keeps a row written under the old surface form («Varus») while a fresh rebuild
  writes «varus». Invisible today — `screen.feed` is empty — and «s2-promote» is the first tick that
  writes signal rows ([[a_rebuild_deletes_its_output_before_it_can_refuse]]).
- **`grade_promo_p1_readings.json` moved although §2 named only the loop record** — ONE producer
  writes both, and leaving it stale against a P1 it no longer describes is the worse of the two.
  No sealed record pins it (`preflight`: 0 pins) and the bar's pre-registered readings are untouched.
- Carried from s44: **two sibling readers keep their own `WHERE p.window_id = ?`** —
  `aggregates.promo_by_chain` and `coverage` return silently EMPTY on `all`; (oo) 3 routes them
  through `positions_source` inside «serve-loop», so they are NOT folded here either
  ([[the_hardening_did_not_reach_the_sibling_reader]]). · **The closing record does not say which
  term graded it** — `spend_promo_c3.json` carries `"tolerance": 0.05` while the $0.05 FLOOR closed
  it. · **The measured/priced gap stands as s42 left it:** 19.828 s/page against the registered 3.369.
- Carried unchanged: `promo_projection_c2.json` not reproducible from its producer (its pin is the
  proof); no test asserts `cap_from`, `{leg}`, `{STEP}-s4`; `tooling.md`'s «plugin disabled», the
  unfloored arm selector, `graded()`'s `rows`, P1/S2/README untested in the tick, the ties.
