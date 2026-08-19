"""`make baselines` — the block a contract pastes, and the stamp that keeps it honest.

The one property worth a test: a run that was not the whole suite may not be printed as if it
were. That is the whole of Dv553 in miniature — a number from another moment, reported as this
one's — and it is the only way this instrument could reintroduce the defect it removes.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import baselines  # noqa: E402

import conftest as stamper  # noqa: E402  (tests/conftest.py — the hook that writes the stamp)


class Reporter:
    """Enough of pytest's terminal reporter for the hook: the stats and the config's args."""

    def __init__(self, args, stats):
        self.stats = stats
        self.config = type("Config", (), {"args": args})()


def stamp(tmp_path: Path, monkeypatch, args, stats) -> dict:
    path = tmp_path / ".suite-stamp.json"
    monkeypatch.setattr(stamper, "STAMP", path)
    stamper.pytest_terminal_summary(Reporter(args, stats))
    monkeypatch.setattr(baselines, "STAMP", path)
    return json.loads(path.read_text(encoding="utf-8"))


def test_the_whole_suite_is_reported_as_the_suite(tmp_path, monkeypatch):
    written = stamp(tmp_path, monkeypatch, ["tests"], {"passed": [0] * 3001, "skipped": [0] * 3})
    assert written["whole_suite"] is True
    assert written["counts"]["passed"] == 3001
    line = baselines.suite_line()
    assert "3001 passed / 3 skipped" in line
    assert "whole suite" in line and "PARTIAL" not in line


def test_a_one_file_run_is_never_printed_as_the_suite(tmp_path, monkeypatch):
    """The defect this instrument exists to remove, pointing at itself: 11 passed is not 3 001."""
    written = stamp(tmp_path, monkeypatch, ["tests/test_baselines.py"], {"passed": [0] * 11})
    assert written["whole_suite"] is False
    line = baselines.suite_line()
    assert "11 passed" in line
    assert "PARTIAL RUN: tests/test_baselines.py" in line


def test_with_no_stamp_it_refuses_to_name_a_number(tmp_path, monkeypatch):
    monkeypatch.setattr(baselines, "STAMP", tmp_path / "nothing.json")
    assert baselines.suite_line() == (
        "NOT STAMPED — run `make check` (the stamp is written by pytest itself)"
    )


def test_the_block_carries_every_section_a_contract_pastes(capsys):
    assert baselines.main() == 0
    out = capsys.readouterr().out
    for section in (
        "- head:",
        "- porcelain:",
        "- census:",
        "- suite:",
        "- boot files:",
        "- preflight:",
    ):
        assert section in out, section
    assert "Ktok boot tax" in out
    assert "MEMORY.md" in out and "UTF-16 units" in out
    assert "pinned paths" in out and "pins" in out


def test_the_makefile_target_calls_this_script():
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "baselines:" in text
    assert "python3.11 scripts/baselines.py" in text
    assert ".PHONY:" in text and "baselines" in text.splitlines()[0]
