#!/usr/bin/env python3
"""Screen the launch composition against the tracked category, from the window already collected.

Why this exists: the 5c1 gate verified CAPABILITY — does the handle resolve, is the channel
alive, is it UA/RU, is there an open discussion group, do its posts carry comments. It never
verified THEME, except for the two channels the operator pre-registered by name. The composition's
themes came from the 5a1 discovery tags, and a discovery tag is what a search query matched, not
what a channel is about: @uasaler was tagged `supermarket_deals:знижки` and turned out to be an
AliExpress affiliate feed whose discussion group is «Чат Аліекспрес».

So this measures, per launch channel, how much of its own 28-day window touches dairy or ice
cream at all. $0 and offline: it reads `data/raw/posts/` and talks to nobody.

It is a SCREEN, not a verdict, and the difference matters twice over. The lexicon is
`scripts/measure_categories.py`'s and says so about itself — `"status": "draft-not-law"` — with a
known collision (`сир` + `ий` matches «креветка сира»). And a low share is not automatically bad:
a mothers-and-kids channel that mentions dairy in one post of forty may still be where the
comments about that one post are worth more than a promo channel's whole feed. What the table
answers is "which of these are plausibly about food at all", which is the question @uasaler failed.

    PYTHONPATH=src python3 scripts/theme_screen_5c1.py
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import measure_categories as cat  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

from market_pulse.brands import find_watchlist_brands, watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
GATE_RECORD = REPO_ROOT / "results" / "entry_gate_5c1.json"
STORE = REPO_ROOT / "data" / "raw" / "posts"
RECORD = REPO_ROOT / "results" / "theme_screen_5c1.json"

TRACKED = ("dairy", "ice-cream")
"""The tracked groups of `config/registry.yaml`. Everything else the lexicon knows is a draft
family and is reported as "food at all", which is the weaker and more forgiving question."""


def posts_of(handle: str) -> list[dict]:
    path = STORE / f"{handle.lstrip('@')}.jsonl"
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def screen(handle: str, compiled: dict, aliases: dict) -> dict:
    """One channel's window, measured against the lexicon."""
    posts = posts_of(handle)
    texts = [(row.get("text") or "").strip() for row in posts]
    with_text = [text for text in texts if text]
    tracked_hits, food_hits, brands, examples = 0, 0, {}, []
    for text in with_text:
        families = cat.categories_of(text, compiled)
        on_category = [key for key in families if key in TRACKED]
        if on_category:
            tracked_hits += 1
            if len(examples) < 3:
                terms = cat.matched_terms(text, compiled)
                examples.append(
                    {"terms": {k: v for k, v in terms.items() if k in TRACKED}, "text": text[:140]}
                )
        if families:
            food_hits += 1
        for hit in find_watchlist_brands(text, aliases):
            brands[hit["brand_id"]] = brands.get(hit["brand_id"], 0) + 1
    return {
        "channel": handle,
        "posts_in_window": len(posts),
        "posts_with_text": len(with_text),
        "tracked_posts": tracked_hits,
        "tracked_share": round(tracked_hits / len(with_text), 3) if with_text else None,
        "any_food_posts": food_hits,
        "any_food_share": round(food_hits / len(with_text), 3) if with_text else None,
        "watchlist_hits": dict(sorted(brands.items(), key=lambda kv: -kv[1])),
        "examples": examples,
    }


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)

    registry = load_registry(REGISTRY)
    gate = json.loads(GATE_RECORD.read_text(encoding="utf-8"))
    composition = gate["rulings"]["composition"]
    bucket_of = {
        handle: name
        for name, handles in composition.items()
        if name != "excluded"
        for handle in handles
    }
    compiled = cat.patterns(cat.build_lexicon(registry))
    aliases = watchlist_aliases(list(registry.watchlist))

    rows = [screen(handle, compiled, aliases) for handle in bucket_of]
    for row in rows:
        row["bucket"] = bucket_of[row["channel"]]

    scored = [row for row in rows if row["posts_with_text"]]
    scored.sort(key=lambda row: (row["tracked_share"], row["any_food_share"]))

    header = f"{'channel':<30}{'bucket':<10}{'posts':>6}{'dairy':>7}{'food':>7}  watchlist"
    print(header)
    print("-" * len(header))
    for row in scored:
        brands = " ".join(f"{k}:{v}" for k, v in list(row["watchlist_hits"].items())[:3]) or "—"
        print(
            f"{row['channel'][:29]:<30}{row['bucket']:<10}{row['posts_with_text']:>6}"
            f"{row['tracked_share']:>7}{row['any_food_share']:>7}  {brands}"
        )
    silent = [row for row in rows if not row["posts_with_text"]]
    if silent:
        print(f"\nno text in the window ({len(silent)}): {' '.join(r['channel'] for r in silent)}")

    zero = [row for row in scored if row["tracked_posts"] == 0]
    print(
        f"\n{len(scored)} channels measured · {len(zero)} with ZERO dairy/ice-cream posts"
        f" · {sum(1 for r in scored if r['any_food_posts'] == 0)} with zero food posts of any kind"
    )

    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "5c1",
        "asks": (
            "how much of each launch channel's own 28-day window touches the tracked category."
            " The gate never measured theme; @uasaler is why that gap is worth a number."
        ),
        "lexicon": cat.build_lexicon(registry),
        "tracked_groups": list(TRACKED),
        "source": "data/raw/posts/ — the window collected by scripts/collect_5c1.py --posts",
        "caveats": [
            "a SCREEN, not a verdict: the lexicon calls itself draft-not-law and has a known"
            " collision (сир + ий matches «креветка сира»)",
            "a low share is not automatically bad — one dairy post in forty can still carry the"
            " comments worth reading; what this catches is a channel not about food at all",
            "post text only. Comments are where the model's rows come from and most channels'"
            " comments are not collected yet",
        ],
        "channels": rows,
        "git": git_state(RECORD),
    }
    RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {RECORD.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
