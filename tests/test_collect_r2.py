"""Offline tests for the r2 collector — no Telegram, no session, no store outside tmp_path.

`--posts` and `--comments` are the two WRITE paths, and the thing they write on every row is
provenance that belongs to ONE source: `source_type` and `comments_enabled` are the source's own.
This script first shipped with a single `make_provenance(None, ...)` hoisted above the loops, which
raised `AttributeError` before a single message was read — 47 green tests over the phase's other
modules and nothing at all over this one ([[the_entry_points_preamble_is_untested_code]]).

So both loops are driven here, and the assertion is per row rather than per run: two sources of
different `source_type` collected in one pass must each be stamped with their own.
"""

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import collect_r2 as collect  # noqa: E402

from market_pulse.raw_store import RawStore  # noqa: E402
from market_pulse.registry import Registry, Source, Taxonomy  # noqa: E402

NOW = datetime(2026, 8, 20, 12, tzinfo=UTC)
SINCE = datetime(2026, 8, 2, 12, tzinfo=UTC)


def source(handle, kind, *, comments=False):
    return Source(handle[1:].lower(), handle, kind, (handle,), True, comments)


def message(msg_id, *, replies=0):
    return SimpleNamespace(
        id=msg_id,
        date=NOW,
        raw_text=f"post {msg_id}",
        media=None,
        grouped_id=None,
        action=None,
        sender_id=7,
        reply_to_msg_id=None,
        replies=SimpleNamespace(replies=replies) if replies else None,
    )


class FakeClient:
    """Enough Telethon for the two write loops. Nothing here reaches the network."""

    def __init__(self, per_channel):
        self.per_channel, self.seen = per_channel, []

    async def start(self):
        pass

    async def disconnect(self):
        pass

    async def get_entity(self, handle):
        self.seen.append(handle)
        return SimpleNamespace(username=str(handle).lstrip("@"), id=1)

    def iter_messages(self, entity, reply_to=None, **kwargs):
        messages = self.per_channel[f"@{entity.username}"]

        async def gen():
            for one in messages if reply_to is None else messages[:1]:
                yield one

        return gen()


def drive(monkeypatch, tmp_path, pairs, client, **phases):
    monkeypatch.setattr(collect, "STORE_ROOT", tmp_path / "raw")
    monkeypatch.setattr(collect, "RECORD", tmp_path / "collect_r2.json")
    monkeypatch.setattr(collect, "JOIN_LOG", tmp_path / "joins.jsonl")
    monkeypatch.setattr(collect, "CHANNEL_PAUSE", 0)
    monkeypatch.setattr(collect, "THREAD_PAUSE", 0)
    monkeypatch.setattr(collect, "REQUEST_PAUSE", 0)
    monkeypatch.setattr(collect, "build_client", lambda *a, **k: client)
    monkeypatch.setattr(collect, "load_salt", lambda *a, **k: "salt")
    monkeypatch.setattr(collect, "a1_sources", lambda registry: pairs)
    off = {
        "plan": False,
        "join": False,
        "posts": False,
        "comments": False,
        "only": None,
        "max": None,
    }
    args = SimpleNamespace(**{**off, **phases})
    registry = Registry(tuple(src for src, _ in pairs), Taxonomy({"dairy": {}}), ())
    return asyncio.run(collect.run(args, registry))


def test_every_stored_post_carries_ITS_OWN_sources_provenance(monkeypatch, tmp_path):
    """The bug this file exists for: one provenance for the whole run cannot describe two sources.

    Two channels of different `source_type` in one `--posts` pass. If provenance were built once
    above the loop, every row would carry the first channel's type — and built from `None`, as it
    shipped, the run dies before the first message.
    """
    pairs = [
        (source("@official", "official_retail"), "@official"),
        (source("@chat", "community", comments=True), "@chat"),
    ]
    client = FakeClient({"@official": [message(1), message(2)], "@chat": [message(3)]})

    drive(monkeypatch, tmp_path, pairs, client, posts=True)

    store = RawStore(tmp_path / "raw")
    for handle, kind, comments in (
        ("@official", "official_retail", False),
        ("@chat", "community", True),
    ):
        rows = store.rows("post", handle)
        assert rows, handle
        for row in rows:
            assert row["provenance"]["source_type"] == kind, handle
            assert row["provenance"]["comments_enabled"] is comments, handle
            assert row["provenance"]["session"] == "collect_r2", handle


def test_the_comment_pass_stamps_the_source_it_is_reading(monkeypatch, tmp_path):
    """`--comments` is the other write path, and it had the same single hoisted provenance.

    A post with replies is placed first so the pass has a thread to walk; the channel is joined in
    the log because an unjoined one is skipped before any write.
    """
    src = source("@chat", "community", comments=True)
    store = RawStore(tmp_path / "raw")
    from market_pulse.raw_store import post_record

    store.append([post_record(message(10, replies=2), src, "@chat", {"session": "seed"})])
    (tmp_path / "joins.jsonl").write_text(
        '{"channel": "@chat", "outcome": "joined"}\n', encoding="utf-8"
    )

    drive(
        monkeypatch,
        tmp_path,
        [(src, "@chat")],
        FakeClient({"@chat": [message(11)]}),
        comments=True,
    )

    rows = store.rows("comment", "@chat")
    assert rows
    for row in rows:
        assert row["provenance"]["source_type"] == "community"
        assert row["provenance"]["comments_enabled"] is True
        assert row["provenance"]["session"] == "collect_r2"


def test_a_channel_that_writes_into_a_pinned_raw_v1_file_is_refused_before_the_client(
    monkeypatch, tmp_path
):
    """SP-4's negative control: four A1 channels map onto the six pinned store files.

    The guard is keyed on the path a write would land on rather than on a channel name, so the
    root it is driven with IS the test. SP-4 ruling (a) moved `STORE_ROOT` to the live root, where
    this guard is right to stay quiet — so the archive root is set back here explicitly, which is
    the configuration the guard exists for and the one a later retarget would restore. A test that
    patched the root away instead would pass over a guard that does nothing.

    Nothing is written: the refusal lands before `build_client`, which is replaced here by something
    that raises, so a guard that fired too late would surface as that error instead of this one.
    """
    monkeypatch.setattr(collect, "STORE_ROOT", collect.ARCHIVE_ROOT)

    def never(*a, **k):
        raise AssertionError("the client was built before the guard refused")

    monkeypatch.setattr(collect, "RECORD", tmp_path / "collect_r2.json")
    monkeypatch.setattr(collect, "JOIN_LOG", tmp_path / "joins.jsonl")
    monkeypatch.setattr(collect, "build_client", never)
    monkeypatch.setattr(collect, "load_salt", lambda *a, **k: "salt")
    pairs = [(source("@VARUS_channel", "official_retail"), "@VARUS_channel")]
    monkeypatch.setattr(collect, "a1_sources", lambda registry: pairs)
    args = SimpleNamespace(plan=False, join=False, posts=True, comments=False, only=None, max=None)
    registry = Registry(tuple(src for src, _ in pairs), Taxonomy({"dairy": {}}), ())
    with pytest.raises(SystemExit, match="pinned raw v1 files"):
        asyncio.run(collect.run(args, registry))


def test_an_unpinned_channel_is_not_refused_by_the_same_guard():
    """The other direction: the guard names four channels, not every channel.

    Without this a guard that refused everything would look identical to one that works
    ([[a_guard_conservative_enough_to_refuse_everything]]).
    """
    from market_pulse.raw_store import RawStore

    varus = [(source("@VARUS_channel", "official_retail"), "@VARUS_channel")]
    archive = RawStore(collect.ARCHIVE_ROOT)
    collect.refuse_pinned([(source("@znishkom", "official_retail"), "@znishkom")], archive)
    with pytest.raises(SystemExit, match="VARUS_channel"):
        collect.refuse_pinned(varus, archive)
    # And the third direction, which is what SP-4 ruling (a) bought: under the LIVE root the same
    # pinned channel is collected, because the write no longer lands on the pinned file.
    collect.refuse_pinned(varus, RawStore(collect.STORE_ROOT))
    assert collect.STORE_ROOT == collect.LIVE_ROOT


def test_the_guard_reads_the_pinned_set_from_the_collector_that_owns_it():
    """One list, not two. A second copy here would be the copy that holds the writer."""
    import collect_5c1

    assert collect.protected is collect_5c1.protected
    assert len(collect.protected()) == 6
