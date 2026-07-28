"""The baseline's brand extractor: it must find the watchlist and nothing else."""

from market_pulse.brands import find_watchlist_brands, watchlist_aliases
from market_pulse.registry import WatchlistBrand

ALIASES = watchlist_aliases(
    [
        WatchlistBrand(brand_id="rud", display_names=("Рудь",), own=False),
        WatchlistBrand(brand_id="ferma", display_names=("Ферма",), own=False),
        WatchlistBrand(brand_id="svoia-liniia", display_names=("Своя Лінія",), own=True),
    ]
)


def test_watchlist_aliases_casefolds_every_display_name():
    assert ALIASES == {"рудь": "rud", "ферма": "ferma", "своя лінія": "svoia-liniia"}


def test_find_watchlist_brands_matches_casefolded_and_collapses_repeats():
    text = "Морозиво ТМ Рудь та ще одне морозиво рудь"
    assert find_watchlist_brands(text, ALIASES) == [{"brand_id": "rud", "mention": "rud"}]


def test_find_watchlist_brands_needs_a_word_boundary():
    """`фермерське` is not the brand `Ферма`; a bare substring test would say it is."""
    assert find_watchlist_brands("Сир фермерське подвір'я", ALIASES) == []
    assert find_watchlist_brands("Масло «Ферма» 82%", ALIASES) == [
        {"brand_id": "ferma", "mention": "ferma"}
    ]


def test_find_watchlist_brands_matches_a_multi_word_name():
    assert find_watchlist_brands("Молоко Своя Лінія 2,5%", ALIASES) == [
        {"brand_id": "svoia-liniia", "mention": "svoia-liniia"}
    ]
