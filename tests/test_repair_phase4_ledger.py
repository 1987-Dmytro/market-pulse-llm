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


LAST_BEFORE_THE_REPAIR = "2026-08-11T18:16:30+00:00"
"""sku-b-run — the last entry `results/spend_phase4.json` carried before this repair, and the two
days of silence that follow it are what the repair exists for."""


@pytest.fixture
def ledger(tmp_path):
    """The phase ledger as it stood BEFORE the repair ran, rebuilt from the committed file.

    A one-shot repair that has been shot cannot be driven against today's ledger: `main` would only
    ever reach the re-run refusal, and the assertions about what it APPENDS would never run. The
    pre-state is this file with every session from the first repaired timestamp onwards dropped —
    the three appended entries and the guard reading that followed them. Rebuilt rather than
    hand-written, so these tests keep reading the real anchor and the real history.

    Never the committed artifact itself: a test that wrote `results/spend_phase4.json` would be the
    silent regeneration the ledger's own note warns about.
    """
    body = json.loads(repair.LEDGER.read_text(encoding="utf-8"))
    first = min(
        json.loads((REPO_ROOT / source).read_text(encoding="utf-8"))["runs"][-1]["at"]
        for source, _ in repair.MISSING
    )
    body["sessions"] = [session for session in body["sessions"] if session["at"] < first]
    assert body["sessions"][-1]["at"] == LAST_BEFORE_THE_REPAIR
    path = tmp_path / "spend_phase4.json"
    path.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def test_the_repair_is_done_and_a_re_run_on_the_committed_ledger_refuses():
    """Idempotency on the real artifact rather than on a copy: the three entries are in, and the
    script's own refusal is what keeps a second invocation from doubling them. It stops on the
    first source, before any write — nothing here can touch the committed file."""
    with pytest.raises(SystemExit, match="already carries an entry at"):
        repair.main([])


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


# --- the permanent guard: a paid session may not leave the phase ledger silent ------------------

WITNESSED_BY_A_LATER_READING = {
    # Three historical paid runs whose phase entry exists but carries a DIFFERENT balance: the step
    # ledger's reading was taken while the session ran and the phase entry was written minutes later,
    # after teardown, when the account had absorbed more of the bill. Named one by one, with the
    # entry that witnesses each — a tolerance on the match would have swallowed the three sessions
    # this repair exists to find, which were not late readings but no readings at all.
    ("results/spend_5c1_vis.json", "2026-08-09T11:28:50+00:00"): "2026-08-09T11:31:48+00:00",
    ("results/spend_5c1_vis.json", "2026-08-09T13:03:50+00:00"): "2026-08-09T13:06:47+00:00",
    ("results/spend_sku_b.json", "2026-08-11T18:14:10+00:00"): "2026-08-11T18:16:30+00:00",
}
"""Paid runs excused from the exact-balance match, keyed on (step ledger, the run's own `at`).

Keyed per RUN and not per FILE on purpose: `results/spend_5c1_vis.json` has three runs that match
exactly and two that do not, and excusing the file would blind this check to the one ledger that has
already gone quiet twice."""


def silent_paid_runs(sessions: list[dict]) -> list[tuple[str, str, float]]:
    """Every paid step-ledger run that `sessions` does not witness, and the used excuses.

    A paid RunPod run is a step-ledger entry carrying a `balance` — which is what separates it from
    an OpenRouter `runs` row, whose fields are `model`/`usd`/`requests`.

    One direction only. The converse is not an invariant: the guard's own `--note` readings and the
    phase's close-out entries have no step ledger behind them and never will.
    """
    by_balance = {session["balance"] for session in sessions}
    by_at = {session["at"]: session for session in sessions}
    silent, excused = [], []
    for path in sorted((REPO_ROOT / "results").glob("spend_*.json")):
        if path.name == repair.LEDGER.name:
            continue
        body = json.loads(path.read_text(encoding="utf-8"))
        source = f"results/{path.name}"
        for key in ("runs", "gpu_sessions"):
            for run in body.get(key) or []:
                if "balance" not in run:
                    continue
                if run["balance"] in by_balance:
                    continue
                named = WITNESSED_BY_A_LATER_READING.get((source, run["at"]))
                if named is None or named not in by_at:
                    silent.append((source, run["at"], run["balance"]))
                    continue
                witness = by_at[named]
                assert witness["at"] > run["at"], (source, run["at"])
                assert witness["balance"] < run["balance"], (
                    f"{source} @ {run['at']} is excused as a LATER reading of the same session, and"
                    f" {named} does not read lower — so it is not that session's teardown reading"
                )
                excused.append((source, run["at"]))
    assert sorted(excused) == sorted(WITNESSED_BY_A_LATER_READING), (
        "an excuse that no longer applies is an excuse nobody looks at"
    )
    return silent


def test_no_paid_step_ledger_is_silent_in_the_phase_ledger():
    """What actually went wrong: three paid sessions ran, each wrote its own step ledger, and
    `results/spend_phase4.json` — the file the guard reads before every start — heard about none of
    them for two days. The phase counter stayed right by arithmetic and lost its witness.

    Matched on the balance READING, because that is the number both files carry and the one a
    mistyped entry would get wrong."""
    sessions = json.loads(repair.LEDGER.read_text(encoding="utf-8"))["sessions"]
    assert silent_paid_runs(sessions) == []
    # and the three this contract repaired are matched by the rule, not by an excuse
    for source, _ in repair.MISSING:
        run = json.loads((REPO_ROOT / source).read_text(encoding="utf-8"))["runs"][-1]
        assert (source, run["at"]) not in WITNESSED_BY_A_LATER_READING
        assert run["balance"] in {session["balance"] for session in sessions}


def test_the_silence_check_fires_when_a_phase_entry_goes_missing():
    """The negative control. A guard that has never been seen to fail is a guard nobody has tested:
    drop skub2's entry and the check has to name that ledger, that timestamp and that balance."""
    sessions = json.loads(repair.LEDGER.read_text(encoding="utf-8"))["sessions"]
    skub2 = json.loads((REPO_ROOT / "results" / "spend_skub2.json").read_text("utf-8"))["runs"][-1]
    without = [session for session in sessions if session["balance"] != skub2["balance"]]
    assert len(without) == len(sessions) - 1
    assert silent_paid_runs(without) == [
        ("results/spend_skub2.json", skub2["at"], skub2["balance"])
    ]


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
