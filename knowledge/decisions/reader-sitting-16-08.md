---
type: decision
date: 2026-08-16
status: accepted
tags: [decision, phase6, comment-signals, reader, cost, taxonomy]
---

# The reader sitting of 16.08: four rulings — the $20 line, instrument v3, the reader's own gate, and one word

**The sitting that answers `docs/reports/probe-b.md`.** probe-b was re-verified from the artifacts
before anything was ruled: `make check` 2 562 / 2 skipped on the team lead's own run, the bar scorer
re-run from the saved rows reproduced the verdict **byte for byte**, the 23/134/4 population and the
`ccef35fa…` digest agreed, the cloud was re-listed with a positive control (serverless `[]` · pods
`[]` · the volume visible), and the ownership sweep was clean. **probe-b is ACCEPTED.**

The target the system is measured against is now named and confirmed by the operator:
`docs/REFERENCE-signals-w1.md`, the team lead's hand reading of 15.08 — 51 candidates down to about a
dozen threads carrying a signal. The operator's standard: «the system must produce an analogous
answer».

## Ruling 1 — the cycle-2 budget line is **$20**

The line is opened by the operator on 2026-08-16. Three clauses come with it and each one is a
constraint on a different actor:

- the SPEC amendment lands **by the house manoeuvre of the next contract, BEFORE the first paid step
  is taken against the line** — the law arrives before the money, not after it;
- **Phase 4 closes at a final reading** rather than drifting;
- **the anchor is written only AFTER the balance is topped up.** Anchoring against an un-funded
  balance would produce a counter that starts at the wrong number, which is the footgun
  `results/spend_phase4.json` has carried in its own note since the phase opened.

**AMENDED THE SAME DAY, at the acceptance of `cycle2-money`.** The third clause landed in SPEC
3.23 (2) as a numeric threshold — «the first guard balance reading of $40.00 or more after the
top-up» — and the team lead withdrew it hours later: *«порог $40 … — ошибка тимлида (порог построен
на непроверенном допущении «пополнение будет новым, поверх»); снимается амендментом 3.24 … якорь
линии берётся осознанным прогоном от текущего баланса. Новых платежей НЕ требуется.»*

**The money was already there, and the artifact this contract wrote is what proves it:** the
Phase-4 ledger's closing entry carries both readings and they differ by **$19.990278** — the
operator's $20 top-up of 2026-08-15, landing after that ledger's anchor. A `≥ $40.00` floor would
have demanded a SECOND top-up nobody planned. The clause was implemented exactly as written and
shipped with tests in both directions; that is its only defence, and no test could have reached the
assumption, because the assumption was about a future payment. `CYCLE2_ANCHOR_MIN_USD` and its
refusal retire with the clause, at step 0.5 of `reader-v3-prep`.

## Ruling 2 — the reader instrument is **A+B as ONE new registration (v3)**

probe-b priced four options; the sitting takes A and B together, and as a single registration rather
than two.

- **A — container tolerance, by explicit ruling.** The parser becomes tolerant to the CONTAINER;
  **the domains stay strict**. Where two top-level objects disagree on a key, the reply is
  **REFUSED — never last-wins.** That clause is the sitting's own answer to the question probe-b left
  open, and it is what stops «tolerance» from becoming a silent repair that authors structure.
- **B — a v3 prompt**: «one JSON object», «`[]` for empty», with the reading-gap questions
  (**F1b, F1c, F2a**) put into the prompt itself.
- The instrument is then measured by **re-reading the same 23 threads for ~$0.08**, with the bars
  scored **against gold r2**.

One registration and not two because A and B move the same instrument: an ablation between them was
not bought, and the report should say so rather than imply the +6 replies are attributable.

## Ruling 3 — the varto/marker silencer is OFF for the **reader path only**

SPEC 3.21 (1)'s marker rule is a determinism hygiene for the display; probe-b showed it also acts as
a **payment gate for the reader** — four of the operator's obligatory cases were never shown to the
model at all. The sitting lifts it for that path and for nothing else:

- **the payment gate of classification and the r1 brand attribution are NOT touched**;
- the operator's word puts the reader's window-1 population at **129 threads**, and **spam/scam
  threads are not removed** either;
- **the new census cell — narrow gate · varto silencer OFF · plus-spam/scam ON — is MEASURED in
  reader-v3 and never derived.** A cell arrived at by arithmetic over two older cells would be a
  number no census on disk can reproduce, which is the whole reason the clause is written down.

## Ruling 4 — the vocabulary adjudication: «категория» ≡ «категория_личное»

The reference file `docs/REFERENCE-signals-w1.md` scores gold rows on the word «категория»; the
ratified taxonomy spells the same class **«категория_личное»**. The sitting adjudicates them as **the
same class**, and fixes how that is applied:

- **the gold is re-derived as a NAMED revision (r2) in reader-v3**;
- **the reference file itself is NOT edited** — pins do not move for a vocabulary reading;
- **the ruling lives as its own record**, which is this section.

That is the shape [[the-law-grows-inside-marked-blocks]] fixes for the SPEC, applied one layer down
to a reference: the adjudication is written where a reader will find it, and the artifact it rules on
stays where it is.

## What follows, in order

1. **`cycle2-money`** — the standing tail, these two ADR debts, the Phase-4 close, the $20 line and
   its amendment, and the guard's Dv411 family (two readings, attribution by kind, an end to a step).
2. **`reader-v3`** — the A+B registration, gold r2, the new census cell, the 23-thread re-read, the
   bars.

`prep-b` (the Сільпо / Varus / Маркетопт collection) is agreed and queued **after** the reader — the
operator's word on 16.08: «we are not finished with the comments».

Related: [[reader-probe-card-and-interface]], [[serving-latency-deferred]],
[[5c2-closed-the-sitting-and-the-shelf-life-redesign]], [[the-law-grows-inside-marked-blocks]].
