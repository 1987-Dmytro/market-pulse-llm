"""Re-asking a row whose post has found its voice.

What has to hold: a row nobody asked about comes out of the new batch byte for byte, a row that
was asked moves only the four label fields, an answer already paid for is not paid for twice,
and a caption file that is not the one the record describes stops the run before the first
request rather than rendering half the rows with a description and half with `no text`.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import recheck_with_captions as recheck  # noqa: E402
import relabel_intents as relabel  # noqa: E402
from market_pulse import zero_shot  # noqa: E402


def batch_row(msg_id, text="Так", parent=1, intents=(), unclear=False):
    return {
        "id": f"@c:{msg_id}",
        "source_id": "varus",
        "source_type": "official_retail",
        "channel": "@c",
        "msg_id": msg_id,
        "parent_msg_id": parent,
        "date": "2026-07-26T05:13:13+00:00",
        "language": "uk",
        "text": text,
        "sentiment": "neutral",
        "sarcasm": False,
        "intents": list(intents),
        "unclear": unclear,
        "annotator": "llm-precheck",
        "notes": "",
    }


def write_lines(path: Path, rows) -> Path:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    return path


def bench(tmp_path: Path, rows, posts, captions, quiz_closed=()):
    """Everything the run reads: a batch, its record, a post store, captions and their record."""
    paths = {
        "batch_in": write_lines(tmp_path / "batch.jsonl", rows),
        "batch_out": tmp_path / "batch2.jsonl",
        "redo_rows": tmp_path / "redo.jsonl",
        "outcomes": tmp_path / "outcomes.jsonl",
        "record": tmp_path / "record.json",
        "captions": write_lines(tmp_path / "captions.jsonl", captions),
    }
    media = sum(1 for row in rows if not dict(posts)[row["parent_msg_id"]].strip())
    (tmp_path / "precheck.json").write_text(
        json.dumps({"runs": [{"pool": {"rows": len(rows), "parent_is_media_only": media}}]}),
        encoding="utf-8",
    )
    (tmp_path / "captions_record.json").write_text(
        json.dumps({"runs": [{"kinds": {"image": len(captions)}}]}), encoding="utf-8"
    )
    (tmp_path / "quiz.json").write_text(
        json.dumps(
            {
                "runs": [
                    {
                        "applied": [{"id": row_id} for row_id in quiz_closed],
                        "unchanged": [],
                        "held": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    store = tmp_path / "posts"
    store.mkdir(exist_ok=True)
    write_lines(
        store / "c.jsonl",
        [
            {
                "channel": "@c",
                "msg_id": msg_id,
                "text": text,
                "has_media": True,
                "grouped_id": None,
                "record_type": "post",
            }
            for msg_id, text in posts
        ],
    )
    paths["posts"] = store
    # the 97 and their v1 labels: an empty population keeps the redo pass out of the way
    source = write_lines(tmp_path / "source.jsonl", rows)
    staged = write_lines(tmp_path / "source_tax2.jsonl", rows)
    (tmp_path / "drop.json").write_text(
        json.dumps({"populations": {"all": {"emptied": 0, "emptied_from": {}}}}), encoding="utf-8"
    )
    (tmp_path / "relabel.json").write_text(json.dumps({"runs": [], "fixes": []}), encoding="utf-8")
    paths |= {"source": source, "staged": staged}
    return paths


def run(tmp_path, paths, monkeypatch, extra=()):
    monkeypatch.setattr(relabel, "SOURCES", {"comments_train": paths["source"]})
    asker = recheck.FakeAsker(zero_shot.Budget(recheck.CAP_USD, recheck.CAP_USD))
    code = recheck.main(
        [
            "--batch-in",
            str(paths["batch_in"]),
            "--batch-out",
            str(paths["batch_out"]),
            "--redo-rows",
            str(paths["redo_rows"]),
            "--outcomes",
            str(paths["outcomes"]),
            "--record",
            str(paths["record"]),
            "--precheck",
            str(tmp_path / "precheck.json"),
            "--quiz-record",
            str(tmp_path / "quiz.json"),
            "--captions",
            str(paths["captions"]),
            "--caption-record",
            str(tmp_path / "captions_record.json"),
            "--posts",
            str(paths["posts"]),
            "--drop",
            str(tmp_path / "drop.json"),
            "--relabel-record",
            str(tmp_path / "relabel.json"),
            *extra,
        ],
        asker=asker,
    )
    assert code == 0
    return json.loads(paths["record"].read_text(encoding="utf-8"))["runs"][-1]


CAPTION = [{"channel": "@c", "msg_id": 2, "caption": "Опитування", "kind": "image"}]


def test_a_row_nobody_asked_about_comes_out_byte_for_byte(tmp_path, monkeypatch):
    rows = [batch_row(1, parent=1), batch_row(2, parent=2)]
    paths = bench(tmp_path, rows, posts=((1, "Новинка"), (2, "")), captions=CAPTION)
    record = run(tmp_path, paths, monkeypatch)

    before = paths["batch_in"].read_text(encoding="utf-8").splitlines()
    after = paths["batch_out"].read_text(encoding="utf-8").splitlines()
    assert len(before) == len(after)
    assert before[0] == after[0], "the row under a post with text was not re-asked"
    assert before[1] != after[1]
    assert record["precheck"]["copied_unchanged"] == 1
    assert record["precheck"]["context_states"] == {"image_caption": 1}


def test_a_re_asked_row_moves_the_four_label_fields_and_nothing_else():
    row = batch_row(2, intents=["price"])
    line = json.dumps(row, ensure_ascii=False)
    produced = recheck.rewritten(
        row, line, {"sentiment": "positive", "sarcasm": True, "intents": ["taste"], "unclear": True}
    )
    back = json.loads(produced)
    assert back["text"] == row["text"] and back["annotator"] == row["annotator"]
    assert back["intents"] == ["taste"] and back["unclear"] is True


def test_a_line_that_does_not_restore_stops_the_run():
    """The byte proof, negated: if the source line and the row disagree about anything else,
    rewriting would carry that disagreement into the new batch under this run's name."""
    row = batch_row(2)
    with pytest.raises(SystemExit, match="more than the four fields"):
        recheck.rewritten(row, json.dumps({**row, "notes": "edited"}), {**row})


def test_an_answer_already_paid_for_is_not_paid_for_twice(tmp_path, monkeypatch):
    rows = [batch_row(1, parent=2), batch_row(2, parent=2)]
    paths = bench(tmp_path, rows, posts=((2, ""),), captions=CAPTION)
    first = run(tmp_path, paths, monkeypatch)
    assert first["cost"]["requests"] == 2
    again = run(tmp_path, paths, monkeypatch)
    assert again["cost"]["requests"] == 0
    assert again["cost"]["rows_from_an_earlier_run"] == 2
    assert again["precheck"]["relabelled"] == 2
    assert paths["batch_out"].read_text(encoding="utf-8") == paths["batch_out"].read_text(
        encoding="utf-8"
    )


def test_an_outcome_file_from_another_population_is_refused(tmp_path, monkeypatch):
    rows = [batch_row(1, parent=2)]
    paths = bench(tmp_path, rows, posts=((2, ""),), captions=CAPTION)
    write_lines(
        paths["outcomes"],
        [{"task": recheck.PRECHECK_TASK, "id": "@c:999", "labels": {"intents": []}}],
    )
    monkeypatch.setattr(relabel, "SOURCES", {"comments_train": paths["source"]})
    with pytest.raises(SystemExit, match="not in that population"):
        run(tmp_path, paths, monkeypatch)


def test_a_caption_file_the_record_does_not_describe_stops_before_the_first_request(
    tmp_path, monkeypatch
):
    """Half a population asked with a description and half with `no text` is a difference no
    downstream file can see: the prompt hash is the same and the record would claim one run."""
    rows = [batch_row(1, parent=2)]
    paths = bench(tmp_path, rows, posts=((2, ""),), captions=CAPTION)
    write_lines(paths["captions"], [])
    monkeypatch.setattr(relabel, "SOURCES", {"comments_train": paths["source"]})
    with pytest.raises(SystemExit, match="is not the one the record describes"):
        run(tmp_path, paths, monkeypatch)


def test_the_diff_counts_rows_once_and_fields_separately():
    before = {
        "a": {"sentiment": "neutral", "sarcasm": False, "intents": ["price"], "unclear": False}
    }
    after = {
        "a": {"sentiment": "positive", "sarcasm": False, "intents": ["taste"], "unclear": False}
    }
    found = recheck.field_diff(before, after)
    assert found["changed_any_field"] == 1
    assert found["per_field"] == {"sentiment": 1, "sarcasm": 0, "intents": 1, "unclear": 0}
    assert found["intents_gained"] == {"taste": 1} and found["intents_lost"] == {"price": 1}
