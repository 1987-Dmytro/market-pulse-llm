"""The production loop's skeleton: cursor, plan, ingest, and the guard that refuses (Phase 5a).

Verifier before features (`docs/PROMPT-5a.md`): what a pass **would** do is computed from the
cursor and the store alone, so it can be read before anything is fetched, and the ingest is
idempotent because it is `RawStore.append` — the dedup on ``(channel, msg_id)`` that the
backfill has relied on since Phase 2, not a second one written here.

Three watermarks per channel, and they are different questions:

``posts``
    the newest post id this channel has been walked to. Collection reads it.
``inference``
    the newest comment id that has been handed to the model. Nothing advances it in 5a — no
    serving endpoint exists — so the queue it measures is every stored comment, which is
    exactly the number 5b needs before it can size a serving-parity run.
``leaflet``
    the newest leaflet PAGE id that has been extracted. Its own key rather than a share of
    ``inference``: the two legs read different id spaces (a comment id from the discussion group,
    a page id from the channel's own album) and one is not ahead of the other.
``post_text``
    the newest POST id whose own text has been read by the position instrument (SPEC 3.18 (7)(e)).
    Its own key though it shares an id space with ``posts``, and that is exactly why: ``posts``
    answers "how far has collection walked" and this one answers "how far has extraction read".
    Folded together, one completed extraction pass would tell the collector it had already fetched
    everything up to that id, and the channel would stop collecting.

The file is `data/backfill_cursor.json`'s pattern and `market_pulse.backfill`'s atomic writer:
one file, one dict per channel, written whole after a flush. A kill mid-write must not lose
the position, and a cursor that cannot be parsed restarts the walk rather than the run.
"""

import base64
import hashlib
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path

from market_pulse import evidence, parents, positions, prompts
from market_pulse.backfill import load_cursor, save_cursor  # noqa: F401  (re-exported)

POSTS = "posts"
INFERENCE = "inference"
LEAFLET = "leaflet"
POST_TEXT = "post_text"
"""The four watermark keys. Named rather than spelled out at each call site: a typo in a
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


# --- the inference leg: render, send, WRITE, then move the watermark ---------------------------

COMMENT_TASK = prompts.REVISIONS["v4"]["T1"]
"""Which registered prompt the loop asks a comment with — read out of `prompts.REVISIONS`, not
spelled out. That table is the one place that answers "what instrument is this run using", and the
v4 entry is the rendering the v4 gold was written with (the parent post is in the request, per
`docs/annotation/comments.md` §Unit). A literal here would be a second answer to that question, free
to drift from the gates the loop's numbers will be compared against."""

RECORD_TYPE = "inference"
"""The derived store's record type. `RawStore` keys its files on this and dedupes on
``(channel, msg_id)`` per type, so the evidence rows get the raw store's own idempotence with no
second implementation — and they land in their own root BESIDE `data/raw/`, never inside it."""


def above(rows: Iterable[dict], answered: set, watermark: int | None) -> list[dict]:
    """The rows a pass still owes an answer for, oldest first — the filter BOTH legs share.

    Two filters and they close different holes. The **watermark** is the queue 3.18 prices, and it
    is what a completed pass moves. The **already-answered ids** are what makes a re-run free after
    a pass that was killed: the records it did write are durable and its watermark never moved, so
    the watermark alone would re-buy every one of them. Subtracting what is already written means
    "a re-run buys nothing twice" holds for an INTERRUPTED pass and not only for a completed one.

    ``answered`` is a MESSAGE id set (`StoreIndex.ids`) in both legs, and that is why the fanned-out
    positions leg subtracts correctly: one answered page is one message, whatever number of position
    rows it wrote.
    """
    return sorted(
        (row for row in rows if row["msg_id"] > (watermark or 0) and row["msg_id"] not in answered),
        key=lambda row: row["msg_id"],
    )


def queued(store, derived, handle: str, watermark: int | None) -> list[dict]:
    """The stored comments this pass still owes an answer for, oldest first."""
    return above(store.rows("comment", handle), derived.index(RECORD_TYPE, handle).ids, watermark)


def render_comment(posts: dict, captions: dict, row: dict, task: str = COMMENT_TASK) -> tuple:
    """One comment as the request the model gets, and which of the four post states it is in.

    `parents.context` decides what stands in the post's place and `parents.post_kwargs` translates
    its answer into `build_messages`' keywords — both are reached rather than reimplemented, because
    a run that asked half its rows with a caption and half with `(this post has no text)` because
    two call sites disagreed is precisely what those two functions exist to make impossible.
    """
    found = parents.context(posts, captions, row)
    return prompts.build_messages(task, row["text"], **parents.post_kwargs(found)), found["state"]


def inference_pass(
    rows: list[dict],
    *,
    send,
    posts: dict,
    captions: dict,
    derived,
    state: dict,
    model_revision,
    served_by: str,
    task: str = COMMENT_TASK,
) -> dict:
    """One channel's queued comments through the model. The record is durable BEFORE the watermark.

    The order is the whole point and it is not a preference: append the evidence row, let the write
    close (which flushes it), and only then move the watermark past that id. The other order loses
    rows silently — a watermark that moved past a row whose record was never written leaves a hole
    nothing downstream can see, because the queue is defined as "above the watermark" and the row is
    no longer in it.

    The watermark advances per ROW, in memory. Persisting the cursor is the caller's, once, after
    the pass — and if this raises, the caller must not persist it: an exception here means the row
    being worked on has no record, and every row before it does. `tests/test_loop.py::
    test_an_interrupted_pass_leaves_the_watermark_and_the_queue_where_they_were` drives exactly that.

    ``send`` is the SEAM, and it is the only thing a smoke replaces. Everything that builds the
    record — the rendering, the prompt sha, the evidence table — is the production path in both
    cases, because a stub shares the premises of the code it stands in for and would agree with a
    record shape that is wrong.
    """
    written, states = [], []
    for row in rows:
        rendering, post_state = render_comment(posts, captions, row, task)
        reply = send(task, rendering)
        derived.append(
            [
                evidence.record(
                    "comment",
                    channel=row["channel"],
                    msg_id=row["msg_id"],
                    parent_msg_id=row["parent_msg_id"],
                    task=task,
                    model_revision=model_revision,
                    served_by=served_by,
                    rendering=rendering,
                    reply=reply,
                    record_type=RECORD_TYPE,
                    post_state=post_state,
                )
            ]
        )
        advance(state, INFERENCE, [row["msg_id"]])
        written.append(row["msg_id"])
        states.append(post_state)
    return {
        "asked": len(rows),
        "written": len(written),
        "watermark": state.get(INFERENCE),
        "post_states": {name: states.count(name) for name in sorted(set(states))},
    }


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


# --- the leaflet leg: one page in, one page row and one row per position out --------------------

PAGE_TASK = prompts.POSITIONS_TASK_PAGE
"""The registered page prompt, read out of `prompts` rather than spelled out — same reason as
:data:`COMMENT_TASK`. SPEC 3.17 (4) fixes leaflet extraction at one page per call, and
`prompts.positions_messages_page_gm4` is what refuses a second image."""

PAGE_RECORD_TYPE = "leaflet_page"
POSITION_RECORD_TYPE = "position_row"
"""The derived store's two record types for this leg — the same strings `evidence.KINDS` names, so a
row's `row_kind` and the file it lands in cannot disagree. They are separate files because they are
separate questions: how many pages have been read, and what was on them."""

CARRIER = "leaflet_page"
"""SPEC 3.17 (4): where the record was read. It fixes `price_origin` through
`positions.origin_of`, so a leaflet price cannot be stamped as a consumer quote by a caller that
decided for itself."""

REPO_ROOT = Path(__file__).resolve().parents[2]
"""The checkout this package lives in — `raw_store`, `provenance` and `telegram_client`'s own line.

Here for one job: :func:`page_file`. The RECORD stores `image_path` REPO-RELATIVE (team-lead ruling
on Dv264) and the code that READS the page resolves it at use time, because a stored absolute path
names one machine's checkout and stops being true the moment the tree is cloned, moved or read from
a worktree — while the row it sits in is evidence the 3.18 (6) sitting has to open months later."""


def page_file(page: dict) -> Path:
    """Where this page's bytes are, from the repo-relative path the record carries.

    An absolute ``path`` passes through unchanged — that is pathlib's `/` and not a fallback this
    leg wants: `scripts/run_loop.pages_of` is the only producer of page dicts and
    `tests/test_loop.py::test_pages_of_emits_the_manifests_repo_relative_path` is what holds it to
    emitting relative ones. Nothing here can tell the two apart after the fact.
    """
    return REPO_ROOT / page["path"]


def render_page(path: Path) -> tuple[list[dict], str, list[str]]:
    """One page as (rendering, sha of the bytes SENT, the one-image album the transport takes).

    The file is read **once**, and the sha and the payload are both built from that one `bytes`
    object. Hashing the path separately from encoding it is two reads of a file that can move
    between them, and the record would then name a sha the model never saw.

    The ``rendering`` is what the model is actually given: `positions_messages_page_gm4` — the
    instructions and ONE image slot. The pixels are not in it, they travel beside it, which is why
    `evidence.KIND_FIELDS["leaflet_page"]` is `image_path` and `image_sha256`: those two identify
    the picture exactly and cost the record a few dozen bytes instead of a few megabytes.
    """
    data = path.read_bytes()
    return (
        prompts.positions_messages_page_gm4(1),
        hashlib.sha256(data).hexdigest(),
        # the house encoding (`scripts/caption_posts.data_url`), inlined for the single read above
        ["data:image/jpeg;base64," + base64.b64encode(data).decode("ascii")],
    )


def parse_page(reply: dict, categories, aliases, task: str = PAGE_TASK) -> tuple[list, str | None]:
    """One reply → its positions, or (—, reason). A refusal is a REASON, never an empty answer.

    `[]` and a refusal are different outcomes: an empty array is a page the model says has no dairy
    on it, and a reason is a reply nobody could read. A caller that conflated them would report the
    parse failures as pages with nothing tracked on them.
    """
    try:
        found = positions.parse_positions(
            reply.get("content") or "",
            categories=categories,
            carrier=CARRIER,
            price_origin=positions.origin_of(CARRIER),
            extraction_source=task,
            aliases=aliases,
            family=positions.DEFAULT_FAMILY,
        )
    except positions.SchemaError as err:
        return [], err.reason
    return found, None


def queued_pages(pages: Iterable[dict], derived, handle: str, watermark: int | None) -> list[dict]:
    """The pages this pass still owes an extraction for, oldest first.

    Keyed on the PAGE record type, not the position one: a page whose reply was refused wrote a
    `leaflet_page` row and no positions at all, and asking it again would buy the same refusal.
    """
    return above(pages, derived.index(PAGE_RECORD_TYPE, handle).ids, watermark)


def page_rows(
    page: dict,
    rendering,
    image_sha256: str,
    reply,
    found: list,
    reason: str | None,
    *,
    model_revision,
    served_by: str,
    task: str,
) -> list[dict]:
    """One page's evidence: the positions in the parser's order, and the page row LAST.

    **That order is the second half of "durable before the watermark" and it is not cosmetic.**
    `RawStore.append` writes file by file — one `open("a")` per record type, sequential — and
    :func:`queued_pages` keys the queue on the PAGE record type, so the page row on disk IS this
    page's answered-marker. Written first, a kill between the two file writes would leave a page row
    saying `n_positions: 3` with no position rows behind it, and the re-run would subtract that page
    as answered: the three rows gone for good, and nothing downstream able to see the hole. Written
    last, the same kill leaves position rows and no marker, the page is simply re-asked, and
    `raw_store.dedup_key` skips the rows already there. The marker goes after the thing it marks.

    Both kinds carry `image_path` — REPO-RELATIVE, resolved by :func:`page_file` at read time — and
    `image_sha256`, though only the page kind is required to:
    SPEC 3.18 (6) shows the operator each position beside the picture it was read from, and a
    position row that had to be joined back to its page through a second file is a join that can
    be got wrong at the sitting.

    ``warnings`` is index-aligned per position and lives in two places for two readers. On a
    position row it is that position's own — `evidence.KIND_FIELDS` requires it. On the page row it
    is the whole page's list of lists, ``None`` on a refusal, which is the shape SPEC 3.17 (13)(a)
    is counted in and the shape `scripts/positions_gm4_skub.py` already writes (Dv232).
    """
    common = {
        "channel": page["channel"],
        "msg_id": page["msg_id"],
        "parent_msg_id": page.get("parent_msg_id"),
        "task": task,
        "model_revision": model_revision,
        "served_by": served_by,
        "rendering": rendering,
        "reply": reply,
        "image_path": page["path"],
        "image_sha256": image_sha256,
    }
    rows = [
        evidence.record(
            "position_row",
            **common,
            record_type=POSITION_RECORD_TYPE,
            # the store's finer key: N positions share the page's msg_id, and without this the
            # second and every later one is dropped inside a single append (`raw_store.dedup_key`).
            # Deterministic, so a re-run of the same page recognises its own rows.
            row_id=f"{page['channel']}:{page['msg_id']}:{ordinal}",
            ordinal=ordinal,
            presence=evidence.presence(position),
            tier=position.tier(),
            warnings=list(position.warnings()),
            # The VALUES beside the five booleans. `presence` says a size was named; 3.18 (6) asks
            # the sitting to see «450 г». `depth` and `depth_disagrees_with_printed` are methods on
            # a frozen dataclass and no reader of a JSON row can call them, so they are computed
            # here or they are lost — which is exactly what results/predictions/LOST.md is.
            position=asdict(position)
            | {
                "depth": position.depth(),
                "depth_disagrees_with_printed": position.depth_disagrees_with_printed(),
            },
        )
        for ordinal, position in enumerate(found)
    ]
    # LAST, and see the docstring: this row is the queue's answered-marker, so it must not reach
    # disk before the rows it speaks for.
    rows.append(
        evidence.record(
            "leaflet_page",
            **common,
            record_type=PAGE_RECORD_TYPE,
            n_positions=None if reason else len(found),
            unreadable=reason,
            warnings=None if reason else [list(position.warnings()) for position in found],
        )
    )
    return rows


def page_pass(
    pages: list[dict],
    *,
    send,
    derived,
    state: dict,
    categories,
    aliases,
    model_revision,
    served_by: str,
    task: str = PAGE_TASK,
) -> dict:
    """One channel's queued pages through the model. The record is durable BEFORE the watermark.

    The ordering, the seam and the failure mode are :func:`inference_pass`', deliberately: append
    the page's rows, let the write close, and only then move the watermark past that page. A
    watermark that moved past a page whose rows are not on disk leaves a hole nothing downstream can
    see, because the queue is *defined* as "above the watermark".

    ``send`` takes ``(task, payload)`` exactly as the comment leg's does. The payload differs
    because the instrument does: a comment's payload IS its rendering, while a page travels as the
    one-image album `local_llm.PositionsClient.positions` takes and the rendering is built from the
    registered prompt on the other side of the wire. That is the production pairing, not a
    convenience — see :func:`render_page`.

    A page whose reply cannot be parsed still writes its `leaflet_page` row, carrying the reason and
    `warnings: None`. It is answered, and re-asking it would buy the same refusal.
    """
    written, positions_written, refused = [], 0, 0
    for page in pages:
        rendering, image_sha256, album = render_page(page_file(page))
        reply = send(task, album)
        found, reason = parse_page(reply, categories, aliases, task)
        rows = page_rows(
            page,
            rendering,
            image_sha256,
            reply,
            found,
            reason,
            model_revision=model_revision,
            served_by=served_by,
            task=task,
        )
        derived.append(rows)
        advance(state, LEAFLET, [page["msg_id"]])
        written.append(page["msg_id"])
        positions_written += len(rows) - 1
        refused += 1 if reason else 0
    return {
        "asked": len(pages),
        "pages_written": len(written),
        "positions_written": positions_written,
        # counted, never folded into "pages with no positions": a refusal is excluded from a
        # denominator and an empty page belongs in it
        "unreadable": refused,
        "watermark": state.get(LEAFLET),
    }


# --- the post-text leg: one post's own text in, one row per position out ------------------------

POST_TASK = prompts.POSITIONS_TASK_TEXT
"""The registered TEXT prompt — SPEC 3.18 (2)'s text tier, the leg that passed bar 3 at 0.8667.

One instrument, two input shapes: `positions_gm4_skub.py` sends a page as a one-image album and a
row as a string, through the same `parse` and the same ladder. This leg is the string shape, and
:data:`PAGE_TASK` is the other one — the same reason both are read out of `prompts` rather than
spelled out here."""

POST_CARRIER = "post_text"
POST_PRICE_ORIGIN = "retail_leaflet"
"""SPEC 3.17 (4)'s third carrier, and the one origin SPEC deliberately does NOT fix for it:
`positions.CARRIER_ORIGIN` has no `post_text` row, and `origin_of` raises rather than guess, because
"a retail chain's post and an aggregator's repost are the retailer speaking, and a community
channel's post about prices may not be".

So the caller states it, and this caller INHERITS rather than decides: the paid skub2 session's text
leg already answered `retail_leaflet` for exactly this carrier (`positions_gm4_skub.parse`, the
`else` of its `carrier in CARRIER_ORIGIN` test), and its bar-3 measurement is the number 3.18 (2)
admitted this leg on. A second answer here would mean the rows the pilot scored and the rows the
loop writes are not the same observation. It is named as a constant so the disagreement, if the
operator ever rules one, is a one-line change with a test on it rather than a search."""

POST_POSITION_RECORD_TYPE = "post_position_row"
"""The derived store's file for this leg's positions — its OWN, not shared with the page leg's.

`RawStore.index` keys on the record type, and :func:`above` subtracts the ids it finds there. Page
ids and post ids are both channel message ids: one file would make each leg's queue subtract the
other leg's answers, and the two would silently shrink each other. The `row_kind` on the rows is
still `position_row` — the kind is what the 3.18 (6) sitting reads, the record type is where the
row lives, and they answer different questions."""


def render_post(post: dict) -> tuple[list[dict], str]:
    """One post as (the rendering the model is given, the string the transport takes).

    Both from ONE read of ``post["text"]``, for `render_page`'s reason one layer up: the rendering
    that goes into the evidence row and the payload that goes on the wire must be the same text, or
    the record names a request the model never saw.

    The payload is a bare string and the page leg's is a one-image album — that asymmetry is the
    instrument's, not this module's (`positions_gm4_skub.run_leg`: ``[item["url"]] if "url" in item
    else item["text"]``), and it is why ``send`` takes ``(task, payload)`` and not a rendering.
    """
    return prompts.positions_messages_text_gm4(post["text"]), post["text"]


def parse_post(reply: dict, categories, aliases, task: str = POST_TASK) -> tuple[list, str | None]:
    """One reply → its positions, or (—, reason). :func:`parse_page`'s rule, on the text carrier."""
    try:
        found = positions.parse_positions(
            reply.get("content") or "",
            categories=categories,
            carrier=POST_CARRIER,
            price_origin=POST_PRICE_ORIGIN,
            extraction_source=task,
            aliases=aliases,
            family=positions.DEFAULT_FAMILY,
        )
    except positions.SchemaError as err:
        return [], err.reason
    return found, None


def queued_posts(posts: Iterable[dict], derived, handle: str, watermark: int | None) -> list[dict]:
    """The posts this pass still owes an extraction for, oldest first — **and see the warning**.

    Keyed on this leg's position rows, which is the best key that exists today and is NOT the key
    the sibling legs get. A comment always writes its `comment` row and a page always writes its
    `leaflet_page` row, so "answered" is exact on both. A post writes rows only when the model found
    something: a post that came back `[]` — or whose reply could not be parsed — leaves nothing
    behind, and this function cannot tell it from a post that was never asked.

    The consequence is bounded and is a COST, never a hole: a COMPLETED pass is covered by the
    watermark, so the idempotence smoke is exact. An INTERRUPTED pass whose cursor was never
    persisted re-asks its empty posts, buying the same nothing a second time. That is precisely what
    the `leaflet_page` marker exists to prevent on the sibling leg (:func:`page_rows`), and closing
    it here needs a row kind that has no positions on it — a fourth member of `evidence.KINDS`,
    which is the team lead's fork and not this contract's. Measured rather than argued:
    `tests/test_loop.py::test_an_interrupted_post_pass_re_asks_the_posts_that_yielded_nothing`.
    """
    return above(posts, derived.index(POST_POSITION_RECORD_TYPE, handle).ids, watermark)


def post_rows(
    post: dict,
    rendering,
    reply,
    found: list,
    *,
    model_revision,
    served_by: str,
    task: str,
) -> list[dict]:
    """One post's evidence: a `position_row` per position, in the parser's order.

    No marker row and no `reason` parameter, for the same one reason: there is no kind for "a post
    was read and yielded nothing". A refusal and an empty answer are still different outcomes — the
    pass counts them apart in its summary — but neither reaches the disk, so neither can be read
    back. See :func:`queued_posts`.

    ``parent_msg_id`` is ``None`` and the key is present, which `evidence.REQUIRED` is explicit
    about: a post has no parent, and an absent key and a key holding ``None`` are different states.
    """
    common = {
        "channel": post["channel"],
        "msg_id": post["msg_id"],
        "parent_msg_id": None,
        "task": task,
        "model_revision": model_revision,
        "served_by": served_by,
        "rendering": rendering,
        "reply": reply,
    }
    return [
        evidence.record(
            "position_row",
            **common,
            record_type=POST_POSITION_RECORD_TYPE,
            # the store's finer key, `page_rows`' reason exactly: N positions share one msg_id and
            # `raw_store.dedup_key` would drop all but the first inside a single append
            row_id=f"{post['channel']}:{post['msg_id']}:{ordinal}",
            ordinal=ordinal,
            presence=evidence.presence(position),
            tier=position.tier(),
            warnings=list(position.warnings()),
            position=asdict(position)
            | {
                "depth": position.depth(),
                "depth_disagrees_with_printed": position.depth_disagrees_with_printed(),
            },
        )
        for ordinal, position in enumerate(found)
    ]


def post_pass(
    posts: list[dict],
    *,
    send,
    derived,
    state: dict,
    categories,
    aliases,
    model_revision,
    served_by: str,
    task: str = POST_TASK,
) -> dict:
    """One channel's queued posts through the text instrument. Durable BEFORE the watermark.

    The ordering, the seam and the failure mode are :func:`inference_pass`', deliberately — the same
    sentence :func:`page_pass` carries, and the same code shape under it: write the rows, let the
    write close, and only then move the watermark past that post. A watermark ahead of a row that
    was never written leaves a hole nothing downstream can see.

    ``send`` takes ``(task, payload)`` as both siblings do, and the payload is this instrument's
    string (:func:`render_post`). It is the SEAM and the only thing a smoke replaces.

    The one place this leg is NOT its siblings is what it writes for a post that yields nothing:
    nothing. :func:`queued_posts` carries the consequence and the fork it belongs to.
    """
    written, positions_written, refused, empty = [], 0, 0, 0
    for post in posts:
        rendering, payload = render_post(post)
        reply = send(task, payload)
        found, reason = parse_post(reply, categories, aliases, task)
        rows = post_rows(
            post,
            rendering,
            reply,
            found,
            model_revision=model_revision,
            served_by=served_by,
            task=task,
        )
        if rows:
            derived.append(rows)
        advance(state, POST_TEXT, [post["msg_id"]])
        written.append(post["msg_id"])
        positions_written += len(rows)
        refused += 1 if reason else 0
        empty += 1 if not reason and not found else 0
    return {
        "asked": len(posts),
        "posts_read": len(written),
        "positions_written": positions_written,
        # the two outcomes that write no row, counted apart in the summary because the disk cannot
        # tell them apart afterwards: a refusal is excluded from a denominator, an empty answer is
        # a post the model says has no tracked SKU on it and belongs in one
        "unreadable": refused,
        "empty": empty,
        "watermark": state.get(POST_TEXT),
    }
