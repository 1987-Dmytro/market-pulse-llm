#!/usr/bin/env python3
"""Append to `results/spend_phase4.json` the three paid sessions it never heard about ($0).

Deliverable 3 of `docs/PROMPT-5c2-prep-a.md`. The phase ledger has not been appended since
`2026-08-11T18:16:30Z` (sku-b-run). Three paid sessions ran after it — sku-b-v3, refused at the
(10)(a) gate and billed anyway; sku-b-v4; skub2 — and each lives only in its own step ledger. The
phase counter has been arithmetic-from-the-anchor ever since: right, and unwitnessed by the file
the guard reads.

**Every number is READ from the step ledger, never typed.** `runs[-1].balance` and its `at`, against
the phase anchor, in the guard's own shape and rounding. What is typed is the label prose, and
nothing downstream reads it.

**`remaining_usd` is scored against $25.00, the cap IN FORCE when that money was spent.** SPEC 3.18
(3) raised the phase cap to $30.00 on 2026-08-13, after all three sessions. A repaired history that
quietly re-scores itself under today's cap is a rewritten history — which is why the literal below
is this module's own and must never become an import of `runpod_guard.PHASE_CAP_USD`.

It REFUSES rather than guesses, and writes nothing when it refuses: a step ledger that is missing or
carries no paid run, a timestamp that is not strictly after the last entry already in the phase
ledger, or a timestamp that ledger already carries. Run it twice and the second run refuses on that
last rule — the refusal is what makes it idempotent.

An append, never a regeneration: the anchor, `anchored_at` and every existing session are read and
written back untouched, and the diff of a successful run is added lines only.

    python3.11 scripts/repair_phase4_ledger.py --dry-run    # prints the entries, writes nothing
    python3.11 scripts/repair_phase4_ledger.py
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / "results" / "spend_phase4.json"

CAP_IN_FORCE_USD = 25.00
"""The phase cap these three sessions were spent under, and this module's own literal on purpose.

`runpod_guard.PHASE_CAP_USD` is 30.00 from 2026-08-13 (SPEC 3.18 (3)). Importing it here for the
sake of one constant would silently re-score three historical entries under a cap that did not
exist when they were billed, and the ledger would read as if the sessions had five dollars more
room than they had."""

MISSING = (
    (
        "results/spend_sku_b_v3.json",
        "sku-b-v3-run: REFUSED by the (10)(a) go/no-go before the first gold call; boot and the two"
        " warm-up calls were billed and no attempt was consumed",
    ),
    (
        "results/spend_sku_b_v4.json",
        "sku-b-v4-run: the resumed pilot, 138 sources asked",
    ),
    (
        "results/spend_skub2.json",
        "skub2-run: the B′ re-measurement under instrument v2, 138 sources asked",
    ),
)
"""The three step ledgers, in the order their sessions ran — which is also the order they are
appended in, because a phase ledger is a time-ordered append and this script does not sort one."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def last_paid_run(source: str) -> dict:
    """`runs[-1]` of a step ledger — refusing anything this repair cannot read its numbers out of."""
    path = REPO_ROOT / source
    if not path.exists():
        raise SystemExit(
            f"{source}: the step ledger is missing. Its balance reading is the only record of what"
            " that session cost, and a phase entry typed without it would be a number nobody can"
            " re-derive. Nothing written."
        )
    runs = json.loads(path.read_text(encoding="utf-8")).get("runs") or []
    if not runs:
        raise SystemExit(
            f"{source}: no `runs` entry, so there is no paid run to append. Nothing written."
        )
    run = runs[-1]
    if missing := [field for field in ("at", "balance") if field not in run]:
        raise SystemExit(f"{source}: runs[-1] has no {missing}. Nothing written.")
    return run


def entry(anchor: float, source: str, label: str) -> dict:
    """One phase-ledger session, in the shape `runpod_guard.main` writes and with its rounding."""
    run = last_paid_run(source)
    spent = anchor - float(run["balance"])
    return {
        "at": run["at"],
        "balance": run["balance"],
        "spent_usd": round(spent, 4),
        "remaining_usd": round(CAP_IN_FORCE_USD - spent, 4),
        "note": (
            f"{label}. Phase-ledger entry REPAIRED 2026-08-13 by scripts/repair_phase4_ledger.py"
            " (5c2-prep-a): the session ran, it was logged in its own step ledger, and this file"
            f" never heard about it. Every number here is read from {source} :: runs[-1]."
            f" remaining_usd is against the ${CAP_IN_FORCE_USD:.2f} cap IN FORCE when the money was"
            " spent — SPEC 3.18 (3) raised the phase cap to $30.00 on 2026-08-13, after all three"
            " of these sessions, and a repaired history is not re-scored under a later cap."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--dry-run", action="store_true", help="print the entries, write nothing")
    args = parser.parse_args(argv)

    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    anchor = float(ledger["runpod_balance_at_phase4_start"])
    sessions = ledger["sessions"]
    seen = {session["at"] for session in sessions}
    last = datetime.fromisoformat(sessions[-1]["at"]) if sessions else None

    appended: list[dict] = []
    for source, label in MISSING:
        new = entry(anchor, source, label)
        if new["at"] in seen:
            raise SystemExit(
                f"{source}: {rel(args.ledger)} already carries an entry at {new['at']}. Each"
                " session is appended exactly once and none is rewritten — if this is a re-run,"
                " the repair is already done. Nothing written."
            )
        at = datetime.fromisoformat(new["at"])
        if last is not None and at <= last:
            raise SystemExit(
                f"{source}: {new['at']} is not strictly after {last.isoformat()}, the last entry"
                f" in {rel(args.ledger)}. A phase ledger is a time-ordered append and this repair"
                " does not sort one. Nothing written."
            )
        seen.add(new["at"])
        last, appended = at, [*appended, new]

    print(f"anchor            ${anchor:.4f} at {ledger['anchored_at']}")
    print(
        f"cap in force      ${CAP_IN_FORCE_USD:.2f} (SPEC 3.4 (4); 3.18 (3) raises it AFTER these)"
    )
    print(f"{'at':<26} {'balance':>12} {'spent':>10} {'remaining':>10}  source")
    for (source, _), new in zip(MISSING, appended, strict=True):
        print(
            f"{new['at']:<26} {new['balance']:>12.10f} {new['spent_usd']:>10.4f}"
            f" {new['remaining_usd']:>10.4f}  {source}"
        )

    if args.dry_run:
        print(f"--dry-run: {len(appended)} entries NOT written")
        return 0
    ledger["sessions"] = [*sessions, *appended]
    args.ledger.write_text(
        json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"appended {len(appended)} entries to {rel(args.ledger)} ({len(ledger['sessions'])} total)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
