# STOP — promo-pulse-1, 2026-09-01

**Stop-point:** a design fork the plan does not settle. Standing beside it: waiting on the team
lead's labels — neither `docs/labels-promo-dev.jsonl` nor `docs/labels-positions-50.jsonl` exists,
so K6, K8, S9 and S10 are blocked whatever the fork answers.

**The fork.** C2 = 3 008 pages / **$3.1563**; ceiling **$4.80**, balance **$4.48**; C3's caps $2.50 +
$0.30. $3.16 + $2.80 = **$5.96 > $4.80**, so the 01.09 ruling's even cut applies — and it has two
parameters that would be mine only by invention:

1. **C2's share.** $4.80 − $2.80 = $2.00 allocates against C3's *cap*, not its cost, which is
   unmeasurable until the labels land; at $2.00 the cut keeps **1 889 of 3 008 pages (62.8%)**.
   Name it — or say «pay $3.16 and re-cap C3 on what is left».
2. **Which pages survive inside a chain** — newest-first, per-week even, or a seeded draw. The
   first answers «what is on promo now», the second «неделя за неделей», the phase's own question.

**A defect I introduced, and closed.** Anchoring cycle 3 reddened six isolated cycle-2 tests, and
the fix for those exposed the real hole: `main()` read `CYCLE3_LEDGER` directly, walking around the
autouse redirect that Dv424 added for cycle 2, so a `--close --note` test appended «probe-b CLOSED
at $0.3132» to the LIVE line at a fixture's $22.07 balance. Restored (anchor intact, `sessions`
empty) and closed as a class, not an instance: the redirect now names cycle 3 explicitly, and
`tests/conftest.py` carries a session-scoped tripwire over all three ledgers that fails the run and
names the file whatever module the write came from. Verified by writing to the real ledger from a
throwaway test — it passes, the teardown fails. Both leaks happened because a protection listed the
lines that existed when it was written, so the watch list is re-derived from the guard's own
constants rather than restated.

**Tree:** clean, nothing bought, no rung fired. Commits `70593f4` `1da3d7e` `3a614f4` `430b16f`
`d7af842` `c09a7c8`. Numbers and evidence: `docs/reports/promo-pulse-1.md`.
