#!/usr/bin/env python3
"""Phase-5a channel discovery for the authorised themes, with a coverage ledger.

SPEC amendment 3.11 (4): discovery over mothers/kids, healthy lifestyle and baby food —
authorised 2026-08-04, **widened 2026-08-06** at the 5a acceptance to cooking/recipes,
supermarket promos, health/fitness and food-quality watch, plus direct seed-handle checks —
produces **candidates only**. `config/registry.yaml` is never touched here; a channel enters
through the track-R entry gate by the operator's choice.

A run scans only the themes the carried record (`--carry`) has not already searched, and
merges its rows in: re-running a theme costs another rate-limited pass and would measure a
different day, so the 5a rows are carried, not re-derived.

The per-channel check is `scripts/entry_check.py`'s, reused rather than reimplemented: same
resolve, same subscriber count, same linked-group test, same verdict vocabulary. Two things
5a needs that it does not measure are added here — posting rate over a **fixed four-week
window** (its own sample is the last 50 posts, however long that took) and a rough language
mix — and both are computed from one extra history request per candidate.

The ledger is what the operator picks channels off: candidates ranked, each carrying the
running portfolio total if everything above it entered, against the operator's coverage
target of 10,000,000 summed subscribers (SPEC 3.11 (4)). Two caveats ride with that number
and are printed in the record verbatim; neither is a footnote:

    summed subscribers != unique reach
    subscribers != comment flow

    PYTHONPATH=src python3 scripts/discover_channels.py --plan   # the queries, no API
    PYTHONPATH=src python3 scripts/discover_channels.py

Writes `results/discovery_5a1.json`. $0: Telegram's API is free and nothing here is a model call.
"""

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import entry_check  # noqa: E402
import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from telethon.errors import FloodWaitError  # noqa: E402

from market_pulse.langid import detect  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402
from market_pulse.telegram_client import build_client  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
RECORD = REPO_ROOT / "results" / "discovery_5a1.json"
PRIOR = REPO_ROOT / "results" / "discovery_5a.json"

THEMES = {
    "mothers_kids": ("мами", "материнство", "мама і малюк", "дітки"),
    "healthy_lifestyle": ("здорове харчування", "здоровий спосіб життя", "ЗОЖ", "нутриціологія"),
    "baby_food": ("дитяче харчування", "прикорм", "дитяче меню"),
    "cooking_recipes": (
        "рецепти",
        "кулінарія",
        "готуємо вдома",
        "страви",
        "випічка",
        "десерти",
        "вечеря",
    ),
    "supermarket_deals": (
        "знижки",
        "акції АТБ",
        "акції Сільпо",
        "акції Аврора",
        "супермаркет знижки",
        "економія продукти",
    ),
    "health_fitness": ("здоров'я", "схуднення", "фітнес", "тренування"),
    "food_quality": (
        "якість продуктів",
        "фальсифікат",
        "експертиза продуктів",
        "перевірка якості",
        "безпечність харчових продуктів",
        "Держпродспоживслужба",
    ),
}
"""Every theme the operator has authorised, and the exact queries sent.

The first three are the 2026-08-04 ruling; the last four were added 2026-08-06 at the 5a
acceptance on `docs/RESEARCH-5a1-themes.md` — `health_fitness` AGAINST the team lead's
recommendation, on the operator's word that the ledger prices a theme better than a forecast
does, and `food_quality` as the operator's own addition (dairy is the most falsified category
in UA retail, so a falsification watch lands inside the mission rather than beside it).

Written out rather than composed at run time and echoed into the record, so "only the
authorised themes were searched" is something a reader checks instead of takes on trust.
Widening this list is an operator decision taken on the ledger's gap (SPEC 3.11 (4))."""

SEED_HANDLES = (
    "@recepti",
    "@mameni_recepti",
    "@klopotenkofood",
    "@blwbabies",
    "@kopiyochka1",
    "@epicentrk_sale",
    "@maudau",
)
"""Handles named in the research note and checked directly, past the search.

`contacts.SearchRequest` ranks by its own relevance and returns at most DISCOVER_LIMIT rows
per query, so a channel the operator already knows about can simply never surface. A seed that
does surface anyway dedups by handle and is measured once."""

SEED_TAG = "seed"
"""The `found_by` prefix seeds carry, so a subtotal can tell a searched theme from a handed
one — a theme that only "found" its own seeds found nothing."""

COVERAGE_TARGET = 10_000_000
"""Operator, 2026-08-05 (SPEC 3.11 (4)): the monitored portfolio aims at this many summed
subscribers."""

CAVEATS = (
    "summed subscribers != unique reach",
    "subscribers != comment flow",
)
"""Printed beside the ledger verbatim, in the words `docs/PROMPT-5a.md` uses.

The first: overlap between two channels' audiences is unmeasurable from the API, so the sum
is an upper bound on reach and nothing else. The second: rows are born in discussion groups,
and a channel with a million subscribers and comments disabled contributes none."""

WINDOW_DAYS = 28
WINDOW_LIMIT = 1200
"""How far back the posting-rate window reaches, and the request cap that bounds one channel's
scan. A channel that fills the cap inside the window is recorded as `window_truncated` — its
rate is a floor, not a measurement."""

COUNTED = ("usable", "posts-only")
"""Which verdicts the coverage ledger counts. A handle that does not resolve, a channel
Telegram flags, and one that errored are listed with the rest and contribute zero: a
portfolio total may not be inflated by a channel nothing can collect from."""


def window_stats(samples: list[tuple], texts: list[str], truncated: bool) -> dict:
    """Posting rate over the fixed window and the rough language mix, from one sample.

    `samples` are `entry_check.collapse_albums` rows — an album is one post, or a retail
    channel that posts six pictures at once reads as six times the traffic. The language mix
    is counted over the texts instead, because only one item of an album carries any.
    """
    posts = entry_check.collapse_albums(samples)
    dates = sorted(date for date, _ in posts)
    mix: dict[str, int] = {}
    for text in texts:
        lang = detect(text)
        mix[lang] = mix.get(lang, 0) + 1
    return {
        "window_days": WINDOW_DAYS,
        "window_truncated": truncated,
        "n_posts": len(posts),
        "posts_per_week": round(len(posts) / (WINDOW_DAYS / 7), 2),
        "last_post": dates[-1].isoformat() if dates else None,
        "n_texts": len(texts),
        # Shares, not counts: "0.62 ua" is what a reader compares across channels.
        "language_mix": {lang: round(count / len(texts), 2) for lang, count in sorted(mix.items())},
    }


def candidate_row(record: dict, window: dict, found_by: list[str]) -> dict:
    """One ledger row: what the brief asks for per candidate, and the verdict behind it."""
    return {
        "title": record.get("title"),
        "handle": record["handle"],
        "subscribers": record.get("subscribers"),
        "discussion_group": bool(record.get("comments_enabled")),
        "posts_per_week": window["posts_per_week"],
        "language_mix": window["language_mix"],
        "last_post": window["last_post"],
        "telegram_verified": bool(record.get("telegram_verified")),
        "broadcast": record.get("broadcast"),
        "verdict": record["verdict"],
        "reasons": record.get("reasons", []),
        "found_by": found_by,
        "window": window,
        "error": record.get("error"),
    }


def build_ledger(registry_rows: list[dict], candidates: list[dict]) -> dict:
    """The coverage ledger: where the portfolio stands, and what each candidate would add.

    The cumulative column is the point of the file. It answers "how many of these does the
    operator have to take to close the gap", which a per-row subscriber count does not.
    """
    registry_sum = sum(row["subscribers"] or 0 for row in registry_rows)
    counted = [row for row in candidates if row["verdict"] in COUNTED]
    running = registry_sum
    ranked = []
    for row in sorted(counted, key=lambda r: r["subscribers"] or 0, reverse=True):
        running += row["subscribers"] or 0
        ranked.append(
            {**row, "cumulative_subscribers": running, "gap_after": COVERAGE_TARGET - running}
        )
    candidate_sum = running - registry_sum
    # The second caveat, made into a number instead of left as a sentence: a channel that has
    # posted nothing in the window contributes subscribers to the sum and no rows to the loop.
    live = [row for row in counted if row["posts_per_week"] > 0]
    live_sum = sum(row["subscribers"] or 0 for row in live)
    return {
        "target_subscribers": COVERAGE_TARGET,
        "caveats": list(CAVEATS),
        "registry_channels": len(registry_rows),
        "registry_subscribers": registry_sum,
        "gap_before_any_candidate": COVERAGE_TARGET - registry_sum,
        "candidates_found": len(candidates),
        "candidates_counted": len(counted),
        "counted_verdicts": list(COUNTED),
        "candidate_subscribers_total": candidate_sum,
        "portfolio_if_all_counted_entered": registry_sum + candidate_sum,
        "gap_if_all_counted_entered": COVERAGE_TARGET - registry_sum - candidate_sum,
        "candidates_posting_in_the_window": len(live),
        "candidates_silent_in_the_window": len(counted) - len(live),
        "live_candidate_subscribers": live_sum,
        "portfolio_if_only_live_entered": registry_sum + live_sum,
        "gap_if_only_live_entered": COVERAGE_TARGET - registry_sum - live_sum,
        "with_a_discussion_group": sum(1 for row in counted if row["discussion_group"]),
        "live_note": (
            f"'live' = at least one post in the last {WINDOW_DAYS} days. The split is the second"
            " caveat as a number: a silent channel adds subscribers to the sum and no comment"
            " rows to the loop."
        ),
        "ranked": ranked,
    }


def merge_candidates(carried: list[dict], fresh: list[dict], extra_tags: dict) -> list[dict]:
    """The union of two scans, deduped by handle — the combined reading the ledger is built on.

    A carried row keeps its measurement (it was measured, and re-measuring it would be a
    different day's number) and gains the `found_by` tags of any theme in this scan that also
    found it.
    """
    merged = []
    for row in carried:
        held = row.get("found_by", [])
        tags = [tag for tag in extra_tags.get(row["handle"].lower(), []) if tag not in held]
        merged.append({**row, "found_by": held + tags} if tags else row)
    seen = {row["handle"].lower() for row in merged}
    merged += [row for row in fresh if row["handle"].lower() not in seen]
    return merged


def theme_subtotals(candidates: list[dict]) -> dict:
    """What each theme would add on its own, so the operator can price it.

    Every authorised theme gets a row even when it found nothing: `health_fitness` was
    authorised against the team lead's recommendation precisely so the ledger could answer
    that, and an empty row IS the answer, where a missing one reads as an oversight.

    A channel two themes both found is counted in both, so these do not sum to the ledger's
    total — `overlap_note` says so in the record rather than in a report nobody re-reads.
    """
    rows = {}
    for theme in [*THEMES, SEED_TAG]:
        found = [
            row
            for row in candidates
            if any(tag.split(":")[0] == theme for tag in row.get("found_by", []))
        ]
        counted = [row for row in found if row["verdict"] in COUNTED]
        live = [row for row in counted if row["posts_per_week"] > 0]
        rows[theme] = {
            "candidates": len(found),
            "counted": len(counted),
            "subscribers": sum(row["subscribers"] or 0 for row in counted),
            "live": len(live),
            "live_subscribers": sum(row["subscribers"] or 0 for row in live),
            "with_a_discussion_group": sum(1 for row in counted if row["discussion_group"]),
        }
    return rows


async def window_sample(client, entity, now: datetime) -> tuple[list[tuple], list[str], bool]:
    """One history request per candidate: the last WINDOW_DAYS of posts, and their texts."""
    cutoff = now - timedelta(days=WINDOW_DAYS)
    samples, texts = [], []
    # wait_time is the collector's own pacing between history requests (scripts/backfill.py).
    async for message in client.iter_messages(entity, limit=WINDOW_LIMIT, wait_time=1.0):
        if message.action is not None:
            continue
        if message.date < cutoff:
            return samples, texts, False
        samples.append(
            (
                message.date,
                message.replies.replies if message.replies else None,
                message.grouped_id,
                False,
            )
        )
        if (message.raw_text or "").strip():
            texts.append(message.raw_text)
    return samples, texts, len(samples) >= WINDOW_LIMIT


async def measure(client, source, handle: str, now: datetime) -> tuple[dict, dict]:
    """The entry check plus the four-week window, for one channel."""
    record = await entry_check.check_channel(client, source, handle)
    if not record.get("resolved"):
        return record, window_stats([], [], False)
    entity = await client.get_entity(handle)
    samples, texts, truncated = await window_sample(client, entity, now)
    return record, window_stats(samples, texts, truncated)


async def search_themes(client, themes: dict[str, tuple]) -> dict[str, dict]:
    """Every theme's queries run once, deduplicated by handle, remembering who found what.

    Keyed by the lowered handle: Telegram treats @MAUDAU and @maudau as one channel, and a
    coverage ledger that counted them apart would add the same audience to the sum twice.
    """
    found: dict[str, dict] = {}
    for theme, queries in themes.items():
        for query in queries:
            print(f"searching {theme}: {query!r}", flush=True)
            for source, handle in await entry_check.search_channels(client, query):
                entry = found.setdefault(
                    handle.lower(), {"source": source, "handle": handle, "found_by": []}
                )
                entry["found_by"].append(f"{theme}:{query}")
            await asyncio.sleep(entry_check.PAUSE_SECONDS)
    return found


def add_seeds(found: dict[str, dict], seeds: tuple[str, ...]) -> None:
    """Put the research note's handles into the same pipeline the search feeds.

    A seed already found by a query keeps that entry and gains the tag: the same channel
    measured twice would be the same audience counted twice.
    """
    for handle in seeds:
        entry = found.setdefault(
            handle.lower(),
            {
                "source": entry_check.Source(SEED_TAG, handle, "community", (handle,)),
                "handle": handle,
                "found_by": [],
            },
        )
        entry["found_by"].append(f"{SEED_TAG}:{handle}")


def themes_to_scan(carried: dict | None) -> dict[str, tuple]:
    """The authorised themes the carried record has not already searched.

    Read off the prior record's own `themes` key rather than kept in a second constant: a
    re-scan costs another rate-limited pass and would measure a different day, and a list of
    "already done" maintained by hand is a list that silently stops matching the file.
    """
    done = set(carried["themes"]) if carried else set()
    return {theme: queries for theme, queries in THEMES.items() if theme not in done}


async def run(registry_channels: list[tuple], themes: dict[str, tuple], known: set[str]) -> dict:
    now = datetime.now(UTC)
    client = build_client()
    await client.connect()
    try:
        if not await client.is_user_authorized():
            raise SystemExit("No Telegram session. Run: python3 scripts/tg_login.py")

        registry_rows = []
        for source, handle in registry_channels:
            print(f"registry {handle} ({source.id})...", flush=True)
            record, window = await measure(client, source, handle, now)
            registry_rows.append(
                {**candidate_row(record, window, ["registry"]), "source_id": source.id}
            )
            await asyncio.sleep(entry_check.PAUSE_SECONDS)

        found = await search_themes(client, themes)
        add_seeds(found, SEED_HANDLES)
        already = {handle.lower() for _, handle in registry_channels}
        candidates, extra_tags = [], {}
        flood_wait = None
        for key, entry in found.items():
            handle = entry["handle"]
            if key in already:
                continue  # already counted in the registry sum; never twice
            if key in known:
                # Measured in the carried record. Its row stands; only the tag is new, and a
                # theme subtotal that dropped it would under-price the theme by exactly the
                # channels it shares with an older one.
                extra_tags[key] = entry["found_by"]
                continue
            print(f"checking {handle}...", flush=True)
            try:
                record, window = await measure(client, entry["source"], handle, now)
            except FloodWaitError as exc:
                # `scripts/entry_check.py:187`'s policy, and it must be branched BEFORE the
                # generic handler below: swallowed there, a rate-limited candidate is written
                # down as `verdict: "error"` — a permanent judgement on a temporary state —
                # and the scan walks straight into the next request Telegram is refusing.
                flood_wait = exc.seconds
                print(
                    f"FloodWait: Telegram asked for {exc.seconds}s. Scan aborted at {handle},"
                    f" keeping the {len(candidates)} candidates already checked.",
                    flush=True,
                )
                break
            except Exception as exc:  # one unusable channel must not discard the scan
                record = {
                    "handle": handle,
                    "resolved": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "verdict": "error",
                    "reasons": ["unexpected failure, see error"],
                }
                window = window_stats([], [], False)
            candidates.append(candidate_row(record, window, entry["found_by"]))
            await asyncio.sleep(entry_check.PAUSE_SECONDS)
    finally:
        await client.disconnect()
    return {
        "registry_rows": registry_rows,
        "candidates": candidates,
        "extra_tags": extra_tags,
        "generated_at": now,
        # A scan cut short by a FloodWait produces a ledger that looks complete. The record
        # says how many seconds it was asked for, so an under-count reads as one.
        "flood_wait_seconds": flood_wait,
    }


def print_table(rows: list[dict]) -> None:
    header = (
        f"{'handle':<24}{'title':<26}{'subs':>10}{'comm':>6}{'posts/wk':>10}  {'last post':<12}mix"
    )
    print(f"\n{header}\n{'-' * len(header)}")
    for row in rows:
        mix = " ".join(f"{k}:{v}" for k, v in row["language_mix"].items()) or "—"
        print(
            f"{row['handle'][:23]:<24}{(row['title'] or '—')[:25]:<26}"
            f"{(row['subscribers'] if row['subscribers'] is not None else 0):>10}"
            f"{'yes' if row['discussion_group'] else 'no':>6}{row['posts_per_week']:>10}  "
            f"{(row['last_post'] or '—')[:10]:<12}{mix}  [{row['verdict']}]"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase-5a channel discovery + coverage ledger.")
    parser.add_argument("--plan", action="store_true", help="print the queries and stop, no API")
    parser.add_argument(
        "--rebuild-ledger",
        action="store_true",
        help="recompute the ledger from the rows already in the record — no API, no re-scan",
    )
    parser.add_argument(
        "--carry",
        default=str(PRIOR),
        help="a prior record whose themes are not re-scanned and whose rows join the ledger",
    )
    args = parser.parse_args(argv)

    registry = load_registry(REGISTRY)
    registry_channels = [
        (source, handle) for source in registry.sources for handle in source.telegram_channels
    ]
    carry = Path(args.carry)
    carried = json.loads(carry.read_text(encoding="utf-8")) if carry.exists() else None
    scanning = themes_to_scan(carried)
    print(f"{len(THEMES)} authorised themes, {len(scanning)} to scan now:")
    for theme, queries in THEMES.items():
        mark = " " if theme in scanning else "·"  # · = carried, not re-searched
        print(f"{mark} {theme:<20}{', '.join(queries)}")
    print(f"  {SEED_TAG:<20}{', '.join(SEED_HANDLES)}")
    if carried:
        print(f"carrying {len(carried['candidates'])} candidates from {relabel.rel(carry)}")
    print(
        f"registry: {len(registry_channels)} channels — {', '.join(h for _, h in registry_channels)}"
    )
    if args.plan:
        return 0

    if args.rebuild_ledger:
        # A rescan costs another rate-limited pass and would measure a different day. The rows
        # are already in the record; a ledger rule that changed is re-derived from them.
        held = json.loads(RECORD.read_text(encoding="utf-8"))
        result = {
            "registry_rows": held["registry"]["rows"],
            "candidates": held["candidates"],
            "generated_at": held["generated_at"],
            "flood_wait_seconds": held.get("flood_wait_seconds"),
        }
        # A rebuild re-derives arithmetic and nothing else: what was scanned, and what was
        # carried in, are facts about the run that produced the rows, not about this pass.
        provenance = {
            "themes_scanned_here": held.get("themes_scanned_here", []),
            "seed_handles": held.get("seed_handles", []),
            "carried_from": held.get("carried_from"),
            "checked_this_run": held.get("checked_this_run"),
        }
    else:
        carried_rows = carried["candidates"] if carried else []
        known = {row["handle"].lower() for row in carried_rows}
        result = asyncio.run(run(registry_channels, scanning, known))
        result["generated_at"] = result["generated_at"].isoformat(timespec="seconds")
        result["scanned"] = len(result["candidates"])
        result["candidates"] = merge_candidates(
            carried_rows, result["candidates"], result.get("extra_tags", {})
        )
        provenance = {
            "themes_scanned_here": sorted(scanning),
            "seed_handles": list(SEED_HANDLES),
            "carried_from": {
                "path": relabel.rel(carry) if carried else None,
                "generated_at": carried["generated_at"] if carried else None,
                "themes": sorted(carried["themes"]) if carried else [],
                "candidates": len(carried_rows),
                "note": (
                    "The carried themes were NOT re-scanned: their rows are the earlier"
                    " measurement, carried whole. A candidate a theme of this run also found"
                    " keeps that row and gains the tag, so the per-theme subtotals see it and"
                    " the coverage sum still counts it once."
                ),
            },
            "checked_this_run": result.get("scanned"),
        }
    ledger = build_ledger(result["registry_rows"], result["candidates"])
    ledger["per_theme"] = theme_subtotals(result["candidates"])
    ledger["overlap_note"] = (
        "per_theme rows are per `found_by` tag: a channel two themes both found is counted in"
        " both, so the subtotals do not sum to candidate_subscribers_total. They price a theme"
        " on its own, not a partition of the portfolio."
    )

    record = {
        "generated_at": result["generated_at"],
        "ledger_rebuilt_at": datetime.now(UTC).isoformat(timespec="seconds")
        if args.rebuild_ledger
        else None,
        "scan_complete": result.get("flood_wait_seconds") is None,
        "flood_wait_seconds": result.get("flood_wait_seconds"),
        "authorised": (
            "operator 2026-08-04 (first three themes) / 2026-08-05 (coverage target) /"
            " 2026-08-06 (four more themes + seed handles, on docs/RESEARCH-5a1-themes.md),"
            " SPEC 3.11 (4)"
        ),
        "themes": {theme: list(queries) for theme, queries in THEMES.items()},
        **provenance,
        "search_limit_per_query": entry_check.DISCOVER_LIMIT,
        "post_sample": entry_check.POST_SAMPLE,
        "window_days": WINDOW_DAYS,
        "registry": {
            "path": relabel.rel(REGISTRY),
            "rows": result["registry_rows"],
            "note": (
                "Subscriber counts read live at this run, not from the registry file — the"
                " registry stores no numbers (config/registry.yaml, §Sources). These are the"
                " channels the loop launches on; the file is not edited by this script."
            ),
        },
        "candidates": result["candidates"],
        "ledger": ledger,
        "caveats": list(CAVEATS),
        "note": (
            "Candidates only. config/registry.yaml is untouched: a new channel enters through"
            " the track-R entry gate by the operator's choice (SPEC 3.11 (4)). The coverage"
            " ledger is an upper bound in both directions named in `caveats` — summed"
            " subscribers != unique reach, and subscribers != comment flow."
        ),
        "git": git_state(RECORD),
    }
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print_table(result["candidates"])
    print(
        f"\nregistry {ledger['registry_channels']} channels: {ledger['registry_subscribers']:,} subscribers"
    )
    print(f"candidates counted: {ledger['candidates_counted']} of {ledger['candidates_found']}")
    print(f"\n{'theme':<20}{'cands':>7}{'counted':>9}{'subscribers':>13}{'live':>6}{'w/group':>9}")
    for theme, row in ledger["per_theme"].items():
        print(
            f"{theme:<20}{row['candidates']:>7}{row['counted']:>9}"
            f"{row['subscribers']:>13,}{row['live']:>6}{row['with_a_discussion_group']:>9}"
        )
    print(f"\nportfolio if all counted entered: {ledger['portfolio_if_all_counted_entered']:,}")
    print(f"gap to {COVERAGE_TARGET:,}: {ledger['gap_if_all_counted_entered']:,}")
    for caveat in CAVEATS:
        print(f"  caveat: {caveat}")
    print(f"\nwrote {relabel.rel(RECORD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
