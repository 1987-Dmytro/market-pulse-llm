"""The r2 re-draw pack — the exam and r1 stay out, the cap holds, and the draw is reproducible.

Same three properties as r1, plus the one r2 adds: **no unit of this pack was drawn for r1**. The
exam never enters it — no drawn unit sits in one of the seven exam threads and none of the 14 gold
msg-ids appears in the RENDERED page, checked against the rendered text and not against the unit
list, because a thread is rendered whole. The cap is a derivation and refuses to be a number
someone picked, and the reachability is a term of the target's own `min`. Nothing here asserts
anything about `docs/labels-pass1-r2.jsonl`: the team lead writes it, and an absence test is a
clock that flips with its artifact.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))


import build_pass1_label_pack_r2 as pack  # noqa: E402
import moved_pins  # noqa: E402

R1 = json.loads((REPO_ROOT / "results" / "pass1_label_pack_r1.json").read_text("utf-8"))

CONTRACT_EXCLUDED = tuple(sorted(R1["exclusion"]["threads"]))
"""The seven exam threads, from the record `docs/PROMPT-pass1-redraw.md` D1 names as their source.
The producer holds them to the probe pack they were derived from, and this is the expectation."""


@pytest.fixture(scope="module")
def state():
    return pack.measure()


@pytest.fixture(scope="module")
def built(state):
    return pack.build(state)


@pytest.fixture(scope="module")
def record(built):
    return built[0]


def test_the_pack_rebuilds_byte_identical_from_its_recorded_seed(tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"
    assert pack.main(["--outdir", str(first)]) == 0
    assert pack.main(["--outdir", str(second)]) == 0
    for name in (pack.RENDER_NAME, pack.PACK_NAME):
        assert (first / name).read_bytes() == (second / name).read_bytes(), name
    assert "generated_at" not in (first / pack.PACK_NAME).read_text(encoding="utf-8")
    assert str(tmp_path) not in (first / pack.PACK_NAME).read_text(encoding="utf-8")


def test_the_shipped_pack_is_what_the_producer_builds_today(tmp_path):
    """The rebuild is byte-identical EXCEPT where it pins a module that moved since.

    `docs/PROMPT-pass1-fewshot.md` D0.2 registered `pass1_comment_gm4_v2` in `prompts.py` and ruled
    old records' pins of it «moved since», not re-pinned. The registered TEXT this record was
    measured under has NOT moved, which is the property that keeps the evidence comparable, and it
    is asserted beside the diff ([[tests/moved_pins.py]]).

    Revision r2 added the second one: this pack BORROWED `scripts/window_summary_5c2.py`, which had
    to learn that the registry has revisions. That half of the expectation is derived from the
    rebuild rather than typed, so it empties itself when the registry is restored.
    """
    assert pack.main(["--outdir", str(tmp_path)]) == 0
    # The render carries no producer sha — every pin lives in the pack JSON below — so it compares
    # byte for byte with no allowance at all.
    assert (tmp_path / pack.RENDER_NAME).read_bytes() == (
        REPO_ROOT / pack.RENDER_NAME
    ).read_bytes()
    shipped = json.loads((REPO_ROOT / pack.PACK_NAME).read_text("utf-8"))
    rebuilt = json.loads((tmp_path / pack.PACK_NAME).read_text("utf-8"))
    moved = moved_pins.assert_only_the_prompts_pin_moved(shipped, rebuilt)
    assert moved == {"producer.borrowed.src/market_pulse/prompts.py"} | moved_pins.r2_paths_in(
        shipped, rebuilt
    )


def test_the_census_run_writes_nothing(tmp_path, capsys):
    """`--census` is D1, and D1 is read-only: it must print the table and touch no file."""
    before = sorted((one.name, one.stat().st_mtime_ns) for one in (REPO_ROOT / "results").iterdir())
    assert pack.main(["--census"]) == 0
    assert (
        sorted((one.name, one.stat().st_mtime_ns) for one in (REPO_ROOT / "results").iterdir())
        == before
    )
    out = capsys.readouterr().out
    assert "REACHABILITY BEFORE THE TARGET" in out
    assert "wrote" not in out


def test_the_exam_threads_are_the_r1_record_s_seven_and_are_re_derived(record):
    assert tuple(record["exclusion"]["threads"]) == CONTRACT_EXCLUDED
    assert len(CONTRACT_EXCLUDED) == 7


def test_the_exam_list_refuses_to_disagree_with_the_probe_pack(monkeypatch):
    """The negative control: the record's list is HELD to its derivation, not trusted."""
    stale = {"exclusion": {"threads": ["@nobody:1"]}}
    with pytest.raises(SystemExit, match="stale"):
        pack.excluded_threads(stale)


def test_no_drawn_unit_was_drawn_for_r1(record):
    r1_units = {(one["thread"], int(one["msg_id"])) for one in R1["units"]}
    assert [one for one in record["units"] if (one["thread"], one["msg_id"]) in r1_units] == []
    assert record["exclusion"]["proof"]["drawn_units_already_drawn_by_r1"] == []
    assert len(record["units"]) == len({(one["thread"], one["msg_id"]) for one in record["units"]})


def test_no_drawn_unit_sits_in_an_exam_thread(record):
    assert record["exclusion"]["proof"]["drawn_units_in_an_exam_thread"] == []
    assert [one for one in record["units"] if one["thread"] in CONTRACT_EXCLUDED] == []


def test_the_fourteen_gold_msg_ids_appear_nowhere_on_the_page(built):
    """Against the RENDERED text, because a thread is rendered whole and the units are not the
    only ids on the page."""
    _, rendering = built
    gold = pack.gold_msg_ids()
    assert len(gold) == 14
    assert [one for one in gold if str(one) in rendering] == []


def test_the_gold_ids_check_bites():
    """The negative control for the test above: a page carrying a gold id is caught."""
    gold = pack.gold_msg_ids()
    planted = f"a page that names `{gold[0]}` somewhere in it"
    assert [one for one in gold if str(one) in planted] == [gold[0]]


def test_the_codebook_leaks_no_bar_number_from_the_adjudication(built):
    """The elided sentence carried a gold row AND the bar it moved. The gold-id test covers the
    first; these are the second, and they are not msg_ids so nothing else would have caught them."""
    _, rendering = built
    figures = ("0.357", "0.429", "0.643")
    assert [one for one in figures if one in rendering] == []
    reading = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text("utf-8"))[
        "revision"
    ]["ruling"]["reading"]
    assert [one for one in figures if one in reading] == list(figures)


def test_the_r2_quote_stops_before_the_row_it_names():
    ruling = pack.r2_ruling()
    gold = pack.gold_msg_ids()
    full = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text("utf-8"))
    reading = full["revision"]["ruling"]["reading"]
    assert [one for one in gold if str(one) in reading] != []  # the source DOES name one
    assert [one for one in gold if str(one) in ruling["rule"]] == []  # the quote does not
    assert ruling["elided"]


def test_no_thread_is_allocated_more_than_its_available_pool_or_the_cap(record):
    rows = record["draw"]["per_thread"]
    assert all(row["weight"] == min(row["available"], record["draw"]["cap"]) for row in rows)
    assert all(row["allocated"] <= row["weight"] for row in rows)
    assert sum(row["allocated"] for row in rows) == record["draw"]["drawn"] == 150


def test_the_cap_leaves_the_target_reachable_and_names_what_binds(record):
    reach = record["draw"]["reachability"]
    assert reach["capped_weight_sum"] == 176
    assert reach["available"] == 468
    assert reach["reachable"] is True
    assert reach["capped_weight_sum"] >= reach["target"] == 150
    assert reach["binding"] == "ceiling"


def test_a_target_above_the_capped_ceiling_is_refused():
    """The reachability term is not decorative: 176 capped weights cannot fill 200."""
    weights = {f"t{index}": 4 for index in range(44)}
    with pytest.raises(SystemExit, match="cannot fill the pack"):
        pack.allocate(weights, 200)


def test_the_cap_refuses_to_stop_being_its_own_derivation():
    with pytest.raises(SystemExit, match="stopped being one"):
        pack.assert_cap_is_the_derivation([1] * 100 + [14] * 22, 13)


def test_the_cap_is_r1_s_cap_re_derived_not_copied(record, state):
    """The candidate subset IS r1's remaining population thread for thread, so the p90 of their
    payable counts must come out at r1's 14 — derived here, quoted from neither."""
    assert record["draw"]["cap"] == pack.percentile(state["sizes"], 0.90) == 14
    assert R1["draw"]["cap"] == 14
    assert len(state["candidates"]) == R1["population"]["threads_after_exclusion"] == 122


def test_the_candidate_rule_selects_the_whole_tract(record):
    """D1's finding, asserted so it fails if the population ever stops making it true: the shipped
    matcher's gate is what the reader cell was selected with, so every thread of it is a candidate.
    """
    assert record["population"]["the_candidate_rule_selects_the_whole_tract"] is True
    assert (
        record["population"]["candidate_threads"] == record["population"]["threads_in_cell"] == 129
    )
    assert record["population"]["threads_after_exam"] == 122


def test_the_volume_arithmetic_is_the_contract_s(record):
    population = record["population"]
    assert population["payable_in_candidates"] == 968
    assert population["already_drawn_by_r1"] == 500
    assert population["gold_rows_inside_candidates"] == 0
    assert population["available"] == 468
    assert population["payable_in_candidates"] - population["already_drawn_by_r1"] == 468
    assert "= 468 available" in population["arithmetic"]


def test_the_census_prices_every_definition_on_r1_s_own_labels(record):
    """The census's second half: what each candidate rule YIELDED where r1 already has answers."""
    table = record["census"]
    assert table["brand or category (D1's rule, = the shipped gate)"]["r1_rows_in_them"] == 500
    assert table["watchlist brand only"]["r1_ours_in_them"] == 0
    assert table["watchlist brand only"]["available"] == 30
    assert (
        table["category and no brand"]["r1_ours_share"]
        > table["brand or category (D1's rule, = the shipped gate)"]["r1_ours_share"]
    )


def test_the_census_prices_the_comment_level_rule_it_does_not_draw_on(record):
    """The one cut of this tract with a large lift — measured, and NOT the pack's rule. Its
    ceiling is the number the next ruling needs, so it is asserted rather than left in prose."""
    row = record["census"]["(not a thread rule) the COMMENT's own text hits"]
    assert row["payable"] == 59 and row["available"] == 21
    assert row["r1_ours_in_them"] == 14 and row["r1_rows_in_them"] == 38
    assert row["r1_ours_share"] > 0.35
    assert "not drawn on" in row["reading"]
    assert len({(one["thread"], one["msg_id"]) for one in record["units"]}) == 150


def test_the_codebook_carries_r1_s_law_by_the_same_bytes(built, record):
    _, rendering = built
    from market_pulse import prompts

    law = prompts.READER_ATTRIBUTION_LAW_V5
    assert law.strip() in rendering
    assert prompts.READER_CARRY_V5.strip() in rendering
    assert record["rendering"]["codebook"]["same_law_as_r1"] is True
    assert (
        record["rendering"]["codebook"]["attribution_law_sha256"]
        == R1["rendering"]["codebook"]["attribution_law_sha256"]
    )


def test_the_codebook_offers_the_four_readings_and_the_null(built):
    _, rendering = built
    from market_pulse import prompts

    for value in prompts.PASS1_SUBJECT_TYPES:
        assert f"`{value}`" in rendering
    assert "JSON `null`" in rendering
    assert "«категория» is NOT one of the four" in rendering


def test_the_rendering_shows_every_comment_of_a_rendered_thread(built, record):
    _, rendering = built
    raw = pack.raw_threads()
    rendered = {one["thread"] for one in record["units"]}
    assert len(rendered) == record["rendering"]["threads_rendered"] == 52
    for name in sorted(rendered)[:5]:
        for row in raw[name]["comments"]:
            assert f"**`{int(row['msg_id'])}`**" in rendering, (name, row["msg_id"])


def test_the_pack_names_the_labels_file_and_who_writes_it(record):
    assert record["labels"]["file"] == "docs/labels-pass1-r2.jsonl"
    assert "TEAM LEAD" in record["labels"]["written_by"]
    assert "--pack results/pass1_label_pack_r2.json" in record["labels"]["validator"]
    assert record["labels"]["values"][-1] is None


def test_no_blind_subset_is_drawn(record):
    assert record["blind"]["drawn"] == 0
    assert "blind-40" in record["blind"]["rule"]


def test_the_r1_producer_and_its_record_are_untouched(record):
    """r2 is a NEW producer because r1's is pinned by the r1 record's own `producer.sha256`."""
    assert record["producer"]["r1_producer_untouched"] is True
    assert record["producer"]["script"] == "scripts/build_pass1_label_pack_r2.py"
