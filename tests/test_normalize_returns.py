"""4.5b normalization: the spreadsheet round-trip, and the ways it may not be trusted.

The returned pack is the only copy of 244 verdicts, and the sealed pack is the
only copy of what was ruled on. Normalization touches both, so what is checked
here is not that it produces a CSV — it is that it refuses to produce one from
anything but the pinned returns over the sealed rows:

- a cell that came back changed outside the verdict column stops the run, because
  the operator ruled on the sealed text and no other;
- a verdict form the table does not carry stops the run, and so does one whose
  words and leading token disagree — a single derivation would accept ``не A, а B``
  as an ``A``;
- a return set that is not the pinned one stops the run;
- a second run over an already-normalized pack writes nothing, so a rerun cannot
  quietly replace verdicts with a stale copy of them.
"""

import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_audit_pack  # noqa: E402
import normalize_audit_returns as normalizer  # noqa: E402
from market_pulse import audit  # noqa: E402

SEALED = [
    {
        "head": "sentiment",
        "id": "@c:1",
        "text": "a text, with a comma",
        "label_A": "negative",
        "label_B": "neutral",
        "verdict": "",
        "notes": "",
    },
    {
        "head": "sentiment",
        "id": "@c:2",
        "text": "a text\non two lines",
        "label_A": "neutral",
        "label_B": "positive",
        "verdict": "",
        "notes": "",
    },
]
CONTROL = [
    {
        "head": "sentiment",
        "id": "@c:3",
        "text": "nobody disagreed here",
        "label": "neutral",
        "verdict": "",
        "notes": "",
    }
]
RULED = ["A — правильная метка label_A", "B — правильная метка label_B\n\n"]


def write_return(path: Path, columns: tuple[str, ...], rows: list[dict]) -> None:
    """A return file as the spreadsheet writes it: semicolons and a BOM."""
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def build(tmp_path: Path, ruled=RULED, control="correct", returned=SEALED) -> dict:
    """A two-row sealed pack, its returns, and the manifest that pins it."""
    pack, returns = tmp_path / "pack", tmp_path / "returned"
    pack.mkdir()
    returns.mkdir()
    build_audit_pack.write_csv(pack / "comments_sentiment.csv", audit.COLUMNS, SEALED)
    build_audit_pack.write_csv(pack / "control.csv", audit.CONTROL_COLUMNS, CONTROL)
    write_return(
        returns / "comments_sentiment.csv",
        audit.COLUMNS,
        [{**row, "verdict": verdict} for row, verdict in zip(returned, ruled)],
    )
    write_return(
        returns / "control.csv",
        audit.CONTROL_COLUMNS,
        [{**row, "verdict": control} for row in CONTROL],
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "pack_path": "the tests pass --pack",
                "key_sha256": "0" * 64,
                "csv": {
                    name: {
                        "rows": 2 if "sentiment" in name else 1,
                        "sha256": normalizer.digest(pack / name),
                    }
                    for name in ("comments_sentiment.csv", "control.csv")
                },
            }
        ),
        encoding="utf-8",
    )
    return {
        "pack": pack,
        "returns": returns,
        "record": tmp_path / "record.json",
        "argv": [
            "--returns",
            str(returns),
            "--pack",
            str(pack),
            "--manifest",
            str(manifest),
            "--record",
            str(tmp_path / "record.json"),
        ],
        "pins": {
            name: normalizer.digest(returns / name)
            for name in ("comments_sentiment.csv", "control.csv")
        },
    }


def run(case: dict) -> int:
    return normalizer.main(case["argv"], pins=case["pins"])


def read(path: Path, columns: tuple[str, ...]) -> list[dict]:
    return normalizer.read_csv(path, columns, ",", "utf-8")


def test_the_returns_become_the_sealed_rows_with_verdicts(tmp_path):
    case = build(tmp_path)
    assert run(case) == 0

    rows = read(case["pack"] / "comments_sentiment.csv", audit.COLUMNS)
    assert [row["verdict"] for row in rows] == ["A", "B"]
    for filled, sealed in zip(rows, SEALED):
        assert {k: v for k, v in filled.items() if k != "verdict"} == {
            k: v for k, v in sealed.items() if k != "verdict"
        }
    assert [
        row["verdict"] for row in read(case["pack"] / "control.csv", audit.CONTROL_COLUMNS)
    ] == ["correct"]

    record = json.loads(case["record"].read_text(encoding="utf-8"))
    entry = record["files"]["comments_sentiment.csv"]
    assert entry["verdicts"] == {"A": 1, "B": 1}
    assert entry["raw_sha256"] == case["pins"]["comments_sentiment.csv"]
    assert entry["normalized_sha256"] == normalizer.digest(case["pack"] / "comments_sentiment.csv")
    assert entry["sealed_sha256"] != entry["normalized_sha256"]
    assert record["git"]["commit"]


def test_a_cell_edited_outside_the_verdict_column_stops_the_run(tmp_path):
    edited = [SEALED[0], {**SEALED[1], "text": "a text the operator retyped"}]
    case = build(tmp_path, returned=edited)
    with pytest.raises(SystemExit, match=r"line 3: text of '@c:2' differs from the sealed pack"):
        run(case)


def test_a_verdict_form_the_table_does_not_carry_stops_the_run(tmp_path):
    case = build(tmp_path, ruled=[RULED[0], "скорее B, но не уверен"])
    with pytest.raises(SystemExit, match="is not one of the forms the returns carry"):
        run(case)


def test_a_verdict_whose_words_contradict_its_token_stops_the_run(tmp_path, monkeypatch):
    monkeypatch.setitem(normalizer.VERDICT_FORMS, "не A, а B", "B")
    case = build(tmp_path, ruled=[RULED[0], "не A, а B"])
    with pytest.raises(SystemExit, match="derivations disagree"):
        run(case)


def test_a_disagreement_verdict_in_the_control_file_stops_the_run(tmp_path):
    case = build(tmp_path, control=RULED[0])
    with pytest.raises(SystemExit, match=r"verdict 'A' is not one of"):
        run(case)


def test_a_return_the_team_lead_did_not_pin_stops_the_run(tmp_path):
    case = build(tmp_path)
    case["pins"]["control.csv"] = "f" * 64
    with pytest.raises(SystemExit, match="This is not the authoritative return set"):
        run(case)


def test_a_second_run_writes_nothing(tmp_path, capsys):
    case = build(tmp_path)
    assert run(case) == 0
    normalized = {name: (case["pack"] / name).read_bytes() for name in ("control.csv",)}

    assert run(case) == 0
    assert "already normalized" in capsys.readouterr().out
    assert {name: (case["pack"] / name).read_bytes() for name in normalized} == normalized


def test_a_pack_that_is_neither_sealed_nor_normalized_stops_the_run(tmp_path):
    case = build(tmp_path)
    (case["pack"] / "control.csv").write_bytes(b"head,id,text,label,verdict,notes\n")
    with pytest.raises(SystemExit, match=r"\['control.csv'\] match neither"):
        run(case)
