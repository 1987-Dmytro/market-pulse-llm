#!/usr/bin/env python3
"""Block 2 — does anyone in the Poltava chats actually NAME a dairy brand?

The operator's question is «где мы сможем искать информацию непосредственно про Гармонію и другие
молочні бренди». The census answers a neighbouring question — `dairy_share`, a lexicon match on the
CATEGORY (молоко, сир, йогурт) — and the two are not the same: a chat can talk about milk every day
and never name a brand. Across the 16 324 comments already collected the watchlist is named 228
times, 198 of them `varus-pl` in Varus's own channel, and Гармонія **zero** — which is SPEC v2 §0's
own finding. But `data/raw/` holds the 66 REGISTRY channels; not one Poltava chat has ever been
collected, so for these the question is untested rather than answered.

This probe tests it before any wider scan: the chats are public groups, so their history reads
without joining — the same read the census already did — and the only new thing is running the
watchlist matcher over the text instead of the category lexicon.

Its own ceiling and its own ledger, beside step_2's contract cap and step_3's authorisation
(Dv894): a new purpose is a new budget line, never a bigger number in an old one.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import retail_census as census  # noqa: E402
from collect_5c1 import refuse_inside_flood_wait  # noqa: E402
from market_pulse import brands  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402
from retail_resolve_r2 import counting, suggest_disabled  # noqa: E402
from retail_working_set import poltava_rows, towns_of  # noqa: E402
from telethon.errors import FloodWaitError  # noqa: E402

OUT = REPO_ROOT / "results" / "poltava_brand_probe.json"
UTC = timezone.utc
PAUSE_SECONDS = 3.0
assert PAUSE_SECONDS >= 3.0, "the wall is account-wide and costs 23.7 h"
MAX_REQUESTS = 60
COST_PER_CANDIDATE = 9  # r2 measured 4..9; reserve the worst case (Dv884)
AUTHORISED_BY = (
    "operator, 2026-08-30: «нам надо покрыть все двадцать четыре районных центра и найти в них"
    " те телеграм-каналы, где идут живые обсуждения... где мы сможем искать информацию"
    " непосредственно про гармонию и другие молочные бренды»"
)


def targets(limit: int) -> list[dict]:
    """The liveliest chats first: a brand is named where people talk, not where they could."""
    chats = poltava_rows()
    chats.sort(key=lambda c: -((c.get("stats") or {}).get("messages_per_day") or 0))
    return chats[:limit]


async def run(limit: int) -> int:
    refuse_inside_flood_wait()
    reg = load_registry(REPO_ROOT / "config" / "registry.yaml")
    rules = brands.load_watchlist_rules(brands.RULES)
    aliases = brands.watchlist_aliases(reg.watchlist)
    compiled = census.compile_categories(census.load_lexicon())

    plan = targets(limit)
    print(f"{len(plan)} chats · ceiling {MAX_REQUESTS} requests · {PAUSE_SECONDS}s apart")
    now = datetime.now(UTC)
    client = census.build_client()
    await client.connect()
    results, flood, gaps, last = [], None, [], None
    with counting(client) as calls, suggest_disabled():
        try:
            if not await client.is_user_authorized():
                raise SystemExit("No Telegram session. Run: python3 scripts/tg_login.py")
            for chat in plan:
                if calls["n"] + COST_PER_CANDIDATE > MAX_REQUESTS:
                    print(
                        f"ceiling: {calls['n']} spent, stopping with {len(plan) - len(results)} left"
                    )
                    break
                if last is not None:
                    gaps.append(round((datetime.now(UTC) - last).total_seconds(), 2))
                last = datetime.now(UTC)
                handle = chat["handle"]
                print(f"{handle} ({calls['n']} spent)", flush=True)
                try:
                    entity = await client.get_entity(handle)
                    sample, truncated = await census.census_sample(client, entity, now)
                except FloodWaitError as exc:
                    flood = exc.seconds
                    print(f"FloodWait: {exc.seconds}s — stopped")
                    break
                except Exception as exc:
                    results.append({"handle": handle, "error": f"{type(exc).__name__}: {exc}"})
                    continue
                texts = [(r.get("text") or "") for r in sample]
                texts = [t for t in texts if t]
                hits: dict[str, int] = {}
                examples: dict[str, list[str]] = {}
                for text in texts:
                    for f in brands.find_watchlist_brands(text, aliases, rules, carrier="comment"):
                        bid = f["brand_id"]
                        hits[bid] = hits.get(bid, 0) + 1
                        if len(examples.setdefault(bid, [])) < 3:
                            examples[bid].append(text[:160])
                stats = census.census_stats(
                    sample, truncated=truncated, is_group=True, compiled=compiled
                )
                results.append(
                    {
                        "handle": handle,
                        "title": chat.get("title"),
                        "towns": towns_of(chat),
                        "subscribers": chat.get("subscribers"),
                        "n_texts": len(texts),
                        "messages_per_day": stats.get("messages_per_day"),
                        "dairy_share": stats.get("dairy_share"),
                        "brand_hits": dict(sorted(hits.items(), key=lambda kv: -kv[1])),
                        "brand_examples": examples,
                        "measured_by": "api (probe)",
                    }
                )
                print(
                    f"   {len(texts)} текстов · молочка {stats.get('dairy_share')} · бренды {hits or '—'}"
                )
                await asyncio.sleep(PAUSE_SECONDS)
        finally:
            await client.disconnect()

    grand: dict[str, int] = {}
    for r in results:
        for bid, n in (r.get("brand_hits") or {}).items():
            grand[bid] = grand.get(bid, 0) + n
    record = {
        "at": census.entry.stamp(),
        "authorised_by": AUTHORISED_BY,
        "budget": MAX_REQUESTS,
        "requests": calls["n"],
        "pause_measured_min": min(gaps) if gaps else None,
        "flood_wait_seconds": flood,
        "chats_probed": len(results),
        "texts_read": sum(r.get("n_texts", 0) for r in results),
        "brand_hits_total": dict(sorted(grand.items(), key=lambda kv: -kv[1])),
        "garmonija": grand.get("garmonija", 0),
        "rows": results,
    }
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if flood:
        census.record_the_wall(flood, census.entry.stamp(), len(results))
    print(f"\n{calls['n']} requests · {record['texts_read']} текстов прочитано")
    print(f"бренды watchlist: {record['brand_hits_total'] or '— ни одного'}")
    print(f"ГАРМОНІЯ: {record['garmonija']}")
    print(f"wrote {OUT.relative_to(REPO_ROOT)}")
    return 1 if flood else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Block 2 — brand mentions in the liveliest chats.")
    p.add_argument("--limit", type=int, default=12)
    p.add_argument("--plan", action="store_true")
    args = p.parse_args(argv)
    if args.plan:
        for c in targets(args.limit):
            s = c.get("stats") or {}
            print(
                f"  {c['handle']:<32}{','.join(towns_of(c))[:16]:<18}"
                f"{s.get('messages_per_day')} msgs/d · dairy {s.get('dairy_share')}"
            )
        return 0
    return asyncio.run(run(args.limit))


if __name__ == "__main__":
    raise SystemExit(main())
