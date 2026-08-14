"""The sitting pack — drawn under a recorded seed, and every rail it ships with.

The sitting is the last thing between the run and the phase closing, and it is the one artifact
whose defects are invisible at the table: a caption measured on other bytes, a picture that is not
the one that was sent, a slot quietly pre-filled. Each of those has a test here, and each of them
is checked in the direction that FAILS — a refusal beside the pass that says the guard
discriminates.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_validate_pack as builder  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import loop, positions  # noqa: E402

PACK = REPO_ROOT / "results" / "validate_5c2_pack.json"
PAGE = REPO_ROOT / "results" / "validate_5c2_pack.html"
AGGREGATES = json.loads((REPO_ROOT / "results" / "window_summary_5c2.json").read_text("utf-8"))


@pytest.fixture(scope="module")
def pack() -> dict:
    return json.loads(PACK.read_text(encoding="utf-8"))


def mirror(tmp_path: Path, drop: str | None = None) -> Path:
    """`data/derived/` as symlinks — the shas are the real ones, so only the gap is the variable."""
    root = tmp_path / "derived"
    for path in sorted(summary.DERIVED.rglob("*.jsonl")):
        inside = path.relative_to(summary.DERIVED)
        if str(inside) == drop:
            continue
        (root / inside).parent.mkdir(parents=True, exist_ok=True)
        (root / inside).symlink_to(path)
    return root


def test_the_committed_pack_and_rendering_are_what_the_producer_writes_today(tmp_path):
    """The determinism pair: same seed, same evidence, byte-identical record AND rendering."""
    out, page = tmp_path / "pack.json", tmp_path / "pack.html"
    assert builder.main(["--out", str(out), "--page", str(page)]) == 0
    assert out.read_bytes() == PACK.read_bytes()
    assert page.read_bytes() == PAGE.read_bytes()


def test_the_draw_meets_the_clause_and_says_how_it_drew(pack):
    """3.18 (6): at least FIVE leaflet posts and FIVE comments, under a RECORDED seed."""
    assert pack["seed"] == builder.SEED
    assert len(pack["leaflet_posts"]) >= 5 and len(pack["comments"]) >= 5
    assert pack["drawn"]["leaflet_posts"] == sorted(
        block["post"] for block in pack["leaflet_posts"]
    )
    assert sorted(pack["drawn"]["comments"]) == sorted(
        block["comment"] for block in pack["comments"]
    )
    assert set(pack["strata"]["leaflet_post"]["populations"]) == {
        "yielded positions",
        "yielded none",
    }
    assert pack["strata"]["comment"]["channels"] == builder.top_channels(AGGREGATES)


def test_the_comment_draw_is_not_one_channel(pack):
    """The stratum exists because two channels are 73.8% of the window."""
    channels = [block["channel"] for block in pack["comments"]]
    assert len(set(channels)) == len(channels) == builder.COMMENT_CHANNELS
    assert channels[0] == "@matusi_ukr", "the largest channel is in, it is simply not all of them"


def test_the_leaflet_draw_carries_both_strata(pack):
    """Four posts that yielded and two that did not — «read and found nothing» is also a claim."""
    strata = [block["stratum"] for block in pack["leaflet_posts"]]
    assert strata.count("yielded positions") == builder.LEAFLET_YIELDED
    assert strata.count("yielded none") == builder.LEAFLET_EMPTY
    for block in pack["leaflet_posts"]:
        yielded = bool(block["positions"])
        assert yielded == (block["stratum"] == "yielded positions"), block["post"]


def test_the_draw_is_reproducible_from_the_seed_alone(pack):
    """Anyone with the record can redo the draw — that is what «recorded seed» has to mean."""
    channel = next(iter(AGGREGATES["leaflet_page"]["per_channel"]))
    pages = summary.read_rows(summary.DERIVED / "leaflet_pages" / f"{channel.lstrip('@')}.jsonl")
    rows = summary.read_rows(summary.DERIVED / "position_rows" / f"{channel.lstrip('@')}.jsonl")
    strata = builder.leaflet_strata(pages, rows)

    redrawn = builder.draw(
        strata["yielded positions"], builder.LEAFLET_YIELDED, "yielded positions", pack["seed"]
    )
    redrawn += builder.draw(
        strata["yielded none"], builder.LEAFLET_EMPTY, "yielded none", pack["seed"]
    )

    assert sorted(redrawn) == pack["drawn"]["leaflet_posts"]


def test_a_stratum_too_small_for_its_draw_is_a_refusal():
    with pytest.raises(SystemExit, match="rows in a stratum the draw needs"):
        builder.draw(["a", "b"], 3, "x")


# --- what the operator is shown ----------------------------------------------------------------


def test_every_shown_position_re_derives_its_rung_from_the_ladder(pack):
    """3.18 (6): «the ladder inputs shown so the rung can be re-derived at the table»."""
    table = pack["ladder"]["table"]
    assert pack["ladder"]["sha256"] == positions.ladder_sha256()
    for block in pack["leaflet_posts"]:
        for row in block["positions"]:
            why = row["why_a_position"]
            assert why["tier"] == why["tier_re_derived"], row["row_id"]
            assert table[why["ladder_key"]] == why["tier"], row["row_id"]
            assert set(why["presence"]) == set(positions.PRESENCE_FIELDS)


def test_every_shown_comment_carries_the_original_the_rendering_and_every_head(pack):
    for block in pack["comments"]:
        assert block["text"] in block["rendering"][0]["content"]
        assert block["parent_post"] in block["rendering"][0]["content"]
        assert set(block["verdicts"]) == {
            "sentiment",
            "sarcasm",
            "intents",
            "unreadable",
            "brand_attribution",
        }
        assert block["verdicts"]["unreadable"] is None
        assert block["reply"] and block["prompt_sha256"]
        # a comment CAN be empty — 1 361 of the 5 075 were sent that way — and the pack has to say
        # so rather than show a blank box beside three confident labels
        assert block["empty_text"] == (not block["text"].strip())


def test_an_empty_comment_is_shown_as_its_class_and_not_as_a_blank_box(pack):
    """The draw pulled one of the 1 361 rows the model was asked about with no text at all."""
    empty = [block for block in pack["comments"] if block["empty_text"]]
    assert empty, "the seed drew one; if that changes this test should be re-pointed, not deleted"
    page = PAGE.read_text(encoding="utf-8")
    assert "ПУСТО" in page and "&lt;comment&gt;" in page
    for block in empty:
        assert block["aggregate"]["empty_text"]["in_window"] == 1361
        assert (
            block["aggregate"]["empty_text"]["in_channel"]
            == AGGREGATES["comment"]["per_channel"][block["channel"]]["empty_text"]["rows"]
        )


def test_no_caption_number_is_computed_here(pack):
    """Every aggregate beside a row comes out of window_summary_5c2.json unchanged."""
    whole = AGGREGATES["comment"]["total"]
    for block in pack["comments"]:
        caption = block["aggregate"]
        here = AGGREGATES["comment"]["per_channel"][block["channel"]]
        assert caption["rows"] == {"in_channel": here["rows"], "in_window": whole["rows"]}
        assert caption["sentiment"]["in_channel"] == here["sentiment"]
        assert caption["sentiment"]["in_window"] == whole["sentiment"]
        assert caption["sarcasm"]["rate_in_window"] == whole["sarcasm"]["rate"]
        assert caption["this_row"]["sentiment"] == block["verdicts"]["sentiment"]
    assert pack["leaflet_aggregate"]["pages"] == AGGREGATES["leaflet_page"]["total"]


def test_the_pack_shows_the_page_as_it_was_sent_and_proves_it(pack):
    for block in pack["leaflet_posts"]:
        for page in block["pages"]:
            path = REPO_ROOT / page["image_path"]
            assert summary.sha256_of(path) == page["image_sha256"], page["image_path"]


def test_an_image_whose_bytes_moved_is_a_refusal(pack, tmp_path):
    """The direction that matters: the picture on disk is not the one the model was sent."""
    page = pack["leaflet_posts"][0]["pages"][0]
    forged = dict(page) | {"image_sha256": "0" * 64}

    with pytest.raises(SystemExit, match="is not the one the model was"):
        builder.page_block(forged | {"reply": {"content": ""}}, REPO_ROOT)


def test_a_missing_image_is_a_refusal(pack):
    forged = dict(pack["leaflet_posts"][0]["pages"][0]) | {"image_path": "data/gone.jpg"}

    with pytest.raises(SystemExit, match="not found"):
        builder.page_block(forged | {"reply": {"content": ""}}, REPO_ROOT)


# --- the sitting's paperwork -------------------------------------------------------------------


def test_not_one_findings_slot_is_pre_filled(pack):
    """The contract's «Do NOT» in one assertion."""
    findings = pack["findings"]
    assert findings["verdicts"] == ["ratified", "disputed"]
    for level in ("leaflet_posts", "positions", "comments"):
        assert findings[level], level
        for key, slot in findings[level].items():
            assert slot == {"verdict": "", "note": ""}, f"{level}[{key}] is pre-filled"


def test_there_is_a_slot_for_every_shown_row_and_no_slot_for_anything_else(pack):
    findings = pack["findings"]
    assert set(findings["leaflet_posts"]) == {block["post"] for block in pack["leaflet_posts"]}
    assert set(findings["comments"]) == {block["comment"] for block in pack["comments"]}
    assert set(findings["positions"]) == {
        row["row_id"] for block in pack["leaflet_posts"] for row in block["positions"]
    }


def test_the_findings_law_is_on_the_table_during_the_sitting(pack):
    """3.18 (6)(c) as a sentence in the rendering's header, not only in the record."""
    page = PAGE.read_text(encoding="utf-8")
    assert builder.FINDINGS_LAW_RU in page
    assert "ORDERS" in pack["laws"]["findings"] and "never a moved bar" in pack["laws"]["findings"]
    assert "ratified" not in page, "a verdict word in the rendering would read as a filled slot"


def test_the_rendering_points_at_pictures_that_exist(pack):
    """`../<repo-relative>` from `results/`, so the pack opens inside any checkout of this repo."""
    page = PAGE.read_text(encoding="utf-8")
    for block in pack["leaflet_posts"]:
        for shown in block["pages"]:
            src = builder.IMAGE_PREFIX + shown["image_path"]
            assert f'src="{src}"' in page
            assert (PAGE.parent / src).resolve().exists()


def test_the_rendering_shows_every_drawn_row(pack):
    page = PAGE.read_text(encoding="utf-8")
    for one in pack["drawn"]["comments"] + pack["drawn"]["leaflet_posts"]:
        assert one in page


# --- the honesty rails -------------------------------------------------------------------------


def test_a_derived_root_with_one_file_removed_is_a_refusal(tmp_path):
    """The negative control the contract asks for, on the file the draw actually reads."""
    root = mirror(tmp_path, drop="inferences/kopiyochka1.jsonl")

    with pytest.raises(SystemExit, match=r"kopiyochka1\.jsonl: not found"):
        builder.main(
            [
                "--derived-root",
                str(root),
                "--out",
                str(tmp_path / "out.json"),
                "--page",
                str(tmp_path / "out.html"),
            ]
        )


def test_the_same_root_with_nothing_removed_still_builds(tmp_path):
    """The control's control: the mirror itself is not what makes the refusal fire.

    Its aggregates are rebuilt over the mirror, because `assert_same_evidence` compares the pack's
    sources against the summary's by NAME — the committed summary names `data/derived/…` and a
    sandbox names itself. That refusal is real and is exercised on its own below; here the point is
    that a complete mirror draws the same ten rows as the committed pack.
    """
    root = mirror(tmp_path)
    aggregates, out = tmp_path / "summary.json", tmp_path / "out.json"
    assert summary.main(["--derived-root", str(root), "--out", str(aggregates)]) == 0

    argv = ["--derived-root", str(root), "--summary", str(aggregates), "--out", str(out)]
    assert builder.main([*argv, "--page", str(tmp_path / "out.html")]) == 0
    assert (
        json.loads(out.read_text(encoding="utf-8"))["drawn"]
        == json.loads(PACK.read_text(encoding="utf-8"))["drawn"]
    )


def test_aggregates_computed_over_other_bytes_are_a_refusal(tmp_path):
    """A caption measured on a different disk than the row beside it is worse than no caption."""
    aggregates = {"sources": {"data/derived/inferences/msuaaaa.jsonl": "f" * 64}}

    with pytest.raises(SystemExit, match="computed over different bytes"):
        builder.assert_same_evidence(
            aggregates,
            {"data/derived/inferences/msuaaaa.jsonl": "a" * 64, "results/x.json": "b" * 64},
            Path("results/x.json"),
        )


def test_the_pack_names_every_byte_it_read(pack):
    assert set(pack["sources"]) >= {
        "results/window_summary_5c2.json",
        f"data/derived/{loop.PAGE_RECORD_TYPE}s/atb_market_official.jsonl",
        f"data/derived/{loop.POSITION_RECORD_TYPE}s/atb_market_official.jsonl",
    }
    for name, digest in pack["sources"].items():
        assert summary.sha256_of(REPO_ROOT / name) == digest, name
    assert pack["aggregates"]["sha256"] == pack["sources"]["results/window_summary_5c2.json"]


def test_no_clock_and_no_git_block(pack):
    """Both records are byte-identical across runs, and that is what the pair proves."""
    assert "at" not in pack and "git" not in pack
    assert pack["producer"]["sha256"] == summary.sha256_of(REPO_ROOT / pack["producer"]["script"])
    assert "scripts/window_summary_5c2.py" in pack["producer"]["borrowed"]
