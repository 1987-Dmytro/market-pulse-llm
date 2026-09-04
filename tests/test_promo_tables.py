"""S6 — the six promo tables, and the one rule that makes `make tick` idempotent.

Every table already in `aggregates.SCHEMA` carries `window_id` in its PRIMARY KEY. These six do not,
and that is the ruling (`docs/reviews/2026-08-30-plan-promo-pulse-1.md` SP-5, amendment 4): week is
derived from the thread root's post date at query time, because a thread that cools across a tick
boundary would otherwise get a SECOND identity on the second tick and K10 would go red on a store
nobody touched. `rollup` is the exception — a rollup IS a per-week fact — and both halves are
asserted here rather than described in a comment.
"""

import json
import sqlite3
import sys
import unicodedata
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse import aggregates, registry  # noqa: E402

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


def test_no_stored_row_id_moves_and_the_carrier_is_what_completes_the_key(conn):
    """Ruling 03.09 (b), fork 2 — re-scoped from `test_positions_is_untouched`, Dv [cause: ruling].

    The plan's claim was «C2 is a POPULATION change, the table is untouched», and the population is
    what broke it: 7 C2 posts were read by BOTH legs, and `row_id` is `channel:msg_id:ordinal`, an
    id the producer owns and that carries no carrier. Under a two-column key the second leg's row
    REPLACED the first — two paid readings, one stored. The ruling's answer is that the id does not
    move (a sealed export names those rows by it) and the carrier the table already stored joins the
    key. So what is asserted here is what the plan actually protects, and it is more than the old
    line said: the ids stay, the rows stay apart, and window 1's values are the shipped record's.
    """
    assert primary_key(conn, "positions") == ["window_id", "row_id", "carrier"]
    assert "brand_raw" in columns(conn, "positions") and "price_old" in columns(conn, "positions")

    # Every row_id the shipped w1 export names is `channel:msg_id:ordinal` — no carrier in it, which
    # is exactly why the key needs one. The record is committed, so this holds on a clean clone.
    shipped = json.loads((REPO_ROOT / "results" / "dashboard_data_w1.json").read_text("utf-8"))
    rows = shipped["promo"]["positions_table"]["rows"]
    assert len(rows) == 145
    carriers = {row["carrier"] for row in rows}
    for row in rows:
        channel, msg_id, ordinal = row["row_id"].rsplit(":", 2)
        assert channel.startswith("@") and msg_id.isdigit() and ordinal.isdigit(), row["row_id"]
        assert row["carrier"] not in row["row_id"], row["row_id"]
    assert carriers == {"leaflet_page", "post_text"}

    # and the reason, driven: one message read by both legs is two rows, not one overwriting the
    # other. Under the old key the second INSERT would have replaced the first and this would read 1.
    for carrier in sorted(carriers):
        conn.execute(
            "INSERT INTO positions (window_id, row_id, channel, carrier, msg_id, ordinal, tier,"
            " presence_brand, presence_line, presence_category, presence_size, presence_attribute)"
            " VALUES ('w2', '@ekomarket_shop:1465:0', '@ekomarket_shop', ?, 1465, 0, 'full',"
            " 0, 0, 0, 0, 0)",
            (carrier,),
        )
    stored = conn.execute(
        "SELECT carrier FROM positions WHERE row_id = '@ekomarket_shop:1465:0'"
    ).fetchall()
    assert sorted(one[0] for one in stored) == ["leaflet_page", "post_text"]


def test_a_chain_name_folds_to_the_chain_id_and_only_a_chain_row_does(tmp_path, monkeypatch):
    """Ruling 04.09 (j) item 1: «VARUS», «Varus» and «Варус» are ONE chain to every reader and
    three ids to a store that never folded them. The fold is on `chain` rows only — a `brand`
    called «АТБ» is not the retailer — which is why it lives in `chain_key` and not in `promo_key`,
    and why `promo_key` itself still answers exactly what it did before."""
    assert aggregates.chain_key("VARUS") == aggregates.chain_key("Варус") == "varus"
    assert aggregates.chain_key("Сільпо") == aggregates.chain_key("Silpo") == "silpo"
    assert aggregates.chain_key("McDonald’s") == "mcdonalds"
    # a name no chain claims is normalised and NOT invented into an id
    assert aggregates.chain_key("  Молокія ") == aggregates.promo_key("молокія") == "молокія"

    assert aggregates.subject_id("chain", "VARUS") == aggregates.subject_id("chain", "Варус")
    assert aggregates.subject_id("brand", "VARUS") != aggregates.subject_id("brand", "Варус"), (
        "a brand is not folded: two spellings of a trade mark are two surface forms, and the"
        " registry's chain names have nothing to say about them"
    )
    assert aggregates.subject_id("chain", "АТБ") != aggregates.subject_id("brand", "АТБ")


def test_one_spelling_may_name_only_one_chain(tmp_path, monkeypatch):
    """A dict built by iteration is last-wins, and last-wins here would hand one chain's comments
    another chain's id ([[select_one_row_refuse_ambiguity]]). Маркетопт is the live case: two
    registry rows, `marketopt_promo` and `marketopt_private`, are one chain — which is why the
    shipped file gives the spellings to one of them and says so."""
    bad = tmp_path / "chain_aliases.yaml"
    bad.write_text("marketopt_promo: [Маркетопт]\nmarketopt_private: [Маркетопт]\n", "utf-8")
    monkeypatch.setattr(registry, "CHAIN_ALIASES", bad)
    aggregates._chain_ids.cache_clear()
    with pytest.raises(ValueError, match="only one chain"):
        aggregates.chain_key("Маркетопт")

    # the negative control: the same loader accepts the SHIPPED file, so the refusal above is the
    # duplicate and not a loader that refuses everything ([[guard_selftest_negative_control]])
    monkeypatch.undo()
    aggregates._chain_ids.cache_clear()
    assert aggregates.chain_key("Маркетопт") == "marketopt_promo"
