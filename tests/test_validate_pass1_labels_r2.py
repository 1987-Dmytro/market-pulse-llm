"""The r2 labels gate — the r1 validator pointed at the r2 pack, red-first.

There is no second validator, and that is the point: `scripts/validate_pass1_labels.py` already
takes its pack as an argument, so the taxonomy, the four refusals and the «writes nothing» proof
have exactly one home. What is new here is the pack it is aimed at and the defect that only r2 can
have — a row answering a unit r1 already drew, which is not a unit of THIS pack.

Every fixture is synthetic and lives in `tmp_path`: `docs/labels-pass1-r2.jsonl` is a team-lead
file and nothing here creates, edits or asserts the absence of one. The last test drives the gate
on the real file WHEN it exists and is silent when it does not — an absence test is a clock.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate_pass1_labels as gate  # noqa: E402

PACK_PATH = REPO_ROOT / "results" / "pass1_label_pack_r2.json"
PACK = json.loads(PACK_PATH.read_text("utf-8"))
R1_PACK = json.loads((REPO_ROOT / "results" / "pass1_label_pack_r1.json").read_text("utf-8"))
LABELS = REPO_ROOT / "docs" / "labels-pass1-r2.jsonl"


def write(tmp_path: Path, rows: list[dict]) -> Path:
    path = tmp_path / "labels-r2.jsonl"
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    return path


def complete() -> list[dict]:
    """One answer per drawn unit, cycling the domain so every class is exercised."""
    return [
        {"thread": unit["thread"], "msg_id": unit["msg_id"], "subject_type": gate.VALUES[index % 5]}
        for index, unit in enumerate(PACK["units"])
    ]


def run(tmp_path: Path, rows: list[dict]) -> int:
    return gate.main([str(write(tmp_path, rows)), "--pack", str(PACK_PATH)])


def test_a_complete_r2_file_passes_and_writes_nothing(tmp_path, capsys):
    path = write(tmp_path, complete())
    before = sorted((one.name, one.stat().st_mtime_ns) for one in tmp_path.iterdir())
    assert gate.main([str(path), "--pack", str(PACK_PATH)]) == 0
    assert sorted((one.name, one.stat().st_mtime_ns) for one in tmp_path.iterdir()) == before
    source = Path(gate.__file__).read_text(encoding="utf-8")
    assert "write_text" not in source and "write_bytes" not in source
    assert "OK — 150 rows" in capsys.readouterr().out


def test_a_missing_unit_is_refused(tmp_path):
    with pytest.raises(SystemExit, match="drawn units are not answered"):
        run(tmp_path, complete()[:-1])


def test_a_unit_answered_twice_is_refused(tmp_path):
    rows = complete()
    with pytest.raises(SystemExit, match="answered more than once"):
        run(tmp_path, rows + rows[:1])


def test_a_value_outside_the_taxonomy_is_refused(tmp_path):
    rows = complete()
    rows[3]["subject_type"] = "null"  # the STRING, which nothing downstream can read
    with pytest.raises(SystemExit, match="outside the taxonomy"):
        run(tmp_path, rows)


def test_a_missing_subject_type_key_is_not_null(tmp_path):
    rows = complete()
    del rows[7]["subject_type"]
    with pytest.raises(SystemExit, match="An absent subject_type is not null"):
        run(tmp_path, rows)


def test_a_row_from_an_exam_thread_is_refused(tmp_path):
    rows = complete()
    rows[0] = {"thread": PACK["exclusion"]["threads"][0], "msg_id": 1, "subject_type": None}
    with pytest.raises(SystemExit, match="EXCLUDED threads"):
        run(tmp_path, rows)


def test_a_row_r1_already_answered_is_not_a_unit_of_this_pack(tmp_path):
    """The defect only r2 can have. An r1 unit is a real, correctly-formed labelling of a real
    comment — and it belongs to the other pack, so the gate must refuse it as unknown."""
    borrowed = R1_PACK["units"][0]
    rows = complete()[1:] + [
        {"thread": borrowed["thread"], "msg_id": borrowed["msg_id"], "subject_type": None}
    ]
    with pytest.raises(SystemExit, match="not units of the pack"):
        run(tmp_path, rows)


def test_the_two_packs_share_no_unit():
    r1 = {(one["thread"], int(one["msg_id"])) for one in R1_PACK["units"]}
    r2 = {(one["thread"], int(one["msg_id"])) for one in PACK["units"]}
    assert r1 & r2 == set()
    assert len(r2) == 150


def test_the_real_file_validates_when_the_team_lead_has_written_it(capsys):
    """WHEN it exists — never that it does not. The team lead writes it after this contract."""
    if not LABELS.exists():
        pytest.skip("docs/labels-pass1-r2.jsonl is the team lead's and is not written yet")
    assert gate.main([str(LABELS), "--pack", str(PACK_PATH)]) == 0
    assert "OK — 150 rows" in capsys.readouterr().out
