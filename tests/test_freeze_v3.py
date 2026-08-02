"""v3 of the frozen sets: 38 rulings applied, and everything else proved untouched.

A test set is the instrument every gate number was read off, so the failure modes
that matter here are the quiet ones: a row nobody ruled that moves anyway, a head
that gets half-relabelled while its law is undecided, a row ruled under two heads
that keeps only one of the two fixes. Each has a test, and the byte-for-byte
re-serialisation check is the one that covers the failure nobody would think to look
for — a formatting change across all 400 rows that no changelog would mention.
"""

import json
import sys
from hashlib import sha256
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_audit_pack  # noqa: E402
import freeze_testsets_v3 as v3  # noqa: E402
from market_pulse import audit  # noqa: E402

COMMENTS = [
    {
        "id": "@c:1",
        "text": "a",
        "sentiment": "negative",
        "sarcasm": False,
        "intents": ["price"],
        "unclear": False,
        "annotator": "llm-precheck",
        "notes": "",
    },
    {
        "id": "@c:2",
        "text": "b",
        "sentiment": "neutral",
        "sarcasm": False,
        "intents": [],
        "unclear": False,
        "annotator": "llm-precheck",
        "notes": "",
    },
]
HOLDOUT = [
    {
        "id": "@h:1",
        "text": "c",
        "sentiment": "negative",
        "sarcasm": True,
        "intents": [],
        "unclear": False,
        "annotator": "llm-holdout",
        "notes": "",
    },
]
POSTS = [
    {
        "id": "@p:1",
        "text": "d",
        "post_type": "promo",
        "brands": [],
        "relevant": True,
        "unclear": False,
        "annotator": "llm-precheck",
        "notes": "",
    },
]
PRED = {
    "comments_test": {
        "@c:1": {"sentiment": "neutral", "sarcasm": False, "intents": ["taste"]},
        "@c:2": {"sentiment": "neutral", "sarcasm": False, "intents": ["price"]},
    },
    "sarcasm_holdout": {"@h:1": {"sentiment": "neutral", "sarcasm": False, "intents": []}},
    "posts_test": {
        "@p:1": {"post_type": "launch", "brands": [{"mention": "Рудь"}], "relevant": True}
    },
}
# head -> (row id, the column the arm's label sits in, the operator's verdict)
RULINGS = {
    "sentiment": ("@c:1", "A", "A"),
    "intents": ("@c:2", "A", "A"),
    "sarcasm_pair": ("@h:1", "B", "B"),
    "post_type": ("@p:1", "A", "A"),
    "brands": ("@p:1", "B", "B"),
}


def case(tmp_path, monkeypatch, verdicts=None, gold=None):
    """A one-row-per-head pack over a tiny frozen set, plus the manifest that pins it."""
    frozen, pack = tmp_path / "frozen", tmp_path / "pack"
    frozen.mkdir()
    pack.mkdir()
    rows = gold or {"comments_test": COMMENTS, "sarcasm_holdout": HOLDOUT, "posts_test": POSTS}
    for name, values in rows.items():
        (frozen / f"{name}.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in values), encoding="utf-8"
        )
    dump = tmp_path / "dump.jsonl"
    dump.write_text(
        "".join(
            json.dumps({"id": row_id, "input": name, "pred": pred}, ensure_ascii=False) + "\n"
            for name, rows_of in PRED.items()
            for row_id, pred in rows_of.items()
        ),
        encoding="utf-8",
    )

    key, by_csv = {}, {}
    for head, (row_id, model_column, _) in RULINGS.items():
        labels = {"label_A": "left", "label_B": "right"}
        key[f"{head}|{row_id}"] = {"model_column": model_column, **labels}
        verdict = (verdicts or {}).get(head, RULINGS[head][2])
        by_csv.setdefault(audit.CSV_OF[head], []).append(
            {"head": head, "id": row_id, "text": "t", **labels, "verdict": verdict, "notes": ""}
        )
    for name, cells in by_csv.items():
        build_audit_pack.write_csv(pack / name, audit.COLUMNS, cells)
    key_path = tmp_path / "key.json"
    key_path.write_text(json.dumps(key, ensure_ascii=False), encoding="utf-8")

    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "arm": "real-only",
                "frozen_path": str(frozen),
                "pack_path": str(pack),
                "key_path": str(key_path),
                "key_sha256": v3.digest(key_path),
                "predictions_path": str(dump),
                "predictions_sha256": v3.digest(dump),
                "frozen_sha256": {
                    f"{name}.jsonl": v3.digest(frozen / f"{name}.jsonl") for name in rows
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        v3, "EXPECTED", {"sentiment": 1, "sarcasm_pair": 1, "post_type": 1, "brands": 1}
    )
    record = tmp_path / "frozen_v3.json"
    return {
        "frozen": frozen,
        "record": record,
        "argv": ["--manifest", str(manifest), "--record", str(record), "--out", str(frozen)],
    }


def rows_of(path: Path) -> dict[str, dict]:
    return {json.loads(line)["id"]: json.loads(line) for line in path.read_text().splitlines()}


def test_the_rulings_are_applied_and_nothing_else_moves(tmp_path, monkeypatch):
    it = case(tmp_path, monkeypatch)
    assert v3.main(it["argv"]) == 0

    comments = rows_of(it["frozen"] / "comments_test_v3.jsonl")
    assert comments["@c:1"]["sentiment"] == "neutral"  # ruled for the arm
    assert comments["@c:1"]["annotator"] == v3.ANNOTATOR
    assert comments["@c:2"] == COMMENTS[1]  # ruled on intents only — untouched
    holdout = rows_of(it["frozen"] / "sarcasm_holdout_v3.jsonl")["@h:1"]
    assert (holdout["sentiment"], holdout["sarcasm"]) == ("neutral", False)  # the pair


def test_intents_are_derived_and_not_applied(tmp_path, monkeypatch):
    it = case(tmp_path, monkeypatch)
    v3.main(it["argv"])

    for before, after in zip(COMMENTS, rows_of(it["frozen"] / "comments_test_v3.jsonl").values()):
        assert after["intents"] == before["intents"]
    record = json.loads(it["record"].read_text())
    assert record["law_pending"] == ["intents"]
    assert record["law_pending_rulings"] == {"intents": 1}


def test_a_row_ruled_under_two_heads_keeps_both_fixes(tmp_path, monkeypatch):
    it = case(tmp_path, monkeypatch)
    v3.main(it["argv"])

    post = rows_of(it["frozen"] / "posts_test_v3.jsonl")["@p:1"]
    assert post["post_type"] == "launch"
    assert post["brands"] == [{"brand_id": "rud", "mention": "Рудь"}]  # brand_id from the watchlist


def test_a_ruling_for_gold_changes_nothing(tmp_path, monkeypatch):
    it = case(tmp_path, monkeypatch, verdicts={"sentiment": "B"})  # B is gold's column here
    monkeypatch.setattr(
        v3, "EXPECTED", {"sentiment": 0, "sarcasm_pair": 1, "post_type": 1, "brands": 1}
    )
    v3.main(it["argv"])

    assert list(rows_of(it["frozen"] / "comments_test_v3.jsonl").values()) == COMMENTS


def test_a_count_the_gate_did_not_approve_stops_the_run(tmp_path, monkeypatch):
    it = case(tmp_path, monkeypatch)
    monkeypatch.setattr(
        v3, "EXPECTED", {"sentiment": 9, "sarcasm_pair": 1, "post_type": 1, "brands": 1}
    )
    with pytest.raises(SystemExit, match="the gate approved"):
        v3.main(it["argv"])


def test_a_v2_file_that_already_moved_stops_the_run(tmp_path, monkeypatch):
    it = case(tmp_path, monkeypatch)
    path = it["frozen"] / "posts_test.jsonl"
    path.write_text(path.read_text().replace('"promo"', '"other"'), encoding="utf-8")
    with pytest.raises(SystemExit, match="v2 is immutable"):
        v3.main(it["argv"])


def test_an_unruled_cell_stops_the_run(tmp_path, monkeypatch):
    it = case(tmp_path, monkeypatch, verdicts={"post_type": ""})
    with pytest.raises(SystemExit, match="unruled"):
        v3.main(it["argv"])


def test_a_row_that_would_be_reformatted_stops_the_run(tmp_path, monkeypatch):
    reformatted = [{**COMMENTS[0]}, {**COMMENTS[1], "extra": None}]
    it = case(
        tmp_path,
        monkeypatch,
        gold={"comments_test": reformatted, "sarcasm_holdout": HOLDOUT, "posts_test": POSTS},
    )
    path = it["frozen"] / "comments_test.jsonl"
    lines = path.read_text().splitlines()
    lines[1] = json.dumps(
        json.loads(lines[1]), ensure_ascii=False, indent=None, separators=(",", ":")
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    manifest["frozen_sha256"]["comments_test.jsonl"] = sha256(path.read_bytes()).hexdigest()
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(SystemExit, match="does not reproduce its v2 line"):
        v3.main(it["argv"])


def test_the_doc_changelog_is_the_records_own_table():
    """docs/frozen-testsets.md quotes the record, or it is a second source of truth.

    The changelog is the document a later reader reconstructs "what v3 changed" from,
    and a hand-edited line in it would not disagree with anything — the files it
    describes are hashed, the table is not.
    """
    root = Path(__file__).resolve().parents[1]
    record = json.loads((root / "results" / "frozen_v3.json").read_text(encoding="utf-8"))
    doc = (root / "docs" / "frozen-testsets.md").read_text(encoding="utf-8")

    assert v3.changelog_table(record["changes"]) in doc
    for name, sha in record["v3_sha256"].items():
        assert f"| `data/frozen/{name}` | {record['rows'][name]['rows']} |" in doc
        assert sha in doc
