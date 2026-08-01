---
type: decision
id: dec-2026-08-01-phase4-own-pod-anchor
date: 2026-08-01
status: accepted
tags: [decision]
---

# The own-pod zero-shot row anchors G1d/G1e, and it is the run that defines the G1b slice

**Context:** [[3b-infra-and-precision]] §(d) promised one thing in exchange for running the 3b
baselines on a third-party endpoint: the model chosen at the Phase 4 gate gets re-run zero-shot on
our own GPU, as a cross-check nobody else's serving stack can invalidate. §(f) left G1d and G1e
without an anchor until that selection was made, and [[phase4-base-model-gate]] §(c) left the G1b
slice to be measured on our own hardware rather than read off OpenRouter's preview. SPEC amendment
3.4 (2) turned all three into one step: 4a.

**Decision (2026-08-01, executed under `docs/PROMPT-4a.md` rev. 1):** the row
`google/gemma-4-31b-it` @ `2026-08-01T09:45:00+00:00` in `results/baselines.json` — 758 frozen rows,
our own A6000, NF4 4-bit — **is the G1d/G1e anchor**, it **defines the G1b slice** at
`results/g1b_slice.json` (n 44), and its quantization config is the base step 4b trains against and
production serves. No training happened in this step.

## (a) The run

| | |
|---|---|
| model | `google/gemma-4-31b-it`, revision `842da3794eaa0b77d5f08bae87a17459d91ff475` (pinned, not a branch) |
| quantization | NF4 4-bit, double quant on, compute dtype bf16 — `config.quantization`, one dict for the record, 4b's training base and the serving default |
| decoding | greedy, `do_sample: false`, `max_new_tokens` 256, seed 42, **batch size 1** (§(c)) |
| hardware | RTX A6000 48 GB, driver 570.195.03, CUDA 12.8, torch 2.8.0+cu128, transformers 5.14.1, bitsandbytes 0.50.0, pod `gxkdecf3g7k3y7` (CA-MTL-3) |
| rows | comments_test 400/400 · posts_test 250/250 · sarcasm_holdout 108/108 |
| failures | **zero** — parse 0, generation 0, truncated 0, on every input. `gate_anchor_valid: true` |
| artifacts | `results/predictions/google-gemma-4-31b-it--20260801T094500Z.jsonl` (758 rows, sha in the record) · `results/g1b_slice.json` (sha in the record) |
| cost | 39 min at $0.53/hr ≈ $0.35. Phase ledger **$0.6203 at 09:52 UTC**, when the pod stopped — the figure keeps growing while the volume exists (**$0.6456 at 10:15 UTC**), which is the point of reading the account balance rather than the pod billing rows. Any quoted phase spend needs its timestamp. |

The prompts are 3b's, and that is checked rather than assumed: the runner reads
`config.prompt_sha256` out of the recorded OpenRouter run of the same model and refuses to load the
weights unless this checkout hashes to the same values —
`T1 9b2a0217…c0de355`, `T2 6a7e66ef…ab3a54b4`. Comparing `prompt_sha256` to itself would have
passed forever; comparing against the stored record is what makes "byte-identical" a claim with a
negative control.

## (b) The cross-check — own-pod against the OpenRouter fp8 row

Both columns are read out of `results/baselines.json` by the same script; nothing is typed from
memory and nothing is averaged. Reproduce with:

```python
import json, pathlib
runs = json.loads(pathlib.Path("results/baselines.json").read_text())["google/gemma-4-31b-it"]
openrouter = next(r for r in runs if r["config"].get("backend", "openrouter") == "openrouter")
pod = next(r for r in runs if r["config"].get("backend") == "local")
```

| head | OpenRouter fp8 | own-pod NF4 | delta (pod − OR) | status |
|---|---|---|---|---|
| G1a sentiment macro-F1 · overall | 0.8944 | 0.8918 | -0.0027 | reported |
| G1a sentiment macro-F1 · `ua` | 0.8957 | 0.8918 | -0.0039 | GATED |
| G1a sentiment macro-F1 · `ru` | 0.8688 | 0.8849 | +0.0162 | GATED |
| G1a sentiment macro-F1 · `other` | 0.8865 | 0.8689 | -0.0177 | not gated (3.1) |
| G1c intents micro-F1 | 0.7981 | 0.7936 | -0.0046 | GATED |
| G1d post_type macro-F1 | 0.8898 | 0.9084 | +0.0187 | GATED |
| G1d relevance macro-F1 | 0.9505 | 0.9415 | -0.0090 | not gated (3.3) |
| G1e brand extraction F1 | 0.9211 | 0.8974 | -0.0236 | GATED |

| diagnostic (not a gate) | OpenRouter fp8 | own-pod NF4 | delta |
|---|---|---|---|
| `sarcasm_binary_macro_f1_comments_test` | 0.7918 | 0.8027 | +0.0109 |
| `holdout_sentiment_macro_f1` · overall | 0.4780 | 0.4703 | -0.0078 |
| `holdout_sarcasm_macro_f1` | 0.7727 | 0.7442 | -0.0285 |
| `holdout_sarcasm_detected` | 68 | 64 | -4 |
| `base_errs_sentiment` | 10 | 13 | +3 |
| `base_errs_sarcasm` | 40 | 44 | +4 |
| `base_errs_union` | 40 | 44 | +4 |

**Reading it.** Every gated head moves, in both directions, by 0.004–0.024. That is the expected
shape of an fp8-on-somebody-else's-kernels row against an NF4-on-ours row, and it is why §(d) of
[[3b-infra-and-precision]] asked for the cross-check instead of trusting one number twice. Nothing
here is averaged and nothing is reconciled: **where the two disagree, the own-pod number anchors**
(amendment 3.4 (2)), and the OpenRouter row keeps its place in the Phase 3 table as what it always
was — a row produced on a stack we do not control.

Two cells are worth naming. **G1d moves +0.0187 in our favour**, so the 10 pp gate G1d must clear
is now measured from 0.9084, not 0.8898 — a harder bar than the Phase 3 table implied, and the
correct one. **G1e moves −0.0236 against us**, so that bar is 0.8974: easier, and equally correct.
The gate does not get to pick whichever anchor flatters the fine-tune, which is exactly why the
anchoring rule was pre-registered before this run existed.

**What the disagreement does not do** is reopen the base-model selection. [[phase4-base-model-gate]]
§(a) chose Gemma against two other candidates on their own OpenRouter rows; a re-measurement of one
model on different hardware is not a paired comparison against rows nobody re-measured, and the
selection is closed.

**One margin re-read.** The gate ADR flagged G1a `ru` as tied inside third-party noise (Gemma
0.8688 against Haiku 0.8988, a 0.0021 lead over the 27B against a 0.0298 same-config swing). Our
own hardware puts Gemma's `ru` at **0.8849**, +0.0162 above its OpenRouter reading — closing about
half the distance to the Haiku reference row. It changes no decision: Haiku is a reference row and
anchors nothing. It does say the `ru` cell of the 3b table was noisy in the direction the ADR
suspected.

## (c) Greedy decoding is not batch-invariant here, and that was measured

`docs/PROMPT-4a.md` allows "batching as memory allows (greedy — batch size must not change
outputs)". The parenthesis was treated as a claim to test. At batch 8, one probe row of 24 came back
with different intents than at batch 1 — `[]` against `["packaging", "quality"]` — with the same
weights, the same prompt, `do_sample: false` and temperature 0. Left padding and kernel selection
move a logit on bitsandbytes NF4 + A6000, so the premise does not hold on this stack.

**The run went at batch size 1**, which is trivially invariant (one row, no padding) — and that
half was measured too: the same 48-row probe twice, byte-identical labels. So the own-pod row
carries a determinism property the OpenRouter rows never could, and `config.determinism_note` says
so.

It cost nothing. 3.04 s/row, 39 minutes for 758 rows, $0.35 — against amendment 3.4 (4)'s ceiling
of 4 h per arm. This is a free correctness win, not a compromise. **Step 4b inherits it:** the two
ablation arms are scored through the same local path, so they run at batch size 1 unless someone
re-measures invariance on the training-time stack and records the result.

## (d) The G1b slice

`results/g1b_slice.json`, hashed into the record, holds **44 ids** — the rows of the 108-row frozen
sarcasm holdout that the base model gets wrong, as the union of its sentiment and sarcasm error
sets. That union is the reading the 2026-07-31 gate review fixed for amendment 3.2's word
"misclassifies" ([[phase4-base-model-gate]] §(c)), and the file computes it as a real set union,
not a sum.

- sentiment errors **13** · sarcasm errors **44** · union **44**.
- The 13 sentiment errors are a **subset** of the 44 sarcasm errors — verified against the file, not
  inferred. The containment the OpenRouter preview showed at 10 ⊂ 40 held on our own hardware at a
  different pair of numbers, which is the more interesting fact: the base model's sentiment mistakes
  on this holdout are mistakes about irony, not about polarity.
- **44 < 100, so amendment 3.2's pre-registered fallback applies**: the slice is whatever the base
  model errs on and the smaller `n` is reported beside the gate verdict. Nothing is topped up,
  nothing is re-drawn, and the OpenRouter preview's 40 is not the slice and never was.

`results/predictions/google-gemma-4-31b-it--20260801T094500Z.jsonl` is the other half of the
artifact: 758 rows of `input`, `id` and the predicted labels — no gold, no source text. It closes
the gap [[phase4-base-model-gate]] §(d) recorded, for this run: the slice can be rebuilt from the
dump and the frozen file, and the record's two sha256 fields are re-derivable by anyone.

## (e) The NF4 config is the artefact, not just this run's setting

`config.quantization` — `load_in_4bit`, `bnb_4bit_quant_type: nf4`, `bnb_4bit_use_double_quant`,
`bnb_4bit_compute_dtype: bfloat16` — is one dict in `src/market_pulse/local_llm.py` that the record
stores verbatim, the loader builds its `BitsAndBytesConfig` from, and step 4b trains its LoRA
adapters against. "Train in the precision you serve" (amendment 3.4 (1)) is only true if one value
spells all three, so it is one value. The whole run held **18.9 GB** of the card's 48 GB
(`nvidia-smi` mid-run, weights plus the batch-size-1 KV cache), which is the number 4b should size
its adapters and optimiser state against — not a weights-only figure this run never isolated.

The corollary already in `knowledge/hot.md` stands and is now load-bearing: the deliverable is the
4-bit base **plus the unmerged adapter**, and merging into bf16 weights is forbidden until measured
(Phase 5). Every gate number from here on is produced in this configuration.

## (f) One open question, and one the operator closed

### The own-pod row is baseline (c) everywhere — operator decision, 2026-08-01

**Decided (operator, 2026-08-01, after this report):** the own-pod row is baseline **(c)** for
**every** task, not only the G1d/G1e anchor. Amendment 3.4 (2) and [[3b-infra-and-precision]] §(f)
reason about G1d and G1e because those two are worded "≥ zero-shot base LLM + 10 pp" and name the
anchor; SPEC §7 makes "zero-shot base LLM with fixed prompt" baseline (c) for every task, and G1a is
"≥ **best baseline** + 5 pp". Two Gemma zero-shot rows existed and no rule said which one G1a and
G1c measured from. Now one does, and it is the row produced on the hardware every Phase 4 number
comes from. The OpenRouter row keeps its place in the Phase 3 table and is no longer a baseline
candidate for any Tier-1 gate.

Pre-registered **before** 4b trains and before any fine-tuned number exists, which is the only time
this decision could honestly be made. Every figure below is `scripts/show_results.py` over
`results/baselines.json`; none is typed from memory.

| gate | rule (SPEC §5) | best baseline, per the decision | **bar the fine-tune must clear** |
|---|---|---|---|
| G1a sentiment macro-F1 · overall | best baseline + 5 pp | **0.8918** own-pod (xlm-r 0.7824, tfidf 0.6834) | **0.9418** |
| G1a · `ua` floor | not below its baseline by >2 pp | 0.8918 | **≥ 0.8718** |
| G1a · `ru` floor | not below its baseline by >2 pp | 0.8849 | **≥ 0.8649** |
| G1c intents micro-F1 | best baseline + 5 pp | **0.7936** own-pod (xlm-r 0.6007, tfidf 0.6000) | **0.8436** |
| G1d post_type macro-F1 | zero-shot base LLM + 10 pp | 0.9084 own-pod | **1.0084** |
| G1e brand extraction F1 | zero-shot base LLM + 10 pp | 0.8974 own-pod | **0.9974** |

The own-pod row is the best baseline on both G1a and G1c by a wide margin, so the "best baseline"
clause selects it whichever way it is read: the per-language reading picks the same row
(`ua` 0.8918, `ru` 0.8849 are both its own), so the two readings coincide here and no second
decision is needed.

### The consequence that has to go back to the operator: G1d's bar is above 1.0

**A macro-F1 cannot exceed 1.0, so G1d as written can no longer be passed by any model.**
0.9084 + 0.10 = **1.0084**. This is arithmetic, not a prediction about the fine-tune.

It is not something this decision created, and the OpenRouter anchor was no better — it was the
*other* gate that was impossible:

| anchor | G1d bar | G1e bar |
|---|---|---|
| OpenRouter fp8 (Phase 3 row) | 0.9898 — reachable | **1.0211 — unreachable** |
| own-pod NF4 (the decision) | **1.0084 — unreachable** | 0.9974 — reachable |

So the condition predates 4a: **no anchor makes both +10 pp gates satisfiable**, because
`gemma-4-31b-it` zero-shot already scores above 0.90 on both heads and a +10 pp gate over a >0.90
baseline has no room left. SPEC §5's "a failed gate closes the question; negative result is a
result" is about a fine-tune that did not deliver — a threshold no model can reach is a
mis-specified gate, not a negative result, and reporting it as one would be dishonest.

The executor does not touch this: G1d/G1e's wording is `docs/SPEC.md` §5, a team-lead file, and
thresholds are immutable without operator approval (`CLAUDE.md`; SPEC §10). **Flagged before 4b is
scoped.** Recorded here so the number is in the vault whatever is decided.

### The slice file the scorer cannot read

`scorer.sarcasm_slice_fix_rate(y_true, base_pred, tuned_pred)` recomputes its slice internally as
`[i for i, gold in enumerate(y_true) if base_pred[i] != gold]` — one label column, and no argument
through which a caller could pass `results/g1b_slice.json`. So the persisted 44-id union and the
arithmetic that will compute G1b's fix-rate are, today, two different definitions of the slice.
4a's contract was to persist the slice and it did; **4b cannot consume it without a change to
`scorer.py`**, and scorer arithmetic is not something the executor changes on its own
(`docs/PROMPT-4a.md` DO-NOT; SPEC §5). Flagged for the operator before 4b is scoped, not worked
around. The baseline decision above sharpens it rather than settling it: G1b's slice is now
unambiguously the own-pod row's 44 ids, and `scorer.sarcasm_slice_fix_rate` still cannot be handed
them.

**Sources:** `docs/PROMPT-4a.md` rev. 1 · SPEC amendment 3.4 · `scripts/show_results.py` over
`results/baselines.json` (both rows) · `results/g1b_slice.json` · `scripts/runbook_4a.md` ·
`implementation-notes.md` § Phase 4a · related [[3b-infra-and-precision]],
[[phase4-base-model-gate]], [[hybrid-sarcasm-holdout-3.2]], [[gpu-provider-runpod]],
[[g1d-gate-clarification-3-3]].
