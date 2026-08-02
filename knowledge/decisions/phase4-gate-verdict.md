---
type: decision
id: dec-2026-08-01-phase4-gate-verdict
date: 2026-08-01
status: accepted
tags: [decision]
---

# The one attempt: two arms trained, each scored once, and the Tier-1 gates decided

**Context:** [[4b-training-contract]] froze the trainer, the config and the dataset; SPEC amendment
3.6 raised the per-arm ceiling to 5 h and left everything else alone. What remained was the step
that cannot be repeated. Both arms train in full, each is scored on the frozen sets exactly once,
the rule of amendment 3.4 (3) selects one, and the five pre-registered bars decide. **After the
first gate number was seen, nothing was retrained, re-scored or reconfigured** — arm B launched on
the frozen config while arm A's failures were already on screen, because no decision exists until
the rule is applied.

**Decision (2026-08-01, under `docs/PROMPT-4c.md` rev. 1):** below. The gate verdicts are the
selected arm's; both columns are published side by side; there is no third run.

## (a) What ran, and on what

| | arm A (real-only) | arm B (with-synthetic) |
|---|---|---|
| pod | `wol5tdhnbyrj1c` | `lxsgsyxdw9jqvd` |
| datacenter | US-TX-1 SECURE, volume-less, 80 GB | US-TX-1 SECURE, volume-less, 80 GB |
| driver | 550.127.08 | 570.195.03 |
| repo | trained at `16e3af1`, scored at `34a27d7` | `34a27d7` throughout |
| rows | 2 171 | 2 771 |
| `train_sha256` | `d2fa6742055aeb26…` | `d6d3c800ecd5916e…` |

Stack on both: torch 2.8.0+cu128 · transformers 5.14.1 · bitsandbytes 0.50.0 · peft 0.20.0 ·
accelerate 1.14.0 — 4b's stack exactly. The A6000 was out of stock in CA-MTL-3 (where the network
volume lives) at both launches, which is what the operator's volume-less ruling was for; US-TX-1
took an 80 GB container disk first try, both times.

**Arm A's split across two commits is real and is bounded**:
`git diff 16e3af1 34a27d7 -- scripts/train_qlora.py config/ src/` is **empty**. The commit between
them fixes a crash in the *eval* script's last line and adds its test; not one file the trainer
reads changed. Both arms therefore trained on identical code, config and seed.

**Arm A's dataset hash equals the 4b contract's**, checked on the pod before the GPU was touched —
the arm that trained is byte-identically the arm 4b projected. Arm B's diff-assert ran on its own
pod before training: exactly 600 `synthetic:NNNN` ids added, zero rows removed, the same 24-row
carve in both.

## (b) Resume, proved against the real stack before arm A started

[[4b-training-contract]] §(h) named one thing 4c had to prove in its first ten minutes: the adapter
reloaded with `is_trainable=True` onto a k-bit-prepared base, plus `torch.load` on a real
paged-AdamW state. Ten steps, then a reload and five more, in a directory of its own:

| step | loss | carve loss | lr |
|---|---|---|---|
| 5 | 0.18051 | — | 6.250e-05 |
| 10 | 0.10974 | 0.11247 | 9.99858e-05 |
| **15 (resumed)** | **0.05680** | **0.05915** | 9.98266e-05 |

`resumed at epoch 1 row 0, optimizer step 10` — the counter continued rather than resetting, the
loss stayed on the pre-kill trajectory rather than restarting at 0.18, and the cosine carried on
from where it was. `state.pt` was 249 587 797 bytes of real optimizer state. `assert_resumable`,
added for this, stayed silent: the state covered exactly the trainable parameters.

Two departures from the written protocol, recorded rather than smoothed: both runs ended at their
own `--max-steps` cap instead of being killed by a signal (the same unconditional `save()` writes
the same artifact, and the reload path under test is unchanged), and the resume happened to cross
an epoch boundary — see finding 2 below for why.

## (c) Both arms, every gated head

Each arm was scored once, at batch size 1, through the same local inference path the anchor was
measured through, the adapter unmerged on the NF4 base. **758/758 rows scored on both, with zero
failures of any kind** — no parse, no generation, no truncation, on either arm.

```
                                     real-only  with-synthetic      delta
G1a sentiment macro-F1                  0.9107          0.9172    +0.0065
  ua                                    0.9146          0.9171    +0.0025
  ru                                    0.8919          0.9364    +0.0444
G1b slice fix-rate                    21/44           24/44
  rate                                  0.4773          0.5455    +0.0682
  guard delta (>= -0.02)                0.0189          0.0254
G1c intents micro-F1                    0.8212          0.8073    -0.0139
G1d post_type macro-F1                  0.9386          0.9159    -0.0227
G1e brand extraction F1                 0.9333          0.9577    +0.0244
relevance (reported, not gated)         0.9894          0.9891    -0.0004
```

Against the zero-shot anchor (0.8918 / — / 0.7936 / 0.9084 / 0.8974, relevance 0.9415) **every
gated head of both arms is up**: real-only by +1.89 / +2.76 / +3.02 / +3.59 pp, with-synthetic by
+2.54 / +1.37 / +0.75 / +6.03 pp. Both arms' ≤2 pp G1b guard is positive — neither traded overall
sentiment for the slice.

Training: arm A 270 steps in **3.40 h**, arm B 346 steps in **4.17 h**, both under the 5 h ceiling
and both under 4b's projection (3.42 h / 4.37 h). Peak GPU 30.86 / 30.84 GB of 48; micro-batch 2 ×
accum 8 held throughout — the OOM branch never fired on either arm.

## (d) The rule, applied

`PYTHONPATH=src python3 scripts/gate_verdict.py`, verbatim:

```
--- the rule ---
the synthetic source stays iff its arm's G1b fix-rate is strictly higher AND no other gated head is
lower by more than 0.5 pp (SPEC amendment 3.4 (3), fixed before any Phase 4 code or GPU spend)
  G1b strictly higher   0.5455 > 0.4773   YES
  head deltas           G1a +0.0065 · G1c -0.0139 · G1d -0.0227 · G1e +0.0244
  lower by > 0.5 pp     G1c -0.0139 · G1d -0.0227
  SELECTED ARM          real-only  (synthetic is dropped)
```

**The synthetic source is dropped, and it is dropped on the half of the rule it was written for.**
It won the first clause outright — 24 of 44 against 21, the largest single-head move either arm
made on the thing it was generated to help. It lost the second: intents fell 1.39 pp and post-type
2.27 pp, both past the 0.5 pp tolerance. That is precisely the trade amendment 3.4 (3) pre-refused
on 2026-08-01, before any of these numbers existed: a fix-rate bought with other heads is not a
better model, and deciding it now would be deciding it after seeing the answer.

Worth recording beside the verdict rather than inside it: with-synthetic's G1a `ru` is **+4.44 pp**
over real-only (0.9364 against 0.8919), by far the biggest per-language gap in the table. It is not
a head the rule reads — the per-language numbers are floors of the G1a gate, not heads of their own
— and both arms clear both floors comfortably. It is the strongest signal in this ablation that the
synthetic Russian sarcasm rows did something real, and it changed nothing, because the rule was
fixed first.

## (e) The five verdicts

Bars derived programmatically from the own-pod anchor (`scripts/gate_bars.py`); no threshold is
typed anywhere in code, tests or this document.

| gate | what | value | bar | verdict |
|---|---|---|---|---|
| **G1a** | overall | 0.9107 | ≥ 0.9418 | **FAIL** |
| | `ua` floor | 0.9146 | ≥ 0.8718 | pass |
| | `ru` floor | 0.8919 | ≥ 0.8649 | pass |
| **G1b** | fixed, n=44 | **21** | ≥ 27 | **FAIL** |
| | guard delta | +0.0189 | ≥ −0.02 | pass |
| **G1c** | intents micro-F1 | 0.8212 | ≥ 0.8436 | **FAIL** |
| **G1d** | post_type macro-F1 | 0.9386 | ≥ 0.8984 | **PASS** |
| **G1e** | brand extraction F1 | 0.9333 | ≥ 0.8874 | **PASS** |

**2 of 5.** The two that pass are the no-regression gates amendment 3.5 (2) rescaled — and they do
not merely hold the line: G1d is 3.02 pp *above* the anchor and G1e 3.59 pp above, so the
multi-task forgetting risk those gates were rewritten to measure did not materialise at all.

The three that fail are the margin gates, and they fail by margins, not by regressions. G1a asked
for +5 pp and got +1.89; G1c asked for +5 pp and got +2.76; G1b asked for 27 of the 44 rows the
base model gets wrong and got 21. **A failed gate closes its question** (SPEC §5) — nothing here is
retried.

What the G1b failure is made of, read off the per-row dump and not re-scored: of the 23 slice rows
real-only does not fix, **15 are wrong on sarcasm only, 8 on both, and 0 on sentiment only**. G1b
is a sarcasm-detection failure, end to end. Across the whole 108-row holdout, every row of which is
gold `sarcasm: true`, real-only detects sarcasm on **82** and with-synthetic on **83**, against the
base model's **64**. Both arms moved that head 18–19 rows and neither cleared a bar defined as 60%
of the base model's own errors — the slice is, by construction, the hardest 44 rows in the corpus
for this model family.

## (f) Findings — none of them changed a number, and none was fixed mid-phase

The rule for all six: 4c is one attempt and the arms must run identical code, so a fix landing
between them would be a confound. Each is stated with what it can and cannot reach.

**1. The run makes 270 steps, not the projected 272.** `planned` is
`ceil(rows / (micro × accum)) × epochs` = `ceil(2171/16) × 2` = 272, but the loop steps once per 8
*completed* micro-batches: 2 171 rows at micro-batch 2 is 1 086 micro-batches an epoch, and
`1086 // 8` is **135**, not 136. The projection was 0.7% long; the cosine was built over 272 so lr
at step 270 was already 1.4e-08. Harmless, and it means every 4b projection reads slightly
pessimistic.

**2. The epoch boundary folds leftover gradients into the next step.** Those 6 trailing
micro-batches accumulate gradients that are never applied and never zeroed, so epoch 1's first
optimizer step folds in 6 micro-batches of epoch 0 — one step in 270 with a 1.75× effective batch.
Arm B's leftover is 2 micro-batches, so the arms differ here too.

**3. The checkpoint written after an early `--max-steps` stop records the wrong position.**
`save()` is called after the `for epoch` loop, so it stores the loop variable's final value:
`epoch 1 row 0` instead of `epoch 0 row ~160`. **A full arm cannot reach this** — the arms pass no
`--max-steps`, and a mid-run crash resumes from the in-loop `save_every` write, which is the *same*
`save()` called from a correct call site. Only the post-loop call site is wrong, which is what makes
it a two-line fix in Phase 5.

**4. `seconds_per_step` in a resumed `provenance.json` is understated.** It divides this process's
wall clock by the cumulative step counter: 236.7 s / 15 = 15.8 s, when the five steps that ran took
~43 s each. `loss.jsonl`'s per-window figure is the honest one. Reaches only a crashed-and-resumed
arm's provenance, never a clean run's.

**5. Training on this stack is not bit-reproducible.** Arm A's step-5 loss is **0.18010**; the
resume proof, on identical data, identical seed 42 and identical config on the same pod, gave
**0.18051**. Two candidate causes and this run cannot separate them — NF4 dequantization and
reduction order on the A6000 (the family [[phase4-own-pod-anchor]] §(c) already measured when greedy
decoding turned out not to be batch-invariant), or the `lora_dropout: 0.05` mask sequence off
torch's global RNG. The mechanism is not claimed; the consequence is what was measured, and it is
the one that matters: **the ablation is paired on data and config, not on bits.** Amendment
3.4 (3)'s "identical config and seed" reads as stronger than what this hardware delivers, and the
rule's 0.5 pp tolerance on the four protected heads is what absorbs it. G1b's "strictly higher" does
not absorb anything, and that is the operator's pre-registered choice, not a new one.

**6. A defect the pod never got to charge for.** `eval_zero_shot.main` ends by printing what it
wrote, and the G1b-slice line was guarded by `anchor_valid` alone. On a fine-tuned arm `slice_ids`
is `None` — the arm scores the pre-registered slice and writes no file — so that line raised
`TypeError` **after** the record had been written: a traceback and a non-zero exit at the end of a
45-minute eval that follows a 3.4 h training run. It was found by the test that now covers it, which
drives `main` through the whole `--record-out` path with stubbed weights. `--smoke` returns before
the record is built and `--probe` before it is written, so nothing had ever executed that path.

## (g) Cost, and what the artefact is

**$6.88 of the $25 Phase 4 cap**, read from `scripts/runpod_guard.py` after the second pod was
deleted — $1.14 of it was 4a and 4b, so **4c cost $5.74** against ~$5.2 projected. Remaining
$18.12. Both 4c pods were deleted rather than stopped: volume-less, so a stopped one would keep
billing 80 GB of container disk by the month. The 4a pod `gxkdecf3g7k3y7` is still `EXITED` on the
CA-MTL-3 network volume — it predates 4c and is left as 4a left it, flagged rather than deleted.

The deliverable is `results/train/4c-arm-a/adapter` — the LoRA adapter of the **real-only** arm,
sha256 `c0e462af81aad9f14e5dbbe67bf53213db1b1b8e3cd4e172a5927f597d37a986`, served **unmerged** on
the same NF4 4-bit base every gate was scored through. Merging into bf16 weights stays forbidden
until measured (amendment 3.4 (1), Phase 5). The with-synthetic adapter
(`0566900e3f42451e54eb75296bc3b773b3c143a80c6dafd6ad5d7f8c0f82806b`) is kept beside it: the
ablation's second column is evidence, not waste.

**Related:** [[4b-training-contract]] · [[phase4-own-pod-anchor]] · [[phase4-base-model-gate]] ·
[[synthetic-sarcasm-augmentation]] · [[hybrid-sarcasm-holdout-3.2]] · [[gpu-provider-runpod]]
