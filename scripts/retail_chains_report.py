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
        }
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
            "no-link": "site READ, twice (HTML and its JS bundle), and carries no t.me link",
            "no-link-in-bundle": "site READ, twice (HTML and its JS bundle), no t.me link",
            "dns": "the contract's candidate domain does not resolve",
            "no-site-verified": "no domain found that both answers and names the chain",
        }.get(row.get("site_status"), row.get("site_status") or "—")
        if row.get("site_status") == "ok" and row.get("handles"):
            why = (
                "site read, and it links only a Telegram bot ("
                + ", ".join(row["handles"])
                + ") — no channel to collect"
            )
        if row["name"] in AGGREGATORS:
            why = row.get("why") or why
        out.append(f"- **{row['name']}** — {why}")
    bots = [r for r in rows if r.get("handles") and not r.get("handle")]
    if bots:
        out += [
            "",
            "Chains whose site links a Telegram BOT but no channel: "
            + ", ".join(
                f"{r['name']} ({', '.join(r['handles'])})" for r in bots if r.get("handles")
            ),
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
