"""The split that restored window 1's root: it finds the boundary in the seal, and it refuses.

`scripts/split_derived_w2.py` ran once, over the real store, and its own output is the evidence that
it was right (38/38 sealed sources back to their sealed digests). What that run cannot show is the
half that did NOT happen: what the script does when the seal does not place a file. A guard only
ever seen succeeding is a guard nobody has watched work ([[guard_selftest_negative_control]]), so
every case below is built on a fabricated store — three shapes that must split, and two that must
stop before a byte is truncated.
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import split_derived_w2 as split  # noqa: E402


def write(path: Path, lines: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f'{{"msg_id": {n}}}\n' for n in lines), encoding="utf-8")
    return path


def sha_of(lines: list[str]) -> str:
    return hashlib.sha256("".join(f'{{"msg_id": {n}}}\n' for n in lines).encode()).hexdigest()


@pytest.fixture
def store(tmp_path, monkeypatch):
    """Three files: one the seal hashed whole, one it hashed a PREFIX of, one it never named."""
    w1, w2 = tmp_path / "derived", tmp_path / "derived_w2"
    write(w1 / "post_texts" / "untouched.jsonl", ["1", "2"])
    write(w1 / "post_texts" / "grew.jsonl", ["1", "2", "3", "4"])
    write(w1 / "leaflet_pages" / "brand_new.jsonl", ["9"])
    seal = tmp_path / "seal.json"
    seal.write_text(
        json.dumps(
            {
                "sources": {
                    "derived/post_texts/untouched.jsonl": sha_of(["1", "2"]),
                    "derived/post_texts/grew.jsonl": sha_of(["1", "2"]),
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(split, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(split, "W1_ROOT", w1)
    monkeypatch.setattr(split, "W2_ROOT", w2)
    monkeypatch.setattr(split, "SEAL", seal)
    return w1, w2, tmp_path


def test_the_boundary_comes_from_the_seal_and_the_split_restores_it(store, capsys):
    """The whole manoeuvre: two lines of `grew.jsonl` are window 2's because the SEAL says the first
    two are window 1's, and the file the seal never named moves entire."""
    w1, w2, tmp = store
    assert split.main(["--backup", str(tmp / "backup")]) == 0

    assert (w1 / "post_texts" / "grew.jsonl").read_text() == '{"msg_id": 1}\n{"msg_id": 2}\n'
    assert (w2 / "post_texts" / "grew.jsonl").read_text() == '{"msg_id": 3}\n{"msg_id": 4}\n'
    assert (w2 / "leaflet_pages" / "brand_new.jsonl").read_text() == '{"msg_id": 9}\n'
    assert not (w1 / "leaflet_pages" / "brand_new.jsonl").exists()
    # untouched by C2: it stays whole and nothing of it is written to the live root
    assert (w1 / "post_texts" / "untouched.jsonl").read_text() == '{"msg_id": 1}\n{"msg_id": 2}\n'
    assert not (w2 / "post_texts" / "untouched.jsonl").exists()

    sealed = json.loads(split.SEAL.read_text())["sources"]
    for name, digest in sealed.items():
        assert hashlib.sha256((tmp / name).read_bytes()).hexdigest() == digest, name
    assert "2/2 sources match" in capsys.readouterr().out
    # the backup is the store as it stood, and it is made before any truncation
    assert (tmp / "backup" / "post_texts" / "grew.jsonl").read_text().count("\n") == 4


def test_a_sealed_file_no_prefix_reaches_stops_before_anything_moves(store, capsys):
    """The negative control. C2 only appended — if a sealed file's first bytes have MOVED, the tail
    this script would cut is not the tail, and there is nothing safe left to do but refuse."""
    w1, w2, tmp = store
    write(w1 / "post_texts" / "grew.jsonl", ["0", "2", "3", "4"])

    assert split.main(["--backup", str(tmp / "backup")]) == 2
    assert "no prefix" in capsys.readouterr().err
    assert not w2.exists() and not (tmp / "backup").exists()
    assert (w1 / "post_texts" / "grew.jsonl").read_text().count("\n") == 4


def test_a_sealed_source_that_is_not_on_disk_is_a_refusal(store, capsys):
    """A missing sealed file reads as «nothing to split» to a glob and as «the store is not the one
    the seal describes» to this. The second reading is the true one."""
    w1, w2, tmp = store
    (w1 / "post_texts" / "untouched.jsonl").unlink()

    assert split.main(["--backup", str(tmp / "backup")]) == 2
    assert "is not on disk" in capsys.readouterr().err
    assert not w2.exists()


def test_it_refuses_to_run_twice(store, capsys):
    """A second run would find every sealed file already at its boundary and every C2 file already
    moved — and would then back up the truncated store over nothing. The live root's existence is
    the fact that says the split has happened."""
    w1, w2, tmp = store
    assert split.main(["--backup", str(tmp / "backup")]) == 0
    assert split.main(["--backup", str(tmp / "backup2")]) == 2
    assert "already holds store files" in capsys.readouterr().err


def test_the_dry_run_writes_nothing(store, capsys):
    w1, w2, tmp = store
    assert split.main(["--dry-run"]) == 0
    assert not w2.exists()
    assert (w1 / "leaflet_pages" / "brand_new.jsonl").exists()
    assert "keep 2 of 4" in capsys.readouterr().out
