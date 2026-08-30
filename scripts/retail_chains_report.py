#!/usr/bin/env python3
"""C1 r2 — one row per chain: the Ukraine screen, the aggregators from r1, and the table.

Renders `results/retail_chains_table.md` (all 36 rows) from `results/retail_chains.json`. The
report links it and carries only the rows that answer the operator's question, because a 36-row
table and a 30-line report cannot both fit (`docs/PROCESS.md` «Reports»).

The Ukraine screen is a COLUMN and a filter, exactly as the contract puts it:
  · an r2 row's handle came off the chain's OWN verified Ukrainian site — it keeps, and the reason
    is the site, not the channel's language. `atbmarket.com` and `rozetka.com.ua` are not `.ua`
    and are not rejected for it; step 1 verified whose sites they are.
  · an aggregator row has no site — it was found by r1's name search, which is how «MSUa» returned
    Moscow State University and «Skidka» returned Kazan. Those screen on language at the bar this
    project already uses for «Ukrainian», `ua >= 0.5` (the same bar as r1's 47 Poltava chats), and
    a `ru 1.00` channel with no Ukrainian site behind it is `reject · not the Ukrainian market`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORD = REPO_ROOT / "results" / "retail_chains.json"
R1_RECORD = REPO_ROOT / "results" / "retail_census.json"
TABLE = REPO_ROOT / "results" / "retail_chains_table.md"

UA_BAR = 0.5  # r1's bar for «Ukrainian», reused — not a new threshold

# What a handle turned out to BE, once resolved or read in context. A `t.me` link in a chain's
# own footer proves the chain published it; it does not prove the channel is the chain's retail
# voice. Three of these would otherwise be read as «the chain's channel» in a table that decides
# where the customer's voice gets collected.
CHANNEL_NOTES = {
    "@HRCNc": (
        "resolves to «HoReCaНець» — METRO's HoReCa (hotel/restaurant/café) B2B channel, not its"
        " retail one. Its dairy share is a wholesale audience's, not a shopper's."
    ),
    "@bloom_cherkasy": (
        "the Делікат group's FLORIST brand Bloom, not the grocery chain: delikat.site is «сім'я"
        " магазинів» and the grocery brand's own links there are Facebook and Instagram, neither"
        " of them Telegram. Not counted as Delikat's channel."
    ),
    "@rrozetka": (
        "the marketplace as a whole; the SPEC §3 name is its grocery vertical, which has no"
        " channel of its own — dairy share 0.000 is the marketplace's mix, not a grocer's."
    ),
    "@fozzyshopua": "«FOZZY Cash&Сarry» — the wholesale cash-and-carry format, not a retail store.",
    "@atb_market_official": (
        "«АТБ-МАРКЕТ (офіційна сторінка)», 41 858 subs — ATB's real official channel, found via"
        " atbmarket.com → its official Instagram. It is CORPORATE: price share 0.000 and comments"
        " closed. ATB's promo with comments lives in unofficial deal channels (working_set A3)."
    ),
    "+Ejz6ubzm21IyMTQy": (
        "«Маркетопт 🔆 Офіційна сторінка», 42 378 members — the chain's main channel, found via its"
        " official Instagram because it has no website. JOINED on the operator's word 2026-08-30"
        " (logged in results/joins_5c1.jsonl, reversible), which is what made its history readable:"
        " this is the census's only row measured from inside. media_share 1.000 over 29 posts and"
        " no `грн`/`₴` hit at all — the prices are IN the flyer images, so the 0.276 text share"
        " understates it and the 5c2 vision instrument is what reads this row properly."
    ),
    "@epicentrk_sale": (
        "«ЕПІЦЕНТР», 52 081 subs, price .657 — but NOT linked from Епіцентр's own properties:"
        " epicentrk.ua carries no t.me and the official Instagram @epicentr_ua (191K) carries none"
        " either. It is a SEED handle from the research note, so its identity is the census's"
        " assumption, not the chain's word."
    ),
}

# Handles a chain publishes that are NOT that chain's channel. Kept as an explicit list rather
# than a heuristic: each one is a judgement about a brand, and a reader must see whose.
NOT_THE_CHAINS_CHANNEL = {"Delikat": {"@bloom_cherkasy"}}

# The reverse case: a chain's OWN channel that its own site does not link, so the site-reading
# instrument cannot reach it. r1's name search did, and the channel's own preview confirms whose
# it is. Without this the table says «Близенько has no channel» while the working set's A3 says it
# does — the two instruments are complementary, and the deliverable has to say so in one voice.
CHAIN_OWN_FROM_R1 = {
    "Близенько": (
        "@blyzenkoua",
        "the chain's own channel, «БЛИЗЕНЬКО🌿», preview description «Мережа магазинів Близенько»."
        " blyzenko.ua links no t.me at all, so step 1 could not see it; r1's name search did."
        " Measured on r1's 2026-08-27 clock, not re-measured.",
    ),
}

AGGREGATORS = ["MSUa", "Копійочка", "Знижком", "Хочу дешевше", "Акції та знижки", "Skidka"]


def ua_share(stats: dict) -> float:
    return float((stats.get("language_mix") or {}).get("ua", 0.0))


def screen(*, from_own_site: bool, stats: dict) -> dict:
    if from_own_site:
        return {
            "ukraine_screen": "keep",
            "why": "handle came from the chain's own verified site",
        }
    share = ua_share(stats)
    if share >= UA_BAR:
        return {"ukraine_screen": "keep", "why": f"ua {share:.2f} >= {UA_BAR}"}
    return {
        "ukraine_screen": "reject · not the Ukrainian market",
        "why": f"ua {share:.2f} < {UA_BAR}, and no Ukrainian site backs the handle",
    }


def pick_aggregator(candidates: list[dict]) -> dict | None:
    """One row per aggregator, chosen by a stated rule, with the losers kept in the record.

    r1's name search returned four «MSUa» rows and five «Skidka» rows. Taking the biggest would
    have crowned Moscow State University; taking the first would depend on scan order. The rule:
    among rows that pass the Ukraine screen and are not `reject`, the most subscribed.
    """
    usable = [
        row
        for row in candidates
        if row.get("verdict") in ("enter", "posts-only")
        and screen(from_own_site=False, stats=row.get("stats") or {})["ukraine_screen"] == "keep"
    ]
    if not usable:
        return None
    return max(usable, key=lambda r: r.get("subscribers") or 0)


def r1_by_name() -> dict[str, list[dict]]:
    r1 = json.loads(R1_RECORD.read_text(encoding="utf-8"))
    out: dict[str, list[dict]] = {}
    for row in r1["rows"]:
        if not row.get("checked"):
            continue
        for found in row.get("found_by", []):
            if found.startswith("retail_chains:"):
                out.setdefault(found.split(":", 1)[1], []).append(row)
    return out


def build() -> list[dict]:
    """One flat row per chain, whatever instrument answered for it."""
    state = json.loads(RECORD.read_text(encoding="utf-8"))
    r1 = r1_by_name()
    table = []
    for row in state["rows"]:
        name = row["name"]
        measured = [
            m for m in row.get("measured", []) if m.get("resolved") or m.get("invite_result")
        ]
        entry = {
            "name": name,
            "site": row.get("site"),
            "site_status": row.get("site_status"),
            "method": row.get("method"),
            "handles": row.get("handles", []),
            "kinds": row.get("kinds", {}),
            "no_site_reason": row.get("no_site_reason"),
        }
        disowned = NOT_THE_CHAINS_CHANNEL.get(name, set())
        if disowned:
            entry["not_the_chains_channel"] = sorted(disowned)
            entry["notes"] = [CHANNEL_NOTES[h] for h in sorted(disowned) if h in CHANNEL_NOTES]
        own_from_r1 = CHAIN_OWN_FROM_R1.get(name)
        if not measured and own_from_r1:
            handle, why = own_from_r1
            hit = [c for c in r1.get(name, []) if c["handle"] == handle]
            if hit:
                measured = [
                    {
                        **hit[0],
                        "handle": handle,
                        "measured_by": "api (r1, 2026-08-27)",
                        "provenance": why,
                    }
                ]
                entry["handles"] = sorted({*entry.get("handles", []), handle})
                entry["kinds"] = {**entry.get("kinds", {}), handle: "channel"}
        if measured:
            m = measured[-1]
            stats = m.get("stats") or {}
            entry |= {
                "handle": m.get("handle"),
                "title": m.get("title"),
                "subscribers": m.get("subscribers"),
                "posts_per_day": stats.get("posts_per_day"),
                "price_share": stats.get("price_share"),
                "comments_enabled": m.get("comments_enabled"),
                "comments_per_day": stats.get("comments_per_day"),
                "dairy_share": stats.get("dairy_share"),
                "language_mix": stats.get("language_mix"),
                "n_posts": stats.get("n_posts"),
                "is_group": bool(m.get("megagroup")),
                "messages_per_day": stats.get("messages_per_day"),
                "verdict": m.get("verdict") or m.get("invite_result"),
                "measured_by": m.get("measured_by"),
                "window": m.get("window"),
                "note": m.get("why_unmeasured") or m.get("error"),
                "channel_note": CHANNEL_NOTES.get(m.get("handle")) or m.get("provenance"),
            } | screen(from_own_site=True, stats=stats)
        elif name in AGGREGATORS:
            pick = pick_aggregator(r1.get(name, []))
            others = [
                c["handle"] for c in r1.get(name, []) if not pick or c["handle"] != pick["handle"]
            ]
            if pick:
                stats = pick.get("stats") or {}
                entry |= {
                    "handle": pick["handle"],
                    "title": pick.get("title"),
                    "subscribers": pick.get("subscribers"),
                    "posts_per_day": stats.get("posts_per_day"),
                    "price_share": stats.get("price_share"),
                    "comments_enabled": pick.get("comments_enabled"),
                    "comments_per_day": stats.get("comments_per_day"),
                    "dairy_share": stats.get("dairy_share"),
                    "language_mix": stats.get("language_mix"),
                    "n_posts": stats.get("n_posts"),
                    "is_group": bool(pick.get("megagroup")),
                    "messages_per_day": stats.get("messages_per_day"),
                    "verdict": pick.get("verdict"),
                    # r1's window ENDS 2026-08-27 — three days before the r2 rows. Sorting these
                    # against today's readings without saying so is r1's own api-vs-store lesson.
                    "measured_by": "api (r1, 2026-08-27)",
                    "window": pick.get("window"),
                    "not_chosen": others,
                } | screen(from_own_site=False, stats=stats)
            else:
                entry |= {
                    "handle": None,
                    "verdict": "no Ukrainian channel found",
                    "measured_by": "api (r1, 2026-08-27)",
                    "not_chosen": others,
                    "ukraine_screen": "reject · not the Ukrainian market",
                    "why": f"every r1 row for «{name}» is below ua {UA_BAR} or already rejected",
                }
        else:
            entry |= {"handle": None, "verdict": None, "measured_by": None}
        table.append(entry)
    return table


def sort_key(row: dict) -> tuple:
    """Comments open first, then price share — the contract's order. `no channel` sinks."""
    has = row.get("handle") is not None
    comments = bool(row.get("comments_enabled"))
    price = row.get("price_share")
    return (not has, not comments, -(price if isinstance(price, (int, float)) else -1))


def fmt(value, digits: int = 3) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def traffic(row: dict) -> str:
    """`com/d` for a broadcast; for a megagroup the same column is messages/day, marked `*`.

    A group has no «comments under a post» — its whole traffic IS the conversation. Printing
    `messages_per_day` unmarked in a column headed `com/d` would make the two comparable when
    they are not, and printing `—` would read as «nobody writes there».
    """
    if row.get("is_group"):
        return f"{fmt(row.get('messages_per_day'))}*"
    return fmt(row.get("comments_per_day"))


def lang(row: dict) -> str:
    mix = row.get("language_mix") or {}
    if not mix:
        return "—"
    return " ".join(f"{k} {v:.2f}" for k, v in sorted(mix.items(), key=lambda kv: -kv[1])[:2])


def render(table: list[dict]) -> str:
    rows = sorted(table, key=sort_key)
    out = [
        "# retail-census r2 — one row per chain (36 rows)",
        "",
        "Built by `scripts/retail_chains_report.py` from `results/retail_chains.json`. Sorted by",
        "comments open, then price share; rows with no channel are at the bottom and say why.",
        "`instr.` is which instrument read the site (`curl` · `curl+bundle` · `browser`), and",
        "`measured` is which census measured the channel — r1's window ends 2026-08-27, r2's",
        "2026-08-30, so the two must not be read as one clock. `n` is the posts the shares were",
        "computed over — `price 1.000` over n=10 is not the claim `price 0.762` over n=168 is.",
        "A `*` on `com/d` marks a megagroup, where the column is messages/day: a group has no",
        "comments under posts, its whole traffic is the conversation.",
        "",
        "| # | chain | site | site read | instr. | handle | subs | posts/d | n | price |"
        " comments | com/d | dairy | language | verdict | Ukraine screen | measured |",
        "|--:|---|---|---|---|---|--:|--:|--:|--:|---|--:|--:|---|---|---|---|",
    ]
    for i, row in enumerate(rows, 1):
        out.append(
            "| {n} | {name} | {site} | {status} | {instr} | {handle} | {subs} | {ppd} | {np} |"
            " {price} | {comm} | {cpd} | {dairy} | {lang} | {verdict} | {screen} | {measured} |".format(
                n=i,
                name=row["name"],
                site=row.get("site") or "—",
                status=row.get("site_status") or "—",
                instr=row.get("method") or "—",
                handle=row.get("handle") or "—",
                subs=fmt(row.get("subscribers")),
                ppd=fmt(row.get("posts_per_day")),
                np=fmt(row.get("n_posts")),
                price=fmt(row.get("price_share")),
                comm=fmt(row.get("comments_enabled")),
                cpd=traffic(row),
                dairy=fmt(row.get("dairy_share")),
                lang=lang(row),
                verdict=row.get("verdict") or "—",
                screen=row.get("ukraine_screen") or "—",
                measured=row.get("measured_by") or "—",
            )
        )
    out += ["", "## Why a row has no channel", ""]
    for row in rows:
        if row.get("handle"):
            continue
        why = {
            "blocked": "site never read — Cloudflare 403 to curl, and Chrome has no permission"
            " for this domain in this session",
            "shell": "site never read — one client-rendered shell for every path, and its own JS"
            " bundle carries no t.me either",
            "no-link": (
                "site READ in a browser and carrying no t.me link"
                if row.get("method") == "browser"
                else "site READ, twice (HTML and its JS bundle), and carries no t.me link"
            ),
            "no-link-in-bundle": "site READ, twice (HTML and its JS bundle), no t.me link",
            "dns": "the contract's candidate domain does not resolve",
            "no-site-verified": "no domain found that both answers and names the chain",
        }.get(row.get("site_status"), row.get("site_status") or "—")
        # A row whose discovery established WHY there is no site says that instead: «no domain
        # found» covers a chain with only an Instagram and a brand that stopped existing in 2016.
        if row.get("no_site_reason"):
            why = row["no_site_reason"]
        if row.get("site_status") == "ok" and row.get("handles"):
            disowned = NOT_THE_CHAINS_CHANNEL.get(row["name"], set())
            if disowned:
                why = "site read; its only Telegram is " + "; ".join(
                    CHANNEL_NOTES[h] for h in sorted(disowned) if h in CHANNEL_NOTES
                )
            else:
                why = (
                    "site read, and it links only a Telegram bot ("
                    + ", ".join(row["handles"])
                    + ") — no channel to collect"
                )
        if row["name"] in AGGREGATORS:
            why = row.get("why") or why
        out.append(f"- **{row['name']}** — {why}")
    # Only handles the classifier calls bots: `@bloom_cherkasy` is a CHANNEL that belongs to
    # another brand of Delikat's group, and listing it here would answer «Delikat links a bot».
    bots = [
        (row, [h for h in row.get("handles", []) if row.get("kinds", {}).get(h) == "bot"])
        for row in rows
        if not row.get("handle")
    ]
    bots = [(row, found) for row, found in bots if found]
    if bots:
        out += [
            "",
            "Chains whose site links a Telegram BOT and no channel: "
            + ", ".join(f"{row['name']} ({', '.join(found)})" for row, found in bots),
        ]
    return "\n".join(out) + "\n"


def main() -> int:
    table = build()
    TABLE.write_text(render(table), encoding="utf-8")
    print(f"wrote {TABLE.relative_to(REPO_ROOT)} — {len(table)} rows")
    with_channel = [r for r in table if r.get("handle")]
    open_comments = [r for r in with_channel if r.get("comments_enabled")]
    print(f"{len(with_channel)} chains with a channel · {len(open_comments)} with comments open")
    for row in sorted(with_channel, key=sort_key):
        print(
            f"  {row['name']:<18}{str(row.get('handle')):<22}"
            f"comments={fmt(row.get('comments_enabled')):<4} price={fmt(row.get('price_share'))} "
            f"dairy={fmt(row.get('dairy_share'))} {row.get('ukraine_screen')}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
