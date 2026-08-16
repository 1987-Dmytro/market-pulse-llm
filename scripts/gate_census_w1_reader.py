#!/usr/bin/env python3
"""`results/gate_census_w1_reader.json` — the READER's own gate cell, measured and never derived.

**What this answers.** The reader sitting of 2026-08-16 (ruling 3) lifts SPEC 3.21 (1)'s marker
silencer for the reader path only: probe-b showed it is a determinism hygiene for the DISPLAY that
also acts as a payment gate for the reader — four of the operator's obligatory cases were never
shown to the model at all. Spam and scam threads stay in as well. That makes a cell the shipped
census does not carry: **narrow lexicon · `varto_rule` OFF · `plus_spam` + `scam` ON**.

**Measured, and that is the whole point of the clause.** The shipped record already holds
`narrow|silencers_off` at 129 threads and `each_alone.varto_rule` at 111, and the operator's word
puts the reader's window-1 population at 129. Arriving at this cell by arithmetic over two older
ones would produce a number no census on disk reproduces, which is exactly why ruling 3 says it is
MEASURED. The census's own `cell()` is called here, unedited and imported.

**Why a new file.** `results/gate_census_w1.json` is never rewritten: its own record pins
`producer.sha256`, `tests/test_gate_census_w1.py` re-derives the whole file, and
`results/prereg_reader_probe*.json` pin its bytes. A comment added to that producer would redden a
sealed record for a reason nobody could connect to it ([[a_comment_only_edit_moves_the_files_hash]]).

**The price is probe-b's, and it names its sample.** `gate_census_w1.price()` is deliberately NOT
reused: it reads `results/run_5c2_comments.json`, an L4-era per-COMMENT rate measured on a different
job. What prices this cell is probe-b's own 23-thread pass on an RTX 4090 — 727.664 billed worker
seconds, re-summed here from the evidence rows rather than copied from a report.

    PYTHONPATH=src python3 scripts/gate_census_w1_reader.py
    PYTHONPATH=src python3 scripts/gate_census_w1_reader.py --out /tmp/again.json   # the pair
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_aggregates as builder  # noqa: E402
import gate_census_w1 as census  # noqa: E402
import reader_population as reader  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import loop  # noqa: E402

OUT = REPO_ROOT / "results" / "gate_census_w1_reader.json"
SHIPPED = REPO_ROOT / "results" / "gate_census_w1.json"
PROBE_B_EVIDENCE = REPO_ROOT / "results" / "reader_probe_b_w1.jsonl"
PROBE_B_RUN = REPO_ROOT / "results" / "reader_probe_b_run.json"

CELL = "narrow|varto_off|plus_spam+scam"
SILENCERS = ("plus_spam", "scam")
"""The reader's two, in the census's own order. `varto_rule` is the one ruling 3 lifts, and it is
lifted for THIS path only — the payment gate of classification and the r1 brand attribution are not
touched (the sitting's own words)."""

EXPECTED_THREADS = 129
"""The operator's word for the reader's window-1 population, carried here as an EXPECTATION and
never as the source of the number. It is printed beside what was measured; a disagreement is a
finding for the report, not something this producer resolves."""


def enumerate_cell(all_threads: list[dict], aliases, rules, categories) -> list[dict]:
    """The cell's threads, NAMED — the keep predicate of `gate_census_w1.cell` applied one at a time.

    A count cannot be run and cannot be joined against ([[count_in_prose_is_not_the_enumeration]]).
    D5 needs each of probe-b's 23 threads' in/out status under this cell, and «129» does not answer
    that for one of them. Held to the census's own measurement by :func:`assert_is_the_cell`, on the
    threads AND on the payable comments, exactly as `reader_population` holds its own restatement.
    """
    kept = []
    for thread in all_threads:
        surviving = [
            row for row in thread["comments"] if not census.silenced_comment(row, SILENCERS)
        ]
        # (text, carrier) per text, the census's own comment: SPEC 3.21 (1) scopes the garmonija
        # rule to comment text. `rules=None` is what «varto_rule OFF» means here — the matcher runs
        # without the watchlist rules, which is the same switch `cell` flips for the silencer
        texts = [(thread["post_text"], census.POST_CARRIER)] + [
            (summary.comment_text(row), census.CARRIER) for row in surviving
        ]
        if not any(
            one["brands"] or one["categories"]
            for one in (
                census.hits(text, categories, aliases, None, carrier) for text, carrier in texts
            )
        ):
            continue
        payable = [
            {"msg_id": int(row["msg_id"]), "text": summary.comment_text(row)}
            for row in surviving
            if loop.has_text(summary.comment_text(row))
        ]
        kept.append(
            {
                "channel": thread["channel"],
                "post_id": thread["post_id"],
                "post_text": thread["post_text"],
                "comments": payable,
                "silenced": len(thread["comments"]) - len(surviving),
                "text_less": len(surviving) - len(payable),
            }
        )
    return kept


def assert_is_the_cell(kept: list[dict], measured: dict) -> None:
    """Refuse unless the enumeration IS the cell the census measured — both numbers."""
    payable = sum(len(one["comments"]) for one in kept)
    if (len(kept), payable) != (measured["threads"], measured["comments_payable"]):
        raise SystemExit(
            f"the enumeration is {len(kept)} threads and {payable} payable comments; the census"
            f" measured {measured['threads']} and {measured['comments_payable']} for the same cell."
            " One of the two describes a population nobody priced — stop and report."
        )


def probe_b_rate() -> dict:
    """probe-b's measured 4090 rate, re-summed from the evidence rows it wrote.

    Not read from a report and not taken from the warm-up. The warm-up's three threads carried 3, 4
    and 4 payable comments against this population's mean of 5.8, and probe-b's own registration
    calls that sample SMALL; the full pass is 23 threads and 134 payable comments, and it is the
    only rate this repo owns that was measured on the reader's actual job
    ([[a_price_is_as_representative_as_its_sample]]).
    """
    rows = [
        json.loads(line)
        for line in PROBE_B_EVIDENCE.read_text(encoding="utf-8").splitlines()
        if line
    ]
    worker_seconds = sum(row["seconds"]["worker"] for row in rows)
    payable = sum(row["payable_comments"] for row in rows)
    run = json.loads(summary.read_text_or_refuse(PROBE_B_RUN))
    return {
        "rate_usd_per_second": run["go_no_go"]["rate_usd_per_second"],
        "seconds_per_thread": round(worker_seconds / len(rows), 4),
        "seconds_per_payable_comment": round(worker_seconds / payable, 4),
        "sample": (
            f"{len(rows)} threads and {payable} payable comments in one pass,"
            f" {round(worker_seconds, 3)} billed worker seconds on an"
            f" {run['worker']['runtime']['gpu']} (endpoint {run['endpoint']},"
            f" {summary.rel(PROBE_B_EVIDENCE)}), re-summed from the rows and not copied"
        ),
        "evidence": {summary.rel(PROBE_B_EVIDENCE): summary.sha256_of(PROBE_B_EVIDENCE)},
    }


def price(threads: int, payable: int, rate: dict) -> dict:
    """This cell at probe-b's rate, both ways, with the binding one named.

    Two projections and not one, for the reason probe-b registered them that way: a thread call's
    cost scales with the text in it, so a per-thread rate measured on a population whose threads are
    smaller under-prices a bigger one. The pessimistic reading binds.
    """
    by_thread = threads * rate["seconds_per_thread"] * rate["rate_usd_per_second"]
    by_comment = payable * rate["seconds_per_payable_comment"] * rate["rate_usd_per_second"]
    return {
        "by_thread": {
            "seconds": round(threads * rate["seconds_per_thread"], 1),
            "usd": round(by_thread, 4),
            "rule": f"{threads} threads × {rate['seconds_per_thread']} s × the rate",
        },
        "by_payable_comment": {
            "seconds": round(payable * rate["seconds_per_payable_comment"], 1),
            "usd": round(by_comment, 4),
            "rule": f"{payable} payable comments × {rate['seconds_per_payable_comment']} s × the rate",
        },
        "binding_usd": round(max(by_thread, by_comment), 4),
        "binding": "by_payable_comment" if by_comment >= by_thread else "by_thread",
        "excludes": (
            "setup — the staging pod, the endpoint's boot and the warm-up. This is the READING cost"
            " of the cell and not an all-in figure for a contract"
        ),
        **rate,
    }


def build() -> dict:
    prereg = json.loads(summary.read_text_or_refuse(builder.PREREG))
    registry = summary.registry_through_the_seal(prereg, builder.REGISTRY)
    from market_pulse import brands

    aliases = brands.watchlist_aliases(registry.watchlist)
    rules = brands.load_watchlist_rules(builder.RULES)
    categories = census.compiled(wide=False)
    prices = json.loads(summary.read_text_or_refuse(census.PRICES))

    all_threads = reader.window()
    measured = census.cell(all_threads, False, SILENCERS, aliases, rules, prices)
    kept = enumerate_cell(all_threads, aliases, rules, categories)
    assert_is_the_cell(kept, measured)

    shipped = json.loads(summary.read_text_or_refuse(SHIPPED))
    sizes = sorted(len(one["comments"]) for one in kept)
    rate = probe_b_rate()

    return {
        "phase": "reader-v3-prep",
        "contract": "docs/PROMPT-reader-v3-prep.md D4",
        "cell": CELL,
        "authority": (
            "the reader sitting of 2026-08-16, ruling 3 (knowledge/decisions/reader-sitting-16-08"
            ".md): SPEC 3.21 (1)'s marker rule is lifted for the READER PATH ONLY — the payment gate"
            " of classification and the r1 brand attribution are not touched — spam and scam threads"
            " are not removed, and this cell is MEASURED and never derived"
        ),
        "silencers": {
            "varto_rule": {
                "active": False,
                "why": (
                    "ruling 3. probe-b measured what it costs the reader: E1 (@matusi_ukr:22242,"
                    " «дитячий центр Гармонія» → не_наш_рынок) and E4 (@mandziak:3684/#3689,"
                    " «чи варто» → an adverb) are two of the operator's four obligatory entity"
                    " cases, and the marker rule removes their threads BEFORE payment. probe-b"
                    " bought them by injection and both were answered"
                ),
            },
            "plus_spam": {"active": True},
            "scam": {"active": True},
            "not_removed": (
                "spam and scam THREADS stay in the population — the two silencers above drop"
                " participation markers and scam COMMENTS, which is what the census always meant by"
                " them. Ruling 3's «spam/scam threads are not removed» is a statement about the"
                " thread gate and it is satisfied by there being no thread-level silencer here"
            ),
        },
        "measured": {
            "threads": measured["threads"],
            "comments": measured["comments"],
            "comments_payable": measured["comments_payable"],
            "comments_silenced_window_wide": measured["comments_silenced_window_wide"],
        },
        "expectation": {
            "threads": EXPECTED_THREADS,
            "source": "the operator's word at the sitting, ruling 3",
            "agrees": measured["threads"] == EXPECTED_THREADS,
            "reading": (
                "carried as an expectation and never as the source of the number. Ruling 3 is"
                " explicit that a cell arrived at by arithmetic over two older cells would be a"
                " number no census on disk can reproduce"
            ),
        },
        "beside_the_shipped_grid": {
            "record": summary.rel(SHIPPED),
            "sha256": summary.sha256_of(SHIPPED),
            "narrow|silencers_off": {
                "threads": shipped["grid"]["narrow|silencers_off"]["threads"],
                "comments_payable": shipped["grid"]["narrow|silencers_off"]["comments_payable"],
            },
            "narrow|silencers_on": {
                "threads": shipped["grid"]["narrow|silencers_on"]["threads"],
                "comments_payable": shipped["grid"]["narrow|silencers_on"]["comments_payable"],
            },
            "varto_rule_alone": shipped["silencer_decomposition"]["each_alone"]["varto_rule"],
            "reading": (
                "the shipped record is NEVER rewritten — its producer's sha is pinned by its own"
                " record and by results/prereg_reader_probe*.json. These three rows are quoted from"
                " it so a reader can see this cell beside the grid it is missing from"
            ),
            "the_thread_count_alone_cannot_identify_this_cell": (
                f"this cell keeps {measured['threads']} threads and so does"
                f" narrow|silencers_off — the two silencers that stay ON drop COMMENTS, and in this"
                " window they never take a thread's last lexicon hit with them"
                f" (`each_alone` reports 0 threads removed for both). The payable count is what"
                f" tells them apart: {measured['comments_payable']} here against"
                f" {shipped['grid']['narrow|silencers_off']['comments_payable']} there, a"
                f" {shipped['grid']['narrow|silencers_off']['comments_payable'] - measured['comments_payable']}"
                "-comment difference that is exactly what plus_spam and scam removed. A cell"
                " identified by its thread count alone would have been indistinguishable from one"
                " nobody meant, which is the second reason ruling 3 asks for a MEASUREMENT"
            ),
        },
        "population": {
            "threads": len(kept),
            "payable_comments": sum(len(one["comments"]) for one in kept),
            "payable_per_thread": {
                "min": sizes[0],
                "median": sizes[len(sizes) // 2],
                "max": sizes[-1],
                "mean": round(sum(sizes) / len(sizes), 2),
            },
            "largest": [
                {
                    "thread": f"{one['channel']}:{one['post_id']}",
                    "payable_comments": len(one["comments"]),
                }
                for one in sorted(kept, key=lambda one: -len(one["comments"]))[:5]
            ],
            "enumeration_rule": (
                "the keep predicate of gate_census_w1.cell, applied one thread at a time and held"
                " to the census's own measurement on BOTH numbers. A count cannot be joined against,"
                " and D5 needs each of probe-b's 23 threads' in/out status under this cell"
            ),
        },
        "price": price(len(kept), sum(len(one["comments"]) for one in kept), rate),
        "reported_risk": {
            "what": (
                "the v3 prompt asks for a `per_comment` row for EVERY comment shown, where v1 and v2"
                " asked for one only where a comment carried a subject or an attitude. Output length"
                " now scales with the payable count of the thread"
            ),
            "ceiling": "local_llm.READER_MAX_NEW_TOKENS = 2000",
            "probe_population_max_payable": max(
                row["payable_comments"]
                for row in (
                    json.loads(line)
                    for line in PROBE_B_EVIDENCE.read_text(encoding="utf-8").splitlines()
                    if line
                )
            ),
            "this_cell_max_payable": sizes[-1],
            "measured_so_far": (
                "probe-b returned `finish_reason: length` on ZERO of 23 replies under v2, and its"
                " largest thread carried 15 payable comments. This cell's largest carries"
                f" {sizes[-1]}, so the ceiling is a WINDOW risk and not a probe risk — the paired"
                " re-read of the same 23 threads cannot reach it, and a window pass under v3 might"
            ),
            "unlock": (
                "measure `finish_reason` per thread on the v3 re-read and re-price the ceiling"
                " against the observed tokens-per-row before any window pass is opened"
            ),
        },
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "borrowed": {
                name: summary.sha256_of(REPO_ROOT / name)
                for name in (
                    "scripts/gate_census_w1.py",
                    "scripts/reader_population.py",
                    "scripts/window_summary_5c2.py",
                    "src/market_pulse/brands.py",
                    "src/market_pulse/lexicon.py",
                    "src/market_pulse/yield_screen.py",
                    "src/market_pulse/loop.py",
                )
            },
        },
        "inputs": {
            summary.rel(path): summary.sha256_of(path)
            for path in (census.LEXICON, builder.RULES, builder.REGISTRY, builder.PREREG, SHIPPED)
        },
    }


def population() -> list[dict]:
    """The cell's threads, for a caller that needs the list rather than the record."""
    prereg = json.loads(summary.read_text_or_refuse(builder.PREREG))
    registry = summary.registry_through_the_seal(prereg, builder.REGISTRY)
    from market_pulse import brands

    aliases = brands.watchlist_aliases(registry.watchlist)
    rules = brands.load_watchlist_rules(builder.RULES)
    prices = json.loads(summary.read_text_or_refuse(census.PRICES))
    all_threads = reader.window()
    kept = enumerate_cell(all_threads, aliases, rules, census.compiled(wide=False))
    assert_is_the_cell(kept, census.cell(all_threads, False, SILENCERS, aliases, rules, prices))
    return kept


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    record = build()
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    print(
        f"  {record['cell']}: {record['measured']['threads']} threads ·"
        f" {record['measured']['comments_payable']} payable comments"
        f"  (expected {EXPECTED_THREADS} · agrees {record['expectation']['agrees']})"
    )
    grid = record["beside_the_shipped_grid"]
    print(
        f"  shipped grid: silencers_off {grid['narrow|silencers_off']['threads']} ·"
        f" silencers_on {grid['narrow|silencers_on']['threads']} ·"
        f" varto alone {grid['varto_rule_alone']['threads']}"
    )
    money = record["price"]
    print(
        f"  at probe-b's 4090 rate: ${money['by_thread']['usd']:.4f} by thread ·"
        f" ${money['by_payable_comment']['usd']:.4f} by payable — binding"
        f" ${money['binding_usd']:.4f} ({money['binding']})"
    )
    risk = record["reported_risk"]
    print(
        f"  output ceiling: probe max {risk['probe_population_max_payable']} payable ·"
        f" this cell max {risk['this_cell_max_payable']} against {risk['ceiling']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
