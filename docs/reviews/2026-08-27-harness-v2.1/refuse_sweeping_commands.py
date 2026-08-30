#!/usr/bin/env python3
"""PreToolUse(Bash) guard v2 — refuses sweeping stage/format by BEHAVIOUR, not by spelling.

v1 matched four literal strings anywhere in the text: it blocked commit messages that merely
mentioned them (Dv874) and let seven other spellings of the same sweep through (Dv875). v2 parses
each command segment and judges its first tokens. Both directions in tests/test_hooks.py.
Hook contract: exit 2 blocks the call, stderr goes back to Claude; exit 0 passes.
"""
import json
import os
import re
import shlex
import sys

STAGE_SWEEPS = {"-A", "--all", "-u", "--update", ".", ":/", ":/.", ":."}
DIR_SWEEPS = {".", "src", "tests", "scripts", "config", "docs", "results", "knowledge"}


def refuse(msg: str) -> None:
    print(f"refused by hook: {msg}", file=sys.stderr)
    sys.exit(2)


def tokens_of(segment: str) -> list[str]:
    try:
        toks = shlex.split(segment)
    except ValueError:
        toks = segment.split()
    while toks and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]):
        toks.pop(0)  # leading env assignments
    return toks


def strip_git_globals(toks: list[str]) -> list[str]:
    i = 1
    while i < len(toks):
        if toks[i] in ("-C", "-c", "--git-dir", "--work-tree"):
            i += 2
        elif toks[i].startswith("-"):
            i += 1
        else:
            break
    return toks[i:]


def check_segment(segment: str) -> None:
    toks = tokens_of(segment)
    if not toks:
        return
    head = os.path.basename(toks[0])
    if head == "git":
        rest = strip_git_globals(toks)
        if rest and rest[0] in ("add", "stage"):
            args = rest[1:]
            if not args or any(a in STAGE_SWEEPS or a.startswith(":/") for a in args):
                refuse("stage BY PATH (git add <file>...), never the whole tree — CLAUDE.md Rules")
    elif head == "make":
        if "fmt" in toks[1:]:
            refuse("repo-wide format is forbidden (producer pins) — ruff format <the one file you touched>")
    elif head == "ruff" or (head.startswith("python") and toks[1:3] == ["-m", "ruff"]):
        rest = toks[1:] if head == "ruff" else toks[3:]
        if rest and rest[0] == "format":
            args = [a for a in rest[1:] if not a.startswith("-")]
            if not args or any(a in DIR_SWEEPS or a.rstrip("/") in DIR_SWEEPS or os.path.isdir(a) for a in args):
                refuse("repo-wide format is forbidden (producer pins) — name the ONE file you touched")


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    cmd = (payload.get("tool_input") or payload).get("command", "") or ""
    for segment in re.split(r"&&|\|\||;|\|", cmd):
        check_segment(segment)


if __name__ == "__main__":
    main()
