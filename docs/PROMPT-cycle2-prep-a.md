# PROMPT — cycle2-prep-a (3.19 skip rule + batch-parity projection; $0)

**Contract class:** zero-cost, code + paper. No GPU, no endpoints, no spend, no prereg.
**Issued:** 2026-08-15 (team lead). **Baseline:** `make check` 2 332 passed / 2 skipped @ `b2ff741`.

## Context (read these sections, nothing wholesale)

- `docs/SPEC.md` — ONLY the block `<!-- amendment-3.19 begin/end -->` (~lines 870–892); background: amendment 3.18 (7). SPEC is pinned whole by sealed preregs — NEVER edit it.
- `knowledge/hot.md` — "What's Hot" / "Next" / "Blockers". You own this file; it carries load-bearing grepped literals — run `make check` after any edit to it.
- Phase 5 closed 2026-08-14 (5c2). This is cycle-2 prep, first of two zero-cost contracts; prep-b (collection: corpus catch-up + Сільпо/Varus leaflets) follows separately after this one is accepted.

## Step 0 — commit the standing tail (checked against live git status this morning)

The working tree carries exactly: `docs/STATUS.md`, `knowledge/daily_logs/2026-08-14.md`, `knowledge/hot.md`, `knowledge/index.md` (the 14.08 close edits). Commit them verbatim by path — `docs/STATUS.md` is a team-lead file: commit, never edit. Commit this prompt file too (it arrives untracked). Then curate `knowledge/hot.md`: mark "Next" item 7 (5c2-close acceptance / Dv327) RESOLVED — the team lead ratified the `.claude/rules/` routing on 2026-08-15 — and run `make check` after the edit. This session's own vault tail goes into its own final commit, as usual.

## Deliverable 1 — the 3.19 skip rule in the inference queue

Law (the intent of amendment 3.19): text-less comments are excluded from the inference QUEUE before payment. A QUEUE rule, not deletion: rows stay collected, watermarked and counted; distributions report on text rows; the text-less count is printed beside them as its own class; the bought window (anchor 09.08) stays as bought.

- **Seam:** the queue-building path in `src/market_pulse/loop.py` whose depth `scripts/run_loop.py` reports as `rows_to_inference`. Unchanged on the other side of the seam: collection and watermark semantics, `data/loop_cursor.json` (schema AND values — the history-backlog latch is OUT of scope), census counting, every sealed artifact.
- **ONE text predicate.** Locate the predicate the 5c2 pipeline actually used to establish "3 714 with text / 1 361 text-less at source" and reuse IT; name its location in the report. If it lives inline today, lift it into one shared function and point both consumers at it. Never write a second definition.
- **Reporting:** the loop's per-pass summary and its written record carry the split: text rows queued + `text_less_skipped` as its own class.
- **Tests, both directions, plus a window regression:** (i) a row with text is never skipped; (ii) a text-less row never enters the paid queue AND stays collected/counted; (iii) the committed 5c2 window artifacts reproduce the 3 714 / 1 361 split through the new path — numbers READ from the artifact, not typed into the test.
- **Consumers** (team-lead preflight — re-run the enumeration and carry the count in your report): queue/cursor semantics touch `src/market_pulse/loop.py`, `scripts/run_loop.py`, `scripts/census_5c2.py`, `scripts/collect_5c1.py`, `tests/test_loop.py`, `tests/test_census_5c2.py`; prose consumers exist in `knowledge/hot.md` (queue notes — update yours; team-lead files are not yours to update). Query the graph as well (`graphify query "what reads loop.py"`); confirm the post-commit hook rebuilt it, else run the update.

## Deliverable 2 — batch-parity projection ($0, paper only)

Output: `results/batch_cycle2_projection.json` (with a `provenance` block naming every anchor path) + a reading in the report. Beside EVERY price, name the SAMPLE it was measured on — the registrations-and-draws rule should inject when you touch projection files; if no system-reminder shows it loaded, open `.claude/rules/registrations-and-draws.md` by hand.

Anchors (all on disk, verified by the team lead this morning):
- `results/spend_5c2run.json` — the only population-priced serverless anchor (5 278 rows bought).
- `results/parity_srv2.json` — srv-2d parity, batch 1, 758 rows.
- `results/serving_5b.json` — the pod cost anchor.
- `results/batch_ladder_5b2.json`, `results/batch_5b2_projection.json`, `results/batch_5b2_verdict.json` — the failed pod batch attempt (ladder chose 16; OOM at 666/758 on A6000 48 GB).

Answer, from records only: (a) candidate batch sizes for serverless RTX 4090 24 GB given the recorded A6000 OOM — say explicitly what is derivable from records and what needs a live probe, and mark the latter NOT MEASURABLE rather than estimating it into a number; (b) what a new prereg would measure and against which anchors — gate evals stay batch 1 forever per 3.11 (2); the candidate is the production loop's row price ONLY; (c) the measurement session's own cost per candidate (boot + warm-up + N rows at measured serverless prices); (d) break-even at −30% and −50% row price against reference volumes (history 11 143; one cycle window ≈ the 5c2 window).

**HARD STOP:** no prereg written, no SPEC edit, no GPU/pod/endpoint, no spend. The projection returns to the team lead; the money line is an open operator decision.

## DO NOT

- Do not edit `docs/STATUS.md`, `docs/SPEC.md`, `docs/PRODUCT.md`, `docs/PROMPT-*.md` — team-lead files (File ownership). Step 0 commits them verbatim.
- Do not touch `data/loop_cursor.json` (goal: the history backlog stays exactly recoverable later; its latch is a future contract's lever).
- Do not create any RunPod resource or spend anything (goal: today is a $0 day by operator ruling — the paid fork is the operator's alone).
- Do not write or modify any prereg / sealed / pinned artifact; `results/spend_5c2run.json` and all spend anchors are closed.
- Do not collect anything from Telegram — collection is prep-b.
- Never `git add -A`; stage by path.

## Autonomy

D1: free within the seam (`loop.py` + its tests + the shared predicate); any record-schema change beyond adding the skip counters → STOP and report. D2: numbers only from the named anchors; no invention.

## Verify (evidence, not assertions)

`make check` green (baseline 2 332/2 — expect growth); paste the pytest tail. Show the per-pass summary line from the existing stub-served smoke path with the new split visible. Show the projection JSON path and its `provenance` block.

## Report

`docs/reports/cycle2-prep-a.md`, commit `docs(report): cycle2-prep-a`; chat gets ONLY the path. Deviations in `implementation-notes.md` AND cited in the report — numbering continues after Dv329 — each with `[cause: contract-gap | spec-gap | env | tooling | model | process]`; close with "Process signals" (≤5 lines). End with the house `/save`; your write-list only.

## Read-back first (answer in one line each, before any edit)

1. What does the queue rule do, and what does it never do?
2. Where will the single text predicate live?
3. The projection's STOP boundary?
4. Step-0 commit list?
