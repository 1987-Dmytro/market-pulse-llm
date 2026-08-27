#!/usr/bin/env bash
# PreToolUse(Bash) guard — refuses the two commands this repo has been burned by.
# Exit 2 blocks the tool call and feeds stderr back to Claude (Claude Code hook contract).
# Both directions are tested in tests/test_hooks.py on this very script.
CMD=$(python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',d).get('command',''))" 2>/dev/null || true)
if [[ "$CMD" =~ git[[:space:]]+add[[:space:]]+(-A|--all|-a|\.)([[:space:]]|$) ]]; then
  echo "refused by hook: stage BY PATH (git add <file>...), never the whole tree — CLAUDE.md Rules" >&2
  exit 2
fi
if [[ "$CMD" =~ (^|[[:space:];&|])make[[:space:]]+fmt([[:space:]]|$) ]] || [[ "$CMD" =~ ruff[[:space:]]+format[[:space:]]+\.([[:space:]]|$) ]]; then
  echo "refused by hook: repo-wide format is forbidden (producer pins) — ruff format <the one file you touched>" >&2
  exit 2
fi
exit 0
