"""The labels gate, red-first — four defects refused by name, and one green path.

Written against a SYNTHETIC labels file every time. `docs/labels-pass1-r1.jsonl` is a team-lead
file from the moment it exists and nothing here may create one, so every fixture lives in
`tmp_path` and the last test asserts the real path is still absent.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate_pass1_labels as gate  # noqa: E402

PACK = json.loads((REPO_ROOT / "results" / "pass1_label_pack_r1.json").read_text("utf-8"))


def write(tmp_path: Path, rows: list[dict]) -> Path:
    path = tmp_path / "labels.jsonl"
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
    return gate.main([str(write(tmp_path, rows)), "--pack", str(gate.PACK)])


def test_a_complete_file_passes_and_writes_nothing(tmp_path, capsys):
    path = write(tmp_path, complete())
    before = sorted((one.name, one.stat().st_mtime_ns) for one in tmp_path.iterdir())
    assert gate.main([str(path), "--pack", str(gate.PACK)]) == 0
    assert sorted((one.name, one.stat().st_mtime_ns) for one in tmp_path.iterdir()) == before
    source = Path(gate.__file__).read_text(encoding="utf-8")
    assert "write_text" not in source and "write_bytes" not in source
    out = capsys.readouterr().out
    assert "OK — 500 rows" in out
    assert "null" in out and "категория_личное" in out


def test_a_missing_unit_is_refused(tmp_path):
    with pytest.raises(SystemExit, match="drawn units are not answered"):
        run(tmp_path, complete()[:-1])


def test_a_duplicate_is_refused(tmp_path):
    rows = complete()
    rows[7] = dict(rows[3])
    with pytest.raises(SystemExit, match="answered more than once"):
        run(tmp_path, rows)


def test_an_off_taxonomy_value_is_refused(tmp_path):
    rows = complete()
    rows[11]["subject_type"] = "категория"
    with pytest.raises(SystemExit, match="outside the taxonomy"):
        run(tmp_path, rows)


def test_the_string_null_is_not_the_null(tmp_path):
    """`"null"` looks like an answer and is a value nothing downstream can read."""
    rows = complete()
    rows[2]["subject_type"] = "null"
    with pytest.raises(SystemExit, match="never the string 'null'"):
        run(tmp_path, rows)


def test_a_contaminated_row_is_refused(tmp_path):
    """A row from one of the seven excluded threads — the defect the honesty frame exists for."""
    rows = complete()
    rows[0] = {
        "thread": PACK["exclusion"]["threads"][0],
        "msg_id": 20594,
        "subject_type": "сеть_ритейлер",
    }
    with pytest.raises(SystemExit, match="EXCLUDED threads"):
        run(tmp_path, rows)


def test_a_row_that_is_not_a_unit_is_refused(tmp_path):
    rows = complete()
    rows[5]["msg_id"] = 999_999_999
    with pytest.raises(SystemExit, match="not units of the pack"):
        run(tmp_path, rows)


def test_an_absent_subject_type_is_not_null(tmp_path):
    rows = complete()
    rows[9].pop("subject_type")
    with pytest.raises(SystemExit, match="null is an answer"):
        run(tmp_path, rows)


def test_a_line_that_is_not_json_is_refused(tmp_path):
    path = tmp_path / "labels.jsonl"
    path.write_text('{"thread": "@a:1", "msg_id": 1, "subject_type": null}\nnot json\n', "utf-8")
    with pytest.raises(SystemExit, match="line 2 is not one JSON object"):
        gate.main([str(path), "--pack", str(gate.PACK)])


def test_a_missing_labels_file_is_refused(tmp_path):
    with pytest.raises(SystemExit, match="The TEAM LEAD writes it"):
        gate.main([str(tmp_path / "nothing.jsonl"), "--pack", str(gate.PACK)])


def test_the_domain_is_the_prompt_s_and_the_real_labels_file_does_not_exist():
    from market_pulse import prompts

    assert gate.VALUES == (*prompts.PASS1_SUBJECT_TYPES, None)
    assert len(gate.VALUES) == 5
    assert not gate.LABELS.exists()
