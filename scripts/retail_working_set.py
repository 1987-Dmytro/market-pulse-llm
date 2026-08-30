#!/usr/bin/env python3
"""C1 r2 — the working set: what we can actually collect, split by what it is FOR.

Two purposes need two lists, and merging them would hide the gap the census found:
  · PRICES and PROMO — a channel that posts flyers. Comments are irrelevant here.
  · COMMENTS — the customer's voice. A channel with comments CLOSED contributes nothing,
    however good its price share.
The chains' own channels turn out to be almost entirely the first kind, which is why category B
(the Poltava chats) carries the second. That contrast IS the finding, so it is rendered, not
summarised away.

`docs/PRODUCT.md` and SPEC v2 §3 leave the final pick to the operator: this file renders the
candidates and their basis, never a decision.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from retail_chains_report import AGGREGATORS, build  # noqa: E402

R1 = REPO_ROOT / "results" / "retail_census.json"
OUT = REPO_ROOT / "results" / "working_set.md"

# SPEC v2 §3 category B: the district centres the census was authorised to look in, in the
# spec's own order. Kept verbatim so «covered 18 of 24» stays a checkable claim.
POLTAVA_TOWNS = [
    "Полтава",
    "Кременчук",
    "Лубни",
    "Миргород",
    "Гадяч",
    "Горішні Плавні",
    "Пирятин",
    "Хорол",
    "Зіньків",
    "Карлівка",
    "Кобеляки",
    "Решетилівка",
    "Глобине",
    "Лохвиця",
    "Гребінка",
    "Шишаки",
    "Диканька",
    "Котельва",
    "Нові Санжари",
    "Оржиця",
    "Чутове",
    "Семенівка",
    "Козельщина",
    "Машівка",
]

# The operator lifted the Ukrainian-language bar on 2026-08-30: «Убрать планку, оставить
# колонкой». Language is now a COLUMN the operator filters by eye, not a filter that silently
# removes rows — Полтавщина speaks суржик and ru-ua mix, and the 4.5h2 adapter is trained on both.
# The bar's old value is kept only to render «what it used to exclude».
UA_BAR_LIFTED = True
FORMER_UA_BAR = 0.5


def towns_of(row: dict) -> list[str]:
    """Which district centre's query surfaced this chat. Two chats answer to more than one."""
    found = {
        f.split(":", 1)[1].rsplit(" ", 1)[0]
        for f in row.get("found_by", [])
        if f.startswith("poltava_chats")
    }
    return sorted(found)


def poltava_rows() -> list[dict]:
    r1 = json.loads(R1.read_text(encoding="utf-8"))
    return [
        row
        for row in r1["rows"]
        if row.get("verdict") == "enter"
        and any(f.startswith("poltava_chats") for f in row.get("found_by", []))
    ]


def cell(text: str) -> str:
    """A channel title can contain `|` («ФАНАТИК АТБ | АКЦІЇ») and that ends the markdown column."""
    return text.replace("|", "\\|")


def num(value, digits: int = 3) -> str:
    if value is None:
        return "—"
    return f"{value:.{digits}f}" if isinstance(value, float) else str(value)


def why_empty(town: str, all_rows: list[dict]) -> str:
    """Why a district centre carries no chat — derived, because there are THREE different causes.

    «Not covered» reads as one gap and is three: a centre where the search found nothing at all is
    a finding about Ukraine; one whose only chat is collectable but posts below the Ukrainian bar
    is a filter decision the operator can lower; one whose candidates were found and never measured
    is the FloodWait's budget, and it is still buyable. Merging them would price all three the same.
    """
    found = [
        r
        for r in all_rows
        if any(f.startswith(f"poltava_chats:{town} ") for f in r.get("found_by", []))
    ]
    if not found:
        return "nothing found at any bar — a finding about Ukraine, not about the budget"
    checked = [r for r in found if r.get("checked")]
    if not checked:
        return f"{len(found)} candidate(s) found and NEVER measured — the FloodWait stopped the pass; still buyable"
    enter = [r for r in checked if r.get("verdict") == "enter"]
    if enter:
        return f"{len(enter)} measured `enter` — should not be empty; check the renderer"
    # Resolved, readable, and nobody writes in it. That is not «not found» and not «not measured»:
    # the chat EXISTS and is open, and its 28-day window holds zero messages. No budget buys that.
    silent = [
        r
        for r in checked
        if r.get("resolved")
        and r.get("messages_open")
        # A broadcast's reason says «no posts», a group's says «no messages» — the same silence,
        # two words. Matching one of them files the other under a meaningless catch-all.
        and any(
            "no posts in the sampled window" in x or "no messages in the sampled window" in x
            for x in r.get("reasons", [])
        )
    ]
    if silent:
        return (
            f"{len(silent)} of {len(checked)} measured chat(s) resolve and are OPEN, and carry"
            " ZERO messages in the 28-day window — the chat exists and is silent, which no budget"
            f" changes: {', '.join(r['handle'] for r in silent)}"
        )
    return f"{len(checked)} measured, none `enter`"


# Chain-specific promo channels r1's name search measured and the site-reading instrument could
# never see, because the chain does not link them. Each identity was confirmed by hand against the
# channel's own public preview (`t.me/s/<handle>`, free HTTP) — a handle whose identity is a guess
# does not belong in a working set, which is exactly what r1 was refused for (Dv871).
#
# This section exists because the operator's priority is «комментарии к промо», and the census
# shows those do NOT live on the chains' official channels: ATB's own channel carries no promo at
# all, while four unofficial ATB deal channels carry nothing else.
CHAIN_PROMO = {
    "@blyzenkoua": (
        "Близенько",
        "own",
        "preview says «Мережа магазинів Близенько» — the CHAIN's own channel; blyzenko.ua simply does not link it, which is why the site instrument missed it",
    ),
    "@ATB_FANatik": (
        "АТБ",
        "unofficial",
        "«ФАНАТИК АТБ | АКЦІЇ» — a fan/deals channel, not ATB's. ATB's own @atb_market_official carries no promo and no comments",
    ),
    "@discountAtb": ("АТБ", "unofficial", "«Знижки АТБ» — a deals channel"),
    "@ATBATBATBAT": ("АТБ", "unofficial", "«НАШЕ АТБ / АКЦІЇ / НОВИНКИ»"),
    "@atbmarketznuzhku": (
        "АТБ",
        "unofficial",
        "«АТБ знижки Україна | Економія», description «Актуальні акції та знижки»",
    ),
    "@rozlyvne": (
        "Маркетопт",
        "own",
        "preview says «Офіційний канал Маркетопт Розливне Пиво» — official, but the draft-beer line",
    ),
    "@zakazzua": (
        "Zakaz.ua",
        "unofficial",
        "«Доставка з супермаркетів/Знижки» — not linked from zakaz.ua",
    ),
    "@RUKAVICHKAkr": (
        "Рукавичка",
        "unconfirmed",
        "«РУКАВИЧКА-КР» — reads like a local branch; no description, identity NOT confirmed",
    ),
    "@kopiyka_tm": (
        "Копійка",
        "unconfirmed",
        "titled «Копійка» with no description; dairy 0.500 is the highest in the census and rests on an unconfirmed identity — do not collect before confirming",
    ),
}
# Measured under a chain's name and NOT that chain: kept visible so the exclusion is a decision on
# the record rather than a silent filter.
REJECTED_AS_NOT_THE_CHAIN = {
    "@chortkiv2": "«Наш край - Чортківщина», description «канал Чортківщини» — regional news, not the Наш Край chain",
    "@ON_LINE_MO": "«Маркетопт ON_LINE» — its own description says «Ця група тільки для робітників мережі МаркетОпт»: a STAFF group, not a promo feed, despite a 0.460 price share",
    "@ispkopiyka": "«Копійка» the internet provider (Dv871's original example)",
    "@K_G_B_fin": "«Копійка гривню береже» — a personal-finance channel",
    "@depositorfrank": "«Канал про гроші» — finance, matched on the word «Грош»",
}


def render() -> str:
    table = build()
    with_channel = [r for r in table if r.get("handle") and r.get("subscribers") is not None]
    for_price = sorted(
        [r for r in with_channel if (r.get("price_share") or 0) > 0],
        key=lambda r: -(r["price_share"] or 0),
    )
    for_comments = sorted(
        [r for r in with_channel if r.get("comments_enabled")],
        key=lambda r: -(r.get("comments_per_day") or r.get("messages_per_day") or 0),
    )
    chats = poltava_rows()

    out = [
        "# retail-census r2 — the working set",
        "",
        "Rendered by `scripts/retail_working_set.py` from `results/retail_chains.json` (category A,",
        "measured 2026-08-30) and `results/retail_census.json` (category B, r1's readings of",
        "2026-08-27, NOT re-measured). Candidates and their basis — the pick is the operator's.",
        "",
        "## A1 — prices and promo: channels that post them",
        "",
        "Comments are not required here. `n` is the posts the share was computed over.",
        "",
        "| chain | channel | subs | n | price share | dairy | posts/day | what the channel is |",
        "|---|---|--:|--:|--:|--:|--:|---|",
    ]
    for r in for_price:
        out.append(
            f"| {r['name']} | {r['handle']} | {num(r.get('subscribers'))} | {num(r.get('n_posts'))} "
            f"| **{num(r.get('price_share'))}** | {num(r.get('dairy_share'))} "
            f"| {num(r.get('posts_per_day'))} | {cell(r.get('channel_note') or '—')} |"
        )
    out += [
        "",
        "## A2 — comments: channels where the customer can answer",
        "",
        "The operator's ruling (2026-08-30): only threads under PRICE posts count — «нам нужны",
        "только комментарии ценовых промо». `com/day` below is the WHOLE channel, so read it with",
        "`results/promo_comment_yield.json`, which joins every collected comment to its parent post",
        "and counts only the promo threads: 4 718 comments in 678 threads across the whole store,",
        "and 71% of what was collected sits under posts with no price in them at all.",
        "",
        "`*` marks a megagroup, where the column is messages/day: a group has no comments under",
        "posts, its whole traffic is the conversation.",
        "",
        "| chain | channel | subs | comments/day | price share | dairy | what the channel is |",
        "|---|---|--:|--:|--:|--:|---|",
    ]
    for r in for_comments:
        rate = (
            f"{num(r.get('messages_per_day'))}*"
            if r.get("is_group")
            else num(r.get("comments_per_day"))
        )
        out.append(
            f"| {r['name']} | {r['handle']} | {num(r.get('subscribers'))} | {rate} "
            f"| {num(r.get('price_share'))} | {num(r.get('dairy_share'))} "
            f"| {r.get('channel_note') or '—'} |"
        )

    # «Dairy AND open comments» is only the operator's question when the audience is a shopper's
    # and the row is a CHAIN. An aggregator answers a different question (which shop is cheapest),
    # and a channel with a note is B2B, wholesale or a marketplace — so both are counted apart
    # rather than folded in, which would put a 0.011 dairy share beside a 0.194 one.
    chains = [
        r
        for r in for_comments
        if (r.get("dairy_share") or 0) > 0
        and not r.get("channel_note")
        and r["name"] not in AGGREGATORS
    ]
    aggs = [r for r in for_comments if (r.get("dairy_share") or 0) > 0 and r["name"] in AGGREGATORS]
    out += [
        "",
        f"**Chains with dairy AND open comments AND a shopper's audience: {len(chains)}** — "
        + (
            ", ".join(
                f"{r['name']} ({r['handle']}, dairy {num(r['dairy_share'])}, "
                f"{num(r.get('comments_per_day'))} comments/day)"
                for r in chains
            )
            or "none"
        )
        + ". Everything else is one or the other: METRO has dairy and comments but a HoReCa"
        " audience, ЕКО and Фора have the deepest promo and comments CLOSED."
        + (
            "  Among aggregators, "
            + ", ".join(
                f"{r['name']} ({r['handle']}) carries dairy {num(r['dairy_share'])}" for r in aggs
            )
            + " — an order of magnitude below the chain above, and on r1's older clock."
            if aggs
            else ""
        ),
        "",
        "## A3 — the chains' promo that their own sites never link",
        "",
        "r1's name search measured these and the site instrument cannot see them: a chain does not",
        "link a fan channel, and Близенько does not link its own. Identity confirmed by hand from",
        "each channel's public preview; `own` means the chain's, `unofficial` a third party's, and",
        "`unconfirmed` must NOT be collected before someone confirms it.",
        "",
        "| chain | channel | kind | subs | price | comments | com/day | dairy | ua | identity |",
        "|---|---|---|--:|--:|---|--:|--:|--:|---|",
    ]
    r1_rows = {r["handle"]: r for r in json.loads(R1.read_text(encoding="utf-8"))["rows"]}
    promo = []
    for handle, (chain, kind, why) in CHAIN_PROMO.items():
        row = r1_rows.get(handle)
        if not row or not row.get("checked"):
            continue
        promo.append((handle, chain, kind, why, row))
    promo.sort(key=lambda x: -((x[4].get("stats") or {}).get("price_share") or 0))
    for handle, chain, kind, why, row in promo:
        s = row.get("stats") or {}
        out.append(
            f"| {chain} | {handle} | {kind} | {row.get('subscribers') or '—'} "
            f"| **{num(s.get('price_share'))}** | {'open' if row.get('comments_enabled') else 'closed'} "
            f"| {num(s.get('comments_per_day'))} | {num(s.get('dairy_share'))} "
            f"| {(s.get('language_mix') or {}).get('ua', 0):.2f} | {cell(why)} |"
        )
    open_promo = [p for p in promo if p[4].get("comments_enabled")]
    out += [
        "",
        f"**{len(open_promo)} of these {len(promo)} have comments OPEN** — "
        + ", ".join(f"{h} ({c})" for h, c, _k, _w, _r in open_promo)
        + ". This is where a comment under a promo post actually exists for АТБ, whose own"
        " channel has neither promo nor comments.",
        "",
        "Measured under a chain's name and NOT that chain — excluded on the record, not silently:",
        "",
    ]
    out += [f"- `{h}` — {cell(why)}" for h, why in REJECTED_AS_NOT_THE_CHAIN.items()]
    out += [
        "",
        "## B — Poltava oblast: the chats, by district centre",
        "",
        f"{len(chats)} chats with verdict `enter`, across "
        f"{len({t for c in chats for t in towns_of(c)})} of {len(POLTAVA_TOWNS)} district centres"
        " SPEC v2 §3 authorises. The Ukrainian-language bar is LIFTED (operator, 2026-08-30) —"
        f" language is the `ua` column below, not a filter; at the former `ua >= {FORMER_UA_BAR}`"
        " this table held 47 chats and 18 centres. A chat surfaced by two centres' queries is"
        " listed under both and counted once.",
        "",
        "| district centre | chats | handles (subs · msgs/day · dairy · ua) |",
        "|---|--:|---|",
    ]
    by_town: dict[str, list[dict]] = {}
    for chat in chats:
        for town in towns_of(chat):
            by_town.setdefault(town, []).append(chat)
    for town in POLTAVA_TOWNS:
        rows = sorted(
            by_town.get(town, []),
            key=lambda c: -((c.get("stats") or {}).get("messages_per_day") or 0),
        )
        if not rows:
            out.append(f"| {town} | 0 | — |")
            continue
        cells = " · ".join(
            f"{c['handle']} ({c.get('subscribers') or '—'} · "
            f"{num((c.get('stats') or {}).get('messages_per_day'), 1)} · "
            f"{num((c.get('stats') or {}).get('dairy_share'))} · "
            f"ua {(c.get('stats') or {}).get('language_mix', {}).get('ua', 0):.2f})"
            for c in rows
        )
        out.append(f"| {town} | {len(rows)} | {cells} |")

    empty = [t for t in POLTAVA_TOWNS if not by_town.get(t)]
    all_rows = json.loads(R1.read_text(encoding="utf-8"))["rows"]
    out += [
        "",
        f"**{len(empty)} district centres carry no chat in the working set**, for three different"
        " reasons — and the difference decides which of them money can fix:",
        "",
    ]
    out += [f"- **{town}** — {why_empty(town, all_rows)}" for town in empty]
    out += [
        "",
        "## What the two categories are for",
        "",
        "The chains' own channels are a PRICE instrument: of the ones with a channel, almost all",
        "have comments closed, and the open ones are B2B, a marketplace, or carry no dairy. Only",
        "Varus carries dairy under live comments.",
        "",
        "And category B does NOT rescue the brand question, which is the finding this session cost",
        "the most to get: a probe over 4 507 messages from the four liveliest chats found ZERO real",
        "dairy-brand mentions — the watchlist's four hits were «третій ПРЕЗИДЕНТ України» and three",
        "job ads for «ФЕРМА клубники» (`results/poltava_brand_probe.json`, hand-verified). These are",
        "classifieds and job boards: they carry CATEGORY voice at ~78 messages a month for the whole",
        "oblast, and BRAND voice not at all. Whether that is worth collecting is the team lead's",
        "ruling, and it belongs before the remaining 81 candidates are bought.",
    ]
    return "\n".join(out) + "\n"


def main() -> int:
    OUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
