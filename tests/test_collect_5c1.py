"""Offline tests for the 5c1 collector — no Telegram, no session, no store outside tmp_path.

The three things a mistake here costs, and the three things these tests hold: a join into a
group the operator forbade, an append into one of the six pinned raw v1 files, and a window that
slides when a run is resumed a day later.
"""

import asyncio
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest
from telethon.errors import FloodWaitError

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import collect_5c1 as collect  # noqa: E402

from market_pulse.registry import Registry, Source, Taxonomy  # noqa: E402

NOW = datetime(2026, 8, 7, 12, tzinfo=UTC)


def source(handle, *, comments=False, watch=False, sid=None):
    return Source(sid or handle[1:].lower(), handle, "community", (handle,), True, comments, watch)


def registry_of(*sources):
    return Registry(tuple(sources), Taxonomy({"dairy": {}}), ())


def gate_of(composition, joins):
    return {
        "registry_written": True,
        "rulings": {"composition": composition, "joins_authorised": joins},
    }


# --- the six pinned files ------------------------------------------------------------------------


def test_the_guard_reads_the_pinned_paths_off_the_pin_file():
    """The guard and the `shasum -c` the report runs must not be able to drift apart."""
    paths = {p.relative_to(REPO_ROOT).as_posix() for p in collect.protected()}
    assert len(paths) == 6
    assert "data/raw/posts/VARUS_channel.jsonl" in paths
    assert all(p.startswith("data/raw/") for p in paths)


def test_a_channel_that_maps_onto_a_pinned_file_is_refused_before_any_record_is_built():
    """The negative control for the whole read-only promise. @VARUS_channel is a real registry
    channel whose store is pinned; if a ruling ever put it back into the composition, this is
    what stops the append."""
    registry = registry_of(source("@VARUS_channel", comments=True))
    gate = gate_of({"comments": ["@VARUS_channel"]}, ["@VARUS_channel"])
    with pytest.raises(SystemExit, match="pinned raw v1 file"):
        collect.collectable(registry, gate)


def test_a_channel_the_rulings_did_not_enter_is_not_collected():
    """The registry holds the four originals too; only what the 5c1 rulings added is in scope."""
    registry = registry_of(source("@old"), source("@fresh"))
    rows = collect.collectable(registry, gate_of({"posts": ["@fresh"]}, []))
    assert [handle for _, handle in rows] == ["@fresh"]


# --- who may be joined ---------------------------------------------------------------------------


def test_a_watch_channel_is_never_joinable_even_though_it_has_a_group():
    """SPEC 3.11 (4): a watch channel keeps its discussion group and is joined only after it
    posts again and the operator says so. `comments_enabled` alone cannot express that."""
    registry = registry_of(
        source("@live", comments=True), source("@quiet", comments=True, watch=True)
    )
    gate = gate_of({"comments": ["@live"], "watch": ["@quiet"]}, ["@live"])
    assert [handle for _, handle in collect.joinable(registry, gate)] == ["@live"]


def test_a_city_feed_is_collected_and_never_joined():
    """ "Дозаявка №3": posts-only until 5c2 rules on a category filter for threads, because
    without one a city chat's whole traffic lands in a paid inference queue. 11 of the 16 have a
    group, so this cannot rest on their not having one — it rests on `comments_enabled: false`,
    and both derivations of the join set have to agree that they are out."""
    registry = registry_of(source("@live", comments=True), source("@poltava_misto"))
    gate = gate_of({"comments": ["@live"], "posts": ["@poltava_misto"]}, ["@live"])
    assert [handle for _, handle in collect.collectable(registry, gate)] == [
        "@live",
        "@poltava_misto",
    ]
    assert [handle for _, handle in collect.joinable(registry, gate)] == ["@live"]


def test_only_narrows_the_fetch_loop_and_refuses_a_handle_it_does_not_collect():
    """The resolve budget is what this is for — 16 new city feeds must not cost 68 resolves. It
    narrows the LOOP; `channel_row` reads the store, so the record still covers every channel."""
    channels = [(source("@a"), "@a"), (source("@b"), "@b"), (source("@c"), "@c")]
    assert [h for _, h in collect.narrowed(channels, None)] == ["@a", "@b", "@c"]
    assert [h for _, h in collect.narrowed(channels, ["@b", "@c"])] == ["@b", "@c"]
    with pytest.raises(SystemExit, match="does not collect"):
        collect.narrowed(channels, ["@b", "@nope"])


def test_the_registry_and_the_rulings_must_agree_about_the_join_list():
    """Two independent derivations of the same set. Disagreement means something moved between
    the ruling and the registry write, and the answer is to stop, not to pick one."""
    registry = registry_of(source("@a", comments=True), source("@b", comments=True))
    gate = gate_of({"comments": ["@a", "@b"]}, ["@a"])
    with pytest.raises(SystemExit, match="disagree about which groups"):
        collect.joinable(registry, gate)


# --- the join log is the cursor -------------------------------------------------------------------


class FakeClient:
    """Enough Telethon for the join loop. Nothing here reaches the network."""

    def __init__(self, *, group=True, left=True, blow_up_on=lambda h: None):
        self.group, self.left, self.blow_up_on = group, left, blow_up_on
        self.joined = []

    async def connect(self):
        pass

    async def is_user_authorized(self):
        return True

    async def disconnect(self):
        pass

    async def get_entity(self, handle):
        return SimpleNamespace(username=str(handle).lstrip("@"), id=1)

    async def __call__(self, request):
        name = type(request).__name__
        if name == "GetFullChannelRequest":
            chat = SimpleNamespace(id=99, title="G", left=self.left)
            return SimpleNamespace(
                full_chat=SimpleNamespace(linked_chat_id=99 if self.group else None),
                chats=[chat] if self.group else [],
            )
        self.joined.append(request)
        return None


def drive_joins(monkeypatch, tmp_path, handles, client):
    monkeypatch.setattr(collect, "JOIN_LOG", tmp_path / "joins.jsonl")
    monkeypatch.setattr(collect, "JOIN_PAUSE", 0)
    channels = [(source(handle, comments=True), handle) for handle in handles]
    return asyncio.run(collect.run_joins(client, channels, None))


def test_a_join_is_logged_with_its_group_and_never_attempted_twice(monkeypatch, tmp_path):
    client = FakeClient()
    first = drive_joins(monkeypatch, tmp_path, ["@a", "@b"], client)
    assert first == {"attempted": 2, "landed": 2, "flood_wait_seconds": None}

    rows = [json.loads(line) for line in (tmp_path / "joins.jsonl").read_text().splitlines()]
    assert [r["outcome"] for r in rows] == ["joined", "joined"]
    assert rows[0]["group_id"] == 99 and rows[0]["group_title"] == "G"

    second = drive_joins(monkeypatch, tmp_path, ["@a", "@b"], FakeClient())
    assert second["attempted"] == 0, "the log is the cursor — a landed join is not repeated"


def test_a_channel_we_are_already_in_is_recorded_rather_than_re_joined(monkeypatch, tmp_path):
    client = FakeClient(left=False)
    drive_joins(monkeypatch, tmp_path, ["@a"], client)
    rows = [json.loads(line) for line in (tmp_path / "joins.jsonl").read_text().splitlines()]
    assert rows[0]["outcome"] == "already_member"
    assert client.joined == [], "no JoinChannelRequest was sent"


def test_a_channel_without_a_group_is_logged_and_not_joined(monkeypatch, tmp_path):
    client = FakeClient(group=False)
    drive_joins(monkeypatch, tmp_path, ["@a"], client)
    rows = [json.loads(line) for line in (tmp_path / "joins.jsonl").read_text().splitlines()]
    assert rows[0]["outcome"] == "no group"
    assert client.joined == []


def test_a_floodwait_stops_the_joins_and_writes_the_wait_down(monkeypatch, tmp_path):
    """A rate limit on joining is measured in hours. Walking into the next one would spend it."""

    class Throttled(FakeClient):
        async def get_entity(self, handle):
            if handle == "@b":
                raise FloodWaitError(request=None, capture=3600)
            return await super().get_entity(handle)

    out = drive_joins(monkeypatch, tmp_path, ["@a", "@b", "@c"], Throttled())
    assert out["flood_wait_seconds"] == 3600
    assert out["landed"] == 1
    rows = [json.loads(line) for line in (tmp_path / "joins.jsonl").read_text().splitlines()]
    assert [r["channel"] for r in rows] == ["@a", "@b"], "it stopped instead of trying @c"
    assert rows[-1]["outcome"] == "floodwait"


def test_an_account_wide_floodwait_is_read_back_from_the_log(monkeypatch, tmp_path):
    """The 2026-08-07 wall: Telegram asked for 20 HOURS on ResolveUsernameRequest, which every
    join and every comment fetch starts with. Retrying inside that window is how a 20-hour wait
    becomes a longer one, so the log carries the expiry and the run refuses until it passes."""
    later = (NOW + timedelta(hours=20)).isoformat()
    state = {
        "*": {"outcome": "floodwait", "seconds": 72312, "clears_at": later, "at": NOW.isoformat()}
    }
    assert collect.flood_wait_until(state, NOW) == datetime.fromisoformat(later)
    assert collect.flood_wait_until(state, NOW + timedelta(hours=21)) is None
    assert collect.flood_wait_until({}, NOW) is None

    # A per-channel floodwait row without an expiry is a retryable attempt, not a global wall.
    old = {"@a": {"outcome": "floodwait", "seconds": 60, "at": NOW.isoformat()}}
    assert collect.flood_wait_until(old, NOW) is None


def test_the_pace_is_measured_from_the_log_not_from_this_process(monkeypatch, tmp_path):
    """A run stopped for other work and resumed would otherwise fire its next join seconds after
    the previous one — the burst the pace exists to avoid. The log is the cursor; it is the clock
    too. A failed attempt still counts: it made requests."""
    monkeypatch.setattr(collect, "JOIN_PAUSE", 900.0)
    assert collect.seconds_until_next_join({}, NOW) == 0.0, "a first join waits for nothing"

    state = {"@a": {"at": (NOW - timedelta(seconds=100)).isoformat(), "outcome": "joined"}}
    assert collect.seconds_until_next_join(state, NOW) == 800.0

    state["@b"] = {"at": (NOW - timedelta(seconds=2000)).isoformat(), "outcome": "error"}
    assert collect.seconds_until_next_join(state, NOW) == 800.0, "the LAST attempt sets the clock"

    old = {"@a": {"at": (NOW - timedelta(hours=3)).isoformat(), "outcome": "joined"}}
    assert collect.seconds_until_next_join(old, NOW) == 0.0, "a long gap owes no extra wait"


def test_a_floodwait_row_is_not_a_landed_join(monkeypatch, tmp_path):
    """The negative control for the cursor: a wait must be retried, a join must not."""
    (tmp_path / "joins.jsonl").write_text(
        json.dumps({"channel": "@a", "outcome": "floodwait", "seconds": 60}) + "\n",
        encoding="utf-8",
    )
    out = drive_joins(monkeypatch, tmp_path, ["@a"], FakeClient())
    assert out["attempted"] == 1


# --- the window does not slide ---------------------------------------------------------------------


def test_the_window_since_is_fixed_by_the_first_run_and_read_back_after(tmp_path, monkeypatch):
    """A resume two days later must collect the same four weeks, not four weeks from today —
    otherwise the record's window dates describe a range nothing was ever collected over."""
    monkeypatch.setattr(collect, "RECORD", tmp_path / "collect.json")
    first_run = NOW.isoformat(timespec="seconds")
    since = (NOW - timedelta(days=collect.WINDOW_DAYS)).isoformat()
    collect.RECORD.write_text(
        json.dumps({"window": {"since": since, "first_run_at": first_run}}), encoding="utf-8"
    )
    prior = json.loads(collect.RECORD.read_text(encoding="utf-8"))
    assert collect.held(prior, "window", {})["since"] == since
    assert collect.held(prior, "window", {})["first_run_at"] == first_run
    assert collect.held(None, "window", {}) == {}, "a first run has nothing to read back"


# --- the comment write path ------------------------------------------------------------------------


class ThreadClient:
    """A client that answers `iter_messages(entity, reply_to=parent)` with a thread."""

    def __init__(self, thread):
        self.thread, self.asked = thread, []

    def iter_messages(self, entity, reply_to=None, **kwargs):
        self.asked.append(reply_to)

        async def gen():
            for message in self.thread:
                yield message

        return gen()


def message(msg_id, *, reply_to=None, text="ок", action=None):
    return SimpleNamespace(
        id=msg_id,
        reply_to_msg_id=reply_to,
        date=NOW,
        raw_text=text,
        sender_id=42,
        action=action,
        media=None,
        grouped_id=None,
        replies=None,
    )


def store_with_a_post(tmp_path, handle, src):
    from market_pulse.raw_store import RawStore, post_record

    store = RawStore(tmp_path / "raw")
    post = SimpleNamespace(
        id=832,
        date=NOW,
        raw_text="post",
        media=None,
        grouped_id=None,
        replies=SimpleNamespace(replies=3),
    )
    store.append([post_record(post, src, handle, {"session": "t"})])
    return store


def test_a_thread_lands_in_a_new_comment_file_and_a_re_run_stores_nothing(tmp_path, monkeypatch):
    """The only path that writes comments. `--posts` stops before it, so an untested `--comments`
    is a write path proved by nothing — and the dedup that makes a resume safe is RawStore's,
    which means the second run must store zero, not "skip".
    """
    src = source("@chan", comments=True)
    store = store_with_a_post(tmp_path, "@chan", src)
    client = ThreadClient(
        [message(11, reply_to=5), message(12, reply_to=11), message(13, action="x")]
    )

    got = asyncio.run(
        collect.fetch_threads(client, object(), src, "@chan", store, "salt", {"session": "t"})
    )
    assert got == {"threads": 1, "comments_stored": 2, "threads_failed": 0}
    assert client.asked == [832], "the thread is fetched by its parent post id"

    written = (
        (tmp_path / "raw" / "comments" / "chan.jsonl").read_text(encoding="utf-8").splitlines()
    )
    assert len(written) == 2, "the service message is not a comment"
    row = json.loads(written[0])
    assert row["parent_msg_id"] == 832 and row["reply_to_msg_id"] == 5
    assert len(row["sender_anon_id"]) == 64, "the salt reached the record"

    again = asyncio.run(
        collect.fetch_threads(client, object(), src, "@chan", store, "salt", {"session": "t"})
    )
    assert again["comments_stored"] == 0 and again["threads"] == 0


def test_one_unreadable_thread_is_counted_and_does_not_end_the_channel(tmp_path):
    """Posts older than the discussion group have no thread to read; the count is the finding."""
    src = source("@chan", comments=True)
    store = store_with_a_post(tmp_path, "@chan", src)

    class Broken(ThreadClient):
        def iter_messages(self, entity, reply_to=None, **kwargs):
            raise RuntimeError("no thread")

    got = asyncio.run(
        collect.fetch_threads(Broken([]), object(), src, "@chan", store, "salt", {"session": "t"})
    )
    assert got == {"threads": 1, "comments_stored": 0, "threads_failed": 1}


def test_the_record_totals_are_summed_from_the_rows(tmp_path, monkeypatch):
    monkeypatch.setattr(collect, "RECORD", tmp_path / "collect.json")
    rows = [
        {"channel": "@a", "posts_stored": 10, "comments_stored": 40, "damaged_lines": 0},
        {"channel": "@b", "posts_stored": 0, "comments_stored": 0, "damaged_lines": 1},
    ]
    record = collect.write_record(None, None, rows, NOW, NOW.isoformat(), {"phases_run": ["posts"]})
    assert record["totals"] == {
        "channels": 2,
        "posts_stored": 10,
        "comments_stored": 40,
        "damaged_lines": 1,
        "channels_with_posts": 1,
        "channels_with_comments": 1,
    }
    assert record["window"]["since"] == NOW.isoformat()
    assert record["git"]["commit"]
