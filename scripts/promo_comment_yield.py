#!/usr/bin/env python3
"""Block 1 — the number the marketing director actually needs: reactions to PRICE PROMO.

The operator's correction, 2026-08-30: «Для анализа реакций на конкретные промо нам не нужны все
комментарии в канале Varus — это лишний шум, нам нужны только комментарии ценовых промо».

So «16.6 comments/day» is the wrong headline: it counts a thread under a recipe and a thread under
a flyer as the same thing. This joins each comment to its parent post through `parent_msg_id` and
splits the corpus three ways — under a PRICE post, under a post with no price, and orphaned — over
the raw store the collector already filled. $0, no Telegram.

Price is `retail_census.PRICE_BRANCHES`, the same matcher the census graded channels with, so the
share here and the `price_share` column are the same instrument. Its `decimal` branch also fires on
dates (r1's own caveat), so the per-branch counts are kept: a yield carried entirely by `decimal`
is a yield to distrust.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse import brands  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402
from retail_census import PRICE_BRANCHES  # noqa: E402

POSTS = REPO_ROOT / "data" / "raw" / "posts"
COMMENTS = REPO_ROOT / "data" / "raw" / "comments"
OUT = REPO_ROOT / "results" / "promo_comment_yield.json"


def rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def price_branches(text: str) -> list[str]:
    return [name for name, pattern in PRICE_BRANCHES.items() if pattern.search(text or "")]


def measure(channel: str, aliases: dict, rules) -> dict | None:
    posts = rows(POSTS / f"{channel}.jsonl")
    comments = rows(COMMENTS / f"{channel}.jsonl")
    if not posts and not comments:
        return None

    by_id, branch_of = {}, {}
    for post in posts:
        pid = str(post.get("msg_id"))
        by_id[pid] = post
        branch_of[pid] = price_branches(post.get("text") or "")

    buckets = defaultdict(list)
    for c in comments:
        parent = str(c.get("parent_msg_id") or "")
        if parent not in by_id:
            # The parent post is outside the collected window: the comment is real and its context
            # is not, so it cannot be graded either way. Counting it as «no price» would invent a
            # verdict about a post nobody read.
            buckets["orphan"].append(c)
        elif branch_of[parent]:
            buckets["under_price"].append(c)
        else:
            buckets["under_no_price"].append(c)

    def brand_hits(items: list[dict]) -> dict:
        hits: dict[str, int] = {}
        for c in items:
            for f in brands.find_watchlist_brands(
                c.get("text") or "", aliases, rules, carrier="comment"
            ):
                hits[f["brand_id"]] = hits.get(f["brand_id"], 0) + 1
        return dict(sorted(hits.items(), key=lambda kv: -kv[1]))

    price_posts = [p for p in posts if branch_of[str(p.get("msg_id"))]]
    branch_totals: dict[str, int] = {}
    for p in price_posts:
        for b in branch_of[str(p.get("msg_id"))]:
            branch_totals[b] = branch_totals.get(b, 0) + 1
    return {
        "channel": channel,
        "posts": len(posts),
        "price_posts": len(price_posts),
        "price_branch_posts": branch_totals,
        "comments": len(comments),
        "under_price": len(buckets["under_price"]),
        "under_no_price": len(buckets["under_no_price"]),
        "orphan": len(buckets["orphan"]),
        "price_threads": len({str(c.get("parent_msg_id")) for c in buckets["under_price"]}),
        "brands_under_price": brand_hits(buckets["under_price"]),
        "brands_under_no_price": brand_hits(buckets["under_no_price"]),
    }


def main() -> int:
    reg = load_registry(REPO_ROOT / "config" / "registry.yaml")
    rules = brands.load_watchlist_rules(brands.RULES)
    aliases = brands.watchlist_aliases(reg.watchlist)

    channels = sorted(
        {p.stem for p in POSTS.glob("*.jsonl")} | {c.stem for c in COMMENTS.glob("*.jsonl")}
    )
    results = [m for ch in channels if (m := measure(ch, aliases, rules))]
    results = [r for r in results if r["comments"]]
    results.sort(key=lambda r: -r["under_price"])

    print(
        f"{'канал':<26}{'постов':>7}{'с ценой':>8}{'комм.':>7}{'под ценой':>10}{'тредов':>7}  бренды под ценой"
    )
    for r in results:
        print(
            f"{r['channel']:<26}{r['posts']:>7}{r['price_posts']:>8}{r['comments']:>7}"
            f"{r['under_price']:>10}{r['price_threads']:>7}  {r['brands_under_price'] or '—'}"
        )
    total = {
        "comments": sum(r["comments"] for r in results),
        "under_price": sum(r["under_price"] for r in results),
        "under_no_price": sum(r["under_no_price"] for r in results),
        "orphan": sum(r["orphan"] for r in results),
        "price_threads": sum(r["price_threads"] for r in results),
    }
    print(
        f"\nВСЕГО: {total['comments']} комментов · под ценовым промо {total['under_price']}"
        f" в {total['price_threads']} тредах · под непромо {total['under_no_price']}"
        f" · сирот {total['orphan']}"
    )
    OUT.write_text(
        json.dumps({"channels": results, "total": total}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
