"""The relevance floor: does a channel's window contain OUR taxonomy at all?

SPEC amendment 3.12 (1). The existing screens grade capability, language, market origin and
"about food"; none of them ever asked whether a source carries the tracked category. This module
is the pure half of that question — matching and counting, no files, no registry, no clock.

Two matchers, both taken as they ship rather than invented here:

* **categories** — the draft lexicon's own rule, `stem + one of its `endings`, bounded by
  non-word characters`. Read out of the lexicon FILE, not restated, so a lexicon that changes its
  endings changes this screen with it. Only the `tracked` half is read: `dairy` and `ice-cream`
  are the taxonomy, and the `draft` families beside them are other people's categories.
* **brands** — `market_pulse.brands.find_watchlist_brands`' rule: the display name exactly as
  written, casefolded, bounded by non-word characters. It is the matcher G1e is scored against,
  and it is the strict one of the two readings the corpus supports (`Гармонію` is not `Гармонія`),
  which is the right direction for a FLOOR: a loose matcher hides the zero-yield channels the
  screen exists to surface.

One thing is added to the shipped brand rule, because the watchlist gained a case it did not have
before: «Яготинське для дітей» CONTAINS «Яготинське», so a post naming the child matches its
parent's alias too. The operator tracks the two separately, so the longer span wins and the
shorter one inside it is dropped.

A hit counts once per post, per the brief.
"""

import re

TRACKED = "tracked"
"""The half of the lexicon that is the taxonomy. The `draft` families are food, not our food."""


def compile_categories(lexicon: dict) -> dict[str, list[tuple[str, re.Pattern]]]:
    """The tracked groups' stems, compiled under the lexicon's own matcher and endings.

    The stem is kept beside its pattern, not thrown away: `dairy: 599` cannot be audited, and
    «масл» matching the surname «Маслов» is only visible if the count can be broken back down to
    the term that produced it.
    """
    endings = "|".join(
        sorted({re.escape(end) for end in lexicon["endings"]}, key=len, reverse=True)
    )
    return {
        group: [
            (stem, re.compile(rf"(?<!\w){re.escape(stem)}(?:{endings})(?!\w)")) for stem in stems
        ]
        for group, stems in sorted(lexicon[TRACKED].items())
    }


def compile_aliases(aliases: dict[str, str]) -> list[tuple[re.Pattern, str, str]]:
    """(pattern, brand_id, alias) for every casefolded watchlist display name.

    ``aliases`` is ``market_pulse.brands.watchlist_aliases``' table, so "a brand hit" means here
    what it means to the scorer.
    """
    return [
        (re.compile(rf"(?<!\w){re.escape(alias)}(?!\w)"), brand_id, alias)
        for alias, brand_id in sorted(aliases.items())
    ]


def category_hits(text: str, compiled: dict[str, list[tuple[str, re.Pattern]]]) -> list[str]:
    """The tracked groups this text names, once each."""
    low = (text or "").casefold()
    return [group for group, stems in compiled.items() if any(p.search(low) for _, p in stems)]


def category_terms(text: str, compiled: dict[str, list[tuple[str, re.Pattern]]]) -> list[str]:
    """The individual stems that fired, as ``group:stem`` — the audit trail of the count above."""
    low = (text or "").casefold()
    return sorted(
        f"{group}:{stem}"
        for group, stems in compiled.items()
        for stem, pattern in stems
        if pattern.search(low)
    )


def brand_hits(text: str, compiled: list[tuple[re.Pattern, str, str]]) -> list[str]:
    """The watchlist brands this text names, once each, with nested aliases resolved.

    A match whose span sits inside another match's span is dropped: «Яготинське для дітей» names
    the baby-food line, and counting «Яготинське» inside it would credit the parent brand with
    every one of the child's mentions.
    """
    low = (text or "").casefold()
    spans = [
        (match.start(), match.end(), brand_id)
        for pattern, brand_id, _ in compiled
        for match in pattern.finditer(low)
    ]
    kept = {
        brand_id
        for start, end, brand_id in spans
        if not any(s <= start and end <= e and (s, e) != (start, end) for s, e, _ in spans)
    }
    return sorted(kept)


def evidence_line(
    text: str,
    compiled: dict[str, list[tuple[str, re.Pattern]]],
    aliases: list[tuple[re.Pattern, str, str]],
    want: str | None = None,
) -> dict | None:
    """The first line of this post that carries a hit, with the term that fired on it.

    The evidence is a quoted line, never a counter — the market screen's rule, for the same
    reason: a share of 0.02 cannot be checked by a human, and «сир» matching «креветка сира» is
    visible at a glance and invisible inside a number.
    """
    for line in (text or "").splitlines():
        if not line.strip():
            continue
        low = line.casefold()
        for group, stems in compiled.items():
            for stem, pattern in stems:
                term = f"{group}:{stem}"
                if (want in (None, term)) and (match := pattern.search(low)):
                    return {
                        "kind": "category",
                        "name": term,
                        "matched": match.group(0),
                        "line": squeeze(line),
                    }
        for pattern, brand_id, _ in aliases:
            if (want in (None, f"brand:{brand_id}")) and (match := pattern.search(low)):
                return {
                    "kind": "brand",
                    "name": brand_id,
                    "matched": match.group(0),
                    "line": squeeze(line),
                }
    return None


def squeeze(line: str, limit: int = 180) -> str:
    one = " ".join(line.split())
    return one if len(one) <= limit else one[:limit] + "…"


def carriers(
    text: str,
    compiled: dict[str, list[tuple[str, re.Pattern]]],
    aliases: list[tuple[re.Pattern, str, str]],
) -> set[str]:
    """Every term that makes this post relevant: ``group:stem`` or ``brand:brand_id``."""
    return set(category_terms(text, compiled)) | {
        f"brand:{brand_id}" for brand_id in brand_hits(text, aliases)
    }


def sole_carriers(relevant: list[set[str]], bar: int) -> list[str]:
    """The terms this channel's bar-A pass depends on — struck one at a time, does it still clear?

    Not a judgement about which term is wrong. It is leverage, and leverage is what a reader needs
    to see before signing: «варто» is an ATB private label AND the ordinary Ukrainian word for "it
    is worth", so a row carried by that one alias says something very different from a row carried
    by «сир» and «морозиво».
    """
    if len(relevant) < bar:
        return []
    every = {term for terms in relevant for term in terms}
    return sorted(term for term in every if sum(1 for terms in relevant if terms - {term}) < bar)


def bar_A_reach(posts_in_window: int, posts_with_text: int, bar: int) -> str:
    """Could this channel have cleared bar A at all? A refusal to rule, not a verdict.

    Bar A is an absolute count over a denominator that runs from 0 to 1,535 across the registry, so
    a channel with fewer readable posts than the bar fails it by arithmetic whatever it publishes.
    The sibling instrument already draws this line — `language_census_5c1` answers
    `NO_POSTS_IN_WINDOW` and `TOO_FEW_DECIDABLE` instead of a verdict — and it matters most for the
    `watch` bucket, whose whole definition is "silent, collected, revisited when it speaks again":
    re-failing those on their own silence would put them on a removal list they were already ruled
    onto a waiting list for.

    The bar itself is untouched. This says whether the row's FAIL is about content.
    """
    if posts_in_window == 0:
        return "NO_POSTS_IN_WINDOW"
    if posts_with_text < bar:
        return "TOO_FEW_TEXTED_POSTS"
    return "gradeable"


def bar_verdicts(relevant_posts: int, comments: int, has_comment_source: bool, bars: dict) -> dict:
    """The two bars, kept in their own currencies, and the flag that reads both at once.

    ``N/A`` is only for a channel with no readable comment source at all. A channel whose group
    WAS read and produced nothing scores a measured zero, and a measured zero is a FAIL — the
    difference between "we did not look" and "we looked and it is empty" is the whole question the
    operator is being asked to rule on.
    """
    passed_a = relevant_posts >= bars["bar_A_relevant_posts_28d"]
    if not has_comment_source:
        bar_b = "N/A"
    else:
        bar_b = "PASS" if comments >= bars["bar_B_comments_under_relevant_28d"] else "FAIL"
    return {
        "bar_A": "PASS" if passed_a else "FAIL",
        "bar_B": bar_b,
        "below_both": not passed_a and bar_b != "PASS",
    }
