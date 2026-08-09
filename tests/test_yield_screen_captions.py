"""`yield_screen_5c1.py --captions`: screen v2, and the two ways it could lie.

It could read a caption for a post the screen already read — and quietly change a number the
operator signed against. Or it could drop the posts it still cannot read, and report a yield
about the readable half of a channel. Both are counted here rather than assumed away.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


screen = _script("yield_screen_5c1")

POSTS = [
    {"msg_id": 1, "date": "2026-07-11T00:00:00+00:00", "text": "  Акція на сир  "},
    {"msg_id": 2, "date": "2026-07-12T00:00:00+00:00", "text": ""},
    {"msg_id": 3, "date": "2026-07-13T00:00:00+00:00", "text": ""},
]


def test_without_captions_the_matcher_reads_the_stored_text_verbatim():
    """The signed screen's reading has to survive the option being added — including the
    whitespace, because `evidence_line` quotes a line and a stripped one is a different quote."""
    assert screen.surrogates("@a", POSTS, {}) == [(POSTS[0], "  Акція на сир  ")]


def test_a_caption_stands_in_for_a_silent_post_and_is_appended_to_a_speaking_one():
    captions = {("@a", 2): {"text": "морозиво Рудь"}, ("@a", 1): {"text": "полиця"}}
    got = dict((row["msg_id"], text) for row, text in screen.surrogates("@a", POSTS, captions))
    assert got == {1: "Акція на сир\nполиця", 2: "морозиво Рудь"}
    assert 3 not in got, "a post with neither text nor a caption is not readable"


def test_the_census_counts_graded_blind_and_truncated_and_flags_a_caption_over_text():
    captions = {("@a", 1): {"text": "полиця"}, ("@a", 2): {"text": "морозиво"}}
    readable = screen.surrogates("@a", POSTS, captions)
    census = screen.caption_census(
        "@a", POSTS, [POSTS[0]], readable, captions, truncated={"@a:2", "@b:9"}
    )
    assert census == {
        "graded": 2,
        "with_own_text": 1,
        "graded_on_a_caption": 1,
        "blind": 1,  # msg 3: silent, and nothing was bought for it
        "truncated": 1,  # @b:9 belongs to another channel and is not counted here
        "captions_over_a_post_that_had_text": 1,
    }


def caption_file(tmp_path: Path, name: str, rows: list[dict]) -> Path:
    path = tmp_path / name
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8"
    )
    return path


def row(msg_id: int, source: str) -> dict:
    return {
        "channel": "@a",
        "msg_id": msg_id,
        "kind": "image",
        "caption": "морозиво",
        "caption_source": source,
    }


def test_two_files_merge_and_a_post_captioned_twice_is_refused(tmp_path):
    one = caption_file(tmp_path, "one.jsonl", [row(1, "gm4-nf4-base")])
    two = caption_file(tmp_path, "two.jsonl", [row(1, "gm4-nf4-base")])
    with pytest.raises(SystemExit, match="captioned in two files"):
        screen.read_caption_files([one, two], None)


def test_an_undeclared_mix_of_caption_instruments_is_refused(tmp_path):
    """SPEC 3.13 (3). vis-c's screen joins ATB's GM4 captions to 25 more channels' — one
    instrument. The day a 4.5g2 file is joined beside them, the records have to say so."""
    mixed = caption_file(tmp_path, "mixed.jsonl", [row(1, "gm4-nf4-base"), row(2, "qwen-4.5g2")])
    with pytest.raises(SystemExit, match="mixes caption instruments"):
        screen.read_caption_files([mixed], None)

    declared = tmp_path / "record.json"
    declared.write_text(
        json.dumps({"caption_sources": ["gm4-nf4-base", "qwen-4.5g2"], "truncated_replies": []}),
        encoding="utf-8",
    )
    captions, block = screen.read_caption_files([mixed], [declared])
    assert block["sources"] == ["gm4-nf4-base", "qwen-4.5g2"]
    assert len(captions) == 2


def test_the_truncations_come_from_the_run_record_not_from_the_caption_rows(tmp_path):
    """A caption row carries no `finish_reason`; the paid record does. Reading truncation off
    the rows would silently report zero of them."""
    captions = caption_file(tmp_path, "c.jsonl", [row(1, "gm4-nf4-base")])
    record = tmp_path / "r.json"
    record.write_text(
        json.dumps({"caption_sources": ["gm4-nf4-base"], "truncated_replies": ["@a:1"]}),
        encoding="utf-8",
    )
    _, block = screen.read_caption_files([captions], [record])
    assert block["truncated_replies"] == ["@a:1"]
    assert block["truncated_set"] == {"@a:1"}


def test_a_caption_record_without_captions_is_refused():
    with pytest.raises(SystemExit, match="screens nothing differently"):
        screen.main(["--caption-record", "x.json"])
