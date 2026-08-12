"""Bar 2's applier: one passing apply, and every refusal that stands between it and a wrong record.

The dictation is numbers, not prose, so the failure it has is a typo — and a typo in a table of 45
rows is invisible. Each test below is one way the table can be wrong while still looking like a
table: a count that does not match the dump, a key nobody carries, a row nobody ruled on, a suffix
that reaches two pages, and the two verdict flips that keep 20/41 intact.
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import apply_sku_pair_verdicts as applier  # noqa: E402

#   p1.jpg  10.0 / 20.0   n=1  correct
#   p2.jpg   5.0 /  8.0   n=2  wrong, the page prints 8.90
#   p3.jpg   3.0 /  4.0   n=1  correct
#   4 rows over 3 keys, 2 correct and 2 wrong -> 2/4 = 0.5
FIXTURE = (
    ("p1.jpg", 10.0, 20.0, 1, "correct", None),
    ("p2.jpg", 5.0, 8.0, 2, "wrong", 8.90),
    ("p3.jpg", 3.0, 4.0, 1, "correct", None),
)
COUNTS = {"keys": 3, "rows": 4, "correct_rows": 2, "wrong_rows": 2, "accuracy_4dp": 0.5}


def row(file: str, promo: float, old, page: int = 1, pct: float = 50.0) -> dict:
    return {
        "item": f"@a:{file}",
        "page": page,
        "file": f"media/{file}",
        "price_promo": promo,
        "price_old": old,
        "discount_pct_printed": pct,
    }


DUMP = [
    row("p1.jpg", 10.0, 20.0),
    row("p2.jpg", 5.0, 8.0),
    row("p2.jpg", 5.0, 8.0, page=2),
    row("p3.jpg", 3.0, 4.0),
    row("p4.jpg", 9.0, None),  # a position with no crossed-out price: outside the denominator
    {**row("t1", 7.0, 14.0), "page": None},  # a text row: bar 2 reads the leaflet leg only
]


def pairs() -> list[dict]:
    return applier.pair_rows(DUMP)


def test_the_denominator_is_leaflet_rows_carrying_a_crossed_out_price():
    assert len(pairs()) == 4
    assert [p["file"] for p in pairs()] == [f"media/p{i}.jpg" for i in (1, 2, 2, 3)]


def test_a_clean_dictation_joins_every_row_exactly_once():
    keys = applier.match(FIXTURE, pairs())
    assert [key["n"] for key in keys] == [1, 2, 1]
    assert applier.checksums(keys, COUNTS) == {
        "keys": 3,
        "rows": 4,
        "correct_rows": 2,
        "wrong_rows": 2,
        "accuracy": pytest.approx(0.5),
        "accuracy_4dp": 0.5,
    }
    # a correct pair's printed old price is the dump's own; a wrong one's comes from the read
    assert [key["printed_old"] for key in keys] == [20.0, 8.90, 4.0]
    assert [key["printed_old_dictated"] for key in keys] == [None, 8.90, None]
    assert keys[1]["pages"] == [1, 2] and keys[1]["items"] == ["@a:p2.jpg"]


def swapped(index: int, **fields):
    """The fixture table with one row's fields replaced — the shape every typo arrives in."""
    columns = ("suffix", "promo", "old", "n", "verdict", "printed_old")
    rows = [dict(zip(columns, entry)) for entry in FIXTURE]
    rows[index].update(fields)
    return tuple(tuple(entry[column] for column in columns) for entry in rows)


def test_it_refuses_an_n_the_dump_does_not_carry():
    with pytest.raises(SystemExit, match="the read says n=3 and the dump carries 2"):
        applier.match(swapped(1, n=3), pairs())


def test_it_refuses_a_key_no_dump_row_carries():
    with pytest.raises(SystemExit, match="p9.jpg 1.0/2.0 was ruled on and no dump row carries it"):
        applier.match(FIXTURE + (("p9.jpg", 1.0, 2.0, 1, "correct", None),), pairs())


def test_it_refuses_a_dump_row_no_dictated_key_covers():
    with pytest.raises(SystemExit, match="1 dump pair row\\(s\\) no dictated key covers"):
        applier.match(FIXTURE[:-1], pairs())


def test_it_refuses_a_suffix_that_reaches_two_pages():
    """`…4404.jpg` is how the read names a page, and `.jpg` would name every page it reached."""
    with pytest.raises(SystemExit, match="the suffix .jpg reaches 3 different pages"):
        applier.match(((".jpg", 10.0, 20.0, 1, "correct", None),), pairs())


def test_it_refuses_the_same_rows_ruled_on_twice():
    with pytest.raises(SystemExit, match="is claimed twice"):
        applier.match(FIXTURE + (FIXTURE[0],), pairs())


def test_it_refuses_a_correct_verdict_that_carries_a_printed_old():
    with pytest.raises(SystemExit, match="is correct and carries printed_old"):
        applier.match(swapped(0, printed_old=19.90), pairs())


def test_it_refuses_a_wrong_verdict_with_no_printed_old():
    with pytest.raises(SystemExit, match="is wrong and the read names no printed_old"):
        applier.match(swapped(1, printed_old=None), pairs())


def test_it_refuses_a_wrong_verdict_whose_printed_old_is_the_dumps_own():
    """The flip the counts cannot see: mark one correct row wrong and one wrong row correct and
    20/41 still holds. `printed_old` is the only field that has to change with the verdict."""
    with pytest.raises(SystemExit, match="a wrong pair whose old price is right"):
        applier.match(swapped(1, printed_old=8.0), pairs())


def test_it_refuses_a_verdict_that_is_neither_correct_nor_wrong():
    with pytest.raises(SystemExit, match="is neither correct nor wrong"):
        applier.match(swapped(0, verdict="partly"), pairs())


def test_the_checksums_are_the_read_s_own_counts_and_not_derived_from_the_table():
    """`EXPECTED` exists to catch a mistyped `DICTATED`; if it were computed from `DICTATED` it
    would agree with every typo. The control is the same table against the stated counts."""
    keys = applier.match(FIXTURE, pairs())
    assert applier.checksums(keys, COUNTS)["accuracy_4dp"] == 0.5
    with pytest.raises(SystemExit, match="the read states rows = 5 and the table joins to 4"):
        applier.checksums(keys, {**COUNTS, "rows": 5})
    with pytest.raises(SystemExit, match="rounds to 0.5 and the read states 0.8"):
        applier.checksums(keys, {**COUNTS, "accuracy_4dp": 0.8})


# --- the whole write path, against the real read ------------------------------


def tree(tmp_path: Path, dump_rows=None) -> dict:
    dump_path = tmp_path / "dump.jsonl"
    rows = DUMP if dump_rows is None else dump_rows
    dump_path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    record_path = tmp_path / "record.json"
    record_path.write_text(
        json.dumps(
            {
                "dump": {
                    "path": str(dump_path),
                    "sha256": hashlib.sha256(dump_path.read_bytes()).hexdigest(),
                }
            }
        ),
        encoding="utf-8",
    )
    return {"record": record_path, "dump": dump_path, "out": tmp_path / "pairs.json"}


def test_main_refuses_a_dump_that_is_not_the_records_own(tmp_path):
    paths = tree(tmp_path)
    paths["dump"].write_text(paths["dump"].read_text(encoding="utf-8") + "\n", encoding="utf-8")
    argv = ["--record", str(paths["record"]), "--out", str(paths["out"])]
    with pytest.raises(SystemExit, match="these are not the pairs that were bought"):
        applier.main(argv)


def test_main_writes_the_real_read_over_the_sealed_dump(tmp_path, capsys):
    """The deliverable itself: `DICTATED` against the merged v4 dump, through the write path.

    Nothing synthetic — the 45 keys, the 61 rows and the 20/61 are the ones the record on disk
    carries, and every guard above ran on the way here.
    """
    out = tmp_path / "sku_b_pair_verdicts.json"
    assert applier.main(["--out", str(out)]) == 0
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["checksums"] == {
        "keys": 45,
        "rows": 61,
        "correct_rows": 20,
        "wrong_rows": 41,
        "accuracy": pytest.approx(20 / 61),
        "accuracy_4dp": 0.3279,
    }
    assert written["checksums"]["accuracy_4dp"] == applier.EXPECTED["accuracy_4dp"]
    assert written["dump"]["pair_rows"] == 61
    assert len(written["keys"]) == 45
    assert all(key["printed_old"] is not None for key in written["keys"])
    assert written["diagnosis"] == applier.DIAGNOSIS
    assert "0.3279" in capsys.readouterr().out
    # this read states one set of counts and extends nothing — both fields exist for B′'s read,
    # and a v4 record that acquired either would be claiming something about itself that is false
    assert written["checksum_deviation"] is None and "extends" not in written


def test_the_default_read_is_this_modules_own_constants():
    """`main` takes the read as a parameter so a second dictation can reuse these guards. The
    default has to stay this file's, or B′'s table would be applied by running the v4 script."""
    assert applier.THIS.dictated is applier.DICTATED
    assert applier.THIS.expected is applier.EXPECTED
    assert (applier.THIS.record, applier.THIS.out) == (applier.RECORD, applier.OUT)
    assert (applier.THIS.stated, applier.THIS.prior) == (None, None)


def test_the_contract_the_record_names_is_in_the_tree():
    """A provenance string nobody re-derives is a string that stops being true silently (Dv170)."""
    named = applier.CONTRACT.split()[0]
    assert (REPO_ROOT / named).exists(), f"the record names {named}, which is not here"
    assert applier.READ_ON == "2026-08-12"
