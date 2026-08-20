"""The labelling pack — the exclusion is PROVED, the cap holds, and the draw is reproducible.

Three properties carry this pack and each one has a test that can fail. The exam never enters it:
no drawn unit shares a thread with any of the 64 registered probe units, and none of the 14 gold
msg-ids appears in either RENDERED document — checked against the rendered text and not against the
unit list, because the rendering shows every comment of a thread and not only the drawn ones. The
cap is a derivation and refuses to be a number someone picked. And the whole pack rebuilds byte for
byte from its recorded seed, which is what makes «drawn under seed 20260818» a checkable sentence.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass1_label_pack as pack  # noqa: E402
import moved_pins  # noqa: E402

CONTRACT_EXCLUDED = (
    "@VARUS_channel:10348",
    "@VARUS_channel:10613",
    "@mandziak:3676",
    "@mandziak:3703",
    "@matusi_ukr:22242",
    "@matusi_ukr:22272",
    "@matusi_ukr:22303",
)
"""`docs/PROMPT-pass1-data-prep.md`'s expectation, carried as the EXPECTATION and never as the
source: the producer derives the list from the probe pack's items and this is what it is held to."""


@pytest.fixture(scope="module")
def built():
    """One build for the whole module — two window passes are 4 s and nothing here mutates it."""
    return pack.build()


@pytest.fixture(scope="module")
def record(built):
    return built[0]


def test_the_pack_rebuilds_byte_identical_from_its_recorded_seed(tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"
    assert pack.main(["--outdir", str(first)]) == 0
    assert pack.main(["--outdir", str(second)]) == 0
    for name in (pack.RENDER_NAME, pack.BLIND_NAME, pack.PACK_NAME):
        assert (first / name).read_bytes() == (second / name).read_bytes(), name
    assert "generated_at" not in (first / pack.PACK_NAME).read_text(encoding="utf-8")


def test_the_shipped_pack_is_what_the_producer_builds_today(tmp_path):
    """The rebuild is byte-identical EXCEPT where it pins `src/market_pulse/prompts.py`.

    `docs/PROMPT-pass1-fewshot.md` D0.2 registered `pass1_comment_gm4_v2` in that module and ruled
    old records' pins of it «moved since», not re-pinned. The registered TEXT this record was
    measured under has NOT moved, which is the property that keeps the evidence comparable, and it
    is asserted beside the diff ([[tests/moved_pins.py]]).
    """
    assert pack.main(["--outdir", str(tmp_path)]) == 0
    for name in (pack.RENDER_NAME, pack.BLIND_NAME):
        assert (tmp_path / name).read_bytes() == (REPO_ROOT / name).read_bytes(), name
    shipped = json.loads((REPO_ROOT / pack.PACK_NAME).read_text("utf-8"))
    rebuilt = json.loads((tmp_path / pack.PACK_NAME).read_text("utf-8"))
    moved = moved_pins.assert_only_the_prompts_pin_moved(shipped, rebuilt)
    assert moved == {"producer.borrowed.src/market_pulse/prompts.py"}
    assert (
        shipped["rendering"]["codebook"]["attribution_law_sha256"]
        == (rebuilt["rendering"]["codebook"]["attribution_law_sha256"])
    )


def test_the_excluded_threads_are_derived_and_are_the_contract_s_seven():
    assert tuple(pack.excluded_threads()) == CONTRACT_EXCLUDED


def test_the_sixty_four_probe_units_are_the_payable_set_of_those_seven(record):
    """The exclusion removes 64 payable comments and not 64 ± k — which is why the arithmetic
    below is a subtraction and not an estimate."""
    assert record["exclusion"]["the_units_are_the_payable_set"] is True
    assert record["exclusion"]["probe_units"] == 64
    assert record["exclusion"]["payable_removed"] == 64


def test_the_volume_arithmetic_is_the_contract_s(record):
    population = record["population"]
    assert population["payable_in_cell"] == 1032
    assert population["threads_in_cell"] == 129
    assert population["payable_after_exclusion"] == 968
    assert population["threads_after_exclusion"] == 122
    assert population["payable_in_cell"] - 64 == population["payable_after_exclusion"]
    assert record["draw"]["target"] == min(500, population["payable_after_exclusion"]) == 500
    assert record["draw"]["drawn"] == 500
    assert len(record["units"]) == 500


def test_no_drawn_unit_shares_a_thread_with_a_probe_unit(record):
    excluded = set(record["exclusion"]["threads"])
    assert not [unit for unit in record["units"] if unit["thread"] in excluded]
    assert record["exclusion"]["proof"]["drawn_units_sharing_a_thread_with_a_probe_unit"] == []


def test_the_fourteen_gold_msg_ids_appear_in_neither_rendering(built):
    """Against the RENDERED text, because a thread is rendered whole and the units are not the
    only ids on the page ([[a_test_that_reads_a_shipped_artifact]] is why it is rebuilt here)."""
    _, rendering, blind = built
    gold = pack.gold_msg_ids()
    assert len(gold) == 14
    assert [one for one in gold if str(one) in rendering] == []
    assert [one for one in gold if str(one) in blind] == []


def test_the_gold_ids_check_bites():
    """The negative control for the test above: a page carrying a gold id is caught."""
    gold = pack.gold_msg_ids()
    planted = f"a page that names `{gold[0]}` somewhere in it"
    assert [one for one in gold if str(one) in planted] == [gold[0]]


def test_no_thread_is_allocated_more_than_the_cap(record):
    rows = record["draw"]["per_thread"]
    assert all(row["allocated"] <= row["weight"] <= pack.CAP for row in rows)
    assert sum(row["allocated"] for row in rows) == record["draw"]["drawn"]
    assert max(row["allocated"] for row in rows) == 12


def test_the_cap_leaves_the_target_reachable(record):
    reach = record["draw"]["reachability"]
    assert reach["capped_weight_sum"] == 572
    assert reach["reachable"] is True
    assert reach["capped_weight_sum"] >= reach["target"]


def test_a_cap_that_cannot_fill_the_pack_is_refused():
    """The reachability check is not decorative: at CAP = 9 this population cannot fill 500."""
    weights = {f"t{index}": 9 for index in range(50)}
    with pytest.raises(SystemExit, match="cannot fill the pack"):
        pack.allocate(weights, 500)


def test_the_cap_refuses_to_stop_being_its_own_derivation(monkeypatch):
    monkeypatch.setattr(pack, "CAP", 13)
    with pytest.raises(SystemExit, match="stopped being one"):
        pack.assert_cap_is_the_derivation([1] * 100 + [14] * 22)


def test_the_largest_thread_is_named_by_its_size_and_not_by_its_allocation(record):
    """Thirteen threads share the top allocation of 12 and one of them is the 125-comment thread."""
    share = record["draw"]["largest_thread_share"]
    rows = record["draw"]["per_thread"]
    assert share["payable"] == max(row["payable"] for row in rows) == 125
    assert [row for row in rows if row["thread"] == share["thread"]][0]["payable"] == 125
    assert share["allocated"] == 12
    assert share["uncapped_would_be"] == 65


def test_the_codebook_carries_the_attribution_law_and_the_carve_out_by_the_same_bytes(built):
    from market_pulse import prompts

    _, rendering, blind = built
    for text in (rendering, blind):
        assert prompts.READER_ATTRIBUTION_LAW_V5.strip() in text
        assert prompts.READER_CARRY_V5.strip() in text
    # and the law is the one the pass-1 prompt itself answers under, not a second wording of it
    assert prompts.READER_ATTRIBUTION_LAW_V5 in prompts.PASS1_COMMENT_PROMPT
    assert "READER_ATTRIBUTION_LAW_V5" in rendering


def test_the_codebook_offers_the_four_readings_and_the_null(built):
    from market_pulse import prompts

    _, rendering, _ = built
    for value in prompts.PASS1_SUBJECT_TYPES:
        assert f"`{value}`" in rendering
    assert len(prompts.PASS1_SUBJECT_TYPES) == 4
    assert "JSON `null`" in rendering
    assert "«категория» is NOT one of the four" in rendering


def test_the_r2_quote_stops_before_the_row_it_names():
    """The adjudication is quoted; the sentence naming a gold msg_id, its gold value and the bar it
    moved is not. The elision is declared in the record and in the page."""
    ruling = pack.r2_ruling()
    gold = pack.gold_msg_ids()
    full = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text("utf-8"))
    reading = full["revision"]["ruling"]["reading"]
    assert [one for one in gold if str(one) in reading] != []  # the source DOES name one
    assert [one for one in gold if str(one) in ruling["rule"]] == []  # the quote does not
    assert ruling["elided"]


def test_the_rendering_shows_every_comment_of_a_rendered_thread(built, record):
    """«payable or not, in order» — the labeller reads the conversation and not the drawn subset."""
    _, rendering, _ = built
    threads = pack.raw_threads()
    name = record["draw"]["largest_thread_share"]["thread"]
    body = rendering.split(f"`{name}` — ")[1].split("\n### ")[0]
    for row in threads[name]["comments"]:
        assert f"**`{int(row['msg_id'])}`**" in body
    assert body.count("⬛ **TARGET**") == 12


def test_the_blind_forty_are_drawn_units_and_are_unlabelled(record, built):
    _, _, blind = built
    units = {(one["thread"], one["msg_id"]) for one in record["units"]}
    chosen = [(one["thread"], one["msg_id"]) for one in record["blind_units"]]
    assert len(chosen) == 40 == len(set(chosen))
    assert set(chosen) <= units
    assert "subject_type" not in blind.split("## Threads")[1]


def test_the_two_zero_payable_threads_are_not_rendered(record):
    rows = record["draw"]["per_thread"]
    silent = [row["thread"] for row in rows if not row["allocated"]]
    assert record["rendering"]["threads_with_no_target"] == sorted(silent)
    assert all(row["payable"] == 0 for row in rows if row["thread"] in silent)
    assert record["rendering"]["threads_rendered"] == 120


def test_the_pack_names_who_writes_the_labels(record):
    assert record["labels"]["file"] == "docs/labels-pass1-r1.jsonl"
    assert "TEAM LEAD" in record["labels"]["written_by"]
    assert (REPO_ROOT / "docs" / "labels-pass1-r1.jsonl").exists()


def test_the_codebook_leaks_no_bar_number_from_the_adjudication(built):
    """The elided sentence carried a gold row AND the bar it moved. The gold-id test covers the
    first; these are the second, and they are not msg_ids so nothing else would have caught them."""
    _, rendering, blind = built
    figures = ("0.357", "0.429", "0.643")
    for text in (rendering, blind):
        assert [one for one in figures if one in text] == []
    # the control: the record the quote is cut from does carry them
    reading = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text("utf-8"))[
        "revision"
    ]["ruling"]["reading"]
    assert [one for one in figures if one in reading] == list(figures)
