#!/usr/bin/env python3
"""`results/prereg_reader_probe_v5.json` — the sitting of 2026-08-17, frozen before the pod exists.

**Two legs and they may not touch each other.** Leg A is reader-v4's population, unchanged and
paired by the same digest, scored by the same four bars against the same gold — the only thing that
moved is the instrument, which is the whole point. Leg B is ONE thread bought to prove the CHUNKING
MECHANISM, with mechanical bars of its own; it carries no semantic gold and cannot move a bar of
leg A. Two legs in one registration and one sentence saying which numbers each may produce.

**The instrument is RE-DERIVED, and that is the inverse of v4's rule.** v4 copied v3's whole
`instruments` block because nothing about what is measured had moved. Here the task, the prompt map,
the parser's behaviour and the output ceiling all move, so a copy would be a claim that is false in
four places. What is copied is what really is unchanged and is copied OBJECT-EQUAL: the scorer's
bytes, the gold, the serving configuration and every threshold of bars 1-4.

**The output ceiling MOVES, and it is the one number this producer computes rather than carries.**
2 000 tokens was v4's and it never fired — `finish_reason: length` on 0 of 23 — but v4's largest
reply is 1 946 tokens, **97.3% of it**. v5 asks for more: the echo duty pushes every id into a list,
the attribution block lengthens `reading` fields and pair 3 puts a second msg_id in `evidence`. Leg
B asks a 16-row chunk for sixteen rows at once. The arithmetic is published as a TABLE, from v4's
own rows, and the ceiling is set above the pessimistic corner of the largest unit in the run —
because a ceiling that fires is a truncated verdict, and a truncated verdict fails a bar for a
transport reason and spends the one attempt on it.

**One ceiling for BOTH legs.** Two ceilings in one run would make leg A and leg B two instruments,
which is worse than either value.

    PYTHONPATH=src python3.11 scripts/write_reader_prereg_v5.py
    PYTHONPATH=src python3.11 scripts/write_reader_prereg_v5.py --out /tmp/again.json   # the pair
"""

import argparse
import hashlib
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
import write_reader_prereg_v3 as v3  # noqa: E402

from market_pulse import prompts, reader_v5  # noqa: E402

OUT = REPO_ROOT / "results" / "prereg_reader_probe_v5.json"
SUPERSEDES = REPO_ROOT / "results" / "prereg_reader_probe_v4.json"
V4_EVIDENCE = REPO_ROOT / "results" / "reader_v4_w1.jsonl"
V4_VERDICT = REPO_ROOT / "results" / "reader_v4_verdict.json"
CONTRACT = REPO_ROOT / "docs" / "PROMPT-reader-v5-prep.md"

CAP_USD = 0.45
"""The operator's ruling of 2026-08-17. v4's $0.35 bought 23 threads for $0.2361 of step resources;
this run adds a second leg and a longer output, and the cap is raised once and named."""

CARD = "NVIDIA GeForce RTX 4090"
CARD_USD_PER_HOUR_EXAMPLE = 0.74
"""**An EXAMPLE and not the meter.** Dv448 is law here: the card's price is READ on the day with
`runpodctl gpu list`, and every figure in the money block is recomputed from the `costPerHr` the
create response returns before the generation process starts. $0.74/h is what EU-RO-1 SECURE offered
on 2026-08-16 and it is used below so the arithmetic is worked rather than described."""

DELETE_MARGIN_S = 60.0
BOOT_KILL_S = 720.0
TERMINATE_AFTER_MIN = 90
BOOT_TABLE_S = (180.0, 300.0, 480.0, 600.0, 720.0)

V4_PRE_GENERATION_S = 39.0
"""reader-v4's measured seconds from the `pod create` response to the generation process's first
line — 18:00:12Z to 18:00:51Z, out of its own run table. The only measurement of that leg this stack
has, and what the boot table below is worked at. The pre-generation BUDGET is a different quantity
and can be negative; this one cannot."""

LEG_B_THREAD = "@klopotenkofood:6040"
LEG_B_CHUNK = 16
"""The sitting's ruling (d): 43 payable comments, chunks of at most 16, so 16/16/11. The thread
renders WHOLE at well under the input ceiling — the chunking is bought to prove the MECHANISM
before the window's 125/108/105-comment giants are sent through it, not because this thread needs
it, and the registration says so where a reader will look."""

OUTPUT_CEILING = 4000
"""The registered `max_new_tokens` for v5, both legs. Set above the pessimistic corner of the
largest unit in the run (a 16-row chunk, 2 491 tokens by the model below), not tuned to a fit."""


def v4_rows() -> list[dict]:
    return [
        json.loads(line) for line in V4_EVIDENCE.read_text(encoding="utf-8").splitlines() if line
    ]


def v4_reading() -> dict:
    """What reader-v4 measured, re-summed from ITS rows — never copied out of its report."""
    rows = v4_rows()
    parsed = [row for row in rows if row["parsed"]]
    seconds = sum(row["seconds"]["worker"] for row in rows)
    completion = sum(int((row.get("usage") or {}).get("completion_tokens") or 0) for row in rows)
    # the per-ROW rate has to be over the threads whose rows can be counted, and the per-SECOND rate
    # over every thread that was billed. Two denominators, named apart: mixing them turns v4's
    # published 137.83 tokens a requested row into 167.9 and over-prices leg B by 22%
    # ([[the_fix_widened_the_denominator]])
    completion_parsed = sum(
        int((row.get("usage") or {}).get("completion_tokens") or 0) for row in parsed
    )
    rates = sorted(
        int((row.get("usage") or {}).get("completion_tokens") or 0) / row["seconds"]["worker"]
        for row in rows
    )
    requested = sum(row["payable_comments"] for row in parsed)
    returned = sum(len(row["parsed"]["per_comment"]) for row in parsed)
    noise_rows = sum(len(row["parsed"]["noise"]) for row in parsed)
    # three numbers and they are not the same number: rows written into `noise`, ids answered ONLY
    # there, and ids the model put in BOTH lists — v4 broke «at most one of the two» on three
    # comments of @VARUS_channel:10366, which the parser deliberately does not refuse
    only_noise = both = 0
    for row in parsed:
        in_pc = {one["msg_id"] for one in row["parsed"]["per_comment"]}
        in_noise = {one["msg_id"] for one in row["parsed"]["noise"]}
        only_noise += len(in_noise - in_pc)
        both += len(in_noise & in_pc)
    return {
        "record": summary.rel(V4_EVIDENCE),
        "sha256": summary.sha256_of(V4_EVIDENCE),
        "threads": len(rows),
        "threads_parsed": len(parsed),
        "payable_comments": sum(row["payable_comments"] for row in rows),
        "generation_seconds": round(seconds, 3),
        "seconds_per_thread": round(seconds / len(rows), 3),
        "completion_tokens": completion,
        "completion_tokens_over_parsed_threads": completion_parsed,
        "tokens_per_second_mean": round(completion / seconds, 2),
        "tokens_per_second_slowest_thread": round(rates[0], 2),
        "per_comment_rows_requested": requested,
        "per_comment_rows_returned": returned,
        "noise_rows": noise_rows,
        "answered_only_in_noise": only_noise,
        "in_both_lists": both,
        "in_both_lists_rule": (
            "ids the reader wrote into `per_comment` AND `noise`, breaking the prompt's own «a"
            " comment belongs to at most one of the two». The parser does not refuse it by design —"
            " two rows about one comment are each readable — so it is COUNTED here instead of hidden"
            " inside the noise total"
        ),
        "tokens_per_requested_row": round(completion_parsed / requested, 2),
        "tokens_per_requested_row_rule": (
            "completion tokens over the PARSED threads divided by the rows those threads were asked"
            " for — v4's own published 137.83. The seconds-per-token rate above uses every billed"
            " thread instead, because a refused reply still cost its seconds"
        ),
        "union_coverage": (
            "MEASURED here and it changes what the echo duty is for: over the 19 parsed threads"
            f" `per_comment` ∪ `noise` answers {returned + only_noise} of {requested} requested ids"
            f" with nothing extra and nothing absent ({returned} in `per_comment`, {only_noise} only"
            f" in `noise`, {both} in both). v4's own report reads the 93/111 split as one"
            " row in six not written; it is not, and the shortfall the duty exists to close is ZERO"
            " on this evidence. What is left is a CLASSIFICATION question — one thread"
            " (@matusi_ukr:22242) answered wholly as noise ([[count_the_kind_not_the_rows]])"
        ),
    }


def output_model() -> dict:
    """Completion tokens as a function of answered rows, fitted on v4's own threads.

    Fitted on the threads that answered every id in `per_comment` and none in `noise`, because a
    noise row is a two-field object and a `per_comment` row is a six-field one: mixing them would
    price the wrong shape. The pessimistic reading is the fit plus its LARGEST residual — a bound
    and not a forecast, which is what a ceiling has to be set from.
    """
    rows = [row for row in v4_rows() if row["parsed"] and not row["parsed"]["noise"]]
    points = [
        (
            len(row["parsed"]["per_comment"]),
            int((row.get("usage") or {}).get("completion_tokens") or 0),
        )
        for row in rows
    ]
    n = len(points)
    sx, sy = sum(x for x, _ in points), sum(y for _, y in points)
    sxx, sxy = sum(x * x for x, _ in points), sum(x * y for x, y in points)
    marginal = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    envelope = (sy - marginal * sx) / n
    residual = max(y - (envelope + marginal * x) for x, y in points)
    return {
        "fitted_on": n,
        "fitted_on_rule": (
            "the v4 threads that answered every id in `per_comment` and none in `noise` — a noise"
            " row is two fields and a per_comment row is six, so a fit over both would price a shape"
            " this run does not send"
        ),
        "envelope_tokens": round(envelope, 1),
        "tokens_per_row": round(marginal, 2),
        "largest_residual_tokens": round(residual, 1),
        "pessimistic_rule": (
            "the fit PLUS its largest residual, which is a bound rather than a forecast. A ceiling"
            " set at the central fit would be exceeded by any thread as talkative as the most"
            " talkative one v4 actually paid for"
        ),
    }


def tokens_for(rows: int, model: dict, pessimistic: bool = True) -> float:
    extra = model["largest_residual_tokens"] if pessimistic else 0.0
    return model["envelope_tokens"] + extra + model["tokens_per_row"] * rows


def ceiling_block(model: dict, reading: dict, leg_a: dict, chunks: list[int]) -> dict:
    """Why 2 000 does not survive v5, unit by unit, with both readings printed."""
    units = [
        {"unit": one["thread"], "leg": "A", "rows": one["payable_comments"]}
        for one in leg_a["enumeration"]["threads"]
    ] + [
        {"unit": f"{LEG_B_THREAD} part {index + 1} of {len(chunks)}", "leg": "B", "rows": size}
        for index, size in enumerate(chunks)
    ]
    for one in units:
        one["central_tokens"] = round(tokens_for(one["rows"], model, pessimistic=False))
        one["pessimistic_tokens"] = round(tokens_for(one["rows"], model))
        one["over_2000_pessimistic"] = one["pessimistic_tokens"] > 2000
    worst = max(units, key=lambda one: one["pessimistic_tokens"])
    largest = max(
        (row for row in v4_rows()),
        key=lambda row: int((row.get("usage") or {}).get("completion_tokens") or 0),
    )
    return {
        "registered": OUTPUT_CEILING,
        "superseded": 2000,
        "rule": (
            "the ceiling must exceed the PESSIMISTIC corner of the largest unit this run sends —"
            f" {worst['unit']} at {worst['rows']} rows, {worst['pessimistic_tokens']} tokens. It is"
            f" set at {OUTPUT_CEILING}, which is"
            f" {OUTPUT_CEILING / worst['pessimistic_tokens']:.2f}x that corner and a doubling of"
            " v4's rather than a number tuned to a fit"
        ),
        "why_it_moves": (
            "v4's ceiling never fired — `finish_reason: length` on 0 of 23 — and that is not the"
            " same as having room. Its largest reply is"
            f" {int((largest.get('usage') or {}).get('completion_tokens') or 0)} tokens on"
            f" {largest['thread']}, 97.3% of 2 000, at 10 answered rows. v5 asks for more from the"
            " same threads (an id echoed for every comment, a second msg_id in the evidence of an"
            " exchange, a longer `reading` under the attribution block) and leg B asks a 16-row"
            " chunk for sixteen rows at once. A ceiling that fires truncates a verdict, and a"
            " truncated verdict fails a bar for a transport reason and spends the one attempt on it"
        ),
        "both_legs": (
            "ONE ceiling for leg A and leg B. Two ceilings in one run would make them two"
            " instruments, which is worse than either value"
        ),
        "cost_of_raising_it": (
            "seconds, and only where the model would have run past the old ceiling — the transport"
            " stops generation at the first balanced object, so a well-formed answer ends at its"
            " closing brace whatever the ceiling is. The runaway corner is priced in `money`"
        ),
        "model": model,
        "measured_rate": {
            "tokens_per_second_mean": reading["tokens_per_second_mean"],
            "tokens_per_second_slowest_thread": reading["tokens_per_second_slowest_thread"],
            "rule": (
                "v4's own 23 threads on the same card at batch 1, greedy. The SLOWEST thread's rate"
                " is what every seconds projection below divides by"
            ),
        },
        "units": units,
        "units_over_2000": sum(1 for one in units if one["over_2000_pessimistic"]),
    }


def leg_a_population() -> dict:
    """reader-v4's population, unchanged — the digest copied, the renderings RE-DERIVED under v5.

    The digest is over `channel:post_id\\tgated|injected\\tpayable msg_ids` and carries no rendering,
    so it does not move when the prompt does — which is exactly why it is the pin the pairing rests
    on. The per-thread `rendering_sha256` DOES move and must: the model is shown a different text
    ([[a_hash_is_not_the_claim_it_carries]]).
    """
    block = v3.population_block()
    for one in block["enumeration"]["threads"]:
        thread = next(
            candidate
            for candidate in subset.population()
            if subset.key(candidate["channel"], candidate["post_id"]) == one["thread"]
        )
        one["rendering_sha256"] = v2writer.rendering_sha256(thread, prompts.READER_TASK_V5)
        one["rendered_chars"] = len(v2writer.rendering(thread, prompts.READER_TASK_V5))
    block["renderings_rule"] = (
        "the per-thread request shas are RE-DERIVED under `reader_thread_gm4_v5` and are"
        " deliberately different from v4's: the same thread shown a different instrument is a"
        " different request. The population DIGEST is unchanged and copied, because it is over the"
        " threads and their payable ids and carries no rendering — that is what keeps this leg"
        " paired to probe-b and to reader-v4"
    )
    return block


def leg_b_thread() -> dict:
    """`@klopotenkofood:6040` out of the reader's own census cell, enumerated and never typed."""
    for one in reader_cell.population():
        if subset.key(one["channel"], one["post_id"]) == LEG_B_THREAD:
            return one
    raise SystemExit(
        f"{LEG_B_THREAD} is not in {reader_cell.CELL}. Leg B's thread has to come out of the"
        " census the registration pins, not out of a list somebody typed — stop and report."
    )


def leg_b_population(thread: dict) -> dict:
    """The chunked leg: one thread, 43 payable ids, three parts, each with its own request sha."""
    msg_ids = [row["msg_id"] for row in thread["comments"]]
    parts = reader_v5.chunks(msg_ids, LEG_B_CHUNK)
    texts = {row["msg_id"]: row["text"] for row in thread["comments"]}
    whole = prompts.reader_messages_gm4(
        thread["channel"],
        thread["post_id"],
        thread["post_text"],
        [(one, texts[one]) for one in msg_ids],
        task=prompts.READER_TASK_V5,
    )[0]["content"]
    items = []
    for index, ids in enumerate(parts, start=1):
        content = prompts.reader_messages_gm4(
            thread["channel"],
            thread["post_id"],
            thread["post_text"],
            [(one, texts[one]) for one in ids],
            task=prompts.READER_TASK_V5,
            part=(index, len(parts)),
        )[0]["content"]
        items.append(
            {
                "id": f"{LEG_B_THREAD}#{index}of{len(parts)}",
                "part": [index, len(parts)],
                "msg_ids": ids,
                "payable_comments": len(ids),
                "rendered_chars": len(content),
                "rendering_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            }
        )
    line = "\n".join(
        f"{LEG_B_THREAD}\t{one['part'][0]}of{one['part'][1]}\t"
        + ",".join(str(msg_id) for msg_id in one["msg_ids"])
        for one in items
    )
    return {
        "class": (
            "ONE thread, bought to prove the CHUNKING MECHANISM and nothing else. It carries no"
            " semantic gold, it is not in the reference, and no bar of leg A can be moved by it —"
            " its own bars are MECHANICAL and are listed apart"
        ),
        "thread": LEG_B_THREAD,
        "channel": thread["channel"],
        "post_id": thread["post_id"],
        "payable_comments": len(msg_ids),
        "msg_ids": msg_ids,
        "chunk_size": LEG_B_CHUNK,
        "chunks": [len(one) for one in parts],
        "items": items,
        "digest": hashlib.sha256(line.encode("utf-8")).hexdigest(),
        "digest_rule": (
            "sha256 over `thread\\tiofn\\tthis part's msg ids` per part, in order. Its OWN pin: leg"
            " A's digest is probe-b's and folding this thread into it would move that pin and end"
            " the pairing three runs rest on"
        ),
        "source": {
            "record": summary.rel(reader_cell.OUT),
            "sha256": summary.sha256_of(reader_cell.OUT),
            "cell": reader_cell.CELL,
            "rule": (
                "enumerated out of the reader's own census cell, never typed. The cell's four"
                " largest threads carry 125, 108, 105 and 43 payable comments and this is the"
                " fourth: big enough that ≤16 really chunks it three ways, small enough that one"
                " failed chunk is not the whole cap"
            ),
        },
        "renders_whole_under_the_ceiling": {
            "chars": len(whole),
            "ceiling": prompts.READER_MAX_INPUT_CHARS,
            "reading": (
                "this thread does NOT need chunking — whole, it renders well inside the input"
                " ceiling. It is chunked because the MECHANISM is what is being bought, before the"
                " window's 125/108/105-comment threads are sent through it. Registered here so"
                " nobody reads the three parts as a necessity"
            ),
        },
    }


def mechanical_bars(leg_b: dict) -> dict:
    """Leg B's four bars. Mechanical by ruling — none of them reads a gold cell."""
    return {
        "m1_every_payable_id_exactly_once": {
            "rule": (
                "the union of the parts' `per_comment` and `noise` msg_ids equals EXACTLY the"
                f" {leg_b['payable_comments']} payable ids of {LEG_B_THREAD}, with no duplicate"
                " across parts and no id that was not sent"
            ),
            "scorer": "market_pulse.reader_v5.echo, per part, then the merge",
            "threshold": f"{leg_b['payable_comments']} of {leg_b['payable_comments']}, 0 extra, 0 duplicated",
            "counts_both_lists": (
                "because v4's evidence says the model answers every id and chooses WHICH list —"
                " 111 of 111 covered, 93 in `per_comment` and 18 in `noise`. A bar over"
                " `per_comment` alone would fail the reader for obeying the prompt's own «a comment"
                " belongs to at most one of the two»"
            ),
        },
        "m2_every_chunk_finished": {
            "rule": (
                "`finish_reason` is `stop` on every chunk — no chunk ran to the output ceiling. With"
                " the transport stopping at the first balanced object, `length` means the reply"
                " never balanced at all"
            ),
            "threshold": f"{len(leg_b['chunks'])} of {len(leg_b['chunks'])}",
            "reachability": (
                f"registered against an output ceiling of {OUTPUT_CEILING} tokens. At 2 000 this bar"
                " is not reachable by arithmetic: a 16-row chunk's pessimistic answer is over it,"
                " and a bar that fails before the model is asked measures nothing"
                " ([[an_absolute_bar_needs_a_reachability_state]])"
            ),
        },
        "m3_every_chunk_parses": {
            "rule": "`prompts.parse_reply` returns a verdict for every chunk — 0 refusals",
            "threshold": f"{len(leg_b['chunks'])} of {len(leg_b['chunks'])}",
        },
        "m4_the_merge_has_no_duplicate_signal": {
            "rule": (
                "after `market_pulse.reader_v5.merge`, no two signals are identical on the dedupe"
                f" key {list(reader_v5.SIGNAL_KEY)} — the merge either folded them or they differ"
            ),
            "scorer": "market_pulse.reader_v5.merge",
            "threshold": "0 duplicate keys",
        },
        "cannot_touch_leg_a": (
            "these four are the ONLY bars leg B produces, and none of them reads gold, the"
            " reference or a flagship. Leg B's rows never enter bars 1-4, never enter the"
            " completeness census of leg A, and never enter a production aggregate"
        ),
    }


def money(reading: dict, model: dict, leg_a: dict, leg_b: dict) -> dict:
    """The cap as a stopwatch, at the worked example price — and every leg of it recomputed here."""
    rate = CARD_USD_PER_HOUR_EXAMPLE / 3600.0
    cap_seconds = CAP_USD / rate
    usable = cap_seconds - DELETE_MARGIN_S
    slow = float(reading["tokens_per_second_slowest_thread"])

    rows_a = [one["payable_comments"] for one in leg_a["enumeration"]["threads"]]
    tokens_a = sum(tokens_for(one, model, pessimistic=False) for one in rows_a)
    growth = tokens_a / reading["completion_tokens"]
    floor_a = reading["seconds_per_thread"] * len(rows_a)
    projection_a = max(floor_a * growth, tokens_a / slow)

    tokens_b_rule = float(reading["tokens_per_requested_row"]) * leg_b["payable_comments"]
    tokens_b_model = sum(tokens_for(one, model, pessimistic=False) for one in leg_b["chunks"])
    projection_b = max(tokens_b_rule, tokens_b_model) / slow

    projection = projection_a + projection_b
    pre_generation = usable - BOOT_KILL_S - projection
    affordability = usable - projection
    return {
        "cap_usd_all_in": CAP_USD,
        "cap_rule": (
            "the operator's ruling of 2026-08-17. v4 read 23 threads for $0.236118 of step resources"
            " under a $0.35 cap; this run adds a second leg, a longer output and a raised token"
            " ceiling, and the cap is raised ONCE and named"
        ),
        "guard": (
            f"scripts/runpod_guard.py --step reader-v5 --step-cap {CAP_USD}, anchored BEFORE the pod"
            " is created and read from the guard, never from a ledger line or a sentence in a"
            " contract"
        ),
        "meter": {
            "resource": (
                "ONE rented pod, billed for every second it EXISTS — from `pod create` to `pod"
                " delete`, provisioning and idle included. `pod stop` does not stop the bill, so the"
                " run deletes and never stops"
            ),
            "card_requested": CARD,
            "datacenter": "EU-RO-1, pinned by network volume qw4nwleanc — the volume decides",
            "price_rule": (
                "**READ ON THE DAY.** `runpodctl gpu list`, EU-RO-1 SECURE, before the pod is"
                " created; `costPerHr` in the create response is the meter of record. Every figure"
                " in this block is recomputed from IT before the generation process starts, and a"
                " projection that no longer fits deletes the pod and STOPS. Dv448 is why this clause"
                " exists: reader-v4's contract worked its example at $0.59/h and the card read"
                " $0.74/h on the day"
            ),
            "worked_example_usd_per_hour": CARD_USD_PER_HOUR_EXAMPLE,
            "worked_example_rule": (
                f"${CARD_USD_PER_HOUR_EXAMPLE:.2f}/h is what EU-RO-1 SECURE offered on 2026-08-16"
                " and it is used below so the arithmetic is WORKED rather than described. It is an"
                " EXAMPLE and not the meter"
            ),
            "usd_per_second_at_the_example": round(rate, 9),
        },
        "arithmetic": {
            "seconds_the_cap_buys": round(cap_seconds, 3),
            "delete_margin_seconds": DELETE_MARGIN_S,
            "usable_seconds": round(usable, 3),
            "v4_measured": {
                "seconds_per_thread": reading["seconds_per_thread"],
                "completion_tokens": reading["completion_tokens"],
                "tokens_per_second_slowest_thread": slow,
                "rule": (
                    "v4's own 23 threads on this card. probe-b's 31.6376 s a thread is NOT the floor"
                    " any more — it was measured under a shorter output and v4 measured"
                    f" {reading['seconds_per_thread']} on the same threads under v3's"
                ),
            },
            "leg_a": {
                "threads": len(rows_a),
                "payable_comments": sum(rows_a),
                "floor_seconds": round(floor_a, 1),
                "floor_rule": (
                    f"{len(rows_a)} x {reading['seconds_per_thread']} s — v4's own measurement on"
                    " exactly these threads, and the contract's registered FLOOR"
                ),
                "projected_tokens": round(tokens_a),
                "growth_vs_v4": round(growth, 3),
                "projection_seconds": round(projection_a, 1),
                "projection_rule": (
                    "the pessimistic of two: the measured floor scaled by the output growth the"
                    " token model predicts, and the projected tokens divided by the SLOWEST"
                    " per-thread rate v4 measured"
                ),
            },
            "leg_b": {
                "payable_comments": leg_b["payable_comments"],
                "chunks": leg_b["chunks"],
                "tokens_by_the_contracts_rule": round(tokens_b_rule),
                "tokens_by_the_row_model": round(tokens_b_model),
                "projection_seconds": round(projection_b, 1),
                "projection_rule": (
                    f"the pessimistic of two: {reading['tokens_per_requested_row']} tokens per"
                    f" requested row x {leg_b['payable_comments']} rows (the contract's own rule),"
                    " and the row model over the three chunks — divided by the slowest measured"
                    " rate. Per-chunk PREFILL is priced at zero and that is measured, not assumed:"
                    " a least-squares fit of v4's seconds on its completion tokens has an intercept"
                    " of -0.39 s, inside the noise, so a prefill is not a separate leg on this stack"
                ),
                "estimate_not_a_measurement": (
                    "no chunked request has ever been sent on this stack, so this leg is an ESTIMATE"
                    " with its own gate: the full-pass inequality is re-checked after every chunk"
                    " exactly as it is after every thread"
                ),
            },
            "reading_projection_seconds": round(projection, 1),
            "boot_kill_seconds": BOOT_KILL_S,
            "boot_kill_usd_at_the_example": round(BOOT_KILL_S * rate, 4),
            "boot_deadline_rule": (
                "min(boot_kill_seconds, usable_seconds − seconds since `pod create` − reading"
                " projection). Both numbers are printed at the gate and both land in the run record"
            ),
            "pre_generation_budget_seconds": round(pre_generation, 3),
            "pre_generation_rule": (
                "the create-elapsed above which the twelve-minute ceiling stops being the binding"
                " number. It is smaller than v4's 195.0 s because the reading projection is bigger,"
                " and here it is NEGATIVE: the affordability deadline binds from the first second."
                " That is a legal state and not an error — it says the twelve-minute ceiling never"
                " gets to be the binding number on this run, and the gate prints which of the two"
                " bound. It is NOT an elapsed and the table below does not use it as one"
            ),
            "affordability_deadline_as_create_elapsed": round(affordability, 1),
            "affordability_rule": (
                "usable_seconds − the reading projection. The FIRST reply must have landed by this"
                f" create-elapsed, and it is {round(affordability, 1)} s against the twelve-minute"
                f" ceiling's {BOOT_KILL_S:.0f} s — so the tighter one is affordability, always, on"
                " this registration"
            ),
            "pre_generation_measured_v4_seconds": V4_PRE_GENERATION_S,
            "pre_generation_measured_rule": (
                "reader-v4's own: `pod create` 18:00:12Z to the generation process's first line"
                " 18:00:51Z. The table below is worked at THIS number, because it is the only"
                " measurement of that leg this stack has"
            ),
            "at_each_boot": [
                {
                    "boot_seconds": boot,
                    "seconds_left_for_reading": round(usable - V4_PRE_GENERATION_S - boot, 1),
                    "times_the_projection_that_fits": round(
                        (usable - V4_PRE_GENERATION_S - boot) / projection, 3
                    ),
                    "fits": usable - V4_PRE_GENERATION_S - boot >= projection,
                    "all_in_usd_at_the_example": round(
                        (V4_PRE_GENERATION_S + boot + projection) * rate, 4
                    ),
                }
                for boot in BOOT_TABLE_S
            ],
            "at_each_boot_rule": (
                "worked at v4's MEASURED pre-generation leg, and a table rather than a forecast. Four boots are on record for this stack and they"
                " disagree by 6.7x — probe-a 373 s, probe-b 179 s, reader-v3 over 1 200 s, reader-v4"
                " 175.1 s"
            ),
            "runaway_corner": {
                "leg_b_seconds": round(len(leg_b["chunks"]) * OUTPUT_CEILING / slow, 1),
                "leg_a_seconds": round(len(rows_a) * OUTPUT_CEILING / slow, 1),
                "rule": (
                    "what the raised ceiling costs if NOTHING ever balances and every unit runs to"
                    " it. Leg A's corner is far past the cap, and that is the GATE's job and not the"
                    " ceiling's: the full-pass inequality is re-checked after every unit and deletes"
                    " the pod before the cap is reached rather than after"
                ),
            },
        },
    }


def go_no_go(reading: dict) -> dict:
    """v4's three gates, kept, with the one lesson v4's own record left behind: gates APPEND."""
    older = json.loads(summary.read_text_or_refuse(SUPERSEDES))["go_no_go"]
    return {
        "clock": older["clock"],
        "gates": {
            "1_staging": {
                "expected_usd": 0.0,
                "rule": (
                    "the volume carries a checkout of this repo and `src/` HAS moved since"
                    " reader-v4: v5 registers a fourth reader text. The run re-stages, then VERIFIES"
                    " the four reader prompt shas and the parser module's sha on the pod. A"
                    " verification that fails deletes the pod and STOPS"
                ),
                "differs_from_v4": (
                    "v4 expected to re-stage nothing. This run MUST re-stage, because the"
                    " instrument moved — and the handshake is what proves the staging worked rather"
                    " than the staging command's exit code"
                ),
            },
            "2_boot_kill": older["gates"]["2_boot_kill"],
            "3_the_full_pass": older["gates"]["3_the_full_pass"]
            | {
                "unit": (
                    "a UNIT is one request: a leg-A thread or a leg-B chunk. The two legs are"
                    " projected apart, because a chunk is not a thread and one rate over both would"
                    " price neither"
                ),
                "order": (
                    "leg A first, whole, then leg B. A stop inside leg A leaves leg B unbought and"
                    " scores no bar; a stop inside leg B leaves leg A COMPLETE and its four bars"
                    " scored, which is the ordering that makes a partial run worth something"
                ),
            },
        },
        "gate_records_APPEND": (
            "the run record keeps `gates` as a LIST and every WAIT/GO/KILL snapshot is appended,"
            " none overwritten. reader-v4's record overwrote: its first GO snapshot was displaced by"
            " the re-gate at twelve threads, the arithmetic had to be re-checked by hand against the"
            " jsonl, and it agreed — which is luck and not a property ([[the_marker_is_written_last]])"
        ),
        "backstop": {
            "terminate_after_minutes": TERMINATE_AFTER_MIN,
            "rule": (
                "passed at create. NOT a cap guard — 90 minutes at the worked example is"
                f" ${TERMINATE_AFTER_MIN * 60 * CARD_USD_PER_HOUR_EXAMPLE / 3600:.2f}, over two"
                " caps. It is what deletes the pod if this Mac dies with the run open"
            ),
        },
        "stop_rule": older["stop_rule"],
        "seconds_v4_measured": reading["seconds_per_thread"],
    }


def bars(older: dict, leg_b: dict) -> dict:
    """Bars 1-4 object-equal to v4's, bar 5 re-priced, and leg B's four beside them."""
    table = {
        name: older["bars"][name] for name in sorted(older["bars"]) if name != "5_time_and_cost"
    }
    table["5_time_and_cost"] = {
        "rule": (
            "one pod, billed for every second it exists. The gates below stop it; this bar is what"
            " the guard's CLOSED step ledger says afterwards"
        ),
        "thresholds": {"cap_usd_all_in": CAP_USD},
        "reported_not_gating": older["bars"]["5_time_and_cost"]["reported_not_gating"]
        | {
            "cut_chars": (
                "per unit — how many characters the transport stop removed. It is the measurement"
                " ruling (b) was bought for and it gates nothing"
            ),
            "balanced": "per unit — whether the reply closed a top-level object at all",
        },
    }
    table["leg_b_mechanical"] = mechanical_bars(leg_b)
    return table


def build() -> dict:
    older = json.loads(summary.read_text_or_refuse(SUPERSEDES))
    reading = v4_reading()
    model = output_model()
    leg_a = leg_a_population()
    thread = leg_b_thread()
    leg_b = leg_b_population(thread)
    ceilings = ceiling_block(model, reading, leg_a, leg_b["chunks"])
    return {
        "phase": "reader-v5",
        "contract": "docs/PROMPT-reader-v5-prep.md D3",
        "class": (
            "PRE-REGISTRATION. Committed before the pod exists; git history is the only witness that"
            " it preceded the money. It FREEZES when the run contract's pod exists and nothing after"
            " that may edit it — a registration a run may amend is a registration the run wrote"
        ),
        "attempt": older["attempt"],
        "programme_stop_rule": (
            "**If this run COMPLETES and bars 1 and 4 are not BOTH taken, the prompt-engineering"
            " line CLOSES.** The next step is an architecture sitting — two passes, labelled data, a"
            " different base — and never a v6 of the same kind. The operator's ruling of 2026-08-17,"
            " pre-registered here so it binds the reading of this run's own result and cannot be"
            " re-decided once the numbers are in"
        ),
        "supersedes": {
            "record": summary.rel(SUPERSEDES),
            "sha256": summary.sha256_of(SUPERSEDES),
            "state": (
                "v4 stays FROZEN and is not withdrawn: it is the record of the attempt that MEASURED"
                " the layer, its step closed at $0.236118 and three of its five bars passed"
            ),
            "ruling": "the sitting of 2026-08-17, after reader-v4 was accepted as an honest negative",
            "what_it_changes": [
                "the prompt: seven `_swap` pairs over v3, registered as reader_thread_gm4_v5",
                "the transport: generation stops at the first balanced top-level JSON object",
                "the render: an optional chunk header, and a second LEG that uses it",
                f"the output ceiling: 2000 -> {OUTPUT_CEILING} tokens, both legs",
                "the cap: $0.35 -> $0.45, one pod, kill rule as code",
                "gate records APPEND instead of overwriting",
            ],
            "what_it_keeps": (
                "gold r2, the population digest, bars 1-4 with their thresholds and their scoring"
                " rule, the symmetric vocabulary collapse, N1's exclusion with v2's cause, the"
                " scorer's bytes and the serving configuration. Everything that could make v4 and v5"
                " incomparable is held still on purpose"
            ),
            "v4_verdict": {
                "record": summary.rel(V4_VERDICT),
                "sha256": summary.sha256_of(V4_VERDICT),
                "reading": "three bars of five passed; 1 and 4 failed and are what v5 exists for",
            },
        },
        "authority": {
            summary.rel(path): summary.sha256_of(path)
            for path in (v3.PLAN, CONTRACT, v3.REFERENCE, SUPERSEDES, v3.GOLD_R2, v3.CENSUS_CELL)
        },
        "instruments": {
            "task": prompts.READER_TASK_V5,
            "instruments_rule": (
                "RE-DERIVED, which is the INVERSE of v4's rule. v4 copied v3's whole `instruments`"
                " block because nothing about what is measured had moved; here the task, the prompt"
                " map, the parser's behaviour and the output ceiling all move, so a copy would be a"
                " claim that is false in four places. What is copied is copied OBJECT-EQUAL and"
                " named below"
            ),
            "prompt_sha256": {task: prompts.prompt_sha256(task) for task in sorted(prompts.READER)},
            "prompt_rule": (
                "a sha per reader text registered at the moment this record was written — FOUR of"
                " them, numbered 1, 2, 3 and 5. There is no v4 text: reader-v4 registered the v3"
                " text on a pod, and the number follows the contract that registers a text. A text"
                " registered LATER is not in this map and is not expected to be; the pod's handshake"
                " compares the tasks THIS map pins, one by one, and the module sha separately"
            ),
            "v5_changes": {
                "prompt": (
                    "SEVEN `_swap` calls from v3 in src/market_pulse/prompts.py — attribution,"
                    " aspect contrast, the exchange's two msg_ids, the narrow F2a carve-out, one"
                    " vocabulary, the echo duty, the chunk header. Every example in them is"
                    " SYNTHETIC and tests/test_reader_prompt_v5.py proves it occurs in no stored"
                    " comment, no stored post, neither gold and not in the reference"
                ),
                "transport": (
                    "generation STOPS at the first balanced top-level JSON object; brace depth is"
                    " counted outside string literals with escapes handled, and the persisted raw"
                    " reply is exactly the emitted prefix. Two of v4's four refusals were `two"
                    " disagreeing objects` and this is the cure; the v3 prompt line and the parser's"
                    " refuse-on-conflict clause stay as defence"
                ),
                "render": (
                    "`prompts.reader_messages_gm4` gains `part=(i, n)`, default None. The default"
                    " path renders BYTE-IDENTICALLY — proven on reader-v4's own 23 registered"
                    " request shas, 23 of 23"
                ),
                "parser": (
                    "UNCHANGED for a reply. `prompts.parse_reply` is not touched: strict domains,"
                    " the three container repairs and refuse-on-conflict are exactly v3's."
                    " market_pulse.reader_v5 adds `echo` (the completeness census) and `merge` (the"
                    " chunk join) over what it returned, never inside it"
                ),
                "ceiling": (
                    f"`max_new_tokens` 2000 -> {OUTPUT_CEILING}, computed and not chosen — see"
                    " `ceilings`"
                ),
            },
            "parser": older["instruments"]["parser"]
            | {
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
                "unchanged_behaviour": (
                    "the module's BYTES moved (the v5 text lives in it) and its behaviour for a"
                    " reply did not. Every refusal and every repair named above is v3's, and the v5"
                    " suite drives them under the v5 task"
                ),
                "v5_additions": {
                    "module": "src/market_pulse/reader_v5.py",
                    "sha256": summary.sha256_of(
                        REPO_ROOT / "src" / "market_pulse" / "reader_v5.py"
                    ),
                    "balanced_prefix": "the transport stop, as a pure function over text",
                    "echo": (
                        "the completeness census, counting THREE states: answered in `per_comment`,"
                        " answered in `noise`, absent. Only `absent` is a shortfall"
                    ),
                    "merge": (
                        "the chunk join — `per_comment` and `noise` concatenated in chunk order with"
                        " the partition VERIFIED, `signals` deduped on"
                        f" {list(reader_v5.SIGNAL_KEY)} with evidence unioned, `entities` deduped by"
                        " (name, msg_id)"
                    ),
                },
            },
            "ceilings": {
                "input_chars": prompts.READER_MAX_INPUT_CHARS,
                "input_rule": older["instruments"]["ceilings"]["input_rule"],
                "output_tokens": OUTPUT_CEILING,
                "output_arithmetic": ceilings,
            },
            "gold": older["instruments"]["gold"],
            "scorer": older["instruments"]["scorer"],
            "serving": older["instruments"]["serving"] | {"output_tokens": OUTPUT_CEILING},
            "serving_rule": older["instruments"]["serving_rule"],
            "copied_object_equal_from_v4": [
                "instruments.gold",
                "instruments.scorer",
                "instruments.serving (plus output_tokens)",
                "bars 1-4 whole",
                "scoring_rules.vocabulary_collapse",
            ],
        },
        "population": {
            "leg_a": leg_a,
            "leg_b": leg_b,
            "two_legs_rule": (
                "leg A produces bars 1-4 and 5; leg B produces its four MECHANICAL bars and 5. No"
                " row of leg B enters a bar of leg A, the completeness census of leg A, gold, or a"
                " production aggregate — and no bar of leg A is scored on fewer than all 23 threads"
            ),
        },
        "money": money(reading, model, leg_a, leg_b),
        "go_no_go": go_no_go(reading),
        "bars": bars(older, leg_b),
        "scoring_rules": older["scoring_rules"],
        "completeness": {
            "rule": (
                "REPORTED beside the bars and NEVER gating bars 1-4. Per thread: rows requested,"
                " answered in `per_comment`, answered in `noise`, and the absent ids NAMED"
            ),
            "scorer": "market_pulse.reader_v5.echo",
            "why_not_a_bar": (
                "because on v4's evidence the shortfall it would measure is ZERO — `per_comment` ∪"
                " `noise` covers 111 of 111 requested ids — so a bar over it would score a number"
                " that is already taken. What the census is for is telling three states apart, which"
                " is what v4's 93/111 line could not do"
            ),
            "v4_baseline": reading,
        },
        "non_gating": [
            "`repairs` per verdict — the three container repairs fired 0 times over v4's 23 replies",
            "`cut_chars` and `balanced` per unit — what the transport stop actually removed",
            "`finish_reason` per unit against the raised ceiling",
            "seconds per unit, leg A against v4's own 39.461 s a thread on the same threads",
            "the completeness census, three states per thread",
        ],
        "transport": {
            "shape": (
                "the generation runs ON the pod and nothing else does. The units travel as a pack"
                " whose every entry is checked against this record's `rendering_sha256` on the Mac"
                " before it is sent and again on the pod before the model is loaded; the on-pod"
                " runner loads the READER config once, answers the units in order and stops each"
                " generation at the first balanced object, flushing one raw line as each lands."
                " Parsing, merging and scoring happen on the Mac"
            ),
            "persisted_per_row": [
                "the rendered request and its sha256",
                "the raw reply, byte for byte, cut at the balanced prefix",
                "`balanced`, `emitted_chars` and `cut_chars` — what the stop removed",
                "the parse outcome — the verdict with its `repairs`, or the refusal's reason",
                "seconds, `finish_reason` and the token usage",
            ],
            "flush_rule": older["transport"]["flush_rule"],
            "why_the_split": older["transport"]["why_the_split"],
        },
        "frozen_when_the_pod_exists": [
            "results/prereg_reader_probe_v5.json",
            summary.rel(v3.GOLD_R2),
            summary.rel(v3.CENSUS_CELL),
            summary.rel(SUPERSEDES),
            f"the {prompts.READER_TASK_V5} prompt text",
            "src/market_pulse/prompts.py — the parser",
            "src/market_pulse/reader_v5.py — the stop, the census and the merge",
            "src/market_pulse/scorer.py",
            "scripts/probe_b_population.py's enumeration",
        ],
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "borrowed": {
                name: summary.sha256_of(REPO_ROOT / name)
                for name in (
                    "scripts/gate_census_w1_reader.py",
                    "scripts/probe_b_population.py",
                    "scripts/window_summary_5c2.py",
                    "scripts/write_reader_prereg_v2.py",
                    "scripts/write_reader_prereg_v3.py",
                    "scripts/write_reader_prereg_v4.py",
                    "src/market_pulse/prompts.py",
                    "src/market_pulse/reader_v5.py",
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
    leg_a, leg_b = record["population"]["leg_a"], record["population"]["leg_b"]
    print(
        f"  leg A {leg_a['threads']} threads · {leg_a['payable_comments']} payable ·"
        f" digest {leg_a['enumeration']['digest'][:16]}…"
    )
    print(
        f"  leg B {leg_b['thread']} · {leg_b['payable_comments']} payable ·"
        f" chunks {leg_b['chunks']} · digest {leg_b['digest'][:16]}…"
    )
    ceilings = record["instruments"]["ceilings"]["output_arithmetic"]
    print(
        f"  output ceiling {ceilings['superseded']} -> {ceilings['registered']} tokens ·"
        f" {ceilings['units_over_2000']} of {len(ceilings['units'])} units over 2000 pessimistic"
    )
    sums = record["money"]["arithmetic"]
    print(
        f"  cap ${CAP_USD:.2f} buys {sums['seconds_the_cap_buys']:.1f} s ·"
        f" usable {sums['usable_seconds']:.1f} s"
    )
    print(
        f"  reading projection {sums['reading_projection_seconds']:.1f} s"
        f" (A {sums['leg_a']['projection_seconds']:.1f} + B {sums['leg_b']['projection_seconds']:.1f})"
        f" · pre-generation budget {sums['pre_generation_budget_seconds']:.1f} s"
    )
    for row in sums["at_each_boot"]:
        print(
            f"    boot {row['boot_seconds']:6.0f} s -> {row['seconds_left_for_reading']:7.1f} s for"
            f" reading ({row['times_the_projection_that_fits']:.3f}x the projection),"
            f" all-in ${row['all_in_usd_at_the_example']:.4f}"
        )
    print(f"  bars: {sorted(record['bars'])}")
    print(f"  STOP-RULE registered: {record['programme_stop_rule'][:78]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
