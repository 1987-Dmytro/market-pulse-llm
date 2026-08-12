"""The B′ pre-registration: it must not exist yet, and it must be right when it does.

Two halves. The first is that the producer REFUSES while a decomposition pair is pending — four
are, so `results/sku_pilot_prereg_b2.json` is not on disk and this suite is what says why. The
second is that the refusal is not the only thing tested: every test below drives the whole build
against a decomposition whose four pending rows are resolved in the fixture, so the gold arithmetic,
the key-space re-mapping and the leaf-by-leaf comparison against v4 are exercised now rather than
discovered at the acceptance.

The fixture's four verdicts are **hypothetical and are never written anywhere**. They are class `a`
because that is the reading that changes the denominator LEAST, so a test that passes under them is
not passing because the fixture removed the hard cases.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse.registry import registry_before_the_latin_aliases  # noqa: E402


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


writer = _script("write_sku_prereg_b2")
v4 = writer.v4

HYPOTHETICAL = "hypothetical, resolved only inside this test fixture"


@pytest.fixture(scope="module")
def shipped_decomposition():
    return json.loads(writer.DECOMPOSITION.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def resolved(shipped_decomposition):
    read = json.loads(json.dumps(shipped_decomposition))
    for row in read["rows"]:
        if row["verdict"] == read["pending_status"]:
            row["verdict"], row["mechanism"] = "a", HYPOTHETICAL
    read["counts"] = {**read["counts"], "a": read["counts"]["a"] + 4, "pending": 0}
    return read


@pytest.fixture(scope="module")
def record(resolved, tmp_path_factory):
    return writer.build(resolved, tmp_path_factory.mktemp("b2") / "prereg_b2.json")


@pytest.fixture(scope="module")
def previous():
    return json.loads(writer.SUPERSEDED.read_text(encoding="utf-8"))


# --- the refusal ------------------------------------------------------------------------------


def test_the_record_is_not_on_disk_and_the_producer_says_why(shipped_decomposition, tmp_path):
    """Four pairs are pending, so B′ has no denominator yet. The refusal names them by number."""
    assert not writer.RECORD.exists()
    assert [
        row["n"]
        for row in shipped_decomposition["rows"]
        if row["verdict"] == shipped_decomposition["pending_status"]
    ] == [4, 9, 28, 29]
    out = tmp_path / "b2.json"
    with pytest.raises(
        SystemExit, match=r"4 missed pair\(s\) are still PENDING_TEAM_LEAD: \[4, 9, 28, 29\]"
    ):
        writer.main(["--out", str(out)])
    assert not out.exists(), "a refusing producer must not leave a partial registration behind"


def test_one_pending_pair_is_enough_to_refuse(resolved, tmp_path):
    """The negative control on the guard above: it must fire on ONE, not only on four, or it is a
    threshold nobody chose."""
    read = json.loads(json.dumps(resolved))
    read["rows"][3]["verdict"] = read["pending_status"]
    path = tmp_path / "one.json"
    path.write_text(json.dumps(read, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit, match=r"1 missed pair\(s\) are still"):
        writer.main(["--decomposition", str(path), "--out", str(tmp_path / "b2.json")])


def test_the_resolved_fixture_actually_builds(record):
    """Otherwise every test below would be passing on a producer that only knows how to refuse."""
    assert record["phase"].startswith("skub2")
    assert record["class"].startswith("PRE-REGISTRATION")


# --- the gold (13)(c) re-scopes -----------------------------------------------------------------


def test_the_denominator_is_the_55_minus_the_b_and_c_pairs(record, resolved):
    gold = record["bars"]["leaflet_brand_recall"]["gold"]
    leaving = [row for row in resolved["rows"] if row["verdict"] in ("b", "c")]
    assert gold["pairs_v4"] == 55
    assert gold["removed"] == len(leaving) == 14
    assert gold["pairs"] == 55 - 14 == 41
    assert sum(len(post["gold_keys"]) for post in gold["per_post"]) == gold["pairs"]
    assert sorted(gold["removed_pairs"]) == sorted(
        [row["item"], row["gold_key"]] for row in leaving
    )


def test_class_a_pairs_stay_because_they_are_the_exam(record, resolved):
    """The misses instrument v2 exists to fix. Removing them would be marking its own paper."""
    gold = record["bars"]["leaflet_brand_recall"]["gold"]
    kept = {(post["item"], key) for post in gold["per_post"] for key in post["gold_keys"]}
    a_pairs = [row for row in resolved["rows"] if row["verdict"] == "a"]
    assert len(a_pairs) == 15  # 11 dictated + the 4 the fixture resolves
    for row in a_pairs:
        # the pair is still in the denominator, under whichever key today's alias table gives it
        assert any(item == row["item"] for item, _ in kept), row["n"]
        assert (row["item"], row["gold_key"]) not in set(map(tuple, gold["removed_pairs"]))


def test_the_rescope_empties_four_posts_and_they_leave_the_recall_average(record):
    """R3's own rule, applied rather than rewritten: an empty gold set is a precision probe. Four
    posts carried exactly one gold key, all ruled class b, so the macro mean is over 11 not 15."""
    gold = record["bars"]["leaflet_brand_recall"]["gold"]
    assert gold["posts_emptied_by_the_rescope"] == [
        "@atb_market_official:4377",
        "@atb_market_official:4411",
        "@atb_market_official:4421",
        "@atb_market_official:4498",
    ]
    assert gold["posts_with_a_non_empty_gold_set"] == 11
    assert len(gold["posts_with_an_empty_gold_set"]) == 8  # v4's 4 + these 4
    for item in gold["posts_emptied_by_the_rescope"]:
        assert item in gold["posts_with_an_empty_gold_set"]


def test_the_asymmetry_is_measured_and_split_rather_than_asserted_away(record):
    """(13)(c) can only remove MISSES, so the same brand can be out of the denominator on one post
    and in it on another. Nine pairs sit that way, and the two halves are not the same thing: six
    were FOUND by v1 (pairs v2 will very likely find again) and three are class-a misses."""
    block = record["bars"]["leaflet_brand_recall"]["gold"]["asymmetry_reported_never_gated"]
    assert block["n"] == 9
    assert block["by_what_the_pair_was"] == {"a": 3, "found by v1": 6}
    assert len(block["pairs"]) == 9
    assert {pair["gold_key_v4"] for pair in block["pairs"]} == {
        "raw:svoia-liniia",
        "raw:каштан",
    }
    assert "gating nothing" in block["reading"]
    assert any(line["id"] == "B4" for line in record["ratification_required"])


# --- the key space (13)(b) moved -----------------------------------------------------------------


def test_the_gold_is_rebuilt_under_the_new_alias_table_and_never_prefix_stripped(record):
    """«Rud» and «LIMO» became display names of their own brand_ids, so two keys change SHAPE. The
    join to the decomposition happens in the v4 space and the gold is written in today's; a `raw:`
    prefix stripped to bridge them would also have matched `raw:try-vedmedi` to `try-vedmedi`."""
    by_post = {
        post["msg_id"]: post for post in record["bars"]["leaflet_brand_recall"]["gold"]["per_post"]
    }
    assert "raw:rud" in by_post[4340]["gold_keys_v4"] and "rud" in by_post[4340]["gold_keys"]
    assert "raw:rud" not in by_post[4340]["gold_keys"]
    assert "raw:limo" in by_post[4360]["gold_keys_v4"] and "limo" in by_post[4360]["gold_keys"]
    # try-vedmedi's Latin form is «Three Bears», which is NOT its brand_id, so its key is unmoved
    assert "raw:try-vedmedi" in by_post[4340]["gold_keys_v4"]
    assert "raw:try-vedmedi" in by_post[4340]["gold_keys"]
    assert "try-vedmedi" not in by_post[4340]["gold_keys"]


def test_every_v4_key_is_reproduced_from_the_reviewers_names(record):
    """The producer's own guard, standing on the shipped reference: re-keying the reviewer's names
    under the v4 table has to give back exactly the gold_keys the sealed record stores, or the
    join that removes the b/c pairs is landing on keys nobody wrote."""
    for post in record["bars"]["leaflet_brand_recall"]["gold"]["per_post"]:
        removed = {name["gold_key_v4"] for name in post["removed"]}
        assert removed <= set(post["gold_keys_v4"]), post["item"]
        assert len(post["gold_keys"]) == len(set(post["gold_keys_v4"]) - removed), post["item"]


def test_a_removed_pair_that_matches_no_reviewer_name_refuses(resolved, tmp_path):
    read = json.loads(json.dumps(resolved))
    # a class-b row, because only b and c rows are what (13)(c) tries to remove
    ruled_out = next(row for row in read["rows"] if row["verdict"] == "b")
    ruled_out["gold_key"] = "raw:nobody-wrote-this"
    path = tmp_path / "d.json"
    path.write_text(json.dumps(read, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit, match="match no reviewer name"):
        writer.main(["--decomposition", str(path), "--out", str(tmp_path / "b2.json")])


# --- what did NOT move ----------------------------------------------------------------------------


def test_the_three_bars_are_byte_equal_apart_from_bar_ones_gold(record, previous):
    moved = writer.check_the_bars_did_not_move(record, previous)
    assert moved == ["leaflet_brand_recall.gold"]
    for name, bar in record["bars"].items():
        assert bar["verbatim"] == previous["bars"][name]["verbatim"] == v4.BARS[name], name
        assert bar["threshold"] == previous["bars"][name]["threshold"], name
    assert record["bars"]["price_pair_accuracy"] == previous["bars"]["price_pair_accuracy"]
    assert record["bars"]["text_tier_accuracy"] == previous["bars"]["text_tier_accuracy"]
    assert record["ladder"] == previous["ladder"]


def test_a_moved_bar_text_stops_the_write(record, previous):
    """The negative control on the check above — it has to fire, or 'byte-equal' is a sentence."""
    tampered = json.loads(json.dumps(record))
    tampered["bars"]["text_tier_accuracy"]["verbatim"] += " (tightened)"
    with pytest.raises(SystemExit, match="verbatim text or threshold moved"):
        writer.check_the_bars_did_not_move(tampered, previous)
    widened = json.loads(json.dumps(record))
    widened["bars"]["price_pair_accuracy"]["threshold"] = 0.7
    with pytest.raises(SystemExit, match="verbatim text or threshold moved"):
        writer.check_the_bars_did_not_move(widened, previous)


def test_the_prompts_are_v4s_copied_and_not_recomputed(record, previous):
    for task in ("positions_post_gm4", "positions_text_gm4"):
        assert record["instruments"][task] == previous["instruments"][task]
    assert "no new ML mechanism" in record["instruments"]["note"]


# --- the pin set ------------------------------------------------------------------------------------


def test_the_spec_pin_keeps_thirteen_and_strips_the_six_before_it(record, previous):
    """v1–v4 pin a law with EVERY ratification block off, because each predates all of them. B′ is
    registered UNDER (13), so a pin over a law without it would not hold the authority for this
    run. Checked three ways: it is not the live file, it is not v4's pin, and the block is in it."""
    pinned = record["pinned_inputs"]["docs/SPEC.md"]
    live = hashlib.sha256(writer.SPEC.read_bytes()).hexdigest()
    assert pinned != live
    assert pinned != previous["pinned_inputs"]["docs/SPEC.md"]
    law = v4.registered_law(writer.SPEC, keep=(writer.KEEP_BLOCK,)).decode("utf-8")
    assert hashlib.sha256(law.encode("utf-8")).hexdigest() == pinned
    assert "sku-b-ratification-7 begin" in law
    for name in ("sku-b-ratification-2", "sku-b-ratification-6"):
        assert name not in law, name
    assert "800 → **1200**" in law, "the amendment this run is registered under, in the pinned law"


def test_keeping_a_block_the_file_does_not_carry_refuses():
    with pytest.raises(SystemExit, match="asked to keep"):
        v4.registered_law(writer.SPEC, keep=("sku-b-ratification-99",))


def test_the_registry_is_pinned_LIVE_because_the_aliases_are_the_instrument(record, previous):
    """The opposite of every earlier registration, and for a stated reason: (13)(b) is part of
    instrument v2, so B′ registers the amended alias table rather than the one v4 read."""
    pinned = record["pinned_inputs"]["config/registry.yaml"]
    assert pinned == hashlib.sha256(writer.REGISTRY.read_bytes()).hexdigest()
    assert pinned != previous["pinned_inputs"]["config/registry.yaml"]
    assert (
        previous["pinned_inputs"]["config/registry.yaml"]
        == hashlib.sha256(registry_before_the_latin_aliases(writer.REGISTRY)).hexdigest()
    )
    assert "pinned LIVE" in record["pinned_inputs_note"]


def test_the_three_halves_of_instrument_v2_are_each_pinned_where_they_can_be_read(record):
    block = record["instruments"]["instrument_v2"]
    for half, path in (
        ("parser", writer.PARSER),
        ("serving_pin", writer.SERVING_V2),
        ("registry", writer.REGISTRY),
    ):
        assert block[half]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest(), half
        assert record["pinned_inputs"][block[half]["path"]] == block[half]["sha256"], half
    assert (
        record["pinned_inputs"]["results/sku_miss_decomposition.json"]
        == hashlib.sha256(writer.DECOMPOSITION.read_bytes()).hexdigest()
    )


def test_every_pinned_input_hashes_to_what_it_says(record):
    for path, sha in record["pinned_inputs"].items():
        if path == "docs/SPEC.md":
            continue  # the stripped law, above
        assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == sha, path


# --- the attempt --------------------------------------------------------------------------------


def test_the_cap_the_phase_and_the_ledger_are_registered_together(record, previous):
    assert record["attempts"]["cap_usd"] == writer.CAP_USD == 0.40
    assert record["attempts"]["phase"] == "skub2"
    assert record["attempts"]["ledger"] == "results/spend_skub2.json"
    assert record["attempts"]["ledger"] != previous["attempts"]["ledger"]
    assert record["attempts"]["phase"] != previous["attempts"]["phase"]
    assert record["attempts"]["on_failure"] == previous["attempts"]["on_failure"]


def test_the_population_is_all_138_and_says_that_this_is_a_reading(record):
    """(11)(a) says exactly-once across the program and (13)(d) says «the same 138 elements». The
    two need reconciling and the record does it out loud instead of quietly picking one."""
    assert record["population"]["elements"] == 138
    assert "supersedes (11)(a) HERE" in record["population"]["reading"]
    assert "resume" not in record, "this is not a resumed session and must not look like one"
    assert any(line["id"] == "B1" for line in record["ratification_required"])


def test_it_names_the_two_mechanisms_thirteen_refuses_to_authorise(record):
    out = record["not_in_scope"]["the two candidates (13) names and does not authorise"]
    assert "two-stage OCR" in out and "brands_visible channel" in out
    assert "no new ML mechanism is authorised" in out
    assert "#4, #9, #28 and #29" in record["not_in_scope"]["the four pending pairs"]
