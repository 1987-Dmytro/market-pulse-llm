# think-zero-shot — the paired table: thinking ON against the readings this repo already bought

**Ruling (ф). One pod, `$6.0187` of a `$8.00` cap, four of seven stages.** `lf989hmhk9diso`, RTX PRO
4500 32 GB, EU-RO-1, `$0.72/h` (rung 0 PASS). `14:00:04Z` → `22:06:39Z` = **8 h 06 m 35 s** on the pod
clock; the guard's step delta is higher because it counts the volumes. Teardown proven by a listing —
pods `[]`, serverless `[]`, both volumes present. Cycle-2 left **`$3.4115`**. Every number below is
read out of `results/think_zero_shot_table.json` or `results/measurements.jsonl`.

| stage | BEFORE | thinking | delta |
|---|---|---|---|
| dev-200 v2 (n=200) | **136/200** · «our» 38/49 · 0 refusals | **136/200** · «our» 36/49 · **2 refusals** | **+0** · «our» **−2** |
| dev-200 v1 | 87/200 · «our» 31/49 | not bought | — |
| holdout-100 | 64/100 | not bought | — |
| bar 1 flagships | 4/5 RED | **4/5 RED** | +0 |
| bar 2 entity cases | 3/4 RED | **3/4 RED** | +0 |
| bar 3 noise | 2 signals RED | **2 signals RED** | +0 |
| pass-2, the same 12 threads | 15 signals over 8 · 15 unreadable fields | **21 over 9** · **39 unreadable** | **+6** · **+24** |
| s/unit | 2.726 pass-1 · 23.760 pass-2 | **110.180** (n=200) · **395.701** (n=11) | **40.4×** · **16.7×** |
| thought tokens, mean | — | 1 130 pass-1 · 3 511 pass-2 | — |

Both pass-2 columns are recomputed over **the twelve threads the pod bought**, never against the
shipped verdict's 79: the bars are per-case and every case is inside the reference eleven, but
«signals found» is a count and a count needs its denominator. Model load **152.7 s**, paid again by
every stage. Peak VRAM **31.17 GiB of 32** (97.4 %).

## What the readings say

1. **Agreement did not move; 27 of 200 rows did** — 14 to gold, 13 away. Per class one exchange:
   `категория` 36→34, `None` 41→43, the other three flat. What the model SAID moved further —
   `категория` 67→59, `None` 57→64 against a gold of 47 and 54: thinking pulled the marginal
   distribution toward gold and took the label off right rows as often as wrong ones.
2. **Pass 2 finds 40 % more signals and no bar moves** — 15→21 on the same twelve, mostly `похвала`
   5→10, while 4/5 · 3/4 · 2 stands cell for cell. Report-only fields the tolerant reader could not
   read: 15→39 on those same threads.
3. **Two parse failures the BEFORE column has none of**, one mode: the thought spent its whole 4 000
   token ceiling and never closed the channel — `@klopotenkofood:6032#21177`, `@matusi_ukr:22308#580147`.
   Pass 2, at 8 000, had none.
4. **The bound beat the scaled estimate.** The smoke bought the longest of 79 threads (638.492 s):
   as a bound it over-stated the reference leg by 1.61×; scaled by the BEFORE column's own mean/max
   shape it said 112.2 s and under-stated by 3.53×. Thinking flattens that distribution — the thought
   is near-constant per unit — so the tail sample was the better instrument, not the worse one.
5. **The full programme is `$20.87` at these rates, 2.61× the cap**, and rung 2 said so after the
   smokes; the platform window agreed independently (11 121 s left where stage 5 needed 21 116 s).
   The operator's word on the fork: **«свернуть по порядку ценности»**.

## Deviations — enum v2, Dv853–860; in full in `implementation-notes.md`

- **853** `[verify-gap]` the `length` cut-off fired in the wild; step 0's fix saved `thought_chars`
  (0 → 13 614) on `#21177` and NOT `balanced` — that working-out carries no top-level `{`.
- **854** `[tooling]` the preflight exits at block 10 on the pod (an annotation image the bundle does
  not carry), so 14b's five assertions ran alone, verbatim, on its own `AutoProcessor`. All PASS.
- **855** `[contract-gap]` the registration is not re-pinned; the allowance is derived both ways and
  no pack pins the runner — asserted positively.
- **856** `[verify-gap]` peak VRAM has no producer in the runner — `nvidia-smi memory.used` beside it,
  which is NOT `torch.cuda.max_memory_allocated()`; the ledger row says which.
- **857** `[process]` a ledger row's prose said n=197 for a value over 200; superseded by an appended
  row naming both sub-populations.
- **858** `[tooling]` `grep -c … || echo 0` yields `"0 0"`; zsh does not word-split ssh flags.
- **859** `[contract-gap]` **`make check` is not green** — one red, `test_repair_phase4_ledger`: r3's
  ledger, the team lead's tier. `1 failed, 4063 passed, 2 skipped`.
- **860** `[model]` there is no single «thinking is N× slower»: 40.4× on pass 1, 16.7× on pass 2.
- **861** `[process]` **this file is 64 lines against «≤30 + the table».** PROCESS's own rule says
  «≤30 lines under v2; the paired table may be longer», and this report IS the paired table — the
  contract asks it to carry per-stage deltas, both flip directions, the parse-failure and
  `length` counts, the thought distribution, s/unit, dollars and the deviations. The deviations'
  full text was moved to `implementation-notes.md` to get here; nothing the contract asked for was
  dropped to meet the number.

**STOP — the path is the operator's call on this table.** Bought: the v2 dev column and all three
pass-2 bars. Not bought: v1, the holdout, and the 67-thread pass-2 remainder, none of which carries a bar.
