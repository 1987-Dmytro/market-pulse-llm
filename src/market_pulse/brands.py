"""Watchlist string matching — the cheapest possible brand extractor.

This is the *prediction* side of G1e: what a model has to beat. It can only ever
emit watchlist brands, so every dairy brand outside the watchlist (``Dziugas``,
``Philadelphia``, ``Baltais``) is a miss by construction — that is the baseline
being cheap, not the metric being wrong. Normalization of the matches, and the
gate itself, live in :mod:`market_pulse.scorer`.
"""

import re

from market_pulse.registry import WatchlistBrand


def watchlist_aliases(watchlist: list[WatchlistBrand]) -> dict[str, str]:
    """Casefolded ``display_name`` -> ``brand_id``, for matching and normalization."""
    return {
        " ".join(name.split()).casefold(): brand.brand_id
        for brand in watchlist
        for name in brand.display_names
    }


def find_watchlist_brands(text: str, aliases: dict[str, str]) -> list[dict]:
    """Every watchlist display name occurring in ``text``, as scorer-shaped entries.

    Matching is casefolded and bounded by non-word characters: a bare substring
    test would read ``Ферма`` out of ``фермерське`` and hand the metric free
    false positives. One entry per brand — the guideline collapses a brand named
    twice in a post, and so does the scorer.
    """
    haystack = text.casefold()
    found = {
        brand_id
        for alias, brand_id in aliases.items()
        if re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", haystack)
    }
    return [{"brand_id": brand_id, "mention": brand_id} for brand_id in sorted(found)]
