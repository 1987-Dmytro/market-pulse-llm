# PROGRESS — ship-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines)

## Done — 10.09 s47 «serve-loop» ($0, PHASE-ship-1 §2 item 4): the product RUNS
Start ritual by path: the gold `docs/labels-positions-50.jsonl` FIRST (`7a00463`, sha `44242b2a…` printed in its
message, 180 lines — it matched), (qq)+(rr) (`94af8da`), `knowledge/` (`ae21f1a`).
**(i) the two sibling readers** (`2e054de`). `aggregates.one_window()` refuses `all` by name before the query in both;
`positions_source` was (oo) 3's other half and `coverage` cannot take it — it reads `windows`/`segments`/`channels`,
no position at all. With it (pp) 2(e): `promo_by_chain` keys by `chain_key(source_id)` and SUMS per carrier (an
assignment would drop one of two folded channels' leaflet rows). Measured BEFORE the edit: no window holds two
channels that fold together (`marketopt_private` is w3-only) and `chain_key` is the identity on every w1 source id —
the sealed `dashboard_data_w1.json` cannot move, and its producer's three test files agree (44 passed).
**(ii) `make serve`** (`a672e51`). `scripts/serve.py`, FastAPI + uvicorn pinned in a new `serve` extra, `127.0.0.1`,
no auth (§3); the paths are the tick's own constants. `/api/status`: the tick state (gitignored → on a clean clone
`at: null` WITH the sentence, never a zero), the windows from the store and from the committed export when there is
none, the queue as `screen.threads`, `money.remaining_usd` as the cycle-3 ledger's last recorded line through
`guard.cycle3_path()` — no balance call exists in the process. `GET`/`PUT /api/schedule` through a pydantic model:
`min ≥ 1`, `default ≥ min` refuse as 422 with the field named BEFORE the file opens, the write merges so its note
survives. `POST /api/tick`: `tick.py` in a subprocess with the server's paths, counters read from the state file IT
wrote. `/api/exports/{name}`: a NAME against `[a-z0-9_]+\.json` under `results/` — `..` is a 404.
**(iii) `make loop`** (`9926760`). `loop_daemon.py` wakes, runs `tick.py --if-due`, writes ONE line, sleeps the
minimum interval re-read each wake. No paid path in it: `data/loop.json :: endpoint` is created empty and only READ,
and the log says WHICH nothing the queue is. `ops/…loop.plist` is a launchd template (`plutil -lint` OK), install
steps in the README's new «Running it» — not installed.
**The checks, run:** `curl /api/status` → three windows with anchors (08-09 · 08-31 · 09-05), «read 118 of 678 · queue
548 · not_collected 12», money $1.1602 of $10.00 from `sessions[-1]`; BOTH spellings of 30 minutes → **422** (`min
0.5`; `default 0.5` under `min 2`) with `data/schedule.json` sha `eaabf0a7…` unmoved; the tick button → exit 0, **new
0 in all six tables**, export sha `e45860c6…` unmoved (K10); `/` 200 (stub), the export 200, `../pyproject.toml` 404;
`--once` → «… nothing written · **queue 548 threads · reading unbought**», the log's whole content. `make
promo-screen` green after the README edit; porcelain over `results dashboard README.md` empty.
**`make check` GREEN at `9926760`: ruff clean, 4339 passed / 2 skipped / 0 failed** in five slices whose union is
PROVEN equal to `ls tests/test_*.py` (231 files, no gap, no overlap; a dropped slice is refused by the control) — 4334
at s46 + 5 new. **$0; cloud untouched.**

## Next — «s1-grade» ($0, §2 item 5, ruling (rr) 3). Then «front-1» → «front-2» → «e2e-ship» (11.09) → the gate 11.09 evening.

## Open stop — NONE. Cloud empty: no pod, endpoint or volume; cycle-3 $8.8398 of $10.00, REMAINING $1.1602 (unmoved).

## Deviations
- **Two sources in one clause:** the item says the queue comes «from the tick's digest counts» and, later, «=
  `screen.threads` … never the tick's cooled counter». Followed (qq) 6 and the second.
- **Process, mine, the same as (pp)'s:** `cat`/`sed`/`awk` on `PHASE-ship-1.md` and the rulings file before I re-read
  §4.5 — no refusal fired (deny is on `Edit`), nothing written; the Read tool from `DESIGN-ship-1.md` on. Cause: the
  prompt's read order run before its constraint list.
- **`make check` sliced**, not one call (~12 min > the ceiling): the totals are the claim, the five-slice method the
  deviation — coverage proven by union, not by summing counts.

## Named, not built (the phase file forbids adding what it did not ask for)
- **No test covers `loop_daemon.py`** (§2's list names the schedule, the three GETs and the tick; it is checked by
  `--once`). Its two other `reading()` branches — a CONFIGURED endpoint, a missing export — were fired by hand and
  print their sentence; neither has ever reached the log, and no test holds them.
- **`tick.SCHEDULE_DEFAULT`'s note still says «the schedule UI is out of scope (§6)»** — false since this item; `PUT`
  preserves it verbatim rather than re-spelling the file's prose. `results/loop*.log` is gitignored beside the tick's
  state — a clock; `tests/test_serve.py` skips itself where the `serve` extra is not installed.
- Carried from s46: no test for `promote_signals.py`, `thread_population`/`threads_read` or the gate's third state; it
  never clears its output dir; the fold map has no guard ((pp) 2(a)). The sibling readers' two defects are CLOSED by
  (i).
- Carried unchanged: `spend_promo_c3.json` says `"tolerance": 0.05` where the FLOOR closed it; 19.828 vs 3.369 s/page;
  `promo_projection_c2.json` not reproducible from its producer; no test asserts `cap_from`/`{leg}`/`{STEP}-s4`, the
  arm selector, `graded()`'s `rows`, P1/S2/README, the ties.
