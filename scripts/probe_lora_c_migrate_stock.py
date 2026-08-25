#!/usr/bin/env python3
"""`results/lora_c_migrate_stock.json` — where a 48 GB card and a network volume can COEXIST, at $0.

`docs/PROMPT-lora-c-migrate.md` D1 asks for «a fresh read-only stock check of A6000/EU-SE-1 at issue
time». This takes that reading and the one it presupposes: **a network volume can only be attached
to a pod in its OWN datacenter** (`scripts/runbook_4a.md` §1 chose CA-MTL-3 on exactly that
intersection), and «which datacenters hold this card» and «which datacenters hold a volume at all»
are two different lists. Ruling (р) moves the line on the first of them. This probe takes both and
intersects them, because a card in a datacenter that cannot hold the 59 GB of weights is a card this
line cannot use ([[a_capability_gate_is_not_a_theme_gate]]).

**This probe creates nothing.** Three readings, all free:

- ``network-volume create --data-center-id NOPE`` — a create that is REFUSED, and whose refusal
  enumerates every volume-capable datacenter. It is the volume-create endpoint's OWN answer rather
  than a catalogue standing beside it ([[a_stock_window_needs_the_create_not_a_poll]]). A refused
  create bills nothing and creates nothing; `runpodctl network-volume list` before and after is the
  positive control, and it is recorded.
- ``datacenter list`` and ``gpu list --include-unavailable`` — the card catalogue from two
  independent surfaces. They spell «out of stock» differently (`''` and `'none'`), so both are
  normalised and every shared pair is compared; a disagreement is RECORDED, never averaged away.

The intersection is the deliverable. A price column is carried with it because the whole cap
arithmetic of the contract divides by one.

    python3.11 scripts/probe_lora_c_migrate_stock.py
"""

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "results" / "lora_c_migrate_stock.json"

MIN_VRAM_GB = 48
"""The floor this line's own measurements set, and not a preference.

`results/lora_c_vramprobe.json` closed 32 GB twice: the second time with `expandable_segments:True`
proven to have reached the trainer, reclaiming 0.79 GiB of fragmentation and still failing on a
request 0.64 GiB short. The only s/step this repo has ever measured — lora-b's 61.047 — was taken on
a 48 GB A6000. So 48 is the smallest card with a measurement behind it; the probe LISTS everything
at or above it and chooses nothing."""

OUT_OF_STOCK = {"", "none", None}
"""`datacenter list` writes `''` where `gpu list` writes `'none'`. Same fact, two spellings — the
record normalises both and :func:`the_two_listings_agree` checks that they never say anything else
about the same pair ([[two_instruments_two_inputs]])."""

BAD_DATACENTER = "NOPE"
"""The id given to the refused create. Any id the platform does not know produces the enumeration;
this one is `scripts/runbook_4a.md`'s own, so the two readings are comparable."""


def run_json(command: list[str], run=subprocess.run) -> object:
    """One read-only `runpodctl` listing, or a recorded failure — never a silent empty."""
    done = run(command, capture_output=True, text=True)
    if done.returncode != 0:
        return {"failed": " ".join(command), "returncode": done.returncode, "stderr": done.stderr}
    try:
        return json.loads(done.stdout)
    except json.JSONDecodeError:
        return {"unparsed": " ".join(command), "stdout": done.stdout[:400]}


def refused_create(run=subprocess.run) -> dict:
    """The volume-create endpoint's own list of datacenters that can hold a network volume.

    The refusal is the reading. Its message names the datacenters in prose, so the parse is
    deliberately narrow — the sentinel below, then a comma-separated list — and a message that does
    not carry it yields an EMPTY list and says so, rather than a plausible one
    ([[a_checker_whose_failure_is_silence]]).
    """
    command = [
        "runpodctl",
        "network-volume",
        "create",
        "--name",
        "probe",
        "--size",
        "1",
        "--data-center-id",
        BAD_DATACENTER,
    ]
    done = run(command, capture_output=True, text=True)
    message = (done.stdout + done.stderr).strip()
    sentinel = "Available data centers:"
    tail = message.split(sentinel, 1)[1] if sentinel in message else ""
    names = [one.strip(' ".').strip() for one in tail.split(".", 1)[0].split(",")]
    return {
        "command": " ".join(command),
        "the_create_was_refused": sentinel in message,
        "message": message,
        "datacenters": sorted(one for one in names if one),
    }


def normalise(status: object) -> str:
    return "none" if status in OUT_OF_STOCK else str(status)


def pairs_from_datacenter_list(catalogue: object) -> dict[tuple[str, str], str]:
    """`(datacenter, card) -> stock`, as `runpodctl datacenter list` reports it."""
    if not isinstance(catalogue, list):
        return {}
    return {
        (one["id"], card["displayName"]): normalise(card.get("stockStatus"))
        for one in catalogue
        for card in (one.get("gpuAvailability") or [])
    }


def pairs_from_gpu_list(catalogue: object) -> dict[tuple[str, str], str]:
    """The same map, as `runpodctl gpu list --include-unavailable` reports it."""
    if not isinstance(catalogue, list):
        return {}
    return {
        (where["dataCenterId"], one["displayName"]): normalise(where.get("stockStatus"))
        for one in catalogue
        for where in (one.get("dataCenterAvailability") or [])
    }


def the_two_listings_agree(left: dict, right: dict) -> dict:
    """Every pair both surfaces carry, compared. A disagreement is a row, not a warning."""
    shared = sorted(set(left) & set(right))
    differ = [
        {
            "datacenter": dc,
            "card": card,
            "datacenter_list": left[(dc, card)],
            "gpu_list": right[(dc, card)],
        }
        for dc, card in shared
        if left[(dc, card)] != right[(dc, card)]
    ]
    return {
        "pairs_in_datacenter_list": len(left),
        "pairs_in_gpu_list": len(right),
        "pairs_compared": len(shared),
        "disagreements": differ,
        "agree": not differ,
    }


def cards_at_or_above(catalogue: object, min_gb: int = MIN_VRAM_GB) -> dict:
    """Every catalogued card with at least `min_gb` of VRAM — price, memory, stock per datacenter.

    Matched on `memoryInGb`, never on the name: «A6000» is a substring of nothing useful and
    «RTX 6000 Ada», «L40S» and «PRO 6000 MIG 48GB» are the same 48 GB by a different word
    ([[run_the_instrument_on_the_named_example]]).
    """
    if not isinstance(catalogue, list):
        return {}
    return {
        one["displayName"]: {
            "gpu_id": one["gpuId"],
            "vram_gb": one["memoryInGb"],
            "secure_usd_per_hour": one.get("securePricePerHr"),
            "by_datacenter": {
                where["dataCenterId"]: normalise(where.get("stockStatus"))
                for where in (one.get("dataCenterAvailability") or [])
            },
        }
        for one in catalogue
        if (one.get("memoryInGb") or 0) >= min_gb
    }


def candidates(cards: dict, volume_capable: list[str]) -> list[dict]:
    """The intersection: at least `MIN_VRAM_GB`, IN stock, in a datacenter that takes a volume.

    Sorted by price, because the cap arithmetic divides by one. An empty list is an answer — it is
    the one this line got ([[the_empty_row_is_the_answer]]).
    """
    capable = set(volume_capable)
    rows = [
        {
            "card": name,
            "gpu_id": spec["gpu_id"],
            "vram_gb": spec["vram_gb"],
            "secure_usd_per_hour": spec["secure_usd_per_hour"],
            "datacenter": dc,
            "stock": stock,
        }
        for name, spec in cards.items()
        for dc, stock in spec["by_datacenter"].items()
        if stock != "none" and dc in capable
    ]
    rows.sort(key=lambda one: (one["secure_usd_per_hour"] or 0.0, one["card"], one["datacenter"]))
    return rows


def where_is(cards: dict, card: str, volume_capable: list[str]) -> dict:
    """One named card, datacenter by datacenter, each row saying whether a volume can live there."""
    spec = cards.get(card)
    if spec is None:
        return {"card": card, "found": False}
    capable = set(volume_capable)
    return {
        "card": card,
        "found": True,
        "vram_gb": spec["vram_gb"],
        "secure_usd_per_hour": spec["secure_usd_per_hour"],
        "datacenters": [
            {"datacenter": dc, "stock": stock, "takes_a_network_volume": dc in capable}
            for dc, stock in sorted(spec["by_datacenter"].items())
        ],
        "in_stock_and_volume_capable": [
            dc for dc, stock in spec["by_datacenter"].items() if stock != "none" and dc in capable
        ],
    }


THE_RULINGS_CARD = "RTX A6000"
THE_RULINGS_DATACENTER = "EU-SE-1"


def read(run=subprocess.run) -> dict:
    """The whole probe, as a record. Every listing is kept beside the conclusion drawn from it."""
    before = run_json(["runpodctl", "network-volume", "list"], run)
    refusal = refused_create(run)
    datacenters = run_json(["runpodctl", "datacenter", "list"], run)
    gpus = run_json(["runpodctl", "gpu", "list", "--include-unavailable"], run)
    after = run_json(["runpodctl", "network-volume", "list"], run)

    capable = refusal["datacenters"]
    cards = cards_at_or_above(gpus)
    rows = candidates(cards, capable)
    ruling = where_is(cards, THE_RULINGS_CARD, capable)

    return {
        "phase": "lora-c-migrate",
        "contract": "docs/PROMPT-lora-c-migrate.md",
        "authority": (
            "ruling (р), docs/STATUS.md — «линия обучения переезжает в EU-SE-1 на A6000 48 GB,"
            " $0.53/ч». D1 asks for a fresh read-only stock check of that card in that datacenter"
            " at issue time; this probe takes it, and the volume-capability reading the ruling"
            " presupposes"
        ),
        "read_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "creates_nothing": (
            "four listings and one REFUSED create. No pod, no endpoint, no volume, no template was"
            " created, started or stopped. `network-volume list` is recorded before and after as"
            " the positive control that the refusal created nothing"
        ),
        "network_volume_list_before": before,
        "network_volume_list_after": after,
        "the_listing_did_not_move": before == after,
        "volume_capable_datacenters": {
            "how": (
                "the create endpoint's own refusal of an unknown datacenter id, which enumerates"
                " them. Free, and it is the create path answering rather than a catalogue beside it"
            ),
            **refusal,
        },
        "minimum_vram_gb": MIN_VRAM_GB,
        "why_48": (
            "results/lora_c_vramprobe.json closed 32 GB twice, the second time with the allocator"
            " setting PROVEN to have reached the trainer and still 0.64 GiB short; the only s/step"
            " this repo has measured (lora-b, 61.047) was taken on a 48 GB A6000"
        ),
        "cards_at_or_above_the_minimum": cards,
        "candidates": rows,
        "candidate_count": len(rows),
        "the_rulings_card": ruling,
        "the_rulings_datacenter": THE_RULINGS_DATACENTER,
        "the_rulings_datacenter_takes_a_network_volume": THE_RULINGS_DATACENTER in capable,
        "cross_check": the_two_listings_agree(
            pairs_from_datacenter_list(datacenters), pairs_from_gpu_list(gpus)
        ),
        "caveat": (
            "a listing is not a create: stock at create-time may differ, in both directions, and"
            " the only free test of a create is the create itself. This reading dates the question."
            " The volume-capability half is stronger — it comes from the create endpoint's own"
            " refusal — but it is still a reading, not a promise"
        ),
        "commands": [
            "runpodctl network-volume list",
            refusal["command"],
            "runpodctl datacenter list",
            "runpodctl gpu list --include-unavailable",
        ],
    }


def main(argv: list[str] | None = None, run=subprocess.run) -> int:
    record = read(run)
    OUT.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"{OUT.relative_to(REPO_ROOT)} — {record['read_at']}")
    print(
        f"volume-capable datacenters: {len(record['volume_capable_datacenters']['datacenters'])}"
        f" · {THE_RULINGS_DATACENTER} among them:"
        f" {record['the_rulings_datacenter_takes_a_network_volume']}"
    )
    print(
        f"cards >= {MIN_VRAM_GB} GB, in stock, in a volume-capable datacenter: {len(record['candidates'])}"
    )
    for one in record["candidates"][:5]:
        print(
            f"  ${one['secure_usd_per_hour']}/h  {one['datacenter']:9} {one['card']:22}"
            f" {one['vram_gb']} GB  {one['stock']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
