"""A phase pre-registered at $0.00 still needs the tripwire that proves it (4.5g5, Budget)."""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import zero_spend_45g5 as guard  # noqa: E402

KEY = "openrouter_total_usage_at_45g5_start"
LEDGER = REPO_ROOT / "results" / "spend_45g5.json"


def test_a_missing_anchor_is_set_to_the_reading_taken_now():
    assert guard.anchored(None, 3.2)[KEY] == 3.2
    assert guard.anchored({}, 1.0)[KEY] == 1.0


def test_an_existing_anchor_is_never_moved():
    """Re-anchoring walks the baseline past exactly the spend it exists to catch."""
    ledger = {KEY: 3.2, "runs": []}

    assert guard.anchored(ledger, 9.99) is ledger
    assert guard.anchored(ledger, 9.99)[KEY] == 3.2


def test_the_delta_is_spend_since_the_anchor():
    assert guard.delta({KEY: 3.2}, 3.2) == 0.0
    assert round(guard.delta({KEY: 3.2}, 3.25), 4) == 0.05


def test_representation_noise_is_not_a_request():
    assert abs(guard.delta({KEY: 3.2}, 3.2 + 1e-12)) < guard.EPSILON
    assert abs(guard.delta({KEY: 3.2}, 3.2 + 1e-4)) > guard.EPSILON


def test_the_phase_ledger_is_this_phases_own_and_carries_no_run():
    """Every other phase's anchor is a different file. A run here would mean a model was called."""
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    assert set(ledger) == {KEY, "note", "cap_usd", "runs"}
    assert ledger["cap_usd"] == 0.0
    assert ledger["runs"] == []
    assert ledger[KEY] > 0
