# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## The money, live — read BY HAND from the guard today, never carried from a record
Cycle 3 **REMAINING $1.8312** of $7.00 (`scripts/runpod_guard.py`, read 05.09 — unmoved: no pod existed this session
either). `promo-holdout` has spent **$0.00**: own ledger `results/spend_promo_holdout.json`, cap **$0.90** ((q)3); c3
follows at ≤$0.50, the volume is deleted after it. `promo-dev-loop` settles at $1.159076 and its ledger is **still
OPEN** — stop (b). **No ledger line this session:** nothing was bought and nothing under `results/` was written.

## Done
- **05.09 s20 (`7378326` lead files · `f879bf9` `7a7d90c` `858ead0` code · `31f9461` runbook):** «holdout-prep» at $0 —
  emitter and grader take the holdout as PARAMETERS (`--part {dev,holdout} --gold --step --cap`), `use_part()` binds
  BOTH halves, `own_rate()` retired the borrow onto its own 88.772 s mean / 201.967 s max, `--register` REFUSES without
  the gold pin, dev leg byte-identical (`5510dd2b3098cdd3…`). `make check` 4320 passed, 2 skipped, exit 0 at `858ead0`.
- **05.09 s21 — the ONE item was the «next» line and it is BLOCKED. $0, no pod, nothing written.** What s20 filed as a
  §5 stop is a **§0a** stop: `register()` writes `decision_table` **unbranched on `PART`** (`promo_dev_pass.py:860`,
  beside an `out_of_scope` that DOES branch), so `--register --part holdout` — the FIRST command of the paid session —
  would commit the DEV loop's bands into the holdout's pre-registration record, carrying the authority string «ruling
  03.09 (b), quoted and not moved» and the wording «run iteration 1 now». `--pack` then refuses on an uncommitted or
  dirty registration, so that record is sealed by the very commit §0a asks for.
- **Checks — `register()` built IN MEMORY and never written; `git status` on `results/` clean, shown.** (1) Rung 0 on
  the holdout: `fits=True` on the mean $0.8420, `dear_fits=False` at $1.8999 against cap $0.90 — (q)3's verdict, duly
  issued. (2) The emitted `decision_table` is the dev table verbatim, printed. (3) **`project()` never reads those
  bands:** `bands` is a display field; the verdict is the LITERALS `0.80` / `1.20` at `promo_dev_pass.py:1275`, and its
  KILL is `not worst["fits"]`. (4) Solved for the flip: **`project()` KILLs once the smoke's slowest of three exceeds
  95.340 s/thread** — and that unit is the population's LONGEST thread by the runbook's own §5 construction, on an
  instrument whose measured MEAN is already 88.772 s and whose measured MAX is 201.967 s ($1.8425 → KILL).
  (5) **Stop (b) does NOT block the shot:** ledgers are per-step (`runpod_guard.py:307`), no sibling-closed assertion
  exists, and `promo_dev_pass.py` never reads the dev ledger — so the runbook's premise «`promo-dev-loop` is closed and
  a closed step cannot carry a new run's spend» is FALSE today while its conclusion holds, for a reason its prose misnames.

## Next — §0a of the runbook, then §1–§7, then «c3» by (l)2–4, then the volume. **BLOCKED at the FIRST command.**

## Open stop — (a) blocks the shot; (b) is an open ledger, named. Nothing was written for either.
- **(a) The holdout has no decision table of its own, and the block starts at `--register`, not at `--project`.** Both
  the record's table and the gate's arithmetic are the dev loop's: `GO ≤ $0.80 · GO-THEN-STOP ≤ $1.20 · NO-GO above`
  (the $1.20 edge sits ABOVE the $0.90 cap) with KILL on the max corner over the cap, which (q)3 already ACCEPTS at
  rung 0. **Question — it needs a SHAPE, not only numbers, because `project()` decides on literals and would ignore new
  bands written into the record: (i)** name the holdout's bands AND authorise editing `project()`'s arithmetic — today
  `project()` is UNTOUCHED and a threshold not in the plan is a scope change — **or (ii)** rule that the holdout's money
  gate is rung 0's FITS plus the cap as the hard stop (`--terminate-after`), so §5's band gate is NOT run on this shot.
  (q)3's own `issued_rule` leans at (ii) without settling it. I have picked neither and written neither.
- **(b) `--close` on `promo-dev-loop` REFUSED and I did not force it.** It settles $1.159076 against the ledger's own
  recorded $0.866700 — **33.7% off**, outside the runbook's 5%. The right-hand side is `recorded_reading()`, the last
  `--note`, ALWAYS taken BEFORE the last pod, so a multi-pod step can never close inside 5%. **Question:** does the
  tolerance read the run record's segments (its $1.153372 is 0.49% away) or a number the team lead names? Picking one
  to make it pass is greening a guard, so the step stays OPEN and named.
- **Tree state:** `96be763` + this file; every path committed, no pod existed, every RunPod call this session a $0 read.

## Named, not built (the phase file forbids adding what it did not ask for)
- **The record's `decision_table` and `project()`'s literals are two thresholds for one decision** — whichever way (a)
  rules, satisfying it in the record alone leaves the gate deciding on the dev numbers.
- **(q)3's expected $0.37–0.58 is BELOW what the instrument's own pace prices:** the mean corner is $0.8420 and
  iteration 3's realised $0.493744 scaled by text rows (140 → 188) is ≈$0.64 — not a KILL, the cap is the hard stop,
  but optimistic. **The `priced` corner (ONE dead-man recreate) leaves $0.0007** — a second pod is no free retry.
- **The holdout branches of `rung_0`, `register`, `use_part` and `build_pack` carry no test** — §4 forbids adding one
  and the $0 contacts are their only exercise · `prep()` still calls its count `draw.dev_threads` and `threads_note`
  still reads «3 smoke + 40 dev-40» on the holdout (the key is pinned by `tests/test_promo_dev_pass.py:61`; renaming is
  §8 (j)) · `items[:3] == pack["smoke_ids"]` is pack-vs-pack · `pod.main` never lifts `close_arrays_too` from
  `reader_v5` · `committed_registration()` ignores `pinned_inputs` · `check_law` compares `codebook_version` only ·
  `resolvable()` with `+` is AUTHORISED by (l)1 · **gold covers 140 of 208** · `1925810730` unaddressable.
