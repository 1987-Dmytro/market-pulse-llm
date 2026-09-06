# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## Done — 06.09 s32, «holdout-2 prep» ($0, ruling (z) item 4 + addendum 2). It ENDS at the committed dry run — no `--register`.
**Start ritual.** (z) + PHASE v15 + STATUS committed by path (`0896ba3`); s31's knowledge leftovers (`312ec89`). **Ceiling
$10.00** ((z) addendum): `CYCLE3_CAP_USD = 10.00`, `spend_cycle3.json` note appended, anchor unchanged (`6fa0a7e`).
**`promo-iter5` CLOSED at $0.9450** (`ac22645`): read-only walk FIRST (pods $0.9450 · volume $0.0097 · serverless $0), then
`--close --tolerance 0.05 --expect-ms 4698000 --until 2026-09-06T12:45:00Z` — **0.47 % off** the post-run $0.9495; the
session's ONE ledger line. The guard's own line: **CYCLE 3 SPENT $7.4179 of $10.00 · REMAINING $2.5821** (14:21Z).
**The gold landed mid-session** ((z) addendum 2, PHASE v16 — committed by path `1e89ff3`): `docs/labels-promo-holdout2.jsonl`
**112 rows / 40 threads, sha `5525ddf1…`**, committed by path with the shasum shown (`2bb9da7`), never edited.
**The item, code (`42dfd97`):** `--part holdout2` = `HOLDOUT2_FILES` (draw-2's `holdout` arm, the gold, line `promo-holdout2`,
stem `promo_holdout2`, own prep/prereg/pack/run); `use_part` binds the DRAW and `dev_threads` reads it at the call (a default
argument had frozen the first draw at import); `by_part(part, **texts)` writes every decision field per leg BY NAME and refuses
a leg without text (PHASE §4 v8); a holdout leg without `--cap` refuses before the guard is read (the verifier's bite). (y)4
risk 2: `died(row)` = `"exception" in row or truthy error`, the ONE spelling in all five readers. (y)4 risk 3: `close_segment`
sums the segments at/after the line's anchor, read from the ledger the record names (`line_anchor`); `spent_all_segments_usd`
→ `spent_this_line_usd` + `line`, `line_anchored_at`, `segments_of_this_line`; no ledger, or a closing segment stamped before
its own anchor → refuse. (w)3's ONE test extended: (e) the silent death in every reader, (f) both directions of the filter +
its two refusals, (g) the `--cap` refusal; the `staged` fixture's stub record carries the ledger field every real record has.
**The dry run (`b05bd12`):** `--dry-run --part holdout2` → `results/promo_holdout2_prep.json`: 40 threads, 40 distinct renders,
longest **10 529** chars (< iteration 5's 14 281 on this card), gold pinned `5525ddf1…` 112 rows, MEASURED **53.6254 s/thread**
(whole run, n=80, max 313.867). **Rung 0 read-only at today's offer** ($0.72/h RTX PRO 4500, EU-RO-1 High), cap $0.90, 43
threads: cheap **$0.5170 (−42.6 %)** · priced $0.5728 · dear **$2.8109 (+212 %)** → **FITS on the MEAN**, hard stop **4500 s =
75 min** — PHASE §6.2's notice figure. No `--register`, no line opened, no pod this session.
**Runbook re-pointed (`d4bc013`)** to `promo_holdout2_*`: §0a inside the paid session, the four pins of `d598573` compared to
the new record by a command (dry-tested HOLD; the three files on disk still equal `d598573`'s shas), liveness by PID.
**Verification:** a fresh 6-lens adversarial workflow (42 agents, 2 refuters per finding) over the diff — 18 findings, **5
confirmed** (4 defects + 1 nit), all fixed before the commits: the `--cap` hole; the runbook's unterminated quote and a wrong
«without --part» sentence; the prep written 4 min BEFORE the gold landed → re-run after the gold commit; a false docstring
example. Of the 13 refuted, the cheap ones were taken too (two non-verbatim quotes, the test's typed 1.46, v15 → v16).
**`make check` at `d4bc013`:** ruff clean, SLICES COVER (229 files), 1000 + 2030 + 1293 = **4323 passed / 2 skipped ≥ 4266**
(the ONE test was extended, not added — the count did not move); §8 (l) porcelain empty.

## Next — the fresh verifier, the team lead's reading, then the PAID shot
The team lead reads `results/promo_holdout2_prep.json` + HEAD `d4bc013`; §6.2's STOP notice to the operator is the figure above.
Then the paid session «holdout-2», nothing in front of runbook §0a: `--register --part holdout2 --step promo-holdout2
--cap 0.90` (FITS shown, the four pins compared) → commit → `--pack --part holdout2` → commit → `ruff` + the three slices →
§0–§7 → `--score --part holdout2` (both bars, ONE arm) → the close. Then c3 ($0.50), then the volume `mp-srv2` ((z)5).

## Open stop — NONE for the executor: the next paid step is a planned read (§6.2), the operator's notice precedes it
Tree clean, no pod, no line opened. Headroom: $2.5821 − $0.90 (the fence) − $0.50 (c3) = $1.18 before the ≈ $0.24/day drip.

## Named, not built (the phase file forbids adding what it did not ask for)
- **A cross-leg `--step`:** `--step promo-holdout2` typed WITHOUT `--part holdout2` is the DEV leg (80 threads) under the
  holdout-2 line — `--register` would anchor `spend_promo_holdout2.json` and overwrite the frozen iteration-5 record before
  `committed_registration()` refuses the pack ($0, a live anchor, a `git checkout`). A refusal on a `--step` that is another
  leg's own line is ~3 lines and not asked for; the runbook names `--part holdout2` as the load-bearing flag instead.
- **A naive `--created-at`** (no `Z`/offset) is accepted at `--open` and dies with a TypeError at `--close-segment`
  (unreachable from every real record: all eight stamps carry `Z`).
- **Import-time `ARMS = ("dev",)`** differs from `DEV_FILES`' two arms until `use_part` runs (pre-existing; harmless via `main`).
- **The dear-corner decision table on a holdout leg refuses by construction** (`by_part(dev=…)` alone): no ruling wrote that
  table for a holdout, and it is unreachable today ($2.81 ≫ $0.90). A design fork only if a holdout's dear corner ever fits.
- `results/promo_holdout2_prep.json :: phase` still reads «dev-40» — a display string of the $0 record ((r)1 accepted it so).
**No test file, pin, guard or ledger was added this session; every new refusal is a fix's own consequence or §4 v8's clause.**
