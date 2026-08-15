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


def drive(monkeypatch, balance, billing=(0.0, "read")):
    monkeypatch.setattr(guard, "balance", lambda: balance)
    monkeypatch.setattr(guard, "billing_since", lambda anchored_at: billing)


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
    assert guard.billing_since("2026-08-08T17:00:00+00:00") == (0.55, "read")
    assert asked == ["pods", "network-volume", "serverless"]


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
