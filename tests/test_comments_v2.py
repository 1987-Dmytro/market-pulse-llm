"""The second pass joins onto v1 without becoming v1's editor (4.5g5, Task 3)."""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import fetch_comments_v2 as fetcher  # noqa: E402

from market_pulse.raw_store import RawStore  # noqa: E402


def v1(msg_id, parent=100, text="смачно"):
    return {
        "record_type": "comment",
        "channel": "@c",
        "parent_msg_id": parent,
        "msg_id": msg_id,
        "text": text,
        "sender_anon_id": "abc",
    }


def fresh(msg_id, parent=100, text="смачно", reply_to=None):
    return {**v1(msg_id, parent, text), "reply_to_msg_id": reply_to}


# --- the join ---------------------------------------------------------------------------


def test_the_reply_target_is_added_and_nothing_else_is_taken():
    rows, counts = joined_rows([v1(5)], [fresh(5, text="edited later", reply_to=4)])

    assert rows[0]["text"] == "смачно"  # v1 text is law
    assert rows[0]["reply_to_msg_id"] == 4
    assert counts["text_differs"] == 1


def test_a_row_the_fresh_fetch_no_longer_has_carries_no_key_at_all():
    """`None` would read as "replies to the post". Absent raises instead, which is the truth:
    nobody knows what this deleted message replied to."""
    rows, counts = joined_rows([v1(5), v1(6)], [fresh(6, reply_to=None)])

    assert "reply_to_msg_id" not in rows[0]
    assert rows[1]["reply_to_msg_id"] is None
    assert counts["missing_from_the_fresh_fetch"] == 1


def test_a_message_that_appeared_since_is_counted_and_left_out():
    rows, counts = joined_rows([v1(5)], [fresh(5, reply_to=4), fresh(9, reply_to=5)])

    assert [row["msg_id"] for row in rows] == [5]
    assert counts["fresh_only"] == 1
    assert counts["v1_rows"] == 1
    assert counts["fresh_rows"] == 2


def test_v1_row_order_survives_the_join():
    rows, _ = joined_rows(
        [v1(9), v1(5), v1(7)], [fresh(5, reply_to=1), fresh(7, reply_to=1), fresh(9, reply_to=1)]
    )

    assert [row["msg_id"] for row in rows] == [9, 5, 7]


def joined_rows(a, b):
    return fetcher.joined(a, b)


# --- what is left to fetch ---------------------------------------------------------------


def test_the_work_list_is_read_off_the_fresh_store_not_v1(tmp_path):
    """Asking v1 which parents are done answers "all of them", fetches nothing, and leaves a v2
    directory that looks merely small."""
    v1_store, fresh_store = RawStore(tmp_path / "v1"), RawStore(tmp_path / "fresh")
    v1_store.append([v1(5, parent=100), v1(6, parent=200)])

    assert fetcher.todo(v1_store, fresh_store, "@c") == [200, 100]

    fresh_store.append([fresh(5, parent=100)])
    assert fetcher.todo(v1_store, fresh_store, "@c") == [200]


def test_the_v1_store_is_never_the_write_target(tmp_path):
    assert fetcher.V2_DIR != fetcher.V1_ROOT / "comments"
    assert fetcher.v2_path("@VARUS_channel", tmp_path).name == "VARUS_channel.jsonl"


def test_round_trip_through_the_writer(tmp_path):
    path = tmp_path / "c.jsonl"
    fetcher.write_jsonl(path, [v1(5), v1(6)])

    assert fetcher.read_jsonl(path) == [v1(5), v1(6)]
    assert path.read_text(encoding="utf-8").endswith("\n")
    assert fetcher.read_jsonl(tmp_path / "absent.jsonl") == []


def test_the_frozen_list_names_every_label_field():
    """A joiner pointed at a labelled file must not be able to widen quietly."""
    assert set(fetcher.FROZEN) == {"text", "sentiment", "sarcasm", "intents", "unclear"}


# --- the corpus this phase re-fetches -----------------------------------------------------


def test_the_two_channels_are_the_labelled_corpus_and_no_new_one():
    assert fetcher.CHANNELS == ("@VARUS_channel", "@msuaaaa")


def test_the_real_work_list_is_every_thread_v1_holds():
    """835 + 703 threads. A run that reports fewer before it starts has lost its work list."""
    v1_store, fresh_store = RawStore(fetcher.V1_ROOT), RawStore(tmp_fresh())
    assert len(fetcher.todo(v1_store, fresh_store, "@VARUS_channel")) == 835
    assert len(fetcher.todo(v1_store, fresh_store, "@msuaaaa")) == 703


def tmp_fresh():
    return Path("/nonexistent-fresh-store-45g5")


def test_the_v1_files_carry_no_reply_target_which_is_why_this_phase_exists():
    for channel in fetcher.CHANNELS:
        first = json.loads(
            (RawStore(fetcher.V1_ROOT).path("comment", channel))
            .read_text(encoding="utf-8")
            .splitlines()[0]
        )
        assert "reply_to_msg_id" not in first
