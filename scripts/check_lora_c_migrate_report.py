#!/usr/bin/env python3
"""Every number in `docs/reports/lora-c-migrate.md`, re-derived from the file that owns it.

A report is prose until something re-computes it. Each check below pairs a value derived from a
record with the string the report prints, and BOTH must hold: a derivation that no longer matches
the page is a stale report, and a page whose string is absent is a number that moved without
anyone noticing ([[rederive_doc_numbers]], [[a_count_in_prose_is_not_the_enumeration]]).

The two shas the report prints for its own producer and for itself are NOT checked here — a file
cannot hash itself into its own body ([[provenance_cannot_name_itself]]). They are stamped after
the suite runs, by hand, and the closing stamped reading is what witnesses them.

    python3.11 scripts/check_lora_c_migrate_report.py
"""

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "lora-c-migrate.md"
STOCK = REPO_ROOT / "results" / "lora_c_migrate_stock.json"
PREREG = REPO_ROOT / "results" / "prereg_lora_c_migrate.json"
FROZEN = REPO_ROOT / "results" / "prereg_lora_c.json"
LEDGER_C = REPO_ROOT / "results" / "spend_lora_c.json"
CONTRACT = REPO_ROOT / "docs" / "PROMPT-lora-c-migrate.md"


def nbsp(text: str) -> str:
    """The page and a derived string, made comparable.

    Three normalisations, each for a mismatch this checker actually hit: the report writes
    thousands with a thin space, it writes a minus as U+2212, and Markdown wraps a sentence
    wherever the line ran out — so a quotation the source wraps is found nowhere and reads as
    «absent» ([[verbatim_quotes_must_be_grepped]])."""
    for one in ("\u2009", "\u202f", "\u00a0"):
        text = text.replace(one, " ")
    return " ".join(text.replace("\u2212", "-").split())


PAGE = nbsp(REPORT.read_text(encoding="utf-8"))
stock = json.loads(STOCK.read_text(encoding="utf-8"))
prereg = json.loads(PREREG.read_text(encoding="utf-8"))
ledger = json.loads(LEDGER_C.read_text(encoding="utf-8"))

checks: list[tuple[str, bool, str]] = []


def says(what: str, printed: str, derived=True) -> None:
    """`printed` must appear on the page, and `derived` must be true of the record."""
    checks.append((what, bool(derived) and nbsp(printed) in PAGE, printed))


def spaced(number: float | int, digits: int = 0) -> str:
    """`3803927` as the report writes it: `3 803 927`."""
    body = f"{number:,.{digits}f}".replace(",", " ")
    return body


# --- §1, the refusal and the card ----------------------------------------------------------------

capable = stock["volume_capable_datacenters"]["datacenters"]
says(
    "the count of volume-capable datacenters",
    f"**{len(capable)} datacenters.**",
    len(capable) == 21,
)
says(
    "the refusal message, verbatim",
    stock["volume_capable_datacenters"]["message"].split("Available data centers: ")[1][:40],
)
says(
    "the ruling's datacenter is not among them",
    "EU-SE-1 is absent",
    "EU-SE-1" not in capable,
)
NAMED_BY_SECTION_5 = ("EU-SE-1", "US-TX-1", "EUR-IS-2", "US-PA-1")
"""Every datacenter `docs/reports/lora-c-vramprobe.md` §5 offered for a 48 GB card. Dv821 counts
them, and a count in prose is not the enumeration ([[a_count_in_prose_is_not_the_enumeration]])."""
missing = [one for one in NAMED_BY_SECTION_5 if one not in capable]
for absent in NAMED_BY_SECTION_5[1:]:
    says(f"{absent} is not volume-capable either", absent, absent not in capable)
says(
    "Dv821 counts every datacenter §5 named",
    f"**all {['zero', 'one', 'two', 'three', 'four'][len(missing)]}** datacenters §5 named",
    len(missing) == len(NAMED_BY_SECTION_5),
)

says("the reading's own timestamp", stock["read_at"], True)

a6000 = {one["datacenter"]: one for one in stock["the_rulings_card"]["datacenters"]}
says("the A6000's price", f"RTX A6000 48 GB, ${stock['the_rulings_card']['secure_usd_per_hour']}/h")
says(
    "A6000 in EU-SE-1 is Low and volume-less",
    "| EU-SE-1 — **the ruling's** | `Low` | **no** |",
    a6000["EU-SE-1"]["stock"] == "Low" and not a6000["EU-SE-1"]["takes_a_network_volume"],
)
says(
    "A6000 in EU-RO-1 is none and volume-capable",
    "| EU-RO-1 — **the existing volume's** | `none` | yes |",
    a6000["EU-RO-1"]["stock"] == "none" and a6000["EU-RO-1"]["takes_a_network_volume"],
)
says(
    "the card is obtainable nowhere a volume can live",
    "in any datacenter that can",
    stock["the_rulings_card"]["in_stock_and_volume_capable"] == [],
)

cross = stock["cross_check"]
says("the cross-check", f"**{cross['pairs_compared']} pairs, 0 disagreements.**", cross["agree"])
says("the listing did not move", "byte-identical in the record", stock["the_listing_did_not_move"])
says(
    "one volume, and it is mp-srv2",
    "**one volume**, `mp-srv2`",
    [one["name"] for one in stock["network_volume_list_after"]] == ["mp-srv2"],
)

# --- §2, the rungs -------------------------------------------------------------------------------

rungs = {one["rung"]: one for one in prereg["registered_as_the_contract_wrote_it"]["kill_clock"]}
says("rung 1's threshold", f"| 1 | the boot gate | {spaced(rungs[1]['threshold'])} s |")
says(
    "rung 2's two thresholds",
    f"| 2 | the download deadline | {spaced(rungs[2]['threshold'])} s,"
    f" liveness {spaced(rungs[2]['liveness_seconds'])} s |",
)
says("rung 3's threshold", f"| 3 | the model-load proof | {spaced(rungs[3]['threshold'])} s |")
says("rung 6's threshold", f"| 6 | the platform backstop | {spaced(rungs[6]['threshold'])} s |")

# --- §3, the four findings -----------------------------------------------------------------------

found = prereg["arithmetic_found_before_the_money"]
hard = found["the_hard_stop_must_be_an_INEQUALITY_not_an_equality"]
buys = hard["cap_usd_all_in"] / hard["price_usd_per_hour"] * 3600
says(
    "what the cap buys at $0.53",
    f"**{spaced(buys, 2)} s**",
    round(buys, 2) == hard["seconds_the_cap_buys"],
)
says("against the registered hard stop", f"**{spaced(hard['hard_stop_seconds'])} s**")
says("the vramprobe's own coincidence", "1 500.0 exactly")
legs = hard["what_the_cap_is_actually_spent_on"]
says(
    "the cap's two legs",
    f"**${legs['the_pod_at_the_hard_stop']:.2f} of pod at the hard stop + ~${legs['the_new_volumes_first_day']:.2f}",
    round(legs["the_pod_at_the_hard_stop"] + legs["the_new_volumes_first_day"], 2) == legs["total"],
)
says(
    "the hard stop as a fraction of what the cap buys",
    f"{spaced(hard['hard_stop_seconds'])} s is {legs['hard_stop_as_a_fraction_of_what_the_cap_buys']:.1%}",
    round(hard["hard_stop_seconds"] / buys, 2)
    == legs["hard_stop_as_a_fraction_of_what_the_cap_buys"],
)

clock = found["the_four_deadlines_are_jointly_unreachable_at_their_bounds"]
summed = rungs[1]["threshold"] + rungs[2]["threshold"] + rungs[3]["threshold"]
says(
    "the three deadlines summed",
    f"boot {spaced(rungs[1]['threshold'])} + download {spaced(rungs[2]['threshold'])}"
    f" + load proof {spaced(rungs[3]['threshold'])} = **{spaced(summed)} s**",
)
says(
    "what is left inside the hard stop",
    f"leaving **{spaced(clock['left_for_everything_else_seconds'])} s**",
    rungs[6]["threshold"] - summed == clock["left_for_everything_else_seconds"],
)

# --- §4, the money -------------------------------------------------------------------------------

closed = ledger["gpu_sessions"][-1]
debts = prereg["the_two_guard_close_debts"]
says(
    "the tolerance and where it comes from",
    f"(`{debts['tolerance_used']:.2f}`, `scripts/runbook_lora_c.md`",
    debts["tolerance_used"] == 0.07,
)
says(
    "r2 settled",
    f"| **CLOSED** | ${closed['settled_usd']:.6f} |",
    closed["settled_usd"] == debts["lora-c"]["settled_usd"],
)
says(
    "r2's recorded reading",
    f"| ${closed['recorded_reading_usd']:.4f} |",
    closed["recorded_reading_usd"] == debts["lora-c"]["recorded_reading_usd"],
)
says(
    "r2's walk against the run record",
    f"{spaced(closed['walk_ms'])} ms against the run record's {spaced(closed['expected_ms'])}",
    abs(closed["walk_ms"] - closed["expected_ms"]) / closed["expected_ms"] < 0.01,
)

probe = debts["lora-c-vramprobe"]
says("the probe's settled figure", f"${probe['settled_usd']:.6f} settled")
says("the probe's recorded reading", f"${probe['recorded_reading_usd']:.4f} is a")
says(
    "the probe's miss",
    f"{probe['off_fraction']:.1%}",
    round(
        abs(probe["settled_usd"] - probe["recorded_reading_usd"]) / probe["recorded_reading_usd"], 5
    )
    == round(probe["off_fraction"], 5),
)

lag = debts["a_relative_tolerance_is_unreachable_on_a_cheap_step"]
lag_r2 = round(debts["lora-c"]["settled_usd"] - debts["lora-c"]["recorded_reading_usd"], 6)
lag_probe = round(probe["settled_usd"] - probe["recorded_reading_usd"], 6)
says(
    "the two absolute lags",
    f"**${lag_r2:.6f}** on r2 and **${lag_probe:.6f}** on the probe",
    lag["n"] == 2,
)
says(
    "the reachability band the lags imply",
    f"roughly **${lag_probe / debts['tolerance_used']:.2f} to ${lag_r2 / debts['tolerance_used']:.2f}**",
)

# --- §5, the operator's table ---------------------------------------------------------------------

table = prereg["what_the_remaining_r2_cap_buys_at_each_obtainable_price"]
says(
    "the count of obtainable 48 GB+ cards",
    f"**{stock['candidate_count']}** cards of 48 GB or more",
    stock["candidate_count"] == len(stock["candidates"]),
)
cheapest = stock["candidates"][0]
says(
    "the cheapest obtainable card",
    f"| {cheapest['card']} | **${cheapest['secure_usd_per_hour']}** | {cheapest['vram_gb']} |"
    f" {cheapest['datacenter']} | `{cheapest['stock']}` |",
)
in_euro1 = sorted(
    (one for one in stock["candidates"] if one["datacenter"] == "EU-RO-1"),
    key=lambda one: one["secure_usd_per_hour"],
)
says(
    "EU-RO-1's own cheapest 48 GB+ card in stock",
    f"**RTX PRO 6000 96 GB at ${in_euro1[0]['secure_usd_per_hour']}/h** in stock today",
    in_euro1[0]["card"] == "RTX PRO 6000" and in_euro1[0]["vram_gb"] == 96,
)

says(
    "the remaining r2 cap",
    f"= **${table['remaining_r2_cap_usd']}**",
    round(4.00 - 0.7606, 4) == table["remaining_r2_cap_usd"],
)
says("the step count", f"{table['steps']} optimizer steps")
says(
    "the charged rate",
    f"**{table['the_charge_is_9.20_by_ruling'].split('ИЗМЕРЕННЫМИ ')[1][:4]} s/call**",
)
for price, row in table["at_each_price"].items():
    seconds = table["remaining_r2_cap_usd"] / float(price) * 3600
    ok = (
        round(seconds, 1) == row["seconds"]
        and round((seconds - table["fixed_seconds_cheapest"]) / table["steps"], 2)
        == row["seconds_per_step_cheapest"]
    )
    cheap = row["seconds_per_step_cheapest"]
    printed = f"| {spaced(seconds, 1)} | " + (
        f"**{cheap:.2f}**" if price in ("0.53", "2.09") else f"{cheap:.2f}"
    )
    says(f"the r3 table at ${price}", printed, ok)
says("the fixed part, cheapest", f"fixed {spaced(table['fixed_seconds_cheapest'], 1)}")
says("the fixed part, richest", f"fixed {spaced(table['fixed_seconds_richest'], 1)}")
says("lora-b's measured rate", f"**{table['the_only_step_rate_this_repo_has_measured']} s/step**")

bound = table["the_conclusion_survives_a_faster_card"]
says(
    "the faster-card bound",
    f"still leaves **{bound['seconds_per_step_at_2.09_under_that_bound']} s/step**",
)

# --- §6, the audit --------------------------------------------------------------------------------

says(
    "the frozen registration's sha",
    f"sha `{hashlib.sha256(FROZEN.read_bytes()).hexdigest()[:16]}`",
    hashlib.sha256(FROZEN.read_bytes()).hexdigest()
    == prereg["this_is_not_the_registered_attempt"]["sha256"],
)
says(
    "the volume that was not touched",
    "`qw4nwleanc`, 100 GB, EU-RO-1",
    stock["network_volume_list_after"][0]["id"] == "qw4nwleanc",
)
says("nothing was billed", "**$0.0000** of $1.00")

for name, path in (
    ("results/lora_c_migrate_stock.json", STOCK),
    ("results/prereg_lora_c_migrate.json", PREREG),
    (
        "scripts/probe_lora_c_migrate_stock.py",
        REPO_ROOT / "scripts" / "probe_lora_c_migrate_stock.py",
    ),
    ("tests/test_lora_c_migrate.py", REPO_ROOT / "tests" / "test_lora_c_migrate.py"),
    # this file's own sha is a stable fixpoint — editing it invalidates the report, and fixing the
    # report does not edit it back. Only the REPORT's own sha cannot be checked from inside it.
    ("scripts/check_lora_c_migrate_report.py", Path(__file__).resolve()),
):
    says(
        f"the sha of {name}",
        f"| `{name}` | `{hashlib.sha256(path.read_bytes()).hexdigest()[:16]}` |",
    )

# --- the deviation tally --------------------------------------------------------------------------

rows = [
    one
    for one in REPORT.read_text(encoding="utf-8").splitlines()
    if one.startswith("| **8") and one.count("|") >= 4
]
kinds: dict[str, int] = {}
for row in rows:
    kind = row.split("|")[2].strip()
    kinds[kind] = kinds.get(kind, 0) + 1
for kind, count in sorted(kinds.items()):
    says(f"the tally's own count of {kind}", f"{kind} {count}")
says(
    "the tally counts every row it has",
    "eight, against eight rows",
    len(rows) == sum(kinds.values()) == 8,
)

# --- the contract's own words ---------------------------------------------------------------------

contract = " ".join(CONTRACT.read_text(encoding="utf-8").split())
says(
    "the load proof is the contract's own deliverable",
    "a volume nobody loaded from is a hope",
    "a volume nobody loaded from is a hope" in contract,
)


bad = [one for one in checks if not one[1]]
for what, ok, printed in checks:
    print(f"{'ok  ' if ok else 'FAIL'} {what}" + ("" if ok else f"  — expected {printed!r}"))
print(f"\n{len(checks) - len(bad)} of {len(checks)} checks hold")
sys.exit(1 if bad else 0)
