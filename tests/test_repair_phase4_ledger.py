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
import sys
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
    """SPEC 3.18 (3) raised the cap to $30.00 on 2026-08-13, after all three of these sessions, and
    (7)(b) raised it to $33.00 the same day. A repaired entry scored against either would report
    room those runs never had — so the constant is this module's own literal and is asserted to be
    DIFFERENT from the one the guard enforces. The gap has now widened twice without this test
    changing its shape, which is what the pattern is for.
    """
    assert repair.CAP_IN_FORCE_USD == 25.00
    assert guard.PHASE_CAP_USD == 33.00
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


# --- the permanent guard: a paid session may not leave the LIVE ledger silent -------------------

LINE_LEDGERS = (guard.CYCLE2_LEDGER, guard.CYCLE3_LEDGER)
"""Every ledger a paid run may be witnessed in once Phase 4 is closed — DERIVED from the guard's own
constants, never restated here (`97e84e6`'s lesson: derive, never restate).

This was `results/spend_cycle2.json`, typed. Cycle 2 was superseded by cycle 3 on 01.09 and the
guard has written the line's sessions into `CYCLE3_LEDGER` since — so the FIRST paid step under the
new line read as SILENT while its witness sat in `results/spend_cycle3.json` at the same timestamp
and the same balance. Changed by ruling 02.09 (d) `[cause: ruling]`; the claim does not move — a
paid step witnessed by NONE of the guard's lines is still named, both directions shown on the stub.
"""
"""The ledger that witnesses a paid run once Phase 4 is closed — SPEC amendment 3.23 (1).

The check below was written when `results/spend_phase4.json` was the only place a paid session could
land, and it stayed green for a week because every step since had run under the phase. Phase 4 is
CLOSED now and `runpod_guard` writes a step's session into whichever ledger is LIVE, so the FIRST
paid step under the cycle-2 line reddened this test while being witnessed exactly as it should be
([[the_control_whose_premise_stopped_being_true]], [[a_green_suite_can_have_a_shelf_life]]).

The invariant was never «the phase ledger hears about it» — it is «the ledger the guard reads before
a start hears about it», and there are two of those now. Reading both is the version of that a test
can state, and it is strictly what the original check meant: a run witnessed by neither is still
named.
"""

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


def line_sessions() -> list[dict]:
    """Every session of every live line, in the guard's own order. A line with no file yet is not
    an error — `CYCLE3_LEDGER` did not exist until the first paid step under it."""
    return [
        session
        for path in LINE_LEDGERS
        if path.exists()
        for session in json.loads(path.read_text(encoding="utf-8"))["sessions"]
    ]


def silent_paid_runs(sessions: list[dict]) -> list[tuple[str, str, float]]:
    """Every paid step-ledger run that the LIVE ledgers do not witness, and the used excuses.

    A paid RunPod run is a step-ledger entry carrying a `balance` — which is what separates it from
    an OpenRouter `runs` row, whose fields are `model`/`usd`/`requests`.

    `sessions` is the phase ledger's, passed in so the negative control can drop one row from it;
    :data:`LINE_LEDGER`'s are read live and added, because after the phase closed that is where the
    guard writes. A run witnessed by neither is what this returns.

    One direction only. The converse is not an invariant: the guard's own `--note` readings and the
    phase's close-out entries have no step ledger behind them and never will.
    """
    line = line_sessions()
    by_balance = {session["balance"] for session in sessions} | {one["balance"] for one in line}
    by_at = {session["at"]: session for session in [*sessions, *line]}
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


def test_no_paid_step_ledger_is_silent_in_the_live_ledger():
    """What actually went wrong: three paid sessions ran, each wrote its own step ledger, and
    `results/spend_phase4.json` — the file the guard reads before every start — heard about none of
    them for two days. The phase counter stayed right by arithmetic and lost its witness.

    Matched on the balance READING, because that is the number both files carry and the one a
    mistyped entry would get wrong.

    Both live ledgers, since Phase 4 closed — and the premise is ASSERTED rather than assumed: an
    empty cycle-2 ledger would make the union silently equal to the phase ledger and this check
    would go on passing while testing the older half of it."""
    sessions = json.loads(repair.LEDGER.read_text(encoding="utf-8"))["sessions"]
    line = line_sessions()
    assert guard.closing_entry(sessions) is not None, "Phase 4 is closed and the line took over"
    assert line, "the cycle-2 ledger witnesses the steps that ran after the close"
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


LINE_SESSIONS_WITH_NO_STEP_LEDGER = {
    # Two cycle-2 entries whose balance no `results/spend_*.json` step ledger carries, so
    # `silent_paid_runs` cannot name them from either direction — it walks the step ledgers, and
    # for these there is nothing to walk. Enumerated per balance and asserted in BOTH directions
    # below, so a THIRD such entry fails this test instead of quietly widening the excuse.
    12.0176685803: "lora-c-run r3 (2026-08-26, pod otq63mmt7s2uf1, rung KILL) — a PAID step whose"
    " only ledger is the line ledger: no `results/spend_lora_c_r3.json` was ever written. Named"
    " here rather than repaired: writing that ledger now would be a record reconstructed from the"
    " line instead of read from the run.",
    5.6783611613: "2026-08-27 C1 retail-census step 0 — a guard reading taken when the"
    " `mp-lora-c` volume was deleted. No pod, no step, no step ledger, and never will be: the"
    " class :func:`silent_paid_runs` already documents as outside its one direction.",
}
"""Line-ledger entries that no step ledger witnesses, keyed on the balance both files carry.

This is what the check below was really protecting, and what it had assumed instead. It was written
when every line entry happened to have a step ledger behind it, so it asserted over the LINE's rows;
`results/spend_cycle2.json` is a live file and it grew two rows that never can
([[a_sealed_reports_checker_reads_a_live_file]]). The claim is narrowed to the step-ledger runs the
function actually reads, and the two exceptions are written down rather than tolerated by a filter.
"""


def test_the_silence_check_fires_on_the_LINE_ledger_too(tmp_path, monkeypatch):
    """The other half's negative control, and the half that has no history behind it yet.

    Dropping a row from the phase ledger proves the check reads THAT file. It says nothing about the
    branch added when the line took over — so the line's sessions are emptied here and every paid
    step whose ONLY witness was the line has to be named. A guard extended to a second source
    without a control over that source is a guard tested on the half it already had.

    Asserted over the STEP-LEDGER runs, not over the line's own rows: `silent_paid_runs` walks
    `results/spend_*.json` and reports the runs it finds there, so a line entry with no step ledger
    behind it is outside its reach by construction and is not evidence that the line branch is
    dead. Both directions — every such run must be named, and nothing else may be — plus the two
    known line entries with no step ledger, enumerated in
    :data:`LINE_SESSIONS_WITH_NO_STEP_LEDGER` and asserted to be exactly those two.
    """
    line = line_sessions()
    empty = tmp_path / "spend_empty_line.json"
    empty.write_text(json.dumps({"sessions": []}), encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "LINE_LEDGERS", (empty,))

    sessions = json.loads(repair.LEDGER.read_text(encoding="utf-8"))["sessions"]
    phase_balances = {session["balance"] for session in sessions}
    only_the_line = {one["balance"] for one in line} - phase_balances
    assert only_the_line, "there is at least one paid step under the line to lose"

    # The step-ledger runs whose only witness is the line — derived from the files, never listed.
    witnessed_only_by_the_line = {
        (f"results/{path.name}", run["at"], run["balance"])
        for path in sorted((REPO_ROOT / "results").glob("spend_*.json"))
        if path.name != repair.LEDGER.name
        for key in ("runs", "gpu_sessions")
        for run in json.loads(path.read_text(encoding="utf-8")).get(key) or []
        if "balance" in run and run["balance"] in only_the_line
    }
    assert witnessed_only_by_the_line, "the line branch witnesses no step-ledger run — vacuous"

    silent = silent_paid_runs(sessions)
    assert silent, "with the line's ledger emptied, its steps must be named"
    assert set(silent) == witnessed_only_by_the_line

    # And the other direction on the excuse: exactly the two known line entries have no step ledger.
    covered = {balance for _, _, balance in witnessed_only_by_the_line}
    assert only_the_line - covered == set(LINE_SESSIONS_WITH_NO_STEP_LEDGER)


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
