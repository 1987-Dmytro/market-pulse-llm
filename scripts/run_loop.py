#!/usr/bin/env python3
"""One pass of the Phase-5 production loop — dry in 5a, on purpose.

`docs/PROMPT-5a.md` deliverable 3 asks for the skeleton and its verifier, not for collection:
the loop's live pass would append to `data/raw/`, and 5a's DO NOT list forbids writing to the
raw v1 stores (derived columns beside them only). So this script computes and prints what a
pass **would** do — from the cursor and the store, without a client — and refuses to run live.
Where the live pass writes is 5c's decision; it is not defaulted here.

Two flags, the house meanings (`scripts/migrate_intents_v4.py`, `scripts/precheck_uplabel.py`):

``--dry-run``
    print the plan and stop. Nothing is written, no client is built. This is the brief's
    literal command, and `tests/test_loop.py` holds it to both halves of that sentence.
``--smoke``
    the same dry pass over one channel, recorded in `results/smoke/loop_5a.json` in the shape
    a real record has. Smoke records are gitignored (`.gitignore`: `results/smoke/`), so the
    numbers are quoted in the task report rather than pointed at.

``--infer``
    5c2-prep-b's half: the queued rows go through the inference leg. With `--smoke` the transport
    is :class:`StubTransport` and the evidence rows land under `results/smoke/derived/`; WITHOUT
    it the pass asks `loop.inference_refusal` for permission and is refused, because no serving
    endpoint is registered and this contract may not register one. **A smoke never saves the
    cursor** — the watermark it advances lives in memory only, so `data/loop_cursor.json` comes
    out byte-identical and the next real pass still owes the rows a stub answered.

``--pages``
    5c2-prep-c1's half: the queued leaflet PAGES go through the extraction leg — one
    `leaflet_page` evidence row per page and one `position_row` per position on it. Same seam,
    same ordering, same guard: with `--smoke` the transport is :class:`StubPageTransport`, and
    without it the pass is refused for the same reason `--infer` is.

``--posts``
    5c2-prep-c3a's half: the posts a channel's own text gets read for, through the SAME instrument
    the leaflet leg uses and the other of its two input shapes (a string, not an album). The queue
    is the posts `positions.prefilter` passes — SPEC 3.18 (7)(e), "FILTERED, never raw" — and the
    guard and the stub are the leaflet leg's, with this leg's own queue depth in the refusal.

    PYTHONPATH=src python3 scripts/run_loop.py --once --dry-run
    PYTHONPATH=src python3 scripts/run_loop.py --once --smoke --channel @VARUS_channel
    PYTHONPATH=src python3 scripts/run_loop.py --once --smoke --infer --channel @VARUS_channel
    PYTHONPATH=src python3 scripts/run_loop.py --once --smoke --pages --channel @atb_market_official
    PYTHONPATH=src python3 scripts/run_loop.py --once --smoke --posts --channel @atb_market_official
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

from market_pulse import loop, parents, positions, yield_screen  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.lexicon import load_lexicon  # noqa: E402
from market_pulse.raw_store import RawStore  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
LEXICON = REPO_ROOT / "config" / "lexicon.yaml"
STORE_ROOT = REPO_ROOT / "data" / "raw"
DERIVED_ROOT = REPO_ROOT / "data" / "derived"
LIVE_DERIVED_ROOT = REPO_ROOT / "data" / "derived_w2"
"""Where evidence rows are written NOW — window 2 and every tick after it.

Ruling 03.09 (b), fork 1: each window writes under its own root, because the C2 run appending
into :data:`DERIVED_ROOT` moved the bytes window 1's seal had hashed. `DERIVED_ROOT` is that
sealed root and is READ from here on, never written; this one is the live one, the same split
`raw_store.ARCHIVE_ROOT` / `raw_store.LIVE_ROOT` made for the raw store on 30.08."""
"""Where a SERVED pass will write its evidence rows — **registered here, written by nothing yet.**

The decision this constant carries is the one 5c2-prep-b was asked to make: derived data lands
BESIDE the raw v1 stores and never inside them, in its own root, which `data/*` already gitignores.
The writer is the paid session's, because a served pass needs an endpoint and this contract may not
register one — so the only code that writes evidence rows today is :func:`smoke_inference`, into
`SMOKE_DERIVED` under `results/smoke/`, which a real pass must never read as already answered.

Deliberately not wired to a caller that cannot exist yet: a constant read by a path that refuses
before reaching it would look tested and be exercised by nothing.

**Its first reader is a guard, not a writer.** `tests/test_loop.py::the_derived_root_is_untouched`
asserts this directory does not exist after a smoke, so a regression that pointed the stub-served
leg at the real root would write into the working tree and be caught. That the constant is read at
all is new in 5c2-prep-c1 (the B1 finding): before it, the assertion named a throwaway path no code
references and could not fire."""

CAPTIONS = REPO_ROOT / "data" / "annotation" / "post_captions.jsonl"
CURSOR = REPO_ROOT / "data" / "loop_cursor.json"
SMOKE = REPO_ROOT / "results" / "smoke" / "loop_5a.json"
SMOKE_DERIVED = REPO_ROOT / "results" / "smoke" / "derived"

POST_MEDIA = REPO_ROOT / "results" / "post_media_5c1.json"
"""Which pictures a channel's posts have on disk, and where — the leaflet leg's page source.

The only file in the repository that maps a (channel, msg_id) to a downloaded page: 5c1's
collection wrote it, and `scripts/caption_gm4_5c1.py` and the sku programme both read pages
through it. Named here rather than re-derived by walking `posts_media/`, because a directory
listing cannot say which post an image belongs to and the parent post is what the 3.18 (6) sitting
shows beside the page.

It covers ONE channel today (`@atb_market_official`, 19 posts / 159 pages). That is a fact about
5c1's collection and not a choice this leg makes: a channel with no entry has no pages queued and
the pass says so rather than failing."""

ENDPOINT = None
"""The serving endpoint the loop would send queued rows to. `None` in 5a — no GPU exists, and
SPEC 3.11 (2) puts a serving-parity measurement in front of the first serving number. This is
the one place 5b changes to open the guard, and `loop.inference_refusal` defaults it closed.

**Still None after 5c2-prep-b, deliberately.** This contract builds the inference leg end to end and
is forbidden from opening the guard: registering an endpoint belongs to the paid session's contract
(`docs/PROMPT-5c2-prep-b.md` DO NOT). The leg is exercised through :class:`StubTransport` instead,
which replaces the TRANSPORT and nothing else — `tests/test_loop.py::test_5a_registers_no_endpoint`
is the assertion that this line has not moved."""

STUB_SERVED_BY = "<stub: scripts/run_loop.py::StubTransport>"
STUB_PAGE_SERVED_BY = "<stub: scripts/run_loop.py::StubPageTransport>"
STUB_POST_SERVED_BY = "<stub: scripts/run_loop.py::StubPostTransport>"
"""What a stub-served evidence row names as its transport.

`market_pulse.evidence.REQUIRED` carries `served_by` for this one reason: a row answered by a fake
and a row answered by a registered endpoint must be distinguishable in the file they land in. The
value is deliberately unusable as an endpoint id — nothing can mistake it for one, and a grep for
``<stub`` finds every row that was never served by a model."""


class StubTransport:
    """The transport a smoke uses, and NOTHING else the pass does.

    It is a stub of the network hop only: the rendering, the prompt sha, the evidence table and the
    record-before-watermark ordering are the production path in a smoke exactly as they are in a
    run. That split is the point — vis-b's paid boot was refused by a guard whose stub had agreed
    with it, because a stub built from the same assumption as the code cannot contradict it.

    The reply shape is `local_llm.LocalClient.batch`'s, per row, so the record a smoke writes has
    the same keys a served record will. Two of the replies are broken on purpose, for the reason
    `positions_gm4_skub.FakeEndpoint` breaks two of its own: an unparseable answer and a refusal are
    different outcomes from an answer nobody could use, and a smoke that only ever succeeds proves
    the record shape on the easy half of the population.
    """

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, task: str, rendering: list[dict]) -> dict:
        self.calls += 1
        broken = self.calls % 5 == 0
        return {
            "content": (
                '{"sentiment": '
                if broken
                else '{"sentiment": "negative", "sarcasm": false, "intents": ["price"]}'
            ),
            "finish_reason": "length" if broken else "stop",
            "cost": 0.0,
            "usage": {"prompt_tokens": 0, "completion_tokens": 0},
            "generation_id": None,
        }


class StubPageTransport:
    """The leaflet leg's stub — the network hop, and nothing else the pass does.

    The schedule is a LIST and not a modulus, which the comment stub can afford and this one
    cannot: the verify gate has to see a triple-warning row and a refusal, and `--limit` decides
    how many pages are ever asked. A modulus plus a small limit can deterministically produce zero
    of a class the gate names, and the smoke would then prove the shape only where it is easy.

    The four outcomes, in the order the first four pages get them:

    1. all three SPEC 3.17 (13)(a) warnings on one position — a multipack size, a «від» price and
       the footnote asterisk. A warning field proven only where it is empty is a field nobody has
       seen work (`positions_gm4_skub.FakeEndpoint`, Dv253).
    2. two positions on one page, so the store's fan-out key is exercised end to end.
    3. truncated mid-object: a REFUSAL, counted by reason and excluded from a denominator.
    4. `[]` — a page the model says has no dairy on it, which belongs IN that denominator.
    """

    ANSWERS = (
        '[{"brand": "Рудь", "category": "ice-cream", "size": "6х100 г", "fat": "12%",'
        ' "price_promo": "від 89,90 грн", "discount_pct_printed": "-31%*"}]',
        '[{"brand": "Рудь", "category": "ice-cream", "size": "450 г", "fat": "12%",'
        ' "price_promo": "89,90 грн", "price_old": "129,90 грн", "discount_pct_printed": "-31%"},'
        ' {"brand": "Яготинське", "category": "ice-cream"}]',
        '[{"brand": "Рудь", ',
        "[]",
    )

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, task: str, album: list[str]) -> dict:
        if len(album) != 1:
            raise ValueError(
                f"{len(album)} images: leaflet extraction is one PAGE per call (SPEC 3.17 (4))"
            )
        content = self.ANSWERS[self.calls % len(self.ANSWERS)]
        self.calls += 1
        return {
            "content": content,
            "finish_reason": "length" if content.endswith(", ") else "stop",
            "cost": 0.0,
            "usage": {"prompt_tokens": 0, "completion_tokens": 0},
            "generation_id": None,
        }


class StubPostTransport(StubPageTransport):
    """The post-text leg's stub — the same four outcomes, arriving as a STRING.

    Subclassed rather than copied: the schedule is the sibling's for the sibling's reason (a
    modulus plus a small `--limit` can deterministically produce zero of a class the gate names),
    and what differs is exactly one thing — the payload shape, which is what this leg's `send`
    contract is about. A stub that accepted either shape would agree with a pass that sent the
    wrong one.
    """

    def __call__(self, task: str, payload) -> dict:
        if not isinstance(payload, str):
            raise ValueError(
                f"{type(payload).__name__}: the text leg sends a row as a string —"
                " `positions_gm4_skub.run_leg` packs an album only for a page"
            )
        content = self.ANSWERS[self.calls % len(self.ANSWERS)]
        self.calls += 1
        return {
            "content": content,
            "finish_reason": "length" if content.endswith(", ") else "stop",
            "cost": 0.0,
            "usage": {"prompt_tokens": 0, "completion_tokens": 0},
            "generation_id": None,
        }


LIVE_REFUSAL = (
    "5a runs the loop dry only. A live pass appends to data/raw/, and docs/PROMPT-5a.md's DO NOT"
    " list forbids writing to the raw v1 stores (derived columns beside them only). The live"
    " pass and the store root it writes to are 5c's, with their own gate. Pass --dry-run to see"
    " what this pass would fetch, or --smoke to record it."
)


def channels_of(registry, only: str | None) -> list[tuple]:
    """The verified channels this pass covers, or the one the operator named."""
    found = [
        (source, handle)
        for source in registry.sources
        if source.verified
        for handle in source.telegram_channels
        if only is None or handle == only
    ]
    if not found:
        raise SystemExit(f"{only}: not a verified channel in {relabel.rel(REGISTRY)}")
    return found


def smoke_inference(channels, store, cursor, limit: int) -> dict:
    """The inference leg, stub-served, over at most ``limit`` queued rows per channel.

    Everything except the transport is the production path, and the evidence rows land in a
    throwaway store under `results/smoke/` (gitignored) rather than in `data/derived/`: a smoke
    must not leave records the next real pass would then read as already answered.
    """
    posts = parents.load(STORE_ROOT / "posts")
    captions = parents.load_captions(CAPTIONS)
    derived = RawStore(SMOKE_DERIVED)
    transport = StubTransport()
    per_channel = []
    for _, handle in channels:
        state = loop.channel_state(cursor, handle)
        rows = loop.queued(store, derived, handle, state.get(loop.INFERENCE))[:limit]
        summary = loop.inference_pass(
            rows,
            send=transport,
            posts=posts,
            captions=captions,
            derived=derived,
            state=state,
            # No endpoint is registered, so nothing can answer "which weights" — and an ABSENT
            # field and a field saying so are different states. The key is carried, holding the
            # only true value there is (`evidence.assert_complete` requires presence, not truth).
            model_revision=None,
            served_by=STUB_SERVED_BY,
        )
        per_channel.append({"channel": handle} | summary)
    return {
        "served_by": STUB_SERVED_BY,
        "why": (
            "the SEAM only. No endpoint is registered (`inference.refusal` above stands and this"
            " contract may not open it), no client is built, no request leaves the machine and"
            " nothing is billed. The rendering, the prompt sha, the evidence table and the"
            " record-before-watermark ordering are the production path in both cases — a stub"
            " shares the premises of the code it stands in for, so it may only replace the"
            " transport. NO NUMBER FROM THESE ROWS MAY REACH AN AGGREGATE."
        ),
        "records": relabel.rel(SMOKE_DERIVED),
        "transport_calls": transport.calls,
        "limit_per_channel": limit,
        "per_channel": per_channel,
    }


def pages_of(manifest: dict, handle: str) -> list[dict]:
    """One channel's leaflet pages, oldest first — the page id, its post, and the file on disk.

    The page's own ``msg_id`` and not the post's: an album is several messages and the sitting
    shows ONE page beside the positions read from it, so the page is the unit the watermark and the
    store key are built on. The post is carried as ``parent_msg_id``, exactly as a comment carries
    the post it hangs under.

    A file the manifest names and disk does not have is skipped rather than sent: the leg would
    hash and encode nothing, and a page that is not there is not a page that failed.

    ``path`` is the manifest's own REPO-RELATIVE string and not the absolute one existence was
    checked with (team-lead ruling on Dv264): it goes into the evidence row verbatim, and a row that
    named `/Users/…/market-pulse-llm/data/…` would be a record about this laptop. `loop.page_file`
    resolves it when the bytes are read.
    """
    out = []
    for entry in manifest["entries"].values():
        if entry["channel"] != handle:
            continue
        for image in entry["images"]:
            if (REPO_ROOT / image["file"]).exists():
                out.append(
                    {
                        "channel": handle,
                        "msg_id": image["msg_id"],
                        "parent_msg_id": entry["msg_id"],
                        "path": image["file"],
                    }
                )
    return sorted(out, key=lambda page: page["msg_id"])


def queued_pages_by_channel(channels, cursor, derived) -> dict:
    """``{handle: the pages that channel still owes an extraction for}``, one answer for two callers.

    The guard COUNTS them and the smoke ANSWERS them, and a second implementation would let the
    refusal report a queue the pass does not have. Which store is passed decides which question is
    asked: `DERIVED_ROOT` for a served pass — read-only, and it does not exist, which is the right
    answer of "nothing has been extracted yet" — and `SMOKE_DERIVED` for a smoke.
    """
    if not POST_MEDIA.exists():
        raise SystemExit(
            f"{relabel.rel(POST_MEDIA)} is not on disk, and it is the only file that maps a page"
            " to the post it belongs to. The leaflet leg has no page source without it."
        )
    manifest = json.loads(POST_MEDIA.read_text(encoding="utf-8"))
    return {
        handle: loop.queued_pages(
            pages_of(manifest, handle),
            derived,
            handle,
            loop.channel_state(cursor, handle).get(loop.LEAFLET),
        )
        for _, handle in channels
    }


def smoke_pages(channels, cursor, registry, limit: int) -> dict:
    """The leaflet leg, stub-served, over at most ``limit`` queued pages per channel.

    Everything except the transport is the production path — the one-page ruling, the sha of the
    bytes sent, `positions.parse_positions`, the ladder, and the rows-then-watermark ordering — and
    the evidence lands in the same throwaway store under `results/smoke/` the comment leg's smoke
    uses. A smoke must not leave records the next real pass would read as already answered.
    """
    derived = RawStore(SMOKE_DERIVED)
    queue = queued_pages_by_channel(channels, cursor, derived)
    transport = StubPageTransport()
    categories = positions.category_keys(registry.taxonomy)
    aliases = watchlist_aliases(registry.watchlist)
    per_channel = []
    for _, handle in channels:
        state = loop.channel_state(cursor, handle)
        pages = queue[handle][:limit]
        summary = loop.page_pass(
            pages,
            send=transport,
            derived=derived,
            state=state,
            categories=categories,
            aliases=aliases,
            # No endpoint is registered, so nothing can answer "which weights" — and an ABSENT
            # field and a field saying so are different states.
            model_revision=None,
            served_by=STUB_PAGE_SERVED_BY,
        )
        per_channel.append({"channel": handle} | summary)
    return {
        "served_by": STUB_PAGE_SERVED_BY,
        "why": (
            "the SEAM only. No endpoint is registered (`inference.refusal` above stands and this"
            " contract may not open it), no client is built, no request leaves the machine and"
            " nothing is billed. The one-page ruling, the sha of the bytes sent, the parser, the"
            " ladder and the rows-before-watermark ordering are the production path in both"
            " cases. NO NUMBER FROM THESE ROWS MAY REACH AN AGGREGATE."
        ),
        "pages": relabel.rel(POST_MEDIA),
        "records": relabel.rel(SMOKE_DERIVED),
        "transport_calls": transport.calls,
        "limit_per_channel": limit,
        "per_channel": per_channel,
    }


def prefilter_instruments(registry) -> tuple[dict, list]:
    """The pre-filter's two compiled halves — the lexicon LAW and the watchlist aliases.

    Compiled shapes, and they are NOT the ones `parse_positions` takes: the filter screens raw text
    with `yield_screen`'s matchers, the parser resolves a brand name the model returned. Both are
    built from the same registry and the same `config/lexicon.yaml` (SPEC 3.17 (8)), which is what
    keeps the frame the census counts and the queue the pass answers the same population.
    """
    lexicon = load_lexicon(LEXICON, taxonomy=registry.taxonomy)
    return (
        yield_screen.compile_categories(lexicon),
        yield_screen.compile_aliases(watchlist_aliases(registry.watchlist)),
    )


def posts_of(store, handle: str, compiled: dict, screen_aliases: list) -> list[dict]:
    """One channel's posts that the relevance PRE-FILTER passes, oldest first.

    SPEC 3.18 (7)(e): "the post leg enters 5c2-run FILTERED, never raw" — through
    `positions.prefilter`, the lexicon-over-post-text instrument, and explicitly not the channel
    entry gate of 3.12, which gates CHANNELS. The raw 9 158-post bound of the prep-c2 projection
    "enters no cap and no session".

    The WINDOW is not applied here and that is deliberate: 3.18 (4) pre-registers the window BY ROW
    COUNT in a census, so the population is the pre-registration's to name and this function's job
    is the filter. A smoke over the whole store is bounded by `--limit` instead.
    """
    return sorted(
        (
            {"channel": handle, "msg_id": row["msg_id"], "text": row["text"]}
            for row in store.rows("post", handle)
            if positions.prefilter(row, compiled, screen_aliases) is not None
        ),
        key=lambda post: post["msg_id"],
    )


def queued_posts_by_channel(channels, store, cursor, derived, registry) -> dict:
    """``{handle: the posts that channel still owes an extraction for}`` — one answer, two callers.

    `queued_pages_by_channel`'s shape and its reason: the guard COUNTS these and the smoke ANSWERS
    them, and a second implementation would let the refusal report a queue the pass does not have.
    """
    compiled, screen_aliases = prefilter_instruments(registry)
    return {
        handle: loop.queued_posts(
            posts_of(store, handle, compiled, screen_aliases),
            derived,
            handle,
            loop.channel_state(cursor, handle).get(loop.POST_TEXT),
        )
        for _, handle in channels
    }


def smoke_posts(channels, store, cursor, registry, limit: int) -> dict:
    """The post-text leg, stub-served, over at most ``limit`` queued posts per channel.

    Everything except the transport is the production path — the pre-filter, the fenced rendering,
    `positions.parse_positions`, the ladder and the rows-then-watermark ordering — and the evidence
    lands in the same throwaway store under `results/smoke/` the other two legs use.
    """
    derived = RawStore(SMOKE_DERIVED)
    queue = queued_posts_by_channel(channels, store, cursor, derived, registry)
    transport = StubPostTransport()
    categories = positions.category_keys(registry.taxonomy)
    aliases = watchlist_aliases(registry.watchlist)
    per_channel = []
    for _, handle in channels:
        state = loop.channel_state(cursor, handle)
        summary = loop.post_pass(
            queue[handle][:limit],
            send=transport,
            derived=derived,
            state=state,
            categories=categories,
            aliases=aliases,
            model_revision=None,
            served_by=STUB_POST_SERVED_BY,
        )
        per_channel.append({"channel": handle} | summary)
    return {
        "served_by": STUB_POST_SERVED_BY,
        "why": (
            "the SEAM only. No endpoint is registered (`inference.refusal` above stands and this"
            " contract may not open it), no client is built, no request leaves the machine and"
            " nothing is billed. The pre-filter, the rendering, the parser, the ladder and the"
            " rows-before-watermark ordering are the production path in both cases."
            " NO NUMBER FROM THESE ROWS MAY REACH AN AGGREGATE."
        ),
        "prefilter": (
            "positions.prefilter over config/lexicon.yaml and the watchlist — SPEC 3.18 (7)(e)."
            " The window of 3.18 (4) is the pre-registration's to apply, not this pass's"
        ),
        "records": relabel.rel(SMOKE_DERIVED),
        "transport_calls": transport.calls,
        "limit_per_channel": limit,
        "per_channel": per_channel,
    }


def smoke_record(
    rows: list[dict],
    refusal: str | None,
    only: str | None,
    served=None,
    pages=None,
    posts=None,
) -> dict:
    return {
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "task": "loop_pass_5a",
        "smoke": True,
        "mode": "dry-run",
        "scope": {
            "registry": relabel.rel(REGISTRY),
            "store_root": relabel.rel(STORE_ROOT),
            "cursor": relabel.rel(CURSOR),
            "cursor_exists": CURSOR.exists(),
            "channel": only,
            "channels_in_pass": len(rows),
        },
        "plan": rows,
        "totals": {
            "threads_to_fetch": sum(row["threads_to_fetch"] for row in rows),
            "rows_to_inference": sum(row["rows_to_inference"] for row in rows),
            # SPEC 3.19 (2): beside the queue and never folded into it. A record that reported only
            # the rows it would buy could not say whether a smaller queue was the skip working or
            # collection failing — and the per-channel number is in `plan` above, row by row.
            "text_less_skipped": sum(row["text_less_skipped"] for row in rows),
        },
        "inference": {"endpoint": ENDPOINT, "refusal": refusal},
        # Beside `inference` and never inside it: that block answers "is an endpoint registered",
        # which is still no, and a served-rows count folded into it would make one record say both
        # "sends none" and "here is what it sent". Absent on a plan-only smoke.
        **({"smoke_inference": served} if served is not None else {}),
        # The leaflet leg gets its own block for the same reason and one more: it counts PAGES and
        # POSITIONS, which are not rows-to-inference, and a reader summing one column across both
        # blocks would be adding comments to SKUs.
        **({"smoke_pages": pages} if pages is not None else {}),
        # and its own block for the third leg, same reason again: it counts POSTS and POSITIONS,
        # and a post that yielded nothing leaves no row at all, so its `empty`/`unreadable` counters
        # are the only record of it — summed into another block they would vanish.
        **({"smoke_posts": posts} if posts is not None else {}),
        "wrote": (
            "nothing — a dry pass builds no client, fetches nothing and leaves the store and the"
            " cursor byte-identical (tests/test_loop.py::test_a_dry_pass_writes_nothing)"
            if served is None and pages is None and posts is None
            else "the plan above, plus stub-served evidence rows under results/smoke/derived/ —"
            " see the `smoke_inference` / `smoke_pages` / `smoke_posts` blocks. The raw v1 stores"
            " and data/derived/ are untouched"
        ),
        "git": git_state(SMOKE),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--once", action="store_true", help="run a single pass (the only mode in 5a)"
    )
    parser.add_argument("--dry-run", action="store_true", help="print the plan and stop")
    parser.add_argument(
        "--smoke", action="store_true", help="the dry pass, recorded in results/smoke/"
    )
    parser.add_argument("--channel", help="restrict the pass to one channel handle")
    parser.add_argument(
        "--infer",
        action="store_true",
        help="run the inference leg (--smoke serves it from a stub; no endpoint exists)",
    )
    parser.add_argument(
        "--pages",
        action="store_true",
        help="run the leaflet leg (--smoke serves it from a stub; no endpoint exists)",
    )
    parser.add_argument(
        "--posts",
        action="store_true",
        help="run the post-text leg over pre-filtered posts (--smoke serves it from a stub)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="most queued rows per channel the stub-served leg answers (default 5)",
    )
    args = parser.parse_args(argv)

    if not args.once:
        parser.error("5a runs one pass at a time: pass --once")
    # `--infer` and `--pages` are MODES here, not options on the other two, and that is what keeps
    # the right guard answering. Left out of this list, `--infer` fell through to LIVE_REFUSAL — a
    # true refusal with the wrong reason, since that one is about appending to the raw v1 stores and
    # neither leg does. Both are refused a few lines down by `inference_refusal`, which is the guard
    # that actually governs them (Dv249, and its repeat is what this line prevents).
    if not (args.dry_run or args.smoke or args.infer or args.pages or args.posts):
        raise SystemExit(LIVE_REFUSAL)

    registry = load_registry(REGISTRY)
    channels = channels_of(registry, args.channel)
    store = RawStore(STORE_ROOT)
    cursor = loop.load_cursor(CURSOR)
    rows = loop.plan(store, channels, cursor)

    print(loop.render_plan(rows))
    queued = sum(row["rows_to_inference"] for row in rows)
    refusal = loop.inference_refusal(queued, ENDPOINT)
    print(
        f"\ninference: {refusal or 'endpoint registered — the pass would send ' + str(queued) + ' rows'}"
    )

    def refuse_a_served_pass(queue: int) -> None:
        """The one place the guard is consulted for real. A leg without `--smoke` asks for a SERVED
        pass, and `inference_refusal` is what stands between that and an endpoint this contract is
        forbidden to register. Both legs go through it — a second copy of the check would be a
        second place to forget one.

        ``queue`` is the asking leg's OWN depth. The comment leg's is `rows_to_inference` and the
        leaflet leg's is its queued pages: a refusal that told a page pass "0 rows are queued" while
        159 pages waited would be a true refusal reporting a number about something else.
        """
        raise SystemExit(
            loop.inference_refusal(queue, ENDPOINT)
            or "an endpoint is registered — a served pass belongs to the paid session's contract"
        )

    served = None
    if args.infer:
        if not args.smoke:
            refuse_a_served_pass(queued)
        served = smoke_inference(channels, store, cursor, args.limit)
        for row in served["per_channel"]:
            print(
                f"  stub-served {row['channel'][:23]:<24} {row['written']:>4} rows written,"
                f" watermark now {row['watermark']}"
            )

    pages = None
    if args.pages:
        if not args.smoke:
            # `RawStore(DERIVED_ROOT)` is READ here and never written: the constructor stores a
            # path and `_read_index` returns an empty index for a root that is not there, which is
            # the true answer — nothing has been extracted yet. The D1 guard stays green.
            queue = queued_pages_by_channel(channels, cursor, RawStore(DERIVED_ROOT))
            refuse_a_served_pass(sum(len(found) for found in queue.values()))
        pages = smoke_pages(channels, cursor, registry, args.limit)
        for row in pages["per_channel"]:
            print(
                f"  stub-served {row['channel'][:23]:<24} {row['pages_written']:>4} pages,"
                f" {row['positions_written']:>4} positions, {row['unreadable']} unreadable,"
                f" watermark now {row['watermark']}"
            )

    posts = None
    if args.posts:
        if not args.smoke:
            # `RawStore(DERIVED_ROOT)` is READ and never written, exactly as the leaflet leg reads
            # it: nothing has been extracted yet, and that is the true answer rather than a guess.
            queue = queued_posts_by_channel(
                channels, store, cursor, RawStore(DERIVED_ROOT), registry
            )
            refuse_a_served_pass(sum(len(found) for found in queue.values()))
        posts = smoke_posts(channels, store, cursor, registry, args.limit)
        for row in posts["per_channel"]:
            print(
                f"  stub-served {row['channel'][:23]:<24} {row['posts_read']:>4} posts,"
                f" {row['positions_written']:>4} positions, {row['unreadable']} unreadable,"
                f" {row['empty']} empty, watermark now {row['watermark']}"
            )

    if args.smoke:
        SMOKE.parent.mkdir(parents=True, exist_ok=True)
        relabel.append_record(
            SMOKE, smoke_record(rows, refusal, args.channel, served, pages, posts)
        )
        print(f"\nwrote {relabel.rel(SMOKE)} (gitignored — quote it, do not point at it)")
    else:
        print("\n--dry-run: nothing fetched, nothing written, no client built")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
