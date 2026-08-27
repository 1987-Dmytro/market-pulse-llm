# PROMPT-4a — Phase 4a: pod bootstrap + own-pod zero-shot re-run (rev. 1)

**Phase 4 opened at the 2026-08-01 briefing.** The base model is locked:
`google/gemma-4-31b-it`, branch (2) — QLoRA on an NF4 4-bit base, RunPod
A6000 48 GB. This step contains **NO training**: it stands up the pod, builds
the local inference path that will later score every gate, and produces the
own-pod zero-shot run that (a) cross-checks the OpenRouter fp8 row,
(b) anchors G1d/G1e, and (c) defines the G1b slice. The training smoke and
the two full ablation arms are step 4b, after this report is accepted.

RunPod balance is $35.00 (operator top-up 2026-08-01, verified). Expected 4a
pod spend: ~$1–2 of the $25 Phase 4 cap.

## Read first (these sections only, not the whole documents)

- `docs/SPEC.md` — the **amendment 3.4** block in the header, and §5 (gates).
- `knowledge/decisions/phase4-base-model-gate.md` — §(c), §(d).
- `knowledge/decisions/3b-infra-and-precision.md` — §(d), §(e), §(f).
- Your own hot.md footguns (auto-loaded at session start).

**Read-back check — before any file change, answer in one line each:** the
ablation selection rule; the Phase 4 dollar cap and the per-arm hour ceiling;
what defines the G1b slice; which row anchors G1d/G1e from now on.

## Step 0 — session entry

1. `git status`. Expect modified team-lead files from the Phase 3 close plus
   today's briefing edits (docs/STATUS.md, docs/SPEC.md, docs/PROMPT-4a.md,
   knowledge/daily_logs/2026-07-31.md, knowledge/index.md). Show
   `git diff --stat`, then commit them all as ONE commit:
   `docs: phase 3 close state; phase 4 opens — amendment 3.4 and prompt 4a`
   (committing team-lead files is your job; editing them is not).
2. **Write-tool probe (F1 empirics):** attempt a Write-tool write to
   `docs/STATUS.md`. Expected: permission denial before the file is touched.
   Paste the verbatim refusal into the report. Do NOT retry via other tools.
3. hot.md: the Phase 3 close is done — curate the Next list accordingly.

## Step 1 — local eval backend (before any pod spend)

Goal: `scripts/eval_zero_shot.py --backend local` (OpenRouter stays the
default) or an equivalent module that REUSES the existing prompt builder,
JSON parser, failure taxonomy, record builder, per-row dump writer and scorer
path. The design is yours; these are fixed:

- **Byte-identical prompts.** The local path asserts its prompt SHA256 equals
  the 3b records' and refuses to run otherwise.
- Model load: `google/gemma-4-31b-it`, bitsandbytes NF4 4-bit, double
  quantization on, compute dtype bf16. Record ALL quant parameters in the
  record's config — this exact config is also step 4b's training base and the
  serving default.
- Generation: temperature 0 / greedy, seed 42 recorded, bounded
  max_new_tokens, batching as memory allows (greedy — batch size must not
  change outputs).
- Failure taxonomy mirrors 3b §(e): parse_failures + generation_failures
  (no API bucket here), counted, ids named, excluded, never defaulted to a
  label. The 2% rule applies: over 2% unusable on any input → **stop and
  report**. No re-run loops.
- Provenance additions: GPU model, driver + CUDA, torch / transformers /
  bitsandbytes versions, pod id, quant config.
- New pyproject extra `gpu` (torch, transformers, bitsandbytes, accelerate).
  No test may import any of them (same rule as the `baseline`/`xlmr`
  extras); unit-test the new plumbing with the model call mocked: prompt-SHA
  assert, dump sorting, record fields, failure buckets. `make check` stays
  green on a bare checkout.

## Step 2 — pod runbook + budget guard

`scripts/runbook_4a.md` (executor file), commands the operator could replay:

- runpodctl: create a ~100 GB network volume, then an A6000 48 GB pod
  attached to it (CUDA image); download `google/gemma-4-31b-it` onto the
  volume; env install from the `gpu` extra.
- **Budget guard, enforced not prose:** `results/spend_phase4.json` anchored
  like spend_3b (never regenerate it); a guard script reads RunPod billing
  before any start and refuses when the $25 Phase 4 cap is reached. Print
  remaining budget before and after every pod session.
- Idle discipline: stop the pod the moment a step ends; never leave it
  running unattended. Show the stopped state at the end of the session.

## Step 3 — the own-pod zero-shot run (one run)

- All 758 frozen rows: 400 comments + 250 posts + 108 holdout. One run.
- Per-row prediction dump (sorted by (input, id); ids + predicted labels
  only — no gold, no source text), sha256 in the record: the step-3c
  contract.
- Record → `results/baselines.json` through the scorer only. This row is the
  G1d/G1e anchor (amendment 3.4) — gate fields stay valid.
- **G1b slice:** persist the explicit id list — union(sentiment ∪ sarcasm
  errors on the holdout) — to `results/g1b_slice.json` with its sha256,
  referenced from the record. If the union is under 100 rows, amendment
  3.2's fallback wording applies: report the n, change nothing.
- **Cross-check table** for the report: own-pod vs the OpenRouter fp8 row on
  every gated head + relevance; deltas shown, nothing averaged. Disagreement
  is a result, not a bug — the own-pod number anchors regardless (3b §(d)).

## Step 4 — RECORD (same session)

- ADR `knowledge/decisions/phase4-own-pod-anchor.md`: the own-pod run as the
  G1d/G1e anchor, the G1b slice (n, sha, file), the cross-check outcome with
  deltas, the NF4 config as the training/serving base. Link it in INDEX.
- hot.md: numbers + next. `implementation-notes.md` kept current throughout;
  **Deviations section mandatory** — write "none" if none.

## Verify-gate — run and SHOW the output

1. `make check` — green; report the test count.
2. `python3 scripts/show_results.py --last` — the new row.
3. Dump + slice file exist; recompute both sha256; show they match the record.
4. The prompt-SHA equality own-pod vs 3b — shown explicitly.
5. Spend: ledger total, remaining of $25; pod stopped (show status).
6. `git log --oneline` for the session — atomic commits, dependencies first.

## Report

Summary (3 plain lines first), the cross-check table, G1b slice n, spend,
test count, Deviations, open questions. Then STOP — no self-acceptance; the
team lead reviews against this checklist.

## DO NOT

- Do not edit `docs/STATUS.md`, `docs/SPEC.md` or `docs/PROMPT-*.md` —
  team-lead files (File ownership). Step 0 commits them, nothing more.
- No training, no peft/LoRA code, no serverless work in 4a.
- No changes to prompt text, frozen files, scorer arithmetic,
  `results/spend_3b.json`, or the six existing 3b records.
- Never `--force` any freeze/mining script; never merge synthetic rows into
  a real-source file.
- No re-run loops: a cap trip or the 2% rule → stop and report.
- `results/baselines.json` is append-only, via the scorer.
- All artifacts in English.
