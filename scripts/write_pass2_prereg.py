#!/usr/bin/env python3
"""`results/prereg_pass2_signals.json` — the law of the ONE paid session of `pass2-signals`.

Every threshold this contract acts on is written HERE and nowhere else, and the H6 block at the
bottom re-derives every number `docs/PROMPT-pass2-signals.md` prints, from the file it comes out of.
A mismatch is a REFUSAL: `main` exits non-zero and nothing is written, which is the step-1 gate the
executor's instruction asks for ([[preregistration_is_a_file_not_a_constant]]).

**The money is in two halves and that is the whole design.** This prompt has no rate — pass-1 replies
were ~50 tokens and a pass-2 reply is a list of signals — so the SMOKE (the reference's five flagship
threads) is priced at an assumed ceiling of 120 s/call and the FULL run is priced from the smoke's
own reading on the same pod, with rung S′ between them. `money.arithmetic.total_seconds` is
therefore the SMOKE's worst case and not the run's: rung 0 authorises a create against what the
registration can actually pay for before anything is measured, and the remaining 74 units are
authorised by a guard that runs after the money that measures them has been spent.

**The deadlines are read by KEY.** `docs/PROMPT-pass2-signals.md` D0: «the deadlines of every rung
read by KEY, not by `first_number` over prose (Dv669)». Every clock rung carries
`deadline_seconds`, and `scripts/gate_pass2_signals.py` is what makes the inherited call sites read
it — see there. This file's job is to put the number in a field.

    PYTHONPATH=src python3.11 scripts/write_pass2_prereg.py
    PYTHONPATH=src python3.11 scripts/write_pass2_prereg.py --out /tmp/again.json   # the pair
"""

import json
import math
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pass2_pack as builder  # noqa: E402
import score_reader_probe_b as readerscore  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import pass2, prompts  # noqa: E402

RESULTS = REPO_ROOT / "results"
OUT = RESULTS / "prereg_pass2_signals.json"
PACK = RESULTS / "pass2_pack.json"
GOLD = RESULTS / "reader_gold_w1_r2.json"
CENSUS = RESULTS / "pass1_window_r2_census.json"
V5B_VERDICT = RESULTS / "reader_v5b_verdict.json"
V5B_ROWS = RESULTS / "reader_v5b_w1.jsonl"
V5B_PACK = RESULTS / "reader_v5b_pack.json"
WINDOW_R2_REPORT = "docs/reports/pass1-window-r2.md"

PHASE = "pass2-signals"
LEG = "v1"
OUT_FILE = "pass2_signals_v1.jsonl"

# ---------------------------------------------------------------------------------------------
# the constants of this registration. Each is typed ONCE, here, with the derivation that produced
# it; everything below is computed. H6 re-derives every one that has a file behind it.
# ---------------------------------------------------------------------------------------------

CAP_USD = 1.50
"""`docs/PROMPT-pass2-signals.md` and the ADR's table (д) — the second of the two contracts."""

HARD_STOP_SECONDS = 6600.0
"""Cumulative billed seconds, PLATFORM-held through `--terminate-after`. 6 600 s = $1.4667 at the
price ceiling, which sits under the $1.50 cap it defends."""

PRICE_CEILING_USD_PER_HOUR = 0.80
"""Rung 1 refuses a create above it. The 4090 24 GB this line has rented four times costs $0.74."""

SMOKE_SECONDS_PER_CALL = 120.0
"""**THE ONE ASSUMPTION IN THIS RECORD, and it is named as one.** A 600-token reply at a 5 tok/s
worst decode plus prefill. Nothing on this stack has measured a pass-2 decode; what it HAS measured
is the reader's, which is the nearest shape — v5b's leg A ran 45.016 s a thread over 23 threads at
864.9 completion tokens a reply, and its two widest threads (both of them F threads) took 108.4 and
103.8 s. The assumption is 2.67× that mean and 1.11× that maximum. It is charged on FIVE calls and
on nothing else."""

SSH_SECONDS = 500.0
STAGE_LAUNCH_SECONDS = 150.0
LOAD_SECONDS = 450.0
"""Pre-generation, charged as `pass1-window r2` charged it and for its reasons: the ssh spread ran
14.5 → 262.5 s over five readings, staging is a git bundle and a checkout, and the boot of this
stack is not a constant (142.7 / 146.8 / 164.9 / 192.1 / 237.2 / 267 / 293 / 353 s). Charged ONCE:
the runner waits for the go with the model in the card, so there is no second load."""

OVERHEAD_SECONDS = 1300.0
"""The same bucket r2 charged — the watch tail, the copy-backs, the deletion tail and the slack
between the last reply and the delete. Rung 4 prices the attempt with it on every poll, so it is one
number and H6 asserts the projection gate carries the same one."""

BACKSTOP_TOLERANCE_SECONDS = 60.0
"""How far the `--terminate-after` stamp actually given to `pod create` may sit BEYOND the computed
one. Only overshoot is bounded: a window rounded DOWN shortens itself and is always safe."""

SSH_DEADMAN_SECONDS = 500.0
LAUNCH_TO_FIRST_REPLY_SECONDS = 450.0
BOOT_BACKSTOP_SECONDS = 1100.0
"""Rung 3's create-anchored backstop = the charged pre-generation. r2's construction: the anchor is
the runner's own `launched_at` and the backstop is what bounds a pod that never wrote one."""

LIVENESS_SECONDS = 600.0
"""Rung 5, from the LAST EVENT. A pass-2 call may take minutes, so the event is the pod LOG line the
runner prints per call — and the WAIT line it prints per poll while it waits for the go — beside a
new out-file row."""

GO_WAIT_SECONDS = LIVENESS_SECONDS
"""Rung S's own deadline: how long the pod waits for the Mac's token before it stops answering.

DERIVED and not chosen — it is rung 5's liveness period. The Mac has one full liveness period to
answer; a Mac that has not answered in one is a Mac the pod should stop waiting for, and the pod
that stops printing then falls to rung 5 on the Mac's own clock."""

PROJECTION_MULTIPLIER = 1.5
"""Rung S′: `charged_full = max(1.5 × smoke_mean, smoke_max)`. Same pod, so what is charged is the
CALL-LENGTH spread and not the pod-class spread."""

PROJECTION_EVERY_CALLS = 20

REFUSALS_FRACTION = 0.174
"""The completeness bar's third number — MEASURED on this schema, not carried from pass 1.

Pass 1's 1 % was derived for an answer of four SCALARS. A pass-2 reply is the reader's four LISTS
with a domain check on every field of every row, and the only rate this stack has measured for that
shape is the reader's own: `results/reader_v5b_verdict.json` refused **4 of 23 = 0.174** after the
2026-08-16 sitting's container repairs and v5's balanced-brace stop, and `reader_probe_b` refused
10 of 23 before them. Carried at 1 %, `int(0.01 × 79)` is **0** — a bar that allows no refusal at
all, against an instrument measured at 17 %, on both arms. That is a bar no reading reaches
([[the_expectation_no_reading_reaches]], [[an_absolute_bar_needs_a_reachability_state]]).

Charged at the top of what was measured and NOT tightened by the story that two of v5b's four
causes — `missing field: entities`, twice — cannot occur here because pass 2 injects that list. The
story is registered beside the number; the number is the measurement."""

RELABELLINGS_ARE_OUTSIDE_THE_BUDGET = True
"""A relabelling does not spend the transport budget, and this is the split the bar rests on.

Rung 7 asks whether the POD delivered: every unit answered, every sha matching, no duplicate and no
unknown id, and the replies readable at the rate this schema is readable at. A reply that rewrote a
pass-1 subject is readable — it says something this pass has no authority to say, which is the ADR's
line arriving as a MEASUREMENT. It is counted by its own cause and reported, and bars 1/2/3 are
where it shows up as a result ([[count_the_kind_not_the_rows]])."""


def pack() -> dict:
    return json.loads(summary.read_text_or_refuse(PACK))


def gold() -> dict:
    return json.loads(summary.read_text_or_refuse(GOLD))


def rows(path: Path) -> list[dict]:
    return [
        json.loads(one) for one in summary.read_text_or_refuse(path).splitlines() if one.strip()
    ]


def v5b_seconds() -> dict:
    """The nearest measured decode this stack owns — the reader's, leg A, per thread.

    Read out of `results/reader_v5b_w1.jsonl` and never typed: the assumption above is only honest
    if the thing it is 2.67× of is a number somebody can re-derive. Leg B is excluded — its units
    are CHUNKS of one 43-comment thread and one of its rows carries no usage at all.
    """
    leg = [one for one in rows(V5B_ROWS) if str(one.get("leg")).casefold() == "a"]
    seconds = [float(one["seconds"]["worker"]) for one in leg]
    tokens = [
        int((one.get("usage") or {}).get("completion_tokens") or 0)
        for one in leg
        if (one.get("usage") or {}).get("completion_tokens")
    ]
    widest = max(leg, key=lambda one: one["seconds"]["worker"])
    return {
        "record": summary.rel(V5B_ROWS),
        "sha256": summary.sha256_of(V5B_ROWS),
        "threads": len(leg),
        "mean_seconds_per_thread": round(statistics.mean(seconds), 3),
        "max_seconds_per_thread": round(max(seconds), 3),
        "min_seconds_per_thread": round(min(seconds), 3),
        "slowest_thread": widest["thread"],
        "mean_completion_tokens": round(statistics.mean(tokens), 1),
        "max_completion_tokens": max(tokens),
        "reading": (
            "the READER's shape and not pass 2's: a v5b reply carries `entities` with their quotes"
            " and a per_comment row for every comment of the thread, while a pass-2 reply carries"
            " no entities and only the FILTERED rows. So this is an upper reading of pass 2's"
            " decode on ANOTHER pod, and it is here to say what the assumption is 2.67× of — never"
            " to price this run ([[a_rate_is_a_property_of_the_pod]])"
        ),
    }


def population(held: dict) -> dict:
    census = json.loads(summary.read_text_or_refuse(CENSUS))
    table = census["pass_2_filter"]
    items = held["legs"][0]["items"]
    widest_rows = max(items, key=lambda one: len(one["comments"]))
    widest_chars = max(items, key=lambda one: sum(len(row["text"]) for row in one["comments"]))
    return {
        "units": len(items),
        "payable_comments": len(items),
        "payable_comments_is_the_UNIT_count": (
            "the same aliasing the pack carries, and for the same reason:"
            " `gate_pass1_window.main` hard-subscripts `population.payable_comments` in BOTH files"
            " before every rung that reads a pack, and that file is pinned by a sealed record of a"
            " closed paid session. A pass-2 unit is a THREAD. Without this key `--projection`,"
            " `--watch`, `--completeness` and `--close` all die on a KeyError — on a pod that is"
            " already billing, with nothing watching it"
        ),
        "smoke_units": held["smoke"]["units"],
        "remaining_after_the_smoke": len(items) - held["smoke"]["units"],
        "filtered_rows": held["population"]["filtered_rows"],
        "filtered_chars": held["population"]["filtered_chars"],
        "out_file": OUT_FILE,
        "leg": LEG,
        "record": summary.rel(PACK),
        "sha256": summary.sha256_of(PACK),
        "filter": list(pass2.PASS2_SUBJECT_TYPES),
        "keyed_on": (
            "the PAIR (thread, msg_id). The ADR's acceptance correction, and this registration is"
            " where it was required to be said: seven msg_ids of window 1 live in two threads each"
        ),
        "threads_pass_2_would_not_call": table["threads_pass_2_would_not_call"],
        "no_signal_by_construction": (
            f"{table['threads_pass_2_would_not_call']} of the"
            f" {table['threads_carrying_a_payable_comment']} callable threads carry no row pass 1"
            " labelled one of the three. They are NOT called and they are not a failure — the"
            " filter answered about them"
        ),
        "widest_unit_rows": {"thread": widest_rows["id"], "rows": len(widest_rows["comments"])},
        "widest_unit_chars": {
            "thread": widest_chars["id"],
            "chars": sum(len(row["text"]) for row in widest_chars["comments"]),
        },
        "input_ceiling": held["length"],
        "derived_by": held["population"]["producer"],
        "census": {"record": summary.rel(CENSUS), "sha256": summary.sha256_of(CENSUS)},
    }


def reachability(held: dict) -> dict:
    """Which registered cases pass 2's population can answer AT ALL — computed, before the pod.

    A case whose thread is not called cannot be answered, and a bar scored over it fails by
    arithmetic rather than by reading. `results/reader_gold_w1_r2.json::reachability` says exactly
    that about the READER's population; this is the same question asked of pass 2's, and the answers
    are different in both directions — E1 falls out, E4's two threads come IN.
    """
    record = gold()
    called = {one["id"] for one in held["legs"][0]["items"]}
    inside = {
        one["id"]: {int(row["msg_id"]) for row in one["comments"]}
        for one in held["legs"][0]["items"]
    }
    # the labels of the WHOLE window and not of the filtered rows only. Built from the pack alone, a
    # gold evidence row outside the filter reports `null` — and this same record's F5 expectation
    # says in prose that pass 1 labelled 579457 `не_наш_рынок`. Two values for one input, inside one
    # pre-registered record, is the class this line keeps making
    # ([[two_values_for_one_input_get_quoted_kindly]])
    answers, _table, _refusals = builder.filtered(builder.r2builder.r1_pack())
    labels: dict[str, dict[int, str | None]] = {}
    for item_id, answer in answers.items():
        thread, _, msg_id = item_id.rpartition("#")
        labels.setdefault(thread, {})[int(msg_id)] = answer.get("subject_type")
    flagships = []
    for case in record["flagships"]:
        name = f"{case['channel']}:{case['post_id']}"
        for signal in case["signals"]:
            cited = {msg_id: labels.get(name, {}).get(msg_id) for msg_id in signal["evidence"]}
            in_filter = {
                msg_id: label
                for msg_id, label in cited.items()
                if msg_id in inside.get(name, set())
            }
            wanted = signal["subject_type"]
            flagships.append(
                {
                    "id": signal["id"],
                    "case": case["id"],
                    "thread": name,
                    "thread_is_called": name in called,
                    "gold_subject_type": wanted,
                    "pass_1_labels_of_the_cited_rows": cited,
                    "pass_1_labels_rule": (
                        "every cited row's label as PASS 1 answered it, whether or not the filter"
                        " kept the row. A row the filter dropped is named below and pass 2 never"
                        " sees it — but the record may not carry `null` for a label it states in"
                        " prose two blocks away"
                    ),
                    "evidence_rows_inside_the_filter": sorted(in_filter),
                    "evidence_rows_outside_the_filter": sorted(set(cited) - set(in_filter)),
                    "reachable": bool(in_filter)
                    and (wanted is None or wanted in set(in_filter.values())),
                }
            )
    entity = []
    for case in record["entity_cases"]:
        name = f"{case['channel']}:{case['post_id']}"
        entity.append({"id": case["id"], "thread": name, "thread_is_called": name in called})
    noise = []
    for case in record["noise_threads"]:
        name = f"{case['channel']}:{case['post_id']}"
        noise.append(
            {
                "id": case["id"],
                "thread": name,
                "thread_is_called": name in called,
                "filtered_rows": len(inside.get(name, set())),
            }
        )
    return {
        "rule": (
            "strict authority makes a flagship signal reachable only where the pass-1 label of a"
            " row it cites IS the gold's subject_type — `scorer.reader_signal_found` matches on"
            " EVIDENCE and then compares `subject_type` AND `aspect`, each where the gold states"
            " one. A signal whose every cited row pass 1 labelled something else cannot be answered"
            " without a relabelling, and a relabelling is a parse refusal. **REACHABLE is a"
            " statement about CONSTRUCTION and not a prediction:** the aspect is the model's to"
            " answer, and exactly three of the seven gold signals state one — F1's three, which is"
            " an all-or-nothing case, which is why `prompts.READER_ASPECT_V5` is spliced into the"
            " pass-2 text rather than retyped from the pre-v3 wording"
        ),
        "flagship_signals": flagships,
        "entity_cases": entity,
        "noise_threads": noise,
        "unreachable_flagship_signals": [one["id"] for one in flagships if not one["reachable"]],
        "unreachable_entity_cases": [one["id"] for one in entity if not one["thread_is_called"]],
        "noise_threads_pass_2_calls": [one["id"] for one in noise if one["thread_is_called"]],
    }


def bar_two_at_zero(held: dict) -> dict:
    """Bar 2's value, COMPUTED before the pod — because `entities` is bought and not answered.

    The list pass 2 returns is the thread's entity block, so the bar the reader's scorer computes
    over it is decided by the pack and by the watchlist matcher, not by the model. Publishing the
    number here is the honest form of «reported as held, never claimed as pass 2's own»: a run that
    came back and reported 3 of 4 would otherwise read as a measurement
    ([[a_provenance_field_can_void_the_gate]] read forwards — a field nothing can move is a field
    whose value belongs in the registration).
    """
    record = gold()
    called = {one["id"]: one["entities"] for one in held["legs"][0]["items"]}
    verdicts = {
        name: {"entities": block, "signals": [], "per_comment": [], "noise": []}
        for name, block in called.items()
    }
    result = readerscore.entity_cases(record, verdicts, set(called), readerscore.aliases())
    return {
        "computed_before_the_pod": True,
        "cases_answered": result["cases_answered"],
        "cases": result["cases"],
        "passed": result["passed"],
        "per_case": result["per_case"],
        "per_row": result["per_row"],
        "why_it_is_knowable": (
            "the entity block is the BOUGHT v5b/v4/topup verdict, passed through and never"
            " re-resolved. The model is not asked for it and cannot move it, so this number is a"
            " property of the pack and of `brands.find_watchlist_brands`"
        ),
        "why_the_bar_is_still_registered": (
            "the contract registers it and it is the INHERITANCE that is being reported: the"
            " signal layer's entity resolution is v5b's, it holds for E2/E3/E4 inside pass 2's"
            " population, and E1's thread carries no filtered row so pass 2 never calls it. The"
            " bar is not moved for that — the reachability is named"
        ),
    }


def bars(held: dict, reach: dict) -> dict:
    record = gold()
    units = len(held["legs"][0]["items"])
    smoke = held["smoke"]["units"]
    noise_called = reach["noise_threads_pass_2_calls"]
    scored_noise = [one for one in noise_called if one != "N1"]
    return {
        "1_flagships": {
            "rule": (
                "F1–F5, 5 of 5, every named signal found: signal_type + subject (collapsed) + at"
                " least one named evidence msg_id. All or nothing, as the reference says"
            ),
            "scorer": "score_reader_probe_b.flagships, through scorer.reader_signal_found",
            "threshold": "5 of 5 cases",
            "scored_over": [one["id"] for one in record["flagships"]],
            "collapsed": (
                "scored BOTH ways and the collapsed reading is the one quoted, as v5b's verdict"
                " quotes it: `score_reader_probe_b.COLLAPSE` folds «категория_личное» into"
                " «категория». Pass 2 answers pass 1's own word, so the two readings agree here —"
                " and both are published because a difference would be a finding"
            ),
            "expectation": {
                "F2": {
                    "expected": "RED",
                    "by_construction": True,
                    "why": (
                        "the gold's F2a is a `молочный_бренд` signal read from msg 580124, and pass"
                        " 1 labelled 580124 `сеть_ритейлер`. Strict authority forbids pass 2 from"
                        " saying the brand, so the only reply that could take F2 is one this"
                        " contract REFUSES as a relabelling"
                    ),
                },
                "F5": {
                    "expected": "reachable",
                    "why": (
                        "F5a cites 579379 and 579457; pass 1 labelled 579457 `не_наш_рынок`, so it"
                        " is outside the filter and pass 2 never sees it. 579379 IS inside and"
                        " `scorer.reader_signal_found` matches on ANY intersection of the evidence"
                        " lists, so citing it alone answers the case"
                    ),
                },
                "the_bar_is_not_moved": (
                    "F2's RED is registered as an EXPECTATION and the threshold stays 5 of 5. The"
                    " bar measures the signal layer as built, and a bar lowered to what the layer"
                    " can reach would measure nothing ([[the_expectation_no_reading_reaches]])"
                ),
                "reachable_signals": [
                    one["id"] for one in reach["flagship_signals"] if one["reachable"]
                ],
                "unreachable_signals": reach["unreachable_flagship_signals"],
            },
        },
        "2_entity_cases": {
            "rule": "E1–E4, 4 of 4 — INHERITED through the pass-through `entities` list",
            "scorer": "score_reader_probe_b.entity_cases, through scorer.reader_entity_found",
            "threshold": "4 of 4 cases",
            "scored_over": [one["id"] for one in record["entity_cases"]],
            "under_a_STOP": (
                "UNSCORED. None of E2/E3/E4's threads is one of the five F threads, so a STOP"
                " leaves `entity_cases` counting 0 of 4 against a registration that says 3 of 4 —"
                " a false RED where bar 3's is a false GREEN. Both are the same defect and both"
                " are answered by asking whether the cases were READ before reporting a number"
            ),
            "held_not_earned": (
                "reported as «held» and never claimed as pass 2's own. The value is computed"
                " before the pod because the model is not asked for the block"
            ),
            "computed": bar_two_at_zero(held),
        },
        "3_noise": {
            "rule": "zero signals out of the reference's N threads that pass 2 calls",
            "scorer": "score_reader_probe_b.noise, through scorer.reader_noise_count",
            "threshold": "0 signals",
            "scored_over": scored_noise,
            "excluded_with_cause": {
                "N1": (
                    "carried unchanged from r1 and from v5b's own verdict: the reference's S list"
                    " reads a signal inside this thread (S1, msg 21420), so a bar that failed the"
                    " machine for agreeing with the reference would measure nothing. It IS called"
                    " — pass 1 labelled two of its rows `сеть_ритейлер` — and its signal count is"
                    " reported beside the bar"
                )
            },
            "not_called": {
                "N3": "the thread carries no payable comment at all, so it is not in the window",
                "N4": "0 filtered rows — no signal by construction",
                "N5": "0 filtered rows — no signal by construction",
                "N6": "0 filtered rows — no signal by construction",
            },
            "under_a_STOP": (
                "UNSCORED, and it is registered here rather than discovered afterwards. N2"
                " (@VARUS_channel:10366) is NOT one of the five F threads, so a STOP at rung S′"
                " leaves this bar with no case in the evidence at all. The contract's «bars 1/3 on"
                " the five» reaches bar 1 — the five F threads ARE the smoke — and does not reach"
                " bar 3. `scorer.reader_noise_count({})` returns `signals: 0`, so a scorer that did"
                " not ask whether the cases were READ would report this bar GREEN over zero threads"
                " ([[a_pre_filter_cannot_certify_the_population]], [[a_checker_whose_failure_is_"
                "silence]])"
            ),
            "the_case_this_bar_is_really_about": (
                "N2 (@VARUS_channel:10366) carries FOUR rows pass 1 labelled `сеть_ритейлер` in a"
                " plus-spam thread. Pass 2 must DROP them into `noise`. This is the mention-vs-about"
                " confusion the whole line has been carrying, arriving as pass 2's own question"
            ),
            "scored_over_is_one_thread": len(scored_noise) == 1,
        },
        "completeness": {
            "rule": (
                "answered N / N · every row's `rendering_sha256` equals its pack item's ·"
                f" UNREADABLE replies ≤ {REFUSALS_FRACTION:.1%} of N (ceil), relabellings excluded."
                " All three, or RED — with N chosen by the ARM the go/no-go landed on"
            ),
            "arms": {
                "GO": {
                    "owed": units,
                    "answered_minimum": units,
                    "parse_refusals_maximum": math.ceil(units * REFUSALS_FRACTION),
                    "sha_mismatches_maximum": 0,
                },
                "STOP": {
                    "owed": smoke,
                    "answered_minimum": smoke,
                    "parse_refusals_maximum": math.ceil(smoke * REFUSALS_FRACTION),
                    "sha_mismatches_maximum": 0,
                },
            },
            "arm_rule": (
                "the arm is READ off the go/no-go's own recorded verdict and never chosen by hand."
                " A STOP is a registered outcome of this contract, not a failure, so it gets a"
                " completeness bar of its own over the units it authorised"
            ),
            "answered_means": (
                "a reply came back and was written into the out-file, counted by DISTINCT id. A"
                " parse refusal is an ANSWERED row whose reply the parser refused — the two counts"
                " are NOT disjoint ([[measure_on_the_rows_the_gate_scores]])"
            ),
            "parse_refusals_fraction": REFUSALS_FRACTION,
            "parse_refusals_fraction_rule": (
                "MEASURED on this schema and not carried from pass 1: results/reader_v5b_w1.jsonl"
                " refused 4 of 23 leg-A threads through the same parser after the same repairs."
                " Pass 1's 1 % was derived for an answer of four scalars, and `int(0.01 × 79)` is"
                " ZERO — a transport bar an instrument measured at 17 % cannot pass. Rounded UP"
                " with ceil, so the STOP arm's five units carry a budget of one rather than none"
            ),
            "relabellings_are_outside_the_budget": (
                "a reply that rewrote a pass-1 subject is READABLE. It says something this pass has"
                " no authority to say, which is the ADR's line arriving as a measurement, and it is"
                " counted by its own cause and reported beside the bar rather than spending a"
                " budget that exists to price a transport"
            ),
            "what_this_bar_is": (
                "TRANSPORT. Every unit answered, every sha matching, no duplicate and no unknown"
                " id, and the replies readable at the rate this schema is readable at. Whether the"
                " answers are RIGHT is bars 1/2/3, and they are a different question"
            ),
            "refusals_are_counted_by_cause": (
                "never dropped and never summed into one «other». A RELABELLING is its own cause"
                " and its own finding: it is the ADR's line, and a run whose refusals are all"
                " relabellings is a different result from one whose refusals are torn objects"
            ),
            "sha_rule": (
                "the pod re-renders every item from its own fields and REFUSES the whole leg if one"
                " sha does not match, so a mismatch on the Mac means the out-file and the pack"
                " parted AFTER the run"
            ),
        },
        "report_only": {
            "4_per_comment_agreement_is_NOT_registered": (
                "`per_comment` is pass 1's pass-through under strict authority, so a bar on the"
                " fourteen would be the SIXTH look at them through a threshold — the base 9/14,"
                " arm A 9/14, v2 registered for a shot it never fired, v2 inside r1's killed pass,"
                " v2 over the complete window at 11/14, and this. The ADR's «What binds» point 2"
                " forbids it, and it binds the team lead as well as the executor"
            ),
            "the_scorecard": (
                "per flagship: found / missing / why, citing the pass-1 label of the row it names"
            ),
            "the_DROP_table": (
                "the filtered rows pass 2 sent to `noise`, by thread and by pass-1 label — the FP"
                " reading of the filter, and the answer this contract was bought for"
            ),
            "subject_doubt_rate": "by pass-1 label — the FP/FN reading ruling (б) asked for",
            "the_v5b_comparison_row": {
                "record": summary.rel(V5B_VERDICT),
                "sha256": summary.sha256_of(V5B_VERDICT),
                "bar_1": "2 of 5 (collapsed)",
                "bar_2": "4 of 4",
                "rule": (
                    "the one-shot reader on the SAME gold and the SAME scorer, quoted from its own"
                    " sealed verdict and never re-scored. What is NOT the same is the population:"
                    " v5b read 23 threads including four the gate injects, and pass 2 calls 79"
                ),
            },
            "the_cost_of_the_signal_layer": "pass 1 $0.742055 + this step, beside v5b's $0.312592",
        },
    }


def kill_clock(people: dict) -> list[dict]:
    remaining = people["remaining_after_the_smoke"]
    smoke_worst = people["smoke_units"] * SMOKE_SECONDS_PER_CALL
    pre_generation = SSH_SECONDS + STAGE_LAUNCH_SECONDS + LOAD_SECONDS
    knife = (HARD_STOP_SECONDS - OVERHEAD_SECONDS - pre_generation - smoke_worst) / remaining
    return [
        {
            "rung": 1,
            "name": "price",
            "deadline_seconds": None,
            "rule": (
                f"live price > ${PRICE_CEILING_USD_PER_HOUR}/h at create → STOP, no endpoint. The"
                " backstop stamp is checked against the cumulative hard stop in the same command"
            ),
            "read": "`--price` refuses to record a pod above the ceiling",
            "before": "the first billed second",
        },
        {
            "rung": 2,
            "name": "ssh dead-man",
            "deadline_seconds": SSH_DEADMAN_SECONDS,
            "rule": (
                "the ssh endpoint has to answer inside this pod's create-elapsed deadline or KILL."
                " r2's ceiling, unmoved: two pods of 2026-08-20 were still unreachable past 230 s"
                " and the spread of five readings runs 14.5 → 262.5"
            ),
            "read": "`--gate0 [--ssh-ok]`",
            "before": "staging",
        },
        {
            "rung": 3,
            "name": "launch → first reply",
            "deadline_seconds": LAUNCH_TO_FIRST_REPLY_SECONDS,
            "anchor": "the runner's own `pass2_signals_launched_at`, copied back by --watch",
            "backstop_seconds": BOOT_BACKSTOP_SECONDS,
            "backstop_rule": (
                "create-anchored, and it equals the charged pre-generation. Without an anchor there"
                " is no GO: a rung whose deadline cannot be demonstrated has not been passed"
            ),
            "rule": (
                "the first reply has to land inside this many seconds of the runner's OWN launch"
                " stamp, or KILL. The create-anchored backstop bounds a pod that never wrote one"
            ),
            "read": "`--boot`, and every poll of `--watch` while no row has landed",
            "before": "the smoke's first reply",
        },
        {
            "rung": 8,
            "name": "S — the smoke",
            "deadline_seconds": GO_WAIT_SECONDS,
            "rule": (
                "the smoke leg is the reference's five flagship threads, charged"
                f" {SMOKE_SECONDS_PER_CALL:.0f} s/call = {smoke_worst:.0f} s. When they are"
                " answered the runner WAITS for the Mac's go token, and this deadline is how long"
                " it waits before it stops answering. It equals rung 5's liveness period by"
                " derivation: the Mac has one liveness period to answer"
            ),
            "the_assumption": (
                f"{SMOKE_SECONDS_PER_CALL:.0f} s/call is an ASSUMPTION and the only one in this"
                " record — a 600-token reply at a 5 tok/s worst decode plus prefill. It is charged"
                f" on {people['smoke_units']} calls and on nothing else"
            ),
            "the_smoke_is_not_a_sample": (
                "the five F threads carry 30 of the 281 filtered rows — 6.0 rows a thread against"
                " the population's 3.56, and v5b's two slowest leg-A threads are two of them. The"
                " rate they measure is charged on the remaining 74 AS REGISTERED, and the"
                " row-weighted reading is published beside it and never gates"
                " ([[a_reproducible_probe_can_be_unrepresentative]])"
            ),
            "read": "`--watch` returns GO when the authorised leg is answered",
            "before": "any unit beyond the five",
        },
        {
            "rung": 9,
            "name": "S′ — the go/no-go",
            "deadline_seconds": None,
            "rule": (
                "charged_full = max(1.5 × smoke_mean, smoke_max) s/call — same pod, so the spread"
                " charged is the CALL-LENGTH spread and not the pod-class spread. projected ="
                " cumulative_billed_now + remaining × charged_full + overhead. GO if projected ≤"
                " the cumulative hard stop; else STOP"
            ),
            "multiplier": PROJECTION_MULTIPLIER,
            "worked_arm": (
                f"the full run fits iff charged_full ≤ (hard_stop − overhead − pre_generation −"
                f" smoke_seconds − go_wait_seconds) / {remaining}; at a {smoke_worst:.0f} s smoke"
                f" and a ZERO wait that is {knife:.4f} s/call, and at the full registered wait it"
                " is 40.5405. The gate projects from the clock at the moment it decides, so the"
                " wait it actually took is inside the number — these two are the band"
            ),
            "knife_edge_seconds_per_call": round(knife, 4),
            "cumulative_not_create_elapsed": (
                "the contract writes `create_elapsed_now`; this gate computes it on"
                " `cumulative_billed_seconds`, which is create-elapsed PLUS every closed pod. The"
                " two are equal when no pod died, and where they differ the cumulative arm is the"
                " stricter one — a recovery must not hide a dead pod's seconds from the guard that"
                " authorises the spend. BOTH are printed (Dv630/655)"
            ),
            "on_stop": (
                "the five F-thread replies are scored — bars 1 and 3 on the five, the scorecard —"
                " and the question returns to the operator WITH the measured rate. No full run at a"
                " price the record did not register"
            ),
            "read": "`--go-no-go`, which RECORDS its verdict and writes the token only on GO",
            "before": "the remaining 74",
        },
        {
            "rung": 4,
            "name": "projection",
            "deadline_seconds": None,
            "rule": (
                f"projection gate every {PROJECTION_EVERY_CALLS} calls — a FLOOR; the gate runs it"
                " on every poll because it is a local computation and costs nothing. The projected"
                " attempt total at MEASURED rates, with the authorised leg's remaining calls priced"
                " at max(mean, last call), against BOTH the cap and the cumulative hard stop"
            ),
            "this_is_the_rate_rung": (
                "no separate rate rung is added. Rung 4 re-prices the remainder on every poll and"
                " kills a pod that cannot finish inside the stop at the first poll that shows it"
            ),
            "what_it_prices_before_the_go": (
                "the SMOKE and nothing else. The remaining 74 are not authorised until rung S′ says"
                " GO, and a projection that priced 79 units against a registration that has bought"
                " five would refuse the create it is guarding"
            ),
            "read": "every poll of `--watch`, and `--projection` on demand",
            "before": "every call after the first reply",
        },
        {
            "rung": 5,
            "name": "liveness",
            "deadline_seconds": LIVENESS_SECONDS,
            "rule": (
                "no new answered row AND no new pod-log line for this many seconds → KILL. The"
                " deadline is measured from the LAST EVENT and never from create, and an event is a"
                " RISE: a failed scp can shorten a local file and a drop is never work"
            ),
            "the_event_is_a_log_line_too": (
                "a pass-2 call may take minutes and the go wait writes no row at all, so the"
                " liveness event is the pod LOG line the runner prints per call and per wait poll,"
                " beside a new out-file row. `reader_v5_pod_runner.run` prints one per reply and"
                " `pass2_pod_runner.wait_for_go` prints one per poll — both asserted by test"
            ),
            "read": "`--watch`",
            "before": "a pod that has stopped working outliving its usefulness",
        },
        {
            "rung": 6,
            "name": "cumulative hard stop",
            "deadline_seconds": HARD_STOP_SECONDS,
            "rule": (
                "cumulative billed seconds, PLATFORM-held. Each pod's `--terminate-after` is its"
                " own create plus what the stop has left, and the overshoot it forgives is"
                f" {BACKSTOP_TOLERANCE_SECONDS:.0f} s"
            ),
            "read": "`--price` checks the stamp; the platform enforces it",
            "before": "a hung call no gate can see",
        },
        {
            "rung": 7,
            "name": "completeness",
            "deadline_seconds": None,
            "rule": (
                "answered N / N · every row's `rendering_sha256` equals its pack item's ·"
                f" UNREADABLE replies ≤ {REFUSALS_FRACTION:.1%} of N (ceil) — 14 of 79 on the GO arm"
                " and 1 of 5 on the STOP arm, relabellings excluded and counted by cause. N is read"
                " off the arm the go/no-go landed on. All three, or RED"
            ),
            "read": "`--completeness` on the Mac, after the pod is deleted",
            "on_red": (
                "the out-file goes back to the team lead WITH its refusals by cause. Nothing"
                " already bought is deleted and nothing is re-asked without the recovery clause"
            ),
            "before": "the census and the report",
        },
    ]


def arithmetic(people: dict) -> dict:
    smoke = people["smoke_units"]
    remaining = people["remaining_after_the_smoke"]
    pre_generation = SSH_SECONDS + STAGE_LAUNCH_SECONDS + LOAD_SECONDS
    smoke_generation = smoke * SMOKE_SECONDS_PER_CALL
    total = smoke_generation + pre_generation + OVERHEAD_SECONDS
    knife = (HARD_STOP_SECONDS - OVERHEAD_SECONDS - pre_generation - smoke_generation) / remaining
    return {
        "calls": {LEG: people["units"]},
        "authorised_before_the_go": smoke,
        "seconds_per_call": {
            LEG: SMOKE_SECONDS_PER_CALL,
            "rule": (
                "the registered FLOOR the projection uses before a leg has a reply. It is the"
                " SMOKE's charge, and it is deliberately the only rate this record carries: the"
                " full run's rate is not a number this registration knows, which is why rung S′"
                " exists"
            ),
            "the_assumption": (
                "a 600-token reply at a 5 tok/s worst decode plus prefill. NAMED as an assumption:"
                " nothing on this stack has measured a pass-2 decode"
            ),
            "nearest_measured_shape": v5b_seconds(),
        },
        "smoke_generation_seconds": smoke_generation,
        "pre_generation_seconds": pre_generation,
        "pre_generation_rule": (
            f"ssh {SSH_SECONDS:.0f} + stage/launch {STAGE_LAUNCH_SECONDS:.0f} + load"
            f" {LOAD_SECONDS:.0f}. Charged ONCE for the whole session: the runner waits for the go"
            " with the model in the card, and `pass1_fewshot_pod_runner.once` is what hands the"
            " second call the client the first one built"
        ),
        "overhead_seconds": OVERHEAD_SECONDS,
        "overhead_rule": (
            "r2's bucket, unmoved — the watch tail, the copy-backs and the deletion tail. Rung 4"
            " prices the attempt with it on every poll, so a second copy would be a second budget;"
            " H6 asserts the projection gate carries this same number"
        ),
        "total_seconds": total,
        "total_seconds_rule": (
            "**the SMOKE's worst case, all in — NOT the run's.** This is what rung 0 authorises a"
            f" create against. The full run at the registered {SMOKE_SECONDS_PER_CALL:.0f} s/call"
            f" would be {people['units'] * SMOKE_SECONDS_PER_CALL + pre_generation + OVERHEAD_SECONDS:.0f}"
            f" s — far outside the {HARD_STOP_SECONDS:.0f} s stop — and that is the point: the"
            " registration cannot price the full run, so it buys the measurement and registers the"
            " guard that decides on it"
        ),
        "hours": round(total / 3600, 4),
        "worst_case_usd_at_the_price_ceiling": round(total / 3600 * PRICE_CEILING_USD_PER_HOUR, 6),
        "worst_case_usd_at_the_measured_price": round(total / 3600 * 0.74, 6),
        "the_full_run_is_priced_by_rung_S_prime": {
            "formula": (
                f"charged_full = max({PROJECTION_MULTIPLIER} × smoke_mean, smoke_max); projected ="
                f" cumulative_billed_now + {remaining} × charged_full + {OVERHEAD_SECONDS:.0f}"
            ),
            "knife_edge_seconds_per_call": round(knife, 4),
            "knife_edge_formula": (
                f"({HARD_STOP_SECONDS:.0f} − {OVERHEAD_SECONDS:.0f} − {pre_generation:.0f} −"
                f" smoke_seconds − go_wait_seconds) / {remaining}, at a"
                f" {smoke_generation:.0f} s smoke"
            ),
            "knife_edge_at_a_zero_go_wait": round(knife, 4),
            "knife_edge_at_the_full_go_wait": round(
                (
                    HARD_STOP_SECONDS
                    - OVERHEAD_SECONDS
                    - pre_generation
                    - smoke_generation
                    - GO_WAIT_SECONDS
                )
                / remaining,
                4,
            ),
            "the_wait_is_billed_and_the_band_is_why": (
                f"the pod sits in `wait_for_go` while the Mac decides, and those seconds are"
                f" BILLED. The contract's own printed figure — {knife:.4f} — is the arm at a ZERO"
                " wait, and the other end of the band is the arm at the full registered wait. The"
                " gate does not use either: `--go-no-go` projects from `cumulative_billed_seconds`"
                " AT THE MOMENT the decision is taken, so whatever the wait actually cost is"
                " already inside the number that decides. These two are the band a reader should"
                " have in front of them, and neither is a threshold"
            ),
            "what_a_GO_needs": (
                f"smoke_mean ≤ {knife / PROJECTION_MULTIPLIER:.4f} AND smoke_max ≤ {knife:.4f}."
                " Both, because the charge is the maximum of the two arms"
            ),
            "against_the_nearest_measured_shape": (
                "v5b's leg A ran 45.016 s a thread with a maximum of 108.362 on @VARUS_channel:10613"
                " — which IS F1 and IS the first unit of the smoke. On those numbers the max arm"
                " alone would STOP. A pass-2 reply is smaller than a reader's, and how much smaller"
                " is exactly what the smoke is bought to find out"
            ),
            "a_STOP_is_a_registered_outcome": (
                "not a failure and not a kill: the five replies are scored, the rate is measured,"
                " and the remainder becomes the operator's decision with a number in front of it"
            ),
        },
        "cumulative": {
            "hard_stop_seconds": HARD_STOP_SECONDS,
            "hard_stop_hours": round(HARD_STOP_SECONDS / 3600, 4),
            "hard_stop_usd_at_the_price_ceiling": round(
                HARD_STOP_SECONDS / 3600 * PRICE_CEILING_USD_PER_HOUR, 4
            ),
            "hard_stop_rule": (
                f"cumulative billed ≤ {HARD_STOP_SECONDS:.0f} s ="
                f" ${HARD_STOP_SECONDS / 3600 * PRICE_CEILING_USD_PER_HOUR:.4f} at the"
                f" ${PRICE_CEILING_USD_PER_HOUR}/h ceiling. It sits UNDER the ${CAP_USD:.2f} cap it"
                " defends and it is the PLATFORM that enforces it, so it protects even a hung call"
                " no gate can see"
            ),
            "session_ceiling_seconds": round(CAP_USD / PRICE_CEILING_USD_PER_HOUR * 3600, 1),
            "session_ceiling_rule": (
                f"${CAP_USD:.2f} / ${PRICE_CEILING_USD_PER_HOUR}/h ="
                f" {CAP_USD / PRICE_CEILING_USD_PER_HOUR:.3f} h ="
                f" {CAP_USD / PRICE_CEILING_USD_PER_HOUR * 3600:.0f} s ≥ the hard stop"
            ),
            "backstop_tolerance_seconds": BACKSTOP_TOLERANCE_SECONDS,
            "backstop_tolerance_rule": (
                "how far the `--terminate-after` stamp actually handed to `pod create` may sit"
                " BEYOND the one the hard stop computes. Only overshoot is bounded — a window"
                " rounded DOWN shortens itself and is always safe. The gate READS it from here and"
                " a record without this field is a refusal, not a default"
            ),
            "projection_gate": {
                "every": f"{PROJECTION_EVERY_CALLS} calls",
                "every_calls": PROJECTION_EVERY_CALLS,
                "formula": (
                    "billed_by_closed_pods + elapsed_on_this_pod + the AUTHORISED leg's remaining"
                    " calls × its s/call + overhead_seconds. The leg is priced at its MEASURED rate"
                    " — the larger of its mean and its last call — as soon as it has a reply, and"
                    " at the registered rate before that"
                ),
                "overhead_seconds": OVERHEAD_SECONDS,
                "overhead_rule": (
                    "the SAME bucket the money block charges, and it has to be: rung 4 prices the"
                    " attempt with it on every poll. H6 asserts the two are one number"
                ),
                "authorised_rule": (
                    "«the authorised leg» is the smoke until the go is recorded and the whole leg"
                    " after it. `gate_pass2_signals.legs_of` is where that is one line of code"
                ),
            },
        },
        "recovery_arithmetic": {
            "re_creations_allowed": 1,
            "rule": (
                "ONE re-creation after a proven deletion, and ONLY for a death BEFORE the smoke's"
                " first reply — rungs 1, 2 and 3. After the first reply a KILL closes the session:"
                " the smoke replies on the Mac are the evidence and the remainder is a new"
                " registration"
            ),
            "widest_dead_pod_that_still_fits_seconds": HARD_STOP_SECONDS - total,
            "widest_dead_pod_rule": (
                f"{HARD_STOP_SECONDS:.0f} − {total:.0f} = {HARD_STOP_SECONDS - total:.0f} s — the"
                " widest dead pod that still leaves the SMOKE's whole worst case inside the stop."
                " Computed by `pre_create` on every create and never typed into a command"
            ),
            "and_the_full_run_after_a_dead_pod": (
                f"charged_full ≤ ({HARD_STOP_SECONDS:.0f} − {OVERHEAD_SECONDS:.0f} −"
                f" {pre_generation:.0f} − smoke_seconds − dead_pod_seconds) / {remaining}. A dead"
                " pod does not close the run, it narrows the go/no-go — and rung S′ computes it"
                " live on `cumulative_billed_seconds`, which is what makes the narrowing automatic"
            ),
            "at_the_registered_arm": (
                f"at the {SMOKE_SECONDS_PER_CALL:.0f} s/call arm the full run does not fit even"
                f" with no dead pod ({people['units']:.0f} ×"
                f" {SMOKE_SECONDS_PER_CALL:.0f} + {pre_generation:.0f} + {OVERHEAD_SECONDS:.0f} ="
                f" {people['units'] * SMOKE_SECONDS_PER_CALL + pre_generation + OVERHEAD_SECONDS:.0f}"
                f" s > {HARD_STOP_SECONDS:.0f}). The inequality above is the honest form of «widest"
                " dead pod»: it is a function of a rate this record does not have"
            ),
        },
    }


def money(people: dict) -> dict:
    sums = arithmetic(people)
    return {
        "cap_usd_all_in": CAP_USD,
        "cap_rule": (
            f"${CAP_USD:.2f}, the ADR's table (д) for the second of the two contracts. The step"
            f" ledger is `results/spend_{PHASE.replace('-', '_')}.json` with a FRESH anchor: the"
            " window's two steps are closed against their own ledgers"
        ),
        "arithmetic": sums,
        "guard": {
            "step": PHASE,
            "step_cap_usd": CAP_USD,
            "rule": (
                f"`scripts/runpod_guard.py --step {PHASE} --step-cap {CAP_USD:.2f}`, anchored"
                " BEFORE the first create. Every rung that names a guard reading acts on the"
                " guard's number and never on the gate's projection"
            ),
        },
        "meter": {
            "price_ceiling_usd_per_hour": PRICE_CEILING_USD_PER_HOUR,
            "price_rule": (
                f"rung 1 refuses a create above ${PRICE_CEILING_USD_PER_HOUR}/h. The 4090 24 GB"
                " this line has rented four times costs $0.74 and is taken on the first attempt"
            ),
            "rule": (
                "the gate's CLOCK is what the rungs act on: create-elapsed × the pod's own price."
                " The billing walk and the balance delta are read afterwards and reconciled in the"
                " report, and where they disagree the clock is the number quoted"
            ),
            "why": (
                "`pass1-window` closed with `pods $0.0000` on a pod that had billed 845 s, and"
                " `pass1-window r2`'s walk was UNAVAILABLE at 20:27Z and $0.1691 at 21:05Z — the"
                " endpoint LAGS. A rung that waited for it would be a rung that never fires"
            ),
        },
        "recovery": {
            "rule": (
                "ONE re-creation after a proven deletion, and only for a death before the smoke's"
                " first reply. `pre_create` computes both bounds on every create — reading + the"
                " SMOKE's worst case ≤ cap, and billed + the SMOKE's worst case ≤ the hard stop —"
                " and the stricter binds. What it authorises is the MEASUREMENT: the remaining"
                " units are authorised by rung S′ and by nothing else"
            ),
            "a_second_dead_pod_is_a_STOP": True,
            "after_the_first_reply": (
                "a KILL closes the session. The replies already on the Mac are the evidence and the"
                " remainder is a new registration, never a third pod"
            ),
        },
        "step_sum": {
            "this_step_cap_usd": CAP_USD,
            "the_signal_layer_so_far_usd": 0.742055,
            "the_signal_layer_rule": (
                "pass 1 over window 1 cost $0.742055 across two registrations — r1's pod"
                " $0.173694 and r2's $0.568361, both on the gate's clock. This step's cap is not"
                " added to that number until it is spent"
            ),
            "the_one_shot_reader_for_comparison_usd": 0.312592,
        },
    }


def instruments(held: dict) -> dict:
    def pin(name: str) -> dict:
        return {"path": name, "sha256": summary.sha256_of(REPO_ROOT / name)}

    return {
        "task": pass2.PASS2_TASK_V1,
        "prompt_sha256": {pass2.PASS2_TASK_V1: pass2.prompt_sha256(pass2.PASS2_TASK_V1)},
        "module": pin("src/market_pulse/pass2.py"),
        "parser": {
            **pin("src/market_pulse/prompts.py"),
            "entry_point": "market_pulse.pass2.parse_pass2",
            "rule": (
                "`prompts._reader_object` then `prompts._reader` — the exact pair"
                " `prompts.parse_reply` binds for a reader task — with the bought entity block"
                " placed into the payload between them, and four refusals of pass 2's own on top"
            ),
        },
        "scorer": {
            **pin("src/market_pulse/scorer.py"),
            "functions": [
                "reader_signal_found",
                "reader_entity_found",
                "reader_noise_count",
                "reader_comment_agreement",
            ],
            "rule": "the reader's own scorer, IMPORTED over pass 2's out-file and never forked",
        },
        "bar_scorer": pin("scripts/score_reader_probe_b.py"),
        "verdict_producer": pin("scripts/score_pass2_signals.py"),
        "pack_builder": pin("scripts/build_pass2_pack.py"),
        "gate": pin("scripts/gate_pass2_signals.py"),
        "runner": pin("scripts/pass2_pod_runner.py"),
        "shipped_runner": pin("scripts/reader_v5_pod_runner.py"),
        "producer": pin("scripts/write_pass2_prereg.py"),
        "gold": {**pin("results/reader_gold_w1_r2.json"), "rule": "the reader's r2 gold, unedited"},
        "pass_1_out_files": {
            summary.rel(RESULTS / name): summary.sha256_of(RESULTS / name)
            for name in ("pass1_window_v2.jsonl", "pass1_window_r2_v2.jsonl")
        },
        "census": pin("results/pass1_window_r2_census.json"),
        "population": {"record": summary.rel(PACK), "sha256": summary.sha256_of(PACK)},
        "serving": held["serving"],
        "reference": {
            **pin("docs/REFERENCE-signals-w1.md"),
            "rule": "the bar's text, the team lead's, never re-read against the machine's answer",
        },
    }


def h6(held: dict, people: dict, sums: dict, clock: list[dict]) -> dict:
    """Every number `docs/PROMPT-pass2-signals.md` prints, RE-DERIVED — the step-1 refusal gate."""
    census = json.loads(summary.read_text_or_refuse(CENSUS))["pass_2_filter"]
    items = held["legs"][0]["items"]
    smoke = held["smoke"]["units"]
    remaining = people["units"] - smoke
    pre_generation = SSH_SECONDS + STAGE_LAUNCH_SECONDS + LOAD_SECONDS
    smoke_generation = smoke * SMOKE_SECONDS_PER_CALL
    total = smoke_generation + pre_generation + OVERHEAD_SECONDS
    knife = (HARD_STOP_SECONDS - OVERHEAD_SECONDS - pre_generation - smoke_generation) / remaining
    v5b = sums["seconds_per_call"]["nearest_measured_shape"]
    smoke_rows = sum(len(one["comments"]) for one in items[:smoke])
    reader_pack = json.loads(summary.read_text_or_refuse(V5B_PACK))

    def row(name, formula, registered, derived, mode="equals"):
        agrees = (
            abs(float(derived) - float(registered)) <= 5e-4
            if mode == "equals"
            else (derived >= registered if mode == "at_least" else derived <= registered)
        )
        return {
            "name": name,
            "formula": formula,
            "mode": mode,
            "registered": registered,
            "re_derived": derived,
            "agrees": bool(agrees),
        }

    table = [
        row(
            "population_units",
            "threads with ≥1 filtered row, census_pass1_window.pass_2_filter over the union",
            79,
            len(items),
        ),
        row(
            "filtered_rows",
            "the same table's filtered_rows_total",
            281,
            census["filtered_rows_total"],
        ),
        row(
            "filtered_chars",
            "the same table's filtered_chars_total",
            32756,
            census["filtered_chars_total"],
        ),
        row(
            "threads_pass_2_would_not_call",
            "callable threads carrying no filtered row",
            48,
            census["threads_pass_2_would_not_call"],
        ),
        row(
            "widest_unit_rows",
            "max rows in a unit — the contract names @klopotenkofood:6040 at 26",
            26,
            max(len(one["comments"]) for one in items),
        ),
        row(
            "widest_unit_chars",
            "max filtered chars in a unit — the contract names @mandziak:3679 at 4 315",
            4315,
            max(sum(len(r["text"]) for r in one["comments"]) for one in items),
        ),
        row("smoke_units", "len(pack.smoke.ids), the reference's five F threads", 5, smoke),
        row("remaining_after_the_smoke", "79 − 5", 74, remaining),
        row(
            "smoke_generation_seconds",
            f"{smoke} × {SMOKE_SECONDS_PER_CALL:.0f} s/call",
            600.0,
            smoke_generation,
        ),
        row(
            "pre_generation_seconds",
            f"ssh {SSH_SECONDS:.0f} + stage/launch {STAGE_LAUNCH_SECONDS:.0f} + load"
            f" {LOAD_SECONDS:.0f}",
            1100.0,
            pre_generation,
        ),
        row("overhead_seconds", "the r2 bucket, carried", 1300.0, OVERHEAD_SECONDS),
        row(
            "overhead_is_one_number",
            "money.arithmetic.overhead_seconds == projection_gate.overhead_seconds",
            OVERHEAD_SECONDS,
            float(sums["cumulative"]["projection_gate"]["overhead_seconds"]),
        ),
        row("smoke_worst_seconds", "600 + 1 100 + 1 300", 3000.0, total),
        row(
            "smoke_worst_usd",
            f"{total:.0f} s at ${PRICE_CEILING_USD_PER_HOUR}/h",
            0.6667,
            round(total / 3600 * PRICE_CEILING_USD_PER_HOUR, 4),
        ),
        row(
            "hard_stop_usd",
            f"{HARD_STOP_SECONDS:.0f} s at ${PRICE_CEILING_USD_PER_HOUR}/h",
            1.4667,
            round(HARD_STOP_SECONDS / 3600 * PRICE_CEILING_USD_PER_HOUR, 4),
        ),
        row(
            "hard_stop_is_under_the_cap",
            "the platform-held stop must sit under the cap it defends",
            CAP_USD,
            round(HARD_STOP_SECONDS / 3600 * PRICE_CEILING_USD_PER_HOUR, 4),
            mode="at_most",
        ),
        row(
            "session_ceiling_seconds",
            f"${CAP_USD:.2f} / ${PRICE_CEILING_USD_PER_HOUR}/h in seconds",
            6750.0,
            round(CAP_USD / PRICE_CEILING_USD_PER_HOUR * 3600, 1),
        ),
        row(
            "session_ceiling_covers_the_hard_stop",
            "the cap must buy at least the seconds the stop allows",
            HARD_STOP_SECONDS,
            round(CAP_USD / PRICE_CEILING_USD_PER_HOUR * 3600, 1),
            mode="at_least",
        ),
        row(
            "rung_S_prime_knife_edge",
            f"({HARD_STOP_SECONDS:.0f} − {OVERHEAD_SECONDS:.0f} − {pre_generation:.0f} −"
            f" {smoke_generation:.0f}) / {remaining} — the contract prints 48.6",
            48.6,
            round(knife, 1),
        ),
        row(
            "rung_S_prime_knife_edge_exact",
            "the same division, unrounded — the arm at a ZERO go wait",
            48.6486,
            round(knife, 4),
        ),
        row(
            "rung_S_prime_knife_edge_at_the_full_go_wait",
            f"the other end of the band: the go wait is BILLED, so ({HARD_STOP_SECONDS:.0f} −"
            f" {OVERHEAD_SECONDS:.0f} − {pre_generation:.0f} − {smoke_generation:.0f} −"
            f" {GO_WAIT_SECONDS:.0f}) / {remaining}",
            40.5405,
            round(
                (
                    HARD_STOP_SECONDS
                    - OVERHEAD_SECONDS
                    - pre_generation
                    - smoke_generation
                    - GO_WAIT_SECONDS
                )
                / remaining,
                4,
            ),
        ),
        row(
            "what_a_GO_needs_of_the_mean",
            f"the knife edge / {PROJECTION_MULTIPLIER}",
            32.4324,
            round(knife / PROJECTION_MULTIPLIER, 4),
        ),
        row(
            "widest_dead_pod_seconds",
            f"{HARD_STOP_SECONDS:.0f} − the SMOKE's worst case",
            3600.0,
            HARD_STOP_SECONDS - total,
        ),
        row(
            "the_full_run_at_the_registered_rate_does_NOT_fit",
            f"{people['units']} × {SMOKE_SECONDS_PER_CALL:.0f} + {pre_generation:.0f} +"
            f" {OVERHEAD_SECONDS:.0f} against the {HARD_STOP_SECONDS:.0f} s stop",
            HARD_STOP_SECONDS,
            people["units"] * SMOKE_SECONDS_PER_CALL + pre_generation + OVERHEAD_SECONDS,
            mode="at_least",
        ),
        row(
            "go_wait_equals_the_liveness_period",
            "rung S's deadline is DERIVED from rung 5's, not chosen",
            LIVENESS_SECONDS,
            GO_WAIT_SECONDS,
        ),
        row(
            "v5b_leg_a_seconds_per_thread",
            "mean of `seconds.worker` over the 23 leg-A rows of results/reader_v5b_w1.jsonl",
            45.016,
            v5b["mean_seconds_per_thread"],
        ),
        row(
            "v5b_slowest_leg_a_thread_seconds",
            "max of the same — and the thread is F1, the smoke's first unit",
            108.362,
            v5b["max_seconds_per_thread"],
        ),
        row(
            "the_assumption_over_the_nearest_measured_mean",
            f"{SMOKE_SECONDS_PER_CALL:.0f} / the v5b leg-A mean",
            2.666,
            round(SMOKE_SECONDS_PER_CALL / v5b["mean_seconds_per_thread"], 3),
        ),
        row(
            "reader_output_ceiling_is_TOKENS",
            "results/reader_v5b_pack.json::serving.output_tokens — the contract says «4 000-char»",
            4000,
            int(reader_pack["serving"]["output_tokens"]),
        ),
        row(
            "pass_2_serving_carries_the_same_ceiling",
            "the pack's own serving.output_tokens",
            pass2.PASS2_MAX_OUTPUT_TOKENS,
            int(held["serving"]["output_tokens"]),
        ),
        row(
            "input_ceiling_chars",
            "prompts.PASS1_MAX_INPUT_CHARS, aliased by pass2.PASS2_MAX_INPUT_CHARS",
            12000,
            int(pass2.PASS2_MAX_INPUT_CHARS),
        ),
        row(
            "widest_request_fits_the_ceiling",
            "the pack's own length block — headroom is what is left of 12 000",
            0,
            int(held["length"]["headroom_chars"]),
            mode="at_least",
        ),
        row(
            "the_smoke_is_row_heavier_than_the_population",
            "rows per thread in the smoke against rows per thread in the population",
            people["filtered_rows"] / people["units"],
            round(smoke_rows / smoke, 4),
            mode="at_least",
        ),
        row(
            "smoke_rows_per_thread",
            "30 filtered rows over the five F threads",
            6.0,
            round(smoke_rows / smoke, 4),
        ),
        row(
            "population_rows_per_thread",
            "281 filtered rows over 79 threads",
            3.5570,
            round(people["filtered_rows"] / people["units"], 4),
        ),
        row(
            "signal_layer_cost_so_far_usd",
            "pass1-window $0.173694 + pass1-window-r2 $0.568361, both on the gate's clock",
            0.742055,
            round(0.173694 + 0.568361, 6),
        ),
        row(
            "kill_clock_rungs_carrying_a_deadline_by_key",
            "rungs 2, 3, 5, 6 and 8 carry a numeric `deadline_seconds`; 1, 4, 7 and 9 are not clocks"
            " and carry None (Dv669)",
            5,
            sum(1 for one in clock if one.get("deadline_seconds") is not None),
        ),
        row(
            "the_rungs_a_pure_function_parses_all_carry_the_key",
            "gate_pass2_signals.DEADLINE_RUNGS ⊆ the rungs carrying deadline_seconds — the four the"
            " inherited gate_zero / gate_boot / watch read out of a rule",
            4,
            sum(
                1
                for one in clock
                if int(one["rung"]) in (2, 3, 5, 8) and one.get("deadline_seconds") is not None
            ),
        ),
        row(
            "reader_schema_refusal_rate_MEASURED",
            "results/reader_v5b_w1.jsonl leg A: rows carrying a parse_error, over rows",
            0.1739,
            round(
                sum(
                    1
                    for one in rows(V5B_ROWS)
                    if str(one.get("leg")).casefold() == "a" and one.get("parse_error")
                )
                / sum(1 for one in rows(V5B_ROWS) if str(one.get("leg")).casefold() == "a"),
                4,
            ),
        ),
        row(
            "refusal_budget_on_the_GO_arm",
            f"ceil({REFUSALS_FRACTION} × {people['units']})",
            14,
            math.ceil(people["units"] * REFUSALS_FRACTION),
        ),
        row(
            "refusal_budget_on_the_STOP_arm",
            f"ceil({REFUSALS_FRACTION} × {people['smoke_units']}) — ceil, so the five units carry"
            " a budget of one and not of none",
            1,
            math.ceil(people["smoke_units"] * REFUSALS_FRACTION),
        ),
        row(
            "the_bars_prose_carries_the_number_it_enforces",
            "the percent printed in bars.completeness.rule, against the fraction that decides"
            " ([[two_values_for_one_input_get_quoted_kindly]])",
            REFUSALS_FRACTION,
            round(
                float(
                    bars(pack(), reachability(pack()))["completeness"]["rule"]
                    .split("≤ ")[1]
                    .split("%")[0]
                )
                / 100,
                4,
            ),
        ),
        row(
            "the_prompt_carries_the_two_clauses_the_reader_line_paid_for",
            "prompts.READER_ASPECT_V5 and prompts.READER_NOT_A_SIGNAL_V3, spliced not retyped",
            2,
            sum(
                1
                for clause in (prompts.READER_ASPECT_V5, prompts.READER_NOT_A_SIGNAL_V3)
                if clause in pass2.PASS2_THREAD_PROMPT
            ),
        ),
        row(
            "pass_1s_fraction_would_have_allowed_no_refusal_at_all",
            "int(0.01 × 79) — the number this record does NOT carry",
            0,
            int(people["units"] * 0.01),
        ),
    ]
    mismatches = [one["name"] for one in table if not one["agrees"]]
    return {
        "rule": (
            "every number the contract prints, re-derived from the file it comes out of. A mismatch"
            " REFUSES: this producer writes nothing and exits non-zero"
        ),
        "rows": table,
        "mismatches": mismatches,
        "reading": (
            "every registered number re-derives"
            if not mismatches
            else f"{len(mismatches)} numbers do not re-derive"
        ),
    }


def build() -> dict:
    held = pack()
    people = population(held)
    reach = reachability(held)
    clock = kill_clock(people)
    purse = money(people)
    return {
        "phase": PHASE,
        "contract": "docs/PROMPT-pass2-signals.md",
        "authority": {
            "rulings": "docs/STATUS.md «Открытые решения» п. 1 (г), (д), (ж)",
            "adr": "knowledge/decisions/v2-is-the-base-and-pass-2-is-not-a-one-shot-reader.md",
            "reference": "docs/REFERENCE-signals-w1.md — the bar's text, the team lead's",
            "what_pass_2_may_not_be": (
                "the closed one-shot reader. It does no per-comment attribution from a raw thread"
                " and its input is a FILTERED set that already carries a label. A design that"
                " started attributing from the raw thread IS the closed instrument and the ADR"
                " refuses it as surely as it permits this one"
            ),
        },
        "attempt": (
            "ONE attempt, ONE paid session. A KILL after the smoke's first reply closes it; a STOP"
            " at rung S′ closes it with the smoke scored. What follows either is a new"
            " registration, never a second pass at this one"
        ),
        "what_this_run_is": (
            "the assembly pass over the bought window: ONE call per THREAD over the comments pass 1"
            " labelled категория_личное / молочный_бренд / сеть_ритейлер, answered in the reader's"
            " schema and scored by the reader's own scorer against the reader's gold r2"
        ),
        "what_this_run_is_not": (
            "not a re-attribution — strict authority, and a reply that relabels is a parse refusal."
            " Not a bar on the fourteen — `per_comment` is pass 1's pass-through and a threshold"
            " over it would be their SIXTH look. Not a claim about entity resolution — bar 2 is"
            " v5b's, inherited, and its value is known before the pod. Not a full run unless rung"
            " S′ says so"
        ),
        "population": people,
        "reachability": reach,
        "bars": bars(held, reach),
        "kill_clock": clock,
        "kill_clock_order": [f"{one['rung']} — {one['name']}" for one in clock],
        "money": purse,
        "instruments": instruments(held),
        "run_record": {
            "record": f"results/{PHASE.replace('-', '_')}_run.json",
            "pod_log": f"results/{PHASE.replace('-', '_')}_pod.log",
            "launch_stamp": "pass2_signals_launched_at",
            "go_token": f"results/{PHASE.replace('-', '_')}_go.json",
            "rule": (
                "this attempt's OWN names for every file a rung reads or writes. `results/` holds"
                " three closed sessions' stamps and logs, and a rung that read one of them would be"
                " reading a dead pod's clock (Dv621/632)"
            ),
        },
        "frozen_when_the_pod_exists": [
            "results/prereg_pass2_signals.json",
            "results/pass2_pack.json",
            "src/market_pulse/pass2.py",
            "scripts/gate_pass2_signals.py",
            "scripts/pass2_pod_runner.py",
        ],
        "supersedes": {
            "nothing": (
                "this is the first registration of pass 2. It INHERITS the kill-clock shape of"
                " `docs/PROMPT-pass1-window-r2.md` and adds rungs S and S′; it repeals none of that"
                " contract's numbers, because none of them describes this population or this decode"
            ),
            "what_it_carries_and_why": {
                "ssh 500 s": "the same five-reading spread; nothing has narrowed it",
                "load 450 s": "the boot is not a constant and is charged at the maximum",
                "overhead 1 300 s": "the same tail this line has now measured twice",
                "backstop tolerance 60 s": "unmoved",
                "liveness 600 s": "unmoved, and rung S's go wait is derived FROM it",
            },
            "what_it_does_NOT_carry": {
                "6.14 s/call": (
                    "pass 1's rate, and it prices a ~50-token reply about ONE comment. Carrying it"
                    " would be the copied-block defect this line has already made once"
                    " ([[an_audit_of_pins_is_not_an_audit_of_thresholds]])"
                ),
                "8 600 s / $2.00": "r2's stop and cap, computed for 901 calls at that rate",
            },
        },
        "return_to_the_operator": {
            "whatever_happens": [
                "the per-flagship scorecard, citing the pass-1 label of every row it names",
                "the DROP table — the filtered rows pass 2 sent to noise, by thread and by label",
                "the subject_doubt rate by pass-1 label",
                "the v5b comparison row on the same gold and scorer",
                "the measured rate of a pass-2 call, which no record on this stack had before",
            ],
            "on_a_STOP": (
                "the measured rate and what it implies for the remaining 74, so the cap-and-rate"
                " decision is the operator's with a number in front of it"
            ),
            "the_fourteen": (
                "no reading over them is a bar, in this report or in its acceptance. The ADR's"
                " «What binds» point 2 binds the team lead as well as the executor"
            ),
        },
        "do_not": [
            "edit prompts.py, scorer.py, the reader gold, any pinned file, the pass-1 out-files or packs",
            "render a raw unfiltered comment in any request",
            "accept a relabelling, however named",
            "register a bar on the fourteen",
            "run the remaining 74 without rung S′'s recorded GO",
            "leave --watch",
            "open two billing endpoints at once, or a third pod",
        ],
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "rule": (
                "the constants are typed once at the top of this file with their derivations; every"
                " other number here is computed. H6 re-derives the ones that have a file behind them"
            ),
        },
        "h6": h6(held, people, purse["arithmetic"], clock),
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    record = build()
    check = record["h6"]
    if check["mismatches"]:
        for one in check["rows"]:
            if not one["agrees"]:
                print(
                    f"  H6 MISMATCH {one['name']}: registered {one['registered']} · re-derived"
                    f" {one['re_derived']} · {one['formula']}"
                )
        raise SystemExit(
            f"{len(check['mismatches'])} of {len(check['rows'])} H6 rows do not re-derive."
            " Nothing was written — this is the step-1 refusal gate."
        )
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    sums = record["money"]["arithmetic"]
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    print(f"  H6: {len(check['rows'])} rows, {check['reading']}")
    print(
        f"  smoke {record['population']['smoke_units']} × {SMOKE_SECONDS_PER_CALL:.0f} s ="
        f" {sums['smoke_generation_seconds']:.0f} s · worst {sums['total_seconds']:.0f} s ="
        f" ${sums['worst_case_usd_at_the_price_ceiling']:.4f}"
    )
    print(
        f"  rung S′ knife edge"
        f" {sums['the_full_run_is_priced_by_rung_S_prime']['knife_edge_seconds_per_call']} s/call ·"
        f" a GO needs mean ≤"
        f" {sums['the_full_run_is_priced_by_rung_S_prime']['knife_edge_seconds_per_call'] / PROJECTION_MULTIPLIER:.4f}"
        f" AND max ≤ {sums['the_full_run_is_priced_by_rung_S_prime']['knife_edge_seconds_per_call']}"
    )
    print(
        f"  hard stop {HARD_STOP_SECONDS:.0f} s ="
        f" ${sums['cumulative']['hard_stop_usd_at_the_price_ceiling']} of ${CAP_USD:.2f} ·"
        f" widest dead pod {sums['recovery_arithmetic']['widest_dead_pod_that_still_fits_seconds']:.0f} s"
    )
    two = record["bars"]["2_entity_cases"]["computed"]
    print(
        f"  bar 2 at $0: {two['cases_answered']} of {two['cases']} ·"
        f" unreachable {record['reachability']['unreachable_entity_cases']} ·"
        f" unreachable flagship signals {record['reachability']['unreachable_flagship_signals']}"
    )
    print(
        f"  {WINDOW_R2_REPORT} is the window this reads; prompts.py untouched at "
        f"{summary.sha256_of(REPO_ROOT / 'src' / 'market_pulse' / 'prompts.py')[:16]}…"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
