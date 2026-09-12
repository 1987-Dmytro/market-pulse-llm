#!/usr/bin/env python3
"""The product's local server: the app at `/` and the four API routes it reads (PHASE-ship-1 §2).

    make serve        # http://localhost:8000/  — the app, or the stub until front-1 lands

Localhost only and no auth (§3): the public build is static and has no API at all, so nothing here
is reachable from anywhere but this Mac.

**It computes no figure.** Every number is a field of a result file, and every block says which
file it came from — `screen.threads` is the export's own reading of the queue (ruling 10.09 (qq) 6:
never the tick's «cooled and not yet read» counter, which counts threads of every channel), and
`money.remaining_usd` is the LAST recorded line of the cycle-3 ledger, read as a file. No balance
call is made here, ever: a display value is not a budget (§4.7).

`POST /api/tick` runs `scripts/tick.py` and nothing else — the $0 promotion of what the paid legs
already wrote. The paid reading has no entry point in this process (§2: a configured endpoint and
the guard's FITS are the operator's word, not this phase's).
"""

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import export_front_data as export_front  # noqa: E402
import runpod_guard as guard  # noqa: E402
import tick  # noqa: E402

# The paths are the tick's own — one spelling of each file, so the server and the loop cannot
# disagree about which store, which export and which schedule they mean. The suite points these at
# a temp copy; production leaves them alone.
APP_DIR = REPO_ROOT / "dashboard" / "app"
RESULTS = tick.EXPORT.parent
EXPORT = tick.EXPORT
STATE = tick.STATE
SCHEDULE = tick.SCHEDULE
DB = tick.DB

EXPORT_NAME = re.compile(r"[a-z0-9_]+\.json")
"""What `/api/exports/{name}` will look for. A name, not a path: the app asks for files that sit in
`results/`, and `..` or a slash is a 404 rather than a read of somewhere else."""

app = FastAPI(title="Market Pulse", description=__doc__)


def read_json(path: Path) -> dict:
    """A required source. Missing is a refusal that names the file — never a zero, never a blank."""
    if not path.exists():
        raise HTTPException(500, f"source missing: {tick.rel(path)}")
    return json.loads(path.read_text(encoding="utf-8"))


def windows() -> dict:
    """The windows with their anchors — from the store, and from the export on a clean clone.

    `data/derived/pulse.db` is a local derived store and gitignored (§3), so a fresh clone has the
    committed export and nothing else. Same five fields either way, and `from` says which was read.
    """
    if DB.exists():
        conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        rows = conn.execute(
            "SELECT window_id, anchor, days, since, until FROM windows ORDER BY anchor"
        ).fetchall()
        conn.close()
        return {
            "from": f"{tick.rel(DB)} :: windows",
            "windows": [
                {"id": one, "anchor": anchor, "days": days, "since": since, "until": until}
                for one, anchor, days, since, until in rows
            ],
        }
    export = read_json(EXPORT)
    return {
        "from": f"{tick.rel(EXPORT)} :: windows (no local store — `make tick` builds one)",
        "windows": export["windows"],
    }


@app.get("/api/status")
def status() -> dict:
    """What the header and the Петля tab read: the last tick, the windows, the queue, the money.

    The fields and their wording are `export_front.status`'s — the SAME shape the static build
    reads out of `results/front_data.json`, so the served and the static screen cannot disagree
    about a figure or about which file it came from. This route adds the two things only a running
    server knows: the tick's own state file, and the store's windows when a store is there.
    """
    export = read_json(EXPORT)
    ledger = read_json(guard.cycle3_path())
    if not ledger.get("sessions"):
        raise HTTPException(500, f"{tick.rel(guard.cycle3_path())} carries no recorded reading")
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else None
    return (
        export_front.status(export, ledger, tick.rel(guard.cycle3_path()))
        | {
            "tick": state
            or {
                "at": None,
                "why": f"no tick recorded — {tick.rel(STATE)} is written by `make tick` and is not"
                " committed",
            }
        }
        | windows()
    )


class Schedule(BaseModel):
    """The two intervals the operator may change, and the rule that keeps them a schedule.

    A tick under an hour is the paid loop's own footgun (`data/schedule.json` is what stops one),
    and a default below the minimum is not a schedule at all. Both refusals are the model's, so
    they arrive as a 422 with the offending field named — and the file is not opened until the body
    has passed ([[a_guard_that_runs_after_the_write]]).
    """

    min_interval_hours: float = Field(ge=1)
    default_interval_hours: float

    @model_validator(mode="after")
    def _default_at_or_above_the_minimum(self) -> "Schedule":
        if self.default_interval_hours < self.min_interval_hours:
            raise ValueError(
                f"default_interval_hours {self.default_interval_hours} is below"
                f" min_interval_hours {self.min_interval_hours}"
            )
        return self


@app.get("/api/schedule")
def get_schedule() -> dict:
    """The loop's schedule — `tick.schedule()` writes the defaults the first time and reads ever
    after, so the server and the tick answer from one file."""
    return tick.schedule(SCHEDULE)


@app.put("/api/schedule")
def put_schedule(body: Schedule) -> dict:
    """The two intervals, merged over what the file already carries so its own note survives."""
    doc = tick.schedule(SCHEDULE) | body.model_dump()
    SCHEDULE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return doc


@app.post("/api/tick")
def post_tick() -> dict:
    """«Тик зараз»: `scripts/tick.py` in a subprocess, with its counters and its exit code.

    $0 by construction — the tick promotes what is already on disk. The counters are the state file
    the tick itself wrote, not this process's reading of its stdout.
    """
    argv = [
        sys.executable, str(REPO_ROOT / "scripts" / "tick.py"),
        "--db", str(DB), "--out", str(EXPORT), "--state", str(STATE), "--schedule", str(SCHEDULE),
    ]
    try:
        run = subprocess.run(argv, capture_output=True, text=True, timeout=900, cwd=REPO_ROOT)
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "tick: no answer in 900 s; the run was killed") from None
    return {
        "exit_code": run.returncode,
        "stdout": run.stdout,
        "stderr": run.stderr,
        "state": json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else None,
    }


@app.get("/api/exports/{name}")
def export_file(name: str) -> FileResponse:
    """One of the JSON exports under `results/`, by name."""
    path = RESULTS / name
    if not EXPORT_NAME.fullmatch(name) or not path.is_file():
        raise HTTPException(404, f"no export named {name!r} under {tick.rel(RESULTS)}")
    return FileResponse(path, media_type="application/json")


STUB = """<!doctype html><meta charset="utf-8"><title>Market Pulse</title>
<style>body{font:14px/1.6 ui-sans-serif,system-ui,sans-serif;margin:3rem auto;max-width:44rem;
padding:0 1rem}code{background:#f0efec;padding:.1rem .3rem;border-radius:4px}</style>
<h1>Market Pulse</h1>
<p>The server runs; the app is not built yet — <code>dashboard/app/</code> is written by
<code>make front</code> (phase item «front-1»). The API is live:</p>
<ul><li><code>GET /api/status</code></li><li><code>GET /api/schedule</code> ·
<code>PUT /api/schedule</code></li><li><code>POST /api/tick</code></li>
<li><code>GET /api/exports/{name}</code></li></ul>
"""

if (APP_DIR / "index.html").is_file():
    # Mounted LAST: a mount at «/» answers every path the routes above did not claim. `StaticFiles`
    # refuses to construct on a missing directory, which is why this is a branch and not a line.
    app.mount("/", StaticFiles(directory=APP_DIR, html=True), name="app")
else:

    @app.get("/", response_class=HTMLResponse)
    def stub() -> str:
        return STUB


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="localhost — the API has no auth (§3)")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
