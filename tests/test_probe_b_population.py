"""`scripts/probe_b_population.py` — the registered subset, and the four threads bought past the gate.

Two claims no other test can make: that every case the operator made obligatory is reachable in this
population, and that the threads which reach it from OUTSIDE the billing gate are exactly the four
the gate removes and no others.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import probe_b_population as subset  # noqa: E402
import reader_population as cell  # noqa: E402

GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def kept() -> list[dict]:
    return subset.population()


@pytest.fixture(scope="module")
def by_key(kept) -> dict:
    return {subset.key(one["channel"], one["post_id"]): one for one in kept}


def test_the_subset_is_enumerated_and_not_estimated(kept):
    """The contract expected «~16–19 threads» and the enumeration is 23: the six S-list rows resolve
    to four posts nobody had counted, and the three warm-up threads are a fourth group. «Enumerate,
    don't estimate» is the contract's own instruction and this is what it produced."""
    assert len(kept) == 23
    assert sum(len(one["comments"]) for one in kept) == 134
    assert len([one for one in kept if one["injected"]]) == 4
    # one fixed order, and it is the digest's: never by size, which a measurement could move
    assert [subset.key(one["channel"], one["post_id"]) for one in kept] == sorted(
        subset.key(one["channel"], one["post_id"]) for one in kept
    )


def test_the_injected_threads_are_the_four_the_gate_removes_and_nothing_else(kept, by_key):
    """Both directions, and the gold's own reachability block is the second opinion.

    A thread marked injected that the census cell holds would be a mislabelled row in a record the
    sitting reads; a thread the gate removed but nobody marked would be paid-for evidence walking
    into an aggregate that must not have it.
    """
    gated = {subset.key(one["channel"], one["post_id"]) for one in cell.population()}
    injected = {subset.key(one["channel"], one["post_id"]) for one in kept if one["injected"]}
    assert injected == set(subset.INJECTED)
    assert not injected & gated
    assert {
        subset.key(one["channel"], one["post_id"]) for one in kept if not one["injected"]
    } <= gated

    unreachable = {
        one["id"]
        for group in ("entity_cases", "noise_threads", "flagships")
        for one in GOLD["reachability"][group]["unreachable"]
    }
    assert unreachable == set(subset.INJECTED.values()) == {"E1", "E4a", "E4b", "N3"}
    for name, case in subset.INJECTED.items():
        assert case in by_key[name]["cases"]


def test_the_guard_refuses_an_injected_set_that_is_not_the_registered_one(kept):
    """The negative control. An assertion over a literal is worth what its failure is worth."""
    forged = [{**one, "injected": True} for one in kept]
    with pytest.raises(SystemExit, match="population nobody registered"):
        subset.assert_the_injected_are_the_four_the_gate_removes(forged)
    none = [{**one, "injected": False} for one in kept]
    with pytest.raises(SystemExit, match="population nobody registered"):
        subset.assert_the_injected_are_the_four_the_gate_removes(none)


def test_every_gold_row_is_reachable_in_this_population(by_key):
    """What the whole subset is for. v1 could register 2 of 2 entity cases and 13 of 14 per-comment
    rows because the gate removed the rest before payment; here every one of them is in a thread the
    run will read, so 4/4 and 14/14 are measurements rather than arithmetic impossibilities."""
    for row in GOLD["per_comment"]:
        name = subset.key(row["channel"], row["evidence_row"]["post_id_in_the_store"])
        assert row["msg_id"] in {one["msg_id"] for one in by_key[name]["comments"]}, row["msg_id"]

    for case in GOLD["flagships"]:
        name = subset.key(case["channel"], case["post_id"])
        ids = {one["msg_id"] for one in by_key[name]["comments"]}
        for signal in case["signals"]:
            assert set(signal["evidence"]) <= ids, signal["id"]

    for case in GOLD["entity_cases"]:
        name = subset.key(case["channel"], case["post_id"])
        assert name in by_key, case["id"]
        if case["msg_id"] is not None:
            assert case["msg_id"] in {one["msg_id"] for one in by_key[name]["comments"]}
    # the two «чи варто» ids are the absence case: the reader has to be SHOWN them to not report
    assert 48099 in {one["msg_id"] for one in by_key["@mandziak:3684"]["comments"]}
    assert 48054 in {one["msg_id"] for one in by_key["@mandziak:3689"]["comments"]}


def test_n3_reaches_the_reader_as_an_empty_thread(by_key):
    """A finding registered rather than repaired: @sashafitnesslife:3939 has 29 comments and the
    gate's plus-spam silencer removes ALL of them before payment, so the thread the reader is given
    is a post and nothing else. Its «0 signals» cell is produced by the silencer, not by the reader
    ([[a_structurally_unreachable_zero]]) — bar 3's other four threads are what can move it."""
    n3 = by_key["@sashafitnesslife:3939"]
    assert n3["comments"] == []
    assert n3["silenced"] == 29 and n3["text_less"] == 0
    assert n3["post_text"].strip()


def test_the_digest_pins_the_list_and_sees_a_swapped_flag(kept):
    """23 is a count and a count cannot be run. The injected flag is INSIDE the hashed line, so a
    subset that swapped a gated thread for an injected one of the same shape cannot hash the same."""
    assert subset.digest(kept) != subset.digest(kept[:-1])
    flipped = [{**kept[0], "injected": not kept[0]["injected"]}, *kept[1:]]
    assert subset.digest(kept) != subset.digest(flipped)
    thinner = [{**kept[0], "comments": kept[0]["comments"][:-1]}, *kept[1:]]
    assert subset.digest(kept) != subset.digest(thinner)
    assert subset.digest(kept) == subset.digest(subset.population())
