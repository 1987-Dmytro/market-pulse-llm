---
type: decision
id: dec-2026-07-31-3b-infra-and-precision
date: 2026-07-31
status: accepted
tags: [decision]
---

# Phase 3b runs on OpenRouter at a pinned precision, not on a rented GPU

**Context:** Phase 3b owes the zero-shot rows of the Phase 3 baseline table — three open
candidates plus the Claude Haiku reference row ([[frontier-api-reference-baseline]]). The plan of
record put them on a rented A6000, which is also where [[gpu-provider-runpod]] pointed. Inference
for 758 frozen rows per model is not what a GPU-hour buys.

**Decision (2026-07-31, operator, pre-registered before any number was produced):** all four
zero-shot rows run through **OpenRouter** (one provider, one key, OpenAI-compatible endpoint),
at a **single precision pinned by the rule below**, under a **hard $8 cap** for all of 3b. No GPU
is rented in this step; [[gpu-provider-runpod]] stands unchanged for Phase 4 training and its
top-up moves to the Phase 4 gate.

## (a) Why the zero-shot rows left the rented A6000

The work is 758 short requests per model — 400 frozen comments, 250 frozen posts, 108 holdout
rows — repeated for four models. On a rented A6000 that is roughly $12 of GPU-hours, most of it
spent downloading weights and idling while four different models are loaded in turn. On
OpenRouter it is roughly $2 of tokens and no idle minute is paid for. Nothing that decides a
number changes: the same frozen inputs, the same prompts, and `src/market_pulse/scorer.py` is
still the only thing that computes a metric. What is bought is the machine the weights sit on,
and that is not an input to any gate.

## (b) The precision rule, fixed before any number was seen

Zero-shot numbers move with the serving precision, so the precision was decided by a rule written
down before the probe ran and before a single row was scored:

> If `bf16` is offered for **all three** candidates → bf16 everywhere. Otherwise → `fp8` for all
> three. Never mix precisions across candidates, never fall back silently. If neither covers all
> three at any provider → stop and report.

**Probe outcome (2026-07-31, `GET /api/v1/models/<slug>/endpoints`).** Endpoints offering each
precision, per candidate:

| candidate | bf16 | fp8 | other |
|---|---|---|---|
| `google/gemma-4-31b-it` | CoreWeave, OpenInference, Venice, Novita | DeepInfra, SiliconFlow, Parasail | fp4 ×4, fp16 ×1, unknown ×6 |
| `qwen/qwen3.6-27b` | **none** | Io Net, Chutes, SiliconFlow, DeepInfra, Venice, Alibaba, CoreWeave | unknown ×2 |
| `qwen/qwen3.5-9b` | DeepInfra, Parasail | SiliconFlow, Venice | unknown ×1 |

`qwen/qwen3.6-27b` has no bf16 endpoint at any provider, so the **`otherwise` branch fired: fp8
for all three**. fp8 exists for all three, so no stop condition was met. Every request pins
`provider.order` to one endpoint tag with `allow_fallbacks: false` and
`quantizations: ["fp8"]`; the runner re-reads the endpoint list at start-up and refuses to run
if the pinned tag no longer reports fp8.

**Which provider serves each candidate** is not fixed by the rule above, so a second rule was
written down before the pins were chosen: among the fp8 endpoints, keep those OpenRouter reports
as healthy (`status == 0`) and accepting the parameters every request sends, then take the
cheapest, tie-broken on `uptime_last_1d`. It selects:

| candidate | pinned endpoint | fp8 | $/Mtok in · out | uptime 1d |
|---|---|---|---|---|
| `google/gemma-4-31b-it` | `parasail/fp8` | fp8 | 0.150 · 0.400 | 98.9% |
| `qwen/qwen3.6-27b` | `io-net/fp8` | fp8 | 0.280 · 1.990 | 99.6% |
| `qwen/qwen3.5-9b` | `venice/fp8` | fp8 | 0.100 · 0.150 | 96.3% |

The two cheapest fp8 endpoints (`deepinfra/fp8` for Gemma, `chutes/fp8` for Qwen3.6) were both
deranked by OpenRouter at probe time (`status: -2`, 5-minute uptime 0% and 89%) and lost on the
health clause, at a cost of $0.02 for the whole run. Choosing a deranked endpoint would have
bought that back in missing rows, and a missing row is worse than an expensive one — see (e).

**Licences, as actually found** (the candidate list is the operator's and was not re-selected):
`google/gemma-4-31b-it` → **Apache-2.0** (`license: apache-2.0` on the model card; the
`license_link` at `ai.google.dev/gemma/docs/gemma_4_license` is itself titled "Apache License
2.0"), *not* the Gemma Terms of Use the candidate list assumed — Gemma 4 changed licence family.
`qwen/qwen3.6-27b` and `qwen/qwen3.5-9b` → **Apache-2.0**, verbatim Apache text in each repo's
`LICENSE`. All three slugs exist on OpenRouter, as does `anthropic/claude-haiku-4.5:batch`.

The Haiku reference row cannot join the pin: every Anthropic-served endpoint reports
`quantization: "unknown"`, so there is nothing to pin. It is routed to the first-party `anthropic`
endpoint with `allow_fallbacks: false` and no `quantizations` clause. This does not violate "never
mix precisions across candidates" — Haiku is not a candidate, it anchors no gate, and its number is
reference only.

## (c) The $8 cap

Hard cap **$8 across all of 3b**, expected spend $1.50–2.50, against an OpenRouter balance of
$9.84 that will not be topped up for this step. The cap is enforced by the runner, not by
discipline: spend is read back from OpenRouter itself (`GET /api/v1/credits`, delta against the
usage recorded when the first 3b run started) and re-checked during the run, so it counts runs
that crashed and runs whose records were never written. Hitting the cap aborts the run and reports;
it never becomes "just a little more". A per-run cap is printed before any spend and enforced the
same way.

## (d) The honest caveat, and the cross-check that answers it

These numbers come from third-party serving endpoints. fp8 is pinned and the provider is pinned,
but nothing here controls the serving stack: kernels, batching, sampling implementation and the
tokenizer build all belong to Parasail, Io Net and Venice, and **provider-side determinism is not
guaranteed** — the same request may not return the same tokens twice. Every record carries the
provider slug, the quantization, the prompt SHA256 and that warning.

Therefore: **the model chosen at the Phase 4 gate gets one zero-shot re-run on our own GPU during
the Phase 4 smoke**, on the same frozen inputs with the same prompt, as a cross-check against its
OpenRouter row. If the two disagree materially, the GPU number is the one Phase 4 anchors G1d and
G1e on, and the disagreement is recorded rather than averaged away. The other two candidates are
never re-run — by then they are not the base model.

## (e) Missing rows, pre-registered before the first request

A row that never comes back is not a row a model got wrong, and the scorer's own contract says
macro averages must run on identical instances or paired comparison quietly stops being true.
Fixed before any spend:

- **`parse_failures`** — a response arrived but is not valid output (not JSON, missing a field, a
  label outside its domain). Counted, reported with its `n` and the row ids, **excluded** from
  scoring. Never coerced to a default label: a model that cannot answer must not be handed the
  majority class.
- **`api_failures`** — no usable response after retries. Counted **separately**, reported the same
  way, excluded the same way.
- Every record stores the ids actually scored per input, and their SHA256, so Phase 4 can
  reproduce the exact paired subset a gate was anchored on.
- If unusable rows exceed **2%** of any input, the record is written with
  `gate_anchor_valid: false` and the run is not silently used as the G1d/G1e anchor; the operator
  decides whether to re-run.

**One thing this ADR does not decide.** Amendment 3.2 defines the G1b slice as the holdout rows
the base model "misclassifies", and the holdout carries two labels — `sentiment` and `sarcasm`.
The executor does not pick the reading. Every candidate's run reports **both** error sets and
their union with separate `n`, and the choice belongs to the operator at the Phase 4 gate.

**Sources:** docs/PROMPT-3b.md rev. 2 (operator constraints, 2026-07-31) · docs/SPEC.md §5, §7,
amendments 3.1–3.3 · OpenRouter `/api/v1/models/<slug>/endpoints`, probed 2026-07-31 ·
related [[gpu-provider-runpod]], [[frontier-api-reference-baseline]], [[architecture-stack]].
