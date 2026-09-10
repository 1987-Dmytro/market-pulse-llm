"""K13 — the product-truth gate's draw: 20 rows, seed 42, twice identical.

The gate itself is the operator's words and nothing here scores it. What a test CAN hold is that the
draw is reproducible, that it draws from the population it names, and that an empty reaction column
says which kind of empty it is — «still in the queue» is a claim about us, «no one commented» is a
claim about the market, and a blank cell would be read as the second
([[empty_field_hides_several_states]]).
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import draw_truth_20 as draw  # noqa: E402


def position(n: int) -> dict:
    return {
        "row_id": f"@atb:{4000 + n}:0",
        "brand": {"display": f"Бренд-{n}"},
        "item": {"line": f"Лінія-{n}", "size_value": 500.0, "size_unit": "г"},
        "chain": {"id": "atb", "named_by_amendment_3_20": True},
        "carrier": "leaflet_page",
        "tier": "position",
        "promo_price": 10.0 + n,
        "printed_pct": 20.0,
        "evidence": {"channel": "@atb", "msg_id": 4000 + n},
    }


def threads(read: list[str]) -> dict:
    """`screen.threads` in the shape `tick.threads_read` writes it — counts plus their evidence."""
    return {
        "population": 678,
        "not_collected": 12,
        "product_population": 666,
        "read": len(read),
        "queue": 666 - len(read),
        "read_threads": read,
        "from": "results/promo_threads_draw*.json :: population.by_channel",
    }


@pytest.fixture
def export(tmp_path):
    document = {
        "window_id": "w1",
        "screen": {
            "positions": [position(n) for n in range(50)],
            "feed": [
                {"channel": "@atb", "thread_root": 4003, "type": "цена", "msg_id": 900,
                 "quote": "дорого"}
            ],
            "threads": threads(["@atb/4003"]),
        },
    }
    path = tmp_path / "promo_screen_data.json"
    path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    return path


def record(export, tmp_path, name: str) -> dict:
    out = tmp_path / name
    assert draw.main(["--export", str(export), "--out", str(out), "--json"]) == 0
    return json.loads(out.read_text(encoding="utf-8"))


def test_twenty_rows_under_seed_42(export, tmp_path):
    drawn = record(export, tmp_path, "a.json")
    assert drawn["seed"] == 42
    assert drawn["rows_drawn"] == 20
    assert drawn["population"] == 50
    assert len({row["row_id"] for row in drawn["rows"]}) == 20, "no row is drawn twice"


def test_two_draws_over_one_export_are_identical(export, tmp_path):
    first = (tmp_path / "a.json", tmp_path / "b.json")
    draw.main(["--export", str(export), "--out", str(first[0]), "--json"])
    draw.main(["--export", str(export), "--out", str(first[1]), "--json"])
    assert first[0].read_bytes() == first[1].read_bytes()


def test_the_reaction_column_says_WHICH_nothing(export, tmp_path):
    """THREE states, not two: a thread still in the queue, a thread that was read and said nothing
    of the five kinds, and a thread with a reaction. The read thread is taken FROM the draw rather
    than guessed — which of the 50 rows seed 42 picks is `random.sample`'s business."""
    picked = record(export, tmp_path, "a.json")["rows"][0]["post"]
    document = json.loads(export.read_text(encoding="utf-8"))
    document["screen"]["feed"] = []
    document["screen"]["threads"] = threads([picked])
    export.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")

    again = record(export, tmp_path, "b.json")
    text = draw.render(again["rows"], document["screen"]["threads"])
    assert "read, and nothing the codebook names was said in it" in text, "the READ thread"
    assert "still in the queue" in text and "«no one commented»" in text, "the other 19"


def test_a_reaction_that_exists_is_carried_with_its_quote_and_msg_id(export, tmp_path):
    """The four columns §2 names — signal · quote · msg_id — reach the row they belong to.

    The thread the feed points at is taken FROM the draw rather than guessed: which of the 50 rows
    seed 42 picks is an implementation detail of `random.sample`, and a test that pinned it would
    fail the day the population changes for a reason that has nothing to do with this join.
    """
    drawn = record(export, tmp_path, "a.json")
    picked = drawn["rows"][0]
    document = json.loads(export.read_text(encoding="utf-8"))
    document["screen"]["feed"] = [
        {"channel": "@atb", "thread_root": int(picked["post"].split("/")[1]), "type": "цена",
         "msg_id": 900, "quote": "дорого"}
    ]
    export.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")

    again = record(export, tmp_path, "b.json")
    hit = [row for row in again["rows"] if row["row_id"] == picked["row_id"]]
    assert hit, "the draw is seeded, so the same row comes back"
    assert hit[0]["reactions"] == [{"signal": "цена", "quote": "дорого", "msg_id": 900}]
    assert "«дорого»" in draw.render(again["rows"], document["screen"]["threads"])


def test_a_short_population_is_a_short_draw_never_a_refusal(tmp_path):
    """145 positions are on disk today and the gate is meant to run on whatever the screen holds."""
    document = {
        "window_id": "w1",
        "screen": {"positions": [position(1)], "feed": [], "threads": threads([])},
    }
    path = tmp_path / "small.json"
    path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    drawn = record(path, tmp_path, "a.json")
    assert drawn["rows_drawn"] == 1


def test_a_missing_export_is_a_non_zero_exit(tmp_path, capsys):
    assert draw.main(["--export", str(tmp_path / "gone.json"), "--out", str(tmp_path / "o.json")]) == 1
    assert "gone.json" in capsys.readouterr().err


def test_the_gate_never_renders_a_price_the_screen_may_not_print(export, tmp_path):
    """SPEC 3.21 (4): a gate that asked the operator to bless the old price would be asking about a
    number he will never see on the screen again."""
    drawn = record(export, tmp_path, "a.json")
    assert not any("price_old" in row for row in drawn["rows"])
    assert "price_old" not in draw.render(drawn["rows"], drawn["threads"])
