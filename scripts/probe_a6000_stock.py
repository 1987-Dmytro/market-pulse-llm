#!/usr/bin/env python3
"""`results/lora_c_stock_probe.json` — what RunPod says is in stock, read-only and at $0.

`docs/PROMPT-lora-c-armb.md` D2. Ruling (к) names «один A6000» and `knowledge/hot.md` records
A6000 48 GB in EU-RO-1 as `none`, taken during `d7-reread`. That reading is old, and the cap
decision the operator is about to take rests partly on which card this line can actually get.

**This probe creates NOTHING.** `runpodctl gpu list` and `runpodctl datacenter list` are listings;
a probe that created a billable resource to find out whether one can be created would be billing
the question ([[a_probe_must_not_create_what_it_measures]]). The cost of that restraint is stated
rather than hidden: a listing is not a create, and stock at create-time may differ — the only free
test of a create is the create ([[a_stock_window_needs_the_create_not_a_poll]]).

The region is not a preference: `results/d7_reread_srv2b.json` records EU-RO-1 as the datacenter
CHOSEN for the network volume, and a pod that cannot mount the volume is a different plan.

    python3.11 scripts/probe_a6000_stock.py
"""

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "results" / "lora_c_stock_probe.json"

REGION = "EU-RO-1"
"""The network volume's datacenter — `results/d7_reread_srv2b.json::chosen`, read below, never typed
twice."""

VOLUME_RECORD = REPO_ROOT / "results" / "d7_reread_srv2b.json"

WANTED = ("RTX A6000", "A40")
"""The 48 GB Ampere class ruling (к) names, as RunPod's own `displayName` spells it. A40 is the same
48 GB silicon catalogued beside it, listed to be READ and not chosen.

Matched by EQUALITY, not by substring: `"A6000" in "RTX A6000"` is true and so is
`"A40" in "RTX A4000"`, and a 16 GB card answering for a 48 GB one is the whole question wrong
([[run_the_instrument_on_the_named_example]])."""


def listing(command: list[str]) -> object:
    """One read-only `runpodctl` listing, or a recorded failure — never a silent empty."""
    done = subprocess.run(command, capture_output=True, text=True)
    if done.returncode != 0:
        return {
            "failed": " ".join(command),
            "returncode": done.returncode,
            "stderr": done.stderr[:400],
        }
    try:
        return json.loads(done.stdout)
    except json.JSONDecodeError:
        return {"unparsed": " ".join(command), "stdout": done.stdout[:400]}


def in_region(catalogue: object, region: str) -> list[dict]:
    """Every catalogued card as the volume's datacenter sees it — price, memory, stock.

    A card with no row for this datacenter is carried with `stock: null` rather than dropped: «not
    catalogued here» and «catalogued here with none» are two different answers and one of them
    would otherwise be invisible ([[an_empty_field_hides_several_states]]).
    """
    if not isinstance(catalogue, list):
        return []
    out = []
    for card in catalogue:
        rows = {
            one.get("dataCenterId"): one.get("stockStatus")
            for one in card.get("dataCenterAvailability") or []
        }
        out.append(
            {
                "displayName": card.get("displayName"),
                "gpuId": card.get("gpuId"),
                "memoryInGb": card.get("memoryInGb"),
                "securePricePerHr": card.get("securePricePerHr"),
                "communityPricePerHr": card.get("communityPricePerHr"),
                "stock": rows.get(region),
                "catalogued_in_this_region": region in rows,
            }
        )
    return sorted(out, key=lambda cell: (cell["securePricePerHr"] or 99, cell["displayName"] or ""))


def region_of_the_volume() -> str:
    record = json.loads(VOLUME_RECORD.read_text(encoding="utf-8"))
    for block in record.values():
        if isinstance(block, dict) and block.get("chosen"):
            return str(block["chosen"])
    raise SystemExit(
        f"{VOLUME_RECORD.name} names no chosen datacenter — stop rather than guess one"
    )


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    out = Path(argv[0]) if argv else OUT
    region = region_of_the_volume()
    at = datetime.now(UTC).isoformat(timespec="seconds")
    record = {
        "phase": "lora-c-armb",
        "contract": "docs/PROMPT-lora-c-armb.md D2 — the stock probe, read-only",
        "read_at": at,
        "region": region,
        "commands": ["runpodctl gpu list --include-unavailable", "runpodctl datacenter list"],
        "creates_nothing": (
            "both commands are listings. No pod, no endpoint, no volume, no template was created,"
            " started or stopped by this file"
        ),
        "caveat": (
            "a listing is not a create: stock at create-time may differ, in both directions, and"
            " the only free test of a create is the create itself. This reading dates the question,"
            " it does not answer it"
        ),
        "wanted": list(WANTED),
    }
    catalogue = listing(["runpodctl", "gpu", "list", "--include-unavailable", "-o", "json"])
    record["in_the_volumes_region"] = in_region(catalogue, region)
    record["wanted_in_the_volumes_region"] = {
        cell["displayName"]: cell["stock"]
        for cell in record["in_the_volumes_region"]
        if cell["displayName"] in WANTED
    }
    record["with_stock_in_the_volumes_region"] = [
        cell for cell in record["in_the_volumes_region"] if cell["stock"] not in (None, "none")
    ]
    record["datacenter_list"] = listing(["runpodctl", "datacenter", "list", "-o", "json"])
    record["reading"] = (
        f"{len(record['with_stock_in_the_volumes_region'])} of"
        f" {len(record['in_the_volumes_region'])} catalogued cards report stock other than `none`"
        f" in {region}. The cards ruling (к) names read"
        f" {record['wanted_in_the_volumes_region'] or 'NOT CATALOGUED THERE AT ALL'}."
        " Prices are listed and nothing is chosen: the card is the operator's word at the cap"
        " decision, and this file only dates the question"
    )
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", "utf-8")
    print(f"wrote {out.relative_to(REPO_ROOT)}  read_at {at}  region {region}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
