# Paste-ready prompt for Claude Code — step 3c (Phase 3 close-out)
# rev. 1, agreed at the 2026-07-31 evening joint gate review. Paste as-is.
#
# Context: the operator accepted 3b's zero-shot work and made four decisions
# at the gate review. They are pre-registered here — do NOT re-litigate:
#   G1. Base model for Phase 4 = google/gemma-4-31b-it (won every gated
#       head and beat the frontier reference row).
#   G2. Pairing: the 27B row's missing instances are closed by a BOUND
#       ANALYSIS in an ADR, $0 — not by a re-run. The team-lead review
#       found per-row predictions were never persisted, so the notes'
#       claim "a paired re-score ... is reproducible from the file" is
#       FALSE. That finding is recorded, not hidden.
#   G3. G1b slice = UNION of sentiment+sarcasm errors, DEFINED by the
#       chosen model's zero-shot re-run on our own pod during the Phase 4
#       smoke (full 108 rows, our hardware, per-row outputs persisted).
#       OpenRouter's 40/108 is a preview, not the slice.
#   G4. XLM-R: the full run starts TONIGHT on this Mac's CPU — the
#       operator lifts the 60-minute ceiling for an overnight run.

SPEC Phase 3, step 3c: record the gate decisions, fix the persistence gap
forward, launch the XLM-R overnight run. This step spends $0.
Read implementation-notes.md (sections "The three candidate rows are not
paired" and "Deviations"), knowledge/decisions/3b-infra-and-precision.md
§(e)-(f), and docs/SPEC.md §5 (paired-comparison clause). State your
assumptions before writing code.

Read back to me in ONE LINE EACH before implementing: the four decisions
G1-G4, and where the per-run failed_ids live in the 3b records.

TASKS

1. CORRECTION, not an edit. Append a dated subsection "Correction
   (2026-07-31, team-lead review)" to implementation-notes.md: per-row
   predictions and holdout error ids were never persisted;
   results/baselines.json carries only scored_ids_sha256 and error COUNTS;
   therefore the paired re-score "from the file" claimed above it does not
   exist, and the $0 paired option offered to the operator rested on that
   false claim. The original sentence stays as written — the correction
   sits under it. Do not soften either.

2. Per-row prediction dump — the permanent guard. For every real scoring
   run, scripts/eval_zero_shot.py must persist
   results/predictions/<sanitized-slug>--<UTC-ts>.jsonl, one line per
   scored row: {"input": ..., "id": ..., "pred": {...}}. Ids and predicted
   labels ONLY — no gold labels, no source text. The run record gains
   config.predictions_path and config.predictions_sha256. Offline tests:
   dump written, schema stable, sha matches, record points at an existing
   file. Do NOT backfill dumps for the six existing 3b runs — they cannot
   be reconstructed and must not be faked.

3. ADR knowledge/decisions/phase4-base-model-gate.md + INDEX entry.
   One short paragraph each:
   (a) gate decision G1, with the headline macro-F1 per gated head taken
       from scripts/show_results.py output — no numbers from memory;
   (b) the bound analysis: from each run-2 dropped instance (failed_ids:
       3/400 comments, 1/250 posts, 4/108 holdout) and the gold labels in
       the frozen files, compute the worst-case paired shift of Gemma's
       score per gated head (worst case = Gemma was perfect on every
       dropped row), and compare each bound against the observed
       Gemma-vs-27B gap on that head. Show the arithmetic in the ADR.
       If ANY gated head's ordering is not protected by its bound, STOP
       and report before writing a conclusion — the operator holds a
       ~$0.90 paired re-run in reserve for exactly that case.
       Otherwise conclude: the unpaired table cannot flip the selection;
       the 27B rows keep gate_anchor_valid: false permanently.
   (c) G3 verbatim: union reading; the slice is defined by the own-pod
       Phase 4 smoke re-run with persisted per-row outputs; OpenRouter's
       40/108 is a preview;
   (d) the persistence gap (task 1) and the forward fix (task 2).
   Amend, do not overwrite, 3b-infra-and-precision.md: one line under
   §(e) pointing at this ADR. Update INDEX.md.

4. Housekeeping. Commit the modified stragglers
   (knowledge/daily_logs/2026-07-31.md, knowledge/index.md). Refresh the
   curated section of knowledge/hot.md: 3b zero-shot closed and accepted;
   the four gate decisions with a wikilink to the new ADR; XLM-R overnight
   run in flight; next = morning record commit, Phase 3 close, RunPod
   top-up, Phase 4 briefing. Add one footgun: "the six 3b zero-shot
   records carry no per-row predictions — never claim paired re-scoring
   from them; dumps exist only from 3c onward."

5. LAST, only after all commits are in and the tree is clean: launch the
   XLM-R full run in the background on CPU. Add xlmr_full_run.log to
   .gitignore first, then use the full-run command from
   scripts/runbook_3b.md wrapped for an unattended night:
     caffeinate -i nohup <full-run command> --device cpu \
       > xlmr_full_run.log 2>&1 &
   Verify it survives: show the PID, wait ~2 minutes, tail the log,
   confirm steps advance and the projected wall clock is consistent with
   the ~131+ min floor. Then give the operator morning-check instructions:
   the exact tail command, what a finished run prints, and that the record
   lands in results/baselines.json via the same scorer, append-only, to be
   committed in the morning session. The record and your report must state
   per-gate coverage explicitly: G1b null (fix-rate needs the Phase 4
   fine-tune), G1e "NOT ATTEMPTED" (no token-classification head) — never
   a silent blank.

6. Atomic commits, repo green after each:
   (a) docs: notes correction, gate ADR, INDEX, 3b ADR amendment
   (b) feat: per-row prediction dumps + tests
   (c) chore: hot.md refresh, knowledge stragglers, gitignore
   (the overnight launch itself commits nothing tonight)

DO NOT
- No OpenRouter requests, no API spend of any kind. This step costs $0.
- No changes to scorer logic, gate definitions, frozen files, or the six
  existing 3b records (append-only; the correction lives in the notes).
- No re-litigation of G1-G4 — they are operator decisions; transcribe.
- No backfilled or synthesized prediction dumps for past runs.
- No MPS, no epoch/MAX_LENGTH/architecture changes to XLM-R: the baseline
  runs exactly as pre-registered; only the wall-clock ceiling moved.

VERIFY and show
- make check output;
- the names of the new dump tests in the pytest output;
- the bound-analysis numbers exactly as they appear in the ADR;
- ps output for the training PID and the last 5 log lines after ~2 min;
- git log --oneline -3 and git status --short (only the running log
  untracked).

Keep implementation-notes.md updated, including the Deviations section —
silence is not compliance. Close your report with the operator's
morning-check instructions.
