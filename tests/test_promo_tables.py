"""S6 — the six promo tables, and the one rule that makes `make tick` idempotent.

Every table already in `aggregates.SCHEMA` carries `window_id` in its PRIMARY KEY. These six do not,
and that is the ruling (`docs/reviews/2026-08-30-plan-promo-pulse-1.md` SP-5, amendment 4): week is
derived from the thread root's post date at query time, because a thread that cools across a tick
boundary would otherwise get a SECOND identity on the second tick and K10 would go red on a store
nobody touched. `rollup` is the exception — a rollup IS a per-week fact — and both halves are
asserted here rather than described in a comment.
"""

import sqlite3
import sys
import unicodedata
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse import aggregates  # noqa: E402

WITHOUT_WINDOW = ("attribution", "signal", "evidence", "digest", "unsure")


@pytest.fixture
def conn():
    return aggregates.connect(":memory:")


def primary_key(conn, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [name for _, name, _, _, _, pk in rows if pk]


def columns(conn, table: str) -> list[str]:
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]


def test_all_six_tables_exist_and_the_list_is_the_one_K10_counts(conn):
    """K10 counts per table, and a table missing from `PROMO_TABLES` is one nothing counts."""
    live = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    }
    assert set(aggregates.PROMO_TABLES) <= live
    assert set(aggregates.PROMO_TABLES) == {*WITHOUT_WINDOW, "rollup"}
    assert "unsure" in aggregates.PROMO_TABLES, "the abstention path is counted like the rest"


def test_window_id_is_in_no_identity_but_rollups_week(conn):
    """The amendment, both directions. `window_id` is not even a COLUMN on the five: a column
    nothing keys on would still invite a join that re-introduces the second identity."""
    for table in WITHOUT_WINDOW:
        assert "window_id" not in columns(conn, table), table
        assert primary_key(conn, table) == [f"{table}_id"], table
    assert "window_id" not in columns(conn, "rollup")
    assert primary_key(conn, "rollup") == ["rollup_id"]
    assert {"week", "chain", "brand", "metric"} <= set(columns(conn, "rollup"))
    # and every table that was here BEFORE still keys on it — the departure is these six only
    assert "window_id" in primary_key(conn, "positions")
    assert "window_id" in primary_key(conn, "comments")


def test_the_id_is_uuid5_over_a_normalised_key_and_is_stable(conn):
    """Deterministic ids are what make the tick idempotent — SPEC v2 S4's «uuid5 over normalised
    keys». Asserted against a hand-built uuid5 rather than against itself, so a changed namespace
    fails here instead of silently renaming every row in the next tick."""
    key = aggregates.promo_key("@VARUS_channel", "4519", "цена")
    assert key == "@varus_channel\x1f4519\x1fцена"
    assert aggregates.promo_id("@VARUS_channel", "4519", "цена") == str(
        uuid.uuid5(aggregates.NAMESPACE, key)
    )
    assert aggregates.NAMESPACE == uuid.uuid5(
        uuid.NAMESPACE_URL, "market-pulse-llm/promo-pulse-1"
    )


def test_the_key_folds_case_and_whitespace_and_normalises_to_NFC():
    """One surface form, one id. «Йогурт» is the same word to a reader in either normalisation and
    two different ids to a database that never normalised — «й» is the letter that decomposes, and
    «Молокія» is not, which is why the brand names in this repo cannot carry this check."""
    assert aggregates.promo_key("  Молокія   ", "X") == aggregates.promo_key("молокія", "x")
    composed = unicodedata.normalize("NFC", "Йогурт")
    decomposed = unicodedata.normalize("NFD", "Йогурт")
    assert composed != decomposed, "the premise: this word really does have two spellings"
    assert aggregates.promo_id(composed) == aggregates.promo_id(decomposed)


def test_the_unit_separator_is_what_keeps_two_tuples_apart():
    """A `|` join collapses the moment a subject name contains a pipe, and a collapsed key is two
    different facts wearing one id. `\\x1f` cannot appear in a handle, a msg_id or a surface form."""
    assert aggregates.promo_id("a|b", "c") != aggregates.promo_id("a", "b|c")
    assert aggregates.promo_key("a", "b") == "a\x1fb"


def test_subject_id_is_over_the_type_and_the_name_and_refuses_an_unknown_type():
    """Amendment (2). The carrier is a pure function and not a `subject` table — `attribution`
    already carries the type and the surface form — so the closed list has to be enforced HERE or
    nowhere."""
    assert aggregates.subject_id("brand", "Яготинське") == aggregates.promo_id(
        "brand", "Яготинське"
    )
    assert aggregates.subject_id("brand", "АТБ") != aggregates.subject_id("chain", "АТБ")
    with pytest.raises(ValueError, match="unknown subject_type"):
        aggregates.subject_id("person", "хтось")


def test_two_complaints_in_one_thread_about_different_subjects_do_not_collapse(conn):
    """Amendment (1), which is why `signal`'s key grew `subject_id`. Driven through the table, not
    through the id function: the claim is that the DATABASE keeps them apart."""
    rows = [
        (
            aggregates.promo_id("@VARUS_channel", "4519", "жалоба", subject),
            "@VARUS_channel",
            4519,
            "жалоба",
            subject,
            0.9,
            "v1",
        )
        for subject in (
            aggregates.subject_id("brand", "Яготинське"),
            aggregates.subject_id("brand", "Молокія"),
        )
    ]
    conn.executemany(
        "INSERT INTO signal (signal_id, channel, thread_root, type, subject_id, confidence,"
        " extractor_version) VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    assert conn.execute("SELECT count(*) FROM signal").fetchone()[0] == 2
    with pytest.raises(sqlite3.IntegrityError):
        conn.executemany(
            "INSERT INTO signal (signal_id, channel, thread_root, type, subject_id, confidence,"
            " extractor_version) VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows[:1],
        )


def test_the_digest_holds_the_state_the_late_comment_delta_reads(conn):
    """Amendment (3): the delta reads digest + delta, so the digest has to carry what it covered."""
    assert {
        "version",
        "text",
        "children_ids",
        "supporting_signal_ids",
        "covers_up_to_msg_id",
        "cooled_at",
    } <= set(columns(conn, "digest"))


def test_the_unsure_row_carries_its_candidates_and_its_reason(conn):
    """SPEC v2 §4 (в), amendment (5): a class the codebook lacks is a ROW, never a silent drop."""
    assert {"channel", "msg_id", "candidates", "reason"} <= set(columns(conn, "unsure"))
    conn.execute(
        "INSERT INTO unsure (unsure_id, channel, msg_id, candidates, reason) VALUES (?, ?, ?, ?, ?)",
        (aggregates.promo_id("@msuaaaa", "1", "no such class"), "@msuaaaa", 1, "[]", "no such class"),
    )
    assert conn.execute("SELECT count(*) FROM unsure").fetchone()[0] == 1


def test_the_closed_vocabularies_are_closed(conn):
    assert aggregates.SUBJECT_TYPES == ("chain", "brand", "sku", "post")
    assert aggregates.SIGNAL_TYPES == ("жалоба", "похвала", "спрос", "привычка", "цена")
    assert aggregates.ATTRIBUTION_SOURCES == ("explicit", "reply_context", "post_context")


def test_positions_is_untouched(conn):
    """The plan says so and the schema has to be able to prove it: C2 is a POPULATION change."""
    assert primary_key(conn, "positions") == ["window_id", "row_id"]
    assert "brand_raw" in columns(conn, "positions") and "price_old" in columns(conn, "positions")
