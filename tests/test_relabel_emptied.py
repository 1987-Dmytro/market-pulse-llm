"""Re-asking the rows the re-label emptied, with the post — and what must not move.

The risky part is not the request; it is that this script writes into files an accepted
gate already judged. So the tests are mostly about refusals: the population has to be the
one the record measured, an operator ruling has to survive a model that disagrees with it,
and a rewritten line has to differ from its predecessor in one value.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import relabel_emptied as emptied  # noqa: E402
import relabel_intents as relabel  # noqa: E402
from market_pulse import zero_shot  # noqa: E402


def row(row_id, parent, intents, text="Так", unclear=False, channel="@c"):
    return {
        "id": row_id,
        "channel": channel,
        "parent_msg_id": parent,
        "text": text,
        "intents": list(intents),
        "unclear": unclear,
    }


def corpus(tmp_path, before, after, posts=((1, "Новинка: сирок"),)):
    """Sources with the v1 labels, staged copies with the v2 ones, and the stored posts."""
    source = tmp_path / "comments.jsonl"
    source.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in before), encoding="utf-8"
    )
    relabel.staged(source).write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in after), encoding="utf-8"
    )
    store = tmp_path / "posts"
    store.mkdir()
    (store / "c.jsonl").write_text(
        "".join(
            json.dumps({"channel": "@c", "msg_id": mid, "text": text}, ensure_ascii=False) + "\n"
            for mid, text in posts
        ),
        encoding="utf-8",
    )
    return {"comments": source}, store


def records(tmp_path, emptied_rows, lost, fixes=()):
    drop = tmp_path / "drop.json"
    drop.write_text(
        json.dumps({"populations": {"all": {"emptied": emptied_rows, "emptied_from": lost}}}),
        encoding="utf-8",
    )
    run = tmp_path / "relabel.json"
    run.write_text(json.dumps({"runs": [], "fixes": list(fixes)}), encoding="utf-8")
    return drop, run


class Canned:
    """A client that answers from a table — the write path with no network and no spend."""

    def __init__(self, answers):
        self.answers = answers
        self.asked = []
        self.budget = zero_shot.Budget(1.0, 1.0)

    def __call__(self, text, parent):
        self.asked.append((text, parent))
        self.budget.add(0.0001)
        return self.answers[text]


def run(tmp_path, sources, store, drop, record, answers, **extra):
    original = relabel.SOURCES
    relabel.SOURCES = sources
    client = Canned(answers)
    try:
        argv = [
            "--drop",
            str(drop),
            "--relabel-record",
            str(record),
            "--posts",
            str(store),
            "--record",
            str(tmp_path / "out.json"),
            "--rows-out",
            str(tmp_path / "rows.jsonl"),
            "--concurrency",
            "1",
            *extra.pop("argv", []),
        ]
        assert emptied.main(argv, asker=client) == 0
    finally:
        relabel.SOURCES = original
    return client, json.loads((tmp_path / "out.json").read_text(encoding="utf-8"))["runs"][-1]


def staged_rows(sources):
    return {r["id"]: r for r in relabel.load(relabel.staged(sources["comments"]))[0]}


def test_the_population_must_be_the_one_the_record_measured(tmp_path):
    """A count that agrees by accident is why the lost-label distribution is checked too."""
    sources, store = corpus(
        tmp_path,
        [row("@c:1", 1, ["taste"]), row("@c:2", 1, ["price"])],
        [row("@c:1", 1, []), row("@c:2", 1, [])],
    )
    drop, record = records(tmp_path, 2, {"taste": 1, "quality": 1})
    original = relabel.SOURCES
    relabel.SOURCES = sources
    try:
        with pytest.raises(SystemExit, match="population and the record of it disagree"):
            emptied.population(drop, record)
    finally:
        relabel.SOURCES = original


def test_a_row_under_an_operator_ruling_is_asked_and_never_written(tmp_path):
    """The model may disagree with the operator; the operator wins and the answer is kept."""
    sources, store = corpus(
        tmp_path,
        [row("@c:1", 1, ["taste"], "ruled"), row("@c:2", 1, ["price"], "free")],
        [row("@c:1", 1, ["taste"], "ruled"), row("@c:2", 1, [], "free")],
    )
    # the staged label of @c:1 is an operator fix: the run itself produced []
    drop, record = records(
        tmp_path, 2, {"taste": 1, "price": 1}, fixes=[{"rows": [{"id": "@c:1", "old": []}]}]
    )
    client, out = run(
        tmp_path,
        sources,
        store,
        drop,
        record,
        {"ruled": '{"intents": []}', "free": '{"intents": ["price"]}'},
    )

    assert out["population"]["held_by_operator_ruling"] == ["@c:1"]
    assert sorted(text for text, _ in client.asked) == ["free", "ruled"], "held rows are asked"
    assert staged_rows(sources)["@c:1"]["intents"] == ["taste"], "and the ruling still stands"
    assert [fix["id"] for fix in out["applied"]] == ["@c:2"]


def test_this_script_reading_its_own_fixes_back_is_not_an_operator_ruling(tmp_path):
    """The bug this exists to stop: the hold is `a fix has moved this row`, and after one
    invocation that is true of every row this script just wrote. A second pass would then
    report its own 32 answers as rulings and refuse to touch them."""
    sources, store = corpus(tmp_path, [row("@c:1", 1, ["taste"])], [row("@c:1", 1, [])])
    drop, record = records(
        tmp_path,
        1,
        {"taste": 1},
        fixes=[
            {"applied_by": emptied.APPLIED_BY, "rows": [{"id": "@c:1", "old": []}]},
            {
                "applied_by": "scripts/apply_calibration_rulings.py",
                "rows": [{"id": "@c:2", "old": []}],
            },
        ],
    )
    assert emptied.ruled(record) == {"@c:2"}

    _, out = run(tmp_path, sources, store, drop, record, {"Так": '{"intents": ["price"]}'})
    assert out["population"]["held_by_operator_ruling"] == []
    assert staged_rows(sources)["@c:1"]["intents"] == ["price"], "its own row is still writable"


def test_an_answer_moves_the_intents_column_and_nothing_else(tmp_path):
    sources, store = corpus(tmp_path, [row("@c:1", 1, ["taste"])], [row("@c:1", 1, [])])
    drop, record = records(tmp_path, 1, {"taste": 1})
    _, out = run(tmp_path, sources, store, drop, record, {"Так": '{"intents": ["taste"]}'})

    after = staged_rows(sources)["@c:1"]
    assert after["intents"] == ["taste"]
    assert {key: value for key, value in after.items() if key != "intents"} == {
        "id": "@c:1",
        "channel": "@c",
        "parent_msg_id": 1,
        "text": "Так",
        "unclear": False,
    }
    history = json.loads(record.read_text(encoding="utf-8"))
    assert history["runs"] == [], "the drift block of the paid run is not recomputed"
    assert history["fixes"][-1]["authority"].endswith("out.json")
    assert history["fixes"][-1]["rows"] == [
        {
            "id": "@c:1",
            "file": relabel.rel(relabel.staged(sources["comments"])),
            "old": [],
            "new": ["taste"],
        }
    ]


def test_the_post_reaches_the_model_and_a_media_only_one_is_split_out(tmp_path):
    """23 of the real 97 reply to a post whose text is in the image, the two ruled rows
    among them — so `the post fixes it` has to be reported separately from `there was one`."""
    sources, store = corpus(
        tmp_path,
        [row("@c:1", 1, ["taste"], "has"), row("@c:2", 2, ["price"], "none")],
        [row("@c:1", 1, [], "has"), row("@c:2", 2, [], "none")],
        posts=((1, "Новинка: сирок"), (2, "")),
    )
    drop, record = records(tmp_path, 2, {"taste": 1, "price": 1})
    client, out = run(
        tmp_path,
        sources,
        store,
        drop,
        record,
        {"has": '{"intents": ["taste"]}', "none": '{"intents": []}'},
    )

    assert dict(client.asked)["has"] == "Новинка: сирок"
    assert dict(client.asked)["none"] == ""
    assert out["population"]["parent_is_media_only"] == 1
    assert out["answers"]["parent_has_text"] == {
        "asked": 1,
        "regained_a_label": 1,
        "rate": 1.0,
        "still_empty": 0,
        "matches_v1": 1,
    }
    assert out["answers"]["parent_is_media_only"]["regained_a_label"] == 0


def test_a_comment_whose_parent_is_not_stored_stops_before_a_request(tmp_path):
    sources, store = corpus(
        tmp_path, [row("@c:1", 99, ["taste"])], [row("@c:1", 99, [])], posts=((1, "post"),)
    )
    drop, record = records(tmp_path, 1, {"taste": 1})
    original = relabel.SOURCES
    relabel.SOURCES = sources
    client = Canned({})
    try:
        with pytest.raises(SystemExit, match="not in the stored posts"):
            emptied.main(
                [
                    "--drop",
                    str(drop),
                    "--relabel-record",
                    str(record),
                    "--posts",
                    str(store),
                    "--record",
                    str(tmp_path / "out.json"),
                    "--rows-out",
                    str(tmp_path / "rows.jsonl"),
                ],
                asker=client,
            )
    finally:
        relabel.SOURCES = original
    assert client.asked == [], "nothing was spent"


def test_the_check_sample_is_seeded_and_counts_the_rows_it_cannot_contrast(tmp_path):
    """A row whose with-post set equals its v1 set gives the operator two identical cells.
    The rule pre-registers those as `new`; the count has to be in the record or the rate
    cannot be recomputed from the rule."""
    before = [row(f"@c:{i}", 1, ["taste"], f"t{i}") for i in range(6)]
    after = [row(f"@c:{i}", 1, [], f"t{i}") for i in range(6)]
    sources, store = corpus(tmp_path, before, after)
    drop, record = records(tmp_path, 6, {"taste": 6})
    answers = {
        f"t{i}": ('{"intents": ["taste"]}' if i < 4 else '{"intents": ["price"]}') for i in range(6)
    }
    _, out = run(tmp_path, sources, store, drop, record, answers, argv=[])

    assert out["check"]["identical_to_v1"] == sum(
        1 for r in out["check"]["rows_drawn"] if r["intents_with_post"] == r["intents_v1"]
    )
    assert out["check"]["bar"] == 0.90
    assert "counts as `new`" in out["check"]["rule"]
    assert [r["id"] for r in out["check"]["rows_drawn"]] == sorted(
        r["id"] for r in out["check"]["rows_drawn"]
    )


def test_a_rows_file_from_another_population_is_refused(tmp_path):
    sources, store = corpus(tmp_path, [row("@c:1", 1, ["taste"])], [row("@c:1", 1, [])])
    drop, record = records(tmp_path, 1, {"taste": 1})
    (tmp_path / "rows.jsonl").write_text('{"id": "@c:9", "intents": []}\n', encoding="utf-8")
    with pytest.raises(SystemExit, match="not one of the emptied rows"):
        run(tmp_path, sources, store, drop, record, {"Так": '{"intents": []}'})
