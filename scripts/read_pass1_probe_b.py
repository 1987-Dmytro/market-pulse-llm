#!/usr/bin/env python3
"""pass1-probe-b's driver — pass1-probe's own Mac side, pointed at the b-registration.

Not one line of transport is written here. `scripts/read_pass1_probe.py` is CALLED with its module
constants swapped (the idiom two generations down: v5 -> v5b -> pass 1 -> here), so the pack check,
the never-two-pods check, gate 0's ssh dead-man, the boot deadline, the full-pass projection, the
appended gate snapshots, the torn-last-line normaliser and the pass-1 ingest are all the code that
has already been paid for — and the cap inequality still has exactly ONE implementation in this repo.

The producer is swapped too, and that swap is not cosmetic: `check_pack` rebuilds the pack through
`producer.build_pack(record)` and compares byte for byte, so a b-run pointed at pass1-probe's
producer would rebuild a pack whose `registration.record` names the wrong registration and refuse.

    PYTHONPATH=src python3.11 scripts/read_pass1_probe_b.py --pack
    PYTHONPATH=src python3.11 scripts/read_pass1_probe_b.py --pre-create-check
    PYTHONPATH=src python3.11 scripts/read_pass1_probe_b.py --open --pod-id … --created-at … \\
        --usd-per-hour … --card …
    PYTHONPATH=src python3.11 scripts/read_pass1_probe_b.py --gate0 --ssh-ok
    PYTHONPATH=src python3.11 scripts/read_pass1_probe_b.py --deadlines
    PYTHONPATH=src python3.11 scripts/read_pass1_probe_b.py --gate
    PYTHONPATH=src python3.11 scripts/read_pass1_probe_b.py --ingest
"""

import sys
from contextlib import contextmanager
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import read_pass1_probe as p1  # noqa: E402
import runpod_guard as guard  # noqa: E402

# read through `globals()` by the swap below, which is why ruff cannot see the use
import write_pass1_prereg_b as producer  # noqa: E402, F401

PHASE = "pass1-probe-b"
PREREG = REPO_ROOT / "results" / "prereg_pass1_probe_b.json"
LEDGER = guard.step_ledger_path(PHASE)
PACK = REPO_ROOT / "results" / "pass1_probe_b_pack.json"
RAW = REPO_ROOT / "results" / "pass1_probe_b_pod.jsonl"
EVIDENCE = REPO_ROOT / "results" / "pass1_probe_b_rows.jsonl"
RECORD = REPO_ROOT / "results" / "pass1_probe_b_run.json"

SWAPPED = (*p1.SWAPPED, "producer")


@contextmanager
def as_probe_b():
    """pass 1's module constants swapped for the b-attempt's, and put back after.

    `read_pass1_probe.as_this_phase` reads ITS globals at call time and pushes them down onto v5b,
    which pushes them onto v5, so one assignment per name here reaches all three modules. Restored
    in a `finally`: a module left pointing at another attempt's files is the bug that only shows up
    in the second command, which on this transport is the one with a meter running.
    """
    ours = {name: globals()[name] for name in SWAPPED}
    keep = {}
    for name in ours:
        if not hasattr(p1, name):
            raise SystemExit(
                f"scripts/read_pass1_probe.py has no `{name}` any more, so this driver is replacing"
                " something that no longer exists and the run would silently read pass1-probe's own"
                " files. Stop and report."
            )
        keep[name] = getattr(p1, name)
    for name, value in ours.items():
        setattr(p1, name, value)
    try:
        yield
    finally:
        for name, value in keep.items():
            setattr(p1, name, value)


def main(argv: list[str] | None = None) -> int:
    with as_probe_b():
        return p1.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
