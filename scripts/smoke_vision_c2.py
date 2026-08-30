#!/usr/bin/env python3
"""The C2 vision smoke: measure `vision_seconds_per_page` on ≤30 pages, then tear down.

The review of 2026-08-30 authorised ONE smoke of the vision leg — «≤30 pages, cap $0.35, four
rungs per docs/PROCESS.md, teardown proven by listing» — because `results/measurements.jsonl`
has no seconds-per-page row at all and `scripts/promo_projection_c2.py` refuses to quote one
number without it. This is that smoke and nothing else: it buys a RATE, not a population.

**Why this is not `scripts/run_5c2.py`.** That driver is bound to `results/prereg_5c2_run.json`,
a SEALED registration whose population is the 159 leaflet pages 5c2 already paid for. Running it
would re-buy a frozen exam and measure the rate on the very pages the next pass must not re-read
([[a_smoke_drawn_from_the_exam_is_not_a_rate_sample]]). So the pages here are drawn from the OTHER
two manifests, and the 159 of `post_media_5c1.json` are excluded by name.

**The transport is not forked.** `serving.EndpointClient`, `loop.render_page`, `loop.PAGE_TASK`
and `run_loop.pages_of` are imported: a rate measured through a second transport is a rate for
that transport ([[the_smokes_rate_carries_the_smokes_transport]]), and the paid pass would then
be projected off a number nothing it runs produced.

    python3.11 scripts/smoke_vision_c2.py --register          # $0, writes the pre-registration
    PYTHONPATH=src python3.11 scripts/smoke_vision_c2.py --run --endpoint <id>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import run_loop  # noqa: E402

from market_pulse import loop, serving  # noqa: E402

PREREG = REPO_ROOT / "results" / "prereg_smoke_vision_c2.json"
RECORD = REPO_ROOT / "results" / "smoke_vision_c2.json"
LEDGER = REPO_ROOT / "results" / "measurements.jsonl"
POSITIONS_PIN = REPO_ROOT / "results" / "sku_pilot_serving_v2.json"

MANIFESTS = ("post_media_45g2.json", "post_media_visc.json")
"""`post_media_5c1.json` is DELIBERATELY absent: its 159 pages are 5c2's bought population."""

EXCLUDED_MANIFEST = "post_media_5c1.json"
MAX_PAGES = 30
SEED = 42
RATE_USD_PER_S = 0.00030669
"""`results/run_5c2_positions.json :: rate_usd_per_second` — the ADA_24 serverless rate, confirmed
twice in `results/srv2c_bootlog.json :: dv18_corrected` ($0.0003068 against the console's $0.00031)."""
CAP_USD = 0.35
"""The review's cap. `enforce()` binds beside it; a cap is not raised to finish a run."""
RATE_NAME = "vision_seconds_per_page"


def pages() -> list[dict]:
    """The smoke's population: MAX_PAGES pages, seed 42, from the manifests 5c2 did not buy."""
    out = []
    for name in MANIFESTS:
        path = REPO_ROOT / "results" / name
        if not path.exists():
            continue
        manifest = json.loads(path.read_text(encoding="utf-8"))
        for handle in sorted({e["channel"] for e in manifest["entries"].values()}):
            out += [page | {"manifest": name} for page in run_loop.pages_of(manifest, handle)]
    out.sort(key=lambda p: (p["manifest"], p["channel"], p["msg_id"]))
    return random.Random(SEED).sample(out, min(MAX_PAGES, len(out)))


def ids_sha256(chosen: list[dict]) -> str:
    blob = "\n".join(f"{p['manifest']}\x1f{p['channel']}\x1f{p['msg_id']}" for p in sorted(
        chosen, key=lambda p: (p["manifest"], p["channel"], p["msg_id"])))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def projection(n_pages: int) -> dict:
    """Rung 0, computed from MEASURED seconds and priced BEFORE anything is created.

    Two boots, not one: `srv2c_bootlog.json` records that «health read {idle:1, ready:1} seconds
    after `serverless create` and before any job was submitted», so something boots at creation
    and the job's own cold start may be a second one ([[a_refusal_is_an_outcome_with_a_price]] —
    the boot lands on the retry's budget). The slower of the two measured boots is the one priced.
    """
    boot_s = 212.041  # the UNWRAPPED control, the slower of srv-2c's two measured boots
    idle_tail_s = 60.0  # `run_5c2_positions.json :: go_no_go.idle_tail_seconds`
    prior_s_per_page = 10.408  # `run_5c2_positions.json :: timing.seconds_per_row`, the realised one
    seconds = 2 * boot_s + n_pages * prior_s_per_page + idle_tail_s
    usd = round(seconds * RATE_USD_PER_S, 4)
    return {
        "boots_priced": 2,
        "boot_seconds_each": boot_s,
        "boot_source": "results/srv2c_bootlog.json :: the_execution_time_gap.unwrapped.execution_ms",
        "idle_tail_seconds": idle_tail_s,
        "pages": n_pages,
        "prior_seconds_per_page": prior_s_per_page,
        "prior_source": "results/run_5c2_positions.json :: timing.seconds_per_row",
        "billable_seconds": round(seconds, 3),
        "rate_usd_per_second": RATE_USD_PER_S,
        "projected_usd": usd,
        "cap_usd": CAP_USD,
        "fits": usd <= CAP_USD,
    }


def register() -> dict:
    chosen = pages()
    record = {
        "phase": "promo-pulse-1-s2s3 — the C2 vision smoke",
        "authority": "docs/reviews/2026-08-30-plan-promo-pulse-1.md, «Money — operator's word"
        " (30.08): Да, смок авторизован» — one smoke, ≤30 pages, cap $0.35, four rungs",
        "the_one_question": "what is vision_seconds_per_page, measured, on the transport the paid"
        " pass would use",
        "population": {
            "pages": len(chosen),
            "ids_sha256": ids_sha256(chosen),
            "seed": SEED,
            "manifests": list(MANIFESTS),
            "excluded": f"{EXCLUDED_MANIFEST} — 5c2's bought 159 pages; a rate measured on the"
            " exam is not a rate sample for the population",
            "rows": sorted(
                f"{p['manifest']}:{p['channel']}:{p['msg_id']}" for p in chosen
            ),
        },
        "expected_worker": json.loads(POSITIONS_PIN.read_text(encoding="utf-8"))["expected_worker"],
        "expected_worker_from": "results/sku_pilot_serving_v2.json — the same pin run_5c2 asserts",
        "rung_0": projection(len(chosen)),
        "kill_rules": [
            "info disagrees with expected_worker → tear down, send NO pages, record the difference",
            "two boots without a served info → KILL, do not try a third",
            "the projection at the MEASURED rate exceeds the cap → KILL (PROCESS rung 2:"
            " over by ≤20% → ASK and hold ≤10 min; over by more → KILL)",
            "the guard refuses at any point → that is the answer, not an obstacle",
        ],
        "teardown": "runpodctl serverless delete <endpoint> && runpodctl template delete <template>,"
        " proven by `runpodctl serverless list` → [] with the network volume mp-srv2 and template"
        " unfcr3ja0t still listed as the positive control",
        "recovery_clause": "one re-create of the SAME endpoint within the same cap if the first"
        " boot dies without serving info; nothing else",
    }
    PREREG.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return record


def run(endpoint: str, api_key: str) -> dict:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    chosen = pages()
    if ids_sha256(chosen) != prereg["population"]["ids_sha256"]:
        raise SystemExit("the selection moved since the registration — refuse rather than re-draw")

    client = serving.EndpointClient(
        endpoint,
        api_key,
        retries=0,
        forward_batch_size=1,
        policy=serving.execution_policy(1800, 3600),
        job_timeout=1800,
        submit="run",
    )
    info = serving.assert_serving(client.info(), prereg["expected_worker"])
    print(f"info: serving {info.get('serving_config')} at {info.get('revision_requested')[:12]}…")

    started = time.time()
    albums = [loop.render_page(loop.page_file(page))[2] for page in chosen]
    replies = client.positions(loop.PAGE_TASK, albums)
    wall = time.time() - started
    timing = client.timing()
    per_page = round(timing["worker_seconds"] / len(chosen), 3)
    record = {
        "phase": prereg["phase"],
        "authority": "results/prereg_smoke_vision_c2.json",
        "endpoint": endpoint,
        "pages": len(chosen),
        "ids_sha256": prereg["population"]["ids_sha256"],
        "replies": len(replies),
        "info": info,
        "timing": timing | {"wall_seconds_client": round(wall, 3)},
        "vision_seconds_per_page": per_page,
        "billed_usd_at_the_rate": round(timing["worker_seconds"] * RATE_USD_PER_S, 4),
        "rung_0": prereg["rung_0"],
    }
    RECORD.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with LEDGER.open("a", encoding="utf-8") as out:
        out.write(json.dumps({
            "contract": "promo-pulse-1-s2s3",
            "name": RATE_NAME,
            "value": per_page,
            "unit": "seconds",
            "n": len(chosen),
            "max": round(max(timing.get("per_call_seconds") or [per_page]), 3)
            if timing.get("per_call_seconds") else per_page,
            "source": "results/smoke_vision_c2.json",
            "instrument": "positions_post_gm4, one page per forward, batch 1, thinking OFF",
            "measured_on": f"serverless endpoint {endpoint}, ADA_24, EU-RO-1, volume mp-srv2",
        }, ensure_ascii=False) + "\n")
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", action="store_true", help="$0: write the pre-registration")
    parser.add_argument("--run", action="store_true", help="the PAID leg")
    parser.add_argument("--endpoint", help="the serving endpoint id")
    args = parser.parse_args(argv)
    if args.register:
        record = register()
        print(json.dumps(record["rung_0"], indent=1))
        print(f"{record['population']['pages']} pages, ids {record['population']['ids_sha256'][:16]}…")
        print(f"wrote {PREREG.relative_to(REPO_ROOT)}")
        return 0
    if args.run:
        key = os.environ.get("RUNPOD_API_KEY")
        if not args.endpoint or not key:
            raise SystemExit("--endpoint and $RUNPOD_API_KEY are both required")
        record = run(args.endpoint, key)
        print(f"{RATE_NAME} = {record['vision_seconds_per_page']} s over {record['pages']} pages")
        print(f"billed at the rate: ${record['billed_usd_at_the_rate']}")
        return 0
    parser.error("choose --register or --run")


if __name__ == "__main__":
    raise SystemExit(main())
