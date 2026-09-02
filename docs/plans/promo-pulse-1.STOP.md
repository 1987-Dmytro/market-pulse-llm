# STOP — promo-pulse-1, 2026-09-02

**Stop-point:** a design fork the plan does not settle. Beside it, unchanged: waiting on the labels (`docs/labels-promo-dev.jsonl`, `docs/labels-positions-50.jsonl`)
— K6, K8, S9, S10 blocked either way.

**The fork.** The 01.09 (later) ruling's two halves cannot both hold while a paid leg runs. The cap is raised (`CYCLE3_CAP_USD = 7.00`, ledger `note`, commit
`981202b`); the ruling also says «anchor unchanged», and `enforce()` refuses on a balance above the anchor — `$14.26 > $4.48`, `CYCLE 3 SPENT $0.2139 of $7.00 ·
REMAINING $6.7861`, **exit 1**. Rung 0 (`--step promo-pulse-1 --step-cap 3.20`) exits 1 and writes no step ledger, so S4 cannot start. That refusal is the module's
documented invariant; re-anchoring is the operator's.

**The question.** May `runpod_balance_at_cycle3_start` move to $14.26 while `anchored_at` stays at `2026-09-01T06:34:08+00:00` (so the billing walk still counts the
$0.2139 spent)? One number, one file. At $7.00 the programme fits: $3.1563 + $2.50 + $0.30 = $5.9563 — nothing over the ceiling.

**Tree:** clean at `97e84e6`, `make check` 4 266 passed · 2 skipped. Nothing bought, no rung fired. S12–S14 and S5's draw landed, all $0. Evidence:
`docs/reports/promo-pulse-1.md`.
