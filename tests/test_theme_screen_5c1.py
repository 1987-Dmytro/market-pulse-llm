"""Offline tests for the market screen — no Telegram, no store writes.

One thing here can quietly destroy a result: a second pass overwriting the first. The pass-1
record is the evidence behind five theme exclusions and cannot be re-derived, because the
composition it measured no longer exists.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import theme_screen_5c1 as screen  # noqa: E402


def test_a_second_pass_refuses_to_overwrite_the_first():
    """The five exclusions of 2026-08-07 cite this file. A re-run over today's registry writes a
    table that cannot contain their rows — the channels left it — so the default path is closed."""
    assert screen.RECORD.exists(), "the pass-1 record is the thing being protected"
    with pytest.raises(SystemExit, match="already exists"):
        screen.main([])


def test_a_named_path_runs_the_screen_and_writes_there(tmp_path):
    """The escape hatch has to actually work, and the record it writes has to be a record: the
    guard is only acceptable because a later pass has somewhere to go."""
    out = tmp_path / "theme_screen_pass2.json"
    assert screen.main(["--out", str(out)]) == 0

    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["channels"], "a screen with no channels measured nothing"
    assert record["tracked_groups"] == list(screen.TRACKED)
    assert json.loads(screen.RECORD.read_text(encoding="utf-8"))["channels"], "pass 1 untouched"
