"""The suite stamp — what pytest ran, written by pytest, read by `scripts/baselines.py`.

A contract's Baselines block quotes a suite count, and until now that count travelled through a
human's memory (Dv553). This is the other end of the fix: the number is written by the run that
produced it, together with WHICH selection produced it, so `make baselines` can refuse to call a
one-file run «the suite».
"""

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STAMP = REPO_ROOT / ".suite-stamp.json"
COUNTED = ("passed", "failed", "error", "skipped", "xfailed", "xpassed")


def pytest_terminal_summary(terminalreporter):
    stats = terminalreporter.stats
    args = list(terminalreporter.config.args)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    STAMP.write_text(
        json.dumps(
            {
                "at": datetime.now(UTC).isoformat(timespec="seconds"),
                "commit": head.stdout.strip() or "(not a git checkout)",
                "args": args,
                # `testpaths = ["tests"]` is what a bare `pytest` resolves to, so the whole suite
                # is that and nothing else. Anything narrower is named rather than counted.
                "whole_suite": args in ([], ["tests"], [str(REPO_ROOT / "tests")]),
                "counts": {kind: len(stats.get(kind, [])) for kind in COUNTED},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
