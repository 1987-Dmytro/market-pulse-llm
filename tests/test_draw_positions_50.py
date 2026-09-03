"""K5 — the S1 draw: 50 positions, seed 42, stratified by chain, two runs one sha.

The one thing a test can hold that the live run cannot: the ≥3-chain rule in BOTH directions. The
live population happens to span eight chains, so a refusal that never fires there would read as
«passed» ([[guard_selftest_negative_control]]).
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import draw_positions_50 as draw  # noqa: E402

from market_pulse import aggregates  # noqa: E402


def database(tmp_path: Path, chains: dict[str, int]) -> Path:
    """A pulse.db carrying `chains` = {source_id: how many positions}."""
    path = tmp_path / "pulse.db"
    conn = aggregates.connect(path)
    conn.execute(
        "INSERT INTO windows (window_id, anchor, days, since, until, bought, payable, text_less,"
        " leaflet_pages, post_texts, registry_channels)"
        " VALUES ('w1', '2026-08-31', 28, '2026-08-03', '2026-08-31', 0, 0, 0, 0, 0, 1)"
    )
    msg_id = 1000
    for source_id, count in chains.items():
        channel = f"@{source_id}"
        conn.execute(
            "INSERT INTO channels (window_id, channel, source_id, source_type, segment)"
            " VALUES ('w1', ?, ?, 'channel', 'retail')",
            (channel, source_id),
        )
        for n in range(count):
            msg_id += 1
            conn.execute(
                "INSERT INTO positions (window_id, row_id, channel, carrier, msg_id, ordinal,"
                " tier, price_promo, discount_pct_printed, depth, presence_brand, presence_line,"
                " presence_category, presence_size, presence_attribute, brand_raw, line,"
                " size_value, size_unit)"
                " VALUES ('w1', ?, ?, 'leaflet_page', ?, 0, 'position', ?, 20.0, 0.2, 1, 1, 0, 1,"
                " 0, ?, 'Лінія', 500, 'г')",
                (f"{channel}:{msg_id}:0", channel, msg_id, 10.0 + n, f"Бренд-{source_id}"),
            )
    conn.commit()
    conn.close()
    return path


FIXTURE_WINDOW = "w1"
"""The window :func:`database` writes its rows into — the one every assertion below is about."""


def run(db: Path, tmp_path: Path, name: str, rows: int = 50) -> tuple[int, Path, Path]:
    out, pred = tmp_path / f"{name}.json", tmp_path / f"{name}.jsonl"
    code = draw.main(
        # `--window` is NAMED and not inherited: `database()` above builds `w1`, the script's
        # default moved to the C2 window `w2`, and a fixture that rides a production default is a
        # test about whichever window production happens to draw ([[a_moved_constant_fails_green]]).
        ["--db", str(db), "--out", str(out), "--predicted", str(pred), "--rows", str(rows),
         "--window", FIXTURE_WINDOW]
    )
    return code, out, pred


def test_fifty_rows_seed_42_and_two_runs_are_one_sha(tmp_path):
    db = database(tmp_path, {"atb": 100, "varus": 20, "silpo": 10})
    code, first, first_pred = run(db, tmp_path, "a")
    assert code == 0
    _, second, second_pred = run(db, tmp_path, "b")
    assert first.read_bytes() == second.read_bytes()
    assert first_pred.read_bytes() == second_pred.read_bytes()

    record = json.loads(first.read_text(encoding="utf-8"))
    assert record["seed"] == 42
    assert record["rows_drawn"] == 50
    assert len({row["row_id"] for row in record["rows"]}) == 50, "no row drawn twice"


def test_every_chain_with_rows_reaches_the_draw(tmp_path):
    """Proportional, but never at the cost of losing a small chain entirely: 10 of 130 rows would
    round to 4, and 2 of 130 would round to 1 rather than to 0."""
    db = database(tmp_path, {"atb": 100, "varus": 20, "silpo": 10, "novus": 2})
    _, out, _ = run(db, tmp_path, "a")
    record = json.loads(out.read_text(encoding="utf-8"))
    assert set(record["by_chain"]) == {"atb", "varus", "silpo", "novus"}
    assert all(count >= 1 for count in record["by_chain"].values())


def test_fewer_than_three_chains_is_a_refusal(tmp_path, capsys):
    """The direction the live population cannot exercise — it spans eight chains."""
    db = database(tmp_path, {"atb": 100, "varus": 20})
    code, _, _ = run(db, tmp_path, "a")
    assert code == 1
    assert "at least 3" in capsys.readouterr().err


def test_three_chains_is_accepted(tmp_path):
    """…and its negative control: a guard that refused everything would pass the test above."""
    db = database(tmp_path, {"atb": 100, "varus": 20, "silpo": 10})
    code, _, _ = run(db, tmp_path, "a")
    assert code == 0


def test_the_labeller_never_sees_the_extraction_he_is_grading(tmp_path):
    """Two files, and the split is the point: the draw carries the carrier and its link, the
    predicted file carries brand/product/volume/price. One file with both would show the labeller
    the answer."""
    db = database(tmp_path, {"atb": 100, "varus": 20, "silpo": 10})
    _, out, pred = run(db, tmp_path, "a")
    record = json.loads(out.read_text(encoding="utf-8"))
    for row in record["rows"]:
        # `image` joined the closed list by ruling 03.09 (b) — Dv [cause: ruling]. It is a POINTER
        # to the page the labeller reads, never an extraction, and the list stays closed so the
        # next field has to be argued for too ([[guard_list_closed_by_its_anchor]]).
        assert set(row) == {
            "row_id", "chain", "carrier", "channel", "msg_id", "week", "link", "image"
        }
    predicted = [json.loads(line) for line in pred.read_text(encoding="utf-8").splitlines()]
    # The gold is PAGE-level (same ruling), so the predicted set is every extracted row of the pages
    # the draw came from — a superset of the 50, never a subset: a drawn row missing from it could
    # not be matched at all.
    assert len(predicted) >= len(record["rows"])
    assert {row["row_id"] for row in record["rows"]} <= {row["row_id"] for row in predicted}
    assert all("price_promo" in row and "brand" in row for row in predicted)
    assert not any(key in row for row in record["rows"] for key in ("price_promo", "brand"))


def test_the_record_names_the_population_it_was_actually_drawn_from(tmp_path):
    """A draw that did not SAY which population it came from would be labelled off the wrong rows.

    Re-scoped from `test_the_record_says_its_population_is_not_yet_the_one_K5_names`, Dv [cause:
    ruling] — that test pinned the LITERAL «PRE-C2», which was true only while C2 was unbought. S4
    bought it, ruling 03.09 (b) makes this the file the team lead labels, and a test that pins a
    moment goes on asserting it after the moment passes ([[a_reading_that_outlived_its_state]]).
    What the record has to do is name the window it read, so that is what is asserted — of BOTH
    windows, so neither answer can be hard-coded.
    """
    db = database(tmp_path, {"atb": 100, "varus": 20, "silpo": 10})
    _, out, _ = run(db, tmp_path, "a")
    record = json.loads(out.read_text(encoding="utf-8"))

    assert record["population_state"] == draw.population_state(FIXTURE_WINDOW)
    assert record["population_state"].startswith("5c2")
    assert draw.population_state("w2").startswith("C2")
    with pytest.raises(SystemExit):
        draw.population_state("w3")


def test_a_missing_store_is_a_non_zero_exit(tmp_path, capsys):
    code, _, _ = run(tmp_path / "gone.db", tmp_path, "a")
    assert code == 1
    assert "no store" in capsys.readouterr().err


@pytest.mark.parametrize("want", (10, 50))
def test_the_draw_is_never_short_when_the_population_is_large_enough(tmp_path, want):
    db = database(tmp_path, {"atb": 100, "varus": 20, "silpo": 10})
    _, out, _ = run(db, tmp_path, f"a{want}", rows=want)
    assert json.loads(out.read_text(encoding="utf-8"))["rows_drawn"] == want
