#!/usr/bin/env python3
"""Phase-2b channel entry check (docs/SPEC.md §2, §8).

For every candidate handle in config/registry.yaml: does the channel exist, is it
the blue-check one, are comments enabled, does it carry traffic? Writes
data/entry_check_report.json (gitignored raw data) and prints the table the
operator reviews before flipping `verified:` in the registry — this script never
edits the registry itself.

`--discover "<query>"` runs the same check over Telegram's global search instead of
the registry: SPEC §9 falls back to aggregator and community channels wherever a
chain has comments disabled, and this is how those candidates are found.

`--gate-5c1` runs the track-R entry gate over the 62 candidates of the operator's
launch composition (`docs/CHANNELS-launch.md`, verdict 2026-08-06) and writes
`results/entry_gate_5c1.json`. The composition choice is already made; the gate
VERIFIES each entry against the bucket it was chosen into, before any of it
reaches `config/registry.yaml`. Read-only like the rest of this file: no joins,
no store writes, and the registry is not edited here either.

Read-only and deliberately slow: one channel at a time, a pause between channels,
no joins, no member lists. FloodWait aborts the run but keeps what was collected.

    python3.11 scripts/tg_login.py     # once, to create the session
    python3.11 scripts/entry_check.py
    python3.11 scripts/entry_check.py --discover "молочні продукти"
    PYTHONPATH=src python3 scripts/entry_check.py --gate-5c1
    PYTHONPATH=src python3 scripts/entry_check.py --gate-5c1 --only @forainfo @tadaua
"""

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling scripts, imported deferred

from telethon import functions, types
from telethon.errors import (
    ChannelPrivateError,
    FloodWaitError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
)

from market_pulse.entry_check import (
    BUCKETS,
    GATE_CYRILLIC_MIN,
    GATE_MIN_LETTERED_TEXTS,
    PRE_REGISTERED_FLAGS,
    build_verdict,
    collapse_albums,
    gate_verdict,
    script_mix,
    traffic_stats,
)
from market_pulse.registry import Source, load_registry
from market_pulse.telegram_client import build_client

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
DATA_DIR = REPO_ROOT / "data"
RESULTS_DIR = REPO_ROOT / "results"
GATE_RECORD = RESULTS_DIR / "entry_gate_5c1.json"
PRIOR_SCAN = RESULTS_DIR / "discovery_5a1.json"
POST_SAMPLE = 50
PAUSE_SECONDS = 2.0
DISCOVER_LIMIT = 15
RESOLVE_ERRORS = (UsernameNotOccupiedError, UsernameInvalidError, ChannelPrivateError, ValueError)

CANDIDATES = (
    # docs/CHANNELS-launch.md — the operator's verdict of 2026-08-06 plus the same evening's
    # addition, copied handle for handle and held to it by tests/test_entry_gate_5c1.py: this
    # tuple and the canon's tables must name the same channels in the same buckets, or the run
    # is gating a composition nobody chose.
    ("@tretyakovaele", "comments"),
    ("@kopiyochka1", "comments"),
    ("@klopotenkofood", "comments"),
    ("@maudau", "comments"),
    ("@uasaler", "comments"),
    ("@retsepty", "comments"),
    ("@katyal55", "comments"),
    ("@smirnov108", "comments"),
    ("@tarilka_malyuka", "comments"),
    ("@kkondr_fit", "comments"),
    ("@polyakova_fitness", "comments"),
    ("@znishkom", "comments"),
    ("@kuksa2022", "comments"),
    ("@HealthPsycholog", "comments"),
    ("@ATB_FANatik", "comments"),
    ("@offspringrus", "comments"),
    ("@sashafitnesslife", "comments"),
    ("@Pro_Detyintumama", "comments"),
    ("@chifit_family", "comments"),
    ("@ya_Nenka", "comments"),
    ("@baby_broccoli_club", "comments"),
    ("@useful_healthy_fitness_menu", "comments"),
    ("@olgaa_trainer", "comments"),
    ("@kolyastravinsky", "comments"),
    ("@whowears", "comments"),
    ("@denisovapro", "comments"),
    ("@eftforhealth", "comments"),
    ("@rezeptmoi", "comments"),
    ("@discountua1", "comments"),
    ("@recepti", "posts"),
    ("@mameni_recepti", "posts"),
    ("@retsepty4", "posts"),
    ("@epicentrk_sale", "posts"),
    ("@konservacia_kulinaria", "posts"),
    ("@intensiv_Mamiev", "posts"),
    ("@Mambabyua", "posts"),
    ("@retsepty5", "posts"),
    ("@blwbabies", "posts"),
    ("@vylkachannel", "posts"),
    ("@whitecode_zny", "posts"),
    ("@gaid_skobioale", "posts"),
    ("@dpssgovua", "posts"),
    ("@kulinariya_chat_a", "posts"),
    ("@Wellosophy_Lesya", "posts"),
    ("@atb_aktsiyi", "posts"),
    ("@anastasiiadavydiukfitness", "posts"),
    ("@korolevakuchni", "posts"),
    ("@itsmamix", "watch"),
    ("@regina_tatlybaeva", "watch"),
    ("@netainaya_vecherya", "watch"),
    ("@retsepty10", "watch"),
    ("@skhudnennya", "watch"),
    ("@prostetsofa", "watch"),
    ("@viktoria_sshh", "watch"),
    ("@hydnem_prosto", "watch"),
    ("@dimakaminskyifit", "watch"),
    ("@dutyache_menu", "watch"),
    ("@polinalykovagv", "watch"),
    ("@Evgenija_dutjache_menu", "watch"),
    ("@chekh_yevheniia1982", "watch"),
    ("@cozymotherhood", "watch"),
    ("@marketopt_official", "late"),
    # Ruling 2026-08-07: the late addition was withdrawn — @marketopt_official's handle resolves
    # to a dead 132-subscriber channel — and @marketopt_promo replaces it on the same gate. This
    # list is the gate's INPUT and only grows: what the operator ruled afterwards is
    # scripts/apply_gate_rulings_5c1.py's business, not a rewrite of what was measured.
    ("@marketopt_promo", "late"),
    # Late addition #2 (canon "Дозаявка №2", operator 2026-08-07 evening): a Poltava deals
    # aggregator, sent to this gate on the same terms.
    ("@akcii_skidki_plt", "late"),
    # "Дозаявка №3" (operator 2026-08-08): the city feeds picked out of the 119-candidate Poltava
    # scan. The canon lists them in prose rather than a table, and the derivation in
    # tests/test_entry_gate_5c1.py reads that list, so this stays the canon's own order.
    ("@mo3ambik", "city"),
    ("@poltava_informue", "city"),
    ("@poltava_misto", "city"),
    ("@suspilnepoltava", "city"),
    ("@telegraf_kremenchuk", "city"),
    ("@kremenchug_live", "city"),
    ("@gorishnie_plavni1", "city"),
    ("@myrhorodtown", "city"),
    ("@Hadiach_telegram", "city"),
    ("@globine1", "city"),
    ("@piryatingromada", "city"),
    ("@Karlivka_live", "city"),
    ("@PirOperative", "city"),
    ("@dikankaa", "city"),
    ("@zinkivnews", "city"),
    ("@LHVC_info", "city"),
    # "Дозаявка №5" (canon "МАСТЕР-ЛИСТ", operator 2026-08-08): the national chains the
    # retail_official segment is still missing. `late`, not `posts`, because their class is not
    # settled in advance — the operator's word is "comments per the group finding", which is what
    # the late-addition rule already says: PASS with an open group → comments, PASS without → posts.
    ("@forainfo", "late"),
    ("@ekomarket_shop", "late"),
    ("@tadaua", "late"),
    # "Дозаявка №8" (canon, 2026-08-08 evening — the operator's own TGStat pass in Chrome). Six
    # public UA candidates, `late` for the same reason as the three above: their class is not
    # settled in advance. Two of them arrive with the canon saying the THEME is the gate's to
    # decide («тематику решит гейт» for @pavlushaiyava, «тематику/язык решат гейт и перепись» for
    # @mandziak), so the segments in PROMPT-5c1-day2 are expectations, not findings.
    # In the CANON's order, which is not the brief's: PROMPT-5c1-day2 groups them by expected
    # segment, the canon lists them as it found them, and the list is the canon's.
    ("@tvorcha_matusyua", "late"),
    ("@mamaiagolodniy", "late"),
    ("@educationwithloven", "late"),
    ("@pavlushaiyava", "late"),
    ("@lab_of_childhood", "late"),
    ("@mandziak", "late"),
)


async def suggest(client, name: str) -> list[dict]:
    """Global search fallback for a handle that does not resolve, verified first."""
    found = await client(functions.contacts.SearchRequest(q=name, limit=10))
    matches = [
        {
            "title": chat.title,
            "username": getattr(chat, "username", None),
            "telegram_verified": bool(getattr(chat, "verified", False)),
            "subscribers": getattr(chat, "participants_count", None),
        }
        for chat in found.chats
        if getattr(chat, "username", None)
    ]
    matches.sort(key=lambda m: not m["telegram_verified"])
    return matches


async def sample_traffic(client, entity) -> dict:
    """Traffic over the last POST_SAMPLE posts.

    The comment count comes from each post's reply counter rather than from reading
    the linked group: it is the same number for one request instead of N, and it
    needs no join (SPEC §9 — conservative limits).
    """
    messages = await client.get_messages(entity, limit=POST_SAMPLE)
    samples = [
        (
            m.date,
            m.replies.replies if m.replies else None,
            m.grouped_id,
            m.action is not None,
        )
        for m in messages
    ]
    return traffic_stats(collapse_albums(samples))


def group_facts(chats, linked_chat_id: int) -> dict:
    """What the linked discussion group looks like from outside, without joining it.

    `GetFullChannelRequest` already returns the linked chat in its `chats` list, so this costs
    no extra request and no membership. "Open" is about whether the join Deliverable 2 would
    make can land and produce comments: approval-gated, Telegram-restricted, or a group where
    everyone is banned from sending are all closed for that purpose. A `min` object carries
    flags Telegram did not fill in — recorded rather than read as False.
    """
    chat = next((c for c in chats if getattr(c, "id", None) == linked_chat_id), None)
    if chat is None:
        return {"present": True, "read": False, "open": None, "closed_because": ["not returned"]}

    banned = getattr(chat, "default_banned_rights", None)
    closed = []
    if getattr(chat, "join_request", False):
        closed.append("join needs admin approval")
    if getattr(chat, "restricted", False):
        closed.append("Telegram-restricted")
    if banned is not None and getattr(banned, "send_messages", False):
        closed.append("everyone banned from sending")
    return {
        "present": True,
        "read": True,
        "id": chat.id,
        "title": getattr(chat, "title", None),
        "username": getattr(chat, "username", None),
        "megagroup": bool(getattr(chat, "megagroup", False)),
        "min": bool(getattr(chat, "min", False)),
        "join_request": bool(getattr(chat, "join_request", False)),
        "join_to_send": bool(getattr(chat, "join_to_send", False)),
        "restricted": bool(getattr(chat, "restricted", False)),
        # `left` is about the collector account: a group it is already in needs no join.
        "already_member": not getattr(chat, "left", True),
        "participants_count": getattr(chat, "participants_count", None),
        "open": not closed,
        "closed_because": closed,
    }


async def check_channel(client, source, handle: str) -> dict:
    record = {
        "source_id": source.id,
        "source_name": source.name,
        "source_type": source.source_type,
        "handle": handle,
    }

    try:
        entity = await client.get_entity(handle)
    except RESOLVE_ERRORS as exc:
        record["resolved"] = False
        record["error"] = f"{type(exc).__name__}: {exc}"
        record["suggestions"] = await suggest(client, source.name)
        return record | build_verdict(
            resolved=False,
            telegram_verified=False,
            scam=False,
            fake=False,
            comments_enabled=False,
            stats={},
        )

    if not isinstance(entity, types.Channel):
        record["resolved"] = False
        record["error"] = f"resolves to {type(entity).__name__}, not a channel"
        record["suggestions"] = await suggest(client, source.name)
        return record | {"verdict": "rejected", "reasons": [record["error"]]}

    result = await client(functions.channels.GetFullChannelRequest(channel=entity))
    full = result.full_chat
    stats = await sample_traffic(client, entity)
    record |= {
        "resolved": True,
        "title": entity.title,
        "username": entity.username,
        "telegram_verified": bool(entity.verified),
        # A supergroup resolves as a Channel too — record which one it really is.
        "broadcast": bool(entity.broadcast),
        "megagroup": bool(entity.megagroup),
        "scam": bool(entity.scam),
        "fake": bool(entity.fake),
        "subscribers": full.participants_count,
        "discussion_group_id": full.linked_chat_id,
        "comments_enabled": full.linked_chat_id is not None,
        "discussion_group": (
            group_facts(result.chats, full.linked_chat_id) if full.linked_chat_id else None
        ),
        "traffic": stats,
    }
    return record | build_verdict(
        resolved=True,
        telegram_verified=record["telegram_verified"],
        scam=record["scam"],
        fake=record["fake"],
        comments_enabled=record["comments_enabled"],
        stats=stats,
        broadcast=record["broadcast"],
    )


def cell(value, width: int) -> str:
    text = "—" if value is None else str(value)
    # width - 1 keeps at least one space between columns.
    text = text if len(text) < width else text[: width - 2] + "…"
    return text.ljust(width)


def print_table(records: list[dict]) -> None:
    header = (
        f"{'source':<11}{'handle':<22}{'title':<24}{'blue':<5}"
        f"{'subs':<9}{'comm':<6}{'posts/d':<9}{'%comm':<7}{'med':<5}verdict"
    )
    print(f"\n{header}\n{'-' * len(header)}")
    for r in records:
        traffic = r.get("traffic", {})
        print(
            cell(r["source_id"], 11)
            + cell(r["handle"], 22)
            + cell(r.get("title"), 24)
            + cell("yes" if r.get("telegram_verified") else "no", 5)
            + cell(r.get("subscribers"), 9)
            + cell("yes" if r.get("comments_enabled") else "no", 6)
            + cell(traffic.get("posts_per_day"), 9)
            + cell(traffic.get("share_with_comments"), 7)
            + cell(traffic.get("median_comments"), 5)
            + r["verdict"]
        )
        for reason in r.get("reasons", []):
            print(f"{'':<11}  ! {reason}")
        for match in r.get("suggestions", [])[:5]:
            check = "✓" if match["telegram_verified"] else " "
            print(f"{'':<11}  ? @{match['username']} {check} {match['title']}")


async def collect(client, candidates: list[tuple[Source, str]], records: list[dict]) -> int | None:
    """Check every (source, handle) pair, appending records. Returns FloodWait seconds."""
    for source, handle in candidates:
        print(f"checking {handle} ({source.id})...", flush=True)
        try:
            records.append(await check_channel(client, source, handle))
        except FloodWaitError as exc:
            return exc.seconds
        except Exception as exc:
            # One unusable channel must not discard the rest of the run.
            records.append(
                {
                    "source_id": source.id,
                    "source_name": source.name,
                    "source_type": source.source_type,
                    "handle": handle,
                    "resolved": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "verdict": "error",
                    "reasons": ["unexpected failure, see error"],
                }
            )
        await asyncio.sleep(PAUSE_SECONDS)
    return None


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def gate_row(
    handle: str, bucket: str, record: dict, window: dict, script: dict, prior: dict
) -> dict:
    """One candidate's row: what was measured, what the bucket expected, and the verdict."""
    traffic = record.get("traffic") or {}
    verdict = gate_verdict(
        handle=handle, bucket=bucket, record=record, window=window, script=script
    )
    return {
        "handle": handle,
        "bucket": bucket,
        "checked_at": stamp(),
        "checks": {
            "resolved": bool(record.get("resolved")),
            "title": record.get("title"),
            "username": record.get("username"),
            "subscribers": record.get("subscribers"),
            "telegram_verified": record.get("telegram_verified"),
            "broadcast": record.get("broadcast"),
            "megagroup": record.get("megagroup"),
            "scam": record.get("scam"),
            "fake": record.get("fake"),
            "liveness": {
                "n_posts": window.get("n_posts"),
                "posts_per_week": window.get("posts_per_week"),
                "last_post": window.get("last_post"),
                "window_days": window.get("window_days"),
                "window_truncated": window.get("window_truncated"),
            },
            "language": {**script, "detect_mix": window.get("language_mix")},
            "discussion_group": record.get("discussion_group"),
            "comments": {
                "post_sample": POST_SAMPLE,
                "n_posts_sampled": traffic.get("n_posts"),
                "share_with_comments": traffic.get("share_with_comments"),
                "median_comments": traffic.get("median_comments"),
                # The sample reaches back as far as POST_SAMPLE posts take it, so for a channel
                # the 28-day window finds empty these two dates are the only evidence of WHEN it
                # went quiet — and "dead" without a date is a verdict the operator cannot check.
                "sample_first_post": traffic.get("first_post"),
                "sample_last_post": traffic.get("last_post"),
            },
            # build_verdict's word on CAPABILITY, kept beside the gate's word on ENTRY.
            "capability_verdict": record.get("verdict"),
        },
        "prior_5a1": prior.get(handle.lower()),
        "verdict": verdict["verdict"],
        "fails": verdict["fails"],
        "flags": verdict["flags"],
        # Filled from the operator's dictated verdicts after the gate-report STOP.
        "ruling": None,
        "error": record.get("error"),
        "suggestions": record.get("suggestions") or None,
    }


async def gate_batch(client, candidates, prior: dict, records: list[dict]) -> int | None:
    """Run the track-R gate over a bucketed handle list. Returns FloodWait seconds.

    Read-only throughout: resolve, one full-channel request, the 50-post traffic sample and the
    four-week history window. No join, no member list, no store write, no registry edit.
    """
    # Deferred on purpose: discover_channels imports THIS module at its top, and the four-week
    # window belongs to it — the gate's posts/week is the same function that produced the
    # canon's п/нед column, not a second implementation of it.
    import discover_channels as discovery

    now = datetime.now(timezone.utc)
    for handle, bucket in candidates:
        print(f"gate {handle} ({bucket})...", flush=True)
        source = Source(bucket, handle, "community", (handle,))
        try:
            record = await check_channel(client, source, handle)
            samples, texts, truncated = [], [], False
            if record.get("resolved"):
                entity = await client.get_entity(handle)
                samples, texts, truncated = await discovery.window_sample(client, entity, now)
        except FloodWaitError as exc:
            # Before the generic handler: swallowed there, a rate-limited channel is written
            # down as a verdict, which is a permanent judgement on a temporary state.
            return exc.seconds
        except Exception as exc:
            records.append(
                {
                    "handle": handle,
                    "bucket": bucket,
                    "checked_at": stamp(),
                    "checks": {},
                    "prior_5a1": prior.get(handle.lower()),
                    "verdict": "ERROR",
                    "fails": [],
                    "flags": [],
                    "ruling": None,
                    "error": f"{type(exc).__name__}: {exc}",
                    "suggestions": None,
                }
            )
            await asyncio.sleep(PAUSE_SECONDS)
            continue
        window = discovery.window_stats(samples, texts, truncated)
        records.append(gate_row(handle, bucket, record, window, script_mix(texts), prior))
        await asyncio.sleep(PAUSE_SECONDS)
    return None


def prior_rows(path: Path) -> dict:
    """The 2026-08-06 scan's row per handle — the measurement the composition was chosen on.

    Description, never a gate input: the verdict is on what today's pass measured. What it buys
    is the delta, which is what a one-line FLAG evidence needs ("canon 13.0/wk, now 0.0").
    """
    if not path.exists():
        return {}
    scan = json.loads(path.read_text(encoding="utf-8"))
    return {
        row["handle"].lower(): {
            "generated_at": scan["generated_at"],
            "posts_per_week": row["posts_per_week"],
            "discussion_group": row["discussion_group"],
            "language_mix": row["language_mix"],
            "subscribers": row["subscribers"],
            "verdict": row["verdict"],
        }
        for row in scan["candidates"]
    }


def gate_summary(rows: list[dict]) -> dict:
    counts = {
        v: sum(1 for r in rows if r["verdict"] == v) for v in ("PASS", "FAIL", "FLAG", "ERROR")
    }
    by_bucket = {}
    for bucket in dict.fromkeys(b for _, b in CANDIDATES):
        picked = [r for r in rows if r["bucket"] == bucket]
        by_bucket[bucket] = {
            "n": len(picked),
            **{
                v: sum(1 for r in picked if r["verdict"] == v)
                for v in ("PASS", "FAIL", "FLAG", "ERROR")
            },
        }
    return {"n": len(rows), **counts, "by_bucket": by_bucket}


def print_gate_report(rows: list[dict]) -> None:
    header = (
        f"{'handle':<29}{'bucket':<9}{'subs':>9}{'p/wk':>7}{'prior':>7}"
        f"{'grp':>5}{'open':>6}{'%comm':>7}{'cyr':>6}  verdict"
    )
    print(f"\n{header}\n{'-' * len(header)}")
    for row in rows:
        checks, group = row["checks"], (row["checks"].get("discussion_group") or {})
        prior = row.get("prior_5a1") or {}
        live, lang = checks.get("liveness") or {}, checks.get("language") or {}
        comments = checks.get("comments") or {}
        print(
            f"{row['handle'][:28]:<29}{row['bucket']:<9}"
            f"{(checks.get('subscribers') or 0):>9}"
            f"{(live.get('posts_per_week') if live.get('posts_per_week') is not None else '—'):>7}"
            f"{(prior.get('posts_per_week') if prior else '—'):>7}"
            f"{('yes' if group.get('present') else 'no'):>5}"
            f"{('—' if not group.get('present') else 'yes' if group.get('open') else 'NO'):>6}"
            f"{(comments.get('share_with_comments') if comments.get('share_with_comments') is not None else '—'):>7}"
            f"{(lang.get('cyrillic_share') if lang.get('cyrillic_share') is not None else '—'):>6}"
            f"  {row['verdict']}"
        )
    for verdict in ("FAIL", "FLAG", "ERROR"):
        picked = [r for r in rows if r["verdict"] == verdict]
        if not picked:
            continue
        print(f"\n--- {verdict} ({len(picked)}) ---")
        for row in picked:
            prior = row.get("prior_5a1") or {}
            was = f" [5a1 06.08: {prior.get('posts_per_week')}/wk]" if prior else " [no prior scan]"
            for reason in row["fails"] + row["flags"] or [row.get("error") or ""]:
                print(f"  {row['handle']:<29}{row['bucket']:<9}{reason}{was}")


async def search_channels(client, query: str) -> list[tuple[Source, str]]:
    """Top public channels for a query, as candidates for the same per-channel check.

    Everything found is `community` until the operator decides otherwise — a real
    aggregator gets that source_type when it is added to the registry by hand.
    """
    found = await client(functions.contacts.SearchRequest(q=query, limit=DISCOVER_LIMIT))
    candidates = []
    for chat in found.chats:
        username = getattr(chat, "username", None)
        if not username:
            continue  # private or invite-only: not collectable
        handle = f"@{username}"
        source = Source("found", chat.title, "community", (handle,))
        candidates.append((source, handle))
    return candidates


def report_path(query: str | None) -> Path:
    if query is None:
        return DATA_DIR / "entry_check_report.json"
    # One file per query: three discovery runs must not overwrite each other, and
    # re-running a scan costs another rate-limited pass.
    slug = re.sub(r"\W+", "-", query.strip()).strip("-").lower()
    return DATA_DIR / f"discovery_{slug}.json"


def rank(record: dict) -> tuple:
    """Discovery order: channels that carry comments first, liveliest first."""
    return (
        bool(record.get("comments_enabled")),
        record.get("traffic", {}).get("median_comments", 0),
    )


def gate_rules() -> dict:
    """The verdict rules, written into the record so a reader checks them instead of trusting.

    Pre-registered before the pass: the thresholds were picked on the 2026-08-06 scan's
    controls (`results/discovery_5a1.json`), not on this run's distribution.
    """
    return {
        "verdicts": ["PASS", "FAIL", "FLAG"],
        "fail_is_a_closed_list": [
            "does not resolve",
            "dead against its bucket's expectation",
            "non-UA/RU dominant",
        ],
        "scam_or_fake_mapping": (
            "Telegram's scam/fake mark is mapped onto FAIL. It is outside the brief's three, and"
            " named here rather than left as an unhandled path: a channel Telegram flags may not"
            " enter the registry by silence."
        ),
        "dead": (
            "canon's own conjunction — docs/CHANNELS-launch.md excluded six channels as 'мёртв:"
            " ни постов за 28 дней, ни группы' (0 posts AND no group, 6/6) and put fourteen"
            " equally silent ones WITH a group into the watch bucket (14/14). So: no posts in the"
            " window and no group = FAIL; no posts and a group present = FLAG (watch shape)."
            " Not a rate test: eight launch channels sit at a canon rate of 0.2-0.5 posts/week,"
            " where zero posts in 28 days is the expected reading."
        ),
        "language": {
            "decisive_signal": "cyrillic_share — posts carrying Cyrillic over posts carrying"
            " any letter; langid.detect's mix rides beside it as description only",
            "why_not_detect": "detect()'s 'other' holds both 'no letters' and 'Cyrillic, ua/ru"
            " tied', and on the 06.08 scan that put operator-chosen channels at ua+ru 0.5",
            "min_lettered_texts": GATE_MIN_LETTERED_TEXTS,
            "fail_below": GATE_CYRILLIC_MIN,
            "under_the_minimum": "described and FLAGged, never a FAIL",
            "controls": "@MAMIPEKER1 (Turkish, excluded) 150 texts at cyrillic_share 0 → FAIL;"
            " @berlin_food, excluded for its TOPIC, writes Ukrainian → language and theme are"
            " separate findings and only the first is mechanical",
        },
        "flag": [
            "evidence contradicts the bucket: a comments-bucket channel with no group, a"
            " posts-only channel that has one, a watch channel that posts again or has no group",
            "a discussion group that is not open (approval-gated, restricted, send-banned)",
            "a comments-bucket channel whose sampled posts carry no comments at all",
            "a supergroup where a broadcast channel was expected",
            "a language share under the minimum sample",
        ],
        "pre_registered_flags": dict(PRE_REGISTERED_FLAGS),
        "buckets": {name: dict(spec) for name, spec in BUCKETS.items()},
    }


def gate_todo(pending: list[tuple[str, str]], only: list[str] | None) -> list[tuple[str, str]]:
    """The candidates this invocation TALKS TO — the record still covers every candidate.

    Same split as `collect_5c1.narrowed`, and for the same limit: every handle in the loop costs a
    `ResolveUsernameRequest`. It exists because the operator sequences batches — the 16 city feeds
    first, the retail addition after — and one gate pass over both would merge them, which also
    merges their rulings: `apply_gate_rulings_5c1.final_bucket` refuses the WHOLE run on a single
    unruled FLAG, so a flag in one batch would hold the other batch's registry write hostage.
    """
    if not only:
        return pending
    wanted = set(only)
    if missing := wanted - {handle for handle, _ in CANDIDATES}:
        raise SystemExit(f"--only names handles this gate does not carry: {sorted(missing)}")
    return [(handle, bucket) for handle, bucket in pending if handle in wanted]


async def run_gate(only: list[str] | None = None) -> int:
    """Deliverable 1 of PROMPT-5c1: the gate over the 62, up to the report. Writes no registry."""
    from build_audit_pack import git_state  # deferred: only the gate path needs it
    from collect_5c1 import log_join, refuse_inside_flood_wait
    from discover_channels import WINDOW_DAYS, WINDOW_LIMIT

    # Every gated candidate starts with a ResolveUsernameRequest, which is what an account-wide
    # FloodWait is on. `collect_5c1.py` has refused to start inside that window since 07.08; this
    # path did not, and on 2026-08-07 a single `--gate-5c1 --only` run walked straight into the
    # wall and came back with 55,779 s. It cost nothing — Telegram returned the REMAINING time on
    # the standing limit, clearing 10:01:27 against the recorded 10:02, so the window was not
    # extended — but the refusal belongs here too, and it reads the same log the collector does.
    refuse_inside_flood_wait()

    prior = prior_rows(PRIOR_SCAN)
    held_record = (
        json.loads(GATE_RECORD.read_text(encoding="utf-8")) if GATE_RECORD.exists() else {}
    )
    held = held_record.get("candidates", [])
    held_state = {
        key: held_record[key]
        for key in ("registry_written", "rulings", "notes")
        if key in held_record
    }
    done = {row["handle"] for row in held if row["verdict"] in ("PASS", "FAIL", "FLAG")}
    rows = [row for row in held if row["handle"] in done]
    pending = [(handle, bucket) for handle, bucket in CANDIDATES if handle not in done]
    todo = gate_todo(pending, only)
    scoped = "" if len(todo) == len(pending) else f" ({len(pending) - len(todo)} held by --only)"
    print(
        f"{len(CANDIDATES)} candidates: {len(rows)} already recorded, {len(todo)} to check{scoped}"
    )
    if not prior:
        print(f"warning: {PRIOR_SCAN} missing — rows carry no prior measurement")

    flood_wait = None
    if todo:
        client = build_client()
        await client.connect()
        try:
            if not await client.is_user_authorized():
                print("No Telegram session. Run: python3 scripts/tg_login.py")
                return 2
            flood_wait = await gate_batch(client, todo, prior, rows)
        finally:
            await client.disconnect()
        if flood_wait is not None:
            # Into the JOIN LOG, not only into this record: the log is where every phase reads
            # "is the account walled" from, and a wall this path found but did not write there is
            # a wall the collector walks into tomorrow.
            log_join(
                {
                    "at": stamp(),
                    "channel": "(gate)",
                    "outcome": "floodwait",
                    "seconds": flood_wait,
                    "clears_at": (
                        datetime.now(timezone.utc) + timedelta(seconds=flood_wait)
                    ).isoformat(timespec="seconds"),
                    "note": "hit by scripts/entry_check.py --gate-5c1",
                }
            )
            print(f"FloodWait: Telegram asks for {flood_wait}s — stopped early, re-run after that.")

    order = {handle: i for i, (handle, _) in enumerate(CANDIDATES)}
    rows.sort(key=lambda row: order[row["handle"]])
    summary = gate_summary(rows)
    record = {
        "generated_at": stamp(),
        "phase": "5c1",
        "deliverable": "1 — the track-R entry gate over the launch composition",
        "contract": "docs/SPEC.md §3.11 (4); docs/PROMPT-5c1.md Deliverable 1",
        "canon": (
            "docs/CHANNELS-launch.md — operator verdict 2026-08-06 plus that evening's addition."
            " The composition is the operator's choice; this gate verifies each entry against"
            " the bucket it was chosen into."
        ),
        "complete": len(rows) == len(CANDIDATES) and summary["ERROR"] == 0,
        "flood_wait_seconds": flood_wait,
        "read_only": "no group joins, no store writes, no registry edit in this pass",
        "post_sample": POST_SAMPLE,
        "window_days": WINDOW_DAYS,
        "window_limit": WINDOW_LIMIT,
        "rules": gate_rules(),
        "prior_scan": {
            "path": rel(PRIOR_SCAN),
            "generated_at": next(iter(prior.values()), {}).get("generated_at"),
            "role": "description only — never a gate input; the verdict is on this pass",
            "handles_without_a_prior_row": [h for h, _ in CANDIDATES if h.lower() not in prior],
        },
        "candidates": rows,
        "summary": summary,
        # Carried, not reset. Gating a LATER candidate must not un-say what the rulings already
        # decided about the earlier ones: a fresh `False` here silently told the 5c1 collector
        # the registry had never been written, and it refused to collect — correctly, on a fact
        # that had stopped being true. `rulings` and `notes` ride along for the same reason.
        "registry_written": held_state.get("registry_written", False),
        "note": (
            "PROMPT-5c1 D1 stops here: every FAIL and FLAG goes to the operator, who rules in"
            " chat; the rulings land in each row's `ruling`, and only then is"
            " config/registry.yaml written. data/entry_check_report.json (the 2026-07-27 run) is"
            " untouched, and the four registry channels are out of this gate's scope."
        ),
        **{key: value for key, value in held_state.items() if key != "registry_written"},
        "git": git_state(GATE_RECORD),
    }
    GATE_RECORD.parent.mkdir(parents=True, exist_ok=True)
    GATE_RECORD.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print_gate_report(rows)
    print(
        f"\n{summary['n']} of {len(CANDIDATES)} checked — "
        f"PASS {summary['PASS']} · FAIL {summary['FAIL']} · FLAG {summary['FLAG']}"
        f" · ERROR {summary['ERROR']}"
    )
    for bucket, counts in summary["by_bucket"].items():
        print(
            f"  {bucket:<10}n={counts['n']:<4}PASS {counts['PASS']:<4}FAIL {counts['FAIL']:<4}"
            f"FLAG {counts['FLAG']:<4}ERROR {counts['ERROR']}"
        )
    print(f"\nrecord: {rel(GATE_RECORD)}")
    print("STOP: the registry is not written until the operator rules on the FAILs and FLAGs.")
    return 1 if flood_wait is not None else 0


async def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Telegram channel entry check.")
    parser.add_argument(
        "--discover",
        metavar="QUERY",
        help="check the top public channels Telegram returns for QUERY instead of the registry",
    )
    parser.add_argument(
        "--gate-5c1",
        action="store_true",
        help="run the track-R entry gate over the 62 launch candidates (PROMPT-5c1 D1)",
    )
    parser.add_argument(
        "--only",
        metavar="HANDLE",
        nargs="+",
        help="gate only these candidates (the record still covers all of them)",
    )
    args = parser.parse_args(argv)

    if args.gate_5c1:
        return await run_gate(args.only)

    records: list[dict] = []
    flood_wait = None

    client = build_client()
    await client.connect()
    try:
        if not await client.is_user_authorized():
            print("No Telegram session. Run: python3.11 scripts/tg_login.py")
            return 2
        if args.discover:
            candidates = await search_channels(client, args.discover)
            print(f"{len(candidates)} public channels found for {args.discover!r}")
        else:
            candidates = [
                (source, handle)
                for source in load_registry(REGISTRY).sources
                for handle in source.telegram_channels
            ]
        flood_wait = await collect(client, candidates, records)
    finally:
        await client.disconnect()

    if args.discover:
        records.sort(key=rank, reverse=True)

    path = report_path(args.discover)
    path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "query": args.discover,
        "registry": None if args.discover else str(REGISTRY.relative_to(REPO_ROOT)),
        "post_sample": POST_SAMPLE,
        "channels": records,
    }
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print_table(records)
    print(f"\nreport: {path.relative_to(REPO_ROOT)} ({len(records)} channels)")
    if flood_wait is not None:
        print(f"FloodWait: Telegram asks for {flood_wait}s — stopped early, re-run after that.")
        return 1
    print("Registry stays untouched: the team lead edits it after reviewing this.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
