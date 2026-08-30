#!/usr/bin/env python3
"""C1 r2 step 2 — resolve ONLY the handles step 1 read off the chains' own sites.

The columns are r1's, computed by r1's code (`retail_census.check_one` → `census_stats` →
`census_verdict`): a column re-implemented here would silently drop r1's грн-vs-`grn` price
branches and its `media_share` saturation finding, and the two censuses would stop comparing.

What this run does NOT inherit from r1:
  · `entry.suggest` is off. On a failed resolve it fires `contacts.SearchRequest` — an extra
    request AND the exact instrument r1 was not accepted for (Dv871). A `"suggestions": []` in
    this record therefore means «not asked», never «asked and found nothing».
  · pacing is this script's own 3.0 s, not `entry_check.PAUSE_SECONDS` (2.0). The contract says
    ≥3 s; inheriting the module constant would have run the contract's floor at two thirds.

Budget: the ≤40 of the contract is enforced on MEASURED MTProto calls — every request the client
sends is counted by wrapping the client, so the ceiling binds on what Telegram actually saw.
Read-only: no joins. An invite hash goes through CheckChatInvite, which does not join either.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import entry_check as entry  # noqa: E402
import retail_census as census  # noqa: E402
from collect_5c1 import refuse_inside_flood_wait  # noqa: E402
from telethon import functions  # noqa: E402
from telethon.errors import FloodWaitError  # noqa: E402

RECORD = REPO_ROOT / "results" / "retail_chains.json"

PAUSE_SECONDS = 3.0
assert PAUSE_SECONDS >= 3.0, "the contract's floor is 3 s between requests"
MAX_REQUESTS = 40
# resolve + GetFullChannel + sample_traffic + census_sample. The contract says "one history
# request each"; r1's code path spends two, and keeping r1's code is what keeps the columns
# comparable — so the divergence is reserved for here and reported, not silently averaged.
COST_PER_CANDIDATE = 4

UTC = timezone.utc


def would_exceed(spent_before: int, spent_now: int) -> bool:
    """Would admitting one more candidate carry the run past the contract's ceiling?

    `spent_before` comes from the record's pass ledger, not from this process: the FloodWait the
    budget exists to avoid is account-wide, so a fresh invocation whose counter starts at 0 would
    otherwise spend the whole 40 again. A candidate costs up to COST_PER_CANDIDATE, so the check
    is against what the NEXT one can spend, not what the previous ones did.
    """
    return spent_before + spent_now + COST_PER_CANDIDATE > MAX_REQUESTS


@contextmanager
def suggest_disabled():
    """`entry.suggest` off, and the record is told how often it would have fired."""
    fired: list[str] = []
    original = entry.suggest

    async def _noop(client, name):
        fired.append(name)
        return []

    entry.suggest = _noop
    try:
        yield fired
    finally:
        entry.suggest = original


@contextmanager
def counting(client):
    """Count every MTProto request the client sends, so ≤40 binds on a measurement.

    Telethon dispatches `client(request)` through the class, not the instance, so the wrapper goes
    on the type. `get_entity` issues its ResolveUsername through the same path, which is what makes
    this a count of what Telegram saw rather than a count of what this script meant to send.
    """
    klass = type(client)
    original = klass.__call__
    counter = {"n": 0, "kinds": {}}

    def wrapper(self, request, *args, **kwargs):
        counter["n"] += 1
        name = type(request).__name__
        counter["kinds"][name] = counter["kinds"].get(name, 0) + 1
        return original(self, request, *args, **kwargs)

    klass.__call__ = wrapper
    try:
        yield counter
    finally:
        klass.__call__ = original


def targets(state: dict, *, resume: bool = False) -> list[dict]:
    """One entry per collectable handle step 1 found, in the record's own row order.

    `resume` drops handles this record already carries a measurement for. The smoke spends real
    requests against the same account-wide rate limit as the pass, so re-measuring it would put
    the smoke's cost inside the pass's budget twice over.
    """
    out = []
    for row in state["rows"]:
        seen = {m.get("handle") for m in row.get("measured", [])}
        for handle in row.get("resolvable", []):
            if resume and handle in seen:
                continue
            out.append({"name": row["name"], "handle": handle, "kind": row["kinds"][handle]})
    return out


async def measure_invite(client, token: str) -> dict:
    """A `+hash` is not a username. CheckChatInvite reads it WITHOUT joining.

    For a non-member Telegram returns a `ChatInvite` — a title and a participant count and no
    history at all. So an invite row cannot carry posts/day, price share or dairy share: those
    fields are `unmeasured`, which is not the same value as zero.
    """
    result = await client(functions.messages.CheckChatInviteRequest(hash=token.lstrip("+")))
    kind = type(result).__name__
    record = {"invite_result": kind, "handle": token}
    if kind in ("ChatInviteAlready", "ChatInvitePeek"):
        # Both carry a `chat`, not a `title` — reading them like the plain `ChatInvite` below
        # returns `title: null`, an empty field that reads as «Telegram told us nothing» when in
        # fact it told us the chat. `Peek` is a preview that expires; `Already` means membership.
        chat = result.chat
        record |= {
            "title": getattr(chat, "title", None),
            "subscribers": getattr(chat, "participants_count", None),
            "megagroup": bool(getattr(chat, "megagroup", False)),
            "history_readable": kind == "ChatInviteAlready",
            "peek_expires": getattr(result, "expires", None) and str(result.expires),
        }
    else:
        record |= {
            "title": getattr(result, "title", None),
            "subscribers": getattr(result, "participants_count", None),
            "megagroup": bool(getattr(result, "megagroup", False)),
            "history_readable": False,
            "why_unmeasured": (
                "CheckChatInvite returns a title and a member count and no messages; measuring"
                " posts/day, price share or comments/day would require joining, and this census"
                " is read-only (r1's rule, unchanged)"
            ),
        }
    return record


async def run(limit: int | None, resume: bool) -> int:
    refuse_inside_flood_wait()
    state = json.loads(RECORD.read_text(encoding="utf-8"))
    pending = targets(state, resume=resume)[: limit or None]
    if not pending:
        print("nothing resolvable in the record — run step 1 first")
        return 1
    print(
        f"{len(pending)} handles from step 1; budget {MAX_REQUESTS} requests, {PAUSE_SECONDS}s apart"
    )

    # The FloodWait this budget exists to avoid is account-wide, and so is the ledger: a fresh
    # invocation starts its own counter at 0, so a ceiling checked against it alone lets every new
    # pass spend the whole 40 again. Seed from what the record says was already spent.
    spent_before = sum(p["requests"] for p in state.get("step_2", {}).get("passes", []))
    if spent_before:
        print(f"{spent_before} requests already spent by earlier passes (record)")

    compiled = census.compile_categories(census.load_lexicon())
    now = datetime.now(UTC)
    by_name = {row["name"]: row for row in state["rows"]}
    client = census.build_client()
    await client.connect()
    flood, gaps, last, done = None, [], None, 0
    with counting(client) as calls, suggest_disabled() as suggested:
        try:
            if not await client.is_user_authorized():
                raise SystemExit("No Telegram session. Run: python3 scripts/tg_login.py")
            for n, target in enumerate(pending, 1):
                # One candidate costs up to COST_PER_CANDIDATE requests (resolve + full channel +
                # two histories). Checking the spent count alone would let the LAST candidate
                # carry the total past 40 — the ceiling has to be checked against what the next
                # candidate can still spend, not against what the previous ones did.
                if would_exceed(spent_before, calls["n"]):
                    print(
                        f"budget: {spent_before + calls['n']} spent, next needs "
                        f"{COST_PER_CANDIDATE} of {MAX_REQUESTS} — stopping with "
                        f"{len(pending) - n + 1} unmeasured"
                    )
                    break
                if last is not None:
                    gap = (datetime.now(UTC) - last).total_seconds()
                    gaps.append(round(gap, 2))
                print(
                    f"[{n}/{len(pending)}] {target['name']}: {target['handle']} "
                    f"({calls['n']} requests spent)",
                    flush=True,
                )
                row = by_name[target["name"]]
                try:
                    if target["kind"] == "invite":
                        measured = await measure_invite(client, target["handle"])
                    else:
                        pseudo = {
                            "handle": target["handle"],
                            "search": {"title": target["name"], "subscribers": None},
                        }
                        measured = await census.check_one(client, pseudo, now, compiled)
                except FloodWaitError as exc:
                    flood = exc.seconds
                    print(f"FloodWait: {exc.seconds}s — stopped, keeping {n - 1}")
                    break
                except Exception as exc:  # a handle that fails is a finding, not a crash
                    measured = {
                        "handle": target["handle"],
                        "resolved": False,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                measured["measured_by"] = "api (r2)"
                measured["window"] = (
                    f"{(now - timedelta(days=census.WINDOW_DAYS)).date()}..{now.date()}"
                )
                row.setdefault("measured", []).append(measured)
                done += 1
                RECORD.write_text(
                    json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )  # after EVERY handle: a kill mid-pass must not zero the run
                last = datetime.now(UTC)
                await asyncio.sleep(PAUSE_SECONDS)
        finally:
            await client.disconnect()

    # Each pass appends: the smoke's requests hit the SAME account-wide rate limit as the pass,
    # so a step_2 that only ever holds the last pass under-reports what Telegram was asked.
    passes = state.get("step_2", {}).get("passes", [])
    state["step_2"] = {
        "at": census.entry.stamp(),
        "handles_measured": done,
        "handles_left_unmeasured": len(pending) - done,
        "requests_measured": calls["n"],
        "requests_by_type": calls["kinds"],
        "budget": MAX_REQUESTS,
        "cost_per_candidate": COST_PER_CANDIDATE,
        "history_requests_per_candidate": 2,
        "budget_unit": "measured MTProto requests (client.__call__ wrapped), not candidates",
        "pause_seconds_intended": PAUSE_SECONDS,
        # Per pass, not one field: a later single-handle pass has no gap to measure and would
        # overwrite the number the multi-handle pass proved. The rows' own `checked_at` stamps are
        # the independent record — `tests/test_retail_resolve_pacing.py` derives the floor from them.
        "pause_seconds_measured_min": min(gaps) if gaps else None,
        "pause_source": "this script — entry_check.PAUSE_SECONDS is 2.0 and would break the floor",
        "suggest_disabled": True,
        "suggest_would_have_fired_for": suggested,
        "read_only": "no joins; an invite is read through CheckChatInvite, which does not join",
        "flood_wait_seconds": flood,
    }
    passes.append(
        {
            "at": state["step_2"]["at"],
            "handles_measured": done,
            "requests": calls["n"],
            "by_type": calls["kinds"],
            "pause_measured_min": min(gaps) if gaps else None,
            "gaps": gaps,
        }
    )
    state["step_2"]["passes"] = passes
    state["step_2"]["requests_all_passes"] = sum(p["requests"] for p in passes)
    RECORD.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if flood:
        census.record_the_wall(flood, census.entry.stamp(), done)
    print(f"\n{calls['n']} requests: {calls['kinds']}")
    print(f"min gap {min(gaps) if gaps else '—'}s · wrote {RECORD.relative_to(REPO_ROOT)}")
    return 1 if flood else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="C1 r2 step 2 — resolve step 1's handles.")
    p.add_argument("--limit", type=int, help="cap the handles this pass (the smoke)")
    p.add_argument("--resume", action="store_true", help="skip handles already measured")
    p.add_argument("--plan", action="store_true", help="print what would be resolved, no API")
    args = p.parse_args(argv)
    if args.plan:
        state = json.loads(RECORD.read_text(encoding="utf-8"))
        rows = targets(state, resume=args.resume)
        for t in rows:
            print(f"  {t['name']:24} {t['handle']:24} {t['kind']}")
        print(f"{len(rows)} handles · budget {MAX_REQUESTS} requests · {PAUSE_SECONDS}s apart")
        return 0
    return asyncio.run(run(args.limit, args.resume))


if __name__ == "__main__":
    raise SystemExit(main())
