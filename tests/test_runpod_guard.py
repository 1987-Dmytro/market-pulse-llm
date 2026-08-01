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
                "phase4_cap_usd": 25.0,
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


def test_a_start_under_the_cap_is_allowed(ledger, monkeypatch):
    drive(monkeypatch, balance=33.20, billing=(1.80, "read"))
    assert guard.main([]) == 0


def test_the_cap_refuses_the_next_start(ledger, monkeypatch):
    drive(monkeypatch, balance=9.99, billing=(0.0, "no billing rows yet"))
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
    assert session["remaining_usd"] == 24.6


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
    assert written["phase4_cap_usd"] == guard.PHASE_CAP_USD == 25.00
    assert "never regenerate" in capsys.readouterr().out


def test_a_session_note_is_only_logged_when_the_start_is_allowed(ledger, monkeypatch):
    drive(monkeypatch, balance=5.0)
    assert guard.main(["--note", "would have been a fourth arm"]) == 1
    assert json.loads(ledger.read_text(encoding="utf-8"))["sessions"] == []
