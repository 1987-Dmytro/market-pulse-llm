#!/usr/bin/env python3
"""`results/pass1_window_pack.json` — pass 1 over the WHOLE window-1 reader population, under v2.

**What this builds.** `docs/PROMPT-pass1-window.md` D0, at $0, with no cloud call: ONE leg `v2`,
every payable comment of the reader's window-1 cell, each rendered EXACTLY as the dev leg of
`pass1-fewshot` rendered its own — the same five-neighbour block and the same topic/entity context,
through the same functions rather than through a second spelling of them.

**The population is CALLED, never typed.** `gate_census_w1_reader.population()` enumerates the cell
`narrow|varto_off|plus_spam+scam` and holds itself to the census's own measurement on both numbers.
This producer asks it for the list and counts what comes back; the contract's «1 032 payable
comments of 129 threads» is written into the record as an EXPECTATION printed beside the
measurement, and a disagreement is a stop, not something this producer resolves
([[count_in_prose_is_not_the_enumeration]]).

**Nothing here is re-purchased and nothing here is re-implemented.**

* the fields come from `build_pass1_sft.request()` — the same join, the same topic substitution and
  the same envelope the dev pack's items were built through;
* the neighbours come from `build_pass1_fewshot_packs.neighbours()` — one nearest labelled comment
  per class over the 650 labels MINUS every row of the query's own thread;
* the rendering and its per-item sha come from `build_pass1_fewshot_packs.rendered_item()`.

A second implementation of any of the three would be a second instrument nobody diffed
([[build_the_training_prompt_with_the_inference_call]]).

**The contamination block of the dev pack becomes a SELF-EXCLUSION block here.** Window-1 is the
population the labels were drawn FROM, so «no neighbour from the gold or the eval pack» is no longer
the interesting statement — «no comment is shown its own thread's labels» is, and it is only a
statement at all on the queries whose own thread carries labels. The record counts those queries and
the labels the rule actually withheld from them, because a filter every candidate passes certifies
nothing ([[a_prefilter_cannot_certify_the_population]]).

**Membership is recorded per item, not grepped later.** Each id says whether it is one of the
fourteen gold rows, one of probe-b's sixty-four, one of the 650 labelled rows and one of the dev-200
— so D2's census rows are derived from the pack instead of being re-joined by hand after the money
is spent.

    PYTHONPATH=src python3.11 scripts/build_pass1_window_pack.py
    PYTHONPATH=src python3.11 scripts/build_pass1_window_pack.py --outdir /tmp/again   # the pair
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pass1_fewshot_packs as fewshot  # noqa: E402
import build_pass1_label_pack_r2 as r2pack  # noqa: E402
import build_pass1_sft as sft  # noqa: E402
import gate_census_w1_reader as census  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import prompts  # noqa: E402

OUT_NAME = "results/pass1_window_pack.json"
LEG_OUT = "pass1_window_v2.jsonl"

GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
PROBE_PACK = REPO_ROOT / "results" / "pass1_probe_b_pack.json"
DEV_PACK = REPO_ROOT / "results" / "pass1_dev_pack.json"

EXPECTED_THREADS = 129
EXPECTED_PAYABLE = 1032
"""`docs/PROMPT-pass1-window.md`'s own two numbers, carried as an EXPECTATION and never as the
source. They are printed beside what `population()` measured and a disagreement stops the build:
the money block, the completeness bar and the recovery arithmetic are all derived from the count,
so a population that moved is a re-registration and not a re-run."""


def gold_keys() -> tuple[set[tuple[str, int]], set[str]]:
    """The fourteen gold rows as `(thread, msg_id)` — the SAME key the other three sets use.

    A msg_id is a Telegram id and it is unique per CHANNEL, not per window: 13 msg_ids of this very
    population are carried by two threads each. Keying the gold on the id alone would be a second id
    space wearing the first one's name ([[id_spaces_that_look_comparable]]). It happens to select the
    same fourteen rows here — no gold id collides — and `gold_id_collisions` records that the
    agreement is a reading of this population and not a property of the key.
    """
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    pairs = {
        (
            f"{row['channel']}:{(row.get('evidence_row') or {}).get('post_id_in_the_store')}",
            int(row["msg_id"]),
        )
        for row in gold["per_comment"]
    }
    threads = {thread for thread, _ in pairs}
    return pairs, threads


def keys_of(path: Path, where: str) -> set[tuple[str, int]]:
    """`(thread, msg_id)` of a pack's items — the identity the window population is joined on."""
    pack = json.loads(summary.read_text_or_refuse(path))
    items = pack["items"] if where == "items" else pack["legs"][0]["items"]
    return {(one["thread"], int(one["msg_id"])) for one in items}


def store_agrees(population: list[dict], store: dict) -> dict:
    """The census's own thread records against the SFT producer's store, field by field.

    Two producers describe each thread here: `population()` says which comments are payable, and
    `build_pass1_label_pack_r2.raw_threads()` is the store `build_pass1_sft.request()` renders from.
    The items below take membership from the first and every rendered field from the second, so the
    two have to be the same thread — asserted on the post text and on every comment's text rather
    than assumed, because a silent divergence would render the window under a post the census never
    saw ([[two_instruments_two_inputs]]).
    """
    checked_comments = 0
    for thread in population:
        name = f"{thread['channel']}:{thread['post_id']}"
        if name not in store:
            raise SystemExit(f"{name} is in the census cell and not in the store — stop.")
        held = store[name]
        if (held["channel"], int(held["post_id"]), held["post_text"]) != (
            thread["channel"],
            int(thread["post_id"]),
            thread["post_text"],
        ):
            raise SystemExit(
                f"{name}: the census record and the store disagree on the post — stop."
            )
        texts = {int(row["msg_id"]): summary.comment_text(row) for row in held["comments"]}
        for comment in thread["comments"]:
            if texts.get(comment["msg_id"]) != comment["text"]:
                raise SystemExit(
                    f"{name}#{comment['msg_id']}: the census record and the store disagree on the"
                    " comment text — the render would not be the population's. Stop."
                )
            checked_comments += 1
    return {
        "threads": len(population),
        "comments": checked_comments,
        "rule": (
            "membership comes from gate_census_w1_reader.population(); every rendered field comes"
            " from build_pass1_label_pack_r2.raw_threads() through build_pass1_sft.request(). Both"
            " describe the same thread, and this is the assertion — post text and every payable"
            " comment's text, one at a time"
        ),
    }


def self_exclusion(items: list[dict], labels: list[dict]) -> dict:
    """The neighbour rule's own guarantee, and the queries it can actually BITE on.

    `items_shown_a_neighbour_from_their_own_thread` is empty in a correct pack — but on a query
    whose thread carries no label it is empty for free, and window-1 is the population the 650
    labels were drawn from, so the number that makes the zero mean something is how many queries had
    labels of their own withheld. Both are counted, and the labels withheld are counted too.
    """
    per_thread = Counter(one["thread"] for one in labels)
    shown = sorted(
        one["id"]
        for one in items
        if any(pick["thread"] == one["thread"] for pick in one["examples_chosen"])
    )
    bites = [one for one in items if per_thread.get(one["thread"])]
    return {
        "rule": "0 items are shown a neighbour from their own thread",
        "items_shown_a_neighbour_from_their_own_thread": shown,
        "items_whose_own_thread_carries_labels": len(bites),
        "labels_withheld_from_those_items": sum(per_thread[one["thread"]] for one in bites),
        "labelled_threads_in_the_pool": len(per_thread),
        "distinct_neighbours_used": len(
            {(pick["thread"], pick["msg_id"]) for one in items for pick in one["examples_chosen"]}
        ),
        "why_it_is_not_the_dev_pack's_contamination_block": (
            "window-1 IS the population the 650 labels were drawn from, so «no neighbour from the"
            " gold or the eval pack» is not the live risk here — a comment being shown its own"
            " thread's answers is. A rule no candidate can trip certifies nothing, so the queries"
            " it withheld a label from are counted beside the zero"
        ),
    }


def membership(items: list[dict]) -> dict:
    """The four sets D2's census rows are derived from, counted and NAMED in the pack."""
    out = {}
    for name in ("gold_14", "probe_64", "labelled_650", "dev_200"):
        ids = sorted(one["id"] for one in items if one["membership"][name])
        out[name] = {"n": len(ids), "ids": ids}
    out["rule"] = (
        "recorded per item so D2's report-only census rows are DERIVED from this pack and never"
        " re-joined by hand after the money is spent. The fourteen and the sixty-four are answered"
        " like any other comment of the population"
    )
    return out


def rendered_entity_chars(item: dict) -> int:
    """What the entity block costs IN THE REQUEST — the same item rendered with it and without it.

    Not `len(str(entities))`: a Python dict repr carries quotes, braces and `: ` separators the
    renderer never emits, and on this population it overstates the block by ~3x. This number prices
    `pass2-signals`, whose call carries the entity context per thread, so it has to be the chars a
    model will actually read ([[a_literal_below_the_minimum_is_a_unit_error]]).
    """

    def render(entities):
        return prompts.pass1_messages_gm4(
            item["channel"],
            item["post_id"],
            item["topic"],
            entities,
            item["msg_id"],
            item["text"],
            task=item["task"],
            examples=item["examples"],
        )[0]["content"]

    return len(render(item["entities"])) - len(render([]))


def per_thread(population: list[dict], items: list[dict]) -> list[dict]:
    """What prices `pass2-signals`: the shape of every thread pass 2 will make ONE call over.

    The pass-2 FILTER — the rows pass 1 labelled `категория_личное` / `молочный_бренд` /
    `сеть_ритейлер` — cannot be known before the run and is D2's row. What can be known now is the
    denominator it will be taken out of: the payable comments, their characters, and the entity
    block each thread carries.
    """
    by_thread: dict[str, list[dict]] = {}
    for one in items:
        by_thread.setdefault(one["thread"], []).append(one)
    out = []
    for thread in population:
        name = f"{thread['channel']}:{thread['post_id']}"
        rows = by_thread.get(name, [])
        out.append(
            {
                "thread": name,
                "payable_comments": len(rows),
                "comment_chars": sum(len(one["text"]) for one in rows),
                "entities": len(rows[0]["entities"]) if rows else 0,
                "entity_block_chars": rendered_entity_chars(rows[0]) if rows else 0,
                "topic_chars": len(rows[0]["topic"]) if rows else 0,
                "topic_from": rows[0]["topic_source"] if rows else None,
                "silenced": thread["silenced"],
                "text_less": thread["text_less"],
            }
        )
    return out


def build() -> dict:
    population = census.population()
    threads = len(population)
    payable = sum(len(one["comments"]) for one in population)
    if (threads, payable) != (EXPECTED_THREADS, EXPECTED_PAYABLE):
        raise SystemExit(
            f"population() measures {threads} threads and {payable} payable comments; the contract"
            f" registers {EXPECTED_THREADS} and {EXPECTED_PAYABLE}. The money block, the"
            " completeness bar and the recovery arithmetic are all derived from that count — this"
            " is a re-registration and not a re-run. Stop and report."
        )

    store = r2pack.raw_threads()
    agreement = store_agrees(population, store)
    labels = fewshot.pool()
    if len(labels) != 650:
        raise SystemExit(f"{len(labels)} labelled rows, and the contract registers 650 — stop.")
    found, limit = fewshot.context()

    gold_pairs, gold_threads = gold_keys()
    probe = keys_of(PROBE_PACK, "items")
    dev = keys_of(DEV_PACK, "legs")
    labelled = {(one["thread"], one["msg_id"]) for one in labels}

    items = []
    for thread in population:
        name = f"{thread['channel']}:{thread['post_id']}"
        held = store[name]
        for comment in thread["comments"]:
            at = (name, comment["msg_id"])
            unit = {
                "thread": name,
                "msg_id": comment["msg_id"],
                "text": comment["text"],
                "store": held,
            }
            built = sft.request(unit, found, limit)
            chosen = fewshot.neighbours(name, fewshot.grams(comment["text"]), labels)
            one = fewshot.rendered_item(built["fields"], prompts.PASS1_TASK_V2, chosen)
            one["topic_source"] = built["topic_source"]
            one["verdict_source"] = built["verdict_source"]
            one["membership"] = {
                "gold_14": at in gold_pairs,
                "probe_64": at in probe,
                "labelled_650": at in labelled,
                "dev_200": at in dev,
            }
            items.append(one)

    if len(items) != payable:
        raise SystemExit(f"{len(items)} items rendered against {payable} payable comments — stop.")
    if len({one["id"] for one in items}) != payable:
        raise SystemExit("two items share an id — the leg's resume would answer fewer units. Stop.")

    # The ceiling STOP the contract asks for is the RENDERER'S, and it has already fired by the time
    # this runs: `prompts.pass1_messages_gm4` raises ValueError on an over-ceiling request rather
    # than truncating it, so `rendered_item` above never returns one. A branch here on
    # `headroom_chars < 0` would be unreachable code wearing a guard's clothes — the check that this
    # is a real STOP is a test that DRIVES the renderer past the ceiling, and there is one
    # ([[an_empty_class_is_the_definitions_answer]]). What this measures is the headroom that is left
    length = fewshot.ceiling_check(items)

    exclusion = self_exclusion(items, labels)
    if exclusion["items_shown_a_neighbour_from_their_own_thread"]:
        raise SystemExit(
            f"{len(exclusion['items_shown_a_neighbour_from_their_own_thread'])} items are shown a"
            " neighbour from their own thread — a comment would see its own thread's answers. Stop."
        )

    probe_pack = json.loads(summary.read_text_or_refuse(PROBE_PACK))
    threads_table = per_thread(population, items)
    return {
        "phase": "pass1-window",
        "contract": "docs/PROMPT-pass1-window.md D0",
        "what_this_run_is": (
            "a PRODUCTION pass, not an evaluation. Its out-file is the INPUT of pass 2 and the bar"
            " is transport and completeness. Nothing in it is a bar on v2's quality"
        ),
        "instruments": fewshot.instruments(),
        "serving": probe_pack["serving"],
        "reading": probe_pack["reading"],
        "order_rule": (
            "the population's own thread-grouped order: threads as"
            " gate_census_w1_reader.population() enumerates them, comments as each thread holds"
            " them. No re-ordering by size — the ruling «pack by descending payable» was WITHDRAWN"
            " on 2026-08-17 before any pod"
        ),
        "registration": {"record": "results/prereg_pass1_window.json"},
        "population": {
            "cell": census.CELL,
            "producer": summary.rel(REPO_ROOT / "scripts" / "gate_census_w1_reader.py"),
            "producer_sha256": summary.sha256_of(
                REPO_ROOT / "scripts" / "gate_census_w1_reader.py"
            ),
            "threads": threads,
            "payable_comments": payable,
            "expected_threads": EXPECTED_THREADS,
            "expected_payable_comments": EXPECTED_PAYABLE,
            "agrees_with_the_contract": True,
            "threads_with_no_payable_comment": sum(1 for one in population if not one["comments"]),
            "silenced_comments": sum(one["silenced"] for one in population),
            "text_less_comments": sum(one["text_less"] for one in population),
            "rule": (
                "derived by CALLING gate_census_w1_reader.population(), which holds its own"
                " enumeration to the census's measurement on both numbers. The contract's figures"
                " are the expectation printed beside it"
            ),
            "store_agreement": agreement,
        },
        "context": {
            "rule": (
                "build_pass1_sft.verdicts() / ::envelope() — the BOUGHT v5b / v4 / topup verdicts."
                " No reading is re-purchased. A thread with no bought verdict renders the store's"
                " post text, bounded to the envelope, exactly as the dev pack's items did"
            ),
            "envelope_limit_chars": limit,
            "threads_in_the_cell_with_a_bought_verdict": sum(
                1 for one in population if f"{one['channel']}:{one['post_id']}" in found
            ),
            "threads_carrying_an_item_with_a_bought_verdict": len(
                {one["thread"] for one in items} & set(found)
            ),
            "threads_carrying_an_item": len({one["thread"] for one in items}),
            "why_two_counts": (
                "two threads of the cell carry no payable comment, so the cell's 129 and the"
                " threads that actually produce a request are different denominators. One of those"
                " two HAS a bought verdict, which is why the two counts differ by one — a single"
                " field would have been true of one set and quoted about the other"
                " ([[count_the_kind_not_the_rows]])"
            ),
            "topic_sources": dict(sorted(Counter(one["topic_source"] for one in items).items())),
            "verdict_files": dict(
                sorted(Counter(one["verdict_source"] or "none" for one in items).items())
            ),
        },
        "neighbours": {
            "rule": (
                "for each of the five readings — the four subject types and the null — the single"
                " nearest labelled comment by Jaccard similarity over lower-cased character"
                f" {fewshot.GRAM}-grams of the comment text, from the 650 labels MINUS every row of"
                " the query's own thread. Ties to the smaller msg_id, then to the thread"
            ),
            "function": "build_pass1_fewshot_packs.neighbours — imported, not copied",
            "pool": {
                "rows": len(labels),
                "files": {
                    name: summary.sha256_of(path) for name, path in sorted(sft.LABELS.items())
                },
            },
        },
        "legs": [
            {
                "name": "v2",
                "task": prompts.PASS1_TASK_V2,
                "out": LEG_OUT,
                "reading": (
                    "the ONE leg. The base was measured in r2 and is not re-run: there is no second"
                    " leg, no dev gate and no paired arm in this contract"
                ),
                "items": items,
            }
        ],
        "membership": membership(items),
        "self_exclusion": exclusion,
        "balance": fewshot.balance(items),
        "length": {
            **length,
            "stop_rule": (
                "the STOP is prompts.pass1_messages_gm4's own ValueError, which fires inside"
                " rendered_item and before any item reaches this record — so the build cannot"
                " produce an over-ceiling request and there is no branch here that could catch one."
                " tests/test_pass1_window_pack.py drives the renderer past the ceiling on the"
                " widest real item and watches it refuse"
            ),
        },
        "gold_id_collisions": {
            "rule": (
                "a msg_id is unique per CHANNEL and not per window. Membership is keyed on"
                " (thread, msg_id) everywhere; this is what the id-only key would have done"
            ),
            "msg_ids_carried_by_more_than_one_thread": sorted(
                one for one, n in Counter(int(item["msg_id"]) for item in items).items() if n > 1
            ),
            "gold_by_pair": sum(1 for one in items if one["membership"]["gold_14"]),
            "gold_by_msg_id_alone": sum(
                1 for one in items if int(one["msg_id"]) in {msg for _, msg in gold_pairs}
            ),
            "the_two_keys_agree_on_this_population": sum(
                1 for one in items if one["membership"]["gold_14"]
            )
            == sum(1 for one in items if int(one["msg_id"]) in {msg for _, msg in gold_pairs}),
        },
        "gold_threads_in_the_population": sorted(
            gold_threads & {f"{one['channel']}:{one['post_id']}" for one in population}
        ),
        "per_thread": threads_table,
        "pass_2_pricing": {
            "rule": (
                "pass 2 is ONE call per thread over the rows pass 1 labelled категория_личное /"
                " молочный_бренд / сеть_ритейлер. The FILTER cannot be known before this run — it"
                " is D2's census row. What `per_thread` carries is the denominator it comes out of"
            ),
            "threads": threads,
            "payable_comments": payable,
            "comment_chars": sum(len(one["text"]) for one in items),
            "widest_thread_payable": max(
                (one["payable_comments"] for one in threads_table), default=0
            ),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    record = build()
    record["producer"] = {
        "script": summary.rel(Path(__file__)),
        "sha256": summary.sha256_of(Path(__file__)),
        "borrowed": {
            one: summary.sha256_of(REPO_ROOT / one)
            for one in (
                "scripts/build_pass1_fewshot_packs.py",
                "scripts/build_pass1_sft.py",
                "scripts/gate_census_w1_reader.py",
                "scripts/window_summary_5c2.py",
                "src/market_pulse/prompts.py",
            )
        },
    }
    path = args.outdir / OUT_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")

    block = record["population"]
    print(f"wrote {OUT_NAME}  sha256 {fewshot.sha_text(payload)[:16]}…")
    print(
        f"  population: {block['threads']} threads · {block['payable_comments']} payable comments"
        f"  (contract {block['expected_threads']} · {block['expected_payable_comments']})"
    )
    print(
        f"  one leg v2 → {LEG_OUT} · {len(record['legs'][0]['items'])} items ·"
        f" {block['threads_with_no_payable_comment']} threads carry no payable comment"
    )
    length = record["length"]
    print(
        f"  length: widest {length['widest_request_chars']} chars ({length['widest_request']}) ·"
        f" median {length['median_chars']} · headroom {length['headroom_chars']} of"
        f" {length['ceiling_chars']}"
    )
    exclusion = record["self_exclusion"]
    print(
        f"  self-exclusion: {len(exclusion['items_shown_a_neighbour_from_their_own_thread'])} items"
        f" shown their own thread · {exclusion['items_whose_own_thread_carries_labels']} items had"
        f" {exclusion['labels_withheld_from_those_items']} labels withheld ·"
        f" {exclusion['distinct_neighbours_used']} distinct neighbours used"
    )
    print(f"  balance: {record['balance']['label_totals']}")
    print(
        "  membership: "
        + " · ".join(
            f"{name} {record['membership'][name]['n']}"
            for name in ("gold_14", "probe_64", "labelled_650", "dev_200")
        )
    )
    context = record["context"]
    print(
        f"  context: envelope {context['envelope_limit_chars']} chars ·"
        f" {context['threads_in_the_cell_with_a_bought_verdict']} of {block['threads']} cell"
        f" threads carry a bought verdict ·"
        f" {context['threads_carrying_an_item_with_a_bought_verdict']} of"
        f" {context['threads_carrying_an_item']} that carry an item ·"
        f" topic sources {context['topic_sources']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
