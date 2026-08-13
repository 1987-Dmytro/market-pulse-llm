#!/usr/bin/env python3
"""Append to `results/spend_phase4.json` the phase entry for a step ledger's latest paid run ($0).

`scripts/repair_phase4_ledger.py` is the ONE-SHOT that went back for three sessions the phase ledger
never heard about. This is its live counterpart: the same append, from the same numbers, run at the
end of a paid stretch so the ledger never goes quiet again in the first place. They are separate
files because they carry separate facts — that one's `CAP_IN_FORCE_USD` is frozen at $25.00 by
design and must never move, and this one scores against the cap in force NOW, because the money it
witnesses is being spent now.

**Every number is READ from the step ledger, never typed.** `runs[-1].balance` and its `at`, against
the phase anchor, in the guard's own shape and rounding — so the phase entry and the step ledger
carry the same balance READING and `test_repair_phase4_ledger.py`'s permanent silence guard matches
them without an excuse.

It REFUSES rather than guesses, and writes nothing when it refuses: a missing step ledger, no paid
run in it, a timestamp the phase ledger already carries, or one that is not strictly after the last
entry there. Run it twice and the second run refuses — the refusal is what makes it idempotent.

    PYTHONPATH=src python3 scripts/witness_phase_ledger.py --source results/spend_5c2run.json \
        --label "5c2-run: Endpoint A, the two positions legs"
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import repair_phase4_ledger as repair  # noqa: E402
import runpod_guard as guard  # noqa: E402

LEDGER = repair.LEDGER


def entry(anchor: float, source: str, label: str, cap: float) -> dict:
    """One phase-ledger session, in `runpod_guard.main`'s shape and with its rounding."""
    run = repair.last_paid_run(source)
    spent = anchor - float(run["balance"])
    return {
        "at": run["at"],
        "balance": run["balance"],
        "spent_usd": round(spent, 4),
        "remaining_usd": round(cap - spent, 4),
        "note": (
            f"{label}. Written by scripts/witness_phase_ledger.py from {source} :: runs[-1], so"
            f" this entry and that run carry the SAME balance reading. remaining_usd is against"
            f" the ${cap:.2f} cap in force when the money was spent."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="the step ledger, repo-relative")
    parser.add_argument("--label", required=True, help="what this session was")
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--cap", type=float, default=guard.PHASE_CAP_USD)
    parser.add_argument("--dry-run", action="store_true", help="print the entry, write nothing")
    args = parser.parse_args(argv)

    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    anchor = float(ledger["runpod_balance_at_phase4_start"])
    sessions = ledger["sessions"]
    new = entry(anchor, args.source, args.label, args.cap)

    if any(session["at"] == new["at"] for session in sessions):
        raise SystemExit(
            f"{args.source}: {repair.rel(args.ledger)} already carries an entry at {new['at']}."
            " Each run is witnessed exactly once and none is rewritten. Nothing written."
        )
    if sessions and datetime.fromisoformat(new["at"]) <= datetime.fromisoformat(sessions[-1]["at"]):
        raise SystemExit(
            f"{args.source}: {new['at']} is not strictly after {sessions[-1]['at']}, the last"
            " entry in the phase ledger. A phase ledger is a time-ordered append and this script"
            " does not sort one. Nothing written."
        )

    print(f"anchor        ${anchor:.4f} at {ledger['anchored_at']}")
    print(f"cap in force  ${args.cap:.2f}")
    print(
        f"{new['at']}  balance {new['balance']:.10f}  spent {new['spent_usd']:.4f}"
        f"  remaining {new['remaining_usd']:.4f}"
    )
    if args.dry_run:
        print("--dry-run: nothing written")
        return 0
    ledger["sessions"] = [*sessions, new]
    args.ledger.write_text(
        json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"witnessed in {repair.rel(args.ledger)} ({len(ledger['sessions'])} sessions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
