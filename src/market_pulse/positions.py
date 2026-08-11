"""The position layer's schema: one SKU as a leaflet page or a text row names it.

SPEC amendment 3.17, which answers question 7 of `docs/PRODUCT.md` — what the chains promote, at
what price, and at what discount depth. Three of its rules are structural and are enforced here
rather than trusted:

* **Identity is not price.** :meth:`Position.identity` returns (brand, line, category, size,
  attribute_pct) and no price field can reach it. A price is an OBSERVATION at (channel, date,
  carrier), so the same SKU at two prices is one identity with two observations — and a test holds
  the tuple to that.
* **The tier is assigned by CODE, never by the model.** :func:`tier` is a pure function of which
  fields are filled in. Nothing in a model's reply can name a tier, and the parser refuses a reply
  that tries.
* **No field is ever imputed.** The dataclass has **no defaults**: every field is passed
  explicitly, so a caller cannot forget one and receive ``None``. ``depth`` and ``tier`` are
  functions and not fields, so neither can be stored wrong. An empty string is refused rather than
  read as "absent" — `""` is not an answer, and turning it into one is the imputation this rule
  exists to forbid.

The category vocabulary is deliberately NOT restated here. It comes from
`config/registry.yaml`'s taxonomy through :func:`category_keys`, so the day 5c3 widens the taxonomy
this schema follows it. Today that is 2 group keys + 9 dairy subcategory keys = 11 names.
"""

import json
import re
from dataclasses import MISSING, dataclass, fields

from market_pulse import lexicon
from market_pulse.registry import Taxonomy

CARRIERS = ("leaflet_page", "post_text", "comment")
"""Where the record was read — SPEC 3.17 (4). A price's carrier is part of the observation."""

PRICE_ORIGINS = ("retail_leaflet", "consumer_quote")
"""Whose price it is. Consumer quotes NEVER enter promo aggregates; they feed the price aspect of
question 2 (SPEC 3.17 (4)), and that filter reads this field."""

CARRIER_ORIGIN = {"leaflet_page": ("retail_leaflet",), "comment": ("consumer_quote",)}
"""The two carriers whose origin SPEC fixes. ``post_text`` is deliberately absent: a retail chain's
post and an aggregator's repost are the retailer speaking, and a community channel's post about
prices may not be — SPEC does not rule on it, so the caller decides and the record says which."""

TIERS = ("position", "product_mention", "brand_mention")
"""The ladder, most specific first. Its rungs are :func:`tier`'s only possible answers."""

SIZE_UNITS = ("г", "мл")
"""Everything normalises to grams or millilitres, so two spellings of one pack compare equal."""

QUALIFIERS = ("exact", "approx")
"""Whether the number is the printed price or a hedged one — «по 90», «~89». A qualifier is not a
confidence: it says what the source wrote."""

APPROX_MARKERS = ("~", "≈", "по ")
# ponytail: the three markers the contract names («по 90», «~»). «близько», «десь», «від» are NOT in
# it — widening this tuple changes what a recorded `approx` means, so it is a named revision, not a
# tweak, and the pilot's counts would stop being comparable across it.

_NUMBER = r"\d+(?:[.,]\d+)?"
_SIZE = re.compile(rf"^({_NUMBER})\s*(кг|мл|г|л)$", re.IGNORECASE)
_MULTIPACK = re.compile(rf"^{_NUMBER}\s*[xх×*]\s*{_NUMBER}", re.IGNORECASE)
_FAT = re.compile(rf"^({_NUMBER})\s*%?$")
_TO_GRAMS_OR_ML = {"г": ("г", 1.0), "кг": ("г", 1000.0), "мл": ("мл", 1.0), "л": ("мл", 1000.0)}

PRINTED_TOLERANCE_PP = 1.0
"""How far a printed «-51%» may sit from the computed depth before it is flagged, in percentage
points. Leaflets round the headline; 1 pp absorbs rounding and nothing else.

# ponytail: one constant, no per-chain table. If a chain is found rounding harder than this, the
# flag fires and the record says so — which is the outcome wanted, since the flag is a report and
# never a resolution (SPEC 3.17 (3): the printed % never substitutes arithmetic)."""


class SchemaError(ValueError):
    """A value that is not a valid answer. Its ``reason`` is what gets counted, never coerced."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def category_keys(taxonomy: Taxonomy) -> frozenset[str]:
    """Every category name a position may carry: the tracked groups and their subcategories.

    Both levels, because a leaflet names both — «Морозиво» is a group with no split and «Сметана»
    is a subcategory of dairy. Read off the registry rather than restated, so widening the taxonomy
    widens this without a code change (SPEC §3: new groups are added by registry edit only).
    """
    return frozenset(
        {group for group in taxonomy.tracked_groups}
        | {
            key
            for group in taxonomy.tracked_groups.values()
            for key in (group.get("subcategories") or {})
        }
    )


@dataclass(frozen=True)
class Position:
    """One SKU as one source names it. Every field is required — see the module docstring.

    ``brand_id`` is the watchlist key when the name resolves to one and ``brand_raw`` is the string
    as written; at least one of the two must be there, because all three rungs of the ladder start
    at a brand. A record naming no brand at all is refused rather than given a fourth rung: SPEC
    3.17 (2) has three, and inventing one here would be law this contract has no authority to write.
    """

    brand_id: str | None
    brand_raw: str | None
    line: str | None
    category: str | None
    size_value: float | None
    size_unit: str | None
    attribute_pct: float | None
    price_promo: float | None
    price_old: float | None
    discount_pct_printed: float | None
    price_qualifier: str | None
    price_origin: str
    carrier: str
    extraction_source: str

    def __post_init__(self) -> None:
        for name in ("brand_id", "brand_raw", "line", "category", "size_unit", "price_qualifier"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise SchemaError(f"{name} is present and empty — absent is None, not ''")
        if not (self.brand_id or self.brand_raw):
            raise SchemaError("a position names a brand: brand_id or brand_raw")
        if self.carrier not in CARRIERS:
            raise SchemaError(f"carrier {self.carrier!r} is not one of {list(CARRIERS)}")
        if self.price_origin not in PRICE_ORIGINS:
            raise SchemaError(
                f"price_origin {self.price_origin!r} is not one of {PRICE_ORIGINS[0]}/{PRICE_ORIGINS[1]}"
            )
        allowed = CARRIER_ORIGIN.get(self.carrier)
        if allowed is not None and self.price_origin not in allowed:
            raise SchemaError(f"carrier {self.carrier} carries price_origin {allowed[0]}")
        if not self.extraction_source.strip():
            raise SchemaError("extraction_source names the instrument and cannot be empty")
        if (self.size_value is None) != (self.size_unit is None):
            raise SchemaError("a size is a number and a unit, or neither")
        if self.size_unit is not None and self.size_unit not in SIZE_UNITS:
            raise SchemaError(f"size_unit {self.size_unit!r} is not normalised to г or мл")
        for name in (
            "size_value",
            "attribute_pct",
            "price_promo",
            "price_old",
            "discount_pct_printed",
        ):
            value = getattr(self, name)
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int | float)
            ):
                raise SchemaError(f"{name} is not a number")
            if value is not None and value <= 0:
                raise SchemaError(f"{name} must be positive, not {value}")
        if self.attribute_pct is not None and self.attribute_pct > 100:
            raise SchemaError(f"attribute_pct {self.attribute_pct} is not a percentage")
        has_price = self.price_promo is not None or self.price_old is not None
        if has_price != (self.price_qualifier is not None):
            raise SchemaError("price_qualifier belongs to a price, and only to a price")
        if self.price_qualifier is not None and self.price_qualifier not in QUALIFIERS:
            raise SchemaError(f"price_qualifier {self.price_qualifier!r} is not exact/approx")

    def identity(self) -> tuple:
        """(brand, line, category, size, attribute_pct) — SPEC 3.17 (2), and no price in it.

        The brand key is ``brand_id`` when it resolved and the raw string otherwise, so two records
        of the same watchlist brand under different spellings are one identity and an unresolved
        name never merges into a resolved one.
        """
        return (
            self.brand_id or f"raw:{self.brand_raw}",
            self.line,
            self.category,
            self.size_value,
            self.size_unit,
            self.attribute_pct,
        )

    def tier(self) -> str:
        return tier(self)

    def depth(self) -> float | None:
        """(old − promo) / old, and only when both prices are there — SPEC 3.17 (3).

        Never reconstructed from the printed percentage: one price without an old one is a promo
        price whose depth is unknown, and ``None`` is that answer. A method rather than a field so
        that no writer can put a number here that the two prices do not support.
        """
        if self.price_promo is None or self.price_old is None:
            return None
        return (self.price_old - self.price_promo) / self.price_old

    def depth_disagrees_with_printed(self) -> bool:
        """Does the leaflet's own «-51%» disagree with the arithmetic by more than the tolerance?

        A flag, not a resolution. Both numbers stay in the record and neither is corrected: the
        printed percentage is what the chain claims and the pair is what it charges, and which one
        is wrong is not this layer's ruling to make.
        """
        computed = self.depth()
        if computed is None or self.discount_pct_printed is None:
            return False
        return abs(computed * 100 - self.discount_pct_printed) > PRINTED_TOLERANCE_PP


def has_size(position: Position) -> bool:
    return position.size_value is not None


def tier(position: Position) -> str:
    """The ladder of SPEC 3.17 (2), as a pure function of which fields are filled in.

    * ``position`` — a category AND at least one differentiating attribute (line, size,
      attribute_pct).
    * ``product_mention`` — a category or an attribute, but not both.
    * ``brand_mention`` — the brand alone.

    Two cells SPEC's three sentences do not reach, decided here and pinned by the truth-table test
    (`tests/test_positions.py`), so the reading is visible rather than implicit:

    * **brand + category + line, no size and no attribute** is a ``position``. ``line`` is a
      differentiating attribute — it is exactly what variant C adds to identity in 3.17 (2), and a
      named line inside a category is what an aggregate can follow week to week.
    * **brand + size (or attribute, or line) with NO category** is a ``product_mention``. It is more than
      a bare brand mention and it is not a position, because the category half of the identity is
      missing and no aggregate for question 7 can place it.
    """
    attributes = (
        position.line is not None or has_size(position) or position.attribute_pct is not None
    )
    if position.category is not None and attributes:
        return "position"
    if position.category is not None or attributes:
        return "product_mention"
    return "brand_mention"


def parse_size(raw: str) -> tuple[float, str]:
    """«0,5 л» → (500.0, "мл"), «1 кг» → (1000.0, "г"). Refuses anything it cannot read.

    Multipacks are refused rather than multiplied: «2х100 г» and «200 г» are different SKUs on a
    shelf and folding one into the other would invent a pack that is not on the page.
    """
    text = " ".join(str(raw).split())
    if _MULTIPACK.match(text):
        raise SchemaError(f"size {text!r} is a multipack — a pack count is not a size")
    found = _SIZE.match(text)
    if not found:
        raise SchemaError(f"size {text!r} is not a number and one of кг/г/л/мл")
    unit, factor = _TO_GRAMS_OR_ML[found.group(2).casefold()]
    return round(float(found.group(1).replace(",", ".")) * factor, 3), unit


def parse_fat(raw: str) -> float:
    """«2,5%» → 2.5. A word — «нежирний» — is refused: it is a claim, not a number."""
    text = " ".join(str(raw).split())
    found = _FAT.match(text)
    if not found:
        raise SchemaError(f"fat {text!r} is not a percentage")
    return float(found.group(1).replace(",", "."))


def parse_price(raw: str) -> tuple[float, str]:
    """«89,90 грн» → (89.9, "exact"); «по 90» and «~89» → approx — the contract's two markers.

    The currency word is dropped and the number is kept; a range («80-90») is refused, because a
    range is two prices and the schema holds one.
    """
    text = " ".join(str(raw).split())
    qualifier = "approx" if any(m in text.casefold() for m in APPROX_MARKERS) else "exact"
    stripped = re.sub(r"(грн|₴|uah|\.)$", "", text.casefold().strip(), flags=re.IGNORECASE).strip()
    for marker in APPROX_MARKERS:
        stripped = stripped.replace(marker, " ")
    stripped = " ".join(stripped.split())
    if not re.fullmatch(_NUMBER, stripped):
        raise SchemaError(f"price {text!r} is not one number")
    return float(stripped.replace(",", ".")), qualifier


def origin_of(carrier: str) -> str:
    """The price origin SPEC fixes for a carrier. ``post_text`` has none and must be told.

    One derivation, so a caller cannot decide it a second way: a comment's price is a consumer
    quote and a leaflet page's is the retailer's, and those two are what the promo aggregate's
    filter rests on.
    """
    if carrier not in CARRIERS:
        raise SchemaError(f"carrier {carrier!r} is not one of {list(CARRIERS)}")
    allowed = CARRIER_ORIGIN.get(carrier)
    if allowed is None:
        raise SchemaError(f"carrier {carrier} does not fix a price_origin — the caller states it")
    return allowed[0]


def assert_no_imputation() -> None:
    """Every field is required, and the two computed values are not fields. Called by the tests.

    A default on any field would let a caller omit it and receive ``None`` — which reads downstream
    exactly like "the source did not name it". That is the imputation SPEC 3.17 (2) forbids, and
    this is the one line that makes its absence checkable.
    """
    for field in fields(Position):
        if field.default is not MISSING or field.default_factory is not MISSING:
            raise SchemaError(f"{field.name} has a default — a missing field would read as absent")
    for name in ("tier", "depth", "depth_disagrees_with_printed"):
        if name in {field.name for field in fields(Position)}:
            raise SchemaError(f"{name} is a field — a computed value must not be storable")


# --- the parser: strict, and it refuses rather than salvages ---------------------------------------

REPLY_KEYS = (
    "brand",
    "line",
    "category",
    "size",
    "fat",
    "price_promo",
    "price_old",
    "discount_pct_printed",
)
"""Exactly what the two position prompts ask for, and the whole vocabulary a reply may use.

An unknown key is a refusal and not a shrug: it means the model answered a question nobody asked,
and the three keys it is most likely to invent are the three that must never come from it — `tier`,
`carrier` and `price_origin` are decided from the answer, not by it.

These are WIRE keys, and `fat` is one of them on purpose: SPEC 3.17 (8) renamed the schema's field
to `attribute` and left the registered prompts alone, so the vocabulary a reply may use is still the
dairy instruments' own. :data:`WIRE_KEYS` is where the two meet."""

DECIDED_BY_CODE = ("tier", "carrier", "price_origin", "extraction_source", "depth", "brand_id")
"""Named separately from the rest of the unknown keys so the refusal says WHY.

`tier` is the one that matters: SPEC 3.17 (2) says the ladder is assigned by code from field
completeness, and a model that names its own tier has assigned it. The others would let a reply
claim its own provenance."""

WIRE_KEYS = {"dairy": {"attribute": "fat"}}
"""Schema field → the key that instrument family writes ON THE WIRE, and the inverse read backwards.

SPEC 3.17 (8) generalised the schema's fifth presence field from `fat` to `attribute`: the ladder is
a function of PRESENCE, and «жирність» is only what a DAIRY source happens to differentiate a SKU
by. The instruments did not move with it, and must not: `positions_post_gm4` and
`positions_text_gm4` are registered prompt texts pinned by sha in
`results/sku_pilot_prereg*.json`, so they still ask for `"fat"` and their replies still say `"fat"`.
Editing a registered text is not a rename, it is a new registration (SPEC 3.17 (5)).

So the wire keeps the domain word and the schema carries the general one, and this table is the one
place the two are tied together — the pack column, the validator's column and the parser's key all
read it. A second instrument family (coffee, say) registers its own prompts and adds one row here;
a family with no entry uses the schema's own name, which is why the table is a translation and not
a vocabulary.
"""

DEFAULT_FAMILY = "dairy"
"""The only family with registered instruments today. Named once here rather than defaulted in
three signatures, so the day a second one exists the callers that must choose are greppable."""


def wire_key(field: str, family: str = DEFAULT_FAMILY) -> str:
    """What ``family``'s replies and packs call this schema field. Unaliased fields are themselves."""
    return WIRE_KEYS.get(family, {}).get(field, field)


_PERCENT = re.compile(rf"^-?\s*({_NUMBER})\s*%?$")


def parse_percent(raw) -> float:
    """«-51%» → 51.0. The sign is dropped: a printed discount is a reduction, and a stored −51
    would compare the wrong way round against a depth of 0.51."""
    if isinstance(raw, int | float) and not isinstance(raw, bool):
        return abs(float(raw))
    found = _PERCENT.match(" ".join(str(raw).split()))
    if not found:
        raise SchemaError(f"printed discount {raw!r} is not a percentage")
    return float(found.group(1).replace(",", "."))


def _array(reply: str) -> list:
    """The JSON array inside a reply — tolerant of wrappers, strict about content.

    The same line `prompts._object` draws, and it is worth restating where it sits: a ```json fence
    or a sentence before the bracket is FORMATTING, so unwrapping is not salvage. Salvage would be
    repairing what is inside — filling a missing key, coercing a type, reading a bare object as a
    one-item list — and none of that happens anywhere below.
    """
    text = str(reply).strip()
    if not text:
        raise SchemaError("empty reply")
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    start = text.find("[")
    if start < 0:
        raise SchemaError("no JSON array in reply")
    try:
        value, _ = json.JSONDecoder().raw_decode(text[start:])
    except ValueError:
        raise SchemaError("malformed JSON") from None
    if not isinstance(value, list):
        raise SchemaError("reply is not a JSON array")
    return value


def resolve_brand(name: str, aliases: dict[str, str]) -> str | None:
    """The watchlist key for a brand the model wrote, or ``None`` when the watchlist has no such
    name. ``aliases`` is `market_pulse.brands.watchlist_aliases`' table, so "a brand" means here
    what it means to the scorer.

    Exact alias, casefolded and whitespace-collapsed — no stemming and no fuzzy match. An unresolved
    name is kept as ``brand_raw`` and gets its own identity: guessing which watchlist row a near-miss
    belongs to is what the 5c3 named revision is for, and «Premialle» is not «Премія».
    """
    return aliases.get(" ".join(str(name).split()).casefold())


def _number_or_price(value, field: str) -> tuple[float, str]:
    """A price as the model gave it: a JSON number is exact, a string carries its own qualifier."""
    if isinstance(value, int | float) and not isinstance(value, bool):
        if value <= 0:
            raise SchemaError(f"{field} must be positive, not {value}")
        return float(value), "exact"
    if not isinstance(value, str):
        raise SchemaError(f"{field} is neither a number nor a printed price")
    return parse_price(value)


def parse_positions(
    reply: str,
    *,
    categories: frozenset[str],
    carrier: str,
    price_origin: str,
    extraction_source: str,
    aliases: dict[str, str],
    family: str = DEFAULT_FAMILY,
) -> list[Position]:
    """One model reply → the positions in it, or :class:`SchemaError` naming what is wrong.

    Strict at the level of the whole reply, exactly as `prompts.parse_reply` is: one bad entry
    invalidates the answer, because the answer is one page or one row. A row that fails here is
    counted by its ``reason`` and excluded — never coerced, and never read as an empty page.
    **`[]` and a refusal are different outcomes and a caller that conflates them is reporting the
    parse failures as pages with no dairy on them.**

    ``carrier``, ``price_origin`` and ``extraction_source`` are stamped by the caller and are
    refused if the reply carries them: they are facts about the request, and a model cannot be both
    the subject and the witness.

    ``family`` says whose instrument produced the reply, and the only thing it decides is which wire
    key carries the `attribute` field — `fat` for the dairy prompts (:data:`WIRE_KEYS`). It is not a
    domain switch: nothing else in this parser reads it.
    """
    if carrier not in CARRIERS:
        raise SchemaError(f"carrier {carrier!r} is not one of {list(CARRIERS)}")
    attribute_key = wire_key("attribute", family)
    out = []
    for index, entry in enumerate(_array(reply)):
        if not isinstance(entry, dict):
            raise SchemaError(f"entry {index} is not an object")
        if claimed := sorted(set(entry) & set(DECIDED_BY_CODE)):
            raise SchemaError(
                f"entry {index} names {claimed[0]}, which code decides and not a model"
            )
        if unknown := sorted(set(entry) - set(REPLY_KEYS)):
            raise SchemaError(f"entry {index} carries an unasked key: {unknown[0]}")
        for key, value in entry.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                raise SchemaError(f"entry {index} sends {key} empty — an unread key is omitted")
        brand = entry.get("brand")
        if not isinstance(brand, str) or not brand.strip():
            raise SchemaError(f"entry {index} names no brand, and every tier starts at one")
        category = entry.get("category")
        if category is not None:
            category = " ".join(str(category).split())
            if category not in categories:
                raise SchemaError(f"entry {index} category {category!r} is outside the taxonomy")
        size_value, size_unit = (None, None)
        if "size" in entry:
            size_value, size_unit = parse_size(entry["size"])
        prices, qualifiers = {}, []
        for key in ("price_promo", "price_old"):
            if key in entry:
                prices[key], qualifier = _number_or_price(entry[key], key)
                qualifiers.append(qualifier)
        out.append(
            Position(
                brand_id=resolve_brand(brand, aliases),
                brand_raw=" ".join(brand.split()),
                line=" ".join(str(entry["line"]).split()) if "line" in entry else None,
                category=category,
                size_value=size_value,
                size_unit=size_unit,
                attribute_pct=(parse_fat(entry[attribute_key]) if attribute_key in entry else None),
                price_promo=prices.get("price_promo"),
                price_old=prices.get("price_old"),
                discount_pct_printed=(
                    parse_percent(entry["discount_pct_printed"])
                    if "discount_pct_printed" in entry
                    else None
                ),
                # one qualifier for the record, and a hedge anywhere in it hedges the record:
                # «по 90» beside a crossed-out 129,90 is not an exact observation
                price_qualifier=("approx" if "approx" in qualifiers else "exact")
                if qualifiers
                else None,
                price_origin=price_origin,
                carrier=carrier,
                extraction_source=extraction_source,
            )
        )
    return out


# --- the pre-filter: which text rows are worth asking a model about --------------------------------

SIZE_PRICE_UNITS = tuple(lexicon.load_lexicon()["units"])
"""The units the contract names: «число + г|кг|л|мл|%|грн» — read from `config/lexicon.yaml`
(SPEC 3.17 (8)) and NOT restated here, which is what uni-a's LEAK L6 was.

Ordered longest-first in the law file, because a regex alternation takes the first branch that
matches and «г» before «грн» would read "90 грн" as a size. The list is deliberately closed: «500
грам» and «5 гривень» do NOT match it, and widening it would move the sample frame the text bar is
measured on, so it is a named revision and not a tweak.
"""

_SIZE_PRICE = re.compile(rf"{_NUMBER}\s*(?:{'|'.join(SIZE_PRICE_UNITS)})(?!\w)", re.IGNORECASE)


def size_price_pattern(text: str) -> str | None:
    """The first «число + unit» in this text, or None. The second half of the pre-filter's AND."""
    found = _SIZE_PRICE.search(text or "")
    return found.group(0) if found else None


def size_price_patterns(text: str) -> list[str]:
    """Every «число + unit» in this text, in order. What the census reads a row's shape from."""
    return _SIZE_PRICE.findall(text or "")


def pattern_kind(pattern: str) -> str:
    """``currency`` | ``percent`` | ``size`` — which of the six units fired.

    The pre-filter's second half accepts all three and cannot tell an OFFER from a recipe: «Кефір —
    400 мл» is a category term beside a size and passes, and it is an ingredient list. A currency
    marker is the cheapest deterministic signal that a line is priced at all, and ``percent`` is
    honestly its own bucket rather than folded into either — «82,5%» is a fat content and «-38%» is
    a discount, and nothing here can tell them apart.
    """
    low = pattern.casefold()
    if "грн" in low:
        return "currency"
    if "%" in low:
        return "percent"
    return "size"


def prefilter(row: dict, compiled: dict, aliases: list) -> dict | None:
    """Is this corpus row worth asking a position model about? Deterministic, and $0.

    SPEC 3.17 (4): text extraction runs only on rows a deterministic pre-filter passes. The rule is
    a conjunction — a watchlist brand or a tracked category term, **and** a size/price pattern — and
    both halves must be on **the same line**.

    Same-line rather than same-row, for two reasons. It is the project's own evidence discipline
    (`yield_screen.evidence_line` quotes a line, never a counter), and a row that names «сир»
    somewhere and «20%» somewhere else is very often two unrelated sentences. The looser reading is
    not lost: the census reports it in the next column, computed from these same primitives, so the
    cost of the strictness is a number rather than an argument.

    # ponytail: one rule, no window parameter. If the census shows leaflet-style posts splitting the
    # brand from the price across lines, the upgrade is a ±1-line window — and it is a named change,
    # because it moves the frame the text bar of 3.17 (6) is measured over.

    Returns the evidence — the line, the term that fired and the pattern beside it — so a human can
    check a pass at a glance. `None` is a fail, and it is not an error.
    """
    from market_pulse import yield_screen

    for line in (row.get("text") or "").splitlines():
        pattern = size_price_pattern(line)
        if pattern is None:
            continue
        found = yield_screen.evidence_line(line, compiled, aliases)
        if found is not None:
            return {
                "line": found["line"],
                "hit": f"{found['kind']}:{found['name']}",
                "matched": found["matched"],
                "pattern": pattern,
            }
    return None


# --- the ladder from a checklist: the adjudicator's side, and one function for both sides ----------

PRESENCE_FIELDS = ("brand", "line", "category", "size", "attribute")
"""What an adjudicator ticks per row. The five fields the ladder reads, and no price field: bar 3 of
SPEC 3.17 (6) is tier accuracy, and a price does not move a rung.

The fifth was `fat` until SPEC 3.17 (8): the ladder is a function of PRESENCE and «жирність» is only
what a dairy source differentiates a SKU by. These are SCHEMA names — the pack column and the
model's reply still say `fat`, through :data:`WIRE_KEYS`."""


def tier_from_presence(
    brand: bool, line: bool, category: bool, size: bool, attribute: bool
) -> str | None:
    """The rung a source reaches when it names exactly these fields, or ``None`` for no brand.

    Built by constructing a :class:`Position` with placeholder values and calling :func:`tier` on it,
    deliberately rather than by restating the rungs: the adjudicated tier and the model's tier MUST
    come out of one function, or bar 3 compares two ladders and a drift between them reads as model
    error. The placeholders are arbitrary because the ladder is a function of PRESENCE only — which
    is the property this indirection proves rather than claims.

    ``None`` means "this row names no position at all": the pre-filter's own false positives, which
    have no rung because every rung starts at a brand.
    """
    if not brand:
        return None
    return tier(
        Position(
            brand_id=None,
            brand_raw="?",
            line="?" if line else None,
            category="?" if category else None,
            size_value=1.0 if size else None,
            size_unit="г" if size else None,
            attribute_pct=1.0 if attribute else None,
            price_promo=None,
            price_old=None,
            discount_pct_printed=None,
            price_qualifier=None,
            price_origin="retail_leaflet",
            carrier="leaflet_page",
            extraction_source="ladder",
        )
    )


def ladder_table() -> dict[str, str]:
    """The whole ladder as data: every combination of the five fields → its rung.

    32 rows, keyed by the fields present joined with ``+`` (``"none"`` when a row names nothing).
    Serialised so a pre-registration can pin the LADDER and not only the bar: bar 3's gold is
    computed by this function from an operator's ticks, so a ladder that moved between the pack
    build and the pilot would move the gold silently and nothing downstream could see it.
    """
    out = {}
    for mask in range(1 << len(PRESENCE_FIELDS)):
        present = [field for index, field in enumerate(PRESENCE_FIELDS) if mask & (1 << index)]
        rung = tier_from_presence(**{field: field in present for field in PRESENCE_FIELDS})
        out["+".join(present) or "none"] = rung or "none"
    return dict(sorted(out.items()))


def ladder_sha256() -> str:
    """SHA256 of :func:`ladder_table`, canonically encoded — what the prereg and the pack both cite."""
    import hashlib

    payload = json.dumps(ladder_table(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
