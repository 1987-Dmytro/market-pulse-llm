"""The up-label precheck: 1,912 rows the operator has not seen yet, and the guards on them.

Nothing here is annotation until three strata come back at ≥90%, so what the tests hold is
the boundary: the pool has to be the one the appetite was sized on, every produced row has
to be a legal annotation row, and a row the model could not read has to stay unlabelled.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import precheck_uplabel as precheck  # noqa: E402
import uplabel_candidates as candidates  # noqa: E402
from market_pulse import zero_shot  # noqa: E402

FOUR_FIELDS = (
    '{"sentiment": "negative", "sarcasm": false, "intents": ["service"], "unclear": false}'
)


def record(msg_id, parent, text="Вже добу чекаю на доставку"):
    return {
        "id": f"@c:{msg_id}",
        "source_id": "varus",
        "channel": "@c",
        "msg_id": msg_id,
        "parent_msg_id": parent,
        "date": "2026-05-01T10:00:00+00:00",
        "text": text,
        "provenance": {"source_type": "official_retail"},
    }


class Canned:
    def __init__(self, answers):
        self.answers = answers
        self.asked = []
        self.budget = zero_shot.Budget(1.0, 1.0)

    def __call__(self, text, parent):
        self.asked.append((text, parent))
        self.budget.add(0.0001)
        return self.answers[text]


def bench(tmp_path, monkeypatch, rows, posts=((1, "Новинка: сирок"),), steps=None):
    """A pool, its funnel record and a post store — the three inputs the run reads."""
    steps = steps or {"corpus": len(rows), "labelable pool": len(rows)}
    monkeypatch.setattr(candidates, "funnel", lambda: (rows, dict(steps)))
    funnel = tmp_path / "funnel.json"
    funnel.write_text(json.dumps({"funnel": steps}), encoding="utf-8")
    store = tmp_path / "posts"
    store.mkdir()
    (store / "c.jsonl").write_text(
        "".join(
            json.dumps({"channel": "@c", "msg_id": mid, "text": text}, ensure_ascii=False) + "\n"
            for mid, text in posts
        ),
        encoding="utf-8",
    )
    return funnel, store


def run(tmp_path, funnel, store, answers):
    client = Canned(answers)
    assert (
        precheck.main(
            [
                "--funnel",
                str(funnel),
                "--posts",
                str(store),
                "--batch",
                str(tmp_path / "batch.jsonl"),
                "--record",
                str(tmp_path / "record.json"),
                "--concurrency",
                "1",
            ],
            asker=client,
        )
        == 0
    )
    batch = [
        json.loads(line)
        for line in (tmp_path / "batch.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return (
        client,
        batch,
        json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))["runs"][-1],
    )


def test_a_funnel_that_no_longer_reproduces_its_record_stops_the_run(tmp_path, monkeypatch):
    """Two exclusions moving opposite ways leave the total intact, so every step is compared."""
    rows = [record(1, 1)]
    funnel, store = bench(tmp_path, monkeypatch, rows, steps={"corpus": 9, "labelable pool": 1})
    funnel.write_text(
        json.dumps({"funnel": {"corpus": 9, "already labelled": 3, "labelable pool": 1}}),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match="no longer reproduces"):
        precheck.pool(funnel)


def test_every_produced_row_is_a_legal_annotation_row(tmp_path, monkeypatch):
    funnel, store = bench(tmp_path, monkeypatch, [record(1, 1)])
    _, batch, out = run(tmp_path, funnel, store, {"Вже добу чекаю на доставку": FOUR_FIELDS})

    assert len(batch) == 1
    row = batch[0]
    assert row["annotator"] == "llm-precheck" and row["notes"] == ""
    assert (row["sentiment"], row["sarcasm"], row["intents"], row["unclear"]) == (
        "negative",
        False,
        ["service"],
        False,
    )
    # the record fields the guideline's schema names, all present and from the raw record
    assert row["channel"] == "@c" and row["parent_msg_id"] == 1 and row["language"]
    assert out["pool"] == {"rows": 1, "parent_is_media_only": 0, "labelled": 1, "unusable": 0}


def test_a_label_outside_the_guideline_stops_before_it_reaches_the_file(tmp_path, monkeypatch):
    """`check_labels` is the gate between labelling and every number downstream, so the
    precheck passes through it too — a batch a later merge could not accept fails here."""
    funnel, store = bench(tmp_path, monkeypatch, [record(1, 1)])
    monkeypatch.setattr(precheck, "ANNOTATOR", "  ")  # an annotator the checker refuses
    with pytest.raises(SystemExit, match="the annotation checker refuses"):
        run(tmp_path, funnel, store, {"Вже добу чекаю на доставку": FOUR_FIELDS})


def test_the_post_travels_with_the_row_and_a_media_only_one_is_counted(tmp_path, monkeypatch):
    rows = [record(1, 1, "has"), record(2, 2, "none")]
    funnel, store = bench(tmp_path, monkeypatch, rows, posts=((1, "Новинка: сирок"), (2, "")))
    client, _, out = run(tmp_path, funnel, store, {"has": FOUR_FIELDS, "none": FOUR_FIELDS})

    assert dict(client.asked) == {"has": "Новинка: сирок", "none": ""}
    assert out["pool"]["parent_is_media_only"] == 1


def test_a_row_the_model_could_not_read_is_named_and_left_unlabelled(tmp_path, monkeypatch):
    """Never coerced: `[]` and `unclear: false` are the majority answers and would flatter
    exactly the rows the model found hardest."""
    rows = [record(1, 1, "good"), record(2, 1, "bad")]
    funnel, store = bench(tmp_path, monkeypatch, rows)
    _, batch, out = run(
        tmp_path, funnel, store, {"good": FOUR_FIELDS, "bad": "I cannot label this."}
    )

    assert [row["id"] for row in batch] == ["@c:1"]
    assert out["unusable_rows"] == [
        {"id": "@c:2", "labels": None, "unusable": "parse: no JSON object in reply"}
    ]
    assert out["pool"]["unusable"] == 1


def test_a_batch_file_from_another_pool_is_refused(tmp_path, monkeypatch):
    funnel, store = bench(tmp_path, monkeypatch, [record(1, 1)])
    (tmp_path / "batch.jsonl").write_text('{"id": "@c:99"}\n', encoding="utf-8")
    with pytest.raises(SystemExit, match="not in this pool"):
        run(tmp_path, funnel, store, {"Вже добу чекаю на доставку": FOUR_FIELDS})


def test_the_record_says_out_loud_that_nothing_is_merged(tmp_path, monkeypatch):
    """The one property a later reader has to be able to see without reading the code."""
    funnel, store = bench(tmp_path, monkeypatch, [record(1, 1)])
    _, _, out = run(tmp_path, funnel, store, {"Вже добу чекаю на доставку": FOUR_FIELDS})

    assert out["annotator"] == "llm-precheck"
    assert "PRECHECK, not annotation" in out["note"]
    assert out["task"] == "precheck_v2_with_post"
    assert out["batch_sha256"] and out["distribution"]["rows"] == 1
