"""The 901 still owed — and the one property that makes the pack safe to ship: nothing was rendered.

The r2 pack is a SUBTRACTION, not a build. Every check here is about that: the items are the r1
items byte for byte, the remainder is exactly the complement of what the r1 pod answered, and each of
the 131 subtracted ids was verified against its pack item's sha before it was removed. A pack rebuilt
from the population instead of copied would carry its own `rendering_sha256` values and would be a
different instrument answering the same question — the pod's handshake, rung 7 and D2's union census
all compare a reply's sha against this file.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass1_fewshot_packs as fewshot  # noqa: E402
import build_pass1_window_r2_pack as builder  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

R1 = json.loads((REPO_ROOT / "results" / "pass1_window_pack.json").read_text("utf-8"))
R2 = json.loads((REPO_ROOT / "results" / "pass1_window_r2_pack.json").read_text("utf-8"))
ANSWERED = [
    json.loads(line)
    for line in (REPO_ROOT / "results" / "pass1_window_v2.jsonl").read_text("utf-8").splitlines()
    if line.strip()
]


def test_the_pack_is_what_the_producer_writes_today(tmp_path):
    assert builder.main(["--out", str(tmp_path / "again.json")]) == 0
    assert (tmp_path / "again.json").read_text("utf-8") == (
        REPO_ROOT / "results" / "pass1_window_r2_pack.json"
    ).read_text("utf-8")


def test_the_901_are_EXACTLY_the_complement_and_in_the_r1_order():
    r1_ids = [one["id"] for one in R1["legs"][0]["items"]]
    r2_ids = [one["id"] for one in R2["legs"][0]["items"]]
    bought = {row["id"] for row in ANSWERED}
    assert len(r1_ids) == 1032 and len(bought) == 131
    assert set(r2_ids) == set(r1_ids) - bought
    assert len(r2_ids) == 901 == len(set(r2_ids))
    # the order is the r1 order with rows removed, not a re-sort
    assert r2_ids == [one for one in r1_ids if one not in bought]


def test_every_item_is_the_r1_ITEM_and_nothing_was_re_rendered():
    r1_by_id = {one["id"]: one for one in R1["legs"][0]["items"]}
    for item in R2["legs"][0]["items"]:
        assert item == r1_by_id[item["id"]], item["id"]
    # and the pack says so, with the sha of what it read
    assert R2["derived_from"]["pack_sha256"] == summary.sha256_of(
        REPO_ROOT / "results" / "pass1_window_pack.json"
    )
    assert R2["derived_from"]["subtracted"]["every_one_verified_by_rendering_sha256"] is True
    assert sorted(R2["derived_from"]["subtracted"]["ids"]) == sorted({r["id"] for r in ANSWERED})


def test_the_leg_writes_its_OWN_out_file_and_the_r1_one_is_untouched():
    assert R2["legs"][0]["out"] == "pass1_window_r2_v2.jsonl"
    assert R2["legs"][0]["out"] != R1["legs"][0]["out"]
    assert R2["legs"][0]["task"] == R1["legs"][0]["task"] == "pass1_comment_gm4_v2"
    assert len(R2["legs"]) == 1


def test_the_membership_sets_partition_the_window_with_what_r1_answered():
    """The union census is DERIVED from this pack: each set here plus what r1 bought is the whole."""
    window = R2["population"]
    assert (
        window["payable_comments_in_the_window"],
        window["answered_by_r1"],
        window["payable_comments"],
    ) == (1032, 131, 901)
    for name in ("gold_14", "probe_64", "labelled_650", "dev_200"):
        whole = window["membership_of_the_whole_window"][name]
        assert whole == R1["membership"][name]["n"]
        owed = R2["membership"][name]["n"]
        answered = whole - owed
        assert set(R2["membership"][name]["ids"]) == set(R1["membership"][name]["ids"]) - {
            row["id"] for row in ANSWERED
        }, name
        assert answered == len(
            set(R1["membership"][name]["ids"]) & {row["id"] for row in ANSWERED}
        ), name
    # and the counts corroborate the census's pair-keyed correction from a different code path:
    # the 650 owe 538, so 112 were answered — not the 117 the id-only key read
    assert R2["membership"]["labelled_650"]["n"] == 538
    assert 650 - 538 == 112
    assert R2["membership"]["dev_200"]["n"] == 152
    assert 200 - 152 == 48


def test_the_length_block_is_recomputed_over_the_901_and_the_ceiling_is_the_renderers():
    assert R2["length"] == fewshot.ceiling_check(R2["legs"][0]["items"])
    # the widest request of the window happens to be owed, so the headroom does not move
    assert R2["length"]["widest_request"] == R1["length"]["widest_request"]
    assert R2["length"]["headroom_chars"] == R1["length"]["headroom_chars"] > 0
    assert R2["length"]["widest_request_chars"] < R2["length"]["ceiling_chars"]
    # and the median DID move with the subset, so this is a measurement and not a copy
    assert R2["length"]["median_chars"] != R1["length"]["median_chars"]


def test_no_item_is_shown_a_neighbour_from_its_own_thread():
    assert R2["self_exclusion"]["items_shown_a_neighbour_from_their_own_thread"] == []
    assert R2["self_exclusion"]["distinct_neighbours_used"] > 0
    for item in R2["legs"][0]["items"]:
        assert all(near["thread"] != item["thread"] for near in item["examples_chosen"])


def test_the_per_thread_table_carries_BOTH_denominators():
    rows = {one["thread"]: one for one in R2["per_thread"]}
    assert len(rows) == len(R1["per_thread"]) == 129
    here = {}
    for item in R2["legs"][0]["items"]:
        here[item["thread"]] = here.get(item["thread"], 0) + 1
    for name, row in rows.items():
        assert row["payable_comments"] == here.get(name, 0), name
        assert (
            row["payable_comments"] + row["answered_by_r1"] == row["payable_comments_in_the_window"]
        ), name
    assert sum(one["payable_comments"] for one in R2["per_thread"]) == 901
    assert sum(one["payable_comments_in_the_window"] for one in R2["per_thread"]) == 1032


# ---- the refusals, driven on a cut-down copy of the real pack --------------------------------


def _fake(tmp_path, monkeypatch, keep: int = 6):
    """A small r1 pack + out-file the builder can be pointed at, derived from the real ones."""
    items = [dict(one) for one in R1["legs"][0]["items"][:keep]]
    pack = {
        **R1,
        "legs": [{**R1["legs"][0], "items": items}],
        "length": {**fewshot.ceiling_check(items), "stop_rule": R1["length"]["stop_rule"]},
        "population": {**R1["population"], "payable_comments": keep},
        "membership": {
            **{
                name: {
                    "n": sum(one["membership"][name] for one in items),
                    "ids": sorted(one["id"] for one in items if one["membership"][name]),
                }
                for name in ("gold_14", "probe_64", "labelled_650", "dev_200")
            },
            "rule": R1["membership"]["rule"],
        },
    }
    pack_path = tmp_path / "pack.json"
    pack_path.write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
    prereg = tmp_path / "prereg.json"
    prereg.write_text(
        json.dumps({"population": {"sha256": summary.sha256_of(pack_path)}}), encoding="utf-8"
    )
    out = tmp_path / "out.jsonl"
    rows = [
        {"id": one["id"], "rendering_sha256": one["rendering_sha256"], "reply": "{}"}
        for one in items[:2]
    ]
    out.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8"
    )
    monkeypatch.setattr(builder, "R1_PACK", pack_path)
    monkeypatch.setattr(builder, "R1_PREREG", prereg)
    monkeypatch.setattr(builder, "R1_OUT", out)
    return pack_path, prereg, out, rows


def test_the_fake_is_a_working_positive_control(tmp_path, monkeypatch):
    """The green path first: without it, every refusal below could be failing for another reason."""
    _fake(tmp_path, monkeypatch)
    built = builder.build()
    assert len(built["legs"][0]["items"]) == 4
    assert built["population"]["answered_by_r1"] == 2


def test_a_reply_whose_rendering_sha_is_not_the_packs_is_REFUSED(tmp_path, monkeypatch):
    _, _, out, rows = _fake(tmp_path, monkeypatch)
    rows[1]["rendering_sha256"] = "0" * 64
    out.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="answered a request this pack did not register"):
        builder.build()


def test_a_reply_the_leg_never_asked_is_REFUSED(tmp_path, monkeypatch):
    _, _, out, rows = _fake(tmp_path, monkeypatch)
    rows.append({"id": "@nobody:1#2", "rendering_sha256": "0" * 64, "reply": "{}"})
    out.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="which the r1 leg never asked"):
        builder.build()


def test_the_same_reply_twice_is_REFUSED(tmp_path, monkeypatch):
    _, _, out, rows = _fake(tmp_path, monkeypatch)
    rows.append(dict(rows[0]))
    out.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="twice"):
        builder.build()


def test_an_r1_pack_that_is_not_the_PINNED_one_is_REFUSED(tmp_path, monkeypatch):
    _, prereg, _, _ = _fake(tmp_path, monkeypatch)
    prereg.write_text(json.dumps({"population": {"sha256": "0" * 64}}), encoding="utf-8")
    with pytest.raises(SystemExit, match="sealed input of this build"):
        builder.build()


def test_a_remainder_that_is_not_the_populations_arithmetic_is_REFUSED(tmp_path, monkeypatch):
    pack_path, prereg, _, _ = _fake(tmp_path, monkeypatch)
    pack = json.loads(pack_path.read_text("utf-8"))
    pack["population"]["payable_comments"] = 99
    pack_path.write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
    prereg.write_text(
        json.dumps({"population": {"sha256": summary.sha256_of(pack_path)}}), encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="a number nobody priced"):
        builder.build()


def test_a_length_measurement_that_MOVED_is_REFUSED(tmp_path, monkeypatch):
    """The positive control inside the builder: re-measuring r1's own block must reproduce it."""
    pack_path, prereg, _, _ = _fake(tmp_path, monkeypatch)
    pack = json.loads(pack_path.read_text("utf-8"))
    pack["length"]["median_chars"] += 1
    pack_path.write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
    prereg.write_text(
        json.dumps({"population": {"sha256": summary.sha256_of(pack_path)}}), encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="the measurement moved"):
        builder.build()
