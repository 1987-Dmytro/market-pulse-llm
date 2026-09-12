# PROGRESS — ship-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines)

## Done — 12.09 s50 «front-1» ($0, PHASE-ship-1 §2 item 6, ruling (tt) 3): the app exists, both modes work
Start ritual: no team-lead file modified or new, so none was committed by path first. **s49 left front-1 built and UNCOMMITTED** — `76ba000`
(the lifted `conclusions()` callable + `tick.SCHEDULE_DEFAULT`'s corrected sentence, ruling (ss) 3, DONE there) and `266d48f` (the producer)
were in HEAD, the app was not. s50 verified it, fixed what that found, committed it: `8d9de41` · `2731fb8` · `dd3c110` · `58e2e1f` ·
`210b878`. **The app** (`frontend/`, 35 files): Vite 6 · React 19 · TS 5 strict · Recharts 3 · vitest, pinned, lockfile committed; hash
routing, UA/EN, light/dark, §3 tokens, no CSS framework. Five promo tabs read the two exports; the command centre's nine route and say
front-2. **The producer** grew `chains` (registry names folded by `chain_aliases.yaml`, so a table reads «АТБ» not `atb`) and `s2_boundary`,
and `tick.REGISTRY` + `registry.CHAIN_ALIASES` joined `required()`. **Determinism measured:** two runs write `results/front_data.json` byte
for byte (sha `f1c7c629…`), carrying `data_until` from the export's windows, never a clock — DESIGN §7's `generated_at` is deliberately
absent (fork §4.2: a clock would dirty the tree on every `make front`). **Checks, all at `210b878`:** `make front` green · `npm run check`
clean · `npx vitest run` **19 passed** (18 + the one new test) · the five tabs render under `make serve` at 1440 px in UA and EN, both
themes, screenshots in `docs/reports/screens/` · static mode over `http.server` on the built `dashboard/app/` · **no console message comes
from the app** (all 35 were a MetaMask extension) · `make check` GREEN: ruff clean, **4340 passed / 2 skipped** in five slices whose union
is PROVEN equal to `ls tests/test_*.py` (231 files, no gap, no overlap, asserted before a slice ran); 819+974+1185+770+592 = 4340 = s48's
count — front-1 adds no pytest, its tests are vitest. Porcelain over the §8 set EMPTY, and EMPTY again after `make front` was re-run on the
tree of `210b878`, the last code commit — the bundle a clone builds. **$0; no cloud call this session.**

## Six defects CAUGHT and FIXED (§3's standing permission; each MEASURED in the browser — full text in `58e2e1f`)
1. **A static build whose `front_data.json` lacks `status` came up BLANK** — read off the parsed document, the throw landed inside the
   render and React unmounted. That is the mode the public showcase ships in and DESIGN §2 promises a panel; through `must()` now: «джерело
   відсутнє: front_data.json :: status».
2. **The table keyed a row on `row_id`, which REPEATS** — 7 of 1 301 rows share an id with a row of the other carrier and the sort's
   tiebreak lands each pair on one page, so one click on such a row's ⓘ opened TWO panels (`buttonsExpanded: 2`); now 1. The key is
   `(carrier, row_id)`, the pair §2 «w3» dedupes by. **ONE test, both ways** — the pair is unique over every shipped row, the id alone is
   not; the only test added.
3. **Якість printed «вибірка 50 сторінок» above «46 сторінок»** — 50 is `rows_drawn`, the pages `pages_drawn_from` = 46: the screen
   contradicted itself about one draw, on the trust tab.
4. **Тренди titled a chart «за мережею» over rows the rollup keys on a CHANNEL** — three strings say «канал»; nothing summed, no row moved
   (a bar per chain is a figure no file carries — s49's reasoning, kept).
5. **`<html lang>` never followed the toggle** — a screen reader read the EN UI in Ukrainian (DESIGN §8).
6. **Static Петля rendered the schedule as two EMPTY number boxes**, wrong label, one sentence twice; an empty input reads as «the interval
   is unset». Served-mode only now; static names the file (DESIGN §10).
Also: the «таблиця» view dropped the empty-state sentence (Тренди's DEFAULT view opens on an empty series); the «мереж» card spelled a path
into its context line (§5). Served mode re-checked after each: no regression.

## Next — «design-pass» ($0, §2, NEW by ruling (vv): DESIGN v2 §11 on the accepted app). Then «front-2» → «e2e-ship» → the gate.

## Open stop — NONE. Cloud empty: no pod, endpoint or volume; cycle-3 $8.8398 of $10.00, REMAINING $1.1602 (unmoved).

## Deviations
- **s49's uncommitted tree** was verified before it was committed, not taken on trust. Its five screenshots were REPLACED (they show the
  pre-fix screens); mine are 1440×778 viewport captures (`210b878` says why). A 39-agent read-only review ran first — 16 findings, 6
  survived an adversarial verify, and **two it REFUTED are fixed anyway**: a measured blank page outranks an argued refutation.

## Named, not built (the phase file forbids adding what it did not ask for)
- **`status.money.from` names `sessions[-1]` for a block whose `cap_usd` is a ROOT key** of the ledger (`export_front_data.py` reads
  `ledger["cycle3_cap_usd"]`); two of three are in `sessions[-1]`. The string is the producer's, so the fix is the team lead's call, not a
  relabel.
- **`depth_by_chain_and_brand` and `rollup` key on a CHANNEL handle** while `positions[].chain.id` is a folded registry id — two id spaces
  in one export. Folding them rebuilds the store and moves `promo_screen_data.json`'s sha (`e45860c6…`): out of front-1, and defect 4
  renames the LABEL only.
- The English `from`/`note` sentences render verbatim in the UA UI — the producer's artifact strings, and the app rewrites no source.
  `/api/status` is asked ONCE at boot (DESIGN §2), so «тик зараз» does not re-read the line.
- Carried from s48: the S1 loss is in `product`, not the grader — a re-extraction is a pod, OUT of ship-1.
- Carried: no test for `loop_daemon.py`, `promote_signals.py`, `thread_population`, the gate's third state; `promote_signals.py` never
  clears its output dir; the fold map has no guard ((pp) 2(a)); `spend_promo_c3.json` says `"tolerance": 0.05` where the FLOOR closed it;
  `promo_projection_c2.json` not reproducible from its producer; no test asserts `cap_from`/`{leg}`/`{STEP}-s4`, `graded()`'s `rows`, the
  ties.
