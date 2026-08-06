---
type: decision
status: accepted
date: 2026-08-06
tags: [decision, phase5, serving, cost]
---

# 5b.2 — the batch measurement failed on memory, and serving is fixed at batch 1

SPEC amendment 3.11 (2), the batch measurement pre-registered 2026-08-06, gave the phase one
paid attempt at whichever N a carve ladder selected. The ladder selected 16, the paid run
scored 666 of 758 rows at 16 with zero failures, and the worker then ran out of GPU memory.
Under the amendment a failed measurement **fixes serving at batch 1 permanently** and returns
the money question to the operator. That is the ruling; the rest of this record is the numbers,
because a decision whose evidence lives in a chat log is not a decision.

## (1) The ladder said every N was identical — including the one that did not fit

`results/batch_ladder_5b2.json`, 24 arm-A carve rows (`8347abd74ae9…`, 19 `T1v2_with_post` + 5
`T2`), on an A6000 in US-TX-1 serving the 4.5h2 stack (`torch 2.8.0+cu128`,
`transformers 5.14.1`, `bitsandbytes 0.50.0`, adapter `b3ca630846c7…`, both asserts passed
before the first row):

| arm | calls | wall s | s/row | byte-identical to batch 1 |
|---|---|---|---|---|
| 1 | 24 | 100.3 | 4.180 | — (the reference) |
| 1-repeat | 24 | 99.5 | 4.145 | **yes** (the control) |
| 16 | 3 | 36.0 | 1.500 | **yes** |
| 8 | 4 | 36.5 | 1.520 | **yes** |
| 4 | 7 | 44.9 | 1.870 | **yes** |

Two things this settles and one it does not. It settles that the stack reproduces itself run to
run at batch 1 — the repeat arm exists for exactly that, and without it "identical at N" and
"identical to itself" cannot be told apart. It settles that the **batch-1 path did not move**
under the new batching code: all 24 rows match the 5b.1 smoke on `finish_reason`, `parsed`,
`prompt_tokens` and `completion_tokens`. (Not byte-for-byte, which the brief asked for and
`results/serving_5b.json` cannot answer — it stores no reply text. The limit is in the record.)

What it does not settle is whether N changes answers, and this is where the ladder was wrong.
It **contradicts** [[phase4-own-pod-anchor]] §(c), which measured one row of 24 flipping between
batch 8 and batch 1 on 2026-08-01 — a different model state (no adapter) and a different stack,
so this record bounds that finding rather than repealing it.

**A discriminator everything passes is not a selection rule.** With all three candidates
identical, "the largest N whose outputs are byte-identical" degenerates into "take the maximum",
and nothing in the rule asks whether the maximum fits in memory. The carve's longest batch of 16
fitted; the test set's did not.

## (2) The paid run: 666 rows, then the card

One attempt, `--batch-size 16 --batch-measurement`, checkpointed per row.

- `comments_test` **400/400** · parse 0 · api 0 · generation 0 · truncated 0
- `posts_test` **250/250** · parse 0 · api 0 · generation 0 · truncated 0
- `sarcasm_holdout` **16/108** — the second batch of 16 raised `torch.OutOfMemoryError`:
  1.85 GiB requested, **432 MiB free of 47.53 GiB**, of which **42.14 GiB genuinely allocated by
  PyTorch** and 4.65 GiB reserved-but-unallocated, against a ~20 GiB model at rest (19 948 MiB
  measured idle). So this was a real working set of ~22 GiB for one batch, not mainly
  fragmentation — defragmenting would have recovered 4.65 GiB and the request was 1.85 GiB, so
  `expandable_segments:True` might have squeezed it through, which is not a margin to plan on.

`classify_local` re-raises an out-of-memory rather than charging it to rows — it is a fact about
the machine, and 758 counted failures would bury the one line that says what happened — so the
process died before writing a record or a prediction dump.

## (3) Why the rule could not run, and what was salvaged

The adoption rule requires **every 4.5h2-passed gate** to stay passing: G1b, G1d, G1e. G1b is
the sarcasm-holdout slice, and this run scored 16 of its 108 rows. An unmeasured gate is not a
passing one — `scorer.select_serving_config` refuses on exactly that — so the rule has no input
and does not run. **Batch 1, permanently.** No retry, no second N, and test v4 is spent.

`results/batch_5b2_verdict.json` records that first and the salvage second. From the
checkpoint's 666 rows (`results/batch_5b2_checkpoint.jsonl`):

| | batch 16 | batch 1 | 4.5h2 | Δ vs 1 | bar |
|---|---|---|---|---|---|
| G1a | 0.9192 | 0.9214 | 0.9214 | −0.0022 | 0.9470 |
| G1c | 0.8509 | 0.8478 | 0.8478 | +0.0031 | 0.8483 |
| G1d | 0.9586 | 0.9586 | 0.9586 | +0.0000 | 0.9090 |
| G1e | 0.9610 | 0.9610 | 0.9610 | +0.0000 | 0.9283 |
| G1b | **not computable** — 16 of 108 rows | | | | |

Row for row against the 5b.1 batch-1 dump: **660 of 666 identical** — `posts_test` 250/250,
`comments_test` 396/400, `sarcasm_holdout` 14/16. Both computable deltas are inside the
pre-registered 0.005 tolerance, and G1d/G1e are the batch-1 numbers by construction because
`posts_test` agreed on every row.

Two readings to refuse. The first: *"batch 16 is fine, it just needs more memory."* Six rows
moved, on a carve that said every batch size was byte-identical — the pre-filter's 24 rows
cannot see a 1% effect, and this is the phase's real finding. The second, more tempting:
G1c at batch 16 is 0.8509 against its bar of 0.8483, so batch 16 would have **passed** the gate
batch 1 misses by 0.0005. That is four flipped rows on a head that was already within a
rounding error of its bar. It is noise, it decides nothing, and adopting a serving
configuration because it flatters a gate is the failure mode the whole pre-registration exists
to prevent.

## (4) What the operator now has to decide

Measured and projected, 2 passes/day, A6000 secure at $0.53/h, cold start 46.2 s (local NVMe;
278.9 s off the CA-MTL-3 network volume):

| | s/row | s/pass | $/pass | $/month |
|---|---|---|---|---|
| batch 1 — **what production is** | 4.071 | 3 132 | 0.4611 | **27.67** |
| batch 8 — *projected, not measured* | 1.491 | 1 176 | 0.1732 | **10.39** |
| the CA-MTL-3 volume, idle | — | — | — | **~7.20** |
| SPEC §3.11 (6) ceiling | | | | 9–12 |

Batch 8 lands inside the ceiling and batch 1 is three times over it. The 100 GB volume alone
costs more than the whole batch-8 GPU bill and is currently attached to nothing — 5b.1 proved
fresh staging beats it on both money and cold start. Neither is this phase's call.

If a future phase re-opens the batch question, three things it should carry that this one did
not: **N = 8**, not the ladder's maximum; a memory term in the selection rule, or a pre-flight
that runs the longest rows of the actual test set at N before committing the run; and
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` and/or length-sorted batching, which are
cheap and would have made the 1.85 GiB request survivable. None of that is authorised here.

## Cost

$0.4277 for 5b.2 — $1.7069 of the $4.00 5b stop, $2.29 unspent. Pod `5pjikuu7rgitor` deleted
and proven gone by `runpodctl pod list -a` → `[]`; `serverless list` → `[]`.

Related: [[5b-parity-abort-and-pod-runtime]], [[phase4-own-pod-anchor]], [[45h2-ablation-verdict]],
[[gpu-provider-runpod]], [[architecture-stack]].
