# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## Done — 06.09 s31, the PAID iteration 5, the whole runbook §0a→§7. **GREEN.**
**S2's dev loop is answered on its fifth and last run (PHASE §2).** `--score --arm dev40`, the BAR:
**subject 0.8857 ≥ 0.80 · signal 0.8667 ≥ 0.75**, 139 rows from **40 of 40** leg-A units, **0
unparsed**; `grade_promo_signals.py` re-derives both from the file. `--arm dev2`, the READING beside
it: subject 0.8883 · signal 0.8296 (188 rows, 40/40, 0 unparsed). Files: `results/grade_promo_dev40_
iter5.json`, `promo_dev{40,2}_{predicted,errors}_iter5.jsonl|json`, all at `15313fb`.
**Ruling (w) is answered and it was the SERVING:** the instrument never moved and
`@VARUS_channel:8647` — the 14 281-char render that OOM'd iteration 4 — came back in **313.9 s,
balanced, `finish stop`** on the 32 GB card with `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`.
**80/80 answered**, so this is NOT PHASE §6.5's incomplete reading.

## The money — the pod is gone, the line is OPEN pending billing
Pod `xt4c5osyr36ew0`, RTX PRO 4500 Blackwell 32 GB, $0.72/h, **11:20:39Z → 12:38:57Z = 4698 s =
$0.9396** of the **$1.40** cap. Guard's post-run reading: **`PROMO-ITER5 SPENT $0.9495 of $1.40`**.
Cycle 3 **SPENT $7.3933, REMAINING $1.6067** of $9.00. New whole-run rate for the next leg:
**53.6254 s/thread (max 313.867, n=80)** in `results/measurements.jsonl`.
**(y)'s same-session rule paid off:** anchor 11:06:19Z → post-run `--note` 12:39Z is **H = 1.55 h**,
so the volume's drip is `0.0079·1.55 / (0.9396 + 0.0079·1.55)` = **1.29 %**, well inside the 5 % band
— iteration 4's whole 2.73 % drift was that term at a larger `H`.

## §0a and the gates, each demonstrated
`--dry-run` → the listing read READ-ONLY **before** `--register` ($0, creates nothing): a card that
had moved would then refuse before the anchor, not after it. Card matched the record exactly.
`--register --step promo-iter5 --cap 1.40`: **FITS at the mean $0.8470 (−39.5 %)**, dear $4.8633 over
the cap and named. Record verified BEFORE the commit: cap 1.4 · `terminate_after_minutes` **116** ·
the Blackwell · «iteration 5». **Commit 1 registration (`d598573`), commit 2 pack (`782bb7f`)** —
`build_pack()` passed `committed_registration()` because s30's order was followed; the fix held in a
live paid run. `make check` at that HEAD **4323/2, FLOOR HOLDS**. §0 both listings `[]`, the
session's ONE pre-pod ledger line. §1 `STOP_AT` 13:16:14Z (the registered 116 min binds, not the
$1.6067 remaining); gpu-id READ from the record; rung 1 **GO** (price and card both registered,
backstop $1.392 ≤ cap). §2 dead-man 500 s from the record, port at **27 s**. §3 pod HEAD == Mac HEAD,
clone clean, volume warm. §4 detached. §5 smoke 3/3, `--smoke` **exit 0**. §6 fetch 80, delete,
both listings `[]`, `--close-segment`, POST-RUN `--note`. **`make check` again at `15313fb`: ruff
clean, SLICES COVER, 1000+2030+1293 = 4323 passed / 2 skipped ≥ 4266, §8 (l) empty.**

## Next — the settlement retry, then the team lead's move
1. **Start ritual of the next session, read-only walk FIRST:** repeat
   `--close --tolerance 0.05 --expect-ms 4698000 --until '2026-09-06T12:45:00Z'`.
2. Then the holdout-2 leg, once the stop below is answered.

## Open stop — TWO, both for the team lead / operator; the tree is clean and nothing is in flight
1. **The line `promo-iter5` did NOT settle and that is a DELAY, not a decision.** `--close` REFUSED:
   the billing walk covered **1 072 748 ms of 4 698 000** and a PARTIAL walk is a third state.
   RunPod posts 30–40 min late (billing had only $0.2156 of the $0.9495 delta). No action is owed —
   it is retried at each session's start until it settles.
2. **GREEN ⇒ the holdout-2 attempt is now due, and the executor cannot start it alone.**
   **Question:** the team lead owes the holdout-2 reference drawn **blind** from the PRODUCT
   population (channels r2, PHASE v9 §2) — and PHASE §6.2 makes the holdout attempt a STOP notice to
   the operator before it is spent. The $0.90 of §6.1 is a FENCE, so it is re-priced at that step's
   own `--register` on the pace measured today (**53.6254 s/thread**) and on the day's own offer.
   **Tree state:** clean, `15313fb`, `make check` 4323/2, no pod, no serverless, `promo-iter5` open
   at $0.9495/$1.40 pending billing; cycle 3 REMAINING $1.6067 — enough for holdout-2 and c3 ($0.50).

## Named, not built (the phase file forbids adding what it did not ask for)
- **(y)4 risk 3 FIRED, exactly as predicted:** `--close-segment` printed `verdict OVER`,
  `spent_all_segments_usd 2.874083` — it summed ALL SEVEN segments since iteration 1 against this
  line's $1.40. A false field nothing gates on (the money is the guard's line, $0.9495). Fix =
  filter by `anchored_at`. **This and (y)4 risk 2** (an exception with an EMPTY message reads as
  ANSWERED — `"exception" in row` + (w)3's test) **are the FIRST $0 items after this session.**
- **§6.5's $0 fit proof** — the smoke's longest unit stood in for it and this time it passed.
- **Contradiction, named per PROCESS v2.1 (the standing law wins, no stop):** the runbook takes three
  guard `--note`s while the operator's line is «one ledger line per session». PHASE **v13 §6.1**
  mandates the post-run reading and `--close` writes the settlement — §0's note is the session's
  ledger line; the other two are the close's own machinery.
- **Watcher note, not a repo change:** `pgrep -f promo_dev_pod_runner.py` also matches the probe's
  own shell and the launcher wrapper, so it can never read 0 — liveness was pinned to the runner's
  PID instead. Nothing in `scripts/` was touched; the runbook's `pgrep` line is prose, not a gate.
**No test, pin, guard or ledger was added this session.**
