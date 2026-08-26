#!/usr/bin/env python3
"""`results/measurements.jsonl` — the registry of physical constants, one row per measurement.

Ruling (у) of 2026-08-26 names this file as the home of the numbers a projection rung reads: the
seconds a step takes, the peak memory it needs, the dollars an hour buys. Three of the six daily
stops of the `lora-c` line were resolved by reading a number that was already in the repo, so what
this file is for is being the ONE place a rate is looked up instead of remembered.

**`source` is required and is a path, not a story.** A rate with no source is a recollection, and a
recollection is what priced two paid sessions wrong ([[projected_rate_versus_measured_rate]],
[[a_paced_log_is_an_interleavable_clock]]). :func:`append` refuses a row without one.

Append-only and never rewritten: a measurement that was superseded is a second row, so the old
number stays readable beside the run that was priced with it.

    PYTHONPATH=src python3 scripts/measurements.py        # print what is registered
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / "results" / "measurements.jsonl"

REQUIRED = ("name", "value", "unit", "source", "measured_on", "contract")
"""What every row says. `measured_on` is the POPULATION or hardware the number was taken over —
a rate is a property of its sample, and the two are the same number only when the sample is the
population (`.claude/rules/registrations-and-draws.md`)."""


def rows(ledger: Path = LEDGER) -> list[dict]:
    if not ledger.exists():
        return []
    return [
        json.loads(one) for one in ledger.read_text(encoding="utf-8").splitlines() if one.strip()
    ]


def append(row: dict, ledger: Path = LEDGER) -> dict:
    """One measurement, checked and appended. A row missing a field is refused, not defaulted."""
    missing = [field for field in REQUIRED if not row.get(field)]
    if missing:
        raise ValueError(
            f"a measurement row needs {', '.join(missing)} and this one has none:"
            f" {json.dumps(row, ensure_ascii=False)[:200]}. A number nobody can trace back to the"
            " file that produced it is a recollection."
        )
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return row


BEFORE_RATES = (
    ("pass1_v1_seconds_per_call", "results/pass1_dev_base.jsonl", "dev-200, leg base (v1)"),
    ("pass1_v2_seconds_per_call", "results/pass1_dev_v2.jsonl", "dev-200, leg v2"),
    ("pass1_window_v2_seconds_per_call", "results/pass1_window_r2_v2.jsonl", "window r2, 901 rows"),
    ("pass2_r2_seconds_per_thread", "results/pass2_signals_r2_v1.jsonl", "pass2-r2, 75 bought"),
)
"""The BEFORE instrument's own rates, derived from the reply files that carry a `seconds` per row.

They are what the cap is sized against before the thinking smoke measures its own: a projection
needs a prior, and the prior has to be a number somebody measured rather than one somebody
remembers. Each row also carries the MAXIMUM, because a mean over 75 threads whose slowest is 5.7×
the mean is not what a liveness rung should be set from ([[a_rate_is_a_property_of_the_pod]]).
"""


def derive(contract: str) -> list[dict]:
    """One row per BEFORE rate, measured off the reply files at $0."""
    import statistics

    out = []
    for name, path, population in BEFORE_RATES:
        rows_ = [
            json.loads(one)
            for one in (REPO_ROOT / path).read_text(encoding="utf-8").splitlines()
            if one.strip()
        ]
        seconds = [
            one["seconds"]
            for one in rows_
            if one.get("seconds") is not None and not one.get("carried_from")
        ]
        out.append(
            {
                "name": name,
                "value": round(statistics.mean(seconds), 3),
                "max": round(max(seconds), 3),
                "n": len(seconds),
                "unit": "seconds",
                "source": path,
                "measured_on": population,
                "contract": contract,
                "instrument": "READER (enable_thinking false) — the BEFORE column's own rate",
            }
        )
    return out


def seed(contract: str, ledger: Path = LEDGER) -> list[dict]:
    """Append the rows this ledger does not already carry BY NAME. Idempotent, still append-only."""
    known = {one["name"] for one in rows(ledger)}
    return [append(one, ledger) for one in derive(contract) if one["name"] not in known]


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or [])
    if "--seed" in argv:
        for one in seed("think-zero-shot"):
            print(f"+ {one['name']}")
    for row in rows():
        print(
            f"{row['name']:34s} {row['value']:>10} {row['unit']:<9} n={row.get('n', '-'):<5}"
            f" {row['measured_on']:<26} {row['source']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
