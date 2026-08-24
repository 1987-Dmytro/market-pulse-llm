# PROMPT — `lora-c-run r2` (fresh session, ONE paid pod session, cap $4.00, Dv from 803)

Execute `docs/PROMPT-lora-c-run.md` AS WRITTEN, with the following amendments from rulings (н)/(о)
(`docs/STATUS.md` п. 1) and the `lora-c-armb` acceptance. Where this file and the original
conflict, THIS file wins. Read also `docs/reports/lora-c-armb.md` §3 (the header tell), §4 (the
derivation and the stock probe).

## Amendments to the original contract

1. **Scope and money (ruling (н) + armb).** Both arms exist and are registered
   (`results/pass1_sft_v3_train.jsonl` + `results/pass1_sft_v3_arm_b.jsonl`, prefix rule).
   **Pass-2 runs for the ARMS only (2 legs, not 4)** — base v2's end-to-end BEFORE is
   pass2-signals-r2's registered 4/5 · 2; base v3 takes no bar. The money block's
   `pre_pod_arithmetic` is armb's (fixed 8 885.88 s at charged rates; break-even 63.29 / 73.43
   s/step; hard stop 18 000 s). **Cap $4.00 — operator's word 24.08 on these numbers.**
2. **The card (ruling (о)): `RTX PRO 4500` 32 GB, $0.72/h secure, EU-RO-1** (the volume's DC;
   A6000 reads none there — `results/lora_c_stock_probe.json`). Register beside it: every prior
   s/call was measured on a 4090 and every s/step on an A6000 — the charged 6.14 / 97 stay the
   conservative charge, the projection rung uses THIS pod's measured rates, and the smoke's 6
   steps are also the VRAM test (an OOM at 3 072 is a KILL + STOP: `micro_batch` is frozen law
   and is not edited on a pod). If the card is out of stock at create-time, one fallback create
   on a 4090 $0.74 is pre-authorized (same rungs); anything else is a STOP.
3. **Step 0.75 ($0, before any create) — the marker fix (team-lead ruling on Dv795):** replace
   the synthetic rows' topic line with the registered constant string
   `«(synthetic training row — this thread has no post)»` — the FALSE production string
   `NO_POST_TEXT` may not appear in synthetic headers (it would teach the model that a REAL
   image-post header correlates with synthetic patterns). Re-render the 160 (the 506 prefix
   byte-identical — diff = STOP), re-run the encode census and the tell table (the new line will
   read 160/0 — that is the ACCEPTED, named confound; the false line must read 0/160), re-pin in
   the registration. `bars` untouched.
4. **Report-only addition — the marker census (~$0.05, inside the fixed part):** after arm B's
   eval leg, take ~20 E requests (drawn under a registered seed, stratified over classes) and buy
   each TWICE from arm B's adapter: as-is, and with the synthetic header block substituted in.
   Report the prediction-flip table (toward/away from `молочный_бренд`). This SEPARATES «synthetic
   did not help» from «the adapter learned the marker». Report-only, never a bar.
5. **Step 0.5 additions:** widen `check_stamped`'s whitelist to `knowledge/index.md` (team-lead
   ruling on Dv802 — it passes the registered criterion by the same AST scan; `knowledge/hot.md`
   stays OUT by name, it is a suite input; the test asserts both directions). Update the
   registration's `reachability.the_pinned_trainer_refuses_a_v3_dataset` wording to note the
   sibling trainer closes it (the block stays, its state reads CLOSED-BY-SIBLING).
6. **Order on the pod (unchanged otherwise):** boot gate → load → base v2 → base v3 → smoke 6
   steps (s/step AND VRAM) → projection rung → arm A (62) → eval A (pass-1 E-198 + pass-2 11
   threads) → projection rung → arm B (82) → eval B (+ the marker census) → pull → teardown
   proven by listing. Liveness 600 s from the LAST log line; kill-clock before the first
   milestone; recovery clause as in the original.

Everything else — bars (one attempt, all-or-RED per arm), report-only rows, the numeric session
audit, Deviations (from **Dv803**) + Process signals, the DO-NOT list — is the original contract's,
unchanged. STOP after the report for team-lead acceptance.
