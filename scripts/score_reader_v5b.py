#!/usr/bin/env python3
"""`results/reader_v5b_w1.jsonl` + gold r2 → `results/reader_v5b_verdict.json`.

**v5's scorer, pointed at this phase's files. Not one line of its arithmetic is re-spelled here.**
`scripts/score_reader_v5.py` carries the bars as module-level paths — `PHASE`, `PREREG`, `EVIDENCE`,
`RUN`, `LEDGER`, `OUT` — and its own sha is pinned by nothing, but the record it produced for v5 is a
sealed artefact and the contract that named it says «unchanged». So it is CALLED, with its constants
swapped for the length of the call and restored after (Dv451's idiom, the third generation of it: v4
called v3's, v5 called v4's and probe-b's, this calls v5's).

What that buys: bars 1-4 over leg A, the four mechanical bars over leg B, the three-state echo
census, the refusal and repair censuses, the transport-stop telemetry and bar 5 are ONE arithmetic
across v4, v5 and v5b — and bar 5 reads the reader-v5b step ledger rather than reader-v5's, which is
the only thing that would have been wrong about running the v5 script as it stands.

    PYTHONPATH=src python3.11 scripts/score_reader_v5b.py
"""

import argparse
import sys
from contextlib import contextmanager
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import runpod_guard as guard  # noqa: E402
import score_reader_v5 as v5  # noqa: E402

PHASE = "reader-v5b"
PREREG = REPO_ROOT / "results" / "prereg_reader_probe_v5b.json"
EVIDENCE = REPO_ROOT / "results" / "reader_v5b_w1.jsonl"
RUN = REPO_ROOT / "results" / "reader_v5b_run.json"
LEDGER = guard.step_ledger_path(PHASE)
OUT = REPO_ROOT / "results" / "reader_v5b_verdict.json"

SWAPPED = ("PHASE", "PREREG", "EVIDENCE", "RUN", "LEDGER", "OUT")


def _ours() -> dict:
    """Read at call time, never frozen into a dict at import — a monkeypatched path in one module and
    the original in the other is the bug this shape exists to prevent."""
    return {name: globals()[name] for name in SWAPPED}


@contextmanager
def as_this_phase():
    ours = _ours()
    keep = {name: getattr(v5, name) for name in ours}
    for name, value in ours.items():
        setattr(v5, name, value)
    try:
        yield
    finally:
        for name, value in keep.items():
            setattr(v5, name, value)


def build() -> dict:
    with as_this_phase():
        return v5.build()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    with as_this_phase():
        return v5.main(["--out", str(args.out)])


if __name__ == "__main__":
    raise SystemExit(main())
