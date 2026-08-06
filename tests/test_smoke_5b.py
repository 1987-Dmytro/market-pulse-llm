"""The 5b smoke's two decisions: which rows go, and whether the dollars can be believed.

The carve rebuild itself is `train_qlora`'s and tested there; what is tested here is the
part that decides something. `stamp_cost` writes the number every downstream projection
divides by, and a floor that fires on the wrong runtime stops a run for being priced
correctly — which is a worse failure than the one the floor exists to catch, because it
happens on the correct case.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
spec = importlib.util.spec_from_file_location("smoke_5b", REPO_ROOT / "scripts" / "smoke_5b.py")
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)

POD_USD_PER_HOUR = 0.53


@pytest.fixture
def record(tmp_path):
    path = tmp_path / "serving_5b.json"
    path.write_text(json.dumps({"timing": {"wall_seconds": 3600.0}}), encoding="utf-8")
    return path


def cost(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["cost"]


def test_a_pod_run_priced_at_its_own_rate_is_not_refused(record, capsys):
    """The serverless inequality is "above the pod class"; a pod bills AT it.

    $0.52 over an hour on a $0.53/h machine is a correctly-priced pod run — a minute of
    boot inside the guard's balance delta and outside the client's wall clock is enough
    to put it under. The serverless floor refuses exactly that.
    """
    assert smoke.stamp_cost(record, 0.52, POD_USD_PER_HOUR) == 0
    assert cost(record)["above_pod_floor"] is True
    assert cost(record)["floor_usd_per_second"] == pytest.approx(0.53 / 3600 * 0.5)
    assert "0.5 x the pod's posted" in cost(record)["floor_basis"]

    assert smoke.stamp_cost(record, 0.52) == 3  # the serverless floor, on the same reading
    assert cost(record)["above_pod_floor"] is False


def test_an_unsettled_balance_is_still_refused_on_a_pod(record, capsys):
    """What the floor is actually for. A balance RunPod has not settled reads as ~0,
    which would clear any projection and authorise a run the phase cannot afford."""
    assert smoke.stamp_cost(record, 0.0004, POD_USD_PER_HOUR) == 3
    assert cost(record)["above_pod_floor"] is False
    assert "STOP AND REPORT" in capsys.readouterr().out


def test_the_rows_are_drawn_round_robin_across_the_renderings():
    """The carve is sorted, so a head slice is all-T1 — and T2 carries the parent post,
    which is the one rendering that can fail on the worker."""
    carve = [{"task": "T1", "id": n} for n in range(20)] + [
        {"task": "T2", "id": n} for n in range(4)
    ]
    picked = smoke.balanced(carve, 8)
    assert [row["task"] for row in picked] == ["T1", "T2"] * 4
    # and it stops at what the carve holds rather than repeating a row
    assert len({(row["task"], row["id"]) for row in smoke.balanced(carve, 24)}) == 24
