"""Offline tests for the raw store — no Telegram, no session."""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pytest
from market_pulse.raw_store import (
    RawStore,
    collapse_albums,
    comment_record,
    load_salt,
    make_provenance,
    post_record,
    sender_anon_id,
)
from market_pulse.registry import Source

SALT = "test-salt"
SOURCE = Source("varus", "Varus", "official_retail", ("@VARUS_channel",), True, True)


class FakeMessage:
    """The handful of Telethon Message attributes the record builders read."""

    def __init__(
        self,
        id,
        *,
        text="",
        media=None,
        grouped_id=None,
        replies=0,
        sender_id=None,
        reply_to_msg_id=None,
    ):
        self.id = id
        self.date = datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc)
        self.raw_text = text
        self.media = media
        self.grouped_id = grouped_id
        self.replies = type("Replies", (), {"replies": replies})() if replies else None
        self.sender_id = sender_id
        # Telethon's own property: None when the message replies to nothing.
        self.reply_to_msg_id = reply_to_msg_id


def provenance():
    return make_provenance(SOURCE, "marketpulse")


def test_sender_anon_id_is_stable_and_hides_the_id():
    anon = sender_anon_id(12345, SALT)
    assert anon == sender_anon_id(12345, SALT)
    assert anon != sender_anon_id(12345, "other-salt")
    assert anon != sender_anon_id(12346, SALT)
    assert "12345" not in anon


def test_anonymous_sender_has_no_pseudonym():
    assert sender_anon_id(None, SALT) is None


def test_post_record_shape():
    record = post_record(
        FakeMessage(7, text="акція", media=object(), replies=3), SOURCE, "@c", provenance()
    )

    assert record["record_type"] == "post"
    assert (record["source_id"], record["channel"], record["msg_id"]) == ("varus", "@c", 7)
    assert record["text"] == "акція"
    assert record["has_media"] is True
    assert record["reply_count"] == 3
    assert record["provenance"]["source_type"] == "official_retail"
    assert record["provenance"]["comments_enabled"] is True


def test_comment_record_carries_no_raw_sender():
    record = comment_record(
        FakeMessage(9, text="смачно", sender_id=555), SOURCE, "@c", 7, SALT, provenance()
    )

    assert record["record_type"] == "comment"
    assert record["parent_msg_id"] == 7
    assert record["sender_anon_id"] == sender_anon_id(555, SALT)
    assert "555" not in str(record)


def test_comment_record_keeps_the_reply_target_raw():
    """Whatever Telethon reports, unread and unresolved — the store is not the place to decide
    whether a reply target is the mirrored post or another commenter."""
    prov = provenance()
    replying = comment_record(
        FakeMessage(9, sender_id=1, reply_to_msg_id=8), SOURCE, "@c", 7, SALT, prov
    )
    top_level = comment_record(FakeMessage(10, sender_id=1), SOURCE, "@c", 7, SALT, prov)

    assert replying["reply_to_msg_id"] == 8
    assert replying["parent_msg_id"] == 7  # the channel post; a different id space
    assert top_level["reply_to_msg_id"] is None


def test_the_library_still_calls_it_reply_to_msg_id():
    """The fake above proves the record builder, not the attribute name it reads. A rename in
    Telethon would leave every test green and every stored reply target None."""
    from telethon.tl.custom.message import Message

    assert isinstance(Message.reply_to_msg_id, property)


def test_post_collection_is_untouched_by_the_reply_target():
    """4.5g5 Task 2 is scoped to comments; a post's record must not have grown a field."""
    record = post_record(FakeMessage(11, text="пост"), SOURCE, "@c", provenance())

    assert "reply_to_msg_id" not in record


def test_collapse_albums_merges_by_grouped_id():
    prov = provenance()
    records = [
        post_record(FakeMessage(11, grouped_id=42, media=object()), SOURCE, "@c", prov),
        post_record(FakeMessage(12, grouped_id=42, text="caption", replies=5), SOURCE, "@c", prov),
        post_record(FakeMessage(13, text="single"), SOURCE, "@c", prov),
    ]

    merged = collapse_albums(records)

    assert [r["msg_id"] for r in merged] == [11, 13]
    assert merged[0]["text"] == "caption"
    assert merged[0]["has_media"] is True
    assert merged[0]["reply_count"] == 5


def test_append_deduplicates_across_reruns(tmp_path):
    prov = provenance()
    records = [post_record(FakeMessage(i, text=str(i)), SOURCE, "@c", prov) for i in (1, 2)]

    assert RawStore(tmp_path).append(records) == 2
    # A second store instance re-reads the file: the rerun must add nothing.
    reopened = RawStore(tmp_path)
    assert reopened.append(records) == 0
    assert reopened.append(records + [post_record(FakeMessage(3), SOURCE, "@c", prov)]) == 1
    assert reopened.index("post", "@c").count == 3


def test_a_post_and_a_comment_may_share_a_msg_id(tmp_path):
    prov = provenance()
    store = RawStore(tmp_path)
    store.append([post_record(FakeMessage(100, replies=1), SOURCE, "@c", prov)])
    store.append([comment_record(FakeMessage(100, sender_id=1), SOURCE, "@c", 100, SALT, prov)])

    assert store.index("post", "@c").count == 1
    assert store.index("comment", "@c").count == 1


def test_index_reports_threads_to_fetch_and_the_date_range(tmp_path):
    prov = provenance()
    store = RawStore(tmp_path)
    store.append(
        [
            post_record(FakeMessage(1, replies=4), SOURCE, "@c", prov),
            post_record(FakeMessage(2), SOURCE, "@c", prov),
        ]
    )
    store.append([comment_record(FakeMessage(50, sender_id=1), SOURCE, "@c", 1, SALT, prov)])

    posts = RawStore(tmp_path).index("post", "@c")
    assert posts.with_replies == {1}
    assert posts.first_date == posts.last_date == "2026-07-01T12:00:00+00:00"
    assert RawStore(tmp_path).index("comment", "@c").parents == {1}


def test_a_truncated_last_line_does_not_break_the_rerun(tmp_path):
    prov = provenance()
    RawStore(tmp_path).append([post_record(FakeMessage(1), SOURCE, "@c", prov)])
    path = RawStore(tmp_path).path("post", "@c")
    with path.open("a", encoding="utf-8") as handle:
        handle.write('{"record_type": "post", "msg_i')  # killed mid-write

    index = RawStore(tmp_path).index("post", "@c")
    assert index.ids == {1}
    assert index.damaged_lines == 1


def test_missing_salt_explains_itself(tmp_path, monkeypatch):
    monkeypatch.delenv("RAW_STORE_SALT", raising=False)
    env = tmp_path / ".env"
    env.write_text("TELEGRAM_API_ID=1\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="RAW_STORE_SALT"):
        load_salt(env)


# --- the durable integrity baseline (PROMPT-5a1 F6) ---------------------------------------


BASELINE = Path(__file__).resolve().parents[1] / "results" / "raw_v1_baseline.sha256"


def baseline_lines() -> list[tuple[str, Path]]:
    """`shasum -c` format: a hash, two spaces, a repo-relative path. `#` lines are comments."""
    rows = []
    for line in BASELINE.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, _, name = line.partition("  ")
        rows.append((digest, BASELINE.parents[1] / name))
    return rows


def test_the_raw_v1_baseline_names_the_six_store_files():
    """`data/` is gitignored, so nothing in git can say these stores were left alone.

    The parse is asserted here rather than only at the shell, because a baseline that stopped
    covering a file would still print six cheerful OK lines for the five it kept.
    """
    rows = baseline_lines()

    assert len(rows) == 6
    assert {path.parent.name for _, path in rows} == {"posts", "comments"}
    assert all(len(digest) == 64 and int(digest, 16) >= 0 for digest, _ in rows)
    assert len({path for _, path in rows}) == 6


@pytest.mark.skipif(not (BASELINE.parents[1] / "data" / "raw").exists(), reason="gitignored data")
def test_the_raw_v1_stores_still_hash_to_their_baseline():
    """`shasum -c results/raw_v1_baseline.sha256`, as a test that runs with the suite."""
    for digest, path in baseline_lines():
        assert path.exists(), f"{path} is in the baseline and not on disk"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, f"{path} moved"
