#!/usr/bin/env python3
"""Block 2 — the genre the census never searched for.

The operator, 2026-08-30: «Ты искал региональные каналы с украинским написанием Підслухано Чутово?»
No. `discover_channels.CHAT_TERMS` is ('чат', 'спільнота', 'оголошення', 'барахолка') and the word
«підслухано» appears nowhere in this repository. All four authorised terms select for CLASSIFIEDS
and notice boards — which is exactly the corpus the brand probe read 4 507 messages of and found
zero dairy-brand mentions in.

So that null result may be an artefact of the query genre, not a fact about Poltava: «Підслухано X»
and «Типове X» are the gossip-and-complaint channels, where somebody writes «взяла молоко в АТБ,
кисле». The population a search defines is the population a finding describes — the same shape as
Dv871, one level up: there the instrument was wrong for the question, here the QUERY was.

Search only: `contacts.SearchRequest` already returns title, subscribers, verified and
broadcast/megagroup, so nothing here spends a resolve. Widening the authorised term list is an
operator decision (`discover_channels` docstring, SPEC 3.11 (4)) and this run records theirs.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import entry_check as entry  # noqa: E402
import retail_census as census  # noqa: E402
from collect_5c1 import refuse_inside_flood_wait  # noqa: E402
from discover_channels import POLTAVA_TOWNS  # noqa: E402
from retail_resolve_r2 import counting, suggest_disabled  # noqa: E402
from telethon import functions  # noqa: E402
from telethon.errors import FloodWaitError  # noqa: E402

CENSUS = REPO_ROOT / "results" / "retail_census.json"
OUT = REPO_ROOT / "results" / "poltava_discussion_search.json"
UTC = timezone.utc
PAUSE_SECONDS = 3.0
MAX_REQUESTS = 60
AUTHORISED_BY = (
    "operator, 2026-08-30: «Ты искал региональные каналы с украинским написанием"
    " Підслухано Чутово?» — widening CHAT_TERMS to the discussion genre"
)
# The gossip-and-complaint genre, in its Ukrainian spellings. «Підслухано» is the canonical one the
# operator named; «типове» is the same genre under a different franchise name.
TERMS = ("підслухано", "типове")


def known_handles() -> set[str]:
    state = json.loads(CENSUS.read_text(encoding="utf-8"))
    return {r["handle"].lower() for r in state["rows"]}


async def run(terms: tuple[str, ...], towns: list[str]) -> int:
    refuse_inside_flood_wait()
    seen = known_handles()
    queries = [(town, term) for term in terms for town in towns]
    print(f"{len(queries)} queries · ceiling {MAX_REQUESTS} · {PAUSE_SECONDS}s apart")

    client = census.build_client()
    await client.connect()
    found: dict[str, dict] = {}
    ran, flood = [], None
    with counting(client) as calls, suggest_disabled():
        try:
            if not await client.is_user_authorized():
                raise SystemExit("No Telegram session. Run: python3 scripts/tg_login.py")
            for town, term in queries:
                if calls["n"] + 1 > MAX_REQUESTS:
                    print(f"ceiling: {calls['n']} spent, {len(queries) - len(ran)} queries left")
                    break
                q = f"{term} {town}"
                try:
                    result = await client(
                        functions.contacts.SearchRequest(q=q, limit=entry.DISCOVER_LIMIT)
                    )
                except FloodWaitError as exc:
                    flood = exc.seconds
                    print(f"FloodWait: {exc.seconds}s — stopped at {q!r}")
                    break
                ran.append({"query": q, "hits": len(result.chats)})
                fresh = 0
                for chat in result.chats:
                    username = getattr(chat, "username", None)
                    if not username:
                        continue  # private or invite-only: not collectable, same rule as r1
                    handle = f"@{username}"
                    row = found.setdefault(
                        handle.lower(),
                        {
                            "handle": handle,
                            "found_by": [],
                            "already_in_census": handle.lower() in seen,
                            "search": {
                                "title": getattr(chat, "title", None),
                                "subscribers": getattr(chat, "participants_count", None),
                                "telegram_verified": bool(getattr(chat, "verified", False)),
                                "broadcast": bool(getattr(chat, "broadcast", False)),
                                "megagroup": bool(getattr(chat, "megagroup", False)),
                            },
                        },
                    )
                    row["found_by"].append(f"poltava_discussion:{q}")
                    if not row["already_in_census"]:
                        fresh += 1
                print(f"  {q:<34}{len(result.chats):>3} hits · {fresh} new", flush=True)
                await asyncio.sleep(PAUSE_SECONDS)
        finally:
            await client.disconnect()

    new = [r for r in found.values() if not r["already_in_census"]]
    new.sort(key=lambda r: -(r["search"]["subscribers"] or 0))
    record = {
        "at": census.entry.stamp(),
        "authorised_by": AUTHORISED_BY,
        "terms": list(terms),
        "why": "CHAT_TERMS selects classifieds; this genre selects discussion",
        "budget": MAX_REQUESTS,
        "requests": calls["n"],
        "queries_run": ran,
        "flood_wait_seconds": flood,
        "found_total": len(found),
        "found_new": len(new),
        "rows": new,
    }
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if flood:
        census.record_the_wall(flood, census.entry.stamp(), len(ran))
    print(f"\n{calls['n']} requests · {len(ran)} queries · {len(found)} handles, {len(new)} NEW")
    for r in new[:25]:
        s = r["search"]
        kind = "group" if s["megagroup"] else "channel"
        print(
            f"  {r['handle']:<30}{str(s['subscribers'] or '—'):>7} {kind:<8}{str(s['title'])[:40]!r}"
        )
    print(f"wrote {OUT.relative_to(REPO_ROOT)}")
    return 1 if flood else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Search the discussion genre across the 24 centres.")
    p.add_argument("--terms", nargs="*", default=list(TERMS))
    p.add_argument("--towns", nargs="*", default=list(POLTAVA_TOWNS))
    p.add_argument("--plan", action="store_true")
    args = p.parse_args(argv)
    if args.plan:
        for term in args.terms:
            for town in args.towns:
                print(f"  {term} {town}")
        print(f"{len(args.terms) * len(args.towns)} queries")
        return 0
    return asyncio.run(run(tuple(args.terms), list(args.towns)))


if __name__ == "__main__":
    raise SystemExit(main())
