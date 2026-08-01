#!/usr/bin/env python3
"""The $25 Phase 4 GPU cap, enforced before a pod starts rather than after.

SPEC amendment 3.4 (4) fixes a hard cap of $25 across all of Phase 4, "checked
against RunPod billing before every start". This is that check, in the shape
`zero_shot.Budget` already proved on OpenRouter: two readings of the same
spend, and the pessimistic one wins.

- **Balance delta.** `results/spend_phase4.json` anchors the RunPod balance as
  it stood when Phase 4 opened; spend is that anchor minus the balance now.
  Always available, and it counts everything RunPod charges for — including a
  network volume, which bills while the pod is stopped. "Pod stopped" is not
  "spend stopped".
- **Billing history.** `runpodctl billing pods` / `billing network-volume`
  since the anchor timestamp. Corroboration, and the thing the amendment names.
  It is read defensively: an unrecognised payload is reported as unreadable and
  never silently becomes $0.00 of spend.

The anchor file is `spend_3b.json`'s sibling and carries its footgun: delete or
regenerate it and the phase counter silently resets to zero at today's balance.

    python3.11 scripts/runpod_guard.py                 # before a start; exit 1 refuses
    python3.11 scripts/runpod_guard.py --note "4a zero-shot run"   # log a session
"""

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / "results" / "spend_phase4.json"

PHASE_CAP_USD = 25.00
"""SPEC amendment 3.4 (4). Not a target — the line the run does not cross."""


def runpodctl(*args: str):
    """One read-only runpodctl call, as JSON. Never creates or destroys anything."""
    result = subprocess.run(
        ["runpodctl", *args, "--output", "json"], capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def balance() -> float:
    """The account balance RunPod itself reports, in dollars."""
    return float(runpodctl("user")["clientBalance"])


def sum_costs(payload) -> tuple[float, bool]:
    """Every cost-like number in a billing payload, and whether it was readable.

    The billing schema is not documented and was empty when this was written,
    so the walk is deliberately broad: anything under a key containing "cost" or
    "amount" counts. Over-counting refuses a start too early, which is the safe
    direction for a cap; inventing a zero is the one outcome this must not have.
    """
    total, seen = 0.0, False
    stack = [payload]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, int | float) and not isinstance(value, bool):
                    if "cost" in key.lower() or "amount" in key.lower():
                        total += float(value)
                        seen = True
                else:
                    stack.append(value)
        elif isinstance(node, list):
            stack.extend(node)
    return total, seen


def billing_since(anchored_at: str) -> tuple[float, str]:
    """Pods plus network volumes since the anchor: the dollars, and how they read."""
    total, readable, empty = 0.0, False, True
    for kind in ("pods", "network-volume"):
        try:
            payload = runpodctl("billing", kind, "--start-time", anchored_at)
        except (OSError, subprocess.CalledProcessError, ValueError) as err:
            return total, f"unreadable ({type(err).__name__})"
        if payload:
            empty = False
        found, seen = sum_costs(payload)
        total += found
        readable |= seen
    if empty:
        return 0.0, "no billing rows yet"
    return total, "read" if readable else "unreadable (no cost field in the payload)"


def spend(anchor_balance: float, balance_now: float, billing_total: float) -> float:
    """The pessimistic reading of what Phase 4 has cost so far."""
    return max(anchor_balance - balance_now, billing_total)


def read_ledger(balance_now: float) -> dict:
    """The anchor, created once. Never regenerated — see the module docstring."""
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {
        "phase4_cap_usd": PHASE_CAP_USD,
        "runpod_balance_at_phase4_start": balance_now,
        "anchored_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "note": (
            "RunPod account balance read at the start of Phase 4, before the first pod or"
            " network volume existed. Phase spend = this anchor minus the balance now, and"
            " the $25 cap of SPEC amendment 3.4 (4) is enforced against that difference."
            " Delete or regenerate this file and the counter silently restarts at today's"
            " balance — the same footgun results/spend_3b.json carries."
        ),
        "sessions": [],
    }


def write_ledger(ledger: dict) -> None:
    LEDGER.parent.mkdir(exist_ok=True)
    LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--note", help="record this reading as a pod session in the ledger")
    args = parser.parse_args(argv)

    balance_now = balance()
    ledger = read_ledger(balance_now)
    anchor = float(ledger["runpod_balance_at_phase4_start"])
    billing_total, how = billing_since(ledger["anchored_at"])
    spent = spend(anchor, balance_now, billing_total)
    remaining = PHASE_CAP_USD - spent

    print(f"anchor            ${anchor:.2f} at {ledger['anchored_at']}")
    print(f"balance now       ${balance_now:.2f}")
    print(f"  balance delta   ${anchor - balance_now:.4f}")
    print(f"  billing since   ${billing_total:.4f} ({how})")
    if how.startswith("unreadable"):
        # The cap still holds — the balance delta is the binding reading and it
        # cannot be fooled by a schema change. But a corroborating number that
        # silently became $0.00 must say so out loud, not blend into the table.
        print(
            "  WARNING: the billing payload could not be read, so only the balance delta is"
            " counting. Look at `runpodctl billing pods` by hand before the next start.",
            file=sys.stderr,
        )
    print(f"PHASE 4 SPENT     ${spent:.4f} of ${PHASE_CAP_USD:.2f}")
    print(f"REMAINING         ${remaining:.4f}")

    if not LEDGER.exists():
        write_ledger(ledger)
        print(f"anchored {LEDGER.name} — commit it and never regenerate it")

    if balance_now > anchor:
        print(
            f"\nREFUSED: the balance (${balance_now:.2f}) is above the anchor (${anchor:.2f}),"
            " so the account was topped up after Phase 4 opened and the delta no longer"
            " measures this phase. Re-anchoring is an operator decision, not a script's.",
            file=sys.stderr,
        )
        return 1
    if spent >= PHASE_CAP_USD:
        print(
            f"\nREFUSED: the ${PHASE_CAP_USD:.2f} Phase 4 cap is reached (${spent:.4f} spent)."
            " Stop and report — a cap is not raised to finish a run.",
            file=sys.stderr,
        )
        return 1

    if args.note:
        ledger["sessions"].append(
            {
                "at": datetime.now(UTC).isoformat(timespec="seconds"),
                "balance": balance_now,
                "spent_usd": round(spent, 4),
                "remaining_usd": round(remaining, 4),
                "note": args.note,
            }
        )
        write_ledger(ledger)
        print(f"logged: {args.note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
