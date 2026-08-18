#!/usr/bin/env python3
"""`results/pass1_probe_b_verdict.json` — pass1-probe's scorer, pointed at the b-attempt's evidence.

Bar P1, the census, the refusal shapes, the per-call price and the window re-price are
`scripts/score_pass1_probe.py`'s, called with its file constants swapped. Bar P1 therefore still
reaches `scorer.reader_comment_agreement` and `score_reader_probe_b.collapse` — the reader's own
comparison under the reader's own collapse — through exactly one implementation.

    PYTHONPATH=src python3.11 scripts/score_pass1_probe_b.py
"""

import sys
from contextlib import contextmanager
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import score_pass1_probe as scoring  # noqa: E402

PHASE = "pass1-probe-b"
PREREG = REPO_ROOT / "results" / "prereg_pass1_probe_b.json"
PACK = REPO_ROOT / "results" / "pass1_probe_b_pack.json"
EVIDENCE = REPO_ROOT / "results" / "pass1_probe_b_rows.jsonl"
RUN = REPO_ROOT / "results" / "pass1_probe_b_run.json"
OUT = REPO_ROOT / "results" / "pass1_probe_b_verdict.json"

SWAPPED = ("PHASE", "PREREG", "PACK", "EVIDENCE", "RUN", "OUT")


@contextmanager
def as_probe_b():
    ours = {name: globals()[name] for name in SWAPPED}
    keep = {}
    for name in ours:
        if not hasattr(scoring, name):
            raise SystemExit(
                f"scripts/score_pass1_probe.py has no `{name}` any more — this scorer is replacing"
                " a name that no longer exists and would silently score pass1-probe's own evidence."
                " Stop and report."
            )
        keep[name] = getattr(scoring, name)
    for name, value in ours.items():
        setattr(scoring, name, value)
    try:
        yield
    finally:
        for name, value in keep.items():
            setattr(scoring, name, value)


def main(argv: list[str] | None = None) -> int:
    with as_probe_b():
        return scoring.main(argv if argv is not None else ["--out", str(OUT)])


if __name__ == "__main__":
    raise SystemExit(main())
