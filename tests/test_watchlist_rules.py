"""`config/watchlist_rules.yaml` — SPEC 3.21 (1)'s named revision r1, held to its own text.

Every case here runs against the REAL rules file. A stub of it would test the loader and leave the
law untested, and the law is the part the operator ruled.
"""

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse.brands import (  # noqa: E402
    RULES,
    find_watchlist_brands,
    load_watchlist_rules,
    watchlist_aliases,
)
from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
LEXICON = REPO_ROOT / "config" / "lexicon.yaml"
DRAFT = REPO_ROOT / "data" / "category_lexicon_draft.json"

ALIASES = watchlist_aliases(load_registry(REGISTRY).watchlist)
R1 = load_watchlist_rules(RULES)


def hits(text: str, carrier: str = "comment") -> list[str]:
    return [
        found["brand_id"] for found in find_watchlist_brands(text, ALIASES, R1, carrier=carrier)
    ]


def test_the_revision_is_named_and_dated():
    """A revision nobody can name cannot be recorded in a provenance block — 3.21 (1) requires it."""
    assert (R1.revision, R1.dated) == ("r1", "2026-08-15")


@pytest.mark.parametrize(
    ("text", "want"),
    [
        # the three rulings, in the words the contract wrote them
        ('В дитячому центрі "Гармонія" на метро Турбоатом набираються нові групи', []),
        ("Гармонія, молоко смачне", ["garmonija"]),
        ("Дівчата, чи варто йти на цей курс?", []),
        ("новинка від власної ТМ Varto", ["varto"]),
        ("Селянське", []),
        # and the other side of each: a brand with no rule is untouched by the revision
        ("Морозиво Рудь ванільне, ескімо 60 г", ["rud"]),
        ("Масло «Селянське» ТМ Гармонія", ["garmonija", "selianske"]),
    ],
)
def test_r1_on_the_ruled_cases(text, want):
    assert hits(text) == want


def test_the_revision_is_opt_in():
    """Without `rules` the matcher is what every sealed record was measured under.

    This is the load-bearing test of the whole manoeuvre: `results/window_summary_5c2.json`'s brand
    attribution, `results/validate_5c2_pack.json` and the 6a mirror all re-derive through the
    default, and 3.21 (1) says G1e history is never rescored.
    """
    for text in ("чи варто йти", 'дитячий центр "Гармонія"', "Селянське"):
        assert find_watchlist_brands(text, ALIASES) != []
        assert hits(text) == []


def test_rules_without_a_carrier_is_a_refusal():
    """One of the three rules is scoped to comment text, so a caller that does not say which text
    this is cannot be given an answer — a default carrier would make the scope unobservable."""
    with pytest.raises(ValueError, match="carrier"):
        find_watchlist_brands("чи варто", ALIASES, R1)
    with pytest.raises(ValueError, match="carrier"):
        find_watchlist_brands("чи варто", ALIASES, carrier="comment")


def test_the_garmonija_rule_stops_at_comment_text():
    """3.21 (1) scopes it: a leaflet page naming Гармонія is a retailer printing a trade mark."""
    page = "СИР КИСЛОМОЛОЧНИЙ ТМ Гармонія 9%"
    assert hits(page, carrier="leaflet_page") == ["garmonija"]
    bare = "Гармонія на Турбоатом"
    assert hits(bare, carrier="leaflet_page") == ["garmonija"]
    assert hits(bare, carrier="comment") == []


def test_the_varto_rule_reaches_every_carrier():
    """Unlike `garmonija`, the adverb is an adverb wherever it is written."""
    assert R1.carriers["varto"] == ("comment", "post_text", "leaflet_page")
    for carrier in R1.carriers["varto"]:
        assert hits("про що варто памʼятати", carrier=carrier) == []


def test_every_ruled_brand_is_a_watchlist_row():
    """A rule on a brand_id the registry does not carry is a rule that can never fire."""
    assert set(R1.required) <= set(ALIASES.values())
    assert set(R1.required) == {"varto", "selianske", "garmonija"}


def test_the_dairy_markers_are_the_lexicon_law_and_not_a_new_vocabulary():
    """The terms are COPIED into the rules file so the rule reads in one place — and copies drift.

    This is the line that stops the copy from becoming its own vocabulary: the marker list must be
    `config/lexicon.yaml`'s tracked dairy plus ice cream, and its endings must be that file's own.
    A term nobody can find in the law is a category word invented here, which is exactly the leak
    SPEC 3.17 (8) closed when the draft stopped being what the pre-filter read.
    """
    law = yaml.safe_load(LEXICON.read_text(encoding="utf-8"))
    rules = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    dairy = rules["markers"]["dairy_marker"]

    assert set(dairy["terms"]) == set(law["tracked"]["dairy"]) | set(law["tracked"]["ice-cream"])
    assert dairy["endings"] == law["endings"]
    # 3.17 (8) migrated the law from the draft byte-faithfully, and the contract names both files as
    # the source. Checking the draft too is what proves "sourced from" rather than "resembles".
    draft = yaml.safe_load(DRAFT.read_text(encoding="utf-8"))
    assert set(dairy["terms"]) == set(draft["tracked"]["dairy"]) | set(
        draft["tracked"]["ice-cream"]
    )


def test_every_rule_cites_the_ruling_that_made_it():
    """Law without a citation is a preference. Each rule names the sitting or the ruling date."""
    rules = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    assert rules["authority"] == "docs/SPEC.md amendment 3.21 (1)"
    for brand_id, rule in rules["rules"].items():
        assert "2026-08-1" in rule["ruling"], brand_id
        assert rule["why"].strip(), brand_id


def test_a_rule_pointing_at_no_marker_family_is_a_refusal(tmp_path):
    law = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    law["rules"]["varto"]["requires"] = "packaging_marker"
    broken = tmp_path / "rules.yaml"
    broken.write_text(yaml.safe_dump(law, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="packaging_marker"):
        load_watchlist_rules(broken)


def test_a_rule_with_no_carriers_is_a_refusal(tmp_path):
    law = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    law["rules"]["garmonija"].pop("applies_to")
    broken = tmp_path / "rules.yaml"
    broken.write_text(yaml.safe_dump(law, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="no carriers"):
        load_watchlist_rules(broken)


def test_a_marker_family_with_no_terms_is_a_refusal(tmp_path):
    """An empty list would compile to a pattern that matches everything or nothing, and both of
    those are a rule that silently stopped being the operator's."""
    law = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    law["markers"]["brand_marker"]["terms"] = []
    broken = tmp_path / "rules.yaml"
    broken.write_text(yaml.safe_dump(law, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="no terms"):
        load_watchlist_rules(broken)


def test_an_unknown_match_mode_is_a_refusal(tmp_path):
    law = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    law["markers"]["dairy_marker"]["match"] = "fuzzy"
    broken = tmp_path / "rules.yaml"
    broken.write_text(yaml.safe_dump(law, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="fuzzy"):
        load_watchlist_rules(broken)


def test_the_marker_is_bounded_like_every_other_match_in_this_repo():
    """«ТМ» inside «ТМИН» is not a trade-mark marker, and «молок» inside «молокозавод» is not one
    of the lexicon's endings."""
    assert hits("ТМИН і варто спробувати") == []
    assert hits("Гармонія — це молокозавод у Полтаві") == []
    assert hits("Гармонія масло 82%") == ["garmonija"]


def test_the_dairy_marker_inherits_the_lexicon_s_collisions():
    """«Маслов» is `масл` + `ов`, and `ов` is one of the law's 36 endings — so a surname is a dairy
    marker here exactly as «креветка сира» is one in the pre-filter.

    Asserted rather than left to be discovered: a marker false positive can only let a hit THROUGH,
    which is the safe direction for a rule whose whole job is to remove hits, and the rules file
    says so in its own `known_collision`. If the lexicon ever tightens, this line goes red and the
    note is updated with it instead of quietly becoming untrue.
    """
    assert hits("Гармонія — це прізвище Маслов") == ["garmonija"]
    assert (
        "known_collision"
        in yaml.safe_load(RULES.read_text(encoding="utf-8"))["markers"]["dairy_marker"]
    )
