#!/usr/bin/env python3
"""5c1 addendum: the Хвилинка search and the Poltava-cities discovery scan ($0, read-only).

Canon: `docs/CHANNELS-launch.md`, section "Дозаявка №2" (operator, 2026-08-07 evening). Two
questions, neither of which is a registry write:

``--search``
    Does the Хвилинка chain (Lubny, Myrhorod, Lokhvytsia, Pyriatyn, Hrebinka) have a Telegram
    channel at all? Their site carries no link. Three queries through Telegram's own global
    search; a convincing match goes to the gate, and NOTHING here decides that — the script
    records what the search returned and whether any row's title even contains the name. A
    negative finding is written into the gate record's notes, because "we looked and found
    nothing" is a result that has to survive, and an absent note reads like an unasked question.

``--poltava``
    The discovery scan for the new `poltava_cities` theme, in `scripts/discover_channels.py`'s
    pattern and reusing its machinery — same per-channel check, same four-week window, same
    language mix — into its own record. Candidates ONLY: no registry entry, no join, no verdict.
    A city channel the operator later picks enters through the track-R gate like everything else,
    and enters POSTS-ONLY until 5c2 rules on category-filtered comment fetch, because without
    that filter a city chat's whole traffic lands in a paid inference queue.

    PYTHONPATH=src python3 scripts/late_batch_5c1.py --search
    PYTHONPATH=src python3 scripts/late_batch_5c1.py --poltava
"""

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import discover_channels as discovery  # noqa: E402
import entry_check  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from telethon.errors import FloodWaitError  # noqa: E402

from market_pulse.registry import load_registry  # noqa: E402
from market_pulse.telegram_client import build_client  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
GATE_RECORD = REPO_ROOT / "results" / "entry_gate_5c1.json"
RECORD = REPO_ROOT / "results" / "discovery_5c1_poltava.json"

HVYLYNKA_QUERIES = ("Хвилинка", "Хвилинка Лубни", "hvylynka")
HVYLYNKA_MARKERS = ("хвилинк", "hvylynk", "хвилинка")
"""What a title has to contain to be worth a human look. Deliberately loose — the judgement is
reported, not automated, and a marker that matched nothing is itself the finding."""

HVYLYNKA_JUDGEMENT = {
    "judged_by": "executor, 2026-08-07",
    "verdict": "NEGATIVE — none of the name matches is the retail chain",
    "why": (
        "«хвилинка» is an ordinary Ukrainian word (a minute), so the marker matches a lot of"
        " unrelated channels. Every row was read: a Zhytomyr freight company (@hwylynkazt), an"
        " English-lesson channel (@englishbrend), a literature digest, a music channel, a"
        " dementia-awareness channel and several joke channels. The only plausible pair —"
        " @khvylynka (2,321) and its @khvylynkachat — was probed read-only and is a private"
        " classified-ads board: its own description reads «Приватні оголошення приймаються"
        " безкоштовно», and its recent posts are giveaways and a counterfeit-spotting poll, not"
        " a retail chain's promos. The query 'Хвилинка Лубни', which pairs the name with the"
        " chain's home town, returned nothing at all."
    ),
    "probed": ["@khvylynka"],
    "bound": (
        "This closes the question by record, it does not prove absence: contacts.SearchRequest"
        " ranks by its own relevance and returns at most ten rows per query. The finding is that"
        " the chain has no FINDABLE public channel under its own name — consistent with"
        " hvylya.net.ua carrying no Telegram link."
    ),
}
"""The executor's read of the search, kept in the repo rather than typed into the record once.

`--search` deliberately judges nothing: it records what came back and whether any title even
carries the name. Deciding which match is convincing is a human call, and this is that call with
its reasons, applied by `--close-hvylynka` without touching Telegram."""

THEME = "poltava_cities"
CITIES = (
    "Полтава",
    "Кременчук",
    "Горішні Плавні",
    "Лубни",
    "Миргород",
    "Гадяч",
    "Пирятин",
    "Хорол",
    "Лохвиця",
    "Зіньків",
    "Карлівка",
    "Кобеляки",
    "Решетилівка",
    "Глобине",
    "Диканька",
    "Великі Сорочинці",
)
"""The operator's own list, in the canon's order. Written out and echoed into the record so
"only these towns were searched" is checked rather than trusted."""


def known_handles() -> dict:
    """Handles already spoken for — registry sources and everything the 5c1 gate measured.

    A scan that re-measured them would spend rate limit on a question already answered, and a
    ledger that listed them would invite the operator to pick a channel they already have.
    """
    registry = {
        handle.lower(): "registry"
        for source in load_registry(REGISTRY).sources
        for handle in source.telegram_channels
    }
    gated = {
        row["handle"].lower(): f"gated 5c1 ({row['verdict']})"
        for row in json.loads(GATE_RECORD.read_text(encoding="utf-8"))["candidates"]
    }
    return {**gated, **registry}


async def run_search(client) -> dict:
    """Telegram's global search for the chain, one row per result. Judges nothing."""
    results = {}
    for query in HVYLYNKA_QUERIES:
        print(f"searching {query!r}...", flush=True)
        results[query] = await entry_check.suggest(client, query)
        for row in results[query]:
            mark = "✓" if row["telegram_verified"] else " "
            print(f"  @{row['username']:<28}{mark} {row['subscribers'] or 0:>8}  {row['title']}")
        await asyncio.sleep(entry_check.PAUSE_SECONDS)

    seen, matches = set(), []
    for rows in results.values():
        for row in rows:
            title = (row["title"] or "").casefold()
            handle = (row["username"] or "").casefold()
            if row["username"] not in seen and any(
                marker in title or marker in handle for marker in HVYLYNKA_MARKERS
            ):
                seen.add(row["username"])
                matches.append(row)
    return {"queries": list(HVYLYNKA_QUERIES), "results": results, "name_matches": matches}


def matched_handles(note: dict) -> list[str]:
    return sorted(row["username"] for row in note.get("name_matches", []) if row.get("username"))


def record_search(found: dict) -> dict:
    """Write the search into the gate record's notes — closed only if it found nothing.

    A judgement already recorded is carried forward rather than overwritten: re-running the
    search would otherwise reopen a question a human had closed, silently. It is carried only
    while it still applies — if this search matched a different set of handles, the judgement is
    about rows that are no longer the rows, and the note says so instead of standing.
    """
    record = json.loads(GATE_RECORD.read_text(encoding="utf-8"))
    closed = not found["name_matches"]
    held = record.get("notes", {}).get("hvylynka_search", {})
    judgement, stale = held.get("judgement"), None
    if judgement is not None:
        stale = matched_handles(held) != matched_handles(found)
        closed = not stale
    note = {
        "asked": (
            "does the Хвилинка chain (Lubny, Myrhorod, Lokhvytsia, Pyriatyn, Hrebinka) have a"
            " Telegram channel? canon docs/CHANNELS-launch.md 'Дозаявка №2'"
        ),
        "searched_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "queries": found["queries"],
        "results_per_query": {query: len(rows) for query, rows in found["results"].items()},
        "name_matches": found["name_matches"],
        "rows": found["results"],
        "closed": closed,
        "judgement": judgement,
        "judgement_stale": stale,
        "finding": (
            f"{judgement['verdict']}. {judgement['why']} {judgement['bound']}"
            if judgement is not None and not stale
            else "REOPENED — a recorded judgement is about a different set of matches than this"
            " search returned. Re-read the rows before closing it again."
            if judgement is not None
            else "NEGATIVE — Telegram's global search returns no channel whose title or handle carries"
            " the chain's name under any of the three queries. The question is closed by record:"
            " the site hvylya.net.ua carries no Telegram link either. Bounded, not proven —"
            " contacts.SearchRequest ranks by its own relevance and returns at most ten rows per"
            " query, so this says the chain has no findable public channel, not that none exists."
            if closed
            else "MATCHES FOUND — not closed. The rows above need a human look before any of them"
            " goes to the gate; this script does not decide what is convincing."
        ),
    }
    record.setdefault("notes", {})["hvylynka_search"] = note
    record["git"] = git_state(GATE_RECORD)
    GATE_RECORD.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return note


async def run_scan(client, known: dict, carried: list[dict]) -> dict:
    """The city scan: `discover_channels`'s own measure over this theme's queries."""
    found = await discovery.search_themes(client, {THEME: CITIES})
    held = {row["handle"].lower() for row in carried}
    now = datetime.now(UTC)
    candidates, skipped, flood_wait = list(carried), {}, None

    for key, entry in found.items():
        if key in known:
            skipped[entry["handle"]] = known[key]
            continue
        if key in held:
            continue  # measured by an earlier pass of this scan; its row stands
        print(f"checking {entry['handle']}...", flush=True)
        try:
            record, window = await discovery.measure(client, entry["source"], entry["handle"], now)
        except FloodWaitError as exc:
            # entry_check.py:187's policy: a wait is not a verdict, and the scan stops rather
            # than walking into the next request Telegram is refusing.
            flood_wait = exc.seconds
            print(f"FloodWait {exc.seconds}s — stopping with {len(candidates)} measured")
            break
        except Exception as exc:
            record = {
                "handle": entry["handle"],
                "resolved": False,
                "error": f"{type(exc).__name__}: {exc}",
                "verdict": "error",
                "reasons": ["unexpected failure, see error"],
            }
            window = discovery.window_stats([], [], False)
        candidates.append(discovery.candidate_row(record, window, entry["found_by"]))
        await asyncio.sleep(entry_check.PAUSE_SECONDS)

    return {"candidates": candidates, "skipped": skipped, "flood_wait_seconds": flood_wait}


def ledger(candidates: list[dict]) -> dict:
    """Ranked by subscribers with a running total — what taking the top N would add.

    Deliberately NOT `discover_channels.build_ledger`: that one measures the portfolio against
    the 10,000,000 coverage target and would need the registry's own subscriber sum re-measured
    to say anything true. This scan's job is to arm a pick, and the portfolio number lives in
    `results/discovery_5a1.json` where it was measured.
    """
    counted = [row for row in candidates if row["verdict"] in discovery.COUNTED]
    running, ranked = 0, []
    for row in sorted(counted, key=lambda r: r["subscribers"] or 0, reverse=True):
        running += row["subscribers"] or 0
        ranked.append({**row, "cumulative_subscribers": running})
    live = [row for row in counted if row["posts_per_week"] > 0]
    return {
        "candidates_found": len(candidates),
        "candidates_counted": len(counted),
        "counted_verdicts": list(discovery.COUNTED),
        "subscribers_total": running,
        "live_in_the_window": len(live),
        "silent_in_the_window": len(counted) - len(live),
        "live_subscribers": sum(row["subscribers"] or 0 for row in live),
        "with_a_discussion_group": sum(1 for row in counted if row["discussion_group"]),
        "caveats": list(discovery.CAVEATS),
        "ranked": ranked,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="5c1 addendum: the Хвилинка search and the scan.")
    parser.add_argument("--search", action="store_true", help="Telegram search for the chain")
    parser.add_argument(
        "--close-hvylynka",
        action="store_true",
        help="write the executor's read of the search into the note (no API, no new search)",
    )
    parser.add_argument("--poltava", action="store_true", help="the poltava_cities discovery scan")
    parser.add_argument("--plan", action="store_true", help="print the queries and stop, no API")
    args = parser.parse_args(argv)

    if args.close_hvylynka:
        record = json.loads(GATE_RECORD.read_text(encoding="utf-8"))
        note = record.get("notes", {}).get("hvylynka_search")
        if note is None:
            raise SystemExit("run --search first: there is no search to judge")
        note["judgement"] = HVYLYNKA_JUDGEMENT
        note["closed"] = True
        note["finding"] = (
            f"{HVYLYNKA_JUDGEMENT['verdict']}. {HVYLYNKA_JUDGEMENT['why']}"
            f" {HVYLYNKA_JUDGEMENT['bound']}"
        )
        record["git"] = git_state(GATE_RECORD)
        GATE_RECORD.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(note["finding"])
        print(f"\nclosed in {GATE_RECORD.relative_to(REPO_ROOT)} :: notes.hvylynka_search")
        return 0

    if args.plan or not (args.search or args.poltava):
        print(f"search  : {', '.join(HVYLYNKA_QUERIES)}")
        print(f"{THEME}: {len(CITIES)} towns — {', '.join(CITIES)}")
        print(f"limit   : {entry_check.DISCOVER_LIMIT}/query · window {discovery.WINDOW_DAYS} d")
        print(f"known   : {len(known_handles())} handles already spoken for, not re-measured")
        return 0

    known = known_handles()
    carried = (
        json.loads(RECORD.read_text(encoding="utf-8"))["candidates"] if RECORD.exists() else []
    )

    async def run():
        client = build_client()
        await client.connect()
        try:
            if not await client.is_user_authorized():
                raise SystemExit("No Telegram session. Run: python3 scripts/tg_login.py")
            out = {}
            if args.search:
                out["search"] = await run_search(client)
            if args.poltava:
                out["scan"] = await run_scan(client, known, carried)
            return out
        finally:
            await client.disconnect()

    out = asyncio.run(run())

    if "search" in out:
        note = record_search(out["search"])
        print(f"\n{note['finding']}")
        print(f"recorded in {GATE_RECORD.relative_to(REPO_ROOT)} :: notes.hvylynka_search")

    if "scan" in out:
        scan = out["scan"]
        record = {
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "phase": "5c1 addendum",
            "theme": THEME,
            "authorised": (
                "operator 2026-08-07 evening, docs/CHANNELS-launch.md 'Дозаявка №2'; SPEC 3.11 (4)"
                " — discovery produces candidates only"
            ),
            "queries": list(CITIES),
            "search_limit_per_query": entry_check.DISCOVER_LIMIT,
            "post_sample": entry_check.POST_SAMPLE,
            "window_days": discovery.WINDOW_DAYS,
            "scan_complete": scan["flood_wait_seconds"] is None,
            "flood_wait_seconds": scan["flood_wait_seconds"],
            "already_spoken_for": scan["skipped"],
            "candidates": scan["candidates"],
            "ledger": ledger(scan["candidates"]),
            "note": (
                "Candidates ONLY. config/registry.yaml is untouched, no group was joined, and no"
                " verdict here admits anything: a channel the operator picks enters through the"
                " track-R gate. A city pick enters POSTS-ONLY until 5c2 rules on"
                " category-filtered comment fetch — without that filter a city chat's whole"
                " traffic lands in a paid inference queue (canon 'Дозаявка №2')."
            ),
            "git": git_state(RECORD),
        }
        RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        discovery.print_table(scan["candidates"])
        led = record["ledger"]
        print(
            f"\n{led['candidates_found']} candidates, {led['candidates_counted']} collectable,"
            f" {led['with_a_discussion_group']} with a group, {led['live_in_the_window']} live"
            f" · {led['subscribers_total']:,} subscribers"
        )
        for caveat in led["caveats"]:
            print(f"  caveat: {caveat}")
        print(f"\nwrote {RECORD.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
