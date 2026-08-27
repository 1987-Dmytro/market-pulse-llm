# PROMPT-4-close — Phase 4 close-out (mechanical, rev. 1)

The 4c report is ACCEPTED by the team lead (independent bit-exact recompute,
one-attempt protocol confirmed, operator quiz 2/2). Phase 4 is closed at
**2 of 5**, arm real-only selected. Phase 5 is PAUSED by operator decision —
do not scope, plan or start anything beyond this list.

1. `git status`; commit today's team-lead edits (docs/STATUS.md — the Phase 4
   close, docs/PROMPT-4-close.md untracked) plus your day records, one commit:
   `docs: phase 4 closed at 2 of 5 — acceptance, pause before phase 5`.
2. Flip `knowledge/decisions/phase4-gate-verdict.md` front-matter
   `status: proposed` → `status: accepted`; mirror the INDEX line. This is
   the team-lead acceptance instruction the "proposed" status was waiting on.
3. `runpodctl` — delete the EXITED pod `gxkdecf3g7k3y7`. The network volume
   (100 GB, CA-MTL-3) is KEPT — its fate is a Phase 5 briefing decision.
   Show the pod list after (expect: empty) and append the spend ledger with
   a timestamped balance reading.
4. hot.md: curate — phase closed at 2/5, no open blockers, deliverable =
   `results/train/4c-arm-a/adapter` (unmerged, NF4), Next = the operator's
   pre-Phase-5 discussion; footguns that survive the phase stay (batch-1
   rule, no-merge-until-measured, spend anchors, frozen-file guards).
5. `/save`.

DO NOT: edit docs/STATUS.md, docs/SPEC.md, docs/PROMPT-* beyond committing
them; touch any record, dump, slice or frozen file; delete the network
volume; start anything Phase-5-shaped. Report the four outputs (commit,
ADR flip, pod list + ledger line, hot.md diff summary) in a few lines.
