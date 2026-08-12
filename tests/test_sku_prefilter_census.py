"""The text leg's frame: the script is driven, not imported, and the shipped record is checked.

The frame decides which rows sku-b may spend a paid attempt on, so two properties matter more than
the counts: the two carriers are never blended, and the filter's own exam (one positive, three
negatives) is taken before any yield is read.
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import sku_prefilter_census as census  # noqa: E402

from market_pulse import positions, yield_screen  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.lexicon import load_lexicon  # noqa: E402
from market_pulse.registry import (  # noqa: E402
    load_registry,
    registry_before_the_latin_aliases,
)

REGISTRY = load_registry(REPO_ROOT / "config" / "registry.yaml")
LEXICON = load_lexicon(census.LEXICON, taxonomy=REGISTRY.taxonomy)
COMPILED = yield_screen.compile_categories(LEXICON)
DRAFT = REPO_ROOT / "data" / "category_lexicon_draft.json"
ALIASES = yield_screen.compile_aliases(watchlist_aliases(REGISTRY.watchlist))


def test_the_controls_are_the_exam_and_all_four_pass():
    """One positive and three negatives. The fitness post is the yield screen's own control, reused
    because it has the SHAPE of a hit — a food-adjacent feed, a discount, a percentage — and the
    conjunction is the only thing that rejects it."""
    controls = census.run_controls(COMPILED, ALIASES)
    assert len(controls) == 4
    assert sum(1 for c in controls.values() if c["kind"] == "negative") == 3
    assert all(control["ok"] for control in controls.values())
    positive = next(c for c in controls.values() if c["kind"] == "positive")
    assert positive["measured"]["hit"].startswith("category:dairy")
    for control in controls.values():
        if control["kind"] == "negative":
            assert control["measured"] is None


def test_a_control_that_starts_passing_is_caught(monkeypatch):
    """The negative control on the exam itself: a filter that passed everything would report four
    OKs unless `ok` is computed per direction. Proved by making the filter say yes to everything."""
    monkeypatch.setattr(census.positions, "prefilter", lambda *a, **k: {"line": "x"})
    controls = census.run_controls(COMPILED, ALIASES)
    assert [name for name, c in controls.items() if not c["ok"]] == [
        name for name, c in controls.items() if c["kind"] == "negative"
    ]


def test_the_script_runs_over_one_channel_and_keeps_the_carriers_apart(tmp_path):
    """Driven through `main`, because an import proves nothing: the write path is where the frame,
    the hash and the git block are built."""
    out = tmp_path / "census.json"
    assert census.main(["--out", str(out), "--only", "@VARUS_channel"]) == 0
    record = json.loads(out.read_text(encoding="utf-8"))
    assert [row["handle"] for row in record["channels"]] == ["@VARUS_channel"]
    cells = record["channels"][0]["carriers"]
    assert set(cells) == {"post_text", "comment"}
    assert cells["post_text"]["passed"] > 0 and cells["comment"]["passed"] > 0
    assert {row["carrier"] for row in record["rows"]} == {"post_text", "comment"}
    # every frame row belongs to a cell, and the cells sum to the frame — no blending, no leakage
    assert len(record["rows"]) == sum(cell["passed"] for cell in cells.values())
    assert record["frame"]["rows"] == len(record["rows"])
    assert record["frame_reportable"] is True


def test_the_frame_is_deterministic_and_its_hash_covers_the_order_it_is_written_in(tmp_path):
    """A run whose draw cannot be reproduced is not a frame. Two passes, same ids, same hash — and
    the hash is over the ids in the record's own order, so a reordered frame is a different one."""
    first, second = tmp_path / "a.json", tmp_path / "b.json"
    census.main(["--out", str(first), "--only", "@VARUS_channel"])
    census.main(["--out", str(second), "--only", "@VARUS_channel"])
    a, b = (json.loads(path.read_text(encoding="utf-8")) for path in (first, second))
    assert [row["id"] for row in a["rows"]] == [row["id"] for row in b["rows"]]
    assert a["frame"]["ids_sha256"] == b["frame"]["ids_sha256"]
    assert a["rows"] == b["rows"], "the evidence lines are part of the frame, not decoration"


def test_an_unknown_handle_stops_the_run(tmp_path):
    with pytest.raises(SystemExit, match="does not carry"):
        census.main(["--out", str(tmp_path / "x.json"), "--only", "@nosuchchannel"])


def test_the_shipped_record_is_refused_a_second_pass():
    """The frame is what the pack's manifest pins, so a pass over a moved corpus must not be able to
    land under the name the pack cites (D68)."""
    assert census.RECORD.exists()
    with pytest.raises(SystemExit, match="already exists"):
        census.main([])


# --- the shipped record ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def shipped():
    return json.loads(census.RECORD.read_text(encoding="utf-8"))


def test_the_shipped_record_covers_the_signed_composition(shipped):
    """The registry sha is the one the frame was selected under, and since SPEC 3.17 (13)(b) that
    is a reconstruction rather than the live file: three Latin aliases landed after this census was
    sealed. The composition itself did not move, which is why the handle set is still compared
    against today's registry — an alias amendment may not add or drop a channel."""
    live = {handle for source in REGISTRY.sources for handle in source.telegram_channels}
    assert {row["handle"] for row in shipped["channels"]} == live
    assert shipped["summary"]["channels"] == len(live) == 66
    pinned = shipped["sources_read"]["registry"]["sha256"]
    assert pinned != census.sha256_of(census.REGISTRY)
    assert pinned == hashlib.sha256(registry_before_the_latin_aliases(census.REGISTRY)).hexdigest()
    assert shipped["frame_reportable"] is True
    assert all(control["ok"] for control in shipped["controls"].values())


def test_the_record_names_the_lexicon_it_was_run_against_and_the_law_says_the_same(shipped):
    """uni-b moved this script onto `config/lexicon.yaml` (SPEC 3.17 (8)). The record predates that
    and is a DO-NOT: it names the draft it actually read, by sha, and that stays true. What makes
    the migration safe for a sealed frame is the second half — the law carries the draft's stems and
    endings, so the filter that selected these 769 rows is the filter the law compiles today.
    """
    read = shipped["sources_read"]["lexicon"]
    assert read["path"] == "data/category_lexicon_draft.json"
    assert read["status"] == "draft-not-law"
    assert read["sha256"] == census.sha256_of(DRAFT)
    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    assert LEXICON["tracked"] == draft["tracked"] and LEXICON["endings"] == draft["endings"]
    assert read["known_collision"] == LEXICON["known_collision"]


def test_the_shipped_frame_adds_up_and_its_hash_reproduces(shipped):
    """Every count is re-derived from the enumeration beside it, so a hand-edited total breaks."""
    import hashlib

    ids = [row["id"] for row in shipped["rows"]]
    assert len(set(ids)) == len(ids) == shipped["frame"]["rows"]
    assert (
        hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest() == shipped["frame"]["ids_sha256"]
    )
    by_carrier = shipped["frame"]["by_carrier"]
    for carrier, cell in by_carrier.items():
        assert cell["passed"] == sum(1 for row in shipped["rows"] if row["carrier"] == carrier)
        assert cell["passed"] == sum(
            row["carriers"][carrier]["passed"] for row in shipped["channels"]
        )
        # the looser reading can only be wider, never narrower: dropping a constraint cannot lose a row
        assert cell["passed_row_level"] >= cell["passed"]
        for kind, count in cell["passed_carrying"].items():
            assert count <= cell["passed"], kind
    assert sum(cell["passed"] for cell in by_carrier.values()) == shipped["frame"]["rows"]


def test_the_shipped_numbers_are_the_ones_reported(shipped):
    """The report and the record cannot drift: these are the figures quoted to the team lead."""
    posts, comments = shipped["frame"]["by_carrier"].values()
    assert (posts["with_text"], posts["passed"], posts["passed_row_level"]) == (14388, 717, 1092)
    assert (comments["with_text"], comments["passed"], comments["passed_row_level"]) == (
        10875,
        52,
        60,
    )
    assert shipped["frame"]["rows"] == 769
    assert posts["passed_carrying"] == {"currency": 226, "percent": 384, "size": 478}
    assert comments["passed_carrying"] == {"currency": 20, "percent": 24, "size": 16}


def test_every_frame_row_still_passes_the_filter_it_was_selected_by(shipped):
    """The frame is re-derived from the stores for 30 sampled rows: a record whose rows no longer
    pass would be describing a corpus that moved under it."""
    rows = {row["id"]: row for row in shipped["rows"]}
    sampled = sorted(rows)[::26]  # a spread over channels, not the head of one
    assert len(sampled) >= 25
    for item in sampled:
        handle, msg_id = item.rsplit(":", 1)
        folder = census.POSTS if rows[item]["carrier"] == "post_text" else census.COMMENTS
        store = census.load_jsonl(folder / f"{handle.lstrip('@')}.jsonl")
        source = next(row for row in store if row["msg_id"] == int(msg_id))
        found = positions.prefilter(source, COMPILED, ALIASES)
        assert found is not None, item
        assert found["hit"] == rows[item]["hit"] and found["line"] == rows[item]["line"]


def test_the_files_outside_the_signed_composition_are_named_and_not_dropped(shipped):
    """15 post stores and one comment store belong to channels the registry no longer carries —
    @dikankaa, @tretyakovaele, @znishkom and the rest of the 5c1 exclusions. A frame that silently
    skipped them would look identical to one that never had them."""
    outside = shipped["sources_read"]["outside_the_registry"]
    live = {
        handle.lstrip("@") for source in REGISTRY.sources for handle in source.telegram_channels
    }
    for path in outside:
        assert Path(path).stem not in live
    assert "data/raw/posts/dikankaa.jsonl" in outside
    assert "data/raw/comments/tretyakovaele.jsonl" in outside
    assert all(count >= 0 for count in outside.values())


def test_the_record_says_what_it_did_not_read(shipped):
    """Captions and `comments_v2` are both deliberate omissions, and an omission nobody wrote down
    is indistinguishable from an oversight."""
    rule = shipped["rule"]
    assert "captions_excluded" in rule and "SAMPLE" in rule["captions_excluded"]
    assert "reply_to_msg_id" in shipped["sources_read"]["comments_v2_note"]
    assert shipped["sources_read"]["stores"] == ["data/raw/posts", "data/raw/comments"]
