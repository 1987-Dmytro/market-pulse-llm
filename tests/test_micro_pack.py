"""The 14 rows the model refused, packed for the operator (4.5f).

The pack is a list of failures, and a list of failures is the easiest kind to collect
wrongly — so the set is derived twice and the two have to agree. The other thing worth
testing is that nothing in the file proposes an answer: these rows exist because the
majority answer would have been the wrong thing to give them.
"""

import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_micro_pack as micro  # noqa: E402
import relabel_intents as relabel  # noqa: E402


def row(row_id, intents=(), text="текст"):
    return {"id": row_id, "text": text, "intents": list(intents), "unclear": False}


def corpus(tmp_path, source_ids, staged_ids):
    source = tmp_path / "comments.jsonl"
    source.write_text(
        "".join(json.dumps(row(i), ensure_ascii=False) + "\n" for i in source_ids), encoding="utf-8"
    )
    relabel.staged(source).write_text(
        "".join(json.dumps(row(i), ensure_ascii=False) + "\n" for i in staged_ids), encoding="utf-8"
    )
    return {"comments": source}


def run_record(tmp_path, unusable_ids, source):
    path = tmp_path / "run.json"
    path.write_text(
        json.dumps(
            {
                "runs": [
                    {
                        "source": str(source),
                        "drift": {"unusable": [{"id": i} for i in ["@c:99"]]},
                    },
                    {
                        "source": str(source),
                        "drift": {"unusable": [{"id": i} for i in unusable_ids]},
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    return path


def build(tmp_path, sources, run, **kwargs):
    original = relabel.SOURCES
    relabel.SOURCES = sources
    try:
        argv = [
            "--pack",
            str(tmp_path / "pack" / "unreadable.csv"),
            "--manifest",
            str(tmp_path / "micro.json"),
            "--run",
            str(run),
            *kwargs.pop("extra", []),
        ]
        assert micro.main(argv) == 0
    finally:
        relabel.SOURCES = original
    return (
        tmp_path / "pack" / "unreadable.csv",
        json.loads((tmp_path / "micro.json").read_text(encoding="utf-8")),
    )


def rows_of(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=micro.DELIMITER))


def test_the_pack_is_the_rows_a_source_has_and_its_staged_copy_does_not(tmp_path):
    sources = corpus(tmp_path, ["@c:1", "@c:2", "@c:3"], ["@c:1"])
    run = run_record(tmp_path, ["@c:2", "@c:3"], sources["comments"])
    path, manifest = build(tmp_path, sources, run)

    assert manifest["rows"] == 2 and manifest["ids"] == ["@c:2", "@c:3"]
    assert [line["id"] for line in rows_of(path)] == ["@c:2", "@c:3"]
    assert tuple(rows_of(path)[0]) == micro.COLUMNS


def test_two_derivations_that_disagree_stop_the_build(tmp_path):
    """`source minus staged` and the runs' own unusable list have to name one set."""
    sources = corpus(tmp_path, ["@c:1", "@c:2", "@c:3"], ["@c:1"])
    run = run_record(tmp_path, ["@c:2"], sources["comments"])
    with pytest.raises(SystemExit, match="derivations disagree on \\['@c:3'\\]"):
        build(tmp_path, sources, run)


def test_nothing_in_the_pack_proposes_a_label(tmp_path):
    sources = corpus(tmp_path, ["@c:1", "@c:2"], [])
    run = run_record(tmp_path, ["@c:1", "@c:2"], sources["comments"])
    path, manifest = build(tmp_path, sources, run)

    assert all(line["intents_v2"] == "" for line in rows_of(path))
    assert manifest["to_fill"] == "intents_v2" and manifest["gated"] is False
    assert all(line["intents_v1"] == "[]" for line in rows_of(path))


def test_a_micro_pack_being_filled_in_is_not_quietly_rebuilt(tmp_path):
    sources = corpus(tmp_path, ["@c:1", "@c:2"], [])
    run = run_record(tmp_path, ["@c:1", "@c:2"], sources["comments"])
    path, _ = build(tmp_path, sources, run)

    lines = rows_of(path)
    lines[0]["intents_v2"] = '["taste"]'
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=micro.COLUMNS, delimiter=micro.DELIMITER, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(lines)

    assert micro.filled(path) == 1
    with pytest.raises(SystemExit, match="already carries 1 labels"):
        build(tmp_path, sources, run)
    assert micro.filled(path) == 1, "the refusal left the operator's work alone"

    build(tmp_path, sources, run, extra=["--force"])
    assert micro.filled(path) == 0, "--force is the one that destroys it"


def test_the_frozen_ids_this_phase_never_asked_are_not_called_unreadable(tmp_path):
    """A test row is absent from the staged copy because it was skipped, not refused."""
    frozen = next(iter(relabel.forbidden_ids()))
    sources = corpus(tmp_path, ["@c:1", frozen], [])
    assert [found["id"] for found in micro.unreadable(sources)] == ["@c:1"]
