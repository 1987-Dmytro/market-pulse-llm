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

## (e) The smoke, and what it measured

50 optimizer steps on the real-only arm, pod `ouhimpvjem3spe`, RTX A6000 / driver 570.195.03 /
torch 2.8.0+cu128 / transformers 5.14.1 / bitsandbytes 0.50.0 / peft 0.20.0 — the 4a stack plus
peft. Artifacts in `results/train/4b-smoke/`.

- **Loss falls**: 0.1799 at step 5 → **0.0399** at step 50, and the held-out carve tracks it
  (0.0585 at step 25 → 0.0335 at step 50) rather than diverging from it. The numbers are small in
  absolute terms because ~20 of the ~460 tokens in a sequence carry loss: the answer is a short
  JSON object and the rest is a fixed prompt the model does not have to predict.
- **LoRA attached to 410 modules**, every one under `model.language_model.*` and not one under
  `vision_tower` or `multi_modal_projector` — the exclusion is verified in the saved
  `adapter_config.json`, not merely configured.
- **The checkpoint round-trips.** The adapter was saved (490 MB), the training model dropped, the
  NF4 base reloaded from scratch and the adapter loaded onto it with `PeftModel.from_pretrained`,
  and the local eval path ran over the 24 carved rows at batch size 1: **zero parse failures**,
  19 T1 and 5 T2 rows scored. Those scores are mechanics evidence and nothing else — the rows come
  from the training pool, and the record labels them so in the file itself.
- **Peak GPU 30.47 GB of 48**, micro-batch never halved, so the OOM branch did not fire. That is
  11.6 GB above 4a's inference figure of 18.9 GB, and it leaves 17.5 GB of headroom.

Nothing in this step opened a frozen test set or the holdout, and no record was appended to
`results/baselines.json`.

## (f) The projection, and the ceiling it crosses

Steps follow exactly from the frozen config; seconds/step is measured.

| arm | rows | steps (2 epochs) | s/step | hours | $ at 0.53/h | vs 4 h |
|---|---|---|---|---|---|---|
| real-only | 2 171 | 272 | 45.23 | **3.42** | 1.81 | under |
| with-synthetic | 2 771 | 348 | 45.23 | **4.37** | 2.32 | **OVER** |

45.23 s/step is the wall-clock average over all 50 steps, carve readings included. The eight
windows that contain no carve reading average 44.35 s/step (43.40–45.60), which moves the
with-synthetic arm to 4.29 h — over the ceiling either way, so the pessimistic figure is the one
tabled.

**Amendment 3.4 (4) says a projection over 4 h per arm stops the line for an operator decision, so
the line is stopped.** The cost is not a surprise to be worked around: bitsandbytes NF4 dequantizes
every weight on every forward *and* backward pass, so a 31B model at effective batch 16 over ~460
tokens a row is roughly 45 s of A6000 time per step, and the same quantization that makes the model
fit is what makes the step slow. The levers all belong to the operator because each changes a
pre-registered quantity:

- **1 epoch instead of 2** halves both arms (real-only 1.71 h, with-synthetic 2.19 h). It changes a
  frozen hyperparameter, and it changes it for both arms or the ablation stops being paired.
- **Raise the ceiling for the second arm only.** 4.37 h against a 4 h box, on a $23.88 remaining
  budget that the run would consume $2.32 of — the ceiling was written as a time-box, and the
  money it was protecting is not the binding constraint here.
- **Drop the synthetic arm.** It is the arm that crosses, and amendment 3.4 (3) makes the ablation
  the way the synthetic source is judged; dropping it would decide by default what the ablation
  was designed to measure. Not recommended, listed for completeness.

## (g) The open question 4c cannot start without

**The weights are in a datacenter the GPU keeps leaving.** 4a got an A6000 in CA-MTL-3 at 08:34
UTC. By 10:49 the stock there was `none`, restarting the exited 4a pod failed with "not enough free
GPUs on the host machine", and the window did not reopen until **11:38 — 49 minutes later, at
`Low`**. This smoke ran instead on a **volume-less pod in US-TX-1**, which cost 4 minutes to
re-download the 62 GB and nothing else; that is fine for a 40-minute smoke and it is not fine for
4c, which needs **two arms of 3.4 h and 4.4 h** and is a one-attempt phase.

Three ways out, all the operator's:

1. **Wait for CA-MTL-3 windows.** Free, and it makes a one-attempt phase depend on stock that was
   observed to vanish for 50 minutes and come back at `Low`.
2. **A second network volume** in a higher-stock datacenter — EU-SE-1 has no volume support at all,
   so this means EU-RO-1, whose A6000 stock was `none` for the whole observation window. ~$7/month
   per 100 GB plus one download.
3. **Run volume-less again**, as this smoke did. The download is genuinely cheap (4 min, ~$0.04)
   and the real cost is the container disk: 80 GB bills by the month while the pod exists, stopped
   or running, which is why this pod was **deleted** rather than stopped once its artifacts were
   home. For 4c that means a session that cannot be paused — a 4.4 h arm would have to run to
   completion or be restarted from a re-downloaded base.

Nothing here is the executor's to choose: (2) and (3) both spend money in ways the budget time-box
was written to control.

**Related:** [[phase4-own-pod-anchor]] · [[phase4-base-model-gate]] · [[3b-infra-and-precision]] ·
[[synthetic-sarcasm-augmentation]] · [[gpu-provider-runpod]]
