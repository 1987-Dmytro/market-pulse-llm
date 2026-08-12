"""B′'s bar-2 applier: the 80 dictated pairs, the one checksum that moved, and the read it extends.

The guards themselves are `tests/test_apply_sku_pair_verdicts.py`'s — this table reaches them
through the same `match`/`checksums`. What is new here is what the v4 read did not have: a contract
whose key count its own table contradicts, and a sealed prior read that 61 of these 80 rows have to
still agree with.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import apply_sku_pair_verdicts as applier  # noqa: E402
import apply_sku_pair_verdicts_skub2 as skub2  # noqa: E402


def dump_pairs() -> list[dict]:
    path = REPO_ROOT / "results" / "sku_b_positions_skub2.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return applier.pair_rows(rows)


# --- the deliverable, over the sealed dump ------------------------------------


def test_main_writes_the_eighty_dictated_pairs_over_the_skub2_dump(tmp_path, capsys):
    out = tmp_path / "pairs.json"
    assert skub2.main(["--out", str(out)]) == 0
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["checksums"] == {
        "keys": 64,
        "rows": 80,
        "correct_rows": 33,
        "wrong_rows": 47,
        "accuracy": pytest.approx(33 / 80),
        "accuracy_4dp": 0.4125,
    }
    assert written["dump"]["pair_rows"] == 80
    assert written["dump"]["path"].endswith("sku_b_positions_skub2.jsonl")
    assert len(written["keys"]) == 64
    assert all(key["printed_old"] is not None for key in written["keys"])
    assert written["diagnosis"] == skub2.DIAGNOSIS
    assert "0.4125" in capsys.readouterr().out


def test_the_contract_the_record_names_is_in_the_tree():
    """A provenance string nobody re-derives is a string that stops being true silently (Dv170)."""
    named = skub2.CONTRACT.split()[0]
    assert (REPO_ROOT / named).exists(), f"the record names {named}, which is not here"
    assert "skub2" in named and applier.READ_ON == "2026-08-12"


def test_the_defaults_cannot_reach_the_pilots_sealed_evidence():
    """Every path here is a NEW one beside v4's: `results/sku_b_pair_verdicts.json` is the closed
    pilot's bar-2 evidence and is this read's INPUT, never its output."""
    assert skub2.OUT.name == "sku_b_pair_verdicts_skub2.json"
    assert skub2.RECORD.name == "sku_b_positions_skub2.json"
    assert skub2.PRIOR.name == "sku_b_pair_verdicts.json" and skub2.PRIOR.exists()
    assert skub2.OUT != skub2.PRIOR
    assert applier.OUT == skub2.PRIOR  # the v4 read's own output IS this read's prior
    assert applier.RECORD.name == "sku_b_positions_v4.json" and skub2.RECORD != applier.RECORD


# --- Dv237: the key count the contract states and the one the dump forces -----


def test_the_contracts_own_key_count_refuses_when_it_is_asserted_verbatim():
    """The negative control for `EXPECTED`. Without it the record shows 64 keys asserted and
    verified, and a reader cannot tell that apart from a guard that was never able to fire."""
    verbatim = skub2.THIS._replace(expected=skub2.CONTRACT_CHECKSUMS, stated=None, stated_why=None)
    keys = applier.match(verbatim.dictated, dump_pairs())
    with pytest.raises(SystemExit, match="the read states keys = 54 and the table joins to 64"):
        applier.checksums(keys, verbatim.expected)


def test_the_key_count_is_the_dumps_and_the_other_four_are_the_contracts():
    """64 is not this table counting itself: it is how many distinct price boxes the DUMP carries,
    and the four counts that could hide a flipped verdict are the contract's own, unedited."""
    pairs = dump_pairs()
    boxes = {(row["file"], row["price_promo"], row["price_old"]) for row in pairs}
    assert len(pairs) == 80 and len(boxes) == 64
    assert skub2.EXPECTED["keys"] == len(boxes) and skub2.CONTRACT_CHECKSUMS["keys"] == 54
    for field in ("rows", "correct_rows", "wrong_rows", "accuracy_4dp"):
        assert skub2.EXPECTED[field] == skub2.CONTRACT_CHECKSUMS[field]


def test_the_deviation_names_the_one_field_that_moved_and_carries_both_numbers():
    moved = applier.deviation(skub2.THIS)
    assert moved["fields"] == {"keys": {"contract": 54, "asserted": 64}}
    assert moved["contract_checksums"] == skub2.CONTRACT_CHECKSUMS
    assert "Dv237" in moved["why"]


def test_a_deviation_that_deviates_in_nothing_is_refused():
    """Two names for one number drift apart; a `stated` line identical to `expected` is a field
    nobody will keep true, and the v4 read (which states nothing separately) deviates in None."""
    with pytest.raises(SystemExit, match="a deviation nobody can see is not a deviation"):
        applier.deviation(skub2.THIS._replace(stated=skub2.EXPECTED))
    assert applier.deviation(applier.THIS) is None


# --- the read this one extends ------------------------------------------------


def test_the_sixty_one_shared_rows_are_the_v4_read_unchanged(tmp_path):
    """The contract's provenance sentence, checked against the file rather than repeated: 61 of the
    80 rows are the sealed v4 dictation, and their share is still that read's own 20/61."""
    keys = applier.match(skub2.DICTATED, dump_pairs())
    extends = applier.carried_forward(keys, skub2.PRIOR)
    sealed = json.loads(skub2.PRIOR.read_text(encoding="utf-8"))
    assert extends["shared"] == {
        "keys": 45,
        "rows": 61,
        "correct_rows": 20,
        "wrong_rows": 41,
        "accuracy": pytest.approx(20 / 61),
        "accuracy_4dp": 0.3279,
    }
    assert extends["shared"]["accuracy_4dp"] == sealed["checksums"]["accuracy_4dp"]
    assert extends["prior"]["checksums"]["rows"] == 61 and extends["rows_whose_n_moved"] == []


def test_the_nineteen_new_rows_are_exactly_the_four_pages_v1_refused():
    """What (13) actually bought, and the ADR's central claim: the new pairs are new because the
    PAGES are new, and those pages are not "some pages" — they are precisely the four page answers
    the v4 run recorded as unreadable (asterisk ×2, malformed JSON at the 800-token ceiling,
    multipack). Derived from the v4 record rather than typed, because a list of four page numbers
    written into a test is a claim that agrees with itself."""
    v4_record = json.loads((REPO_ROOT / "results" / "sku_b_positions_v4.json").read_text("utf-8"))
    refused = {
        outcome["source"].rsplit("/", 1)[-1]
        for outcome in v4_record["outcomes"]
        if outcome["leg"] == "page" and outcome["unreadable"]
    }
    keys = applier.match(skub2.DICTATED, dump_pairs())
    fresh = applier.carried_forward(keys, skub2.PRIOR)["new"]
    assert set(fresh["rows_by_page"]) == refused
    assert fresh["rows_by_page"] == {
        "atb_market_official_4342.jpg": 2,
        "atb_market_official_4405.jpg": 9,
        "atb_market_official_4446.jpg": 6,
        "atb_market_official_4467.jpg": 2,
    }
    assert (fresh["keys"], fresh["rows"], fresh["correct_rows"]) == (19, 19, 13)
    assert fresh["accuracy_4dp"] == 0.6842


def test_a_pair_that_already_has_a_verdict_cannot_be_re_adjudicated(tmp_path):
    """The guard the provenance sentence needs: this read may EXTEND the v4 one and may not revise
    it. Flipping one shared key — with the `printed_old` a legal flip would carry — is refused by
    the sealed file, not by the counts, which stay at 33/47 either way."""
    flipped = tuple(
        ("4343.jpg", 17.9, 29.9, 1, "wrong", 29.50) if row[0] == "4343.jpg" else row
        for row in skub2.DICTATED
    )
    keys = applier.match(flipped, dump_pairs())
    with pytest.raises(SystemExit, match="4343.jpg 17.9/29.9: .* reads verdict 'correct'"):
        applier.carried_forward(keys, skub2.PRIOR)


def test_a_prior_read_over_another_dump_still_joins_by_key_not_by_row(tmp_path):
    """`carried_forward` compares two READS, and the v4 one was taken over the v4 dump. The join is
    the price box, so a prior read whose rows are a different shape is still comparable — what it
    may not be is silently partial, and a key it does not carry is reported as new, never as
    agreeing."""
    keys = applier.match(skub2.DICTATED, dump_pairs())
    short = tmp_path / "prior.json"
    sealed = json.loads(skub2.PRIOR.read_text(encoding="utf-8"))
    short.write_text(json.dumps({**sealed, "keys": sealed["keys"][:5]}), encoding="utf-8")
    extends = applier.carried_forward(keys, short)
    assert extends["shared"]["keys"] == 5
    assert extends["new"]["keys"] == 59 and extends["new"]["rows"] == 80 - extends["shared"]["rows"]
