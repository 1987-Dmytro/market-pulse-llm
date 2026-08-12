"""The B′ pre-registration: the refusal that held it back, and the record it writes now.

For one contract this suite said the record must NOT exist: four decomposition pairs were pending,
the producer refused, and every test drove the build against a fixture that resolved them
hypothetically. SPEC 3.17 (14)(a) read all four — class b, with the pages each was read on — so the
fixture is gone and the tests stand on the shipped decomposition itself.

What did NOT go is the refusal. `pending` below re-opens one row on a copy, because a guard whose
trigger has been retired is a guard nothing exercises — and this one is the difference between a
denominator that was signed and one that moved after it was.
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


@pytest.fixture(scope="module")
def shipped_decomposition():
    return json.loads(writer.DECOMPOSITION.read_text(encoding="utf-8"))


@pytest.fixture
def pending(shipped_decomposition):
    """The shipped read with row 4 put back to PENDING_TEAM_LEAD — the state (14)(a) closed.

    A copy, and never written to `results/`: the point is to keep the refusal under test now that
    nothing on disk can fire it.
    """
    read = json.loads(json.dumps(shipped_decomposition))
    row = next(row for row in read["rows"] if row["n"] == 4)
    row["verdict"], row["mechanism"] = read["pending_status"], None
    read["counts"] = {**read["counts"], "b": read["counts"]["b"] - 1, "pending": 1}
    return read


@pytest.fixture(scope="module")
def record(shipped_decomposition, tmp_path_factory):
    return writer.build(shipped_decomposition, tmp_path_factory.mktemp("b2") / "prereg_b2.json")


@pytest.fixture(scope="module")
def previous():
    return json.loads(writer.SUPERSEDED.read_text(encoding="utf-8"))


# --- the refusal ------------------------------------------------------------------------------


def test_nothing_is_pending_any_more_and_the_denominator_is_a_number(shipped_decomposition):
    """SPEC 3.17 (14)(a). The condition the producer refused on is gone, and `final` is 37."""
    assert shipped_decomposition["pending_rows"] == []
    assert not [
        row["n"]
        for row in shipped_decomposition["rows"]
        if row["verdict"] == shipped_decomposition["pending_status"]
    ]
    assert shipped_decomposition["counts"] == {"a": 11, "b": 16, "c": 2, "pending": 0, "rows": 29}
    assert shipped_decomposition["b_prime_denominator"]["final"] == 37


def test_one_pending_pair_is_still_enough_to_refuse(pending, tmp_path):
    """The guard kept under test after its trigger retired: it fires on ONE, not only on four, and
    it leaves nothing behind. A registration whose denominator can still move is not one."""
    path = tmp_path / "one.json"
    path.write_text(json.dumps(pending, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "b2.json"
    with pytest.raises(SystemExit, match=r"1 missed pair\(s\) are still PENDING_TEAM_LEAD: \[4\]"):
        writer.main(["--decomposition", str(path), "--out", str(out)])
    assert not out.exists(), "a refusing producer must not leave a partial registration behind"


def test_the_shipped_decomposition_actually_builds(record):
    """Otherwise every test below would be passing on a producer that only knows how to refuse."""
    assert record["phase"].startswith("skub2")
    assert record["class"].startswith("PRE-REGISTRATION")


# --- the gold (13)(c) re-scopes -----------------------------------------------------------------


def test_the_denominator_is_the_55_minus_the_b_and_c_pairs(record, shipped_decomposition):
    """SPEC 3.17 (14)(c)'s 37, arrived at independently: 55 gold pairs less the 18 ruled b or c."""
    gold = record["bars"]["leaflet_brand_recall"]["gold"]
    leaving = [row for row in shipped_decomposition["rows"] if row["verdict"] in ("b", "c")]
    assert gold["pairs_v4"] == 55
    assert gold["removed"] == len(leaving) == 18
    assert gold["pairs"] == 55 - 18 == 37
    assert sum(len(post["gold_keys"]) for post in gold["per_post"]) == gold["pairs"]
    assert sorted(gold["removed_pairs"]) == sorted(
        [row["item"], row["gold_key"]] for row in leaving
    )


def test_class_a_pairs_stay_because_they_are_the_exam(record, shipped_decomposition):
    """The misses instrument v2 exists to fix. Removing them would be marking its own paper."""
    gold = record["bars"]["leaflet_brand_recall"]["gold"]
    kept = {(post["item"], key) for post in gold["per_post"] for key in post["gold_keys"]}
    a_pairs = [row for row in shipped_decomposition["rows"] if row["verdict"] == "a"]
    assert len(a_pairs) == 11
    for row in a_pairs:
        # the pair is still in the denominator, under whichever key today's alias table gives it
        assert any(item == row["item"] for item, _ in kept), row["n"]
        assert (row["item"], row["gold_key"]) not in set(map(tuple, gold["removed_pairs"]))


def test_the_rescope_empties_five_posts_and_they_leave_the_recall_average(record):
    """SPEC 3.17 (14)(c): «37 pairs over 10 posts … five posts empty and become precision probes
    under R3». R3's own rule applied rather than rewritten, and the macro mean is over 10, not 15.
    4391 is the fifth, and it is 4391 because (14)(a) ruled its `svoia-liniia` pair class b."""
    gold = record["bars"]["leaflet_brand_recall"]["gold"]
    assert gold["posts_emptied_by_the_rescope"] == [
        "@atb_market_official:4377",
        "@atb_market_official:4391",
        "@atb_market_official:4411",
        "@atb_market_official:4421",
        "@atb_market_official:4498",
    ]
    assert gold["posts_with_a_non_empty_gold_set"] == 10
    assert len(gold["posts_with_an_empty_gold_set"]) == 9  # v4's 4 + these 5
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
        "raw:try-vedmedi",
        "raw:каштан",
    }
    # (14)(b) rules them IN, and the ruling is quoted here rather than summarised
    assert "RULED by 3.17 (14)(b)" in block["reading"]
    assert writer.RULINGS["B4"] in block["reading"]
    b4 = next(line for line in record["ratification_required"] if line["id"] == "B4")
    assert writer.RULINGS["B4"] in b4["ruled_by"]


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


def test_a_removed_pair_that_matches_no_reviewer_name_refuses(shipped_decomposition, tmp_path):
    read = json.loads(json.dumps(shipped_decomposition))
    # a class-b row, because only b and c rows are what (13)(c) tries to remove
    ruled_out = next(row for row in read["rows"] if row["verdict"] == "b")
    ruled_out["gold_key"] = "raw:nobody-wrote-this"
    path = tmp_path / "d.json"
    path.write_text(json.dumps(read, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit, match="match no reviewer name"):
        writer.main(["--decomposition", str(path), "--out", str(tmp_path / "b2.json")])


# --- what did NOT move ----------------------------------------------------------------------------


def test_the_three_bars_are_byte_equal_apart_from_the_rescoped_leaves(record, previous):
    """The law's words do not move; the registration's READING of them does, and exactly on the
    four leaves that count posts and pairs. Enumerated literally in the producer so a fifth cannot
    slip in behind this check."""
    moved = writer.check_the_bars_did_not_move(record, previous)
    assert sorted(moved) == [
        "leaflet_brand_recall.denominator",
        "leaflet_brand_recall.excluded",
        "leaflet_brand_recall.gold",
        "leaflet_brand_recall.reachable",
    ]
    assert sorted(writer.MOVED_BY_THE_RESCOPE) == ["denominator", "excluded", "gold", "reachable"]
    for name, bar in record["bars"].items():
        assert bar["verbatim"] == previous["bars"][name]["verbatim"] == v4.BARS[name], name
        assert bar["threshold"] == previous["bars"][name]["threshold"], name
    assert record["bars"]["price_pair_accuracy"] == previous["bars"]["price_pair_accuracy"]
    assert record["bars"]["text_tier_accuracy"] == previous["bars"]["text_tier_accuracy"]
    assert record["ladder"] == previous["ladder"]


def test_the_readings_that_count_posts_follow_the_rescope(record, previous):
    """The failure this catches is silent and expensive. Inherited from v4, bar 1 would carry
    `denominator` = «the 15 posts … all 55 pairs», `reachable` = «15 of 19», and an `excluded` list
    of FOUR posts — beside a gold of 37 pairs over 10. B5 would ask the team lead to ratify 10
    while the machine-readable fields said 15."""
    bar = record["bars"]["leaflet_brand_recall"]
    assert len(bar["excluded"]["posts"]) == 9
    assert "the 10 posts" in bar["denominator"] and "37 pairs" in bar["denominator"]
    assert "10 of 19" in bar["reachable"] and "37 pairs" in bar["reachable"]
    for stale in ("the 15 posts", "55 pairs", "the 11 posts", "41 pairs"):
        assert stale not in bar["denominator"] and stale not in bar["reachable"], stale
    assert len(previous["bars"]["leaflet_brand_recall"]["excluded"]["posts"]) == 4
    assert "class b or c" in bar["excluded"]["why_this_list_grew"]
    # and the law's own words are untouched, which is the half the contract holds byte-equal
    assert bar["verbatim"] == previous["bars"]["leaflet_brand_recall"]["verbatim"]
    assert bar["threshold"] == previous["bars"]["leaflet_brand_recall"]["threshold"] == 0.75


def test_the_excluded_list_is_the_one_bar_one_checks_before_it_scores(record):
    """`sku_bar_verdicts.bar_one` opens by comparing `excluded.posts` against the reference's own
    empty-gold list and refuses if they differ. With v4's four inherited, that comparison would
    MATCH the sealed reference and wave a 15-post scoring through — in the v4 key space, missing
    `rud` and `limo` by arithmetic, at the one paid attempt. With B′'s nine it refuses instead,
    until skub2-run points the scorer at this record's own gold."""
    reference = json.loads(writer.REFERENCE.read_text(encoding="utf-8"))
    sealed = set(reference["gold"]["posts_with_an_empty_gold_set"])
    bar = record["bars"]["leaflet_brand_recall"]
    assert set(bar["excluded"]["posts"]) == set(bar["gold"]["posts_with_an_empty_gold_set"])
    assert len(sealed) == 4
    assert set(bar["excluded"]["posts"]) > sealed, "B′ excludes the sealed four and five more"
    assert set(bar["excluded"]["posts"]) != sealed, "so bar_one refuses the sealed reference"


def test_the_sentence_beside_the_excluded_list_counts_the_same_posts_it_does(record, previous):
    """Dv209's shape, caught a second time by (14)(a). The sentence used to be typed — «the four new
    ones each carried exactly one gold key» — beside a computed list, and four more class-b pairs
    turned the four into five. It is computed now, and this drives the function on a fake where the
    numbers are different, so a re-typed literal would show up as a sentence that stopped moving."""
    bar = record["bars"]["leaflet_brand_recall"]
    gold = bar["gold"]
    sentence = bar["excluded"]["why_this_list_grew"]
    assert (
        f"v4 excluded {len(previous['bars']['leaflet_brand_recall']['excluded']['posts'])}"
        in sentence
    )
    assert f"B′ excludes {len(bar['excluded']['posts'])} posts" in sentence
    assert f"The {len(gold['posts_emptied_by_the_rescope'])} new ones" in sentence
    assert "exactly 1 gold key each" in sentence

    faked = json.loads(json.dumps({"posts": gold["per_post"]}))
    faked["posts"][0] = {**faked["posts"][0], "gold_keys_v4": ["x", "y", "z"], "gold_keys": []}
    other = writer.why_this_list_grew(previous, faked, bar["excluded"]["posts"] + ["fake"])
    assert other != sentence
    assert "B′ excludes 10 posts" in other and "between 1 and 3 gold keys" in other


def test_an_excluded_list_that_disagrees_with_the_gold_stops_the_write(record, previous):
    """The negative control on the equality above — the producer has to refuse, not warn."""
    tampered = json.loads(json.dumps(record))
    tampered["bars"]["leaflet_brand_recall"]["excluded"]["posts"] = previous["bars"][
        "leaflet_brand_recall"
    ]["excluded"]["posts"]
    with pytest.raises(SystemExit, match="that equality is what sku_bar_verdicts.bar_one checks"):
        writer.check_the_bars_did_not_move(tampered, previous)


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


def test_the_spec_pin_keeps_thirteen_and_fourteen_and_strips_the_rest(record, previous):
    """v1–v4 pin a law with EVERY ratification block off, because each predates all of them. B′ is
    registered UNDER (13) AND (14) — (13) authorises the re-measurement, (14) fixes the gold this
    record carries and the cap it enforces — so a pin over a law without either would not hold the
    authority for this run. Checked four ways: it is not the live file, it is not v4's pin, both
    blocks are in it, and the sentences the record quotes are too."""
    pinned = record["pinned_inputs"]["docs/SPEC.md"]
    live = hashlib.sha256(writer.SPEC.read_bytes()).hexdigest()
    assert pinned != live
    assert pinned != previous["pinned_inputs"]["docs/SPEC.md"]
    law = v4.registered_law(writer.SPEC, keep=writer.KEEP_BLOCKS).decode("utf-8")
    assert hashlib.sha256(law.encode("utf-8")).hexdigest() == pinned
    assert writer.KEEP_BLOCKS == ("sku-b-ratification-7", "sku-b-ratification-8")
    for name in writer.KEEP_BLOCKS:
        assert f"{name} begin" in law, name
    for name in ("sku-b-ratification-2", "sku-b-ratification-6"):
        assert name not in law, name
    assert "800 → **1200**" in law, "the amendment this run is registered under, in the pinned law"
    assert "$0.65" in law and "a=11 · b=16 · c=2" in law
    # a pin that kept only (13) is a different hash — the control that says the eighth block counts
    thirteen_only = v4.registered_law(writer.SPEC, keep=("sku-b-ratification-7",))
    assert hashlib.sha256(thirteen_only).hexdigest() != pinned


def test_every_ruling_the_record_quotes_is_in_the_law_as_written(record):
    """The rule `check_the_bars_are_the_laws` applies to the bars, applied to (14)'s rulings: a
    registration that paraphrases the amendment it is made under cannot be held to it. The
    negative control matters more than the check — a substring test passes on almost anything."""
    writer.check_the_quoted_rulings_are_the_law(writer.SPEC)
    law = writer.law_without_emphasis(writer.SPEC)
    for name, quote in writer.RULINGS.items():
        assert quote in law, name
    ruled = {line["id"]: line["ruled_by"] for line in record["ratification_required"]}
    assert set(ruled) == {"B1", "B2", "B3", "B4", "B5"}
    for name in ruled:
        assert writer.RULINGS[name] in ruled[name], name
    assert record["attempts"]["cap_verbatim"] == writer.RULINGS["cap"]


def test_a_paraphrased_ruling_refuses(monkeypatch):
    monkeypatch.setitem(writer.RULINGS, "B5", "B5 follows: the gold is about forty pairs")
    with pytest.raises(SystemExit, match="the ruling quoted for B5 is not in docs/SPEC.md"):
        writer.check_the_quoted_rulings_are_the_law(writer.SPEC)


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
    assert record["attempts"]["cap_usd"] == writer.CAP_USD == 0.65
    assert record["attempts"]["phase"] == "skub2"
    assert record["attempts"]["ledger"] == "results/spend_skub2.json"
    assert record["attempts"]["ledger"] != previous["attempts"]["ledger"]
    assert record["attempts"]["phase"] != previous["attempts"]["phase"]
    assert record["attempts"]["on_failure"] == previous["attempts"]["on_failure"]


def test_the_superseded_cap_is_quoted_unedited_beside_the_one_that_applies(record):
    """(13)(d)'s own sentence says «cap $0.40» and (14)(e) supersedes it. The verbatim is NOT tidied
    to match — a law quoted with its number swapped is not the law — so the record carries both
    sentences, each named by the clause it came from, and `cap_usd` follows (14)(e)."""
    attempts = record["attempts"]
    assert "cap $0.40" in attempts["verbatim"]
    assert "(13)(d)" in attempts["verbatim_source"]
    assert (
        "$0.65" in attempts["cap_verbatim"]
        and "superseding (13)(d)'s $0.40" in (attempts["cap_verbatim"])
    )
    assert "(14)(e)" in attempts["cap_verbatim_source"]
    assert attempts["cap_usd"] == 0.65


def test_the_population_is_all_138_and_says_that_this_is_a_reading(record):
    """(11)(a) says exactly-once across the program and (13)(d) says «the same 138 elements». The
    two need reconciling and the record does it out loud instead of quietly picking one."""
    assert record["population"]["elements"] == 138
    assert "supersedes (11)(a) HERE" in record["population"]["reading"]
    assert writer.RULINGS["B1"] in record["population"]["reading"]
    assert "resume" not in record, "this is not a resumed session and must not look like one"
    assert any(line["id"] == "B1" for line in record["ratification_required"])


def test_it_names_the_two_mechanisms_thirteen_refuses_to_authorise(record):
    out = record["not_in_scope"]["the two candidates (13) names and does not authorise"]
    assert "two-stage OCR" in out and "brands_visible channel" in out
    assert "no new ML mechanism is authorised" in out
    read = record["not_in_scope"]["the four pairs that were pending"]
    assert "#4, #9, #28 and #29" in read and "3.17 (14)(a)" in read


def test_the_open_lines_are_kept_whole_and_every_one_of_them_is_ruled(record):
    """A registration records the question as well as the answer: what B4's losing reading was, and
    that it was put BEFORE the run. So no line is deleted when it is ruled — `ruled_by` is added
    beside it, and the note says the list is closed."""
    lines = record["ratification_required"]
    assert [line["id"] for line in lines] == ["B1", "B2", "B3", "B4", "B5"]
    for line in lines:
        assert line["ruled_by"], line["id"]
        assert line["question"] and line["if_refused"], line["id"]
    assert "every line below is RULED" in record["ratification_required_note"]


# --- the shipped witness -------------------------------------------------------------------------


def test_the_shipped_registration_is_the_one_this_script_writes(record):
    """`results/sku_pilot_prereg_b2.json` is on disk from SPEC 3.17 (14)(a) onwards, and it is a
    PRE-run witness: `generated_at` and `git` are the two fields a rebuild legitimately moves, and
    everything else has to be what the producer computes from the shipped decomposition today."""
    shipped = json.loads(writer.RECORD.read_text(encoding="utf-8"))
    assert shipped.pop("git")["commit"]
    assert shipped.pop("generated_at")
    fresh = {key: value for key, value in record.items() if key not in ("git", "generated_at")}
    assert shipped == fresh


def test_the_written_registration_is_never_rewritten(tmp_path):
    """A pre-registration regenerated after the run carries a timestamp from after it. There is no
    --force, and the refusal fires on the shipped path — which is the one that matters."""
    assert writer.RECORD.exists()
    with pytest.raises(SystemExit, match="already exists"):
        writer.main([])
    copy = tmp_path / "b2.json"
    copy.write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit, match="already exists"):
        writer.main(["--out", str(copy)])
    assert copy.read_text(encoding="utf-8") == "{}"
