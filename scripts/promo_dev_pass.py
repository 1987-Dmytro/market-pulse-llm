#!/usr/bin/env python3
"""S9 — the dev-40 pass over the promo-signal instrument. $0 until `--run` exists.

The draw (`results/promo_threads_draw.json`, seed 42) named 40 dev threads; the team lead labelled
every comment of them WITH TEXT in `docs/labels-promo-dev.jsonl`. This script renders what the model
reads for those threads, and turns one answer back into the row shape the grader scores.

**The render is shown before anything is bought.** Ruling 03.09 asks for the RENDERED prompt of one
dev thread at $0, so the team lead reads the law the model will actually obey rather than the
module's source. `--render` is that command.

**The answer is joined back per comment, not per signal.** Gold is one row per comment with a
`signal_types` LIST; the model answers with an `about` row per comment and free-standing `signal`
rows. `predicted_rows` joins them on `msg_id` — a comment the model said nothing about produces no
row and the grader counts it as a miss, which is what
[[an_abstention_is_an_answer]] asks for: silence is scored, never dropped.

**The price of iteration 1 is a BORROWED bound and the record says so.** No rate for THIS instrument
exists — `results/measurements.jsonl` has no row for the promo-signal prompt — so `--dry-run` prices
the leg at the nearest measured thing (`pass2_r2_seconds_per_thread`, 23.76 s over 75 cooled threads,
thinking off) and marks it BORROWED: a different prompt, a different pod, a different transport
([[a_rate_is_a_property_of_the_pod]], [[the_smokes_rate_carries_the_smokes_transport]]). It bounds
the ask; the smoke replaces it before anything is bought.

    python3.11 scripts/promo_dev_pass.py --render 6009 --channel @VARUS_channel
    python3.11 scripts/promo_dev_pass.py --dry-run          # $0: the corpus, its sizes, the bound
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import draw_promo_threads as draw  # noqa: E402

from market_pulse import promo_prompts  # noqa: E402

DRAW = REPO_ROOT / "results" / "promo_threads_draw.json"
CODEBOOK = REPO_ROOT / "docs" / "CODEBOOK-promo-signals.md"
GOLD = REPO_ROOT / "docs" / "labels-promo-dev.jsonl"
MEASUREMENTS = REPO_ROOT / "results" / "measurements.jsonl"
RATE_RECORD = REPO_ROOT / "results" / "srv2d_cost.json"
PREP = REPO_ROOT / "results" / "promo_dev40_prep.json"

PART = "dev"
"""Which half of the frozen draw this process is about — `dev` or `holdout`, and never both.

The draw (`results/promo_threads_draw.json`) named 20 + 20 of each stratum at seed 42 and froze
them disjoint; the dev half took the bar over three iterations and the holdout is the ONE shot
ruling 05.09 (q) prices. The two halves are the SAME instrument over different rows, so this module
is one module with a part, not a fork of itself ([[a_moved_guard_that_left_its_copy]]).
`use_part` rebinds the file constants below and every function reads them by name — the mechanism
`tests/test_promo_dev_pass.py`'s own fixture already uses to redirect the run record."""

BORROWED_RATE = "pass2_r2_seconds_per_thread"
"""The nearest MEASURED seconds-per-thread in the house — READER, thinking off, 75 cooled threads.
Named, never typed: :func:`borrowed_rate` reads it out of `results/measurements.jsonl` and carries
the row's own `instrument` and `n` into the record, so a reader sees what was borrowed from where."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def dev_threads(path: Path = DRAW, part: str | None = None) -> list[dict]:
    """The draw's rows for THIS part, both strata, in the record's own order."""
    body = json.loads(path.read_text(encoding="utf-8"))
    part = part or PART
    return [row for stratum in sorted(body["draw"]) for row in body["draw"][stratum][part]]


def thread_of(row: dict) -> tuple[str, list[dict]]:
    """One thread's post text and its comments, from the frozen v1 archive the draw read.

    The join is the draw's own — `parent_msg_id` against the post's `msg_id`, both as strings — so
    a thread rendered here is the thread that was drawn and labelled, not a re-derived neighbour.
    """
    stem, root = row["store_file"], str(row["thread_root"])
    posts = {str(one.get("msg_id")): one for one in draw.rows(draw.POSTS / f"{stem}.jsonl")}
    if root not in posts:
        raise SystemExit(f"{row['channel']} root {root}: no post in data/raw/posts/{stem}.jsonl")
    comments = [
        one
        for one in draw.rows(draw.COMMENTS / f"{stem}.jsonl")
        if str(one.get("parent_msg_id")) == root
    ]
    return posts[root].get("text") or "", comments


LEAK_CHECK = REPO_ROOT / "results" / "promo_law_leak_check.json"
CODEBOOK_LITERAL_FLOOR = 8
"""Chars, and NOT a new threshold: it is the rule the 04.09 session-12 measurement ran under, which
PROGRESS at `d002967` writes down as «of its 27 literals ≥8 chars». Below it the law's quotes are
marker WORDS the ruling never asked anyone to touch («дякую», «постійно», «завжди»), and every
comment in the store contains some of them. A(3)'s examples take NO floor — they were written today
and every one of them is checked."""


def quoted(text: str) -> list[str]:
    """Every «…» literal of a law text, whitespace-collapsed — the shape a quote takes in it."""
    return [" ".join(one.split()) for one in re.findall(r"«([^»]+)»", text)]


def store_texts(path: Path = DRAW) -> list[dict]:
    """Every dev-40 AND holdout-40 comment with text, from the frozen archive the draw read.

    Both splits, because the leak the check looks for is the instrument having seen its own exam,
    and the holdout is the exam that has not been sat yet ([[the_instruments_examples_came_from_the_exam]]).
    """
    body = json.loads(path.read_text(encoding="utf-8"))
    return [
        {
            "split": split,
            "channel": row["channel"],
            "thread_root": str(row["thread_root"]),
            "msg_id": str(one["msg_id"]),
            "text": " ".join((one.get("text") or "").split()),
        }
        for split in ("dev", "holdout")
        for stratum in sorted(body["draw"])
        for row in body["draw"][stratum][split]
        for one in thread_of(row)[1]
        if (one.get("text") or "").strip()
    ]


def leak_check(texts: list[dict]) -> dict:
    """Ruling 04.09 (j) item 2's check: no string of the LAW is a store comment. $0.

    The strings are read out of the shipped module, never retyped here
    ([[a_number_typed_into_its_own_checker]]) — a list beside the law would go on passing the day
    the law changed. Two populations, one rule each, and each hit names the comment it landed on so
    a reader can see WHICH thread the instrument had read.
    """
    populations = {
        "codebook": [one for one in quoted(promo_prompts.CODEBOOK) if len(one) >= CODEBOOK_LITERAL_FLOOR],
        "examples": quoted(promo_prompts.EXAMPLES),
    }
    hits = [
        {
            "population": name,
            "literal": literal,
            "split": row["split"],
            "unit": f"{row['channel']}:{row['thread_root']}:{row['msg_id']}",
        }
        for name, literals in populations.items()
        for literal in literals
        for row in texts
        if literal in row["text"]
    ]
    return {
        "contract": "docs/reviews/2026-08-30-plan-promo-pulse-1.md «Ruling 04.09 (j)» item 2 — no"
        " string of the rendered law is a substring of a dev-40 or holdout-40 comment",
        "codebook_version": promo_prompts.codebook_version(),
        "template_version": promo_prompts.template_version(),
        "corpus": {
            "comments_with_text": len(texts),
            "dev": sum(1 for one in texts if one["split"] == "dev"),
            "holdout": sum(1 for one in texts if one["split"] == "holdout"),
            "from": rel(DRAW) + " + the frozen v1 archive data/raw",
        },
        "populations": {
            "codebook": {
                "literals": len(populations["codebook"]),
                "rule": f"«…» literals of promo_prompts.CODEBOOK, >= {CODEBOOK_LITERAL_FLOOR} chars",
            },
            "examples": {
                "literals": len(populations["examples"]),
                "rule": "«…» literals of promo_prompts.EXAMPLES, no floor — every one of them",
            },
        },
        "hits": hits,
        "verdict": "CLEAN" if not hits else "LEAK",
    }


def render_thread(row: dict) -> str:
    post, comments = thread_of(row)
    return promo_prompts.render(row["channel"], row["thread_root"], post, comments)


def predicted_rows(row: dict, answer: dict) -> list[dict]:
    """One model answer → gold-shaped rows, one per comment the model placed."""
    types: dict[str, set] = {}
    for signal in answer.get("signals") or []:
        types.setdefault(str(signal.get("msg_id")), set()).add(signal.get("type"))
    return [
        {
            "channel": row["channel"],
            "thread_root": str(row["thread_root"]),
            "msg_id": str(one.get("msg_id")),
            "subject_type": one.get("subject_type"),
            "subject": one.get("subject"),
            "source": one.get("source"),
            "signal_types": sorted(types.get(str(one.get("msg_id")), set()), key=str),
        }
        for one in (answer.get("about") or [])
    ]


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def borrowed_rate() -> dict:
    """The named measurement row, or a refusal. A projection with no named rate projects nothing —
    `scripts/project_think_zero_shot.py:107`'s rule, applied to an instrument that has none yet."""
    for line in MEASUREMENTS.read_text(encoding="utf-8").splitlines():
        if line.strip() and (row := json.loads(line))["name"] == BORROWED_RATE:
            return row
    raise SystemExit(
        f"{BORROWED_RATE} is not in results/measurements.jsonl — this leg has no rate of its own"
        " and no rate to borrow, so it prices nothing. The smoke writes it."
    )


def own_rate() -> dict:
    """This instrument's OWN measured seconds-per-thread, from the SLOWEST pod it has ever run on.

    Ruling 04.09 (o) item 4 retires the borrow the day the instrument has a rate of its own, and
    ruling 05.09 (q) item 3 says WHICH of its rows: the slowest, because three pods of one RTX 4090
    ran 1.5-2.3x apart on byte-identical answers and a rate is a property of the pod, not of the
    prompt ([[a_rate_is_a_property_of_the_pod]]). `max` picks the row, not `value`: the row's own
    maximum is what the dear corner is priced at, and a row can carry the higher mean with the lower
    max. Read out of the file, never typed ([[a_number_typed_into_its_own_checker]]).

    It READS the dev loop's rows while the holdout's own smoke WRITES under `promo_holdout40_…` —
    two names on purpose. The INSTRUMENT is one: (q) item 2 freezes it byte for byte, so the dev
    loop's three rows are this prompt's own history and are exactly what (q) item 3 prices the shot
    at. The POPULATIONS are not: the holdout's threads are the longer half of the draw, and a row of
    one landing under the other's name is how a second population gets inside a first one's reading
    ([[a_second_population_in_a_shared_store_voids_the_first_seal]], [[id_spaces_that_look_comparable]]).
    """
    rows = [
        json.loads(line)
        for line in MEASUREMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and json.loads(line)["name"] == MEASURED_RATE
    ]
    if not rows:
        raise SystemExit(
            f"{MEASURED_RATE} is not in results/measurements.jsonl — the holdout is priced on this"
            " instrument's OWN pace (ruling (o) 4) and no smoke of it has been measured yet."
        )
    return max(rows, key=lambda row: row["max"])


def rate_for(part: str) -> dict:
    """The seconds-per-thread one part is priced at. The dev loop borrowed; the holdout owns."""
    return borrowed_rate() if part == "dev" else own_rate()


def prep(part: str | None = None, gold: Path | None = None) -> dict:
    """The part's corpus as the model will read it, its sizes, and the ask BOUNDED, not priced."""
    part, gold = part or PART, gold or GOLD
    rows = dev_threads(part=part)
    rate = rate_for(part)
    usd_per_second = json.loads(RATE_RECORD.read_text(encoding="utf-8"))["rate"]["usd_per_second"]
    threads = []
    for row in rows:
        rendered = render_thread(row)
        threads.append(
            {
                "channel": row["channel"],
                "thread_root": str(row["thread_root"]),
                "stratum": row["stratum"],
                "n_comments": row["n_comments"],
                "n_wordless": row["n_wordless"],
                "chars": len(rendered),
                "extractor_version": promo_prompts.extractor_version(rendered),
            }
        )
    seconds = rate["value"] * len(threads)
    return {
        **({} if part == "dev" else {"part": part}),
        "phase": "promo-pulse-1 S9 — dev-40, the $0 half: what the model reads and what it bounds",
        "authority": "docs/reviews/2026-08-30-plan-promo-pulse-1.md «Ruling 03.09» — the prompt's"
        " law is re-rendered from the codebook BEFORE the first paid K8 run, and the RENDERED"
        " prompt is read at $0 before any pod exists",
        "law": {
            "codebook": rel(CODEBOOK),
            "codebook_sha256": sha256_of(CODEBOOK),
            "codebook_version": promo_prompts.codebook_version(),
            "vocabulary": promo_prompts.vocabulary(),
        },
        "gold": {"path": rel(gold), "sha256": sha256_of(gold), "lines": len(
            [one for one in gold.read_text(encoding="utf-8").splitlines() if one.strip()]
        )} if gold.exists() else {
            "path": rel(gold),
            "sha256": None,
            "lines": 0,
            "missing": "gold missing -> no record: --register REFUSES to write a registration whose"
            " pinned gold does not exist, because a pin over an absent file pins nothing"
            " ([[preregistration_is_a_file_not_a_constant]]). The dry run prices the leg anyway —"
            " the pricing is the pod's arithmetic and does not read a label.",
        },
        "draw": {"path": rel(DRAW), "sha256": sha256_of(DRAW), "dev_threads": len(threads)},
        "corpus": {
            "threads": threads,
            "chars_total": sum(one["chars"] for one in threads),
            "chars_max": max(one["chars"] for one in threads),
            "distinct_renders": len({one["extractor_version"] for one in threads}),
        },
        "bound": {
            "is_a_bound_and_not_a_price": "this instrument has no measured rate. The seconds below"
            " are BORROWED from another prompt, another pod and another transport; the smoke"
            " measures this leg's own and the registration is written against THAT",
            "borrowed_from": {
                "name": rate["name"],
                "value": rate["value"],
                "unit": rate["unit"],
                "n": rate["n"],
                "max": rate["max"],
                "instrument": rate["instrument"],
                "measured_on": rate["measured_on"],
                "source": rate["source"],
            },
            "threads": len(threads),
            "seconds_at_the_borrowed_mean": round(seconds, 1),
            "seconds_at_the_borrowed_max": round(rate["max"] * len(threads), 1),
            "usd_per_second": usd_per_second,
            "usd_at_the_borrowed_mean": round(seconds * usd_per_second, 4),
            "usd_at_the_borrowed_max": round(rate["max"] * len(threads) * usd_per_second, 4),
            "boot_not_included": "a boot is the endpoint's, not the leg's — the registration adds"
            " it once at the corner it is measured at",
        },
    }


# --- the PAID half: the dev loop's own step, its rungs, its registration ---------------------------

ITERATION = 3
"""The dev-loop iteration the registration and the pack are emitted for — ruling 04.09 (m) item 5.
Iterations 1 and 2 are bought, priced and on disk; the transport repair of `f872a53` is a NEW
`extractor_version` by ruling 03.09 (c) item 3's own letter, so it is bought under the NEXT number
and never re-bought under iteration 2's."""

STEP = "promo-dev-loop"
"""Its OWN step and its own ledger (plan §9). S4's `promo-pulse-1` is CLOSED at $2.9867 and a closed
step cannot carry a new run's spend; ruling 03.09 (c) opens this one."""

STEP_CAP_USD = 2.50
STEP_FLOOR_USD = 2.00
HOLDOUT_RESERVE_USD = 0.30
"""Plan §9: cap `min($2.50, REMAINING − $0.30)`, floor $2.00, and the holdout's $0.30 is a separate
pre-registration this step may not reach. The REMAINING is the guard's, read at `--register`."""

SMOKE_N = 3
"""Plan §9's sample, and a RULE rather than a pick: the shortest, the median and the longest render
by `promo_dev40_prep.json :: corpus.threads[].chars`."""

PREREG = REPO_ROOT / "results" / "prereg_promo_dev_loop.json"
RUNNER = REPO_ROOT / "scripts" / "promo_dev_pod_runner.py"
PROMO_PROMPTS = REPO_ROOT / "src" / "market_pulse" / "promo_prompts.py"
"""The two halves of iteration 3's repair — the dispatch is in the runner, the fold in the module.
`extractor_version` is `sha256(rendered prompt)` and a transport repair leaves all 40 renders
identical, so the record separates the instruments by these shas or by nothing at all (ruling
04.09 (m) item 5, confirmed by (n) item 2)."""
PACK = REPO_ROOT / "results" / "promo_dev40_pack.json"
SIBLING = REPO_ROOT / "results" / "pass2_signals_r2_run.json"
BORROWED_GATES = REPO_ROOT / "results" / "prereg_reader_probe_v5b.json"
SIBLING_PREREG = REPO_ROOT / "results" / "prereg_pass2_signals_r2.json"
PREREG_5C2 = REPO_ROOT / "results" / "prereg_5c2_run.json"

CARD = "NVIDIA GeForce RTX 4090"
DATACENTER = "EU-RO-1"
"""The volume decides the datacenter (`qw4nwleanc`, `mp-srv2`), and the card is the sibling's — the
same RTX 4090 `pass2-signals-r2` measured the borrowed rate on."""

POST_TASK = "positions_text_gm4"
"""Leg B's task, and it is a REGISTERED prompt of `src/market_pulse/prompts.py`: the 16 posts ride
this pod through the SHIPPED render, so nothing new is written for them."""

GUARD = REPO_ROOT / "scripts" / "runpod_guard.py"

HOLDOUT_FILES = {
    "gold": REPO_ROOT / "docs" / "labels-promo-holdout.jsonl",
    "prep": REPO_ROOT / "results" / "promo_holdout40_prep.json",
    "prereg": REPO_ROOT / "results" / "prereg_promo_holdout.json",
    "pack": REPO_ROOT / "results" / "promo_holdout40_pack.json",
    "run": REPO_ROOT / "results" / "promo_holdout_run.json",
    "step": "promo-holdout",
    "stem": "promo_holdout40",
}
"""The holdout's OWN files — ruling 05.09 (q) item 5. Its own everything: the dev registration is
committed, frozen and already spent against, and a second population in one record voids the first
seal ([[a_second_population_in_a_shared_store_voids_the_first_seal]])."""

STEM = "promo_dev40"
"""What `--score` names its two files after. The iteration suffix is the dev loop's, not the part's:
the holdout is ONE shot and has no iteration to number."""


def guard_reading() -> dict:
    """What the cycle has left, in the guard's own words. Never re-derived here.

    `run_promo_c2.guard_says_go`'s rule, one line further: a missing REMAINING reads as unlimited,
    so a run that cannot find the guard's own line refuses instead of pricing itself against a
    number it invented ([[a_budget_is_not_an_elapsed]])."""
    done = subprocess.run(
        [sys.executable, str(GUARD)], check=False, capture_output=True, text=True
    )
    print(done.stdout, end="", flush=True)
    print(done.stderr, end="", file=sys.stderr, flush=True)
    if done.returncode != 0:
        raise SystemExit(f"the guard refused (exit {done.returncode}) — no registration is written")
    found = re.search(r"^REMAINING\s+\$([0-9.]+)", done.stdout, re.M)
    cycle = re.search(r"^CYCLE 3 SPENT\s+\$([0-9.]+) of \$([0-9.]+)", done.stdout, re.M)
    if not found or not cycle:
        raise SystemExit(
            "the guard printed no 'REMAINING $…' / 'CYCLE 3 SPENT $… of $…' pair — the cycle's"
            " headroom is unreadable and an unreadable headroom is not $∞. Refuse."
        )
    return {
        "remaining_usd": float(found.group(1)),
        "cycle3_spent_usd": float(cycle.group(1)),
        "cycle3_cap_usd": float(cycle.group(2)),
        "from": "scripts/runpod_guard.py, its own printed REMAINING and CYCLE 3 lines",
        "at": datetime.now(UTC).isoformat(timespec="seconds"),
    }


def offered_price() -> dict:
    """The card's price in this datacenter, READ ON THE DAY — v5b's `money.meter.price_rule`.

    The DEARER of the two clouds is registered: the create response's `costPerHr` is the price that
    is actually billed, and a registration written at the cheaper offer would be a ceiling the run
    can exceed without a single gate firing ([[a_ceiling_derived_from_one_span_measured_over_another]]).
    """
    done = subprocess.run(
        ["runpodctl", "gpu", "list"], check=False, capture_output=True, text=True
    )
    if done.returncode != 0:
        raise SystemExit(f"runpodctl gpu list failed: {done.stderr.strip()[:200]}")
    for gpu in json.loads(done.stdout):
        if gpu.get("displayName") not in ("RTX 4090",):
            continue
        here = [
            one
            for one in (gpu.get("dataCenterAvailability") or [])
            if one.get("dataCenterId") == DATACENTER
        ]
        prices = [
            float(one)
            for one in (gpu.get("securePricePerHr"), gpu.get("communityPricePerHr"))
            if one
        ]
        if not here or not prices:
            continue
        return {
            "card": CARD,
            "datacenter": DATACENTER,
            "stock": here[0].get("stockStatus"),
            "usd_per_hour": max(prices),
            "offers_usd_per_hour": prices,
            "rule": "the DEARER offer of secure/community, read on the day; the create response's"
            " own costPerHr is the price the meter bills and the price gate re-checks it",
            "read_at": datetime.now(UTC).isoformat(timespec="seconds"),
        }
    raise SystemExit(
        f"{CARD} is not offered in {DATACENTER} today — the volume pins the datacenter, so this is"
        " a STOP for the operator's word, not a card to substitute"
    )


def ssh_deadman() -> dict:
    """The liveness deadline, from the PRODUCTION sibling — ruling 03.09 (e) item 1.

    v5b is a PROBE. Its 180 s killed two healthy pods of this step on 2026-09-03 while
    `prereg_pass2_signals_r2.json` — the sibling that SETTLED on the same image, card and
    datacenter — registers 500 s with six readings running 14.5 → 262.5 s. A gate set below the
    observed maximum of the span it measures returns KILL before a measurement can exist
    ([[a_reproducible_probe_can_be_unrepresentative]]), which is what happened."""
    clock = json.loads(SIBLING_PREREG.read_text(encoding="utf-8"))["kill_clock"]
    rows = [one for one in clock if one.get("rung") == 2 and one.get("name") == "ssh dead-man"]
    if len(rows) != 1 or not isinstance(rows[0].get("deadline_seconds"), (int, float)):
        raise SystemExit(
            f"{rel(SIBLING_PREREG)} :: kill_clock has {len(rows)} rung-2 ssh dead-man rows with a"
            " numeric deadline — the ruled source is unreadable, and an unreadable gate is not 500 s"
        )
    return {
        "seconds": float(rows[0]["deadline_seconds"]),
        "from": f"{rel(SIBLING_PREREG)} :: kill_clock[rung 2].deadline_seconds",
        "rule": rows[0]["rule"],
    }


def borrowed_gates() -> dict:
    """v5b's frozen transport gates, READ and not retyped — plan §9a's borrow.

    The dead-man is NOT v5b's any more: ruling 03.09 (e) item 1 moved that one field to the
    production sibling's record. The other three stay where they were."""
    v5b = json.loads(BORROWED_GATES.read_text(encoding="utf-8"))
    gate0 = v5b["go_no_go"]["gates"]["0_transport_ssh_deadman"]
    money = v5b["money"]["arithmetic"]
    dead = ssh_deadman()
    margin = float(money["delete_margin_seconds"])
    return {
        "from": rel(BORROWED_GATES)
        + " — frozen; boot_kill_seconds, delete_margin_seconds and max_recreates only",
        "ssh_deadman_seconds": dead["seconds"],
        "ssh_deadman_from": dead["from"],
        "ssh_deadman_rule": "ruling 03.09 (e) item 1, read and not typed: the PRODUCTION sibling's"
        f" deadline on the same card and datacenter — «{dead['rule']}»",
        "max_recreates": int(gate0["max_recreates"]),
        "boot_kill_seconds": float(money["boot_kill_seconds"]),
        "delete_margin_seconds": margin,
        "terminate_after_minutes": int(v5b["go_no_go"]["backstop"]["terminate_after_minutes"]),
    }


def sibling_overhead() -> dict:
    """Everything a pod bills that is NOT generation, measured on the sibling that settled.

    `pass2-signals-r2` billed 2 061 s for 75 threads at 23.76 s each; the remainder is boot, the
    31B load, the scp up and back, the poll gaps and the delete. A registration that multiplied
    per-thread seconds by a per-second price and stopped there would price the generation and not
    the bill ([[no_rung_watches_an_idle_pod]])."""
    pod = json.loads(SIBLING.read_text(encoding="utf-8"))["pods"][0]
    rate = borrowed_rate()
    generation = float(rate["value"]) * 75
    return {
        "seconds": round(float(pod["billed_seconds"]) - generation, 1),
        "rule": "the sibling's BILLED seconds less its generation at the same borrowed rate over"
        " its own 75 threads — boot, the 31B load, scp up and back, the polls and the delete",
        "from": f"{rel(SIBLING)} :: pods[0].billed_seconds {pod['billed_seconds']} and"
        f" results/measurements.jsonl :: {BORROWED_RATE} × 75",
        "sibling_usd_per_hour": float(pod["usd_per_hour"]),
        "sibling_billed_usd": float(pod["billed_usd"]),
    }


def smoke_units(threads: list[dict]) -> list[dict]:
    """The shortest, the median and the longest render — a rule, never a pick (plan §9)."""
    order = sorted(threads, key=lambda one: (one["chars"], one["channel"], one["thread_root"]))
    picked = [order[0], order[len(order) // 2], order[-1]]
    for one, role in zip(picked, ("shortest", "median", "longest")):
        one["smoke_role"] = role
    return picked


def unit_id(row: dict) -> str:
    return f"{row['channel']}:{row['thread_root']}"


def corner(name: str, *, n_threads, n_posts, s_thread, s_post, overhead, usd_per_second, cap):
    seconds = overhead + n_threads * s_thread + n_posts * s_post
    usd = round(seconds * usd_per_second, 4)
    return {
        "name": name,
        "seconds_per_thread": round(s_thread, 3),
        "seconds_per_post": round(s_post, 3),
        "overhead_seconds": round(overhead, 1),
        "billable_seconds": round(seconds, 1),
        "usd": usd,
        "cap_usd": round(cap, 4),
        "fits": usd <= cap,
        "over_cap_by": round(usd / cap - 1, 4),
    }


def rung_0(
    *, cap: float, price: dict, threads: list[dict], n_posts: int, part: str | None = None
) -> dict:
    """The step at three corners, in the POD's own unit — seconds of existence × $/s.

    Ruling 03.09 (c) amendment 1: this prices the SMOKE plus ITERATION 1 and the 16 posts, never
    five iterations. Iterations 2–5 are re-projected at the MEASURED rate before they are bought.
    """
    part = part or PART
    rate = rate_for(part)
    owned = rate["name"] == MEASURED_RATE
    word, whose = ("measured", "smoke's") if owned else ("borrowed", "sibling's")
    overhead = sibling_overhead()
    text_s = float(load(PREREG_5C2)["prices"]["post_text"]["seconds_model"]["value"])
    usd_per_second = price["usd_per_hour"] / 3600.0
    n_threads = SMOKE_N + len(threads)
    common = {
        "n_threads": n_threads,
        "n_posts": n_posts,
        "s_post": text_s,
        "overhead": overhead["seconds"],
        "usd_per_second": usd_per_second,
        "cap": cap,
    }
    table = [
        corner(
            f"cheap — the {word} MEAN over every leg, the sibling's measured overhead",
            s_thread=rate["value"],
            **common,
        ),
        corner(
            f"priced — the {word} mean plus one whole extra overhead (a second segment after a"
            " dead-man KILL, which the transport allows twice)",
            s_thread=rate["value"],
            **(common | {"overhead": overhead["seconds"] * 2}),
        ),
        corner(
            f"dear — the {word} MAX on every thread ({rate['max']} s was ONE of the {whose}"
            f" {rate['n']}) and two overheads. Pessimistic by construction: the guard's spend is a"
            " maximum and a cap blown after the money is spent cannot be un-spent",
            s_thread=rate["max"],
            **(common | {"overhead": overhead["seconds"] * 2}),
        ),
    ]
    cheap, dear = table[0], table[-1]
    read, issued = dear, "dear"
    ruling = "docs/PROCESS.md «Money» rung (0) — the registered corner is the DEAR one"
    if part != "dev" and not dear["fits"]:
        read, issued = cheap, "mean"
        ruling = (
            f"ruling 05.09 (q) item 3 — the dear corner ${dear['usd']:.4f} is OVER the"
            f" ${cap:.4f} cap and the holdout is issued FITS on the MEAN corner"
            f" ${cheap['usd']:.4f}, with the cap as the HARD STOP: `--terminate-after` is derived"
            " from it and the meter cannot pass it. The dear corner stays in this table and in"
            " `dear_usd`, priced and named, so nothing over the cap is hidden"
            " ([[a_bound_the_meter_cannot_reach]])"
        )
    return {
        "rule": "docs/PROCESS.md «Money» rung (0): price at create ≤ the registered ceiling — the"
        " ceiling is the step cap, the price is the DEAR corner",
        "amendment": "ruling 03.09 (c) item 1 — smoke + iteration 1 + the 16 posts, not five"
        " iterations: the borrowed max over five would refuse a loop the smoke may prove cheap",
        "threads": n_threads,
        "threads_note": f"{SMOKE_N} smoke + {len(threads)} dev-40. The smoke's three ARE the pass's"
        " first three units, so the pod answers 40 and the registration is bought high, spent low",
        "posts": n_posts,
        "cap_usd": round(cap, 4),
        "price": price,
        **{
            ("measured_rate" if owned else "borrowed_rate"): {
                k: rate[k] for k in ("name", "value", "max", "n", "instrument", "source")
            }
        },
        "overhead": overhead,
        "seconds_per_post_from": "results/prereg_5c2_run.json :: prices.post_text.seconds_model",
        "table": table,
        "dear_usd": dear["usd"],
        "dear_fits": dear["fits"],
        "issued_on": issued,
        "issued_rule": ruling,
        "fits": read["fits"],
        "hard_stop_seconds": round(cap / usd_per_second, 1),
    }


def render_rung_0(verdict: dict) -> str:
    lines = [
        f"rung 0 — {verdict['threads']} threads + {verdict['posts']} posts on one"
        f" {verdict['price']['card']} at ${verdict['price']['usd_per_hour']}/h"
        f" ({verdict['price']['datacenter']}, stock {verdict['price']['stock']})"
        f" against the step cap ${verdict['cap_usd']:.4f}",
        f"{'corner':<8}{'s/thread':>10}{'overhead':>10}{'seconds':>10}{'usd':>9}  fits",
    ]
    for row in verdict["table"]:
        lines.append(
            f"{row['name'].split(' ')[0]:<8}{row['seconds_per_thread']:>10.3f}"
            f"{row['overhead_seconds']:>10.1f}{row['billable_seconds']:>10.1f}{row['usd']:>9.4f}"
            f"  {'yes' if row['fits'] else 'NO':<4} ({row['over_cap_by']:+.1%})"
        )
    lines.append(
        f"verdict: {'FITS' if verdict['fits'] else 'DOES NOT FIT'} at the"
        f" {verdict.get('issued_on', 'dear')} corner"
        f" · hard stop {verdict['hard_stop_seconds']:.0f} s of pod existence"
    )
    if verdict.get("issued_on") == "mean":
        lines.append(f"  {verdict['issued_rule']}")
    return "\n".join(lines)


def leg_b_posts() -> dict:
    """The C2 posts S4 left without an evidence row, enumerated from the store and not from prose.

    `docs/reports/promo-pulse-1.md` names 16 of them; this reads the same subtraction S4's own
    driver makes — the registered posts less what the derived store already answers — so the
    registration pins IDS and not a count ([[count_in_prose_is_not_the_enumeration]])."""
    import run_loop
    import run_promo_c2 as c2

    from market_pulse import loop
    from market_pulse.raw_store import RawStore

    derived = RawStore(run_loop.LIVE_DERIVED_ROOT, archives=(run_loop.DERIVED_ROOT,))
    left = {}
    for handle, rows in c2.posts().items():
        queued = loop.queued_posts(rows, derived, handle, None)
        if queued:
            left[handle] = sorted(str(one["msg_id"]) for one in queued)
    return {
        "task": POST_TASK,
        "rule": "S4's own subtraction: results/promo_census_c2.json's price posts less the rows"
        " data/derived_w2/ already answers. A REGISTERED prompt, so the pod renders them with the"
        " shipped render and nothing new is written for them",
        "by_channel": left,
        "posts": sum(len(ids) for ids in left.values()),
    }


def register(cap_usd: float | None = None) -> dict:
    """Rung 0 before anything exists — plan §9, ruling 03.09 (c) amendments 1 and 5.

    `--cap` is the holdout's, and it is an OPERATOR's number (ruling 05.09 (q) item 3), never this
    script's: the $0.30 the plan fenced was an estimate over a rate that has since been retired, and
    PHASE v7 §6.1 makes a fence for a later step an estimate re-priced at that step's registration
    ([[a_cap_set_from_one_legs_price]]). The dev loop's own rule is untouched and still the default.
    """
    if not GOLD.exists():
        raise SystemExit(
            f"{rel(GOLD)} is missing — gold missing -> no record. The registration PINS the gold by"
            " sha256 and a pin over an absent file pins nothing, so nothing is written: the record"
            " would claim a frozen answer key that does not exist"
            " ([[preregistration_is_a_file_not_a_constant]]). Commit the gold, then --register."
        )
    money = guard_reading()
    if cap_usd is None:
        cap = round(min(STEP_CAP_USD, money["remaining_usd"] - HOLDOUT_RESERVE_USD), 4)
        cap_rule = f"min(${STEP_CAP_USD:.2f}, REMAINING − ${HOLDOUT_RESERVE_USD:.2f})"
        if cap < STEP_FLOOR_USD:
            raise SystemExit(
                f"the dev loop's cap is ${cap:.4f} — below the ${STEP_FLOOR_USD:.2f} floor plan §9"
                " names. Ruling 02.09 (b) §4 makes that the operator's word, not this script's:"
                " STOP."
            )
    else:
        cap = round(min(cap_usd, money["remaining_usd"]), 4)
        cap_rule = f"min(${cap_usd:.4f} — the operator's word, ruling 05.09 (q) 3 — , REMAINING)"
        if cap < cap_usd:
            raise SystemExit(
                f"the cap asked for is ${cap_usd:.4f} and the guard's REMAINING is"
                f" ${money['remaining_usd']:.4f} — a cap above what the cycle has left is a cap"
                " nothing enforces. The operator raises the cycle or lowers the cap: STOP."
            )
    threads = dev_threads()
    prep = json.loads(PREP.read_text(encoding="utf-8"))["corpus"]["threads"]
    smoke = smoke_units([dict(one) for one in prep])
    left_over = leg_b_posts() if PART == "dev" else {"task": None, "by_channel": {}, "posts": 0}
    price = offered_price()
    verdict = rung_0(cap=cap, price=price, threads=threads, n_posts=0)
    return {
        "part": PART,
        "phase": f"promo-pulse-1 S9 — the dev loop's PAID instrument, iteration {ITERATION}"
        if PART == "dev"
        else "promo-pulse-1 S9 — the FROZEN holdout-40, the ONE shot (ruling 05.09 (q))",
        "class": "PRE-REGISTRATION. Written and committed before any pod of this step exists; git"
        " history is the only witness that it preceded the money.",
        "re_emission": "ruling 04.09 (m) item 5 and (n) item 2 — iterations 1 and 2 are kept by"
        " git history; THIS record is the one iteration 3 is bought under. The law, the TEMPLATE"
        " and the gold do NOT move: what moves is the answer's transport, and `extractor_version`"
        " = sha256(rendered prompt) cannot see it — so `scripts/promo_dev_pod_runner.py` and"
        " `src/market_pulse/promo_prompts.py` are pinned beside the law, half the repair in each"
        " and `check_law` covering neither. `committed_registration()` still does not re-verify"
        " `pinned_inputs`: a named debt.",
        "authority": "docs/reviews/2026-08-30-plan-promo-pulse-1.md «Ruling 03.09 (c)» — «the flags"
        " and their stub tests at $0 … --register shown with fits at the dear corner → then, in the"
        " same session if the registration fits, the pod: smoke → the table → iteration 1 → K8 →"
        " error table → teardown»; docs/plans/promo-pulse-1.md §9 and §9a",
        "question": "does the promo-signal instrument, under CODEBOOK"
        f" {promo_prompts.codebook_version()[:16]}…, clear subject ≥ 0.80 and signal ≥ 0.75 on"
        " dev-40 within at most 5 dev runs?"
        if PART == "dev"
        else "does the instrument that took the dev bar — the SAME four pins, byte for byte"
        " (ruling 05.09 (q) item 2) — clear subject ≥ 0.80 and signal ≥ 0.75 on the frozen"
        " holdout-40, in ONE shot?",
        "step": {
            "name": STEP,
            "ledger": rel(REPO_ROOT / "results" / f"spend_{STEP.replace('-', '_')}.json"),
            "cap_usd": cap,
            "cap_rule": cap_rule,
            "floor_usd": STEP_FLOOR_USD if PART == "dev" else None,
            "money": money,
            "no_cap_raise": "never, mid-run. Silence is KILL: nobody can be asked.",
        },
        "law": {
            "codebook": rel(CODEBOOK),
            "codebook_sha256": sha256_of(CODEBOOK),
            "codebook_version": promo_prompts.codebook_version(),
            "template_sha256": promo_prompts.template_version(),
            "template_rule": "ruling 04.09 (g) item 3 — the sha of the TEMPLATE with its examples"
            " block, so a render-only change is visible in the record; `codebook_version` alone"
            " compares the law and would read two instruments as one.",
            "baseline": (
                "iterations 1 and 2 are bought and priced on disk (ruling 03.09 (c) item 3;"
                " 04.09 (m) item 1 — signal 0.8854 HOLDS, subject 0.7500 RED). Iteration 3 moves"
                " ONE thing and nothing else: the answer's TRANSPORT — `balanced_prefix` reads the"
                " fence off before it dispatches on the shape, and a bare array is read as the rows"
                " it is (`f872a53`, ruling 04.09 (m) item 2). The law (v1.2), the TEMPLATE, the"
                " gold (v1.1), the decoding and the token ceiling are untouched."
                if PART == "dev"
                else "iteration 3 took BOTH dev bars on a complete reading (subject 0.8714, signal"
                " 0.9104; `results/grade_promo_dev40_iter3.json`) and ruling 05.09 (q) item 1"
                " accepted it. NOTHING moves for this shot: item 2 freezes the instrument as that"
                " iteration bought it, so `codebook_version`, `template_sha256`,"
                " `scripts/promo_dev_pod_runner.py` and `src/market_pulse/promo_prompts.py` are the"
                " dev-bar registration's own, byte for byte, and the near-quote and codebook-doc"
                " sync queue BEHIND this run. What changes is the POPULATION and nothing else — the"
                " frozen holdout arm of the same seed-42 draw, disjoint from dev-40 and never"
                " scored."
            ),
            "vocabulary": promo_prompts.vocabulary(),
        },
        "pinned_inputs": {
            rel(path): sha256_of(path)
            for path in (CODEBOOK, GOLD, DRAW, PREP, PREREG_5C2, RUNNER, PROMO_PROMPTS)
        },
        "population": {
            "leg_a": {
                "threads": len(threads),
                "order": [unit_id(one) for one in threads],
                "digest": hashlib.sha256(
                    "\n".join(unit_id(one) for one in threads).encode("utf-8")
                ).hexdigest(),
                "digest_rule": "sha256 over `channel:thread_root` per thread, in the draw's order",
                "smoke": {
                    "n": SMOKE_N,
                    "rule": "shortest, median and longest render by promo_dev40_prep.json's own"
                    " chars — a rule, not a pick",
                    "units": [
                        {
                            "unit_id": f"{one['channel']}:{one['thread_root']}",
                            "chars": one["chars"],
                            "role": one["smoke_role"],
                        }
                        for one in smoke
                    ],
                    "prefix": "these three are the pass's FIRST three units; the pod answers them,"
                    " the Mac reads the rate, and the decision table of ruling 03.09 (b) decides"
                    " whether the remaining 37 are bought at all",
                },
            },
            "leg_b": {
                "posts": 0,
                "by_channel": {},
                "closed": "ruling 04.09 (m) item 4 — 16 of 16 posts answered `[]` under BOTH"
                " iteration 1 and iteration 2: two identical readings. Iteration 3 buys leg A"
                " only. `build_pack` iterates `by_channel`, so the empty map is what actually"
                " keeps them off the pod; `not_bought` keeps them NAMED, not deleted.",
                "not_bought": left_over,
            },
        },
        "rung_0": verdict,
        "gates": borrowed_gates()
        | {
            "1_liveness": "the ssh dead-man above; never two pods, checked BEFORE `pod create`",
            "3_hard_stop": f"{verdict['hard_stop_seconds']:.1f} s of pod existence at the"
            " registered price — the platform-side backstop is terminate_after",
        },
        "decision_table": {
            "authority": "ruling 03.09 (b), quoted and not moved",
            "after_the_smoke_for_40_threads": {
                "<= 0.80": "run iteration 1 now",
                "0.80 - 1.20": "run it, then STOP with the error table",
                "> 1.20": "STOP before buying; pod torn down, listing shown",
            },
        },
        "teardown": "`runpodctl pod delete <id>`, then `runpodctl pod list -a` → [] and"
        " `runpodctl serverless list` → [] in the transcript, before every STOP and before the"
        " session ends (ruling 03.09 (c) item 2)",
        "out_of_scope": "no training; no holdout spend; no new sources; no cap raise. Leg B's"
        " answers land on disk as evidence for the store, and the ingest into data/derived_w2 is"
        " NOT in this session's sequence."
        if PART == "dev"
        else "no training; no new sources; no cap raise; no second shot — §8 (e) spends the"
        " holdout ONCE. Leg B does not exist here: ruling 05.09 (q) item 5 buys leg A only. A run"
        " that comes back incomplete is recorded under §6.5 and re-bought under the next number"
        " with the law UNMOVED; it is not a second reading of the same shot.",
    }


def prompt_shas() -> dict:
    """The READER texts this checkout serves, for `reader_v4_pod_runner.check_instrument`.

    Leg A's law is NOT in this map — `promo_prompts` is a module of its own — so the pack pins its
    codebook version beside it and the pod checks both."""
    from market_pulse import prompts

    return {task: prompts.prompt_sha256(task) for task in sorted(prompts.READER)}


OUTPUT_TOKENS = 4000
"""BORROWED, not chosen: `results/prereg_reader_probe_v5b.json :: instruments.ceilings.output_tokens`
— the sibling instrument's registered ceiling on the same card and the same template. Ruling
03.09 (c) item 3 makes max tokens a knob iterations 2-5 may turn; iteration 1 is the baseline."""

PROMO_TASK = "promo_signals_gm4_v1"
"""Leg A's task name. NOT a `prompts.py` registration — that module is pinned, which is why
`promo_prompts` exists at all — so the pod's client dispatches on it and refuses anything else."""


def committed_registration() -> dict:
    """The pre-registration, refused unless it is committed and unmodified — v5's check, its file.

    Until it is committed nothing stops it from being rewritten once the numbers are in
    ([[preregistration_is_a_file_not_a_constant]])."""
    for argv, message in (
        (["git", "ls-files", "--error-unmatch", str(PREREG)], f"{rel(PREREG)} is not tracked"),
        (["git", "diff", "HEAD", "--quiet", "--", str(PREREG)], f"{rel(PREREG)} differs from HEAD"),
    ):
        if subprocess.run(argv, cwd=REPO_ROOT, capture_output=True).returncode != 0:
            raise SystemExit(
                f"{message} — the committed registration is the one this run is read against, and"
                " it is FROZEN. Commit it before the pack, and never after the pod."
            )
    return load(PREREG)


def build_pack() -> dict:
    """Every UNIT as the pod will be given it, each held to its own rendering sha.

    Built on the Mac and checked again ON the pod: shipping the rendered string would only prove the
    two machines agree about a string, and what has to be true is that the model is shown what the
    registration registered (v5b's `reading`, quoted). The SMOKE's three units come FIRST, because
    the decision table of ruling 03.09 (b) reads their rate before the remaining 37 are bought.
    """
    import run_promo_c2 as c2

    from market_pulse import loop

    record = committed_registration()
    smoke = [one["unit_id"] for one in record["population"]["leg_a"]["smoke"]["units"]]
    leg_a = {}
    for row in dev_threads():
        post, comments = thread_of(row)
        ordered = sorted(comments, key=lambda one: int(one["msg_id"]))
        rendered = promo_prompts.render(row["channel"], row["thread_root"], post, comments)
        leg_a[unit_id(row)] = {
            "id": unit_id(row),
            "thread": unit_id(row),
            "leg": "a",
            "task": PROMO_TASK,
            "channel": row["channel"],
            "post_id": str(row["thread_root"]),
            "post": post,
            # the sender id rides IN the pack: the pod re-renders from these rows and nothing else,
            # so a marker resolved only on the Mac would render two different prompts
            "comments": [
                [int(one["msg_id"]), one.get("text") or "", one.get("sender_anon_id")]
                for one in ordered
            ],
            "rendering_sha256": promo_prompts.extractor_version(rendered),
            "chars": len(rendered),
            "smoke": unit_id(row) in smoke,
        }
    if sorted(smoke) != sorted(one for one in leg_a if leg_a[one]["smoke"]):
        raise SystemExit(f"the registration's smoke units are not in the draw: {smoke}")
    items = [leg_a[one] for one in smoke] + [
        leg_a[one] for one in record["population"]["leg_a"]["order"] if one not in smoke
    ]

    wanted = record["population"]["leg_b"]["by_channel"]
    by_id = {
        f"{handle}:{one['msg_id']}": one for handle, rows in c2.posts().items() for one in rows
    }
    for handle, ids in sorted(wanted.items()):
        for msg_id in ids:
            row = by_id.get(f"{handle}:{msg_id}")
            if row is None:
                raise SystemExit(f"{handle}:{msg_id} is registered and not in the census — stop")
            messages, text = loop.render_post(row)
            # the sha is of the RENDERED request and not of the payload, because that is what the
            # pod re-derives and compares — the two differ by the whole positions instruction, and
            # a pack pinning the payload would refuse every leg-B unit on a healthy pod
            rendered = messages[0]["content"]
            items.append(
                {
                    "id": f"{handle}:{msg_id}",
                    "thread": f"{handle}:{msg_id}",
                    "leg": "b",
                    "task": POST_TASK,
                    "text": text,
                    "rendering_sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
                    "chars": len(rendered),
                    "smoke": False,
                }
            )
    return {
        "phase": STEP,
        "iteration": ITERATION,
        "registration": {"record": rel(PREREG), "sha256": sha256_of(PREREG)},
        "instruments": {
            "leg_a": {
                "task": PROMO_TASK,
                "module": "src/market_pulse/promo_prompts.py",
                "sha256": sha256_of(REPO_ROOT / "src" / "market_pulse" / "promo_prompts.py"),
                "codebook_version": promo_prompts.codebook_version(),
                "template_sha256": promo_prompts.template_version(),
            },
            "leg_b": {"task": POST_TASK, "module": "src/market_pulse/prompts.py — REGISTERED"},
            "prompt_sha256": prompt_shas(),
            "parser": {"sha256": sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py")},
        },
        "task": PROMO_TASK,
        "reading": "the pod renders each item ITSELF and refuses unless its sha equals the one"
        " pinned here; the rendered string never travels",
        "serving": {
            "adapter": None,
            "merge_state": "base-no-adapter",
            "chat_template": {"add_generation_prompt": True, "enable_thinking": False},
            "decoding": "greedy",
            "do_sample": False,
            "forward_batch_size": 1,
            "model": "google/gemma-4-31b-it",
            "model_revision": "842da3794eaa0b77d5f08bae87a17459d91ff475",
            "serving_config": "READER",
            "output_tokens": OUTPUT_TOKENS,
        },
        "smoke_ids": smoke,
        "items": items,
    }


RUN_RECORD = REPO_ROOT / "results" / "promo_dev_loop_run.json"


def score(replies: Path, iteration: int) -> dict:
    """The pod's replies → the grader's rows and the error table. $0, and after the pod is gone.

    The pod writes the reader family's row (`id`, `reply`, `balanced`, timings); K8 scores the GOLD
    shape (one row per comment). Nothing joined the two, so this does — and it invents no metric:
    `grade_promo_signals` is the judge and its own functions produce every number here
    ([[a_number_typed_into_its_own_checker]]). What the table adds is what a grade cannot say —
    which comments were missed and what the model said instead, and how many answers never parsed,
    counted by cause ([[empty_class_eats_the_parse_failures]]).

    Iteration 1 is the BASELINE, so an unparseable answer is COUNTED and never repaired: answer
    repair is a knob ruling 03.09 (c) item 3 gives iterations 2–5, each a new extractor_version.
    """
    import grade_promo_signals as k8

    units = {item["id"]: item for item in load(PACK)["items"] if item["leg"] == "a"}
    rows: list[dict] = []
    failures: list[dict] = []
    answered: list[str] = []
    fenced = 0
    for line in replies.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        reply = json.loads(line)
        item = units.get(reply["id"])
        if item is None:
            continue  # leg B rides the same out-file and is not leg A's gold
        answered.append(reply["id"])
        answer = promo_prompts.parse(reply["reply"])
        fenced += 1 if answer.get("fenced") else 0
        if answer["parse_failure"]:
            failures.append(
                {
                    "unit_id": reply["id"],
                    "cause": answer["parse_failure"],
                    "balanced": reply.get("balanced"),
                    "finish_reason": reply.get("finish_reason"),
                    "emitted_chars": reply.get("emitted_chars"),
                }
            )
        where = {"channel": item["channel"], "thread_root": item["post_id"]}
        stamp = {"extractor_version": reply["rendering_sha256"]}
        placed = predicted_rows(where, answer)
        rows += [one | stamp for one in placed]
        said = {one["msg_id"] for one in placed}
        # an abstention is an answer: the model's `unsure` comments become rows that carry no
        # subject, so the grader's own reading counts them instead of reporting a silent zero
        rows += [
            where
            | stamp
            | {
                "msg_id": str(one.get("msg_id")),
                "subject_type": None,
                "subject": None,
                "source": None,
                "signal_types": [],
                "unsure": one.get("reason") or True,
            }
            for one in answer["unsure"]
            if str(one.get("msg_id")) not in said
        ]

    gold = k8.rows(GOLD)
    strata = k8.strata_of(DRAW, PART)
    graded = k8.grade(gold, rows, strata)
    said_rows = {(k8.thread_key(one), str(one["msg_id"])): one for one in rows if one.get("msg_id")}
    misses = []
    for one in gold:
        if not one.get("msg_id"):
            continue
        found = said_rows.get((k8.thread_key(one), str(one["msg_id"])))
        if found is not None and k8.subject(found) == k8.subject(one):
            continue
        misses.append(
            {
                "channel": one.get("channel"),
                "thread_root": str(one.get("thread_root")),
                "msg_id": str(one["msg_id"]),
                "gold": {key: one.get(key) for key in ("subject_type", "subject", "signal_types")},
                "model": found
                and {
                    key: found.get(key)
                    for key in ("subject_type", "subject", "signal_types", "unsure")
                },
            }
        )
    # ponytail: 40 threads × 140 rows — the filter is O(n²) and runs in milliseconds
    jaccard = {
        f"{key[0]}:{key[1]}": k8.agree(
            [one for one in gold if k8.thread_key(one) == key],
            [one for one in rows if k8.thread_key(one) == key],
        )["signal_type_agreement"]
        for key in sorted({k8.thread_key(one) for one in gold})
    }
    causes: dict[str, int] = {}
    for one in failures:
        causes[str(one["cause"]).split(":")[0]] = causes.get(str(one["cause"]).split(":")[0], 0) + 1
    return {
        "contract": f"docs/plans/promo-pulse-1.md §9 — the error table of iteration {iteration}",
        "iteration": iteration,
        "replies": rel(replies),
        "rows": rows,
        "answers": {
            "leg_a_units_answered": len(answered),
            "leg_a_units_registered": len(units),
            "gold_shaped_rows": len(rows),
            "parse_failures": len(failures),
            "fenced_answers": fenced,
            "fenced_note": "the codebook asks for JSON and never forbids a markdown fence; the"
            " object inside it is read as it stands and nothing in it is repaired"
            " (promo_prompts.unfence)",
            "parse_failures_by_cause": causes,
            "unparsed": failures,
        },
        "grade": {
            "from": "scripts/grade_promo_signals.py — its own functions, never re-derived here",
            "bars": graded["bars"],
            "whole_40": graded["whole_40"],
            "by_stratum": graded["by_stratum"],
            "readings": graded["readings"],
        },
        "subject_misses_total": len(misses),
        "subject_misses_rule": "the first ten in the GOLD file's own order — a rule, not a pick;"
        " the total stands beside them",
        "subject_misses": misses[:10],
        "signal_jaccard_per_thread": jaccard,
    }


def run_state() -> dict:
    return load(RUN_RECORD) if RUN_RECORD.exists() else {"phase": STEP, "segments": [], "gates": []}


def append_gate(state: dict, kind: str, gate: dict) -> dict:
    """Every WAIT/GO/KILL snapshot APPENDED, none overwritten — v5's rule, its shape.

    A gate verdict that lives only in the transcript is prose, and prose is not the gate
    ([[gate_verdicts_need_an_artifact]])."""
    segment = state["segments"][-1] if state["segments"] else {}
    state["gates"].append(
        {
            "kind": kind,
            "at": datetime.now(UTC).isoformat(timespec="seconds"),
            "segment": len(state["segments"]),
            "pod_id": segment.get("pod_id"),
            **gate,
        }
    )
    state["latest"] = {"kind": kind, "verdict": gate["verdict"], "at": state["gates"][-1]["at"]}
    RUN_RECORD.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return state


def open_segment(*, pod_id: str, created_at: str, usd_per_hour: float, card: str) -> dict:
    """Rung 1 at the create, on the numbers the create RESPONSE gave.

    The registration priced the step at an offer read on the day; the meter bills what the response
    says. A pod whose price came back above the registered one is a different pod's price and the
    run stops before a single token — the cap was computed against the other number."""
    record = committed_registration()
    registered = float(record["rung_0"]["price"]["usd_per_hour"])
    state = run_state()
    if any(one.get("deleted_at") is None for one in state["segments"]):
        raise SystemExit(
            "a segment of this attempt is still OPEN — never two pods at once, and the check runs"
            " BEFORE the second create rather than as a refusal after the second meter started."
        )
    state["segments"].append(
        {
            "pod_id": pod_id,
            "created_at": created_at,
            "usd_per_hour": usd_per_hour,
            "card": card,
            "deleted_at": None,
        }
    )
    hard_stop = float(record["rung_0"]["hard_stop_seconds"])
    gate = {
        "verdict": "GO" if usd_per_hour <= registered and card == record["rung_0"]["price"]["card"]
        else "KILL",
        "rule": "rung 1: the create response's costPerHr ≤ the registered price, and the card is"
        " the registered card. Delete on KILL — the cap was computed against the other number",
        "usd_per_hour": usd_per_hour,
        "registered_usd_per_hour": registered,
        "card": card,
        "registered_card": record["rung_0"]["price"]["card"],
        "hard_stop_seconds": hard_stop,
        "terminate_after_minutes": int(record["gates"]["terminate_after_minutes"]),
        "backstop_fits": record["gates"]["terminate_after_minutes"] * 60 <= hard_stop,
        "cap_usd": float(record["step"]["cap_usd"]),
        "usd_at_the_backstop": round(
            record["gates"]["terminate_after_minutes"] * 60 * usd_per_hour / 3600, 4
        ),
    }
    return append_gate(state, "price", gate)


MEASURED_RATE = "promo_dev40_seconds_per_thread"
"""This instrument's OWN name in `results/measurements.jsonl`. The borrow
(`pass2_r2_seconds_per_thread`, another prompt and another pod) is never reused after the smoke —
plan §9, and [[the_smokes_rate_carries_the_smokes_transport]]."""


def project(replies: Path) -> dict:
    """The smoke's own rate, and ruling 03.09 (b)'s verdict on it. $0, on a pod that is waiting.

    The gate that decides whether the remaining 37 threads are bought must not be a number typed
    into its own decision, so the projection is `corner()` — the very function that priced the
    registration's three corners — fed the MEASURED seconds instead of the borrowed ones. Same
    shape, same units, same cap: the bands were written against that arithmetic.

    Two readings, one verdict. The band is read at the MEAN, because the smoke's three units are
    chosen to SPAN the population (shortest, median, longest) and their mean is what estimates it;
    the max is a deliberately worst-case draw and projecting all 40 at it would refuse a loop the
    sample was built to price. The max is still decisive for MONEY: a max corner above the cap is a
    KILL whatever band the mean falls in ([[a_reproducible_probe_can_be_unrepresentative]]).
    """
    record = committed_registration()
    smoke = record["population"]["leg_a"]["smoke"]["units"]
    rows = {}
    for line in replies.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row["id"]] = row
    missing = [one["unit_id"] for one in smoke if one["unit_id"] not in rows]
    if missing:
        raise SystemExit(
            f"{rel(replies)} carries no reply for {missing} — the smoke's own units are the rate's"
            " only sample, and a projection over a partial smoke prices a population nothing"
            " measured. Wait for the three, or STOP."
        )
    seconds = [float(rows[one["unit_id"]]["seconds"]) for one in smoke]
    price = record["rung_0"]["price"]
    threads = record["population"]["leg_a"]["threads"]
    common = {
        "n_threads": SMOKE_N + threads,
        "n_posts": record["population"]["leg_b"]["posts"],
        "s_post": float(load(PREREG_5C2)["prices"]["post_text"]["seconds_model"]["value"]),
        "overhead": float(record["rung_0"]["overhead"]["seconds"]),
        "usd_per_second": float(price["usd_per_hour"]) / 3600.0,
        "cap": float(record["step"]["cap_usd"]),
    }
    mean = corner("measured mean", s_thread=sum(seconds) / len(seconds), **common)
    worst = corner("measured max", s_thread=max(seconds), **common)
    bands = record["decision_table"]["after_the_smoke_for_40_threads"]
    usd = mean["usd"]
    verdict = "GO" if usd <= 0.80 else ("GO-THEN-STOP" if usd <= 1.20 else "NO-GO")
    if not worst["fits"]:
        verdict = "KILL"
    return {
        "verdict": verdict,
        "rule": "ruling 03.09 (b), quoted and not moved — the band is read at the MEAN corner; a"
        " MAX corner over the cap is a KILL whatever the band says",
        "bands": bands,
        "usd_at_the_measured_mean": mean["usd"],
        "usd_at_the_measured_max": worst["usd"],
        "corners": [mean, worst],
        "measured": {
            "name": f"{STEM}_seconds_per_thread",
            "seconds": {one["unit_id"]: rows[one["unit_id"]]["seconds"] for one in smoke},
            "value": round(sum(seconds) / len(seconds), 3),
            "max": round(max(seconds), 3),
            "n": len(seconds),
            "replaces": BORROWED_RATE,
        },
        "replies": rel(replies),
    }


def write_measurement(gate: dict) -> dict:
    """The smoke's rate into `results/measurements.jsonl`, under its OWN name and never the borrow's."""
    row = {
        "contract": "promo-pulse-1-s9",
        "name": f"{STEM}_seconds_per_thread",
        "instrument": "promo-signal prompt (leg A), READER serving, thinking OFF, batch 1 — the"
        f" SMOKE's three units on this pod; it replaces the borrowed {BORROWED_RATE}",
        "measured_on": ", ".join(f"{unit} {seconds}s" for unit, seconds in gate["measured"]["seconds"].items()),
        "n": gate["measured"]["n"],
        "unit": "seconds",
        "value": gate["measured"]["value"],
        "max": gate["measured"]["max"],
        "source": rel(RUN_RECORD),
    }
    with MEASUREMENTS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return row


def close_segment(*, deleted_at: str, billed_seconds: float, outcome: str) -> dict:
    """The segment's own bill, at its OWN price. Never a balance delta — that prices the account."""
    state = run_state()
    if not state["segments"] or state["segments"][-1].get("deleted_at"):
        raise SystemExit("no segment is open — there is nothing to close")
    segment = state["segments"][-1]
    segment["deleted_at"] = deleted_at
    segment["billed_seconds"] = billed_seconds
    segment["billed_usd"] = round(billed_seconds * float(segment["usd_per_hour"]) / 3600, 6)
    segment["outcome"] = outcome
    spent = sum(float(one.get("billed_usd") or 0) for one in state["segments"])
    cap = float(committed_registration()["step"]["cap_usd"])
    return append_gate(
        state,
        "close",
        {
            "verdict": "GO" if spent <= cap else "OVER",
            "billed_seconds": billed_seconds,
            "billed_usd": segment["billed_usd"],
            "spent_all_segments_usd": round(spent, 6),
            "cap_usd": cap,
            "left_usd": round(cap - spent, 6),
            "outcome": outcome,
        },
    )


def use_part(part: str, *, gold: Path | None = None, step: str | None = None) -> None:
    """Point this module's file constants at ONE half of the draw. `dev` is what they already are.

    Called once, from `main`, before any branch reads them — so a process is about the dev loop or
    about the holdout and never about both. `--gold` and `--step` override afterwards, because §4
    makes a re-used producer take its paths as parameters and the holdout's gold is a pin the paid
    session names on the command line."""
    global PART, GOLD, PREP, PREREG, PACK, RUN_RECORD, STEP, STEM
    if part not in ("dev", "holdout"):
        raise SystemExit(f"--part {part}: the draw has two halves, dev and holdout, and no third")
    if part != "dev":
        PART, STEM = part, HOLDOUT_FILES["stem"]
        GOLD, PREP = HOLDOUT_FILES["gold"], HOLDOUT_FILES["prep"]
        PREREG, PACK = HOLDOUT_FILES["prereg"], HOLDOUT_FILES["pack"]
        RUN_RECORD, STEP = HOLDOUT_FILES["run"], HOLDOUT_FILES["step"]
    if gold is not None:
        GOLD = gold
    if step is not None:
        STEP = step


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--part", default="dev", choices=("dev", "holdout"), help="which half of the frozen draw"
    )
    parser.add_argument("--gold", type=Path, help="the part's answer key; the registration pins it")
    parser.add_argument("--step", help="the money step this part spends under, and its own ledger")
    parser.add_argument("--cap", type=float, help="the step's cap in USD — the operator's number")
    parser.add_argument("--render", metavar="THREAD_ROOT")
    parser.add_argument("--channel", default=None, help="disambiguate a root two channels share")
    parser.add_argument("--dry-run", action="store_true", help="$0: the corpus, its sizes, the bound")
    parser.add_argument(
        "--register", action="store_true", help="$0: rung 0 and the pre-registration"
    )
    parser.add_argument(
        "--pack", action="store_true", help="$0: the units as the pod will be given them"
    )
    parser.add_argument("--open", action="store_true", help="$0: rung 1 at the create response")
    parser.add_argument("--close-segment", action="store_true", help="$0: the segment's own bill")
    parser.add_argument(
        "--score", action="store_true", help="$0: the pod's replies → K8's rows and the error table"
    )
    parser.add_argument(
        "--project", action="store_true", help="$0: the smoke's rate and the decision table"
    )
    parser.add_argument(
        "--leak-check", action="store_true", help="$0: no string of the law is a store comment"
    )
    parser.add_argument(
        "--suffix",
        default="",
        help="names a $0 RE-reading beside the paid files, never over them (ruling 04.09 (g) 4)",
    )
    parser.add_argument("--replies", type=Path, help="the out-file the pod wrote")
    parser.add_argument("--iteration", type=int, help="names the two files this iteration keeps")
    parser.add_argument("--pod-id")
    parser.add_argument("--created-at")
    parser.add_argument("--deleted-at")
    parser.add_argument("--usd-per-hour", type=float)
    parser.add_argument("--billed-seconds", type=float)
    parser.add_argument("--card")
    parser.add_argument("--outcome")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    use_part(args.part, gold=args.gold, step=args.step)

    if args.register:
        record = register(args.cap)
        out = args.out or PREREG
        out.write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"\nwrote {rel(out)}")
        floor = record["step"]["floor_usd"]
        print(
            f"  step          {record['step']['name']} · cap ${record['step']['cap_usd']:.4f}"
            f" = {record['step']['cap_rule']} · floor "
            + (f"${floor:.2f}" if floor is not None else "none — the ONE shot has no floor to"
               " refuse below; the cap is the hard stop (ruling 05.09 (q) 3)")
        )
        print(
            f"  population    leg A {record['population']['leg_a']['threads']} threads"
            f" (smoke {SMOKE_N}: "
            + ", ".join(
                f"{one['role']} {one['unit_id']} {one['chars']}c"
                for one in record["population"]["leg_a"]["smoke"]["units"]
            )
            + f") · leg B {record['population']['leg_b']['posts']} posts"
        )
        print(render_rung_0(record["rung_0"]))
        return 0 if record["rung_0"]["fits"] else 1

    if args.open:
        for name in ("pod_id", "created_at", "usd_per_hour", "card"):
            if getattr(args, name) is None:
                parser.error(f"--open needs --{name.replace('_', '-')}: a pod that exists against"
                             " no counter is a pod nothing is measuring")
        state = open_segment(
            pod_id=args.pod_id,
            created_at=args.created_at,
            usd_per_hour=args.usd_per_hour,
            card=args.card,
        )
        print(json.dumps(state["gates"][-1], ensure_ascii=False, indent=1))
        return 0 if state["latest"]["verdict"] == "GO" else 1

    if args.close_segment:
        for name in ("deleted_at", "billed_seconds", "outcome"):
            if getattr(args, name) is None:
                parser.error(f"--close-segment needs --{name.replace('_', '-')}")
        state = close_segment(
            deleted_at=args.deleted_at,
            billed_seconds=args.billed_seconds,
            outcome=args.outcome,
        )
        print(json.dumps(state["gates"][-1], ensure_ascii=False, indent=1))
        return 0 if state["latest"]["verdict"] == "GO" else 1

    if args.project:
        if args.replies is None:
            parser.error("--project needs --replies: the smoke's own out-file is the only sample")
        gate = project(args.replies)
        state = append_gate(run_state(), "smoke", gate)
        row = write_measurement(gate)
        print(json.dumps(state["gates"][-1], ensure_ascii=False, indent=1))
        print(f"\nmeasured {row['name']} = {row['value']} s/thread (max {row['max']}, n={row['n']})"
              f" — appended to {rel(MEASUREMENTS)}, and it replaces {BORROWED_RATE}")
        print(f"the pass projects to ${gate['usd_at_the_measured_mean']} at the measured mean and"
              f" ${gate['usd_at_the_measured_max']} at its max, against the cap"
              f" ${gate['corners'][0]['cap_usd']}")
        print(f"VERDICT {gate['verdict']} — {gate['rule']}")
        return 0 if gate["verdict"] in ("GO", "GO-THEN-STOP") else 1

    if args.leak_check:
        record = leak_check(store_texts())
        LEAK_CHECK.write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {rel(LEAK_CHECK)}")
        print(f"  corpus     {record['corpus']['comments_with_text']} comments with text"
              f" ({record['corpus']['dev']} dev + {record['corpus']['holdout']} holdout)")
        for name, block in sorted(record["populations"].items()):
            print(f"  {name:<10} {block['literals']} literals — {block['rule']}")
        for hit in record["hits"]:
            print(f"  LEAK       [{hit['population']}] «{hit['literal']}»"
                  f" is in {hit['split']} {hit['unit']}")
        print(f"VERDICT {record['verdict']} — codebook {record['codebook_version'][:16]}…"
              f" · template {record['template_version'][:16]}…")
        return 0 if record["verdict"] == "CLEAN" else 1

    if args.score:
        for name in ("replies", "iteration") if PART == "dev" else ("replies",):
            if getattr(args, name) is None:
                parser.error(f"--score needs --{name}")
        table = score(args.replies, args.iteration)
        rows = table.pop("rows")
        tag = f"_iter{args.iteration}" if PART == "dev" else ""
        out = REPO_ROOT / "results" / f"{STEM}_predicted{tag}{args.suffix}.jsonl"
        out.write_text(
            "".join(json.dumps(one, ensure_ascii=False, sort_keys=True) + "\n" for one in rows),
            encoding="utf-8",
        )
        errors = REPO_ROOT / "results" / f"{STEM}_errors{tag}{args.suffix}.json"
        errors.write_text(
            json.dumps(table, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        answers = table["answers"]
        print(f"wrote {rel(out)} — {len(rows)} rows from {answers['leg_a_units_answered']} of"
              f" {answers['leg_a_units_registered']} leg-A units"
              f" · {answers['parse_failures']} unparsed {answers['parse_failures_by_cause'] or ''}")
        print(f"wrote {rel(errors)} — {table['subject_misses_total']} subject misses, top 10 named")
        for name, block in sorted(table["grade"]["bars"].items()):
            print(f"  {name:<24} {block['value']} against {block['bar']}"
                  f" — {'HOLDS' if block['held'] else 'RED'}")
        return 0

    if args.pack:
        pack = build_pack()
        PACK.write_text(
            json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        legs = {"a": 0, "b": 0}
        for item in pack["items"]:
            legs[item["leg"]] += 1
        print(f"wrote {rel(PACK)}")
        print(f"  registration  {pack['registration']['record']} sha {pack['registration']['sha256'][:16]}…")
        print(f"  units         leg A {legs['a']} threads · leg B {legs['b']} posts")
        print(f"  smoke first   {', '.join(pack['smoke_ids'])}")
        print(f"  codebook      {pack['instruments']['leg_a']['codebook_version'][:16]}…")
        return 0

    if args.dry_run:
        record = prep()
        out = args.out or PREP
        out.write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        bound, corpus = record["bound"], record["corpus"]
        own = bound["borrowed_from"]["name"] == MEASURED_RATE
        print(f"wrote {rel(out)}")
        print(f"  law           {record['law']['codebook']} sha {record['law']['codebook_sha256'][:16]}…")
        print(f"  corpus        {bound['threads']} {PART} threads · {corpus['chars_total']} chars ·"
              f" longest {corpus['chars_max']} · {corpus['distinct_renders']} distinct renders")
        print(f"  gold          {record['gold']['path']} — "
              + (f"sha {record['gold']['sha256'][:16]}… · {record['gold']['lines']} rows"
                 if record["gold"]["sha256"] else "gold missing -> no record"))
        print(f"  {'MEASURED' if own else 'BORROWED'} rate {bound['borrowed_from']['name']} ="
              f" {bound['borrowed_from']['value']} s/thread (n={bound['borrowed_from']['n']},"
              f" max {bound['borrowed_from']['max']}) — "
              + ("this instrument's OWN, on the slowest pod it has run on"
                 if own else "another prompt, pod and transport"))
        print(f"  bound         ${bound['usd_at_the_borrowed_mean']} at its mean ·"
              f" ${bound['usd_at_the_borrowed_max']} at its max, boot excluded — NOT a price")
        print(f"  priced at     ${bound['usd_per_second'] * 3600:.4f}/h from {rel(RATE_RECORD)} —"
              " NOT the cap's rate and NOT a gate: rung 0 at --register prices the pod at the"
              " day's own offer, and that is the number a cap is read against")
        return 0

    if not args.render:
        parser.error("choose --render or --dry-run")

    found = [
        row
        for row in dev_threads()
        if str(row["thread_root"]) == str(args.render)
        and (args.channel is None or row["channel"] == args.channel)
    ]
    if len(found) != 1:
        raise SystemExit(
            f"--render {args.render}: {len(found)} dev threads match"
            f"{' in ' + args.channel if args.channel else ''} — name --channel to pick one"
        )
    rendered = render_thread(found[0])
    print(rendered)
    print()
    print(f"--- codebook_version  {promo_prompts.codebook_version()}")
    print(f"--- extractor_version {promo_prompts.extractor_version(rendered)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
