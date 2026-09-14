#!/usr/bin/env python3
"""Print the standing prompt — `make session`, the one command that starts an executor session.

The prompt is the team lead's (`docs/PROMPT-standing.md`, v3 of ruling 10.09 (ss)) and it lives in
exactly one fenced block of that file. Printing it from the file is the point: a copy pasted into
the Makefile or into a runbook would be a second spelling that goes stale the next time the team
lead revises the prompt, and the operator would paste the stale one into a fresh process.

The block is NOT selected by ordinal. A file with no fenced block, or with more than one, is a
named non-zero exit rather than a guess about which of them the operator meant — counting fences
is how a runbook once ran its PURCHASE section ([[a_block_selected_by_ordinal_runs_the_wrong_block]]).

    make session
    python3.11 scripts/session_prompt.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPT = REPO_ROOT / "docs" / "PROMPT-standing.md"


def blocks(text: str) -> list[list[str]]:
    """Every fenced block's body, in order."""
    found: list[list[str]] = []
    body: list[str] | None = None
    for line in text.splitlines():
        if line.startswith("```"):
            if body is None:
                body = []
            else:
                found.append(body)
                body = None
        elif body is not None:
            body.append(line)
    return found


def main() -> int:
    if not PROMPT.exists():
        print(f"session REFUSED: {PROMPT.relative_to(REPO_ROOT)} is missing", file=sys.stderr)
        return 1
    found = blocks(PROMPT.read_text(encoding="utf-8"))
    if len(found) != 1:
        print(
            f"session REFUSED: {PROMPT.relative_to(REPO_ROOT)} carries {len(found)} fenced blocks,"
            " and the standing prompt is the one of them — say which in the file, never here",
            file=sys.stderr,
        )
        return 1
    print("\n".join(found[0]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
