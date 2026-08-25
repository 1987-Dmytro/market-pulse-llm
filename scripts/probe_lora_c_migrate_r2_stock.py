#!/usr/bin/env python3
"""The r2 migration's issue-time stock reading — a SIBLING of `probe_lora_c_migrate_stock.py`.

D1 asks for «a fresh read-only stock check of A100/CA-MTL-3 at issue time, dated». The previous
contract already built that instrument for a different card in a different datacenter, and all of
it — the refused create that enumerates the volume-capable datacenters, the >=48 GB filter on
`memoryInGb` rather than on the display name, the three-way intersection, the two-surface
cross-check and the before/after volume listing as the positive control — is the behaviour this
reading wants. Four module constants point it at the other ruling, so they are re-bound for the
length of one call and the parent is CALLED ([[a_self_pinning_producer_cannot_grow_a_parameter]]).

Creates nothing: four listings and one deliberately refused create.

    python3.11 scripts/probe_lora_c_migrate_r2_stock.py
"""

import contextlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import probe_lora_c_migrate_stock as parent  # noqa: E402

OUT = REPO_ROOT / "results" / "lora_c_migrate_r2_stock.json"
THE_RULINGS_CARD = "A100 PCIe"
THE_RULINGS_DATACENTER = "CA-MTL-3"

MINIMUM_STAYS_48 = (
    "the ruling's card is 80 GB, and the floor stays at 48 so that this table and the one taken"
    " 90 minutes earlier for ruling (р) are the SAME instrument. Raising it to 80 would drop every"
    " row the operator's alternatives live in, and a shorter table would read as a smaller market"
)


@contextlib.contextmanager
def the_probe_reads_the_r2_ruling():
    """The parent's four constants point at ruling (с), for the length of one call."""
    was = (parent.OUT, parent.THE_RULINGS_CARD, parent.THE_RULINGS_DATACENTER)
    parent.OUT = OUT
    parent.THE_RULINGS_CARD = THE_RULINGS_CARD
    parent.THE_RULINGS_DATACENTER = THE_RULINGS_DATACENTER
    try:
        yield
    finally:
        parent.OUT, parent.THE_RULINGS_CARD, parent.THE_RULINGS_DATACENTER = was


def read(run=subprocess.run) -> dict:
    with the_probe_reads_the_r2_ruling():
        record = parent.read(run)
    capable = set(record["volume_capable_datacenters"]["datacenters"])
    return {
        **record,
        "phase": "lora-c-migrate-r2",
        "contract": "docs/PROMPT-lora-c-migrate-r2.md",
        "authority": (
            "ruling (с), docs/STATUS.md — «A100 PCIe 80 GB, ≤$1.50/ч, CA-MTL-3». D1 asks for a"
            " fresh read-only stock check of that card in that datacenter at issue time; this is it"
        ),
        "minimum_vram_gb_stays_48": MINIMUM_STAYS_48,
        "the_rulings_card_is_reachable": bool(
            (record["the_rulings_card"] or {}).get("found")
            and THE_RULINGS_DATACENTER
            in (record["the_rulings_card"] or {}).get("in_stock_and_volume_capable", [])
        ),
        "the_price_ceiling_usd_per_hour": 1.5,
        "the_card_is_within_the_ceiling": (
            (record["the_rulings_card"] or {}).get("secure_usd_per_hour") is not None
            and float(record["the_rulings_card"]["secure_usd_per_hour"]) <= 1.5
        ),
        "cheaper_volume_capable_alternatives": [
            one
            for one in record["candidates"]
            if float(one["secure_usd_per_hour"])
            < float((record["the_rulings_card"] or {}).get("secure_usd_per_hour") or 0)
            and one["datacenter"] in capable
        ],
        "why_the_cheaper_rows_are_recorded": (
            "they are not this contract's to choose — ruling (с) names the card and the datacenter,"
            " and the DO-NOT list forbids picking either. They are recorded because a stock table"
            " that only shows the row the plan already chose cannot tell an operator that the"
            " premise behind the choice has moved ([[a_prefilter_cannot_certify_the_population]])"
        ),
    }


def main(argv: list[str] | None = None, run=subprocess.run) -> int:
    record = read(run)
    OUT.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    card = record["the_rulings_card"]
    print(f"{OUT.relative_to(REPO_ROOT)} — {record['read_at']}")
    print(
        f"{THE_RULINGS_CARD} in {THE_RULINGS_DATACENTER}:"
        f" reachable={record['the_rulings_card_is_reachable']}"
        f" · ${card.get('secure_usd_per_hour')}/h"
        f" · within the $1.50 ceiling={record['the_card_is_within_the_ceiling']}"
    )
    print(
        f"cheaper volume-capable rows at >= {parent.MIN_VRAM_GB} GB:"
        f" {len(record['cheaper_volume_capable_alternatives'])}"
    )
    return 0 if record["the_rulings_card_is_reachable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
