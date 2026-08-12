#!/usr/bin/env python3
"""Write `results/sku_projection_b2.json` — what the B′ session will cost, against $0.65 ($0).

Deliverable 5 of `docs/PROMPT-skub2-prep.md`, re-stamped by step 5 of `docs/PROMPT-skub2-fix.md`
against the cap SPEC 3.17 (14)(e) sets. Not one corner moved: every rate below was measured before
the cap was, and the arithmetic is the same arithmetic. What changed is the line it is compared to
— (13)(d)'s $0.40, which the dearest corner grazed at $0.4004, against (14)(e)'s $0.65.

Registered BESIDE `results/sku_projection_v4.json`,
which priced a 121-element session at a $0.65 cap from marginals nothing had measured yet. This one
is the first sku-b projection built entirely out of MEASURED seconds: the v4 session completed, and
every rate below is read off its own record.

What is measured, and what is not:

* **measured.** The page marginal (4.0161 s/call at the last in-run gate, n=91), the text marginal
  (2.8177 s/row, n=30, derived from the same record's billed seconds), the idle tail (60 s, the
  driver's own constant, billed on both sessions) and the boot — as a RANGE, because the same
  serving configuration booted in 205.518 s on v4 and 402.586 s on the refused v3 and neither is
  more real than the other.
* **NOT measured, and the reason this file has corners.** Every one of those seconds was billed at
  an 800-token ceiling, and (13)(a) raises it to 1200. A ceiling is not a rate: it binds only the
  replies that reach it, so 4.0161 s/page is a FLOOR at 1200 and not an estimate. The pessimistic
  corner scales every call by 1200/800 — a hard upper bound, since no reply can generate past the
  ceiling — and the optimistic corner leaves the rates alone, which is what happens if the pages
  that hit 800 are the one page v4 recorded as `malformed JSON`.

The population is 138 and not 121: (13)(d) authorises a re-measurement of instrument v2 over the
whole registered set, so the 17 elements the first session bought are re-asked too.

    PYTHONPATH=src python3 scripts/write_sku_projection_b2.py
"""

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import positions_gm4_skub as driver  # noqa: E402
import write_sku_prereg_b2 as b2  # noqa: E402

from market_pulse import local_llm, provenance  # noqa: E402

RATE = REPO_ROOT / "results" / "srv2d_cost.json"
RUN_V4 = REPO_ROOT / "results" / "sku_b_positions_v4.json"
RUN_V3 = REPO_ROOT / "results" / "sku_b_positions_v3.json"
RECORD = REPO_ROOT / "results" / "sku_projection_b2.json"

PAGES = 108
TEXT_ROWS = 30
"""The registered population of SPEC 3.17 (6), whole: 108 sent pages and 30 adjudicated rows. 138."""

DRIFT = 0.03
"""Carried from `write_sku_projection_v4.DRIFT` and it is still a contract term, not a measurement:
nothing here measures how far a serverless worker's seconds drift between two runs of the same job.
Applied to the whole billed second count, because what it stands in for is the endpoint being
slower on the day rather than one leg being mis-priced."""

CEILING_WAS = 800
"""The ceiling every measured second below was billed at — `results/sku_pilot_serving.json`."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def load(path: Path) -> tuple[dict, str]:
    return (
        json.loads(path.read_text(encoding="utf-8")),
        hashlib.sha256(path.read_bytes()).hexdigest(),
    )


def text_marginal(run: dict) -> float:
    """The text leg's seconds per row, derived from the v4 record's own totals.

    The in-run gates report ONE marginal across both legs, and the last of them (n=91) lands while
    only pages have been asked — so the page rate is read off it directly and the text rate is what
    is left when the page leg is subtracted from the billed total. Derived here rather than
    estimated, and the arithmetic is stated because it is the one number in this file that no
    single field of the record holds.
    """
    gates = run["projection"]["per_gate"]
    pages_asked = gates[-1]["calls_done"]
    page_rate = gates[-1]["marginal_seconds_per_call"]
    gold_seconds = run["timing"]["worker_seconds"] - run["projection"]["opened_seconds"]
    rows = run["population"]["text_rows"]
    return round((gold_seconds - pages_asked * page_rate) / rows, 4)


def marginals(v4: dict, v3: dict) -> dict:
    gates = v4["projection"]["per_gate"]
    return {
        "page_seconds_per_call": {
            "value": gates[-1]["marginal_seconds_per_call"],
            "n": gates[-1]["calls_done"],
            "source": f"{rel(RUN_V4)} :: projection.per_gate[-1].marginal_seconds_per_call",
            "what_it_is": (
                "the last in-run gate of the completed v4 session, over 91 leaflet pages of the"
                " registered gold population. This is the number the cap stop itself acted on"
            ),
        },
        "text_seconds_per_row": {
            "value": text_marginal(v4),
            "n": v4["population"]["text_rows"],
            "source": f"{rel(RUN_V4)} :: timing.worker_seconds less the page leg — see text_marginal",
            "what_it_is": (
                "the 30 adjudicated rows, derived from the same record's billed seconds. Short"
                " answers on short inputs: a third of a page's cost and nowhere near any ceiling"
            ),
        },
        "boot_seconds": {
            "low": v4["projection"]["boot_seconds"],
            "high": v3["projection"]["boot_seconds"],
            "source": (
                f"{rel(RUN_V4)} :: projection.boot_seconds (low) and"
                f" {rel(RUN_V3)} :: projection.boot_seconds (high)"
            ),
            "what_it_is": (
                "a RANGE and not an estimate: the same serving configuration on the same volume"
                " booted in 205.518 s once and 402.586 s once, a 1.96x spread with n=1 on each"
                " side. Both are corners; neither is averaged away"
            ),
        },
        "warmup_seconds": {
            "value": v4["projection"]["warmup_seconds"],
            "source": f"{rel(RUN_V4)} :: projection.warmup_seconds",
            "what_it_is": "the two non-gold calls of SPEC 3.17 (9), billed before the first gold one",
        },
        "idle_tail_seconds": {
            "value": driver.IDLE_TAIL_SECONDS,
            "source": "scripts/positions_gm4_skub.IDLE_TAIL_SECONDS",
            "what_it_is": "what the worker bills after the last job, inside every projection below",
        },
    }


def uplift() -> dict:
    """What the 800 → 1200 ceiling does to a measured second, as two corners and no estimate."""
    ratio = local_llm.POSITIONS_MAX_NEW_TOKENS / CEILING_WAS
    return {
        "none": {
            "factor": 1.0,
            "reading": (
                "the ceiling binds only the replies that REACH it. v4 recorded exactly one page"
                " refused as `malformed JSON` — a reply that used its whole budget — so if that"
                " page is the only one that was truncated, the measured rates stand"
            ),
        },
        "the whole ceiling": {
            "factor": round(ratio, 4),
            "reading": (
                f"every call decodes to the new ceiling: {local_llm.POSITIONS_MAX_NEW_TOKENS} /"
                f" {CEILING_WAS}. A hard UPPER bound rather than a guess — no reply can generate"
                " past the ceiling — and the reason 4.0161 s/page is quoted as a floor at 1200"
                " rather than as a rate"
            ),
        },
    }


def corner(marg: dict, boot: float, factor: float, rate: float) -> dict:
    calls = {
        "pages": PAGES * marg["page_seconds_per_call"]["value"] * factor,
        "text_rows": TEXT_ROWS * marg["text_seconds_per_row"]["value"] * factor,
    }
    warmup = marg["warmup_seconds"]["value"] * factor
    idle = marg["idle_tail_seconds"]["value"]
    seconds = boot + warmup + calls["pages"] + calls["text_rows"] + idle
    return {
        "boot_seconds": boot,
        "decode_uplift": factor,
        "warmup_seconds": round(warmup, 3),
        "page_leg_seconds": round(calls["pages"], 3),
        "text_leg_seconds": round(calls["text_rows"], 3),
        "idle_tail_seconds": idle,
        "billed_seconds": round(seconds, 3),
        "usd": round(seconds * rate, 4),
        "usd_with_drift": round(seconds * rate * (1 + DRIFT), 4),
    }


def build(out: Path) -> dict:
    rate_record, rate_sha = load(RATE)
    v4, v4_sha = load(RUN_V4)
    v3, v3_sha = load(RUN_V3)
    rate = rate_record["rate"]["usd_per_second"]
    marg = marginals(v4, v3)
    factors = uplift()

    corners = {
        f"boot {boot_name} · decode {up_name}": corner(
            marg, marg["boot_seconds"][boot_name], factors[up_name]["factor"], rate
        )
        for boot_name in ("low", "high")
        for up_name in factors
    }
    worst = max(corners.values(), key=lambda cell: cell["usd_with_drift"])
    best = min(corners.values(), key=lambda cell: cell["usd_with_drift"])
    cap = b2.CAP_USD

    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "skub2 — what the re-measurement costs against its $0.65 cap",
        "written_by": (
            "skub2-prep (executor, $0), docs/PROMPT-skub2-prep.md deliverable 5; re-stamped by"
            " docs/PROMPT-skub2-fix.md step 5 against the cap 3.17 (14)(e) sets"
        ),
        "authority": "docs/SPEC.md amendment 3.17 (10)(a), (13)(d) and (14)(e)",
        "class": (
            "PROJECTION. Every rate is MEASURED — this is the first sku-b projection with a"
            " completed session behind it — and the two things that are not measured, the boot"
            " spread and what the 800 → 1200 ceiling does to a decode, are carried as corners"
            " rather than averaged into one number. Nothing here authorises a run: the (10)(a)"
            " gate re-prices from the session's own warm-up before the first gold call"
        ),
        "population": {
            "pages": PAGES,
            "text_rows": TEXT_ROWS,
            "elements": PAGES + TEXT_ROWS,
            "reading": (
                "all 138, per SPEC 3.17 (13)(d) — a re-measurement of instrument v2 cannot reuse"
                " instrument v1's answers, so the 17 the first session bought are re-asked"
            ),
        },
        "cap_usd": cap,
        "cap_source": f"{rel(b2.RECORD)} :: attempts.cap_usd (SPEC 3.17 (14)(e))",
        "rate_usd_per_second": rate,
        "rate_source": f"{rel(RATE)} :: rate.usd_per_second",
        "marginals": marg,
        "decode_uplift": factors,
        "drift": {
            "factor": DRIFT,
            "reading": (
                "a contract term carried from the v4 projection, not a measurement. Applied to the"
                " whole billed second count"
            ),
        },
        "corners": corners,
        "against_the_cap": {
            "cheapest_usd": best["usd_with_drift"],
            "dearest_usd": worst["usd_with_drift"],
            "cap_usd": cap,
            "fits": worst["usd_with_drift"] <= cap,
            "headroom_usd": round(cap - worst["usd_with_drift"], 4),
            "dearest_usd_without_drift": worst["usd"],
            "fits_without_drift": worst["usd"] <= cap,
            "headroom_without_drift_usd": round(cap - worst["usd"], 4),
            "reading": (
                "the dearest corner is boot-high with every call decoding to the new ceiling, and"
                " it is a HARD upper bound rather than a pessimistic guess: no reply can generate"
                " past the ceiling and no boot longer than the longest one ever measured on this"
                " configuration is in evidence. Against (13)(d)'s $0.40 that bound OVERSHOT, by"
                " four hundredths of a cent and only once the 3% drift term was applied on top of"
                " it; the ruling on that arithmetic is SPEC 3.17 (14)(e), which sets the cap at"
                " $0.65. The same bound now fits with room, and the room is the point rather than"
                " the margin: (12)(a)'s standing rule is that the cap admits the gate's own"
                " pessimism while the in-run gate protects the middle. Nothing here moved to make"
                " that true — every corner is the number it was before the cap was ruled on. The"
                " measured expectation is still the cheapest corner and change, and what must NOT"
                " happen is discovering a shortfall in flight: the (10)(a) gate would refuse the"
                " session after the boot is already billed, which is the outcome (12)(b) prices"
            ),
        },
        "job_timeout_headroom": job_timeout_headroom(marg, factors),
        "pinned_inputs": {
            rel(RATE): rate_sha,
            rel(RUN_V4): v4_sha,
            rel(RUN_V3): v3_sha,
        },
        "not_in_scope": {
            "the driver's constants": (
                "scripts/positions_gm4_skub.py still carries v4's CAP_USD, PHASE and LEDGER. Moving"
                " them to the B′ three is skub2-run's step and is guarded by the driver's own"
                " refusal on a mismatched registration — this file prices the run, it does not"
                " configure it"
            ),
        },
        "git": provenance.git_state(out),
    }


def job_timeout_headroom(marg: dict, factors: dict) -> dict:
    """`JOB_TIMEOUT_S` bounds ONE wedged worker, and the ceiling change moves what one job costs.

    The text leg is a single job of 30 rows, which is the longest job the packing produces; the
    page leg is split. Reported here because the property `tests/test_positions_driver.py` asserts
    — the timeout is at least twice the longest predicted job — was written at the 800 ceiling.
    """
    worst = factors["the whole ceiling"]["factor"]
    text_job = TEXT_ROWS * marg["text_seconds_per_row"]["value"] * worst
    # the same bound the driver's test uses: the text leg priced at the PAGE marginal, which is the
    # conservative reading of a row that turns out to be as dense as a page
    conservative = TEXT_ROWS * marg["page_seconds_per_call"]["value"] * worst
    return {
        "job_timeout_s": driver.JOB_TIMEOUT_S,
        "longest_job_measured_rates_s": round(text_job, 1),
        "longest_job_conservative_s": round(conservative, 1),
        "twice_the_conservative_job_s": round(2 * conservative, 1),
        "still_twice_the_conservative_job": 2 * conservative <= driver.JOB_TIMEOUT_S,
        "reading": (
            "checked because the property was established at the 800 ceiling and a ceiling change"
            " is exactly what could have quietly broken it. It did not: even at the conservative"
            " bound the driver's own test uses — 30 rows each as dense as a leaflet page, every"
            " one decoding to 1200 — twice the longest job still sits well under the 900 s"
            " timeout, and one wedged worker still cannot out-bill the cap. Measured rather than"
            " assumed, and reported either way"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    record = build(args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {rel(args.out)}")
    print(
        f"  measured      {record['marginals']['page_seconds_per_call']['value']} s/page"
        f" (n={record['marginals']['page_seconds_per_call']['n']}) ·"
        f" {record['marginals']['text_seconds_per_row']['value']} s/row"
        f" (n={record['marginals']['text_seconds_per_row']['n']}) · boot"
        f" {record['marginals']['boot_seconds']['low']}–{record['marginals']['boot_seconds']['high']} s"
    )
    for name, cell in record["corners"].items():
        print(
            f"  {name:<40} {cell['billed_seconds']:>8.1f} s  ${cell['usd']:.4f}"
            f"  ${cell['usd_with_drift']:.4f} with drift"
        )
    verdict = record["against_the_cap"]
    fits = "FITS" if verdict["fits"] else "DOES NOT FIT"
    print(
        f"  vs the ${verdict['cap_usd']:.2f} cap: {fits} —"
        f" dearest ${verdict['dearest_usd']:.4f}, headroom ${verdict['headroom_usd']:.4f}"
    )
    timeout = record["job_timeout_headroom"]
    print(
        f"  job timeout   {timeout['job_timeout_s']:.0f} s vs"
        f" 2x{timeout['longest_job_conservative_s']:.0f} s conservative —"
        f" {'ok' if timeout['still_twice_the_conservative_job'] else 'NO LONGER TWICE'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
