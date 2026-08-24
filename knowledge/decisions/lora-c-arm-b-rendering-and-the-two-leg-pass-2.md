---
type: decision
date: 2026-08-24
status: accepted
tags: [decision, phase6, pass1, lora, synthetic, rendering, registration, money, stock]
---

# A synthetic row is a v3 QUERY — and pass 2 runs for the arms only

`lora-c-armb` executed at $0 on 2026-08-24. Two team-lead rulings, both registered in
`docs/STATUS.md` п. 1 (н), and both grepped back into that file by
`scripts/write_lora_c_prereg.py::quoted()` on every build of the registration. This record is the
English long form with the numbers.

## The rulings, verbatim

> синтетический запрос рендерится ТЕМ ЖЕ правилом на ТОМ ЖЕ пуле 515 (закон уже запрещает синтетику
> только как СОСЕДА; запрет двойника действует)

> проход-2 в ране — ТОЛЬКО для армов (2 ноги, не 4): база v2 сквозной уже измерена (r2: 4/5 · 2),
> база v3 бара не берёт — экономия ~$0.47 по заряду.

They answer the two questions `lora-c-run` stopped on. `docs/reports/lora-c-run.md` Dv786 found that
**arm B had a registered row count and no registered file**, and that the missing piece was not only
a producer: `scripts/build_lora_c_synthetic.py` states the isolation as «a synthetic row may never
reach the neighbour pool, an eval set or arm A», which bars synthetic as a NEIGHBOUR and says
nothing about synthetic as a QUERY. Dv788 found the contract stating the pass-2 leg count twice —
four in its fixed part, two in its order of operations.

## What the first ruling decides, and what it does not

**Decided.** A synthetic row goes through `pass1_v3.pass1_messages_gm4_v3` against the same pool of
515 real rows: five per-class neighbours by `build_pass1_fewshot_packs.neighbours`, the own-thread
block (satisfied trivially — no `synthetic:` thread is in the pool), amendment 3.25 (2)'s equality
refusal, `build_pass1_sft.target_for`'s +1 boundary with the rationale written first. Not one of
those is re-implemented for arm B; `scripts/build_lora_c_data.py --arm-b-out` calls the same
functions arm A goes through, which is what makes the two arms comparable at all.

**Not decided, and the consequence is measured.** The ruling names the renderer, the pool and the
target shape. It does not name the four HEADER fields the renderer needs — `channel`, `post_id`,
`topic`, `entities` — and a synthetic row has no store to read them from. What was built takes the
branch the existing rules already take: the thread id `synthetic:brand_vs_retailer` splits where a
real one splits (`@tarilka_malyuka:746` → channel, post id), an absent post renders
`prompts.NO_POST_TEXT`, and an empty entity list renders «(this thread resolved no entity)». Nothing
invented; nothing borrowed from a real thread, because a synthetic row wearing a real channel would
fabricate provenance inside training data and break the property the whole isolation rests on — that
the `synthetic:` prefix makes every downstream refusal one string comparison.

**That choice leaves a marker, and the marker is a confound.** Five header lines are carried by
synthetic rows and by NONE of the 506:

| line | in the 160 | in the 506 |
|---|---|---|
| `(this post has no text of its own — it is an image or a video)` | 160 | **0** |
| `<thread channel="synthetic" post_id="brand_vs_retailer">` | 40 | **0** |
| `<thread channel="synthetic" post_id="retailer_non_dairy">` | 40 | **0** |
| `<thread channel="synthetic" post_id="non_dairy_brand">` | 40 | **0** |
| `<thread channel="synthetic" post_id="mention_vs_about">` | 40 | **0** |

All 160 rows are marked. The one that matters is the topic line: not a single real row of this pool
renders `NO_POST_TEXT`, so «this post has no text» is a perfect separator between the training
top-up and everything the model will ever be evaluated on. And the 160 rows carry **all 32**
`молочный_бренд` targets in this line — arm A has zero — so an adapter that conditions the class on
the marker would leave «synthetic did not help» and «the model learned the marker»
indistinguishable, on the one comparison arm B exists to make.

The examples block is where a reader looks for a tell first, and there is none there: the pool holds
exactly ONE `молочный_бренд` row, so that example slot is the same row for every query in this line,
real or synthetic (`1` distinct in both columns of the sixth isolation row).

## What the second ruling changes: the money, and only through one term

`lora-c-run` derived the price at four pass-2 legs and reported the plan SHORT. Ruling (н) takes two
of those legs off — 2 × 11 × 97 = **2 134 s = $0.4742** at the worst price — and that is the only
term that moved. No rate was re-estimated, no row count changed, both arms' step counts (62 and 82)
were registered before either contract.

| price | fixed | left for 144 steps | break-even s/step | readings under it |
|---|---|---|---|---|
| $0.80/h — lora-b rung 1, a create refuses above it | 8 885.88 s = **$1.9746** | 9 114.1 s | **63.29** | 61.047 |
| $0.74/h — what the last five pods billed | 8 885.88 s = **$1.8265** | 10 573.6 s | **73.43** | 61.047 · 68.442 |

Against `lora-c-run`'s 11 019.88 s and 48.47 / 58.61, under which NEITHER reading fitted. **Still no
s/step is registered**: both readings were taken on sequences of at most 1 222 tokens against this
line's 1 445–2 975, and the smoke buys the rate. The finding is published as a field
(`money.pre_pod_arithmetic.readings_under_the_break_even`) and not only as a sentence, so a test can
check it without parsing prose.

`bars.report_only.pass_2_tables` still says «per leg» and this contract may not touch `bars`. The
two are reconciled inside the money block: the tables are per leg for the legs that RUN, and the
ruling says those are the two arms.

## What the file is

`results/pass1_sft_v3_arm_b.jsonl` — the 506 real rows BYTE-IDENTICAL as a prefix, then 160 rendered
synthetic rows. The prefix is re-rendered by the same build and compared against the SHIPPED bytes
before anything is written, so a pool that drifted is a STOP and not a silent pass; comparing the
prefix with the bytes the same call is about to write would prove nothing. Provenance
(`synthetic: true`, `error_class`, `author`) rides on the 160 and on none of the 506 — a key on a
real row would move the prefix, and the prefix is what makes the ablation an ablation.

Readings, each printed and written to a result file:

- **encode census over all 666** through `train_qlora.encode_pass1` with the real tokenizer at the
  pinned revision: **666 encoded, 0 refused**, min 1 445 / median 1 603 / max 2 975 against 3 072,
  headroom **97**. The widest row is still `@tarilka_malyuka:746#83`, a real one;
- `class_weights` on arm B: **five** classes, `молочный_бренд` = 666/(5·32) = **4.1625**;
- isolation: 800 examples, all pool rows, 228 distinct · 0 synthetic ids used as an example over all
  666 rows · 0 example texts equal to their query · synthetic ∩ E / holdout-100 / gold-14 = 0;
- length: widest synthetic request 6 436 chars against the 12 000 ceiling, headroom 5 564.

## The card the ruling names is still out of stock

A read-only probe (`runpodctl gpu list`, `datacenter list`; nothing created) read EU-RO-1 — the
network volume's own datacenter — at 2026-08-24T08:24Z: **RTX A6000 48 GB `none`**, A40 not
catalogued there at all. Seven of 47 cards report stock: RTX 2000 Ada 16 GB $0.24 Low · L4 24 GB
$0.49 Low · RTX PRO 4000 24 GB $0.57 Medium · RTX PRO 4500 32 GB $0.72 **High** · RTX 4090 24 GB
$0.74 Low · RTX PRO 6000 96 GB $2.09 Low · B200 180 GB $6.79 Low.

Listed, priced, and NOT chosen. A listing is not a create: stock at create-time may differ in both
directions, and the only free test of a create is the create — which is also this record's freeze,
so the card and the cap reach the operator together.

## Status

The registration is still a **DRAFT**, the attempt unspent, `bars` untouched, no price key written.
`results/pass1_sft_v3_arm_b.jsonl` and `results/lora_c_arm_b.json` join
`frozen_when_the_pod_exists`; nothing left that list.

Related: [[lora-c-rationale-supervision-and-the-shared-pool]] ·
`docs/reports/lora-c-run.md` (Dv786, Dv788) · `docs/reports/lora-c-armb.md`
