#!/usr/bin/env python3
"""What the census's window costs, per leg, from PAID serverless measurements. ($0, offline.)

SPEC amendment 3.18 (4): the window is "priced from the most recent measurement that actually PAID
on the serverless runtime", and it names the two numbers that may not be used — "5b's 0.5993 per
1,000 rows and 0.4611 per pass were measured on a POD and are not this runtime's numbers". Both of
those live in `results/srv2d_cost.json :: pod_comparison`, and they appear below exactly once, in a
block that says so.

Every number in the record is READ OUT of the file it cites, by the dotted path the record prints.
Nothing is typed: `cite()` is the only way a figure enters this file, so a source that moved cannot
leave a stale copy behind, and `tests/test_projection_5c2.py` re-resolves every one of them.

Two legs, two paid sessions, and they are not the same endpoint:

* the COMMENT leg is srv-2d — `results/spend_srv2d.json`, 758 rows scored on the serverless
  endpoint `hbq25reui1tpj6`, and `results/srv2d_cost.json` is that session's own cost record.
* the POSITIONS leg is skub2-run — `results/spend_skub2.json`, one serverless session, and its
  page marginal is the in-run gate's own reading at the end of the page leg.

Two endpoints means TWO boots and two idle tails when both legs run, and that is how the caps
below are priced. Seconds are carried beside dollars in every row: a cap that fits in dollars can
still name a session the transport cannot run in one sitting, and the job count at the endpoint's
own execution timeout is what makes that visible.

    PYTHONPATH=src python3 scripts/projection_5c2.py
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import positions_gm4_skub as driver  # noqa: E402
import runpod_guard as guard  # noqa: E402

RATE = REPO_ROOT / "results" / "srv2d_cost.json"
SKUB2 = REPO_ROOT / "results" / "sku_b_positions_skub2.json"
SMOKE = REPO_ROOT / "results" / "serving_srv2d_smoke.json"
PARITY = REPO_ROOT / "results" / "parity_srv2.json"
SPEND_SRV2D = REPO_ROOT / "results" / "spend_srv2d.json"
SPEND_SKUB2 = REPO_ROOT / "results" / "spend_skub2.json"
LEDGER = REPO_ROOT / "results" / "spend_phase4.json"
CENSUS = REPO_ROOT / "results" / "census_5c2.json"
SKUB2_REPORT = REPO_ROOT / "docs" / "reports" / "skub2-run.md"
RECORD = REPO_ROOT / "results" / "projection_5c2.json"

DRIFT = 0.03
"""Carried from `write_sku_projection_v4.DRIFT` and `write_sku_projection_b2.DRIFT`, where it is
already documented as a CONTRACT TERM and not a measurement: nothing in this repo has measured how
far a serverless worker's seconds drift between two runs of the same job. Applied to the whole
billed second count, which is the conservative reading — what it stands in for is the endpoint
being slower on the day, not one leg being mis-priced."""

CANDIDATE_CAPS = (0.25, 2.00, 6.00)
"""Three caps to price, chosen to bracket the decision rather than to recommend one: the leaflet
leg alone, a middle session, and one just inside the remaining phase budget. The operator rules the
cap at the STOP; this file only says what each buys."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dig(data, dotted: str):
    """`a.b[-1].c` → the value. The one resolver, so the record's `source` string is executable.

    A field named in prose is a claim; a field named in a path something walks is a check. The test
    re-implements this in six lines and compares — two readers, one string.
    """
    for step in re.findall(r"[^.\[\]]+|\[-?\d+\]", dotted):
        data = data[int(step[1:-1])] if step.startswith("[") else data[step]
    return data


def cite(path: Path, dotted: str, why: str) -> dict:
    """A number, where it came from, and why it is the one to use. Never a typed literal."""
    return {"value": dig(load(path), dotted), "source": f"{rel(path)} :: {dotted}", "why": why}


def quote_line(path: Path, needle: str, why: str) -> dict:
    """A line of a report, verbatim, with the file that holds it. One line, or a refusal.

    Ambiguity is the failure this refuses. A loose needle («page leg») matches the packing line and
    the marginal line in the same report, takes the first, and the record then prints a true quote
    that says nothing about the number beside it — caught here by printing the citations and
    reading them, which is the only reason it is not still in the file.
    """
    lines = [
        line.strip() for line in path.read_text(encoding="utf-8").splitlines() if needle in line
    ]
    if len(lines) != 1:
        raise SystemExit(
            f"{rel(path)} has {len(lines)} lines containing {needle!r} — a quote is one line"
        )
    return {"quote": lines[0], "source": rel(path), "why": why}


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def producer() -> dict:
    """Which code wrote this, by its own sha — and NOT `git_state`, deliberately.

    Every other record in this repo carries a `git` block, and this one may not: that block holds
    `git status --porcelain`, so the artifact's bytes change when an unrelated file is committed
    or edited. The contract makes byte-identity this record's own gate, and a provenance field that
    moves with the working tree would void it on the first commit after the record was written —
    which is exactly what happened here once before this line existed. The script's sha is the
    stronger answer anyway: a commit id does not say the file was not dirty when it ran.
    """
    return {
        "script": rel(Path(__file__)),
        "sha256": sha256_of(Path(__file__)),
        "why": "no git block: `git status --porcelain` is a fact about the tree, not the measurement",
    }


def cost(seconds: float, rate: float) -> dict:
    """Seconds beside dollars, always. A cap is a dollar bound and a session is a wall-clock one."""
    return {
        "billed_seconds": round(seconds, 1),
        "hours": round(seconds / 3600, 2),
        "usd": round(seconds * rate, 4),
        "usd_with_drift": round(seconds * rate * (1 + DRIFT), 4),
        "jobs_at_the_execution_timeout": -(-int(seconds) // int(driver.JOB_TIMEOUT_S)),
    }


def comment_leg(rate: float, rows: int) -> dict:
    """The comment leg, priced two ways from ONE paid session, because the two disagree by 9%."""
    unit = cite(
        RATE,
        "measured.usd_per_1000_rows",
        "srv-2d's whole parity pass over 758 rows on the serverless endpoint, its own boot"
        " amortised INSIDE it. The conservative corner: nothing else has to be added to it",
    )
    marginal = cite(
        RATE,
        "measured.like_for_like_seconds_per_row",
        "the same session's per-row seconds with the cold start taken out — the corner a boot is"
        " added to. It is the one that answers «how many more rows fit under this cap»",
    )
    boot = cite(
        RATE,
        "inputs.cold_start_seconds_measured_on_this_endpoint",
        "one cold start on that endpoint, paid once per session before any row is scored",
    )
    fixed = boot["value"] + driver.IDLE_TAIL_SECONDS
    return {
        "leg": "comment",
        "task": "T1 with the parent post — market_pulse.loop.COMMENT_TASK",
        "paid_measurement": {
            "session": "srv-2d, 2026-08-08",
            "runtime": "serverless (RunPod endpoint hbq25reui1tpj6)",
            "ledger": {
                "path": rel(SPEND_SRV2D),
                "smoke_usd": dig(load(SPEND_SRV2D), "gpu_sessions[1].step_spent_usd"),
                "parity_usd": dig(load(SPEND_SRV2D), "gpu_sessions[2].step_spent_usd"),
                "why": (
                    "cumulative against that session's own anchor, so the parity step is the"
                    " difference — and it is an ACCOUNT delta, not a per-leg price. The per-leg"
                    " figures below come from srv2d_cost.json, which applies the settled rate to"
                    " measured seconds and agrees with the account to about 1%"
                ),
            },
            "rows_scored": cite(
                PARITY,
                "diagnostics.failures[0].rows",
                "the comment half of the 758: 400 comments_test rows, 0 parse and 0 api failures",
            ),
            "composition": {
                "comments_test": dig(load(PARITY), "diagnostics.failures[0].rows"),
                "posts_test": dig(load(PARITY), "diagnostics.failures[1].rows"),
                "sarcasm_holdout": dig(load(PARITY), "diagnostics.failures[2].rows"),
                "why": (
                    "the unit cost is BLENDED across those three and this window is pure T1."
                    " Direction of the error, from the smoke's own per-row seconds,"
                    " results/serving_srv2d_smoke.json :: rows[*].worker_seconds — T1"
                    " 5.176/4.319/4.368/4.408 against T2 3.978/3.903/3.991/3.958, n=4 each — the"
                    " comment task is the SLOWER of the two, so a blended rate under-prices a"
                    " pure-comment window rather than over-pricing it"
                ),
            },
            "floor": dig(load(RATE), "caveat_dv33"),
        },
        "window_rows": rows,
        "corners": {
            "unit_cost": {
                **unit,
                **cost(rows * unit["value"] / 1000 / rate + driver.IDLE_TAIL_SECONDS, rate),
                "note": "the boot is already inside the unit cost; only the idle tail is added",
                "seconds_are": (
                    "IMPLIED — the dollars divided by the settled rate, not a measured wall clock."
                    " The marginal corner below is the one whose seconds were counted"
                ),
            },
            "marginal_plus_boot": {
                **marginal,
                "boot": boot,
                "idle_tail_seconds": driver.IDLE_TAIL_SECONDS,
                **cost(rows * marginal["value"] + fixed, rate),
                "seconds_are": "MEASURED per-row seconds plus that endpoint's measured cold start",
            },
        },
        "fixed_seconds": fixed,
        "seconds_per_row": marginal["value"],
    }


def leaflet_leg(rate: float, pages: int) -> dict:
    """The positions leg, from the one serverless session that has ever bought leaflet pages."""
    marginal = cite(
        SKUB2,
        "projection.per_gate[-1].marginal_seconds_per_call",
        "the LAST in-run gate of the skub2 session, taken when 108 of the 138 sources were done"
        " and every one of them was a page — so this is the page leg's own marginal, and it is the"
        " number the cap stop itself acted on",
    )
    boot = cite(SKUB2, "projection.boot_seconds", "that session's cold start, paid once")
    warmup = cite(
        SKUB2,
        "projection.warmup_seconds",
        "the two non-gold calls SPEC 3.17 (9) requires before either leg touches gold",
    )
    fixed = boot["value"] + warmup["value"] + driver.IDLE_TAIL_SECONDS
    return {
        "leg": "leaflet_page",
        "task": "positions_post_gm4, one page per call — SPEC 3.17 (4)",
        "paid_measurement": {
            "session": "skub2-run, 2026-08-12",
            "runtime": "serverless (the POSITIONS endpoint of SPEC 3.17)",
            "ledger": {
                "path": rel(SPEND_SKUB2),
                "usd": dig(load(SPEND_SKUB2), "runs[0].step_spent_usd"),
                "why": "the whole session against its own anchor: 138 sources, cap $0.65",
            },
            "population": {
                "pages_sent": dig(load(SKUB2), "population.pages_sent"),
                "text_rows": dig(load(SKUB2), "population.text_rows"),
                "asked": dig(load(SKUB2), "population.asked"),
                "why": (
                    "the contract's briefing says the session «bought 138 pages»; the record says"
                    " 138 SOURCES — 108 pages and 30 text rows. The page marginal below is"
                    " measured over the 108, which is what per_gate[-1].calls_done counts"
                ),
            },
            "report_line": quote_line(
                SKUB2_REPORT,
                "462.173",
                "the same arithmetic in that session's own report: (711.102 - 248.929) / 108 ="
                " 4.2794, which is the field cited above, and $0.1417 is what those pages cost",
            ),
        },
        "window_pages": pages,
        "corners": {
            "marginal_plus_boot": {
                **marginal,
                "boot": boot,
                "warmup": warmup,
                "idle_tail_seconds": driver.IDLE_TAIL_SECONDS,
                **cost(pages * marginal["value"] + fixed, rate),
            }
        },
        "fixed_seconds": fixed,
        "seconds_per_page": marginal["value"],
    }


def budget() -> dict:
    """The remaining phase budget, read off the ledger and the guard — never restated from memory.

    The LAST LOGGED reading, and it says so: the guard's live number needs a balance call to RunPod
    and this contract makes none. Nothing has been billed since that entry — 5c2-prep-b, -c1 and
    this session are all $0 — so the logged remainder is still the remainder, and a reader who
    doubts it can run the guard.
    """
    last = dig(load(LEDGER), "sessions[-1]")
    return {
        "phase_cap_usd": guard.PHASE_CAP_USD,
        "cap_source": "scripts/runpod_guard.py :: PHASE_CAP_USD (the line that ENFORCES it)",
        "spent_usd": last["spent_usd"],
        "remaining_usd": last["remaining_usd"],
        "read_at": last["at"],
        "source": f"{rel(LEDGER)} :: sessions[-1]",
        "note": last["note"],
        "ledger_cap_usd": dig(load(LEDGER), "phase4_cap_usd"),
    }


def cap_row(cap: float, comment: dict, leaflet: dict, rate: float, remaining: float) -> dict:
    """What one candidate cap buys: the whole leaflet leg first, then comments with what is left.

    The leaflet leg goes first because it is small, bounded and complete — 78 pages is the whole
    window — while the comment leg is divisible and does not have to finish. That is an ARITHMETIC
    order, not a ruling: the operator may spend the cap the other way round and the rows-per-dollar
    below are what that decision is made on.
    """
    seconds_budget = cap / (1 + DRIFT) / rate
    leaflet_seconds = (
        leaflet["window_pages"] * leaflet["seconds_per_page"] + leaflet["fixed_seconds"]
    )
    fits_leaflet = leaflet_seconds <= seconds_budget
    left = seconds_budget - (leaflet_seconds if fits_leaflet else 0)
    marginal_rows = max(0, int((left - comment["fixed_seconds"]) // comment["seconds_per_row"]))
    unit = comment["corners"]["unit_cost"]["value"] / 1000
    conservative_rows = max(
        0,
        int(
            ((left - driver.IDLE_TAIL_SECONDS) * rate) // unit
            if left > driver.IDLE_TAIL_SECONDS
            else 0
        ),
    )
    rows = min(marginal_rows, conservative_rows)
    seconds = (leaflet_seconds if fits_leaflet else 0) + (
        rows * comment["seconds_per_row"] + comment["fixed_seconds"] if rows else 0
    )
    # The row count was solved for at the CONSERVATIVE rate, so the dollars that bind are the
    # conservative ones and the wall clock is the marginal model's — the only one with measured
    # seconds in it. Printing one number from each model in a single field is how a row ends up
    # with two denominators, so each says which rate it came from.
    conservative_usd = (
        (leaflet_seconds if fits_leaflet else 0) * rate
        + rows * unit
        + (driver.IDLE_TAIL_SECONDS * rate if rows else 0)
    ) * (1 + DRIFT)
    return {
        "cap_usd": cap,
        "fits_in_the_remaining_budget": cap <= remaining,
        "buys": {
            "leaflet_pages": leaflet["window_pages"] if fits_leaflet else 0,
            "comments_conservative": rows,
            "comments_optimistic": marginal_rows,
            "why": (
                "conservative uses the unit cost (srv-2d's boot inside it), optimistic the marginal"
                " plus one boot. The two rates differ by 9% and neither is settled — the account"
                " reading behind both is a FLOOR (Dv33)"
            ),
        },
        "share_of_the_comment_window": round(rows / comment["window_rows"], 4)
        if comment["window_rows"]
        else 0.0,
        "at_the_conservative_rate": {
            "usd_with_drift": round(conservative_usd, 4),
            "why": "what the cap was solved against — this is the number that must stay under it",
        },
        "at_the_marginal_rate": {
            **cost(seconds, rate),
            "why": "the same rows on measured seconds: the wall clock and the job count",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    rate = cite(
        RATE,
        "rate.usd_per_second",
        "the settled serverless rate: five endpoints billed on 2026-08-08 read within 1% of it."
        " Every projection in this repo since sku-b has used this one field",
    )
    census = load(CENSUS)
    comment = comment_leg(rate["value"], dig(census, "totals.comments_unanswered_in_window"))
    leaflet = leaflet_leg(rate["value"], dig(census, "totals.leaflet_pages_in_window"))
    money = budget()
    whole = (
        comment["corners"]["unit_cost"]["usd_with_drift"]
        + leaflet["corners"]["marginal_plus_boot"]["usd_with_drift"]
    )

    record = {
        "phase": "5c2-prep-c2 — the projection",
        "contract": "docs/PROMPT-5c2-prep-c2.md deliverable 2; docs/SPEC.md amendment 3.18 (4)",
        "asks": "what the census's window costs per leg, from measurements that actually paid",
        "window": {
            "path": rel(CENSUS),
            "sha256": sha256_of(CENSUS),
            "anchor": dig(census, "anchor.anchor"),
            "since": dig(census, "anchor.since"),
            "comments_unanswered": comment["window_rows"],
            "leaflet_pages": leaflet["window_pages"],
            "why": "row counts, never a date range evaluated at run time (SPEC 3.18 (4))",
        },
        "rate": rate,
        "drift": {
            "factor": DRIFT,
            "source": "scripts/write_sku_projection_v4.py :: DRIFT, carried unchanged",
            "why": "a contract term, not a measurement, applied to the whole billed second count",
        },
        "job_shape": {
            "execution_timeout_s": driver.JOB_TIMEOUT_S,
            "ttl_s": driver.JOB_TTL_S,
            "idle_tail_s": driver.IDLE_TAIL_SECONDS,
            "workers_max": dig(load(SMOKE), "deployment.endpoint.workersMax"),
            "source": (
                "scripts/positions_gm4_skub.py :: JOB_TIMEOUT_S / JOB_TTL_S / IDLE_TAIL_SECONDS;"
                f" {rel(SMOKE)} :: deployment.endpoint.workersMax"
            ),
            "why": (
                "a cap is a bound in DOLLARS and a session is also a bound in wall clock. One"
                " worker at a 900 s execution timeout means the seconds below are serial and the"
                " job count is what a session has to be packed into — SPEC 3.17 (10)(c) is the"
                " rule that no single job may be capable of billing past the remaining cap"
            ),
        },
        "legs": {"comment": comment, "leaflet_page": leaflet},
        "whole_window": {
            "usd_with_drift": round(whole, 4),
            "usd_source": "the CONSERVATIVE corner of each leg, summed",
            "billed_seconds": round(
                comment["corners"]["marginal_plus_boot"]["billed_seconds"]
                + leaflet["corners"]["marginal_plus_boot"]["billed_seconds"],
                1,
            ),
            "hours": round(
                (
                    comment["corners"]["marginal_plus_boot"]["billed_seconds"]
                    + leaflet["corners"]["marginal_plus_boot"]["billed_seconds"]
                )
                / 3600,
                2,
            ),
            "seconds_source": (
                "the MARGINAL corner of each leg — the only one whose seconds were counted rather"
                " than divided out of a price. Dollars and wall clock come from different corners"
                " on purpose, and each field says which"
            ),
            "remaining_usd": money["remaining_usd"],
            "fits": whole <= money["remaining_usd"],
            "why": (
                "This is the number the window ruling turns on and it is the reason this contract"
                " ends at a STOP: the whole window does not fit in what the phase has left"
            ),
        },
        "caps": [
            cap_row(cap, comment, leaflet, rate["value"], money["remaining_usd"])
            for cap in CANDIDATE_CAPS
        ],
        "budget": money,
        "no_paid_measurement": {
            "legs": [],
            "why": (
                "both legs have one, so no row is marked NO PAID MEASUREMENT. The candidate that"
                " did NOT become a source is named beside it"
            ),
            "candidate_read_and_not_used": {
                "path": rel(PARITY),
                "block": "diagnostics",
                "holds": (
                    "row counts and failure counts — 400 + 250 + 108 rows, 0 parse failures, 0 api"
                    " failures — and `parity.cap_usd` 4.0. It carries no seconds and no dollars"
                ),
                "why": (
                    "a candidate is not a source until its number is on the screen. Its rows are"
                    " used above (they are what the unit cost is per) and its cost is not, because"
                    " it has none: srv2d_cost.json is where that session's price was written"
                ),
            },
        },
        "context_not_a_headline": {
            "pod_usd_per_1000_rows": dig(load(RATE), "pod_comparison.pod_usd_per_1000_rows"),
            "pod_usd_per_pass": dig(load(RATE), "pod_comparison.pod_usd_per_pass"),
            "source": f"{rel(RATE)} :: pod_comparison",
            "amendment": (
                "SPEC 3.18 (4): «5b's 0.5993 per 1,000 rows and 0.4611 per pass were measured on a"
                " POD and are not this runtime's numbers». They are printed here once, labelled,"
                " and they enter no row above"
            ),
            "ratio_serverless_over_pod": dig(
                load(RATE), "pod_comparison.ratio_per_1000_serverless_over_pod"
            ),
        },
        "producer": producer(),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"rate ${rate['value']}/s · drift {DRIFT:.0%} · remaining ${money['remaining_usd']:.4f}")
    for name, found in record["legs"].items():
        corner = found["corners"].get("unit_cost") or found["corners"]["marginal_plus_boot"]
        rows = found.get("window_rows", found.get("window_pages"))
        print(
            f"  {name:<14}{rows:>7} rows  {corner['billed_seconds']:>10.1f} s"
            f"  ${corner['usd_with_drift']:>8.4f} with drift"
        )
    print(
        f"\nwhole window ${record['whole_window']['usd_with_drift']:.4f} with drift"
        f" — fits in ${money['remaining_usd']:.4f}: {record['whole_window']['fits']}"
    )
    header = f"{'cap':>7}{'pages':>8}{'comments':>10}{'$ cons':>9}{'hours':>8}{'jobs':>7}  fits"
    print(f"\n{header}\n{'-' * len(header)}")
    for row in record["caps"]:
        print(
            f"${row['cap_usd']:>6.2f}{row['buys']['leaflet_pages']:>8}"
            f"{row['buys']['comments_conservative']:>10}"
            f"{row['at_the_conservative_rate']['usd_with_drift']:>9.4f}"
            f"{row['at_the_marginal_rate']['hours']:>8.2f}"
            f"{row['at_the_marginal_rate']['jobs_at_the_execution_timeout']:>7}"
            f"  {row['fits_in_the_remaining_budget']}"
        )
    print(f"\nwrote {rel(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
