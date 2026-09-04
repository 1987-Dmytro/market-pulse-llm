# PROGRESS — promo-pulse-1 (executor's one file: done / next / open stop, ≤60 lines)

Ruling 03.09 (e) made this file the phase's state; §8 of the phase file stays the DONE list.

## The money, live
`promo-dev-loop`: **$0.7493 of the registered $2.4469** (iteration 1 $0.5254 + B $0.2239), **$1.6977
left**, the step OPEN — **this session spent $0, no pod, no ledger line**. Cycle 3: **$4.5265 of
$7.00, REMAINING $2.4735** (balance delta, the pessimistic reading; billing still says $4.2920, 30–40
min late). c3's cap under (l)4 = `min($0.50, REMAINING − $0.30)` = **$0.50**; holdout $0.30 untouched.

## Done
- **03.09 s9 iteration 1** ($0.4358): signal 0.8792, subject 0.7929 — **0.8214 re-read under the
  v1.1 gold**; **s10/s11 A(1)**; **04.09 s12 «A-rest», $0** — ACCEPTED by (k); **s14 «sources-r3»,
  $0** — ACCEPTED by (l)1; **04.09 s15 B, $0.2239** — pod `ej1dxfcpe0etff`, 1089 s, 56/56 units, one
  boot, ACCEPTED by (m)1: **signal 0.8854 HOLDS (bar 0.75) · subject 0.7500 RED (bar 0.80)**, the
  `…_iter2.*` files never rewritten. Plateau counter **0 of 2** ((m)3: signal gained, and the 122
  delivered comments went 25 → 17 misses; subject fell by transport, not by law).
- **04.09 s16 — the stop is CLOSED by (m) and the repair is written and green ($0).** Team-lead files
  committed by path first (`b220acc`); `make preflight ARGS='promo_dev_pod_runner promo_prompts'` —
  **0 of the touched paths pinned by any record**. The repair as (m)2 wrote it: `balanced_prefix`
  reads the fence off with `promo_prompts.unfence` FIRST, dispatches on the shape SECOND, and returns
  a prefix of the emitted text (fence opener kept — what `run` persists and `parse` unfences again);
  `promo_prompts.fold` reads a bare array as the rows it is (`about` singular = one row), an element
  that is not an object still counting as «not an object». **ONE test, both directions** (§4 v5) and
  it IS §6.5's $0 drill — object · array × fenced · unfenced, driven through `close_arrays_too` +
  `stops_here` (the wiring the `StoppingCriteria` applies, not the bare function), three negative
  controls: the shipped rule still cuts the fenced array short, an object comes back byte-for-byte
  from it, an unclosed array is `None`. 5 passed; ruff clean; the added `unfence`+`index` costs the
  stop **+5.7 ms over a whole 6.6 KB array generation** (+0.4 ms on the longest paid leg-A answer).
- **The paid record does not move:** re-parsing `results/promo_dev40_iter2.jsonl` with the fold gives
  the SAME 122 `about` rows and the SAME one parse failure at `@VARUS_channel:6216` ((m)1).

## Next
**Iteration 3, ONE session as B was ((m)5), starting at its re-emission:** the registration
(`iteration: 3`, the runner's sha among the pins, three money numbers pre-declared before the smoke,
cap = the step's remainder as the guard prints it) → buy → K8 → the error table naming the diff
((c)3). Subject ≥ 0.80 → the holdout NOTICE is the open stop, END; RED → the error table, END; «c3»
as (l) 2–4 either way. The runbook is off every paid `…_iter1.*` — its `_iter2` paths and the smoke
units `7187/9006/6009` repoint first.

## Open stop
None — (m) answered both: the repair is a NEW instrument bought under the NEXT number, no plateau.

## Named, not built (the standing prompt forbids adding what the phase did not ask for)
- **`extractor_version` cannot carry iteration 3's identity:** it is `sha256(rendered prompt)`
  (`promo_prompts.py:194`) and a transport/parser repair leaves every one of the 40 identical.
  (m)5's «the runner's sha among the pins» is what separates them — and the re-emission must pin
  `promo_prompts.py` BESIDE the runner: half the repair is in each and `check_law` covers neither.
- **`pod.main` installs `close_arrays_too` on `market_pulse.reader_v5` and never lifts it**, so by
  file order the attribute is patched when a later test reads it; the new test takes the shipped rule
  from a reload and puts back what it found. Not fixed — nothing asked for it.
- **Leg B is closed by (m)4:** 16 of 16 posts answered `[]` in BOTH iterations; iteration 3 buys leg
  A only, S4's leftover posts staying without a position row. **Gold covers 140 of the 208 comments**
  in the 40 threads, so fewer rows can score better (iteration 2 wrote 122, iteration 1 151).
- **A unit test for `resolvable()` with a `+` handle is AUTHORISED by (l)1**, not yet written.
- **`project()` prices its KILL against the whole step cap, never the step's remainder.**
- **`check_law` compares `codebook_version` only**; **`committed_registration()` ignores
  `pinned_inputs`** — checked by hand in s15, all five held. **(k)2** holds the near-quote «Шикарно…»
  and the codebook doc's 11 quotes to the law FREEZE. **c3 stays as (l) 2–4 wrote it**;
  `@ON_LINE_MO` after c3, `1925810730` unaddressable.
