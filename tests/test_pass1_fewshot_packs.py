"""The two packs of pass1-fewshot — the pairing, the balance, the contamination and the ceiling.

What carries the money here. The dev pack is PAIRED — the same 200 rows, the same context, one
difference — because a table comparing two prompts over two different populations measures the
populations. The example block is one per class BY CONSTRUCTION, which is the whole defence against
the prior the LoRA of line B learned. The shot pack is probe-b's sixty-four in identity and ORDER,
and the sealed pack it is read from is proved untouched by its own pinned sha. And every
`rendering_sha256` is re-derived through the POD's own checker, with the fewshot runner's swap
installed, so a registered request no pod can rebuild is a red gate here and not at $0.80/h.
"""

import json
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass1_fewshot_packs as packs  # noqa: E402
import moved_pins  # noqa: E402
import pass1_fewshot_pod_runner as fewshot  # noqa: E402
import reader_v5_pod_runner as runner  # noqa: E402

from market_pulse import prompts  # noqa: E402

DEV = json.loads((REPO_ROOT / packs.DEV_NAME).read_text("utf-8"))
SHOT = json.loads((REPO_ROOT / packs.SHOT_NAME).read_text("utf-8"))
SEALED = json.loads((REPO_ROOT / "results" / "pass1_probe_b_pack.json").read_text("utf-8"))


def leg(pack: dict, name: str) -> dict:
    return next(one for one in pack["legs"] if one["name"] == name)


def test_both_packs_are_what_the_producer_builds_today(tmp_path):
    assert packs.main(["--outdir", str(tmp_path)]) == 0
    for name in (packs.DEV_NAME, packs.SHOT_NAME):
        again = json.loads((tmp_path / name).read_text(encoding="utf-8"))
        shipped = json.loads((REPO_ROOT / name).read_text(encoding="utf-8"))
        # EXCEPT where they pin `src/market_pulse/prompts.py`: ruling (ф) moved it again, and
        # `results/pass1_dev_pack.json` is the BEFORE column of `think-zero-shot`'s paired table —
        # a re-pinned rebuild committed over it would move the file that column is read from
        moved_pins.assert_only_the_prompts_pin_moved(shipped, again)


def test_the_dev_legs_are_the_same_rows_with_one_difference():
    base, v2 = leg(DEV, "base"), leg(DEV, "v2")
    assert len(base["items"]) == len(v2["items"]) == packs.DEV_TARGET
    assert [one["id"] for one in base["items"]] == [one["id"] for one in v2["items"]]
    assert base["task"] == prompts.PASS1_TASK and v2["task"] == prompts.PASS1_TASK_V2
    for left, right in zip(base["items"], v2["items"]):
        assert left["topic"] == right["topic"]
        assert left["entities"] == right["entities"]
        assert left["text"] == right["text"] and left["msg_id"] == right["msg_id"]
        assert "examples" not in left and len(right["examples"]) == 5
        assert right["rendered_chars"] > left["rendered_chars"]
    assert DEV["paired"]["same_rows"] and DEV["paired"]["same_context"]
    # and the two legs answer into DIFFERENT files — one file would let the resume skip a leg
    assert base["out"] != v2["out"] != leg(SHOT, "shot")["out"]


def test_the_dev_population_is_all_49_our_rows_plus_the_stratified_151():
    assert DEV["population"]["rows"] == packs.DEV_TARGET
    assert DEV["population"]["our_rows"] == 49
    assert DEV["draw"]["ours_taken_whole"] == 49
    assert DEV["population"]["distribution"] == {
        "молочный_бренд": 2,
        "сеть_ритейлер": 12,
        "категория_личное": 47,
        "не_наш_рынок": 85,
        "null": 54,
    }
    assert DEV["draw"]["rest_allocation"] == {"не_наш_рынок": 85, "null": 54, "сеть_ритейлер": 12}
    assert sum(DEV["draw"]["rest_allocation"].values()) == packs.DEV_TOPPED_UP
    assert DEV["draw"]["seed"] == packs.SEED
    # every «our» label of the 650 is in the dev set, not a sample of them
    ours = {
        (one["thread"], int(one["msg_id"]))
        for one in packs.pool()
        if one["subject_type"] in packs.OUR
    }
    drawn = {(one["thread"], int(one["msg_id"])) for one in leg(DEV, "base")["items"]}
    assert ours <= drawn and len(ours) == 49
    # and msg_id ALONE is unique across the 200. `scorer.reader_comment_agreement` keys its answers
    # on msg_id and nothing else, so two dev rows sharing one would be last-wins: one answer would
    # be dropped silently and BOTH rows would read `absent` ([[select_one_row_refuse_ambiguity]])
    ids = [int(one["msg_id"]) for one in leg(DEV, "base")["items"]]
    assert len(ids) == len(set(ids)) == packs.DEV_TARGET
    shot_ids = [int(one["msg_id"]) for one in leg(SHOT, "shot")["items"]]
    assert len(shot_ids) == len(set(shot_ids)) == 64


@pytest.mark.parametrize("pack,name", [(DEV, "v2"), (SHOT, "shot")])
def test_every_example_block_is_one_of_each_reading_and_none_from_the_query_thread(pack, name):
    items = leg(pack, name)["items"]
    for item in items:
        chosen = item["examples_chosen"]
        assert len(chosen) == 5
        assert [one["label"] for one in chosen] == [
            "молочный_бренд",
            "сеть_ритейлер",
            "категория_личное",
            "не_наш_рынок",
            "null",
        ]
        assert all(one["thread"] != item["thread"] for one in chosen), item["id"]
        assert [one["label"] for one in chosen] == [
            packs.key(one["label"]) for one in item["examples"]
        ]
    totals = Counter(one["label"] for item in items for one in item["examples_chosen"])
    assert len(set(totals.values())) == 1, totals  # balance BY CONSTRUCTION, not by luck
    assert pack["balance"]["label_totals"] == dict(totals)


@pytest.mark.parametrize("pack", [DEV, SHOT])
def test_the_four_contamination_lists_are_empty_and_the_matcher_can_find_something(pack):
    block = pack["contamination"]
    for name in (
        "neighbour_ids_in_the_gold_14",
        "neighbour_threads_in_the_gold_threads",
        "neighbour_ids_in_the_eval_pack_64",
        "neighbour_threads_in_the_eval_pack_threads",
    ):
        assert block[name] == [], (name, block[name])
    assert block["items_shown_a_neighbour_from_their_own_thread"] == []
    assert block["distinct_neighbours_used"] > 5, block["distinct_neighbours_used"]
    # the negative control: the same two exams DO intersect each other, so the matcher works
    gold_ids = {
        int(row["msg_id"])
        for row in packs.json.loads(
            (REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text("utf-8")
        )["per_comment"]
    }
    probe_ids = {int(one["msg_id"]) for one in SEALED["items"]}
    assert gold_ids and gold_ids <= probe_ids


def test_the_shot_pack_is_the_sealed_sixty_four_in_identity_and_order():
    items = leg(SHOT, "shot")["items"]
    assert [one["id"] for one in items] == [one["id"] for one in SEALED["items"]]
    for ours, sealed in zip(items, SEALED["items"]):
        for field in ("channel", "post_id", "topic", "entities", "msg_id", "text", "leg"):
            assert ours[field] == sealed[field], (ours["id"], field)
        # the request itself MOVED — that is the contract — and it moved by more than nothing
        assert ours["rendering_sha256"] != sealed["rendering_sha256"]
        assert ours["task"] == prompts.PASS1_TASK_V2
    # the sealed pack is READ and never written: its own sha still matches what pins it
    assert SHOT["sealed_source"]["sha256"] == packs.summary.sha256_of(packs.PROBE_PACK)
    pinned = json.loads((REPO_ROOT / "results" / "prereg_lora_b.json").read_text("utf-8"))[
        "population"
    ]["eval_pack"]
    assert pinned["sha256"] == SHOT["sealed_source"]["sha256"]


@pytest.mark.parametrize("pack,name", [(DEV, "base"), (DEV, "v2"), (SHOT, "shot")])
def test_the_pod_rebuilds_every_registered_request_from_the_items_own_fields(pack, name):
    """The transport proof, run on the Mac at $0 through the POD's own checker.

    `reader_v5_pod_runner.check_requests` is what refuses on the pod, and it is driven here with the
    fewshot swap installed — the same two names the run replaces. A pack whose shas this checkout
    cannot reproduce is a pod that stops after the model is loaded, with a meter running.
    """
    one = leg(pack, name)
    with fewshot.as_fewshot():
        items = runner.check_requests({**pack, "task": one["task"], "items": one["items"]}, prompts)
    assert len(items) == len(one["items"])


def test_the_widest_request_is_inside_the_registered_ceiling():
    for pack in (DEV, SHOT):
        block = pack["length"]
        assert block["ceiling_chars"] == prompts.PASS1_MAX_INPUT_CHARS
        assert block["widest_request_chars"] < block["ceiling_chars"]
        assert block["headroom_chars"] > 0
    # the ceiling really does bite — the renderer refuses rather than truncating, proven in
    # tests/test_pass1_prompt.py; here the claim is only that no registered item is near it
    assert DEV["length"]["widest_request_chars"] < 9000
    assert SHOT["length"]["widest_request_chars"] < 9000


def test_the_instruments_cover_the_whole_served_family_and_v1s_sha_did_not_move():
    for pack in (DEV, SHOT):
        block = pack["instruments"]
        assert set(block["prompt_sha256"]) == set(prompts.PASS1)
        assert (
            block["prompt_sha256"][prompts.PASS1_TASK]
            == (SEALED["instruments"]["prompt_sha256"][prompts.PASS1_TASK])
        )
        assert block["prompt_sha256"][prompts.PASS1_TASK_V2] == prompts.prompt_sha256(
            prompts.PASS1_TASK_V2
        )
        # The pin describes the checkout this pack was SEALED against. Ruling (ф) moved the module
        # again, and this pack is the BEFORE column of `think-zero-shot`'s paired table, so it is
        # not re-pinned — the DERIVED pack is what carries the live sha, and it records what the
        # pin here was. Both halves, so a silent re-pin of the sealed file fails here.
        think = json.loads(
            (REPO_ROOT / "results" / "pass1_dev_pack_think.json").read_text(encoding="utf-8")
        )
        live = packs.summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py")
        assert think["instruments"]["parser"]["sha256"] == live
        assert block["parser"]["sha256"] == think["moved_from_the_shipped_pack"]["was"]["parser"]
        assert (
            block["moved_from_the_sealed_pack"]["parser.sha256"]
            == (SEALED["instruments"]["parser"]["sha256"])
        )
        assert pack["serving"] == SEALED["serving"]


def test_the_neighbour_similarity_is_the_measure_the_record_names():
    """The rule, re-derived on one item: the chosen neighbour really is the class's nearest."""
    item = leg(SHOT, "shot")["items"][0]
    labels = packs.pool()
    query = packs.grams(item["text"])
    for chosen in item["examples_chosen"]:
        candidates = [
            one
            for one in labels
            if one["thread"] != item["thread"] and packs.key(one["subject_type"]) == chosen["label"]
        ]
        best = max(packs.jaccard(query, one["grams"]) for one in candidates)
        assert chosen["similarity"] == round(best, 6), chosen
