#!/usr/bin/env python3
"""`results/prereg_reader_probe.json` — the reader probe's registration, written before it can run.

**What a pre-registration is here.** The bars are the operator's word (`docs/PLAN-comment-signals.md`
§5, rulings of 2026-08-15); what this file adds is everything a bar needs before it can be a
measurement: the population as a LIST, the instruments by sha, the matching rules spelled out in
words, the go/no-go arithmetic, and — the part this contract could not have anticipated — which of
the operator's obligatory cases the pinned population is able to carry at all.

**It is committed before the endpoint exists, and git is the only witness to that order.** Nothing
here is a result. No clock is stamped, so the record re-derives byte for byte and its date is the
date of the commit that carries it ([[provenance_cannot_name_itself]]).

**The bars that shrank, and why that is not shrinking them.** Three of the four obligatory entity
cases and one of the six noise threads are outside the population `docs/PROMPT-probe-a.md` D3 pins:
the gate's own marker rule removes the thread's only lexicon hit before payment, so the reader is
never shown them. A bar of 4/4 over two reachable cases fails by arithmetic rather than by reading
([[an_absolute_bar_needs_a_reachability_state]]), so each bar is registered over the cases the
population can carry, with the unreachable ones named beside it and returned to the operator. One
more thread leaves bar 3 for the opposite reason: the reference's own secondary list reads a signal
inside it, and a bar that punished the reader for agreeing with the reference would measure nothing.

    PYTHONPATH=src python3 scripts/write_reader_prereg.py
    PYTHONPATH=src python3 scripts/write_reader_prereg.py --out /tmp/again.json   # the pair
"""

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import reader_population as population  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import local_llm, prompts  # noqa: E402

CONTRACT = REPO_ROOT / "docs" / "PROMPT-probe-a.md"
PLAN = REPO_ROOT / "docs" / "PLAN-comment-signals.md"
REFERENCE = REPO_ROOT / "docs" / "REFERENCE-signals-w1.md"
GOLD = REPO_ROOT / "results" / "reader_gold_w1.json"
PRICES = REPO_ROOT / "results" / "run_5c2_comments.json"
OUT = REPO_ROOT / "results" / "prereg_reader_probe.json"

WARM_UP = 3
WARM_UP_SEED = "probe-a warm-up · narrow|silencers_on · 2026-08-15"
"""The draw is 3 threads from the MIDDLE third of the population by size, and the seed says which
population and which draw it is. A seed that is only a number is reproducible and says nothing about
what it drew; put the stratum in it and a second draw over another stratum cannot silently reuse it
([[a_reproducible_draw_can_be_correlated]]).

The middle and never the head: a price named from the first threads of a sorted list is a price of
whatever that ordering put first."""

CAP_USD = 0.45
"""RAISED from the contract's $0.20 by the operator, 2026-08-15, after this session showed the
smaller cap cannot buy the registered run: $0.20 ÷ $0.00030669/s is 652 s of billed worker time, and
the census's own LOWER bound for the 111 threads (471 s) plus one measured weight load (99 s) plus a
staging pod ($0.032) is $0.2069 before the warm-up is priced ([[the_setup_is_inside_the_cap]]).

The raise moves the ceiling and nothing else. The go/no-go still fires against it, the stop is still
a legitimate outcome, and the phase cap behind it is untouched — `scripts/runpod_guard.py` read
$1.0923 remaining of $33.00 when this was written."""

WINDOW_MINUTES = 30.0
AGREEMENT_BAR = 0.80
"""The two ceilings the raise does NOT move, transcribed from the operator's rulings of 2026-08-15:
≤30 minutes billed for a full window, per-comment agreement ≥0.80. They live in this record because
a bar is a registration; the scorer computes numbers and holds no threshold at all."""


def middle_third(kept: list[dict]) -> list[dict]:
    """The population ordered by the size that drives its price, middle third only."""
    ordered = sorted(kept, key=lambda one: (len(one["comments"]), one["channel"], one["post_id"]))
    third = len(ordered) // 3
    return ordered[third : 2 * third + len(ordered) % 3]


def draw(kept: list[dict]) -> list[dict]:
    """The warm-up sample, with each thread's RANK in the whole population beside it.

    The rank is recorded because the draw's representativeness is a fact about where it landed, not
    about the seed that put it there: three threads all at the same rank would be reproducible and
    still be one measurement.
    """
    ordered = sorted(kept, key=lambda one: (len(one["comments"]), one["channel"], one["post_id"]))
    rank = {(one["channel"], one["post_id"]): index for index, one in enumerate(ordered)}
    band = middle_third(kept)
    picked = random.Random(WARM_UP_SEED).sample(band, WARM_UP)
    return [
        {
            "channel": one["channel"],
            "post_id": one["post_id"],
            "payable_comments": len(one["comments"]),
            "rank_by_size": rank[(one["channel"], one["post_id"])],
            "rendered_chars": len(rendering(one)),
        }
        for one in sorted(picked, key=lambda one: rank[(one["channel"], one["post_id"])])
    ]


def rendering(thread: dict) -> str:
    """One thread as the run will send it — the registered rendering, never a look-alike."""
    return prompts.reader_messages_gm4(
        thread["channel"],
        thread["post_id"],
        thread["post_text"],
        [(row["msg_id"], row["text"]) for row in thread["comments"]],
    )[0]["content"]


def sizes(kept: list[dict]) -> dict:
    payable = sorted(len(one["comments"]) for one in kept)
    chars = sorted(len(rendering(one)) for one in kept)

    def spread(values: list[int]) -> dict:
        return {
            "min": values[0],
            "median": values[len(values) // 2],
            "mean": round(sum(values) / len(values), 3),
            "max": values[-1],
            "total": sum(values),
        }

    return {"payable_comments": spread(payable), "rendered_chars": spread(chars)}


def population_digest(kept: list[dict]) -> str:
    """A digest over the LIST, so the pin is the population and not its size.

    `channel:post_id` and every payable msg_id, in the enumeration's own order. Re-derivable from
    `scripts/reader_population.py` at any time — this is a check on that code, not a substitute for
    it ([[reproducible_means_try_it]]).
    """
    body = "\n".join(
        f"{one['channel']}:{one['post_id']}\t"
        + ",".join(str(row["msg_id"]) for row in one["comments"])
        for one in kept
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def bars(gold: dict) -> dict:
    """The five bars, each over the cases the population can carry, each with its exclusions named."""
    reach = gold["reachability"]
    flagship_signals = [signal["id"] for case in gold["flagships"] for signal in case["signals"]]
    entity_out = {one["id"]: one["cause"] for one in reach["entity_cases"]["unreachable"]}
    noise_out = {one["id"]: one["cause"] for one in reach["noise_threads"]["unreachable"]}
    scored_rows = reach["per_comment"]["inside_the_population"]
    # the smallest agreement count that CLEARS the bar, computed rather than rounded: 0.80 of 13
    # rows is 10.4, and «10 of 13» is 0.769 — a threshold read off a percentage would pass it
    needed = next(
        count for count in range(len(scored_rows) + 1) if count / len(scored_rows) >= AGREEMENT_BAR
    )
    return {
        "1_flagships": {
            "rule": (
                "each of the reference's five flagship CASES is found when every gold signal it"
                " carries is found by scorer.reader_signal_found — evidence overlap, plus"
                " subject_type and aspect where the gold states them. signal_type is not compared"
                " and neither is subject_id"
            ),
            "threshold": "5 of 5 cases",
            "scored_over": reach["flagships"]["reachable"],
            "gold_signals": flagship_signals,
            "also_reported": (
                f"per-signal found/missed for all {len(flagship_signals)} gold signals, so the"
                " narrower reading of"
                " plan §5 (1) — which names five SIGNALS (F1a, F1b, F2a, F3a, F4a) and neither"
                " F1c nor F5 — can be read off the same table. The case reading is the stricter of"
                " the two and is the one registered"
            ),
            "scorer": "reader_signal_found",
        },
        "2_entity_cases": {
            "rule": (
                "an entity case is answered when the verdict for its thread carries an entity whose"
                " name or quote resolves to the case's brand_id through the watchlist matcher AND"
                " whose subject_type is the operator's ruling. E4 is the absence case: «чи варто» is"
                " the adverb, so the case is answered when NO entity in that thread names varto"
            ),
            "threshold": "2 of 2 reachable cases",
            "scored_over": reach["entity_cases"]["reachable"],
            "unreachable": entity_out,
            "the_contract_asked_for": "4 of 4",
            "why_it_cannot_be_4": (
                "E1 «Гармонія», E4a and E4b «чи варто» are in the window and NOT in the population:"
                " each passes the gate with no silencer running and is removed by the marker rule of"
                " SPEC 3.21 (1), which takes away the thread's only lexicon hit. The reader is never"
                " shown them, so 4/4 is unreachable by arithmetic and the missing three are a"
                " finding about the GATE, not about the reader"
            ),
            "scorer": "reader_entity_found",
        },
        "3_noise": {
            "rule": "zero signals in the verdicts of the reference's noise threads",
            "threshold": "0 signals",
            "scored_over": ["N2", "N4", "N5", "N6"],
            "unreachable": noise_out,
            "excluded_with_cause": {
                "N1": (
                    "the reference's own S list reads a signal inside this thread (S1, msg 21420,"
                    " «Половина товаров закончилась, гениально»), and the store shows two comments"
                    " there rather than the «десятки «+»» the N list describes — the plus-spam it"
                    " refers to was silenced before payment. A bar that failed the reader for"
                    " agreeing with the reference would measure nothing. The signal count for N1 is"
                    " reported beside the bar and gates nothing"
                )
            },
            "scorer": "reader_noise_count",
        },
        "4_per_comment_agreement": {
            "rule": (
                "each gold row is compared on the fields the reference STATES for it"
                " (`scored_fields`) and on no others; a gold row the reader wrote no per_comment"
                " entry for counts as a disagreement and is also counted separately as `absent`"
            ),
            "threshold": f"rate >= {AGREEMENT_BAR}",
            "scored_over": scored_rows,
            "arithmetic": (
                f"{len(scored_rows)} rows are inside the population, so the bar is {needed} of"
                f" {len(scored_rows)} ({needed / len(scored_rows):.3f}) — {needed - 1} agreements"
                f" scores {(needed - 1) / len(scored_rows):.3f} and fails"
            ),
            "unreachable": reach["per_comment"]["outside_the_population"],
            "scorer": "reader_comment_agreement",
        },
        "5_time_and_cost": {
            "rule": (
                "the warm-up measures billed worker seconds per thread; the window is projected two"
                " ways and the PESSIMISTIC one binds — per thread (mean seconds × 111) and per"
                " payable comment (seconds ÷ warm-up payable × 912). A rate is a property of the"
                " sample it was measured on, and a thread call is not a comment call"
            ),
            "thresholds": {
                "cap_usd_all_in": CAP_USD,
                "window_minutes_billed": WINDOW_MINUTES,
            },
            "prior": {
                "source": summary.rel(PRICES),
                "rate_usd_per_second": json.loads(summary.read_text_or_refuse(PRICES))[
                    "rate_usd_per_second"
                ],
                "reading": (
                    "the 5c2 comment run's measured rate, carried as the PRIOR only. The probe's"
                    " own rate is the one its endpoint bills, and it is what the projection uses"
                ),
            },
        },
    }


def build(kept: list[dict], gold: dict) -> dict:
    return {
        "phase": "probe-a",
        "contract": "docs/PROMPT-probe-a.md D3",
        "class": (
            "PRE-REGISTRATION. Committed before the endpoint exists; git history is the only"
            " witness to that order, and no clock is stamped so the record re-derives byte for"
            " byte. Nothing here is a result. A pre-registration is a registration and not law:"
            " the layer's amendment comes after adjudication"
        ),
        "authority": {
            summary.rel(path): summary.sha256_of(path) for path in (CONTRACT, PLAN, REFERENCE, GOLD)
        },
        "rulings": [
            "operator 2026-08-15: the taxonomy of plan §3 ratified — subject, signal and noise words",
            "operator 2026-08-15: per-comment agreement bar ≥ 0.80",
            "operator 2026-08-15: window reading time budget ≤ 30 minutes billed",
            "operator 2026-08-15: the gate is the narrow lexicon with its silencers; precision"
            " lives with the reader",
            "operator 2026-08-15, after the arithmetic of docs/reports/probe-a.md §5: the probe's"
            f" cap is raised from $0.20 to ${CAP_USD:.2f} all-in. Nothing else moves — the"
            " population, the instruments, the bars and the stop rule are the ones registered"
            " before it, and this record was re-derived and re-committed before any endpoint"
            " existed",
        ],
        "attempt": (
            "ONE attempt, no retry. A failed bar after a completed run closes the question by"
            " design review (plan §5). Anything this registration did not anticipate stops the run"
            " and is reported with the attempt intact"
        ),
        "population": {
            "record": summary.rel(population.CENSUS),
            "sha256": population.census_sha256(),
            "cell": population.CELL,
            "threads": len(kept),
            "payable_comments": sum(len(one["comments"]) for one in kept),
            "enumeration": {
                "producer": "scripts/reader_population.py",
                "sha256": summary.sha256_of(REPO_ROOT / "scripts" / "reader_population.py"),
                "digest": population_digest(kept),
                "digest_rule": (
                    "sha256 over `channel:post_id\\tpayable msg_ids` for every thread, in the"
                    " enumeration's order — the population pinned as a list rather than as a count"
                ),
            },
            "sizes": sizes(kept),
            "threads_with_no_payable_comment": [
                f"{one['channel']}:{one['post_id']}" for one in kept if not one["comments"]
            ],
        },
        "instruments": {
            "task": prompts.READER_TASK,
            "prompt_sha256": prompts.prompt_sha256(prompts.READER_TASK),
            "parser": {
                "module": "src/market_pulse/prompts.py",
                "function": "parse_reply",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
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
            },
            "gold": {"record": summary.rel(GOLD), "sha256": summary.sha256_of(GOLD)},
            "ceilings": {
                "input_chars": prompts.READER_MAX_INPUT_CHARS,
                "input_rule": (
                    "a LOUD refusal, never a truncation. The largest thread of this population"
                    f" renders to {max(len(rendering(one)) for one in kept)} characters, so the"
                    " guard cannot fire on a thread the probe is registered to read"
                ),
                "output_tokens": local_llm.READER_MAX_NEW_TOKENS,
                "output_rule": (
                    "a ceiling against a truncated verdict, not a target. A reply that uses it all"
                    " comes back `finish_reason: length` and is counted as a parse failure by"
                    " cause — never read as a thread with nothing in it"
                ),
                "threads_the_output_ceiling_may_truncate": [
                    f"{one['channel']}:{one['post_id']} ({len(one['comments'])} payable)"
                    for one in sorted(kept, key=lambda one: -len(one["comments"]))[:3]
                ],
            },
            "serving": {
                "serving_config": "READER",
                "merge_state": "base-no-adapter",
                "adapter": None,
                "adapter_note": (
                    "the reader is a NEW capability and the classification adapter stays out."
                    " `serve_handler.settings` refuses the whole ADAPTER_ENV set before the model"
                    " loads and `assert_no_adapter` refuses the loaded object — the environment and"
                    " the model are two different checks"
                ),
                "model": local_llm.MODEL_ID,
                "model_revision": "842da3794eaa0b77d5f08bae87a17459d91ff475",
                "quantization": dict(local_llm.QUANTIZATION),
                "chat_template": dict(local_llm.CHAT_TEMPLATE),
                "thinking_note": (
                    "`enable_thinking: false` is explicit and registered: a thinking-ON reader is a"
                    " NEW pre-registration and not a knob, and `parse_reply` reads from the first"
                    " brace it finds"
                ),
                "decoding": "greedy",
                "do_sample": False,
                "forward_batch_size": 1,
                "template_note": (
                    "a NEW serving template for the READER config. `settings()` refuses"
                    " config-mixing by design; the srv-2d and CAPTION templates are never edited"
                ),
            },
        },
        "bars": bars(gold),
        "go_no_go": {
            "pattern": "the (10)(a) go/no-go: measure a warm-up, project, and stop before the rest",
            "warm_up": {
                "threads": WARM_UP,
                "seed": WARM_UP_SEED,
                "rule": (
                    "the population ordered by payable comments, the MIDDLE third of that order,"
                    f" {WARM_UP} threads drawn from it by the seed above. Never the head: a"
                    " registered price names its sample"
                ),
                "drawn": draw(kept),
                "representativeness": (
                    "the drawn threads' payable counts are recorded beside the population's median"
                    " and maximum. A middle-third draw prices a median thread, and the per-payable"
                    " projection is what carries that price to the threads above it"
                ),
            },
            "stop_rule": (
                "if the binding projection exceeds either ceiling — the remaining cap or 30 minutes"
                " billed for the window — STOP before any further call. The attempt stays intact,"
                " the measured rate goes back to the operator, and no bar is scored on a partial run"
            ),
            "what_a_stop_costs": "the warm-up's own spend, and nothing else",
        },
        "money": {
            "cap_usd_all_in": CAP_USD,
            "includes": "the warm-up, the run, and every second the endpoint bills while it exists",
            "guard": (
                "scripts/runpod_guard.py before the endpoint is created, read from the guard and"
                " never from a ledger line (Dv33)"
            ),
        },
        "frozen_when_the_endpoint_exists": [
            "results/prereg_reader_probe.json",
            "results/reader_gold_w1.json",
            f"the {prompts.READER_TASK} prompt text",
            "src/market_pulse/scorer.py's four reader functions",
            "scripts/reader_population.py's enumeration",
        ],
        "non_gating": [
            "how many of the 111 the reader marks signal-bearing versus «нет сигнала», counted"
            " apart from replies that failed to parse — an unreadable reply is not a thread with no"
            " signal in it",
            "parse failures by reason, and how many were `finish_reason: length`",
            "signal types the reader proposed with `proposed: true`",
            "comments that appear in both `per_comment` and `noise` in one verdict",
            "entities resolved inside the noise threads",
            "the plan §5 (1) five-signal reading of bar 1, beside the five-case one",
            "signals raised in N1, the thread excluded from bar 3",
        ],
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "borrowed": {
                name: summary.sha256_of(REPO_ROOT / name)
                for name in (
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
    record = build(population.population(), gold)
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    print(
        f"  population {record['population']['threads']} threads ·"
        f" {record['population']['payable_comments']} payable · digest"
        f" {record['population']['enumeration']['digest'][:16]}…"
    )
    for name, bar in record["bars"].items():
        print(f"  bar {name:26s} {bar.get('threshold') or bar['thresholds']}")
    for one in record["go_no_go"]["warm_up"]["drawn"]:
        print(
            f"  warm-up {one['channel']}:{one['post_id']} — rank {one['rank_by_size']}/111 ·"
            f" {one['payable_comments']} payable · {one['rendered_chars']} chars"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
