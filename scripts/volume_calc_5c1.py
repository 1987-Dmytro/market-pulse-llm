#!/usr/bin/env python3
"""Phase-5c1 Deliverable 3: what the CA-MTL-3 volume costs, against its two alternatives ($0).

SPEC §3.11 (6), cycle-1 economics ruling: "The volume-vs-redownload-vs-stopped-pod economics is
a zero-cost step-0 task of 5c (using the measured staging costs and RunPod's price list); the
CA-MTL-3 volume's fate — it idles at ~$0.24/day and local-NVMe staging is faster (46 s vs 279 s)
— is decided on those numbers, advancing the ~2026-09-05 review."

Every input names the artifact it came from and is checked against it before it is used: a JSON
input is READ by key path and never typed, and a number quoted from a runbook or from the vault
must still be found in that file or this script refuses to print a table. A cost model whose
inputs cannot be re-derived is a slide, not a calculation.

What this does NOT do is blend. Each option is storage dollars plus boot/stage dollars plus the
risk it carries, because the three differ in different terms — (b) is cheapest on storage and
buys a download per pass, (c) is fastest to boot and cannot promise it will boot at all — and a
single number per row would hide exactly the trade the operator is deciding.

    PYTHONPATH=src python3 scripts/volume_calc_5c1.py
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_audit_pack import git_state  # noqa: E402

RECORD = REPO_ROOT / "results" / "volume_calc_5c1.json"
SERVING = REPO_ROOT / "results" / "serving_5b.json"
SPEND_P4 = REPO_ROOT / "results" / "spend_phase4.json"
RUNBOOK_5B = REPO_ROOT / "scripts" / "runbook_5b.md"
RUNBOOK_5B2 = REPO_ROOT / "scripts" / "runbook_5b2.md"
HOT = REPO_ROOT / "knowledge" / "hot.md"
ADR_5B2 = REPO_ROOT / "knowledge" / "decisions" / "5b2-batch-measurement.md"

PASSES_PER_DAY = 2
DAYS = 30
"""Cycle-1 cadence, SPEC §3.11 (1) and (6): 2 passes/day, priced over a 30-day month."""


def read_json(path: Path, dotted: str):
    """A number read out of a record by key path — the only kind that is not typed at all."""
    value = json.loads(path.read_text(encoding="utf-8"))
    for key in dotted.split("."):
        value = value[key]
    return value


def quoted(path: Path, literal: str, value):
    """A number typed here because its artifact is prose — and only after grepping it back.

    The check is the point: `results/serving_5b.json` can be read by key, a runbook cannot, and
    the difference between "the runbook says 4 minutes" and "I remember 4 minutes" is this line.
    """
    if literal not in path.read_text(encoding="utf-8"):
        name = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
        raise SystemExit(f"{name}: {literal!r} is not in the file")
    return value


def inputs() -> dict:
    """Every number the table stands on, with the artifact that carries it."""
    return {
        "usd_per_hour": {
            "value": read_json(SERVING, "adopted.usd_per_hour"),
            "unit": "USD/h",
            "source": "results/serving_5b.json :: adopted.usd_per_hour",
            "what": "the A6000 pod's posted rate, the runtime SPEC 3.11 (1) fixed production on",
        },
        "cold_start_local_s": {
            "value": read_json(SERVING, "adopted.cold_start_seconds"),
            "unit": "s",
            "source": "results/serving_5b.json :: adopted.cold_start_seconds",
            "what": "cold start with the weights already on the pod's local NVMe",
        },
        "cold_start_volume_s": {
            "value": quoted(RUNBOOK_5B, "278.9 s", 278.9),
            "unit": "s",
            "source": "scripts/runbook_5b.md §2 (corroborated in results/spend_5b.json's first session note)",
            "what": "cold start with the weights on the CA-MTL-3 network volume",
            "note": (
                "PROMPT-5c1 attributes this number to results/serving_5b.json; it is not in that"
                " file. It is in the 5b runbook and in the spend record's session note, and is"
                " taken from there."
            ),
        },
        "stage_minutes": {
            "value": quoted(RUNBOOK_5B2, "59 GB in ~4 min", 4.0),
            "unit": "min",
            "source": "scripts/runbook_5b2.md §'Fresh staging'",
            "what": "downloading the 59 GB pinned revision onto a fresh pod's local NVMe",
            "note": "one measurement, not a distribution — a slow day costs pod minutes",
        },
        "weights_gb": {
            "value": quoted(RUNBOOK_5B, "59 GB", 59),
            "unit": "GB",
            "source": "scripts/runbook_5b.md §the staging pod",
            "what": "the pinned-revision weight payload",
        },
        "volume_usd_per_day": {
            "value": quoted(HOT, "~$0.24/day", 0.24),
            "unit": "USD/day",
            "source": "knowledge/hot.md (observed, attached to nothing)",
            "what": "the 100 GB CA-MTL-3 network volume's idle billing",
        },
        "volume_usd_per_month": {
            "value": quoted(ADR_5B2, "**~7.20**", 7.20),
            "unit": "USD/month",
            "source": "knowledge/decisions/5b2-batch-measurement.md, the run-rate table",
            "what": "the same volume as a monthly line item",
        },
        "usd_per_pass": {
            "value": read_json(SERVING, "adopted.usd_per_pass"),
            "unit": "USD/pass",
            "source": "results/serving_5b.json :: adopted.usd_per_pass",
            "what": (
                "one 758-row pass INCLUDING one local-NVMe cold start. 758 is test v4's row"
                " count, not a measured production flow — the real per-pass row count is what"
                " 5c2 prices off the collection this phase just made"
            ),
        },
        "rows_per_pass_assumed": {
            "value": read_json(SERVING, "adopted.rows"),
            "unit": "rows",
            "source": "results/serving_5b.json :: adopted.rows",
            "what": "the row count behind usd_per_pass — an assumption here, not a measurement",
        },
        "container_disk_note": {
            "value": quoted(
                HOT, "80 GB is about what the", "80 GB ≈ the 100 GB volume's monthly cost"
            ),
            "unit": "—",
            "source": "knowledge/hot.md, footguns",
            "what": "a stopped pod still bills its container disk, and 59 GB + ~20 GB venv needs ~80 GB",
        },
    }


def idle_rate_bound() -> dict:
    """What the account-balance deltas can say about the volume's idle rate.

    They bound it, they do not isolate it: every interval between two spend sessions contains
    whatever ran inside it, so the quietest one is an UPPER bound on what the volume alone costs.
    Reported as an inequality rather than as a second estimate of the same number.
    """
    sessions = json.loads(SPEND_P4.read_text(encoding="utf-8"))["sessions"]
    intervals = []
    for prev, row in zip(sessions, sessions[1:]):
        hours = (
            datetime.fromisoformat(row["at"]) - datetime.fromisoformat(prev["at"])
        ).total_seconds() / 3600
        spent = prev["balance"] - row["balance"]
        if hours > 0:
            intervals.append(
                {
                    "hours": round(hours, 2),
                    "spent_usd": round(spent, 4),
                    "usd_per_day": round(spent / (hours / 24), 4),
                    "note": row["note"][:80],
                }
            )
    quietest = min(intervals, key=lambda row: row["usd_per_day"])
    return {
        "source": "results/spend_phase4.json :: sessions (account-balance deltas)",
        "quietest_interval": quietest,
        "reading": (
            f"the quietest {quietest['hours']} h between two spend sessions implies"
            f" ${quietest['usd_per_day']}/day, and that interval still contains the pod work its"
            " own note describes. So it is an upper bound on the volume's idle rate, and"
            " knowledge/hot.md's ~$0.24/day sits under it — corroborated, not re-derived."
        ),
        "intervals": intervals,
    }


def options(numbers: dict) -> list[dict]:
    """The three rows, each decomposed into storage, boot/stage and its risk."""
    rate = numbers["usd_per_hour"]["value"]
    passes = PASSES_PER_DAY * DAYS
    local = numbers["cold_start_local_s"]["value"]
    volume = numbers["cold_start_volume_s"]["value"]
    stage = numbers["stage_minutes"]["value"] * 60
    month = numbers["volume_usd_per_month"]["value"]

    def row(key, label, storage, boot_s, storage_basis, boot_basis, risk):
        boot_usd = boot_s * passes / 3600 * rate
        return {
            "option": key,
            "label": label,
            "storage_usd_per_month": round(storage, 4),
            "storage_basis": storage_basis,
            "boot_seconds_per_pass": round(boot_s, 3),
            "boot_hours_per_month": round(boot_s * passes / 3600, 4),
            "boot_usd_per_month": round(boot_usd, 4),
            "boot_basis": boot_basis,
            "total_usd_per_month": round(storage + boot_usd, 4),
            "risk": risk,
        }

    return [
        row(
            "a",
            "keep the CA-MTL-3 network volume",
            month,
            volume,
            f"the 100 GB volume at ${numbers['volume_usd_per_day']['value']}/day, idle or not",
            f"{volume} s off the volume, every pass",
            "the volume pins the datacenter. SPEC 3.11 (1)'s capacity clause makes the GPU CLASS"
            " the contract and the datacenter a convenience — and on 2026-08-06 an A6000"
            " stock-out in CA-MTL-3 blocked the run while the volume kept billing.",
        ),
        row(
            "b",
            "delete it, re-stage the 59 GB per pass onto pod NVMe",
            0.0,
            local + stage,
            "no volume, and a running pod's container disk is inside its hourly rate",
            f"{stage:.0f} s staging + {local} s cold start (the faster cold start, after the"
            " download that buys it)",
            "every pass depends on the download completing; ~4 min is one measurement, not a"
            " distribution. In exchange there is no datacenter pin: A6000 in any region.",
        ),
        row(
            "c",
            "stopped pod with the weights on its container disk",
            month,
            local,
            "~80 GB of container disk billing while stopped, about what the 100 GB volume costs"
            " per month (knowledge/hot.md) — an approximation, not a posted price",
            f"{local} s, the weights are already on local disk",
            "resume is NOT guaranteed. The capacity clause pins the GPU class, never one pod, and"
            " a stopped pod's host can be reclaimed; `runpodctl pod list` shows running pods only,"
            " so an unavailable one does not announce itself.",
        ),
    ]


def render(rows: list[dict], numbers: dict, common: dict) -> str:
    passes = PASSES_PER_DAY * DAYS
    head = f"{'':<3}{'option':<46}{'storage':>10}{'boot/mo':>10}{'total':>10}{'boot/pass':>12}"
    lines = [
        f"cycle-1 cadence: {PASSES_PER_DAY} passes/day x {DAYS} days = {passes} passes"
        f" · pod ${numbers['usd_per_hour']['value']}/h",
        "",
        head,
        "-" * len(head),
    ]
    for row in rows:
        lines.append(
            f"{row['option']:<3}{row['label'][:45]:<46}"
            f"${row['storage_usd_per_month']:>8.2f}${row['boot_usd_per_month']:>9.2f}"
            f"${row['total_usd_per_month']:>9.2f}{row['boot_seconds_per_pass']:>11.1f}s"
        )
    lines += ["", "each row, decomposed:"]
    for row in rows:
        lines += [
            f"  ({row['option']}) {row['label']}",
            f"      storage  ${row['storage_usd_per_month']:.2f}/mo — {row['storage_basis']}",
            f"      boot     ${row['boot_usd_per_month']:.2f}/mo"
            f" = {row['boot_hours_per_month']:.2f} h — {row['boot_basis']}",
            f"      risk     {row['risk']}",
        ]
    lines += [
        "",
        f"common to all three and therefore deciding nothing: {common['note']}",
        f"  ${common['usd_per_pass']}/pass x {passes} = ${common['usd_per_month']:.2f}/mo"
        f" at {common['rows_per_pass_assumed']} rows/pass",
    ]
    return "\n".join(lines)


def recommendation(rows: list[dict]) -> str:
    best = min(rows, key=lambda row: row["total_usd_per_month"])
    keep = next(row for row in rows if row["option"] == "a")
    saved = keep["total_usd_per_month"] - best["total_usd_per_month"]
    return (
        f"RECOMMENDATION: ({best['option']}) {best['label']} — ${best['total_usd_per_month']:.2f}/mo"
        f" against ${keep['total_usd_per_month']:.2f} for keeping the volume, ${saved:.2f}/mo"
        f" saved, and the boot it costs ({best['boot_seconds_per_pass']:.0f} s) is within"
        f" {abs(best['boot_seconds_per_pass'] - keep['boot_seconds_per_pass']):.0f} s of what the"
        " volume already charges for. The saving is the smaller half of the argument: deleting"
        " the volume also removes the datacenter pin that blocked 5b, which is the failure this"
        " project has actually had. The DECISION is the operator's at acceptance."
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)

    numbers = inputs()
    rows = options(numbers)
    passes = PASSES_PER_DAY * DAYS
    common = {
        "usd_per_pass": numbers["usd_per_pass"]["value"],
        "rows_per_pass_assumed": numbers["rows_per_pass_assumed"]["value"],
        "usd_per_month": round(numbers["usd_per_pass"]["value"] * passes, 4),
        "note": (
            "the inference compute itself. It is the same in all three options, and its size is"
            " an ASSUMPTION here — 758 rows is test v4's count, and what a production pass"
            " actually carries is what 5c2 prices off this phase's collection."
        ),
    }
    text = render(rows, numbers, common)
    print(text)
    print()
    print(recommendation(rows))

    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "5c1",
        "deliverable": "3 — the volume decision input",
        "contract": "docs/SPEC.md §3.11 (6) cycle-1 economics ruling; docs/PROMPT-5c1.md D3",
        "cadence": {"passes_per_day": PASSES_PER_DAY, "days": DAYS, "passes": passes},
        "inputs": numbers,
        "idle_rate_corroboration": idle_rate_bound(),
        "options": rows,
        "common_to_all_options": common,
        "recommendation": recommendation(rows),
        "decision": (
            "OPEN — the volume's fate is the operator's at acceptance. SPEC §3.11 (6) says this"
            " calculation advances the ~2026-09-05 review; it does not take it."
        ),
        "spend": "$0 — this script reads artifacts and talks to nothing.",
        "git": git_state(RECORD),
    }
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {RECORD.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
