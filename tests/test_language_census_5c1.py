"""Offline tests for the language census — no Telegram, no store writes.

What can go wrong here is not arithmetic. It is a bar that moved after the numbers were seen, a
source with two posts being called Ukrainian, and a detector that fails a case we already know the
answer to and rules anyway. Those three are what these tests are about.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import language_census_5c1 as census  # noqa: E402

from moved_pins import handles_before_r2  # noqa: E402


def counts(ua=0, ru=0, en=0, other=0):
    return {"ua": ua, "ru": ru, "en": en, "other": other}


def post(text, date="2026-08-01T00:00:00+00:00"):
    return {"record_type": "post", "text": text, "date": date}


# --- the bars were fixed before the numbers ------------------------------------------------------


def test_the_bars_are_the_ones_registered_before_anything_was_computed():
    """The pre-registration is a separate artifact with its own timestamp, and the script refuses
    to run against a different one — otherwise "fixed beforehand" is a claim, not a fact."""
    registered = json.loads(census.PREREGISTRATION.read_text(encoding="utf-8"))["rule"]
    assert registered["dominance"] == census.DOMINANCE
    assert registered["min_decidable"] == census.MIN_DECIDABLE
    assert set(registered["verdicts"]) == {
        "UA_DOMINANT",
        "RU_DOMINANT",
        "MIXED",
        "TOO_FEW_DECIDABLE",
        "NO_POSTS_IN_WINDOW",
    }
    assert (
        census.check_preregistration()
        == __import__("hashlib").sha256(census.PREREGISTRATION.read_bytes()).hexdigest()
    )


def test_a_bar_moved_only_in_the_script_stops_the_run(monkeypatch):
    """The negative control for the test above: without it, the check cannot fail."""
    monkeypatch.setattr(census, "DOMINANCE", 0.55)
    with pytest.raises(SystemExit, match="not the ones registered"):
        census.check_preregistration()


# --- the verdict rule ----------------------------------------------------------------------------


def test_the_bar_is_where_the_registration_says_it_is():
    assert census.verdict_for(counts(ua=7, ru=3), 10)[0] == "UA_DOMINANT"
    assert census.verdict_for(counts(ua=6, ru=4), 10)[0] == "MIXED"
    assert census.verdict_for(counts(ua=3, ru=7), 10)[0] == "RU_DOMINANT"
    assert census.verdict_for(counts(ua=4, ru=6), 10)[0] == "MIXED"


def test_the_two_states_without_a_verdict_have_two_names():
    """A silent channel and a channel with four posts are different problems with different fixes.
    One name for both would hide which one a row is — and 14 of the 56 are the first kind."""
    assert census.verdict_for(counts(), 0)[0] == "NO_POSTS_IN_WINDOW"
    assert census.verdict_for(counts(ua=4, ru=1), 5)[0] == "TOO_FEW_DECIDABLE"
    # And neither carries a share: a share on five posts reads like a measurement.
    assert census.verdict_for(counts(ua=4, ru=1), 5)[1:] == (None, None)


def test_undecidable_posts_are_counted_and_kept_out_of_the_denominator():
    """`other` mixes "no letters at all" with "Cyrillic, no distinctive marker". Neither is
    evidence for a language, and putting them in the denominator would push every share down."""
    verdict, ua_share, _ = census.verdict_for(counts(ua=10, ru=0, en=5, other=40), 55)
    assert (verdict, ua_share) == ("UA_DOMINANT", 1.0)


def test_a_post_outside_the_window_is_not_measured(tmp_path, monkeypatch):
    """The window is `collect_5c1.py`'s own fixed `since`. A store that later holds older rows
    must not quietly widen the corpus this verdict was computed on."""
    monkeypatch.setattr(census, "STORE", tmp_path)
    lines = [
        json.dumps(post("Сьогодні знижка на молоко", "2026-08-01T00:00:00+00:00")),
        json.dumps(post("Вчорашній пост", "2026-06-01T00:00:00+00:00")),
        '{"record_type": "post", "text": "трунк',  # a line cut off mid-write
    ]
    (tmp_path / "chan.jsonl").write_text("\n".join(lines), encoding="utf-8")
    rows = census.posts_in_window("@chan", "2026-07-10T10:33:14+00:00")
    assert [r["text"] for r in rows] == ["Сьогодні знижка на молоко"]


def test_the_detector_reads_the_two_languages_the_policy_is_about():
    """Not a test of `langid` — a check that the two directions this census turns into verdicts
    are the ones a reader would call by eye."""
    measured = census.count_languages(
        [post("Смачний сир та молоко, дуже гарна ціна"), post("Вкусный сыр и молоко, очень хорошо")]
    )
    assert measured["counts"]["ua"] == 1 and measured["counts"]["ru"] == 1
    assert len(measured["examples"]["ru"]) == 1


# --- the record and the controls -----------------------------------------------------------------


def test_the_verdictless_rows_sort_last_instead_of_ranking_as_zero(tmp_path, monkeypatch):
    """The brief asks for a table sorted by RU share. A row with no share is not a row at 0.0."""
    monkeypatch.setattr(census, "RECORD", tmp_path / "census.json")
    assert census.main(["--out", str(tmp_path / "census.json")]) == 0

    rows = json.loads((tmp_path / "census.json").read_text(encoding="utf-8"))["sources"]
    shares = [r["ru_share"] for r in rows]
    with_share = [s for s in shares if s is not None]
    assert with_share == sorted(with_share, reverse=True)
    assert shares[len(with_share) :] == [None] * (len(shares) - len(with_share))


def test_a_control_that_fails_makes_every_verdict_unreportable(tmp_path, monkeypatch):
    """A detector that gets a known channel wrong cannot rule on unknown ones. The record is still
    written — the counts are the evidence for whatever went wrong — and the run exits non-zero."""
    monkeypatch.setattr(census, "CONTROLS", {"@offspringrus": "ua"})  # it is a Russian shop
    out = tmp_path / "census.json"
    assert census.main(["--out", str(out)]) == 1

    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["verdicts_reportable"] is False
    assert record["controls"]["@offspringrus"]["ok"] is False
    assert record["sources"], "the counts still have to be written down"


def test_the_shipped_record_carries_the_preregistration_it_was_computed_under():
    """The claim "the threshold was fixed first" is checkable from the record alone: it cites the
    file's hash, and that hash has to be the hash of the file in the tree."""
    import hashlib

    record = json.loads(
        (REPO_ROOT / "results" / "language_census_5c1.json").read_text(encoding="utf-8")
    )
    digest = hashlib.sha256(census.PREREGISTRATION.read_bytes()).hexdigest()
    assert record["preregistration"]["sha256"] == digest
    assert record["preregistration"]["dominance"] == census.DOMINANCE
    assert record["verdicts_reportable"] is True
    # Self-consistent rather than literal: the shipped record covers 56 sources because it was
    # computed BEFORE wave 3 took the registry to 41, and a re-run after any composition change
    # writes a different n without making either record wrong.
    assert record["summary"]["n"] == len(record["sources"])
    # It is the WAVE-3 record and stays one: the rows the ruling cites are channels that have
    # since left, so this file can never be re-derived from today's registry. The pass that must
    # cover the live composition is the day-2 one below.
    for handle in ("@retsepty5", "@retsepty4", "@katyal55", "@tretyakovaele"):
        assert any(row["handle"] == handle for row in record["sources"]), handle


def test_the_day_2_census_covers_the_live_registry_under_the_same_bars():
    """Step 6 of the day-2 order. Same pre-registration file, a second output path — so the wave-3
    evidence survives and the live composition still has a language verdict."""
    import hashlib

    record = json.loads(
        (REPO_ROOT / "results" / "language_census_5c1_day2.json").read_text(encoding="utf-8")
    )
    # The composition of 08.08, not today's: revision r2 (2026-08-30) added eight A1 sources this
    # census never read, and r2 is the only revision that moved a ROW, so the pre-r2 bytes ARE that
    # composition ([[the_field_true_under_the_old_constant]]).
    live = handles_before_r2()
    # The record is a dated pass over the 67 that stood on 08.08; @dikankaa left on the acceptance
    # ruling that same evening, on this very census. So the covering direction is the one that
    # matters — every source of that composition has a language verdict — and the difference is
    # named, not tolerated as a set that drifted.
    measured = {row["handle"] for row in record["sources"]}
    assert live <= measured
    assert measured - live == {"@dikankaa"}, sorted(measured - live)
    assert (
        record["preregistration"]["sha256"]
        == hashlib.sha256(census.PREREGISTRATION.read_bytes()).hexdigest()
    ), "a second pass under a different bar is a different instrument"
    assert record["preregistration"]["dominance"] == census.DOMINANCE
    assert record["verdicts_reportable"] is True
    # The one RU_DOMINANT of the day-2 entrants, reported and not acted on: the brief says fresh
    # entries are REPORT ONLY. Its own text is why it is worth the operator's eye — a rehoming
    # post covering «Волгоградской области ( Энгельс, Саратов )».
    ru = [row["handle"] for row in record["sources"] if row["verdict"] == "RU_DOMINANT"]
    assert ru == ["@dikankaa"], ru
    assert any(
        "Саратов" in line
        for line in next(row for row in record["sources"] if row["handle"] == "@dikankaa")[
            "ru_examples"
        ]
    )


def test_the_census_refuses_to_overwrite_the_wave_3_evidence(tmp_path, monkeypatch):
    """The failure it prevents: a re-run writes a table without @retsepty5's 139 posts in it, and
    the ruling that cites them keeps pointing at a file that no longer says so."""
    import pytest

    with pytest.raises(SystemExit, match="evidence behind wave 3"):
        census.main([])
    # The negative control, without which this only proves the script refuses everything: another
    # path is accepted, and it is what the day-2 pass above was written through.
    monkeypatch.setattr(census, "REGISTRY", REPO_ROOT / "config" / "registry.yaml")
    assert census.main(["--out", str(tmp_path / "elsewhere.json")]) == 0
    assert (tmp_path / "elsewhere.json").exists()
