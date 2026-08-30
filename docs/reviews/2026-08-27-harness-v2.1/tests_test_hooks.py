"""Both directions of the PreToolUse guard v2, on the real script — including the seven spellings
the v1 guard let through (Dv875) and the commit-message false positive it used to block (Dv874)."""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "scripts" / "hooks" / "refuse_sweeping_commands.py"

REFUSED = [
    "git add -A", "git add .", "git add --all", "git add -u", "git add :/", "git stage -A",
    "git -C . add -A", "git add -A --dry-run", "cd x && git add .",
    "make fmt", "ruff format", "ruff format .", "ruff format --check .", "ruff format src tests",
    "ruff format docs/", "python3 -m ruff format .",
]
ACCEPTED = [
    "git add docs/STATUS.md docs/PROCESS.md", "git add -A-not-a-flag.txt",
    "git commit -m 'never git add -A: see CLAUDE.md'", "git commit -F msg.txt",
    "echo 'make fmt is forbidden'", "grep -rn 'ruff format .' docs/",
    "make check", "make preflight", "ruff format tests/test_hooks.py", "ruff check .",
]


def _run(command: str) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_input": {"command": command}})
    return subprocess.run([sys.executable, str(HOOK)], input=payload, text=True, capture_output=True)


def test_refuses_every_spelling_of_the_sweep():
    for bad in REFUSED:
        r = _run(bad)
        assert r.returncode == 2, f"let through: {bad!r}"
        assert "refused by hook" in r.stderr


def test_accepts_targeted_forms_and_mere_mentions():
    for good in ACCEPTED:
        r = _run(good)
        assert r.returncode == 0, f"blocked: {good!r} — {r.stderr}"
