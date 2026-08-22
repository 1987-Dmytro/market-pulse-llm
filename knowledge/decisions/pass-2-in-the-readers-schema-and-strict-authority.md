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

## r2 — the ruling (з), the 75 owed, and a parser no report-only field can refuse

**The operator's ruling of 2026-08-22 (day), verbatim from `docs/STATUS.md` «Открытые решения»
п. 1 (з):**

> **РУЛИНГ 22.08 (день):** `pass2-signals r2` — докупить 75 тредов, кап **$2.50** (арм по максимуму
> смока × разброс подов); альтернативы (кап $2.00 с армом по строкам; стоп → LoRA) отклонены.

**75 and not 74.** The 74 rung S′ never authorised, plus `@matusi_ukr:22303` — F2 — whose reply was
ANSWERED by r1's pod and REFUSED by r1's parser. A refused reply is a transport outcome and not a
verdict, so the thread is owed. The four replies that parsed are COPIED into r2's out-file and never
re-bought: decoding is greedy and pass 1 answered 200 of 200 identically across three pods, so
re-asking them would buy the same strings twice.

**Which makes the prompt text immovable, and that is the whole of r2's construction.** A carried
reply is an answer to r2's request only if r2's request is r1's request, byte for byte. So
`pass2_thread_gm4_v1`, its renderer and its blocks are r1's — imported, never restated — every unit
is re-rendered at build time and held to r1's own `rendering_sha256`, and a moved rendering is a
STOP before any pod rather than a finding at scoring time.

**A SIBLING module, not an edit.** `src/market_pulse/pass2.py` is pinned by
`results/pass2_pack.json::instruments.module.sha256`, and that pack is pinned by r1's sealed record;
r1's own test re-runs the pack builder and compares. One character in that file turns `make check`
red on a closed paid session's artifacts. The contract states the rule for the gate — «if r1's
pinned bytes stay untouched, otherwise a sibling (say which)» — and the same rule decides the
module, the gate, the runner and the scorer. All four are siblings and all four say so.

**Report-only means it cannot refuse — by construction.** Every field the record marks report-only
is read through a tolerant reader that runs the PINNED validator that owns it and repairs only where
that validator raises, recording `unreadable` beside the value. The domains are never
re-implemented. The reply's refusal set is CLOSED at six: a relabel · an id that was not in the
request · a signal citing no comment · a reply about another thread · an unbalanced or unreadable
object · a domain violation on a SCORED field. What «scored» means is read off the scorer and not
asserted — `scorer.reader_signal_found` compares evidence, `subject_type` and `aspect` and says in
its own docstring that `signal_type` and `subject_id` are deliberately NOT compared.

**A ceiling derived instead of aliased.** r1 aliased pass 1's 12 000 characters, a number sized for
a request whose prompt is ~2 300; pass 2's is 5 480 and the widest unit renders to 11 856 — 144
characters of headroom, 1.2 %. r2 derives its own from what this stack can PROVE: the widest prompt
the READER serving config has been observed to serve (`@matusi_ukr:22272`, 4 510 prompt tokens,
`finish_reason: stop`, under the same `serving.output_tokens` reservation of 4 000), converted at
pass 2's own worst measured density of 3.4523 characters per prompt token → **15 569**. No record on
this stack carries a context length for the model, and the derivation says so rather than importing
a number from outside.

**The rate is registered, so there is no rung to decide it.** `ceil(58.07 × 1.67) = 97 s/thread` —
the smoke's MAXIMUM times v2's measured pod-class spread over three pods. The MAX and not a
row-weighted fit: the population's widest unit carries 26 filtered rows against the smoke's widest
EIGHT, so a fit over the five smoke points extrapolates 3.25× beyond its own range on exactly the
units most likely to be slow. r1's row-weighted arm would have said GO; this registration declines
to bet on it and publishes both.

**And the carried rows created a class of defect the review had to find by driving.** Four rows sit
in the out-file before the pod exists, and every inherited rung that COUNTS ROWS then answers a
different question than it thinks: `watch`'s boot branch is `if not cleared and not answered`, so
rung 3 could never fire; `first_reply_after_launch` returns 197.6 s measured on r1's pod; the rate
rung 4 multiplies by 75 would be a blend of two pods; and the recovery clause would refuse this
session's FIRST create. The rule that came out of it: **rungs 3, 4 and 5 count the rows THIS POD
bought; rung 7 counts the whole file.** Neither count is wrong — using one where the other belongs
is.

## r2's outcome — 79 of 79, all three bars scored, and what the carry proved

**The run.** Pod `dusd807citw8d7`, RTX 4090 EU-RO-1, create `2026-08-22T12:07:23Z` → delete
`12:41:44Z`: **2 061 s = $0.42365** of a $2.50 cap. 75 threads bought at **23.760 s/thread mean**
against 97 charged — **0.245 of the charge**. Rung 7 GO: 79 answered, 79 parsed, **0 refusals, 0
relabellings, 0 sha mismatches, 0 unbalanced replies**, carried 4 / bought 75 with no disagreement.

**The bars, scored for the first time.** Bar 1 **4 of 5 cases and 6 of 7 signals** — the only miss
is F2a, registered UNREACHABLE before the pod because pass 1 labelled its only cited row
`сеть_ритейлер` and the gold reads a `молочный_бренд` signal from it. **F2 was ANSWERED and READ
this time** and still does not take the case, which is the expectation proving itself: the RED is
about AUTHORITY and never was about the transport. Bar 2 **3 of 4**, exactly the value computed at
$0 before the pod. Bar 3 **RED at 2 signals**.

**Bar 3's two signals are this line's own question arriving as a measurement.**
`@VARUS_channel:10366` is a giveaway thread the reference calls noise; pass 2 was handed its four
`сеть_ритейлер` rows, dropped none of them, and read `похвала · service` from «Класні призи, все
хочу)» and `жалоба · service` from «Де умови?!». Both are about the chain's giveaway and neither is
about dairy. Under STRICT authority that is the honest outcome — pass 2 may drop a row and here it
judged there was something to say — and the bar is 0 and reads RED at 2. It was registered in
advance as «the case this bar is really about».

**The FP reading ruling (б) bought.** DROP **21 of 281 = 7.47 %**, and `сеть_ритейлер` drops at
**11.86 %** against `категория_личное`'s 6.28 %. `subject_doubt` **15 of 260**, and its highest rate
is **`молочный_бренд` at 21.4 %** — a café, a stationery brand and a throat spray, all labelled a
dairy brand by pass 1. r1's five threads doubted only `категория_личное`; over the population the
smallest and most valuable class is where the precision problem is.

**What the carry proved, and it is the reading to keep.** `@matusi_ukr:22303` is the one thread BOTH
pods answered — r1's parser refused its reply, so r2 re-bought it — and the reply came back
**byte-identical**: 815 characters, the same sha256, 304 completion tokens, 15.801 s → 15.934 s.
Greedy decoding on the same request gives the same string on two different pods. That is the
empirical answer to «may four paid replies be carried into a new registration», and it is the only
SIZE-FREE pod-class reading this stack owns: **1.008**, against the 1.67 the registration borrowed
from pass 1.

**And what Dv702 was worth.** r1's parser, driven over r2's out-file, refuses **52 of 79 threads —
65.8 %**, every one on `per_comment.note is not a non-empty string`. r1's F2 refusal was not a
fluke; it was the MODAL outcome. Two thirds of the population would have come back unreadable and
the run would have bought a verdict nobody could compute. One structural rule — a report-only field
may not be able to refuse — was worth 52 threads.

**Three things the r2 construction learned that the ADR did not have.**

1. **A tolerant reader can MOVE a refusal instead of removing it.** Nulling every repaired field
   satisfied the parser and broke the consumer: `prompts._reader` guarantees six report-only fields
   are non-empty STRINGS, two of them are `Counter`-sorted downstream, and one of those consumers is
   a SEALED file. The repair has to satisfy the CONSUMER's contract and not only the producer's.
2. **A run that carries rows it did not buy has two counts and every rung has to declare which.**
   Rungs 3, 4 and 5 count what the POD bought; rung 7 counts the FILE. Four different rungs read the
   wrong one before the review; the fatal one was `fingerprint`, which made `watch`'s boot branch
   dead and meant rung 3 could never fire.
3. **A review of a FROZEN tree is a different instrument.** r1's five lenses returned 3 confirmed
   and 12 refuted, and every refutation named the commit that had just fixed it. r2 committed D0′
   first, gave every lens the sha, fixed in one commit, and ran a SECOND pass on that sha asking a
   second question — did the fix open something. 10 of 11 confirmed, 8 of 8 closed, and 19 further
   distinct defects **inside the fixes**, one of them fatal.

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
   built so that nothing it can contain costs a thread — and r2 makes it structural: a CLOSED
   refusal set, and every other field read through the pinned validator that owns it and repaired
   where it raises.
6. **A run that carries rows it did not buy has two counts, and every rung has to say which.** The
   pod's rungs count what the pod bought; the transport bar counts the file. A carried row is
   evidence, not work, and no rate may average one in.
7. **A pinned file is not edited to grow a parameter.** The sibling is the construction: load the
   pinned module, re-bind what changed, and name the re-binding in the record. r2 does it four
   times — module, gate, runner, scorer — and the gate's own docstring lists which globals move and
   why each one had to.
8. **A repair satisfies the CONSUMER's contract, not only the producer's.** A field's TYPE is part
   of what the next stage was promised, and «it is report-only» says nothing about what may be
   written into it. Every repaired non-nullable string keeps a string, and the census beside it is
   what makes «unreadable» and «absent» two readings.
9. **A carried reply is legitimate only if the request is byte-identical, and r2 measured that
   rather than assuming it.** The prompt did not move, every unit was re-rendered to r1's own
   `rendering_sha256` at build time, and the one carried-class thread that WAS re-bought came back
   byte for byte. A registration that carries paid evidence forward owes that proof.

Related: [[v2-is-the-base-and-pass-2-is-not-a-one-shot-reader]] (what pass 2 may not be) ·
[[reader-programme-closed-and-the-architecture-sitting-17-08]] (the stop-rule both read) ·
[[pass1-probe-b-measured-and-the-sitting-owns-it]] (the reader gold and its bars).
