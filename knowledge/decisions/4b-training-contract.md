---
type: decision
id: dec-2026-08-01-4b-training-contract
date: 2026-08-01
status: accepted
tags: [decision]
---

# The training contract: frozen hyperparameters, and the invariant that a training example is an eval prompt

**Context:** [[phase4-own-pod-anchor]] left Phase 4 with an anchor, a 44-id slice and a base whose
NF4 config one dict spells for eval, training and serving. SPEC amendment 3.5 then decided both of
4a's escalations — (2) rescaled G1d/G1e to no-regression bars, (3) instructed the scorer to consume
the persisted slice. What was still undecided was everything about the fine-tune itself: what an
example looks like, which rows are in it, and every hyperparameter. 4c trains two arms and scores
the gates **once**, so all of that has to be frozen before it starts, not chosen while it runs.

**Decision (2026-08-01, under `docs/PROMPT-4b.md` rev. 1):** the contract below —
`config/qlora.yaml` plus `scripts/train_qlora.py` — is frozen for 4c. Both ablation arms read the
same config and differ by exactly one data path. No full training run happened in this step, and
nothing scored a frozen set or the holdout.

## (a) A training example is an eval prompt plus the answer, and that is asserted twice

The measurement is the prompt (SPEC §7): its SHA256 is in every record, and 4a refused to run until
this checkout's prompts hashed to the recorded ones. Training inherits that check —
`records.assert_prompt_sha` is the same function, called at dataset build against the same records.

The other half is the answer. A target is the gold labels serialized in exactly the schema
`prompts.parse_reply` reads, normalised the way the parser normalises: intents deduplicated and
sorted, brand mentions reduced to `{"mention": …}` with collapsed whitespace and no `brand_id` (a
model cannot know an id an annotator assigned). `assert_format_identity` sends **every** target of
both arms back through the parser and refuses on the first one it cannot read. A target the eval
parser rejects would be a label the model is trained to produce and the scorer counts as a parse
failure — the failure mode is silent, so the check is exhaustive rather than sampled.

### The skew this caught before a pod existed

The obvious way to build the example is to render the whole assistant turn through the chat
template and split it at the prompt. On this template revision that is **wrong**, and the assertion
written to check the split is what said so:

```
prompt (eval path): …</comment><turn|>\n<|turn>model\n<|channel>thought\n<channel|>
turn form:          …</comment><turn|>\n<|turn>model\n{"sentiment": …}<turn|>\n
```

With `enable_thinking=False` the *generation* prompt ends with an already-closed thinking channel —
the local equivalent of 3b's `reasoning: {"enabled": false}`, and what every gate row is scored
through. The *turn* form drops that channel entirely. Training on the turn form would have
conditioned the model on a context the eval path never sends: no error, no failed assert at gate
time, just gates lower than the smoke suggested and nothing to point at.

So the prompt comes from the same `apply_chat_template(..., **local_llm.CHAT_TEMPLATE)` call the
eval client makes, and only the end-of-turn marker is taken from the turn form — derived from the
template rather than typed here, because it is the token generation stops at and `_trim` reads
back. Loss is masked to the completion: the prompt is context, not something to learn.

## (b) The rows

| source | rows | of | note |
|---|---|---|---|
| `data/frozen/comments_train.jsonl` | 895 | 1 600 | T1 |
| `data/annotation/sarcasm_candidates.jsonl` | 532 | 746 | T1 |
| `data/frozen/posts_train.jsonl` | 744 | 750 | T2 |
| `data/annotation/synthetic_sarcasm.jsonl` | 600 | 600 | T1, `--with-synthetic` only |

**`unclear` rows are dropped, and it is a large drop** — 694 of 1 600 comments and 206 of 746
candidates. The assumption, stated because it is one: a row the annotator could not decide has no
right answer to teach, and SPEC §4 already excludes it from every gate, so training on it would put
a label into the model that the scorer refuses to score. The alternative — training on `unclear` as
a fourth sentiment class — would teach the model to emit a label `parse_reply` rejects out of hand.
The surviving counts are the same reading the Phase 3 baselines trained on (906/540/749 in the
`tfidf-logreg` and `xlm-roberta-base` records; the 11/8/5-row differences are the carve, below).

**The carve is 24 rows held out of training**, drawn from the real pool with seed 42 **before** the
synthetic rows join. That ordering is the point: both arms hold out the same rows, so the arms
still differ by exactly the 600 synthetic ids. It is a convergence thermometer and the fixture the
mechanics check runs on. It selects nothing — no early stopping, no checkpoint choice, no
hyperparameter reads it — and it never touches a frozen set.

**Arm identity is asserted in both directions.** `with-synthetic − real-only` must be exactly the
600 `synthetic:NNNN` ids and `real-only − with-synthetic` must be empty; a one-directional check
would miss a real row silently dropped from one arm, because the arm would still be 600 rows
longer. Both assembled datasets carry a content hash over sorted rows (`train_sha256`), so the
hash is of the data and not of the order it was read in — the same rule the prediction dumps
follow.

A guard that looks redundant and is not: `(task, id)` must be unique across the assembled set.
Eighteen posts carry the same `@channel:msg_id` as a comment, so `id` alone is not a key, and a
duplicate inside one task would collapse in exactly the set comparisons the arm-identity assert is
made of.

## (c) The hyperparameters, one line of why each

| value | setting | why |
|---|---|---|
| LoRA r | 16 | the QLoRA paper's working point for a task-specific adapter; ~0.2% of 31B trainable |
| alpha | 32 | 2r — the scale the 1e-4 LR below assumes |
| dropout | 0.05 | 2 171 rows over 2 epochs is a small budget; some regularisation, not much |
| target modules | every attention + MLP projection of the language model | QLoRA's own result is that adapting all linear layers, not just q/v, closes the gap to full fine-tuning |
| excluded | `vision_tower`, `multi_modal_projector`, `vision_model` | Gemma 4 is image-text and we train on text; an adapter there is untrained weights on the serving path |
| optimizer | paged AdamW 8-bit | paged so a long-sequence spike does not OOM a card that is also holding 4-bit weights |
| LR | 1e-4, cosine, 3% warmup | the QLoRA default for r=16 on an instruct base; cosine because the epoch count is fixed |
| weight decay | 0.0 | LoRA B starts at zero; decaying it fights the only thing that learns |
| grad clip | 0.3 | QLoRA's value; the loss is dominated by ~20 answer tokens per row and a bad batch is a big gradient |
| epochs | 2, fixed | **no early stopping**: nothing may select against an eval (SPEC §5) |
| max seq len | 1024 | measured — the longest of the 2 795 scoreable rows renders to **973** tokens, so nothing truncates |
| micro-batch × accum | 2 × 8 | effective 16; on OOM the trainer halves one and doubles the other, holding the effective batch |
| seed | 42 | the project's seed, recorded in provenance |
| gradient checkpointing | on | activation memory is the one term that scales with sequence here |

`max_seq_len` deserves the emphasis. It is the one hyperparameter whose wrong value fails silently:
a truncated row teaches a cut-off label, and the model would learn to emit half a JSON object. The
number comes from tokenizing every assembled example with the pinned tokenizer revision before any
pod existed — p95 717, p99 806, max 973 — so 1024 is a measurement with 5% of headroom, not a
round number. The trainer refuses any example over the cap rather than truncating it.

**What is NOT in this config, on purpose:** the base model id and the NF4 quantization dict. They
live in `src/market_pulse/local_llm.py`, which the eval path, the trainer and production all read.
"Train in the precision you serve" is only true while one value spells all three.

## (d) The artefact

Adapter-only checkpoints, resumable (optimizer, scheduler, epoch, row index, step). The deliverable
is the 4-bit base **plus the unmerged adapter**, served in exactly the configuration every gate is
scored in; merging into bf16 weights stays forbidden until measured (amendment 3.4 (1), Phase 5).
The base is never written by this script.

## (e) The smoke

Not run in this session: RunPod had **no A6000 capacity in CA-MTL-3** — the datacenter that holds
network volume `gfwa2an8fn`, and a volume cannot move — from 10:49 UTC onward, and restarting the
exited 4a pod failed with "not enough free GPUs on the host machine". Stock was `Medium` in EU-SE-1
and `Low` in US-TX-1, neither of which takes network volumes. See §(g).

## (f) The projection

Steps per arm follow from the frozen config and the row counts, and they are exact:

| arm | rows | steps/epoch | steps (2 epochs) |
|---|---|---|---|
| real-only | 2 171 | 136 | **272** |
| with-synthetic | 2 771 | 174 | **348** |

The one input the smoke owes is seconds/step, and it is the one number this ADR cannot yet carry.
Against amendment 3.4 (4)'s **4 h per arm**, the ceiling is 53 s/step for the real-only arm and
41 s/step for the with-synthetic one; 4a measured 3.04 s/row of *inference* at batch 1, and a
training step at effective batch 16 with checkpointing is a different quantity — which is exactly
why the number is measured rather than argued.

## (g) The open question 4c cannot start without

**The weights are in a datacenter the GPU keeps leaving.** 4a got an A6000 in CA-MTL-3 at 08:34
UTC; by 10:49 the stock there was `none` and stayed there. 4c needs **two arms of up to 4 h each**
on that same pairing, and it is a one-attempt phase. Three ways out, all the operator's:

1. **Wait for CA-MTL-3 windows.** Free, and it makes a one-attempt phase depend on stock.
2. **A second network volume** in a higher-stock datacenter (EU-SE-1 has no volume support at all,
   so this means EU-RO-1, whose A6000 stock was also `none`). ~$7/month per 100 GB, and the weights
   must be downloaded into it once.
3. **Run volume-less** and re-download 62 GB per session onto a larger container disk. Costs pod
   time and a bigger disk per hour, and a volume-less pod is deleted unrecoverably at a $0 balance.

Nothing here is chosen by the executor: (2) and (3) both spend money in ways the budget time-box
was written to control.

**Related:** [[phase4-own-pod-anchor]] · [[phase4-base-model-gate]] · [[3b-infra-and-precision]] ·
[[synthetic-sarcasm-augmentation]] · [[gpu-provider-runpod]]
