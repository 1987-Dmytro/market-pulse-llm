"""The corrections record of «price-fix», driven both ways on synthetic rows (PHASE-ship-1 §2).

`config/price_corrections.yaml` is a hand-written record of what six leaflet pages print, and the
one thing a record like it must never do is silently apply nothing: a row it names that the export
does not carry, or a figure that never reaches the card the app renders, would leave the screen
publishing the misread the readers already corrected — with no sign that anything was claimed.

So both directions are pinned here: the correction lands on its ONE row, carrying what it replaced
and who read the page, all the way into the card; and a record naming a row the data does not carry
refuses by name instead of passing.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

spec = importlib.util.spec_from_file_location(
    "export_front_data", REPO_ROOT / "scripts" / "export_front_data.py"
)
efd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(efd)

ENTRY = {
    "row_id": "@blyzenkoua:7951:0",
    "carrier": "leaflet_page",
    "page": "blyzenkoua_7951.jpg",
    "promo_price": 42.99,
    "reads": "the tag prints 42⁹⁹ over a struck 53⁹⁹; the stored answer says «4,29»",
    "verified_by": ["reader-1", "reader-2", "team-lead"],
}


def position(row_id="@blyzenkoua:7951:0", carrier="leaflet_page", **over):
    """One position row of `results/promo_screen_data.json :: screen.positions`, as it is stored."""
    base = {
        "row_id": row_id,
        "carrier": carrier,
        "tier": "position",
        "brand": {"display": "Млековіта"},
        "chain": {"id": "blyzenko", "named_by_amendment_3_20": False},
        "item": {
            "category": "yogurt",
            "line": "ЙОГУРТ Натуральний",
            "size_value": 350.0,
            "size_unit": "г",
        },
        "evidence": {"channel": "@blyzenkoua", "msg_id": 7951},
        "promo_price": 4.29,
    }
    return base | over


def test_a_correction_lands_on_its_one_row_with_provenance_and_a_record_naming_no_row_refuses():
    """Both ways, plus the id that names two products: `row_id` repeats across carriers in the real
    export, so the entry's identity is `(row_id, carrier)` and the twin it does not name is left
    exactly as the store wrote it."""
    fixed, untouched = efd.page_true(
        [position(), position(row_id="@blyzenkoua:7951:1")], {"rows": [ENTRY]}
    )
    assert fixed["promo_price"] == 42.99
    assert efd.unit_price(fixed) == ("uah_per_kg", 122.8286)
    assert fixed["correction"]["was"] == {"promo_price": 4.29}
    assert fixed["correction"]["page"] == "blyzenkoua_7951.jpg"
    assert untouched["promo_price"] == 4.29 and "correction" not in untouched

    # the provenance reaches the card the app renders, or the screen shows a hand-corrected figure
    # with nothing on it that says a human corrected it
    card = efd.position_card(fixed, {"@blyzenkoua:7951": "blyzenkoua_7951.jpg"}, {})
    assert card["unit_price"] == 122.8286
    assert card["correction"]["verified_by"] == ["reader-1", "reader-2", "team-lead"]

    same_id = efd.page_true([position(), position(carrier="post_text")], {"rows": [ENTRY]})
    assert same_id[0]["promo_price"] == 42.99
    assert "correction" not in same_id[1] and same_id[1]["promo_price"] == 4.29

    with pytest.raises(SystemExit) as refused:
        efd.page_true([position(row_id="@blyzenkoua:7951:9")], {"rows": [ENTRY]})
    assert "config/price_corrections.yaml" in str(refused.value)

    # an entry that corrects nothing would stamp «виправлено вручну» on a row nobody changed
    empty = {key: value for key, value in ENTRY.items() if key != "promo_price"}
    with pytest.raises(SystemExit):
        efd.page_true([position()], {"rows": [empty]})


def test_the_pack_divides_the_price_and_a_row_with_no_pack_is_priced_by_its_own_size():
    """The multipack divisor, both ways — the four packs in the store (Рудь 6×100 г, Лацяти
    10×10 мл) carry the size of ONE piece and the price of the WHOLE pack, so a ₴/кг that forgot
    `pack_count` publishes ice cream at six times its price and puts it at the dear end of its own
    category's exhibit."""
    pack = position(item={"category": "ice-cream", "size_value": 100.0, "size_unit": "г",
                          "pack_count": 6}, promo_price=89.99)
    assert efd.unit_price(pack) == ("uah_per_kg", 149.9833)

    single = position(item={key: value for key, value in pack["item"].items()
                            if key != "pack_count"}, promo_price=89.99)
    assert efd.unit_price(single) == ("uah_per_kg", 899.9)

    # and a row that cannot carry a unit price at all says so instead of guessing a divisor
    assert efd.unit_price(position(item={"category": "ice-cream", "size_value": 1.0,
                                         "size_unit": "шт"}, promo_price=89.99)) is None


def test_a_missing_source_is_a_named_refusal_and_a_complete_set_passes(tmp_path):
    """`make front`'s data step must not write a partial export: a figure that silently became a
    blank is worse than a red panel, so the producer refuses BY NAME and writes nothing."""
    present = tmp_path / "promo_screen_data.json"
    present.write_text("{}", encoding="utf-8")
    assert efd.refuse_on_a_missing_source((present,)) is None

    with pytest.raises(SystemExit) as refused:
        efd.refuse_on_a_missing_source((present, tmp_path / "price_corrections.yaml"))
    assert "price_corrections.yaml" in str(refused.value)


def test_a_category_with_no_priced_row_keeps_its_row_and_its_count():
    """No silent zero-row category. The rows are the REGISTRY's categories and not the observed
    ones (DESIGN-ship-1 §10): a category the market stopped promoting, and one whose rows carry a
    size no price can be cut from, both keep their card — one saying «немає в даних» and the other
    showing the positions it holds beside an empty set of bases. A card that quietly disappears is
    an empty state with no sentence, and the reader cannot tell it from a category nobody sells."""
    priced = position()
    unpriceable = position(
        row_id="@blyzenkoua:7952:0",
        item={"category": "ice-cream", "size_value": 1.0, "size_unit": "шт"},
        evidence={"channel": "@blyzenkoua", "msg_id": 7952},
        promo_price=29.9,
    )
    media = {
        "pages": {"@blyzenkoua:7951": "page.jpg", "@blyzenkoua:7952": "page.jpg"},
        "flyers": [{"pages": ["page.jpg"]}],
    }
    block = efd.category_prices({"screen": {"positions": [priced, unpriceable]}}, media, {})
    cards = {row["category"]: row for row in block["categories"]}

    assert list(cards) == [row["category"] for row in efd.tracked_categories()]
    assert block["positions"] == 2 and block["rows_without_a_unit_price"] == 1

    assert cards["ice-cream"]["positions"] == 1 and cards["ice-cream"]["bases"] == []
    assert cards["yogurt"]["positions"] == 1
    assert [basis["n"] for basis in cards["yogurt"]["bases"]] == [1]
    assert cards["yogurt"]["bases"][0]["median"] == efd.unit_price(priced)[1]

    empty = [row for row in block["categories"] if row["positions"] == 0]
    assert empty and all(row["bases"] == [] for row in empty)
