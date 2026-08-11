"""The vocabulary law: is it the draft it claims to have migrated, and does it still refuse?

`config/lexicon.yaml` replaced `data/category_lexicon_draft.json` as what the pre-filter's category
half reads (SPEC 3.17 (8), uni-b deliverable A). Two things have to hold or the migration is a
rewrite wearing a migration's name: the law says what the draft said, and the guard that tied the
draft to `config/registry.yaml` still fires on the law.
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse import lexicon, positions  # noqa: E402
from market_pulse.registry import Taxonomy, load_registry  # noqa: E402

DRAFT = REPO_ROOT / "data" / "category_lexicon_draft.json"
REGISTRY = load_registry(REPO_ROOT / "config" / "registry.yaml")


@pytest.fixture(scope="module")
def law():
    return lexicon.load_lexicon()


@pytest.fixture(scope="module")
def draft():
    return json.loads(DRAFT.read_text(encoding="utf-8"))


def test_the_law_is_the_draft_migrated_and_not_a_rewrite(law, draft):
    """The one-time migration check. Content, not bytes — JSON became YAML — and it covers the two
    halves the matcher reads: a stem quietly dropped here matches nothing, and «the category is not
    in the corpus» is exactly what that looks like three files downstream."""
    assert law["tracked"] == draft["tracked"]
    assert law["endings"] == draft["endings"]
    assert {group: len(stems) for group, stems in law["tracked"].items()} == {
        "dairy": 14,
        "ice-cream": 2,
    }
    assert len(law["endings"]) == 36


def test_the_law_names_the_draft_it_came_from_by_sha(law):
    """The draft is not edited and not deleted — five sealed records pin it — so the law can cite
    it, and a citation that is not checked is a sentence rather than a provenance."""
    assert law["source"]["path"] == "data/category_lexicon_draft.json"
    assert law["source"]["sha256"] == hashlib.sha256(DRAFT.read_bytes()).hexdigest()
    assert law["status"] == "law" and law["source"]["status_then"] == "draft-not-law"


def test_the_matcher_and_the_collision_came_across_verbatim(law, draft):
    assert law["matcher"] == draft["matcher"]
    assert law["known_collision"] == draft["known_collision"]


def test_the_units_are_an_ordered_list_and_not_a_set(law):
    """The order is load-bearing: a regex alternation takes the first branch that matches, so «г»
    before «грн» reads "90 грн" as a size. Asserted as the exact sequence, because a later tidy-up
    into alphabetical order would break the pre-filter silently."""
    assert law["units"] == ["кг", "мл", "грн", "г", "л", "%"]
    assert positions.SIZE_PRICE_UNITS == tuple(law["units"])
    # the property the order exists for, measured rather than asserted about
    assert positions.size_price_pattern("Сир 90 грн") == "90 грн"
    assert positions.size_price_pattern("Сир 200 г") == "200 г"


def test_the_empty_ending_survives_the_yaml_round_trip(law):
    """`endings[0]` is "" — the bare stem. A bare `-` in YAML loads as None and would reach
    `re.escape` as one, three call frames away from the file that caused it."""
    assert law["endings"][0] == ""
    assert all(isinstance(ending, str) for ending in law["endings"])


def test_the_live_law_agrees_with_the_live_registry(law):
    """The positive control for the guard below: today's law passes today's registry."""
    lexicon.check_against_registry(law, REGISTRY.taxonomy)
    assert set(law["tracked"]) == set(REGISTRY.taxonomy.tracked_groups)


def test_a_stem_that_names_nothing_in_the_registry_is_refused(law):
    """The negative control. This is `measure_categories.build_lexicon`'s rule, now on the law and
    with one implementation: a tracked stem that is not a prefix of a display name measures zero
    rows, and zero rows reads as «the category is not there»."""
    broken = {**law, "tracked": {**law["tracked"], "dairy": ["ковбас"]}}
    with pytest.raises(ValueError, match="not prefixes"):
        lexicon.check_against_registry(broken, REGISTRY.taxonomy)


def test_a_group_the_registry_does_not_track_is_refused(law):
    broken = {**law, "tracked": {**law["tracked"], "seafood": ["риб"]}}
    with pytest.raises(ValueError, match="not a tracked group"):
        lexicon.check_against_registry(broken, REGISTRY.taxonomy)


def test_the_russian_forms_are_exempt_one_by_one_and_not_by_loosening(law):
    """«кефир», «творог», «морожен» have nothing to be a prefix of — the display names are
    Ukrainian. Named in the file; drop the exemption list and the law stops loading."""
    assert law["ru_variants"] == ["кефир", "творог", "морожен"]
    without = {**law, "ru_variants": []}
    with pytest.raises(ValueError, match="not prefixes"):
        lexicon.check_against_registry(without, REGISTRY.taxonomy)


def test_the_loader_names_the_defect_it_refuses(tmp_path, law):
    """Strict for `registry.py`'s reason: a malformed vocabulary collects nothing and only surfaces
    as wrong analytics later. Each defect is checked by writing one, not by reading the code."""
    cases = {
        "needs a 'units' section": {key: law[key] for key in ("status", "tracked", "endings")},
        "has no stems": {**law, "tracked": {"dairy": []}},
        "carries an empty stem": {**law, "tracked": {"dairy": ["  "]}},
        "which is not a string": {**law, "endings": ["а", None]},
        "a unit is empty": {**law, "units": ["кг", ""]},
        "must be a non-empty list": {**law, "endings": []},
    }
    for expected, body in cases.items():
        path = tmp_path / "lexicon.yaml"
        path.write_text(yaml.safe_dump(body, allow_unicode=True), encoding="utf-8")
        with pytest.raises(ValueError, match=expected):
            lexicon.load_lexicon(path)


def test_the_loader_checks_the_registry_when_it_is_given_one(law):
    """The loud half is opt-in because the schema reading `units` holds no registry to check
    against — so the check has to be provable from the load path, not only from the helper."""
    toy = Taxonomy({"coffee": {"name": "Кава", "subcategories": {"ground": "Мелена"}}})
    with pytest.raises(ValueError, match="not a tracked group"):
        lexicon.load_lexicon(lexicon.LAW, taxonomy=toy)
