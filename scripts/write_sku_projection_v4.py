#!/usr/bin/env python3
"""Write `results/sku_projection_v4.json` — what the v4 session will cost ($0).

Deliverable 3 of `docs/PROMPT-sku-b-v4-prep.md`, under SPEC 3.17 (12)(a). Registered BESIDE
`results/sku_projection_v3.json` and not over it: that record priced the resumed session at the
$0.45 cap and is what the (10)(a) gate then refused, so it is the history this one exists because
of.

What changed between the two, and it is the whole point of this record:

* **the page marginal is no longer a single estimate.** v3's projection had one measured number —
  5.0772 s/call, `results/sku_b_positions.json :: projection.per_gate[0]`, drawn from 17 pages of
  the gold population — and every corner was built on it. The refused session then measured a
  SECOND one on a real unsent page: 14.808 s. Both are real, they disagree by 2.9x, and neither is
  the population's rate: the 17 are first-six-page posters (10 of them answered `[]`), the probe is
  a deep dense grid, and each is n of its own kind. So both are carried as CORNERS and the cap is
  read against the pessimistic one, which is what (12)(a) sized $0.65 to admit.
* **the text marginal is measured at all.** 3.862 s, from the same probe. v3's projection had to
  BOUND the text leg by the page marginal because no positions call had ever been made on text;
  this one prices it at what a real pre-filtered row cost. n=1, said out loud — it is one row, not
  a rate over the pack.
* **the boot is one number, not a range.** 402.586 s, billed by this endpoint class on the refused
  session — the same serving configuration, the same volume, the same GPU class. v3 carried a range
  because it had neighbours and no same-configuration reading; this one has the reading.

    PYTHONPATH=src python3 scripts/write_sku_projection_v4.py
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

from market_pulse import provenance  # noqa: E402

RATE = REPO_ROOT / "results" / "srv2d_cost.json"
RUN = REPO_ROOT / "results" / "sku_b_positions.json"
REFUSED = REPO_ROOT / "results" / "sku_b_positions_v3.json"
PREREG = REPO_ROOT / "results" / "sku_pilot_prereg_v4.json"
RECORD = REPO_ROOT / "results" / "sku_projection_v4.json"

DRIFT = 0.03
"""The margin `docs/PROMPT-sku-b-v4-prep.md` deliverable 3 requires the pessimistic corner to fit
under $0.65 WITH. It is a contract term, not a measurement: nothing in this repository measures how
far a serverless worker's seconds drift between two runs of the same job, and dressing 3% up as an
observed spread would be inventing a number. Applied to the whole billed second count — boot, both
warm-ups, both legs and the idle tail — because the drift it stands in for is the endpoint being
slower on the day, not one leg being mis-priced."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def load(path: Path) -> tuple[dict, str]:
    return (
        json.loads(path.read_text(encoding="utf-8")),
        hashlib.sha256(path.read_bytes()).hexdigest(),
    )


def marginals(run: dict, refused: dict) -> dict:
    """The two page rates and the one text rate, each with what it is made of said out loud.

    Read off the artifacts rather than recomputed: `per_gate[0]` is the number the in-run cap stop
    acted on and `warmup.replies` are the numbers the (10)(a) gate refused on, so a second
    arithmetic path here could disagree with the instruments that actually decided something.
    """
    gate = run["projection"]["per_gate"][0]
    replies = refused["warmup"]["replies"]
    return {
        "the registered probe, a deep unsent page": {
            "seconds_per_call": replies["positions_post_gm4"]["marginal_seconds"],
            "n": 1,
            "source": f"{rel(REFUSED)} :: warmup.replies.positions_post_gm4.marginal_seconds",
            "what_it_is": (
                "SPEC 3.17 (11)(c)'s registered warm-up page, answered once by the refused session."
                " It is one of the 51 pages the caption run never sent — structurally a DEEP page,"
                " because the first six of each leaflet are the ones that were sent. A dense grid of"
                " positions costs decode time the way a poster with two price tags does not"
            ),
            "why_it_is_the_cap_corner": (
                "it is the number the (10)(a) gate priced this run at, and (12)(a) sized the $0.65"
                " cap to admit it. A cap that only fits the optimistic marginal is a cap that"
                " refuses on the day"
            ),
        },
        "the population's drawn marginal, 17 first-six pages": {
            "seconds_per_call": gate["marginal_seconds_per_call"],
            "n": gate["calls_done"],
            "source": f"{rel(RUN)} :: projection.per_gate[0].marginal_seconds_per_call",
            "what_it_is": (
                "(billed_seconds - opened_seconds) / calls_done ="
                f" ({gate['billed_seconds']} - {gate['opened_seconds']}) / {gate['calls_done']},"
                " so neither the cold start nor the warm-up is inside it. Drawn from the gold"
                " population itself — which is its strength — but all 17 travelled in ONE /run"
                " submission, so the rate carries that job's overhead divided by 17 and a 6-job run"
                " pays it 6 times"
            ),
            "why_it_is_not_the_cap_corner": (
                "10 of those 17 pages answered `[]`. An empty answer is a real outcome and a cheap"
                " one — the decode stops early — so a mean over a sample that is 59% empty prices"
                " the pages that are NOT empty at less than they cost"
            ),
        },
        "text, measured": {
            "seconds_per_call": replies["positions_text_gm4"]["marginal_seconds"],
            "n": 1,
            "source": f"{rel(REFUSED)} :: warmup.replies.positions_text_gm4.marginal_seconds",
            "what_it_is": (
                "(11)(c)'s registered warm-up row — a real pre-filtered comment the 30-row pack did"
                " not draw — answered once. It is the FIRST positions call ever made on text: v3's"
                " projection had to bound the text leg by the page marginal because no such"
                " measurement existed. One row is not a rate over the pack, and it is used as one"
                " here only because the alternative is the bound it replaces"
            ),
        },
    }


def build(out: Path) -> dict:
    rate_record, rate_sha = load(RATE)
    run, run_sha = load(RUN)
    refused, refused_sha = load(REFUSED)
    prereg, prereg_sha = load(PREREG)

    rate = float(rate_record["rate"]["usd_per_second"])
    rates = marginals(run, refused)
    per_row = float(rates["text, measured"]["seconds_per_call"])
    boot = float(refused["projection"]["boot_seconds"])
    idle = driver.IDLE_TAIL_SECONDS

    unbought = prereg["resume"]["bought_already"]["unbought"]
    n_pages = sum(1 for name in unbought if name.startswith("data/"))
    n_rows = len(unbought) - n_pages
    cap = float(prereg["attempts"]["cap_usd"])

    def corner(name: str) -> dict:
        per_page = float(rates[name]["seconds_per_call"])
        # SPEC 3.17 (9), unchanged by (11)(c) and (12)(c): TWO warm-up calls before either leg
        # touches gold — one page, one row. Both are registered inputs and both were measured by
        # the refused session, so each is priced at its own marginal rather than one bounding both.
        warm = per_page + per_row
        gold = n_pages * per_page + n_rows * per_row
        seconds = boot + warm + gold + idle
        drifted = seconds * (1 + DRIFT)
        # the decision is an INEQUALITY: every term but the page marginal is fixed, so this is the
        # rate at which the cap is exhausted — 91 gold pages plus the one warm-up page
        fixed = boot + idle + n_rows * per_row + per_row
        break_even = (cap / rate / (1 + DRIFT) - fixed) / (n_pages + 1)
        return {
            "page_marginal_seconds": per_page,
            "page_marginal_n": rates[name]["n"],
            "boot_seconds": boot,
            "boot_usd": round(boot * rate, 4),
            "warmup_seconds": round(warm, 3),
            "page_leg_usd": round(n_pages * per_page * rate, 4),
            "text_leg_usd": round(n_rows * per_row * rate, 4),
            "idle_tail_usd": round(idle * rate, 4),
            "billed_seconds": round(seconds, 3),
            "total_usd": round(seconds * rate, 4),
            "headroom_usd": round(cap - seconds * rate, 4),
            "fits": seconds * rate <= cap,
            "with_drift": {
                "pct": DRIFT,
                "billed_seconds": round(drifted, 3),
                "total_usd": round(drifted * rate, 4),
                "headroom_usd": round(cap - drifted * rate, 4),
                "fits": drifted * rate <= cap,
            },
            "break_even_page_marginal_seconds": round(break_even, 4),
            "break_even_multiple": round(break_even / per_page, 4),
        }

    corners = {name: corner(name) for name in rates if name != "text, measured"}
    pessimistic = max(corners.values(), key=lambda cell: cell["total_usd"])
    optimistic = min(corners.values(), key=lambda cell: cell["total_usd"])

    # the positive control, and it is free: the pessimistic corner IS the run the (10)(a) gate
    # priced, from the same marginals over the same 121 elements. If the two disagree, the
    # arithmetic here is not the arithmetic that refused the session and one of them is wrong.
    gate = refused["projection"]["go_no_go"]
    if abs(pessimistic["total_usd"] - gate["projected_usd"]) > 0.0001:
        raise SystemExit(
            f"the pessimistic corner prices ${pessimistic['total_usd']:.4f} and"
            f" {rel(REFUSED)} :: projection.go_no_go priced ${gate['projected_usd']:.4f} from the"
            " same marginals over the same population. Same inputs, two answers — this record's"
            " arithmetic is not the gate's and the difference has to be found, not rounded away."
        )

    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "sku-b — the v4 session, priced from what the refused one measured",
        "written_by": "sku-b-v4-prep (executor, $0), docs/PROMPT-sku-b-v4-prep.md deliverable 3",
        "authority": "docs/SPEC.md amendment 3.17 (12)(a)",
        "class": (
            "PROJECTION. Arithmetic over named artifacts — no new measurement was taken and no paid"
            " call was made to produce it. Every input names the file it came from. It does not"
            " replace results/sku_projection_v3.json, which priced the same population against the"
            " $0.45 cap and is what the (10)(a) gate then refused"
        ),
        "population": {
            "pages": n_pages,
            "rows": n_rows,
            "calls": n_pages + n_rows,
            "source": f"{rel(PREREG)} :: resume.bought_already.unbought",
            "why": (
                "the 121 elements SPEC 3.17 (11)(a) leaves to buy, unchanged by (12)(d). The 17"
                " already bought are not priced here and are never re-asked; the refused session"
                " bought none of them"
            ),
        },
        "rate": {
            "usd_per_second": rate,
            "source": f"{rel(RATE)} :: rate.usd_per_second",
            "sha256": rate_sha,
            "corroboration": rate_record["rate"]["corroboration"],
        },
        "marginals": rates,
        "boot": {
            "seconds": boot,
            "usd": round(boot * rate, 4),
            "source": f"{rel(REFUSED)} :: projection.boot_seconds",
            "why_one_number": (
                "the refused session booted THIS endpoint class — SERVING_CONFIG=POSITIONS on"
                " ADA_24 off volume qw4nwleanc — so v3's range of neighbours is superseded by a"
                " same-configuration reading. It is 2.19x vis-c's 183.58 s on the same base and the"
                " gap is diagnosed but not fixed: 112 s of it is a cold read of 1188 shards off the"
                " network volume (docs/reports/sku-b-v3-run.md §2). The volume is warm now in no"
                " sense this record can rely on, so the full 402.586 s is priced"
            ),
        },
        "idle_tail": {
            "seconds": idle,
            "usd": round(idle * rate, 4),
            "source": "scripts/positions_gm4_skub.py :: IDLE_TAIL_SECONDS",
            "why": (
                "serverless bills WALL UPTIME: the worker stays up for the endpoint's"
                " `--idle-timeout 60` after the last reply and that tail is charged to whoever woke"
                " it. Once per session, which is why it sits beside the boot rather than inside a"
                " leg's rate"
            ),
        },
        "drift": {
            "pct": DRIFT,
            "source": "docs/PROMPT-sku-b-v4-prep.md deliverable 3",
            "why": (
                "a contract term, not a measurement. Nothing here measures how far a serverless"
                " worker's seconds move between two runs of the same job, and presenting 3% as an"
                " observed spread would be inventing a number. Applied to the whole billed second"
                " count, because what it stands in for is the endpoint being slower on the day"
            ),
        },
        "corners": corners,
        "against_the_cap": {
            "cap_usd": cap,
            "cap_source": f"{rel(PREREG)} :: attempts.cap_usd (SPEC 3.17 (12)(a))",
            "lowest_usd": optimistic["total_usd"],
            "highest_usd": pessimistic["total_usd"],
            "highest_with_drift_usd": pessimistic["with_drift"]["total_usd"],
            "fits_at_every_corner": all(cell["with_drift"]["fits"] for cell in corners.values()),
            "corners_over_the_cap": sorted(
                name for name, cell in corners.items() if not cell["with_drift"]["fits"]
            ),
            "reading": (
                f"the v4 session fits the ${cap:.2f} cap at both corners with the 3% drift on:"
                f" ${pessimistic['with_drift']['total_usd']:.4f} at the pessimistic one"
                f" (${pessimistic['with_drift']['headroom_usd']:.4f} of headroom) and"
                f" ${optimistic['with_drift']['total_usd']:.4f} at the optimistic one. Without the"
                f" drift the pessimistic corner is ${pessimistic['total_usd']:.4f}, which is the"
                " number the (10)(a) gate refused $0.45 with — the same arithmetic, checked against"
                " the gate's own figure when this record is built. The decision it supports is an"
                " INEQUALITY: at this boot the page marginal would have to reach"
                f" {pessimistic['break_even_page_marginal_seconds']:.2f} s/call —"
                f" {pessimistic['break_even_multiple']:.2f}x the registered probe's own"
                f" {pessimistic['page_marginal_seconds']} s — before the cap is exhausted with the"
                " drift on"
            ),
            "what_the_headroom_is_not": (
                "it is not a licence to run at the pessimistic corner and hope. The in-run gate of"
                " (10)(b) re-prices between jobs and is what stops a run whose real marginal lands"
                " above the probe's; this record only says the CAP is adequate for the run the"
                " (10)(a) gate is expected to let through"
            ),
            "what_an_early_stop_costs": (
                "unchanged from results/sku_projection.json and now demonstrated twice: bar 1's page"
                " set is R2's 108, a post whose pages were partly bought has a gold set written"
                " against all of them, and fewer pages moves the numerator and not the denominator."
                " A second partial run would leave the pilot where the first one did"
            ),
        },
        "pinned_inputs": {
            rel(RATE): rate_sha,
            rel(RUN): run_sha,
            rel(REFUSED): refused_sha,
            rel(PREREG): prereg_sha,
        },
        "git": provenance.git_state(out),
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
        f"  population   {record['population']['pages']} pages +"
        f" {record['population']['rows']} rows = {record['population']['calls']} calls"
        f"\n  boot         {record['boot']['seconds']} s (${record['boot']['usd']:.4f})"
        f" · idle tail {record['idle_tail']['seconds']:.0f} s"
        f" (${record['idle_tail']['usd']:.4f}) · text {record['marginals']['text, measured']['seconds_per_call']} s/row (n=1)"
    )
    for name, cell in record["corners"].items():
        print(
            f"  {name:<46} {cell['page_marginal_seconds']:>7} s/page (n={cell['page_marginal_n']})"
            f"  ${cell['total_usd']:.4f} → ${cell['with_drift']['total_usd']:.4f} with drift"
            f"  headroom ${cell['with_drift']['headroom_usd']:+.4f}"
            f"  {'fits' if cell['with_drift']['fits'] else 'OVER THE CAP'}"
        )
    against = record["against_the_cap"]
    print(
        f"  cap          ${against['cap_usd']:.2f} · fits at every corner with drift:"
        f" {against['fits_at_every_corner']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
