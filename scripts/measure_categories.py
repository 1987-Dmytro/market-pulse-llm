"""Four category measurements over the corpus we already have. No model, no gold, $0.

The amendment candidate of 2026-08-03 says a category is a property of the POST and
comments inherit it through `parent_msg_id`. Nothing here decides that — the taxonomy
is the operator's word later. This measures whether the signal is *there*: how many
posts a keyword lexicon can read a category out of, how often a comment talks about a
different category than its post, how often a post names a concrete position, and how
often a comment compares two brands.

Every share is a LOWER BOUND. The lexicon is a draft (`data/category_lexicon_draft.json`,
`status: draft-not-law`), the matcher is stem + a closed set of inflectional endings, and
Ukrainian morphology beyond that set is missed on purpose: a looser matcher reads
`супермаркет` as `суп`. The ten examples printed with every measure are the check on
that, not decoration.

Usage: PYTHONPATH=src python3 scripts/measure_categories.py
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from precheck_45h import scoreable  # noqa: E402  — one definition of "scoreable", not two

from market_pulse import lexicon  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

RAW_POSTS = REPO_ROOT / "data" / "raw" / "posts"
RAW_COMMENTS = REPO_ROOT / "data" / "raw" / "comments_v2"
FROZEN = REPO_ROOT / "data" / "frozen"
ANNOTATION = REPO_ROOT / "data" / "annotation"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
LEXICON = REPO_ROOT / "data" / "category_lexicon_draft.json"
RECORD = REPO_ROOT / "results" / "categories_45h.json"

EXAMPLES = 10

ENDINGS = (
    "",
    "а",
    "у",
    "и",
    "і",
    "е",
    "о",
    "я",
    "ю",
    "ї",
    "й",
    "ы",
    "ів",
    "ой",
    "ою",
    "ом",
    "ем",
    "ім",
    "ам",
    "ям",
    "ах",
    "ях",
    "ей",
    "ов",
    "ий",
    "их",
    "ій",
    "ої",
    "не",
    "на",
    "ні",
    "ами",
    "ями",
    "ими",
    "ого",
    "ому",
)
"""Inflectional endings only. `чайник` is `чай` + a derivational suffix and is not a
tea; `супермаркет` is `суп` + `ермаркет`; both are excluded by keeping this set closed
rather than allowing "any few letters". The one collision left is `сир` + `ий` —
`креветка сира` (raw shrimp) reads as curd on 11 posts, and it is named here rather
than patched away, because a stop-list of forms is where a draft lexicon starts
pretending to be law."""

TRACKED_STEMS = {
    "dairy": [
        "молок",
        "молочн",
        "кефір",
        "кефир",
        "ряжанк",
        "йогурт",
        "сир",
        "сирк",
        "творог",
        "сметан",
        "масл",
        "десерт",
        "рослинн",
        "аналог",
    ],
    "ice-cream": ["морозив", "морожен"],
}
"""Stems for the two tracked groups. Every one is checked against the registry's own
display names at build time, so a typo here fails instead of quietly measuring nothing."""

RU_VARIANTS = frozenset({"кефир", "творог", "морожен"})
"""The Russian forms of a tracked stem. The registry's display names are Ukrainian, so
these have nothing to be a prefix of and are exempt from that check — named one by one
rather than by loosening the check, which is the only thing keeping a typo visible. The
corpus is UA/RU mixed (SPEC §1) and dropping them would undercount the RU half."""

DRAFT_STEMS = {
    "confectionery": ["шокола", "цукерк", "конфет", "печив", "торт", "пастил", "вафл"],
    "meat": ["ковбас", "м'яс", "мясо", "курк", "куриц", "сосиск", "шинк"],
    "bakery": ["хліб", "булоч", "випічк", "круасан", "багет"],
    "drinks": ["напій", "напит", "пиво", "вино", "віскі", "виски", "кав", "чай", "сік", "сок"],
    "seafood": ["риб", "креветк", "оселедц", "лосос", "мідії"],
    "produce": [
        "овоч",
        "овощ",
        "фрукт",
        "ягод",
        "яблук",
        "банан",
        "помідор",
        "огірк",
        "картопл",
        "цибул",
        "моркв",
        "капуст",
    ],
    "grocery": ["макарон", "крупа", "рис", "гречк", "олі", "борошн", "цукор", "сіль"],
    "ready-meals": [
        "вареник",
        "пельмен",
        "піц",
        "пицц",
        "суші",
        "салат",
        "борщ",
        "суп",
        "млинц",
        "сирни",
        "кімч",
        "кимч",
        "готов",
    ],
    "snacks": ["снек", "чіпс", "чипс", "горіх", "сухарик"],
    "sauces": ["соус", "кетчуп", "майонез", "гірчиц"],
    "eggs": ["яйц"],
    "preserved": ["консерв", "заморож"],
}
"""Families the posts talk about that the registry does not track — вареники, кімчі and
the rest. Draft, and only here to answer "how much of the corpus is outside the tracked
category", which is the number that says whether a category layer needs more than two
groups."""

UNIT = re.compile(r"(?<!\w)(\d+(?:[.,]\d+)?)\s*(г|кг|мл|л|шт|%)(?!\w)")
"""A pack-size or volume token. The right-hand boundary is what keeps `300 грн` out of
`\\d+ г`, and `%` is counted separately below because a retail post is full of `знижка
20%` — a discount is not a position."""
DECIMAL_PERCENT = re.compile(r"(?<!\w)\d+[.,]\d+\s*%(?!\w)")
"""`2,5%` — a fat percentage reads like a position; `20%` reads like a promo."""

COMPARISON = (
    "краще",
    "гірше",
    "ніж",
    "смачніше",
    "дешевше",
    "дорожче",
    "найкращ",
    "найсмачніш",
    "лучше",
    "хуже",
    "чем",
    "вкуснее",
    "дешевле",
    "дороже",
    "порівняно",
    "на відміну",
)
"""Draft comparison markers. `за` is deliberately NOT in this list on its own: in
Ukrainian it means "than" only after a comparative (`смачніше за`), and everywhere else
it is for/behind/by (`за 20 грн`, `за акцією`). It is measured as a separate counter
below so the sensitivity is visible instead of baked in."""
COMPARATIVE_ZA = re.compile(
    r"(?<!\w)(?:\w+(?:іше|ішим|іший|іша|ше|ща|щий|щі)|краще|гірше|більше|менше)\s+за(?!\w)"
)
"""`за` counted only where a comparative stands in front of it."""

RETAILER_ENTRIES = frozenset({"varus-pl", "varto"})
"""Watchlist entries that name the retailer whose channel this is, or its private label.
`VARUS` and `VARTO` are on the watchlist and are matched like any brand — but a comment
on @VARUS_channel naming VARUS is not comparing two products, and a pair measure that
counts it would price an amendment on noise. Reported both ways, gated on neither."""


def word(stem: str) -> re.Pattern:
    alts = "|".join(sorted({re.escape(end) for end in ENDINGS}, key=len, reverse=True))
    return re.compile(rf"(?<!\w){re.escape(stem)}(?:{alts})(?!\w)")


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def load(path: Path) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def load_dir(directory: Path) -> list[dict]:
    return [row for path in sorted(directory.glob("*.jsonl")) for row in load(path)]


# --- the draft lexicon --------------------------------------------------------
def build_lexicon(registry) -> dict:
    """Tracked stems checked against the registry's display names, draft stems beside them."""
    # the rule itself lives in `market_pulse.lexicon` since uni-b, so the law in
    # `config/lexicon.yaml` and this draft are held to ONE implementation of it
    bad = lexicon.unmatched_stems(TRACKED_STEMS, registry.taxonomy, exempt=RU_VARIANTS)
    for key, unmatched in sorted(bad.items()):
        if not unmatched:
            raise SystemExit(f"{key} is not a tracked group of {rel(REGISTRY)}")
        raise SystemExit(
            f"{key}: {unmatched} are not prefixes of any display name in the registry —"
            " a tracked stem that names nothing measures nothing"
        )
    return {
        "status": "draft-not-law",
        "note": (
            "A DRAFT keyword lexicon built for one measurement (docs/PROMPT-4.5h.md Step 2)."
            " The tracked half is seeded from config/registry.yaml tracked_groups display names"
            " and every stem is asserted to be a prefix of one; the rest are draft families seen"
            " in the posts. This is not the taxonomy — the taxonomy is the operator's word later,"
            " and nothing reads this file except scripts/measure_categories.py."
        ),
        "matcher": "stem + one of `endings`, bounded by non-word characters on both sides",
        "endings": list(ENDINGS),
        "known_collision": "сир + ий matches `креветка сира` (raw shrimp) on 11 posts",
        "tracked": {key: sorted(stems) for key, stems in sorted(TRACKED_STEMS.items())},
        "draft": {key: sorted(stems) for key, stems in sorted(DRAFT_STEMS.items())},
    }


def patterns(lexicon: dict) -> dict[str, list[re.Pattern]]:
    families = {**lexicon["tracked"], **lexicon["draft"]}
    return {key: [word(stem) for stem in stems] for key, stems in sorted(families.items())}


def categories_of(text: str, compiled: dict[str, list[re.Pattern]]) -> list[str]:
    low = text.casefold()
    return sorted(key for key, pats in compiled.items() if any(p.search(low) for p in pats))


def matched_terms(text: str, compiled: dict[str, list[re.Pattern]]) -> dict[str, list[str]]:
    """The words that actually fired, per family — the examples are the audit of the
    lexicon, and an example that does not show what matched cannot be audited."""
    low = text.casefold()
    found = {
        key: sorted({m.group(0) for p in pats for m in p.finditer(low)})
        for key, pats in compiled.items()
    }
    return {key: words for key, words in found.items() if words}


# --- brands and positions -----------------------------------------------------
def brand_hits(text: str, aliases: dict[str, str]) -> list[tuple[int, str]]:
    """(offset, brand_id) for every watchlist display name in the text.

    The alias table is `market_pulse.brands.watchlist_aliases` — the same table G1e is
    scored against — so "a brand hit" means here what it means to the scorer.
    """
    low = text.casefold()
    found = []
    for alias, brand_id in aliases.items():
        for match in re.finditer(rf"(?<!\w){re.escape(alias)}(?!\w)", low):
            found.append((match.start(), brand_id))
    return sorted(found)


VOWELS = "аеиоуяюєіїы"


def brand_hits_inflected(text: str, aliases: dict[str, str]) -> list[tuple[int, str]]:
    """The same brands, read through the case system — a strictly wider set.

    The exact matcher above is the scorer's, and the scorer's is right for G1e: a
    prediction is graded against a display name. It is the wrong instrument for asking
    "how often does a comment mention two brands", because Ukrainian declines them —
    the operator's own canonical example, «Морозиво пломбір Рудь смачніший за
    Гармонію», names `Гармонія` in the accusative and the exact matcher does not see
    it. Both counts are reported; neither is gated, and this one is the looser of the
    two (`Премія` the brand and `премію` the prize are one token to it).
    """
    low = text.casefold()
    found = []
    for alias, brand_id in aliases.items():
        stem = alias[:-1] if alias[-1] in VOWELS and len(alias) > 3 else alias
        for match in word(stem).finditer(low):
            found.append((match.start(), brand_id))
    return sorted(found)


def position_span(text: str, compiled: dict, aliases: dict) -> dict | None:
    """The first line that carries a unit token beside a category or brand hit."""
    for line in text.splitlines():
        units = list(UNIT.finditer(line))
        if not units:
            continue
        cats = categories_of(line, compiled)
        brands = brand_hits(line, aliases)
        if not cats and not brands:
            continue
        return {
            "line": " ".join(line.split()),
            "unit": units[0].group(0),
            "unit_is_percent": units[0].group(2) == "%",
            "unit_is_decimal_percent": bool(DECIMAL_PERCENT.search(units[0].group(0))),
            "categories": cats,
            "brands": sorted({brand for _, brand in brands}),
        }
    return None


def sentences(text: str) -> list[str]:
    return [part for part in re.split(r"[.!?…\n]+", text) if part.strip()]


def comparison_marker(sentence: str) -> str | None:
    """The first comparison marker in the sentence, matched on word boundaries.

    A bare `in` test reads `чем` out of `Зачем` and `ніж` out of `ніжний`, which is
    how a five-row measure becomes a fifty-row one made of nothing.
    """
    low = sentence.casefold()
    for marker in COMPARISON:
        pattern = (
            re.compile(rf"(?<!\w){re.escape(marker)}(?!\w)") if " " in marker else word(marker)
        )
        if pattern.search(low):
            return marker
    found = COMPARATIVE_ZA.search(low)
    return found.group(0) if found else None


# --- the four measures --------------------------------------------------------
def coverage(posts: list[dict], compiled: dict, tracked: set[str]) -> dict:
    """`tracked` comes from `config/registry.yaml` — uni-a's LEAK L3.

    It was the literal `{"dairy", "ice-cream"}`, sitting inside the lexicon's own producer: the one
    file that already holds a registry and checks every stem against it still restated the taxonomy
    by hand. `share_of_texted_naming_tracked` would have kept counting dairy under a new category.
    """
    texted = [post for post in posts if post.get("text")]
    read = [(post, categories_of(post["text"], compiled)) for post in texted]
    with_signal = [(post, cats) for post, cats in read if cats]
    if not tracked & set(compiled):
        raise SystemExit(
            f"the registry tracks {sorted(tracked)} and the lexicon compiles {sorted(compiled)} —"
            " no group is in both, so `posts_naming_a_tracked_group` would be a measured zero and"
            " read as a fact about the corpus"
        )
    tracked_only = [(p, c) for p, c in with_signal if set(c) & tracked]
    return {
        "posts": len(posts),
        "posts_with_text": len(texted),
        "posts_without_text": len(posts) - len(texted),
        "posts_with_a_category_signal": len(with_signal),
        "share_of_all_posts": len(with_signal) / len(posts),
        "share_of_texted_posts": len(with_signal) / len(texted),
        "posts_naming_a_tracked_group": len(tracked_only),
        "share_of_texted_naming_tracked": len(tracked_only) / len(texted),
        "per_family": {key: sum(1 for _, cats in read if key in cats) for key in sorted(compiled)},
        "examples": [
            {
                "id": f"{p['channel']}:{p['msg_id']}",
                "categories": c,
                "matched": matched_terms(p["text"], compiled),
                "text": short(p["text"]),
            }
            for p, c in sorted(with_signal, key=lambda pair: pair[0]["msg_id"])[:EXAMPLES]
        ],
    }


def short(text: str, limit: int = 160) -> str:
    one = " ".join(text.split())
    return one if len(one) <= limit else one[:limit] + "…"


def cross_category(comments: list[dict], posts: dict, compiled: dict, label: str) -> dict:
    both, cross = [], []
    for comment in comments:
        text = comment.get("text") or ""
        parent = posts.get((comment["channel"], comment.get("parent_msg_id")))
        if not text or not parent or not parent.get("text"):
            continue
        post_cats = set(categories_of(parent["text"], compiled))
        own = set(categories_of(text, compiled))
        if not post_cats or not own:
            continue
        both.append(comment)
        if own - post_cats:
            cross.append((comment, sorted(post_cats), sorted(own)))
    return {
        "population": label,
        "rows": len(comments),
        "rows_where_both_sides_name_a_category": len(both),
        "cross_category_rows": len(cross),
        "share_of_comparable_rows": len(cross) / len(both) if both else 0.0,
        "share_of_all_rows": len(cross) / len(comments) if comments else 0.0,
        "examples": [
            {
                "id": comment["id"]
                if "id" in comment
                else f"{comment['channel']}:{comment['msg_id']}",
                "channel": comment["channel"],
                "post_category": post_cats,
                "comment_category": own,
                "matched_in_comment": matched_terms(comment["text"], compiled),
                "text": short(comment["text"]),
            }
            for comment, post_cats, own in sorted(cross, key=lambda triple: triple[0]["msg_id"])[
                :EXAMPLES
            ]
        ],
    }


def positions(posts: list[dict], compiled: dict, aliases: dict, source_type: dict) -> dict:
    texted = [post for post in posts if post.get("text")]
    hits = [(post, position_span(post["text"], compiled, aliases)) for post in texted]
    named = [(post, span) for post, span in hits if span]
    percent_only = [(p, s) for p, s in named if s["unit_is_percent"]]
    decimal_percent = [(p, s) for p, s in percent_only if s["unit_is_decimal_percent"]]
    by_type: dict[str, dict] = {}
    for kind in sorted({source_type[post["source_id"]] for post in texted}):
        pool = [post for post in texted if source_type[post["source_id"]] == kind]
        found = [post for post, span in named if source_type[post["source_id"]] == kind]
        by_type[kind] = {
            "posts_with_text": len(pool),
            "naming_a_position": len(found),
            "share": len(found) / len(pool) if pool else 0.0,
        }
    return {
        "posts_with_text": len(texted),
        "naming_a_position": len(named),
        "share_of_texted_posts": len(named) / len(texted),
        "of_which_the_unit_is_percent": len(percent_only),
        "of_which_a_decimal_percent": len(decimal_percent),
        "share_excluding_percent_units": (len(named) - len(percent_only)) / len(texted),
        "by_source_type": by_type,
        "examples": [
            {
                "id": f"{post['channel']}:{post['msg_id']}",
                "source_type": source_type[post["source_id"]],
                "matched_span": span["line"],
                "unit": span["unit"],
                "categories": span["categories"],
                "brands": span["brands"],
            }
            for post, span in sorted(named, key=lambda pair: pair[0]["msg_id"])[:EXAMPLES]
        ],
    }


def row_id(row: dict) -> str:
    return row.get("id") or f"{row['channel']}:{row['msg_id']}"


def comparisons(comments: list[dict], compiled: dict, aliases: dict, label: str) -> dict:
    """Both readings of "a brand hit", side by side. The exact one is the scorer's."""
    rows = [(row, row.get("text") or "") for row in comments]
    rows = [(row, text) for row, text in rows if text]
    strict = one_reading(rows, compiled, aliases, brand_hits)
    return {
        "population": label,
        "rows_with_text": len(rows),
        "brand_matching": (
            "`exact` is market_pulse.brands — the display name as written, the way G1e is"
            " scored. `inflected` allows the case endings and is a strictly wider, looser"
            " count; the operator's canonical example needs it, because «Гармонію» is not"
            " «Гармонія». Neither is law; both are reported."
        ),
        **strict,
        "inflected": one_reading(rows, compiled, aliases, brand_hits_inflected),
    }


def one_reading(rows: list[tuple[dict, str]], compiled: dict, aliases: dict, hits_of) -> dict:
    a, b, c, za_only = [], [], [], []
    any_brand, any_marker, product_pairs = [], [], []
    for row, text in rows:
        hits = hits_of(text, aliases)
        brands = {brand for _, brand in hits}
        two_brands = len(brands) >= 2
        if brands:
            any_brand.append(row)
        if any(comparison_marker(sentence) for sentence in sentences(text)):
            any_marker.append(row)
        if len(brands - RETAILER_ENTRIES) >= 2:
            product_pairs.append(row)
        marker, marker_za = None, None
        for sentence in sentences(text):
            if not hits_of(sentence, aliases):
                continue
            found = comparison_marker(sentence)
            if found and COMPARATIVE_ZA.fullmatch(found):
                marker_za = marker_za or found
            elif found:
                marker = marker or found
        span = position_span(text, compiled, aliases)
        own_categories = categories_of(text, compiled)
        if two_brands:
            a.append((row, sorted(brands)))
        if marker or marker_za:
            b.append((row, marker or marker_za))
        if marker_za and not marker:
            za_only.append(row_id(row))
        if span or own_categories:
            c.append((row, span, own_categories))

    ids = {
        "a": {row_id(row) for row, _ in a},
        "b": {row_id(row) for row, _ in b},
        "c": {row_id(row) for row, _, _ in c},
        "product_pairs": {row_id(row) for row in product_pairs},
    }
    total = len(rows)

    def share(count: int) -> float:
        return count / total if total else 0.0

    return {
        "context": {
            "rows_naming_at_least_one_watchlist_brand": len(any_brand),
            "rows_with_any_comparison_marker_anywhere": len(any_marker),
            "note": (
                "the denominators the gated measures sit inside: (b) needs the marker and the"
                " brand in ONE sentence, so it can only ever be a subset of both"
            ),
        },
        "a_two_or_more_watchlist_brands": {
            "rows": len(ids["a"]),
            "share": share(len(ids["a"])),
            "rows_excluding_the_retailer_entries": len(ids["product_pairs"]),
            "retailer_entries_excluded": sorted(RETAILER_ENTRIES),
            "examples": [
                {"id": row_id(row), "brands": brands, "text": short(row.get("text", ""))}
                for row, brands in sorted(a, key=lambda pair: row_id(pair[0]))[:EXAMPLES]
            ],
        },
        "b_comparison_marker_beside_a_brand": {
            "rows": len(ids["b"]),
            "share": share(len(ids["b"])),
            "rows_carried_only_by_the_comparative_za": len(za_only),
            "share_without_za": share(len(ids["b"]) - len(za_only)),
            "examples": [
                {"id": row_id(row), "marker": marker, "text": short(row.get("text", ""))}
                for row, marker in sorted(b, key=lambda pair: row_id(pair[0]))[:EXAMPLES]
            ],
        },
        "c_position_or_category_token": {
            "rows": len(ids["c"]),
            "share": share(len(ids["c"])),
            "rows_with_a_unit_token_beside_a_hit": sum(1 for _, span, _ in c if span),
            "rows_with_a_category_word_only": sum(1 for _, span, _ in c if not span),
            "examples": [
                {
                    "id": row_id(row),
                    "span": span["line"] if span else None,
                    "categories": cats,
                    "text": short(row.get("text", "")),
                }
                for row, span, cats in sorted(c, key=lambda triple: row_id(triple[0]))[:EXAMPLES]
            ],
        },
        "intersections": {
            "a_and_b": len(ids["a"] & ids["b"]),
            "a_and_b_share": share(len(ids["a"] & ids["b"])),
            "a_and_b_and_c": len(ids["a"] & ids["b"] & ids["c"]),
            "a_and_b_and_c_share": share(len(ids["a"] & ids["b"] & ids["c"])),
            "a_and_b_ids": sorted(ids["a"] & ids["b"])[:EXAMPLES],
            "a_and_b_and_c_ids": sorted(ids["a"] & ids["b"] & ids["c"])[:EXAMPLES],
            "product_pairs_and_b": len(ids["product_pairs"] & ids["b"]),
            "product_pairs_and_b_and_c": len(ids["product_pairs"] & ids["b"] & ids["c"]),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--lexicon", type=Path, default=LEXICON)
    args = parser.parse_args(argv)

    registry = load_registry(REGISTRY)
    aliases = watchlist_aliases(registry.watchlist)
    source_type = {source.id: source.source_type for source in registry.sources}
    lexicon = build_lexicon(registry)
    args.lexicon.write_text(
        json.dumps(lexicon, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    compiled = patterns(lexicon)

    posts = load_dir(RAW_POSTS)
    post_index = {(post["channel"], post["msg_id"]): post for post in posts}
    comments = load_dir(RAW_COMMENTS)
    train = scoreable(load(FROZEN / "comments_train.jsonl")) + scoreable(
        load(ANNOTATION / "sarcasm_candidates.jsonl")
    )
    test = load(FROZEN / "comments_test.jsonl")

    record = {
        "step": "4.5h Step 2 — category measurements",
        "produced_by": "scripts/measure_categories.py",
        "spend_usd": 0.0,
        "lexicon": rel(args.lexicon),
        "lexicon_status": lexicon["status"],
        "caveat": (
            "every share is a lower bound: a draft lexicon, stem + closed inflectional endings,"
            " and no morphology beyond it"
        ),
        "post_category_coverage": coverage(posts, compiled, set(registry.taxonomy.tracked_groups)),
        "cross_category_comments": [
            cross_category(comments, post_index, compiled, "all comments (raw v2 store)"),
            cross_category(train, post_index, compiled, "scoreable train rows"),
        ],
        "post_position_mentions": positions(posts, compiled, aliases, source_type),
        "comment_comparisons": [
            comparisons(comments, compiled, aliases, "all comments (raw v2 store)"),
            comparisons(train, compiled, aliases, "scoreable train rows"),
            comparisons(test, compiled, aliases, "comments_test.jsonl (400 rows)"),
        ],
    }
    args.record.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    cover = record["post_category_coverage"]
    print(f"lexicon: {rel(args.lexicon)} ({lexicon['status']})")
    print(f"record:  {rel(args.record)}")
    print(
        f"  coverage {cover['posts_with_a_category_signal']}/{cover['posts_with_text']} texted"
        f" posts ({cover['share_of_texted_posts']:.1%}), {cover['posts_without_text']} have no text"
    )
    for measure in record["cross_category_comments"]:
        print(
            f"  cross-category {measure['population']}: {measure['cross_category_rows']} of"
            f" {measure['rows_where_both_sides_name_a_category']} comparable"
            f" ({measure['share_of_comparable_rows']:.1%})"
        )
    pos = record["post_position_mentions"]
    print(
        f"  positions {pos['naming_a_position']}/{pos['posts_with_text']}"
        f" ({pos['share_of_texted_posts']:.1%}), without % units"
        f" {pos['share_excluding_percent_units']:.1%}"
    )
    for measure in record["comment_comparisons"]:
        inter, loose = measure["intersections"], measure["inflected"]["intersections"]
        print(
            f"  comparisons {measure['population']}:"
            f" a={measure['a_two_or_more_watchlist_brands']['rows']}"
            f" b={measure['b_comparison_marker_beside_a_brand']['rows']}"
            f" c={measure['c_position_or_category_token']['rows']}"
            f" a∩b={inter['a_and_b']} a∩b∩c={inter['a_and_b_and_c']}"
            f" | inflected a∩b={loose['a_and_b']} a∩b∩c={loose['a_and_b_and_c']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
