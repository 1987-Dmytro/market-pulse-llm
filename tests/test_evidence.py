"""The evidence table of SPEC 3.18 (6) — the one place that names what the sitting is built from."""

import itertools

import pytest

from market_pulse import evidence, positions, prompts

TASK = prompts.REVISIONS["v4"]["T1"]


def a_row(kind="comment", **extra):
    return evidence.record(
        kind,
        channel="@VARUS_channel",
        msg_id=7,
        parent_msg_id=3,
        task=TASK,
        model_revision=None,
        served_by="<stub>",
        rendering=[{"role": "user", "content": "…"}],
        reply={"content": "{}", "finish_reason": "stop"},
        **extra,
    )


def a_position(**over):
    fields = {
        "brand_id": "rud",
        "brand_raw": "Рудь",
        "line": None,
        "category": None,
        "size_value": None,
        "size_unit": None,
        "pack_count": None,
        "attribute_pct": None,
        "price_promo": None,
        "price_old": None,
        "discount_pct_printed": None,
        "discount_footnote": False,
        "price_qualifier": None,
        "price_origin": "retail_leaflet",
        "carrier": "leaflet_page",
        "extraction_source": "positions_post_gm4",
    }
    return positions.Position(**(fields | over))


# --- the table is the authority, and it is read whole ------------------------------------------


def test_a_complete_comment_row_carries_every_required_field():
    row = a_row()
    assert evidence.missing(row) == []
    assert set(evidence.REQUIRED) <= set(row)


def test_the_prompt_sha_is_derived_from_the_task_and_cannot_be_passed_in():
    """Two instrument fields that could disagree is provenance nobody can check."""
    assert a_row()["prompt_sha256"] == prompts.prompt_sha256(TASK)
    with pytest.raises(ValueError, match="cannot be handed in"):
        a_row(prompt_sha256="deadbeef")


@pytest.mark.parametrize("field", evidence.REQUIRED)
def test_deleting_any_required_field_is_refused_by_name(field):
    """The negative control for the whole table: every field is load-bearing, one at a time."""
    row = a_row()
    del row[field]
    with pytest.raises(ValueError, match="3.18 \\(6\\)" if field != "row_kind" else "row_kind"):
        evidence.assert_complete(row)
    assert evidence.missing(row) == [field]


def test_a_field_that_is_present_and_none_satisfies_the_table():
    """Presence, not truthiness. `model_revision` has no answer at $0 and `parent_msg_id` is
    legitimately None for a leaflet page — an absent key and a null one are different states."""
    row = a_row()
    assert row["model_revision"] is None, "the $0 value of a field nothing can answer yet"
    row["parent_msg_id"] = None
    assert evidence.assert_complete(row) is row


def test_a_kind_the_table_does_not_know_is_refused():
    with pytest.raises(ValueError, match="row_kind"):
        a_row(kind="whatever")
    assert evidence.missing({"row_kind": "whatever"}) == ["row_kind"]


def test_the_kinds_are_enumerated_literally_and_every_one_has_a_row_in_the_table():
    """A fifth kind is a change to what the 3.18 (6) sitting is shown, so it may not land quietly.

    Nothing here asserted the MEMBERSHIP of `KINDS` until the fourth one arrived — `post_text` was
    added and the whole suite stayed green, which is exactly the shape this file exists to refuse.
    The literal below is the amendment's cost: adding a kind costs one line here and a reader.
    """
    assert evidence.KINDS == ("comment", "leaflet_page", "position_row", "post_text")
    assert set(evidence.KIND_FIELDS) == set(evidence.KINDS), (
        "a kind the table does not know is a refusal, so every kind needs its row — an empty tuple"
        " is how a kind says it carries nothing of its own"
    )


def test_a_post_text_row_carries_nothing_beyond_the_required_table():
    """The `comment` shape: the post's text IS its `rendering`, so there is no second artifact to
    name. What the marker adds rides in `extra` and the table does not require it."""
    assert evidence.KIND_FIELDS["post_text"] == ()
    assert evidence.missing(a_row(kind="post_text")) == []
    marker = a_row(kind="post_text", n_positions=None, unreadable="unparseable JSON")
    assert (marker["n_positions"], marker["unreadable"]) == (None, "unparseable JSON")


def test_a_leaflet_page_row_needs_its_image_and_sha():
    with pytest.raises(ValueError, match="image_path"):
        a_row(kind="leaflet_page")
    assert evidence.missing(a_row(kind="leaflet_page", image_path="p.jpg", image_sha256="ab")) == []


def test_a_position_row_needs_the_ladder_inputs_and_the_warnings():
    """Dv232 is in this tuple: `warnings` is a REQUIRED field of a position row, so a writer that
    computes them and drops them cannot produce a showable record."""
    assert set(evidence.KIND_FIELDS["position_row"]) == {"presence", "tier", "warnings"}
    with pytest.raises(ValueError, match="warnings"):
        a_row(kind="position_row", presence={}, tier="position")


# --- presence: a second implementation, held to the ladder's own -------------------------------


def test_the_presence_keys_are_the_ladders_own_field_names():
    assert tuple(evidence.presence(a_position())) == positions.PRESENCE_FIELDS


@pytest.mark.parametrize("combo", itertools.product((False, True), repeat=4))
def test_the_presence_fields_re_derive_the_ladders_own_tier(combo):
    """`evidence.presence` maps a Position to the five booleans and `positions.tier_from_presence`
    maps those back to a rung. `src/market_pulse/positions.py` is pinned by sha inside
    `results/sku_pilot_prereg_b2.json`, so the mapping could not be added there and lives beside it
    — which makes it a SECOND implementation of the ladder's inputs. This is what stops it drifting:
    across all 16 combinations the re-derived rung is the position's own.

    A drift would be invisible in the record and fatal at the sitting: 3.18 (6) asks the operator to
    see, field by field, what made a row a position rather than a product_mention, and the fields
    shown would no longer produce the tier shown beside them.
    """
    line, category, size, attribute = combo
    position = a_position(
        line="морозиво" if line else None,
        category="ice-cream" if category else None,
        size_value=450.0 if size else None,
        size_unit="г" if size else None,
        attribute_pct=12.0 if attribute else None,
    )
    assert positions.tier_from_presence(**evidence.presence(position)) == position.tier()


def test_presence_reads_a_raw_brand_as_a_brand():
    """`brand_id or brand_raw` — a name that did not resolve to the watchlist is still a brand, and
    every rung of the ladder starts at one."""
    assert evidence.presence(a_position(brand_id=None))["brand"] is True
