#!/usr/bin/env python3
"""The Baselines block a contract pastes — measured here, at the moment it is asked for.

**Why this exists.** Three contracts in a row carried a Baselines block written from the team
lead's memory, and three times a number in it was from another moment: the census that predated a
`/save` curation, a suite count from before the last commit, a porcelain list that no longer
matched the tree (Dv549, Dv553). A block a human retypes is a block that ages between the writing
and the reading. This prints the same block from the instruments, so a contract's baselines are
INSTRUMENT OUTPUT with a timestamp on them and never a recollection.

Every line here is a reading, not a judgement: nothing is compared against a target and nothing
exits non-zero. The one thing it refuses to do is invent the suite count — pytest stamps it
(`tests/conftest.py`), and with no stamp this says so instead of printing a number from anywhere
else.

    python3.11 scripts/baselines.py
    make baselines
"""

import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import preflight  # noqa: E402

STAMP = REPO_ROOT / ".suite-stamp.json"
"""Where `tests/conftest.py` records what pytest last ran. Gitignored: it is a reading of this
working tree at one moment, and a committed copy would be one run behind whoever reads it."""

BOOT_FILES = (
    Path.home() / ".claude" / "CLAUDE.md",
    Path.home() / "CLAUDE.md",
    REPO_ROOT / "CLAUDE.md",
    REPO_ROOT / "knowledge" / "hot.md",
)
"""The always-loaded files the census sums, MEMORY.md apart — it has two axes of its own."""


def memory_index() -> Path:
    slug = re.sub(r"[^a-zA-Z0-9]", "-", str(REPO_ROOT))
    return Path.home() / ".claude" / "projects" / slug / "memory" / "MEMORY.md"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    ).stdout.rstrip("\n")


def census_line() -> str:
    """The census script's own printed line — run, never re-implemented."""
    out = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "context-census.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    return out.stdout.strip() or out.stderr.strip() or "(census produced no line)"


def suite_line() -> str:
    """What pytest last ran, from its own stamp — including WHICH selection it ran.

    A stamp from `pytest tests/test_one.py` says 11 passed and is not the suite count; printing it
    as one would be the same defect this file exists to remove, a step down.
    """
    if not STAMP.exists():
        return "NOT STAMPED — run `make check` (the stamp is written by pytest itself)"
    stamp = json.loads(STAMP.read_text(encoding="utf-8"))
    counts = " / ".join(
        f"{stamp['counts'].get(kind, 0)} {kind}"
        for kind in ("passed", "failed", "error", "skipped")
        if stamp["counts"].get(kind)
    )
    selection = " ".join(stamp["args"]) or "(default)"
    whole = "whole suite" if stamp["whole_suite"] else f"PARTIAL RUN: {selection}"
    return f"{counts} — {whole}, stamped {stamp['at']} at {stamp['commit'][:12]}"


def sizes() -> list[str]:
    out = []
    for path in BOOT_FILES:
        size = path.stat().st_size if path.exists() else 0
        name = str(path).replace(str(REPO_ROOT) + "/", "").replace(str(Path.home()), "~")
        out.append(f"{name} {size} B")
    index = memory_index()
    if index.exists():
        text = index.read_text(encoding="utf-8")
        units = len(text.encode("utf-16-le")) // 2
        out.append(
            f"MEMORY.md {index.stat().st_size} B = {len(text.splitlines())} lines /"
            f" {units} UTF-16 units"
        )
    return out


def pins() -> str:
    """The pin registry, counted — and how many paths every pin on them still matches.

    The tail of that sentence is not an alarm and must not read as one. A record pins a file as it
    was at ITS moment, so a file two contracts have edited since carries older pins by design; what
    `make preflight ARGS='<path>'` reports is the same question scoped to the paths one task
    touches, which is where a stale pin is a finding. Here it is a population count.
    """
    registry = preflight.pin_registry()
    records = {record for entries in registry.values() for record, _, _ in entries}
    total = sum(len(entries) for entries in registry.values())
    missing, older = 0, 0
    for path, entries in registry.items():
        live = preflight.digest(path)
        if live is None:
            missing += 1
        elif any(sha and sha != live for _, _, sha in entries):
            older += 1
    tail = f"{len(registry) - missing - older} match every pin on them, {older} carry an older pin"
    if missing:
        tail += f", {missing} MISSING on disk"
    return f"{len(registry)} pinned paths · {total} pins · {len(records)} records — {tail}"


def block() -> str:
    porcelain = git("status", "--porcelain") or "(clean)"
    lines = [
        f"## Baselines — instrument output, {datetime.now(UTC).isoformat(timespec='seconds')}",
        "",
        f"- head: {git('rev-parse', '--short=12', 'HEAD')} on {git('rev-parse', '--abbrev-ref', 'HEAD')}",
        "- porcelain:",
        *[f"    {line}" for line in porcelain.splitlines()],
        f"- census: {census_line()}",
        f"- suite: {suite_line()}",
        "- boot files: " + " · ".join(sizes()),
        f"- preflight: {pins()}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    print(block())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
