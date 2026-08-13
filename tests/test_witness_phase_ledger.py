"""The live counterpart of the one-shot phase-ledger repair.

The property that matters is the one the permanent silence guard reads: the phase entry and the step
ledger's run carry the SAME balance reading. Everything else here is the refusals that keep it from
guessing.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import repair_phase4_ledger as repair  # noqa: E402
import witness_phase_ledger as witness  # noqa: E402


def step_ledger(tmp_path: Path, *, at="2026-08-14T09:00:00+00:00", balance=10.0) -> Path:
    path = tmp_path / "spend_step.json"
    path.write_text(
        json.dumps(
            {
                "runpod_balance_at_step_start": 11.0,
                "cap_usd": 8.0,
                "runs": [{"at": at, "balance": balance, "step_spent_usd": 1.0, "note": "a leg"}],
            }
        ),
        encoding="utf-8",
    )
    return path


def phase_ledger(tmp_path: Path, *, last="2026-08-13T08:00:00+00:00") -> Path:
    path = tmp_path / "spend_phase4.json"
    path.write_text(
        json.dumps(
            {
                "phase4_cap_usd": 33.0,
                "runpod_balance_at_phase4_start": 35.0,
                "anchored_at": "2026-08-01T08:34:09+00:00",
                "sessions": [{"at": last, "balance": 12.0, "spent_usd": 23.0, "note": "before"}],
            }
        ),
        encoding="utf-8",
    )
    return path


def run(tmp_path, *extra):
    step, phase = step_ledger(tmp_path), phase_ledger(tmp_path)
    return witness.main(
        ["--source", str(step), "--label", "a leg", "--ledger", str(phase), *extra]
    ), phase


def test_the_phase_entry_carries_the_step_ledgers_own_balance_reading(tmp_path):
    """The whole point: the silence guard matches on the balance, so it must not be re-read."""
    code, phase = run(tmp_path)
    sessions = json.loads(phase.read_text(encoding="utf-8"))["sessions"]

    assert code == 0
    assert len(sessions) == 2
    assert sessions[-1]["balance"] == 10.0
    assert sessions[-1]["at"] == "2026-08-14T09:00:00+00:00"
    assert sessions[-1]["spent_usd"] == 25.0  # 35.00 anchor - 10.00 balance
    assert sessions[-1]["remaining_usd"] == 8.0  # against the $33.00 cap in force


def test_witnessing_the_same_run_twice_refuses_and_writes_nothing(tmp_path):
    step, phase = step_ledger(tmp_path), phase_ledger(tmp_path)
    args = ["--source", str(step), "--label", "a leg", "--ledger", str(phase)]
    assert witness.main(args) == 0
    after_first = phase.read_bytes()

    with pytest.raises(SystemExit, match="already carries an entry"):
        witness.main(args)

    assert phase.read_bytes() == after_first, "a refusal writes nothing"


def test_an_out_of_order_entry_is_refused(tmp_path):
    step = step_ledger(tmp_path, at="2026-08-12T09:00:00+00:00")
    phase = phase_ledger(tmp_path, last="2026-08-13T08:00:00+00:00")

    with pytest.raises(SystemExit, match="not strictly after"):
        witness.main(["--source", str(step), "--label", "x", "--ledger", str(phase)])


def test_a_dry_run_writes_nothing(tmp_path):
    step, phase = step_ledger(tmp_path), phase_ledger(tmp_path)
    before = phase.read_bytes()

    assert (
        witness.main(["--source", str(step), "--label", "x", "--ledger", str(phase), "--dry-run"])
        == 0
    )

    assert phase.read_bytes() == before


def test_a_step_ledger_with_no_paid_run_is_refused(tmp_path):
    step = tmp_path / "empty.json"
    step.write_text(json.dumps({"runs": []}), encoding="utf-8")

    with pytest.raises(SystemExit, match="no paid run to append"):
        witness.main(
            ["--source", str(step), "--label", "x", "--ledger", str(phase_ledger(tmp_path))]
        )


def test_it_scores_against_the_cap_in_force_now_and_the_repair_does_not(tmp_path):
    """Two instruments, two caps, on purpose.

    The one-shot repair's $25.00 is frozen to the moment three historical sessions were billed and
    its docstring forbids importing today's constant. This one defaults to the live cap, because
    the money it witnesses is being spent under it.
    """
    assert repair.CAP_IN_FORCE_USD == 25.00
    assert witness.guard.PHASE_CAP_USD == 33.00
