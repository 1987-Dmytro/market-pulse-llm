"""Both directions of the PreToolUse guard, on the real script — a guard nobody has seen refuse is
not a guard (team-lead skill v2.1 §4)."""
import json
import subprocess
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "scripts" / "hooks" / "refuse-sweeping-commands.sh"


def _run(command: str) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_input": {"command": command}})
    return subprocess.run(["bash", str(HOOK)], input=payload, text=True, capture_output=True)


def test_refuses_the_sweeps():
    for bad in ("git add -A", "git add . && git commit -m x", "make fmt", "ruff format ."):
        r = _run(bad)
        assert r.returncode == 2, bad
        assert "refused by hook" in r.stderr


def test_accepts_the_targeted_forms():
    for good in ("git add docs/STATUS.md docs/PROCESS.md", "git commit -m 'x'", "make check",
                 "ruff format src/market_pulse/prompts.py", "git add -A-not-a-flag.txt"):
        r = _run(good)
        assert r.returncode == 0, good
