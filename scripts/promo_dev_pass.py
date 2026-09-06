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
import reader_v5_pod_runner as pod_runner  # noqa: E402

from market_pulse import promo_prompts  # noqa: E402

DRAW = REPO_ROOT / "results" / "promo_threads_draw.json"
DRAW2 = REPO_ROOT / "results" / "promo_threads_draw_2.json"
"""The second draw — holdout-2 alone, ruling 05.09 (s) item 3 (b). Its own file, because the first
draw is frozen and pinned by every registration already spent against it."""
CODEBOOK = REPO_ROOT / "docs" / "CODEBOOK-promo-signals.md"
GOLD = REPO_ROOT / "docs" / "labels-promo-dev.jsonl"
MEASUREMENTS = REPO_ROOT / "results" / "measurements.jsonl"
RATE_RECORD = REPO_ROOT / "results" / "srv2d_cost.json"
PREP = REPO_ROOT / "results" / "promo_dev40_prep.json"

PART = "dev"
"""Which LEG this process is about — `dev`, `holdout` or `holdout2`, and never two of them.

The first draw (`results/promo_threads_draw.json`) named 20 + 20 of each stratum at seed 42 and
froze them disjoint; the dev half took the bar over five iterations and the holdout half was the ONE
shot ruling 05.09 (q) priced — spent, read RED on subject, relabelled `dev-2` by (s) item 3. The
second draw (`DRAW2`) holds holdout-2, the exam that has not been sat (ruling 06.09 (z) item 4).
All three are the SAME instrument over different rows, so this module is one module with a part,
not a fork of itself ([[a_moved_guard_that_left_its_copy]]). `use_part` rebinds the file constants
below — the draw among them — and every function reads them by name, the mechanism
`tests/test_promo_dev_pass.py`'s own fixture already uses to redirect the run record."""

ARMS: tuple[str, ...] = ("dev",)
"""Which arms of this leg's DRAW its population IS, in the order the pod answers them. Bound by
`use_part` from `DEV_FILES`/`HOLDOUT_FILES`/`HOLDOUT2_FILES` — a part is a leg, and a leg may be
more than one arm since ruling 05.09 (s) item 3 relabelled the spent holdout-40 as `dev-2`."""

ARM: str | None = None
"""Which arm of this leg the SCORER is grading, or None on a leg of one arm. Bound by `use_arm`
from `DEV_ARMS` — the label (`dev40`, `dev2`) and the draw's part name (`dev`, `holdout`) are two
namespaces that happen to overlap on one word, so the arm is named by its label everywhere and the
draw part is read out of the map ([[id_spaces_that_look_comparable]])."""

CONTRACT = "promo-pulse-1-s9"
"""What every measurement row of THIS instrument is written under — the dev loop's and the
holdout's alike, because ruling 05.09 (q) item 2 froze one instrument across both legs."""

WHOLE_RUN = "whole run"
"""The `sample` field that separates a row a leg may be PRICED on from a row that is history.
Ruling 05.09 (t) item 4: n is the run's own units, never a smoke of three. A field and not a size —
`n == 3` would misread the day a run of three units is bought ([[a_default_is_a_marker_when_nothing_takes_it]])."""

BORROWED_RATE = "pass2_r2_seconds_per_thread"
"""The nearest MEASURED seconds-per-thread in the house — READER, thinking off, 75 cooled threads.
Named, never typed: :func:`borrowed_rate` reads it out of `results/measurements.jsonl` and carries
the row's own `instrument` and `n` into the record, so a reader sees what was borrowed from where."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def dev_threads(path: Path | None = None, arms: tuple[str, ...] | None = None) -> list[dict]:
    """This leg's rows — arm by arm in the ORDER given, both strata, in the record's own order.

    A leg was one arm of the draw until ruling 05.09 (s) item 3 turned the spent holdout-40 into
    `dev-2`; iteration 4's leg A is dev-40 AND dev-2, dev-40 FIRST because the bar is dev-40's and
    dev-2 is a reading the hard stop may cut (ruling 05.09 (t) item 5). The order is the pod's, so
    it is the record's: what a hard stop cuts is the tail.

    The draw is the PART's — `DRAW` as `use_part` last bound it — read at the call and never as a
    default argument: a default is frozen into the signature at import, and holdout-2 would have
    been read out of the very draw it was drawn to be disjoint from.
    """
    body = json.loads((path or DRAW).read_text(encoding="utf-8"))
    return [
        row
        for arm in (arms or ARMS)
        for stratum in sorted(body["draw"])
        for row in body["draw"][stratum][arm]
    ]


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


CORPUS = (
    ("dev-40", DRAW, "dev"),
    ("dev-2", DRAW, "holdout"),
    ("holdout-2", DRAW2, "holdout"),
)
"""Every set the law may not have read, and the draw arm each one is. Ruling 05.09 (s) item 5 asks
for the check over all three: dev-40 is the bar, dev-2 is the burned holdout-40 relabelled, and
holdout-2 is the exam that has not been sat. The list is INDEPENDENT of `--part` — a leak is the
instrument having seen its own exam, and which leg is being registered does not change what it read
([[the_instruments_examples_came_from_the_exam]])."""


def store_texts(corpus=CORPUS) -> list[dict]:
    """Every comment with text of every set in `corpus`, from the frozen archive the draws read."""
    return [
        {
            "split": split,
            "channel": row["channel"],
            "thread_root": str(row["thread_root"]),
            "msg_id": str(one["msg_id"]),
            "text": " ".join((one.get("text") or "").split()),
        }
        for split, path, arm in corpus
        for body in [json.loads(path.read_text(encoding="utf-8"))]
        for stratum in sorted(body["draw"])
        for row in body["draw"][stratum][arm]
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
        " string of the rendered law is a substring of a comment of ANY set the law will be graded"
        " on; ruling 05.09 (s) item 5 names the three: dev-40, dev-2 and holdout-2",
        "codebook_version": promo_prompts.codebook_version(),
        "template_version": promo_prompts.template_version(),
        "corpus": {
            "comments_with_text": len(texts),
            "by_split": {
                split: sum(1 for one in texts if one["split"] == split)
                for split in dict.fromkeys(one["split"] for one in texts)
            },
            "from": ", ".join(sorted({rel(path) for _, path, _ in CORPUS}))
            + " + the frozen v1 archive data/raw",
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


def reply_rows(replies: Path) -> list[dict]:
    """Every WHOLE row an out-file carries, under the POD's own rule and not a second spelling of it.

    Ruling 05.09 (x) item 4, the first half. `smoke_state` runs while the pod is billing, on a file
    `scp` copied WHILE the pod was still appending to it, so its final line can be half written —
    and `json.loads` on it raised, which read as «the tool is broken» at the one moment a reading
    decides whether to delete a live pod ([[a_crash_must_write_into_the_file_its_reader_opens]]).
    `reader_v5_pod_runner.whole_lines` is the shipped rule — forgive the LAST line, refuse a torn one
    anywhere else, because that is a damaged file and not the mid-write race — and it is IMPORTED
    rather than restated: `promo_dev_pod_runner.rows_of` already reads its crash file through it, and
    two spellings of one rule drift ([[a_moved_guard_that_left_its_copy]]). A dropped last line simply
    leaves its unit unanswered, which every reader below already has a word for.
    """
    return pod_runner.whole_lines(replies.read_text(encoding="utf-8"), str(replies))[0]


def died(row: dict) -> bool:
    """Is this reply row a unit's DEATH — the ONE spelling every reader below keys on.

    Ruling 06.09 (y) item 4, risk 2 (fixed under (z) item 3, on the Mac side only). Five readers
    keyed on a truthy `error`, and `error` is `str(exc)` — an exception raised with an EMPTY
    message (`RuntimeError()`: `str()` of it is `""`) wrote `"error": ""`, which read as an
    ANSWERED row everywhere: the smoke as «3 replies are in», the rate row as a unit with no
    `seconds`, the grader as an answer to parse. The runner (PINNED — it does not move for this)
    always writes the `exception` field beside the message, so presence of THAT field is the
    death; a truthy `error` still counts, for a row written by hand.
    """
    return "exception" in row or bool(row.get("error"))


def answered_rows(replies: Path) -> dict[str, dict]:
    """The out-file's ANSWERED rows by unit id — the ERROR replies left out, never dying on them.

    Ruling 05.09 (x) item 4, the second half. A unit that died carries `id`, `error`, `exception` and
    `unanswered` and no `seconds` and no `reply` (ruling (w) item 3, the pod half), so every reader
    that joins on the id has to say what such a row MEANS. It means UNANSWERED: the rate row must not
    average a unit nothing measured, the grader must not parse an answer nobody gave, and neither may
    raise a `KeyError` on the field the dead row does not have — `--close-segment` writes its money
    gate BEFORE the rate row, so a traceback there loses the measurement and keeps the bill
    ([[a_guard_that_runs_after_the_write]]).

    `smoke_state` is the one reader that does NOT use this: an error reply is the whole point there,
    and it reads `reply_rows` directly.
    """
    return {
        row["id"]: row
        for row in reply_rows(replies)
        if row.get("id") is not None and not died(row)
    }


def dead_units(replies: Path) -> list[str]:
    """The ids of the units an out-file records as DEAD — reported wherever they are skipped.

    A skip nobody counts is a silence, and a silence reads as «there was nothing there»
    ([[a_checker_whose_failure_is_silence]])."""
    return [str(row.get("id")) for row in reply_rows(replies) if died(row)]


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def measurement_rows() -> list[dict]:
    """Every row of `results/measurements.jsonl`, read once and never retyped."""
    return [
        json.loads(line)
        for line in MEASUREMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def borrowed_rate() -> dict:
    """The named measurement row, or a refusal. A projection with no named rate projects nothing —
    `scripts/project_think_zero_shot.py:107`'s rule, applied to an instrument that has none yet.

    Ruling 05.09 (t) item 4 retires the borrow as a PRICE on every leg; this stays because
    `sibling_overhead` reads it to undo the sibling's own generation from the sibling's own bill.
    """
    for row in measurement_rows():
        if row["name"] == BORROWED_RATE:
            return row
    raise SystemExit(
        f"{BORROWED_RATE} is not in results/measurements.jsonl — this leg has no rate of its own"
        " and no rate to borrow, so it prices nothing. The smoke writes it."
    )


def own_rate() -> dict:
    """This instrument's OWN seconds-per-thread over WHOLE RUNS — ruling 05.09 (t) item 4.

    A smoke of three built to hold the LONGEST thread is a maximum, not a mean. The three smoke
    rows this file already carries priced iteration 4 at 88.772 s/thread — three times anything the
    instrument has ever actually run at — and no corner fitted. They stay as history and price
    nothing ([[a_smoke_drawn_from_the_exam_is_not_a_rate_sample]]). What prices is the whole run:
    n is the run's own units, mean and max over all of them.

    The pool is the INSTRUMENT's, not one leg's. Ruling 05.09 (q) item 2 froze the instrument byte
    for byte across the dev loop and the holdout, and a pace is a property of the pod
    ([[a_rate_is_a_property_of_the_pod]]) — which is why (t) item 4 prices iteration 4 off
    iteration 3's 47.7 while naming the holdout's 25.8 and iteration 2's 17.7 as the fast hosts.
    The per-part NAMES stay, so every row says which population it was timed over; what they may
    not do is decide which rows a POD's pace is chosen from. The rule
    [[a_second_population_in_a_shared_store_voids_the_first_seal]] guards a GRADED population, and
    nothing here is graded.

    The two corners are read off two rows on purpose: the MEAN corner takes the slowest pod's
    whole-run mean, the DEAR corner the largest max any pod produced. Today one row carries both,
    and a rule that holds only because two maxima coincide is a rule that holds for the wrong
    reason ([[an_inequality_that_holds_for_the_wrong_reason]]).
    """
    rows = [
        row
        for row in measurement_rows()
        if row.get("contract") == CONTRACT and row.get("sample") == WHOLE_RUN
    ]
    if not rows:
        raise SystemExit(
            f"no «{WHOLE_RUN}» row of contract {CONTRACT} is in results/measurements.jsonl — ruling"
            " 05.09 (t) item 4 prices every leg on a whole run's own mean, and a smoke of three"
            " prices nothing. `--measure-run --replies <the pod's out-file> --pod-id <id>` writes"
            " the row from the run record; then price."
        )
    slowest = max(rows, key=lambda row: row["value"])
    dearest = max(rows, key=lambda row: row["max"])
    return slowest | {
        "max": dearest["max"],
        "value_from": f"{slowest['name']} — {slowest['measured_on']}",
        "max_from": f"{dearest['name']} — {dearest['measured_on']}",
        "pool": sorted(f"{row['name']} {row['value']}/{row['max']} n={row['n']}" for row in rows),
    }


def rate_for(part: str) -> dict:
    """The seconds-per-thread a leg is priced at — `own_rate()`, on EVERY leg (ruling 05.09 (t) 3).

    Ruling 04.09 (o) item 4 retired the borrow and this function did not: it asked `own_rate()` on
    the holdout and went on handing the dev loop another prompt's pod, which is how iteration 4 came
    to be priced at 23.760 s/thread months after the instrument had a pace of its own
    ([[the_hardening_did_not_reach_the_sibling_reader]]). `part` stays in the signature because the
    caller has one and the record says which leg was priced.
    """
    return own_rate()


def prep(part: str | None = None, gold: Path | None = None) -> dict:
    """The part's corpus as the model will read it, its sizes, and the ask BOUNDED, not priced."""
    part, gold = part or PART, gold or GOLD
    rows = dev_threads()
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
        ), "covers": "the BAR arm of this leg, dev-40. A leg of two arms has two answer keys"
        " and BOTH are pinned: the reading arm dev-2's is docs/labels-promo-dev2.jsonl and the"
        " registration carries it among `pinned_inputs` beside this one (ruling 05.09 (u) item 2 —"
        " a reading needs its reference pinned as much as a bar does). `--score --arm dev40` and"
        " `--score --arm dev2` grade each arm against its own key, over its own units, in its own"
        " part of the draw."
        if len(ARMS) > 1 else "this leg's only arm"} if gold.exists() else {
            "path": rel(gold),
            "sha256": None,
            "lines": 0,
            "missing": "gold missing -> no record: --register REFUSES to write a registration whose"
            " pinned gold does not exist, because a pin over an absent file pins nothing"
            " ([[preregistration_is_a_file_not_a_constant]]). The dry run prices the leg anyway —"
            " the pricing is the pod's arithmetic and does not read a label.",
        },
        "draw": {
            "path": rel(DRAW),
            "sha256": sha256_of(DRAW),
            "arms": list(ARMS),
            "dev_threads": len(threads),
        },
        "corpus": {
            "threads": threads,
            "chars_total": sum(one["chars"] for one in threads),
            "chars_max": max(one["chars"] for one in threads),
            "distinct_renders": len({one["extractor_version"] for one in threads}),
        },
        "bound": {
            "is_a_bound_and_not_a_price": (
                "the seconds below are this instrument's OWN, over a WHOLE run of the slowest pod"
                " it has run on (ruling 05.09 (t) item 4). They are still a BOUND and not a price:"
                " no overhead is in them and no offer of the day — rung 0 at --register adds both"
                " and THAT is the number a cap is read against"
                if rate.get("sample") == WHOLE_RUN
                else "this instrument has no measured rate. The seconds below are BORROWED from"
                " another prompt, another pod and another transport; the smoke measures this leg's"
                " own and the registration is written against THAT"
            ),
            "priced_from": {
                "name": rate["name"],
                "sample": rate.get("sample"),
                "value": rate["value"],
                "unit": rate["unit"],
                "n": rate["n"],
                "max": rate["max"],
                "instrument": rate["instrument"],
                "measured_on": rate["measured_on"],
                "source": rate["source"],
            },
            "threads": len(threads),
            "seconds_at_the_mean": round(seconds, 1),
            "seconds_at_the_max": round(rate["max"] * len(threads), 1),
            "usd_per_second": usd_per_second,
            "usd_at_the_mean": round(seconds * usd_per_second, 4),
            "usd_at_the_max": round(rate["max"] * len(threads) * usd_per_second, 4),
            "boot_not_included": "a boot is the endpoint's, not the leg's — the registration adds"
            " it once at the corner it is measured at",
        },
    }


# --- the PAID half: the dev loop's own step, its rungs, its registration ---------------------------

ITERATION = 5
"""The dev-loop iteration the registration and the pack are emitted for — ruling 04.09 (m) item 5.
Iterations 1-3 are bought, priced and on disk; the transport repair of `f872a53` was a NEW
`extractor_version` by ruling 03.09 (c) item 3's own letter, so it was bought under the NEXT number
and never re-bought under iteration 2's. Iteration 4 was the codebook-v1.2 law over BOTH arms of the
first draw and came back INCOMPLETE (PHASE §6.5 — CUDA OOM on the smoke's longest render at 24 GB),
so ruling 05.09 (w) re-buys it as iteration 5 with the INSTRUMENT unmoved and the SERVING changed.
Iteration 5 is the LAST of the five runs §2 allows: a red bar closes S2's question with a number."""

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

DATACENTER = "EU-RO-1"
"""The volume decides the datacenter (`qw4nwleanc`, `mp-srv2`) and nothing else may move it."""

CARDS = ("RTX PRO 4500", "RTX A6000", "L40S")
MIN_VRAM_GB = 32
PRICE_CEILING_USD_PER_HOUR = 0.90
"""The serving, as ruling 05.09 (w) item 2 moved it and (x) item 3 made it a PARAMETER of this record.

Iteration 4 died of 24 GB: `CARD = "NVIDIA GeForce RTX 4090"` stood here as a constant and
`offered_price` matched it by hand, so «the card is ≥ 32 GB now» was a ruling no line of code could
obey ([[a_shifted_constant_has_physical_consumers]]). These three are (w)2's own order, tried in it,
and BOTH names come out of the same `runpodctl gpu list` row: `displayName` is what is matched here
and `gpuId` is what `pod create --gpu-id` and `--open --card` are given.

The match is EXACT for a reason — the listing carries `RTX PRO 4500` and `RTX PRO 4500 SE` at one
price, and only the first is offered in EU-RO-1 today. A prefix match would register the twin's row
and rung 1 would then KILL the pod the operator actually created."""

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
    "arms": ("holdout",),
    "draw": DRAW,
}
"""The holdout's OWN files — ruling 05.09 (q) item 5. Its own everything: the dev registration is
committed, frozen and already spent against, and a second population in one record voids the first
seal ([[a_second_population_in_a_shared_store_voids_the_first_seal]])."""

HOLDOUT2_FILES = {
    "gold": REPO_ROOT / "docs" / "labels-promo-holdout2.jsonl",
    "prep": REPO_ROOT / "results" / "promo_holdout2_prep.json",
    "prereg": REPO_ROOT / "results" / "prereg_promo_holdout2.json",
    "pack": REPO_ROOT / "results" / "promo_holdout2_pack.json",
    "run": REPO_ROOT / "results" / "promo_holdout2_run.json",
    "step": "promo-holdout2",
    "stem": "promo_holdout2",
    "arms": ("holdout",),
    "draw": DRAW2,
}
"""Holdout-2's OWN files — ruling 06.09 (z) item 4: «draw-2's holdout arm, gold
`docs/labels-promo-holdout2.jsonl`, step `promo-holdout2`, own stem/files». The arm is the SECOND draw's
`holdout` — the same word as the first draw's spent arm and a different population
([[id_spaces_that_look_comparable]]) — and the draw is a file of this map for that reason: the part
binds which draw `dev_threads` reads, so a leg can never be read out of a draw it was drawn to be
disjoint from. Its run record is its own too: the dev loop's is written at batch scale and carries
seven pods, and a line's `--close-segment` sums the segments of ITS anchor (`line_anchor`)."""

STEM = "promo_dev40"
"""What `--score` names its two files after. The iteration suffix is the dev loop's, not the part's:
the holdout is ONE shot and has no iteration to number."""


def guard_reading(step: str, step_cap: float) -> dict:
    """What the cycle AND this step's OWN line have left, in the guard's words. Never re-derived.

    `run_promo_c2.guard_says_go`'s rule, one line further: a missing REMAINING reads as unlimited,
    so a run that cannot find the guard's own line refuses instead of pricing itself against a
    number it invented ([[a_budget_is_not_an_elapsed]]).

    Ruling 05.09 (v) item 3 makes the STEP a parameter of the reading. Called without one, this
    function priced iteration 4 against the CYCLE's $3.4843 while `promo-dev-loop`'s own line stood
    at $1.8462 of the $1.20 the record named — the registration read FITS and the guard refused the
    run it had registered. A record that names a step but prices against the cycle is a false
    record, so the step's line is read here and a step line the guard did not print refuses exactly
    as a missing REMAINING does. A CLOSED line prints CLOSED and carries no new run."""
    done = subprocess.run(
        [sys.executable, str(GUARD), "--step", step, "--step-cap", f"{step_cap:.4f}"],
        check=False,
        capture_output=True,
        text=True,
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
    line = re.search(
        rf"^{re.escape(step.upper())} SPENT\s+\$([0-9.]+) of \$([0-9.]+)", done.stdout, re.M
    )
    if not line:
        raise SystemExit(
            f"the guard printed no '{step.upper()} SPENT $… of $…' line — THIS step's own headroom"
            " is unreadable, and pricing the cap against the cycle instead is the false record"
            " ruling 05.09 (v) closed. A settled line prints CLOSED and carries no new run: open"
            " the run its own line. Refuse."
        )
    step_spent, step_cap_read = float(line.group(1)), float(line.group(2))
    return {
        "remaining_usd": float(found.group(1)),
        "cycle3_spent_usd": float(cycle.group(1)),
        "cycle3_cap_usd": float(cycle.group(2)),
        "step_name": step,
        "step_spent_usd": step_spent,
        "step_cap_usd": step_cap_read,
        "step_remaining_usd": round(step_cap_read - step_spent, 4),
        "from": "scripts/runpod_guard.py --step <name> --step-cap <cap>, its own printed REMAINING,"
        " CYCLE 3 and step lines",
        "at": datetime.now(UTC).isoformat(timespec="seconds"),
    }


def offered_price(cards: tuple[str, ...] = CARDS) -> dict:
    """The FIRST card of `cards` this datacenter has in stock today, and its price — read ON THE DAY.

    The DEARER of the two clouds is registered: the create response's `costPerHr` is the price that
    is actually billed, and a registration written at the cheaper offer would be a ceiling the run
    can exceed without a single gate firing ([[a_ceiling_derived_from_one_span_measured_over_another]]).

    Ruling 05.09 (x) item 3 makes the card a parameter and gives the walk three conditions beyond the
    name, because (w)2 asked for a SERVING and not for a spelling: at least `MIN_VRAM_GB` — the 24 GB
    that OOM'd is what this leg is moving away from and a card is not «the next one» if it repeats
    it; offered in `DATACENTER` with stock, since the volume pins the cloud and «else A6000 / L40S»
    means «when the first is not there»; and a dearer offer at or under `PRICE_CEILING_USD_PER_HOUR`,
    which is the operator's own ≤ $0.90/h. A card that fails one of them is SKIPPED and the next name
    is tried; nothing is substituted silently and the refusal below names every candidate it saw.
    """
    done = subprocess.run(
        ["runpodctl", "gpu", "list"], check=False, capture_output=True, text=True
    )
    if done.returncode != 0:
        raise SystemExit(f"runpodctl gpu list failed: {done.stderr.strip()[:200]}")
    listing = json.loads(done.stdout)
    seen = []
    for want in cards:
        # EXACT, never a prefix: `RTX PRO 4500 SE` is another row at the same price and another cloud
        for gpu in [one for one in listing if one.get("displayName") == want]:
            here = [
                one
                for one in (gpu.get("dataCenterAvailability") or [])
                if one.get("dataCenterId") == DATACENTER
                and str(one.get("stockStatus") or "none").lower() != "none"
            ]
            prices = [
                float(one)
                for one in (gpu.get("securePricePerHr"), gpu.get("communityPricePerHr"))
                if one
            ]
            vram = gpu.get("memoryInGb") or 0
            why = (
                f"{vram} GB < {MIN_VRAM_GB}" if vram < MIN_VRAM_GB
                else f"no stock in {DATACENTER}" if not here
                else "no offer" if not prices
                else f"${max(prices)}/h > ${PRICE_CEILING_USD_PER_HOUR}/h"
                if max(prices) > PRICE_CEILING_USD_PER_HOUR
                else None
            )
            seen.append(f"{want} ({why})" if why else want)
            if why:
                continue
            return {
                "card": gpu["gpuId"],
                "display_name": want,
                "vram_gb": vram,
                "datacenter": DATACENTER,
                "stock": here[0].get("stockStatus"),
                "usd_per_hour": max(prices),
                "offers_usd_per_hour": prices,
                "considered": list(cards),
                "rule": f"the FIRST of {list(cards)} with ≥ {MIN_VRAM_GB} GB, stock in {DATACENTER}"
                f" and a dearer offer ≤ ${PRICE_CEILING_USD_PER_HOUR}/h; the price is the DEARER"
                " offer of secure/community, read on the day; the create response's own costPerHr is"
                " the price the meter bills and the price gate re-checks it",
                "read_at": datetime.now(UTC).isoformat(timespec="seconds"),
            }
    raise SystemExit(
        f"none of {list(cards)} is offered in {DATACENTER} today at ≥ {MIN_VRAM_GB} GB and"
        f" ≤ ${PRICE_CEILING_USD_PER_HOUR}/h — saw {seen or 'no matching row at all'}. The volume"
        " pins the datacenter, so this is a STOP for the operator's word, not a card to substitute"
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


def backstop(borrowed_minutes: int, hard_stop_seconds: float) -> dict:
    """`--terminate-after`, in whole minutes, from the CAP — ruling 05.09 (w) item 4, (x) item 3.

    v5b's 90 minutes is a BORROWED constant and it was the live bound by accident. Iteration 5's cap
    is $1.40 and the card is ≈ $0.72/h, so the cap pays for 116 minutes and the borrowed 90 would
    have killed the pod at $1.08 — a run this record prices as FITS, ended by a number from another
    step's transport ([[a_ceiling_derived_from_one_span_measured_over_another]]). The mean corner is
    ≈ 71 minutes at that price, so 90 leaves a slower card no room at all.

    So the CAP is the bound, always: `hard_stop_seconds` is the cap divided by the registered price,
    and the floor to whole minutes keeps `terminate_after_minutes * 60 <= hard_stop_seconds` — the
    inequality `open_segment` checks as `backstop_fits`. Taking the borrowed number whenever it were
    the larger of the two would let the meter run past the cap, which is the one thing
    «the cap is the hard stop» forbids ([[a_bound_the_meter_cannot_reach]]). Both numbers are in the
    record and it says which one is live, so nothing is dropped silently.
    """
    minutes = int(hard_stop_seconds // 60)
    return {
        "terminate_after_minutes": minutes,
        "terminate_after_borrowed_minutes": borrowed_minutes,
        "terminate_after_live_bound": "the cap",
        "terminate_after_rule": f"the CAP's own minutes at the registered price —"
        f" floor({hard_stop_seconds:.1f} s / 60) = {minutes} min, against the"
        f" {borrowed_minutes} min this leg used to borrow from"
        f" {rel(BORROWED_GATES)} :: go_no_go.backstop, which would have bitten"
        + (" FIRST" if borrowed_minutes < minutes else " LAST")
        + ". Ruling 05.09 (x) item 3: the cap is the hard stop and nothing else bounds the money.",
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
    owned = rate.get("sample") == WHOLE_RUN
    word = "measured" if owned else "borrowed"
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
            f"dear — the {word} MAX on every thread ({rate['max']} s, one unit of"
            f" «{rate.get('max_from', rate['name'])}») and two overheads. Pessimistic by"
            " construction: the guard's spend is a maximum and a cap blown after the money is"
            " spent cannot be un-spent",
            s_thread=rate["max"],
            **(common | {"overhead": overhead["seconds"] * 2}),
        ),
    ]
    cheap, dear = table[0], table[-1]
    read, issued = dear, "dear"
    ruling = "docs/PROCESS.md «Money» rung (0) — the registered corner is the DEAR one"
    if not dear["fits"]:
        read, issued = cheap, "mean"
        ruling = (
            f"PHASE v10 §6.1, ruling 05.09 (t) item 3 — on EVERY leg, dev as holdout: the dear"
            f" corner ${dear['usd']:.4f} is OVER the ${cap:.4f} cap, so the leg is issued FITS on"
            f" the MEAN corner ${cheap['usd']:.4f} with the cap as the HARD STOP:"
            " `--terminate-after` is derived from it and the meter cannot pass it. The mean is the"
            " WHOLE-RUN mean of the slowest pod seen, never a smoke of three (item 4). The dear"
            " corner stays in this table and in `dear_usd`, priced and named, so nothing over the"
            " cap is hidden ([[a_bound_the_meter_cannot_reach]]). Ruling 05.09 (r) item 2 makes"
            " this pair — FITS here plus the hard stop — the leg's ONLY money gate: the band gate"
            " is not run. The `part != \"dev\"` condition this branch used to carry is what left"
            " iteration 4 unregisterable under a cap the operator had already named"
        )
    return {
        "rule": "docs/PROCESS.md «Money» rung (0): price at create ≤ the registered ceiling — the"
        " ceiling is the step cap, the price is the DEAR corner",
        "amendment": by_part(
            part,
            dev="ruling 03.09 (c) item 1 — smoke + iteration 1 + the 16 posts, not five"
            " iterations: the borrowed max over five would refuse a loop the smoke may prove cheap",
            holdout="ruling 05.09 (q) item 5 and (r) item 5 — smoke + the ONE shot over the"
            " holdout's 40 threads, no posts and no second reading: §8 (e) spends the holdout once,"
            " so there is no later iteration this corner is priced short for",
            holdout2="ruling 06.09 (z) item 4 and 05.09 (r) item 5 — smoke + the ONE shot over"
            " holdout-2's 40 threads, no posts and no second reading: §8 (e) spends the holdout"
            " once, so there is no later iteration this corner is priced short for. Priced on the"
            " whole-run mean of the slowest pod seen (`measured_rate` beside this names it), the"
            " cap as the hard stop",
        ),
        "threads": n_threads,
        "threads_note": f"{SMOKE_N} smoke + {len(threads)} {part}-40. The smoke's three ARE the pass's"
        " first three units, so the pod answers 40 and the registration is bought high, spent low",
        "posts": n_posts,
        "cap_usd": round(cap, 4),
        "price": price,
        **{
            ("measured_rate" if owned else "borrowed_rate"): {
                k: rate[k]
                for k in (
                    "name", "sample", "value", "max", "n", "instrument", "source",
                    "value_from", "max_from", "pool",
                )
                if k in rate
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


def by_part(part: str, **texts: str) -> str:
    """ONE leg's decision-bearing prose by NAME, or a refusal — PHASE §4 v8 (ruling 05.09 (r) 2).

    Every field of the record that states a decision — phase, authority, question, baseline, the
    leg-B verdict, out-of-scope, rung 0's amendment, the decision table — is listed here per leg.
    The `if PART == "dev" else …` this replaces handed ANY third leg the holdout-40's words, which
    is how a `--part holdout2` record would have carried ruling (r) 5's `--cap 1.10` as its own
    authority: a population parameterised under another leg's decision table is a false record,
    so a leg this table has no text for REFUSES instead of inheriting a neighbour's.
    """
    if part not in texts:
        raise SystemExit(
            f"--part {part}: no decision text for this leg (the table names {sorted(texts)}) — the"
            " emitter refuses to write a record parameterised under another leg's decisions"
            " (PHASE §4 v8, ruling 05.09 (r) item 2)"
        )
    return texts[part]


def register(cap_usd: float | None = None) -> dict:
    """Rung 0 before anything exists — plan §9, ruling 03.09 (c) amendments 1 and 5.

    `--cap` is the holdout's, and it is an OPERATOR's number (ruling 05.09 (q) item 3), never this
    script's: the $0.30 the plan fenced was an estimate over a rate that has since been retired, and
    PHASE v7 §6.1 makes a fence for a later step an estimate re-priced at that step's registration
    ([[a_cap_set_from_one_legs_price]]). The dev loop's own rule is untouched and still the default.
    """
    if cap_usd is None and PART != "dev":
        raise SystemExit(
            f"--part {PART} needs --cap: a holdout leg's cap is the OPERATOR's number (PHASE §6.1,"
            " rulings 05.09 (q) 3 and (r) 3) and plan §9's min($2.50, REMAINING − $0.30) is the DEV"
            " loop's rule — a record priced on another leg's cap rule is a false record (PHASE §4"
            " v8). Nothing is written and no line is opened."
        )
    if not GOLD.exists():
        raise SystemExit(
            f"{rel(GOLD)} is missing — gold missing -> no record. The registration PINS the gold by"
            " sha256 and a pin over an absent file pins nothing, so nothing is written: the record"
            " would claim a frozen answer key that does not exist"
            " ([[preregistration_is_a_file_not_a_constant]]). Commit the gold, then --register."
        )
    money = guard_reading(STEP, cap_usd if cap_usd is not None else STEP_CAP_USD)
    if cap_usd is None:
        cap = round(
            min(
                STEP_CAP_USD,
                money["step_remaining_usd"],
                money["remaining_usd"] - HOLDOUT_RESERVE_USD,
            ),
            4,
        )
        cap_rule = (
            f"min(${STEP_CAP_USD:.2f}, THIS step's own REMAINING,"
            f" the cycle's REMAINING − ${HOLDOUT_RESERVE_USD:.2f})"
        )
        if cap < STEP_FLOOR_USD:
            raise SystemExit(
                f"the dev loop's cap is ${cap:.4f} — below the ${STEP_FLOOR_USD:.2f} floor plan §9"
                " names. Ruling 02.09 (b) §4 makes that the operator's word, not this script's:"
                " STOP."
            )
    else:
        cap = round(min(cap_usd, money["step_remaining_usd"], money["remaining_usd"]), 4)
        cap_rule = (
            f"min(${cap_usd:.4f} — the operator's own number, quoted in"
            " docs/PHASE-promo-pulse-1.md §6.1 for this leg — , THIS step's own REMAINING, the"
            " cycle's REMAINING) — ruling 05.09 (v) item 3"
        )
        if cap < cap_usd:
            raise SystemExit(
                f"the cap asked for is ${cap_usd:.4f}; {STEP} has"
                f" ${money['step_remaining_usd']:.4f} left of its OWN line and the cycle has"
                f" ${money['remaining_usd']:.4f} — a cap above either is a cap nothing enforces."
                " Ruling 05.09 (v) item 2: a paid run is bought under its own step line. The"
                " operator opens one or lowers the cap: STOP."
            )
    threads = dev_threads()
    prep = json.loads(PREP.read_text(encoding="utf-8"))["corpus"]["threads"]
    smoke = smoke_units([dict(one) for one in prep])
    left_over = leg_b_posts() if PART == "dev" else {"task": None, "by_channel": {}, "posts": 0}
    price = offered_price()
    verdict = rung_0(cap=cap, price=price, threads=threads, n_posts=0)
    gates = borrowed_gates()
    gates |= backstop(int(gates["terminate_after_minutes"]), verdict["hard_stop_seconds"])
    return {
        "part": PART,
        "phase": by_part(
            PART,
            dev=f"promo-pulse-1 S9 — the dev loop's PAID instrument, iteration {ITERATION}",
            holdout="promo-pulse-1 S9 — the FROZEN holdout-40, the ONE shot (ruling 05.09 (q))",
            holdout2="promo-pulse-1 S9 — holdout-2, the ONE shot on the instrument FROZEN as"
            " iteration 5 bought it (rulings 06.09 (z) item 3, 05.09 (s) item 3 (b))",
        ),
        "class": "PRE-REGISTRATION. Written and committed before any pod of this step exists; git"
        " history is the only witness that it preceded the money.",
        "re_emission": by_part(
            PART,
            dev="ruling 04.09 (m) item 5 and (n) item 2 — iterations 1-3 are kept by git"
        f" history; THIS record is the one iteration {ITERATION} is bought under. What moves since"
        " iteration 3 is the LAW (codebook v1.2, ruling 05.09 (s) item 2: partners, the off-domain"
        " thread, three product forms, price-as-quality) and the POPULATION (dev-2, the spent"
        " holdout-40 relabelled by (s) item 3, riding beside dev-40 as a reading)."
        " Iteration 4 was bought under exactly that law and came back INCOMPLETE (PHASE v12 §6.5 —"
        " CUDA OOM in `gemma4._norm` on the smoke's LONGEST render, 338 MiB refused at 23.19 of"
        " 23.52 GiB), so ruling 05.09 (w) item 2 re-buys it as iteration 5 with the INSTRUMENT"
        " unmoved and the SERVING changed, and item 3 of (x) makes that serving a field of this"
        f" record rather than a constant: `rung_0.price` names the card this run is registered on"
        f" ({price['display_name']}, {price['vram_gb']} GB, gpu-id «{price['card']}»,"
        f" ${price['usd_per_hour']}/h in {DATACENTER}) — chosen by"
        f" `offered_price` from {list(CARDS)} in ruling 05.09 (w) item 2's own order, at"
        f" ≥ {MIN_VRAM_GB} GB and ≤ ${PRICE_CEILING_USD_PER_HOUR}/h. The 24 GB the OOM happened on"
        " cannot be registered again by construction. The pod is launched with"
        " `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` ((w) item 2, the allocator half): it is"
        " an ENVIRONMENT of the launch line and touches no pinned byte, and it is disclosed here"
        " because a serving nobody wrote down is a serving the next reading cannot be compared"
        " against ([[provenance_cannot_name_itself]]). `gates.terminate_after_minutes` is the CAP's"
        " own minutes at that price and no longer the 90 borrowed from v5b ((x) item 3)."
        " `src/market_pulse/promo_prompts.py` stays pinned beside the law and"
        " `scripts/promo_dev_pod_runner.py` MOVES by ruling 05.09 (w) item 3: the runner catches a"
        " unit's exception, writes it down as that unit's ERROR reply and exits non-zero, so the Mac"
        " reads a death instead of waiting out the GO deadline. That is the SERVING and not the"
        " instrument (PHASE v12 §6.5) — the render, the prefix rule, the law handshake and the GO"
        " are byte-for-byte iteration 3's, and `pinned_inputs` above carries the runner's new sha,"
        " re-read from disk at this call. `check_law` compares only `codebook_version` and covers"
        " neither the template nor the runner. Ruling 05.09 (u) item 2 adds the reading arm's own"
        " answer key, docs/labels-promo-dev2.jsonl, to `pinned_inputs`: dev-2 carries no bar of this"
        " record, and a reading still needs its reference pinned as much as a bar does."
        " `committed_registration()` still does not re-verify `pinned_inputs`: a named debt.",
            holdout="there is no re-emission of THIS record: §8 (e) spends the holdout ONCE and"
            " ruling 05.09 (q) item 2 freezes the instrument as iteration 3 bought it, so nothing"
            " about it can move to justify a second number. The ONE case that writes another record"
            " is PHASE §6.5 — a reading that comes back incomplete is recorded under its number,"
            " never compared to the bars, and re-bought under the NEXT number with the law UNMOVED"
            " and after the operator's money word. `committed_registration()` still does not"
            " re-verify `pinned_inputs`: a named debt it inherits from the dev loop.",
            holdout2="there is no re-emission of THIS record: §8 (e) spends the holdout ONCE and"
            " ruling 06.09 (z) item 3 freezes the instrument as iteration 5 bought it — the four"
            " pins of `d598573` (`results/prereg_promo_dev_loop.json` at that commit: the codebook,"
            " `src/market_pulse/promo_prompts.py`, `scripts/promo_dev_pod_runner.py` and the"
            " template it renders), re-read from disk into `pinned_inputs` at this call and equal"
            " to that record's byte for byte, or the shot is a STOP («A pin that moves before the"
            " shot is a stop»). The serving is iteration 5's and is disclosed as fields, not"
            f" constants: `rung_0.price` names the card ({price['display_name']},"
            f" {price['vram_gb']} GB, gpu-id «{price['card']}», ${price['usd_per_hour']}/h in"
            f" {DATACENTER}) chosen by `offered_price` from {list(CARDS)} in ruling 05.09 (w)"
            f" item 2's order at ≥ {MIN_VRAM_GB} GB and ≤ ${PRICE_CEILING_USD_PER_HOUR}/h, and the"
            " launch line carries `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` — the"
            " allocator half of (w) item 2, an ENVIRONMENT that touches no pinned byte."
            " `gates.terminate_after_minutes` is the CAP's own minutes at that price ((x) item 3)."
            " The ONE case that writes another record is PHASE §6.5 — a reading that comes back"
            " incomplete is recorded under its number, never compared to the bars, and re-bought"
            " under the NEXT number with the law UNMOVED and after the operator's money word."
            " `committed_registration()` still does not re-verify `pinned_inputs`: a named debt it"
            " inherits from the dev loop.",
        ),
        "authority": by_part(
            PART,
            dev="docs/reviews/2026-08-30-plan-promo-pulse-1.md «Ruling 05.09 (v)» items 2-3 —"
        " «a paid run is its own money line: iteration 4 is bought under `promo-iter4`"
        " (results/spend_promo_iter4.json, its own anchor, cap $1.20, closed in the SAME session);"
        " the registration names its line and reads the guard WITH `--step <name> --step-cap <cap>`,"
        " so FITS is judged against THAT line's own remaining and the record's `money` carries it"
        " beside the cycle's; the old `promo-dev-loop` line stays as (r)4 left it and carries no new"
        " run». It re-emits the record «Ruling 05.09 (u)» item 2 wrote —"
        " «the registration is re-emitted with docs/labels-promo-dev2.jsonl among `pinned_inputs`"
        " and `gold.covers` naming both arms; `--score` takes the arm as parameters and writes"
        " per-arm files; `--pack` again on the re-emitted record; commit — then the pod». It stands"
        " on «Ruling 05.09 (t)» item 6, which this record was first written under —"
        " «`rate_for`/`rung_0`/`--close-segment` as 3–4 → whole-run rows → `ITERATION = 4`,"
        " `--dry-run --part dev --cap 1.20` FITS on the mean → `--register` → commit → `--pack`"
        " (green) → the paid iteration 4» — and (t) item 5 is the operator's cap and the arm order;"
        " docs/PHASE-promo-pulse-1.md §6.1 v11; docs/plans/promo-pulse-1.md §9 and §9a",
            holdout="docs/reviews/2026-08-30-plan-promo-pulse-1.md «Ruling 05.09 (r)» item 5 —"
            " «`register()`'s part branch (item 2) → `--register --part holdout --step"
            " promo-holdout --cap 1.10 --gold docs/labels-promo-holdout.jsonl` → commit → §1–§4 →"
            " smoke → GO → §6–§7: K8 (`--part holdout`) → the error table naming the holdout"
            " misses. A complete reading closes S2's question green or red; an incomplete one is"
            " recorded and re-bought under the next number only after the operator's money word."
            " END at the reading.»; the cap is item 3's operator word of 05.09;"
            " docs/PHASE-promo-pulse-1.md §6.1–6.2 v8",
            holdout2="docs/reviews/2026-08-30-plan-promo-pulse-1.md «Ruling 06.09 (z)» items 3-4 —"
            " «The instrument is FROZEN as bought (§6.2)» … «the four pins the holdout-2"
            " registration carries byte for byte» … «A pin that moves before the shot is a stop»;"
            " «the holdout-2 leg as a PART of the emitter (`--part holdout2`: draw-2's holdout arm,"
            " gold `docs/labels-promo-holdout2.jsonl`, step `promo-holdout2`, own stem/files; every"
            " decision field of the record branches on the leg — §4)»; the population is «Ruling"
            " 05.09 (s)» item 3 (b)'s second draw, results/promo_threads_draw_2.json — seed 42 over"
            " the PRODUCT's population, disjoint from the 80 the first draw spent; the cap is the"
            " operator's fence of docs/PHASE-promo-pulse-1.md §6.1 v16 («holdout-2 ≤ $0.90 on the"
            " measured pace»), an ESTIMATE re-priced at THIS registration on the whole-run mean of"
            " the slowest pod seen, with the cap as the hard stop (rulings (r) 2, (t) 3); §6.2's"
            " STOP notice to the operator precedes the paid session; the shot is bought once",
        ),
        "question": by_part(
            PART,
            dev="does the promo-signal instrument, under CODEBOOK"
            f" {promo_prompts.codebook_version()[:16]}…, clear subject ≥ 0.80 and signal ≥ 0.75 on"
            " dev-40 within at most 5 dev runs — and what does the SAME law read on dev-2, the"
            " spent holdout-40 whose 0.7181 subject sent the codebook back for v1.2? dev-40 carries"
            " the bars; dev-2 is a reading beside them and no bar of this record.",
            holdout="does the instrument that took the dev bar — the SAME four pins, byte for byte"
            " (ruling 05.09 (q) item 2) — clear subject ≥ 0.80 and signal ≥ 0.75 on the frozen"
            " holdout-40, in ONE shot?",
            holdout2="does the instrument that took the dev bar on iteration 5 — the SAME four pins"
            " of `d598573`, byte for byte (ruling 06.09 (z) item 3) — clear subject ≥ 0.80 and"
            " signal ≥ 0.75 on holdout-2, the second draw's 40 threads of the product's own"
            " population, in ONE shot?",
        ),
        "step": {
            "name": STEP,
            "ledger": rel(REPO_ROOT / "results" / f"spend_{STEP.replace('-', '_')}.json"),
            "cap_usd": cap,
            "cap_rule": cap_rule,
            "floor_usd": STEP_FLOOR_USD if (PART == "dev" and cap_usd is None) else None,
            "floor_rule": f"plan §9's ${STEP_FLOOR_USD:.2f} floor guards the DERIVED cap"
            " min($2.50, REMAINING − $0.30) and nothing else"
            if (PART == "dev" and cap_usd is None)
            else "none — the cap above is the operator's own number, and a floor standing OVER it"
            " would be a field of this record refusing the very run the record registers"
            " ([[a_threshold_that_lives_in_prose]]); the cap is the hard stop",
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
            "baseline": by_part(
                PART,
                dev="iterations 1-3 are bought and priced on disk; iteration 3 took BOTH dev bars"
                " on a complete reading (subject 0.8714, signal 0.9104,"
                " `results/grade_promo_dev40_iter3.json`) and ruling 05.09 (q) item 1 accepted it."
                " Then the holdout came back subject 0.7181 RED under that same law"
                " (`results/grade_promo_holdout40.json`), and ruling 05.09 (s) turned the shot into"
                " dev-2 and sent the codebook back. So iteration 4 moves TWO things and names both:"
                " the LAW (codebook v1.2 — partners to `chain`, rule 11 for an off-domain thread,"
                " three product forms in rule 4, price-as-quality; `--leak-check` CLEAN over all"
                " three sets) and the POPULATION (dev-40 + dev-2, 80 threads). The transport, the"
                " decoding and the token ceiling are untouched — this is not a transport iteration.",
                holdout="iteration 3 took BOTH dev bars on a complete reading (subject 0.8714,"
                " signal 0.9104; `results/grade_promo_dev40_iter3.json`) and ruling 05.09 (q)"
                " item 1 accepted it. NOTHING moves for this shot: item 2 freezes the instrument as"
                " that iteration bought it, so `codebook_version`, `template_sha256`,"
                " `scripts/promo_dev_pod_runner.py` and `src/market_pulse/promo_prompts.py` are the"
                " dev-bar registration's own, byte for byte, and the near-quote and codebook-doc"
                " sync queue BEHIND this run. What changes is the POPULATION and nothing else — the"
                " frozen holdout arm of the same seed-42 draw, disjoint from dev-40 and never"
                " scored.",
                holdout2="iteration 5 took BOTH dev bars on a complete reading — 80 of 80 units,"
                " 0 unparsed; subject 0.8857, signal 0.8667 (`results/grade_promo_dev40_iter5.json`)"
                " — and ruling 06.09 (z) item 1 accepted it, with dev-2 read beside it (0.8883 /"
                " 0.8296, a reading and no bar). NOTHING moves for this shot: (z) item 3 freezes the"
                " instrument as that iteration bought it, so `codebook_version`, `template_sha256`,"
                " `scripts/promo_dev_pod_runner.py` and `src/market_pulse/promo_prompts.py` are"
                " `d598573`'s own, byte for byte. What changes is the POPULATION and nothing else —"
                " the holdout arm of the SECOND draw (ruling 05.09 (s) item 3 (b): seed 42 over the"
                " product's population, the paused channels and the 80 already drawn taken out),"
                " never scored and never read by the law (`--leak-check` CLEAN over all three"
                " sets).",
            ),
            "vocabulary": promo_prompts.vocabulary(),
        },
        "pinned_inputs": {
            rel(path): sha256_of(path)
            for path in (CODEBOOK, *leg_golds(), DRAW, PREP, PREREG_5C2, RUNNER, PROMO_PROMPTS)
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
                    "rule": f"shortest, median and longest render by {rel(PREP)}'s own"
                    " chars — a rule, not a pick",
                    "units": [
                        {
                            "unit_id": f"{one['channel']}:{one['thread_root']}",
                            "chars": one["chars"],
                            "role": one["smoke_role"],
                        }
                        for one in smoke
                    ],
                    "prefix": by_part(
                        PART,
                        dev="these three are the pass's FIRST three units; the pod answers them,"
                        " the Mac reads the rate, and the decision table of ruling 03.09 (b)"
                        f" decides whether the remaining {len(threads) - SMOKE_N} are bought at all",
                    )
                    if verdict["issued_on"] == "dear"
                    else "these three are the pass's FIRST three units; the pod answers them and"
                    " their arrival IS the GO (ruling 05.09 (r) item 2, widened to every leg by"
                    " (t) item 3). Their seconds are read off the pod log for the record, not for a"
                    f" gate: no band decides whether the remaining {len(threads) - SMOKE_N} are"
                    " bought — this leg is issued on the MEAN corner and the cap as"
                    " `--terminate-after` is what bounds them",
                },
            },
            "leg_b": {
                "posts": 0,
                "by_channel": {},
                "closed": by_part(
                    PART,
                    dev="ruling 04.09 (m) item 4 — 16 of 16 posts answered `[]` under BOTH"
                    " iteration 1 and iteration 2: two identical readings. Iteration 3 buys leg A"
                    " only. `build_pack` iterates `by_channel`, so the empty map is what actually"
                    " keeps them off the pod; `not_bought` keeps them NAMED, not deleted.",
                    holdout="ruling 05.09 (q) item 5 — leg B does not exist on this leg at all:"
                    " the holdout is the frozen draw's THREADS and the 16 posts were the dev"
                    " loop's, closed there by two identical `[]` readings. The empty map is what"
                    " keeps them off the pod; nothing of leg B is bought or re-bought under the"
                    " holdout's cap.",
                    holdout2="ruling 06.09 (z) item 4 — leg B does not exist on this leg: holdout-2"
                    " is the SECOND draw's THREADS and the 16 posts were the dev loop's, closed"
                    " there by two identical `[]` readings. The empty map is what keeps them off"
                    " the pod; nothing of leg B is bought under this shot's cap.",
                ),
                "not_bought": left_over,
            },
        },
        "rung_0": verdict,
        "gates": gates
        | {
            "1_liveness": "the ssh dead-man above; never two pods, checked BEFORE `pod create`",
            "3_hard_stop": f"{verdict['hard_stop_seconds']:.1f} s of pod existence at the"
            " registered price — the platform-side backstop is terminate_after"
            if verdict["issued_on"] == "dear"
            else f"{verdict['hard_stop_seconds']:.1f} s of pod existence at the registered price."
            " On a leg issued on the MEAN corner it is not a backstop BEHIND a band gate: ruling"
            " 05.09 (r) item 2, widened by (t) item 3, does not run §5's band gate at all, so the"
            " cap as `--terminate-after` is the ONE thing that bounds the money after rung 0 has"
            " issued FITS",
        },
        "decision_table": by_part(
            PART,
            dev={
                "authority": "ruling 03.09 (b), quoted and not moved — this leg is issued on the"
                " DEAR corner, and PHASE v10 §6.1 gives the dear corner the bands",
                "after_the_smoke_for_40_threads": {
                    "<= 0.80": "run iteration 1 now",
                    "0.80 - 1.20": "run it, then STOP with the error table",
                    "> 1.20": "STOP before buying; pod torn down, listing shown",
                },
            },
        )
        if verdict["issued_on"] == "dear"
        else {
            "authority": "ruling 05.09 (r) item 2 as PHASE v10 §6.1 widens it to EVERY leg (ruling"
            " 05.09 (t) item 3): the money gate is rung 0 FITS on the measured MEAN corner"
            f" (${verdict['table'][0]['usd']:.4f} ≤ ${verdict['cap_usd']:.4f}) plus the cap as the"
            " platform's hard stop (`--terminate-after`); §5's band gate is NOT run — GO is written"
            " the moment the smoke's three replies are in (their seconds stay in the pod log);"
            " `project()` and its literals stay untouched",
            "why_not_the_dev_bands": "the dev loop's bands are absolute dollars ($0.80 / $1.20) with"
            " KILL on the MAX corner over the cap. This leg's max corner is over the cap BY"
            " CONSTRUCTION — rung 0 above prices it at"
            f" ${verdict['dear_usd']:.4f} and issues FITS on the mean anyway — so the band gate"
            " would KILL a run this very record registers as FITS. Two thresholds for one decision"
            " ([[two_gates_on_one_spend_read_different_corners]]); the corner that was priced keeps"
            " the decision.",
            "after_the_smoke_for_40_threads": {
                "3 replies are in": "write GO. The pod answers the rest under the hard stop.",
                "the smoke did not come back": "no GO is written; the pod is deleted, the segment"
                " closed, the listing shown, and the run is PHASE §6.5's incomplete reading.",
                "the key name": "kept as it stands because `project()` reads it by name; the leg's"
                f" own size is `population.leg_a.threads` = {len(threads)}",
            },
        },
        "teardown": "`runpodctl pod delete <id>`, then `runpodctl pod list -a` → [] and"
        " `runpodctl serverless list` → [] in the transcript, before every STOP and before the"
        " session ends (ruling 03.09 (c) item 2)",
        "out_of_scope": by_part(
            PART,
            dev="no training; no holdout spend; no new sources; no cap raise. Leg B's answers land"
            " on disk as evidence for the store, and the ingest into data/derived_w2 is NOT in this"
            " session's sequence.",
            holdout="no training; no new sources; no cap raise; no second shot — §8 (e) spends the"
            " holdout ONCE. Leg B does not exist here: ruling 05.09 (q) item 5 buys leg A only. A"
            " run that comes back incomplete is recorded under §6.5 and re-bought under the next"
            " number with the law UNMOVED; it is not a second reading of the same shot.",
            holdout2="no training; no new sources; no cap raise; no second shot — §8 (e) spends the"
            " holdout ONCE. Leg B does not exist here (ruling 06.09 (z) item 4). A run that comes"
            " back incomplete is recorded under §6.5 and re-bought under the next number with the"
            " law UNMOVED, after the operator's money word; it is not a second reading of the same"
            " shot. c3 comes after this shot and the volume `mp-srv2` after c3 ((z) item 5).",
        ),
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

    From iteration 4 the leg is TWO arms in ONE out-file, and `ARM` grades ONE of them: its own
    units of the pack, its own gold, its own part of the draw. Scoring both at once would read 80
    answered units against a key covering 40 and call the result the leg's
    ([[measure_on_the_rows_the_gate_scores]]).
    """
    import grade_promo_signals as k8

    arm = DEV_ARMS[ARM] if ARM else None
    own = {unit_id(one) for one in dev_threads(arms=(arm["draw_part"],))} if arm else None
    units = {
        item["id"]: item
        for item in load(PACK)["items"]
        if item["leg"] == "a" and (own is None or item["id"] in own)
    }
    rows: list[dict] = []
    failures: list[dict] = []
    answered: list[str] = []
    fenced = 0
    dead = [one for one in dead_units(replies) if one in units]
    for reply in reply_rows(replies):
        item = units.get(reply.get("id"))
        if item is None:
            continue  # leg B rides the same out-file and is not leg A's gold
        if died(reply):
            # ruling 05.09 (x) item 4 — a unit that DIED is UNANSWERED, not an answer that failed to
            # parse: it has no `reply` to parse and counting it among the parse failures would blame
            # the instrument for the serving ([[empty_class_eats_the_parse_failures]]). It is named
            # in `dead_units` above and it stays out of `leg_a_units_answered`.
            continue
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
    # the draw ARM, never the part's name: `holdout2` is a leg whose arm in DRAW2 is «holdout»
    strata = k8.strata_of(DRAW, arm["draw_part"] if arm else ARMS[0])
    graded = k8.grade(gold, rows, strata)
    said_rows = {(k8.thread_key(one), str(one["msg_id"])): one for one in rows if one.get("msg_id")}
    misses = []
    for one in gold:
        if not one.get("msg_id"):
            continue
        found = said_rows.get((k8.thread_key(one), str(one["msg_id"])))
        # the grade's OWN predicate, never a second copy of it: a miss table built on a different
        # comparison would name rows the bar above counted as hits
        # ([[two_gates_on_one_spend_read_different_corners]])
        if found is not None and k8.subjects_agree(one, found):
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
        "contract": f"docs/plans/promo-pulse-1.md §9 — the error table of iteration {iteration}"
        + (f", arm {ARM}" if ARM else ""),
        "iteration": iteration,
        # which arm and which key, IN the record: two arms write two files of the same shape, and a
        # file that cannot name its own reference is a file a reader has to guess about
        # ([[provenance_cannot_name_itself]])
        "arm": ARM,
        "gold": {"path": rel(GOLD), "sha256": sha256_of(GOLD)},
        "replies": rel(replies),
        "rows": rows,
        "answers": {
            "leg_a_units_answered": len(answered),
            "leg_a_units_registered": len(units),
            "leg_a_units_dead": dead,
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
            "k8_version": graded["k8_version"],
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


"""`MEASURED_RATE` stood here and is orphaned by ruling 05.09 (t) item 4: a rate is no longer
chosen by NAME. `own_rate()` selects on `contract` + `sample`, so both legs' rows are one
instrument's history and the per-part names stay provenance instead of a filter."""


SMOKE_IN = "3 replies are in"
SMOKE_GONE = "the smoke did not come back"
"""The two outcomes of the registration's `after_the_smoke_for_40_threads`, by their own key names.
`smoke_state` indexes the record with these, so a renamed branch is a KeyError and not a silent
third meaning ([[gate_verdicts_need_an_artifact]])."""


def smoke_state(replies: Path) -> dict:
    """Which branch of the registration's OWN decision table this out-file is in — $0, on a live pod.

    Ruling 05.09 (w) item 3, the Mac half. The pod's runner now writes an ERROR reply for the unit it
    died on, and this is the reading that makes it decisive: an error reply among the replies IS «the
    smoke did not come back», so the pod is deleted AT ONCE instead of at the GO deadline.

    Three states, and the third is why this is a reading and not a verdict. A file with fewer than
    the smoke's rows is WAITING — the pod may still be generating, and no file can tell that from a
    death by itself. What tells them apart is the PROCESS, which the runbook already watches
    (`pgrep -fa promo_dev_pod_runner`) — so WAITING with no runner alive is the same outcome, read by
    the operator's own eyes ([[long_run_watch_the_process]]). An error reply needs neither.

    Ruling 05.09 (x) item 4 gives the rows one more reading: the file is copied off a LIVE pod, so
    its last line can be half written, and `reply_rows` forgives exactly that one. A torn last line
    leaves its unit unanswered, which is WAITING — never a traceback on the command that decides
    whether the pod is deleted.

    The units and the branch prose are READ from the committed registration, never typed here: a
    literal would pin ONE record's smoke, which a ruling moves ([[a_number_typed_into_its_own_checker]]).
    The presence rule is the one the runbook's heredoc already enforced; the `finish_reason` of each
    unit is REPORTED and not judged, exactly as that heredoc left it for the operator.
    """
    record = committed_registration()
    bands = record["decision_table"]["after_the_smoke_for_40_threads"]
    want = [one["unit_id"] for one in record["population"]["leg_a"]["smoke"]["units"]]
    read = reply_rows(replies)
    rows = {row["id"]: row for row in read if row.get("id") is not None}
    # off `read` and not off `rows`: a crash AFTER the loop names no unit at all and writes
    # `id: null` (the runner's own «a row that claimed one would be a false record»). It is still a
    # death, and keying it away would lose the only row that says so
    dead = [row for row in read if died(row)]
    missing = [one for one in want if one not in rows]
    state = SMOKE_GONE if dead else (SMOKE_IN if not missing else "waiting")
    return {
        "state": state,
        "action": bands.get(
            state, "the pod is still generating — poll again, and watch the PROCESS, not this file"
        ),
        "units": [
            {"unit_id": one, "reply": rows.get(one)}
            for one in want
        ],
        "errors": [
            {"id": row.get("id"), "exception": row.get("exception"), "error": row.get("error")}
            for row in dead
        ],
        "missing": missing,
        "replies": rel(replies),
    }


def render_smoke(state: dict) -> str:
    """The three units as the runbook's heredoc printed them, plus the branch the record names."""
    lines = []
    for one in state["units"]:
        row = one["reply"]
        lines.append(
            f"  {one['unit_id']:38s} "
            + (
                "MISSING"
                if row is None
                else f"ERROR {row.get('exception')}"
                if died(row)
                else f"{row['seconds']:6.1f}s balanced={row['balanced']} finish={row['finish_reason']}"
            )
        )
    for one in state["errors"]:
        lines.append(f"  ERROR {one['exception']} on {one['id']}: {one['error']}")
    return "\n".join([f"\n{state['state'].upper()} — {state['action']}", *lines])


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
    # a DEAD unit is not a sample: `answered_rows` leaves it out, so it reads as MISSING and this
    # refusal fires instead of a KeyError on the `seconds` an error reply has never had
    rows = answered_rows(replies)
    missing = [one["unit_id"] for one in smoke if one["unit_id"] not in rows]
    if missing:
        raise SystemExit(
            f"{rel(replies)} carries no reply for {missing} — the smoke's own units are the rate's"
            " only sample, and a projection over a partial smoke prices a population nothing"
            f" measured. Wait for the three, or STOP. (dead units: {dead_units(replies) or 'none'})"
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


def append_measurement(row: dict) -> dict:
    """One row onto `results/measurements.jsonl`. The file is append-only: a rate is history."""
    with MEASUREMENTS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return row


def write_measurement(gate: dict) -> dict:
    """The smoke's rate into `results/measurements.jsonl`, under its OWN name and never the borrow's.

    It is marked `sample: smoke of three` and ruling 05.09 (t) item 4 prices NOTHING on it: three
    units chosen as shortest / median / LONGEST are a maximum wearing a mean's clothes.
    """
    return append_measurement(
        {
            "contract": CONTRACT,
            "name": f"{STEM}_seconds_per_thread",
            "sample": "smoke of three",
            "instrument": "promo-signal prompt (leg A), READER serving, thinking OFF, batch 1 — the"
            f" SMOKE's three units on this pod; it replaces the borrowed {BORROWED_RATE}",
            "measured_on": ", ".join(
                f"{unit} {seconds}s" for unit, seconds in gate["measured"]["seconds"].items()
            ),
            "n": gate["measured"]["n"],
            "unit": "seconds",
            "value": gate["measured"]["value"],
            "max": gate["measured"]["max"],
            "source": rel(RUN_RECORD),
        }
    )


def whole_run_row(replies: Path, pod_id: str) -> dict:
    """One pod's WHOLE-RUN seconds-per-thread — ruling 05.09 (t) item 4, the row a leg is priced on.

    The units are the committed registration's `population.leg_a.order` and not «every line of the
    out-file»: leg B rides the same file and a post answered in 0.8 s is not a thread
    ([[a_second_population_in_a_shared_store_voids_the_first_seal]]). The POD is named and checked
    against the run record's own segments — a rate is a property of the pod
    ([[a_rate_is_a_property_of_the_pod]]), and a row whose pod the ledger never billed prices
    nothing. `n` is what the run answered, so an incomplete run measures the units it did — and
    ruling 05.09 (x) item 4 makes a DEAD unit one of those it did not: an error reply has no
    `seconds`, this row is written at `--close-segment` AFTER the money gate has landed, and a
    `KeyError` there would keep the bill and lose the measurement the next leg is priced on.
    """
    units = set(committed_registration()["population"]["leg_a"]["order"])
    answered = answered_rows(replies)
    seconds = [float(row["seconds"]) for unit, row in answered.items() if unit in units]
    dead = [one for one in dead_units(replies) if one in units]
    if not seconds:
        raise SystemExit(
            f"{rel(replies)} answers no registered leg-A unit of {rel(PREREG)} — there is no whole"
            f" run here to measure, and a rate over nothing prices nothing. (dead units:"
            f" {dead or 'none'})"
        )
    segments = [one for one in run_state()["segments"] if one.get("pod_id") == pod_id]
    if len(segments) != 1:
        raise SystemExit(
            f"{rel(RUN_RECORD)} carries {len(segments)} segments for pod {pod_id} — the row names"
            " the pod it was measured on, and a pod the ledger never billed is a pod nothing paid"
            " for."
        )
    segment = segments[0]
    return {
        "contract": CONTRACT,
        "name": f"{STEM}_seconds_per_thread",
        "sample": WHOLE_RUN,
        "instrument": "promo-signal prompt (leg A), READER serving, thinking OFF, batch 1 — the"
        f" WHOLE run of pod {pod_id}: every registered leg-A unit it answered, not a sample of"
        " them. Ruling 05.09 (t) item 4 makes this the row a leg is priced on.",
        "measured_on": f"pod {pod_id}, {len(seconds)} leg-A threads on {segment['card']} at"
        f" ${segment['usd_per_hour']}/h, {rel(PREREG)}'s population"
        + (f"; {len(dead)} unit(s) DEAD and counted unanswered: {dead}" if dead else ""),
        "n": len(seconds),
        "dead_units": dead,
        "unit": "seconds",
        "value": round(sum(seconds) / len(seconds), 4),
        "max": round(max(seconds), 4),
        "source": rel(replies),
        "pod_id": pod_id,
        "run_record": rel(RUN_RECORD),
    }


def line_anchor(record: dict) -> datetime:
    """When the line THIS record spends under was OPENED — `anchored_at` of the ledger it names.

    Ruling 06.09 (y) item 4, risk 3, fixed under (z) item 3. The run record is written at BATCH
    scale and carries every pod of the dev loop since iteration 1, so a sum over all its segments
    printed iteration 5's $0.9396 as `spent_all_segments_usd 2.874083`, `verdict OVER` — seven pods
    against one line's $1.40, a false field nothing gated on (the money is the guard's line). A
    segment belongs to a line when it was created at or after the line's anchor, which `--register`
    wrote when it OPENED the line ([[the-registration-opens-the-line]]). The ledger is the one the
    committed registration names — never a path built here a second time from the step's name.
    """
    named = record.get("step", {}).get("ledger")
    path = REPO_ROOT / named if named else None
    stamp = load(path).get("anchored_at") if path is not None and path.exists() else None
    if not stamp:
        raise SystemExit(
            f"{rel(PREREG)} names {named or 'no ledger'} and it carries no `anchored_at` — this"
            " line's segments cannot be told from the batch's, and a sum over the batch is the"
            " false OVER of ruling 06.09 (y) item 4. Refuse."
        )
    return datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))


def created_at(segment: dict) -> datetime:
    """A segment's create stamp as a moment — RunPod writes `…Z`, the ledger `…+00:00`."""
    return datetime.fromisoformat(str(segment["created_at"]).replace("Z", "+00:00"))


def close_segment(*, deleted_at: str, billed_seconds: float, outcome: str) -> dict:
    """The segment's own bill, at its OWN price, summed with THIS line's segments only.

    Never a balance delta — that prices the account. And never the whole run record — that is one
    file per leg at batch scale: the segments summed against the line's cap are those created at
    or after the line's anchor (`line_anchor`), so the verdict is the line's and not the batch's.
    """
    state = run_state()
    if not state["segments"] or state["segments"][-1].get("deleted_at"):
        raise SystemExit("no segment is open — there is nothing to close")
    segment = state["segments"][-1]
    segment["deleted_at"] = deleted_at
    segment["billed_seconds"] = billed_seconds
    segment["billed_usd"] = round(billed_seconds * float(segment["usd_per_hour"]) / 3600, 6)
    segment["outcome"] = outcome
    record = committed_registration()
    anchor = line_anchor(record)
    own = [one for one in state["segments"] if created_at(one) >= anchor]
    if segment not in own:
        # the fix's own consequence: a filter that dropped the very bill it just wrote would print a
        # GO beside a `billed_usd` the line never counted — a gate contradicting itself
        raise SystemExit(
            f"the segment being closed ({segment['pod_id']}, created {segment['created_at']})"
            f" predates its own line's anchor {anchor.isoformat(timespec='seconds')} — nothing is"
            " written; check the --created-at stamp against the ledger the record names"
        )
    spent = sum(float(one.get("billed_usd") or 0) for one in own)
    cap = float(record["step"]["cap_usd"])
    return append_gate(
        state,
        "close",
        {
            "verdict": "GO" if spent <= cap else "OVER",
            "billed_seconds": billed_seconds,
            "billed_usd": segment["billed_usd"],
            "line": record["step"].get("name"),
            "line_anchored_at": anchor.isoformat(timespec="seconds"),
            "segments_of_this_line": len(own),
            "spent_this_line_usd": round(spent, 6),
            "cap_usd": cap,
            "left_usd": round(cap - spent, 6),
            "outcome": outcome,
        },
    )


DEV_ARMS = {
    "dev40": {
        "draw_part": "dev",
        "stem": "promo_dev40",
        "gold": REPO_ROOT / "docs" / "labels-promo-dev.jsonl",
    },
    "dev2": {
        "draw_part": "holdout",
        "stem": "promo_dev2",
        "gold": REPO_ROOT / "docs" / "labels-promo-dev2.jsonl",
    },
}
"""The dev leg's arms, in the order the pod answers them — the BAR arm dev-40 FIRST, the reading
arm dev-2 after (ruling 05.09 (t) item 5). Each names three things that must agree: the part of the
FIRST draw its units were drawn in, the stem `--score` names its files after, and its own answer
key. They are the dev leg's and no other leg's: `draw_part` «holdout» here is dev-2, the SPENT
holdout-40 that ruling 05.09 (s) item 3 relabelled, and it is not the holdout LEG — the same word in
two id spaces, which is why `use_arm` refuses any arm outside `--part dev`
([[id_spaces_that_look_comparable]])."""

DEV_FILES = {
    "gold": GOLD,
    "prep": PREP,
    "prereg": PREREG,
    "pack": PACK,
    "run": RUN_RECORD,
    "step": STEP,
    "stem": STEM,
    "arms": tuple(one["draw_part"] for one in DEV_ARMS.values()),
    "draw": DRAW,
}
"""The dev loop's own files, captured here so `use_part` binds EVERY leg and none is «what the
constants already are». A selector with a leg that quietly does nothing reads as a selector that
worked ([[a_moved_guard_that_left_its_copy]]).

`arms` is the dev leg's population from iteration 4 on: dev-40 FIRST, then dev-2 — the SAME first
draw's two arms, because ruling 05.09 (s) item 3 relabelled the spent holdout-40 as a reading. It is
DERIVED from `DEV_ARMS` above and never listed twice: two lists of one population drift, and the
pack's order is the one the scorer must slice back apart. The holdout leg still names the first
draw's holdout arm; holdout-2 is `HOLDOUT2_FILES`, over `DRAW2`."""


def leg_golds() -> list[Path]:
    """Every answer key this leg is graded on, the BAR arm's FIRST — what a registration pins.

    A leg of two arms has two, and ruling 05.09 (u) item 2 pins both: dev-2 carries no bar, and a
    reading needs its reference pinned as much as a bar does. `--gold` overrides the BAR arm's key
    (the holdout names its own on the command line, §4), and the reading arms keep their own file —
    so an override replaces a pin instead of leaving a second, stale one beside it."""
    if PART != "dev":
        return [GOLD]
    return [GOLD] + [one["gold"] for one in list(DEV_ARMS.values())[1:]]


def use_arm(arm: str, *, gold: Path | None = None) -> None:
    """Point the SCORER at ONE arm of this leg — never at the registration, which pins them all.

    Called from the `--score` branch alone, because binding `GOLD` here on a `--register` run would
    pin a reading arm's key as the leg's bar key. `--gold` still wins over the arm's own file."""
    global ARM, STEM, GOLD
    files = DEV_ARMS.get(arm) if PART == "dev" else None
    if files is None:
        raise SystemExit(
            f"--arm {arm}: the arms are {', '.join(DEV_ARMS)} and they are the DEV leg's — this"
            f" run is --part {PART}. The holdout leg is ONE arm and chooses none."
        )
    ARM, STEM = arm, files["stem"]
    GOLD = gold or files["gold"]


def use_part(part: str, *, gold: Path | None = None, step: str | None = None) -> None:
    """Point this module's file constants — the draw among them — at ONE leg.

    Called once, from `main`, before any branch reads them — so a process is about the dev loop,
    about the spent holdout or about holdout-2, and never about two of them. EVERY leg is bound,
    so `use_part("dev")` after a holdout call really returns to the dev loop instead of leaving the
    holdout in place. `--gold` and `--step` override afterwards, because §4 makes a re-used producer
    take its paths as parameters and a holdout's gold is a pin the paid session names on the
    command line."""
    global PART, GOLD, PREP, PREREG, PACK, RUN_RECORD, STEP, STEM, ARMS, DRAW
    files = {"dev": DEV_FILES, "holdout": HOLDOUT_FILES, "holdout2": HOLDOUT2_FILES}.get(part)
    if files is None:
        raise SystemExit(
            f"--part {part}: the legs are dev, holdout and holdout2 (ruling 06.09 (z) item 4), and"
            " no fourth"
        )
    PART, STEM, STEP, ARMS = part, files["stem"], files["step"], files["arms"]
    GOLD, PREP, DRAW = files["gold"], files["prep"], files["draw"]
    PREREG, PACK, RUN_RECORD = files["prereg"], files["pack"], files["run"]
    if gold is not None:
        GOLD = gold
    if step is not None:
        STEP = step


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--part",
        default="dev",
        choices=("dev", "holdout", "holdout2"),
        help="which leg: the first draw's dev half, its spent holdout half, or the second draw",
    )
    parser.add_argument("--gold", type=Path, help="the part's answer key; the registration pins it")
    parser.add_argument(
        "--arm",
        help="which arm of the leg --score grades: its units, its answer key, its part of the draw",
    )
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
        "--measure-run",
        action="store_true",
        help="$0: one pod's WHOLE-RUN seconds-per-thread into results/measurements.jsonl",
    )
    parser.add_argument(
        "--score", action="store_true", help="$0: the pod's replies → K8's rows and the error table"
    )
    parser.add_argument(
        "--project", action="store_true", help="$0: the smoke's rate and the decision table"
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="$0: the smoke's own units — which branch of the decision table, on a LIVE pod",
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
            + (f"${floor:.2f}" if floor is not None else record["step"]["floor_rule"])
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

    if args.measure_run:
        for name in ("replies", "pod_id"):
            if getattr(args, name) is None:
                parser.error(
                    f"--measure-run needs --{name.replace('_', '-')}: a whole-run rate is a"
                    " property of ONE pod and is read off the units that pod answered"
                )
        row = append_measurement(whole_run_row(args.replies, args.pod_id))
        print(f"appended to {rel(MEASUREMENTS)}: {row['name']} «{row['sample']}»"
              f" = {row['value']} s/thread (max {row['max']}, n={row['n']}) — {row['measured_on']}")
        return 0

    if args.close_segment:
        for name in ("deleted_at", "billed_seconds", "outcome"):
            if getattr(args, name) is None:
                parser.error(f"--close-segment needs --{name.replace('_', '-')}")
        pod_id = (run_state()["segments"] or [{}])[-1].get("pod_id")
        state = close_segment(
            deleted_at=args.deleted_at,
            billed_seconds=args.billed_seconds,
            outcome=args.outcome,
        )
        print(json.dumps(state["gates"][-1], ensure_ascii=False, indent=1))
        # ruling 05.09 (t) item 4 — the whole-run row is written HERE, at the close, so the next
        # leg is priced on what this pod actually ran. A segment with no out-file (a dead-man that
        # launched nothing) has no run to measure and says so instead of writing a row over nothing.
        if args.replies is None:
            print("\nno --replies: NO whole-run rate row was written for this segment. Ruling"
                  " 05.09 (t) item 4 prices every later leg on such a row — pass the pod's own"
                  " out-file unless this segment answered nothing.")
        else:
            row = append_measurement(whole_run_row(args.replies, pod_id))
            print(f"\nappended to {rel(MEASUREMENTS)}: {row['name']} «{row['sample']}»"
                  f" = {row['value']} s/thread (max {row['max']}, n={row['n']})")
        return 0 if state["latest"]["verdict"] == "GO" else 1

    if args.smoke:
        if args.replies is None:
            parser.error("--smoke needs --replies: the pod's own out-file is what it reads")
        state = smoke_state(args.replies)
        print(render_smoke(state))
        # $0 and it writes NOTHING: this runs while the pod is billing, and a reading that appended
        # a gate would make a poll a verdict ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]]).
        return 0 if state["state"] == SMOKE_IN else 1

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
        print(f"  corpus     {record['corpus']['comments_with_text']} comments with text ("
              + " + ".join(f"{n} {split}" for split, n in record["corpus"]["by_split"].items())
              + ")")
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
        if args.arm is None and len(ARMS) > 1:
            parser.error(
                "--score needs --arm on a leg of two arms: one grade over the leg's answered units"
                " against a key that covers one arm of them is a grade of neither"
                " ([[measure_on_the_rows_the_gate_scores]]). Name it — "
                + " or ".join(f"--arm {one}" for one in DEV_ARMS)
            )
        if args.arm is not None:
            use_arm(args.arm, gold=args.gold)
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
              f" · {answers['parse_failures']} unparsed {answers['parse_failures_by_cause'] or ''}"
              + (f" · {len(answers['leg_a_units_dead'])} DEAD (unanswered):"
                 f" {answers['leg_a_units_dead']}" if answers["leg_a_units_dead"] else ""))
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
        own = bound["priced_from"]["sample"] == WHOLE_RUN
        print(f"wrote {rel(out)}")
        print(f"  law           {record['law']['codebook']} sha {record['law']['codebook_sha256'][:16]}…")
        print(f"  corpus        {bound['threads']} {PART} threads · {corpus['chars_total']} chars ·"
              f" longest {corpus['chars_max']} · {corpus['distinct_renders']} distinct renders")
        print(f"  gold          {record['gold']['path']} — "
              + (f"sha {record['gold']['sha256'][:16]}… · {record['gold']['lines']} rows"
                 if record["gold"]["sha256"] else "gold missing -> no record"))
        print(f"  {'MEASURED' if own else 'BORROWED'} rate {bound['priced_from']['name']} ="
              f" {bound['priced_from']['value']} s/thread (n={bound['priced_from']['n']},"
              f" max {bound['priced_from']['max']}) — "
              + ("this instrument's OWN, the WHOLE run of the slowest pod it has run on"
                 if own else "another prompt, pod and transport"))
        print(f"  bound         ${bound['usd_at_the_mean']} at its mean ·"
              f" ${bound['usd_at_the_max']} at its max, boot excluded — NOT a price")
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
