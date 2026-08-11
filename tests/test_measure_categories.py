"""The draft lexicon's negative controls.

Every share in `results/categories_45h.json` is a count of regex hits, so the only
thing that makes it a measurement rather than a number is what the regexes refuse.
These are the refusals: the words that look like a food family and are not, the
discount that looks like a pack size, and the Russian `чем` hiding inside `Зачем`.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import measure_categories as mc  # noqa: E402

from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402


@pytest.fixture(scope="module")
def registry():
    return load_registry(mc.REGISTRY)


@pytest.fixture(scope="module")
def compiled(registry):
    return mc.patterns(mc.build_lexicon(registry))


@pytest.mark.parametrize(
    "stem,text",
    [
        ("суп", "супермаркет"),
        ("чай", "чайник закипів"),
        ("кав", "кавалер і кавун"),
        ("олі", "олівець"),
        ("сок", "сокол"),
        ("сир", "сировина"),
    ],
)
def test_a_stem_does_not_eat_the_word_it_starts(stem, text):
    assert not mc.word(stem).search(text)


@pytest.mark.parametrize(
    "stem,text",
    [("суп", "супи"), ("кав", "кава"), ("сир", "твердий сир"), ("морозив", "морозиво")],
)
def test_the_stem_still_matches_its_own_inflections(stem, text):
    assert mc.word(stem).search(text)


@pytest.mark.parametrize("text", ["300 грн", "знижка на 5 гривень", "код 20л1"])
def test_the_unit_token_refuses_a_price(text):
    assert not mc.UNIT.search(text)


@pytest.mark.parametrize("text", ["молоко 900 мл", "сир 200 г", "кефір 1 л", "яйця 10 шт"])
def test_the_unit_token_reads_a_pack_size(text):
    assert mc.UNIT.search(text)


def test_a_promo_percent_and_a_fat_percent_are_told_apart():
    assert mc.UNIT.search("знижка 20%")
    assert not mc.DECIMAL_PERCENT.search("знижка 20%")
    assert mc.DECIMAL_PERCENT.search("молоко 2,5%")


@pytest.mark.parametrize("text", ["Зачем это", "ніжний смак", "за 20 грн", "за акцією"])
def test_a_comparison_marker_does_not_fire_on_a_substring(text):
    assert mc.comparison_marker(text) is None


@pytest.mark.parametrize(
    "text", ["Рудь смачніший за Гармонію", "це краще ніж інше", "лучше чем вчера"]
)
def test_a_real_comparison_is_read(text):
    assert mc.comparison_marker(text)


def test_the_lexicon_is_marked_draft_and_bound_to_the_registry(registry):
    lexicon = mc.build_lexicon(registry)
    assert lexicon["status"] == "draft-not-law"
    assert set(lexicon["tracked"]) == set(registry.taxonomy.tracked_groups)


def test_a_tracked_stem_that_names_nothing_stops_the_build(registry, monkeypatch):
    """The check that keeps the tracked half tied to config/registry.yaml: a typo there
    would measure zero rows and read as 'the category is not in the corpus'."""
    monkeypatch.setitem(mc.TRACKED_STEMS, "dairy", ["ковбас"])
    with pytest.raises(SystemExit, match="not prefixes"):
        mc.build_lexicon(registry)


def test_the_coverage_measure_reads_the_tracked_groups_from_the_registry(registry, compiled):
    """uni-a's LEAK L3: `coverage` held `tracked = {"dairy", "ice-cream"}` as a local literal —
    inside the very file that checks every stem against the registry. `share_of_texted_naming_
    tracked` would have kept counting dairy under a new taxonomy's name."""
    posts = [
        {"text": "Морозиво Рудь 500 г", "channel": "@x", "msg_id": 1},
        {"text": "Хліб та булочки", "channel": "@x", "msg_id": 2},
    ]
    read = mc.coverage(posts, compiled, set(registry.taxonomy.tracked_groups))
    assert read["posts_naming_a_tracked_group"] == 1
    assert read["posts_with_a_category_signal"] == 2


def test_a_taxonomy_the_lexicon_cannot_see_stops_the_coverage_measure(compiled):
    """The loud half. Every share would come back 0.0 and read as a fact about the corpus."""
    with pytest.raises(SystemExit, match="no group is in both"):
        mc.coverage([{"text": "Морозиво"}], compiled, {"coffee"})


def test_the_position_span_needs_a_category_or_a_brand_on_the_line(registry, compiled):
    aliases = watchlist_aliases(registry.watchlist)
    assert mc.position_span("масло 200 г", compiled, aliases)
    assert mc.position_span("Рудь 100 г", compiled, aliases)
    assert mc.position_span("подарунковий набір 200 г", compiled, aliases) is None


def test_the_comparison_measure_is_deterministic(registry, compiled):
    aliases = watchlist_aliases(registry.watchlist)
    rows = [
        {"id": "@c:2", "text": "Рудь смачніший за Гармонію, пломбір 100 г"},
        {"id": "@c:1", "text": "просто дякую"},
        {"id": "@c:3", "text": "Галичина і Злагода 82%"},
    ]
    first = mc.comparisons(rows, compiled, aliases, "fixture")
    second = mc.comparisons(list(reversed(rows)), compiled, aliases, "fixture")
    assert first == second


def test_the_canonical_example_needs_the_inflected_reading(registry, compiled):
    """«Морозиво пломбір Рудь смачніший за Гармонію» — the row the operator named as
    the case a per-(brand+position) amendment would exist for. The exact matcher, which
    is the scorer's, sees one brand: `Гармонію` is not `Гармонія`. If the two readings
    ever agree on this row, one of them has stopped doing its job."""
    aliases = watchlist_aliases(registry.watchlist)
    rows = [{"id": "@c:2", "text": "Морозиво пломбір Рудь смачніший за Гармонію, 100 г"}]
    measured = mc.comparisons(rows, compiled, aliases, "fixture")
    assert measured["intersections"]["a_and_b_and_c"] == 0
    assert measured["inflected"]["intersections"]["a_and_b_and_c"] == 1
