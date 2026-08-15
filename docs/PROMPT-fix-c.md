# PROMPT — fix-c (row surfaces carry the badge depth only; $0, micro)

**Baseline:** fix-b closing `make check` 2 437 passed / 2 skipped; record HEAD.
**Ruling:** operator, 2026-08-15 («бейдж везде»), closing fix-b finding (1).

## Step 0 — tail + amendment 3.22

Commit the standing tail by path (verify live `git status`; this prompt arrives untracked). Land
**amendment 3.22** by the house manoeuvre — block (3.19/3.20/3.21 marker convention, index entry
INSIDE the block) + `tests/test_sku_prereg.py` enumeration + `write_prereg_5c2.BLOCKS_TODAY` +
green suite, ONE commit. Verbatim block content:

1. Row-level promo surfaces (drill-down rows and any per-row rendering) carry the depth from the
   PRINTED badge only, absent when no badge was printed. The arithmetic (price-pair) reading lives
   exclusively in window aggregates, where no row's own promo price sits beside it. Operator ruling
   2026-08-15, closing the fix-b finding: `promo ÷ (1 − arithmetic depth)` reconstructs the
   extracted old price, which 3.17 (3) and 3.18 (7) keep off every surface.

## Deliverable — one seam, rebuilt

The 6a producer's `position_row` drill-down rows: `depth` = badge reading (`printed_pct / 100`),
absent otherwise; never the arithmetic reading. Rebuild `pulse.db` → export → page. Extend the
fix-b test: every DRAWN drill-down position row's depth equals its badge or is absent — asserted on
the committed page's embedded rows. Determinism, embedded==committed, convergence 902/902 and the
poisoned guards stay green. No other surface moves; sealed anchors untouched; never `git add -A`.

## Verify · Report · Read-back

`make check` tail pasted; one previously-inverting row (e.g. `promo 12.9 · depth 35.47%`) shown
before/after FROM the built page. Report `docs/reports/fix-c.md`, `docs(report): fix-c`, path only
in chat; Deviations Dv373+, cause tags, Process signals ≤5. Read-back (one line each): (1) which
depth reading may sit beside a row's promo price; (2) the four moving parts of the 3.22 manoeuvre.
