---
type: decision
date: 2026-09-05
status: accepted
tags: [decision, promo-pulse-1, s21, s22, money, holdout, records]
---

# The holdout's money gate is rung 0 FITS plus the cap as the hard stop — the band gate never runs (ruling 05.09 (r), option ii)

**Team lead's ruling, taken on the executor's stop of s21 and spent the same day in s22.** The dev
loop's §5 band gate (`GO ≤ $0.80 · GO-THEN-STOP ≤ $1.20 · NO-GO above`, ruling 03.09 (b)) could not
be carried onto the holdout: its KILL is «the MAX corner over the cap», and the holdout's max corner
is over the cap **by construction** — rung 0 prices it at $1.8999 against a $1.10 cap and issues
FITS on the measured mean $0.8420 anyway. Applied unchanged, `--project` would return KILL on a run
its own registration had just issued as FITS. The ruling kept the gate that was priced and left
`project()` and its literals untouched. Related: [[2026-09-05]],
[[the-sealed-file-does-not-grow-it-gets-a-sibling]], [[the-law-grows-inside-marked-blocks]].

## Why the record, not only the gate, had to change

s21 stopped at `--register`, one command earlier than s20 had predicted the block. `register()`
re-used the population by parameter but left the record's **decision-bearing fields** on the dev
leg, so `--register --part holdout` — the first command of the paid session — would have sealed the
dev loop's bands and the authority string «ruling 03.09 (b), quoted and not moved» into the
holdout's pre-registration, and `--pack` refuses on a dirty registration, so the very commit §0a
asks for is what would have sealed it. PHASE §4 v8 now states the general rule: every field of a
re-used producer's record that states a decision branches on the leg, or the emitter refuses.

**Four named, seven found.** The ruling enumerated `decision_table`, `authority`, `out_of_scope`
and `phase`; two of those already branched. Auditing the built record turned up seven that did not:
`decision_table` (plus a new `why_not_the_dev_bands` pricing the dev gate's KILL against this
record's own dear corner), `authority`, `re_emission`, `gates.3_hard_stop`, `rung_0.amendment`,
`population.leg_a.smoke.rule`/`.prefix`, and `population.leg_b.closed` — plus `step.cap_rule` and
`threads_note`. An enumeration in a ruling is a starting point, not the list
([[a_patch_list_closed_by_enumeration]]).

## What it cost and what it bought

The shot ran under the new gate for **$0.296617** of the $1.10 cap: pod `pcu2fqc7ebwfcw`, 1443 s,
40 of 40 units, 0 unparsed. The pod ran **3.4× faster** than the rate it was registered at (25.826
s/thread measured against 88.772), so the dear corner that did not fit was never approached — the
1.5–2.3× host spread that (o)4 and (q)3 priced for, running the other way for once.

The reading: **signal 0.7958 HOLDS (bar 0.75), subject 0.7181 RED (bar 0.80)**, against the dev
bar's 0.8714 / 0.9104 taken by the byte-identical instrument. By (r)5 that ends the shot either
way — a red bar answers S2 with a number rather than moving the gate.

## The debt this ruling created

`write_measurement()` is called **only** from the `--project` branch (`promo_dev_pass.py:1538`).
With the band gate off this leg, no `promo_holdout40_seconds_per_thread` row ever reaches
`results/measurements.jsonl`, and `own_rate()`'s own docstring promise that «the holdout's own smoke
WRITES under `promo_holdout40_…`» is orphaned. Nothing reads that row today, so nothing breaks; the
pace survives in the replies' `seconds` field and in `results/promo_holdout40_pod.log`. But a future
leg priced through `own_rate()` still reads the DEV row — 88.772 s where this pod measured 25.826.
