#!/usr/bin/env python3
"""`results/prereg_reader_probe_v2.json` — probe-b's registration, written before it can run.

**What it supersedes and what it keeps.** `results/prereg_reader_probe.json` registered the reader
over the whole census cell and its go/no-go stopped the run at 54.8 s a thread. This record changes
three things and nothing else: the INSTRUMENT (`reader_thread_gm4_v2`, two measured defects closed),
the CARD (the fastest 24 GB class first, because the 5c2 rate that priced everything was measured on
an RTX 4090 and probe-a's endpoint drew an L4 at the same price), and the POPULATION (the threads
the reference's cases live in, four of them injected past the gate so bars 2 and 3 are reachable).
Every bar, every matching rule, every ceiling and the whole scorer are v1's.

**It is committed before the endpoint exists, and git is the only witness to that order.** No clock
is stamped, so the record re-derives byte for byte and its date is the date of its commit
([[provenance_cannot_name_itself]]).

**The arithmetic is in the record, not in the report.** probe-a proved the cap has to be divided by
a measured rate BEFORE a resource exists ([[the_setup_is_inside_the_cap]]). Done here: at the L4's
measured 54.806 s a thread this population is $0.42–$0.65 against a $0.35 cap, so the run is only
affordable if the faster card is faster by at least the break-even factor this file computes. That
is what the go/no-go buys, and it is the one number it is bought for.

    PYTHONPATH=src python3 scripts/write_reader_prereg_v2.py
    PYTHONPATH=src python3 scripts/write_reader_prereg_v2.py --out /tmp/again.json   # the pair
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import probe_b_population as subset  # noqa: E402
import reader_population as cell  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import local_llm, prompts  # noqa: E402

CONTRACT = REPO_ROOT / "docs" / "PROMPT-probe-b.md"
PLAN = REPO_ROOT / "docs" / "PLAN-comment-signals.md"
REFERENCE = REPO_ROOT / "docs" / "REFERENCE-signals-w1.md"
GOLD = REPO_ROOT / "results" / "reader_gold_w1.json"
SUPERSEDED = REPO_ROOT / "results" / "prereg_reader_probe.json"
PRICES = REPO_ROOT / "results" / "run_5c2_comments.json"
PROBE_A_RUN = REPO_ROOT / "results" / "reader_probe_run.json"
OUT = REPO_ROOT / "results" / "prereg_reader_probe_v2.json"

CAP_USD = 0.35
"""The operator's ruling of 2026-08-15 (evening), all-in — every second the endpoint bills, the
staging pod, the warm-up and the run. Read against the phase remainder the GUARD reports and never
against a ledger line or a sentence in a brief (Dv33, Dv378)."""

WINDOW_MINUTES = 30.0
AGREEMENT_BAR = 0.80
"""The two thresholds v1 registered and this record carries unchanged. The ≤30-minute budget prices
PRODUCTION — a full window of 111 threads — so for a 23-thread probe it is a REPORTED projection and
not a gate; the cap is what binds here, and the stop rule below says so in one place."""

SETUP_USD = 0.0440
SETUP_RULE = (
    "probe-a's SETTLED step ledger ($0.0944, read from scripts/runpod_guard.py) minus its own"
    " reading (164.4 billed worker seconds at the rate below) — the staging pod, the boot, the"
    " weight load and the idle tail, measured rather than budgeted. The rung that produces nothing"
    " is inside the same cap. Settled and not as-reported: docs/reports/probe-a.md closed at $0.0750"
    " and RunPod's billing kept moving for hours afterwards, so a setup taken from that reading"
    " would have been optimistic by $0.010 — 2.8% of this cap, in the direction that opens runs"
    " ([[unreadable_now_versus_never]])"
)

L4_SECONDS_PER_THREAD = 54.806
L4_SECONDS_PER_PAYABLE = 14.947
"""probe-a's measured rate, and the card it is a property of. `docs/reports/probe-a.md` §5.3: the
endpoint's runtime was an NVIDIA L4, while the $/s every projection in this repo uses was measured
on an `ADA_24` (RTX 4090) — `docs/reports/5c2-run.md`. Same price, slower card."""

CARD_PREFERENCE = ("ADA_24", "ADA_24_PRO", "AMPERE_24")
"""The 24 GB serverless classes to request, fastest first. `ADA_24` is the RTX 4090 the D7 re-read
exercised with this very volume attached (`results/d7_reread_srv2b.json`) and the class every 5c2
and sku-b run billed on; EU-RO-1 lists it at High stock today. The class is REQUESTED and never
asserted: which card a worker gets is the runtime delta SPEC 3.11 (2) exists to report, the actual
one lands in provenance, and the measured seconds are reported per card. A wrong card is caught by
the go/no-go's arithmetic, not by a guard that would spend a boot to refuse."""


def rendering(thread: dict, task: str) -> str:
    """One thread as the run will send it — the registered rendering, never a look-alike."""
    return prompts.reader_messages_gm4(
        thread["channel"],
        thread["post_id"],
        thread["post_text"],
        [(row["msg_id"], row["text"]) for row in thread["comments"]],
        task=task,
    )[0]["content"]


def rendering_sha256(thread: dict, task: str) -> str:
    """The sha of the exact string the worker will be sent for this thread.

    Per thread and not only over the list, because the list pins WHICH threads and this pins WHAT
    each of them is. A comment edited in the store between the registration and the run moves this
    number and moves nothing else ([[a_hash_is_not_the_claim_it_carries]])."""
    return hashlib.sha256(rendering(thread, task).encode("utf-8")).hexdigest()


def enumeration(kept: list[dict]) -> list[dict]:
    """The population as a LIST — every thread with its cases, its ids and its request's sha."""
    return [
        {
            "thread": subset.key(one["channel"], one["post_id"]),
            "channel": one["channel"],
            "post_id": one["post_id"],
            "injected": one["injected"],
            "in_the_census_cell": one["in_the_census_cell"],
            "cases": one["cases"],
            "payable_comments": len(one["comments"]),
            "msg_ids": [row["msg_id"] for row in one["comments"]],
            "silenced_before_payment": one["silenced"],
            "text_less": one["text_less"],
            "rendered_chars": len(rendering(one, prompts.READER_TASK_V2)),
            "rendering_sha256": rendering_sha256(one, prompts.READER_TASK_V2),
        }
        for one in kept
    ]


def bars(gold: dict, kept: list[dict]) -> dict:
    """The five bars. Every case the operator made obligatory is reachable now — that is D2's point.

    What is NOT changed is how a bar is decided: the four scorer functions, the fields they compare
    and the fields they refuse to compare are v1's, hashed into this record beside them.
    """
    rows = gold["per_comment"]
    needed = next(count for count in range(len(rows) + 1) if count / len(rows) >= AGREEMENT_BAR)
    flagship_signals = [signal["id"] for case in gold["flagships"] for signal in case["signals"]]
    n3 = next(one for one in kept if one["cases"] == ["N3"])
    return {
        "1_flagships": {
            "rule": (
                "each of the reference's five flagship CASES is found when every gold signal it"
                " carries is found by scorer.reader_signal_found — evidence overlap, plus"
                " subject_type and aspect where the gold states them. signal_type is not compared"
                " and neither is subject_id"
            ),
            "threshold": "5 of 5 cases",
            "scored_over": ["F1", "F2", "F3", "F4", "F5"],
            "gold_signals": flagship_signals,
            "scorer": "reader_signal_found",
        },
        "2_entity_cases": {
            "rule": (
                "an entity case is answered when the verdict for its thread carries an entity whose"
                " name or quote resolves to the case's brand_id through the watchlist matcher AND"
                " whose subject_type is the operator's ruling. E4 is the absence case: «чи варто» is"
                " the adverb, so the case is answered when NO entity in that thread names varto"
            ),
            "threshold": "4 of 4 cases",
            "scored_over": ["E1", "E2", "E3", "E4a", "E4b"],
            "reading": (
                "four CASES over five rows: E4 is one ruling about two threads and both must answer"
                " it. E1, E4a and E4b are the injected ones — v1 could only register 2 of 2 because"
                " the gate removes them before payment, and buying them directly is what makes the"
                " operator's 4/4 a measurement instead of an arithmetic impossibility"
            ),
            "scorer": "reader_entity_found",
        },
        "3_noise": {
            "rule": "zero signals in the verdicts of the reference's noise threads",
            "threshold": "0 signals",
            "scored_over": ["N2", "N3", "N4", "N5", "N6"],
            "excluded_with_cause": {
                "N1": (
                    "carried unchanged from v1: the reference's own S list reads a signal inside"
                    " this thread (S1, msg 21420), and the store shows two comments there rather"
                    " than the «десятки «+»» the N list describes. A bar that failed the reader for"
                    " agreeing with the reference would measure nothing. The thread is READ — S1 is"
                    " in the population — and its signal count is reported beside the bar"
                )
            },
            "n3_is_not_a_discriminating_case": (
                f"@sashafitnesslife:3939 reaches the reader as a post with"
                f" {len(n3['comments'])} payable comments: all {n3['silenced']} of its comments"
                " are removed by the gate's own plus-spam silencer before payment. Its «0 signals»"
                " is therefore produced by the silencer and not by the reader, and the bar's other"
                " four threads are what can move it. Registered inside the bar because the contract"
                " names it, and reported beside it because a cell that cannot be non-zero is not"
                " evidence ([[a_structurally_unreachable_zero]])"
            ),
            "scorer": "reader_noise_count",
        },
        "4_per_comment_agreement": {
            "rule": (
                "each gold row is compared on the fields the reference STATES for it"
                " (`scored_fields`) and on no others; a gold row the reader wrote no per_comment"
                " entry for counts as a disagreement and is also counted separately as `absent`"
            ),
            "threshold": f"rate >= {AGREEMENT_BAR}",
            "scored_over": [row["msg_id"] for row in rows],
            "arithmetic": (
                f"all {len(rows)} gold rows are inside this population — 578951 came with E1 — so"
                f" the bar is {needed} of {len(rows)} ({needed / len(rows):.3f});"
                f" {needed - 1} agreements scores {(needed - 1) / len(rows):.3f} and fails"
            ),
            "scorer": "reader_comment_agreement",
        },
        "5_time_and_cost": {
            "rule": (
                "the warm-up measures billed worker seconds per thread; the UNREAD remainder is"
                " projected two ways and the PESSIMISTIC one binds — per thread and per payable"
                " comment. The warm-up's own spend and the setup are added to it, because the cap is"
                " all-in and the rung that produces nothing is inside it"
            ),
            "thresholds": {"cap_usd_all_in": CAP_USD},
            "reported_not_gating": {
                "window_minutes_billed": WINDOW_MINUTES,
                "reading": (
                    "the ≤30-minute budget prices a PRODUCTION window of 111 threads and this probe"
                    " reads 23, four of which the gate does not deliver at all. Projecting it from"
                    " here is a reported number; the cap is the ceiling that gates"
                ),
            },
            "prior": {
                "source": summary.rel(PRICES),
                "rate_usd_per_second": json.loads(summary.read_text_or_refuse(PRICES))[
                    "rate_usd_per_second"
                ],
                "measured_on": "ADA_24 (RTX 4090) — docs/reports/5c2-run.md",
                "reading": (
                    "carried as the PRIOR only. The probe's own rate is what its endpoint bills, and"
                    " it is what the projection uses"
                ),
            },
        },
    }


def arithmetic(kept: list[dict]) -> dict:
    """What the cap can buy at the only rate that has been measured — computed before anything runs.

    The whole point of the card change is in this block: at the L4's measured seconds this
    population does not fit the cap, so the registration says by how much the faster card has to be
    faster, and the go/no-go measures exactly that.
    """
    rate = json.loads(summary.read_text_or_refuse(PRICES))["rate_usd_per_second"]
    threads = len(kept)
    payable = sum(len(one["comments"]) for one in kept)
    seconds_the_cap_buys = (CAP_USD - SETUP_USD) / rate
    by_thread = threads * L4_SECONDS_PER_THREAD
    by_payable = payable * L4_SECONDS_PER_PAYABLE
    binding = max(by_thread, by_payable)
    return {
        "rate_usd_per_second": rate,
        "setup_usd": SETUP_USD,
        "setup_rule": SETUP_RULE,
        "seconds_the_cap_buys_after_setup": round(seconds_the_cap_buys, 1),
        "at_the_l4_rate_probe_a_measured": {
            "seconds_per_thread": L4_SECONDS_PER_THREAD,
            "seconds_per_payable_comment": L4_SECONDS_PER_PAYABLE,
            "by_thread": {"seconds": round(by_thread, 1), "usd": round(by_thread * rate, 4)},
            "by_payable_comment": {
                "seconds": round(by_payable, 1),
                "usd": round(by_payable * rate, 4),
            },
            "all_in_usd": round(binding * rate + SETUP_USD, 4),
            "verdict": "does not fit the cap",
        },
        "break_even_speedup": round(binding / seconds_the_cap_buys, 3),
        "break_even_rule": (
            "the binding projection divided by the seconds the cap can buy after setup. A card this"
            " much faster than the L4 makes the registered population affordable; a slower one makes"
            " the go/no-go say STOP, which is the outcome this arithmetic exists to make legible"
            " BEFORE a resource is created rather than after"
        ),
        "what_a_stop_costs": (
            f"the setup and the warm-up's three threads — ${SETUP_USD:.4f} plus what three threads"
            " bill on the card that turns up; probe-a's L4 billed $0.0504 for exactly that draw"
        ),
    }


def build(kept: list[dict], gold: dict) -> dict:
    payable = sum(len(one["comments"]) for one in kept)
    injected = [one for one in kept if one["injected"]]
    return {
        "phase": "probe-b",
        "contract": "docs/PROMPT-probe-b.md D2",
        "class": (
            "PRE-REGISTRATION. Committed before the endpoint exists; git history is the only witness"
            " to that order, and no clock is stamped so the record re-derives byte for byte. Nothing"
            " here is a result. A pre-registration is a registration and not law: the layer's"
            " amendment comes after adjudication"
        ),
        "supersedes": {
            "record": summary.rel(SUPERSEDED),
            "sha256": summary.sha256_of(SUPERSEDED),
            "ruling": (
                "operator 2026-08-15 (evening), after docs/reports/probe-a.md §9: options A (fix the"
                " two shape defects), B (re-price on a faster 24 GB card) and C (score the bars on a"
                " registered subset) are bought as ONE registration under a $0.35 all-in cap. The"
                " superseded record is not edited, not re-derived and not re-pinned — it describes"
                " the run that was paid for under it"
            ),
            "what_it_keeps": [
                "the four scorer functions and every matching rule they implement",
                "results/reader_gold_w1.json, byte for byte",
                "the per-comment agreement bar of 0.80 and the flagship/entity/noise thresholds",
                "the input and output ceilings",
                "the serving block: base, no adapter, NF4, enable_thinking false, greedy, batch 1",
                "one attempt, no retry, and a STOP that leaves the attempt intact",
            ],
            "what_it_changes": [
                "the instrument: reader_thread_gm4_v2, two measured defects closed (Dv393, Dv394)",
                "the card: the fastest 24 GB class first, actual card in provenance",
                "the population: a registered subset with four threads injected past the gate",
            ],
        },
        "authority": {
            summary.rel(path): summary.sha256_of(path)
            for path in (CONTRACT, PLAN, REFERENCE, GOLD, SUPERSEDED)
        },
        "attempt": (
            "ONE attempt, no retry. A failed bar after a completed run closes the question by design"
            " review (plan §5). Anything this registration did not anticipate stops the run and is"
            " reported with the attempt intact"
        ),
        "population": {
            "class": (
                "a registered SUBSET of window 1, enumerated as a list. NOT the census cell: 19 of"
                " these threads are inside it and 4 are injected past the gate"
            ),
            "threads": len(kept),
            "payable_comments": payable,
            "injected_threads": len(injected),
            "gated_threads": len(kept) - len(injected),
            "injected_rule": (
                "the four threads SPEC 3.21 (1)'s marker rule removes before payment — E1, E4a, E4b"
                " and N3. They exist to make bars 2 and 3 reachable and nothing else: they never"
                " enter a production aggregate, and never a window or per-thread price for the"
                " census cell, because the gate does not deliver them and a rate measured over them"
                " would price a population nobody has. They DO cost money and are inside this cap."
                " Whether the production gate should deliver them is the sitting's question"
            ),
            "census_cell": {
                "record": summary.rel(cell.CENSUS),
                "sha256": cell.census_sha256(),
                "cell": cell.CELL,
                "threads": 111,
                "payable_comments": 912,
                "reading": (
                    "the population v1 registered, and what the 19 gated threads here are a subset"
                    " of. It is pinned so a later reader can say which of these threads production"
                    " would ever see"
                ),
            },
            "enumeration": {
                "producer": "scripts/probe_b_population.py",
                "sha256": summary.sha256_of(REPO_ROOT / "scripts" / "probe_b_population.py"),
                "digest": subset.digest(kept),
                "digest_rule": (
                    "sha256 over `channel:post_id\\tgated|injected\\tpayable msg_ids` for every"
                    " thread, in the enumeration's order. The flag is INSIDE the line: a subset that"
                    " swapped a gated thread for an injected one of the same shape would otherwise"
                    " hash the same"
                ),
                "threads": enumeration(kept),
            },
        },
        "instruments": {
            "task": prompts.READER_TASK_V2,
            # the two texts THIS registration registers, named — not `sorted(prompts.READER)`, which
            # is the live family and grew to three at the reader sitting. A frozen record derived
            # from a family that grows is a record that rewrites itself the day a fourth text lands,
            # and re-pinning a sealed registration is refused. Same narrowing `write_reader_prereg
            # .rendering()` took when v2 arrived, one field over ([[a_sealed_caller_forces_the_
            # default]]).
            "prompt_sha256": {
                task: prompts.prompt_sha256(task)
                for task in sorted((prompts.READER_TASK, prompts.READER_TASK_V2))
            },
            # the committed record's own words, unchanged: this file re-derives that record byte for
            # byte and a clearer sentence here would be a re-pinning of a sealed registration
            "prompt_rule": (
                "a sha per REGISTERED reader text, compared whole against what the worker's `info`"
                " answers. v1 stays servable so probe-a's evidence can be re-rendered; `task` above"
                " is the one this run reads with, and a scalar could not have said both"
            ),
            "v2_changes": {
                "Dv393": (
                    "`entities` is a LIST with the brackets written into the schema line and the"
                    " keyed form forbidden by name. All three of probe-a's paid verdicts came back"
                    " as an object keyed by the name, every other field right"
                ),
                "Dv394": (
                    "a signal read in the POST carries `from_post: true` and an empty `evidence`;"
                    " the «for the post the id is null» rule is scoped to `entities.msg_id`. probe-a"
                    " returned `evidence: [null]`, applying that rule to a field of message ids"
                ),
                "derivation": (
                    "v2 is derived from v1 by three `_swap` calls in src/market_pulse/prompts.py, so"
                    " «exactly two wording changes» is a property of the code rather than a claim"
                ),
            },
            "parser": {
                "module": "src/market_pulse/prompts.py",
                "function": "parse_reply",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
                "change": (
                    "one branch, in place: `from_post` absent reads False, so a v1 verdict is still"
                    " validated by exactly the rule it was registered under, and `evidence: [null]`"
                    " still refuses"
                ),
            },
            "scorer": {
                "module": "src/market_pulse/scorer.py",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
                "functions": [
                    "reader_signal_found",
                    "reader_entity_found",
                    "reader_comment_agreement",
                    "reader_noise_count",
                ],
                "unchanged": (
                    "byte for byte what v1 registered. The bars move because the population can"
                    " carry their cases now, never because the judge was rewritten"
                ),
            },
            "gold": {"record": summary.rel(GOLD), "sha256": summary.sha256_of(GOLD)},
            "ceilings": {
                "input_chars": prompts.READER_MAX_INPUT_CHARS,
                "input_rule": (
                    "a LOUD refusal, never a truncation. The largest thread of THIS population"
                    f" renders to {max(len(rendering(one, prompts.READER_TASK_V2)) for one in kept)}"
                    " characters under v2, so the guard cannot fire on a thread the probe is"
                    " registered to read"
                ),
                "output_tokens": local_llm.READER_MAX_NEW_TOKENS,
                "output_rule": (
                    "a ceiling against a truncated verdict, not a target. A reply that uses it all"
                    " comes back `finish_reason: length` and is counted as a parse failure by cause"
                ),
                "largest_threads": [
                    f"{subset.key(one['channel'], one['post_id'])} ({len(one['comments'])} payable)"
                    for one in sorted(kept, key=lambda one: -len(one["comments"]))[:3]
                ],
            },
            "serving": {
                "serving_config": "READER",
                "merge_state": "base-no-adapter",
                "adapter": None,
                "model": local_llm.MODEL_ID,
                "model_revision": "842da3794eaa0b77d5f08bae87a17459d91ff475",
                "quantization": dict(local_llm.QUANTIZATION),
                "chat_template": dict(local_llm.CHAT_TEMPLATE),
                "decoding": "greedy",
                "do_sample": False,
                "forward_batch_size": 1,
                "gpu_class_preference": list(CARD_PREFERENCE),
                "gpu_rule": (
                    "requested fastest-first and never asserted. probe-a asked for the display name"
                    " «NVIDIA L4», the endpoint came back `gpuIds: AMPERE_24` and the worker reported"
                    " an L4 runtime — so the CLASS is what is requested and the RUNTIME string is"
                    " what lands in provenance. Seconds per thread are reported per card"
                ),
                "template_note": (
                    "a NEW serving template for this run. `settings()` refuses config-mixing by"
                    " design; the srv-2d, CAPTION and probe-a templates are never edited"
                ),
            },
        },
        "bars": bars(gold, kept),
        "money": {
            "cap_usd_all_in": CAP_USD,
            "includes": (
                "the staging pod, the endpoint's boot, the warm-up, the run, the injected threads"
                " and every second the endpoint bills while it exists"
            ),
            "guard": (
                "scripts/runpod_guard.py --step probe-b --step-cap 0.35, read from the guard and"
                " never from a ledger line or from a sentence in the contract (Dv33, Dv378)"
            ),
            "arithmetic": arithmetic(kept),
        },
        "go_no_go": {
            "pattern": "the (10)(a) go/no-go: measure a warm-up, project, and stop before the rest",
            "warm_up": {
                "threads": list(subset.WARM_UP),
                "rule": (
                    "probe-a's registered draw, re-read under v2 — the same three threads, so the"
                    " two instruments are compared on one sample and the seconds are comparable"
                    " card for card. They were drawn from the MIDDLE third of the 111 by size"
                ),
                "where_they_sit_in_this_population": [
                    {
                        "thread": subset.key(one["channel"], one["post_id"]),
                        "payable_comments": len(one["comments"]),
                        "rank_by_size": index,
                        "of": len(kept),
                    }
                    for index, one in enumerate(
                        sorted(kept, key=lambda one: (len(one["comments"]), one["channel"]))
                    )
                    if subset.key(one["channel"], one["post_id"]) in subset.WARM_UP
                ],
                "representativeness": (
                    "3, 4 and 4 payable comments against this population's mean of"
                    f" {payable / len(kept):.2f} — the warm-up is SMALLER than the average thread it"
                    " prices, which is exactly why the per-payable projection is registered beside"
                    " the per-thread one and why the pessimistic of the two binds"
                ),
            },
            "projection_rule": (
                "the UNREAD remainder is what is projected, and the warm-up's own billed seconds"
                " plus the measured setup are added to it. Projecting the whole population and"
                " comparing it against what the cap has left after the warm-up counts those threads"
                " twice — 13% of this cap at 23 threads, against 2.7% at 111"
            ),
            "stop_rule": (
                "if setup + warm-up + the binding projection of the remainder exceeds the cap, STOP"
                " before any further call. The attempt stays intact, the measured seconds per thread"
                " and the card they were measured on go back to the operator, and no bar is scored"
                " on a partial run"
            ),
        },
        "frozen_when_the_endpoint_exists": [
            "results/prereg_reader_probe_v2.json",
            "results/reader_gold_w1.json",
            f"the {prompts.READER_TASK_V2} prompt text",
            "src/market_pulse/scorer.py's four reader functions",
            "scripts/probe_b_population.py's enumeration",
        ],
        "non_gating": [
            "the same bars recomputed with «категория» and «категория_личное» collapsed into one"
            " class. 8 of the 14 per-comment gold rows and 4 of the 7 flagship signals score on"
            " «категория», a word the ratified entity taxonomy does not carry and that the plan's"
            " own schema example stopped using on 2026-08-15 — so a bar that failed on that split"
            " would be measuring a vocabulary the two authorities disagree about, and the collapsed"
            " reading is what says whether it did",
            "parse failures by reason, and how many were `finish_reason: length` — «no signal» is"
            " counted over PARSED replies only",
            "signal types the reader proposed with `proposed: true`",
            "signals raised in N1, the thread excluded from bar 3 with cause",
            "signals the reader marked `from_post`, the field Dv394 adds",
            "entities resolved inside the noise threads",
            "how the four injected threads read, reported apart from every other number",
            "seconds per thread on THIS card beside probe-a's 54.806 on an L4",
        ],
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "borrowed": {
                name: summary.sha256_of(REPO_ROOT / name)
                for name in (
                    "scripts/probe_b_population.py",
                    "scripts/reader_population.py",
                    "scripts/write_reader_gold.py",
                    "src/market_pulse/prompts.py",
                    "src/market_pulse/scorer.py",
                    "src/market_pulse/local_llm.py",
                )
            },
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    gold = json.loads(summary.read_text_or_refuse(GOLD))
    record = build(subset.population(), gold)
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    pop = record["population"]
    print(
        f"  population {pop['threads']} threads ({pop['injected_threads']} injected) ·"
        f" {pop['payable_comments']} payable · digest {pop['enumeration']['digest'][:16]}…"
    )
    money = record["money"]["arithmetic"]
    print(f"  cap ${CAP_USD:.2f} · setup ${money['setup_usd']:.4f} ·")
    print(
        f"  at the L4's rate this population is"
        f" ${money['at_the_l4_rate_probe_a_measured']['all_in_usd']:.4f} all-in —"
        f" break-even speedup {money['break_even_speedup']}x"
    )
    for name, bar in record["bars"].items():
        print(f"  bar {name:26s} {bar.get('threshold') or bar['thresholds']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
