"""Offline tests for the Phase-5a poll census — no Telegram, no session."""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import poll_census as census  # noqa: E402

from market_pulse import parents  # noqa: E402

POLL = {"question": "Як вам зручніше?", "options": ["фото", "pdf"]}


def fake_media(name, **fields):
    """A stand-in for a Telethon media object: only its class name and fields are read."""
    return type(name, (), fields)()


def message(media):
    return type("Message", (), {"media": media})()


def document(*attributes):
    return fake_media(
        "MessageMediaDocument", document=fake_media("Document", attributes=attributes)
    )


def post(channel, msg_id, text=""):
    return {"channel": channel, "msg_id": msg_id, "text": text}


# --- what a text-less post actually is ----------------------------------------------------


def test_a_poll_is_a_poll():
    assert census.media_kind(message(fake_media("MessageMediaPoll"))) == "poll"


def test_a_giveaway_is_counted_apart_from_a_picture():
    assert census.media_kind(message(fake_media("MessageMediaGiveaway"))) == "giveaway"
    assert census.media_kind(message(fake_media("MessageMediaGiveawayResults"))) == "giveaway"
    assert census.media_kind(message(fake_media("MessageMediaPhoto"))) == "photo"


def test_a_voice_note_and_an_uploaded_audio_file_are_not_the_same_row():
    """Both are audio/ogg documents. The `voice` flag is the only thing that tells them apart."""
    voice = document(fake_media("DocumentAttributeAudio", voice=True))
    audio = document(fake_media("DocumentAttributeAudio", voice=False))
    assert census.media_kind(message(voice)) == "voice"
    assert census.media_kind(message(audio)) == "audio"


def test_a_video_is_read_off_its_attribute_not_its_mime_type():
    assert census.media_kind(message(document(fake_media("DocumentAttributeVideo")))) == "video"


def test_a_document_with_no_telling_attribute_stays_a_document():
    assert census.media_kind(message(document())) == "document"


def test_a_message_with_no_media_at_all():
    assert census.media_kind(message(None)) == "no_media"


# --- the population -------------------------------------------------------------------------


def test_the_population_is_the_posts_with_no_text_of_their_own():
    records = [
        post("@a", 1, "продукти"),
        post("@a", 2),
        post("@a", 3, "   "),
        post("@b", 9),
    ]
    assert census.population(records) == {"@a": [2, 3], "@b": [9]}


# --- the counts ------------------------------------------------------------------------------


def test_the_census_counts_polls_per_channel_and_in_total():
    empty = {"@a": [1, 2, 3], "@b": [7]}
    found = {("@a", 1): "poll", ("@a", 2): "photo", ("@a", 3): "poll", ("@b", 7): "video"}

    counts = census.census(found, empty, {"@a": 100, "@b": 50})

    assert counts["per_channel"]["@a"]["polls"] == 2
    assert counts["per_channel"]["@a"]["poll_share_of_empty"] == round(2 / 3, 4)
    assert counts["total"] == {
        "posts_stored": 150,
        "empty_text": 4,
        "polls": 2,
        "poll_share_of_empty": 0.5,
        "kinds": {"photo": 1, "poll": 2, "video": 1},
    }


def test_an_id_that_was_never_read_is_named_not_guessed():
    """A batch that never came back must not land in the census as "not a poll"."""
    counts = census.census({("@a", 1): "poll"}, {"@a": [1, 2]}, {"@a": 10})
    assert counts["per_channel"]["@a"]["kinds"] == {"not_fetched": 1, "poll": 1}


def test_a_deleted_message_has_its_own_class():
    counts = census.census({("@a", 1): "gone"}, {"@a": [1]}, {"@a": 10})
    assert counts["total"]["kinds"] == {"gone": 1}
    assert counts["total"]["polls"] == 0


# --- the sidecar -------------------------------------------------------------------------------


def test_the_transcript_is_the_4_5g2_format_and_nothing_new():
    built = census.sidecar_record("@a", 5, POLL)
    assert built["kind"] == "poll"
    assert built["caption"] == "Як вам зручніше?\n— фото\n— pdf"
    assert built["poll"] == POLL


def test_the_sidecar_is_readable_by_the_loader_the_repo_already_has(tmp_path):
    """The claim "no second reader is needed" is checked, not asserted."""
    path = tmp_path / "post_polls.jsonl"
    census.write_sidecar(path, {("@a", 5): POLL, ("@a", 6): POLL})

    loaded = parents.load_captions(path)

    assert set(loaded) == {("@a", 5), ("@a", 6)}
    assert loaded[("@a", 5)]["kind"] == "poll"
    assert parents.STATE_OF[loaded[("@a", 5)]["kind"]] == "poll_text"


# --- the positive control on the fetch -----------------------------------------------------------


def write_captions(path, rows):
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )


def test_the_cross_check_passes_when_this_run_reproduces_4_5g2(tmp_path):
    path = tmp_path / "post_captions.jsonl"
    write_captions(
        path,
        [
            {
                "channel": "@a",
                "msg_id": 5,
                "kind": "poll",
                "caption": "Як вам зручніше?\n— фото\n— pdf",
            },
            {"channel": "@a", "msg_id": 9, "kind": "image", "caption": "a leaflet"},
        ],
    )

    checked = census.cross_check([census.sidecar_record("@a", 5, POLL)], path)

    assert checked["rows_45g2"] == 1, "the image row is not a poll and is not in the control"
    assert checked["transcripts_identical"] == 1
    assert checked["missing_from_this_run"] == []
    assert checked["transcripts_that_differ"] == []


def test_the_cross_check_names_a_transcript_that_moved(tmp_path):
    path = tmp_path / "post_captions.jsonl"
    write_captions(
        path, [{"channel": "@a", "msg_id": 5, "kind": "poll", "caption": "something else"}]
    )

    checked = census.cross_check([census.sidecar_record("@a", 5, POLL)], path)

    assert checked["transcripts_that_differ"] == ["@a:5"]
    assert checked["transcripts_identical"] == 0


def test_the_cross_check_names_a_poll_this_run_did_not_find(tmp_path):
    path = tmp_path / "post_captions.jsonl"
    write_captions(path, [{"channel": "@a", "msg_id": 5, "kind": "poll", "caption": "x"}])

    checked = census.cross_check([], path)

    assert checked["missing_from_this_run"] == ["@a:5"]
    assert checked["also_found_here"] == 0
