#!/usr/bin/env python3
"""C1 r3 — the pass the operator authorised after the FloodWait cleared.

This is NOT step 2 with a bigger number. `docs/PROMPT-retail-census-r2.md` caps step 2 at ≤40
requests, that cap is spent (40/40), and `retail_resolve_r2.would_exceed` correctly refuses. A
contract's ceiling is not something the executor raises by editing a constant — so this pass gets
its OWN authorisation, its own ceiling and its own ledger, and step 2's «40 of 40» stays true.

AUTHORISATION, verbatim, 2026-08-30:
    «по райцентрам flood wait окончен продолжи сканирование каналов»
    «маркет опт оптовичек обязательно требуется добавить так как это локальный регион,
     проверь еще раз новус, епицентр фуд направление, метро, Ашан»
and, on the language bar: «Убрать планку, оставить колонкой».

Two tranches, in the operator's own order of value:
  A · the retail handles found on the chains' own official properties since step 2.
  B · the four district centres with NO chat at all — 7 candidates, taking coverage 18 → 22 of 24.
      Chosen over the other 81 unchecked because r1 hit a 23.7-hour wall after 200 checks, and
      that wall stops every phase, not this one.
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
from retail_chains_report import NOT_THE_CHAINS_CHANNEL  # noqa: E402
from retail_resolve_r2 import counting, measure_invite, suggest_disabled  # noqa: E402
from telethon.errors import FloodWaitError  # noqa: E402

CHAINS = REPO_ROOT / "results" / "retail_chains.json"
CENSUS = REPO_ROOT / "results" / "retail_census.json"

UTC = timezone.utc
PAUSE_SECONDS = 3.0
assert PAUSE_SECONDS >= 3.0, "keep r2's floor: the wall is account-wide and costs 23.7 h"
MAX_REQUESTS = 80  # this pass's own ceiling, not the contract's 40. r1 reached its
# wall after ~200 candidates; 11 at r2's measured 4.4 avg is ~48, so this leaves room
# for the 9-request worst case without a mid-run stop, and stays far from the wall.
COST_PER_CANDIDATE = 9  # r2 MEASURED 4..9; reserve the worst case, not the smoke's (Dv884)

AUTHORISED_BY = "operator, 2026-08-30: «flood wait окончен продолжи сканирование каналов»"

# The four district centres SPEC v2 §3 names that carry no chat at all, and whose candidates were
# found by r1 and never measured — the FloodWait stopped that pass, so this is buyable coverage.
EMPTY_TOWNS = ["Диканька", "Оржиця", "Козельщина", "Машівка"]


def stamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def retail_targets() -> list[dict]:
    """Handles in the chains record that still have no r3/r2 measurement."""
    state = json.loads(CHAINS.read_text(encoding="utf-8"))
    out = []
    for row in state["rows"]:
        seen = {m.get("handle") for m in row.get("measured", [])}
        # A handle the record already says belongs to ANOTHER brand is not worth a request:
        # `@bloom_cherkasy` is Delikat's group's florist, and measuring it would price a flower
        # shop's traffic as a grocery chain's.
        disowned = NOT_THE_CHAINS_CHANNEL.get(row["name"], set())
        for handle in row.get("resolvable", []):
            if handle not in seen and handle not in disowned:
                out.append({"name": row["name"], "handle": handle, "kind": row["kinds"][handle]})
    return out


def poltava_targets() -> list[dict]:
    """The unmeasured candidates of the four empty district centres, biggest first."""
    census_state = json.loads(CENSUS.read_text(encoding="utf-8"))
    out = []
    for row in census_state["rows"]:
        if row.get("checked"):
            continue
        towns = {
            f.split(":", 1)[1].rsplit(" ", 1)[0]
            for f in row.get("found_by", [])
            if f.startswith("poltava_chats:")
        }
        if towns & set(EMPTY_TOWNS):
            out.append({"row": row, "towns": sorted(towns & set(EMPTY_TOWNS))})
    out.sort(key=lambda t: -(t["row"]["search"].get("subscribers") or 0))
    return out


async def run(do_retail: bool, do_poltava: bool) -> int:
    refuse_inside_flood_wait()
    chains = json.loads(CHAINS.read_text(encoding="utf-8"))
    census_state = json.loads(CENSUS.read_text(encoding="utf-8"))
    chain_rows = {r["name"]: r for r in chains["rows"]}
    census_index = {r["handle"]: i for i, r in enumerate(census_state["rows"])}

    plan_a = retail_targets() if do_retail else []
    plan_b = poltava_targets() if do_poltava else []
    print(f"A: {len(plan_a)} retail handles · B: {len(plan_b)} Poltava candidates")
    print(f"ceiling {MAX_REQUESTS} measured requests, {PAUSE_SECONDS}s apart · {AUTHORISED_BY}")

    compiled = census.compile_categories(census.load_lexicon())
    now = datetime.now(UTC)
    client = census.build_client()
    await client.connect()
    flood, gaps, last, done_a, done_b = None, [], None, 0, 0

    async def pace():
        nonlocal last
        if last is not None:
            gaps.append(round((datetime.now(UTC) - last).total_seconds(), 2))
        last = datetime.now(UTC)

    with counting(client) as calls, suggest_disabled() as suggested:
        try:
            if not await client.is_user_authorized():
                raise SystemExit("No Telegram session. Run: python3 scripts/tg_login.py")

            for target in plan_a:
                if calls["n"] + COST_PER_CANDIDATE > MAX_REQUESTS:
                    print(f"ceiling: {calls['n']} spent, stopping tranche A")
                    break
                await pace()
                print(f"A {target['name']}: {target['handle']} ({calls['n']} spent)", flush=True)
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
                    print(f"FloodWait: {exc.seconds}s — stopped in tranche A")
                    break
                except Exception as exc:
                    measured = {
                        "handle": target["handle"],
                        "resolved": False,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                measured["measured_by"] = "api (r3)"
                measured["authorised_by"] = AUTHORISED_BY
                chain_rows[target["name"]].setdefault("measured", []).append(measured)
                CHAINS.write_text(
                    json.dumps(chains, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                done_a += 1
                await asyncio.sleep(PAUSE_SECONDS)

            for target in plan_b:
                if flood or calls["n"] + COST_PER_CANDIDATE > MAX_REQUESTS:
                    if not flood:
                        print(f"ceiling: {calls['n']} spent, stopping tranche B")
                    break
                row = target["row"]
                await pace()
                print(
                    f"B {'/'.join(target['towns'])}: {row['handle']} "
                    f"({row['search'].get('subscribers')} subs, {calls['n']} spent)",
                    flush=True,
                )
                try:
                    measured = await census.check_one(client, row, now, compiled)
                except FloodWaitError as exc:
                    flood = exc.seconds
                    print(f"FloodWait: {exc.seconds}s — stopped in tranche B")
                    break
                except Exception as exc:
                    measured = {
                        **row,
                        "checked": True,
                        "checked_at": census.entry.stamp(),
                        "measured_by": "api",
                        "resolved": False,
                        "stats": census.census_stats(
                            [], truncated=False, is_group=False, compiled=compiled
                        ),
                        "verdict": "reject",
                        "reasons": ["unexpected failure, see error"],
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                census_state["rows"][census_index[row["handle"]]] = measured
                CENSUS.write_text(
                    json.dumps(census_state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                done_b += 1
                await asyncio.sleep(PAUSE_SECONDS)
        finally:
            await client.disconnect()

    ledger = chains.setdefault("step_3", {"passes": []})
    ledger["authorised_by"] = AUTHORISED_BY
    ledger["budget"] = MAX_REQUESTS
    ledger["budget_note"] = (
        "a SEPARATE ceiling from the contract's ≤40, which step 2 spent in full; this pass does"
        " not raise that cap, it records a new authorisation beside it"
    )
    ledger["passes"].append(
        {
            "at": stamp(),
            "retail_measured": done_a,
            "poltava_measured": done_b,
            "requests": calls["n"],
            "by_type": calls["kinds"],
            "pause_measured_min": min(gaps) if gaps else None,
            "gaps": gaps,
            "suggest_would_have_fired_for": suggested,
            "flood_wait_seconds": flood,
        }
    )
    ledger["requests_all_passes"] = sum(p["requests"] for p in ledger["passes"])
    CHAINS.write_text(json.dumps(chains, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if flood:
        census.record_the_wall(flood, census.entry.stamp(), done_a + done_b)
    print(f"\n{calls['n']} requests: {calls['kinds']}")
    print(f"A {done_a} · B {done_b} · min gap {min(gaps) if gaps else '—'}s")
    return 1 if flood else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="C1 r3 — the operator-authorised scan.")
    p.add_argument("--plan", action="store_true", help="print both tranches, no API")
    p.add_argument("--retail-only", action="store_true")
    p.add_argument("--poltava-only", action="store_true")
    args = p.parse_args(argv)
    if args.plan:
        for t in retail_targets():
            print(f"  A  {t['name']:<28}{t['handle']:<26}{t['kind']}")
        for t in poltava_targets():
            r = t["row"]
            print(
                f"  B  {'/'.join(t['towns']):<28}{r['handle']:<26}"
                f"{r['search'].get('subscribers')} subs · {str(r['search'].get('title'))[:30]!r}"
            )
        return 0
    return asyncio.run(run(do_retail=not args.poltava_only, do_poltava=not args.retail_only))


if __name__ == "__main__":
    raise SystemExit(main())
