"""The reader that turns the sitting's verdicts into three gate numbers (4.5g3).

The gate is arithmetic over cells a human filled in, so the reader is judged on the ways
that arithmetic can be wrong without looking wrong: a stratum's number computed on the wrong
denominator, a blank cell dropped instead of counted, a verdict form nobody registered, and
rows that came back changed in a column nobody was asked about.

Nothing here reads the real pack or the real manifest: a suite that depends on those bytes
goes red the moment the next phase re-labels anything.
"""

import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_sitting_pack as sitting  # noqa: E402
import read_sitting_returns as reader  # noqa: E402

from test_sitting_pack import bench, build, spread  # noqa: E402


def hand_back(pack: Path, verdicts, notes=None, edit=None, columns=None):
    """The pack as the sitting gives it back: verdicts filled, everything else untouched."""
    path = pack / "precheck300.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=sitting.DELIMITER))
    for row, verdict in zip(rows, verdicts, strict=True):
        row["verdict"] = verdict
        if notes:
            row["notes"] = notes.get(row["id"], "")
    if edit:
        edit(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=columns or sitting.PRECHECK_COLUMNS,
            delimiter=sitting.DELIMITER,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    return rows


def order_of(pack: Path) -> list[str]:
    with (pack / "precheck300.csv").open(encoding="utf-8", newline="") as handle:
        return [row["id"] for row in csv.DictReader(handle, delimiter=sitting.DELIMITER)]


def grader(wrong: dict[str, int]):
    """Verdicts marking the first `wrong[stratum]` rows of each stratum `incorrect`.

    A callable rather than a list because the file order is a seeded shuffle: which stratum a
    position belongs to is only known once the pack exists.
    """

    def make(manifest, order):
        where = manifest["precheck"]["stratum_of"]
        seen: dict[str, int] = {}
        out = []
        for row_id in order:
            name = where[row_id]
            seen[name] = seen.get(name, 0) + 1
            out.append("incorrect" if seen[name] <= wrong.get(name, 0) else "correct")
        return out

    return make


def read(tmp_path, paths, verdicts, monkeypatch, **kwargs):
    """A sealed pack, handed back with the given verdicts, read by the reader."""
    manifest = build(tmp_path, paths, monkeypatch, per_stratum=kwargs.pop("per_stratum", 2))
    if callable(verdicts):
        verdicts = verdicts(manifest, order_of(tmp_path / "pack"))
    back = hand_back(tmp_path / "pack", verdicts, **kwargs)
    # derived from the file as it actually came back, so an edit made on the way out is in it
    monkeypatch.setattr(
        reader,
        "RECORDED_IN_LOG",
        {
            "correct": sum(1 for row in back if row["verdict"].strip().casefold() == "correct"),
            "incorrect": sum(1 for row in back if row["verdict"].strip().casefold() != "correct"),
        },
    )
    record = tmp_path / "gates.json"
    code = reader.main(
        [
            "--manifest",
            str(tmp_path / "manifest.json"),
            "--pack",
            str(tmp_path / "pack"),
            "--posts",
            str(paths["posts"]),
            "--record",
            str(record),
        ]
    )
    return code, manifest, (json.loads(record.read_text(encoding="utf-8")) if code == 0 else None)


def test_each_stratum_is_scored_on_its_own_hundred_and_the_total_is_not_the_gate(
    tmp_path, monkeypatch
):
    """The bar was registered per stratum. A 93% average over three strata can hold one at 80%,
    and merging on the average would merge the population that failed."""
    paths = bench(tmp_path, spread(20), per_stratum=10)
    code, _, record = read(tmp_path, paths, grader({"general": 2}), monkeypatch, per_stratum=10)

    assert code == 0
    assert {name: block["agreement"] for name, block in record["strata"].items()} == {
        "general": 0.8,
        "service-rich": 1.0,
        "short-text <= 30 chars": 1.0,
    }
    assert record["failed"] == ["general"]
    assert record["passed"] == ["service-rich", "short-text <= 30 chars"]
    assert record["totals"]["agreement"] == pytest.approx(28 / 30)
    assert record["totals"]["agreement"] >= record["bar"], "the average passes, one stratum did not"
    # what goes back is the failed stratum's whole population, not the 10 rows judged
    assert record["second_round_rows"] == record["strata"]["general"]["population"] == 20


def test_a_blank_cell_is_counted_incorrect_and_not_dropped_from_the_denominator(
    tmp_path, monkeypatch
):
    """The manifest registered it that way before the pack went out. A blank quietly skipped
    would shrink the denominator and raise the agreement of the stratum that skipped it."""
    rows = spread(4)
    paths = bench(tmp_path, rows)
    verdicts = ["correct"] * 6
    code, _, record = read(tmp_path, paths, verdicts, monkeypatch, edit=blank_the_first)

    assert code == 0
    blank = next(block for block in record["strata"].values() if block["n"] != block["correct"])
    assert blank["n"] == 2, "the row is still in the denominator"
    assert blank["tally"]["(blank)"] == 1
    assert blank["agreement"] == 0.5
    assert record["blank_counts_as"] == "incorrect"


def blank_the_first(rows):
    rows[0]["verdict"] = ""


def test_a_verdict_form_nobody_registered_stops_the_run(tmp_path, monkeypatch):
    rows = spread(4)
    paths = bench(tmp_path, rows)
    verdicts = ["correct"] * 5 + ["mostly"]
    with pytest.raises(SystemExit, match="is not one of"):
        read(tmp_path, paths, verdicts, monkeypatch)


def test_a_verdict_a_spreadsheet_capitalised_is_the_same_verdict(tmp_path, monkeypatch):
    rows = spread(4)
    paths = bench(tmp_path, rows)
    code, _, record = read(tmp_path, paths, ["Correct", "CORRECT"] + ["correct"] * 4, monkeypatch)
    assert code == 0 and record["totals"]["correct"] == 6


def test_a_frozen_column_that_came_back_changed_stops_the_run(tmp_path, monkeypatch):
    """Only `verdict` and `notes` may move. A row whose `intents` cell was edited on the way
    back was judged against something other than what the model produced."""
    rows = spread(4)
    paths = bench(tmp_path, rows)

    def retouch(back):
        back[0]["intents"] = '["taste"]'

    with pytest.raises(SystemExit, match="intents of .* differs from the sealed pack"):
        read(tmp_path, paths, ["correct"] * 6, monkeypatch, edit=retouch)


def test_a_notes_column_that_came_back_full_is_not_a_defect(tmp_path, monkeypatch):
    """`notes` is where the sitting says which field was wrong, so it is mutable on purpose —
    and it is the only place a reader can later see why a row was refused."""
    rows = spread(4)
    paths = bench(tmp_path, rows)
    verdicts = ["incorrect"] + ["correct"] * 5
    code, _, record = read(
        tmp_path, paths, verdicts, monkeypatch, notes={"@c:0": "sarcasm should be true"}
    )
    assert code == 0
    assert any(row["notes"] == "sarcasm should be true" for row in record["rows"])


def test_a_column_that_is_not_the_packs_stops_the_run(tmp_path, monkeypatch):
    rows = spread(4)
    paths = bench(tmp_path, rows)
    with pytest.raises(SystemExit, match="was re-shaped on the way back"):
        read(
            tmp_path,
            paths,
            ["correct"] * 6,
            monkeypatch,
            columns=(*sitting.PRECHECK_COLUMNS, "stratum"),
            edit=lambda back: [row.update(stratum="general") for row in back],
        )


def test_rows_that_came_back_in_a_different_order_stop_the_run(tmp_path, monkeypatch):
    """Order is what the cell-by-cell comparison lines up on; a re-sorted file would compare
    every row against somebody else's and report the first mismatch as a changed cell."""
    rows = spread(4)
    paths = bench(tmp_path, rows)
    with pytest.raises(SystemExit, match="came back in a different order"):
        read(tmp_path, paths, ["correct"] * 6, monkeypatch, edit=lambda back: back.reverse())


def test_a_recount_that_disagrees_with_the_capture_log_stops_without_a_number(
    tmp_path, monkeypatch
):
    """STOP-RULE 1. The log already corrected itself once by one row; a second disagreement is
    not a third arithmetic slip to absorb, it is a file that is not the one the log describes."""
    rows = spread(4)
    paths = bench(tmp_path, rows)
    build(tmp_path, paths, monkeypatch)
    hand_back(tmp_path / "pack", ["correct"] * 6)
    monkeypatch.setattr(reader, "RECORDED_IN_LOG", {"correct": 5, "incorrect": 1})
    record = tmp_path / "gates.json"
    code = reader.main(
        [
            "--manifest",
            str(tmp_path / "manifest.json"),
            "--pack",
            str(tmp_path / "pack"),
            "--posts",
            str(paths["posts"]),
            "--record",
            str(record),
        ]
    )
    assert code == 2
    assert not record.exists(), "a stop that still writes a gate number is not a stop"


def test_a_batch_whose_bytes_moved_since_the_seal_stops_the_rebuild(tmp_path, monkeypatch):
    """The rows the pack was drawn from are the pack. If they moved, the rebuild draws a
    different 300 and the verdicts belong to neither."""
    rows = spread(4)
    paths = bench(tmp_path, rows)
    build(tmp_path, paths, monkeypatch)
    hand_back(tmp_path / "pack", ["correct"] * 6)
    paths["batch"].write_text(
        paths["batch"].read_text(encoding="utf-8").replace("коротко", "коротшe"), encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="the manifest pins"):
        reader.main(
            [
                "--manifest",
                str(tmp_path / "manifest.json"),
                "--pack",
                str(tmp_path / "pack"),
                "--posts",
                str(paths["posts"]),
                "--record",
                str(tmp_path / "gates.json"),
            ]
        )


def test_the_incorrect_rows_of_a_passed_stratum_are_listed_and_a_failed_ones_are_not(
    tmp_path, monkeypatch
):
    """The next step fixes adjudicated rows in passed strata only. A failed stratum's rows are
    not fixed one by one — its whole population goes back — so the list must not contain them."""
    paths = bench(tmp_path, spread(20), per_stratum=10)
    code, manifest, record = read(
        tmp_path, paths, grader({"general": 2, "service-rich": 1}), monkeypatch, per_stratum=10
    )

    assert code == 0
    where = manifest["precheck"]["stratum_of"]
    listed = record["incorrect_in_passed_strata"]
    assert len(listed) == 1, "the one incorrect row that sits in a stratum that passed"
    assert {where[row_id] for row_id in listed} == {"service-rich"}
    wrong = {row["id"] for row in record["rows"] if row["verdict"] != "correct"}
    assert len(wrong) == 3 and set(listed) < wrong, "general's two are wrong and not listed"


def test_the_record_names_what_produced_the_verdicts_and_never_calls_it_calibration(
    tmp_path, monkeypatch
):
    """Amendment 2 renamed the provenance: 264 of the 300 verdicts came from a team-lead LLM
    the operator spot-checked, and SPEC §8 means something else by "operator calibration"."""
    rows = spread(4)
    paths = bench(tmp_path, rows)
    code, _, record = read(tmp_path, paths, ["correct"] * 6, monkeypatch)

    assert code == 0
    assert record["provenance"] == reader.PROVENANCE
    assert "spot-check" in record["provenance"] and "adjudication" in record["provenance"]
    assert "operator calibration" not in json.dumps(record, ensure_ascii=False)
    assert record["capture_log"].endswith("quiz-sitting-45g-log.md")


def test_the_returned_file_hashes_differently_from_the_sealed_one_by_design(tmp_path, monkeypatch):
    """Two columns were filled in, so a whole-file sha256 check would refuse every real return.
    Identity is proved on the frozen columns, and both hashes are recorded to say so."""
    rows = spread(4)
    paths = bench(tmp_path, rows)
    code, manifest, record = read(tmp_path, paths, ["correct"] * 6, monkeypatch)

    assert code == 0
    assert record["sealed_sha256"] == manifest["sha256"]["precheck300.csv"]
    assert record["returned_sha256"] != record["sealed_sha256"]
    assert "verdict" in record["sha256_note"] and "frozen columns" in record["sha256_note"]
