#!/usr/bin/env python3
"""5c1 addenda: the "does this chain have a channel at all" searches and the Poltava-cities
discovery scan ($0, read-only).

Canon: `docs/CHANNELS-launch.md`, section "Дозаявка №2" (operator, 2026-08-07 evening) and the
"МАСТЕР-ЛИСТ" of 2026-08-08, plus addendum 9 of the same day. Four questions, none of which is a
registry write:

``--search``
    Does the Хвилинка chain (Lubny, Myrhorod, Lokhvytsia, Pyriatyn, Hrebinka) have a Telegram
    channel at all? Their site carries no link. Three queries through Telegram's own global
    search; a convincing match goes to the gate, and NOTHING here decides that — the script
    records what the search returned and whether any row's title even contains the name. A
    negative finding is written into the gate record's notes, because "we looked and found
    nothing" is a result that has to survive, and an absent note reads like an unasked question.

``--search-retail``
    The same instrument over the five national chains whose CONSUMER channel the web pass could
    not find — Novus, Velmart, Fozzy C&C, Auchan, METRO Ukraine (canon "МАСТЕР-ЛИСТ"). One note
    per chain, because five questions asked in one pass are five findings: a chain that turns up
    goes to the gate, and a chain that does not is closed by its own negative record.

``--search-food-quality``
    Does the Consumer Union of Ukraine's counterfeit-dairy channel exist (addendum 9)? Five
    queries, ONE note: unlike the retail five this is a single channel asked about five ways, so
    five empty queries are one negative and any match keeps one question open. A convincing match
    goes to the gate like everything else — and its `audience` has no value in the closed list
    yet, which is the operator's to rule, not this script's to invent.

``--search-titles``
    The five channels the operator's TGStat pass saw by TITLE only (canon "Дозаявка №8":
    «Хендлы добрать завтра ботом/поиском»). Five questions, five notes — TGStat shows a name and
    not a handle, so the search is the only way from one to the other, and a match still needs a
    human read before it reaches the gate.

``--search-city-analogues``
    Two towns lost their handle at the day-2 sitting because it turned out to be a chat
    (@poltava_misto, @kremenchug_live). This asks Telegram which BROADCAST channels those towns
    have — the rows now carry `broadcast` and `megagroup`, so a reader can tell a feed from
    another chat without opening each one.

``--poltava``
    The discovery scan for the new `poltava_cities` theme, in `scripts/discover_channels.py`'s
    pattern and reusing its machinery — same per-channel check, same four-week window, same
    language mix — into its own record. Candidates ONLY: no registry entry, no join, no verdict.
    A city channel the operator later picks enters through the track-R gate like everything else,
    and enters POSTS-ONLY until 5c2 rules on category-filtered comment fetch, because without
    that filter a city chat's whole traffic lands in a paid inference queue.

    PYTHONPATH=src python3 scripts/late_batch_5c1.py --search
    PYTHONPATH=src python3 scripts/late_batch_5c1.py --search-retail
    PYTHONPATH=src python3 scripts/late_batch_5c1.py --search-food-quality
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

SEARCH_BOUND = (
    "Bounded, not proven — contacts.SearchRequest ranks by its own relevance and returns at most"
    " ten rows per query, so this says there is no FINDABLE public channel under the names"
    " searched, not that none exists."
)

SEARCHES = {
    "hvylynka_search": {
        "subject": "the Хвилинка chain",
        "asked": (
            "does the Хвилинка chain (Lubny, Myrhorod, Lokhvytsia, Pyriatyn, Hrebinka) have a"
            " Telegram channel? canon docs/CHANNELS-launch.md 'Дозаявка №2'"
        ),
        "queries": HVYLYNKA_QUERIES,
        "markers": HVYLYNKA_MARKERS,
        "also": "The site hvylya.net.ua carries no Telegram link either.",
    },
}
"""One entry per question the search answers, so the note it writes is per question too.

A search is not a verdict here: it records what came back and whether any row's title even carries
the name. The negative is the finding worth keeping — "we looked and found nothing" has to survive,
because an absent note reads like an unasked question — and a search that DID match anything stays
open for a human read (`--close-*`), because deciding what is convincing is not a script's call."""

CANON_MASTER_LIST = (
    "canon docs/CHANNELS-launch.md 'МАСТЕР-ЛИСТ', the line «Проверить внутри Telegram (вебом не"
    " найдено)» — the Telegram-side half of «Дозаявка №5»"
)

RETAIL_SEARCHES = {
    # Written out one per brand, each carrying what the web pass found, because a reader deciding
    # whether a chain is really absent needs to see the question and its evidence in one place.
    # The five brands and their order are the canon's; a test parses that line to hold this table.
    "novus_consumer_search": {
        "subject": "Novus's consumer channel",
        "asked": f"does Novus have a consumer Telegram channel? {CANON_MASTER_LIST}",
        "queries": ("Novus", "Новус"),
        "markers": ("novus", "новус"),
        "also": "On the web only the corporate @NovusNews was found, a channel for staff.",
    },
    "velmart_consumer_search": {
        "subject": "Velmart's consumer channel",
        "asked": f"does Velmart have a consumer Telegram channel? {CANON_MASTER_LIST}",
        "queries": ("Velmart", "Вельмарт"),
        "markers": ("velmart", "вельмарт"),
        "also": "The web pass found no channel for this chain at all.",
    },
    "fozzy_consumer_search": {
        "subject": "Fozzy C&C's consumer channel",
        "asked": f"does Fozzy C&C have a consumer Telegram channel? {CANON_MASTER_LIST}",
        "queries": ("Fozzy", "Фоззі"),
        "markers": ("fozzy", "фоззі", "фоззи"),
        "also": (
            "The web pass found nothing for the cash-and-carry format. The group's retail brands"
            " are already in the registry (@silposilpo, and @forainfo is on this gate)."
        ),
    },
    "auchan_consumer_search": {
        "subject": "Auchan's consumer channel",
        "asked": f"does Auchan have a consumer Telegram channel? {CANON_MASTER_LIST}",
        "queries": ("Auchan", "Ашан"),
        "markers": ("auchan", "ашан"),
        "also": "On the web only a support bot was found, which collects nothing.",
    },
    "metro_consumer_search": {
        "subject": "METRO Ukraine's consumer channel",
        "asked": f"does METRO Ukraine have a consumer Telegram channel? {CANON_MASTER_LIST}",
        "queries": ("METRO Україна", "Метро Кеш енд Кері"),
        "markers": ("metro", "метро"),
        "also": "The web pass found no consumer channel for the Ukrainian arm.",
    },
}

SEARCHES.update(RETAIL_SEARCHES)

FOOD_QUALITY_SEARCH = {
    "food_quality_search": {
        "subject": "the Consumer Union of Ukraine's counterfeit-dairy channel",
        "asked": (
            "does Maksym Nesmiyanov / the Союз споживачів України have a Telegram channel? The"
            " operator remembers independent lab checks on counterfeit dairy published near this"
            " project's category — canon: operator brief, 5c1 addendum 9 (2026-08-08)"
        ),
        # One question asked five ways, so ONE note: the retail five were five chains and five
        # findings, this is a single channel that may or may not exist under any of these names.
        "queries": (
            "Макс Контроль",
            "MaxControl",
            "Несміянов",
            "Союз споживачів України",
            "фальсифікат",
        ),
        # Deliberately loose, and the last one is a TOPIC word rather than a name: a channel about
        # фальсифікат that is not this one is still worth a human look, and a marker matching
        # nothing is itself the finding. Anything matched keeps the note open for that look.
        "markers": (
            "макс контроль",
            "maxcontrol",
            "несміянов",
            "несмиянов",
            "союз споживачів",
            "союз потребителей",
            "фальсифікат",
        ),
        "also": (
            "The operator's own recollection is the only prior evidence — no web pass was run for"
            " this one, so a negative here is bounded by Telegram's search alone."
        ),
    },
}

SEARCHES.update(FOOD_QUALITY_SEARCH)

CANON_HARVEST = (
    "canon docs/CHANNELS-launch.md 'Дозаявка №8', the line «Хендлы добрать завтра ботом/поиском»"
)

TITLE_SEARCHES = {
    # Five channels the operator's TGStat pass saw by TITLE only — TGStat shows the name, not the
    # handle. One note each: five different channels, so a hit on one closes nothing about the
    # other four. The subscriber counts are TGStat's and are carried so a match can be sanity
    # checked against the size the operator saw, not just against the name.
    "matusi_ukrainy_title": {
        "subject": "«Матусі України» (~19.3k, TGStat)",
        "asked": f"what is the handle of «Матусі України»? {CANON_HARVEST}",
        "queries": ("Матусі України", "Матусі"),
        # The bare «матусі» is here because the second query is bare too, and a marker that does
        # not catch its own query turns every hit into a clean negative. It is loose on purpose:
        # what it costs is a human read, and what the precise one costs is a missed channel.
        "markers": ("матусі україн", "матусі"),
        "also": "TGStat showed ~19.3k subscribers and no handle.",
    },
    "mamo_ne_psihuy_title": {
        "subject": "«Мамо, не псіхуй!» (~13.8k, TGStat)",
        "asked": f"what is the handle of «Мамо, не псіхуй!»? {CANON_HARVEST}",
        "queries": ("Мамо, не псіхуй", "не псіхуй"),
        "markers": ("не псіхуй", "не психуй"),
        "also": "TGStat showed ~13.8k subscribers and no handle.",
    },
    "dytiache_kharchuvannia_title": {
        "subject": "«Дитяче харчування» (~7.9k, TGStat)",
        "asked": f"what is the handle of «Дитяче харчування»? {CANON_HARVEST}",
        "queries": ("Дитяче харчування", "дитяче харчування прикорм"),
        "markers": ("дитяче харчуван",),
        "also": (
            "TGStat showed ~7.9k subscribers and no handle. The name is also an ordinary phrase"
            " («baby food»), so several unrelated channels can carry it — the rows need a read."
        ),
    },
    "vse_pro_ditey_title": {
        "subject": "«Все про дітей | Виховання | Психологія» (~23.7k, TGStat)",
        "asked": f"what is the handle of «Все про дітей | Виховання | Психологія»? {CANON_HARVEST}",
        "queries": ("Все про дітей", "Все про дітей Виховання Психологія"),
        "markers": ("все про діт",),
        "also": "TGStat showed ~23.7k subscribers and no handle.",
    },
    "suchasni_batky_title": {
        "subject": "«Сучасні батьки | Виховання» (~36.4k, TGStat)",
        "asked": f"what is the handle of «Сучасні батьки | Виховання»? {CANON_HARVEST}",
        "queries": ("Сучасні батьки", "Сучасні батьки Виховання"),
        "markers": ("сучасні батьк",),
        "also": (
            "TGStat showed ~36.4k subscribers and no handle, and the canon flags it «возможно"
            " приватный» — a search that finds nothing is consistent with a private channel and"
            " does not distinguish the two. That belongs to the deferred privates track."
        ),
    },
}

SEARCHES.update(TITLE_SEARCHES)

CANON_CITY_ANALOGUES = (
    "canon docs/CHANNELS-launch.md 'Рулинги гейта дня 2', ruling (6) — the operator's addition"
    " during the session: find broadcast analogues for the two towns whose handles left as"
    " supergroups"
)

CITY_ANALOGUE_SEARCHES = {
    # Poltava and Kremenchuk lost a handle each to ruling (1), which excluded three chats. The
    # question is not "does the town have a channel" — both already have one in the composition —
    # but "is there a BROADCAST feed of the size that left". `entry_check.suggest` now carries
    # `broadcast` and `megagroup` per row precisely so this search can tell them apart; the
    # marker is only the town name, because a filter on the answer is what the human look is for.
    "poltava_broadcast_analogue": {
        "subject": "a broadcast news feed of Poltava to replace @poltava_misto (60,028, a chat)",
        "asked": (
            "which PUBLIC BROADCAST channels of Poltava does Telegram's own search return?"
            f" {CANON_CITY_ANALOGUES}"
        ),
        "queries": ("Полтава новини", "Полтава", "Poltava"),
        "markers": ("полтав", "poltav"),
        "also": (
            "@poltava_informue and @suspilnepoltava already entered from the same town, so a row"
            " that is one of them is coverage already held, not a find."
        ),
    },
    "kremenchuk_broadcast_analogue": {
        "subject": "a broadcast news feed of Kremenchuk to replace @kremenchug_live (16,056, a chat)",
        "asked": (
            "which PUBLIC BROADCAST channels of Kremenchuk does Telegram's own search return?"
            f" {CANON_CITY_ANALOGUES}"
        ),
        "queries": ("Кременчук новини", "Кременчук", "Кременчуг"),
        "markers": ("кременчу",),
        "also": "@telegraf_kremenchuk already entered from the same town.",
    },
}

SEARCHES.update(CITY_ANALOGUE_SEARCHES)

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

SEARCH_LIMIT = (
    "Bounded the same way every search here is: contacts.SearchRequest ranks by Telegram's own"
    " relevance and returns at most ten rows per query, so this closes the question by record"
    " rather than proving absence."
)

DAY2_JUDGEMENTS = {
    # The executor's read of the day-2 searches, 2026-08-08, kept in the repo and applied by
    # `--close` so the RECORD carries the verdict. Step 7's rule is "not found → negative
    # recorded", and a note that still says «MATCHES FOUND — not closed» while the report says
    # NEGATIVE is a verdict living in prose. Every row of every search was read.
    "novus_consumer_search": {
        "verdict": "NEGATIVE — Novus has no consumer channel findable in Telegram",
        "why": (
            "Six name matches and not one is the chain: @newworldra «NOVUS ORDO SECLORUM» (1,568),"
            " @novus_ordo, @novus_ordum, @Americana2001, @novusycc, and @dc_novus — a Kazakh"
            " house-of-culture channel in Tobyl (81). The Latin phrase is what the name collides"
            " with. The web pass had already found only the corporate @NovusNews, for staff."
        ),
    },
    "velmart_consumer_search": {
        "verdict": "NEGATIVE — Velmart's Telegram presence is two empty placeholders",
        "why": (
            "@velmart «Velmart Channel» has THREE subscribers and @velmart1 «ВЕЛМАРТ» is a chat"
            " with three. The handles are taken and nothing is published under them; the other"
            " matches (@velmartyr, @velmartinus) are unrelated. A registered handle is not a"
            " channel, and neither of these would survive the gate's liveness check."
        ),
    },
    "fozzy_consumer_search": {
        "verdict": "NEGATIVE — no consumer channel for the cash-and-carry format",
        "why": (
            "Nine matches, all peripheral: a currency booth inside a Fozzy store"
            " (@obminfozzy, 55), a jobs channel (@robotafozzipochayna, 3), «Fozzy Експериментаріум»"
            " (a chat, 1,227), a test channel, and crypto/exchange channels borrowing the word."
            " The group's retail brands are covered instead — @silposilpo is in the registry and"
            " @forainfo entered today."
        ),
    },
    "auchan_consumer_search": {
        "verdict": "NEGATIVE for Ukraine — every real Auchan channel found is Russian",
        "why": (
            "@auchanrus «АШАН Россия» (82,813) and @auchan_retail_russia (1,435) are the only"
            " substantial matches, and SPEC §3.11 (4) excludes RF-market sources regardless of"
            " language, so finding them is not finding a candidate. The Ukrainian side returns"
            " @auchanempire (2) and @creativefogg «Ашан» (25). The web pass had found only a"
            " support bot, which collects nothing."
        ),
    },
    "metro_consumer_search": {
        "verdict": "NEGATIVE — METRO Ukraine's name is held by resellers, not by the chain",
        "why": (
            "Six matches and the largest is @metroShopikN1S «Метро шоп Україна» with THIRTEEN"
            " subscribers; the rest run 3, 2, 2. «Метро» also collides with the underground —"
            " @kyrsvalyutpumbpalatsukraina is an exchange rate board at a metro station. Nothing"
            " here is the wholesaler."
        ),
    },
    "food_quality_search": {
        "verdict": "NEGATIVE — the Consumer Union's counterfeit-dairy channel is not in Telegram search",
        "why": (
            "@maxcontrol exists and has TWO subscribers, which is not the channel the operator"
            " remembers. «Несміянов» and «Союз споживачів України» return nothing at all, and the"
            " topic word «фальсифікат» returns @lukashukpidoras «комірка фальсифікатора» (98) —"
            " not an NGO. The operator's recollection is the only prior evidence and no web pass"
            " was run for it, so this negative is bounded by Telegram's search alone."
        ),
    },
    "matusi_ukrainy_title": {
        "verdict": "FOUND — @matusi_ukr, and the subscriber count is what confirms it",
        "why": (
            "«Матусі України» came back at 19,278 against the ~19.3k the operator's TGStat pass"
            " showed. The name is a common one — the same search returns six chats and two other"
            " towns' «Матусі» channels — so the size is what identifies the row rather than the"
            " title. Gated the same day (PASS, ua 0.93, open group) and entered the registry."
        ),
    },
    "mamo_ne_psihuy_title": {
        "verdict": "FOUND — @mamo_nepsichuy, confirmed by size",
        "why": (
            "13,781 against TGStat's ~13.8k. The only other match is @maluvana2024 «Малюй і не"
            " псіхуй» (4), a different channel borrowing the phrase. Gated PASS, ua 1.00, open"
            " group; entered the registry and is one of the day's ten joins."
        ),
    },
    "dytiache_kharchuvannia_title": {
        "verdict": "NEGATIVE — nothing of the size the operator saw carries this name",
        "why": (
            "TGStat showed ~7.9k. The largest match is @dobrobutPoltava «ДИТЯЧЕ ХАРЧУВАННЯ"
            " (ДОБРОБУТ)» with 439 subscribers — a clinic — then two shops on 28 and 4. The"
            " phrase is also an ordinary one («baby food»), so a name match here carries less"
            " than usual. @ya_Nenka matched too and is already ours."
        ),
    },
    "vse_pro_ditey_title": {
        "verdict": "NOT THE CHANNEL — the title matches exactly and the size does not",
        "why": (
            "@children45 carries «Все про дітей | Виховання | Психологія» word for word and has"
            " 277 subscribers where TGStat showed ~23.7k — a factor of 85. A title is copyable and"
            " a subscriber count is not, so this is either a namesake or a public shell beside a"
            " private original. Not sent to the gate; recorded as unresolved."
        ),
    },
    "suchasni_batky_title": {
        "verdict": "NOT THE CHANNEL — same shape, and the canon predicted it",
        "why": (
            "@suchasnibatki «Сучасні батьки» has TEN subscribers against the ~36.4k TGStat showed"
            " — a factor of 3,600. The canon had already flagged this one «возможно приватный»,"
            " and a public namesake beside a private original is exactly what that looks like from"
            " outside. It belongs to the deferred privates track, not to the gate."
        ),
    },
    "poltava_broadcast_analogue": {
        "verdict": "FOUND — two taken, and three of the four day-2 picks were invisible to the town scan",
        "why": (
            "Nineteen name matches. Taken to the gate: @poltava_pvp «PVP.POLTAVA» (106,761) and"
            " @poltava20 «Полтава ІНФО | Новини Світло» (43,486), both broadcast, both PASS, both"
            " in the registry. NOT taken, by the operator's ruling: @region_poltava_syrena"
            " «ПОЛТАВА НОВИНИ | СИРЕНА» (195,553) and @trevoga_karta — alert feeds, the genre that"
            " produced all three of the composition's RF_FLAGs. @poltava_insider (22,831) is"
            " recorded as a candidate. @poltava_informue, @poltava_misto and @suspilnepoltava came"
            " back as rows and are already ours or already excluded."
        ),
    },
    "kremenchuk_broadcast_analogue": {
        "verdict": "FOUND — two taken, and the largest feed of the town was never in the scan",
        "why": (
            "Twenty-two name matches. Taken: @h_kremenchug «Х Кременчук» (137,221) and"
            " @kremen_news «КРЕМІНЬ | НОВИНИ | КРЕМЕНЧУК» (28,286), both broadcast, both PASS,"
            " both in the registry — against the 16,056-subscriber chat that left as a supergroup."
            " NOT taken: @sirena_kremenchuk (72,660) and @treeshkremik «НеТруха ⚡️ Кременчук |"
            " Новини війни» (49,521), alert and war-digest feeds. @kremenchuk_insider (11,563) is"
            " recorded as a candidate. Neither of the two taken here was in the 119-candidate"
            " town-name scan — the town's largest feed was invisible to it."
        ),
    },
}
"""Executor judgements over the day-2 searches, applied by `--close` and never by `--search`.

Same division of labour `HVYLYNKA_JUDGEMENT` set: the search records what came back and whether a
title carries the name, and a human decides what is convincing. Kept in the repo rather than typed
into the record once, so a re-run can carry them forward and `record_search` can mark them stale if
the matched handles ever change."""

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


async def run_search(client, spec: dict) -> dict:
    """Telegram's global search for one subject, one row per result. Judges nothing."""
    results = {}
    for query in spec["queries"]:
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
                marker in title or marker in handle for marker in spec["markers"]
            ):
                seen.add(row["username"])
                matches.append(row)
    return {"queries": list(spec["queries"]), "results": results, "name_matches": matches}


def matched_handles(note: dict) -> list[str]:
    return sorted(row["username"] for row in note.get("name_matches", []) if row.get("username"))


def record_search(key: str, found: dict) -> dict:
    """Write the search into the gate record's notes — closed only if it found nothing.

    A judgement already recorded is carried forward rather than overwritten: re-running the
    search would otherwise reopen a question a human had closed, silently. It is carried only
    while it still applies — if this search matched a different set of handles, the judgement is
    about rows that are no longer the rows, and the note says so instead of standing.

    One note per question, keyed by `SEARCHES`: five chains asked in one pass are five findings,
    and one of them coming back positive must not close or reopen the other four.
    """
    spec = SEARCHES[key]
    record = json.loads(GATE_RECORD.read_text(encoding="utf-8"))
    closed = not found["name_matches"]
    held = record.get("notes", {}).get(key, {})
    judgement, stale = held.get("judgement"), None
    if judgement is not None:
        stale = matched_handles(held) != matched_handles(found)
        closed = not stale
    note = {
        "asked": spec["asked"],
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
            else f"NEGATIVE — Telegram's global search returns no channel whose title or handle"
            f" carries the name of {spec['subject']} under any of the {len(found['queries'])}"
            f" queries. The question is closed by record: {spec['also']} {SEARCH_BOUND}"
            if closed
            else "MATCHES FOUND — not closed. The rows above need a human look before any of them"
            " goes to the gate; this script does not decide what is convincing."
        ),
    }
    record.setdefault("notes", {})[key] = note
    record["git"] = git_state(GATE_RECORD)
    GATE_RECORD.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return note


def close_notes(judgements: dict[str, dict]) -> int:
    """Write the executor's readings into the notes they are about. No API, no new search.

    A search records rows; a human decides which of them is convincing. Until that decision reaches
    the note, `results/entry_gate_5c1.json` says «MATCHES FOUND — not closed» about a question the
    report calls answered, and the verdict lives only in prose. Step 7's rule is "not found →
    negative recorded", and this is what records it.

    `matched_handles` is stamped into the judgement so `record_search` can tell later whether the
    reading is still about the rows it was made on — the same staleness check the Хвилинка
    judgement already gets.
    """
    record = json.loads(GATE_RECORD.read_text(encoding="utf-8"))
    notes = record.get("notes", {})
    missing = [key for key in judgements if key not in notes]
    if missing:
        raise SystemExit(f"no search to judge for {sorted(missing)} — run --search first")

    for key, judgement in judgements.items():
        note = notes[key]
        full = {
            "judged_by": judgement.get("judged_by", "executor, 2026-08-08"),
            **judgement,
            "bound": judgement.get("bound", SEARCH_LIMIT),
            "judged_on_matches": matched_handles(note),
        }
        note["judgement"] = full
        note["judgement_stale"] = False
        note["closed"] = True
        note["finding"] = f"{full['verdict']}. {full['why']} {full['bound']}"
        print(f"{key}:\n  {full['verdict']}")
    record["git"] = git_state(GATE_RECORD)
    GATE_RECORD.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    where = (
        GATE_RECORD.relative_to(REPO_ROOT) if GATE_RECORD.is_relative_to(REPO_ROOT) else GATE_RECORD
    )
    print(f"\nclosed {len(judgements)} note(s) in {where} :: notes")
    return 0


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
        "--search-retail",
        action="store_true",
        help="Telegram search for the consumer channels of the five chains the web pass missed",
    )
    parser.add_argument(
        "--search-food-quality",
        action="store_true",
        help="Telegram search for the Consumer Union of Ukraine's counterfeit-dairy channel",
    )
    parser.add_argument(
        "--search-titles",
        action="store_true",
        help="Telegram search for the handles of the five channels «Дозаявка №8» saw by title",
    )
    parser.add_argument(
        "--search-city-analogues",
        action="store_true",
        help="Telegram search for broadcast feeds of Poltava and Kremenchuk (day-2 ruling 6)",
    )
    parser.add_argument(
        "--close-hvylynka",
        action="store_true",
        help="write the executor's read of the search into the note (no API, no new search)",
    )
    parser.add_argument(
        "--close",
        action="store_true",
        help="write the executor's reads of the day-2 searches into their notes (no API)",
    )
    parser.add_argument("--poltava", action="store_true", help="the poltava_cities discovery scan")
    parser.add_argument("--plan", action="store_true", help="print the queries and stop, no API")
    args = parser.parse_args(argv)

    if args.close_hvylynka:
        return close_notes({"hvylynka_search": HVYLYNKA_JUDGEMENT})
    if args.close:
        return close_notes(DAY2_JUDGEMENTS)

    keys = ["hvylynka_search"] if args.search else []
    keys += list(RETAIL_SEARCHES) if args.search_retail else []
    keys += list(FOOD_QUALITY_SEARCH) if args.search_food_quality else []
    keys += list(TITLE_SEARCHES) if args.search_titles else []
    keys += list(CITY_ANALOGUE_SEARCHES) if args.search_city_analogues else []

    if args.plan or not (keys or args.poltava):
        for key in keys or SEARCHES:
            print(f"search  : {key:<24}{', '.join(SEARCHES[key]['queries'])}")
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
            out = {"searches": {}}
            for key in keys:
                try:
                    out["searches"][key] = await run_search(client, SEARCHES[key])
                except FloodWaitError as exc:
                    # Ten queries is the longest search pass this phase runs, and the account
                    # already lost 20 hours to one wall. Stop on the first refusal and keep what
                    # was answered: a retry inside the window lengthens it.
                    out["flood_wait_seconds"] = exc.seconds
                    done = len(out["searches"])
                    print(f"FloodWait {exc.seconds}s on {key} — stopping, {done}/{len(keys)} done")
                    break
            if args.poltava and "flood_wait_seconds" not in out:
                out["scan"] = await run_scan(client, known, carried)
            return out
        finally:
            await client.disconnect()

    out = asyncio.run(run())

    for key, found in out.get("searches", {}).items():
        note = record_search(key, found)
        print(f"\n{note['finding']}")
        print(f"recorded in {GATE_RECORD.relative_to(REPO_ROOT)} :: notes.{key}")

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

    if (wait := out.get("flood_wait_seconds")) is not None:
        asked = set(out.get("searches", {}))
        print(f"\nFloodWait {wait}s — not asked: {', '.join(k for k in keys if k not in asked)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
