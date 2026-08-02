"""The pack the re-label is accepted on, judged on what it cannot leak or lose.

Three properties carry it: the gated hundred is a plain sample of the rows a gate
scores, nothing in it says which rows the model moved, and the denominator is fixed
before any verdict exists. The fourth is that a filled-in pack survives a rebuild.
"""

import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_calibration_pack as pack  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]


def pair(row_id, before, after, unclear=False, source="comments_train"):
    return {
        "id": row_id,
        "source": source,
        "text": f"текст {row_id}",
        "unclear": unclear,
        "before": list(before),
        "after": list(after),
        "changed": set(before) != set(after),
    }


def population(n=1000):
    """Half of them `unclear`, a third of the rest moved — the real shape, in miniature."""
    rows = []
    for index in range(n):
        before = ["price"] if index % 3 else []
        after = ["service"] if index % 3 == 1 else before
        rows.append(pair(f"@c:{index}", before, after, unclear=index % 2 == 1))
    return rows


def fake_load(rows=None):
    drawn = rows if rows is not None else population()
    return lambda: (drawn, {"staged": {"fixture": "—"}, "sources": {"fixture": "—"}})


def build(tmp_path, rows=None, **kwargs):
    """The pack, built into a temp directory from a fixed population."""
    original = pack.load_pairs
    pack.load_pairs = fake_load(rows)
    try:
        args = ["--pack", str(tmp_path / "calib"), "--manifest", str(tmp_path / "manifest.json")]
        for name, value in kwargs.items():
            args += [f"--{name.replace('_', '-')}", str(value)]
        assert pack.main(args) == 0
    finally:
        pack.load_pairs = original
    return tmp_path / "calib", json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))


def rows_of(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_the_two_strata_never_share_a_row():
    """The diagnostic shows the old label; a shared row would arrive pre-argued."""
    drawn = pack.strata(population(), 100, 50)
    assert len(drawn["gated"]) == 100 and len(drawn["changed"]) == 50
    assert not {p["id"] for p in drawn["gated"]} & {p["id"] for p in drawn["changed"]}
    assert all(p["changed"] for p in drawn["changed"])


def test_the_gated_sample_is_drawn_only_from_rows_a_gate_scores():
    """`unclear` rows are excluded from every metric; agreement on them measures nothing."""
    drawn = pack.strata(population(), 100, 50)
    assert not any(p["unclear"] for p in drawn["gated"] + drawn["changed"])


def test_a_sample_larger_than_its_population_stops_instead_of_shrinking():
    with pytest.raises(SystemExit, match="fewer than the 100 SPEC asks"):
        pack.strata([pair("@c:1", [], ["service"])], 100, 50)
    with pytest.raises(SystemExit, match="changed rows left outside"):
        pack.strata(population(), 100, 500)


def test_nothing_in_the_gated_file_says_whether_a_row_moved(tmp_path):
    where, _ = build(tmp_path)
    written = rows_of(where / "gated.csv")
    assert tuple(written[0]) == pack.GATED_COLUMNS, "no before/after column"

    moved = {p["id"] for p in population() if p["changed"]}
    flags = [row["id"] in moved for row in written]
    assert set(flags) == {True, False}, "the fixture has to contain both kinds"
    assert flags != sorted(flags) and flags != sorted(flags, reverse=True), (
        "the rows are grouped by whether they moved, which is the one thing the"
        " operator may not be able to see"
    )
    after = {p["id"]: p["after"] for p in population()}
    for row in written:
        assert json.loads(row["intents"]) == sorted(after[row["id"]])
        assert row["verdict"] == "" and row["notes"] == ""


def test_the_diagnostic_file_shows_both_labels_and_is_not_the_gate(tmp_path):
    where, manifest = build(tmp_path)
    written = rows_of(where / "changed.csv")
    assert tuple(written[0]) == pack.DIAGNOSTIC_COLUMNS
    assert all(row["intents_before"] != row["intents_after"] for row in written)
    readme = (where / "README-calibration.md").read_text(encoding="utf-8")
    assert "на гейт НЕ влияет" in readme
    assert manifest["note"].startswith("The gated sample decides")


def test_the_denominator_is_registered_before_a_single_verdict_exists(tmp_path):
    where, manifest = build(tmp_path)
    readme = (where / "README-calibration.md").read_text(encoding="utf-8")
    assert manifest["rule"] in readme, "one wording, in the pack and in the record"
    assert "blank cell" in manifest["rule"] and "counts as disagreement" in manifest["rule"]
    assert manifest["bar"] == 0.90 and manifest["gated_verdicts"] == ["correct", "incorrect"]
    assert all(not row["verdict"] for row in rows_of(where / "gated.csv"))


def test_the_manifest_pins_the_bytes_that_were_written(tmp_path):
    from hashlib import sha256

    where, manifest = build(tmp_path)
    for name, digest in manifest["sha256"].items():
        assert sha256((where / name).read_bytes()).hexdigest() == digest
    assert manifest["composition"]["gated"]["rows"] == 100
    assert sum(manifest["composition"]["gated"]["by_source"].values()) == 100


def test_a_rebuild_reproduces_the_pack_byte_for_byte(tmp_path):
    first, _ = build(tmp_path / "one")
    second, _ = build(tmp_path / "two")
    for name in ("gated.csv", "changed.csv", "README-calibration.md"):
        assert (first / name).read_bytes() == (second / name).read_bytes()


def test_a_pack_that_is_being_filled_in_is_not_quietly_rebuilt(tmp_path):
    where, _ = build(tmp_path)
    written = rows_of(where / "gated.csv")
    written[0]["verdict"] = "correct"
    with (where / "gated.csv").open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=pack.GATED_COLUMNS, lineterminator="\n")
        out.writeheader()
        out.writerows(written)

    assert pack.filled(where / "gated.csv") == 1
    with pytest.raises(SystemExit, match="already carries 1 verdicts"):
        build(tmp_path)
    assert pack.filled(where / "gated.csv") == 1, "the refusal left the evening's work alone"

    original = pack.load_pairs
    pack.load_pairs = fake_load()
    try:
        argv = ["--pack", str(where), "--manifest", str(tmp_path / "manifest.json"), "--force"]
        assert pack.main(argv) == 0
    finally:
        pack.load_pairs = original
    assert pack.filled(where / "gated.csv") == 0, "--force is the one that destroys it"
