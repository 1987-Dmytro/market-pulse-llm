"""Validation tests for the source registry loader."""

from pathlib import Path

import pytest
from market_pulse.registry import AUDIENCES, load_registry

REGISTRY = Path(__file__).resolve().parents[1] / "config" / "registry.yaml"

SOURCES = (
    "sources:\n"
    "  - id: a\n    name: A\n    source_type: official_retail\n"
    "    telegram_channels: ['@chan_one']\n"
)
TAXONOMY = "taxonomy:\n  tracked_groups:\n    dairy:\n      name: Молочні продукти\n"


def write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "registry.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_shipped_registry_loads():
    registry = load_registry(REGISTRY)
    assert registry.sources
    assert all(s.telegram_channels for s in registry.sources)
    assert len({s.id for s in registry.sources}) == len(registry.sources)
    assert registry.taxonomy.tracked_groups
    assert any(b.own for b in registry.watchlist)
    # Reactions must be readable somewhere, or T1 has no input at all (SPEC §9).
    assert any(s.comments_enabled for s in registry.sources)


def test_comments_enabled_defaults_to_false(tmp_path):
    # A source added before its entry check must not claim it carries comments.
    registry = load_registry(write(tmp_path, SOURCES + TAXONOMY))
    assert registry.sources[0].comments_enabled is False


def test_watch_defaults_to_false(tmp_path):
    # The default has to be "collect normally": a launch channel that silently read as watch
    # would be dropped from the joins with nothing to see it.
    registry = load_registry(write(tmp_path, SOURCES + TAXONOMY))
    assert registry.sources[0].watch is False


def test_watch_is_read_and_must_be_a_boolean(tmp_path):
    """`watch: "no"` is truthy in Python, and a launch channel read as watch loses its join."""
    body = SOURCES.replace("['@chan_one']\n", "['@chan_one']\n    watch: true\n")
    assert load_registry(write(tmp_path, body + TAXONOMY)).sources[0].watch is True

    bad = SOURCES.replace("['@chan_one']\n", "['@chan_one']\n    watch: 'no'\n")
    with pytest.raises(ValueError, match="non-boolean watch"):
        load_registry(write(tmp_path, bad + TAXONOMY))


def test_audience_defaults_to_none_and_is_a_closed_list(tmp_path):
    """The eight segments are the canon's; a ninth would silently make its own bucket in every
    aggregate 5c2 keys on this field and read as an audience nobody chose."""
    registry = load_registry(write(tmp_path, SOURCES + TAXONOMY))
    assert registry.sources[0].audience is None

    good = SOURCES.replace("['@chan_one']\n", "['@chan_one']\n    audience: baby_food\n")
    assert load_registry(write(tmp_path, good + TAXONOMY)).sources[0].audience == "baby_food"

    bad = SOURCES.replace("['@chan_one']\n", "['@chan_one']\n    audience: mums\n")
    with pytest.raises(ValueError, match="unknown audience"):
        load_registry(write(tmp_path, bad + TAXONOMY))


def test_every_shipped_source_carries_an_audience():
    """The 08.08 ruling covers all 56, so a null here is a source no aggregate can attribute."""
    sources = load_registry(REGISTRY).sources
    assert [s.id for s in sources if s.audience is None] == []
    assert set(AUDIENCES) >= {s.audience for s in sources}


def test_government_is_a_source_type(tmp_path):
    """@dpssgovua, Держпродспоживслужба — a state inspectorate is neither retail, aggregator
    nor community, and the 5c1 registry write needed a fourth value (team-lead, 2026-08-07)."""
    body = SOURCES.replace("source_type: official_retail", "source_type: government")
    assert load_registry(write(tmp_path, body + TAXONOMY)).sources[0].source_type == "government"


def test_duplicate_source_id_rejected(tmp_path):
    path = write(
        tmp_path,
        "sources:\n"
        "  - id: a\n    name: A\n    source_type: official_retail\n"
        "    telegram_channels: ['@chan_one']\n"
        "  - id: a\n    name: A again\n    source_type: aggregator\n"
        "    telegram_channels: ['@chan_two']\n" + TAXONOMY,
    )
    with pytest.raises(ValueError, match="duplicate source id"):
        load_registry(path)


def test_source_without_channels_rejected(tmp_path):
    path = write(
        tmp_path,
        "sources:\n  - id: a\n    name: A\n    source_type: official_retail\n"
        "    telegram_channels: []\n" + TAXONOMY,
    )
    with pytest.raises(ValueError, match="no telegram_channels"):
        load_registry(path)


def test_malformed_channel_handle_rejected(tmp_path):
    path = write(
        tmp_path,
        "sources:\n  - id: a\n    name: A\n    source_type: official_retail\n"
        "    telegram_channels: ['chan_without_at']\n" + TAXONOMY,
    )
    with pytest.raises(ValueError, match="malformed handle"):
        load_registry(path)


def test_unknown_source_type_rejected(tmp_path):
    path = write(
        tmp_path,
        "sources:\n  - id: a\n    name: A\n    source_type: newspaper\n"
        "    telegram_channels: ['@chan_one']\n" + TAXONOMY,
    )
    with pytest.raises(ValueError, match="unknown source_type"):
        load_registry(path)


def test_empty_tracked_groups_rejected(tmp_path):
    path = write(tmp_path, SOURCES + "taxonomy:\n  tracked_groups: {}\n")
    with pytest.raises(ValueError, match="tracked_groups"):
        load_registry(path)


def test_duplicate_brand_id_rejected(tmp_path):
    path = write(
        tmp_path,
        SOURCES + TAXONOMY + "watchlist:\n"
        "  - brand_id: rud\n    display_names: ['Рудь']\n"
        "  - brand_id: rud\n    display_names: ['Rud']\n",
    )
    with pytest.raises(ValueError, match="duplicate brand_id"):
        load_registry(path)


def test_the_operators_watchlist_addition_is_in_both_files_and_says_the_same_thing():
    """The +3 of 2026-08-08. `docs/WATCHLIST.md` is the operator-facing list and the registry is
    what code reads; a brand that lives in one of them is a brand half the project cannot see.

    UA canon, RU as a matching alias — checked as an ORDER, because "Заріг, Зарог" and "Зарог,
    Заріг" are the same set and only one of them is the ruling.
    """
    doc = (REGISTRY.parent.parent / "docs" / "WATCHLIST.md").read_text(encoding="utf-8")
    brands = {b.brand_id: b for b in load_registry(REGISTRY).watchlist}
    added = {
        "zarih": ("Заріг", "Зарог"),
        "myrhorodska-korivka": ("Миргородська корівка", "Миргородская коровка"),
        "yahotynske-dlia-ditei": ("Яготинське для дітей", "Яготинское для детей"),
    }
    for brand_id, names in added.items():
        assert brands[brand_id].display_names == names, brand_id
        assert brands[brand_id].own is False, brand_id
        assert f"| {brand_id} | {names[0]}, {names[1]} |" in doc, brand_id


def test_the_baby_food_line_is_a_row_of_its_own_and_its_name_nests_in_its_parents():
    """«Яготинське для дітей» is tracked separately from «Яготинське» — the Мгарське pattern, and
    the operator's own words. The trap that comes with it: the child's display name CONTAINS the
    parent's, so a post naming the child matches both aliases. Pinned here so any matcher over
    this list has to answer for it rather than double-count in silence."""
    brands = {b.brand_id: b for b in load_registry(REGISTRY).watchlist}
    assert "yagotynske" in brands and "yahotynske-dlia-ditei" in brands
    parent = brands["yagotynske"].display_names
    child = brands["yahotynske-dlia-ditei"].display_names
    assert any(p in c for p in parent for c in child), "the nesting this test exists for is gone"
