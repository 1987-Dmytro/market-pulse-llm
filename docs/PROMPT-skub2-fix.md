# PROMPT-skub2-fix — the four verdicts land, the B′ registration writes ($0)

> Authority: SPEC §3.17 (14). Light contract, one pass. $0, no paid calls.

## The team lead's four verdicts (dictated; full-page reads on 16 images)

| # | post | key | verdict | mechanism |
|---|---|---|---|---|
| 4 | 4360 | `raw:svoia-liniia` | **b** | non-dairy watchlist item (fish p2, tea p3, zefir p4, oil p5, pate p6 — every page read) |
| 9 | 4391 | `raw:svoia-liniia` | **b** | non-dairy watchlist item (mayonnaise p1, cereals p5) |
| 28 | 4508 | `raw:svoia-liniia` | **b** | non-dairy watchlist item (crab sticks/dough p2, drink p3, sweets p5) |
| 29 | 4508 | `raw:try-vedmedi` | **b** | non-dairy watchlist item (dumplings p2, with price boxes) |

Final decomposition checksums the applier must assert:
**a=11 · b=16 · c=2 · pending=0**, total 29.

## Steps (one session)

1. Team-lead docs commit, unedited (`docs/SPEC.md` -8 block, this file,
   `docs/STATUS.md`); enumeration gains `sku-b-ratification-8`.
2. Apply the four verdicts through the existing applier path;
   `results/sku_miss_decomposition.json` re-stamped with the final
   counts; `b_prime_denominator.final` becomes non-null.
3. `write_sku_prereg_b2.py` now RUNS: `results/sku_pilot_prereg_b2.json`
   BESIDE v4 — gold **37 pairs / 10 posts** (5 emptied posts = R3
   precision probes), cap **$0.65** per (14)(e), B1/B4/B5 readings
   quoted from (14), the three instrument-v2 pins (parser module sha,
   serving pin v2, live registry), bars verbatim byte-equal. Its own
   commit, before any skub2-run artifact.
4. Driver constants set together per the Dv167 rule: cap $0.65, phase
   `skub2`, ledger `results/spend_skub2.json`, registration → B′; the
   constants-coherence test re-pointed. (Dv208 paid here, not in the
   run.)
5. Projection re-stamped against $0.65 (corners as computed, now with
   headroom); preflight re-driven (pins move); `make check` green;
   checkout table; Deviations Dv211+; report appended as `## Fix` to
   `docs/reports/skub2-prep.md`; chat gets only the path.

## Do NOT

No paid calls; sealed artifacts and v1–v4 registrations untouched;
team-lead files commit-only; never `git add -A`; vault tail → its own
final commit.
