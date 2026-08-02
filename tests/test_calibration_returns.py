"""The reader that turns the operator's returns into the gate number (4.5f).

The gate is arithmetic over cells a spreadsheet re-encoded, so the reader is judged
on the three ways that arithmetic can be wrong without looking wrong: a verdict form
nobody registered, a blank cell quietly dropped from the denominator, and returned
rows that are no longer the sealed ones.

Nothing here reads the real pack, the real manifest or the real `_tax2` files: the
4.5f rulings change those bytes, and a suite that depends on them goes red the moment
the phase it tests moves on.
"""

import csv
import json
import sys
from hashlib import sha256
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_calibration_pack as pack  # noqa: E402
import read_calibration_returns as reader  # noqa: E402

from test_calibration_pack import population  # noqa: E402


def provenance(tmp_path):
    """Two stand-in files with real hashes — the staged rows the pack was drawn from."""
    written = {}
    tmp_path.mkdir(parents=True, exist_ok=True)
    for group, name in (("staged", "staged.jsonl"), ("sources", "source.jsonl")):
        path = tmp_path / name
        path.write_text(f"{name}\n", encoding="utf-8")
        written[group] = {str(path): sha256(path.read_bytes()).hexdigest()}
    return written


def sealed(tmp_path, rows=None):
    """A pack built into a temp directory, with its manifest — the state that went out."""
    drawn = rows if rows is not None else population()
    where = tmp_path / "calib"
    manifest_path = tmp_path / "manifest.json"
    original = pack.load_pairs
    pack.load_pairs = lambda: (drawn, provenance(tmp_path))
    try:
        assert pack.main(["--pack", str(where), "--manifest", str(manifest_path)]) == 0
    finally:
        pack.load_pairs = original
    return where, manifest_path, drawn


def rows_of(path, delimiter=","):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def hand_back(where, name, columns, verdicts, notes=None, edit=None):
    """The pack as a spreadsheet gives it back: semicolons, a BOM, verdicts filled."""
    rows = rows_of(where / name)
    for index, row in enumerate(rows):
        row["verdict"] = verdicts[index]
        if notes:
            row["notes"] = notes.get(row["id"], "")
    if edit:
        edit(rows)
    with (where / name).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter=";", lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)
    return rows


def returned(tmp_path, gated_verdicts, diagnostic_verdicts=None, **kwargs):
    """A sealed pack, handed back with the given verdicts, read by the reader."""
    where, manifest_path, drawn = sealed(tmp_path)
    hand_back(where, "gated.csv", pack.GATED_COLUMNS, gated_verdicts, **kwargs)
    hand_back(
        where,
        "changed.csv",
        pack.DIAGNOSTIC_COLUMNS,
        diagnostic_verdicts or ["new"] * 50,
    )
    record = tmp_path / "verdict.json"
    original = pack.load_pairs
    pack.load_pairs = lambda: (drawn, provenance(tmp_path))
    try:
        assert reader.main(["--manifest", str(manifest_path), "--record", str(record)]) == 0
    finally:
        pack.load_pairs = original
    return json.loads(record.read_text(encoding="utf-8"))


def test_a_hand_computed_tally_is_what_the_gate_says(tmp_path):
    """91 of 100 is 0.91 and clears 0.90; 89 is 0.89 and does not. No third reading."""
    record = returned(tmp_path, ["correct"] * 91 + ["incorrect"] * 9)
    assert record["gate"]["tally"] == {"correct": 91, "incorrect": 9}
    assert record["gate"]["agreement"] == pytest.approx(0.91)
    assert record["gate"]["verdict"] == "PASS"
    assert len(record["rows"]["gated"]) == 100 and len(record["rows"]["changed"]) == 50
    assert record["rule"] == json.loads((tmp_path / "manifest.json").read_text())["rule"]

    record = returned(tmp_path / "again", ["correct"] * 89 + ["incorrect"] * 11)
    assert record["gate"]["agreement"] == pytest.approx(0.89)
    assert record["gate"]["verdict"] == "FAIL"


def test_a_verdict_form_nobody_registered_stops_the_run(tmp_path):
    """The negative control: a sixth form is not guessed at, it ends the run."""
    with pytest.raises(SystemExit, match="is not one of"):
        returned(tmp_path, ["correct"] * 99 + ["правильно"])
    with pytest.raises(SystemExit, match="is not one of"):
        returned(tmp_path / "two", ["correct"] * 100, diagnostic_verdicts=["yes"] * 50)


def test_a_blank_gated_cell_counts_as_disagreement_and_the_run_goes_on(tmp_path):
    """The registered rule. A blank is not an unknown form and not a missing row."""
    record = returned(tmp_path, ["correct"] * 88 + ["  "] * 12)
    assert record["gate"]["tally"] == {reader.BLANK: 12, "correct": 88}
    assert record["gate"]["rows"] == 100, "the blanks stay in the denominator"
    assert record["gate"]["agreement"] == pytest.approx(0.88)
    assert record["gate"]["verdict"] == "FAIL"


def test_the_case_a_spreadsheet_capitalises_is_the_same_verdict(tmp_path):
    record = returned(
        tmp_path,
        ["Correct"] * 60 + ["correct"] * 40,
        diagnostic_verdicts=["Old"] * 2 + ["NEW"] * 47 + ["neither"],
    )
    assert record["gate"]["tally"] == {"correct": 100}
    assert record["diagnostic"]["tally"] == {"neither": 1, "new": 47, "old": 2}


def test_notes_may_come_back_written_and_a_label_may_not(tmp_path):
    where, manifest_path, drawn = sealed(tmp_path)
    first = rows_of(where / "gated.csv")[0]["id"]
    record = returned(
        tmp_path / "notes",
        ["correct"] * 100,
        notes={first: "operator: dictated in chat"},
    )
    assert any(row["notes"] == "operator: dictated in chat" for row in record["rows"]["gated"])

    def retype(rows):
        rows[3]["intents"] = '["service"]'

    hand_back(where, "gated.csv", pack.GATED_COLUMNS, ["correct"] * 100, edit=retype)
    hand_back(where, "changed.csv", pack.DIAGNOSTIC_COLUMNS, ["new"] * 50)
    original = pack.load_pairs
    pack.load_pairs = lambda: (drawn, provenance(tmp_path))
    try:
        with pytest.raises(SystemExit, match="intents of .* differs from the sealed pack"):
            reader.main(["--manifest", str(manifest_path), "--record", str(tmp_path / "r.json")])
    finally:
        pack.load_pairs = original


def test_rows_that_came_back_reordered_are_not_silently_re_paired(tmp_path):
    where, manifest_path, drawn = sealed(tmp_path)
    hand_back(
        where,
        "gated.csv",
        pack.GATED_COLUMNS,
        ["correct"] * 100,
        edit=lambda rows: rows.reverse(),
    )
    hand_back(where, "changed.csv", pack.DIAGNOSTIC_COLUMNS, ["new"] * 50)
    original = pack.load_pairs
    pack.load_pairs = lambda: (drawn, provenance(tmp_path))
    try:
        with pytest.raises(SystemExit, match="came back in a different order"):
            reader.main(["--manifest", str(manifest_path), "--record", str(tmp_path / "r.json")])
    finally:
        pack.load_pairs = original


def test_the_gate_is_not_computed_against_a_pack_that_cannot_be_rebuilt(tmp_path):
    """Both halves of the chain: the staged rows, and the bytes they draw."""
    where, manifest_path, drawn = sealed(tmp_path)
    hand_back(where, "gated.csv", pack.GATED_COLUMNS, ["correct"] * 100)
    hand_back(where, "changed.csv", pack.DIAGNOSTIC_COLUMNS, ["new"] * 50)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    moved = dict(manifest)
    moved["staged"] = {name: "0" * 64 for name in manifest["staged"]}
    (tmp_path / "moved.json").write_text(json.dumps(moved), encoding="utf-8")
    original = pack.load_pairs
    pack.load_pairs = lambda: (drawn, provenance(tmp_path))
    try:
        with pytest.raises(SystemExit, match="the sealed manifest pins"):
            reader.main(["--manifest", str(tmp_path / "moved.json"), "--pack", str(where)])

        redrawn = dict(manifest, sha256=dict(manifest["sha256"], **{"gated.csv": "1" * 64}))
        (tmp_path / "redrawn.json").write_text(json.dumps(redrawn), encoding="utf-8")
        with pytest.raises(SystemExit, match="no longer draws the pack that went out"):
            reader.main(["--manifest", str(tmp_path / "redrawn.json"), "--pack", str(where)])
    finally:
        pack.load_pairs = original


def test_the_diagnostic_tally_is_recorded_beside_the_gate_and_not_inside_it(tmp_path):
    """STATUS.md pre-committed to this: a counter-signal stands beside the number."""
    record = returned(
        tmp_path,
        ["correct"] * 100,
        diagnostic_verdicts=["old"] * 2 + ["neither"] + ["new"] * 47,
    )
    assert record["gate"]["agreement"] == 1.0 and record["gate"]["verdict"] == "PASS"
    assert record["diagnostic"]["tally"] == {"neither": 1, "new": 47, "old": 2}
    assert "does not move the verdict" in record["diagnostic"]["note"]
