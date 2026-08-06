"""Offline tests for the Phase-5a loop skeleton — no Telegram, no session, no writes."""

import hashlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import run_loop as runner  # noqa: E402

from market_pulse import loop  # noqa: E402
from market_pulse.raw_store import RawStore, comment_record, post_record  # noqa: E402
from market_pulse.registry import Source  # noqa: E402
from test_raw_store import SALT, SOURCE, FakeMessage, provenance  # noqa: E402

NO_COMMENTS = Source("silpo", "Сільпо", "official_retail", ("@silposilpo",), True, False)


def store_with(tmp_path, *, posts=(), comments=()):
    """A store holding the given post ids, and comments under the given parents."""
    store = RawStore(tmp_path)
    store.append(
        [
            post_record(FakeMessage(i, replies=1), SOURCE, "@VARUS_channel", provenance())
            for i in posts
        ]
    )
    store.append(
        [
            comment_record(FakeMessage(i), SOURCE, "@VARUS_channel", parent, SALT, provenance())
            for parent, i in comments
        ]
    )
    return store


# --- cursor: advance and rollback ------------------------------------------------------


def test_advance_moves_the_watermark_to_the_newest_id():
    state = {}
    assert loop.advance(state, loop.POSTS, [12, 40, 7]) is None
    assert state[loop.POSTS] == 40


def test_advance_never_walks_backwards():
    state = {loop.POSTS: 500}
    previous = loop.advance(state, loop.POSTS, [10, 20])
    assert previous == 500
    assert state[loop.POSTS] == 500, "an older page must not drag the watermark back"


def test_advance_over_nothing_leaves_the_watermark_alone():
    state = {loop.POSTS: 500}
    assert loop.advance(state, loop.POSTS, []) == 500
    assert state[loop.POSTS] == 500


def test_rollback_puts_the_watermark_back_where_advance_found_it():
    state = {loop.POSTS: 500}
    previous = loop.advance(state, loop.POSTS, [900])
    assert state[loop.POSTS] == 900
    loop.rollback(state, loop.POSTS, previous)
    assert state[loop.POSTS] == 500


def test_rollback_of_a_first_advance_removes_the_key():
    """A channel that never had a watermark must not end up with a fabricated one."""
    state = {}
    previous = loop.advance(state, loop.POSTS, [900])
    loop.rollback(state, loop.POSTS, previous)
    assert loop.POSTS not in state


def test_a_failed_pass_leaves_the_saved_cursor_where_it_was(tmp_path):
    """Advance in memory, fail, roll back: what is on disk never saw the advance."""
    path = tmp_path / "loop_cursor.json"
    loop.save_cursor(path, {"@VARUS_channel": {loop.POSTS: 500}})

    cursor = loop.load_cursor(path)
    state = loop.channel_state(cursor, "@VARUS_channel")
    previous = loop.advance(state, loop.POSTS, [900])
    try:
        raise RuntimeError("the store write failed")
    except RuntimeError:
        loop.rollback(state, loop.POSTS, previous)

    assert loop.load_cursor(path)["@VARUS_channel"][loop.POSTS] == 500
    assert cursor["@VARUS_channel"][loop.POSTS] == 500


# --- idempotent ingest ------------------------------------------------------------------


def test_a_rerun_of_the_same_pass_stores_nothing_new(tmp_path):
    store = RawStore(tmp_path)
    records = [
        post_record(FakeMessage(i, replies=1), SOURCE, "@VARUS_channel", provenance())
        for i in (10, 11, 12)
    ]

    first = loop.ingest(store, records)
    second = loop.ingest(store, records)

    assert first == {"offered": 3, "stored": 3}
    assert second == {"offered": 3, "stored": 0}
    assert RawStore(tmp_path).index("post", "@VARUS_channel").count == 3


def test_ingest_stores_only_the_part_of_an_overlapping_pass_that_is_new(tmp_path):
    store = RawStore(tmp_path)
    loop.ingest(
        store, [post_record(FakeMessage(i), SOURCE, "@VARUS_channel", provenance()) for i in (1, 2)]
    )

    again = loop.ingest(
        store,
        [post_record(FakeMessage(i), SOURCE, "@VARUS_channel", provenance()) for i in (2, 3, 4)],
    )

    assert again == {"offered": 3, "stored": 2}


# --- the plan ---------------------------------------------------------------------------


def test_the_plan_counts_the_threads_that_have_no_comments_yet(tmp_path):
    store = store_with(tmp_path, posts=(1, 2, 3), comments=((1, 100), (1, 101)))

    row = loop.plan_channel(store, SOURCE, "@VARUS_channel", {})

    assert row["posts_stored"] == 3
    assert row["comments_stored"] == 2
    assert row["threads_to_fetch"] == 2, "posts 2 and 3 have replies and no comments stored"
    assert row["rows_to_inference"] == 2


def test_a_channel_without_comments_has_no_threads_to_fetch(tmp_path):
    store = store_with(tmp_path, posts=(1, 2))
    row = loop.plan_channel(store, NO_COMMENTS, "@VARUS_channel", {})
    assert row["threads_to_fetch"] == 0


def test_the_inference_watermark_is_what_shrinks_the_queue(tmp_path):
    store = store_with(tmp_path, posts=(1,), comments=((1, 100), (1, 101), (1, 102)))

    assert loop.plan_channel(store, SOURCE, "@VARUS_channel", {})["rows_to_inference"] == 3
    state = {loop.INFERENCE: 101}
    assert loop.plan_channel(store, SOURCE, "@VARUS_channel", state)["rows_to_inference"] == 1


def test_queue_depth_counts_only_ids_above_the_watermark():
    assert loop.queue_depth([1, 5, 9], None) == 3
    assert loop.queue_depth([1, 5, 9], 5) == 1
    assert loop.queue_depth([], 5) == 0


# --- the spend-guard hook point ----------------------------------------------------------


def test_the_guard_refuses_while_no_endpoint_is_registered():
    refusal = loop.inference_refusal(1234, None)
    assert refusal is not None
    assert "1234" in refusal and "3.11 (2)" in refusal


def test_an_unset_endpoint_from_env_keeps_the_guard_closed():
    """PROMPT-5a1 F4. `os.getenv` on an unset-but-present variable is `""`, not `None`.

    5b reads this endpoint out of env or config. Under `is None` the empty string counted as
    "registered", and the pass would decide it was allowed to spend before failing on the URL.
    """
    assert loop.inference_refusal(1234, "") is not None


def test_the_guard_opens_once_an_endpoint_exists():
    """The negative control: a guard that refuses everything proves nothing about what it blocks."""
    assert loop.inference_refusal(1234, "https://api.runpod.ai/v2/whatever") is None


def test_5a_registers_no_endpoint():
    assert runner.ENDPOINT is None, "5a has no serving endpoint — SPEC 3.11 (2) comes first"


# --- the script: purity, and the refusal of a live pass -----------------------------------


def digests(root: Path) -> dict:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def wire(monkeypatch, tmp_path, sources):
    """Point the script at a throwaway store and cursor, and forbid it a Telegram client."""
    monkeypatch.setattr(runner, "STORE_ROOT", tmp_path / "raw")
    monkeypatch.setattr(runner, "CURSOR", tmp_path / "loop_cursor.json")
    monkeypatch.setattr(runner, "SMOKE", tmp_path / "smoke" / "loop_5a.json")
    monkeypatch.setattr(runner, "load_registry", lambda _: type("R", (), {"sources": sources})())
    # Telethon's own constructor, not the repo's factory: patching `build_client` would only
    # catch a call through the front door, and "no network" has to hold for every door.
    import telethon

    monkeypatch.setattr(
        telethon, "TelegramClient", lambda *a, **k: pytest.fail("a dry pass built a client")
    )


def test_a_dry_pass_writes_nothing(monkeypatch, tmp_path):
    """Dry-run purity: no client, and every byte under the store and the cursor unchanged."""
    store_with(tmp_path / "raw", posts=(1, 2, 3), comments=((1, 100),))
    (tmp_path / "loop_cursor.json").write_text('{"@VARUS_channel": {"posts": 3}}', encoding="utf-8")
    wire(monkeypatch, tmp_path, [SOURCE])
    before = digests(tmp_path)

    assert runner.main(["--once", "--dry-run"]) == 0

    assert digests(tmp_path) == before
    assert not (tmp_path / "smoke").exists(), "a dry run is not a smoke run"


def test_a_live_pass_is_refused_before_anything_is_read(monkeypatch, tmp_path):
    wire(monkeypatch, tmp_path, [SOURCE])
    with pytest.raises(SystemExit, match="raw v1 stores"):
        runner.main(["--once"])


def test_the_smoke_writes_a_record_for_one_channel(monkeypatch, tmp_path):
    store_with(tmp_path / "raw", posts=(1, 2, 3), comments=((1, 100), (1, 101)))
    wire(monkeypatch, tmp_path, [SOURCE])

    assert runner.main(["--once", "--smoke", "--channel", "@VARUS_channel"]) == 0

    import json

    record = json.loads((tmp_path / "smoke" / "loop_5a.json").read_text(encoding="utf-8"))["runs"][
        -1
    ]
    assert record["smoke"] is True
    assert record["scope"]["channel"] == "@VARUS_channel"
    assert record["totals"]["rows_to_inference"] == 2
    assert record["inference"]["endpoint"] is None
    assert "3.11 (2)" in record["inference"]["refusal"]


def test_an_unknown_channel_stops_the_pass(monkeypatch, tmp_path):
    wire(monkeypatch, tmp_path, [SOURCE])
    with pytest.raises(SystemExit, match="@nope"):
        runner.main(["--once", "--dry-run", "--channel", "@nope"])
