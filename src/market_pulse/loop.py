"""The production loop's skeleton: cursor, plan, ingest, and the guard that refuses (Phase 5a).

Verifier before features (`docs/PROMPT-5a.md`): what a pass **would** do is computed from the
cursor and the store alone, so it can be read before anything is fetched, and the ingest is
idempotent because it is `RawStore.append` — the dedup on ``(channel, msg_id)`` that the
backfill has relied on since Phase 2, not a second one written here.

Two watermarks per channel, and they are different questions:

``posts``
    the newest post id this channel has been walked to. Collection reads it.
``inference``
    the newest comment id that has been handed to the model. Nothing advances it in 5a — no
    serving endpoint exists — so the queue it measures is every stored comment, which is
    exactly the number 5b needs before it can size a serving-parity run.

The file is `data/backfill_cursor.json`'s pattern and `market_pulse.backfill`'s atomic writer:
one file, one dict per channel, written whole after a flush. A kill mid-write must not lose
the position, and a cursor that cannot be parsed restarts the walk rather than the run.
"""

from collections.abc import Iterable

from market_pulse.backfill import load_cursor, save_cursor  # noqa: F401  (re-exported)

POSTS = "posts"
INFERENCE = "inference"
"""The two watermark keys. Named rather than spelled out at each call site: a typo in a
cursor key does not raise, it silently starts the channel over from nothing."""


def channel_state(cursor: dict, handle: str) -> dict:
    """One channel's slot in the cursor, created empty on first sight."""
    return cursor.setdefault(handle, {})


def advance(state: dict, key: str, msg_ids: Iterable[int]) -> int | None:
    """Move a watermark forward over ids that are already stored. Returns the previous value.

    Forward only. A pass that fetched an older page must not drag the watermark back with it —
    the store dedupes, so re-reading costs a request, while a watermark that moved backwards
    costs a re-walk of everything between.
    """
    previous = state.get(key)
    ids = [msg_id for msg_id in msg_ids]
    if ids:
        state[key] = max(previous or 0, max(ids))
    return previous


def rollback(state: dict, key: str, previous: int | None) -> None:
    """Put a watermark back where :func:`advance` found it.

    For the pass that advanced in memory and then failed to store: leaving the advance in
    place would skip the rows it never wrote, and nothing downstream could see the hole.
    """
    if previous is None:
        state.pop(key, None)
    else:
        state[key] = previous


def ingest(store, records: list[dict]) -> dict:
    """Store a batch and say how much of it was new.

    Idempotency is `RawStore.append`'s, not this function's: it skips a record whose
    ``(channel, msg_id)`` it already holds, so a re-run of the same pass stores nothing.
    """
    return {"offered": len(records), "stored": store.append(records)}


def queue_depth(comment_ids: Iterable[int], watermark: int | None) -> int:
    """How many stored comments sit above the inference watermark."""
    return sum(1 for msg_id in comment_ids if msg_id > (watermark or 0))


def plan_channel(store, source, handle: str, state: dict) -> dict:
    """What one pass would fetch for one channel, and what would go to inference.

    Read off the store and the cursor — no client, no request. A dry run that had to talk to
    Telegram to say what it would do could not be the thing that proves the pass is safe.
    """
    posts = store.index("post", handle)
    comments = store.index("comment", handle)
    # `watch` is why this is not `comments_enabled` alone (5c1): a watch channel keeps its
    # discussion group and is deliberately never joined, so its threads are unreadable. Planning
    # them would put rows nobody can fetch into the queue 5c2 prices.
    collects_comments = source.comments_enabled and not source.watch
    threads = posts.with_replies - comments.parents if collects_comments else set()
    return {
        "channel": handle,
        "source_id": source.id,
        "comments_enabled": source.comments_enabled,
        "watch": source.watch,
        "posts_stored": posts.count,
        "comments_stored": comments.count,
        "fetch_posts_newer_than": state.get(POSTS),
        "threads_to_fetch": len(threads),
        "inference_watermark": state.get(INFERENCE),
        "rows_to_inference": queue_depth(comments.ids, state.get(INFERENCE)),
        "damaged_lines": posts.damaged_lines + comments.damaged_lines,
    }


def plan(store, channels: list[tuple], cursor: dict) -> list[dict]:
    """One pass, one row per channel."""
    return [
        plan_channel(store, source, handle, channel_state(cursor, handle))
        for source, handle in channels
    ]


def render_plan(rows: list[dict]) -> str:
    header = (
        f"{'channel':<24}{'posts':>8}{'comments':>10}{'since':>10}"
        f"{'threads':>9}{'to infer':>10}  comments"
    )
    lines = [header, "-" * len(header)]
    for row in rows:
        lines.append(
            f"{row['channel'][:23]:<24}{row['posts_stored']:>8}{row['comments_stored']:>10}"
            f"{(row['fetch_posts_newer_than'] or '—'):>10}{row['threads_to_fetch']:>9}"
            # "watch" rather than "yes": the group is there and is deliberately not joined, and a
            # column that said yes would describe a collection this pass will not do.
            f"{row['rows_to_inference']:>10}  "
            f"{'watch' if row.get('watch') else 'yes' if row['comments_enabled'] else 'no'}"
        )
    lines.append("")
    lines.append(
        f"TOTAL {sum(r['threads_to_fetch'] for r in rows)} comment threads would be fetched, "
        f"{sum(r['rows_to_inference'] for r in rows)} rows would go to inference"
    )
    return "\n".join(lines)


def inference_refusal(rows: int, endpoint: str | None) -> str | None:
    """Why this pass may not send rows to inference, or ``None`` if it may.

    The spend-guard hook point, inert in 5a on purpose: no GPU exists, no serving endpoint is
    registered, and the guard defaults **closed**. 5b fills in the real check here — the same
    shape `scripts/runpod_guard.py` enforces against a cap — and until it does, a loop that
    grew an inference call by accident refuses instead of spending.
    """
    # `not endpoint`, not `is None`: 5b reads this out of env or config, where "unset" arrives
    # as the empty string. A guard that only closes on `None` would open on `TypeError` later,
    # after the pass had already decided it was allowed to spend.
    if not endpoint:
        return (
            f"{rows} rows are queued and no serving endpoint is registered. SPEC 3.11 (2)"
            " pre-registers a serving-parity measurement before any serving number reaches an"
            " aggregate, so 5a queues rows and sends none."
        )
    return None
