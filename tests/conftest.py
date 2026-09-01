"""The suite stamp — what pytest ran, written by pytest, read by `scripts/baselines.py`.

A contract's Baselines block quotes a suite count, and until now that count travelled through a
human's memory (Dv553). This is the other end of the fix: the number is written by the run that
produced it, together with WHICH selection produced it, so `make baselines` can refuse to call a
one-file run «the suite».
"""

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

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


LEDGERS = ("spend_phase4.json", "spend_cycle2.json", "spend_cycle3.json")
"""The three money records `scripts/runpod_guard.py` can WRITE. Every one is a one-shot anchor plus
an append-only session log, so a stray write is not a value a later run corrects — it is a number
the line is measured against from then on."""


@pytest.fixture(autouse=True, scope="session")
def no_test_writes_a_real_ledger():
    """The suite may not move a real spend ledger. Session-scoped and repo-wide, on purpose.

    Dv424 caught this once for cycle 2 — repealing 3.23 (2)'s $40.00 floor let the next `make check`
    anchor the production ledger at a fixture's $22.00 — and the remedy was an autouse redirect in
    `tests/test_runpod_guard.py`. That redirect names ONE constant, so opening cycle 3 reproduced the
    same event immediately: the guard read `CYCLE3_LEDGER` directly, the fixture knew nothing about
    it, and a `--close --note` test appended «probe-b CLOSED at $0.3132» to the live line at a
    fixture's $22.07 balance.

    The redirect is still the fix, and `cycle3_path()` makes the successor follow the ledger the
    redirect patches. This is the thing that FAILS when a fourth line, another module or a direct
    read reopens the hole — because both of the previous two times, the protection existed and did
    not cover the new name ([[a_guards_list_is_closed_by_its_anchor]]).
    """
    before = {name: digest(REPO_ROOT / "results" / name) for name in LEDGERS}
    yield
    moved = [name for name in LEDGERS if digest(REPO_ROOT / "results" / name) != before[name]]
    assert not moved, (
        f"the suite wrote a real spend ledger: {moved}. A test drove the guard with a ledger path"
        " it did not redirect — patch it into tmp_path (see tests/test_runpod_guard.py"
        " :: never_the_real_ledgers) rather than relaxing this."
    )


def digest(path: Path) -> str | None:
    """The file's bytes, or None when it does not exist — the absent state has to be one of the
    readings, or anchoring a ledger that was missing would read as «unchanged»."""
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
