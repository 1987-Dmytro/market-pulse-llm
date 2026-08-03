"""What the sitting decided, written into the staged taxonomy-v2 files (4.5g3).

This merge writes into training sources, so it is judged on the ways a write can be wrong and
still look right: a blank cell read as `[]`, a line that moved a column nobody named, a row
appended at the end of a file whose whole purpose is to diff against its source, and — the one
that actually bit — a fix block whose `old` is the value found on disk rather than the answer
the re-labeller gave, which silently redefines the population every later step derives.
"""

import csv
import json
import sys
from hashlib import sha256
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import merge_sitting_returns as merge  # noqa: E402
import relabel_intents as relabel  # noqa: E402

REDO_COLUMNS = (
    "id",
    "post",
    "post_media",
    "caption",
    "text",
    "intents_v1",
    "intents_model",
    "intents_final",
    "notes",
)
MICRO_COLUMNS = ("id", "text", "intents_v1", "intents_v2", "notes")


def row(msg_id, text, intents, annotator="human"):
    return {
        "id": f"@c:{msg_id}",
        "channel": "@c",
        "msg_id": msg_id,
        "parent_msg_id": 1,
        "language": "uk",
        "text": text,
        "sentiment": "neutral",
        "sarcasm": False,
        "intents": intents,
        "unclear": False,
        "annotator": annotator,
        "notes": "",
    }


def write_lines(path: Path, rows) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in rows), encoding="utf-8"
    )
    return path


def write_csv(path: Path, columns, rows) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def bench(tmp_path, monkeypatch, redo_final=None, unreadable_v2="[]", passed=()):
    """One source file, its staged copy, and the three returned artefacts.

    Four rows with four jobs: @c:1 was emptied and stays emptied on disk, @c:2 was emptied and
    then moved by a later fix (the case that broke the first draft), @c:3 was never staged at
    all, and @c:4 is a bystander that must come out byte-identical.
    """
    source_rows = [
        row(1, "з вишнею", ["taste"]),
        row(2, "а знижка буде?", ["price"]),
        row(3, "…", []),
        row(4, "прокисло", ["quality"]),
    ]
    staged_rows = [
        row(1, "з вишнею", []),
        row(2, "а знижка буде?", ["service"], annotator="llm-recheck-v2"),
        row(4, "прокисло", ["quality"]),
    ]
    source = write_lines(tmp_path / "comments_train.jsonl", source_rows)
    staged = write_lines(tmp_path / "comments_train_tax2.jsonl", staged_rows)
    monkeypatch.setattr(relabel, "SOURCES", {"comments_train": source})
    monkeypatch.setattr(
        relabel, "NEVER", (write_lines(tmp_path / "never.jsonl", [row(99, "x", [])]),)
    )

    (tmp_path / "drop.json").write_text(
        json.dumps(
            {"populations": {"all": {"emptied": 2, "emptied_from": {"taste": 1, "price": 1}}}}
        ),
        encoding="utf-8",
    )
    # @c:2's staged value is a later fix's answer; the re-labeller's own answer was `[]`
    (tmp_path / "relabel.json").write_text(
        json.dumps(
            {
                "runs": [],
                "fixes": [
                    {
                        "applied_by": "scripts/relabel_emptied.py",
                        "rows": [{"id": "@c:2", "old": [], "new": ["service"]}],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "quiz.json").write_text(
        json.dumps({"runs": [{"applied": [], "unchanged": [], "held": []}]}), encoding="utf-8"
    )

    pack = tmp_path / "pack"
    final = redo_final or {"@c:1": '["taste"]', "@c:2": "[]"}
    write_csv(
        pack / "emptied_redo.csv",
        REDO_COLUMNS,
        [
            {
                "id": item["id"],
                "post": "[опрос] З чим?",
                "post_media": "",
                "caption": "",
                "text": item["text"],
                "intents_v1": json.dumps(item["intents"]),
                "intents_model": "",
                "intents_final": final[item["id"]],
                "notes": "tl-llm; dish answer",
            }
            for item in source_rows[:2]
        ],
    )
    micro_pack = tmp_path / "micro" / "unreadable14.csv"
    write_csv(
        micro_pack,
        MICRO_COLUMNS,
        [
            {
                "id": "@c:3",
                "text": "…",
                "intents_v1": "[]",
                "intents_v2": unreadable_v2,
                "notes": "verdict: operator; noise",
            }
        ],
    )
    (tmp_path / "micro.json").write_text(
        json.dumps({"pack": "micro/unreadable14.csv", "ids": ["@c:3"]}), encoding="utf-8"
    )
    (tmp_path / "manifest.json").write_text(
        json.dumps({"pack": "pack", "precheck": {"rows": 300}}), encoding="utf-8"
    )
    (tmp_path / "gates.json").write_text(
        json.dumps(
            {
                "manifest": str(tmp_path / "manifest.json"),
                "bar": 0.9,
                "passed": list(passed),
                "failed": ["general"],
                "second_round_rows": 859,
                "strata": {"general": {"agreement": 0.81}},
            }
        ),
        encoding="utf-8",
    )
    return {"source": source, "staged": staged, "pack": pack, "micro": micro_pack}


def run(tmp_path, extra=()):
    return merge.main(
        [
            "--gates",
            str(tmp_path / "gates.json"),
            "--manifest",
            str(tmp_path / "manifest.json"),
            "--micro-manifest",
            str(tmp_path / "micro.json"),
            "--drop",
            str(tmp_path / "drop.json"),
            "--relabel-record",
            str(tmp_path / "relabel.json"),
            "--quiz-record",
            str(tmp_path / "quiz.json"),
            "--record",
            str(tmp_path / "merge.json"),
            "--root",
            str(tmp_path),
            *extra,
        ]
    )


def staged_of(paths):
    return {item["id"]: item for item in relabel.load(paths["staged"])[0]}


def test_the_decided_labels_land_and_the_bystander_row_is_untouched(tmp_path, monkeypatch):
    paths = bench(tmp_path, monkeypatch)
    before = relabel.load(paths["staged"])[1][-1]
    assert run(tmp_path) == 0

    rows = staged_of(paths)
    assert rows["@c:1"]["intents"] == ["taste"] and rows["@c:2"]["intents"] == []
    assert rows["@c:1"]["annotator"] == merge.ANNOTATOR
    assert rows["@c:1"]["notes"].startswith(f"{merge.ANNOTATOR}: tl-llm")
    assert relabel.load(paths["staged"])[1][-1] == before, "@c:4 came out byte-identical"


def test_an_empty_answer_is_a_label_and_an_empty_cell_is_not(tmp_path, monkeypatch):
    """`[]` is what 11 of the 75 rows say. A truthiness test would read them as unfilled and a
    lenient one would read a genuinely unfilled cell as `[]` — the two must not be the same."""
    paths = bench(tmp_path, monkeypatch, redo_final={"@c:1": "[]", "@c:2": "[]"})
    assert run(tmp_path) == 0
    assert staged_of(paths)["@c:1"]["intents"] == []

    bench(tmp_path, monkeypatch, redo_final={"@c:1": "  ", "@c:2": "[]"})
    with pytest.raises(SystemExit, match="the cell is empty"):
        run(tmp_path)


def test_the_fix_block_reverses_to_the_relabellers_answer_and_not_to_the_disk_value(
    tmp_path, monkeypatch
):
    """@c:2's staged value is a later fix's `["service"]`, not the `[]` the re-labeller gave.
    Recording the disk value as `old` makes the reversal restore `["service"]`, and the row
    stops deriving as emptied — which is how a population every later step reads gets redefined
    by a merge that reported success."""
    bench(tmp_path, monkeypatch)
    assert run(tmp_path) == 0

    history = json.loads((tmp_path / "relabel.json").read_text(encoding="utf-8"))
    mine = next(fix for fix in history["fixes"] if fix["applied_by"] == merge.APPLIED_BY)
    moved = {entry["id"]: entry for entry in mine["rows"]}
    assert moved["@c:2"]["old"] == [], "the re-labeller's answer, which the reversal restores"
    assert moved["@c:2"]["replaced"] == ["service"], "and what was actually overwritten"
    assert moved["@c:1"]["old"] == moved["@c:1"]["replaced"] == []
    record = json.loads((tmp_path / "merge.json").read_text(encoding="utf-8"))["runs"][-1]
    assert record["emptied_population_still"] == 2


def test_a_row_that_was_never_staged_joins_at_its_source_position(tmp_path, monkeypatch):
    """A `_tax2` copy exists to diff against its source line for line. Appended at the end,
    @c:3 would show up in that diff as every row after it having moved."""
    paths = bench(tmp_path, monkeypatch)
    assert run(tmp_path) == 0

    order = [item["id"] for item in relabel.load(paths["staged"])[0]]
    assert order == ["@c:1", "@c:2", "@c:3", "@c:4"]
    added = relabel.load(paths["staged"])[0][2]
    assert added["intents"] == [] and added["annotator"] == merge.ANNOTATOR
    assert "verdict: operator" in added["notes"]


def test_an_added_row_that_would_join_the_emptied_class_stops_before_any_write(
    tmp_path, monkeypatch
):
    """The 97 are a population other steps derive from. A row whose v1 label is not empty and
    whose sitting answer is `[]` would widen it as a side effect of a merge — and a guard that
    notices after the files are rewritten is not a guard."""
    paths = bench(tmp_path, monkeypatch)
    write_csv(
        paths["micro"],
        MICRO_COLUMNS,
        [{"id": "@c:3", "text": "…", "intents_v1": "[]", "intents_v2": "[]", "notes": ""}],
    )
    # give @c:3 a non-empty v1 label in the source, so adding it with `[]` empties it
    source_rows = relabel.load(paths["source"])[0]
    source_rows[2]["intents"] = ["taste"]
    write_lines(paths["source"], source_rows)
    write_csv(
        paths["micro"],
        MICRO_COLUMNS,
        [{"id": "@c:3", "text": "…", "intents_v1": '["taste"]', "intents_v2": "[]", "notes": ""}],
    )
    untouched = sha256(paths["staged"].read_bytes()).hexdigest()

    with pytest.raises(SystemExit, match="would join the emptied class"):
        run(tmp_path)
    assert sha256(paths["staged"].read_bytes()).hexdigest() == untouched


def test_a_stratum_that_passed_stops_the_run_instead_of_being_merged_blind(tmp_path, monkeypatch):
    """Nothing in 4.5g3 passed, so this path was never exercised — and the up-label rows are in
    no source file, so accepting one is a decision rather than a line of code."""
    bench(tmp_path, monkeypatch, passed=("service-rich",))
    with pytest.raises(SystemExit, match="passed the bar and their rows are not merged here"):
        run(tmp_path)


def test_a_gate_record_about_another_sitting_is_refused(tmp_path, monkeypatch):
    bench(tmp_path, monkeypatch)
    gates = json.loads((tmp_path / "gates.json").read_text(encoding="utf-8"))
    gates["manifest"] = "results/sitting_45f_manifest.json"
    (tmp_path / "gates.json").write_text(json.dumps(gates), encoding="utf-8")
    with pytest.raises(SystemExit, match="two sittings, and the strata do not transfer"):
        run(tmp_path)


def test_a_returned_row_that_is_not_the_derived_one_stops_the_merge(tmp_path, monkeypatch):
    paths = bench(tmp_path, monkeypatch)
    rows = list(
        csv.DictReader(
            (paths["pack"] / "emptied_redo.csv").open(encoding="utf-8-sig"), delimiter=";"
        )
    )
    rows[0]["text"] = "з полуницею"
    write_csv(paths["pack"] / "emptied_redo.csv", REDO_COLUMNS, rows)
    with pytest.raises(SystemExit, match="the returned text is not the staged row's text"):
        run(tmp_path)


def test_a_line_that_moved_a_column_nobody_named_stops_the_merge(tmp_path, monkeypatch):
    """The byte proof, and its negation: three columns may move and a fourth may not."""
    staged = {"id": "@c:1", "text": "з вишнею", "intents": [], "notes": "", "annotator": "x"}
    line = json.dumps(staged, ensure_ascii=False)
    assert json.loads(merge.rewritten(staged, line, {"intents": ["taste"]}))["intents"] == ["taste"]
    with pytest.raises(SystemExit, match="more than the columns it names"):
        merge.rewritten({**staged, "text": "інше"}, line, {"intents": ["taste"]})


def test_a_row_sitting_in_a_frozen_test_file_is_refused(tmp_path, monkeypatch):
    bench(tmp_path, monkeypatch)
    write_lines(tmp_path / "never.jsonl", [row(1, "з вишнею", ["taste"])])
    with pytest.raises(SystemExit, match="sit in a frozen test file"):
        run(tmp_path)
