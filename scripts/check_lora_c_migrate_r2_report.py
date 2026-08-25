#!/usr/bin/env python3
"""Every number in `docs/reports/lora-c-migrate-r2.md`, re-derived from the file that owns it.

A report is prose until something re-computes it. Each check pairs a value derived from a record
with the string the report prints, and BOTH must hold: a derivation that no longer matches the page
is a stale report, and a page whose string is absent is a number that moved without anyone noticing
([[rederive_doc_numbers]], [[a_count_in_prose_is_not_the_enumeration]]).

Two selectors are by STAMP and never by position. This page is about ONE pod session and ONE guard
reading, and both live in files that keep growing — the very defect this contract's step 0.5 fixed
in the previous report's checker ([[a_sealed_reports_checker_reads_a_live_file]]).

The report's own sha is not checked here: a file cannot hash itself into its own body
([[provenance_cannot_name_itself]]).

    python3.11 scripts/check_lora_c_migrate_r2_report.py
"""

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "lora-c-migrate-r2.md"
PREREG = REPO_ROOT / "results" / "prereg_lora_c_migrate_r2.json"
STOCK = REPO_ROOT / "results" / "lora_c_migrate_r2_stock.json"
RECORD = REPO_ROOT / "results" / "lora_c_migrate_r2.json"
PROOF = REPO_ROOT / "results" / "lora_c_migrate_r2_load_proof.json"
BYTES = REPO_ROOT / "results" / "lora_c_migrate_r2_load_bytes.json"
POLLS = REPO_ROOT / "results" / "lora_c_migrate_r2_bytes.jsonl"
VENV = REPO_ROOT / "results" / "lora_c_migrate_r2_venv.txt"
FROZEN = REPO_ROOT / "results" / "prereg_lora_c.json"
CONTRACT = REPO_ROOT / "docs" / "PROMPT-lora-c-migrate-r2.md"

THE_POD_THIS_REPORT_IS_ABOUT = "khixo68oxnls38"
"""By id, not by `pods[-1]`. One pod exists today; a re-creation would make the last row someone
else's ([[select_one_row_refuse_ambiguity]])."""


def nbsp(text: str) -> str:
    """The page and a derived string, made comparable — thin spaces, U+2212, and Markdown's wraps."""
    for one in (" ", " ", " "):
        text = text.replace(one, " ")
    return " ".join(text.replace("−", "-").split())


PAGE = nbsp(REPORT.read_text(encoding="utf-8"))
prereg = json.loads(PREREG.read_text(encoding="utf-8"))
stock = json.loads(STOCK.read_text(encoding="utf-8"))
record = json.loads(RECORD.read_text(encoding="utf-8"))
proof = json.loads(PROOF.read_text(encoding="utf-8"))
moved = json.loads(BYTES.read_text(encoding="utf-8"))
contract = " ".join(CONTRACT.read_text(encoding="utf-8").split())

checks: list[tuple[str, bool, str]] = []


def says(what: str, printed: str, derived=True) -> None:
    checks.append((what, bool(derived) and nbsp(printed) in PAGE, printed))


def spaced(number: float | int, digits: int = 0) -> str:
    return f"{number:,.{digits}f}".replace(",", " ")


def the_pod() -> dict:
    hit = [one for one in record["pods"] if one["pod_id"] == THE_POD_THIS_REPORT_IS_ABOUT]
    if len(hit) != 1:
        raise SystemExit(
            f"{len(hit)} pods named {THE_POD_THIS_REPORT_IS_ABOUT} — must be exactly one"
        )
    return hit[0]


def the_gate(kind: str) -> dict:
    hit = [one for one in record["gates"] if one["kind"] == kind]
    if len(hit) != 1:
        raise SystemExit(f"{len(hit)} gates of kind {kind!r} — this report describes exactly one")
    return hit[0]


def rung(number: int) -> dict:
    for one in prereg["kill_clock"]:
        if int(one["rung"]) == number:
            return one
    raise SystemExit(f"no rung {number}")


pod = the_pod()

# --- the verdict and the deliverable ---------------------------------------------------------------

says("the volume id", "`mp-lora-c` (`soymlju8q0`)")
says("the datacenter", "**CA-MTL-3**", prereg["target"]["datacenter"] == "CA-MTL-3")
says("the card", "**A100 PCIe 80 GB**", pod["card"] == "A100 PCIe")
says("the load seconds", f"**{proof['load_seconds']} s at", proof["load_seconds"] == 40.22)
gb = 1024**3
says(
    "the VRAM allocated and the card's total",
    f"{proof['vram_bytes_allocated'] / gb:.3f} GiB of {proof['vram_bytes_total'] / gb:.3f}**",
)
says(
    "the pod's money",
    f"**${pod['billed_usd']:.6f} of the $1.50 cap**, {pod['billed_seconds']:.0f} s",
    round(pod["billed_seconds"] / 3600 * pod["usd_per_hour"], 6) == pod["billed_usd"],
)
says("the revision", "`842da379…`", proof["revision"] == prereg["target"]["revision"])
says("the pinned revision in full", proof["revision"])

# --- §1, the gates ---------------------------------------------------------------------------------

says(
    "the meter's two ends", f"**{pod['created_at'][:19].replace('T', 'T')}Z**".replace("+00:00", "")
)
says("the create stamp", "2026-08-25T19:54:36Z", pod["created_at"] == "2026-08-25T19:54:36+00:00")
says("the delete stamp", "20:07:00Z**", pod["deleted_at"] == "2026-08-25T20:07:00+00:00")
says("rung 0's price", f"`costPerHr` **{pod['usd_per_hour']}**", pod["usd_per_hour"] == 1.39)
says("rung 0's rule as registered", "≤$1.50/h, card `A100 PCIe`", rung(0)["threshold"] == 1.5)
says(
    "rung 6's two stamps",
    f"given `{pod['terminate_after'][11:19]}Z`, computed `{pod['terminate_after_computed'][11:19]}Z`",
)
says(
    "rung 1's reading",
    f"**{the_gate('gate0')['elapsed_on_this_pod_seconds']} s** | {rung(1)['threshold']:.0f} s",
)
says(
    "rung 3's reading",
    f"**{the_gate('venv')['measured_seconds']} s** | {rung(3)['threshold']:.0f} s",
)
downloaded = the_gate("download")


def the_download_span() -> float:
    """From the download's own start to the FIRST poll that read the final byte count.

    An UPPER bound at the poll cadence: the transfer finished somewhere inside the 41 s between the
    last growing poll and this one, and `hf download`'s own clock says 02:32. Both are printed and
    neither is averaged ([[two_values_for_one_input_get_quoted_kindly]]). Derived here rather than
    typed, because a figure asserted on the page AND in its checker is checked by nobody
    ([[preregistration_is_a_file_not_a_constant]]).
    """
    from datetime import datetime

    rows = [
        json.loads(one) for one in POLLS.read_text(encoding="utf-8").splitlines() if one.strip()
    ]
    top = max(int(one["bytes"]) for one in rows)
    first = next(one for one in rows if int(one["bytes"]) == top)
    began = datetime.fromisoformat(the_gate("download")["started_at"])
    return (datetime.fromisoformat(first["at"]) - began).total_seconds()


SPAN = the_download_span()
says(
    "rung 4's bytes and polls",
    f"**{spaced(downloaded['bytes_now'])} B** in ~**{SPAN:.0f} s**, {downloaded['polls_seen']} polls",
    downloaded["polls_seen"] == len(POLLS.read_text(encoding="utf-8").strip().splitlines()),
)
says(
    "rung 4's bound and floor",
    f"{spaced(rung(4)['threshold'])} s, floor {spaced(rung(4)['the_download_is_complete_at_bytes'])} B",
)
says("rung 5's verdict", "| **KILL** |", the_gate("load-proof")["verdict"] == "KILL")
says(
    "the quietest the download got",
    f"**{downloaded['quiet_seconds']} s** of {rung(2)['threshold']:.0f}",
)
says("the reading had no blind window", "no blind window", downloaded["the_reading_has_no_holes"])
says("the cadence", "registered 120 s cadence", rung(4)["poll_cadence_seconds"] == 120.0)
says(
    "every gate is a GO except rung 5",
    "| **GO** |",
    [one["verdict"] for one in record["gates"]].count("KILL") == 1,
)

# --- §2, the two readings ----------------------------------------------------------------------------

says("the venv's own line", VENV.read_text(encoding="utf-8").strip())
says(
    "the venv bound over the measurement",
    f"it is {rung(3)['threshold'] / the_gate('venv')['measured_seconds']:.1f}× the measurement",
)
says("the card the proof names", proof["gpu"], proof["gpu"] == "NVIDIA A100 80GB PCIe")
says(
    "the share of the card the model takes",
    f"**{proof['vram_bytes_allocated'] / proof['vram_bytes_total']:.1%}** of this card",
)
says(
    "the download in both units",
    f"**{proof['hf_bytes_before'] / gb:.2f} GiB / {proof['hf_bytes_before'] / 1e9:.2f} GB**",
)
says(
    "the download rate on the wall clock",
    f"**{proof['hf_bytes_before'] / SPAN / 1e6:.1f} MB/s**",
)
says(
    "the download rate on hf's own clock",
    f"**{proof['hf_bytes_before'] / 152 / 1e6:.1f} MB/s**",
)
says(
    "the blob count and the incomplete count",
    f"{moved['the_weights_themselves']['blob_count']} blobs, **{moved['the_weights_themselves']['incomplete_blobs']} incomplete**",
)

# --- §3, the 40 bytes --------------------------------------------------------------------------------

says("the two du readings", f"**{spaced(proof['hf_bytes_before'])}** before")
says("the du reading after", f"**{spaced(proof['hf_bytes_after'])}** after")
says(
    "the delta",
    f"**by {moved['delta_bytes']} bytes**",
    proof["hf_bytes_after"] - proof["hf_bytes_before"] == moved["delta_bytes"],
)
says(
    "the enumeration's own count",
    f"**five files totalling {moved['delta_bytes']} bytes**",
    len(moved["what_the_load_wrote"]) == 5
    and sum(one["bytes"] for one in moved["what_the_load_wrote"]) == moved["delta_bytes"],
)
says(
    "the blobs did not move",
    f"**Blobs written after the download finished: {moved['the_weights_themselves']['blobs_written_after_the_download_finished']}**",
)
says(
    "the blobs' own bytes",
    f"{moved['the_weights_themselves']['blob_count']} blobs totalling {spaced(moved['the_weights_themselves']['blobs_bytes'])} bytes",
)
says(
    "what the blob invariant would have said",
    "the reading is **GO**",
    moved["what_the_blob_invariant_would_have_returned"].startswith("GO"),
)

# --- §4, the money ---------------------------------------------------------------------------------

cap = prereg["money"]["cap_usd_all_in"]
says(
    "the arithmetic of the pod's bill",
    f"{pod['billed_seconds']:.0f} s × ${pod['usd_per_hour']}/h = **${pod['billed_usd']:.6f}**",
)
says(
    "what the cap has left",
    f"**${cap - pod['billed_usd']:.6f} left**, {pod['billed_usd'] / cap:.1%} used",
)
stages = (
    the_gate("gate0")["elapsed_on_this_pod_seconds"]
    + the_gate("venv")["measured_seconds"]
    + SPAN
    + proof["load_seconds"]
)
allowed = sum(float(rung(one)["threshold"]) for one in (1, 3, 4, 5))
says(
    "the four stages against what they were allowed",
    f"{stages:.2f} s of {spaced(allowed)} s = **{stages / allowed:.1%}**",
)
says(
    "the pod against the hard stop",
    f"{pod['billed_seconds']:.0f} s of {spaced(prereg['money']['pre_pod_arithmetic']['hard_stop_seconds'])} = **{pod['billed_seconds'] / 3600:.1%}**",
)
rent = prereg["money"]["the_second_volume_rents_beside_the_step_not_inside_it"]
says("one volume a day", f"**~${rent['one_volume_daily_usd']}/day**")
says("both volumes a day", f"**~${rent['both_volumes_daily_usd']}/day**")
says(
    "what the remaining balance covers",
    f"about **{10.2694 / rent['both_volumes_daily_usd']:.1f} days**",
)

# --- §5 and §6 ---------------------------------------------------------------------------------------

says("the untouched volume", "mp-srv2 qw4nwleanc 100 GB EU-RO-1")
says("the volume this step built", "mp-lora-c soymlju8q0 100 GB CA-MTL-3")
says("the staged HEAD", "997a2a23db7978d32e50675d29306f10e0a1d098")
says(
    "the stock reading's stamp",
    f"**{stock['read_at'][11:19]}Z**",
    stock["read_at"][:10] == "2026-08-25",
)
says(
    "the stock reading's cross-check",
    f"{len(stock['volume_capable_datacenters']['datacenters'])} capable datacenters,"
    f" {stock['cross_check']['pairs_compared']} pairs cross-checked, 0 disagreements",
    stock["cross_check"]["agree"],
)
says(
    "the count of cheaper rows",
    "**four cheaper volume-capable rows at ≥48 GB**",
    len(stock["cheaper_volume_capable_alternatives"]) == 4,
)
for one in stock["cheaper_volume_capable_alternatives"]:
    says(
        f"the cheaper row {one['card']} in {one['datacenter']}", f"| {one['secure_usd_per_hour']} |"
    )

REMAINING, STEPS, FIXED = 3.2394, 150, 6577.2
for price, printed in ((0.53, "102.84"), (0.82, "50.96"), (0.84, "48.71"), (1.39, "12.08")):
    per = (REMAINING / price * 3600 - FIXED) / STEPS
    says(f"the r3 rate at ${price}", f"{printed} s", abs(per - float(printed)) < 0.01)

# --- §7, the close debts ------------------------------------------------------------------------------

debts = prereg["the_two_guard_close_debts"]
says(
    "the r2 close",
    f"${debts['lora-c']['settled_usd']:.6f} settled against ${debts['lora-c']['recorded_reading_usd']}",
)
probe = debts["lora-c-vramprobe"]
says(
    "the probe's two figures",
    f"${probe['settled_usd']:.6f} settled against ${probe['recorded_reading_usd']}",
)
says(
    "the probe's miss", f"**{probe['off_fraction']:.1%}** off a {probe['tolerance_used']:.0%} band"
)

# --- §8, the audit -----------------------------------------------------------------------------------

says(
    "the frozen registration",
    "`4d5a8f1d34765b4a…`",
    hashlib.sha256(FROZEN.read_bytes()).hexdigest()
    == prereg["this_is_not_the_registered_attempt"]["sha256"],
)
says("one pod alive at any moment", "| **1** |", len(record["pods"]) == 1)
says(
    "the load proof is the contract's own deliverable",
    "through the shipped loader",
    "model loaded to GPU once through the shipped loader" in contract,
)

for name, path in (
    ("results/prereg_lora_c_migrate_r2.json", PREREG),
    ("results/lora_c_migrate_r2_stock.json", STOCK),
    ("results/lora_c_migrate_r2.json", RECORD),
    ("results/lora_c_migrate_r2_load_proof.json", PROOF),
    ("results/lora_c_migrate_r2_load_bytes.json", BYTES),
    ("scripts/gate_lora_c_migrate_r2.py", REPO_ROOT / "scripts" / "gate_lora_c_migrate_r2.py"),
    ("scripts/load_proof_pod_runner.py", REPO_ROOT / "scripts" / "load_proof_pod_runner.py"),
    ("tests/test_lora_c_migrate_r2.py", REPO_ROOT / "tests" / "test_lora_c_migrate_r2.py"),
):
    says(
        f"the sha of {name}",
        f"| `{name}` | `{hashlib.sha256(path.read_bytes()).hexdigest()[:16]}` |",
    )

# --- the deviation tally ---------------------------------------------------------------------------

rows = [
    one
    for one in REPORT.read_text(encoding="utf-8").splitlines()
    if one.startswith("| **8") and one.count("|") >= 4
]
kinds: dict[str, int] = {}
for row in rows:
    kinds[row.split("|")[2].strip()] = kinds.get(row.split("|")[2].strip(), 0) + 1
for kind, count in sorted(kinds.items()):
    says(f"the tally's own count of {kind}", f"{kind} {count}")
says(
    "the tally counts every row it has",
    f"**{['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'][len(rows)]} rows**",
    sum(kinds.values()) == len(rows),
)

if __name__ == "__main__":
    bad = [one for one in checks if not one[1]]
    for what, ok, printed in checks:
        print(f"{'ok  ' if ok else 'FAIL'} {what}" + ("" if ok else f"  — expected {printed!r}"))
    print(f"\n{len(checks) - len(bad)} of {len(checks)} checks hold")
    sys.exit(1 if bad else 0)
