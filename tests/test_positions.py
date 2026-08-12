"""The position schema: the ladder as a truth table, and the three rules that must not bend.

SPEC 3.17 (2)-(4) states the tier ladder in three sentences and leaves two field combinations
unreached; :func:`positions.tier` decides them and this file pins the WHOLE table, 16 rows, so the
executor's reading is visible and a change to it has to break a test rather than move a number.

The other three: identity carries no price, depth exists only for a pair, and nothing is imputed.
"""

import itertools
import json
from dataclasses import fields
from pathlib import Path

import pytest
from market_pulse import positions as P
from market_pulse import lexicon, prompts, yield_screen
from market_pulse.brands import watchlist_aliases
from market_pulse.registry import load_registry

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = load_registry(REPO_ROOT / "config" / "registry.yaml")
SOURCE = "positions_post_gm4/gm4-nf4-base"


def position(**over) -> P.Position:
    """A leaflet position with every field explicit — the dataclass has no defaults on purpose."""
    row = {
        "brand_id": "rud",
        "brand_raw": "Рудь",
        "line": None,
        "category": None,
        "size_value": None,
        "size_unit": None,
        "attribute_pct": None,
        "price_promo": None,
        "price_old": None,
        "discount_pct_printed": None,
        "price_qualifier": None,
        "price_origin": "retail_leaflet",
        "carrier": "leaflet_page",
        "extraction_source": SOURCE,
    }
    return P.Position(**{**row, **over})


# --- the ladder ----------------------------------------------------------------------------------

FILLED = {
    "category": {"category": "ice-cream"},
    "line": {"line": "Золотий Каштан"},
    "size": {"size_value": 500.0, "size_unit": "г"},
    "attribute": {"attribute_pct": 2.5},
}
ATTRIBUTES = ("line", "size", "attribute")


def expected(present: frozenset[str]) -> str:
    """The reading under test, written independently of the implementation.

    Deliberately not a call into `positions.tier`: a table that computed its own expectation would
    pass whatever the ladder does.
    """
    has_category = "category" in present
    has_attribute = bool(present & set(ATTRIBUTES))
    if has_category and has_attribute:
        return "position"
    if has_category or has_attribute:
        return "product_mention"
    return "brand_mention"


TABLE = [
    frozenset(combo)
    for size in range(len(FILLED) + 1)
    for combo in itertools.combinations(sorted(FILLED), size)
]


@pytest.mark.parametrize("present", TABLE, ids=lambda present: "+".join(sorted(present)) or "brand")
def test_the_tier_ladder_over_every_field_combination(present):
    """All 16 rows of the table, brand always present because all three rungs start at one."""
    over = {}
    for name in present:
        over.update(FILLED[name])
    row = position(**over)
    assert row.tier() == expected(present) == P.tier(row)
    assert row.tier() in P.TIERS


def test_the_two_cells_spec_does_not_reach_are_the_ones_documented():
    """The executor's two readings, named in `positions.tier`'s docstring and reported to the team
    lead. They are the only cells where SPEC's three sentences do not decide, so they are asserted
    on their own rather than left inside a 16-row sweep nobody reads."""
    # a named line inside a category IS a differentiating attribute — variant C's whole point
    assert position(category="ice-cream", line="Золотий Каштан").tier() == "position"
    # a size with no category cannot be placed in an aggregate, so it is not a position
    assert position(size_value=500.0, size_unit="г").tier() == "product_mention"
    assert position(line="Золотий Каштан").tier() == "product_mention"
    assert position(category="ice-cream").tier() == "product_mention"
    assert position().tier() == "brand_mention"


def test_filling_a_field_never_lowers_the_tier():
    """Monotonicity is the property that makes the ladder safe to aggregate on: a richer record
    cannot land on a lower rung than the poorer one it contains."""
    rank = {name: index for index, name in enumerate(P.TIERS)}  # 0 = most specific
    for present in TABLE:
        for extra in set(FILLED) - present:
            wider = present | {extra}
            assert rank[expected(wider)] <= rank[expected(present)], (present, extra)


def test_a_record_with_no_brand_is_refused_rather_than_given_a_fourth_rung():
    """SPEC 3.17 (2) has three rungs and all of them start at a brand. An unbranded leaflet line
    («Сир 50% 200 г — 89,90») is a real thing on a page and it is refused here BY NAME, so the
    pilot counts it instead of the schema inventing law for it."""
    with pytest.raises(P.SchemaError) as caught:
        position(brand_id=None, brand_raw=None)
    assert caught.value.reason == "a position names a brand: brand_id or brand_raw"


def test_an_empty_string_is_not_an_absent_field():
    """`""` reads downstream exactly like "the source did not name it", and mapping one to the
    other is the imputation 3.17 (2) forbids. Refused for every optional string."""
    for name in ("brand_id", "line", "category"):
        with pytest.raises(P.SchemaError, match="present and empty"):
            position(**{name: "  "})


# --- identity is not price ------------------------------------------------------------------------


def test_identity_carries_no_price_field():
    """SPEC 3.17 (2): price is an OBSERVATION at (channel, date, carrier), never identity. So the
    same SKU seen at two prices is ONE identity — checked by moving every price field and watching
    the tuple stand still."""
    cheap = position(category="milk", size_value=900.0, size_unit="мл", attribute_pct=2.5)
    dear = position(
        category="milk",
        size_value=900.0,
        size_unit="мл",
        attribute_pct=2.5,
        price_promo=39.9,
        price_old=49.9,
        discount_pct_printed=20.0,
        price_qualifier="exact",
    )
    assert cheap.identity() == dear.identity()
    price_fields = ("price_promo", "price_old", "discount_pct_printed", "price_qualifier")
    assert not set(dear.identity()) & {getattr(dear, name) for name in price_fields}


def test_an_unresolved_brand_never_merges_into_a_resolved_one():
    """`brand_raw` alone is a name the watchlist did not resolve. It gets its own identity key —
    folding it into a resolved brand would credit a watchlist row with a mention nobody matched."""
    resolved = position(brand_id="rud", brand_raw="Рудь", category="ice-cream")
    raw = position(brand_id=None, brand_raw="Рудь", category="ice-cream")
    assert resolved.identity() != raw.identity()
    assert raw.identity()[0] == "raw:Рудь"


# --- depth, and the printed percentage ------------------------------------------------------------


def test_depth_needs_the_pair_and_is_never_reconstructed_from_the_printed_percent():
    """SPEC 3.17 (3). One price with a printed «-30%» is a promo price whose depth is unknown, and
    `None` is that answer — reconstructing the old price from the percentage would invent the number
    the whole aggregate rests on."""
    pair = position(price_promo=90.0, price_old=120.0, price_qualifier="exact")
    assert pair.depth() == pytest.approx(0.25)
    lonely = position(price_promo=90.0, discount_pct_printed=30.0, price_qualifier="exact")
    assert lonely.depth() is None
    assert position().depth() is None
    old_only = position(price_old=120.0, price_qualifier="exact")
    assert old_only.depth() is None


def test_the_printed_percentage_disagreement_is_a_flag_and_not_a_correction():
    """Both numbers stay in the record. Which of the two is wrong is not this layer's ruling."""
    agrees = position(
        price_promo=90.0, price_old=120.0, discount_pct_printed=25.0, price_qualifier="exact"
    )
    assert agrees.depth_disagrees_with_printed() is False
    disagrees = position(
        price_promo=90.0, price_old=120.0, discount_pct_printed=50.0, price_qualifier="exact"
    )
    assert disagrees.depth_disagrees_with_printed() is True
    assert disagrees.discount_pct_printed == 50.0, "the printed value is not corrected"
    assert disagrees.depth() == pytest.approx(0.25), "and neither is the pair"
    # no pair and no printed value cannot disagree: the flag is False, not True-by-absence
    assert position(discount_pct_printed=50.0).depth_disagrees_with_printed() is False
    assert (
        position(price_promo=90.0, price_qualifier="exact").depth_disagrees_with_printed() is False
    )


def test_the_tolerance_absorbs_rounding_and_nothing_more():
    """A leaflet rounds its headline; 1 pp is the pre-registered slack and the boundary is checked
    on both sides so a widened constant cannot pass unnoticed."""
    assert P.PRINTED_TOLERANCE_PP == 1.0
    inside = position(
        price_promo=90.0, price_old=120.0, discount_pct_printed=24.0, price_qualifier="exact"
    )
    assert inside.depth_disagrees_with_printed() is False  # exactly 1.0 pp away
    outside = position(
        price_promo=90.0, price_old=120.0, discount_pct_printed=23.9, price_qualifier="exact"
    )
    assert outside.depth_disagrees_with_printed() is True


# --- no imputation --------------------------------------------------------------------------------


def test_nothing_is_imputed_and_nothing_computed_is_storable():
    P.assert_no_imputation()
    names = {field.name for field in fields(P.Position)}
    assert not names & {"tier", "depth", "depth_disagrees_with_printed"}
    assert len(names) == 14


def test_a_forgotten_field_is_a_TypeError_and_not_a_None():
    """The negative control on the rule above: with no defaults, omitting a field cannot produce a
    record that says "the source did not name it"."""
    with pytest.raises(TypeError):
        P.Position(brand_id="rud", brand_raw=None)  # type: ignore[call-arg]


# --- normalization --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expect",
    [
        ("450 г", (450.0, "г")),
        ("450г", (450.0, "г")),
        ("1 кг", (1000.0, "г")),
        ("0,5 л", (500.0, "мл")),
        ("1.5 Л", (1500.0, "мл")),
        ("500 мл", (500.0, "мл")),
    ],
)
def test_sizes_normalise_to_grams_or_millilitres(raw, expect):
    assert P.parse_size(raw) == expect


@pytest.mark.parametrize(
    "raw", ["2х100 г", "2 x 100 г", "200", "1 шт", "великий", "", "5 кг 200 г"]
)
def test_a_size_it_cannot_read_is_refused_and_never_guessed(raw):
    """Multipacks are the case worth naming: «2х100 г» and «200 г» are different SKUs, and
    multiplying one into the other invents a pack that is not on the page."""
    with pytest.raises(P.SchemaError):
        P.parse_size(raw)


@pytest.mark.parametrize(
    "raw, expect", [("2,5%", 2.5), ("2.5", 2.5), ("20 %", 20.0), ("0,5%", 0.5)]
)
def test_fat_normalises_the_comma_away(raw, expect):
    assert P.parse_fat(raw) == expect


@pytest.mark.parametrize("raw", ["нежирний", "2,5 %%", "жирність", ""])
def test_a_fat_claim_that_is_not_a_number_is_refused(raw):
    with pytest.raises(P.SchemaError):
        P.parse_fat(raw)


@pytest.mark.parametrize(
    "raw, expect",
    [
        ("89,90 грн", (89.9, "exact")),
        ("89.90", (89.9, "exact")),
        ("90 ₴", (90.0, "exact")),
        ("по 90", (90.0, "approx")),
        ("~89", (89.0, "approx")),
        ("≈ 89,5", (89.5, "approx")),
        ("по 90 грн", (90.0, "approx")),
    ],
)
def test_prices_carry_their_own_qualifier(raw, expect):
    """The contract's two markers — «по 90» and «~». The qualifier says what the source wrote; it
    is not a confidence, and a hedged number is kept rather than dropped."""
    assert P.parse_price(raw) == expect


@pytest.mark.parametrize("raw", ["80-90", "дешево", "", "два дев'яносто"])
def test_a_price_that_is_not_one_number_is_refused(raw):
    """A range is two prices and this schema holds one."""
    with pytest.raises(P.SchemaError):
        P.parse_price(raw)


def test_an_attribute_percentage_above_one_hundred_is_not_a_percentage():
    with pytest.raises(P.SchemaError, match="not a percentage"):
        position(attribute_pct=250.0)


@pytest.mark.parametrize("name", ["size_value", "price_promo", "price_old", "discount_pct_printed"])
def test_a_non_positive_number_is_refused(name):
    """A price of 0 is not a price and a 0 g pack is not a pack — both are a parser that gave up."""
    with pytest.raises(P.SchemaError, match="must be positive"):
        extra = {"size_unit": "г"} if name == "size_value" else {"price_qualifier": "exact"}
        position(**{name: 0.0}, **extra)


# --- carrier and origin ---------------------------------------------------------------------------


def test_the_two_carriers_spec_fixes_an_origin_for():
    assert P.origin_of("leaflet_page") == "retail_leaflet"
    assert P.origin_of("comment") == "consumer_quote"
    with pytest.raises(P.SchemaError, match="does not fix a price_origin"):
        P.origin_of("post_text")
    with pytest.raises(P.SchemaError, match="not one of"):
        P.origin_of("leaflet")


def test_a_comment_price_cannot_be_declared_a_retailer_price():
    """The filter that keeps consumer quotes out of promo aggregates reads `price_origin`, so a
    comment relabelled `retail_leaflet` would walk straight into them (SPEC 3.17 (4))."""
    with pytest.raises(P.SchemaError, match="carrier comment carries price_origin consumer_quote"):
        position(carrier="comment", price_origin="retail_leaflet")
    assert position(carrier="comment", price_origin="consumer_quote").carrier == "comment"
    # post_text takes either, because SPEC does not rule on it — a chain's post and a community
    # channel's post about prices are not the same voice
    for origin in P.PRICE_ORIGINS:
        assert position(carrier="post_text", price_origin=origin).price_origin == origin


def test_an_unknown_carrier_or_origin_stops_the_record():
    with pytest.raises(P.SchemaError, match="carrier"):
        position(carrier="leaflet")
    with pytest.raises(P.SchemaError, match="price_origin"):
        position(price_origin="shelf_tag")
    with pytest.raises(P.SchemaError, match="extraction_source"):
        position(extraction_source=" ")


def test_a_qualifier_belongs_to_a_price_and_only_to_a_price():
    with pytest.raises(P.SchemaError, match="belongs to a price"):
        position(price_qualifier="exact")
    with pytest.raises(P.SchemaError, match="belongs to a price"):
        position(price_promo=90.0, price_qualifier=None)
    with pytest.raises(P.SchemaError, match="not exact/approx"):
        position(price_promo=90.0, price_qualifier="roughly")


def test_a_size_is_a_number_and_a_unit_or_neither():
    with pytest.raises(P.SchemaError, match="number and a unit"):
        position(size_value=500.0)
    with pytest.raises(P.SchemaError, match="number and a unit"):
        position(size_unit="г")
    with pytest.raises(P.SchemaError, match="not normalised"):
        position(size_value=0.5, size_unit="л")


# --- the category vocabulary ----------------------------------------------------------------------


def test_the_category_vocabulary_is_the_registrys_and_is_not_restated_in_code():
    """Both levels of the taxonomy, read off the file: a leaflet names «Морозиво» (a group with no
    split) and «Сметана» (a subcategory) and both are legal categories for a position.

    The contract says "the 13+2 taxonomy"; the registry carries 2 tracked groups and 9 dairy
    subcategories = 11 keys today. The count is not asserted as a literal on purpose — it follows
    the file, so 5c3 widening the taxonomy widens this without a code change.
    """
    keys = P.category_keys(REGISTRY.taxonomy)
    assert keys == set(REGISTRY.taxonomy.tracked_groups) | {
        key
        for group in REGISTRY.taxonomy.tracked_groups.values()
        for key in (group.get("subcategories") or {})
    }
    assert {"dairy", "ice-cream", "milk", "butter", "sour-cream"} <= keys
    assert "морозиво" not in keys, "the keys are the kebab-case ones that reach result files"


# --- the parser -----------------------------------------------------------------------------------

CATEGORIES = P.category_keys(REGISTRY.taxonomy)
ALIASES = watchlist_aliases(REGISTRY.watchlist)
STAMP = {
    "categories": CATEGORIES,
    "carrier": "leaflet_page",
    "price_origin": "retail_leaflet",
    "extraction_source": SOURCE,
    "aliases": ALIASES,
}


def parse(reply: str, **over):
    return P.parse_positions(reply, **{**STAMP, **over})


def test_a_page_of_offers_comes_back_as_positions():
    reply = json.dumps(
        [
            {
                "brand": "Рудь",
                "line": "Золотий Каштан",
                "category": "ice-cream",
                "size": "70 г",
                "price_promo": "19,90",
                "price_old": "27,90",
                "discount_pct_printed": "-29%",
            },
            {"brand": "Своя Лінія", "category": "milk", "size": "0,9 л", "fat": "2,5%"},
        ],
        ensure_ascii=False,
    )
    first, second = parse(reply)
    assert first.brand_id == "rud" and first.brand_raw == "Рудь"
    assert first.identity() == ("rud", "Золотий Каштан", "ice-cream", 70.0, "г", None)
    assert first.tier() == "position"
    assert first.depth() == pytest.approx((27.9 - 19.9) / 27.9)
    assert first.depth_disagrees_with_printed() is False
    assert first.price_qualifier == "exact"
    assert second.identity() == ("svoia-liniia", None, "milk", 900.0, "мл", 2.5)
    assert second.depth() is None and second.price_qualifier is None
    for row in (first, second):
        assert (row.carrier, row.price_origin, row.extraction_source) == (
            "leaflet_page",
            "retail_leaflet",
            SOURCE,
        )


def test_an_empty_page_is_an_answer_and_a_broken_reply_is_not():
    """The distinction the pilot's counters rest on. `[]` is "no dairy on this page"; a refusal is
    "this page was not read" — and a caller that conflates them reports its parse failures as
    pages with nothing on them (`[[empty_field_hides_several_states]]`)."""
    assert parse("[]") == []
    assert parse("```json\n[]\n```") == []
    for reply in ("", "   ", "I could not read the page.", "{}", "null"):
        with pytest.raises(P.SchemaError):
            parse(reply)


def test_a_fence_or_a_sentence_before_the_bracket_is_formatting_and_not_a_different_answer():
    """The same line `prompts._object` draws. Unwrapping is not salvage; repairing content is."""
    body = '[{"brand": "Рудь", "category": "ice-cream"}]'
    for reply in (body, f"```json\n{body}\n```", f"Here you go: {body}", f"```\n{body}\n```"):
        assert [row.brand_id for row in parse(reply)] == ["rud"]


@pytest.mark.parametrize("field", sorted(P.DECIDED_BY_CODE))
def test_a_reply_that_names_what_code_decides_is_refused(field):
    """SPEC 3.17 (2): the tier is assigned by CODE from field completeness. A model that names its
    own tier has assigned it, and a parser that ignored the key would let it happen invisibly. The
    same for the provenance fields — a model cannot be both subject and witness."""
    reply = json.dumps([{"brand": "Рудь", field: "position"}], ensure_ascii=False)
    with pytest.raises(P.SchemaError, match="which code decides and not a model"):
        parse(reply)


def test_an_unasked_key_is_refused_rather_than_dropped():
    """No salvage: a key nobody asked for means the model answered a different question, and
    quietly dropping it would hide that the instrument and the prompt have drifted apart."""
    with pytest.raises(P.SchemaError, match="unasked key: colour"):
        parse('[{"brand": "Рудь", "colour": "red"}]')
    assert set(P.REPLY_KEYS) & set(P.DECIDED_BY_CODE) == set()


def test_every_asked_key_is_accepted_and_nothing_else_is():
    """The positive half of the control above: each of the eight keys the prompt lists parses."""
    for key, value in (
        ("brand", "Рудь"),
        ("line", "Пломбір"),
        ("category", "ice-cream"),
        ("size", "500 г"),
        ("fat", "2,5%"),
        ("price_promo", "89,90"),
        ("price_old", "129,90"),
        ("discount_pct_printed", "-30%"),
    ):
        row = parse(json.dumps([{"brand": "Рудь", key: value}], ensure_ascii=False))[0]
        assert row.brand_raw == "Рудь", key


def test_a_reply_the_schema_refuses_names_the_defect():
    for reply, fragment in (
        ('[{"line": "Пломбір"}]', "names no brand"),
        ('[{"brand": "   "}]', "empty"),
        ('[{"brand": "Рудь", "line": null}]', "an unread key is omitted"),
        ('[{"brand": "Рудь", "line": ""}]', "an unread key is omitted"),
        ('[{"brand": "Рудь", "category": "cheeseburger"}]', "outside the taxonomy"),
        ('[{"brand": "Рудь", "size": "2х100 г"}]', "multipack"),
        ('[{"brand": "Рудь", "size": "500"}]', "not a number and one of"),
        ('[{"brand": "Рудь", "price_promo": "80-90"}]', "not one number"),
        ('[{"brand": "Рудь", "price_promo": -5}]', "must be positive"),
        ('[{"brand": "Рудь", "price_promo": true}]', "neither a number nor a printed price"),
        ('[{"brand": "Рудь", "fat": "нежирний"}]', "not a percentage"),
        ('[{"brand": "Рудь", "discount_pct_printed": "half"}]', "not a percentage"),
        ('["Рудь"]', "not an object"),
        ('{"brand": "Рудь"}', "no JSON array"),
        ('[{"brand": "Рудь"', "malformed JSON"),
    ):
        with pytest.raises(P.SchemaError, match=fragment):
            parse(reply)


def test_one_bad_entry_invalidates_the_whole_answer():
    """Strict at the level of the reply, exactly as `parse_reply` is: the answer is one page, and
    half a page kept is a page nobody can audit against the image."""
    reply = json.dumps(
        [{"brand": "Рудь", "category": "ice-cream"}, {"brand": "Ласунка", "size": "нема"}],
        ensure_ascii=False,
    )
    with pytest.raises(P.SchemaError):
        parse(reply)


def test_a_hedged_price_hedges_the_record():
    """«по 90» beside a crossed-out 129,90 is not an exact observation, and the record carries one
    qualifier — so the hedge wins rather than being averaged away."""
    reply = '[{"brand": "Рудь", "price_promo": "по 90", "price_old": "129,90"}]'
    row = parse(reply, carrier="comment", price_origin="consumer_quote")[0]
    assert row.price_qualifier == "approx"
    assert (row.price_promo, row.price_old) == (90.0, 129.9)
    assert row.depth() == pytest.approx((129.9 - 90.0) / 129.9)


def test_a_json_number_price_is_exact_and_a_string_carries_its_own_qualifier():
    numeric = parse('[{"brand": "Рудь", "price_promo": 29.9}]')[0]
    assert (numeric.price_promo, numeric.price_qualifier) == (29.9, "exact")
    hedged = parse('[{"brand": "Рудь", "price_promo": "~29,9"}]')[0]
    assert (hedged.price_promo, hedged.price_qualifier) == (29.9, "approx")


def test_the_printed_percentage_reaches_the_flag_and_the_sign_is_dropped():
    reply = '[{"brand": "Рудь", "price_promo": "90", "price_old": "120", "discount_pct_printed": "-50%"}]'
    row = parse(reply)[0]
    assert row.discount_pct_printed == 50.0
    assert row.depth() == pytest.approx(0.25)
    assert row.depth_disagrees_with_printed() is True


@pytest.mark.parametrize("raw, expect", [("-51%", 51.0), ("51", 51.0), ("51%", 51.0), (-30, 30.0)])
def test_a_printed_discount_is_stored_as_a_magnitude(raw, expect):
    assert P.parse_percent(raw) == expect


def test_an_unresolved_brand_keeps_its_string_and_never_guesses_a_watchlist_row():
    """«Premialle» is a real ATB leaflet TM and it is NOT «Премія». A near-miss resolved by
    resemblance would credit a watchlist brand with a mention nobody matched — the 5c3 named
    revision is where new names are ruled onto the list."""
    row = parse('[{"brand": "Premialle", "category": "cheese"}]')[0]
    assert row.brand_id is None and row.brand_raw == "Premialle"
    assert row.identity()[0] == "raw:Premialle"
    assert P.resolve_brand("Premialle", ALIASES) is None
    assert P.resolve_brand("  рудь  ", ALIASES) == "rud", "casefolded, whitespace collapsed"
    assert P.resolve_brand("Три Ведмеді", ALIASES) == "try-vedmedi"
    # the audit's Latin-script finding is RULED ON now: SPEC 3.17 (13)(b) put «Three Bears», «Rud»
    # and «LIMO» into the watchlist on the evidence of the pages that print them
    assert P.resolve_brand("Three Bears", ALIASES) == "try-vedmedi"
    assert P.resolve_brand("Rud", ALIASES) == "rud" and P.resolve_brand("LIMO", ALIASES) == "limo"
    # and the negative half of the same ruling, which is the reason it is three names and not a
    # transliteration rule: «Galicia» on atb_market_official_4510 is a JUICE TM, not «Галичина»
    assert P.resolve_brand("Galicia", ALIASES) is None
    assert P.resolve_brand("Галичина", ALIASES) == "halychyna"


def test_the_carrier_is_the_callers_and_an_unknown_one_stops_the_parse():
    for carrier in P.CARRIERS:
        origin = "consumer_quote" if carrier == "comment" else "retail_leaflet"
        rows = parse('[{"brand": "Рудь"}]', carrier=carrier, price_origin=origin)
        assert rows[0].carrier == carrier and rows[0].price_origin == origin
    with pytest.raises(P.SchemaError, match="carrier"):
        parse('[{"brand": "Рудь"}]', carrier="leaflet")
    with pytest.raises(P.SchemaError, match="carrier comment carries"):
        parse('[{"brand": "Рудь"}]', carrier="comment", price_origin="retail_leaflet")


def test_the_parser_and_the_prompt_ask_for_the_same_keys():
    """The gap that would otherwise be charged to the model. Held from this side too, so an edit to
    either list has to break a test in both files."""
    for key in P.REPLY_KEYS:
        assert f'"{key}"' in prompts.PROMPTS["positions_post_gm4"], key
    assert prompts.POSITIONS == {"positions_post_gm4", "positions_text_gm4"}


def test_an_unregistered_instrument_family_is_refused_rather_than_read_as_empty():
    """SPEC 3.17 (8) split the schema's `attribute` from the wire's `fat`, and a family with no row
    in `WIRE_KEYS` falls through to the schema's own name — which no registered prompt asks for.

    Both directions then fail SILENTLY: a reply naming `attribute` is refused as an unasked key, and
    one naming `fat` passes the key check and is dropped by the parser, which is looking elsewhere.
    That is the empty-class silence this repo keeps paying for, so it is a refusal instead."""
    reply = '[{"brand": "Галка", "category": "ice-cream", "fat": "2,5%"}]'
    kwargs = dict(
        categories=frozenset({"ice-cream"}),
        carrier="leaflet_page",
        price_origin="retail_leaflet",
        extraction_source=SOURCE,
        aliases={},
    )
    # the registered family reads it
    assert P.parse_positions(reply, **kwargs)[0].attribute_pct == 2.5
    with pytest.raises(P.SchemaError, match="instruments are not registered"):
        P.parse_positions(reply, family="coffee", **kwargs)


# --- the pre-filter -------------------------------------------------------------------------------

LEXICON = lexicon.load_lexicon()  # the vocabulary LAW, SPEC 3.17 (8) — not the draft it migrated
COMPILED = yield_screen.compile_categories(LEXICON)
COMPILED_ALIASES = yield_screen.compile_aliases(ALIASES)


def passes(text: str):
    return P.prefilter({"text": text}, COMPILED, COMPILED_ALIASES)


@pytest.mark.parametrize(
    "text, hit, pattern",
    [
        ("Молоко Яготинське 2,5% 900 г — 39,90 грн", "category:dairy:молок", "2,5%"),
        ("Пломбір Рудь 500 г", "brand:rud", "500 г"),
        ("Сметана 15% ТМ Яготинська 350 г", "category:dairy:сметан", "15%"),
        ("0,5 л молока", "category:dairy:молок", "0,5 л"),
        ("Морозиво Ласунка 12,90 грн", "category:ice-cream:морозив", "12,90 грн"),
    ],
)
def test_the_prefilter_passes_a_hit_beside_a_number_and_says_which(text, hit, pattern):
    """The evidence is the payload: a pass carries the line, the term that fired and the pattern
    beside it, so a human can check one at a glance instead of trusting a count."""
    found = passes(text)
    assert found is not None
    assert (found["hit"], found["pattern"]) == (hit, pattern)
    assert found["line"] == " ".join(text.split())


@pytest.mark.parametrize(
    "text, why",
    [
        ("Люблю сир і морозиво!", "a category with no number"),
        ("Кросівки, розмір 37, 1499 грн", "a price with no category and no brand"),
        (
            "Знижка 20% на тренування, реєстрація за посиланням",
            "the shape of a hit and no taxonomy",
        ),
        ("Морозиво\nвсього 89,90 грн", "the hit and the number on different lines"),
        ("", "nothing at all"),
        ("Сир 500 грам", "«грам» is outside the six units the contract names"),
        ("Молоко 5 гривень", "«гривень» is outside them too"),
    ],
)
def test_the_prefilter_refuses_and_the_conjunction_is_what_refuses(text, why):
    assert passes(text) is None, why


def test_the_same_line_rule_is_the_rule_and_the_looser_reading_is_measurable():
    """The strictness is a choice and the census prices it, so both readings have to be computable
    from these primitives — this is the pair the census's `passed_row_level` column is built from."""
    split = "Морозиво Рудь\nвсього 89,90 грн"
    assert passes(split) is None
    assert yield_screen.brand_hits(split, COMPILED_ALIASES) == ["rud"]
    assert P.size_price_pattern(split) == "89,90 грн"


@pytest.mark.parametrize(
    "text, expect",
    [
        ("90 грн", "90 грн"),
        ("500 г", "500 г"),
        ("1,5 кг", "1,5 кг"),
        ("0,5л", "0,5л"),
        ("82,5%", "82,5%"),
        ("500 грам", None),
        ("5 гривень", None),
        ("сир", None),
        ("37 розмір", None),
    ],
)
def test_the_size_price_pattern_is_the_six_units_the_contract_names(text, expect):
    """Closed on purpose: widening it moves the frame the text bar of 3.17 (6) is measured over."""
    assert P.size_price_pattern(text) == expect
    assert P.SIZE_PRICE_UNITS == ("кг", "мл", "грн", "г", "л", "%")


def test_grn_wins_over_g_because_the_alternation_is_ordered():
    """«90 грн» must not read as a size. The branch order is load-bearing, so it is pinned."""
    assert P.pattern_kind(P.size_price_pattern("90 грн")) == "currency"
    assert P.pattern_kind(P.size_price_pattern("500 г")) == "size"
    assert P.pattern_kind(P.size_price_pattern("82,5%")) == "percent"
    assert P.size_price_patterns("масло 82,5%, 180 г — 79,99 грн") == [
        "82,5%",
        "180 г",
        "79,99 грн",
    ]
