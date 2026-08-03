"""The quiz rulings and the pattern they validated.

Three things are worth a test: the table that carries the authority is checked before it is
believed, the mechanical rule fires on exactly its four conjuncts, and a row the operator has
already ruled on is protected from the rule even when the rule would write something else.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import apply_quiz_rulings as quiz  # noqa: E402
import relabel_intents as relabel  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
TABLE = """# quiz

RESULT: 1/2 matches.

| # | id | arm | policy | operator | match |
|---|----|-----|--------|----------|-------|
| 1 | @c:1 | restore | ["taste"] | ["taste"] | yes |
| 2 | @c:2 | model | ["price"] | [] | no |
"""
SMALL = {"rows": 2, "matched": 1, "divergent": 1, "restore": 1, "model": 1}


@pytest.fixture
def aliases():
    return watchlist_aliases(load_registry(REPO_ROOT / "config" / "registry.yaml").watchlist)


def comment(msg_id, text, intents, parent=1):
    return {
        "id": f"@c:{msg_id}",
        "channel": "@c",
        "msg_id": msg_id,
        "parent_msg_id": parent,
        "language": "uk",
        "text": text,
        "sentiment": "neutral",
        "sarcasm": False,
        "intents": intents,
        "unclear": False,
        "annotator": "operator",
        "notes": "",
    }


def bench(tmp_path, rows, posts=((1, ""),), fixes=()):
    """A source file, its emptied `_tax2` copy, a drop record, a post store and a quiz table."""
    source = tmp_path / "comments_train.jsonl"
    source.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    staged = relabel.staged(source)
    staged.write_text(
        "".join(json.dumps({**row, "intents": []}, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    drop = tmp_path / "drop.json"
    lost: dict[str, int] = {}
    for row in rows:
        key = ", ".join(sorted(row["intents"]))
        lost[key] = lost.get(key, 0) + 1
    drop.write_text(
        json.dumps({"populations": {"all": {"emptied": len(rows), "emptied_from": lost}}}),
        encoding="utf-8",
    )
    record = tmp_path / "relabel.json"
    record.write_text(json.dumps({"runs": [], "fixes": list(fixes)}), encoding="utf-8")
    store = tmp_path / "posts"
    store.mkdir(exist_ok=True)
    (store / "c.jsonl").write_text(
        "".join(
            json.dumps({"channel": "@c", "msg_id": mid, "text": text}, ensure_ascii=False) + "\n"
            for mid, text in posts
        ),
        encoding="utf-8",
    )
    table = tmp_path / "quiz.md"
    table.write_text(TABLE, encoding="utf-8")
    return {
        "source": source,
        "staged": staged,
        "drop": drop,
        "record": record,
        "posts": store,
        "quiz": table,
    }


def run(tmp_path, paths, monkeypatch, extra=()):
    monkeypatch.setattr(relabel, "SOURCES", {"comments_train": paths["source"]})
    monkeypatch.setattr(quiz, "EXPECTED", SMALL)
    return quiz.main(
        [
            "--quiz",
            str(paths["quiz"]),
            "--record",
            str(tmp_path / "out.json"),
            "--relabel-record",
            str(paths["record"]),
            "--drop",
            str(paths["drop"]),
            "--posts",
            str(paths["posts"]),
            *extra,
        ]
    )


def staged_intents(path):
    return {row["id"]: row["intents"] for row in relabel.load(path)[0]}


def test_the_real_verdict_table_is_the_shape_it_declares():
    """The authority for every label this script writes, parsed rather than trusted."""
    rows = quiz.quiz_rows(REPO_ROOT / "docs" / "quiz-45g-verdicts.md")
    assert len(rows) == quiz.EXPECTED["rows"]
    assert sum(row["match"] for row in rows) == quiz.EXPECTED["matched"]
    assert all(row["match"] == (row["policy"] == row["operator"]) for row in rows)


def test_a_table_that_lost_a_row_is_refused(tmp_path, monkeypatch):
    """A formatting slip does not fail loudly — it parses into a smaller quiz."""
    table = tmp_path / "quiz.md"
    table.write_text("\n".join(TABLE.splitlines()[:-1]) + "\n", encoding="utf-8")
    monkeypatch.setattr(quiz, "EXPECTED", SMALL)
    with pytest.raises(SystemExit, match="declares"):
        quiz.quiz_rows(table)


def test_a_match_the_two_columns_do_not_support_is_refused(tmp_path, monkeypatch):
    table = tmp_path / "quiz.md"
    table.write_text(
        TABLE.replace('["price"] | [] | no', '["price"] | [] | yes').replace("1/2", "2/2"),
        encoding="utf-8",
    )
    monkeypatch.setattr(quiz, "EXPECTED", {**SMALL, "matched": 2, "divergent": 0})
    with pytest.raises(SystemExit, match="marked a match"):
        quiz.quiz_rows(table)


@pytest.mark.parametrize(
    "text,intents,post,fires",
    [
        ("З вишнею", ["taste"], "", True),
        ("З вишнею", ["taste", "price"], "", False),  # v1 was not `taste` alone
        ("а" * 80, ["taste"], "", False),  # not a short answer
        ("Гармонія", ["taste"], "", False),  # a watchlist brand, not a dish
        ("З вишнею", ["taste"], "Який смак вам більше?", False),  # the post has text
    ],
)
def test_the_pattern_fires_on_exactly_its_four_conjuncts(
    tmp_path, monkeypatch, aliases, text, intents, post, fires
):
    paths = bench(tmp_path, [comment(1, text, intents)], posts=((1, post),))
    monkeypatch.setattr(relabel, "SOURCES", {"comments_train": paths["source"]})
    emptied = quiz.population(paths["drop"], paths["record"])
    labelled = {row["id"]: row for row in relabel.load(paths["source"])[0]}
    from market_pulse import parents

    family = quiz.taste_family(emptied, labelled, parents.load(paths["posts"]), aliases)
    assert bool(family) is fires


def test_an_operator_ruling_survives_a_pattern_that_disagrees_with_it(tmp_path, monkeypatch):
    """The negative control: the hold has to protect a row whose value the rule would change.

    A rule that only ever writes what is already there would pass a hold test by writing
    nothing, which proves the value and not the guard.
    """
    rows = [comment(1, "З вишнею", ["taste"]), comment(2, "Полуниця", ["taste"])]
    paths = bench(
        tmp_path,
        rows,
        fixes=[
            {
                "applied_by": "scripts/apply_calibration_rulings.py",
                "rows": [{"id": "@c:2", "old": [], "new": ["quality"]}],
            }
        ],
    )
    # the ruling itself is in the staged file; the fix block is what makes it law
    staged = relabel.load(paths["staged"])
    lines = [
        json.dumps(
            {**row, "intents": ["quality"] if row["id"] == "@c:2" else []}, ensure_ascii=False
        )
        for row in staged[0]
    ]
    paths["staged"].write_text("".join(line + "\n" for line in lines), encoding="utf-8")

    assert run(tmp_path, paths, monkeypatch) == 0
    after = staged_intents(paths["staged"])
    assert after["@c:1"] == ["taste"], "the pattern closed the row it was validated for"
    assert after["@c:2"] == ["quality"], "an operator ruling is not overwritten by a pattern"
    written = json.loads((tmp_path / "out.json").read_text(encoding="utf-8"))["runs"][-1]
    assert [row["id"] for row in written["held"]] == ["@c:2"]


def test_a_second_run_does_not_read_its_own_fixes_back_as_a_ruling(tmp_path, monkeypatch):
    rows = [comment(1, "З вишнею", ["taste"]), comment(2, "Дорого", ["price"])]
    paths = bench(tmp_path, rows)
    assert run(tmp_path, paths, monkeypatch) == 0
    first = json.loads(paths["record"].read_text(encoding="utf-8"))["fixes"]
    assert len(first) == 1 and first[0]["applied_by"] == quiz.APPLIED_BY

    assert run(tmp_path, paths, monkeypatch) == 0
    again = json.loads(paths["record"].read_text(encoding="utf-8"))["fixes"]
    assert len(again) == 1, "a run that changes nothing writes no fix block"
    written = json.loads((tmp_path / "out.json").read_text(encoding="utf-8"))["runs"][-1]
    assert written["held"] == [], "its own writes are not somebody else's law"
    assert [row["id"] for row in written["unchanged"]] == ["@c:1"]


def test_only_the_intents_column_moves(tmp_path, monkeypatch):
    rows = [comment(1, "З вишнею", ["taste"]), comment(2, "Дорого", ["price"])]
    paths = bench(tmp_path, rows)
    before = relabel.load(paths["staged"])[1]
    assert run(tmp_path, paths, monkeypatch) == 0
    after = relabel.load(paths["staged"])[1]
    assert len(after) == len(before)
    restored = [
        json.dumps({**json.loads(line), "intents": []}, ensure_ascii=False) for line in after
    ]
    assert restored == before


def test_a_quiz_row_outside_the_population_stops_the_run(tmp_path, monkeypatch):
    paths = bench(tmp_path, [comment(9, "З вишнею", ["taste"]), comment(2, "Дорого", ["price"])])
    with pytest.raises(SystemExit, match="not in the 97"):
        run(tmp_path, paths, monkeypatch)
