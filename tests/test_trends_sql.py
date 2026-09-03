"""K9 — S3's trends: recomputed twice identical, and an empty week ABSENT rather than zero.

Both assertions are about the same failure: a screen that renders a week nobody promoted in as a
number. The customer reads a flat zero as a price collapse, and the phase's question is «неделя за
неделей» — so the weeks that are missing carry as much meaning as the weeks that are there.
"""

import sqlite3

import pytest

from market_pulse import aggregates, trends

WINDOW = "w-test"
CHAIN = "@chain"


def position(row_id, msg_id, *, brand="Яготинське", price=52.9, depth=0.2, size=900.0,
             carrier="leaflet_page"):
    """One `positions` row in `add_positions`'s shape — the producer's, never a hand-built tuple
    ([[a_fixture_on_disk_pins_yesterdays_schema]])."""
    return {
        "row_id": row_id,
        "channel": CHAIN,
        "msg_id": msg_id,
        "ordinal": 0,
        "tier": "tracked",
        "warnings": [],
        "presence": dict.fromkeys(aggregates.PRESENCE, True),
        "position": {
            "carrier": carrier,
            "brand_id": "yagotynske",
            "category": "dairy",
            "price_promo": price,
            "price_old": 65.0,
            "discount_pct_printed": 20,
            "discount_footnote": False,
            "price_qualifier": None,
            "depth": depth,
            "depth_disagrees_with_printed": False,
            "brand_raw": brand,
            "line": "Молоко",
            "size_value": size,
            "size_unit": "ml",
            "pack_count": 1,
            "attribute_pct": 2.5,
        },
    }


@pytest.fixture
def db(tmp_path):
    conn = aggregates.connect(tmp_path / "pulse.db")
    conn.execute(
        "INSERT INTO windows VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (WINDOW, "2026-08-31", 28, "2026-08-03", "2026-08-31", 0, 0, 0, 0, 0, 0),
    )
    return conn


# --- recomputed twice, identical -----------------------------------------------------------------


def test_the_trends_recompute_to_the_same_reading(db):
    """Nothing in the aggregation may depend on row order, dict order or a clock. `GROUP BY` with
    no `ORDER BY` returns rows in whatever order the planner picks, which is stable today and is
    not a promise — so the statement orders, and this is what says so."""
    weeks = {(CHAIN, 1): "2026-W32", (CHAIN, 2): "2026-W32", (CHAIN, 3): "2026-W34"}
    aggregates.add_positions(
        db, WINDOW, [position("a", 1), position("b", 2, price=49.9), position("c", 3)]
    )
    first = trends.build(db, WINDOW, weeks)
    second = trends.build(db, WINDOW, weeks)
    assert first == second
    assert first["weeks"] == ["2026-W32", "2026-W34"]


def test_the_same_sku_in_one_week_is_one_row_with_its_spread(db):
    """Two promos of the same SKU in one week are one trend point, not two — otherwise «price per
    SKU per week» has two prices and the screen has to pick one without saying which."""
    weeks = {(CHAIN, 1): "2026-W32", (CHAIN, 2): "2026-W32"}
    aggregates.add_positions(
        db, WINDOW, [position("a", 1, price=52.9), position("b", 2, price=49.9)]
    )
    rows = trends.build(db, WINDOW, weeks)["sku_price_by_week"]["2026-W32"]
    assert len(rows) == 1
    assert rows[0]["n"] == 2
    assert (rows[0]["price_min"], rows[0]["price_max"]) == (49.9, 52.9)


def test_two_sizes_of_one_brand_are_two_skus(db):
    """The other direction: the SKU key is brand+line+size, so 900 ml and 2 l do not average into
    a price nothing is sold at."""
    weeks = {(CHAIN, 1): "2026-W32", (CHAIN, 2): "2026-W32"}
    aggregates.add_positions(
        db, WINDOW, [position("a", 1, size=900.0), position("b", 2, size=2000.0)]
    )
    assert len(trends.build(db, WINDOW, weeks)["sku_price_by_week"]["2026-W32"]) == 2


# --- an empty week is absent, never zero ---------------------------------------------------------


def test_a_week_with_no_positions_is_absent_and_not_a_zero(db):
    """W33 sits BETWEEN two weeks that have data, so it cannot be dismissed as "outside the
    range". It must not appear at all — not as `[]`, not as a row with `price 0`, not as `n: 0`."""
    weeks = {(CHAIN, 1): "2026-W32", (CHAIN, 2): "2026-W34"}
    aggregates.add_positions(db, WINDOW, [position("a", 1), position("b", 2)])
    built = trends.build(db, WINDOW, weeks)
    assert "2026-W33" not in built["sku_price_by_week"]
    assert "2026-W33" not in built["depth_by_week"]
    assert "2026-W33" not in built["weeks"]
    assert all(row["n"] > 0 for rows in built["sku_price_by_week"].values() for row in rows)


def test_the_weeks_that_do_have_data_are_present_with_their_rows(db):
    """The negative control for the assertion above: a reading that dropped EVERY week would pass
    «W33 is absent» and say nothing ([[guard_selftest_negative_control]])."""
    weeks = {(CHAIN, 1): "2026-W32", (CHAIN, 2): "2026-W34"}
    aggregates.add_positions(db, WINDOW, [position("a", 1), position("b", 2)])
    built = trends.build(db, WINDOW, weeks)
    assert sorted(built["sku_price_by_week"]) == ["2026-W32", "2026-W34"]
    assert built["sku_rows"] == 2


def test_a_position_whose_post_is_not_in_the_store_is_dropped_not_bucketed(db):
    """`week_of` returns NULL for a post the store does not have. Bucketing it under any week —
    the window's first, "unknown" — would put a price in a week it was never promoted in."""
    aggregates.add_positions(db, WINDOW, [position("a", 1), position("b", 99)])
    built = trends.build(db, WINDOW, {(CHAIN, 1): "2026-W32"})
    assert built["sku_rows"] == 1
    assert list(built["sku_price_by_week"]) == ["2026-W32"]


# --- depth is a window aggregate, never a row's own number ---------------------------------------


def test_depth_is_read_per_chain_and_brand_and_carries_no_promo_price(db):
    """SPEC 3.22 (1): depth per chain and brand is a window aggregate, and 3.21 (4) keeps the old
    price off any surface. A depth row beside its own `price_promo` would let a reader recover the
    old price by `promo / (1 - depth)`, so the depth query returns no price column at all."""
    weeks = {(CHAIN, 1): "2026-W32"}
    aggregates.add_positions(db, WINDOW, [position("a", 1, depth=0.25)])
    row = trends.build(db, WINDOW, weeks)["depth_by_week"]["2026-W32"][0]
    assert row["depth_mean"] == 0.25
    assert "price_promo" not in row and "price_old" not in row


def test_the_iso_week_label_sorts_across_a_year_boundary():
    """`%G-W%V` and not `%Y-W%U`: week 1 of 2027 must sort after week 52 of 2026, and the ISO year
    is not always the calendar year on those days."""
    assert trends.iso_week("2026-12-28T10:00:00+00:00") < trends.iso_week(
        "2027-01-04T10:00:00+00:00"
    )
    assert trends.iso_week("2026-08-05T10:00:00+00:00") == "2026-W32"


def test_the_store_reader_finds_a_real_post_and_labels_its_week(tmp_path):
    """`post_weeks` is the one leg of this that touches disk. Driven on the store's own record
    shape rather than asserted from the shipped file, so it fails on a schema move."""
    root = tmp_path / "posts"
    root.mkdir()
    (root / "chain.jsonl").write_text(
        '{"channel": "@chain", "msg_id": 7, "date": "2026-08-05T10:00:00+00:00"}\n',
        encoding="utf-8",
    )
    assert trends.post_weeks((root,)) == {("@chain", 7): "2026-W32"}


def test_a_connection_with_no_bound_weeks_refuses_rather_than_returning_nothing(db):
    """`week_of` is bound by `bind_weeks`. A query run on a connection that never bound it must
    raise, not return zero rows — zero rows and "no promos this window" look identical
    ([[a_checker_whose_failure_is_silence]])."""
    aggregates.add_positions(db, WINDOW, [position("a", 1)])
    fresh = sqlite3.connect(":memory:")
    fresh.executescript(aggregates.SCHEMA)
    with pytest.raises(sqlite3.OperationalError, match="week_of"):
        trends.sku_trends(fresh, WINDOW)


# --- one message read by both legs is one reading, not two ---------------------------------------


def test_the_same_sku_off_one_message_is_counted_once_and_the_leaflet_wins(db):
    """Ruling 03.09 (b), fork 2. Two carriers may hold two genuine rows about one message — the
    C2 window has 7 such row_ids — and `positions` keeps both because both were paid for. A TREND
    must not count one promo twice: `n` of 2 for a single price, and that price weighted double in
    the mean, is a number about the collection and not about the market."""
    aggregates.add_positions(db, WINDOW, [
        position("@chain:1:0", 1, price=52.9),
        position("@chain:1:0", 1, price=48.0, carrier="post_text"),
    ])
    trends.bind_weeks(db, {(CHAIN, 1): "2026-W32"})

    rows = trends.sku_trends(db, WINDOW)
    assert len(rows) == 1 and rows[0]["n"] == 1
    assert rows[0]["price_min"] == rows[0]["price_max"] == rows[0]["price_mean"] == 52.9
    assert [row["n"] for row in trends.depth_trends(db, WINDOW)] == [1]


def test_two_different_skus_on_one_message_both_survive(db):
    """The negative control: the rule collapses a repeated READING, never two products. A dedupe
    keyed one field too short would quietly halve a leaflet page that lists two sizes."""
    aggregates.add_positions(db, WINDOW, [
        position("@chain:1:0", 1, size=900.0),
        position("@chain:1:1", 1, size=450.0, carrier="post_text"),
    ])
    trends.bind_weeks(db, {(CHAIN, 1): "2026-W32"})

    assert sorted(row["size_value"] for row in trends.sku_trends(db, WINDOW)) == [450.0, 900.0]


def test_the_preferred_carrier_is_the_leaflet_legs_own_string(db):
    """`trends` names the carrier without importing the collection loop, so the two are held against
    each other here — a rename on one side that missed the other would make the preference match
    nothing and silently fall back to the row_id tiebreak."""
    from market_pulse import loop

    assert trends.PREFERRED_CARRIER == loop.CARRIER

