---
type: decision
date: 2026-08-18
status: accepted
tags: [decision, phase6, comment-signals, pass1, sitting, lora, labelling, honesty-frame]
---

# The sitting rules line B — labelled `subject_type` + LoRA, and the TEAM LEAD does the labelling

**The record debt of an accepted step.** `pass1-probe-b`'s bar P1 failed at **9 of 14** against 12
and the registration's return-to-sitting clause fired
([[pass1-probe-b-measured-and-the-sitting-owns-it]]). The sitting was held on the evening of
2026-08-18 and its ruling is registered in `docs/STATUS.md` («Сидение B/C СОСТОЯЛОСЬ 18.08
(вечер)»). This record is the English long form; the numbers that forced the sitting are in
`docs/reports/pass1-probe-b.md` and are not re-argued here.

## What forced the choice

The sitting was offered two branches by the stop-rule and nothing else — **B**: labelled
`subject_type` data plus a LoRA; **C**: another base model. What the measurement put on the table:

| | reading |
|---|---|
| bar **P1** | FAIL — 9 of 14 agreed against 12; losses 5 of a budget of 2 |
| what the losses are made of | **all five are `subject_type`**; `stance` is right on all three rows that score it |
| refusals | **0 of 64** — the transport is settled and is not the question |
| the shape of two losses | `subject_type: null` — an **abstention**, not a parse failure |
| at scale | 25 of 50 census rows carry no `subject_type`, with zero refusals behind them |

One field fails, on an instrument that answers everything asked of it. That is the argument for B:
the model is not refusing to read, it is unwilling to commit to a class — which is what supervision
buys and what another base is not guaranteed to change ([[an-abstention-is-an-answer]]).

## What was decided

1. **Line B.** Labelled `subject_type` data plus a LoRA over the same base. C is not taken.
2. **The team lead does the labelling** — the operator's words: «я доверяю разметку тебе».
3. **The honesty frame**, in the team lead's own five points, registered here so no later contract
   has to reconstruct it:
   1. **The judge does NOT move.** The bar stays the sealed gold **r2 ≥ 12/14**, and the labeller
      never touches exam material.
   2. **Team-lead labels are TRAINING data**, not gold: provenance-tagged (`labelled_by`, date,
      codebook, seed, pack sha) and **ablated at training time** (train with / without). That
      ablation is the LoRA registration's law — named here so it cannot be lost between contracts.
   3. **Contamination is excluded with proof**, by msg_id. The sitting's words scope it to the 14
      gold rows and their threads; `docs/PROMPT-pass1-data-prep.md` widens it to every thread
      carrying any of the **64 registered probe units** — a strictly larger set, and the one the
      pack is built under.
   4. **The codebook is not an opinion**: the v5 attribution law **by the same bytes**
      (`prompts.READER_ATTRIBUTION_LAW_V5`, which is what the pass-1 prompt itself carries by
      reference), the F2a carve-out, and the gold-r2 adjudication ruling
      ([[prompt-must-carry-the-annotators-law]]).
   5. **Volume ≈ 500 rows**, precedent-sized against the intents pass (508). The exact formula is
      fixed by the data-prep contract and not by this record.
4. **The blind control is the operator's option and blocks nothing.** ~40 rows, emitted unlabelled
   so the operator CAN measure team-lead/operator agreement later. No contract depends on whether
   they do.

## What this record does not decide

The training configuration, the cost forecast, the renders and the cap belong to the **LoRA
registration**, which the sitting placed after the labels exist. `docs/STATUS.md` carries it as an
open decision with its own briefing. Nothing in the data-prep contract may pre-empt it.

## Consequences

- The pack is drawn from the reader cell `narrow|varto_off|plus_spam+scam` minus the excluded
  threads, and the exclusion is proved in the pack record and in a test, never asserted in prose
  ([[gate_verdicts_need_an_artifact]]).
- `docs/labels-pass1-r1.jsonl` becomes a **team-lead file** the moment it exists: the executor
  validates it and commits it verbatim, and never generates a label into it
  ([[team_lead_owns_the_docs]]).
- The measurement that would settle B against C — does supervision move `subject_type` — is the
  LoRA registration's, scored against the same sealed bar. This sitting bought the right to try it,
  not the result.

See `docs/reports/pass1-data-prep.md` for the pack this ruling produced.
