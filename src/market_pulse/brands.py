"""Watchlist string matching — the cheapest possible brand extractor.

This is the *prediction* side of G1e: what a model has to beat. It can only ever
emit watchlist brands, so every dairy brand outside the watchlist (``Dziugas``,
``Philadelphia``, ``Baltais``) is a miss by construction — that is the baseline
being cheap, not the metric being wrong. Normalization of the matches, and the
gate itself, live in :mod:`market_pulse.scorer`.

**Revisions (SPEC 3.21 (1)).** Three watchlist names are also ordinary words or
other people's entities, and `config/watchlist_rules.yaml` holds the rules that
say so. They are OPT-IN: :func:`find_watchlist_brands` called without ``rules``
matches exactly what it matched before the file existed, because every sealed
record — `results/window_summary_5c2.json`'s brand attribution above all — was
measured under that matching, and 3.21 (1) says G1e history is never rescored.
A caller that wants the honest cut names the revision and says so in its own
provenance; a caller that mirrors a sealed record must not.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from market_pulse.registry import WatchlistBrand

RULES = Path(__file__).resolve().parents[2] / "config" / "watchlist_rules.yaml"

MATCHES = ("phrase", "stem")
"""How a marker family is matched. ``phrase`` is the term as written, casefolded and bounded by
non-word characters — the alias table's own rule. ``stem`` is `config/lexicon.yaml`'s: the stem
followed by one of the file's endings, bounded on both sides."""


def watchlist_aliases(watchlist: list[WatchlistBrand]) -> dict[str, str]:
    """Casefolded ``display_name`` -> ``brand_id``, for matching and normalization."""
    return {
        " ".join(name.split()).casefold(): brand.brand_id
        for brand in watchlist
        for name in brand.display_names
    }


@dataclass(frozen=True)
class WatchlistRules:
    """`config/watchlist_rules.yaml`, loaded — a requirement per ruled brand, and nothing else.

    A rule can only ever REMOVE a hit the alias table already made. Nothing here adds a name or a
    spelling, which is what keeps a revision from being a quiet registry edit: the watchlist stays
    the sealed `config/registry.yaml`'s, and this file says which of its hits are believed.
    """

    revision: str
    dated: str
    required: dict[str, str]
    carriers: dict[str, tuple[str, ...]]
    markers: dict[str, re.Pattern]

    def carries(self, brand_id: str, carrier: str) -> bool:
        """Whether ``brand_id``'s rule reaches ``carrier`` at all. 3.21 (1) scopes `garmonija` to
        comment text: a leaflet page naming Гармонія is a retailer printing a trade mark."""
        return carrier in self.carriers[brand_id]

    def satisfied(self, brand_id: str, text: str) -> bool:
        return bool(self.markers[self.required[brand_id]].search(text.casefold()))


def load_watchlist_rules(path: str | Path = RULES) -> WatchlistRules:
    """The rules file, or a ``ValueError`` naming the defect.

    Strict for `registry.py`'s reason: a rule silently dropped by a typo is a matcher that keeps
    handing a surface the collisions the operator ruled off, and the only symptom is a brand table
    that looks plausible.
    """
    law = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    for key in ("revision", "dated", "rules", "markers"):
        if key not in law:
            raise ValueError(f"{path}: no {key!r} — the rules file must name it")

    markers: dict[str, re.Pattern] = {}
    for family, spec in law["markers"].items():
        if spec.get("match") not in MATCHES:
            raise ValueError(f"{path}: marker family {family!r} matches {spec.get('match')!r}")
        terms = [str(term).casefold() for term in spec.get("terms") or ()]
        if not terms:
            raise ValueError(f"{path}: marker family {family!r} lists no terms")
        if spec["match"] == "phrase":
            body = "|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True))
            markers[family] = re.compile(rf"(?<!\w)(?:{body})(?!\w)")
            continue
        endings = spec.get("endings")
        if not endings:
            raise ValueError(f"{path}: stem family {family!r} lists no endings")
        # longest first, for `compile_categories`' reason: an alternation takes the first branch
        # that matches, and «а» before «ами» would let the word end three letters early.
        tail = "|".join(sorted({re.escape(end) for end in endings}, key=len, reverse=True))
        body = "|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True))
        markers[family] = re.compile(rf"(?<!\w)(?:{body})(?:{tail})(?!\w)")

    required, carriers = {}, {}
    for brand_id, rule in law["rules"].items():
        family = rule.get("requires")
        if family not in markers:
            raise ValueError(f"{path}: {brand_id} requires {family!r}, which no marker family is")
        if not rule.get("applies_to"):
            raise ValueError(f"{path}: {brand_id} names no carriers — a rule with no scope")
        required[brand_id] = family
        carriers[brand_id] = tuple(rule["applies_to"])

    return WatchlistRules(
        revision=str(law["revision"]),
        dated=str(law["dated"]),
        required=required,
        carriers=carriers,
        markers=markers,
    )


def find_watchlist_brands(
    text: str,
    aliases: dict[str, str],
    rules: WatchlistRules | None = None,
    *,
    carrier: str | None = None,
) -> list[dict]:
    """Every watchlist display name occurring in ``text``, as scorer-shaped entries.

    Matching is casefolded and bounded by non-word characters: a bare substring
    test would read ``Ферма`` out of ``фермерське`` and hand the metric free
    false positives. One entry per brand — the guideline collapses a brand named
    twice in a post, and so does the scorer.

    ``rules`` applies a named revision (SPEC 3.21 (1)) and is off by default: the sealed records
    were measured without it. It comes with ``carrier`` — which text this is — and NOT with a
    default, because 3.21 (1) scopes one of its three rules to comment text, and a scope the caller
    never states is a scope nothing can check.
    """
    if (rules is None) != (carrier is None):
        raise ValueError("rules and carrier travel together: a scoped rule needs the carrier named")
    haystack = text.casefold()
    found = {
        brand_id
        for alias, brand_id in aliases.items()
        if re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", haystack)
    }
    if rules is not None:
        found = {
            brand_id
            for brand_id in found
            if brand_id not in rules.required
            or not rules.carries(brand_id, carrier)
            or rules.satisfied(brand_id, text)
        }
    return [{"brand_id": brand_id, "mention": brand_id} for brand_id in sorted(found)]
