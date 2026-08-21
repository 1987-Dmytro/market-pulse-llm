---
type: decision
date: 2026-08-21
status: accepted
tags: [decision, phase6, pass1, pass2, prompt, stop-rule, architecture, census, honesty-frame]
---

# v2 is the BASE prompt of pass 1, and a per-thread assembly call is NOT the one-shot reader

The operator ruled on 2026-08-21 in the team-lead session, after the briefing, and the ruling is
registered in `docs/STATUS.md` «Открытые решения», п. 1 (а)–(д). Two of its five parts need a
record of their own: **(а)** ships a prompt whose own dev gate answered RED, and **(г)** reads the
stop-rule of 2026-08-17 as not covering pass 2. Both bind the team lead, not only the executor, and
neither can live in a contract file that a later contract supersedes.

## The ruling, verbatim from `docs/STATUS.md`

> (а) **v2 (`pass1_comment_gm4_v2`) — базовый промпт прохода-1**: следующая линия строится поверх
> него и меряется против него («до»-числа 136/200 · 38/49 на dev-200). Регистрация r2 закрыла
> итерацию промпта, не принятие измеренного; по 14 золотым v2 НЕ стрелял — и не стреляет без новой
> регистрации.
>
> (б) **Следующий контракт — (1) сквозной прогон окна-1 на v2:** проход-1 по ~1 032 платным
> комментам + проход-2 (сборка сигналов) против `docs/REFERENCE-signals-w1.md` с
> пре-регистрированным баром по F1–F5 / E1–E4 / N; ~$1–2, без обучения. Это рулинг ПОВЕРХ следствия
> регистрации r2 (v2 шипится как ПРОВИЗОРНЫЙ фильтр для сквозного замера, не как принятый
> деливерабл). Цель замера — узнать, какая ошибка прохода-1 (мусор 45% / пропуски 20%) ломает
> проход-2.
>
> (в) **Затем — (4) LoRA «рассуждение→метка» поверх v2 с (3) синтетикой как армом B** одной
> регистрации; цель обучения задаётся результатом (б). Альтернативы, отклонённые в ревью: (4)
> первым (инструмент оценки 22 строки, цель обучения не известна); стоп и упаковка.
>
> (г) **Дизайн прохода-2 = (A):** один LLM-вызов на ТРЕД по комментам, которые проход-1 пометил
> «наши»/`сеть_ритейлер`, с entity-контекстом → сигналы `{тип · субъект · аспект · цитаты msg_id}`;
> **рулинг по ADR 17.08: такой вызов НЕ «однопроходный читатель»** (не делает per-comment
> атрибуцию, не отвечает на всё по сырому треду) — записать в ADR, связывает обе ступени. (B)
> детерминированная сборка отклонена (тип сигнала недоступен по построению).
>
> (д) **Два контракта, один платный прогон на каждый:** `pass1-window` (проход-1 по окну-1 на v2
> байт-в-байт, бар — транспорт и полнота, кап **$1.50**) → `pass2-signals` (построение + прогон,
> бар F 5/5 · E 4/4 · N 0 по референсу, кап **$1.50**). 14 золотых строк в окне отвечаются как
> часть популяции: их сверка с голдом — отчётная строка ценза с названной множественностью,
> НИКОГДА не бар и не «v2 взял 12/14». ADR рулинга — в промпте `pass1-window`.

## (а) — a prompt that failed its own gate is shipped as a PROVISIONAL filter

`pass1-fewshot r2` registered one question and answered it: does the codebook clause plus five
labelled neighbours fix the mention-vs-about confusion on the rows we care about? The dev gate was
`our_v2 − our_base ≥ 10` over 49 rows and it came out **+7 — RED**, with the second inequality
(overall agreement ≥ −5) met at +49 ([[pass1-fewshot-closes-at-the-ssh-dead-man]]).

The ruling does not overturn that. It says the registration closed **the prompt ITERATION** and not
the acceptance of what was measured, and it ships v2 for a purpose the dev gate never asked about:
to be the pass-1 filter of an end-to-end measurement whose bar is transport and completeness. The
distinction is load-bearing in both directions.

* **What v2 IS now:** the base every next line is built on and measured against. The «before»
  numbers are fixed at **136/200 overall and 38/49 on the «our» rows, on dev-200**, and any line
  that claims an improvement over v2 quotes those two.
* **What v2 is NOT:** an accepted deliverable. Its dev gate is red and stays red. The reading that
  matters more than the verdict is r2's own decomposition: v2's gain is bought almost entirely on
  `не_наш_рынок` (12 → 46), the base's error was **silence** rather than mis-attribution (13 of the
  14 «our» rows v2 gained were rows the base answered `None`), and the mention-vs-about cell —
  `не_наш_рынок → категория` — is the ONE cell v2 did not move: 22 at the base, **24** under v2. The
  clause bought answers, not that discrimination.
* **The fourteen were never fired at.** r2's attempt was not spent — no gold row was answered, and
  `results/pass1_fewshot_shot.jsonl` does not exist. That attempt belongs to a bar on the fourteen
  and stays intact.

## The fourteen inside a production population — a census row with its multiplicity

`pass1-window` answers all 1 032 payable comments of window-1, and the fourteen gold rows and
probe-b's sixty-four are INSIDE that population. They are answered because they are in it, not
because anyone is taking a shot. The ruling fixes what may be said about the result:

> их сверка с голдом — отчётная строка ценза с названной множественностью, НИКОГДА не бар и не «v2
> взял 12/14».

The multiplicity is **four**: the base (pass1-probe-b, 9/14), arm A of the LoRA line (lora-b, 9/14),
v2 registered for a shot it never fired, and now v2 inside a production pass registered for
transport. A reading taken on rows this program has already looked at three times is a reading and
never a bar. `results/prereg_pass1_window.json` carries the sentence in `return_to_the_operator` and
the record's `what_this_run_is_not` says the same thing about the whole run. The same holds for the
larger report-only readings the same run produces — the 650 labelled rows and the 450 outside
dev-200. Bigger samples, still readings.

**A bar on the fourteen needs a NEW registration** with its own attempt, its own pre-declared
threshold and the operator's word.

## (г) — the stop-rule of 17.08 does not close pass 2, and this is the reading

[[reader-programme-closed-and-the-architecture-sitting-17-08]] closed a specific instrument and said
so in terms:

> The stop-rule closes **the one-shot prompt reader**: one call, one thread, every question answered
> at once, cured by editing the prompt. A per-comment classification pass is the rule's own named
> successor — the sentence says the next step is an architecture sitting and names «two passes»
> among its options, so pass 1 IS that step and is not «a v6 of the same kind».
>
> **This record binds the TEAM LEAD as well as the executor: no new one-shot reader registration may
> be written.** Not under a new letter, not with a new prompt, not at a smaller cap.

Pass 2 as ruled is **one LLM call per THREAD over the comments pass 1 has already attributed**,
carrying the entity context, returning `{тип · субъект · аспект · цитаты msg_id}`. It fails the
closed instrument's definition on both of its clauses:

1. **It does no per-comment attribution.** Which comments are «ours» is decided upstream, by pass 1,
   per comment, and pass 2 never revisits it. The question the stop-rule closed — «given a raw
   thread, say which comment is about what» — is not asked of it.
2. **It does not answer everything from the raw thread.** Its input is a FILTERED set of comments
   that already carry a label, plus a bought entity block. A one-shot reader's input was the thread.

What makes this a ruling rather than an observation is that the closed instrument was closed by a
stop-rule that binds the team lead, so only the operator can say where its boundary runs. It has
been said, and it is recorded here so that a later contract cannot re-open the question by quietly
reclassifying the same call. **The consequence is symmetric:** if a future pass-2 design starts
doing per-comment attribution from the raw thread, it IS the closed instrument and this record
refuses it as surely as it permits the ruled one.

## (д) — two contracts, one paid run each, and where the money sits

| contract | what it buys | bar | cap |
|---|---|---|---|
| `pass1-window` | pass 1 over all 1 032 payable comments of window-1 on v2, byte for byte | transport and completeness: answered 1 032/1 032 · 0 sha mismatches · ≤ 10 parse refusals | **$1.50** |
| `pass2-signals` | the assembly, built and run against `docs/REFERENCE-signals-w1.md` | F 5/5 · E 4/4 · N 0 | **$1.50** |

The step `pass1-window` opens with no pods of its own: `pass1-fewshot`'s $0.397133 of pods belongs
to ITS step ledger, which is closed, so the step cap and the contract cap are the same $1.50.
`pass2-signals` is priced from THIS run's census — the per-thread table of comments pass 1 labelled
`категория_личное` / `молочный_бренд` / `сеть_ритейлер`, their characters and each thread's entity
block — which is why the pack records the denominator that table comes out of.

## What (д) bought, measured — `pass1-window` closed RED and the reason is a rate

The first of the two contracts ran on 2026-08-21 and **closed RED at rung 7: 131 of 1 032 answered**
(`docs/reports/pass1-window.md`). One pod, 845.0 s, **$0.173694 of the $1.50 the ruling gave it**.
Rung 4 deleted it because the projection left the 6 500 s hard stop; the cap was never near it
($1.3948 of $1.50), and the recovery clause then refused on seconds, so there is no second pod.

**Nothing about (а), (б) or (г) is disturbed by this.** No bar on v2 was taken, no gold row was
scored against a threshold, and the fourteen the pod did reach — five of them, four agreeing — are
a census row with the multiplicity this record already binds. The transport was clean on every row
it bought: 131 replies, 131 parsed, 0 sha mismatches, 0 refusals, 0 duplicates.

**What failed is a number, and it is the number the next registration has to fix.** The run was
priced at 3.4075 s/call — r2's measured 2.726 over 200 dev rows on pod `8tpx8lf05n6skc`, times a
1.25 margin. The pod that ran it, `xpz3zb7yxus5cw`, went at **4.498 s/call: 1.65× the sample.**
Request width (+1.14 %), a cold leg (r2's own base leg ran 2.199 cold), the prompt, the card model,
the datacenter and the population were each eliminated with numbers. A rate measured on one rented
pod does not describe another, even at the same card model in the same datacenter, and this is now
a reading the programme owns rather than a surprise it can have twice.

**The consequence for (д), and it is the operator's to take.** `pass2-signals` is priced «from THIS
run's census», and the census covers **24 of 127 callable threads — 91 filtered rows of an unknown
whole**. The per-thread shape is sound and the extrapolation is not the executor's to make. The 901
comments still owed need their own registration with a rate charged on the POD CLASS: at 4.498 s/call
they are ≈ 5 600 s ≈ $1.15, which does not fit under this registration's stop once pod 1's seconds
are counted, and a hard stop that would carry the whole run at the measured rate is $1.5556 —
OUTSIDE the $1.50 cap. So the next step is a cap-and-rate decision together, not an amendment to
this one.

## The acceptance's correction — comment identity is the PAIR, and it binds pass 2

The team lead's acceptance of `pass1-window` (21.08, evening) found that the report-only readings
were scored on the msg_id alone. A msg_id is unique per CHANNEL, not per window: seven of them inside
the 650 labelled rows live in two threads each, and five had exactly one twin answered, so five
comments the pod never reached inherited a namesake's reply. Corrected, pair-keyed:

| reading | as first reported | corrected |
|---|---|---|
| the 650 labelled rows | 69 / 117 · «our» 23 / 49 | **68 / 112 · «our» 21 / 49** |
| the 450 not in dev-200 | 35 / 65 | **34 / 64** |
| the dev-200 | 34 / 48 · «our» 21 / 49 | unchanged — it carries no collision |
| the fourteen | 4 of the 5 reached | unchanged — the gold pairs carry no collision |

Neither `scorer.reader_comment_agreement` nor `gate_pass1_fewshot.py::leg_table` was touched: both
are pinned by sealed records, and the census now hands the named instrument one THREAD at a time,
where a msg_id is unique. Details and the pair-by-pair reconciliation are in the ADDENDUM of
`docs/reports/pass1-window.md`.

**What this binds.** *Comment identity anywhere in window 1 is the pair `(thread, msg_id)`.* Ruling
(г) makes pass 2 a per-thread assembly call over the rows pass 1 filtered — a table keyed on msg_id
would merge two comments of two channels into one thread's row, and the merge would be silent. The
`pass2-signals` registration says so in its own record or it is not registered.

The same acceptance found that `--pre-create-check` printed the refusal that ended the paid session
and recorded nothing. It is now an appended, recomputed gate in `results/pass1_window_run.json`, and
from `pass1-window r2` on, that guard records its verdict at the moment it runs.

## What binds, from here

1. **v2 is the base.** A line that claims to improve on pass 1 measures against 136/200 and 38/49 on
   dev-200 and says so. v2 is not an accepted deliverable and no report may call it one.
2. **The fourteen, the 650 and the 450 are census rows.** With their multiplicity named, in the
   record and in the report. Never a bar, never a headline, never promoted by a later reader.
3. **A per-thread assembly call over already-attributed comments is not the closed instrument** —
   and a call that starts attributing per comment from the raw thread is.
4. **The team lead is bound by 2 and 3** exactly as the executor is, which is the whole reason this
   is an ADR and not a paragraph in a prompt.

Related: [[pass1-fewshot-closes-at-the-ssh-dead-man]] (the r2 registration and its RED) ·
[[reader-programme-closed-and-the-architecture-sitting-17-08]] (the stop-rule this reads) ·
[[lora-b-red-and-line-b-closes]] (the line closed before this one) ·
[[pass1-probe-b-measured-and-the-sitting-owns-it]] (the base's 9/14 on the fourteen).
