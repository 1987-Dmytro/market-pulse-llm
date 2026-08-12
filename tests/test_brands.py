"""The baseline's brand extractor: it must find the watchlist and nothing else."""

from pathlib import Path

from market_pulse.brands import find_watchlist_brands, watchlist_aliases
from market_pulse.registry import WatchlistBrand, load_registry

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


# --- SPEC 3.17 (13)(b): the three evidenced Latin forms, and the one that is refused ---------------

SHIPPED = watchlist_aliases(
    load_registry(Path(__file__).resolve().parents[1] / "config" / "registry.yaml").watchlist
)


def test_the_three_ratified_latin_forms_resolve_on_the_shipped_watchlist():
    """Against the real `config/registry.yaml`, not a fixture: the amendment is a registry edit,
    and a fixture would pass whatever the shipped file said."""
    assert SHIPPED["three bears"] == "try-vedmedi"
    assert SHIPPED["rud"] == "rud"
    assert SHIPPED["limo"] == "limo"
    # and the Cyrillic canon they were added beside, unmoved
    assert SHIPPED["три ведмеді"] == SHIPPED["три медведя"] == "try-vedmedi"
    assert SHIPPED["рудь"] == "rud"
    assert SHIPPED["лімо"] == SHIPPED["лимо"] == "limo"


def test_latin_galicia_must_not_reach_halychyna():
    """The negative half of (13)(b), and the reason it is three named forms rather than a
    transliteration rule. `atb_market_official_4510` prints juice ТМ «Galicia»; the dairy brand
    «Галичина» is a different company. The reviewer's own note on @atb_market_official:4508 names
    the pair — «one transliteration shape costs a miss, the other invites a false hit».

    Both directions, because either alone passes for the wrong reason: an alias table with no
    Cyrillic «Галичина» would also fail to resolve «Galicia».
    """
    assert SHIPPED["галичина"] == "halychyna"
    assert "galicia" not in SHIPPED
    assert find_watchlist_brands("Сік Galicia яблучний 1 л", SHIPPED) == []
    assert find_watchlist_brands("Молоко Галичина 2,5%", SHIPPED) == [
        {"brand_id": "halychyna", "mention": "halychyna"}
    ]


def test_a_latin_form_nobody_ratified_is_not_in_the_table():
    """The enumeration is the ruling: «Yagotynske», «Selianske» and «Prostokvashino» are just as
    real as «Rud» on a pack shot, and none of them was evidenced to the team lead, so none is
    here. The alias table grows by named row, never by pattern."""
    for latin in ("yagotynske", "selianske", "prostokvashino", "premia", "harmonia"):
        assert latin not in SHIPPED, latin
