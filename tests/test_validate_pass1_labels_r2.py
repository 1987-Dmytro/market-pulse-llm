"""The r2 labels gate and the r2 SEAL — the r1 validator pointed at the r2 pack, red-first.

There is no second validator, and that is the point: `scripts/validate_pass1_labels.py` already
takes its pack as an argument, so the taxonomy, the four refusals and the «writes nothing» proof
have exactly one home. What is new here is the pack it is aimed at and the defect that only r2 can
have — a row answering a unit r1 already drew, which is not a unit of THIS pack.

Every refusal fixture is synthetic and lives in `tmp_path`: `docs/labels-pass1-r2.jsonl` is a
team-lead file and nothing here creates or edits one. The seal at the bottom is the other half —
the team lead wrote the file and `docs/PROMPT-lora-b.md` Step 0 (3) commits it, so the two tests
that guard it drive the validator ON it and re-derive every digest of the provenance record.
Reading the team-lead file is licensed by the same source-level proof the green-path test makes:
the gate holds no `write_text` and no `write_bytes`, so running it cannot touch what it reads.
"""

import hashlib
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
FROZEN = REPO_ROOT / "results" / "labels_pass1_r2.jsonl"
PROVENANCE = REPO_ROOT / "results" / "labels_pass1_r2_provenance.json"

DISTRIBUTION = {
    "не_наш_рынок": 89,
    "null": 46,
    "категория_личное": 11,
    "сеть_ритейлер": 4,
    "молочный_бренд": 0,
}
"""What the TEAM LEAD's 150 rows say, counted off the file itself and registered in the contract.

`молочный_бренд: 0` is written out. The top-up drew no row of the class the whole re-draw was
aimed at, and that zero is the input arm B is registered on — a key dropped for being empty reads
as a class nobody counted."""

FILES = {
    "labels": "docs/labels-pass1-r2.jsonl",
    "frozen": "results/labels_pass1_r2.jsonl",
    "codebook": "docs/label-pack-pass1-r2.md",
    "pack": "results/pass1_label_pack_r2.json",
}
"""The four paths the record's blocks must NAME. Without this the digests still match — of
whatever files the record happens to point at, which is a pin that moves with its own subject."""


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


def test_the_real_labels_file_is_sealed_and_the_domain_is_the_prompt_s(capsys):
    """Driven on the REAL labels, not a synthetic — the file lands in the commit this test does.

    Until the team lead wrote it, this test SKIPPED. A skip is the softer form of the same clock an
    absence assert is: it reports green while proving nothing, and it would have gone on doing so
    if the file had never arrived. It flips here, with the file
    ([[a_green_suite_can_have_a_shelf_life]]).
    """
    from market_pulse import prompts

    assert gate.VALUES == (*prompts.PASS1_SUBJECT_TYPES, None)
    assert LABELS.exists()
    rows = gate.read_rows(LABELS)
    assert len(rows) == 150 == sum(DISTRIBUTION.values())
    counted = gate.validate(rows, PACK)
    assert {**{key: 0 for key in DISTRIBUTION}, **counted} == DISTRIBUTION
    assert gate.main([str(LABELS), "--pack", str(PACK_PATH)]) == 0
    assert "OK — 150 rows" in capsys.readouterr().out


def test_the_freeze_carries_the_labels_byte_for_byte_and_the_record_pins_them():
    """`results/labels_pass1_r2.jsonl` is what training reads and the sidecar says where it came
    from. Every digest is RE-DERIVED here and none is retyped: a sha with two homes goes green
    while one of them drifts ([[a_moved_constant_fails_green]])."""
    record = json.loads(PROVENANCE.read_text("utf-8"))
    assert FROZEN.read_bytes() == LABELS.read_bytes()

    for block, expected in FILES.items():
        assert record[block]["file"] == expected, block  # the digest is of the file it NAMES
        named = REPO_ROOT / record[block]["file"]
        assert hashlib.sha256(named.read_bytes()).hexdigest() == record[block]["sha256"], block

    assert record["labels"]["sha256"] == record["frozen"]["sha256"]
    assert record["distribution"] == DISTRIBUTION
    assert record["labels"]["date"] == "2026-08-19"
    assert record["labels"]["rows"] == 150
    assert "TEAM LEAD" in record["labels"]["labelled_by"]
    assert record["pack"]["seed"] == 20260819
    assert record["pack"]["units"] == 150
    assert "ablated" in record["ablation"] or "ablation" in record["ablation"]


def test_one_flipped_label_is_caught_three_ways(tmp_path):
    """The negative control, on a SCRATCH copy — nothing here touches the sealed pair.

    One row's `subject_type` moved, everything else byte-identical. The digest sees it, the
    distribution sees it, and the byte-identity against the freeze sees it; a seal whose only
    guard is a sha that nobody re-derives is a sha with one home.
    """
    scratch = tmp_path / "labels-pass1-r2.jsonl"
    rows = gate.read_rows(LABELS)
    flipped = next(
        index for index, row in enumerate(rows) if row["subject_type"] != "молочный_бренд"
    )
    rows[flipped] = {**rows[flipped], "subject_type": "молочный_бренд"}
    scratch.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )

    record = json.loads(PROVENANCE.read_text("utf-8"))
    assert hashlib.sha256(scratch.read_bytes()).hexdigest() != record["labels"]["sha256"]
    assert gate.validate(gate.read_rows(scratch), PACK) != {
        key: value for key, value in DISTRIBUTION.items() if value
    }
    assert scratch.read_bytes() != FROZEN.read_bytes()
    # and it is still a VALID file: only the seal can tell, which is why the seal exists
    assert gate.main([str(scratch), "--pack", str(PACK_PATH)]) == 0
