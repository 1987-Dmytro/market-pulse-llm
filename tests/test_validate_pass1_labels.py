"""The labels gate, red-first — four defects refused by name, one green path, and the seal.

The refusals are written against a SYNTHETIC labels file every time: `docs/labels-pass1-r1.jsonl`
is a team-lead file and nothing here may create or edit one, so every defect fixture lives in
`tmp_path`. The seal at the bottom is the other half — the real file exists now, and the two tests
that guard it drive the validator ON it and pin its digest. Reading the team-lead file is licensed
by the same source-level proof the green-path test makes: the gate contains no `write_text` and no
`write_bytes`, so running it cannot touch what it reads.
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate_pass1_labels as gate  # noqa: E402

PACK = json.loads((REPO_ROOT / "results" / "pass1_label_pack_r1.json").read_text("utf-8"))

DISTRIBUTION = {
    "не_наш_рынок": 251,
    "null": 167,
    "сеть_ритейлер": 44,
    "категория_личное": 36,
    "молочный_бренд": 2,
}
"""What the TEAM LEAD's 500 rows say, counted off the file itself and registered in the contract."""


FILES = {
    "labels": "docs/labels-pass1-r1.jsonl",
    "frozen": "results/labels_pass1_r1.jsonl",
    "codebook": "docs/label-pack-pass1-r1.md",
    "pack": "results/pass1_label_pack_r1.json",
}
"""The four paths the record's blocks must NAME. Without this the digests still match — of whatever
files the record happens to point at, which is a pin that moves with its own subject."""


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


def test_the_domain_is_the_prompt_s_and_the_real_labels_file_is_sealed():
    """The domain, and the file it was labelled under — driven on the REAL labels, not a synthetic.

    Until the team lead wrote it, this test asserted the file's ABSENCE, which is a clock and not a
    verifier: it expired the moment the plan it was waiting for executed
    ([[a_green_suite_can_have_a_shelf_life]]).
    """
    from market_pulse import prompts

    assert gate.VALUES == (*prompts.PASS1_SUBJECT_TYPES, None)
    assert len(gate.VALUES) == 5

    assert gate.LABELS.exists()
    rows = gate.read_rows(gate.LABELS)
    assert len(rows) == 500 == sum(DISTRIBUTION.values())
    assert gate.validate(rows, PACK) == DISTRIBUTION
    assert gate.main([str(gate.LABELS), "--pack", str(gate.PACK)]) == 0


def test_the_freeze_carries_the_labels_byte_for_byte_and_the_record_pins_them():
    """`results/labels_pass1_r1.jsonl` is what training reads and the sidecar says where it came
    from. Every digest is RE-DERIVED here and none is retyped: a sha with two homes goes green
    while one of them drifts ([[a_moved_constant_fails_green]])."""
    record = json.loads(
        (REPO_ROOT / "results" / "labels_pass1_r1_provenance.json").read_text("utf-8")
    )
    frozen = REPO_ROOT / "results" / "labels_pass1_r1.jsonl"
    assert frozen.read_bytes() == gate.LABELS.read_bytes()

    for block, expected in FILES.items():
        assert record[block]["file"] == expected, block  # the digest is of the file it NAMES
        named = REPO_ROOT / record[block]["file"]
        assert hashlib.sha256(named.read_bytes()).hexdigest() == record[block]["sha256"], block

    assert record["labels"]["sha256"] == record["frozen"]["sha256"]
    assert record["distribution"] == DISTRIBUTION
    assert record["labels"]["date"] == "2026-08-18"
    assert "TEAM LEAD" in record["labels"]["labelled_by"]
    assert record["pack"]["seed"] == 20260818
    assert "ablated" in record["ablation"]
