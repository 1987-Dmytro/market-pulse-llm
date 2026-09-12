# Report — `front-1` (PHASE-ship-1 §2 item 6, ruling 11.09 (tt) 3), 12.09 s50, $0

**Question.** Does the app exist, is the promo half on it, do both modes work — every number from a file it names?

**Answer. Yes, at $0, HEAD `5c47bd6`.** `frontend/` (Vite 6 · React 19 · TS 5 · Recharts 3, pinned) builds via
`make front` into `dashboard/app/`; `make serve` renders five promo tabs, and static mode is the same build,
read-only. Позиції **1 301** rows over three windows · Реакції **118** read of **678**, feed **281** · Якість S1
RED at **0.2333** against 0.90, price **0.9524** against 0.95 · Петля the windows and **$1.1602** of $10.00 — each
from `promo_screen_data.json`, `grade_positions_50.json` or `spend_cycle3.json`. `front_data.json` (sha
`f1c7c629…`) is byte-identical across two runs and the app computes no figure.

**Evidence.** `make front` green → `dashboard/app/` + `data/manifest.json` naming both shas · `npm run check` clean
· `npx vitest run` **19 passed** · five tabs read in UA and EN, both themes, at 1440 px, six screenshots in
`docs/reports/screens/` · static mode verified with `/api/status` 404 · no console message comes from the app. Six
defects were caught IN THE BROWSER and fixed in `58e2e1f` (§3's standing permission), re-measured after: a static
build missing `front_data.json :: status` came up **BLANK** and now draws the red panel; the table keyed rows on
`row_id`, which repeats for 7 rows, so one click on such a row's ⓘ opened **two** provenance panels — now one,
keyed `(carrier, row_id)`, the defect carrying the one test. The other four: `docs/plans/ship-1.PROGRESS.md`.

**Deviations.** Dv1 [process] s49 left front-1 UNCOMMITTED; s50 verified before committing — the six defects are
what that found. Dv2 [verify-gap] `tsc` and `vitest` passed over all six: no fast loop sees a rendered screen. Dv3
[spec-gap] DESIGN §7 names `generated_at`; the producer writes `data_until` — a clock would dirty the tree every
build (fork §4.2). Dv4 [process] s49's five screenshots were REPLACED (pre-fix). Dv5 [verify-gap] a 39-agent review
filed 16 findings, 6 survived verification, and **two it refuted were fixed anyway**.

**Debts.** (a) `status.money.from` names `sessions[-1]` for a block whose `cap_usd` is a ROOT key — the string is
the producer's, so the fix is the team lead's call. (b) `screen.rollup` and `depth_by_chain_and_brand` key on a
CHANNEL handle while `positions[].chain.id` is folded; folding them rebuilds the store and moves the export's sha,
out of front-1, so the fix renamed the LABEL only. (c) The producer's English strings render verbatim on the
Ukrainian UI — correct, but visible. Each is $0; `docs/plans/ship-1.PROGRESS.md` carries the rest.

**`make check`** at `210b878`: ruff clean · `pytest -q` in five slices whose union is PROVEN equal to `ls
tests/test_*.py` (231 files, no gap, no overlap, asserted before a slice ran) → 819+974+1185+770+592 = **4340
passed, 2 skipped, 0 failed** — s48's count, unmoved: front-1's tests are vitest. The commits after that reading
move only `docs/plans/` and `docs/reports/`, which no test reads; `make front` was re-run at HEAD and the §8
porcelain is EMPTY. **HEAD `5c47bd6`. $0; no cloud call was made.**
