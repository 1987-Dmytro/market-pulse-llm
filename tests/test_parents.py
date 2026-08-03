"""Finding the post a comment replies to, and refusing to guess when it is not there.

The guideline states as fact that every parent is stored. This module exists because a
claim about the corpus is worth checking: the failure it prevents is not a crash but a row
quietly asked with a prompt that promised a post and rendered none, sitting in the output
looking exactly like the 1,911 that were asked properly.
"""

import json
from pathlib import Path

import pytest

from market_pulse import parents, prompts


def post(channel: str, msg_id: int, text: str = "Новинка: сирок") -> dict:
    return {"channel": channel, "msg_id": msg_id, "text": text}


def comment(channel: str, parent: int, row_id: str = "@c:1") -> dict:
    return {"id": row_id, "channel": channel, "parent_msg_id": parent, "text": "Так"}


def store(tmp_path: Path, records: list[dict]) -> Path:
    directory = tmp_path / "posts"
    directory.mkdir()
    (directory / "channel.jsonl").write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )
    return directory


def test_the_parent_is_matched_on_channel_and_msg_id_together(tmp_path):
    """Two channels number their posts independently, so the id alone names two rows."""
    posts = parents.load(store(tmp_path, [post("@a", 10, "post A"), post("@b", 10, "post B")]))
    assert parents.text_for(posts, comment("@a", 10)) == "post A"
    assert parents.text_for(posts, comment("@b", 10)) == "post B"


def test_a_missing_parent_stops_and_names_the_row(tmp_path):
    posts = parents.load(store(tmp_path, [post("@a", 10)]))
    with pytest.raises(ValueError, match=r"@c:9: its parent @a:11 is not in the stored posts"):
        parents.text_for(posts, comment("@a", 11, "@c:9"))


def test_a_media_only_parent_is_a_parent(tmp_path):
    """Present with no text of its own — not the same state as absent, and not an error."""
    posts = parents.load(store(tmp_path, [post("@a", 10, "")]))
    assert parents.text_for(posts, comment("@a", 10)) == ""
    content = prompts.build_messages("T1v2_with_post", "Так", parent="")[0]["content"]
    assert prompts.NO_POST_TEXT in content


def captions(tmp_path: Path, records: list[dict]) -> Path:
    path = tmp_path / "post_captions.jsonl"
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )
    return path


def test_the_three_states_a_post_can_reach_the_model_in(tmp_path):
    """`post_text` / `image_caption` / `no_text_and_no_caption` is what the record counts, and
    the counts are only checkable while one function decides all three."""
    posts = parents.load(store(tmp_path, [post("@a", 1), post("@a", 2, ""), post("@a", 3, "")]))
    seen = parents.load_captions(
        captions(
            tmp_path,
            [{"channel": "@a", "msg_id": 2, "caption": "Опитування про начинку", "kind": "image"}],
        )
    )
    assert parents.context(posts, seen, comment("@a", 1)) == {
        "parent": "Новинка: сирок",
        "caption": None,
        "caption_kind": None,
        "state": "post_text",
    }
    assert parents.context(posts, seen, comment("@a", 2)) == {
        "parent": "",
        "caption": "Опитування про начинку",
        "caption_kind": "image",
        "state": "image_caption",
    }
    assert parents.context(posts, seen, comment("@a", 3))["state"] == "no_text_and_no_caption"


def test_a_post_captioned_twice_is_refused(tmp_path):
    """Last-wins would pick a description silently, and the record would name the other one."""
    path = captions(
        tmp_path,
        [
            {"channel": "@a", "msg_id": 2, "caption": "first", "kind": "image"},
            {"channel": "@a", "msg_id": 2, "caption": "second", "kind": "poll"},
        ],
    )
    with pytest.raises(ValueError, match="captioned twice"):
        parents.load_captions(path)


def test_a_missing_caption_file_is_no_captions_and_not_a_crash(tmp_path):
    assert parents.load_captions(tmp_path / "absent.jsonl") == {}


def test_a_poll_reaches_the_model_tagged_as_a_poll_and_not_as_a_picture(tmp_path):
    """16 of the 41 media-only parents are polls. A question read out as an image description
    would be a claim about what a vision model saw, and no vision model saw it."""
    posts = parents.load(store(tmp_path, [post("@a", 1, "")]))
    seen = parents.load_captions(
        captions(tmp_path, [{"channel": "@a", "msg_id": 1, "caption": "З чим?", "kind": "poll"}])
    )
    found = parents.context(posts, seen, comment("@a", 1))
    assert found["state"] == "poll_text"
    content = prompts.build_messages(
        "T1v2_with_post",
        "З вишнею",
        parent=found["parent"],
        caption=found["caption"],
        caption_kind=found["caption_kind"],
    )[0]["content"]
    assert "<post>\n[poll] З чим?\n</post>" in content


def test_an_empty_store_is_a_defect_and_not_an_empty_index(tmp_path):
    """Otherwise every lookup fails one by one and the report reads as a corpus problem."""
    directory = tmp_path / "posts"
    directory.mkdir()
    with pytest.raises(ValueError, match="no stored posts"):
        parents.load(directory)


def test_every_comment_the_corpus_holds_has_its_parent_stored():
    """The guideline's claim, checked against the real store rather than a fixture.

    This is the assertion the 4.5g runs rely on: if it ever fails, a with-post pass would
    have to skip rows, and a skipped row is what this phase exists to stop producing.
    """
    root = Path(__file__).resolve().parents[1] / "data" / "raw"
    posts = parents.load(root / "posts")
    missing = []
    for path in sorted((root / "comments").glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if (record["channel"], record["parent_msg_id"]) not in posts:
                missing.append(f"{record['channel']}:{record['msg_id']}")
    assert not missing, f"{len(missing)} comments have no stored parent: {missing[:5]}"
