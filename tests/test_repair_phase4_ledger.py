"""The phase-ledger repair: read the numbers, refuse the guesses, append exactly once.

Three paid sessions ran after `results/spend_phase4.json` was last appended and lived only in their
own step ledgers. Repairing that is a write into the one file the guard reads to decide whether a
run may start, so the things that can go wrong are the expensive quiet ones: a number typed instead
of read, a history re-scored under a cap that did not exist yet, an entry appended twice.

Driven against COPIES of the phase ledger in `tmp_path`. The step ledgers are read live and never
written — they are what the repair is derived FROM.
"""

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _module(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


repair = _module("repair_phase4_ledger")
guard = _module("runpod_guard")


@pytest.fixture
def ledger(tmp_path):
    """A copy of the phase ledger as it stands, so a test never writes the committed artifact."""
    path = tmp_path / "spend_phase4.json"
    path.write_bytes(repair.LEDGER.read_bytes())
    return path


def sessions_of(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["sessions"]


def test_every_number_is_read_from_the_step_ledger_and_none_is_typed(ledger):
    """The whole point: `spent_usd` is the anchor minus a balance the SESSION recorded, not a figure
    someone reconstructed afterwards. Re-derived here from the step ledgers directly, so a typo in
    the producer cannot agree with a typo in the test."""
    before = sessions_of(ledger)
    assert repair.main(["--ledger", str(ledger)]) == 0
    after = sessions_of(ledger)
    assert after[: len(before)] == before, "an append, never a rewrite of what was already there"
    appended = after[len(before) :]
    assert len(appended) == len(repair.MISSING) == 3

    anchor = json.loads(ledger.read_text(encoding="utf-8"))["runpod_balance_at_phase4_start"]
    for (source, _), written in zip(repair.MISSING, appended, strict=True):
        run = json.loads((REPO_ROOT / source).read_text(encoding="utf-8"))["runs"][-1]
        assert written["at"] == run["at"]
        assert written["balance"] == run["balance"]
        assert written["spent_usd"] == round(anchor - run["balance"], 4)
        assert source in written["note"], "an entry that cannot name its source is not evidence"


def test_the_history_is_scored_under_the_cap_that_was_in_force_not_todays(ledger):
    """SPEC 3.18 (3) raised the cap to $30.00 on 2026-08-13, after all three of these sessions. A
    repaired entry scored against $30.00 would report room those runs never had — so the constant
    is this module's own literal and is asserted to be DIFFERENT from the one the guard enforces.
    """
    assert repair.CAP_IN_FORCE_USD == 25.00
    assert guard.PHASE_CAP_USD == 30.00
    assert repair.CAP_IN_FORCE_USD != guard.PHASE_CAP_USD

    assert repair.main(["--ledger", str(ledger)]) == 0
    for written in sessions_of(ledger)[-3:]:
        assert written["remaining_usd"] == round(25.00 - written["spent_usd"], 4)
        assert "$25.00 cap IN FORCE" in written["note"]


def test_the_anchor_and_the_existing_entries_are_carried_through_untouched(ledger):
    """An anchor rewritten silently restarts the counter — the footgun the ledger's own note names.
    The repair reads every other field and writes it back as it found it."""
    before = json.loads(ledger.read_text(encoding="utf-8"))
    assert repair.main(["--ledger", str(ledger)]) == 0
    after = json.loads(ledger.read_text(encoding="utf-8"))
    assert {key: value for key, value in after.items() if key != "sessions"} == {
        key: value for key, value in before.items() if key != "sessions"
    }
    assert after["runpod_balance_at_phase4_start"] == 35.0
    assert after["anchored_at"] == "2026-08-01T08:34:09+00:00"


def test_a_dry_run_prints_the_entries_and_writes_nothing(ledger, capsys):
    raw = ledger.read_bytes()
    assert repair.main(["--ledger", str(ledger), "--dry-run"]) == 0
    assert ledger.read_bytes() == raw
    printed = capsys.readouterr().out
    assert "NOT written" in printed
    for source, _ in repair.MISSING:
        assert source in printed


def test_a_second_run_refuses_and_writes_nothing(ledger):
    """Idempotent by refusal, which is the honest shape: the second run cannot tell a re-run from a
    session that legitimately shares a timestamp, so it stops instead of appending a duplicate."""
    assert repair.main(["--ledger", str(ledger)]) == 0
    raw = ledger.read_bytes()
    with pytest.raises(SystemExit, match="already carries an entry at"):
        repair.main(["--ledger", str(ledger)])
    assert ledger.read_bytes() == raw


def test_a_missing_step_ledger_refuses_and_writes_nothing(ledger, monkeypatch):
    """The number would have to be typed, and a typed number in a spend ledger is a claim nobody
    can re-derive."""
    monkeypatch.setattr(repair, "MISSING", (("results/spend_never_existed.json", "x"),))
    raw = ledger.read_bytes()
    with pytest.raises(SystemExit, match="the step ledger is missing"):
        repair.main(["--ledger", str(ledger)])
    assert ledger.read_bytes() == raw


def test_a_step_ledger_with_no_paid_run_refuses(ledger, tmp_path, monkeypatch):
    empty = tmp_path / "results"
    empty.mkdir()
    (empty / "spend_empty.json").write_text(json.dumps({"runs": []}), encoding="utf-8")
    monkeypatch.setattr(repair, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(repair, "MISSING", (("results/spend_empty.json", "x"),))
    with pytest.raises(SystemExit, match="no paid run to append"):
        repair.main(["--ledger", str(ledger)])


def test_an_entry_that_is_not_after_the_last_one_refuses_and_writes_nothing(ledger):
    """A phase ledger is a time-ordered append. If the last entry already postdates the sessions
    being repaired, something has been logged that this script cannot reason about — and quietly
    appending out of order would make the file unreadable as a history."""
    body = json.loads(ledger.read_text(encoding="utf-8"))
    body["sessions"].append(
        {"at": "2026-08-13T00:00:00+00:00", "balance": 11.0, "spent_usd": 24.0, "note": "later"}
    )
    ledger.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    raw = ledger.read_bytes()
    with pytest.raises(SystemExit, match="is not strictly after"):
        repair.main(["--ledger", str(ledger)])
    assert ledger.read_bytes() == raw
