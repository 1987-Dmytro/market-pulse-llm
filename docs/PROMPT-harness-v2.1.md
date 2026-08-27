# PROMPT — `harness-v2.1` (fresh session; $0; mechanical — the executor's environment is brought in line with skill v2.1)

**Question this contract answers:** «Does the executor's environment now enforce the v2.1 loop —
phase spec → plan → review → go → report that answers first — by files and hooks, not by memory?»
**Artifact:** `docs/reports/harness-v2.1.md` whose first ten lines list each guard with its refusal
shown and its acceptance shown, and the SessionStart context cost before/after.

**Checks (run them; paste tails):** (1) `pytest tests/test_hooks.py -q` green — the hook refuses
`git add -A`, `git add .`, `make fmt`, `ruff format .` and accepts `git add <path>`, `make check`,
`ruff format <file>`; (2) an `Edit` on `docs/PHASE-x.md`, `docs/SPEC-v2-promo-pulse.md`,
`docs/labels-x.jsonl` is refused by `permissions.deny` (show the refusal, then delete the probe files);
(3) `python3 scripts/context-census.py` before and after — the SessionStart injection does not grow
(hot.md curated block ≤40 lines); (4) `make check`: no new red (2 known: ledger debt + none else expected
after step 0); (5) `/plan-phase` and `/report` appear in the command list.

**Step 0.** Commit by path `docs/PROCESS.md`, `docs/reviews/2026-08-27-harness-v2.1/**`, this prompt.
Confirm `tests/test_think_zero_shot.py::test_the_registration_rebuilds…` is GREEN at HEAD (the (ф) quotes
now live in STATUS's MACHINE-READ BLOCK) — paste the line.

**Apply, file by file, from `docs/reviews/2026-08-27-harness-v2.1/` (drafted by the team lead; copy,
do not paraphrase):** `CLAUDE.md` → repo root (replaces the 80-line one; ≤80 lines); `settings.json` →
`.claude/settings.json`; `refuse-sweeping-commands.sh` → `scripts/hooks/` (`chmod +x`);
`tests_test_hooks.py` → `tests/test_hooks.py`; `commands/*.md` → `.claude/commands/` (`plan-phase`,
`report` new; `save`, `close` replaced); `rules/reports-and-plans.md` → `.claude/rules/`. Create
`docs/plans/` with a `.gitkeep`. Trim `knowledge/hot.md`'s curated block to ≤40 lines (move the rest
into today's daily log). Update `knowledge/runbooks/tooling.md` «Relevant here» with the 27.08 decisions
in `docs/PROCESS.md` («MCP/plugins») — including enabling the `code-review` plugin, if the operator's
user-level settings allow it from the repo; otherwise state the exact `~/.claude/settings.json` line for
the operator.

**Archive, do not delete:** `git mv` every `docs/PROMPT-*.md` that NO script, test or sealed record
references (grep `PROMPT-` across `scripts/ tests/ results/*.json src/`; `make preflight` names the
pinned ones) into `docs/archive/prompts/`; list the ones that stay and why. Team-lead files move by path
only — never edited.

**Report.** `/report harness-v2.1` — answer first, then evidence per check, deviations with cause tags,
`make check` tail, HEAD. Do not touch `config/registry.yaml`, `results/`, or any team-lead file's content.
