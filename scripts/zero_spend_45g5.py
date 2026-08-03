#!/usr/bin/env python3
"""The anchor that proves 4.5g5 called no model (docs/PROMPT-4.5g5.md, Budget).

A phase whose budget is $0.00 has nothing to meter, so the ledger is not a
counter here — it is a tripwire. Read lifetime provider usage before the work
starts, read it again at the end, and any difference at all means a request was
made that this phase had no licence to make.

Anchoring is once-only on purpose: re-reading the provider into an existing
anchor would move the baseline forward over exactly the spend it is meant to
catch, which is the footgun `results/spend_3b.json` documents.

    PYTHONPATH=src python3 scripts/zero_spend_45g5.py           # anchor, then check
    PYTHONPATH=src python3 scripts/zero_spend_45g5.py --check   # check only, never anchors

Exit code 1 means the delta is not zero. Writes `results/spend_45g5.json`.
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import relabel_intents as relabel  # noqa: E402
from eval_zero_shot import api_key  # noqa: E402

from market_pulse import zero_shot  # noqa: E402

PHASE = "45g5"
LEDGER = REPO_ROOT / "results" / "spend_45g5.json"

# Provider usage is a float carried through JSON; a hair of representation noise
# is not a request. Anything a request could cost is orders of magnitude above.
EPSILON = 1e-9

NOTE = (
    "lifetime OpenRouter usage read at the start of 45g5, before any work. This phase is "
    "pre-registered at $0.00 in completion requests (docs/PROMPT-4.5g5.md), so this anchor is a "
    "tripwire and not a budget: the phase-end delta has to be exactly zero. Never re-anchor into "
    "an existing file — that moves the baseline past the very spend it exists to catch. Every "
    "other phase's anchor is a different file and is never written here."
)


def anchored(ledger: dict | None, usage_now: float) -> dict:
    """The ledger to write: the existing anchor is kept, a missing one is set."""
    key = relabel.anchor_key(PHASE)
    if ledger and key in ledger:
        return ledger
    return {key: usage_now, "note": NOTE, "cap_usd": 0.0, "runs": []}


def delta(ledger: dict, usage_now: float) -> float:
    """Spend since the anchor. Zero is the only value this phase may report."""
    return usage_now - ledger[relabel.anchor_key(PHASE)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="refuse to create the anchor; only report the delta against an existing one",
    )
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    args = parser.parse_args()

    existing = json.loads(args.ledger.read_text(encoding="utf-8")) if args.ledger.exists() else None
    if args.check and existing is None:
        raise SystemExit(f"{relabel.rel(args.ledger)}: no anchor to check against")

    usage_now = zero_shot.total_usage(api_key())
    ledger = anchored(existing, usage_now)
    if existing is None:
        relabel.write_json(args.ledger, ledger)

    spent = delta(ledger, usage_now)
    anchor = ledger[relabel.anchor_key(PHASE)]
    print(f"{relabel.rel(args.ledger)}: anchor {anchor} · usage now {usage_now}")
    print(f"45g5 spend: ${spent:.6f} (pre-registered $0.00)")
    if abs(spent) > EPSILON:
        print("NOT ZERO — a completion request was made that this phase did not authorise")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
