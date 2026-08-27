#!/usr/bin/env python3
"""Contract C1 — the retail census: chains, promo aggregators, and Poltava's open chats.

`docs/PROMPT-retail-census.md` over `docs/SPEC-v2-promo-pulse.md` §3. Read-only against
Telegram throughout: resolve, one full-channel request, one 28-day history request per
candidate, the pause `entry_check.py` already keeps. **No joins** — joining is the one action
that writes on Telegram's side, `collect_5c1.JOIN_PAUSE` prices it at fifteen minutes each, and
the Rules line of the brief says read-only. A public supergroup's history reads without one
(probed 2026-08-27 on `@TomkaPoltav`: `left=True`, five messages returned), so `messages_open`
is measured rather than bought.

Two stages, because the population is not knowable in advance:

* ``--search`` sends the 236 queries of the two themes and writes every row Telegram returned,
  with the fields the search response gives away for free — title, username, subscribers,
  broadcast/megagroup, blue check. Costs no `ResolveUsername`, which is what an account-wide
  FloodWait sits on (this account has seen one of 55 779 s).
* the default pass entry-checks the rows above ``--min-subscribers`` one at a time, writing the
  record after **every** candidate. A row below the bar keeps its free fields and says
  ``checked: false`` with the reason: silent truncation reads as "we looked at everything", and
  a logged filter is something the operator can raise or lower.

Already-registered channels are not re-measured over the API at all — the brief says their row
comes from the store, so `data/raw/` and `results/entry_gate_5c1.json` supply it and 66 handles
of resolve pressure never happen.

    PYTHONPATH=src python3 scripts/retail_census.py --plan
    PYTHONPATH=src python3 scripts/retail_census.py --search
    PYTHONPATH=src python3 scripts/retail_census.py --min-subscribers 300
    PYTHONPATH=src python3 scripts/retail_census.py --report
"""

import argparse
import asyncio
import json
import re
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import discover_channels as discovery  # noqa: E402
import entry_check as entry  # noqa: E402
import registry_revision_proposal as store_side  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from telethon import functions  # noqa: E402
from telethon.errors import FloodWaitError  # noqa: E402

from market_pulse.entry_check import build_verdict, collapse_albums, traffic_stats  # noqa: E402
from market_pulse.langid import detect  # noqa: E402
from market_pulse.lexicon import load_lexicon  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402
from market_pulse.telegram_client import build_client  # noqa: E402
from market_pulse.yield_screen import category_hits, compile_categories  # noqa: E402

RECORD = REPO_ROOT / "results" / "retail_census.json"
REPORT = REPO_ROOT / "docs" / "reports" / "retail-census.md"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
GATE_RECORD = REPO_ROOT / "results" / "entry_gate_5c1.json"

THEMES = ("retail_chains", "poltava_chats")
WINDOW_DAYS = 28
WINDOW_LIMIT = 1200
"""The brief's "last 4 weeks", and the request cap that bounds one candidate's history scan.
A candidate that fills the cap inside the window is `window_truncated` — its rates are floors."""

MIN_SUBSCRIBERS = 300
"""The default entry-check bar, set on the search population and not before it (see the record's
`bound` block for the distribution it was read off). It is a BUDGET, not a judgement: every row
below it is in the record with its free fields, and `--min-subscribers 0` checks the lot."""

CONTRACT_PRICE = re.compile(r"grn|₴|\d+[,.]\d\d", re.IGNORECASE)
"""The price marker exactly as `docs/PROMPT-retail-census.md` writes it."""

PRICE_BRANCHES = {
    "грн": re.compile(r"грн", re.IGNORECASE),
    "₴": re.compile(r"₴"),
    "grn": re.compile(r"\bgrn\b", re.IGNORECASE),
    "decimal": re.compile(r"\d+[,.]\d\d"),
}
"""The census pattern, one branch at a time so the column can be audited.

The brief's literal `grn` is Latin and Ukrainian retail writes «грн»: as written the first branch
matches almost nothing in this corpus, which is a unit error rather than a strict reading
([[a_literal_below_the_minimum_is_a_unit_error]]). Both shares are reported, so the deviation is
a number and not an assertion. `decimal` fires on «27.08» as well as on «49,90» — the per-branch
counts are the only way to see which branch is carrying the column."""

CENSUS_VERDICTS = ("enter", "posts-only", "reject")
"""The brief's three, mapped off `market_pulse.entry_check.build_verdict`'s own vocabulary so
the reasons are the entry check's words and not a second grading scheme:
`usable → enter`, `posts-only → posts-only`, `rejected|unresolved → reject`."""


# --- the one history request, and everything read off it ---------------------------------------


async def census_sample(client, entity, now: datetime) -> tuple[list[dict], bool]:
    """The last WINDOW_DAYS of messages, as the rows every census column is computed from.

    One request per candidate, which is the brief's own instrument. Album items arrive as
    separate messages and only one of them carries the reply counter and the text, so the rows
    keep `grouped_id` and are collapsed downstream rather than counted as they land.
    """
    cutoff = now - timedelta(days=WINDOW_DAYS)
    rows = []
    # wait_time is the collector's own pacing between history pages (scripts/backfill.py).
    async for message in client.iter_messages(entity, limit=WINDOW_LIMIT, wait_time=1.0):
        if message.date < cutoff:
            return rows, False
        rows.append(
            {
                "date": message.date.isoformat(),
                "grouped_id": message.grouped_id,
                "is_service": message.action is not None,
                "replies": message.replies.replies if message.replies else None,
                "has_media": message.media is not None,
                "text": message.raw_text or "",
            }
        )
    return rows, len(rows) >= WINDOW_LIMIT


def price_hits(text: str) -> dict:
    return {name: bool(pattern.search(text)) for name, pattern in PRICE_BRANCHES.items()}


def census_stats(rows: list[dict], *, truncated: bool, is_group: bool, compiled: dict) -> dict:
    """Every column the brief asks for, off the one sample. Shares, so rows compare.

    An album is one authored message in a channel and in a barahol'ka alike — five photos of one
    lot is one thing said — so both sides collapse. What differs is the name: a broadcast channel
    has posts and comments under them, a group has messages and nobody comments on a comment.
    """
    live = [row for row in rows if not row["is_service"]]
    # (date, replies, grouped_id, is_service) — the shape entry_check.collapse_albums reduces.
    samples = [
        (
            datetime.fromisoformat(row["date"]),
            row["replies"],
            row["grouped_id"],
            row["is_service"],
        )
        for row in rows
    ]
    posts = collapse_albums(samples)
    n_posts = len(posts)

    # An album's text and media ride on one item; keyed by grouped_id so the collapsed post is
    # judged on everything it carried, not on whichever item happened to come first.
    merged: dict = {}
    for row in live:
        key = row["grouped_id"] or ("solo", row["date"], id(row))
        cell = merged.setdefault(key, {"text": "", "has_media": False})
        cell["text"] = (cell["text"] + "\n" + row["text"]).strip()
        cell["has_media"] = cell["has_media"] or row["has_media"]

    units = list(merged.values())
    texts = [unit["text"] for unit in units if unit["text"].strip()]
    branch_counts = {name: 0 for name in PRICE_BRANCHES}
    n_price = n_contract_price = n_media = n_dairy = 0
    for unit in units:
        hits = price_hits(unit["text"])
        for name, fired in hits.items():
            branch_counts[name] += fired
        n_price += any(hits.values())
        n_contract_price += bool(CONTRACT_PRICE.search(unit["text"]))
        n_media += unit["has_media"]
        n_dairy += bool(category_hits(unit["text"], compiled))

    mix: dict[str, int] = {}
    for text in texts:
        lang = detect(text)
        mix[lang] = mix.get(lang, 0) + 1

    def share(count: int) -> float | None:
        return round(count / len(units), 3) if units else None

    dates = sorted(date for date, _ in posts)
    replies = [count for _, count in posts if count is not None]
    return {
        "window_days": WINDOW_DAYS,
        "window_truncated": truncated,
        "n_messages_raw": len(rows),
        "n_posts": n_posts,
        "posts_per_day": round(n_posts / WINDOW_DAYS, 3),
        "messages_per_day": round(n_posts / WINDOW_DAYS, 3) if is_group else None,
        "last_post": dates[-1].isoformat() if dates else None,
        "n_texts": len(texts),
        # A group has no reply counters on its messages: nobody comments on a comment. `None`
        # rather than 0.0 — the two are a different finding ([[empty_field_hides_several_states]]).
        "comments_per_day": None if is_group else round(sum(replies) / WINDOW_DAYS, 3),
        "n_posts_with_comments": None if is_group else sum(1 for c in replies if c > 0),
        "price_share": share(n_price),
        "price_share_contract_regex": share(n_contract_price),
        "price_branch_hits": branch_counts,
        "media_share": share(n_media),
        "leaflet_or_price_share": share(
            sum(1 for u in units if u["has_media"] or any(price_hits(u["text"]).values()))
        ),
        "dairy_share": share(n_dairy),
        "dairy_posts_per_day": round(n_dairy / WINDOW_DAYS, 3),
        "language_mix": {lang: round(n / len(texts), 2) for lang, n in sorted(mix.items())}
        if texts
        else {},
        "traffic": traffic_stats(posts),
    }


def census_verdict(record: dict, stats: dict, *, is_group: bool, messages_open: bool) -> dict:
    """`enter | posts-only | reject`, off the entry check's own verdict and reasons.

    A group is graded on the brief's rule and not on `comments_enabled`: a chat IS the
    conversation, so "no linked discussion group" — true of every group — would post-only the
    whole theme. What decides it there is whether the history reads at all, and whether anybody
    is talking in it.
    """
    if not record.get("resolved"):
        return {
            "verdict": "reject",
            "reasons": record.get("reasons") or ["handle does not resolve"],
        }
    if record.get("scam") or record.get("fake"):
        flag = "scam" if record.get("scam") else "fake"
        return {"verdict": "reject", "reasons": [f"Telegram flags this channel as {flag}"]}
    if is_group:
        reasons = []
        if not messages_open:
            return {"verdict": "reject", "reasons": ["history is not readable without joining"]}
        if not stats["n_posts"]:
            return {"verdict": "reject", "reasons": ["no messages in the sampled window"]}
        if not record.get("telegram_verified"):
            reasons.append("no blue check — confirm this is the official channel")
        return {"verdict": "enter", "reasons": reasons}
    mapping = {"usable": "enter", "posts-only": "posts-only"}
    graded = build_verdict(
        resolved=True,
        telegram_verified=bool(record.get("telegram_verified")),
        scam=False,
        fake=False,
        comments_enabled=bool(record.get("comments_enabled")),
        stats=stats["traffic"],
        broadcast=bool(record.get("broadcast")),
    )
    return {"verdict": mapping.get(graded["verdict"], "reject"), "reasons": graded["reasons"]}


# --- stage 1: the searches, and the free metadata they hand back --------------------------------


async def search_population(
    client, themes: dict[str, tuple]
) -> tuple[dict, list[dict], int | None]:
    """Every row the two themes' queries returned, deduped by handle, with who found it.

    `contacts.SearchRequest` already carries subscribers, blue check and broadcast/megagroup for
    each hit — no resolve needed, and those are exactly the fields the entry-check bound reads.
    """
    found: dict[str, dict] = {}
    queries_run = []
    for theme, queries in themes.items():
        for query in queries:
            print(f"searching {theme}: {query!r}", flush=True)
            try:
                result = await client(
                    functions.contacts.SearchRequest(q=query, limit=entry.DISCOVER_LIMIT)
                )
            except FloodWaitError as exc:
                print(f"FloodWait during search: {exc.seconds}s — stopped at {query!r}", flush=True)
                return found, queries_run, exc.seconds
            queries_run.append({"theme": theme, "query": query, "hits": len(result.chats)})
            for chat in result.chats:
                username = getattr(chat, "username", None)
                if not username:
                    continue  # private or invite-only: not collectable
                handle = f"@{username}"
                entry_row = found.setdefault(
                    handle.lower(),
                    {
                        "handle": handle,
                        "found_by": [],
                        "search": {
                            "title": getattr(chat, "title", None),
                            "subscribers": getattr(chat, "participants_count", None),
                            "telegram_verified": bool(getattr(chat, "verified", False)),
                            "broadcast": bool(getattr(chat, "broadcast", False)),
                            "megagroup": bool(getattr(chat, "megagroup", False)),
                            "scam": bool(getattr(chat, "scam", False)),
                            "fake": bool(getattr(chat, "fake", False)),
                        },
                    },
                )
                entry_row["found_by"].append(f"{theme}:{query}")
            await asyncio.sleep(entry.PAUSE_SECONDS)
    return found, queries_run, None


# --- stage 2: one candidate at a time, checkpointed --------------------------------------------


def to_check(rows: list[dict], minimum: int, limit: int | None) -> list[dict]:
    """The rows this pass talks to. Everything else keeps its free fields and says why not."""
    pending = [
        row
        for row in rows
        if not row.get("checked")
        and (row["search"]["subscribers"] or 0) >= minimum
        and not row.get("skipped_because")
    ]
    pending.sort(key=lambda row: -(row["search"]["subscribers"] or 0))
    return pending[:limit] if limit else pending


async def check_one(client, row: dict, now: datetime, compiled: dict) -> dict:
    """Resolve + full channel + ONE history request, for one candidate."""
    handle = row["handle"]
    source = entry.Source("census", row["search"]["title"] or handle, "community", (handle,))
    record = await entry.check_channel(client, source, handle)
    is_group = bool(record.get("megagroup"))
    messages_open, sample, truncated, error = True, [], False, None
    if record.get("resolved"):
        try:
            sample, truncated = await census_sample(client, handle, now)
        except FloodWaitError:
            raise
        except Exception as exc:  # a group that refuses its history is a finding, not a crash
            messages_open, error = False, f"{type(exc).__name__}: {exc}"
    else:
        messages_open = False
    stats = census_stats(sample, truncated=truncated, is_group=is_group, compiled=compiled)
    verdict = census_verdict(record, stats, is_group=is_group, messages_open=messages_open)
    return {
        **row,
        "checked": True,
        "checked_at": entry.stamp(),
        "measured_by": "api",
        "window": f"{(now - timedelta(days=WINDOW_DAYS)).date()}..{now.date()}",
        "resolved": bool(record.get("resolved")),
        "title": record.get("title"),
        "subscribers": record.get("subscribers"),
        "telegram_verified": bool(record.get("telegram_verified")),
        "broadcast": bool(record.get("broadcast")),
        "megagroup": is_group,
        "is_group": is_group,
        "messages_open": messages_open,
        "messages_open_error": error,
        "comments_enabled": bool(record.get("comments_enabled")),
        "discussion_group": record.get("discussion_group"),
        "stats": stats,
        "verdict": verdict["verdict"],
        "reasons": verdict["reasons"],
        "capability_verdict": record.get("verdict"),
        "error": record.get("error"),
    }


# --- the registry's own channels: from the store, never over the API ---------------------------


def gate_facts() -> dict:
    """Subscribers, blue check and linked group as `results/entry_gate_5c1.json` measured them."""
    if not GATE_RECORD.exists():
        return {}
    rows = json.loads(GATE_RECORD.read_text(encoding="utf-8")).get("candidates", [])
    return {row["handle"].lower(): row.get("checks", {}) for row in rows}


def registry_rows(compiled: dict, today: date) -> list[dict]:
    """One row per registered channel, measured on the store — the brief's own instruction.

    The store's window is 28 days back from that channel's own collection date, so the length
    matches the API rows and only the end date differs. Every row says which instrument read it
    and over which window: the census table sorts both together, and a reader who cannot see the
    two instruments reads the ordering as a finding ([[two_instruments_two_inputs]]).
    """
    gate = gate_facts()
    rows = []
    for source in load_registry(REGISTRY).sources:
        for handle in source.telegram_channels:
            stem = handle.lstrip("@")
            posts = store_side.store_rows("posts", stem)
            window = store_side.window_of(posts)
            in_win = store_side.in_window(posts, window) if window else []
            comments = store_side.store_rows("comments", stem)
            n_comments = len(store_side.in_window(comments, window)) if window and comments else 0
            checks = gate.get(handle.lower(), {})
            sample = [
                {
                    "date": row["date"],
                    "grouped_id": row.get("grouped_id"),
                    "is_service": False,
                    "replies": row.get("reply_count"),
                    "has_media": bool(row.get("has_media")),
                    "text": row.get("text") or "",
                }
                for row in in_win
            ]
            stats = census_stats(sample, truncated=False, is_group=False, compiled=compiled)
            # The store knows how many comments were COLLECTED; the reply counters in it are the
            # same field the API rows use, so the rate is not re-derived from a second model.
            stats["comments_per_day"] = (
                round(n_comments / store_side.WINDOW_DAYS, 3) if comments else None
            )
            stats["comments_cause"] = store_side.comment_rate(
                source, handle, stem, window, store_side.joined_groups()
            )[1]
            rows.append(
                {
                    "handle": handle,
                    "in_registry": True,
                    "source_id": source.id,
                    "bucket": store_side.bucket(source),
                    "checked": True,
                    "measured_by": "store",
                    "window": f"{window[0]}..{window[1]}" if window else None,
                    "found_by": ["registry"],
                    "search": {
                        "title": source.name,
                        "subscribers": checks.get("subscribers"),
                        "telegram_verified": bool(checks.get("telegram_verified")),
                        "broadcast": bool(checks.get("broadcast", True)),
                        "megagroup": bool(checks.get("megagroup")),
                        "scam": False,
                        "fake": False,
                    },
                    "title": source.name,
                    "subscribers": checks.get("subscribers"),
                    "telegram_verified": bool(checks.get("telegram_verified")),
                    "broadcast": bool(checks.get("broadcast", True)),
                    "megagroup": bool(checks.get("megagroup")),
                    "is_group": bool(checks.get("megagroup")),
                    "messages_open": None,
                    "comments_enabled": source.comments_enabled,
                    "discussion_group": checks.get("discussion_group"),
                    "resolved": True,
                    "stats": stats,
                    "verdict": None,
                    "reasons": ["in_registry — measured on the store, not graded by this census"],
                    "days_stale": (today - date.fromisoformat(stats["last_post"][:10])).days
                    if stats["last_post"]
                    else None,
                }
            )
    return rows


# --- the record --------------------------------------------------------------------------------


def sort_key(row: dict) -> tuple:
    """`dairy posts/day × (1 + comments/day)` — the brief's ordering.

    `dairy posts/day` is not a measured column: it is posts/day × dairy share, and it is written
    into every row so the product can be checked. The tie at zero is most of the table, so the
    secondary keys are named rather than left to dict order
    ([[the_argmax_and_the_max_are_two_rows]]).
    """
    stats = row["stats"]
    dairy = stats["dairy_posts_per_day"]
    comments = stats["comments_per_day"] or 0.0
    return (
        -(dairy * (1 + comments)),
        -(stats["posts_per_day"] or 0),
        -(row.get("subscribers") or 0),
        row["handle"].lower(),
    )


def build_record(state: dict) -> dict:
    rows = state["rows"]
    checked = [row for row in rows if row.get("checked")]
    return {
        **state,
        "generated_at": entry.stamp(),
        "contract": "docs/PROMPT-retail-census.md (C1) over docs/SPEC-v2-promo-pulse.md §3",
        "authorised": "operator ruling (x), 2026-08-27 — SPEC v2 §3",
        "read_only": (
            "no joins, no member lists, no store writes, no registry edit. A public supergroup's"
            " history reads without membership (probed 2026-08-27 on @TomkaPoltav: left=True,"
            " five messages returned), so messages_open is measured, not bought."
        ),
        "themes": {theme: list(discovery.THEMES[theme]) for theme in THEMES},
        "window_days": WINDOW_DAYS,
        "window_limit": WINDOW_LIMIT,
        "post_sample": entry.POST_SAMPLE,
        "price_patterns": {
            "contract_as_written": CONTRACT_PRICE.pattern,
            "census_branches": {name: p.pattern for name, p in PRICE_BRANCHES.items()},
            "why": (
                "the brief's literal `grn` is Latin and this corpus writes «грн»; both shares are"
                " in every row so the deviation is a number, not an assertion"
            ),
        },
        "lexicon": {
            "path": "config/lexicon.yaml",
            "groups": ["dairy", "ice-cream"],
            "matcher": "market_pulse.yield_screen.compile_categories — the lexicon's own rule",
        },
        "verdicts": list(CENSUS_VERDICTS),
        "verdict_mapping": (
            "market_pulse.entry_check.build_verdict: usable→enter, posts-only→posts-only,"
            " rejected|unresolved→reject. A group is graded on the brief's own rule instead"
            " (history readable + somebody talking), because `comments_enabled` is false for"
            " every chat and would posts-only the whole theme."
        ),
        "counts": {
            "candidates_found": len([r for r in rows if not r.get("in_registry")]),
            "checked": len([r for r in checked if not r.get("in_registry")]),
            "unchecked": len([r for r in rows if not r.get("checked")]),
            "in_registry": len([r for r in rows if r.get("in_registry")]),
        },
        "rows": sorted(rows, key=sort_key),
        "git": git_state(RECORD),
    }


def save(state: dict) -> None:
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(
        json.dumps(build_record(state), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_state() -> dict:
    if not RECORD.exists():
        raise SystemExit(f"{RECORD} is missing — run --search first")
    held = json.loads(RECORD.read_text(encoding="utf-8"))
    return {
        "rows": held["rows"],
        "queries": held.get("queries", []),
        "flood_wait_events": held.get("flood_wait_events", []),
        "searched_at": held.get("searched_at"),
        "bound": held.get("bound"),
        "step_0": held.get("step_0"),
    }


# --- entry points -------------------------------------------------------------------------------


def held_step_0() -> dict | None:
    """Whatever a previous pass already recorded about step 0 — a re-search must not un-say it."""
    if not RECORD.exists():
        return None
    return json.loads(RECORD.read_text(encoding="utf-8")).get("step_0")


def record_step_0(before: Path, delete: Path, after: Path, guard: dict) -> int:
    """Put the volume deletion's own evidence into the record, verbatim.

    The brief wants both `runpodctl network-volume list` listings in the report word for word.
    A report is a rendering, so the bytes belong in the file the rendering reads: kept only in a
    session's scrollback they are unreproducible, and the report would be quoting nothing
    ([[gate_verdicts_need_an_artifact]]).
    """
    state = load_state()
    state["step_0"] = {
        "deleted": "mp-lora-c (soymlju8q0, 100 GB, CA-MTL-3)",
        "kept": "mp-srv2 (qw4nwleanc, 100 GB, EU-RO-1) — the positive control, in both listings",
        "authorised": "SPEC v2 §9 / operator ruling (x): the merge is off stage 1's path",
        "weights_checked": (
            "scripts/runbook_think_zero_shot_d2.md mounts qw4nwleanc and reads /workspace/hf, so"
            " «the weights are on mp-srv2» is verified against a runbook, not taken from prose"
        ),
        "cost_of_the_deletion": (
            "mp-lora-c held a SECOND copy of the pinned base weights (rev 842da379…,"
            " docs/reports/lora-c-migrate-r2.md) for a line closed by stop-rule (ruling (u));"
            " re-creating it is the 62.58 GB download the measurement registry prices at 184 s"
        ),
        "before": before.read_text(encoding="utf-8"),
        "delete": delete.read_text(encoding="utf-8"),
        "after": after.read_text(encoding="utf-8"),
        **guard,
    }
    save(state)
    print(f"step 0 evidence written into {RECORD.relative_to(REPO_ROOT)}")
    return 0


async def run_search() -> int:
    themes = {theme: discovery.THEMES[theme] for theme in THEMES}
    client = build_client()
    await client.connect()
    try:
        if not await client.is_user_authorized():
            raise SystemExit("No Telegram session. Run: python3 scripts/tg_login.py")
        found, queries, flood = await search_population(client, themes)
    finally:
        await client.disconnect()

    registered = {
        handle.lower()
        for source in load_registry(REGISTRY).sources
        for handle in source.telegram_channels
    }
    rows = [row for key, row in found.items() if key not in registered]
    for row in rows:
        row["checked"] = False
    state = {
        "rows": rows,
        "queries": queries,
        "searched_at": entry.stamp(),
        "flood_wait_events": (
            [{"stage": "search", "seconds": flood, "at": entry.stamp()}] if flood else []
        ),
        "bound": None,
        "step_0": held_step_0(),
    }
    save(state)
    print(f"\n{len(queries)} queries sent, {len(rows)} unregistered handles found")
    print(f"wrote {RECORD.relative_to(REPO_ROOT)}")
    return 1 if flood else 0


async def run_checks(minimum: int, limit: int | None) -> int:
    state = load_state()
    compiled = compile_categories(load_lexicon())
    pending = to_check(state["rows"], minimum, limit)
    below = [
        row
        for row in state["rows"]
        if not row.get("checked") and (row["search"]["subscribers"] or 0) < minimum
    ]
    for row in below:
        row["skipped_because"] = f"subscribers < {minimum} (search response, no resolve spent)"
    state["bound"] = {
        "min_subscribers": minimum,
        "skipped_below_the_bar": len(below),
        "why": (
            "every ResolveUsername is what an account-wide FloodWait sits on, and this account"
            " has seen one of 55 779 s. The skipped rows keep their search-response fields and"
            " say so — a logged filter the operator can lower, not a silent truncation."
        ),
    }
    print(f"{len(pending)} to check at >= {minimum} subscribers; {len(below)} below the bar")
    if not pending:
        save(state)
        return 0

    now = datetime.now(UTC)
    client = build_client()
    await client.connect()
    flood = None
    try:
        if not await client.is_user_authorized():
            raise SystemExit("No Telegram session. Run: python3 scripts/tg_login.py")
        by_handle = {row["handle"]: i for i, row in enumerate(state["rows"])}
        for n, row in enumerate(pending, 1):
            print(
                f"[{n}/{len(pending)}] {row['handle']} ({row['search']['subscribers']})...",
                flush=True,
            )
            try:
                done = await check_one(client, row, now, compiled)
            except FloodWaitError as exc:
                # Before the generic handler: swallowed there, a rate-limited candidate is
                # written down as a verdict, which is a permanent judgement on a temporary state.
                flood = exc.seconds
                print(f"FloodWait: Telegram asks for {exc.seconds}s — stopped, keeping {n - 1}.")
                break
            except Exception as exc:
                done = {
                    **row,
                    "checked": True,
                    "checked_at": entry.stamp(),
                    "measured_by": "api",
                    "resolved": False,
                    "stats": census_stats([], truncated=False, is_group=False, compiled=compiled),
                    "verdict": "reject",
                    "reasons": ["unexpected failure, see error"],
                    "error": f"{type(exc).__name__}: {exc}",
                }
            state["rows"][by_handle[row["handle"]]] = done
            save(state)  # after EVERY candidate: a kill mid-scan must not zero the pass
            await asyncio.sleep(entry.PAUSE_SECONDS)
    finally:
        await client.disconnect()
    if flood:
        state["flood_wait_events"].append({"stage": "check", "seconds": flood, "at": entry.stamp()})
    save(state)
    print(f"wrote {RECORD.relative_to(REPO_ROOT)}")
    return 1 if flood else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="C1 retail census — chains and Poltava chats.")
    parser.add_argument("--plan", action="store_true", help="print the queries and stop, no API")
    parser.add_argument("--search", action="store_true", help="stage 1: the queries, no resolves")
    parser.add_argument("--report", action="store_true", help="render the report from the record")
    parser.add_argument("--min-subscribers", type=int, default=MIN_SUBSCRIBERS)
    parser.add_argument("--max-checks", type=int, help="cap the candidates checked this pass")
    parser.add_argument(
        "--registry-rows", action="store_true", help="add the store-measured registry rows"
    )
    parser.add_argument(
        "--step0",
        nargs=3,
        metavar=("BEFORE", "DELETE", "AFTER"),
        help="record the volume listings verbatim from these three captured files",
    )
    args = parser.parse_args(argv)

    if args.plan:
        for theme in THEMES:
            queries = discovery.THEMES[theme]
            print(f"{theme}: {len(queries)} queries")
            print("  " + " · ".join(queries))
        return 0
    if args.search:
        return asyncio.run(run_search())
    if args.step0:
        ledger = json.loads(
            (REPO_ROOT / "results" / "spend_cycle2.json").read_text(encoding="utf-8")
        )["sessions"][-1]
        return record_step_0(
            *(Path(p) for p in args.step0),
            guard={
                "guard_line": ledger["note"],
                "at": ledger["at"],
                "balance": ledger["balance"],
                "spent_usd": ledger["spent_usd"],
                "remaining_usd": ledger["remaining_usd"],
                "guard_source": "results/spend_cycle2.json :: sessions[-1]",
            },
        )
    if args.registry_rows:
        state = load_state()
        compiled = compile_categories(load_lexicon())
        state["rows"] = [row for row in state["rows"] if not row.get("in_registry")]
        state["rows"] += registry_rows(compiled, date.today())
        save(state)
        print(f"added the registry's store rows; wrote {RECORD.relative_to(REPO_ROOT)}")
        return 0
    if args.report:
        from retail_census_report import render  # deferred: only this path needs it

        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(render(json.loads(RECORD.read_text(encoding="utf-8"))), encoding="utf-8")
        print(f"wrote {REPORT.relative_to(REPO_ROOT)}")
        return 0
    return asyncio.run(run_checks(args.min_subscribers, args.max_checks))


if __name__ == "__main__":
    raise SystemExit(main())
