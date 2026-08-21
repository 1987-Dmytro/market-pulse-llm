"""The window pack — the population, the rendering the pod will rebuild, and the self-exclusion.

Three properties carry this file. **The population is the census's**, not a number in a docstring:
the producer CALLS `gate_census_w1_reader.population()` and refuses if what comes back is not the
1 032 payable comments of 129 threads the contract registers. **Every request re-renders**, item by
item, on this checkout — the pod refuses the whole leg on a single sha it cannot reproduce, and a
registered request no pod can rebuild is a red test here rather than a dead pod at $0.80/h. **The
self-exclusion has a denominator**: window-1 is the population the 650 labels were drawn from, so
«0 items shown their own thread» is only a claim about the 968 items whose thread carries labels at
all — a filter every candidate passes certifies nothing
([[a_prefilter_cannot_certify_the_population]]).
"""

import json
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass1_fewshot_packs as fewshot  # noqa: E402
import build_pass1_sft as sft  # noqa: E402
import build_pass1_window_pack as window  # noqa: E402
import gate_census_w1_reader as census  # noqa: E402

from market_pulse import prompts  # noqa: E402

PACK = json.loads((REPO_ROOT / window.OUT_NAME).read_text("utf-8"))
ITEMS = PACK["legs"][0]["items"]


def test_the_shipped_pack_is_what_the_producer_builds_today(tmp_path):
    assert window.main(["--outdir", str(tmp_path)]) == 0
    assert (tmp_path / window.OUT_NAME).read_text("utf-8") == (
        REPO_ROOT / window.OUT_NAME
    ).read_text("utf-8")


def test_the_population_is_the_CENSUS_cells_and_the_contract_only_expects_it():
    kept = census.population()
    payable = {
        (f"{one['channel']}:{one['post_id']}", comment["msg_id"])
        for one in kept
        for comment in one["comments"]
    }
    assert (len(kept), len(payable)) == (129, 1032)
    assert PACK["population"]["cell"] == census.CELL
    assert (PACK["population"]["threads"], PACK["population"]["payable_comments"]) == (129, 1032)
    assert {(one["thread"], int(one["msg_id"])) for one in ITEMS} == payable
    # the order is the population's own, thread-grouped and never re-sorted by size
    assert [one["id"] for one in ITEMS] == [
        f"{one['channel']}:{one['post_id']}#{comment['msg_id']}"
        for one in kept
        for comment in one["comments"]
    ]


def test_the_producer_REFUSES_a_population_that_has_moved(monkeypatch):
    monkeypatch.setattr(window, "EXPECTED_PAYABLE", 1031)
    with pytest.raises(SystemExit, match="re-registration and not a re-run"):
        window.build()


def test_there_is_ONE_leg_and_it_names_its_own_out_file():
    (leg,) = PACK["legs"]
    assert leg["name"] == "v2"
    assert leg["task"] == prompts.PASS1_TASK_V2
    assert leg["out"] == window.LEG_OUT
    assert len(leg["items"]) == 1032
    assert len({one["id"] for one in leg["items"]}) == 1032


def test_the_pod_rebuilds_every_registered_request_from_the_items_own_fields():
    for item in ITEMS:
        content = prompts.pass1_messages_gm4(
            item["channel"],
            item["post_id"],
            item["topic"],
            item["entities"],
            item["msg_id"],
            item["text"],
            task=item["task"],
            examples=item["examples"],
        )[0]["content"]
        assert fewshot.sha_text(content) == item["rendering_sha256"], item["id"]
        assert len(content) == item["rendered_chars"]


def test_every_example_block_is_one_of_each_reading_and_none_from_the_query_thread():
    for item in ITEMS:
        chosen = item["examples_chosen"]
        assert len(chosen) == 5, item["id"]
        assert {one["label"] for one in chosen} == {
            *prompts.PASS1_SUBJECT_TYPES,
            "null",
        }, item["id"]
        assert all(one["thread"] != item["thread"] for one in chosen), item["id"]
    totals = PACK["balance"]["label_totals"]
    assert set(totals.values()) == {1032}


def test_the_self_exclusion_has_a_DENOMINATOR_and_the_rule_really_bites():
    block = PACK["self_exclusion"]
    assert block["items_shown_a_neighbour_from_their_own_thread"] == []
    per_thread = Counter(one["thread"] for one in sft.labelled_units())
    bites = [one for one in ITEMS if per_thread.get(one["thread"])]
    assert block["items_whose_own_thread_carries_labels"] == len(bites) == 968
    assert block["labels_withheld_from_those_items"] == sum(
        per_thread[one["thread"]] for one in bites
    )
    assert block["labels_withheld_from_those_items"] > 0
    # the 64 the rule cannot bite on are exactly probe-b's, whose threads were removed from the
    # labelling population WHOLE — so their emptiness is a construction and not an oversight
    assert {one["id"] for one in ITEMS} - {one["id"] for one in bites} == {
        one["id"] for one in ITEMS if one["membership"]["probe_64"]
    }


def test_gold_membership_is_keyed_on_the_pair_and_a_COLLIDING_id_proves_it(monkeypatch):
    """A msg_id is unique per channel, not per window — 13 of them here are carried by two threads.

    The id-only key selects the same fourteen on THIS population and that is a reading, not a
    property of the key. The mutation is the proof: hand `gold_keys` a pair whose msg_id belongs to
    a second thread as well, and the pair key marks ONE row where the id key would mark two
    ([[id_spaces_that_look_comparable]]).
    """
    block = PACK["gold_id_collisions"]
    assert len(block["msg_ids_carried_by_more_than_one_thread"]) == 13
    assert block["gold_by_pair"] == block["gold_by_msg_id_alone"] == 14
    assert block["the_two_keys_agree_on_this_population"] is True

    colliding = block["msg_ids_carried_by_more_than_one_thread"][0]
    threads = sorted({one["thread"] for one in ITEMS if int(one["msg_id"]) == colliding})
    assert len(threads) == 2, threads
    monkeypatch.setattr(window, "gold_keys", lambda: ({(threads[0], colliding)}, {threads[0]}))
    rebuilt = window.build()
    marked = [one["id"] for one in rebuilt["legs"][0]["items"] if one["membership"]["gold_14"]]
    by_id = sorted(one["id"] for one in ITEMS if int(one["msg_id"]) == colliding)
    assert len(by_id) == 2
    assert marked == [f"{threads[0]}#{colliding}"] != by_id


def test_membership_is_recorded_per_item_and_is_the_four_real_sets():
    gold_pairs, _ = window.gold_keys()
    probe = window.keys_of(window.PROBE_PACK, "items")
    dev = window.keys_of(window.DEV_PACK, "legs")
    labelled = {(one["thread"], one["msg_id"]) for one in sft.labelled_units()}
    for item in ITEMS:
        at = (item["thread"], int(item["msg_id"]))
        assert item["membership"] == {
            "gold_14": at in gold_pairs,
            "probe_64": at in probe,
            "labelled_650": at in labelled,
            "dev_200": at in dev,
        }, item["id"]
    assert {
        name: PACK["membership"][name]["n"]
        for name in ("gold_14", "probe_64", "labelled_650", "dev_200")
    } == {
        "gold_14": 14,
        "probe_64": 64,
        "labelled_650": 650,
        "dev_200": 200,
    }
    # dev-200 is a SUBSET of the 650, so the «450 not in dev-200» reading has its rows
    dev_ids = set(PACK["membership"]["dev_200"]["ids"])
    labelled_ids = set(PACK["membership"]["labelled_650"]["ids"])
    assert dev_ids < labelled_ids
    assert len(labelled_ids - dev_ids) == 450


def test_the_widest_request_is_inside_the_registered_ceiling():
    block = PACK["length"]
    assert block["ceiling_chars"] == prompts.PASS1_MAX_INPUT_CHARS
    assert block["widest_request_chars"] == max(one["rendered_chars"] for one in ITEMS)
    assert block["headroom_chars"] == block["ceiling_chars"] - block["widest_request_chars"] > 0
    # the renderer REFUSES rather than truncates, so a breach is a ValueError and not a short request
    widest = max(ITEMS, key=lambda one: one["rendered_chars"])
    with pytest.raises(ValueError):
        prompts.pass1_messages_gm4(
            widest["channel"],
            widest["post_id"],
            widest["topic"],
            widest["entities"],
            widest["msg_id"],
            widest["text"] + "x" * prompts.PASS1_MAX_INPUT_CHARS,
            task=widest["task"],
            examples=widest["examples"],
        )


def test_the_context_is_the_bought_verdicts_and_nothing_is_re_purchased():
    found, limit = fewshot.context()
    assert PACK["context"]["envelope_limit_chars"] == limit
    with_verdict = {one["thread"] for one in ITEMS if one["topic_source"] == "reader verdict"}
    assert with_verdict <= set(found)
    # two counts, two denominators, both named: two threads of the cell carry no payable comment
    # and one of THOSE has a bought verdict, so a single field would have been quoted about the
    # wrong set ([[count_the_kind_not_the_rows]])
    assert PACK["context"]["threads_carrying_an_item_with_a_bought_verdict"] == len(
        {one["thread"] for one in ITEMS} & set(found)
    )
    assert (
        PACK["context"]["threads_carrying_an_item"] == len({one["thread"] for one in ITEMS}) == 127
    )
    assert PACK["context"]["threads_in_the_cell_with_a_bought_verdict"] == 122
    assert PACK["context"]["threads_carrying_an_item_with_a_bought_verdict"] == 121
    # every topic came from one of exactly two places, and both are named
    assert set(PACK["context"]["topic_sources"]) == {
        "reader verdict",
        "the store's post text, bounded",
    }
    assert sum(PACK["context"]["topic_sources"].values()) == 1032


def test_the_per_thread_table_prices_pass_2s_denominator():
    table = PACK["per_thread"]
    assert len(table) == 129
    assert sum(one["payable_comments"] for one in table) == 1032
    assert sum(one["comment_chars"] for one in table) == sum(len(one["text"]) for one in ITEMS)
    by_thread = Counter(one["thread"] for one in ITEMS)
    for row in table:
        assert row["payable_comments"] == by_thread.get(row["thread"], 0), row["thread"]
    # two threads carry no payable comment at all — they are IN the cell and contribute no call
    assert sum(1 for one in table if not one["payable_comments"]) == 2


def test_the_store_and_the_census_are_asserted_to_be_the_same_thread():
    block = PACK["population"]["store_agreement"]
    assert (block["threads"], block["comments"]) == (129, 1032)


def test_all_three_store_refusals_FIRE_and_none_of_them_is_decoration():
    """A refusal nobody has watched fire is a refusal nobody has.

    `store_agrees` is the join between the census's membership and the store the render comes from,
    and all three of its branches can be deleted without the suite noticing unless they are driven
    ([[guard_selftest_negative_control]]).
    """
    import copy

    import build_pass1_label_pack_r2 as r2pack

    population = census.population()
    store = r2pack.raw_threads()
    assert window.store_agrees(population, store)["comments"] == 1032  # the GREEN path first

    name = f"{population[0]['channel']}:{population[0]['post_id']}"

    missing = {key: value for key, value in store.items() if key != name}
    with pytest.raises(SystemExit, match="in the census cell and not in the store"):
        window.store_agrees(population, missing)

    moved_post = copy.deepcopy(store)
    moved_post[name] = {**moved_post[name], "post_text": moved_post[name]["post_text"] + " …"}
    with pytest.raises(SystemExit, match="disagree on the post"):
        window.store_agrees(population, moved_post)

    # the comment leg is mutated on the CENSUS side: the store keeps its text inside the row's own
    # recorded `rendering`, and the refusal fires on the two sides disagreeing whichever one moves
    moved_comment = copy.deepcopy(population)
    moved_comment[0]["comments"][0]["text"] = "a text the store never held"
    with pytest.raises(SystemExit, match="disagree on the comment text"):
        window.store_agrees(moved_comment, store)
