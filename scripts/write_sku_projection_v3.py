#!/usr/bin/env python3
"""Write `results/sku_projection_v3.json` — what the RESUMED session will cost ($0).

Deliverable 4 of `docs/PROMPT-sku-b-v3-prep.md`, under SPEC 3.17 (11)(d). The same class as
`results/sku_projection.json` and not a replacement for it: that record priced the whole pilot from
neighbouring runs before anything had been measured, it is what the $0.35 cap was set against, and
it stands as history. This one prices the 121 elements that are LEFT, and its inputs are different
in the one way that matters — the page marginal is no longer extrapolated from a caption run. It
was measured, by the session that stopped.

What that session proved, and what this record is built to respect:

* **the marginal is measured, and it is one job wide.** `results/sku_b_positions.json ::
  projection.per_gate[0]` reads 5.0772 s/call over 17 pages — one job, 17 of the 108, the first
  pages of three ATB posts. It carries that job's own overhead divided by 17 and it is one layout
  family. It is the best number in existence for this instrument and it is still n=17.
* **the text leg has never been measured at all.** No positions call has ever been made on text.
  The stated corner BOUNDS it by the page marginal — the assumption is written out below — and
  srv-2d's 4.262 s/row is carried beside it as the only image-free measurement on this stack.
* **a warm-up marginal does not price a gold call.** That is the whole finding of the interrupted
  session, so the two warm-up calls of SPEC 3.17 (11)(c) are priced at the PAGE marginal here
  rather than at anything a warm-up measured. They are real inputs now.
* **the boot is a range and its ends are different transports.** 391.369 s was billed yesterday on
  this endpoint class; 183.58 s is vis-c's serverless boot on the same base; 175.791 s is a POD
  cold start and is named as one. The spread does not change the verdict, which is the useful
  thing to be able to say.

    PYTHONPATH=src python3 scripts/write_sku_projection_v3.py
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
PREREG = REPO_ROOT / "results" / "sku_pilot_prereg_v3.json"
VISC = REPO_ROOT / "results" / "captions_gm4_visc.json"
POD = REPO_ROOT / "results" / "d7_reread_srv2b.json"
RECORD = REPO_ROOT / "results" / "sku_projection_v3.json"

WARMUP_CALLS = 2
"""SPEC 3.17 (9), unchanged by (11)(c): one page and one row, before either leg touches gold."""

TEXT_BOUND_NOTE = (
    "ASSUMPTION, and the only one left with a number attached. No positions call has ever been made"
    " on text, so the resumed session's 30 text calls are BOUNDED by the measured page marginal:"
    " both legs run the same instrument at the same 800-token ceiling, and a call with no image on"
    " the wire skips the vision prefill entirely — it cannot be slower than one that pays it, at"
    " equal decode. So the stated corner over-counts by however much of the 5.0772 s is prefill,"
    " and it over-counts in the safe direction for a cap. srv-2d's 4.262 s/row is carried beside it"
    " as the only image-free measurement on this stack and priced as its own corner; it is a"
    " DIFFERENT instrument at a 256-token ceiling, which is why it bounds nothing on its own."
)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def load(path: Path) -> tuple[dict, str]:
    return (
        json.loads(path.read_text(encoding="utf-8")),
        hashlib.sha256(path.read_bytes()).hexdigest(),
    )


def measured_page_marginal(run: dict) -> dict:
    """The one gold marginal this instrument has, with what it is made of said out loud.

    Read off the in-run gate rather than recomputed: `per_gate[0]` is the number the cap stop
    actually acted on, and a second arithmetic path here could disagree with the one that stopped
    the run. Its `calls_done` is the n, so the caveat cannot drift from the figure.
    """
    gate = run["projection"]["per_gate"][0]
    pages = [row["source"] for row in run["outcomes"]]
    return {
        "seconds_per_call": gate["marginal_seconds_per_call"],
        "n": gate["calls_done"],
        "source": f"{rel(RUN)} :: projection.per_gate[0].marginal_seconds_per_call",
        "how": (
            "(billed_seconds - opened_seconds) / calls_done ="
            f" ({gate['billed_seconds']} - {gate['opened_seconds']}) / {gate['calls_done']}."
            " `opened_seconds` is the clock after the handshake AND the two warm-up calls, so"
            " neither the cold start nor the warm-up is inside this rate"
        ),
        "caveats": (
            f"ONE job wide. All {gate['calls_done']} pages travelled in a single /run submission, so"
            " this rate carries that job's own per-job overhead divided by"
            f" {gate['calls_done']} — a resumed run of 6 jobs pays that overhead 6 times, which this"
            " rate under-counts. And they are the first pages of 3 of the 19 posts"
            f" ({', '.join(sorted({row['item'] for row in run['outcomes']}))}), which is one layout"
            f" family: {len(set(pages))} distinct pages, no post seen to its end"
        ),
    }


def build(out: Path) -> dict:
    rate_record, rate_sha = load(RATE)
    run, run_sha = load(RUN)
    prereg, prereg_sha = load(PREREG)
    visc, visc_sha = load(VISC)
    pod, pod_sha = load(POD)

    rate = float(rate_record["rate"]["usd_per_second"])
    page = measured_page_marginal(run)
    per_page = float(page["seconds_per_call"])
    srv2d_row = float(rate_record["measured"]["like_for_like_seconds_per_row"])

    already = prereg["resume"]["bought_already"]
    unbought = already["unbought"]
    n_pages = sum(1 for name in unbought if name.startswith("data/"))
    n_rows = len(unbought) - n_pages
    cap = float(prereg["attempts"]["cap_usd"])

    idle_seconds = driver.IDLE_TAIL_SECONDS
    boots = {
        "measured on this endpoint class yesterday": {
            "seconds": float(run["projection"]["boot_seconds"]),
            "source": f"{rel(RUN)} :: projection.boot_seconds",
            "transport": "serverless, POSITIONS worker, ADA_24 — the same thing the resume creates",
        },
        "vis-c's serverless boot on the same base": {
            "seconds": float(visc["projection"]["per_slice"][0]["boot_seconds"]),
            "source": f"{rel(VISC)} :: projection.per_slice[0].boot_seconds",
            "transport": "serverless, CAPTION worker — same transport, different serving config",
        },
        "the srv-2b pod control": {
            "seconds": float(pod["pod_control_the_same_evening"]["cold_start_s_wall"]),
            "source": f"{rel(POD)} :: pod_control_the_same_evening.cold_start_s_wall",
            "transport": (
                "a POD, not a serverless worker. It measures the weight load off the volume without"
                " the container start a serverless worker also pays, so it is a floor for a"
                " different thing and is carried as the optimistic END of the range rather than as"
                " a figure this session could expect"
            ),
        },
    }

    yesterday = boots["measured on this endpoint class yesterday"]["seconds"]
    visc_boot = boots["vis-c's serverless boot on the same base"]["seconds"]

    def corner(boot_name: str, text_name: str) -> dict:
        boot = boots[boot_name]["seconds"]
        text_rate = per_page if text_name == "bounded by the page marginal" else srv2d_row
        gold = n_pages * per_page + n_rows * text_rate
        warm = WARMUP_CALLS * per_page
        seconds = boot + warm + gold + idle_seconds
        total = seconds * rate
        return {
            "boot": boot_name,
            "text_rate": text_name,
            "boot_seconds": round(boot, 3),
            "boot_usd": round(boot * rate, 4),
            "warmup_seconds": round(warm, 3),
            "page_leg_usd": round(n_pages * per_page * rate, 4),
            "text_leg_usd": round(n_rows * text_rate * rate, 4),
            "idle_tail_usd": round(idle_seconds * rate, 4),
            "billed_seconds": round(seconds, 3),
            "total_usd": round(total, 4),
            "cap_usd": cap,
            "headroom_usd": round(cap - total, 4),
            "headroom_share_of_cap": round((cap - total) / cap, 4),
            "fits": total <= cap,
        }

    corners = {
        f"{boot} · {text}": corner(boot, text)
        for boot in boots
        for text in ("bounded by the page marginal", "srv-2d's image-free row")
    }
    worst = max(corners.values(), key=lambda cell: cell["total_usd"])
    best = min(corners.values(), key=lambda cell: cell["total_usd"])

    # what the measured marginal would have to become for the worst corner to exhaust the cap. The
    # decision needs an inequality, not another estimate: every term but the marginal is fixed here
    fixed = worst["boot_seconds"] + idle_seconds
    calls = WARMUP_CALLS + n_pages + n_rows  # the text leg is priced at the page marginal there
    break_even = (cap / rate - fixed) / calls

    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "sku-b — the resumed session, priced from what the interrupted one measured",
        "written_by": "sku-b-v3-prep (executor, $0), docs/PROMPT-sku-b-v3-prep.md deliverable 4",
        "authority": "docs/SPEC.md amendment 3.17 (11)(d)",
        "class": (
            "PROJECTION. Arithmetic over named artifacts — no new measurement was taken and no paid"
            " call was made to produce it. Every input names the file it came from. It does not"
            " replace results/sku_projection.json, which priced the pilot before anything had been"
            " measured and is what the $0.35 cap was set against"
        ),
        "population": {
            "pages": n_pages,
            "rows": n_rows,
            "calls": n_pages + n_rows,
            "source": f"{rel(PREREG)} :: resume.bought_already.unbought",
            "why": (
                "the 121 elements SPEC 3.17 (11)(a) leaves to buy. The 17 already bought are not"
                " priced here and are never re-asked"
            ),
        },
        "rate": {
            "usd_per_second": rate,
            "source": f"{rel(RATE)} :: rate.usd_per_second",
            "sha256": rate_sha,
            "corroboration": rate_record["rate"]["corroboration"],
        },
        "page_leg": page | {"calls": n_pages, "unit": "one PAGE, one call (SPEC 3.17 (4))"},
        "text_leg": {
            "calls": n_rows,
            "unit": "one ROW, one call, no image",
            "bound_usd_per_call": round(per_page * rate, 6),
            "assumption": TEXT_BOUND_NOTE,
            "srv2d": {
                "seconds_per_row": srv2d_row,
                "source": f"{rel(RATE)} :: measured.like_for_like_seconds_per_row",
                "why_not_the_stated_rate": (
                    "srv-2d ran a different instrument at a 256-token ceiling"
                    f" against this one's {driver.JOB_TIMEOUT_S:.0f}s-bounded 800. It is the only"
                    " image-free measurement on this stack and it is a neighbour, not a bound"
                ),
            },
        },
        "warmup": {
            "calls": WARMUP_CALLS,
            "priced_at": "the measured PAGE marginal, both of them",
            "why": (
                "SPEC 3.17 (11)(c) makes them real inputs — an unsent leaflet page and a"
                " pre-filtered row — so pricing them at anything a synthetic warm-up measured would"
                " repeat the error that stopped the interrupted session. The page call IS a page;"
                " the row call is bounded by it for the reason the text leg is"
            ),
        },
        "boot": boots
        | {
            "why_a_range": (
                "which boot the resumed session pays is not knowable in advance and the ends of this"
                " range are not the same measurement. 391.369 s is what this endpoint class billed"
                " yesterday and is the only same-configuration reading; the other two are neighbours"
                " and one of them is a pod. The range is carried because the verdict does not depend"
                " on it — see against_the_cap"
            ),
            "regression_not_diagnosed": (
                f"{yesterday} s is {yesterday / visc_boot:.2f}x vis-c's {visc_boot} s"
                " on the same base, and nothing in this repository explains the difference. The"
                " session's worker-boot.log is on the volume qw4nwleanc and a staging pod can read"
                " it for near-free. Named here because a projection that quietly used the cheaper"
                " boot would be assuming the regression away"
            ),
        },
        "idle_tail": {
            "seconds": idle_seconds,
            "usd": round(idle_seconds * rate, 4),
            "source": "scripts/positions_gm4_skub.py :: IDLE_TAIL_SECONDS",
            "why": (
                "serverless bills WALL UPTIME: the worker stays up for the endpoint's `--idle-timeout"
                " 60` after the last reply and that tail is charged to whoever woke it. Once per"
                " session, which is why it sits beside the boot rather than inside a leg's rate"
            ),
        },
        "corners": corners,
        "against_the_cap": {
            "cap_usd": cap,
            "cap_source": f"{rel(PREREG)} :: attempts.cap_usd (SPEC 3.17 (11)(d))",
            "lowest_usd": best["total_usd"],
            "highest_usd": worst["total_usd"],
            "fits_at_every_corner": all(cell["fits"] for cell in corners.values()),
            "corners_over_the_cap": sorted(
                name for name, cell in corners.items() if not cell["fits"]
            ),
            "break_even_page_marginal_seconds": round(break_even, 4),
            "reading": (
                f"the resumed session fits the ${cap:.2f} cap at every corner —"
                f" ${worst['total_usd']:.4f} at the worst"
                f" ({worst['headroom_share_of_cap']:.0%} headroom) and ${best['total_usd']:.4f} at"
                f" the best. The spread between the boot readings is ${worst['boot_usd'] - best['boot_usd']:.4f}"
                " and it does not change the verdict, which is the useful thing about carrying it."
                " The decision this record supports is an INEQUALITY and not an estimate: at the"
                " worst boot, the measured page marginal would have to reach"
                f" {break_even:.2f} s/call — {break_even / per_page:.2f}x the {per_page} s measured —"
                " before the cap is exhausted. The interrupted session's error was 3.54x in exactly"
                " that quantity, so the margin is real but it is not unlimited"
            ),
            "what_this_is_not": (
                "not a substitute for the go/no-go of SPEC 3.17 (10)(a). That gate re-prices the"
                " whole run from the session's OWN warm-up before the first gold call, and under"
                " (11)(c) that warm-up is finally representative. This record says the cap is"
                " adequate; the gate is what refuses if the day disagrees"
            ),
            "what_an_early_stop_costs": (
                "unchanged from results/sku_projection.json and now demonstrated: bar 1's page set"
                " is R2's 108, a post whose pages were partly bought has a gold set written against"
                " all of them, and fewer pages moves the numerator and not the denominator. A second"
                " partial run would leave the pilot exactly where the first one did"
            ),
        },
        "pinned_inputs": {
            rel(RATE): rate_sha,
            rel(RUN): run_sha,
            rel(PREREG): prereg_sha,
            rel(VISC): visc_sha,
            rel(POD): pod_sha,
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
    page = record["page_leg"]
    print(
        f"  population   {record['population']['pages']} pages +"
        f" {record['population']['rows']} rows = {record['population']['calls']} calls"
        f"\n  page rate    {page['seconds_per_call']} s/call MEASURED (n={page['n']}, one job)"
        f"\n  text rate    bounded by it; srv-2d reads"
        f" {record['text_leg']['srv2d']['seconds_per_row']} s/row"
    )
    for name, cell in record["corners"].items():
        print(
            f"  {name:<62} ${cell['total_usd']:.4f}"
            f"  headroom ${cell['headroom_usd']:+.4f}"
            f"  {'fits' if cell['fits'] else 'OVER THE CAP'}"
        )
    against = record["against_the_cap"]
    print(
        f"  break-even   {against['break_even_page_marginal_seconds']} s/call at the worst boot"
        f" (measured {page['seconds_per_call']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
