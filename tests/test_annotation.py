"""Offline tests for the annotation sampling maths and the emitted row shapes."""

from market_pulse.annotation import (
    COMMENT_LABELS,
    POST_LABELS,
    allocate,
    comment_row,
    post_row,
)

RECORD = {
    "record_type": "comment",
    "source_id": "varus",
    "channel": "@VARUS_channel",
    "msg_id": 21720,
    "parent_msg_id": 10633,
    "date": "2026-07-27T09:05:50+00:00",
    "text": "Смачно!",
    "sender_anon_id": "dd56",
    "provenance": {"source_type": "official_retail", "comments_enabled": True},
}
POST = {
    "record_type": "post",
    "source_id": "varus",
    "channel": "@VARUS_channel",
    "msg_id": 10633,
    "date": "2026-07-26T09:00:00+00:00",
    "text": "Морозиво ТМ Рудь",
    "has_media": True,
    "grouped_id": None,
    "reply_count": 7,
    "provenance": {"source_type": "official_retail", "comments_enabled": True},
}


def test_allocation_is_proportional():
    quota = allocate({"a": 600, "b": 300, "c": 100}, 100)
    assert quota == {"a": 60, "b": 30, "c": 10}
    assert sum(quota.values()) == 100


def test_the_batch_is_always_filled_and_never_overdrawn():
    capacity = {"a": 600, "b": 300, "c": 5}
    for total in (1, 7, 100, 904, 905):
        quota = allocate(capacity, total)
        assert sum(quota.values()) == total
        assert all(quota[key] <= size for key, size in capacity.items())


def test_allocation_never_exceeds_the_corpus():
    quota = allocate({"a": 3, "b": 2}, 100)
    assert quota == {"a": 3, "b": 2}


def test_remainders_are_handed_out_deterministically():
    first = allocate({"a": 10, "b": 10, "c": 10}, 4)
    assert sum(first.values()) == 4
    assert first == allocate({"a": 10, "b": 10, "c": 10}, 4)


def test_more_strata_than_rows_still_fills_the_batch():
    quota = allocate({key: 100 for key in "abcdefgh"}, 3)
    assert sum(quota.values()) == 3


def test_weight_oversamples_a_pool():
    # Equal pools, weight 2 on the first: it draws twice as many rows.
    quota = allocate({True: 300, False: 300}, 90, weight={True: 2})
    assert quota == {True: 60, False: 30}


def test_oversampling_stops_at_what_exists():
    # A weight can ask for more rows than the pool holds — the cap binds and the
    # remainder goes to the other pool instead of shrinking the batch.
    quota = allocate({"hot": 5, "cold": 5}, 8, weight={"hot": 10})
    assert quota == {"hot": 5, "cold": 3}


def test_comment_row_matches_the_guideline_schema():
    row = comment_row(RECORD, "ua")

    assert set(COMMENT_LABELS) <= set(row)
    assert row["id"] == "@VARUS_channel:21720"
    assert (row["sentiment"], row["sarcasm"], row["intents"], row["unclear"]) == (
        None,
        None,
        [],
        False,
    )
    assert row["language"] == "ua"
    assert row["source_type"] == "official_retail"
    assert row["parent_msg_id"] == 10633
    # The pseudonym stays out of the annotator's view; it is not needed to label.
    assert "sender_anon_id" not in row


def test_post_row_matches_the_guideline_schema():
    row = post_row(POST, "ua")

    assert set(POST_LABELS) <= set(row)
    assert (row["relevant"], row["post_type"], row["brands"], row["unclear"]) == (
        None,
        None,
        [],
        False,
    )
    assert (row["has_media"], row["reply_count"]) == (True, 7)


def test_label_lists_are_not_shared_between_rows():
    first, second = comment_row(RECORD, "ua"), comment_row(RECORD, "ru")
    first["intents"].append("price")
    assert second["intents"] == []
