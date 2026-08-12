"""The miss pack: the contract's checksums, one post checked by hand, and the pins that hold.

The happy path runs over the REAL artifacts — the pack has no arithmetic of its own to fake with a
fixture, and what it must get right is exactly the join between the shipped bar, the reference gold
and the merged dump. Each refusal tampers with one input only, so the guard it names is the guard
it reaches; the whole-population test above is their positive control.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_sku_miss_pack as packer  # noqa: E402


@pytest.fixture(scope="module")
def pack(tmp_path_factory) -> dict:
    out = tmp_path_factory.mktemp("pack")
    assert packer.main(["--out", str(out / "pack.json"), "--sheet", str(out / "pack.md")]) == 0
    written = json.loads((out / "pack.json").read_text(encoding="utf-8"))
    written["_sheet_text"] = (out / "pack.md").read_text(encoding="utf-8")
    return written


def run(tmp_path, **overrides) -> int:
    args = {"--out": str(tmp_path / "pack.json"), "--sheet": str(tmp_path / "pack.md")}
    args.update(overrides)
    return packer.main([item for pair in args.items() for item in pair])


def copy_of(tmp_path: Path, source: Path, mutate) -> Path:
    """The real artifact, altered by `mutate`, written beside the test's own output."""
    target = tmp_path / source.name
    loaded = json.loads(source.read_text(encoding="utf-8"))
    mutate(loaded)
    target.write_text(json.dumps(loaded, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def test_the_contract_s_checksums_hold_over_the_real_population(pack):
    assert pack["checksums"] == {"posts": 15, "missed": 29, "found": 26}
    assert pack["checksums"] == packer.EXPECTED
    assert len(pack["missed"]) == 29 and len(pack["found"]) == 26 and len(pack["posts"]) == 15
    assert pack["bar"]["value"] == 0.3603174603
    assert pack["bar"]["verdict"] == "FAIL"
    assert pack["bar"]["n_gold_keys"] == 55


def test_every_missed_row_is_joinable_and_carries_no_verdict(pack):
    assert [row["n"] for row in pack["missed"]] == list(range(1, 30))
    keys = [(row["item"], row["gold_key"]) for row in pack["missed"]]
    assert len(set(keys)) == 29, "a dictated verdict has to join exactly one row"
    assert all(row["verdict"] is None for row in pack["missed"])
    # the contract asks for the post's sent pages on the missed pair itself, not one level up
    pages_of = {post["item"]: post["pages"] for post in pack["posts"]}
    assert all(row["pages"] == pages_of[row["item"]] for row in pack["missed"])
    assert all(row["written_by_the_reviewer"] for row in pack["missed"])


def test_the_flags_ride_on_the_rows_they_decide(pack):
    """16 and 5 — the two numbers the read is reported with, and the rows that carry neither."""
    on_unreadable = [row["n"] for row in pack["missed"] if row["unreadable_pages"]]
    on_unmatched = [row["n"] for row in pack["missed"] if row["unmatched_extractions_on_this_post"]]
    assert len(on_unreadable) == 16
    assert len(on_unmatched) == 5
    assert set(on_unmatched) == {1, 2, 6, 7, 8}  # 4340 (2 rows) and 4381 (3)
    # the negative control: a post with a clean page set flags nothing
    clean = [row for row in pack["missed"] if row["msg_id"] == 4350]
    assert clean and not any(row["unreadable_pages"] for row in clean)
    assert not any(row["unmatched_extractions_on_this_post"] for row in clean)


def test_post_4340_by_hand(pack):
    """Three gold keys, one found, two missed, one unreadable page, one unmatched extraction — the
    only post in the population that exercises every answer state and both flags."""
    post = next(row for row in pack["posts"] if row["msg_id"] == 4340)
    assert post["gold_keys"] == ["raw:rud", "raw:svoia-liniia", "raw:try-vedmedi"]
    assert post["found"] == ["raw:svoia-liniia"]
    assert post["missed"] == ["raw:rud", "raw:try-vedmedi"]
    assert post["unmatched_extractions"] == ["raw:three bears"]
    assert (post["pages_sent"], post["pages_available"], post["pages_not_sent"]) == (6, 10, 4)
    assert post["recall"] == pytest.approx(1 / 3)

    assert [page["answer"] for page in post["pages"]] == [
        "empty",
        "positions",
        "unreadable",
        "positions",
        "positions",
        "empty",
    ]
    assert post["pages"][1]["brand_raw"] == ["Three Bears", "Three Bears"]
    assert post["pages"][1]["file"].endswith("atb_market_official_4341.jpg")
    assert post["pages"][2]["unreadable_reason"] == "printed discount '-50%*' is not a percentage"
    assert post["pages"][2]["brand_raw"] == []
    assert post["unreadable_pages"] == [
        {
            "page": 3,
            "file": "data/annotation/captions_5c1/posts_media/atb_market_official_4342.jpg",
            "reason": "printed discount '-50%*' is not a percentage",
        }
    ]

    missed = [row for row in pack["missed"] if row["msg_id"] == 4340]
    assert [row["gold_key"] for row in missed] == ["raw:rud", "raw:try-vedmedi"]
    assert missed[0]["written_by_the_reviewer"] == [{"source": "watchlist_hits", "written": "rud"}]
    assert missed[0]["registry_display_names"] == ["Рудь"]
    assert missed[1]["registry_display_names"] == ["Три Ведмеді", "Три Медведя"]

    found = next(row for row in pack["found"] if row["msg_id"] == 4340)
    assert found["gold_key"] == "raw:svoia-liniia"
    assert [hit["page"] for hit in found["carried_by"]] == [4, 5]
    assert all(hit["brand_raw"] == ["Своя Лінія"] for hit in found["carried_by"])
    # page 4's positions are filed under page 4's own image, here and on all 62 page rows below
    assert found["carried_by"][0]["file"] == post["pages"][3]["file"]


def test_the_page_a_position_is_filed_under_is_the_page_it_is_printed_beside(pack):
    """The outcome is joined by FILE and the positions by PAGE NUMBER; nothing else asserts that
    the two numberings agree, and a sheet that printed one page's brands under another page's name
    would send the read to the wrong image without ever looking wrong."""
    dump = REPO_ROOT / "results" / "sku_b_positions_v4.jsonl"
    rows = [json.loads(line) for line in dump.read_text(encoding="utf-8").splitlines() if line]
    filed, checked = {}, 0
    for row in rows:
        if row["page"] is not None:
            filed.setdefault((row["item"], row["page"]), set()).add(row["file"])
    for post in pack["posts"]:
        for page in post["pages"]:
            for name in filed.get((post["item"], page["page"]), set()):
                assert name == page["file"]
                checked += 1
    # all 22 pages that carried a position sit on a scoreable post: the four posts with an empty
    # gold set are the precision probe, and the instrument named nothing on any of them
    assert checked == 22


def test_it_refuses_a_position_filed_under_another_page(tmp_path, monkeypatch):
    """The negative control for the guard above: the same dump with one row's page number moved."""
    real = packer.page_answers

    def shifted(post, record, dump):
        for row in dump:
            if row["item"] == "@atb_market_official:4340" and row["page"] == 2:
                row["page"] = 1
        monkeypatch.setattr(packer, "page_answers", real)
        return real(post, record, dump)

    monkeypatch.setattr(packer, "page_answers", shifted)
    with pytest.raises(
        SystemExit, match="page 1 is .*4340.jpg in the reference and the dump files"
    ):
        run(tmp_path)


def test_a_post_with_nothing_on_one_side_says_so(pack):
    """4426 missed nothing and six posts found nothing — an empty bold heading in a document a
    human scans reads as data that failed to render."""
    sheet = pack["_sheet_text"]
    assert sheet.count("**MISSED — to be ruled on**\n\n- — none") == 1
    assert sheet.count("**FOUND — the control half**\n\n- — none") == 6
    assert [post["msg_id"] for post in pack["posts"] if not post["missed"]] == [4426]
    assert sum(1 for post in pack["posts"] if not post["found"]) == 6


def test_a_name_the_reviewer_wrote_is_reproduced_as_written(pack):
    """The parenthetical IS the evidence a (c) verdict would be about — never cleaned up."""
    written = {row["gold_key"]: row["written_by_the_reviewer"] for row in pack["missed"]}
    assert written["raw:frenzy (рудь)"] == [
        {"source": "other_dairy_brands", "written": "Frenzy (Рудь)"}
    ]
    assert written["raw:комо / komo"] == [
        {"source": "other_dairy_brands", "written": "Комо / Komo"}
    ]
    assert written["raw:svoia-liniia"] == [{"source": "watchlist_hits", "written": "svoia-liniia"}]


def test_the_sheet_ends_with_an_empty_verdict_line_per_missed_pair(pack):
    rows = [line for line in pack["_sheet_text"].splitlines() if line.startswith("| ")]
    template = [line for line in rows if line.rstrip().endswith("|  |")]
    assert len(template) == 29, "one line per missed pair, and every verdict cell empty"
    assert all(f"| {n} |" in line for n, line in zip(range(1, 30), template))
    for name, text in packer.CLASSES.items():
        assert f"- **{name}** — {text}" in pack["_sheet_text"]
    assert "@atb_market_official:4340" in pack["_sheet_text"]
    assert "«Три Ведмеді» / «Три Медведя»" in pack["_sheet_text"]


def test_it_refuses_a_gold_that_moved_under_the_registration(tmp_path):
    moved = copy_of(tmp_path, packer.REFERENCE, lambda gold: gold.update(touched=True))
    with pytest.raises(SystemExit, match="leaflet gold .* hashes"):
        run(tmp_path, **{"--reference": str(moved)})


def test_it_refuses_a_dump_that_is_not_the_records_own(tmp_path):
    dump = tmp_path / "dump.jsonl"
    lines = (REPO_ROOT / "results" / "sku_b_positions_v4.jsonl").read_text(encoding="utf-8")
    dump.write_text(lines + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="dump .* hashes"):
        run(tmp_path, **{"--dump": str(dump)})


def test_it_refuses_a_shipped_bar_one_that_is_not_this_bar(tmp_path):
    def drop_a_miss(shipped):
        post = shipped["bars"]["leaflet_brand_recall"]["per_post"][0]
        post["missed"] = post["missed"][1:]

    moved = copy_of(tmp_path, packer.VERDICTS, drop_a_miss)
    with pytest.raises(SystemExit, match="differ on \\['@atb_market_official:4340'\\]"):
        run(tmp_path, **{"--verdicts": str(moved)})


def test_it_refuses_a_shipped_value_that_is_not_the_recomputed_one(tmp_path):
    def move_the_value(shipped):
        shipped["bars"]["leaflet_brand_recall"]["value"] = 0.9

    moved = copy_of(tmp_path, packer.VERDICTS, move_the_value)
    with pytest.raises(SystemExit, match="recomputes to 0.3603174603 and the shipped record"):
        run(tmp_path, **{"--verdicts": str(moved)})


def test_it_refuses_counts_the_contract_does_not_state(tmp_path, monkeypatch):
    monkeypatch.setattr(packer, "EXPECTED", {"posts": 15, "missed": 28, "found": 26})
    with pytest.raises(SystemExit, match="the pack counts .* and the contract states"):
        run(tmp_path)


def test_the_shipped_pack_is_the_one_this_script_writes(tmp_path):
    """The artifact in `results/` and the producer, on the same inputs, are the same file — the
    `git` block excepted, which names the tree the run happened on and moves with every commit."""
    assert packer.OUT.exists() and packer.SHEET.exists()
    assert run(tmp_path) == 0
    fresh = json.loads((tmp_path / "pack.json").read_text(encoding="utf-8"))
    shipped = json.loads(packer.OUT.read_text(encoding="utf-8"))
    assert shipped["sheet"] == "results/sku_miss_pack.md"
    for record in (fresh, shipped):
        record.pop("git")  # names the tree the run happened on, and this one is a later tree
        record.pop("sheet")  # the test wrote its copy elsewhere
    assert fresh == shipped
    assert (tmp_path / "pack.md").read_text("utf-8") == packer.SHEET.read_text("utf-8")
