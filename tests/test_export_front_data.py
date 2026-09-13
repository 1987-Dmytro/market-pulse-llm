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
