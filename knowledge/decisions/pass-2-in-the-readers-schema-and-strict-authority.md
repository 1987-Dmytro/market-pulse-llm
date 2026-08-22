---
type: decision
date: 2026-08-22
status: accepted
tags: [decision, phase6, pass2, prompt, schema, stop-rule, architecture, honesty-frame]
---

# pass 2 answers in the reader's schema under STRICT authority, and the fourteen keep their sixth look off a bar

The operator ruled on 2026-08-21/22 and the ruling is registered in `docs/STATUS.md` «Открытые
решения» п. 1 (г), (д) and (ж). Three of its parts need a record of their own, because each one
binds a later contract that could otherwise re-decide it quietly: **what pass 2 may do to a pass-1
label**, **which output schema it answers in**, and **what may never be scored as a bar**.

This record is the second half of [[v2-is-the-base-and-pass-2-is-not-a-one-shot-reader]]. That one
said what pass 2 is NOT — not the closed one-shot reader, because it does no per-comment attribution
from a raw thread. This one says what it IS, and what it is forbidden to become on the way.

## The rulings, verbatim

> (г) **Дизайн прохода-2 = (A):** один LLM-вызов на ТРЕД по комментам, которые проход-1 пометил
> «наши»/`сеть_ритейлер`, с entity-контекстом → сигналы `{тип · субъект · аспект · цитаты msg_id}`;
> **рулинг по ADR 17.08: такой вызов НЕ «однопроходный читатель»** … (B) детерминированная сборка
> отклонена (тип сигнала недоступен по построению).

> (д) **Два контракта, один платный прогон на каждый:** `pass1-window` … → `pass2-signals`
> (построение + прогон, бар F 5/5 · E 4/4 · N 0 по референсу, кап **$1.50**). 14 золотых строк в
> окне отвечаются как часть популяции: их сверка с голдом — отчётная строка ценза с названной
> множественностью, НИКОГДА не бар и не «v2 взял 12/14».

Ruling (ж) is the one this record exists for, and `docs/PROMPT-pass2-signals.md` states it in the
authority block: **STRICT authority — pass 2 never relabels a subject; it may DROP a comment as
noise; a report-only `subject_doubt` records disagreement.**

## STRICT authority, and where it stops being a sentence

Pass 2 receives comments that already carry a `subject_type` decided by pass 1. Three things follow
and all three are enforced by `market_pulse.pass2.parse_pass2` rather than asked for in prose:

1. **A `subject_type` in `per_comment` must equal the pass-1 label of that comment.** A reply that
   changes one is a parse REFUSAL — `pass2.RelabelError`, a subclass of `prompts.ParseError`, so the
   gate counts it as a refusal by its own cause and never folds it into «other».
2. **A signal's `subject_type` must be the pass-1 label of one of the rows it cites.** One of them
   and not all of them: pass 1 labelled each comment on its own, so a signal read from two comments
   of two subjects is a signal about one of the two, and demanding both would refuse F1(б)'s shape
   for a reason the ruling never gave.
3. **A signal that cites NO comment is refused.** The reader's `from_post: true` is not offered by
   pass 2's text, because strict authority keys on the pass-1 label of a CITED row: a signal citing
   none carries a subject nothing authorises, and it is the hole the relabelling refusal would
   otherwise be walked around through.

**What pass 2 MAY do is DROP.** A filtered comment it judges not to be discussion at all goes into
`noise` and out of the signals. That is the one judgement about a comment this pass makes, and the
DROP table — by thread and by pass-1 label — is the false-positive reading of the filter that ruling
(б) bought the whole end-to-end run to get.

**And it may DOUBT, on the record and nowhere else.** `subject_doubt: true` plus one line of reason
changes nothing downstream. It is the FP/FN reading, and its being report-only is what keeps it a
reading rather than a relabelling wearing a different name.

**The consequence is symmetric, as the earlier ADR's was.** A future pass-2 design that acts on a
doubt — that re-decides a subject, however it is named — has left this ruling, and this record
refuses it as surely as it permits the ruled one.

## The reader's schema, and the two lists pass 2 does not answer

Pass 2 answers in the v5 reader's schema, so `prompts._reader_object` (the container repairs the
2026-08-16 sitting ruled) and `prompts._reader` (the domains) apply unchanged — the exact pair
`prompts.parse_reply` binds for a reader task — and `scripts/score_reader_probe_b.py` scores it
against `results/reader_gold_w1_r2.json` through `market_pulse.scorer`. Nothing is forked.

`src/market_pulse/prompts.py` is NOT edited. It is pinned by 38 sealed records, so the pass-2 text
and renderer live in a new module, `src/market_pulse/pass2.py`, task `pass2_thread_gm4_v1`.

Two of the reader's four lists are not asked of the model:

* **`entities` is BOUGHT, not answered.** The list a pass-2 verdict carries is the thread's entity
  block from the v5b/v4/topup verdicts, placed into the payload between the parser's two halves. The
  prompt never mentions it. Two measured reasons: the block is 1 288 characters on
  `@VARUS_channel:10613` and 653 on `@matusi_ukr:22303` — two of the five threads whose seconds rung
  S′ multiplies by the 74 that follow — and a verbatim-copy slip in a quote would refuse the whole
  thread and take bar 1's hardest case down with a transcription error.
* **`from_post` is not offered**, for the strict-authority reason above.

**The consequence has to be said plainly, because it is a bar: bar 2's value is knowable at $0.**
`results/prereg_pass2_signals.json` registers it — **3 of 4, RED** — before a pod exists. E2, E3 and
E4 are held by the inherited block; **E1's thread carries no filtered row, so pass 2 never calls it.**
The bar is not moved for that; the reachability is named, and the number is reported as «held» and
never claimed as pass 2's own.

## Reachability is a property of the POPULATION, and pass 2's is not the reader's

`results/reader_gold_w1_r2.json::reachability` answers this question for the reader probe's cell.
Pass 2's population — the 79 threads of window 1 carrying at least one filtered row — answers it
differently **in both directions**, and the registration carries the table:

| case | in the reader probe | in pass 2 | why |
|---|---|---|---|
| E1 `@matusi_ukr:22242` | unreachable (silenced) | **unreachable** | callable, but 0 filtered rows |
| E4a/E4b `@mandziak:3684/3689` | unreachable (silenced) | **reachable** | pass 1's window is a wider cell |
| F2a msg 580124 | reachable | **unreachable** | pass 1 labelled it `сеть_ритейлер`; the gold says `молочный_бренд` |
| F5a msgs 579379 / 579457 | reachable | **reachable** | 579457 is outside the filter, 579379 is in, and the scorer matches on ANY evidence intersection |

**F2 is expected RED by construction and the bar stays at 5 of 5.** A bar lowered to what the layer
can reach measures nothing. The expectation is registered so that the RED reads as the measurement
it is, and the scorecard names the pass-1 label of every row it cites, so a strict-authority miss
and a reading miss never look alike in a bar's zero.

## The fourteen: no bar, and this is their SIXTH look

`per_comment` is pass 1's pass-through under strict authority. A threshold over it would be the
sixth time this programme has looked at the fourteen gold rows: the base 9/14, arm A 9/14, v2
registered for a shot it never fired, v2 reaching five inside r1's killed pass, v2 over the complete
window at 11/14, and this. **Bar 4 is NOT registered.** Point 2 of the earlier ADR's «What binds»
applies unchanged, and it binds the team lead as well as the executor.

## The money shape this ruling forced, and why it is a precedent

Ruling (д) gives `pass2-signals` a $1.50 cap. **This prompt has no rate** — pass-1 replies were ~50
tokens and a pass-2 reply is a list of signals — so the registration could not price the run it was
authorising. What it does instead is the shape a later contract should copy:

* the **SMOKE** (the reference's five flagship threads) is priced at an assumed ceiling of 120 s/call
  — the ONE assumption in the record, named as one — for a worst case of 3 000 s = $0.6667;
* `money.arithmetic.total_seconds` is therefore **the smoke's worst case and not the run's**, which
  is what rung 0 authorises a create against;
* **rung S′** computes `charged_full = max(1.5 × smoke_mean, smoke_max)` from the smoke's own seconds
  on the same pod, projects the remaining 74 against the 6 600 s hard stop, RECORDS its verdict, and
  only then writes the token the pod is waiting for. The knife edge is **48.6486 s/call**;
* **a STOP is a registered outcome**, not a failure: the five replies are scored, the rate is
  measured, and the remainder returns to the operator as a cap-and-rate decision with a number in
  front of it.

**And the smoke is not a sample.** The five F threads carry 30 of the 281 filtered rows — 6.0 rows a
thread against the population's 3.56 — and v5b's two slowest leg-A threads are two of them. The rate
they measure is charged on the remaining 74 as registered, which is the SAFE direction, and the
row-weighted reading is published beside it and never gates
([[a_reproducible_probe_can_be_unrepresentative]]).

## What the registration BOUGHT — rung S′ said STOP at 5 of 79

The paid session ran on 2026-08-22. One pod, `9rquj8p0lelct3`, **526.0 s = $0.108122** of the $1.50
cap; ssh in 38 s, boot in **139.5 s** — a new floor for this stack — and 135 s of pre-generation
against 1 100 charged. `docs/reports/pass2-signals.md` carries the arithmetic.

**The measurement the registration could not price is now a number.** A pass-2 decode:
58.07 · 15.80 · 40.85 · 56.46 · 56.70 → **mean 45.582, max 58.07**, which is **0.53 of what the
one-shot reader took on the same five threads**. Nothing on this stack had it before.

**And rung S′ refused the remainder, on the `1.5 × mean` arm.** `charged_full = 68.373`, projected
6 876.9 against the 6 600 s stop, over by 276.9 — **3.74 seconds a call**. Three readings sit beside
that verdict and all three belong in this record, because the next registration is a cap-and-rate
decision:

* the **live** knife edge was **64.63** s/call and not the registered 48.6486, because the pod
  reached the decision at 517.3 s of create-elapsed rather than the ~1 700 the worked arm assumes;
* the **max arm alone** (58.07) would have passed with 6.5 s a call to spare — it is the `1.5 ×`
  multiplier, applied to a mean drawn from the five richest threads, that closed it;
* the **row-weighted arm**, computed live and gating nothing, predicted the remaining 74 at
  **27.485 s/call** and 3 851.2 s, and **would have said GO**.

So the STOP is correct under the law as registered and is, on this evidence, a STOP about the
SAMPLE. Point 4 of «What binds» held — the authorisation was the smoke and the rest was a rung with
a recorded verdict — and the design's own honesty clause is what makes the reading available.

**Strict authority held on every reply that parsed: 0 relabellings.** And `subject_doubt` did the
job ruling (б) bought it for — 4 of 23 `категория_личное` rows doubted, each with a reason, one of
them the АТБ/творог row that IS the mention-vs-about cell v2 did not move (22 → 24).

**One refusal, and it is a rule for the next registration.** `@matusi_ukr:22303` — F2 — died on
`per_comment.note is not a non-empty string`: the model wrote `"note": ""` for a row it did not
doubt. That is the THIRD report-only field found to carry whole-thread refusal power, after
`subject_doubt` and an omitted `subject_type` — both caught at $0 by the five-lens review — and the
first to fire. **A report-only field may not be able to refuse. Build it so it cannot.**

## What binds, from here

1. **Pass 2 never relabels.** A reply that does is a refusal by cause; a design that does is the
   closed instrument under a new name, and [[v2-is-the-base-and-pass-2-is-not-a-one-shot-reader]]
   refuses it.
2. **A pass-through list is reported as inherited and never claimed.** Where its value is knowable
   before the run, the registration carries the value.
3. **No bar on the fourteen.** Sixth look, still a census row, in this report and in its acceptance.
4. **A registration that cannot price its run buys the measurement and registers the guard.** The
   authorisation is the smoke; the rest is a rung with a recorded verdict, never a plan. And the
   guard must publish the arm it did NOT use: a STOP that comes out of the sampling rather than out
   of the rate is only visible if the honest reading was computed beside the binding one.
5. **A report-only field may not be able to refuse.** Three were found with that power in one
   registration and the third one fired. A field the contract says changes nothing downstream is
   built so that nothing it can contain costs a thread.

Related: [[v2-is-the-base-and-pass-2-is-not-a-one-shot-reader]] (what pass 2 may not be) ·
[[reader-programme-closed-and-the-architecture-sitting-17-08]] (the stop-rule both read) ·
[[pass1-probe-b-measured-and-the-sitting-owns-it]] (the reader gold and its bars).
