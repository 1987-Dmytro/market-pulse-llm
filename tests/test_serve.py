"""The local server: it answers from the committed files, and it refuses a schedule that is not one.

`fastapi` lives in the `serve` extra, isolated like `baseline`, `xlmr` and `gpu` — a bare checkout
has no such wheel, so this file skips rather than reddening `make check` on one.
"""

import json
import shutil
import sys
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import runpod_guard as guard  # noqa: E402
import serve  # noqa: E402

EXPORT = REPO_ROOT / "results" / "promo_screen_data.json"
LEDGER = REPO_ROOT / "results" / "spend_cycle3.json"


@pytest.fixture
def client(tmp_path, monkeypatch):
    """The server over a COPY of the committed results, and a store that is not there.

    A temp copy is the point: `PUT /api/schedule` writes, `POST /api/tick` runs the real script,
    and neither may touch the repo's own files while the suite runs.
    """
    results, data = tmp_path / "results", tmp_path / "data"
    results.mkdir()
    data.mkdir()
    shutil.copy(EXPORT, results / EXPORT.name)
    shutil.copy(LEDGER, results / LEDGER.name)
    monkeypatch.setattr(serve, "RESULTS", results)
    monkeypatch.setattr(serve, "EXPORT", results / EXPORT.name)
    monkeypatch.setattr(serve, "STATE", results / "promo_tick.json")
    monkeypatch.setattr(serve, "SCHEDULE", data / "schedule.json")
    monkeypatch.setattr(serve, "DB", data / "derived" / "pulse.db")
    monkeypatch.setattr(guard, "CYCLE2_LEDGER", results / "spend_cycle2.json")
    return TestClient(serve.app)


def test_the_status_answers_from_the_files_and_names_each_one(client):
    """Every figure of the status line is a field of a committed file, and none is computed here.

    The queue is the export's own `screen.threads` — ruling 10.09 (qq) 6 — and not the tick's
    «cooled and not yet read», which counts threads of channels the product never reads. The money
    is the guard's last RECORDED line: no balance call is made, and none can be, from this process.
    """
    export = json.loads(EXPORT.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    body = client.get("/api/status").json()

    assert body["threads"] == export["screen"]["threads"]
    assert body["windows"] == export["windows"], "no store in the fixture — the export answers"
    assert "promo_screen_data.json :: windows" in body["from"]
    assert body["money"]["remaining_usd"] == ledger["sessions"][-1]["remaining_usd"]
    assert body["money"]["from"].endswith("sessions[-1]")
    assert body["tick"]["at"] is None and "make tick" in body["tick"]["why"]


def test_an_export_is_served_by_name_and_only_from_results(client):
    served = client.get(f"/api/exports/{EXPORT.name}")

    assert served.status_code == 200
    assert served.json() == json.loads(EXPORT.read_text(encoding="utf-8"))
    for name in ("../pyproject.toml", "spend_cycle9.json", "promo_screen_data.txt"):
        assert client.get(f"/api/exports/{name}").status_code == 404


def test_a_schedule_below_the_minimum_is_refused_and_the_file_is_unchanged(client):
    """Both ways, and both spellings of the same 30 minutes.

    The file is read back after every refusal: a validator that runs after the write would leave
    the loop on a schedule the API said it would not accept.
    """
    assert client.get("/api/schedule").json()["min_interval_hours"] == 1
    before = serve.SCHEDULE.read_text(encoding="utf-8")

    good = client.put("/api/schedule", json={"min_interval_hours": 2, "default_interval_hours": 8})
    assert good.status_code == 200
    assert good.json()["default_interval_hours"] == 8
    assert "note" in good.json(), "the file's own note survives the merge"
    written = serve.SCHEDULE.read_text(encoding="utf-8")

    for body in (
        {"min_interval_hours": 0.5, "default_interval_hours": 6},
        {"min_interval_hours": 2, "default_interval_hours": 0.5},
        {"min_interval_hours": 2},
    ):
        assert client.put("/api/schedule", json=body).status_code == 422
        assert serve.SCHEDULE.read_text(encoding="utf-8") == written

    assert before != written


def test_the_tick_runs_as_a_subprocess_and_says_so_when_there_is_no_store(client):
    """The button's own path — the real script, the real exit code, and the counters from the state
    file the tick wrote rather than from a reading of its stdout. A store that is not there is an
    answer (exit 0, named), which is what makes `make serve` runnable on a clean clone."""
    body = client.post("/api/tick").json()

    assert body["exit_code"] == 0
    assert "no store" in body["stderr"]
    assert body["state"] is None
