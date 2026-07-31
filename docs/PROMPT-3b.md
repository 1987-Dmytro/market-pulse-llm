# Paste-ready prompt for Claude Code — step 3b
# rev. 2, agreed at the 2026-07-31 joint step review. Paste as-is, do not edit.
#
# CHANGELOG vs rev. 1 (2026-07-28) — the operator's infrastructure changed:
#   OpenRouter is funded ($9.84), RunPod is at $0.00 and its top-up is
#   deliberately deferred to the Phase 4 gate.
#   - Zero-shot candidates now run through the OpenRouter API instead of a
#     rented A6000. No GPU is rented in 3b.
#   - The frontier reference row goes through OpenRouter too; no
#     ANTHROPIC_API_KEY is needed.
#   - "bf16 on A6000" is replaced by a pre-registered precision RULE (task 2),
#     written down before any accuracy number exists.
#   - XLM-R trains locally on Apple MPS.
#   - Budget cap $20 -> $8 (below the actual OpenRouter balance).
#   - The candidate list is now FIXED by the operator; no live re-selection.

SPEC Phase 3, step 3b: zero-shot LLM baselines via OpenRouter + XLM-R
supervised baseline + frontier reference row.
Read docs/SPEC.md §5 (gates, amendments 3.1-3.3) and §7 (model plan), plus
the structure of results/baselines.json and src/market_pulse/scorer.py's
public surface. State your assumptions before you write code.

Before any implementation, read back to me in ONE LINE EACH: the five gates
G1a-G1e, and the pre-registered precision rule in task 2. If your read-back
is wrong I will stop you there.

OPERATOR-APPROVED CONSTRAINTS (pre-registered, 2026-07-31)

- Budget: hard cap $8 across ALL of 3b, expected $1.50-2.50. The OpenRouter
  balance is $9.84 and will not be topped up for this step. Hitting the cap =
  STOP and report, never "just a little more". The runner tracks spend and
  aborts by itself (task 4).
- Everything API-side goes through ONE provider: OpenRouter, key
  OPENROUTER_API_KEY in .env (OpenAI-compatible endpoint
  https://openrouter.ai/api/v1). No Anthropic key, no other vendor SDK.
- No GPU is rented in this step. RunPod stays the decided provider for
  Phase 4 training ([[gpu-provider-runpod]] stands); its top-up is deferred
  to the Phase 4 gate by operator decision.
- FIXED candidate list (operator decision, 2026-07-31, live search already
  done — do NOT re-select):
    1. google/gemma-4-31b-it        (~31B dense, Gemma Terms of Use)
    2. qwen/qwen3.6-27b             (~27B dense, Apache-2.0)
    3. qwen/qwen3.5-9b              (~9B dense, Apache-2.0 — the cheap floor)
  Verify each slug exists and record the licence you actually find; if a slug
  is gone, STOP and report rather than substituting a model yourself.
- Frontier reference row: anthropic/claude-haiku-4.5:batch via OpenRouter.
  Reference only — it never anchors a gate ([[frontier-api-reference-baseline]]).

TASKS

1. ADR + INDEX: knowledge/decisions/3b-infra-and-precision.md.
   Record, one short paragraph each: (a) why zero-shot moved from a rented
   A6000 to OpenRouter (cost ~$2 vs ~$12, no GPU-hours, same scorer, same
   frozen inputs); (b) the precision rule below and the fact it was fixed
   before any number was seen; (c) the $8 cap; (d) the honest caveat — these
   numbers come from third-party serving endpoints, so the model chosen at
   the Phase 4 gate gets ONE zero-shot re-run on our own GPU during the
   Phase 4 smoke, as a cross-check. Amend, do not overwrite,
   [[gpu-provider-runpod]]. Update INDEX.md.

2. PRECISION PROBE — do this before any scoring run, and write the outcome
   into the ADR from task 1.
   For each of the three candidate slugs call
   GET https://openrouter.ai/api/v1/models/<canonical_slug>/endpoints and
   list every endpoint with its provider slug and `quantization` field.
   Then apply this PRE-REGISTERED RULE verbatim:
     - if `bf16` is offered for ALL THREE candidates -> use bf16 everywhere;
     - otherwise -> use `fp8` for ALL THREE;
     - never mix precisions across candidates, and never fall back silently.
   Pin the routing explicitly on every request:
     "provider": {"order": ["<provider>/<variant>"], "allow_fallbacks": false,
                  "quantizations": ["<chosen>"]}
   If neither bf16 nor fp8 is available for all three at any provider, STOP
   and report — do not improvise a third option.

3. Prompts. One fixed prompt per task, identical for every model including
   the frontier row:
     T1 (comment): sentiment + sarcasm + intents
     T2 (post):    relevance + post type + brands
   Prompts live in a module (not inline strings scattered around) and their
   SHA256 goes into every result record. Ask for strict JSON output.

4. scripts/eval_zero_shot.py — ONE runner, `--model <slug>` selects the row;
   the frontier row is the same script with the Haiku slug plus
   `--reference-only`, which marks the record so no gate can read it.
   Do not write a second near-identical script.
   Requirements:
     - temperature 0, fixed max_tokens, batched with bounded concurrency;
     - strict output parsing with a parse-failure counter: an unparseable
       response is COUNTED, REPORTED with its n, and EXCLUDED from scoring —
       never silently coerced to a default label;
     - it scores three inputs: the frozen comment test set (400), the frozen
       post test set (250), and data/frozen/sarcasm_holdout.jsonl (108).
       The holdout scoring is what DEFINES each candidate's G1b slice —
       report "base model errs on N of 108" per candidate;
     - budget guard: estimate cost before the run, track actual spend during
       it (X-Generation-Id header -> GET /api/v1/generation?id=), abort at
       the $8 cap and at a per-run cap you print up front;
     - provenance per record: model slug, provider slug, quantization,
       prompt SHA256, temperature, run timestamp, commit, dirty paths —
       plus a note that provider-side determinism is NOT guaranteed;
     - numbers reach results/baselines.json ONLY through
       src/market_pulse/scorer.py, append-only, never hand-edited.

5. XLM-R supervised baseline — LOCAL, on this Mac (Apple MPS), $0.
   scripts/train_xlmr_baseline.py, train on REAL sources only
   (comments_train.jsonl + sarcasm_candidates.jsonl; synthetic_sarcasm.jsonl
   is ablation-gated for Phase 4 and must NOT be touched here).
   Run a timed SMOKE first (a few steps) and print an estimated full-run
   wall clock. If the estimate exceeds 60 minutes, STOP and report the
   estimate instead of starting the full run — the operator will move it to
   a GPU pod. Same scorer, same append-only results file.
   Put torch/transformers in a new `xlmr` optional-dependency extra in
   pyproject.toml, mirroring how `baseline` isolates sklearn: `make check`
   must stay green on a bare checkout and no test may import them.

6. Offline tests for the pure parts: prompt building, output parsing
   (including the failure counter), routing-config assembly, result-record
   assembly. NO network in pytest — mock the client.

7. scripts/runbook_3b.md — operator-facing, English, exact copy-paste
   commands in order: install extras, set OPENROUTER_API_KEY, precision
   probe, dry run, each candidate run, the Haiku reference run, the XLM-R
   smoke and full run, and how to read the table with
   scripts/show_results.py. Include a "what to do if the cap trips" section.

8. Atomic commits, repo green after each:
   (a) docs: 3b infra and precision ADR
   (b) feat: OpenRouter zero-shot eval harness + tests
   (c) feat: XLM-R supervised baseline
   (d) docs: runbook 3b

DO NOT
- No QLoRA, no fine-tuning of any generative model (that is Phase 4).
- No changes to scorer logic, gate definitions, frozen files or hashes.
- No touching data/frozen/*, synthetic_sarcasm.jsonl, or any *_pristine file.
- No model-choice conclusions in your report. Numbers go to the file; the
  choice happens at the Phase 4 gate with the operator.
- No new provider, no second API key, no substituting a candidate.
- Do not re-run scripts/freeze_testsets.py or any --force mining script
  (see knowledge/hot.md "Footguns").

VERIFY and show
- `make check` output;
- the precision probe table (candidate x provider x quantization) and which
  branch of the rule fired;
- `python scripts/eval_zero_shot.py --smoke` with a mocked client;
- the estimated cost printout before any real spend, and the actual spend after;
- `python scripts/show_results.py`;
- `git log --oneline -4` and `git status --short`.

Keep implementation-notes.md updated, including a "Deviations" section:
every departure from this contract is logged there and cited in your report.
Silence is not compliance. Then walk the operator through runbook_3b.md.
