#!/usr/bin/env python3
"""`results/prereg_pass1_probe.json` — architecture D's decisive micro-measurement, registered.

The reader's prompt-engineering programme CLOSED by its own stop-rule on 2026-08-17 and the sitting
ruled a hybrid decomposition. This record registers the one measurement that decides whether the
decomposition is worth building: can a SHORT per-comment classification call, given the thread's
already-bought entity context, take bar 4's own gold?

Three things about it are unusual and each is here on purpose.

* **The population is ENUMERATED, not chosen.** The gating rows are bar 4's own fourteen, read out
  of gold r2; the census rows are every OTHER payable comment of those same seven threads, read out
  of the store through `probe_b_population`. Both counts are derived here and typed nowhere.
* **The entity context is bought already.** v5b's parsed verdicts supply six of the seven threads
  and reader-v4's supplies `@VARUS_channel:10613`, which v5b refused; the source file and its sha
  are recorded PER THREAD. Not one new reading is purchased to feed context.
* **The projection has TWO readings and the pessimistic one is registered.** A fitted line from
  v5b's 26 calls extrapolates below the range it was fitted on, so the gate is registered against a
  bound with no extrapolation in it — v5b's own CHEAPEST observed call, which emitted more tokens
  and prefilled more than any pass-1 call can ([[the_probe_must_cost_what_the_run_costs]]).

    PYTHONPATH=src python3.11 scripts/write_pass1_prereg.py
    PYTHONPATH=src python3.11 scripts/write_pass1_prereg.py --out /tmp/again.json   # the pair
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
import read_threads_reader_v5 as driver  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import prompts  # noqa: E402

OUT = REPO_ROOT / "results" / "prereg_pass1_probe.json"
PACK_PATH = REPO_ROOT / "results" / "pass1_probe_pack.json"
CONTRACT = REPO_ROOT / "docs" / "PROMPT-pass1-probe.md"
GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
V5B_PREREG = REPO_ROOT / "results" / "prereg_reader_probe_v5b.json"
V5B_VERDICT = REPO_ROOT / "results" / "reader_v5b_verdict.json"
V5B_EVIDENCE = REPO_ROOT / "results" / "reader_v5b_w1.jsonl"
V4_EVIDENCE = REPO_ROOT / "results" / "reader_v4_w1.jsonl"

PHASE = "pass1-probe"
CAP_USD = 0.20
"""The contract's cap, all in. Every second the pod EXISTS is inside it, dead segments included."""

CARD_USD_PER_HOUR_EXAMPLE = 0.74
"""What EU-RO-1 SECURE charged for the 4090 on 2026-08-17, and what reader-v5b was actually billed
at (`results/reader_v5b_run.json`, segment 1). An EXAMPLE so the arithmetic below is WORKED; the
meter of record is `costPerHr` in this run's own create response, and every figure is recomputed
from it before the generation process starts."""

DELETE_MARGIN_S = 60.0
BOOT_KILL_S = 300.0
SSH_DEADMAN_S = 180.0
MAX_RECREATES = 2
OUTPUT_CEILING = 256
"""Well above any answer the schema can produce — a pass-1 object is four scalars — and low enough
that a runaway generation is a bounded loss rather than a 4 000-token one. `finish_reason: length`
firing at all is a finding, and it is counted beside the bar."""

BAR_P1_MIN = 12
"""≥12 of 14. The contract's number, and it tolerates exactly TWO losses of any kind — a
disagreement, a refusal and an absent row all cost the same one row. Registered with the loss budget
spelled out so the result cannot be re-read afterwards
([[an_absolute_bar_needs_a_reachability_state]])."""


# --- what v5b measured, read out of v5b's own evidence ---------------------------------------------


def v5b_calls() -> list[dict]:
    """v5b's 26 answered units — the only per-call timings this stack has at this ceiling."""
    rows = [
        json.loads(line)
        for line in summary.read_text_or_refuse(V5B_EVIDENCE).splitlines()
        if line.strip()
    ]
    return [row for row in rows if isinstance(row.get("usage"), dict)]


def measured_rate() -> dict:
    """Two readings of what one short call costs, and which one the gate is registered against."""
    calls = v5b_calls()
    seconds = sum(float(one["seconds"]["worker"]) for one in calls)
    tokens = sum(int(one["usage"]["completion_tokens"]) for one in calls)
    chars = sum(int(one["emitted_chars"]) for one in calls)
    cheapest = min(calls, key=lambda one: int(one["usage"]["completion_tokens"]))
    # the fitted line, least squares over the 26 calls
    mean_x, mean_y = tokens / len(calls), seconds / len(calls)
    xs = [int(one["usage"]["completion_tokens"]) for one in calls]
    ys = [float(one["seconds"]["worker"]) for one in calls]
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True)) / sum(
        (x - mean_x) ** 2 for x in xs
    )
    intercept = mean_y - slope * mean_x
    answer = '{"msg_id": 21626, "subject_type": "сеть_ритейлер", "subject_id": "varus", "stance": "negative"}'
    per_token_chars = chars / tokens
    expected_tokens = len(answer) / per_token_chars
    return {
        "source": {
            "record": summary.rel(V5B_EVIDENCE),
            "sha256": summary.sha256_of(V5B_EVIDENCE),
            "calls": len(calls),
        },
        "v5b_totals": {
            "worker_seconds": round(seconds, 3),
            "completion_tokens": tokens,
            "emitted_chars": chars,
            "seconds_per_completion_token": round(seconds / tokens, 6),
            "chars_per_completion_token": round(per_token_chars, 4),
        },
        "fitted": {
            "line": "seconds ≈ intercept + slope × completion_tokens, least squares over the 26",
            "intercept_seconds": round(intercept, 3),
            "slope_seconds_per_token": round(slope, 6),
            "fitted_over_completion_tokens": [min(xs), max(xs)],
            "expected_answer_chars": len(answer),
            "expected_completion_tokens": round(expected_tokens, 2),
            "seconds_per_pass1_call": round(intercept + slope * expected_tokens, 3),
            "why_it_does_not_gate": (
                "a pass-1 answer is ~36 tokens and the line was fitted between 96 and 2 056, so"
                " using it would EXTRAPOLATE below its own range. It is published because the"
                " difference between the two readings is what the run measures"
            ),
        },
        "ceiling": {
            "rule": (
                "the cheapest call v5b actually made, used as a BOUND. It emitted more completion"
                " tokens and prefilled more prompt tokens than any pass-1 request can, on the same"
                " transport, the same card and the same serving config — so no pass-1 call can cost"
                " more, and the bound carries no forecast in it"
            ),
            "unit": cheapest["id"],
            "completion_tokens": int(cheapest["usage"]["completion_tokens"]),
            "prompt_tokens": int(cheapest["usage"]["prompt_tokens"]),
            "seconds_per_pass1_call": round(float(cheapest["seconds"]["worker"]), 3),
            "gates": True,
        },
        "boot": {
            "seconds": float(next(one["boot_seconds"] for one in calls if one.get("boot_seconds"))),
            "rule": (
                "v5b's own measured boot, from `pod create` to the first request being answerable."
                " The boot-kill deadline below is registered above it with room, and the projection"
                " charges it in full"
            ),
        },
    }


# --- the population, enumerated ---------------------------------------------------------------------


def gold_rows() -> list[dict]:
    """Bar 4's fourteen, as gold r2 spells them — thread, id, and the fields the bar scores."""
    record = json.loads(summary.read_text_or_refuse(GOLD))
    rows = []
    for row in record["per_comment"]:
        evidence = row["evidence_row"]
        rows.append(
            {
                "thread": f"{row['channel']}:{evidence['post_id_in_the_store']}",
                "msg_id": int(row["msg_id"]),
                "scored_fields": sorted(row["scored_fields"]),
                "gold": {field: row.get(field) for field in sorted(row["scored_fields"])},
                "rule": row["rule"],
            }
        )
    return sorted(rows, key=lambda one: (one["thread"], one["msg_id"]))


def entity_context() -> dict:
    """Per gold thread, the BOUGHT verdict its entity block comes from — file, sha and count.

    v5b first because it is the latest reading; v4 for `@VARUS_channel:10613`, whose v5b reply was
    refused `malformed JSON` and whose four gold rows are exactly the four bar 4 counted ABSENT.
    Recorded per thread rather than as one sentence, because the two sources are not interchangeable
    and a reader of this record has to be able to say which row rests on which
    ([[spell_the_rows_out_with_their_source]]).
    """
    parsed = {}
    for path in (V5B_EVIDENCE, V4_EVIDENCE):
        for line in summary.read_text_or_refuse(path).splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            key = f"{row.get('channel')}:{row.get('post_id')}"
            if row.get("parsed") and key not in parsed:
                parsed[key] = (path, row["parsed"])

    context = {}
    for thread in sorted({one["thread"] for one in gold_rows()}):
        if thread not in parsed:
            raise SystemExit(
                f"{thread}: neither v5b nor v4 carries a parsed verdict for it, so pass 1 has no"
                " entity context to send and the bar's rows for it are unreachable. Stop and report."
            )
        path, verdict = parsed[thread]
        entities = verdict.get("entities") or []
        context[thread] = {
            "source": summary.rel(path),
            "sha256": summary.sha256_of(path),
            "entities": len(entities),
            "post_summary_chars": len(verdict.get("post_summary") or ""),
        }
    return context


def population() -> dict:
    """The 14 gating rows and the census rows around them, both derived from files.

    The census population is «every OTHER payable comment of the same seven threads» — the store's
    own payable set through `probe_b_population.build`, minus the gold ids. It buys the per-thread
    distribution and the price of a window pass-1, and it carries no gold and gates nothing.
    """
    gold = gold_rows()
    by_thread: dict[str, list[int]] = {}
    for row in gold:
        by_thread.setdefault(row["thread"], []).append(row["msg_id"])

    threads = {f"{one['channel']}:{one['post_id']}": one for one in subset.population()}
    gating, census, per_thread = [], [], {}
    for thread in sorted(by_thread):
        if thread not in threads:
            raise SystemExit(f"{thread}: not in the registered subset — the population cannot form")
        payable = [int(one["msg_id"]) for one in threads[thread]["comments"]]
        missing = sorted(set(by_thread[thread]) - set(payable))
        if missing:
            raise SystemExit(
                f"{thread}: gold rows {missing} are not payable comments of it, so pass 1 could not"
                " be asked about them at all. Stop and report."
            )
        mine = sorted(by_thread[thread])
        others = [msg_id for msg_id in payable if msg_id not in set(mine)]
        gating += [{"thread": thread, "msg_id": msg_id} for msg_id in mine]
        census += [{"thread": thread, "msg_id": msg_id} for msg_id in others]
        per_thread[thread] = {
            "payable_comments": len(payable),
            "gold_rows": len(mine),
            "census_rows": len(others),
        }
    return {
        "rule": (
            "ENUMERATED, never chosen. The gating rows are bar 4's own fourteen out of gold r2; the"
            " census rows are every other payable comment of the same seven threads, out of the"
            " store through scripts/probe_b_population.py. Every count here is derived from those"
            " two files by this producer and typed nowhere"
        ),
        "gold": {
            "record": summary.rel(GOLD),
            "sha256": summary.sha256_of(GOLD),
            "revision": "r2",
            "rows": gating,
            "n": len(gating),
        },
        "census": {
            "producer": "scripts/probe_b_population.py::population",
            "sha256": summary.sha256_of(REPO_ROOT / "scripts" / "probe_b_population.py"),
            "rows": census,
            "n": len(census),
            "carries_no_gold": True,
        },
        "threads": sorted(by_thread),
        "per_thread": per_thread,
        "units": len(gating) + len(census),
        "entity_context": entity_context(),
    }


# --- the money, and the gate solved backwards over the built pack -----------------------------------


def money(units: int) -> dict:
    rate = CARD_USD_PER_HOUR_EXAMPLE / 3600.0
    cap_seconds = CAP_USD / rate
    usable = cap_seconds - DELETE_MARGIN_S
    reading = measured_rate()
    per_call = float(reading["ceiling"]["seconds_per_pass1_call"])
    boot = float(reading["boot"]["seconds"])
    projection = per_call * units
    return {
        "cap_usd_all_in": CAP_USD,
        "cap_rule": (
            "the contract's cap, all in. Every second the pod EXISTS is inside it — provisioning,"
            " idle and every segment of the attempt, dead pods included"
        ),
        "guard": (
            f"scripts/runpod_guard.py --step {PHASE} --step-cap {CAP_USD}, anchored BEFORE the"
            " first pod create and read from the guard, never from a sentence in a contract"
        ),
        "meter": {
            "resource": (
                "ONE rented pod, billed for every second it EXISTS — from `pod create` to `pod"
                " delete`. `pod stop` does not stop the bill, so the run deletes and never stops"
            ),
            "card_requested": "NVIDIA GeForce RTX 4090",
            "datacenter": "EU-RO-1, pinned by network volume qw4nwleanc — the volume decides",
            "price_rule": (
                "**READ ON THE DAY.** `costPerHr` in the create response is the meter of record and"
                " every figure in this block is recomputed from it before the generation process"
                " starts. A projection that no longer fits deletes the pod and STOPS"
            ),
            "worked_example_usd_per_hour": CARD_USD_PER_HOUR_EXAMPLE,
            "worked_example_rule": (
                f"${CARD_USD_PER_HOUR_EXAMPLE:.2f}/h is what reader-v5b was BILLED at on 2026-08-17"
                " and it is used below so the arithmetic is WORKED rather than described. It is an"
                " EXAMPLE and not the meter"
            ),
            "usd_per_second_at_the_example": round(rate, 9),
        },
        "reading": reading,
        "arithmetic": {
            "seconds_the_cap_buys": round(cap_seconds, 3),
            "delete_margin_seconds": DELETE_MARGIN_S,
            "usable_seconds": round(usable, 3),
            "units": units,
            "seconds_per_call_registered": per_call,
            "reading_projection_seconds": round(projection, 3),
            "boot_seconds_charged": boot,
            "pre_generation_budget_seconds": round(usable - BOOT_KILL_S - projection, 3),
            "affordability_deadline_seconds": round(usable - projection, 3),
            "boot_free_corner_seconds_per_unit": round(usable / units, 3),
            "boot_free_corner_rule": (
                "what one unit may cost if the pod were provisioned for free — `usable ÷ units`,"
                " with no boot forecast in it at all. The FIRST unit's by-unit leg extrapolates the"
                " other units off it, so a first call above this bound STOPs the gate on arithmetic"
                " alone, whatever provisioning turns out to cost (Dv471's method)"
            ),
        },
        "segments": (
            "the cap is the ATTEMPT's. Per-segment spend is that segment's billed seconds times its"
            " OWN costPerHr, summed across segments — never a balance delta, which prices the"
            " account and not the step"
        ),
    }


def gate_table(record: dict, pack: dict) -> dict:
    """The registered full-pass gate, run over the built pack unit by unit BEFORE anything exists.

    Dv471's method, and the reason it is not optional: reader-v5b's ruled pack order was priced this
    way at $0 and turned out to STOP the gate at unit 1, which cost nothing because the table was
    built before the pod ([[a_ruling_aimed_at_one_leg_lands_on_the_other]]).

    The per-call cost fed in is the REGISTERED bound, so the table answers «does this order clear
    the gate even if every call costs what the cheapest thread-read cost».
    """
    rate = CARD_USD_PER_HOUR_EXAMPLE / 3600.0
    per_call = float(record["money"]["arithmetic"]["seconds_per_call_registered"])
    boot = float(record["money"]["arithmetic"]["boot_seconds_charged"])
    rows, stop_after, tightest = [], None, None
    elapsed = boot
    for index, item in enumerate(pack["items"], start=1):
        elapsed += per_call
        seen = [
            {"id": one["id"], "seconds": per_call, "unit": one["id"]}
            for one in pack["items"][:index]
        ]
        state = driver.projection(record, rate, seen, elapsed, pack)
        margin = state["seconds_per_unit_that_still_fits"] - state["measured_seconds_per_unit"]
        rows.append(
            {
                "after": index,
                "unit": item["id"],
                "verdict": state["verdict"],
                "binding_leg": state["projections"]["binding"]["which"],
                "headroom_seconds": state["headroom_seconds"],
                "margin_seconds_per_unit": round(margin, 3),
            }
        )
        if state["verdict"] == "STOP" and stop_after is None:
            stop_after = index
        if tightest is None or margin < tightest["margin_seconds_per_unit"]:
            tightest = rows[-1]
    first = pack["items"][0]
    corner = float(record["money"]["arithmetic"]["boot_free_corner_seconds_per_unit"])
    return {
        "rule": (
            "the registered full-pass gate, evaluated after every unit at the per-call bound above."
            " Reported and gating NOTHING here — the run's own gate is the one that binds — but it"
            " is in the record because a knife-edge nobody named before the money is a knife-edge"
            " discovered in a log"
        ),
        "per_call_seconds": per_call,
        "boot_seconds_charged": boot,
        "first_stop_after_units": stop_after,
        "tightest": tightest,
        "unit_one_without_any_boot": {
            "unit": first["id"],
            "expected_seconds": per_call,
            "zero_boot_ceiling_seconds": corner,
            "clears": per_call <= corner,
            "rule": (
                "the corner with NO provisioning forecast in it: even charging the pod nothing to"
                " boot, unit 1 may not cost more than `usable ÷ units`"
            ),
        },
        "two_legs_collapse": (
            "every pass-1 unit carries exactly ONE payable comment, so the gate's by-payable leg"
            " and its by-unit leg are the same number by construction. v5b's knife-edge lived in"
            " the gap between them; this pack has no gap"
        ),
        "per_unit": rows,
    }


# --- the record --------------------------------------------------------------------------------------


def bars(pop: dict) -> dict:
    n = pop["gold"]["n"]
    return {
        "P1_per_comment_agreement": {
            "gating": True,
            "threshold": f"{BAR_P1_MIN} of {n} rows agreed",
            "n": n,
            "minimum_agreed": BAR_P1_MIN,
            "loss_budget": {
                "rows_that_may_be_lost": n - BAR_P1_MIN,
                "rule": (
                    "a disagreement, a refusal and an ABSENT row each cost exactly one row, so the"
                    " bar tolerates two losses of any mixture. Registered here so the result cannot"
                    " be re-read afterwards against a budget nobody wrote down"
                ),
                "the_thread_that_carries_the_most": max(
                    pop["per_thread"], key=lambda name: pop["per_thread"][name]["gold_rows"]
                ),
            },
            "comparison": (
                "scorer.reader_comment_agreement — the SAME comparison bar 4 was scored with, called"
                " and never restated. The symmetric vocabulary collapse and the ABSENT state come"
                " with it; a fresh equality loop here would be a second definition of the bar"
            ),
            "collapse": {"map": {"категория_личное": "категория"}, "symmetric": True},
            "scored_fields": sorted(
                {field for row in pop["gold"]["rows"] for field in _fields_of(row)}
            ),
        },
        "census": {
            "gating": False,
            "n": pop["census"]["n"],
            "reports": [
                "the per-thread distribution of subject_type over the neighbour rows",
                "refusals by shape",
                "seconds and completion tokens per call",
                "the window pass-1 re-price: per-comment cost × the census cell's payable comments",
            ],
            "rule": "REPORTED and never gating — no number here moves P1",
        },
    }


def _fields_of(row: dict) -> list[str]:
    return row.get("scored_fields", [])


def build() -> dict:
    pop = population()
    block = money(pop["units"])
    record = {
        "phase": PHASE,
        "class": (
            "PRE-REGISTRATION. Committed before any pod of this attempt exists; git history is the"
            " only witness that it preceded the money. It FREEZES at the FIRST `pod create` of the"
            " attempt and nothing after that may edit it — a recreated pod reads the SAME frozen"
            " record, which is what makes a replacement a segment of one attempt, not a second one"
        ),
        "contract": {
            summary.rel(CONTRACT): summary.sha256_of(CONTRACT),
        },
        "authority": {
            "knowledge/decisions/reader-programme-closed-and-the-architecture-sitting-17-08.md": (
                summary.sha256_of(
                    REPO_ROOT
                    / "knowledge"
                    / "decisions"
                    / "reader-programme-closed-and-the-architecture-sitting-17-08.md"
                )
            ),
            "results/prereg_reader_probe_v5b.json": summary.sha256_of(V5B_PREREG),
            "results/reader_v5b_verdict.json": summary.sha256_of(V5B_VERDICT),
        },
        "attempt": (
            "ONE attempt, no retry. A kill or a STOP closes the question, and so does a completed"
            " run with a failed bar"
        ),
        "return_to_sitting": (
            "**A FAILED BAR GOES BACK TO THE SITTING, never to a prompt iteration.** The options"
            " the sitting of 2026-08-17 left open are B (labelled subject_type data + LoRA) and C"
            " (a different base). There is no pass1-v2 prompt without a sitting ruling, and this"
            " clause is pre-registered so it cannot be re-decided once the number is in"
        ),
        "instruments": {
            "task": prompts.PASS1_TASK,
            "prompt_sha256": {prompts.PASS1_TASK: prompts.prompt_sha256(prompts.PASS1_TASK)},
            "renderer": "market_pulse.prompts.pass1_messages_gm4",
            "parser": {
                "module": "src/market_pulse/prompts.py",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
                "entry_point": "market_pulse.prompts.parse_pass1",
                "rule": (
                    "strict single object, domain-checked: the four subject_type readings, the"
                    " stance domain, and the request's own msg_id echoed back. Everything else is a"
                    " refusal and no container is repaired"
                ),
            },
            "subject_types": list(prompts.PASS1_SUBJECT_TYPES),
            "subject_types_rule": (
                "FOUR, not the reader parser's five. The v5 text stopped offering «категория» and"
                " the run measured what that did: over v5b's 195 per_comment rows the word does not"
                " appear once. The gold's own «категория» is handled by the scorer's symmetric"
                " collapse, where it has always been handled"
            ),
            "gold": {
                "record": summary.rel(GOLD),
                "sha256": summary.sha256_of(GOLD),
                "revision": "r2",
            },
            "scorer": {
                "module": "src/market_pulse/scorer.py",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
                "unchanged": True,
            },
            "serving": json.loads(summary.read_text_or_refuse(V5B_PREREG))["instruments"]["serving"]
            | {"output_tokens": OUTPUT_CEILING},
            "serving_rule": (
                "v5b's serving block object-equal except the output ceiling: same base, same"
                " adapter state, same quantisation, same greedy decoding, same batch of one. The"
                " ceiling drops 4 000 → "
                f"{OUTPUT_CEILING} because the answer is four scalars, and `finish_reason: length`"
                " firing at all is counted beside the bar"
            ),
            "ceilings": {
                "output_tokens": OUTPUT_CEILING,
                "input_chars": prompts.PASS1_MAX_INPUT_CHARS,
                "input_rule": "a request over the input ceiling is REFUSED, never truncated",
            },
        },
        "population": pop,
        "bars": bars(pop),
        "money": block,
        "transport": {
            "inherited_from": "results/prereg_reader_probe_v5b.json",
            "gate_0_ssh_deadman_seconds": SSH_DEADMAN_S,
            "max_recreates": MAX_RECREATES,
            "third_dead_pod": "a datacenter state and a STOP, not a fourth create",
            "boot_kill_seconds": BOOT_KILL_S,
            "gates_append": (
                "every gate snapshot is APPENDED to a list and stamped with its segment and pod id."
                " reader-v4 overwrote its first GO and the arithmetic had to be re-checked by hand"
            ),
            "per_row_persistence": (
                "request + its rendering sha, the raw reply, the parse outcome, seconds,"
                " finish_reason and cut_chars — one row per unit, exactly as v5b wrote them"
            ),
            "delete_never_stop": True,
        },
        "frozen_when_the_pod_exists": [
            "results/prereg_pass1_probe.json",
            "results/pass1_probe_pack.json",
            f"the {prompts.PASS1_TASK} prompt text",
            "src/market_pulse/prompts.py — the renderer and the parser",
            "results/reader_gold_w1_r2.json",
        ],
        "go_no_go": (
            "before the FIRST paid call: the guard is anchored, the pack's rendering shas are"
            " re-derived on the pod and must equal the registered ones, and the full-pass gate is"
            " evaluated after every unit. A STOP deletes the pod and closes the attempt"
        ),
        "non_gating": (
            "the census, the refusal shapes, the seconds and tokens per call, and the window"
            " re-price. None of them moves P1"
        ),
    }
    pack = build_pack(record)
    record["money"]["arithmetic"]["full_pass_over_the_registered_order"] = gate_table(record, pack)
    record["producer"] = {
        "script": summary.rel(Path(__file__)),
        "sha256": summary.sha256_of(Path(__file__)),
        "borrowed": {
            name: summary.sha256_of(REPO_ROOT / name)
            for name in (
                "scripts/probe_b_population.py",
                "scripts/read_threads_reader_v5.py",
                "scripts/window_summary_5c2.py",
                "src/market_pulse/prompts.py",
            )
        },
        "rule": "no clock is stamped, so the record re-derives byte for byte from its own inputs",
    }
    return record


def build_pack(record: dict) -> dict:
    """The 64 requests, in the registered order, each with the sha of what the pod must render.

    Thread-grouped and, inside a thread, gold rows and census rows INTERLEAVED as the store
    enumerates them — the order is the comment order, which is the only order that is a fact about
    the data rather than about the bar. Grouping by thread is what lets one entity block be rendered
    per thread instead of per row.
    """
    threads = {f"{one['channel']}:{one['post_id']}": one for one in subset.population()}
    parsed = {}
    for path in (V5B_EVIDENCE, V4_EVIDENCE):
        for line in summary.read_text_or_refuse(path).splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            key = f"{row.get('channel')}:{row.get('post_id')}"
            if row.get("parsed") and key not in parsed:
                parsed[key] = row["parsed"]

    gold_ids = {(one["thread"], one["msg_id"]) for one in record["population"]["gold"]["rows"]}
    items = []
    for thread in record["population"]["threads"]:
        source = threads[thread]
        verdict = parsed[thread]
        channel, post_id = source["channel"], int(source["post_id"])
        for comment in source["comments"]:
            msg_id = int(comment["msg_id"])
            rendered = prompts.pass1_messages_gm4(
                channel,
                post_id,
                verdict.get("post_summary") or "",
                verdict.get("entities") or [],
                msg_id,
                comment["text"],
            )[0]["content"]
            items.append(
                {
                    "id": f"{thread}#{msg_id}",
                    "thread": thread,
                    "channel": channel,
                    "post_id": post_id,
                    "msg_id": msg_id,
                    "leg": "gold" if (thread, msg_id) in gold_ids else "census",
                    "payable_comments": 1,
                    "text": comment["text"],
                    "topic": verdict.get("post_summary") or "",
                    "entities": verdict.get("entities") or [],
                    "rendered_chars": len(rendered),
                    "rendering_sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
                }
            )
    if len({one["id"] for one in items}) != len(items):
        raise SystemExit("two units share an id — the answers would be unresolvable")
    return {
        "phase": PHASE,
        "task": prompts.PASS1_TASK,
        "registration": {"record": summary.rel(OUT)},
        "instruments": {
            "prompt_sha256": record["instruments"]["prompt_sha256"],
            "renderer": record["instruments"]["renderer"],
            # the pod's handshake asks BOTH questions off the pack: is the registered text what this
            # checkout renders, and is the module the Mac will parse with the module the pod
            # rendered from. The second needs the parser's sha to travel in the pack
            "parser": record["instruments"]["parser"],
        },
        "serving": record["instruments"]["serving"],
        "reading": (
            "the pod renders each item itself, from the fields in it, and refuses unless its sha"
            " equals the one above. Shipping the rendered string would only prove the two machines"
            " agree about a string; what has to be true is that the model is shown what the"
            " registration registered"
        ),
        "order_rule": (
            "thread-grouped in `channel:post_id` order, and inside a thread the store's own comment"
            " order — gold rows and census rows interleaved, never sorted apart. A pack that read"
            " the gold rows first would make the gate's first units unrepresentative of the rest"
        ),
        "items": items,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--pack", type=Path, default=PACK_PATH)
    args = parser.parse_args(argv)
    record = build()
    pack = build_pack(record)
    for path, payload in ((args.out, record), (args.pack, pack)):
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {summary.rel(path)}  sha256 {summary.sha256_of(path)[:16]}…")

    arithmetic = record["money"]["arithmetic"]
    table = arithmetic["full_pass_over_the_registered_order"]
    print(
        f"  cap ${CAP_USD:.2f} buys {arithmetic['seconds_the_cap_buys']:.1f} s ·"
        f" usable {arithmetic['usable_seconds']:.1f} s ·"
        f" {arithmetic['units']} units at {arithmetic['seconds_per_call_registered']:.3f} s"
    )
    print(
        f"  reading projection {arithmetic['reading_projection_seconds']:.1f} s ·"
        f" boot {arithmetic['boot_seconds_charged']:.1f} s ·"
        f" budget {arithmetic['pre_generation_budget_seconds']:.1f} s ·"
        f" affordability {arithmetic['affordability_deadline_seconds']:.1f} s"
    )
    print(
        f"  unit 1 {table['unit_one_without_any_boot']['unit']} ·"
        f" {table['per_call_seconds']:.3f} s vs a zero-boot ceiling of"
        f" {table['unit_one_without_any_boot']['zero_boot_ceiling_seconds']:.1f} s"
        f" -> clears {table['unit_one_without_any_boot']['clears']}"
    )
    print(
        f"  full pass: first STOP after {table['first_stop_after_units']} unit(s) ·"
        f" tightest margin {table['tightest']['margin_seconds_per_unit']:.2f} s/unit at unit"
        f" {table['tightest']['after']} ({table['tightest']['unit']})"
    )
    print(
        f"  population: {record['population']['gold']['n']} gold +"
        f" {record['population']['census']['n']} census ="
        f" {record['population']['units']} units over"
        f" {len(record['population']['threads'])} threads"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
