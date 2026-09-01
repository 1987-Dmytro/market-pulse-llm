"""The suite-wide ledger tripwire — proof it BITES, on a file it is allowed to move.

`tests/conftest.py :: no_test_writes_a_real_ledger` asserts at session teardown that none of the
three spend ledgers moved. A session fixture that never fires and a session fixture that cannot
fire look identical from inside the run, so its comparison is exercised here on a temp file
([[a_checker_whose_failure_is_silence]]).
"""

import json

import conftest


def test_the_detector_sees_a_changed_ledger(tmp_path):
    """A write is a different digest. This is the state the leak produced: the anchor untouched,
    one session appended — a change that leaves the file valid JSON and the anchor intact, which is
    why «is it still parseable» would not have caught it."""
    path = tmp_path / "spend_cycle3.json"
    path.write_text(json.dumps({"cycle3_cap_usd": 4.8, "sessions": []}), encoding="utf-8")
    before = conftest.digest(path)
    path.write_text(
        json.dumps({"cycle3_cap_usd": 4.8, "sessions": [{"note": "probe-b CLOSED"}]}),
        encoding="utf-8",
    )
    assert conftest.digest(path) != before


def test_the_detector_is_quiet_when_nothing_moved(tmp_path):
    """The other direction: a detector that reported a move on every run would be turned off by
    the first person it stopped."""
    path = tmp_path / "spend_cycle2.json"
    path.write_text("{}", encoding="utf-8")
    assert conftest.digest(path) == conftest.digest(path)


def test_anchoring_a_missing_ledger_reads_as_a_move(tmp_path):
    """The state the cycle-2 leak of Dv424 was in: the file did not exist, and a test ANCHORED it.
    If absence and emptiness both read as None-equals-None the tripwire would sleep through exactly
    the one-shot write it exists to catch."""
    path = tmp_path / "spend_phase4.json"
    before = conftest.digest(path)
    assert before is None
    path.write_text("{}", encoding="utf-8")
    assert conftest.digest(path) != before


def test_the_tripwire_watches_every_ledger_the_guard_can_write(tmp_path, monkeypatch):
    """The list is closed by its anchor unless something re-derives it. Both leaks happened because
    a protection named the lines that existed when it was written, so this reads the guard's own
    ledger constants and demands the tripwire cover each one
    ([[a_guards_list_is_closed_by_its_anchor]])."""
    import importlib.util
    from pathlib import Path

    script = Path(__file__).resolve().parents[1] / "scripts" / "runpod_guard.py"
    spec = importlib.util.spec_from_file_location("runpod_guard_probe", script)
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)

    writable = {
        guard.LEDGER.name,
        guard.CYCLE2_LEDGER.name,
        guard.CYCLE3_LEDGER.name,
        guard.cycle3_path().name,
    }
    assert writable <= set(conftest.LEDGERS), (
        f"the guard can write {sorted(writable - set(conftest.LEDGERS))}, which the tripwire in"
        " tests/conftest.py does not watch — add it to LEDGERS"
    )
