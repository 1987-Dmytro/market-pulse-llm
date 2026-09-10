#!/usr/bin/env python3
"""`make loop`: wake on the schedule, run the $0 tick, write one line — and buy nothing, ever.

    make loop                       # until it is stopped
    python3.11 scripts/loop_daemon.py --once   # one wake, for a check

**The paid reading has no code path here** (PHASE-ship-1 §2). `data/loop.json :: endpoint` is the
operator's own field: empty, the log says the queue is unbought and the daemon sleeps; set, the log
says so and the daemon STILL only ticks — a configured endpoint plus the guard's FITS is the
operator's word before a paid pass, not a daemon's inference from a file it found ([[a_probe_must_
not_create_what_it_measures]]). Nothing is created in the cloud by this process.

What a wake does: `scripts/tick.py --if-due`, which reads `data/schedule.json` and does nothing
until the minimum interval has passed, and one line into `results/loop.log`. The queue is the
export's own `screen.threads.queue` — the same number the status line serves, never re-derived.
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import tick  # noqa: E402

LOOP = REPO_ROOT / "data" / "loop.json"
LOG = REPO_ROOT / "results" / "loop.log"

LOOP_DEFAULT = {
    "endpoint": "",
    "note": "WRITTEN BY THE OPERATOR. The serverless endpoint the paid reading of the remaining"
    " threads would run on. scripts/loop_daemon.py only READS it and says what it found: this"
    " phase has no paid path, and a filled-in endpoint is not an authorisation to spend"
    " (docs/PROCESS.md, money rungs).",
}


def loop_config(path: Path = LOOP) -> dict:
    """The loop's own file, created once with an EMPTY endpoint and read ever after."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(LOOP_DEFAULT, indent=2) + "\n", encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))


def reading(endpoint: str) -> str:
    """What the log says about the UNREAD threads — which of the two nothings this is.

    The queue is a field of the export, so a missing export says so rather than reading as zero.
    """
    export = tick.EXPORT
    if not export.exists():
        queue = f"queue unknown ({tick.rel(export)} missing — run `make tick`)"
    else:
        threads = json.loads(export.read_text(encoding="utf-8"))["screen"]["threads"]
        queue = f"queue {threads['queue']} threads"
    if not endpoint:
        return f"{queue} · reading unbought"
    return f"{queue} · endpoint set · the paid reading is the operator's word, never this daemon's"


def wake(now: datetime) -> str:
    """One tick, one line. The line is the log's whole content — a wake that wrote nothing is a
    wake nobody can tell from a daemon that died ([[a_crash_must_write_into_the_file_its_reader_
    opens]])."""
    run = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "tick.py"), "--if-due"],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    last = [line for line in run.stdout.splitlines() if line.startswith(("schedule:", "tick:"))]
    line = (
        f"{now.isoformat(timespec='seconds')}  tick exit {run.returncode}"
        f" · {' · '.join(last) or 'no schedule line'} · {reading(loop_config()['endpoint'])}"
    )
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as log:
        log.write(line + "\n")
    return line


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="one wake, then exit — for a check")
    args = parser.parse_args(argv)
    while True:
        print(wake(datetime.now(UTC)), flush=True)
        if args.once:
            return 0
        # The schedule is re-read every wake: the operator changes it through `PUT /api/schedule`
        # while this is running, and a daemon holding the interval it started with would ignore it.
        time.sleep(tick.schedule()["min_interval_hours"] * 3600)


if __name__ == "__main__":
    raise SystemExit(main())
