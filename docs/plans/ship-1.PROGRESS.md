# PROGRESS — ship-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; created at s44's start from `docs/plans/promo-pulse-1.PROGRESS.md` per ruling (nn) 4 — its DONE tail and «named, not built» carried, `next` set to «w3» per (mm) 4)

## Done — carried tail: 09.09 s43 «kk-close» ($0, ruling (kk) 5, phase promo-pulse-1)
The floor is in, `promo-c3` is CLOSED at $0.2577, the volume is GONE.
**(i)** `DOLLAR_FLOOR = 0.05` beside `MS_FLOOR`; `runpod_guard.py:911` reads
`abs(settled − recorded) > max(DOLLAR_FLOOR, args.tolerance * abs(recorded))` and the refusal names WHICH term the
run faced. `--tolerance` stays 5%. **(ii)** four rows both ways (c3's real pair CLOSES · a $0.20 gap still REFUSES ·
a $2.99 leg CLOSES at $0.10, REFUSES at $0.21); negative control: with the guard change stashed exactly one row fails.
**`make check` GREEN at `c5cad96`: ruff clean, 4330 passed / 2 skipped.** The close: `CLOSED spend_promo_c3.json at
$0.2577`, gap $0.030468 under the $0.05 floor while 5% × $0.2272 = $0.0114 — **the floor graded it, not the band**.
Cycle-3 $8.8398 of $10.00, REMAINING **$1.1602**. `network-volume delete qw4nwleanc` → listing `[]`; the ≈$0.24/day
drip is stopped. Deviation `contract-gap`: `--window all` is NOT a window id — the tick wrote `positions 1113 → 0`
with no non-zero exit; nothing was committed, the artifacts were restored and rebuilt on `w2`, porcelain EMPTY.

## Next — «w3» ($0, ruling (mm) 4 · PHASE-ship-1 §2 item 1)
**next: w3.** promo-pulse-1's «next: chain-fold» is SUPERSEDED by (mm) 4. Then «chain-fold» → «s2-promote» →
«serve-loop» (10.09), «front-1» → «front-2» → «e2e-ship» (11.09) → the operator's gate 11.09 evening (reserve 12.09).

## Open stop — NONE
**Tree at s44's start:** porcelain EMPTY after two commits by path — `c22c80f` (the team lead's ship-1 re-spec:
PHASE-ship-1 v1, DESIGN-ship-1 v1, PROMPT-standing v2, rulings (mm)+(nn), PROCESS v2.7, STATUS, PHASE-promo-pulse-1
v30) and `69e75cd` (the three hook-touched `knowledge/` files). `make check` green at `c5cad96` as above; the commits
after it move ledgers, PROGRESS, `knowledge/` and the team lead's own files only.
Cloud empty: `serverless []`, `pod list -a []`, `network-volume list []`. **$0 spent this session.**

## Named, not built (the phase file forbids adding what it did not ask for)
- **The closing record does not say which term graded it.** `spend_promo_c3.json`'s entry carries `"tolerance": 0.05`
  while the $0.05 FLOOR is what let it close ([[a_record_must_read_the_gate_its_run_will_face]]). A `dollar_floor`
  field is a ledger field (kk) 5 did not ask for — named here, not written.
- **`--window all` fails silently** (the s43 deviation): PHASE-ship-1 §2 item 1 (iii) now ASKS for the non-zero exit
  and its one test both ways, so this debt is w3's own work, no longer unasked.
- **c3's 57 positions reach no window of the store** — ruled by (mm) 2 and become w3 itself.
- **The measured/priced gap stands as s42 left it:** 19.828 s/page against the registered 3.369. No threshold moved.
- Carried unchanged: `promo_projection_c2.json` is not reproducible from its producer (its pin is the proof); no test
  asserts `cap_from`, `{leg}` or the `{STEP}-s4` contract; `tooling.md`'s «plugin disabled», the unfloored arm
  selector, `graded()`'s `rows`, P1/S2/README untested in the tick, the ties; (jj) 3's two nits stay in «chain-fold».
