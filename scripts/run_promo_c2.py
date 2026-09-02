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
(2) the (10)(a) gate after two representative warm-ups (a real C2 page, a real C2 post); then the
TEXT leg first — stage 0, the cheapest, surest, cross-chain data (ruling 02.09 (b)) — and a
re-projection after it and after EVERY channel at the measured marginal; over the cap → the run
stops at that boundary and the unbought channels are recorded (silence = KILL: nobody can be asked
mid-run; the cap is never raised mid-run). (3) the per-pack `cap_gate`: no job may be capable of
billing past the remaining cap.

    python3.11 scripts/run_promo_c2.py --register                        # $0: the registration
    PYTHONPATH=src python3.11 scripts/run_promo_c2.py --dry-run          # $0: selections, hashes
    PYTHONPATH=src python3.11 scripts/run_promo_c2.py --run --endpoint <id>   # PAID
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

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


def pinned() -> tuple[Path, ...]:
    """The inputs the registration hashes — read at call time, so a test can point them elsewhere."""
    return (CENSUS, PAGECOUNT, PROJECTION, MANIFEST, POSITIONS_PIN, PREREG_5C2, RUN_5C2, SMOKE)


ORDER = (
    "@atb_market_official",
    "@ATB_FANatik",
    "@atb_aktsiyi",
    "@VARUS_channel",
    "@ekomarket_shop",
    "@epicentrk_sale",
    "@forainfo",
    "@marketopt_promo",
    "@blyzenkoua",
    "@silposilpo",
    "@fozzyshopua",
    "@sim23_simi",
    "@rrozetka",
    "@msuaaaa",
    "@kop1chat",
    "@znishkom",
    "@xochydeshevshe",
)
"""Stages in VALUE order (PROCESS «Money»): the operator's confirmed A1 list of
`docs/PHASE-promo-pulse-1.md` §3, in its printed order — a channel the census carries that the
list does not (`@kopiyochka1`, an A2 voice) follows it, sorted. A completed channel is a usable
number; the order is the spec's, not a ranking invented here."""

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


def ordered(handles) -> list[str]:
    handles = set(handles)
    return [one for one in ORDER if one in handles] + sorted(handles - set(ORDER))


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
        "page_from": "results/promo_projection_c2.json :: verdict.marginal_bound (the smoke, n=30)",
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
        "boot_derived_from": "results/promo_projection_c2.json :: verdict.marginal_bound.one_boot_seconds",
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


def rung_0(n_pages: int, n_posts: int, cap: float = STEP_CAP_USD) -> dict:
    """The whole step at three measured corners, and the realised 5c2 rate beside them.

    `results/promo_projection_c2.json` priced the VISION leg at the dear end of the smoke's marginal
    plus one boot — `c2_priced_usd`, the number the cap was set from. The step buys the text leg too
    and pays whatever boots at creation, so the table here is that price plus what it left out,
    at the same corners. The verdict is the DEAR corner's, for the projection's own reason: the
    guard's `spend()` is the pessimistic max and a cap blown after the money is spent cannot be
    un-spent.
    """
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
        "cap_from": "docs/reviews/2026-08-30-plan-promo-pulse-1.md «Ruling 02.09 (b)»",
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
    page_queue, post_queue = pages(), posts()
    wrong = pages_match_the_pagecount(page_queue)
    if wrong:
        raise SystemExit("the pages on disk are not the pagecount's: " + "; ".join(wrong))
    n_pages = sum(len(rows) for rows in page_queue.values())
    n_posts = sum(len(rows) for rows in post_queue.values())
    record = {
        "phase": "promo-pulse-1 S4 — the C2 backfill (PAID): vision for the census's pages, text"
        " for its price posts",
        "authority": "docs/reviews/2026-08-30-plan-promo-pulse-1.md «Ruling 02.09 (b)» — «STEP_CAP_USD"
        " = 3.95 … the guard's step anchor with --step promo-pulse-1 --step-cap 3.95 … The text leg"
        " runs FIRST … Mid-run: no cap raise, ever»; docs/plans/promo-pulse-1.md S4, SP-1b",
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
                "source": "results/post_media_promo_c2.json through run_loop.pages_of — the"
                " census's pinned media posts, one file per photo member, counted against"
                " results/promo_pagecount_c2.json :: pages_exact per channel",
            },
            "posts": {
                "total": n_posts,
                "by_channel": {handle: len(rows) for handle, rows in post_queue.items()},
                "ids_sha256": posts_sha256(post_queue),
                "source": "results/promo_census_c2.json :: channels[].text_price_msg_ids, read off"
                " the live store (v1 ∪ r2)",
            },
            "order": ordered(set(page_queue) | set(post_queue)),
            "order_from": "docs/PHASE-promo-pulse-1.md §3, the operator's A1 list in its printed"
            " order; channels the list does not name follow it, sorted",
            "stage_0": "post_text — every channel's text posts BEFORE any page (ruling 02.09 (b))",
        },
        "expected_worker": load(POSITIONS_PIN)["expected_worker"],
        "expected_worker_from": "results/sku_pilot_serving_v2.json — the pin run_5c2 and the smoke"
        " assert",
        "rung_0": rung_0(n_pages, n_posts),
        "in_run_gates": {
            "go_no_go": "SPEC 3.17 (10)(a): after two warm-ups on REPRESENTATIVE inputs — the"
            " first queued C2 page and the first queued C2 post — the whole step is re-projected"
            " at the measured marginals and no gold call is made if it exceeds the step cap",
            "stage_projection": "after EVERY channel, positions_gm4_skub.projection at the"
            " measured marginal; projected over the cap → the run stops at that boundary and the"
            " unbought channels are recorded (PROCESS rung 2; silence = KILL)",
            "cap_gate": "SPEC 3.17 (10)(c), per pack: refuse the next job when what is left of"
            f" the cap cannot absorb one job at the {skub.JOB_TIMEOUT_S:.0f} s execution timeout",
            "packs": f"bytes first ({skub.MAX_PAYLOAD_MB} MB, RunPod's /run refuses 10 MiB), then"
            " the count the pessimistic marginal allows inside the timeout",
        },
        "kill_rules": [
            "the dear corner of rung 0 does not fit the step cap → nothing is created (STOP)",
            "the guard refuses --step promo-pulse-1 --step-cap 3.95 → that is the answer",
            "mid-run the cap is never raised: the (10)(a) gate, the re-projection after every"
            " stage and the per-pack cap gate decide (ruling 02.09 (b) item 3)",
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


def guard_says_go() -> int:
    """Rung 0 in the guard's own words: the step anchored (once) and both caps enforced."""
    return subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "runpod_guard.py"),
            "--step",
            STEP,
            "--step-cap",
            f"{STEP_CAP_USD:.2f}",
        ],
        check=False,
    ).returncode


def stage_projection(client, *, opened: float, done: int, total: int, rate: float, cap: float):
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
    gate = skub.go_no_go(
        billed=opened,
        page_marginal=page_seconds,
        text_marginal=text_seconds,
        n_pages=n_pages,
        n_rows=n_posts,
        rate=rate,
        budget=cap,
    )
    gate["over_cap_by"] = round(gate["projected_usd"] / cap - 1, 4)
    outcome["go_no_go"] = gate
    print(json.dumps(gate, indent=1), flush=True)
    if gate["refuse"]:
        note.append(
            f"REFUSED at the (10)(a) gate — projected ${gate['projected_usd']:.4f} against the"
            f" ${cap:.2f} step cap ({gate['over_cap_by']:+.1%}); no gold call was made"
        )
        # Ruling 02.09 (b) item 3: a stop on ANY gate records what is left, for the STOP's table.
        outcome["unbought"] = unbought(prereg, queued_pages, queued_posts, derived, cursor)
        return

    registered = load(PREREG_5C2)["prices"]
    page_registered = float(registered["leaflet_page"]["seconds_model"]["value"])
    text_registered = float(registered["post_text"]["seconds_model"]["value"])
    total = n_pages + n_posts
    done = 0
    outcome["leaflet"], outcome["stages"] = [], []

    def halted(stage: str, before: int, reading: dict) -> bool:
        """A pack the cap gate refused, or a projection over the cap: stop HERE, record the rest."""
        if len(note) > before:
            note.append(f"the run STOPPED at {stage}: the cap gate refused a pack")
        elif reading["over_cap"]:
            note.append(
                f"the run STOPPED after {stage}: projected ${reading['projected_usd']:.4f} over"
                f" the ${cap:.2f} step cap at the measured marginal (PROCESS rung 2, silence = KILL)"
            )
        else:
            return False
        outcome["unbought"] = unbought(prereg, queued_pages, queued_posts, derived, cursor)
        return True

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
    outcome["stages"].append({"after": "post_text"} | reading)
    print(f"  after post_text: {reading}", flush=True)
    if halted("post_text", before, reading):
        return

    for handle in prereg["population"]["order"]:
        rows = queued_pages.get(handle) or []
        if not rows:
            continue
        before = len(note)
        leg = fivec2.page_leg(
            client,
            fivec2.SliceTransport(fivec2.album_key),
            rows,
            derived=derived,
            cursor=cursor,
            categories=categories,
            aliases=aliases,
            revision=revision,
            endpoint=endpoint,
            marginal=page_seconds,
            registered_marginal=page_registered,
            cap=cap,
            rate=rate,
            drift=drift,
            note=note,
        )
        outcome["leaflet"].append(leg)
        done += sum(pack["pages_written"] for pack in leg["packs"])
        reading = stage_projection(
            client, opened=opened, done=done, total=total, rate=rate, cap=cap
        )
        outcome["stages"].append({"after": handle} | reading)
        print(f"  after {handle}: {reading}", flush=True)
        if halted(handle, before, reading):
            return


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register", action="store_true", help="$0: write the pre-registration")
    parser.add_argument("--dry-run", action="store_true", help="$0: selections, hashes, rung 0")
    parser.add_argument("--run", action="store_true", help="the PAID leg")
    parser.add_argument("--endpoint", help=f"the serving endpoint id (or ${ENDPOINT_ENV})")
    args = parser.parse_args(argv)

    if args.register:
        record = register()
        print(render_rung_0(record["rung_0"]))
        print(f"wrote {rel(PREREG)}")
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
        parser.error("choose --register, --dry-run or --run")

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
    if guard_says_go() != 0:
        raise SystemExit("the guard refuses — that is the answer, not an obstacle")

    page_queue, post_queue = pages(), posts()
    if pages_sha256(page_queue) != prereg["population"]["pages"]["ids_sha256"]:
        raise SystemExit("the page selection moved since the registration — refuse")
    if posts_sha256(post_queue) != prereg["population"]["posts"]["ids_sha256"]:
        raise SystemExit("the post selection moved since the registration — refuse")

    rate = float(prereg["rung_0"]["rates"]["rate_usd_per_second"])
    drift = float(load(PREREG_5C2)["drift"]["factor"])
    cap = float(prereg["step"]["cap_usd"])
    client = fivec2.client_for(endpoint, api_key)
    derived = RawStore(run_loop.DERIVED_ROOT)
    cursor = loop.load_cursor(run_loop.CURSOR)
    note: list[str] = []
    outcome = {
        "phase": prereg["phase"],
        "authority": rel(PREREG),
        "endpoint": endpoint,
        "step": prereg["step"],
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
            cap=cap,
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
