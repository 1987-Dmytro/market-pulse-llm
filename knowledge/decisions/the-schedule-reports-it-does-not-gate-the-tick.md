---
type: decision
id: dec-2026-09-02-the-schedule-reports-it-does-not-gate-the-tick
date: 2026-09-02
status: accepted
tags: [decision, promo-pulse-1, tick, verification]
---

# `data/schedule.json` reports whether a tick is due; it does not refuse one — because a gate there would make the idempotence check untestable

**Who this is written for:** whoever next reads `scripts/tick.py` and asks why a file that declares
a one-hour minimum interval does not enforce it.

**Context.** The phase spec asks two things of the loop in one sentence: «`make tick` is idempotent:
run twice on an unchanged store → zero new rows … reads `data/schedule.json` (min interval 1h,
default 6h)». Written the obvious way — read the interval, refuse a tick inside it — the two
clauses destroy each other. `make tick && make tick` is the check, the second invocation lands
milliseconds after the first, and a refusing tick would print «not due», write nothing, and let
«zero new rows» pass over **a run that never happened**. Green, and measuring nothing
([[a_prefilter_cannot_certify_the_population]], [[a_saturated_proxy_cannot_discriminate]]).

## The decision

The schedule is READ, and the reading is printed (`schedule: due — 6.00 h since the last tick, at
or past the default interval` / `not due — 0.02 h …, below the 1 h minimum`). It does not gate.
`--if-due` exists for a cron caller that genuinely wants the refusal, and it is not what `make tick`
passes.

**Why this is the honest split, not a dodge.** The interval is a property of the SCHEDULER — how
often the loop should be woken — and the tick is a $0 idempotent promotion of what is already on
disk. Running it twice in a minute costs nothing and changes nothing; that is exactly what the
check asserts. A minimum interval protects against repeated *collection*, and the tick does not
collect: it calls no model, opens no endpoint and imports no guard.

**What carries the burden instead.** The clock is `--now`, an argument, never read inside the
cooled-thread queue — so two ticks a second apart agree by construction — and the screen's export
carries no timestamp at all, which makes «unchanged store → unchanged output» a `shasum` anybody can
run. The tick's own clock lives in `results/promo_tick.json`, gitignored, because a committed clock
would dirty the tree on every run and the phase's check (l) asks `git status --porcelain results` to
print nothing.

**Consequence to remember.** The live store leaves five of the six promo tables at zero, so the live
K10 is a saturated proxy. The discriminating reading is `tests/test_tick.py`, which ticks twice over
a fixture with rows in ALL six and carries the negative control — a changed store DOES write. Quote
that, not the live run, when the check is challenged.

Related: [[one-live-raw-root-and-an-opt-in-union]] · [[the-d-cut-and-the-fourth-kind]]
