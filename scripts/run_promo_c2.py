#!/usr/bin/env python3
"""S4 — the C2 backfill, served for real: the census's pages through vision, its price posts as text.

`results/promo_census_c2.json` pinned the population (968 media posts → 3 008 pages counted by
`results/promo_pagecount_c2.json`, and 405 text price posts) and `results/promo_projection_c2.json`
priced the vision leg at the smoke's marginal. This driver buys exactly that population under the
step ruling 02.09 (b) names — `--step promo-pulse-1 --step-cap 3.95` — and nothing decides a
price, a cap or a population here: they are READ from those records and the run refuses when what
is on disk has moved.

**Not a fork of `scripts/run_5c2.py`.** That driver is bound to a SEALED registration whose
population is the 159 pages 5c2 already paid for. Its transport (`SliceTransport`: one job per
pack, the pass still recording one row at a time), its money gates (`cap_gate`, `pack_size`,
`page_packs`, `billed_now`) and its legs (`page_leg`, `post_leg`) are imported, because a pass
measured through one transport and bought through another is priced off a number it never produced.
The evidence rows land in `data/derived/` through `loop.page_pass` / `loop.post_pass`, durable
before the watermark, so an interrupted run re-asks nothing it already answered (`loop.queued_pages`
subtracts the page markers on disk) and a second `--run` continues under the same step cap.

**The four rungs of `docs/PROCESS.md` («Money»), where each one is:**
(0) `--register` prices the WHOLE step — pages, posts, boots, idle tail — at the measured corners
BEFORE anything is created, and `--run` refuses to build a client when the dear corner does not fit
the step cap; the guard's own step anchor is written by `scripts/runpod_guard.py`, not here.
(1) liveness — the endpoint's execution timeout (900 s per job) and the client's `retries=0`.
(2) the (10)(a) gate PER LEG and the room PER CHANNEL (ruling 02.09 (c)): the text leg is projected
on its own after its warm-up and bought as stage 0 — it is never refused for the page leg — and
each channel is then measured by its OWN first pack, its remainder projected at that rate against
what is left of the cap; a remainder that does not fit is left unbought and the next channel starts;
the run ends when the room is below one pack at the worst measured rate. The whole-step page
projection is retired: one rate over 17 channels lies in both directions (a leaflet page reads
10–13 s, a promo photo 2.6–3.4 s). (3) the per-pack `cap_gate`: no job may be capable of billing
past the remaining cap. The cap is never raised mid-run (silence = KILL: nobody can be asked).

    python3.11 scripts/run_promo_c2.py --register                        # $0: the registration
    PYTHONPATH=src python3.11 scripts/run_promo_c2.py --dry-run          # $0: selections, hashes
    PYTHONPATH=src python3.11 scripts/run_promo_c2.py --run --endpoint <id>   # PAID
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import measurements  # noqa: E402
import positions_gm4_skub as skub  # noqa: E402
import run_5c2 as fivec2  # noqa: E402
import run_loop  # noqa: E402

from market_pulse import loop, positions, serving  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.raw_store import RawStore, live_store  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

STEP = "promo-pulse-1"
STEP_CAP_USD = 3.95
"""Ruling 02.09 (b) (`docs/reviews/2026-08-30-plan-promo-pulse-1.md`), the operator's word «$3.95 —
весь шаг»: «`STEP_CAP_USD = 3.95` … the guard's step anchor with `--step promo-pulse-1 --step-cap
3.95`». The team lead's number, not this file's; never raised mid-run."""

STEP_CAP_FROM = "docs/reviews/2026-08-30-plan-promo-pulse-1.md «Ruling 02.09 (b)»"
"""WHO set the cap `rung_0` is priced against — the one field of the record that answers it.

It is a sentence about the number in `STEP_CAP_USD`, so it moves with it: a leg that carries its
own `--cap` is not capped by (b) and a record that says it is names the wrong authority for the
only number that can stop the run. `repoint` derives it from the flag; ruling 09.09 (ii) item 3(iv)."""

PREREG = REPO_ROOT / "results" / "prereg_promo_c2.json"
RECORD = REPO_ROOT / "results" / "run_promo_c2.json"
CENSUS = REPO_ROOT / "results" / "promo_census_c2.json"
PAGECOUNT = REPO_ROOT / "results" / "promo_pagecount_c2.json"
PROJECTION = REPO_ROOT / "results" / "promo_projection_c2.json"
MANIFEST = REPO_ROOT / "results" / "post_media_promo_c2.json"
POSITIONS_PIN = REPO_ROOT / "results" / "sku_pilot_serving_v2.json"
PREREG_5C2 = REPO_ROOT / "results" / "prereg_5c2_run.json"
RUN_5C2 = REPO_ROOT / "results" / "run_5c2_positions.json"
SMOKE = REPO_ROOT / "results" / "smoke_vision_c2.json"
SMOKE_PREREG = REPO_ROOT / "results" / "prereg_smoke_vision_c2.json"
MEASUREMENTS = REPO_ROOT / "results" / "measurements.jsonl"


def pinned() -> tuple[Path, ...]:
    """The inputs the registration hashes — read at call time, so a test can point them elsewhere."""
    return (
        CENSUS,
        PAGECOUNT,
        PROJECTION,
        MANIFEST,
        POSITIONS_PIN,
        PREREG_5C2,
        RUN_5C2,
        SMOKE,
        SMOKE_PREREG,
    )


LEAFLET_CARRIER = "@atb_market_official"
"""Ruling 02.09 (c) §3, the operator's «АТБ → дешёвые → малые»: «`@atb_market_official` whole (the
leaflet carrier, 209 pages)» opens the page stages. The one handle this file names; the rest of the
order is derived below from the pagecount and the smoke's own population."""

MEASURED_MIN_ROWS = 2
"""How many smoke pages a channel needs before the smoke counts as having MEASURED it. One page is
a row, not a rate ([[a_reproducible_probe_can_be_unrepresentative]]) — and it is the line that
makes the derivation below reproduce the three channels ruling (c) §3 names."""

ENDPOINT_ENV = "RUNPOD_PROMO_C2_ENDPOINT"
API_KEY_ENV = "RUNPOD_API_KEY"


def rel(path: Path) -> str:
    """Repo-relative for the record; a path outside the checkout (a test's) stays absolute."""
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def smoke_rows_per_channel() -> dict[str, int]:
    """How many pages of each channel the vision smoke actually bought — its population file."""
    rows = load(SMOKE_PREREG)["population"]["rows"]
    return collections.Counter(one.split(":")[1] for one in rows)


def stage_order() -> list[str]:
    """The page stages of ruling 02.09 (c) §3, DERIVED — «АТБ → дешёвые → малые».

    The carrier first, then the channels the smoke measured (its own population file, most-measured
    first), then everything else ascending by the exact page count. Nothing is a typed list: a
    channel that leaves the census, or one whose pages grow, moves itself.
    """
    exact = {row["channel"]: row["pages_exact"] for row in load(PAGECOUNT)["channels"]}
    smoke = smoke_rows_per_channel()
    measured = sorted(
        (
            handle
            for handle, rows in smoke.items()
            if rows >= MEASURED_MIN_ROWS and handle in exact and handle != LEAFLET_CARRIER
        ),
        key=lambda handle: (-smoke[handle], handle),
    )
    head = [LEAFLET_CARRIER] if LEAFLET_CARRIER in exact else []
    rest = sorted(
        (handle for handle in exact if handle not in {*head, *measured}),
        key=lambda handle: (exact[handle], handle),
    )
    return head + measured + rest


def ordered(handles) -> list[str]:
    handles = set(handles)
    order = stage_order()
    return [one for one in order if one in handles] + sorted(handles - set(order))


# --- the population, read off the records --------------------------------------------------------


def pages() -> dict[str, list[dict]]:
    """``{handle: pages}`` in stage order, through the loop's own page source (`pages_of`)."""
    manifest = load(MANIFEST)
    handles = {entry["channel"] for entry in manifest["entries"].values()}
    return {handle: run_loop.pages_of(manifest, handle) for handle in ordered(handles)}


def posts() -> dict[str, list[dict]]:
    """``{handle: posts}`` — the census's pinned text price posts, read off the live store.

    Pinned by id, not by re-running the census's regex: the population is the registration's
    (SPEC 3.18 (4)). A pinned id the store does not hold is a moved input and a refusal.
    """
    store = live_store()
    out: dict[str, list[dict]] = {}
    for entry in load(CENSUS)["channels"]:
        wanted = {int(one) for one in entry["text_price_msg_ids"]}
        if not wanted:
            continue
        rows = {
            row["msg_id"]: {
                "channel": entry["channel"],
                "msg_id": row["msg_id"],
                "text": row["text"],
            }
            for row in store.rows("post", entry["channel"])
            if row["msg_id"] in wanted
        }
        if set(rows) != wanted:
            raise SystemExit(
                f"{entry['channel']}: {len(wanted - set(rows))} pinned text posts are not in the"
                " store — the population moved under the registration; refuse rather than re-derive"
            )
        out[entry["channel"]] = [rows[msg_id] for msg_id in sorted(rows)]
    return {handle: out[handle] for handle in ordered(out)}


def pages_sha256(by_channel: dict[str, list[dict]]) -> str:
    blob = "\n".join(
        f"{page['channel']}\x1f{page['msg_id']}\x1f{page['path']}"
        for handle in sorted(by_channel)
        for page in sorted(by_channel[handle], key=lambda one: one["msg_id"])
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def posts_sha256(by_channel: dict[str, list[dict]]) -> str:
    blob = "\n".join(
        f"{post['channel']}\x1f{post['msg_id']}"
        for handle in sorted(by_channel)
        for post in sorted(by_channel[handle], key=lambda one: one["msg_id"])
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def pages_match_the_pagecount(by_channel: dict[str, list[dict]]) -> list[str]:
    """Every channel's files on disk against the exact count the pagecount re-read. [] = match."""
    exact = {row["channel"]: row["pages_exact"] for row in load(PAGECOUNT)["channels"]}
    wrong = []
    for handle, want in exact.items():
        got = len(by_channel.get(handle, []))
        if got != want:
            wrong.append(f"{handle}: {got} pages on disk, {want} counted")
    return wrong


# --- rung 0: the whole step, priced before anything exists ----------------------------------------


def rates() -> dict:
    """Every rate the step is priced at, each naming the file it is read from. Nothing typed."""
    projection = load(PROJECTION)
    bound = projection["verdict"]["marginal_bound"]
    warmup = load(RUN_5C2)["go_no_go"]
    return {
        "rate_usd_per_second": float(projection["rate_usd_per_second"]),
        "page_lower": float(bound["seconds_per_page_lower"]),
        "page_upper": float(bound["seconds_per_page_upper"]),
        "page_from": f"{rel(PROJECTION)} :: verdict.marginal_bound (the smoke, n=30)",
        "page_realised_5c2": float(load(RUN_5C2)["timing"]["seconds_per_row"]),
        "page_realised_from": "results/run_5c2_positions.json :: timing.seconds_per_row"
        " (boot-inclusive, n=205 rows, 159 of them ATB leaflet pages)",
        "text_warmup": float(warmup["text_marginal_seconds"]),
        "text_warmup_from": "results/run_5c2_positions.json :: go_no_go.text_marginal_seconds (n=1)",
        "text_registered": float(load(PREREG_5C2)["prices"]["post_text"]["seconds_model"]["value"]),
        "text_registered_from": "results/prereg_5c2_run.json :: prices.post_text.seconds_model"
        " (skub2's text leg, n=30)",
        "page_registered": float(
            load(PREREG_5C2)["prices"]["leaflet_page"]["seconds_model"]["value"]
        ),
        "page_registered_from": "results/prereg_5c2_run.json :: prices.leaflet_page.seconds_model"
        " (skub2's last in-run gate, 108 pages) — sizes the packs, never the price",
        "boot_derived": float(bound["one_boot_seconds"]),
        "boot_derived_from": f"{rel(PROJECTION)} :: verdict.marginal_bound.one_boot_seconds",
        "boot_measured": float(load(SMOKE)["rung_0"]["boot_seconds_each"]),
        "boot_measured_from": "results/smoke_vision_c2.json :: rung_0.boot_seconds_each (srv-2c's"
        " slower boot)",
        "idle_tail_seconds": float(warmup["idle_tail_seconds"]),
    }


def corner(
    name: str, *, n_pages, n_posts, page_s, text_s, boots, boot_s, tail_s, rate, cap
) -> dict:
    seconds = n_pages * page_s + n_posts * text_s + boots * boot_s + tail_s
    usd = round(seconds * rate, 4)
    return {
        "name": name,
        "page_seconds": page_s,
        "text_seconds": text_s,
        "boots": boots,
        "boot_seconds_each": boot_s,
        "idle_tail_seconds": tail_s,
        "billable_seconds": round(seconds, 3),
        "usd": usd,
        "cap_usd": cap,
        "fits": usd <= cap,
        "over_cap_by": round(usd / cap - 1, 4),
    }


def rung_0(n_pages: int, n_posts: int, cap: float | None = None) -> dict:
    """The whole step at three measured corners, and the realised 5c2 rate beside them.

    `results/promo_projection_c2.json` priced the VISION leg at the dear end of the smoke's marginal
    plus one boot — `c2_priced_usd`, the number the cap was set from. The step buys the text leg too
    and pays whatever boots at creation, so the table here is that price plus what it left out,
    at the same corners. The verdict is the DEAR corner's, for the projection's own reason: the
    guard's `spend()` is the pessimistic max and a cap blown after the money is spent cannot be
    un-spent.
    """
    # The cap is read at CALL time. A default bound at import freezes the C2 number into every leg
    # that re-points STEP_CAP_USD, and the freeze is invisible: the table still prints a verdict.
    cap = STEP_CAP_USD if cap is None else cap
    r = rates()
    common = {"n_pages": n_pages, "n_posts": n_posts, "rate": r["rate_usd_per_second"], "cap": cap}
    table = [
        corner(
            "cheap — the marginal's lower end, the text warm-up, one derived boot",
            page_s=r["page_lower"],
            text_s=r["text_warmup"],
            boots=1,
            boot_s=r["boot_derived"],
            tail_s=r["idle_tail_seconds"],
            **common,
        ),
        corner(
            "priced — the projection's own corner (upper marginal + one derived boot) plus the"
            " text leg at its registered rate",
            page_s=r["page_upper"],
            text_s=r["text_registered"],
            boots=1,
            boot_s=r["boot_derived"],
            tail_s=r["idle_tail_seconds"],
            **common,
        ),
        corner(
            "dear — the upper marginal, the registered text rate, two measured boots (the smoke's"
            " rung 0: something boots at creation and the first job may boot again)",
            page_s=r["page_upper"],
            text_s=r["text_registered"],
            boots=2,
            boot_s=r["boot_measured"],
            tail_s=r["idle_tail_seconds"],
            **common,
        ),
    ]
    realised = corner(
        "READING, not a corner — the vision leg at 5c2's realised boot-inclusive rate on ATB"
        " leaflet pages; the projection's table carries it as `realised_5c2`",
        page_s=r["page_realised_5c2"],
        text_s=r["text_registered"],
        boots=0,
        boot_s=0.0,
        tail_s=r["idle_tail_seconds"],
        **common,
    )
    dear = table[-1]
    return {
        "rule": "docs/PROCESS.md «Money» rung (0): price at create ≤ the registered ceiling — the"
        " ceiling is the step cap, the price is the DEAR corner",
        "pages": n_pages,
        "posts": n_posts,
        "cap_usd": cap,
        "cap_from": STEP_CAP_FROM,
        "rates": r,
        "table": table,
        "realised_5c2": realised,
        "priced_usd": table[1]["usd"],
        "dear_usd": dear["usd"],
        "fits": dear["fits"],
        "fits_at_the_priced_corner": table[1]["fits"],
        "fits_at_the_cheap_corner": table[0]["fits"],
        "over_cap_by_at_the_dear_corner": dear["over_cap_by"],
    }


def render_rung_0(verdict: dict) -> str:
    lines = [
        f"rung 0 — {verdict['pages']} pages + {verdict['posts']} posts against the step cap"
        f" ${verdict['cap_usd']:.2f}",
        f"{'corner':<10}{'page s':>8}{'text s':>8}{'boots':>7}{'seconds':>10}{'usd':>9}  fits",
    ]
    for row in [*verdict["table"], verdict["realised_5c2"]]:
        lines.append(
            f"{row['name'].split(' ')[0]:<10}{row['page_seconds']:>8.3f}{row['text_seconds']:>8.3f}"
            f"{row['boots']:>7}{row['billable_seconds']:>10.1f}{row['usd']:>9.4f}"
            f"  {'yes' if row['fits'] else 'NO':<4} ({row['over_cap_by']:+.1%})"
        )
    lines.append(f"verdict: {'FITS' if verdict['fits'] else 'DOES NOT FIT'} at the dear corner")
    return "\n".join(lines)


# --- the registration -----------------------------------------------------------------------------


def register() -> dict:
    leg = CENSUS.stem.rsplit("_", 1)[-1].upper()  # promo_census_c2.json → C2, _c3 → C3
    page_queue, post_queue = pages(), posts()
    wrong = pages_match_the_pagecount(page_queue)
    if wrong:
        raise SystemExit("the pages on disk are not the pagecount's: " + "; ".join(wrong))
    n_pages = sum(len(rows) for rows in page_queue.values())
    n_posts = sum(len(rows) for rows in post_queue.values())
    record = {
        "phase": f"promo-pulse-1 S4 — the {leg} backfill (PAID): vision for the census's pages,"
        " text for its price posts",
        "authority": "docs/reviews/2026-08-30-plan-promo-pulse-1.md «Ruling 02.09 (b)» — «STEP_CAP_USD"
        " = 3.95 … the guard's step anchor with --step promo-pulse-1 --step-cap 3.95 … The text leg"
        " runs FIRST … Mid-run: no cap raise, ever» — and «Ruling 02.09 (c)»: «Per leg — yes … Per"
        " channel, measured by the channel's own first pack … The whole-step page projection is"
        " RETIRED for this step»; docs/plans/promo-pulse-1.md S4, SP-1b",
        "step": {
            "name": STEP,
            "cap_usd": STEP_CAP_USD,
            "ledger": f"results/spend_{STEP.replace('-', '_')}.json",
        },
        "pinned_inputs": {rel(path): sha256_of(path) for path in pinned()},
        "population": {
            "pages": {
                "total": n_pages,
                "by_channel": {handle: len(rows) for handle, rows in page_queue.items()},
                "ids_sha256": pages_sha256(page_queue),
                "source": f"{rel(MANIFEST)} through run_loop.pages_of — the census's pinned"
                " media posts, one file per photo member, counted against"
                f" {rel(PAGECOUNT)} :: pages_exact per channel",
            },
            "posts": {
                "total": n_posts,
                "by_channel": {handle: len(rows) for handle, rows in post_queue.items()},
                "ids_sha256": posts_sha256(post_queue),
                "source": f"{rel(CENSUS)} :: channels[].text_price_msg_ids, read off"
                " the live store (v1 ∪ r2)",
            },
            "order": ordered(set(page_queue) | set(post_queue)),
            "order_from": "ruling 02.09 (c) §3, the operator's «АТБ → дешёвые → малые», DERIVED:"
            " the leaflet carrier, then the channels the smoke measured (>= 2 of its 30 pages,"
            " most-measured first, results/prereg_smoke_vision_c2.json), then the rest ascending"
            f" by {rel(PAGECOUNT)} :: pages_exact",
            "stage_0": "post_text — every channel's text posts BEFORE any page (ruling 02.09 (b)),"
            " gated on its own (10)(a) projection (ruling 02.09 (c) item 1)",
        },
        "expected_worker": load(POSITIONS_PIN)["expected_worker"],
        "expected_worker_from": "results/sku_pilot_serving_v2.json — the pin run_5c2 and the smoke"
        " assert",
        "rung_0": rung_0(n_pages, n_posts),
        "in_run_gates": {
            "go_no_go": "SPEC 3.17 (10)(a) PER LEG (ruling 02.09 (c) item 1): after two warm-ups on"
            f" REPRESENTATIVE inputs — the first queued {leg} page and the first queued {leg} post"
            " — the"
            " TEXT leg alone is projected at its own measured marginal and no gold call is made if"
            " IT exceeds what is left of the step cap; the page leg is never priced as one step",
            "per_channel": "ruling 02.09 (c) item 2: the channel's own first pack is its"
            " measurement (worker seconds ÷ pages written, one row per channel in"
            " results/measurements.jsonl); its remainder is projected at THAT rate against the"
            " room (cap − step spent − one wedged job − the idle tail) — fits → the channel runs"
            " whole, does not → the remainder is left unbought and the next channel starts; the"
            " run ends when the room is below one pack at the worst measured rate",
            "stage_projection": "after EVERY channel, positions_gm4_skub.projection at the blended"
            " marginal — a READING for the record and the STOP's table, no longer a gate: ruling"
            " 02.09 (c) retires the whole-step page projection",
            "cap_gate": "SPEC 3.17 (10)(c), per pack: refuse the next job when what is left of"
            f" the cap cannot absorb one job at the {skub.JOB_TIMEOUT_S:.0f} s execution timeout",
            "packs": f"bytes first ({skub.MAX_PAYLOAD_MB} MB, RunPod's /run refuses 10 MiB), then"
            " the count the pessimistic marginal allows inside the timeout",
        },
        "kill_rules": [
            "the dear corner of rung 0 does not fit the step cap → nothing is created (STOP)",
            f"the guard refuses --step {STEP} --step-cap {STEP_CAP_USD:.2f} → that is the answer",
            "mid-run the cap is never raised: the text leg's (10)(a) gate, the per-channel room"
            " and the per-pack cap gate decide (ruling 02.09 (b) item 3, (c) item 2)",
            "a channel whose remainder does not fit the room is skipped WHOLE — never half a"
            " channel, and never a cap stretched to finish one (ruling 02.09 (c) item 2(b))",
            "info disagrees with expected_worker → tear down, send nothing, record the difference",
            "two boots without a served info → KILL, do not try a third",
            "the (10)(a) gate refuses → no gold call, tear down, record the measured marginals",
            "a job ends TIMED_OUT → the run ends with its unbought remainder recorded",
        ],
        "teardown": "runpodctl serverless delete <endpoint> && runpodctl template delete"
        " <template>, proven by `runpodctl serverless list` → [] and `runpodctl template list"
        " --type user` → the endpoint's template gone, with `runpodctl network-volume list` →"
        " mp-srv2 (qw4nwleanc) still listed as the positive control",
        "recovery_clause": "one re-create of the SAME endpoint within the same step cap if the"
        " first boot dies without serving info; an interrupted run is re-entered with a second"
        " --run under the same step — the derived store's markers subtract what was answered",
    }
    PREREG.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return record


WINDOW_ID = "w2"
"""The aggregate id of the window this registration bought — `windows.window_id`, ruling 02.09 (d)
item 1 («the executor picks it and says so in the record»). `w1` stays 5c2's. A NAME and not a date,
for the reason `build_aggregates.WINDOW_ID` gives: `windows.anchor` already carries the date."""

REGISTRY = REPO_ROOT / "config" / "registry.yaml"


def register_addendum() -> dict:
    """Ruling 02.09 (d) item 1 — the registry this run bought under, ADDED to a sealed record.

    An addendum and not a re-registration: `register()` would recompute every rate and population
    against today's files and silently re-pin what the run was judged on. This adds the ONE key the
    ruling names and refuses to touch a key that is already there, so the sealed half stays sealed
    ([[a_self_pinning_producer_cannot_grow_a_parameter]]). The field is DATED, so the record says
    when the pin joined it rather than reading as if it had always been there.
    """
    prereg = load(PREREG)
    key = rel(REGISTRY)
    if key in prereg["pinned_inputs"]:
        raise SystemExit(
            f"{rel(PREREG)} already pins {key} as {prereg['pinned_inputs'][key][:16]}… — an"
            " addendum adds, it never re-pins. If the registry moved, that is a refusal for the"
            " team lead, not a rewrite here."
        )
    prereg["pinned_inputs"][key] = sha256_of(REGISTRY)
    prereg["addendum"] = [
        {
            "dated": "2026-09-03",
            "authority": "docs/reviews/2026-08-30-plan-promo-pulse-1.md «Ruling 02.09 (d)» item 1"
            " — «It pins the registry it was bought under … added to pinned_inputs by the"
            " registration's own writer … never re-pinning what is already there»",
            "added": [key],
            "window_id": WINDOW_ID,
            "why": "the C2 window is aggregated through ITS OWN seal, and the segment join is a"
            " join to a set of channels: without this pin the window would be built against"
            " whatever registry the checkout happens to hold",
        }
    ]
    PREREG.write_text(
        json.dumps(prereg, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return prereg


def preflight(prereg: dict) -> dict:
    """Every pinned input still reads as the registration pinned it. A moved one is a stop."""
    moved = {
        path: (pinned, sha256_of(REPO_ROOT / path))
        for path, pinned in prereg["pinned_inputs"].items()
        if sha256_of(REPO_ROOT / path) != pinned
    }
    if moved:
        raise SystemExit(
            "pinned inputs moved since the registration — refuse rather than re-derive: "
            + "; ".join(f"{path} {was[:12]}… → {now[:12]}…" for path, (was, now) in moved.items())
        )
    return dict(prereg["pinned_inputs"])


# --- the served half ------------------------------------------------------------------------------


def guard_says_go() -> tuple[int, float]:
    """Rung 0 in the guard's own words, and what the STEP has already spent.

    Ruling 02.09 (c) prices every channel against «cap − step spent», so the run needs a number for
    what earlier runs of this step took. It is the guard's, read off its own printed line and never
    re-derived here: a run that cannot find that line refuses, because a missing prior reads as
    zero and hands this run a cap it does not have.
    """
    done = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "runpod_guard.py"),
            "--step",
            STEP,
            "--step-cap",
            f"{STEP_CAP_USD:.2f}",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    print(done.stdout, end="", flush=True)
    print(done.stderr, end="", file=sys.stderr, flush=True)
    if done.returncode != 0:
        return done.returncode, 0.0
    spent = re.search(rf"{re.escape(STEP.upper())} (?:SPENT|CLOSED)\s+\$([0-9.]+) of", done.stdout)
    if not spent:
        raise SystemExit(
            f"the guard printed no '{STEP.upper()} SPENT $… of' line — the step's prior spend is"
            " unreadable and a missing prior reads as $0.00. Refuse rather than run on it."
        )
    return 0, float(spent.group(1))


def room(*, cap_left: float, billed: float, rate: float, reserve: float) -> float:
    """What may still be spent on ROWS — ruling 02.09 (c) item 2(b).

    «cap − step spent − the one-job reserve − the idle tail», with the step's earlier runs already
    out of `cap_left`. The reserve is `cap_gate`'s wedged job, so the room and the hard per-pack
    gate cannot disagree about what one job can cost; the tail is charged once the last job ends
    and is therefore owed before it is spent.
    """
    return cap_left - billed * rate - reserve - skub.IDLE_TAIL_SECONDS * rate


def stage_projection(client, *, opened: float, done: int, total: int, rate: float, cap: float):
    """A READING after every channel, no longer a gate (ruling 02.09 (c) retires the whole-step
    page projection): one blended rate over 17 channels lies in both directions."""
    reading = skub.projection(
        opened_seconds=opened, billed=fivec2.billed_now(client), done=done, total=total, rate=rate
    )
    reading["cap_usd"] = cap
    reading["over_cap"] = reading["projected_usd"] > cap
    return reading


def run_the_legs(
    *, outcome, note, client, prereg, page_queue, post_queue, derived, cursor, rate, drift, cap
):
    registry = load_registry(run_loop.REGISTRY)
    categories = positions.category_keys(registry.taxonomy)
    aliases = watchlist_aliases(registry.watchlist)
    endpoint = client.endpoint_id

    info = serving.assert_serving(client.info(), prereg["expected_worker"])
    revision = info.get("revision_requested")
    outcome["info"] = info

    queued_pages = {
        handle: loop.queued_pages(
            rows, derived, handle, loop.channel_state(cursor, handle).get(loop.LEAFLET)
        )
        for handle, rows in page_queue.items()
    }
    queued_posts = {
        handle: loop.queued_posts(
            rows, derived, handle, loop.channel_state(cursor, handle).get(loop.POST_TEXT)
        )
        for handle, rows in post_queue.items()
    }
    n_pages = sum(len(rows) for rows in queued_pages.values())
    n_posts = sum(len(rows) for rows in queued_posts.values())
    outcome["queued"] = {"pages": n_pages, "posts": n_posts}
    first_page = next((rows[0] for rows in queued_pages.values() if rows), None)
    first_post = next((rows[0] for rows in queued_posts.values() if rows), None)
    if first_page is None and first_post is None:
        note.append("nothing queued — every registered row is already answered on disk")
        return

    # The two warm-ups of 3.17 (10)(a) on REPRESENTATIVE inputs, answered OUTSIDE the passes so no
    # evidence row is written; the same rows are asked again inside their pass (~$0.003).
    page_seconds = text_seconds = 0.0
    if first_page is not None:
        album = loop.render_page(loop.page_file(first_page))[2]
        _, page_seconds = fivec2.measure(client, lambda: client.positions(loop.PAGE_TASK, [album]))
    if first_post is not None:
        payload = loop.render_post(first_post)[1]
        _, text_seconds = fivec2.measure(
            client, lambda: client.positions(loop.POST_TASK, [payload])
        )
    opened = fivec2.billed_now(client)
    # (10)(a) PER LEG — ruling 02.09 (c) item 1. The text leg is priced from its OWN warm-up and its
    # own rows, and is never refused for the page leg: `n_pages=0` is the law here, not an empty
    # queue. The pages are gated per channel below, each at the rate its own first pack measures.
    gate = skub.go_no_go(
        billed=opened,
        page_marginal=page_seconds,
        text_marginal=text_seconds,
        n_pages=0,
        n_rows=n_posts,
        rate=rate,
        budget=cap,
    )
    gate["leg"] = (
        "post_text — ruling 02.09 (c) item 1: this gate prices the TEXT leg alone (n_pages = 0 by"
        " the law); the page legs gate per channel against the room, never as one step"
    )
    gate["page_warmup_seconds"] = round(page_seconds, 4)
    gate["over_cap_by"] = round(gate["projected_usd"] / cap - 1, 4)
    outcome["go_no_go"] = gate
    print(json.dumps(gate, indent=1), flush=True)
    if gate["refuse"]:
        note.append(
            f"REFUSED at the (10)(a) gate of the TEXT leg — projected ${gate['projected_usd']:.4f}"
            f" against the ${cap:.4f} left of the step cap ({gate['over_cap_by']:+.1%}); no gold"
            " call was made"
        )
        # Ruling 02.09 (b) item 3: a stop on ANY gate records what is left, for the STOP's table.
        outcome["unbought"] = unbought(prereg, queued_pages, queued_posts, derived, cursor)
        return

    registered = load(PREREG_5C2)["prices"]
    page_registered = float(registered["leaflet_page"]["seconds_model"]["value"])
    text_registered = float(registered["post_text"]["seconds_model"]["value"])
    total = n_pages + n_posts
    done = 0
    reserve = fivec2.worst_case_job_usd(rate, drift)
    size = fivec2.pack_size(page_seconds, page_registered)
    outcome["leaflet"], outcome["stages"], outcome["measured"] = [], [], {}
    outcome["room"] = {
        "rule": "ruling 02.09 (c) item 2(b): cap − step spent − one wedged job − the idle tail",
        "cap_left_usd": round(cap, 4),
        "reserve_usd": reserve,
        "idle_tail_usd": round(skub.IDLE_TAIL_SECONDS * rate, 4),
        "pack_pages_by_count": size,
        "pack_note": "the COUNT bound; bytes bind first (8 MB), so a real pack is smaller and the"
        " pre-channel check below refuses early rather than late",
    }

    def left() -> float:
        return room(cap_left=cap, billed=fivec2.billed_now(client), rate=rate, reserve=reserve)

    # Stage 0 — the TEXT leg first (ruling 02.09 (b)): the cheapest, surest, cross-chain data is
    # bought before the dearest, so a gate that stops the run stops it on pages, not on posts.
    before = len(note)
    outcome["post_text"] = fivec2.post_leg(
        client,
        fivec2.SliceTransport(fivec2.text_key),
        {handle: rows for handle, rows in queued_posts.items() if rows},
        derived=derived,
        cursor=cursor,
        categories=categories,
        aliases=aliases,
        revision=revision,
        endpoint=endpoint,
        marginal=text_seconds,
        registered_marginal=text_registered,
        cap=cap,
        rate=rate,
        drift=drift,
        note=note,
    )
    done += sum(pack["posts_read"] for pack in outcome["post_text"])
    reading = stage_projection(client, opened=opened, done=done, total=total, rate=rate, cap=cap)
    outcome["stages"].append({"after": "post_text"} | reading | {"room_usd": round(left(), 4)})
    print(f"  after post_text: {reading}", flush=True)
    if len(note) > before:
        note.append("the run STOPPED at post_text: the cap gate refused a pack")
        outcome["unbought"] = unbought(prereg, queued_pages, queued_posts, derived, cursor)
        return

    for handle in prereg["population"]["order"]:
        rows = queued_pages.get(handle) or []
        if not rows:
            continue
        # (c) item 2(c): the run ends when the room is below one pack at the WORST rate measured so
        # far — the page warm-up seeds it for the first channel and nothing after that.
        worst = max([*outcome["measured"].values(), page_seconds])
        before_room, one_pack = left(), size * worst * rate
        if before_room < one_pack:
            note.append(
                f"the run ENDS before {handle}: ${before_room:.4f} of room is below one pack"
                f" ({size} pages at the worst measured {worst:.3f} s/page = ${one_pack:.4f})"
            )
            break
        entry = channel_leg(
            client,
            rows,
            handle=handle,
            size=size,
            note=note,
            derived=derived,
            cursor=cursor,
            categories=categories,
            aliases=aliases,
            revision=revision,
            endpoint=endpoint,
            page_registered=page_registered,
            cap=cap,
            rate=rate,
            drift=drift,
            room_before=before_room,
            room_after=left,
        )
        outcome["leaflet"].append(entry)
        if entry["measured_seconds_per_page"] is not None:
            outcome["measured"][handle] = entry["measured_seconds_per_page"]
            measurements.append(
                {
                    "contract": f"{STEP}-s4",
                    "name": f"page_seconds_{handle.lstrip('@')}",
                    "value": entry["measured_seconds_per_page"],
                    "max": entry["measured_seconds_per_page"],
                    "unit": "seconds",
                    "n": entry["measured_n"],
                    "source": rel(RECORD),
                    "instrument": "the channel's OWN first pack (ruling 02.09 (c) item 2(a)): one"
                    " job, worker seconds ÷ pages written; value and max are one aggregate, as the"
                    " smoke's vision_seconds_per_page row is",
                    "measured_on": f"{handle}, {entry['measured_n']} pages, endpoint {endpoint},"
                    " POSITIONS serving, thinking OFF",
                },
                ledger=MEASUREMENTS,
            )
        done += entry["pages_bought"]
        reading = stage_projection(
            client, opened=opened, done=done, total=total, rate=rate, cap=cap
        )
        outcome["stages"].append({"after": handle} | reading | {"room_usd": round(left(), 4)})
        print(f"  after {handle}: {reading}", flush=True)
        if entry["stopped"]:
            note.append(f"the run STOPPED at {handle}: the cap gate refused a pack")
            break
    outcome["unbought"] = unbought(prereg, queued_pages, queued_posts, derived, cursor)


def channel_leg(
    client,
    rows,
    *,
    handle,
    size,
    note,
    derived,
    cursor,
    categories,
    aliases,
    revision,
    endpoint,
    page_registered,
    cap,
    rate,
    drift,
    room_before,
    room_after,
):
    """ONE channel under ruling 02.09 (c) item 2: its first pack, its rate, then all or nothing.

    The first pack is the channel's measurement (`worker seconds ÷ pages written`) and the rest of
    the channel is projected at THAT rate against the room. It fits → the channel runs whole; it
    does not → the remainder is left unbought and named, and the caller moves to the next channel.
    `fivec2.page_leg` buys both halves, so the pack is cut here exactly once, by the transport's own
    packer, and the two calls see one pack and the remainder of the same cut.
    """
    packs = fivec2.page_packs(rows, size)
    first = [item["page"] for item in packs[0]]
    rest = [item["page"] for pack in packs[1:] for item in pack]
    del packs  # the rendered albums; `page_leg` renders the halves it is given
    leg = dict(
        channel=handle,
        pages_queued=len(rows),
        pages_bought=0,
        pages_left=len(rows),
        measured_seconds_per_page=None,
        measured_n=len(first),
        remainder_pages=len(rest),
        remainder_usd_at_its_rate=None,
        remainder_bought=False,
        room_usd_before=round(room_before, 4),
        packs=[],
        stopped=False,
    )

    def buy(half: list[dict]) -> float:
        before_note, before_seconds = len(note), skub.billed_seconds(client)
        bought = fivec2.page_leg(
            client,
            fivec2.SliceTransport(fivec2.album_key),
            half,
            derived=derived,
            cursor=cursor,
            categories=categories,
            aliases=aliases,
            revision=revision,
            endpoint=endpoint,
            marginal=leg["measured_seconds_per_page"] or page_registered,
            registered_marginal=page_registered,
            cap=cap,
            rate=rate,
            drift=drift,
            note=note,
        )
        leg["stopped"] = leg["stopped"] or len(note) > before_note
        # Both halves come off ONE cut, so the packs are numbered across the channel and not per
        # call — a record with two `pack: 0` rows would read as two cuts of the same pages.
        first_index = len(leg["packs"])
        leg["packs"].extend(
            dict(pack, pack=first_index + index) for index, pack in enumerate(bought["packs"])
        )
        leg["pages_bought"] = sum(pack["pages_written"] for pack in leg["packs"])
        leg["pages_left"] = leg["pages_queued"] - leg["pages_bought"]
        return skub.billed_seconds(client) - before_seconds

    seconds = buy(first)
    if not leg["pages_bought"]:
        return leg
    leg["measured_seconds_per_page"] = round(seconds / leg["pages_bought"], 4)
    leg["measured_n"] = leg["pages_bought"]
    print(
        f"  {handle}: measured {leg['measured_seconds_per_page']:.3f} s/page on its first pack"
        f" (n={leg['measured_n']})",
        flush=True,
    )
    if not rest or leg["stopped"]:
        leg["remainder_bought"] = not rest
        return leg
    need = len(rest) * leg["measured_seconds_per_page"] * rate
    room_now = room_after()
    leg["remainder_usd_at_its_rate"] = round(need, 4)
    leg["room_usd_after_first_pack"] = round(room_now, 4)
    if need > room_now:
        note.append(
            f"{handle}: {len(rest)} pages left UNBOUGHT — ${need:.4f} at the measured"
            f" {leg['measured_seconds_per_page']:.3f} s/page against ${room_now:.4f} of room"
            " (SPEC 3.17 (10)(b); ruling 02.09 (c) item 2(b): the channel is skipped whole)"
        )
        return leg
    buy(rest)
    leg["remainder_bought"] = not leg["stopped"]
    return leg


def unbought(prereg: dict, page_queue: dict, post_queue: dict, derived, cursor) -> dict:
    """What the registration named and this run did not answer — re-read off the disk, per channel."""
    out = {"pages": {}, "posts": {}}
    for handle, rows in page_queue.items():
        left = loop.queued_pages(
            rows, derived, handle, loop.channel_state(cursor, handle).get(loop.LEAFLET)
        )
        if left:
            out["pages"][handle] = len(left)
    for handle, rows in post_queue.items():
        left = loop.queued_posts(
            rows, derived, handle, loop.channel_state(cursor, handle).get(loop.POST_TEXT)
        )
        if left:
            out["posts"][handle] = len(left)
    out["pages_total"] = sum(out["pages"].values())
    out["posts_total"] = sum(out["posts"].values())
    return out


def finalise(outcome: dict, note: list, client, rate: float) -> None:
    """The run record, on EVERY exit that could have billed. The ledger is the guard's."""
    timing = client.timing()
    outcome["timing"] = timing
    outcome["billed_usd_at_the_rate"] = round(
        max(float(timing.get("worker_seconds") or 0.0), float(timing.get("wall_seconds") or 0.0))
        * rate,
        4,
    )
    outcome["notes"] = note
    outcome["at"] = datetime.now(UTC).isoformat(timespec="seconds")
    record = load(RECORD) if RECORD.exists() else {"runs": []}
    record["runs"].append(outcome)
    RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {rel(RECORD)} (run {len(record['runs'])})")


def repoint(args) -> None:
    """Point this module's files, ledger line and cap at ONE leg — parameters, not siblings.

    Ruling 04.09 (l) item 2: the c3 leg is this producer with `--out` / `--channels` / `--anchor` /
    `--prereg` / `--step` / `--cap`, writing `results/*_c3.json` under its own registration and its
    own ledger `promo-c3`. Every reader below takes these off the module, so one rebinding before
    the dispatch is the whole change; nothing re-runs C2, whose result files stay as sealed.
    """
    global PREREG, RECORD, CENSUS, PAGECOUNT, PROJECTION, MANIFEST, STEP, STEP_CAP_USD
    global STEP_CAP_FROM
    PREREG, RECORD = args.prereg, args.record
    CENSUS, PAGECOUNT = args.census, args.pagecount
    PROJECTION, MANIFEST = args.projection, args.manifest
    if args.cap != STEP_CAP_USD:  # read BEFORE the rebind: the import-time constant is (b)'s number
        STEP_CAP_FROM = (
            "the leg's runbook §0 command (`--cap`) — derived in the paid session from the guard's"
            " own REMAINING line, never carried from a document"
        )
    STEP, STEP_CAP_USD = args.step, args.cap


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", action="store_true", help="$0: write the pre-registration")
    parser.add_argument(
        "--register-addendum",
        action="store_true",
        help="$0: add the registry pin + window id to the sealed registration (ruling 02.09 (d))",
    )
    parser.add_argument("--dry-run", action="store_true", help="$0: selections, hashes, rung 0")
    parser.add_argument("--run", action="store_true", help="the PAID leg")
    parser.add_argument("--endpoint", help=f"the serving endpoint id (or ${ENDPOINT_ENV})")
    parser.add_argument("--prereg", type=Path, default=PREREG, help="the leg's registration")
    parser.add_argument("--record", type=Path, default=RECORD, help="the leg's run record")
    parser.add_argument("--census", type=Path, default=CENSUS)
    parser.add_argument("--pagecount", type=Path, default=PAGECOUNT)
    parser.add_argument("--projection", type=Path, default=PROJECTION)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--step", default=STEP, help="the ledger line this leg spends on")
    parser.add_argument("--cap", type=float, default=STEP_CAP_USD, help="the step's cap, USD")
    args = parser.parse_args(argv)
    repoint(args)

    if args.register:
        record = register()
        print(render_rung_0(record["rung_0"]))
        print(f"wrote {rel(PREREG)}")
        return 0

    if args.register_addendum:
        prereg = register_addendum()
        key = rel(REGISTRY)
        print(f"{rel(PREREG)} :: pinned_inputs[{key}] = {prereg['pinned_inputs'][key]}")
        print(f"{rel(PREREG)} :: addendum[0].window_id = {prereg['addendum'][0]['window_id']}")
        return 0

    if args.dry_run:
        page_queue, post_queue = pages(), posts()
        wrong = pages_match_the_pagecount(page_queue)
        n_pages = sum(len(rows) for rows in page_queue.values())
        n_posts = sum(len(rows) for rows in post_queue.values())
        print(f"  stage  0  {'post_text':<24} posts {n_posts:>4}   (every channel, FIRST)")
        for index, handle in enumerate(ordered(set(page_queue) | set(post_queue)), 1):
            print(
                f"  stage {index:>2}  {handle:<24} pages {len(page_queue.get(handle, [])):>5}"
                f"  posts {len(post_queue.get(handle, [])):>4}"
            )
        print(
            f"pages {n_pages} ({pages_sha256(page_queue)[:16]}…) · posts {n_posts} ({posts_sha256(post_queue)[:16]}…)"
        )
        print("pagecount: " + ("match" if not wrong else "; ".join(wrong)))
        print(render_rung_0(rung_0(n_pages, n_posts)))
        print("--dry-run: no client built, nothing sent, nothing written")
        return 0 if not wrong else 2

    if not args.run:
        parser.error("choose --register, --register-addendum, --dry-run or --run")

    prereg = load(PREREG)
    preflight(prereg)
    if not prereg["rung_0"]["fits"]:
        raise SystemExit(
            f"rung 0: the dear corner is ${prereg['rung_0']['dear_usd']:.4f} against the"
            f" ${STEP_CAP_USD:.2f} step cap — STOP; nothing is created and the cap is not raised"
            " to fit a run"
        )
    endpoint = args.endpoint or os.environ.get(ENDPOINT_ENV)
    api_key = os.environ.get(API_KEY_ENV)
    if not endpoint or not api_key:
        raise SystemExit(f"--endpoint (or ${ENDPOINT_ENV}) and ${API_KEY_ENV} are both required")
    returncode, prior = guard_says_go()
    if returncode != 0:
        raise SystemExit("the guard refuses — that is the answer, not an obstacle")

    page_queue, post_queue = pages(), posts()
    if pages_sha256(page_queue) != prereg["population"]["pages"]["ids_sha256"]:
        raise SystemExit("the page selection moved since the registration — refuse")
    if posts_sha256(post_queue) != prereg["population"]["posts"]["ids_sha256"]:
        raise SystemExit("the post selection moved since the registration — refuse")

    rate = float(prereg["rung_0"]["rates"]["rate_usd_per_second"])
    drift = float(load(PREREG_5C2)["drift"]["factor"])
    cap = float(prereg["step"]["cap_usd"])
    # Ruling 02.09 (c): every gate below prices against «cap − step spent», so what run 1 took is
    # out of the cap before the first job — not left for the ledger to discover afterwards.
    cap_left = round(cap - prior, 4)
    print(f"step cap ${cap:.2f} − ${prior:.4f} already spent = ${cap_left:.4f} for this run")
    client = fivec2.client_for(endpoint, api_key)
    # Ruling 03.09 (b) fork 1: C2 writes under its OWN root. The sealed w1 root is passed as an
    # archive so the dedupe still sees what window 1 already answered — a re-run must not re-buy
    # a page because its evidence row now lives one directory over.
    derived = RawStore(run_loop.LIVE_DERIVED_ROOT, archives=(run_loop.DERIVED_ROOT,))
    cursor = loop.load_cursor(run_loop.CURSOR)
    note: list[str] = []
    outcome = {
        "phase": prereg["phase"],
        "authority": rel(PREREG),
        "endpoint": endpoint,
        "step": prereg["step"] | {"spent_before_this_run_usd": prior, "cap_left_usd": cap_left},
    }
    try:
        run_the_legs(
            outcome=outcome,
            note=note,
            client=client,
            prereg=prereg,
            page_queue=page_queue,
            post_queue=post_queue,
            derived=derived,
            cursor=cursor,
            rate=rate,
            drift=drift,
            cap=cap_left,
        )
    except BaseException as err:  # noqa: BLE001 — the record outranks the reason (run_5c2's rule)
        outcome["died"] = f"{type(err).__name__}: {err}"
        note.append(f"the run ENDED on an exception: {type(err).__name__}")
        finalise(outcome, note, client, rate)
        raise
    finalise(outcome, note, client, rate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
