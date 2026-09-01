# Harness note — brain-init module M6 «two-tier» (2026-08-30, applied to `~/.claude/skills/brain-init`)

Team-lead file. Provenance of a change to the operator's GLOBAL executor-side skill, made from this
project; the skill itself holds the result (templates under `templates/two-tier/`, `scaffold.py` M6
branch, `evals/evals.md` E6, backups in `.m6-backup-2026-08-30/`). Nothing in this repo changed.

## Why
Every two-tier project rebuilt the same harness by hand (this one: a week in August — `/plan-phase`,
`/report`, the sweep-refusing hook, deny rules, PROCESS/STATUS/PHASE formats). The operator ruled
30.08: `brain-init` (Claude Code) + `team-lead` (Cowork) must be a seamless start kit.

## What M6 installs in a new project (copies, refuse-overwrite, idempotent)
`docs/PRODUCT.md` · `docs/PROCESS.md` · `docs/STATUS.md` skeletons (the team lead fills them after
the kickoff interview) · `docs/templates/PHASE-TEMPLATE.md` §1–§8 (§8 = the `/goal` predicate) ·
`docs/{plans,reports,reviews}/` · `.claude/commands/plan-phase.md` + `report.md` (ported from this
repo) · `implementation-notes.md` (Deviations, cause-tag enum) · `Makefile` (`check`, `hooks-selftest`) ·
`scripts/hooks/refuse_sweeping_commands.py` (this repo's v2 + `--selftest`) with its PreToolUse(Bash)
entry · `permissions.deny` +7 (10 total) · CLAUDE.md «Two-tier workflow» block + full team-lead list.
Deliberately NOT templated: pins/sealed records/`moved_pins`, `check-stamped`, `preflight`,
`baselines`, PROMPT-*.md — project-specific, switched on by a PROCESS decision when needed.

## Evidence (on a copy of the skill, then on the real one)
Patch: 12 anchors matched, all-or-nothing. E6 on the copy: manifest complete; deny 10; PreToolUse
`Bash`; selftest 12/9/0; `git add -A` → exit 2, `git add src/x.py` → exit 0; no `{{…}}` left; no
Cyrillic in artifacts; CLAUDE.md 76 lines; rerun → 0 writes, no duplicate deny/hook entries.
E1 regression without M6: deny 3, no Two-tier block, no `docs/` — unchanged. Real skill after apply:
`two-tier/` present, `scaffold.py` parses, M6 dry-run scaffold = 33 entries, selftest green.

## Cowork side
`team-lead` skill: cadence line «kickoff in a repo without `docs/PROCESS.md` → `/brain-init` with
M6 first; the interview then fills PRODUCT → PROCESS → STATUS → the first PHASE» — proposed as a
skill card 30.08 (the skill is account-synced; edited from claude.ai, not from the repo).
