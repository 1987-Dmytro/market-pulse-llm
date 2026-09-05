# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## The money, live — read BY HAND from the guard today, never carried from a record
Cycle 3 **REMAINING $1.8312** of $7.00 ($1.97 on the evening of 04.09; the volume drips ≈$0.24/day). `promo-dev-loop`
settles at **$1.159076** of own resources and its ledger is **still OPEN** — the authorised `--close` REFUSED, stop (b).
`promo-holdout` is a NEW step: cap **$0.90** ((q)3, the operator's), spent **$0.00**, own ledger
`results/spend_promo_holdout.json` and run record `results/promo_holdout_run.json`; c3 follows at ≤$0.50. **No ledger line
was written this session** — the close refused before its write and both ledgers are byte-unchanged.

## Done
- **05.09 s20 — team-lead files committed by path (`7378326`):** ruling (q), PHASE v7, STATUS 05.09, the (q) stop-pattern
  review, and the **holdout-40 gold** — 188 rows, sha256 `6fa804880d5d14db…`, byte-for-byte the sha (q)7 names.
- **05.09 s20 — «holdout-prep», (q)5's ONE item. $0, no pod, no registration written.** The emitter and grader take the
  holdout as PARAMETERS (§4): `--part {dev,holdout} --gold --step --cap`. `use_part()` binds the module's file constants
  once at the entry point — both halves, so the holdout owns its prep, registration, pack, run record and step and **`dev`
  is the default**: every reading taken before (q) still means what it meant. `own_rate()` RETIRES the borrow ((o)4) onto
  this instrument's own **88.772 s mean / 201.967 s max** (n=3), the SLOWEST pod it ran on, read from
  `measurements.jsonl` and never typed. `rung_0` issues (q)3's verdict: a dear corner over the cap is issued FITS on the
  MEAN corner with the cap as the hard stop, the dear one staying in the table, priced and named. `--register` REFUSES on
  an absent gold; the smoke's rate row takes the PART's own name so the holdout's rate never joins the dev population
  that priced it. The runbook is off every `_iter3` path onto `_holdout`, smoke = the HOLDOUT's own three.
- **Checks, all shown.** (1) `--dry-run --part holdout` → 40 threads, 261 283 chars, gold 188 rows, the MEASURED rate, the
  bound. (2) The refusal BOTH ways — an absent gold prints «gold missing -> no record», `--register` on it writes
  nothing, exit 1. (3) `grep -n _iter3 scripts/runbook_promo_dev_1.md` → nothing. (4) **The dev leg is byte-identical:**
  `promo_dev40_prep.json` re-emits at `5510dd2b3098cdd3…`, the sha the registration PINS. (5) **`make check` 4320
  passed, 2 skipped, exit 0** at `858ead0` — s19's own count, so no test was added and none changed (floor 4266).
  (6) **$0 dry contacts on `--register` and `--pack`, into the scratchpad — nothing under `results/` moved.** They
  priced the table (cheap **$0.8420 −6.4%** · priced **$0.8993 −0.1%** · dear **$1.8999 +111%**), proved the pack
  renders 40 leg-A units whose ids ARE the registration's population, smoke first and none of them a dev-40 thread, and
  caught three defects now fixed — a `None` floor crashing the print after the write, the rate row landing under the dev
  name, and `use_part("dev")` a silent no-op — two of them reachable only on the paid path.

## Next — the paid shot, §0a-§7 of the runbook; then «c3» by (l)2-4, then the volume. **BLOCKED by stop (a).**

## Open stop — two questions the ruling does not settle; nothing was written for either
- **(a) `--project`'s decision table is the DEV loop's and it KILLs the holdout by construction.** Its bands are 03.09
  (b)'s absolute dollars (`GO ≤ $0.80 · GO-THEN-STOP ≤ $1.20 · NO-GO above`) — the $1.20 edge is ABOVE the $0.90 cap — and
  its KILL is «the MAX corner over the cap». The holdout's max corner is $1.8999 against $0.90, which (q)3 already ACCEPTS
  at rung 0: `--register` says FITS and `--project`, minutes later on the same pod, says KILL. **Question:** does (q)3's
  «FITS on the mean corner, the cap as the hard stop» extend to `--project`, or does the holdout get its own bands? A
  threshold not in the plan is a scope change: `project()` is UNTOUCHED.
- **(b) `--close` on `promo-dev-loop` REFUSED and I did not force it.** It settles at **$1.159076** against the ledger's
  own recorded reading **$0.866700** — **33.7% off**, outside the runbook's 5%. Its right-hand side is
  `recorded_reading()` — the last `--note`, ALWAYS taken BEFORE the last pod — so a multi-pod step can never close inside
  5%, and the dev loop's own runbook line was never runnable. The settled figure is sound — the run record's $1.153372 is
  0.49% from it. **Question:** does the tolerance read against the run record's segments, or against a number the team
  lead names? Picking one to make it pass is greening a guard; the step stays OPEN and named.
- **Tree state:** every path committed — `7378326` lead files · `f879bf9` `7a7d90c` `858ead0` code · `31f9461`
  runbook · `032b69d` knowledge; no pod existed and every RunPod call this session was a $0 read.

## Named, not built (the phase file forbids adding what it did not ask for)
- **(q)3's expected $0.37–0.58 is BELOW what the instrument's own pace prices**: the registered mean corner is $0.8420
  and iteration 3's realised $0.493744 scaled by text rows (140 → 188) is ≈$0.64 — not a KILL, the cap is the hard stop,
  but optimistic. **The `priced` corner (one dead-man recreate) leaves $0.0007** — a second pod is no free retry.
- **The holdout branches of `rung_0`, `register`, `use_part` and `build_pack` carry no test** — §4 forbids adding one and
  the $0 dry contacts are their only exercise · `prep()` still calls its count `draw.dev_threads` on the holdout, pinned
  by `tests/test_promo_dev_pass.py:61` (renaming it is §8 (j)), so `part` sits beside it · `items[:3] ==
  pack["smoke_ids"]` is pack-vs-pack · `pod.main` never lifts `close_arrays_too` from `reader_v5` ·
  `committed_registration()` ignores `pinned_inputs` · `check_law` compares `codebook_version` only · `resolvable()`
  with `+` is AUTHORISED by (l)1, not written · **gold covers 140 of 208 dev comments** · `1925810730` unaddressable ·
  (k)2 and `@ON_LINE_MO` are the team lead's now.
