# PROMPT — acceptance of lora-b-run (for the NEXT TEAM-LEAD session, not the executor)

**You are the team lead (Fable, /team-lead skill loaded). The previous
team-lead session closed at context limit after: accepting lora-b D0–D2 +
reader-topup (suite 3 114/2 own run), registering the operator's rulings,
and launching the ONE paid session via `docs/PROMPT-lora-b-run.md` in a
fresh executor session. The report you are accepting is
`docs/reports/lora-b-run.md`. Verify THIS file's claims against the repo —
files are the truth, this handoff is a map.**

## State at handoff (19.08 evening, team-lead readings)

- Suite **3 114 / 2** (own run). Census 10.1K under TARGET_KTOK 10.7.
- Money (own guard read): cycle-2 **$3.4171 / $20.00**, remaining
  **$16.5829**, balance $19.09; cloud pods `[]` from team-lead side.
- Gate: **max(gold14(A), gold14(B)) ≥ 12/14** on sealed gold r2, ONE
  attempt (multiplicity named in prereg), tie ships B, red → line B closed
  → sitting C. Attempt is SPENT at the first gold-row reply. Format-smoke
  failure on BOTH arms = attempt NOT spent, session returns.
- Cap **$6.00**; worst cases registered: $2.63 no-incident · $3.44 with the
  one sanctioned re-creation · **$4.40 cumulative hard stop (5.5 h)**.
- Base = 9/14, per-row verdicts in probe-b's SEALED record, never re-run.

## Acceptance protocol (the skill's VERIFY & ACCEPT, instantiated)

1. Read the report fully, then `docs/PROMPT-lora-b.md` +
   `docs/PROMPT-lora-b-run.md` + `results/prereg_lora_b.json`.
2. **Own `make check`** (Desktop Commander, background, ~9 min) — green,
   final count matches the report's named number.
3. **Prereg integrity:** the commitment blocks — `bars` ·
   `population.gold` · `instruments.prompt_sha256` · `money.cap_usd_all_in`
   · `return_to_the_sitting` — byte-identical to the accepted D2 state
   (diff via `git show`); D3a was licensed to ADD go_no_go rungs, extend
   `learn_chars` through the closing quote, and regenerate dataset digests —
   nothing else.
4. **Git-clock order:** D3a commits → prereg regen → first `pod create`
   (timestamps in the spend record / pod log) → training → smokes → evals →
   scp → delete → verdict. No training or dataset commit AFTER any eval
   artifact exists (that would be tuning after the bar).
5. **Money, own reading:** `python3.11 scripts/runpod_guard.py` — quote the
   pessimistic arm; total ≤ $6.00; every kill-clock rung's pasted reading
   present (price ≤ $0.80/h recorded · boot ≤ 450 s · milestone ≤ $2.50
   after arm A · projection-gate logs · cumulative ≤ 5.5 h).
6. **Cloud hygiene, own listing:** `runpodctl pod list -a` → `[]`; the
   guard's volume line is the positive control.
7. **The verdict:** re-derive the bar per-row — scorer output vs sealed
   gold; max() applied mechanically; each arm's eval in its OWN out-file
   (Dv560); smoke rows are TRAINING rows (check their ids against the 14
   gold ids — zero overlap).
8. **Fresh-context subagent (MANDATORY — money + gate):** hand it the
   per-row scored table + the ablation pairing (base/A/B on the same 14) +
   the kill readings vs formulas; ask it to refute. Calibrate its findings
   (act on correctness only; positive-control your own paste before
   trusting a CONFIRMED against the repo).
9. **Evidence completeness:** raw per-row replies, adapters + per-file
   hashes, loss logs, pod log — scp'd BEFORE the verdict; deletion proven
   by listing in the report AND by your own listing.
10. **Deviations** from Dv575 on the closed enum v2; Process signals; the
    ownership sweep (`git log` for docs/STATUS.md, docs/SPEC.md,
    docs/PROMPT-* — verbatim commits only); tag tally split into STATUS.
11. **Outcomes.** GREEN: ship per prereg (higher arm; tie → B); ADR checked;
    next steps to brief the operator — integrate the shipped adapter into
    the pass-1 tract, then проход-1 окна (~$1.095 генерации ПОЛ + бут) as
    its own contract. RED: line B CLOSED, no retry; brief the operator for
    sitting C (другая база) with the ablation table. NOT-SPENT (both smokes
    failed): diagnose format collapse at $0, return to the operator.
12. **STATUS.md** (team-lead file, ≤300 lines, Russian): day entry, money
    reading, queue, phase map «ты здесь» — after acceptance, never before.

## Standing debts and context (carry, do not drop)

- Index-line debts (MEMORY.md at its 150-line bar):
  `a-checker-whose-failure-is-silence`, `the-argmax-and-the-max-are-two-rows`.
- `money-anchors` contract agenda (Dv504 right-hand side, stuck walk,
  19 refused ledgers) — operator's word.
- Blind-40 option on r1 labels — operator's, non-blocking.
- prep-b queued after the reader tract; H4/H5a/H7 pilots measured at the
  phase-6 close; weekly-retro cadence.
- A team-lead SKILL delta was PROPOSED and awaits the operator's «да»
  (Names rule: «a DESTINATION is a name too» + «two lists must cover each
  other», from Dv539/Dv544) — show the diff before applying.
- Contract-health tallies to date are in STATUS «День 19.08»; the split
  discipline (spike → cut the next contract) is live.

## Rules that bit this project before (do not relearn them for money)

Numbers from artifacts, never report prose · deletion proven by listing,
positive-controlled · the scorer is the judge, never the eyeball · a
mid-phase operator ruling in the executor session is REGISTERED in STATUS at
acceptance at the latest · your verification commands are instruments —
control them before trusting an absurd answer · baselines are pasted from
`make baselines`, never recalled.
