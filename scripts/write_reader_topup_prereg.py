#!/usr/bin/env python3
"""`results/reader_topup_prereg.json` — the registration for branch B's paid reader pass.

**What this buys and why.** `docs/reports/lora-b.md` found that a pass-1 training request carries a
topic and an entity block that come from a reader verdict, and that 105 of the 120 labelled threads
never bought one. The operator ruled branch B on 2026-08-19. This registers the buy: the same
reader instrument v5b was measured on, over the 105 threads, so the training prompts carry context
of the same KIND the gate's own rows are answered under.

**There is no PROMPT file for this step.** The authority is the operator's ruling, and the price it
was ruled over is `results/reader_topup_projection.json` — which is also where the arithmetic lives,
committed before this record and re-derived by it rather than restated.

**The cap.** $2.00, and it is the executor's derivation from a number the operator ruled over
(≈$1.20 published, $1.44 at the ceiling once the read is chunked into 132 units). It is a CEILING
and not a spend: the projection is $1.34 at the price v5b was billed. Every figure below is worked
at both prices, and the table shows the cap surviving the worst boot on record at the worse price.
A cap the operator wants smaller makes this record wrong and it is one constant away from saying so.

    PYTHONPATH=src python3.11 scripts/write_reader_topup_prereg.py
    PYTHONPATH=src python3.11 scripts/write_reader_topup_prereg.py --outdir /tmp/again
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_census_w1_reader as cell  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import prompts  # noqa: E402

PROJECTION = REPO_ROOT / "results" / "reader_topup_projection.json"
V5B_PREREG = REPO_ROOT / "results" / "prereg_reader_probe_v5b.json"
OUT_NAME = "results/reader_topup_prereg.json"

PHASE = "reader-topup"
TASK = "reader_thread_gm4_v5"
"""v5b's own registered text. A different one would make these verdicts a different instrument from
the 24 already bought and from the ones the eval prompts carry — which is the whole point."""

CHUNK = 16
CAP_USD = 2.00
DELETE_MARGIN_SECONDS = 60.0
BACKSTOP_HOURS = 3.0
MAX_RECREATES = 2
SSH_DEADMAN_SECONDS = 180
FIRST_REPLY_CEILING_SECONDS = 720
BOOTS = (180.0, 300.0, 480.0, 720.0, 1200.0)
"""Every boot this stack has on record, the 1 200 s outlier included. A table, not a forecast."""


def read(path: Path) -> dict:
    return json.loads(summary.read_text_or_refuse(path))


def chunks_of(msg_ids: list[int]) -> list[list[int]]:
    if len(msg_ids) <= CHUNK:
        return [msg_ids]
    return [msg_ids[index : index + CHUNK] for index in range(0, len(msg_ids), CHUNK)]


def units() -> list[dict]:
    """Every request the pod will be given, rendered here and pinned by its own sha.

    Order is DESCENDING payable count, v5b's rule: the expensive units go first, so the full-pass
    gate sees this run's worst seconds-per-unit early and the cheap tail cannot flatter it.
    """
    projection = read(PROJECTION)
    wanted = projection["population"]["sizes"]
    kept = {f"{one['channel']}:{one['post_id']}": one for one in cell.population()}
    missing = sorted(set(wanted) - set(kept))
    if missing:
        raise SystemExit(f"the reader cell no longer holds {missing[:3]} — the population moved.")

    out = []
    for name in sorted(wanted, key=lambda one: (-wanted[one], one)):
        thread = kept[name]
        texts = {int(row["msg_id"]): row["text"] for row in thread["comments"]}
        ids = [int(row["msg_id"]) for row in thread["comments"]]
        if len(ids) != wanted[name]:
            raise SystemExit(
                f"{name}: the projection counted {wanted[name]} payable comments and the cell holds"
                f" {len(ids)}. The record this run was priced from is stale — stop and report."
            )
        pieces = chunks_of(ids)
        for index, piece in enumerate(pieces, start=1):
            part = None if len(pieces) == 1 else (index, len(pieces))
            content = prompts.reader_messages_gm4(
                thread["channel"],
                int(thread["post_id"]),
                thread["post_text"],
                [(one, texts[one]) for one in piece],
                task=TASK,
                part=part,
            )[0]["content"]
            out.append(
                {
                    "id": name if part is None else f"{name}#{index}of{len(pieces)}",
                    "thread": name,
                    "channel": thread["channel"],
                    "post_id": int(thread["post_id"]),
                    "msg_ids": piece,
                    "part": None if part is None else list(part),
                    "payable_comments": len(piece),
                    "rendered_chars": len(content),
                    "rendering_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                }
            )
    return out


def money(items: list[dict], projection: dict) -> dict:
    generation = float(projection["projection"]["generation_seconds"])
    table = []
    prices = {"reader_card_example": 0.74, "ceiling": 0.80}
    for name, price in sorted(prices.items()):
        usable = CAP_USD / price * 3600 - DELETE_MARGIN_SECONDS
        for boot in BOOTS:
            left = usable - boot
            table.append(
                {
                    "price_usd_per_hour": price,
                    "which_price": name,
                    "boot_seconds": boot,
                    "usable_seconds": round(usable, 1),
                    "seconds_left_for_reading": round(left, 1),
                    "times_the_projection_that_fits": round(left / generation, 3),
                    "fits": left >= generation,
                }
            )
    return {
        "arithmetic": {
            "at_each_boot": table,
            "at_each_boot_rule": (
                "the cap, at both prices, less the deletion margin and the boot, against the"
                " generation projection. A table and not a forecast: four boots are on record for"
                " this stack and they disagree by 6.7×, so the pessimistic end is what the cap has"
                " to survive"
            ),
            "boot_kill_seconds": float(FIRST_REPLY_CEILING_SECONDS),
            "delete_margin_seconds": DELETE_MARGIN_SECONDS,
            "items": len(items),
            "reading_projection_seconds": generation,
            "projection_record": {
                "record": summary.rel(PROJECTION),
                "sha256": summary.sha256_of(PROJECTION),
            },
            "the_names_are_the_consumers": (
                "`boot_kill_seconds`, `reading_projection_seconds` and `delete_margin_seconds` are"
                " spelled the way `read_threads_reader_v4.deadlines` and `usable_seconds` READ"
                " them. A registration is consumed by shipped code, and a field it cannot find is"
                " a KeyError on the kill-rule path with a meter running — which is what the first"
                " attempt at this run bought for 23 billed seconds"
            ),
            "worst_case_that_still_fits": min(
                one["times_the_projection_that_fits"] for one in table
            ),
        },
        "cap_rule": (
            f"${CAP_USD:.2f} all-in, frozen at the first `pod create`. It is the EXECUTOR's"
            " derivation from a price the operator ruled over — ≈$1.20 published in"
            " docs/reports/lora-b.md, $1.44 once the read is chunked into 132 units and priced at"
            " the $0.80/h ceiling — rounded up so the cap survives the worst boot on record at the"
            " worse price. Raising it is the operator's word BEFORE any endpoint; lowering it makes"
            " this record wrong, which is one constant and a rebuild"
        ),
        "cap_usd_all_in": CAP_USD,
        "guard": (
            f"python3.11 scripts/runpod_guard.py --step {PHASE} --step-cap {CAP_USD:.2f}"
            " --note '<why this reading>' — anchored BEFORE the pod and read at every gate"
        ),
        "meter": {
            "card_requested": "NVIDIA GeForce RTX 4090",
            "datacenter": "EU-RO-1, pinned by network volume qw4nwleanc — the volume decides",
            "price_rule": (
                "**READ ON THE DAY.** `costPerHr` in the create response is the meter of record and"
                " every figure here is recomputed from it before the generation process starts. A"
                " projection that no longer fits deletes the pod and STOPS (Dv448)"
            ),
            "price_ceiling_usd_per_hour": 0.80,
            "resource": (
                "ONE rented pod, billed for every second it EXISTS — from `pod create` to `pod"
                " delete`. `pod stop` does not stop the bill, so this run deletes and never stops"
            ),
            "usd_per_second_at_the_example": round(0.74 / 3600, 9),
            "worked_example_rule": (
                "$0.74/h is what reader-v5b was BILLED at on the 24 GB card this run asks for. The"
                " ceiling beside it is lora-b's, and both are worked because the first is what this"
                " run is likely to pay and the second is what it may not exceed"
            ),
            "worked_example_usd_per_hour": 0.74,
        },
    }


def gates(items: list[dict], projection: dict) -> dict:
    generation = float(projection["projection"]["generation_seconds"])
    usable_at_the_example = CAP_USD / 0.74 * 3600 - DELETE_MARGIN_SECONDS
    return {
        "backstop": {
            "rule": (
                f"`--terminate-after` at create + {BACKSTOP_HOURS} h. NOT a cap guard — at the"
                f" worked example that is ${BACKSTOP_HOURS * 0.74:.2f}, over the cap. It is what"
                " deletes the pod if this Mac dies with the run open"
            ),
            "terminate_after_hours": BACKSTOP_HOURS,
        },
        "clock": (
            "seconds since the `pod create` response, which is when the meter starts. Not since ssh"
            " came up and not since the model began loading — the machine is billed for"
            " provisioning too, and a clock that starts later prices a leg at zero"
        ),
        "gate_records_APPEND": (
            "the run record keeps `gates` as a LIST; every WAIT/GO/KILL snapshot is appended, none"
            " overwritten, each stamped with its segment and pod id"
        ),
        "gates": {
            "0_transport_ssh_deadman": {
                "max_recreates": MAX_RECREATES,
                "threshold_seconds": float(SSH_DEADMAN_SECONDS),
                "rule": (
                    f"if `runpodctl ssh info` has not answered with a connectable endpoint by"
                    f" {SSH_DEADMAN_SECONDS} s of THIS segment's create-elapsed, the pod is killed"
                    " and replaced. A third dead pod is a datacenter state and a STOP"
                ),
            },
            "1_first_reply": {
                "ceiling_since_generation_started_seconds": FIRST_REPLY_CEILING_SECONDS,
                "affordability_deadline_since_create_seconds": round(
                    usable_at_the_example - generation, 1
                ),
                "rule": (
                    "the first reply must have landed by the EARLIER of the two, both put on the"
                    " create-elapsed axis. Affordability is loose on this registration — the cap"
                    " buys far more than the projection needs — so the twelve-minute ceiling is the"
                    " one that binds, and that is stated rather than left to be discovered"
                ),
            },
            "2_full_pass": {
                "rule": (
                    "`elapsed + max(unread units ÷ read, unread payable ÷ read payable) × measured"
                    " ≤ usable`. BOTH legs computed and the PESSIMISTIC one binds; re-run as"
                    " replies land. It is what deletes the pod BEFORE the cap rather than after"
                ),
                "scored_by": "scripts/read_threads_reader_v5.py::projection, through the swap",
            },
        },
        "stop_rules": [
            "a `costPerHr` above the $0.80/h ceiling at create → delete, no generation, STOP",
            "gate 0 KILL twice → a third dead pod is a datacenter state, STOP",
            "gate 1 or gate 2 STOP → scp everything, delete, and report what was read",
            f"more than {MAX_RECREATES} recreates in this attempt → STOP",
            "never two billing endpoints at once, checked BEFORE `pod create` and not after",
        ],
        "partial_is_a_result": (
            f"the {len(items)} units are independent and the runner skips what is already answered,"
            " so a STOP at any gate leaves a USABLE partial buy: the threads that were read get a"
            " bought topic and an entity block, and the rest keep the branch-C substitute. Nothing"
            " downstream requires the pass to be complete — `build_pass1_sft` renders whatever"
            " verdicts exist"
        ),
    }


def build() -> dict:
    projection = read(PROJECTION)
    items = units()
    v5b = read(V5B_PREREG)
    by_thread: dict[str, int] = {}
    for one in items:
        by_thread[one["thread"]] = by_thread.get(one["thread"], 0) + 1
    return {
        "attempt": (
            "ONE attempt, up to three pod SEGMENTS (two recreates), one cap. Each segment carries"
            " its own create stamp and its own costPerHr; never two pods at once"
        ),
        "authority": (
            "the operator's ruling «выполни ветку B» of 2026-08-19, over the fork published in"
            " docs/reports/lora-b.md. There is no PROMPT file for this step: the ruling is the"
            " authority and this record is the registration it is executed under"
        ),
        "contract": "docs/reports/lora-b.md — branch B",
        "frozen_when_the_pod_exists": [
            OUT_NAME,
            "results/reader_topup_pack.json",
            "results/reader_topup_projection.json",
            "src/market_pulse/prompts.py — the renderer and the parser",
            "the reader_thread_gm4_v5 prompt text",
        ],
        "go_no_go": gates(items, projection),
        "instruments": {
            "parser": {
                "entry_point": "market_pulse.reader_v5.parse / merge",
                "module": "src/market_pulse/prompts.py",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
            },
            "prompt_sha256": {TASK: prompts.prompt_sha256(TASK)},
            "same_instrument_as": (
                "reader-v5b — the same registered text, the same serving config and the same"
                " ceilings. The 24 verdicts already bought and the ones this run buys have to be"
                " one instrument, or the training prompts carry two kinds of context and the"
                " difference lands inside the arm"
            ),
            "serving": dict(v5b["instruments"]["serving"]),
            "task": TASK,
        },
        "money": money(items, projection),
        "phase": PHASE,
        "population": {
            "chunk_payable_max": CHUNK,
            "chunk_rule": (
                f"a thread of more than {CHUNK} payable comments is split into chunks of {CHUNK} in"
                " the store's own comment order, and the chunks' verdicts are merged back by"
                " `market_pulse.reader_v5.merge`. v5b read its 43-comment thread as 16/16/11 and"
                " every other thread whole; ten threads here are over the line, three of them past"
                " 100 comments"
            ),
            "enumeration_sha256": projection["population"]["enumeration_sha256"],
            "order": "descending payable comments, then thread id — the expensive units first",
            "payable_comments": projection["population"]["payable_comments"],
            "purpose": (
                "every one of these threads carries pass-1 training rows and no bought reader"
                " verdict. What the buy changes is measured in the projection record: 559 rows get"
                " a bought topic instead of a cut post fragment, and the entity block is expected"
                " to reach ~279 of 650 rows against 39 today"
            ),
            "threads": len(by_thread),
            "units": items,
            "units_per_thread_over_the_chunk_line": {
                name: count for name, count in sorted(by_thread.items()) if count > 1
            },
        },
        "producer": {
            "borrowed": {
                "results/reader_topup_projection.json": summary.sha256_of(PROJECTION),
                "results/prereg_reader_probe_v5b.json": summary.sha256_of(V5B_PREREG),
            },
            "script": "scripts/write_reader_topup_prereg.py",
        },
        "return_to_the_ruling": (
            "a STOP at any gate returns the partial buy and its reason to the operator. It does not"
            " re-decide branch B, and it never widens the cap: a cap raised after a reading is a"
            " cap that was never a cap"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    record = build()
    record["producer"]["sha256"] = summary.sha256_of(Path(__file__))
    out = args.outdir / OUT_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUT_NAME}  sha256 {summary.sha256_of(out)[:16]}…")

    pop = record["population"]
    sums = record["money"]["arithmetic"]
    print(
        f"\nPOPULATION  {pop['threads']} threads · {pop['payable_comments']} payable ·"
        f" {len(pop['units'])} units ({len(pop['units_per_thread_over_the_chunk_line'])} threads chunked)"
    )
    print(
        f"            rendered chars: max {max(one['rendered_chars'] for one in pop['units'])}"
        f" against the registered 40 000 ceiling"
    )
    print(
        f"MONEY       cap ${CAP_USD:.2f} · projection {sums['reading_projection_seconds']:.0f} s"
        f" of generation · the worst row of the boot table still fits at"
        f" {sums['worst_case_that_still_fits']}× the projection"
    )
    for row in record["money"]["arithmetic"]["at_each_boot"]:
        if row["boot_seconds"] in (300.0, 1200.0):
            print(
                f"            ${row['price_usd_per_hour']:.2f}/h · boot {row['boot_seconds']:.0f} s"
                f" -> {row['seconds_left_for_reading']:.0f} s left ="
                f" {row['times_the_projection_that_fits']}× the projection · fits {row['fits']}"
            )
    print(
        f"\nFIRST REPLY by generation + {FIRST_REPLY_CEILING_SECONDS} s (the binding one);"
        f" affordability sits at create + {record['go_no_go']['gates']['1_first_reply']['affordability_deadline_since_create_seconds']:.0f} s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
