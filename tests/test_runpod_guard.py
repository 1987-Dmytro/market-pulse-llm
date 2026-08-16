"""The Phase 4 cap, driven with the RunPod readings faked.

No network and no `runpodctl`: the two readers are monkeypatched, which is also
the only way to prove the guard refuses rather than merely printing a number.
"""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "runpod_guard.py"
spec = importlib.util.spec_from_file_location("runpod_guard", SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


REAL_CYCLE2_LEDGER = SCRIPT.parents[1] / "results" / "spend_cycle2.json"


@pytest.fixture(autouse=True)
def never_the_real_cycle2_ledger(tmp_path, monkeypatch):
    """No test in this module may write `results/spend_cycle2.json`. Measured, not precautionary.

    The cycle-2 anchor is a ONE-SHOT: `read_cycle2` creates it on the first reading after a closed
    phase and it is never regenerated, so whatever balance writes it IS the line's starting number.
    Until 3.24 this file could not reach it by accident — 3.23 (2)'s $40.00 floor refused every
    balance these tests drive — and the floor was doing a second job nobody had registered it for.
    Repealing it made the very next `make check` anchor the production ledger at a fixture's $22.00
    (Dv424), through a test whose subject is the PHASE close and whose second reading happens to
    fall through to the line.

    So the redirect is autouse and on the MODULE, not on the test that was caught: a per-test patch
    holds only until the next test drives `main()` past a closed phase, which is exactly how this
    one arrived. `closed_phase` re-points it at a path its assertions name; this fixture is what
    makes the real one unreachable in between.
    """
    monkeypatch.setattr(guard, "CYCLE2_LEDGER", tmp_path / "not-the-real-cycle2-ledger.json")


def test_the_suite_cannot_reach_the_production_cycle2_anchor():
    """The negative control for the fixture above, asserting the REDIRECT and not the absence of a
    file: «the real ledger does not exist» would pass forever once the operator's deliberate run has
    created it, which is exactly when the protection stops being observable
    ([[guard_selftest_negative_control]]). That the redirect BITES — that `main()`'s write follows
    this attribute rather than a path of its own — is what
    `test_the_cycle2_anchor_is_taken_at_the_balance_the_guard_reads` shows, by finding the anchor in
    a temp dir after driving the whole guard.
    """
    assert guard.CYCLE2_LEDGER != REAL_CYCLE2_LEDGER
    assert not guard.CYCLE2_LEDGER.exists(), "and it starts unanchored, so a write here is visible"


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    """An anchored ledger in a temp dir; the real one is a committed artifact."""
    path = tmp_path / "spend_phase4.json"
    path.write_text(
        json.dumps(
            {
                "phase4_cap_usd": 33.0,
                "runpod_balance_at_phase4_start": 35.0,
                "anchored_at": "2026-08-01T09:00:00+00:00",
                "sessions": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "LEDGER", path)
    return path


def drive(monkeypatch, balance, billing=(0.0, "read"), kinds=None):
    """`balance` and the billing walk, faked.

    `billing_by_kind` is what gets patched and not a total-returning wrapper: every leg of the guard
    reads the walk through this one function, so a test that patched a sum would leave the STEP leg
    reaching for `runpodctl` (Dv411's fix is what put a second caller there). `kinds` is for the
    tests that care about the decomposition; the default puts the whole total under `pods`, which is
    what every test written before 3.23 (4) meant by its one number.
    """
    total, how = billing
    lines = dict(kinds) if kinds is not None else {"pods": total, "network-volume": 0.0}
    monkeypatch.setattr(guard, "balance", lambda: balance)
    monkeypatch.setattr(guard, "billing_by_kind", lambda anchored_at: (lines, how))


def test_the_pessimistic_reading_wins():
    """`Budget` on OpenRouter: a local sum can only ever be corrected upwards."""
    assert guard.spend(35.0, 34.0, 0.25) == 1.0
    assert guard.spend(35.0, 34.0, 2.50) == 2.50


def test_costs_are_summed_wherever_the_payload_hides_them():
    payload = [{"pods": [{"costPerHr": 0.5, "id": "x"}]}, {"totalAmount": 1.25, "nested": None}]
    assert guard.sum_costs(payload) == (1.75, True)


def test_a_payload_with_no_cost_field_is_reported_unreadable_not_zero():
    """The one outcome a cap must never have is inventing $0.00 of spend."""
    total, seen = guard.sum_costs([{"podId": "abc", "gpuTypeId": "NVIDIA RTX A6000"}])
    assert (total, seen) == (0.0, False)


def test_the_billing_walk_asks_for_serverless_too(monkeypatch):
    """The kind srv-2b's spend hid in. A worker that crash-loops bills at the flex rate
    while it does it, and the walk knew pods and volumes only: $0.86 of the session was
    invisible to the reading SPEC 3.4 (4) names, with the balance delta carrying the cap
    alone. The endpoint row is the one this asserts, so dropping the kind reddens here."""
    asked = []

    def one_reading(*args):
        asked.append(args[1])
        return [{"amount": 0.55, "endpointId": "zbptdon5jvfteu"}] if args[1] == "serverless" else []

    monkeypatch.setattr(guard, "runpodctl", one_reading)
    lines, how = guard.billing_by_kind("2026-08-08T17:00:00+00:00")
    assert (sum(lines.values()), how) == (0.55, "read")
    assert asked == ["pods", "network-volume", "serverless"]
    # 3.23 (4): the kinds arrive APART. A walk that returned the sum would make the volume's rent
    # and the run's own bill one number, which is the whole of Dv412 one layer down.
    assert lines == {"pods": 0.0, "network-volume": 0.0, "serverless": 0.55}


def test_the_always_on_kinds_are_left_out_of_what_the_run_itself_billed(monkeypatch):
    """SPEC 3.23 (4), on probe-b's own measured lines: the split is BY KIND and not by arithmetic.

    Reading the numbers `docs/reports/probe-b.md` §10 settled, the two answers straddle the cap they
    were judged against — $0.4396 refuses a $0.35 cap and $0.3132 does not, so this is the line
    between «overrun» and «inside», not a rounding note.

    The control is the constant emptied rather than the volume row deleted: dropping the row proves
    only that `sum` skips what is not there, while emptying :data:`guard.ALWAYS_ON_KINDS` shows the
    two readings COLLAPSE the moment nothing is declared always-on."""
    measured = {"pods": 0.028689, "network-volume": 0.126389, "serverless": 0.284473}
    assert guard.ALWAYS_ON_KINDS == ("network-volume",)
    assert round(guard.own_resources(measured), 6) == 0.313162
    assert round(sum(measured.values()), 6) == 0.439551
    assert guard.own_resources(measured) < 0.35 < sum(measured.values())

    monkeypatch.setattr(guard, "ALWAYS_ON_KINDS", ())
    assert guard.own_resources(measured) == sum(measured.values())


def test_a_start_under_the_cap_is_allowed(ledger, monkeypatch):
    drive(monkeypatch, balance=33.20, billing=(1.80, "read"))
    assert guard.main([]) == 0


def test_the_cap_refuses_the_next_start(ledger, monkeypatch):
    """The balance moves WITH the cap: 1.99 is $33.01 spent against the $33.00 of SPEC 3.18 (7)(b),
    the same one cent over that 4.99 was against $30.00 and 9.99 against $25.00. Left where it was
    this test would have gone on passing while measuring the opposite thing — $30.01 is under the
    raised cap and ALLOWED, which is what it measured for four minutes before this line moved."""
    drive(monkeypatch, balance=1.99, billing=(0.0, "no billing rows yet"))
    assert guard.main([]) == 1


def test_the_volume_keeps_billing_while_the_pod_is_stopped(ledger, monkeypatch):
    """A stopped pod is not a stopped bill: the network volume is charged by the
    month, and only the balance delta sees it."""
    drive(monkeypatch, balance=34.60, billing=(0.0, "no billing rows yet"))
    assert guard.main([]) == 0
    drive(monkeypatch, balance=34.60, billing=(0.0, "no billing rows yet"))
    guard.main(["--note", "4a zero-shot run"])
    session = json.loads(ledger.read_text(encoding="utf-8"))["sessions"][-1]
    assert session["spent_usd"] == 0.4
    assert session["remaining_usd"] == 32.6  # 33.00 − 0.40; the spend is what the volume bills


def test_a_top_up_refuses_instead_of_quietly_under_counting(ledger, monkeypatch):
    """A balance above the anchor means the delta stopped measuring this phase.
    Re-anchoring is the operator's call — the alternative is a cap that grows."""
    drive(monkeypatch, balance=60.0)
    assert guard.main([]) == 1


def test_the_first_run_anchors_and_says_so(tmp_path, monkeypatch, capsys):
    path = tmp_path / "spend_phase4.json"
    monkeypatch.setattr(guard, "LEDGER", path)
    drive(monkeypatch, balance=35.0)
    assert guard.main([]) == 0
    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["runpod_balance_at_phase4_start"] == 35.0
    # the ledger's field and the enforced constant are ONE number, and every raise moves both
    # together — 3.18 (3) to 30.00, 3.18 (7)(b) to 33.00. The literal is deliberate: this is the
    # test that goes red if the cap is quietly moved BACK, and `== guard.PHASE_CAP_USD` alone
    # cannot do that, because it would agree with the constant whatever the constant says.
    assert written["phase4_cap_usd"] == guard.PHASE_CAP_USD == 33.00
    assert "never regenerate" in capsys.readouterr().out


def test_a_session_note_is_only_logged_when_the_start_is_allowed(ledger, monkeypatch):
    """1.00 is $34.00 spent. Under the previous cap 4.00 was $31.00 — a dollar over $30.00 and now
    three dollars UNDER $33.00, which is the direction that matters: the old balance did not merely
    lose margin, it stopped refusing at all. 2.00 would sit exactly ON $33.00 and still refuse
    (`spent >= cap`), so the boundary is left to the test above and this one keeps its margin."""
    drive(monkeypatch, balance=1.0)
    assert guard.main(["--note", "would have been a fourth arm"]) == 1
    assert json.loads(ledger.read_text(encoding="utf-8"))["sessions"] == []


# --- a step's own cap, inside the phase's (4.5h2) ------------------------------


def test_a_step_anchors_once_and_never_re_anchors(tmp_path):
    """Regenerating a step anchor restarts its counter at today's balance — the same
    footgun the phase ledger carries, on a smaller cap."""
    path = tmp_path / "spend_45h2.json"
    first = guard.read_step(path, "45h2", 9.0, 27.53)
    guard.write_ledger_at(path, first)
    again = guard.read_step(path, "45h2", 9.0, 3.00)
    assert again["runpod_balance_at_45h2_start"] == 27.53


def test_a_step_anchor_lands_beside_what_the_ledger_already_holds(tmp_path):
    """One file per step, so "what did 4.5h2 cost" is one document: the OpenRouter
    anchor written by the migration pass must survive the GPU one."""
    path = tmp_path / "spend_45h2.json"
    path.write_text(json.dumps({"openrouter_total_usage_at_45h2_start": 3.23}), encoding="utf-8")
    ledger = guard.read_step(path, "45h2", 9.0, 27.53)
    assert ledger["openrouter_total_usage_at_45h2_start"] == 3.23
    assert ledger["runpod_balance_at_45h2_start"] == 27.53


def test_a_cap_without_an_anchor_is_refused():
    with pytest.raises(SystemExit):
        guard.main(["--step-cap", "9.00"])


# --- Dv151: one step, one anchor, however its name is typed -------------------


def test_a_hyphen_and_an_underscore_are_the_same_step(tmp_path):
    """Measured on 2026-08-11. `--step sku-b` wrote `results/spend_sku-b.json` beside the driver's
    own `results/spend_sku_b.json`, holding the balance AFTER the step had spent $0.0943 and a
    `step_spent_usd` of 0.0 — every number false and none of them looking it.

    Two halves of the fix, and each one alone leaves the hole open: the file is normalised, and the
    key is looked for under BOTH spellings inside it, because the driver writes
    `runpod_balance_at_sku-b_start` into the underscored file.
    """
    assert guard.step_ledger_path("sku-b") == guard.step_ledger_path("sku_b")
    assert guard.step_ledger_path("sku-b").name == "spend_sku_b.json"

    path = tmp_path / "spend_sku_b.json"
    path.write_text(
        json.dumps({"runpod_balance_at_sku-b_start": 12.4184987367, "runs": []}), encoding="utf-8"
    )
    ledger = guard.read_step(path, "sku-b", 0.35, 12.2220)
    assert guard.anchor_key_in(ledger, "sku-b") == "runpod_balance_at_sku-b_start"
    assert ledger["runpod_balance_at_sku-b_start"] == 12.4184987367
    assert "runpod_balance_at_sku_b_start" not in ledger, "a second anchor for one step"
    # and the other way round: the underscored spelling finds the same one
    assert guard.read_step(path, "sku_b", 0.35, 1.0)["runpod_balance_at_sku-b_start"] == (
        12.4184987367
    )


def test_one_step_writes_exactly_one_ledger_file(ledger, tmp_path, monkeypatch):
    """Dv392, and why the assertion above was not enough to catch it.

    `step_ledger_path` normalised the READ and `--note` rebuilt the WRITE from the raw step name, so
    probe-a's anchor was read from `results/spend_probe_a.json` while its session note landed in
    `results/spend_probe-a.json`. Both carried the same anchor, so no number was wrong — and two
    anchor files for one step is the counter this module's docstring says must never restart.

    A test that only compares two calls of the path function cannot see that: the second spelling was
    never built by the function ([[a_guard_on_one_path_is_not_a_guard]]). This one drives `main` with
    the write flag, without `--step-ledger`, and looks at the DIRECTORY.
    """
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)
    drive(monkeypatch, balance=23.00)

    assert guard.main(["--step", "probe-b", "--step-cap", "0.35", "--note", "the anchor"]) == 0
    assert guard.main(["--step", "probe-b", "--step-cap", "0.35", "--note", "a session"]) == 0

    written = sorted(path.name for path in (tmp_path / "results").glob("spend_probe*.json"))
    assert written == ["spend_probe_b.json"], written
    body = json.loads((tmp_path / "results" / "spend_probe_b.json").read_text(encoding="utf-8"))
    assert body["runpod_balance_at_probe-b_start"] == 23.00
    assert [one["note"] for one in body["gpu_sessions"]] == ["the anchor", "a session"]


def test_the_existing_anchor_is_what_the_cap_is_enforced_against(tmp_path, monkeypatch, capsys):
    """The consequence, driven through `main`: the step's spend is measured against the anchor that
    already exists, not against today's balance, and nothing is rewritten."""
    ledger_path = tmp_path / "spend_phase4.json"
    ledger_path.write_text(
        json.dumps(
            {
                "phase4_cap_usd": 33.0,
                "runpod_balance_at_phase4_start": 35.0,
                "anchored_at": "2026-08-01T09:00:00+00:00",
                "sessions": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "LEDGER", ledger_path)
    step_path = tmp_path / "spend_sku_b.json"
    before = json.dumps({"runpod_balance_at_sku-b_start": 12.4184987367, "runs": []})
    step_path.write_text(before, encoding="utf-8")

    drive(monkeypatch, balance=12.2220, billing=(0.0, "no billing rows yet"))
    assert (
        guard.main(["--step", "sku-b", "--step-cap", "0.35", "--step-ledger", str(step_path)]) == 0
    )
    printed = capsys.readouterr().out
    assert "SKU-B SPENT      $0.1965" in printed
    assert "anchored" not in printed, "an existing anchor is never re-anchored"
    assert step_path.read_text(encoding="utf-8") == before

    # the control: a step that genuinely has no anchor still gets one
    fresh = tmp_path / "spend_new_step.json"
    drive(monkeypatch, balance=12.2220, billing=(0.0, "no billing rows yet"))
    assert (
        guard.main(["--step", "new-step", "--step-cap", "1.00", "--step-ledger", str(fresh)]) == 0
    )
    assert json.loads(fresh.read_text(encoding="utf-8"))["runpod_balance_at_new-step_start"] == (
        12.2220
    )
    assert "anchored" in capsys.readouterr().out


# --- Dv411: a step is read twice, like the phase, or its figure has no upper bound --------------


def step_with(tmp_path, **fields) -> Path:
    path = tmp_path / "spend_probe_b.json"
    path.write_text(
        json.dumps({"runpod_balance_at_probe-b_start": 22.9784784161, **fields}), encoding="utf-8"
    )
    return path


PROBE_B_LINES = {"pods": 0.028689, "network-volume": 0.126389, "serverless": 0.284473}
"""probe-b's window as `runpodctl billing` settled it, read back on 2026-08-16 and identical to the
three lines `docs/reports/probe-b.md` §10 published. The balance delta over the same window is
$0.4493, so this fixture is the one case where all three readings of one step are on the table."""


def read_step_line(printed: str, prefix: str) -> str:
    return next(line for line in printed.splitlines() if line.strip().startswith(prefix))


def test_a_step_takes_two_readings_and_the_pessimistic_one_binds(
    ledger, tmp_path, monkeypatch, capsys
):
    """Dv411: `spend()` takes `max(delta, billing)` for the phase and `--step` took the delta alone.

    Driven on probe-b's real numbers. The delta ($0.4493) is the larger of the two here, so the
    verdict is the delta — and the point is that it is a MAXIMUM and not the only reading: the
    billing total is printed beside it and the step's own resources under that."""
    path = step_with(tmp_path, anchored_at="2026-08-15T20:31:00+00:00")
    drive(monkeypatch, balance=22.5292058832, billing=(0.0, "read"), kinds=PROBE_B_LINES)

    assert guard.main(["--step", "probe-b", "--step-cap", "0.50", "--step-ledger", str(path)]) == 0
    printed = capsys.readouterr().out
    assert "PROBE-B SPENT      $0.4493 of $0.50" in printed
    assert "balance delta   $0.4493" in printed
    assert "billing since   $0.4396 (read)" in printed
    assert "step resources  $0.3132" in printed


def test_the_volumes_rent_is_named_beside_the_step_and_never_inside_it(
    ledger, tmp_path, monkeypatch, capsys
):
    """SPEC 3.23 (4). The volume gets its own line and is marked always-on; the step's own figure
    is the same lines with that kind left out. Both numbers are on the page, which is what makes
    «$0.29 of probe + $0.15 of volume» readable instead of a $0.44 mystery."""
    path = step_with(tmp_path, anchored_at="2026-08-15T20:31:00+00:00")
    drive(monkeypatch, balance=22.5292058832, billing=(0.0, "read"), kinds=PROBE_B_LINES)
    guard.main(["--step", "probe-b", "--step-cap", "0.50", "--step-ledger", str(path)])
    printed = capsys.readouterr().out

    volume = read_step_line(printed, "network-volume")
    assert "$0.1264" in volume and "always on" in volume
    assert "$0.0287" in read_step_line(printed, "pods")
    assert "$0.2845" in read_step_line(printed, "serverless")
    # and the step's own figure is the two that are not always-on
    assert round(0.028689 + 0.284473, 4) == 0.3132
    assert "step resources  $0.3132" in printed


def test_an_unposted_bill_is_UNAVAILABLE_and_the_delta_is_called_a_lower_bound(
    ledger, tmp_path, monkeypatch, capsys
):
    """Dv411's exact reading: «no billing rows yet» is not $0.00 of corroboration, it is the absence
    of one. A step at 92% of its cap with the second reading missing is UNKNOWN, not INSIDE."""
    path = step_with(tmp_path, anchored_at="2026-08-15T20:31:00+00:00")
    drive(monkeypatch, balance=22.6555, billing=(0.0, "no billing rows yet"))
    guard.main(["--step", "probe-b", "--step-cap", "0.50", "--step-ledger", str(path)])
    printed = capsys.readouterr().out

    assert "PROBE-B SPENT      $0.3230" in printed
    assert "UNAVAILABLE (no billing rows yet)" in printed and "LOWER BOUND" in printed
    assert "step resources" not in printed, "there is no decomposition to print"


def test_a_ledger_with_no_anchor_time_says_so_and_not_that_billing_returned_nothing(
    ledger, tmp_path, monkeypatch, capsys
):
    """The third state, which must not collapse into the second.

    A step ledger written before the guard recorded its anchor TIME cannot have the walk asked for
    it at all — there is no window. Printing «no billing rows yet» there would claim a reading that
    was never taken, which is the same shape of lie the two-reading rule exists to stop."""
    path = step_with(tmp_path)  # no `anchored_at`, exactly as results/spend_probe_b.json stood
    drive(monkeypatch, balance=22.5292058832, billing=(0.0, "read"), kinds=PROBE_B_LINES)
    guard.main(["--step", "probe-b", "--step-cap", "0.50", "--step-ledger", str(path)])
    printed = capsys.readouterr().out

    # scoped to the STEP's own block: the phase leg above it has an anchor time and does walk
    step_block = printed.split("PROBE-B", 1)[1]
    assert "records no anchor time" in step_block and "LOWER BOUND" in step_block
    assert "no billing rows yet" not in step_block, "a window never asked is not an empty one"
    assert "$0.4396" not in step_block, "the walk must not be run over some other ledger's window"
    assert "step resources" not in step_block, "and there is no decomposition to print"


def test_a_new_step_anchor_records_the_moment_its_balance_was_read(tmp_path, monkeypatch):
    """The write half of the fix: from here on a step HAS a window, so state three empties out."""
    monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)
    written = guard.read_step(tmp_path / "spend_new.json", "new", 1.0, 30.0)
    assert written["anchored_at"].endswith("+00:00")
    assert "the pessimistic maximum" in written["gpu_note"]

    # and it is never given a later time it did not happen at: a ledger the DRIVER anchored first
    # already carries the moment, and `read_step` adds its balance key beside it
    path = tmp_path / "spend_driven.json"
    path.write_text(json.dumps({"anchored_at": "2026-08-15T20:31:00+00:00"}), encoding="utf-8")
    assert guard.read_step(path, "driven", 1.0, 30.0)["anchored_at"] == "2026-08-15T20:31:00+00:00"


# --- Dv412: a step can be CLOSED, and a closed one stops growing at the volume's rate -----------


def test_a_closed_step_is_priced_by_its_settled_figure_and_never_by_a_growing_delta(
    ledger, tmp_path, monkeypatch, capsys
):
    """The whole of Dv412, driven twice with the balance moved between the runs.

    `--close` settles the step from the billing walk over its window; the second invocation reads
    the settled figure back out of the entry and does NOT ask the walk again. That is what makes the
    figure stop moving: the balance has drifted $0.05 lower between the two calls — the volume doing
    what it always does — and the printed number is identical."""
    path = step_with(tmp_path, anchored_at="2026-08-15T20:31:00+00:00")
    drive(monkeypatch, balance=22.5292058832, billing=(0.0, "read"), kinds=PROBE_B_LINES)

    assert (
        guard.main(
            [
                "--step",
                "probe-b",
                "--step-cap",
                "0.35",
                "--step-ledger",
                str(path),
                "--close",
                "--note",
                "probe-b closed",
            ]
        )
        == 0
    ), "the settled figure is inside the cap that the delta breached"
    first = capsys.readouterr().out
    assert "PROBE-B CLOSED     $0.3132 of $0.35" in first
    entry = json.loads(path.read_text(encoding="utf-8"))["gpu_sessions"][-1]
    assert entry["closed"] is True and entry["settled_usd"] == 0.313162
    assert entry["billing_by_kind"]["network-volume"] == 0.126389
    assert entry["balance_delta_usd"] == 0.449273, "the delta is recorded, it just does not bind"

    # thirteen more hours of volume: the delta grows, the closed step does not
    drive(monkeypatch, balance=22.4792058832, billing=(0.0, "read"), kinds=PROBE_B_LINES)
    assert guard.main(["--step", "probe-b", "--step-cap", "0.35", "--step-ledger", str(path)]) == 0
    again = capsys.readouterr().out
    assert "PROBE-B CLOSED     $0.3132 of $0.35" in again
    assert "SPENT" not in again.split("PHASE 4")[-1].split("PROBE-B")[-1]
    assert json.loads(path.read_text(encoding="utf-8"))["gpu_sessions"][-1] == entry, "append-only"


def test_a_closed_step_that_really_overran_still_refuses(ledger, tmp_path, monkeypatch):
    """The other direction, and the reason closing is not an amnesty: the verdict moves to the
    SETTLED figure, it does not disappear. Same lines, a cap of $0.30 instead of $0.35."""
    path = step_with(tmp_path, anchored_at="2026-08-15T20:31:00+00:00")
    drive(monkeypatch, balance=22.5292058832, billing=(0.0, "read"), kinds=PROBE_B_LINES)
    assert (
        guard.main(
            [
                "--step",
                "probe-b",
                "--step-cap",
                "0.30",
                "--step-ledger",
                str(path),
                "--close",
                "--note",
                "closed over its cap",
            ]
        )
        == 1
    )
    assert json.loads(path.read_text(encoding="utf-8"))["gpu_sessions"][-1]["closed"] is True


def test_closing_refuses_when_the_walk_cannot_settle_anything(ledger, tmp_path, monkeypatch):
    """A closing entry is never re-derived, so it is never written over a reading that did not
    answer. «no billing rows yet» would settle the step at $0.00 for good."""
    path = step_with(tmp_path, anchored_at="2026-08-15T20:31:00+00:00")
    before = path.read_text(encoding="utf-8")
    drive(monkeypatch, balance=22.6555, billing=(0.0, "no billing rows yet"))
    assert (
        guard.main(
            [
                "--step",
                "probe-b",
                "--step-cap",
                "0.50",
                "--step-ledger",
                str(path),
                "--close",
                "--note",
                "would have settled at zero",
            ]
        )
        == 1
    )
    assert path.read_text(encoding="utf-8") == before, "a refused closure wrote nothing"


def test_a_step_with_no_window_cannot_be_closed_without_since(ledger, tmp_path, monkeypatch):
    """`results/spend_probe_b.json` as it actually stood: an anchor, no anchor time. The window has
    to be supplied and SOURCED, and the entry records which one it was closed over."""
    path = step_with(tmp_path)
    drive(monkeypatch, balance=22.5292058832, billing=(0.0, "read"), kinds=PROBE_B_LINES)
    argv = ["--step", "probe-b", "--step-cap", "0.35", "--step-ledger", str(path)]
    assert guard.main([*argv, "--close", "--note", "no window"]) == 1
    assert "gpu_sessions" not in json.loads(path.read_text(encoding="utf-8"))

    assert (
        guard.main(
            [*argv, "--close", "--note", "with a window", "--since", "2026-08-15T20:31:00+00:00"]
        )
        == 0
    )
    entry = json.loads(path.read_text(encoding="utf-8"))["gpu_sessions"][-1]
    assert entry["window_start"] == "2026-08-15T20:31:00+00:00"
    assert entry["settled_usd"] == 0.313162


# --- SPEC 3.23: Phase 4 closes, and the $20 line is what replaces it ----------------------------


def closed_phase(tmp_path, monkeypatch, spent=32.4611):
    path = tmp_path / "spend_phase4.json"
    path.write_text(
        json.dumps(
            {
                "phase4_cap_usd": 33.0,
                "runpod_balance_at_phase4_start": 35.0,
                "anchored_at": "2026-08-01T09:00:00+00:00",
                "sessions": [
                    {"at": "2026-08-15T20:51:14+00:00", "balance": 22.68, "spent_usd": 32.01},
                    {
                        "at": "2026-08-16T12:00:00+00:00",
                        "closed": True,
                        "spent_usd": spent,
                        "remaining_usd": round(33.0 - spent, 4),
                        "billing_by_kind": {
                            "pods": 17.692135,
                            "network-volume": 3.218056,
                            "serverless": 11.550881,
                        },
                        "note": "PHASE 4 IS CLOSED",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "LEDGER", path)
    monkeypatch.setattr(guard, "CYCLE2_LEDGER", tmp_path / "spend_cycle2.json")
    return path


def test_the_guard_says_the_phase_is_closed_and_reads_the_final_entry_not_a_live_delta(
    tmp_path, monkeypatch, capsys
):
    """«The guard learns to SAY the phase is closed when it is.» It reads the closing entry's own
    numbers: no `PHASE 4 SPENT` line, no live delta, and the decomposition the entry carries.

    The live-walk control is SCOPED to the phase's half of the print since 3.24. Under 3.23 (2) the
    balance driven here was below the anchor floor, so the guard stopped before any walk and «$99
    appears nowhere» was true for two reasons at once — the phase not asking, and the line not
    existing. The floor is repealed, the line anchors on this very reading and its walk is asked and
    printed; what must still be true is that the CLOSED phase's own figures are the settled ones.
    """
    closed_phase(tmp_path, monkeypatch)
    drive(monkeypatch, balance=22.00, billing=(99.0, "read"))
    assert guard.main([]) == 1
    printed = capsys.readouterr().out
    # split at the first line `enforce` prints: the phase is CLOSED, so the only ledger that reaches
    # `enforce` — and therefore the only walk that is asked — is the cycle-2 line below it
    phase_half, sep, line_half = printed.partition("anchor            $")
    assert sep, "the line's own reading is what follows the closed phase"

    assert "PHASE 4 CLOSED    $32.4611 of $33.00" in phase_half
    assert "PHASE 4 SPENT" not in printed, "a closed ledger prints its settlement, not a delta"
    assert "network-volume  $3.2181" in phase_half
    assert "$99.0" not in phase_half, "the live walk is not asked for a closed phase"
    assert "$99.0" in line_half, "and it IS asked for the line that replaced it"


def test_a_closed_phase_anchors_the_line_and_never_refuses_a_cap_breach(
    tmp_path, monkeypatch, capsys
):
    """SPEC 3.23 (3) as 3.24 (1) leaves it. The volume alone will carry the phase past $33.00 within
    days, so a closed phase that refused «the cap is reached» would reproduce Dv412 one layer up: a
    refusal about a charge that belongs to nothing anybody started. What the repeal removes is the
    OTHER refusal — the inter-ledger gap is closed by this reading rather than reported by it."""
    closed_phase(tmp_path, monkeypatch)
    drive(monkeypatch, balance=22.5292058832, billing=(0.0, "no billing rows yet"))
    assert guard.main([]) == 0
    out, err = capsys.readouterr()

    assert "PHASE 4 CLOSED    $32.4611 of $33.00" in out
    assert "CYCLE 2 SPENT     $0.0000 of $20.00" in out
    assert "NOT ANCHORED" not in out and "INTER-LEDGER GAP" not in err
    assert "cap is reached" not in err
    assert (tmp_path / "spend_cycle2.json").exists(), "the line is anchored by this very reading"


def test_the_cycle2_anchor_is_taken_at_the_balance_the_guard_reads(tmp_path, monkeypatch, capsys):
    """SPEC amendment 3.24 (1): the $40.00 floor of 3.23 (2) is REPEALED.

    The balance driven here is $22.5292058832 — the real reading of 2026-08-16, and the one the old
    threshold refused. It anchors, VERBATIM and with the timestamp it was read at. The negative
    control is the second half: the repealed constant is gone from the module, so a threshold that
    survived the repeal by being renamed or defaulted could not pass this line
    ([[a_lifted_ceiling_is_not_lifted_code]]).
    """
    closed_phase(tmp_path, monkeypatch)
    drive(monkeypatch, balance=22.5292058832, billing=(0.0, "no billing rows yet"))
    assert guard.main([]) == 0
    written = json.loads((tmp_path / "spend_cycle2.json").read_text(encoding="utf-8"))
    assert written["runpod_balance_at_cycle2_start"] == 22.5292058832
    assert written["anchored_at"].endswith("+00:00")
    # the ledger's own cap field and the enforced constant are ONE number. The literals are
    # deliberate: `== guard.CYCLE2_CAP_USD` alone would agree with the constant whatever it said,
    # so this is the test that reddens if either line is quietly moved.
    assert written["cycle2_cap_usd"] == guard.CYCLE2_CAP_USD == 20.00
    assert not hasattr(guard, "CYCLE2_ANCHOR_MIN_USD"), "the floor retires with the clause"
    assert "3.24 (1)" in written["note"] and "repealed" in written["note"]
    assert "never regenerate" in capsys.readouterr().out


def test_an_anchored_line_is_never_re_anchored_by_a_later_reading(tmp_path, monkeypatch, capsys):
    """The one-shot the repeal does NOT touch. Without the threshold the first reading fixes the
    line's starting number, so the second reading must find the file and leave it alone — the
    footgun `results/spend_phase4.json` names, one ledger over."""
    closed_phase(tmp_path, monkeypatch)
    drive(monkeypatch, balance=22.5292058832, billing=(0.0, "no billing rows yet"))
    assert guard.main([]) == 0
    first = (tmp_path / "spend_cycle2.json").read_text(encoding="utf-8")
    capsys.readouterr()

    drive(monkeypatch, balance=21.00, billing=(0.0, "no billing rows yet"))
    assert guard.main([]) == 0
    assert (tmp_path / "spend_cycle2.json").read_text(encoding="utf-8") == first
    assert "CYCLE 2 SPENT     $1.5292 of $20.00" in capsys.readouterr().out


def test_the_cycle2_line_is_enforced_exactly_as_the_phase_cap_was(tmp_path, monkeypatch, capsys):
    """Once anchored the line is the live ledger: both readings, the pessimistic maximum, the same
    two refusals. $19.99 spent is allowed and $20.00 is not — `spent >= cap`, as the phase has it."""
    closed_phase(tmp_path, monkeypatch)
    (tmp_path / "spend_cycle2.json").write_text(
        json.dumps(
            {
                "cycle2_cap_usd": 20.0,
                "runpod_balance_at_cycle2_start": 40.0,
                "anchored_at": "2026-08-17T09:00:00+00:00",
                "sessions": [],
            }
        ),
        encoding="utf-8",
    )
    drive(monkeypatch, balance=20.01, billing=(0.0, "no billing rows yet"))
    assert guard.main([]) == 0
    assert "CYCLE 2 SPENT     $19.9900 of $20.00" in capsys.readouterr().out

    drive(monkeypatch, balance=20.00, billing=(0.0, "no billing rows yet"))
    assert guard.main([]) == 1
    assert "$20.00 CYCLE 2 cap is reached" in capsys.readouterr().err

    # and the pessimistic maximum, on the corroborating side this time
    drive(monkeypatch, balance=39.00, billing=(19.99, "read"))
    assert guard.main([]) == 0
    drive(monkeypatch, balance=39.00, billing=(20.00, "read"))
    assert guard.main([]) == 1


def test_a_note_after_the_close_lands_in_the_line_and_not_in_the_closed_phase(
    tmp_path, monkeypatch
):
    """One live ledger at a time. A session logged after the phase closed belongs to the line that
    replaced it, and the closed ledger never gains another row."""
    phase = closed_phase(tmp_path, monkeypatch)
    before = phase.read_text(encoding="utf-8")
    (tmp_path / "spend_cycle2.json").write_text(
        json.dumps(
            {
                "cycle2_cap_usd": 20.0,
                "runpod_balance_at_cycle2_start": 40.0,
                "anchored_at": "2026-08-17T09:00:00+00:00",
                "sessions": [],
            }
        ),
        encoding="utf-8",
    )
    drive(monkeypatch, balance=39.50, kinds={"pods": 0.4, "network-volume": 0.1})
    assert guard.main(["--note", "the first paid step of cycle 2"]) == 0

    assert phase.read_text(encoding="utf-8") == before, "a closed ledger is append-only and closed"
    row = json.loads((tmp_path / "spend_cycle2.json").read_text(encoding="utf-8"))["sessions"][-1]
    assert (row["spent_usd"], row["balance_delta_usd"], row["billing_since_usd"]) == (0.5, 0.5, 0.5)
    assert row["billing_read"] == "read", (
        "Dv33: both readings travel with the row, not just the max"
    )


def test_the_phase_is_closed_by_the_guard_and_the_entry_carries_both_readings(
    ledger, monkeypatch, capsys
):
    """D1's instrument. Every number in the closing entry comes from the walk and the balance the
    guard just read — none of them is typed — and the decomposition rides along."""
    drive(
        monkeypatch,
        balance=22.5292058832,
        billing=(0.0, "read"),
        kinds={"pods": 17.692135, "network-volume": 3.218056, "serverless": 11.550881},
    )
    assert guard.main(["--close", "--note", "PHASE 4 IS CLOSED"]) == 0
    entry = json.loads(ledger.read_text(encoding="utf-8"))["sessions"][-1]

    assert entry["closed"] is True and entry["note"] == "PHASE 4 IS CLOSED"
    assert entry["spent_usd"] == 32.4611 and entry["balance_delta_usd"] == 12.470794
    assert entry["billing_since_usd"] == 32.461072
    assert entry["billing_by_kind"]["serverless"] == 11.550881
    assert entry["remaining_usd"] == round(33.00 - 32.4611, 4)
    assert "CLOSED spend_phase4.json at $32.4611" in capsys.readouterr().out

    # and the next reading says so instead of taking the delta again
    drive(monkeypatch, balance=22.0, billing=(0.0, "read"))
    guard.main([])
    assert "PHASE 4 CLOSED    $32.4611" in capsys.readouterr().out


def test_the_closing_flags_refuse_to_be_used_half(ledger, monkeypatch):
    """A closing entry with no note is a state change nobody signed, and `--since` outside a
    closure is a window for a walk that is not happening."""
    drive(monkeypatch, balance=30.0)
    with pytest.raises(SystemExit):
        guard.main(["--close"])
    with pytest.raises(SystemExit):
        guard.main(["--since", "2026-08-15T20:31:00+00:00", "--note", "x"])


def test_a_refused_start_leaves_no_step_anchor_behind(ledger, tmp_path, monkeypatch):
    """The write gate: a counter is created only for a step that is allowed to begin. Before the
    refusals were collected instead of returned on, the phase leg returned first and this could not
    happen; now that every leg runs, the anchor has to be gated on the verdict rather than on the
    order of the code."""
    fresh = tmp_path / "spend_never_ran.json"
    drive(monkeypatch, balance=1.99, billing=(0.0, "no billing rows yet"))
    assert (
        guard.main(["--step", "never-ran", "--step-cap", "1.00", "--step-ledger", str(fresh)]) == 1
    )
    assert not fresh.exists(), "a step that was refused a start has no anchor"


# --- the two ledgers this contract actually closed, read from disk ------------------------------


def test_phase_4_is_closed_on_disk_and_its_closing_entry_adds_up():
    """The committed artifact, not a fixture. A closed ledger never moves again, so the literals
    here are the shipped numbers rather than a snapshot with a shelf life.

    Everything is re-derived from the entry's own fields: `spent_usd` must be the pessimistic
    maximum of the two readings it carries, and `billing_since_usd` must be the sum of the kinds it
    decomposes into. A hand-typed figure fails one of those two lines."""
    ledger = json.loads(
        (Path(__file__).resolve().parents[1] / "results" / "spend_phase4.json").read_text("utf-8")
    )
    entry = guard.closing_entry(ledger["sessions"])

    assert entry is not None and entry["note"].startswith("PHASE 4 IS CLOSED")
    assert entry is ledger["sessions"][-1], "the closing entry is the last thing appended"
    assert (
        entry["spent_usd"]
        == 32.4708
        == round(max(entry["balance_delta_usd"], entry["billing_since_usd"]), 4)
    )
    assert entry["remaining_usd"] == round(guard.PHASE_CAP_USD - entry["spent_usd"], 4) == 0.5292
    assert round(sum(entry["billing_by_kind"].values()), 6) == entry["billing_since_usd"]
    assert set(entry["billing_by_kind"]) == set(guard.BILLING_KINDS)
    # the delta is $20.00 short of the billing walk, which is the operator's 2026-08-15 top-up
    # landing after this ledger's anchor. Both readings are kept BECAUSE they disagree.
    assert entry["balance_delta_usd"] == 12.480516
    assert 19.9 < entry["billing_since_usd"] - entry["balance_delta_usd"] < 20.1
    # untouched by the closure, and named so a regeneration would be seen
    assert ledger["runpod_balance_at_phase4_start"] == 35.0
    assert ledger["anchored_at"] == "2026-08-01T08:34:09+00:00"
    assert len(ledger["sessions"]) == 41


def test_probe_b_is_closed_on_disk_at_its_own_resources_and_inside_its_cap():
    """Dv412's retirement, on the artifact. The step settles at what ITS resources billed; the
    volume's rent is in the decomposition beside it and in neither the figure nor the verdict."""
    path = Path(__file__).resolve().parents[1] / "results" / "spend_probe_b.json"
    step = json.loads(path.read_text("utf-8"))
    entry = guard.closing_entry(step["gpu_sessions"])

    assert entry is not None and entry["window_start"] == "2026-08-15T20:31:00+00:00"
    assert (
        entry["settled_usd"] == 0.313162 == round(guard.own_resources(entry["billing_by_kind"]), 6)
    )
    assert entry["settled_usd"] < step["probe-b_gpu_cap_usd"] == 0.35
    # the two readings the guard refused on before this contract, both recorded and neither binding
    assert entry["billing_since_usd"] > 0.35 and entry["balance_delta_usd"] > 0.35
    assert entry["billing_by_kind"]["network-volume"] == round(
        entry["billing_since_usd"] - entry["settled_usd"], 6
    )
    # append-only: the anchor and the run's own session are exactly as probe-b left them
    assert step["runpod_balance_at_probe-b_start"] == 22.9784784161
    assert step["gpu_sessions"][0]["step_spent_usd"] == 0.2907
    assert len(step["gpu_sessions"]) == 2


def test_a_closing_entry_re_derives_from_the_lines_it_publishes():
    """The rounding seam, at the producer rather than only on the shipped artifacts.

    Built on the exact numbers that exposed it: `runpodctl` returned probe-b's pods and serverless
    at full precision, whose raw sum rounds to $0.313161, while the two lines the record PUBLISHES
    round to $0.028689 and $0.284473 and add to $0.313162. A reader adding up the decomposition got
    a different number from the headline beside it — one micro-dollar, and a record that cannot be
    checked against itself."""
    raw = {"pods": 0.0286886, "network-volume": 0.1361111, "serverless": 0.2844725}
    entry = guard.closing_record(
        anchored_at="2026-08-15T20:31:00+00:00",
        balance_now=22.5,
        anchor=22.9784784161,
        lines=raw,
        how="read",
        note="x",
    )
    assert round(sum(raw.values()), 6) == 0.449272 != entry["billing_since_usd"] == 0.449273
    assert entry["billing_since_usd"] == round(sum(entry["billing_by_kind"].values()), 6)
    assert round(guard.own_resources(entry["billing_by_kind"]), 6) == 0.313162

    # and the other direction: a walk that did not answer settles nothing
    assert (
        guard.closing_record(
            anchored_at="x",
            balance_now=1.0,
            anchor=2.0,
            lines={},
            how="no billing rows yet",
            note="x",
        )
        is None
    )


def test_the_balance_is_printed_once_whichever_ledger_is_live(tmp_path, monkeypatch, capsys):
    """One reading, one line. The closed branch prints the balance itself when there is no line to
    enforce, and stays quiet when there is — `enforce` says it in that case, and a guard that
    printed two `balance now` rows would invite a reader to look for two readings."""
    closed_phase(tmp_path, monkeypatch)
    drive(monkeypatch, balance=22.5)
    guard.main([])
    assert capsys.readouterr().out.count("balance now") == 1

    (tmp_path / "spend_cycle2.json").write_text(
        json.dumps(
            {
                "cycle2_cap_usd": 20.0,
                "runpod_balance_at_cycle2_start": 40.0,
                "anchored_at": "2026-08-17T09:00:00+00:00",
                "sessions": [],
            }
        ),
        encoding="utf-8",
    )
    drive(monkeypatch, balance=39.5)
    guard.main([])
    assert capsys.readouterr().out.count("balance now") == 1
