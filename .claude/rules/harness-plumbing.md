---
paths:
  - ".claude/**"
  - "scripts/brain-*"
  - "scripts/refresh-hot-cache.py"
  - "scripts/stale-check.sh"
  - "scripts/context-census.py"
  - "scripts/check-wikilinks.py"
---
# Harness plumbing — hooks, generated regions, operator commands

Moved out of `CLAUDE.md` on 2026-08-19 by `boot-debloat` (the joint sitting's group D),
verbatim: still true, and needed only by a session that opens the files below.

- Hooks in `.claude/settings.json`: SessionStart runs `scripts/refresh-hot-cache.py`,
  `scripts/stale-check.sh` and `scripts/context-census.py`; Stop runs
  `scripts/brain-session-end.py`, which regenerates `knowledge/index.md` and the daily-log stub.
  Generated regions belong to those scripts — do not hand-edit them.
- `/save` (checkpoint) and `/close` (end of day) in `.claude/commands/` are operator-invoked only.
