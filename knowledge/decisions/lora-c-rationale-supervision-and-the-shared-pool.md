---
type: decision
date: 2026-08-22
status: accepted
tags: [decision, phase6, pass1, lora, prompt, registration, review-gate, reachability]
---

# Rationale supervision, one shared neighbour pool — and four things the design cannot reach

`lora-c-prep` executed at $0 on 2026-08-22. Everything below is measured; nothing here was bought.
The two team-lead review gates are **OPEN** and the registration is a **DRAFT**.

## The rulings, verbatim

> **(в) Затем — (4) LoRA «рассуждение→метка» поверх v2 с (3) синтетикой как армом B** одной
> регистрации; цель обучения — из (б).

> **(к) РУЛИНГ 22.08 (вечер) — дизайн `lora-c`:** промпт v3 = v2 + поле `rationale` ПЕРЕД меткой,
> одним рендерингом для обучения и инференса; таблица парно в четыре колонки (база v2 · база v3 ·
> адаптер A · адаптер B) на одном пуле соседей; рационали для обучающих строк пишет Claude Code по
> кодбуку и метке тимлида, тимлид ревьюит все «наши» + ~40 пограничных; синтетика ~160 (по 40 на
> класс ошибки) — арм B, тег в provenance, абляция армом A, никогда в холдаут/голд; из обучения и из
> пула соседей исключены холдаут-100 и ВСЕ строки 16 референсных тредов; **бар на арм (один
> выстрел): холдаут-100 ≥ 64 И сквозной бар 1 = 5/5 И бар 3 = 0 — все три или КРАСНЫЙ**; отчётно:
> ячейка «упоминание → категория» на холдауте (18 → ?), dev-200 (fit), 14 золотых (шестой взгляд).
> Два контракта: `lora-c-prep` ($0, с ревью-гейтом тимлида) → `lora-c-run` (один A6000, кап
> **$4.00**).

Both strings are grepped back into `docs/STATUS.md` by `scripts/write_lora_c_prereg.py::quoted()`
on every build of the registration, and a paraphrase is refused. A ruling quoted from memory is a
paraphrase with quotation marks around it.

## What was built

**Prompt v3 is a SIBLING module, and that is the answer to the contract's own question.**
`docs/PROMPT-lora-c-prep.md` asks whether `build_pass1_fewshot_packs.rendered_item` can take v3.
It cannot: it dispatches into `prompts.pass1_messages_gm4`, which raises
`ValueError("… not a registered pass-1 prompt")` for every task outside `prompts.PASS1`, and
`prompts.py` is pinned by 38 records. So `src/market_pulse/pass1_v3.py` restates the request
assembly and CALLS everything that can be shared — the v2 text, the examples validator, the
media-less-post string, the 12 000-character ceiling. The text is a strict PREFIX extension of v2's
(asserted in both directions), so the base-v2 and base-v3 columns differ by exactly one paragraph.

**`rationale` is REPORT-ONLY and can never refuse a reply.** That is pass2-r2's rule applied before
the money instead of after it: `prompts._text` refuses an empty string, and a field the record calls
report-only must not be able to cost a row its label. `parse_pass1_v3` delegates the four SCORED
fields to `prompts.parse_pass1` unchanged — legal because `_require` collects only what is MISSING,
so a payload carrying a fifth key passes it — and reads the fifth beside them into one of six named
states. [[a_report_only_field_can_refuse_the_whole_row]]

**The pool is 515, not the contract's ~430, and the arithmetic is why.** `650 − 100 − 41 + 6`: the
two exclusions OVERLAP, because six holdout rows sit inside reference threads. 8 of the 16 reference
threads carry labelled rows. The same 515 rows are both the training set and the neighbour pool, so
every leg is answered against one neighbour set and the paired table compares prompts and adapters.

**515 rationales, written here, and the check that makes them worth writing.** Every one names a cue
that occurs in ITS OWN comment, compared on whitespace-collapsed case-folded text — **501 distinct
cues over 515 rows, and 267 over the 272-row majority class.** A rationale derivable from the label
alone would leave the target a deterministic function of the class, which is exactly what line B's
adapter learned; the distinct-cue rate is the measurement that says it did not happen here.
Shapes: `коментар ПРО` 339 · `коментар ні про кого` 160 · `лише ЗГАДУЄ` 16.

**160 synthetic rows, 40 per error class, and the four classes are the ones pass 2 measured.**
Balance is 8/8/8/8/8 inside every class — spread 0 against the contract's ±2. Contamination is four
EMPTY lists on word 6-grams through `market_pulse.synthetic`, against 650 labelled rows, 100 holdout
rows, 106 reference-thread comments and the gold's own quotes. **The register was measured on both
sides rather than asserted**, and **two of six axes clear ±3** (emoji 19 % vs 19 %, lowercase
opening 6 % vs 6 %); four do not and are named — questions 8 % vs 13 %, terminal punctuation 54 % vs
59 %, median length 7 words vs 11, median characters 40 vs 68. The length gap is deliberate: the
window's tail is 40–190-word recipe posts and writing those synthetically would be a different
instrument.

**Eval set E is 200 and renders 198.** `100 + 106 − 6` — the same overlap, in the other direction.
Two legs in one pack, paired on identical instances. All 14 gold rows are inside E because they are
inside the reference threads, and they take **no bar**: report-only, the sixth look.

**The pass-2 builder reproduces r2.** `scripts/build_lora_c_pass2_pack.py --reproduce`, driven at $0
over the window's own out-files and cut from 79 threads to the 11 reference threads that carry a
filtered row, returns **bar 1 = 4 of 5 and bar 3 = 2 signals** — exactly the readings
`results/pass2_signals_r2_verdict.json` holds. Both bars read only reference threads, so the cut may
not move them, and that is now a measurement rather than an argument.

## The four things this design cannot reach — and they are rulings, not fixes

**1. The smallest class has no fifth neighbour.** The pool holds ONE `молочный_бренд` row: the 650
hold two and the holdout took the other. `build_pass1_fewshot_packs.neighbours` refuses a query
whose own thread is the only place a class occurs, because a four-example block is a different
instrument from a five-example one. So all nine pool rows of `@VARUS_channel:10367` are
unrenderable, and **the rendered training set has ZERO real `молочный_бренд` positives**; two
holdout rows of the same thread fall out of E. The exclusion the ruling itself demands is what
caused it.

**2. No v3 row fits `max_seq_len`.** `config/qlora.yaml` freezes it at 1 408 and it is pinned by
`results/prereg_lora_b.json::instruments.config_sha256`. v3's rows are 5 262–9 402 characters where
lora-b's v1 rows were 2 950 median and 4 132 max, because the five-neighbour block now carries a
rationale per example on top of v2's two paragraphs. **All 506 rows are over the ceiling at every
ratio this repo has measured** — at the MINIMUM observed tokens-per-character the SHORTEST row still
needs 1 419 of the pod's own count. Both the Mac-side drop rule and `train_qlora.encode_pass1`'s
refusal fire, on every row.

**3. Arm A has no `молочный_бренд` target at all.** The pool's single row of that class is one of
the nine that cannot be rendered, so arm A's 506 rows carry **zero** targets of it and
`train_qlora.class_weights` returns four classes, not five — `sampling_order` can never draw one.
Arm B has **32** (8 per error class) at a weight of 4.1625. **Bar 1 = 5 of 5 turns on relabelling
msg `580124` to `молочный_бренд`**, so the bar is near-unreachable for arm A and reachable for arm
B, by the same arithmetic. The bar is not lowered — it is registered per arm at 5 of 5 — and this
block is why a RED on arm A would say something different from a RED on arm B.

**4. The pinned trainer refuses a v3 dataset by name.** Two guards, driven at $0 and quoted in the
registration: `load_sft`'s task-name check and `build_pass1`'s registered-dataset-sha check. What
PASSES is named beside them — the `learn_chars` guard and the prompt-sha equality both do, so the
`+1` END-offset boundary survived being prefixed with a rationale. `train_qlora.py` is pinned live
by lora-b's prereg AND its verdict, so the remedy is a sibling and it is `lora-c-run`'s first $0
deliverable, not an edit here.

**Four neighbours does NOT dissolve the second STOP, and that is measured.** Re-rendering the same rows with FOUR examples leaves **484 of 506 over at the most favourable measured ratio and 506 of 506 at the registered one**; with ONE example 62 are still over. The cause is the TEXT, not the block: v3's prompt is **4 112 characters = 1 200 tokens at the worst measured ratio and 1 109 at the minimum**, against a ceiling of 1 408 — the prompt alone occupies 79–85 % of it before a single neighbour, the topic, the entity block or the comment. Only raising `max_seq_len` or shortening the text closes STOP 2. Four neighbours DOES dissolve STOP 1, and that is a **scoped** change to nine rows of one thread against a **global** one — so they are two decisions, not one.

## The registration is a draft and carries no price

`results/prereg_lora_c.json`. The money block is OPEN by the contract's own instruction: formulas
over rates this repo has measured, the cap the ruling set ($4.00), and for every rate the condition
that would invalidate it. **All three rates are borrowed, and two of them across a change of
instrument** — 6.14 s/call was measured on v2 requests and three of four legs send v3; 61.047 /
68.442 / 121.0 s/step are all readings at ≤ 1 222 tokens. `config/qlora.yaml`'s own comment says
raising `max_seq_len` «changes no step time and no memory except on the batches that need it» —
here every batch needs it. They are registered as inherited readings with their invalidating
condition and are NOT the formulas' inputs. No `worst_case_usd`, no `total_seconds`, no projection.

The step count uses the arithmetic the trainer actually runs — `floor(ceil(n/micro)/accum) × epochs`
— and not the count lora-b registered and missed by two.

## Both review gates are OPEN and D0 stops at them

- `docs/reviews/lora-c-rationales-sample.md` — 40 «our» rows (every one) and 40 boundary rows in two
  tiers. The team lead's `docs/reviews/lora-c-rationales-verdict.md` does not exist.
- `docs/reviews/lora-c-synthetic.md` — all 160 rows with a blank verdict column. The team lead's
  `docs/reviews/lora-c-synthetic-verdict.md` does not exist.

Until they do: no rationale is rewritten, no synthetic row is dropped, `rationale_reviewed` and
`reviewed` stay `false` on every row, and the registration stays a draft.

**And the executor flags 15 of its own 160 synthetic rows.** They name a chain and make a stock,
price or assortment claim about it — «У варусі корм для котів закінчився», «В АТБ шампунь дешевший
ніж в аптеці» — and are labelled `не_наш_рынок` because the THING is non-dairy. The codebook rules
that shape `сеть_ритейлер`, and the team lead's own labels agree on three real rows of it, one of
which is a NON-DAIRY item out of stock at a chain (`@VARUS_channel:10470:21236`). **Nothing was
rewritten** — the gate is a STOP and the executor does not grade its own sample (SPEC §10) — and
`docs/reviews/lora-c-synthetic.md` now opens with the concern, the clause, the precedents and the
fifteen ids, computed by the producer rather than typed.

**And the boundary draw found the instrument before it found the rows.** The shipped
registry-and-watchlist matchers find **zero** retailer or brand mentions across all 466 non-«our»
rows: `config/registry.yaml` spells the chain `Varus` in Latin and the comments write «Варус»,
«варусі», «Варусу». Running the registry names through the lexicon's own stem+endings screen reaches
«Сільпо» and «АТБ» and still not «варусі» — no file in this repo carries that source's Cyrillic
spelling. Tier A is therefore named by two instruments: the shipped watchlist matcher, and pass 1's
OWN window answer where it read `сеть_ритейлер` / `молочный_бренд` and the `subject_id` it wrote
occurs in the comment. Nine rows, and they are the four error classes exactly — «Кола Зеро», «1
вересня» and «Uakino» read as a dairy brand, «Гамета» as a retailer, «варус кафе» as a dairy brand,
«Новус» and «Варусу» as retailers in a giveaway. [[run_the_instrument_on_the_named_example]]

## What this record does NOT claim

- **Nothing is trained and nothing is measured about v3's quality.** Every number here is about the
  DATA and the instruments. The four-column table does not exist yet.
- **Synthetic IS the `молочный_бренд` positive side, and only arm B has it.** The synthetic rows
  carry **32** targets of that class — 8 in each of the four error classes — while arm A's 506 rows
  carry **zero**, and `train_qlora.class_weights` does not even contain the key for arm A, so
  `sampling_order` can never draw one. **Bar 1 = 5 of 5 turns on relabelling msg `580124` to
  `молочный_бренд`**, so the bar is near-unreachable for arm A and reachable for arm B by the same
  arithmetic. Registered as a fourth reachability block; the bar is NOT lowered for arm A, and this
  is why a RED there would mean something different from a RED on arm B.
- **The bar of ≥ 64 on holdout is reachable, and its maximum is 98 and not 100** — the two
  unrenderable holdout rows.
