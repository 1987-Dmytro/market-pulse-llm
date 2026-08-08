#!/usr/bin/env python3
"""5c1 day-2 step 9: Telegram's own "similar channels" for the mothers/baby seeds ($0, read-only).

The launch `mothers_kids` segment is EMPTY after wave 3, and the operator's web pass measured why:
the open web does not hand back the top UA niches of Telegram — only instruments inside Telegram
do (canon `docs/CHANNELS-launch.md`, «Дозаявка №8»). `channels.getChannelRecommendations` is the
free one, so this asks it of the three seeds the brief names and writes what came back.

It is a CANDIDATE LIST and nothing else. PROMPT-5c1-day2's amendment-3.12 rider says it in the
brief's own words: "Step 9's harvest output is candidates only — its entries reach the registry,
as every candidate now does, only through the gate PLUS the 3.12 yield floor." So: no registry
write, no join, no verdict. Rows already spoken for (registry sources, anything the 5c1 gate
measured) are marked `known` rather than dropped — a seed recommending channels we already hold
is a fact about the seed, and a silently shortened list cannot be told from a short answer.

    PYTHONPATH=src python3 scripts/harvest_similar_5c1.py --plan
    PYTHONPATH=src python3 scripts/harvest_similar_5c1.py
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

import entry_check  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from late_batch_5c1 import known_handles  # noqa: E402
from telethon import functions  # noqa: E402
from telethon.errors import FloodWaitError  # noqa: E402

from market_pulse.telegram_client import build_client  # noqa: E402

RECORD = REPO_ROOT / "results" / "harvest_mothers_ua.json"

SEEDS = ("@ya_Nenka", "@tarilka_malyuka", "@blwbabies")
"""The brief's three, in its order. All three are baby_food/mothers sources this phase gated, so
what Telegram considers "similar" to them is the nearest thing to a segment catalogue we can read
for free. @tarilka_malyuka is a member group as well, which changes nothing here — this call
reads the CHANNEL."""

CANON = (
    "docs/PROMPT-5c1-day2.md step 9; canon docs/CHANNELS-launch.md «Дозаявка №8» — «открытый веб"
    " не отдаёт топы UA-ниш Telegram — их отдают только инструменты внутри Telegram»"
)


def chat_row(chat) -> dict:
    """One recommended channel, in `entry_check.suggest`'s shape so both feed the same reading."""
    return {
        "handle": f"@{chat.username}" if getattr(chat, "username", None) else None,
        "title": getattr(chat, "title", None),
        "subscribers": getattr(chat, "participants_count", None),
        "telegram_verified": bool(getattr(chat, "verified", False)),
        # A recommendation can be a chat, and a chat is not a source this project collects — the
        # day-2 sitting excluded three of them. Carried per row so the reader never has to guess.
        "broadcast": bool(getattr(chat, "broadcast", False)),
        "megagroup": bool(getattr(chat, "megagroup", False)),
    }


async def recommendations(client, seed: str, known: dict) -> dict:
    entity = await client.get_entity(seed)
    result = await client(functions.channels.GetChannelRecommendationsRequest(channel=entity))
    rows = [chat_row(chat) for chat in result.chats]
    for row in rows:
        row["known"] = known.get((row["handle"] or "").lower())
    return {
        "seed": seed,
        "asked_at": datetime.now(UTC).isoformat(timespec="seconds"),
        # `ChatsSlice` carries a total the returned list is a slice of; `Chats` does not.
        "returned": len(rows),
        "count_upstream": getattr(result, "count", None),
        "rows": rows,
    }


def render(seeds: list[dict]) -> str:
    lines = []
    for found in seeds:
        fresh = [r for r in found["rows"] if not r["known"]]
        lines.append(
            f"\n{found['seed']}: {found['returned']} recommended, {len(fresh)} not already ours"
        )
        for row in found["rows"]:
            kind = "channel" if row["broadcast"] else ("chat" if row["megagroup"] else "?")
            mark = f"  [{row['known']}]" if row["known"] else ""
            lines.append(
                f"  {str(row['handle']):<28}{(row['subscribers'] or 0):>8}  {kind:<8}"
                f"{str(row['title'])[:34]}{mark}"
            )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="5c1 day-2 step 9: Telegram similar channels.")
    parser.add_argument("--plan", action="store_true", help="print the seeds and stop, no API")
    args = parser.parse_args(argv)

    known = known_handles()
    print(f"seeds: {', '.join(SEEDS)}")
    print(f"known: {len(known)} handles already spoken for — marked, never dropped")
    if args.plan:
        return 0

    async def run():
        client = build_client()
        await client.connect()
        try:
            if not await client.is_user_authorized():
                raise SystemExit("No Telegram session. Run: python3 scripts/tg_login.py")
            found, flood_wait = [], None
            for seed in SEEDS:
                try:
                    found.append(await recommendations(client, seed, known))
                except FloodWaitError as exc:
                    # Every seed costs a ResolveUsernameRequest, the limit that cost this account
                    # 20 hours on 2026-08-07. Keep what was answered and stop.
                    flood_wait = exc.seconds
                    print(f"FloodWait {exc.seconds}s on {seed} — stopping, {len(found)} done")
                    break
                await asyncio.sleep(entry_check.PAUSE_SECONDS)
            return found, flood_wait
        finally:
            await client.disconnect()

    seeds, flood_wait = asyncio.run(run())
    fresh = {row["handle"]: row for found in seeds for row in found["rows"] if not row["known"]}
    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "5c1",
        "step": "day-2 step 9 — harvest similar-channels (mothers UA)",
        "contract": CANON,
        "instrument": "channels.getChannelRecommendations (free; SPEC §3.11 amendment 3.12 (2))",
        "status": (
            "CANDIDATES ONLY. Nothing here enters config/registry.yaml from this file: a row"
            " reaches the registry through the track-R gate PLUS the 3.12 yield floor, and the"
            " operator signs the launch verdict after that. No join, no verdict, no write."
        ),
        "seeds": seeds,
        "flood_wait_seconds": flood_wait,
        "summary": {
            "seeds_asked": len(seeds),
            "rows_returned": sum(found["returned"] for found in seeds),
            "distinct_not_already_ours": len(fresh),
            "broadcast_channels_among_them": sum(1 for row in fresh.values() if row["broadcast"]),
        },
        "git": git_state(RECORD),
    }
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(render(seeds))
    print(f"\n{record['summary']}")
    print(f"record: {RECORD.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
