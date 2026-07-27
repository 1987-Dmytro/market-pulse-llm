"""Offline tests for the annotation sampling maths, row shapes and label checks."""

import copy
import random

from market_pulse.annotation import (
    COMMENT_LABELS,
    POST_LABELS,
    allocate,
    check_batch,
    comment_row,
    post_row,
    row_state,
    stratified_sample,
)

WATCHLIST = ("rud", "premia")

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


# --- validation -------------------------------------------------------------


def batch(kind: str, *labels: dict) -> tuple[list[dict], list[dict]]:
    """(rows, pristine) for as many rows as label sets were passed."""
    builder = comment_row if kind == "comments" else post_row
    source = RECORD if kind == "comments" else POST
    pristine = []
    for index in range(len(labels)):
        record = dict(source, msg_id=source["msg_id"] + index, text=f"text {index}")
        pristine.append(builder(record, "ua"))
    rows = [dict(copy.deepcopy(row), **label) for row, label in zip(pristine, labels)]
    return rows, pristine


CLEAN_COMMENT = {
    "sentiment": "negative",
    "sarcasm": True,
    "intents": ["price"],
    "annotator": "llm-precheck",
}
CLEAN_POST = {
    "relevant": True,
    "post_type": "promo",
    "brands": [{"brand_id": "rud", "mention": "Рудь"}],
    "annotator": "llm-precheck",
}


def violations(kind: str, *labels: dict) -> list[str]:
    rows, pristine = batch(kind, *labels)
    return check_batch(rows, pristine, kind, WATCHLIST).violations


def test_a_clean_batch_passes():
    assert violations("comments", CLEAN_COMMENT, CLEAN_COMMENT) == []
    assert violations("posts", CLEAN_POST) == []


def test_untouched_rows_are_progress_not_violations():
    # The batch is validated after every chunk, so most rows are still blank.
    rows, pristine = batch("comments", CLEAN_COMMENT, {})
    report = check_batch(rows, pristine, "comments", WATCHLIST)
    assert report.ok
    assert (report.stats["labeled"], report.stats["unlabeled"]) == (1, 1)


def test_a_half_labelled_row_is_caught():
    bad = violations("comments", {"sentiment": "negative", "annotator": "llm-precheck"})
    assert len(bad) == 1
    assert "half-labelled" in bad[0] and "sarcasm" in bad[0]
    assert row_state({"sentiment": "negative", "sarcasm": None, "annotator": None}, "comments") == (
        "partial"
    )


def test_illegal_values_name_the_field():
    bad = violations(
        "comments",
        dict(CLEAN_COMMENT, sentiment="mixed", sarcasm="yes", intents=["price", "delivery"]),
    )
    assert len(bad) == 3
    assert any("sentiment" in line for line in bad)
    assert any("sarcasm" in line for line in bad)
    assert any("delivery" in line for line in bad)


def test_repeated_intent_is_caught():
    bad = violations("comments", dict(CLEAN_COMMENT, intents=["price", "price"]))
    assert len(bad) == 1 and "duplicate" in bad[0]


def test_an_unclear_row_still_needs_legal_labels():
    # The guideline asks for the labels even on unclear rows; they are excluded
    # from the gates, not from the schema.
    assert violations("comments", dict(CLEAN_COMMENT, unclear=True)) == []
    bad = violations("comments", dict(CLEAN_COMMENT, unclear="yes"))
    assert len(bad) == 1 and "unclear" in bad[0]


def test_annotator_is_required():
    bad = violations("comments", dict(CLEAN_COMMENT, annotator="  "))
    assert len(bad) == 1 and "annotator" in bad[0]


def test_a_lost_row_is_caught():
    rows, pristine = batch("comments", CLEAN_COMMENT, CLEAN_COMMENT)
    bad = check_batch(rows[:1], pristine, "comments", WATCHLIST).violations
    assert len(bad) == 1 and "row lost" in bad[0]


def test_a_row_outside_the_pristine_copy_is_caught():
    rows, pristine = batch("comments", CLEAN_COMMENT, CLEAN_COMMENT)
    bad = check_batch(rows, pristine[:1], "comments", WATCHLIST).violations
    assert len(bad) == 1 and "not in the pristine copy" in bad[0]


def test_a_duplicated_row_is_caught():
    rows, pristine = batch("comments", CLEAN_COMMENT)
    bad = check_batch(rows * 2, pristine, "comments", WATCHLIST).violations
    assert len(bad) == 1 and "duplicate id" in bad[0]


def test_editing_the_text_being_labelled_is_caught():
    rows, pristine = batch("comments", CLEAN_COMMENT)
    rows[0]["text"] = "tidied up"
    bad = check_batch(rows, pristine, "comments", WATCHLIST).violations
    assert len(bad) == 1 and "record fields edited: text" in bad[0]


def test_post_type_is_required_even_for_an_irrelevant_post():
    bad = violations("posts", dict(CLEAN_POST, relevant=False, post_type=None, brands=[]))
    assert len(bad) == 1 and "half-labelled" in bad[0]


def test_an_invented_brand_id_is_caught():
    bad = violations("posts", dict(CLEAN_POST, brands=[{"brand_id": "rude", "mention": "Рудь"}]))
    assert len(bad) == 1 and "watchlist" in bad[0]


def test_an_off_watchlist_brand_is_legal_with_a_null_id():
    assert (
        violations("posts", dict(CLEAN_POST, brands=[{"brand_id": None, "mention": "Звени"}])) == []
    )


def test_a_brand_entry_needs_both_keys():
    bad = violations("posts", dict(CLEAN_POST, brands=[{"mention": "Рудь"}]))
    assert len(bad) == 1 and "brand_id and mention" in bad[0]


def test_stats_count_unclear_among_the_labelled():
    rows, pristine = batch(
        "comments",
        dict(CLEAN_COMMENT, unclear=True),
        CLEAN_COMMENT,
        dict(CLEAN_COMMENT, unclear=True),
    )
    stats = check_batch(rows, pristine, "comments", WATCHLIST).stats
    assert (stats["labeled"], stats["unclear"]) == (3, 2)
    assert stats["unclear_share"] == 2 / 3
    assert stats["dist"]["sentiment"]["negative"] == 3
    assert stats["dist"]["annotator"] == {"llm-precheck": 3}


# --- review sampling --------------------------------------------------------


def pool(count: int, start: int = 0, **fields) -> list[dict]:
    return [dict(id=f"@c:{index}", **fields) for index in range(start, start + count)]


def test_the_review_sample_is_spread_over_the_strata():
    rows = pool(60, 0, language="ua") + pool(30, 60, language="ru") + pool(10, 90, language="en")
    picked, table = stratified_sample(rows, lambda row: row["language"], 10, random.Random(42))

    assert len(picked) == 10
    assert {name: drawn for name, (_, drawn) in table.items()} == {"ua": 6, "ru": 3, "en": 1}
    assert table["ua"][0] == 60


def test_the_same_seed_draws_the_same_rows():
    rows = pool(50, 0, language="ua") + pool(50, 50, language="ru")
    first, _ = stratified_sample(rows, lambda row: row["language"], 20, random.Random(42))
    second, _ = stratified_sample(rows, lambda row: row["language"], 20, random.Random(42))
    assert [row["id"] for row in first] == [row["id"] for row in second]


def test_drawn_rows_are_distinct_rows_of_the_batch():
    rows = pool(40, 0, language="ua") + pool(40, 40, language="ru")
    picked, _ = stratified_sample(rows, lambda row: row["language"], 30, random.Random(42))
    ids = [row["id"] for row in picked]
    assert len(set(ids)) == 30
    assert set(ids) <= {row["id"] for row in rows}


def test_the_flagged_stratum_is_oversampled():
    # Equal pools of sarcastic and plain rows; the review budget goes to sarcasm.
    rows = pool(300, 0, sarcasm=True) + pool(300, 300, sarcasm=False)
    _, table = stratified_sample(
        rows,
        lambda row: row["sarcasm"],
        90,
        random.Random(42),
        weight_of=lambda name: 3 if name else 1,
    )
    sarcastic, plain = table[True][1], table[False][1]
    assert sarcastic + plain == 90
    assert sarcastic > 2.5 * plain


def test_a_scarce_stratum_is_lifted_but_never_overdrawn():
    # Only 5 sarcastic rows exist. The 3x weight pulls more of them in than their
    # share would give, cannot invent a sixth, and the sample stays at 90.
    rows = pool(5, 0, sarcasm=True) + pool(300, 5, sarcasm=False)
    draw = dict(rows=rows, key=lambda row: row["sarcasm"], total=90)
    picked, table = stratified_sample(
        **draw, rng=random.Random(42), weight_of=lambda name: 3 if name else 1
    )
    _, plain = stratified_sample(**draw, rng=random.Random(42))

    assert len(picked) == 90
    assert plain[True][1] < table[True][1] <= 5


def test_post_stats_separate_off_watchlist_from_absent_brands():
    rows, pristine = batch(
        "posts",
        CLEAN_POST,
        dict(CLEAN_POST, brands=[{"brand_id": None, "mention": "Звени гора"}]),
        dict(CLEAN_POST, relevant=False, post_type="other", brands=[]),
    )
    dist = check_batch(rows, pristine, "posts", WATCHLIST).stats["dist"]
    assert dist["brand_id"]["rud"] == 1
    assert dist["brand_id"]["(off-watchlist)"] == 1
    assert dist["brand_id"]["(no brands)"] == 1
    assert dist["post_type"] == {"promo": 2, "other": 1}
