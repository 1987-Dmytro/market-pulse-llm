#!/usr/bin/env python3
"""Join ONE private channel by its invite hash, log it, and measure what the join unlocked.

The first non-read-only action this census has taken. r1 and r2 were both «no joins», so this is
a change of kind, not of degree, and it is done the way the project already records membership:
every join, and every leave, is a row in `results/joins_5c1.jsonl` — the file that answers «what
is this account a member of». A membership created outside that log would make the log a lie
(`collect_5c1.leave_group`'s own words).

`collect_5c1.join_group` cannot do this one: it joins a channel's LINKED DISCUSSION GROUP by
handle, and Маркетопт's channel is a private invite with no username at all. The request is
`ImportChatInviteRequest`, not `JoinChannelRequest`.

REVERSIBLE: `--leave` sends `LeaveChannelRequest` and logs the reverse row, so the account can be
taken back out and the ledger still tells the truth.

AUTHORISATION (operator, 2026-08-30): «Вступай в канал маркет опт».
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
from collect_5c1 import log_join, refuse_inside_flood_wait  # noqa: E402
from telethon import functions  # noqa: E402
from telethon.errors import FloodWaitError, InviteRequestSentError  # noqa: E402

CHAINS = REPO_ROOT / "results" / "retail_chains.json"
UTC = timezone.utc
AUTHORISED_BY = "operator, 2026-08-30: «Вступай в канал маркет опт»"


def invite_of(name: str) -> str:
    """The invite this chain's row already carries — never a hash typed at the call site."""
    state = json.loads(CHAINS.read_text(encoding="utf-8"))
    row = next(r for r in state["rows"] if r["name"] == name)
    invites = [h for h in row.get("resolvable", []) if row["kinds"].get(h) == "invite"]
    if len(invites) != 1:
        raise SystemExit(f"{name}: expected exactly one invite, found {invites}")
    return invites[0]


async def run(name: str, leave: bool, force: bool) -> int:
    refuse_inside_flood_wait()
    token = invite_of(name)
    digest = token.lstrip("+")
    client = census.build_client()
    await client.connect()
    try:
        if not await client.is_user_authorized():
            raise SystemExit("No Telegram session. Run: python3 scripts/tg_login.py")

        # Look before joining: CheckChatInvite says what this is and whether we are already in.
        # A blind ImportChatInvite on a channel we already belong to spends a join-class request
        # for nothing, and joins are rate-limited harder than resolves.
        info = await client(functions.messages.CheckChatInviteRequest(hash=digest))
        kind = type(info).__name__
        title = getattr(info, "title", None) or getattr(getattr(info, "chat", None), "title", None)
        # `request_needed` is the flag that decides whether a join is a JOIN or only a REQUEST an
        # admin must approve. Reading it before sending is the difference between «we are in» and
        # «we are in a queue, and the chain can see who asked».
        needs_approval = bool(getattr(info, "request_needed", False))
        print(f"{name}: {kind} · {title!r} · request_needed={needs_approval}")

        row = {
            "at": datetime.now(UTC).isoformat(timespec="seconds"),
            "channel": token,
            "channel_title": title,
            "authorised_by": AUTHORISED_BY,
            "via": "ImportChatInviteRequest (private invite, no username)",
        }

        if leave:
            if kind != "ChatInviteAlready":
                log_join(row | {"outcome": "not_a_member", "note": "already out before this run"})
                print("not a member — nothing to leave")
                return 0
            await client(functions.channels.LeaveChannelRequest(channel=info.chat))
            after = await client(functions.messages.CheckChatInviteRequest(hash=digest))
            # Re-read rather than trust a request that did not raise — leave_group's rule.
            log_join(
                row
                | {
                    "outcome": "left",
                    "group_id": info.chat.id,
                    "verified_left": type(after).__name__ != "ChatInviteAlready",
                }
            )
            print("left, verified")
            return 0

        if kind == "ChatInviteAlready":
            log_join(row | {"outcome": "already_member", "group_id": info.chat.id})
            print("already a member — no join sent")
            chat = info.chat
        else:
            if needs_approval and not force:
                log_join(row | {"outcome": "approval_required", "note": "not sent; --force to ask"})
                print(
                    "this invite needs an ADMIN's approval: joining sends a request the chain's"
                    " admins see, and grants nothing until they accept. Re-run with --force to"
                    " send it."
                )
                return 0
            try:
                updates = await client(functions.messages.ImportChatInviteRequest(hash=digest))
            except InviteRequestSentError:
                # Not a failure and not a membership: the request is now pending with the chain's
                # admins. It MUST be logged — the request was really sent, and a ledger that only
                # records outright joins would say this account never asked.
                log_join(row | {"outcome": "join_requested", "note": "pending admin approval"})
                print(
                    "join REQUEST sent — pending the chain's approval. No membership, no history."
                )
                return 0
            except FloodWaitError as exc:
                census.record_the_wall(exc.seconds, census.entry.stamp(), 0)
                log_join(row | {"outcome": "floodwait", "seconds": exc.seconds})
                print(f"FloodWait on the JOIN: {exc.seconds}s — recorded, nothing joined")
                return 1
            chat = updates.chats[0]
            after = await client(functions.messages.CheckChatInviteRequest(hash=digest))
            log_join(
                row
                | {
                    "outcome": "joined",
                    "group_id": chat.id,
                    "group_title": getattr(chat, "title", None),
                    "verified_member": type(after).__name__ == "ChatInviteAlready",
                }
            )
            print(f"joined: {getattr(chat, 'title', None)!r} (id {chat.id})")

        # The point of joining: the columns that were `unmeasured` because history needed a member.
        now = datetime.now(UTC)
        compiled = census.compile_categories(census.load_lexicon())
        full = await client(functions.channels.GetFullChannelRequest(channel=chat))
        sample, truncated = await census.census_sample(client, chat, now)
        stats = census.census_stats(
            sample,
            truncated=truncated,
            is_group=bool(getattr(chat, "megagroup", False)),
            compiled=compiled,
        )
        linked = full.full_chat.linked_chat_id
        measured = {
            "handle": token,
            "resolved": True,
            "title": getattr(chat, "title", None),
            "subscribers": getattr(full.full_chat, "participants_count", None),
            "megagroup": bool(getattr(chat, "megagroup", False)),
            "comments_enabled": linked is not None,
            "discussion_group": {"present": linked is not None, "id": linked},
            "stats": stats,
            "measured_by": "api (r4, after joining)",
            "authorised_by": AUTHORISED_BY,
            "read_only": False,
            "window": f"{(now - census.timedelta(days=census.WINDOW_DAYS)).date()}..{now.date()}",
        }
        state = json.loads(CHAINS.read_text(encoding="utf-8"))
        target = next(r for r in state["rows"] if r["name"] == name)
        target.setdefault("measured", []).append(measured)
        CHAINS.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(
            f"measured: posts/day {stats.get('posts_per_day')} · price {stats.get('price_share')} "
            f"· dairy {stats.get('dairy_share')} · comments {linked is not None} "
            f"· lang {stats.get('language_mix')}"
        )
        return 0
    finally:
        await client.disconnect()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Join one private channel by invite, logged.")
    p.add_argument("--name", default="Маркетопт", help="the chain row whose invite to use")
    p.add_argument("--leave", action="store_true", help="the reverse: leave and log it")
    p.add_argument("--force", action="store_true", help="send a request that needs admin approval")
    p.add_argument("--plan", action="store_true", help="print what would be joined, no API")
    args = p.parse_args(argv)
    if args.plan:
        print(f"{args.name}: {invite_of(args.name)} · {AUTHORISED_BY}")
        return 0
    return asyncio.run(run(args.name, args.leave, args.force))


if __name__ == "__main__":
    raise SystemExit(main())
