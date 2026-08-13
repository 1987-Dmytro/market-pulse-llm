"""Offline tests for the Phase-5a loop skeleton — no Telegram, no session, no writes."""

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import run_loop as runner  # noqa: E402

from market_pulse import evidence, loop, parents, prompts  # noqa: E402
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


# --- the inference leg: the record is durable before the watermark moves -------------------

TASK = loop.COMMENT_TASK


def texted_store(tmp_path, *, posts=(), comments=()):
    """A store whose posts and comments carry text, so a with-post prompt can be rendered."""
    store = RawStore(tmp_path)
    store.append(
        [
            post_record(
                FakeMessage(i, text=f"пост {i}", replies=1), SOURCE, "@VARUS_channel", provenance()
            )
            for i in posts
        ]
    )
    store.append(
        [
            comment_record(
                FakeMessage(i, text=f"коментар {i}"),
                SOURCE,
                "@VARUS_channel",
                parent,
                SALT,
                provenance(),
            )
            for parent, i in comments
        ]
    )
    return store


def wired(tmp_path, *, posts=(1,), comments=((1, 100), (1, 101), (1, 102))):
    """(store, derived, posts-index, state) for one channel — everything the pass takes."""
    store = texted_store(tmp_path / "raw", posts=posts, comments=comments)
    derived = RawStore(tmp_path / "derived")
    return store, derived, parents.load(tmp_path / "raw" / "posts"), {}


def answer(task, rendering):
    return {"content": '{"sentiment": "neutral"}', "finish_reason": "stop"}


def run(store, derived, posts, state, rows=None, send=answer):
    return loop.inference_pass(
        rows
        if rows is not None
        else loop.queued(store, derived, "@VARUS_channel", state.get(loop.INFERENCE)),
        send=send,
        posts=posts,
        captions={},
        derived=derived,
        state=state,
        model_revision=None,
        served_by="<test>",
    )


def test_a_pass_writes_one_evidence_row_per_queued_comment_and_advances(tmp_path):
    store, derived, posts, state = wired(tmp_path)

    summary = run(store, derived, posts, state)

    assert summary["asked"] == summary["written"] == 3
    assert state[loop.INFERENCE] == 102
    assert derived.index(loop.RECORD_TYPE, "@VARUS_channel").count == 3


def test_every_row_the_pass_writes_satisfies_the_evidence_table(tmp_path):
    """Driven through the PASS, not through `evidence.record` — checking the builder against the
    table it also writes would be circular. What has to hold is that the production path produces
    rows the 3.18 (6) sitting could be built from."""
    store, derived, posts, state = wired(tmp_path)
    run(store, derived, posts, state)

    rows = RawStore(tmp_path / "derived").rows(loop.RECORD_TYPE, "@VARUS_channel")
    assert len(rows) == 3
    for row in rows:
        assert evidence.assert_complete(row) is row
        assert row["prompt_sha256"] == prompts.prompt_sha256(TASK)
        # the EXACT rendering, not a description of it: the post and the comment are both in it
        assert "коментар" in row["rendering"][0]["content"]
        assert "<post>" in row["rendering"][0]["content"]


def test_an_interrupted_pass_leaves_the_watermark_and_the_queue_where_they_were(tmp_path):
    """The interruption is between «the model answered» and «the record was written».

    The reply exists — the transport returned it — and the sink refuses. What must not happen is a
    watermark that moved past a row whose record is not on disk: the queue is *defined* as "above
    the watermark", so that row would leave a hole nothing downstream could see.

    Asserted against the cursor ON DISK and not against the in-memory `state`: the guarantee is
    about what survives the process, and a `finally: save_cursor(...)` anywhere in the pass would
    make an in-memory assertion pass while the file told the opposite story.
    """
    cursor_path = tmp_path / "loop_cursor.json"
    loop.save_cursor(cursor_path, {"@VARUS_channel": {loop.INFERENCE: 100}})
    store, derived, posts, _ = wired(tmp_path)
    cursor = loop.load_cursor(cursor_path)
    state = loop.channel_state(cursor, "@VARUS_channel")
    queued_before = loop.queued(store, derived, "@VARUS_channel", state.get(loop.INFERENCE))
    assert [row["msg_id"] for row in queued_before] == [101, 102]

    class RefusesToWrite(RawStore):
        def append(self, records):
            raise OSError("the disk went away between the answer and the write")

    with pytest.raises(OSError, match="between the answer and the write"):
        run(store, RefusesToWrite(tmp_path / "derived"), posts, state, rows=queued_before)

    on_disk = loop.load_cursor(cursor_path)["@VARUS_channel"]
    assert on_disk[loop.INFERENCE] == 100, "the watermark on disk never moved"
    assert [
        row["msg_id"]
        for row in loop.queued(store, derived, "@VARUS_channel", on_disk[loop.INFERENCE])
    ] == [101, 102], "both rows are still queued"


def test_a_rerun_of_the_same_pass_writes_no_new_record_and_leaves_the_watermark(tmp_path):
    """Idempotence asserted on the ARTIFACT: the file's row count and the watermark, not prose."""
    store, derived, posts, state = wired(tmp_path)
    run(store, derived, posts, state)
    first = (tmp_path / "derived" / "inferences" / "VARUS_channel.jsonl").read_bytes()

    again = run(store, RawStore(tmp_path / "derived"), posts, state)

    assert again == {"asked": 0, "written": 0, "watermark": 102, "post_states": {}}
    assert (tmp_path / "derived" / "inferences" / "VARUS_channel.jsonl").read_bytes() == first


def test_the_queue_subtracts_rows_a_killed_pass_already_answered(tmp_path):
    """The crash-resume case the watermark alone cannot see.

    A pass that wrote two records and died before its cursor was saved leaves durable rows and an
    unmoved watermark. Filtering on the watermark alone would re-buy both — which is the same money
    the idempotence rule exists to refuse, just spent by a different route.
    """
    store, derived, posts, _ = wired(tmp_path)
    run(store, derived, posts, {}, rows=loop.queued(store, derived, "@VARUS_channel", None)[:2])

    fresh = RawStore(tmp_path / "derived")
    assert [row["msg_id"] for row in loop.queued(store, fresh, "@VARUS_channel", None)] == [102]


def test_the_pass_records_which_of_the_four_post_states_each_row_was_asked_in(tmp_path):
    """`parents.context` is reached, not reimplemented: a post with text is `post_text`, and a
    caller that assembled the keywords itself could ask half a run with a caption and half without."""
    store, derived, posts, state = wired(tmp_path)
    assert run(store, derived, posts, state)["post_states"] == {"post_text": 3}


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
    monkeypatch.setattr(runner, "SMOKE_DERIVED", tmp_path / "smoke" / "derived")
    # `DERIVED_ROOT` is deliberately NOT patched: nothing reads it (see its docstring — it registers
    # where a SERVED pass will write, and that writer is the paid session's). Patching it would make
    # an unread constant look wired, and `test_a_smoke_leaves_the_real_cursor_and_the_derived_store
    # _untouched` asserts the real thing instead — that no directory appears there at all.
    monkeypatch.setattr(runner, "CAPTIONS", tmp_path / "post_captions.jsonl")
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


# --- the script's inference leg: stub-served, guard closed, cursor untouched ---------------


def wire_infer(monkeypatch, tmp_path):
    texted_store(tmp_path / "raw", posts=(1,), comments=((1, 100), (1, 101), (1, 102)))
    (tmp_path / "loop_cursor.json").write_text(
        '{"@VARUS_channel": {"posts": 1, "inference": 100}}', encoding="utf-8"
    )
    wire(monkeypatch, tmp_path, [SOURCE])


def test_a_served_pass_without_the_smoke_is_refused_by_the_guard(monkeypatch, tmp_path):
    """The DO NOT this contract is likeliest to break. `--infer` alone asks for a SERVED pass, and
    `loop.inference_refusal` is what stands between that and an endpoint nobody registered.

    The MESSAGE is asserted and not just the exit. Left out of the mode list, `--infer` fell through
    to `LIVE_REFUSAL` — still a refusal, still a `SystemExit`, and for a reason that does not apply:
    that one is about appending to the raw v1 stores, which the inference leg never does. A guard
    shadowed by an older one looks exactly like a guard that works.
    """
    wire_infer(monkeypatch, tmp_path)
    with pytest.raises(SystemExit, match="3.11 \\(2\\)"):
        runner.main(["--once", "--infer", "--channel", "@VARUS_channel"])
    assert not (tmp_path / "smoke").exists(), "a refused pass wrote nothing"


def test_a_pass_with_no_mode_at_all_is_still_the_5a_live_refusal(monkeypatch, tmp_path):
    """The control for the test above: the older guard did not move, it only stopped answering for
    a mode that is not its business."""
    wire_infer(monkeypatch, tmp_path)
    with pytest.raises(SystemExit, match="raw v1 stores"):
        runner.main(["--once"])


def test_5c2_prep_b_leaves_the_endpoint_constant_closed():
    """`docs/PROMPT-5c2-prep-b.md` DO NOT: opening this belongs to the paid session's contract. The
    inference leg is built and exercised in this contract and the guard stays shut through all of
    it — `test_the_guard_opens_once_an_endpoint_exists` is the negative control beside this one."""
    assert runner.ENDPOINT is None
    assert loop.inference_refusal(1, runner.ENDPOINT) is not None


def test_the_stub_served_smoke_writes_evidence_rows_and_names_the_stub(monkeypatch, tmp_path):
    wire_infer(monkeypatch, tmp_path)

    assert runner.main(["--once", "--smoke", "--infer", "--channel", "@VARUS_channel"]) == 0

    record = json.loads((tmp_path / "smoke" / "loop_5a.json").read_text(encoding="utf-8"))["runs"][
        -1
    ]
    served = record["smoke_inference"]
    assert served["served_by"] == runner.STUB_SERVED_BY
    assert served["per_channel"] == [
        {
            "channel": "@VARUS_channel",
            "asked": 2,
            "written": 2,
            "watermark": 102,
            "post_states": {"post_text": 2},
        }
    ]
    # the block beside `inference`, never inside it: that one still answers "is an endpoint
    # registered", which is still no, and both statements in the record are true
    assert record["inference"]["endpoint"] is None
    assert "3.11 (2)" in record["inference"]["refusal"]
    rows = RawStore(tmp_path / "smoke" / "derived").rows(loop.RECORD_TYPE, "@VARUS_channel")
    assert [row["msg_id"] for row in rows] == [101, 102]
    assert {row["served_by"] for row in rows} == {runner.STUB_SERVED_BY}
    for row in rows:
        evidence.assert_complete(row)


def test_a_smoke_leaves_the_real_cursor_and_the_derived_store_untouched(monkeypatch, tmp_path):
    """The watermark a smoke advances lives in memory only. If it were saved, the rows a fake
    answered would be marked bought and the next real pass would skip them — for good."""
    wire_infer(monkeypatch, tmp_path)
    before = digests(tmp_path)

    runner.main(["--once", "--smoke", "--infer", "--channel", "@VARUS_channel"])

    after = digests(tmp_path)
    assert after["loop_cursor.json"] == before["loop_cursor.json"]
    assert not (tmp_path / "derived").exists(), "data/derived/ is the real pass's, not a smoke's"
    assert {path for path in after if not path.startswith("smoke/")} == set(before)


def test_the_smoke_answers_at_most_the_limit_it_was_given(monkeypatch, tmp_path):
    wire_infer(monkeypatch, tmp_path)
    runner.main(["--once", "--smoke", "--infer", "--channel", "@VARUS_channel", "--limit", "1"])
    record = json.loads((tmp_path / "smoke" / "loop_5a.json").read_text(encoding="utf-8"))["runs"][
        -1
    ]
    assert record["smoke_inference"]["per_channel"][0]["written"] == 1


def test_a_plan_only_smoke_carries_no_inference_block(monkeypatch, tmp_path):
    """The negative control for the block above: without `--infer` nothing was served, so the
    record must not carry a field a reader could take for served rows."""
    wire_infer(monkeypatch, tmp_path)
    runner.main(["--once", "--smoke", "--channel", "@VARUS_channel"])
    record = json.loads((tmp_path / "smoke" / "loop_5a.json").read_text(encoding="utf-8"))["runs"][
        -1
    ]
    assert "smoke_inference" not in record
