"""What stands in for a post that has no text of its own.

The failure this guards against is not a bad caption — it is a caption that cannot be told apart
from a transcript, or a post silently left with nothing while the record says every row was
asked with its context. So: the three populations are split by rule, a poll carries no model and
no prompt hash, and what the file says is what `parents.load_captions` can read back.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import caption_posts as captions  # noqa: E402
from market_pulse import parents, prompts, zero_shot  # noqa: E402


def image(root: Path, name: str, body: bytes = b"\xff\xd8\xff\xe0jpeg") -> dict:
    path = root / "posts_media" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    return {"file": f"posts_media/{name}", "sha256": "0" * 64, "bytes": len(body)}


def entry(channel="@c", msg_id=1, images=(), poll=None, has_text=False):
    return {
        "channel": channel,
        "msg_id": msg_id,
        "asked_by": ["emptied_97"],
        "post_has_text": has_text,
        "has_media": True,
        "album": len(images) > 1,
        "images": list(images),
        "poll": poll,
        "missing": [],
    }


def manifest(tmp_path: Path, entries: dict) -> Path:
    path = tmp_path / "media.json"
    path.write_text(json.dumps({"entries": entries}, ensure_ascii=False), encoding="utf-8")
    return path


def test_the_three_populations_are_split_by_what_the_post_actually_is():
    found = captions.population(
        {
            "entries": {
                "@c:1": entry(msg_id=1, images=[{"file": "a.jpg", "sha256": "x"}]),
                "@c:2": entry(msg_id=2, poll={"question": "З чим?", "options": ["A"]}),
                "@c:3": entry(msg_id=3),
                "@c:4": entry(msg_id=4, has_text=True),
            }
        }
    )
    images, polls, blind = found
    assert [row["name"] for row in images] == ["@c:1"]
    assert [row["name"] for row in polls] == ["@c:2"]
    assert blind == ["@c:3"], "a post with neither is named, never guessed at"


def test_a_poll_is_transcribed_question_first_then_its_options():
    assert captions.poll_caption({"question": "З чим?", "options": ["З вишнею", "З сиром"]}) == (
        "З чим?\n— З вишнею\n— З сиром"
    )


def run(tmp_path, entries, extra=()):
    asker = captions.FakeAsker(zero_shot.Budget(captions.CAP_USD, captions.CAP_USD))
    assert (
        captions.main(
            [
                "--manifest",
                str(manifest(tmp_path, entries)),
                "--out",
                str(tmp_path / "post_captions.jsonl"),
                "--record",
                str(tmp_path / "record.json"),
                "--root",
                str(tmp_path),
                *extra,
            ],
            asker=asker,
        )
        == 0
    )
    return json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))["runs"][-1]


def test_a_transcript_carries_no_model_and_a_caption_carries_both(tmp_path):
    """A poll's question came from Telegram and a description came from a vision model. A file
    that recorded them the same way would let a later reader attribute one to the other."""
    entries = {
        "@c:1": entry(msg_id=1, images=[image(tmp_path, "c_1.jpg")]),
        "@c:2": entry(msg_id=2, poll={"question": "З чим?", "options": ["З вишнею"]}),
    }
    record = run(tmp_path, entries)
    rows = {
        row["msg_id"]: row
        for row in (
            json.loads(line)
            for line in (tmp_path / "post_captions.jsonl").read_text(encoding="utf-8").splitlines()
        )
    }
    assert rows[1]["kind"] == "image"
    assert rows[1]["model"] == captions.MODEL
    assert rows[1]["prompt_sha256"] == prompts.prompt_sha256(prompts.CAPTION_TASK)
    assert rows[2]["kind"] == "poll"
    assert rows[2]["model"] is None and rows[2]["prompt_sha256"] is None
    assert rows[2]["caption"].startswith("З чим?")
    assert record["kinds"] == {"image": 1, "poll": 1}
    assert record["cost"]["requests"] == 1, "the poll cost nothing because nothing was asked"


def test_the_file_reads_back_through_the_loader_the_prompts_use(tmp_path):
    entries = {
        "@c:1": entry(msg_id=1, images=[image(tmp_path, "c_1.jpg")]),
        "@c:2": entry(msg_id=2, poll={"question": "З чим?", "options": []}),
    }
    run(tmp_path, entries)
    loaded = parents.load_captions(tmp_path / "post_captions.jsonl")
    assert {key[1]: value["kind"] for key, value in loaded.items()} == {1: "image", 2: "poll"}


def test_an_album_longer_than_the_cap_says_so_in_the_record(tmp_path):
    """A silent cap reads as `the model saw the whole post`, which is the one thing it did not."""
    entries = {
        "@c:1": entry(
            msg_id=1, images=[image(tmp_path, f"c_{i}.jpg") for i in range(captions.MAX_IMAGES + 3)]
        )
    }
    record = run(tmp_path, entries)
    assert record["images"] == {
        "sent": captions.MAX_IMAGES,
        "available": captions.MAX_IMAGES + 3,
        "max_per_request": captions.MAX_IMAGES,
        "posts_truncated": ["@c:1"],
    }
    row = json.loads((tmp_path / "post_captions.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert len(row["images"]) == captions.MAX_IMAGES, (
        "the record names the images it was written from"
    )


def test_an_empty_reply_is_counted_and_never_written_as_a_caption(tmp_path):
    """The FakeAsker returns nothing on its ninth call, so the counter is exercised rather than
    printed as a zero."""
    entries = {
        f"@c:{i}": entry(msg_id=i, images=[image(tmp_path, f"c_{i}.jpg")]) for i in range(1, 10)
    }
    record = run(tmp_path, entries)
    assert len(record["population"]["unusable"]) == 1
    written = (tmp_path / "post_captions.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(written) == 8
    assert all(json.loads(line)["caption"].strip() for line in written)
