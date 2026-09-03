---
type: decision
date: 2026-09-03
status: open
tags: [decision, harness, process, promo-pulse-1]
---

# §8's PAUSE branch is unsatisfiable as worded — the evaluator agrees and still returns «not met»

**Finding, not a ruling.** Recorded because ruling 03.09 (b) already diagnosed the symptom («the
Stop-hook evaluator does not honour the PAUSE branch and blocked eight turns before the cap ended
the session») and prescribed the workaround (the executor says «STOP — /goal clear», the operator
types it). Session 6 shows the CAUSE, which is not evaluator misbehaviour but the sentence itself,
and it can be fixed by moving four words. Related: [[the-goal-loop-never-engaged]].

## The sentence

§8's PAUSE branch reads:

> ALSO met, as a PAUSE, when `docs/plans/promo-pulse-1.STOP.md` exists (shown with cat) naming one
> of: … — after the ruling lands in the rulings file, the operator re-enters this SAME predicate in
> a fresh session.

The clause after the em-dash describes what the OPERATOR does next. The evaluator reads it as a
PRECONDITION on the PAUSE, and under that reading the branch can never be satisfied: the session
that WRITES the STOP cannot already have re-entered after a ruling that does not exist yet. The
subject of the clause is «the operator», not the executor, which is the tell.

## What was measured, four times in one session

The evaluator blocked four times. Each verdict affirmed the executor's reasoning and still returned
«not met». Its own words, quoted:

- «The PAUSE branch does not validly satisfy the condition either: the condition requires … as a
  precondition, **which is logically impossible** in the session that creates the STOP.»
- «**The executor's analysis is correct on both counts.**»

So the evaluator is not misreading the state of the repo — its state report is accurate — and it is
not disagreeing with the executor. It is applying a predicate whose PAUSE branch it has itself
labelled impossible. Two sessions have now paid turns for this (01.09 and 03.09).

## The one-line fix, for the team lead who owns §8

Split the clause into its own sentence so the resume protocol stops reading as a condition:

> ALSO met, as a PAUSE, when `docs/plans/promo-pulse-1.STOP.md` exists (shown with cat) naming one
> of: … . **Resume protocol (not a condition on the above):** after the ruling lands in the rulings
> file, the operator re-enters this SAME predicate in a fresh session.

Cheaper still, and it removes the evaluator from the loop the way ruling 03.09 (b) already wants:
drop the trailing clause from the predicate entirely and keep the protocol in `docs/PROCESS.md`,
where the operator reads it and no evaluator parses it. A predicate should describe a STATE; a
protocol describes a sequence, and a sequence inside a state description will keep being read as a
guard on it.

## Why it matters beyond the annoyance

A PAUSE that cannot be signalled turns every design fork into a choice between two forbidden acts —
buying an unreviewed paid leg, or fabricating the artifact the check wants. In session 6 the blocked
branch was the ONLY correct outcome: check (e) had been triggered by the arrival of
`docs/labels-promo-dev.jsonl` and could not be met at $0 by any instrument in the repo
(`scripts/promo_dev_pass.py` has no paid path; `src/market_pulse/local_llm.py` runs on the rented
card). The executor stopped, which was right, and could not say so in a way the gate accepted.
