# Paste-ready prompt for Claude Code — step 3b
# (agreed at the 2026-07-28 joint step review; do not edit before pasting)

SPEC Phase 3, step 3b: GPU baselines runbook + zero-shot candidate evals.
Read docs/SPEC.md §5 (gates, amendments 3.1-3.3) and §7 (model plan), plus
the structure of results/baselines.json. State assumptions.

OPERATOR-APPROVED CONSTRAINTS (pre-registered, 2026-07-28):
- Budget cap for ALL of 3b: $20 (expected $5-10). Hitting the cap = STOP and
  report, never "a little more". Track estimated spend in the report.
- Precision policy: all open candidates evaluated in bf16 on a rented
  RunPod A6000 48GB (Secure Cloud, EU region if available) - uniform
  precision, decision-grade numbers. Record precision + GPU in provenance.
- Frontier reference row: Claude Haiku via API (ANTHROPIC_API_KEY in .env),
  reference only, never a gate anchor.

TASKS
1. ADR + INDEX: 3b-budget-and-precision.md (the two constraints above,
   rationale one line each).
2. Candidate refresh: web-search the CURRENT best open models for UA/RU
   classification fine-tuning as of the run date (check at minimum:
   Gemma 4 12B, Qwen3 8B/14B, latest Llama; licenses; vLLM support).
   Pick <=3 candidates, record versions + rationale in the ADR. If Gemma 4
   lacks stable vLLM support, fall back to transformers and record it.
3. scripts/runbook_3b.md - the operator-facing runbook (English, exact
   commands): create pod (A6000, image, network volume ~50GB), rsync the
   frozen sets + holdout + registry, run steps, teardown checklist
   ("pod terminated" is a checklist item - idle pods burn money).
4. Automation the runbook calls:
   - scripts/eval_zero_shot.py: vLLM batch inference, fixed prompt per task
     (T1 comment: sentiment+sarcasm+intents; T2 post: relevance+type+brands),
     strict output parsing with a parse-failure counter (unparseable ->
     counted, reported, excluded from scoring with its n);
   - XLM-R fine-tune + eval (train on real sources ONLY - synthetic is
     ablation-gated for Phase 4, not for baselines);
   - scripts/eval_frontier.py: same prompts via Anthropic API (Haiku), runs
     locally, ~$1-3;
   - every eval writes through src/market_pulse/scorer.py into
     results/baselines.json (append-only), including per-candidate G1b
     "base model errs on N of 108 holdout rows" - that N defines each
     candidate's slice.
5. Offline tests for pure parts (prompt building, output parsing, result
   assembly). No network in pytest.
6. Atomic commits: (a) docs: 3b ADR (b) feat: zero-shot and frontier eval
   harness (c) docs: runbook 3b.

DO NOT: no QLoRA/training code (Phase 4). No changes to scorer logic,
frozen files, or gates. No model choice conclusions in the report - numbers
go to the file, the choice happens at the Phase 4 gate with the operator.

VERIFY and show: make check; dry-run of eval_zero_shot.py --smoke (mocked
client) output; runbook table of contents; git log --oneline -3.
Then walk the operator through the runbook step by step.
