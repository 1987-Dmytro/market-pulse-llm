# STOP — promo-pulse-1, 2026-09-02

**Stop-point:** a frozen file that would move — cycle 3's anchor. Beside it, unchanged: waiting on the team lead's labels (`docs/labels-promo-dev.jsonl`,
`docs/labels-positions-50.jsonl`), which block K6, K8, S9 and S10 either way.

**THE QUESTION — one, and it takes yes or no.** May `runpod_balance_at_cycle3_start` in `results/spend_cycle3.json` move off `4.4799665639` to the balance the guard
reads at that moment (≈$14.24 today, falling $0.2333/day with the volume), while `anchored_at` stays `2026-09-01T06:34:08+00:00` so the billing walk still counts the
$0.2139 already spent? There is no second option for me to weigh and nothing to design: that file is written once by law — «delete or regenerate this file and the
counter restarts at today's balance» — and the guard says in its own words that re-anchoring is an operator decision, not a script's.

**Why it is the only thing left.** The ceiling was raised exactly as the 01.09 (later) ruling says (`CYCLE3_CAP_USD = 7.00`, ledger `note`, `981202b`), and that
changed nothing: `enforce()` refuses on a balance above the anchor, so rung 0 (`--step promo-pulse-1 --step-cap 3.20`) exits **1**, writes no step ledger, and S4
cannot start. That refusal is the module's documented invariant, not a defect, and weakening it is not mine. At $7.00 the money is there the moment the anchor is:
$3.1563 + $2.50 + $0.30 = **$5.9563**. Tree clean at `97e84e6`, `make check` 4 266 passed · 2 skipped, nothing bought, no rung fired; S12–S14 and S5's draw landed,
all $0. Evidence: `docs/reports/promo-pulse-1.md`.
