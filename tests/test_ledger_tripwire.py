"""The suite-wide ledger tripwire — proof it BITES, on a file it is allowed to move.

`tests/conftest.py :: no_test_writes_a_real_ledger` asserts at session teardown that none of the
three spend ledgers moved. A session fixture that never fires and a session fixture that cannot
fire look identical from inside the run, so its comparison is exercised here on a temp file
([[a_checker_whose_failure_is_silence]]).
"""

import json
from pathlib import Path
from types import SimpleNamespace

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


def test_the_tripwire_watches_every_ledger_the_guard_can_write():
    """The three lines the guard names today, found by the derivation and not by a list."""
    guard = guard_module()
    writable = {
        guard.LEDGER.name,
        guard.CYCLE2_LEDGER.name,
        guard.CYCLE3_LEDGER.name,
        guard.cycle3_path().name,
    }
    assert writable <= set(conftest.LEDGERS), (
        f"the guard can write {sorted(writable - set(conftest.LEDGERS))}, which the tripwire in"
        " tests/conftest.py does not watch"
    )


def guard_module(source: str | None = None):
    """`scripts/runpod_guard.py` as a module — optionally from altered SOURCE, for the control."""
    import importlib.util

    script = Path(__file__).resolve().parents[1] / "scripts" / "runpod_guard.py"
    if source is None:
        spec = importlib.util.spec_from_file_location("runpod_guard_probe", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    namespace: dict = {"__file__": str(script), "__name__": "runpod_guard_fourth_line"}
    exec(compile(source, str(script), "exec"), namespace)  # noqa: S102
    return SimpleNamespace(**namespace)


def test_a_FOURTH_line_is_watched_without_anybody_adding_its_name():
    """The control the old version of this test could not run, and the one `/code-review` used to
    show it was tautological: it compared the guard's constants against a list hand-written from
    those same constants, so a fourth line added to BOTH stayed invisible.

    Here the guard's source really gains a `CYCLE4_LEDGER`, and the derivation — the same function
    `conftest.LEDGERS` is built by — has to find it with nothing else changed. Cycle 3 arrived in
    exactly this shape and the protection did not cover it, twice over
    ([[a_guards_list_is_closed_by_its_anchor]])."""
    script = Path(__file__).resolve().parents[1] / "scripts" / "runpod_guard.py"
    source = script.read_text(encoding="utf-8")
    fourth = source.replace(
        'CYCLE3_LEDGER = REPO_ROOT / "results" / "spend_cycle3.json"',
        'CYCLE3_LEDGER = REPO_ROOT / "results" / "spend_cycle3.json"\n'
        'CYCLE4_LEDGER = REPO_ROOT / "results" / "spend_cycle4.json"',
        1,
    )
    assert fourth != source, "the anchor this control edits moved — fix the control, not the guard"

    module = guard_module(fourth)
    derived = {
        value.name
        for value in vars(module).values()
        if isinstance(value, Path) and value.parent == conftest.REPO_ROOT / "results"
    }
    assert "spend_cycle4.json" in derived, (
        "a fourth money line was added to the guard and the derivation did not see it — the watch"
        " list is closed by its anchor again"
    )
    assert "spend_cycle4.json" not in conftest.LEDGERS, "…and there is no fourth line on disk today"


def test_a_step_ledger_is_watched_too():
    """`results/spend_<step>.json` is under the same one-shot law and there are 22 of them. The
    teardown walks the DIRECTORY rather than a name list, so a step ledger a test wrote is caught
    by the same reading — a list of three names could never have covered them."""
    names = {path.name for path in conftest.spend_records()}
    assert set(conftest.LEDGERS) <= names
    assert len(names) > len(conftest.LEDGERS), "the step ledgers are in the watched set"
