"""Offline tests for the raw store — no Telegram, no session."""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pytest
from market_pulse.raw_store import (
    ARCHIVE_ROOT,
    LIVE_ROOT,
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


def test_several_rows_from_one_message_all_survive_the_append(tmp_path):
    """The fan-out case the (channel, msg_id) key cannot hold, and 5c2's positions leg is made of.

    One leaflet page yields N positions, and every one of them is a row the 3.18 (6) sitting shows
    field by field. They share the page's ``msg_id`` because that is the message they were read
    from, so under a msg_id-only key the second and every later position is silently dropped —
    inside a SINGLE :meth:`append` call, because `_by_file` marks each record seen as it iterates.

    ``row_id`` is what a record carries when its identity is finer than its message. Absent — every
    post and every comment ever stored — the key falls back to ``msg_id`` and nothing changes.
    """
    store = RawStore(tmp_path)
    rows = [
        {
            "record_type": "position_row",
            "channel": "@VARUS_channel",
            "msg_id": 4340,
            "row_id": f"@VARUS_channel:4340:{ordinal}",
            "brand": name,
        }
        for ordinal, name in enumerate(("Рудь", "Яготинське", "Своя Лінія"))
    ]

    assert store.append(rows) == 3
    assert len(RawStore(tmp_path).rows("position_row", "@VARUS_channel")) == 3
    index = RawStore(tmp_path).index("position_row", "@VARUS_channel")
    assert index.ids == {4340}, (
        "`ids` stays the MESSAGE id space: it is what a queue subtracts answered pages by"
    )
    assert index.count == 1, (
        "and `count` counts THOSE — one page, three rows. Pinned rather than left to be discovered:"
        " for a fanned-out type it is not the row count, and nothing reads it today"
    )


def test_a_rerun_of_a_fanned_out_page_writes_none_of_its_rows_twice(tmp_path):
    """The other half: a finer key must not cost idempotence. Same rows, second call, zero written."""
    store = RawStore(tmp_path)
    rows = [
        {
            "record_type": "position_row",
            "channel": "@VARUS_channel",
            "msg_id": 4340,
            "row_id": f"@VARUS_channel:4340:{ordinal}",
        }
        for ordinal in range(3)
    ]
    store.append(rows)

    assert RawStore(tmp_path).append(rows) == 0
    assert len(RawStore(tmp_path).rows("position_row", "@VARUS_channel")) == 3


# --- SP-4 ruling (a): the archive, the live root and the union (plan §5.14) -------------------


def a_post(msg_id: int, text: str) -> dict:
    return post_record(FakeMessage(msg_id, text=text), SOURCE, "@VARUS_channel", provenance())


def test_the_archive_root_refuses_a_write_and_the_live_root_takes_one():
    """The guard, both directions, on the REAL roots — a refusal proves nothing about a tmp path.

    v1 is read-only forever (SP-4 ruling (a), review 2026-08-30) and the append is irreversible:
    `data/` is gitignored, so `git status` is silent in both directions and
    `results/raw_v1_baseline.sha256` is the only durable proof. The refusing direction is asserted
    on `data/raw` itself, and the accepting direction on `data/raw_r2` itself — a guard self-test
    that only ever refuses cannot tell «blocked» from «broken»
    ([[guard_selftest_negative_control]]).
    """
    archive = RawStore(ARCHIVE_ROOT)
    for kind, record in (
        ("posts", a_post(1, "into data/raw/posts")),
        (
            "comments",
            comment_record(
                FakeMessage(2, text="into data/raw/comments"),
                SOURCE,
                "@VARUS_channel",
                1,
                SALT,
                provenance(),
            ),
        ),
    ):
        with pytest.raises(SystemExit) as refusal:
            archive.append([record])
        assert "read-only forever" in str(refusal.value)
        assert "raw_v1_baseline.sha256" in str(refusal.value)
        assert not (ARCHIVE_ROOT / kind / "_guard_selftest.jsonl").exists()

    live = LIVE_ROOT / "posts" / "_guard_selftest.jsonl"
    written = a_post(1, "into the live root") | {"channel": "_guard_selftest"}
    try:
        assert RawStore(LIVE_ROOT).append([written]) == 1
        assert live.exists() and "into the live root" in live.read_text(encoding="utf-8")
    finally:
        live.unlink(missing_ok=True)


def test_the_baseline_still_verifies_after_the_refusal():
    """The refusal above is only worth something if the six pinned files are still their bytes."""
    import subprocess

    baseline = Path(__file__).resolve().parents[1] / "results" / "raw_v1_baseline.sha256"
    done = subprocess.run(
        ["shasum", "-c", str(baseline)],
        cwd=baseline.parents[1],
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.count(": OK") == 6, done.stdout


def test_the_union_reads_both_roots_and_the_live_row_wins(tmp_path):
    """v1 ∪ r2, deduplicated on (channel, msg_id), r2 winning — the ruling's read rule.

    Both directions of the dedup matter: a row only the archive has is still read (the top-up is a
    TOP-UP, not a re-collection), and a row both roots hold is the live root's — otherwise an
    edited or re-fetched post would be answered by the frozen copy forever.
    """
    archive, live = tmp_path / "raw", tmp_path / "raw_r2"
    RawStore(archive).append([a_post(1, "archive"), a_post(2, "archive only")])
    RawStore(live).append([a_post(1, "live"), a_post(3, "live only")])

    union = RawStore(live, archives=(archive,))
    rows = union.rows("post", "@VARUS_channel")
    assert [row["msg_id"] for row in rows] == [1, 2, 3]
    assert {row["msg_id"]: row["text"] for row in rows}[1] == "live"
    assert union.index("post", "@VARUS_channel").count == 3
    # And the union's dedup is what makes the top-up idempotent: a row the ARCHIVE holds is not
    # re-written into the live root.
    assert union.append([a_post(2, "archive only")]) == 0
    assert not (live / "posts" / "VARUS_channel.jsonl").read_text(encoding="utf-8").count(
        "archive only"
    )


def test_the_write_path_is_the_live_root_even_when_the_archive_holds_the_channel(tmp_path):
    """`path()` is the WRITE path and stays under `root`; `paths()` is what the reader walks."""
    store = RawStore(tmp_path / "raw_r2", archives=(tmp_path / "raw",))
    assert store.path("post", "@VARUS_channel").parent.parent == tmp_path / "raw_r2"
    assert [p.parent.parent for p in store.paths("post", "@VARUS_channel")] == [
        tmp_path / "raw",
        tmp_path / "raw_r2",
    ]
