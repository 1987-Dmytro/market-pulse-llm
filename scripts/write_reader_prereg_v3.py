#!/usr/bin/env python3
"""`results/prereg_reader_probe_v3.json` — the A+B registration, frozen before any money.

**One registration and not two.** The reader sitting of 2026-08-16 (ruling 2) takes A — the parser's
CONTAINER tolerance, with the refuse-on-conflict clause — and B — a v3 prompt — TOGETHER, as a single
instrument. No ablation between them was bought, so nothing this record or the run that spends
against it may attribute a recovered reply to one of the two halves.

**What it registers**, and each one has its own block below:

* the INSTRUMENT — the v3 prompt's sha, and the parser's v3 behaviour STATED: exactly which three
  container repairs fire, under which names, and which refusals stand;
* the POPULATION — probe-b's same 23 threads, digest `ccef35fa…`, so the two runs are paired. Each
  thread's status under the NEW reader census cell is recorded BESIDE the digest and never inside
  it: a status field is a fact about the production gate, and folding it into the pin would move the
  pin and end the pairing this record exists for;
* the SERVING — unchanged from probe-b, card named in every projection;
* the MONEY — $0.35 all-in against the cycle-2 line, setup re-derived from probe-b's SETTLED ledger
  entry, go/no-go on the UNREAD remainder with the pessimistic projection binding;
* the BARS — the same five thresholds, with one fix written into bar 3.

**The rate this record projects with is a FLOOR and says so.** probe-b measured 31.6376 s a thread on
an RTX 4090 under the v2 prompt, whose `per_comment` carried a row only where a comment had
something to charge. v3 asks for a row for EVERY comment shown, so the same threads owe more output
and will bill more seconds. The projection is registered anyway, with the slowdown the cap can
absorb computed beside it — that number is what the warm-up measures and what the go/no-go stops on
([[a_price_is_as_representative_as_its_sample]]).

    PYTHONPATH=src python3 scripts/write_reader_prereg_v3.py
    PYTHONPATH=src python3 scripts/write_reader_prereg_v3.py --out /tmp/again.json   # the pair
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_census_w1_reader as reader_cell  # noqa: E402
import probe_b_population as subset  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_reader_prereg_v2 as v2writer  # noqa: E402

from market_pulse import local_llm, prompts, scorer  # noqa: E402

OUT = REPO_ROOT / "results" / "prereg_reader_probe_v3.json"
SUPERSEDES = REPO_ROOT / "results" / "prereg_reader_probe_v2.json"
GOLD_R2 = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
CENSUS_CELL = REPO_ROOT / "results" / "gate_census_w1_reader.json"
PROBE_B_EVIDENCE = REPO_ROOT / "results" / "reader_probe_b_w1.jsonl"
PROBE_B_LEDGER = REPO_ROOT / "results" / "spend_probe_b.json"
PROBE_B_RUN = REPO_ROOT / "results" / "reader_probe_b_run.json"
PLAN = REPO_ROOT / "docs" / "PLAN-comment-signals.md"
CONTRACT = REPO_ROOT / "docs" / "PROMPT-reader-v3-prep.md"
REFERENCE = REPO_ROOT / "docs" / "REFERENCE-signals-w1.md"

CAP_USD = 0.35
"""All-in, against the CYCLE-2 line of SPEC 3.23 (1) and no longer against a phase cap: Phase 4 is
CLOSED and 3.18 (7)(b) forbids a line opened afterwards from reaching back into it. The same $0.35
probe-b was bought under, because this is the same 23 threads read once more."""

AGREEMENT_BAR = v2writer.AGREEMENT_BAR
"""The operator's ≥0.80, imported from the registration that carries it rather than retyped: a
threshold written twice is a threshold that can disagree with itself."""

POPULATION_DIGEST = "ccef35fa4b9c771fd62506cd7878177f8184c8344702ad1d05c3bec33abbc1f3"
"""probe-b's population, pinned as a literal BEFORE it is computed.

The pairing this whole registration rests on is «the same 23 threads with the same payable comments,
read twice». A digest recomputed and stored would agree with whatever the enumeration happened to
be; a literal that must MATCH it is the only version of the claim that can fail."""


def parser_behaviour() -> dict:
    """The v3 parser STATED — the three repairs by the names the code emits, and what still refuses.

    Derived from the module's own constants and not retyped: the repair names are what land in a
    verdict's `repairs` list and what a scorer will group by, so a rename in `prompts` has to redden
    this registration rather than quietly change what it registered.
    """
    fields = prompts.READER_LIST_FIELDS
    return {
        "module": "src/market_pulse/prompts.py",
        "function": "parse_reply",
        "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
        "scope": (
            "the READER task family (prompts.READER), all three registered texts. The ruling is"
            " about how the reader's answer is READ, not about which text asked for it. POSITIONS"
            " and the caption parser are untouched"
        ),
        "logs_on_every_verdict": "repairs",
        "repairs": {
            "1_two_top_level_objects": {
                "shape": (
                    "an answer split into two top-level JSON objects — {thread, post_summary,"
                    " discussion_summary} then {entities, signals, per_comment, noise}. 2 of"
                    " probe-b's 23 replies"
                ),
                "logs": prompts.TWO_OBJECTS_MERGED,
                "refuses_when": (
                    "a key is present in BOTH with different values — «two disagreeing objects»,"
                    " the operator's word. NEVER last-wins: two objects that disagree are two"
                    " answers, and choosing one would be the parser deciding what the model meant."
                    " The reason string is `two disagreeing objects: <key>`"
                ),
            },
            "2_empty_object_for_an_empty_list": {
                "shape": "`{}` where the schema asks for a list. 5 of probe-b's 23 replies",
                "logs": [f"{field}: empty object -> empty list" for field in fields],
            },
            "3_map_keyed_by_msg_id": {
                "shape": (
                    'a map keyed by msg_id where a list belongs — `noise: {"47896": {…}}`. 1 of'
                    " probe-b's 23 replies"
                ),
                "logs": [f"{field}: map keyed by msg_id -> list" for field in fields],
                "narrower_than_the_coercion_script": (
                    "the keys are DROPPED, because every row already carries its own msg_id;"
                    " scripts/probe_b_coercion.py folded the key into `entities` as a `name`, which"
                    " is supplying a field the model did not write. A map keyed by anything but a"
                    " msg_id is not repaired — that is `entities`' Dv393 shape, which the v2 schema"
                    " line closed at the source and which no probe-b reply returned"
                ),
            },
        },
        "repairable_fields": list(fields),
        "refuses": {
            "signals.aspect is not a string": (
                "`aspect: null` on a signal — a DOMAIN and not a container. Repairing it would mean"
                " inventing an aspect or dropping a signal the schema cannot carry."
                " probe_b_coercion.repairs() dropped it as its FOURTH repair and this registration"
                " deliberately does not carry that over"
            ),
            "missing field: evidence": (
                "a `from_post` signal with no `evidence` key. An evidence list is what a finding is"
                " made of, and supplying one would be writing the answer"
            ),
            "no JSON object in reply": (
                "a bare un-braced fragment — probe-b's seventh shape. Where an answer began is a"
                " guess, and a guess about that is a guess about the whole verdict"
            ),
        },
        "measured_on_probe_bs_own_replies": {
            "as_run_under_v2": 13,
            "under_v3": 19,
            "of": 23,
            "reading": (
                "the same count results/reader_probe_b_coerced.json reached with a WIDER repair"
                " list, by a different instrument — not the same measurement, and this record does"
                " not claim an agreement it did not buy. The four that still refuse are two"
                " `missing field: evidence`, one `signals.aspect is not a string`, and"
                " @VARUS_channel:10360, whose reply closes its object early and continues with bare"
                ' `"entities": [...]` pairs; its array elements read as many top-level objects'
                " disagreeing on `name`, so the refuse-on-conflict clause catches the seventh shape"
                " too. Reported, and gating nothing: probe-b's registered verdict is"
                " results/reader_probe_b_verdict.json and nothing here moves it"
            ),
        },
    }


def bar_three_over_answers(noise_signals: dict[str, int], answered: set[str]) -> dict:
    """Bar 3 under the predicate this registration fixes — the reference implementation.

    probe-b finding 2: «a bar that counts things is a bar an unreadable reply passes». Four of bar
    3's five threads returned no verdict at all, so the bar's «0 signals» was a count over ONE actual
    answer and it was the only gate that cleared. The predicate is therefore stated with its
    denominator and with a reachability state, not as a threshold alone
    ([[an_absolute_bar_needs_a_reachability_state]]):

    * the bar is counted over the registered noise threads that have a PARSED verdict;
    * a refused reply contributes nothing — never a zero;
    * with no parsed verdict among them the bar is UNREACHABLE, which is not a pass.

    Written here so the bar has a producer a human can open, and named in the record so the run
    contract's scorer reproduces it rather than inventing a second reading
    ([[a_registered_bar_may_have_no_producer]]).
    """
    counted = {name: signals for name, signals in noise_signals.items() if name in answered}
    refused = sorted(name for name in noise_signals if name not in answered)
    return {
        "threads_registered": len(noise_signals),
        "threads_with_a_verdict": len(counted),
        "threads_refused": refused,
        "signals": sum(counted.values()),
        "per_thread": counted,
        "reachable": bool(counted),
        "passed": bool(counted) and sum(counted.values()) == 0,
    }


def probe_b_setup_usd(rate: float, worker_seconds: float) -> tuple[float, str]:
    """What probe-b billed that was not thread-reading — read from the guard's own closing entry.

    The staging pod, the endpoint's boot, the weight load and the idle tail, measured rather than
    budgeted, and taken from the SETTLED figure rather than from a report: probe-a closed at $0.0750
    and the same step settled at $0.0944 the next day, which is 2.8% of this cap in the direction
    that opens runs ([[unreadable_now_versus_never]]).
    """
    ledger = json.loads(summary.read_text_or_refuse(PROBE_B_LEDGER))
    closing = [one for one in ledger["gpu_sessions"] if one.get("closed")][-1]
    settled = closing["settled_usd"]
    return settled - worker_seconds * rate, (
        f"probe-b's SETTLED step ledger (${settled:.6f}, its own resources per SPEC 3.23 (4) — the"
        f" standing network volume is on its own line and is NOT in it) minus its reading"
        f" ({worker_seconds:.3f} billed worker seconds at the rate below). Read from"
        f" {summary.rel(PROBE_B_LEDGER)}, the file scripts/runpod_guard.py wrote, and never from a"
        " sentence in a report"
    )


def probe_b_pass() -> dict:
    """probe-b's 23-thread pass, re-summed from the rows it wrote."""
    rows = [
        json.loads(line)
        for line in PROBE_B_EVIDENCE.read_text(encoding="utf-8").splitlines()
        if line
    ]
    worker = sum(row["seconds"]["worker"] for row in rows)
    payable = sum(row["payable_comments"] for row in rows)
    return {"threads": len(rows), "payable": payable, "worker_seconds": round(worker, 3)}


def money() -> dict:
    run = json.loads(summary.read_text_or_refuse(PROBE_B_RUN))
    rate = run["go_no_go"]["rate_usd_per_second"]
    pass_b = probe_b_pass()
    setup, setup_rule = probe_b_setup_usd(rate, pass_b["worker_seconds"])
    seconds_the_cap_buys = (CAP_USD - setup) / rate
    projected = pass_b["worker_seconds"] * rate
    return {
        "cap_usd_all_in": CAP_USD,
        "line": (
            "the CYCLE-2 line of SPEC amendment 3.23 (1), $20.00, anchored 2026-08-16T12:14:48Z at"
            " $22.5097614388 in results/spend_cycle2.json. Phase 4 is CLOSED and 3.18 (7)(b) keeps"
            " it that way: a line opened after a phase closed cannot reach back into what the phase"
            " bought, and this contract's spend cannot be charged to it either"
        ),
        "guard": (
            "scripts/runpod_guard.py --step reader-v3 --step-cap 0.35, read from the guard and never"
            " from a ledger line or from a sentence in the contract (Dv33, Dv378)"
        ),
        "includes": (
            "the staging pod, the endpoint's boot, the warm-up, the run and every second the"
            " endpoint bills while it exists"
        ),
        "arithmetic": {
            "rate_usd_per_second": rate,
            "setup_usd": round(setup, 4),
            "setup_rule": setup_rule,
            "seconds_the_cap_buys_after_setup": round(seconds_the_cap_buys, 1),
            "at_probe_bs_measured_4090_rate": {
                "sample": (
                    f"{pass_b['threads']} threads and {pass_b['payable']} payable comments in one"
                    f" pass, {pass_b['worker_seconds']} billed worker seconds on an"
                    f" {run['worker']['runtime']['gpu']} (endpoint {run['endpoint']})"
                ),
                "seconds_per_thread": round(pass_b["worker_seconds"] / pass_b["threads"], 4),
                "seconds_per_payable_comment": round(
                    pass_b["worker_seconds"] / pass_b["payable"], 4
                ),
                "reading_seconds": pass_b["worker_seconds"],
                "reading_usd": round(projected, 4),
                "all_in_usd": round(setup + projected, 4),
                "headroom_usd": round(CAP_USD - setup - projected, 4),
                "verdict": "fits the cap"
                if setup + projected < CAP_USD
                else "does not fit the cap",
            },
            "max_slowdown_vs_probe_b": round(seconds_the_cap_buys / pass_b["worker_seconds"], 3),
            "slowdown_rule": (
                "this projection is a FLOOR and not a forecast. probe-b's seconds were measured"
                " under the v2 prompt, whose `per_comment` carried a row only where a comment had"
                " something to charge; v3 asks for a row for EVERY comment shown, so the same 23"
                " threads owe more output tokens and will bill more seconds. The number above is how"
                " much slower than probe-b this run may be and still fit: over it, the go/no-go says"
                " STOP. What a rate measured on a different output shape is good for is a bound"
            ),
            "what_a_stop_costs": (
                f"the setup and the warm-up's three threads — ${setup:.4f} plus what three threads"
                " bill on the card that turns up; probe-b's 4090 billed 62.276 s for exactly that"
                " draw"
            ),
        },
    }


def population_block() -> dict:
    kept = subset.population()
    digest = subset.digest(kept)
    if digest != POPULATION_DIGEST:
        raise SystemExit(
            f"the population digest is {digest} and this registration is paired to"
            f" {POPULATION_DIGEST}. probe-b's 23 threads or their payable comments have moved —"
            " stop and report, because the comparison this record exists for is gone."
        )
    in_the_new_cell = {
        f"{one['channel']}:{one['post_id']}": [row["msg_id"] for row in one["comments"]]
        for one in reader_cell.population()
    }
    threads = []
    for one in kept:
        name = subset.key(one["channel"], one["post_id"])
        threads.append(
            {
                "thread": name,
                "cases": one["cases"],
                "payable_comments": len(one["comments"]),
                "msg_ids": [row["msg_id"] for row in one["comments"]],
                "injected_under_probe_b": one["injected"],
                "in_the_reader_census_cell": name in in_the_new_cell,
                "payable_list_unchanged_by_the_cell": in_the_new_cell.get(name)
                == [row["msg_id"] for row in one["comments"]],
                "rendering_sha256": v2writer.rendering_sha256(one, prompts.READER_TASK_V3),
                "rendered_chars": len(v2writer.rendering(one, prompts.READER_TASK_V3)),
            }
        )
    entering = [one["thread"] for one in threads if one["injected_under_probe_b"]]
    return {
        "class": (
            "probe-b's registered subset, unchanged — the SAME 23 threads with the SAME payable"
            " comments, so the two runs are paired on data and on population and the only thing"
            " that moved is the instrument"
        ),
        "record": "scripts/probe_b_population.py",
        "threads": len(threads),
        "payable_comments": sum(one["payable_comments"] for one in threads),
        "injected_threads": sum(1 for one in threads if one["injected_under_probe_b"]),
        "enumeration": {
            "digest": digest,
            "digest_rule": (
                "sha256 over `channel:post_id\\tgated|injected\\tpayable msg_ids` for every thread,"
                " in the enumeration's order — probe-b's own rule, byte for byte, and the flags in"
                " it are probe-b's. The reader census cell's status is recorded per thread BELOW and"
                " is NOT in the digest: folding it in would move the pin and end the pairing"
            ),
            "paired_to": POPULATION_DIGEST,
            "threads": threads,
        },
        "under_the_reader_census_cell": {
            "record": summary.rel(CENSUS_CELL),
            "sha256": summary.sha256_of(CENSUS_CELL),
            "cell": reader_cell.CELL,
            "in_the_cell": sum(1 for one in threads if one["in_the_reader_census_cell"]),
            "outside_the_cell": [
                one["thread"] for one in threads if not one["in_the_reader_census_cell"]
            ],
            "injected_under_probe_b_that_now_enter": entering,
            "measured": (
                "ENUMERATED and not estimated (Dv399). All FOUR threads probe-b had to inject —"
                " E1 @matusi_ukr:22242, E4a @mandziak:3684, E4b @mandziak:3689 and N3"
                " @sashafitnesslife:3939 — enter the reader cell, because `varto_rule` is the"
                " silencer that removed every one of them and ruling 3 lifts it for this path. The"
                " contract's expectation that N3 «likely stays injectable» is WRONG, measured: its"
                " post carries the lexicon hit and plus_spam only silences its comments. So under"
                " the reader's own gate this population has ZERO injected threads and all 23 are"
                " production-reachable"
            ),
            "payable_lists_unchanged": all(
                one["payable_list_unchanged_by_the_cell"] for one in threads
            ),
            "why_the_lists_cannot_move": (
                "`varto_rule` is a matcher rule and gates a THREAD; the two per-comment silencers"
                " plus_spam and scam are the only ones `gate_census_w1.silenced_comment` implements"
                " and both stay ON. So lifting varto changes which threads are in and never which"
                " comments inside them are payable — checked per thread above rather than argued"
            ),
        },
    }


def bars(gold: dict) -> dict:
    noise = [one["id"] for one in gold["noise_threads"]]
    per_comment = [one["msg_id"] for one in gold["per_comment"]]
    return {
        "1_flagships": {
            "threshold": "5 of 5 cases",
            "scorer": "reader_signal_found",
            "rule": (
                "each of the reference's five flagship CASES is found when every gold signal it"
                " carries is found. Unchanged from v1 and v2 — the threshold is the operator's word"
                " and this contract does not move it"
            ),
            "scored_over": [one["id"] for one in gold["flagships"]],
            "gold_signals": [
                signal["id"] for case in gold["flagships"] for signal in case["signals"]
            ],
        },
        "2_entity_cases": {
            "threshold": "4 of 4 cases",
            "scorer": "reader_entity_found",
            "scored_over": [one["id"] for one in gold["entity_cases"]],
            "rule": (
                "an entity case is answered when the verdict for its thread carries an entity whose"
                " name resolves to the case's brand and whose subject_type is the ruled one."
                " Unchanged"
            ),
        },
        "3_noise": {
            "threshold": "0 signals",
            "scorer": "reader_noise_count",
            "scored_over": noise,
            "rule": (
                "zero signals in the verdicts of the reference's noise threads — counted over the"
                " threads that HAVE a parsed verdict. A refused reply contributes nothing and is"
                " NEVER a zero; with no parsed verdict among them the bar is UNREACHABLE, which is"
                " not a pass"
            ),
            "fixed_because": (
                "probe-b finding 2. As registered, this bar's «0 signals» was the only gate that"
                " cleared and it was computed over ONE actual answer: four of its five threads"
                " returned `signals: {}` and were refused, and a refused reply has no signals to"
                " count. Any bar whose predicate is «zero of X» has to be scored over answers that"
                " exist, and the registration is where that belongs — not in a post-run analysis"
            ),
            "producer": (
                "scripts/write_reader_prereg_v3.py::bar_three_over_answers — the reference"
                " implementation, exercised by tests/test_reader_prereg_v3.py on probe-b's own"
                " rows. The run contract's scorer reproduces this predicate and may not invent a"
                " second reading of it"
            ),
            "result_must_carry": [
                "threads_registered",
                "threads_with_a_verdict",
                "threads_refused",
                "signals",
                "reachable",
                "passed",
            ],
        },
        "4_per_comment_agreement": {
            "threshold": f"rate >= {AGREEMENT_BAR}",
            "scorer": "reader_comment_agreement",
            "gold": {
                "record": summary.rel(GOLD_R2),
                "sha256": summary.sha256_of(GOLD_R2),
                "why_r2": (
                    "the sitting's ruling 4 adjudicates «категория» and «категория_личное» as ONE"
                    " class, and r2 is that ruling applied to the twelve gold cells that read the"
                    " first. Scoring against r2 is what makes the collapsed reading the BAR rather"
                    " than a number reported beside it, which is what probe-b had to do"
                ),
            },
            "scored_over": per_comment,
            "rule": (
                "each gold row is compared on the fields the reference STATES for it"
                " (`scored_fields`) and on no others. Unchanged from v1 and v2 except for which"
                " gold it reads"
            ),
            "arithmetic": (
                f"{len(per_comment)} rows: 11 of 14 is"
                f" {11 / len(per_comment):.3f} and fails, 12 of 14 is {12 / len(per_comment):.3f}"
                " and passes"
            ),
        },
        "5_time_and_cost": {
            "thresholds": {"cap_usd_all_in": CAP_USD},
            "rule": (
                "the warm-up measures billed worker seconds per thread; the UNREAD remainder is"
                " projected from it and added to the warm-up's own seconds and the measured setup."
                " Over the cap, STOP before any further call"
            ),
            "reported_not_gating": {
                "finish_reason": (
                    "per thread, and it is the field that says whether the longer v3 output hit the"
                    " 2 000-token ceiling. probe-b returned `length` on ZERO of 23 under v2; this is"
                    " the run that can find out whether a row-per-comment changes that"
                ),
                "seconds_vs_probe_b": (
                    "per thread, so the slowdown the longer output really costs is measured rather"
                    " than assumed. It is also what re-prices the 129-thread window cell"
                ),
            },
        },
    }


def build() -> dict:
    gold = json.loads(summary.read_text_or_refuse(GOLD_R2))
    older = json.loads(summary.read_text_or_refuse(SUPERSEDES))
    return {
        "phase": "reader-v3",
        "contract": "docs/PROMPT-reader-v3-prep.md D5",
        "class": (
            "PRE-REGISTRATION. Committed before the endpoint exists; git history is the only witness"
            " that it preceded the money. It FREEZES when written and the run contract"
            " (`reader-v3-run`) may not edit it — a registration a run may amend is a registration"
            " the run wrote"
        ),
        "attempt": (
            "ONE attempt, no retry. A failed bar after a completed run closes the question by rule:"
            " what follows is a new registration after a design sitting, never a second pass at the"
            " same one"
        ),
        "supersedes": {
            "record": summary.rel(SUPERSEDES),
            "sha256": summary.sha256_of(SUPERSEDES),
            "ruling": (
                "the reader sitting, operator 2026-08-16, ruling 2: the instrument is A+B as ONE new"
                " registration (v3)"
            ),
            "what_it_changes": [
                "the parser is tolerant to the CONTAINER and refuses two disagreeing objects (A)",
                "the prompt is reader_thread_gm4_v3, v2 plus six measured changes (B)",
                "bar 4 is scored against gold r2, so the vocabulary collapse is the bar and not a"
                " reading beside it",
                "bar 3 is counted over threads with a parsed verdict",
            ],
            "what_it_keeps": (
                "the population digest, the five thresholds, the serving configuration, the $0.35"
                " cap and the scorer's bytes. Everything that could make the two runs incomparable"
                " is held still on purpose"
            ),
            "no_ablation": (
                "A and B move the same instrument and no ablation between them was bought. A reply"
                " that parses under v3 and refused under v2 may NOT be attributed to the parser or"
                " to the prompt — the sitting took them together and this record says so where a"
                " reader of the result will find it"
            ),
        },
        "authority": {
            summary.rel(path): summary.sha256_of(path)
            for path in (PLAN, CONTRACT, REFERENCE, SUPERSEDES, GOLD_R2, CENSUS_CELL)
        },
        "instruments": {
            "task": prompts.READER_TASK_V3,
            "prompt_sha256": {task: prompts.prompt_sha256(task) for task in sorted(prompts.READER)},
            "prompt_rule": (
                "a sha per reader text registered at the moment this record was written — three of"
                " them. A text registered LATER is not in this map and is not expected to be; the"
                " driver compares each of THESE against the worker, and separately compares the"
                " worker's whole map against the checkout, which is the check that sees a volume a"
                " session behind. probe-b's registration learned that distinction the hard way"
            ),
            "v3_changes": {
                "A_parser": (
                    "container tolerance by ruling: three repairs, domains strict, two disagreeing"
                    " objects REFUSED. Stated field by field under `parser` below"
                ),
                "B_prompt": (
                    "six `_swap` calls from v2 — «answer with ONE JSON object», «[] when there is"
                    " nothing», a per_comment row for EVERY comment, several signals per thread, the"
                    " channel's own reply as evidence, praise of taste as a signal"
                ),
                "derivation": (
                    "v3 is derived from v2 by six `_swap` calls in src/market_pulse/prompts.py, so"
                    " «six wording changes» is a property of the file and a seventh would have to"
                    " appear there as a seventh call"
                ),
            },
            "parser": parser_behaviour(),
            "scorer": {
                "module": "src/market_pulse/scorer.py",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
                "functions": sorted(
                    name
                    for name in dir(scorer)
                    if name.startswith("reader_") and callable(getattr(scorer, name))
                ),
                "unchanged": (
                    "byte for byte what v1 and v2 registered. Bar 3's fixed predicate is a"
                    " DENOMINATOR and a reachability state, not a new count: `reader_noise_count`"
                    " already returns `per_thread`, and what the fix adds is which threads may be in"
                    " it. Moving the scorer would have taken four sealed records with it for a"
                    " change the run contract's own driver can carry"
                ),
            },
            "gold": {
                "record": summary.rel(GOLD_R2),
                "sha256": summary.sha256_of(GOLD_R2),
                "revision": gold["revision"]["name"],
                "supersedes": gold["revision"]["supersedes"]["record"],
            },
            "ceilings": {
                "input_chars": prompts.READER_MAX_INPUT_CHARS,
                "output_tokens": local_llm.READER_MAX_NEW_TOKENS,
                "input_rule": (
                    "a LOUD refusal, never a truncation. The largest thread of THIS population"
                    f" renders to {max(len(v2writer.rendering(one, prompts.READER_TASK_V3)) for one in subset.population())}"
                    " characters under v3"
                ),
                "output_risk": (
                    "v3 asks for a `per_comment` row for EVERY comment shown, so output length now"
                    " scales with a thread's payable count. This population's largest thread carries"
                    " 15 payable comments and probe-b returned `finish_reason: length` on ZERO of"
                    " 23 under v2, so the ceiling is not expected to fire here — but the 129-thread"
                    " reader cell's largest carries 125, and results/gate_census_w1_reader.json"
                    " reports that as a WINDOW risk. `finish_reason` is reported per thread by bar 5"
                    " so this run is what answers it"
                ),
            },
            "serving": older["instruments"]["serving"],
            "serving_rule": (
                "unchanged from probe-b, quoted from its registration rather than retyped: READER"
                " config, base-no-adapter, forward batch 1, greedy, ADA_24 requested fastest-first"
                " and never asserted. The card that turns up is NAMED in every projection this"
                " record makes and in every one the run reports"
            ),
        },
        "population": population_block(),
        "money": money(),
        "go_no_go": {
            "pattern": "measure a warm-up, project the UNREAD remainder, and stop before the rest",
            "projection_rule": (
                "the UNREAD remainder is what is projected, and the warm-up's own billed seconds"
                " plus the measured setup are added to it. Projecting the whole population and"
                " comparing it against what the cap has left after the warm-up counts those threads"
                " twice — probe-b's corrected arithmetic, kept"
            ),
            "stop_rule": (
                "if setup + warm-up + the binding projection of the remainder exceeds the cap, STOP"
                " before any further call. The attempt stays intact, the measured seconds per thread"
                " and the card they were measured on go back to the operator, and no bar is scored"
                " on a partial run"
            ),
            "binding": (
                "the pessimistic of the per-thread and per-payable-comment projections. Both are"
                " computed and the larger one decides"
            ),
            "warm_up": {
                "threads": list(subset.WARM_UP),
                "rule": (
                    "probe-a's registered draw, re-read a third time — the same three threads, so"
                    " all three instruments are compared on one sample and the seconds are"
                    " comparable card for card"
                ),
                "what_it_measures_here": (
                    "not just the card. v3's output is longer than v2's by construction, and these"
                    " three threads under v3 against the same three under probe-b's 4090 is the"
                    " first measurement of what that costs"
                ),
            },
        },
        "bars": bars(gold),
        "frozen_when_the_endpoint_exists": [
            "results/prereg_reader_probe_v3.json",
            summary.rel(GOLD_R2),
            summary.rel(CENSUS_CELL),
            f"the {prompts.READER_TASK_V3} prompt text",
            "scripts/probe_b_population.py's enumeration",
        ],
        "non_gating": [
            "`repairs` per verdict — which of the three container repairs fired, and how often. It"
            " is the measurement A was bought for and it gates nothing",
            "`finish_reason` per thread — the 2 000-token ceiling against v3's longer output",
            "seconds per thread against probe-b's 31.6376, which is what re-prices the window cell",
            "the four threads probe-b had to inject are inside the reader census cell now, so this"
            " population is production-reachable end to end. That is a fact about the gate and it"
            " changes no bar here",
            "no ablation between A and B was bought — see `supersedes.no_ablation`",
        ],
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "borrowed": {
                name: summary.sha256_of(REPO_ROOT / name)
                for name in (
                    "scripts/gate_census_w1_reader.py",
                    "scripts/probe_b_population.py",
                    "scripts/reader_population.py",
                    "scripts/window_summary_5c2.py",
                    "scripts/write_reader_prereg_v2.py",
                    "src/market_pulse/local_llm.py",
                    "src/market_pulse/prompts.py",
                    "src/market_pulse/scorer.py",
                )
            },
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    record = build()
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    pop = record["population"]
    print(
        f"  population {pop['threads']} threads · {pop['payable_comments']} payable ·"
        f" digest {pop['enumeration']['digest'][:16]}…"
        f" (paired {pop['enumeration']['digest'] == POPULATION_DIGEST})"
    )
    cell = pop["under_the_reader_census_cell"]
    print(
        f"  under {cell['cell']}: {cell['in_the_cell']}/{pop['threads']} in the cell ·"
        f" {len(cell['injected_under_probe_b_that_now_enter'])} of probe-b's injected now enter"
    )
    sums = record["money"]["arithmetic"]
    at = sums["at_probe_bs_measured_4090_rate"]
    print(
        f"  cap ${CAP_USD:.2f} · setup ${sums['setup_usd']:.4f} · reading ${at['reading_usd']:.4f}"
        f" -> all-in ${at['all_in_usd']:.4f} ({at['verdict']}, headroom ${at['headroom_usd']:.4f})"
    )
    print(f"  the cap absorbs a {sums['max_slowdown_vs_probe_b']}x slowdown against probe-b")
    for name, bar in record["bars"].items():
        print(f"  bar {name:26s} {bar.get('threshold') or bar['thresholds']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
