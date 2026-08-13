"""Offline tests for the 5c2 window census — a fake store, a fake manifest, no Telegram."""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import census_5c2 as census  # noqa: E402
import yield_screen_5c1 as screen  # noqa: E402

from market_pulse.registry import Source  # noqa: E402

ANCHOR = "2026-02-01T00:00:00+00:00"
"""The window is then 2026-01-04T00:00:00+00:00 .. 2026-02-01T00:00:00+00:00."""

INSIDE = "2026-01-20T12:00:00+00:00"
OUTSIDE = "2025-12-31T12:00:00+00:00"

ATB = Source("atb", "АТБ", "official_retail", ("@atb",), True, False)
VARUS = Source("varus", "Varus", "official_retail", ("@varus",), True, True)
SILENT = Source("silpo", "Сільпо", "official_retail", ("@silpo",), True, False)


def jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )


def post(msg_id: int, date: str, *, media=False) -> dict:
    return {"record_type": "post", "msg_id": msg_id, "date": date, "has_media": media}


def comment(msg_id: int, date: str, parent: int = 1) -> dict:
    return {"record_type": "comment", "msg_id": msg_id, "date": date, "parent_msg_id": parent}


def wire(monkeypatch, tmp_path, *, sources=(ATB, VARUS, SILENT), entries=None, cursor=None):
    """A throwaway corpus: two channels with posts, one of them with comments, one manifest.

    `@silpo` gets a posts file and NO comments file — it is the CANNOT ANSWER control. `@varus`
    gets a comments file holding one in-window row and one outside it, so «read and produced
    nothing» and «never read» are two different cells in the same record.
    """
    jsonl(
        tmp_path / "posts" / "atb.jsonl",
        [post(1, INSIDE, media=True), post(2, INSIDE), post(3, OUTSIDE, media=True)],
    )
    jsonl(tmp_path / "posts" / "varus.jsonl", [post(10, INSIDE, media=True)])
    jsonl(tmp_path / "posts" / "silpo.jsonl", [post(20, OUTSIDE)])
    jsonl(tmp_path / "comments" / "varus.jsonl", [comment(100, INSIDE), comment(101, OUTSIDE)])
    manifest = {
        "entries": {
            "@atb:1": {
                "channel": "@atb",
                "msg_id": 1,
                "date": INSIDE,
                "images": [{"msg_id": 1, "file": "a.jpg"}, {"msg_id": 2, "file": "b.jpg"}],
            },
            "@atb:3": {
                "channel": "@atb",
                "msg_id": 3,
                "date": OUTSIDE,
                "images": [{"msg_id": 3, "file": "c.jpg"}],
            },
        }
    }
    if entries is not None:
        manifest["entries"] = entries
    (tmp_path / "post_media.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "loop_cursor.json").write_text(json.dumps(cursor or {}), encoding="utf-8")
    (tmp_path / "registry.yaml").write_text("sources: []\n", encoding="utf-8")
    monkeypatch.setattr(census, "POSTS", tmp_path / "posts")
    monkeypatch.setattr(census, "COMMENTS", tmp_path / "comments")
    monkeypatch.setattr(census, "CURSOR", tmp_path / "loop_cursor.json")
    monkeypatch.setattr(census, "POST_MEDIA", tmp_path / "post_media.json")
    monkeypatch.setattr(screen, "REGISTRY", tmp_path / "registry.yaml")
    monkeypatch.setattr(
        census, "load_registry", lambda _: type("R", (), {"sources": list(sources)})()
    )


def run(tmp_path, out="census.json", anchor=ANCHOR) -> dict:
    assert census.main(["--anchor", anchor, "--out", str(tmp_path / out)]) == 0
    return json.loads((tmp_path / out).read_text(encoding="utf-8"))


def channel(record: dict, handle: str) -> dict:
    return next(row for row in record["channels"] if row["handle"] == handle)


def test_the_window_is_28_days_back_from_the_anchor(monkeypatch, tmp_path):
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)
    window = record["anchor"]
    assert window["until"] == ANCHOR
    assert window["since"] == "2026-01-04T00:00:00+00:00"
    assert window["days"] == 28


def test_the_same_anchor_reproduces_the_artifact_byte_for_byte(monkeypatch, tmp_path):
    """The census's own gate. It holds only because nothing in the record is read from the clock
    and every collection is sorted before it is written."""
    wire(monkeypatch, tmp_path)
    run(tmp_path, "first.json")
    run(tmp_path, "second.json")

    assert (tmp_path / "first.json").read_bytes() == (tmp_path / "second.json").read_bytes()


def test_the_record_carries_no_clock_of_its_own(monkeypatch, tmp_path):
    """The anchor is the only timestamp a reader can mistake for «when this ran».

    Both halves: the record has no `generated_at`, and the module CALLS no clock. The second is
    what stops the first from being re-added by a later hand — a `generated_at` would void the
    determinism gate above while every other assertion in this file stayed green.

    Read off the AST rather than grepped, because this module's own docstring argues about
    `datetime.now()` in prose and a text search cannot tell an argument from a call.
    """
    import ast

    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    assert "generated_at" not in record and "timestamp" not in record
    tree = ast.parse(Path(census.__file__).read_text(encoding="utf-8"))
    called = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not called & {"now", "utcnow", "today", "time"}, "the census reads no clock"


def test_the_record_carries_no_git_state_and_names_its_producer(monkeypatch, tmp_path):
    """`git_state` embeds `git status --porcelain`, so a record carrying it moves when an unrelated
    file is committed or edited. Measured, not feared: this census was committed, the next commit
    landed, and the same command with the same anchor produced different bytes — which is the
    determinism gate voided by a provenance field. Provenance here is the script's own sha.

    Read off the AST for the same reason the clock test is: `producer()`'s docstring argues about
    `git_state` in prose, and a grep cannot tell an argument from a call.
    """
    import ast
    import hashlib

    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    assert "git" not in record
    assert (
        record["producer"]["sha256"]
        == hashlib.sha256(Path(census.__file__).read_bytes()).hexdigest()
    )
    tree = ast.parse(Path(census.__file__).read_text(encoding="utf-8"))
    assert not [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "git_state"
    ]


def test_a_row_on_the_boundary_is_in_and_a_row_on_the_anchor_is_out(monkeypatch, tmp_path):
    """Half-open, so the window counts exactly 28 days and two adjacent windows never share a row."""
    wire(monkeypatch, tmp_path)
    jsonl(
        tmp_path / "posts" / "atb.jsonl",
        [post(1, "2026-01-04T00:00:00+00:00"), post(2, ANCHOR)],
    )

    assert channel(run(tmp_path), "@atb")["posts"]["in_window"] == 1


def test_a_channel_with_no_comment_file_says_cannot_answer_and_one_with_none_says_zero(
    monkeypatch, tmp_path
):
    """The whole point of the string: «never read» and «read, nothing there» are different facts.

    `@silpo` has no comments file at all. `@varus` has one holding a row outside the window, so it
    was read and the window is empty — a measured 0.
    """
    wire(monkeypatch, tmp_path)
    jsonl(tmp_path / "comments" / "varus.jsonl", [comment(101, OUTSIDE)])
    record = run(tmp_path)

    assert channel(record, "@silpo")["comments"] == census.CANNOT_ANSWER
    assert channel(record, "@silpo")["comments_unanswered_in_window"] == census.CANNOT_ANSWER
    assert channel(record, "@varus")["comments"]["in_window"] == 0
    assert record["totals"]["comments_in_window"] == 0, "a CANNOT ANSWER cell is not summed as 0"


def test_the_cannot_answer_block_separates_a_collection_gap_from_a_channel_with_no_group(
    monkeypatch, tmp_path
):
    """`@varus` is comments-enabled and unread here; `@atb` and `@silpo` have no discussion group.
    Only the first is a gap, and only it belongs in a sentence about what the window is missing."""
    wire(monkeypatch, tmp_path)
    (tmp_path / "comments" / "varus.jsonl").unlink()
    block = run(tmp_path)["cannot_answer"]["comments"]

    assert block["collection_gap"] == ["@varus"]
    assert block["no_discussion_group"] == ["@atb", "@silpo"]
    assert block["n"] == 3


def test_posts_with_media_counts_the_stored_flag_inside_the_window(monkeypatch, tmp_path):
    """`@atb` has two in-window posts, one of them with media, and one out-of-window post with
    media that must not be counted."""
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    assert channel(record, "@atb")["posts"]["in_window"] == 2
    assert channel(record, "@atb")["posts_with_media_in_window"] == 1


def test_a_page_is_in_the_window_when_its_post_is(monkeypatch, tmp_path):
    """A page has no date of its own. Two pages hang under the in-window post and one under the
    post outside it — the coverage column counts two."""
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    leaflet = channel(record, "@atb")["leaflet"]
    assert (leaflet["pages_in_window"], leaflet["posts_with_pages_in_window"]) == (2, 1)
    assert (leaflet["pages_in_store"], leaflet["posts_with_pages_in_store"]) == (3, 2)
    assert record["totals"]["leaflet_pages_in_window"] == 2


def test_the_coverage_gap_names_both_of_its_two_nearby_numbers(monkeypatch, tmp_path):
    """«Media posts with no page anywhere» and «media posts in channels with no page at all» are
    different questions, and the second is smaller by the covered channel's own uncovered posts.

    Here `@atb` has two in-window posts, one with media, and it is the only channel with a page —
    so the first number counts `@varus`'s media post and ATB's own uncovered ones, and the second
    counts `@varus`'s alone.
    """
    wire(monkeypatch, tmp_path)
    jsonl(
        tmp_path / "posts" / "atb.jsonl", [post(1, INSIDE, media=True), post(2, INSIDE, media=True)]
    )
    gap = run(tmp_path)["leaflet_coverage"]["gap"]

    assert gap["channels_with_any_page"] == ["@atb"]
    assert gap["posts_with_media_in_window"] == 3, "two ATB posts and @varus's one"
    assert gap["posts_with_a_page_downloaded"] == 1
    assert gap["posts_with_media_and_no_page"] == 2, "ATB's second post and @varus's"
    assert gap["posts_with_media_in_channels_with_no_page_at_all"] == 1, "@varus's alone"


def test_a_manifest_that_disagrees_with_the_store_is_reported(monkeypatch, tmp_path):
    """A manifest date that has drifted from the post's would move pages in and out of the window
    with no row moving, so the disagreement is named rather than silently used."""
    wire(monkeypatch, tmp_path)
    manifest = json.loads((tmp_path / "post_media.json").read_text(encoding="utf-8"))
    manifest["entries"]["@atb:1"]["date"] = OUTSIDE
    (tmp_path / "post_media.json").write_text(json.dumps(manifest), encoding="utf-8")

    check = run(tmp_path)["leaflet_coverage"]["manifest_vs_store"]
    assert not check["agrees"] and len(check["date_drift"]) == 1


def test_the_watermark_is_what_makes_a_row_unanswered(monkeypatch, tmp_path):
    """Today every `inference` watermark is unset, so every in-window comment is unanswered. That
    is a reading of the cursor and not an assumption — set one and the count drops."""
    wire(monkeypatch, tmp_path)
    assert channel(run(tmp_path), "@varus")["comments_unanswered_in_window"] == 1

    wire(monkeypatch, tmp_path, cursor={"@varus": {"inference": 100}})
    record = run(tmp_path, "second.json")
    assert channel(record, "@varus")["comments"]["in_window"] == 1
    assert channel(record, "@varus")["comments_unanswered_in_window"] == 0
    assert record["watermarks"]["inference_set_on"] == ["@varus"]


def test_the_concentration_table_carries_the_running_total(monkeypatch, tmp_path):
    """«The top N channels are X% of the window» is read off the file, not recomputed by hand."""
    wire(monkeypatch, tmp_path)
    jsonl(
        tmp_path / "comments" / "varus.jsonl",
        [comment(100 + i, INSIDE) for i in range(3)],
    )
    jsonl(tmp_path / "comments" / "atb.jsonl", [comment(200, INSIDE)])

    table = run(tmp_path)["concentration"]["comments_in_window"]
    assert [(row["handle"], row["n"]) for row in table] == [("@varus", 3), ("@atb", 1)]
    assert [row["cumulative"] for row in table] == [3, 4]
    assert table[0]["cumulative_share"] == 0.75 and table[-1]["cumulative_share"] == 1.0


def test_the_alternative_anchors_are_reported_and_never_summed_into_the_totals(
    monkeypatch, tmp_path
):
    """The anchor is a choice and it moves every column, so the alternatives are published beside
    it. They are a separate block: adding one to the totals would double-count the same rows."""
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    assert len(record["anchor_sensitivity"]) == len(census.ALTERNATIVE_ANCHORS)
    for alternative, (anchor, _) in zip(
        record["anchor_sensitivity"], census.ALTERNATIVE_ANCHORS, strict=True
    ):
        assert alternative["window"]["until"] == anchor
        assert alternative["window"]["days"] == 28
    assert "anchor_sensitivity" not in record["totals"]


def test_store_files_outside_the_registry_are_counted_apart(monkeypatch, tmp_path):
    """The loop walks the registry, so a store file with no registry entry is invisible to every
    number the paid session produces — and it is exactly the difference a reader would trip over."""
    wire(monkeypatch, tmp_path)
    jsonl(tmp_path / "comments" / "stranger.jsonl", [comment(300, INSIDE)])

    outside = run(tmp_path)["scope"]["outside_the_registry"]
    assert outside["comments"]["channels"] == ["@stranger"]
    assert outside["comments"]["rows"] == {"@stranger": 1}


def test_a_rerun_under_another_anchor_refuses_to_take_the_records_name(monkeypatch, tmp_path):
    """D68, narrowed: the same anchor may overwrite (that is the determinism gate), another one
    may not — the record the operator's ruling cites has to keep naming the window it was made on."""
    import pytest

    wire(monkeypatch, tmp_path)
    run(tmp_path)

    with pytest.raises(SystemExit, match="A different window is a different measurement"):
        census.main(
            ["--anchor", "2026-03-01T00:00:00+00:00", "--out", str(tmp_path / "census.json")]
        )
    assert run(tmp_path)["anchor"]["anchor"] == ANCHOR, "and the same anchor still may"


# --- the shipped record ---------------------------------------------------------------------


def test_the_shipped_census_still_matches_its_own_anchor():
    """A hand edit to the record is the threat this exists for: the artifact is a derivation, and
    the two fields any correction would touch first are the window bounds."""
    from datetime import datetime, timedelta

    record = json.loads(census.RECORD.read_text(encoding="utf-8"))
    anchor = record["anchor"]

    assert anchor["until"] == anchor["anchor"]
    assert datetime.fromisoformat(anchor["since"]) == datetime.fromisoformat(
        anchor["until"]
    ) - timedelta(days=census.WINDOW_DAYS)
    assert "generated_at" not in record
